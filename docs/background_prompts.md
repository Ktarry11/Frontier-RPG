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
