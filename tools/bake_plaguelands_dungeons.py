"""
Bake Scholomance's two floors, Stratholme's three and Hearthglen's two.

    PYTHONPATH=. python3 tools/bake_plaguelands_dungeons.py [upper lower live service slaughter town keep] [--preview DIR]

The floors and walls are Kyle's Plaguelands dungeon ground sheet (assets/tiles/plaguelands/dungeon_ground, 16 Nov
2026): Scholomance's flagstones, marble, crypt and ossuary stone and its own wall; Stratholme's market cobble, charred
wood, ash and burned cobble, its Scourge street, ziggurat stone, grates and frost, and the slaughter yard; Hearthglen's
cobble, gravel, barracks boards and kennel straw, and Mardenholde's flags. Each room takes the floor it is: a shop is
charred boards, a ziggurat is ziggurat stone.

NO REPEATING MOTIFS (Kyle on the Monastery's first Cathedral: "having a repeating pattern like that looks weird"). The
sheet's patterned floors (the mosaic, the diamond square, the chapel tiles, the throne carpet, the ritual circles, the
bastion's red bars, the Baron's diamonds) tile into wallpaper over a room, so none of them is used.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M
from tools import handbuilt_scholomance as SCH
from tools import handbuilt_stratholme as STR
from tools import handbuilt_hearthglen as HG

_L = "durotar_caves/materials/"


def _dg(stem):
    """A seamless copy of one of Kyle's dungeon ground tiles: the sheet's cells carry a thin dark rim that tiles into a
    grid, so the rim is cropped and the edges blended once (saved beside the other shared interior materials)."""
    import numpy as np
    from PIL import Image
    from tools.bake_ashenvale import _seamless
    out = f"{_L}{stem}_dgsl"
    fn = BD.TEX / (out + ".png")
    if not fn.exists():
        im = Image.open(BD.TEX / f"plaguelands/dungeon_ground/{stem}.png").convert("RGB")
        w, h = im.size
        im = im.crop((8, 8, w - 8, h - 8)).resize((w, h), Image.LANCZOS)
        a = _seamless(np.asarray(im, np.float32) / 255.0)
        fn.parent.mkdir(parents=True, exist_ok=True)
        Image.fromarray(np.clip(a * 255, 0, 255).astype(np.uint8)).save(fn)
    return out


def _box(r):
    """(x0, y0, x1, y1) of a room in either module's form."""
    if r[0] == "rect":
        return r[1], r[2], r[3], r[4]
    if r[0] == "lobes" or isinstance(r[0], list):
        lobes = r[1] if r[0] == "lobes" else r[0]
        return (min(cx - rx for cx, _cy, rx, _ry in lobes), min(cy - ry for _cx, cy, _rx, ry in lobes),
                max(cx + rx for cx, _cy, rx, _ry in lobes), max(cy + ry for _cx, cy, _rx, ry in lobes))
    return r[0], r[1], r[2], r[3]


def _fill(x0, y0, x1, y1, step=4):
    """Overlapping blobs that cover a room wall to wall."""
    return [(x, y, step * 1.1, step * 1.1) for y in range(y0, y1 + 1, step) for x in range(x0, x1 + 1, step)]


def rooms(floor_spec, *names):
    out = []
    for n in names:
        out += _fill(*_box(floor_spec["rooms"][n]))
    return out


_CFG = dict(ao=0.46, depth=0.90, lip=12, lip_col=(0.55, 0.50, 0.48), deep_dark=0.50, foam_col=(170, 165, 160),
            glows=[])
SU, SL = SCH.FLOOR[SCH.UPPER], SCH.FLOOR[SCH.LOWER]
LV, D1, D2 = STR.FLOOR[STR.LIVE], STR.FLOOR[STR.DEAD_1], STR.FLOOR[STR.DEAD_2]
HT, HK = HG.FLOOR[HG.TOWN], HG.FLOOR[HG.KEEP]

