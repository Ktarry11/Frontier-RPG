#!/usr/bin/env python3
"""
Bake The Lashings - the Southsea cove, nine hulls rafted together.

    PYTHONPATH=. python3 tools/bake_lashings.py [--preview OUT.png]

IT IS SHIPS, SO IT IS PAINTED AS SHIPS. The Return Voyage's deck palette already exists and is
already tropical - stv_planks for working deck, sp_pier_planks holystoned pale for the raised ends,
tf_rotten_planks where a deck has gone, and stv_sea_d / stv_sea_s for the water that is this map's
wall. Reaching for a cave palette here would have been the mistake: the whole premise is that these
are not rooms, they are HULLS, and the floor has to say so on every tile.

THE ONE THING THAT IS NOT THE RETURN VOYAGE'S PALETTE IS WHAT THE DIFFERENCE IS ABOUT. Those ships
are sailing. These have not sailed in twenty years, so:

  THE PLANKS ARE ROTTEN, not worn. tf_rotten_planks is the default across the lashings themselves,
  because a gangway slung between two hulls and walked for two decades in salt air is the first
  thing to go and the last thing anybody repairs.
  THE RAISED DECKS ARE NOT HOLYSTONED. Nobody has scrubbed anything here since the Southsea stopped
  being a fleet and started being a town, so the pale scrub is confined to the Flagship, which is
  the one hull Ardessa Rake still keeps like a ship. That contrast IS her characterisation, and it
  costs nothing - one entry in the floors table.

DECK CFG, NOT CAVE CFG. The baker darkens into the wall and here the wall is open water, which is
most of the picture; at cave values the whole cove comes out as decks floating in ink.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_lashings as LA
from tools.bake_durotar_caves import M, dim

MODULES = {"lashings": LA}

STV = "stranglethorn/materials/"
SP = "silverpine/materials/"
TF = "tirisfal/materials/"

SPECS = {}


def _hull(key):
    """(x, y, w, h) covering a hull, for the floors table."""
    (_k, _nm, x0, x1, ycen, beam, _bow) = LA.HULL_BY_KEY[key]
    return (x0, ycen - beam, (x1 - x0) + 1, 2 * beam + 1)


SPECS["lashings"] = lambda: dict(
    build="build_lashings_baked", seed=791, slug="lashings", wall_tile="tropical_water",
    materials={
        # working deck: what most of this fleet is
        "deck":   M(STV + "stv_planks", SP + "sp_wood_planks"),
        # the Flagship, and only the Flagship. Ardessa Rake still keeps one hull like a ship.
        "scrub":  M(SP + "sp_pier_planks", STV + "stv_planks"),
        # the lashings themselves, and the two hulls nobody maintains
        "rot":    M(TF + "tf_rotten_planks", SP + "sp_wood_planks"),
        "sea_d":  M(STV + "stv_sea_d", STV + "stv_sea_s"),
        "sea_s":  M(STV + "stv_sea_s"),
    },
    floor_keys=["deck", "scrub", "rot"],
    wall_keys=["sea_d", "sea_s"],
    floors={
        "scrub": [_hull("h5")],
        # the careenage is laid over and the cable tier is a store nobody stands in
        "rot": [_hull("h1"), _hull("l2"), _hull("l1")],
    },
    walls={},
    pools=[],
    cfg=dict(ao=0.26, depth=0.22, lip=14, lip_col=(0.80, 0.95, 0.96), deep_dark=0.10,
             foam_col=(228, 242, 244), glows=[]),
)


def main():
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    BD.SPECS = {k: SPECS[k]() for k in keys}
    for k in keys:
        BD.C = MODULES[k]
        BD.bake_spec(k, pv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
