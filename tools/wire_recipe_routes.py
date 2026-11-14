#!/usr/bin/env python3
"""Make every recipe's source label true: wire a real route for each one.

    PYTHONPATH=. python3 tools/wire_recipe_routes.py [--apply]

Idempotent and deterministic. Run it after any pass that changes recipe
sources - tools/rebalance_recipe_sources.py above all.

=============================================================================
WHY THIS HAD TO EXIST
=============================================================================

tools/rebalance_recipe_sources.py moved 214 recipes off trainers to hit Kyle's
40-60% target. It set the `source` field and stopped there, which is exactly
the bug tools/qa_recipe_sources.py was written to catch, and it caught it:

    "135 recipes carried source 'drop' and 57 carried 'vendor', every one of
     them was labelled as something you find or buy, and not one could be
     found or bought. Nothing failed, nothing warned; the labels were simply
     decoration."

I reproduced that defect at a smaller scale within the hour. A `source` is a
promise about how a player gets something, and writing the word is not keeping
the promise.

    drop    already honest. entities/recipe_drops.py derives its pool by
            creature level, so a recipe starts dropping the moment it is
            labelled. Nothing to wire.
    vendor  needs a vendor whose `sells` list names it.
    quest   needs a quest whose `reward_recipe` names it.

=============================================================================
HOW A ROUTE IS CHOSEN
=============================================================================

By level, so the recipe turns up where a player who can use it is standing.
Profession skill maps to character level at roughly five to one - the same
relationship entities/recipe_drops.py already assumes and the material ladders
imply - so a skill-150 pattern wants a level-30 zone.

Vendors: only those that ALREADY stock patterns are used. A recipe appearing
on a general goods seller who has never sold one is worse than no route.
Quests: only those with no reward_recipe yet, so nothing existing is displaced.

Both pick deterministically from the eligible set by md5 of the recipe id -
not hash(), which is salted per process and would reshuffle the world on every
run. If nothing eligible exists at the right level, the recipe falls back to
`drop`, which always works, rather than keeping a label that lies.
"""
import argparse
import collections
import glob
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SKILL_PER_LEVEL = 5
#: How far a route's level may sit from the recipe's own, before we look wider.
LEVEL_WINDOW = 8

def drop_pool():
    """Recipe ids a creature in this game can actually carry.

    Derived exactly as tools/qa_recipe_sources.py derives it, from the highest
    level any real creature reaches - NOT from a constant. The two must agree
    or this tool writes labels that suite then rejects.

    This bit me twice. entities.recipe_drops.eligible(60) returns recipes up to
    skill 300, which looks like the ceiling; but the highest creature in the
    game is level 48, so the real limit is 48 * 5 + 15 = 255. Guessing 300 left
    Elementium plans labelled `drop` that nothing alive could carry.
    """
    from entities.recipe_drops import eligible
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    top = max((max(c.get("level_range") or [1]) for c in creatures.values()), default=1)
    return set(eligible(top)), top

RECIPE_FILES = {
    "blacksmithing": ("data/blacksmithing/recipes.json", None),
    "leatherworking": ("data/leatherworking/recipes.json", None),
    "alchemy": ("data/crafting/recipes.json", "alchemy"),
    "tailoring": ("data/crafting/recipes.json", "tailoring"),
    "woodworking": ("data/crafting/recipes.json", "woodworking"),
    "engineering": ("data/crafting/recipes.json", "engineering"),
    "cooking": ("data/crafting/recipes.json", "cooking"),
    "woodcutting": ("data/crafting/recipes.json", "woodcutting"),
}


def slug(n):
    s = str(n).lower().replace(" ", "_").replace("'", "")
    return s[4:] if s.startswith("the_") else s


