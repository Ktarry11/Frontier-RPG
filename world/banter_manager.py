"""
Party banter - companions saying things when something happens.

Kyle, 2026-10-28: "let's try to actually start the ability for party banter in towns if possible. We
have character portraits so it'll be fine... Players are real and need distinct personalities. We will
only have 24 now but eventually 50+ and each character has unique personality. Party banter maybe after
Dungeons, or if something goes on."

THE N-SQUARED TRAP, AND WHY THIS IS NOT PAIRWISE
------------------------------------------------
The obvious way to write banter is per PAIR: a line for Dan-and-Ama, another for Dan-and-Silas. That is
how most games do it and it is why most games ship banter for six companions and then stop. Twenty-four
characters is 276 pairs. Fifty is 1,225. Kyle has said 50+, so pairwise was dead before it started.

So lines are authored PER CHARACTER PER TRIGGER, which is linear. A beat is: something happens, one
companion says their own line about it, and sometimes a second companion answers with a line from their
OWN pool. Nobody's line is written for a specific partner.

THAT IS ALSO WHAT KEEPS THE LORE HONEST. Kyle, the same morning: "These people are all independent and
don't know each other." A line that says "Dan was right about the scaffolding" assumes Dan is here, that
they have met, and that there is a shared history. None of that is true. These are strangers who happen
to have been picked up by the same person, and the player is the only thing they have in common.

So the hard rule, enforced by tools/qa_banter.py rather than by good intentions:
    A LINE MAY NEVER NAME ANOTHER COMPANION, and may never imply a shared past with one.
A line talks about the EVENT, about the speaker's own life, or to the player. Two strangers reacting to
the same dungeon is a real conversation and a more interesting one than two old friends performing a
rapport they were handed.

WHAT IT COSTS TO ADD A CHARACTER: one block of lines in data/banter/lines.json. No pair tables, no
matrix to backfill, nothing to touch in here.
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).parent.parent / "data" / "banter" / "lines.json"

#: What can start a beat. Kyle named towns and dungeons; the rest are the moments that already exist in
#: the engine and are worth a reaction. Adding one is a key here plus lines in the data file.
TRIGGERS = (
    "town_arrive",      # walked into a town or city
    "dungeon_clear",    # left a dungeon after its boss went down
    "boss_down",        # a boss died
    "close_call",       # somebody survived a fight on almost nothing
    "zone_arrive",      # first time in a zone
)

#: A beat needs breathing room or it becomes wallpaper. Measured in seconds of play, not in events -
#: a player who clears three bosses in four minutes should not get three beats.
BEAT_COOLDOWN = 150.0

#: And the same person should not be the voice of the party. Once someone speaks they go to the back
#: of the queue; this is how many OTHER speakers have to go before they come up again.
SPEAKER_COOLDOWN = 3

#: Chance a second companion answers. Not every beat is a conversation - a line that lands and then
#: silence is better than a guaranteed call-and-response, which is how banter starts sounding like a
#: sitcom.
REPLY_CHANCE = 0.45


class BanterLine:
    """One authored line: who says it, what sets it off, and whether it answers or opens."""

    def __init__(self, recruit_id, trigger, text, kind="open", zone=None):
        self.recruit_id = recruit_id
        self.trigger = trigger
        self.text = text
        self.kind = kind          # "open" starts a beat, "reply" answers one
        self.zone = zone          # optional: only in this zone


class BanterBeat:
    """What the UI draws: one or two lines with portraits, and how long it has left."""

    def __init__(self, lines, hold=6.0):
        self.lines = lines        # [(recruit_id, speaker_name, text)]
        self.remaining = hold + 2.5 * (len(lines) - 1)
        self.revealed = 1         # the reply appears a beat after the opener

    def update(self, dt):
        self.remaining -= dt
        if self.revealed < len(self.lines) and self.remaining < (len(self.lines) - 1) * 2.5 + 2.0:
            self.revealed = len(self.lines)
        return self.remaining > 0


class BanterManager:
    def __init__(self):
        self.by_trigger = {}      # trigger -> [BanterLine]
        self.recent_speakers = []
        self.current = None
        self.since_last_beat = BEAT_COOLDOWN   # so the first real event can speak
        self._load()

    def _load(self):
        try:
            raw = json.loads(DATA.read_text())
        except (OSError, ValueError):
            return
        for recruit_id, blocks in (raw.get("lines") or {}).items():
            for trigger, entries in blocks.items():
                for e in entries:
                    if isinstance(e, str):
                        e = {"text": e}
                    line = BanterLine(recruit_id, trigger, e["text"],
                                      e.get("kind", "open"), e.get("zone"))
                    self.by_trigger.setdefault(trigger, []).append(line)

    # ---------------------------------------------------------------- firing
    def update(self, dt):
        self.since_last_beat += dt
        if self.current and not self.current.update(dt):
            self.current = None

    def _eligible(self, trigger, party_ids, kind, zone=None, exclude=()):
        out = []
        for line in self.by_trigger.get(trigger, []):
            if line.kind != kind or line.recruit_id not in party_ids:
                continue
            if line.recruit_id in exclude:
                continue
            if line.zone and zone and line.zone != zone:
                continue
            out.append(line)
        return out

    def _pick_speaker(self, lines):
        """Prefer whoever has not spoken lately, so the party does not get a narrator.

        Falls back to the full pool when everyone is on cooldown, because with a small party that is
        the normal case and silence would read as the feature being broken. The ONE case it will not
        fall back on is repeating whoever just spoke - caught in testing, where a party in which only
        one member had a zone_arrive line heard that same person say that same sentence twice in a
        row. Returns None there and the beat is dropped; a companion who talks to themselves is worse
        than a quiet walk.
        """
        fresh = [x for x in lines if x.recruit_id not in self.recent_speakers[-SPEAKER_COOLDOWN:]]
        if fresh:
            return random.choice(fresh)
        last = self.recent_speakers[-1] if self.recent_speakers else None
        pool = [x for x in lines if x.recruit_id != last]
        return random.choice(pool) if pool else None

    def fire(self, trigger, party, zone=None, force=False):
        """Try to start a beat. Returns the BanterBeat, or None if nothing was said.

        Most calls return None and that is the design - this is wired to events that happen constantly
        and it has to stay quiet most of the time.
        """
        if self.current is not None:
            return None
        if not force and self.since_last_beat < BEAT_COOLDOWN:
            return None
        members = [m for m in (party.members if party else []) if getattr(m, "recruit_id", None)]
        if not members:
            return None
        by_id = {m.recruit_id: m for m in members}

        openers = self._eligible(trigger, set(by_id), "open", zone)
        if not openers:
            return None
        first = self._pick_speaker(openers)
        if first is None:
            return None
        beat = [(first.recruit_id, by_id[first.recruit_id].name, first.text)]

        if len(by_id) > 1 and random.random() < REPLY_CHANCE:
            replies = self._eligible(trigger, set(by_id), "reply", zone, exclude=(first.recruit_id,))
            if replies:
                second = self._pick_speaker(replies)
                if second is not None:
                    beat.append((second.recruit_id, by_id[second.recruit_id].name, second.text))

        for rid, _, _ in beat:
            self.recent_speakers.append(rid)
        self.recent_speakers = self.recent_speakers[-12:]
        self.since_last_beat = 0.0
        self.current = BanterBeat(beat)
        return self.current

    # ---------------------------------------------------------------- coverage
    def coverage(self):
        """{trigger: {recruit_id: (opens, replies)}} - what tools/qa_banter.py reports on."""
        out = {}
        for trigger, lines in self.by_trigger.items():
            per = {}
            for line in lines:
                o, r = per.get(line.recruit_id, (0, 0))
                per[line.recruit_id] = (o + (line.kind == "open"), r + (line.kind == "reply"))
            out[trigger] = per
        return out


_manager = None


def get_banter_manager():
    global _manager
    if _manager is None:
        _manager = BanterManager()
    return _manager


def reset_banter_manager():
    """Fresh state for a new character, same as the other per-run managers."""
    global _manager
    _manager = BanterManager()
    return _manager
