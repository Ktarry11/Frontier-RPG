#!/usr/bin/env python3
"""Derive a per-spec GEAR PROFILE and write data/items/spec_gear.json.

    PYTHONPATH=. python3 tools/build_spec_gear.py [--check]

WHY THIS EXISTS. Gear was itemized by CLASS and nothing else. A class has
one armor type and one stat template in data/items/{armor_types,
stat_templates}.json, which is right for armor (a Shaman wears mail in every
spec) and badly wrong for everything else: the Shaman entry is int_caster, so
an Enhancement Shaman - a melee attacker - was itemized as a caster, and
every one of the six <school>_spell_power stats sat in a single set, so a
Fire Mage could roll +Holy spell power. Kyle, 6 Nov: "Ive seen a fire mage
come with +holy spell power gear."

The spec is the missing key, and it is already in the data - every recruit in
data/npcs/recruits.json carries one, and a player character's is read by
entities/proficiency.active_spec. So this derives, per spec:

    role            tank / healer / melee_dps / ranged_dps
    stat_template   which of stat_templates.json's six the spec itemizes as
    school          the damage school its gear should carry spell power in
    weapons         main_hand / off_hand / ranged, by weapon TYPE

NOTHING HERE IS HAND-AUTHORED, because a 97-row table typed by hand is a
table that drifts the first time a talent tree changes. Every field is read
out of data the game already runs on, and the tool prints which source each
one came from so a guess cannot hide:

    role      the authored gear_theme in recruits.json where a companion
              uses this spec; else the role in data/reference/
              coa_playstyles.json's derived block; else classified from the
              tree's own talent effect keys (threat/block/parry -> tank,
              healing_done/hot_duration -> healer, and so on). The authored
              themes were cross-checked against the reference's own role
              column and disagree on three of 68 - Grovekeeper (a support
              that heals), Moon Priest (Discipline Priest) and Black Knight
              (Blood DK) - all three defensible, so the authored value wins.
              Only four specs have neither source and reach the classifier:
              druid_feral, runemaster_engravement, warlock_affliction and
              witch_doctor_shadowhunting.
    melee or  the FIRST retail kit named in the reference's plays_like
    ranged    string, which is the dominant one ("Survival Hunter + Feral
              Druid" is a hunter first). NOT whether the class has bow
              proficiency: Warriors and Rogues both do, and an early version
              of this classified every Warrior spec as ranged because of it.
    school    the tree's <school>_spell_damage effects, its procs' schools,
              and the damage_school of every ability its nodes name, with
              the class's own ability spread as the tiebreak. Pure counting.
    template  role + what the class is proficient in, narrowed to what the
              chosen weapon type actually accepts (weapon_types.json's
              valid_stat_templates silently SWAPS a template it does not
              accept, which is how a Fury Warrior ended up holding an
              intellect staff - see LootGenerator.generate_weapon).
    weapons   role + class_weapon_map + the dual_wield allow-list, in a
              preference order. A class with no shield proficiency gets a
              two-hander rather than a tome, and a ranged role gets its bow
              or gun in the RANGED slot, which nothing filled before.

--check re-derives and diffs against the committed file instead of writing,
so CI catches a talent edit that moves a spec without the file being rebuilt.
"""

import argparse
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/items/spec_gear.json"

SCHOOLS = ("fire", "frost", "arcane", "shadow", "nature", "holy")

