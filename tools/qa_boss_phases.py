#!/usr/bin/env python3
"""Boss phases work: a boss can become another creature, or change its kit, when its health crosses a line.

    PYTHONPATH=. python3 tools/qa_boss_phases.py

Kyle, 16 Nov 2026, on Dathrohan turning into Balnazzar: "if you need to build the proper transformation mechanism
thats fine. A lot of raids have them... having the mechanism in place for phases is good." The mechanism is
entities/monster.Monster._phase_cap and _enter_phase, fed from a creature's "phases" list in creatures.json:
    {"at_pct": 40, "into": "<creature>", "text": "<combat log line>"}       become another creature
    {"at_pct": 50, "kit": "<kit id>", "text": "..."}                         same creature, new abilities
Holds, on two real creatures with a phase added in memory:
  1. a blow that would cross the line (even a killing one) stops on it, and the boss becomes the new creature,
     at the new creature's full health, with its name and kit, and the old name remembered
  2. the combat log gets the phase's line
  3. a kit phase changes the abilities and nothing else
  4. a creature with no phases is untouched by the same blow
  5. every phase written in creatures.json names a creature or kit that exists
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    from world.creature_manager import CreatureManager
    from entities.monster import get_kits
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        cm = CreatureManager()
    first, second = "Bloodmage Thalnos", "Arcanist Doan"
    for n in (first, second):
        if n not in cm.creatures:
            print(f"FAIL - {n} isn't a creature")
            return 1
    cm.creatures["_qa_phaser"] = dict(cm.creatures[first], phases=[
        {"at_pct": 40, "into": second, "text": "The QA boss tears off its face."}])
    m = cm.spawn_creature("_qa_phaser")
    before_kit = m.kit_id
    line = int(m.max_health * 0.4)
    m.dodge = m.parry = m.block_chance = 0
    m.take_damage(m.max_health * 50, "physical")               # far more than lethal
    want = cm.spawn_creature(second, level=m.level)
    if not m.is_alive():
        bad.append("the blow that crossed the line killed the boss instead of turning it")
    if m.name != second:
        bad.append(f"after the line it's called {m.name}, not {second}")
    if m.max_health != want.max_health or m.current_health != m.max_health:
        bad.append(f"the new form has {m.current_health}/{m.max_health}, not {want.max_health} full")
    if m.kit_id == before_kit or m.kit_id != want.kit_id:
        bad.append("the new form didn't take its own kit")
    if m.former_names != ["_qa_phaser"]:
        bad.append(f"the old name isn't remembered ({m.former_names})")
    log = getattr(m, "_pending_proc_messages", []) or []
    if "The QA boss tears off its face." not in log:
        bad.append("the phase's line never reached the combat log")
    m.dodge = m.parry = m.block_chance = 0
    m.take_damage(10, "physical")
    if m.name != second or m.current_health != m.max_health - 10 and m.current_health >= m.max_health:
        bad.append("the new form doesn't take damage like itself")
    print(f"  {first} at {line} health -> {m.name} at {want.max_health}")

    other_kit = cm.creatures[second]["ability_kit"]
    cm.creatures["_qa_kitphase"] = dict(cm.creatures[first], phases=[{"at_pct": 50, "kit": other_kit}])
    k = cm.spawn_creature("_qa_kitphase")
    hp = k.max_health
    k.dodge = k.parry = k.block_chance = 0         # a dodged blow crosses nothing
    k.take_damage(hp * 50, "physical")                   # armour can't save it from crossing
    if k.kit_id != other_kit or k.name != "_qa_kitphase" or k.max_health != hp:
        bad.append("a kit phase changed more (or less) than the kit")
    if k.current_health != int(hp * 0.5) and abs(k.current_health - int(hp * 0.5)) > 1:
        bad.append(f"the kit phase's blow didn't stop on the line ({k.current_health} of {hp})")

    plain = cm.spawn_creature(first)
    plain.dodge = plain.parry = plain.block_chance = 0
    plain.take_damage(plain.max_health * 50, "physical")
    if plain.is_alive() or plain.name != first:
        bad.append("a creature with no phases was changed by the phase code")

    kits = get_kits()
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    n = 0
    for name, c in creatures.items():
        for ph in c.get("phases") or []:
            n += 1
            if ph.get("into") and ph["into"] not in creatures:
                bad.append(f"{name}'s phase turns into {ph['into']}, which isn't a creature")
            if ph.get("kit") and ph["kit"] not in kits:
                bad.append(f"{name}'s phase kit {ph['kit']} doesn't exist")
            if not (0 < float(ph.get("at_pct", 0)) < 100):
                bad.append(f"{name}'s phase line {ph.get('at_pct')} isn't a share of health")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad:
            print("  -", b)
        return 1
    print(f"PASS - a boss becomes another creature or another kit at its line; {n} phases written in the bestiary")
    return 0


if __name__ == "__main__":
    sys.exit(main())
