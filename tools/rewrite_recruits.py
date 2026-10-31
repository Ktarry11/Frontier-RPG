#!/usr/bin/env python3
"""Apply a batch of hand-written recruit rewrites into data/npcs/recruits.json.

    PYTHONPATH=. python3 tools/rewrite_recruits.py --check
    PYTHONPATH=. python3 tools/rewrite_recruits.py

Kyle, 2026-10-31: "We 100% NEED to fix up writting. It's too fake. No recruits feel alive."

WHY THE OLD ONES FELT FAKE, measured rather than guessed:

    41/44  the `forward` section began with the literal words "She wants" / "He wants"
    44/44  the same four sections in the same order, every time
    28/44  backstory opened "[job] in [named city] for N years"
    20/44  `adjustment` began "Three years ago he/she came through..."
    12/44  contained the literal sentence "is not adapting"

Each one read fine alone. Four in a row and you can feel the mould. Underneath the phrasing was
the worse problem: every single recruit was a competent professional who had quietly found
their calling. Nobody failing, nobody wrong about themselves, nobody hard work. Forty-four
well-adjusted adults who all landed on their feet is not a cast, it is one character with
forty-four CVs.

THE SECTION KEYS ARE FIXED. ui/screens/background_screen.py draws exactly the four tabs in
Character.BACKGROUND_SECTION_KEYS, so the variety has to live in the prose.

ASHER COLEMAN IS NEVER TOUCHED. He is hand-authored and fixed by Kyle's standing instruction;
this refuses to write to him even if a batch names him.

--check re-runs the measurements above over the current data, so the mould cannot creep back in
unnoticed.
"""
import argparse
import collections
import importlib
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

NEVER_TOUCH = {"asher_coleman"}

BATCH_MODULES = [
    "tools.writing.recruits_batch1",
    "tools.writing.recruits_batch2",
    "tools.writing.recruits_batch3",
    "tools.writing.recruits_batch4",
    "tools.writing.recruits_batch5",
    "tools.writing.recruits_batch6",
    # Register pass. Kyle, 2026-10-31: "avoid weird tics... Avoid the weird prose."
    # Overlays the batches above field-by-field, so these carry only rewritten sections.
    "tools.writing.recruits_batch7a",
    "tools.writing.recruits_batch7b",
    "tools.writing.recruits_batch7c",
]

#: The tics the rewrite exists to kill. --check counts them and fails if any survive.
TICS = {
    '"She/He wants" opening `forward`': (lambda r: bool(
        re.match(r'^(She|He|They) wants?\b',
                 str((r.get("background_sections") or {}).get("forward", "")).strip()))),
    '"is/was not adapting"': (lambda r: bool(re.search(
        r'\b(is|was|has|have)\s+n[o\']t\s+adapt', _all_text(r), re.I))),
    '"came through"': (lambda r: "came through" in _all_text(r).lower()),
    # THE INTEGRATION WAS THREE YEARS AGO and claude/integration_timeline.md records that two
    # separate passes have already got this wrong. A sentence dating the MERGE is constrained; a
    # sentence dating a PERSON ("they made it up four years before the world ended") is not, so
    # this only catches the phrasings that date the merge itself.
    'mis-dating the Integration': (lambda r: bool(re.search(
        r'(four|five|two) years ago\b|'
        r'was not on this world (four|five|two) years ago|'
        r'(four|five|two) years (since|after) (it|the Integration)', _all_text(r), re.I))),
    '"[job] in [City] for N years" opener': (lambda r: bool(re.match(
        r'^[A-Z][a-z]+\b[^.]{0,60}\bin [A-Z][a-z]+,?\s+(for\s+)?'
        r'(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|'
        r'fifteen|sixteen|seventeen|eighteen|nineteen|twenty)\b',
        str(r.get("backstory", "")).strip()))),
}