#: Talent effect keys that mark a tree's role. HARD markers are ones only
#: that role has any use for; SOFT ones are suggestive but appear in trees
#: of every role (every tree has some damage_taken_pct), so they only break
#: ties. Classifying on the soft set alone called Beast Mastery a tank.
HARD = {
    "tank": ("threat_generation_pct", "threat_multiplier", "block",
             "block_value_pct", "shield_armor_pct", "parry", "dodge",
             "crit_taken_reduction"),
    "healer": ("healing_done", "healing_power_pct", "hot_duration_pct",
               "heal_cost_pct", "healing_spell_cost_pct",
               "low_health_healing_pct", "healing_power_from_intellect_pct",
               "healing_power_from_spirit_pct", "healing_power_from_spirit_pct"),
    "phys": ("attack_power_pct", "physical_damage", "crit_chance_physical",
             "crit_damage_physical", "armor_penetration",
             "armor_penetration_pct", "expertise",
             "attack_power_from_intellect_pct", "attack_power_from_stamina_pct",
             "ranged_ap_from_agility_pct", "ranged_ap_from_intellect_pct",
             "ranged_ap_from_spirit_pct"),
    "cast": ("spell_damage", "crit_chance_spell", "crit_damage_spell",
             "dot_damage", "spell_penetration", "spell_power_from_intellect_pct",
             "spell_power_from_spirit_pct", "spell_power_from_agility_pct",
             "spell_power_from_strength_pct", "spell_power_from_stamina_pct",
             "spell_power_from_ap_pct", "spell_damage_from_intellect_pct",
             "spell_damage_from_spirit_pct", "spell_damage_from_strength_pct",
             "crit_chance_spell_from_intellect_pct",
             "crit_chance_spell_from_spirit_pct"),
}
SOFT = {
    "tank": ("damage_taken_pct", "physical_damage_taken_pct",
             "magic_damage_taken_pct", "armor_pct", "stamina_pct",
             "max_health_pct", "low_health_damage_reduction_pct",
             "spell_damage_taken_pct"),
    "healer": ("healing_taken_pct",),
    "phys": ("aoe_damage",),
    "cast": ("mp5", "max_mana_pct"),
}

#: Which weapon type to reach for first, by role. Intersected with the
#: class's own class_weapon_map, so a preference the class cannot hold is
#: simply skipped - this is an order, not a promise.
ONE_HAND = ["sword_1h", "mace_1h", "axe_1h", "fist_weapon", "dagger"]
#: STAFF IS NOT IN HERE. A staff is a two-hander, but it is the softest
#: auto-attack weapon in the game by design (damage_tier "staff", 0.55
#: against a real two-hander's 1.8 - see weapon_types.json) and it accepts
#: only caster templates, so putting it in the physical two-hand order gave
#: a melee Bloodmage and a Feral Druid a staff while both classes had a real
#: two-hander available. Casters get it from CASTER_TWO_HAND.
TWO_HAND = ["sword_2h", "axe_2h", "polearm", "mace_2h"]
#: A rogue reaches for a dagger and a warrior for a sword, so the melee
#: one-hand order is not the tank one.
ROGUE_ONE_HAND = ["dagger", "sword_1h", "fist_weapon", "axe_1h", "mace_1h"]
CASTER_TWO_HAND = ["staff"]
CASTER_ONE_HAND = ["mace_1h", "dagger", "sword_1h", "axe_1h"]
PHYS_RANGED = ["bow", "gun", "crossbow", "thrown"]
CASTER_RANGED = ["wand", "libram", "idol", "totem"]
CASTER_OFF_HAND = ["tome"]

#: The physical half of each hybrid stat template. A hybrid class itemizing
#: a tank or melee spec wants the stat its own kit is built around, not
#: whichever physical template a weapon type happens to list first: Felsworn
#: is leather and agility-side, so its tank is agi_physical, and an earlier
#: version handed it str_physical because sword_2h lists Strength first.
PHYSICAL_SIDE = {
    "agi_int_hybrid": "agi_physical",
    "str_int_hybrid": "str_physical",
    "agi_physical": "agi_physical",
    "str_physical": "str_physical",
}
#: ...and for a class whose map entry is a pure caster template but whose
#: spec is physical anyway (Feral Druid, a melee Starcaller), the armour
#: weight decides. Plate is a Strength chassis; everything lighter is an
#: Agility one. Overridden by the spec's own Strength/Agility talent
#: signals wherever its tree has any - see physical_side().
ARMOR_PHYSICAL_SIDE = {"plate": "str_physical"}

#: Retail kit names in the reference's plays_like string, and whether that
#: kit fights at range. Scanned LEFT TO RIGHT and the first hit wins,
#: because the reference lists the dominant kit first.
KIT_RANGE = [
    ("marksmanship", True), ("survival", False), ("beast mastery", True),
    ("moonkin", True), ("balance druid", True), ("feral", False),
    ("elemental", True), ("enhancement", False), ("restoration", True),
    ("mistweaver", False), ("windwalker", False),
    ("affliction", True), ("destruction", True), ("demonology", True),
    ("shadow priest", True), ("discipline", True), ("holy priest", True),
    ("retribution", False), ("protection", False),
    ("death knight", False), ("demon hunter", False),
    ("augmentation", True), ("evoker", True),
    ("mage", True), ("warlock", True), ("hunter", True), ("priest", True),
    ("rogue", False), ("warrior", False), ("paladin", False),
    ("monk", False), ("druid", False), ("shaman", False),
]


