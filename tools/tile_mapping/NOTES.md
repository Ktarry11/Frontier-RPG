# Tile texture mapping - handoff notes

Context: mid-session context reset expected. This file exists so a fresh
Claude session (or Kyle) can pick this up without re-deriving anything.

## Session update 4 - Barrens subzone coverage audit, dead-code discovery,
## a real generator overlap bug, and a game-wide "stop using flat/bland
## crops" pass

**Discovered: the original Barrens subzone work (session 2 - Field of
Giants/Witchwing Terrace/Razorfen Approach) was built against
`world/zone_generator.py`'s `generate_the_barrens()`, which is DEAD CODE
- defined but never called from `create_all_zones()`, never reachable
in-game.** The live Barrens is the 5-zone split (`Northern Barrens`,
`Central Barrens`, `Crossroads`, `Southern Barrens`, `Camp Taurajo`,
generators in `tools/zone_expansion_generators.py`), which has its OWN
separate, different subzone list. Kyle caught this by asking "how much
of the Barrens is actually done" - a fair question the session-2 notes
didn't make clear. Audited every live zone's actual `.subzones` and
cross-checked against `SUBZONE_BIOME`:

| Live zone | Subzones | Had coverage before this session |
|---|---|---|
| Northern Barrens | Slug Fens, Harpy Roost | 0/2 |
| Central Barrens | Lushwater Oasis, The Forgotten Pools, Raider's Rest Oasis, Kolkar Plains | 0/4 |
| Southern Barrens | Field of Giants, Bael Modan, Razorfen Approach | 2/3 (accidental - see below) |
| Crossroads, Camp Taurajo | none | n/a |

Field of Giants and Razorfen Approach worked by coincidence - subzone
lookup keys off DISPLAY NAME only (`SUBZONE_BIOME` dict), not which zone
registered it, so the dead zone's mappings happened to still apply
wherever a live zone registers a subzone with the identical name.
**`SUBZONE_BIOME`'s header comment now explicitly documents this
name-only matching behavior** so a future session doesn't assume a
mapping is dead just because its "parent" zone is, or assume it's live
just because the name exists in the dict - always verify against the
actual live zone with `get_subzone_biome()`.

