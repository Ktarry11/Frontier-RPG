#!/usr/bin/env python3
"""A character has its race's abilities - and a companion has none of them.

    PYTHONPATH=. python3 tools/qa_racials.py

Kyle, [10]: "Recruits need to feel unique - not all the same human racials."

Two faults, opposite ways round:
  * 67 of the 68 companions carried the Azerothian Human racial - the same Every Man for
    Himself, Perception and The Human Spirit on 67 Core tabs - because they are drawn as humans.
    They are people from Earth; what makes each one different is the personal kit.
  * THE PLAYER had the reverse: its race's passive, and none of its abilities. Nothing gave a
    new Orc Blood Fury, and an ability given by hand was gone after a save and load.

FIVE CLAIMS:
  1. NO COMPANION HAS A RACIAL ABILITY OR A RACIAL PASSIVE, and each still has its own kit.
  2. NO TWO COMPANIONS SHARE A PASSIVE - the thing that is theirs alone really is.
  3. EVERY PLAYABLE RACE GIVES A NEW CHARACTER ITS ABILITIES, in the Core tab.
  4. THEY SURVIVE A SAVE AND A LOAD - and so does a companion's kit, without the racial
     coming back.
  5. A RACE'S PASSIVE REACHES THE CHARACTER - every number it lists - and nobody else's does.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from entities.character import Character
    from world import personal_kits as PK
    from world.recruit_manager import get_recruit_manager
    from world.race_registry import get_race


def racial_ids(c):
    return sorted(a for a in c.ability_book.abilities if str(a).startswith("racial_"))


def main():
    bad = []
    racials = {k: v for k, v in json.load(open("data/races/racials.json", encoding="utf-8")).items() if not k.startswith("_")}

    # ---- 1, 2. companions
    rm = get_recruit_manager()
    passives, built = {}, 0
    for rec in rm.recruits.values():
        with contextlib.redirect_stdout(io.StringIO()):
            c = rm.build_or_restore(rec, player_level=60)
        if c is None:
            continue
        built += 1
        if racial_ids(c):
            bad.append(f"{c.name} carries racial abilities: {racial_ids(c)}")
        entries = PK.passive_entries_for(c)
        if any(source == "Racial" for _n, source, _l in entries):
            bad.append(f"{c.name} lists a racial passive")
        if PK.racial_of(c) is not None:
            bad.append(f"{c.name} is given a racial block")
        if rec.recruit_id != "asher_coleman":
            mine = [n for n, source, _l in entries if source == "Personal"]
            own = [a for a in c.ability_book.abilities if str(a).startswith("personal_")]
            if not mine or not own:
                bad.append(f"{c.name} has no personal passive or no personal abilities")
            for n in mine:
                passives.setdefault(n, []).append(c.name)
        # a companion saved while it still had the racial loses it on the next grant
        with contextlib.redirect_stdout(io.StringIO()):
            from combat.abilities import _ability_from_data
            stale = racials["human"]["abilities"][0]
            c.ability_book.add_ability(_ability_from_data(stale))
            back = Character.from_dict(c.to_dict())
        if racial_ids(back):
            bad.append(f"{c.name} got a racial back from a save: {racial_ids(back)}")
            break
    shared = {n: who for n, who in passives.items() if len(who) > 1}
    if shared:
        bad.append(f"companions share a named passive: {shared}")

    # ---- 3, 4, 5. players
    for race, block in racials.items():
        opt = get_race(race)
        if opt is None or not getattr(opt, "available", True):
            continue
        want = sorted(a["ability_id"] for a in block.get("abilities", []))
        with contextlib.redirect_stdout(io.StringIO()):
            plain = Character("p", "Warrior")
            plain.race = None                      # a character of no race at all, to compare with
            plain._recalculate_derived_stats()
            c = Character("p", "Warrior")
            c.race = race
            PK.grant(c)
            c._recalculate_derived_stats()
        if racial_ids(c) != want:
            bad.append(f"a new {race} has {racial_ids(c)}, the race gives {want}")
        with contextlib.redirect_stdout(io.StringIO()):
            back = Character.from_dict(c.to_dict())
        if racial_ids(back) != want:
            bad.append(f"a {race} loaded from a save has {racial_ids(back)}, not {want}")
        # the passive is in force: every number the race lists reaches the character
        scal = dict(PK.passives_for(c))
        scal.update({k: c.get_talent_effect(k, 0) for k in PK.combat_passives_for(c)})   # the ones combat reads by name
        listed = [k for k, v in (block.get("passives") or {}).items()
                  if not k.startswith("_") and isinstance(v, (int, float)) and v]
        gone = [k for k in listed if not scal.get(k)]
        if gone:
            bad.append(f"{race}'s passive lists {gone} and the character does not get them")
        if PK.passives_for(plain):
            bad.append("a character of no race is given a racial passive")
    src = Path("ui/screens/character_screen.py").read_text(encoding="utf-8")
    if "grant(char)" not in src:
        bad.append("character creation never grants the race's abilities")

    print(f"{built} companions carry no racial; {len(passives)} distinct personal passives; "
          f"{len(racials)} races give their abilities at creation and after a load")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad[:20]:
            print("  -", line)
        return 1
    print("\nracials OK - a companion is its own person, and a player has what its race gives.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
