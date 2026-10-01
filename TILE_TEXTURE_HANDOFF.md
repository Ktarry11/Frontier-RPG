# Tile Texturing — Handoff for Next Session (Cities + Barrens)

## The real starting discovery (read this first)

The game already has a **fully-built texture system** wired into the
renderer — `world/tile_textures.py` does biome resolution + per-tile
sheet/rect lookups, `ui/tilemap_renderer.py` calls it every frame and
falls back to `world/tiles.py`'s flat color only when a lookup returns
`None`. This was NOT a missing feature. The actual problem: `assets/tiles/`
was completely empty. Every one of the ~17 source packs the registry
references (Forgotten Memories, undead, caves, jungle, dungeons, etc.)
was designed for but never actually delivered as files. That's why
every zone in the game has been rendering as flat colored squares this
whole time.

**Before doing anything new, check `assets/tiles/<biome>/` for files
that already exist and `world/tile_textures.py`'s `SHEETS` dict for
entries that already point at real paths** — don't assume a biome is
untouched just because a zone looks flat; some of the fallback chain
might be one broken sheet reference away from working.

## What's actually done (this session, scoped to Kyle's ask: "Durotar,
towns, caves")

- **Durotar / Razor Hill** (`desert` biome) and **Valley of Trials**
  (`desert_oasis` biome) — full real ground texture set, real mountain/
  cliff art for walls, real cacti/scrub scatter props.
