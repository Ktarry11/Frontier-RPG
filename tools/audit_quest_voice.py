#!/usr/bin/env python3
"""Score every zone's quest text against the voice bar, as the player reads it (overlays applied).

    PYTHONPATH=. python3 tools/audit_quest_voice.py                 # the league table, worst first
    PYTHONPATH=. python3 tools/audit_quest_voice.py stranglethorn   # every finding in files matching that
    PYTHONPATH=. python3 tools/audit_quest_voice.py --max 0 stranglethorn_north stranglethorn_central
                                                                    # exit 1 if any named file has a finding

Kyle, 17 Nov 2026: "Can you start to do a quest writing pass while we wait for art. Like I'm seeing issues in
STV with writing too. You have the template for what is good writing."

THE BAR is claude/quest_writing_guide.md and the 10 Nov playtest notes: a giver says who they are, what is wrong,
why it matters to them and what to do, in plain speech. This script measures what a machine can:

  * the tics tools/build_tempest_quests.voice_problems catches: "it is not X, it is Y", missing contractions,
    dashes, filler, "kill N of X", and fragments of one or two words;
  * refrains: a closer or address that turns up again and again across a zone ("friend", "Thank you", "Take
    your pick", "mon" in a speaker who isn't a troll is not checked: voice is a reader's call);
  * aphorism shapes the playtest named: "the difference between", "the gap between", "is the kind of", "X is
    one thing. Y is another", a line ending on a moral;
  * empty fields and turn-ins that are only thanks.

It does not judge whether a line is good. It finds the lines that certainly aren't, so a rewrite starts with them.
"""
import collections
import contextlib
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from tools.build_tempest_quests import voice_problems

FIELDS = ("description", "accept_text", "turn_in_text")

APHORISM = {
    "aphorism: the difference/gap between": re.compile(r"\bthe (difference|gap|distance) between\b", re.I),
    "aphorism: is the kind of": re.compile(r"\bis the (kind|sort) of (thing|man|woman|place|person)\b", re.I),
    "aphorism: X is one thing": re.compile(r"\bis one thing\b", re.I),
    "aphorism: and that's the point/whole": re.compile(r"\b(and )?that'?s the (whole )?(point|trick|thing)\b", re.I),
    "aphorism: some things": re.compile(r"^\s*some (things|men|people)\b|\. Some (things|men|people) ", re.I),
}
REFRAINS = {
    "friend": re.compile(r"\bfriend\b", re.I),
    "thank you": re.compile(r"\bthank(s| you)\b", re.I),
    "take your pick": re.compile(r"\btake your pick\b", re.I),
    "stranger": re.compile(r"\bstranger\b", re.I),
    "outsider": re.compile(r"\boutsider\b", re.I),
}
THANKS_ONLY = re.compile(r"^\W*(thank(s| you)|good work|well done|excellent|perfect)[^.!?]{0,30}[.!?]?\W*$", re.I)


def load():
    """{source file stem: [quest]} with the overlay text the game shows."""
    with contextlib.redirect_stdout(io.StringIO()):
        from world.quest_manager import QuestManager
        qm = QuestManager()
    by_file = {}
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        try:
            ids = [q["quest_id"] for q in json.loads(path.read_text(encoding="utf-8")).get("quests", [])
                   if isinstance(q, dict) and q.get("quest_id")]
        except (ValueError, OSError):
            continue
        qs = [qm.quests[i] for i in ids if i in qm.quests]
        if qs:
            by_file[path.stem] = qs
    return by_file


# THIRD PERSON. Kyle, 21 Nov 2026: "Azshara is doing that weird third person shit again with quests", then "make some
# kind of note that doesnt have quests handed out in third person...and likely something else that has a story and aims
# for at least 5-6 sentences of coherant structure". The body the offer window prints (the same pick the dialog makes,
# ui/screens/quest_dialog_screen.py) has to be the giver talking: "Okkar says the caravans won't run" from Okkar's own
# mouth is a narrator, not a person. Caught when the body names its own giver with a verb after it, or opens on
# He/She/They, and has no first person anywhere outside quotes.
_GIVERS = None
_TITLE_WORDS = {"grunt", "elder", "overseer", "bloodwarden", "provisioner", "innkeeper", "captain", "sergeant", "the",
                "of", "high", "lord", "lady", "keeper", "warden", "scout", "quartermaster", "doctor", "master",
                "mistress", "apothecary", "deathstalker", "loremaster", "magister", "commander", "chieftain", "old"}
