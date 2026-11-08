#!/usr/bin/env python3
"""What plants, ore, leather, trees and cloth drop where - and whether they do anything.

    PYTHONPATH=. python3 tools/audit_material_bands.py [--roles] [--csv out.csv]

Kyle, 7 Nov 2026: "an audit about what plants, what ore, what leather, what
trees, and what cloth drops where? We should have it based on a level band,
like wow."

=============================================================================
THE BASELINE, STATED BEFORE ANY COMPARISON. Read this before trusting a number.
=============================================================================

I got this wrong twice before getting it right, both times by inventing a
baseline instead of reading the game's own, so the wrong ones are written down
here too - they are the tempting answers.

WRONG #1: "expected level = skill / 5 + 1", taken from
world/crafting_manager.py's `item_level = int(skill * 60 / 300) + 1`. That
formula converts a RECIPE's skill requirement into a stat budget for the item
it produces. It says nothing about which character level should be gathering a
material. Using it reported 202 findings, nearly all of them phantom.

WRONG #2: "a material carrying a real WoW name should sit at its real WoW
skill" - i.e. Thorium at 230 rather than Frontier's 90. Checked against the
real Classic numbers (wow-professions.com, warcraft.wiki.gg: Stranglekelp 85,
Kingsblood 125, Liferoot 150, Khadgar's Whisker 185, Ghost Mushroom 245 - all
of which Frontier's late herbs already match exactly). It looked like every
WoW-named material was crammed into the bottom third of the ladder.

It is not a ladder. Kyle, 7 Nov: "I always found wow's crafting to be too
limited. So I added more stuff while leveling and we will MASSIVELY expand out
end game. Also I don't like that one ore, or cloth, or herb makes multiple
things. Like for me having different cloth being specialized is ideal. Want
Healer gear? Use cotton. Want dps? Use hemp."

So Linen/Wool/Cotton/Hempen at skill 5/15/20/25 are four PARALLEL early cloths,
not four rungs. Forty materials per type against WoW's eight is the design, and
rescaling them onto WoW's numbers would have destroyed it. WoW is a reference
for where a BAND sits, never for what an individual material is worth.

RIGHT: the gate is the trainer ladder, which the game already ships in
data/professions/professions.json and enforces in Character.profession_cap:

      skill    tier         character level
      1- 75    Apprentice   1
     76-150    Journeyman   10
    151-225    Expert       25
    226-300    Artisan      40
      >300     no tier exists - ungatherable by anyone, at any level

A node is MISPLACED when the zone it spawns in tops out below the level needed
to train the skill that node requires. That is the whole test, and it is the
game's own rule rather than one of mine.

Above skill 300 is deliberate forward authoring for the endgame expansion
("we will MASSIVELY expand out end game"), not a bug - 14-16 materials per
type sit up there waiting for a fifth tier. They are counted, never flagged.

=============================================================================
THE SECOND HALF: does the material DO anything?
=============================================================================

"Drops where" is only half of Kyle's question, because a node in the right zone
that feeds no recipe is still a dead node. So this also walks every recipe in
every profession - following ore -> bar -> gear, cloth -> bolt -> gear - and
reports which stat_templates each material can ultimately reach.

That is the axis Kyle's specialization idea runs on: cotton for healer gear and
hemp for dps means the two must reach DIFFERENT templates. Two materials in one
band reaching the identical set are interchangeable, which is the thing he said
he does not want, and this reports them as such.

WATCH OUT - smelting_recipes.json writes `"output": "bar_copper"` as a bare
string while every other recipe file writes `"output": {...}`. Skipping the
string form silently severs all 26 ores from their bars and reports mining as
entirely dead. One rule, two schemas, again.
"""
import argparse
import collections
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (skill cap, tier name, character level that can train it). Mirrors
#: data/professions/professions.json. Read from the file at runtime so this
#: cannot drift from the game; the literal is the fallback only.
FALLBACK_TIERS = [(75, "Apprentice", 1), (150, "Journeyman", 10),
                  (225, "Expert", 25), (300, "Artisan", 40)]

#: Types a player gathers or loots directly. The rest (bar, bolt, plank,
#: upgrade_kit, part, reagent) are crafted intermediates and are checked only
#: as links in a chain.
GATHERED = ("herb", "ore", "wood", "cloth", "leather")

RECIPE_FILES = ("data/blacksmithing/recipes.json", "data/crafting/recipes.json",
                "data/leatherworking/recipes.json", "data/gathering/smelting_recipes.json")


def load(rel):
    with open(ROOT / rel) as f:
        return json.load(f)


