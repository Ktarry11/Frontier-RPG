#!/usr/bin/env python3
"""Nine recruit attacks whose text promised a condition and which were plain attacks.

    python3 tools/qa_kit_abilities_batch9.py

Each is cast for real against a monster, with the dice pinned, and the damage compared with
the same cast when the condition does not hold.
"""
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

bad = []


def check(ok, text):
    if not ok:
        bad.append(text)


def main():
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party
    from world.recruit_manager import get_recruit_manager

    doc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict) else rm.recruits)}

    def fill(ch, ab):
        for res in ("rage", "energy", "mana", "focus", "power"):
            for attr in (f"max_{res}", f"current_{res}"):
                if isinstance(getattr(ch, attr, None), (int, float)):
                    setattr(ch, attr, 9999)
        try:
            rtype = ab._effective_resource_type(ch)
            ch.set_resource(rtype, max(ch.get_resource_max(rtype) or 0, 9999))
        except Exception:
            pass
        ab.turns_remaining = 0

    def setup(ability_name):
        for kid, kit in doc.items():
            if kid.startswith("_"):
                continue
            for a in kit["abilities"]:
                if a["name"] == ability_name:
                    ch = recs[kid].build_character()
                    ab = next(x for x in ch.ability_book.get_all_abilities() if x.ability_id == a["ability_id"])
                    return ch, ab
        raise KeyError(ability_name)

    def foe(ch, kind="beast_basic"):
        m = Monster("Test Boar", kind, ch.level)
        m.max_health = m.current_health = 10 ** 7
        m.dodge = m.parry = 0.0
        if hasattr(m, "block_chance"):
            m.block_chance = 0.0
        return m

    def hit(ch, ab, m, eng=None, seed=5):
        """Cast it with the dice pinned; return damage dealt."""
        fill(ch, ab)
        random.seed(seed)
        before = m.current_health
        ok, msg = ab.use(ch, m, party=[ch], engine=eng)
        if not ok:
            bad.append(f"{ab.name}: would not cast ({msg!r})")
        return before - m.current_health

    def fresh(ch):
        ch._fight_uses = {}
        ch._attack_streak = (None, 0)

    def ratio(a, b):
        return a / b if b else 0.0

    # Emre: hardest on a full-health enemy
    ch, ab = setup("The Thing Behind the Door")
    m = foe(ch); full = hit(ch, ab, m)
    m = foe(ch); m.current_health = m.max_health // 10; low = hit(ch, ab, m)
    check(1.30 <= ratio(full, low) <= 1.50, f"Thing Behind the Door: full {full} vs nearly dead {low} (x{ratio(full, low):.2f}, wanted about 1.43)")

    # Eino: double above 60%
    ch, ab = setup("Timber the Size of Towers")
    m = foe(ch); high = hit(ch, ab, m)
    m = foe(ch); m.current_health = m.max_health // 2; mid = hit(ch, ab, m)
    check(1.9 <= ratio(high, mid) <= 2.1, f"Timber: above 60% {high} vs half {mid} (x{ratio(high, mid):.2f}, wanted 2)")

    # Ratih: 40% more to a full-health target
    ch, ab = setup("A Route She Drew Herself")
    m = foe(ch); full = hit(ch, ab, m)
    m = foe(ch); m.current_health = int(m.max_health * 0.9); hurt = hit(ch, ab, m)
    check(1.33 <= ratio(full, hurt) <= 1.47, f"A Route She Drew: full {full} vs hurt {hurt} (x{ratio(full, hurt):.2f}, wanted 1.4)")

    # Matias: 30% more to what he has already hit
    ch, ab = setup("The Same Forty Faces")
    m = foe(ch); fresh(ch); first = hit(ch, ab, m); second = hit(ch, ab, m)
    check(1.24 <= ratio(second, first) <= 1.36, f"Same Forty Faces: first {first}, second {second} (x{ratio(second, first):.2f}, wanted 1.3)")

    # Eino: 12% per earlier use, to 60%
    ch, ab = setup("The Same Axe")
    m = foe(ch); fresh(ch)
    got = [hit(ch, ab, m) for _ in range(7)]
    rs = [round(ratio(g, got[0]), 2) for g in got]
    check(all(abs(r - w) <= 0.04 for r, w in zip(rs, [1.0, 1.12, 1.24, 1.36, 1.48, 1.6, 1.6])),
          f"Same Axe: went {rs}, wanted 1.0 1.12 1.24 1.36 1.48 1.6 1.6")
    eng = CombatEngine(ch, m, party=Party(ch), enemies=[m])
    check(ch._fight_uses == {}, "Same Axe: the count carried into a new fight")

    # Ivan: 25% per attack in a row on one target, to 100%; broken by changing target
    ch, ab = setup("Committed Middle")
    m, other = foe(ch), foe(ch); fresh(ch)
    got = [hit(ch, ab, m) for _ in range(6)]
    rs = [round(ratio(g, got[0]), 2) for g in got]
    check(all(abs(r - w) <= 0.05 for r, w in zip(rs, [1.0, 1.25, 1.5, 1.75, 2.0, 2.0])),
          f"Committed Middle: went {rs}, wanted 1.0 1.25 1.5 1.75 2.0 2.0")
    swap = hit(ch, ab, other)
    check(abs(ratio(swap, got[0]) - 1.0) <= 0.05, f"Committed Middle: a new target still got x{ratio(swap, got[0]):.2f}")

    # Adrian: 50% more to an enemy that attacked on its last turn
    ch, ab = setup("When You Were in the Wrong")
    m = foe(ch); fresh(ch)
    quiet = hit(ch, ab, m)
    m.abilities[0].turns_remaining = 0
    m.abilities[0].use(m, ch)
    m.tick_status_effects()
    loud = hit(ch, ab, m)
    check(1.42 <= ratio(loud, quiet) <= 1.58, f"When You Were in the Wrong: quiet {quiet}, after it attacked {loud} (x{ratio(loud, quiet):.2f}, wanted 1.5)")
    m.tick_status_effects()
    calm = hit(ch, ab, m)
    check(abs(ratio(calm, quiet) - 1.0) <= 0.05, "When You Were in the Wrong: still punishing an enemy that did not attack")

    # Emre and Haruto: cannot miss, be dodged or parried; Haruto always crits
    for name, crits in (("A Short Conversation", False), ("A Single Stroke", True)):
        ch, ab = setup(name)
        ch.hit_rating = -100
        m = foe(ch, "humanoid_warrior")
        m.dodge, m.parry = 60.0, 39.0
        landed = 0
        for seed in range(12):
            if hit(ch, ab, m, seed=seed) > 0:
                landed += 1
        check(landed == 12, f"{name}: landed {landed} of 12 against 99% avoidance")
        if crits:
            fill(ch, ab); ab.use(ch, m, party=[ch])
            check(getattr(ab, "_last_crit", False), f"{name}: did not crit")
        plain = ch.ability_book.abilities[ch.get_basic_attack_id()]
        missed = sum(1 for seed in range(12) if hit(ch, plain, m, seed=seed) <= 0)
        check(missed >= 8, f"{name}: harness - a plain attack only failed {missed} of 12 against the same enemy")

    print("9 abilities: health-scaled, felling strike, full-health shot, struck before, same axe, "
          "committed, punish, two sure hits")
    if bad:
        print("FAIL:")
        for b in bad:
            print("  " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
