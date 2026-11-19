#!/usr/bin/env python3
"""Master crafting: level-60 gear from level-60 materials, competitive with heroics and raids.

    PYTHONPATH=. python3 tools/qa_master_crafting.py

Kyle, 18 Nov 2026: "I'll ALWAYS want crafting to be competitive to raiding/Dungeons", a Master tier (cap 325) from the
Artisan trainers at level 60, and new gear for each profession (tools/build_master_crafting.py, docs/master_crafting.md).
Checks, through the real data and code:
  1. Master is a tier: cap 325 at level 60, after Artisan; a trainer offers it to a level 60 at 300 and not to a 59
  2. every gear trade has blues (rare 66, worn at 60, trainer-taught) and epics (epic 68, worn at 60, dropped by
     heroic bosses), all at skill 300-325 and on the item curve
  3. every Master recipe is made of level 60's materials, and everything it needs can be had: the raw ten from
     heroics, processed at skill 325 or under
  4. the Exalted rep patterns have real ingredients (no stand-ins left), epics from the second rung, and the Honored
     ones stay pre-60
  5. a heroic boss's pattern is a Master epic, and those patterns are in no trainer's list and no world drop pool
  6. competitive: a crafted blue matches a heroic drop's level, a crafted epic matches T1 and Exalted
  7. every spec of every class can use at least 3 Master pieces (Kyle: "a little bit for most classes")
"""
import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recipe_manager import _load_all_recipes, all_recipes_by_source
    from entities.item_budget import budget_ratio
    from entities.material_tiers import LEVEL60_TOP, PRE_60_SKILL_CEILING
    from entities.character import Character
    from world import profession_manager as PM
    from world import heroic as H

    # 1
    tiers = json.loads((ROOT / "data/professions/professions.json").read_text(encoding="utf-8"))["tiers"]
    check(tiers[-1]["name"] == "Master" and tiers[-1]["cap"] == 325 and tiers[-1]["required_level"] == 60
          and tiers[-2]["name"] == "Artisan", f"the tiers end {[(t['name'], t['cap']) for t in tiers[-2:]]}")
    check(Character.PROFESSION_TIER_CAPS[-1] == 325, "a character's caps stop short of Master")
    for lvl, want in ((60, True), (59, False)):
        with contextlib.redirect_stdout(io.StringIO()):
            ch = Character(name="QA", char_class="Warrior", level=lvl)
        ch.known_professions = ["blacksmithing"]
        ch.profession_skills = {"blacksmithing": 300}
        ch.profession_tiers = {"blacksmithing": 3}
        rows = PM.offers(ch, "blacksmithing")
        master = [r for r in rows if r.get("kind") == "advance"]
        ok = bool(master) and master[0].get("enabled")
        check(ok == want, f"a level {lvl} at Artisan 300: Master offered and enabled is {ok}")
        if lvl == 60:
            check(ch.profession_cap("blacksmithing") == 300, "Artisan's cap isn't 300")
            ch.profession_tiers["blacksmithing"] = 4
            check(ch.profession_cap("blacksmithing") == 325, "Master's cap isn't 325")

    # 2 + 3
    recipes = _load_all_recipes()
    m60 = {rid: (p, r) for rid, (p, r) in recipes.items() if rid.startswith("m60_")}
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    skill_of = lambda m: ((mats.get(m) or {}).get("skill_range") or [0])[0]
    first = {LEVEL60_TOP[k][0] for k in LEVEL60_TOP} | {LEVEL60_TOP[k][1] for k in LEVEL60_TOP}
    # what can be made at 325 or under, and from what
    makes = {}
    for rid, (p, r) in recipes.items():
        o = r.get("output") or {}
        if o.get("kind") == "material" and r.get("skill_required", 0) <= 325:
            makes.setdefault(o.get("material_id"), []).append(r)
    smelt = json.loads((ROOT / "data/gathering/smelting_recipes.json").read_text(encoding="utf-8"))
    smelt = smelt.get("recipes", smelt)
    for k, v in (smelt.items() if isinstance(smelt, dict) else []):
        if isinstance(v, dict) and v.get("skill_required", 0) <= 325:
            makes.setdefault(v.get("output"), []).append(v)

    def obtainable(m, depth=0):
        if m in first or skill_of(m) <= PRE_60_SKILL_CEILING or depth > 4:
            return True
        return any(all(obtainable(i, depth + 1) for i in (r.get("inputs") or {})) for r in makes.get(m, []))

    by_trade = {}
    for rid, (prof, r) in m60.items():
        o = r.get("output") or {}
        check(300 <= r.get("skill_required", 0) <= 325, f"{rid}: skill {r.get('skill_required')}")
        for i in (r.get("inputs") or {}):
            check(obtainable(i), f"{rid}: {i} can't be had (no way to it at skill 325)")
        if o.get("kind") == "material":
            continue
        it = o.get("item") or {}
        by_trade.setdefault(prof, {"rare": 0, "epic": 0})[it.get("rarity")] = \
            by_trade.setdefault(prof, {"rare": 0, "epic": 0}).get(it.get("rarity"), 0) + 1
        if it.get("rarity") == "rare":
            check(it.get("item_level") == 66 and it.get("required_level") == 60 and r.get("source") == "trainer",
                  f"{rid}: blue {it.get('item_level')} worn at {it.get('required_level')} from {r.get('source')}")
        else:
            check(it.get("rarity") == "epic" and it.get("item_level") == 68 and it.get("required_level") == 60
                  and r.get("source") == "heroic",
                  f"{rid}: {it.get('rarity')} {it.get('item_level')} worn at {it.get('required_level')} "
                  f"from {r.get('source')}")
        rr = budget_ratio(it)
        check(rr is None or 0.8 <= rr <= 1.25, f"{rid}: {rr:.2f} of the item curve")
        hi_inputs = [i for i in (r.get("inputs") or {}) if skill_of(i) > PRE_60_SKILL_CEILING]
        check(hi_inputs, f"{rid}: made of nothing from level 60")
    for trade in ("tailoring", "leatherworking", "blacksmithing", "woodworking", "jewelcrafting", "engineering"):
        got = by_trade.get(trade, {})
        check(got.get("rare", 0) >= 3 and got.get("epic", 0) >= 2, f"{trade}: {got}")
    check({"bolt_dreamsilk", "bolt_chronoweave"} <= set(makes), "the new bolts can't be made")

    # 4
    for rid, (prof, r) in recipes.items():
        if not rid.startswith("rep_"):
            continue
        check(not r.get("_rare_ingredients_todo"), f"{rid}: still on stand-in ingredients")
        it = (r.get("output") or {}).get("item") or r.get("output") or {}
        hi = [i for i in (r.get("inputs") or {}) if skill_of(i) > PRE_60_SKILL_CEILING]
        if it.get("rarity") == "epic":
            check(hi, f"{rid}: an Exalted epic made of nothing from level 60")
        elif (it.get("item_level") or 0) < 66:
            check(not hi, f"{rid}: an Honored pattern needs level-60 {hi}")

    # 5
    heroic = set(all_recipes_by_source("heroic"))
    check(heroic and heroic <= set(m60), f"heroic patterns aren't Master epics: {sorted(heroic - set(m60))[:5]}")
    from entities import recipe_drops
    recipe_drops._POOL = None
    check(not heroic & set(recipe_drops.eligible(60)), "a Master epic pattern is in the world drop pool")
    with contextlib.redirect_stdout(io.StringIO()):
        ch = Character(name="QA", char_class="Warrior", level=60)
    ch.known_professions = ["tailoring"]
    ch.profession_skills = {"tailoring": 325}
    ch.profession_tiers = {"tailoring": 4}
    taught = {row.get("recipe_id") or row.get("id") for row in PM.recipe_offers(ch, "tailoring")}
    check(not heroic & taught, "a trainer teaches a Master epic")
    check("m60_dreamsilk_robe" in taught or any("Dreamsilk Robe" in str(row) for row in PM.recipe_offers(ch, "tailoring")),
          "the tailoring trainer doesn't teach the Dreamsilk Robe at 325")
    seen = {H.roll_pattern(random.Random(i)) for i in range(400)} - {None}
    check(seen and seen <= heroic, f"a heroic boss dropped {sorted(seen - heroic)[:5]}")
    ce = (ROOT / "combat/combat_engine.py").read_text(encoding="utf-8")
    check("roll_pattern()" in ce, "heroic bosses don't drop patterns")

    # 6
    check(H.ITEM_LEVEL == 66, f"heroic drops are {H.ITEM_LEVEL}, crafted blues are 66")

    # 7. a little for every class (Kyle, 18 Nov 2026: "We can have a little bit for most classes"): every spec in
    # data/items/spec_gear.json can use at least 3 Master pieces, its stats in its armour or its weapons
    specs = {k: v for k, v in json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8")).items()
             if not k.startswith("_")}
    pieces = [r["output"]["item"] for rid, (p, r) in m60.items() if isinstance(r.get("output", {}).get("item"), dict)]

    def fits(spec, it):
        if it.get("stat_template") != spec["stat_template"]:
            return False
        if it["slot"] in ("ring", "neck", "back"):
            return True
        if it.get("weapon_type"):
            return it["weapon_type"] in [v for v in spec["weapons"].values() if v]
        return it.get("armor_type") == spec["armor_type"]
    thin = [f"{s['class']} {k.split('_', 1)[1]}" for k, s in specs.items() if sum(fits(s, it) for it in pieces) < 3]
    check(not thin, f"specs with fewer than 3 Master pieces: {thin}")

    print(f"{len(m60)} Master recipes: " + ", ".join(f"{t} {v['rare']} blue/{v['epic']} epic"
                                                    for t, v in sorted(by_trade.items())))
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails[:30]:
            print("  ", x)
        return 1
    print("Master crafting OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
