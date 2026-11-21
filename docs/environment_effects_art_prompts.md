# Environment effects: art prompts (sheets EFX1 to EFX10)

Kyle, 21 Nov 2026: "I do like the sunbeams you're doing in the sky too. Are visual things like that in zones easy to
do? They give a sense of depth", then "So how about we build 2 full sheets for environmental effects please. We can add
some of them in to old zones etc", then "Actually, let's go for about 10 sheets. Think of what we have for world zones,
and while you build I'll gather art. Don't hold back, whatever we don't make now is backlogged and cleared later."

**Status (21 Nov 2026): delivered and sliced the same day** (`tools/slice_effects_sheets.py`, 150 effects to
`assets/effects/`). The renderer draws light, shade, scrolling layers and particles (`tilemap.light`, `.shade`,
`.weather`, `.particles`); Dawnhaven is the first to use them. See `docs/art_status.md` for every sheet.

## What these are, and how the game uses them

Four kinds of thing, and each sheet is one kind, because each kind needs its own background:

| Kind | Sheets | Background | How it's drawn |
|---|---|---|---|
| **Light overlays**: full-screen washes of light | EFX1, EFX2, EFX10 | pure black `#000000` | added over the screen (black adds nothing), like the sky's sun rays today |
| **Shade overlays**: full-screen washes of shadow | EFX3 | pure white `#FFFFFF` | multiplied over the screen (white changes nothing) |
| **Weather and atmosphere layers**: seamless tiles that scroll | EFX4, EFX5 | pure black `#000000` | tiled across the screen, scrolled and added, at two speeds for depth |
| **Sprites**: small single things the game moves | EFX6 to EFX9 | flat magenta `#FF00FF` | keyed out and moved by code (drift, sway, spin, fade) |

A zone picks what it wants: Dawnhaven might take autumn god rays, a canopy dapple and falling red leaves; the Barrens
a noon glare, heat haze and a dust drift; Tirisfal a plague fog and the odd crow. The light overlay already works
(`TilemapRenderer._draw_light`, `tilemap.light`). The shade overlays, the scrolling layers, the particles and the
flyover shadows are small renderer additions, built when the sheets land.

**Sizes.** The overlay and layer sheets are 2048x1366 in a 3 x 3 grid, each panel about 682 x 455. Soft light and fog
stretch to the screen without showing it. The sprite sheets are 2048x1366 in a 6 x 4 grid, cells about 341 x 341.

**Slices** go to `assets/effects/` (overlays to `assets/effects/light/`, `shade/`, `weather/`, sprites to
`assets/effects/particles/` and `assets/effects/life/`), named in the lists under each sheet.

**References to attach:** for the overlays, `assets/tiles/sky/backdrop/sun_rays.png` (the look to match: soft,
painterly, no hard edges). For the sprites, any two props from the same art set, e.g.
`assets/tiles/azshara/props/az_crimson_bush.png` and `assets/tiles/sky/props/sk_cloud_wisp.png`.

---------------------------------------------------------------------
## SHEET EFX1: SUNLIGHT (light overlays, black background)

