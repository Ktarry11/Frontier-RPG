#!/usr/bin/env python3
"""QA the Crystalline Underdark content pass.

    PYTHONPATH=. python3 tools/qa_underdark_content.py

WHY THIS EXISTS. The Hillsbrad pass shipped a loot table that was a melee dump - 14 leather pieces to 4
cloth, strength 50 to intellect 18, one caster weapon in ninety-six - and nobody noticed until it was
read back by hand afterwards. The game has 30 playable classes (8 cloth, 8 leather, 7 mail, 7 plate) and
most of them are not warriors, so "it validates" is not the bar. These checks are the bar.

  1  every creature referenced by an encounter table exists
  2  every creature's ability_kit exists, and bosses at 20+ carry four abilities
  3  every boss/rare has a loot pool, and every pool has four items
  4  item_level == creature level + 3, exactly
  5  armour spread across cloth / leather / mail / plate
  6  all 18 weapon types appear, none hoarded
  7  casting vs physical stat budget, measured on the generated stats rather than guessed from the suffix
  8  the Deep Bloom's hand-placed pack members all exist as creatures
  9  slots and weapon types are legal values
"""
import collections
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

SLOTS = {"back", "chest", "feet", "hands", "head", "legs", "main_hand", "neck", "off_hand",
         "ranged", "ring", "shoulder", "trinket", "waist", "wrist"}
#: THE REAL TYPE LIST, read from the data rather than typed out. This was a
#: literal set of 18 and the game has 20: libram and idol were added on
#: 2026-10-31 (the same day the loot-balance pass authored the first items
#: for them), so a perfectly legal Libram of the Last Rite in Shardmaw's
#: pool read as an "illegal weapon type". A hardcoded list of the game's own
#: types is a list that goes stale the first time Kyle adds one.
WEAPONS = set(json.loads(
    (ROOT / "data/items/weapon_types.json").read_text(encoding="utf-8"))["weapon_types"])
CAST = {"intellect", "spirit", "spell_power", "healing_power", "mp5", "crit_chance_spell",
        "spell_penetration"}
PHYS = {"strength", "agility", "attack_power", "crit_chance_physical", "dodge_rating", "defense_rating",
        "block_rating", "armor"}

ZONES = ("The Frostward Descent", "The Crystalline Underdark")


