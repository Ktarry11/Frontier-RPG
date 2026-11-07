# Combat background prompts — the thin packs

Seven packs are at one or two images, which means every fight in those places
shows the same painting. `tools/qa_combat_backgrounds.py` prints the current
list under "thin pack"; re-run it after adding art.

| pack | has | wants | what it covers |
|---|---|---|---|
| `savanna` | 1 | 5 | Northern/Central/Southern Barrens, Crossroads, Camp Taurajo, Field of Giants, Razorfen Approach |
| `savanna_oasis` | 1 | 3 | Lushwater Oasis, The Forgotten Pools, Raider's Rest Oasis |
| `arena` | 1 | 3 | Gurbashi Arena |
| `hive` | 1 | 3 | silithid interiors |
| `fungal` | 2 | 4 | spore caverns |
| `salt_flat` | 2 | 4 | The Shimmering Flats, Saltwheel |
| `sky` | 2 | 4 | the three zeppelin towers, Freewind Post |
| `coast` | **0** | 4 | 8 shoreline subzones that currently fight inland — see below |

These are **landscape backdrops**, not icons — wide, deep, and empty in the
middle third, because the party and the enemies are drawn standing on top of
them. The loader scales by the larger ratio and centre-crops, so anything
important near an edge gets cut.

---

## Shared style preamble

> Generate a 16:9 landscape fantasy-RPG combat backdrop, painterly digital
> illustration in a classic MMO style. Wide establishing view, horizon low in
> the frame. Saturated but natural colour, strong directional light, soft
> aerial perspective into the distance. No characters, no creatures, no text,
> no UI, no borders. The centre and lower third must stay visually calm and
> uncluttered — characters will be composited standing there. Detail and
> silhouette belong at the sides and along the horizon.

---

## SAVANNA — 5 images

Dry tropical grassland. The Barrens: ochre and olive, not sand, not green
pasture. Flat-topped acacia, thornbush, standing dead wood, red dirt tracks.

> [preamble]
>
> Palette: dry ochre grass, olive scrub, red-brown earth, pale washed-out
> blue sky, dark acacia green.
>
> 1. Open dry grassland at midday, two flat-topped acacias to one side, a dirt
>    track running toward distant blue hills, heat shimmer on the horizon
> 2. Thornbush scrub on broken red ground, scattered boulders, a dead tree
>    bleached white, low afternoon sun from the left
> 3. A shallow dry wash cut through ochre grass, banks of cracked red clay,
>    tall grass on the ridges, overcast bright sky
> 4. Rolling savanna at golden hour, long grass bent by wind, a line of
>    acacias on the ridge, dust haze
> 5. Night savanna under a huge star field, grass silhouetted dark against a
>    deep blue sky, distant heat lightning on the horizon

## SAVANNA_OASIS — 3 images

A pocket of real water in the middle of the above. Palms, reeds, turquoise
shallows, lush green that stops abruptly at the dry grass line.

> [preamble]
>
> Palette: turquoise water, lush palm green, pale sand, ochre dry grass at
> the edges.
>
> 1. A wide spring-fed pool ringed by palms and reeds, turquoise shallows,
>    dry ochre grassland visible beyond the green
> 2. A chain of small pools in low ground, papyrus and broad-leaf growth,
>    bright midday light, palms leaning over the water
> 3. An oasis at dusk, still dark water reflecting palms, fireflies, the
>    surrounding dry plain fading to blue

## ARENA — 3 images

Gurbashi: a troll fighting pit, sand floor, raked stone tiers, torches.

> [preamble]
>
> Palette: sun-bleached sand, weathered stone, jungle green beyond the walls,
> torch orange.
>
> 1. A circular sand fighting pit from floor level, stepped stone seating
>    rising on all sides, troll stone carvings, bright sun
> 2. The same pit at night lit by ringed torches, deep shadow in the stands
> 3. A pit floor half-flooded after rain, sand dark and churned, overcast sky

## HIVE — 3 images

Silithid. Chitin architecture, resin, organic tunnels — insect, not undead.

> [preamble]
>
> Palette: amber resin, chitin brown-green, sickly yellow glow, dark earth.
>
> 1. A vaulted underground chamber of ribbed chitin, amber resin dripping
>    from the ceiling, faint yellow glow from the floor
> 2. A tunnel of packed earth lined with hardened secretion, egg clusters
>    recessed in the walls, dim light from ahead
> 3. A hive entrance from inside looking out, harsh desert light in the
>    opening, chitin arches framing it

## FUNGAL — 2 more

