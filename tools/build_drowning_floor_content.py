#!/usr/bin/env python3
"""The Drowning Floor content pass (2026-10-28). Idempotent.

  PYTHONPATH=. python3 tools/build_drowning_floor_content.py
  cd tools && python3 generate_creatures.py        # after any kit edit

THE ROSTER IS AN ANSWER TO ONE QUESTION: what can live somewhere that fills to the roof once a year?

Only three kinds of thing can. Something that LEAVES, something that does not need to breathe, and
something that is not there yet when it happens. Every creature down here is one of those three, and a
player who works that out has read the place correctly without being told a word of it.

  THE DRY-SEASON TENANTS   kodo come down out of the heat, and the Galak come down after the kodo. Both
                           of them are gone before the rains - the Galak keep a calendar for it, which is
                           the single most civilised thing about them. Humanoids, so: cloth and coin.
  THE DROWNED              what the calendar got wrong. Salt has set over them the way it sets over
                           everything the flood leaves, and they did not stop walking.
  THE YEAR-ROUND           the Sump, which never dries. Two things live in it and neither has eyes.

LEVELS 33-35 against a 30-35 parent zone. Cave rule: a cave is never below its zone.

CAVE, not dungeon (claude/dungeon_authoring_rules.md): random trash from its own table,
`fixed_spawns = False`, one pinned boss and two named rares, no hand-placed packs.

LOOT  ONE item per kill from the creature's own pool of 4; item_level = creature level + 3.
      BUDGET FIXED UP FRONT, as it has been since the Aspen pass shipped a melee dump: across the three
      pools, THREE weapons of three DIFFERENT types with ONE of them a caster weapon, EIGHT armour
      pieces at TWO APIECE across cloth/leather/mail/plate, and one trinket. Checked below, not assumed.
      Named rares are never quested (standing rule).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

CREATURES = {
    # ---- THE DRY-SEASON TENANTS. Here because it is 40 degrees upstairs and not down here.
    "Sightless Kodo": C("beast_large", 33, 34, "sightless_kodo"),
    "Galak Dryseason Raider": C("humanoid_warrior", 33, 34, "galak_dryseason_raider"),
    "Galak Stormcaller": C("humanoid_caster", 34, 35, "galak_stormcaller"),
    # ---- THE DROWNED. What the calendar got wrong, with the salt set hard over it.
    "Saltbound Shambler": C("humanoid_warrior", 33, 34, "saltbound_shambler"),
    # ---- THE YEAR-ROUND. The Sump and the wrack line.
    "Washline Scuttler": C("vermin_sneaky", 33, 34, "washline_scuttler"),
    "Sumpblind Thresher": C("beast_fast", 34, 35, "sumpblind_thresher"),

    # ---- the boss, pinned in the Sump, and two named rares. Never quested.
    "Yearmaw": C("beast_large", 35, 35, "yearmaw", True, 1.9),
    "The Leavings": C("beast_large", 34, 34, "the_leavings", True, 1.7),
    "Old Saltbed": C("beast_large", 34, 34, "old_saltbed", True, 1.7),
}

#: Weighted so the cave reads as its own geography. The Galak hold the dry middle because that is where
#: a camp goes; the drowned are thickest near the water that made them; the Sump is the Sump.
CAVE = {
    "name": "The Drowning Floor",
    "creatures": {"Galak Dryseason Raider": 4, "Sightless Kodo": 4, "Saltbound Shambler": 3,
                  "Washline Scuttler": 3, "Galak Stormcaller": 2, "Sumpblind Thresher": 2,
                  "Yearmaw": 0, "The Leavings": 0, "Old Saltbed": 0},
}


def pools():
    return {
        "Yearmaw": [
            mk("Yearmaw's Drowned Fang", "main_hand", "of the Tiger", 38,
               "It feeds once, on the day the cave fills, and then it waits out the year.",
               weapon_type="fist_weapon"),
            mk("Sumpblind Hauberk", "chest", "of the Eagle", 38,
               "Nothing that lives in that water has needed eyes in a very long time.",
               armor_type="mail"),
            mk("High-Water Greaves", "legs", "of the Bear", 38,
               "The mark is above your head on every pillar down here. Look up once and then do not.",
               armor_type="plate"),
            mk("Yearmaw's Salt-Cured Hide", "chest", "of the Monkey", 38,
               "A year in standing brine does to a skin what no tanner can.", armor_type="leather"),
        ],
        "The Leavings": [
            mk("Wrackline Shiv", "off_hand", "of the Monkey", 37,
               "Cut from something the flood brought in. It is not bone and it is not wood.",
               weapon_type="dagger"),
            mk("Driftwood Bracers", "wrist", "of the Eagle", 37,
               "Three years in the pile and the grain has gone hard as fired clay.",
               armor_type="leather"),
            mk("Pillar-Shadow Cowl", "head", "of the Sorcerer", 37,
               "It denned where the roof came down, and the roof came down a long time ago.",
               armor_type="cloth"),
            mk("Floodmark Pendant", "trinket", "of the Owl", 37,
               "Somebody wore this and did not get out. The cord outlasted them."),
        ],
        "Old Saltbed": [
            mk("Saltbed's Evaporite Staff", "main_hand", "of the Owl", 37,
               "White all the way through, and it rings when you set it down.", weapon_type="staff"),
            mk("Crusted Kodo Pauldrons", "shoulder", "of the Bear", 37,
               "He came down out of the heat one dry season and the salt closed over him in that one.",
               armor_type="plate"),
            mk("Dry-Season Wraps", "hands", "of the Physician", 37,
               "The Galak keep a calendar for this cave. It is the best thing about them.",
               armor_type="cloth"),
            mk("Bedding-Plane Spaulders", "shoulder", "of the Monkey", 37,
               "One soft layer between two hard ones. The whole cave is that, and nothing else.",
               armor_type="mail"),
        ],
    }


def audit(out):
    """Fail the build on budget drift rather than discovering it in-game six zones later."""
    items = [i for k, v in out.items() if not k.startswith("_") for i in v]
    wt = [i["weapon_type"] for i in items if i.get("weapon_type")]
    ar = {}
    for i in items:
        if i.get("armor_type"):
            ar[i["armor_type"]] = ar.get(i["armor_type"], 0) + 1
    # mk() bakes the suffix into primary_stats and keeps no suffix key, so caster-ness is read off the
    # STATS. Checking the name for "of the Owl" silently scored 0/12 and would have passed a melee dump
    # the moment the floor dropped - exactly the failure this audit exists to catch.
    casting = sum(1 for i in items
                  if {"intellect", "spirit"} & set(i.get("primary_stats", {})))
    errs = []
    if len(wt) != len(set(wt)):
        errs.append(f"duplicate weapon types: {wt}")
    if sorted(ar.values()) != [2, 2, 2, 2] or set(ar) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour not 2 apiece across four classes: {ar}")
    lvl = {"Yearmaw": 35, "The Leavings": 34, "Old Saltbed": 34}
    for k, v in out.items():
        if k.startswith("_"):
            continue
        for i in v:
            if i["item_level"] != lvl[k] + 3:
                errs.append(f"{i['name']}: ilvl {i['item_level']} != {lvl[k]} + 3")
    if not 0.30 <= casting / len(items) <= 0.60:
        errs.append(f"casting share {casting}/{len(items)}")
    if errs:
        raise SystemExit("LOOT BUDGET FAILED:\n  " + "\n  ".join(errs))
    print(f"  loot ok: {len(items)} items, weapons {wt}, armour {ar}, casting {casting}/{len(items)}")


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    # NAME COLLISIONS ARE SILENT DATA LOSS. This pass originally called its east-bay rare "The Tidewrack"
    # and dict.update() quietly replaced a L26 undead boss of that name on the other side of the world -
    # same name, same kit id, no error, gone. Nine creatures is not worth trusting to memory.
    clash = [n for n in CREATURES if n in cdata["creatures"]
             and cdata["creatures"][n].get("ability_kit") != CREATURES[n].get("ability_kit")]
    if clash:
        raise SystemExit(f"CREATURE NAME COLLISION (would overwrite existing): {clash}")
    cdata["creatures"].update(CREATURES)

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())
    z = edata["zones"].setdefault("Southern Thousand Needles", {})
    z.setdefault("caves", {})["The Drowning Floor"] = CAVE

    out = {"_notes": "The Drowning Floor boss and named-rare loot (2026-10-28). ONE item drops per kill "
                     "from the pool. item_level = creature level + 3. Budget checked by audit() in "
                     "tools/build_drowning_floor_content.py."}
    out.update(pools())
    audit(out)

    (ROOT / "data/loot/drowning_floor_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")
    print(f"The Drowning Floor: creatures +{len(CREATURES)}, loot pools 3, "
          f"items {sum(len(v) for k, v in out.items() if not k.startswith('_'))}")


if __name__ == "__main__":
    main()
