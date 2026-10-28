#!/usr/bin/env python3
"""Aspen Wilderness content pass (2026-10-27). Idempotent.

  PYTHONPATH=. python3 tools/build_aspen_content.py
  cd tools && python3 generate_creatures.py        # after any kit edit (kits: monster_kits.ASPEN_KITS)

LEVEL LADDER - and it runs the opposite way to every other zone in the game, because this zone does.
You arrive at the TOP of the mountain and descend, so the levels rise as you go DOWN:

  The Broken Lift     25      the Barrens plateau, the platform, and the Seam running across it
  The Seam            25-26   the line itself. Things that came across and should not have.
  The Rim             25-27   the escarpment. Harpies, nesting where harpies actually do nest.
  The Gold Stands     26-28   aspen. Elk, lynx, and the tauren who are learning to log it.
  Blackneedle Rise    27-29   lodgepole. Wolves and bears, and no sightlines.
  The Slide           27-29   quilboar, pushed up out of the Barrens and furious about the cold.
  The Burn            28-29   old fire. Scavengers and the ravens that are not quite ravens.
  Elkhorn Meadow      28-29   the open park. Herds, and what follows herds.
  Beaverdam Benches   29-30   the valley floor. Water, dams, bears at the water, a quilboar den.
  The Weeping Ice     29-31   the cave. Bears and yetis. Rimehowl 31.

FIVE POPULATIONS, and each one is a different answer to "what does an overlay do to the things living
under it":

  THE STRANDED    creatures the Integration caught on the wrong side of the Seam and did not kill. The
                  kodo is the clearest case - a Barrens animal standing in snow, which is not a monster
                  design so much as a thing that is going to die and has not finished.
  THE DISPLACED   harpies and quilboar, pushed UP out of the Barrens by the mountain taking their ground.
                  They are not here because they like it. The quilboar in particular are a desert people
                  wintering badly, and their kits are built around that: they fight hard and briefly.
  THE NATIVE      elk, lynx, wolves, bears, beaver. The mountain brought its own fauna with it and these
                  are doing FINE - they are the only things in the zone that are where they belong.
  THE SCAVENGERS  the burn's population. Fire happened before the player arrived and something has been
                  eating it ever since.
  THE YETIS       the cave. They came across inside the glacier, the glacier is melting out from under
                  them, and they are cornered at the one end of it that is still frozen. See
                  tools/handbuilt_weeping_ice.py - the cave's shape IS this story.

CAVE RULE (claude/dungeon_authoring_rules.md): The Weeping Ice is a CAVE, not a dungeon - random trash
from its own table, `fixed_spawns = False`, one pinned boss and two named rares. No hand-placed packs.
Cave level rule: a cave is never below its zone, so 29-31 against a 25-30 zone is correct.

LOOT  ONE item per kill from the creature's own pool of 4; item_level = creature level + 3; real loot
      formulas (tools/build_durotar_content.make). Named rares are is_boss with weight 0 - they roll at
      ~6% in their subzone, and per the standing rule NO QUEST IS EVER BUILT AROUND A RARE.
      Budget is fixed up front and checked by tools/qa_aspen_content.py rather than discovered after.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make as mk, C  # noqa: E402

# ======================================================================================================
# CREATURES
# ======================================================================================================
ASPEN_CREATURES = {
    # ---- THE STRANDED: caught on the wrong side of the Seam
    "Seam-Struck Kodo": C("beast_large", 25, 26, "seam_struck_kodo"),
    "Redscrub Scavenger": C("vermin_sneaky", 25, 26, "redscrub_scavenger"),

    # ---- THE DISPLACED: pushed up out of the Barrens by the mountain taking their ground
    "Rimcliff Harpy": C("humanoid_ranged", 25, 27, "rimcliff_harpy"),
    "Rimcliff Windcaller": C("humanoid_caster", 26, 28, "rimcliff_windcaller"),
    "Quilboar Highrunner": C("humanoid_warrior", 27, 29, "quilboar_highrunner"),
    "Quilboar Frostspeaker": C("humanoid_caster", 28, 29, "quilboar_frostspeaker"),
    "Quilboar Dencarver": C("humanoid_warrior", 29, 30, "quilboar_dencarver"),

    # ---- THE NATIVE: the fauna that came with the mountain and is doing fine
    "Aspen Elk": C("beast_large", 26, 28, "aspen_elk"),
    "Goldwood Lynx": C("beast_fast", 26, 28, "goldwood_lynx"),
    "Blackneedle Wolf": C("beast_fast", 27, 29, "blackneedle_wolf"),
    "Timber Bear": C("beast_large", 27, 29, "timber_bear"),
    "Elkhorn Stag": C("beast_large", 28, 29, "elkhorn_stag"),
    "Benchwater Dambuilder": C("beast_basic", 29, 30, "benchwater_dambuilder"),
    "Pondside Bear": C("beast_large", 29, 30, "pondside_bear"),

    # ---- THE SCAVENGERS: the burn's population
    "Ashcrown Raven": C("beast_fast", 28, 29, "ashcrown_raven"),
    "Charwood Prowler": C("vermin_sneaky", 28, 29, "charwood_prowler"),

    # ---- named rares, open zone. One per three subzones, never quested.
    "The Last Kodo": C("beast_large", 27, 27, "the_last_kodo", True, 1.6),
    "Goldcrown": C("beast_large", 28, 28, "goldcrown", True, 1.7),
    "Bristlehide the Wintered": C("humanoid_warrior", 30, 30, "bristlehide_the_wintered", True, 1.8),
}

#: THE WEEPING ICE. Bears and yetis, per Kyle. The split is deliberate: bears nearer the door where it is
#: wet and warm, yetis cornered at the frozen end. A player who notices that has read the cave correctly.
ICE_CREATURES = {
    "Winterhide Bear": C("beast_large", 29, 30, "winterhide_bear"),
    "Thawbone Crawler": C("vermin_sneaky", 29, 30, "thawbone_crawler"),
    "Meltwater Yeti": C("beast_large", 29, 31, "meltwater_yeti"),
    "Rimefist Yeti": C("beast_large", 30, 31, "rimefist_yeti"),
    "Glacier Bear": C("beast_large", 30, 31, "glacier_bear"),
    # boss and named rares
    "Rimehowl": C("beast_large", 31, 31, "rimehowl", True, 1.9),
    "Snowmaw": C("beast_large", 30, 30, "snowmaw", True, 1.7),
    "The Last Drift": C("beast_large", 30, 30, "the_last_drift", True, 1.7),
}

# ======================================================================================================
# ENCOUNTERS
# ======================================================================================================
ASPEN_ZONE = {
    "open_zone": {
        "name": "The Aspen Wilderness",
        "creatures": {"Aspen Elk": 4, "Goldwood Lynx": 3, "Blackneedle Wolf": 3, "Timber Bear": 3,
                      "Rimcliff Harpy": 3, "Quilboar Highrunner": 2, "Ashcrown Raven": 2,
                      "The Last Kodo": 0, "Goldcrown": 0, "Bristlehide the Wintered": 0},
    },
    "subzones": {
        "The Broken Lift": {
            "name": "The Broken Lift",
            "creatures": {"Redscrub Scavenger": 5, "Seam-Struck Kodo": 3, "Ashcrown Raven": 2},
        },
        "The Seam": {
            "name": "The Seam",
            "creatures": {"Seam-Struck Kodo": 5, "Redscrub Scavenger": 4, "Ashcrown Raven": 3,
                          "The Last Kodo": 0},
        },
        "The Rim": {
            "name": "The Rim",
            "creatures": {"Rimcliff Harpy": 5, "Rimcliff Windcaller": 3, "Ashcrown Raven": 3},
        },
        "The Gold Stands": {
            "name": "The Gold Stands",
            "creatures": {"Aspen Elk": 5, "Goldwood Lynx": 4, "Rimcliff Harpy": 2, "Goldcrown": 0},
        },
        "Blackneedle Rise": {
            "name": "Blackneedle Rise",
            "creatures": {"Blackneedle Wolf": 5, "Timber Bear": 4, "Goldwood Lynx": 3},
        },
        "The Slide": {
            "name": "The Slide",
            "creatures": {"Quilboar Highrunner": 5, "Quilboar Frostspeaker": 3, "Blackneedle Wolf": 2},
        },
        "The Burn": {
            "name": "The Burn",
            "creatures": {"Charwood Prowler": 5, "Ashcrown Raven": 4, "Blackneedle Wolf": 2},
        },
        "Elkhorn Meadow": {
            "name": "Elkhorn Meadow",
            "creatures": {"Elkhorn Stag": 5, "Aspen Elk": 4, "Blackneedle Wolf": 3, "Goldcrown": 0},
        },
        "Beaverdam Benches": {
            "name": "Beaverdam Benches",
            "creatures": {"Benchwater Dambuilder": 4, "Pondside Bear": 4, "Quilboar Dencarver": 3,
                          "Bristlehide the Wintered": 0},
        },
    },
    "caves": {
        "The Weeping Ice": {
            "name": "The Weeping Ice",
            "creatures": {"Winterhide Bear": 4, "Meltwater Yeti": 4, "Glacier Bear": 3,
                          "Rimefist Yeti": 3, "Thawbone Crawler": 3,
                          "Rimehowl": 0, "Snowmaw": 0, "The Last Drift": 0},
        },
    },
}


# ======================================================================================================
# LOOT - boss and named-rare pools. Four items each; one drops per kill.
# ======================================================================================================
def aspen_pools():
    """Open-zone named rares. Spread across armour classes and weapon types on purpose - see the header."""
    return {
        "The Last Kodo": [
            mk("Hide of the Last Herd", "chest", "of the Bear", 30,
               "Still smells of red dust, four winters on.", armor_type="leather"),
            mk("Seam-Walker's Girdle", "waist", "of the Wolf", 30,
               "He crossed the line going the wrong way and never worked out how to cross back.",
               armor_type="mail"),
            mk("Dust-Caked Hoofguards", "feet", "of the Bear", 30,
               "Barrens clay in the seams. Nothing up here makes clay like that.", armor_type="plate"),
            mk("Stranded Totem", "neck", "of the Owl", 30,
               "Carved for a herd that is three hundred miles away and might as well be on the moon."),
        ],
        "Goldcrown": [
            mk("Goldcrown's Antler", "main_hand", "of the Owl", 31,
               "Shed, found, and worth more than the stag ever was.", weapon_type="mace_1h"),
            mk("Pale Bark Leggings", "legs", "of the Monkey", 31,
               "Aspen bark takes a scar and keeps it. So do these.", armor_type="leather"),
            mk("Stand-Watcher's Longbow", "ranged", "of the Monkey", 31,
               "Drawn in a stand where you can see forty yards and hear four hundred.", weapon_type="bow"),
            mk("Gilded Canopy Mantle", "shoulder", "of the Physician", 31,
               "The light comes through these trees sideways, and gold, and only in the afternoon.",
               armor_type="cloth"),
        ],
        "Bristlehide the Wintered": [
            mk("Bristlehide's Cleaver", "main_hand", "of the Bear", 33,
               "Quilboar iron, re-ground for wood instead of flesh. It does both.", weapon_type="axe_2h"),
            mk("Wintered Tusk Pauldrons", "shoulder", "of the Bear", 33,
               "He grew the tusks in a desert and broke them on a mountain.", armor_type="plate"),
            mk("Dencarver's Hand-Axe", "off_hand", "of the Tiger", 33,
               "They dig in now. Nobody taught them to; the cold did.", weapon_type="axe_1h"),
            mk("Frost-Bitten Bracers", "wrist", "of the Monkey", 33,
               "The hide under them never did grow back right.", armor_type="mail"),
        ],
    }


def ice_pools():
    """The cave. Rimehowl is the best drop in the zone and the only reason to walk to the Sink."""
    return {
        "Rimehowl": [
            mk("Rimehowl's Frozen Maul", "main_hand", "of the Bear", 34,
               "He did not make it and he did not need to. Something else brought it across.",
               weapon_type="mace_2h"),
            mk("Pelt of the Last Winter", "chest", "of the Tiger", 34,
               "Grown for a cold that does not exist on this continent.", armor_type="leather"),
            mk("Glacier-Born Helm", "head", "of the Bear", 34,
               "Ice this old is blue, and blue all the way through.", armor_type="plate"),
            mk("Icemelt Focus", "off_hand", "of the Owl", 34,
               "It weeps steadily and has not got any smaller. Nobody can say why.",
               weapon_type="wand"),
        ],
        "Snowmaw": [
            mk("Snowmaw's Claw", "main_hand", "of the Tiger", 32,
               "She denned here when it was only a cave, and she was here first.",
               weapon_type="fist_weapon"),
            mk("Denmother's Hide Vest", "chest", "of the Bear", 32,
               "Warm enough for a mountain she was not born on.", armor_type="leather"),
            mk("Meltwater Waders", "feet", "of the Eagle", 32,
               "The cistern is ankle-deep and it is never going to drain.", armor_type="mail"),
            mk("Bear-Tooth Pendant", "neck", "of the Physician", 32,
               "One tooth, drilled through, on a cord somebody else tied."),
        ],
        "The Last Drift": [
            mk("The Last Drift's Shard", "main_hand", "of the Owl", 32,
               "He is the oldest of them and the only one who remembers the ice before it started going.",
               weapon_type="dagger"),
            mk("Drift-Watcher's Cowl", "head", "of the Owl", 32,
               "He sits where the melt has not reached and watches it come.", armor_type="cloth"),
            mk("Old Ice Vambraces", "wrist", "of the Eagle", 32,
               "Rime that has set hard enough to take a blow.", armor_type="plate"),
            mk("Yeti-Hair Cloak", "back", "of the Monkey", 32,
               "Shed in handfuls now. It did not used to come out at all.", armor_type="leather"),
        ],
    }


def main():
    cp = ROOT / "data/creatures/creatures.json"
    cdata = json.loads(cp.read_text())
    ep = ROOT / "data/creatures/encounters.json"
    edata = json.loads(ep.read_text())

    for group in (ASPEN_CREATURES, ICE_CREATURES):
        cdata["creatures"].update(group)

    z = edata["zones"].setdefault("The Aspen Wilderness", {})
    z["open_zone"] = ASPEN_ZONE["open_zone"]
    z["subzones"] = ASPEN_ZONE["subzones"]
    z["caves"] = ASPEN_ZONE["caves"]

    out = {"_notes": "Aspen Wilderness / Weeping Ice boss and named-rare loot (2026-10-27). ONE item "
                     "drops per kill from the pool. item_level = creature level + 3; real loot formulas "
                     "(tools/build_durotar_content.make). Checked by tools/qa_aspen_content.py."}
    for f in (aspen_pools, ice_pools):
        out.update(f())
    (ROOT / "data/loot/aspen_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")

    n_c = sum(len(g) for g in (ASPEN_CREATURES, ICE_CREATURES))
    n_i = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"Aspen: creatures +{n_c}, loot pools {len(out) - 1}, items {n_i}")
    cp.write_text(json.dumps(cdata, indent=2) + "\n")
    ep.write_text(json.dumps(edata, indent=2) + "\n")


if __name__ == "__main__":
    main()
