#!/usr/bin/env python3
"""Plain-speech rewrites of older quests and townsfolk, zone by zone. Idempotent.

    PYTHONPATH=. python3 tools/plain_text.py [--check]

Kyle, 14 Nov 2026, after Kael's Bastion: "Since it still irks me can you keep auditing npcs and
quest texts." The audit read a quest or two from every zone and then scanned all 1,208. Nearly
everything written before this week reads the same way: punchline endings ("Keep that wherever
you keep hope."), sentence fragments ("Shaft's quiet." "Iron hat. Bullhorn."), stage directions
in brackets, capital letters for emphasis, people introducing themselves like a form ("Gresk.
Foreman, this claim."), no contractions, dashes, and about 98 quests with their opening count cut
off by an older script.

Each zone's rewrite lives in tools/plain/<zone>.py:
  QUESTS            {quest_id: {description, accept_text, turn_in_text[, title]}}
  GREETINGS         {greetings file stem: {npc_id: text}}
  VENDOR_GREETINGS  {vendor_greetings file stem: {vendor_id: text}}

This writes data/quests/text/zzzz_plain.json, which the game lays over every other text file,
and merges the greetings into data/npcs/greetings/ and data/npcs/vendor_greetings/.

THE RULES every line is checked against (tools/build_tempest_quests.voice_problems plus these):
say what's wrong, where to go and what to bring back; the turn-in thanks you and stops;
contractions; no sentence under three words unless it's a real reaction; no dashes or shouted
capitals; and no counts in the prose (Kyle's standing rule: the objective line carries the
number). Bracketed pauses are fine.
"""
import argparse
import importlib
import json
import pkgutil
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_tempest_quests import voice_problems     # noqa: E402

OUT = ROOT / "data/quests/text/zzzz_plain.json"
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight",
         9: "nine", 10: "ten", 11: "eleven", 12: "twelve", 15: "fifteen", 20: "twenty"}
#: short sentences people really do say: reactions, greetings, questions, "I'm Kuraw." What
#: stays banned is the dramatic short line Kyle named ("Stay. I'm asking.", "Shaft's quiet.")
NATURAL = re.compile(r"^(?:.*\?|(?:oh|hi|hey|great|nice|good|right|okay|alright|yes|no|sorry|wow|"
                     r"thanks|cheers|perfect|brilliant|bad news|that's \w+|i'm [A-Z][\w']+)\b.*)$",
                     re.I)
SHOUT = re.compile(r"\b(?!(?:NPC|UI|XP|HP|II|III|IV|VI|MV|OK|AM|PM)\b)[A-Z]{3,}\b")


def modules():
    import tools.plain as pkg
    for m in sorted(pkgutil.iter_modules(pkg.__path__), key=lambda m: m.name):
        yield m.name, importlib.import_module(f"tools.plain.{m.name}")


def line_problems(text):
    # "go and kill five of them" is how people talk; the Tempest tic against it stays there
    bad = [p for p in voice_problems(text) if not p.startswith("kill N of X")
           and not (p.startswith("fragment: ") and NATURAL.match(p[11:-1]))]
    # bracketed pauses are fine (Kyle: "[A pause.]" - keep them)
    if (m := SHOUT.search(text)):
        bad.append(f"shouting: {m.group(0)}")
    if "–" in text or "—" in text:
        bad.append("dash")
    return bad


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        from world.quest_manager import QuestManager
        qm = QuestManager()
    bad, quests, greet, vgreet = [], {}, {}, {}
    for name, mod in modules():
        for qid, fields in getattr(mod, "QUESTS", {}).items():
            q = qm.quests.get(qid)
            if q is None:
                bad.append(f"{name}: no quest {qid}")
                continue
            for k in ("description", "accept_text", "turn_in_text"):
                if not fields.get(k):
                    bad.append(f"{qid}: no {k}")
            for k, t in fields.items():
                bad += [f"{qid} {k}: {p}" for p in line_problems(t)]
            # Kyle's standing rule: no counts in quest prose, the objective line carries the
            # number (tools/strip_prose_counts.py). A count written twice drifts.
            for k, t in fields.items():
                low = f" {t.lower()} "
                for o in q.objectives:
                    n = o.count
                    if n and n > 1 and (re.search(rf"\b{n}\b", t) or
                                        re.search(rf"\b{WORDS.get(n, '#')}\b (?!years|days|weeks|months|times|of us)", low)):
                        bad.append(f"{qid} {k}: states the count {n} ({o.target})")
            quests[qid] = fields
        for stem, rows in getattr(mod, "GREETINGS", {}).items():
            for nid, t in rows.items():
                bad += [f"{nid}: {p}" for p in line_problems(t)]
            greet.setdefault(stem, {}).update(rows)
        for stem, rows in getattr(mod, "VENDOR_GREETINGS", {}).items():
            for nid, t in rows.items():
                bad += [f"{nid}: {p}" for p in line_problems(t)]
            vgreet.setdefault(stem, {}).update(rows)
    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print(f"{len(quests)} quests, {sum(map(len, greet.values()))} greetings, "
          f"{sum(map(len, vgreet.values()))} shopkeepers pass")
    if args.check:
        return 0
    OUT.write_text(json.dumps(quests, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for folder, rows in (("greetings", greet), ("vendor_greetings", vgreet)):
        for stem, new in rows.items():
            p = ROOT / "data/npcs" / folder / f"{stem}.json"
            old = json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}
            old.update(new)
            p.write_text(json.dumps(old, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
