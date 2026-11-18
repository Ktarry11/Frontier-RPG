#!/usr/bin/env python3
"""The Rotroot Deeps: creatures, fighting kits, encounter table, zone levels, boss loot and the Timbermaw's pay.
Idempotent.

    PYTHONPATH=. python3 tools/build_rotroot_deeps_content.py

The map is tools/handbuilt_rotroot_deeps.py (its docstring has the rooms). Under Timbermaw Hold, 55-58, five bosses,
Kyle's names and art (18 Nov 2026: "The Rotroot Deeps", "Keep all five"). The rot that took the Deadwood came up from
here: the Hold's own dead first, then the satyrs who tend it, then what it grew.

    OLD MOSSJAW              55  the chieftain the rot took first, on his bier; calls his dead clan up round him
    MOTHER SPOREHEART        56  the fungus mother on her island; breeds spore clouds, feeds on the garden
    ROTWARDEN KAZ'THUL       57  the satyr who keeps the cages; cages a player, opens the cages on the party
    THORNBLIGHT              57  the Hold's own roots, gone bad; entangles, hardens its bark, then the thorn storm
    XAVRAS THE GLOOMTENDER   58  the satyr who planted it; calls her satyrs, and the Rot Below at the end

THE NUMBERS are the Plaguelands dungeons' (the game's 54-60 band, tools/build_plaguelands_dungeons_content.py): boss
basic 10L - 200, trash basic 4L - 10, boss health 2.5 a boss and 2.8 the last. Every boss carries something dangerous
(tools/qa_dungeon_boss_turns.py).

LOOT. Four items a boss, item level = the boss's level + 3 (a dungeon's lift), spread over every armour type and the
six stat templates. Xavras also rolls her two named epics at 5% (tools/epic_table.py).

THE TIMBERMAW PAY for it: 75 a boss (factions.json dungeon_rep), and the trash 10 a kill up to Revered. Both are also
written in tools/build_timbermaw_hold.py's FACTION, so a rebuild of the Hold keeps them.
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools.build_plaguelands_dungeons_content import (  # noqa: E402
    opener, phase, stun_hit, shell, heal, last_gasp, hit_with)
from tools import handbuilt_rotroot_deeps as RD  # noqa: E402

LOOT = ROOT / "data/loot/rotroot_deeps_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
FACTIONS = ROOT / "data/factions/factions.json"
SRC = ROOT / "assets/creatures/_src/azshara"
NAME = RD.NAME
PARENT = "Timbermaw Hold"
ZONE_LEVELS = {NAME: [55, 58]}
FID = "timbermaw_hold"


def B(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


#: name -> (template, lo, hi, boss multiplier or None, sprite)
ROSTER = {
    "Rotroot Furbolg":        ("humanoid_warrior",  55, 56, None, "az_rot_furbolg"),
    "Rotroot Mystic":         ("humanoid_caster",   55, 56, None, "az_rot_shaman"),
    "Rotroot Mauler":         ("beast_large",       55, 57, None, "az_rot_beast"),
    "Drifting Sporecloud":    ("elemental_caster",  55, 57, None, "az_spore_cloud"),
    "Satyr Rot-Tender":       ("humanoid_caster",   56, 58, None, "az_rot_tender"),
    "Gloomhollow Satyr":      ("humanoid_rogue",    57, 58, None, "fw_satyr_shadowstalker"),
    "Rootbound Horror":       ("elemental_bruiser", 57, 58, None, "az_root_horror"),
    "Rotroot Bodyguard":      ("humanoid_warrior",  57, 58, None, "fr_elite_guard"),
    "Old Mossjaw":            ("humanoid_warrior",  55, 55, 2.5, "fr_boss_mossjaw"),
    "Mother Sporeheart":      ("elemental_caster",  56, 56, 2.5, "fr_boss_sporeheart"),
    "Rotwarden Kaz'thul":     ("humanoid_caster",   57, 57, 2.5, "fr_boss_kazthul"),
    "Thornblight":            ("elemental_bruiser", 57, 57, 2.5, "fr_boss_thornblight"),
    "Xavras the Gloomtender": ("demon_caster",      58, 58, 2.8, "fr_boss_xavras"),
}
BOSSES = [n for n, r in ROSTER.items() if r[3]]
TRASH = [n for n, r in ROSTER.items() if not r[3]]
FINAL = "Xavras the Gloomtender"


def summon(name, creature, cooldown, max_alive, max_casts):
    return dict(name=name, kind="summon", amount=0, cooldown=cooldown, mana_cost=0,
                summon={"name": creature, "template": ROSTER[creature][0], "kit": kit_slug(creature),
                        "count": 1, "level_offset": -1, "max_alive": max_alive, "max_casts": max_casts})


def boss_kit(level, school, basic, second, heavy, spread, mechanic, phase_name, *, signature, aoe=True, extra=()):
    b = B(level)
    kit = [opener(basic, b, school), dmg(second, int(b * 0.88), cooldown=4, school=school),
           dmg(heavy, int(b * 1.3), cooldown=4, school=school)]
    kit.append(dmg(spread, int(b * 0.68), cooldown=5, school=school, is_aoe=True) if aoe
               else dot(spread, int(b * 0.36), 5, 4, school=school))
    if mechanic:
        kit.append(mechanic)
    kit.extend(extra)
    kit.extend(signature)
    kit.append(phase(phase_name, level, school))
    return kit


def kits():
    k = {}
    t = T
    # ---- trash: the Hold's risen dead, the garden, the satyrs and what they grew
    k["Rotroot Furbolg"] = [dmg("Rotten Claw", t(55)), dmg("Maul", int(t(55) * 0.86), cooldown=3),
                            dot("Rot Fever", int(t(55) * 0.24), 4, 3, school="nature", dispel_type="disease")]
    k["Rotroot Mystic"] = [dmg("Fel Totem Bolt", t(56), school="nature"), heal("Rot Mending", int(t(56) * 1.4)),
                           dot("Grave Moss", int(t(56) * 0.26), 4, 3, school="nature", dispel_type="magic")]
    k["Rotroot Mauler"] = [dmg("Gore", t(56)), dmg("Trample", int(t(56) * 0.64), cooldown=5, is_aoe=True),
                           debuff("Mossy Hide", 5, 3, {"agility": -30})]
    k["Drifting Sporecloud"] = [dmg("Spore Puff", t(56), school="nature"),
                                dmg("Burst", int(t(56) * 0.64), cooldown=5, school="nature", is_aoe=True),
                                dot("Choking Spores", int(t(56) * 0.24), 4, 3, school="nature",
                                    dispel_type="poison")]
    k["Satyr Rot-Tender"] = [dmg("Fel Bolt", t(57), school="fire"), heal("Tend the Rot", int(t(57) * 1.4)),
                             debuff("Wither", 5, 3, {"haste": -15}, school="shadow")]
    k["Gloomhollow Satyr"] = [dmg("Hooked Blade", t(58)), dmg("Backstab", int(t(58) * 1.1), cooldown=4),
                              dot("Gloomrot Poison", int(t(58) * 0.24), 4, 3, school="nature",
                                  dispel_type="poison")]
    k["Rootbound Horror"] = [dmg("Root Lash", t(58) + 10),
                             dmg("Thrash", int(t(58) * 0.64), cooldown=5, is_aoe=True),
                             stun_hit("Grasping Roots", int(t(58) * 0.6), cooldown=6, school="nature")]
    k["Rotroot Bodyguard"] = [dmg("Cleave", t(58)), dmg("Shield Bash", int(t(58) * 0.86), cooldown=3),
                              buff("Bark Shield", 6, 3, {"armor": 240})]
    # ---- the bosses
    k["Old Mossjaw"] = boss_kit(                 # the chieftain on his bier: calls his dead clan up round him
        55, "physical", "Chieftain's Maul", "Rotten Bite", "Grave-Rend", "Grave-Roar",
        summon("Wake the Clan", "Rotroot Furbolg", 4, 2, 4), "The Last Chieftain",
        signature=[dmg("Bier-Breaker", int(B(55) * 1.9), cooldown=5),
                   last_gasp("Roar of the Fallen", 55)])
    k["Mother Sporeheart"] = boss_kit(           # breeds spore clouds and feeds on her garden
        56, "nature", "Spore Lash", "Fungal Whip", "Crushing Cap", "Spore Burst",
        summon("Seed the Air", "Drifting Sporecloud", 4, 3, 6), "Full Bloom",
        extra=[heal("Feed on the Garden", int(B(56) * 1.1), cooldown=6, school="nature")],
        signature=[dot("Mycelial Rot", int(B(56) * 0.5), 5, 4, school="nature", dispel_type="disease"),
                   dmg("Sporestorm", int(B(56) * 1.1), cooldown=6, school="nature", is_aoe=True)])
    k["Rotwarden Kaz'thul"] = boss_kit(          # cages a player, then opens the cages on the party
        57, "shadow", "Warden's Lash", "Chain Whip", "Fel Brand", "Rot Breath",
        stun_hit("Caged", int(B(57) * 0.7), cooldown=6, school="shadow"), "Keys to Every Cage",
        extra=[summon("Open the Cages", "Rootbound Horror", 5, 2, 4)],
        signature=[dmg("The Warden's Due", int(B(57) * 1.9), cooldown=5, school="shadow")])
    k["Thornblight"] = boss_kit(                 # the Hold's own roots, gone bad
        57, "nature", "Root Slam", "Thorn Lash", "Heartwood Crush", "Bramble Sweep",
        stun_hit("Entangling Roots", int(B(57) * 0.6), cooldown=6, school="nature"), "Rot to the Core",
        extra=[shell("Blighted Bark", 6, 3, int(B(57) * 1.2), school="nature")],
        signature=[dmg("Thorn Storm", int(B(57) * 1.2), cooldown=6, school="nature", is_aoe=True),
                   last_gasp("The Roof Comes Down", 57, "nature")])
    k[FINAL] = boss_kit(                         # the satyr who planted the rot under the Hold
        58, "shadow", "Gloom Bolt", "Rotting Touch", "Fel Blight", "Gloomwave",
        summon("Tenders, to Me", "Gloomhollow Satyr", 4, 2, 5), "The Garden Wakes",
        extra=[hit_with("Seed of Rot", int(B(58) * 0.7), {"healing_power": -60, "haste": -10}, 3, school="shadow",
                        cooldown=5)],
        signature=[dmg("The Rot Below", int(B(58) * 2.0), cooldown=6, school="shadow"),
                   dot("Gloomrot", int(B(58) * 0.5), 5, 4, school="shadow", dispel_type="magic"),
                   last_gasp("Fel Tide", 58, "fire", mult=1.7)])
    return k


#: boss -> [(item, slot, suffix, (a|w, type) or None, stat template)], four each, spread over every type
POOLS = {
    "Old Mossjaw": [
        ("Mossjaw's Burial Mantle", "shoulder", "of the Bear", ("a", "plate"), "str_physical"),
        ("Bier-Bearer's Leggings", "legs", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Chieftain's Grave Totem", "off_hand", "of the Prophet", ("w", "totem"), "spi_healer"),
        ("Clan-Ring of the Hold", "ring", "of the Sorcerer", None, "int_caster")],
    "Mother Sporeheart": [
        ("Sporeheart's Cap", "head", "of the Owl", ("a", "cloth"), "spi_healer"),
        ("Mycelium Wraps", "wrist", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Fungal Bloom Staff", "main_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Gardener's Rot-Boots", "feet", "of the Gorilla", ("a", "plate"), "str_int_hybrid")],
    "Rotwarden Kaz'thul": [
        ("Warden's Keyring Belt", "waist", "of the Tiger", ("a", "leather"), "agi_physical"),
        ("Cage-Breaker Gauntlets", "hands", "of the Champion", ("a", "plate"), "str_physical"),
        ("Kaz'thul's Hooked Glaive", "main_hand", "of the Hunt", ("w", "polearm"), "agi_physical"),
        ("Chainwhip Cloak", "back", "of the Invoker", None, "int_caster")],
    "Thornblight": [
        ("Heartwood Breastplate", "chest", "of the Bear", ("a", "plate"), "str_physical"),
        ("Rootbark Hauberk", "chest", "of the Prophet", ("a", "mail"), "spi_healer"),
        ("Thornwoven Robe", "chest", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Blighted Bramble Maul", "main_hand", "of the Gorilla", ("w", "mace_2h"), "str_int_hybrid")],
    FINAL: [
        ("Gloomtender's Shroud", "chest", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Xavras's Hoofguards", "feet", "of the Monkey", ("a", "mail"), "agi_physical"),
        ("Scythe of the Rot Below", "main_hand", "of the Champion", ("w", "axe_2h"), "str_physical"),
        ("Tender's Pruning Knife", "main_hand", "of the Physician", ("w", "dagger"), "spi_healer")],
}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows, moved = {}, [], 0
    for b, items in POOLS.items():
        ilvl = ROSTER[b][2] + 3
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
            d["item_id"] = "rrd_" + kit_slug(name)
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
    if set(POOLS) != set(BOSSES):
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ set(BOSSES))}")
    placed = set(RD.BOSSES)
    if placed != set(BOSSES):
        bad.append(f"bosses on the map {sorted(placed)} differ from the roster {sorted(BOSSES)}")
    on_map = {m for (_x, _y, m, _l) in [s for p in RD._trash() for s in p]}
    if on_map - set(TRASH):
        bad.append(f"trash on the map with no roster entry: {sorted(on_map - set(TRASH))}")
    from tools.build_timbermaw_hold import ROTROOT_TRASH
    if set(ROTROOT_TRASH) != set(TRASH):
        bad.append(f"build_timbermaw_hold.ROTROOT_TRASH differs from the roster's trash: "
                   f"{sorted(set(ROTROOT_TRASH) ^ set(TRASH))}")
    lo, hi = ZONE_LEVELS[NAME]
    for n, r in ROSTER.items():
        if not (lo <= r[1] and r[2] <= hi):
            bad.append(f"{n} ({r[1]}-{r[2]}) sits outside {NAME} {lo}-{hi}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, (_t, lo_, hi_, _m, sprite) in ROSTER.items():
        prior = existing.get(name)
        if prior and prior.get("level_range") != [lo_, hi_]:
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
    n = 0
    for (_t, _lo, _hi, _m, sprite) in ROSTER.values():
        src, dst = SRC / f"{sprite}.png", ROOT / "assets/creatures" / f"{sprite}.png"
        if src.exists() and not dst.exists():
            shutil.copyfile(src, dst)
            n += 1
    return n


def _write(path, data, raw):
    indent, newline = _detect_format(json.loads(raw), raw)     # read off the file as it was, before the edit
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")


def main():
    RD.build_rotroot()                  # the map places the bosses; build it once so the check can read them
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
    for name, (template, lo, hi, mult, _s) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    caves = enc["zones"].setdefault(PARENT, {"name": PARENT}).setdefault("caves", {})
    caves[NAME] = {"name": NAME, "creatures": {n: (0 if ROSTER[n][3] else 4) for n in ROSTER}}
    _write(ENCOUNTERS, enc, raw)

    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    lv["zones"].update(ZONE_LEVELS)
    _write(LEVELS, lv, raw)

    from tools.build_timbermaw_hold import FACTION
    raw = FACTIONS.read_text(encoding="utf-8")
    fd = json.loads(raw)
    rec = fd["factions"][FID]
    rec["dungeon_rep"] = json.loads(json.dumps(FACTION["dungeon_rep"]))
    rec["kill_rep"]["creatures"].update(FACTION["kill_rep"]["creatures"])
    _write(FACTIONS, fd, raw)

    out = {"_notes": ("Boss loot for the Rotroot Deeps (55-58), under Timbermaw Hold. ONE item per kill from the boss's "
                      "four; item_level = boss level + 3. Hand-authored in tools/build_rotroot_deeps_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(BOSSES)} bosses); {copied} sprites installed; "
          f"{sum(len(v) for v in loot.values())} boss items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
