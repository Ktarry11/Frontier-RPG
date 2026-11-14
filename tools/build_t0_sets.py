#!/usr/bin/env python3
"""Build the thirty Tier 0 class sets -> data/items/gear_sets.json   (idempotent)

    python3 tools/build_t0_sets.py [--dry-run]

Kyle's rulings, 12 Nov 2026, all of which this file is:

  * names approved ("The names are good for T0") - SETS below;
  * T0 is EIGHT pieces, and "the gear isnt all lvl 60 for T0. Look at how Classic wow does it.
    Lvl 52-58" - LEVELS below is Classic's dungeon set 1: bracers 52, belt 53, gloves and boots
    54, shoulders 55, legs 56, helm 57, chest 58;
  * one set per class with a VERSION per way the class gears, not per talent tree ("we dont
    need 3 sets for a necromancer as each set is dps"), counted separately, never mixed;
  * two home-brew versions: a Cryotherapist healer for the Mage ("homebrew DPS healer") and an
    Enhancement tank for the Shaman;
  * bonuses: "2 piece be stats like +30 (something appropriate). 4 Piece can be either +spell
    power, +Healing power, +attack power, or +ranged attack power (for hybrid classes like ret
    pally or primalist - we can do SP + AP). For 6 piece and 8 piece we can figure something
    out." So 6 and 8 are deliberately ABSENT here, not forgotten.
  * no home yet ("can you design the gear without giving it a home right away? We dont have all
    the dungeons yet") - nothing in this file says where a piece drops.

WHERE THE NUMBERS COME FROM. Each piece's primary-stat total and armour are what the loot
generator itself gives a rare of that slot, armour type and item level (the median of 40 rolls),
so a set piece is exactly as big as a good blue of its level - the set is worth wearing for its
bonuses, not because its pieces break the item budget. Only the SPLIT is authored, per version.
"""
import contextlib
import io
import json
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data" / "items" / "gear_sets.json"

SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet"]
#: required level per slot - Classic's dungeon set 1, moved up one level (see ILVL_ABOVE).
LEVELS = {"wrist": 53, "waist": 54, "hands": 55, "feet": 55, "shoulder": 56, "legs": 57, "head": 58, "chest": 59}
#: A set piece's item level sits this far above its required level. Kyle, 13 Nov 2026: "The T0
#: item set will be from lvl 53 to lvl 59 (So ilvl 56 to ilvl 62)" - one level later than the
#: first draft (52-58) and three above instead of the usual two, so a set piece is a notch better
#: than an ordinary blue of its level.
ILVL_ABOVE = 3

#: class -> (set name, the word(s) its pieces are named with)
SETS = {
    "Warrior": ("Gatebreaker's Battlegear", "Gatebreaker's"),
    "Paladin": ("Dawnwarden Plate", "Dawnwarden"),
    "Knight of Xoroth": ("Hellforged Warplate", "Hellforged"),
    "Guardian": ("Lastwall Bulwark", "Lastwall"),
    "Cultist": ("Hollow Saint's Harness", "Hollow Saint's"),
    "Starcaller": ("Nightglass Plate", "Nightglass"),
    "Sun Cleric": ("Noonfire Regalia", "Noonfire"),
    "Primalist": ("Wildhorn Warplate", "Wildhorn"),
    "Shaman": ("Rainspeaker's Harness", "Rainspeaker's"),
    "Hunter": ("Longstalk Mail", "Longstalk"),
    "Witch Hunter": ("Pyrewatch Mail", "Pyrewatch"),
    "Tinker": ("Sparkwright's Rig", "Sparkwright's"),
    "Venomancer": ("Fangsilk Mail", "Fangsilk"),
    "Reaper": ("Last Harvest Mail", "Last Harvest"),
    "Rogue": ("Lowlight Leathers", "Lowlight"),
    "Druid": ("Deeproot Raiment", "Deeproot"),
    "Barbarian": ("Ramhorn Warhide", "Ramhorn"),
    "Witch Doctor": ("Bonecharm Wraps", "Bonecharm"),
    "Felsworn": ("Felscar Hides", "Felscar"),
    "Templar": ("Penitent's Leathers", "Penitent's"),
    "Bloodmage": ("Bloodletter's Finery", "Bloodletter's"),
    "Ranger": ("Greenway Leathers", "Greenway"),
    "Priest": ("Vestments of the Quiet Hour", "Quiet Hour"),
    "Mage": ("Leyweaver's Regalia", "Leyweaver's"),
    "Warlock": ("Pactbinder's Raiment", "Pactbinder's"),
    "Necromancer": ("Gravewright's Shroud", "Gravewright's"),
    "Pyromancer": ("Cinderscale Robes", "Cinderscale"),
    "Runemaster": ("Glyphwoven Regalia", "Glyphwoven"),
    "Chronomancer": ("Vestments of the Stopped Clock", "Stopped Clock"),
    "Stormbringer": ("Thunderhead Raiment", "Thunderhead"),
}