SPECS = {
    "upper": dict(
        build="build_upper_baked", seed=921, slug="scholo_upper", wall_tile="wall",
        materials={"floor": M(_dg("scholo_flag")), "crypt": M(_dg("scholo_crypt")),
                   "ossuary": M(_dg("scholo_ossuary")), "marble": M(_dg("scholo_marble")),
                   "wall": M(_dg("scholo_wall"))},
        floor_keys=["floor", "crypt", "ossuary", "marble"], wall_keys=["wall"],
        floors={"crypt": rooms(SU, "The Reliquary"), "ossuary": rooms(SU, "The Great Ossuary"),
                "marble": rooms(SU, "The Laboratory", "Hall of Secrets", "Chamber of Summoning")},
        walls={}, pools=[], cfg=_CFG),
    "lower": dict(
        build="build_lower_baked", seed=922, slug="scholo_lower", wall_tile="wall",
        materials={"floor": M(_dg("scholo_marble")), "crypt": M(_dg("scholo_crypt")),
                   "library": M(_dg("mh_library")), "ossuary": M(_dg("scholo_ossuary")),
                   "wall": M(_dg("scholo_wall"))},
        floor_keys=["floor", "crypt", "library", "ossuary"], wall_keys=["wall"],
        floors={"crypt": rooms(SL, "The Shadow Vault", "Vault of the Ravenian", "Barov Family Vault",
                               "Hall of the Damned"),
                "library": rooms(SL, "The Headmaster's Study"), "ossuary": rooms(SL, "The Coven")},
        walls={}, pools=[], cfg=_CFG),
    "live": dict(
        build="build_live_baked", seed=923, slug="strat_live", wall_tile="wall",
        materials={"floor": M(_dg("strat_market")), "wood": M(_dg("strat_charred_wood")),
                   "stone": M(_dg("mh_flag")), "ash": M(_dg("strat_ash")),
                   "burned": M(_dg("strat_burned_cobble")), "wall": M(_dg("strat_wall"))},
        floor_keys=["floor", "wood", "stone", "ash", "burned"], wall_keys=["wall"],
        floors={"wood": rooms(LV, "The Baker's", "The Smithy", "The Apothecary", "The Postmaster's", "The Hoard"),
                "stone": rooms(LV, "Hall of the Crimson Legion", "The Archives", "Hall of High Command"),
                "ash": rooms(LV, "Crusaders' Square"), "burned": rooms(LV, "The Main Gate")},
        walls={}, pools=[], cfg=_CFG),
    "service": dict(
        build="build_service_baked", seed=924, slug="strat_service", wall_tile="wall",
        materials={"floor": M(_dg("strat_scourge_street")), "zig": M(_dg("strat_ziggurat")),
                   "frost": M(_dg("strat_frost")), "grate": M(_dg("strat_grate")),
                   "ash": M(_dg("strat_ash")), "wall": M(_dg("strat_wall"))},
        floor_keys=["floor", "zig", "frost", "grate", "ash"], wall_keys=["wall"],
        floors={"zig": rooms(D1, "Nerub'enkan's Ziggurat", "Anastari's Ziggurat"),
                "frost": rooms(D1, "Maleki's Ziggurat"), "grate": rooms(D1, "The Portcullis"),
                "ash": rooms(D1, "The Alonsus Chapel")},
        walls={}, pools=[], cfg=_CFG),
    "slaughter": dict(
        build="build_slaughter_baked", seed=925, slug="strat_slaughter", wall_tile="wall",
        materials={"floor": M(_dg("strat_slaughter")), "hall": M(_dg("mh_burned")),
                   "grate": M(_dg("strat_grate")), "street": M(_dg("strat_scourge_street")),
                   "wall": M(_dg("strat_wall"))},
        floor_keys=["floor", "hall", "grate", "street"], wall_keys=["wall"],
        floors={"hall": rooms(D2, "The Slaughterhouse"), "grate": rooms(D2, "The Portcullis Yard"),
                "street": rooms(D2, "The West Houses", "The East Houses")},
        walls={}, pools=[], cfg=_CFG),
    "town": dict(
        build="build_town_baked", seed=926, slug="hg_town", wall_tile="wall",
        materials={"floor": M(_dg("hg_cobble")), "square": M(_dg("strat_market")), "stone": M(_dg("mh_flag")),
                   "kennel": M(_dg("mh_kennel")), "wood": M(_dg("hg_barracks")), "gravel": M(_dg("hg_gravel")),
                   "wall": M(_dg("mh_wall"))},
        floor_keys=["floor", "square", "stone", "kennel", "wood", "gravel"], wall_keys=["wall"],
        floors={"square": rooms(HT, "The Town Square"), "stone": rooms(HT, "The Chapel of the Flame"),
                "kennel": rooms(HT, "The Kennels"), "wood": rooms(HT, "The Infirmary", "The Barbican"),
                "gravel": rooms(HT, "The Hearthglen Gate")},
        walls={}, pools=[], cfg=_CFG),
    "keep": dict(
        build="build_keep_baked", seed=927, slug="hg_keep", wall_tile="wall",
        materials={"floor": M(_dg("mh_flag")), "yard": M(_dg("hg_gravel")), "ash": M(_dg("strat_ash")),
                   "wood": M(_dg("hg_barracks")), "cobble": M(_dg("hg_cobble")), "wall": M(_dg("mh_wall"))},
        floor_keys=["floor", "yard", "ash", "wood", "cobble"], wall_keys=["wall"],
        floors={"yard": rooms(HK, "The Muster Yard"), "ash": rooms(HK, "The Armoury", "The Barracks"),
                "wood": rooms(HK, "The Great Hall"), "cobble": rooms(HK, "The Tower Top")},
        walls={}, pools=[], cfg=_CFG),
}
FLOOR_OF = {"upper": SCH.UPPER, "lower": SCH.LOWER, "live": STR.LIVE, "service": STR.DEAD_1,
            "slaughter": STR.DEAD_2, "town": HG.TOWN, "keep": HG.KEEP}
BAKED = {**SCH.BAKED, **STR.BAKED, **HG.BAKED}


class _Shim:
    def __init__(self, build_name, baked):
        self.BAKED = baked
        fns = {"build_upper_baked": SCH.build_upper_baked, "build_lower_baked": SCH.build_lower_baked,
               "build_live_baked": lambda: STR.build_baked(STR.LIVE),
               "build_service_baked": lambda: STR.build_baked(STR.DEAD_1),
               "build_slaughter_baked": lambda: STR.build_baked(STR.DEAD_2),
               "build_town_baked": lambda: HG.build_baked(HG.TOWN), "build_keep_baked": lambda: HG.build_baked(HG.KEEP)}
        setattr(self, build_name, fns[build_name])


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    keys = [a for a in sys.argv[1:] if a in SPECS] or list(SPECS)
    for key in keys:
        spec = SPECS[key]
        BD.SPECS = {key: spec}
        BD.C = _Shim(spec["build"], BAKED[FLOOR_OF[key]])
        BD.bake_spec(key, preview=pv)
