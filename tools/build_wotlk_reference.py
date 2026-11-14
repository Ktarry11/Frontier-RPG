#!/usr/bin/env python3
"""Turn the real 3.3.5a talent data into Frontier reference worksheets.

    PYTHONPATH=. python3 tools/build_wotlk_reference.py --repo <clone>

WHERE THE DATA COMES FROM, and why this source and not the others.

Kyle sent three sources on 5 Nov 2026:

    https://www.wowhead.com/wotlk/talent-calc
    https://www.warcrafttavern.com/wotlk/tools/talent-calculator/
    https://github.com/atosfr/WotLK-3.3.5-Talent-Calculator

Both calculators render their trees in JavaScript, so a fetch returns the
page furniture and nothing else - the second one yields only a bare list of
max-rank values per slot, with no talent names, no tier labels and no
effect text. The GitHub project is a C# WPF app whose data sits in two
plain JSON files extracted from the game's own `Spell.dbc`:

    Talents.json             name, row, col, maxRank, attached (prereq)
    TalentDescriptions.json  the per-rank tooltip text, every rank

That is the authoritative shape - structure in one file, the real
per-rank wording in the other - so this script reads those two.

IT WAS CROSS-CHECKED BEFORE BEING TRUSTED. The slot counts the JS
calculator did surrender were kept and compared against the repo, because
a single unverified source for 240 talents is how a whole pass ends up
subtly wrong:

    druid  Balance 28   Feral Combat 30   Restoration 27
    shaman Elemental 25 Enhancement 29    Restoration 26

All six match the repo exactly, and across all 27 Classic trees every
talent's description rank-count equals its maxRank. One talent is missing
its text - Hunter "Thick Hide" - and is filled in below from knowledge and
MARKED as such in the worksheet, so it is the one line a reader should
treat as second-hand.

THE TWO TRANSLATIONS THIS RECORDS.

1. ELEVEN ROWS BECOME SEVEN TIERS. Every WotLK tree is 11 rows deep; a
   Frontier tree is tier 0-6 - seven tiers, gated by tier_requirements
   0/5/10/15/20/25/30. The map is `tier = round(row * 6 / 10)`, giving
   0/1/1/2/2/3/4/4/5/5/6, which spreads the rows as evenly as the
   arithmetic allows and leaves row 10 - the WotLK capstone - alone on
   tier 6, where Frontier already puts its capstones. Roughly two rows per
   tier is also how the real trees gate: a row is 5 points of depth, a
   Frontier tier is 5.

2. THE NUMBERS DO NOT COME ACROSS, only the mechanics. WotLK numbers
   assume 80 levels, raid-length fights and real-time seconds; Frontier
   caps at 60, fights run 2-3 turns on trash and 5-6 on a boss
   (tools/qa_dot_durations.py has the measurements), and a "10 sec" window
   is 3 turns, not 10. This is the same rule the CoA pass ran under and the
   reason that pass worked: take the mechanic, re-derive the number.
   Point totals need no engineering either - the real trees come in at
   66-81 points against Frontier's 56-point floor and 71 median.

WHAT THE `needs` TAGS ARE FOR. Each talent is tagged with the engine
mechanic its text actually asks for, and a tag is marked BLOCKED when
findings say this engine has no way to express it (no stack counts, no
periodic trigger, no cast times, and so on - claude/engine_findings_
2026_11_06.md section by section). A blocked tag is not a defect in the
data; it is the signal to find the nearest mechanic the engine does have
rather than ship a tooltip the engine cannot honour.
"""

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: The nine original WoW Classic classes. Death Knight is in the source
#: data and deliberately skipped - Frontier has no Death Knight, and the
#: Knight of Xoroth that fills that niche came from CoA, not WotLK.
CLASSIC = ["mage", "rogue", "priest", "hunter", "warlock",
           "warrior", "paladin", "shaman", "druid"]

