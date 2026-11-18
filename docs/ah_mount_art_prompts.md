# Auction house exclusive mounts (6 sheets of mounts, 27 mounts, plus one icon sheet)

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

---------------------------------------------------------------------
## SHEET H6: four more auction house mounts, 4 facings each

Kyle, 18 Nov 2026: "more!". Same rules as H5 (4x4, 1024x1024). Sliced by `tools/asset_pipeline/slice_mount_sheet.py
SHEET.png ruby_scorpid golden_dromedary obsidian_rhino jadehorn_elk`. Sent to Kyle in full the same day.

1. RUBY SCORPID: a giant scorpion, red lacquered carapace edged in gold, a gold stinger with a ruby.
2. GOLDEN DROMEDARY: a tall camel, a saffron and crimson silk canopy on gilded poles, rows of gold tassels and coins.
3. OBSIDIAN RHINO: a huge rhino in polished obsidian plates inlaid with gold, a gold-sheathed horn.
4. JADEHORN ELK: a giant elk with carved jade antlers hung with gold charms, green silk barding.

Scale: scorpid widest and lowest, dromedary tall with a long neck, rhino heaviest, elk with the widest antlers.

---------------------------------------------------------------------
## SHEET H7: four more auction house mounts, 4 facings each

Kyle, 18 Nov 2026: "one more". Same rules as H5 (4x4, 1024x1024). Ids: `gilded_bone_steed gilded_mechanostrider
crowned_grizzly emerald_basilisk`. Sent to Kyle in full the same day.

1. GILDED BONE STEED: a skeletal warhorse, every bone plated in gold, violet ghost-fire, purple silk barding.
2. GILDED MECHANOSTRIDER: a gold-plated two-legged goblin machine bird, glass dome head, red leather bucket seat.
3. CROWNED GRIZZLY: a colossal black bear in a gold crown helm and an ermine-trimmed red robe.
4. EMERALD BASILISK: a long low lizard with emerald gem scales, crystal spikes, gold leg bands.

---------------------------------------------------------------------
## SHEET H8: 36 icons to buy the auction house mounts and forms with

Kyle, 18 Nov 2026: "quick icons to BUY these mounts with. Like a harness or whistle or something! Aim for 36 icons."
Sent to Kyle in full the same day. 6x6 at 2048x2048, the H1 rules. Sliced in this order:

```
col_reins_bazaar_brute, col_reins_coinscale_raptor, col_reins_velvet_saber, col_reins_ledger_tortoise, col_reins_silkwind_strider, col_reins_goldtusk_boar,
col_reins_platinum_direwolf, col_reins_ruby_scorpid, col_reins_golden_dromedary, col_reins_obsidian_rhino, col_reins_jadehorn_elk, col_reins_gilded_bone_steed,
col_reins_gilded_mechanostrider, col_reins_crowned_grizzly, col_reins_emerald_basilisk, col_charm_tycoon_golem, col_charm_treasure_mimic, col_charm_pearl_murloc_king,
col_charm_bronze_drakonid, col_charm_gilded_infernal, col_charm_spirit_ancestor, col_charm_living_geode, col_charm_opulent_furbolg, col_charm_goldleaf_treant,
col_charm_silken_harpy_matriarch, col_charm_ember_djinn, col_charm_goldtooth_pirate_ghost, col_charm_beast, col_charm_undead, col_charm_demon,
col_charm_elemental, col_charm_dragonkin, col_charm_insect, col_charm_humanoid, col_charm_giant, col_charm_plant
```

1-15 are the fifteen H4 to H7 mounts' summoning items (a bell, coin reins, a velvet collar, a tortoise-shell key, a
silk bridle, a ruby tusk cap, a wolf-head whistle, a stinger pendant, a coin harness, an obsidian horn, a jade tine, a
gilded skull ornament, a gold ignition key, ermine reins, an emerald leg band). 16-27 are the F6 and F7 auction house
forms' charms. 28-36 are nine creature-family disguise charms (beast, undead, demon, elemental, dragonkin, insect,
humanoid, giant, plant) to split up the 418 forms that share the wolf charm today.
