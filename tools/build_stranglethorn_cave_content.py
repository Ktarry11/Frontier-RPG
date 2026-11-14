#!/usr/bin/env python3
"""Stranglethorn cave content pass (2026-10-29). Idempotent.

  PYTHONPATH=. python3 tools/build_stranglethorn_cave_content.py
  cd tools && python3 generate_creatures.py    # after any kit edit (kits: monster_kits.STRANGLETHORN_CAVE_KITS)

One cave per Stranglethorn zone, and each one is a different kind of wet:

  ROTVINE HOLLOW      32-34, under the Zul'Marosh crag.  The crag's stair comes down into standing
                      water and stops, which is where the river that rots the fen downhill starts.
                      Nothing here chose to be here: roots, fungus, river animals, and the trolls the
                      stair dropped, who are still in the water because nobody came down for them.
  VEILFALL CAVE       35-37, behind the waterfall.  The only one of the three with people in it who
                      want to be.  Zul'Rath keep the shrine terraces, light the inside of the fall and
                      argue with the water for a living; everything else in the cave is limestone fauna
                      that got used to the noise.
  THE DROWNED SHRINE  40-42, the bottom terrace of Zul'Kundaraz.  The sea came up the courts and the
                      naga walked in after it.  The court that was standing here when it happened is
                      still standing here, which is the whole of what this cave has to say.

Caves, NOT dungeons (claude/dungeon_authoring_rules.md): random trash off the cave's own table,
`fixed_spawns = False`, one pinned boss and one named rare apiece, no hand-placed packs.  Each cave sits
at or above the top of its parent zone's band, because a cave is never below its zone.

LOOT  ONE item per kill from the creature's own pool of 4; item_level = creature level + 3.
      BUDGET FIXED UP FRONT across the six pools: EIGHT weapons of EIGHT DIFFERENT types with at least
      TWO of them caster weapons, SIXTEEN armour at FOUR APIECE across cloth/leather/mail/plate, and a
      casting share of 40-60%.  audit() fails the build rather than letting it drift toward a melee
      dump, which is what the Aspen pass shipped before anyone was checking.
      NO MAGIC-RESISTANCE GEAR: the deepest thing here is level 42 and the floor for resistance is 45.
      Named rares are lore and loot, never quest targets (standing rule).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

CREATURES = {
    # ---- ROTVINE HOLLOW ------------------------------------------------------------------------
    "Rotvine Strangler": C("beast_large", 32, 33, "rotvine_strangler"),
    "Rotwater Snapper": C("aquatic_basic", 32, 33, "rotwater_snapper"),
    "Sporelit Bat": C("beast_fast", 32, 33, "sporelit_bat"),
    "Zul'Marosh Drowned": C("undead_basic", 33, 34, "zulmarosh_drowned"),
    "Rotcap Walker": C("elemental_bruiser", 33, 34, "rotcap_walker"),
    "Rootmaw": C("beast_large", 34, 34, "rootmaw", True, 1.8),
    "Hap'ka the Drowned": C("undead_basic", 34, 34, "hapka_the_drowned", True, 1.7),

    # ---- VEILFALL CAVE -------------------------------------------------------------------------
    "Veilfall Limeback": C("aquatic_basic", 35, 36, "veilfall_limeback"),
    "Limewing Bat": C("beast_fast", 35, 36, "limewing_bat"),
    "Zul'Rath Shrinekeeper": C("humanoid_warrior", 35, 36, "zulrath_shrinekeeper"),
    "Zul'Rath Mistcaller": C("humanoid_caster", 36, 37, "zulrath_mistcaller"),
    "Spraywater Elemental": C("elemental_caster", 36, 37, "spraywater_elemental"),
    "Veilspeaker Zul'Rath": C("humanoid_caster", 37, 37, "veilspeaker_zulrath", True, 1.8),
    "Sheetfall": C("elemental_bruiser", 37, 37, "sheetfall", True, 1.7),

    # ---- THE DROWNED SHRINE --------------------------------------------------------------------
    "Saltscale Myrmidon": C("humanoid_warrior", 40, 41, "saltscale_myrmidon"),
    "Kundaraz Tidecaller": C("humanoid_caster", 40, 41, "kundaraz_tidecaller"),
    "Terrace Reefclaw": C("aquatic_basic", 40, 41, "terrace_reefclaw"),
    "Sunken Court Drowned": C("undead_basic", 41, 42, "sunken_court_drowned"),
    "Brinefang Eel": C("beast_fast", 41, 42, "brinefang_eel"),
    "Tide-Priestess Myzrai": C("humanoid_caster", 42, 42, "tide_priestess_myzrai", True, 1.9),
    "Saltgorge": C("beast_large", 42, 42, "saltgorge", True, 1.7),
}

#: Each cave's roster is weighted to read as its own place: the Hollow is mostly plant and river with
#: the troll dead as the thing you remember; the Veilfall is held by people; the Shrine is naga with
#: the old court still in the halls under them.
CAVES = {
    "Northern Stranglethorn": ("Rotvine Hollow", {
        "Rotvine Strangler": 4, "Rotwater Snapper": 4, "Sporelit Bat": 3,
        "Zul'Marosh Drowned": 3, "Rotcap Walker": 2,
        "Rootmaw": 0, "Hap'ka the Drowned": 0,
    }),
    "Central Stranglethorn": ("Veilfall Cave", {
        "Zul'Rath Shrinekeeper": 4, "Veilfall Limeback": 3, "Limewing Bat": 3,
        "Zul'Rath Mistcaller": 3, "Spraywater Elemental": 2,
        "Veilspeaker Zul'Rath": 0, "Sheetfall": 0,
    }),
    "Southern Stranglethorn": ("The Drowned Shrine", {
        "Saltscale Myrmidon": 4, "Kundaraz Tidecaller": 3, "Terrace Reefclaw": 3,
        "Sunken Court Drowned": 3, "Brinefang Eel": 2,
        "Tide-Priestess Myzrai": 0, "Saltgorge": 0,
    }),
}

LEVELS = {"Rootmaw": 34, "Hap'ka the Drowned": 34, "Veilspeaker Zul'Rath": 37, "Sheetfall": 37,
          "Tide-Priestess Myzrai": 42, "Saltgorge": 42}

#: Weapons a caster actually wants in hand. Used by audit() so "eight weapons" can't quietly mean
#: eight ways to hit something.
CASTER_WEAPONS = {"staff", "wand", "tome", "idol", "libram", "totem"}


def pools():
    return {
        "Rootmaw": [
            mk("Rootmaw's Drag-Tooth", "main_hand", "of the Bear", 37,
               "It does not bite to kill. It bites to carry you to the drain.", weapon_type="dagger"),
            mk("Sunken Bole Stave", "main_hand", "of the Owl", 37,
               "Root, not wood. The difference matters to whoever has to hold it.", weapon_type="staff"),
            mk("Sinkwader Boots", "feet", "of the Monkey", 37,
               "Everyone who comes out of the Hollow comes out wet to the knee.", armor_type="leather"),
            mk("Outflow Warden's Hauberk", "chest", "of the Eagle", 37,
               "The water leaves the crag here and it has to get past something to do it.",
               armor_type="mail"),
        ],
        "Hap'ka the Drowned": [
            mk("Stairfall Maul", "main_hand", "of the Bear", 37,
               "Zul'Marosh has a stair and the bottom of it is under water.", weapon_type="mace_1h"),
            mk("Hap'ka's Rotted Longbow", "ranged", "of the Eagle", 37,
               "The stave held. Everything that was wrapped around it did not.", weapon_type="bow"),
            mk("Drowned Shelf Wrappings", "chest", "of the Sorcerer", 37,
               "Still laced the way he laced them, and still on him.", armor_type="cloth"),
            mk("Nobody-Came-Down Greaves", "legs", "of the Bear", 37,
               "They knew where he fell. That was never the problem.", armor_type="plate"),
        ],
        "Veilspeaker Zul'Rath": [
            mk("Veilspeaker's Spray-Rod", "main_hand", "of the Sorcerer", 40,
               "He argues with the waterfall daily and has not lost yet.", weapon_type="wand"),
            mk("Terracekeeper's Glaive", "main_hand", "of the Bear", 40,
               "Long enough to reach the terrace below without going down to it.",
               weapon_type="polearm"),
            mk("Mistcaller's Shroud", "chest", "of the Owl", 40,
               "It has not been properly dry since it was made.", armor_type="cloth"),
            mk("Shrinekeeper's Spaulders", "shoulder", "of the Eagle", 40,
               "Carved on the inside, where the keeper can see it and nobody else can.",
               armor_type="mail"),
        ],
        "Sheetfall": [
            mk("Standing Column Bulwark", "off_hand", "of the Bear", 40,
               "It holds its shape for about as long as you need it not to.", weapon_type="shield"),
            mk("Lipwater Jerkin", "chest", "of the Monkey", 40,
               "Cut for someone who works where the floor is always running.", armor_type="leather"),
            mk("Plungewrought Legplates", "legs", "of the Eagle", 40,
               "Water falling this far does the hammering for you.", armor_type="plate"),
            mk("Coif of the Fourth Terrace", "head", "of the Eagle", 40,
               "The lowest one. You hear the pool before you can see over the edge.",
               armor_type="mail"),
        ],
        "Tide-Priestess Myzrai": [
            mk("Myzrai's Court Blade", "main_hand", "of the Sorcerer", 45,
               "Naga work over troll stone. Neither of them asked the other.", weapon_type="sword_1h"),
            mk("Vestments of the Taken Court", "chest", "of the Owl", 45,
               "Cut to the old pattern, by someone who had seen the old pattern.", armor_type="cloth"),
            mk("Terrace-Walker's Treads", "feet", "of the Monkey", 45,
               "The dry ground down here is two spans wide and it is the only road.",
               armor_type="leather"),
            mk("Sanctum Guard's Pauldrons", "shoulder", "of the Bear", 45,
               "Salt gets into the joints of everything and then stays there.", armor_type="plate"),
        ],
        "Saltgorge": [
            mk("Saltgorge Hide Mantle", "shoulder", "of the Monkey", 45,
               "It lives in a hall with a roof on it and comes out at the doorway.",
               armor_type="leather"),
            mk("Deep Hall Chain", "chest", "of the Eagle", 45,
               "Whoever wore it last went into the water in it.", armor_type="mail"),
            mk("Brinelogged Girdle", "waist", "of the Sorcerer", 45,
               "Heavy, and it does not get lighter as it dries, because it does not dry.",
               armor_type="cloth"),
            mk("Courtyard Sabatons", "feet", "of the Bear", 45,
               "Stone, water, stone. You can hear somebody coming the length of the terrace.",
               armor_type="plate"),
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
    if len(wt) != 8 or len(set(wt)) != 8:
        errs.append(f"want 8 weapons of 8 types, got {wt}")
    if len(set(wt) & CASTER_WEAPONS) < 2:
        errs.append(f"want at least 2 caster weapons, got {sorted(set(wt) & CASTER_WEAPONS)}")
    if sorted(ar.values()) != [4, 4, 4, 4] or set(ar) != {"cloth", "leather", "mail", "plate"}:
        errs.append(f"armour not 4 apiece across four classes: {ar}")
    for k, v in out.items():
        if k.startswith("_"):
            continue
        for i in v:
            if i["item_level"] != levels[k] + 3:
                errs.append(f"{i['name']}: ilvl {i['item_level']} != {levels[k]} + 3")
    # Nothing in these three caves is above 42 and resistance gear starts at 45 (standing rule).
    bad_res = [i["name"] for i in items
               if any("resist" in s for s in i.get("primary_stats", {}))
               or any("resist" in s for s in i.get("secondary_stats", {}))]
    if bad_res:
        errs.append(f"magic-resistance gear below level 45: {bad_res}")
    if not 0.40 <= casting / len(items) <= 0.60:
        errs.append(f"casting share {casting}/{len(items)} outside 40-60%")
    if errs:
        raise SystemExit("LOOT BUDGET FAILED:\n  " + "\n  ".join(errs))
    print(f"  loot ok: {len(items)} items, weapons {wt}, armour {ar}, casting {casting}/{len(items)}")


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    # NAME COLLISIONS ARE SILENT DATA LOSS - dict.update() replaced an existing boss on the Drowning
    # Floor pass with no error at all. Twenty-one creatures is not worth trusting to memory.
    clash = [n for n in CREATURES if n in cdata["creatures"]
             and cdata["creatures"][n].get("ability_kit") != CREATURES[n].get("ability_kit")]
    if clash:
        raise SystemExit(f"CREATURE NAME COLLISION (would overwrite existing): {clash}")
    cdata["creatures"].update(CREATURES)

    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))
    for parent, (cave, roster) in CAVES.items():
        z = edata["zones"].setdefault(parent, {})
        z.setdefault("caves", {})[cave] = {"name": cave, "creatures": roster}

    out = {"_notes": "Stranglethorn cave boss and named-rare loot (2026-10-29). ONE item drops per kill "
                     "from the pool. item_level = creature level + 3. Budget checked by audit() in "
                     "tools/build_stranglethorn_cave_content.py. Rares are never quested, and nothing "
                     "here carries magic resistance (floor is level 45)."}
    out.update(pools())
    audit(out, LEVELS)

    (ROOT / "data/loot/stranglethorn_cave_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")
    print(f"Stranglethorn caves: creatures +{len(CREATURES)}, caves {len(CAVES)}, loot pools "
          f"{len(out) - 1}, items {sum(len(v) for k, v in out.items() if not k.startswith('_'))}")


if __name__ == "__main__":
    main()
