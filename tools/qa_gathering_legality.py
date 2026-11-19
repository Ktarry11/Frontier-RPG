"""Every gathering node must be a real material, and legal for its level.

Kyle, 10 Nov 2026: "DO 100% ENSURE THAT THE GATHERABLES ARE NOT BEING MADE UP
... So this means that something that is 54-60....fuck, even 58-60 wont have
high end frontier nodes."

TWO FAILURES THIS CATCHES, both of which happened while designing Tempest
Isle and neither of which any existing suite would have noticed:

1. AN INVENTED ID. `wood_bloodwood_log` was written into a design from the
   material's DISPLAY NAME ("Bloodwood Log"). The real id is
   `wood_bloodwood_tree`. A node pool referencing an id that does not exist
   does not crash - it just never spawns anything, so the zone quietly has
   less gathering than it was designed with.

2. A GATED MATERIAL THAT LOOKS LOW. `leather_hydra` sits at skill 215, below
   Rugged Leather's 260, so by the numbers it reads as mid-ladder. It is in
   HIGH_TIER_LEATHER and must never be served below level 60. Reading the
   skill number instead of asking entities/material_tiers.py is how a
   post-60 material ends up in a level-52 zone.

The authority is `entities/material_tiers.py`, not a design document and not
the skill number: "THE LINE IS TIER HEIGHT, NOT WHERE THE NAME CAME FROM."
This suite asks that module directly, so if the ceiling ever moves, the test
moves with it rather than disagreeing with it.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.material_tiers import HIGH_TIER, HIGH_TIER_FLOOR

failures = []


def check(label, condition, detail=""):
    if condition:
        print(f"  PASS  {label}")
    else:
        print(f"  FAIL  {label}  {detail}")
        failures.append(label)


materials = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
pools = json.loads((ROOT / "data/gathering/node_pools.json").read_text(encoding="utf-8"))["zones"]

print(f"== every node id in every zone pool is a real material "
      f"({len(pools)} zones)")
invented = []
for zone, spec in pools.items():
    for mid in (spec.get("table") or {}):
        if mid not in materials:
            invented.append(f"{zone}:{mid}")
check("no invented material ids", not invented, f"{invented[:6]}")

print("\n== no zone pool serves a material gated above level 60")
gated = []
for zone, spec in pools.items():
    for mid in (spec.get("table") or {}):
        if mid in HIGH_TIER:
            gated.append(f"{zone}:{mid}")
check(f"nothing from HIGH_TIER (floor {HIGH_TIER_FLOOR}) is placed", not gated,
      f"{gated[:6]}")

print("\n== the pre-60 line is skill 300 for ore and wood too")
# Kyle, 16 Nov 2026, on Ashen Steel and Starleaf (skill 260, placed in Felwood): "No we keep it as it
# is. We want a backlog of around 16-18 materials as end game only so crafting can get tiers (like raid
# tiers)." The old ceilings here (ore at Thorium, wood never on the "endgame" tier label) predate the
# "go to skill 300" crafting canon and were failing on exactly those two. The line is now the same one
# the game uses, material_tiers.is_postgame, and qa_no_postgame_below_pure_60 holds it per zone band.
from entities.material_tiers import is_postgame
over = []
for zone, spec in pools.items():
    for mid in (spec.get("table") or {}):
        mat = materials.get(mid)
        if mat and mat.get("material_type") in ("ore", "bar", "wood", "plank") and is_postgame(mid, materials):
            over.append(f"{zone}:{mid}")
check("no placed ore or wood above the pre-60 line", not over, f"{over[:6]}")

print("\n== each ladder keeps its end-game backlog (about 16-18 tiers held for raid-tier crafting)")
from collections import Counter
held = Counter(m.get("material_type") for mid, m in materials.items() if is_postgame(mid, materials))
# 18 Nov 2026: wood is 15. Emberwood, Frostheart and Ebonthorn came below the line because the pre-60 woodworking
# tier was built on them and they grew nowhere (Kyle: "Nothing sub 60 should use lvl 60 materials";
# tools/fix_pre60_woods.py). Kyle was told it's one short of his 16; a new end-game wood is his call.
FLOOR = {"wood": 15}
thin = [f"{kind}:{held[kind]}" for kind in ("ore", "wood", "cloth", "leather", "gem") if held[kind] < FLOOR.get(kind, 16)]
check("ore, cloth, leather and gems each hold 16+ end-game-only tiers, wood 15+", not thin, f"{thin}")

print("\n== Tempest Isle specifically")
for zone in ("tempest_shallows", "ashen_reach"):
    check(f"{zone} has a node pool", zone in pools)

if "ashen_reach" in pools:
    reach = set(pools["ashen_reach"]["table"])
    # This is the whole point of the zone: the terminal tier had been
    # authored for weeks with nowhere to gather it.
    check("the Ashen Reach opens Thorium", "ore_thorium" in reach)
    check("the Ashen Reach has Dark Iron, under a Dark Iron city",
          "ore_dark_iron" in reach)

print("\n== weights are sane")
bad_w = []
for zone, spec in pools.items():
    for mid, w in (spec.get("table") or {}).items():
        if not isinstance(w, int) or w < 1:
            bad_w.append(f"{zone}:{mid}={w}")
check("every weight is a positive integer", not bad_w, f"{bad_w[:6]}")

print()
if failures:
    print(f"FAILED ({len(failures)}): " + ", ".join(failures))
    sys.exit(1)
print(f"All gathering legality checks passed across {len(pools)} zone pools.")
