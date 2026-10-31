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
        # epic_drops.json is keyed by BUCKET ("dungeon", "world"), not by boss
        # name. Reading it as a boss table reported two phantom broken entries.
        if p.name == "epic_drops.json":
            continue
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

    Dungeons, caves AND subzones. Subzones are included not because a rare out
    there is a boss - Kyle: "Hand placed mobs are only in full dungeons!", and
    rares are deliberately not bosses - but because a creature listed in one IS
    REACHABLE, and the only question this section answers is reachability. A
    first version excluded them and then reported 163 bosses as spawning
    nowhere, which was its own blind spot rather than 163 bugs.
    """
    where = collections.defaultdict(list)
    for zname, z in enc.items():
        for bucket in ("dungeons", "caves", "subzones"):
            for sub, sdata in (z.get(bucket) or {}).items():
                for cname in (sdata.get("creatures") or {}):
                    where[cname].append(f"{zname}/{sub}")
        if (z.get("location_type") or "").lower() in ("dungeon", "cave"):
            for cname in ((z.get("open_zone") or {}).get("creatures") or {}):
                where[cname].append(f"{zname}/open")
    return where



def _simulate(creatures, is_boss, sample=None):
    """Kill every flagged boss and return [(name, why)] for any that dropped nothing."""
    import random
    from world.creature_manager import CreatureManager
    from entities.character import Character
    from combat.combat_engine import CombatEngine
    from entities.boss_loot import shares_hoard

    random.seed(20261031)
    cm = CreatureManager()
    # A boss who SHARES A HOARD drops nothing on purpose - the Return Voyage
    # finale is one fight with two bosses in it, and the pair's loot is on the
    # other one. Dropping nothing is correct for him and only for him.
    names = [n for n in sorted(creatures) if is_boss(n) and not shares_hoard(n)]
    if sample:
        names = names[:sample]

    bad = []
    for name in names:
        try:
            m = cm.spawn_creature(name)
        except Exception as exc:
            bad.append((name, f"spawn_creature raised {type(exc).__name__}: {exc}"))
            continue
        if m is None:
            bad.append((name, "spawn_creature returned None"))
            continue
        if not getattr(m, "is_boss", False):
            bad.append((name, "spawned WITHOUT is_boss - takes the 35% trash roll"))
            continue
        # A FRESH PLAYER PER BOSS. Reusing one filled his bags after ~20 kills,
        # after which every drop hit combat_engine's "bags are full" branch and
        # never reached loot_gained - and the run reported 312 broken bosses.
        # That was the harness, not the game. Worth leaving written down: this
        # check was wrong in the alarming direction, which is the direction that
        # wastes a day chasing a bug that is not there.
        player = Character("Boss Loot QA", "shaman", level=60)
        ce = CombatEngine(player, m)
        for e in ce.enemies:
            e.current_health = 0
        try:
            ce._resolve_victory()
        except Exception as exc:
            bad.append((name, f"_resolve_victory raised {type(exc).__name__}: {exc}"))
            continue
        gear = [l for l in (getattr(ce, "loot_gained", None) or [])
                if getattr(l, "slot", None)]       # an item, not cloth/meat
        if not gear:
            bad.append((name, "victory produced no equipment drop"))
    return bad


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

    # Deliberately NOT reported: the ~680 creatures that spawn in an instance
    # with neither flag nor table. They are the trash, by design, and listing
    # them buried the two checks above under 680 rows of noise. A check nobody
    # reads is worse than no check. If a boss is ever hiding in there, the
    # curated-table check above is what catches it the moment it gets loot.

    if unspawnable:
        print(f"  REVIEW - {len(unspawnable)} flagged boss(es) appear in no dungeon or cave table:")
        for n in unspawnable[:25]:
            print(f"    {n:34s} table={loot.get(n, '-')}")
        if len(unspawnable) > 25:
            print(f"    ... and {len(unspawnable)-25} more")
        print()

    print(f"  OK - {len(procedural)} flagged boss(es) use the procedural boss roll "
          f"(guaranteed drop, rare floor) by design")

    # ------------------------------------------------------------------
    # BEHAVIOURAL PASS: actually kill every boss and look in the bag.
    #
    # Everything above reads data. Data agreeing with itself is not the same as
    # a boss dropping loot, and Kyle's report was behavioural - "none of the
    # bosses in grom's rest are dropping loot" - so the audit has to be too.
    # This spawns each flagged boss through CreatureManager exactly as the game
    # does, runs CombatEngine._resolve_victory on a corpse, and requires a drop.
    #
    # A boss is GUARANTEED a drop: curated table first, else the procedural boss
    # roll with a rare floor. So "no items" here is always a bug, never variance.
    # ------------------------------------------------------------------
    dropped = _simulate(creatures, is_boss)
    if dropped:
        fail = True
        print(f"\n  BROKEN - {len(dropped)} boss(es) killed and dropped NOTHING:")
        for n, why in dropped[:30]:
            print(f"    {n:34s} {why}")
        if len(dropped) > 30:
            print(f"    ... and {len(dropped)-30} more")

    print("\nFAIL" if fail else "\nPASS")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main())
