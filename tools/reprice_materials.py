"""Raise what gathered and refined materials sell for, on one curve by skill.

Kyle, 10 Nov: "profession goods should actually vendor for a bit more" (Spidersilk Cloth sold
for 14c), and in the same breath: the card "dont need to advertise its 'mid-tier'".

A material's price was hand-set and nearly flat - Linen 4c, Soulcloth at skill 300 48c - so a
bag of the best cloth in the game was worth less than one grey drop. Now:

    copper = (5 + 0.0055 * skill**2) * type weight

    skill     1    75    150    225    300
    ore      5c   36c  1s 29c 2s 83c    5s
    bar     10c   72c  2s 58c 5s 67c   10s

Rules:
  - only RAISES a price; anything already dearer (Arcanite, Black Lotus) keeps its figure
  - a material a vendor SELLS (it has a vendor_price) is left alone - raising its sell price
    past a quarter of what the vendor charges would be a money printer
  - crafted intermediates with no skill of their own (scopes, pages, kits) are not priced
    here; they need pricing from their recipes, which belongs with the crafting audit

    python3 tools/reprice_materials.py            # rewrite data/gathering/materials.json
    python3 tools/reprice_materials.py --check    # exit 1 if anything is under the curve
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data/gathering/materials.json"

#: Refined goods are worth about two of what they are made from.
TYPE_WEIGHT = {
    "ore": 1.0, "bar": 2.0, "cloth": 0.9, "bolt": 2.0, "leather": 0.9, "herb": 1.0,
    "wood": 0.8, "plank": 1.6, "crystal": 1.5, "meat": 0.6,
}


def curve(skill, material_type):
    weight = TYPE_WEIGHT.get(material_type)
    if weight is None:
        return None
    return max(1, int(round((5 + 0.0055 * skill * skill) * weight)))


def target(mat):
    """The curve price for one material, or None if this tool does not price it."""
    rng = mat.get("skill_range")
    if not rng or mat.get("vendor_price"):
        return None
    return curve(rng[0], mat.get("material_type"))


def main():
    check = "--check" in sys.argv
    raw = PATH.read_text()
    data = json.loads(raw)
    mats = data.get("materials", data)
    low = []
    for mid, mat in mats.items():
        want = target(mat)
        if want is not None and mat.get("sell_price", 0) < want:
            low.append((mid, mat["sell_price"], want))
            if not check:
                mat["sell_price"] = want
    if check:
        for mid, have, want in low[:15]:
            print(f"  {mid}: sells for {have}c, the curve says {want}c")
        print(f"{len(low)} material(s) under the curve")
        return 1 if low else 0
    style = next(((i, asc) for i in (2, 4, 1, None) for asc in (True, False)
                  if json.dumps(json.loads(raw), indent=i, ensure_ascii=asc) == raw.rstrip("\n")), (2, True))
    PATH.write_text(json.dumps(data, indent=style[0], ensure_ascii=style[1]) + ("\n" if raw.endswith("\n") else ""))
    print(f"{len(low)} material(s) repriced")
    return 0


if __name__ == "__main__":
    sys.exit(main())
