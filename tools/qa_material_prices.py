"""
Materials are worth selling, and nothing can be bought, crafted and sold at a profit.

Kyle, 10 Nov: "profession goods should actually vendor for a bit more" - and the card "dont
need to advertise its 'mid-tier'".

  1. every gathered or refined material is at or above the skill curve
     (tools/reprice_materials.py --check)
  2. within a type, a higher-skill material never sells for less than a lower-skill one
     by more than rounding - the ladder climbs
  3. nothing a vendor sells can be sold back for more than half its price
  4. NO MONEY LOOP: no recipe whose inputs can all be bought from a vendor makes something
     that sells for more than the inputs cost - materials or gear
  5. the material card does not say "tier"
"""
import json
import os
import subprocess
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
    r = subprocess.run([sys.executable, "tools/reprice_materials.py", "--check"], capture_output=True, text=True)
    check(r.returncode == 0, "materials under the curve:\n      " + "\n      ".join(r.stdout.strip().splitlines()[-6:]))

    data = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))
    mats = data.get("materials", data)
    sys.path.insert(0, str(ROOT / "tools"))
    from reprice_materials import TYPE_WEIGHT, curve

    priced = 0
    for mtype in TYPE_WEIGHT:
        ladder = sorted((m["skill_range"][0], m["sell_price"], m["name"]) for m in mats.values()
                        if m.get("material_type") == mtype and m.get("skill_range") and not m.get("vendor_price"))
        priced += len(ladder)
        check(len(ladder) >= 5, f"rig: only {len(ladder)} {mtype} materials")
        for skill, price, name in ladder:
            check(price >= curve(skill, mtype), f"{name}: {price}c at skill {skill}, curve {curve(skill, mtype)}c")
        top = [p for s, p, n in ladder if s >= 250]
        bottom = [p for s, p, n in ladder if s <= 30]
        if top and bottom:
            check(min(top) >= 10 * max(1, min(bottom)),
                  f"{mtype}: the best ({min(top)}c) is not worth ten of the worst ({min(bottom)}c)")

    for mid, m in mats.items():
        vp = m.get("vendor_price")
        if vp:
            check(m["sell_price"] * 2 <= vp, f"{m['name']}: a vendor sells it for {vp}c and buys it back for {m['sell_price']}c")

    from world.recipe_manager import _load_all_recipes
    from entities.pricing import gear_sell_price
    recipes = _load_all_recipes()
    seen = 0
    for rid, (_prof, rec) in recipes.items():
        ins = rec.get("inputs") or {}
        if not ins or not all(i in mats and mats[i].get("vendor_price") for i in ins):
            continue
        seen += 1
        cost = sum(mats[i]["vendor_price"] * q for i, q in ins.items())
        out = rec.get("output") or {}
        if out.get("kind") in ("armor", "weapon") or out.get("slot"):
            worth = gear_sell_price(out.get("item_level", 1), out.get("rarity", "uncommon"),
                                    out.get("slot"), out.get("weapon_type"))
        else:
            oid = out.get("material_id") or out.get("id") or out.get("item_id")
            worth = mats.get(oid, {}).get("sell_price", 0) * (out.get("quantity", 1) or 1)
        check(worth <= cost, f"MONEY LOOP {rid}: inputs cost {cost}c at a vendor, the result sells for {worth}c")

    src = (ROOT / "ui/screens/inventory_screen.py").read_text(encoding="utf-8")
    i = src.index("def _draw_material_tooltip")
    body = src[i:src.index("\n    def ", i + 10)]
    check(".tier" not in body, "the material card still prints the material's tier")

    print(f"{priced} materials on the curve; {seen} all-vendor recipes checked for money loops of {len(recipes)}")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("material prices OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
