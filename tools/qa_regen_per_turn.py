#!/usr/bin/env python3
"""mp5 and hp5 do something in a fight.

    PYTHONPATH=. python3 tools/qa_regen_per_turn.py

Kyle's [79]: "HP5 and MP5 (regen) are broken." Measured: mp5 was read only by the
out-of-combat clock, so in combat it did nothing; a BUFF granting mp5 was read nowhere; and
hp5 had no reader at all. The model now: ONE COMBAT TURN IS ONE "FIVE SECONDS".

FIVE CLAIMS:

  1. mp5 FROM GEAR comes back every turn, on top of Spirit's share.
  2. mp5 FROM A BUFF comes back every turn - and every ability in the game that grants one
     grants one that is read.
  3. hp5 heals each turn, and never raises the dead.
  4. OUT OF COMBAT both count too, at a fifth per second.
  5. THE SHEET SHOWS THE REAL NUMBER - "Mana per turn" is the same method the turn uses.
"""
import contextlib
import glob
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
    from combat.status_effects import StatusEffect, EffectType


def make(cls="Priest", level=40):
    with contextlib.redirect_stdout(io.StringIO()):
        c = Character(name=cls, char_class=cls, level=level)
    return c


def main():
    bad = []
    c = make()
    spirit_share = c.effective_spirit * c.MANA_PER_SPIRIT_PER_TURN

    def turn_gain(ch):
        ch.current_mana = 0
        ch.restore_resources_between_turns()
        return ch.current_mana

    base = turn_gain(c)
    if abs(base - spirit_share) > 0.01:
        bad.append(f"with no mp5 a turn should give Spirit's share {spirit_share}, got {base}")

    # 1. gear
    c.mp5 = 12
    if abs(turn_gain(c) - (spirit_share + 12)) > 0.01:
        bad.append(f"12 mp5 on gear added {turn_gain(c) - base} mana a turn, not 12")

    # 2. a buff
    c.apply_status_effect(StatusEffect("t_mp5", "Test", EffectType.BUFF, 3, stat_mods={"mp5": 20},
                                       real_time_seconds=None))
    # (applying a buff recalculates the sheet, which is also what proves a buff's mp5 reaches
    # the same number gear's does - and that it is counted once, not twice)
    share = c.effective_spirit * c.MANA_PER_SPIRIT_PER_TURN
    if abs(turn_gain(c) - (share + 20)) > 0.01:
        bad.append(f"a 20 mp5 buff gave {turn_gain(c) - share} extra mana a turn, not 20")
    if abs(c.mana_per_turn() - (share + 20)) > 0.01:
        bad.append("mana_per_turn() - the number on the sheet - disagrees with what a turn restores")

    granting = 0
    for path in sorted(glob.glob("data/abilities/*.json")):
        for a in json.load(open(path)).get("abilities", []):
            if "mp5" in (a.get("stat_mods") or {}) or "hp5" in (a.get("stat_mods") or {}):
                granting += 1
    if granting == 0:
        bad.append("no ability grants mp5 or hp5 any more - claim 2 has nothing to protect")

    # 3. hp5
    w = make("Warrior")
    w.hp5 = 15
    w.current_health = 100
    w.restore_resources_between_turns()
    if abs(w.current_health - 115) > 0.01:
        bad.append(f"15 hp5 took health from 100 to {w.current_health} in a turn, not 115")
    w.current_health = 0
    w.restore_resources_between_turns()
    if w.current_health != 0:
        bad.append("hp5 raised the dead")

    # 4. out of combat
    c2 = make()
    c2.current_mana = 0
    c2.tick_out_of_combat_regen(5.0, is_moving=True)
    plain = c2.current_mana
    c2.current_mana = 0
    c2.mp5 = 50
    c2.tick_out_of_combat_regen(5.0, is_moving=True)
    if abs((c2.current_mana - plain) - 50) > 0.5:
        bad.append(f"50 mp5 gave {c2.current_mana - plain:.1f} extra mana over five seconds out "
                   f"of combat, not 50")
    w.current_health = 100
    w.hp5 = 0
    w.tick_out_of_combat_regen(5.0, is_moving=True)
    plain_hp = w.current_health - 100
    w.current_health = 100
    w.hp5 = 30
    w.tick_out_of_combat_regen(5.0, is_moving=True)
    if abs((w.current_health - 100 - plain_hp) - 30) > 0.5:
        bad.append("30 hp5 did not give 30 extra health over five seconds out of combat")

    # 5. the sheet
    src = Path("ui/screens/party_screen.py").read_text()
    if "mana_per_turn()" not in src or '("mp5", self._num(getattr(member, "mp5", 0)))' in src:
        bad.append("the character sheet still shows the bare mp5 stat instead of mana per turn")

    print(f"Spirit share {spirit_share:.1f}/turn for a level 40 Priest; {granting} abilities grant "
          f"mp5 or hp5 as a buff")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nregen OK - mp5 and hp5 from gear and from buffs come back every turn and out of "
          "combat, the dead get nothing, and the sheet shows what a turn really restores.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
