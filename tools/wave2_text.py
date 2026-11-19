#!/usr/bin/env python3
"""Wave 2 of the recruit work: how each recruit behaves, one source file per recruit.

    PYTHONPATH=. python3 tools/wave2_text.py          # check every file, write nothing

Each recruit's Wave 1 profile (docs/recruits/<name>.md) is turned into a file in tools/wave2/
named <recruit_id>.json. It carries up to three blocks, and each block feeds one existing builder,
so there's still only one place each kind of text is written:

  bond          their friendship record: dials, likes, the five stages, the reply moments and
                the lines that name a cause. Read by tools/build_recruit_bonds.py, which also
                holds the pilot three (Kesten, Adrián and Tarek) by hand.
  banter        their party banter, per trigger. Read by tools/build_banter_lines.py, and it
                replaces whatever that file had for them before.
  recruit_text  any of greeting, backstory, before, adjustment, now, forward, overlaid on
                recruits.json by tools/rewrite_recruits.py as its last batch. Only the fields
                that the profile changed are here.

Kyle's rules for all of it: plain speech that a person would say to somebody they travel with,
contractions, no one or two word sentences, no dashes, no stage asides. A line never names another
recruit (they start as strangers; Wave 3 is where they meet). Asher is never touched.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

SRC = ROOT / "tools" / "wave2"
NEVER_TOUCH = {"asher_coleman"}
PILOT = {"kesten_the_catalogued", "adrian_templar", "tarek_templar"}

TEXT_FIELDS = ("greeting", "backstory", "before", "adjustment", "now", "forward")
#: BackgroundScreen doesn't scroll; tools/build_recruit_backgrounds.py set this limit.
SECTION_MAX = 700
STAGES = ("stranger", "acquaintance", "companion", "friend", "sworn")
LINE_KEYS = ("bored_warning", "leaving_good", "leaving_bored", "after_wipe", "wipe_warning",
             "wipe_leave", "zone_warning", "zone_leave", "gear_refuse", "gear_taken", "gear_short",
             "gear_upgrade", "back", "send_word", "walkout_talk", "neglect", "asked_to_stay",
             "on_break")
LIKES = {"dungeon", "boss", "quest", "new_ground", "undead", "demon", "beast", "grinding",
         "full_party", "quest_abandoned"}
TRIGGERS = ("town_arrive", "dungeon_clear", "boss_down", "close_call", "zone_arrive")
WHEN = {"hire", "talk", "wipe", "first_stint_end"}


def load():
    """{recruit_id: {"bond":..., "banter":..., "recruit_text":...}} for every file in tools/wave2."""
    out = {}
    if SRC.is_dir():
        for p in sorted(SRC.glob("*.json")):
            out[p.stem] = json.loads(p.read_text(encoding="utf-8"))
    return out


def bonds():
    return {rid: d["bond"] for rid, d in load().items() if "bond" in d}


def banter():
    return {rid: d["banter"] for rid, d in load().items() if "banter" in d}


def recruit_text():
    return {rid: d["recruit_text"] for rid, d in load().items() if "recruit_text" in d}


def _texts(rid, d):
    for k, t in d.get("recruit_text", {}).items():
        yield f"text {k}", t
    b = d.get("bond", {})
    for k, t in b.get("stages", {}).items():
        yield f"stage {k}", t
    for k, t in b.get("lines", {}).items():
        yield f"line {k}", t
    for m in b.get("moments", []):
        if m.get("line"):
            yield f"moment {m['id']}", m["line"]
        for o in m["options"]:
            yield f"reply {m['id']}", o["reply"]
    for trig, es in d.get("banter", {}).items():
        for e in es:
            yield f"banter {trig}", e["text"]


#: Stock phrases. Each line passes the voice rules alone, but read 75 recruits back to back and
#: these turn up again and again, and that's what makes them sound written rather than spoken.
#: Kyle: "These are real people." Narrator lines (send_word, on_break) are left out.
TICS = [
    (r"\byou'd (love|never leave)", "postcard closer"),
    (r"\bi'd give (anything|a lot|a great deal)", "postcard closer"),
    (r"\bi miss (the|both|every|them both|it every|that)\b", "postcard closer"),
    (r"'s (all|built on) [\w ,'-]+? and ", "postcard list"),
    (r"^(?!That|It|This)[A-ZÀ-Ý][\w' -]+ (has|had) (a|an|the|two|seven|forty|miles|more|twenty) [\w ,'-]+?, (a|an|and|the) ", "postcard list"),
    (r"\bevery(body|one)('s| is)? (out|walked out|accounted|came out)", "everybody out"),
    (r"\bevery(body|one) (counted|alive)", "everybody out"),
    (r"\b(somebody|someone|there) always is\b|\bthey always are\b|\bmost of them are\b", "always is"),
    (r"\balways a reason\b", "always a reason"),
    (r",? honestly[.!?]", "honestly tag"),
    (r"\bcan we go outside\b", "repeat"),
    (r"\b(that's|that is|it's|isn't) not \w+, it's\b|\bisn't \w+, it's\b", "not X, it's Y zinger"),
    (r"\bdifferent things\b", "zinger"),
    (r"\bwho's (bleeding|hurt)\b|\bbleeding (and|who)\b", "who's bleeding"),
    (r"\bthat's a (good|perfect) (shift|day|night)\b|\bin my book\b", "good shift"),
    (r"\b(bit|rule|thing) i care about\b", "repeat"),
    (r"\bnew place, new\b", "repeat"),
    (r"\b(say|call) it (sooner|louder)\b|\bsaid it too\b", "repeat"),
    (r"\bi'll find (them|it)\b", "repeat"),
]
NARRATOR = {"send_word", "on_break"}
#: Only checked in banter and the short bond lines; in a long speech these read naturally.
SHORT_ONLY = {"postcard list", "postcard closer", "everybody out", "who's bleeding", "good shift"}


def tic_problems(data=None):
    """Stock phrases, and any four word run that three or more recruits' banter shares."""
    data = load() if data is None else data
    bad, seen = [], {}
    for rid, d in data.items():
        for where, t in _texts(rid, d):
            if where.split()[-1] in NARRATOR:
                continue
            spoken_short = where.startswith(("banter", "line"))
            for rx, why in TICS:
                if why in SHORT_ONLY and not spoken_short:
                    continue
                if re.search(rx, t, re.I):
                    bad.append(f"{rid} {where}: {why}: {t!r}")
            if where.startswith("banter"):
                w = re.findall(r"[\w']+", t.lower())
                for g in {" ".join(w[i:i + 4]) for i in range(len(w) - 3)}:
                    seen.setdefault(g, set()).add(rid)
    for g, rids in sorted(seen.items()):
        if len(rids) >= 3:
            bad.append(f"banter shared by {len(rids)} recruits: {g!r} ({', '.join(sorted(rids))})")
    return bad


