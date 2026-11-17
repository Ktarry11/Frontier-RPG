#!/usr/bin/env python3
"""A buff's tooltip says what the buff does, and every heal sits in its healing spec's tab.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_buff_tooltips.py

Kyle, 16 Nov 2026: "It says 12 but it gives 29 spell power" (Flametongue Weapon Rank 8), and "ensure that some things
are put properly like shaman healing spells in wrong tab".

For every class's every buff, at every rank:
  1. the stat line is what the rank applies (the same scaled_stat_mods the cast uses), never the authored number;
  2. a long buff (thirty minutes, kept between fights) says "lasts 30 minutes", never "lasts N turns".
And for the classic healers, every heal, heal over time and revive lands in a spec tab, not in Class.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    from combat.abilities import get_class_abilities
    from ui.spellbook_tree_map import get_owning_tree, HEALING_TREE
    classes = sorted({v["class"] for v in json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8")).values()})
    bad, checked = [], 0
    for c in classes:
        for a in get_class_abilities(c).abilities.values():
            if a.effect_type == "buff":
                for i in range(len(a.ranks) or 1):
                    a.current_rank_index = i
                    lines = a.get_tooltip_lines()
                    text = " | ".join(lines)
                    if a.stat_mods:
                        want = ", ".join(a._stat_mod_text(k, v) for k, v in a.scaled_stat_mods().items())
                        if want not in lines:
                            bad.append(f"{c} {a.name} rank {i + 1}: tooltip doesn't say '{want}'")
                        checked += 1
                    if a.buff_scope == "raid" and "turn" in text.split(";")[-1] and "lasts" in text \
                            and "lasts 30 minutes" not in text:
                        bad.append(f"{c} {a.name}: a thirty-minute buff whose tooltip counts turns")
                a.current_rank_index = 0
            if c in HEALING_TREE and a.effect_type in ("heal", "hot", "revive") and not a.requires_talent:
                if not get_owning_tree(c, a):
                    bad.append(f"{c} {a.name}: a heal with no spec tab (it lands in Class)")
    print(f"{checked} buff ranks checked across {len(classes)} classes")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad[:30]:
            print("  -", b)
        return 1
    print("PASS - every buff's tooltip says what it gives and how long; every heal is in its spec's tab")
    return 0


if __name__ == "__main__":
    sys.exit(main())
