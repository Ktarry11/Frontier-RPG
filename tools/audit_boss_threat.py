#!/usr/bin/env python3
"""Which bosses can actually do something to you?

    PYTHONPATH=. python3 tools/audit_boss_threat.py [--worst 30]

Kyle, 7 Nov:

    "i just auto attack every boss to death without gear on and survive."
    "most dungeon mobs just shit out loot as they either buff themselves for
     piddly shit then proceed to hit like a wet noodle."
    "I want enemies to have some threat when they hit you, but i dont want
     them to be massive HP sponges. we can improve difficulty by having
     unique skills / things to deal with too. We have such a varied magic
     system / skill system. Why not have more boss variety, it feels very
     boring. everything is tank and spank with forgetable skills."

THE HYPOTHESIS THIS TESTS, which is not the obvious one. "Bosses are too
easy" sounds like a damage or health number, and the fix for that sounds
like multiplying something. But Kyle's own screenshots point somewhere else:
Deepmuck casting Settle for +146 Armor, a Kobold Tunneler applying Bring
Down the Timber, Venom auto-attacking for 25. If a boss's whole kit is
self-buffs and small debuffs, then it IS a trash mob with a bigger health
bar, and auto-attacking it to death is not an exploit - it is the correct
play, because nothing in its kit asks the player to do anything else.

So this measures a kit's THREAT SHAPE rather than its numbers:

  pressure   does anything in the kit actually remove health fast enough to
             matter - a big hit, a stacking DOT, a heal on itself?
  demand     does anything require a RESPONSE - a stun to break, a debuff to
             dispel, a shield to burn, an add to kill, a heal to interrupt?
             This is the one Kyle is asking for and the one with no engine
             support problem: stuns, dispel types, absorbs and resistances
             all exist and are used by player abilities.
  variety    how many DISTINCT kits does a dungeon's boss roster use? Eight
             bosses sharing three kits is the "forgetable skills" complaint
             stated as a number.

A boss whose kit scores zero on demand is a tank-and-spank by construction,
regardless of how big its numbers are. That is the list worth having.
"""

import argparse
import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#: Kinds that take health off the party in a way the player feels.
PRESSURE_KINDS = {"damage", "dot", "lifesteal"}

#: Kinds that ask the player to DO something rather than keep attacking.
#: These are the mechanics the engine already supports on the player side.
DEMAND = {
    "stun": "a stun to play around",
    "dispel": "a debuff worth removing",
    "absorb": "a shield to burn through",
    "heal_self": "a heal that must be raced",
    "summon": "adds to handle",
    "aoe": "party-wide damage",
    "enrage": "a timer",
    "big_hit": "a hit the tank must survive",
}


def _load():
    with open(os.path.join(ROOT, "data/creatures/creatures.json"), encoding="utf-8") as fh:
        creatures = json.load(fh)["creatures"]
    with open(os.path.join(ROOT, "data/creatures/ability_kits.json"), encoding="utf-8") as fh:
        kits = json.load(fh)["kits"]
    return creatures, kits


def classify(kit, level_hint=30):
    """-> (pressure_score, {demand_tag}, notes)"""
    demands, notes = set(), []
    pressure = 0
    biggest = 0
    for ab in kit or []:
        kind = ab.get("kind", "")
        amount = float(ab.get("amount", 0) or 0)
        if kind in PRESSURE_KINDS:
            pressure += amount * (ab.get("duration", 1) or 1 if kind == "dot" else 1)
            biggest = max(biggest, amount)
        # A STUN USUALLY RIDES AN ATTACK rather than being its own ability,
        # which is the whole point of putting it there - a stun that costs
        # the boss its turn is a free turn for the party. Reading only the
        # top-level flag made this tool report 0 stuns across the roster
        # while live fights showed 19 of 60 bosses stunning the player. An
        # audit that disagrees with the game is wrong until proven otherwise.
        rider = ab.get("rider") or {}
        if ab.get("is_stun") or kind == "stun" or rider.get("is_stun"):
            demands.add("stun")
        if ab.get("dispel_type") or rider.get("dispel_type"):
            demands.add("dispel")
        if ab.get("absorb") or rider.get("absorb"):
            demands.add("absorb")
        if kind == "heal" and ab.get("self_only", True):
            demands.add("heal_self")
        if kind == "summon" or ab.get("summon"):
            demands.add("summon")
        if ab.get("is_aoe"):
            demands.add("aoe")
        if ab.get("hp_below"):
            demands.add("enrage")
            notes.append(f"{ab.get('name')} below {int(ab['hp_below']*100)}%")
    # A single hit worth a big slice of a player's health is its own demand -
    # it is the thing a tank exists for. SCALED BY LEVEL, because a flat 180
    # was written before the creature damage rescale and afterwards reported
    # 236 of 358 bosses as hitting hard, including level-5 ones: the number
    # it was measuring moved and the threshold did not, which is the bug
    # this repo keeps shipping. Player health runs roughly 100 + 30/level.
    if biggest >= (100 + 30 * max(1, level_hint)) * 0.18:
        demands.add("big_hit")
    return pressure, demands, notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worst", type=int, default=30)
    args = ap.parse_args()

    creatures, kits = _load()
    bosses = {n: c for n, c in creatures.items() if c.get("is_boss")}

    rows = []
    kit_use = collections.Counter()
    for name, c in bosses.items():
        key = c.get("ability_kit")
        kit = kits.get(key)
        kit_use[key] += 1
        lr = c.get("level_range") or [1, 1]
        lvl = int(((lr[0] or 1) + (lr[1] or 1)) / 2)
        pressure, demands, notes = classify(kit, lvl)
        rows.append((len(demands), pressure, name, key, demands,
                     len(kit or []), notes))

    rows.sort(key=lambda r: (r[0], r[1]))

    toothless = [r for r in rows if r[0] == 0]
    nokit = [r for r in rows if not r[3] or r[5] == 0]

    print(f"  {len(bosses)} bosses across {len(kit_use)} distinct kits")
    print(f"  {len(toothless)} have NO ability that demands a response "
          f"- tank-and-spank by construction")
    print(f"  {len(nokit)} have no kit at all\n")

    print(f"  {'boss':34}{'kit':22}{'abils':>6}{'demands'}")
    for n_dem, pressure, name, key, demands, nab, notes in rows[:args.worst]:
        tags = ", ".join(sorted(DEMAND[d] for d in demands)) or "-- nothing --"
        print(f"  {name[:33]:34}{str(key)[:21]:22}{nab:>6}  {tags}")

    print("\n  -- kit reuse: the 'forgetable skills' number ----------------")
    for key, n in kit_use.most_common(12):
        kit = kits.get(key) or []
        names = ", ".join(a.get("name", "?") for a in kit[:4])
        print(f"  {n:>4} bosses share {str(key)[:20]:22}{names[:48]}")

    print("\n  -- what the roster is missing ------------------------------")
    have = collections.Counter()
    for _d, _p, _n, _k, demands, _na, _no in rows:
        for d in demands:
            have[d] += 1
    for tag, label in DEMAND.items():
        print(f"  {have.get(tag, 0):>4} of {len(rows)} bosses present {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