```
Generate ONE image, 2048x1366, a 3 columns x 3 rows grid = 9 separate panels, each panel about 682x455. Every panel is a FULL-SCREEN LIGHT OVERLAY for a top-down 2D fantasy RPG: only light, painted as soft glowing shapes on a pure #000000 black background. Black means "no light"; brighter means more light. Each panel's light stays inside its own panel and fades to pure black well before the panel's edges, with a thin pure black gutter between panels. No objects, no ground, no trees, no characters, no text, no labels, no grid lines. Painterly and very soft, like the attached sun rays reference: no hard edges, no lens-flare rings, no stars, no sparkles, nothing that reads as a picture of anything, only light falling into a scene seen from above at about 45 degrees.

Panels, row by row, left to right:
1 AUTUMN GOD RAYS: broad warm golden shafts of sunlight slanting in from the top-left corner, as if through gaps in a forest canopy, five or six beams of different widths, strongest at the top-left and fading out by the middle of the panel. Warm gold and amber.
2 JUNGLE SHAFTS: narrow steep near-vertical beams of humid green-gold light from the top edge, many thin beams close together, hazy, as through a dense jungle canopy.
3 DESERT NOON GLARE: a wide bright white-yellow wash across the whole top third, bleaching down to black at the bottom, with a faint brighter bloom near the top centre. Harsh, hot.
4 DAWN: long low soft pink-and-gold shafts coming in nearly horizontal from the left edge, wide and gentle.
5 DUSK: long low deep orange and red shafts coming in nearly horizontal from the right edge, fewer and wider than dawn, heavy and warm.
6 OVERCAST: a very faint, even, pale grey-white light from the whole top edge, no beams at all, just a soft top-down brightness fading down the panel.
7 GOLDEN HOUR CANOPY: three or four long thin beams of rich gold light slanting from the top-right, crossing most of the panel, with soft dust-hazed edges, as through high branches.
8 WINTER SUN: pale blue-white low light from the top-left, cold and thin, one wide soft wash with a few faint long beams in it.
9 HIGH SUN BLOOM: a single soft round bloom of white-gold light in the top-right corner with a broad gentle glow spreading from it, no rings, no spikes.
```

Slices: `light_autumn_rays`, `light_jungle_shafts`, `light_desert_glare`, `light_dawn`, `light_dusk`, `light_overcast`,
`light_golden_canopy`, `light_winter_sun`, `light_sun_bloom`.

---------------------------------------------------------------------
## SHEET EFX2: MAGIC, NIGHT AND UNDERGROUND LIGHT (light overlays, black background)

```
Generate ONE image, 2048x1366, a 3 columns x 3 rows grid = 9 separate panels, each panel about 682x455. Every panel is a FULL-SCREEN LIGHT OVERLAY for a top-down 2D fantasy RPG: only light, painted as soft glowing shapes on a pure #000000 black background. Black means "no light"; brighter means more light. Each panel's light stays inside its own panel and fades to pure black well before its edges, with a thin pure black gutter between panels. No objects, no ground, no characters, no text, no labels, no grid lines. Painterly and very soft, like the attached reference: no hard edges, no sparkles, no stars, only coloured light.

Panels, row by row, left to right:
1 MOONLIGHT: cool silver-blue shafts slanting from the top-left, soft and wide, a night-time forest light.
2 FEL GLOW: a sickly bright green glow rising from the bottom edge and the two lower corners, as if the ground itself is lit from below by corruption, fading upward to black by the top third.
3 PLAGUE MIASMA: a low murky yellow-green glow lying along the whole bottom third in uneven patches, like light caught in a poisonous fog close to the ground.
4 ARCANE SHIMMER: soft violet and teal glow creeping in along all four edges of the panel in uneven ribbons, leaving the middle dark, as if old magic hums at the edges of sight.
5 CAVE SKYLIGHT: one narrow shaft of pale daylight falling from a point near the top centre down to a soft pool of light in the middle of the panel, everything else black.
6 CRYSTAL CAVE: three or four soft blooms of teal, blue and pale violet light near the edges and corners, like glowing crystals just out of view.
7 EMBER UNDERGLOW: a deep orange and red glow rising from the bottom edge, flickering-looking in its unevenness, as if lava or a great fire lies just below the scene.
8 HOLY COLUMN: a tall soft column of warm white-gold light in the centre of the panel, brightest in the middle, gently widening at the bottom.
9 AURORA GLOW: a broad soft band of green and teal light across the top quarter, wavy and uneven, like the glow of an aurora reflected on snow below it.
```

Slices: `light_moonlight`, `light_fel_glow`, `light_plague_miasma`, `light_arcane_shimmer`, `light_cave_skylight`,
`light_crystal_cave`, `light_ember_underglow`, `light_holy_column`, `light_aurora_glow`.

---------------------------------------------------------------------
## SHEET EFX3: SHADE (shade overlays, WHITE background)

