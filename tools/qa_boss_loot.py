#!/usr/bin/env python3
"""Audit boss loot wiring across EVERY dungeon and cave.

Kyle, 2026-10-31: "none of the bosses in grom's rest are dropping loot. We likely
need a full audit of every single dungeon and cave. this can't be isolated."

He is right that it cannot be isolated, and the reason is the shape this codebase
keeps producing: ONE RULE, TWO IMPLEMENTATIONS. A boss is "a boss" in three
separate places that nothing forces to agree -

  1. data/creatures/creatures.json      "is_boss": true   -> the stat multiplier
                                                             AND the loot branch
  2. data/loot/<zone>_boss_loot.json    a key per boss     -> the curated drops
  3. data/creatures/encounters.json     in a dungeon or
                                        cave creature table -> whether it spawns

combat_engine's loot branch keys on enemy.is_boss and NOTHING ELSE. A creature
with a hand-authored loot table but no is_boss flag silently takes the TRASH
roll: a 35% chance of an unfloored-rarity item. From the player's seat that reads
as "the boss dropped nothing", which is exactly what Kyle saw, and the curated
table sits there unreachable with no error anywhere.

So this checks all three against each other, in both directions, and FAILS on
the combination that is silently broken.
"""
import sys, os, json, pathlib, collections
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent
D = ROOT / "data"


def load():
    creatures = json.load(open(D / "creatures" / "creatures.json")).get("creatures", {})
    enc = json.load(open(D / "creatures" / "encounters.json")).get("zones", {})
    loot = {}
    for p in sorted((D / "loot").glob("*.json")):
        try:
            data = json.load(open(p))
        except (json.JSONDecodeError, OSError):
            continue
        if not isinstance(data, dict):
            continue
        for k, v in data.items():
            if k.startswith("_") or not isinstance(v, list):
                continue
            loot[k] = p.name
    return creatures, enc, loot


def instanced_tables(enc):
    """Every creature that spawns in a DUNGEON or CAVE, with where it spawns.

    Dungeons and caves are the instanced content - the places with bosses. The
    open-world "open_zone" table and the overworld "subzones" are excluded: a
    named rare out in a subzone is deliberately NOT a boss (Kyle: "Hand placed
    mobs are only in full dungeons!"), so pulling them in here would bury the
    real failures under a hundred by-design ones.
    """
    where = collections.defaultdict(list)
    for zname, z in enc.items():
        for bucket in ("dungeons", "caves"):
            for sub, sdata in (z.get(bucket) or {}).items():
                for cname in (sdata.get("creatures") or {}):
                    where[cname].append(f"{zname}/{sub}")
        # a dungeon zone may put its bosses straight in open_zone when the whole
        # zone IS the instance (Grom's Rest, Ragefire) - count those too
        if (z.get("location_type") or "").lower() in ("dungeon", "cave"):
            for cname in ((z.get("open_zone") or {}).get("creatures") or {}):
                where[cname].append(f"{zname}/open")
    return where


def main():
    creatures, enc, loot = load()
    where = instanced_tables(enc)

    def is_boss(n):
        return bool(creatures.get(n, {}).get("is_boss", False))

    # THE SILENT BUG: curated loot table, but no is_boss flag -> trash roll.
    unflagged = sorted(n for n in loot if n in creatures and not is_boss(n))
    # Loot authored for a creature that does not exist at all.
    orphan_loot = sorted(n for n in loot if n not in creatures)
    # Boss that spawns in an instance but has neither flag nor table.
    unflagged_spawned = sorted(
        n for n in where if n in creatures and not is_boss(n) and n not in loot)
    # Flagged boss with no curated table: falls through to the procedural boss
    # roll. That is BY DESIGN and guaranteed to drop, so it is reported as
    # information, never as a failure.
    procedural = sorted(n for n in creatures if is_boss(n) and n not in loot)
    # Flagged boss that nothing spawns anywhere.
    unspawnable = sorted(n for n in creatures if is_boss(n) and n not in where)

    print(f"  {len(creatures)} creature defs, {len(loot)} curated loot tables, "
          f"{len(where)} creatures spawning in dungeons/caves")
    print(f"  {sum(1 for n in creatures if is_boss(n))} flagged is_boss\n")

    fail = False

    if unflagged:
        fail = True
        print(f"  BROKEN - {len(unflagged)} creature(s) have a hand-authored loot table")
        print(f"  but NOT is_boss, so combat_engine gives them the 35% TRASH roll and the")
        print(f"  curated table is unreachable:")
        for n in unflagged:
            print(f"    {n:34s} table={loot[n]:34s} spawns={', '.join(where.get(n)) or 'NOWHERE'}")
        print()

    if orphan_loot:
        fail = True
        print(f"  BROKEN - {len(orphan_loot)} loot table(s) name a creature that does not exist")
        print(f"  in creatures.json, so the table can never be reached:")
        for n in orphan_loot:
            print(f"    {n:34s} table={loot[n]}")
        print()

    if unflagged_spawned:
        print(f"  REVIEW - {len(unflagged_spawned)} creature(s) spawn in a dungeon or cave with")
        print(f"  neither is_boss nor a loot table. Most are intended trash; a boss hiding")
        print(f"  in here is dropping trash loot:")
        for n in unflagged_spawned[:40]:
            print(f"    {n:34s} spawns={', '.join(where[n])}")
        if len(unflagged_spawned) > 40:
            print(f"    ... and {len(unflagged_spawned)-40} more")
        print()

    if unspawnable:
        print(f"  REVIEW - {len(unspawnable)} flagged boss(es) appear in no dungeon or cave table:")
        for n in unspawnable[:25]:
            print(f"    {n:34s} table={loot.get(n, '-')}")
        if len(unspawnable) > 25:
            print(f"    ... and {len(unspawnable)-25} more")
        print()

    print(f"  OK - {len(procedural)} flagged boss(es) use the procedural boss roll "
          f"(guaranteed drop, rare floor) by design")

    print("\nFAIL" if fail else "\nPASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
