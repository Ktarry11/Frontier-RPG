"""Where the recruits stand, by zone - so scenery can keep off them.

A recruit's position lives in data/npcs/recruits.json, not in the zone module, so a zone that
scatters props has no way to know someone is standing there. The Flats' new shore scatter put a
skeleton on Ratih (13 Nov 2026) and she became unreachable; tools/qa_recruits.py caught it.
"""
import json
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent


def recruit_tiles(zone_name):
    data = json.loads((_ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]
    rows = data.values() if isinstance(data, dict) else data
    return [(r["x"], r["y"]) for r in rows if r.get("zone") == zone_name and "x" in r and "y" in r]