```
Generate ONE image, 2048x1366, a 3 columns x 3 rows grid = 9 separate panels, each panel about 682x455. Every panel is a FULL-SCREEN SHADE OVERLAY for a top-down 2D fantasy RPG: only shadow, painted on a pure #FFFFFF white background. White means "no shadow"; darker or coloured means shade, and it will be MULTIPLIED over the game. Keep every panel mostly light: the darkest areas should be a mid grey or a mid colour, never pure black. Each panel's shade stays inside its own panel with a thin pure white gutter between panels. No objects, no characters, no text, no labels, no grid lines. Soft and painterly, no hard edges.

Panels, row by row, left to right:
1 CANOPY DAPPLE: soft grey leaf-shadow dappling across the whole panel, irregular blotches of shade from leaves high above with light gaps between, evenly spread, SEAMLESSLY TILEABLE on all four sides.
2 JUNGLE CANOPY: darker green-grey shade heavy at all four edges and lighter in the middle, as under a thick jungle roof, with a few soft leaf shapes in the shade.
3 CLOUD SHADOWS: two or three very large soft blue-grey blobs of shadow with lots of white between them, like clouds passing over a sunny plain, SEAMLESSLY TILEABLE on all four sides.
4 CAVE VIGNETTE: a soft dark grey vignette closing in from all four edges, clear white in the centre, for underground maps.
5 NIGHT: an even soft dusky blue-grey over the whole panel, a little darker toward the edges.
6 HAUNTED DARK: a deep uneven grey-violet vignette with soft tendrils of shade reaching in from the edges toward the middle, for cursed and haunted places.
7 STORM GLOOM: a dark slate grey-blue gradient heavy across the top half, fading to white at the bottom, like a storm sky darkening the land.
8 UNDERWATER: a teal-blue shade over everything, deeper at the edges and the bottom, lighter at the top centre.
9 DUST HAZE: a warm sandy brown-orange tint over the whole panel, stronger at the edges, like a sandstorm's brown-out.
```

Slices: `shade_canopy_dapple`, `shade_jungle_canopy`, `shade_cloud_shadows`, `shade_cave_vignette`, `shade_night`,
`shade_haunted`, `shade_storm_gloom`, `shade_underwater`, `shade_dust_haze`.

---------------------------------------------------------------------
## SHEET EFX4: WEATHER (scrolling layers, black background)

```
Generate ONE image, 2048x1366, a 3 columns x 3 rows grid = 9 separate panels, each panel about 682x455. Every panel is a SEAMLESSLY TILEABLE WEATHER LAYER for a top-down 2D fantasy RPG, painted in light colours on a pure #000000 black background (black is see-through; the layer is added over the game and scrolled). EVERY panel must tile seamlessly on all four sides: anything crossing an edge continues exactly on the opposite edge. A thin pure black gutter between panels. No ground, no objects, no characters, no text, no grid lines. Seen from above at about 45 degrees, so falling things read as short slanted streaks or soft flakes.

Panels, row by row, left to right:
1 LIGHT RAIN: thin pale blue-white rain streaks, sparse, all slanting the same way down to the lower-left at about 70 degrees, short, varied lengths, some fainter than others.
2 DOWNPOUR: the same rain, three times as dense, longer streaks, with a faint grey sheen between them.
3 LIGHT SNOW: soft round white snowflakes of a few sizes, sparse, evenly scattered, some slightly blurred.
4 BLIZZARD: dense white snow driven sideways in streaks to the left, with soft white gusts between them.
5 SANDSTORM: warm tan and orange streaks of blown sand and dust driven sideways to the right, with soft dusty clouds between them.
6 ASHFALL: grey and charcoal ash flakes of a few sizes drifting down, sparse, a few with a faint orange glowing edge.
7 DRIZZLE MIST: a very fine pale grey speckle of tiny droplets with soft misty patches, barely there.
8 SEA SPRAY: fine white spray and droplets blown sideways to the left in loose bursts, as off breaking waves.
9 FALLING PETALS AND LEAVES: a light scatter of small soft red, orange and gold leaf shapes drifting, varied angles, sparse.
```

Slices: `wx_rain_light`, `wx_downpour`, `wx_snow_light`, `wx_blizzard`, `wx_sandstorm`, `wx_ashfall`, `wx_drizzle`,
`wx_sea_spray`, `wx_leaf_drift`.

---------------------------------------------------------------------
## SHEET EFX5: FOG, MIST AND MOTES (scrolling layers, black background)

