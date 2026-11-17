#!/usr/bin/env python3
"""Give the healers that had no way to cleanse a party member one. Idempotent.

    PYTHONPATH=. python3 tools/add_missing_cleanses.py [--check]

The support pass, 16 Nov 2026 (Kyle: "don't forget to look at EVERY Healer"). The bosses from level 40 now carry
party-wide damage-over-time in curse, magic, poison and disease (tools/build_boss_aoe.py), so a healer who can't
cleanse anything is missing half its job. Measured, ally cleanses per healer class:
  Druid       none at all (Restoration had no Remove Curse and no Abolish Poison)
  Shaman      only Cleanse Spirit (curse), from a level-50 talent: nothing for poison or disease before or after it
  Mage        none: a Frost Cryotherapist heals but couldn't lift a curse
Every other healer already had two or three schools (Paladin's Cleanse, Priest's Dispel Magic and Abolish Disease,
the Sun Cleric's Sanctify...). This adds, in each class's own file, the Classic shape of each:
  Druid   Remove Curse (curse, 18) and Abolish Poison (poison, 26)
  Shaman  Cure Toxins (poison and disease, 16)
  Mage    Remove Curse (curse, 18)
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ADD = {
    "druid": [
        dict(ability_id="druid_remove_curse", name="Remove Curse", level=18, cost=30, cooldown=2, dispel="curse",
             description="Removes 1 curse from a friendly target."),
        dict(ability_id="druid_abolish_poison", name="Abolish Poison", level=26, cost=35, cooldown=2,
             dispel="poison", description="Removes 1 poison from a friendly target."),
    ],
    "shaman": [
        dict(ability_id="shaman_cure_toxins", name="Cure Toxins", level=16, cost=30, cooldown=2,
             dispel=["poison", "disease"], description="Removes 1 poison or disease from a friendly target."),
    ],
    "mage": [
        dict(ability_id="mage_remove_curse", name="Remove Curse", level=18, cost=30, cooldown=2, dispel="curse",
             description="Removes 1 curse from a friendly target."),
    ],
}
NOTE = "16 Nov 2026, support pass: added so this healer can cleanse a party member (tools/add_missing_cleanses.py)"


def entry(a):
    return {"ability_id": a["ability_id"], "name": a["name"], "resource_type": "mana", "cooldown": a["cooldown"],
            "effect_type": "dispel", "duration": 0, "stat_mods": {}, "description": a["description"],
            "ranks": [{"rank": 1, "level_req": a["level"], "cost": a["cost"], "effect_value": 0}],
            "target_type": "ally", "dispel_type": a["dispel"], "is_instant": True, "icon_id": None, "_tuning": [NOTE]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    missing = 0
    for cls, adds in ADD.items():
        fn = ROOT / f"data/abilities/{cls}.json"
        d = json.loads(fn.read_text(encoding="utf-8"))
        rows = d["abilities"] if isinstance(d, dict) and "abilities" in d else d
        have = {a.get("ability_id") for a in rows if isinstance(a, dict)}
        new = [entry(a) for a in adds if a["ability_id"] not in have]
        missing += len(new)
        if new and not args.check:
            rows.extend(new)
            fn.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        for a in new:
            print(f"  {'would add' if args.check else 'added'} {a['ability_id']} ({a['dispel_type']}, level "
                  f"{a['ranks'][0]['level_req']})")
    print("up to date" if not missing else f"{missing} cleanse(s) {'missing' if args.check else 'added'}")
    return 1 if (args.check and missing) else 0


if __name__ == "__main__":
    sys.exit(main())
