#!/usr/bin/env python3
"""Recruit friendship works the way Kyle asked, for the three pilot recruits.

    PYTHONPATH=. python3 tools/qa_recruit_bonds.py

Kyle, 13 Nov 2026: "theres nothing special with the 3 recruits....its all the same, no way to
improve their relationship." Design: claude/recruit_bonds_DESIGN_ONLY.md. Engine:
world/bond_manager.py. Text: tools/build_recruit_bonds.py.

Played through the real party, the real recruit manager and the real save format:
  1. the text exists for all three and passes the voice check
  2. a first-meeting answer matters: the wrong one sends you away until your next outing
  3. trust grows with outings and moves the stage up; taking gear dips it but never drops a stage
  4. a stint ends at a safe point only: never inside a dungeon, always in a town
  5. a break is real: their spot is empty until you've done enough without them, and a Friend
     sends word when they're back
  6. Adrián's first goodbye is a question, and asking him to stay keeps him
  7. wipes: always a warning first; a nervy one walks out at the door, a steady one finishes
     the run; an angry walkout means a longer break and a talk before they rejoin
  8. a zone too high: a warning, then they leave at the next town, never in the field
  9. gear: a Stranger refuses, a Friend hands it over and wants it replaced, an upgrade helps
 10. grinding wears them down and the warning names the cause
 11. pairs who travel together long enough get their own banter
 12. it all survives a save and load
 13. the screens draw: the first meeting, the talk view and the test panel
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
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

K, A, T = "kesten_the_catalogued", "adrian_templar", "tarek_templar"


class Z:
    def __init__(self, name, town=False):
        self.name, self.is_town = name, town


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    with contextlib.redirect_stdout(io.StringIO()):
        import subprocess
        r = subprocess.run([sys.executable, str(ROOT / "tools/build_recruit_bonds.py")],
                           capture_output=True, text=True)
        from world.recruit_manager import reset_recruit_manager
        from world.bond_manager import get_bond_manager, STAGES, THRESHOLDS
        from entities.character import Character
        from entities.party import Party
    check(r.returncode == 0, f"the pilot text fails its own checks: {r.stdout[-400:]}")

    def fresh(level=40):
        with contextlib.redirect_stdout(io.StringIO()):
            rm = reset_recruit_manager()
            bm = get_bond_manager()
            hero = Character(name="Hero", char_class="Warrior", level=level)
            party = Party(hero)
        bm.party = party
        return rm, bm, party

    def hire(rm, bm, party, rid, answer=0):
        m = bm.hire_moment(rid)
        if m is not None:
            bm.answer(rid, m["id"], answer)
        ok, _ = bm.can_hire(rid)
        if not ok:
            return None
        with contextlib.redirect_stdout(io.StringIO()):
            ch = rm.build_or_restore(rm.recruits[rid], party.player.level)
            party.add_member(ch)
            rm.mark_recruited(rid)
        bm.on_joined(rid)
        return ch

    def in_party(party, rid):
        return any(getattr(m, "recruit_id", None) == rid for m in party.members)

    # 1
    rm, bm, party = fresh()
    for rid in (K, A, T):
        b = bm.get(rid)
        check(b is not None, f"{rid} has no friendship record")
        if b:
            check(len(bm.learned(rid)) == 1, f"{rid}: a stranger should tell you one thing")
            for key in ("bored_warning", "leaving_good", "wipe_warning", "zone_warning", "back",
                        "walkout_talk", "gear_refuse", "gear_upgrade", "neglect"):
                check(bool(bm.line(rid, key)), f"{rid}: no line for {key}")

    # 2
    check(hire(rm, bm, party, K, answer=1) is None, "Kesten joined after being asked his number")
    check(not in_party(party, K), "Kesten is in the party after the wrong answer")
    bm.on_deed("quest", party)
    check(hire(rm, bm, party, K, answer=0) is not None, "Kesten won't join after the right answer")

    # 3
    b = bm.get(K)
    start = b.stage
    for _ in range(3):
        bm.on_deed("dungeon", party, zone=Z("The Open Road"))
        if not in_party(party, K):
            break
    check(b.trust > 0, "trust didn't grow with outings")
    b.trust = THRESHOLDS[2]
    bm._trust(b, 0)
    check(b.stage == 2, f"trust at the Companion threshold left him at {STAGES[b.stage]}")
    bm._trust(b, -50)
    check(b.stage == 2 and b.trust >= THRESHOLDS[2], "a dip dropped him a stage")
    check(b.stage >= start, "stage went down")

    # 4
    rm, bm, party = fresh()
    hire(rm, bm, party, T)
    b = bm.get(T)
    b.outings = b.stint_len
    bm.on_deed("quest", party, zone=Z("Ragefire Chasm"))
    check(in_party(party, T), "Tarek went home from inside a dungeon")
    bm.on_zone(Z("Orgrimmar", town=True), party)
    check(not in_party(party, T), "Tarek's stint ended and he didn't go home in town")

    # 5
    check(b.away, "Tarek isn't on a break after going home")
    here = [r.recruit_id for r in rm.get_recruits_in_zone(rm.recruits[T].zone)]
    check(T not in here, "Tarek is standing at home while on his break")
    check(not bm.can_hire(T)[0], "Tarek can be hired straight back")
    b.stage = STAGES.index("friend")
    for _ in range(10):
        bm.on_deed("quest", party)
    check(not b.away, "Tarek never came back from his break")
    check(any("sent word" in t for _r, t in bm.log), "a Friend back from a break sent no word")

    # 6
    rm, bm, party = fresh()
    hire(rm, bm, party, A)
    b = bm.get(A)
    b.outings = b.stint_len
    bm.on_zone(Z("Astranaar", town=True), party)
    check(in_party(party, A) and b.pending == "first_goodbye",
          "Adrián's first goodbye wasn't a question")
    m = bm.talk_moment(A)
    check(m is not None and m["id"] == "first_goodbye", "the party screen can't ask the question")
    bm.answer(A, "first_goodbye", 0)
    check(in_party(party, A) and "asked_to_stay" in b.flags, "asking Adrián to stay didn't keep him")

    # 7
    rm, bm, party = fresh()
    hire(rm, bm, party, A)
    hire(rm, bm, party, K)
    a, k = bm.get(A), bm.get(K)
    log0 = len(bm.log)
    for _ in range(8):
        bm.on_wipe(party, at_dungeon_door=True)
        if a.pending:
            bm.answer(A, a.pending, 0)
        if not in_party(party, A):
            break
    said = [t for r, t in bm.log[log0:] if r == A]
    check(bm.line(A, "wipe_warning") in said, "Adrián walked out without warning first")
    check(not in_party(party, A), "Adrián (nervy) never walked out at the door")
    check(a.angry and a.needs_talk, "an angry walkout doesn't need a talk")
    check(a.break_left >= 2 * 4 - 1, "an angry walkout didn't mean a longer break")
    check(bm.walkout_talk(A), "no talk before Adrián rejoins")
    for _ in range(6):
        bm.on_wipe(party, at_dungeon_door=True)
    check(in_party(party, K), "Kesten (steady) walked out instead of finishing the run")
    check(k.leave_cause == "wipe", "Kesten isn't set to leave after the run")
    bm.on_zone(Z("Undercity", town=True), party)
    check(not in_party(party, K), "Kesten didn't leave at the town after the run")

    # 8
    rm, bm, party = fresh(level=26)
    hire(rm, bm, party, T)
    t = bm.get(T)
    tm = next(m for m in party.members if getattr(m, "recruit_id", None) == T)
    orig = bm._zone_level
    bm._zone_level = lambda z: tm.level + 6 if z.name == "Hot" else orig(z)
    log0 = len(bm.log)
    for _ in range(4):
        bm.on_zone(Z("Hot"), party)
    check(bm.line(T, "zone_warning") in [x for _r, x in bm.log[log0:]], "no too-dangerous warning")
    check(in_party(party, T), "Tarek left in the field")
    bm._zone_level = orig
    bm.on_zone(Z("Splintertree Post", town=True), party)
    check(not in_party(party, T), "Tarek didn't leave at the town after the warning")

    # 9
    rm, bm, party = fresh()
    ch = hire(rm, bm, party, K)
    slot = next((s for s, it in ch.equipment.slots.items() if it is not None and not s.startswith("bag")), None)
    if slot:
        ch.last_refusal = None
        check(not ch.unequip_item(slot, into=party.player), "a Stranger handed over his gear")
        check(bool(getattr(ch, "last_refusal", None)), "the refusal wasn't said")
        bm.get(K).stage = STAGES.index("friend")
        check(ch.unequip_item(slot, into=party.player), "a Friend wouldn't hand over his gear")
        check(slot in bm.get(K).short, "the empty slot isn't remembered")
        bm.on_gear_given(K, slot, better=True)
        check(slot not in bm.get(K).short, "an upgrade didn't clear the empty slot")
    else:
        bad.append("Kesten has no gear to test with")

    # 10
    rm, bm, party = fresh()
    hire(rm, bm, party, T)
    t = bm.get(T)
    log0 = len(bm.log)
    for _ in range(6):
        bm.on_kills([type("E", (), {"is_boss": False, "monster_type": "beast", "name": "Boar"})()] * 30,
                    party, zone=Z("Ashenvale East"))
    check(t.warned == "bored", f"grinding didn't warn about boredom (warned {t.warned})")
    check(bm.line(T, "bored_warning") in [x for _r, x in bm.log[log0:]], "the bored warning wasn't said")

    # 11
    rm, bm, party = fresh()
    hire(rm, bm, party, T)
    hire(rm, bm, party, A)
    for b in (bm.get(T), bm.get(A)):
        b.stint_len = 99
        b.flags.append("asked_to_stay")
    for _ in range(9):
        bm.on_deed("quest", party, zone=Z("Ragefire Chasm"))
    check(any(p.startswith(T) or p.endswith(T) for p in bm.pairs_heard), "Tarek and Adrián never talked")

    # 12
    data = rm.to_dict()
    with contextlib.redirect_stdout(io.StringIO()):
        rm2 = reset_recruit_manager()
        rm2.load_state(json.loads(json.dumps(data)))
    bm2 = get_bond_manager()
    check(bm2.deeds == bm.deeds and bm2.get(T).trust == bm.get(T).trust
          and bm2.pairs_heard == bm.pairs_heard, "friendship didn't survive a save and load")

    # 13
    with contextlib.redirect_stdout(io.StringIO()):
        from core.game_state import GameStateManager
        from core.game_states import GameState
        screen = pygame.Surface((1600, 900))
        try:
            gsm = GameStateManager(screen)
            rm, bm, party = fresh()
            gsm.get_party = lambda: party
            from ui.screens.recruit_dialog_screen import RecruitDialogScreen
            d = RecruitDialogScreen(gsm, rm.recruits[K])
            d.render(screen)
            check(d.option_rects, "the first meeting shows no replies")
            hire(rm, bm, party, K)
            d = RecruitDialogScreen(gsm, rm.recruits[K])
            d.render(screen)
            from ui.screens.bond_test_screen import BondTestScreen
            p = BondTestScreen(gsm)
            p.render(screen)
            check(len(p.rects) >= 7 + 3 * 6, "the test panel is missing buttons")
            from ui.screens.party_screen import PartyScreen
            ps = PartyScreen(gsm)
            ps.selected = next(m for m in party.members if getattr(m, "recruit_id", None) == K)
            ps.render(screen)
            check(any(a == "talk" for a, _r in ps.action_rects), "the party screen has no Talk button")
        except Exception as exc:
            import traceback
            bad.append(f"a screen failed to draw: {exc}\n{traceback.format_exc()[-800:]}")

    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("recruit friendship OK - answers matter, trust grows and never drops a stage, nobody leaves "
          "in a dungeon, breaks are real, wipes and high zones warn first, gear is refused or "
          "missed, pairs talk, and it saves.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
