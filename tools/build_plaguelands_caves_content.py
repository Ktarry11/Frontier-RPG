#!/usr/bin/env python3
"""The Plaguelands caves' creatures, kits, encounter tables, zone levels and boss loot. Idempotent.

    PYTHONPATH=. python3 tools/build_plaguelands_caves_content.py

The maps are tools/handbuilt_plaguelands_caves.py (its docstring has the shapes). Caves, not dungeons: one or two
bosses pinned by the map, trash rolled from the cave's own table under its parent map's "caves", no set packs.
Each cave sits at the top of its parent map's band, because a cave is never below its zone.

  THE WRITHING DEEP   53-55  crypt fiends and their brood         Broodlord Szarak, the Silken Bride (optional)
  THE WEEPING CAVE    55-57  the drowned and what lives in the wet The Weeper, the Drowned Hermit (optional)
  THE MARRIS CRYPT    56-58  the Marris family's dead               Sexton Hollowell, the Bone Choir
  THE BONE MINES      58-60  the Scourge's bone miners              Overseer Marrowgrim, the Ossifier (optional)

THE NUMBERS are the game's own 52-58 dungeons' (measured 16 Nov 2026): a boss's basic hit 10L - 200 (360 at 56),
trash 4L - 10. Boss health 2.5 for the one at the end, 2.3 for the optional one. Every boss carries something
dangerous (Kyle: "make sure bosses are not just debuffing"), and tools/qa_dungeon_boss_turns.py holds them to it.

LOOT. Four items a boss, item level = the boss's level + 2 (the caves' lift, as in Stonetalon's), spread over every
armour type and the six stat templates. No trinkets (every trinket from 50 has to do something).
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, loot_audit)
from tools.build_scarlet_monastery_content import opener, stun_hit, heal, hit_with  # noqa: E402
from tools import handbuilt_plaguelands_caves as PC  # noqa: E402

LOOT = ROOT / "data/loot/plaguelands_caves_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
W_, V_, M_, B_ = PC.WRITHING, PC.WEEPING, PC.MARRIS, PC.BONE
ZONE_LEVELS = {W_: [53, 55], V_: [55, 57], M_: [56, 58], B_: [58, 60]}


def BH(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


#: name -> (template, lo, hi, boss multiplier or None, sprite, cave)
ROSTER = {
    "Writhing Burrower":     ("undead_beast",     53, 55, None, "crypt_fiend_1", W_),
    "Deep Webspinner":       ("beast_fast",       53, 54, None, "spider_3", W_),
    "Haunt Larva":           ("vermin_swarm",     53, 54, None, "maggot", W_),
    "Brood Guardian":        ("undead_warrior",   54, 55, None, "crypt_fiend_2", W_),
    "Broodlord Szarak":      ("undead_beast",     55, 55, 2.5, "crypt_fiend_2", W_),
    "The Silken Bride":      ("beast_large",      55, 55, 2.3, "spider_broodmother_1", W_),
    "Seepwater Shade":       ("undead_caster",    55, 57, None, "spectre_1", V_),
    "Cave Drowned":          ("undead_basic",     55, 56, None, "drowned_sailor_3", V_),
    "Blind Cave Bat":        ("beast_fast",       55, 56, None, "bat", V_),
    "Seep Ooze":             ("elemental_bruiser", 56, 57, None, "ooze_acid_1", V_),
    "The Weeper":            ("undead_caster",    57, 57, 2.5, "banshee", V_),
    "The Drowned Hermit":    ("undead_warrior",   57, 57, 2.3, "drowned_sailor_1", V_),
    "Crypt Shambler":        ("undead_basic",     56, 57, None, "zombie_2", M_),
    "Marris Ossuary Guard":  ("undead_warrior",   56, 58, None, "skeleton_warrior_1", M_),
    "Crypt Rat Swarm":       ("vermin_swarm",     56, 57, None, "rat_plague_1", M_),
    "Grave Wight":           ("undead_caster",    57, 58, None, "revenant_1", M_),
    "Sexton Hollowell":      ("undead_warrior",   58, 58, 2.5, "revenant_2", M_),
    "The Bone Choir":        ("undead_caster",    58, 58, 2.3, "spectre_2", M_),
    "Bone Miner":            ("undead_basic",     58, 59, None, "ghoul_2", B_),
    "Scourge Pit Guard":     ("undead_warrior",   58, 60, None, "skeleton_warrior_2", B_),
    "Marrow Construct":      ("undead_warrior",   59, 60, None, "abomination_1", B_),
    "Bone Dust Swarm":       ("vermin_swarm",     58, 59, None, "maggot", B_),
    "Overseer Marrowgrim":   ("undead_warrior",   60, 60, 2.5, "abomination_2", B_),
    "The Ossifier":          ("humanoid_caster",  60, 60, 2.3, "necromancer", B_),
}
BOSSES = {n for n, r in ROSTER.items() if r[3]}


def trash(level, basic, second, third, school="physical"):
    t = T(level)
    return [dmg(basic, t, school=school), second(t), third(t)]


def boss(level, school, basic, second, heavy, spread, signature, *, aoe=True, extra=()):
    b = BH(level)
    kit = [opener(basic, b, school), dmg(second, int(b * 0.88), cooldown=4, school=school),
           dmg(heavy, int(b * 1.3), cooldown=4, school=school)]
    kit.append(dmg(spread, int(b * 0.7), cooldown=5, school=school, is_aoe=True) if aoe
               else dot(spread, int(b * 0.4), 5, 4, school=school))
    kit.extend(extra)
    kit.extend(signature)
    kit.append(dict(name="Last Stand", kind="buff", amount=0, cooldown=99, mana_cost=0, school=school,
                    duration=30, self_only=True, hp_below=0.3, stat_mods={"attack_power": int(b * 0.4)}))
    return kit


def kits():
    k = {}
    # ---- the Writhing Deep (53-55)
    k["Writhing Burrower"] = trash(55, "Pincer", lambda t: dmg("Burst From the Floor", int(t * 1.3), cooldown=4),
                                   lambda t: dot("Crypt Venom", int(t * 0.3), 4, 3, school="nature",
                                                 dispel_type="poison"))
    k["Deep Webspinner"] = trash(54, "Fang", lambda t: hit_with("Web Wrap", int(t * 0.8), {"haste": -12}, 2),
                                 lambda t: dot("Venom", int(t * 0.28), 4, 3, school="nature", dispel_type="poison"))
    k["Haunt Larva"] = trash(54, "Chew", lambda t: dmg("Swarm Over", int(t * 0.7), cooldown=4, is_aoe=True),
                             lambda t: dot("Burrowing", int(t * 0.25), 4, 3))
    k["Brood Guardian"] = trash(55, "Carapace Smash", lambda t: stun_hit("Pin Down", int(t * 1.1), 5),
                                lambda t: hit_with("Brood Call", int(t * 0.8), {"armor": 120}, 3, on="buff"))
    k["Broodlord Szarak"] = boss(55, "physical", "Rending Pincers", "Burrow Strike", "Impale", "Brood Swarm",
                                 [dmg("Erupt From Below", int(BH(55) * 1.8), cooldown=4),
                                  stun_hit("Web of the Brood", int(BH(55) * 1.1), 6)])
    k["The Silken Bride"] = boss(55, "nature", "Venom Fang", "Spit Silk", "Paralytic Bite", "Brood Burst",
                                 [dot("Bride's Venom", int(BH(55) * 0.5), 5, 4, school="nature",
                                      dispel_type="poison"),
                                  stun_hit("Cocoon", int(BH(55) * 1.0), 6, school="nature")], aoe=True)
    # ---- the Weeping Cave (55-57)
    k["Seepwater Shade"] = trash(57, "Cold Touch", lambda t: dmg("Weep", int(t * 0.7), cooldown=4,
                                                                  school="shadow", is_aoe=True),
                                 lambda t: hit_with("Drown the Senses", int(t * 0.8), {"intellect": -20}, 3,
                                                    school="shadow"), school="shadow")
    k["Cave Drowned"] = trash(56, "Waterlogged Fist", lambda t: dmg("Drag Under", int(t * 1.3), cooldown=4),
                              lambda t: dot("Cave Rot", int(t * 0.28), 4, 3, school="nature", dispel_type="disease"))
    k["Blind Cave Bat"] = trash(56, "Bite", lambda t: hit_with("Screech", int(t * 0.8), {"hit_rating": -14}, 2),
                                lambda t: dmg("Dive", int(t * 1.25), cooldown=3))
    k["Seep Ooze"] = trash(57, "Acid Slap", lambda t: hit_with("Corrode", int(t * 0.8), {"armor": -150}, 3,
                                                                school="nature"),
                           lambda t: dot("Dissolving", int(t * 0.3), 4, 3, school="nature"), school="nature")
    k["The Weeper"] = boss(57, "shadow", "Mournful Touch", "Keening", "Grief Lash", "Wail of the Drowned",
                           [dmg("Every Tear at Once", int(BH(57) * 1.8), cooldown=4, school="shadow"),
                            dot("Drowning Sorrow", int(BH(57) * 0.5), 5, 4, school="shadow", dispel_type="curse")])
    k["The Drowned Hermit"] = boss(57, "physical", "Oar Swing", "Net Throw", "Pulled Under", "Wash of Silt",
                                   [stun_hit("Held Under", int(BH(57) * 1.1), 5),
                                    dmg("Hermit's Grudge", int(BH(57) * 1.7), cooldown=4)], aoe=False)
    # ---- the Marris Crypt (56-58)
    k["Crypt Shambler"] = trash(57, "Grasp", lambda t: dmg("Lurch", int(t * 1.3), cooldown=4),
                                lambda t: dot("Grave Rot", int(t * 0.28), 4, 3, school="nature",
                                              dispel_type="disease"))
    k["Marris Ossuary Guard"] = trash(58, "Rusted Blade", lambda t: stun_hit("Shield Bash", int(t * 1.1), 5),
                                      lambda t: hit_with("Stand Guard", int(t * 0.8), {"armor": 150}, 3, on="buff"))
    k["Crypt Rat Swarm"] = trash(57, "Gnaw", lambda t: dmg("Swarm", int(t * 0.7), cooldown=4, is_aoe=True),
                                 lambda t: dot("Plague Bite", int(t * 0.25), 4, 3, school="nature",
                                               dispel_type="disease"))
    k["Grave Wight"] = trash(58, "Grave Chill", lambda t: dmg("Wither", int(t * 1.25), cooldown=4, school="shadow"),
                             lambda t: hit_with("Drain Warmth", int(t * 0.8), {"haste": -10}, 3, school="frost"),
                             school="shadow")
    k["Sexton Hollowell"] = boss(58, "physical", "Spade", "Shovel Swing", "Grave Digger's Blow", "Throw the Dirt",
                                 [dmg("Six Feet Under", int(BH(58) * 1.8), cooldown=4),
                                  stun_hit("Buried Alive", int(BH(58) * 1.1), 6)])
    k["The Bone Choir"] = boss(58, "shadow", "Dirge", "Requiem", "Last Rites", "Chorus of the Dead",
                               [dmg("The Final Verse", int(BH(58) * 1.0), cooldown=5, school="shadow", is_aoe=True),
                                dot("Funeral Hymn", int(BH(58) * 0.5), 5, 4, school="shadow", dispel_type="magic")],
                               extra=[heal("Sung Back Together", int(BH(58) * 1.2), 6, school="shadow")])
    # ---- the Bone Mines (58-60)
    k["Bone Miner"] = trash(59, "Pick", lambda t: dmg("Swing the Pick", int(t * 1.3), cooldown=4),
                            lambda t: dot("Marrow Dust", int(t * 0.28), 4, 3, school="nature", dispel_type="disease"))
    k["Scourge Pit Guard"] = trash(60, "Bone Blade", lambda t: stun_hit("Pommel", int(t * 1.1), 5),
                                   lambda t: hit_with("Hold the Pit", int(t * 0.8), {"armor": 160}, 3, on="buff"))
    k["Marrow Construct"] = trash(60, "Bone Fist", lambda t: dmg("Grind", int(t * 1.35), cooldown=4),
                                  lambda t: dmg("Shrapnel", int(t * 0.7), cooldown=5, is_aoe=True))
    k["Bone Dust Swarm"] = trash(59, "Scour", lambda t: dmg("Cloud of Dust", int(t * 0.7), cooldown=4, is_aoe=True),
                                 lambda t: hit_with("Blinding Dust", int(t * 0.8), {"hit_rating": -14}, 2))
    k["Overseer Marrowgrim"] = boss(60, "physical", "Meat Hook", "Chain Lash", "Gut Punch", "Bone Shrapnel",
                                    [dmg("Hook and Haul", int(BH(60) * 1.8), cooldown=4),
                                     stun_hit("Slam the Cart", int(BH(60) * 1.1), 6)],
                                    extra=[hit_with("Bone Plating", int(BH(60) * 0.85), {"armor": 300}, 3, on="buff", cooldown=6)])
    k["The Ossifier"] = boss(60, "shadow", "Bone Bolt", "Ossify", "Shatter the Marrow", "Bone Storm",
                             [dmg("Calcify", int(BH(60) * 1.8), cooldown=4, school="shadow"),
                              dot("Marrow Rot", int(BH(60) * 0.5), 5, 4, school="shadow", dispel_type="curse")],
                             extra=[hit_with("Bone Armour", int(BH(60) * 0.85), {"armor": 300}, 4, school="shadow",
                                             on="buff", cooldown=5)])
    return k


#: boss -> [(item, slot, suffix, (a|w, type) or None, stat template)], four each, spread over every type
POOLS = {
    "Broodlord Szarak": [
        ("Szarak's Carapace", "chest", "of the Champion", ("a", "plate"), "str_physical"),
        ("Burrowlord's Grips", "hands", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Pincer of the Brood", "main_hand", "of the Tiger", ("w", "axe_1h"), "agi_physical"),
        ("Egg-Sac Shawl", "back", "of the Prophet", None, "spi_healer")],
    "The Silken Bride": [
        ("Bride's Silken Robes", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Webwalker Treads", "feet", "of the Hunt", ("a", "mail"), "agi_int_hybrid"),
        ("Venom-Sac Wand", "ranged", "of the Invoker", ("w", "wand"), "int_caster"),
        ("Silk-Bound Girdle", "waist", "of the Gorilla", ("a", "plate"), "str_int_hybrid")],
    "The Weeper": [
        ("Veil of the Weeper", "head", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Tearstained Leggings", "legs", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Sorrow's Edge", "main_hand", "of the Sorcerer", ("w", "dagger"), "int_caster"),
        ("Damp-Rusted Pauldrons", "shoulder", "of the Defender", ("a", "plate"), "str_physical")],
    "The Drowned Hermit": [
        ("Hermit's Oar", "main_hand", "of the Bear", ("w", "staff"), "agi_physical"),
        ("Netcaster's Hauberk", "chest", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Silt-Soaked Bracers", "wrist", "of the Prophet", ("a", "leather"), "spi_healer"),
        ("Drowned Man's Signet", "ring", "of the Gladiator", None, "str_physical")],
    "Sexton Hollowell": [
        ("Sexton's Spade", "main_hand", "of the Bear", ("w", "polearm"), "str_physical"),
        ("Gravedigger's Coat", "chest", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Crypt-Key Girdle", "waist", "of the Owl", ("a", "mail"), "spi_healer"),
        ("Marris Family Cloak", "back", "of the Sorcerer", None, "int_caster")],
    "The Bone Choir": [
        ("Choirmaster's Mantle", "shoulder", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Hymnal of the Dead", "off_hand", "of the Physician", ("w", "tome"), "spi_healer"),
        ("Dirge-Sung Gauntlets", "hands", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Requiem Chain", "neck", "of the Hunt", None, "agi_physical")],
    "Overseer Marrowgrim": [
        ("Overseer's Meat Hook", "main_hand", "of the Vanquisher", ("w", "axe_2h"), "str_physical"),
        ("Bone-Plated Legguards", "legs", "of the Defender", ("a", "plate"), "str_physical"),
        ("Miner's Marrow Boots", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Pit Boss's Bulwark", "off_hand", "of the Defender", ("w", "shield"), "str_physical")],
    "The Ossifier": [
        ("Ossifier's Bone Staff", "main_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Calcified Robes", "chest", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Marrow-Etched Coif", "head", "of the Owl", ("a", "mail"), "agi_int_hybrid"),
        ("Bonecaster's Band", "ring", "of the Invoker", None, "int_caster")],
}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows, moved = {}, [], 0
    for b, items in POOLS.items():
        ilvl = ROSTER[b][2] + 2
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
            d["item_id"] = "plc_" + kit_slug(name)
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:
                fit_to_curve(d)
                moved += 1
            built.append(d)
            rows.append((name, slot, "weapon" if typ and typ[0] == "w" else "armor", typ[1] if typ else None,
                         template))
        out[b] = built
    return out, rows, moved


def check(k, loot):
    bad = []
    if set(k) != set(ROSTER):
        bad.append(f"kits and roster differ: {sorted(set(k) ^ set(ROSTER))}")
    if set(POOLS) != BOSSES:
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ BOSSES)}")
    for cave in PC.CAVES:
        placed = set(PC.BOSSES[cave]) if PC.BOSSES[cave] else None
        ours = {n for n in BOSSES if ROSTER[n][5] == cave}
        if placed is not None and placed != ours:
            bad.append(f"{cave}: bosses on the map {sorted(placed)} differ from the roster {sorted(ours)}")
        lo, hi = ZONE_LEVELS[cave]
        for n, r in ROSTER.items():
            if r[5] == cave and not (lo <= r[1] and r[2] <= hi):
                bad.append(f"{n} ({r[1]}-{r[2]}) sits outside {cave} {lo}-{hi}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, (_t, lo, hi, _m, sprite, _c) in ROSTER.items():
        prior = existing.get(name)
        if prior and prior.get("level_range") != [lo, hi]:
            bad.append(f"{name} already exists elsewhere at {prior.get('level_range')}; names never repeat")
        if not (ROOT / "assets/creatures" / f"{sprite}.png").exists():
            bad.append(f"{name}'s sprite {sprite} is not on disk")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    return bad


def main():
    for cave in PC.CAVES:              # the map places the bosses; build it once so the check can read them
        PC.build(cave)
    k = kits()
    loot, rows, moved = build_loot()
    bad = check(k, loot)
    problems = loot_audit(rows)
    if bad or problems:
        print("FAILED - fix the data, not the check:")
        for b in bad + problems:
            print("  -", b)
        return 1
    creatures = {}
    for name, (template, lo, hi, mult, _s, _c) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    for cave in PC.CAVES:
        caves = enc["zones"].setdefault(PC.PARENT[cave], {}).setdefault("caves", {})
        caves[cave] = {"name": cave, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items() if r[5] == cave}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    indent, newline = _detect_format(lv, raw)
    lv["zones"].update(ZONE_LEVELS)
    LEVELS.write_text(json.dumps(lv, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")
    out = {"_notes": ("Boss loot for the Plaguelands' four caves (53-60). ONE item per kill from the boss's four; "
                      "item_level = boss level + 2. Hand-authored in tools/build_plaguelands_caves_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(BOSSES)} bosses) in {len(PC.CAVES)} caves; "
          f"{sum(len(v) for v in loot.values())} boss items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
