"""
Loot generator. Procedurally generates Item instances using the data-driven
armor type / weapon type / stat template / rarity / slot definitions in
data/items/*.json. Mirrors the approach used by world/creature_manager.py
for creatures - no hardcoded item stats in Python.
"""
import json
import random
import uuid
from pathlib import Path
from entities.item import Item
from gear_icons import pick_armor_icon, pick_weapon_icon


ARMOR_SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet", "back"]
# "ring" and "trinket" are GENERIC slot identities, not "ring1"/"ring2" -
# Equipment._resolve_slot() maps a generic item to whichever concrete paired
# slot (ring1/ring2, trinket1/trinket2) is open at equip time. Previously an
# item was generated already hardcoded to ring1 or ring2 specifically, so a
# ring1-flavored drop could never fill an empty ring2 - the "can only equip
# one ring" bug.
ACCESSORY_SLOTS = ["neck", "ring", "trinket"]
WEAPON_SLOTS = ["main_hand", "off_hand", "ranged"]

# Simple flavor name pools so generated items don't all say "Item of Strength"
ARMOR_NAME_PREFIXES = {
    "poor": ["Tattered", "Worn", "Crude"],
    "common": ["Sturdy", "Plain", "Simple"],
    "uncommon": ["Reinforced", "Well-Made", "Hardened"],
    "rare": ["Superior", "Masterwork", "Battleworn"],
    "epic": ["Heroic", "Ancient", "Runed"],
    "legendary": ["Mythic", "Godforged", "Eternal"],
}
ARMOR_NAME_NOUNS = {
    "head":     {"str_physical": "Helm",     "agi_physical": "Hood",          "int_caster": "Circlet",    "spi_healer": "Cowl",       "_default": "Cap"},
    "shoulder": {"str_physical": "Pauldrons","agi_physical": "Shoulderguards","int_caster": "Mantle",     "spi_healer": "Shoulderpads","_default": "Shoulderguards"},
    "chest":    {"str_physical": "Breastplate","agi_physical":"Chestguard",   "int_caster": "Robe",       "spi_healer": "Vestments",  "_default": "Tunic"},
    "wrist":    {"str_physical": "Bracers",  "agi_physical": "Wristguards",   "int_caster": "Cuffs",      "spi_healer": "Bindings",   "_default": "Bracers"},
    "hands":    {"str_physical": "Gauntlets","agi_physical": "Gloves",        "int_caster": "Handwraps",  "spi_healer": "Gloves",     "_default": "Gloves"},
    "waist":    {"str_physical": "Girdle",   "agi_physical": "Belt",          "int_caster": "Sash",       "spi_healer": "Cord",       "_default": "Belt"},
    "legs":     {"str_physical": "Legplates","agi_physical": "Legguards",     "int_caster": "Leggings",   "spi_healer": "Trousers",   "_default": "Leggings"},
    "feet":     {"str_physical": "Greaves",  "agi_physical": "Boots",         "int_caster": "Sandals",    "spi_healer": "Slippers",   "_default": "Boots"},
    "back":  {"_default": "Cloak"},
    "neck":  {"_default": "Amulet"},
    "ring":  {"_default": "Ring"},
    # Keyed on the GENERIC slot identity, matching ACCESSORY_SLOTS above and
    # Equipment.PAIRED_SLOTS - an item's slot is "ring"/"trinket", never
    # "ring1"/"trinket2". Deliberately NOT normalised to accept a concrete
    # paired slot: an item generated with slot="trinket1" is a real bug (it
    # can never fill an empty trinket2 - see ACCESSORY_SLOTS' comment), and
    # falling through to "Item" here is a loud, useful signal that it
    # happened rather than something to paper over.
    "trinket": {"_default": "Charm"},
}
WEAPON_NAME_NOUNS = {
    "sword_1h": ["Sword", "Blade", "Shortsword"],
    "sword_2h": ["Greatsword", "Longsword"],
    "axe_1h": ["Axe", "Hatchet"],
    "axe_2h": ["Battleaxe", "Great Axe"],
    "mace_1h": ["Mace", "Hammer"],
    "mace_2h": ["Maul", "Warhammer"],
    "dagger": ["Dagger", "Shiv", "Knife"],
    "fist_weapon": ["Knuckles", "Claws"],
    "staff": ["Staff", "Rod"],
    "wand": ["Wand", "Rod"],
    "totem": ["Totem", "Fetish"],
    "tome": ["Tome", "Grimoire", "Codex"],
    # Relics, added 29 Oct 2026. tools/validate_content.py already checks that
    # every weapon type has an entry here, which is why the five ranged types
    # below were caught; libram and idol would have fallen through to the
    # generic "Weapon" noun the same way ("Well-Made Weapon of the Seer").
    "libram": ["Libram", "Tract", "Psalter"],
    "idol": ["Idol", "Talisman", "Carving"],
    "shield": ["Shield", "Bulwark", "Aegis"],
    # The five ranged/polearm types were defined in data/items/weapon_types.json
    # but never given nouns here, so every one of them fell through to the
    # generic "Weapon" fallback - a crafted bow came out as "Reinforced Weapon
    # of the Wolf". That hit 27 crafted recipes (15 bows, 4 crossbows, 8
    # polearms) AND all procedural ranged loot. Guns are included because
    # Engineering makes them.
    "bow": ["Bow", "Shortbow", "Longbow"],
    "crossbow": ["Crossbow", "Repeater"],
    "gun": ["Rifle", "Blunderbuss", "Musket"],
    "thrown": ["Throwing Knife", "Throwing Axe"],
    "polearm": ["Polearm", "Halberd", "Spear"],
}


