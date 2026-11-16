#!/usr/bin/env python3
"""Do the bosses actually DO anything? Every boss in the game, fought turn by turn.

    PYTHONPATH=. python3 tools/audit_boss_turns.py [--worst 40] [--only "Name,Name"] [--csv PATH]

Kyle, 16 Nov 2026: "make sure bosses are not just debuffing. they should have something dangerous", then "I'm not
sure if we should audit bosses throughout to ensure that bosses are actually doing stuff rather than just buffing /
debuffing and being punching bags".

WHY A NEW AUDIT. tools/audit_boss_threat.py reads each kit on paper and found every boss "demands" something: it
counts a big hit that EXISTS. But what a boss does is decided by Monster.choose_action, and a boss never spends a
turn on a plain buff or debuff while it has an attack ready, so a kit can carry a fearsome-sounding debuff the AI
never once casts. This one fights each boss with tools/audit_monster_combat.run_one (a real CombatEngine, a party
that cannot die, half the turns healthy and half under every phase gate) and counts what it actually did.

TWO QUESTIONS PER BOSS.
  PASSIVE    what share of the turns it acted on hurt nobody: self-buffs, debuffs, shields, heals. Summons count as
             pressure, because the adds then take turns of their own. Flagged over PASSIVE_LIMIT.
  TOOTHLESS  did it ever actually THROW something dangerous, measured against its own basic attack:
               big hit        a single-target hit of at least 1.6x its basic
               party blast    an area hit of at least 0.9x its basic on each target before the area split
               stun-and-smash a stun riding a hit of at least 1.0x its basic
               killing DoT    a damage-over-time worth at least 1.5x its basic over its duration
               desperation    a hit or blast gated on its own low health
               adds           a summon that landed
             A boss that used none of these is a punching bag with a health bar, whatever its kit is called.
DEAD SLOTS (for information): plain buffs and debuffs the boss carries and never used.

Report-only for the whole game (exit 0). With --only, exits 1 if any named boss is passive or toothless, which is
how a dungeon's own QA holds its bosses to it (tools/qa_scarlet_monastery.py).
"""
import argparse
import collections
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))

PASSIVE_LIMIT = 0.30
TURNS = 40
PASSIVE_KINDS = {"buff", "debuff", "heal"}


def dangers(m, success):
    """-> sorted list of the dangerous things this boss actually did."""
    abil = m.abilities
    basic = max(1, abil[0].amount or max((a.amount for a in abil if a.kind == "damage"), default=1))
    found = set()
    for i, a in enumerate(abil):
        if not success[i]:
            continue
        rider = a.rider or {}
        stun = bool(rider.get("is_stun")) or a.is_stun
        if a.kind == "summon":
            found.add("adds")
        if a.kind == "damage":
            if a.hp_below is not None and a.amount >= 1.2 * basic:
                found.add("desperation")
            if a.is_aoe and a.amount >= 0.9 * basic:
                found.add("party blast")
            if not a.is_aoe and a.amount >= 1.6 * basic:
                found.add("big hit")
            if stun and a.amount >= 1.0 * basic:
                found.add("stun-and-smash")
        if a.kind == "dot" and a.amount * max(1, a.duration) >= 1.5 * basic:
            found.add("killing DoT")
    return sorted(found)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worst", type=int, default=40)
    ap.add_argument("--only", default=None)
    ap.add_argument("--csv", default=None)
    a = ap.parse_args()
    import audit_monster_combat as AMC

    cm = AMC._manager()
    if a.only:
        names = [n.strip() for n in a.only.split(",") if n.strip()]
    else:
        names = sorted(n for n, d in cm.creatures.items() if d.get("is_boss"))
    rows, skipped = assess(names, cm)
    return _report(rows, skipped, a)


