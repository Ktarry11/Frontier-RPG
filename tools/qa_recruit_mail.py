#!/usr/bin/env python3
"""Writing to recruits who've gone home works the way Kyle asked (world/recruit_mail.py).

    PYTHONPATH=. python3 tools/qa_recruit_mail.py [--shot=path.png]

Kyle, 19 Nov 2026: "I like the bond gates who comes and how often they are to respond. You can still have new
friends who come quickly though. But also getting them to meet at a location of choosing works too."

  1. every recruit bar Asher has all three letters, in voice, and a yes names the town
  2. the bond sets the odds and the pace; a warm, restless newcomer beats a guarded, settled friend for speed, and a
     Sworn recruit always answers
  3. only people you've been out with are listed, and only towns with a mailbox you've been to are offered (none of
     them hidden)
  4. the whole road: a letter, no answer before it's due, then a reply naming your town; they leave home (their spot
     stands empty), don't join in the wrong town, and join in the right one, the party first and then the bench
  5. silence: no letter, and you can't write again until the wait's up
  6. on a break they write "not yet"; after an angry walkout they write "come and see me", and neither waits for you
  7. with the party and the bench full they keep waiting, and say so once
  8. too far above your level to come: listed, but you can't write
  9. walking up and hiring them in person clears the letter
 10. the invite and the towns survive a save and load
 11. the Friends tab draws, with someone picked and a town offered
 12. a windrider flight takes time by distance (Kyle: "make wind riders pass time as it takes time to fly... to help
     recruit people"): half an hour next door, longer the further you go, never a hearth's eight, and an answer due
     in the air arrives, with the recruit joining as you land in their town
"""
import contextlib
import io
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)
    return ok


