"""
Bake the Gurbashi Arena painting.

    python3 tools/bake_gurbashi_arena.py [--preview DIR]

Same pipeline as tools/bake_echo_caves.py: the Durotar cave baker
(tools/bake_durotar_caves.bake_spec) pointed at this dungeon's own layout
(tools/handbuilt_gurbashi_arena) and material spec.

NO NEW TEXTURES.  Every material below already ships - and since 29 Oct they are Stranglethorn's
own, not Durotar's red desert rock.  The five pits are told apart by what the
Gurbashi do with each floor rather than by hue tricks:

    The Sand Gate ......... swept stone.  The only part of the place anyone maintains.
    The Opening Bout ...... raked sand.  Resurfaced between bouts, which is why it still looks new.
    The Hot Grate ......... the Burning Blade grate texture over basalt walls - there is a fire
                            under this floor and the stoker's whole job is keeping it there.
    The Pairing ........... bone-shot sand.  Nobody rakes this one; two fighters at once leaves more
                            behind than one crew can clear between rounds.
    The Hard Round ........ hardpan, beaten flat by however many years of this.
    The House Floor ....... stone again, because the house sits on it and the house gets stone.
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
            # Repointed at Stranglethorn's own tiles once Sheet F landed (29 Oct). The Durotar cave
            # set is RED DESERT ROCK, and against this dungeon's warm lip light the whole arena came
            # out glowing orange like a lava tube. The Gurbashi run a sand pit under a jungle crag,
            # not a volcano.
            "sand":    M(SP + "stv_beach", dim(SP + "stv_beach", 0.90)),
            "stone":   M(SP + "stv_ruin"),
            "grate":   M(VC + "bbc_floor_grate"),
            "bone":    M(SP + "stv_arena_sand"),
            "hardpan": M(SP + "stv_trampled"),
            "wall":    M(SP + "stv_cliff_b"),
            "cliff":   M(SP + "stv_cliff_a"),
            "basalt":  M(CS + "rf_basalt_wall_a"),
        },
        floor_keys=["sand", "stone", "grate", "bone", "hardpan"],
        wall_keys=["wall", "cliff", "basalt"],
        floors={
            "stone":   [(40, 12, 14, 9), (40, 130, 29, 10)],
            "grate":   [(40, 59, 26, 11)],
            "bone":    [(40, 84, 26, 11)],
            "hardpan": [(40, 109, 26, 11)],
        },
        walls={
            "cliff":  [(40, 34, 30, 13), (40, 109, 30, 13)],
            "basalt": [(40, 59, 30, 13), (40, 84, 30, 13)],
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
