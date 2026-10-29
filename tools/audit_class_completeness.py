#!/usr/bin/env python3
"""Is each class actually a FULL class?

Kyle's question, verbatim: "I want to ensure these have full skills, stats,
talents, specs, skill levels. They're FULL classes."

validate_class.py answers "does this class's data load and fight without
errors". That is a different question from "is this a complete class a
player can take from 1 to 60". A class can pass validation with eight
abilities, one tree and no trainer.

So this measures the things a player would notice, per class:

  skills       how many abilities, and how they compare to the shipped nine
  skill levels RANK COVERAGE - every ability rank sorted by level, then the
               gaps. A class with 46 abilities that learns nothing between
               36 and 56 is not a full class; it's a full class for twenty
               levels and then a shrug. Reported as the widest dead band.
  stats        base stat spread present, and the total in line with others
  specs        tree count vs CoA's own spec count (the reference wins)
  talents      nodes and points per tree, and whether 51 points is spendable
  wiring       trainer rows, starting gear, character creation, spellbook
               tabs, party row

Nothing here is a pass/fail gate - it's a report with the shipped nine as
the yardstick, because they're what "full class" already means in this game.
"""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# The nine classes that shipped before any of this. They define the bar.
ORIGINAL_NINE = [
    "Warrior", "Shaman", "Rogue", "Priest", "Hunter",
    "Mage", "Warlock", "Druid", "Paladin",
]

LEVEL_CAP = 60
# Bands used for the "learns nothing here" report.
BAND = 10


def file_prefix(char_class: str) -> str:
    return char_class.lower().replace(" ", "_").replace("-", "_")


def coa_spec_counts() -> dict[str, int]:
    """How many specs CoA gives each class, from the scraped page names."""
    out: dict[str, int] = defaultdict(int)
    ref = ROOT / "reference/coa_sidekick"
    if not ref.is_dir():
        return {}
    for p in ref.glob("SPEC_*.txt"):
        stem = p.stem[len("SPEC_"):]
        cls = stem.split("__")[0].replace("-", "_")
        out[cls] += 1
    return dict(out)


def load_classes() -> list[str]:
    """Every class the character sheet knows base stats for."""
    text = (ROOT / "entities/character.py").read_text(encoding="utf-8")
    block = text.split("class_stats = {", 1)[1]
    block = block.split("\n        }", 1)[0]
    return re.findall(r'^\s*"([^"]+)":\s*\{\s*#?', block, re.M)


def base_stats(char_class: str) -> dict[str, int]:
    from entities.character import Character
    c = Character(name="Audit", char_class=char_class, level=1)
    return {
        "strength": c.strength, "stamina": c.stamina,
        "intellect": c.intellect, "spirit": c.spirit, "agility": c.agility,
    }


def abilities_for(char_class: str) -> list[dict]:
    p = ROOT / f"data/abilities/{file_prefix(char_class)}.json"
    if not p.exists():
        return []
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get("abilities", [])


def trees_for(char_class: str) -> dict[str, dict]:
    pre = file_prefix(char_class) + "_"
    out = {}
    for p in sorted((ROOT / "data/talents").glob(pre + "*.json")):
        out[p.stem[len(pre):]] = json.loads(p.read_text(encoding="utf-8"))
    return out


def tree_nodes(tree: dict) -> list[dict]:
    """Talent files vary in shape across the build generations."""
    for key in ("talents", "nodes"):
        if isinstance(tree.get(key), list):
            return tree[key]
    for v in tree.values():
        if isinstance(v, list) and v and isinstance(v[0], dict) and "talent_id" in v[0]:
            return v
    return []


def rank_levels(abilities: list[dict]) -> list[int]:
    out = []
    for a in abilities:
        for r in a.get("ranks", []):
            lv = r.get("level_req")
            if isinstance(lv, int):
                out.append(lv)
    return sorted(out)


