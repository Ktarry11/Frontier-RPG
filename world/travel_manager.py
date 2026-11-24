"""
TravelManager - hearthstone, flight paths (windriders) and mounts.

One process-lifetime singleton (same access pattern as get_quest_manager()), replaced with a fresh instance on
new-game / load so a second character never inherits the first one's bind, flight nodes or mounts.

Rules (Kyle's calls, 2026-10-21):
  * MOUNTS   - a riding skill (trainer, gold, level-gated) plus a mount bought from a stable/mount vendor.  Mounted
               = faster walking and fewer random encounters.  Never in caves/dungeons; dismounted on entering one.
  * HEARTH   - usable ANYWHERE off cooldown, caves and dungeons included.
  * HEARTH   - bind at any innkeeper (you stand on their tile).  Using it teleports you to the bind from any overworld
               zone, never from a cave/dungeon.  Cooldown is counted in overworld STEPS, not real time.
  * WINDRIDER- talking to a flight master discovers that node; pay gold to fly to any other discovered node.

All tuning lives in data/travel/travel_data.json.
"""
import json
from pathlib import Path

_DATA = None


#: Flight-map units flown in one market hour (see TravelManager.flight_hours).
FLIGHT_UNITS_PER_HOUR = 50.0


def travel_data():
    global _DATA
    if _DATA is None:
        path = Path(__file__).parent.parent / "data" / "travel" / "travel_data.json"
        with open(path, "r", encoding="utf-8") as fh:
            _DATA = json.load(fh)
    return _DATA