```
Generate ONE image, 2048x1366, a 3 columns x 3 rows grid = 9 separate panels, each panel about 682x455. Every panel is a SEAMLESSLY TILEABLE ATMOSPHERE LAYER for a top-down 2D fantasy RPG, painted in light colours on a pure #000000 black background (black is see-through; the layer is added over the game and drifts slowly). EVERY panel must tile seamlessly on all four sides. A thin pure black gutter between panels. No ground, no objects, no characters, no text, no grid lines. Soft and painterly, like the attached reference.

Panels, row by row, left to right:
1 GROUND FOG: long low soft wisps of pale grey-white fog, stretched horizontally, with plenty of black between them.
2 FOG BANK: thick rolling soft fog, mostly covering the panel, with a few darker gaps, pale grey-white.
3 SWAMP MIST: low wisps of mist tinted a murky green-grey, uneven and clinging.
4 PLAGUE FOG: thick sickly yellow-green fog in heavy rolling clumps, with a few darker gaps.
5 WATERFALL MIST: fine white vapour in soft rising puffs, brighter in patches, as near falling water.
6 STEAM: soft white steam plumes rising in scattered columns from below, curling at the top.
7 GOLDEN MOTES: tiny soft glowing gold specks of a few sizes, sparse, like dust in a sunbeam or magic in the air.
8 FIREFLIES: small soft glowing green-yellow points with a faint halo each, sparse, scattered at different brightnesses.
9 VOID WISPS: thin drifting ribbons of dim violet light and a few violet specks, sparse, eerie.
```

Slices: `atm_ground_fog`, `atm_fog_bank`, `atm_swamp_mist`, `atm_plague_fog`, `atm_waterfall_mist`, `atm_steam`,
`atm_golden_motes`, `atm_fireflies`, `atm_void_wisps`.

---------------------------------------------------------------------
## SHEET EFX6: PARTICLES I, NATURE (sprites, magenta background)

```
Generate ONE sprite sheet image, 2048x1366, a 6 columns x 4 rows grid = 24 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single small object, centred in its own cell with a wide margin, drawn LARGE enough to fill about half its cell (it will be shrunk in the game), not touching its neighbours or the image edge. No ground, no shadow under anything, no text, no labels, no grid lines, no magenta or pink anywhere in the art. Painterly semi-realistic WoW Classic style matching the attached references: soft dark outline, simple readable shapes, lit from the top-left. These are PARTICLES the game will spin and drift across the screen, so each is seen flat, from directly above.

Sprites, row by row, left to right:
Row 1, LEAVES: 1 a red maple leaf. 2 a gold aspen leaf, round. 3 an orange oak leaf. 4 a dry brown curled leaf. 5 a long crimson elven leaf with a gold vein, slender and elegant. 6 a green summer leaf.
Row 2, PETALS AND SEEDS: 7 a pink blossom petal. 8 a white petal. 9 a golden glowing tree-blossom petal with a faint warm glow. 10 a dandelion seed with its fluffy white parachute. 11 a small winged maple seed. 12 a soft yellow pollen puff.
Row 3, SNOW, RAIN, WATER: 13 a large white snowflake, six-armed, soft. 14 a small soft round snowflake. 15 a single blue-white raindrop, elongated. 16 a raindrop splash, a little crown of droplets seen from above. 17 a ripple, two thin concentric rings of pale water. 18 a small spray of white water droplets.
Row 4, FIRE, ASH, DUST: 19 a glowing orange ember spark. 20 a grey ash flake with a burning orange edge. 21 a charcoal ash flake, plain. 22 a soft tan dust puff. 23 a small swirl of blown sand. 24 a white bird feather.
```

Slices: `p_leaf_maple`, `p_leaf_aspen`, `p_leaf_oak`, `p_leaf_dry`, `p_leaf_elven`, `p_leaf_green`; `p_petal_pink`,
`p_petal_white`, `p_petal_gold`, `p_seed_dandelion`, `p_seed_maple`, `p_pollen`; `p_snowflake`, `p_snow_soft`,
`p_raindrop`, `p_rain_splash`, `p_ripple`, `p_spray`; `p_ember`, `p_ash_burning`, `p_ash`, `p_dust_puff`,
`p_sand_swirl`, `p_feather_white`.