def widest_gap(levels: list[int]) -> tuple[int, int, int]:
    """Biggest stretch of levels 1..60 that teaches nothing new.

    Returns (span, from_level, to_level). A span of 1 means something new
    every level.
    """
    if not levels:
        return (LEVEL_CAP, 1, LEVEL_CAP)
    pts = sorted(set(l for l in levels if l <= LEVEL_CAP))
    if not pts:
        return (LEVEL_CAP, 1, LEVEL_CAP)
    best = (pts[0], 1, pts[0])
    for a, b in zip(pts, pts[1:]):
        if b - a > best[0]:
            best = (b - a, a, b)
    tail = LEVEL_CAP - pts[-1]
    if tail > best[0]:
        best = (tail, pts[-1], LEVEL_CAP)
    return best


def empty_bands(levels: list[int]) -> list[str]:
    """Which 10-level bands teach nothing at all."""
    have = set(l for l in levels if l <= LEVEL_CAP)
    out = []
    for lo in range(1, LEVEL_CAP + 1, BAND):
        hi = min(lo + BAND - 1, LEVEL_CAP)
        if not any(lo <= l <= hi for l in have):
            out.append(f"{lo}-{hi}")
    return out


def tabs_for(char_class: str) -> dict[str, list[str]]:
    p = ROOT / "data/spellbook_tabs_coa.json"
    if not p.exists():
        return {}
    d = json.loads(p.read_text(encoding="utf-8"))
    return d.get(char_class) or d.get(file_prefix(char_class)) or {}


def wiring(char_class: str) -> dict[str, bool]:
    """Four things that have to be true for a class to be fully hooked up.

    NOT checked: class trainers. data/training/trainers.json maps every
    class trainer to "*" - one trainer teaches every class, by design - so
    there is no per-class trainer row to be missing. An earlier version of
    this audit looked for the class NAME in that file and duly reported
    "missing trainer" for all 30 classes including the nine that have
    shipped for months. A check that fails on known-good data is measuring
    itself, not the game.
    """
    checks = {}

    gear = ROOT / "entities/starting_gear.py"
    g = gear.read_text(encoding="utf-8") if gear.exists() else ""
    checks["start_gear"] = char_class in g

    screen = ROOT / "ui/screens/character_screen.py"
    s = screen.read_text(encoding="utf-8") if screen.exists() else ""
    checks["creation"] = char_class in s

    party = ROOT / "entities/party.py"
    pt = party.read_text(encoding="utf-8") if party.exists() else ""
    checks["party"] = (not pt) or char_class in pt or "char_class" in pt

    # Spellbook tabs. The nine original classes resolve theirs at runtime in
    # ui/spellbook_tree_map.py (CLASS_SCHOOL_TREE_MAP plus the physical
    # overrides), so they are correctly absent from the CoA json and are
    # reported as fine. The CoA classes are placed by that json, and its
    # VALUES are tab names while its KEYS are ability_ids - reading the keys
    # as tabs was the second false check here.
    if char_class in ORIGINAL_NINE:
        checks["tabs"] = True
    else:
        tabs = tabs_for(char_class)
        checks["tabs"] = bool(tabs) and any(v != "core" for v in tabs.values())

    return checks


