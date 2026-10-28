"""
Recruitable companion NPCs.

Loads data/npcs/recruits.json and builds real `Character` objects on
recruitment - companions are full characters, not a parallel lightweight
class, so they share gear, abilities, resources, ranks and levelling with
the player.

Recruits arrive wearing a **themed starter set** appropriate to their role
(a tank in plate with a shield, a healer in cloth with a staff) rather than
naked or in generic filler. They're established adults who've been surviving
out here, so showing up with nothing would read wrong - but the gear is
deliberately Common quality, leaving all the real gearing to the player.

Zone-key normalization matters here: recruits.json keys zones as
`valley_of_trials` while ZoneManager passes "Valley of Trials". Vendors
shipped broken for exactly this reason, so `_zone_key` mirrors
VendorManager's normalization rather than inventing a second convention.
"""
import json
from pathlib import Path


#: Equipment slots each gear theme should be handed on recruitment, and the
#: weapon type to put in their main hand.
GEAR_THEMES = {
    "tank": {
        "slots": ["chest", "legs", "head", "hands", "feet"],
        "main_hand": "sword_1h",
        "off_hand": "shield",
    },
    "healer": {
        "slots": ["chest", "legs", "head", "feet"],
        "main_hand": "staff",
    },
    "melee_dps": {
        "slots": ["chest", "legs", "hands", "feet"],
        "main_hand": "dagger",
    },
    "ranged_dps": {
        "slots": ["chest", "legs", "hands", "feet"],
        "main_hand": "axe_1h",
    },
}


