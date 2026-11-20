#!/usr/bin/env python3
"""Rootwater Isle's creatures, rares, encounter tables, rare loot, gathering and fishing (42-44). Idempotent.

    PYTHONPATH=. python3 tools/build_rootwater_isle_content.py [--dry]

docs/worldtree_brief.md: the reef island where the World Tree's roots meet the sea. The tree is hungry (its sap makes
the beasts that drink it big and wrong, and its bark has started to rot); the Bloodsail tap the roots for sap; the
Bloodscalp come up the roots after the trolls who climbed it. Sprites are Kyle's sheet W6 (the wt_* sprites,
docs/worldtree_art_prompts.md).

    The Root Lagoons       sap-drunk crocolisks, rootbound murlocs, reef crabs          rare: The Rootmaw
    Sapwash Beach          the Bloodsail's sap camp                                     rare: Tapmaster Grell
    The Bloodscalp Climb   the Bloodscalp war camp up the north-west root               rare: Zul'gash the Climber
    The Saproot Thicket    the rot on the north-east root                               rare: The Rot-Mother
    Rootwater Landing      the trolls' landing                                          safe

THE NUMBERS follow the open world in the 40s, like Feralas: trash basic 4L - 10, a rare's 10L - 200 at boss
multiplier 2.2. Rares sit in subzone tables at weight 0, one item from four, item level = the rare's level + 3.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402

LOOT = ROOT / "data/loot/rootwater_isle_rare_loot.json"
RW = "Rootwater Isle"
MAP_MODULE = "handbuilt_worldtree_rootwater_isle"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- wanderers, the whole island
    "Bark Lizard":            ("beast_fast", 42, 43, None, "wt_bark_lizard", "beast", "physical",
                               ["Bite", "Scuttle Strike", "Infected Bite"]),
    "Leafwing Moth":          ("beast_fast", 42, 43, None, "wt_leafwing_moth", "caster", "nature",
                               ["Wing Dust", "Dusting Flutter", "Itching Scales"]),
    # ---------------------------------------------------------------- the Root Lagoons
    "Sap-Drunk Crocolisk":    ("beast_large", 42, 44, None, "wt_sap_crocolisk", "bruiser", "physical",
                               ["Snap", "Death Roll", "Sap-Slicked"]),
    "Rootbound Murloc":       ("humanoid_warrior", 42, 43, None, "wt_root_murloc", "warrior", "physical",
                               ["Tangled Spear", "Gurgling Rush", "Root-Grown Hide"]),
    "Reef Shellcrusher":      ("beast_basic", 42, 43, None, "wt_reef_crab", "warrior", "physical",
                               ["Pinch", "Crushing Claw", "Rootbound Shell"]),
    "The Rootmaw":            ("beast_large", 44, 44, 2.2, "wt_rare_rootmaw", "rare", "physical",
                               ["Barnacled Jaws", "Lagoon Roll", "Dragged Down", "Three Years Drinking"]),
    # ---------------------------------------------------------------- Sapwash Beach: the Bloodsail
    "Bloodsail Sap-Tapper":   ("humanoid_warrior", 42, 43, None, "wt_sap_tapper", "warrior", "physical",
                               ["Tapping Mallet", "Bucket to the Head", "Sticky With Sap"]),
    "Bloodsail Cutthroat":    ("humanoid_rogue", 43, 44, None, "wt_cutthroat", "beast", "physical",
                               ["Cutlass", "Dirty Slash", "Bleeding Cut"]),
    "Bloodsail Powder Monkey": ("beast_fast", 42, 43, None, "wt_powder_monkey", "caster", "fire",
                                ["Lit Fuse", "Black Powder Toss", "Singed"]),
    "Tapmaster Grell":        ("humanoid_warrior", 44, 44, 2.2, "wt_sap_tapper", "rare", "physical",
                               ["Iron Tap", "Sap Barrel Rolled", "Hammered Into the Root", "Grell's Cut"]),
    # ---------------------------------------------------------------- the Bloodscalp Climb
    "Bloodscalp Headhunter":  ("humanoid_ranged", 42, 43, None, "wt_bloodscalp_headhunter", "beast", "physical",
                               ["Spear Throw", "Headhunter's Mark", "Barbed Spear"]),
    "Bloodscalp Shaman":      ("humanoid_caster", 42, 43, None, "wt_bloodscalp_shaman", "caster", "nature",
                               ["Lightning Bolt", "Chain Lightning", "Skull Hex"]),
    "Bloodscalp Axe-Thrower": ("humanoid_ranged", 43, 44, None, "wt_bloodscalp_axe_thrower", "beast", "physical",
                               ["Thrown Axe", "Twin Axes", "Deep Gash"]),
    "Bloodscalp Berserker":   ("humanoid_warrior", 43, 44, None, "wt_bloodscalp_berserker", "bruiser", "physical",
                               ["Two-Axe Chop", "Frenzied Swing", "Hamstrung"]),
    "Bloodscalp War-Climber": ("humanoid_rogue", 42, 43, None, "wt_bloodscalp_climber", "warrior", "physical",
                               ["Climbing Hook", "Drop From Above", "Bark-Scaled"]),
    "Bloodscalp Witch Doctor": ("humanoid_caster", 43, 44, None, "wt_bloodscalp_witch_doctor", "caster", "shadow",
                                ["Shadow Hex", "Censer Smoke", "Witch Doctor's Curse"]),
    "Zul'gash the Climber":   ("humanoid_warrior", 44, 44, 2.2, "wt_bloodscalp_berserker", "rare", "physical",
                               ["Red Axes", "Up the Root", "Thrown Off the Root", "The Bloodscalp Way"]),
    # ---------------------------------------------------------------- the Saproot Thicket: the rot
    "Rot Crawler":            ("vermin_swarm", 42, 43, None, "wt_rot_crawler", "warrior", "nature",
                               ["Gnaw", "Burst of Rot", "Rot-Soft Hide"]),
    "Bark-Borer Beetle":      ("vermin_swarm", 42, 43, None, "wt_bark_borer", "warrior", "physical",
                               ["Drill Bite", "Bore", "Chitin Plates"]),
    "Goldensap Ooze":         ("elemental_bruiser", 43, 44, None, "wt_sap_ooze", "bruiser", "nature",
                               ["Engulf", "Sap Splash", "Mired"]),
    "Rot-Spore Swarm":        ("elemental_caster", 43, 44, None, "wt_spore_swarm", "caster", "nature",
                               ["Spore Burst", "Choking Cloud", "Rotting Spores"]),
    "The Rot-Mother":         ("elemental_bruiser", 44, 44, 2.2, "wt_rare_rot_mother", "rare", "nature",
                               ["Rotten Bough", "Black Blossom Burst", "Taken Root", "Mother of the Rot"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}


def sprite(name):
    return ROSTER[name][4]


RULES_START = "    # ROOTWATER ISLE (generated by tools/build_rootwater_isle_content.py; do not edit by hand)\n"
RULES_END = "    # END ROOTWATER ISLE\n"


def write_sprite_rules():
    import re
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ROSTER) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # FERALAS'S OPEN WORLD (generated by tools/build_feralas_openworld.py; do not edit by hand)\n"
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def kit(name):
    template, lo, hi, mult, _s, shape, school, names = ROSTER[name]
    t = T(hi)
    s = school
    dispel = {"nature": "poison", "shadow": "curse"}.get(s, "magic")
    if shape == "beast":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                dot(names[2], int(t * 0.27), 3, 3, school=s, **({"dispel_type": dispel} if s != "physical" else {}))]
    if shape == "warrior":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.86), cooldown=3, school=s),
                buff(names[2], 6, 3, {"armor": 180})]
    if shape == "caster":
        return [dmg(names[0], t, school=s), dmg(names[1], int(t * 0.84), cooldown=5, school=s, is_aoe=True),
                dot(names[2], int(t * 0.27), 3, 3, school=s, dispel_type=dispel)]
    if shape == "bruiser":
        return [dmg(names[0], t + 8, school=s), dmg(names[1], int(t * 0.84), cooldown=4, school=s, is_aoe=True),
                debuff(names[2], 5, 2, {"dodge_rating": -20}, school=s)]
    # a rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    b = B(hi)
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Bark Lizard": 4, "Leafwing Moth": 3, "Sap-Drunk Crocolisk": 2},
    "subzones": {
        "The Root Lagoons": {"Sap-Drunk Crocolisk": 5, "Rootbound Murloc": 5, "Reef Shellcrusher": 4,
                             "Leafwing Moth": 1, "The Rootmaw": 0},
        "Sapwash Beach": {"Bloodsail Sap-Tapper": 5, "Bloodsail Cutthroat": 5, "Bloodsail Powder Monkey": 4,
                          "Tapmaster Grell": 0},
        "The Bloodscalp Climb": {"Bloodscalp Headhunter": 5, "Bloodscalp Shaman": 4, "Bloodscalp Axe-Thrower": 4,
                                 "Bloodscalp Berserker": 3, "Bloodscalp War-Climber": 4, "Bloodscalp Witch Doctor": 3,
                                 "Zul'gash the Climber": 0},
        "The Saproot Thicket": {"Rot Crawler": 5, "Bark-Borer Beetle": 5, "Goldensap Ooze": 4, "Rot-Spore Swarm": 3,
                                "The Rot-Mother": 0},
        "Rootwater Landing": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "The Rootmaw": [
        ("Rootmaw Hide Jerkin", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Barnacle-Crusted Pauldrons", "shoulder", "of the Bear", ("a", "plate"), "str_physical"),
        ("Lagoon-Drowned Sash", "waist", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Rootmaw's Tooth", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical")],
    "Tapmaster Grell": [
        ("Grell's Iron Tap", "main_hand", "of the Bear", ("w", "mace_1h"), "str_physical"),
        ("Sap-Stained Gauntlets", "hands", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Bloodsail Captain's Coat", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Tapmaster's Spyglass", "trinket", "of the Hunt", None, "agi_physical")],
    "Zul'gash the Climber": [
        ("Zul'gash's Red Axe", "two_hand", "of the Champion", ("w", "axe_2h"), "str_physical"),
        ("Climber's Hooked Bracers", "wrist", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Bloodscalp Scalp-Belt", "waist", "of the Bear", ("a", "mail"), "str_physical"),
        ("Witch-Doctor's Skull Staff", "two_hand", "of the Invoker", ("w", "staff"), "int_caster")],
    "The Rot-Mother": [
        ("Black Blossom Circlet", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Rot-Mother's Heartwood", "off_hand", "of the Owl", ("w", "tome"), "spi_healer"),
        ("Saproot Greaves", "legs", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Rootbark Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid")],
}

#: gathering at 42-44 on a jungle reef: the 40s herbs (Khadgar's Whisker, Goldthorn, Fadeleaf, Purple Lotus, a little
#: Sungrass), mithril, and the jungle's woods. Fishing: the warm reef's fish.
NODES = {"rootwater_isle": {"slots": 26, "active_percent": 0.42, "table": {
    "herb_khadgar": 3, "herb_goldthorn": 3, "herb_fadeleaf": 3, "herb_purple_lotus": 2, "herb_sungrass": 1,
    "herb_liferoot": 2,
    "ore_mithril": 5, "ore_verdant_iron": 2,
    "wood_bloodroot_stump": 3, "wood_driftwood_stump": 2, "wood_thornveil_stump": 2},
    "fishing": {"slots": 8, "active_percent": 0.6, "table": {
        "fish_stonescale_eel": 3, "fish_spotted_yellowtail": 3, "fish_nightfin_snapper": 2, "fish_redgill": 2,
        "fish_greater_sagefish": 2}}}}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for rare, items in POOLS.items():
        ilvl = ROSTER[rare][2] + 3
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = "rwi_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[rare] = built
    return out, rows


def check():
    import importlib
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    bad = []
    mod = importlib.import_module(f"tools.{MAP_MODULE}")
    declared = {s[0] for s in mod.SUBZONES}
    if set(TABLE["subzones"]) != declared:
        bad.append(f"subzones disagree with the map: {sorted(set(TABLE['subzones']) ^ declared)}")
    named = set(TABLE["open_zone"])
    if RARES & named:
        bad.append("a rare is in the open-zone table")
    for s in TABLE["subzones"].values():
        named |= set(s or {})
    if named != set(ROSTER) or set(POOLS) != RARES:
        bad.append(f"tables, roster and pools differ: {sorted(named ^ set(ROSTER))} {sorted(set(POOLS) ^ RARES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name in ROSTER:
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
        # a name already used elsewhere is someone else's creature (Stonetalon's Sap Ooze, 30-31, nearly got
        # re-levelled to 44): only this builder's own earlier run may own it, at its own levels
        if prev and (prev.get("ability_kit") != kit_slug(name)
                     or list(prev.get("level_range") or [])[:2] != list(ROSTER[name][1:3])):
            bad.append(f"{name} is already a different creature in creatures.json")
    return bad


def main():
    write_sprite_rules()
    bad = check()
    loot, rows = build_loot()
    bad += loot_audit(rows)
    if "--dry" in sys.argv or bad:
        print("\n".join(bad) if bad else f"dry run clean: {len(ROSTER)} creatures, {len(RARES)} rares")
        return 1 if bad else 0
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): kit(n) for n in ROSTER}, "ability_kits.json")
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(json.loads(raw), raw)
    entry = enc["zones"].setdefault(RW, {})
    entry["name"] = RW
    entry["open_zone"] = {"name": RW, "creatures": dict(TABLE["open_zone"])}
    entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                             {"name": s, "creatures": dict(c)}) for s, c in TABLE["subzones"].items()}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nd["zones"].update(NODES)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Rootwater Isle's open-world rares (44). ONE item per kill from the rare's four; item_level = the "
                      "rare's level + 3. Hand-authored in tools/build_rootwater_isle_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(RARES)} rares); {len(rows)} rare items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
