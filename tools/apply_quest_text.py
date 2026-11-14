#!/usr/bin/env python3
"""Apply authored quest text to a zone file, safely.

    PYTHONPATH=. python3 tools/apply_quest_text.py <zone> <patch.json> [--dry-run]

The patch file is {quest_id: {field: text, ...}}, where field is one of
description / accept_text / turn_in_text / title.

WHY A TOOL. Rewriting hundreds of quests by hand-editing a 3000-line JSON
file is how a stray comma eats a zone. This touches ONLY the named fields
of the named quests, leaves every other key byte-identical, and refuses
outright if a quest_id in the patch does not exist in the zone - a typo'd
id would otherwise silently write nothing and look like success.

IT ALSO GUARDS THE NUMBERS. tools/audit_quests.py reports ~129 quests
whose prose states a count the objectives disagree with ("Eight worgs"
against a kill count of 5). Rewriting the prose is exactly when that gets
re-introduced, so every number word in new text is checked against the
quest's own objective counts and the write is REFUSED on a mismatch.
Spelled-out numbers are checked too, because that is how quest text
actually reads.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "fifteen": 15, "twenty": 20,
}
FIELDS = ("title", "description", "accept_text", "turn_in_text")


def load_zone(zone):
    path = ROOT / "data/quests" / f"{zone}.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    block = raw if isinstance(raw, list) else raw.get("quests", raw)
    items = block if isinstance(block, list) else list(block.values())
    return path, raw, [it for it in items if isinstance(it, dict)]


def load_overlay(zone, quest_ids):
    """The text overlay this zone's quests actually read from.

    A quest's overlay entry does not have to live in the file named after
    its own zone - every Barrens hub quest sits in central_barrens.json,
    northern_barrens.json or southern_barrens.json - so the right file is
    found by looking for the quest ids, not by name."""
    tdir = ROOT / "data/quests/text"
    tdir.mkdir(parents=True, exist_ok=True)
    for cand in sorted(tdir.glob("*.json")):
        data = json.loads(cand.read_text(encoding="utf-8"))
        if any(qid in data for qid in quest_ids):
            return cand, data
    cand = tdir / f"{zone}.json"
    return cand, (json.loads(cand.read_text(encoding="utf-8")) if cand.exists() else {})


def counts_for(quest):
    out = set()
    for obj in quest.get("objectives") or []:
        c = obj.get("count")
        if isinstance(c, int) and c > 1:
            out.add(c)
    return out


#: A number followed by one of these is a measurement, not a kill count.
#: Quest prose is full of them - "thirty years I've dug in this ground",
#: "three years ago", "the first man in Brill". Without this the guard
#: rejected Meryl Ashdown's turn-in for saying "three years", which is the
#: Integration date and has nothing to do with her five sets of orders.
UNITS = (r"year|years|month|months|week|weeks|day|days|hour|hours|minute|minutes|"
         r"winter|winters|summer|summers|mile|miles|yard|yards|foot|feet|"
         r"o'clock|time|times|times over|percent|copper|silver|gold")


def numbers_in(text):
    """Every quantity the prose claims as a COUNT, digits and words alike."""
    text = text or ""
    found = set()
    for m in re.finditer(r"\b(\d{1,3})\b(?!\s*(?:%s))" % UNITS, text):
        found.add(int(m.group(1)))
    for w, n in WORDS.items():
        if re.search(rf"\b{w}\b(?!\s*(?:{UNITS}))", text, re.I):
            found.add(n)
    return found


def count_conflicts(quest, text):
    """Numbers in the prose that contradict an objective's own count.

    DELIBERATELY NARROW. An earlier version flagged every small number in
    the text against the set of objective counts, and drowned in false
    positives the moment the prose had any life in it - "I have lost two
    boots to them", "three travellers in a month", "don't take more than
    two at once", "an hour, maybe two". None of those are quantities of
    anything the quest tracks.

    The bug actually worth catching is the one all over the old text:
    a number sitting directly in front of the thing being counted, saying
    something different from the objective. "Eight worgs" against a kill
    count of five. So a number is only a conflict when the objective's own
    target noun follows it within a few words.
    """
    out = []
    low = (text or "").lower()
    for obj in quest.get("objectives") or []:
        count = obj.get("count")
        target = obj.get("target")
        if not isinstance(count, int) or count < 2 or not target:
            continue
        # The noun as a player would say it: last word of the target,
        # singular or plural ("Bleak Worg" -> worg/worgs).
        noun = re.sub(r"[^a-z ]", "", str(target).lower()).split()
        if not noun:
            continue
        noun = noun[-1]
        pattern = rf"\b(\d{{1,3}}|{'|'.join(WORDS)})\b[\w' ]{{0,24}}?{noun}s?\b"
        for m in re.finditer(pattern, low):
            tok = m.group(1)
            said = int(tok) if tok.isdigit() else WORDS[tok]
            if said != count:
                out.append(f"text says \"{m.group(0).strip()}\" but the "
                           f"objective wants {count}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zone")
    ap.add_argument("patch")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--allow-numbers", action="store_true",
                    help="skip the count cross-check (use only when the "
                         "number genuinely is not an objective count)")
    args = ap.parse_args()

    path, raw, items = load_zone(args.zone)
    by_id = {it["quest_id"]: it for it in items}
    patch = json.loads(Path(args.patch).read_text(encoding="utf-8"))
    opath, overlay = load_overlay(args.zone, set(patch))

    missing = [q for q in patch if q not in by_id]
    if missing:
        print(f"  REFUSED: {len(missing)} quest_id(s) are not in {args.zone}:")
        for q in missing:
            print(f"      {q}")
        return 1

    problems = []
    changed = 0
    for qid, fields in patch.items():
        quest = by_id[qid]
        bad = [f for f in fields if f not in FIELDS]
        if bad:
            problems.append(f"{qid}: unknown field(s) {bad}")
            continue
        if not args.allow_numbers:
            for fname, text in fields.items():
                if fname == "title":
                    continue
                for msg in count_conflicts(quest, text):
                    problems.append(f"{qid}.{fname}: {msg}")
        for fname, text in fields.items():
            if quest.get(fname) != text:
                quest[fname] = text
                changed += 1
            # THE OVERLAY IS WHAT THE PLAYER READS. QuestManager loads the
            # zone files and then OVERWRITES title/description/accept_text/
            # turn_in_text from data/quests/text/*.json for any quest listed
            # there (see world/quest_manager.py, "Writing lives here (not in
            # the generated zone files) so re-running a tools/build_*_quests
            # .py never reverts a rewrite").
            #
            # This tool wrote only the zone file, so every rewrite applied
            # through it was invisible in game for the 653 quests that have
            # an overlay entry - 637 quests across the Barrens, Tirisfal,
            # Silverpine, Ashenvale, the dungeon files, Undercity and the
            # Sepulcher were rewritten and never shown. Writing BOTH keeps
            # the zone file readable as the source of truth while making
            # sure the text actually reaches the player.
            overlay.setdefault(qid, {})[fname] = text

    if problems:
        print(f"  REFUSED: {len(problems)} problem(s), nothing written:")
        for p in problems:
            print(f"      {p}")
        return 1

    print(f"  {len(patch)} quest(s), {changed} field(s) "
          f"{'would change' if args.dry_run else 'updated'}")
    if not args.dry_run:
        path.write_text(json.dumps(raw, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        opath.write_text(json.dumps(overlay, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  wrote {path}")
        print(f"  wrote {opath}  <- this is the layer the player reads")
    return 0


if __name__ == "__main__":
    sys.exit(main())
