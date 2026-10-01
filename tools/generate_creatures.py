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
    print("Generating ability_kits.json...")
    kits_data = build_kits()
    with open(data_dir / "ability_kits.json", "w") as f:
        json.dump(kits_data, f, indent=2)
    print(f"  ✓ {len(kits_data['kits'])} kits")

    print("\nCreature data generated successfully.")


if __name__ == "__main__":
    main()