def load(rel):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


def ability_schools():
    """ability_id -> [school, ...] for every ability in the game."""
    out = {}
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        data = load(path.relative_to(ROOT))
        for entry in (data["abilities"] if isinstance(data, dict) else data):
            school = entry.get("damage_school")
            if not school:
                continue
            out[entry["ability_id"]] = school if isinstance(school, list) else [school]
    return out


def class_school_spread(ab_schools):
    """class_file -> Counter of schools across that class's whole kit.

    The tiebreak for a spec whose own tree names no school at all - a
    Restoration Shaman's tree is all healing and says nothing about fire or
    nature, but the class it belongs to plainly casts nature.
    """
    out = {}
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        data = load(path.relative_to(ROOT))
        counter = collections.Counter()
        for entry in (data["abilities"] if isinstance(data, dict) else data):
            school = entry.get("damage_school")
            for s in (school if isinstance(school, list) else [school]):
                if s in SCHOOLS:
                    counter[s] += 1
        out[path.stem] = counter
    return out


#: Primary stats, for the Strength-vs-Agility read in physical_side().
STAT_NAMES = ("strength", "agility", "intellect", "spirit", "stamina")


def tree_signals(tree, ab_schools):
    """(role_scores, school_counts, stat_counts) off one spec's nodes."""
    role = collections.Counter()
    schools = collections.Counter()
    stats = collections.Counter()
    for node in tree["nodes"]:
        effects = dict(node.get("effects") or {})
        proc = node.get("proc") or {}
        if isinstance(proc, dict) and proc.get("school") in SCHOOLS:
            schools[proc["school"]] += 1
        for key in effects:
            for name, keys in HARD.items():
                if key in keys:
                    role[name] += 2
            for name, keys in SOFT.items():
                if key in keys:
                    role[name] += 1
            for stat in STAT_NAMES:
                if key in (stat, f"{stat}_pct") or key.endswith(f"_from_{stat}_pct"):
                    stats[stat] += 1
            m = re.match(r"^(%s)_spell_damage$" % "|".join(SCHOOLS), key)
            if m:
                # A tree that buffs a school BY NAME is the strongest
                # statement it can make about what it casts.
                schools[m.group(1)] += 3
            if key.startswith("ability_"):
                core = key[len("ability_"):]
                for aid, sch in ab_schools.items():
                    if core.startswith(aid):
                        for s in sch:
                            if s in SCHOOLS:
                                schools[s] += 1
        unlock = effects.get("unlock_ability")
        for aid in ([unlock] if isinstance(unlock, str) else (unlock or [])):
            for s in ab_schools.get(aid, []):
                if s in SCHOOLS:
                    schools[s] += 1
    return role, schools, stats


def classify_role(role_scores, ranged_class):
    """tank / healer / melee_dps / ranged_dps from the talent scores.

    Tank needs a HARD marker and not merely the best score, because the
    defensive soft keys are in every tree in the game.
    """
    hard_tank = role_scores["tank"] >= 2
    hard_heal = role_scores["healer"] >= 2
    if hard_heal and role_scores["healer"] >= role_scores["tank"]:
        return "healer"
    if hard_tank and role_scores["tank"] > max(role_scores["phys"],
                                               role_scores["cast"]):
        return "tank"
    if role_scores["phys"] > role_scores["cast"]:
        return "ranged_dps" if ranged_class else "melee_dps"
    if role_scores["cast"]:
        return "ranged_dps"
    return "melee_dps"


def pick(order, allowed, weapons=None, wants=None):
    """First type in `order` the class owns - and, if `wants` is given,
    that also ACCEPTS that stat template.

    The second condition is the whole reason this takes the extra two
    arguments. weapon_types.json gives each type a valid_stat_templates
    list, and LootGenerator.generate_weapon silently substitutes
    valid_stat_templates[0] for anything not on it. So choosing the weapon
    and the template independently does not produce a mismatch you can see
    - it produces an item quietly itemized for somebody else, which is how
    a Fury Warrior ended up holding an intellect staff and how a physical
    Bloodmage tank ended up itemized int_caster.
    """
    for wt in order:
        if wt not in allowed:
            continue
        if wants and weapons:
            ok = weapons["weapon_types"][wt]["valid_stat_templates"]
            if ok and wants not in ok:
                continue
        return wt
    return None


