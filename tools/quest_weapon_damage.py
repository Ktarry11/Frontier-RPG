#!/usr/bin/env python3
"""Give every quest-reward weapon its damage and swing speed. Idempotent.

    PYTHONPATH=. python3 tools/quest_weapon_damage.py          # patch data/quests/*.json
    PYTHONPATH=. python3 tools/quest_weapon_damage.py --check  # report only, exit 1 if any are inert

Item takes weapon_damage_min/max and attack_speed as given and derives nothing, so a weapon written without them
equips as a 0-0 stick (tools/audit_quest_rewards.py, check 5). The numbers come from the generator itself
(tools/build_crafted_gear.reference), seeded on the item's name, so they sit on the same curve as every built weapon
and never change between runs. Only missing numbers are filled: a weapon that already hits keeps what it has.

Held items and relics aren't swung (HELD): a tome, an orb, a totem, a libram or an idol carries stats only, and a
shield is judged on its block value, never on damage.

A quest builder can call arm_quests() on its quests before writing. The two Ashenvale builders whose files held
most of these are older than their data and refuse to run without --force, so a rebuild can't undo this.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

HELD = {"tome", "orb", "totem", "libram", "idol", "shield"}
RANGED = {"bow", "gun", "crossbow", "wand", "thrown"}


def inert(item):
    wt = item.get("weapon_type")
    return bool(wt) and wt not in HELD and not (item.get("weapon_damage_max") and item.get("attack_speed"))


def arm(item):
    """Fill a swung weapon's missing damage and speed off the generator's curve. Returns True if it changed."""
    if not inert(item):
        return False
    import build_crafted_gear as C
    wt = item["weapon_type"]
    out = {"kind": "weapon", "slot": item.get("slot") or ("ranged" if wt in RANGED else "main_hand"),
           "weapon_type": wt, "item_level": int(item.get("item_level") or item.get("required_level") or 10),
           "rarity": item.get("rarity") or "uncommon",
           "stat_template": item.get("stat_template") or ("agi_physical" if wt in RANGED else "str_physical")}
    ref = C.reference("questweapon_" + item["name"], out)
    item["weapon_damage_min"] = item.get("weapon_damage_min") or ref.weapon_damage_min
    item["weapon_damage_max"] = item.get("weapon_damage_max") or ref.weapon_damage_max
    if item["weapon_damage_min"] > item["weapon_damage_max"]:
        item["weapon_damage_min"] = ref.weapon_damage_min
        item["weapon_damage_max"] = ref.weapon_damage_max
    item["attack_speed"] = item.get("attack_speed") or ref.attack_speed
    return True


def arm_quests(quests):
    """arm() every reward weapon in a list of quest dicts; returns how many changed."""
    n = 0
    for q in quests:
        if not isinstance(q, dict):
            continue
        for key in ("unique_item_defs", "rewards"):
            for it in q.get(key) or []:
                if isinstance(it, dict):
                    n += arm(it)
    return n


def _quests(d):
    qs = d if isinstance(d, list) else d.get("quests", [])
    return list(qs.values()) if isinstance(qs, dict) else qs


def main():
    check = "--check" in sys.argv
    total, files = 0, 0
    for p in sorted((ROOT / "data/quests").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        qs = _quests(d)
        if check:
            n = sum(inert(it) for q in qs if isinstance(q, dict)
                    for key in ("unique_item_defs", "rewards") for it in (q.get(key) or []) if isinstance(it, dict))
        else:
            n = arm_quests(qs)
            if n:
                p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        if n:
            total += n
            files += 1
            print(f"  {p.name:34} {n}")
    verb = "inert" if check else "armed"
    print(f"{total} quest-reward weapon(s) {verb} across {files} file(s)")
    return 1 if (check and total) else 0


if __name__ == "__main__":
    sys.exit(main())
