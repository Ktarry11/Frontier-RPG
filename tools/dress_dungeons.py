#!/usr/bin/env python3
"""Furnish every dungeon interior. Writes data/dungeons/dressing.json.

    PYTHONPATH=. python3 tools/dress_dungeons.py [--apply] [zone ...]

Kyle, 7 Nov: "dress up The Dungeons. Give them proper tiles and PROPER props."

THE MEASUREMENT THAT PROMPTED IT. Props per 1,000 walkable tiles, across the 58
interiors: 3.7 to 22.5, against 135 for Rocky Pass, the one that was dressed by
hand. Stromgarde Keep is 4.1 - one prop per 243 walkable tiles, which in play is
a single barrel alone in a room you could hold a parade in.

And the props were never the problem: assets/tiles/dungeon_props has 144 of
them - braziers, cages, ore carts, sarcophagi, broken columns, lava pools, steam
vents, shackle frames, spider nests. They were sitting unused while the rooms
were empty.

WHERE FURNITURE GOES. Not uniformly at random, which reads as litter. Real rooms
put their contents against the walls and keep the middle clear, so the pass
works off two different sets of tiles:

  WALL LINE   walkable tiles with a solid neighbour. Takes the bulk of the
              dressing - crates, racks, braziers, rubble, bones. Spaced along
              the wall rather than clustered, so a room gets a furnished edge
              instead of one heap.

  CENTREPIECE walkable tiles with a clear radius around them, in rooms big
              enough to deserve a focal point. Takes the large pieces - an
              altar, a throne, a cart, a fallen pillar - one per room, never
              two.

NOTHING IS SOLID, and nothing is placed on a tile that already matters: portals,
NPCs, chests, existing landmarks and every trash-spawn tile are all excluded, with
a margin. The dressing cannot block a corridor, cannot bury a quest giver and
cannot stand on the tile a pack spawns on.
"""
import argparse
import json
import os
import random
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

OUT = ROOT / "data" / "dungeons" / "dressing.json"
DP = "assets/tiles/dungeon_props/"
CP = "assets/tiles/cave_props/"

#: Target pieces per 1,000 walkable tiles. Rocky Pass is 135 and is hand-made;
#: 55 is a furnished room without pretending a generator can match a person.
TARGET_PER_1K = 55

#: Share of the budget that goes against the walls rather than into the middle.
WALL_SHARE = 0.82

