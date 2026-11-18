#!/usr/bin/env python3
"""Azshara's two caves: creatures, kits, encounter tables, zone levels and boss loot. Idempotent.

    PYTHONPATH=. python3 tools/build_azshara_caves_content.py

The maps are tools/handbuilt_azshara_caves.py (its docstring has the shapes). Caves, not dungeons: one or two bosses
pinned by the map, trash rolled from the cave's own table under its parent map's "caves", no set packs. Kyle picked
both names and both rosters on 18 Nov 2026.

  HALDARR DEN        54-56  Haldarr's satyrs, their felhounds, and the Highborne dead they bound
                            Haldarr the Hornlord; the Bound Magister (optional)
  HETAERA'S GROTTO   56-58  the naga coming up from Zin-Azshari, and the hydra's brood
                            Tide-Priestess Sel'thira; Hetaera, the hydra mother (optional)

THE NUMBERS are the Plaguelands caves' (the game's 52-58 dungeons, measured 16 Nov 2026): a boss's basic hit 10L - 200,
trash 4L - 10, boss health 2.5 for the one at the end and 2.3 for the optional one. Every boss carries something
dangerous (Kyle: "make sure bosses are not just debuffing"), and tools/qa_dungeon_boss_turns.py holds them to it.

THE SPRITES are Kyle's Azshara creature sheet (sheet 5, sliced 17 Nov 2026 to assets/creatures/_src/azshara/); this
script copies the ones it uses into assets/creatures/ and creature_sprites.py names them. Haldarr borrows Felwood's
satyr lord and Hetaera a sea serpent until they get art of their own.

LOOT. Four items a boss, item level = the boss's level + 2 (the caves' lift), spread over every armour type and the six
stat templates. No trinkets (every trinket from 50 has to do something).
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, loot_audit)
from tools.build_scarlet_monastery_content import opener, stun_hit, heal, hit_with  # noqa: E402
from tools import handbuilt_azshara_caves as AC  # noqa: E402

LOOT = ROOT / "data/loot/azshara_caves_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
SRC = ROOT / "assets/creatures/_src/azshara"
D_, G_ = AC.DEN, AC.GROTTO
ZONE_LEVELS = {D_: [54, 56], G_: [56, 58]}


def BH(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


#: name -> (template, lo, hi, boss multiplier or None, sprite, cave)
ROSTER = {
    "Haldarr Cursed":            ("humanoid_rogue",   54, 55, None, "az_satyr_cursed", D_),
    "Haldarr Fel-Sorcerer":      ("demon_caster",     55, 56, None, "az_satyr_sorcerer", D_),
    "Haldarr Houndmaster":       ("humanoid_warrior", 55, 56, None, "az_satyr_houndmaster", D_),
    "Crystalback Felhound":      ("demon_hound",      54, 55, None, "az_felhound", D_),
    "Bound Highborne Servant":   ("undead_caster",    54, 56, None, "az_ghost_handmaiden", D_),
    "Haldarr the Hornlord":      ("humanoid_warrior", 56, 56, 2.5, "fw_satyr_lord", D_),
    "The Bound Magister":        ("undead_caster",    56, 56, 2.3, "az_ghost_arcanist", D_),
    "Clutch Tidehunter":         ("humanoid_warrior", 56, 57, None, "az_naga_tidehunter", G_),
    "Clutch Siren":              ("humanoid_caster",  56, 57, None, "az_naga_siren", G_),
    "Clutch Brute":              ("humanoid_warrior", 57, 58, None, "az_naga_brute", G_),
    "Hetaera's Brood":           ("beast_fast",       56, 57, None, "az_serpent_hatchling", G_),
    "Barnacled Shorecrab":       ("aquatic_basic",    56, 57, None, "az_shore_crab", G_),
    "Tide-Priestess Sel'thira":  ("humanoid_caster",  58, 58, 2.5, "az_naga_sea_witch", G_),
    "Hetaera":                   ("beast_large",      58, 58, 2.3, "serpent_2", G_),
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
    # ---- Haldarr Den (54-56)
    k["Haldarr Cursed"] = trash(55, "Hooked Blade", lambda t: dmg("Gore", int(t * 1.3), cooldown=4),
                                lambda t: dot("Cursed Cut", int(t * 0.3), 4, 3, school="shadow", dispel_type="curse"))
    k["Haldarr Fel-Sorcerer"] = trash(56, "Fel Bolt", lambda t: dmg("Fel Rain", int(t * 0.7), cooldown=4,
                                                                    school="fire", is_aoe=True),
                                      lambda t: hit_with("Hex of Weakness", int(t * 0.8), {"attack_power": -60}, 3,
                                                         school="shadow"), school="fire")
    k["Haldarr Houndmaster"] = trash(56, "Whip Crack", lambda t: stun_hit("Chain Snare", int(t * 1.1), 5),
                                     lambda t: hit_with("Set the Hounds", int(t * 0.8), {"attack_power": 80}, 3,
                                                        on="buff"))
    k["Crystalback Felhound"] = trash(55, "Bite", lambda t: hit_with("Mana Bite", int(t * 0.8), {"intellect": -20}, 3),
                                      lambda t: dmg("Crystal Spines", int(t * 0.7), cooldown=5, is_aoe=True))
    k["Bound Highborne Servant"] = trash(56, "Cold Hand", lambda t: dmg("Beg", int(t * 0.7), cooldown=4,
                                                                         school="shadow", is_aoe=True),
                                         lambda t: dot("The Chain's Weight", int(t * 0.28), 4, 3, school="shadow",
                                                       dispel_type="curse"), school="shadow")
    k["Haldarr the Hornlord"] = boss(56, "physical", "Horned Blade", "Gore", "Trample", "Fel Fire Ring",
                                     [dmg("Lord of the Roots", int(BH(56) * 1.8), cooldown=4),
                                      stun_hit("Pinned to the Tree", int(BH(56) * 1.1), 6)])
    k["The Bound Magister"] = boss(56, "arcane", "Arcane Lash", "Shackled Bolt", "Ten Thousand Years", "Arcane Storm",
                                   [dmg("Break the Chain", int(BH(56) * 1.8), cooldown=4, school="arcane"),
                                    dot("Madness of the Bound", int(BH(56) * 0.5), 5, 4, school="arcane",
                                        dispel_type="magic")],
                                   extra=[heal("Drink the Leyline", int(BH(56) * 1.2), 6, school="arcane")])
    # ---- Hetaera's Grotto (56-58)
    k["Clutch Tidehunter"] = trash(57, "Trident", lambda t: stun_hit("Net", int(t * 1.1), 5),
                                   lambda t: dmg("Impale", int(t * 1.3), cooldown=4))
    k["Clutch Siren"] = trash(57, "Frost Bolt", lambda t: hit_with("Siren Song", int(t * 0.8), {"haste": -12}, 3,
                                                                    school="frost"),
                              lambda t: dmg("Cold Wave", int(t * 0.7), cooldown=4, school="frost", is_aoe=True),
                              school="frost")
    k["Clutch Brute"] = trash(58, "Stone Club", lambda t: dmg("Crush", int(t * 1.35), cooldown=4),
                              lambda t: hit_with("Barnacle Hide", int(t * 0.8), {"armor": 160}, 3, on="buff"))
    k["Hetaera's Brood"] = trash(57, "Snap", lambda t: dot("Venom Bite", int(t * 0.3), 4, 3, school="nature",
                                                              dispel_type="poison"),
                                 lambda t: dmg("Writhe", int(t * 0.7), cooldown=4, is_aoe=True))
    k["Barnacled Shorecrab"] = trash(57, "Pinch", lambda t: hit_with("Crack the Shell", int(t * 0.8), {"armor": -150}, 3),
                                     lambda t: dmg("Claw Sweep", int(t * 0.7), cooldown=5, is_aoe=True))
    k["Tide-Priestess Sel'thira"] = boss(58, "frost", "Tide Bolt", "Riptide", "Crushing Depths", "The Sea Comes In",
                                         [dmg("Wave of Zin-Azshari", int(BH(58) * 1.0), cooldown=5, school="frost",
                                              is_aoe=True),
                                          stun_hit("Drag Below", int(BH(58) * 1.1), 6, school="frost")],
                                         extra=[heal("Tidal Mending", int(BH(58) * 1.2), 6, school="nature")])
    k["Hetaera"] = boss(58, "nature", "Many Jaws", "Hydra Bite", "Coil and Crush", "Venom Spray",
                        [dmg("Every Head at Once", int(BH(58) * 1.8), cooldown=4),
                         dot("Hydra Venom", int(BH(58) * 0.5), 5, 4, school="nature", dispel_type="poison")],
                        aoe=True)
    return k


#: boss -> [(item, slot, suffix, (a|w, type) or None, stat template)], four each, spread over every type
POOLS = {
    "Haldarr the Hornlord": [
        ("Hornlord's Breastplate", "chest", "of the Champion", ("a", "plate"), "str_physical"),
        ("Rootwarren Stalkers", "feet", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Haldarr's Hooked Glaive", "main_hand", "of the Tiger", ("w", "polearm"), "agi_physical"),
        ("Cursed Bark Cloak", "back", "of the Prophet", None, "spi_healer")],
    "The Bound Magister": [
        ("Magister's Chained Robes", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Leyshackle Gauntlets", "hands", "of the Hunt", ("a", "mail"), "agi_int_hybrid"),
        ("Ten Thousand Year Rod", "ranged", "of the Invoker", ("w", "wand"), "int_caster"),
        ("Broken Fetter Girdle", "waist", "of the Gorilla", ("a", "plate"), "str_int_hybrid")],
    "Tide-Priestess Sel'thira": [
        ("Sel'thira's Coral Crown", "head", "of the Physician", ("a", "cloth"), "spi_healer"),
        ("Undertow Leggings", "legs", "of the Wolf", ("a", "leather"), "agi_int_hybrid"),
        ("Tidecaller's Trident", "main_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Pearl-Scale Spaulders", "shoulder", "of the Owl", ("a", "mail"), "spi_healer")],
    "Hetaera": [
        ("Hydra-Tooth Cleaver", "main_hand", "of the Bear", ("w", "axe_2h"), "str_physical"),
        ("Brood-Mother's Scale Hauberk", "chest", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Shed-Skin Bracers", "wrist", "of the Prophet", ("a", "leather"), "spi_healer"),
        ("Many-Headed Signet", "ring", "of the Gladiator", None, "str_physical")],
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
            d["item_id"] = "azc_" + kit_slug(name)
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
    for cave in AC.CAVES:
        placed = set(AC.BOSSES[cave])
        ours = {n for n in BOSSES if ROSTER[n][5] == cave}
        if placed != ours:
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
        if not ((ROOT / "assets/creatures" / f"{sprite}.png").exists() or (SRC / f"{sprite}.png").exists()):
            bad.append(f"{name}'s sprite {sprite} is not on disk")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    import creature_sprites as CS
    for name, r in ROSTER.items():
        if CS.sprite_for(name, r[0]) != r[4]:
            bad.append(f"creature_sprites.py draws {name} as {CS.sprite_for(name, r[0])}, not {r[4]}")
    return bad


def install_sprites():
    """Copy the sliced Azshara creature sprites this cave pass uses into assets/creatures/."""
    n = 0
    for (_t, _lo, _hi, _m, sprite, _c) in ROSTER.values():
        src, dst = SRC / f"{sprite}.png", ROOT / "assets/creatures" / f"{sprite}.png"
        if src.exists() and not dst.exists():
            shutil.copyfile(src, dst)
            n += 1
    return n


def main():
    for cave in AC.CAVES:              # the map places the bosses; build it once so the check can read them
        AC.build(cave)
    copied = install_sprites()
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
    for cave in AC.CAVES:
        caves = enc["zones"].setdefault(AC.PARENT[cave], {}).setdefault("caves", {})
        caves[cave] = {"name": cave, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items() if r[5] == cave}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    indent, newline = _detect_format(lv, raw)
    lv["zones"].update(ZONE_LEVELS)
    LEVELS.write_text(json.dumps(lv, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")
    out = {"_notes": ("Boss loot for Azshara's two caves (54-58). ONE item per kill from the boss's four; "
                      "item_level = boss level + 2. Hand-authored in tools/build_azshara_caves_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(BOSSES)} bosses) in {len(AC.CAVES)} caves; {copied} sprites installed; "
          f"{sum(len(v) for v in loot.values())} boss items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