class Z:
    def __init__(self, name, town=True):
        self.name, self.is_town = name, town


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    with contextlib.redirect_stdout(io.StringIO()):
        from entities.character import Character
        from entities.party import Party
        from world import recruit_mail as RM
        from world.bond_manager import STAGES, get_bond_manager
        from world.mail import Mailbox
        from world.recruit_manager import get_recruit_manager, reset_recruit_manager
        from tools.build_tempest_quests import voice_problems

    # 1
    bm = get_bond_manager()
    for rid in bm.bonds:
        for k in ("mail_yes", "mail_later", "mail_see_me"):
            t = bm.line(rid, k)
            if not check(bool(t) and t != k, f"{rid}: no {k} letter"):
                continue
            check(not voice_problems(t), f"{rid} {k}: {voice_problems(t)}")
            check(("{town}" in t) == (k == "mail_yes"), f"{rid} {k}: the town token is wrong: {t!r}")
            check("{" not in t.replace("{town}", ""), f"{rid} {k}: a stray token: {t!r}")
    check("asher_coleman" not in bm.bonds, "Asher has letters")

    # 2
    b = bm.bonds["cristobal_knight"]
    g = bm.bonds["eino_barbarian"]
    keep = (b.stage, g.stage)
    b.stage, g.stage = 0, STAGES.index("friend")
    check(RM.reply_hours(b) < RM.reply_hours(g),
          f"a warm newcomer ({RM.reply_hours(b):.1f}h) isn't quicker than a guarded friend ({RM.reply_hours(g):.1f}h)")
    for x in (b, g):
        odds = []
        for st in range(5):
            x.stage = st
            odds.append(RM.chance(x))
        check(odds == sorted(odds), f"{x.rid}: the odds don't rise with the bond {odds}")
        check(odds[-1] == 1.0, f"{x.rid}: a Sworn recruit doesn't always answer")
        hrs = []
        for st in range(5):
            x.stage = st
            hrs.append(RM.reply_hours(x))
        check(hrs == sorted(hrs, reverse=True), f"{x.rid}: answers don't come sooner as the bond grows {hrs}")
        check(all(RM.MIN_HOURS <= h <= RM.MAX_HOURS for h in hrs), f"{x.rid}: a reply time out of range {hrs}")
    b.stage, g.stage = keep

    def fresh(level=60):
        with contextlib.redirect_stdout(io.StringIO()):
            rm = reset_recruit_manager()
            import world.bond_manager as BM
            BM._bond_manager = None
            bm = get_bond_manager()
            party = Party(Character(name="Hero", char_class="Warrior", level=level))
        bm.party = party
        return rm, bm, party

    def hire(rm, bm, party, rid):
        with contextlib.redirect_stdout(io.StringIO()):
            ch = rm.build_or_restore(rm.recruits[rid], party.player.level)
            party.add_member(ch)
            rm.mark_recruited(rid)
        bm.on_joined(rid)
        return ch

    def send_home(rm, bm, party, ch):
        party.remove_member(ch)
        rm.dismiss(ch)
        bm.bonds[ch.recruit_id].in_party = False

    def here(party, rid):
        return [p for p in list(party.members) + list(party.bench) if getattr(p, "recruit_id", None) == rid]

    # 3
    rm, bm, party = fresh()
    R = "cristobal_knight"
    ch = hire(rm, bm, party, R)
    check(not [f for f, _r in RM.friends(bm, rm, party) if f.rid == R], "somebody in the party is listed as a friend")
    send_home(rm, bm, party, ch)
    listed = [f.rid for f, _r in RM.friends(bm, rm, party)]
    check(listed == [R], f"the Friends list should be just the one you've had out, got {listed}")
    RM.note_town(bm, Z("Orgrimmar"))
    RM.note_town(bm, Z("Valley of Trials"))           # no mailbox
    RM.note_town(bm, Z("Freewind Post"))
    towns = RM.meeting_towns(bm)
    check([k for k, _n in towns] == ["freewind_post", "orgrimmar"], f"meeting towns {towns}")
    for _k, n in towns:
        check(not RM._hidden(n), "a hidden zone is offered as a meeting place")
    try:
        from world.hidden_zones import registry
        for name in list(registry())[:50]:
            RM.note_town(bm, Z(name))
        check(all(not RM._hidden(n) for _k, n in RM.meeting_towns(bm)), "a hidden zone was recorded as a town")
    except Exception:
        pass

    # 4
    mail = Mailbox()
    b = bm.bonds[R]
    rng = random.Random(1)
    b.stage = STAGES.index("friend")
    home = rm.recruits[R].home_location() if rm.recruits[R].has_home() else (rm.recruits[R].zone, 0, 0)
    ok, msg = RM.invite(bm, b, "freewind_post", 100.0, rng)
    check(ok and b.invite and b.invite["state"] == "sent", f"the letter wasn't posted ({msg})")
    _line, can = RM.status(bm, rm, b, rm.recruits[R], 100.0, 60)
    check(not can, "you can write twice while the first letter is on its way")
    due = b.invite["due"]
    RM.process(due - 0.01, party, mail, zone=Z("Freewind Post"))
    check(not mail.letters and b.invite["state"] == "sent", "an answer came before it was due")
    RM.process(due, party, mail, zone=Z("Orgrimmar"))
    got = [x for x in mail.letters if x.sender == rm.recruits[R].name]
    if check(len(got) == 1, f"{len(got)} replies came"):
        check("Freewind Post" in got[0].body and "{town}" not in got[0].body,
              f"the reply doesn't name the town: {got[0].body!r}")
    check(b.invite and b.invite["state"] == "waiting", "they didn't set off after saying yes")
    check(R not in [r.recruit_id for r in rm.get_recruits_in_zone(home[0])], "they're still standing at home")
    check(not here(party, R), "they joined in the wrong town")
    joined = RM.meet(party, Z("Freewind Post"))
    check(joined and joined[0][1] == "active" and here(party, R), f"they didn't join at the meeting place ({joined})")
    check(b.invite is None and b.in_party, "the letter is still open after they joined")

    # 5
    rm, bm, party = fresh()
    ch = hire(rm, bm, party, R)
    send_home(rm, bm, party, ch)
    RM.note_town(bm, Z("Orgrimmar"))
    b = bm.bonds[R]

    class Never:
        def random(self):
            return 0.999
    RM.invite(bm, b, "orgrimmar", 0.0, Never()) if RM.chance(b) < 0.999 else None
    if b.invite:
        mail = Mailbox()
        RM.process(b.invite["due"], party, mail, zone=Z("Orgrimmar"))
        check(not mail.letters and b.invite["state"] == "silent", "a recruit who shouldn't answer wrote back")
        line, can = RM.status(bm, rm, b, rm.recruits[R], b.invite["due"] + 1, 60)
        check(not can and "try again" in line, f"silence: {line!r}")
        line, can = RM.status(bm, rm, b, rm.recruits[R], b.invite["retry_at"] + 0.01, 60)
        check(can, f"you can't write again after the wait ({line!r})")

    # 6
    for flag, key in (("away", "mail_later"), ("needs_talk", "mail_see_me")):
        rm, bm, party = fresh()
        ch = hire(rm, bm, party, R)
        send_home(rm, bm, party, ch)
        RM.note_town(bm, Z("Orgrimmar"))
        b = bm.bonds[R]
        b.stage = STAGES.index("sworn")
        setattr(b, flag, True)
        mail = Mailbox()
        RM.invite(bm, b, "orgrimmar", 0.0, random.Random(2))
        RM.process(b.invite["due"], party, mail, zone=Z("Orgrimmar"))
        check(len(mail.letters) == 1 and mail.letters[0].body == bm.line(R, key), f"{flag}: the wrong letter came")
        check(b.invite is None and not here(party, R), f"{flag}: they came anyway, or the letter is still open")

    # 7
    rm, bm, party = fresh()
    ch = hire(rm, bm, party, R)
    send_home(rm, bm, party, ch)
    for rid in [x for x in bm.bonds if x != R][:6]:
        hire(rm, bm, party, rid)
    check(party.is_full() and party.bench_full(), "rig: the party and bench aren't full")
    RM.note_town(bm, Z("Orgrimmar"))
    b = bm.bonds[R]
    b.stage = STAGES.index("sworn")
    RM.invite(bm, b, "orgrimmar", 0.0, random.Random(3))
    RM.process(b.invite["due"], party, Mailbox(), zone=Z("Orgrimmar"))
    RM.meet(party, Z("Orgrimmar"))
    check(b.invite and b.invite["state"] == "waiting" and not here(party, R), "no room, and they joined anyway")
    told = [t for _r, t in bm.log if "no room" in t]
    check(len(told) == 1, f"no room should be said once, was said {len(told)} times")

    # 8
    rm, bm, party = fresh(level=60)
    ch = hire(rm, bm, party, R)
    send_home(rm, bm, party, ch)
    party.player.level = 5
    line, can = RM.status(bm, rm, bm.bonds[R], rm.recruits[R], 0.0, 5)
    check(not can and "too far" in line, f"a recruit far above you can be written to ({line!r})")

    # 9
    rm, bm, party = fresh()
    ch = hire(rm, bm, party, R)
    send_home(rm, bm, party, ch)
    RM.note_town(bm, Z("Orgrimmar"))
    RM.invite(bm, bm.bonds[R], "orgrimmar", 0.0, random.Random(4))
    hire(rm, bm, party, R)
    check(bm.bonds[R].invite is None, "hiring them in person left the letter open")

    # 10
    rm, bm, party = fresh()
    ch = hire(rm, bm, party, R)
    send_home(rm, bm, party, ch)
    RM.note_town(bm, Z("Orgrimmar"))
    RM.invite(bm, bm.bonds[R], "orgrimmar", 7.0, random.Random(5))
    saved = bm.to_dict()
    inv = dict(bm.bonds[R].invite)
    import world.bond_manager as BM
    BM._bond_manager = None
    bm2 = get_bond_manager()
    bm2.load_state(saved)
    check(bm2.bonds[R].invite == inv, "the letter didn't survive a save")
    check(bm2.towns.get("orgrimmar") == "Orgrimmar", "the towns didn't survive a save")

    # 12
    from world.travel_manager import TravelManager, travel_data
    nodes = travel_data()["flight_nodes"]
    pairs = []
    for a in nodes:
        for b2 in nodes:
            if a < b2 and TravelManager.can_fly_between(a, b2):
                pa, pb = nodes[a]["pos"], nodes[b2]["pos"]
                pairs.append((((pa[0] - pb[0]) ** 2 + (pa[1] - pb[1]) ** 2) ** 0.5, TravelManager.flight_hours(a, b2)))
    pairs.sort()
    hrs = [h for _d, h in pairs]
    check(hrs == sorted(hrs), "a longer flight takes less time than a shorter one")
    check(hrs[0] == 0.5 and hrs[-1] < 8.0, f"flights run {hrs[0]} to {hrs[-1]} hours, want half an hour up to under eight")
    rm, bm, party = fresh()
    ch = hire(rm, bm, party, R)
    send_home(rm, bm, party, ch)
    RM.note_town(bm, Z("Orgrimmar"))
    b = bm.bonds[R]
    b.stage = STAGES.index("sworn")
    from world.market import market as MK
    m = MK.market_of(party)

    class ZM:
        current_zone = Z("Orgrimmar")
    MK._LIVE["zone_manager"] = ZM()
    RM.invite(bm, b, "orgrimmar", m.clock, random.Random(6))
    MK.on_flight(party, b.invite["due"] - m.clock + 0.01)
    check(here(party, R), "a recruit whose answer came in the air didn't meet you as you landed")
    MK._LIVE["zone_manager"] = None

    # 11
    shot = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--shot=")), None)
    try:
        draw_tab(bm2, rm, party, shot)
    except Exception as e:
        import traceback
        traceback.print_exc()
        check(False, f"the Friends tab didn't draw: {e}")

    for x in bad:
        print("  -", x)
    if bad:
        print(f"Recruit mail: {len(bad)} problems")
        sys.exit(1)
    print("Recruit mail OK - letters in every voice, odds and pace from the bond, meeting at the town you pick, "
          "and the tab draws.")


def draw_tab(bm, rm, party, shot):
    import pygame
    from config import SCREEN_HEIGHT, SCREEN_WIDTH
    from ui.screens.mail_screen import MailScreen
    from world.market.market import market_of

    class SM:
        player = party.player
        zone_manager = None
        icon_ui_helper = None

        def get_party(self):
            return party
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    ms = MailScreen(SM())
    market_of(party)
    for rid in list(bm.bonds)[:9]:
        if rid in rm.recruits and not [p for p in party.members + party.bench if getattr(p, "recruit_id", None) == rid]:
            bm.bonds[rid].stints = max(1, bm.bonds[rid].stints)
    bm.towns.update({"freewind_post": "Freewind Post", "orgrimmar": "Orgrimmar"})
    ms.tab = "friends"
    from world import recruit_mail as RM
    people = RM.friends(bm, rm, party)
    check(len(people) >= 2, f"the tab has {len(people)} friends to show")
    if people:
        ms.friend_id = people[0][0].rid
    ms.render(screen)
    if shot:
        pygame.image.save(screen, shot)


if __name__ == "__main__":
    main()