_SAYS = (r"(says|said|wants|needs|thinks|has|had|asks|is|was|reckons|believes|knows|figures|would|will|won't|can't|"
         r"swears|hopes|tells|told|keeps|runs|sent|sends)")
_FIRST = re.compile(r"\b(I|I'm|I've|I'll|I'd|[Mm]e|[Mm]y|[Mm]ine|[Ww]e|[Ww]e're|[Ww]e've|[Ww]e'll|[Oo]ur|[Uu]s)\b")
STORY_MIN = 5


def _giver_names():
    global _GIVERS
    if _GIVERS is None:
        names = {}
        for fn, key in (("data/npcs/ambient_npcs.json", "npc_id"), ("data/npcs/vendors.json", "vendor_id")):
            for v in json.loads((ROOT / fn).read_text(encoding="utf-8")).values():
                if isinstance(v, list):
                    names.update({r[key]: r.get("name", "") for r in v if isinstance(r, dict) and r.get(key)})
        by_quest = {}
        for f in (ROOT / "data/quests").glob("*.json"):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except Exception:                                    # noqa: BLE001
                continue
            for qd in (doc.get("quests") if isinstance(doc, dict) else doc) or []:
                if isinstance(qd, dict) and qd.get("quest_id"):
                    by_quest[qd["quest_id"]] = names.get(qd.get("giver_npc_id") or "", "")
        _GIVERS = by_quest
    return _GIVERS


def offer_body(q):
    """(field, text): what the offer window prints as the giver's words, by the dialog's own rule."""
    desc, speech = (getattr(q, "description", "") or "").strip(), (getattr(q, "accept_text", "") or "").strip()
    if len(speech) > len(desc) or (len(desc) > 200 and len(speech) > 200):
        return "accept_text", speech
    return "description", desc


def third_person(q):
    giver = getattr(q, "giver_npc_id", None)
    if isinstance(giver, str) and giver.startswith("item:"):
        return False                                     # an item starter narrates to "you" on purpose
    name = _giver_names().get(getattr(q, "quest_id", ""), "")
    _field, body = offer_body(q)
    if _FIRST.search(re.sub(r'"[^"]*"', "", body)):
        return False
    if re.match(rf"^(He|She|They)\s+{_SAYS}\b", body):
        return True
    for tok in re.findall(r"[A-Z][a-z']+", name):
        if tok.lower() in _TITLE_WORDS or len(tok) < 3:
            continue
        if re.search(rf"\b{re.escape(tok)}('s)?\s+{_SAYS}\b", body) or re.search(rf"\b{re.escape(tok)}\b", body[:80]):
            return True
    return False


def _check_third(body, q):
    giver = getattr(q, "giver_npc_id", None)
    if isinstance(giver, str) and giver.startswith("item:"):
        return False
    name = _giver_names().get(getattr(q, "quest_id", ""), "")
    if _FIRST.search(re.sub(r'"[^"]*"', "", body)):
        return False
    if re.match(rf"^(He|She|They)\s+{_SAYS}\b", body):
        return True
    for tok in re.findall(r"[A-Z][a-z']+", name):
        if tok.lower() in _TITLE_WORDS or len(tok) < 3:
            continue
        if re.search(rf"\b{re.escape(tok)}('s)?\s+{_SAYS}\b", body) or re.search(rf"\b{re.escape(tok)}\b", body[:80]):
            return True
    return False


# Givers that are things, not people (a skeleton, a grave marker). Like item starters they narrate to "you", because
# the remains can't talk.
OBJECT_GIVERS = {"durotar_skeleton_marker"}


