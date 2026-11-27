"""Wave 3: the recruits get to know each other.

Kyle, 19 Nov 2026, on the four open calls: neighbours start on nodding terms (yes); once they're
friendly a line may use the other one's first name (yes); no romance between recruits; rivals never
refuse to share a party. And: "I'd like more complex interactions that you can manage. Don't skimp
out, this is very important."

Text: data/npcs/relationships.json, written by tools/build_relationships.py from tools/wave3/.
Hooked in by world/bond_manager.py, which owns one of these and saves it with the bonds.

HOW TWO RECRUITS GET ON
  affinity   one number per pair, -100 to 100, the same from both sides.
  chemistry  what each outing together does to it. Worked out once from the two people's traits:
             how they talk, what makes them laugh, how they handle people, how they take risks,
             what each of them likes and can't stand in other people, what they have in common
             from Earth, and anyone their profile says they'd warm to or grate on.
  familiarity  time together wears the edges off. Each shared outing adds a little more, so a
             pair who grate at first can come round if they keep travelling together, and a pair
             whose chemistry is really bad never quite do.
  events     a wipe together, a healer dragging you back from almost nothing, the player handing
             one of them the other's gear, and what they say to each other when they talk.

STATES (with a little slack either side so they don't flicker)
  strangers -> nodding (met) -> friendly (20) -> close friends (55)
                          \\-> grating (-20) -> rivals (-50)
  Neighbours (the same home in bonds.json) start at nodding.

WHAT THEY SAY
  Every recruit has their own pool of lines, one file each in tools/wave3/. A beat is two to four
  lines from two or three people's pools, picked by the pair's state and by the other person's
  traits: a joker teased about being quiet teases back, a formal one bristles and the teaser either
  apologises or digs in; a gentle one needled after a wipe goes quiet, and a friend of theirs in the
  party tells the needler to leave it. Then there are the one-off moments: meeting, finding out you
  both worked nights, becoming friends, falling out, making up, and the hand-written arcs for the
  pairs whose profiles name each other (signature pairs).

  A line may use {name} (the other person's first name) only in the keys listed in NAMED below,
  which are the ones that can only happen once they're friendly. Nothing else names anybody.

EFFECTS
  Mood only, through the bond: friends along lift it, rivals along wear it down. No refusals and
  nothing in combat.
"""
import json
import math
import random
import re
import zlib
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "npcs" / "relationships.json"

FRIENDLY, CLOSE, GRATING, RIVALS = 20, 55, -20, -50
ADDRESS = re.compile(r"\{([^{}|]+)\|([^{}|]+)\}")
#: the slack: once in a state you stay until affinity crosses back past these
LEAVE = {"friendly": 15, "close": 48, "grating": -14, "rivals": -42}
STATE_NAMES = {"strangers": "Strangers", "nodding": "On nodding terms", "friendly": "Friendly",
               "close": "Close friends", "grating": "Grating", "rivals": "Rivals"}
GOOD = ("friendly", "close")
#: pair lines that carry what a recruit keeps from the player until Friend, and the stage they wait for (see _beat)
PRIVATE_KEYS = frozenset({"confide", "turn_friends"})
PRIVATE_STAGE = 3
BAD = ("grating", "rivals")
NEIGHBOUR_START = 6

#: chance of one ordinary conversation at the end of an outing, and at a town rest
AMBIENT_CHANCE = 0.30   # 0.55 until 26 Nov 2026 (talk should feel special)
REST_CHANCE = 0.20      # 0.30 until 26 Nov 2026
#: chance a shared bit of Earth comes up, per outing, for a pair that hasn't found it yet
TAG_CHANCE = 0.20       # 0.35 until 26 Nov 2026
#: seconds after the last beat before a queued relationship beat is shown
#: seconds of play between two party scenes. 12 until 26 Nov 2026, when Kyle: "Should also not talk as much. Talking
#: should be something that should feel special, not being spammed every 2 seconds."
GAP = 150.0
#: beats waiting longer than this many outings are dropped; nobody wants an old conversation
STALE = 2

#: the keys that can only happen between friends, so {name} is allowed in them
NAMED = {"tease_quiet", "tease_talker", "tease_careful", "tease_bold", "tease_any", "tease_back",
         "take_it_kindly", "bristle", "look_out", "accept", "deflect", "confide", "listen",
         "check_in", "worry", "turn_friendly", "turn_friends", "make_up", "defend", "friend_left",
         "friend_back"}
#: everything a recruit's pool should have; common_<tag> comes on top, one per tag they carry
KEYS = ("meet", "meet_neighbour", "ask_home", "ask_work", "answer_home", "answer_work",
        "chat_food", "chat_sleep", "chat_missing", "chat_here",
        "tease_quiet", "tease_talker", "tease_careful", "tease_bold", "tease_any",
        "tease_back", "take_it_kindly", "bristle",
        "needle_quiet", "needle_talker", "needle_careful", "needle_bold", "needle_any",
        "bite_back", "hurt", "laugh_off", "apologise", "double_down",
        "confide", "listen", "look_out", "accept", "deflect", "check_in", "blame",
        "thank", "brush_off", "worry", "handed_down", "hand_fine", "hand_sulk",
        "turn_friendly", "turn_friends", "turn_grating", "turn_rivals", "make_up",
        "defend", "friend_left", "friend_back")
