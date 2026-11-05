#!/usr/bin/env python3
"""Per-class authoring worksheet: CoA's real tree against ours.

    PYTHONPATH=. python3 tools/coa_class_worksheet.py tinker
    PYTHONPATH=. python3 tools/coa_class_worksheet.py --all

Kyle, 5 Nov 2026: "let's build the 21 CoA classes PROPERLY WITH REAL DATA
FROM THE WEBSITE."

The real data is on disk already - data/reference/coa/, from Ascension's own
CoA Builder, the same source allthingscoa.com presents. 2,902 talents and 700
abilities across all 21 classes, every one with its genuine description.

WHY A WORKSHEET AND NOT A DIRECT CONVERTER.

Writing CoA's talents straight into data/talents/ would ship dead data, and
this project has been burned by that repeatedly. Our `effects` blocks are
machine-readable keys the engine reads by name; CoA's descriptions are prose
referencing CoA's own abilities ("every 4th Scrap Shot grants Innate
Brilliance"). Only 16% are single-clause scalars that convert mechanically.
The other 84% are design decisions - which is exactly what Kyle wants, since
the flat scalars are the problem - and a converter that guessed at them would
produce 2,400 plausible-looking talents that do nothing.

So this emits the thing a person can actually work from: CoA's real tree, in
reading order, each node carrying its true name, rank count, prerequisites
and description, matched against our existing talent where one exists, with
the engine mechanic it needs already identified.

WHAT THE MECHANIC TAGS MEAN. They are matched against what the engine
ALREADY supports, not a wish list - cooldown reduction, stacking buffs,
procs, resource grants and health-threshold gates are all live systems here
(566 of our nodes already carry a proc). A tag is a pointer at the mechanism
to reach for, so authoring is a translation job rather than an invention job.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.coa_reference import (  # noqa: E402
    classes, nodes_for, clean, icon_for, SHARED_CLASS_TAB,
)

OUT_DIR = ROOT / "data/reference/coa_worksheets"

#: Engine mechanics we already have, and how to spot a talent that needs one.
#: Ordered most-specific first so a talent reports its defining mechanic
#: rather than an incidental mention.
MECHANICS = [
    ("transforms-ability", r"\bnow (?:causes|deals|grants|applies|summons|fires|hits)\b"
                           r"|\breplaces?\b|\btransforms?\b"),
    ("every-nth-cast",     r"every\s+\d+(?:st|nd|rd|th)\b"),
    ("charges",            r"\bcharges?\b"),
    ("proc-chance",        r"\b\d+%\s*chance\b"),
    ("stacking-buff",      r"\bstack(?:s|ing)?\b"),
    ("cooldown",           r"\bcooldown\b|\brecharge\b|\brefresh(?:es|ed)?\b|\breset"),
    ("resource-grant",     r"\bgenerat\w*\b|\brestores?\s+\d|\bgrants?\s+\d+\s*"
                           r"(?:rage|energy|mana|scrap|insanity|static)"),
    ("pet-summon",         r"\bpet\b|\bsummon\w*\b|\bturret\b|\bmechsuit\b|\bminion\b"
                           r"|\bguardian\b"),
    ("hp-threshold",       r"below\s+\d+%|above\s+\d+%|\bwounded\b"),
    ("aoe-cleave",         r"\bnearby\b|\bchain\b|\bcleave\b|within\s+\d+\s*yd"),
    ("dot-hot",            r"\bover\s+\d+\s*sec\b|\bperiodic\b|\bevery\s+\d+\s*sec\b"),
]

#: REAL-TIME ASSUMPTIONS THAT DO NOT SURVIVE A TURN-BASED PORT.
#:
#: Kyle, 5 Nov 2026: "it is important to note this is turn based. So we likely
#: won't use every single skill or talent. So we need to be creative when
#: needed."
#:
#: CoA is real-time WoW, and a large share of its talent text is priced in
#: seconds, yards and cast speed - none of which mean anything here. Combat
#: is a turn meter: there is no movement, no range, no global cooldown, and
#: haste makes you ACT MORE OFTEN rather than cast faster.
#:
#: Each entry carries the translation, not just the warning, because "this
#: says seconds" is useless on its own and "6 sec is about 2 turns" is a
#: decision someone can act on. Flagged separately from the mechanic tags: a
#: talent can be perfectly portable AND need its numbers reinterpreted.
TURN_BASED_RISKS = [
    ("duration-in-seconds", r"\b\d+\s*sec\b|\bseconds?\b",
     "seconds -> turns (roughly 3 sec per turn)"),
    ("range-or-movement", r"\b\d+\s*yd\b|\byards?\b|\bmovement speed\b|\bdash\b"
                          r"|\bcharge towards\b|\bleap\b|\bknock(?:back|s)\b",
     "no positioning in this engine - reprice as damage, a debuff, or drop it"),
    ("cast-speed", r"\bcast(?:ing)? (?:time|speed)\b|\b-?\d+% faster\b|\bchannel",
     "no cast times - haste here means acting more often, so route to turn_speed"),
    ("gcd", r"\bglobal cooldown\b|\bGCD\b",
     "no GCD exists - usually means the talent is free value, so drop or reprice"),
    ("real-time-window", r"\bwithin \d+ sec\b|\bfor the next \d+ sec\b",
     "becomes a turn window - state how many TURNS"),
]


#: A single-clause "+N% to X" talent. These are the ones that convert
#: mechanically - and also the shape Kyle is trying to get AWAY from, so a
#: high count here on a CoA tree is itself worth seeing.
SCALAR_RE = re.compile(
    r"^(?:increases?|reduces?|decreases?|improves?)\b[^.]{0,90}\bby\s+-?\d+(?:\.\d+)?%?"
    r"[^.]{0,25}\.?$", re.I)


def mechanics_for(text):
    body = re.sub(r"\s+", " ", text)
    return [name for name, rx in MECHANICS if re.search(rx, body, re.I)]


def turn_risks_for(text):
    """Real-time assumptions in this talent, with how to translate each."""
    body = re.sub(r"\s+", " ", text)
    return [(name, fix) for name, rx, fix in TURN_BASED_RISKS
            if re.search(rx, body, re.I)]


def our_talents(slug):
    """{normalised name: (tree, node)} for every talent we already have."""
    out = {}
    prefix = slug.replace("-", "_")
    for path in sorted((ROOT / "data/talents").glob(f"{prefix}_*.json")):
        doc = json.loads(path.read_text())
        for node in doc.get("nodes", []):
            key = re.sub(r"[^a-z0-9]", "", (node.get("name") or "").lower())
            if key:
                out[key] = (path.stem, node)
    return out


def is_scalar(node):
    """True if OUR talent is a pure numeric bonus and nothing else."""
    if node.get("proc") or node.get("unlock_ability"):
        return False
    effects = node.get("effects") or {}
    if not effects:
        return False
    return all(isinstance(v, (int, float)) for v in effects.values())


def build(slug):
    info = next((c for c in classes() if c["slug"] == slug), None)
    if info is None:
        raise SystemExit(f"unknown class slug {slug!r}")

    by_tab = nodes_for(slug)
    mine = our_talents(slug)
    tabs = [(s["name"], s["role"], s["tab"]) for s in info["specs"]]
    tabs.append(("Class (shared)", "ALL", SHARED_CLASS_TAB))

    lines = [f"# {info['name']} - CoA reference vs ours", ""]
    lines.append("Source: data/reference/coa/%s.json (Ascension CoA Builder "
                 "payload, the same data allthingscoa.com presents)." % slug)
    lines.append("")
    lines.append("`MATCH` - we already have a talent of this name. `scalar` "
                 "means ours is a pure numeric bonus, which is the thing being "
                 "replaced. `needs` lists the engine mechanic CoA's version "
                 "wants; every one listed is a system this engine already has.")
    lines.append("")

    stats = {"total": 0, "matched": 0, "scalar_ours": 0, "scalar_coa": 0,
             "new": 0, "turn_risk": 0, "no_icon": 0}

    for spec_name, role, tab in tabs:
        rows = [n for n in by_tab.get(tab, []) if n.get("entryType") == "Talent"]
        abilities = [n for n in by_tab.get(tab, []) if n.get("entryType") == "Ability"]
        if not rows and not abilities:
            continue
        lines.append(f"## {spec_name}  ({role}) - {len(rows)} talents, "
                     f"{len(abilities)} abilities")
        lines.append("")
        for node in rows:
            stats["total"] += 1
            name = node.get("name") or "(unnamed)"
            text = clean(node.get("description"))
            flat = re.sub(r"\s+", " ", text)
            key = re.sub(r"[^a-z0-9]", "", name.lower())
            ours = mine.get(key)
            ranks = node.get("maxPoints", 1)

            tags = mechanics_for(text)
            if SCALAR_RE.match(flat):
                stats["scalar_coa"] += 1
                tags = tags or ["scalar"]

            if ours:
                stats["matched"] += 1
                tree, onode = ours
                scalar = is_scalar(onode)
                if scalar:
                    stats["scalar_ours"] += 1
                state = f"MATCH {tree}" + ("  [ours is scalar]" if scalar else "")
            else:
                stats["new"] += 1
                state = "NEW - we have no talent of this name"

            lines.append(f"- **{name}** ({ranks} rank{'s' if ranks != 1 else ''})"
                         f" - {state}")
            if tags:
                lines.append(f"  - needs: {', '.join(tags)}")
            risks = turn_risks_for(text)
            if risks:
                stats["turn_risk"] += 1
                for rname, fix in risks:
                    lines.append(f"  - TURN-BASED [{rname}]: {fix}")
            icon = icon_for(name)
            lines.append(f"  - icon: {'assets/icons/coa/' + icon if icon else 'MISSING - needs art'}")
            if not icon:
                stats["no_icon"] += 1
            lines.append(f"  - CoA: {flat[:400]}")
        lines.append("")

        if abilities:
            lines.append(f"### {spec_name} abilities")
            for node in abilities:
                text = re.sub(r"\s+", " ", clean(node.get("description")))
                lines.append(f"- **{node.get('name')}**: {text[:300]}")
            lines.append("")

    header = [
        f"- CoA talents: **{stats['total']}**",
        f"- already in our data by name: **{stats['matched']}** "
        f"(of those, **{stats['scalar_ours']}** are pure scalars on our side)",
        f"- not in our data at all: **{stats['new']}**",
        f"- single-clause scalars in CoA's own tree: **{stats['scalar_coa']}** "
        f"({100 * stats['scalar_coa'] // max(1, stats['total'])}%)",
        f"- carry real-time assumptions needing translation: **{stats['turn_risk']}** "
        f"({100 * stats['turn_risk'] // max(1, stats['total'])}%)",
        f"- without an extracted CoA icon: **{stats['no_icon']}**",
        "",
    ]
    lines[2:2] = header
    return "\n".join(lines), stats


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    do_all = "--all" in sys.argv
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    slugs = [c["slug"] for c in classes()] if do_all else args
    if not slugs:
        raise SystemExit("usage: coa_class_worksheet.py <slug> | --all")

    print(f"{'class':<18} {'CoA':>5} {'match':>6} {'ours-scalar':>12} {'new':>5} {'turn-fix':>9}")
    for slug in slugs:
        text, stats = build(slug)
        (OUT_DIR / f"{slug}.md").write_text(text + "\n")
        print(f"{slug:<18} {stats['total']:>5} {stats['matched']:>6} "
              f"{stats['scalar_ours']:>12} {stats['new']:>5} {stats['turn_risk']:>9}")
    print(f"\nwritten to {OUT_DIR.relative_to(ROOT)}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
