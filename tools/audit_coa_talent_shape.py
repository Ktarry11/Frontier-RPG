#!/usr/bin/env python3
"""
Does a talent change what you DO, or only how big a number is?

    PYTHONPATH=. python3 tools/audit_coa_talent_shape.py [--class Primalist] [--examples N]

Kyle, 2026-11-01, looking at Tinker: "theyre mostly just flat % boosts that are boring".

THE WHOLE AUDIT IN ONE NUMBER. A talent tree's job is to make the player choose. A node that
reads "+3% armor" is not a choice, it is a tax you pay on the way to the node you wanted; a tree
made mostly of those is a tree that could be replaced by a slider. So this classifies every
talent on both sides - Ascension's CoA and ours - by what it DOES, and prints the ratio.

It compares LIKE WITH LIKE, which took two goes to get right. Comparing CoA's *abilities*
against our *talents* is meaningless, because an ability is mechanical by definition - it is a
button that does a thing. Only talent-to-talent says anything.

THE REFERENCE DATA IS NOT OCR ANY MORE. tools/extract_coa_reference.py reads the community
screenshot archive, and it works, but allthingscoa.com publishes the same thing as structured
JSON scraped from Ascension's own builder - 7,224 nodes across 21 classes, with rank-by-rank
descriptions, tree positions, node connections, passive flags and level requirements. Fifteen
seconds and no OCR noise, against three and a half hours and word-level errors. The OCR tool
stays because it is the only route if that site goes away, and because it is the only source for
the TRAINER data (ability costs, ranges and cast types), which the builder JSON does not carry.

WHAT COUNTS AS MECHANICAL. Not a judgement call per node - a pattern over the description:
a node is mechanical if it changes a rule ("now also", "instead", "each time you", "gain a
charge", "transforms"), and scalar if it only moves a magnitude ("increases X by N%"). The
patterns are below and are meant to be argued with; the point is that the same rule is applied
to both sides, so the RATIO is comparable even where an individual call is debatable.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

COA = ROOT / "data/reference/coa"
OURS = ROOT / "data/talents"

#: Changes a RULE. Any of these and the node is doing something a slider could not.
MECH = re.compile(r"""(?ix)
    \b(now\s|instead|also\b|additionally|each\s+time|when(ever)?\s+you|upon\b|
    transform(s|ing)?|becomes?|replaces?|allows?|enables?|can\s+now|grants?\s+a\b|
    summons?|applies|triggers?|resets?|refunds?|charges?|consumes?|
    stack(s|ing)?\b|proc(s|)\b|spread(s|)\b|bounces?|cleaves?|
    no\s+longer|removes?\s+the|causes?\b|gain(s|ing)?\s+(a|an|the)\b)
""")
#: Only moves a magnitude.
SCALAR = re.compile(r"""(?ix)
    ^\s*(increas|reduc|decreas|improv|lower|rais|boost)\w*\s
    .{0,90}?\bby\s+[\d.]+\s*%?
