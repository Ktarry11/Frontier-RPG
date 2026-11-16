# Stonetalon combat backgrounds

For `docs/stonetalon_brief.md`. These are the pictures behind a fight (`assets/backgrounds/<folder>/`, picked by `world/combat_backgrounds.py` from the zone or subzone you're fighting in). Today Stonetalon would borrow the generic mountain and mossy-forest packs. These give each part of it its own.

Kyle sent two redwood photos for reference (15 Nov 2026): giant straight trunks going up into fog, light coming through in shafts, and a floor of sword ferns. **Attach them as reference images for #1 and #2.** The prompt asks for them painted, not copied, so they match the rest of the set.

## The shared part (put this at the start of every prompt)

> A wide 16:9 painted battle backdrop for a turn-based fantasy RPG, World of Warcraft Classic art style: painterly, semi-realistic, rich colour, visible brushwork, no photorealism. A ground-level view of a place where a fight happens. The lower third of the frame is open, fairly flat ground where the fighters will stand, kept clear of big objects. The interest is in the middle distance and at the left and right edges. No people, no creatures, no characters, no text, no logo, no UI, no frame, no border, no vignette.

Then add the place's own line. Save as PNG; any 16:9 size (the game scales it).

## The backgrounds

| # | Folder / file | Used for | Add this to the prompt |
|---|---|---|---|
| 1 | `redwoods/st_redwood_fog.png` | Stonetalon West's low valleys (Greatwood Vale) | **Place: a coastal redwood forest in fog.** Enormous straight red-brown trunks rising out of frame, the nearest ones wider than a house, deeply furrowed bark with moss at the base. Thick pale fog between the trees, soft shafts of morning light coming down through it. A carpet of sword ferns and redwood sorrel, a red needle-duff path through the middle. Damp, quiet, cathedral-scale. *(attach both redwood photos)* |
| 2 | `redwoods/st_redwood_ferns.png` | the Standing Grove, the Cutline's edge | **Place: looking up from a deep fern bank at the foot of the giant redwoods.** Big sword ferns in the near foreground at both edges, trunks rising into fog, sunlight breaking through high up. A small clearing of trampled ferns and needles in the lower middle. *(attach both redwood photos)* |
| 3 | `redwoods/st_sequoia_slopes.png` | the Sequoia Slopes | **Place: a slope of giant sequoias in clear mountain light.** Massive cinnamon-orange trunks with rounded crowns, one with a black fire scar at its base, sunlit dry duff and big pinecones on the ground, granite boulders, blue sky through the gaps. Warmer and drier than the redwoods. |
| 4 | `blowdown/st_blowdown.png` | the Blowdown, Stonetalon East's open ground | **Place: a forest flattened by a volcanic blast.** Hundreds of huge grey trunks lying in rows on the ground, all pointing the same way, stripped of bark and branches. Everything coated in pale grey ash. A few charred snags still standing. Pink fireweed coming up through the ash. Far behind, a grey volcano with a broken-open side under a hazy sky. Desolate but strangely beautiful. |
| 5 | `blowdown/st_salvage_yard.png` | the Venture Salvage Yard | **Place: a goblin logging yard in the grey blast zone.** Huge cut logs chained in stacks, a steam saw rig with a round blade and a smoking stack, cables, crates and sawdust heaps, rusty green-painted machinery and a corrugated iron bunkhouse. Ash and sawdust on the ground. Fallen grey giants beyond the yard. |
| 6 | `mountain/st_windshear_crag.png` | Windshear Crag | **Place: wind-carved rock spires high on a mountain.** Tall grey spires with stick-and-bone harpy nests on their ledges, torn cloth flapping, a windswept ledge of rock and gravel, cloud moving fast below the peaks. |
| 7 | `mountain/st_grimtotem.png` | the Grimtotem Compound | **Place: a hardline tauren war camp in a mountain hollow.** Tall dark totems painted blood red with horned skulls, tents of dark hides and black feathers, a war drum on a frame, a palisade of sharpened logs with red handprints, trampled dark earth. Stern and threatening. |
| 8 | `blighted/st_mulgore_rim.png` | the Mulgore Rim | **Place: the edge of a land where the daylight stops.** The near ground is dead grass and dark cracked earth under a grey sky. Beyond a line of black thorned stakes hung with torn tauren totems, the land falls away into an inky black dark. Over the dark hangs a sun stuck in eclipse: a black disc with a thin burning ring, the sky around it a deep wrong red. Faint pale shapes stand far off in the dark. Dread, not gore. |
| 9 | `mountain/st_crater_rim.png` | Stonetalon Peak (the volcano) | **Place: the rim of a dormant volcano's crater.** Black basalt and red cinder underfoot, yellow sulphur crust round steaming vents, a deep cold blue crater lake below, the inner crater walls streaked grey and rust. Thin air, a hard blue sky, white steam drifting. |
| 10 | `fire_dungeon/st_ashvent.png` | the Ashvent (the lava tube cave) | **Place: inside a volcanic lava tube.** A round tunnel of glossy black rock with ropey, folded walls, a faint orange glow from cracks in the floor, grey ash drifts, steam curling from vents. Not a lava lake: a dark tunnel that's still warm. |
| 11 | `dark_dungeon/st_windshear_mine.png` | Windshear Mine | **Place: a goblin mine dug into a mountain.** Rough timber supports, mine cart rails, hanging lanterns, crates of blasting powder, ore veins in the rock, a dark shaft going deeper. |
| 12 | `sequoia/st_heartwood.png` | the sequoia dungeon, map 1 (the trunk) | **Place: inside a living giant tree, hollowed out.** Walls of red-gold heartwood made of curving growth rings, a spiral of wooden ledges going up into the dark, glossy amber sap pooled on the floor, beetle-bored tunnels in the wood, warm light coming through cracks in the bark. |
| 13 | `sequoia/st_crown.png` | the sequoia dungeon, map 2 (the crown) | **Place: high in the crown of a giant tree, above the clouds.** Branches as wide as roads, dense green needle foliage, a huge stick nest on one bough, and below and all around, open sky and a sea of cloud with other giant crowns poking through it. |

**Priority:** #1, #4 and #8 first (one for each zone's feel, plus the Rim). The two sequoia ones (#12, #13) can wait until the dungeon is built.

New folders (`redwoods`, `blowdown`, `sequoia`) get added to `world/combat_backgrounds.py` when the art lands; the rest go into the existing packs.
