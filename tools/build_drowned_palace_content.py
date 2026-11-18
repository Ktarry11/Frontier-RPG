#!/usr/bin/env python3
"""The Drowned Palace: creatures, fighting kits, encounter tables, zone levels and boss loot. Idempotent.

    PYTHONPATH=. python3 tools/build_drowned_palace_content.py

The maps are tools/handbuilt_drowned_palace.py (its docstring has the rooms and what each boss asks of a party). Kyle,
18 Nov 2026: "The Drowned Palace", "Naga up, ghosts down", "Sunken palace, dry vault". 59-60, six bosses over two
floors, the naga's flooded halls and then the Highborne dead's vault under them.

    THE FLOODED HALLS  Lady Ssiriss 59 | The Drowned Chamberlain 59 | Tidelord Vashj'ren 60 (the floor's last)
    THE QUEEN'S VAULT  The Moonguard Revenant 60 | Magistrix Elaria the Undying 60 | Echo of the Queen 60 (the last)

THE NUMBERS are the Plaguelands dungeons' (the 54-60 band): boss basic 10L - 200, trash basic 4L - 10, boss health
2.5 a boss and 2.8 the last of a floor. Every boss carries something dangerous (tools/qa_dungeon_boss_turns.py).

LOOT. Four items a boss, item level = boss level + 3, spread over every armour type and the six stat templates. The
Echo of the Queen rolls her two named epics at 5% (tools/epic_table.py).

REPUTATION waits on the Sunreach Conclave (the Azshara content pass): the magisters are the ones who'd pay for it.
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
from tools import handbuilt_drowned_palace as DP  # noqa: E402

LOOT = ROOT / "data/loot/drowned_palace_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
SRC = ROOT / "assets/creatures/_src/azshara"
H, V = DP.HALLS, DP.VAULT
PARENT = DP.REGION
ZONE_LEVELS = {H: [59, 60], V: [59, 60]}


def B(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


#: name -> (template, lo, hi, boss multiplier or None, sprite, floor)
ROSTER = {
    # ---- the Flooded Halls: the naga, and the Highborne they found down here
    "Zin-Azshari Myrmidon":     ("humanoid_warrior", 59, 60, None, "az_naga_brute", H),
    "Zin-Azshari Royal Guard":  ("humanoid_warrior", 59, 60, None, "az_naga_royal_guard", H),
    "Zin-Azshari Siren":        ("humanoid_caster",  59, 60, None, "az_naga_siren", H),
    "Zin-Azshari Tidecaller":   ("humanoid_caster",  59, 60, None, "az_naga_sea_witch", H),
    "Hydra Spawn":              ("beast_fast",       59, 60, None, "az_serpent_hatchling", H),
    "Drowned Highborne":        ("undead_caster",    59, 60, None, "az_ghost_noble", H),
    "Lady Ssiriss":             ("humanoid_caster",  59, 59, 2.5, "vz_boss_ssiriss", H),
    "The Drowned Chamberlain":  ("undead_caster",    59, 59, 2.5, "vz_boss_chamberlain", H),
    "Tidelord Vashj'ren":       ("humanoid_warrior", 60, 60, 2.8, "vz_boss_vashjren", H),
    # ---- the Queen's Vault: the Highborne dead who still keep it for her
    "Moonguard Sentinel":       ("undead_warrior",   59, 60, None, "az_ghost_guard", V),
    "Highborne Spellbinder":    ("undead_caster",    59, 60, None, "az_ghost_arcanist", V),
    "Queen's Handmaiden":       ("undead_caster",    59, 60, None, "az_ghost_handmaiden", V),
    "Tormented Courtier":       ("undead_basic",     59, 60, None, "az_ghost_tormented", V),
    "Vault Hound":              ("undead_beast",     59, 60, None, "az_ghost_hound", V),
    "Arcane Sentry":            ("elemental_bruiser", 59, 60, None, "az_arcane_construct", V),
    "Mana Wyrm":                ("elemental_caster", 59, 60, None, "az_mana_wyrm_leader", V),
    "Ley Beast":                ("beast_large",      59, 60, None, "az_ley_beast", V),
    "The Moonguard Revenant":   ("undead_warrior",   60, 60, 2.5, "vz_boss_revenant", V),
    "Magistrix Elaria the Undying": ("undead_caster", 60, 60, 2.5, "vz_boss_elaria", V),
    "Echo of the Queen":        ("elemental_caster", 60, 60, 2.8, "vz_boss_echo_queen", V),
}
BOSSES = [n for n, r in ROSTER.items() if r[3]]
FINAL = "Echo of the Queen"


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
    # ---- the halls' trash
    k["Zin-Azshari Myrmidon"] = [dmg("Trident Thrust", t(60)), dmg("Sweeping Tail", int(t(60) * 0.64), cooldown=5,
                                                                    is_aoe=True), buff("Coral Hide", 6, 3, {"armor": 240})]
    k["Zin-Azshari Royal Guard"] = [dmg("Halberd Cleave", t(60)), dmg("Shield Slam", int(t(60) * 0.86), cooldown=3),
                                    stun_hit("Pin to the Floor", int(t(60) * 0.6), cooldown=6)]
    k["Zin-Azshari Siren"] = [dmg("Frost Bolt", t(60), school="frost"),
                              dmg("Siren's Wail", int(t(60) * 0.64), cooldown=5, school="frost", is_aoe=True),
                              debuff("Enthral", 5, 3, {"haste": -15}, school="arcane")]
    k["Zin-Azshari Tidecaller"] = [dmg("Tidal Bolt", t(60), school="frost"), heal("Healing Tide", int(t(60) * 1.4)),
                                   dot("Brine", int(t(60) * 0.26), 4, 3, school="frost", dispel_type="magic")]
    k["Hydra Spawn"] = [dmg("Snapping Jaws", t(59)), dmg("Many Bites", int(t(59) * 0.86), cooldown=3),
                        dot("Hydra Venom", int(t(59) * 0.24), 4, 3, school="nature", dispel_type="poison")]
    k["Drowned Highborne"] = [dmg("Drowned Touch", t(60), school="frost"),
                              dot("Lungful of Sea", int(t(60) * 0.26), 4, 3, school="frost", dispel_type="curse"),
                              debuff("Ten Thousand Years", 5, 3, {"intellect": -40}, school="shadow")]
    # ---- the vault's trash
    k["Moonguard Sentinel"] = [dmg("Moonblade", t(60)), dmg("Shield Bash", int(t(60) * 0.86), cooldown=3),
                               buff("Shield Wall", 6, 3, {"armor": 240})]
    k["Highborne Spellbinder"] = [dmg("Arcane Bolt", t(60), school="arcane"),
                                  dmg("Arcane Explosion", int(t(60) * 0.64), cooldown=5, school="arcane", is_aoe=True),
                                  debuff("Spellbind", 5, 3, {"haste": -15}, school="arcane")]
    k["Queen's Handmaiden"] = [dmg("Chilling Touch", t(60), school="frost"),
                               heal("Mend the Court", int(t(60) * 1.4)),
                               dot("Courtly Curse", int(t(60) * 0.26), 4, 3, school="shadow", dispel_type="curse")]
    k["Tormented Courtier"] = [dmg("Wailing Grasp", t(59), school="shadow"),
                               dmg("Lament", int(t(59) * 0.86), cooldown=3, school="shadow"),
                               debuff("Despair", 5, 3, {"haste": -10}, school="shadow")]
    k["Vault Hound"] = [dmg("Spectral Bite", t(59), school="shadow"), dmg("Lunge", int(t(59) * 0.86), cooldown=3),
                        debuff("Hamstring", 5, 3, {"agility": -30})]
    k["Arcane Sentry"] = [dmg("Crystal Fist", t(60) + 10, school="arcane"),
                          dmg("Arcane Pulse", int(t(60) * 0.64), cooldown=5, school="arcane", is_aoe=True),
                          stun_hit("Mana Lock", int(t(60) * 0.6), cooldown=6, school="arcane")]
    k["Mana Wyrm"] = [dmg("Arcane Bite", t(59), school="arcane"),
                      dmg("Mana Spark", int(t(59) * 0.64), cooldown=5, school="arcane", is_aoe=True),
                      debuff("Drain Mana", 5, 3, {"intellect": -40}, school="arcane")]
    k["Ley Beast"] = [dmg("Leyline Maul", t(60), school="arcane"), dmg("Trample", int(t(60) * 0.86), cooldown=3),
                      buff("Ley Surge", 6, 3, {"attack_power": 50})]
    # ---- the bosses
    k["Lady Ssiriss"] = boss_kit(                # the siren queen on her dais: charms and drowns
        59, "frost", "Four-Armed Lash", "Pearl Bolt", "Crushing Depths", "Siren Song",
        stun_hit("Enthralling Song", int(B(59) * 0.7), cooldown=6, school="arcane"), "Queen of the Court",
        extra=[summon("Sisters, Sing", "Zin-Azshari Siren", 5, 2, 4)],
        signature=[dmg("Drown", int(B(59) * 1.9), cooldown=5, school="frost"),
                   last_gasp("The Sea Takes You", 59, "frost")])
    k["The Drowned Chamberlain"] = boss_kit(     # the steward, still keeping the ledger
        59, "shadow", "Ring of Keys", "Ledger Strike", "Collect the Debt", "Audit",
        stun_hit("Locked In", int(B(59) * 0.7), cooldown=6, school="shadow"), "Ten Thousand Years Overdue",
        extra=[hit_with("Tithe", int(B(59) * 0.7), {"attack_power": -60, "spell_power": -40}, 3, school="shadow",
                        cooldown=5)],
        signature=[dmg("Final Accounting", int(B(59) * 1.2), cooldown=6, school="shadow", is_aoe=True),
                   dot("Interest", int(B(59) * 0.5), 5, 4, school="shadow", dispel_type="curse")])
    k["Tidelord Vashj'ren"] = boss_kit(          # the naga warlord on the coral throne: the tide comes in with him
        60, "physical", "Trident Strike", "Coral Gore", "Tidal Slam", "Riptide",
        stun_hit("Undertow", int(B(60) * 0.7), cooldown=6, school="frost"), "High Tide",
        extra=[summon("Guard, to Me", "Zin-Azshari Royal Guard", 5, 2, 4)],
        signature=[dmg("The Tide Comes In", int(B(60) * 1.2), cooldown=6, school="frost", is_aoe=True),
                   dmg("Impale", int(B(60) * 2.0), cooldown=6),
                   last_gasp("Tsunami", 60, "frost", mult=1.7)])
    k["The Moonguard Revenant"] = boss_kit(      # the queen's knight, drowned in its armour
        60, "physical", "Moonguard Blade", "Shield Bash", "Riposte", "Cleave",
        stun_hit("Shield Charge", int(B(60) * 0.7), cooldown=6), "Last of the Moonguard",
        extra=[shell("Shield Wall", 6, 3, int(B(60) * 1.3))],
        signature=[dmg("Oath of the Moonguard", int(B(60) * 2.0), cooldown=6),
                   last_gasp("Drowned Charge", 60)])
    k["Magistrix Elaria the Undying"] = boss_kit(   # the sorceress at the well: blue fire, and she drinks the well
        60, "arcane", "Blue Fire", "Arcane Lance", "Immolating Flame", "Arcane Storm",
        hit_with("Spell Shackle", int(B(60) * 0.7), {"haste": -15, "spell_power": -40}, 3, school="arcane", cooldown=5),
        "The Undying",
        extra=[heal("Drink the Well", int(B(60) * 1.2), cooldown=6, school="arcane")],
        signature=[dmg("Well of Eternity", int(B(60) * 1.2), cooldown=6, school="arcane", is_aoe=True),
                   dot("Blue Flame", int(B(60) * 0.5), 5, 4, school="arcane", dispel_type="magic")])
    k[FINAL] = boss_kit(                         # moonlight and water in the queen's shape
        60, "arcane", "Queen's Disdain", "Moonlit Lash", "Kneel", "Tidal Glory",
        stun_hit("Kneel Before Me", int(B(60) * 0.75), cooldown=6, school="arcane"), "The Queen Remembers",
        extra=[summon("My Court", "Queen's Handmaiden", 4, 2, 5),
               hit_with("Unworthy", int(B(60) * 0.7), {"healing_power": -60, "haste": -10}, 3, school="arcane",
                        cooldown=5)],
        signature=[dmg("The Sea Returns", int(B(60) * 1.3), cooldown=6, school="frost", is_aoe=True),
                   dmg("Light of Zin-Azshari", int(B(60) * 2.0), cooldown=6, school="arcane"),
                   last_gasp("Ten Thousand Years", 60, "arcane", mult=1.8)])
    return k


#: boss -> [(item, slot, suffix, (a|w, type) or None, stat template)], four each, spread over every type
POOLS = {
    "Lady Ssiriss": [
        ("Pearl Crown of the Siren", "head", "of the Sorcerer", ("a", "cloth"), "int_caster"),
        ("Four-Armed Bracers", "wrist", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Siren-Scale Leggings", "legs", "of the Prophet", ("a", "mail"), "spi_healer"),
        ("Ssiriss's Coral Sceptre", "main_hand", "of the Invoker", ("w", "mace_1h"), "int_caster")],
    "The Drowned Chamberlain": [
        ("Chamberlain's Ledger", "off_hand", "of the Physician", ("w", "tome"), "spi_healer"),
        ("Ring of the Palace Keys", "ring", "of the Wolf", None, "agi_int_hybrid"),
        ("Steward's Drowned Gloves", "hands", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Waterlogged Livery", "chest", "of the Tiger", ("a", "leather"), "agi_physical")],
    "Tidelord Vashj'ren": [
        ("Tidelord's Trident", "main_hand", "of the Champion", ("w", "polearm"), "str_physical"),
        ("Coral Warplate", "chest", "of the Bear", ("a", "plate"), "str_physical"),
        ("Undertow Belt", "waist", "of the Hunt", ("a", "mail"), "agi_physical"),
        ("Cloak of the Rising Tide", "back", "of the Owl", None, "spi_healer")],
    "The Moonguard Revenant": [
        ("Moonguard Bulwark", "off_hand", "of the Bear", ("w", "shield"), "str_physical"),
        ("Revenant's Silver Greaves", "feet", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Seaweed-Wrapped Pauldrons", "shoulder", "of the Monkey", ("a", "leather"), "agi_physical"),
        ("Oathkeeper's Mantle", "shoulder", "of the Sorcerer", ("a", "cloth"), "int_caster")],
    "Magistrix Elaria the Undying": [
        ("Elaria's Blue Flame", "main_hand", "of the Sorcerer", ("w", "staff"), "int_caster"),
        ("Robes of the Undying", "chest", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Wellspring Gauntlets", "hands", "of the Wolf", ("a", "mail"), "agi_int_hybrid"),
        ("Magistrix's Sash", "waist", "of the Invoker", ("a", "cloth"), "int_caster")],
    FINAL: [
        ("Moonlit Mantle of the Queen", "shoulder", "of the Prophet", ("a", "mail"), "spi_healer"),
        ("Echoing Greatsword", "main_hand", "of the Champion", ("w", "sword_2h"), "str_physical"),
        ("Tidewoven Leggings", "legs", "of the Tiger", ("a", "leather"), "agi_physical"),
        ("Signet of Zin-Azshari", "ring", "of the Sorcerer", None, "int_caster")],
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
            d["item_id"] = "dpl_" + kit_slug(name)
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
    for fl in DP.FLOORS:
        placed = set(DP.BOSSES[fl])
        ours = {n for n in BOSSES if ROSTER[n][5] == fl}
        if placed != ours:
            bad.append(f"{fl}: bosses on the map {sorted(placed)} differ from the roster {sorted(ours)}")
        on_map = {m for p in DP._trash(fl) for (_x, _y, m, _l) in p}
        theirs = {n for n, r in ROSTER.items() if r[5] == fl and not r[3]}
        if on_map - theirs:
            bad.append(f"{fl}: trash on the map that isn't this floor's: {sorted(on_map - theirs)}")
        lo, hi = ZONE_LEVELS[fl]
        for n, r in ROSTER.items():
            if r[5] == fl and not (lo <= r[1] and r[2] <= hi):
                bad.append(f"{n} ({r[1]}-{r[2]}) sits outside {fl} {lo}-{hi}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    for name, (_t, lo_, hi_, _m, sprite, _f) in ROSTER.items():
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
    for (_t, _lo, _hi, _m, sprite, _f) in ROSTER.values():
        src, dst = SRC / f"{sprite}.png", ROOT / "assets/creatures" / f"{sprite}.png"
        if src.exists() and not dst.exists():
            shutil.copyfile(src, dst)
            n += 1
    return n


def _write(path, data, raw):
    indent, newline = _detect_format(json.loads(raw), raw)
    path.write_text(json.dumps(data, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")


def main():
    for fl in DP.FLOORS:
        DP.build_floor(fl)
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
    for name, (template, lo, hi, mult, _s, _f) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    caves = enc["zones"].setdefault(PARENT, {"name": PARENT}).setdefault("caves", {})
    for fl in DP.FLOORS:
        caves[fl] = {"name": fl, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items() if r[5] == fl}}
    _write(ENCOUNTERS, enc, raw)
    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    lv["zones"].update(ZONE_LEVELS)
    _write(LEVELS, lv, raw)
    out = {"_notes": ("Boss loot for the Drowned Palace (59-60), off East Azshara. ONE item per kill from the boss's "
                      "four; item_level = boss level + 3. Hand-authored in tools/build_drowned_palace_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    print(f"{len(ROSTER)} creatures ({len(BOSSES)} bosses); {copied} sprites installed; "
          f"{sum(len(v) for v in loot.values())} boss items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
