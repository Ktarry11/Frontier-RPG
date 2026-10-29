"""
Bake the three Stranglethorn cave paintings.

    python3 tools/bake_stranglethorn_caves.py [rotvine_hollow|veilfall_cave|drowned_shrine ...]
                                              [--preview DIR]

Reuses the Durotar cave baker (tools/bake_durotar_caves.bake_spec) with Stranglethorn's own layouts
(tools/handbuilt_stranglethorn_caves) and material specs.  NO NEW TEXTURES: every material here is an
existing seamless tile from assets/tiles/caves/seamless, some of them dimmed by dim() (which writes its
darkened copy once and commits it, exactly as the Durotar and Echo bakers do).

  Rotvine Hollow      the Wailing Caverns damp set - wet clay, moss and standing water, with the troll
                      stonework of the crag's own stair showing through on the drowned shelf.
  Veilfall Cave       bare limestone at the mouth, and the Blackfathom temple floor on the inner two
                      terraces where the carving starts.  Water is grotto tidepool, as everywhere wet.
  The Drowned Shrine  grotto TEMPLE floor and wall throughout, because this is a building: the only
                      cave floor in it is the sea mouth you came in through.  Water is read back from
                      the zone's own tiles (tile_water) rather than from analytic pools - the flooded
                      halls are hand-placed rectangles, so the painting has to follow the collision.
"""
import sys

from tools import bake_durotar_caves as BD
from tools import handbuilt_stranglethorn_caves as SC
from tools.bake_durotar_caves import M, dim, CS

SPECS = {}

SPECS["rotvine_hollow"] = dict(
    build="build_rotvine_hollow", seed=137, slug="rotvine_hollow",
    materials={
        "clay":    M(dim(CS + "wc_floor_a", 0.88)),
        "moss":    M(CS + "mossy_cave_floor_a", CS + "cave_moss_clump_a"),
        "silt":    M(dim(CS + "gro_sand_a", 0.52)),
        "stone":   M(dim(CS + "bfd_temple_floor_a", 0.72)),
        "water_s": M(CS + "wc_water_a"),
        "water_d": M(dim(CS + "gro_deep_floor_a", 0.82)),
        "wall":    M(CS + "wc_wall_a"),
        "rock":    M(CS + "cave_wall_2_a"),
        "twall":   M(dim(CS + "bfd_temple_wall_a", 0.78)),
    },
    floor_keys=["clay", "moss", "silt", "stone"],
    wall_keys=["wall", "rock", "twall"],
    floors={
        "moss": [(54, 50, 40, 24), (24, 60, 16, 12), (32, 12, 7, 9)],
        "silt": [(88, 70, 15, 11), (84, 34, 14, 10)],
        "stone": [(18, 30, 11, 8)],
    },
    walls={"rock": [(54, 50, 46, 30), (88, 70, 18, 13)],
           "twall": [(18, 30, 14, 11)]},
    pools=[SC.RH_POOLS],
    cfg=dict(ao=0.46, depth=0.88, lip=22, lip_col=(0.55, 0.85, 0.6), deep_dark=0.48,
             foam_col=(200, 225, 205), glows=[]),
)

SPECS["veilfall_cave"] = dict(
    build="build_veilfall_cave", seed=149, slug="veilfall_cave",
    materials={
        "lime":    M(CS + "cave_floor_rock_1_a", CS + "cave_floor_rock_2_a"),
        "wet":     M(dim(CS + "mossy_cave_floor_a", 0.92)),
        "shrine":  M(CS + "bfd_temple_floor_a"),
        "sand":    M(dim(CS + "gro_sand_a", 0.66)),
        "water_s": M(CS + "gro_tidepool_a"),
        "water_d": M(CS + "gro_deep_floor_a"),
        "wall":    M(CS + "cave_wall_1_b"),
        "rock":    M(CS + "cave_wall_2_a"),
        "twall":   M(CS + "bfd_temple_wall_a"),
    },
    floor_keys=["lime", "wet", "shrine", "sand"],
    wall_keys=["wall", "rock", "twall"],
    # the inner ellipse covers the two inner terraces; a floor score only ever lands on floor tiles,
    # so one blob per depth band is enough to make the carving get more deliberate as you descend
    floors={
        "shrine": [(66, 52, 24, 24)],
        "sand": [(66, 52, 9, 9), (30, 73, 6, 5), (85, 87, 6, 4)],
        "wet": [(32, 22, 8, 16), (30, 73, 10, 8), (85, 87, 10, 7), (73, 11, 10, 7)],
    },
    walls={"twall": [(66, 52, 26, 26)],
           "rock": [(32, 22, 11, 19), (30, 73, 12, 10), (85, 87, 12, 9), (73, 11, 12, 9)]},
    pools=[SC.VF_POOLS],
    cfg=dict(ao=0.44, depth=0.86, lip=20, lip_col=(0.65, 0.9, 1.0), deep_dark=0.5,
             foam_col=(210, 240, 245), glows=[]),
)

SPECS["drowned_shrine"] = dict(
    build="build_drowned_shrine", seed=151, slug="drowned_shrine",
    materials={
        "stone":   M(CS + "gro_temple_floor_a"),
        "silt":    M(dim(CS + "gro_sand_a", 0.6)),
        "kelp":    M(CS + "gro_kelp_floor_a"),
        "pearl":   M(dim(CS + "gro_pearl_floor_a", 0.6)),
        "water_s": M(CS + "gro_tidepool_a"),
        "water_d": M(CS + "gro_deep_floor_a"),
        "twall":   M(CS + "gro_temple_wall_a"),
        "coral":   M(CS + "gro_coral_wall_a"),
        "wall":    M(CS + "gro_cave_wall_a"),
    },
    floor_keys=["stone", "silt", "kelp", "pearl"],
    wall_keys=["twall", "coral", "wall"],
    floors={
        "silt": [(32, 14, 7, 11), (59, 22, 20, 5)],
        "kelp": [(59, 61, 20, 15), (20, 83, 10, 10)],
        "pearl": [(85, 83, 15, 11)],
    },
    walls={"wall": [(32, 12, 11, 10)],
           "coral": [(59, 61, 24, 18), (33, 35, 16, 14), (85, 35, 16, 14)]},
    pools=[],
    tile_water=True,
    cfg=dict(ao=0.40, depth=0.80, lip=18, lip_col=(0.6, 0.9, 1.0), deep_dark=0.52,
             foam_col=(205, 238, 245), glows=[]),
)

BD.C = SC
BD.SPECS = SPECS

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    if pv and pv in args:
        args.remove(pv)
    for k in (args or list(SPECS)):
        BD.bake_spec(k, pv)
