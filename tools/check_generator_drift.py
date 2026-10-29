#!/usr/bin/env python3
"""Does each class's shipped data still match what its generator emits?

THE TRAP THIS CATCHES, which bit three times in one session:

  1. Bloodmage's cost-sign bug. Someone fixed the GENERATOR and never re-ran
     it, so the shipped JSON kept the broken values and the fix sat unused
     in the script for a whole session.

  2. Templar's descriptions. I fixed the emitted JSON and forgot the class
     HAS a generator, so the next rebuild would have reverted every change.

  3. Felsworn, Barbarian and Witch Hunter's unit errors. I fixed the JSON
     only; an agent then regenerated those classes from their build scripts
     and restored the broken values. Three classes started failing
     validation mid-session with nobody having touched them directly.

All three are the same defect: two sources of truth for one file, drifting
apart silently. Only 13 of the 30 classes have a generator, which makes it
worse - "edit the generator, not the data" is right for those 13 and wrong
for the other 17, so there is no single habit that is always correct.

HOW IT WORKS. The repo must be clean (or at least these paths must be).
For each class with a tools/build_<class>.py, it runs the generator with
--apply and asks git whether anything changed. A changed file means the data
and the generator disagreed; the tool then restores the file so your tree is
left exactly as it was found.

A reported drift is not automatically the data's fault. Read the diff: if
the generator is right, keep the regenerated version. If a hand edit to the
JSON is right, port it INTO the generator. What is never right is leaving
them different.

    python3 tools/check_generator_drift.py
    python3 tools/check_generator_drift.py --keep   # leave regenerated output
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                          text=True).stdout


def dirty_paths() -> set[str]:
    return {line[3:].strip() for line in git("status", "--porcelain").splitlines()
            if line.strip()}


def main(argv: list[str]) -> int:
    keep = "--keep" in argv
    builders = sorted((ROOT / "tools").glob("build_*.py"))
    # Only the per-class builders; the others build items, recipes, zones.
    classes = []
    for b in builders:
        slug = b.stem[len("build_"):]
        if (ROOT / f"data/abilities/{slug}.json").exists():
            classes.append(slug)

    before = dirty_paths()
    if before:
        print(f"NOTE: {len(before)} file(s) already modified before this ran; "
              f"they are ignored and left alone.\n")

    drifted: dict[str, list[str]] = {}
    for slug in classes:
        r = subprocess.run([sys.executable, f"tools/build_{slug}.py", "--apply"],
                           cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            drifted[slug] = [f"GENERATOR FAILED: {r.stderr.strip()[:200]}"]
            continue
        now = dirty_paths() - before
        mine = sorted(p for p in now
                      if slug in p and (p.startswith("data/abilities")
                                        or p.startswith("data/talents")))
        if mine:
            drifted[slug] = mine
            if not keep:
                subprocess.run(["git", "checkout", "--", *mine], cwd=ROOT)

    print(f"{len(classes)} of 30 classes have a generator; "
          f"{len(classes) - len(drifted)} match their shipped data.\n")
    if drifted:
        print("DRIFTED - the data and the generator disagree:")
        for slug, paths in drifted.items():
            print(f"  {slug}")
            for p in paths:
                print(f"      {p}")
        print()
        print("Decide which side is right and make the other match. If the")
        print("generator is right, keep its output; if a hand edit to the JSON")
        print("is right, port it into the generator. Leaving them different is")
        print("how a fix sits unused in a script for a session, and how a")
        print("regeneration silently reverts someone else's work.")
        if not keep:
            print("\n(files restored; pass --keep to retain the regenerated output)")
    else:
        print("No drift.")

    print(f"\nThe other {30 - len(classes)} classes have NO generator, so their")
    print("data IS the source of truth and editing the JSON is correct there.")
    return 1 if drifted else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