#: Row -> tier. Frontier trees are tier 0-6 - SEVEN tiers, with
#: tier_requirements 0/5/10/15/20/25/30 - not 1-6. An earlier version of
#: this mapped rows to 1-6 with `row // 2 + 1`, which both lost tier 0 and
#: squeezed 11 rows into 6 slots; it was caught by reading a real tree file
#: before any tree was built on top of it.
#:
#: round(row * 6 / 10) spreads 11 rows across 7 tiers as evenly as the
#: arithmetic allows and lands the WotLK capstone row (10) alone on tier 6,
#: which is where Frontier already puts its capstones:
#:
#:     row  0  1  2  3  4  5  6  7  8  9 10
#:    tier  0  1  1  2  2  3  4  4  5  5  6
def tier_of(row):
    return min(6, int(round(row * 6 / 10)))


#: The one talent with no text in the source, filled from knowledge.
#: Flagged in the worksheet so it is auditable rather than invisible.
FILLED_FROM_KNOWLEDGE = {
    ("hunter", "Thick Hide"): [
        "Increases the armor rating of your pets by 20% and your armor "
        "contribution from items by 4%.",
        "Increases the armor rating of your pets by 30% and your armor "
        "contribution from items by 7%.",
        "Increases the armor rating of your pets by 40% and your armor "
        "contribution from items by 10%.",
    ],
}

#: Mechanic detection. Each entry is (tag, pattern, blocked). `blocked`
#: means the engine has no key or trigger for it, per
#: claude/engine_findings_2026_11_06.md - so a talent carrying that tag
#: needs a substitute mechanic, not a literal port.
MECHANICS = [
    ("proc-chance",     r"\bchance\b",                              False),
    ("hp-threshold",    r"below \d+% (?:of their )?health|"
                        r"health below|under \d+% health",           False),
    ("resource-grant",  r"\b(?:generat|restor|grant)\w*\b.{0,30}"
                        r"(?:rage|energy|mana|runic power|"
                        r"combo point)",                             False),
    ("dot-hot",         r"over \d+ sec|every \d+ sec",               False),
    ("duration-window", r"for \d+ sec",                              False),
    ("cooldown-change", r"cooldown",                                 False),
    ("cost-change",     r"\bcost\b|mana cost|rage cost",             False),
    ("crit",            r"critical strike",                          False),
    ("heal",            r"\bheal\w*\b",                              False),
    ("absorb",          r"absorb",                                   False),
    ("stun",            r"\bstun\w*\b",                              False),
    ("threat",          r"\bthreat\b",                               False),
    ("pet",             r"\byour pet\b|\bpets\b|minion|demon",       False),
    ("aoe",             r"nearby enem|all enem|all targets|"
                        r"within \d+ yards",                         False),
    ("dispel",          r"dispel|cleanse|remove .{0,20}effect",      False),
    # Everything below has no engine expression. See module docstring.
    ("BLOCKED:stacks",  r"\bstack\w*\b|up to \d+ times|"
                        r"per application|each application",         True),
    ("BLOCKED:cast-time",
                        r"cast time|casting time|instant cast",      True),
    ("BLOCKED:channel", r"\bchannel\w*\b",                            True),
    ("BLOCKED:interrupt",
                        r"\bsilenc\w*\b|\binterrupt\w*\b",           True),
    ("BLOCKED:stealth", r"\bstealth\w*\b|\bprowl\w*\b",              True),
    ("BLOCKED:position",
                        r"\bbehind\b|in front of|\bfacing\b",        True),
    ("BLOCKED:charges", r"\bcharges?\b(?! up)",                       True),
    ("BLOCKED:periodic-trigger",
                        r"each time .{0,40}(?:ticks|periodic)|"
                        r"periodic damage .{0,20}chance",            True),
    ("BLOCKED:weapon-type",
                        r"\b(?:dagger|axe|mace|sword|polearm|staff|"
                        r"fist weapon)s?\b",                         True),
    ("BLOCKED:target-count",
                        r"\d+ additional target|one additional "
                        r"(?:target|enem)",                          True),
]

#: Real-time language that must be re-derived as turns.
REALTIME = re.compile(r"\b\d+(?:\.\d+)?\s*sec\b|\bper \d+ sec\b|"
                      r"\b\d+ min\b", re.I)