class LootGenerator:
    """Generates procedural Item instances from ilvl/rarity/slot inputs."""

    # Real stat-budget rescale (Kyle's Gear.docx, this session): the old
    # 2.2 base multiplier was producing gear at roughly 5-8x the doc's
    # actual target ranges at every level bracket checked (e.g. a level
    # 25 Rare chest rolled ~93 total stat points against a documented
    # target of 13-20). 0.36 is fit directly against the doc's real
    # bracket table (green/uncommon midpoints across L1-60), landing
    # within the documented range at every bracket tested rather than
    # picked arbitrarily. Rarity-tier RATIOS (uncommon/rare/epic spread,
    # see data/items/rarity.json) were already close to the doc's own
    # blue/green (~1.4x) and purple/green (~1.8x) targets and did not
    # need changing - only this one base constant was wrong. Shared by
    # both generate_armor_piece and generate_weapon so armor and weapons
    # stay on one consistent scale rather than two independently-tuned
    # numbers drifting apart later.
    STAT_BUDGET_BASE_MULT = 0.36

    def __init__(self):
        self._load_data()

    def _load_data(self):
        data_dir = Path(__file__).parent.parent / "data" / "items"

        with open(data_dir / "armor_types.json", 'r') as f:
            self.armor_types = json.load(f)
        with open(data_dir / "weapon_types.json", 'r') as f:
            self.weapon_types = json.load(f)
        with open(data_dir / "stat_templates.json", 'r') as f:
            self.stat_templates = json.load(f)
        with open(data_dir / "rarity.json", 'r') as f:
            self.rarity_tiers = json.load(f)["rarity_tiers"]
        with open(data_dir / "slots.json", 'r') as f:
            self.slots = json.load(f)
        with open(data_dir / "bags.json", 'r') as f:
            self.bags_catalog = json.load(f)["bags"]
        with open(data_dir / "gear_suffixes.json", 'r') as f:
            _suffix_data = json.load(f)
            self.gear_suffixes = _suffix_data["suffixes"]
            self.stat_budget_costs = _suffix_data["stat_budget_costs"]

        # THE LINE THAT WAS MISSING. The class-attribute comment block above
        # _roll_target_class says "Populated in _load_data from the armour
        # map, never written here" - and nothing ever populated it, so
        # LOOT_CLASS_POOL did not exist at all. random.choice() on it raised
        # AttributeError inside _resolve_victory, which means EVERY creature
        # kill in the game crashed: the stale hardcoded list was correctly
        # deleted and its replacement never written. Nothing caught it because
        # the role-balance sims pin enemy health at 10**6 so combat never
        # resolves to a victory, and the class sim dies on the first kill -
        # which is how this surfaced.
        #
        # sorted() so a seeded rng gives the same drops run to run; dict order
        # would make the sim irreproducible for no reason.
        self.LOOT_CLASS_POOL = sorted(self.armor_types["class_armor_map"])

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    #: Ordering used to compare rarity tiers when a minimum floor is
    #: requested (e.g. a boss guaranteeing at least Rare/"blue" gear).
    RARITY_ORDER = ["poor", "common", "uncommon", "rare", "epic", "legendary"]

    def roll_rarity(self, player_level=1, min_rarity=None):
        """
        Weighted random rarity roll, skipping disabled tiers (poor/legendary)
        AND tiers whose min_level exceeds the player's current level (e.g.
        Epic won't drop before level 30, Rare won't drop before level 10).

        min_rarity: if given, only tiers at or above this rarity are
        eligible - used to guarantee boss kills roll at least Rare ("blue")
        gear, per the rule that a dungeon boss should always be worth
        fighting rather than rolling the same table as a trash mob. If no
        tier at or above the floor is unlocked yet for this player_level
        (e.g. a level 8 party downing a boss before Rare's level-10 gate),
        falls back to the highest eligible tier below the floor rather than
        returning nothing.
        """
        eligible = {
            k: v for k, v in self.rarity_tiers.items()
            if v.get("enabled", False) and player_level >= v.get("min_level", 1)
        }
        if not eligible:
            eligible = {"common": self.rarity_tiers["common"]}

        if min_rarity:
            floor_index = self.RARITY_ORDER.index(min_rarity)
            floored = {k: v for k, v in eligible.items()
                       if self.RARITY_ORDER.index(k) >= floor_index}
            if floored:
                eligible = floored
            else:
                # Floor tier isn't unlocked yet at this player_level (e.g. a
                # level 8 boss kill before Rare's level-10 gate) - guarantee
                # the single BEST tier available instead, not a weighted
                # roll across everything under the floor (which could still
                # hand back Poor/grey loot from a boss).
                best = max(eligible, key=lambda k: self.RARITY_ORDER.index(k))
                eligible = {best: eligible[best]}

        names = list(eligible.keys())
        weights = [eligible[n]["drop_weight"] for n in names]
        return random.choices(names, weights=weights, k=1)[0]

    def generate_bag(self, bag_id=None, player_level=None, min_level=None, max_rarity=None):
        """
        Generate a bag Item from the hand-authored catalog (data/items/
        bags.json) - see that file's _notes for why bags are the one
        exception to this class's usual procedural generation.

        bag_id=None picks a random bag from the catalog, level-gated by
        player_level (defaults to no gate, i.e. any bag can come up) the
        same way roll_rarity gates armor/weapon rarity - a level 3
        character shouldn't be handed a required_level 30 bag by a random
        vendor roll.

        min_level narrows from the BOTTOM as well, for callers that are a
        shop rather than a drop - see the floor note below.
        """
        catalog = self.bags_catalog
        if bag_id is not None:
            entries = [b for b in catalog if b["item_id"] == bag_id]
            if not entries:
                return None
        elif player_level is not None:
            entries = [b for b in catalog if b["required_level"] <= player_level]
            # A FLOOR AS WELL AS A CEILING. The ceiling alone is what a DROP wants - a level 3 character
            # should not be handed a required_level 30 bag. A VENDOR is the other problem: filtering only
            # upward left a tier-38 Underdark quartermaster offering a required_level 1 Worn Leather
            # Satchel, which is exactly the "generic trash" Kyle reported. Narrow from below too, and
            # fall back rather than return nothing if the floor empties the catalog.
            if min_level is not None:
                floored = [b for b in entries if b["required_level"] >= min_level]
                if floored:
                    entries = floored
            # A RARITY CEILING, because the floor alone is not enough. The catalog tops out at a
            # required_level 30 EPIC, so a tier-38 vendor with a floor of 28 filtered down to exactly
            # that one bag and sold a guaranteed epic on every single shelf - a worse bug than the
            # starter satchel it replaced, and one that cuts straight across epics being the max-rep
            # reward. Shops stop at rare; epics are earned.
            if max_rarity is not None:
                order = ["poor", "common", "uncommon", "rare", "epic", "legendary"]
                cap = order.index(max_rarity) if max_rarity in order else len(order)
                capped = [b for b in entries
                          if order.index(b.get("rarity", "common")) <= cap
                          if b.get("rarity", "common") in order]
                if capped:
                    entries = capped
            if not entries:
                # Nobody below the lowest bag's level requirement should
                # ever hit this in practice (burlap_sack is required_level
                # 1), but fail safe to the full catalog rather than return
                # None if the data ever changes.
                entries = catalog
        else:
            entries = catalog

        data = random.choice(entries)
        return Item(
            item_id=f"{data['item_id']}_{uuid.uuid4().hex[:6]}",
            name=data["name"],
            slot="bag",
            item_level=data["required_level"],
            rarity=data["rarity"],
            armor_type="bag",
            bag_capacity=data["bag_capacity"],
            required_level=data["required_level"],
            sell_price=data["sell_price"],
            vendor_price=data.get("vendor_price"),
            flavor_text=data.get("flavor_text", ""),
            icon_id=data.get("icon_id"),
        )

    def generate_item_for_class(self, char_class, item_level, slot=None, rarity=None,
                                player_level=None, weapon_type=None,
                                stat_template=None, school=None):
        """
        Convenience entry point: generate an item appropriate for a given
        launch class (Warrior/Shaman/Rogue/Priest), using that class's
        armor_type and stat_template mapping.

        If slot is None, picks a random valid slot for that class.
        If rarity is None, rolls one using drop weights, gated by
        player_level (defaults to item_level if not given separately).

        THE THREE OVERRIDES ARE FOR A CALLER HOLDING A REAL CHARACTER.
        A world drop is itemized for a class nobody is playing, so the class
        maps are all it has to go on - but a companion's starter kit, a spec
        quest reward or anything else generated FOR somebody knows more than
        the class does, and the class-only version was measurably wrong for
        it (see data/items/spec_gear.json and tools/build_spec_gear.py):

          weapon_type     the exact type to make. world/recruit_manager.py
                          computed the right one and then threw it away -
                          `weapon_type = theme.get(slot_key)` was read as a
                          truthiness guard and never passed - so every
                          companion's weapon was a random legal pick. A Fury
                          Warrior turned up with a staff.
          stat_template   overrides the class map, which has one entry per
                          class and so itemized an Enhancement Shaman as a
                          caster and a Holy Paladin as a Strength hybrid.
          school          which school's spell power may roll. See
                          _off_school.

        armor_type stays class-derived with no override, because it really
        is a class fact: a Shaman wears mail in every spec.
        """
        armor_type = self.armor_types["class_armor_map"].get(char_class, "cloth")
        stat_template = stat_template or self.stat_templates[
            "class_stat_template_map"].get(char_class, "int_caster")
        rarity = rarity or self.roll_rarity(player_level if player_level is not None else item_level)

        if slot is None:
            slot = self._pick_random_slot(char_class)

        if slot in WEAPON_SLOTS:
            weapon_type = weapon_type or self._pick_weapon_type_for_class(
                char_class, slot, player_level)
            if weapon_type is None:
                # The class has no legal item for this slot (an off-hand for a
                # class with no shield, no tome and no dual wield). Roll the
                # main hand instead of returning nothing, so the drop still
                # happens and is still something the class can hold.
                slot = "main_hand"
                weapon_type = self._pick_weapon_type_for_class(
                    char_class, slot, player_level)
            return self.generate_weapon(slot, weapon_type, stat_template,
                                        item_level, rarity, school=school)
        else:
            return self.generate_armor_piece(slot, armor_type, stat_template,
                                             item_level, rarity, school=school)

    def generate_armor_piece(self, slot, armor_type, stat_template, item_level,
                             rarity, school=None):
        """Generate a single armor/accessory item for a specific slot."""
        rarity_data = self.rarity_tiers[rarity]
        slot_data = self.slots["slots"][slot]
        slot_weight = self.slots["weight_tiers"][slot_data["weight_tier"]]

        # Accessory slots have no armor value and use the "accessory" armor_type
        effective_armor_type = slot_data.get("armor_type_override")
        if slot_data["armor_slot"] and not effective_armor_type:
            effective_armor_type = armor_type
        elif not slot_data["armor_slot"]:
            effective_armor_type = "accessory"

        total_budget = item_level * self.STAT_BUDGET_BASE_MULT * rarity_data["stat_budget_multiplier"] * slot_weight

        primary_stats, secondary_stats, suffix_name = self._roll_stats(
            stat_template, total_budget, rarity_data["bonus_stat_rolls"], rarity,
            item_level, school=school
        )

        armor_value = 0
        if slot_data["armor_slot"] and effective_armor_type in self.armor_types["armor_types"]:
            armor_mult = self.armor_types["armor_types"][effective_armor_type]["armor_multiplier"]
            armor_value = int(item_level * 1.5 * armor_mult * slot_weight * rarity_data["stat_budget_multiplier"])

        name = self._generate_armor_name(rarity, slot, stat_template, suffix_name)
        item_id = f"{slot}_{effective_armor_type}_{stat_template}_{item_level}_{rarity}_{uuid.uuid4().hex[:6]}"

        return Item(
            item_id=item_id,
            name=name,
            slot=slot,
            item_level=item_level,
            rarity=rarity,
            armor_type=effective_armor_type,
            weapon_type=None,
            stat_template=stat_template,
            primary_stats=primary_stats,
            secondary_stats=secondary_stats,
            armor_value=armor_value,
            required_level=max(1, item_level - 2),
            sell_price=max(1, int(item_level * rarity_data["stat_budget_multiplier"])),
            flavor_text="",
            # Real WoW icon art (Kyle's icon pack, see gear_icons.py) -
            # every procedural piece now gets a visually-matching icon
            # instead of rendering as a bare rarity-colored box. None if
            # this slot/armor_type has no matching art (shouldn't happen
            # for any real slot - gear_icons.py has full coverage - but
            # never crash generation over missing icon art either way).
            icon_id=pick_armor_icon(slot, effective_armor_type),
        )

    def generate_weapon(self, slot, weapon_type, stat_template, item_level, rarity,
                        strict=False, school=None):
        """Generate a weapon or off-hand item (shield/totem/wand).

        strict=True refuses an invalid stat_template instead of quietly
        swapping it. TWO HAND-AUTHORED EPICS SILENTLY BECAME OTHER ITEMS:
        "The Quiet Argument" was specified as a spi_healer one-handed mace
        and "The Deep Bloom's Root" as a spi_healer staff, spi_healer was
        valid on no weapon type at all, and the substitution below turned
        both into int_caster items. Nothing failed, nothing logged, and the
        table still said they were healer weapons. For a procedural roll the
        substitution is right - better a slightly-off item than no drop -
        but for a named item somebody wrote on purpose it is a lie, so
        every hand-authoring caller passes strict=True.
        """
        rarity_data = self.rarity_tiers[rarity]
        weapon_data = self.weapon_types["weapon_types"][weapon_type]

        # Validate stat_template against this weapon type's allowed list (shields have none)
        valid_templates = weapon_data["valid_stat_templates"]
        if valid_templates and stat_template not in valid_templates:
            if strict:
                raise ValueError(
                    f"{weapon_type} does not accept stat_template "
                    f"'{stat_template}' (valid: {', '.join(valid_templates)}) - "
                    f"the item would have been generated as "
                    f"'{valid_templates[0]}' instead of what was asked for")
            stat_template = valid_templates[0]

        hand = weapon_data["hand"]
        weight_tier = "weapon_two_hand" if hand == "two_hand" else "weapon_medium"
        slot_weight = self.slots["weight_tiers"][weight_tier]
        budget_mult = weapon_data["budget_multiplier"]

        total_budget = item_level * self.STAT_BUDGET_BASE_MULT * rarity_data["stat_budget_multiplier"] * slot_weight * budget_mult

        if valid_templates:
            primary_stats, secondary_stats, suffix_name = self._roll_stats(
                stat_template, total_budget, rarity_data["bonus_stat_rolls"], rarity,
                item_level, school=school
            )
        elif rarity in self.STATLESS_RARITIES:
            # Shields at Poor/Common: armor+block only, no stamina stat -
            # same "just the base item, no bonus stats" rule as armor pieces.
            primary_stats = {}
            secondary_stats = {}
            suffix_name = None
        else:
            # Shields: no stat_template, budget goes entirely to stamina + armor
            primary_stats = {"stamina": int(total_budget * 0.6)}
            secondary_stats = {}
            suffix_name = "of Stamina"  # closest real suffix match for a pure-stamina shield roll

        armor_value = 0
        block_value = 0
        weapon_damage_min = 0
        weapon_damage_max = 0
        attack_speed = weapon_data.get("base_attack_speed", 0.0)

        if weapon_type == "shield":
            armor_value = int(item_level * 1.2 * rarity_data["stat_budget_multiplier"])
            # Block value scales similarly to armor - higher ilvl/rarity = better block
            block_value = int(item_level * 1.5 * rarity_data["stat_budget_multiplier"])
        elif weapon_data.get("relic") or weapon_data.get("non_weapon"):
            # Relics (Totem/Libram/Idol) and held-in-off-hand items (Tome) are
            # passive stat sticks - no auto-attack damage.
            #
            # This was a hardcoded `weapon_type in ("totem", "tome")`, which
            # is a trap rather than a rule: adding libram and idol as relics
            # on 29 Oct 2026 silently gave them 67-91 weapon damage at ilvl
            # 50, because they were not in the tuple. Keyed on the type's own
            # relic/non_weapon flags now, so any relic added later is a stat
            # stick without anyone having to remember this line exists.
            pass
        else:
            # Melee weapons and wands: roll a damage range around a DPS
            # target, driven by damage_tier (data/items/weapon_types.json's
            # damage_tiers table) rather than base_attack_speed *
            # budget_multiplier.
            #
            # Kyle (2026-09-06): "Speed we won't ever use" - combat is
            # turn-based, so attack_speed never actually gates swing
            # frequency (see combat/combat_engine.py - nothing reads it),
            # it was ONLY ever a multiplier baked into this damage
            # formula. That produced real, player-visible bugs: staff
            # (base_attack_speed 3.2, same budget_multiplier tier as
            # sword_2h/polearm) rolled damage on par with genuine
            # two-handers - a level-6 quest reward staff hit for 58-78
            # (22.7 DPS-equivalent) next to a same-level dagger at 15-20
            # (10.3) and sword_1h at 24-33 (11.9), roughly DOUBLE. Kyle's
            # ask: "1H to be similar, 2H to be similar, staves will be
            # lower" - i.e. real, clean TIERS, not a continuous
            # per-weapon-type formula that happens to correlate with a
            # stat now fully decoupled from actual combat behavior.
            #
            # damage_tier multipliers (see weapon_types.json):
            #   two_hand 1.8 > one_hand 1.0 > ranged 0.85 > staff 0.55
            # one_hand and ranged deliberately sit close together (Kyle:
            # "1H should be somewhat similar to ranged, just slightly
            # stronger") - staff is the softest auto-attack weapon in the
            # game by design, since casters lean on spells, not their
            # white-damage staff swing.
            tier_key = weapon_data.get("damage_tier", "one_hand")
            tier_mult = self.weapon_types["damage_tiers"].get(
                tier_key, {"dps_multiplier": 1.0})["dps_multiplier"]

            # +6.4 flat DPS offset (Kyle's balance pass, 2026-09-05): the old
            # pure item_level*1.1 curve made ilvl-1 gear nearly worthless
            # (a common sword_1h averaged ~2.5 dmg/swing) while still letting
            # ilvl-10 already overshoot the "~30 max auto-attack at start"
            # target once AP was added. The flat offset is a fixed absolute
            # bump that matters hugely at ilvl 1 (roughly triples early
            # weapon damage) but fades to a small % of the total by ilvl 15+,
            # so it fixes the starting-gear floor without meaningfully
            # reshaping the mid/late curve.
            #
            # NOTE: this target_dps is now a flat per-hit damage value, not
            # a literal "damage per second" - attack_speed no longer
            # multiplies it (see above). The name/variable is kept as
            # target_dps to avoid touching every downstream reference, but
            # it's really "target average hit" now.
            target_dps = (item_level * 1.1 + 6.4) * rarity_data["stat_budget_multiplier"] * tier_mult
            avg_damage = target_dps
            # Spread +/-15% around the average for a min/max roll range (WoW-style weapon damage range)
            weapon_damage_min = max(1, int(avg_damage * 0.85))
            weapon_damage_max = max(weapon_damage_min + 1, int(avg_damage * 1.15))

        name = self._generate_weapon_name(rarity, weapon_type, stat_template, suffix_name)
        item_id = f"{slot}_{weapon_type}_{stat_template}_{item_level}_{rarity}_{uuid.uuid4().hex[:6]}"

        return Item(
            item_id=item_id,
            name=name,
            slot=slot,
            item_level=item_level,
            rarity=rarity,
            armor_type=None,
            weapon_type=weapon_type,
            stat_template=stat_template if valid_templates else None,
            primary_stats=primary_stats,
            secondary_stats=secondary_stats,
            armor_value=armor_value,
            weapon_damage_min=weapon_damage_min,
            weapon_damage_max=weapon_damage_max,
            attack_speed=attack_speed,
            block_value=block_value,
            required_level=max(1, item_level - 2),
            sell_price=max(1, int(item_level * rarity_data["stat_budget_multiplier"] * 1.5)),
            flavor_text="",
            icon_id=pick_weapon_icon(weapon_type),
        )

    def generate_loot_for_creature(self, creature_level, char_class=None, drop_chance=0.35, player_level=None):
        """
        Roll for loot drop from a defeated creature. Returns an Item or None.

        item_level is capped at (player_level + ITEM_LEVEL_LEAD_CAP) even when
        the creature is higher level than the player. Without this cap, a
        low-level player fighting an out-leveled subzone/cave creature (which
        the bestiary deliberately sets several levels above the open-zone
        baseline) could loot gear far ahead of their actual character level -
        e.g. a level 6 player killing a level 11 cave mob would otherwise get
        ilvl 11 gear, a huge relative power spike. Rarity is gated by
        player_level (not creature_level) for the same reason - Epic/Rare
        shouldn't drop just because the creature you're fighting is tough.
        """
        if random.random() > drop_chance:
            return None

        effective_player_level = player_level if player_level is not None else creature_level
        ITEM_LEVEL_LEAD_CAP = 2  # how far above player level a drop's ilvl can go
        item_level = max(1, min(creature_level, effective_player_level + ITEM_LEVEL_LEAD_CAP))

        rarity = self.roll_rarity(effective_player_level)

        # Loot is NOT tailored to the player's class. Drops roll against the
        # whole class pool, so a Paladin sees cloth and leather too - matching
        # WoW, and essential groundwork for parties (Phase 9), where gear for
        # classes you aren't playing needs to actually exist in the world.
        #
        # char_class, when given, is a soft BIAS not a guarantee: it wins the
        # roll CLASS_BIAS_CHANCE of the time so progression doesn't stall on
        # pure randomness, and the rest of the time any class can roll.
        target_class = self._roll_target_class(char_class)

        return self.generate_item_for_class(target_class, item_level, rarity=rarity)

    def generate_boss_loot(self, creature_level, char_class=None, player_level=None):
        """
        Guaranteed loot drop for a boss/elite kill. Unlike trash loot, this
        ALWAYS drops (no drop_chance roll) and is floored at Rare ("blue")
        rarity, so a dungeon boss is reliably worth fighting rather than
        rolling the exact same table as a wolf. Epic ("purple") can still
        roll instead of Rare when the player is high enough level, per the
        normal rarity weights - this only raises the FLOOR, not the ceiling.
        """
        effective_player_level = player_level if player_level is not None else creature_level
        ITEM_LEVEL_LEAD_CAP = 2
        item_level = max(1, min(creature_level, effective_player_level + ITEM_LEVEL_LEAD_CAP))

        rarity = self.roll_rarity(effective_player_level, min_rarity="rare")
        target_class = self._roll_target_class(char_class)

        return self.generate_item_for_class(target_class, item_level, rarity=rarity)

    #: Fraction of drops that favour the player's own class. The remainder
    #: roll freely across the full class pool.
    CLASS_BIAS_CHANCE = 0.35

    #: Every class loot can roll for - READ FROM data/items/armor_types.json
    #: rather than listed here, so it cannot go stale again. See
    #: _roll_target_class.
    #:
    #: THIS WAS A HARDCODED LIST OF THE 9 VANILLA CLASSES, with a comment
    #: saying "the 21 CoA classes join this list when they become
    #: selectable". They became selectable: all 30 are offered by
    #: CharacterCreationScreen, all 30 have an entry in class_armor_map,
    #: class_weapon_map and class_stat_template_map, and
    #: tools/smoke_play_all_classes.py plays all 30 from level 1 to 60. The
    #: list simply never got updated, and because a drop still *looked*
    #: perfectly normal, nothing noticed. Rolling 120,000 real drops through
    #: generate_loot_for_creature measured what it cost:
    #:
    #:   * CLOTH WAS 1.46x MAIL. Three of the nine pooled classes wear cloth
    #:     and only two wear mail, so the free roll - the 65% of drops the
    #:     class bias does not claim - was skewed by the shape of the stale
    #:     list. Across all 30 the split is 8 cloth / 8 leather / 7 mail /
    #:     7 plate, which is 1.14x at worst.
    #:   * POLEAREMS CAME OUT 25 TIMES IN 120,000 ROLLS. polearm is in
    #:     exactly one class's weapon list (Tinker), so it could only ever
    #:     arrive through the class-bias path, for a Tinker player, and never
    #:     once for the other 29 classes - while data/loot and data/quests
    #:     between them hand-author 78 polearm items.
    #:   * agi_int_hybrid NEVER ROLLED AT ALL with no player class given, and
    #:     only for its own four classes otherwise.
    #:
    #: Deliberately NOT filtered to the classes character creation offers.
    #: Loot rolls across the whole class pool on purpose (see
    #: generate_loot_for_creature) precisely so gear for classes you are not
    #: playing exists in the world for party members, and a class with gear
    #: data is a class whose gear should exist whether or not the creation
    #: screen lists it yet.
    #: Populated in _load_data from the armour map, never written here.

    def _roll_target_class(self, char_class=None):
        """Pick which class a drop is itemized for (see generate_loot_for_creature)."""
        if char_class and random.random() < self.CLASS_BIAS_CHANCE:
            return char_class
        return random.choice(self.LOOT_CLASS_POOL)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _pick_random_slot(self, char_class):
        all_slots = ARMOR_SLOTS + ACCESSORY_SLOTS
        # Small chance to roll a weapon slot instead
        if random.random() < 0.2:
            valid_weapons = self.weapon_types["class_weapon_map"].get(char_class, [])
            if valid_weapons:
                # Only offer the Ranged slot if this class actually has a
                # ranged-hand-compatible weapon type (Wand, Totem, Thrown, etc).
                # Otherwise a class with e.g. only melee weapons could roll
                # "ranged" and end up with a Main Hand weapon mislabeled into
                # that slot.
                candidate_slots = list(WEAPON_SLOTS)
                has_ranged_option = any(
                    self.weapon_types["weapon_types"][wt]["hand"] == "ranged"
                    for wt in valid_weapons
                )
                if not has_ranged_option:
                    candidate_slots.remove("ranged")
                return random.choice(candidate_slots)
        return random.choice(all_slots)

    def _class_may_dual_wield(self, char_class, player_level=None):
        """Can ANY spec of this class dual-wield, at this level? See the data's
        dual_wield key.

        Class-level, not spec-level, on purpose: loot is generated with no
        character in hand (see _roll_target_class - most drops are itemized
        for a class nobody is playing), so the spec gate cannot be applied
        here. proficiency.can_dual_wield does the spec check at equip time.
        A Fury-only weapon can therefore drop for a Warrior and an Arms
        Warrior cannot equip it, exactly as WoW behaves.

        The LEVEL gate is applied when the level is known, because that one
        can be: dual wield is trained at 20, so an off-hand one-hander
        dropping for a level-8 Hunter is dead in the bag for twelve levels.
        Unknown level means no level filter rather than a guess.

        Fails CLOSED on a missing key, matching proficiency.can_dual_wield:
        an unauthored entry would quietly restore the free-for-all the
        restriction exists to stop.
        """
        entry = self.weapon_types.get("dual_wield", {}).get(char_class)
        if entry is None:
            return False
        # Tolerates the older shape ("all" / bare spec list) as well as the
        # current {"specs": ..., "min_level": N}.
        if isinstance(entry, dict):
            specs, min_level = entry.get("specs", "all"), entry.get("min_level", 0)
        else:
            specs, min_level = entry, 0
        if not (specs == "all" or specs):
            return False
        if player_level is not None and player_level < min_level:
            return False
        return True

    def _pick_weapon_type_for_class(self, char_class, slot, player_level=None):
        valid_weapons = self.weapon_types["class_weapon_map"].get(char_class, ["mace_1h"])
        # Filter by hand compatibility for the given slot
        compatible = []
        for wt in valid_weapons:
            hand = self.weapon_types["weapon_types"][wt]["hand"]
            if slot == "main_hand" and hand in ("main_or_off", "two_hand"):
                compatible.append(wt)
            elif slot == "off_hand" and hand in ("main_or_off", "off_hand"):
                # A one-handed WEAPON in the off-hand is dual-wielding, so only
                # offer it to a class that may dual-wield at all. Before this,
                # off_hand accepted every main_or_off type for every class, so
                # a normal drop could hand a Priest an off-hand sword - a slot
                # it can fill but should never be able to. Shields and tomes
                # are hand == "off_hand" and are unaffected.
                #
                # Class-level, not spec-level, deliberately: loot is generated
                # without a character in hand (see _roll_target_class - most
                # drops are itemized for a class nobody is playing), so the
                # spec gate cannot be applied here. entities/proficiency.py's
                # can_dual_wield does the spec check at equip time. The result
                # is that a Fury-only weapon can drop for a Warrior and an Arms
                # Warrior cannot equip it, which is exactly how WoW behaves.
                if hand == "main_or_off" and not self._class_may_dual_wield(
                        char_class, player_level):
                    continue
                compatible.append(wt)
            elif slot == "ranged" and hand == "ranged":
                compatible.append(wt)

        if not compatible and slot == "off_hand":
            # NOTHING, rather than a main-hand weapon shoved into the off-hand.
            # The main-hand fallback below is right for the ranged slot it was
            # written for and wrong here: once dual-wield was restricted,
            # Hunter had no legal off-hand item at all - no shield, no tome,
            # and no dual wield - so the fallback handed it off-hand polearms
            # and staves, which is worse than the hole it was patching.
            # Returning None lets the caller roll a different slot.
            return None

        if not compatible:
            # No hand-compatible weapon exists for this class+slot combo (e.g. a
            # class with no Ranged weapon type defined). Previously this fell
            # back to `valid_weapons` unfiltered, which could hand a Main Hand
            # weapon like a Dagger into the Ranged slot - fixed by falling back
            # to Main Hand-compatible weapons instead, which always exist for
            # every class, rather than ignoring hand compatibility entirely.
            compatible = [
                wt for wt in valid_weapons
                if self.weapon_types["weapon_types"][wt]["hand"] in ("main_or_off", "two_hand")
            ] or valid_weapons

        return random.choice(compatible)

    #: Rarities that carry NO bonus stats at all - only armor value (and, for
    #: weapons, base weapon damage). This matches WoW: a white/grey item is
    #: "just armor" - a plain breastplate that stops hits, not a stat stick.
    #: Stats become part of the game starting at Uncommon (green).
    STATLESS_RARITIES = ("poor", "common")

    #: Sub-level-10 gear is restricted to pure primary-stat suffixes only
    #: (the 5 single-stat suffixes + the 7 "of the [Animal]" dual-stat
    #: combos) - no spell power, ratings, mp5, resistances, or armor
    #: suffixes below level 10, matching real WoW Classic's early-leveling
    #: gear curve where those stats simply don't appear yet. Built by
    #: filtering gear_suffixes.json to suffixes whose stats are a subset
    #: of the 5 primary stats, so it stays in sync automatically if the
    #: suffix data changes.
    LOW_LEVEL_STAT_CAP = 10
    _PRIMARY_STAT_NAMES = {"strength", "agility", "intellect", "stamina", "spirit"}

    #: Groups suffixes by which stat_template they're thematically
    #: appropriate for, so class-based generation (generate_item_for_class)
    #: picks a suffix that actually fits the caller's intent instead of a
    #: purely random one (e.g. a Warrior's Strength-plate roll shouldn't
    #: come back "of the Prophet"). Built once from gear_suffixes.json's
    #: real stat keys - a suffix is filed under EVERY stat_template whose
    #: primary stats overlap with at least one of that suffix's stats,
    #: rather than a hand-maintained parallel list that could drift out of
    #: sync with the real suffix data.
    #: 43 OF 77 SUFFIXES COULD NEVER BE ROLLED. This mapped each template to
    #: its PRIMARY stat alone, and a suffix was filed only if it overlapped,
    #: so any suffix made purely of secondary stats was filed under nothing
    #: and class-based generation could never pick it. That was 56% of the
    #: authored suffix table, dead:
    #:   - all 10 resistance suffixes, which is why Kyle's "magic resistance
    #:     gear starts only after level 45, phased in gradually" could not
    #:     happen - a sweep of 60 geared characters from level 20 to 60 found
    #:     exactly zero resistance rolls
    #:   - all 19 school-specific spell power suffixes (of Fiery Wrath, of
    #:     Frostfire, of the Void, ...), i.e. every caster's flavour slot
    #:   - all 7 tank suffixes (of the Bulwark, Defender, Juggernaut,
    #:     Bastion, Warder, Duelist, of Eluding)
    #:   - "of Stamina", "of Spirit" and "of the Whale", because stamina and
    #:     spirit were in no template's set either
    #:
    #: Each template now carries the secondaries that actually belong to it:
    #: physical templates get the melee ratings and the tank defences, caster
    #: templates get spell power in every school plus healing/mp5/spell crit,
    #: and the hybrids get the union. A Warrior still cannot roll "of the
    #: Prophet" - the point of this map - because intellect-side stats stay
    #: out of the physical templates.
    _PHYSICAL_SECONDARY = {
        "attack_power", "crit_chance_physical", "hit_rating",
        "defense_rating", "dodge_rating", "parry_rating",
        "block_rating", "block_value",
        # ARMOUR PENETRATION, the physical counterpart to spell_penetration
        # below. It was in no template's wanted set and on no suffix, so a
        # physical DPS had exactly one stat to chase (hit rating) while a
        # caster now has two - the inverse of the unfairness Kyle raised.
        "armor_penetration_pct",
    }
    _CASTER_SECONDARY = {
        "spell_power", "healing_power", "mp5", "crit_chance_spell",
        "spell_penetration", "hit_rating",
        "fire_spell_power", "frost_spell_power", "arcane_spell_power",
        "shadow_spell_power", "nature_spell_power", "holy_spell_power",
    }
    #: Stamina, Spirit and Armour belong to everyone - every class wants
    #: health, Spirit is the universal regen stat, and armour is on every
    #: piece of gear in the game regardless of who wears it. Kyle, 30 Oct:
    #: "we DO need things like armor on weapons and bonus armor able to roll
    #: on gear" - BFD's Tortoise Armor and the Wildfury Greatstaff are the
    #: references, and the classes that need it most are the tanks with no
    #: shield slot to put block value in (druid, venomancer). Armour lived in
    #: _PHYSICAL_SECONDARY before, which kept "of the Tortoise" off every
    #: cloth and caster piece for no reason anyone could defend.
    #: Haste is here because two hand-authored quest items carry it
    #: (Grokka's Appraised Tusk Pendant, Bloodfeather's Talon Staff) and
    #: tools/audit_stat_coherence flagged both: it was priced in
    #: stat_budget_costs at 12.0 and claimed by no template, so it was a stat
    #: that existed only on items somebody typed by hand. Shared is the
    #: honest home for it - every class wants haste. Note there is still no
    #: haste SUFFIX in Kyle's list, so haste reaches gear only by bonus roll
    #: or by hand; that is his table to extend, not mine to invent.
    _SHARED_SECONDARY = {"stamina", "spirit", "armor", "haste"}

    #: The two physical templates each admit the OTHER's primary stat, which
    #: the exclude-set comment below has always said they should ("Strength
    #: and Agility may cross between the two physical templates, which real
    #: Classic gear does freely") - the wanted sets just never said it, and
    #: under the old overlap test nobody noticed, because a str+agi suffix got
    #: in on the Stamina it happened to carry. Under the subset test the
    #: contradiction became three dead suffixes: "of the Tiger", "of Striking"
    #: and "of the Beast" were reachable by no template at all.
    #:
    #: The cross is NOT a free pass, or a Strength plate piece could roll pure
    #: "of Agility" - see _lead_stat_ok below, which lets a suffix carry the
    #: opposite primary only when it also carries the template's own.
    _SUFFIX_TEMPLATE_STATS = {
        "str_physical": ({"strength", "agility"} | _PHYSICAL_SECONDARY
                         | _SHARED_SECONDARY),
        "agi_physical": ({"agility", "strength"} | _PHYSICAL_SECONDARY
                         | _SHARED_SECONDARY),
        "int_caster": {"intellect"} | _CASTER_SECONDARY | _SHARED_SECONDARY,
        # spi_healer WAS MISSING, and the failure mode was invisible rather
        # than loud. It is a real template in data/items/stat_templates.json,
        # but no entry here meant wanted_stats came back empty - so BELOW
        # RESISTANCE_LEVEL it fell through to the "fails soft to the full
        # suffix list" branch and rolled anything at all, and AT 46+ the only
        # stats it wanted were the resistances unioned in just above, so its
        # whole suffix pool was resistance suffixes and gear in that band
        # rolled NO PRIMARY STATS. tools/audit_loot.py reported it as
        # "templates whose whole suffix pool is resistance suffixes, so gear
        # there rolls no primary stats at all: spi_healer at ilvl 51-60".
        # Nothing maps to it today (class_stat_template_map uses the other
        # five), so it is reachable only by an explicit caller - which is
        # exactly the kind of latent trap worth closing before someone points
        # a healer at it.
        "spi_healer": ({"intellect", "spirit"} | _CASTER_SECONDARY
                       | _SHARED_SECONDARY),
        "str_int_hybrid": ({"strength", "intellect"} | _PHYSICAL_SECONDARY
                           | _CASTER_SECONDARY | _SHARED_SECONDARY),
        "agi_int_hybrid": ({"agility", "intellect"} | _PHYSICAL_SECONDARY
                           | _CASTER_SECONDARY | _SHARED_SECONDARY),
    }

    #: Resistance stats, which every template can roll but ONLY from
    #: RESISTANCE_LEVEL up. Kyle: "Magic resistance gear starts only after
    #: level 45, phased in gradually." They are deliberately NOT in the
    #: template sets above, because the gate is by level rather than by
    #: class - a plate tank and a cloth caster both want Fire Resistance,
    #: and neither should see it at level 20.
    _RESISTANCE_STATS = {
        "fire_resistance", "frost_resistance", "nature_resistance",
        "shadow_resistance", "arcane_resistance", "holy_resistance",
    }
    #: ITEM level, and the gate has to clear the REQUIRED level. Generated
    #: gear sets required_level = item_level - 2, so a value of 46 produced
    #: resistance items a player could equip at 44 - audit_loot caught it as
    #: "RULE VIOLATION - magic resistance before level 45: 153 rolled items".
    #: 48 puts the earliest usable resistance piece at required_level 46,
    #: which is what "starts only after level 45" means.
    RESISTANCE_LEVEL = 48

    #: OVERLAP ALONE IS NOT ENOUGH, and my first version of the widening
    #: above proved it. A suffix matches on overlap, so once Stamina and
    #: Spirit were added to every template, 22 suffixes carrying Intellect,
    #: spell power or healing power reached str_physical through the Stamina
    #: in them - including "of the Prophet", which the original comment here
    #: named as the exact thing to prevent ("a Warrior's Strength-plate roll
    #: shouldn't come back 'of the Prophet'"). A Warrior picked up spell
    #: power in 1 of 40 geared sets.
    #:
    #: So a suffix must ALSO carry nothing from its template's excluded set.
    #: Physical templates refuse caster stats and caster templates refuse the
    #: melee/tank ones; Strength and Agility may cross between the two
    #: physical templates, which real Classic gear does freely, and Stamina,
    #: Spirit, hit rating and armour belong to everyone so they are excluded
    #: nowhere.
    _CASTER_ONLY = {
        "intellect", "spell_power", "healing_power", "mp5",
        "crit_chance_spell", "spell_penetration",
        "fire_spell_power", "frost_spell_power", "arcane_spell_power",
        "shadow_spell_power", "nature_spell_power", "holy_spell_power",
    }
    _PHYSICAL_ONLY = {
        "strength", "agility", "attack_power", "crit_chance_physical",
        "defense_rating", "dodge_rating", "parry_rating",
        "block_rating", "block_value", "armor_penetration_pct",
    }
    _SUFFIX_TEMPLATE_EXCLUDES = {
        "str_physical": _CASTER_ONLY,
        "agi_physical": _CASTER_ONLY,
        "int_caster": _PHYSICAL_ONLY,
        # Same exclusion as int_caster, for the same reason: a healer has no
        # use for attack power or parry rating. Without an entry here
        # spi_healer banned nothing, so physical suffixes slipped in on the
        # Stamina and Spirit overlap and its pool came out at 60 against
        # int_caster's 38 from an identical stat set - the tell that the
        # exclusion was missing rather than the stats being different.
        "spi_healer": _PHYSICAL_ONLY,
        # A hybrid wants both sides, so it excludes neither.
        "str_int_hybrid": frozenset(),
        "agi_int_hybrid": frozenset(),
    }

    #: The primary stat (or stats) a template exists to deliver. Two jobs:
    #: the cross-primary rule in _lead_stat_ok, and the roll weighting in
    #: _suffix_weight - an item named for a stat should usually carry it.
    _TEMPLATE_LEAD = {
        "str_physical": frozenset({"strength"}),
        "agi_physical": frozenset({"agility"}),
        "int_caster": frozenset({"intellect"}),
        "spi_healer": frozenset({"spirit", "intellect"}),
        "str_int_hybrid": frozenset({"strength", "intellect"}),
        "agi_int_hybrid": frozenset({"agility", "intellect"}),
    }
    #: Stamina and Spirit are nobody's foreign stat - every class wants them.
    _UNIVERSAL_PRIMARY = frozenset({"stamina", "spirit"})

    def _lead_stat_ok(self, suffix_stats, stat_template):
        """A suffix may carry a primary stat this template does not lead with
        ONLY if it also carries one the template does.

        This is what keeps the Strength/Agility cross honest. "of the Tiger"
        (Strength + Agility) belongs on a Warrior's plate and on a Rogue's
        leather, because it leads with the stat each of them came for. Pure
        "of Agility" on a Strength piece does not belong on either, and the
        wanted-set test cannot tell the two cases apart - both are subsets.
        """
        leads = self._TEMPLATE_LEAD.get(stat_template)
        if not leads:
            return True
        carried = set(suffix_stats) & self._PRIMARY_STAT_NAMES
        foreign = carried - leads - self._UNIVERSAL_PRIMARY
        return not foreign or bool(carried & leads)

    #: How often a suffix should come up, relative to its neighbours in the
    #: pool. Kyle, on an earlier version of this: "So i dont like the
    #: weighted roll. It limits the game too much." The measurement said the
    #: opposite - variety went UP, because an unweighted roll over a pool
    #: that is 3/4 flavour suffixes means the stat an item is named for shows
    #: up in a minority of rolls, and the items that do carry it all look the
    #: same. Weighting the lead stat up spends the budget on the identity and
    #: leaves the flavour slots free to differ. Kyle, after seeing it: "that
    #: looks good bro." Worth keeping the history here, because the next
    #: person to read this file will have the same first reaction he did.
    #:
    #: These are weights, not gates - a resistance suffix at 1 against a lead
    #: at 10 is uncommon, never impossible.
    SUFFIX_WEIGHT_LEAD = 10
    SUFFIX_WEIGHT_PRIMARY = 6
    SUFFIX_WEIGHT_UTILITY = 3
    SUFFIX_WEIGHT_SCHOOL = 2
    SUFFIX_WEIGHT_RESIST = 1

    _SCHOOL_SPELL_POWER = frozenset({
        "fire_spell_power", "frost_spell_power", "arcane_spell_power",
        "shadow_spell_power", "nature_spell_power", "holy_spell_power",
    })

    def _off_school(self, school):
        """The school spell power stats a `school` caster must not roll.

        All six lived in one set, so any caster template could roll any
        school. Kyle, 6 Nov: "Ive seen a fire mage come with +holy spell
        power gear." A school is only known when the caller has a real
        character or spec in hand, so school=None keeps the old behaviour
        for an ordinary world drop itemized for nobody in particular.
        """
        if not school:
            return frozenset()
        return self._SCHOOL_SPELL_POWER - {f"{school}_spell_power"}

    def _suffix_weight(self, suffix_name, stat_template):
        """Roll weight for one suffix under one template - see the
        SUFFIX_WEIGHT_* constants for why this is weighted at all."""
        stats = set(self.gear_suffixes[suffix_name]["stats"])
        if stats & self._RESISTANCE_STATS:
            return self.SUFFIX_WEIGHT_RESIST
        if stats & self._SCHOOL_SPELL_POWER:
            return self.SUFFIX_WEIGHT_SCHOOL
        if stats & self._TEMPLATE_LEAD.get(stat_template, frozenset()):
            return self.SUFFIX_WEIGHT_LEAD
        if stats & self._PRIMARY_STAT_NAMES:
            return self.SUFFIX_WEIGHT_PRIMARY
        return self.SUFFIX_WEIGHT_UTILITY

    def _suffixes_for_template(self, stat_template, low_level=False,
                               item_level=None, school=None):
        """Real suffixes whose primary stat set overlaps this
        stat_template's real stats - built lazily and cached per
        LootGenerator instance since gear_suffixes.json doesn't change
        during a session.

        low_level=True (item_level < LOW_LEVEL_STAT_CAP) further
        restricts the pool to pure-primary-stat suffixes only (see
        LOW_LEVEL_STAT_CAP docstring) - cached separately from the
        normal pool under a "{template}::low" key."""
        if not hasattr(self, "_suffix_template_cache"):
            self._suffix_template_cache = {}
        resists_ok = item_level is not None and item_level >= self.RESISTANCE_LEVEL
        cache_key = (f"{stat_template}::low" if low_level
                     else f"{stat_template}::res" if resists_ok else stat_template)
        # The school belongs IN the cache key. Without it the first caller
        # to ask for a template cached its pool and every later school got
        # that one back - a fire-only pool served to a frost caster.
        cache_key = f"{cache_key}::{school}" if school else cache_key
        if cache_key in self._suffix_template_cache:
            return self._suffix_template_cache[cache_key]

        wanted_stats = set(self._SUFFIX_TEMPLATE_STATS.get(stat_template, set()))
        if resists_ok:
            wanted_stats |= self._RESISTANCE_STATS
        banned = set(self._SUFFIX_TEMPLATE_EXCLUDES.get(stat_template, frozenset()))
        # Every school but this caster's own.
        banned |= self._off_school(school)
        # SUBSET, NOT OVERLAP. Kyle asked why an agility two-handed mace had
        # come out carrying Healing Power, and the honest answer is that a
        # suffix matched if ANY ONE of its stats was wanted. "of the Wild"
        # carries agility and healing power; the agility was enough to let it
        # through, and the healing power came along for the ride. The exclude
        # sets below were a patch over the same hole - they list the stats a
        # template must refuse, which only works for as long as somebody
        # remembers to add every new stat to the right list.
        #
        # Requiring the whole suffix to sit inside the template's wanted set
        # inverts that: a stat has to be named as appropriate before it can
        # appear, so a stat nobody has classified is excluded by default
        # rather than included by default. The exclude test stays as a second
        # gate for the hybrids, whose wanted set is the union of both sides
        # and so would otherwise accept anything.
        matches = [
            name for name, data in self.gear_suffixes.items()
            if (set(data["stats"].keys()) <= wanted_stats
                and not (banned & set(data["stats"].keys()))
                and self._lead_stat_ok(data["stats"], stat_template))
        ]
        if not resists_ok:
            # Below RESISTANCE_LEVEL a resistance suffix must not appear at
            # all, including the "of Fire Protection" shapes that pair a
            # resistance with Stamina and would otherwise slip in on the
            # Stamina overlap.
            matches = [
                name for name in matches
                if not (self._RESISTANCE_STATS
                        & set(self.gear_suffixes[name]["stats"].keys()))
            ]
        if not matches:
            # No suffix overlaps this template's stats at all (shouldn't
            # happen with the 5 real templates above, but fails soft to
            # the full suffix list rather than crashing generation if a
            # new template is ever added without a matching entry here).
            matches = list(self.gear_suffixes.keys())

        if low_level:
            base_stat_only = [
                name for name in matches
                if set(self.gear_suffixes[name]["stats"].keys()) <= self._PRIMARY_STAT_NAMES
            ]
            # Fails soft to the unrestricted match list if a template
            # somehow has zero pure-primary-stat suffixes overlapping it,
            # rather than crashing generation over a low-level drop.
            matches = base_stat_only or matches

        self._suffix_template_cache[cache_key] = matches
        return matches

    def _bonus_pool(self, stat_template):
        """The bonus-roll pool, filtered to stats this template should carry.

        FIXING THE SUFFIX WAS ONLY HALF OF IT. The suffix test above decides
        the item's core stats; bonus_stat_rolls then layer extra secondaries
        on top of Rare and Epic items, and that pool was the raw eight-stat
        list from stat_templates.json with no template filter at all. So an
        agility weapon whose suffix was now clean could still pick up Healing
        Power on the bonus roll, which is exactly the item Kyle asked about,
        arriving by the other door.

        Derived from the same wanted/banned sets as the suffix pool rather
        than a hand-kept parallel list, so a stat added to one is added to
        both. Falls back to the unfiltered pool for an unknown template,
        which is the same fail-soft the suffix path uses.

        `haste` nearly left the game here. It is in none of the 83 authored
        suffixes, so the first version of this filter dropped it for every
        template and bonus Haste rolls stopped happening - quietly, which is
        the wrong way for a stat to die. audit_stat_coherence then found two
        hand-authored quest items carrying it, so it is now in the shared
        set and survives. It still has no suffix, which means it reaches
        gear only by bonus roll or by hand; adding one is Kyle's call.
        """
        pool = self.stat_templates["secondary_stat_pool"]
        wanted = self._SUFFIX_TEMPLATE_STATS.get(stat_template)
        if not wanted:
            return pool
        banned = self._SUFFIX_TEMPLATE_EXCLUDES.get(stat_template, frozenset())
        return [s for s in pool if s in wanted and s not in banned] or pool

    def _roll_stats(self, stat_template, total_budget, bonus_rolls, rarity=None,
                    item_level=None, school=None):
        """Pick a real suffix (data/items/gear_suffixes.json) appropriate
        for stat_template, then distribute total_budget across that
        suffix's real stats using each stat's real budget COST (not an
        equal split) - a stat with cost 10.0 needs 10x the budget of a
        plain +1 Str to get +1 of it, which is exactly why low-level
        items roll fractional amounts of expensive stats like Crit/Haste/
        Parry Rating (Kyle's Gear.docx: "Level 6 Green Shield 'of
        Blocking': +1 Strength, +2 Block Value (or +0.3% Block Rating)").

        Replaces the old flat stat_templates.json system entirely - that
        system had 5 invented generic templates with fixed 0.7/0.3-style
        splits and no per-stat cost differentiation (every stat cost
        exactly 1 budget point, so a "+1% Crit" was exactly as easy to
        roll as "+1 Strength", which is why rings/trinkets were coming
        out as things like "+0.1% Crit Chance" - Kyle's report - instead
        of real, meaningful primary stats).

        Poor/Common items return empty stat dicts unconditionally - white
        gear in WoW is armor-only, not a source of Strength/Agility/etc.

        Returns (primary_stats, secondary_stats, suffix_name) - the
        chosen suffix name is returned so callers can build a real item
        name from it (see _generate_armor_name/_generate_weapon_name)
        instead of a name disconnected from the item's actual stats.
        """
        if rarity in self.STATLESS_RARITIES:
            return {}, {}, None

        low_level = item_level is not None and item_level < self.LOW_LEVEL_STAT_CAP
        candidates = self._suffixes_for_template(stat_template, low_level=low_level,
                                                 item_level=item_level,
                                                 school=school)
        suffix_name = random.choices(
            candidates,
            weights=[self._suffix_weight(n, stat_template) for n in candidates],
        )[0]
        suffix_stats = self.gear_suffixes[suffix_name]["stats"]

        # Real budget-cost-aware division: each stat's raw weight is
        # divided by its cost, so an expensive stat (Haste, cost 12.0)
        # comes out much smaller per budget-point spent than a cheap one
        # (a primary stat, cost 1.0) - matches the doc's actual worked
        # examples rather than a flat 1-point-per-stat assumption.
        primary_stats = {}
        secondary_stats = {}
        # WoW convention: Strength/Agility/Intellect/Stamina/Spirit are
        # "primary" stats (shown in the character panel's core stats);
        # everything else (ratings, spell power, resistances, mp5, ...)
        # is a "secondary" stat for display/UI purposes, even though both
        # come from the exact same suffix roll here.
        PRIMARY_STAT_NAMES = {"strength", "agility", "intellect", "stamina", "spirit"}

        for stat_name, weight in suffix_stats.items():
            cost = self.stat_budget_costs.get(stat_name, 1.0)
            raw_value = (total_budget * weight) / cost
            # Primary stats round to whole numbers (a fractional "+2.3
            # Strength" reads as a bug, not flavor); rating/spell-power/
            # resistance stats keep one decimal of precision - low-budget
            # items are SUPPOSED to show "+0.3% Block Rating" per the
            # doc's own examples, rounding those to whole numbers would
            # zero out nearly every early-game secondary stat roll.
            if stat_name in PRIMARY_STAT_NAMES:
                value = round(raw_value)
                if value > 0:
                    primary_stats[stat_name] = value
            else:
                value = round(raw_value, 1)
                if value > 0:
                    secondary_stats[stat_name] = value

        # Bonus secondary rolls (Rare+ items) still pull from the older
        # generic secondary_stat_pool (crit/haste/dodge/spell_power/AP/
        # healing/hit) as EXTRA stats layered on top of the suffix's own
        # allocation - a suffix defines the item's core identity, bonus
        # rolls are the "and also a little of something else" flavor
        # rarer items get, same role bonus_stat_rolls always played.
        # Skipped entirely below LOW_LEVEL_STAT_CAP - a rare/epic drop at
        # level 4 has no business rolling bonus Haste/Crit Rating when
        # those stats don't exist on gear yet at that level.
        if bonus_rolls > 0 and not low_level:
            pool = self._bonus_pool(stat_template)
            available = [s for s in pool if s not in secondary_stats]
            chosen = random.sample(available, min(bonus_rolls, len(available)))
            bonus_budget = total_budget * 0.15
            for stat_name in chosen:
                cost = self.stat_budget_costs.get(stat_name, 1.0)
                value = round((bonus_budget / len(chosen)) / cost, 1)
                if value > 0:
                    secondary_stats[stat_name] = secondary_stats.get(stat_name, 0) + value

        return primary_stats, secondary_stats, suffix_name

    def _generate_armor_name(self, rarity, slot, stat_template, suffix_name=None):
        """Real item name = [rarity prefix] [slot noun] [suffix], e.g.
        "Reinforced Robe of Intellect" - matches Kyle's Gear.docx naming
        convention directly. suffix_name is None for Poor/Common items
        (STATLESS_RARITIES never roll a suffix - white gear has no
        stats to name a suffix after) and for the shield-no-stats
        fallback path, in which case the name has no suffix at all,
        same as before this system existed."""
        prefix = random.choice(ARMOR_NAME_PREFIXES.get(rarity, ARMOR_NAME_PREFIXES["common"]))
        # The NOUN table is keyed by the kind of thing ("ring", "trinket"); the EQUIPMENT is
        # keyed by the physical slot ("ring1", "ring2", "trinket1", "trinket2"). Anything
        # generated for a numbered slot missed the table entirely and came out named "Simple
        # Item" - which is how a level 32 companion ended up wearing a "Reinforced Item of the
        # Squire". Strip the trailing index and ask once.
        noun_map = ARMOR_NAME_NOUNS.get(slot) or ARMOR_NAME_NOUNS.get(
            str(slot).rstrip("12") if slot else slot, {"_default": "Item"})
        noun = noun_map.get(stat_template, noun_map.get("_default", "Item"))
        base_name = f"{prefix} {noun}"
        return f"{base_name} {suffix_name}" if suffix_name else base_name

    def _generate_weapon_name(self, rarity, weapon_type, stat_template, suffix_name=None):
        """Real item name = [rarity prefix] [weapon noun] [suffix] - see
        _generate_armor_name's docstring for the same convention."""
        prefix = random.choice(ARMOR_NAME_PREFIXES.get(rarity, ARMOR_NAME_PREFIXES["common"]))
        noun = random.choice(WEAPON_NAME_NOUNS.get(weapon_type, ["Weapon"]))
        base_name = f"{prefix} {noun}"
        return f"{base_name} {suffix_name}" if suffix_name else base_name