#: biome -> (wall pieces, centrepieces). Weighted by repetition in the list.
#: Every name is checked against disk at startup; a typo fails loudly rather
#: than silently dressing a room with nothing.
TABLES = {
    "cave_dark": (
        ["rf_supply_crates", "rf_tool_rack", "rf_ore_cart", "skull_pile", "broken_column",
         "rf_fallen_pillar", "bones_1", "bones_2", "bones_3", "rf_shackle_frame",
         "rf_prison_cage", "candelabra", "spirit_brazier", "rf_trogg_nest"],
        ["rf_sacrificial_altar", "sarcophagus", "rf_obsidian_throne", "ritual_circle",
         "rf_summoning_circle", "banquet_table"]),
    "cave_keep": (
        ["weapon_rack", "rf_supply_crates", "broken_column", "candelabra", "rf_prison_cage",
         "rf_shackle_frame", "banquet_table", "bbc_bookshelf", "bbc_chains", "bbc_candelabra"],
        ["bbc_throne", "banquet_table", "sarcophagus", "wizard_desk", "temple_archway"]),
    "cave_mossy": (
        ["den_glow_mushrooms", "broken_column", "rf_fallen_pillar", "bones_2", "vot_reeds",
         "vot_fallen_log", "rf_trogg_nest", "temple_column"],
        ["temple_archway", "ritual_circle", "rf_fallen_pillar"]),
    "cave_sick": (
        ["bbc_fel_barrels", "bbc_fel_crystals" if False else "rf_void_crystals", "skull_pile",
         "bbc_skull_pile", "bbc_chains", "bbc_cage", "bones_4", "cocoon_victim"],
        ["bbc_summon_circle", "bbc_altar", "twilight_altar", "bbc_fel_pylon"]),
    "cave_webbed": (
        ["web_tangle", "web_curtain", "spider_nest", "spider_husk", "cocoon_victim",
         "bones_1", "den_egg_cluster", "den_chitin_husk"],
        ["spider_nest", "cocoon_victim", "den_egg_cluster"]),
    "cave_thornscrub": (
        ["vot_thornbush", "rf_trogg_tent", "rf_trogg_totem", "vot_hide_rack", "bones_3",
         "vot_palisade", "den_nest" if False else "rf_trogg_nest", "vot_fallen_log"],
        ["rf_trogg_totem", "vot_war_drum", "vot_fire_pit"]),
    "cave_swamp": (
        ["vot_reeds", "bones_2", "den_glow_mushrooms", "vot_fallen_log", "rf_fallen_pillar"],
        ["ritual_circle", "temple_archway"]),
    "cave_fire": (
        ["rf_lava_stalagmite", "rf_obsidian_spikes", "rf_steam_vent", "bbc_fel_brazier",
         "rf_ore_cart", "rf_tool_rack", "skull_pile", "bbc_red_stalagmites"],
        ["rf_lava_pool", "rf_obsidian_throne", "bbc_fel_bonfire", "rf_golem_husk"]),
    "cave_ice": (
        ["crystal_1", "crystal_2", "crystal_3", "bones_1", "broken_column", "rf_fallen_pillar"],
        ["rf_void_crystals", "ritual_circle"]),
    "cave_crystal": (
        ["crystal_1", "crystal_2", "crystal_3", "rf_void_crystals", "den_glow_mushrooms",
         "broken_column"],
        ["rf_void_crystals", "ritual_circle", "temple_archway"]),
    "cave_flooded_ruins": (
        ["broken_column", "rf_fallen_pillar", "temple_column", "vot_reeds", "bones_2",
         "rf_supply_crates"],
        ["temple_archway", "ritual_circle", "sarcophagus"]),
}
#: Anything whose biome is not in TABLES falls back to this.
DEFAULT = "cave_dark"

#: A zone's own cave biome tag -> table key, where the names differ.
ALIASES = {"cave_lava": "cave_fire", "cave_molten": "cave_fire", "cave_frozen": "cave_ice",
           "cave_crystalline": "cave_crystal", "cave_web": "cave_webbed",
           "cave_undead": "cave_dark", "cave_bone": "cave_dark",
           "cave_ragefire": "cave_fire", "cave_warm": "cave_dark",
           "cave_demonic": "cave_sick", "cave_canyon": "cave_thornscrub",
           "cave_dustwind": "cave_dark", "cave_troll_ruins": "cave_mossy",
           "cave_grotto": "cave_flooded_ruins", "cave_sunken": "cave_flooded_ruins",
           "cave_cold": "cave_ice"}

#: Background pack -> table key. THIS is the fallback, not "grassland".
#:
#: CAVE_BIOME covers 24 of the 58 interiors. The other 34 - Stromgarde and
#: Drywhisker among them - are not in it at all, so get_biome_for_zone hands
#: back the OVERWORLD biome, and the first run of this pass dressed a ruined
#: human keep and a kobold mine from the same default table because both came
#: back "grassland". The background pack does cover all 58 (that was the 7 Nov
#: subzone work), it is already the right shape - what does this room LOOK like
#: - and it is kept correct by qa_combat_backgrounds. So it is the better key.
PACK_TABLE = {"dark_dungeon": "cave_dark", "keep": "cave_keep",
              "mossy_dungeon": "cave_mossy", "fire_dungeon": "cave_fire",
              "ice_dungeon": "cave_ice", "crystal": "cave_crystal",
              "nautical": "cave_flooded_ruins", "jungle": "cave_mossy",
              "mountain": "cave_dark", "blighted": "cave_sick",
              "desert": "cave_dark", "savanna": "cave_thornscrub"}