---------------------------------------------------------------------
## SHEET EFX7: PARTICLES II, MAGIC AND SMOKE (sprites, magenta background)

```
Generate ONE sprite sheet image, 2048x1366, a 6 columns x 4 rows grid = 24 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single small object or puff, centred in its own cell with a wide margin, drawn LARGE enough to fill about half its cell, not touching its neighbours or the image edge. No ground, no shadow, no text, no labels, no grid lines, no magenta or pink anywhere in the art. Painterly WoW Classic style matching the attached references. Glows are painted as OPAQUE soft coloured blobs with a bright core, never transparent, so nothing shows the magenta through them. Seen flat from above.

Sprites, row by row, left to right:
Row 1, MOTES: 1 a blue arcane mote, a bright core in a soft blue glow. 2 a gold holy mote. 3 a violet void mote. 4 a green fel mote. 5 a teal mana spark with four tiny points. 6 a white star twinkle, soft four-pointed.
Row 2, CREATURE LIGHTS AND SPORES: 7 a firefly, a tiny dark body with a green-yellow glowing tail. 8 a pale blue will-o'-the-wisp, a soft flame-shaped light. 9 a fel spore, a spiky green pod with a faint glow. 10 a puff of plague spores, a little yellow-green cloud. 11 a glowing gold seed with a tiny leaf. 12 a drop of glowing amber sap.
Row 3, SMOKE AND STEAM: 13 a grey smoke puff. 14 a black smoke puff. 15 a white steam puff. 16 a small soft white cloud wisp. 17 a green poison gas puff. 18 a violet shadow wisp, curling.
Row 4, SPARKS AND SHARDS: 19 a crackling white-blue lightning spark. 20 a sharp glinting crystal shard, pale blue. 21 a soap-bubble, round with a light highlight. 22 a cluster of three small bubbles. 23 a floating gold blood elf rune glyph, a simple elegant curved sigil, glowing. 24 a black raven feather.
```

Slices: `p_mote_arcane`, `p_mote_holy`, `p_mote_void`, `p_mote_fel`, `p_mana_spark`, `p_star_twinkle`; `p_firefly`,
`p_wisp_light`, `p_spore_fel`, `p_spore_plague`, `p_seed_glow`, `p_sap_drop`; `p_smoke_grey`, `p_smoke_black`,
`p_steam`, `p_cloud_small`, `p_gas_poison`, `p_shadow_wisp`; `p_spark_lightning`, `p_shard_crystal`, `p_bubble`,
`p_bubbles`, `p_rune_gold`, `p_feather_black`.

---------------------------------------------------------------------
## SHEET EFX8: AMBIENT LIFE AND FLYOVER SHADOWS (sprites, magenta background)

```
Generate ONE sprite sheet image, 2048x1366, a 6 columns x 4 rows grid = 24 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single thing (or one small flock drawn as one sprite), centred in its own cell with a wide margin, not touching its neighbours or the image edge. No ground, no text, no labels, no grid lines, no magenta or pink anywhere in the art. Painterly WoW Classic style matching the attached references.

These are AMBIENT LIFE the game sends across a map: things seen from DIRECTLY ABOVE, flying or swimming, wings spread, heading to the RIGHT. Rows 1 to 3 are the animals themselves, small and simple. Row 4 is their SHADOWS on the ground: solid flat soft-edged dark grey silhouettes (not black, a mid-dark grey), no detail at all, as cast on the ground by something flying high overhead.

Sprites, row by row, left to right:
Row 1, BIRDS: 1 a V-shaped flock of five geese, from above. 2 a single black crow, wings spread. 3 a white seagull, wings spread. 4 a vulture, wide wings spread, from above. 5 a small flock of four bright jungle parrots, red, blue and yellow. 6 a raven, wings spread, ragged feathers.
Row 2, SMALL FLIERS: 7 an orange monarch butterfly, wings open. 8 a blue butterfly, wings open. 9 a dragonfly, iridescent green-blue. 10 a pale moth, wings open. 11 a flock of six small bats. 12 a small swarm of bees, a loose cluster of tiny dots and blurs.
Row 3, ON AND IN WATER: 13 a duck swimming, from above. 14 a white swan swimming, from above. 15 a small fish just under the surface, from above, a dark shape with a tail. 16 a school of six small silver fish, from above. 17 a large dark fish shadow under water, from above. 18 a lily pad with a small frog on it, from above.
Row 4, FLYOVER SHADOWS (flat soft mid-grey silhouettes, no detail): 19 the shadow of a large bird of prey, wings spread. 20 the shadow of a flock of small birds. 21 the shadow of a wyvern, bat wings spread, long tail. 22 the shadow of a great dragon, wings spread wide, filling most of the cell. 23 the shadow of a zeppelin, a long rounded hull with a small gondola. 24 the shadow of a griffin, feathered wings and a lion's tail.
```

