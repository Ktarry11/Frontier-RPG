#!/usr/bin/env python3
"""Ashenvale's seven named rares drop loot. Idempotent; writes one file.

    PYTHONPATH=. python3 tools/build_ashenvale_rare_loot.py

Found 13 Nov 2026 while giving Blackfathom Deeps its loot (Kyle: "blackfathom depth bosses have no
loot pool? We should fix that"): the same was true of every named rare in the open zones of
Ashenvale. Six of the seven are the last quest of a chain - Ursal, Keeper Rustveil, Lord Malgan,
the Twilight Overseer - and killing them dropped nothing of their own.

ONE ITEM PER KILL from a pool of four, item level = level + 2 (the open-world offset; dungeons use
+3), stats from tools/build_durotar_content.make. The spread across the 28 items is checked: four
or five of each armour class and eight weapons of eight types.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make  # noqa: E402

OUT = ROOT / "data/loot/ashenvale_rare_loot.json"


def it(ilvl, name, slot, suffix, armor_type=None, weapon_type=None):
    d = make(name, slot, suffix, ilvl, "", armor_type=armor_type, weapon_type=weapon_type)
    d.pop("flavor_text", None)
    return d


def pools():
    P = {}
    P["Felstalker"] = [             # 23 -> 25. The Demon Wastes
        it(25, "Felstalker's Leash", "waist", "of the Monkey", armor_type="leather"),
        it(25, "Manaburnt Fang", "main_hand", "of the Assassin", weapon_type="dagger"),
        it(25, "Houndmaster's Wristguards", "wrist", "of the Hunt", armor_type="mail"),
        it(25, "Collar of the Demon Wastes", "neck", "of the Sorcerer"),
    ]
    P["Lord Malgan"] = [            # 25 -> 27. Satyr's Throne
        it(27, "Malgan's Throne-Staff", "main_hand", "of the Sorcerer", weapon_type="staff"),
        it(27, "Satyr-Lord's Mantle", "shoulder", "of the Invoker", armor_type="cloth"),
        it(27, "Cloven Stompers", "feet", "of the Soldier", armor_type="plate"),
        it(27, "Horn of Satyr's Throne", "off_hand", "of the Prophet", weapon_type="idol"),
    ]
    P["Twilight Overseer"] = [      # 25 -> 27. Twilight Barrow
        it(27, "Overseer's Flail", "main_hand", "of the Gladiator", weapon_type="mace_1h"),
        it(27, "Barrow-Keeper's Breastplate", "chest", "of the Champion", armor_type="plate"),
        it(27, "Twilight Barrow Hood", "head", "of the Owl", armor_type="cloth"),
        it(27, "Barrow-Warden's Gauntlets", "hands", "of the Squire", armor_type="plate"),
    ]
    P["Pit Lord Emissary"] = [      # 25 -> 27. The Demon Wastes
        it(27, "Emissary's Glaive", "main_hand", "of the Beast", weapon_type="polearm"),
        it(27, "Wastes-Walker Leggings", "legs", "of the Falcon", armor_type="mail"),
        it(27, "Fel-Scorched Handwraps", "hands", "of the Sorcerer", armor_type="cloth"),
        it(27, "Pit-Iron Shoulderguards", "shoulder", "of the Bear", armor_type="plate"),
    ]
    P["Elder Timberling"] = [       # 26 -> 28. Silverwind Vale, Warsong Lumber Camp
        it(28, "Heartwood Cudgel", "main_hand", "of the Bear", weapon_type="mace_2h"),
        it(28, "Barkhide Jerkin", "chest", "of the Hunt", armor_type="leather"),
        it(28, "Timberling Root Sandals", "feet", "of the Prophet", armor_type="cloth"),
        it(28, "Mossgrown Bracers", "wrist", "of the Wolf", armor_type="leather"),
    ]
    P["Ursal the Mauler"] = [       # 28 -> 30. The Ragged Highlands
        it(30, "Mauler's Paw", "main_hand", "of the Bandit", weapon_type="fist_weapon"),
        it(30, "Ursal's Pelt", "back", "of the Monkey", armor_type="cloth"),
        it(30, "Highland Bearhide Leggings", "legs", "of the Monkey", armor_type="leather"),
        it(30, "Ragged Highlands Coif", "head", "of the Marksman", armor_type="mail"),
    ]
    P["Keeper Rustveil"] = [        # 28 -> 30. Moonwhisper Grove
        it(30, "Rustveil's Bough", "ranged", "of the Archmage", weapon_type="wand"),
        it(30, "Grovewarden's Chainmail", "chest", "of the Eagle", armor_type="mail"),
        it(30, "Keeper's Antlered Helm", "head", "of the Physician", armor_type="leather"),
        it(30, "Moonwhisper Band", "ring", "of the Wellspring"),
    ]
    return P


def audit(P):
    bad = []
    items = [i for v in P.values() for i in v]
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text())["creatures"]
    for n, pool in P.items():
        if n not in creatures or not creatures[n].get("is_boss"):
            bad.append(f"{n} is not a rare in the game")
            continue
        want = creatures[n]["level_range"][1] + 2
        if any(i["item_level"] != want for i in pool) or len(pool) != 4:
            bad.append(f"{n}: pool is not four items at item level {want}")
    names = Counter(i["name"] for i in items)
    if any(c > 1 for c in names.values()):
        bad.append("duplicate names")
    arm = Counter(i["armor_type"] for i in items if i.get("armor_type"))
    for t in ("cloth", "leather", "mail", "plate"):
        if not 4 <= arm[t] <= 5:
            bad.append(f"{arm[t]} {t} pieces - want four or five of each")
    weapons = [i["weapon_type"] for i in items if i.get("weapon_type")]
    if len(set(weapons)) != len(weapons):
        bad.append(f"a weapon type is repeated: {sorted(weapons)}")
    return bad, arm, weapons


def main():
    P = pools()
    bad, arm, weapons = audit(P)
    if bad:
        print("FAILED - fix the pools, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    out = {"_notes": "Ashenvale's named open-world rares (2026-11-13). ONE item drops per kill from the "
                     "pool. item_level = level + 2; hand-authored in tools/build_ashenvale_rare_loot.py."}
    out.update(P)
    OUT.write_text(json.dumps(out, indent=2) + "\n")
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"{len(P)} pools, {sum(len(v) for v in P.values())} items -> {OUT.name}")
    print(f"  armour {dict(arm)}; weapons {sorted(weapons)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