class TravelManager:
    def __init__(self, start_id=None):
        data = travel_data()
        hearth = data["hearth"]
        self.cooldown_steps = int(hearth["cooldown_steps"])
        db = hearth["default_bind"]
        # DEFAULT BIND FOLLOWS THE START ZONE. It used to be the Valley's tile from the data file, full
        # stop, which was correct while the Valley was the only start - and became a bug the moment
        # Deathknell became one, because a Forsaken character's first hearth would have thrown them
        # across the world to a zone they had never seen. start_id comes from character creation.
        from world.start_zones import get_start
        sz = get_start(start_id) if start_id else None
        if sz:
            self.bind = {"zone": sz.zone_name, "x": sz.x, "y": sz.y, "name": sz.label}
        else:
            self.bind = {"zone": db["zone"], "x": db["x"] if db["x"] is not None else 60,
                         "y": db["y"] if db["y"] is not None else 40, "name": db["name"]}
        self.hearth_steps_left = 0          # overworld steps until the hearth is ready again
        self.known_nodes = set()            # flight node ids discovered
        self.riding_rank = 0                # 0 none, 1 apprentice, 2 journeyman, 3 master
        self.owned_mounts = []              # mount ids
        self.active_mount = None            # mount id the player prefers/summons
        self.mounted = False
        # THE COLLECTION (world/collection.py, docs/collection_design.md): the second hearthstone's own bind and
        # cooldown, each portable service's last use in market hours, and the form the leader walks in.
        self.bind2 = None
        self.hearth2_steps_left = 0
        self.collection_used = {}
        self.active_form = None
        # {class form id: Collection look id}: how Bear Form and friends look on the map (world/collection.py)
        self.form_looks = {}
        # heroic dungeons (world/heroic.py): the run in progress (the dungeon entered from outside) and the market
        # day each heroic was last entered, for the once-a-day lockout
        self.heroic_run = None
        self.heroic_locks = {}
        self.active_title = None
        try:
            from world.collection import apply_feathers
            apply_feathers(self)
        except Exception:
            pass

    # ------------------------------------------------------------------ hearth
    def hearth_ready(self):
        return self.hearth_steps_left <= 0

    def set_bind(self, zone_name, x, y, place_name):
        self.bind = {"zone": zone_name, "x": int(x), "y": int(y), "name": place_name}

    def hearth_block_reason(self):
        """None when the hearth can be used right now, otherwise a short player-facing reason.

        USABLE IN CAVES AND DUNGEONS (Kyle, 2026-10-31). This used to refuse anywhere
        zone.is_cave was set, which meant the one place a player most wants to leave in a hurry
        was the one place they could not - and the walk back out of a nine-hull cove or a
        two-map seam is long enough that "no" was a real cost for no design reason. The cooldown
        is the only limit now.
        """
        if not self.hearth_ready():
            return f"Your hearthstone is recharging ({self.hearth_steps_left} steps)."
        return None

    def hearth_cooldown(self):
        """Steps the hearth waits after use: halved by the Collection's Tome of the Swift Hearth."""
        try:
            from world.collection import hearth_cooldown_mult
            mult = hearth_cooldown_mult()
        except Exception:
            mult = 1.0
        return max(1, int(round(self.cooldown_steps * mult)))

    def use_hearth(self):
        """Spend the hearth: starts the cooldown, unmounts, returns the bind dict to teleport to."""
        self.hearth_steps_left = self.hearth_cooldown()
        self.mounted = False
        _hearth_eases_breaks()
        return dict(self.bind)

    # the Collection's Hearthstone of the Second Home: its own bind (set at any innkeeper), its own cooldown
    def has_second_hearth(self):
        try:
            from world.collection import has_second_hearth
            return has_second_hearth()
        except Exception:
            return False

    def set_bind2(self, zone_name, x, y, place_name):
        self.bind2 = {"zone": zone_name, "x": int(x), "y": int(y), "name": place_name}

    def second_hearth_block_reason(self):
        if not self.has_second_hearth():
            return "You haven't learned the Hearthstone of the Second Home."
        if not self.bind2:
            return "Your second hearthstone isn't bound yet. Ask any innkeeper."
        if self.hearth2_steps_left > 0:
            return f"Your second hearthstone is recharging ({self.hearth2_steps_left} steps)."
        return None

    def use_second_hearth(self):
        self.hearth2_steps_left = self.hearth_cooldown()
        self.mounted = False
        _hearth_eases_breaks()
        return dict(self.bind2)

    def on_step(self):
        """Called once per successful overworld tile step."""
        if self.hearth_steps_left > 0:
            self.hearth_steps_left -= 1
        if self.hearth2_steps_left > 0:
            self.hearth2_steps_left -= 1

    # ------------------------------------------------------------------ riding / mounts
    @staticmethod
    def riding_skill(rank):
        return travel_data()["riding_skills"].get(str(rank))

    def next_riding_skill(self):
        """(rank, skill dict) of the next skill to learn, or None when maxed."""
        rank = self.riding_rank + 1
        skill = self.riding_skill(rank)
        return (rank, skill) if skill else None

    def can_learn_riding(self, level, copper):
        nxt = self.next_riding_skill()
        if not nxt:
            return False, "You have already mastered riding."
        rank, skill = nxt
        if level < skill["level"]:
            return False, f"{skill['name']} requires level {skill['level']}."
        if copper < self.riding_price(rank):
            return False, f"{skill['name']} costs {format_copper(skill['price'])}."
        return True, ""

    def riding_price(self, rank):
        """A riding skill's price: free if the Collection's Tome of the Quick Study covers it."""
        skill = self.riding_skill(rank)
        if skill is None:
            return 0
        try:
            from world.collection import free_riding_rank
            if rank <= free_riding_rank():
                return 0
        except Exception:
            pass
        from world.faction_manager import rep_price
        return rep_price(skill["price"])

    @staticmethod
    def mount_price(mount):
        """A stable mount's price after the town's reputation discount."""
        from world.faction_manager import rep_price
        return rep_price(mount["price"])

    def learn_riding(self):
        nxt = self.next_riding_skill()
        if nxt:
            self.riding_rank = nxt[0]
        return self.riding_rank

    @staticmethod
    def mounts_for_vendor(vendor_id):
        return [m for m in travel_data()["mounts"] if vendor_id in m["vendors"]]

    @staticmethod
    def get_mount(mount_id):
        for m in travel_data()["mounts"]:
            if m["id"] == mount_id:
                return m
        try:
            from world.collection import mount_def
            return mount_def(mount_id)
        except Exception:
            return None

    def all_mounts(self):
        """Mounts this character can ride: the ones they bought, and the Collection's (art permitting)."""
        try:
            from world.collection import collection_mount_ids
            extra = [m for m in collection_mount_ids() if m not in self.owned_mounts]
        except Exception:
            extra = []
        return list(self.owned_mounts) + extra

    def can_buy_mount(self, mount, copper):
        if mount["id"] in self.owned_mounts:
            return False, "You already own this mount."
        if self.riding_rank < mount["tier"]:
            need = self.riding_skill(mount["tier"])
            return False, f"Requires {need['name']}."
        if copper < self.mount_price(mount):
            return False, f"Costs {format_copper(mount['price'])}."
        return True, ""

    def buy_mount(self, mount):
        self.owned_mounts.append(mount["id"])
        # a better mount becomes the one you ride
        cur = self.get_mount(self.active_mount) if self.active_mount else None
        if cur is None or mount["tier"] >= cur["tier"]:
            self.active_mount = mount["id"]

    def owned(self):
        """Every mount you've bought, best tier first (the mount picker's rows)."""
        rows = [m for m in (self.get_mount(i) for i in self.all_mounts()) if m]
        return sorted(rows, key=lambda m: (-m["tier"], m["name"]))

    def choose_mount(self, mount_id, in_cave):
        """Kyle, 16 Nov 2026: "for mounts we need a way to select the mount - as when we buy them it just replaces
        the old mount with the new ones". Pick one you own to ride: it becomes the one R summons, and you're on it
        now if you can ride here. Returns (mounted_now, message)."""
        m = self.get_mount(mount_id)
        if m is None or mount_id not in self.all_mounts():
            return self.mounted, "You don't own that mount."
        self.active_mount = mount_id
        reason = self.mount_block_reason(in_cave)
        if reason:
            self.mounted = False
            return False, f"{m['name']} will be the one you ride. {reason}"
        self.mounted = True
        return True, f"You mount your {m['name']}."

    def current_mount(self):
        return self.get_mount(self.active_mount) if self.active_mount else None

    def mount_block_reason(self, in_cave):
        if self.riding_rank < 1:
            return "You haven't learned to ride yet. Find a riding trainer (level 20)."
        if not self.all_mounts():
            return "You don't own a mount. Buy one from a mount vendor."
        if in_cave:
            return "You can't ride in a cave or dungeon."
        return None

    def toggle_mount(self, in_cave):
        """Returns (mounted_now, message)."""
        if self.mounted:
            self.mounted = False
            return False, "You dismount."
        reason = self.mount_block_reason(in_cave)
        if reason:
            return False, reason
        self.mounted = True
        return True, f"You mount your {self.current_mount()['name']}."

    def force_dismount(self):
        was = self.mounted
        self.mounted = False
        return was

    def _skill_for_mount(self):
        """The skill whose numbers apply right now, or None when on foot.

        SPEED COMES FROM THE SKILL, NOT THE MOUNT. This used to cap the rank at the mount's tier,
        which was fine while the mounts went as high as the skills did and became a silent bug the
        moment Master Riding existed: the best mount in the game is tier 2, so a 200g skill could
        never deliver its 2.5x and Master Riding was inert. The tier is a gate on OWNING a mount
        (can_buy_mount), which is where a gate belongs; it is not a cap on how well you ride.
        """
        mount = self.current_mount()
        if not (self.mounted and mount):
            return None
        return self.riding_skill(self.riding_rank)

    def speed_mult(self):
        skill = self._skill_for_mount()
        return skill["speed_mult"] if skill else 1.0

    def encounter_mult(self):
        skill = self._skill_for_mount()
        return skill["encounter_mult"] if skill else 1.0

    # ------------------------------------------------------------------ flight paths
    @staticmethod
    def nodes():
        return travel_data()["flight_nodes"]

    @staticmethod
    def node_for_master(npc_id):
        for node_id, node in travel_data()["flight_nodes"].items():
            if node["master"] == npc_id:
                return node_id
        return None

    def discover_node(self, node_id):
        """True if this was a NEW discovery."""
        if node_id in self.known_nodes:
            return False
        self.known_nodes.add(node_id)
        return True

    @staticmethod
    def continent_of(node_id):
        node = travel_data()["flight_nodes"].get(node_id)
        return node.get("continent", "kalimdor") if node else None

    @classmethod
    def can_fly_between(cls, from_node, to_node):
        """Flight networks are per-continent: Kalimdor and Eastern Kingdoms never connect
        (the Orgrimmar <-> Undercity zeppelin is the only way across)."""
        return from_node is not None and cls.continent_of(from_node) == cls.continent_of(to_node)

    @staticmethod
    def flight_hours(from_node, to_node):
        """Market hours a flight takes (Kyle, 19 Nov 2026: "make wind riders pass time as it takes time to fly?
        Maybe based on distance to help recruit people"). An hour per FLIGHT_UNITS_PER_HOUR map units, rounded to
        the half hour, at least half an hour: a hop next door is half an hour, the median flight two and a half
        hours, and coast to coast about six and a half, still under a hearth's eight. It costs gold by the same
        distance, so flying back and forth to pass time is never free."""
        nodes = travel_data()["flight_nodes"]
        if from_node not in nodes or to_node not in nodes:
            return 0.0
        a, b = nodes[from_node]["pos"], nodes[to_node]["pos"]
        dist = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        return max(0.5, round(dist / FLIGHT_UNITS_PER_HOUR * 2) / 2.0)

    @staticmethod
    def flight_cost(from_node, to_node):
        nodes = travel_data()["flight_nodes"]
        a, b = nodes[from_node]["pos"], nodes[to_node]["pos"]
        dist = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        cost = travel_data()["flight_cost"]
        from world.faction_manager import rep_price
        return int(rep_price(int(cost["base"] + cost["per_unit"] * dist)))

    # ------------------------------------------------------------------ persistence
    def to_dict(self):
        return {
            "bind": dict(self.bind),
            "hearth_steps_left": self.hearth_steps_left,
            "known_nodes": sorted(self.known_nodes),
            "riding_rank": self.riding_rank,
            "owned_mounts": list(self.owned_mounts),
            "active_mount": self.active_mount,
            "mounted": self.mounted,
            "bind2": dict(self.bind2) if self.bind2 else None,
            "hearth2_steps_left": self.hearth2_steps_left,
            "collection_used": dict(self.collection_used),
            "active_form": self.active_form,
            "form_looks": dict(self.form_looks),
            "heroic_run": self.heroic_run,
            "heroic_locks": dict(self.heroic_locks),
            "active_title": self.active_title,
        }

    def load_from_dict(self, data):
        if not data:
            return
        bind = data.get("bind")
        if bind and bind.get("zone"):
            self.bind = {"zone": bind["zone"], "x": int(bind.get("x", 0)), "y": int(bind.get("y", 0)),
                         "name": bind.get("name", bind["zone"])}
        self.hearth_steps_left = max(0, int(data.get("hearth_steps_left", 0)))
        nodes = travel_data()["flight_nodes"]
        self.known_nodes = {n for n in data.get("known_nodes", []) if n in nodes}
        # CLAMP FROM THE DATA, NEVER A LITERAL. This said min(2, ...) and so a player who had
        # bought Master Riding loaded back as a Journeyman - silently, on every reload, for 200g.
        top = max(int(k) for k in travel_data()["riding_skills"])
        self.riding_rank = max(0, min(top, int(data.get("riding_rank", 0))))
        self.owned_mounts = [m for m in data.get("owned_mounts", []) if self.get_mount(m)]
        self.active_mount = data.get("active_mount") if self.get_mount(data.get("active_mount")) else None
        if self.active_mount is None and self.owned_mounts:
            self.active_mount = self.owned_mounts[-1]
        self.mounted = bool(data.get("mounted")) and self.riding_rank >= 1 and self.active_mount is not None
        b2 = data.get("bind2")
        self.bind2 = ({"zone": b2["zone"], "x": int(b2.get("x", 0)), "y": int(b2.get("y", 0)),
                       "name": b2.get("name", b2["zone"])} if b2 and b2.get("zone") else None)
        self.hearth2_steps_left = max(0, int(data.get("hearth2_steps_left", 0)))
        self.collection_used = {k: float(v) for k, v in (data.get("collection_used") or {}).items()}
        self.active_form = data.get("active_form")
        self.form_looks = {k: v for k, v in (data.get("form_looks") or {}).items() if isinstance(v, str)}
        self.heroic_run = data.get("heroic_run") if isinstance(data.get("heroic_run"), str) else None
        self.heroic_locks = {k: int(v) for k, v in (data.get("heroic_locks") or {}).items()
                             if isinstance(v, (int, float))}
        self.active_title = data.get("active_title")
        try:
            from world.collection import apply_feathers, form_ids
            apply_feathers(self)
            if self.active_form not in form_ids():
                self.active_form = None
        except Exception:
            pass


