#!/usr/bin/env python3
"""Creatures, ability kits, encounter table and boss loot for Rocky Pass. Idempotent.

    PYTHONPATH=. python3 tools/build_rocky_pass_content.py

Same contract as tools/build_return_voyage_content.py and the same helpers: the roster is READ
FROM THE ZONE MODULE rather than retyped, so a name that does not match fails here instead of the
game raising on zone entry.

QUILBOAR AND HARPIES, DELIBERATELY LOPSIDED AWAY FROM WILDLIFE. The zone's other cave, The Weeping
Ice at 29-31, is all beasts - bears and yetis. A second all-beast pocket on the same mountain would
make the range feel like one habitat with two doors. So this is a FIGHT between two factions that
the player walks into the middle of: quilboar who climbed highest when the mountain pushed them out
of the Barrens and took the only defensible ground up here, and the harpies they drove off it, who
are now nesting in aspen crowns down in the Gold Stands - which the zone's own doc flags as "not
where harpies nest" and never explains. This is the explanation. One beast in the roster, at the
lowest weight, so the mountain is not empty of animals.

Damage is calibrated against what is already at this level: 34-35 trash sits at 48-80 and bosses
at 80-150, so trash here lands at 62-86 and bosses at 96-140.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, BOSS_MULT, kit_slug, merge_json, _detect_format,
    dmg, dot, debuff, buff, loot_audit,
)

LOOT = ROOT / "data/loot/rocky_pass_boss_loot.json"

ROSTER = {
    "Pass-Climber Quilboar": ("humanoid_warrior", 33, 35, False),
    "Thornweald Geomancer":  ("humanoid_caster",  33, 35, False),
    "Ridge-Wind Harpy":      ("humanoid_rogue",   34, 36, False),
    "Snowcrest Windcaller":  ("humanoid_caster",  34, 36, False),
    "Cliff-Backed Ram":      ("beast_basic",      33, 35, False),
    "Thornmother Vekka":     ("humanoid_caster",  34, 34, True),
    "Hagra Stormcrown":      ("humanoid_caster",  35, 35, True),
    "Gorrek Passkeeper":     ("humanoid_warrior", 36, 36, True),
    "The Windsnapped":       ("humanoid_rogue",   35, 35, True),
}

KITSETS = {
    "Pass-Climber Quilboar": [
        dmg("Frozen Tusk", 74),
        dmg("Drive Uphill", 62, cooldown=3),
        debuff("Gore", 4, 3, {"defense_rating": -22}),
    ],
    "Thornweald Geomancer": [
        dmg("Splintering Stone", 70, school="nature"),
        dmg("Rockfall", 84, cooldown=4, school="nature"),
        dot("Thorn in the Boot", 22, 3, 3, school="nature"),
    ],
    "Ridge-Wind Harpy": [
        dmg("Talon Rake", 78),
        dmg("Stoop", 86, cooldown=4),
        debuff("Buffeting Wings", 4, 2, {"hit_rating": -20}),
    ],
    "Snowcrest Windcaller": [
        dmg("Ice Shard", 72, school="frost"),
        dmg("Scouring Gust", 64, cooldown=5, school="frost", is_aoe=True),
        debuff("Numbed", 4, 3, {"agility": -24}),
    ],
    "Cliff-Backed Ram": [
        dmg("Headlong Charge", 86),
        dmg("Hoof and Horn", 68, cooldown=3),
    ],
    # ---- the three main bosses and the rare
    "Thornmother Vekka": [
        dmg("Thornmother's Rite", 104, school="nature", boss_rework=1),
        dmg("Raise the Briar", 88, cooldown=3, school="nature"),
        dmg("The Shelf Answers", 82, cooldown=5, school="nature", is_aoe=True),
        dot("Rooted Through", 28, 4, 3, school="nature"),
        buff("Blood of the Mountain", 8, 4, {"defense_rating": 30}),
    ],
    "Hagra Stormcrown": [
        dmg("Stormcrown's Talons", 112, boss_rework=1),
        dmg("Drop From the Crag", 96, cooldown=3),
        dmg("Everything On The Wind", 88, cooldown=5, school="frost", is_aoe=True),
        debuff("Thrown Off the Ledge", 5, 2, {"dodge_rating": -26, "agility": -28}),
    ],
    "Gorrek Passkeeper": [
        dmg("Passkeeper's Cleaver", 128, boss_rework=1),
        dmg("Nobody Crosses", 110, cooldown=3),
        dmg("Sweep the Ledge", 98, cooldown=5, is_aoe=True),
        dot("Opened to the Cold", 34, 4, 3),
        buff("Hold the Summit", 99, 30, {"attack_power": 40}),
    ],
    # The rare. Hits harder than its level and has less to hit you with - a thing that has been up
    # here too long on its own, rather than a fourth officer.
    "The Windsnapped": [
        dmg("Windsnapped Talons", 140, boss_rework=1),
        dmg("Nothing Left To Lose", 118, cooldown=4),
        dot("Frostbitten Wounds", 36, 3, 3, school="frost"),
    ],
}

TABLE = {
    # Weighted toward quilboar, because they hold the ground; harpies second; one beast at 1, so
    # the mountain has something living on it that is not in the fight.
    "Pass-Climber Quilboar": 7,
    "Thornweald Geomancer": 5,
    "Ridge-Wind Harpy": 5,
    "Snowcrest Windcaller": 4,
    "Cliff-Backed Ram": 1,
    "Thornmother Vekka": 0,
    "Hagra Stormcrown": 0,
    "Gorrek Passkeeper": 0,
    "The Windsnapped": 0,
}

POOLS = {
    "Thornmother Vekka": (36, [
        ("Thornmother's Briar Staff", "main_hand", "weapon", "staff", "int_caster"),
        ("Shelf-Holder's Girdle", "waist", "armor", "mail", "str_physical"),
        ("Frozen Tusk Pendant", "back", "armor", "leather", "agi_physical"),
        ("Geomancer's Split Mitts", "hands", "armor", "cloth", "spi_healer"),
    ]),
    "Hagra Stormcrown": (37, [
        ("Stormcrown's Talon", "main_hand", "weapon", "dagger", "agi_physical"),
        ("Matriarch's Feathered Mantle", "shoulder", "armor", "leather", "agi_int_hybrid"),
        ("Updraft Boots", "feet", "armor", "mail", "agi_physical"),
        ("Roostwarden's Wrap", "chest", "armor", "cloth", "int_caster"),
    ]),
    "Gorrek Passkeeper": (38, [
        ("Passkeeper's Cleaver", "main_hand", "weapon", "axe_2h", "str_physical"),
        ("Summit-Holder's Breastplate", "chest", "armor", "plate", "str_physical"),
        ("Cornice-Watcher's Helm", "head", "armor", "plate", "str_int_hybrid"),
        ("Windward Buckler", "off_hand", "weapon", "shield", "str_physical"),
    ]),
    "The Windsnapped": (37, [
        ("The Windsnapped's Spur", "main_hand", "weapon", "fist_weapon", "agi_physical"),
        ("Hollow-Boned Leggings", "legs", "armor", "leather", "agi_physical"),
        ("Thin-Air Bracers", "wrist", "armor", "mail", "agi_int_hybrid"),
        ("Last Nest Shroud", "back", "armor", "cloth", "spi_healer"),
    ]),
}


def main():
    import tools.handbuilt_rocky_pass as RP

    declared = set(RP.TRASH) | set(RP.BOSSES)
    unknown = declared - set(ROSTER)
    unused = set(ROSTER) - declared
    if unknown or unused:
        print("FAILED: the zone module and this file disagree about the roster")
        for n in sorted(unknown):
            print(f"  - the zone places '{n}', which nothing defines")
        for n in sorted(unused):
            print(f"  - this file defines '{n}', which no zone places")
        return 1
    print(f"roster agrees: {len(declared)} creatures")

    creatures = {}
    for name, (template, lo, hi, is_boss) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": is_boss,
             "ability_kit": kit_slug(name)}
        if is_boss:
            e["boss_multiplier"] = BOSS_MULT
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): k for n, k in KITSETS.items()}, "ability_kits.json")

    enc_raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(enc_raw)
    indent, newline = _detect_format(enc, enc_raw)
    caves = enc.setdefault("zones", {}).setdefault("The Aspen Wilderness", {}).setdefault("caves", {})
    caves["Rocky Pass"] = {"creatures": dict(TABLE)}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    print("  encounters.json: Rocky Pass under 'The Aspen Wilderness'")

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    out = {"_notes": ("Rocky Pass boss pools. Identity hand-authored in "
                      "tools/build_rocky_pass_content.py; stats from LootGenerator at rare "
                      "budget, so they sit on the same curves as the rest of the game's loot.")}
    rows = []
    for boss, (ilvl, items) in POOLS.items():
        built = []
        for (name, slot, kind, atype, template) in items:
            if kind == "armor":
                it = gen.generate_armor_piece(slot, atype, template, ilvl, "rare")
            else:
                it = gen.generate_weapon(slot, atype, template, ilvl, "rare", strict=True)
            if it is None:
                print(f"FAILED: the generator would not build {name}")
                return 1
            d = it.to_dict() if hasattr(it, "to_dict") else {}
            d["name"] = name
            d["item_id"] = "rp_" + name.lower().replace("'", "").replace(" ", "_")
            built.append(d)
            rows.append((name, slot, kind, atype, template))
        out[boss] = built
    problems = loot_audit(rows)
    if problems:
        print("\nFAILED - fix the pools, not the check:")
        for pr in problems:
            print(f"  - {pr}")
        return 1
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  {LOOT.relative_to(ROOT)}: {len(POOLS)} pools, {len(rows)} items")
    return 0


if __name__ == "__main__":
    sys.exit(main())