- **Orgrimmar** (`orgrimmar` biome) — ground shares Durotar's palette
  (same canyon per the zone's own lore), `stone` gets real paved-
  courtyard art, `wall` gets real fortress-wall + boulder-wall art.
- **The Den** (`cave_mossy` biome) and **Drygulch Ravine**
  (`cave_canyon` biome) — real cave floor/wall art, genuinely distinct
  from each other (they used to be pixel-identical, which was the
  actual "can't tell path from wall" complaint).
- **12 other cave biomes are still untouched** (Ragefire Chasm,
  Blackfathom Deeps, etc.) — deliberately out of scope this session,
  not forgotten.

All real assets used came from two places:
1. `crop_work2/` (a much earlier session's asset-cropping pass) —
   `terrain1/`, `terrain_barrens/`, `terrain_dungeon/`, `roads/`,
   `props/`. 256 pre-cropped individual PNGs, never wired into the game
   until this session.
2. A fresh 20-sprite Durotar-specific drop Kyle uploaded mid-session
   (`durotar_20_unique_png_sprites.zip`) — real ground variants, 5 real
   cacti/scrub props, 6 mountain/cliff tiles.

## The real technical pattern to copy for Barrens/cities

### 1. Files are individual crops, not sheets — `rect` is always the whole image

Every file added this session is a single tight-cropped PNG (not a
multi-tile sheet), so every `BIOME_TILES` entry uses
`(0, 0, actual_width, actual_height)` as the rect — the crop covers the
whole file. **Get the real pixel dimensions before writing an entry**:

```python
from PIL import Image
Image.open("assets/tiles/<biome>/<file>.png").size
```

Don't guess dimensions or reuse another file's rect - a mismatched rect
either clips the sprite or leaves empty space.

### 2. Real texture variety, not one tile per material (Kyle caught this
   mid-session — "I don't want one uniform tile across the board")

`get_texture_entry(biome_id, tile_id, x=None, y=None)` now accepts
EITHER a single `(sheet_key, rect, smooth)` tuple OR a **list** of them.
When a list and `(x, y)` are both given, it picks a variant
deterministically from tile position (`(x*7 + y*13) % len(variants)` -
same tile always renders the same way, no per-frame flicker, no RNG
dependency). Every biome touched this session uses real variant lists
for `sand`/`dirt`/`stone`/`rock` (2-5 real textures each) specifically
because a single fixed texture produces a visible grid-repeat pattern
once actually rendered at scale — verify this yourself by rendering a
zone and looking at the ground, not just checking the registry code.

**When wiring Barrens/city biomes: use real variant lists from the
start, don't ship a single-texture version and fix it after Kyle
notices the repeat pattern (that's what happened this session).**

### 3. Background-removal is sometimes required — check every RGBA file's
   corner alpha before trusting it

The 6 scatter props (cacti/shrubs) in the new Durotar drop were
technically RGBA files but had a BAKED-IN opaque white background (not
real transparency) plus a leftover black cropping-artifact bar. Real
transparency was added with a proper pass, not assumed from the file
mode:

```python
import numpy as np
arr = np.array(Image.open(path).convert("RGB")).astype(int)
r,g,b = arr[:,:,0], arr[:,:,1], arr[:,:,2]
brightness = (r+g+b)/3
saturation = np.maximum(np.maximum(r,g),b) - np.minimum(np.minimum(r,g),b)
is_white_bg = (brightness > 195) & (saturation < 25)
is_black_bar = (brightness < 35) & (saturation < 20)
mask = ~(is_white_bg | is_black_bar)
# then binary_erosion(mask, iterations=1) to kill the anti-aliased
# halo ring left at the edge, THEN build the alpha channel and
# tight-crop to real content bounds.
```

**Always check `np.array(im)[0,0]` (or a few corner pixels) on any new
RGBA scatter prop before wiring it in** - `im.mode == "RGBA"` does NOT
mean the background is actually transparent.

### 4. Verify every new mapping actually resolves to a file that exists,
   before rendering

```python
from world.tile_textures import get_texture_entry
import os
entry = get_texture_entry(biome, tile_id, x, y)
path, rect, smooth = entry
assert os.path.exists(path)  # do this for every tile_id x every biome touched
```

This session ran this check across 196 lookups before doing any visual
render - catches a typo'd SHEETS key or a forgotten `cp` instantly,
instead of finding out via a silent flat-color fallback that looks like
"the biome just isn't textured" rather than "one specific mapping is
broken."

### 5. Actually render and look, don't just trust the registry

Use a throwaway headless render script (`SDL_VIDEODRIVER=dummy`, a fake
camera object, `renderer.render_tilemap()` to a `pygame.Surface`, save
to PNG, view it) for every biome touched. This is how the "one uniform
tile" bug got caught in the first place - the registry code looked
correct, the rendered zone didn't.

## What's NOT done yet (the actual next-session scope)

- **Barrens** (`savanna`/whatever the real ZONE_BIOME entry is for
  Central/Northern/Southern Barrens, Crossroads, Ratchet, Camp
  Taurajo) - check `ZONE_BIOME` in `world/tile_textures.py` for the
  exact biome_id each zone resolves to before assuming they share one
  biome entry.
- **Every other city** beyond Orgrimmar - Undercity is a real one to
  check; `tools/orgrimmar_undercity_expansion.py` also has a
  `UndercityMassive._build_section` with the exact same "fake
  perimeter wall" pattern that got removed from Orgrimmar's
  `_build_district` a couple sessions back - worth checking if that
  ever got fixed for Undercity too, or if it's still there.
- **12 other cave biomes** - Ragefire Chasm, Wailing Caverns,
  Blackfathom Deeps, etc. Check `CAVE_BIOME` in `world/tile_textures.py`
  for the full list and which biome_id each currently resolves to -
  several likely still reference the same missing packs everything else
  did before this session.
- Whatever's left of the ~17 missing source packs referenced elsewhere
  in `BIOME_TILES` that this session didn't touch (tropical/jungle,
  swamp, lava, undead, naga, seabed, etc.) - same "designed but never
  delivered" gap, just not yet audited zone-by-zone.

## Assets available but not yet copied into `assets/tiles/`

`crop_work2/` (at the project root, sibling to `frontier_rpg/`) still
has material that hasn't been used:
- `crop_work2/roads/` (50 files) - real connective road pieces
  (straights/corners/T-junctions/crossroads/dead-ends across 7 styles:
  Dirt Trail, Packed Trade Road, Town Cobblestone, Stone-Paved Plaza,
  River-Stone Crossing, Ruined/Overgrown Road, Desert Caravan Track).
  Every zone in the game currently paints roads with one flat "path"
  tile via `_paint_road`/`_carve_path` - these would need real
  autotiling logic (picking the right corner/junction piece based on
  neighboring road tiles) to pay off, not just a texture swap. Worth
  scoping as its own conversation before diving in - a straight-only
  placement wastes 40 of the 50 pieces.
- `crop_work2/props/` (50 files) - crates, barrels, market stalls,
  wells, torches, fences, anvils, animal pens. Every rebuilt town this
  project has done reads a bit empty/plaza-like between buildings -
  this is the fix, just never wired in.
- `crop_work2/terrain_barrens/` (50 files) - real Barrens-specific
  ground (Open Savanna, Scrubland & Mesa, Watering Holes & Oasis,
  Ancient Forest Remnants, Roads & Trails). This is very likely the
  right source for the Barrens texturing pass specifically - check it
  before assuming new art is needed.
