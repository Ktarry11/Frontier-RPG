# Collection art prompts (2 sheets)

For `docs/collection_design.md`. Kyle, 18 Nov 2026, on the mount colourways: "Hue shift them. And I'll get art." Two
sheets are needed now:

1. **Sheet C: the six unique Collection mounts.** They're in the game and on the auction house already. Until this
   art lands, they can be bought and learned but not ridden, and their card says so.
2. **Sheet D: 36 icons.** These are the bag icons for every kind of collectable. Today they borrow quest-item
   pictures.

The 84 mount colourways are hue shifts of the twelve existing mounts (`world/collection_art.py`), and the 465 forms
wear creature art the game already has, so neither needs a sheet. If you'd rather have hand-made colourways later,
say which ones and I'll write a Sheet E.

---------------------------------------------------------------------
## SHEET C: six Collection mounts, 4 facings each  (paste this whole block)

Same shape, slicer and rules as the stable's Sheets A and B (`claude/mount_art_prompts.md`): 6 columns x 4 rows,
1536x1024, magenta key, no rider. Sliced by `tools/asset_pipeline/slice_mount_sheet.py SHEET.png bone_white_kodo
steamwheedle_runabout tidecaller_sea_turtle dread_elk_of_felwood sunreach_hawkstrider ashen_nightmare`. Attach two
or three existing mount facings (`war_kodo_left.png`, `rune_saber_down.png`, `plaguebone_charger_right.png`) as the
style reference.

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are RARE COLLECTOR'S RIDING MOUNTS for a Horde fantasy RPG, shown with NO RIDER. Each wears a saddle and tack, with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five, and each should look special: these sell for hundreds of gold.

Columns, left to right (the same six animals in every row, each turned according to that row's rule):
1. BONE-WHITE KODO - a huge, ancient kodo beast with chalk-white shaggy hide and pale grey skin, long curved ivory tusks carved with faint tauren patterns, a heavy brow, very old and calm. A tauren elder's saddle of bone, painted hide and turquoise beads, a woven blanket in ochre and teal, small feathered totems hanging from the saddle horn.
2. STEAMWHEEDLE RUNABOUT - a goblin-built riding contraption on two long jointed brass legs like a mechanical ostrich, a round riveted brass boiler body with a small smokestack at the back puffing a little steam, a goggle-eyed lamp for a head, a padded red leather seat, patched copper plates, dangling spanners and a horn. Clearly fantasy goblin engineering: brass, rivets, gears and pipes, nothing modern.
3. TIDECALLER SEA TURTLE - a great sea turtle the size of a kodo, standing on four broad flippers, a domed sea-green shell crusted with small barnacles and coral, a wise old beaked head, damp shining skin. A saddle built onto the top of the shell from driftwood and rope, with shells and a net of kelp hanging from it.
4. DREAD ELK - a tall black elk with huge branching antlers, sleek dark hide, glowing pale green eyes, small sickly green flames flickering along the tines of the antlers and at the hooves. A dark leather saddle with a moss-green blanket and silver fittings. Proud and eerie, not rotten.
5. SUNREACH HAWKSTRIDER - a tall, elegant two-legged bird mount with a long neck and a sharp hooked beak, golden-orange and white plumage, a crest of long red-gold feathers, slender powerful legs. A blood elf saddle of white leather and gold filigree, with a crimson and gold caparison, gems at the bridle.
6. ASHEN NIGHTMARE - a powerful black warhorse with a mane and tail of slow-burning embers and smoke, eyes like coals, hooves glowing faintly orange at the edges, dark charcoal-grey hide with faint cracks of orange light. A black iron and leather war saddle with a dark red blanket. Menacing and magnificent, not skeletal.

Scale: keep sizes consistent with real proportions: the kodo and the turtle are the largest and widest; the elk and the nightmare are horse-sized, the elk taller with its antlers; the hawkstrider and the runabout are tall and narrow. Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET D: 36 Collection icons  (paste this whole block)

Square bag icons, sliced to `assets/icons/collection/` and wired to every collectable of that kind. Attach two or
three existing icons (`qi_journal.png`, `qi_horn.png`, `qi_signet.png`) as the style reference.

```
Generate ONE image, 2048x2048, a grid of 6 columns x 6 rows = 36 separate square inventory icons, each about 341x341. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no magenta or pink inside the icons. Nothing modern except where a cell says so.

Icons, row by row, left to right:
Row 1 (mount reins and keys): 1 leather reins with a bone toggle and a turquoise bead; 2 a brass goblin key with a gear-shaped bow; 3 a rope bridle hung with seashells and a sea-green bead; 4 a black leather bridle with a small green flame on its silver buckle; 5 a white and gold bridle with a red gem; 6 a black iron bridle trailing ember sparks.
Row 2 (mount colourway reins, the same leather reins in six colours): 7 rose-red reins; 8 warm gold-and-amber reins; 9 spring-green reins; 10 jade reins with a pale stone bead; 11 sea-blue reins; 12 deep twilight-violet reins with a silver star bead.
Row 3 (form charms): 13 a carved wooden charm of a murloc's head on a cord; 14 a bone charm of a wolf's head; 15 a stone charm of a coiled serpent; 16 a feathered charm of a bird skull; 17 a glowing ghost-blue charm of a howling wolf; 18 a coral charm of a drowned crowned head.
Row 4 (titles and travel): 19 a rolled parchment scroll tied with a red ribbon and a wax seal; 20 a gold-edged scroll with a blue ribbon; 21 a large tawny wind rider feather bound with a leather strip; 22 a pale grey-blue feather bound with a silver wire; 23 a small book with a hearth fire stamped in gold on the cover; 24 a second hearthstone, a smooth blue-grey stone with a glowing white rune.
Row 5 (services and tomes): 25 a leather satchel with a small iron strongbox lock; 26 a brass handbell on a wooden grip; 27 a curled courier's horn with a sealed letter tied to it; 28 a heavy tome with a sword and staff crossed on the cover; 29 a thick book with a hammer, a needle and a flask on the cover; 30 a satchel clinking with small glass vials.
Row 6 (heirloom pieces, all in one family style: dark polished steel with gold filigree and a small glowing blue gem): 31 a helm; 32 a pair of shoulderpads; 33 a breastplate; 34 a cloak folded over a hook; 35 a two-handed sword; 36 a round shield.
```

Send it back and it's sliced in this order:

```
col_reins_kodo, col_reins_runabout, col_reins_turtle, col_reins_elk, col_reins_hawkstrider, col_reins_nightmare,
col_reins_rose, col_reins_dawn, col_reins_spring, col_reins_jade, col_reins_tide, col_reins_twilight,
col_charm_murloc, col_charm_wolf, col_charm_serpent, col_charm_bird, col_charm_spirit, col_charm_drowned,
col_title_common, col_title_rare, col_feather_kalimdor, col_feather_eastern, col_tome_hearth, col_hearthstone_2,
col_satchel_bank, col_peddler_bell, col_courier_horn, col_book_master, col_book_professions, col_satchel_reagents,
col_heirloom_head, col_heirloom_shoulder, col_heirloom_chest, col_heirloom_back, col_heirloom_two_hand, col_heirloom_shield
```

The other four heirlooms (Legs, Trinket, One-Hander, Off-Hand), the four tomes and the Dusk reins reuse the nearest of these. Forms
pick a charm by creature family.