def deal(rid, options):
    """Stable pick. hashlib, not hash() - see docstring."""
    n = int(hashlib.md5(rid.encode()).hexdigest()[:8], 16)
    return options[n % len(options)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    from world.recipe_manager import _load_all_recipes
    recipes = _load_all_recipes()
    droppable, top_level = drop_pool()

    vdoc = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))
    vendors = vdoc["vendors"]
    bands = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]
    zband = {}
    for name, b in bands.items():
        zband.setdefault(slug(name), tuple(b))
        zband.setdefault(str(name).lower().replace(" ", "_").replace("'", ""), tuple(b))

    # who already has a route
    vendor_stock = set()
    for v in vendors:
        vendor_stock |= {s for s in v.get("sells", []) if s in recipes}

    qfiles = {}
    quest_rewards, free_quests = set(), []
    for p in sorted(set(glob.glob(str(ROOT / "data/quests/**/*.json"), recursive=True))):
        try:
            d = json.loads(Path(p).read_text(encoding="utf-8"))
        except Exception:
            continue
        qs = d.get("quests", d)
        if isinstance(qs, dict):
            qs = list(qs.values())
        if not isinstance(qs, list):
            continue
        touched = False
        for q in qs:
            if not isinstance(q, dict):
                continue
            if q.get("reward_recipe"):
                quest_rewards.add(q["reward_recipe"])
            elif q.get("quest_id") and q.get("level_min") is not None:
                free_quests.append((p, q))
            touched = True
        if touched:
            qfiles[p] = d

    # vendors that already sell patterns, with a level
    # Remember WHICH professions each one already stocks. An engineer selling
    # an alchemy flask recipe is the "no illogical shit" problem in vendor form -
    # level alone is not enough to pick a seller.
    pattern_vendors = []
    for v in vendors:
        profs = {recipes[s][0] for s in v.get("sells", []) if s in recipes}
        if not profs:
            continue
        b = zband.get(slug(v.get("zone", "")))
        if b:
            pattern_vendors.append((v, (b[0] + b[1]) / 2, profs))

    wired, fell_back, unroutable = [], [], []
    for rid, (prof, r) in sorted(recipes.items()):
        src = r.get("source", "trainer")
        if src == "trainer":
            continue
        if src == "drop":
            if rid in droppable:
                continue
            # labelled a drop that nothing alive can carry - needs a real route
            pass
        if src == "vendor" and rid in vendor_stock:
            continue
        if src == "quest" and rid in quest_rewards:
            continue
        want = r.get("skill_required", 0) / SKILL_PER_LEVEL

        if src == "vendor":
            # Same profession AND the right level first; then same profession at
            # any level; only then anyone who sells patterns at all.
            # Preference order, and the order matters more than it looks.
            # Profession-first alone put every alchemy recipe on the single
            # alchemy vendor, so a starter town stocked the Black Lotus flask.
            # Level-first alone put alchemy recipes on an engineer. So: the
            # right profession in the right place, then ANY pattern seller in
            # the right place, and only then stretch on level.
            same = [(v, lv) for v, lv, pr in pattern_vendors if prof in pr]
            allv = [(v, lv) for v, lv, _ in pattern_vendors]
            pool = [v for v, lv in same if abs(lv - want) <= LEVEL_WINDOW]
            if not pool:
                pool = [v for v, lv in allv if abs(lv - want) <= LEVEL_WINDOW]
            if not pool and same:
                best = min(abs(lv - want) for _, lv in same)
                pool = [v for v, lv in same if abs(lv - want) == best]
            if not pool and allv:
                best = min(abs(lv - want) for _, lv in allv)
                pool = [v for v, lv in allv if abs(lv - want) == best]
            if pool:
                v = deal(rid, pool)
                wired.append((rid, prof, "vendor", v.get("name"), want))
                if args.apply:
                    v.setdefault("sells", []).append(rid)
                    vendor_stock.add(rid)
                continue
        elif src == "quest":
            pool = [(p, q) for p, q in free_quests
                    if abs((q.get("level_min", 0) + q.get("level_max", 0)) / 2 - want) <= LEVEL_WINDOW]
            if pool:
                p, q = deal(rid, pool)
                wired.append((rid, prof, "quest", q.get("title", q["quest_id"]), want))
                if args.apply:
                    q["reward_recipe"] = rid
                quest_rewards.add(rid)
                free_quests.remove((p, q))
                continue

        # Nothing suitable. `drop` routes for anything a player can reach, but
        # NOT above the skill ceiling - the drop pool is derived from creature
        # level and tops out near 300 - so a forward-authored recipe goes back
        # to `trainer`, the one label that stays true when nobody can reach it.
        dest = "drop" if rid in droppable else "trainer"
        fell_back.append((rid, prof, src, want, dest))
        if args.apply:
            r["source"] = dest
            r.pop("vendor_location", None)

    print(f"  {len(recipes)} recipes checked")
    print(f"  creatures top out at level {top_level}, so {len(droppable)} recipes "
          f"can be carried by something alive\n")
    byk = collections.Counter(w[2] for w in wired)
    print(f"  WIRED {len(wired)}: " + (", ".join(f"{k} {v}" for k, v in sorted(byk.items())) or "-"))
    for rid, prof, kind, where, lv in wired[:14]:
        print(f"    {rid[:30]:32}{prof:15}{kind:7}lv~{lv:>5.0f}  {where}")
    if len(wired) > 14:
        print(f"    ... and {len(wired) - 14} more")

    if fell_back:
        print(f"\n  FELL BACK: {len(fell_back)} (no vendor or quest at the right level)")
        byp = collections.Counter((f[1], f[4]) for f in fell_back)
        for (p, d), n in sorted(byp.items()):
            print(f"    {p:16}-> {d:8}{n}")

    if args.apply:
        for rel in {v[0] for v in RECIPE_FILES.values()}:
            pass
        # recipe docs are mutated in place by _load_all_recipes' cache, so rewrite
        # each source file from disk with the new source fields
        for prof, (rel, key) in RECIPE_FILES.items():
            path = ROOT / rel
            doc = json.loads(path.read_text(encoding="utf-8"))
            rs = doc["professions"][key]["recipes"] if key else doc["recipes"]
            changed = False
            for rid, r in rs.items():
                if not isinstance(r, dict):
                    continue
                live = recipes.get(rid)
                if live and live[1].get("source") != r.get("source"):
                    r["source"] = live[1]["source"]
                    r.pop("vendor_location", None)
                    changed = True
            if changed:
                path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
        (ROOT / "data/npcs/vendors.json").write_text(json.dumps(vdoc, indent=2) + "\n", encoding="utf-8")
        for p, d in qfiles.items():
            Path(p).write_text(json.dumps(d, indent=2) + "\n", encoding="utf-8")
        print("\n  wrote vendors.json, quest files, recipe files")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
