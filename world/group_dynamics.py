"""Wave 4: the party as a group, not just pairs (pilot: Diego, Sebastian, Sondre).

Plan: claude/group_dynamics_plan.md in the Frontier project. Kyle, 25 Nov 2026: "I want this to be a wide mix...
nice, drama, hilarious to read, found family, support, or pure absolute chaos". Then: people love each other FOR
something and hate each other for the same things; friends criticise, rivals give each other their due; complexity,
growth and change; a recruit is a different version of themselves depending on who's in the room.

The two non-negotiables:
  1. The pilot is the whole system, small. Everything here runs for any set of recruits who have the lines; the rest
     of the cast is data only (tools/group_lines/<rid>.json -> data/npcs/group_lines.json). No code names a recruit.
  2. Templates choose situations, never words. Every word spoken comes from the speaker's own pool.

Owned by RelationshipManager (self.groups), saved inside its save under "groups". Pair states, affinity and the beat
queue are the pair system's; this adds:

  MOOD      the party's dynamic, read fresh each outing from the pairs and traits: family, crew, third wheel,
            split camp, powder keg, chaos crew, easy company.
  ROLES     instigator, peacemaker, mother hen, hype, chaos goblin, quiet one, straight one, scored from traits and
            from WHO'S IN THE ROOM (room()): quiet among strangers, loud with their closest, sharper with a rival.
  KINDS     what someone is loved or hated for (sharp, kind, funny, brave, steady, clever, honest, quiet, fierce,
            warm). Whether a trait is loved or hated is the watcher's call, from their own likes and dislikes.
  SCENES    roast, bicker, third wheel, terrible plan, chaos riff, hype, toast, after a wipe, admire, fondness, dig,
            call-out (sore, then concede), rivals' respect and truce, callbacks to the pair's story, former rivals,
            arc turning points, crew and family milestones.
  CREWS     a trio of mutual friends with enough shared outings, named after the zone it formed in, and a family of
            four. Small perks while together (CREW_BONUS, FAMILY_BONUS), read by Ability._damage_multiplier.
  GROWTH    each pair's story log; slow capped drifts on each person; one authored arc each (or an anchor), three
            turning points, and "after" lines that replace the old ones once they've changed. Arcs can fail.
"""
import json
import random
import zlib
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "npcs" / "group_lines.json"

GOOD = ("friendly", "close")
BAD = ("grating", "rivals")

#: chance a group scene takes the place of the ordinary pair chat at the end of an outing, with 3+ along
GROUP_CHANCE = 0.4
#: the player and two recruits (a group of three): the chance of a topic or ensemble at an outing (x1.5 at a rest)
SMALL_SCENE_CHANCE = 0.25
#: campfire topics: how many recent topics are held back, and the odds the player is asked or talked about
TOPIC_MEMORY = 5
TOPIC_ASK = 0.3
TOPIC_GUESS = 0.35
#: what a reaction to someone's answer does between the two of them (small: this is chat, not an event)
REACT_MOVE = {"t_react_warm": 1.0, "t_react_laugh": 0.8, "t_react_same": 1.2, "t_react_tease": -0.6}
#: shared outings before a trio of mutual friends becomes a crew, and a four becomes a family
CREW_OUTINGS, FAMILY_OUTINGS = 6, 10
#: the perks, as a fraction of damage and healing done, while the whole crew or family is in the party
CREW_BONUS, FAMILY_BONUS = 0.03, 0.05
#: outings a pair stays sore after a call-out, and a truce lasts after rivals give each other their due
SORE_OUTINGS, TRUCE_OUTINGS = 2, 3
#: a speaker can admire someone at most once in this many outings
ADMIRE_GAP = 8
#: drifts: how far one push moves a dial, and the cap either way
DRIFT_STEP, DRIFT_CAP = 0.04, 1.0
#: a pair's story log keeps this many moments; each is called back at most twice
STORY_CAP, CALLBACK_MAX = 12, 2
#: arc progress needed for each turning point
ARC_STEPS = (3.0, 7.0, 12.0)

KINDS = ("sharp", "kind", "funny", "brave", "steady", "clever", "honest", "quiet", "fierce", "warm")
ROLES = ("instigator", "peacemaker", "mother_hen", "hype", "goblin", "quiet_one", "straight")
SHAPES = ("rise", "fray", "thaw", "voice", "settle", "let_go", "humbled", "redemption", "won_over", "slide",
          "faith", "belonging", "homesick", "burnout")
#: what moves each arc: event name -> progress
DRIVERS = {
    "rise": {"carried": 2.0, "conceded": 1.5, "saved_someone": 1.5},
    "fray": {"wipe": 1.5, "friend_left": 2.0, "crew_split": 2.5, "high_zone": 0.5},
    "thaw": {"fondness_to": 1.5, "saved": 1.5, "crew_formed": 3.0, "included": 2.0},
    "voice": {"call_out_right": 2.0, "plan_taken": 1.5, "listened": 1.5},
    "settle": {"long_stint": 1.0, "crew_formed": 2.5, "family": 3.0},
    "let_go": {"quest_done": 4.0, "fondness_to": 1.0, "confided": 1.5},
    "humbled": {"wipe": 1.0, "called_out": 1.5, "conceded": 2.0},
    "redemption": {"saved_someone": 2.0, "carried": 1.5},
    "won_over": {"fondness_to": 1.5, "saved": 2.0, "crew_formed": 2.5},
    "slide": {"wipe": 1.0, "dark_power": 1.0, "friend_left": 1.5},
    "faith": {"wipe": 1.0, "friend_left": 1.5, "quest_done": 2.0},
    "belonging": {"long_stint": 1.0, "crew_formed": 2.0, "family": 3.0},
    "homesick": {"long_stint": 0.5, "confided": 1.5, "quest_done": 2.0},
    "burnout": {"carried": 1.5, "wipe": 1.0, "fondness_to": 1.0},
}
#: events that pull an arc back (a slide caught in time, a thaw refreezing)
UNDO = {"slide": {"pulled_back": 3.0}, "thaw": {"friend_left": 2.0, "crew_split": 2.0},
        "fray": {"crew_formed": 1.5}, "burnout": {"let_others": 2.5}}

#: lines that fall back to the pair pool (data/npcs/relationships.json) when a scene borrows a pair beat
PAIR_KEYS = {"needle_any", "bite_back", "hurt", "laugh_off", "double_down", "apologise", "tease_any",
             "tease_back", "take_it_kindly", "turn_grating", "defend", "accept", "deflect"}
#: an ordinary group scene won't reuse a line any member has said in the last this many group lines
RECENT_G = 14


def _hid(rid, text):
    return f"{rid}:{zlib.crc32(text.encode('utf-8')):08x}"


def kinds_of(t):
    """What someone can be loved or hated for, from their traits. Most people are two or three things."""
    tags, out = set(t.get("is", [])), []
    if tags & {"sarcastic", "cynic"} or t.get("manner") == "blunt" or (t.get("humour") == "dry" and "posh" in tags):
        out.append("sharp")
    if tags & {"healer", "host", "patient"} or t.get("manner") == "gentle":
        out.append("kind")
    if t.get("humour") == "joker" or "showoff" in tags:
        out.append("funny")
    if t.get("pace") == "bold" or "fighter" in tags:
        out.append("brave")
    if t.get("pace") in ("careful", "steady") or "elder" in tags:
        out.append("steady")
    if tags & {"scholar", "teacher", "maker"}:
        out.append("clever")
    if "honest" in tags or t.get("humour") == "earnest":
        out.append("honest")
    if t.get("talk") == "quiet":
        out.append("quiet")
    if tags & {"competitive", "sporty"}:
        out.append("fierce")
    if t.get("talk") == "talker" or tags & {"sentimental", "young", "host"}:
        out.append("warm")
    return out or ["steady"]