#: MY OWN TICS, not the old text's. Kyle, 2026-10-31: "Ok also avoid weird tics. I know you can
#: write well. Avoid the weird prose."
#:
#: He was right and it measured. The first rewrite replaced one template with another one: 168
#: flat negations across 42 of 43 characters, 92 em dashes in 38 of them, and 51 trailing
#: "..., which is ..." closers in 31. Every character was being narrated by the same dry,
#: withholding voice that will not use a contraction. That is a house style, and a house style
#: is the thing we were removing.
#:
#: These are capped as a SHARE OF THE CAST rather than banned, because any one of them is fine in
#: one character's mouth and a tic in twenty. The cap is what stops a narrator emerging.
STYLE_CAPS = {
    "flat negation (does not / has not / is not)": (r'\b(does|did|has|have|is|was|would|could) not\b', 0.55),
    "em dash":                                     (r'—', 0.45),
    '", which is/was ..." closer':                 (r', which (is|was|has|he|she|they)\b', 0.30),
    '"is aware"':                                  (r'\b(is|was) aware\b', 0.20),
    '"has stopped"':                               (r'\b(has|have) stopped\b', 0.20),
    '"never once"':                                (r'\bnever once\b', 0.15),
    '"will tell you"':                             (r'\b(will|would) tell you\b', 0.15),
    '"he/she says it like"':                       (r'\bsays (it|that|so)\b', 0.20),
}


def _all_text(r):
    return " ".join([str(r.get("backstory", "")), str(r.get("greeting", ""))]
                    + [str(v) for v in (r.get("background_sections") or {}).values()])


def load_batches():
    out = {}
    for mod in BATCH_MODULES:
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError:
            continue
        for rid, fields in m.BATCH.items():
            if rid in NEVER_TOUCH:
                print(f"  refusing to rewrite {rid} - hand-authored and fixed")
                continue
            # A later batch OVERLAYS an earlier one, field by field, which is how the family
            # pass works: batch 6 carries only the sections that gained a thread and leaves the
            # rest of each character alone.
            if rid in out:
                merged = dict(out[rid])
                merged.update(fields)
                fields = merged
            out[rid] = fields
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="measure the tics, write nothing")
    args = ap.parse_args()

    path = ROOT / "data/npcs/recruits.json"
    data = json.loads(path.read_text(), object_pairs_hook=collections.OrderedDict)
    block = data.get("recruits", data)
    records = block if isinstance(block, list) else list(block.values())
    by_id = {r["recruit_id"]: r for r in records}

    if not args.check:
        batches = load_batches()
        written = 0
        for rid, fields in batches.items():
            r = by_id.get(rid)
            if r is None:
                print(f"  !! no recruit called {rid}")
                continue
            if "greeting" in fields:
                r["greeting"] = fields["greeting"]
            if "backstory" in fields:
                r["backstory"] = fields["backstory"]
            sections = r.setdefault("background_sections", collections.OrderedDict())
            for key in ("before", "adjustment", "forward", "now"):
                if key in fields:
                    sections[key] = fields[key]
            written += 1
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        print(f"\n{written} recruits rewritten")

    # ---- the measurements, over whatever is on disk now ------------------------------------
    rewritten = set(load_batches()) if not args.check else set(load_batches())
    print(f"\n{len(records)} recruits on disk, {len(rewritten)} covered by a batch so far\n")
    failed = False
    for label, test in TICS.items():
        hits = [r for r in records if r["recruit_id"] not in NEVER_TOUCH and test(r)]
        # A tic surviving in a recruit nobody has rewritten yet is expected. One surviving in a
        # recruit this pass claims to have rewritten is the pass failing at its only job.
        done = [r["name"] for r in hits if r["recruit_id"] in rewritten]
        if done:
            failed = True
        print(f"  {len(hits):2d}/{len(records)}  {label}"
              + ("   <-- IN A REWRITTEN RECRUIT" if done else ""))
        if done:
            print(f"        {done}")

    # ---- style caps: is a narrator emerging? ----------------------------------------------
    import re as _re
    pool = [r for r in records if r["recruit_id"] not in NEVER_TOUCH]
    print()
    for label, (pat, cap) in STYLE_CAPS.items():
        hit = [r["name"] for r in pool if _re.search(pat, _all_text(r), _re.I)]
        share = len(hit) / max(1, len(pool))
        over = share > cap
        if over:
            failed = True
        print(f"  {share:5.0%} of the cast (cap {cap:.0%})  {label}"
              + ("   <-- A NARRATOR IS EMERGING" if over else ""))

    lens = [len(str(r.get("backstory", "")).split()) for r in records]
    import statistics
    print(f"\n  backstory words: median {statistics.median(lens):.0f}, "
          f"range {min(lens)}-{max(lens)}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
