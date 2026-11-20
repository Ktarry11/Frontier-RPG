# The Crown: the cutscene at the top of the ascent

Kyle, 20 Nov 2026: "at the end of the ascent there is a mural, and when we get close it triggers. The mural has the 3
races on it, we go to touch it and it crumbles. Golden light floods into the room and we step out onto the crown of the
world tree and look over, we see a tiny STV as we are so high up, then we turn and see the countless islands and the
capital city."

This is the end of the Cloudbreak (`docs/worldtree_brief.md`, "The ascent"): the moment the ground ends. It's the
game's first cutscene, so it brings the cutscene player with it.

## Where it happens

The Cloudbreak's rope ladder climbs through the cloud and ends in a chamber grown in the living wood at the top of the
tree, closed on its far side by an old stone wall. On the wall is a mural of three peoples standing together under a
golden sun: the Aetherians (tall, crystal-grown, luminous-eyed), the Veyr (feathered, taloned, beaked) and the Kharad
(stone-skinned, cloud-haired giants). Nobody on the ground knows who they are yet. Two of them won't be met until their
continents are built, so the mural is the first promise of them.

You see the mural as a prop on the map first. Walking up to it triggers the cutscene, once per character. When it ends
you're standing on the Sunward Crown, and the wall in the Cloudbreak is broken open from then on (a second prop), so
walking back up shows the way through.

## The shots

| # | Shot | Frame | Moves | About |
|---|---|---|---|---|
| 1 | The chamber | CS1 | slow push in on the mural | 4 s |
| 2 | The touch | CS2 | hold, cracks of gold light spreading from where it was touched | 3 s |
| 3 | It crumbles | CS3 | shake, then the light floods to white | 3 s |
| 4 | Out into the light | CS4 | white fades down into the crown's edge in full sun | 4 s |
| 5 | Looking over | CS5 | slow tilt down to a tiny Stranglethorn far below through a gap in the clouds | 5 s |
| 6 | Turning round | CS6 | slow pan across the countless islands to the capital, the sun behind it | 7 s |

Then the frame fades to the game, and the Crown's name comes up the way every zone's does. No words are spoken; one line
of text can sit under the last shot if Kyle wants it. Escape skips, for anyone seeing it again on another character.

**The frames are painted from the player's eyes, with no figure in them**, because every race and class has to fit:
no hand reaches for the mural in CS2, the cracks just start where you touched it.