def physical_side(class_default, armor_type, stat_signals):
    """str_physical or agi_physical for a spec that fights with its hands."""
    side = PHYSICAL_SIDE.get(class_default)
    if side:
        return side
    # The tree's own Strength/Agility talents, where it has any - Feral
    # Druid's three agility nodes say agility louder than Druid's class map
    # entry (int_caster) says anything.
    if stat_signals["strength"] != stat_signals["agility"]:
        return ("str_physical" if stat_signals["strength"] > stat_signals["agility"]
                else "agi_physical")
    return ARMOR_PHYSICAL_SIDE.get(armor_type, "agi_physical")


def wanted_templates(role, char_class, is_caster, templates, armor_type,
                     stat_signals):
    """The stat templates this spec would itemize as, best first."""
    class_default = templates["class_stat_template_map"].get(char_class, "int_caster")
    physical = physical_side(class_default, armor_type, stat_signals)
    if role == "healer":
        return ["spi_healer", "int_caster", class_default]
    if role in ("tank", "melee_dps") or not is_caster:
        # A hybrid keeps its hybrid template when the weapon accepts one,
        # since half its kit really is spells. A PURE CASTER map entry does
        # NOT survive a physical role: an int_caster Feral Druid tank is the
        # itemization bug this whole file exists to stop, so the physical
        # side comes first and the class default is only a fallback.
        head = [class_default, physical] if class_default in PHYSICAL_SIDE \
            else [physical, class_default]
        return head + ["agi_physical", "str_physical"]
    return ["int_caster", class_default]


def weapon_plan(char_class, spec, role, is_caster, weapons, may_dw, wants):
    """{main_hand, off_hand, ranged} by weapon type.

    The three bugs this is written against, all measured on the live 68
    recruits: the main hand was whatever the generator rolled at random
    (Fury Warrior with a staff), the ranged slot was EMPTY on all 68 (a
    Tinker with no gun - Kyle's own example), and a tank with no shield
    proficiency was handed a tome.
    """
    allowed = set(weapons["class_weapon_map"].get(char_class, []))
    types = weapons["weapon_types"]
    plan = {"main_hand": None, "off_hand": None, "ranged": None}

    # THE CLASS'S OWN WEAPON FIRST. The orders below are generic - "a one-hander" means a
    # sword before anything else - so every class that can hold a sword came out holding
    # one: a Barbarian with swords, a Venomancer tank with maces, a Witch Hunter with a bow,
    # while entities/starting_gear.CLASS_WEAPON_TYPE (the hand-written list of what each
    # class is KNOWN for) says axe, dagger, crossbow. Where a pick has that weapon, or its
    # two-handed or one-handed sibling, among its choices, that comes first. The order is
    # otherwise untouched, so a class with no listed identity for a slot picks as before.
    import sys as _sys
    _root = str(Path(__file__).resolve().parent.parent)
    if _root not in _sys.path:
        _sys.path.insert(0, _root)
    from entities.starting_gear import CLASS_WEAPON_TYPE
    family = CLASS_WEAPON_TYPE.get(char_class, "").split("_")[0]

    def own_first(order):
        mine = [wt for wt in order if family and wt.split("_")[0] == family]
        return mine + [wt for wt in order if wt not in mine]

    def one(order, w=wants):
        order = own_first(order)
        return pick(order, allowed, weapons, w) or pick(order, allowed)

    caster_hands = is_caster and role in ("healer", "ranged_dps")

    def ranged_slot(caster_first):
        """The ranged slot, preferring the role's own family but taking the
        other rather than leaving the slot empty.

        A Tinker healer is the case this exists for, and it is Kyle's own
        example: "an inventor tinkerer (healer) doesn't come with a gun".
        Tinker has no wand, libram, idol or totem - its whole identity is
        guns - so a relic-only rule left her ranged slot empty, which is
        what it was before any of this. The gun keeps its own agi_physical
        itemization; the ranged slot does not vote on the kit's template."""
        first = CASTER_RANGED if caster_first else PHYS_RANGED
        second = PHYS_RANGED if caster_first else CASTER_RANGED
        return one(first) or one(second, None)
    if role == "tank":
        if "shield" in allowed:
            plan["main_hand"] = one(CASTER_ONE_HAND if caster_hands else ONE_HAND)
            plan["off_hand"] = "shield"
        else:
            # NO SHIELD, SO A TWO-HANDER - not a tome. A tank holding a
            # passive stat stick in the off hand was the measured state of
            # Bloodmage Eternal, Mountain King and Venomancer Fortitude.
            # A ONE-HANDER BEATS A STAFF here, because a staff accepts only
            # caster templates: a Bloodmage tank (no shield, no real
            # two-hander) came out holding a staff whose template then
            # silently overwrote his physical itemization.
            plan["main_hand"] = (one(TWO_HAND) or one(ONE_HAND)
                                 or one(CASTER_TWO_HAND))
    elif role == "healer":
        plan["main_hand"] = one(CASTER_ONE_HAND) or one(CASTER_TWO_HAND)
        plan["ranged"] = ranged_slot(True)
    elif role == "ranged_dps" and is_caster:
        plan["main_hand"] = one(CASTER_TWO_HAND) or one(CASTER_ONE_HAND)
        plan["ranged"] = ranged_slot(True)
    elif role == "ranged_dps":
        # A BOW IS THE WEAPON, so it is picked first and the melee hand is
        # whatever is left. Deliberately NOT dual-wielding even for a Hunter
        # the dual_wield table permits: Kyle, 6 Nov - "if a hunter is using 2
        # weapons and shoots a gun, the gun should be impacted by hit chance
        # associated with the gun" - a ranged companion should not be paying
        # an off-hand miss penalty on a hand it barely swings.
        plan["ranged"] = ranged_slot(False)
        plan["main_hand"] = one(ONE_HAND) or one(TWO_HAND)
    else:  # melee_dps
        order = ROGUE_ONE_HAND if char_class in ("Rogue", "Ranger", "Bloodmage") else ONE_HAND
        if may_dw:
            plan["main_hand"] = one(order)
            plan["off_hand"] = one(order)
        else:
            plan["main_hand"] = one(TWO_HAND) or one(order) or one(CASTER_TWO_HAND)
        plan["ranged"] = ranged_slot(is_caster)

    # The off hand, for anything that did not already claim it. A one-hander
    # goes there only for a class permitted to dual wield; everyone else gets
    # a shield if they own one, a tome if they are a caster, or nothing.
    if plan["off_hand"] is None and plan["main_hand"]:
        if types[plan["main_hand"]]["hand"] != "two_hand":
            plan["off_hand"] = (one(["shield"]) if role == "tank" else None) \
                or (one(CASTER_OFF_HAND) if is_caster else None)

    # A two-hander cannot share the hands with anything.
    mh = plan["main_hand"]
    if mh and types[mh]["hand"] == "two_hand":
        plan["off_hand"] = None
    return plan