Slices: `life_geese`, `life_crow`, `life_gull`, `life_vulture`, `life_parrots`, `life_raven`; `life_monarch`,
`life_butterfly_blue`, `life_dragonfly`, `life_moth`, `life_bats`, `life_bees`; `life_duck`, `life_swan`,
`life_fish`, `life_fish_school`, `life_fish_big`, `life_lily_frog`; `shadow_hawk`, `shadow_flock`, `shadow_wyvern`,
`shadow_dragon`, `shadow_zeppelin`, `shadow_griffin`.

---------------------------------------------------------------------
## SHEET EFX9: WATER AND GROUND EFFECTS (sprites and tiles, magenta background)

```
Generate ONE sprite sheet image, 2048x1366, a 6 columns x 4 rows grid = 24 separate cells, each about 341x341. Flat pure #FF00FF magenta background everywhere. Each cell holds ONE thing, centred with a wide margin, not touching its neighbours or the image edge. No text, no labels, no grid lines, no magenta or pink anywhere in the art. Painterly WoW Classic style matching the attached references, camera from above at about 45 degrees for the plumes and bursts. Water and steam are painted OPAQUE (soft white and blue), never transparent, so nothing shows the magenta through them.

Cells, row by row, left to right:
Row 1, WATER SURFACE (cells 1 to 3 are SQUARE TILES that fill their whole cell edge to edge, NO magenta inside them, and tile seamlessly on all four sides): 1 bright cyan water caustics, a net of wavy light lines on a dark teal water colour. 2 the same caustics, paler, on a sandy shallow-water colour. 3 sparkles of sun on rippling blue water. 4 a strip of white shoreline foam, long and thin, lying horizontally. 5 the white foam ring where a small waterfall hits a pool, seen from above. 6 a tall soft plume of white mist rising from the foot of a waterfall.
Row 2, BURSTS: 7 a splash of water bursting upward. 8 a small geyser spout of white water and steam. 9 a bubbling patch of brown mud with one bubble bursting. 10 a lava bubble bursting, orange with dark crust. 11 a tall plume of white steam from a vent in the ground. 12 a fountain's spray, a little arc of water drops.
Row 3, GROUND LIFE AND DUST: 13 a dust devil, a small whirl of tan dust. 14 a puff of dust kicked up by a footstep. 15 a small pile of fallen red and gold leaves. 16 a ring of tiny pale mushrooms. 17 a patch of tiny glowing blue mushrooms with a soft glow. 18 a scorch mark, a dark burned splotch with a few embers.
Row 4, PUDDLES AND DRIPS: 19 a small rain puddle with a ripple ring. 20 a drip of water falling, with the drop and its splash below it. 21 a pool of slime, green and glistening. 22 a glowing fel crack in the ground, green light from a jagged split. 23 a glowing arcane rune circle on the ground, faint violet lines. 24 a small swirl of blown snow on the ground.
```

Slices: `fx_caustics_deep`, `fx_caustics_shallow`, `fx_sun_sparkle`, `fx_shore_foam`, `fx_fall_foam`, `fx_fall_mist`;
`fx_splash`, `fx_geyser`, `fx_mud_bubble`, `fx_lava_bubble`, `fx_steam_vent`, `fx_fountain_spray`; `fx_dust_devil`,
`fx_dust_step`, `fx_leaf_pile`, `fx_mushroom_ring`, `fx_glow_mushrooms`, `fx_scorch`; `fx_puddle`, `fx_drip`,
`fx_slime_pool`, `fx_fel_crack`, `fx_arcane_circle`, `fx_snow_swirl`.