def services_for_npc(npc):
    """Services an NPC offers ('inn', 'flight', 'riding', 'mounts', 'train_class', 'train_prof'), looked up by vendor_id/npc_id."""
    npc_id = getattr(npc, "vendor_id", None) or getattr(npc, "npc_id", None)
    services = list(travel_data()["services"].get(npc_id, []))
    from world.training_manager import class_for_trainer
    if class_for_trainer(npc_id) and "train_class" not in services:
        services.append("train_class")
    from world.profession_manager import profession_for_trainer
    if profession_for_trainer(npc_id) and "train_prof" not in services:
        services.append("train_prof")
    # A jewelcrafting trainer is the town's jeweller: they'll take gems out of sockets for a fee
    # (world/jewelcrafting.py, Kyle 14 Nov 2026).
    from world.profession_manager import professions_for_trainer
    if "jewelcrafting" in (professions_for_trainer(npc_id) or []) and "jeweller" not in services:
        services.append("jeweller")
    return services


def find_flight_master(node, vendor_manager=None):
    """The NPC who runs this flight node, wherever they are defined.

    A flight master can be an ambient NPC or a vendor (one who also sells you jerky). Anything
    that needs to know where a flight lands - the flight screen, the map, the QA - asks here,
    so they cannot disagree about who the master is.
    """
    master_id = (node or {}).get("master")
    if not master_id:
        return None
    from world.ambient_npc_manager import get_ambient_npc_manager
    npc = get_ambient_npc_manager().npcs.get(master_id)
    if npc is not None:
        return npc
    if vendor_manager is None:
        try:
            from world.vendor_manager import get_vendor_manager
            vendor_manager = get_vendor_manager()
        except Exception:
            return None
    return getattr(vendor_manager, "vendors", {}).get(master_id)


def format_copper(copper):
    """Prices in the travel/mount shops. Was its own copy of the split and padded every value to
    all three parts, so "200g 0s 0c" at the riding trainer sat next to "3g" at the vendor."""
    from entities.coins import coins
    return coins(copper)


_travel_manager = None


def get_travel_manager():
    global _travel_manager
    if _travel_manager is None:
        _travel_manager = TravelManager()
    return _travel_manager


def reset_travel_manager(start_id=None):
    """Fresh state for a new character / before applying a loaded save.

    start_id binds the hearth to that start zone. Omitted - which is every pre-existing caller and
    every save load - it falls back to the data file's default bind exactly as before.
    """
    global _travel_manager
    _travel_manager = TravelManager(start_id)
    return _travel_manager


def _hearth_eases_breaks():
    """Hearthing home counts toward a recruit's break (world/bond_manager.BREAK_TICK, 23 Nov 2026)."""
    try:
        from world.bond_manager import get_bond_manager
        get_bond_manager().on_hearth()
    except Exception as exc:
        print(f"[Travel] break tick failed: {exc}")
