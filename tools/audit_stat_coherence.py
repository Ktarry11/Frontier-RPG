#!/usr/bin/env python3
"""Items whose stats do not make sense together. Scans all committed data.

    PYTHONPATH=. python3 tools/audit_stat_coherence.py
    PYTHONPATH=. python3 tools/audit_stat_coherence.py --verbose

Kyle, 2026-10-29: "we need to ensure the suffix does what it is supposed to. I
have a suffix list there bro. Quest items are generally hand crafted so they
dont really get the 'of the x' or 'of the y' but they still need coherant
stats which most of them do."

So there are two different questions and this tool asks them separately:

  1. An item that NAMES a stat template must stay inside it. The template's
     wanted set is the authority (entities/loot_generator), the same one the
     suffix roller uses, so this and the generator cannot drift apart.

  2. A hand-authored item that names NO template still cannot mix a
     melee-only stat with a caster-only one. Attack power next to healing
     power is not a design choice anybody would defend, and it needs no
     template to be recognisably wrong.

THIS CHECK CRIED WOLF ON ITS FIRST RUN and the shape of that mistake is worth
keeping. It reported 80 findings, 79 of which were blueprint entries in
data/blacksmithing/recipes.json: a recipe names a slot and an armour type and
has no stat block at all, so "no stats from its template" was true and
meaningless. A check that reports 80 problems of which 1 is real is worse
than no check, because the next person learns to skip its output. It now
requires an item to actually carry a stat before it has an opinion.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

STAT_KEYS = ("primary_stats", "secondary_stats")


def stats_of(node):
    """Merged stat dict for one item node, or {} if it carries no stats."""
    out = {}
    for key in STAT_KEYS:
        block = node.get(key)
        if isinstance(block, dict):
            out.update(block)
    return {k: v for k, v in out.items() if v}


def looks_like_item(node):
    """An item node, as opposed to any other dict in the tree. Needs a name
    and a slot - a recipe has those too, which is exactly why carrying a
    stat is a separate test rather than part of this one."""
    return (isinstance(node, dict) and isinstance(node.get("name"), str)
            and isinstance(node.get("slot"), str))


def walk(node, path, out):
    if isinstance(node, dict):
        if looks_like_item(node):
            out.append((path, node))
        for k, v in node.items():
            walk(v, f"{path}.{k}" if path else str(k), out)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, f"{path}[{i}]", out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--verbose", action="store_true",
                    help="also list the items that were skipped and why")
    args = ap.parse_args()

    from entities.loot_generator import LootGenerator
    gen = LootGenerator()
    wanted_by_template = gen._SUFFIX_TEMPLATE_STATS
    banned_by_template = gen._SUFFIX_TEMPLATE_EXCLUDES
    resists = gen._RESISTANCE_STATS
    caster_only = gen._CASTER_ONLY
    physical_only = gen._PHYSICAL_ONLY

    items = []
    for path in sorted((ROOT / "data").rglob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        found = []
        walk(data, "", found)
        for where, node in found:
            items.append((path.relative_to(ROOT), where, node))

    checked = skipped_nostats = 0
    findings = []

    for rel, where, node in items:
        stats = stats_of(node)
        if not stats:
            # A recipe, a vendor listing, a quest reward stub: names a slot,
            # carries no stat block. Nothing to say about it. This is the
            # line that took the first run from 80 findings to 1.
            skipped_nostats += 1
            continue
        checked += 1
        name = node["name"]
        template = node.get("stat_template")
        keys = set(stats)

        if template and template in wanted_by_template:
            # Resistances are gated by level rather than by template and are
            # deliberately outside every template's set, so they are allowed
            # here - audit_loot owns the level rule for them.
            stray = keys - set(wanted_by_template[template]) - resists
            banned = keys & set(banned_by_template.get(template, frozenset()))
            if stray:
                findings.append(
                    f"{rel}: {name} is {template} but carries "
                    f"{', '.join(sorted(stray))}, which that template does not want")
            elif banned:
                findings.append(
                    f"{rel}: {name} is {template} but carries "
                    f"{', '.join(sorted(banned))}, which that template refuses")
        else:
            # NO TEMPLATE CLAIMED, so the question is whether ANY template
            # would want this combination. "Melee stat plus caster stat"
            # was the obvious test and it was wrong: it fired on 15
            # hand-authored quest items carrying agility with intellect,
            # which is agi_int_hybrid - a real template in this game, and
            # the one Kyle asked for variation on. The data was right and
            # my check was wrong, which is the third time a check of mine
            # has over-reported on its first run.
            #
            # Asking the templates instead means a combination is incoherent
            # only when no role in the game wants it, and new templates widen
            # this automatically instead of needing the test rewritten.
            interesting = keys - resists
            if interesting and not any(
                    interesting <= set(wanted)
                    for wanted in wanted_by_template.values()):
                findings.append(
                    f"{rel}: {name} carries {', '.join(sorted(interesting))}, "
                    f"which no stat template in the game wants together")

    print(f"{len(items)} item-shaped entries across data/")
    print(f"  {checked} carry stats and were checked")
    print(f"  {skipped_nostats} carry no stats (recipes, stubs, vendor rows) and were skipped")
    if args.verbose:
        print(f"  templates in use: "
              f"{sorted({n.get('stat_template') for _r, _w, n in items if n.get('stat_template')})}")
    print()

    if not findings:
        print("every item carrying stats is coherent")
        return 0
    print(f"{len(findings)} FINDING(S)")
    for f in findings:
        print(f"  * {f}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
