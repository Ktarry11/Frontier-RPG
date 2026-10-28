#!/usr/bin/env python3
"""Southern Thousand Needles content pass (2026-10-28). Idempotent.

  PYTHONPATH=. python3 tools/build_southern_needles_content.py
  cd tools && python3 generate_creatures.py        # after any kit edit (kits: monster_kits.SOUTHERN_NEEDLES_KITS)

The zone shipped with terrain, roads, Freewind and a cave, and nothing alive in it. This is the pass that
fixes that. Band 29-34, which bridges the Aspen Wilderness (25-30, and it IS Northern Thousand Needles)
to Shimmering Flats (33-38).

LEVEL LADDER - and unlike the Aspen Wilderness it runs the ordinary way, because this zone is flat. What
sorts it is not altitude but DISTANCE FROM THE PASS: you come down out of the timber at the top of the
map and the country gets older, drier and less interested in you the further south and east you go.

  The Last Stand      29-30   the aspen tail. The name is the joke and the joke is about to stop being one.
  The Seam            29-30   where the timber quits. Mountain animals, in a desert, failing.
  Redhoof Mesa        30-31   first mesa country. Hyena, vulture, the Galak's western edge.
  Needle's Eye        30-32   the zone's landmark, and the harpies have the top of it.
  The Anvil           31-32   sheer. Nothing walks up it, which is the point of what lives there.
  Lowshelf            31-32   the easiest top in the zone, so everything is on it.
  Broadback           31-33   the big tableland, and the Galak's heartland. The Drowning Floor is under it.
  The Sisters         31-33   two mesas and the gap between them. Galak toll road.
  The Windward Road   32-33   the floor beneath Freewind's three mesas. Contested ground, openly.
  Saltwatch           32-34   the evaporite pans. Salt and the things salt makes.
  Dryhollow           32-34   oldest, driest, furthest from anything. Basilisks.

FIVE POPULATIONS, and the zone's whole argument is in the first two:

  THE SPILL       mountain animals that came down the pass and cannot go back up it. Elk and lynx in a
                  desert, overheating, hunting badly in open ground. This is the EXACT MIRROR of the
                  Aspen Wilderness's Stranded - the kodo standing in snow - and it is deliberate. The
                  Integration did not do one cruel thing in one direction. It opened a door both ways and
                  everything that walked through it is dying of the wrong climate.
  THE GALAK       centaur, and the dominant power on this floor. Not because they won anything: the Great
                  Lift fell, the road north died with it, and the Galak were simply the people already
                  standing on the only ground that still connected to anywhere. They hold the floor, they
                  tax the gaps, and Freewind lives above them because above them is the only place left.
  THE SHEERWING   harpies, on the mesa tops that have no ramps. The terrain was authored with four mesas
                  that cannot be climbed - "whatever is on top of them stays there" - and this is the
                  population that makes that decision pay. Humanoids: cloth and coin, per the harpy rule.
  THE NATIVES     hyena, vulture, scorpid, kodo. The only things here that are where they belong, and
                  the only ones with nothing to say about any of it.
  THE DRY         salt elementals and basilisks, east, where the zone stops being a desert with weather
                  and becomes a pan. These are the step up toward Shimmering Flats.

LOOT  ONE item per kill from the creature's own pool of 4; item_level = creature level + 3.
      BUDGET FIXED UP FRONT: across four pools, FOUR weapons of four DIFFERENT types with ONE a caster
      weapon, TWELVE armour at THREE APIECE across cloth/leather/mail/plate, casting share 40-60%.
      audit() fails the build rather than letting it drift. Named rares are NEVER quested (standing rule).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

CREATURES = {
    # ---- THE SPILL: came down the pass, cannot go back up it, and it is 40 degrees here -------------
    "Sunstruck Elk": C("beast_large", 29, 30, "sunstruck_elk"),
    "Downslope Lynx": C("beast_fast", 29, 30, "downslope_lynx"),

    # ---- THE GALAK: they hold the floor because the floor is all that is left -----------------------
    "Galak Outrider": C("humanoid_warrior", 30, 31, "galak_outrider"),
    "Galak Wrangler": C("humanoid_warrior", 31, 32, "galak_wrangler"),
    "Galak Windcatcher": C("humanoid_caster", 31, 33, "galak_windcatcher"),
    "Galak Khan's Chosen": C("humanoid_warrior", 32, 33, "galak_khans_chosen"),

    # ---- THE SHEERWING: the mesas with no ramps ----------------------------------------------------
    "Sheerwing Harpy": C("humanoid_ranged", 31, 32, "sheerwing_harpy"),
    "Sheerwing Rooktender": C("humanoid_caster", 32, 33, "sheerwing_rooktender"),

    # ---- THE NATIVES -------------------------------------------------------------------------------
    "Dustmane Hyena": C("beast_fast", 29, 31, "dustmane_hyena"),
    "Thermal Vulture": C("beast_fast", 30, 31, "thermal_vulture"),
    "Rimstalker Scorpid": C("vermin_sneaky", 30, 32, "rimstalker_scorpid"),
    "Saltpan Kodo": C("beast_large", 31, 33, "saltpan_kodo"),

    # ---- THE DRY: east, and the step toward Shimmering Flats ---------------------------------------
    "Saltspite Elemental": C("elemental_bruiser", 32, 34, "saltspite_elemental"),
    "Dryhollow Basilisk": C("beast_large", 32, 34, "dryhollow_basilisk"),

    # ---- NAMED RARES. One per ~three subzones, weight 0, never quested.
    "The Thermal": C("beast_fast", 32, 32, "the_thermal", True, 1.7),
    "Oldcrest": C("humanoid_ranged", 32, 32, "oldcrest", True, 1.7),
    "Khan Saltmane": C("humanoid_warrior", 33, 33, "khan_saltmane", True, 1.8),
    "Panglass": C("beast_large", 34, 34, "panglass", True, 1.9),
}

ZONE = {
    "open_zone": {
        "name": "Southern Thousand Needles",
        "creatures": {"Dustmane Hyena": 4, "Galak Outrider": 4, "Thermal Vulture": 3,
                      "Rimstalker Scorpid": 3, "Saltpan Kodo": 3, "Sheerwing Harpy": 2,
                      "Galak Windcatcher": 2,
                      "The Thermal": 0, "Oldcrest": 0, "Khan Saltmane": 0, "Panglass": 0},
    },
    "subzones": {
        # -- the top fifth, still aspen. The Spill, and nothing else: the Galak do not come up here and
        #    the natives have no reason to.
        "The Last Stand": {
            "name": "The Last Stand",
            "creatures": {"Sunstruck Elk": 5, "Downslope Lynx": 4, "Thermal Vulture": 2},
        },
        "The Seam": {
            "name": "The Seam",
            "creatures": {"Downslope Lynx": 4, "Sunstruck Elk": 4, "Dustmane Hyena": 3,
                          "Thermal Vulture": 3},
        },
        # -- mesa country proper
        "Redhoof Mesa": {
            "name": "Redhoof Mesa",
            "creatures": {"Dustmane Hyena": 5, "Thermal Vulture": 3, "Galak Outrider": 3,
                          "Rimstalker Scorpid": 2, "The Thermal": 0},
        },
        "Needle's Eye": {
            "name": "Needle's Eye",
            "creatures": {"Sheerwing Harpy": 5, "Sheerwing Rooktender": 3, "Thermal Vulture": 3,
                          "The Thermal": 0},
        },
        "The Anvil": {
            "name": "The Anvil",
            "creatures": {"Sheerwing Harpy": 5, "Sheerwing Rooktender": 4, "Rimstalker Scorpid": 2,
                          "Oldcrest": 0},
        },
        "Lowshelf": {
            "name": "Lowshelf",
            "creatures": {"Saltpan Kodo": 4, "Dustmane Hyena": 4, "Galak Wrangler": 3,
                          "Rimstalker Scorpid": 3},
        },
        "Broadback": {
            "name": "Broadback",
            "creatures": {"Galak Outrider": 5, "Galak Wrangler": 4, "Galak Windcatcher": 3,
                          "Saltpan Kodo": 3, "Khan Saltmane": 0},
        },
        "The Sisters": {
            "name": "The Sisters",
            "creatures": {"Galak Outrider": 4, "Galak Khan's Chosen": 3, "Galak Windcatcher": 3,
                          "Sheerwing Harpy": 2, "Oldcrest": 0},
        },
        "The Windward Road": {
            "name": "The Windward Road",
            "creatures": {"Galak Khan's Chosen": 4, "Galak Windcatcher": 4, "Galak Outrider": 3,
                          "Saltpan Kodo": 2, "Khan Saltmane": 0},
        },
        # -- east, and drying out
        "Saltwatch": {
            "name": "Saltwatch",
            "creatures": {"Saltspite Elemental": 5, "Saltpan Kodo": 3, "Rimstalker Scorpid": 3,
                          "Dryhollow Basilisk": 2},
        },
        "Dryhollow": {
            "name": "Dryhollow",
            "creatures": {"Dryhollow Basilisk": 5, "Saltspite Elemental": 3, "Rimstalker Scorpid": 3,
                          "Panglass": 0},
        },
    },
}


def pools():
    return {
        "The Thermal": [
            mk("Thermal-Rider's Longbow", "main_hand", "of the Eagle", 35,
               "It has not landed in anyone's memory. People have started checking.",
               weapon_type="bow"),
            mk("Updraft Mantle", "shoulder", "of the Monkey", 35,
               "The heat comes off a mesa top all day and something has learned to live on it.",
               armor_type="leather"),
            mk("Carrion-Watcher's Coif", "head", "of the Owl", 35,
               "It is not waiting for you specifically. It is only waiting.", armor_type="cloth"),
            mk("Sun-Scoured Greaves", "legs", "of the Bear", 35,
               "Red stone holds the day's heat until about two in the morning.", armor_type="plate"),
        ],
        "Oldcrest": [
            mk("Oldcrest's Talonward", "off_hand", "of the Sorcerer", 35,
               "She has held the Anvil since before the Lift fell and does not know it fell.",
               weapon_type="shield"),
            mk("Sheerwing Featherweave", "chest", "of the Physician", 35,
               "Harpies weave. Nobody who calls them animals has looked at the work.",
               armor_type="cloth"),
            mk("Unclimbable Spaulders", "shoulder", "of the Eagle", 35,
               "Four mesas in this zone have no way up. Three of them are hers.", armor_type="mail"),
            mk("Rooktender's Grips", "hands", "of the Monkey", 35,
               "She feeds the ones that cannot fly yet, and there are always some.",
               armor_type="leather"),
        ],
        "Khan Saltmane": [
            mk("Saltmane's Toll-Taker", "main_hand", "of the Bear", 36,
               "The Sisters have a gap between them and he decided what it costs.",
               weapon_type="polearm"),
            mk("Khan's Barded Breastplate", "chest", "of the Bear", 36,
               "Galak work, and good. They were never the savages Freewind needs them to be.",
               armor_type="plate"),
            mk("Hoofguard Sabatons", "feet", "of the Eagle", 36,
               "Centaur do not shoe. These go over, and they are somebody's idea.",
               armor_type="mail"),
            mk("Windcatcher's Cord", "waist", "of the Sorcerer", 36,
               "They read the thermals off the mesas the way a sailor reads water.",
               armor_type="cloth"),
        ],
        "Panglass": [
            mk("Panglass Focus", "main_hand", "of the Owl", 37,
               "The pan behind it is fused to a sheet you can see your own face in.",
               weapon_type="wand"),
            mk("Fused Salt Pauldrons", "shoulder", "of the Bear", 37,
               "Whatever it does, it does to the ground first and to you second.",
               armor_type="plate"),
            mk("Basilisk-Hide Jerkin", "chest", "of the Monkey", 37,
               "Thick, cold, and it does not take dye.", armor_type="leather"),
            mk("Dryhollow Wristguards", "wrist", "of the Eagle", 37,
               "The oldest, driest ground in the zone, and the furthest from anyone.",
               armor_type="mail"),
        ],
    }


def audit(out, levels):
    items = [i for k, v in out.items() if not k.startswith("_") for i in v]
    wt = [i["weapon_type"] for i in items if i.get("weapon_type")]
    ar = {}
    for i in items:
        if i.get("armor_type"):
            ar[i["armor_type"]] = ar.get(i["armor_type"], 0) + 1
    # mk() bakes the suffix into primary_stats and keeps no suffix key - reading a "suffix" key here
    # scored a flat 0 on the Drowning Floor pass and would have waved a melee dump straight through.
    casting = sum(1 for i in items if {"intellect", "spirit"} & set(i.get("primary_stats", {})))
    errs = []
    if len(wt) != 4 or len(set(wt)) != 4:
        errs.append(f"want 4 weapons of 4 types, got {wt}")
    if sorted(ar.values()) != [3, 3, 3, 3] or set(ar) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour not 3 apiece across four classes: {ar}")
    for k, v in out.items():
        if k.startswith("_"):
            continue
        for i in v:
            if i["item_level"] != levels[k] + 3:
                errs.append(f"{i['name']}: ilvl {i['item_level']} != {levels[k]} + 3")
    if not 0.40 <= casting / len(items) <= 0.60:
        errs.append(f"casting share {casting}/{len(items)} outside 40-60%")
    if errs:
        raise SystemExit("LOOT BUDGET FAILED:\n  " + "\n  ".join(errs))
    print(f"  loot ok: {len(items)} items, weapons {wt}, armour {ar}, casting {casting}/{len(items)}")


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    # NAME COLLISIONS ARE SILENT DATA LOSS - dict.update() replaced an existing boss on the Drowning
    # Floor pass with no error at all. Eighteen creatures is not worth trusting to memory.
    clash = [n for n in CREATURES if n in cdata["creatures"]
             and cdata["creatures"][n].get("ability_kit") != CREATURES[n].get("ability_kit")]
    if clash:
        raise SystemExit(f"CREATURE NAME COLLISION (would overwrite existing): {clash}")
    cdata["creatures"].update(CREATURES)

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())
    z = edata["zones"].setdefault("Southern Thousand Needles", {})
    z["open_zone"] = ZONE["open_zone"]
    z["subzones"] = ZONE["subzones"]            # z["caves"] is the Drowning Floor's; left untouched

    levels = {"The Thermal": 32, "Oldcrest": 32, "Khan Saltmane": 33, "Panglass": 34}
    out = {"_notes": "Southern Thousand Needles named-rare loot (2026-10-28). ONE item drops per kill "
                     "from the pool. item_level = creature level + 3. Budget checked by audit() in "
                     "tools/build_southern_needles_content.py. Rares are never quested."}
    out.update(pools())
    audit(out, levels)

    (ROOT / "data/loot/southern_needles_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")
    print(f"Southern Thousand Needles: creatures +{len(CREATURES)}, subzones {len(ZONE['subzones'])}, "
          f"loot pools 4, items {sum(len(v) for k, v in out.items() if not k.startswith('_'))}")


if __name__ == "__main__":
    main()
