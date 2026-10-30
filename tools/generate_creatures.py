#!/usr/bin/env python3
"""
Generate creature data files (templates, kits) from the authoritative sources.

Invoked by: python3 tools/generate_creatures.py

RUN THIS WHEN:
  - Adding/changing a template in tools/monster_templates.py
  - Adding/changing a kit in tools/monster_kits.py

This is a build step, not a runtime system. The data files it produces are
checked in and shipped; regenerate only when the source data changes.
"""
import json
import sys
from pathlib import Path

# Add tools/ to path so we can import the source data
tools_dir = Path(__file__).parent
sys.path.insert(0, str(tools_dir))

from monster_templates import build as build_templates
from monster_kits import build as build_kits


def main():
    data_dir = tools_dir.parent / "data" / "creatures"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Generate templates
    print("Generating templates.json...")
    templates_data = build_templates()
    with open(data_dir / "templates.json", "w") as f:
        json.dump(templates_data, f, indent=2)
    print(f"  ✓ {len(templates_data['templates'])} templates")

    # Generate kits
    #
    # THIS MERGES. IT USED TO REPLACE, AND REPLACING SILENTLY DESTROYED 39 KITS.
    #
    # Not every kit lives in monster_kits.py. The per-zone content builders (build_return_voyage_content,
    # build_undercrust_content and the rest) write theirs straight into ability_kits.json through
    # merge_json, which is a perfectly reasonable thing for them to do and has been the pattern for a
    # while. But this function rebuilt the file from monster_kits.ALL_KITS alone and wrote it out, so
    # running it deleted every kit that only lived in the JSON.
    #
    # Measured the day this was fixed: one run took the file from 949 kits to 927 and left 34 creatures
    # in live encounter tables - every Bloodsail aboard the Return Voyage ships among them - pointing at
    # a kit that no longer existed. Monster.__init__ raises KeyError on an unknown kit, so those were not
    # degraded mobs, they were a hard crash the moment one rolled. Nothing warned. The only reason it was
    # caught is that rework_boss_kits() below happened to die on one of the missing ids.
    #
    # So: anything already in the file that this run does not know about is KEPT, and said out loud.
    print("Generating ability_kits.json...")
    kits_data = build_kits()
    path = data_dir / "ability_kits.json"
    if path.exists():
        existing = json.loads(path.read_text(encoding="utf-8")).get("kits", {})
        outside = {k: v for k, v in existing.items() if k not in kits_data["kits"]}
        if outside:
            print(f"  keeping {len(outside)} kit(s) that live in the JSON rather than in "
                  f"monster_kits.py (zone content builders write these)")
        kits_data["kits"].update(outside)
    with open(path, "w") as f:
        json.dump(kits_data, f, indent=2)
    print(f"  ✓ {len(kits_data['kits'])} kits")

    # Boss kits are post-processed (buffs/debuffs ride on attacks, enrage phase, ...): see tools/rework_boss_kits.py.
    # Regenerating overwrites ability_kits.json with the raw kits, so re-apply it here.
    from rework_boss_kits import main as rework_boss_kits
    rework_boss_kits()

    print("\nCreature data generated successfully.")


if __name__ == "__main__":
    main()
