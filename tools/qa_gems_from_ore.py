"""
Ore veins give up gemstones, the way they do in WoW.

Kyle, 12 Nov: "we get crystals from ore! ... Start adding gemstones and crystals to ore
(think of wow!)" - for jewelcrafting later.

  1. there are 50 gems, every one a real material with a name, a description, a price and an
     icon id, and every one comes from an ore that exists
  2. all 40 ores have at least one gem
  3. rolled 20,000 times per ore, each gem turns up at its stated rate, and only from its ore
  4. herbs, wood and cloth never give a gem
  5. a better vein gives a more valuable gem: price rises with the ore's skill
  6. a gem is worth more than the ore it came out of
  7. mining a vein for real puts the gem in the bag
  8. the crafting crystals still drop as before
"""
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
    from world.gathering_manager import get_gathering_node_manager
    gm = get_gathering_node_manager()
    mats = gm.materials
    gems = {k: v for k, v in mats.items() if v.get("material_type") == "gem"}
    ores = {k: v for k, v in mats.items() if v.get("material_type") == "ore"}
    table = gm.gem_table()

    check(len(gems) == 50, f"{len(gems)} gems, wanted 50")
    names = [g["name"] for g in gems.values()]
    check(len(set(names)) == len(names), "two gems share a name")
    listed = {g for rows in table.values() for g, _c in rows}
    check(listed == set(gems), f"gems with no source ore: {sorted(set(gems) - listed)}; unknown gems in the table: {sorted(listed - set(gems))}")
    for gid, g in gems.items():
        check(g.get("name") and len(g.get("description", "")) > 20 and g.get("sell_price", 0) > 0 and g.get("icon_id"),
              f"{gid} is missing a name, description, price or icon id")
    for ore in table:
        check(ore in ores, f"gem table names {ore}, which is not an ore")
    check(not (set(ores) - set(table)), f"ores with no gem: {sorted(set(ores) - set(table))}")

    rng = random.Random(3)
    N = 20000
    for ore, rows in table.items():
        got = {}
        for _ in range(N):
            g = gm.roll_vein_gem(ore, rng=rng)
            if g:
                got[g] = got.get(g, 0) + 1
        check(set(got) <= {g for g, _c in rows}, f"{ore} gave {set(got) - {g for g, _c in rows}}")
        skip = 1.0
        for gid, chance in rows:
            want = chance * skip                      # a later gem only rolls if the earlier ones missed
            rate = got.get(gid, 0) / N
            check(abs(rate - want) <= max(0.006, want * 0.3), f"{mats[gid]['name']} from {ores[ore]['name']}: {rate:.2%}, stated {want:.2%}")
            skip *= (1 - chance)
        total = sum(got.values()) / N
        check(0.01 <= total <= 0.12, f"{ores[ore]['name']}: a gem on {total:.1%} of swings")
    for other in [k for k, v in mats.items() if v.get("material_type") in ("herb", "wood", "cloth", "bar")][:40]:
        check(gm.roll_vein_gem(other, rng=random.Random(1)) is None or False, f"{other} gave a gem")
        for _ in range(200):
            if gm.roll_vein_gem(other, rng=rng):
                check(False, f"{other} is not ore and gave a gem")
                break

    by_skill = sorted((ores[o]["skill_range"][0], max(mats[g]["sell_price"] for g, _c in rows), o) for o, rows in table.items())
    check(by_skill[-1][1] >= 20 * by_skill[0][1], f"the best ore's gem ({by_skill[-1][1]}c) is not worth 20 of the worst's ({by_skill[0][1]}c)")
    for ore, rows in table.items():
        for gid, _c in rows:
            check(mats[gid]["sell_price"] > ores[ore]["sell_price"], f"{mats[gid]['name']} ({mats[gid]['sell_price']}c) is worth no more than {ores[ore]['name']} ({ores[ore]['sell_price']}c)")

    # 7. a real gem lands in a real bag
    from entities.character import Character
    c = Character("Hero", "Warrior", 20)
    gem = gm.make_material_instance("gem_malachite")
    check(gem is not None and c.add_material(gem), "a Malachite could not be put in the bag")
    check(any(getattr(m, "material_id", None) == "gem_malachite" for m in getattr(c, "materials", []) or []),
          "the Malachite is not in the bag afterwards")
    src = (ROOT / "ui/screens/overworld_screen.py").read_text()
    check("roll_vein_gem(material_id)" in src, "gathering a vein does not roll for a gem")

    # 8. crystals untouched
    hits = sum(1 for _ in range(4000) if gm.roll_vein_crystal("ore_copper", rng=rng))
    check(0.14 <= hits / 4000 <= 0.22, f"copper veins give a crafting crystal {hits / 4000:.1%} of the time (was 18%)")

    print(f"{len(gems)} gems from {len(table)} ores; cheapest {min(g['sell_price'] for g in gems.values())}c, dearest {max(g['sell_price'] for g in gems.values())}c")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("gems from ore OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