def journal_third_person(q):
    """The quest journal always prints `description`, whichever field the offer window picked. A narrator there is
    the same failure as a narrator in the window. Stricter than the window check: a giver talking says I, me, my, we
    or us somewhere, so a description with no first person at all is narration even when it never names the giver
    ("Twice a week Hillsbrad's militia walk up the tower road..."). Item starters narrate to "you" on purpose."""
    giver = getattr(q, "giver_npc_id", None)
    if not giver or (isinstance(giver, str) and giver.startswith("item:")) or giver in OBJECT_GIVERS:
        return False
    body = (getattr(q, "description", "") or "").strip()
    return not _FIRST.search(re.sub(r'"[^"]*"', "", body)) or _check_third(body, q)


# STORY-DONE ZONES. Kyle, 22 Nov 2026: one zone at a time, to docs/quest_writing_standard.md. Once a zone is on this
# list, an offer under STORY_MIN sentences or a journal that narrates is a hard finding there, so it can't slip back.
STORY_DONE = {"feralas", "hillsbrad", "stranglethorn_north", "stranglethorn_central", "stranglethorn_south", "shimmering_flats", "tanaris", "lower_boughs", "middle_boughs", "upper_boughs", "rootwater_isle", "harvest_finds", "dawnhaven", "aurelion", "great_settlement", "southern_needles", "aspen", "arathi", "plaguelands_south", "plaguelands_north", "plaguelands_epl_west", "plaguelands_epl_east", "ashenvale", "black_strand", "felwood", "abyssal_sands", "glittervein", "tempest_shallows", "ashen_reach", "underdark", "valley_of_trials", "moonglade", "underdark_dungeons", "deadwind", "stonetalon", "hillsbrad_dungeons", "orgrimmar", "lashings", "scarlet_monastery", "razor_hill", "timbermaw_tunnel", "royal_hive", "plaguelands_turnins", "crossroads", "hidden_zones", "durotar", "sepulcher", "ashenvale_dungeons", "fenris_isle", "central_barrens", "northern_barrens", "southern_barrens"}
_STEM_OF = None


def _stem_of(qid):
    global _STEM_OF
    if _STEM_OF is None:
        _STEM_OF = {}
        for f in (ROOT / "data/quests").glob("*.json"):
            try:
                doc = json.loads(f.read_text(encoding="utf-8"))
            except Exception:                                    # noqa: BLE001
                continue
            for qd in (doc.get("quests") if isinstance(doc, dict) else doc) or []:
                if isinstance(qd, dict) and qd.get("quest_id"):
                    _STEM_OF[qd["quest_id"]] = f.stem
    return _STEM_OF.get(qid)


# ACCEPT ECHO. Kyle, 22 Nov 2026: the accept line is one short, DIFFERENT beat. A line that only repeats what the
# speech above it already said ("Look at them properly while you're among them" under a speech that ends "while
# you're among them, look at them properly") adds nothing, and 320 of them slipped through because no check asked.
_ECHO_STOP = set("""that this with your they them have what when from there their will just here back come bring
before would into been than then more some about like only need want make sure it's i'll i've don't they're you're
you'll we'll he's she's that's there's what's can't won't isn't aren't didn't doesn't over still even much very also
because while where which who's those these other every each again once well good right take takes give tell""".split())
ECHO_SHARE = 0.6
ECHO_RUN = 6


def _content_words(text):
    return {w for w in re.findall(r"[a-z']{4,}", (text or "").lower()) if w not in _ECHO_STOP}


def accept_echo(q):
    """Share of the accept line's content words already in the description, when the accept line is the short beat
    (the window shows the description). None when there is no short accept line to judge."""
    acc = (getattr(q, "accept_text", "") or "").strip()
    if not acc or len(acc) > 200:
        return None
    desc = getattr(q, "description", "") or ""
    # a run of ECHO_RUN words lifted straight out of the speech is an echo however few content words it has
    # ("Second street off the east gate" under a speech that already says it)
    seq = re.findall(r"[a-z']+", acc.lower())
    flat = " " + " ".join(re.findall(r"[a-z']+", desc.lower())) + " "
    if any(" " + " ".join(seq[i:i + ECHO_RUN]) + " " in flat for i in range(len(seq) - ECHO_RUN + 1)):
        return 1.0
    words = _content_words(acc)
    if len(words) < 2:
        return None
    return len(words & _content_words(desc)) / len(words)


