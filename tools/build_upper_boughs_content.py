#!/usr/bin/env python3
"""The Upper Boughs' creatures, rares, encounter tables, loot, gathering and fishing (47-48), and the Stormsplit's (the
lightning split in the trunk off the ring). Idempotent.

    PYTHONPATH=. python3 tools/build_upper_boughs_content.py [--dry]

docs/worldtree_brief.md: "Thin air and wind: wind-bent branches, wyvern roosts, and the first wreckage falling out of the
clouds", "Storms and elementals; wyverns and harpies; something from above". The last of Kyle's sheet W6 is worn here
(wyverns, tempest harpies, gust elementals, storm wisps, thunderhawks, the crystal sentinel).

    The Trunk Ring          skinks and moths on the ledge round the trunk
    The Wyvern Roosts       the wyverns on the east branch                                  rare: Stormcrest
    The Storm Bough         wisps and gusts where the lightning struck                     rare: The Lightning-Eater
    The Gale                the harpies riding the wind on the west                        rare: Gale Queen Skirra
    The Thunderhawk Reach   the thunderhawks on the north branch                           rare: Old Thunderbeak
    The Skiff Wreck         what came down with the Fallen Skiff                           rare: The Skiff Warden
    Highrest                the last troll camp                                            safe
    The Stormsplit (cave)   the storm trapped in the trunk            bosses: The Caught Storm, Old Charwing

THE NUMBERS follow the tiers below: trash basic 4L - 10, a rare's 10L - 200 at multiplier 2.2, item level = the rare's
level + 3; a cave boss's 10L - 200 at 2.5 (the end) and 2.3, item level = boss level + 2.
"""
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_tempest_openworld import enrage, stun, shield  # noqa: E402
from tools.build_scarlet_monastery_content import opener, stun_hit, heal  # noqa: E402

