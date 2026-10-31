#!/usr/bin/env python3
"""Every price, reward and purse in the game is shown in gold/silver/copper, split in ONE place.

    PYTHONPATH=. python3 tools/qa_coin_display.py

Kyle: "Ensure the shops are using copper, silver, gold. Not expressing in just copper."

The split had been written five times and the copies had drifted. The expensive one was in the
quest screens, which printed `g` and `s` and dropped the copper, so 178 quests understated their
own reward and every sub-gold quest in the game read "0g 33s".

TWO CLAIMS, AND THE SECOND IS THE ONE THAT KEEPS THIS FIXED:

  1. the four names the game imports (format_coins, format_copper, gold_str,
     Party.get_currency_string) all agree with entities.coins.coins on the same inputs. A name
     that stops delegating fails here rather than in a shop three months from now.
  2. NOBODY DIVIDES BY 10000 OR 100 OUTSIDE entities/coins.py. That is the sixth copy's only
     possible shape, and it is the check that actually has teeth - claim 1 can only see the
     copies that already exist, and the quest-screen bug was never a formatter at all, it was an
     f-string somebody wrote inline because reaching for the helper was one import further away.
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from entities.coins import coins  # noqa: E402

#: the values that broke things. 0, a bare-copper reward, a quest whose copper part was dropped,
#: every mount and riding price, and a purse big enough to carry all three parts.
CASES = [0, 1, 45, 99, 100, 3360, 4080, 6000, 6500, 20000, 30000, 500000, 2000000, 453075]

#: the division is legitimate in the one module that owns it, and in tools/ and tests.
ALLOWED = {"entities/coins.py"}
SEARCH = ("ui", "world", "entities", "game", "core")
SPLIT = re.compile(r"(?<![\w.])(?://|/|%)\s*(?:10000|100)(?![\d.])")


def main():
    bad = []

    # ---- claim 1: the four names agree with the one implementation
    from ui.coin_format import format_coins
    from world.travel_manager import format_copper
    from entities.bank import gold_str
    from entities.party import Party

    for c in CASES:
        want = coins(c)
        for name, got in (("format_coins", format_coins(c)), ("format_copper", format_copper(c)),
                          ("gold_str", gold_str(c))):
            if got != want:
                bad.append(f"{name}({c}) = {got!r}, but coins({c}) = {want!r}")
        p = Party.__new__(Party)
        p.copper = c
        if (full := p.get_currency_string()) != coins(c, full=True):
            bad.append(f"Party.get_currency_string at {c} = {full!r}, "
                       f"want {coins(c, full=True)!r}")

    # ---- claim 2: nobody else does the arithmetic
    for d in SEARCH:
        for f in sorted(Path(d).rglob("*.py")):
            rel = f.as_posix()
            if rel in ALLOWED or "__pycache__" in rel:
                continue
            for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                code = line.split("#", 1)[0]
                if SPLIT.search(code) and re.search(r"copper|gold|price|coin|silver", code, re.I):
                    bad.append(f"{rel}:{i} splits coins by hand - call entities.coins.coins "
                               f"instead:\n      {line.strip()}")

    if bad:
        print(f"{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1

    print(f"coin display OK - 4 names agree with entities.coins on {len(CASES)} values, "
          f"and no module outside entities/coins.py splits coins by hand.")
    print("  " + "   ".join(f"{c}->{coins(c)}" for c in (45, 3360, 20000, 2000000)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
