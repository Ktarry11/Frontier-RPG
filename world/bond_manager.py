"""Recruit friendship: trust that grows over time, and a mood that decides whether they stay.

Design: claude/recruit_bonds_DESIGN_ONLY.md (Kyle's fifteen answers, 13 Nov 2026). Text:
data/npcs/bonds.json, written by tools/build_recruit_bonds.py. Pilot: Kesten, Adrián and Tarek.
Anyone without a record in bonds.json is untouched by all of this and behaves as before.

TWO THINGS PER RECRUIT
  trust   slow and long-term. Moves through five named stages and never drops a stage (decision 6):
          bad treatment stalls it, a Friend is never an Acquaintance again.
  mood    this trip only. Starts each stint at 70. Below WARN they say what is wrong, once, naming
          the cause; below LEAVE, or when the stint is over, they go home at the next safe point.

OUTINGS. Time is counted in things done, not minutes (decision 2): a quest handed in or a dungeon
finished is one outing. A stint is so many outings with you; a break is so many outings you do
without them. Idling brings nobody back.

SAFE POINTS. Nobody leaves in a dungeon, a cave, a fight or on the way to one. Departures queued
during a trip happen when the party arrives in a town or hands in a quest outside a dungeon. The
one exception is decision 1: a nervy recruit can walk out at the dungeon door after one wipe too
many, and only after a warning.
"""
import json
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "npcs" / "bonds.json"

STAGES = ["stranger", "acquaintance", "companion", "friend", "sworn"]
STAGE_NAMES = {"stranger": "Stranger", "acquaintance": "Acquaintance", "companion": "Companion",
               "friend": "Friend", "sworn": "Sworn"}
#: trust needed for each stage. Sworn also needs their personal quest done (flag goal_done).
THRESHOLDS = [0, 20, 60, 130, 220]
#: outings with you before they want to go home, by stage
STINT = [3, 5, 8, 12, 16]
#: outings you do without them before they're back, by stage
BREAK = [4, 4, 3, 3, 2]
#: trust for each kind of thing done together
GAIN = {"quest": 3, "dungeon": 8, "boss": 4, "upgrade": 5, "rest": 2}
MOOD_START, WARN, LEAVE = 70, 35, 20
GRIND_KILLS = 30            # open-world kills with no outing in between = one dose of boredom
ZONE_GAP = 3                # a zone this many levels above them is too high
NEGLECT_OUTINGS = 25        # this many outings without them earns a tease when they rejoin
PAIR_OUTINGS = 8            # outings two of them share before pair banter appears


class Bond:
    def __init__(self, rid, data):
        self.rid = rid
        self.data = data
        self.trust = 0.0
        self.stage = 0
        self.mood = MOOD_START
        self.outings = 0
        self.stint_len = 0
        self.stints = 0
        self.away = False
        self.break_left = 0
        self.angry = False
        self.needs_talk = False         # an angry walkout: they say their piece before rejoining
        self.warned = None              # the cause they've already warned about this stint
        self.leave_cause = None         # set when they'll go at the next safe point
        self.asked_this_stint = False
        self.wipes = 0
        self.kills = 0
        self.high_zones = 0
        self.short = []                 # slots you took and never refilled
        self.flags = []
        self.moments_done = []
        self.blocked_until = -1         # an answer that made them say "come back another day"
        self.last_with_you = 0
        self.pending = None             # a moment waiting to be shown (id)
        self.in_party = False

    # -- reading
    @property
    def dials(self):
        return self.data.get("dials", {})

    def dial(self, k):
        return float(self.dials.get(k, 1.0))

    @property
    def stage_key(self):
        return STAGES[self.stage]

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if k not in ("rid", "data")}

    def load(self, d):
        for k, v in d.items():
            if k in self.__dict__ and k not in ("rid", "data"):
                setattr(self, k, v)