#: A VERSION is a way of gearing. For each: how a piece's primary total is split, what its
#: secondaries are (points on a chest; smaller slots scale down), the 2- and 4-piece bonuses,
#: and the slot words that name its pieces - a different word per slot in every version, so two
#: versions of one set never share a piece name (Kyle's own example: Hauberk / Vestments).
PROFILES = {
    "melee_str": dict(split={"strength": 0.55, "stamina": 0.45}, sec={"attack_power": 10, "hit_rating": 1},
                      two={"strength": 30}, four={"attack_power": 40}, words="melee"),
    "melee_agi": dict(split={"agility": 0.55, "stamina": 0.45}, sec={"attack_power": 10, "hit_rating": 1},
                      two={"agility": 30}, four={"attack_power": 40}, words="melee"),
    "ranged_agi": dict(split={"agility": 0.6, "stamina": 0.4}, sec={"ranged_attack_power": 12, "hit_rating": 1},
                       two={"agility": 30}, four={"ranged_attack_power": 40}, words="ranged"),
    "tank_str": dict(split={"stamina": 0.6, "strength": 0.4}, sec={"defense_rating": 3, "dodge_rating": 2},
                     two={"stamina": 30}, four={"attack_power": 40}, words="tank"),
    "tank_agi": dict(split={"stamina": 0.6, "agility": 0.4}, sec={"defense_rating": 3, "dodge_rating": 2},
                     two={"stamina": 30}, four={"attack_power": 40}, words="tank"),
    "tank_hybrid": dict(split={"stamina": 0.5, "strength": 0.25, "intellect": 0.25},
                        sec={"defense_rating": 3, "spell_power": 8},
                        two={"stamina": 30}, four={"attack_power": 20, "spell_power": 14}, words="tank"),
    "caster": dict(split={"intellect": 0.5, "stamina": 0.35, "spirit": 0.15}, sec={"spell_power": 18},
                   two={"intellect": 30}, four={"spell_power": 25}, words="caster"),
    "healer": dict(split={"intellect": 0.4, "spirit": 0.3, "stamina": 0.3}, sec={"spell_power": 10, "healing_power": 9},
                   two={"spirit": 30}, four={"healing_power": 40}, words="healer"),
    "hybrid_str": dict(split={"strength": 0.35, "intellect": 0.3, "stamina": 0.35},
                       sec={"attack_power": 6, "spell_power": 9},
                       two={"strength": 15, "intellect": 15}, four={"attack_power": 20, "spell_power": 14}, words="hybrid"),
    "hybrid_agi": dict(split={"agility": 0.35, "intellect": 0.3, "stamina": 0.35},
                       sec={"attack_power": 6, "spell_power": 9},
                       two={"agility": 15, "intellect": 15}, four={"attack_power": 20, "spell_power": 14}, words="hybrid"),
    # HOME-BREW: a healer who heals by doing damage - spell power first, healing behind it.
    "cryomancer": dict(split={"intellect": 0.5, "stamina": 0.3, "spirit": 0.2},
                       sec={"spell_power": 14, "healing_power": 5},
                       two={"intellect": 30}, four={"spell_power": 14, "healing_power": 20}, words="frost"),
}

WORDS = {
    "melee": ["Helm", "Pauldrons", "Hauberk", "Bracers", "Gauntlets", "Girdle", "Legguards", "Greaves"],
    "ranged": ["Coif", "Spaulders", "Brigandine", "Wristguards", "Grips", "Belt", "Leggings", "Boots"],
    "tank": ["Greathelm", "Shoulderguards", "Chestguard", "Vambraces", "Handguards", "Waistguard", "Legplates", "Sabatons"],
    "caster": ["Circlet", "Mantle", "Vestments", "Bindings", "Gloves", "Sash", "Trousers", "Slippers"],
    "healer": ["Cowl", "Shoulderpads", "Robe", "Wraps", "Handwraps", "Cord", "Kilt", "Sandals"],
    "hybrid": ["Headguard", "Epaulets", "Harness", "Armguards", "Fists", "Clasp", "Tassets", "Treads"],
    "frost": ["Hood", "Shawl", "Raiment", "Cuffs", "Mitts", "Cincture", "Skirt", "Footwraps"],
}

#: Versions no talent tree asks for. class -> [(key, label, profile)]
HOMEBREW = {
    "Mage": [("cryotherapist", "Cryotherapist", "cryomancer")],   # Kyle, 13 Nov 2026: "Call them cryotherapist."
    "Shaman": [("enhancement_tank", "Enhancement Tank", "tank_agi")],
}


#: Specs whose recorded stat profile is not how Kyle wants the set to gear them.
#: "for hybrid classes like ret pally or primalist - we can do SP + AP".
OVERRIDES = {"paladin_retribution": "hybrid_str"}


