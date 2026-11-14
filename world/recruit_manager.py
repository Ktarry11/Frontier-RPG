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

COMPANIONS KEEP PACE WITH YOU, AND YOU CANNOT SKIP AHEAD TO THEM.
Two rules, both Kyle's, and they are halves of the same idea - that who you
travel with should be a choice about PEOPLE, never a race to the strongest
body you can find:

  CATCH-UP   a recruit you have not hired yet is never more than CATCHUP
             levels below you, but never below the level they were authored
             at. Silas stands in Ratchet at 12; meet him at 30 and he is 26.
             Kyle: "if a player gets to level 30 and realize they want to try
             a rogue, they don't want to level him from lvl 12."
  THE GATE   you cannot hire somebody more than CATCHUP levels above you.
             Kaelen starts at 36, so at 31 he will not come - he is five
             levels up and that is one too many. At 32 he will.

The two interlock: catch-up means anyone BELOW you is always within reach, so
the gate only ever bites on a recruit authored above you. That is the whole
point - it stops a level 20 player walking to the end of the map to collect a
level 45 companion, without ever stranding a low-level one as unusable.

CATCH-UP APPLIES TO SOMEBODY YOU DISMISSED TOO. Kyle: "these are real people
bro. They're not just sitting there doing nothing." Dismiss Silas at 20, come
back at 45, and he has not been standing in a doorway in Ratchet for twenty
levels - he has been working. He returns caught up, and in kit that matches.

The worry that kept this out at first was that raising a snapshot's level
without its gear hands the player a level 41 companion in level 20 plate. So
the gear comes with it, on two rules that keep it from being a theft:

  RARITY IS PRESERVED. Each piece is re-rolled at their new level AT THE SAME
  RARITY, so a rare you handed them comes back a rare. Only the numbers move.
  THE OLD KIT IS GONE. It is not retired into their pack. Kyle, overruling the
  careful version of this: "if these people are in the party, and I dismiss
  them at level 20 in greens. I come back at level 50 and they are level 46.
  They very much can destroy shit we give them lol. No one is keeping lvl 20
  gear for no reason." He is right - hoarding it would be the one unrealistic
  thing in a feature whose entire point is that these are people living their
  own lives, and it would hand the player back six bags of dead weight.

