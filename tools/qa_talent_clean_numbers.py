#!/usr/bin/env python3
"""Every talent number is a clean one, at every rank, and its text tells the truth.

    PYTHONPATH=. python3 tools/qa_talent_clean_numbers.py

Kyle, [29]: "Talent percentages must be clean numbers. ASKED BEFORE."

A talent is designed as a total and stored per rank, so a three-rank 35% was 11.67% a rank, and
an earlier rescale had left totals like 16.2% and 13.5%. tools/clean_talent_numbers.py makes
each rank worth a whole number (975 values) and rewrites the text - including 600-odd lines
that were still quoting the number from BEFORE that rescale ("by 25%" on a talent giving 13.5%).

FOUR CLAIMS:

  1. EVERY RANK IS A WHOLE NUMBER: a whole percent, or a whole point, and never less than one.
     So the total is whole too, and so is the "Per rank / At N of N" line the tooltip computes.
  2. NO DESCRIPTION QUOTES A DECIMAL PERCENTAGE.
  3. THE CLEANER HAS NOTHING LEFT TO DO. If a talent generator is re-run, this is the check
     that says "run tools/clean_talent_numbers.py again".
  4. DESCRIPTIONS THAT QUOTE NO REAL NUMBER ONLY GET FEWER. A line whose percentages match none
     of its talent's effects is lying or is describing something the effects do not hold. Two
     remain (a proc chance the effects table does not carry); a new one fails.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

import clean_talent_numbers as C  # noqa: E402

#: Descriptions whose percentages match none of their effects. Lower it as they are fixed.
UNTRUE_CEILING = 2


def main():
    bad, unclean, decimals, untrue, total = [], [], [], [], 0
    for path in sorted(glob.glob("data/talents/*.json")):
        tree = os.path.basename(path)[:-5]
        nodes = json.load(open(path, encoding="utf-8"))["nodes"]
        for node in (nodes if isinstance(nodes, list) else nodes.values()):
            total += 1
            ranks = int(node.get("max_points") or 1)
            text = node.get("description", "")
            effects = {k: v for k, v in (node.get("effects") or {}).items()
                       if isinstance(v, (int, float)) and not isinstance(v, bool) and v}
            for k, v in effects.items():
                if not C.is_clean(v, k):
                    unclean.append(f"{tree}: {node['name']} {k} = {v}")
            if re.search(r"\d\.\d+%", text):
                decimals.append(f"{tree}: {node['name']}: {text[:90]}")
            real = set()
            for k, v in effects.items():
                real.update(C.totals(v, ranks, k))
            quoted = {float(m) for m in re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)%", text)}
            if effects and quoted and not (quoted & real):
                untrue.append(f"{tree}: {node['name']}")
    if unclean:
        bad.append(f"{len(unclean)} talent value(s) are not a whole number per rank: {unclean[:6]}")
    if decimals:
        bad.append(f"{len(decimals)} description(s) quote a decimal percentage: {decimals[:4]}")
    # 3. nothing left for the cleaner
    left = sum(C.fix_file(p, write=False)[0] + C.fix_file(p, write=False)[2]
               for p in sorted(glob.glob("data/talents/*.json")))
    if left:
        bad.append(f"tools/clean_talent_numbers.py would still change {left} thing(s) - run it")
    if len(untrue) > UNTRUE_CEILING:
        bad.append(f"{len(untrue)} descriptions quote percentages that match none of their effects "
                   f"(ceiling {UNTRUE_CEILING}): {untrue[:8]}")
    # the checks can fail
    if C.is_clean(0.054) or C.is_clean(1.6667) or not C.is_clean(0.05) or C.clean(0.1167) != 0.12 \
            or C.clean(0.6, "ability_x_crit") != 1 or C.clean(-0.027) != -0.03:
        bad.append("negative control: the cleaner's own rules are not what this suite assumes")

    print(f"{total} talents; {len(untrue)} descriptions quote no real number (ceiling {UNTRUE_CEILING})")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\ntalent numbers OK - every rank is a whole number and no description quotes a decimal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