class RecruitNPC:
    """A companion the player can find and recruit."""

    def __init__(self, data):
        self.recruit_id = data["recruit_id"]
        self.name = data["name"]
        self.char_class = data["char_class"]
        self.spec = data.get("spec")
        self.level = data.get("level", 1)
        # Unplaced recruits ("placed": false) are fully authored but not
        # standing anywhere yet - zone/x/y may be null until the zone that
        # hosts them is built (several are earmarked for the Eastern
        # Kingdoms; "suggested_zone" is only a hint).
        self.placed = data.get("placed", True)
        self.suggested_zone = data.get("suggested_zone", "")
        self.zone = data.get("zone")
        self.x = data.get("x")
        self.y = data.get("y")
        self.row = data.get("row", "front")
        self.backstory = data.get("backstory", "")
        # Real 4-part background (Before/Adjustment/Now/Looking Forward -
        # see Character.background_sections). Optional per-recruit JSON
        # key, absent for every recruit authored before this system
        # existed - Character.get_background_section's "now" fallback to
        # self.backstory means those recruits keep working with zero
        # changes needed to their existing data.
        self.background_sections = data.get("background_sections", {})
        self.greeting = data.get("greeting", "")
        self.gear_theme = data.get("gear_theme")
        self.npc_color = data.get("npc_color", "#FFFFFF")  # Bright color for visibility

        # Appearance - recruits are always human regardless of zone
        # (Kyle's explicit call: they're real people from Earth, not
        # native to whatever Horde territory they're standing in, unlike
        # environmental/vendor NPCs which take the zone's race - see
        # VendorNPC and world/race_registry.get_zone_default_race).
        self.race = "human"
        self.gender = data.get("gender", "male")
        self.appearance_variant = data.get("appearance_variant", 0)
        self.facing = data.get("facing", "down")

        # Where this companion retires to if dismissed. Per Kyle: it depends
        # on the character - Dan wants a big city with a chain of command,
        # Silas wants a port with loose laws. A dismissed companion is not
        # deleted, they just go home, and can be found and re-hired there.
        self.home_town = data.get("home_town")
        self.home_x = data.get("home_x")
        self.home_y = data.get("home_y")
        self.home_note = data.get("home_note", "")

    def has_home(self):
        return bool(self.home_town
                    and self.home_x is not None
                    and self.home_y is not None)

    def home_location(self):
        """(zone, x, y) where this companion waits after being dismissed."""
        return (self.home_town, self.home_x, self.home_y)

    def _faction_gate_met(self):
        """False when a faction has reserved this companion for a given standing.

        The Codex will not release one of their own surveyors to somebody who is not in their record -
        see data/factions/factions.json, rewards.recruit.
        """
        from world.faction_manager import get_faction_manager
        return get_faction_manager().recruit_requirement_met(self.recruit_id)

    def is_available(self):
        """True if this recruit should currently appear/be interactable at
        all. Every recruit except Asher is always available (returns True
        unconditionally) - this hook exists specifically for his scripted
        join/leave window.

        Asher Coleman (Kyle, 2026-09-09: "Asher needs to ONLY join when we
        have the quests to kill the demons, he needs to be inside the
        dungeon itself, not outside"): only appears once the player has
        actually accepted the first quest in the Burning Blade Coven demon
        chain (vot_vile_familiars, "Fel Taint" - see
        data/quests/valley_of_trials.json), and disappears again once the
        chain's final quest (vot_yarrog_baneshadow, "Baneshadow" -
        next_quest_id chains Fel Taint -> Disrupting the Ritual ->
        Baneshadow, confirmed the actual last step) has been turned in, since his scripted departure
        (QuestManager.turn_in_quest) already removes him from the party at
        that point - he shouldn't be standing back at his old spot ready
        to rejoin immediately after leaving.

        Before Fel Taint is accepted: not yet available (nothing to fight
        yet). Between accepting Fel Taint and turning in Baneshadow:
        available. After Baneshadow is turned in: gone for good, per
        Kyle's "leaves the party to explore the world."
        """
        if not self.placed or self.zone is None:
            return False
        if not self._faction_gate_met():
            return False
        if self.recruit_id != "asher_coleman":
            return True

        from world.quest_manager import get_quest_manager
        quest_mgr = get_quest_manager()

        fel_taint = quest_mgr.quests.get("vot_vile_familiars")
        baneshadow = quest_mgr.quests.get("vot_yarrog_baneshadow")
        if fel_taint is None or baneshadow is None:
            # Quest data failed to load for some reason - fail closed
            # (not available) rather than let a broken quest state leave
            # him permanently recruitable outside his intended window.
            return False

        from world.quest import QuestStatus
        fel_taint_started = fel_taint.status != QuestStatus.NOT_STARTED
        baneshadow_done = baneshadow.status == QuestStatus.COMPLETED
        return fel_taint_started and not baneshadow_done

    def build_character(self):
        """
        Create the actual `Character` for this recruit, spec-locked and
        wearing a themed starter set.
        """
        from entities.character import Character

        char = Character(self.name, self.char_class, self.level)
        char.row = self.row

        # Spec lock: companions committed to a role back on Earth and stay
        # committed to it. They still earn talent points, but only their one
        # tree is spendable. The player has no locked_spec and keeps all three.
        char.locked_spec = self.spec
        char.recruit_id = self.recruit_id
        char.backstory = self.backstory
        char.background_sections = dict(self.background_sections)

        # Asher Coleman (Kyle, 2026-09-07): a fixed, unchangeable companion,
        # not a normal recruit. He gets his OWN two-ability kit (not the
        # standard Paladin/Retribution list) and a fixed, hand-authored gear
        # loadout the player can never alter - see _build_asher_kit for the
        # full rationale. Every other recruit falls through to the normal
        # path below unaffected.
        if self.recruit_id == "asher_coleman":
            self._build_asher_kit(char)
            return char

        self._equip_starter_gear(char)
        return char

    @staticmethod
    def build_asher_ability_book(char):
        """Rebuild just Asher's fixed ability_book + hotbar slots.

        Split out from _build_asher_kit (which also builds his permanent
        gear) so entities/character.py's Character.from_dict can call this
        alone on load - bug fix (Kyle: AttributeError 'NoneType' object
        has no attribute 'is_usable_by' on Asher's combat turn).
        from_dict's `char = cls(data["name"], data["class"], data["level"])`
        line runs the NORMAL Character.__init__, which gives Asher a
        generic Paladin ability_book (get_class_abilities), not his real
        two-ability one - but a couple lines later from_dict also restores
        his SAVED hotbar, which still points at "asher_wrath"/
        "asher_resignation". Those ability_ids don't exist in the generic
        book, so ability_book.get_ability() returns None for them, and the
        combat screen's hotbar rendering crashes calling .is_usable_by()
        on that None the first time his turn comes up post-load. Calling
        the FULL _build_asher_kit from from_dict would be wrong - it also
        re-generates his gear with fresh random item_ids every call,
        which would silently discard whatever was actually saved.
        """
        from combat.abilities import AbilityBook, _ability_from_data, _abilities_dir

        book = AbilityBook()
        try:
            with open(_abilities_dir() / "asher_unique.json", "r") as f:
                data = json.load(f)
            for entry in data.get("abilities", []):
                book.add_ability(_ability_from_data(entry))
        except Exception:
            pass  # fails soft to an empty book rather than crashing recruitment
        char.ability_book = book

        # His bar is EXACTLY his two abilities. Character.__init__ had already auto-filled the bar with the
        # generic Paladin list; those ids are not in this book, so they crashed the combat screen
        # (ability_book.get_ability() -> None) and showed up as blank "?" blocks on the skills screen.
        if hasattr(char, "hotbar"):
            size = max(len(char.hotbar), 20)
            char.hotbar = ["asher_wrath", "asher_resignation"] + [None] * (size - 2)
            char.hotbar_autofilled_ids = {"asher_wrath", "asher_resignation"}
        if hasattr(char, "extra_slots"):
            char.extra_slots = [None] * len(char.extra_slots)

    def _build_asher_kit(self, char):
        """Asher's unique, unchangeable ability book and gear.

        Two abilities ONLY (Asher's Wrath, Asher's Resignation) - not the
        normal Paladin ability list get_class_abilities(char_class) would
        otherwise populate Character.__init__ with. His ability_book is
        built fresh here and swaps out whatever Character.__init__ already
        assigned, loaded from data/abilities/asher_unique.json rather than
        the per-class pipeline in combat/abilities.py, since these
        abilities are his alone and should never be learnable, discoverable,
        or usable by any player-made Paladin.

        Gear is hand-authored to Kyle's exact spec (blue chest, blue legs,
        blue mace_2h, white ring) rather than pulled from GEAR_THEMES like
        every other recruit's randomized starter kit - his loadout is
        fixed and permanent (the player can never re-equip him), so there's
        no "starter kit that gets replaced later" concept to design for
        here the way there is for a normal recruit.
        """
        RecruitNPC.build_asher_ability_book(char)

        from entities.item import Item
        from gear_icons import pick_armor_icon, pick_weapon_icon
        import uuid

        ITEM_LEVEL = 5

        def armor_item(slot, primary_stats, name):
            item_id = f"asher_{slot}_{uuid.uuid4().hex[:6]}"
            return Item(
                item_id=item_id, name=name, slot=slot, item_level=ITEM_LEVEL,
                rarity="rare", armor_type="plate", weapon_type=None,
                stat_template=None, primary_stats=primary_stats,
                secondary_stats={}, armor_value=10, required_level=1,
                sell_price=0, flavor_text="",
                icon_id=pick_armor_icon(slot, "plate"),
            )

        chest = armor_item("chest", {"strength": 2, "stamina": 1}, "Family Breastplate")
        legs = armor_item("legs", {"strength": 2, "stamina": 1}, "Family Greaves")

        weapon = Item(
            item_id=f"asher_mainhand_{uuid.uuid4().hex[:6]}",
            name="Judgment's Weight", slot="main_hand", item_level=ITEM_LEVEL,
            rarity="rare", armor_type=None, weapon_type="mace_2h",
            stat_template=None, primary_stats={"strength": 4},
            secondary_stats={}, armor_value=0, required_level=1,
            sell_price=0, flavor_text="",
            weapon_damage_min=30, weapon_damage_max=41, attack_speed=3.6,
            # Fixed, not pick_weapon_icon()'s random pool pick (Kyle,
            # 2026-09-09: "Let's also give his mace a unique icon") - a
            # gold, gem-set ceremonial hammer specifically, not whatever
            # random gear_inv_hammer_* the pool would otherwise roll. His
            # gear is already permanent/unchangeable (see equip_item's
            # recruit_id guard in entities/character.py); the icon should
            # be equally fixed, not re-rolled if this method ever runs
            # again.
            icon_id="gear_inv_hammer_05",
        )

        # The ring: white (common), zero stats on purpose - this is not
        # gear, it's the one object in his kit that belongs to Rachel and
        # not to the mission. Never explained in dialogue pre-reveal (see
        # the handoff profile, Section 7) - players should be free to form
        # their own theories about it long before any answer exists.
        ring = Item(
            item_id=f"asher_ring_{uuid.uuid4().hex[:6]}",
            name="Worn Wedding Ring", slot="ring", item_level=1,
            rarity="common", armor_type=None, weapon_type=None,
            stat_template=None, primary_stats={}, secondary_stats={},
            armor_value=0, required_level=1, sell_price=0,
            flavor_text="",
            icon_id=None,
        )

        for item in (chest, legs, weapon, ring):
            char.equipment.equip(item)

    def _equip_starter_gear(self, char):
        """Generate and equip a Common-quality themed kit."""
        from entities.loot_generator import LootGenerator

        theme = GEAR_THEMES.get(self.gear_theme)
        if not theme:
            return

        generator = LootGenerator()
        ilvl = max(1, self.level)

        for slot in theme["slots"]:
            try:
                item = generator.generate_item_for_class(
                    self.char_class, ilvl, slot=slot, rarity="common")
            except Exception:
                continue
            if item:
                # add_to_inventory can now fail if char's bag is full (see
                # Character.inventory_capacity) - equip_item() below already
                # requires the item to be in inventory first and no-ops
                # otherwise, so a full bag here just means this one starter
                # piece doesn't apply, not a crash. Shouldn't normally
                # happen for a freshly-created recruit's empty bag.
                char.add_to_inventory(item)
                char.equip_item(item)

        for slot_key in ("main_hand", "off_hand"):
            weapon_type = theme.get(slot_key)
            if not weapon_type:
                continue
            try:
                item = generator.generate_item_for_class(
                    self.char_class, ilvl, slot=slot_key, rarity="common")
            except Exception:
                continue
            if item:
                char.add_to_inventory(item)
                char.equip_item(item)


