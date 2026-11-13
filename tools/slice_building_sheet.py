#!/usr/bin/env python3
"""Slice the 6x5 magenta-background BUILDING sheet into 30 transparent PNGs in assets/buildings/.

    python3 tools/slice_building_sheet.py tools/building_sheets/eastern_kingdoms_buildings.png
    python3 tools/slice_building_sheet.py <sheet.png> --preview /tmp/ek_buildings.png

Same magenta key as the icon sheets (tools/slice_icon_sheet.key_magenta: soft alpha ramp plus a despill pass so
dark eaves and timber edges don't come back with a pink fringe). Prompts and the cell order live in
claude/eastern_kingdoms_building_prompts.md - NAMES below is that table, and the two must stay in step.

Two things differ from slice_icon_sheet, both because these are buildings and not inventory icons:

  * no square padding and no fixed output size. An icon is a 96x96 square by contract; a building is a sprite
    placed by its bottom-centre with a declared height in tiles, so it keeps its own aspect.
  * RELATIVE SCALE IS PRESERVED. Every sprite is cropped to its own bounding box but NOT normalised, so a
    cottage stays smaller than a barn exactly as drawn. Normalising per-cell is right for a sheet of unrelated
    objects (a feather and a strongbox) and wrong here, where a cottage drawn at a cottage's size is the
    information. Same reasoning as the potion sheet's PRESERVE_SCALE.

The generated sheets are never on a perfect pixel grid - rows drift - so sprites are found as connected blobs
and assigned to whichever cell holds their centre, rather than cut on arithmetic cell boundaries.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from slice_icon_sheet import key_magenta  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

#: set name -> (cols, rows, output dir, names in grid order left-to-right then top-to-bottom)
SETS = {}


def _set(key, cols, rows, out, names):
    names = names.split()
    assert len(names) == cols * rows, (key, len(names), cols * rows)
    SETS[key] = (cols, rows, out, names)


_set("ek_buildings", 6, 5, "assets/buildings", """
    ek_watermill ek_mill_sluice ek_granary ek_millstone_shelter ek_apothecarium ek_plague_vat_platform
    ek_forsaken_field_tent ek_forsaken_watchtower ek_cottage_small ek_cottage_medium ek_townhouse ek_village_inn
    ek_village_chapel ek_smithy_forge ek_stable_block ek_barn ek_trading_post ek_fishery_shed
    ek_boathouse ek_sawmill_shed ek_tannery ek_apiary_shelter ek_border_watchtower ek_gatehouse
    ek_barracks_hall ek_command_tent ek_ruined_gatehouse ek_burnt_cottage ek_syndicate_house ek_wayshrine""")

#: Generic high-elven architecture in the classic crimson and gold. Deliberately NOT Underdark-specific:
#: Kael's Bastion gets its look by hue-shifting these, and Silvermoon/Ghostlands/Eversong reuse the originals.
_set("blood_elf", 6, 5, "assets/buildings", """
    be_house_small be_house_medium be_manor be_townhouse be_inn be_shop
    be_market_stall be_smithy be_alchemist be_sanctum be_spire be_grand_spire
    be_great_hall be_library be_temple be_barracks be_guard_post be_gatehouse
    be_wall_arch be_arcane_well be_portal_frame be_stable be_storehouse be_treasury
    be_observatory be_pavilion be_command_tent be_ruined_house be_ruined_tower be_obelisk""")

#: The giant mushrooms are the Underdark's TREES - cells 1-4 are scattered by the forest pass, so their
#: relative scale against the camp gear and rubble is load-bearing, not cosmetic.
_set("underdark_props", 6, 6, "assets/tiles/underdark/props", """
    ud_shroom_tall_violet ud_shroom_squat_ochre ud_shroom_cluster_blue ud_shroom_canopy ud_shroom_small ud_shelf_fungus
    ud_crystal_violet ud_crystal_cyan ud_lattice_growth ud_crystal_spire ud_geode_open ud_crystal_float
    ud_glow_pool ud_lichen_boulder ud_moss_curtain ud_spore_vent ud_ice_stalagmites ud_frozen_crate
    ud_survey_tripod ud_arcane_brazier ud_field_desk ud_codex_crates ud_specimen_rack ud_codex_banner
    ud_dig_scaffold ud_codex_tent ud_broken_column ud_fallen_arch ud_statue_armless ud_masonry_rubble
    ud_floating_stone ud_rune_stone ud_fungal_shelf ud_fungal_node ud_cocooned_shape ud_stalagmites""")

#: BANDIT / OUTLAW buildings (claude/bandit_building_prompts.md). Kyle, 2026-11-01: "not caveman or
#: archaic or anything" - these are tradesmen and dispossessed gentry who turned, so the sheet is
#: competent human architecture that has been seized and barricaded. Cell 23 is the one deliberately
#: crude building on it.
_set("bandit", 6, 5, "assets/buildings", """
    bd_brigand_hall bd_counting_house bd_captains_quarters bd_barricaded_townhouse bd_seized_chapel bd_strongroom
    bd_seized_watermill bd_powder_store bd_arms_workshop bd_carpenter_shop bd_mason_shed bd_warehouse
    bd_seized_farmhouse bd_commandeered_barn bd_grain_store bd_cart_shed bd_stock_pen bd_well_house
    bd_gate_barricade bd_lookout_tower bd_guard_post bd_palisade_section bd_sentry_leanto bd_winch_house
    bd_dock_house bd_boat_shed bd_hideout_entrance bd_interrogation_house bd_fence_shop bd_burnt_house""")

#: ORC GARRISON buildings (claude/orc_building_prompts.md). The eleven orc buildings already in the
#: library are Valley-of-Trials starter architecture - huts, tents, hide. Kyle: "actual buildings and not
#: just huts and shacks." Cells 28-30 are orc construction with Forsaken tenants, for Hammerfall.
_set("orc", 6, 5, "assets/buildings", """
    orc_war_hall orc_warchief_lodge orc_barracks_longhouse orc_officers_house orc_great_gatehouse orc_stockade_section
    orc_war_forge orc_armoury orc_siege_workshop orc_tannery_hall orc_butchery orc_supply_store
    orc_spirit_lodge orc_totem_court orc_great_totem orc_warbeast_stable orc_kennel_block orc_pyre_platform
    orc_mess_hall orc_brew_house orc_warlock_tower orc_healer_house orc_quartermaster_post orc_smokehouse
    orc_watch_tower orc_guard_post orc_signal_beacon orc_forsaken_apothecary orc_deathguard_post orc_bone_yard_shed""")

#: THE ASPEN WILDERNESS props. Cells 1-10 are the zone's TREES - aspen and lodgepole - so like the
#: Underdark's giant mushrooms they get scattered by the forest pass and their relative scale against the
#: brush and camp gear is load-bearing. Nothing from Earth is on this sheet (Kyle, 2026-10-27: "we dont
#: want anything from our world yet"); the burn and the seam row is the range's own violence instead.
#: SOUTHERN THOUSAND NEEDLES props. Row 4 is the whole Freewind idea in six objects - rope, aspen timber
#: and the gear to span a gap between mesas. Nothing on this sheet is Earth-made; the aspen is the only
#: imported thing on it and it arrived as trees.
_set("southern_needles_props", 6, 6, "assets/tiles/southern_needles/props", """
    sn_rock_spire sn_boulder_red sn_layered_stack sn_split_stone sn_rock_arch sn_toppled_column
    sn_barrel_cactus sn_saguaro sn_thornbush sn_desert_sage sn_dead_shrub sn_grass_tuft
    sn_kodo_skull sn_rib_bones sn_hide_frame sn_driftwood_salt sn_clay_vessel sn_stone_pile
    sn_rope_coil sn_anchor_post sn_plank_stack sn_scaffold sn_pulley_hoist sn_bridge_upright
    sn_hide_tent sn_totem_aspen sn_cook_fire sn_drying_rack sn_water_trough sn_hide_banner
    sn_windsock sn_streamers sn_lookout_platform sn_cairn sn_rope_railing sn_spear_bundle""")

_set("aspen_props", 6, 6, "assets/tiles/aspen/props", """
    asp_aspen_tall asp_aspen_bare asp_aspen_young asp_aspen_clump asp_aspen_fallen asp_aspen_stump
    asp_pine_tall asp_pine_bent asp_pine_krummholz asp_pine_young asp_snag_standing asp_deadfall_pile
    asp_willow_thicket asp_fireweed asp_huckleberry asp_ferns asp_grass_tussock asp_wildflowers
    asp_boulder asp_boulder_lichen asp_boulder_split asp_talus_pile asp_beaver_dam asp_beaver_lodge
    tau_timber_stack tau_hide_tent_small tau_totem_carved tau_drying_rack tau_hitching_post tau_cook_fire
    asp_snag_charred asp_stump_burned asp_trunk_snapped asp_dead_scrub asp_red_drift asp_elk_skull""")

#: TAUREN BUILDINGS, general purpose (Kyle: "keep them general enough to reuse as needed"). Camp Taurajo,
#: Freewind Post and anything tauren later all draw from this one set. Traditional hide-and-pole
#: architecture; Freewind's aspen-timber rebuild is a recolour experiment first, not a second sheet.
_set("tauren", 6, 5, "assets/buildings", """
    tau_tent_small tau_tent_medium tau_tent_large tau_longhouse tau_elder_lodge tau_yurt
    tau_great_lodge tau_spirit_lodge tau_hearth_lodge tau_meeting_shelter tau_bonfire_pavilion tau_trading_post
    tau_smithy tau_tannery tau_carver_shop tau_herb_hut tau_bowyer tau_kiln
    tau_storehouse tau_food_cache tau_kodo_pen tau_stable tau_water_trough tau_watchtower
    tau_gate_arch tau_palisade tau_totem_pole tau_footbridge tau_tent_burned tau_lodge_collapsed""")

#: ENTRANCE ART, sheet 2 (claude/entrance_art_prompts_2.md): the way OUT seen from inside, road
#: gates by region, and entrances for the newer zones' dungeons. The ent_ prefix is what lets a
#: sprite stand over a portal tile (world/portal_art.py).
_set("entrances_2", 6, 4, "assets/tiles/cave_entrances", """
    ent_exit_cave_daylight ent_exit_stone_stairs ent_exit_mine_adit ent_exit_ice_tunnel ent_exit_crystal ent_exit_flooded_stairs
    ent_exit_ship_hatch ent_exit_gangplank ent_gate_kodo_tusks ent_gate_lychgate ent_gate_tollgate ent_gate_standing_stones
    ent_gate_sand_pylons ent_gate_rope_bridge ent_gate_snow_logs ent_gate_basalt_storm ent_gate_goblin_port ent_gate_crystal_arch
    ent_ogre_mound ent_kobold_dig ent_shipwreck_hull ent_dwarven_vault ent_salt_sinkhole ent_sunken_belltower""")

#: ENTRANCE ART, sheet 3 (claude/entrance_art_prompts_3_4.md): town gates, boat landings, and
#: six more road gates. Row 4 was ASKED for side-on and came back facing the camera, so those
#: six are filed as plain front-facing gates; the side-on piece is still missing.
_set("entrances_3", 6, 4, "assets/tiles/cave_entrances", """
    ent_town_tauren_totems ent_town_nightelf_bridge ent_town_forsaken_gate ent_town_troll_gate ent_town_wheel_arch ent_town_highelf_gate
    ent_town_headframe_gate ent_town_charred_gate ent_town_whalerib_gate ent_town_pirate_gate ent_gate_wall_breach ent_gate_pass_cairns
    ent_dock_pier ent_dock_troll ent_dock_goblin ent_dock_forsaken ent_dock_nightelf ent_dock_slipway
    ent_gate_logs ent_gate_stone_pillars ent_gate_tusk_banners ent_gate_sandstone ent_gate_bamboo ent_gate_snowpine""")

#: Sheet 4: the way OUT by dungeon flavour, and doors that lead deeper. Kyle generated it twice
#: and kept both ("i downloaded both"), so the second take is the same list with _b - a second
#: look for each, which matters where one dungeon has several exits.
_set("entrances_4a", 6, 4, "assets/tiles/cave_entrances", """
    ent_exit_crypt_stairs ent_exit_spider_web ent_exit_troll_temple ent_exit_lava_fissure ent_exit_ogre_hall ent_exit_kobold_tunnel
    ent_exit_dwarven_vault ent_exit_keep_gate ent_exit_tower_door ent_exit_root_hollow ent_exit_sewer_grate ent_exit_salt_shaft
    ent_exit_bramble ent_exit_wreck_hull ent_exit_bell_window ent_exit_slot_canyon ent_exit_fern_cavern ent_exit_coral_arch
    ent_door_ship_cabin ent_door_ship_hatch_down ent_door_stairs_down ent_door_bronze_pipe ent_door_ice_steps ent_door_crystal_rift""")
_set("entrances_4b", 6, 4, "assets/tiles/cave_entrances", """
    ent_exit_crypt_stairs_b ent_exit_spider_web_b ent_exit_troll_temple_b ent_exit_lava_fissure_b ent_exit_ogre_hall_b ent_exit_kobold_tunnel_b ent_exit_dwarven_vault_b ent_exit_keep_gate_b ent_exit_tower_door_b ent_exit_root_hollow_b ent_exit_sewer_grate_b ent_exit_salt_shaft_b ent_exit_bramble_b ent_exit_wreck_hull_b ent_exit_bell_window_b ent_exit_slot_canyon_b ent_exit_fern_cavern_b ent_exit_coral_arch_b ent_door_ship_cabin_b ent_door_ship_hatch_down_b ent_door_stairs_down_b ent_door_bronze_pipe_b ent_door_ice_steps_b ent_door_crystal_rift_b""")

#: DARK IRON buildings (assets/buildings/_src/tempest_dark_iron_buildings_sheet_30.png). Drawn for
#: Tempest Isle and first used for Onyxhollow, the Dark Iron town under the Abyssal Sands (Kyle, 13
#: Nov 2026: "We have all the art"). Rows: the works, the heavy plant, the town and its ruins, forge
#: gear, street furniture.
_set("dark_iron", 6, 5, "assets/buildings", """
    di_smeltery di_great_hall di_gatehouse di_barracks di_watchtower di_wall_section
    di_blast_furnace di_boiler_works di_mine_head di_crane_warehouse di_smithy di_vault
    di_inn di_shop di_shrine di_ruined_hall di_ruined_tower di_ruined_gate
    di_forge_anvil di_bellows di_crucible di_ore_cart di_steam_pipes di_slag_heap
    di_brazier di_crane_hook di_cage di_rune_obelisk di_dwarf_statue di_rubble""")

#: SMOKE DRAWN OVER A MAGENTA KEY COMES BACK PURPLE. A generator asked for a lodge with a smoke hole
#: draws the plume semi-transparent, and whatever is behind it - the key - bleeds through. Keying then
#: gives a correctly-shaped wisp in the wrong colour, which is invisible against dark ground and obvious
#: against snow or pale grass.
#:
#: This cannot be a blanket despill: tauren decoration is full of legitimate violet beadwork and the
#: Aspen set has fireweed, which really is magenta. So it is opt-in per sprite and confined to the top
#: fraction of that sprite, where a plume lives and hanging beads do not.
#: {sprite: fraction of height treated, measured from the top}
DESPILL_TOP = {"tau_great_lodge": 0.22, "di_smeltery": 0.30, "di_boiler_works": 0.30,
               "di_steam_pipes": 0.30}


def _despill_plume(cut, frac):
    """Neutralise magenta-cast pixels in the top `frac` of a sprite, keeping luminance and alpha."""
    out = cut.copy()
    h = out.shape[0]
    band = out[:max(1, int(h * frac))]
    rgb = band[..., :3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    # Any strong colour cast on a SEMI-TRANSPARENT pixel in this band, not just magenta. Over-subtracting
    # the key leaves a green edge exactly where it removed a magenta one, so testing only for magenta
    # trades a purple wisp for a green one. Smoke is achromatic; the opaque roof ring below it is not
    # touched, which is what the alpha test protects.
    chroma = rgb.max(axis=-1) - rgb.min(axis=-1)
    a = band[..., 3]
    # Two cases, and it needs both. Restricting to semi-transparent pixels alone leaves the opaque magenta
    # smudge where the plume meets the smoke hole; testing only for magenta leaves the green edge the key
    # over-subtracted. Magenta is safe to treat at ANY alpha here because the structure underneath is brown
    # and orange - warm colours have b well BELOW g, so the roof ring never matches.
    magenta = (r - g > 22) & (b - g > 22) & (a > 8)
    cast = (chroma > 22) & (a > 8) & (a < 205)
    bad = magenta | cast
    if bad.any():
        lum = (0.299 * r + 0.587 * g + 0.114 * b)[bad]
        for ch in range(3):
            rgb[..., ch][bad] = lum
    return out


def _settles(name):
    """Entrance art that is a MASS - a cave mouth, a mound, a hull, a stair cut out of its wall -
    rather than something standing on posts. Kyle, 12 Nov, of the kobold dig on a riverbank and
    a ship's stair on a deck: "try to blend these better". A mass cut out with a hard edge reads
    as a sticker; a gate on two posts does not, and softening it would only eat the posts."""
    if not name.startswith("ent_"):
        return False
    return not name.startswith(("ent_gate_", "ent_town_", "ent_dock_"))


def _settle_into_ground(cut):
    """Fade a sprite's silhouette edge to nothing, a little at the top and a lot at the foot.

    The foot is where a prop meets the ground it was not painted on, so that is where the hard
    cut-out line shows; the top is sky-side and only needs the stair-step taken off. The fade is
    by distance from the silhouette's own edge, so holes in the art (the gap in a railing) fade
    too and nothing is blurred - colour is untouched, only alpha.
    """
    from scipy import ndimage
    out = cut.copy()
    a = out[..., 3]
    h = a.shape[0]
    dist = ndimage.distance_transform_edt(a > 40)
    width = 3.0 + 13.0 * (np.arange(h) / max(1, h - 1)) ** 1.5         # px: 3 at the top, 16 at the foot
    out[..., 3] = a * np.clip(dist / width[:, None], 0.0, 1.0) ** 0.8
    return out


#: A blob this big ANCHORS a cell - it is the building body. Buildings are far larger than icons, so the icon
#: slicer's 60px floor would let keying dirt anchor a cell on its own.
MIN_BLOB = 1500
#: ...but a detached chimney, banner, lantern, weathervane or wheel paddle is far SMALLER than that and must
#: still be merged into its building, so anything above plain keying noise is kept as long as its cell already
#: has an anchor. Found by testing: a 20x22 chimney left 10px clear of its roof is 440px and was being
#: silently dropped, which cost the sprite its whole top.
MIN_PART = 60


def slice_sheet(which, sheet_path, out_dir=None, preview=None):
    COLS, ROWS, default_out, NAMES = SETS[which]
    from scipy import ndimage
    out_dir = Path(out_dir) if out_dir else ROOT / default_out
    out_dir.mkdir(parents=True, exist_ok=True)

    im = Image.open(sheet_path).convert("RGB")
    W, H = im.size
    rgba = key_magenta(np.asarray(im).astype(np.float64))
    cw, ch = W / COLS, H / ROWS

    solid = rgba[..., 3] > 24
    solid[:4, :] = solid[-4:, :] = False          # a sheet edge that is not quite magenta is not a building
    solid[:, :4] = solid[:, -4:] = False
    # Dilation bridges a detached chimney or banner back onto its building. Too much of it welds NEIGHBOURING
    # buildings together instead: a tall sprite overflows its cell, touches the one in the next row, the merged
    # blob's centre lands in one cell and the other comes up empty. Found with the blood elf sheet, where the
    # grand spire (449px in a 250px row) swallowed the shop above it. Two is enough to catch a loose chimney
    # and not enough to cross the gap between two drawn buildings.
    labels, n = ndimage.label(ndimage.binary_dilation(solid, iterations=2))

    cells, parts = {}, {}
    for lab in range(1, n + 1):
        m = (labels == lab) & solid
        area = m.sum()
        if area < MIN_PART:
            continue
        ys, xs = np.where(m)
        key = (int(ys.mean() // ch), int(xs.mean() // cw))
        (cells if area >= MIN_BLOB else parts).setdefault(key, []).append(m)

    problems, written = [], []
    for idx, name in enumerate(NAMES):
        r, c = divmod(idx, COLS)
        blobs = cells.get((r, c))
        if not blobs:
            problems.append(f"{name}: no building found in cell r{r} c{c}")
            continue
        # A building is one object, but chimneys, banners and wheel paddles can key as their own blobs, so
        # everything whose centre lands in the cell is merged rather than taking only the largest.
        mask = np.logical_or.reduce(blobs + parts.get((r, c), []))
        ys, xs = np.where(mask)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        cut = rgba[y0:y1, x0:x1].copy()
        cut[..., 3] *= mask[y0:y1, x0:x1]         # drop a neighbour bleeding into this bounding box
        if name in DESPILL_TOP:
            cut = _despill_plume(cut, DESPILL_TOP[name])
        if _settles(name):
            cut = _settle_into_ground(cut)
        img = Image.fromarray(cut.astype(np.uint8), "RGBA")
        img.save(out_dir / f"{name}.png")
        written.append((name, img.size))
        n_extra = len(blobs) - 1 + len(parts.get((r, c), []))
        if n_extra:
            problems.append(f"{name}: {n_extra} detached part(s) merged in (chimney/banner?) - eyeball it")

    for (name, size) in written:
        print(f"  {name:28} {size[0]:4}x{size[1]:<4}")
    print(f"\n{len(written)}/{len(NAMES)} sliced -> {out_dir}")
    if written:
        tall = max(written, key=lambda w: w[1][1])
        short = min(written, key=lambda w: w[1][1])
        print(f"relative scale kept: tallest {tall[0]} {tall[1][1]}px, shortest {short[0]} {short[1][1]}px")
    for p in problems:
        print(f"  !! {p}")

    if preview:
        _preview(written, out_dir, preview)
    return written, problems


def _preview(written, out_dir, path):
    """One contact sheet of everything that was cut, on a mid grey so alpha fringing shows up."""
    cols = 6
    cells = [Image.open(out_dir / f"{n}.png") for (n, _) in written]
    cw = max(c.width for c in cells) + 16
    rh = max(c.height for c in cells) + 16
    rows = (len(cells) + cols - 1) // cols
    sheet = Image.new("RGBA", (cols * cw, rows * rh), (110, 110, 115, 255))
    for i, c in enumerate(cells):
        r, k = divmod(i, cols)
        sheet.alpha_composite(c, (k * cw + (cw - c.width) // 2, r * rh + (rh - c.height) - 8))
    sheet.convert("RGB").save(path)
    print(f"preview -> {path}")


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if len(args) < 2 or args[0] not in SETS:
        raise SystemExit(f"usage: slice_building_sheet.py <{'|'.join(SETS)}> <sheet.png> [--preview OUT]")
    pv = sys.argv[sys.argv.index("--preview") + 1] if "--preview" in sys.argv else None
    slice_sheet(args[0], args[1], preview=pv)