CHAT_TOPICS = ("food", "sleep", "missing", "here")

# ---------------------------------------------------------------- chemistry (tunable)
HUMOUR = {("joker", "joker"): 3, ("dry", "dry"): 2, ("dry", "joker"): 1, ("earnest", "earnest"): 1,
          ("earnest", "joker"): -1}
PACE = {("bold", "careful"): -2, ("careful", "careful"): 1, ("bold", "bold"): 1}
MANNER = {("blunt", "blunt"): 1, ("blunt", "gentle"): -1, ("formal", "formal"): 1,
          ("blunt", "formal"): -1}
TALK = {("quiet", "talker"): -1.5, ("talker", "talker"): 1, ("quiet", "quiet"): 1}
LIKE, LIKE_CAP = 2.0, 4.0
DISLIKE, DISLIKE_CAP = -2.5, -5.0
TAG, TAG_CAP = 1.5, 4.5
WARM, WARY, SPAR = 3.0, -3.0, 2.0
FORMAL_JOKER = -1.0
EASYGOING = 0.5
#: an ordinary conversation won't reuse a line any of the party has said in the last few beats
RECENT = 10
#: how many line ids a pair remembers hearing (about 40 exchanges)
HEARD = 80


def _hid(rid, text):
    """A short id for one line, for a pair's memory of what's been said (saves stay small)."""
    return f"{rid}:{zlib.crc32(text.encode('utf-8')):08x}"


def _pair(table, a, b):
    return table.get(tuple(sorted((a, b))), 0)


def described(t):
    """What other people notice about someone: their explicit descriptors plus the ones their
    traits give them (a talker is loud, a bold one is reckless, and so on)."""
    out = set(t.get("is", []))
    out |= {"loud"} if t.get("talk") == "talker" else {"quiet"} if t.get("talk") == "quiet" else set()
    out |= {"careful"} if t.get("pace") == "careful" else {"reckless"} if t.get("pace") == "bold" else set()
    out |= {"funny"} if t.get("humour") == "joker" else {t.get("humour")} if t.get("humour") else set()
    if t.get("manner"):
        out.add(t["manner"])
    return out


def chemistry_parts(ta, tb, a, b):
    """(lasting, fading). What they like about each other lasts; what grates wears off as they
    get used to each other (fade below), so a pair who rub each other up the wrong way at first can
    come round, the way Adrián's profile says he does with careless people who try."""
    lasting, fading = 0.0, 0.0

    def add(v):
        nonlocal lasting, fading
        if v >= 0:
            lasting += v
        else:
            fading += v
    add(_pair(HUMOUR, ta.get("humour"), tb.get("humour")))
    add(_pair(PACE, ta.get("pace"), tb.get("pace")))
    add(_pair(MANNER, ta.get("manner"), tb.get("manner")))
    add(_pair(TALK, ta.get("talk"), tb.get("talk")))
    if {ta.get("manner"), tb.get("humour")} == {"formal", "joker"} \
            or {tb.get("manner"), ta.get("humour")} == {"formal", "joker"}:
        add(FORMAL_JOKER)
    for x, y in ((ta, tb), (tb, ta)):
        seen = described(y)
        add(min(LIKE_CAP, LIKE * len(seen & set(x.get("likes", [])))))
        add(max(DISLIKE_CAP, DISLIKE * len(seen & set(x.get("dislikes", [])))))
    add(min(TAG_CAP, TAG * len(set(ta.get("tags", [])) & set(tb.get("tags", [])))))
    for x, other in ((ta, b), (tb, a)):
        if other in x.get("warm_to", []):
            add(WARM)
        if other in x.get("wary_of", []):
            add(WARY)
        if other in x.get("spar", []):
            add(SPAR)
    if "easygoing" in ta.get("is", []) or "easygoing" in tb.get("is", []):
        fading *= EASYGOING     # "gets on with nearly everyone": the rough edges matter half as much
    return lasting, fading


def chemistry(ta, tb, a, b):
    """How their first outings together tend to go. Positive pulls them together."""
    return sum(chemistry_parts(ta, tb, a, b))


def fade(outings):
    """How much the things that grate still matter after this many outings together."""
    return max(0.25, 1.0 - outings / 50.0)


#: how hard chemistry pulls each outing. With the median pair (chemistry about 2) that's friendly
#: after twenty-odd outings together and close friends after sixty; a pair the profiles say would
#: click (10 and up) are friends inside one long stint, and a pair who clash (-6) are grating
#: in about ten and rivals by thirty unless something happens between them.
PULL = 0.3


def familiarity(outings):
    """Time together wears the edges off: a little at first, more the longer they've travelled."""
    return 0.1 + min(0.8, outings * 0.02)


