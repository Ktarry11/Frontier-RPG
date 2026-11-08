#!/usr/bin/env python3
"""Carry Blacksmithing from skill 245 to 300, on every bar instead of four.

    PYTHONPATH=. python3 tools/build_blacksmithing_300.py [--apply]

Idempotent. Prints the plan by default; --apply writes it.

=============================================================================
WHAT WAS WRONG
=============================================================================

Kyle, 7 Nov 2026: "I want to expand out the crafting... Go to skill 300", and
"I want crafting to be FULLY viable as a path alternative to raids and
Dungeons."

Blacksmithing stopped at 245 and stood on FOUR bars - copper, rough iron,
bronze, iron, with a handful of steel and mithril. Nineteen of twenty-three
bars inside 1-300 smelted perfectly and went nowhere, Thorium and Dark Iron
and Truesilver among them. The recipe skill climbed; the materials did not.
The 39 rare recipes at skill 150-199 were all built on low-tier bars.

=============================================================================
ROLE PAIRS - the specialization rule
=============================================================================

Kyle: "I don't like that one ore, or cloth, or herb makes multiple things.
Like for me having different cloth being specialized is ideal. Want Healer
gear? Use cotton. Want dps? Use hemp." Asked how strictly, he chose role
PAIRS: each material covers two related roles rather than one, or everything.

The six stat templates split into three natural pairs, so three bars cover
every role in a band and a fourth would be a duplicate rather than an option:

    PLATE  str_physical + str_int_hybrid      warriors and the hybrid plate
    MAIL   agi_physical + agi_int_hybrid      rogues, hunters, tinkers
    SPELL  int_caster   + spi_healer          casters and healers

This is what the audit was complaining about - before this, eight late
leathers all reached exactly agi_physical and three early cloths reached an
identical set of four. Interchangeable, not specialized.

=============================================================================
VIABLE AGAINST RAIDS - what the number has to be
=============================================================================

Boss drops in this game cap at RARE, item level 57. Kyle chose "Epic, matching
raid item level", so the top of this ladder must reach epic at item level
56-61.

It falls out of the existing formula rather than needing a new one.
world/crafting_manager.py: item_level = int(skill * 60 / 300) + 1. So skill
275 is item level 56 and skill 300 is 61 - parity with the best boss loot, by
construction, with no special case.

Epic begins at skill 265 (item level 54) rather than at the first endgame bar,
because an epic at item level 50 would be an epic that loses to a dungeon
drop, which is worse for the crafting path than no epic at all.

=============================================================================
UPGRADE KITS
=============================================================================

Every metal tier that gear can be made from needs a kit, or that gear is
second-class against Copper. world/upgrade_manager.py's MATERIAL_KITS had five
metals; this adds one per new bar, with the recipe that crafts it. The python
dict is NOT written by this tool - it prints the lines to paste, because that
file carries reasoning in its comments and a script would trample it.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RECIPES = ROOT / "data" / "blacksmithing" / "recipes.json"
MATS = ROOT / "data" / "gathering" / "materials.json"

#: stat template pairs - see docstring.
PAIRS = {
    "PLATE": ("str_physical", "str_int_hybrid"),
    "MAIL":  ("agi_physical", "agi_int_hybrid"),
    "SPELL": ("int_caster", "spi_healer"),
}
ARMOR_TYPE = {"PLATE": "plate", "MAIL": "mail", "SPELL": "mail"}

#: SPELL bars alternate between mail and plate rather than all making mail.
#:
#: Kyle, 7 Nov: "We can have BS still make some crafter gear too. Since we have
#: primalist.... plate with a caster spec. Or ele shaman with int", and "having
#: some int/sp plate is fine etc". Both shapes exist in this game - an
#: elemental shaman wants int mail, a Primalist wants a caster's plate - so a
#: smith who only ever made caster MAIL would be serving half of them.
#:
#: Note this is about int_caster and spi_healer specifically. The plate
#: casters whose CLASS default is str_int_hybrid (Primalist, Sun Cleric,
#: Knight of Xoroth, Cultist, Paladin) are already served by the PLATE pair;
#: this covers the ones who get there by SPEC instead - Kyle: "Chronomancer is
#: spi Healer or dps", which is why spi_healer maps to no class by default and
#: is not the orphan it looks like in class_stat_template_map.
SPELL_ARMOR = {
    "bar_living_copper":   "mail",
    "bar_frostveined_tin": "plate",
    "bar_verdant_iron":    "mail",
    "bar_truesilver":      "plate",
    "bar_arcanite":        "plate",
}

#: bar -> role pair. Flavour picked the pair: silver and gold and truesilver
#: are the caster metals, the "-iron" variants are workhorse plate, the lighter
#: and stranger alloys are mail.
#: Silver and Gold are DELIBERATELY ABSENT. They are precious, soft metals -
#: WoW makes rods and jewelry from them and never armour, and a Silver Hauberk
#: is exactly the illogical item Kyle called out. Neither is orphaned by this:
#: engineering already consumes bar_silver and bar_gold.
BAR_ROLES = {
    "bar_weakstone":       "MAIL",
    "bar_tin":             "PLATE",
    "bar_bronze_vein":     "MAIL",
    "bar_living_copper":   "SPELL",
    "bar_frostveined_tin": "SPELL",   # frost-veined metal reads as a caster alloy
    "bar_verdant_iron":    "SPELL",   # living/green iron - nature caster and healer
    "bar_felslag":         "PLATE",
    "bar_bloodiron":       "PLATE",
    "bar_deepearth":       "MAIL",
    "bar_dark_iron":       "PLATE",
    "bar_truesilver":      "SPELL",
    "bar_thorium":         "PLATE",
    "bar_ashen_steel":     "MAIL",
    "bar_arcanite":        "SPELL",
    "bar_elementium":      "PLATE",
}

#: Armour slots, cycled so coverage spreads evenly up the ladder instead of
#: every bar making the same four pieces.
SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet"]

#: Weapons a bar may make, BY ROLE. Not one shared rotation.
#:
#: Kyle, 7 Nov: "Make crafted items make sense....no illogical shit." A blind
#: rotation produced a Silver Great Axe granting Intellect, a Gold Great Axe
#: for casters, and a Living Copper Hatchet with Spirit - a two-handed axe is
#: not a healer's weapon whatever metal it is made of. The weapon has to suit
#: the role, so the role owns the list.
WEAPONS_BY_ROLE = {
    "PLATE": [("main_hand", "sword_1h"), ("two_hand", "axe_2h"),
              ("main_hand", "axe_1h"), ("two_hand", "sword_2h"),
              ("two_hand", "polearm"), ("off_hand", "shield")],
    # NO SHIELD. The MAIL pair is agi_physical + agi_int_hybrid - rogues,
    # hunters, rangers, tinkers - and none of them carry one. An "Ashen Steel
    # Bulwark" with Agility was the second illogical item this pass produced.
    # The shield is back, PINNED to agi_int_hybrid. Kyle, 7 Nov: "Rogues and
    # hunters don't use shields. But sure. Tinkerers can." Tinker, Felsworn,
    # Venomancer and Witch Doctor are agi_int_hybrid; rogues, hunters and
    # rangers are agi_physical. A third element forces the template so the
    # shield can never land on the agility-physical half of the pair.
    "MAIL":  [("main_hand", "sword_1h"), ("main_hand", "dagger"),
              ("main_hand", "axe_1h"), ("two_hand", "polearm"),
              ("off_hand", "shield", 1)],
    # No great axes, no polearms. A caster or healer carries a mace, a dagger,
    # or a shield - the three a smith can plausibly make for them.
    "SPELL": [("main_hand", "mace_1h"), ("main_hand", "dagger"),
              ("off_hand", "shield")],
}

ARMOUR_PER_BAR = 4
WEAPONS_PER_BAR = 2
SKILL_STEP = 5

#: Bars produced per piece, by slot. Mirrors the existing recipes' own costs.
BAR_COST = {"chest": 8, "legs": 7, "head": 6, "shoulder": 5, "hands": 4,
            "feet": 4, "waist": 4, "wrist": 3,
            "main_hand": 6, "two_hand": 10, "off_hand": 6}

PIECE_NAME = {"head": "Helm", "shoulder": "Pauldrons", "chest": "Breastplate",
              "wrist": "Bracers", "hands": "Gauntlets", "waist": "Girdle",
              "legs": "Legplates", "feet": "Sabatons"}
MAIL_NAME = {"head": "Coif", "shoulder": "Spaulders", "chest": "Hauberk",
             "wrist": "Wristguards", "hands": "Grips", "waist": "Belt",
             "legs": "Leggings", "feet": "Boots"}
WEAPON_NAME = {"sword_1h": "Blade", "axe_1h": "Hatchet", "mace_1h": "Mace",
               "sword_2h": "Greatsword", "axe_2h": "Great Axe",
               "shield": "Bulwark", "polearm": "Halberd", "dagger": "Dirk"}

EPIC_FROM = 265
RARE_FROM = 150
CEILING = 300


def item_level(skill):
    """The game's own formula - world/crafting_manager.py line 130."""
    return max(1, int(skill * 60 / 300) + 1)