def profile_for(spec, key=None):
    if key in OVERRIDES:
        return OVERRIDES[key]
    role, template = spec["role"], spec["stat_template"]
    if role == "healer":
        return "healer"
    if role == "tank":
        return {"str_physical": "tank_str", "agi_physical": "tank_agi"}.get(template, "tank_hybrid")
    if template == "int_caster" or template == "spi_healer":
        return "caster"
    if template == "str_int_hybrid":
        return "hybrid_str"
    if template == "agi_int_hybrid":
        return "hybrid_agi"
    if template == "str_physical":
        return "melee_str"
    return "ranged_agi" if role == "ranged_dps" else "melee_agi"


def split_whole(total, shares):
    """Whole numbers that sum to exactly `total`, in the given proportions; rounding loss goes
    to the first (main) stat - the same rule entities/item.py uses for generated gear."""
    out = {k: int(total * v) for k, v in shares.items()}
    first = next(iter(shares))
    out[first] += total - sum(out.values())
    return {k: v for k, v in out.items() if v > 0}


def budgets(gen, char_class):
    """{slot: (item_level, required_level, primary total, armour, armour type)}"""
    out = {}
    for slot in SLOTS:
        req = LEVELS[slot]
        prim, armor, kind = [], [], None
        for seed in range(40):
            random.seed(seed * 7919 + req)
            it = gen.generate_item_for_class(char_class, req + ILVL_ABOVE, slot=slot, rarity="rare")
            prim.append(sum(it.primary_stats.values()))
            armor.append(it.armor_value)
            kind = it.armor_type
        out[slot] = (req + ILVL_ABOVE, req, int(statistics.median(prim)), int(statistics.median(armor)), kind)
    return out


def build():
    with contextlib.redirect_stdout(io.StringIO()):
        from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    specs = json.loads((ROOT / "data/items/spec_gear.json").read_text())
    sets = {}
    for char_class, (set_name, word) in SETS.items():
        slug = char_class.lower().replace(" ", "_")
        mine = [(k, v) for k, v in specs.items() if v.get("class") == char_class]
        if not mine:
            raise SystemExit(f"no specs recorded for {char_class}")
        # one version per PROFILE, labelled with every tree that gears that way
        by_profile = {}
        for key, spec in mine:
            by_profile.setdefault(profile_for(spec, key), []).append(key[len(slug) + 1:].replace("_", " ").title())
        versions = [(prof.split("_")[0] if len([p for p in by_profile if p.split("_")[0] == prof.split("_")[0]]) == 1 else prof,
                     " / ".join(trees), prof) for prof, trees in by_profile.items()]
        versions += HOMEBREW.get(char_class, [])
        budget = budgets(gen, char_class)
        chest_total = budget["chest"][2]
        variants = {}
        for key, label, prof in versions:
            p = PROFILES[prof]
            pieces = {}
            for i, slot in enumerate(SLOTS):
                ilvl, req, total, armor, _kind = budget[slot]
                scale = total / chest_total
                pieces[slot] = {
                    "name": f"{word} {WORDS[p['words']][i]}",
                    "primary_stats": split_whole(total, p["split"]),
                    "secondary_stats": {k: max(1, int(round(v * scale))) for k, v in p["sec"].items()},
                }
            variants[key] = {"label": label, "profile": prof, "pieces": pieces,
                             "bonuses": {"2": {"stats": p["two"]}, "4": {"stats": p["four"]}}}
        sets[f"t0_{slug}"] = {
            "name": set_name, "class": char_class, "tier": "T0", "rarity": "rare",
            "armor_type": budget["chest"][4],
            "slots": {slot: {"item_level": budget[slot][0], "required_level": budget[slot][1],
                             "armor": budget[slot][3]} for slot in SLOTS},
            "variants": variants,
        }
    return sets


def main():
    sets = build()
    doc = {"_about": "Gear sets. BUILT by tools/build_t0_sets.py - edit that, not this. Shape: world/gear_sets.py. "
                     "T0: eight pieces, required levels 53-59 with item level three above, one version per way a "
                     "class gears, bonuses at 2 and 4 (6 and 8 not designed yet). Bracers, belts and legs "
                     "come from tokens dropped in Khaz Varun and the Emberdeep (data/items/set_tokens.json); "
                     "the other five slots have no drop source yet.",
           "sets": sets}
    text = json.dumps(doc, indent=1) + "\n"
    versions = sum(len(s["variants"]) for s in sets.values())
    print(f"{len(sets)} sets, {versions} versions, {versions * len(SLOTS)} pieces")
    for sid, s in sets.items():
        print(f"  {s['class']:17} {s['armor_type']:8} " + "; ".join(f"{v['label']} [{v['profile']}]" for v in s["variants"].values()))
    if "--dry-run" in sys.argv:
        return 0
    OUT.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
