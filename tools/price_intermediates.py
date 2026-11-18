#!/usr/bin/env python3
"""Price crafted intermediates (upgrade kits, parts, pages, sticks, fibre) from their recipes.

    PYTHONPATH=. python3 tools/price_intermediates.py            # rewrite data/gathering/materials.json
    PYTHONPATH=. python3 tools/price_intermediates.py --check    # exit 1 if any is under its recipe

tools/reprice_materials.py put gathered and refined materials on one curve by skill and left these out on purpose:
they have no skill of their own, so the curve can't price them, and "they need pricing from their recipes". Left
alone they sold for next to nothing (a Copper Tube made from copper bars for 2c, an Iron Upgrade Kit of iron bars
for 30c), less than the bars that went in. Now an intermediate sells for at least what its inputs sell for, per
one made, times WORK (1.10, the auction house's figure for intermediates, docs/auction_house_design.md section 3):

    sell = sum(input sell x qty) / made x 1.10

Rules, the same as reprice_materials.py:
  - only RAISES a price; one already dearer keeps it
  - a material a vendor SELLS (it has a vendor_price) is left alone
  - an intermediate whose inputs are all bought from a vendor is held under a quarter of what those inputs cost
    to buy, so making one and selling it is never a money printer (tools/qa_material_prices.py checks it)
Inputs are priced in order, so a kit made of parts sees the parts' new price.
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data/gathering/materials.json"
TYPES = {"upgrade_kit", "kit", "part", "pages", "stick", "fiber"}
WORK = 1.10


def recipes():
    """(inputs, output material_id, made) for every recipe that makes a material, in every profession."""
    out = []

    def walk(o):
        if isinstance(o, dict):
            outp = o.get("output")
            if isinstance(o.get("inputs"), dict) and isinstance(outp, dict) and outp.get("material_id"):
                out.append((o["inputs"], outp["material_id"], max(1, int(outp.get("count", 1) or 1))))
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for f in sorted(glob.glob(str(ROOT / "data/*/recipes*.json"))):
        walk(json.loads(Path(f).read_text(encoding="utf-8")))
    return out


def plan(mats):
    """{material_id: (old, new)} for every intermediate under its recipe."""
    by_out = {}
    for inputs, mid, made in recipes():
        m = mats.get(mid)
        if m and m.get("material_type") in TYPES and not m.get("vendor_price") and not m.get("skill_range"):
            by_out.setdefault(mid, []).append((inputs, made))
    price = {k: int(v.get("sell_price") or 0) for k, v in mats.items()}
    changes = {}
    for _ in range(4):                      # parts into kits: a few passes settle the chain
        for mid, ways in by_out.items():
            costs = []
            for inputs, made in ways:
                if any(i not in mats for i in inputs):
                    continue
                cost = sum(price[i] * q for i, q in inputs.items()) / made * WORK
                if all(mats[i].get("vendor_price") for i in inputs):
                    buy = sum(mats[i]["vendor_price"] * q for i, q in inputs.items()) / made
                    cost = min(cost, buy / 4)
                costs.append(cost)
            if not costs:
                continue
            want = max(1, int(round(min(costs))))      # the cheapest way to make it sets its worth
            if want > price[mid]:
                old = changes.get(mid, (price[mid],))[0]
                price[mid] = want
                changes[mid] = (old, want)
    return changes


def main():
    check = "--check" in sys.argv
    data = json.loads(PATH.read_text(encoding="utf-8"))
    mats = data.get("materials", data)
    changes = plan(mats)
    for mid, (old, new) in sorted(changes.items(), key=lambda kv: mats[kv[0]].get("material_type")):
        print(f"  {mid:32} {old:>6}c -> {new}c")
    if check:
        print(f"{len(changes)} intermediates under their recipe" if changes else "intermediates priced OK.")
        return 1 if changes else 0
    for mid, (_old, new) in changes.items():
        mats[mid]["sell_price"] = new
    text = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    PATH.write_text(text, encoding="utf-8")
    print(f"repriced {len(changes)} intermediates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