class BondManager:
    def __init__(self):
        self.bonds = {}
        self.pairs = []
        self.deeds = 0
        self.pair_time = {}
        self.pairs_heard = []
        self.log = []                   # [(rid, text)] for the test panel and the party screen
        self.party = None
        self._load()

    def _load(self):
        try:
            raw = json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        for rid, d in (raw.get("bonds") or {}).items():
            self.bonds[rid] = Bond(rid, d)
        self.pairs = raw.get("pairs") or []

    # ------------------------------------------------------------ helpers
    def has(self, rid):
        return rid in self.bonds

    def get(self, rid):
        return self.bonds.get(rid)

    def name_of(self, rid):
        try:
            from world.recruit_manager import get_recruit_manager
            r = get_recruit_manager().recruits.get(rid)
            return r.name if r else rid
        except Exception:
            return rid

    def say(self, rid, text, hold=7.0):
        if not text:
            return
        self.log.append((rid, text))
        self.log = self.log[-40:]
        try:
            from world.banter_manager import get_banter_manager
            get_banter_manager().say(rid, self.name_of(rid), f"\"{text}\"", hold=hold)
        except Exception:
            pass

    def line(self, rid, key):
        b = self.bonds.get(rid)
        return (b.data.get("lines") or {}).get(key, "") if b else ""

    def _members(self, party):
        if party is None:
            return []
        return [m for m in getattr(party, "members", []) if getattr(m, "recruit_id", None) in self.bonds]

    def _in(self, party):
        out = []
        for m in self._members(party):
            b = self.bonds[m.recruit_id]
            if not b.in_party:
                # already with you when this system arrived (an older save), or added some way
                # that didn't go through the recruit screen: start a trip quietly
                b.in_party = True
                b.away = False
                b.stint_len = self._stint_length(b)
                b.stints += 1
                b.mood = MOOD_START
            out.append(b)
        return out

    def _trust(self, b, amount):
        """Trust moves; the stage only ever moves up. A dip can't take them below their stage."""
        if amount > 0:
            amount *= b.dial("warmth")
        b.trust = max(THRESHOLDS[b.stage], b.trust + amount)
        top = len(STAGES) - 1 if "goal_done" in b.flags else len(STAGES) - 2
        while b.stage < top and b.trust >= THRESHOLDS[b.stage + 1]:
            b.stage += 1
            self.log.append((b.rid, f"[{self.name_of(b.rid)} is now a {STAGE_NAMES[b.stage_key]}.]"))

    def _mood(self, b, amount):
        b.mood = max(0, min(100, b.mood + amount))
        if b.mood < WARN and not b.warned:
            self._warn(b, "bored")

    def _warn(self, b, cause):
        b.warned = cause
        key = {"bored": "bored_warning", "wipe": "wipe_warning", "zone": "zone_warning"}[cause]
        self.say(b.rid, self.line(b.rid, key))

    def _stint_length(self, b):
        n = STINT[b.stage]
        if b.data.get("first_stint_short") and b.stints == 0:
            n = 2
        elif "asked_to_stay" in b.flags:
            n = round(n * 1.5)
        # restless people go sooner; 1.0 is ordinary
        return max(2, round(n / max(0.4, b.dial("restless"))))

    # ------------------------------------------------------------ joining and leaving
    def can_hire(self, rid):
        """(ok, text). False while they're away, or when an answer sent you off for today."""
        b = self.bonds.get(rid)
        if b is None:
            return True, ""
        if b.away:
            return False, self.line(rid, "on_break")
        if b.blocked_until > self.deeds:
            return False, ""
        return True, ""

    def hire_moment(self, rid):
        """The first-meeting reply moment, if it's still to be answered."""
        b = self.bonds.get(rid)
        if b is None:
            return None
        for m in b.data.get("moments", []):
            if m["when"] == "hire" and m["id"] not in b.moments_done:
                return m
        return None

    def on_joined(self, rid):
        b = self.bonds.get(rid)
        if b is None:
            return
        returning = b.stints > 0
        b.in_party = True
        b.mood = MOOD_START
        b.outings = 0
        b.stint_len = self._stint_length(b)
        b.warned = b.leave_cause = None
        b.asked_this_stint = False
        b.wipes = b.kills = b.high_zones = 0
        b.angry = False
        if returning:
            if self.deeds - b.last_with_you >= NEGLECT_OUTINGS:
                self.say(rid, self.line(rid, "neglect"))
            else:
                self.say(rid, self.line(rid, "back"))
        b.stints += 1

    def depart(self, b, cause, angry=False, quiet=False):
        """Send them home now. The caller has already checked it's a safe point."""
        key = {"stint": "leaving_good", "bored": "leaving_bored", "wipe": "wipe_leave",
               "zone": "zone_leave"}.get(cause, "leaving_good")
        if cause == "stint" and b.stage == 0 and b.data.get("first_stint_short") \
                and "first_goodbye" not in b.moments_done:
            # Adrián's first goodbye is a question, not a departure: the party screen asks it
            if b.pending != "first_goodbye":
                b.pending = "first_goodbye"
                m = next(x for x in b.data["moments"] if x["id"] == "first_goodbye")
                self.say(b.rid, m.get("line", ""))
            b.leave_cause = None
            return False
        if not quiet:
            self.say(b.rid, self.line(b.rid, key))
        b.in_party = False
        b.away = True
        b.angry = angry
        b.needs_talk = angry
        b.break_left = BREAK[b.stage] * (2 if angry else 1)
        b.last_with_you = self.deeds
        b.leave_cause = None
        member = next((m for m in self._members(self.party) if m.recruit_id == b.rid), None)
        if member is not None:
            try:
                from world.recruit_manager import get_recruit_manager
                get_recruit_manager().dismiss(member)
                self.party.remove_member(member)
            except Exception:
                pass
        return True

    def ask_to_stay(self, rid):
        """The player asks them to stay for one more outing. Once a stint, never after an angry walkout."""
        b = self.bonds.get(rid)
        if b is None or not b.in_party or b.asked_this_stint or b.angry:
            return False
        if not (b.warned or b.leave_cause):
            return False
        b.asked_this_stint = True
        b.stint_len = max(b.stint_len, b.outings + 1)
        if b.leave_cause in ("stint", "bored"):
            b.leave_cause = None
        b.mood = max(b.mood, WARN + 5)
        b.warned = None
        self.say(rid, self.line(rid, "asked_to_stay"))
        return True

    def safe_point(self, party=None):
        """A town, or a quest handed in outside a dungeon. Anyone due to go goes now."""
        party = party or self.party
        gone = []
        for b in self._in(party):
            cause = b.leave_cause
            if cause is None and b.mood < LEAVE and b.warned:
                cause = b.warned
            if cause is None and b.outings >= b.stint_len:
                cause = "stint"
            if cause and self.depart(b, cause, angry=cause in ("wipe",)):
                gone.append(b.rid)
        return gone

    # ------------------------------------------------------------ what happens on the road
    def on_deed(self, kind, party=None, zone=None):
        """A quest handed in ("quest") or a dungeon finished ("dungeon")."""
        party = party or self.party
        self.deeds += 1
        here = self._in(party)
        for b in self.bonds.values():
            if b.away:
                b.break_left -= 1
                if b.break_left <= 0:
                    b.away = False
                    if b.stage >= STAGES.index("friend"):
                        self.log.append((b.rid, self.line(b.rid, "send_word")))
                        self._notify(self.line(b.rid, "send_word"))
        for b in here:
            b.outings += 1
            b.kills = 0
            b.last_with_you = self.deeds
            self._trust(b, GAIN.get(kind, 3))
            if kind in b.data.get("likes", []):
                self._mood(b, 6)
            if len(getattr(party, "members", [])) >= 5 and "full_party" in b.data.get("likes", []):
                self._mood(b, 3)
            if b.short:
                self._mood(b, -4 * b.dial("pride"))
        self._pairs(here)
        if zone is None or not self._is_dungeon(zone):
            self.safe_point(party)

    def on_kills(self, enemies, party=None, zone=None):
        party = party or self.party
        here = self._in(party)
        if not here:
            return
        bosses = [e for e in enemies if getattr(e, "is_boss", False)]
        kinds = {self._creature_kind(e) for e in enemies}
        for b in here:
            for k in kinds:
                if k in b.data.get("likes", []):
                    self._mood(b, 2)
                if k in b.data.get("dislikes", []):
                    self._mood(b, -3)
            if bosses:
                self._trust(b, GAIN["boss"])
                self._mood(b, 5 + (5 if "boss" in b.data.get("likes", []) else 0))
                continue
            if zone is not None and self._is_dungeon(zone):
                continue
            before = b.kills // GRIND_KILLS
            b.kills += len(enemies)
            if b.kills // GRIND_KILLS > before:
                hit = 10 * (1.6 if "grinding" in b.data.get("dislikes", []) else 1.0)
                self._mood(b, -hit)

    def on_wipe(self, party=None, at_dungeon_door=False):
        """The whole party died. Returns the ids of anyone who walked out on the spot."""
        party = party or self.party
        gone = []
        for b in self._in(party):
            b.wipes += 1
            nerve = b.dial("nerve")
            self._mood(b, -12 * (1.5 - nerve))
            limit = 2 + round(nerve * 3)
            moment = next((m for m in b.data.get("moments", [])
                           if m["when"] == "wipe" and m["id"] not in b.moments_done), None)
            if moment and b.wipes < limit:
                b.pending = moment["id"]
                continue
            if b.wipes == limit - 1:
                if b.warned != "wipe":
                    self._warn(b, "wipe")
            elif b.wipes >= limit:
                if nerve < 0.7 and at_dungeon_door:
                    if self.depart(b, "wipe", angry=True):
                        gone.append(b.rid)
                else:
                    b.leave_cause = "wipe"      # finishes the run, then goes
            else:
                self.say(b.rid, self.line(b.rid, "after_wipe"))
        return gone

    def on_zone(self, zone, party=None, left_cleared_dungeon=False):
        """Arriving somewhere. A dungeon left with its boss down is an outing; a town is a safe
        point; a zone well above someone's level wears on them."""
        party = party or self.party
        if left_cleared_dungeon:
            self.on_deed("dungeon", party, zone)
        lo = self._zone_level(zone)
        for m in self._members(party):
            b = self.bonds[m.recruit_id]
            if lo and lo >= getattr(m, "level", 1) + ZONE_GAP and not self._is_town(zone):
                b.high_zones += 1
                self._mood(b, -8 * (1.4 - b.dial("nerve")))
                if b.warned != "zone":
                    self._warn(b, "zone")
                elif b.high_zones >= 3:
                    b.leave_cause = "zone"
            else:
                b.high_zones = 0
            if b.short and b.mood > LEAVE:
                self._mood(b, -3 * b.dial("pride"))
        if self._is_town(zone):
            self.safe_point(party)

    # ------------------------------------------------------------ gear
    def may_take(self, rid):
        """(allowed, line). A Stranger refuses; so does a proud one who isn't a Friend yet."""
        b = self.bonds.get(rid)
        if b is None:
            return True, ""
        if b.stage == 0 or (b.dial("pride") >= 0.7 and b.stage < STAGES.index("friend")):
            return False, self.line(rid, "gear_refuse")
        return True, ""

    def on_gear_taken(self, rid, slot, refilled=False):
        b = self.bonds.get(rid)
        if b is None:
            return
        if refilled:
            return
        if slot not in b.short:
            b.short.append(slot)
        self._mood(b, -6 * b.dial("pride"))
        self._trust(b, -2)
        self.say(rid, self.line(rid, "gear_taken"))

    def on_gear_given(self, rid, slot, better):
        b = self.bonds.get(rid)
        if b is None:
            return
        if slot in b.short:
            b.short.remove(slot)
        if better:
            self._trust(b, GAIN["upgrade"])
            self._mood(b, 8)
            self.say(rid, self.line(rid, "gear_upgrade"))

    def on_quest_abandoned(self, party=None):
        for b in self._in(party or self.party):
            if "quest_abandoned" in b.data.get("dislikes", []):
                self._mood(b, -8)
                self.say(b.rid, self.line(b.rid, "quest_abandoned"))

    # ------------------------------------------------------------ talking
    def learned(self, rid):
        """Everything they've told you so far, stage by stage: [(stage name, text)]."""
        b = self.bonds.get(rid)
        if b is None:
            return []
        out = []
        st = b.data.get("stages", {})
        for i in range(b.stage + 1):
            key = STAGES[i]
            if key == "sworn" and key not in st:
                key = f"sworn_{b.data.get('ending', 'bad')}"
            if key in st:
                out.append((STAGE_NAMES[STAGES[i]], st[key]))
        return out

    def talk_moment(self, rid):
        """A reply moment that's due now: a pending one (a goodbye, a wipe) or this stage's talk."""
        b = self.bonds.get(rid)
        if b is None:
            return None
        moments = {m["id"]: m for m in b.data.get("moments", [])}
        if b.pending and b.pending in moments:
            return moments[b.pending]
        for m in b.data.get("moments", []):
            if m["when"] == "talk" and m["id"] not in b.moments_done \
                    and STAGES.index(m["stage"]) <= b.stage:
                return m
        return None

    def answer(self, rid, moment_id, index):
        """Choose a reply. Returns (their reply, joins, stays)."""
        b = self.bonds.get(rid)
        if b is None:
            return "", False, False
        m = next((x for x in b.data.get("moments", []) if x["id"] == moment_id), None)
        if m is None or not 0 <= index < len(m["options"]):
            return "", False, False
        o = m["options"][index]
        joins = bool(o.get("joins", m["when"] != "hire"))
        b.moments_done.append(moment_id)
        if m["when"] == "hire" and not o.get("joins"):
            # "come back another day": they'll ask again after your next outing
            b.moments_done.remove(moment_id)
            b.blocked_until = self.deeds + 1
        self._trust(b, o.get("trust", 0))
        if o.get("mood"):
            self._mood(b, o["mood"])
        if o.get("flag") and o["flag"] not in b.flags:
            b.flags.append(o["flag"])
        if b.pending == moment_id:
            b.pending = None
        stays = bool(o.get("stays"))
        if m["when"] == "first_stint_end":
            if stays:
                b.stint_len = self._stint_length(b) + b.outings
            else:
                self.depart(b, "stint", quiet=True)      # the reply is his goodbye
        return o.get("reply", ""), joins, stays

    def walkout_talk(self, rid):
        """What they say before rejoining after an angry walkout, then the slate is clean."""
        b = self.bonds.get(rid)
        if b is None or not b.needs_talk:
            return None
        return self.line(rid, "walkout_talk")

    def heard_walkout_talk(self, rid):
        b = self.bonds.get(rid)
        if b is not None:
            b.needs_talk = False

    def mood_line(self, rid):
        """One line for the party screen. Words, no numbers (decision 3)."""
        b = self.bonds.get(rid)
        if b is None:
            return ""
        if b.leave_cause == "wipe":
            return "Will finish this run, then go home."
        if b.leave_cause == "zone" or b.warned == "zone":
            return "Thinks this place is too dangerous."
        if b.warned == "wipe":
            return "Shaken by the wipes."
        if b.short:
            return "Wants the gear you took replaced."
        if b.warned == "bored" or b.mood < WARN:
            return "Restless. Wants to do something else."
        if b.outings >= b.stint_len - 1:
            return "Will head home soon."
        if b.mood >= 75:
            return "Glad to be along."
        return "Doing fine."

    # ------------------------------------------------------------ pairs
    def _pairs(self, here):
        ids = {b.rid for b in here}
        for p in self.pairs:
            key = f"{p['a']}|{p['b']}"
            if p["a"] in ids and p["b"] in ids:
                n = self.pair_time.get(key, 0) + 1
                self.pair_time[key] = n
                if p.get("feel") == "grate_then_like":
                    delta = -2 if n < PAIR_OUTINGS else 2
                    self._mood(self.bonds[p["a"]], delta)
                    self._mood(self.bonds[p["b"]], delta)
                elif p.get("feel") == "like":
                    self._mood(self.bonds[p["a"]], 2)
                    self._mood(self.bonds[p["b"]], 2)
                if n >= PAIR_OUTINGS and key not in self.pairs_heard:
                    self.pairs_heard.append(key)
                    self._pair_banter(p)

    def _pair_banter(self, p):
        lines = [(rid, self.name_of(rid), f"\"{t}\"") for rid, t in p["lines"]]
        for rid, _n, t in lines:
            self.log.append((rid, t.strip('"')))
        try:
            from world.banter_manager import get_banter_manager, BanterBeat
            get_banter_manager().current = BanterBeat(lines, hold=6.0)
        except Exception:
            pass

    # ------------------------------------------------------------ the world
    @staticmethod
    def _creature_kind(e):
        t = (getattr(e, "creature_type", None) or getattr(e, "template", None)
             or getattr(e, "monster_type", "") or "").lower()
        for k in ("undead", "demon", "beast"):
            if k in t:
                return k
        return t

    @staticmethod
    def _zone_name(zone):
        return zone if isinstance(zone, str) else getattr(zone, "name", "") or ""

    def _is_dungeon(self, zone):
        try:
            from world.zone_classification import is_dungeon
            return bool(is_dungeon(self._zone_name(zone)))
        except Exception:
            return False

    def _is_town(self, zone):
        if not isinstance(zone, str) and getattr(zone, "is_town", False):
            return True
        return False

    def _zone_level(self, zone):
        try:
            from world.zone_levels import band
            r = band(self._zone_name(zone))
            return int(r[0]) if r else 0
        except Exception:
            return 0

    def _notify(self, text):
        self.log.append(("", text))

    # ------------------------------------------------------------ save
    def to_dict(self):
        return {"deeds": self.deeds, "pair_time": self.pair_time, "pairs_heard": self.pairs_heard,
                "bonds": {rid: b.to_dict() for rid, b in self.bonds.items()}}

    def load_state(self, d):
        d = d or {}
        self.deeds = int(d.get("deeds", 0))
        self.pair_time = dict(d.get("pair_time", {}))
        self.pairs_heard = list(d.get("pairs_heard", []))
        for rid, bd in (d.get("bonds") or {}).items():
            if rid in self.bonds:
                self.bonds[rid].load(bd)


_bond_manager = None


def get_bond_manager():
    global _bond_manager
    if _bond_manager is None:
        _bond_manager = BondManager()
    return _bond_manager


def reset_bond_manager():
    global _bond_manager
    _bond_manager = None
