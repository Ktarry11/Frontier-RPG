"""
Write the hand-chosen NPC / vendor positions (and town forges) from the Astranaar, Splintertree Post and Zoram Strand
layout modules into data/npcs/*.json, and create the few NPCs Zoram Strand never had.  Idempotent.

    python3 tools/sync_ashenvale_town_npcs.py
"""
import importlib
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

MODULES = ["tools.handbuilt_astranaar", "tools.handbuilt_splintertree", "tools.handbuilt_zoram"]
FORGES = {"tools.handbuilt_astranaar": ("astranaar_forge", "Astranaar Forge", "astranaar"),
          "tools.handbuilt_splintertree": ("splintertree_forge", "Splintertree Forge", "splintertree_post")}

# Zoram Strand had one unnamed boat tile and no NPC records at all.
NEW_NPCS = [
    {"npc_id": "zoram_boatwright", "name": "Boatwright Illyen", "zone": "zoram_strand",
     "greeting": "The Strand's boats go where the tide lets them. Mind the planks, they're wet.",
     "gender": "female", "race": "night_elf", "appearance_variant": 2, "facing": "left"},
    {"npc_id": "zoram_fisher", "name": "Old Maelis", "zone": "zoram_strand",
     "greeting": "Silverfin run thick this season. Shame the Horde ships scare them off.",
     "gender": "male", "race": "night_elf", "appearance_variant": 4, "facing": "down"},
    {"npc_id": "zoram_sentinel", "name": "Lookout Taelanor", "zone": "zoram_strand",
     "greeting": "I watch the water so the others can sleep. Nothing has crossed it tonight.",
     "gender": "female", "race": "night_elf", "appearance_variant": 1, "facing": "down"},
]
NEW_VENDORS = [
    {"vendor_id": "zoram_fishmonger", "name": "Fishmonger Sylra", "zone": "zoram_strand", "tile_sprite": "npc",
     "sells": ["healing_potion_minor", "healing_potion_standard", "mana_potion_minor", "bread_and_cheese",
               "roasted_meat"],
     "buys_from_player": True, "faction": "neutral", "gear_level": 14, "sells_gear": False,
     "race": "night_elf", "appearance_variant": 3,
     "greeting": "Fresh from the tide, and the only honest scales on the coast."},
]


def _patch(path, list_key, id_key, positions, new=()):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    ids = {r.get(id_key) for r in data[list_key]}
    n = 0
    for rec in new:
        if rec[id_key] not in ids:
            data[list_key].append(dict(rec, x=0, y=0))
            n += 1
    for rec in data[list_key]:
        pos = positions.get(rec.get(id_key))
        if pos and (rec.get("x"), rec.get("y")) != tuple(pos):
            rec["x"], rec["y"] = pos
            n += 1
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return n


def main():
    npcs, forges = {}, []
    for name in MODULES:
        M = importlib.import_module(name)
        npcs.update(M.NPC_POSITIONS)
        if name in FORGES and hasattr(M, "FORGE"):
            forges.append((FORGES[name], M.FORGE))
    total = _patch("data/npcs/ambient_npcs.json", "npcs", "npc_id", npcs, NEW_NPCS)
    total += _patch("data/npcs/vendors.json", "vendors", "vendor_id", npcs, NEW_VENDORS)
    fp = Path("data/npcs/forges.json")
    data = json.loads(fp.read_text(encoding="utf-8"))
    for (fid, fname, zone), (x, y) in forges:
        rec = next((f for f in data["forges"] if f["forge_id"] == fid), None)
        if rec is None:
            data["forges"].append({"forge_id": fid, "name": fname, "zone": zone, "x": x, "y": y})
            total += 1
        elif (rec["x"], rec["y"]) != (x, y):
            rec["x"], rec["y"] = x, y
            total += 1
    fp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"moved/added {total} records")


if __name__ == "__main__":
    main()
