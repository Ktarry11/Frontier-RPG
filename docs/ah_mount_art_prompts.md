# Auction house exclusive mounts (2 sheets, 7 mounts)

Kyle, 18 Nov 2026: "can you whip up another 3 art prompts for mounts that are AH exclusive?!" Three Collection mounts
that only ever turn up on the auction house, put up by its traders: no vendor, no drop, no quest. Built into the
Collection when the sheet lands.

---------------------------------------------------------------------
## SHEET H4: three auction house mounts, 4 facings each  (paste this whole block)

Same rules as the Collection's mount sheets, three columns instead of six: 3 columns x 4 rows, 768x1024, magenta key,
no rider. Sliced by `tools/asset_pipeline/slice_mount_sheet.py SHEET.png bazaar_brute coinscale_raptor velvet_saber`.
Attach two or three existing mount facings (`war_kodo_left.png`, `rune_saber_down.png`) as the style reference.

```
Generate ONE sprite sheet image, 768x1024, a 3 columns x 4 rows grid = 12 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are the RAREST, MOST EXPENSIVE RIDING MOUNTS in a Horde fantasy RPG, the kind only a rich goblin trader would sell, shown with NO RIDER. Each wears lavish tack with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each should look expensive at a glance: gold, silk, jewels, showing off. Each needs a silhouette you could pick out at a glance from the other two.

Columns, left to right (the same three animals in every row, each turned according to that row's rule):
1. BAZAAR BRUTE - a huge, heavy, four-legged dinosaur the size of two kodos, thick grey-green hide, a broad armoured head with a short horn, a long thick tail. On its back, behind the saddle, a small goblin market stall: a striped red and gold canopy on poles, crates and sacks lashed down, a set of brass scales, lanterns and a few hanging rugs. Gold rings in its horn, a red tasselled harness. A walking marketplace.
2. COINSCALE RAPTOR - a lean, fast raptor whose scales are naturally a deep bronze, decked in barding made of hundreds of overlapping gold coins like fish scales along its neck and back, a jewelled headpiece with a red gem between its eyes, a crest of black and gold feathers. A sleek black leather saddle with gold trim. Proud and flashy.
3. VELVET SABER - a big, sleek sabre-toothed cat with dark midnight-purple fur and faint silver stripes, long ivory sabre teeth, bright gold eyes. Draped in deep plum velvet barding edged with gold embroidery, pearls and small sapphires on the harness, a plush velvet saddle with gold tassels. Elegant and dangerous.

Scale: the brute is by far the largest and widest; the raptor is tall and narrow; the saber is long and low. Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

Their reins icons can go on any later icon sheet; until then they borrow the Collection's reins.

---------------------------------------------------------------------
## SHEET H5: four more auction house mounts, 4 facings each

Kyle, 18 Nov 2026: "4 more mounts please". Same rules as H4, four columns: 4 columns x 4 rows, 1024x1024, magenta key,
no rider. Sliced by `tools/asset_pipeline/slice_mount_sheet.py SHEET.png ledger_tortoise silkwind_strider goldtusk_boar
platinum_direwolf`. The prompt is the H4 block with these four columns (sent to Kyle in full the same day):

1. LEDGER TORTOISE: a giant tortoise, gold-leaf domed shell, a padlocked strongbox vault and ledgers on top.
2. SILKWIND STRIDER: a very tall flightless bird, emerald and gold plumes, trailing teal and gold silk, gold bells.
3. GOLDTUSK BOAR: a massive war boar, gold-capped tusks ringed with rubies, red lacquered barding.
4. PLATINUM DIREWOLF: a white direwolf in engraved platinum plates, sapphires on the brow, white fur saddle.

Scale: tortoise widest and lowest, strider tallest and thinnest, boar short and heavy, wolf long and lean.