class RecruitManager:
    """
    Loads recruit definitions and tracks where every companion currently is.

    A recruit is in exactly one of three states:

      AVAILABLE  - never hired; standing at their wild spawn point
      IN_PARTY   - hired; not present in the world at all
      DISMISSED  - let go; standing in their HOME TOWN, re-hireable there

    Dismissal deliberately does NOT delete the companion. Their full
    serialized Character is kept in `dismissed_characters`, so re-hiring Dan
    at level 34 in his plate gets you a level 34 Dan in his plate - not a
    fresh level 2 one. Without that, dismissing anyone would be a trap that
    silently destroys hours of levelling and gear.
    """

    AVAILABLE = "available"
    IN_PARTY = "in_party"
    DISMISSED = "dismissed"

    def __init__(self):
        self.recruits = {}
        self.recruited_ids = set()
        # recruit_id -> Character.to_dict() snapshot taken at dismissal
        self.dismissed_characters = {}
        self._load()

    def _load(self):
        path = Path(__file__).parent.parent / "data" / "npcs" / "recruits.json"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for entry in data.get("recruits", []):
            self.recruits[entry["recruit_id"]] = RecruitNPC(entry)

    @staticmethod
    def _zone_key(zone):
        """Normalize "Valley of Trials" -> "valley_of_trials"."""
        return str(zone).lower().replace(" ", "_").replace("'", "")

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def state_of(self, recruit_id):
        if recruit_id in self.recruited_ids:
            return self.IN_PARTY
        if recruit_id in self.dismissed_characters:
            return self.DISMISSED
        return self.AVAILABLE

    def current_location(self, recruit):
        """
        (zone, x, y) where this recruit can currently be found, or None if
        they're in the party and therefore not standing anywhere.
        """
        state = self.state_of(recruit.recruit_id)
        if state == self.IN_PARTY:
            return None
        if state == self.DISMISSED:
            if not recruit.has_home():
                # No home defined: they wait where you first found them
                # rather than vanishing from the game entirely.
                return (recruit.zone, recruit.x, recruit.y)
            return recruit.home_location()
        return (recruit.zone, recruit.x, recruit.y)

    def all_world_positions(self):
        """
        Every tile a recruit could EVER occupy - wild spawn and home town.

        ZoneManager carves and marks all of these at startup, so a companion
        is never stranded on a tile that terrain scatter sealed off. Both
        positions are carved unconditionally because dismissal can happen at
        any time and zones are only generated once, at launch.
        """
        positions = []
        for recruit in self.recruits.values():
            if not recruit.placed or recruit.zone is None:
                continue  # authored but not yet standing anywhere
            positions.append((recruit.zone, recruit.x, recruit.y))
            if recruit.has_home():
                positions.append(recruit.home_location())
        return positions

    # ------------------------------------------------------------------
    # Lookup
    # ------------------------------------------------------------------

    def get_recruits_in_zone(self, zone):
        """Recruits currently STANDING in this zone (wild or home town) AND
        currently available (see RecruitNPC.is_available - filters Asher
        out entirely outside his scripted join/leave window, so he's not
        just unrecruitable but genuinely invisible/absent, same as if he
        weren't placed there at all)."""
        key = self._zone_key(zone)
        found = []
        for recruit in self.recruits.values():
            if not recruit.is_available():
                continue
            location = self.current_location(recruit)
            if location and self._zone_key(location[0]) == key:
                found.append(recruit)
        return found

    def get_recruit_at_location(self, zone, x, y):
        """The recruit standing on this tile, if any and currently
        available (see RecruitNPC.is_available)."""
        key = self._zone_key(zone)
        for recruit in self.recruits.values():
            if not recruit.is_available():
                continue
            location = self.current_location(recruit)
            if not location:
                continue
            r_zone, rx, ry = location
            if self._zone_key(r_zone) == key and rx == x and ry == y:
                return recruit
        return None

    # ------------------------------------------------------------------
    # Transitions
    # ------------------------------------------------------------------

    def mark_recruited(self, recruit_id):
        """Hire (or re-hire) a companion - they leave the world."""
        self.recruited_ids.add(recruit_id)
        self.dismissed_characters.pop(recruit_id, None)

    def dismiss(self, character):
        """
        Send a companion home, preserving everything about them.

        Returns the RecruitNPC they map back to, or None for a character with
        no recruit_id (which should not happen for a companion, but a party
        member built by hand in a test would hit it).
        """
        recruit_id = getattr(character, "recruit_id", None)
        if not recruit_id or recruit_id not in self.recruits:
            return None
        self.recruited_ids.discard(recruit_id)
        self.dismissed_characters[recruit_id] = character.to_dict()
        return self.recruits[recruit_id]

    def build_or_restore(self, recruit):
        """
        The Character to hand the player when they hire this recruit.

        A previously dismissed companion is rebuilt from their stored
        snapshot so they return at the level and in the gear they left with.
        A first-time hire is generated fresh.
        """
        snapshot = self.dismissed_characters.get(recruit.recruit_id)
        if snapshot:
            from entities.character import Character
            try:
                return Character.from_dict(snapshot)
            except Exception as exc:
                # Never let a bad snapshot block re-hiring; fall back to a
                # fresh build rather than making the NPC permanently dead.
                print(f"Could not restore {recruit.name} from snapshot "
                      f"({exc}); rebuilding from scratch.")
        return recruit.build_character()

    def is_recruited(self, recruit_id):
        return recruit_id in self.recruited_ids

    def is_dismissed(self, recruit_id):
        return recruit_id in self.dismissed_characters

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        return {
            "recruited_ids": sorted(self.recruited_ids),
            "dismissed_characters": self.dismissed_characters,
        }

    def load_state(self, data):
        self.recruited_ids = set(data.get("recruited_ids", []))
        self.dismissed_characters = dict(data.get("dismissed_characters", {}))


_recruit_manager = None


def get_recruit_manager():
    """Get or create the global RecruitManager instance."""
    global _recruit_manager
    if _recruit_manager is None:
        _recruit_manager = RecruitManager()
    return _recruit_manager
