"""
Bake the Citadel of Ascent's four dungeon floors (tools/handbuilt_gravity_foundry.py, tools/handbuilt_ascendant_spire.py).

    PYTHONPATH=. python3 tools/bake_citadel_dungeons.py [halls keel spire command] [--preview DIR]

Painted from Kyle's sheet AB4 (21 Nov 2026) and the Aetherian ground the sky already has:
  THE FOUNDRY HALLS   riveted iron plate everywhere, rail tracks in the Intake where the carts come in, slag-spattered
                      stone round the pour, engine plate in the Quench Halls, the forge grating in
                      the Assembly Ring, bronze floor in the Gallery. The pour and the pit are molten crystal, lit
                      orange. Walls of soot-stained bronze pipework, vent brick round the Casting Floor.
  THE KEELWORKS       iron plate, hazard bronze on the Lift Landing, deck grating round the drop, gravity-cracked
                      paving in the Gravity Chamber, the forge grating in the Core Vault, rails down the Great Slip.
                      Every drop is open sky, cold blue light off it. Gearwork walls.
  THE HALLS OF ASCENT pale marble; parade flagstones in the Muster Yard, grand paving down the Lancer Halls, the
                      storm-scorched balcony on the Storm Gallery, ash-strewn boards in the Burning Archive, the
                      rune-circle slate in the Inquisitorium. White-and-gold walls, black stone round the
                      Inquisitorium, shelves round the Archive. The Gallery's open side is the storm sky.
  THE COMMAND SPIRE   palace marble; the rune floor in the Aegis Hall, royal carpet in the War Room, gold-veined black
                      marble down the Guard's Walk, gold floor in the Sanctum. Blue tile walls, crystal round the
                      Sanctum, which is open to the sky at both ends.
"""
import sys

from tools import bake_durotar_caves as BD
from tools.bake_durotar_caves import M, dim

from tools import handbuilt_gravity_foundry as GF
from tools import handbuilt_ascendant_spire as AS
from tools.citadel_dungeon_kit import room_box

G = "sky/ground/"


def _room(mod, floor, name, pad=2):
    x, y, w, h = room_box(mod.FLOOR[floor]["rooms"][name])
    return [(x + w / 2, y + h / 2, w / 2 + pad, h / 2 + pad)]


def spec_halls():
    F = GF.HALLS
    return dict(
        build="build_halls_baked", seed=561, slug="gravity_foundry", lava=True, mod=GF, floor=F,
        materials={"floor": M(G + "ab_iron_plates"), "rail_f": M(G + "ab_rail_floor"),
                   "slag_f": M(G + "ab_slag_stone"), "hazard_f": M(G + "ae_engine_plates"),
                   "grate_f": M(G + "ab_forge_grate"), "bronze_f": M(G + "ae_bronze_floor"),
                   "wall": M(dim(G + "ab_wall_foundry_pipes", 0.75)), "vent_w": M(dim(G + "ab_wall_vent_brick", 0.75)),
                   "lava": M(G + "ab_molten_crystal")},
        floor_keys=["floor", "rail_f", "slag_f", "hazard_f", "grate_f", "bronze_f"],
        wall_keys=["wall", "vent_w"],
        floors={"rail_f": _room(GF, F, "The Intake"), "slag_f": _room(GF, F, "The Casting Floor"),
                "hazard_f": _room(GF, F, "The Quench Halls"), "grate_f": _room(GF, F, "The Assembly Ring", 0),
                "bronze_f": _room(GF, F, "The Overseer's Gallery")},
        walls={"vent_w": _room(GF, F, "The Casting Floor", 8)},
        pools=[],
        cfg=dict(ao=0.45, depth=0.80, lip=14, lip_col=(1.0, 0.75, 0.40), deep_dark=0.20,
                 foam_col=(255, 210, 140), glows=[("d_lava", (255, 140, 40), 2.6, 0.75)]),
    )


def spec_keel():
    F = GF.KEEL
    return dict(
        build="build_keel_baked", seed=562, slug="keelworks", lava=True, mod=GF, floor=F,
        materials={"floor": M(G + "ab_iron_plates"), "hazard_f": M(G + "ab_hazard_bronze"),
                   "deck_f": M(G + "sk_deck_grating"), "gravity_f": M(G + "kh_gravity_paving"),
                   "grate_f": M(G + "ab_forge_grate"), "rail_f": M(G + "ab_rail_floor"),
                   "wall": M(dim(G + "ab_wall_gearwork", 0.75)), "pipe_w": M(dim(G + "ab_wall_foundry_pipes", 0.75)),
                   "lava": M(G + "sk_sky_deep")},
        floor_keys=["floor", "hazard_f", "deck_f", "gravity_f", "grate_f", "rail_f"],
        wall_keys=["wall", "pipe_w"],
        floors={"hazard_f": _room(GF, F, "The Lift Landing"), "deck_f": _room(GF, F, "The Gantry Walks"),
                "gravity_f": _room(GF, F, "The Gravity Chamber"), "grate_f": _room(GF, F, "The Core Vault", 0),
                "rail_f": _room(GF, F, "The Great Slip")},
        walls={"pipe_w": _room(GF, F, "The Great Slip", 8)},
        pools=[],
        cfg=dict(ao=0.40, depth=0.75, lip=18, lip_col=(0.80, 0.92, 1.0), deep_dark=0.30,
                 foam_col=(225, 240, 255), glows=[("d_lava", (120, 170, 255), 2.4, 0.6)]),
    )