#: Where a pair SETTLES (Kyle, 27 Nov 2026: "Right now everyone is just super friendly all the time" / "not
#: everyone will love each other, respect and dislike, absolutely. but not every group is another found family").
#: Until then affinity climbed every outing, so 88% of pairs were close friends by eighty outings. Now each pair
#: drifts toward its own ceiling, set by its chemistry, a little familiarity, and what's happened between them
#: (Rel.memory), and the ceiling flattens out at the ends so nobody runs off to +100 or -100. What grates is loud at
#: first and softens over about a hundred outings, never to nothing. Over every pair of the 113 (tools/sim in
#: claude/group_scenes_design.md), before wipes, saves and group scenes move them:
#:   20 outings: about 9% rivals, 16% grating, 37% nodding, 33% friendly, 5% close
#:   80 outings: about 1% rivals, 7% grating, 32% nodding, 37% friendly, 23% close
SETTLE_LIKE = 6.0       # what they like in each other, per point of chemistry
SETTLE_CLASH = 12.0     # what grates, per point; it softens with time but never below FADE_FLOOR
SETTLE_OFFSET = 6.0     # travelling together isn't the same as liking each other
FAMILIAR_CAP = 8.0      # the most that time alone ever adds
FAMILIAR_RATE = 0.15    # per outing, up to the cap
FADE_FLOOR = 0.25
FADE_OUTINGS = 100.0
SETTLE_CAP = 85.0       # the ceiling flattens toward this (tanh), so it's a ceiling and not a runaway
SETTLE_SOFT = 45.0
SETTLE_RATE = 0.07      # the share of the gap to its ceiling a pair closes per outing
MEMORY = 0.4            # how much of a real event's push stays in where they settle
MEMORY_MIN = 2.0        # small talk (a chat, a question) warms the moment and fades; only bigger things stick


def settle_target(lasting, fading, outings, memory=0.0):
    fd = max(FADE_FLOOR, 1.0 - outings / FADE_OUTINGS)
    raw = (lasting * SETTLE_LIKE + fading * fd * SETTLE_CLASH - SETTLE_OFFSET
           + min(FAMILIAR_CAP, FAMILIAR_RATE * outings))
    return SETTLE_CAP * math.tanh(raw / SETTLE_SOFT) + memory


def next_state(old, a):
    """Where a pair stands at affinity a, given where they stood. Each state holds on a little past
    the line that got them into it, so one bad day doesn't undo a friendship."""
    if a <= RIVALS or (old == "rivals" and a <= LEAVE["rivals"]):
        return "rivals"
    if a <= GRATING or (old in BAD and a <= LEAVE["grating"]):
        return "grating"
    if a >= CLOSE or (old == "close" and a >= LEAVE["close"]):
        return "close"
    if a >= FRIENDLY or (old in GOOD and a >= LEAVE["friendly"]):
        return "friendly"
    return "nodding"


def talk_speed(ta, tb):
    talks = {ta.get("talk"), tb.get("talk")}
    if talks == {"quiet"}:
        return 0.6
    if "talker" in talks:
        return 1.25
    return 1.0


class Rel:
    """One pair. a and b are in sorted order."""

    def __init__(self, a, b):
        self.a, self.b = a, b
        self.affinity = 0.0
        self.state = "strangers"
        self.outings = 0
        self.wipes = 0
        self.saves = {}                 # healer rid -> times they pulled the other through
        self.gifts = 0                  # gear passed between them by the player
        self.quarrels = 0
        self.was_bad = False            # has ever been grating or rivals
        self.met_said = False           # the introduction has been spoken
        self.tags_found = []
        self.milestones = []            # turn_friendly, turn_friends, ... once each
        self.heard = []                 # line ids already used for this pair, so it doesn't repeat
        self.sig_step = 0               # next step of their signature arc, if they have one
        self.sig_at = 0                 # outings when the last signature step played
        self.memory = 0.0               # what's happened between them, kept in where they settle

    def other(self, rid):
        return self.b if rid == self.a else self.a

    def to_dict(self):
        return dict(self.__dict__)

    def load(self, d):
        for k, v in d.items():
            if k in self.__dict__:
                setattr(self, k, v)