Zone-key normalization matters here: recruits.json keys zones as
`valley_of_trials` while ZoneManager passes "Valley of Trials". Vendors
shipped broken for exactly this reason, so `_zone_key` mirrors
VendorManager's normalization rather than inventing a second convention.
"""
import json
from pathlib import Path
from world.zone_keys import zone_key as _zk


#: Equipment slots each gear theme should be handed on recruitment, and the
#: weapon type to put in their main hand.
#: Armour every companion turns up wearing, whatever their role. Kyle, 2026-10-31: "when players
#: join our party, it should be reasonable with their gear. a lvl 32 shouldnt start with this
#: lol." A level 32 Barbarian was arriving in FIVE pieces - chest, legs, hands, feet and a
#: weapon - with head, shoulders, back, wrist, waist, neck, both rings and both trinkets all
#: empty, which is not a starter kit, it is a character who lost a fight with a wardrobe.
#: Everyone now fills the armour slots; the accessories below are what still varies.
BASE_ARMOR_SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet", "back"]

#: The accessories, added on top. Kept separate because they are the slots a player is most
#: likely to want to fill themselves, so a companion arrives with something rather than
#: everything.
ACCESSORY_SLOTS = ["neck", "ring1"]

#: THE WEAPON ENTRIES HERE ARE A FALLBACK ONLY. A spec's real weapons come
#: from data/items/spec_gear.json via entities/spec_gear.py, which knows what
#: each spec is proficient in, whether it dual wields and which slot its
#: actual weapon sits in; these four generic entries cannot express any of
#: that (note ranged_dps below reaching for a one-handed AXE) and are read
#: only for a recruit with no spec at all. `slots` is still live for
#: everybody - it is the armour list, which is a role fact, not a spec one.
GEAR_THEMES = {
    "tank": {
        "slots": BASE_ARMOR_SLOTS + ACCESSORY_SLOTS,
        "main_hand": "sword_1h",
        "off_hand": "shield",
    },
    "healer": {
        "slots": BASE_ARMOR_SLOTS + ACCESSORY_SLOTS,
        "main_hand": "staff",
    },
    "melee_dps": {
        "slots": BASE_ARMOR_SLOTS + ACCESSORY_SLOTS,
        "main_hand": "dagger",
    },
    "ranged_dps": {
        "slots": BASE_ARMOR_SLOTS + ACCESSORY_SLOTS,
        "main_hand": "axe_1h",
    },
}


def starter_rarity(level, slot=None):
    """What quality a companion met at `level` is wearing in `slot`.

    A companion was previously dressed entirely in COMMON at every level, which is why a level
    32 Barbarian read as a level 1 one: common gear is named from one fixed prefix pool
    ("Simple", "Plain") at every item level, so his level 32 chestpiece was called a Simple
    Breastplate. The fix is the quality, not the naming - "Simple" is the right word for a
    level 4 recruit and the wrong word for a level 32 one.

    Rises with level because somebody who has survived to 40 out here has found better than
    vendor stock, and the weapon runs one step ahead of the armour because it is the piece a
    player looks at first and the one that most defines what the companion can do.
    """
    tiers = ["common", "uncommon", "rare"]
    idx = 0 if level < 12 else (1 if level < 38 else 2)
    # The ranged slot is a WEAPON and gets the weapon bump. It was left out
    # because nothing ever generated for the slot, so the omission could not
    # show - a Hunter's bow is as much "the piece a player looks at first"
    # as a Warrior's sword is.
    if slot in ("main_hand", "off_hand", "ranged") and idx < len(tiers) - 1:
        idx += 1
    return tiers[idx]


#: How far a companion may sit from the player in either direction: they level
#: up to within this many levels below you, and you cannot hire one this many
#: levels above you. One number, both rules, because they are the same promise
#: read from each end - see the module docstring.
CATCHUP = 4


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

    def effective_level(self, player_level=None):
        """The level this companion is actually at when the player meets them.

        Their authored level, raised so they are never more than CATCHUP below
        the player. Never lowered: a companion authored above you waits at
        their own level until you have caught up to them.
        """
        if player_level is None:
            return self.level
        return max(self.level, int(player_level) - CATCHUP)

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

    def build_character(self, player_level=None):
        """
        Create the actual `Character` for this recruit, spec-locked and
        wearing a themed starter set.

        `player_level` applies the catch-up rule; omitting it builds them at
        their authored level, which is what the audit tools want.
        """
        from entities.character import Character

        char = Character(self.name, self.char_class,
                         self.effective_level(player_level))
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
        # Built, not blank - see _catch_up for why. A recruit hired at their authored level 38
        # had the same empty tree a caught-up one did; this is the same fix at the other door.
        char.auto_spend_talents()

        # THE PERSONAL KIT. data/npcs/personal_kits.json was authored, committed
        # and complete - 67 recruits, 201 abilities, 67 named passives - and
        # nothing in the codebase read it, so every companion played exactly
        # like a stock character of their class and spec. That is the one thing
        # the kits exist to prevent. Kyle, 6 Nov: "Give each human about 4
        # UNIQUE abilities that are based on who they are as people... it'll
        # let me build more people of same class/spec."
        #
        # After auto_spend_talents, not before: talent spending re-syncs the
        # ability book, and a kit granted first would be rebuilt away.
        #
        # Asher never reaches here - he returns above with his own two-ability
        # book - and world/personal_kits.py also excludes him by id.
        from world.personal_kits import grant
        grant(char)
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
            with open(_abilities_dir() / "asher_unique.json", "r", encoding="utf-8") as f:
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
                # Seeded, so every Asher everywhere wears the same plate. His loadout is
                # documented right above as fixed and unalterable, but this call was a plain
                # random pick, so his breastplate came out plate11 on one build and plate14 on
                # the next and nobody could tell because a save keeps whatever it rolled. Kyle
                # already asked for exactly this on the mace below; the armour never got it.
                icon_id=pick_armor_icon(slot, "plate", seed=f"asher_coleman:{slot}"),
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
        """Generate and equip a themed kit that matches the spec's playstyle.

        WHAT THIS LOOKED LIKE BEFORE, measured across all 68 companions,
        because every line below is written against one of these:

          * THE WEAPON WAS RANDOM. `weapon_type = theme.get(slot_key)` was
            read, used as a truthiness guard, and never passed to the
            generator, so every companion's weapon was whatever
            _pick_weapon_type_for_class happened to roll for the class. A
            Fury Warrior arrived with a staff, a Resto Druid with a fist
            weapon, a Subtlety Rogue with a mace.
          * THE RANGED SLOT WAS EMPTY ON ALL 68. Kyle, 6 Nov: "an inventor
            tinkerer (healer) doesn't come with a gun". Nothing ever
            generated for the slot.
          * FOUR TANKS HAD NO WEAPON. Prot Paladin, Cultist Dreadnought,
            Moon Guard and Oathkeeper: the generator rolled a two-hander
            into the main hand and the shield that came after displaced it
            (see Equipment.equip's 2H interaction), and nothing re-rolled.
            Hence main hand first, off hand second, and a plan that never
            pairs a two-hander with an off-hand item at all.
          * EIGHT TANKS HAD NO SHIELD, three of them holding a TOME - a
            tank with a passive stat stick. The profile gives a shieldless
            tank a real two-hander instead.
          * 14 COMPANIONS WORE TWO STAT TEMPLATES AT ONCE, because the
            armour took the class map's value and each weapon then silently
            swapped in whatever its own valid_stat_templates listed first.
            One template now comes from the profile and goes to every piece.
          * OFF-SCHOOL SPELL POWER. Kyle: "Ive seen a fire mage come with
            +holy spell power gear."
        """
        from entities.loot_generator import LootGenerator
        from entities.spec_gear import profile as spec_profile
        from entities.proficiency import can_dual_wield

        prof = spec_profile(getattr(self, "spec", None))
        theme = GEAR_THEMES.get(self.gear_theme) or GEAR_THEMES.get(prof["role"])
        if not theme:
            return

        generator = LootGenerator()
        # THE CHARACTER'S level, not the authored one. Catch-up means a Silas
        # met at 30 is level 26, and reading self.level here would have sent
        # him out in the level 12 kit he was written with.
        ilvl = max(1, char.level)
        itemize = {"stat_template": prof.get("stat_template"),
                   "school": prof.get("school")}

        for slot in theme["slots"]:
            try:
                item = generator.generate_item_for_class(
                    self.char_class, ilvl, slot=slot,
                    rarity=starter_rarity(ilvl, slot), **itemize)
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

        # MAIN HAND FIRST. Equipment.equip takes a two-hander off the
        # character when an off-hand item goes on, so any order that puts
        # the off hand first can silently empty the main hand - which is
        # exactly what left four tanks unarmed.
        for slot_key in ("main_hand", "off_hand", "ranged"):
            weapon_type = (prof["weapons"].get(slot_key)
                           or theme.get(slot_key))
            if not weapon_type:
                continue
            # A ONE-HANDER IN THE OFF HAND IS DUAL WIELDING, and dual wield
            # is trained at 20 and spec-gated (entities/proficiency.py's
            # can_dual_wield, off data/items/weapon_types.json's allow-list -
            # Kyle's dual wielders are Enhancement Shaman, Primalist and
            # Rogue, plus the specs the table already lists). equip_item
            # would refuse it anyway; checking here means a level 12
            # companion does not turn up carrying a second sword in her bag
            # that she cannot hold.
            if (slot_key == "off_hand" and weapon_type not in ("shield", "tome")
                    and not can_dual_wield(char)):
                continue
            try:
                item = generator.generate_item_for_class(
                    self.char_class, ilvl, slot=slot_key,
                    rarity=starter_rarity(ilvl, slot_key),
                    weapon_type=weapon_type, **itemize)
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
        return _zk(zone)

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
        from world.bond_manager import get_bond_manager
        bonds = get_bond_manager()
        for recruit in self.recruits.values():
            if not recruit.is_available():
                continue
            b = bonds.get(recruit.recruit_id)
            if b is not None and b.away and not self.is_recruited(recruit.recruit_id):
                continue        # on a break: their spot stands empty (bonds design, "gone means gone")
            location = self.current_location(recruit)
            if location and self._zone_key(location[0]) == key:
                found.append(recruit)
        return found

    def get_recruit_at_location(self, zone, x, y):
        """The recruit standing on this tile, if any and currently
        available (see RecruitNPC.is_available)."""
        key = self._zone_key(zone)
        from world.bond_manager import get_bond_manager
        bonds = get_bond_manager()
        for recruit in self.recruits.values():
            if not recruit.is_available():
                continue
            b = bonds.get(recruit.recruit_id)
            if b is not None and b.away and not self.is_recruited(recruit.recruit_id):
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

    @staticmethod
    def _catch_up(character, target_level, regear=True):
        """Bring a returning companion up to `target_level`, gear included.

        Levels go through Character.level_up() one at a time rather than by
        assigning to .level: that is the only path that scales core stats,
        recalculates derived ones, unlocks ability ranks, grants talent points
        and syncs pets. Setting the attribute directly would return a level 45
        companion with a level 20 body and a level 20 pet.
        """
        from entities.loot_generator import LootGenerator

        gained = character.level < target_level
        guard = 0
        while character.level < target_level and guard < 200:
            character.level_up()
            guard += 1

        # AND THEY SPENT THE POINTS. level_up() grants a talent point per level but nothing
        # places it, so a companion caught up from 20 to 46 arrived with 42 unspent points and an
        # empty tree - which on a level 46 healer is not a blank slate, it is a level 46 healer
        # missing most of their healing, in a party the player is relying on. They come built,
        # down their own locked spec. Kyle's free reset refunds the lot if he wants to redo it by
        # hand.
        #
        # Asher excepted, same as the regear above and for the same reason: he is a fixed,
        # hand-authored companion who has to come back exactly as he left, and a build is part of
        # "exactly". build_character does not need this guard because he returns early there.
        if getattr(character, "recruit_id", None) != "asher_coleman":
            character.auto_spend_talents()

        if not (gained and regear):
            return character

        gen = LootGenerator()
        for slot, item in list(character.equipment.slots.items()):
            if item is None or item.item_level >= character.level - CATCHUP:
                continue
            try:
                fresh = gen.generate_item_for_class(
                    character.char_class, character.level, slot=slot,
                    rarity=item.rarity)          # what the player invested stays invested
            except Exception:
                continue
            if fresh is None:
                continue
            # Straight into the slot. NOT through equip_item, which would push
            # the old piece into their pack - they replaced that gear years ago
            # and did not carry the corpse of it around. See the module
            # docstring for Kyle overruling the version that kept it.
            character.equipment.slots[slot] = fresh

        # And they did not keep the contents of the pack either. Same rule, same
        # reason: somebody who gained twenty-six levels sold the level 20 commons
        # they were carrying rather than hauling them the whole way. Anything
        # without an item_level (quest items and the like) is left alone, because
        # that is not gear and not theirs to throw out.
        character.inventory = [
            it for it in character.inventory
            if getattr(it, "item_level", None) is None
            or it.item_level >= character.level - CATCHUP]

        character._recalculate_derived_stats()
        character.current_health = character.health
        character.current_mana = character.mana
        return character

    def join_level(self, recruit, player_level=None):
        """The level this companion would ACTUALLY join at, right now.

        Their catch-up level, or the level they left with if that is higher -
        somebody dismissed at 46 does not shrink back to 26 to suit a level 30
        player (Kyle: "they won't de-level, no").

        THE GATE READS THIS, not RecruitNPC.effective_level, and that is the
        whole reason this method exists on the manager instead. effective_level
        knows only what a companion was authored at, so it said a level 46
        veteran was a level 26 hire and waved a level 30 player straight past
        the gate - who then got the level 46 character anyway. The rule and the
        number it judges have to come from the same place.
        """
        lvl = recruit.effective_level(player_level)
        snap = self.dismissed_characters.get(recruit.recruit_id)
        if snap and snap.get("level"):
            lvl = max(lvl, int(snap["level"]))
        return lvl

    def block_reason(self, recruit, player_level=None):
        """None if this companion will come with you, else a line saying why not."""
        if player_level is None:
            return None
        lvl = self.join_level(recruit, player_level)
        gap = lvl - int(player_level)
        if gap > CATCHUP:
            return (f"{recruit.name} is level {lvl} and will not follow somebody "
                    f"{gap} levels below them. Come back at level {lvl - CATCHUP}.")
        return None

    def build_or_restore(self, recruit, player_level=None):
        """
        The Character to hand the player when they hire this recruit.

        A previously dismissed companion is rebuilt from their stored
        snapshot - keeping every choice the player made for them - and then
        caught up, because they have been living their own life while away.
        A first-time hire is generated fresh, at their catch-up level.
        """
        # Refuse here too, not only at the button: this is the only place a
        # companion actually joins, so it is the only place the rule is sure to
        # hold however the call is made.
        if self.block_reason(recruit, player_level):
            return None
        snapshot = self.dismissed_characters.get(recruit.recruit_id)
        if snapshot:
            from entities.character import Character
            try:
                char = Character.from_dict(snapshot)
                # Asher's loadout is fixed and hand-authored and the player can
                # never alter it, so he catches up in level but not in kit.
                return self._catch_up(char, self.join_level(recruit, player_level),
                                      regear=recruit.recruit_id != "asher_coleman")
            except Exception as exc:
                # Never let a bad snapshot block re-hiring; fall back to a
                # fresh build rather than making the NPC permanently dead.
                print(f"Could not restore {recruit.name} from snapshot "
                      f"({exc}); rebuilding from scratch.")
        return recruit.build_character(player_level)

    def is_recruited(self, recruit_id):
        return recruit_id in self.recruited_ids

    def is_dismissed(self, recruit_id):
        return recruit_id in self.dismissed_characters

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_dict(self):
        from world.bond_manager import get_bond_manager
        return {
            "recruited_ids": sorted(self.recruited_ids),
            "dismissed_characters": self.dismissed_characters,
            # friendship rides along in the recruit block, so the save format needs no new key
            "bonds": get_bond_manager().to_dict(),
        }

    def load_state(self, data):
        self.recruited_ids = set(data.get("recruited_ids", []))
        self.dismissed_characters = dict(data.get("dismissed_characters", {}))
        from world.bond_manager import get_bond_manager
        get_bond_manager().load_state(data.get("bonds"))


_recruit_manager = None


def get_recruit_manager():
    """Get or create the global RecruitManager instance."""
    global _recruit_manager
    if _recruit_manager is None:
        _recruit_manager = RecruitManager()
    return _recruit_manager


def reset_recruit_manager():
    """Fresh recruit state for a new character / before applying a loaded save.

    THIS MANAGER IS A PROCESS-LIFETIME SINGLETON AND ITS STATE IS A DELETION
    LIST. `recruited_ids` makes a companion IN_PARTY, and an IN_PARTY recruit
    has no world location at all - `current_location` returns None, so they
    are not drawn, not interactable and not in `get_recruits_in_zone`. Carry
    one character's hires into another character and those companions are
    simply missing from the world, with nothing logged and nothing to see.

    That is exactly what happened: creating a new character reset the zone,
    quest and travel managers and never this one, so a new level 1 started in
    a world emptied of every companion the PREVIOUS character had hired, and
    the empty state was then written into the new save. Reported live as "all
    recruits are gone with new character creation".

    `dismissed_characters` is the same failure wearing a different coat -
    a dismissed recruit stands in their home town instead of where they were
    authored, so they do not vanish, they MOVE, which is worse to diagnose.
    """
    global _recruit_manager
    _recruit_manager = RecruitManager()
    from world.bond_manager import reset_bond_manager
    reset_bond_manager()        # friendship belongs to a character, same as hires
    return _recruit_manager
