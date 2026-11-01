"""
Bake the seven Arathi interiors: five caves and two dungeons.

    PYTHONPATH=. python3 tools/bake_arathi_caves.py [key ...] [--preview DIR]

NO NEW TEXTURES. Everything here paints from assets/tiles/durotar_caves/materials, which is the shared
interior library the whole game draws on - 60-odd pre-dimmed floors, walls, waters and decks. Seven new
interiors shipping with seven new texture sets would be seven more things to keep in step, and the
library already has the right surface for each of these.

What differs between them is the PAIRING, and the pairings are chosen to say what each place is:

  Boulder'gor        den floor + rock wall, nest matting in the dens. A lived-in hole.
  Boulderfist Hall   the same, so the two ogre holds read as one people - the SHAPES are what tell
                     them apart (dumbbell vs hub-and-spokes), not the stone.
  The Drowned Barrow mausoleum marble and crypt wall at the top, wet limestone and standing water at
                     the bottom. The material changes as you descend, which is the whole zone's idea.
  Wrackline Hold     grotto floor, deck planking on the shelves, sand at the tideline. Built-on rock.
  The Tidewrack      sand and pearl floor, open water in the sump. Nothing built at all.
  Stromgarde Keep    temple flagstones and dressed stone wall - the ONLY masonry interior in Arathi -
                     with mausoleum marble in the undercroft, because that part predates the keep.
  Drywhisker Deeps   gravel and rock, going to wet limestone and water in the sump, because a mine
                     floor is spoil and a mine fills from underneath.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M

from tools import handbuilt_arathi_caves as CV
from tools import handbuilt_stromgarde_keep as STRO
from tools import handbuilt_drywhisker_deeps as DRY

#: Shared library names (already dimmed for interiors). TEX root is assets/tiles, so every name is
#: prefixed with the folder - bake_durotar_caves.M takes a path relative to assets/tiles, not a bare
#: material name.
_L = "durotar_caves/materials/"
ROCK_W = _L + "ud_rock_wall_dim80"
DEN_F = _L + "den_floor_a_dim70"
NEST_F = _L + "den_floor_nest_dim90"
DAMP_F = _L + "den_floor_damp_dim75"
WET_F = _L + "cen_limestone_wet_dim78"
MARBLE = _L + "tf_mausoleum_marble_dim85"
CRYPT_W = _L + "tf_crypt_wall_dim55"
STONE_W = _L + "tf_stone_wall_dim60"
TEMPLE_F = _L + "bfd_temple_floor_a_dim72"
GRO_F = _L + "gro_cave_floor_a_dim80"
GRO_DECK = _L + "gro_deck_a_dim85"
GRO_SAND = _L + "gro_sand_a_dim60"
PEARL_F = _L + "gro_pearl_floor_a_dim60"
GRAVEL_F = _L + "vot_gravel_dim62"
WATER_S = _L + "cen_water_shallow_dim78"
WATER_D = _L + "cen_water_deep_dim70"


def _rooms(spec, *keys):
    """Ellipse hints (cx, cy, rx, ry) for the named rooms of an Arathi cave spec."""
    out = []
    for k in keys:
        lobes = spec["ROOMS"][k][0]
        for (cx, cy, rx, ry, _rot, _ph) in lobes:
            out.append((cx, cy, rx * 1.3, ry * 1.3))
    return out


def spec_bouldergor():
    s = CV.BOULDERGOR
    return dict(
        build="_baked_bouldergor", seed=401, slug="bouldergor",
        materials={"floor": M(DEN_F), "nest_f": M(NEST_F), "wall": M(ROCK_W)},
        floor_keys=["floor", "nest_f"], wall_keys=["wall"],
        floors={"nest_f": _rooms(s, "lower", "upper")},
        walls={}, pools=[],
        cfg=dict(ao=0.47, depth=0.85, lip=20, lip_col=(0.78, 0.66, 0.50), deep_dark=0.4,
                 foam_col=(210, 205, 190), glows=[]),
    )


def spec_boulderfist():
    s = CV.BOULDERFIST
    return dict(
        build="_baked_boulderfist", seed=402, slug="boulderfist",
        materials={"floor": M(DEN_F), "nest_f": M(NEST_F), "wall": M(ROCK_W)},
        floor_keys=["floor", "nest_f"], wall_keys=["wall"],
        floors={"nest_f": _rooms(s, "hall", "north", "east")},
        walls={}, pools=[],
        cfg=dict(ao=0.47, depth=0.85, lip=20, lip_col=(0.78, 0.66, 0.50), deep_dark=0.4,
                 foam_col=(210, 205, 190), glows=[]),
    )


def spec_barrow():
    s = CV.BARROW
    # The DESCENT is painted, not just described: marble at the mouth end, wet limestone and standing
    # water at the head. That is the one thing this cave is about.
    return dict(
        build="_baked_barrow", seed=403, slug="barrow",
        materials={"floor": M(MARBLE), "wet_f": M(WET_F), "wall": M(CRYPT_W)},
        floor_keys=["floor", "wet_f"], wall_keys=["wall"],
        floors={"wet_f": _rooms(s, "n_e", "n_f", "head") + [(28, 18, 10, 10)]},
        walls={},
        # pools is a list of GROUPS, each a list of (cx, cy, rx, ry, phase) - bake_spec flattens
        # one level. Passing the tuples directly gets them unpacked as ints.
        pools=[[(28, 8, 12, 6, 0.5), (28, 16, 8, 4, 1.4)]],
        cfg=dict(ao=0.50, depth=0.88, lip=18, lip_col=(0.72, 0.72, 0.70), deep_dark=0.45,
                 foam_col=(190, 200, 205), glows=[]),
    )


def spec_wrackline():
    s = CV.WRACKLINE
    return dict(
        build="_baked_wrackline", seed=404, slug="wrackline",
        materials={"floor": M(GRO_F), "sand_f": M(GRO_SAND), "deck_f": M(GRO_DECK), "wall": M(ROCK_W)},
        floor_keys=["floor", "sand_f", "deck_f"], wall_keys=["wall"],
        floors={"sand_f": _rooms(s, "dock"), "deck_f": _rooms(s, "cargo", "crew")},
        walls={},
        pools=[[(22, 45, 12, 3, 0.7)]],
        cfg=dict(ao=0.46, depth=0.86, lip=20, lip_col=(0.70, 0.74, 0.76), deep_dark=0.42,
                 foam_col=(215, 225, 230), glows=[]),
    )


def spec_tidewrack():
    s = CV.TIDEWRACK
    return dict(
        build="_baked_tidewrack", seed=405, slug="tidewrack",
        materials={"floor": M(GRO_SAND), "pearl_f": M(PEARL_F), "wall": M(ROCK_W)},
        floor_keys=["floor", "pearl_f"], wall_keys=["wall"],
        floors={"pearl_f": _rooms(s, "sump")},
        walls={},
        pools=[[(32, 27, 7, 7, 1.1)]],
        cfg=dict(ao=0.45, depth=0.86, lip=20, lip_col=(0.68, 0.74, 0.78), deep_dark=0.44,
                 foam_col=(220, 230, 235), glows=[]),
    )


def spec_stromgarde():
    R = STRO.ROOMS
    def rect(key, pad=2):
        x0, y0, x1, y1, _c, _n = R[key]
        return ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0 + pad, (y1 - y0) / 2.0 + pad)
    return dict(
        build="build_stromgarde_baked", seed=406, slug="stromgarde_keep",
        materials={"floor": M(TEMPLE_F), "marble_f": M(MARBLE), "wall": M(STONE_W)},
        floor_keys=["floor", "marble_f"], wall_keys=["wall"],
        # the undercroft and the chapel: older stone than the keep above them
        floors={"marble_f": [(16, 120, 18, 12), (6, 130, 9, 8), (28, 131, 9, 8), rect("chapel")]},
        walls={}, pools=[],
        cfg=dict(ao=0.42, depth=0.80, lip=16, lip_col=(0.76, 0.74, 0.68), deep_dark=0.38,
                 foam_col=(200, 200, 200), glows=[]),
    )


def spec_drywhisker():
    G = DRY.GALLERIES
    def gal(key, pad=3):
        lobes = G[key][0]
        x0 = min(cx - rx for (cx, cy, rx, ry, _r, _p) in lobes) - pad
        x1 = max(cx + rx for (cx, cy, rx, ry, _r, _p) in lobes) + pad
        y0 = min(cy - ry for (cx, cy, rx, ry, _r, _p) in lobes) - pad
        y1 = max(cy + ry for (cx, cy, rx, ry, _r, _p) in lobes) + pad
        return ((x0 + x1) / 2.0, (y0 + y1) / 2.0, (x1 - x0) / 2.0, (y1 - y0) / 2.0)
    return dict(
        build="build_drywhisker_baked", seed=407, slug="drywhisker_deeps",
        materials={"floor": M(GRAVEL_F), "wet_f": M(WET_F), "wall": M(ROCK_W)},
        floor_keys=["floor", "wet_f"], wall_keys=["wall"],
        # a mine fills from underneath: the bottom two levels are wet, the top two are spoil
        floors={"wet_f": [gal("sump"), gal("g3", pad=0)]},
        walls={},
        pools=[[(70, 24, 20, 6, 0.9), (40, 30, 8, 4, 2.0)]],
        cfg=dict(ao=0.50, depth=0.88, lip=18, lip_col=(0.74, 0.68, 0.56), deep_dark=0.46,
                 foam_col=(195, 205, 205), glows=[]),
    )


# The cave module builds all five from one entry point, so give the baker a per-cave shim with the
# name its spec asks for - bake_spec resolves spec["build"] off ONE module and these five live
# together in handbuilt_arathi_caves.
def _mk(name, spec, dresser):
    def _f():
        return CV._build(name, spec, dresser, baked=False)
    return _f


CV._baked_bouldergor = _mk("Boulder'gor", CV.BOULDERGOR, CV._dress_bouldergor)
CV._baked_boulderfist = _mk("Boulderfist Hall", CV.BOULDERFIST, CV._dress_boulderfist)
CV._baked_barrow = _mk("The Drowned Barrow", CV.BARROW, CV._dress_barrow)
CV._baked_wrackline = _mk("Wrackline Hold", CV.WRACKLINE, CV._dress_wrackline)
CV._baked_tidewrack = _mk("The Tidewrack", CV.TIDEWRACK, CV._dress_tidewrack)

SPECS = {
    "bouldergor": (spec_bouldergor, CV, CV.BOULDERGOR["BAKED"]),
    "boulderfist": (spec_boulderfist, CV, CV.BOULDERFIST["BAKED"]),
    "barrow": (spec_barrow, CV, CV.BARROW["BAKED"]),
    "wrackline": (spec_wrackline, CV, CV.WRACKLINE["BAKED"]),
    "tidewrack": (spec_tidewrack, CV, CV.TIDEWRACK["BAKED"]),
    "stromgarde": (spec_stromgarde, STRO, STRO.BAKED),
    "drywhisker": (spec_drywhisker, DRY, DRY.BAKED),
}


class _Shim:
    """What bake_spec needs off a module: the build function it names, and a BAKED path.

    bake_spec resolves spec["build"] off the single module bake_durotar_caves.C and writes to
    C.BAKED.format(slug). These seven interiors live in three different modules and each has its own
    literal output path, so each gets a one-attribute shim rather than three modules being bent to fit
    one baker's assumption. format() on a string with no braces returns the string.
    """

    def __init__(self, module, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(module, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for k in keys:
        make, module, baked = SPECS[k]
        spec = make()
        BD.SPECS = {k: spec}
        BD.C = _Shim(module, spec["build"], baked)
        BD.bake_spec(k, preview=(f"{pv}/{k}.png" if pv else None))