def problems():
    from tools.build_tempest_quests import voice_problems
    recruits = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]
    names = {r["recruit_id"]: r["name"].split()[0] for r in recruits}
    bad = []
    for rid, d in load().items():
        if rid not in names:
            bad.append(f"{rid}: not a recruit")
            continue
        if rid in NEVER_TOUCH or rid in PILOT:
            bad.append(f"{rid}: hand-held elsewhere, not a Wave 2 file")
        others = {first for oid, first in names.items() if oid != rid and first != names[rid]}
        for where, t in _texts(rid, d):
            bad += [f"{rid} {where}: {x}" for x in voice_problems(t)]
            hit = others & set(re.findall(r"[A-ZÀ-Ý][\w'À-ÿ-]+", t))
            if hit:
                bad.append(f"{rid} {where}: names another recruit {sorted(hit)}")
        for k, t in d.get("recruit_text", {}).items():
            if k not in TEXT_FIELDS:
                bad.append(f"{rid}: recruit_text has unknown field {k}")
            elif k in ("before", "adjustment", "now", "forward") and len(t) > SECTION_MAX:
                bad.append(f"{rid}: {k} is {len(t)} characters, over {SECTION_MAX}")
        b = d.get("bond")
        if b:
            for k in STAGES:
                if k not in b.get("stages", {}):
                    bad.append(f"{rid}: no {k} stage")
            for k in LINE_KEYS:
                if k not in b.get("lines", {}):
                    bad.append(f"{rid}: no {k} line")
            for k in ("warmth", "nerve", "pride", "restless"):
                if not 0.3 <= float(b.get("dials", {}).get(k, 0)) <= 1.6:
                    bad.append(f"{rid}: dial {k} missing or out of range")
            for k in b.get("likes", []) + b.get("dislikes", []):
                if k not in LIKES:
                    bad.append(f"{rid}: unknown like or dislike {k}")
            for m in b.get("moments", []):
                if m.get("when") not in WHEN:
                    bad.append(f"{rid}: moment {m.get('id')} has unknown when {m.get('when')}")
        for trig in d.get("banter", {}):
            if trig not in TRIGGERS:
                bad.append(f"{rid}: unknown banter trigger {trig}")
    return bad + tic_problems()


if __name__ == "__main__":
    bad = problems()
    for b in bad:
        print("  -", b)
    print(f"{len(load())} Wave 2 files, {len(bad)} problems")
    sys.exit(1 if bad else 0)
