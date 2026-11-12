#!/usr/bin/env python3
"""Every creature in the game resolves to a sprite some sheet actually draws.

    PYTHONPATH=. python3 tools/qa_creature_sprites.py

Kyle: "Currently trash mobs are red boxes and dungeon and cave bosses are generic things. We can
afford up to 5 sprite prompts. So about 36 sprites per sheet."

SIX CLAIMS:

  1. NOTHING IS DRAWN TWICE AND NO SHEET IS TOO BIG TO GENERATE. Art is the scarce thing here, and
     a sheet quietly growing past what one image can lay out is a prompt that will not slice.
  2. EVERY RULE AND EVERY FALLBACK POINTS AT A SPRITE THAT EXISTS IN A SHEET. A rule naming art
     nobody drew is a red box in a dungeon, and it gets found by a player rather than by us.
  3. EVERY CREATURE IN THE GAME RESOLVES. Not just cave creatures - sprite_for has a floor, so
     this checks the floor actually holds for all 1102.
  4. THE RESOLUTION IS STABLE. A creature must draw the same sprite on every call and in every
     process. Python's hash() is randomised per run, so a variant picked with it would change the
     monster's appearance every time the game restarted; this is the check that would have caught
     that.
  6. NOBODY STANDS AMONG OGRES DRAWN AS A HUMAN. A named boss does not carry the race word, so
     the race rules miss him; and a tribe name (Drywhisker, Witherbark) is not a race word either.
     See race_mismatches().
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

#: Sheets are added over time, so the total is reported rather than asserted - the claim that
#: matters is the per-sheet cap (a prompt can only lay out so many cells) and that nothing is
#: drawn twice.
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

    # ---- 1. nothing drawn twice, no sheet too big to generate
    flat = [s for v in CS.SHEETS.values() for s in v]
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

    for _, s, _only in CS.RULES:
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
    # SPARE art is parked on purpose, not dead - see creature_sprites.SPARE.
    dead = sorted(CS.ALL_SPRITES - set(reached) - set(getattr(CS, "SPARE", {})))
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

    # ---- 6. THE COMBAT SCREEN AND THE DUNGEON FLOOR AGREE.
    #
    # Two call sites draw the same creature from two different sources: the dungeon floor reads the
    # stat template out of creatures.json, and the combat screen reads it off the live Monster
    # object. They have to be the same string or the same monster has two appearances two seconds
    # apart. The first version of the combat wiring read `foe.template`, which does not exist -
    # Monster calls it `monster_type` - so every enemy in combat resolved with template=None and
    # anything that resolves by template alone drew as a human bandit. Nothing crashed and most
    # creatures looked fine, which is exactly why this is a check and not a code read.
    attr = "monster_type"
    try:
        from entities.monster import Monster
        probe_name, probe = next(iter(cre.items()))
        m = Monster(probe_name, probe["template"], level=max(1, int(probe.get("level", 1))))
        if not hasattr(m, attr):
            bad.append(f"a live Monster has no .{attr}; the combat screen reads that attribute to "
                       f"pick creature art and would pass None for every enemy in the game")
        else:
            mismatch = []
            for n, c in cre.items():
                mon = Monster(n, c["template"], level=max(1, int(c.get("level", 1))))
                if CS.sprite_file(n, getattr(mon, attr, None)) != CS.sprite_file(n, c["template"]):
                    mismatch.append(n)
            if mismatch:
                bad.append(f"{len(mismatch)} creature(s) draw differently in combat than on the "
                           f"dungeon floor: {mismatch[:8]}")
    except Exception as exc:
        bad.append(f"could not build a Monster to check the combat path agrees: {exc!r}")

    wrong_race = race_mismatches()
    for line in wrong_race:
        bad.append(line)

    named = sum(1 for n in cave if any(rx.search(n) for rx, _s, _o in CS.RULES))
    print(f"{len(flat)} sprites over {len(CS.SHEETS)} sheets "
          f"{ {k: len(v) for k, v in CS.SHEETS.items()} }")
    print(f"  {len(cre)} creatures resolve; {len(cave)} are in caves, {named} of those "
          f"({named / max(1, len(cave)):.0%}) matched by name or title rather than stat template")
    spare = sorted(getattr(CS, "SPARE", {}))
    if spare:
        print(f"  parked for later ({len(spare)}): {spare}")
    print(f"  busiest art: {[f'{s} x{k}' for s, k in reached.most_common(6)]}")

    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:20]:
            print("  -", b)
        return 1
    # Counted, not typed. This line said "180 across 5 sheets" for two sheets longer than it was
    # true, which is the small version of the bug this whole file exists to catch.
    print(f"\ncreature sprites OK - {len(flat)} across {len(CS.SHEETS)} sheets, nothing drawn "
          "twice, every rule and fallback points at real art, all creatures resolve, resolution "
          "is stable across processes, no sprite is dead weight, and combat draws each creature "
          "the same as the dungeon floor does.")
    return 0


def race_mismatches():
    """Claim 6: nobody stands in a roster of ogres (kobolds, trolls...) drawn as a human.

    Kyle, 10 Nov: "Boulder'gor boss should be an ogre." A named boss does not carry the race
    word, so the race rules missed him and his humanoid stat template drew a human bandit.
    For every encounter table where at least half the other creatures share one race's art,
    a humanoid drawn with GENERIC human art is reported - unless it is listed below as a
    person who really is a human among them.
    """
    import re
    import creature_sprites as cs
    root = Path(__file__).resolve().parent.parent
    creatures = json.loads((root / "data/creatures/creatures.json").read_text())["creatures"]
    enc = json.loads((root / "data/creatures/encounters.json").read_text())
    race = re.compile(r"^(ogre|kobold|troll|gnoll|murloc|naga|quilboar|harpy|centaur|furbolg|satyr|worgen|yeti|goblin)")
    generic = re.compile(r"^(bandit_human|cultist|champion|syndicate|executioner|hunter_ranger|cult_overseer|archmage|houndmaster)")
    #: Humans who belong where they are: cultists in a worgen village, a Syndicate man in a
    #: kobold mine, and three whose race the name does not settle.
    really_human = {"Pyrewood Cultist", "Peril Packmaster", "Syndicate Prospector",
                    "Kundaraz Terrace-Watch", "Skinwalker Garn", "Oldcrest"}
    found = {}

    def walk(node, path=""):
        if not isinstance(node, dict):
            return
        for key, value in node.items():
            here = f"{path}/{key}"
            if path.endswith("/caves") or path.endswith("/subzones"):
                names = sorted(n for n in set(re.findall(r'"([^"]{3,45})"', json.dumps(value))) if n in creatures)
                art = {n: cs.sprite_file(n, creatures[n]["template"]) for n in names}
                tally = Counter(race.match(a).group(1) for a in art.values() if race.match(a))
                if tally:
                    top, count = tally.most_common(1)[0]
                    for n, a in art.items():
                        if (generic.match(a) and creatures[n]["template"].startswith("humanoid")
                                and count >= max(2, (len(names) - 1) * 0.5) and n not in really_human):
                            found[n] = f"{n} is drawn as {a} among {count} {top}s ({key})"
            walk(value, here)
    walk(enc)

    # ...and the tribes: a creature named for a tribe draws as that tribe's race.
    tribes = {"drywhisker": "kobold", "witherbark": "troll", "sandfury": "troll", "boulderfist": "ogre",
              "death's head": "quilboar", "mudsnout": "gnoll", "witchwing": "harpy", "kolkar": "centaur"}
    for n, e in creatures.items():
        for tribe, want in tribes.items():
            if tribe in n.lower() and e["template"].startswith(("humanoid", "vermin")):
                a = cs.sprite_file(n, e["template"])
                if not a.startswith(want) and "pack runner" not in n.lower():
                    found[n] = f"{n} is a {tribe.title()} ({want}) and is drawn as {a}"
    return sorted(found.values())


if __name__ == "__main__":
    sys.exit(main())
