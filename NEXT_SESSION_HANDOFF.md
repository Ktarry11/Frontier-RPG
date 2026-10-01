# Next Session: Full Tile Revamp

## Where we left off

This session was a pure asset-cropping pass — no wiring into the actual
game yet. 256 individual assets sit cropped and verified clean in
`crop_work2/` (outside the main `frontier_rpg/` tree, so not in this
zip's `frontier_rpg/` folder — see the top-level `crop_work2/` directory
in this zip instead):

- `crop_work2/props/` (50) — crates, barrels, market stalls, wells,
  torches, fences, anvils, animal pens. Real town scatter/detail, which
  every rebuilt town this session (Razor Hill, Crossroads, Ratchet, Camp
  Taurajo, Orgrimmar) is still missing — they read as a bit empty/plaza-like
  between buildings because this prop kit didn't exist yet when they were built.
- `crop_work2/terrain1/` (50) — Durotar, Echo Isles, general Barrens,
  Town/Road, Rock/Mountain/Cliff, Water ground textures.
- `crop_work2/terrain_barrens/` (50) — Barrens-specific: Open Savanna,
  Scrubland & Mesa, Watering Holes & Oasis, Ancient Forest Remnants,
  Roads & Trails.
- `crop_work2/roads/` (50) — 7 road styles (Dirt Trail, Packed Trade
  Road, Town Cobblestone, Stone-Paved Plaza, River-Stone Crossing,
  Ruined/Overgrown Road, Desert Caravan Track), each with straight/
  corner/T-junction/crossroads/dead-end variants. This is the real
  connective road tileset Kyle's been wanting instead of the flat single
  "path" base tile every zone currently uses for every road ever painted.
- `crop_work2/terrain_dungeon/` (56) — Oasis, Cave, Keep/Fortress,
  Dungeon floor/wall tiles. Real material for dungeon interiors
  (Ragefire Chasm, Wailing Caverns, Blackfathom Deeps, Broodspiral, etc.)
  which currently reuse generic "stone"/"rock" placeholder tiles
  regardless of what the dungeon actually is.

None of this has been copied into `assets/`, referenced by any tile ID,
or wired into any zone generator yet. It's a clean, categorized library
sitting ready to use.

## The actual next task (Kyle's words)

> "The next main thing will be to do a full revamp of tiles. Since
> eventually I want to start expansion again soon. But I want the zones
> we have (like all 55 of them) to be beautiful before we start growing
> to new zones."

So: **stop adding new zones, go back through all 53 (Kyle said "55",
close enough - see `create_all_zones()` in `world/zone_generator.py` for
the real live count) already-existing zones and revamp their tiles**
using this new library, before any further expansion. Roughly, in order
of what'll move the needle most:

1. **Roads**: every zone's roads are currently one flat "path" base tile
   painted via `_paint_road`/`_carve_path`. The new 50-tile road set has
   real straight/corner/junction pieces per road style - swapping these
   in is probably the single biggest visual upgrade available, since
   roads run through literally every zone.
2. **Ground textures**: zones currently use a small set of base tiles
   (`grass`, `sand`, `dirt`, `stone`) painted with random scatter. The
   terrain sheets have 5-10x that variety per biome (Durotar alone has
   10 dedicated ground variants vs. the current 1-2). Swapping these in
   zone-by-zone would be the second-biggest upgrade.
3. **Dungeon/cave interiors**: currently generic rock/stone regardless of
   theme. The Oasis/Cave/Keep/Dungeon sheet gives real per-dungeon floor
   variety (crystal caves, ritual floors, collapsed wall sections, etc.)
   that could differentiate Ragefire Chasm from Wailing Caverns from
   Blackfathom Deeps instead of them all looking the same.
4. **Town/scatter props**: the 50-item prop kit (crates, wells, market
   stalls, fences, torches) fills the empty plaza feeling every rebuilt
   town currently has between buildings - flagged repeatedly this session
   as a known gap ("scatter details later").

## Real technical considerations for next session (not yet solved)

- **Tile rendering pipeline**: check how `world/tiles.py` and
  `ui/tilemap_renderer.py` currently resolve a base-layer tile ID to a
  drawn sprite - probably need new tile IDs (or a variant system) rather
  than replacing existing ones outright, so old zones don't silently
  break if a generator still references `"grass"` by name.
- **Autotiling for roads**: the road tileset's real value is in its
  corner/junction pieces, which only work if the generator knows
  which piece to place based on neighboring road tiles (a straight-only
  placement wastes 40 of the 50 road tiles). This needs actual logic,
  not just a tile swap - worth scoping as its own conversation before
  diving in.
- **Per-zone mapping**: which terrain-1 vs. terrain-barrens tiles apply
  to which zones needs a real decision pass (e.g. does Durotar use
  terrain1's Durotar set, or does every red-dirt zone from both sheets
  get merged into one pool?).

## Housekeeping if picking this up fresh
- Full asset library also referenced in prior session transcripts as
  `crop_work/` (buildings, 51 sprites, already wired into
  `assets/buildings/` and used throughout) vs. `crop_work2/` (this
  session's terrain/props/roads, NOT yet copied into `assets/`).
- Every town rebuild this session (Razor Hill, Crossroads, Ratchet, Camp
  Taurajo) and the Orgrimmar district expansion are already complete and
  verified - don't redo those, they're done. This next phase is tiles/
  terrain/props only, layered on top of what's already built.
