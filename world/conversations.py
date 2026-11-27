"""Wave 4: recruits talk to the player, and pull the player into their arguments (pilot cast first).

Kyle, 25 Nov 2026: "Right now we are wall flowers." Plan: claude/group_dynamics_plan.md, sections Talking to the player,
The player gets a reputation, The player doesn't always get to resolve things, Some conversations should be
uncomfortable, and Delayed consequences.

WANTS TO TALK   a recruit with something to say gets a speech-bubble mark on their portrait. One waiting per recruit,
                at most one new request across the party every NEW_GAP outings (milestones skip the queue), never
                shown mid-fight, and they expire after EXPIRE outings. Ignoring an emotional one is remembered.
KINDS           aftermath, development (their arc), relationship (about another recruit), history, milestone, and
                confrontation (favouritism, dislike, risks, admitting they were wrong, trust, a decision made for them).
APPROACHES      comfort, tough love, a joke, honesty, or just listening. No right answers: what lands depends on who
                it is (fit()), so trust can't be farmed by always picking the nice one.
IMPRESSIONS     each recruit's own read on the player, from what THEY saw: a private talk only they saw, an argument
                everyone present saw. How much an impression counts depends on their likes and dislikes.
SEEDS           a choice can pay off later instead of now: tough love that stings today and, the next time the same
                thing happens and they handle it, "you were right".
ARGUMENTS       authored per pair (tools/group_lines/_arguments.json). One of them asks the player; the player backs one side,
                finds a third way, or stays out, or ignores it. They don't always take the call (resolve()).

Every word a recruit says comes from their own pool in data/npcs/group_lines.json; the player's own options are the
player's voice and are shared (PLAYER).
"""
import json
import random
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "npcs" / "group_lines.json"

NEW_GAP = 3                 # outings between new requests across the whole party
EXPIRE = 4                  # outings a request waits before it lapses
EMOTIONAL = {"aftermath", "confrontation", "development"}
APPROACHES = ("comfort", "tough", "joke", "honest", "listen")
IMPRESSIONS = ("listens", "truth", "jokes", "responsible", "stays_out", "backs_me", "biased", "harsh", "protective",
               "reckless")
#: trust moved by how an approach lands
FIT_TRUST = {"lands": 3, "shrug": 1, "stings": -2}
#: an argument chip left alone this many seconds after its beat is settled without the player
WALLFLOWER_SECONDS = 25.0

#: what the player can say, by kind (the player's own voice, so it's shared). {name} is the other recruit.
PLAYER = {
    "aftermath": {
        "comfort": "Hey. You're still here, and that's what matters right now.",
        "tough": "That one was on us, and we'll fix it before the next one.",
        "joke": "Look on the bright side, the floor's never going to forget us.",
        "honest": "It went wrong. Tell me what you saw, and we'll go through it.",
        "listen": "Sit down a minute. I'm listening.",
    },
    "development": {
        "comfort": "Whatever's changing, it's not making you worse. I'd tell you.",
        "tough": "Then own it. Stop waiting for permission to be who you are now.",
        "joke": "Changed? You still can't make a decent cup of tea, so no.",
        "honest": "Yeah, I've noticed. Want to tell me what it feels like from the inside?",
        "listen": "Go on. Say it the way it is in your head.",
    },
    "relationship": {
        "comfort": "Give it time. People come round, and so do you.",
        "tough": "Then go and say it to their face, not to me.",
        "joke": "Want me to stand between you two? I'll bring snacks.",
        "honest": "From where I'm standing, you're both a bit right and a bit stubborn.",
        "listen": "Tell me what happened. All of it.",
    },
    "confrontation": {
        "comfort": "You're right that I owe you an explanation. Here it is.",
        "tough": "I made the call, and I'd make it again. That's on me.",
        "joke": "Is this the part where you storm off? Let me get comfortable.",
        "honest": "Fair. I didn't think it through from your side.",
        "listen": "Say all of it. I won't interrupt.",
    },
}

