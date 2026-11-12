"""
A spell's tooltip shows the range it rolls in, and the roll stays inside it.

Kyle, 10 Nov: "range for spells (+/- 9% of base) can we show this?"

For every spell_damage and heal ability in the game:
  1. the tooltip's base line reads "<low> to <high>", not one number
  2. low/high are what the roll itself can produce: 400 real rolls of the listed value all land
     inside the printed range, and reach both ends of it (within 2)
And for a weapon strike or a DoT the line is still one number - nothing rolls it.
"""
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def main():
    import random
    import json
    from combat.abilities import _abilities_dir, _ability_from_data
    random.seed(7)
    abilities, ids = [], set()
    for f in sorted(Path(_abilities_dir()).glob("*.json")):
        data = json.loads(f.read_text())
        entries = data.get("abilities", data) if isinstance(data, dict) else data
        if isinstance(entries, dict):
            entries = list(entries.values())
        for entry in entries:
            if isinstance(entry, dict) and entry.get("ability_id") and entry["ability_id"] not in ids:
                ids.add(entry["ability_id"])
                abilities.append(_ability_from_data(entry))
    bad, seen, flat = [], 0, 0
    for ab in abilities:
        lines = ab.get_tooltip_lines()
        line = next((l for l in lines if l.startswith(("Base damage:", "Base healing:"))), None)
        if line is None:
            continue
        if ab.effect_type in ab.ROLLED_EFFECT_TYPES and ab.effect_value:
            seen += 1
            m = re.search(r": (\d+) to (\d+)", line)
            low, high = ab.roll_range(ab.effect_value)
            if low == high:
                continue                                     # too small to have a spread
            if not m:
                bad.append(f"{ab.ability_id}: rolled, but the tooltip says {line!r}")
                continue
            lo, hi = int(m.group(1)), int(m.group(2))
            rolls = [ab._roll_variance(ab.effect_value, None) for _ in range(400)]
            if min(rolls) < lo or max(rolls) > hi:
                bad.append(f"{ab.ability_id}: tooltip {lo}-{hi}, rolled {min(rolls)}-{max(rolls)}")
            elif ab.effect_value >= 60 and (min(rolls) - lo > 2 or hi - max(rolls) > 2):
                bad.append(f"{ab.ability_id}: tooltip {lo}-{hi} is wider than the roll "
                           f"{min(rolls)}-{max(rolls)}")
        elif ab.effect_type in ("damage", "ranged_damage", "dot", "spell_dot", "hot"):
            flat += 1
            if " to " in line.split("over")[0]:
                bad.append(f"{ab.ability_id}: {ab.effect_type} is not rolled but shows a range: {line!r}")
    print(f"{seen} rolled spells checked, {flat} flat ones")
    if seen < 100:
        bad.append(f"rig: only {seen} rolled spells found - the ability list did not load")
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad[:30]:
            print("  ", b)
        return 1
    print("spell ranges OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
