"""
Bake the Scarlet Monastery's grounds and four wings.

    PYTHONPATH=. python3 tools/bake_scarlet_monastery.py [grounds|graveyard|library|armory|cathedral ...] [--preview DIR]

NO NEW ART: the floors are seamless copies of Kyle's Plaguelands ground sheet (assets/tiles/plaguelands/ground) and the walls are the
shared interior library's keep and crypt stone (Shadowfang Keep's and Tirisfal's), so the Monastery reads as one
building with four moods: the Graveyard's moss and cracked slabs, the Library's runners between the stacks, the
Armory's yard and keep floor, the Cathedral's worn paving and pale chancel.

NO REPEATING MOTIFS. Kyle, 16 Nov 2026, on the first Cathedral: "Avoid tiles where they look like that in
cathedral... having a repeating pattern like that looks weird". The monastery floor (a flame emblem in every square),
the Scarlet flagstones (a diamond grid) and the cathedral runner (stripes) tile into wallpaper over a room this size,
so the floors here are stone and paving with no single feature the eye can count.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M

from tools import handbuilt_scarlet_monastery as SM

_L = "durotar_caves/materials/"
_TF = "tirisfal/materials/"          # already seamless


def _sl(stem):
    """A seamless copy of a Plaguelands ground tile. Kyle's sheet tiles carry a dark rim along their top and bottom
    edges, which tiles into a stripe every few metres; this crops the rim and blends the edges (generated once,
    committed, beside the other shared interior materials)."""
    import numpy as np
    from PIL import Image
    from tools.bake_ashenvale import _seamless
    out = f"{_L}{stem}_sl"
    fn = BD.TEX / (out + ".png")
    if not fn.exists():
        im = Image.open(BD.TEX / f"plaguelands/ground/{stem}.png").convert("RGB")
        w, h = im.size
        im = im.crop((10, 10, w - 10, h - 10)).resize((w, h), Image.LANCZOS)
        a = _seamless(np.asarray(im, np.float32) / 255.0)
        fn.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).save(fn)
    return out


def _rooms(wing, *names):
    rooms = SM.WING[wing]["rooms"]
    return [((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + 2, (y1 - y0) / 2 + 2)
            for n in names for (x0, y0, x1, y1, _c) in [rooms[n]]]


def _fill(x0, y0, x1, y1, step=4):
    """Overlapping blobs that cover a box edge to edge: an open-air yard is ground all the way to its walls, not an
    oval of lawn in the middle of a floor."""
    return [(x, y, step * 1.1, step * 1.1) for y in range(y0, y1 + 1, step) for x in range(x0, x1 + 1, step)]


def _open(wing, *names):
    out = []
    for n in names:
        x0, y0, x1, y1, _c = SM.WING[wing]["rooms"][n]
        out += _fill(x0, y0, x1, y1)
    return out


_CFG = dict(ao=0.42, depth=0.90, lip=12, lip_col=(0.62, 0.55, 0.50), deep_dark=0.52, foam_col=(180, 170, 160),
            glows=[])

SPECS = {
    "grounds": dict(
        build="build_grounds_baked", seed=811, slug="sm_grounds", wall_tile="wall", no_smoothing=True,
        materials={"floor": M(_sl("pl_hearthglen_cobble")), "moss": M(_sl("pl_grey_moss")),
                   "wall": M(_L + "sp_keep_wall_dim60")},
        floor_keys=["floor", "moss"], wall_keys=["wall"],
        floors={"moss": [(14, 30, 12, 16)]}, walls={}, pools=[], cfg=_CFG),
    "graveyard": dict(
        build="build_graveyard_baked", seed=812, slug="sm_graveyard", wall_tile="wall",
        materials={"floor": M(_sl("pl_mossy_flag")), "crypt": M(_sl("pl_scourge_cracked")),
                   "grass": M(_TF + "tf_dead_grass"), "gravel": M(_TF + "tf_grave_gravel"),
                   "wall": M(_L + "tf_crypt_wall_dim55")},
        floor_keys=["floor", "crypt", "grass", "gravel"], wall_keys=["wall"],
        floors={"crypt": _rooms(SM.GRAVEYARD, "The Chamber of Atonement", "Honor's Tomb"),
                "grass": _open(SM.GRAVEYARD, "The Forlorn Cloister"),
                "gravel": [(42, 27, 7, 7), (26, 27, 13, 2.2), (58, 27, 13, 2.2), (42, 40, 2.2, 8)]},
        floor_weight={"gravel": 1.7},
        walls={}, pools=[], cfg=dict(_CFG, ao=0.5, deep_dark=0.46)),
    "library": dict(
        build="build_library_baked", seed=813, slug="sm_library", wall_tile="wall",
        materials={"floor": M(_sl("pl_lightshope_stone")), "runner": M(_sl("pl_keep_floor")),
                   "grass": M(_TF + "tf_dead_grass"), "wall": M(_L + "sp_keep_wall_dim90")},
        floor_keys=["floor", "runner", "grass"], wall_keys=["wall"],
        floors={"runner": _rooms(SM.LIBRARY, "Gallery of Treasures", "The Athenaeum"),
                "grass": _fill(12, 42, 26, 54)},
        walls={}, pools=[], cfg=_CFG),
    "armory": dict(
        build="build_armory_baked", seed=814, slug="sm_armory", wall_tile="wall",
        materials={"floor": M(_sl("pl_keep_floor")), "yard": M(_sl("pl_dirt_road")),
                   "grass": M(_TF + "tf_dead_grass"), "wall": M(_L + "sp_keep_wall_dim60")},
        floor_keys=["floor", "yard", "grass"], wall_keys=["wall"],
        floors={"yard": _open(SM.ARMORY, "Training Grounds"),
                "grass": [(26, 72, 5, 3), (84, 72, 5, 3)]},
        walls={}, pools=[], cfg=_CFG),
    "cathedral": dict(
        build="build_cathedral_baked", seed=815, slug="sm_cathedral", wall_tile="wall",
        materials={"floor": M(_sl("pl_andorhal_paving")), "grass": M(_TF + "tf_dead_grass"),
                   "path": M(_TF + "tf_old_cobble"), "chancel": M(_sl("pl_lightshope_stone")),
                   "wall": M(_L + "sp_keep_wall_dim90")},
        floor_keys=["floor", "grass", "path", "chancel"], wall_keys=["wall"],
        # the gardens are grass with a cross of old cobble through them and a ring round the fountain
        floors={"grass": _open(SM.CATHEDRAL, "Chapel Gardens"),
                "path": [(60, 81, 3, 24), (60, 81, 44, 2.5), (60, 81, 9, 8)],
                "chancel": _rooms(SM.CATHEDRAL, "The Chancel")},
        floor_weight={"path": 1.7},
        walls={}, pools=[], cfg=_CFG),
}
ZONE = {"grounds": SM.GROUNDS, "graveyard": SM.GRAVEYARD, "library": SM.LIBRARY, "armory": SM.ARMORY,
        "cathedral": SM.CATHEDRAL}


class _Shim:
    def __init__(self, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(SM, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for key in keys:
        spec = SPECS[key]
        BD.SPECS = {key: spec}
        BD.C = _Shim(spec["build"], SM.BAKED[ZONE[key]])
        BD.bake_spec(key, preview=(f"{pv}/sm_{key}.png" if pv else None))
