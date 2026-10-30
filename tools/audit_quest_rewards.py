#!/usr/bin/env python3
"""Does every quest that was written with gear actually hand it over?

    PYTHONPATH=. python3 tools/audit_quest_rewards.py

WHY THIS EXISTS. Hand-authored reward gear got written under two different keys by two different
generations of builder - `unique_item_defs` and `rewards` - and QuestManager._build_quest only ever
read the first. 166 quests across 13 zones paid experience and gold and dropped 531 authored items
on the floor. Nothing crashed. Nothing warned. You turned the quest in and the reward screen was
empty, and since an empty reward screen looks exactly like a quest written not to give gear, it
survived every pass over this data.

The fix is an alias in _build_quest. This file is the guard, because the fix is one `or` away from
being lost in a merge and the symptom is invisible.

WHAT IT CHECKS, and why each one is worth a line:

  1. Every quest carrying authored gear under ANY key resolves to a non-empty reward set. This is
     the regression that happened. It fails if the alias is removed.
  2. Items survive the trip intact - name, slot, item_level, rarity and the stat blocks come out
     the far side of build_unique_reward_set as authored. `rewards` carries secondary_stats and
     `unique_item_defs` does not, so an alias that quietly dropped a field would pass check 1.
  3. A quest carrying BOTH keys resolves to the unique_item_defs set. Where both exist they are
     duplicates, except aspen's asp_winch_house where the unique entry is a book and the rewards
     are gear - precedence is what keeps already-working quests byte-identical.
  4. No quest promises gear in its prose and hands over nothing.
  5. No reward weapon has zero damage. Item takes weapon_damage_min/max and attack_speed as given
     and derives nothing, so a weapon authored without them equips as a 0-0 damage stick. 79 of
     600 reward weapons are in this state across 20 zones. Reported, NOT auto-fixed: picking the
     numbers is a balance decision per item, and the 521 correct ones sit on a clean curve
     (~0.57 dps per item level for uncommon) that makes each one a short, deliberate choice
     rather than something to sweep.

Exits non-zero on any finding, except check 5, which only warns - it is a backlog, not a
regression, and failing the build on it would mean nobody can use this file for the thing it was
written to guard.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: Prose that tells the player to expect a physical thing. Deliberately narrow - "you will be paid"
#: is gold and must not trip this.
PROMISES_GEAR = re.compile(
    r"\b(take (?:this|one|your pick)|pick (?:one|something)|help yourself|"
    r"choose (?:one|a)|yours to keep|off the rack|from the (?:rack|stores|armoury|armory))\b",
    re.I,
)


def load():
    out = []
    for path in sorted((ROOT / "data/quests").glob("*.json")):
        try:
            data = json.loads(path.read_text())
        except json.JSONDecodeError as e:
            print(f"UNPARSEABLE {path.name}: {e}")
            raise SystemExit(2)
        for q in data.get("quests", []):
            out.append((path.name, q))
    return out


def main():
    from world.quest_manager import QuestManager

    rows = load()
    qm = QuestManager()
    findings = []

    offered = 0
    for fname, q in rows:
        qid = q["quest_id"]
        built = qm.quests.get(qid)
        if built is None:
            findings.append(f"{fname}: {qid} is in the file but did not load")
            continue

        authored = q.get("unique_item_defs") or q.get("rewards")

        # ---- 1. authored gear reaches the reward screen -------------------------------------
        gate_blocks = built.gear_reward_gear_level is None and not built.unique_item_defs
        if authored and gate_blocks:
            findings.append(
                f"{fname}: {qid} authors {len(authored)} reward item(s) but get_gear_choices "
                f"returns [] - the player is handed nothing"
            )
            continue
        if not gate_blocks:
            offered += 1

        # ---- 3. precedence ------------------------------------------------------------------
        if q.get("unique_item_defs") and q.get("rewards"):
            # Compare by VALUE. The first version of this check used `is not` against a dict from
            # a separate json.loads, which is never the same object, so it flagged all 40 quests
            # that legitimately carry both keys. An audit that cannot be trusted gets ignored.
            if built.unique_item_defs != q.get("unique_item_defs"):
                findings.append(
                    f"{fname}: {qid} carries both keys and resolved to the wrong one - "
                    f"unique_item_defs must win"
                )

        # ---- 2. fields survive --------------------------------------------------------------
        if authored and built.unique_item_defs:
            for src in authored:
                match = next(
                    (d for d in built.unique_item_defs if d.get("name") == src.get("name")), None
                )
                if match is None:
                    # Only a real problem when this quest resolved to the key we are reading.
                    if authored == built.unique_item_defs:
                        findings.append(f"{fname}: {qid} lost reward item {src.get('name')!r}")
                    continue
                for field in ("slot", "item_level", "rarity", "required_level",
                              "primary_stats", "secondary_stats", "armor_type", "weapon_type"):
                    if field in src and match.get(field) != src.get(field):
                        findings.append(
                            f"{fname}: {qid} item {src['name']!r} field {field} changed: "
                            f"{src.get(field)!r} -> {match.get(field)!r}"
                        )

        # ---- 4. prose that promises gear ----------------------------------------------------
        prose = f"{q.get('turn_in_text', '')} {q.get('accept_text', '')}"
        if PROMISES_GEAR.search(prose) and gate_blocks:
            hit = PROMISES_GEAR.search(prose).group(0)
            findings.append(
                f"{fname}: {qid} prose says {hit!r} but the quest hands over no gear"
            )

    # ---- 5. zero-damage weapons (warning only, see the module docstring) --------------------
    zero = []
    for fname, q in rows:
        for item in (q.get("unique_item_defs") or []) + (q.get("rewards") or []):
            if item.get("weapon_type") and not item.get("weapon_damage_max"):
                zero.append((fname, q["quest_id"], item["name"], item.get("weapon_type"),
                             item.get("item_level")))

    print(f"quests in data: {len(rows)}   loaded: {len(qm.quests)}   offering gear: {offered}")

    if zero:
        by_file = {}
        for fname, _, _, _, _ in zero:
            by_file[fname] = by_file.get(fname, 0) + 1
        print(f"\nWARNING: {len(zero)} reward weapon(s) have no damage and equip as 0-0 sticks, "
              f"across {len(by_file)} file(s):")
        for fname, count in sorted(by_file.items(), key=lambda kv: -kv[1]):
            print(f"  {fname:34} {count}")
        print("  (backlog, not a regression - see check 5 in this file's docstring)")
    if findings:
        print(f"\n{len(findings)} finding(s):")
        for f in findings:
            print(f"  {f}")
        return 1
    print("\nevery quest that was written with gear hands it over")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
