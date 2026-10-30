"""
Bake the Return Voyage: our own deck, the two Bloodsail ships, and the anchorage.

    PYTHONPATH=. python3 tools/bake_return_voyage.py [zone ...] [--preview DIR]

WHY THESE WERE NOT BAKED, AND WHY THEY ARE NOW. Kyle: "so bro im a bit confused why we get sexy
baked pictures for things but not for the ships lol" - and he is right to ask. A baked zone is
painted from real textures; an unbaked one renders from flat tile colours, which is why Rocky Pass
looks like a mountain and The Crossing looked like a brown lozenge with a dark edge on it.

The reason was a wrong assumption of mine rather than a missing asset. The Return Voyage design
note says the ships use `path`/`dirt`/`stone` because "planks is a bake-time material, not a tile
id" and lists four ship ground tiles as outstanding art. All true, and it does not follow that
nothing could be baked: stv_planks, sp_pier_planks, sp_wood_planks and tf_rotten_planks have been
in the tree the whole time, and the Stranglethorn set has the beach and the ocean this crossing
actually sails through. Four BESPOKE tiles were missing; four USABLE ones were not.

THE SEA IS THE WALL, so it is painted as one. These zones are built with wall_id="tropical_water",
which means every blocked tile is open water, and the baker's wall pass is exactly the right place
to put the ocean texture. It also means the baker's wall shading does the gunwale for free: the
darkening INTO the wall from the deck edge reads as the shadow under a ship's side.

depth is 0.34 - lower than a cave, higher than Rocky Pass. A hull has a real bulwark casting a real
shadow, which a mountainside does not, but there is still sky overhead.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_return_voyage as RV
from tools import handbuilt_bloodsail_raider as R
from tools import handbuilt_bloodsail_galleon as G
from tools.bake_durotar_caves import M, dim

STV = "stranglethorn/materials/"
SP = "silverpine/materials/"
TF = "tirisfal/materials/"

#: Shared by every zone that is a ship. The deck is the base; the pale raised decks and the dark
#: hatches are regions laid over it.
DECK_MATS = {
    "deck":   M(STV + "stv_planks", SP + "sp_wood_planks"),
    "scrub":  M(SP + "sp_pier_planks", STV + "stv_planks"),   # holystoned fore and aft
    "hatch":  M(dim(TF + "tf_rotten_planks", 0.8)),           # a hole down to the deck below
    "worn":   M(TF + "tf_rotten_planks", SP + "sp_wood_planks"),
    # TROPICAL, which took measuring rather than looking. stv_ocean is (5, 57, 110) - North
    # Atlantic navy - and mixing it into the base sea dragged the whole crossing dark even though
    # stv_sea_d on its own is (5, 142, 191). Kyle asked for tropical water and the texture for it
    # was already there; it was being averaged away.
    "sea_d":  M(STV + "stv_sea_d", STV + "stv_sea_s"),
    "sea_s":  M(STV + "stv_sea_s"),
}
# depth and deep_dark are both LOW for a reason particular to these maps: the baker darkens into
# the wall, and here the wall is the open sea, which is most of the picture. At cave values the
# crossing came out as a deck floating in ink. 0.22 still gives the gunwale its shadow.
DECK_CFG = dict(ao=0.26, depth=0.22, lip=14, lip_col=(0.80, 0.95, 0.96), deep_dark=0.10,
                foam_col=(228, 242, 244), glows=[])


def ship(build, seed, slug, scrub, hatch, worn, shallow, sand=()):
    """A ship: planks everywhere, pale raised decks, dark hatches, sea for walls.

    `sand` is for The Crossing's sand bar, which is walkable ground that is NOT deck - without it
    the base floor key paints the whole zone in planks and the island comes out as more ship."""
    """A ship: planks everywhere, pale raised decks, dark hatches, sea for walls."""
    mats = dict(DECK_MATS)
    mats["sand"] = M(STV + "stv_beach", STV + "stv_coral_sand")
    return dict(
        build=build, seed=seed, slug=slug, wall_tile="tropical_water",
        materials=mats,
        floor_keys=["deck", "scrub", "hatch", "worn", "sand"],
        wall_keys=["sea_d", "sea_s"],
        floors={"scrub": scrub, "hatch": hatch, "worn": worn, "sand": list(sand)},
        walls={"sea_s": shallow},
        pools=[],
        cfg=dict(DECK_CFG),
    )


SPECS = {
    # Our own deck. The forecastle and quarterdeck are scrubbed pale, the waist is working deck,
    # and the sea shallows round the sand bar to the south.
    "crossing": lambda: ship(
        "build_crossing_baked", 211, "crossing",
        scrub=[(29, 50, 10, 8), (93, 50, 10, 9)],
        hatch=[(59, 50, 5, 4)],
        worn=[(58, 32, 4, 7), (56, 68, 4, 8)],          # the two planks, walked to death
        shallow=[(58, 78, 18, 14), (70, 80, 14, 10)],
        sand=[(58, 78, 11, 9), (70, 80, 9, 7)],         # the sand bar is not more ship
    ),
    "raider_deck": lambda: ship(
        "build_raider_deck_baked", 212, "raider_deck",
        scrub=[(22, 35, 9, 7), (89, 35, 8, 9)],
        hatch=[(54, 35, 5, 6)],
        worn=[(64, 35, 4, 4), (24, 35, 4, 4)],          # the two barricades
        shallow=[],
    ),
    "raider_hold": lambda: ship(
        "build_raider_hold_baked", 213, "raider_hold",
        scrub=[(89, 35, 8, 8)],                          # the cabin, a made room
        hatch=[(18, 35, 5, 5)],
        worn=[(50, 35, 10, 8)],
        shallow=[],
    ),
    "galleon_deck": lambda: ship(
        "build_galleon_deck_baked", 214, "galleon_deck",
        scrub=[(26, 40, 11, 9), (106, 40, 11, 11)],
        hatch=[(63, 40, 6, 6), (25, 40, 6, 5)],
        worn=[(44, 40, 4, 5)],
        shallow=[],
    ),
    "galleon_hold": lambda: ship(
        "build_galleon_hold_baked", 215, "galleon_hold",
        scrub=[(109, 40, 7, 9)],
        hatch=[(24, 40, 5, 5)],
        worn=[(58, 40, 12, 9)],
        shallow=[],
    ),
    "cabin": lambda: ship(
        "build_cabin_baked", 216, "cabin",
        scrub=[(30, 16, 15, 5)],                         # the stern gallery, under the windows
        hatch=[],
        worn=[(30, 28, 18, 2)],                          # the screen bulkhead's doorway
        shallow=[],
    ),
    # THE ANCHORAGE IS NOT A SHIP. Sand, the pools the route weaves between, and the sea round it.
    "anchorage": lambda: dict(
        build="build_anchorage_baked", seed=217, slug="anchorage",
        wall_tile="tropical_water",
        materials={
            "beach":  M(STV + "stv_beach", STV + "stv_coral_sand"),
            "wet":    M(STV + "stv_wet", STV + "stv_beach"),
            "shell":  M(STV + "stv_coral_sand", STV + "stv_arena_sand"),
            "rock":   M(STV + "stv_rocky", STV + "stv_clay"),
            "sea_d":  M(STV + "stv_sea_d", STV + "stv_ocean"),
            "sea_s":  M(STV + "stv_sea_s", STV + "stv_wet"),
        },
        floor_keys=["beach", "wet", "shell", "rock"],
        wall_keys=["sea_d", "sea_s"],
        floors={
            # damp sand round every pool, dry shelly sand up the middle of the horns, and rock
            # where the headland shows through
            # +2, not +5: at +5 the damp ring round every pool met the damp ring round the next
            # one and the whole bar came out wet, which on a baked map reads as a washed-out
            # beach rather than as a tide line.
            "wet": [(cx, cy, rx + 2, ry + 2) for (cx, cy, rx, ry) in G.COVE_POOLS],
            "shell": [(42, 90, 14, 12), (62, 78, 14, 12), (54, 106, 16, 10), (48, 40, 14, 10)],
            "rock": [(76, 82, 10, 8), (28, 88, 10, 8), (32, 66, 8, 7), (72, 46, 8, 7)],
        },
        # the pools themselves are blocked tiles, so they are painted by the WALL pass
        walls={"sea_s": [(cx, cy, rx + 1, ry + 1) for (cx, cy, rx, ry) in G.COVE_POOLS]},
        pools=[],
        # lip 8, not 16: the foam line is the surf, and 16 tiles of it reaches halfway
        # across a sand bar this narrow.
        cfg=dict(ao=0.24, depth=0.22, lip=8, lip_col=(0.84, 0.96, 0.94), deep_dark=0.10,
                 foam_col=(232, 246, 244), glows=[]),
    ),
}

MODULES = {"crossing": RV, "raider_deck": R, "raider_hold": R, "galleon_deck": G,
           "galleon_hold": G, "cabin": G, "anchorage": G}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