def main():
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))["kits"]
    loot = json.loads((ROOT / "data/loot/underdark_boss_loot.json").read_text(encoding="utf-8"))
    pools = {k: v for k, v in loot.items() if not k.startswith("_")}
    fails = []

    # ---- 1/2: encounters reference real creatures, creatures reference real kits
    print("== creatures and kits")
    referenced = set()
    for z in ZONES:
        spec = enc.get(z, {})
        blocks = [spec.get("open_zone", {})] + list(spec.get("subzones", {}).values()) \
            + list(spec.get("caves", {}).values())
        for b in blocks:
            referenced |= set(b.get("creatures", {}))
    missing = sorted(n for n in referenced if n not in cre)
    print(f"  {len(referenced)} creatures referenced, {len(missing)} missing")
    if missing:
        fails.append(f"encounters reference missing creatures: {missing}")

    ours = {n: c for n, c in cre.items() if c.get("ability_kit") in kits or n in referenced}
    nokit = sorted(n for n in referenced if n in cre and cre[n].get("ability_kit") not in kits)
    print(f"  creatures with no kit: {len(nokit)}")
    if nokit:
        fails.append(f"no ability_kit: {nokit}")

    thin = []
    for n in sorted(referenced):
        c = cre.get(n)
        if not c or not c.get("is_boss"):
            continue
        lo = c["level_range"][0]
        k = kits.get(c.get("ability_kit"), [])
        if lo >= 20 and len(k) < 4:
            thin.append(f"{n} lvl{lo} has {len(k)}")
    print(f"  bosses 20+ with fewer than 4 abilities: {len(thin)}")
    if thin:
        fails.append(f"thin boss kits: {thin}")

    # ---- 3/4: pools exist, are four deep, and are levelled correctly
    print("\n== loot pools")
    bosses = sorted(n for n in referenced if cre.get(n, {}).get("is_boss"))
    nopool = [n for n in bosses if n not in pools]
    print(f"  {len(bosses)} bosses/rares, {len(nopool)} without a pool")
    if nopool:
        fails.append(f"no loot pool: {nopool}")
    for n, items in sorted(pools.items()):
        # THE ZONE'S OWN FOUR, not counting the cross-zone loot-balance
        # overlay. tools/build_loot_gap_items.py added 64 items for the five
        # starved weapon types across every boss and quest file in the game
        # (Kyle: "fix loot balance. Throw in an item throughout caves or
        # Dungeons or quest rewards"), and four of them landed in Underdark
        # pools. That is a deliberate addition, so counting it here reported
        # three pools as over budget and the tome count as hoarded for
        # something nobody did wrong. Gap items carry a "label"; they are
        # still held to the item level and schema rules below.
        own = [i for i in items if "label" not in i]
        if len(own) != 4:
            fails.append(f"{n} has {len(own)} items, want 4")
        want = cre.get(n, {}).get("level_range", [None])[0]
        if want is None:
            fails.append(f"loot pool for unknown creature: {n}")
            continue
        bad = [(i["name"], i["item_level"]) for i in items if i["item_level"] != want + 3]
        if bad:
            fails.append(f"{n}: item_level != level+3 ({want + 3}): {bad}")
    print(f"  pools {len(pools)}, items {sum(len(v) for v in pools.values())}, "
          f"level/ilvl mismatches {sum(1 for f in fails if 'item_level' in f)}")

    items = [i for v in pools.values() for i in v]

    # ---- 5: armour spread. 30 classes, 8/8/7/7 across the four types.
    print("\n== armour spread  (8 cloth / 8 leather / 7 mail / 7 plate classes need gear)")
    at = collections.Counter(i.get("armor_type") for i in items if i.get("armor_type"))
    for k in ("cloth", "leather", "mail", "plate"):
        print(f"  {k:8s} {at[k]:2d}")
    lo, hi = min(at[k] for k in ("cloth", "leather", "mail", "plate")), \
        max(at[k] for k in ("cloth", "leather", "mail", "plate"))
    ok = hi - lo <= 2
    print(f"  spread {lo}-{hi}  {'ok' if ok else 'FAIL - one armour class is being favoured'}")
    if not ok:
        fails.append(f"armour spread {lo}-{hi}, max gap 2")

    # ---- 6: weapon types
    print(f"\n== weapon types  ({len(WEAPONS)} exist; a zone that only drops swords and bows fails 30 classes)")
    wt = collections.Counter(i["weapon_type"] for i in items
                             if i.get("weapon_type") and "label" not in i)
    #: A CLASS RELIC IS NOT EXPECTED IN EVERY ZONE. "Every type appears" is a
    #: fair demand of the eighteen types many classes hold, and an unfair one
    #: of the three that serve one to three classes each: the whole game
    #: contains 3 idols, 6 librams and 9 totems against 134 one-handed maces.
    #: Asking the Crystalline Underdark specifically to stock an idol would
    #: mean a third of every idol in existence lives in one zone. They stay
    #: legal and still count against hoarding; they are just not required.
    RELICS = {"idol", "libram", "totem"}
    absent = sorted(WEAPONS - RELICS - set(wt))
    worst = wt.most_common(1)[0] if wt else ("-", 0)
    print(f"  {len(wt)}/{len(WEAPONS)} types present, {sum(wt.values())} weapons; most common {worst[0]} x{worst[1]}")
    if absent:
        print(f"  absent: {absent}")
        fails.append(f"weapon types absent: {absent}")
    if worst[1] > 2:
        fails.append(f"weapon type hoarded: {worst[0]} x{worst[1]}")

    # ---- 7: cast vs physical, measured on the actual generated stats
    print("\n== stat budget  (measured on generated stats, not inferred from suffix names)")
    tot = collections.Counter()
    for i in items:
        for d in (i.get("primary_stats", {}), i.get("secondary_stats", {})):
            for s, v in d.items():
                tot[s] += v
    c = sum(v for s, v in tot.items() if s in CAST)
    p = sum(v for s, v in tot.items() if s in PHYS)
    sta = tot.get("stamina", 0)
    share = c / (c + p) if (c + p) else 0
    print(f"  casting {c:7.1f} | physical {p:7.1f} | stamina {sta:7.1f} | casting share {share:.0%}")
    print(f"  top stats: {', '.join(f'{s} {v:.0f}' for s, v in tot.most_common(6))}")
    ok = 0.40 <= share <= 0.60
    print(f"  {'ok' if ok else 'FAIL - this table favours one half of the roster'}")
    if not ok:
        fails.append(f"casting share {share:.0%}, want 40-60%")

    # ---- 8: the Deep Bloom's hand-placed packs
    print("\n== the Deep Bloom's hand-placed packs")
    from tools import handbuilt_deep_bloom as DB
    DB.build_deep_bloom()
    names = sorted({n for (_x, _y, n, _l) in DB.TRASH})
    gone = [n for n in names if n not in cre]
    print(f"  {len(DB.TRASH)} mobs, {len(names)} distinct, {len(gone)} not in creatures.json")
    if gone:
        print(f"  FAIL {gone}  (world/cave_spawns.py raises on these at load)")
        fails.append(f"pack members missing from creatures.json: {gone}")
    for n in names:
        lo, hi = cre.get(n, {}).get("level_range", [0, 0])
        used = sorted({lv for (_x, _y, m, lv) in DB.TRASH if m == n})
        bad = [lv for lv in used if not lo <= lv <= hi]
        if bad:
            fails.append(f"{n} placed at {bad}, creature range is {lo}-{hi}")
    bosses_db = sorted(DB.BOSSES)
    gone_b = [n for n in bosses_db if n not in cre]
    print(f"  {len(bosses_db)} bosses, {len(gone_b)} not in creatures.json")
    if gone_b:
        fails.append(f"Deep Bloom bosses missing: {gone_b}")

    # ---- 9: legal slots and weapon types
    print("\n== schema")
    bad_slot = sorted({i["slot"] for i in items if i["slot"] not in SLOTS})
    bad_wt = sorted({i["weapon_type"] for i in items if i.get("weapon_type") not in WEAPONS
                     and i.get("weapon_type")})
    print(f"  illegal slots {bad_slot or 'none'} | illegal weapon types {bad_wt or 'none'}")
    if bad_slot:
        fails.append(f"illegal slots: {bad_slot}")
    if bad_wt:
        fails.append(f"illegal weapon types: {bad_wt}")

    print("\n" + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    for f in fails:
        print("  -", f)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
