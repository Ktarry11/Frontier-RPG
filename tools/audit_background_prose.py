#!/usr/bin/env python3
"""Which recruit backgrounds read like a machine wrote them?

    PYTHONPATH=. python3 tools/audit_background_prose.py [--worst 20] [--show NAME]

Kyle, 7 Nov, with Adrian Mendoza's "Looking Forward" tab on screen reading
"He would like to be asked. That is the whole of it.":

    "we have these super weird 'off' AI written backgrounds. Lets aim for some
     life bro. dont be so....cold/lame/odd. People should feel these are real
     humans."

He is right, and the useful thing this tool established is that he is right
about SOME of them. 68 recruits x 4 sections is 272 pieces of prose, and the
tics are not spread evenly across them - Adrian alone trips six different
patterns, while most sections trip none. Rewriting all 272 would be expensive
and would damage the ones that already work ("He still has the whistle. He has
never blown it here. He checks that it is there about four times a day." is
not the problem).

WHAT THE TICS ACTUALLY ARE. Every pattern below is a way of having the
NARRATOR know the character better than the character does, which is the thing
that reads as uncanny rather than as a person:

  verdict      a short declarative that summarises the character and closes
               the subject - "That is the whole of it", "That is all there is
               to it". A person does not come with a summary.
  omniscient   the narrator reporting what the character has NOT realised, is
               not saying, or would not admit. Nobody can see this from the
               outside, so its presence announces an author.
  tidy         "and he knows precisely how that sounds", "the way a man does"
               - the character pre-empting the reader's judgement, which real
               people do not do on cue.
  aphorism     a one-sentence paragraph used as a drum beat before the real
               paragraph. Fine once; 47 sections do it, and in a row it reads
               as a format rather than as writing.

Score is the count of distinct tic families a section trips, then total hits.
It reports; it rewrites nothing.
"""

import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROSTER = os.path.join(ROOT, "data/npcs/recruits.json")

#: family -> (label, [patterns]). Grouped so a section using three flavours of
#: the same trick scores once for the trick, not three times.
TICS = {
    "verdict": ("closing verdict", [
        r"That is (the whole of it|all( there is( to it)?)?)\.",
        r"That is (what|who) (he|she|they) (is|are)\.",
        r"\bAnd that is that\b",
    ]),
    "omniscient": ("narrator knows what they do not", [
        r"has not (yet )?occurred to (him|her|them)",
        r"(does not|has never|will not) (quite )?(know|realise|realize|see) (that|how|why|it)",
        r"than (he|she|they) (would |will |has any intention of |have any intention of )?"
        r"(admit|admits|mention|mentions|say|says)",
        r"never (told|said|mentioned|explained) (this to )?anyone",
        r"(does not|never) (say|explain|mention|tell anyone) why",
    ]),
    "tidy": ("pre-empts the reader", [
        r"knows (precisely |exactly )?how (that|it) sounds",
        r"is clear-eyed about",
        r"the way (a|an) \w+ does\b",
        r"\band (he|she|they) means? it\b",
    ]),
    "aphorism": ("one-line drum beat opener", [
        r"\A[^\n]{1,70}\.\n\n",
    ]),
    "precision": ("suspiciously exact tally", [
        r"about \w+ times a (day|week|month)",
        r"\b(four|three|five|six|eleven|twelve) times a (day|week)\b",
    ]),
}


def score(text):
    hits = {}
    for key, (label, pats) in TICS.items():
        n = sum(len(re.findall(p, text, re.M)) for p in pats)
        if n:
            hits[key] = n
    return hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worst", type=int, default=20)
    ap.add_argument("--show", help="print one recruit's full sections")
    args = ap.parse_args()

    with open(ROSTER, encoding="utf-8") as fh:
        recruits = json.load(fh)["recruits"]

    if args.show:
        for r in recruits:
            if args.show.lower() in r.get("name", "").lower():
                print(f"  == {r['name']}  ({r.get('char_class')}, lvl {r.get('level')})")
                for k in ("before", "adjustment", "now", "forward"):
                    v = (r.get("background_sections") or {}).get(k)
                    if not v:
                        continue
                    h = score(v)
                    tags = " ".join(f"[{TICS[t][0]}]" for t in h)
                    print(f"\n  -- {k}  {tags}")
                    for line in v.split("\n"):
                        print(f"     {line}")
                print()
        return 0

    rows = []
    for r in recruits:
        total, fams, detail = 0, set(), []
        for k in ("before", "adjustment", "now", "forward"):
            v = (r.get("background_sections") or {}).get(k)
            if not v:
                continue
            h = score(v)
            if h:
                total += sum(h.values())
                fams |= set(h)
                detail.append((k, h))
        rows.append((len(fams), total, r.get("name"), r.get("char_class"), detail))

    rows.sort(key=lambda t: (-t[0], -t[1], t[2]))
    clean = sum(1 for r in rows if r[0] == 0)
    print(f"  {len(rows)} recruits, {len(rows)*4} sections")
    print(f"  {clean} recruits trip no tic at all; {len(rows)-clean} trip at least one\n")
    print(f"  {'recruit':24}{'class':14}{'fams':>5}{'hits':>6}  what")
    for fams, total, name, cls, detail in rows[:args.worst]:
        if not fams:
            break
        what = "; ".join(f"{k}: " + ",".join(TICS[t][0] for t in h)
                         for k, h in detail)
        print(f"  {str(name)[:23]:24}{str(cls)[:13]:14}{fams:>5}{total:>6}  {what[:70]}")

    print("\n  -- by family ------------------------------------------")
    for key, (label, _p) in TICS.items():
        n = sum(1 for _f, _t, _n, _c, d in rows for _k, h in d if key in h)
        print(f"  {n:>4} sections  {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
