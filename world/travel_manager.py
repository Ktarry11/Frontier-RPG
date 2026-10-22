"""
TravelManager - hearthstone, flight paths (windriders) and mounts.

One process-lifetime singleton (same access pattern as get_quest_manager()), replaced with a fresh instance on
new-game / load so a second character never inherits the first one's bind, flight nodes or mounts.

Rules (Kyle's calls, 2026-10-21):
  * MOUNTS   - a riding skill (trainer, gold, level-gated) plus a mount bought from a stable/mount vendor.  Mounted
               = faster walking and fewer random encounters.  Never in caves/dungeons; dismounted on entering one.
  * HEARTH   - bind at any innkeeper (you stand on their tile).  Using it teleports you to the bind from any overworld
               zone, never from a cave/dungeon.  Cooldown is counted in overworld STEPS, not real time.
  * WINDRIDER- talking to a flight master discovers that node; pay gold to fly to any other discovered node.

All tuning lives in data/travel/travel_data.json.
"""
import json
from pathlib import Path

_DATA = None


def travel_data():
    global _DATA
    if _DATA is None:
        path = Path(__file__).parent.parent / "data" / "travel" / "travel_data.json"
        with open(path, "r", encoding="utf-8") as fh:
            _DATA = json.load(fh)
    return _DATA


class TravelManager:
    def __init__(self):
        data = travel_data()
        hearth = data["hearth"]
        self.cooldown_steps = int(hearth["cooldown_steps"])
        db = hearth["default_bind"]
        # Default bind: the Valley of Trials start tile (set properly by ZoneManager.reset_to_start's coordinates).
        self.bind = {"zone": db["zone"], "x": db["x"] if db["x"] is not None else 60,
                     "y": db["y"] if db["y"] is not None else 40, "name": db["name"]}
        self.hearth_steps_left = 0          # overworld steps until the hearth is ready again
        self.known_nodes = set()            # flight node ids discovered
        self.riding_rank = 0                # 0 none, 1 apprentice, 2 journeyman
        self.owned_mounts = []              # mount ids
        self.active_mount = None            # mount id the player prefers/summons
        self.mounted = False

    # ------------------------------------------------------------------ hearth
    def hearth_ready(self):
        return self.hearth_steps_left <= 0

    def set_bind(self, zone_name, x, y, place_name):
        self.bind = {"zone": zone_name, "x": int(x), "y": int(y), "name": place_name}

    def hearth_block_reason(self, in_cave):
        """None when the hearth can be used right now, otherwise a short player-facing reason."""
        if in_cave:
            return "You can't use your hearthstone inside a cave or dungeon."
        if not self.hearth_ready():
            return f"Your hearthstone is recharging ({self.hearth_steps_left} steps)."
        return None

    def use_hearth(self):
        """Spend the hearth: starts the cooldown, unmounts, returns the bind dict to teleport to."""
        self.hearth_steps_left = self.cooldown_steps
        self.mounted = False
        return dict(self.bind)

    def on_step(self):
        """Called once per successful overworld tile step."""
        if self.hearth_steps_left > 0:
            self.hearth_steps_left -= 1

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
        if copper < skill["price"]:
            return False, f"{skill['name']} costs {format_copper(skill['price'])}."
        return True, ""

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
        return None

    def can_buy_mount(self, mount, copper):
        if mount["id"] in self.owned_mounts:
            return False, "You already own this mount."
        if self.riding_rank < mount["tier"]:
            need = self.riding_skill(mount["tier"])
            return False, f"Requires {need['name']}."
        if copper < mount["price"]:
            return False, f"Costs {format_copper(mount['price'])}."
        return True, ""

    def buy_mount(self, mount):
        self.owned_mounts.append(mount["id"])
        # a better mount becomes the one you ride
        cur = self.get_mount(self.active_mount) if self.active_mount else None
        if cur is None or mount["tier"] >= cur["tier"]:
            self.active_mount = mount["id"]

    def current_mount(self):
        return self.get_mount(self.active_mount) if self.active_mount else None

    def mount_block_reason(self, in_cave):
        if self.riding_rank < 1:
            return "You haven't learned to ride yet. Find a riding trainer (level 20)."
        if not self.owned_mounts:
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
        mount = self.current_mount()
        if not (self.mounted and mount):
            return None
        return self.riding_skill(min(self.riding_rank, mount["tier"]))

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
    def flight_cost(from_node, to_node):
        nodes = travel_data()["flight_nodes"]
        a, b = nodes[from_node]["pos"], nodes[to_node]["pos"]
        dist = ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5
        cost = travel_data()["flight_cost"]
        return int(cost["base"] + cost["per_unit"] * dist)

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
        self.riding_rank = max(0, min(2, int(data.get("riding_rank", 0))))
        self.owned_mounts = [m for m in data.get("owned_mounts", []) if self.get_mount(m)]
        self.active_mount = data.get("active_mount") if self.get_mount(data.get("active_mount")) else None
        if self.active_mount is None and self.owned_mounts:
            self.active_mount = self.owned_mounts[-1]
        self.mounted = bool(data.get("mounted")) and self.riding_rank >= 1 and self.active_mount is not None


def services_for_npc(npc):
    """Travel services an NPC offers ('inn', 'flight', 'riding', 'mounts'), looked up by vendor_id/npc_id."""
    npc_id = getattr(npc, "vendor_id", None) or getattr(npc, "npc_id", None)
    return list(travel_data()["services"].get(npc_id, []))


def format_copper(copper):
    gold, rem = divmod(int(copper), 10000)
    silver, cop = divmod(rem, 100)
    parts = []
    if gold:
        parts.append(f"{gold}g")
    if silver or gold:
        parts.append(f"{silver}s")
    parts.append(f"{cop}c")
    return " ".join(parts)


_travel_manager = None


def get_travel_manager():
    global _travel_manager
    if _travel_manager is None:
        _travel_manager = TravelManager()
    return _travel_manager


def reset_travel_manager():
    """Fresh state for a new character / before applying a loaded save."""
    global _travel_manager
    _travel_manager = TravelManager()
    return _travel_manager