def tiers():
    try:
        t = load("data/professions/professions.json")["tiers"]
        return [(x["cap"], x["name"], x["required_level"]) for x in t]
    except Exception:
        return FALLBACK_TIERS


def gate(skill, ladder):
    """(tier name, min character level) that can hold this skill."""
    for cap, name, lvl in ladder:
        if skill <= cap:
            return name, lvl
    return None, None          # past the last tier: nobody can train it


def all_recipes():
    out = {}
    for rel in RECIPE_FILES:
        try:
            d = load(rel)
        except OSError:
            continue
        if "professions" in d:
            for pd in d["professions"].values():
                for rid, r in (pd.get("recipes") or {}).items():
                    if isinstance(r, dict):
                        out[rid] = r
        else:
            for rid, r in (d.get("recipes") or {}).items():
                if isinstance(r, dict):
                    out[rid] = r
    return out


def role_map():
    """(roles, used) where
         roles[mid] = stat_templates mid can ultimately reach, and
         used      = every material that is an input to ANY recipe.

    BOTH, because roles alone gave me a badly wrong answer. Counting only
    recipes whose output carries a stat_template treats a POTION as nothing, so
    alchemy's 72 recipes vanished and the audit reported 14 of 16 herbs as
    feeding nothing. Every herb is used. A material can be perfectly alive and
    reach no stat_template at all - that is what a consumable profession looks
    like - so "unused" and "reaches no gear" are two different findings and get
    reported separately.
    """
    roles = collections.defaultdict(set)
    feeds = collections.defaultdict(set)
    used = set()
    for r in all_recipes().values():
        inputs = r.get("inputs")
        out = r.get("output")
        if not isinstance(inputs, dict):
            continue
        used |= set(inputs)
        if isinstance(out, str):                       # smelting's bare-string form
            for inp in inputs:
                feeds[inp].add(out)
            continue
        if not isinstance(out, dict):
            continue
        tmpl = out.get("stat_template")
        for inp in inputs:
            if out.get("kind") == "material":
                feeds[inp].add(out.get("material_id"))
            elif tmpl:
                roles[inp].add(tmpl)
    for _ in range(4):                                 # ore -> bar -> gear, cloth -> bolt -> gear
        for m, outs in list(feeds.items()):
            for o in outs:
                roles[m] |= roles.get(o, set())
    return roles, used


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--roles", action="store_true", help="per-material role table")
    ap.add_argument("--csv", default=None)
    args = ap.parse_args()

    mats = load("data/gathering/materials.json")["materials"]
    pools = load("data/gathering/node_pools.json")["zones"]
    bands = load("data/zones/zone_levels.json")["zones"]
    ladder = tiers()
    roles, used = role_map()

    # node_pools.json keys drop a leading "The" that zone_levels.json keeps, so
    # "The Abyssal Sands" vs "abyssal_sands". Without stripping it, that zone
    # reported as having no level band at all - a phantom finding that sent me
    # looking for a missing band instead of a slug mismatch.
    def slug(n):
        s = str(n).lower().replace(" ", "_").replace("'", "")
        return s[4:] if s.startswith("the_") else s
    band_by_slug = {}
    for k, v in bands.items():
        band_by_slug.setdefault(slug(k), v)
        band_by_slug.setdefault(str(k).lower().replace(" ", "_").replace("'", ""), v)

    print("  gate = trainer ladder, data/professions/professions.json: "
          + ", ".join(f"{c}@lv{l}" for c, _, l in ladder))

    # ---------------------------------------------------------------- placement
    rows, unbanded, okn = [], [], 0
    for zkey, pool in pools.items():
        bd = band_by_slug.get(zkey)
        if not bd:
            unbanded.append(zkey)
            continue
        lo, hi = bd
        for mid in (pool.get("table") or {}):
            m = mats.get(mid)
            if not m:
                rows.append((zkey, mid, "?", None, lo, hi, "NO SUCH MATERIAL"))
                continue
            sr = m.get("skill_range")
            if not sr:
                rows.append((zkey, mid, m["material_type"], None, lo, hi, "no skill_range"))
                continue
            tname, need = gate(sr[0], ladder)
            if need is None:
                rows.append((zkey, mid, m["material_type"], sr[0], lo, hi,
                             "no trainer tier reaches this skill"))
            elif need > hi:
                rows.append((zkey, mid, m["material_type"], sr[0], lo, hi,
                             f"needs {tname} (lv {need}), zone tops at {hi}"))
            else:
                okn += 1

    print(f"\n  PLACEMENT  {okn + len(rows)} node placements over {len(pools)} zones")
    print(f"             {okn} reachable at the zone's own level, {len(rows)} not")
    if unbanded:
        print(f"             no level band so unchecked: {', '.join(sorted(unbanded))}")
    if rows:
        print(f"\n  {'zone':24}{'material':24}{'type':8}{'skill':>6}{'band':>9}   verdict")
        for z, mid, t, s, lo, hi, v in sorted(rows):
            print(f"  {z[:23]:24}{mats.get(mid,{}).get('name',mid)[:23]:24}"
                  f"{t:8}{str(s):>6}{f'{lo}-{hi}':>9}   {v}")

    # ------------------------------------------------------------------- chains
    print(f"\n  CHAINS     UNUSED = input to no recipe at all, the real defect.")
    print(f"             NO GEAR = used, but reaches no stat_template - normal for a")
    print(f"             consumable line (every herb is here; alchemy makes potions).")
    print(f"             above skill {ladder[-1][0]} = forward-authored endgame, not counted.")
    print(f"\n  {'type':9}{'total':>7}{'<={0}'.format(ladder[-1][0]):>7}"
          f"{'unused':>8}{'no gear':>9}{'forward':>9}   unused ones")
    for t in GATHERED:
        every = [(m.get("skill_range") or [9999])[0] for m in mats.values()
                 if m["material_type"] == t]
        live = [(s, mid, m["name"]) for mid, m in mats.items()
                if m["material_type"] == t
                for s in [(m.get("skill_range") or [9999])[0]] if s <= ladder[-1][0]]
        unused = sorted((s, n) for s, mid, n in live if mid not in used)
        nogear = [1 for s, mid, n in live if mid in used and not roles.get(mid)]
        fwd = sum(1 for s in every if s > ladder[-1][0])
        names = ", ".join(f"{n} ({s})" for s, n in unused) if unused else "none"
        if len(names) > 58:
            names = f"{len(unused)} from skill {unused[0][0]} up"
        print(f"  {t:9}{len(every):>7}{len(live):>7}{len(unused):>8}"
              f"{len(nogear):>9}{fwd:>9}   {names}")

    # ----------------------------------------------- interchangeable in a band
    print(f"\n  SPECIALIZATION  materials in one tier reaching the IDENTICAL roles are")
    print(f"                  interchangeable, not specialized")
    for t in GATHERED:
        byrole = collections.defaultdict(list)
        for mid, m in mats.items():
            if m["material_type"] != t:
                continue
            s = (m.get("skill_range") or [9999])[0]
            if s > ladder[-1][0]:
                continue
            r = roles.get(mid)
            if r:
                byrole[(m["tier"], tuple(sorted(r)))].append(m["name"])
        dupes = {k: v for k, v in byrole.items() if len(v) > 1}
        if dupes:
            print(f"\n    {t}")
            for (tier, rs), names in sorted(dupes.items(), key=lambda kv: -len(kv[1])):
                print(f"      {len(names)} {tier} materials share {len(rs)} role(s): "
                      f"{', '.join(sorted(names))}")

    if args.roles:
        print("\n  --- per material ---")
        for t in GATHERED:
            print(f"\n  === {t} ===")
            for mid, m in sorted(mats.items(),
                                 key=lambda kv: (kv[1].get("skill_range") or [9999])[0]):
                if m["material_type"] != t:
                    continue
                s = (m.get("skill_range") or [9999])[0]
                if s > ladder[-1][0]:
                    continue
                r = sorted(roles.get(mid, ()))
                print(f"    {s:>4} {m['name'][:28]:30}{m['tier']:9}"
                      f"{len(r)}  {','.join(r) or 'FEEDS NOTHING'}")

    if args.csv:
        with open(args.csv, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["material", "name", "type", "tier", "skill", "min_level",
                        "reaches_roles", "zones"])
            where = collections.defaultdict(list)
            for z, pool in pools.items():
                for mid in (pool.get("table") or {}):
                    where[mid].append(z)
            for mid, m in sorted(mats.items()):
                if m["material_type"] not in GATHERED:
                    continue
                s = (m.get("skill_range") or [None])[0]
                _, need = gate(s, ladder) if s is not None else (None, None)
                w.writerow([mid, m["name"], m["material_type"], m["tier"], s,
                            need if need is not None else "unreachable",
                            ";".join(sorted(roles.get(mid, ()))),
                            ";".join(sorted(where.get(mid, ())))])
        print(f"\n  wrote {args.csv}")

    return 1 if rows else 0


if __name__ == "__main__":
    sys.exit(main())
