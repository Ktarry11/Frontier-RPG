"""
Mana keeps regenerating while shapeshifted.

Kyle, 12 Nov: "mana doesnt regen while in shapeshift forms."

Both regen paths asked "is this character's CURRENT resource mana?", and the current resource
follows the form - so a druid in Bear Form was a rage user and got nothing. For every
shapeshift a class has, in every form: mana at the end of a combat turn and over ten seconds
out of combat must rise, and by the same amount as it does unshifted.
"""
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def gains(c):
    c.current_mana = c.mana * 0.25
    before = c.current_mana
    c.restore_resources_between_turns()
    turn = c.current_mana - before
    c.current_mana = c.mana * 0.25
    before = c.current_mana
    for _ in range(10):
        c.tick_out_of_combat_regen(1.0, True)
    return round(turn, 3), round(c.current_mana - before, 3)


def main():
    from entities.character import Character
    bad, checked = [], 0
    for path in sorted((ROOT / "data/abilities").glob("*.json")):
        blob = json.loads(path.read_text())
        entries = blob.get("abilities", blob) if isinstance(blob, dict) else blob
        if isinstance(entries, dict):
            entries = list(entries.values())
        forms = [a["ability_id"] for a in entries
                 if isinstance(a, dict) and a.get("effect_type") == "shapeshift"]
        if not forms:
            continue
        cls = " ".join(w.capitalize() for w in path.stem.split("_"))
        try:
            base = Character(name="T", char_class=cls, level=60)
        except Exception:
            continue
        if base.mana <= 0:
            continue                      # no mana pool to regenerate into
        plain = gains(base)
        if plain[0] <= 0 or plain[1] <= 0:
            bad.append(f"{cls}: regenerates no mana even unshifted {plain} - rig or a wider bug")
            continue
        for fid in forms:
            c = Character(name="T", char_class=cls, level=60)
            ab = c.ability_book.get_ability(fid)
            if ab is None:
                continue
            c.current_mana = c.mana
            ab.turns_remaining = 0
            ab.use(c, c, in_combat=True)
            if not c.current_form:
                continue
            checked += 1
            got = gains(c)
            if got != plain:
                bad.append(f"{cls} in {c.current_form}: mana gain per turn / per 10s is {got}, "
                           f"unshifted it is {plain}")
            else:
                print(f"  ok   {cls} in {c.current_form}: +{got[0]} a turn, +{got[1]} over 10s "
                      f"- same as unshifted")
    if checked == 0:
        print("FAIL no form could be entered - the rig is not reaching shapeshifts")
        return 1
    if bad:
        print(f"FAIL {len(bad)}:")
        for b in bad:
            print("  ", b)
        return 1
    print(f"mana regen OK in {checked} forms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