""")


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s or "")).strip()


def classify(text):
    """'mech' | 'scalar' | 'none'. The order matters: a node that moves a number AND changes a
    rule is mechanical, because the rule change is the part the player is choosing."""
    t = strip_html(text)
    if not t:
        return "none"
    if MECH.search(t):
        return "mech"
    if SCALAR.search(t) or "%" in t:
        return "scalar"
    return "mech"


def coa_rows():
    """(class, spec, name, text) for every CoA TALENT. Excludes the shared class tree (tab 87),
    which every class has identically and which would dilute all 21 the same way."""
    meta = (COA / "_classes-meta.js").read_text()
    tabmap = {}
    for m in re.finditer(r'name:\s*"([^"]+)",\s*slug:\s*"([a-z-]+)".*?specs:\s*\[(.*?)\]\}',
                         meta, re.S):
        cls, slug, body = m.group(1), m.group(2), m.group(3)
        for s in re.finditer(r'name:\s*"([^"]+)",\s*role:\s*"([^"]+)",\s*tab:\s*(\d+)', body):
            tabmap[(slug, int(s.group(3)))] = (cls, s.group(1), s.group(2))
    out = []
    for p in sorted(COA.glob("*.json")):
        slug = p.stem
        for n in json.loads(p.read_text()):
            hit = tabmap.get((slug, n.get("tabId")))
            if not hit:
                continue                      # the shared class tree, or an unmapped tab
            cls, spec, role = hit
            out.append((cls, spec, role, n.get("name", "?"), n.get("description", "")))
    return out


def our_rows():
    """(class, spec, name, text) for every talent we ship."""
    out = []
    for p in sorted(OURS.glob("*.json")):
        d = json.loads(p.read_text())
        spec = d.get("spec_name") or p.stem
        cls = spec.split()[0]
        for known in ("Knight of Xoroth", "Sun Cleric", "Witch Doctor", "Witch Hunter"):
            if spec.startswith(known):
                cls = known
        for n in d.get("nodes", []):
            # An unlock node is mechanical by construction - it hands the player a new button.
            text = n.get("description", "")
            if "unlock_ability" in (n.get("effects") or {}):
                text = "now grants " + text
            out.append((cls, spec[len(cls):].strip() or spec, None, n.get("name", "?"), text))
    return out


def tally(rows):
    by = defaultdict(lambda: [0, 0])
    for (cls, spec, _role, _name, text) in rows:
        k = classify(text)
        if k == "none":
            continue
        by[(cls, spec)][0 if k == "mech" else 1] += 1
    return by


def main(argv):
    only = argv[argv.index("--class") + 1].lower() if "--class" in argv else None
    nex = int(argv[argv.index("--examples") + 1]) if "--examples" in argv else 0

    coa, ours = tally(coa_rows()), tally(our_rows())
    coa_cls = defaultdict(lambda: [0, 0])
    our_cls = defaultdict(lambda: [0, 0])
    for (c, _s), (m, sc) in coa.items():
        coa_cls[c][0] += m
        coa_cls[c][1] += sc
    for (c, _s), (m, sc) in ours.items():
        our_cls[c][0] += m
        our_cls[c][1] += sc

    pct = lambda m, s: (100 * s // (m + s)) if (m + s) else 0
    print(f"{'CLASS':20} {'CoA talents':>12} {'scalar':>7}   {'OURS':>10} {'scalar':>7}   gap")
    print("-" * 74)
    worst = []
    for c in sorted(set(coa_cls) | set(our_cls)):
        if only and c.lower() != only:
            continue
        cm, cs = coa_cls.get(c, [0, 0])
        om, os_ = our_cls.get(c, [0, 0])
        cp, op = pct(cm, cs), pct(om, os_)
        gap = op - cp if (cm + cs and om + os_) else 0
        worst.append((gap, c, cm + cs, cp, om + os_, op))
        flag = "  <<<" if gap >= 30 else ""
        print(f"{c:20} {cm + cs:12} {cp:6}%   {om + os_:10} {op:6}%   {gap:+4}{flag}")

    if not only:
        tcm = sum(v[0] for v in coa_cls.values())
        tcs = sum(v[1] for v in coa_cls.values())
        tom = sum(v[0] for v in our_cls.values())
        tos = sum(v[1] for v in our_cls.values())
        print("-" * 74)
        print(f"{'ALL':20} {tcm + tcs:12} {pct(tcm, tcs):6}%   "
              f"{tom + tos:10} {pct(tom, tos):6}%   {pct(tom, tos) - pct(tcm, tcs):+4}")

    if nex:
        print(f"\nOur most scalar talents (a sample of what '{nex}' looks like):")
        shown = 0
        for (cls, spec, _r, name, text) in our_rows():
            if only and cls.lower() != only:
                continue
            if classify(text) == "scalar":
                print(f"  [{cls} {spec}] {name}: {strip_html(text)[:95]}")
                shown += 1
                if shown >= nex:
                    break
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
