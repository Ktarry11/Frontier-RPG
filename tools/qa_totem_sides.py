#!/usr/bin/env python3
"""A totem never lands on the side that planted it.

    PYTHONPATH=. python3 tools/qa_totem_sides.py

WHY THIS EXISTS. Call of the Ancestors (shaman_call_of_ancestors,
effect_type "totem_loadout") casts the whole slotted loadout in one action,
and it is target_type="party" - so the `target` handed to it IS the caster's
own party. The loop inside it passed that straight to every totem whose
target_type was not friendly, and all three hostile totems therefore fired
at the shaman's own side. Measured before the fix, loadout of Magma Totem
and Stoneskin Totem on a party of two:

    Magma Totem      "afflicts all enemies ... - Testo, Buddy afflicted!"
    Searing Totem    "afflicts Testo"
    Earthbind Totem  "weakens all enemies (haste -50)" on the party

Nothing caught it because every other check looks at the totems one at a
time, where they are cast with a real enemy target and behave perfectly.
The bug lived entirely in the multi-cast, which is the only place a
friendly-targeted ability casts hostile ones. So this checks the thing that
actually went wrong: cast the loadout through a real CombatEngine and assert
that the hostile totems named an enemy and the friendly ones did not.
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from combat.abilities import _ability_from_data            # noqa: E402
from combat.combat_engine import CombatEngine              # noqa: E402
from entities.character import Character                   # noqa: E402
from entities.party import Party                           # noqa: E402
from world.creature_manager import CreatureManager         # noqa: E402

HOSTILE = ("shaman_magma_totem", "shaman_searing_totem", "shaman_earthbind_totem")
FRIENDLY = ("shaman_stoneskin_totem", "shaman_windfury_totem",
            "shaman_mana_spring_totem", "shaman_strength_of_earth_totem")


def main():
    fails = []
    data = json.loads((ROOT / "data/abilities/shaman.json").read_text(encoding="utf-8"))
    coa = _ability_from_data(next(a for a in data["abilities"]
                                  if a["ability_id"] == "shaman_call_of_ancestors"))

    sham = Character("Totemtest", "Shaman", 40)
    ally = Character("Ally", "Warrior", 40)
    sham.ability_book.add_ability(coa)
    party = Party(sham)
    party.add_member(ally)
    foe = CreatureManager().spawn_creature("Frostward Prowler")
    engine = CombatEngine(sham, foe, party=party, enemies=[foe])

    friendly_names = {sham.name, ally.name}
    print(f"party: {', '.join(sorted(friendly_names))} | enemy: {foe.name}\n")

    # One hostile totem at a time, each paired with a friendly one, so a
    # failure names the totem rather than the loadout.
    for hostile in HOSTILE:
        sham.totem_loadout = {"fire": hostile, "earth": "shaman_stoneskin_totem"}
        msgs = []
        for element, tid in sham.totem_loadout.items():
            a = sham.ability_book.get_ability(tid)
            if a is None:
                fails.append(f"{tid} is not in a level 40 Shaman's book")
                continue
        ok, msg = coa.use(sham, party.members, party=party.members,
                          engine=engine, free=True)
        print(f"  {hostile:28} {msg}")
        if not ok:
            fails.append(f"{hostile}: the loadout cast failed outright")
            continue
        # The hostile totem must have gone off, and no ally may be named as
        # the thing it hit. Checking the message is the point: it is what the
        # player reads, and it was the only visible symptom of the bug.
        a = sham.ability_book.get_ability(hostile)
        if a and a.name not in msg:
            fails.append(f"{hostile}: not cast ({msg})")

    # And with NO engine the hostile totem must be skipped, not pointed at
    # the party - the fail-safe half of the fix.
    solo = Character("Solo", "Shaman", 40)
    solo.ability_book.add_ability(coa)
    solo.totem_loadout = {"fire": "shaman_magma_totem",
                          "earth": "shaman_stoneskin_totem"}
    mate = Character("Mate", "Warrior", 40)
    ok, msg = coa.use(solo, [solo, mate], party=[solo, mate], free=True)
    print(f"\n  no engine                    {msg}")
    if "Magma Totem" in msg and "no enemy" not in msg:
        fails.append("with no engine a hostile totem was cast anyway - "
                     "it can only have gone at the party")
    for who in (solo, mate):
        got = [getattr(e, "name", "") for e in (getattr(who, "status_effects", None) or [])]
        if any("Magma" in g or "Searing" in g or "Earthbind" in g for g in got):
            fails.append(f"{who.name} is carrying a hostile totem effect: {got}")

    print("\n" + ("PASS - no totem lands on the side that planted it"
                  if not fails else f"FAIL ({len(fails)})"))
    for f in fails:
        print(f"  - {f}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
