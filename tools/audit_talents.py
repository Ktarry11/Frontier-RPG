#!/usr/bin/env python3
"""Audit talent data for the ways it gets bastardised.

    python3 tools/audit_talents.py           # all checks
    python3 tools/audit_talents.py --verbose # list every hit, not just a sample

Kyle, 2026-10-26: "we should audit each talent since some of them are
bastardized."

1358 talents across 56 trees is too many to eyeball, and the damage is not
uniform - it is a handful of specific failure modes, each of which IS
detectable. This finds them. What it cannot judge is whether a talent is
BALANCED or whether its fantasy fits its spec; that still needs eyes.

The checks, and the real bug each was written for:

  dev-note-in-tooltip   warrior_arms "Sudden Death" shipped a design
                        rationale as its player-facing description: "Real
                        proc: ... matches Sudden Death's actual WOTLK
                        identity ... (previously Execute had no HP gate at
                        all)". A player reads that in the tooltip.
  junk-name             cultist_godblade's capstone was called "Nutcase".
  name-belongs-to-other A talent carrying a DIFFERENT talent's name while its
                        own description describes itself - primalist's
                        raptor_talons was named "Rylak's Bite" while
                        describing Raptor Talons, and a separate
                        rylaks_bite node existed alongside it.
  duplicate-name        Two talents with the same name in one tree. Always a
                        mistake: the player cannot tell them apart.
  orphan-prefix         A node whose id names a spec that is not the file it
                        lives in - six shaman_tank_* nodes sitting inside
                        shaman_enhancement, three of them colliding with real
                        enhancement talents.
  no-effects            A talent with a description but an empty effects
                        dict: it reads as doing something and does nothing.
  vague-magnitude       The description states a condition but never the
                        number, while the effects carry one - "Reaching 60
                        Insanity grants a flat bonus to Magic damage" when
                        the effect is 10%.
  number-contradiction  A number in the description that matches NO effect
                        value, in either sign or scale.
"""
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TALENTS = ROOT / "data" / "talents"

#: Words that belong in a design document and never in a tooltip.
DEV_NOTE = re.compile(
    r"\b(real proc|WOTLK|WotLK|per handoff|confirmed via|screenshot|identity as|"
    r"previously|now that|TODO|placeholder|source:|note to self)\b", re.I)

#: Names that are obviously not shipping names. Deliberately narrow - an
#: earlier, looser version flagged "Test of Faith" and "Tempest's Call",
#: which are real talent names, so this matches whole words only.
JUNK_NAME = re.compile(r"^(nutcase|todo|tbd|placeholder|temp|test|xxx|untitled|new talent)$", re.I)

#: A description that sets a condition but gives no magnitude.
VAGUE = re.compile(r"\b(a flat bonus|scale up further|increases healing done|"
                   r"additional health|reduces damage that would|further)\b", re.I)


def load():
    out = {}
    for f in sorted(TALENTS.glob("*.json")):
        doc = json.loads(f.read_text())
        for n in doc.get("nodes", []):
            out[n["talent_id"]] = dict(n, _file=f.stem, _spec=doc.get("spec_name", f.stem))
    return out


def numbers(s):
    return {float(x) for x in re.findall(r"\b(\d+(?:\.\d+)?)\b", s)}


#: Effect keys whose value is a FLAG (1 = on), not a magnitude. Comparing a
#: description's numbers against these is meaningless - "after 3 Horrorbolt
#: casts" against a proc flag of 1 is not a contradiction.
FLAG_KEY = re.compile(r"(_proc|^unlock_|_unlock$|^ability_)", re.I)


def effect_magnitudes(eff):
    """Every plausible rendering of an effect value, so the comparison is not
    fooled by sign (reductions are negative), by 0-1 vs percent, or by a
    duration stored in minutes against a description in seconds."""
    vals = set()
    for k, v in eff.items():
        if FLAG_KEY.search(k):
            continue
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            a = abs(float(v))
            vals |= {a, a * 100, a / 100, a * 60}
    return vals


def main():
    verbose = "--verbose" in sys.argv
    T = load()
    findings = defaultdict(list)

    by_file_name = defaultdict(list)
    for tid, n in T.items():
        by_file_name[(n["_file"], n.get("name"))].append(tid)

    for tid, n in T.items():
        name = (n.get("name") or "").strip()
        desc = (n.get("description") or "").strip()
        eff = n.get("effects") or {}

        if DEV_NOTE.search(desc):
            findings["dev-note-in-tooltip"].append(f"{tid}: {desc[:90]}")

        if JUNK_NAME.match(name):
            findings["junk-name"].append(f"{tid}: {name!r}")

        if not desc:
            findings["no-description"].append(tid)
        elif not eff and n.get("node_type") != "ability":
            findings["no-effects"].append(f"{tid} ({name!r}): {desc[:70]}")

        # a node whose id claims a spec it does not live in
        prefix = tid.rsplit("_", 1)[0]
        if not tid.startswith(n["_file"]):
            cls = n["_file"].split("_")[0]
            if tid.startswith(cls + "_"):
                findings["orphan-prefix"].append(f"{tid} lives in {n['_file']}.json")

        # the name belongs to a DIFFERENT talent that also exists
        slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        if slug and not tid.endswith(slug):
            sibling = f"{n['_file']}_{slug}"
            if (sibling in T and sibling != tid
                    and (T[sibling].get("name") or "").strip() == name):
                # Only a problem when the sibling ALSO still carries the name -
                # two nodes claiming it. A node named after the ability it
                # teaches (alkahest_active -> "Alkahest") is correct and must
                # not trip this forever.
                findings["name-belongs-to-other"].append(
                    f"{tid} is named {name!r}, and so is {sibling}")

        if eff and desc:
            dn = numbers(desc)
            vals = effect_magnitudes(eff)
            if vals and dn and not any(abs(x - y) < 0.011 for x in dn for y in vals):
                if VAGUE.search(desc):
                    findings["vague-magnitude"].append(
                        f"{tid} ({name!r}): {desc[:70]} | effects {eff}")
                else:
                    findings["number-contradiction"].append(
                        f"{tid} ({name!r}): {desc[:70]} | effects {eff}")
            elif vals and not dn and VAGUE.search(desc):
                findings["vague-magnitude"].append(
                    f"{tid} ({name!r}): {desc[:70]} | effects {eff}")

    for (f, name), ids in by_file_name.items():
        if len(ids) > 1 and name:
            findings["duplicate-name"].append(f"{f}: {name!r} on {', '.join(sorted(ids))}")

    print(f"audited {len(T)} talents across {len({n['_file'] for n in T.values()})} trees\n")
    if not findings:
        print("No issues found.")
        return 0

    total = sum(len(v) for v in findings.values())
    print(f"{total} findings\n" + "=" * 68)
    for check in sorted(findings, key=lambda k: -len(findings[k])):
        hits = findings[check]
        print(f"\n{check}  ({len(hits)})")
        for h in (hits if verbose else hits[:6]):
            print(f"    {h}")
        if not verbose and len(hits) > 6:
            print(f"    ... and {len(hits)-6} more (--verbose for all)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
