#!/usr/bin/env python3
"""Every stat on the party sheet can be hovered, and says what it does for that member.

    PYTHONPATH=. SDL_VIDEODRIVER=dummy python3 tools/qa_stat_tooltips.py

Kyle, 16 Nov 2026: "lets do it wow style where you HOVER OVER the spell power and it breaks it down by school", and
"we should be able to hover over ALL stats and see what they offer? Crit? mana? HP....etc".

For a warrior, a rogue, a shaman and a priest at 60:
  1. every row of the Stats tab has a tooltip, and a primary stat's says what it gives;
  2. Spell power's lists all six schools and Healing;
  3. working a tooltip out never changes the member (health, mana, every derived stat stay put);
  4. the Stats tab no longer prints a "SPELL POWER BY SCHOOL" block.
"""
import inspect
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

IDS = ["strength", "agility", "stamina", "intellect", "spirit", "armor", "attack_power", "ranged_attack_power",
       "spell_power", "healing_power", "crit_chance_physical", "crit_chance_spell", "haste", "dodge", "parry",
       "block_chance", "block_value", "mana_per_turn", "mana_per_turn_casting", "hp5", "spell_penetration",
       "resist_fire", "resist_frost", "resist_arcane", "resist_shadow", "resist_nature", "resist_holy"]


def main():
    from entities.character import Character
    from ui.stat_tooltips import stat_tooltip, DERIVED
    import ui.screens.party_screen as PS
    bad = []
    for cls in ("Warrior", "Rogue", "Shaman", "Priest"):
        c = Character("T", cls, 60)
        before = {k: getattr(c, k, None) for k, _l, _p in DERIVED} | {"cur_h": c.current_health,
                                                                      "cur_m": c.current_mana}
        for sid in IDS:
            lines = stat_tooltip(c, sid)
            if not lines:
                bad.append(f"{cls}: '{sid}' has no tooltip")
        for st in ("stamina", "intellect" if cls in ("Shaman", "Priest") else "strength"):
            if not any(k == "good" for _t, k in stat_tooltip(c, st)):
                bad.append(f"{cls}: {st}'s tooltip doesn't say what it gives")
        sp = " ".join(t for t, _k in stat_tooltip(c, "spell_power"))
        for school in ("Arcane", "Fire", "Frost", "Nature", "Shadow", "Holy", "Healing"):
            if school not in sp:
                bad.append(f"{cls}: Spell power's tooltip leaves out {school}")
        after = {k: getattr(c, k, None) for k, _l, _p in DERIVED} | {"cur_h": c.current_health,
                                                                     "cur_m": c.current_mana}
        if before != after:
            bad.append(f"{cls}: working out the tooltips changed the character: "
                       f"{ {k: (before[k], after[k]) for k in before if before[k] != after[k]} }")
    if 'block("SPELL POWER BY SCHOOL"' in inspect.getsource(PS.PartyScreen._render_stats):
        bad.append("the Stats tab still prints a SPELL POWER BY SCHOOL block")
    if bad:
        print(f"FAIL ({len(bad)})")
        for b in bad[:20]:
            print("  -", b)
        return 1
    print(f"PASS - {len(IDS)} stats hover with what they do, spell power breaks down by school, nothing moves")
    return 0


if __name__ == "__main__":
    sys.exit(main())