#: which watcher likes/dislikes make a kind lovable or hateful (the pair system's described() words)
KIND_WORDS = {"sharp": {"sarcastic", "cynic", "blunt", "dry"}, "kind": {"gentle", "healer", "host", "patient"},
              "funny": {"funny", "joker", "showoff"}, "brave": {"reckless", "bold", "fighter"},
              "steady": {"careful", "steady", "elder"}, "clever": {"scholar", "teacher", "maker"},
              "honest": {"honest", "earnest"}, "quiet": {"quiet"}, "fierce": {"competitive", "sporty"},
              "warm": {"loud", "talker", "young", "sentimental", "host"}}


def role_scores(t):
    tags = set(t.get("is", []))
    s = dict.fromkeys(ROLES, 0.0)
    s["instigator"] += 3 * bool(tags & {"sarcastic", "cynic"}) + 2 * (t.get("manner") == "blunt") \
        + (t.get("humour") == "dry") + (t.get("humour") == "joker") + ("showoff" in tags)
    s["peacemaker"] += 2 * (t.get("manner") == "gentle") + 2 * ("patient" in tags) + bool(tags & {"host", "healer"}) \
        + ("teacher" in tags)
    s["mother_hen"] += 2 * ("host" in tags) + 2 * ("healer" in tags) + 2 * ("elder" in tags) \
        + (t.get("manner") == "gentle")
    s["hype"] += 2 * (t.get("talk") == "talker") + 2 * ("competitive" in tags) + (t.get("humour") == "joker") \
        + ("showoff" in tags) + ("sporty" in tags) + ("young" in tags)
    s["goblin"] += 2 * (t.get("pace") == "bold") + 2 * (t.get("humour") == "joker") + ("young" in tags) \
        + ("showoff" in tags)
    s["quiet_one"] += 3 * (t.get("talk") == "quiet") + (t.get("humour") == "dry")
    s["straight"] += 2 * (t.get("pace") == "careful") + 2 * (t.get("manner") == "formal") \
        + (t.get("humour") == "earnest") + ("honest" in tags)
    return s