def main() -> int:
    classes = load_classes()
    coa = coa_spec_counts()

    rows = []
    for cls in classes:
        ab = abilities_for(cls)
        trees = trees_for(cls)
        lv = rank_levels(ab)
        gap, ga, gb = widest_gap(lv)
        stats = base_stats(cls)
        pts = {}
        nodes = {}
        for name, tree in trees.items():
            ns = tree_nodes(tree)
            nodes[name] = len(ns)
            pts[name] = sum(n.get("max_points", 0) for n in ns)
        rows.append({
            "class": cls,
            "abilities": len(ab),
            "ranks": len(lv),
            "top_rank_level": max(lv) if lv else 0,
            "gap": gap, "gap_from": ga, "gap_to": gb,
            "empty_bands": empty_bands(lv),
            "stat_total": sum(stats.values()),
            "stats": stats,
            "specs": len(trees),
            "coa_specs": coa.get(file_prefix(cls), 0),
            "nodes": nodes,
            "points": pts,
            "wiring": wiring(cls),
            "original": cls in ORIGINAL_NINE,
        })

    orig = [r for r in rows if r["original"]]
    new = [r for r in rows if not r["original"]]

    def med(vals):
        v = sorted(vals)
        return v[len(v) // 2] if v else 0

    bar = {
        "abilities": med([r["abilities"] for r in orig]),
        "ranks": med([r["ranks"] for r in orig]),
        "gap": med([r["gap"] for r in orig]),
        "stat_total": med([r["stat_total"] for r in orig]),
        "points": med([sum(r["points"].values()) for r in orig]),
    }

    print("=" * 108)
    print("CLASS COMPLETENESS - the shipped nine are the yardstick")
    print("=" * 108)
    print(f"  shipped-nine median: {bar['abilities']} abilities, {bar['ranks']} ranks, "
          f"widest dead band {bar['gap']} levels, {bar['stat_total']} base stats, "
          f"{bar['points']} talent points across all trees")
    print()
    hdr = (f"{'class':<17}{'abil':>5}{'ranks':>6}{'top':>5}{'gap':>5} {'dead bands':<18}"
           f"{'stats':>6}{'spec':>5}{'coa':>4}{'pts':>6}  wiring")
    print(hdr)
    print("-" * 108)
    for r in sorted(rows, key=lambda x: (x["original"], x["class"])):
        w = r["wiring"]
        wire = "".join(
            k[0].upper() if w[k] else k[0]
            for k in ("start_gear", "creation", "party", "tabs")
        )
        bands = ",".join(r["empty_bands"]) or "-"
        spec_flag = "" if r["coa_specs"] in (0, r["specs"]) else " !"
        tag = "" if r["original"] else "*"
        print(f"{tag + r['class']:<17}{r['abilities']:>5}{r['ranks']:>6}"
              f"{r['top_rank_level']:>5}{r['gap']:>5} {bands:<18}"
              f"{r['stat_total']:>6}{r['specs']:>5}{r['coa_specs']:>4}{spec_flag:<2}"
              f"{sum(r['points'].values()):>4}  {wire}")
    print("-" * 108)
    print("  * = built this session.  wiring: SCPT = start_gear/creation/party/tabs")
    print("    uppercase = present, lowercase = MISSING. 'gap' = widest run of")
    print("    levels 1-60 that teaches nothing new.")
    print()

    # --- findings -------------------------------------------------------
    findings = []
    for r in rows:
        c = r["class"]
        if r["abilities"] == 0:
            findings.append(f"{c}: NO ABILITY FILE - not playable")
            continue
        if r["specs"] == 0:
            findings.append(f"{c}: NO TALENT TREES - not playable")
        if r["coa_specs"] and r["specs"] != r["coa_specs"]:
            findings.append(
                f"{c}: {r['specs']} specs but CoA has {r['coa_specs']} "
                f"({', '.join(sorted(r['nodes'])) or 'none'})")
        if r["empty_bands"]:
            findings.append(
                f"{c}: learns NOTHING in levels {', '.join(r['empty_bands'])}")
        elif r["gap"] > max(8, bar["gap"] + 2):
            findings.append(
                f"{c}: {r['gap']}-level dead run at {r['gap_from']}-{r['gap_to']} "
                f"(nine median {bar['gap']})")
        if r["top_rank_level"] < 50:
            findings.append(
                f"{c}: last thing learned at level {r['top_rank_level']} - "
                f"nothing new for the final {LEVEL_CAP - r['top_rank_level']} levels")
        if r["abilities"] < bar["abilities"] * 0.6:
            findings.append(
                f"{c}: only {r['abilities']} abilities vs nine median {bar['abilities']}")
        tp = sum(r["points"].values())
        if r["specs"] and tp < 51:
            findings.append(f"{c}: only {tp} talent points total - 51 not spendable")
        for name, p in sorted(r["points"].items()):
            if p < 51:
                findings.append(
                    f"{c}/{name}: {p} points in the tree - a player who stays "
                    f"in one tree can't spend 51")
        missing = [k for k, v in r["wiring"].items() if not v]
        if missing:
            findings.append(f"{c}: not wired - missing {', '.join(missing)}")

    if findings:
        print("FINDINGS")
        print("-" * 108)
        for f in findings:
            print(f"  - {f}")
    else:
        print("No findings.")
    print()
    print(f"{len(rows)} classes, {len(findings)} findings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