---------------------------------------------------------------------
## SHEET EFX10: SKY EVENTS (light overlays, black background)

```
Generate ONE image, 2048x1366, a 3 columns x 3 rows grid = 9 separate panels, each panel about 682x455. Every panel is a FULL-SCREEN LIGHT OVERLAY for a top-down 2D fantasy RPG, painted as glowing light on a pure #000000 black background (black is see-through; the panel is added over the game for a moment). Each panel's light stays inside its own panel, with a thin pure black gutter between panels. No ground, no objects, no characters, no text, no labels, no grid lines. Painterly, matching the attached reference.

Panels, row by row, left to right:
1 LIGHTNING STRIKE A: one jagged bright white-blue lightning bolt from the top edge down to the lower middle, with two thin branches and a soft glow round it.
2 LIGHTNING STRIKE B: a different bolt, forking twice, striking down to the lower left.
3 LIGHTNING FLASH: no bolt, just a bright soft white-blue flash filling most of the panel, brightest at the top, as clouds lit from inside.
4 AURORA RIBBONS: two long wavy curtains of green and teal light across the upper half, with faint violet at their edges.
5 SHOOTING STARS: three thin bright white streaks with soft tails, crossing diagonally down to the right, spaced apart.
6 FALLING STAR: one larger glowing gold-white meteor with a long soft burning tail, coming down from the top-right.
7 RIFT GLOW: a jagged tear of bright violet light in the middle of the panel with a soft violet glow round it, as a crack in the sky.
8 RAINBOW: a soft wide rainbow arc across the upper half, gentle and faded, as after rain.
9 HEAT SHIMMER: faint wavy horizontal lines of pale light across the lower half, very subtle, like hot air rising off sand.
```

Slices: `sky_lightning_a`, `sky_lightning_b`, `sky_lightning_flash`, `sky_aurora`, `sky_shooting_stars`,
`sky_falling_star`, `sky_rift_glow`, `sky_rainbow`, `sky_heat_shimmer`.

---------------------------------------------------------------------
## Which zones get what (a first pass, for when the sheets land)

| Zone family | Light | Shade | Layer | Particles and life |
|---|---|---|---|---|
| Durotar, the Barrens, Tanaris, the Abyssal Sands | desert glare | dust haze (Tanaris) | sandstorm (sometimes), heat shimmer | dust devils, vultures, sand swirls |
| Tirisfal, Silverpine, the Plaguelands, Deadwind | overcast, moonlight, plague miasma | haunted, night | ground fog, plague fog | crows, ravens, bats, plague spores |
| Ashenvale, Azshara, Dawnhaven, Feralas | autumn rays, golden canopy | canopy dapple | leaf drift, golden motes | leaves, butterflies, fireflies at night |
| Stranglethorn, the Echo Isles, the World Tree | jungle shafts | jungle canopy | drizzle, waterfall mist | parrots, dragonflies, glowing seeds |
| Felwood | fel glow | haunted | swamp mist | fel spores, fel motes |
| Winterspring, the Weeping Ice, the cold lands | winter sun, aurora glow | storm gloom | snow, blizzard | snowflakes, aurora event |
| Thunder Ridge, the Tempest Isles, the Bastions | overcast | storm gloom | downpour, sea spray | lightning events, gulls |
| The Underdark, caves, dungeons | cave skylight, crystal cave, ember underglow | cave vignette | steam | glowing mushrooms, drips, bubbles |
| Moonglade | moonlight, holy column at the shrines | night | fireflies | wisp lights, falling stars |
| The sky, Caelora | sun bloom (as now) | cloud shadows | golden motes | flyover shadows, feathers |
| The Fading Firmament | dusk, arcane shimmer | haunted | void wisps | void motes, rift glow |
| The coasts and towns | dawn, dusk by time of day | cloud shadows | sea spray | gulls, shore foam, ripples |
