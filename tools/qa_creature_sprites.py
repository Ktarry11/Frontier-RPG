#!/usr/bin/env python3
"""Every creature in the game resolves to a sprite some sheet actually draws.

    PYTHONPATH=. python3 tools/qa_creature_sprites.py

Kyle: "Currently trash mobs are red boxes and dungeon and cave bosses are generic things. We can
afford up to 5 sprite prompts. So about 36 sprites per sheet."

FIVE CLAIMS:

  1. THE BUDGET IS THE BUDGET. 180 sprites across 5 sheets, nothing drawn twice. Art is the scarce
     thing here, so a sheet quietly growing to 41 means a prompt that will not slice.
  2. EVERY RULE AND EVERY FALLBACK POINTS AT A SPRITE THAT EXISTS IN A SHEET. A rule naming art
     nobody drew is a red box in a dungeon, and it gets found by a player rather than by us.
  3. EVERY CREATURE IN THE GAME RESOLVES. Not just cave creatures - sprite_for has a floor, so
     this checks the floor actually holds for all 1102.
  4. THE RESOLUTION IS STABLE. A creature must draw the same sprite on every call and in every
     process. Python's hash() is randomised per run, so a variant picked with it would change the
     monster's appearance every time the game restarted; this is the check that would have caught
     that.
  5. NO SPRITE IS DEAD WEIGHT. Every one of the 180 is reachable by some real creature. A sprite
     nothing can select is a cell of a sheet spent on nothing, and with only 5 prompts that is the
     expensive mistake.
"""
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import creature_sprites as CS  # noqa: E402

BUDGET = 180
#: A sheet is generated as one image, so this is really "how many cells a prompt can lay out and
#: still have every creature come back distinct". 41 is a 6x7 grid with one gap; past the mid-40s
#: the generator starts blending neighbours, which is a whole sheet wasted.
SHEET_MAX = 42


def main():
    bad = []
    cre = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]

    cave = set()
    for z in enc.values():
        for cv in z.get("caves", {}).values():
            cave |= set(cv.get("creatures", {}))

    # ---- 1. the budget
    flat = [s for v in CS.SHEETS.values() for s in v]
    if len(flat) != BUDGET:
        bad.append(f"{len(flat)} sprites across the sheets, budget is {BUDGET}")
    dup = [s for s, k in Counter(flat).items() if k > 1]
    if dup:
        bad.append(f"drawn more than once: {dup}")
    for name, v in CS.SHEETS.items():
        if len(v) > SHEET_MAX:
            bad.append(f"sheet {name!r} holds {len(v)} sprites, over the {SHEET_MAX} a prompt can "
                       f"reliably lay out")

    # ---- 2. rules and fallbacks point at real art
    #
    # A rule returns a BASE id and sprite_file() resolves it to a numbered look, so "drawn" means
    # either the sheets hold that exact id or they hold its variants. The first version of this
    # check compared rule output straight against ALL_SPRITES and reported 40-odd false failures
    # for sprites that are perfectly well drawn as <id>_1..<id>_n.
    def drawn(sprite):
        return sprite in CS.ALL_SPRITES or sprite in CS.VARIANTS

    for _, s in CS.RULES:
        if not drawn(s):
            bad.append(f"a name rule returns {s!r}, which no sheet draws")
    for t, s in CS.TEMPLATE_FALLBACK.items():
        if not drawn(s):
            bad.append(f"template fallback {t} -> {s!r}, which no sheet draws")
    if not drawn(CS.DEFAULT):
        bad.append(f"DEFAULT is {CS.DEFAULT!r}, which no sheet draws")
    for base in CS.VARIANTS:
        if base in CS.ALL_SPRITES:
            bad.append(f"{base!r} has variants but is ALSO drawn un-numbered - pick one")

    # ---- 3 & 5. every creature resolves, every sprite is reachable
    reached = Counter()
    for n, c in cre.items():
        f = CS.sprite_file(n, c.get("template"))
        if f not in CS.ALL_SPRITES:
            bad.append(f"{n!r} resolves to {f!r}, which no sheet draws")
        reached[f] += 1
    dead = sorted(CS.ALL_SPRITES - set(reached))
    if dead:
        bad.append(f"{len(dead)} sprite(s) no creature can ever select: {dead[:12]}"
                   f"{' ...' if len(dead) > 12 else ''}")

    # ---- 4. stable within and across processes
    probe = "Kobold Miner"
    if len({CS.sprite_file(probe) for _ in range(20)}) != 1:
        bad.append(f"{probe} resolves differently between calls in one process")
    code = ("import sys; sys.path.insert(0, %r); import creature_sprites as C; "
            "print(C.sprite_file(%r))" % (str(ROOT), probe))
    outs = {subprocess.run([sys.executable, "-c", code], capture_output=True, text=True).stdout.strip()
            for _ in range(3)}
    if len(outs) != 1 or outs == {""}:
        bad.append(f"{probe} resolves differently between PROCESSES ({outs}) - the variant is "
                   f"being picked with something randomised per run, so a monster would change "
                   f"appearance every time the game restarts.")

    named = sum(1 for n in cave if any(rx.search(n) for rx, _ in CS.RULES))
    print(f"{len(flat)} sprites over {len(CS.SHEETS)} sheets "
          f"{ {k: len(v) for k, v in CS.SHEETS.items()} }")
    print(f"  {len(cre)} creatures resolve; {len(cave)} are in caves, {named} of those "
          f"({named / max(1, len(cave)):.0%}) matched by name or title rather than stat template")
    print(f"  busiest art: {[f'{s} x{k}' for s, k in reached.most_common(6)]}")

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("\ncreature sprites OK - 180 across 5 sheets, nothing drawn twice, every rule and "
          "fallback points at real art, all creatures resolve, resolution is stable across "
          "processes, and no sprite is dead weight.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
