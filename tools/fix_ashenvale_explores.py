"""
One-off repair (2026-10-22): five Ashenvale explore quests were authored with target=None (and a display-name zone), so
they could never complete.  Gate each on a walkable point at the centre of the named subzone.  Idempotent.

    python3 tools/fix_ashenvale_explores.py
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from world.zone_generator import create_all_zones   # noqa: E402

WHERE = {   # subzone display name -> (zone, radius)
    "Ragged Highlands": ("Ashenvale West", 14), "The Night Run": ("Ashenvale West", 14),
    "Lake Elune'ara": ("Ashenvale West", 10), "Coast Bluffs": ("Ashenvale West", 10),
    "The Demon Wastes": ("Ashenvale East", 12),
}


def main():
    Z = create_all_zones()
    n = 0
    for fn in ("ashenvale.json", "forsaken_lands.json"):
      path = ROOT / "data/quests" / fn
      data = json.loads(path.read_text(encoding="utf-8"))
      for q in data["quests"]:
          for o in q["objectives"]:
              if o["type"] != "explore" or o.get("target_x") is not None:
                  continue
              sub = o.get("zone")
              if sub not in WHERE:
                  continue
              zname, radius = WHERE[sub]
              z = Z[zname]
              s = next(s for s in z.subzones if s["name"] == sub)
              cx, cy = s["x"] + s["w"] // 2, s["y"] + s["h"] // 2
              pts = [(x, y) for y in range(s["y"], s["y"] + s["h"]) for x in range(s["x"], s["x"] + s["w"])
                     if z.is_walkable(x, y)]
              x, y = min(pts, key=lambda p: (p[0] - cx) ** 2 + (p[1] - cy) ** 2)
              o.clear()
              o.update(type="explore", target=zname.lower().replace(" ", "_"), target_x=x, target_y=y, radius=radius)
              n += 1
              print(q["quest_id"], "->", o)
      path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("fixed", n)


if __name__ == "__main__":
    main()