def settle_template(wanted, plan, weapons):
    """The first wanted template the armour and both hands can share.

    One template for the WHOLE kit. 14 of the 68 measured recruits were
    wearing two at once - "agi_physical,int_caster" - because the armour
    took the class map's value and each weapon then swapped in whatever its
    own valid_stat_templates listed first.

    THE RANGED SLOT IS DELIBERATELY NOT IN THE VOTE. Every bow, gun and
    crossbow accepts agi_physical and nothing else, so counting it dragged
    all three Warrior specs and both Barbarian ones off Strength and onto
    Agility - the ranged weapon was itemizing the plate. A Warrior's bow
    carrying Agility while his armour carries Strength is how Classic gear
    actually reads, so the ranged piece keeps its own template.
    """
    types = weapons["weapon_types"]
    held = [plan[s] for s in ("main_hand", "off_hand") if plan.get(s)]
    for t in wanted:
        if all(not types[wt]["valid_stat_templates"]
               or t in types[wt]["valid_stat_templates"] for wt in held):
            return t
    return wanted[0]


def kit_is_ranged(plays_like):
    """Whether the dominant retail kit named in plays_like fights at range."""
    if not plays_like:
        return None
    low = plays_like.lower()
    best, pos = None, len(low) + 1
    for name, ranged in KIT_RANGE:
        at = low.find(name)
        if at != -1 and at < pos:
            best, pos = ranged, at
    return best


