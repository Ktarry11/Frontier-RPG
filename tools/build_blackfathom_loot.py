#!/usr/bin/env python3
"""Blackfathom Deeps: loot for its seven bosses. Idempotent; writes one file.

    PYTHONPATH=. python3 tools/build_blackfathom_loot.py

Kyle, 13 Nov 2026: "I just saw blackfathom depth bosses have no loot pool? We should fix that."
All seven dropped nothing of their own. The dungeon was built and its bosses placed and given
abilities, and the loot file was simply never written.

ONE ITEM PER KILL from a pool of four, item level = boss level + 3 like the other Ashenvale
dungeons (Moonwell Hollow, Howling Barrows, Grom's Rest), stats from the real formulas
(tools/build_durotar_content.make) and a suffix that does what it says.

THE SPREAD IS CHECKED, NOT ASSUMED (Kyle: loot must not lean on one armour class or weapon type).
Across the 28 items: four or five of each armour class, nine weapons of nine different types -
three of them for casters and healers - and something for every way of gearing: strength,
agility, agility/intellect, caster, healer and tank.

No flavour text. Kyle keeps it for epics and legendaries; these are rares.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make  # noqa: E402

OUT = ROOT / "data/loot/blackfathom_deeps_boss_loot.json"
ILVL = 29          # every boss here is level 26


def it(name, slot, suffix, armor_type=None, weapon_type=None):
    d = make(name, slot, suffix, ILVL, "", armor_type=armor_type, weapon_type=weapon_type)
    d.pop("flavor_text", None)
    return d


def pools():
    P = {}
    # The great turtle at the pool. Shell, and what a shell is good for.
    P["Ghamoo-ra"] = [
        it("Ghamoo-ra's Shellplate Girdle", "waist", "of the Soldier", armor_type="plate"),
        it("Carapace of the Old Snapper", "off_hand", "of Stamina", weapon_type="shield"),
        it("Tide-Worn Wristguards", "wrist", "of the Eagle", armor_type="mail"),
        it("Snapjaw Hide Boots", "feet", "of the Monkey", armor_type="leather"),
    ]
    # The naga who holds the first shrine.
    P["Lady Sarevess"] = [
        it("Sarevess's Recurve", "ranged", "of the Sharpshooter", weapon_type="bow"),
        it("Coilscale Hauberk", "chest", "of the Hunt", armor_type="mail"),
        it("Sea-Witch's Circlet", "head", "of the Sorcerer", armor_type="cloth"),
        it("Band of the Drowned Shrine", "ring", "of the Bandit"),
    ]
    # The murloc oracle.
    P["Gelihast"] = [
        it("Gelihast's Tidecaller", "main_hand", "of the Prophet", weapon_type="mace_1h"),
        it("Reef-Scale Gauntlets", "hands", "of the Falcon", armor_type="mail"),
        it("Murk-Silt Leggings", "legs", "of the Physician", armor_type="leather"),
        it("Oracle's Fin Cloak", "back", "of the Seer", armor_type="cloth"),
    ]
    # The Twilight's Hammer stormcaller.
    P["Lorgus Jett"] = [
        it("Jett's Thunder Maul", "main_hand", "of the Gladiator", weapon_type="mace_2h"),
        it("Stormcaller's Mantle", "shoulder", "of the Wellspring", armor_type="mail"),
        it("Hammerbound Bracers", "wrist", "of the Squire", armor_type="plate"),
        it("Twilight Litany", "off_hand", "of the Invoker", weapon_type="tome"),
    ]
    # The thresher in the flooded hall.
    P["Old Serra'kis"] = [
        it("Thresher's Tooth", "main_hand", "of the Assassin", weapon_type="dagger"),
        it("Serra'kis Hide Tunic", "chest", "of the Bandit", armor_type="leather"),
        it("Deepwater Legguards", "legs", "of the Champion", armor_type="plate"),
        it("Fishbone Pendant", "neck", "of the Marksman"),
    ]
    # He dreams for the Old Gods and speaks for them awake.
    P["Twilight Lord Kelris"] = [
        it("Rod of the Sleepwalker", "main_hand", "of Shadow Wrath", weapon_type="staff"),
        it("Gaze-Dreamer's Robes", "chest", "of the Archmage", armor_type="cloth"),
        it("Kelris's Dreamweave Gloves", "hands", "of the Owl", armor_type="cloth"),
        it("Twilight Lord's Blade", "main_hand", "of the Champion", weapon_type="sword_1h"),
    ]
    # The hydra at the bottom of it.
    P["Aku'mai"] = [
        it("Strike of the Hydra", "main_hand", "of the Beast", weapon_type="sword_2h"),
        it("Moss Cinch", "waist", "of the Wolf", armor_type="leather"),
        it("Leech-Silk Trousers", "legs", "of the Invoker", armor_type="cloth"),
        it("Three-Crowned Helm", "head", "of the Bear", armor_type="plate"),
    ]
    return P


def audit(P):
    bad = []
    items = [i for v in P.values() for i in v]
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]
    table = json.loads((ROOT / "data/creatures/encounters.json").read_text())["zones"]["Ashenvale West"]["caves"]["Blackfathom Deeps"]["creatures"]
    bosses = {n for n in table if creatures.get(n, {}).get("is_boss")}
    if set(P) != bosses:
        bad.append(f"pools and bosses differ: {sorted(set(P) ^ bosses)}")
    for n in P:
        if creatures[n]["level_range"][1] + 3 != ILVL:
            bad.append(f"{n} is not level {ILVL - 3}")
    if any(len(v) != 4 for v in P.values()):
        bad.append("a pool does not have four items")
    names = Counter(i["name"] for i in items)
    if any(c > 1 for c in names.values()):
        bad.append(f"duplicate names: {[n for n, c in names.items() if c > 1]}")
    arm = Counter(i["armor_type"] for i in items if i.get("armor_type"))
    for t in ("cloth", "leather", "mail", "plate"):
        if not 4 <= arm[t] <= 5:
            bad.append(f"{arm[t]} {t} pieces - want four or five of each")
    weapons = [i["weapon_type"] for i in items if i.get("weapon_type")]
    if len(set(weapons)) != len(weapons):
        bad.append(f"a weapon type is repeated: {sorted(weapons)}")
    if len([w for w in weapons if w in ("staff", "tome", "mace_1h", "wand", "idol", "libram", "totem")]) < 3:
        bad.append("fewer than three caster or healer weapons")
    for i in items:
        if any("resistance" in k for k in dict(i.get("primary_stats") or {}, **(i.get("secondary_stats") or {}))):
            bad.append(f"{i['name']} carries resistance below level 45")
    return bad, arm, weapons


def main():
    P = pools()
    bad, arm, weapons = audit(P)
    if bad:
        print("FAILED - fix the pools, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    out = {"_notes": "Blackfathom Deeps boss loot (2026-11-13). ONE item drops per kill from the pool. "
                     "item_level = boss level + 3; hand-authored in tools/build_blackfathom_loot.py."}
    out.update(P)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"{len(P)} pools, {sum(len(v) for v in P.values())} items -> {OUT.name}")
    print(f"  armour {dict(arm)}; weapons {sorted(weapons)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
