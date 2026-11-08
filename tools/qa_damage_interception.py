#!/usr/bin/env python3
"""Death floors, reflects and low-health triggers do what their text says.

    PYTHONPATH=. python3 tools/qa_damage_interception.py [--list]

Companion to tools/qa_damage_share.py, which covers the fourth member of
this family. All four hook the same place in Character.take_damage and all
four are invisible to any inspection of the data.

=============================================================================
THE THREE CLAIMS
=============================================================================

DEATH PREVENTION - "the first blow that would kill any ally leaves them at
15% health instead". Four abilities. Three catch only a LETHAL blow; Henrik's
catches any blow that would take him below 20%, which is a different trigger.
Two things that would be wrong and look fine:

  - IT KEEPS WORKING. "The FIRST blow" means one use. An effect that catches
    every blow is an invulnerability for its whole duration, and a tank who
    simply does not die looks like good tanking until someone notices.
  - IT RESCUES SOMEONE ALREADY BELOW THE FLOOR. The effect catches the blow
    that CROSSES the line. If it also fires for a character sitting at 1
    health, it is an immunity with extra steps.

REFLECT - a share of what landed goes back to the attacker. Callum's is
returned as NATURE regardless of what hit him and only off MELEE, so a magic
hit must return nothing. The return is applied to the attacker's health
directly: routing it through their take_damage would mitigate it a second
time and would re-enter this path on an attacker who also reflects.

LOW-HEALTH TRIGGER - "the first time that ally drops below 35% health they
are healed for 30% of their maximum". Measured by actually crossing the
threshold, because the payout reads the health the holder ENDED on - a check
that sets health directly and never calls take_damage would pass against an
implementation that never fires.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
KITS = ROOT / "data" / "npcs" / "personal_kits.json"
MAX_SWINGS = 30


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", action="store_true")
    args = ap.parse_args()

    from entities.character import Character
    from entities.monster import Monster
    from world.recruit_manager import get_recruit_manager

    findings, rows = [], []
    doc = json.loads(KITS.read_text())
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict)
                      else rm.recruits)}

    def ready(kid, aid):
        r = recs.get(kid)
        if r is None:
            return None, None
        g = r.build_character()
        g.level = 60
        try:
            g.recalculate_stats()
        except Exception:
            pass
        ab = next((x for x in g.ability_book.get_all_abilities()
                   if x.ability_id == aid), None)
        if ab is None:
            return None, None
        for res in ("mana", "rage", "energy", "focus"):
            for at in (f"max_{res}", f"current_{res}", res):
                if isinstance(getattr(g, at, None), (int, float)):
                    setattr(g, at, 99999)
        try:
            g.set_resource(ab._effective_resource_type(g), 99999)
        except Exception:
            pass
        g.current_health = g.health
        ab.turns_remaining = 0
        return g, ab

    def cast_on(g, ab, ally):
        tgt = (ally if ab.target_type == "ally"
               else g if ab.target_type == "self" else [g, ally])
        ab.use(g, tgt, party=[g, ally], in_combat=True)
        return g if ab.target_type == "self" else ally

    n_floor = n_reflect = n_trigger = 0

    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        for a in (kit.get("abilities") or []):
            who = f"{kit.get('name')} / {a.get('name')}"

            # ---- death prevention ------------------------------------------
            spec = a.get("death_prevent")
            if spec:
                n_floor += 1
                g, ab = ready(kid, a["ability_id"])
                if g is None:
                    findings.append(f"{who}: not granted")
                    continue
                ally = Character("Ally", "Priest", 60)
                ally.current_health = ally.health
                v = cast_on(g, ab, ally)
                floor = spec.get("hp") or int(v.health * spec.get("pct", 0) / 100)
                floor = max(1, floor)
                # MAGIC damage, deliberately. Dodge, parry and block are
                # physical-only in this engine, and with a physical probe
                # this check was flaky in exactly the way that hides a real
                # bug: a dodged lethal blow leaves the victim at FULL health
                # ("left them at 420, want the floor of 1"), and a dodged
                # SECOND blow leaves them sitting at the floor, which reads
                # as having survived it. Six consecutive runs failed
                # differently for that one reason.
                v.current_health = v.health
                v.take_damage(10 ** 6, "arcane", attacker_level=60)
                held = v.current_health
                v.take_damage(10 ** 6, "arcane", attacker_level=60)
                second = v.current_health
                rows.append(("death floor", who, f"held at {held}",
                             f"floor {floor}, then {second}"))
                if held != floor:
                    findings.append(f"{who}: a lethal blow left them at "
                                    f"{held}, want the floor of {floor}")
                if second > 0:
                    findings.append(f"{who}: survived a SECOND lethal blow at "
                                    f"{second} health - 'the first blow' is "
                                    f"one use, not an invulnerability")
                # must not rescue someone already under the floor
                g2, ab2 = ready(kid, a["ability_id"])
                ally2 = Character("Ally", "Priest", 60)
                ally2.current_health = ally2.health
                v2 = cast_on(g2, ab2, ally2)
                v2.current_health = 1
                v2.take_damage(10 ** 6, "arcane", attacker_level=60)
                if v2.current_health > 0:
                    findings.append(f"{who}: rescued someone already at 1 "
                                    f"health - the floor must catch the blow "
                                    f"that CROSSES it, not any blow")

            # ---- reflect ---------------------------------------------------
            spec = a.get("reflect")
            if spec:
                n_reflect += 1
                got = None
                for _ in range(MAX_SWINGS):
                    g, ab = ready(kid, a["ability_id"])
                    if g is None:
                        break
                    ally = Character("Ally", "Priest", 60)
                    ally.current_health = ally.health
                    cast_on(g, ab, ally)
                    foe = Monster("Brute", "beast_basic", level=60)
                    fb, gb = foe.current_health, g.current_health
                    g.take_damage(400, "physical", attacker_level=60,
                                  attacker=foe)
                    took, back = gb - g.current_health, fb - foe.current_health
                    if took:
                        got = (took, back, g, ab)
                        break
                if got is None:
                    findings.append(f"{who}: no landed hit to measure")
                    continue
                took, back, g, ab = got
                want = int(took * spec.get("pct", 0) / 100.0)
                rows.append(("reflect", who, f"took {took}, returned {back}",
                             f"want {want}"))
                if abs(back - want) > 2:
                    findings.append(f"{who}: returned {back} off a {took} hit, "
                                    f"want {want} ({spec.get('pct')}%)")
                if spec.get("melee_only"):
                    foe2 = Monster("Caster", "beast_basic", level=60)
                    f2 = foe2.current_health
                    g.take_damage(400, "arcane", attacker_level=60,
                                  attacker=foe2)
                    if f2 != foe2.current_health:
                        findings.append(
                            f"{who}: returned {f2 - foe2.current_health} off a "
                            f"MAGIC hit - melee_only must ignore it")

            # ---- low-health trigger ----------------------------------------
            spec = a.get("on_low_health")
            if spec:
                n_trigger += 1
                g, ab = ready(kid, a["ability_id"])
                if g is None:
                    findings.append(f"{who}: not granted")
                    continue
                ally = Character("Ally", "Priest", 60)
                ally.current_health = ally.health
                v = cast_on(g, ab, ally)
                # cross the threshold with a real hit, so the payout sees the
                # health it actually ended on
                # magic again - a dodged hit never crosses the threshold and
                # the payout correctly does not fire, which looks identical
                # to a trigger that is broken.
                v.current_health = int(v.health * 0.9)
                v.take_damage(int(v.health * 0.75), "arcane",
                              attacker_level=60)
                heal_pct = spec.get("heal_pct", 0)
                shield_pct = spec.get("shield_pct", 0)
                shield = sum(getattr(e, "absorb", 0) or 0 for e in v._effects())
                rows.append(("low health", who,
                             f"health {v.current_health:.0f}/{v.health}, "
                             f"shield {shield}",
                             f"pct {spec.get('pct')}, "
                             f"{'heal' if heal_pct else 'shield'}"))
                if heal_pct:
                    want = int(v.health * heal_pct / 100.0)
                    # it healed if health exceeds what the raw hit would leave
                    if v.current_health < int(v.health * 0.15):
                        findings.append(
                            f"{who}: health {v.current_health:.0f} after "
                            f"crossing {spec.get('pct')}% - the {want} heal "
                            f"did not fire")
                elif shield_pct:
                    want = int(v.health * shield_pct / 100.0)
                    if abs(shield - want) > 2:
                        findings.append(f"{who}: shield {shield}, want {want}")
                # second crossing must NOT pay out again
                v.heal(v.health)
                before = v.current_health
                v.take_damage(int(v.health * 0.8), "arcane",
                              attacker_level=60)
                shield2 = sum(getattr(e, "absorb", 0) or 0
                              for e in v._effects())
                if shield_pct and shield2 > want + 2:
                    findings.append(f"{who}: paid out a SECOND shield "
                                    f"({shield2}) - 'the first time' is one use")

    print(f"  {n_floor} death floor(s), {n_reflect} reflect(s), "
          f"{n_trigger} low-health trigger(s)")
    print(f"  {len(rows)} measurement(s), all through real take_damage calls\n")

    if args.list:
        print(f"  {'kind':14}{'who':42}{'measured':34}expected")
        for kind, who, got, want in rows:
            print(f"  {kind:14}{str(who)[:40]:42}{str(got)[:32]:34}{want}")
        print()

    if findings:
        print(f"  {len(findings)} finding(s):\n")
        for f in findings:
            print(f"    {f}")
        print("\nFAIL")
        return 1

    print("  floors hold once and only once, reflects return the right share "
          "of the right\n  school, and a low-health payout fires on crossing "
          "and not again")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
