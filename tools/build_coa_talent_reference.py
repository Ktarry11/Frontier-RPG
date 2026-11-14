#!/usr/bin/env python3
"""Turn the scraped CoA tooltips into a per-class talent reference.

    python3 tools/build_coa_talent_reference.py <scrape_dir> [--apply]

Input is whatever tools/scrape_coa_talents.js wrote: one file per spec page,
each holding every talent tooltip on that page as
{name, desc, cost, requires, rank}.

Two things have to be sorted out before the data is usable.

EACH SPEC PAGE CARRIES TWO TREES. CoA gives every class a shared class tree
plus one tree per spec, and a spec page renders both. The cost field says
which is which: "1 AE" is a class-tree point, "1 TE" a spec-tree point.
So the class tree repeats on all three or four of that class's pages and has
to be deduplicated, or the Guardian class tree would appear three times.

TIER IS ENCODED IN THE REQUIREMENT, not in a tier field. "Requires 9 AE in
this tree" is CoA's gate, and Frontier's trees gate the same way
(tier_requirements maps a tier to points spent in that tree). So the
requirement text converts directly into a Frontier tier: no requirement is
tier 0, and each distinct threshold above it is the next tier up. That is
the mapping the second authoring pass needs, and the reason this reference
is worth building rather than reading the raw scrape.

Output is reference/coa_sidekick/talents/<class>.json:

    {"class": "Guardian",
     "class_tree": [{name, desc, cost, requires, tier}, ...],
     "specs": {"vanguard": [...], "inspiration": [...], ...}}
"""
import argparse
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTDIR = ROOT / "reference/coa_sidekick/talents"

#: "Requires 9 AE in this tree", "Requires 16 points in this tree (level 40)"
REQ = re.compile(r"Requires\s+(\d+)\s+(?:AE|TE|points)", re.I)


def points_required(requires):
    match = REQ.search(requires or "")
    return int(match.group(1)) if match else 0


def tree_of(cost):
    """'1 AE' -> 'class', '1 TE' -> 'spec', 'Free' -> None (either)."""
    if "AE" in (cost or ""):
        return "class"
    if "TE" in (cost or ""):
        return "spec"
    return None


def assign_tiers(nodes):
    """Turn CoA point requirements into Frontier tier numbers.

    Distinct thresholds, sorted, become tiers 0..n. Frontier's own trees use
    {0:0, 1:5, 2:10, ...}, so a CoA tree with gates at 0/9/16 maps onto
    three tiers rather than being forced into seven.
    """
    thresholds = sorted({points_required(n.get("requires")) for n in nodes})
    tier_of = {t: i for i, t in enumerate(thresholds)}
    for node in nodes:
        node["tier"] = tier_of[points_required(node.get("requires"))]
    return nodes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scrape_dir")
    parser.add_argument("--apply", action="store_true", help="write the files")
    args = parser.parse_args()

    scrape = Path(args.scrape_dir)
    files = sorted(scrape.glob("*.json"))
    if not files:
        print(f"no scrape files in {scrape}")
        return 1

    by_class = OrderedDict()
    for path in files:
        doc = json.loads(path.read_text(encoding="utf-8"))
        spec_path = doc["path"]                      # e.g. /guardian/vanguard
        cls_slug, spec_slug = spec_path.strip("/").split("/", 1)
        entry = by_class.setdefault(cls_slug, {"class_tree": OrderedDict(),
                                               "specs": OrderedDict()})
        spec_nodes = []
        for tip in doc.get("tooltips", []):
            where = tree_of(tip.get("cost"))
            record = {k: tip.get(k, "") for k in ("name", "desc", "cost",
                                                  "requires", "rank")}
            if where == "class":
                # Repeats on every spec page of this class - keep one.
                entry["class_tree"].setdefault(tip["name"], record)
            else:
                spec_nodes.append(record)
        entry["specs"][spec_slug] = spec_nodes

    total_class, total_spec = 0, 0
    for cls_slug, entry in by_class.items():
        class_nodes = assign_tiers(list(entry["class_tree"].values()))
        specs = {s: assign_tiers(n) for s, n in entry["specs"].items()}
        total_class += len(class_nodes)
        total_spec += sum(len(n) for n in specs.values())
        tiers = max((n["tier"] for n in class_nodes), default=0)
        print(f"{cls_slug:18s} class tree {len(class_nodes):3d} nodes "
              f"({tiers + 1} tiers) | " +
              ", ".join(f"{s} {len(n)}" for s, n in specs.items()))
        if args.apply:
            OUTDIR.mkdir(parents=True, exist_ok=True)
            doc = {"class": cls_slug.replace("-", " ").title(),
                   "_source": "ascensionsidekick.com, scraped "
                              "2026-10-28 by tools/scrape_coa_talents.js. "
                              "AE = class-tree point, TE = spec-tree point; "
                              "tier is derived from the 'Requires N in this "
                              "tree' gate.",
                   "class_tree": class_nodes,
                   "specs": specs}
            (OUTDIR / f"{cls_slug}.json").write_text(
                json.dumps(doc, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"\n{len(by_class)} classes, {total_class} class-tree nodes, "
          f"{total_spec} spec-tree nodes")
    if not args.apply:
        print("(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