RARE_LOOT = ROOT / "data/loot/upper_boughs_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/stormsplit_boss_loot.json"
LB = "The Upper Boughs"
CAVE = "The Stormsplit"
MAP_MODULE = "handbuilt_worldtree_upper_boughs"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare/boss multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- the Trunk Ring
    "Windscour Skink":        ("beast_fast", 47, 47, None, "wt_bark_lizard", "beast", "physical",
                               ["Bite", "Wind-Quick Snap", "Grit in the Eyes"]),
    "Gale Moth":              ("beast_fast", 47, 47, None, "wt_leafwing_moth", "caster", "nature",
                               ["Dust on the Wind", "Gust of Wings", "Itching Dust"]),
    # ---------------------------------------------------------------- the Wyvern Roosts
    "Cloudtop Wyvern":        ("beast_fast", 47, 48, None, "wt_wyvern", "beast", "nature",
                               ["Talons", "Diving Strike", "Wyvern Sting"]),
    "Stormcrest":             ("beast_fast", 48, 48, 2.2, "wt_wyvern", "rare", "nature",
                               ["Crest-Rake", "Out of the Cloud", "Pinned to the Bough", "Old Bull's Fury"]),
    # ---------------------------------------------------------------- the Storm Bough
    "Crackling Wisp":         ("elemental_caster", 47, 48, None, "wt_storm_wisp", "caster", "nature",
                               ["Spark", "Chain of Sparks", "Static"]),
    "Galebound Gust":         ("elemental_bruiser", 47, 48, None, "wt_gust_elemental", "bruiser", "physical",
                               ["Buffet", "Downdraft", "Knocked Off Balance"]),
    "The Lightning-Eater":    ("elemental_bruiser", 48, 48, 2.2, "wt_gust_elemental", "rare", "nature",
                               ["Swallowed Bolt", "Thunderclap", "Struck Still", "Full of the Storm"]),
    # ---------------------------------------------------------------- the Gale
    "Gale-Rider Harpy":       ("humanoid_rogue", 47, 48, None, "wt_tempest_harpy", "warrior", "physical",
                               ["Raking Talons", "Ride the Gust", "Wind-Hardened"]),
    "Gale Windcaller":        ("humanoid_caster", 47, 48, None, "wt_harpy_windcaller", "caster", "nature",
                               ["Cutting Wind", "Squall", "Wind-Sick"]),
    "Gale Queen Skirra":      ("humanoid_caster", 48, 48, 2.2, "wt_tempest_harpy", "rare", "nature",
                               ["Queen's Talons", "The Whole Gale", "Thrown on the Wind", "Queen of the Gale"]),
    # ---------------------------------------------------------------- the Thunderhawk Reach
    "Thunderhawk":            ("beast_fast", 47, 48, None, "wt_thunderhawk", "beast", "nature",
                               ["Beak", "Thunder Dive", "Crackling Wound"]),
    "Old Thunderbeak":        ("beast_fast", 48, 48, 2.2, "wt_thunderhawk", "rare", "nature",
                               ["Thunder Beak", "Storm Wings", "Struck From Above", "The Old Bird's Anger"]),
    # ---------------------------------------------------------------- the Skiff Wreck
    "Skiff Sentinel":         ("humanoid_warrior", 47, 48, None, "wt_crystal_sentinel", "warrior", "arcane",
                               ["Crystal Fist", "Shard Burst", "Crystal Ward"]),
    "Wreck Drone":            ("humanoid_warrior", 47, 48, None, "wt_gear_drone", "bruiser", "physical",
                               ["Clamp", "Spinning Blades", "Sparking"]),
    "The Skiff Warden":       ("humanoid_caster", 48, 48, 2.2, "wt_crystal_sentinel", "rare", "arcane",
                               ["Warden's Beam", "Crystal Pulse", "Held in Place", "The Ship Is Mine"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: the Stormsplit: trash rolled from the cave's own table, the two bosses pinned by the map (tools/handbuilt_stormsplit)
CAVE_ROSTER = {
    "Split Wisp":             ("elemental_caster", 47, 48, None, "wt_storm_wisp", "caster", "nature",
                               ["Arc", "Forked Arc", "Charged"]),
    "Trapped Gust":           ("elemental_bruiser", 47, 48, None, "wt_gust_elemental", "bruiser", "physical",
                               ["Slam", "Whirl", "Thrown Back"]),
    "Stormstruck Wyvern":     ("beast_fast", 47, 48, None, "wt_wyvern", "beast", "nature",
                               ["Scorched Talons", "Lunge", "Burning Sting"]),
    "Charred Borer":          ("vermin_swarm", 47, 48, None, "wt_bark_borer", "warrior", "physical",
                               ["Mandibles", "Chew Through", "Charred Shell"]),
    "Old Charwing":           ("beast_large", 48, 48, 2.3, "wt_wyvern_matriarch", "boss", "nature",
                               ["Charred Talons", "Venom Like Fire", "Pinned to the Nest", "Every Wyvern in the Split"]),
    "The Caught Storm":       ("elemental_caster", 48, 48, 2.5, "elemental_air_2", "boss", "nature",
                               ["Bolt", "Thunder in the Trunk", "Struck Down", "The Storm Breaks Loose"]),
}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
ALL = {**ROSTER, **CAVE_ROSTER}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE UPPER BOUGHS (generated by tools/build_upper_boughs_content.py; do not edit by hand)\n"
RULES_END = "    # END THE UPPER BOUGHS\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE MIDDLE BOUGHS (generated by tools/build_middle_boughs_content.py; do not edit by hand)\n"
        assert anchor in s
        s = s.replace(anchor, block + anchor, 1)
    path.write_text(s, encoding="utf-8")


def kit(name):
    template, lo, hi, mult, _s, shape, school, names = ALL[name]
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
    b = B(hi)
    if shape == "boss":
        # a cave boss: an opener, a hard hit, a party hit, a stun, something dangerous, a heal or a flood, last stand
        kit_ = [opener(names[0], b, s), dmg(names[1], int(b * 0.88), cooldown=4, school=s),
                dmg(f"{names[0]}, Twice", int(b * 1.3), cooldown=4, school=s),
                dmg(names[3], int(b * 0.7), cooldown=5, school=s, is_aoe=True),
                stun_hit(names[2], int(b * 1.1), 6, school=s) if s != "physical" else stun_hit(names[2], int(b * 1.1), 6),
                dot(f"{names[1]}, Deep", int(b * 0.45), 5, 4, school=s, dispel_type=dispel)]
        if name == "Old Charwing":
            kit_.append(heal("Fed on the Storm", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("Lightning Through the Trunk", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Windscour Skink": 4, "Gale Moth": 3},
    "subzones": {
        "The Trunk Ring": {"Windscour Skink": 5, "Gale Moth": 5},
        "The Wyvern Roosts": {"Cloudtop Wyvern": 6, "Gale Moth": 1, "Stormcrest": 0},
        "The Storm Bough": {"Crackling Wisp": 5, "Galebound Gust": 5, "The Lightning-Eater": 0},
        "The Gale": {"Gale-Rider Harpy": 6, "Gale Windcaller": 4, "Gale Queen Skirra": 0},
        "The Thunderhawk Reach": {"Thunderhawk": 6, "Windscour Skink": 1, "Old Thunderbeak": 0},
        "The Skiff Wreck": {"Skiff Sentinel": 5, "Wreck Drone": 5, "The Skiff Warden": 0},
        "Highrest": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Stormcrest": [
        ("Stormcrest Scale Mantle", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Crest-Bone Band", "ring", "of the Bear", None, "str_physical"),
        ("Cloudtop Rider's Gloves", "hands", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Wyvern-Sting Wand", "ranged", "of the Invoker", ("w", "wand"), "int_caster")],
    "The Lightning-Eater": [
        ("Bolt-Swallower's Robe", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Grounded Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Stormstruck Bracers", "wrist", "of the Prophet", ("a", "leather"), "spi_healer"),
        ("Thunderclap Maul", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical")],
    "Gale Queen Skirra": [
        ("Gale Queen's Plume", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Windrider's Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Queen's Talon", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical"),
        ("Squall-Chain Belt", "waist", "of the Gorilla", ("a", "mail"), "str_int_hybrid")],
    "Old Thunderbeak": [
        ("Thunderbeak Cloak", "back", "of the Wolf", None, "agi_physical"),
        ("Storm-Feather Shoulderpads", "shoulder", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Hawk-Eye Longbow", "ranged", "of the Monkey", ("w", "bow"), "agi_physical"),
        ("Thunder-Hide Boots", "feet", "of the Bear", ("a", "plate"), "str_physical")],
    "The Skiff Warden": [
        ("Warden's Crystal Focus", "off_hand", "of the Invoker", ("w", "tome"), "int_caster"),
        ("Skiff-Plate Breastplate", "chest", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Brass-Bound Helm", "head", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Crystal-Lens Ring", "ring", "of the Prophet", None, "spi_healer")],
}
CAVE_POOLS = {
    "Old Charwing": [
        ("Charwing's Scorched Hide", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Nest-Burned Gauntlets", "hands", "of the Bear", ("a", "plate"), "str_physical"),
        ("Sting of the Old Mother", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical"),
        ("Ash-Feather Mantle", "shoulder", "of the Prophet", ("a", "cloth"), "spi_healer")],
    "The Caught Storm": [
        ("Heart of the Caught Storm", "two_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Thunder Hall Hauberk", "chest", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Lightning-Split Legplates", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Static-Charged Leggings", "legs", "of the Wolf", ("a", "leather"), "agi_int_hybrid")],
}

#: gathering at 47-48 at the top of the tree: the high 40s herbs on the bark, truesilver and mithril in what the storms
#: tore loose, and wood off the wind-bent branches. Fishing: rain caught in the forks (tools/build_fishing.window).
NODES = {"upper_boughs": {"slots": 24, "active_percent": 0.42, "table": {
    "herb_sungrass": 3, "herb_purple_lotus": 3, "herb_firebloom": 2, "herb_khadgar": 2,
    "ore_mithril": 3, "ore_truesilver": 2,
    "wood_thornveil_stump": 5}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(47, 48)
    fits = sorted([(fid, sk) for fid, _n, sk, _i, _d in FISH if s_lo <= sk <= s_hi], key=lambda f: -f[1])[:4]
    return {"slots": 6, "active_percent": 0.6, "table": {fid: 3 if n else 2 for n, (fid, _s) in enumerate(fits)}}


def build_loot(pools, roster, lift, prefix):
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows = {}, []
    for who, items in pools.items():
        ilvl = roster[who][2] + lift
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
            d["item_id"] = prefix + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[who] = built
    return out, rows


def check(loot):
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
    from tools import handbuilt_stormsplit as KH
    KH.build_stormsplit_baked()
    if set(KH.BOSSES) != CAVE_BOSSES or set(CAVE_POOLS) != CAVE_BOSSES:
        bad.append(f"the cave's bosses differ: map {sorted(KH.BOSSES)}, roster {sorted(CAVE_BOSSES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ALL.items():
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
        # a name already used elsewhere is someone else's creature: only this builder's own earlier run may own it
        if prev and (prev.get("ability_kit") != kit_slug(name) or list(prev.get("level_range") or [])[:2] != list(r[1:3])):
            bad.append(f"{name} is already a different creature in creatures.json")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ALL.items():
        if CS.sprite_for(name, r[0]) != sprite(name):
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {sprite(name)}")
    return bad


def main():
    write_sprite_rules()
    import importlib
    import creature_sprites
    importlib.reload(creature_sprites)
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "ubi_")
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ROSTER, 2, "ssi_")
    bad = check({**rare_loot, **cave_loot}) + loot_audit(rows + crows)
    if "--dry" in sys.argv or bad:
        print("\n".join(bad) if bad else f"dry run clean: {len(ALL)} creatures, {len(RARES)} rares, "
                                         f"{len(CAVE_BOSSES)} cave bosses")
        return 1 if bad else 0
    creatures = {}
    for name, (template, lo, hi, mult, *_rest) in ALL.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): kit(n) for n in ALL}, "ability_kits.json")
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(json.loads(raw), raw)
    entry = enc["zones"].setdefault(LB, {})
    entry["name"] = LB
    entry["open_zone"] = {"name": LB, "creatures": dict(TABLE["open_zone"])}
    entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                             {"name": s, "creatures": dict(c)}) for s, c in TABLE["subzones"].items()}
    entry.setdefault("caves", {})[CAVE] = {"name": CAVE, "creatures": {n: (0 if r[3] else 4)
                                                                         for n, r in CAVE_ROSTER.items()}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["upper_boughs"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Upper Boughs' open-world rares (48). ONE item per kill from the rare's four; item_level = "
                      "the rare's level + 3. Hand-authored in tools/build_upper_boughs_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for the Stormsplit (the World Tree's trunk, 47-48). ONE item per kill from the boss's "
                      "four; item_level = boss level + 2. Hand-authored in tools/build_upper_boughs_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares), {len(CAVE_ROSTER)} in the cave "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
