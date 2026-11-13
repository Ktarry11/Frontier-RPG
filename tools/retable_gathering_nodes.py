"""Make every zone's herb, ore and wood nodes fit the zone's level (backlog I [58]).

    python3 tools/retable_gathering_nodes.py            # report
    python3 tools/retable_gathering_nodes.py --apply    # rewrite data/gathering/node_pools.json

A node needs skill S. A character in a zone of levels lo-hi can have at most hi*5 skill, and a
node is still worth picking about fifteen levels past the level its skill implies (WoW's
window). So a node FITS when   (lo - 15) * 5  <=  S  <=  hi * 5.
Measured 12 Nov: 99 entries too low (copper and ashwood in level 40 zones) and 22 too high.

An entry that does not fit is swapped for a material of the same kind that does - the unused
one nearest the middle of the window - keeping its weight. If every fitting material is already
in the table the weight is added to the nearest one. Nothing above skill 300 and nothing from
the post-60 tiers is ever chosen.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
KINDS = ("herb", "ore", "wood")
#: Rare by design - never used to fill a table.
NEVER_FILL = {"herb_black_lotus", "herb_purple_lotus", "ore_dark_iron", "ore_elementium", "ore_coal"}


def window(lo, hi):
    return max(0, (lo - 15) * 5), hi * 5


def load():
    from world.zone_keys import zone_key
    from entities.material_tiers import HIGH_TIER
    mats = json.load(open(ROOT / "data/gathering/materials.json"))["materials"]
    levels = {zone_key(k): v for k, v in json.load(open(ROOT / "data/zones/zone_levels.json"))["zones"].items()}
    skill = {k: v["skill_range"][0] for k, v in mats.items() if v.get("skill_range")}
    kind = {k: v.get("material_type") for k, v in mats.items()}
    return mats, levels, skill, kind, HIGH_TIER, zone_key


#: Tables designed by hand with Kyle (claude/tempest_isle_gathering_and_vendors.md) - left alone.
DESIGNED = {"tempest_shallows", "ashen_reach", "cinderwharf", "khaz_varun_the_black_hollow", "emberdeep"}


def quest_materials():
    """Materials a quest sends you to gather. A quest that says 'pull bruiseweed along the road
    cuts' needs bruiseweed to stay where it is, whatever its skill."""
    import glob
    out = set()
    for path in glob.glob(str(ROOT / "data/quests/*.json")):
        for q in json.load(open(path)).get("quests", []):
            for o in q.get("objectives", []):
                if o.get("type") == "gather":
                    out.add(o.get("target"))
    return out


def excused(zone, mat, zone_key, keep):
    return zone_key(zone) in DESIGNED or mat in NEVER_FILL or mat in keep


def unfit(pools, levels, skill, kind, zone_key):
    out = []
    for zone, pool in pools.items():
        lv = levels.get(zone_key(zone))
        if not lv:
            continue
        s_lo, s_hi = window(*lv)
        for mat in pool.get("table", {}):
            if excused(zone, mat, zone_key, KEEP):
                continue
            if kind.get(mat) in KINDS and mat in skill and not (s_lo <= skill[mat] <= s_hi):
                out.append((zone, mat, skill[mat], "low" if skill[mat] < s_lo else "high", lv))
    return out


KEEP = quest_materials()


def main():
    apply = "--apply" in sys.argv
    mats, levels, skill, kind, HIGH_TIER, zone_key = load()
    path = ROOT / "data/gathering/node_pools.json"
    data = json.load(open(path))
    pools = data["zones"]
    before = unfit(pools, levels, skill, kind, zone_key)
    for zone, pool in pools.items():
        lv = levels.get(zone_key(zone))
        if not lv:
            continue
        s_lo, s_hi = window(*lv)
        mid = (max(s_lo, (lv[0] - 6) * 5) + s_hi) / 2
        table = pool.get("table", {})
        for mat in list(table):
            k = kind.get(mat)
            if k not in KINDS or mat not in skill or s_lo <= skill[mat] <= s_hi:
                continue
            if excused(zone, mat, zone_key, KEEP):
                continue
            weight = table.pop(mat)
            fits = [m for m in skill if kind.get(m) == k and s_lo <= skill[m] <= min(s_hi, 300)
                    and m not in HIGH_TIER and m not in NEVER_FILL]
            fresh = [m for m in fits if m not in table]
            if fresh:
                new = min(fresh, key=lambda m: abs(skill[m] - mid))
            elif fits:
                new = min(fits, key=lambda m: abs(skill[m] - skill[mat]))
            else:
                table[mat] = weight            # nothing of this kind fits here at all
                print(f"  ?? {zone}: nothing to replace {mat} with")
                continue
            table[new] = table.get(new, 0) + weight
            if "--verbose" in sys.argv:
                print(f"  {zone} {lv}: {mat} ({skill[mat]}) -> {new} ({skill[new]})")
    after = unfit(pools, levels, skill, kind, zone_key)
    print(f"entries that do not fit their zone: {len(before)} before "
          f"({sum(1 for b in before if b[3] == 'low')} too low, {sum(1 for b in before if b[3] == 'high')} too high), "
          f"{len(after)} after")
    if apply:
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print("written")
    return 0


if __name__ == "__main__":
    sys.exit(main())