> [preamble]
>
> Palette: bioluminescent blue-green, violet spore haze, wet black stone.
>
> 1. A cavern of giant mushroom caps, glowing gills underlighting the scene,
>    spore motes in the air
> 2. A low fungal marsh underground, shallow black water, luminous shelf
>    fungus climbing the walls

## SALT_FLAT — 2 more

> [preamble]
>
> Palette: blinding white crust, pale blue sky, thin grey-brown mineral stain.
>
> 1. A cracked white salt pan to a flat horizon, polygon crust pattern,
>    hard midday light, no vegetation at all
> 2. A salt flat under a thin sheet of standing water, perfect mirror
>    reflection of a pale sky, distant low ridges

## SKY — 2 more

Up high: zeppelin towers and wind-riding mesas, looking out over cloud.

> [preamble]
>
> Palette: cloud white, deep sky blue, warm wood and rope, distant gold haze.
>
> 1. A wooden platform high above a sea of cloud, mooring ropes and a
>    windsock, the land far below showing through a gap
> 2. A wind-carved mesa top at sunrise, cloud filling the valleys between
>    other mesas, long warm light

---

## COAST — 4 images, a pack that does not exist yet

`tools/qa_combat_backgrounds.py` lists subzones whose NAME promises terrain
their parent zone's pack cannot show. After tightening the match to whole
words it reports 78, and most of those are still the tool being cautious — a
grove in a forest is a forest, and "Entrance Caverns" inside a cave dungeon is
already right.

The one genuinely actionable cluster is **shorelines inside land zones**:

    The Wrackline Shore    Arathi East         fights in mossy_forest
    Coast Bluffs           Ashenvale West      fights in fantasy_forest
    Zoram Coast            Ashenvale West      fights in fantasy_forest
    Scuttle Coast          Durotar             fights in desert
    The Eastern Strand     Eastern Hillsbrad   fights in mossy_forest
    The North Coast        Eastern Tirisfal    fights in blighted
    Razorjaw Reef          Echo Isles          fights in jungle

**`nautical` is not the answer** — its three variants are a weather deck, a
hold, and flooded ruins. Routing a beach there puts the fight on a ship.

These want four shorelines, deliberately spread across climates so one pack
serves Durotar's red-rock coast and Tirisfal's dead northern one:

> [preamble]
>
> 1. A rocky northern shoreline under grey overcast, dark wet stone, cold
>    green-grey surf, driftwood and kelp above the tide line
> 2. A warm red-rock coast at midday, ochre cliffs meeting turquoise shallows,
>    pale sand, scrub clinging to the rock
> 3. A temperate beach at golden hour, pale sand, low dunes with marram grass,
>    a long calm sea and a distant headland
> 4. A reef shore at low tide, exposed coral and tidal pools, bright shallow
>    water, jagged rock, seabirds in the distance

Once the folder exists: add `"coast"` to `FLAT_FOLDERS` and
`BIOME_TO_BACKGROUND` in `world/combat_backgrounds.py`, then give the seven
subzones above a `"coast"` entry in `SUBZONE_BIOME` (`world/tile_textures.py`).
The loader already consults subzone biomes, so that is the whole wiring.

---

## Three one-image packs (7 Nov, second batch)

`abyssal_sands`, `glittervein` and `frozen_ruins` each exist to stop a named,
written place from borrowing a neighbour's art. Each currently holds ONE
image, so the same backdrop draws every fight in that place until the pack
grows. These are the next three to fill, in that order.

Same house style as every other pack: painterly fantasy matte, no text, no
characters, no UI, horizon low enough that the lower third is empty ground.

**abyssal_sands** - sunken, haunted desert. Its one image is violet sky over
black runed monoliths in red sand.

> 1. A collapsed sinkhole in red desert sand, the rim crumbling inward, violet
>    dusk sky, black obelisks half-swallowed at the edge
> 2. A buried causeway of dark carved stone emerging from a dune field under a
>    bruised purple sky, drifting sand, no vegetation
> 3. A night desert of deep red dunes lit by cold violet light from beneath the
>    sand, thin crystal spires, heavy stars

**glittervein** - a mining canyon whose rock is full of ore. Its one image is
a red canyon split by green-gold crystal seams.

> 1. A worked quarry face in red sandstone, gold and green crystal exposed in
>    the cut, spoil heaps and timber shoring, dusty sunlight from above
> 2. A narrow red-rock gorge floor at midday, glittering gold dust on the sand,
>    green crystal clusters growing from fallen boulders
> 3. The mouth of a mine driven into a red cliff, gold seams running out of the
>    dark into daylight, broken carts and rail, haze