def spec_spire():
    F = AS.HALLS
    return dict(
        build="build_halls_baked", seed=601, slug="ascendant_spire", lava=True, mod=AS, floor=F,
        materials={"floor": M(G + "ae_palace_marble"), "parade_f": M(G + "ab_parade_flags"),
                   "paving_f": M(G + "ae_grand_paving"), "storm_f": M(G + "ab_storm_balcony"),
                   "boards_f": M(G + "ab_archive_boards"), "rune_f": M(G + "ab_rune_slate"),
                   "wall": M(dim(G + "ab_wall_white_gold", 0.8)), "black_w": M(dim(G + "ab_wall_black_stone", 0.8)),
                   "shelf_w": M(dim(G + "ab_wall_shelves", 0.8)), "lava": M(G + "sk_cloud_storm")},
        floor_keys=["floor", "parade_f", "paving_f", "storm_f", "boards_f", "rune_f"],
        wall_keys=["wall", "black_w", "shelf_w"],
        floors={"parade_f": _room(AS, F, "The Muster Yard"), "paving_f": _room(AS, F, "The Lancer Halls"),
                "storm_f": _room(AS, F, "The Storm Gallery"), "boards_f": _room(AS, F, "The Burning Archive"),
                "rune_f": _room(AS, F, "The Inquisitorium")},
        walls={"black_w": _room(AS, F, "The Inquisitorium", 8), "shelf_w": _room(AS, F, "The Burning Archive", 6)},
        pools=[],
        cfg=dict(ao=0.35, depth=0.70, lip=18, lip_col=(0.85, 0.92, 1.0), deep_dark=0.25,
                 foam_col=(230, 240, 255), glows=[("d_lava", (150, 180, 255), 2.4, 0.55)]),
    )


def spec_command():
    F = AS.COMMAND
    return dict(
        build="build_command_baked", seed=602, slug="command_spire", lava=True, mod=AS, floor=F,
        materials={"floor": M(G + "ae_palace_marble"), "rune_f": M(G + "ae_rune_floor"),
                   "carpet_f": M(G + "ae_royal_carpet"), "black_f": M(G + "ab_gold_black_marble"),
                   "gold_f": M(G + "ae_gold_floor"),
                   "wall": M(dim(G + "ab_wall_blue_tile", 0.8)), "crystal_w": M(dim(G + "ab_wall_crystal", 0.8)),
                   "lava": M(G + "sk_sky_deep")},
        floor_keys=["floor", "rune_f", "carpet_f", "black_f", "gold_f"],
        wall_keys=["wall", "crystal_w"],
        floors={"rune_f": _room(AS, F, "The Aegis Hall", 0), "carpet_f": _room(AS, F, "The War Room"),
                "black_f": _room(AS, F, "The Guard's Walk"), "gold_f": _room(AS, F, "The Exarch's Sanctum")},
        walls={"crystal_w": _room(AS, F, "The Exarch's Sanctum", 8)},
        pools=[],
        cfg=dict(ao=0.35, depth=0.70, lip=20, lip_col=(0.85, 0.95, 1.0), deep_dark=0.25,
                 foam_col=(230, 245, 255), glows=[("d_lava", (140, 180, 255), 2.6, 0.6)]),
    )


class _Shim:
    def __init__(self, mod, build_name, baked):
        self.BAKED = baked
        setattr(self, build_name, getattr(mod, build_name))


SPECS = {"halls": spec_halls, "keel": spec_keel, "spire": spec_spire, "command": spec_command}

if __name__ == "__main__":
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    only = [a for a in sys.argv[1:] if a in SPECS]
    for key, fn in SPECS.items():
        if only and key not in only:
            continue
        spec = fn()
        mod, floor = spec.pop("mod"), spec.pop("floor")
        BD.SPECS = {spec["slug"]: spec}
        BD.C = _Shim(mod, spec["build"], mod.BAKED[floor])
        BD.bake_spec(spec["slug"], preview=(f"{pv}/{spec['slug']}.png" if pv else None))