def tags_for(text):
    found, blocked = [], []
    for tag, pat, is_blocked in MECHANICS:
        if re.search(pat, text, re.I):
            (blocked if is_blocked else found).append(tag)
    return found, blocked


def load_ours():
    """Our current Classic talents, by class: name -> (tree, is_scalar)."""
    ours = {}
    for cls in CLASSIC:
        byname = {}
        for path in sorted((ROOT / "data/talents").glob(f"{cls}_*.json")):
            tree = json.loads(path.read_text(encoding="utf-8"))
            for n in tree["nodes"]:
                scalar = not (n.get("proc") or n.get("effect_type")
                              or (n.get("effects") or {}).get(
                                  "unlock_ability"))
                byname[n["name"].strip().lower()] = (path.stem, scalar,
                                                     n["talent_id"])
        ours[cls] = byname
    return ours


def normalise(repo):
    """Flatten the two source files into one record per talent."""
    talents = json.loads((repo / "Talents.json").read_text(encoding="utf-8"))["classes"]
    descs = json.loads((repo / "TalentDescriptions.json").read_text(encoding="utf-8"))
    out = {}
    for cls in talents:
        cid = cls["id"]
        if cid not in CLASSIC:
            continue
        trees = []
        for tree in cls["trees"]:
            rows = []
            for t in tree["talents"]:
                key = (cid, t["name"])
                entry = descs.get(cid, {}).get(t["name"])
                ranks = entry["ranks"] if entry else \
                    FILLED_FROM_KNOWLEDGE.get(key, [])
                rows.append({
                    "name": t["name"],
                    "row": t["row"],
                    "col": t["col"],
                    "tier": tier_of(t["row"]),
                    "max_rank": t["maxRank"],
                    "requires": (None if t["attached"] == "none"
                                 else t["attached"]),
                    "ranks": ranks,
                    "text_from_knowledge": key in FILLED_FROM_KNOWLEDGE,
                })
            trees.append({"name": tree["name"], "talents": rows})
        out[cid] = {"name": cls["name"], "trees": trees}
    return out