**The rules it keeps:** nothing built from Earth (Stranglethorn is Azeroth's own), and the mural says nothing about what
the Integration was or why it happened. It's three peoples and a sun.

## What it needs built (with the Cloudbreak)
- `ui/screens/cutscene_screen.py`: plays a list of shots, each an image with a start and end framing (pan and zoom),
  a duration, crossfades, an optional shake, an optional light flood (a white-gold overlay that ramps to full), and an
  optional line of text. Escape skips. It hands back to the overworld when it's done.
- A trigger on the Cloudbreak's map: a few tiles in front of the mural. Seen once per character (a saved flag), then
  the player is moved to the Sunward Crown's arrival.
- The two mural props on the Cloudbreak (intact, then broken open), swapped by the same flag.

## Art: sheet CS (landed 20 Nov 2026)

All seven came in on 20 Nov: the six frames are saved to `assets/ui/cutscenes/crown/` (cs1_chamber, cs2_touch,
cs3_crumble, cs4_crown, cs5_looking_down, cs6_islands) and the two props are sliced to `assets/buildings/` (the sheet is
kept at `tools/building_sheets/crown_mural_props.png`). The prompts stay below as the record.

Six paintings at 1536x1024, the same size as the panoramas, plus one small sheet with the two mural props. Paste each
prompt as its own image. The frames save to `assets/ui/cutscenes/crown/`; the props slice to `assets/buildings/`.

### CS1: the mural chamber (`assets/ui/cutscenes/crown/cs1_chamber.png`)

```
Generate ONE wide painting, 1536x1024. Painterly semi-realistic fantasy art in the style of a World of Warcraft loading screen or in-game cinematic still: rich detail, soft painted edges, glowing light. No text, no logo, no watermark, no frame, no people or hands in the picture, nothing from our real world, no pink or magenta anywhere.

THE SUBJECT: the last chamber at the very top of a colossal World Tree, seen from the eyes of someone who has just climbed up into it out of thick cloud. The chamber is grown from the living wood of the tree: smooth curving walls of honey-gold heartwood and pale bark, roots and branches woven into ribs overhead, a few wisps of white cloud still drifting across the floor behind the viewer. A worn rope ladder's top rungs are visible at the very bottom edge.

THE MURAL: the far wall, filling the centre of the image, is not wood but an ancient wall of pale weathered stone set into the tree, much older than the tree around it. On it is a great carved and painted mural, faded and cracked with age, with traces of gold leaf: three figures of three different peoples standing side by side beneath a huge golden sun with long rays. On the left a tall, imposing humanoid with pale blue-grey skin, luminous eyes and crystal growths along the shoulders and brow, in flowing robes. In the middle an avian humanoid with feathered arms like wings, powerful talons and a hooked beak, proud and fierce. On the right a huge broad giant with stone-like skin, cloud-white hair and mineral crystals growing from the skin, twice the height of the others. Below them, tiny painted islands floating on a sea of cloud.

LIGHT: dim and quiet. Thin threads of golden light leak through the hairline cracks around the edges of the stone wall, as if something very bright is on the other side. Soft cool light from the cloud below. Dust in the air.

MOOD: hushed, sacred, the end of a very long climb.
```

### CS2: the touch (`assets/ui/cutscenes/crown/cs2_touch.png`)

```
Generate ONE wide painting, 1536x1024, the same scene and style as the attached picture (the mural chamber at the top of the World Tree) but closer: the stone mural of the three peoples beneath the golden sun now fills most of the frame. No people or hands in the picture, no text, no logo, no frame, nothing from our real world, no pink or magenta anywhere.

THE MOMENT: the mural has just been touched at its centre, on the painted sun. From that point brilliant cracks of golden light are spreading out across the whole stone like lightning frozen in rock, running through the three painted figures and to the edges of the wall. Golden light is shining out through every crack. Tiny chips and dust are starting to fall from the surface. The rest of the chamber is darker by contrast, the honey-gold wood walls lit gold where the light reaches them.

MOOD: the breath before something gives way.
```

### CS3: it crumbles (`assets/ui/cutscenes/crown/cs3_crumble.png`)

```
Generate ONE wide painting, 1536x1024, the same chamber and style as the attached pictures. No people or hands in the picture, no text, no logo, no frame, nothing from our real world, no pink or magenta anywhere.

THE MOMENT: the ancient stone wall with the mural is collapsing. Great slabs of the painted stone are breaking apart and falling, fragments of the three painted figures and the painted sun tumbling in slow motion with dust and chips of gold leaf. Through the opening where the wall was, overwhelming GOLDEN LIGHT is flooding into the chamber: a blinding wall of warm gold and white light with long god rays pouring in, lighting every falling stone from behind, turning the dust into glittering motes. The wooden chamber walls glow bright gold. The centre of the image is almost pure golden white.

MOOD: awe, release, the sky breaking in.
```

### CS4: out into the light (`assets/ui/cutscenes/crown/cs4_crown.png`)

```
Generate ONE wide painting, 1536x1024. Painterly semi-realistic fantasy art in the style of a World of Warcraft loading screen or cinematic still. No people or hands in the picture, no text, no logo, no frame, nothing from our real world, no pink or magenta anywhere.

THE VIEW: from the eyes of someone stepping out of a broken stone wall onto the crown of a colossal World Tree, high above the clouds. In the foreground the crown's branches, each as wide as a road, covered in golden leaves and moss, a broken stone doorway's edge at one side of the frame with light still pouring past it. Beyond the branches, an endless sea of white and gold cloud spread to the horizon in every direction. A huge golden sun hangs low ahead, its light blinding and warm, long rays across the cloud tops. The air is clear and bright, everything rimmed in gold.

MOOD: arriving at the top of the world. Bright, open, breathtaking.
```

### CS5: looking over (`assets/ui/cutscenes/crown/cs5_looking_down.png`)

```
Generate ONE wide painting, 1536x1024, the same style as the attached picture. No people or hands in the picture, no text, no logo, no frame, nothing from our real world, no pink or magenta anywhere.

THE VIEW: looking straight down over the edge of the golden crown of a colossal World Tree from unimaginably high up. Golden-leafed branch ends and a few falling leaves at the top and sides of the frame frame the view. Far, far below, through a great round gap in the sea of white cloud, is the ground: a tiny green jungle coastline of tropical Stranglethorn Vale, so small it looks like a map, with a turquoise sea, a tiny curved bay with a pirate harbour town no bigger than a speck, winding jungle rivers, and the vast trunk of the World Tree itself plunging down from the viewer through the clouds and disappearing into the haze toward a small island on that coast. The cloud sea around the gap glows gold in the sun. Strong sense of vertigo and scale: the ground is miles below.

MOOD: dizzying height; how far you've come.
```

### CS6: turning round (`assets/ui/cutscenes/crown/cs6_islands.png`)

```
Generate ONE wide painting, 1536x1024, the same style as the attached pictures. No people or hands in the picture, no text, no logo, no frame, nothing from our real world, no pink or magenta anywhere.

THE VIEW: from the golden crown of a colossal World Tree high above the clouds, turning away from the edge to look out across the sky. In the foreground a few golden branches and leaves at the bottom corners. Beyond them, across an endless golden cloud sea, COUNTLESS FLOATING ISLANDS at every height and distance, near and far, big and small: islands of pale stone and gold grass with waterfalls pouring off their edges into the clouds, hanging roots, little ruins and crystal towers on some, sky rivers falling from one to the next. Far off in the centre, catching the light, the CAPITAL CITY of the sky: a gleaming city of white marble, gold and glowing blue crystal floating above the clouds, with a soaring central spire palace, domes, arched bridges and airships with golden sail-fins around it. A huge golden sun low behind the city, long god rays, deep atmospheric perspective fading to gold haze.

MOOD: a whole new world, impossibly vast and beautiful.
```

### CS-P: the mural on the map (two props, MAGENTA KEY; slice to `assets/buildings/cb_mural_intact.png` and `cb_mural_broken.png`)

```
Generate ONE image, 1536x1024, on a flat solid magenta (#FF00FF) background, with TWO separate game props side by side, each centred in its own half with plenty of magenta around it. Top-down three-quarter view like a classic isometric RPG building sprite, painterly, soft shading, light from the top left. No text, no frame, no shadow on the magenta.

LEFT: an ancient pale stone wall set into living golden tree wood, with a faded carved and painted mural on it of three figures (a tall crystal-grown humanoid, a feathered avian humanoid, a huge stone-skinned giant) under a golden sun, thin threads of gold light at its edges.

RIGHT: the same wall broken open in the middle, the mural's stone fallen in rubble at its foot, a ragged opening through which bright golden light shines out.
```
