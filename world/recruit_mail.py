"""Writing to recruits who've gone home: the Friends tab in the mailbox.

Kyle and a friend, 19 Nov 2026: "make a friend list where you can message them to join if you know them". Kyle:
"I like the bond gates who comes and how often they are to respond. You can still have new friends who come
quickly though. But also getting them to meet at a location of choosing works too."

WHO YOU CAN WRITE TO. Anybody who has been out with you at least once (bond.stints > 0) and isn't in the party or on
the bench now. Nobody you haven't met is listed, so the tab never gives away who is out there.

WHETHER THEY ANSWER, AND HOW FAST. The bond stage sets the odds and the pace, and who they are moves both:
  chance  ANSWER[stage] x (0.5 + warmth / 2)  (a Sworn recruit always answers)
  hours   REPLY_HOURS[stage] / (warmth x restless), between 1 and 8 market hours
so a warm, restless newcomer can be on the road within a couple of hours, and a guarded, settled one you've known for
months still takes a while. Personality moves the pace far more than the odds: who answers at all is mostly the bond. Silence is an answer too: the Friends tab says nobody has written back, and you can try again after
RETRY_HOURS.

WHAT THEY SAY. Their own voice, three letters each (tools/wave2/<id>.json, bond.lines):
  mail_yes      they'll meet you at the inn in the town you picked ({town})
  mail_later    they're on a break, and want a few more of your jobs done first
  mail_see_me   they walked out angry, and want to say it to your face, so you go to them

THE MEETING. You pick the town: any town with a mailbox you've been to. Once they've said yes they leave home (their
spot stands empty) and wait at that town's inn. Walk in, or be there when the letter comes, and they join: the
party if there's room, the bench if not. With both full they keep waiting and say so. Nobody is pulled into a
dungeon or a fight, a break still runs its course, and an angry walkout is still settled in person.

Time is the market clock (world/market/market.py), the same one the post runs on.
"""
import json
from pathlib import Path

from world.bond_manager import STAGES

#: chance a letter gets any answer, by stage (stranger .. sworn), before warmth
ANSWER = [0.35, 0.55, 0.75, 0.9, 1.0]
#: market hours before the answer comes, by stage, before warmth and restlessness
REPLY_HOURS = [4.0, 3.5, 3.0, 2.0, 1.0]
MIN_HOURS, MAX_HOURS = 1.0, 8.0
#: market hours after a letter nobody answered before you can write again
RETRY_HOURS = 12.0
SUBJECT = "Come and join me"

_MAIL_TOWNS = None


def mail_towns():
    """zone key -> True for every town with a mailbox (data/npcs/ambient_npcs.json)."""
    global _MAIL_TOWNS
    if _MAIL_TOWNS is None:
        from world.zone_keys import zone_key
        try:
            raw = json.loads((Path(__file__).resolve().parent.parent / "data" / "npcs" / "ambient_npcs.json")
                             .read_text(encoding="utf-8"))
        except (OSError, ValueError):
            raw = {}
        _MAIL_TOWNS = {zone_key(r["zone"]) for r in raw.get("npcs", []) if r.get("is_mailbox") and r.get("zone")}
    return _MAIL_TOWNS


def _key(zone):
    from world.zone_keys import zone_key
    name = zone if isinstance(zone, str) else getattr(zone, "name", "") or ""
    return zone_key(name), name


def _hidden(name):
    try:
        from world.hidden_zones import is_hidden
        return bool(is_hidden(name))
    except Exception:
        return False


# ------------------------------------------------------------------ towns you've been to
def note_town(bonds, zone):
    """Remember a town with a mailbox the party has walked into (offered as a meeting place)."""
    key, name = _key(zone)
    if key in mail_towns() and name and not _hidden(name):
        bonds.towns[key] = name


def meeting_towns(bonds):
    """[(key, display name)] of the towns you can name in a letter, alphabetical."""
    def order(kv):
        n = kv[1].lower()
        return n[4:] if n.startswith("the ") else n
    return sorted(((k, n) for k, n in bonds.towns.items() if k in mail_towns() and not _hidden(n)), key=order)


# ------------------------------------------------------------------ who, and how they'd answer
def chance(b):
    if b.stage >= STAGES.index("sworn"):
        return 1.0
    return max(0.15, min(1.0, ANSWER[b.stage] * (0.5 + b.dial("warmth") / 2.0)))


def reply_hours(b):
    pace = b.dial("warmth") * b.dial("restless")
    return max(MIN_HOURS, min(MAX_HOURS, REPLY_HOURS[b.stage] / max(0.2, pace)))