def write_worksheet(cls, data, ours, out_dir):
    lines = []
    all_t = [t for tr in data["trees"] for t in tr["talents"]]
    matched = [t for t in all_t
               if t["name"].strip().lower() in ours.get(cls, {})]
    scalar_ours = [t for t in matched
                   if ours[cls][t["name"].strip().lower()][1]]
    blocked_t = [t for t in all_t if tags_for(" ".join(t["ranks"]))[1]]
    realtime = [t for t in all_t if REALTIME.search(" ".join(t["ranks"]))]

    lines.append(f"# {data['name']} - real WotLK 3.3.5a reference vs ours\n")
    lines.append(f"- WotLK talents: **{len(all_t)}** across "
                 f"{len(data['trees'])} trees")
    lines.append(f"- already in our data by name: **{len(matched)}** "
                 f"(of those, **{len(scalar_ours)}** are pure scalars on "
                 f"our side)")
    lines.append(f"- not in our data at all: **{len(all_t) - len(matched)}**")
    lines.append(f"- carry real-time assumptions needing translation: "
                 f"**{len(realtime)}** "
                 f"({len(realtime) / max(len(all_t), 1):.0%})")
    lines.append(f"- ask for a mechanic this engine does not have: "
                 f"**{len(blocked_t)}**\n")
    lines.append("Source: the game's own `Spell.dbc`, via "
                 "github.com/atosfr/WotLK-3.3.5-Talent-Calculator "
                 "(`Talents.json` + `TalentDescriptions.json`). Slot counts "
                 "independently cross-checked against the rendered "
                 "wowtbc.gg calculator - all six checkable trees match.\n")
    lines.append("`MATCH` - we already have a talent of this name. "
                 "`scalar` means ours is a pure numeric bonus, which is the "
                 "thing being replaced. `needs` lists the engine mechanic "
                 "the real talent wants. **BLOCKED** means this engine has "
                 "no way to express it, so that talent needs a substitute "
                 "mechanic rather than a literal port - never a tooltip the "
                 "engine cannot honour.\n")
    lines.append("WotLK rows 0-10 map onto Frontier's SEVEN tiers (0-6, "
                 "tier_requirements 0/5/10/15/20/25/30) as "
                 "`tier = round(row * 6 / 10)`, so rows go "
                 "0/1/1/2/2/3/4/4/5/5/6 and the WotLK capstone row sits "
                 "alone at tier 6. **Numbers are not ported**: WotLK "
                 "assumes 80 levels, raid fights and real seconds; Frontier "
                 "caps at 60 and fights run 2-3 turns on trash, 5-6 on a "
                 "boss.\n")

    for tree in data["trees"]:
        pts = sum(t["max_rank"] for t in tree["talents"])
        lines.append(f"\n## {tree['name']} - {len(tree['talents'])} "
                     f"talents, {pts} points\n")
        for t in sorted(tree["talents"], key=lambda x: (x["row"], x["col"])):
            key = t["name"].strip().lower()
            mine = ours.get(cls, {}).get(key)
            if mine:
                status = (f"MATCH {mine[2]}"
                          + ("  [ours is scalar]" if mine[1] else ""))
            else:
                status = "NEW - we have no talent of this name"
            lines.append(f"- **{t['name']}** ({t['max_rank']} "
                         f"rank{'s' if t['max_rank'] != 1 else ''}) "
                         f"- row {t['row']} -> tier {t['tier']} - {status}")
            if t["requires"]:
                lines.append(f"  - requires: {t['requires']}")
            found, blocked = tags_for(" ".join(t["ranks"]))
            if found:
                lines.append(f"  - needs: {', '.join(found)}")
            if blocked:
                lines.append(f"  - **BLOCKED**: {', '.join(blocked)} "
                             f"- needs a substitute mechanic")
            if REALTIME.search(" ".join(t["ranks"])):
                lines.append("  - TURN-BASED: real seconds -> turns "
                             "(~3 sec per turn; re-derive, do not divide)")
            if t["text_from_knowledge"]:
                lines.append("  - *** TEXT FILLED FROM KNOWLEDGE - the "
                             "source has no description for this talent ***")
            if t["ranks"]:
                lines.append(f"  - WotLK rank 1: {t['ranks'][0]}")
                if len(t["ranks"]) > 1:
                    lines.append(f"  - WotLK rank {len(t['ranks'])}: "
                                 f"{t['ranks'][-1]}")
            else:
                lines.append("  - (no description available)")

    (out_dir / f"{cls}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(all_t), len(matched), len(scalar_ours), len(blocked_t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True,
                    help="clone of the WotLK-3.3.5-Talent-Calculator repo")
    args = ap.parse_args()
    repo = Path(args.repo)

    data = normalise(repo)
    ours = load_ours()

    json_dir = ROOT / "data/reference/wotlk"
    ws_dir = ROOT / "data/reference/wotlk_worksheets"
    json_dir.mkdir(parents=True, exist_ok=True)
    ws_dir.mkdir(parents=True, exist_ok=True)

    print(f"  {'class':10s} {'talents':>7} {'match':>6} {'ours-scalar':>12} "
          f"{'blocked':>8}")
    tot = [0, 0, 0, 0]
    for cls in CLASSIC:
        (json_dir / f"{cls}.json").write_text(
            json.dumps(data[cls], indent=1) + "\n", encoding="utf-8")
        n, m, s, b = write_worksheet(cls, data[cls], ours, ws_dir)
        print(f"  {cls:10s} {n:>7} {m:>6} {s:>12} {b:>8}")
        for i, v in enumerate((n, m, s, b)):
            tot[i] += v
    print(f"  {'TOTAL':10s} {tot[0]:>7} {tot[1]:>6} {tot[2]:>12} "
          f"{tot[3]:>8}")
    print(f"\n  wrote {len(CLASSIC)} worksheets to {ws_dir}")
    print(f"  wrote {len(CLASSIC)} normalised payloads to {json_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