class GroupDynamics:
    def __init__(self, rm):
        self.rm = rm                    # the RelationshipManager that owns this
        self.lines, self.arcs, self.orient, self.after = {}, {}, {}, {}
        self.crews = {}                 # key (sorted ids joined by |) -> {members, name, outings, formed, split, family}
        self.together = {}              # same key -> outings that exact set has shared
        self.drift = {}                 # rid -> {"pace": x, "talk": x, "sharp": x, "trust": x}
        self.arc_state = {}             # rid -> {"progress", "stage", "path", "failed", "changed": [..]}
        self.story = {}                 # pair key -> [moment, ...]
        self.called_back = {}           # pair key -> {moment: times}
        self.sore = {}                  # pair key -> outings left
        self.truce = {}                 # pair key -> outings left
        self.first_down = []            # rid who went down first, per recent fight
        self.admired_at = {}            # rid -> outing count when they last admired someone
        self.noticed = []               # one-off notices already played ("open:rid", "changed:rid:kind")
        self.recent = []                # line ids in the last few group scenes
        self.outings = 0
        self.last_mood = "easy"
        self.topics, self.ensembles = [], []
        self.topics_heard = []          # campfire topic ids, most recent last
        self.ensembles_heard = []       # written ensembles already played (each plays once)
        self._fill = {}                 # extra placeholders for the beat being built ({topic})
        self._load()

    def _load(self):
        try:
            raw = json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        self.lines = raw.get("lines") or {}
        self.arcs = raw.get("arcs") or {}
        self.orient = raw.get("orientation") or {}
        self.topics = raw.get("topics") or []
        self.ensembles = raw.get("ensembles") or []

    # ------------------------------------------------------------------ basics
    def t(self, rid):
        """Traits with the person's drifts folded in (a careful one grown braver reads as steadier)."""
        base = dict(self.rm._t(rid))
        d = self.drift.get(rid) or {}
        if d.get("pace", 0) >= 0.6 and base.get("pace") == "careful":
            base["pace"] = "steady"
        if d.get("talk", 0) >= 0.6 and base.get("talk") == "quiet":
            base["talk"] = "middle"
        if d.get("sharp", 0) <= -0.6:
            base["is"] = [x for x in base.get("is", []) if x not in ("cynic", "sarcastic")]
        return base

    def has(self, rid):
        return bool(self.lines.get(rid))

    def ids(self, ids):
        return [i for i in ids if self.has(i)]

    @staticmethod
    def key(ids):
        return "|".join(sorted(ids))

    def state(self, a, b):
        return self.rm.state(a, b)

    def first(self, rid):
        return self.rm.first(rid)

    # ------------------------------------------------------------------ lines
    def line_opts(self, rid, key):
        """A recruit's options for a key: their "after" version once their arc has changed them, else their own,
        else (for borrowed pair beats) their pair line."""
        st = self.arc_state.get(rid) or {}
        mine = self.lines.get(rid) or {}
        if st.get("stage", 0) >= 3 and not st.get("failed") and mine.get(key + "_after"):
            t = mine[key + "_after"]
        elif st.get("failed") and mine.get(key + "_failed"):
            t = mine[key + "_failed"]
        else:
            t = mine.get(key)
        if not t and key in PAIR_KEYS:
            t = (self.rm.lines.get(rid) or {}).get(key)
        if not t:
            return []
        return t if isinstance(t, list) else [t]

    def can(self, rid, key):
        return bool(self.line_opts(rid, key))

    def beat(self, parts, priority=1, ask=None, pair=None):
        """parts: [(rid, key)] or [(rid, key, name_of)]. Queues one scene on the pair system's queue. Every line
        must exist; the opener mustn't have been heard lately. ask: an argument the player is pulled into."""
        out, ids = [], []
        for p in parts:
            rid, key = p[0], p[1]
            who = p[2] if len(p) > 2 else None
            opts = self.line_opts(rid, key)
            if not opts:
                return False
            fresh = [o for o in opts if _hid(rid, o) not in self.recent]
            raw = random.choice(fresh or opts)
            ids.append(_hid(rid, raw))
            text = raw.replace("{name}", self.first(who) if who else "")
            if who and (key.startswith("g_love_") or key.startswith("g_hate_")) and "{name}" not in raw:
                # these are said to one person; with three or four people listening, say whose it is
                keep = text.startswith(("I ", "I'"))
                text = f"{self.first(who)}, {text if keep else text[0].lower() + text[1:]}"
            text = text.replace("{player}", self._player_name())
            for k, v in self._fill.items():
                text = text.replace("{" + k + "}", v)
            out.append((rid, self.rm.address(text, who)))
        if priority <= 1 and ids[0] in self.recent:
            return False
        self.recent = (self.recent + ids)[-RECENT_G:]
        item = (priority, self.rm._deeds(), out) if ask is None else (priority, self.rm._deeds(), out, ask)
        self.rm.queue.append(item)
        self.rm.queue.sort(key=lambda q: -q[0])
        self.rm.queue = self.rm.queue[:3]
        for rid, text in out:
            self.rm.log.append((rid, text))
        self.rm.log = self.rm.log[-60:]
        return True

    def _player_name(self):
        """The player character's first name (the party's first member is always the player)."""
        try:
            party = getattr(self.rm.bm, "party", None)
            name = party.members[0].name.split()[0]
            return name or "Boss"
        except Exception:
            return "Boss"

    def move(self, a, b, amount):
        r = self.rm.rel(a, b)
        self.rm._milestone(r, self.rm._move(r, amount))
        return r

    # ------------------------------------------------------------------ who's in the room
    def room(self, rid, ids):
        """How rid comes across with this company: a speaking weight multiplier and the shifts that go with it."""
        others = [x for x in ids if x != rid]
        t = self.t(rid)
        close = [x for x in others if self.state(rid, x) == "close"]
        good = [x for x in others if self.state(rid, x) in GOOD]
        rivals = [x for x in others if self.state(rid, x) == "rivals"]
        wary = [x for x in others if x in t.get("wary_of", []) or self.state(rid, x) == "grating"]
        warm = [x for x in others if x in t.get("warm_to", []) or self.state(rid, x) == "close"]
        strangers = [x for x in others if self.state(rid, x) in ("strangers", "nodding")]
        weight, sharp, confident = 1.0, 0.0, 0.0
        clipped = unguarded = False
        quiet = t.get("talk") == "quiet"
        if others and len(strangers) >= len(others) - 0.0001 * 0 and len(strangers) * 2 > len(others):
            weight *= 0.33 if quiet else 1.15
            clipped = quiet
        if len(close) >= 2:
            weight *= 3.0 if quiet else 1.3
            unguarded, confident = True, 1.0
        elif good:
            weight *= 1.2
        if rivals:
            sharp += 2.0 if ("sharp" in kinds_of(t)) else 0.0
            if t.get("manner") == "gentle":
                weight *= 0.7
                clipped = True
        if wary:
            weight *= 0.75
            clipped = True
            confident -= 1.0
        if warm:
            weight *= 1.15
        key = self.key(ids)
        if key in self.crews and self.crews[key].get("formed") and not self.crews[key].get("split"):
            confident += 1.0
        talkw = {"talker": 1.6, "middle": 1.0, "quiet": 0.55}.get(t.get("talk"), 1.0)
        return {"weight": max(0.15, min(3.0, talkw * weight)), "sharp": sharp, "confident": confident,
                "clipped": clipped, "unguarded": unguarded}

    def describe_room(self, rid, ids):
        """The room profile in words, for the Friendship Test panel."""
        r = self.room(rid, ids)
        bits = []
        if r["unguarded"]:
            bits.append("at ease with their closest")
        elif r["weight"] >= 1.5:
            bits.append("chatty in this company")
        elif r["weight"] <= 0.5:
            bits.append("barely talking")
        if r["sharp"]:
            riv = [self.first(x) for x in ids if x != rid and self.state(rid, x) == "rivals"]
            bits.append(f"sharper than usual ({', '.join(riv)} is here)")
        if r["clipped"] and r["weight"] > 0.5:
            wary = [self.first(x) for x in ids if x != rid and self.state(rid, x) in BAD]
            bits.append(f"on edge around {', '.join(wary)}" if wary else "guarded")
        return ", ".join(bits) or "themselves"

    def pick(self, ids, role, exclude=(), need=None):
        """Who in the room plays this role now: trait score, room shifts and some luck. need: a key they must have."""
        cand = [x for x in ids if x not in exclude and (need is None or self.can(x, need))]
        if not cand:
            return None
        ws = []
        for x in cand:
            rs = role_scores(self.t(x))[role]
            rm = self.room(x, ids)
            w = (0.5 + rs) * rm["weight"]
            if role == "instigator":
                w += rm["sharp"]
            if role in ("hype", "goblin"):
                w *= max(0.4, 1.0 + 0.3 * rm["confident"])
            if role == "straight":
                w *= max(0.4, 1.0 - 0.2 * rm["confident"])
            ws.append(max(0.05, w))
        return random.choices(cand, weights=ws)[0]

    def clip_or(self, rid, ids, key):
        """A guarded person says their clipped line instead, now and then."""
        if self.room(rid, ids)["clipped"] and self.can(rid, "g_clipped") and random.random() < 0.5:
            return "g_clipped"
        return key

    # ------------------------------------------------------------------ the party's mood
    def mood(self, ids):
        ids = self.ids(ids)
        if len(ids) < 3:
            return "small"
        pairs = self.rm.pairs_in(ids)
        st = {p: self.state(*p) for p in pairs}
        if len(ids) == 4 and self.crews.get(self.key(ids), {}).get("family"):
            return "family"
        if any(s == "rivals" for s in st.values()):
            return "powder_keg"
        good = [p for p, s in st.items() if s in GOOD]
        bad = [p for p, s in st.items() if s in BAD]
        if len(good) >= 2 and len(bad) >= 2:
            # two good pairs that are bad to each other: two camps
            for g1 in good:
                for g2 in good:
                    if set(g1) & set(g2):
                        continue
                    if all(self.state(x, y) in BAD for x in g1 for y in g2):
                        return "split_camp"
        for trio in self._trios(ids):
            crew = self.crews.get(self.key(trio))
            if crew and crew.get("formed") and not crew.get("split"):
                rest = [x for x in ids if x not in trio]
                if not rest:
                    return "crew"
                if all(self.state(r, m) not in GOOD for r in rest for m in trio):
                    return "third_wheel"
                return "crew"
        close_pairs = [p for p, s in st.items() if s == "close"]
        for p in close_pairs:
            rest = [x for x in ids if x not in p]
            if any(all(self.state(r, m) not in GOOD for m in p) for r in rest):
                return "third_wheel"
        wild = [x for x in ids if self.t(x).get("humour") == "joker" or self.t(x).get("pace") == "bold"]
        anchor = [x for x in ids if self.t(x).get("pace") == "careful" or self.t(x).get("manner") == "formal"]
        if len(wild) >= 2 and not anchor:
            return "chaos"
        return "easy"

    @staticmethod
    def _trios(ids):
        ids = sorted(ids)
        return [(ids[i], ids[j], ids[k]) for i in range(len(ids)) for j in range(i + 1, len(ids))
                for k in range(j + 1, len(ids))]

    MOOD_NAMES = {"family": "Found family", "crew": "A crew", "third_wheel": "A crew and a third wheel",
                  "split_camp": "Split into camps", "powder_keg": "A powder keg", "chaos": "Chaos crew",
                  "easy": "Easy company", "small": "Too few for a group"}

    # ------------------------------------------------------------------ hooks from the road
    def on_outing(self, ids, kind="quest", zone=None):
        """After the pair system's own outing. Returns True if a group scene took the ambient chat's place."""
        ids = self.ids(ids)
        self.outings += 1
        self._tick_timers()
        if len(ids) >= 3:
            self._count_together(ids, zone)
        for rid in ids:
            self.push(rid, "long_stint", 0.25)
        self._drift_from_company(ids)
        if len(ids) == 2 and random.random() < SMALL_SCENE_CHANCE and self._small_scene(ids, "outing"):
            return True
        if len(ids) < 3 and not self._pair_growth(ids):
            return False
        played = self._milestones(ids)
        if played:
            return True
        if self._growth_beats(ids):
            return True
        if len(ids) >= 3 and random.random() < GROUP_CHANCE:
            return self.scene(ids, "outing")
        return False

    def on_rest(self, ids):
        ids = self.ids(ids)
        if len(ids) == 2:
            return random.random() < SMALL_SCENE_CHANCE * 1.5 and self._small_scene(ids, "rest")
        if len(ids) < 3:
            return False
        m = self.mood(ids)
        if m in ("family", "crew", "easy") and random.random() < 0.5:
            return self._toast(ids)
        if random.random() < 0.3:
            return self.scene(ids, "rest")
        return False

    def on_dungeon(self, ids):
        ids = self.ids(ids)
        if len(ids) >= 2:
            return self._hype(ids)
        return False

    def on_wipe(self, ids, first_down=None):
        ids = self.ids(ids)
        self.first_down = (self.first_down + [first_down])[-3:]
        for rid in ids:
            self.push(rid, "wipe")
        if first_down and self._call_out(ids, first_down, "first_down"):
            return True
        if len(ids) >= 2:
            return self._after_wipe(ids)
        return False

    def on_fight_won(self, ids, first_down=None, standing=None, saves=None, boss=False):
        """A fight ended in a win. standing: party members still up. saves: [(saver, saved)] that stopped a death."""
        ids = self.ids(ids)
        self.first_down = (self.first_down + [first_down])[-3:]
        if standing is not None:
            up = [x for x in self.ids(standing)]
            if len(up) == 2 and len(ids) >= 3 and self.state(*up) in BAD:
                if self._respect(up[0], up[1], "clutch"):
                    return True
        for saver, saved in saves or []:
            if saver in ids and saved in ids:
                self.log_story(saver, saved, "save")
                self.push(saver, "saved_someone")
                self.push(saved, "saved")
                if self.state(saver, saved) in BAD:
                    if self._respect(saved, saver, "save"):
                        return True
                elif self._fondness(saved, saver, trigger="save"):
                    return True
        if first_down and self.first_down[-2:] == [first_down, first_down]:
            if self._call_out(ids, first_down, "first_down"):
                return True
        if boss:
            for a, b in self.rm.pairs_in(ids):
                if self.state(a, b) in BAD and random.random() < 0.4:
                    if self._respect(a, b, "boss"):
                        return True
        return False

    def on_close_call(self, ids, hurt):
        ids = self.ids(ids)
        for h in hurt:
            if h not in ids:
                continue
            healers = [x for x in ids if x != h and "healer" in self.t(x).get("is", [])]
            for x in healers:
                self.log_story(x, h, "save")
                self.push(x, "carried")
            if healers and random.random() < 0.5:
                return self._fondness(h, random.choice(healers), trigger="save")
        return False

    def on_left(self, rid, ids):
        for x in self.ids(ids):
            if x != rid and self.state(rid, x) in GOOD:
                self.push(x, "friend_left")
        for key, c in self.crews.items():
            if rid in c["members"] and c.get("formed"):
                pass                    # a crew isn't split by one of them going home; only by falling out

    def on_gear_moved(self, giver, taker):
        if self.has(giver) and self.has(taker) and self.state(giver, taker) in GOOD:
            self.log_story(giver, taker, "gear")

    # ------------------------------------------------------------------ timers, counts, crews
    def _tick_timers(self):
        for table in (self.sore, self.truce):
            for k in list(table):
                table[k] -= 1
                if table[k] <= 0:
                    del table[k]
                    if table is self.sore:
                        self._concede(k)

    def _count_together(self, ids, zone):
        for n in (3, 4):
            if len(ids) < n:
                continue
            for combo in (self._trios(ids) if n == 3 else [tuple(sorted(ids))] if len(ids) == 4 else []):
                k = self.key(combo)
                self.together[k] = self.together.get(k, 0) + 1
                c = self.crews.get(k)
                if c is None:
                    self.crews[k] = c = {"members": list(combo), "name": None, "outings": 0, "formed": False,
                                         "split": False, "family": False, "zone": zone}
                c["outings"] = self.together[k]
                if zone and not c.get("formed"):
                    c["zone"] = zone

    def _milestones(self, ids):
        """A crew forming, splitting or coming back together; a family forming."""
        for combo in self._trios(ids) + ([tuple(sorted(ids))] if len(ids) == 4 else []):
            k = self.key(combo)
            c = self.crews.get(k)
            if not c:
                continue
            pairs = self.rm.pairs_in(combo)
            all_good = all(self.state(*p) in GOOD for p in pairs)
            if len(combo) == 3:
                if not c["formed"] and all_good and c["outings"] >= CREW_OUTINGS:
                    # a crew that overlaps one already formed (two of the same people) joins it quietly: in a party
                    # of four, four trios can form, and only the first deserves the toast
                    overlap = next((o for o in self.crews.values() if o is not c and o.get("formed")
                                    and len(set(o["members"]) & set(combo)) >= 2), None)
                    c["formed"] = True
                    c["name"] = overlap["name"] if overlap and overlap.get("name") else self._crew_name(c, 3)
                    for m in combo:
                        self.push(m, "crew_formed")
                    self._story_all(combo, "crew")
                    if overlap:
                        continue
                    return self._crew_scene(combo, "formed")
                if c["formed"] and not c["split"] and any(self.state(*p) in BAD for p in pairs):
                    c["split"] = True
                    for m in combo:
                        self.push(m, "crew_split")
                    return self._crew_scene(combo, "split")
                if c["formed"] and c["split"] and all_good:
                    c["split"] = False
                    self._story_all(combo, "reunited")
                    return self._crew_scene(combo, "back")
            else:
                close = sum(1 for p in pairs if self.state(*p) == "close")
                if not c["family"] and all_good and close >= 3 and c["outings"] >= FAMILY_OUTINGS:
                    c["family"], c["formed"] = True, True
                    c["name"] = self._crew_name(c, 4)
                    for m in combo:
                        self.push(m, "family")
                    self._story_all(combo, "family")
                    return self._family_toast(list(combo))
        return False

    def _crew_name(self, c, n):
        zone = c.get("zone") or "Road"
        for cut in (" North", " South", " East", " West", " Central", "Northern ", "Southern ", "Eastern ",
                    "Western ", "Central "):
            zone = zone.replace(cut, "")
        return f"The {zone.strip()} {'Three' if n == 3 else 'Four'}"

    def crew_bonus(self, rid, party_ids):
        """The perk: the biggest of the crews and families rid belongs to that are all in the party now."""
        here = set(party_ids)
        best = 0.0
        for c in self.crews.values():
            if rid in c["members"] and c.get("formed") and not c.get("split") and set(c["members"]) <= here:
                best = max(best, FAMILY_BONUS if c.get("family") else CREW_BONUS)
        return best

    def family_softens_wipes(self, rid, party_ids):
        here = set(party_ids)
        return any(rid in c["members"] and c.get("family") and set(c["members"]) <= here for c in self.crews.values())

    def mood_effect(self, ids):
        """Extra mood per outing on top of the pair system's: a crew or family lifts it, a powder keg wears it."""
        m = self.mood(ids)
        return {"family": 2.0, "crew": 2.0, "powder_keg": -2.0}.get(m, 0.0)

    # ------------------------------------------------------------------ growth: story, drifts, arcs
    def log_story(self, a, b, moment):
        k = self.rm.key(a, b)
        log = self.story.setdefault(k, [])
        if moment not in log:
            log.append(moment)
        self.story[k] = log[-STORY_CAP:]

    def _story_all(self, ids, moment):
        for a, b in self.rm.pairs_in(ids):
            self.log_story(a, b, moment)

    def push(self, rid, event, amount=None):
        """Something happened that can move rid's arc."""
        arc = self.arcs.get(rid) or {}
        if not arc or arc.get("anchor"):
            return
        st = self.arc_state.setdefault(rid, {"progress": 0.0, "stage": 0, "path": "primary", "failed": False,
                                             "changed": [], "fail": 0.0})
        if st.get("stage", 0) >= 3 or st.get("failed"):
            return
        shape = arc.get("alt") if st["path"] == "alt" else arc.get("shape")
        gain = DRIVERS.get(shape, {}).get(event)
        if amount is not None and gain:
            gain = amount
        if gain:
            st["progress"] += gain
        back = UNDO.get(shape, {}).get(event)
        if back:
            st["progress"] = max(0.0, st["progress"] - back)
        # a recruit who can go two ways tips onto the alternate path if the alternate's driver keeps coming
        alt = arc.get("alt")
        if alt and st["path"] == "primary" and st["stage"] == 0:
            ag = DRIVERS.get(alt, {}).get(event, 0)
            st["alt_pull"] = st.get("alt_pull", 0.0) + ag
            if st["alt_pull"] >= ARC_STEPS[0] + 1 and st["alt_pull"] > st["progress"]:
                st["path"], st["progress"] = "alt", st["alt_pull"]
        # failing: the arc's fail condition (UNDO events) piling up after the turn
        if back and st["stage"] >= 2:
            st["fail"] = st.get("fail", 0.0) + back
            if st["fail"] >= 6.0 and self.can(rid, "arc_failed"):
                st["failed"], st["due"] = True, "arc_failed"
                return
        while st["stage"] < 3 and st["progress"] >= ARC_STEPS[st["stage"]]:
            st["stage"] += 1
            st["due"] = ("arc_cracks", "arc_turn", "arc_become")[st["stage"] - 1]
            if st["path"] == "alt":
                st["due"] = {"arc_cracks": "arc_cracks", "arc_turn": "alt_turn", "arc_become": "alt_become"}[st["due"]]

    def _drift_from_company(self, ids):
        for rid in ids:
            others = [x for x in ids if x != rid]
            t = self.rm._t(rid)
            d = self.drift.setdefault(rid, {"pace": 0.0, "talk": 0.0, "sharp": 0.0, "trust": 0.0})
            if t.get("pace") == "careful":
                bold_friends = [x for x in others if self.rm._t(x).get("pace") == "bold" and self.state(rid, x) in GOOD]
                if bold_friends:
                    d["pace"] = min(DRIFT_CAP, d["pace"] + DRIFT_STEP)
            if t.get("talk") == "quiet":
                if sum(1 for x in others if self.state(rid, x) in GOOD) >= 2:
                    d["talk"] = min(DRIFT_CAP, d["talk"] + DRIFT_STEP)
            if set(t.get("is", [])) & {"cynic", "sarcastic"}:
                key = self.key(ids)
                if self.crews.get(key, {}).get("family"):
                    d["sharp"] = max(-DRIFT_CAP, d["sharp"] - DRIFT_STEP)
            for change, test in (("braver", d["pace"] >= 0.6), ("talks_more", d["talk"] >= 0.6),
                                 ("softer", d["sharp"] <= -0.6)):
                tag = f"changed:{rid}:{change}"
                if test and tag not in self.noticed and self.can(rid, "g_changed"):
                    self.noticed.append(tag)
                    self.arc_state.setdefault(rid, {"progress": 0.0, "stage": 0, "path": "primary", "failed": False,
                                                    "changed": [], "fail": 0.0})
                    self.arc_state[rid].setdefault("pending", []).append("g_changed")

    def describe_drift(self, rid):
        d = self.drift.get(rid) or {}
        out = []
        if d.get("pace", 0) >= 0.3:
            out.append("braver than they were")
        if d.get("talk", 0) >= 0.3:
            out.append("talks more these days")
        if d.get("sharp", 0) <= -0.3:
            out.append("softer round the edges")
        if d.get("trust", 0) <= -0.3:
            out.append("slower to trust")
        st = self.arc_state.get(rid) or {}
        arc = self.arcs.get(rid) or {}
        if arc.get("anchor"):
            out.append("an anchor")
        elif arc:
            shape = arc.get("alt") if st.get("path") == "alt" else arc.get("shape")
            stage = ("not started", "cracks showing", "turning", "changed")[min(3, st.get("stage", 0))]
            out.append(f"{shape.replace('_', ' ')}: {'failed' if st.get('failed') else stage}")
        return ", ".join(out) or "the same as ever"

    def _growth_beats(self, ids):
        """An arc turning point or a noticed change that's due, said with somebody here to hear it."""
        for rid in ids:
            st = self.arc_state.get(rid) or {}
            due = st.get("due")
            if due:
                other = self._closest(rid, ids)
                parts = [(rid, due)]
                reply = None
                if other:
                    reply = (other, "g_noticed_open") if due == "arc_become" and self.can(other, "g_noticed_open") \
                        else (other, "g_quiet_line") if self.can(other, "g_quiet_line") else None
                anchors = [x for x in ids if x != rid and (self.arcs.get(x) or {}).get("anchor")
                           and self.can(x, "anchor_notice")]
                if due in ("arc_become", "alt_become") and anchors:
                    reply = (anchors[0], "anchor_notice")
                if reply:
                    parts.append(reply)
                if self.beat(parts, priority=3):
                    st["due"] = None
                    st.setdefault("changed", []).append(due)
                    try:
                        from world.conversations import get_conversations
                        get_conversations().want(rid, "development", reason=due)
                    except Exception:
                        pass
                    return True
            for p in list(st.get("pending", [])):
                if self.beat([(rid, p)] + ([(self._closest(rid, ids), "g_noticed_open")]
                                           if self._closest(rid, ids) and p == "g_changed"
                                           and self.can(self._closest(rid, ids), "g_noticed_open") else []),
                             priority=2):
                    st["pending"].remove(p)
                    return True
        # a quiet one opening up with their two closest, noticed once
        for rid in ids:
            rm = self.room(rid, ids)
            tag = f"open:{rid}"
            if rm["unguarded"] and self.rm._t(rid).get("talk") == "quiet" and tag not in self.noticed:
                friend = self._closest(rid, ids)
                if friend and self.beat([(rid, "g_unguarded"), (friend, "g_noticed_open")], priority=2):
                    self.noticed.append(tag)
                    return True
        return False

    def _pair_growth(self, ids):
        """Even two recruits can have callbacks, call-outs and growth beats; only the group scenes need three."""
        return len(ids) >= 2

    def _closest(self, rid, ids):
        best, score = None, -999
        for x in ids:
            if x == rid:
                continue
            a = self.rm.rel(rid, x).affinity
            if a > score:
                best, score = x, a
        return best

    # ------------------------------------------------------------------ the scenes
    def scene(self, ids, when="outing"):
        """One group scene picked for the mood and the moment. Each scene returns False if its lines aren't there."""
        m = self.mood(ids)
        self.last_mood = m
        options = []
        options += [("roast", 3)]
        options += [("plan", 2)]
        options += [("riff", 4 if m == "chaos" else 1)]
        options += [("bicker", 4 if m in ("powder_keg", "split_camp") else 1)]
        options += [("third", 4 if m == "third_wheel" else 0)]
        options += [("fond", 2 if m in ("crew", "family", "easy") else 1)]
        options += [("dig", 3 if m in ("powder_keg", "split_camp") else 1)]
        options += [("admire", 1)]
        options += [("callback", 2)]
        options += [("argue", 2)]
        options += [("topic", 4 if when == "rest" else 2)]
        options += [("ensemble", 5)]
        if when == "rest":
            options += [("toast", 3)]
        random.shuffle(options)
        options.sort(key=lambda o: -o[1] * random.random())
        for name, w in options:
            if w <= 0:
                continue
            if (self._topic(ids, when) if name == "topic" else getattr(self, f"_{name}")(ids)):
                return True
        return False

    # ------------------------------------------------------------------ scenes with the player in them
    # (Kyle, 27 Nov 2026: "Are there inter-party conversations with groups of 3, 4, and 5 (player included)" /
    # "we dont need to always respond, but more mention of us during some of the interactions". A party of the
    # player and two recruits is a group of three, so these play from two recruits up.)
    def _small_scene(self, ids, when):
        """The player and two recruits: a written ensemble for these two if there is one, else a campfire topic."""
        return self._ensemble(ids) or self._topic(ids, when)

    def _topic(self, ids, when="outing"):
        """A campfire question: somebody raises it, two or three answer in their own words, somebody reacts to
        somebody else's answer (warmly, or not), and the player is asked, or talked about, or neither."""
        fresh = [tp for tp in self.topics if tp["id"] not in self.topics_heard[-TOPIC_MEMORY:]
                 and when in (tp.get("when") or ["rest", "outing"])]
        random.shuffle(fresh)
        for tp in fresh:
            key = "topic_" + tp["id"]
            who = [x for x in ids if self.can(x, key)]
            if len(who) < 2:
                continue
            raiser = self.pick(who, "instigator", need="t_raise")
            if not raiser:
                continue
            rest = [x for x in who if x != raiser]
            random.shuffle(rest)
            answer = [raiser] + rest[:2]
            parts = [(raiser, "t_raise")] + [(x, key) for x in answer]
            # somebody reacts to somebody else's answer, and it isn't always kind. Only a person who hasn't answered
            # yet can say "that's mine too" (t_react_same): it's the answer they'd have given
            quiet = [x for x in ids if x not in answer]
            if quiet and random.random() < 0.4:
                r, a = random.choice(quiet), random.choice(answer)
            else:
                r, a = random.sample(answer, 2)
            react = self._react_key(r, a, can_same=r not in answer)
            if self.can(r, react):
                parts.append((r, react, a))
            ask = None
            roll = random.random()
            if roll < TOPIC_ASK:
                asker = random.choice(answer)
                if self.can(asker, "t_ask_player"):
                    parts.append((asker, "t_ask_player"))
                    ask = {"kind": "topic", "topic": tp["id"], "asker": asker, "witnesses": list(ids)}
            elif roll < TOPIC_ASK + TOPIC_GUESS:
                g = random.choice(answer)
                if self.can(g, "t_guess_player"):
                    parts.append((g, "t_guess_player"))
            self._fill = {"topic": tp["question"]}
            try:
                ok = self.beat(parts, priority=2, ask=ask)    # topics_heard keeps them from repeating
            finally:
                self._fill = {}
            if not ok:
                continue
            self.topics_heard = (self.topics_heard + [tp["id"]])[-12:]
            self.move(r, a, REACT_MOVE.get(react, 0))
            for x in answer:
                for y in answer:
                    if x < y and self.state(x, y) not in BAD:
                        self.move(x, y, 0.3)    # sitting round a fire telling stories, the small warmth of it
            return True
        return False

    def _react_key(self, r, a, can_same=False):
        """How r takes a's answer: by where they stand, and by r's own manner. Friends tease too."""
        st = self.state(r, a)
        t = self.t(r)
        if st in BAD:
            w = {"t_react_tease": 6, "t_react_laugh": 1, "t_react_same": 0.5, "t_react_warm": 0.2}
        elif st in GOOD:
            w = {"t_react_warm": 3, "t_react_laugh": 3, "t_react_same": 2, "t_react_tease": 2}
        else:
            w = {"t_react_tease": 3, "t_react_laugh": 2, "t_react_same": 1.5, "t_react_warm": 1}
        if t.get("humour") in ("dry", "joker") or "sarcastic" in t.get("is", []):
            w["t_react_tease"] *= 1.6
        if t.get("manner") == "gentle":
            w["t_react_warm"] *= 1.6
            w["t_react_tease"] *= 0.6
        if not can_same:
            w.pop("t_react_same")
        keys = list(w)
        return random.choices(keys, weights=[w[k] for k in keys])[0]

    def _ensemble(self, ids):
        """A written conversation for exactly these people, or some of them: two to four recruits and the player.
        Each plays once. Some stop for the player's answer; most just talk about them."""
        here = set(ids)
        fits = [e for e in self.ensembles if e["id"] not in self.ensembles_heard and set(e["cast"]) <= here]
        if not fits:
            return False
        fits.sort(key=lambda e: -len(e["cast"]))       # the biggest scene this party can play
        e = fits[0] if random.random() < 0.7 else random.choice(fits)
        rows = []
        name = self._player_name()
        for rid, text in e["lines"]:
            rows.append((rid, self.rm.address(text.replace("{player}", name), None)))
        ask = None
        ch = e.get("choice")
        if ch:
            ask = {"kind": "ensemble", "ensemble": e["id"], "asker": ch["asker"], "witnesses": list(ids)}
        item = (2, self.rm._deeds(), rows) if ask is None else (2, self.rm._deeds(), rows, ask)
        self.rm.queue.append(item)
        self.rm.queue.sort(key=lambda q: -q[0])
        self.rm.queue = self.rm.queue[:3]
        for rid, text in rows:
            self.rm.log.append((rid, text))
        self.rm.log = self.rm.log[-60:]
        self.ensembles_heard.append(e["id"])
        for a in e["cast"]:
            for b in e["cast"]:
                if a < b:
                    self.move(a, b, float(e.get("affinity", 0)))
        return True

    def _roast(self, ids):
        i = self.pick(ids, "instigator", need="g_roast")
        if not i:
            return False
        f = self.pick(ids, "hype", exclude=(i,), need="g_fire_back")
        if not f:
            return False
        third = [x for x in ids if x not in (i, f)]
        parts = [(i, "g_roast"), (f, self.clip_or(f, ids, "g_fire_back"))]
        if third:
            p = third[0]
            parts.append((p, "g_pile_on" if random.random() < 0.6 else "g_quiet_line"))
        if self.beat(parts):
            for x in ids:
                if x != i:
                    self.move(i, x, 0.8 if self.state(i, x) in GOOD else 0.3)
            return True
        return False

    def _plan(self, ids):
        g = self.pick(ids, "goblin", need="g_bad_plan")
        if not g:
            return False
        y = self.pick(ids, "hype", exclude=(g,), need="g_plan_yes")
        n = self.pick(ids, "straight", exclude=(g, y), need="g_plan_no")
        if not y or not n:
            return False
        close = (n, "g_exasperated") if self.can(n, "g_exasperated") and random.random() < 0.5 else None
        parts = [(g, "g_bad_plan"), (y, "g_plan_yes"), (n, self.clip_or(n, ids, "g_plan_no"))]
        if close:
            parts.append(close)
        if self.beat(parts):
            self.move(g, y, 1.0)
            if self.state(n, g) in GOOD:
                self.push(n, "listened")
            return True
        return False

    def _riff(self, ids):
        g = self.pick(ids, "goblin", need="g_bad_plan")
        if not g:
            return False
        yes = [x for x in ids if x != g and self.can(x, "g_plan_yes")
               and (self.t(x).get("humour") == "joker" or self.t(x).get("pace") == "bold")]
        straight = self.pick(ids, "straight", exclude=[g] + yes[:2], need="g_exasperated")
        if not yes or not straight:
            return False
        parts = [(g, "g_bad_plan")] + [(x, "g_plan_yes") for x in yes[:2]] + [(straight, "g_exasperated")]
        if self.beat(parts):
            for x in yes[:2]:
                self.move(g, x, 1.2)
            return True
        return False

    def _hype(self, ids):
        h = self.pick(ids, "hype", need="g_hype")
        if not h:
            return False
        others = [x for x in ids if x != h]
        if not others:
            return False
        o = random.choice(others)
        reply = "g_plan_yes" if self.t(o).get("humour") in ("joker", "earnest") else "g_quiet_line"
        return self.beat([(h, "g_hype"), (o, reply)], priority=2)

    def _toast(self, ids):
        tst = self.pick(ids, "mother_hen", need="g_toast")
        if not tst:
            return False
        rest = [x for x in ids if x != tst and self.can(x, "g_cheers")]
        if not rest:
            return False
        random.shuffle(rest)
        parts = [(tst, "g_toast")] + [(x, "g_cheers") for x in rest[:2]]
        q = [x for x in ids if x not in (tst,) and self.t(x).get("talk") == "quiet" and self.can(x, "g_quiet_line")]
        if q and random.random() < 0.4:
            parts.append((q[0], "g_quiet_line"))
        if self.beat(parts, priority=2):
            for x in rest[:2]:
                self.move(tst, x, 1.0)
            return True
        return False

    def _after_wipe(self, ids):
        a = self.pick(ids, "mother_hen", need="g_after_wipe")
        b = self.pick(ids, "instigator", exclude=(a,), need="g_after_wipe")
        if not a or not b:
            return False
        parts = [(a, "g_after_wipe"), (b, "g_after_wipe")]
        c = [x for x in ids if x not in (a, b)]
        if c:
            parts.append((c[0], "g_quiet_line" if self.can(c[0], "g_quiet_line") else "g_exasperated"))
        return self.beat(parts, priority=2)

    def _bicker(self, ids):
        bad = [(a, b) for a, b in self.rm.pairs_in(ids) if self.state(a, b) in BAD
               and self.rm.key(a, b) not in self.truce]
        if not bad:
            return False
        a, b = random.choice(bad)
        c = [x for x in ids if x not in (a, b)]
        if not c:
            return False
        c = c[0]
        good_a, good_b = self.state(c, a) in GOOD, self.state(c, b) in GOOD
        parts = [(a, "needle_any"), (b, "bite_back")]
        if (good_a and good_b) or (self.t(c).get("manner") == "gentle" and not (good_a or good_b)):
            parts.append((c, "g_peacemake"))
            calm = True
        else:
            side = a if good_a else b if good_b else None
            if side is None:
                parts.append((c, "g_quiet_line"))
                calm = False
            else:
                other = b if side == a else a
                parts += [(c, "g_take_side"), (other, "g_fire_back")]
                calm = False
        if self.beat(parts):
            self.move(a, b, 0.5 if calm else -1.5)
            if not calm and len(parts) == 5:
                side = parts[3][0] if False else (a if good_a else b)
                other = b if side == a else a
                self.move(c, side, 1.5)
                self.move(c, other, -1.5)       # hate spreads: backing a friend sours you on their rival
            return True
        return False

    def _third(self, ids):
        for a, b in self.rm.pairs_in(ids):
            if self.state(a, b) != "close" and not self._crew_with(a, b, ids):
                continue
            rest = [x for x in ids if x not in (a, b) and self.state(x, a) not in GOOD and self.state(x, b) not in GOOD]
            if not rest:
                continue
            out = rest[0]
            inc = min((a, b), key=lambda x: -role_scores(self.t(x))["peacemaker"])
            parts = [(a, "tease_any", b), (b, "tease_back", a), (out, self.clip_or(out, ids, "g_left_out")),
                     (inc, "g_include")]
            if self.beat(parts):
                self.move(inc, out, 2.0)
                self.push(out, "included")
                return True
        return False

    def _crew_with(self, a, b, ids):
        return any(a in c["members"] and b in c["members"] and c.get("formed") and set(c["members"]) <= set(ids)
                   for c in self.crews.values())

    def _fondness(self, a, b, trigger=None):
        """a tells b what they love about them: the kind picked from what b just did, or what a likes."""
        if not (self.has(a) and self.has(b)) or self.rm.key(a, b) in self.sore:
            return False
        if self.state(a, b) in BAD:
            return False
        kinds = kinds_of(self.t(b))
        likes = set(self.rm._t(a).get("likes", []))
        if trigger == "save":
            pref = ["kind", "steady", "brave"]
        elif trigger == "joke":
            pref = ["funny"]
        elif trigger == "call_out":
            pref = ["sharp", "honest"]
        else:
            pref = [k for k in KINDS if KIND_WORDS[k] & likes]
        chosen = next((k for k in pref if k in kinds and self.can(a, f"g_love_{k}")), None)
        if chosen is None:
            chosen = next((k for k in kinds if self.can(a, f"g_love_{k}")), None)
        if chosen is None or not self.can(b, "g_loved"):
            return False
        parts = [(a, f"g_love_{chosen}", b), (b, "g_loved", a)]
        if self.beat(parts, priority=2):
            contrast = self._contrast(a, b)
            self.move(a, b, 2.5 + (1.5 if contrast and self.state(a, b) in GOOD else 0))
            self.push(b, "fondness_to")
            return True
        return False

    def _contrast(self, a, b):
        ta, tb = self.rm._t(a), self.rm._t(b)
        return ta.get("pace") != tb.get("pace") and {"bold", "careful"} == {ta.get("pace"), tb.get("pace")} \
            or {ta.get("manner"), tb.get("manner")} == {"gentle", "blunt"}

    def _fond(self, ids):
        pairs = [(a, b) for a, b in self.rm.pairs_in(ids) if self.state(a, b) in GOOD]
        random.shuffle(pairs)
        for a, b in pairs:
            x, y = (a, b) if random.random() < 0.5 else (b, a)
            if self._fondness(x, y):
                return True
        return False

    def _dig(self, ids):
        """Someone goes after another for exactly the thing they can't stand about them."""
        cand = []
        for a in ids:
            dislikes = set(self.rm._t(a).get("dislikes", []))
            for b in ids:
                if a == b or self.rm.key(a, b) in self.truce:
                    continue
                kinds = kinds_of(self.t(b))
                hated = [k for k in kinds if KIND_WORDS[k] & dislikes and self.can(a, f"g_hate_{k}")]
                if self.state(a, b) in BAD:
                    hated = hated or [k for k in kinds if self.can(a, f"g_hate_{k}")]
                if hated:
                    cand.append((a, b, random.choice(hated)))
        if not cand:
            return False
        a, b, k = random.choice(cand)
        tb = self.t(b)
        reply = "laugh_off" if tb.get("humour") == "joker" else "bite_back" if tb.get("manner") == "blunt" else "hurt"
        if not self.can(b, reply):
            reply = "g_fire_back"
        parts = [(a, f"g_hate_{k}", b), (b, reply)]
        third = [x for x in ids if x not in (a, b)]
        if third:
            c = third[0]
            if self.state(c, b) in GOOD and self.state(c, a) not in GOOD:
                parts.append((c, "g_take_side"))
            elif self.state(c, a) in GOOD and self.state(c, b) in BAD:
                parts.append((c, "g_pile_on"))
            elif self.can(c, "g_peacemake"):
                parts.append((c, "g_peacemake"))
        if self.beat(parts):
            self.move(a, b, 1.0 if reply == "laugh_off" else -2.0)
            return True
        return False

    def _admire(self, ids):
        speakers = [x for x in ids if self.orient.get(x) and self.can(x, "g_admire")
                    and self.outings - self.admired_at.get(x, -999) >= ADMIRE_GAP]
        random.shuffle(speakers)
        for s in speakers:
            into = {"gay": {"male"}, "lesbian": {"female"}, "bi": {"male", "female"},
                    "straight": {"female"} if self.rm.gender(s) == "male" else {"male"}}.get(self.orient[s], set())
            targets = [x for x in ids if x != s and self.rm.gender(x) in into and self.state(s, x) not in BAD]
            if not targets:
                continue
            o = random.choice(targets)
            reply = "laugh_off" if self.t(o).get("humour") == "joker" else "take_it_kindly"
            if not self.can(o, reply):
                reply = "g_loved"
            parts = [(s, "g_admire", o), (o, reply)]
            third = [x for x in ids if x not in (s, o) and self.can(x, "g_pile_on")]
            if third and random.random() < 0.5:
                parts.append((third[0], "g_pile_on"))
            if self.beat(parts):
                self.admired_at[s] = self.outings
                self.move(s, o, 0.5)
                return True
        return False

    def _callback(self, ids):
        pairs = self.rm.pairs_in(ids)
        random.shuffle(pairs)
        for a, b in pairs:
            k = self.rm.key(a, b)
            log = self.story.get(k) or []
            used = self.called_back.setdefault(k, {})
            for moment, key in (("save", "g_callback_save"), ("clutch", "g_callback_clutch"),
                                ("callout", "g_callback_callout")):
                if moment in log and used.get(moment, 0) < CALLBACK_MAX:
                    x, y = (a, b) if self.can(a, key) else (b, a)
                    if not self.can(x, key):
                        continue
                    reply = "g_quiet_line" if self.t(y).get("humour") == "dry" else "g_fire_back"
                    if self.beat([(x, key, y), (y, reply)]):
                        used[moment] = used.get(moment, 0) + 1
                        self.move(a, b, 1.0)
                        return True
            r = self.rm.rel(a, b)
            if r.was_bad and r.state in GOOD and "former_rivals" not in log:
                x, y = (a, b) if self.can(a, "g_former_rivals") else (b, a)
                if self.can(x, "g_former_rivals") and self.beat([(x, "g_former_rivals", y), (y, "g_loved", x)], 2):
                    self.log_story(a, b, "former_rivals")
                    return True
        return False

    def _argue(self, ids):
        try:
            from world.conversations import get_conversations
            return get_conversations().start_argument(ids)
        except Exception:
            return False

    # ------------------------------------------------------------------ shades of grey
    def _call_out(self, ids, target, why):
        """A friend tells target straight that it was on them. Sore for a while, then they come round."""
        if target not in ids or any(target in k.split("|") for k in self.sore):
            return False                # already being told off by somebody; one at a time
        friends = [x for x in ids if x != target and self.state(x, target) in GOOD and self.can(x, "g_call_out")
                   and self.rm.key(x, target) not in self.sore]
        if not friends or not self.can(target, "g_stung"):
            return False
        ws = [1.0 + 2 * bool({"honest"} & set(self.t(x).get("is", []))) + 2 * (self.t(x).get("manner") == "blunt")
              + (self.t(x).get("pace") == "steady") - 0.6 * (self.t(x).get("manner") == "gentle") for x in friends]
        caller = random.choices(friends, weights=[max(0.2, w) for w in ws])[0]
        if self.beat([(caller, "g_call_out", target), (target, "g_stung", caller)], priority=2):
            k = self.rm.key(caller, target)
            pride = self.rm._dial(target, "pride")
            self.sore[k] = SORE_OUTINGS + (1 if pride >= 1.1 else 0)
            self.move(caller, target, -3.0)
            self.log_story(caller, target, "callout")
            self.push(target, "called_out")
            self._sore_meta = getattr(self, "_sore_meta", {})
            self._sore_meta[k] = (caller, target, why)
            return True
        return False

    def _concede(self, k):
        meta = getattr(self, "_sore_meta", {}).pop(k, None)
        if not meta:
            return
        caller, target, why = meta
        # right if they didn't go down first again since
        right = target not in self.first_down[-2:]
        try:
            from world.conversations import get_conversations
            get_conversations().on_conceded(target, caller)
        except Exception:
            pass
        if self.beat([(target, "g_concede", caller)], priority=2):
            self.move(caller, target, 5.0 if right else 3.0)
            self.push(target, "conceded")
            if right:
                self.push(caller, "call_out_right")

    def _respect(self, a, b, why):
        """Two who can't stand each other give each other their due. A truce, not a friendship."""
        k = self.rm.key(a, b)
        if k in self.truce or not self.can(a, "g_respect") or not self.can(b, "g_nod"):
            return False
        parts = [(a, "g_respect", b), (b, "g_nod", a)]
        others = [x for x in self.rm.ids(getattr(self.rm.bm, "party", None)) if x not in (a, b)] if False else []
        if self.beat(parts, priority=2):
            self.truce[k] = TRUCE_OUTINGS
            self.move(a, b, 3.0)
            self.log_story(a, b, "clutch" if why == "clutch" else "respect")
            return True
        return False

    # ------------------------------------------------------------------ crew scenes
    def _crew_scene(self, combo, what):
        combo = list(combo)
        random.shuffle(combo)
        if what == "formed":
            parts = [(m, "g_crew") for m in combo]
            toaster = max(combo, key=lambda m: role_scores(self.t(m))["mother_hen"])
            if self.can(toaster, "g_toast"):
                parts = [(toaster, "g_toast")] + parts
            return self.beat(parts[:5], priority=3)
        if what == "split":
            a, b = next(((x, y) for x, y in self.rm.pairs_in(combo) if self.state(x, y) in BAD), combo[:2])
            c = next(x for x in combo if x not in (a, b))
            return self.beat([(a, "turn_grating"), (c, "g_left_out")], priority=3)
        if what == "back":
            return self.beat([(combo[0], "g_crew"), (combo[1], "g_cheers")], priority=3)
        return False

    def _family_toast(self, members):
        """Each in turn tells another what they love about them, so everyone is named once."""
        random.shuffle(members)
        parts = []
        for i, a in enumerate(members):
            b = members[(i + 1) % len(members)]
            kinds = [k for k in kinds_of(self.t(b)) if self.can(a, f"g_love_{k}")]
            if not kinds:
                return False
            parts += [(a, f"g_love_{random.choice(kinds)}", b)]
        # the queue holds one scene; a family toast is the big one, so it's one long beat
        return self.beat(parts + [(members[0], "g_cheers")], priority=3)

    # ------------------------------------------------------------------ the test panel
    def panel(self, ids):
        """Rows for the Friendship Test panel's Groups section."""
        ids = self.ids(ids)
        rows = [("Group", self.MOOD_NAMES.get(self.mood(ids), "?"))]
        formed = [c for c in self.crews.values() if c.get("formed") and set(c["members"]) & set(ids)]
        families = [c for c in formed if c.get("family")]
        shown = []
        for c in sorted(formed, key=lambda c: (-len(c["members"]), -c["outings"])):
            # a family covers the crews inside it, and one crew stands for the trios it overlaps
            if any(set(c["members"]) < set(f["members"]) for f in families):
                continue
            if any(len(set(c["members"]) & set(o["members"])) >= 2 and c.get("name") == o.get("name") for o in shown):
                continue
            shown.append(c)
            names = ", ".join(self.first(m) for m in c["members"])
            status = "split" if c.get("split") else ("family" if c.get("family") else "crew")
            rows.append((c.get("name") or "Crew", f"{names} ({status}, {c['outings']} outings)"))
        waiting = [c for c in self.crews.values() if not c.get("formed") and set(c["members"]) <= set(ids)
                   and len(c["members"]) == 3]
        if waiting and not shown:
            c = max(waiting, key=lambda c: c["outings"])
            need = max(0, CREW_OUTINGS - c["outings"])
            rows.append(("Not a crew yet", f"{c['outings']} outings together; {need} more, if all three are friends"))
        for rid in ids:
            sc = role_scores(self.t(rid))
            top = max(sc, key=sc.get).replace("_", " ")
            rows.append((self.first(rid), f"{top}; {self.describe_room(rid, ids)}; {self.describe_drift(rid)}"))
        return rows

    # ------------------------------------------------------------------ save
    def to_dict(self):
        return {k: getattr(self, k) for k in ("crews", "together", "drift", "arc_state", "story", "called_back",
                                              "sore", "truce", "first_down", "admired_at", "noticed", "outings",
                                              "topics_heard", "ensembles_heard")} | \
            {"sore_meta": {k: list(v) for k, v in getattr(self, "_sore_meta", {}).items()}}

    def load_state(self, d):
        d = d or {}
        for k in ("crews", "together", "drift", "arc_state", "story", "called_back", "sore", "truce",
                  "admired_at"):
            setattr(self, k, dict(d.get(k) or {}))
        self.first_down = list(d.get("first_down") or [])
        self.noticed = list(d.get("noticed") or [])
        self.topics_heard = list(d.get("topics_heard") or [])
        self.ensembles_heard = list(d.get("ensembles_heard") or [])
        self.outings = int(d.get("outings") or 0)
        self._sore_meta = {k: tuple(v) for k, v in (d.get("sore_meta") or {}).items()}
