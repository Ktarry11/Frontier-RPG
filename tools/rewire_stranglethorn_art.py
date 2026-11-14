#!/usr/bin/env python3
"""Swap Stranglethorn's borrowed art for the art that was generated for it. Idempotent.

    PYTHONPATH=. python3 tools/rewire_stranglethorn_art.py [--check]

WHY. The nine Stranglethorn zones were built before their art existed, against a standing rule that
nothing waits on a sheet: the jungle was dressed in Ashenvale's temperate forest, the troll ruins in
night-elf masonry, Booty Bay in Ratchet's savanna-port buildings, and the fen in Barrens scrub. An
audit counted 127 placements of the wrong biome. Sheets A-F landed on 29 Oct 2026 and this is the pass
that puts the right sprite behind every one of those calls.

HOW IT WORKS, and why it is a script rather than a hand edit. Every Stranglethorn module reaches its
props through a one-letter helper bound to a directory - A was Ashenvale, C was coastal, J was Echo
Isles, X was Ashenvale corruption. The new art all lives in ONE directory, so the rewire is two moves:
repoint those four helpers at it, and rename the sprites. Doing that by hand across seven files and
~200 call sites is how a typo gets shipped; doing it with an explicit table means the table is the
thing to review, and --check will tell you whether every target actually exists on disk before
anything is written.

WHAT IT DELIBERATELY LEAVES ALONE:
  * `P` (Barrens props) keeps br_signpost, which is a shared sign used in a dozen zones and is not
    biome-specific.
  * `D` (dungeon props) keeps the vot_/rf_ crates, braziers, cages and banners. Those are generic
    interior dressing and the sheets did not replace them.
  * `B` (buildings) is renamed but not repointed - bb_* and gg_* live in assets/buildings/ with
    everything else, because they are buildings.

ONE SPRITE CAN REPLACE SEVERAL. There is no stv_ equivalent of a sawbuck or a hay pile, and inventing
one would have cost a sheet slot that a buttress-rooted tree needed more. Where the table maps two old
names onto one new sprite it is a deliberate merge, not an oversight.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SP = "assets/tiles/stranglethorn/props/"
BLD = ROOT / "assets/buildings"

FILES = ["tools/handbuilt_stranglethorn_north.py", "tools/handbuilt_stranglethorn_central.py",
         "tools/handbuilt_stranglethorn_south.py", "tools/handbuilt_gromgol.py",
         "tools/handbuilt_booty_bay.py", "tools/handbuilt_stranglethorn_caves.py",
         "tools/handbuilt_gurbashi_arena.py"]

#: old sprite name -> new sprite name. Everything on the right lives in SP unless it starts with
#: bb_ or gg_, which are buildings.
RENAME = {
    # ---- canopy and floor. The Ashenvale set is a temperate forest and this is a rainforest.
    "large_canopy_tree": "stv_tree_buttress",
    "medium_canopy_tree": "stv_tree_cluster",
    "canopy_tree_cluster": "stv_tree_vined",
    "jungle_banyan": "stv_tree_buttress",
    "fern_cluster": "stv_fern_clump",
    "fallen_log": "stv_log_mossy",
    "ash_felled_tree": "stv_log_mossy",
    "ash_log_pile": "stv_driftwood",
    "rock_outcrop_small": "stv_boulder_mossy",
    "rock_outcrop_large": "stv_stone_pile",
    "mossy_jungle_boulder": "stv_boulder_mossy",
    "mountain_rock": "stv_boulder_mossy",
    "ash_bramble_thicket": "stv_bramble",
    "ashx_nightmare_thorns": "stv_bramble",
    "ash_glow_mushrooms": "stv_mushroom_ring",
    "ash_glow_mushroom_ring": "stv_mushroom_ring",
    "ash_root_arch": "stv_liana_arch",
    "ash_root_curtain": "stv_moss_curtain",
    "ash_hay_pile": "stv_frond_litter",
    "dead_corrupted_tree": "stv_tree_dead_giant",
    "twisted_dead_tree_cluster": "stv_tree_dead_giant",
    "bamboo_grove": "stv_bamboo",
    "banana_plant": "stv_banana_clump",
    "hibiscus_bush": "stv_hibiscus",
    "palm_cluster": "stv_palm_young",
    "palm_lean_a": "stv_palm_frond",
    "palm_lean_b": "stv_screw_pine",
    "mangrove_thicket": "stv_mangrove",
    "nb_fen_willow": "stv_mangrove",
    "nb_lily_cattails": "stv_lily_pads",

    # ---- troll work. None of this existed before Sheet B: the ruins were night-elf masonry and the
    #      camps were furbolg.
    "ash_ivy_pillar": "stv_troll_column",
    "ash_mossy_spire": "stv_troll_obelisk",
    "ash_overgrown_steps": "stv_troll_steps",
    "ash_elven_ruin_wall": "stv_troll_ziggurat_block",
    "overgrown_ruin": "stv_troll_ziggurat_block",
    "stone_archway": "stv_troll_arch",
    "jungle_idol": "stv_troll_idol_head",
    "tiki_totem": "stv_troll_totem",
    "sunken_totem": "stv_troll_totem",
    "troll_stilt_hut": "stv_troll_hut",
    "troll_cookfire": "stv_troll_cookfire",
    "ash_furbolg_bonfire": "stv_troll_cookfire",
    "troll_war_banner": "stv_arena_standard",
    "ash_watch_platform": "stv_troll_platform",
    "ash_herb_rack": "stv_troll_hide_rack",
    "ash_sawbuck": "stv_troll_post",
    "ashx_skull_fence": "stv_troll_skull_fence",
    "kodo_skull": "stv_troll_skull_pile",
    "br_kodo_skeleton": "stv_troll_skull_pile",

    # ---- water's edge and the docks
    "ash_canoe_jetty": "stv_gangplank",
    "ash_footbridge": "stv_gangplank",
    "ash_pier_segment": "stv_dock_rail",
    "nb_boardwalk": "stv_dock_rail",
    "ash_stream_bed": "stv_tide_pool",
    "ash_waterfall_pool": "stv_tide_pool",
    "tide_pool": "stv_tide_pool",
    "coral_shell_cluster": "stv_shells",
    "coral_reef_outcrop": "stv_coral_outcrop",
    "sea_stack_spire": "stv_sea_stack",
    "crab_claw_arch": "stv_bone_arch",
    "driftwood_pile": "stv_driftwood",
    "shipwreck_full": "stv_wreck_hull",
    "shipwreck_fragment": "stv_wreck_bow",
    "rowboat_wreck": "stv_boat_wreck",
    "outrigger_canoe": "stv_outrigger",
    "mooring_posts": "stv_bollard",
    "dock_lantern_post": "stv_dock_lantern",
    "fish_crates_traps": "stv_fish_crates",
    "fish_drying_rack": "stv_fish_rack",

    # ---- the orc camp
    "ash_palisade_wall": "stv_palisade_wall",
    "ash_orc_trophy_pole": "stv_trophy_pole",
    "ash_supply_crates": "stv_crate_stack",
    "br_raptor_nest": "stv_raptor_nest",
    "br_hitching_trough": "stv_trough",

    # ---- buildings
    "the_broken_keel": "bb_harbour_inn",
    "harbor_tower": "bb_harbourmaster_tower",
    "trading_post": "bb_trade_shop",
    "mixed_trading_post": "bb_trade_shop",
    "bazaar_stall_row": "bb_trade_shop",
    "ratchet_docks_warehouse": "bb_warehouse",
    "gazlowes_office": "bb_counting_house",
    "generic_shack_a": "bb_lean_shack",
    "generic_shack_b": "bb_lean_shack",
    "clan_hall": "gg_longhouse",
    "smithy": "gg_forge",
    "watchtower": "gg_watchtower",
    "supply_depot": "gg_supply_store",
    "supply_cache_shed": "gg_supply_store",
    "generic_tent_a": "gg_command_tent",
    "generic_tent_b": "gg_command_tent",
    "plain_orc_house_a": "gg_supply_store",
    "plain_orc_house_b": "gg_command_tent",
    "generic_hut_a": "stv_troll_hut",
    "generic_hut_b": "stv_troll_hut",
}

#: helper letter -> the module-level dir constant it should be bound to after the rewire.
REPOINT = {"A": "SP", "C": "SP", "J": "SP", "X": "SP"}


def targets_exist():
    props = {p.stem for p in (ROOT / SP).glob("*.png")}
    blds = {p.stem for p in BLD.glob("*.png")}
    missing = sorted({v for v in RENAME.values() if v not in props and v not in blds})
    return missing


def rewire(text):
    n = 0
    # 1. bind the module's own SP constant
    if 'SP = "assets/tiles/stranglethorn/props/"' not in text:
        text = re.sub(r'^(KEY = )', 'SP = "assets/tiles/stranglethorn/props/"\n\n\\1', text,
                      count=1, flags=re.M)
        if 'SP = "assets' not in text:          # modules with no KEY line
            text = text.replace("\nW, H", '\nSP = "assets/tiles/stranglethorn/props/"\nW, H', 1)
    # 2. repoint the one-letter helpers at it
    for letter, const in REPOINT.items():
        text, k = re.subn(rf'(\b{letter} = lambda n, x, y, h, \*\*kw: L\.prop\(n, x, y, h, path_dir=)[A-Za-z.]+',
                          rf'\g<1>{const}', text)
        n += k
    text, k = re.subn(r'path_dir=(E\.AP|E\.XP|CPD|JP|CP|AP|XP)\b', 'path_dir=SP', text)
    n += k
    # 3. rename the sprites
    for old, new in sorted(RENAME.items(), key=lambda kv: -len(kv[0])):
        text, k = re.subn(rf'"{re.escape(old)}"', f'"{new}"', text)
        n += k
        text, k = re.subn(rf'"{re.escape(old)}\.png"', f'"{new}.png"', text)
        n += k
    # 4. tree kits go through ashenvale_engine, which only honours a full path when it sees a "/"
    text = re.sub(r'\("(stv_[a-z_]+)", (\d+)\)', r'(SP + "\1.png", \2)', text)
    text = text.replace('JP + "', 'SP + "')
    return text, n


def main():
    missing = targets_exist()
    if missing:
        raise SystemExit("these rename targets are not on disk yet:\n  " + "\n  ".join(missing))
    if "--check" in sys.argv:
        print(f"all {len(set(RENAME.values()))} rename targets exist")
        return
    total = 0
    for f in FILES:
        p = ROOT / f
        before = p.read_text(encoding="utf-8")
        after, n = rewire(before)
        if after != before:
            p.write_text(after, encoding="utf-8")
        print(f"  {f}: {n} substitutions")
        total += n
    print(f"{total} substitutions across {len(FILES)} modules")


if __name__ == "__main__":
    main()
