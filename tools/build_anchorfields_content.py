#!/usr/bin/env python3
"""The Anchorfields' creatures, rares, encounter tables, loot, gathering and fishing (51-54), and the Keel's (its cave).
Idempotent.

    PYTHONPATH=. python3 tools/build_anchorfields_content.py [--dry]

docs/worldtree_brief.md: "The engines wake wrong (constructs, arcane overload, gravity gone strange); the Ascendancy
seizing the anchors; the sky's own storms". Ancient, not new: the constructs are House Vaelith's and the wardens' own,
built centuries ago and running wrong now; the island that fell is the Dropfield, and things have nested in it since.

    open shards             hares and lantern puffballs between the places
    The Estates             the house's own sentinels and garden drones, gone wild         rare: The Gardener
    The First Anchor        chain-wind elementals and anchorlight wisps                    rare: Starfall, the Burning Shard
    The Gearwork            overloaded constructs, scrap-walkers, overflow                 rare: Engine Seven
    The Seized Anchor       the Ascendancy's wardens, weavers, bombers and engineers       rare: Anchor-Marshal Corvan Sael
    The Slipping Anchor     slipstone, keelcrack crawlers and void-touched wisps           rare: The Unmoored
    The Dropfield           stalkers, rubble and carrion hawks on the fallen island        rare: Old Ballast
    The Listing Isle        goats and moths on the tilt                                    rare: Old Hornback
    Keelstone, Tiltside, the Observatory, the Aqueduct Arm: safe
    The Keel (cave)         the ballast golems, keel crystal, crawlers, the hollowed wardens   bosses: The Keel-Heart,
                            Warden-Captain Oris Hale

THE NUMBERS follow the tiers (tools/build_sunward_crown_content.py): trash basic 4L - 10, a rare's 10L - 200 at
multiplier 2.2, item level = the rare's level + 3; a cave boss's at 2.5 and 2.3, item level = boss level + 2.
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

RARE_LOOT = ROOT / "data/loot/anchorfields_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/keel_boss_loot.json"
CAVE = "The Keel"
ZONE = "The Anchorfields"
MAP_MODULE = "handbuilt_worldtree_anchorfields"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- the open shards
    "Shelfrunner Hare":       ("beast_fast", 51, 52, None, "sk_sky_hare", "beast", "physical",
                               ["Kick", "Bolt Away", "Scratched"]),
    "Lantern Puffball":       ("elemental_caster", 51, 52, None, "sk_puffball", "caster", "arcane",
                               ["Pop", "Spore Burst", "Glowing Spores"]),
    # ---------------------------------------------------------------- the Estates
    "Estate Sentinel":        ("humanoid_warrior", 51, 52, None, "ae_sentinel", "warrior", "arcane",
                               ["Halberd", "Trespasser's Strike", "Warded"]),
    "Garden Repair-Drone":    ("elemental_caster", 51, 52, None, "ae_repair_drone", "caster", "arcane",
                               ["Cutting Beam", "Pruning Sweep", "Sap-Burn"]),
    "Orchard Fowl":           ("beast_fast", 51, 52, None, "sk_meadow_fowl", "beast", "physical",
                               ["Peck", "Wing Flurry", "Pecked"]),
    "The Gardener":           ("elemental_bruiser", 52, 52, 2.2, "ae_crystal_golem", "rare", "arcane",
                               ["Gardener's Shears", "Tend the Grounds", "Planted", "Old Orders"]),
    # ---------------------------------------------------------------- the First Anchor
    "Chain-Wind Elemental":   ("elemental_caster", 52, 53, None, "sk_cloud_elemental", "caster", "nature",
                               ["Gust", "Chain-Wind", "Wind-Scoured"]),
    "Anchorlight Wisp":       ("elemental_caster", 52, 53, None, "sk_gold_wisp", "caster", "holy",
                               ["Flicker", "Anchorlight", "Searing Glow"]),
    "Starfall, the Burning Shard": ("elemental_caster", 53, 53, 2.2, "sk_falling_star", "rare", "fire",
                                    ["Burning Shard", "Starfall", "Struck Down", "Burning Up"]),
    # ---------------------------------------------------------------- the Gearwork
    "Overloaded Construct":   ("humanoid_warrior", 52, 53, None, "ae_storm_construct", "bruiser", "nature",
                               ["Discharge Fist", "Overload", "Shocked"]),
    "Scrap-Walker":           ("humanoid_warrior", 52, 53, None, "ae_broken_construct", "warrior", "physical",
                               ["Scrap Blade", "Grinding Advance", "Plated"]),
    "Overflow Elemental":     ("elemental_caster", 52, 53, None, "sk_storm_elemental", "caster", "arcane",
                               ["Arcane Spill", "Overflow", "Arcane Burn"]),
    "Engine Seven":           ("elemental_bruiser", 53, 53, 2.2, "ae_siege_walker", "rare", "physical",
                               ["Piston Strike", "Full Throttle", "Pinned in the Gears", "Overheat"]),
    # ---------------------------------------------------------------- the Seized Anchor
    "Ascendancy Warden":      ("humanoid_warrior", 53, 54, None, "ae_warden", "warrior", "arcane",
                               ["Warden's Blade", "Hold the Line", "Shielded"]),
    "Ascendancy Crystal-Weaver": ("humanoid_caster", 53, 54, None, "ae_crystal_weaver", "caster", "arcane",
                                  ["Crystal Lance", "Weave", "Crystal Splinters"]),
    "Ascendancy Bomber Construct": ("humanoid_warrior", 53, 54, None, "ae_bomber_construct", "bruiser", "fire",
                                    ["Bomb", "Carpet Bombing", "Burning"]),
    "Ascendancy Engineer":    ("humanoid_caster", 53, 54, None, "ae_engineer", "caster", "fire",
                               ["Spanner", "Rigged Charge", "Scorched"]),
    "Anchor-Marshal Corvan Sael": ("humanoid_caster", 54, 54, 2.2, "ae_magister", "rare", "arcane",
                                   ["Marshal's Edict", "Seize the Anchor", "Held in Place", "Ascendant Will"]),
    # ---------------------------------------------------------------- the Slipping Anchor
    "Slipstone Elemental":    ("elemental_bruiser", 53, 54, None, "kh_mineral_elemental", "bruiser", "physical",
                               ["Stone Fist", "Slip", "Bruised"]),
    "Keelcrack Crawler":      ("beast_fast", 53, 54, None, "sk_rift_crawler", "beast", "shadow",
                               ["Rending Claws", "Out of the Crack", "Rift-Sick"]),
    "Void-Touched Wisp":      ("elemental_caster", 53, 54, None, "sk_void_touched", "caster", "shadow",
                               ["Void Bolt", "Unmooring", "Hollowed"]),
    "The Unmoored":           ("elemental_caster", 54, 54, 2.2, "sk_hollow_storm", "rare", "shadow",
                               ["Unmoored Grasp", "Gravity Fails", "Lifted Away", "Nothing to Hold"]),
    # ---------------------------------------------------------------- the Dropfield
    "Dropfield Stalker":      ("beast_fast", 52, 53, None, "sk_cloud_stalker", "beast", "physical",
                               ["Bite", "Pounce", "Torn"]),
    "Wreck-Rubble Elemental": ("elemental_bruiser", 52, 53, None, "kh_mineral_elemental", "bruiser", "physical",
                               ["Rubble Fist", "Collapse", "Grit"]),
    "Carrion Gale Hawk":      ("beast_fast", 52, 53, None, "sk_gale_hawk", "beast", "nature",
                               ["Talons", "Stoop", "Wind-Torn"]),
    "Old Ballast":            ("elemental_bruiser", 53, 53, 2.2, "kh_stonewarden", "rare", "physical",
                               ["Ballast Fist", "The Weight of It", "Crushed Flat", "Dead Weight"]),
    # ---------------------------------------------------------------- the Listing Isle
    "Tiltside Goat":          ("beast_fast", 53, 53, None, "sk_sky_goat", "beast", "physical",
                               ["Butt", "Headlong", "Bruised"]),
    "Cliffside Moth":         ("beast_fast", 53, 53, None, "sk_sky_moth", "beast", "nature",
                               ["Dust", "Wing Gust", "Choking Dust"]),
    "Old Hornback":           ("beast_large", 53, 53, 2.2, "sk_sky_goat", "rare", "physical",
                               ["Old Horns", "The Long Charge", "Knocked Flat", "Stubborn"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: the Keel (tools/handbuilt_keel.py): the ballast golems, the keel's own crystal grown loose, the crawlers in the
#: chainwell, and the wardens who went down to tend the keel and never came back up. Trash rolled from the cave's own
#: table, the two bosses pinned by the map.
CAVE_ROSTER = {
    "Ballast Golem":          ("elemental_bruiser", 53, 54, None, "kh_gravity_golem", "bruiser", "physical",
                               ["Ballast Fist", "Heavy Step", "Weighed Down"]),
    "Keel-Crystal Shard":     ("elemental_caster", 53, 54, None, "sk_crystal_elemental", "caster", "arcane",
                               ["Shard", "Crystal Flare", "Crystal Burn"]),
    "Chainwell Crawler":      ("beast_fast", 53, 54, None, "sk_rift_crawler", "beast", "shadow",
                               ["Rending Claws", "Up the Chain", "Rift-Sick"]),
    "Hollowed Warden":        ("humanoid_warrior", 53, 54, None, "ae_warden", "warrior", "arcane",
                               ["Warden's Blade", "Last Watch", "Warded"]),
    "Warden-Captain Oris Hale": ("humanoid_warrior", 54, 54, 2.3, "ae_city_guard", "boss", "arcane",
                                 ["Captain's Blade", "Hold the Post", "Shield-Bash", "No One Leaves the Post"]),
    "The Keel-Heart":         ("elemental_caster", 54, 54, 2.5, "ae_construct_titan", "boss", "arcane",
                               ["Keel-Light", "The Crack Widens", "Held in the Light", "The Keel Gives Way"]),
}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
#: the boss whose kit gets a heal instead of a big blast
HEALER_BOSSES = {"Warden-Captain Oris Hale"}
ALL = {**ROSTER, **CAVE_ROSTER}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE ANCHORFIELDS (generated by tools/build_anchorfields_content.py; do not edit by hand)\n"
RULES_END = "    # END THE ANCHORFIELDS\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE CELESTIAL EXPANSE (generated by tools/build_celestial_expanse_content.py; do not edit by hand)\n"
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
                buff(names[2], 6, 3, {"armor": 190})]
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
                dot(f"{names[1]}, Deep", int(b * 0.45), 5, 4, school=s, **({"dispel_type": dispel} if s != "physical"
                                                                            else {}))]
        if name in HEALER_BOSSES:
            kit_.append(heal("Last Orders", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("The Shelf Shakes", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Shelfrunner Hare": 5, "Lantern Puffball": 4},
    "subzones": {
        "The Estates": {"Estate Sentinel": 5, "Garden Repair-Drone": 4, "Orchard Fowl": 4, "The Gardener": 0},
        "The First Anchor": {"Chain-Wind Elemental": 5, "Anchorlight Wisp": 5, "Shelfrunner Hare": 1,
                             "Starfall, the Burning Shard": 0},
        "The Gearwork": {"Overloaded Construct": 5, "Scrap-Walker": 4, "Overflow Elemental": 4, "Engine Seven": 0},
        "The Seized Anchor": {"Ascendancy Warden": 4, "Ascendancy Crystal-Weaver": 4, "Ascendancy Bomber Construct": 3,
                              "Ascendancy Engineer": 3, "Anchor-Marshal Corvan Sael": 0},
        "The Slipping Anchor": {"Slipstone Elemental": 5, "Keelcrack Crawler": 4, "Void-Touched Wisp": 4,
                                "The Unmoored": 0},
        "The Dropfield": {"Dropfield Stalker": 4, "Wreck-Rubble Elemental": 4, "Carrion Gale Hawk": 4,
                          "Old Ballast": 0},
        "The Listing Isle": {"Tiltside Goat": 5, "Cliffside Moth": 4, "Old Hornback": 0},
        "The Aqueduct Arm": None,
        "Keelstone": None,
        "Tiltside": None,
        "The Observatory": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "The Gardener": [
        ("Gardener's Crystal Shears", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical"),
        ("Orchard-Keeper's Gloves", "hands", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("House Vaelith Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Grafted Silverbark Ring", "ring", "of the Wolf", None, "agi_int_hybrid")],
    "Starfall, the Burning Shard": [
        ("Shard of Starfall", "trinket", "of the Sorcerer", None, "int_caster"),
        ("Star-Scorched Mantle", "shoulder", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Fallen Light Hauberk", "chest", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Burning Shard Signet", "ring", "of the Gorilla", None, "str_int_hybrid")],
    "Engine Seven": [
        ("Piston-Driven Maul", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical"),
        ("Gearwork Breastplate", "chest", "of the Bear", ("a", "plate"), "str_physical"),
        ("Coolant-Stained Jerkin", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Engine Seven's Governor", "trinket", "of the Monkey", None, "agi_physical")],
    "Anchor-Marshal Corvan Sael": [
        ("Marshal's Crystal Staff", "two_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Seized Anchor Pauldrons", "shoulder", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Ascendant Edict", "off_hand", "of the Prophet", ("w", "tome"), "spi_healer"),
        ("Sael's Command Belt", "waist", "of the Wolf", ("a", "mail"), "agi_int_hybrid")],
    "The Unmoored": [
        ("Unmoored Wraps", "wrist", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Gravityless Treads", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Void-Hollowed Helm", "head", "of the Bear", ("a", "plate"), "str_physical"),
        ("Nothing-to-Hold Pendant", "neck", "of the Prophet", None, "spi_healer")],
    "Old Ballast": [
        ("Ballast-Stone Bulwark", "off_hand", "of the Bear", ("w", "shield"), "str_physical"),
        ("Dropfield Salvager's Cloak", "back", "of the Monkey", None, "agi_physical"),
        ("Dead Weight Legguards", "legs", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Fallen Isle Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer")],
    "Old Hornback": [
        ("Hornback's Horn Bow", "ranged", "of the Monkey", ("w", "bow"), "agi_physical"),
        ("Tilt-Walker Boots", "feet", "of the Bear", ("a", "plate"), "str_physical"),
        ("Stubborn Hide Vest", "chest", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Old Hornback's Charm", "neck", "of the Sorcerer", None, "int_caster")],
}

#: the Keel's bosses: item level = boss level + 2
CAVE_POOLS = {
    "Warden-Captain Oris Hale": [
        ("Hale's Warden Blade", "main_hand", "of the Champion", ("w", "sword_1h"), "str_physical"),
        ("Last Post Shoulderguards", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Lost Warden's Cowl", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Unrelieved Watch Band", "ring", "of the Monkey", None, "agi_physical")],
    "The Keel-Heart": [
        ("Keel-Heart Crystal", "trinket", "of the Sorcerer", None, "int_caster"),
        ("Keel-Forged Chestguard", "chest", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Cracked Keel Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Anchor-Light Wand", "ranged", "of the Invoker", ("w", "wand"), "int_caster")],
}

#: gathering at 51-54: the high herbs on the shards, mithril, truesilver and thorium in the shelf's stone, and wood
#: off the Estates' groves. Fishing: the Estates' pool, the coolant pond and Tiltside's spring.
NODES = {"anchorfields": {"slots": 40, "active_percent": 0.42, "table": {
    "herb_sungrass": 2, "herb_purple_lotus": 2, "herb_firebloom": 3, "herb_khadgar": 3,
    "ore_mithril": 2, "ore_truesilver": 3, "ore_thorium": 3,
    "wood_thornveil_stump": 5}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(51, 54)
    fits = sorted([(fid, sk) for fid, _n, sk, _i, _d in FISH if s_lo <= sk <= s_hi], key=lambda f: -f[1])[:4]
    return {"slots": 8, "active_percent": 0.6, "table": {fid: 3 if n else 2 for n, (fid, _s) in enumerate(fits)}}


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
    from tools import handbuilt_keel as KL
    KL.build_keel_baked()
    if set(KL.BOSSES) != CAVE_BOSSES or set(CAVE_POOLS) != CAVE_BOSSES:
        bad.append(f"the cave's bosses differ: map {sorted(KL.BOSSES)}, roster {sorted(CAVE_BOSSES)}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, r in ALL.items():
        if not (ROOT / "assets/creatures" / f"{sprite(name)}.png").exists():
            bad.append(f"{name}'s sprite {sprite(name)} is not on disk")
        prev = existing.get(name)
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
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "afi_")
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ROSTER, 2, "kli_")
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
    entry = enc["zones"].setdefault(ZONE, {})
    entry["name"] = ZONE
    entry["open_zone"] = {"name": ZONE, "creatures": dict(TABLE["open_zone"])}
    entry["subzones"] = {s: ({"name": s, "safe": True, "creatures": {}} if c is None else
                             {"name": s, "creatures": dict(c)}) for s, c in TABLE["subzones"].items()}
    entry.setdefault("caves", {})[CAVE] = {"name": CAVE, "creatures": {n: (0 if r[3] else 4)
                                                                         for n, r in CAVE_ROSTER.items()}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    np_path = ROOT / "data/gathering/node_pools.json"
    nd = json.loads(np_path.read_text(encoding="utf-8"))
    nodes = json.loads(json.dumps(NODES))
    nodes["anchorfields"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Anchorfields' open-world rares (52-54). ONE item per kill from the rare's four; item_level = "
                      "the rare's level + 3. Hand-authored in tools/build_anchorfields_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for the Keel (the root of the Anchorfields' third anchor, 53-54). ONE item per kill "
                      "from the boss's four; item_level = boss level + 2. Hand-authored in "
                      "tools/build_anchorfields_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares), {len(CAVE_ROSTER)} in the cave "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
