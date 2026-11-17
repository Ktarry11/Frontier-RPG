#!/usr/bin/env python3
"""Leatherworking's classic conversions: scraps to light to medium to heavy to thick to rugged, and they skill you up.

    PYTHONPATH=. python3 tools/qa_leather_conversions.py

Kyle, 16 Nov 2026: "for leatherworking - we need the classic conversion! Scraps to light to medium to heavy to thick
to rugged which can also give crafting skill". A new leatherworker, taught by a trainer, makes Light Leather from
scraps at skill 0, gains skill doing it, and every later step is taught and craftable at its skill.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

CHAIN = [("lw_cure_light_leather", "leather_scrap", 3, "leather_light", 0),
         ("lw_cure_medium_leather", "leather_light", 4, "leather_medium", 100),
         ("lw_cure_heavy_leather", "leather_medium", 5, "leather_heavy", 150),
         ("lw_cure_thick_leather", "leather_heavy", 6, "leather_thick", 200),
         ("lw_cure_rugged_leather", "leather_thick", 6, "leather_rugged", 250)]


def main():
    from entities.character import Character
    from world.leatherworking_manager import LeatherworkingManager
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        lm = LeatherworkingManager()
    c = Character(name="T", char_class="Warrior", level=60)
    c.learn_profession("leatherworking")
    c.profession_skills["leatherworking"] = 0
    for rid, src, n, out, skill in CHAIN:
        r = lm.recipes.get(rid)
        if r is None:
            bad.append(f"{rid} is missing")
            continue
        if r.get("inputs") != {src: n} or (r.get("output") or {}).get("material_id") != out:
            bad.append(f"{rid}: {r.get('inputs')} -> {r.get('output')}, wanted {n} {src} -> {out}")
        if r.get("skill_required") != skill or r.get("source") != "trainer":
            bad.append(f"{rid}: skill {r.get('skill_required')} from {r.get('source')}, wanted {skill} from a trainer")
    c.profession_tiers["leatherworking"] = 3
    c.learn_trainer_recipes("leatherworking", lm.recipes)
    rid, src, n, out, _s = CHAIN[0]
    c.add_material(_mat(src, n * 3))
    before = c.profession_skills.get("leatherworking", 0)
    made = [lm.craft(c, rid) for _ in range(3)]
    if not all(made):
        bad.append(f"a new leatherworker couldn't cure Light Leather at skill {before}")
    if c.get_material_quantity(out) < 3:
        bad.append(f"three crafts left {c.get_material_quantity(out)} Light Leather")
    after = c.profession_skills.get("leatherworking", 0)
    if after <= before:
        bad.append("curing Light Leather at skill 0 gave no skill")
    for rid, src, n, out, skill in CHAIN[1:]:
        c.profession_skills["leatherworking"] = skill
        c.learn_trainer_recipes("leatherworking", lm.recipes)      # a trainer visit at this skill
        if not c.knows_recipe(rid):
            bad.append(f"a trainer doesn't teach {rid} at skill {skill}")
        c.add_material(_mat(src, n))
        if not lm.craft(c, rid):
            bad.append(f"couldn't make {out} at skill {skill}")
    print(f"{len(CHAIN)} conversions; skill after three Light Leather: {before} -> "
          f"{after}")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print("PASS - scraps to light to medium to heavy to thick to rugged, taught, and they skill you up")
    return 0


def _mat(mid, n):
    from world.gathering_manager import GatheringNodeManager
    with contextlib.redirect_stdout(io.StringIO()):
        m = GatheringNodeManager().make_material_instance(mid)
    m.quantity = n
    return m


if __name__ == "__main__":
    sys.exit(main())