def build():
    weapons = load("data/items/weapon_types.json")
    templates = load("data/items/stat_templates.json")
    armors = load("data/items/armor_types.json")
    ab_schools = ability_schools()
    spread = class_school_spread(ab_schools)

    # Dual wield, spec-gated, straight out of the table the engine enforces
    # (entities/proficiency.can_dual_wield) rather than a second opinion.
    dual_wield = {}
    for cls, entry in weapons.get("dual_wield", {}).items():
        specs = entry.get("specs", "all") if isinstance(entry, dict) else entry
        dual_wield[cls] = specs
    # Role authored by Kyle for the companions, which beats any classifier.
    recruits = load("data/npcs/recruits.json")["recruits"]
    authored = {r["spec"]: r["gear_theme"] for r in recruits
                if r.get("spec") and r.get("gear_theme")}
    # The identity reference's own role and plays_like, for the specs no
    # companion uses. Not game data, so it only fills gaps.
    ref = {}
    for row in load("data/reference/coa_playstyles.json").get("derived", []):
        key = f"{row['class'].lower().replace(' ', '_')}_{row['spec'].lower().replace(' ', '_')}"
        ref[key] = row

    out = {}
    report = []
    for path in sorted((ROOT / "data/talents").glob("*.json")):
        tree = load(path.relative_to(ROOT))
        spec = tree["tree_id"]
        char_class = None
        for cls in weapons["class_weapon_map"]:
            key = cls.lower().replace(" ", "_")
            if spec.startswith(key + "_") and (char_class is None or len(key) > len(char_class[1])):
                char_class = (cls, key)
        if char_class is None:
            continue
        cls, class_key = char_class

        role_scores, schools, stat_signals = tree_signals(tree, ab_schools)
        row = ref.get(spec) or {}
        is_caster = (templates["class_stat_template_map"].get(cls)
                     in ("int_caster", "spi_healer"))
        # Whether this SPEC fights at range, from the dominant retail kit the
        # reference names. Falls back to the tree's own ranged attack-power
        # conversions, then to the class being a caster at all.
        ranged = kit_is_ranged(row.get("plays_like"))
        if ranged is None:
            ranged = any(k.startswith("ranged_ap_from_")
                         for n in tree["nodes"] for k in (n.get("effects") or {}))
            ranged = ranged or is_caster

        if spec in authored:
            role, source = authored[spec], "recruits.json"
        elif row.get("role") in ("Tank", "Healer"):
            role, source = row["role"].lower(), "coa_playstyles"
        elif row.get("role"):
            role = "ranged_dps" if ranged else "melee_dps"
            source = "coa_playstyles"
        else:
            role, source = classify_role(role_scores, ranged), "talents"
        derived = classify_role(role_scores, ranged)

        dw_specs = dual_wield.get(cls)
        may_dw = dw_specs == "all" or bool(dw_specs and spec in dw_specs)
        armor_type = armors["class_armor_map"].get(cls, "cloth")
        wanted = wanted_templates(role, cls, is_caster, templates, armor_type,
                                  stat_signals)
        plan = weapon_plan(cls, spec, role, is_caster, weapons, may_dw, wanted[0])
        tmpl = settle_template(wanted, plan, weapons)

        school = None
        if schools:
            school = schools.most_common(1)[0][0]
        elif spread.get(class_key):
            school = spread[class_key].most_common(1)[0][0]

        out[spec] = {
            "class": cls,
            "role": role,
            "role_source": source,
            "stat_template": tmpl,
            "armor_type": armor_type,
            "school": school,
            "dual_wield": bool(may_dw) and role == "melee_dps",
            "weapons": plan,
        }
        report.append((spec, role, source, derived, tmpl, school, plan))

    return out, report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()

    out, report = build()
    if not args.quiet:
        print(f"{'spec':30}{'role':12}{'src':16}{'derived':12}{'template':16}"
              f"{'school':8}main/off/ranged")
        mismatch = 0
        for spec, role, src, derived, tmpl, school, plan in report:
            flag = ""
            if src != "talents" and derived != role:
                flag = "  <- classifier disagrees"
                mismatch += 1
            print(f"{spec:30}{role:12}{src:16}{derived:12}{tmpl:16}"
                  f"{str(school):8}"
                  f"{plan['main_hand']}/{plan['off_hand']}/{plan['ranged']}{flag}")
        print(f"\n{len(out)} specs; classifier disagrees with an authored role "
              f"on {mismatch}")

    text = json.dumps(out, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != text:
            print(f"  STALE: {OUT} does not match a fresh derivation")
            return 1
        print(f"  {OUT} is up to date")
        return 0
    OUT.write_text(text, encoding="utf-8")
    print(f"  wrote {OUT} ({len(out)} specs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
