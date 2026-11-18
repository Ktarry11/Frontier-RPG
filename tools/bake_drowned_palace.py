"""
Bake the Drowned Palace's two floors (tools/handbuilt_drowned_palace.py).

    PYTHONPATH=. python3 tools/bake_drowned_palace.py [--preview DIR]

Painted from Kyle's Azshara ground sheet:
  THE FLOODED HALLS   wet marble everywhere, barnacled at the Sunken Gate, the drowned mosaic in the Siren's Court,
                      seaweed marble on the Gallery's ledges, kelp in the Archive, coral round the Throne of Tides;
                      the sea in the channels is real collision (lava tiles under the hood) painted deep sea, with a
                      cold teal light off it; tide-pool rock for the walls
  THE QUEEN'S VAULT   dry: marble terraces, the moon mosaic down the Processional, violet tile in the Arcanum, plaza
                      slab in the Hall of Mirrors, Highborne paving in the Throne Room. The walls ARE the sea (Kyle's
                      "dry vault" under the water): the wall material is deep sea, rimmed with a pale ward-light. The
                      well's water is arcane, glowing violet-blue.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

from tools import handbuilt_drowned_palace as DP

AZ = "azshara/ground/az_"


def _room(floor, name, pad=2):
    spec = DP.FLOOR[floor]["rooms"][name]
    if spec[0] == "rect":
        _k, x0, y0, x1, y1 = spec[:5]
        return [((x0 + x1) / 2, (y0 + y1) / 2, (x1 - x0) / 2 + pad, (y1 - y0) / 2 + pad)]
    return [(cx, cy, rx + pad, ry + pad) for (cx, cy, rx, ry) in spec[1]]


def spec_halls():
    H = DP.HALLS
    return dict(
        build="build_halls_baked", seed=591, slug="drowned_halls", lava=True,
        materials={"floor": M(AZ + "wet_marble"), "barnacle_f": M(AZ + "barnacle_marble"),
                   "mosaic_f": M(AZ + "drowned_mosaic"), "seaweed_f": M(AZ + "seaweed_marble"),
                   "kelp_f": M(AZ + "kelp_floor"), "coral_f": M(AZ + "coral_stone"),
                   "wall": M(dim(AZ + "tidepool_rock", 0.55)), "deep_w": M(dim(AZ + "rock_hill", 0.45)),
                   "lava": M(AZ + "sea_deep")},
        floor_keys=["floor", "barnacle_f", "mosaic_f", "seaweed_f", "kelp_f", "coral_f"],
        wall_keys=["wall", "deep_w"],
        floors={"barnacle_f": _room(H, "The Sunken Gate"), "mosaic_f": _room(H, "The Siren's Court", 0),
                "seaweed_f": _room(H, "The Collapsed Gallery"), "kelp_f": _room(H, "The Drowned Archive"),
                "coral_f": _room(H, "The Throne of Tides", 0)},
        walls={"deep_w": [(90, 75, 90, 75)]},
        pools=[],
        cfg=dict(ao=0.50, depth=0.85, lip=16, lip_col=(0.70, 0.90, 0.95), deep_dark=0.50,
                 foam_col=(215, 235, 240), glows=[("d_lava", (30, 110, 130), 2.2, 0.55)]),
    )


def spec_vault():
    V = DP.VAULT
    return dict(
        build="build_vault_baked", seed=592, slug="queens_vault", lava=True,
        materials={"floor": M(AZ + "marble_terrace"), "wet_f": M(AZ + "wet_marble"),
                   "moon_f": M(AZ + "moon_mosaic"), "violet_f": M(AZ + "violet_tile"),
                   "slab_f": M(AZ + "plaza_slab"), "paving_f": M(AZ + "highborne_paving"),
                   "wall": M(AZ + "sea_deep"), "deep_w": M(dim(AZ + "sea_deep", 0.6)),
                   "lava": M(AZ + "arcane_water")},
        floor_keys=["floor", "wet_f", "moon_f", "violet_f", "slab_f", "paving_f"],
        wall_keys=["wall", "deep_w"],
        floors={"wet_f": _room(V, "The Air Pocket"), "moon_f": _room(V, "The Moonguard Processional", 0),
                "violet_f": _room(V, "The Arcanum"), "slab_f": _room(V, "The Hall of Mirrors", 0),
                "paving_f": _room(V, "The Queen's Throne Room", 0)},
        walls={"deep_w": [(85, 70, 85, 70)]},
        pools=[],
        cfg=dict(ao=0.35, depth=0.70, lip=20, lip_col=(0.75, 0.95, 1.0), deep_dark=0.40,
                 foam_col=(220, 245, 255), glows=[("d_lava", (110, 90, 200), 2.6, 0.7)]),
    )


class _Shim:
    def __init__(self, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(DP, build_name))


if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    only = [a for a in sys.argv[1:] if a in ("halls", "vault")]
    for key, fn, floor in (("halls", spec_halls, DP.HALLS), ("vault", spec_vault, DP.VAULT)):
        if only and key not in only:
            continue
        spec = fn()
        BD.SPECS = {spec["slug"]: spec}
        BD.C = _Shim(spec["build"], DP.BAKED[floor])
        BD.bake_spec(spec["slug"], preview=(f"{pv}/{spec['slug']}.png" if pv else None))
