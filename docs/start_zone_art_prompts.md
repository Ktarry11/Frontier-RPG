# Start zone cards: art prompt (sheet SZ1)

**Status (21 Nov 2026): delivered and in the game.** See `docs/art_status.md` for every sheet.

Kyle, 21 Nov 2026: "instead of clicking on the starting zones. We make a more prominent 'Starting zone' thing you click
on to pick it. It has actual lore about the location and an image too", then "give me a prompt that adds 4 gorgeous art
pieces to the zone selector in one sheet". Character creation now has one big **Starting zone** card, and clicking it
opens the picker: a card for each start with its painting, where it is, its levels and its lore
(`world/start_zones.py`). The White Expanse's card is shown locked until the Aetherian start zone is built.

The paintings are shown at about 268 x 201 on the picker and 136 x 102 on the creation screen, so each needs one strong,
readable focal point. They share one idea so the four read as a set: **a lone small figure seen from behind, just
arrived, looking at where they've woken up.**

Slice: `python3 tools/slice_start_zone_art.py tools/building_sheets/start_zones_sz1.png` cuts the 2x2 into
`assets/ui/start_zones/valley_of_trials.png`, `deathknell.png`, `dawnhaven.png` and `white_expanse.png`, in that order
(left to right, top to bottom). Until then each card shows a painted stand-in.

**Attach as style references:** `assets/ui/factions/bg_orgrimmar.png` and `assets/ui/factions/bg_sunreach_conclave.png`
(the faction card paintings, the finish to match).

---------------------------------------------------------------------
## SHEET SZ1: THE FOUR STARTS (paste this whole block)

```
Generate ONE image, 2048x1536, laid out as a strict 2 columns x 2 rows grid = 4 separate landscape paintings, each panel exactly 1024x768. COUNT THEM: exactly 2 across and 2 down. Each panel is COMPLETELY FILLED by its painting, edge to edge, with no border, no frame, no gutter, no grid lines, no text, no letters, no logos, no banners with writing, no numbers. Painterly semi-realistic fantasy art in the style of World of Warcraft loading screens, matching the attached references in finish: rich colour, dramatic light, atmospheric depth, soft painted edges, breathtaking and inviting. These are the four places a new character can wake up in a fantasy RPG, shown on the cards you choose between, so each one must be GORGEOUS and readable even when shown small: one clear focal point, a strong silhouette, a clear sense of place and mood, the light doing most of the work.

In EVERY panel, somewhere in the lower middle, a single small figure seen from BEHIND, standing still and looking out at the place they've just woken up in, simple travel clothes, no face visible, small in the frame. They are a newcomer who has never been here before. Nothing from our real world appears anywhere.

Panels, left to right, top to bottom:

1 THE VALLEY OF TRIALS (Durotar): a sun-baked red rock canyon at late afternoon, towering red cliffs on both sides, spiky orc huts with hide roofs and tusk-and-timber frames along the valley floor, cooking smoke rising, a few tall cacti and scrubby trees, wild boars in the distance, a great orange sky and long golden shadows. The figure stands on a rise at the valley mouth looking down into it. Warm, hard, welcoming in a gruff way.

2 DEATHKNELL (Tirisfal Glades): a misty graveyard at dawn under a heavy grey-green sky, crooked gravestones and open freshly dug graves, a ruined stone chapel with a broken bell tower, dead twisted trees, a pale sickly light breaking through the clouds onto the graves, a few tall gaunt undead figures far off by the chapel with green lantern light. The figure stands beside an open grave, its earth disturbed, looking toward the chapel. Eerie, melancholy and quietly beautiful.

3 DAWNHAVEN (an island off Azshara): a breathtaking autumn island at sunrise, a gold sand shore with gentle turquoise waves, trees blazing red and gold all over the hills, an ancient white marble and gold elven ruin among them, and on a headland across the bay a single very tall slender white and gold spire with a crimson-roofed crown and a great gold crystal blazing at its top, catching the first light. The figure stands at the water's edge on the shore, wet to the knees, looking up at the spire. Hopeful, warm, the feeling of a new home.

4 THE WHITE EXPANSE (Caelora, above the clouds): a vast cold shelf of white cloud and pale stone floating high in the sky, wind streaming over it, a few weathered white marble ruins with gold trim and glowing blue crystals half buried in the cloud, and far away across a golden sea of clouds a breathtaking floating city of white towers and gold spires with blue crystal windows, rings of stone around it, waterfalls pouring off its islands into the clouds, a huge low golden sun behind it, and far below through a gap in the clouds the faint gold-green crown of an impossibly huge tree. The figure stands on the cloud shelf with their back to us, looking across at the city. Awe, distance, wonder, and a little cold.
```

Slice order: `valley_of_trials`, `deathknell`, `dawnhaven`, `white_expanse`.
