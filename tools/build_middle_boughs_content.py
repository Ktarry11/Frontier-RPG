#!/usr/bin/env python3
"""The Middle Boughs' creatures, rares, encounter tables, loot, gathering and fishing (45-47), and Shriekhollow's
(the harpies' hollow in the trunk off the terraces). Idempotent.

    PYTHONPATH=. python3 tools/build_middle_boughs_content.py [--dry]

docs/worldtree_brief.md: "The tree is hungry: bark rot, sap blight, things living in the rot; harpies nesting in the
hollows", and on the ascent, "a crashed scout construct, still twitching". Sprites are Kyle's sheet W6 (wt_*), with the
harpies and the owls borrowed from older sheets under their own names.

    The Old Terraces       skinks, moths and owls on the first climbers' stone            rare: Hushwing
    The Lichen Reach       what crawled out of the construct, and pythons in the lichen   rare: The Wakened Surveyor
    The Rotting Bough      the rot and what lives in it                                   rare: Old Barkrot
    The Hollow Bough       the blighted harpies in the hollows                            rare: Old Raggedwing
    Heartwatch             the shadow hunters' outpost                                    safe
    Shriekhollow (cave)    harpies on the roost, the rot below            bosses: Matron Vyssa, Old Splinterheart

THE NUMBERS follow the Lower Boughs': trash basic 4L - 10, a rare's 10L - 200 at multiplier 2.2, item level = the rare's
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

RARE_LOOT = ROOT / "data/loot/middle_boughs_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/shriekhollow_boss_loot.json"
LB = "The Middle Boughs"
CAVE = "Shriekhollow"
MAP_MODULE = "handbuilt_worldtree_middle_boughs"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare/boss multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- the Old Terraces
    "Terrace Skink":          ("beast_fast", 45, 46, None, "wt_bark_lizard", "beast", "physical",
                               ["Bite", "Skittering Snap", "Grit in the Wound"]),
    "Lichenwing Moth":        ("beast_fast", 45, 46, None, "wt_leafwing_moth", "caster", "nature",
                               ["Pale Dust", "Wingbeat Flurry", "Lichen Rash"]),
    "Mistfeather Owl":        ("beast_fast", 45, 46, None, "st_canopy_owl", "beast", "physical",
                               ["Talon Rake", "Silent Swoop", "Torn Feathers"]),
    "Hushwing":               ("beast_fast", 46, 46, 2.2, "ps_fen_owl", "rare", "physical",
                               ["Hushed Talons", "Out of the Mist", "Carried Off", "Old Hunter's Patience"]),
    # ---------------------------------------------------------------- the Lichen Reach: the construct and the lichen
    "Scuttling Gear-Drone":   ("humanoid_warrior", 45, 46, None, "wt_gear_drone", "warrior", "physical",
                               ["Clamp", "Whirring Charge", "Bronze Plating"]),
    "Twitching Scout":        ("humanoid_caster", 45, 46, None, "wt_scout_construct", "caster", "arcane",
                               ["Arc Spark", "Discharge", "Static Lock"]),
    "Mistcoil Python":        ("beast_large", 45, 46, None, "wt_tree_python", "bruiser", "physical",
                               ["Constrict", "Coiled Strike", "Winded"]),
    "The Wakened Surveyor":   ("humanoid_caster", 46, 46, 2.2, "wt_scout_construct", "rare", "arcane",
                               ["Surveying Beam", "Arcane Pulse", "Held in the Light", "Overcharged Core"]),
    # ---------------------------------------------------------------- the Rotting Bough
    "Rotheart Treant":        ("elemental_bruiser", 46, 47, None, "wt_rot_treant", "bruiser", "nature",
                               ["Rotten Limb", "Shower of Rot", "Mouldering"]),
    "Blightgrub":             ("vermin_swarm", 46, 47, None, "wt_rot_crawler", "beast", "nature",
                               ["Gnaw", "Burrowing Lunge", "Blight Bile"]),
    "Rotspore Cloud":         ("elemental_caster", 46, 47, None, "wt_spore_swarm", "caster", "nature",
                               ["Rotspores", "Choking Cloud", "Spore Fever"]),
    "Sap-Blight Ooze":        ("elemental_bruiser", 46, 47, None, "wt_sap_ooze", "bruiser", "nature",
                               ["Blighted Engulf", "Burst of Bad Sap", "Gummed Fast"]),
    "Old Barkrot":            ("elemental_bruiser", 47, 47, 2.2, "wt_rot_treant", "rare", "nature",
                               ["Barkrot Fist", "The Bough Sags", "Rooted in Rot", "Rotten to the Core"]),
    # ---------------------------------------------------------------- the Hollow Bough: the harpies
    "Blighted Harpy":         ("humanoid_rogue", 46, 47, None, "wt_blighted_harpy", "warrior", "physical",
                               ["Raking Claws", "Diving Rake", "Blight-Hardened"]),
    "Hollow Screecher":       ("beast_fast", 46, 47, None, "harpy_1", "beast", "physical",
                               ["Talon Slash", "Screech", "Festering Scratch"]),
    "Hollow Talon":           ("humanoid_ranged", 46, 47, None, "harpy_2", "beast", "physical",
                               ["Thrown Feather-Knife", "Volley From Above", "Barbed Feather"]),
    "Hollow Windcaller":      ("humanoid_caster", 46, 47, None, "st_windshear_witch", "caster", "nature",
                               ["Gust", "Cutting Wind", "Wind-Sick"]),
    "Old Raggedwing":         ("humanoid_rogue", 47, 47, 2.2, "harpy_3", "rare", "physical",
                               ["Ragged Talons", "Wings Like Knives", "Dragged Off the Bough", "Last of the Old Flock"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: Shriekhollow: trash rolled from the cave's own table, the two bosses pinned by the map (tools/handbuilt_shriekhollow)
CAVE_ROSTER = {
    "Brood-Harpy":            ("humanoid_rogue", 46, 47, None, "wt_blighted_harpy", "warrior", "physical",
                               ["Brood Claws", "Mobbing Rake", "Hardened by the Rot"]),
    "Shriekhollow Screamer":  ("beast_fast", 46, 47, None, "harpy_1", "caster", "physical",
                               ["Shriek", "Scream Through the Hollow", "Ringing Ears"]),
    "Roost Talonguard":       ("humanoid_warrior", 46, 47, None, "st_windshear_harpy", "bruiser", "physical",
                               ["Talon Guard", "Sweep of Wings", "Off Your Feet"]),
    "Rotdark Crawler":        ("vermin_swarm", 46, 47, None, "wt_rot_crawler", "beast", "nature",
                               ["Gnaw in the Dark", "Squirming Lunge", "Rotdark Bile"]),
    "Rotdark Spores":         ("elemental_caster", 46, 47, None, "wt_spore_swarm", "caster", "nature",
                               ["Dark Spores", "Choking Rot", "Spore-Blind"]),
    "Matron Vyssa":           ("humanoid_caster", 47, 47, 2.3, "harpy_matriarch", "boss", "nature",
                               ["Matron's Talons", "Blighted Shriek", "Snatched Up", "Every Harpy Screams"]),
    "Old Splinterheart":      ("elemental_bruiser", 47, 47, 2.5, "st_redwood_ancient", "boss", "nature",
                               ["Splintered Fist", "Rot in the Wood", "Crushed Under Bark", "The Rot Comes Up"]),
}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
ALL = {**ROSTER, **CAVE_ROSTER}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE MIDDLE BOUGHS (generated by tools/build_middle_boughs_content.py; do not edit by hand)\n"
RULES_END = "    # END THE MIDDLE BOUGHS\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # THE LOWER BOUGHS (generated by tools/build_lower_boughs_content.py; do not edit by hand)\n"
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
        if name == "Matron Vyssa":
            kit_.append(heal("Fed by the Flock", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("The Whole Hollow Rots", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Terrace Skink": 4, "Lichenwing Moth": 3, "Mistfeather Owl": 1},
    "subzones": {
        "The Old Terraces": {"Terrace Skink": 5, "Lichenwing Moth": 4, "Mistfeather Owl": 3, "Hushwing": 0},
        "The Lichen Reach": {"Scuttling Gear-Drone": 5, "Twitching Scout": 4, "Mistcoil Python": 4,
                             "Mistfeather Owl": 2, "The Wakened Surveyor": 0},
        "The Rotting Bough": {"Rotheart Treant": 4, "Blightgrub": 5, "Rotspore Cloud": 4, "Sap-Blight Ooze": 4,
                              "Old Barkrot": 0},
        "The Hollow Bough": {"Blighted Harpy": 5, "Hollow Screecher": 4, "Hollow Talon": 4, "Hollow Windcaller": 3,
                             "Old Raggedwing": 0},
        "Heartwatch": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Hushwing": [
        ("Hushwing Feather Cloak", "back", "of the Monkey", None, "agi_physical"),
        ("Silent Hunter's Wraps", "wrist", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Owl-Talon Gauntlets", "hands", "of the Bear", ("a", "plate"), "str_physical"),
        ("Mistfeather Mantle", "shoulder", "of the Prophet", ("a", "leather"), "spi_healer")],
    "The Wakened Surveyor": [
        ("Surveyor's Lens", "off_hand", "of the Invoker", ("w", "tome"), "int_caster"),
        ("Bronze-Plated Vambraces", "wrist", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Arc-Wired Chain Leggings", "legs", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Overcharged Coil Ring", "ring", "of the Sorcerer", None, "int_caster")],
    "Old Barkrot": [
        ("Barkrot Bracers", "wrist", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Rot-Root Staff", "two_hand", "of the Physician", ("w", "staff"), "spi_healer"),
        ("Mouldered Heartwood Greaves", "legs", "of the Bear", ("a", "plate"), "str_physical"),
        ("Sporecap Hood", "head", "of the Sorcerer", ("a", "cloth"), "int_caster")],
    "Old Raggedwing": [
        ("Raggedwing's Talon", "main_hand", "of the Tiger", ("w", "fist_weapon"), "agi_physical"),
        ("Flock-Elder's Shoulderguards", "shoulder", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Plucked-Feather Sandals", "feet", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Hollow-Roost Jerkin", "chest", "of the Wolf", ("a", "leather"), "agi_int_hybrid")],
}
CAVE_POOLS = {
    "Matron Vyssa": [
        ("Matron's Blighted Plumage", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Vyssa's Raking Claw", "main_hand", "of the Monkey", ("w", "fist_weapon"), "agi_physical"),
        ("Eyrie-Guard Pauldrons", "shoulder", "of the Bear", ("a", "plate"), "str_physical"),
        ("Screaming Wind Band", "ring", "of the Sorcerer", None, "int_caster")],
    "Old Splinterheart": [
        ("Splinterheart Bark-Mail", "chest", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Rotdark Sabatons", "feet", "of the Bear", ("a", "plate"), "str_physical"),
        ("Heartrot Branch", "two_hand", "of the Invoker", ("w", "staff"), "int_caster"),
        ("Grubhide Gloves", "hands", "of the Monkey", ("a", "leather"), "agi_physical")],
}

#: gathering at 45-47 up the tree: the 40s herbs on the bark, wood from the boughs, and a little mithril caught in the
#: forks and the terraces' fallen stone. Fishing: rain held in the bark's hollows (tools/build_fishing.window).
NODES = {"middle_boughs": {"slots": 24, "active_percent": 0.42, "table": {
    "herb_khadgar": 3, "herb_goldthorn": 2, "herb_fadeleaf": 2, "herb_purple_lotus": 3, "herb_sungrass": 3,
    "herb_liferoot": 2,
    "ore_mithril": 3,
    "wood_bloodroot_stump": 3, "wood_thornveil_stump": 3}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(45, 47)
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
    from tools import handbuilt_shriekhollow as KH
    KH.build_shriekhollow_baked()
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
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "mbi_")
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ROSTER, 2, "shi_")
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
    nodes["middle_boughs"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Middle Boughs' open-world rares (46-47). ONE item per kill from the rare's four; item_level = "
                      "the rare's level + 3. Hand-authored in tools/build_middle_boughs_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for Shriekhollow (the World Tree's trunk, 45-47). ONE item per kill from the boss's "
                      "four; item_level = boss level + 2. Hand-authored in tools/build_middle_boughs_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares), {len(CAVE_ROSTER)} in the cave "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
