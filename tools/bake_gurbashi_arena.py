"""
Bake the Gurbashi Arena painting.

    python3 tools/bake_gurbashi_arena.py [--preview DIR]

Same pipeline as tools/bake_echo_caves.py: the Durotar cave baker
(tools/bake_durotar_caves.bake_spec) pointed at this dungeon's own layout
(tools/handbuilt_gurbashi_arena) and material spec.

RETARGETED 30 OCT for the octagon.  The blobs below used to be keyed to the five-chamber line that
ran down the middle of an 80x140 map; against the 104x104 ring they would have painted the grate into
solid rock.  They now follow the ring round, station by station, and the only part of the arena that
gets a laid floor is the hall in the middle - the house's own floor, behind the wall, which nobody
stands on until the ring is empty.

NO NEW TEXTURES.  Every material already ships, and they are Stranglethorn's own set, NOT Durotar's.
The Durotar cave materials are red desert rock and against this dungeon's warm lip light the whole
arena came out glowing orange like a lava tube; the Gurbashi run a sand pit under a jungle crag, not
a volcano.  The two exceptions are deliberate and are not desert textures: the Burning Blade floor
grate under seven o'clock, and basalt for the walls either side of it.

    the ring .............. arena sand, raked between bouts.  The default floor, so anything not
                            called out below is sand.
    The Sand Gate ......... laid stone, same as the hall.  The stair and the gate are the only built
                            parts of the approach and the only parts anyone maintains.
    The Hot Grate ......... the Burning Blade grate over basalt walls.  There is a fire under this
                            stretch of floor and the stoker's whole job is keeping it there.
    The Pairing ........... bone-shot sand.  Nobody rakes this one; two fighters at once leaves more
                            behind than one crew clears between rounds.
    The Hard Round ........ hardpan.  The dead end, beaten flat by however many years of this.
    the alcoves ........... hardpan too, because that is where the crowd stands.
    The House Floor ....... laid stone inside the wall band, and the band itself is painted as ruin
                            masonry rather than crag: it is the one wall in here somebody BUILT.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_gurbashi_arena as GA
from tools.bake_durotar_caves import M, dim, CS, VC

SP = "stranglethorn/materials/"

SPECS = {
    GA.SLUG: dict(
        build="build_arena", seed=211, slug=GA.SLUG,
        materials={
            # Repointed at Stranglethorn's own tiles once Sheet F landed (29 Oct); kept there on the
            # 30 Oct rebuild. The Durotar cave set is RED DESERT ROCK - do not point these back at it.
            "sand":    M(SP + "stv_arena_sand"),
            "stone":   M(SP + "stv_plaza"),
            "grate":   M(VC + "bbc_floor_grate"),
            "bone":    M(SP + "stv_beach", dim(SP + "stv_beach", 0.90)),
            "hardpan": M(SP + "stv_trampled"),
            "wall":    M(SP + "stv_cliff_b"),
            "cliff":   M(SP + "stv_cliff_a"),
            "basalt":  M(CS + "rf_basalt_wall_a"),
            "masonry": M(SP + "stv_ruin"),
        },
        floor_keys=["sand", "stone", "grate", "bone", "hardpan"],
        wall_keys=["wall", "cliff", "basalt", "masonry"],
        floors={
            # the hall inside the wall band, and the stair hall at twelve o'clock
            "stone":   [(52, 56, 17, 17), (52, 15, 9, 13)],
            # seven o'clock, and only the sand the stoker works - the benches behind it are not on fire
            "grate":   [(37, 82, 11, 10)],
            # five o'clock
            "bone":    [(67, 82, 11, 10)],
            # the three o'clock dead end, plus all four crowd alcoves
            "hardpan": [(75, 56, 12, 11), (17, 36, 10, 8), (32, 90, 10, 8),
                        (72, 90, 10, 8), (92, 56, 10, 8)],
        },
        walls={
            # the outer crag behind the rim, cut away to make room for the benches
            "cliff":  [(17, 36, 16, 13), (32, 90, 16, 13), (72, 90, 16, 13), (92, 56, 16, 13)],
            # the two stretches with a fire under them
            "basalt": [(37, 82, 15, 14), (67, 82, 15, 14)],
            # the wall band itself, radius 15 out to 24. Overspilling the hall's own floor is free -
            # a wall score only ever lands on a wall tile.
            "masonry": [(52, 56, 26, 26)],
        },
        pools=[],
        cfg=dict(ao=0.46, depth=0.78, lip=18, lip_col=(0.92, 0.90, 0.82), deep_dark=0.3,
                 foam_col=(205, 225, 225), glows=[]),
    ),
}

BD.C = GA
BD.SPECS = SPECS

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    for k in (args or list(SPECS)):
        BD.bake_spec(k, pv)
