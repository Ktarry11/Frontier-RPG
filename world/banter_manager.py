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
#: 150 was right when every eligible trigger fired; with TRIGGER_CHANCE gating on top of it the two
#: compounded and a measured 45-minute session produced five beats with a 28-minute silence in the
#: middle. That is not restraint, that is an empty party. 75 lets the chance table do the shaping.
BEAT_COOLDOWN = 75.0

#: And the same person should not be the voice of the party. Once someone speaks they go to the back
#: of the queue; this is how many OTHER speakers have to go before they come up again.
SPEAKER_COOLDOWN = 3

#: Chance a second companion answers. Not every beat is a conversation - a line that lands and then
#: silence is better than a guaranteed call-and-response, which is how banter starts sounding like a
#: sitcom.
REPLY_CHANCE = 0.45

#: How often a trigger actually gets a remark, once the cooldown has passed. Kyle, 30 Oct 2026:
#: "the characters don't always need to chat 24/7. But I don't want life to be boring."
#:
#: Without this the feature is CLOCKWORK: the cooldown elapses and then the very next event, always,
#: produces a line. Walk into four towns and you get four comments, evenly spaced, forever. That
#: reads as a system rather than as people.
#:
#: So the big moments nearly always land and the routine ones often pass in silence. You cleared a
#: dungeon or somebody nearly died - somebody says something. You walked into another town - maybe
#: not, and the silence is what makes the next remark worth hearing.
TRIGGER_CHANCE = {
    "dungeon_clear": 0.85,
    "close_call": 0.75,
    "boss_down": 0.50,
    "town_arrive": 0.55,
    "zone_arrive": 0.40,
}

#: Lines the player has heard lately, by text. A four-person party only has two or three lines for a
#: given trigger, so without this you hear the same sentence on your third town and the party stops
#: feeling alive - repetition is a far worse kind of boring than silence. Keeping the recent texts
#: out of the running makes a small pool feel several times larger.
LINE_MEMORY = 14


class BanterLine:
    """One authored line: who says it, what sets it off, and whether it answers or opens."""

    def __init__(self, recruit_id, trigger, text, kind="open", zone=None, topic=None):
        self.recruit_id = recruit_id
        self.trigger = trigger
        self.text = text
        self.kind = kind          # "open" starts a beat, "reply" answers one
        self.zone = zone          # optional: only in this zone
        #: Optional shared EARTH subject - "cities", "night_work", "the_cold". A reply carrying the
        #: same topic as the opener answers what was actually said instead of changing the subject.
        #: Kyle, 29 Oct 2026: "it'd be cool if Tarek mentions back home and kouroush mentions his
        #: time in egypt. Players are integrated from earth, all players are."
        #:
        #: This is how two strangers can have a real exchange without breaking the independence
        #: rule. They did not meet before and they have no history HERE - what they share is a
        #: planet. So a topical reply answers the SUBJECT and never names or addresses the speaker,
        #: which keeps qa_banter's no-naming check intact while making the beat feel pairwise.
        #:
        #: It stays linear, too. Topics are authored per character, not per pair: 44 companions is
        #: 946 pairs and Kyle has said 50+, so anything quadratic was dead before it started.
        self.topic = topic


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
        self.recent_lines = []
        self.current = None
        self.since_last_beat = BEAT_COOLDOWN   # so the first real event can speak
        self._load()

    def _load(self):
        try:
            raw = json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        for recruit_id, blocks in (raw.get("lines") or {}).items():
            for trigger, entries in blocks.items():
                for e in entries:
                    if isinstance(e, str):
                        e = {"text": e}
                    line = BanterLine(recruit_id, trigger, e["text"],
                                      e.get("kind", "open"), e.get("zone"), e.get("topic"))
                    self.by_trigger.setdefault(trigger, []).append(line)

    # ---------------------------------------------------------------- firing
    def update(self, dt):
        self.since_last_beat += dt
        if self.current and not self.current.update(dt):
            self.current = None

    def _eligible(self, trigger, party_ids, kind, zone=None, exclude=(), topic=None):
        out = []
        for line in self.by_trigger.get(trigger, []):
            if line.kind != kind or line.recruit_id not in party_ids:
                continue
            if line.recruit_id in exclude:
                continue
            if line.zone and zone and line.zone != zone:
                continue
            if topic is not None and line.topic != topic:
                continue
            out.append(line)
        return out

    def _unheard(self, lines):
        """Drop lines the player has heard lately, unless that leaves nothing."""
        fresh = [x for x in lines if x.text not in self.recent_lines]
        return fresh or lines

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
        if not force and random.random() > TRIGGER_CHANCE.get(trigger, 0.5):
            # Stay quiet AND keep the cooldown running, so a skipped moment does not bank up into a
            # burst of three remarks the moment the dice finally land.
            return None
        members = [m for m in (party.members if party else []) if getattr(m, "recruit_id", None)]
        if not members:
            return None
        by_id = {m.recruit_id: m for m in members}

        openers = self._unheard(self._eligible(trigger, set(by_id), "open", zone))
        if not openers:
            return None
        first = self._pick_speaker(openers)
        if first is None:
            return None
        beat = [(first.recruit_id, by_id[first.recruit_id].name, first.text)]

        if len(by_id) > 1:
            # A TOPICAL answer is the good case and is not left to the generic coin flip. When the
            # opener raised a shared Earth subject and somebody else in the party has a line on that
            # same subject, take it - that is the exchange Kyle asked for, and it is rare enough
            # already without a 45% gate on top of needing two matching lines in one party.
            second = None
            if first.topic:
                same = self._eligible(trigger, set(by_id), "reply", zone,
                                      exclude=(first.recruit_id,), topic=first.topic)
                if same:
                    second = self._pick_speaker(self._unheard(same))
            if second is None and random.random() < REPLY_CHANCE:
                replies = self._eligible(trigger, set(by_id), "reply", zone,
                                         exclude=(first.recruit_id,))
                # An untopiced opener should not be answered by a line written to follow a specific
                # subject - that is how you get a reply about Cairo after a remark about the weather.
                replies = [r for r in replies if r.topic is None]
                if replies:
                    second = self._pick_speaker(self._unheard(replies))
            if second is not None:
                beat.append((second.recruit_id, by_id[second.recruit_id].name, second.text))

        for rid, _, txt in beat:
            self.recent_speakers.append(rid)
            self.recent_lines.append(txt)
        self.recent_speakers = self.recent_speakers[-12:]
        self.recent_lines = self.recent_lines[-LINE_MEMORY:]
        self.since_last_beat = 0.0
        self.current = BanterBeat(beat)
        return self.current

    def say(self, recruit_id, speaker_name, text, hold=6.0):
        """Put ONE scripted line in the banter panel, bypassing every gate above.

        fire() is deliberately a lottery - cooldown, per-trigger chance, "has this
        been heard" - because ambient chatter has to stay quiet most of the time.
        A scripted beat is the opposite: it is a specific character saying a
        specific thing at a specific moment (Asher refusing to leave the Coven),
        and a 45% coin flip deciding whether the player is told why their
        companion just vanished is not ambience, it is a bug. Does not touch
        recent_lines/recent_speakers either, so a scripted line never uses up a
        slot in the "don't repeat yourself" memory that ambient banter needs.
        """
        self.current = BanterBeat([(recruit_id, speaker_name, text)], hold=hold)
        self.since_last_beat = 0.0
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
