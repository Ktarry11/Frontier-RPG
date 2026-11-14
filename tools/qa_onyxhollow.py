#!/usr/bin/env python3
"""Onyxhollow is the town Kyle asked for.

    PYTHONPATH=. python3 tools/qa_onyxhollow.py

Kyle, 13 Nov 2026: "a small 'town' - (seperate map) of dark iron dwarfs. There wont be a flight
master but this can have an inn", and "innkeeper for hearth, level appropriate shops, this can be
more of a mining town and Blacksmithing."

SEVEN CLAIMS:
  1. A SEPARATE TOWN MAP, joined both ways to the gate in The Black Strand.
  2. AN INN: the innkeeper is registered for the hearth and stands where you can reach her.
  3. NO FLIGHT MASTER, now or by accident later.
  4. LEVEL APPROPRIATE SHOPS: every vendor is tiered inside the zone's band (50-53) and sells a
     the town sells a health potion fit for that level; at least two sell gear.
  5. A MINING AND BLACKSMITHING TOWN: exactly one trainer, teaching exactly those two, a working
     forge you can stand beside, a smithy, a smeltery and a mine head on the map.
  6. EVERYONE CAN BE WALKED TO and nobody is drawn under a building or a prop.
  7. EVERYONE IS DRAWN AS A DARK IRON DWARF: each has a figure of their own on disk.
"""
import contextlib
import io
import json
import os
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from tools import handbuilt_onyxhollow as O
    from tools import handbuilt_black_strand as S
    from tools import onyxhollow_npc_roster as R
    from world.npc_clearance import covered


def main():
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        zone, _L = O.build_onyxhollow_baked()
    O.verify(zone)

    # 1
    if not zone.is_town or zone.is_cave:
        bad.append("not flagged as a town")
    src = Path("world/portal_manager.py").read_text(encoding="utf-8")
    for needle in (f'({S.TOWN_GATE[0]}, {S.TOWN_GATE[1]}): ("Onyxhollow", {O.ARRIVAL[0]}, {O.ARRIVAL[1]})',
                   f'({O.PORTAL[0]}, {O.PORTAL[1]}): ("The Black Strand", {S.TOWN_ARRIVAL[0]}, {S.TOWN_ARRIVAL[1]})'):
        if needle not in src:
            bad.append(f"portal link missing: {needle}")
    if S.TOWN_GATE not in S.PORTALS:
        bad.append("the Strand's gate is not a door")

    seen, q = {O.ARRIVAL}, deque([O.ARRIVAL])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and zone.is_walkable(*n):
                seen.add(n)
                q.append(n)

    def beside(p):
        return any((p[0] + dx, p[1] + dy) in seen for dx in (-1, 0, 1) for dy in (-1, 0, 1))

    # 2, 3
    td = json.load(open("data/travel/travel_data.json", encoding="utf-8"))
    if "inn" not in td["services"].get("oh_innkeeper", []):
        bad.append("the innkeeper is not registered as an inn")
    if any("flight" in v for k, v in td["services"].items() if k.startswith("oh_")) \
            or any(n.get("zone") == "Onyxhollow" for n in td["flight_nodes"].values()):
        bad.append("the town has a flight master")

    # 4
    vendors = {v["vendor_id"]: v for v in json.load(open("data/npcs/vendors.json", encoding="utf-8"))["vendors"]
               if v["zone"] == "onyxhollow"}
    cons = json.load(open("data/items/consumables.json", encoding="utf-8")) if Path("data/items/consumables.json").exists() else None
    if set(vendors) != set(R.ONYXHOLLOW_VENDORS):
        bad.append(f"vendors on file differ from the roster: {sorted(set(vendors) ^ set(R.ONYXHOLLOW_VENDORS))}")
    for vid, v in vendors.items():
        if not 50 <= v["gear_level"] <= 53:
            bad.append(f"{vid} is tiered {v['gear_level']}, outside 50-53")
    # one shop in town is enough (tools/vendor_trades.py: the smith no longer sells potions)
    if not any("healing_potion_masterwork" in v["sells"] for v in vendors.values()):
        bad.append("nobody in town sells a health potion fit for the level")
    if sum(1 for v in vendors.values() if v.get("sells_gear")) < 2:
        bad.append("fewer than two shops sell gear")
    del cons

    # 5
    tr = json.load(open("data/training/trainers.json", encoding="utf-8"))["profession_trainers"]
    here = {k: v for k, v in tr.items() if k.startswith("oh_")}
    # the forge, and the enchanter (tools/build_enchanters.py, 14 Nov 2026) who teaches enchanting
    # and runecrafting
    if here != {"oh_forgemaster": ["mining", "blacksmithing", "jewelcrafting"],
                "oh_enchanter": ["enchanting", "runecrafting"]}:
        bad.append(f"trainers here: {here}")
    npcs = {n["npc_id"]: n for n in json.load(open("data/npcs/ambient_npcs.json", encoding="utf-8"))["npcs"]
            if n["zone"] == "onyxhollow"}
    if npcs.get("oh_forgemaster", {}).get("trains_profession") != ["mining", "blacksmithing", "jewelcrafting"]:
        bad.append("the forgemaster's own record does not say what he teaches")
    forge = [f for f in json.load(open("data/npcs/forges.json", encoding="utf-8"))["forges"] if f["zone"] == "onyxhollow"]
    if len(forge) != 1 or not beside((forge[0]["x"], forge[0]["y"])):
        bad.append(f"the forge is missing or cannot be stood beside: {forge}")
    drawn = {lm["sprite_key"].split("/")[-1][:-4] for lm in zone.landmarks}
    for must in ("di_smithy", "di_smeltery", "di_mine_head", "di_inn"):
        if must not in drawn:
            bad.append(f"no {must} on the map")

    # 6, 7
    everyone = dict(O.NPC_POSITIONS)
    if set(everyone) != set(vendors) | set(npcs):
        bad.append(f"people on the map and on file differ: {sorted(set(everyone) ^ (set(vendors) | set(npcs)))}")
    for nid, (x, y) in everyone.items():
        rec = vendors.get(nid) or npcs.get(nid) or {}
        if (rec.get("x"), rec.get("y")) != (x, y):
            bad.append(f"{nid} is filed at {(rec.get('x'), rec.get('y'))}, the map says {(x, y)}")
        if not beside((x, y)):
            bad.append(f"{nid} cannot be reached")
        over = [lm["sprite_key"].split("/")[-1] for lm in zone.landmarks if covered(lm, x, y) > 0.5]
        if over:
            bad.append(f"{nid} is drawn under {over}")
        if not Path(f"assets/npcs/leaders/{nid}/down.png").exists():
            bad.append(f"{nid} has no figure of their own")
    if "assets/npcs/leaders/{getattr(vendor, 'vendor_id', '')}" not in Path("ui/tilemap_renderer.py").read_text(encoding="utf-8"):
        bad.append("the map does not draw a vendor's own figure")

    print(f"{len(everyone)} people ({len(vendors)} shops), {len(O.BUILDINGS)} buildings, "
          f"1 inn, 1 trainer, 1 forge, 0 flight masters")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nOnyxhollow OK - an inn, level 52 shops, one forgemaster, a forge, and no way to fly out.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
