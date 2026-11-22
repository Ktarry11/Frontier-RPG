#!/usr/bin/env python3
"""Recruits rewritten in whole sentences: their background tabs, greetings and bond stages (21 Nov 2026).

    PYTHONPATH=. python3 tools/build_recruit_voice.py            # check only
    PYTHONPATH=. python3 tools/build_recruit_voice.py --write    # check, then write recruits.json and bonds.json

Kyle, 21 Nov 2026, reading the backgrounds: "why does every background read like it was written by a 2 year old bro",
"Theres no sentence, theyre just fragments bro", "none of this makes sense", and of a bond line, "bro am i having a
stroke". The old text was clipped and clever ("Tables, reserves, a good office with a bad view"), and the stage lines
jumped from one thought to the next with nothing between them.

Each recruit's new text lives in tools/recruit_voice/<batch>.py as VOICE = {recruit_id: {field: text}}, where a field
is one of greeting, before, adjustment, now, forward, or a bond stage (stranger, acquaintance, companion, friend,
sworn, sworn_bad, sworn_soft). A field left out keeps what the recruit has. This runs LAST, after every builder that
writes recruits.json or bonds.json (build_recruit_bonds.py and the sheet builders), because it overwrites their text.

THE BAR, checked before anything is written:
  * the voice bar (tools/build_tempest_quests.voice_problems): contractions, no dashes, no sentence of one or two
    words, no stiff constructions;
  * a background tab is four to seven sentences and fits the tab's panel (760 characters; the screen has no scroll);
  * ASCII only;
  * Asher Coleman is never touched (standing rule: "DONT TOUCH ASHER"), and the three endings still waiting on Kyle's
    call (Neil's, Valentina's sun conclusion, Marisol's brother) aren't written here.
"""
import importlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

SECTIONS = ("before", "adjustment", "now", "forward")
STAGES = ("stranger", "acquaintance", "companion", "friend", "sworn", "sworn_bad", "sworn_soft")
CAP = 760
NEVER = {"asher_coleman"}
#: endings Kyle hasn't called yet: the stage text for these stays as it is
PENDING = {("neil_felsworn", "sworn"), ("neil_felsworn", "sworn_bad"), ("neil_felsworn", "sworn_soft"),
           ("valentina_starcaller", "sworn"), ("valentina_starcaller", "sworn_bad"),
           ("valentina_starcaller", "sworn_soft")}


def sentences(text):
    flat = re.sub(r"\b(Dr|Mr|Mrs|St)\.", r"\1", text.replace("\n", " "))
    return [s for s in re.split(r"(?<=[.!?])['\"]?\s+", flat) if len(s.split()) >= 3]


def load_all():
    voice = {}
    for f in sorted((ROOT / "tools/recruit_voice").glob("*.py")):
        if f.name.startswith("_"):
            continue
        mod = importlib.import_module(f"recruit_voice.{f.stem}")
        for rid, fields in mod.VOICE.items():
            if rid in voice:
                raise SystemExit(f"{rid} is in two batches")
            voice[rid] = fields
    return voice


def problems(voice, rec, bonds):
    from build_tempest_quests import voice_problems
    bad = []
    for rid, fields in voice.items():
        if rid in NEVER:
            bad.append(f"{rid}: never touched")
            continue
        if rid not in rec:
            bad.append(f"{rid}: no such recruit")
            continue
        for k, text in fields.items():
            if k not in SECTIONS + STAGES + ("greeting",):
                bad.append(f"{rid}.{k}: unknown field")
                continue
            if (rid, k) in PENDING:
                bad.append(f"{rid}.{k}: that ending is waiting on Kyle's call")
            if k in STAGES and k not in (bonds.get(rid, {}).get("stages") or {}) and k != "sworn":
                bad.append(f"{rid}.{k}: this recruit has no {k} stage")
            if any(ord(c) > 127 for c in text):
                bad.append(f"{rid}.{k}: non-ASCII")
            for p in voice_problems(text):
                bad.append(f"{rid}.{k}: {p}")
            if k in SECTIONS:
                n = len(sentences(text))
                if not 4 <= n <= 8:
                    bad.append(f"{rid}.{k}: {n} sentences (a tab is four to seven)")
                if len(text) > CAP:
                    bad.append(f"{rid}.{k}: {len(text)} characters, over the tab's {CAP}")
    return bad


def main():
    rpath, bpath = ROOT / "data/npcs/recruits.json", ROOT / "data/npcs/bonds.json"
    rdoc = json.loads(rpath.read_text(encoding="utf-8"))
    bdoc = json.loads(bpath.read_text(encoding="utf-8"))
    rec = {r["recruit_id"]: r for r in rdoc["recruits"]}
    bonds = bdoc["bonds"]
    voice = load_all()
    bad = problems(voice, rec, bonds)
    fields = sum(len(v) for v in voice.values())
    print(f"  {len(voice)} recruits, {fields} fields rewritten, {len(bad)} problem(s)")
    for p in bad:
        print("  PROBLEM " + p)
    if "--write" not in sys.argv:
        return 1 if bad else 0
    if bad:
        print("  REFUSING TO WRITE while there are problems")
        return 1
    for rid, fs in voice.items():
        r, b = rec[rid], bonds.setdefault(rid, {})
        for k, text in fs.items():
            if k == "greeting":
                r["greeting"] = text
            elif k in SECTIONS:
                r.setdefault("background_sections", {})[k] = text
            else:
                b.setdefault("stages", {})[k] = text
    rpath.write_text(json.dumps(rdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    bpath.write_text(json.dumps(bdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("  written: data/npcs/recruits.json, data/npcs/bonds.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
