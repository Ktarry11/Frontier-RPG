#!/usr/bin/env python3
"""A stat reads the same on the spell, on the buff it applies, and in the combat log.

    PYTHONPATH=. python3 tools/qa_stat_text_agrees.py

Kyle, of *Hasten*: "Haste +15%" on the spell, "Haste +15" on the buff. Three formatters each had
their own idea of which stats are percentages; 8 of the 64 stat keys in the game disagreed about
the % sign alone, and a fraction (-0.4 damage taken) read "-40%" in one place and "-0.4" in
another. combat/stat_text.py is now the only one.

THREE CLAIMS:
  1. FOR EVERY STAT ANY ABILITY OR RECRUIT KIT GRANTS, the spell tooltip, the buff hover and
     the combat log give the same number and the same unit.
  2. A FRACTION IS SHOWN AS A PERCENTAGE: -0.4 and -40 damage taken both read 40%.
  3. A FLAG IS WORDS, NOT "+1".
"""
import contextlib
import glob
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from combat.abilities import Ability
    from combat.status_effects import StatusEffect, EffectType, StatusEffectMixin
    from combat.stat_text import stat_text
    from ui import effect_tooltip as ET


def figure(text):
    """The signed number and unit out of a line: '+15%' from 'Haste +15%' or '+15% Haste'."""
    m = re.search(r"[+-]\d+(?:\.\d+)?%?", text)
    return m.group(0) if m else None


def main():
    bad = []
    seen = {}
    sources = [json.load(open(p, encoding="utf-8")).get("abilities", []) for p in glob.glob("data/abilities/*.json")]
    kits = json.load(open("data/npcs/personal_kits.json", encoding="utf-8"))
    sources += [v.get("abilities", []) for v in kits.values() if isinstance(v, dict)]
    for abilities in sources:
        for a in abilities:
            for k, v in (a.get("stat_mods") or {}).items():
                if isinstance(v, (int, float)) and not isinstance(v, bool) and v:
                    seen.setdefault(k, v)
    for key, value in seen.items():
        spell = Ability._stat_mod_text(key, value)
        effect = StatusEffect("t", "T", EffectType.BUFF, 3, stat_mods={key: value}, real_time_seconds=None)
        hover = (ET._stat_lines(effect, None) or [""])[0]
        log = StatusEffectMixin._describe_stat_mods({key: value})
        figures = {figure(spell), figure(hover), figure(log)}
        if key in ET._PLAIN_WORDS:
            continue                       # the hover says these as a sentence, on purpose
        if len(figures) != 1:
            bad.append(f"{key}={value}: spell '{spell}', buff '{hover}', log '{log}'")
    if figure(stat_text("damage_taken_pct", -0.4)) != "-40%" or figure(stat_text("damage_taken_pct", -40)) != "-40%":
        bad.append("a fraction and a whole percentage of the same stat read differently")
    if figure(stat_text("haste", 15)) != "+15%" or figure(stat_text("strength", 8)) != "+8" \
            or figure(stat_text("block_value", 25)) != "+25":
        bad.append("haste is not a percentage, or strength / block value is")
    if any(ch.isdigit() for ch in stat_text("cc_immune", 1)) or any(ch.isdigit() for ch in stat_text("taunt", 1)):
        bad.append("a flag is printed with its number")

    print(f"{len(seen)} stat keys checked across spell tooltip, buff hover and combat log")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad[:20]:
            print("  -", line)
        return 1
    print("\nstat text OK - one stat, one number, one unit, wherever it is shown.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