def _exists(name):
    for d in (DP, CP):
        if (ROOT / d / f"{name}.png").exists():
            return d + f"{name}.png"
    return None


def _check_tables():
    missing = []
    for biome, (wall, mid) in TABLES.items():
        for n in set(wall) | set(mid):
            if not _exists(n):
                missing.append(f"{biome}/{n}")
    return missing


def _aspect(path):
    from PIL import Image
    with Image.open(ROOT / path) as im:
        return im.width / im.height


def dress_zone(zone, biome, seed):
    """-> list of pieces for one interior."""
    rng = random.Random(f"{zone.name}:{seed}")
    W, H = zone.width, zone.height

    walk = [[zone.is_walkable(x, y) for y in range(H)] for x in range(W)]
    walkable = [(x, y) for x in range(W) for y in range(H) if walk[x][y]]
    if not walkable:
        return []

    # Tiles already spoken for, with a margin so nothing crowds them.
    taken = set()
    for lm in (getattr(zone, "landmarks", []) or []):
        ax, ay = int(lm.get("anchor_x", 0)), int(lm.get("anchor_y", 0))
        for dx in range(-3, 4):
            for dy in range(-3, 4):
                taken.add((ax + dx, ay + dy))
    # A spawn is (x, y, name, level) - x and y FIRST. I read it as (?, x, y) on
    # the first pass and got "Syndicate Watchman" where a coordinate should be.
    # And `fixed_spawns` is a BOOL on some zones and a list on others, so this
    # has to survive both rather than assume.
    for attr in ("trash_spawns", "fixed_spawns", "authored_trash_spawns"):
        val = getattr(zone, attr, None)
        if not isinstance(val, (list, tuple)):
            continue
        for sp in val:
            try:
                if isinstance(sp, dict):
                    sx, sy = sp["x"], sp["y"]
                else:
                    sx, sy = sp[0], sp[1]
                sx, sy = int(sx), int(sy)
            except (TypeError, ValueError, KeyError, IndexError):
                continue
            for dx in range(-2, 3):
                for dy in range(-2, 3):
                    taken.add((sx + dx, sy + dy))
    for x in range(W):
        for y in range(H):
            if zone.get_tile(x, y, "interaction"):
                for dx in range(-2, 3):
                    for dy in range(-2, 3):
                        taken.add((x + dx, y + dy))

    def solid_neighbours(x, y):
        n = 0
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                px, py = x + dx, y + dy
                if not (0 <= px < W and 0 <= py < H) or not walk[px][py]:
                    n += 1
        return n

    wall_line, open_floor = [], []
    for (x, y) in walkable:
        if (x, y) in taken:
            continue
        n = solid_neighbours(x, y)
        if 1 <= n <= 4:
            wall_line.append((x, y))
        elif n == 0:
            open_floor.append((x, y))

    budget = max(6, round(len(walkable) / 1000.0 * TARGET_PER_1K))
    n_wall = int(budget * WALL_SHARE)
    n_mid = budget - n_wall

    wall_names, mid_names = TABLES.get(biome, TABLES[DEFAULT])

    pieces, used = [], set()

    def place(x, y, name, height):
        path = _exists(name)
        if not path:
            return False
        w = max(1, round(height * _aspect(path)))
        pieces.append({"sprite": path, "x": x - w // 2, "y": y - height + 1,
                       "w": w, "h": height})
        for dx in range(-2, 3):
            for dy in range(-2, 3):
                used.add((x + dx, y + dy))
        return True

    # Walls first, spaced: shuffle then skip anything too near a piece already down.
    rng.shuffle(wall_line)
    for (x, y) in wall_line:
        if len(pieces) >= n_wall:
            break
        if (x, y) in used:
            continue
        place(x, y, rng.choice(wall_names), rng.choice((3, 3, 4, 4, 5)))

    # Centrepieces: only where there is room for one, and never two in a huddle.
    rng.shuffle(open_floor)
    mid = 0
    for (x, y) in open_floor:
        if mid >= n_mid:
            break
        if (x, y) in used:
            continue
        clear = all(0 <= x + dx < W and 0 <= y + dy < H and walk[x + dx][y + dy]
                    for dx in (-3, 0, 3) for dy in (-3, 0, 3))
        if not clear:
            continue
        if place(x, y, rng.choice(mid_names), rng.choice((5, 6, 6, 7))):
            mid += 1
            for dx in range(-9, 10):
                for dy in range(-9, 10):
                    used.add((x + dx, y + dy))
    return pieces


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("zones", nargs="*")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--seed", default="7nov")
    args = ap.parse_args()

    missing = _check_tables()
    if missing:
        print("  prop names with no file on disk:")
        for m in missing:
            print(f"    {m}")
        return 1

    # GENERATE FROM BARE ZONES. create_all_zones() applies the dressing this
    # tool writes, so a second run would measure rooms that are already
    # furnished and furnish them again - it did, and Rocky Pass went from 528
    # props to 726 on the second pass. Move the file aside first so the zones
    # come up undressed and the output is always the whole answer rather than
    # an increment on an unknown starting point.
    stashed = None
    if OUT.exists():
        stashed = OUT.read_text()
        OUT.unlink()
    try:
        from world.zone_generator import create_all_zones
    except Exception:
        if stashed is not None:
            OUT.write_text(stashed)
        raise
    from world.tile_textures import get_biome_for_zone
    from world.combat_backgrounds import resolve_place

    zones = create_all_zones()
    want = set(args.zones)
    out, rows, skipped = {}, [], []
    for name, z in zones.items():
        if not getattr(z, "is_cave", False):
            continue
        if want and name not in want:
            continue
        tag = get_biome_for_zone(name, is_cave=True) or ""
        if tag in ALIASES or tag in TABLES:
            biome = ALIASES.get(tag, tag)
        else:
            folder = resolve_place(name, None, True)[0]
            biome = PACK_TABLE.get(folder, DEFAULT)
        before = len(getattr(z, "landmarks", []) or [])
        walk0 = sum(1 for x in range(z.width) for y in range(z.height) if z.is_walkable(x, y))
        # ALREADY FURNISHED? LEAVE IT. Rocky Pass was dressed by hand at 135 per
        # 1k and this pass cheerfully added 198 more pieces on top, taking it to
        # 186 - a pass meant to fix empty rooms making the one good room worse.
        # Anything at or above target is somebody's deliberate work.
        if before / max(walk0, 1) * 1000 >= TARGET_PER_1K:
            skipped.append((name, before, walk0, before / max(walk0, 1) * 1000))
            continue
        pieces = dress_zone(z, biome, args.seed)
        if not pieces:
            continue
        out[name] = pieces
        walk = sum(1 for x in range(z.width) for y in range(z.height) if z.is_walkable(x, y))
        rows.append((name, biome, before, len(pieces), walk,
                     (before + len(pieces)) / max(walk, 1) * 1000))

    if args.apply:
        # A whole-game run replaces the file; a named-zone run edits the old one.
        existing = {}
        if want and stashed:
            try:
                existing = json.loads(stashed)
            except json.JSONDecodeError:
                existing = {}
        existing.update(out)
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(existing, indent=0, sort_keys=True))

    total = sum(len(v) for v in out.values())
    print(f"  {len(out)} interiors, {total} pieces, target {TARGET_PER_1K} per 1k walkable\n")
    print(f"  {'interior':32}{'biome':20}{'had':>5}{'+new':>6}{'per 1k after':>14}")
    for name, biome, before, added, walk, after in sorted(rows, key=lambda r: r[5]):
        print(f"  {name[:31]:32}{biome[:19]:20}{before:>5}{added:>6}{after:>14.1f}")
    if not args.apply and stashed is not None:
        OUT.write_text(stashed)        # report-only must not disarm the game
    for name, n, walk, d in skipped:
        print(f"  {name[:31]:32}{'(already furnished)':20}{n:>5}{'-':>6}{d:>14.1f}")
    print("\n  written to " + str(OUT.relative_to(ROOT)) if args.apply
          else "\n  (report only; pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
