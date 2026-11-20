#!/usr/bin/env python3
"""The Lower Boughs' creatures, rares, encounter tables, loot, gathering and fishing (44-45), and the Knothollow's
(the cave into the trunk off the ledge). Idempotent.

    PYTHONPATH=. python3 tools/build_lower_boughs_content.py [--dry]

docs/worldtree_brief.md: the first lived-on tier. "Climbers from below (Bloodscalp war parties come up the roots);
sap-drunk apes and spiders." Sprites are Kyle's sheet W6 (the wt_* sprites, docs/worldtree_art_prompts.md); the ones
Rootwater wears are worn here by other creatures of the same kind, under their own names.

    The Trunk Ledge        skinks and moths along the trunk's foot
    The Greenwater Bough   pythons and sap oozes down the river bough                   rare: Sunscale
    The Howling Bough      the sap-drunk apes                                           rare: Old Goldtooth
    The Silkwood           the canopy spiders                                           rare: Mother Lattice
    The Climbers' Cut      the Bloodscalp coming up on ropes                            rare: Ropemaster Vaz'jin
    Mossroof               the trolls' village                                          safe
    The Knothollow (cave)  borers, grubs, sap and spiders in the trunk         bosses: Gnawmother Ixx, The Amber Glut

THE NUMBERS follow Rootwater's: trash basic 4L - 10, a rare's 10L - 200 at multiplier 2.2, item level = the rare's
level + 3. The cave's are the Zukk'ash Hive's: a boss's basic 10L - 200, multiplier 2.5 for the one at the end and 2.3 for
the other, item level = boss level + 2, and every boss carries something dangerous.
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

RARE_LOOT = ROOT / "data/loot/lower_boughs_rare_loot.json"
CAVE_LOOT = ROOT / "data/loot/knothollow_boss_loot.json"
LB = "The Lower Boughs"
CAVE = "The Knothollow"
MAP_MODULE = "handbuilt_worldtree_lower_boughs"


def T(level):
    return 4 * level - 10


def B(level):
    return 10 * level - 200


#: name -> (template, lo, hi, rare/boss multiplier or None, sprite, kit shape, school, [ability names])
ROSTER = {
    # ---------------------------------------------------------------- wanderers, along the trunk and the boughs
    "Mossback Skink":         ("beast_fast", 44, 45, None, "wt_bark_lizard", "beast", "physical",
                               ["Bite", "Darting Snap", "Festering Bite"]),
    "Glimmerwing Moth":       ("beast_fast", 44, 45, None, "wt_leafwing_moth", "caster", "nature",
                               ["Glittering Dust", "Wingbeat Gust", "Dust in the Eyes"]),
    # ---------------------------------------------------------------- the Greenwater Bough
    "Bough Python":           ("beast_large", 44, 45, None, "wt_tree_python", "bruiser", "physical",
                               ["Constrict", "Coiled Lunge", "Squeezed"]),
    "Amberdrip Ooze":         ("elemental_bruiser", 44, 45, None, "wt_sap_ooze", "bruiser", "nature",
                               ["Smother", "Amber Splash", "Gummed"]),
    "Sunscale":               ("beast_large", 45, 45, 2.2, "wt_tree_python", "rare", "physical",
                               ["Sunlit Coils", "Thrashing Tail", "Wrapped and Squeezed", "Basking Fury"]),
    # ---------------------------------------------------------------- the Howling Bough: the apes
    "Canopy Howler":          ("beast_fast", 44, 45, None, "wt_canopy_ape", "beast", "physical",
                               ["Pummel", "Howling Leap", "Torn Ear"]),
    "Sap-Drunk Silverback":   ("beast_large", 44, 45, None, "wt_sap_silverback", "bruiser", "physical",
                               ["Fist Slam", "Chest-Beat Shockwave", "Rattled"]),
    "Old Goldtooth":          ("beast_large", 45, 45, 2.2, "wt_sap_silverback", "rare", "physical",
                               ["Golden Fist", "Bough Shaker", "Thrown From the Branch", "Drunk on Sap"]),
    # ---------------------------------------------------------------- the Silkwood: the spiders
    "Silkwood Weaver":        ("beast_fast", 44, 45, None, "wt_canopy_spider", "beast", "nature",
                               ["Venom Bite", "Web Spray", "Weaver's Venom"]),
    "Silkwood Stalker":       ("beast_fast", 44, 45, None, "wt_canopy_spider", "warrior", "physical",
                               ["Lunging Bite", "Drop From the Web", "Hardened Carapace"]),
    "Mother Lattice":         ("beast_fast", 45, 45, 2.2, "wt_canopy_spider", "rare", "nature",
                               ["Lattice Fangs", "Web of the Mother", "Cocooned", "Every Strand Hers"]),
    # ---------------------------------------------------------------- the Climbers' Cut: the Bloodscalp
    "Bloodscalp Ropecutter":  ("humanoid_rogue", 44, 45, None, "wt_bloodscalp_climber", "warrior", "physical",
                               ["Hooked Knife", "Swing on the Rope", "Climber's Grip"]),
    "Bloodscalp Skull-Taker": ("humanoid_ranged", 44, 45, None, "wt_bloodscalp_headhunter", "beast", "physical",
                               ["Thrown Spear", "Marked for a Trophy", "Barbed Point"]),
    "Bloodscalp Spear-Hurler": ("humanoid_ranged", 44, 45, None, "wt_bloodscalp_axe_thrower", "beast", "physical",
                                ["Hurled Spear", "Two Spears", "Pinned"]),
    "Bloodscalp Reaver":      ("humanoid_warrior", 44, 45, None, "wt_bloodscalp_berserker", "bruiser", "physical",
                               ["Cleaving Axe", "Reaving Sweep", "Knocked Off Balance"]),
    "Bloodscalp Bough-Shaman": ("humanoid_caster", 44, 45, None, "wt_bloodscalp_shaman", "caster", "nature",
                                ["Lightning Bolt", "Storm Through the Leaves", "Static Hex"]),
    "Bloodscalp Hexer":       ("humanoid_caster", 44, 45, None, "wt_bloodscalp_witch_doctor", "caster", "shadow",
                               ["Shadow Bolt", "Hex Smoke", "Hexer's Curse"]),
    "Ropemaster Vaz'jin":     ("humanoid_rogue", 45, 45, 2.2, "wt_bloodscalp_climber", "rare", "physical",
                               ["Rope Knife", "Swung From Below", "Cut Loose", "Vaz'jin's Climb"]),
}
RARES = {n for n, r in ROSTER.items() if r[3]}

#: the Knothollow: trash rolled from the cave's own table, the two bosses pinned by the map (tools/handbuilt_knothollow)
CAVE_ROSTER = {
    "Knothollow Borer":       ("vermin_swarm", 44, 45, None, "wt_bark_borer", "warrior", "physical",
                               ["Boring Mandibles", "Chew Through", "Bark-Hard Shell"]),
    "Borer Grub":             ("vermin_swarm", 44, 45, None, "wt_rot_crawler", "beast", "nature",
                               ["Gnaw", "Squirming Lunge", "Grub Bile"]),
    "Sapwell Ooze":           ("elemental_bruiser", 44, 45, None, "wt_sap_ooze", "bruiser", "nature",
                               ["Engulf", "Burst of Sap", "Stuck Fast"]),
    "Hollow Weaver":          ("beast_fast", 44, 45, None, "wt_canopy_spider", "beast", "nature",
                               ["Fang", "Web in the Dark", "Hollow Venom"]),
    "Knotrot Swarm":          ("elemental_caster", 44, 45, None, "wt_spore_swarm", "caster", "nature",
                               ["Rot Spores", "Choking Rot", "Spore-Sick"]),
    "Gnawmother Ixx":         ("beast_large", 45, 45, 2.5, "wt_bark_borer", "boss", "nature",
                               ["Mother's Mandibles", "Borer Venom", "The Wood Gives Way", "Call the Brood"]),
    "The Amber Glut":         ("elemental_bruiser", 45, 45, 2.3, "wt_sap_ooze", "boss", "nature",
                               ["Amber Fist", "Smothering Sap", "Swallowed Whole", "Sap Flood"]),
}
CAVE_BOSSES = {n for n, r in CAVE_ROSTER.items() if r[3]}
ALL = {**ROSTER, **CAVE_ROSTER}


def sprite(name):
    return ALL[name][4]


RULES_START = "    # THE LOWER BOUGHS (generated by tools/build_lower_boughs_content.py; do not edit by hand)\n"
RULES_END = "    # END THE LOWER BOUGHS\n"


def write_sprite_rules():
    path = ROOT / "creature_sprites.py"
    s = path.read_text(encoding="utf-8")
    block = RULES_START + "".join(f'    (r"^{re.escape(n.lower())}$", "{sprite(n)}"),\n' for n in ALL) + RULES_END
    if RULES_START in s:
        a = s.index(RULES_START)
        b = s.index(RULES_END) + len(RULES_END)
        s = s[:a] + block + s[b:]
    else:
        anchor = "    # ROOTWATER ISLE (generated by tools/build_rootwater_isle_content.py; do not edit by hand)\n"
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
        if name == "Gnawmother Ixx":
            kit_.append(heal("Feed on the Brood", int(b * 1.1), 6, school=s))
        else:
            kit_.append(dmg("Everything Turns to Amber", int(b * 1.8), cooldown=4, school=s))
        kit_.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=s,
                         duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
        return kit_
    # an open-world rare: a heavy basic, a party hit, a stun with a hammer behind it, and its last stand
    last = (shield(names[3], int(b * 1.2), school=s) if s in ("arcane", "frost") else enrage(names[3], int(b * 0.15), s))
    return [dmg(names[0], b, school=s), dmg(names[1], int(b * 0.8), cooldown=4, school=s, is_aoe=True),
            stun(names[2], int(b * 0.85), cooldown=5, school=s), dmg(f"{names[0]}, Again", int(b * 1.7), cooldown=5,
                                                                   school=s), last]


TABLE = {
    "open_zone": {"Mossback Skink": 4, "Glimmerwing Moth": 3, "Bough Python": 1},
    "subzones": {
        "The Trunk Ledge": {"Mossback Skink": 5, "Glimmerwing Moth": 5, "Bough Python": 1},
        "The Greenwater Bough": {"Bough Python": 5, "Amberdrip Ooze": 5, "Glimmerwing Moth": 2, "Mossback Skink": 1,
                                 "Sunscale": 0},
        "The Howling Bough": {"Canopy Howler": 6, "Sap-Drunk Silverback": 5, "Mossback Skink": 1, "Old Goldtooth": 0},
        "The Silkwood": {"Silkwood Weaver": 6, "Silkwood Stalker": 5, "Glimmerwing Moth": 1, "Mother Lattice": 0},
        "The Climbers' Cut": {"Bloodscalp Ropecutter": 5, "Bloodscalp Skull-Taker": 4, "Bloodscalp Spear-Hurler": 4,
                              "Bloodscalp Reaver": 4, "Bloodscalp Bough-Shaman": 3, "Bloodscalp Hexer": 3,
                              "Ropemaster Vaz'jin": 0},
        "Mossroof": None,
    },
}

#: rare -> four (name, slot, suffix, (a|w, type) or None, template)
POOLS = {
    "Sunscale": [
        ("Sunscale Hide Vest", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Coiled Python Girdle", "waist", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Basking Stone Pendant", "neck", "of the Owl", None, "spi_healer"),
        ("Sunscale Fang", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical")],
    "Old Goldtooth": [
        ("Goldtooth's Knuckle-Wraps", "hands", "of the Bear", ("a", "plate"), "str_physical"),
        ("Silverback Mantle", "shoulder", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Sap-Matted Hood", "head", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Bough-Breaker Maul", "two_hand", "of the Champion", ("w", "mace_2h"), "str_physical")],
    "Mother Lattice": [
        ("Lattice-Silk Robe", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Webwalker Boots", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Silkwood Spaulders", "shoulder", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Mother's Spinneret Wand", "ranged", "of the Invoker", ("w", "wand"), "int_caster")],
    "Ropemaster Vaz'jin": [
        ("Vaz'jin's Rope Knife", "main_hand", "of the Monkey", ("w", "dagger"), "agi_physical"),
        ("Climber's Hide Leggings", "legs", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Bloodscalp Bone Bracers", "wrist", "of the Bear", ("a", "plate"), "str_physical"),
        ("Hexer's Shrunken Head", "off_hand", "of the Sorcerer", ("w", "tome"), "int_caster")],
}
CAVE_POOLS = {
    "Gnawmother Ixx": [
        ("Borer-Chitin Breastplate", "chest", "of the Bear", ("a", "plate"), "str_physical"),
        ("Gnawmother's Silk Leggings", "legs", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Bored-Through Bracers", "wrist", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Mandible Shiv", "main_hand", "of the Tiger", ("w", "dagger"), "agi_physical")],
    "The Amber Glut": [
        ("Amber-Sealed Hauberk", "chest", "of the Gorilla", ("a", "mail"), "str_int_hybrid"),
        ("Heartwood Staff", "two_hand", "of the Physician", ("w", "staff"), "spi_healer"),
        ("Sap-Gilded Cowl", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Glut-Glazed Treads", "feet", "of the Monkey", ("a", "leather"), "agi_physical")],
}

#: gathering at 44-45 up the tree: the 40s herbs on the bark, wood from the boughs, and a little mithril in the stones
#: caught in the forks. Fishing: the river down the Great Bough, fish the zone's level fits (tools/build_fishing.window).
NODES = {"lower_boughs": {"slots": 24, "active_percent": 0.42, "table": {
    "herb_khadgar": 3, "herb_goldthorn": 3, "herb_fadeleaf": 2, "herb_purple_lotus": 2, "herb_sungrass": 2,
    "herb_liferoot": 2,
    "ore_mithril": 3,
    "wood_bloodroot_stump": 3, "wood_thornveil_stump": 3}}}


def fishing():
    from tools.build_fishing import FISH, window
    s_lo, s_hi = window(44, 45)
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
    from tools import handbuilt_knothollow as KH
    KH.build_knothollow_baked()
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
    rare_loot, rows = build_loot(POOLS, ROSTER, 3, "lbi_")
    cave_loot, crows = build_loot(CAVE_POOLS, CAVE_ROSTER, 2, "khi_")
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
    nodes["lower_boughs"]["fishing"] = fishing()
    nd["zones"].update(nodes)
    np_path.write_text(json.dumps(nd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("The Lower Boughs' open-world rares (45). ONE item per kill from the rare's four; item_level = the "
                      "rare's level + 3. Hand-authored in tools/build_lower_boughs_content.py.")}
    out.update(rare_loot)
    RARE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = {"_notes": ("Boss loot for the Knothollow (the World Tree's trunk, 44-45). ONE item per kill from the boss's "
                      "four; item_level = boss level + 2. Hand-authored in tools/build_lower_boughs_content.py.")}
    out.update(cave_loot)
    CAVE_LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} open-world creatures ({len(RARES)} rares), {len(CAVE_ROSTER)} in the cave "
          f"({len(CAVE_BOSSES)} bosses); {len(rows) + len(crows)} items; gathering and fishing")
    return 0


if __name__ == "__main__":
    sys.exit(main())