**frozen_ruins** - alpine ruins above the treeline, outdoors. Its one image is
snowbound arches and blue crystal under an aurora.

> 1. A snowbound stone courtyard in a high pass, broken columns, blowing snow,
>    overcast daylight, dark pines far below
> 2. A frozen lake between ruined walls, blue ice, snow-laden firs, pale
>    winter sun low on the horizon
> 3. A high stair of weathered stone climbing out of deep snow toward a ridge,
>    ice-glazed carvings, aurora over the peaks

---

## The repetition list (7 Nov) — generate these in this order

`tools/qa_combat_backgrounds.py` now prints a **places/image** ratio per pack.
That is the number worth chasing, not the image count: `coast` has eleven
images for thirteen places and `dark_dungeon` has five for **one hundred and
forty-three**. A third of the game is drawing from five pictures.

Six packs are over 10. Four prompts each, one sheet per pack, in this order:

Same house style throughout: painterly fantasy matte, no text, no characters,
no UI, lower third mostly empty ground so a fight can stand on it.

### 1. dark_dungeon — 5 images, 143 places (28.6)
The single worst number in the game. It serves crypts, barrows, mines,
spider caves, worked dwarven stone and flooded undercrofts all at once, so
the four should be visibly different ROOMS, not four angles on one.

> 1. A square-cut dwarven hall of dressed grey stone, iron sconces, a
>    collapsed section of ceiling letting dust-light in
> 2. A burial barrow of damp earth and fieldstone, low lintels, root threads
>    through the roof, green-grey gloom
> 3. A worked mine gallery with timber shoring and rail, spoil heaps, a
>    lantern-lit working face receding into dark
> 4. A web-choked cavern, pale silk sheeting the walls and floor, husks and
>    bundles, sickly light from a crack above

### 2. savanna — 3 images, 39 places (13.0)
The whole Barrens. Dry open grassland; keep oases out, that is its own pack.

> 1. Open golden grass to a flat horizon, scattered thorn scrub, heavy noon
>    light, a few vultures high up
> 2. A dry wash cut through red earth, cracked banks, pale grass on the rim,
>    acacia shade on one side
> 3. Burnt grassland after fire, black stubble and new green, smoke haze on
>    the horizon, bleached bone
> 4. Tall seed-head grass at dusk under a huge orange sky, distant mesas
>    flattened to silhouette

### 3. mossy_forest — 8 images, 101 places (12.6)
Hillsbrad farm country and temperate woodland. It already holds a cottage and
a barn; these should widen it, not repeat the buildings.

> 1. A stone-walled sheep pasture on a green hillside, drystone dyke, oaks,
>    bright broken cloud
> 2. A mossy beech wood with a stream running over flat rock, dappled green
>    light, ferns
> 3. A rutted cart track through hedgerow in late afternoon, wildflowers,
>    rolling fields beyond
> 4. A mill pond and sluice under willows, weed on the water, grey soft light

### 4. mountain — 6 images, 72 places (12.0)
Real elevation. It is currently doing red canyon AND alpine, which is two
different mountains; weight these alpine.

> 1. A boulder field on a high shoulder above the treeline, scree, cloud
>    shadow moving over bare rock
> 2. A glacial bench with a milky meltwater tarn, moraine, snow in the
>    gullies, grey peaks behind
> 3. A narrow switchback ledge cut into a cliff face, drop on one side,
>    thin cold light
> 4. A wind-scoured saddle between two summits, stunted pines bent one way,
>    broken cloud below

### 5. ice_dungeon — 3 images, 34 places (11.3)
Cold water and cold stone, roofed. Blackfathom and the Weeping Ice both pull
from here, so one of the four should read sunken rather than frozen.

> 1. A blue ice gallery with meltwater running down the walls, frozen
>    columns, light filtering from deep above
> 2. A flooded stone chamber of dark water to knee height, icicles, carved
>    pillars half submerged
> 3. A glacier crevasse floor, walls of layered blue ice closing overhead,
>    snow dust falling
> 4. A frozen cave mouth from inside, white daylight at the far end, rimed
>    rock, frozen cascade to one side

### 6. blighted — 7 images, 73 places (10.4)
The whole undead belt: Silverpine, Tirisfal, Undercity. Dead country, not
dungeon.

> 1. A dead pine forest in standing fog, bare grey trunks, no undergrowth,
>    light with no source
> 2. A sunken graveyard, leaning stones, wet black earth, a bare thorn
>    hedge, sick green sky
> 3. An abandoned farmstead gone to rot, collapsed roof, dead orchard rows,
>    crows
> 4. A plagued stream through grey reeds, oily surface, dead rushes, the
>    far bank lost in haze