def friends(bonds, rm, party):
    """Everybody you've been out with who isn't with you now, as (bond, recruit)."""
    here = {getattr(m, "recruit_id", None) for m in list(getattr(party, "members", [])) + list(getattr(party, "bench", []))}
    out = []
    for rid, b in bonds.bonds.items():
        if b.stints <= 0 or rid in here or rid not in rm.recruits:
            continue
        out.append((b, rm.recruits[rid]))
    out.sort(key=lambda br: (-br[0].stage, br[1].name))
    return out


def status(bonds, rm, b, recruit, now, player_level=None):
    """(line for the Friends tab, can you write to them now)."""
    inv = b.invite
    if inv:
        if inv.get("state") == "waiting":
            return f"Waiting for you at the inn in {inv['town_name']}.", False
        if inv.get("state") == "sent":
            return "Your letter is on its way. No answer yet.", False
        if inv.get("state") == "silent" and now < inv.get("retry_at", 0):
            hours = max(1, int(inv["retry_at"] - now + 0.999))
            return f"Hasn't written back. You can try again in about {hours} hours.", False
    block = rm.block_reason(recruit, player_level) if player_level is not None else None
    if block:
        return f"Level {rm.join_level(recruit, player_level)}, too far above you to come yet.", False
    if b.away:
        return f"On a break at home in {b.data.get('home', 'their home')}.", True
    return f"At home in {b.data.get('home', 'their home')}.", True


# ------------------------------------------------------------------ the letter and the answer
def invite(bonds, b, town_key, now, rng):
    """Post the letter. Decides now, quietly, whether and when they'll answer."""
    name = bonds.towns.get(town_key)
    if not name:
        return False, "Pick a town you've been to."
    answers = rng.random() < chance(b)
    b.invite = {"state": "sent", "town": town_key, "town_name": name, "sent_at": now,
                "due": now + reply_hours(b), "answers": bool(answers)}
    return True, f"Posted to {bonds.name_of(b.rid).split()[0]}. Answers come by mail."


def _reply_kind(b):
    if b.needs_talk:
        return "mail_see_me"
    if b.away:
        return "mail_later"
    return "mail_yes"


def process(now, party, mail, zone=None, rng=None):
    """Run every letter whose answer is due, then let anyone waiting where you are join. Returns the joiners."""
    from world.bond_manager import get_bond_manager
    from world.mail import Letter
    bonds = get_bond_manager()
    for b in bonds.bonds.values():
        inv = b.invite
        if not inv or inv.get("state") != "sent" or now < inv.get("due", 0):
            continue
        if not inv.get("answers"):
            inv["state"] = "silent"
            inv["retry_at"] = inv["due"] + RETRY_HOURS
            continue
        kind = _reply_kind(b)
        text = bonds.line(b.rid, kind).replace("{town}", inv["town_name"])
        if mail is not None:
            mail.deliver(Letter(bonds.name_of(b.rid), "Re: " + SUBJECT, body=text, kind="letter",
                                sent_at=inv["due"], sender_kind="recruit"))
        if kind == "mail_yes":
            inv["state"] = "waiting"
        else:
            b.invite = None             # on a break, or wants you in person: nothing more to wait for
    return meet(party, zone)


def meet(party, zone):
    """Anyone waiting in this town joins now. Returns [(name, "active"|"bench")], and leaves anyone there's no room
    for waiting (with one word to say so)."""
    if party is None or zone is None:
        return []
    from world.bond_manager import get_bond_manager
    from world.recruit_manager import get_recruit_manager
    key, _name = _key(zone)
    bonds, rm = get_bond_manager(), get_recruit_manager()
    joined = []
    for b in list(bonds.bonds.values()):
        inv = b.invite
        if not inv or inv.get("state") != "waiting" or inv.get("town") != key:
            continue
        recruit = rm.recruits.get(b.rid)
        if recruit is None:
            b.invite = None
            continue
        if party.is_full() and party.bench_full():
            if not inv.get("told_full"):
                inv["told_full"] = True
                bonds._notify(f"{recruit.name} is waiting at the inn, but there's no room in the party or on the bench.")
            continue
        level = getattr(getattr(party, "player", None), "level", None)
        character = rm.build_or_restore(recruit, level)
        placement = party.add_member(character)
        if placement is None:
            continue
        rm.mark_recruited(b.rid)
        b.invite = None
        bonds.on_joined(b.rid)
        where = "joins the party" if placement == "active" else "waits on the bench"
        bonds._notify(f"{recruit.name} meets you at the inn and {where}.")
        joined.append((recruit.name, placement))
    return joined


def away_from_home(rid):
    """True while a recruit has left home to meet you, so their spot stands empty."""
    from world.bond_manager import get_bond_manager
    b = get_bond_manager().bonds.get(rid)
    return bool(b is not None and b.invite and b.invite.get("state") == "waiting")