def story_sentences(q):
    """How many real sentences (three words or more) the offer body holds. The bar is STORY_MIN."""
    _field, body = offer_body(q)
    return len([x for x in re.split(r"(?<=[.!?])\s+", body.strip()) if len(x.split()) >= 3])


def findings(q):
    out = []
    if third_person(q):
        out.append((offer_body(q)[0], "third person: the giver is talked about instead of talking"))
    if _stem_of(getattr(q, "quest_id", "")) in STORY_DONE:
        if story_sentences(q) < STORY_MIN:
            out.append((offer_body(q)[0], f"story: under {STORY_MIN} sentences (docs/quest_writing_standard.md)"))
        if journal_third_person(q):
            out.append(("description", "third person in the journal: the description narrates the giver"))
        share = accept_echo(q)
        if share is not None and share >= ECHO_SHARE:
            out.append(("accept_text", f"accept echo: {share:.0%} of the accept line repeats the speech; write a new beat"))
    for f in FIELDS:
        text = getattr(q, f, "") or ""
        if not text.strip():
            out.append((f, "empty"))
            continue
        for p in voice_problems(text):
            out.append((f, p))
        for name, rx in APHORISM.items():
            m = rx.search(text)
            if m:
                out.append((f, f"{name}: '{m.group(0).strip()}'"))
        if f == "turn_in_text" and THANKS_ONLY.match(text):
            out.append((f, "turn-in is only thanks"))
    return out


def refrains(qs):
    """{refrain: count} where a refrain shows up in more than a fifth of a zone's quests."""
    c = collections.Counter()
    for q in qs:
        text = " ".join(getattr(q, f, "") or "" for f in FIELDS)
        for name, rx in REFRAINS.items():
            if rx.search(text):
                c[name] += 1
    return {k: v for k, v in c.items() if v >= max(3, len(qs) // 5)}


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    cap = None
    if "--max" in sys.argv:
        cap = int(sys.argv[sys.argv.index("--max") + 1])
        args = [a for a in args if a != str(cap)]
    by_file = load()
    if not args:
        rows = []
        for stem, qs in by_file.items():
            n = sum(len(findings(q)) for q in qs)
            bad_q = sum(1 for q in qs if findings(q))
            third = sum(1 for q in qs if third_person(q))
            short = sum(1 for q in qs if story_sentences(q) < STORY_MIN)
            rows.append((n / len(qs), stem, len(qs), bad_q, n, third, short, refrains(qs)))
        print(f"{'file':34s} {'quests':>6s} {'flagged':>7s} {'findings':>8s} {'per q':>6s} {'3rd p':>5s} "
              f"{'<' + str(STORY_MIN) + ' sent':>7s}  refrains")
        for per, stem, nq, bq, n, third, short, ref in sorted(rows, reverse=True):
            print(f"{stem:34s} {nq:6d} {bq:7d} {n:8d} {per:6.2f} {third:5d} {short:7d}  {ref or ''}")
        return 0
    total = 0
    for stem, qs in by_file.items():
        # an argument that names a file exactly matches only that file ("southern_barrens" is not the hub)
        if not any(a == stem or (a not in by_file and a in stem) for a in args):
            continue
        n = 0
        for q in qs:
            fs = findings(q)
            if fs:
                n += len(fs)
                print(f"{stem} | {q.quest_id} | {q.title}")
                for f, p in fs:
                    print(f"    {f:12s} {p}")
            if "--story" in sys.argv and story_sentences(q) < STORY_MIN:
                print(f"{stem} | {q.quest_id} | {q.title}\n    {'story':12s} {story_sentences(q)} sentences, aim for 5-6")
        ref = refrains(qs)
        print(f"== {stem}: {n} findings in {len(qs)} quests; refrains {ref or 'none'}\n")
        total += n + sum(ref.values())
    if cap is not None and total > cap:
        print(f"FAIL: {total} > {cap}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
