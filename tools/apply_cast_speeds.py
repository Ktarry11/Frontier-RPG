#!/usr/bin/env python3
"""Tag the classic casters' damage spells quick or slow, from Classic's cast times, and size them for it.

    PYTHONPATH=. python3 tools/apply_cast_speeds.py            # show what would change
    PYTHONPATH=. python3 tools/apply_cast_speeds.py --apply

Kyle, 15 Nov 2026, picking "Speed sets next turn" for every caster (combat/abilities.CAST_SPEEDS): a quick spell
hands your turn back after 0.6 of a turn, a slow one holds it for 1.5. Classic's cast times decide which is which -
about 2.5 seconds is a normal turn, instants and 1.5-second casts are quick, 3.5 seconds and up is slow:

  SLOW   Pyroblast (6s), Starfire (3.5s), Aimed Shot (3s)
  QUICK  Fire Blast, Ice Lance, Searing Pain (1.5s), Conflagrate, Mind Blast (1.5s), Earth/Frost/Flame Shock,
         Moonfire, Arcane Shot, Holy Shock, Hammer of Wrath
  everything else stays normal (Fireball, Frostbolt, Shadow Bolt, Smite, Lightning Bolt, Wrath...), and physical
  instants (Rogue and Warrior specials) stay normal - their whole economy is one action a turn.

SIZING, the same rule as the heals: a slow spell is 1.5x for 1.15x the cost (the same per turn of time, cheaper per
point); a quick one 0.65x for 0.85x the cost (a touch more per turn of time, dearer per point, lands sooner).
Idempotent: an ability already carrying this cast_speed is left alone.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SIZE = {"slow": (1.5, 1.15), "quick": (0.65, 0.85)}
TAGS = {
    "mage": {"mage_pyroblast": "slow", "mage_fire_blast": "quick", "mage_ice_lance": "quick"},
    "warlock": {"warlock_searing_pain": "quick", "warlock_conflagrate": "quick"},
    "priest": {"priest_mind_blast": "quick"},
    "shaman": {"shaman_earth_shock": "quick", "shaman_frost_shock": "quick", "shaman_flame_shock": "quick"},
    "druid": {"druid_starfire": "slow", "druid_moonfire": "quick"},
    "hunter": {"hunter_aimed_shot": "slow", "hunter_arcane_shot": "quick"},
    "paladin": {"paladin_holy_shock": "quick", "paladin_hammer_of_wrath": "quick"},
}


def main():
    apply = "--apply" in sys.argv
    changed = 0
    for cls, tags in TAGS.items():
        path = ROOT / f"data/abilities/{cls}.json"
        doc = json.loads(path.read_text(encoding="utf-8"))
        L = doc if isinstance(doc, list) else doc.get("abilities", doc)
        for e in L:
            speed = tags.get(e.get("ability_id"))
            if not speed or e.get("cast_speed") == speed:
                continue
            mult, cmult = SIZE[speed]
            before = [(r["level_req"], r.get("effect_value"), r.get("cost")) for r in e["ranks"]][-1]
            for r in e["ranks"]:
                if r.get("effect_value"):
                    r["effect_value"] = max(1, round(r["effect_value"] * mult))
                if r.get("cost"):
                    r["cost"] = max(1, round(r["cost"] * cmult))
            e["cast_speed"] = speed
            e.setdefault("_tuning", []).append(
                f"15 Nov 2026: a {speed} cast (Kyle: \"Speed sets next turn\"), sized {mult}x for {cmult}x the cost "
                f"(tools/apply_cast_speeds.py)")
            after = [(r["level_req"], r.get("effect_value"), r.get("cost")) for r in e["ranks"]][-1]
            print(f"  {e['ability_id']:28} {speed:5}  top rank {before} -> {after}")
            changed += 1
        if apply:
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{changed} abilities {'tagged' if apply else 'would be tagged'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
