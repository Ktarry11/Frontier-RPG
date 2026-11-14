#!/usr/bin/env python3
"""Mark mutually-exclusive buff families (one at a time, like Classic WoW) so they stop stacking.

Shaman imbues are handled in tools/build_shaman_imbues.py; Cultist presences/whispers and Tinker rounds already had groups.
Idempotent.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUPS = {
    "paladin": {"paladin_seal_of_righteousness": "paladin_seal", "paladin_seal_of_command": "paladin_seal"},
    "hunter": {"hunter_aspect_of_the_hawk": "hunter_aspect", "hunter_aspect_of_the_wild": "hunter_aspect"},
}

for cls, groups in GROUPS.items():
    path = ROOT / "data" / "abilities" / f"{cls}.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    n = 0
    for a in data["abilities"]:
        if a["ability_id"] in groups and a.get("exclusive_group") != groups[a["ability_id"]]:
            a["exclusive_group"] = groups[a["ability_id"]]
            n += 1
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(cls, "exclusive groups set on", n)
