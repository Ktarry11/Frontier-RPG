#!/usr/bin/env python3
"""Wire an authored class into the game: spellbook tabs + character creation.

    PYTHONPATH=. python3 tools/wire_class.py <slug> [<slug> ...] [--apply]
    PYTHONPATH=. python3 tools/wire_class.py --unwired [--apply]

The two steps a class-authoring agent is deliberately NOT allowed to do,
because twelve of them run concurrently and both touch shared files:

  data/spellbook_tabs_coa.json   ability -> tab, one tab per spec plus "core"
  ui/screens/character_screen.py the selectable class list

TABS ARE INFERRED FROM THE TALENT TREES, not from a hand-written list. A
talent that carries `unlock_ability` names the ability it teaches, so the
tree that teaches an ability is the spec that owns it; everything else is
class-wide and goes to "core". That makes the mapping a consequence of the
data rather than a second place to keep in sync, and it means a spec-gated
ability can never be filed under the wrong spec.

Abilities an agent gated with `requires_talent` but no tree actually
unlocks are reported rather than guessed at - that pairing is usually a
mistake worth seeing.

REFUSES TO WIRE A CLASS THAT DOES NOT VALIDATE. A class in the creation
list with a broken kit is worse than one that is missing: picking it makes
a character that cannot act. So this runs tools/validate_class.py first and
stops on any error.
"""
import argparse
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

TABS_FILE = ROOT / "data/spellbook_tabs_coa.json"
CREATION_FILE = ROOT / "ui/screens/character_screen.py"


def display_name(slug):
    from combat.abilities import CLASS_RESOURCE_MAP
    want = slug.replace("_", " ").replace("-", " ").lower()
    for name in CLASS_RESOURCE_MAP:
        if name.lower() == want:
            return name
    return slug.replace("_", " ").title()


def validates(slug):
    result = subprocess.run(
        [sys.executable, "tools/validate_class.py", slug],
        cwd=ROOT, capture_output=True, text=True,
        env={**__import__("os").environ, "PYTHONPATH": "."})
    tail = [l for l in result.stdout.splitlines() if "errors total" in l]
    return result.returncode == 0, (tail[-1] if tail else "(no summary)")


def tab_map(slug):
    """{ability_id: tab} for one class, inferred from its talent trees."""
    prefix = slug.replace("-", "_")
    ability_file = ROOT / f"data/abilities/{slug}.json"
    abilities = [a["ability_id"]
                 for a in json.loads(ability_file.read_text())["abilities"]]

    owner = {}
    for tree_path in sorted(ROOT.glob(f"data/talents/{prefix}_*.json")):
        tree_id = tree_path.stem
        for node in json.loads(tree_path.read_text()).get("nodes", []):
            target = (node.get("effects") or {}).get("unlock_ability")
            if not target:
                continue
            for aid in (target if isinstance(target, list) else [target]):
                if aid in abilities:
                    # An ability unlocked by two trees is class-wide in
                    # practice, so it stays in core rather than being filed
                    # under whichever tree was read last.
                    owner[aid] = "core" if owner.get(aid, tree_id) != tree_id \
                        else tree_id

    mapping = {aid: owner.get(aid, "core") for aid in abilities}

    orphans = [a["ability_id"]
               for a in json.loads(ability_file.read_text())["abilities"]
               if a.get("requires_talent") and a["ability_id"] not in owner]
    return mapping, orphans


def wire(slugs, apply):
    tabs = json.loads(TABS_FILE.read_text()) if TABS_FILE.exists() else {}
    creation = CREATION_FILE.read_text()
    failed, wired = [], []

    for slug in slugs:
        name = display_name(slug)
        ok, summary = validates(slug)
        if not ok:
            print(f"SKIP {name:20s} does not validate - {summary}")
            failed.append(slug)
            continue

        mapping, orphans = tab_map(slug)
        counts = Counter(mapping.values())
        print(f"{name:20s} {len(mapping):3d} abilities -> " +
              ", ".join(f"{t.replace(slug + '_', '')} {n}"
                        for t, n in sorted(counts.items())))
        if orphans:
            print(f"  ! {len(orphans)} abilities set requires_talent but no "
                  f"tree unlocks them: {orphans[:6]}")
        tabs[name] = dict(sorted(mapping.items()))

        if f'"{name}"' not in creation:
            anchor = '            "Guardian",\n'
            if anchor in creation:
                creation = creation.replace(anchor, anchor + f'            "{name}",\n', 1)
            else:
                print(f"  ! could not find the insertion anchor for {name}")
        wired.append(name)

    if apply and wired:
        TABS_FILE.write_text(json.dumps(tabs, indent=2, ensure_ascii=False) + "\n")
        CREATION_FILE.write_text(creation)
        print(f"\nwrote {TABS_FILE.relative_to(ROOT)} and "
              f"{CREATION_FILE.relative_to(ROOT)} for {len(wired)} classes")
    elif not apply:
        print("\n(dry run - pass --apply to write)")
    return len(failed)


def unwired():
    """Classes that have an ability file but are not yet selectable."""
    creation = CREATION_FILE.read_text()
    out = []
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        slug = path.stem
        if slug.startswith("_") or slug == "asher_unique":
            continue
        if f'"{display_name(slug)}"' not in creation:
            out.append(slug)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("slugs", nargs="*")
    parser.add_argument("--unwired", action="store_true",
                        help="wire every class that has a kit but is not selectable")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    slugs = args.slugs
    if args.unwired or not slugs:
        slugs = unwired()
        if not slugs:
            print("every class with an ability file is already wired")
            return 0
        print(f"unwired classes: {', '.join(slugs)}\n")
    return wire(slugs, args.apply)


if __name__ == "__main__":
    raise SystemExit(min(main(), 125))