#: what each approach tells a recruit about the player
APPROACH_IMPRESSION = {"comfort": "protective", "tough": "truth", "joke": "jokes", "honest": "truth",
                       "listen": "listens"}
#: which impressions someone values, from what they like and can't stand in people
VALUES = {"listens": {"quiet", "patient", "gentle"}, "truth": {"honest", "blunt", "earnest"},
          "jokes": {"funny", "joker", "loud"}, "responsible": {"steady", "careful", "worker"},
          "stays_out": {"quiet", "formal"}, "protective": {"gentle", "healer", "host"},
          "harsh": set(), "biased": set(), "reckless": {"reckless"}, "backs_me": set()}


class Conversations:
    def __init__(self):
        self.lines, self.talks, self.arguments, self.history, self.milestones = {}, {}, [], {}, {}
        self.wants = {}             # rid -> {"kind", "sub", "about", "since", "reason"}
        self.last_new = -999        # outing of the last new request
        self.outings = 0
        self.impressions = {}       # rid -> {impression: count}
        self.backed = {}            # pair key -> {rid: times the player backed them}
        self.seeds = []             # [{"rid", "said", "about", "until", "kind"}]
        self.grumbles = []          # [(due outing, rid, other)]
        self.args_heard = []        # argument ids already played, newest last
        self.history_done = {}      # rid -> [conversation ids]
        self.history_later = {}     # rid -> outing count before a set-aside history chat can come back (not_now)
        self.milestones_done = {}   # rid -> [milestone kinds]
        self.ignored = {}           # rid -> times an emotional request lapsed
        self.pending_ask = None     # the argument the player is being asked about right now
        self.ask_age = 0.0
        self.favour = {}            # rid -> gear upgrades and argument backing received, for favouritism
        self.benched = {}           # rid -> times left out of a dungeon run while in the roster
        self._load()

    def _load(self):
        try:
            raw = json.loads(DATA.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return
        self.lines = raw.get("lines") or {}
        self.arguments = raw.get("arguments") or []
        self.history = raw.get("history") or {}
        self.milestones = raw.get("milestones") or {}

    # ------------------------------------------------------------------ plumbing
    def rm(self):
        from world.bond_manager import get_bond_manager
        return get_bond_manager().rel

    def bm(self):
        from world.bond_manager import get_bond_manager
        return get_bond_manager()

    def t(self, rid):
        try:
            return self.rm().groups.t(rid)
        except Exception:
            return {}

    def say(self, rid, key, about=None):
        """A line from rid's own pool, {name} and {player} filled in. None if they don't have it."""
        g = self.rm().groups
        opts = g.line_opts(rid, key)
        if not opts:
            return None
        text = random.choice(opts)
        if about:
            text = text.replace("{name}", g.first(about))
        text = text.replace("{player}", g._player_name())
        return g.rm.address(text.replace("{name}", ""), about)

    def name(self, rid):
        try:
            return self.bm().name_of(rid).split()[0]
        except Exception:
            return rid

    # ------------------------------------------------------------------ fit and reputation
    def fit(self, rid, approach, kind="aftermath", sub=None):
        """lands / shrug / stings: how this approach goes down with this person, in this kind of talk."""
        t = self.t(rid)
        tags = set(t.get("is", []))
        pride = self._dial(rid, "pride")
        raw = sub in ("near_death", "blame_self", "wipe", "dislike", "decided")
        if approach == "comfort":
            if t.get("manner") == "gentle" or "young" in tags or t.get("talk") == "quiet":
                return "lands"
            return "stings" if (t.get("manner") == "blunt" and pride >= 1.1) else "shrug"
        if approach == "tough":
            if t.get("manner") == "blunt" or tags & {"competitive", "sporty", "honest"}:
                return "lands"
            return "stings" if t.get("manner") == "gentle" or pride >= 1.2 else "shrug"
        if approach == "joke":
            if t.get("humour") == "joker" and not (raw and kind == "confrontation"):
                return "lands"
            return "stings" if t.get("humour") == "earnest" or raw else "shrug"
        if approach == "honest":
            if tags & {"honest"} or t.get("manner") == "blunt" or t.get("humour") == "earnest" \
                    or t.get("pace") == "careful":
                return "lands"
            return "shrug"
        if approach == "listen":
            if t.get("talk") in ("quiet", "talker") or kind in ("development", "history"):
                return "lands"
            return "shrug"
        return "shrug"

    def _dial(self, rid, k):
        try:
            return self.bm().bonds[rid].dial(k)
        except Exception:
            return 1.0

    def impress(self, rid, impression, n=1):
        d = self.impressions.setdefault(rid, {})
        before = d.get(impression, 0)
        d[impression] = before + n
        # once an impression has really set in, they say so, once (seen_listens, seen_biased, ...)
        if before < 3 <= d[impression]:
            said = d.setdefault("_said", [])
            if impression not in said:
                line = self.say(rid, f"seen_{impression}")
                if line:
                    said.append(impression)
                    try:
                        self.rm().queue.append((2, self.rm()._deeds(), [(rid, line)]))
                    except Exception:
                        pass

    def seen_as(self, rid):
        """rid's strongest impression of the player and whether they like it, or None."""
        d = {k: v for k, v in (self.impressions.get(rid) or {}).items() if not k.startswith("_")}
        if not d:
            return None
        top = max(d, key=d.get)
        if d[top] < 3:
            return None
        return top

    def describe_impression(self, rid):
        top = self.seen_as(rid)
        if not top:
            return "hasn't made up their mind about you"
        words = {"listens": "thinks you listen", "truth": "thinks you tell it straight",
                 "jokes": "counts on you for a joke when it's bad", "responsible": "thinks you take responsibility",
                 "stays_out": "thinks you keep out of it", "backs_me": "thinks you've got their back",
                 "biased": "thinks you play favourites", "harsh": "thinks you're harsh",
                 "protective": "thinks you look out for people", "reckless": "thinks you're reckless with them"}
        likes = set(self.t(rid).get("likes", [])) | set(self.t(rid).get("is", []))
        liked = bool(VALUES.get(top, set()) & likes)
        return words.get(top, top) + (" and likes it" if liked else "")

    def trust(self, rid, amount):
        try:
            bm = self.bm()
            b = bm.bonds.get(rid)
            if b is not None:
                bm._trust(b, amount)
        except Exception:
            pass

    # ------------------------------------------------------------------ wants to talk
    def want(self, rid, kind, sub=None, about=None, reason=None, force=False):
        """rid has something to say. Respects one-per-recruit, the party-wide gap, and needs their lines."""
        if not self.lines.get(rid):
            return False
        if rid in self.wants and not force:
            return False
        if kind not in ("milestone", "history") and not self._can_open(rid, kind, sub):
            return False
        if kind == "history" and not self._next_history(rid):
            return False
        if kind == "milestone" and not (self.milestones.get(rid) or {}).get(sub):
            return False
        if not force and kind != "milestone" and self.outings - self.last_new < NEW_GAP:
            return False
        self.wants[rid] = {"kind": kind, "sub": sub, "about": about, "since": self.outings, "reason": reason}
        if kind != "milestone":
            self.last_new = self.outings
        return True

    def _can_open(self, rid, kind, sub):
        mine = self.lines.get(rid) or {}
        return bool(mine.get(f"talk_{kind}_{sub}") or mine.get(f"talk_{kind}"))

    def waiting(self, rid):
        return rid in self.wants

    def on_outing(self, ids):
        """Lapse old requests, ripen seeds and grumbles, and now and then start a history chat."""
        self.outings += 1
        for rid, w in list(self.wants.items()):
            if self.outings - w["since"] > EXPIRE and w["kind"] != "milestone":
                del self.wants[rid]
                if w["kind"] in EMOTIONAL:
                    self.ignored[rid] = self.ignored.get(rid, 0) + 1
                    self.trust(rid, -1)
        for due, rid, other in list(self.grumbles):
            if self.outings >= due and rid in ids:
                self.grumbles.remove((due, rid, other))
                line = self.say(rid, "arg_grumble", other)
                if line:
                    self.rm().queue.append((2, self.rm()._deeds(), [(rid, line)]))
        self.seeds = [s for s in self.seeds if s["until"] >= self.outings]
        for rid in ids:
            if random.random() < 0.15:
                self.want(rid, "history")
        self._confrontations(ids)

    def _confrontations(self, ids):
        fav = self.favour
        if len(ids) >= 2 and fav:
            top = max(ids, key=lambda r: fav.get(r, 0))
            for rid in ids:
                if rid != top and fav.get(top, 0) - fav.get(rid, 0) >= 4:
                    if self.want(rid, "confrontation", "favour", about=top):
                        fav[top] = fav.get(top, 0) - 2
                        return
        for rid in ids:
            if self.benched.get(rid, 0) >= 3 and self.want(rid, "confrontation", "trust"):
                self.benched[rid] = 0
                return
        rm = self.rm()
        for a, b in rm.pairs_in(ids):
            if rm.state(a, b) == "rivals":
                x = a if random.random() < 0.5 else b
                if random.random() < 0.2 and self.want(x, "confrontation", "dislike", about=rm.rel(a, b).other(x)):
                    return

    # ------------------------------------------------------------------ events that start talks
    def on_close_call(self, ids, hurt):
        for h in hurt:
            if h in ids:
                self.want(h, "aftermath", "near_death")

    def on_wipe(self, ids, first_down=None):
        if not ids:
            return
        nervous = min(ids, key=lambda r: self._dial(r, "nerve"))
        if not self.want(nervous, "aftermath", "wipe"):
            for rid in ids:
                if rid != first_down and self.rm().state(rid, first_down) in ("friendly", "close") \
                        and self.want(rid, "aftermath", "blame_self", about=first_down):
                    break
        for rid in ids:
            if self.bm().bonds.get(rid) and self.bm().bonds[rid].wipes >= 2:
                if self.want(rid, "confrontation", "risks"):
                    break
        self._ripen_seeds("wipe", ids, handled=False)

    def on_fight_won(self, ids, first_down=None, boss=False):
        handled = [r for r in ids if r != first_down]
        self._ripen_seeds("first_down", handled, handled=True)
        if boss:
            for rid in ids:
                if self.want(rid, "aftermath", "first_clear"):
                    break

    def on_gear_taken(self, rid, given_to=None):
        if given_to:
            self.favour[given_to] = self.favour.get(given_to, 0) + 1
        self.want(rid, "confrontation", "decided", about=given_to)

    def on_conceded(self, rid, caller):
        self.want(rid, "confrontation", "wrong", about=caller)

    def on_pair_changed(self, a, b, milestone):
        """A pair milestone from the relationship system turns into somebody wanting a word about the other."""
        sub = {"turn_grating": "acting_off", "turn_rivals": "respect_hate", "make_up": "hard_on",
               "turn_friendly": "likes_me"}.get(milestone)
        if sub:
            x = a if random.random() < 0.5 else b
            self.want(x, "relationship", sub, about=b if x == a else a)
        if milestone == "make_up":
            self.want(a, "milestone", "reconciled", about=b)

    def on_stage(self, rid, stage):
        if stage in ("friend", "sworn"):
            self.want(rid, "milestone", stage, force=True)

    # ------------------------------------------------------------------ running a conversation
    def open(self, rid):
        """The conversation rid wants: {"rid", "kind", "sub", "about", "line", "options": [(label, approach)]} or None.
        Options are the player's words; the recruit's opener is their own."""
        w = self.wants.get(rid)
        if not w:
            return None
        kind, sub, about = w["kind"], w["sub"], w["about"]
        if kind == "history":
            conv = self._next_history(rid)
            if not conv:
                self.wants.pop(rid, None)
                return None
            return {"rid": rid, "kind": kind, "id": conv["id"], "line": self._fill(conv["open"]),
                    "options": [(self._fill(o["text"]), i) for i, o in enumerate(conv["options"])]}
        if kind == "milestone":
            m = (self.milestones.get(rid) or {}).get(sub)
            if not m:
                self.wants.pop(rid, None)
                return None
            text = self._fill(m["open"].replace("{name}", self.name(about) if about else ""))
            return {"rid": rid, "kind": kind, "sub": sub, "line": text,
                    "options": [(self._fill(o["text"]), i) for i, o in enumerate(m["options"])]}
        opener = self.say(rid, f"talk_{kind}_{sub}", about) or self.say(rid, f"talk_{kind}", about)
        if not opener:
            self.wants.pop(rid, None)
            return None
        texts = PLAYER.get(kind, PLAYER["aftermath"])
        opts = [(texts[a].replace("{name}", self.name(about) if about else "them"), a) for a in APPROACHES]
        return {"rid": rid, "kind": kind, "sub": sub, "about": about, "line": opener, "options": opts}

    def choose(self, rid, choice):
        """The player answered. Returns the recruit's reply (their own line), and applies trust, impressions and seeds.
        Some talks don't resolve: the reply can be a door closing ("We're done here.")."""
        w = self.wants.pop(rid, None)
        if not w:
            return ""
        kind, sub, about = w["kind"], w["sub"], w["about"]
        if kind == "history":
            conv = self._next_history(rid)
            if not conv:
                return ""
            o = conv["options"][choice]
            self.history_done.setdefault(rid, []).append(conv["id"])
            self.trust(rid, o.get("trust", 1))
            if o.get("impression"):
                self.impress(rid, o["impression"])
            return self._fill(o.get("reply", ""))
        if kind == "milestone":
            m = (self.milestones.get(rid) or {}).get(sub) or {}
            o = (m.get("options") or [{}])[choice]
            self.milestones_done.setdefault(rid, []).append(sub)
            self.trust(rid, o.get("trust", 2))
            return self._fill(o.get("reply", ""))
        approach = choice
        f = self.fit(rid, approach, kind, sub)
        self.trust(rid, FIT_TRUST[f])
        self.impress(rid, APPROACH_IMPRESSION.get(approach, "listens"))
        if f == "stings" and approach == "tough":
            self.impress(rid, "harsh")
        g = self.rm().groups
        # the delayed part: tough love or honesty that stung plants a seed; the next time the same thing comes up
        # and they handle it, they come back and say so
        if kind == "aftermath" and approach in ("tough", "honest"):
            self.seeds.append({"rid": rid, "said": approach, "about": sub, "until": self.outings + 12,
                               "kind": "first_down" if sub in ("wipe", "near_death") else sub})
        if kind == "development":
            st = g.arc_state.get(rid) or {}
            arc = g.arcs.get(rid) or {}
            shape = arc.get("alt") if st.get("path") == "alt" else arc.get("shape")
            if f == "lands":
                g.push(rid, "listened")
                if shape == "slide" and approach in ("tough", "honest"):
                    g.push(rid, "pulled_back")
            elif f == "stings" and shape == "slide" and approach == "comfort":
                g.push(rid, "dark_power")
            if shape == "burnout" and approach in ("comfort", "listen"):
                g.push(rid, "let_others")
        if kind == "relationship" and about:
            if approach in ("comfort", "honest") and f != "stings":
                g.move(rid, about, 2.0)
            elif approach == "tough" and f == "lands":
                g.move(rid, about, 1.0)
            elif approach == "joke" and f == "stings":
                g.move(rid, about, -1.0)
        reply = self.say(rid, f"talk_{f}_{kind}", about) or self.say(rid, f"talk_{f}", about) or ""
        if kind == "confrontation" and f == "stings":
            reply = self.say(rid, "talk_door_closed", about) or reply
            self.bm()._mood(self.bm().bonds[rid], -3) if self.bm().bonds.get(rid) else None
        return reply

    def _fill(self, text):
        """{player} in an authored line becomes the hero's name. The history and milestone talks were written with
        it and shown raw (Kyle, 26 Nov 2026: "they dont use my name lol...sometimes")."""
        try:
            name = self.bm().rel.groups._player_name()
        except Exception:
            name = "friend"
        return (text or "").replace("{player}", name)

    def not_now(self, rid):
        """The player closed the window without answering. The talk is set aside rather than left waiting, so the
        next time he's looked at he doesn't open with the very same line (Kyle, 26 Nov 2026: "the characters keep
        repeating their opening lines"). A history chat comes back later, after the usual gap; no trust is lost for
        a polite not now."""
        w = self.wants.pop(rid, None)
        if w and w.get("kind") == "history":
            self.history_later[rid] = self.outings + NEW_GAP
        self.last_new = self.outings

    def _next_history(self, rid):
        if self.outings < self.history_later.get(rid, 0):
            return None
        done = set(self.history_done.get(rid, []))
        try:
            stage = self.bm().bonds[rid].stage
        except Exception:
            stage = 0
        for conv in self.history.get(rid) or []:
            if conv["id"] not in done and conv.get("stage", 0) <= stage:
                return conv
        return None

    def _ripen_seeds(self, event, ids, handled):
        for s in list(self.seeds):
            if s["rid"] in ids and s["kind"] == event:
                key = "seed_right" if handled else "seed_remember"
                line = self.say(s["rid"], key)
                if line:
                    self.rm().queue.append((2, self.rm()._deeds(), [(s["rid"], line)]))
                    self.trust(s["rid"], 4 if handled else 1)
                    self.impress(s["rid"], "truth")
                    self.seeds.remove(s)
                    try:
                        self.rm().groups.push(s["rid"], "conceded" if handled else "listened")
                    except Exception:
                        pass
                    return

    # ------------------------------------------------------------------ arguments
    def start_argument(self, ids):
        """One of the authored arguments between two people present. The asker turns to the player at the end."""
        here = set(ids)
        options = [a for a in self.arguments if set(a["between"]) <= here and a["id"] not in self.args_heard[-6:]]
        if not options or self.pending_ask:
            return False
        arg = random.choice(options)
        rm = self.rm()
        asker = arg.get("asker") or arg["between"][0]
        other = next(x for x in arg["between"] if x != asker)
        ask_line = self.say(asker, "arg_ask", other)
        if not ask_line:
            return False
        lines = [(rid, text) for rid, text in arg["lines"]] + [(asker, ask_line)]
        # sometimes they sort it out themselves before the player gets a word in
        if random.random() < 0.15 and self.say(other, "arg_settled", asker):
            lines[-1] = (other, self.say(other, "arg_settled", asker))
            rm.queue.append((2, rm._deeds(), lines))
            self.args_heard.append(arg["id"])
            rm.groups.move(asker, other, 1.0)
            return True
        ask = {"arg": arg["id"], "asker": asker, "other": other, "witnesses": list(ids)}
        rm.queue.append((2, rm._deeds(), lines, ask))
        rm.queue.sort(key=lambda q: -q[0])
        self.args_heard.append(arg["id"])
        return True

    def ask_options(self, ask):
        """[(label, choice)] for the argument the player was pulled into."""
        arg = next((a for a in self.arguments if a["id"] == ask["arg"]), None)
        if not arg:
            return []
        a, b = ask["asker"], ask["other"]
        return [(f"Back {self.name(a)}: {arg['sides'][a]}", "back_asker"),
                (f"Back {self.name(b)}: {arg['sides'][b]}", "back_other"),
                (arg.get("third", "Split the difference."), "third"),
                ("Leave me out of this.", "stay_out")]

    def resolve(self, ask, choice):
        """The player's call on an argument. They don't always take it. Queues the reaction; returns its lines."""
        rm = self.rm()
        g = rm.groups
        a, b = ask["asker"], ask["other"]
        arg = next((x for x in self.arguments if x["id"] == ask["arg"]), {})
        stakes = arg.get("stakes", "low")
        k = rm.key(a, b)
        tally = self.backed.setdefault(k, {})
        lines = []
        weight = 2 if stakes == "high" else 1
        if choice in ("back_asker", "back_other"):
            win, lose = (a, b) if choice == "back_asker" else (b, a)
            tally[win] = tally.get(win, 0) + 1
            self.favour[win] = self.favour.get(win, 0) + 1
            pride = self._dial(lose, "pride")
            seen_biased = self.seen_as(lose) == "biased"
            roll = random.random()
            reject = roll < (0.15 + 0.15 * (pride >= 1.1) + 0.2 * seen_biased)
            grumble = not reject and roll < 0.55
            lines.append((win, self.say(win, "arg_backed_me", lose)))
            if tally.get(win, 0) - tally.get(lose, 0) >= 3 and self.say(lose, "arg_always_their_side", win):
                lines.append((lose, self.say(lose, "arg_always_their_side", win)))
                self.impress(lose, "biased", 2)
            elif reject:
                lines.append((lose, self.say(lose, "arg_reject", win)))
            else:
                lines.append((lose, self.say(lose, "arg_backed_them", win)))
                if grumble:
                    self.grumbles.append((self.outings + random.randint(2, 4), lose, win))
            self.trust(win, 1 * weight)
            self.trust(lose, -1 * weight if reject or seen_biased else 0)
            self.impress(win, "backs_me")
            for w in ask.get("witnesses", []):
                if w not in (a, b):
                    self.impress(w, "truth")
            g.move(a, b, -0.5 * weight if reject else 0.5)
        elif choice == "third":
            if random.random() < 0.7:
                lines += [(a, self.say(a, "arg_settled", b)), (b, self.say(b, "g_cheers") or self.say(b, "arg_settled", a))]
                g.move(a, b, 1.5 * weight)
                for w in ask.get("witnesses", []):
                    self.impress(w, "jokes" if "joke" in arg.get("third", "").lower() else "responsible")
            else:
                lines += [(a, self.say(a, "arg_reject", b)), (b, self.say(b, "arg_reject", a))]
                g.move(a, b, -0.5)
        else:
            lines.append((a, self.say(a, "arg_stayed_out", b)))
            for w in ask.get("witnesses", []):
                self.impress(w, "stays_out")
            if self.impressions.get(a, {}).get("stays_out", 0) >= 4:
                self.trust(a, -1)
        lines = [(r, t) for r, t in lines if t]
        if lines:
            rm.queue.insert(0, (3, rm._deeds(), lines))
        self.pending_ask = None
        return lines

    def wallflower(self, ask):
        """The player never answered: they settle it themselves, with a jab at the wallflower."""
        rm = self.rm()
        a, b = ask["asker"], ask["other"]
        line = self.say(a, "arg_wallflower", b)
        if line:
            rm.queue.insert(0, (2, rm._deeds(), [(a, line)]))
        for w in ask.get("witnesses", []):
            self.impress(w, "stays_out")
        self.pending_ask = None

    # ------------------------------------------------------------------ save
    def to_dict(self):
        return {k: getattr(self, k) for k in ("wants", "last_new", "outings", "impressions", "backed", "seeds",
                                              "grumbles", "args_heard", "history_done", "milestones_done", "ignored",
                                              "favour", "benched", "history_later")}

    def load_state(self, d):
        d = d or {}
        for k in ("wants", "impressions", "backed", "history_done", "milestones_done", "ignored", "favour", "benched",
                  "history_later"):
            setattr(self, k, dict(d.get(k) or {}))
        for k in ("seeds", "args_heard"):
            setattr(self, k, list(d.get(k) or []))
        self.grumbles = [tuple(x) for x in d.get("grumbles") or []]
        self.last_new = int(d.get("last_new", -999))
        self.outings = int(d.get("outings", 0))
        self.pending_ask = None


_INSTANCE = None


def get_conversations():
    global _INSTANCE
    if _INSTANCE is None:
        _INSTANCE = Conversations()
    return _INSTANCE


def reset_conversations():
    global _INSTANCE
    _INSTANCE = None