**`Witchwing Terrace` (session 2's third subzone biome, `savanna_cliff`)
has NO live target at all** - it only ever existed in the dead zone. Not
deleted (harmless if a zone with that name shows up later) but flagged
as doing nothing right now.

**Filled the 6 real coverage gaps this session**, reading each live
generator's actual code first rather than assuming the old dead-zone
subzone identities carried over:
- **Slug Fens** (Northern Barrens) - new biome `barrens_fen`. Northern
  Barrens' base fill uses `grass`/`dirt`/`shallow_water` tile_ids
  (different from Central/Southern's `dirt`-primary fill), so this biome
  covers those specific ids rather than mirroring the savanna family 1:1.
  Ground is the same swamp bog-floor tile as Wailing Caverns (open-air
  use, not just cave-coded - confirmed it reads fine either way). Water
  is the textured `water_ice` crop, not flat - generator rolls
  shallow_water on ~40% of tiles here, same density problem as Wailing
  Caverns.
- **Harpy Roost** (Northern Barrens) - reuses `savanna_cliff` (the
  now-otherwise-dead Witchwing Terrace biome, given a real home). Ground
  swaps to gray stone for "rocky terrain underfoot." **Had to add
  shallow_water/deep_water entries to `savanna_cliff` that weren't there
  before** - the original Witchwing Terrace context never needed water
  (dead zone, no water in its generator), but Northern Barrens' base fill
  rolls water game-wide including here; caught via render (flat blue
  squares on otherwise-textured stone) and fixed.
- **Lushwater Oasis / The Forgotten Pools / Raider's Rest Oasis**
  (Central Barrens) - new biome `savanna_pond`, one biome covers all
  three since they share identical concentric-ring generator code
  (deep_water core -> shallow_water -> grass fringe).
- **Kolkar Plains** (Central Barrens) - deliberately given NO distinct
  biome. The generator's own comment says this is open savanna placed
  only for encounter-table/lore purposes (Kolkar centaur camps), not
  distinct terrain - texturing it differently would misrepresent what's
  actually there. Falls through to parent `savanna`, correct as-is.
- **Bael Modan** (Southern Barrens) - new biome `bael_modan`, dwarf
  excavation ruins. Ground reuses the gray stone crop; `small_rocks`
  swaps to a REAL ruins-rubble prop from `resurrected_rpg/Props.png`
  (sandstone rubble, sourced back in session 1's asset inventory but
  never actually wired into any biome until now) instead of the generic
  boulder - genuine "excavated dig site" character, not a stand-in flag
  like Field of Giants' bones.

**Found and flagged (not fixed) a real geometry bug in
`generate_central_barrens()`:** the `Kolkar Plains` subzone rect
(x:190-290, y:20-220) partially overlaps `Raider's Rest Oasis`
(x:205-245, y:195-235) and is registered AFTER it in the subzone list.
`Tilemap.get_subzone_at()`'s own docstring says later-registered
subzones win on overlap, so ~62% of Raider's Rest Oasis (everything
except roughly y:220-235, the bottom sliver) gets silently shadowed by
Kolkar Plains and never resolves to `savanna_pond` - it renders as plain
`savanna` instead, incorrect for what should be pond ground/water there.
**This is a zone-generator geometry bug, not a texture-mapping bug** -
the `savanna_pond` mapping is correct and does work in the unshadowed
sliver (confirmed). Needs a decision in
`tools/zone_expansion_generators.py`: either shrink Kolkar Plains' rect
to not overlap the oasis, or re-order subzone registration so Raider's
Rest wins instead. Not touched this session - flagged for Kyle to decide
the right call rather than a Claude session silently picking one.

**Game-wide "stop defaulting to bland crops" pass.** Kyle pushed back
hard (rightly) after seeing a test-render screenshot that looked like
flat recolored blocks - even though that particular screenshot turned
out to be a real texture (the flat calm-pond water crop, just a color
he didn't expect), it surfaced a legitimate pattern: several crops in
use game-wide were technically "real texture" but visually almost
featureless, indistinguishable from a flat-color bug at a glance. Fixed
two specific offenders everywhere they appeared, not just where they'd
been noticed:
- **Flat calm-pond water** (`topdown_forest` (16,176,16,16), solid
  teal-green, zero internal detail) - swapped to the textured wavy
  `water_ice` crop in ALL 5 places it was used: `desert_oasis`,
  `savanna` (the plain zone-wide entry, not just savanna_pond),
  `savanna_bones`, `savanna_pond`, `cave_mossy`. Still a single static
  frame (not animated), so it stays "calm"/non-active per the original
  design intent - it just isn't boring to look at anymore.
- **Flat gray "generic rock" fill** (`undead_ground` (24,24,32,32),
  near-featureless solid gray with only edge detail) - swapped to a
  genuinely textured cobblestone crop with visible crack/grout detail
  from the SAME source sheet (`undead_ground` (244,344,24,24) - found by
  scanning the sheet programmatically for the highest-variance fully-
  opaque 32x32 region, several manual crop attempts hit transparent
  border/spike-decoration bleed before landing on a clean patch). This
  was the `stone`/`rock`/`cliff` tile_id in 18 separate places across
  `desert`, the whole `savanna` family (including the new session-4
  biomes), `grassland`, `decayed_forest`, `orgrimmar`, `bael_modan` - a
  single sed-style bulk replace since it was the exact same crop
  constant reused everywhere, not 18 separate hand-picks.
- Confirmed via render: Bael Modan's ruins floor, Valley of Trials'
  oasis pond, and general rock scatter across biomes all show real
  surface detail now instead of flat fill.
- **Not a "make everything busy" pass** - Kyle's actual ask was texture
  should be visible even on plain ground, not that every tile needs to
  be maximally detailed. Didn't touch anything that was already using a
  detailed crop (e.g. the Forgotten Memories grass/dirt tiles, tf_jungle,
  swamp bog floor were all already fine and untouched).

## Session update 3 - Wailing Caverns, Razorfen Kraul, Orgrimmar, and two
## real renderer bugs (visual-layer compositing + wall/floor contrast)

**New cave biomes: `cave_swamp` (Wailing Caverns), `cave_thornscrub`
(Razorfen Kraul).** Both were previously silently falling back to
`grassland`/DEFAULT_BIOME despite being real, built, portal-wired
dungeons (240x220 each, multi-boss, `is_cave=True`) - not a placeholder
gap, just never wired.
- `cave_swamp`: bog-floor ground from the `swamp` tile pack (unused by
  any biome until now - dark purple, olive-moss speckle, sourced but
  never wired per NOTES.md asset inventory), mossy green-brick walls
  (DampDungeons). Water uses the textured wavy `water_ice` crop, NOT the
  flat calm-pond crop used elsewhere - the calm-pond crop is solid teal
  with zero texture, fine as a sparse oasis accent but reads as an
  unmapped/debug color at the ~30% per-chamber water density this
  dungeon's generator actually rolls. Confirmed via render.
- `cave_thornscrub`: same dry-dirt/gray-rock/bramble palette as the
  Razorfen Approach overworld subzone it connects from, for continuity
  crossing from surface to dungeon. Bramble scatter (1,023 tiles,
  generator's own "signature feature") confirmed rendering after the
  visual-layer fix below.

**New biome: `orgrimmar`** (Orgrimmar, 200x200, 8 walled districts +
central plaza). Reuses the same `gen_red_sand`/`gen_red_rock` tinted
stand-ins as Durotar/Valley of Trials rather than a separate palette,
since Orgrimmar is built INTO the same red rock canyon per its own zone
description - consistent geology, not a jarring city dropped into desert.
Same "real limitation, not final art" flag as the rest of the desert
family.

**Bug fix 1 - visual layer was never read by the renderer at all.**
`ui/tilemap_renderer.py`'s per-tile draw loop checked
base/collision/interaction and picked one "winning" layer to draw -
`visual` was completely absent from that chain, not just deprioritized.
This meant every biome's decorative scatter placed via the visual layer
(flowers, grass_tuft, bramble/root bushes at low density, Durotar's
small_rocks) has been invisible game-wide since texturing was first
wired, not just for the new dungeons. Fixed by adding visual_tile to the
lookup, priority base < visual < collision < interaction.

**Bug fix 2 - visual-layer sprites rendered with a solid black box behind
them instead of blending into the ground.** Found via Kyle's screenshot
of Durotar (small_rocks scatter). Root cause: fixing bug 1 by picking
`visual` as the new "winning tile" whenever present meant the base
ground's draw call was skipped entirely for any tile with a visual-layer
decoration - the rock sprite's transparent margins showed the raw
viewport background color (dark gray `(20,20,20)`) instead of the actual
red-dirt ground underneath. The "one winning layer, draw only that" model
was correct for collision/interaction (a wall or NPC genuinely occupies
the whole tile) but wrong for visual (decorative scatter ON TOP of
ground, not a replacement for it).
**Real fix (not a one-off patch):** `render_tilemap` now always draws
base first (sprite or flat-color fallback), then composites
visual/collision/interaction sprites on top in priority order if each
layer actually has a tile_id set. This is correct compositing, not
another band-aid - confirmed via re-render, boulders/decorations now sit
cleanly on top of textured ground with proper alpha, zero black boxes,
across Durotar (regression-checked) and the new Razorfen Kraul brambles.
**This affects every biome with visual-layer scatter, i.e. most of the
game - if anything still shows a black-box artifact behind a decorative
sprite after pulling this fix, that's a NEW bug, not a recurrence of this
one.**

**Bug fix 3 - wall/cliff tiles were visually indistinguishable from open
ground in the whole red-rock family (desert, desert_oasis, orgrimmar).**
`gen_red_rock` (avg RGB (143,80,52)) and `gen_red_sand` (avg (164,90,50))
are only ~20 points apart in brightness/hue - a wall built from the rock
crop was disappearing into the sand floor next to it. Confirmed via
screenshot in Orgrimmar (the outer defensive wall was completely
invisible against the plaza). Fixed by generating a new stand-in variant,
`assets/tiles/generated/durotar_red_rock_dark.png` (~45% darker + 25%
desaturated, avg (80,51,39) - clearly a different/shadowed material,
still the same warm red-brown family, not a jarring color swap) and
repointing `wall`/`cliff` tile_ids specifically (NOT `stone`/`rock` -
those stay on the lighter natural-boulder variant, this is a
constructed-wall-vs-natural-terrain distinction) across `desert`,
`desert_oasis`, `orgrimmar` to the new `gen_red_rock_dark` sheet key.
Confirmed via render: Orgrimmar's district/outer walls, Razor Hill's
town walls both now read clearly against their floors. **Same technique
(darken+desaturate a stand-in, new sheet key, swap wall/cliff only) is
the template if any other biome's wall material turns out too close to
its floor - check average color first before assuming it's fine.**

**Also fixed this session (missed instances of the tree-crop bug from
session 2):** `desert` biome's own `bushes` entry (Durotar itself, the
single most-visited zone) and `desert_oasis`'s `bushes` entry both still
had the old broken `(284,253,69,130)` rect - session 2 fixed `savanna`/
`savanna_thornscrub`/`savanna_bones`/`cave_mossy` but missed these two.
Grepped the whole file afterward to confirm zero remaining instances -
all now `(310,235,40,145)`.

## Session update 2 - Barrens savanna biome + subzone-aware texturing

**New biome added: `savanna`** (The Barrens, Central/Northern/Southern
Barrens, Crossroads, Camp Taurajo). Ground is Forgotten Memories' tan
dirt-patch tile (same source sheet as grassland/mythical_forest/
decayed_forest, different crop - a dry-sprig variant, not the vivid green
blob). Tree/bushes reuse the bare gnarled tree (props_nature) since no
pack has a real acacia/savanna-tree asset - same real limitation as
Durotar's red-sand stand-in, flagged not hidden. Rock/cliff reuse the
neutral gray undead_ground crop, consistent with grassland/decayed_forest
(this predates the wall-contrast fix above and hasn't been re-examined
against it - undead_ground's gray reads fine against tan dirt, contrast
isn't an issue there the way red-on-red was).

**Subzone-aware texturing added** - this is infrastructure, not just a
Barrens content pass. Previously biome resolution was strictly whole-map
(`Tilemap.name` -> one biome_id, cached per-tilemap-object). Named
subzones (Field of Giants, Witchwing Terrace, Razorfen Approach, etc -
already registered via `Tilemap.add_subzone()` for the encounter-table
system) can now look different from their parent zone, not just have
different creature/prop scatter. Implementation:
- `world/tile_textures.py`: `SUBZONE_BIOME` dict (subzone display name ->
  biome_id) + `get_subzone_biome(tilemap, x, y)` helper. Falls through to
  `None` (parent biome wins) for any subzone not explicitly listed -
  registering a subzone for encounter-table purposes never silently
  changes its look.
- `ui/tilemap_renderer.py`: `_biome_for()` takes optional `x, y`, checks
  subzone override before falling back to the cached whole-map biome.

**Three subzone biome variants for Barrens sub-regions:**
- `savanna_bones` (Field of Giants) - kodo bone fields / silithid
  country. Ground/water/tree identical to plain `savanna` - only
  `small_rocks` differs, and even that is the SAME gray boulder crop used
  everywhere else as a stand-in, not real bone-pile or insect-mound art.
  Checked props_nature, undead, topdown_forest - nothing fits either
  read. Kyle confirmed: keep the stand-in scatter, don't fake real bone
  art, revisit if a real pack turns up. **Next real limitation to swap
  out, same tier as the red-sand/rock stand-ins.**
- `savanna_cliff` (Witchwing Terrace) - base ground swaps fully to gray
  stone, plateau reads as bare stone underfoot. Real asset, no flag.
- `savanna_thornscrub` (Razorfen Approach) - ground swaps to Forgotten
  Memories' dark-green grass variant (already used for decayed_forest),
  visibly darker/denser, foreshadows Razorfen Kraul below (which now
  shares the same palette family, see session 3 above). Real asset, no
  flag.

**Also fixed session 2:** the `tree`/`bushes` crop in `props_nature` had
a bad rect - `(284, 253, 69, 130)` clipped into a neighboring purple
coral sprite's non-transparent pixels, rendering trees with a solid
black/purple box behind them. Corrected to `(310, 235, 40, 145)`.
**Session 3 found this same bad rect was still present in 2 more places
this fix missed - see session 3 notes above. If touching any biome's
tree/bushes entry, grep the whole file for `284, 253, 69, 130` first to
make sure no stale instances remain.**

## READ THIS FIRST - current state as of latest session

**IMPORTANT: "The Barrens" as a single zone is DEAD CODE.** If you see
that name in `world/zone_generator.py` (`generate_the_barrens()`),
it's defined but never called - not reachable in-game. The LIVE Barrens
is 5 separate zones (`Northern Barrens`, `Central Barrens`, `Crossroads`,
`Southern Barrens`, `Camp Taurajo`), generators in
`tools/zone_expansion_generators.py`. Always check which one you're
actually looking at before assuming subzone/biome work applies - see
session 4 notes above for the full story of how this caused confusion.

**Fully textured and verified (code-level coverage check passes, base +
visual + collision layers all confirmed compositing correctly, water/
rock crops upgraded from flat-fill to real texture per session 4):**
- Valley of Trials (biome `desert_oasis`)
- Durotar (biome `desert`)
- Razor Hill (biome `desert`) - walls contrast against ground (session 3)
- Echo Isles (biome `tropical`)
- 8 named caves tied to starter zones (The Den, Burning Blade Coven,
  Drygulch Ravine, Skull Rock, Tiragarde Hold, Dustwind Cave, Sunken
  Temple Grotto, Zalazane's Hollow) - biome `cave_mossy`
- Undercity - biome `undead`
- Ashenvale (West/East/Astranaar/Zoram Strand/Splintertree Post) - biome
  `mythical_forest`
- Silverpine + Tirisfal undead-starting zones - biome `decayed_forest`
- 4 generic cave palette variants (cave_warm/sick/cold/dark) via
  caves_rpgw
- Northern Barrens, Central Barrens, Southern Barrens, Crossroads, Camp
  Taurajo (all LIVE zones) - biome `savanna` as base ground
- Wailing Caverns - biome `cave_swamp` (session 3)
- Razorfen Kraul - biome `cave_thornscrub` (session 3)
- Orgrimmar - biome `orgrimmar`, 8 districts + plaza + outer walls
  (session 3)

**Live subzone coverage (session 4 audit + fill-in) - this is the
accurate picture, ignore any session-2-era claim about Barrens subzones
being done, that was against the dead zone:**
| Live zone | Subzone | Biome | Status |
|---|---|---|---|
| Northern Barrens | Slug Fens | `barrens_fen` | done, session 4 |
| Northern Barrens | Harpy Roost | `savanna_cliff` | done, session 4 |
| Central Barrens | Lushwater Oasis | `savanna_pond` | done, session 4 |
| Central Barrens | The Forgotten Pools | `savanna_pond` | done, session 4 |
| Central Barrens | Raider's Rest Oasis | `savanna_pond` | **mapping correct but PARTIALLY SHADOWED by a Kolkar Plains overlap bug - see session 4 notes, unfixed** |
| Central Barrens | Kolkar Plains | (none - intentional) | correct as-is, not a gap |
| Southern Barrens | Field of Giants | `savanna_bones` | done (originally session 2, confirmed still live) |
| Southern Barrens | Bael Modan | `bael_modan` | done, session 4, real ruins-rubble art |
| Southern Barrens | Razorfen Approach | `savanna_thornscrub` | done (originally session 2, confirmed still live) |

**Dead mapping, do nothing with it unless a new zone needs it:**
`Witchwing Terrace` -> `savanna_cliff` in `SUBZONE_BIOME` has no live
target - only ever existed in the dead standalone Barrens zone.

**Known real limitations, not bugs (flagged in code comments):**
- Durotar/Valley of Trials/Razor Hill/Orgrimmar's red ground+rock is a
  TINTED STAND-IN (`assets/tiles/generated/durotar_red_sand.png` /
  `durotar_red_rock.png` / `durotar_red_rock_dark.png`), not genuine
  art. Swap target: change the `gen_red_*` SHEETS entries + the
  `desert`/`desert_oasis`/`orgrimmar` BIOME_TILES rects if a real pack
  shows up.
- Field of Giants' bone-pile/silithid-mound scatter is the same gray
  boulder crop used everywhere else as generic rock scatter, not real
  bone/insect-mound art. Swap target: `savanna_bones` biome's
  `small_rocks` entry.

**Known bug, not yet fixed (flagged, not silently patched around -
needs a design decision, see session 4 for detail):** Central Barrens'
`Kolkar Plains` subzone rect overlaps `Raider's Rest Oasis` and (per
`Tilemap.get_subzone_at()`'s own later-wins-on-overlap rule) shadows
~62% of it, so most of that oasis renders as plain savanna instead of
pond. Fix belongs in `tools/zone_expansion_generators.py`
(`generate_central_barrens()`), either shrink Kolkar Plains' rect or
reorder subzone registration - not a `tile_textures.py` fix.

**Not yet visually screenshot-verified (should work per code coverage
check, not eyeballed):** Drygulch Ravine, Tiragarde Hold, Dustwind Cave,
Zalazane's Hollow.

**Not started:** Ratchet (port town), Zeppelin Tower (airship interior).
These still render in flat tiles.py colors. **Boulder Lode Mine is
portal-wired (currently mis-wired under Northern Barrens instead of its
own stated parent Central Barrens - a portal_manager.py bug, not
discussed in depth this session, flagged for awareness) and named in a
loot table but has no generator function at all yet - that's a
zone-building gap, not a texture gap, separate task from anything in
this file.**

**Kalimdor coverage status per Kyle's "mostly done before Eastern
Kingdoms" goal:** every LIVE, portal-wired Kalimdor zone/dungeon now has
real texture mapping except Ratchet and Zeppelin Tower (both small,
single-purpose town/interior maps) and Boulder Lode Mine (not built yet,
not a texture task). Undercity/Tirisfal/Silverpine are technically
Eastern Kingdoms geography but were already done in an earlier session
before this distinction mattered - not re-scoped out.


**Props found and cropped but NOT wired into any generator yet** (i.e.
confirmed-good image crops exist, but nothing in zone_generator.py places
them - this needs generator-level work, not just registry mapping):
- DampDungeons torch/lantern post (`assets/tiles/damp_dungeons/
  DungeonDecorations.png`, crop roughly x=0-34,y=256-335)
- Resurrected RPG sandstone obelisk (`assets/tiles/resurrected_rpg/
  Props.png`, crop x=16-48,y=16-95) - earmarked for Ashenvale ruins per
  Kyle's "beautiful ruins" ask, and a desaturated version for Silverpine's
  "decayed ruins" ask - neither done yet.

## Assets compiled this session (see "Asset inventory" further down for
full original list) - newly added:
- `assets/tiles/mini_dungeon/` - small stone floor tile, low priority
- `assets/tiles/swamp/` - purple/green bog tileset (60 individual 32px
  tiles), not wired into any biome yet
- `assets/backgrounds/` - ALL 7 combat-background scene-art packs, now
  fully extracted and copied in (previously only 3 of 7 were extracted):
  dark_dungeon, desert, fire_dungeon, ice_dungeon, jungle, mossy_forest,
  mountain. These are NOT tilesets - full painted/isometric scene
  illustrations (JPG, numbered like screenshots, some with time-of-day
  variants). Intended use: combat screen backdrop images, one full image
  per encounter type, not cropped into tiles. Nothing in the codebase
  reads from this folder yet - no combat-background rendering system
  exists. This is pure asset staging for a future feature.


## What's done

1. **`ui/sprite_loader.py`** - sheet loading/caching, crisp + smooth scale
   variants. Fully built, tested logic (loads once, caches crops, fails
   soft to None on missing file/bad rect). Not yet wired into the renderer.
2. **`world/tile_textures.py`** - the tile_id -> texture registry. Maps
   zone name -> biome -> per-tile-id (sheet, rect, smooth-flag). Real
   coordinates found via the scanner below + manual visual confirmation.
   NOT YET WIRED into `ui/tilemap_renderer.py` - that's the next step.
3. **`tools/tile_mapping/find_flat_tiles.py`** - scans a sheet for
   locally-tileable, non-transparent NxN blocks (low color variance = good
   flat/tileable texture) and can dump a labeled contact sheet PNG for
   fast visual review. Usage:
   ```
   python3 tools/tile_mapping/find_flat_tiles.py <sheet.png> <block_size> [out.png]
   ```
   Contact sheets from this session were saved to
   `/home/claude/work/contact_sheets/` (outside the repo, in the sandbox -
   regenerate with the command above if needed, they're cheap to rebuild).

## What's NOT done yet (next steps in order)

1. **Wire `tile_textures.py` into `ui/tilemap_renderer.py`.** Currently
   `render_tilemap()` always calls `get_tile_color()` for flat rects.
   Need to: look up `zone.name` + `zone.is_cave` -> biome via
   `tile_textures.get_biome_for_zone()`, then for each tile_id try
   `tile_textures.get_texture_entry()` -> if found, call
   `sprite_loader.get_tile_sprite()` (or `_smooth` per the flag) and blit
   the returned Surface instead of `pygame.draw.rect`. Fall back to the
   existing flat-color draw if the sprite lookup returns None at any
   step (missing biome, missing tile_id, missing/bad sheet).
2. **Bump `tile_size` from 16 to 32** in both:
   - `ui/tilemap_renderer.py` `__init__(self, tile_size=16)` default
   - `ui/screens/overworld_screen.py` line ~23 `TilemapRenderer(tile_size=16)`
   Or better: import `TILE_SIZE` from `world/tile_textures.py` in both
   places instead of hardcoding, so there's one source of truth.
   Reasoning for 32 (not 16, not native ~170): see "resolution decision"
   below.
3. **Test render each wired biome** in isolation (headless pygame,
   `SDL_VIDEODRIVER=dummy`, same pattern used for the combat screen
   screenshots earlier this session) before calling it done - don't trust
   the mapping blind, actually render Durotar/Undercity/a cave and look.
4. **Extend `BIOME_TILES` coverage.** Current entries are intentionally
   partial (only grass/dirt/stone/water-ish, not every one of the 24 tile
   IDs in `world/tiles.py`). Trees/props (fm_trees, fm_props,
   undead_objects, Resurrected RPG ruins) aren't wired as *tiles* yet -
   they're better suited to the `visual`/`collision` layer overlay (props
   scattered on top of base ground) rather than base tile_id swaps. That's
   a follow-up pass once base ground textures are confirmed working.
5. **Unconfirmed biomes still needing real asset sourcing** (currently
   render as flat color, deliberately not faked):
   - Port town (Ratchet)
   - Urban/capital stone (Orgrimmar)
   - Airship interior (Zeppelin Tower)
   - ~~Savanna + oasis (Barrens zones, Camp Taurajo, Crossroads)~~ - DONE,
     see top-of-file session update. Tropical (Echo Isles) was also
     already done prior to that note being written here.

## Resolution decision (tile_size 16 -> 32)

Forgotten Memories tileset (`assets/tiles/forgotten_memories/TileSet.png`)
is high-res painterly art, native tile size ~170px (confirmed by cropping
and visually counting grid boundaries - NOT a 16px grid like the other
packs). Tested downscaling a sample tile to 16px vs 32px vs 48px:
- 16px: shape/texture reads as mush, basically a flat color blob
- 32px: shape, dirt edge, and grass texture all still read clearly
- Chose 32px. At viewport 800x600 this means ~25x19 tiles visible on
  screen (vs ~50x37 at the old 16px) - still plenty of room for an
  overworld view, not a zoomed-in mess.
16px-native packs (undead, caves_rpgw, water_ice) upscale cleanly 2x to
32px with nearest-neighbor - no quality loss, pixel art scales up fine.

## Asset inventory (confirmed usable, copied into assets/tiles/)

- `assets/tiles/forgotten_memories/` - TileSet.png (grass/dirt blobs,
  multiple color variants, cliff edges, bridges), WaterTiles-6frames.png
  (animated water+ice, ponds+coastlines), Trees.png + Props.png (color
  variants: orange/teal/gold/pine/green willow + matching bushes/stumps).
  Flat pixel-art style. **Primary pack for grassland/forest biomes.**
- `assets/tiles/undead/` - Ground_rocks.png (ash-gray ground, dark rock
  cliff/spike edges, pebble texture patches), Objects.png,
  Objects_separately/ (pre-cropped props). **Undercity / undead capital.**
- `assets/tiles/caves/` - MainLev2.0.png (caves_rpgw pack) - multi-biome
  color-tinted cave floor (green/blue-gray/purple-wine/dark-ash variants,
  same shapes different palette). **Dungeon variety without new art.**
- `assets/tiles/water_ice_sheet.png` (from Kyle's `Water_.png` upload) -
  top-down wave-pattern water + ice/crystal variants + fish + a couple
  rock/gem props. Confirmed top-down (not isometric).
- `assets/tiles/generic_16px/` (from `separate.zip`, 609 individually
  cropped 16px tiles) - generic seamless material fills, no autotile
  edges. Copied in but SUPERSEDED by Forgotten Memories for ground use -
  keep as a fallback/filler source only, not the primary pick.

## Rejected / not used

- `isometric_tileset.zip` / `.7z` - genuinely isometric (diamond tiles),
  wrong projection for this top-down renderer. Skipped per Kyle's
  decision (was mid-discussion on this when the savanna-palette question
  got overtaken by the Forgotten Memories/Resurrected RPG uploads, which
  solved the grassland/forest gap a better way - isometric pack is still
  sitting unused in uploads if a savanna palette is needed later, but
  Forgotten Memories' dirt-patch tiles likely cover that need instead).
- `seamless_patterns.zip` - raw Pixaki editor project file (source +
  cache/keyframes), not a usable exported asset.
- `Textures-16.png` / `textures_02_08_25.png` - same content as
  `separate.zip`, just as uncut sheets. Redundant, separate.zip's
  pre-cropped tiles are easier to work with directly.
- Resurrected RPG pack (`Grass.png`, `Wall.png`, `Props.png`, `Plants.png`)
  - painterly style (soft-shaded, not flat pixel art), would clash if
  mixed directly onto Forgotten Memories' flat-shaded ground. Decision:
  use ONLY for ruins/structure props (sandstone obelisks/statues/walls),
  not for ground tiles. Earmarked for Ashenvale's "beautiful ruins" (used
  as-is) and Silverpine's "decayed ruins" (same assets, desaturated/
  darkened in-code or via a duplicate darker crop - not yet done).
  Trees.png/Grass 2 layer.png from this pack are NOT currently mapped to
  anything - the Forgotten Memories tree variants covered the mythical/
  decayed forest need instead, so these are spare/unused for now.

## Zone name -> biome quick reference (see tile_textures.py ZONE_BIOME/CAVE_BIOME for authoritative version)

grassland: Valley of Trials, Durotar, Razor Hill
mythical_forest: Ashenvale West/East, Astranaar, Zoram Strand, Splintertree Post
decayed_forest: Silverpine North/South, The Sepulcher, Fenris Isle, Deathknell, Eastern/Western Tirisfal, Brill
undead: Undercity
cave_warm/sick/cold/dark: the 8 dungeon names, see CAVE_BIOME dict
unmapped (flat color): Echo Isles, Northern/Central/Southern Barrens, Crossroads, Camp Taurajo, Ratchet, Orgrimmar, Zeppelin Tower

## Session update: red-sand fix (Valley of Trials / Durotar)

Kyle flagged (with a real WoW screenshot reference) that Valley of Trials
was rendering green - traced to the ZONE GENERATOR, not just a missing
texture: `generate_valley_of_trials()` had `zone.fill("grass", "base")`
and description text calling it a "verdant valley", a leftover from
before the zone's real geography/palette was pinned down. Fixed:

- `world/zone_generator.py`: Valley of Trials now `zone.fill("sand", ...)`,
  description updated to "sheltered red-sand valley ringed by rock".
  Visual-layer flowers/grass_tuft scatter (both zones) replaced with
  small_rocks - those tile_ids don't belong on sand.
- Durotar's generator was already correctly filling "sand" with accurate
  description text - only its stray `grass_tuft` visual scatter (1.5%
  density) needed the same small_rocks swap.
- New `"desert"` biome added to `world/tile_textures.py` (separate from
  `"grassland"`, which still exists for whichever zone actually wants
  green later). Valley of Trials/Durotar/Razor Hill now point at
  `"desert"` instead of `"grassland"`.
- **No source pack had genuine red-sand/rust-rock texture** (Forgotten
  Memories' dirt patch is muddy brown, not red). Generated stand-ins by
  luminance-remapping existing clean crops into a red-orange ramp:
  `tools/tile_mapping/` scripts weren't used for this part - it was done
  inline, see the tint code pattern (sample source crop -> compute
  luminance -> remap into a dark/light color ramp -> save PNG). Baked
  output lives in `assets/tiles/generated/durotar_red_sand.png` (from a
  128x128 crop of fm_tileset's dirt patch at 1344,378) and
  `durotar_red_rock.png` (from undead_ground's pebble crop at 24,24,
  normalized then remapped darker/rustier). Registered in
  `tile_textures.py` SHEETS as `gen_red_sand`/`gen_red_rock`.
- **This is a stand-in, not a purpose-made asset.** If Kyle finds/uploads
  a real red-sand tileset later, swap the `"desert"` biome's sheet_key
  from `gen_red_sand`/`gen_red_rock` to the real pack and delete the
  generated PNGs - the biome/zone wiring doesn't need to change, just the
  SHEETS entry and BIOME_TILES rect.
- Verified by actually rendering Durotar headless (SDL_VIDEODRIVER=dummy)
  after the fix - real red-sand ground with darker rust rock outcrops,
  confirmed against the reference screenshot's palette by eye.

Razor Hill was NOT touched - it's already 100% "stone"+"wall" (a built
town), never had a grass assumption to begin with.

in-session as "8 zones", corrected after checking `create_all_zones()` in
world/zone_generator.py which pulls from 3 generator modules: the base
ZoneGenerator class, tools/zone_expansion_generators.py, and
tools/ashenvale_silverpine_fenris_generators.py + tools/orgrimmar_undercity_expansion.py)

Valley of Trials, Durotar, Razor Hill, Echo Isles, Ratchet, Orgrimmar,
Zeppelin Tower, Deathknell, Eastern Tirisfal, Western Tirisfal, Undercity,
Northern Barrens, Central Barrens, Crossroads, Southern Barrens,
Camp Taurajo, Ashenvale West, Ashenvale East, Astranaar, Zoram Strand,
Splintertree Post, Silverpine North, Silverpine South, The Sepulcher,
Brill, Fenris Isle, Ragefire Chasm, Plague Depths, Blackfathom Deeps,
Grom's Rest, Widow's Lair, Shadowfang Keep, Ambermill Tower,
Shadowpine Altar
