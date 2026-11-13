#!/usr/bin/env python3
"""Recruit abilities that deal damage, heal or shield grow at 15 / 30 / 45 / 60.

    python3 tools/qa_kit_ranks.py

Kyle, 13 Nov 2026: five ranks "WHEN POSSIBLE ... for attacks or spells or heals that have
potency", "shield or absorb too", and "not each ability will get multiple ranks".

Then: "We need to ensure the END rank is stronger than lvl 60 abilities. So that includes for
dots, hots etc" and "these should be massive 'oh shit' buttons, like trump cards."

Checks the data against tools/rank_kit_abilities.py's own rule, that the last rank beats the
strong end of the class kits at 60 (read live from data/abilities), and that the game really
uses the right rank at each level.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import rank_kit_abilities as R
    from world.recruit_manager import get_recruit_manager

    doc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text())
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict) else rm.recruits)}
    bad, five, trumps = [], 0, []
    for kid, kit in doc.items():
        if kid.startswith("_"):
            continue
        ch = recs[kid].build_character()
        for a in kit["abilities"]:
            ranks, what = a["ranks"], R.grows(a)
            who = f"{kit['name']} / {a['name']}"
            # Kyle, 13 Nov: "i want them all as true trump cards ... they do need cooldowns" -
            # "hence why they have 10-15 turn CDs".
            if (a.get("cooldown") or 0) < 10:
                bad.append(f"{who}: cooldown {a.get('cooldown')} - a trump card has at least 10 turns")
            if ranks != R.ranks_for(a, doc):
                bad.append(f"{who}: ranks are not what tools/rank_kit_abilities.py writes - run it with --apply")
                continue
            if not what:
                if len(ranks) != 1:
                    bad.append(f"{who}: {len(ranks)} ranks on an ability with nothing that grows")
                continue
            five += 1
            if [r["level_req"] for r in ranks] != list(R.LEVELS):
                bad.append(f"{who}: rank levels {[r['level_req'] for r in ranks]}")
            for key in what:
                sizes = [r.get(key, 0) for r in ranks]
                if not all(b > a_ for a_, b in zip(sizes, sizes[1:])) or sizes[-1] < sizes[0] * 2.9:
                    bad.append(f"{who}: {key} goes {sizes}, wanted a steady rise to at least triple")
            # THE POINT (Kyle: "the END rank is stronger than lvl 60 abilities ... massive 'oh
            # shit' buttons"): the last rank against the strong end of the class kits at 60.
            ref = R.class_refs().get(R.kind_of(a)) or 0
            trump = (a.get("cooldown") or 0) >= R.TRUMP_COOLDOWN
            last = R.final_size(a, doc)
            need = ref * (R.LOW if trump else R.SPAMMABLE)
            if last < need - 1:
                bad.append(f"{who}: last rank {last}, the best class {R.kind_of(a)} at 60 is {ref} - wanted at least {need:.0f}")
            if trump:
                trumps.append(last / ref if ref else 0)
            if a["effect_type"] in ("buff", "debuff") and a.get("stat_mods") and len({r.get("effect_value") for r in ranks}) > 1:
                bad.append(f"{who}: effect_value changes by rank on a buff with stat_mods (it scales the mods)")
            ab = next((x for x in ch.ability_book.get_all_abilities() if x.ability_id == a["ability_id"]), None)
            if ab is None:
                bad.append(f"{who}: not in their book")
                continue
            for level, want in ((1, 0), (14, 0), (15, 1), (44, 2), (45, 3), (60, 4)):
                ab.refresh_rank_for_level(level)
                if ab.current_rank_index != want:
                    bad.append(f"{who}: at level {level} uses rank {ab.current_rank_index + 1}, wanted {want + 1}")
            ab.refresh_rank_for_level(60)
            for key in what:
                if key == "effect_value" and ab.effect_value != ranks[4]["effect_value"]:
                    bad.append(f"{who}: at 60 the game reads effect_value {ab.effect_value}, data says {ranks[4]['effect_value']}")
                if key == "absorb" and ab.current_rank.get("absorb") != ranks[4]["absorb"]:
                    bad.append(f"{who}: at 60 the shield is {ab.current_rank.get('absorb')}, data says {ranks[4]['absorb']}")
            ab.refresh_rank_for_level(ch.level)
    print(f"{five} recruit abilities with five ranks")
    if five < 60:
        bad.append(f"only {five} abilities grow - expected about 69")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad[:20]:
            print("  " + b)
        return 1
    trumps.sort()
    print(f"OK: the game uses the right rank at every level; at 60 a trump card is "
          f"{trumps[0]:.1f}x to {trumps[-1]:.1f}x the best class ability of its kind (median {trumps[len(trumps) // 2]:.1f}x)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
