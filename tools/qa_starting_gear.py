#!/usr/bin/env python3
"""A new character, and a new companion, starts with gear that fits the class and the spec.

    PYTHONPATH=. python3 tools/qa_starting_gear.py

Kyle, [27] + [48]: "Starting gear must fit the class AND spec - players AND recruits."

Measured 12 Nov: seven classes (every wand, bow and gun class) started with a ranged weapon and
NOTHING IN THE HAND; and the per-spec plans companions are dressed from picked "a one-hander"
as "a sword", so a Barbarian companion carried swords, a Witch Hunter a bow, a Felsworn a
sword - against the class's own listed weapon (axe, crossbow, fist).

SIX CLAIMS:

  1. EVERY CLASS STARTS WITH SOMETHING IN THE MAIN HAND, three pieces of armour of its own
     armour type, and nothing it is not allowed to use.
  2. A CLASS WHOSE SPECS CARRY A RANGED WEAPON STARTS WITH ONE - and a relic is never handed
     out as a starting weapon.
  3. STARTING GEAR IS WHITE: no stats, item level 1. (Kyle, Sept: "general white weapon,
     ranged if needed and a chest piece, pants, and boots.")
  4. A SPEC'S PLAN USES THE CLASS'S OWN WEAPON where the class is known for one and may hold
     it in that hand.
  5. EVERY COMPANION IS HOLDING WHAT ITS SPEC'S PLAN SAYS, in armour of its class's type.
     (An off-hand weapon waits for dual wield at 20 - that is the game's rule, not a miss.)
  6. THE PLANS ARE WHAT THEIR BUILDER BUILDS - tools/build_spec_gear.py and the data agree.
"""
import contextlib
import io
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from entities.character import Character
    from entities.starting_gear import grant_starting_gear, CLASS_WEAPON_TYPE, _REAL_RANGED
    from entities.proficiency import can_wear_weapon_type, _load_class_armor_map
    from world.recruit_manager import get_recruit_manager

RELICS = ("libram", "idol", "totem", "tome")


def main():
    bad = []
    specs = json.load(open("data/items/spec_gear.json"))
    weapons = json.load(open("data/items/weapon_types.json"))
    allowed = weapons["class_weapon_map"]
    armor_of = _load_class_armor_map()
    classes = sorted({v["class"] for v in specs.values()})

    # ---- 1, 2, 3. a new character
    for cls in classes:
        with contextlib.redirect_stdout(io.StringIO()):
            c = Character(name="p", char_class=cls, level=1)
            grant_starting_gear(c)
        eq = {s: i for s, i in c.equipment.slots.items() if i}
        if "main_hand" not in eq:
            bad.append(f"a new {cls} has nothing in the main hand")
        for slot in ("chest", "legs", "feet"):
            if slot not in eq:
                bad.append(f"a new {cls} has no {slot} armour")
            elif eq[slot].armor_type != armor_of.get(cls):
                bad.append(f"a new {cls} wears {eq[slot].armor_type} on the {slot}; the class wears {armor_of.get(cls)}")
        for slot, item in eq.items():
            if item.weapon_type and not can_wear_weapon_type(cls, item.weapon_type):
                bad.append(f"a new {cls} starts with a {item.weapon_type} it may not use")
            if item.weapon_type in RELICS:
                bad.append(f"a new {cls} starts with a relic ({item.weapon_type}) as a weapon")
            if item.rarity != "common" or item.primary_stats or item.secondary_stats or item.item_level != 1:
                bad.append(f"a new {cls}'s {item.name} is not a plain white level 1 item")
        plans = [v["weapons"] for v in specs.values() if v["class"] == cls]
        carry = [p.get("ranged") for p in plans if p.get("ranged") in _REAL_RANGED]
        if len(carry) * 2 >= len(plans) and "ranged" not in eq:
            bad.append(f"{len(carry)} of {cls}'s {len(plans)} specs carry a ranged weapon and a new {cls} has none")

    # ---- 4. the class's own weapon in the plans
    hands = {k: v["hand"] for k, v in weapons["weapon_types"].items()}
    for cls in classes:
        own = CLASS_WEAPON_TYPE.get(cls)
        if not own or own in ("wand", "staff"):
            continue
        family = own.split("_")[0]
        mine = [v["weapons"] for v in specs.values() if v["class"] == cls]
        slot = "ranged" if own in _REAL_RANGED else "main_hand"
        using = [p for p in mine if (p.get(slot) or "").split("_")[0] == family]
        could = [p for p in mine if p.get(slot)]
        if could and not using:
            bad.append(f"{cls} is known for the {own} and none of its {len(mine)} specs carries one "
                       f"({sorted({p.get(slot) for p in could})})")

    # ---- 5. companions
    rm = get_recruit_manager()
    checked = 0
    for rec in rm.recruits.values():
        plan = specs.get(getattr(rec, "spec", None) or "")
        if not plan or rec.recruit_id.startswith("asher"):
            continue          # Asher's kit is hand-built and hash-locked, not dressed from a plan
        with contextlib.redirect_stdout(io.StringIO()):
            c = rm.build_or_restore(rec, player_level=60)
        if c is None:
            continue
        checked += 1
        eq = c.equipment.slots
        for slot in ("main_hand", "ranged"):
            want = plan["weapons"].get(slot)
            have = eq.get(slot).weapon_type if eq.get(slot) else None
            if want != have:
                bad.append(f"{c.name} ({rec.spec}): {slot} holds {have}, the plan says {want}")
        off = eq.get("off_hand")
        if off is not None and off.weapon_type != plan["weapons"].get("off_hand"):
            bad.append(f"{c.name} ({rec.spec}): off hand holds {off.weapon_type}, the plan says "
                       f"{plan['weapons'].get('off_hand')}")
        worn = {i.armor_type for s, i in eq.items() if i is not None and i.armor_type
                and s in ("head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet")}
        if worn and worn != {plan["armor_type"]}:
            bad.append(f"{c.name}: wears {sorted(worn)}, the class wears {plan['armor_type']}")
        for slot in ("chest", "legs", "feet"):
            if eq.get(slot) is None:
                bad.append(f"{c.name} has no {slot} armour")

    # ---- 6. builder and data agree
    before = Path("data/items/spec_gear.json").read_text()
    subprocess.run([sys.executable, "tools/build_spec_gear.py"], capture_output=True, text=True)
    after = Path("data/items/spec_gear.json").read_text()
    if after != before:
        Path("data/items/spec_gear.json").write_text(before)
        bad.append("tools/build_spec_gear.py builds something different from data/items/spec_gear.json")

    print(f"{len(classes)} classes start armed and dressed; {checked} companions hold what their spec plans")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad[:25]:
            print("  -", line)
        return 1
    print("\nstarting gear OK - every class has a weapon in hand and the right armour, and every "
          "companion carries its spec's kit.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
