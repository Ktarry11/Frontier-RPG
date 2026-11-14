#!/usr/bin/env python3
"""The spellbook refine pass holds (tools/refine_class_kits.py).

    PYTHONPATH=. python3 tools/qa_spellbook_refine.py

Kyle, 14 Nov 2026: "we don't need every single ability as they become too heavy... 'usable while
moving' is pointless." Checked:
  1. the refine tool has nothing left to do (a class file was not rebuilt with cut abilities back in);
  2. no retired ability is named anywhere in a class file, the spellbook tabs or a talent tree;
  3. no ability text in ANY class still talks about moving, teleporting, knockback, attack or casting
     speed, real-time durations, raids or players;
  4. an old save with a retired ability on its hotbar loses it on load, and keeps everything else.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)


def main():
    r = subprocess.run([sys.executable, str(ROOT / "tools/refine_class_kits.py"), "--check"],
                       capture_output=True, text=True, env={**os.environ, "PYTHONPATH": str(ROOT)})
    check(r.returncode == 0, "refine_class_kits.py --check has work left:\n" + r.stdout)

    sys.path.insert(0, str(ROOT / "tools"))
    import refine_class_kits as R
    retired = set(json.loads((ROOT / "data/reference/retired_abilities.json").read_text(encoding="utf-8"))["ids"])
    files = [ROOT / "data/spellbook_tabs_coa.json"]
    for cls in R.CLASSES:
        prefix = cls.lower().replace(" ", "_")
        files.append(ROOT / f"data/abilities/{prefix}.json")
        files += sorted((ROOT / "data/talents").glob(f"{prefix}_*.json"))
        for a in json.loads((ROOT / f"data/abilities/{prefix}.json").read_text(encoding="utf-8"))["abilities"]:
            for pat in R.REALTIME:
                check(not re.search(pat, a.get("description", "")), f"{a['name']}: still says '{a['description']}'")
    def live(o):
        """The data the game reads - dev notes ("_source" and the like) are history, not references."""
        if isinstance(o, dict):
            return {k: live(v) for k, v in o.items() if not k.startswith("_")}
        if isinstance(o, list):
            return [live(v) for v in o]
        return o

    # every class, refined or not: no ability text that only means something in real time
    realtime = re.compile(r"usable while (?:moving|stealthed|stunned|casting)|cannot move|movement speed|"
                          r"teleport|knock(?:s|ed)? back|knockback|pushback|attack speed|casting speed|"
                          r"spell cast time|for \d+ (?:hrs?|hours?|minutes?|seconds?)|party and raid|"
                          r"allied player|if the target is a player", re.I)
    for f in sorted((ROOT / "data/abilities").glob("*.json")):
        for a in json.loads(f.read_text(encoding="utf-8")).get("abilities", []):
            m = realtime.search(a.get("description", ""))
            check(not m, f"{a['ability_id']}: '{m.group(0) if m else ''}' in '{a.get('description', '')}'")

    for f in files:
        text = json.dumps(live(json.loads(f.read_text(encoding="utf-8"))))
        for rid in retired:
            check(not re.search(re.escape(rid) + r"(?![a-z_])", text), f"{f.name} still names {rid}")

    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    from entities.character import Character
    c = Character("Saved", "Runemaster", 40)
    keep = next(a.ability_id for a in c.get_learned_abilities() if a.ability_id not in retired)
    gone = sorted(retired)[0]
    c.hotbar[0], c.hotbar[1] = gone, keep
    c._prune_unlearned_hotbar()
    check(gone not in c.hotbar, f"{gone} survived on an old save's hotbar")
    check(c.hotbar[1] == keep, f"{keep} was knocked off the hotbar with it")

    print(f"{len(R.CLASSES)} class(es) refined, {len(retired)} abilities retired")
    if fails:
        for m in fails:
            print("  -", m)
        return 1
    print("\nspellbook refine OK - cut abilities are gone everywhere, old saves drop them, no real-time text left.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
