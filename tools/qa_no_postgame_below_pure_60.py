"""Nothing post-game grows or drops anywhere that isn't a pure 60 zone.

Kyle, 16 Nov 2026: "this is CRITICAL that no post-game materials drop and no post-game gathering nodes in
zones that are NOT pure 60. So even though these zones go to 60, they are not at pure 60." Pure 60 is a band
of exactly 60 to 60 (his answer: "Yes, 60-60 only").

entities/material_tiers.is_postgame is the line and is_pure_60 the zone test, so this suite and the game
ask the same two questions. It checks:
  1. gathering node pools (herbs, ore, wood) and fishing tables, per zone
  2. ore veins' gem and crystal side-rolls, for every ore that is placed below pure 60
  3. creature-dropped crafting materials, by every zone the creature lives in
  4. the cloth, leather and recipe rolls themselves, for a level 60 creature in a 55-60 zone, a level 60
     creature in an unknown zone, and a level 63 boss, many times over
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from entities import material_tiers as T  # noqa: E402

fails = []


def check(label, bad):
    print(f"  {'PASS' if not bad else 'FAIL'}  {label}" + (f"  {bad[:8]}" if bad else ""))
    if bad:
        fails.append(label)


mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
pools = json.loads((ROOT / "data/gathering/node_pools.json").read_text(encoding="utf-8"))["zones"]

print("== 1. node pools and fishing tables")
bad_nodes, bad_fish, placed_ores = [], [], set()
for zone, spec in pools.items():
    pure = T.is_pure_60(zone)
    for mid in (spec.get("table") or {}):
        if not pure:
            placed_ores.add(mid)
            if T.is_postgame(mid, mats):
                bad_nodes.append(f"{zone}:{mid}")
    for mid in ((spec.get("fishing") or {}).get("table") or {}):
        if not pure and T.is_postgame(mid, mats):
            bad_fish.append(f"{zone}:{mid}")
check("no post-game node in a zone below pure 60", bad_nodes)
check("no post-game fish in a zone below pure 60", bad_fish)

print("== 2. what an ore vein below pure 60 can give up")
from world.gathering_manager import get_gathering_node_manager  # noqa: E402
gm = get_gathering_node_manager()
bad_gem = []
for ore in sorted(placed_ores):
    for gem_id, _c in gm.gem_table().get(ore, ()):
        if T.is_postgame(gem_id, mats):
            bad_gem.append(f"{ore}->{gem_id}")
    tier = (mats.get(ore) or {}).get("tier")
    if (mats.get(ore) or {}).get("material_type") == "ore":
        for crystal in gm.CRYSTAL_FROM_VEIN.get(tier, ()):
            if T.is_postgame(crystal, mats):
                bad_gem.append(f"{ore}->{crystal}")
check("no post-game gem or crystal from a placed vein", bad_gem)

print("== 3. creature-dropped materials")
mm_path = ROOT / "data/gathering/mob_materials.json"
bad_mob = []
if mm_path.exists():
    mm = json.loads(mm_path.read_text(encoding="utf-8")).get("materials", {})
    for mid, d in mm.items():
        if T.is_postgame(mid, mats) and not all(T.is_pure_60(z) for z in (d.get("zones") or ["?"])):
            bad_mob.append(mid)
check("no post-game creature material outside pure 60", bad_mob)

print("== 4. the rolls themselves")
from entities.cloth_drops import roll_cloth  # noqa: E402
from entities.skinning_drops import roll_leather  # noqa: E402
from entities.recipe_drops import roll_recipe  # noqa: E402


class Foe:
    def __init__(self, name, level, boss):
        self.name, self.level, self.is_boss = name, level, boss
        self.location_type = "dungeon"


rng = random.Random(60)
bad_roll = []
for zone in ("steamwheedle_port", "the_emberdeep", None, "zone_that_does_not_exist"):
    T.set_active_zone(zone)
    for level in (59, 60, 63):
        for _ in range(400):
            got = [m for m, _q in roll_cloth(Foe("Kolkar Centaur", level, True), rng)]
            got += [m for m, _q in roll_leather(Foe("Plagued Wolf", level, True), rng=rng)]
            r = roll_recipe(Foe("Kolkar Centaur", level, True), rng)
            for m in got:
                if T.is_postgame(m, mats):
                    bad_roll.append(f"{zone}@{level}:{m}")
            rid = getattr(r, "item_id", None) or (r if isinstance(r, str) else None)
            if rid and T.is_postgame(rid, mats):
                bad_roll.append(f"{zone}@{level}:{rid}")
T.set_active_zone(None)
check("a level 60+ creature below pure 60 rolls nothing post-game", sorted(set(bad_roll)))
check("an unknown zone counts as below pure 60", [] if not T.is_pure_60(None) and not T.is_pure_60("nowhere") else ["unknown"])

print()
if fails:
    print(f"{len(fails)} problem(s)")
    sys.exit(1)
print("Nothing post-game below pure 60.")
