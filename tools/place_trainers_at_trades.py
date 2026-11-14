#!/usr/bin/env python3
"""Stand every trainer at the building of their trade (idempotent; run after the trainer builders).

    PYTHONPATH=. python3 tools/place_trainers_at_trades.py [--dry-run]

Kyle, 14 Nov 2026: "Fix where trainers stand, make it better for each town."

tools/build_profession_trainers.py and tools/build_class_trainers.py scatter their trainers on open
tiles 3 to 12 steps from the innkeeper. That puts people in sensible open ground, but nowhere in
particular: Razor Hill's smith stood across the square from the smithy, its tinker nowhere near the
scrapyard workshop. A player looking for the tanner should be able to walk to the tannery.

This pass moves each pt_<town>_<pair> and ct_<town> NPC (their ids, names and greetings are
untouched) to the front of the building that fits their trade:

    forge    the town's forge (forges.json), else a smithy
    herbs    an apothecary, herb hut, alchemy table, healer's or shaman's house
    wood     the town's sawmill (sawmills.json), else a carver's, bowyer's or log pile
    hide     a tannery, hide rack, smokehouse, stable or kennel
    essence  a workshop, goblin office or arcane desk
    class    a trainers' lodge, training pavilion, barracks or hall

"In front" means a free tile below the building's base row, near its middle, in the same walkable
area as the town, not under any other scenery (world/npc_clearance.py would delete a prop drawn
over an NPC, so a trainer must never stand where that happens), and not on top of another NPC.
A town without a fitting building keeps the trainer where the builder put them.
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
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
DRY = "--dry-run" in sys.argv

#: building art (substring of the sprite file name) for each trade, best first. A trainer goes to
#: the best tier present in their town, the nearest one to the town's middle within that tier.
TRADES = {
    "forge": [["smithy", "war_forge", "grand_forge", "elf_forge", "smithy_forge"], ["tau_kiln", "weapon_rack_shelter"]],
    "herbs": [["herb", "alchem", "apothec", "copper_still"],
              ["healer", "shamans_hut", "druid_priestess", "spirit_lodge", "elders_tent", "stall_bottles", "plague_vat"]],
    "wood": [["carver", "bowyer", "lumber", "sawmill"], ["log_pile", "felled_tree", "winch_house", "storehouse"],
             ["supply_store", "supply_depot", "supply_cache", "quartermaster", "granary"]],
    "hide": [["tannery", "tanner"], ["hide_rack", "drying_rack", "smokehouse", "kennel", "kodo_pen", "stable"]],
    "essence": [["workshop", "gazlowe", "siege"],
                ["wizard_desk", "warlock_tower", "pulley_hoist", "winch_house", "mixed_trading_post", "trading_post"]],
    "class": [["trainers_lodge", "training_pavilion", "novice_longhouse"],
              ["barracks", "war_hall", "sentinel_outpost_hall", "great_lodge", "elder_lodge", "elders_roundhouse",
               "taurajo_lodge", "command_tent", "command_war_tent", "town_hall", "warchief_lodge", "armoury"]],
}
#: how far from the innkeeper a building still counts as "in town". A zone that is just the town
#: (Razor Hill, Hammerfall, Brill...) counts all of it; a town inside a bigger zone (the Valley,
#: Freewind on its mesas, Southern Barrens) only what is near the inn.
TOWN_RADIUS = 30
TOWN_ZONE_AREA = 120 * 120
CAPITALS = {"Orgrimmar": 110, "Undercity": 110}


def flood(tm, start):
    seen, q = {start}, deque([start])
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            n = (x + dx, y + dy)
            if n not in seen and 0 <= n[0] < tm.width and 0 <= n[1] < tm.height and tm.is_walkable(*n):
                seen.add(n)
                q.append(n)
    return seen


def art(lm):
    return os.path.basename(lm["sprite_key"])[:-4]


def front_tile(tm, region, NC, box, taken, own):
    """The best free tile in front of a building box (ax, ay, w, h), or None."""
    ax, ay, w, h = box
    door = (ax + w // 2, ay + h)
    best = None
    for y in range(ay + h - 1, ay + h + 6):
        for x in range(ax - 3, ax + w + 3):
            if (x, y) not in region or (x, y) in taken:
                continue
            kind = tm.interaction_layer[y][x]
            if kind and (x, y) != own:
                continue
            if any((x + dx, y + dy) in taken for dx in (-1, 0, 1) for dy in (-1, 0, 1)):
                continue
            if any(NC.covered(lm, x, y) > 0.15 for lm in tm.landmarks
                   if lm["anchor_x"] - 2 <= x < lm["anchor_x"] + lm["width_tiles"] + 2
                   and lm["anchor_y"] - 8 <= y < lm["anchor_y"] + lm["height_tiles"] + 2):
                continue
            open_n = sum((x + dx, y + dy) in region for dx in (-1, 0, 1) for dy in (-1, 0, 1) if dx or dy)
            if open_n < 5:
                continue
            d = abs(x - door[0]) + abs(y - door[1])
            score = d + (3 if y < ay + h else 0) - open_n * 0.2
            if best is None or score < best[0]:
                best = (score, x, y)
    return (best[1], best[2]) if best else None


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        import pygame
        pygame.init()
        pygame.display.set_mode((64, 64))
        import build_class_trainers as bct
        from world.zone_manager import ZoneManager
        from world import npc_clearance as NC
        zm = ZoneManager()
    amb_path = ROOT / "data" / "npcs" / "ambient_npcs.json"
    amb = json.loads(amb_path.read_text(encoding="utf-8"))
    by_id = {n["npc_id"]: n for n in amb["npcs"]}
    vend = json.loads((ROOT / "data" / "npcs" / "vendors.json").read_text(encoding="utf-8"))["vendors"]
    forges = json.loads((ROOT / "data" / "npcs" / "forges.json").read_text(encoding="utf-8"))["forges"]
    mills = json.loads((ROOT / "data" / "npcs" / "sawmills.json").read_text(encoding="utf-8"))["sawmills"]

    def norm(s):
        return s.lower().replace(" ", "_").replace("'", "")

    # A town laid out by hand (Hammerfall, Cinderwharf) already stands its trainers where its
    # designer meant them, in its own NPC_POSITIONS. Those win: this pass only copies them over.
    import re
    pinned = {}
    for mod in (ROOT / "tools").glob("handbuilt_*.py"):
        for m in re.finditer(r'"((?:pt|ct)_\w+)":\s*\((\d+),\s*(\d+)\)', mod.read_text(encoding="utf-8")):
            pinned[m.group(1)] = (int(m.group(2)), int(m.group(3)))

    moved, kept = [], []
    for zone_name, (slug, anchor_id) in bct.TOWNS.items():
        entry = zm.zones.get(zone_name)
        if entry is None:
            print("MISSING ZONE", zone_name)
            continue
        tm = entry["tilemap"]
        zk = bct.ZONE_FIELD.get(zone_name, norm(zone_name))
        inn = by_id.get(anchor_id) or next((v for v in vend if v.get("vendor_id") == anchor_id), None)
        mine = [n for n in amb["npcs"] if n["npc_id"] == f"ct_{slug}" or n["npc_id"].startswith(f"pt_{slug}_")]
        if not mine:
            continue
        centre = (inn["x"], inn["y"]) if inn else (mine[0]["x"], mine[0]["y"])
        radius = CAPITALS.get(zone_name, 999 if tm.width * tm.height < TOWN_ZONE_AREA else TOWN_RADIUS)
        start = next(((centre[0] + dx, centre[1] + dy) for dx in range(-2, 3) for dy in range(-2, 3)
                      if tm.is_walkable(centre[0] + dx, centre[1] + dy)), None)
        region = flood(tm, start)
        # every NPC tile in the zone, minus the trainers being placed
        taken = {(x, y) for y, row in enumerate(tm.interaction_layer) for x, k in enumerate(row) if k == "npc"}
        taken -= {(n["x"], n["y"]) for n in mine}
        objects = {(f["x"], f["y"]) for f in forges if norm(f["zone"]) == zk} | \
                  {(s["x"], s["y"]) for s in mills if norm(s["zone"]) == zk}
        buildings = [lm for lm in tm.landmarks if lm["width_tiles"] * lm["height_tiles"] >= 9
                     and abs(lm["anchor_x"] + lm["width_tiles"] // 2 - centre[0])
                     + abs(lm["anchor_y"] + lm["height_tiles"] - centre[1]) <= radius]
        used = set()
        if os.environ.get("DEBUG_TOWN") == zone_name:
            for lm in tm.landmarks:
                if lm["width_tiles"] * lm["height_tiles"] >= 9 and any(k in art(lm) for tiers in TRADES.values() for t in tiers for k in t):
                    d = abs(lm["anchor_x"] + lm["width_tiles"] // 2 - centre[0]) + abs(lm["anchor_y"] + lm["height_tiles"] - centre[1])
                    ft = front_tile(tm, region, NC, (lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"]), taken | objects, None)
                    print("DBG", art(lm), (lm["anchor_x"], lm["anchor_y"]), "dist", d, "front", ft)
        # the class trainer first: the hall is the town's most obvious building
        order = sorted(mine, key=lambda n: (not n["npc_id"].startswith("ct_"), n["npc_id"]))
        for n in order:
            if n["npc_id"] in pinned:
                n["x"], n["y"] = pinned[n["npc_id"]]
                moved.append(f"{zone_name:18} {n['npc_id']:24} pinned by hand at {pinned[n['npc_id']]}")
                taken.add(pinned[n["npc_id"]])
                continue
            trade = "class" if n["npc_id"].startswith("ct_") else n["npc_id"].rsplit("_", 1)[1]
            boxes = []
            # the forge and the sawmill are objects, not buildings: stand beside them
            if trade == "forge":
                boxes += [(f["x"] - 1, f["y"] - 1, 3, 2, "forge") for f in forges if norm(f["zone"]) == zk
                          and abs(f["x"] - centre[0]) + abs(f["y"] - centre[1]) <= radius]
            if trade == "wood":
                boxes += [(s["x"] - 1, s["y"] - 1, 3, 2, "sawmill") for s in mills if norm(s["zone"]) == zk
                          and abs(s["x"] - centre[0]) + abs(s["y"] - centre[1]) <= radius]
            for tier in TRADES[trade]:
                hits = [lm for lm in buildings if any(k in art(lm) for k in tier) and id(lm) not in used]
                hits.sort(key=lambda lm: abs(lm["anchor_x"] + lm["width_tiles"] // 2 - centre[0])
                          + abs(lm["anchor_y"] + lm["height_tiles"] - centre[1]))
                boxes += [(lm["anchor_x"], lm["anchor_y"], lm["width_tiles"], lm["height_tiles"], lm) for lm in hits]
            spot = None
            for ax, ay, w, h, lm in boxes:
                spot = front_tile(tm, region, NC, (ax, ay, w, h), taken | objects, (n["x"], n["y"]))
                if spot:
                    if not isinstance(lm, str):
                        used.add(id(lm))
                    where = lm if isinstance(lm, str) else art(lm)
                    break
            if spot is None:
                tried = ", ".join(b[4] if isinstance(b[4], str) else art(b[4]) for b in boxes) or "nothing in town"
                kept.append(f"{zone_name:18} {n['npc_id']:24} stays at {(n['x'], n['y'])} (tried: {tried})")
                taken.add((n["x"], n["y"]))
                continue
            if spot != (n["x"], n["y"]):
                moved.append(f"{zone_name:18} {n['npc_id']:24} {(n['x'], n['y'])} -> {spot} at {where}")
            else:
                moved.append(f"{zone_name:18} {n['npc_id']:24} already at {where}")
            n["x"], n["y"] = spot
            n["facing"] = "down"
            taken.add(spot)
    print("\n".join(moved))
    print()
    print("\n".join(kept))
    if DRY:
        print("\ndry run, nothing written")
        return 0
    amb_path.write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {amb_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