class RelationshipManager:
    def __init__(self, bonds=None):
        self.bm = bonds                 # the BondManager that owns this one
        self.traits, self.lines, self.sigs = {}, {}, {}
        self.rels = {}
        self.queue = []                 # [(priority, deed stamp, [(rid, text)])]
        self.recent = []                # line ids from the last few beats, whoever said them
        self.log = []
        self._chem = {}
        self.last_ask = None            # the argument the beat just popped pulls the player into, if any
        self._load()
        # Wave 4: the party as a group (world/group_dynamics.py), on top of the pairs
        from world.group_dynamics import GroupDynamics
        self.groups = GroupDynamics(self)

    def _load(self):
        try:
            raw = json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        self.traits = raw.get("traits") or {}
        self.lines = raw.get("lines") or {}
        for p in raw.get("pairs") or []:
            self.sigs[self.key(p["a"], p["b"])] = p

    # ------------------------------------------------------------ helpers
    @staticmethod
    def key(a, b):
        return "|".join(sorted((a, b)))

    def has(self, rid):
        return rid in self.traits

    def rel(self, a, b):
        k = self.key(a, b)
        r = self.rels.get(k)
        if r is None:
            x, y = sorted((a, b))
            r = self.rels[k] = Rel(x, y)
            if self._neighbours(x, y):
                r.affinity = NEIGHBOUR_START
                r.state = "nodding"
        return r

    def state(self, a, b):
        r = self.rels.get(self.key(a, b))
        if r is None:
            return "nodding" if self._neighbours(a, b) else "strangers"
        return r.state

    def chem(self, a, b, outings=0):
        """Chemistry as it stands after this many outings together."""
        k = self.key(a, b)
        if k not in self._chem:
            self._chem[k] = chemistry_parts(self.traits.get(a, {}), self.traits.get(b, {}), a, b)
        lasting, fading = self._chem[k]
        return lasting + fading * fade(outings)

    def _neighbours(self, a, b):
        try:
            ha = self.bm.bonds[a].data.get("home")
            hb = self.bm.bonds[b].data.get("home")
            return bool(ha) and ha == hb
        except (AttributeError, KeyError):
            return False

    def _t(self, rid):
        return self.traits.get(rid, {})

    def first(self, rid):
        try:
            return self.bm.name_of(rid).split()[0]
        except Exception:
            return rid

    def gender(self, rid):
        try:
            from world.recruit_manager import get_recruit_manager
            r = get_recruit_manager().recruits.get(rid)
            return getattr(r, "gender", None) or "male"
        except Exception:
            return "male"

    def address(self, text, to):
        """{hermano|hermana}: the first form for a man, the second for a woman, by whoever the
        line is said to. Spanish, Portuguese, Arabic and Turkish all change the word."""
        if "{" not in text:
            return text
        female = to is not None and self.gender(to) == "female"
        return ADDRESS.sub(lambda m: m.group(2) if female else m.group(1), text)

    def _deeds(self):
        return getattr(self.bm, "deeds", 0)

    def ids(self, party):
        return [m.recruit_id for m in getattr(party, "members", []) or []
                if getattr(m, "recruit_id", None) in self.traits]

    def pairs_in(self, ids):
        ids = sorted(set(ids))
        return [(ids[i], ids[j]) for i in range(len(ids)) for j in range(i + 1, len(ids))]

    def line(self, rid, key, r=None, name_of=None):
        """A line from rid's pool, with {name} filled in. Unheard for this pair if possible.
        Returns None when they don't have one (a recruit whose Wave 3 lines aren't written yet)."""
        t = (self.lines.get(rid) or {}).get(key)
        if not t:
            return None
        opts = t if isinstance(t, list) else [t]
        if r is not None:
            fresh = [o for o in opts if _hid(rid, o) not in r.heard]
            opts = fresh or opts
        text = random.choice(opts)
        if r is not None:
            r.heard = (r.heard + [_hid(rid, text)])[-HEARD:]
        if "{name}" in text:
            text = text.replace("{name}", self.first(name_of) if name_of else "")
        return text

    def _beat(self, parts, r=None, priority=1):
        """parts: [(rid, key, name_of)]. Queues the beat if every line exists, and if this pair
        hasn't just had the same exchange: the player shouldn't hear the same two lines twice in a
        row from the same two people, even when the same thing has happened twice."""
        out, ids = [], []
        for rid, key, who in parts:
            # A CONFIDENCE WAITS FOR THE PLAYER'S FRIENDSHIP TOO (27 Nov 2026). Two recruits confide in each other once
            # they're close, but the player is standing right there, and these lines tell the secrets a recruit keeps
            # from the player until Friend (Matias's father, Dan's four years, Ivan's fear). So a confidence plays only
            # once the speaker is at least a Friend of the player's.
            if key in PRIVATE_KEYS and self.bm is not None:
                b = getattr(self.bm, "bonds", {}).get(rid)
                if b is not None and b.stage < PRIVATE_STAGE:
                    return False
            t = (self.lines.get(rid) or {}).get(key)
            if not t:
                return False
            opts = t if isinstance(t, list) else [t]
            if r is not None:
                opts = [o for o in opts if _hid(rid, o) not in r.heard] or opts
            raw = random.choice(opts)
            ids.append(_hid(rid, raw))
            to = who or (r.other(rid) if r is not None and rid in (r.a, r.b) else None)
            text = raw.replace("{name}", self.first(who)) if who else raw.replace("{name}", "")
            out.append((rid, self.address(text, to)))
        if r is not None:
            # an ordinary chat is never told twice to the same person while they'd remember it;
            # something that happens again (a wipe, a near miss) can be answered the same way
            # once enough else has been said in between
            if ids[0] in (r.heard if priority <= 1 else r.heard[-12:]):
                return False
            r.heard = (r.heard + ids)[-HEARD:]
        if priority <= 1:
            # the same question to three people in a row is a script, not a person
            if any(i in self.recent for i in ids):
                return False
        self.recent = (self.recent + ids)[-RECENT:]
        self.queue.append((priority, self._deeds(), out))
        self.queue.sort(key=lambda q: -q[0])
        self.queue = self.queue[:3]
        for rid, text in out:
            self.log.append((rid, text))
        self.log = self.log[-60:]
        return True

    def _chem_parts(self, a, b):
        k = self.key(a, b)
        if k not in self._chem:
            self._chem[k] = chemistry_parts(self.traits.get(a, {}), self.traits.get(b, {}), a, b)
        return self._chem[k]

    def _move(self, r, amount, event=True):
        """Change affinity and work out the new state. Returns the milestone key, if any. An event (a wipe, a save,
        something said) also shifts where the pair settles, so it isn't simply pulled back out of them."""
        r.affinity = max(-100.0, min(100.0, r.affinity + amount))
        if event and abs(amount) >= MEMORY_MIN:
            r.memory = max(-60.0, min(60.0, getattr(r, "memory", 0.0) + amount * MEMORY))
        old = "nodding" if r.state == "strangers" else r.state
        new = next_state(old, r.affinity)
        r.state = new
        if new == old:
            return None
        if new in BAD and old not in BAD:
            r.was_bad = True
            r.quarrels += 1
        if new == "friendly" and r.was_bad and old not in GOOD:
            return "make_up"
        return {"friendly": "turn_friendly", "close": "turn_friends", "grating": "turn_grating",
                "rivals": "turn_rivals"}.get(new)

    def _milestone(self, r, key):
        if key is None or key in r.milestones:
            return
        r.milestones.append(key)
        try:
            from world.conversations import get_conversations
            get_conversations().on_pair_changed(r.a, r.b, key)
        except Exception:
            pass
        if key == "turn_friendly" and "make_up" in r.milestones:
            return
        x, y = self._by_talk(r.a, r.b)
        named = key in NAMED
        self._beat([(x, key, y if named else None), (y, key, x if named else None)], r, priority=3)

    def _by_talk(self, a, b):
        """The one more likely to speak first goes first."""
        w = {"talker": 3, "middle": 2, "quiet": 1}
        wa, wb = w.get(self._t(a).get("talk"), 2), w.get(self._t(b).get("talk"), 2)
        if wa == wb:
            return (a, b) if random.random() < 0.5 else (b, a)
        return (a, b) if wa > wb else (b, a)

    # ------------------------------------------------------------ the road
    def on_outing(self, ids, kind="quest"):
        """An outing finished with these recruits along. Returns {rid: mood change}."""
        ids = [i for i in ids if i in self.traits]
        mood = {i: 0.0 for i in ids}
        self._introductions(ids)
        for a, b in self.pairs_in(ids):
            r = self.rel(a, b)
            r.outings += 1
            if not r.met_said:
                continue                # they get to know each other once they've been introduced
            lasting, fading = self._chem_parts(a, b)
            target = settle_target(lasting, fading, r.outings, r.memory)
            delta = SETTLE_RATE * (target - r.affinity) * talk_speed(self._t(a), self._t(b))
            self._milestone(r, self._move(r, delta, event=False))
            if kind in ("dungeon", "boss") and r.state in BAD:
                self._milestone(r, self._move(r, 0.5))   # a hard job done together earns a grudging nod
            for me, other in ((a, b), (b, a)):
                mood[me] += {"close": 5, "friendly": 3, "grating": -2, "rivals": -4}.get(r.state, 0)
        took = False
        try:
            took = self.groups.on_outing(ids, kind, zone=getattr(self, "zone", None))
            extra = self.groups.mood_effect(ids)
            for i in mood:
                mood[i] += extra
        except Exception:
            pass
        if len(ids) >= 2 and not took:
            self._sig_or_ambient(ids, AMBIENT_CHANCE)
        return {i: max(-6.0, min(6.0, v)) for i, v in mood.items()}

    def _introductions(self, ids):
        """Whoever has the most people here they haven't met says who they are, and up to two of
        the others answer. Everybody present hears it, so one beat introduces the whole party.
        A pair who've never been introduced (their lines aren't written yet) meet quietly."""
        unmet = [(a, b) for a, b in self.pairs_in(ids) if not self.rel(a, b).met_said]
        if not unmet:
            return
        count = {}
        for a, b in unmet:
            count[a] = count.get(a, 0) + 1
            count[b] = count.get(b, 0) + 1
        new = max(sorted(count), key=lambda x: (count[x], random.random()))
        others = [x for x in ids if x != new and not self.rel(new, x).met_said]
        random.shuffle(others)
        others.sort(key=lambda x: -self._speaker_weight(x))
        parts = [(new, "meet", others[0] if others else None)]
        for x in others[:2]:
            # (meet lines never use {name}; passing who only tells {hermano|hermana} who's listening)
            parts.append((x, "meet_neighbour" if self._neighbours(new, x) else "meet", new))
        spoken = [p for p in parts if (self.lines.get(p[0]) or {}).get(p[1])]
        heard = set()
        if len(spoken) >= 2 and spoken[0][0] == new:
            if self._beat(spoken, self.rel(new, spoken[1][0]), priority=2):
                heard = {p[0] for p in spoken}
        has = lambda x: bool((self.lines.get(x) or {}).get("meet"))
        for a, b in unmet:
            if a in heard or b in heard or not has(a) or not has(b):
                self.rel(a, b).met_said = True

    def on_rest(self, ids):
        """Arriving in a town: sometimes they talk while they settle in."""
        ids = [i for i in ids if i in self.traits]
        try:
            if self.groups.on_rest(ids):
                return
        except Exception:
            pass
        if len(ids) >= 2:
            self._sig_or_ambient(ids, REST_CHANCE, tags=False)

    def _sig_or_ambient(self, ids, chance, tags=True):
        if any(q[0] >= 2 for q in self.queue):
            return                      # a meeting or a milestone is already waiting
        pairs = self.pairs_in(ids)
        random.shuffle(pairs)
        for a, b in pairs:
            if self._signature(a, b):
                return
        if tags:
            for a, b in pairs:
                r = self.rel(a, b)
                common = [t for t in set(self._t(a).get("tags", [])) & set(self._t(b).get("tags", []))
                          if t not in r.tags_found]
                if common and r.met_said and random.random() < TAG_CHANCE:
                    tag = random.choice(sorted(common))
                    x, y = self._by_talk(a, b)
                    if self._beat([(x, f"common_{tag}", None), (y, f"common_{tag}", None)], r, 2):
                        r.tags_found.append(tag)
                        self._milestone(r, self._move(r, 3))
                        return
        if random.random() < chance:
            self._ambient(ids)

    def _signature(self, a, b):
        r = self.rel(a, b)
        p = self.sigs.get(self.key(a, b))
        if not p or r.sig_step >= len(p["steps"]):
            return False
        step = p["steps"][r.sig_step]
        if not self._sig_ready(r, step):
            return False
        self.queue.append((2, self._deeds(), [(rid, t) for rid, t in step["lines"]]))
        self.queue.sort(key=lambda q: -q[0])
        self.queue = self.queue[:3]
        for rid, t in step["lines"]:
            self.log.append((rid, t))
        if r.sig_step == 0:
            # an arc opens with the two of them finding out where each other's from and what they
            # did, so the ordinary "where are you from" and "you speak Greek too" beats would only
            # repeat it: count those as said
            for x in (a, b):
                for topic in ("home", "work"):
                    if f"ask_{topic}:{x}" not in r.milestones:
                        r.milestones.append(f"ask_{topic}:{x}")
            shared = set(self._t(a).get("tags", [])) & set(self._t(b).get("tags", []))
            r.tags_found += [g for g in sorted(shared) if g not in r.tags_found]
        r.sig_step += 1
        r.sig_at = r.outings
        if step.get("affinity"):
            self._milestone(r, self._move(r, step["affinity"]))
        return True

    @staticmethod
    def _sig_ready(r, step):
        """when: met, friendly, close, grating, outings:N, or gap:N (outings since the last step)."""
        w = step.get("when", "met")
        if w == "met":
            return r.met_said
        if w == "friendly":
            return r.state in GOOD
        if w == "close":
            return r.state == "close"
        if w == "grating":
            return r.state in BAD
        if w.startswith("outings:"):
            return r.outings >= int(w.split(":")[1])
        if w.startswith("gap:"):
            return r.outings - r.sig_at >= int(w.split(":")[1])
        return False

    def _speaker_weight(self, rid):
        return {"talker": 1.6, "middle": 1.0, "quiet": 0.55}.get(self._t(rid).get("talk"), 1.0)

    def _ambient(self, ids):
        """One ordinary conversation between two of them, picked by how they get on."""
        pairs = [(a, b) for a, b in self.pairs_in(ids) if self.rel(a, b).met_said]
        if not pairs:
            return
        # talkative pairs talk more often; a pair who just talked lets somebody else have a turn
        last = getattr(self, "_last_pair", None)
        weights = [(self._speaker_weight(a) + self._speaker_weight(b)) * (0.3 if (a, b) == last else 1)
                   for a, b in pairs]
        a, b = random.choices(pairs, weights=weights)[0]
        self._last_pair = (a, b)
        r = self.rel(a, b)
        s = a if random.random() * (self._speaker_weight(a) + self._speaker_weight(b)) \
            < self._speaker_weight(a) else b
        o = r.other(s)
        st = r.state
        acts = []
        for topic in ("home", "work"):
            if f"ask_{topic}:{s}" not in r.milestones:
                acts += [("ask", topic)] * (3 if st == "nodding" else 1)
        acts += [("chat", None)] * (3 if st == "nodding" else 2 if st in GOOD else 1)
        if st in GOOD:
            acts += [("tease", None)] * (3 if self._t(s).get("humour") == "joker" else 2)
            acts += [("look_out", None)] * 1
        if st == "close" and f"confide:{s}" not in r.milestones:
            acts += [("confide", None)] * 2
        if st in BAD:
            acts += [("needle", None)] * (4 if st == "rivals" else 3)
        random.shuffle(acts)
        for act, topic in acts:
            if getattr(self, f"_act_{act}")(r, s, o, ids, topic):
                return

    # ------------------------------------------------------------ acts
    def _act_ask(self, r, s, o, ids, topic):
        if self._beat([(s, f"ask_{topic}", None), (o, f"answer_{topic}", None)], r):
            r.milestones.append(f"ask_{topic}:{s}")
            self._milestone(r, self._move(r, 1.5))
            return True
        return False

    def _act_chat(self, r, s, o, ids, topic):
        topics = list(CHAT_TOPICS)
        random.shuffle(topics)
        for tp in topics:
            if self._beat([(s, f"chat_{tp}", None), (o, f"chat_{tp}", None)], r):
                self._milestone(r, self._move(r, 1))
                return True
        return False

    def _aimed(self, s, o, kind):
        """tease_quiet, needle_bold and so on: aimed at what stands out about the other one."""
        t = self._t(o)
        keys = []
        if t.get("talk") in ("quiet", "talker"):
            keys.append(f"{kind}_{t['talk']}")
        if t.get("pace") == "careful":
            keys.append(f"{kind}_careful")
        elif t.get("pace") == "bold":
            keys.append(f"{kind}_bold")
        keys.append(f"{kind}_any")
        mine = self.lines.get(s) or {}
        keys = [k for k in keys if mine.get(k)]
        return random.choice(keys) if keys else None

    def _act_tease(self, r, s, o, ids, topic):
        key = self._aimed(s, o, "tease")
        if key is None:
            return False
        ts, to = self._t(s), self._t(o)
        bristles = to.get("manner") == "formal" or (to.get("manner") == "blunt" and r.affinity < 35
                                                     and to.get("humour") == "earnest")
        if bristles and random.random() < 0.6:
            sorry = ts.get("manner") == "gentle" or ts.get("humour") == "earnest" or r.state == "close"
            third = "apologise" if sorry else "double_down"
            if self._beat([(s, key, o), (o, "bristle", s), (s, third, None)], r):
                self._milestone(r, self._move(r, -2 + (2.5 if sorry else -1)))
                return True
            return False
        back = to.get("humour") in ("joker", "dry") and random.random() < 0.75
        if self._beat([(s, key, o), (o, "tease_back" if back else "take_it_kindly", s)], r):
            self._milestone(r, self._move(r, 2 if back else 1.5))
            return True
        return False

    def _act_look_out(self, r, s, o, ids, topic):
        proud = self._dial(o, "pride") >= 1.1 or self._t(o).get("manner") == "blunt"
        reply = "deflect" if proud and random.random() < 0.6 else "accept"
        if self._beat([(s, "look_out", o), (o, reply, s)], r):
            self._milestone(r, self._move(r, 2 if reply == "accept" else 0.5))
            return True
        return False

    def _act_confide(self, r, s, o, ids, topic):
        if self._beat([(s, "confide", o), (o, "listen", s)], r):
            r.milestones.append(f"confide:{s}")
            self._milestone(r, self._move(r, 3))
            return True
        return False

    def _act_needle(self, r, s, o, ids, topic):
        key = self._aimed(s, o, "needle")
        if key is None:
            return False
        return self._sharp(r, s, o, ids, key)

    def _sharp(self, r, s, o, ids, key):
        """A dig (a needle, or blame after a wipe) and how it lands."""
        ts, to = self._t(s), self._t(o)
        if to.get("humour") == "joker" or (self._dial(o, "nerve") >= 1.3 and to.get("manner") != "blunt"):
            reply, delta = "laugh_off", 1.5
        elif to.get("manner") == "blunt" or self._dial(o, "pride") >= 1.1:
            reply, delta = "bite_back", -2.5
        else:
            reply, delta = "hurt", -1.5
        parts = [(s, key, None), (o, reply, None)]
        friend = None
        if reply == "hurt":
            if ts.get("manner") == "gentle" or ts.get("humour") == "earnest":
                parts.append((s, "apologise", None))
                delta += 3
            else:
                friend = next((d for d in ids if d not in (s, o)
                               and self.state(d, o) in GOOD and self.state(d, s) != "close"), None)
                if friend and self.line(friend, "defend") is not None:
                    parts.append((friend, "defend", o))
        elif reply == "bite_back" and ts.get("humour") == "joker" and random.random() < 0.5:
            parts.append((s, "double_down", None))
            delta -= 1
        if self._beat(parts, r):
            self._milestone(r, self._move(r, delta))
            if friend:
                rf, rs = self.rel(friend, o), self.rel(friend, s)
                self._milestone(rf, self._move(rf, 2))
                self._milestone(rs, self._move(rs, -3))
            return True
        return False

    def _dial(self, rid, k):
        try:
            return self.bm.bonds[rid].dial(k)
        except (AttributeError, KeyError):
            return 1.0

    # ------------------------------------------------------------ events
    def on_wipe(self, ids, first_down=None):
        ids = [i for i in ids if i in self.traits]
        try:
            if self.groups.on_wipe(ids, first_down):
                for a, b in self.pairs_in(ids):
                    self.rel(a, b).wipes += 1
                return
        except Exception:
            pass
        if len(ids) < 2:
            return
        for a, b in self.pairs_in(ids):
            r = self.rel(a, b)
            r.wipes += 1
            self._milestone(r, self._move(r, -1 if r.state in BAD else 2))
        pairs = self.pairs_in(ids)
        random.shuffle(pairs)
        for a, b in pairs:
            r = self.rel(a, b)
            s, o = self._by_talk(a, b)
            if r.state in GOOD:
                proud = self._dial(o, "pride") >= 1.1 or self._t(o).get("manner") == "blunt"
                if self._beat([(s, "check_in", o), (o, "deflect" if proud else "accept", s)], r, 2):
                    return
            elif r.state in BAD and random.random() < 0.6:
                if self._sharp(r, s, o, ids, "blame"):
                    return

    def on_close_call(self, ids, hurt):
        """hurt: recruit ids who ended a fight on almost nothing. A healer in the party pulled them
        through; a friend who saw it goes grey."""
        ids = [i for i in ids if i in self.traits]
        try:
            if self.groups.on_close_call(ids, hurt):
                return
        except Exception:
            pass
        for h in [x for x in hurt if x in self.traits]:
            healers = [x for x in ids if x != h and "healer" in self._t(x).get("is", [])]
            for x in healers:
                r = self.rel(h, x)
                r.saves[x] = r.saves.get(x, 0) + 1
                self._milestone(r, self._move(r, 4))
            friends = [x for x in ids if x != h and self.state(h, x) in GOOD and x not in healers]
            if healers and random.random() < 0.6:
                x = random.choice(healers)
                if self._beat([(h, "thank", None), (x, "brush_off", None)], self.rel(h, x), 2):
                    return
            if friends:
                x = random.choice(friends)
                proud = self._dial(h, "pride") >= 1.1
                self._beat([(x, "worry", h), (h, "deflect" if proud else "accept", x)],
                           self.rel(h, x), 2)
                return

    def on_gear_moved(self, giver, taker, better):
        """The player took a piece off giver and put it on taker."""
        if giver not in self.traits or taker not in self.traits or giver == taker:
            return
        r = self.rel(giver, taker)
        r.gifts += 1
        self.groups.on_gear_moved(giver, taker)
        sulk = r.state in BAD or (self._dial(giver, "pride") >= 1.2 and r.state not in GOOD)
        if self._beat([(taker, "handed_down", None), (giver, "hand_sulk" if sulk else "hand_fine", None)],
                      r, 2):
            self._milestone(r, self._move(r, -3 if sulk else 2))

    def on_left(self, rid, ids):
        """rid went home; a close friend still in the party says so."""
        self.groups.on_left(rid, ids)
        for x in ids:
            if x != rid and self.state(rid, x) == "close":
                self._beat([(x, "friend_left", rid)], self.rel(rid, x), 2)
                return

    def on_back(self, rid, ids):
        for x in ids:
            if x != rid and self.state(rid, x) == "close":
                self._beat([(x, "friend_back", rid)], self.rel(rid, x), 2)
                return

    # ------------------------------------------------------------ showing it
    def pop_beat(self, since_last=GAP):
        """The next queued beat as [(rid, text)], or None. Called by the banter panel when it's free."""
        if since_last < GAP or not self.queue:
            return None
        now = self._deeds()
        self.queue = [q for q in self.queue if now - q[1] <= STALE]
        if not self.queue:
            return None
        item = self.queue.pop(0)
        # one scene per gap, and what was waiting behind it is let go rather than banked: a backlog played out one
        # after another is exactly the spam (the queue is sorted by priority, so what's dropped is the small talk)
        self.queue = [q for q in self.queue if q[0] >= 2]
        self.last_ask = item[3] if len(item) > 3 else None
        return item[2]

    def summary(self, rid):
        """[(other rid, state)] for everyone rid has met, warmest first. For the party screen."""
        out = []
        for r in self.rels.values():
            if rid in (r.a, r.b) and r.state != "strangers":
                out.append((r.other(rid), r.state, r.affinity))
        out.sort(key=lambda x: -x[2])
        return [(o, s) for o, s, _a in out]

    # ------------------------------------------------------------ save
    def to_dict(self):
        out = {k: r.to_dict() for k, r in self.rels.items()}
        out["__groups__"] = self.groups.to_dict()
        return out

    def load_state(self, d):
        self.rels = {}
        d = dict(d or {})
        self.groups.load_state(d.pop("__groups__", None))
        for k, rd in d.items():
            a, _, b = k.partition("|")
            r = Rel(a, b)
            r.load(rd)
            self.rels[k] = r