def assess(names, cm=None):
    """Fight each named boss for TURNS turns. -> (rows, skipped). Each row: name, level, kind, passive (share of
    acted turns spent on buff/debuff/heal), acted, dangers (what dangerous things it did), dead (buff/debuff slots
    it never got to use). Shared by tools/fix_dungeon_boss_turns.py and tools/qa_dungeon_boss_turns.py."""
    import audit_monster_combat as AMC
    from world.difficulty import kind_of
    cm = cm or AMC._manager()
    rows, skipped = [], []
    for name in names:
        d = cm.creatures.get(name)
        if d is None:
            skipped.append((name, "no such creature"))
            continue
        level = (d.get("level_range") or [1, 1])[-1]
        try:
            r = AMC.run_one(name, level, TURNS)
        except Exception as e:          # a kit the engine can't build is its own finding
            skipped.append((name, f"{type(e).__name__}: {e}"))
            continue
        if "skip" in r:
            skipped.append((name, r["skip"]))
            continue
        m = r["monster"]
        succ = r["success"]
        acted = max(1, r["acted"])
        passive = sum(succ[i] for i, ab in enumerate(m.abilities) if ab.kind in PASSIVE_KINDS)
        dead = [ab.name for i, ab in enumerate(m.abilities)
                if ab.kind in ("buff", "debuff") and not succ[i] and not ab.hp_below]
        found = dangers(m, succ)
        rows.append(dict(name=name, level=level, kind=kind_of(m), passive=passive / acted, acted=r["acted"],
                         dangers=found, dead=dead))
    return rows, skipped


def _report(rows, skipped, a):

    passive = [r for r in rows if r["passive"] > PASSIVE_LIMIT]
    toothless = [r for r in rows if not r["dangers"]]
    dead = [r for r in rows if r["dead"]]
    by_kind = collections.Counter(r["kind"] for r in rows)
    print(f"{len(rows)} bosses fought, {TURNS} turns each ({len(skipped)} could not be fought)")
    print(f"  by kind: {dict(by_kind)}")
    print(f"  PASSIVE (over {PASSIVE_LIMIT:.0%} of turns hurt nobody): {len(passive)}")
    print(f"  TOOTHLESS (never threw anything dangerous): {len(toothless)}")
    print(f"  carrying dead buff/debuff slots: {len(dead)}")
    for kind in sorted(by_kind):
        k_rows = [r for r in rows if r["kind"] == kind]
        print(f"    {kind:14} {len(k_rows):>4} bosses: {sum(1 for r in k_rows if r in passive):>4} passive, "
              f"{sum(1 for r in k_rows if r in toothless):>4} toothless")
    tally = collections.Counter(x for r in rows for x in r["dangers"])
    print("  what the dangerous ones throw: " + ", ".join(f"{k} {v}" for k, v in tally.most_common()))

    worst = sorted(passive + [r for r in toothless if r not in passive],
                   key=lambda r: (bool(r["dangers"]), -r["passive"]))[:a.worst]
    if worst:
        print(f"\n  {'boss':36}{'lvl':>4}  {'kind':12}{'passive':>8}  dangerous moves used")
        for r in worst:
            print(f"  {r['name'][:35]:36}{r['level']:>4}  {r['kind']:12}{r['passive']:>7.0%}  "
                  f"{', '.join(r['dangers']) or 'NONE'}")
    if skipped:
        print(f"\n  could not be fought: {len(skipped)}")
        for n, why in skipped[:10]:
            print(f"    {n}: {why}")
    if a.csv:
        import csv
        with open(a.csv, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["boss", "level", "kind", "passive_share", "dangers", "dead_slots"])
            for r in rows:
                w.writerow([r["name"], r["level"], r["kind"], f"{r['passive']:.2f}", "; ".join(r["dangers"]),
                            "; ".join(r["dead"])])
    if a.only:
        bad = passive + [r for r in toothless if r not in passive]
        if bad or skipped:
            print("FAIL")
            return 1
        print("PASS - every boss named acts and has something dangerous")
    return 0


if __name__ == "__main__":
    sys.exit(main())