def rarity(skill):
    if skill >= EPIC_FROM:
        return "epic"
    return "rare" if skill >= RARE_FROM else "uncommon"


def spread(lo):
    return [lo + 5, lo + 15, lo + 25, lo + 35]


def tier_of(bar):
    return bar[4:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    mats_doc = json.loads(MATS.read_text())
    mats = mats_doc["materials"]
    doc = json.loads(RECIPES.read_text())
    recipes = doc["recipes"]

    missing = [b for b in BAR_ROLES if b not in mats]
    if missing:
        print(f"  REFUSING - bar(s) not in materials.json: {', '.join(missing)}")
        return 1

    before_max = max((r.get("skill_required", 0) for r in recipes.values()
                      if isinstance(r, dict)), default=0)

    new_recipes, new_kits, si, wi = {}, {}, 0, 0
    for bar in sorted(BAR_ROLES, key=lambda b: mats[b]["skill_range"][0]):
        role = BAR_ROLES[bar]
        base = mats[bar]["skill_range"][0]
        tier = tier_of(bar)
        a, b = PAIRS[role]
        atype = SPELL_ARMOR.get(bar, ARMOR_TYPE[role]) if role == "SPELL" else ARMOR_TYPE[role]
        step = 0

        for k in range(ARMOUR_PER_BAR):
            slot = SLOTS[si % len(SLOTS)]; si += 1
            skill = min(CEILING, base + step); step += SKILL_STEP
            tmpl = (a, b)[k % 2]
            names = PIECE_NAME if atype == "plate" else MAIL_NAME
            rid = f"bs300_{tier}_{slot}"
            if rid in recipes:
                continue
            new_recipes[rid] = dict(
                name=f"{mats[bar]['name'].replace(' Bar', '')} {names[slot]}",
                skill_required=skill, skill_range=spread(skill), source="trainer",
                inputs={bar: BAR_COST[slot]},
                output=dict(kind="armor", slot=slot, armor_type=atype,
                            stat_template=tmpl, item_level=item_level(skill),
                            rarity=rarity(skill), material_tier=tier))

        wlist = WEAPONS_BY_ROLE[role]
        for k in range(WEAPONS_PER_BAR):
            entry = wlist[wi % len(wlist)]; wi += 1
            slot, wtype = entry[0], entry[1]
            skill = min(CEILING, base + step); step += SKILL_STEP
            # a third element pins which half of the pair this weapon serves
            tmpl = (a, b)[entry[2]] if len(entry) > 2 else (a, b)[k % 2]
            rid = f"bs300_{tier}_{wtype}"
            if rid in recipes:
                continue
            new_recipes[rid] = dict(
                name=f"{mats[bar]['name'].replace(' Bar', '')} {WEAPON_NAME[wtype]}",
                skill_required=skill, skill_range=spread(skill), source="trainer",
                inputs={bar: BAR_COST[slot]},
                output=dict(kind="weapon", slot=slot, weapon_type=wtype,
                            stat_template=tmpl, item_level=item_level(skill),
                            rarity=rarity(skill), material_tier=tier))

        kit_id = f"upgrade_kit_{tier}"
        if kit_id not in mats:
            new_kits[kit_id] = dict(
                name=f"{mats[bar]['name'].replace(' Bar', '')} Upgrade Kit",
                material_type="upgrade_kit", profession="blacksmithing",
                tier=mats[bar]["tier"], # Convention, not a guess: every existing kit names its icon after
                # itself. Only 2 of 29 of those files exist today and the rest
                # already fall back to the bag's text box, so following the
                # convention means art drops in with no data change.
                icon_id=kit_id,
                stack_limit=20, sell_price=max(10, base * 3),
                skill_range=spread(base),
                description=f"Plates and rivets for reworking {tier.replace('_', ' ')} gear.")
            rid = f"bs300_kit_{tier}"
            if rid not in recipes:
                new_recipes[rid] = dict(
                    name=new_kits[kit_id]["name"], skill_required=min(CEILING, base + 20),
                    skill_range=spread(min(CEILING, base + 20)), source="trainer",
                    inputs={bar: 6},
                    output=dict(kind="material", material_id=kit_id))

    gear = [r for r in new_recipes.values() if r["output"]["kind"] != "material"]
    after_max = max([before_max] + [r["skill_required"] for r in new_recipes.values()])
    print(f"  blacksmithing reaches skill {before_max} -> {after_max}")
    print(f"  {len(recipes)} -> {len(recipes) + len(new_recipes)} recipes "
          f"({len(gear)} gear, {len(new_kits)} upgrade kits)")
    print(f"  bars used: 4 -> {4 + len(BAR_ROLES)} of {len(BAR_ROLES) + 6}\n")

    # A re-run with nothing to do must print a clean "already applied" rather
    # than crash on min() of an empty list. This tool is meant to be re-run
    # after the skill ladders move, so the no-op path is a real path.
    if not gear and not new_kits:
        print("  nothing to do - already applied")
        return 0

    import collections
    byr = collections.Counter(r["output"]["rarity"] for r in gear)
    print(f"  rarity: " + ", ".join(f"{k} {v}" for k, v in sorted(byr.items())))
    lv = [r["output"]["item_level"] for r in gear]
    print(f"  item level {min(lv)}-{max(lv)}   (boss drops cap at rare, 57)")
    epics = [r for r in gear if r["output"]["rarity"] == "epic"]
    if epics:
        el = [r["output"]["item_level"] for r in epics]
        print(f"  {len(epics)} epics at item level {min(el)}-{max(el)}")

    tmpl = collections.Counter(r["output"]["stat_template"] for r in gear)
    print(f"\n  role coverage: " + ", ".join(f"{k} {v}" for k, v in sorted(tmpl.items())))
    missing_roles = {t for p in PAIRS.values() for t in p} - set(tmpl)
    if missing_roles:
        print(f"  MISSING ROLES: {', '.join(sorted(missing_roles))}")

    print(f"\n  {'bar':22}{'pair':7}{'skill':>11}{'rarity':>10}   pieces")
    for bar in sorted(BAR_ROLES, key=lambda b: mats[b]["skill_range"][0]):
        tier = tier_of(bar)
        rs = [r for k, r in new_recipes.items()
              if k.startswith(f"bs300_{tier}_") and r["output"]["kind"] != "material"]
        if not rs:
            continue
        sk = [r["skill_required"] for r in rs]
        print(f"  {mats[bar]['name'][:20]:22}{BAR_ROLES[bar]:7}"
              f"{f'{min(sk)}-{max(sk)}':>11}{rs[-1]['output']['rarity']:>10}   "
              f"{len(rs)}")

    if new_kits:
        print(f"\n  PASTE INTO world/upgrade_manager.py MATERIAL_KITS:")
        for k in new_kits:
            print(f'    "{k}":{" " * max(1, 26 - len(k))}"{k[len("upgrade_kit_"):]}",')

    if args.apply:
        recipes.update(new_recipes)
        RECIPES.write_text(json.dumps(doc, indent=2) + "\n")
        mats.update(new_kits)
        MATS.write_text(json.dumps(mats_doc, indent=2) + "\n")
        print(f"\n  wrote recipes.json, materials.json")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
