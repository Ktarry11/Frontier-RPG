#!/usr/bin/env python3
"""Ashenvale dungeon content pass (Moonwell Hollow, Howling Barrows, Grom's Rest).  Idempotent.

  PYTHONPATH=. python3 tools/build_ashenvale_dungeon_content.py && python3 tools/generate_creatures.py

Ladder (Kyle's confirmed table, claude/dungeon_levels_and_loot_plan.md):
  Moonwell Hollow  22-25  boss Maelwyn Blightbloom 25          (rare: Mosshide the Gloomcap Elder 24)   [West zone 22-28]
  Howling Barrows  21-24  boss 24                                                                      [East zone 20-25]
  Grom's Rest      26-30 trash, 6 bosses: Satyr Warlord 28 | Void Handmaiden 29 | Doomguard Sentinel 29 | Corrupted Ancient 30 | Felguard Overseer 31 | Lord Nightmare 32
LOOT: ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas (build_durotar_content.make).
Ability kits live in tools/monster_kits.py (ASHENVALE_DUNGEON_KITS); sub-20 bosses have 3 abilities, 20+ have 4.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

DUNGEONS = {}          # key -> dict(region, cave, creatures{}, fixes{}, table{}, pools{}, quest_drops{})


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


# ================================================================================================== MOONWELL HOLLOW
MOONWELL = dict(
    region="Ashenvale West", cave="Moonwell Hollow",
    creatures={
        "Hollow Rotlasher": C("elemental_bruiser", 22, 24, "hollow_rotlasher"),
        "Gloomcap Sporeling": C("vermin_swarm", 22, 23, "gloomcap_sporeling"),
        "Moonwell Mothwing": C("beast_fast", 22, 24, "moonwell_mothwing"),
        "Corrupted Moon Guard": C("humanoid_warrior", 23, 25, "corrupted_moon_guard"),
        "Twilight Rootbinder": C("humanoid_caster", 23, 25, "twilight_rootbinder"),
        "Mosshide the Gloomcap Elder": C("elemental_bruiser", 24, 24, "mosshide_elder", True, 1.7),
        "Maelwyn Blightbloom": C("humanoid_caster", 25, 25, "maelwyn_blightbloom", True, 2.2),
    },
    table={
        "Hollow Rotlasher": 3, "Gloomcap Sporeling": 3, "Moonwell Mothwing": 2, "Corrupted Moon Guard": 2,
        "Twilight Rootbinder": 2, "Twilight Adept": 2, "Satyr Soulstealer": 1,
        "Maelwyn Blightbloom": 0, "Mosshide the Gloomcap Elder": 0,
    },
    quest_drops={
        "Twilight Rootbinder": [qd("moonwell_root_sample", "Blighted Root Sample",
                                   "A fist-sized knot of root, black at the core and still faintly warm. The Moonwell's sap runs "
                                   "through it, and it is wrong.", 0.45)],
        "Gloomcap Sporeling": [qd("gloomcap_spore_sac", "Gloomcap Spore Sac",
                                  "A swollen sac that smells of old cellars. Handle it gently, and then don't.", 0.4)],
    },
)


def moonwell_pools():
    P = {}
    P["Maelwyn Blightbloom"] = [      # L25 -> 28: nature caster staff / cloth chest / leather boots / ring
        make("Blightbloom Staff", "main_hand", "of the Prophet", 28,
             "A staff of root-wood, split at the head where a flower should be. The flower is elsewhere.",
             weapon_type="staff"),
        make("Moonwell-Stained Robes", "chest", "of the Sorcerer", 28,
             "Cloth that went through the Moonwell and came out a different shade of silver.", armor_type="cloth"),
        make("Hollow-Walker's Boots", "feet", "of the Falcon", 28,
             "Soft leather soled in root-fibre. They know where the floor is, even where you don't.",
             armor_type="leather"),
        make("Signet of the Withered Grove", "ring", "of the Restorer", 28,
             "A ring of petrified bark. It does not remember being alive, which may be a mercy.")]
    P["Mosshide the Gloomcap Elder"] = [    # L24 -> 27: shield / mail wrist / neck
        make("Mosshide Bulwark", "off_hand", "of Stamina", 27,
             "A slab of living moss over a stone core. It's damp, and it is very hard to move.", weapon_type="shield"),
        make("Gloomcap Bracers", "wrist", "of the Wolf", 27,
             "Mail bracers with a pale fungus growing between the links. It is, somehow, load-bearing.",
             armor_type="mail"),
        make("Elder's Spore Pendant", "neck", "of the Whale",
             27, "A dried gloomcap on a leather cord. It smells like a cellar and hums like a hive.")]
    return P


MOONWELL["pools"] = moonwell_pools()
DUNGEONS["moonwell"] = MOONWELL
# ===================================================================================================================


# ====================================================================================================== HOWLING BARROWS
BARROWS = dict(
    region="Ashenvale East", cave="Howling Barrows",
    creatures={
        "Rimebone Hound": C("beast_fast", 21, 23, "rimebone_hound"),
        "Barrow Wight": C("undead_basic", 21, 23, "barrow_wight"),
        "Frostbitten Huntsman": C("humanoid_ranged", 22, 24, "frostbitten_huntsman"),
        "Howling Wraith": C("humanoid_caster", 22, 24, "howling_wraith"),
        "Rimeguard Sentinel": C("elemental_bruiser", 22, 24, "rimeguard_sentinel"),
        "Wintermaw the Howling": C("beast_large", 23, 23, "wintermaw_howling", True, 1.7),
        "Hunt-King Valorin": C("humanoid_warrior", 24, 24, "hunt_king_valorin", True, 2.2),
    },
    table={
        "Rimebone Hound": 3, "Barrow Wight": 3, "Frostbitten Huntsman": 2, "Howling Wraith": 2, "Rimeguard Sentinel": 2,
        "Hunt-King Valorin": 0, "Wintermaw the Howling": 0,
    },
    quest_drops={
        "Frostbitten Huntsman": [qd("hunters_horn_shard", "Cracked Hunting Horn",
                                    "A horn of pale bone, split down one side. It still tries to sound when the wind finds it.", 0.45)],
    },
)


def barrows_pools():
    P = {}
    P["Hunt-King Valorin"] = [      # L24 -> 27: 1h sword / plate chest / leather legs / bow
        make("Frostbrand of the Hunt-King", "main_hand", "of the Tiger", 27,
             "A hunter's blade rimed over for a thousand winters. It still remembers the sound a quarry makes.",
             weapon_type="sword_1h"),
        make("Rimeplate Hauberk", "chest", "of the Bear", 27,
             "Plate cold enough to stick to bare skin. The Hunt-King wore it to his grave and then some.",
             armor_type="plate"),
        make("Winterwalker Legguards", "legs", "of the Hunt", 27,
             "Leather stiffened with frost, cut for a rider who never once dismounted.", armor_type="leather"),
        make("Horn-Call Longbow", "ranged", "of the Marksman", 27,
             "A bow of pale heartwood with a horn-mouth carved in the grip. Draw it and something howls back.",
             weapon_type="bow")]
    P["Wintermaw the Howling"] = [  # L23 -> 26: neck / cloak / mail hands
        make("Wintermaw's Fang", "neck", "of the Wolf", 26,
             "A fang as long as a dagger on a cord of frayed gut. The cold goes through it.", ),
        make("Rimefur Cloak", "back", "of the Eagle", 26,
             "Cut from a hound that should not have been able to die, and was.", armor_type="cloth"),
        make("Houndkeeper's Gauntlets", "hands", "of the Bulwark", 26,
             "Chained gauntlets, gnawed through at the knuckle. Whoever wore them lost the argument.",
             armor_type="mail")]
    return P


BARROWS["pools"] = barrows_pools()
DUNGEONS["barrows"] = BARROWS
# ===================================================================================================================


# ========================================================================================================== GROM'S REST
# 6 bosses (Kyle's home-brew dungeon): 2 optional wings off the hub + a 4-boss mandatory gated chain.
GROMS = dict(
    region="Ashenvale East", cave="Grom's Rest",
    creatures={
        # trash 26-30 (kits already exist: satyr / imp / felhound / void_construct); the old "kit" key was ignored by the engine
        "Satyr Cultist": C("humanoid_caster", 26, 30, "satyr"),
        "Dread Imp": C("demon_caster", 26, 30, "imp"),
        "Corrupted Felhound": C("demon_hound", 26, 30, "felhound"),
        "Corrupted Void Construct": C("humanoid_caster", 26, 30, "void_construct"),
        "Felguard Legionnaire": C("humanoid_warrior", 28, 30, "groms_felguard_legionnaire"),
        "Doomguard Warden": C("elemental_bruiser", 27, 30, "groms_doomguard_warden"),
        # bosses
        "Satyr Warlord": C("humanoid_warrior", 28, 28, "groms_satyr_warlord", True, 2.2),
        "Void Handmaiden": C("humanoid_caster", 29, 29, "groms_void_handmaiden", True, 2.2),
        "Doomguard Sentinel": C("elemental_bruiser", 29, 29, "groms_doomguard_sentinel", True, 2.3),
        "Corrupted Ancient": C("elemental_bruiser", 30, 30, "groms_corrupted_ancient", True, 2.4),
        "Felguard Overseer": C("humanoid_warrior", 31, 31, "groms_felguard_overseer", True, 2.4),
        "Lord Nightmare": C("humanoid_caster", 32, 32, "groms_lord_nightmare", True, 2.6),
    },
    table={
        "Satyr Cultist": 3, "Dread Imp": 3, "Corrupted Felhound": 2, "Corrupted Void Construct": 2,
        "Felguard Legionnaire": 2, "Doomguard Warden": 2,
        "Satyr Warlord": 0, "Void Handmaiden": 0, "Doomguard Sentinel": 0, "Corrupted Ancient": 0,
        "Felguard Overseer": 0, "Lord Nightmare": 0,
    },
    quest_drops={
        "Felguard Legionnaire": [qd("legion_brand_plate", "Legion Brand Plate",
                                    "A palm-sized plate of fel-iron stamped with the Legion's mark. The edges are still warm.", 0.45)],
    },
    drop=["Dread Mage Malik", "Possessed Oracle"],       # superseded by the 6-boss roster (never placed, kits were dead)
)


def groms_pools():
    P = {}
    P["Satyr Warlord"] = [          # L28 -> 31
        make("Warlord's Hewing Cleaver", "main_hand", "of Strength", 31,
             "A two-handed satyr axe, notched by every war it never lost.", weapon_type="axe_2h"),
        make("Horn-Plated Spaulders", "shoulder", "of the Bear", 31,
             "Mail pauldrons with a ram's horn riveted to each. They are heavier than they look and louder than they should be.",
             armor_type="mail"),
        make("Cloven-Hide Belt", "waist", "of the Tiger", 31,
             "Leather cut from something with split hooves. It pulls tight and never quite lets go.", armor_type="leather"),
        make("Signet of the Ritual Hall", "ring", "of the Wolf", 31,
             "A ring of blackened horn. It is warm in the way a hand is warm, and nobody is attached to it.")]
    P["Void Handmaiden"] = [        # L29 -> 32
        make("Handmaiden's Veilwand", "ranged", "of the Void", 32,
             "A wand of pale wood that does not quite reflect light. Point it at a thing and the thing is a little less there.",
             weapon_type="wand"),
        make("Veilweave Robes", "chest", "of the Sorcerer", 32,
             "Cloth that hangs as if the wearer were underwater. They stopped noticing years ago.", armor_type="cloth"),
        make("Gloves of Quiet Hunger", "hands", "of Shadow Wrath", 32,
             "Thin gloves, very patient. They finish sentences you have not said yet.", armor_type="cloth"),
        make("Siphon Pendant", "neck", "of the Seer", 32,
             "A bead of violet glass. Hold it to the light and the light holds back.")]
    P["Doomguard Sentinel"] = [     # L29 -> 32
        make("Doomplate Greaves", "legs", "of the Bulwark", 32,
             "Plate that has stood in the fire for a very long time and has not been asked to move.", armor_type="plate"),
        make("Sentinel's Bulwark", "off_hand", "of Stamina", 32,
             "A tower shield with a brazier's soot worked into the face. Things that hit it come away burnt.",
             weapon_type="shield"),
        make("Emberforged Gauntlets", "hands", "of Strength", 32,
             "Mail gauntlets still ticking as they cool. You get used to it.", armor_type="mail"),
        make("Brand of the Doomguard", "ring", "of the Defender", 32,
             "A hot-iron ring that has never been quite cool. It does not burn the wearer. It insists.")]
    P["Corrupted Ancient"] = [      # L30 -> 33
        make("Heartwood of the Fallen Grove", "main_hand", "of Nature's Wrath", 33,
             "A staff of root and rot, with a heart-shaped knot at the head. It beats slowly.", weapon_type="staff"),
        make("Mantle of Twisted Boughs", "shoulder", "of the Falcon", 33,
             "Leather braided from living bark. It grows a little each time you look away.", armor_type="leather"),
        make("Rotbark Cloak", "back", "of the Eagle", 33,
             "A cloak of layered bark that sheds without ever getting thinner.", armor_type="cloth"),
        make("Wardroot Circlet", "head", "of the Restorer", 33,
             "A woven crown of root. It was green once, and wants to be again.", armor_type="leather")]
    P["Felguard Overseer"] = [      # L31 -> 34
        make("Overseer's Fel-Edge", "main_hand", "of the Champion", 34,
             "A long fel-iron blade, ridged for the cutting of chains and the lengthening of sentences.",
             weapon_type="sword_1h"),
        make("Legion Warplate", "chest", "of the Soldier", 34,
             "Plate stamped with the Legion's mark. It fits like it knew you were coming.", armor_type="plate"),
        make("Sunderchain Girdle", "waist", "of the Bear", 34,
             "Heavy links, each stamped with a name. Somebody kept count.", armor_type="mail"),
        make("Overseer's Collar", "neck", "of the Tactician", 34,
             "A fel-iron band, split at the clasp. Whoever it collared learned the clasp from the outside.")]
    P["Lord Nightmare"] = [         # L32 -> 35
        make("Gaze of the Inner Sanctum", "head", "of the Archmage", 35,
             "A cowl with no face inside it, and no need for one.", armor_type="cloth"),
        make("Staff of Eldritch Hours", "main_hand", "of the Necromancer", 35,
             "A staff of dark glass that tells the wrong time on purpose. Everything it counts down to is the same thing.",
             weapon_type="staff"),
        make("Dreadweave Leggings", "legs", "of Shadow Wrath", 35,
             "Cloth that remembers a very long nightmare and offers to share.", armor_type="cloth"),
        make("Horror-Touched Dirk", "main_hand", "of the Assassin", 35,
             "A short blade of void-glass. It does not so much cut as subtract.", weapon_type="dagger")]
    return P


GROMS["pools"] = groms_pools()
DUNGEONS["groms"] = GROMS
# ===================================================================================================================


def main():
    only = [a for a in sys.argv[1:] if not a.startswith("-")]
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text(encoding="utf-8"))
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text(encoding="utf-8"))
    qp = ROOT / "data/creatures/quest_drops.json"
    qdata = json.loads(qp.read_text(encoding="utf-8"))
    for key, D in DUNGEONS.items():
        if only and key not in only:
            continue
        cdata["creatures"].update(D["creatures"])
        for gone in D.get("drop", []):
            cdata["creatures"].pop(gone, None)
        if D["cave"] in edata:                       # legacy top-level table (never read by the spawn code)
            edata.pop(D["cave"])
        for n, patch in D.get("fixes", {}).items():
            cdata["creatures"].setdefault(n, {}).update(patch)
        z = edata["zones"][D["region"]]
        z.setdefault("caves", {})[D["cave"]] = {"name": D["cave"], "creatures": D["table"]}
        for creature, drops in D.get("quest_drops", {}).items():
            qdata["drops"].setdefault(creature, [])
            keep = [d for d in qdata["drops"][creature] if d["item_id"] not in {x["item_id"] for x in drops}]
            qdata["drops"][creature] = keep + drops
        out = {"_notes": f"{D['cave']} boss + rare loot (2026-10-22). ONE item drops per kill from the pool. "
                         "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
        out.update(D["pools"])
        fn = D["cave"].lower().replace("'", "").replace(" ", "_") + "_boss_loot.json"
        (ROOT / "data/loot" / fn).write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
        n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
        print(f"{D['cave']}: creatures +{len(D['creatures'])}, pools {len(out) - 1}, items {n} -> {fn}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n", encoding="utf-8")
    ep.write_text(json.dumps(edata, indent=2) + "\n", encoding="utf-8")
    qp.write_text(json.dumps(qdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
