# Shapeshift form art (10 sheets, 60 forms, 4 facings each, plus one icon sheet)

Kyle, 18 Nov 2026: "a quick prompt for shapeshift forms! Bears, trees, cats, etc.", "Then more special shape shift
forms after to be sold on AH!", "shapeshift forms should have all 4 angles to move with. like mounts!" and "We need each
form - Bears, beetles, cats, tree of life, spiders. All 4 angles. Some common and some rare!"

Every sheet is the mount layout: 6 columns x 4 rows, 1536x1024, magenta key, one creature per column turned four ways
(front, left, right, back). Slice with `tools/asset_pipeline/slice_mount_sheet.py SHEET.png <the six ids>`.
Attach two or three existing mount facings (`war_kodo_left.png`, `rune_saber_down.png`) as the style reference.

- F1 and F2: the twelve class forms in combat/forms.py, plus the Tinker's Mechsuit.
- F3 to F5: looks for the bear, cat, tree, spider, beetle and moonkin forms, one common, one uncommon and one rare each.
- F8 to F10: looks for the dire bear, void monstrosity, shadowform, mechsuit, weaver and vizier forms.
- F6 and F7: twelve Collection forms sold only on the auction house.

Today a class form doesn't change how the character looks, and a Collection form is one still picture. Walking in all
four facings is the hook-up once the art lands (backlog).

---------------------------------------------------------------------
**Landed 20 Nov 2026**: F6 to F10 and I1 are sliced and in (F8 came back twice; the first was used). Earlier: F1 to F5.

## SHEET F1: the class forms, part 1  (paste this whole block)

Ids in order: `form_bear form_dire_bear form_cat form_moonkin form_tree_of_life form_shadowform`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. BEAR FORM - a big brown bear on all fours, thick shaggy fur, a pale muzzle, small fierce eyes, a few tribal bone beads and a leather band braided into the fur at its neck. Sturdy and protective.
2. DIRE BEAR FORM - a much larger, battle-scarred bear on all fours, dark umber fur, a heavy hump of shoulder muscle, huge claws, scars across the snout, horn-like growths of bark and antler at its shoulders, glowing pale green eyes. A primal guardian.
3. CAT FORM - a lean panther on all fours, sleek dark grey fur with faint darker stripes, a long tail curling up, bright yellow eyes, low and ready to pounce, a thin leather band with a feather at its throat.
4. MOONKIN FORM - a large round owl-bear standing upright on two thick legs, brown and white feathered body, a big owl face with huge round glowing eyes and a hooked beak, short antlers, broad feathered arms, a faint silver-blue moonlight glow.
5. TREE OF LIFE FORM - a walking tree spirit standing upright, a trunk of living pale bark shaped like a gentle tall figure, root-like legs, long branching arms covered in fresh green leaves and small white blossoms, a soft green-gold healing glow at its heart.
6. SHADOWFORM - a priest turned into living shadow: a hooded robed figure made of dark violet-black smoke, see-through at the edges where it fades to wisps, glowing pale purple eyes, tendrils of shadow curling from the hands.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F2: the class forms, part 2  (paste this whole block)

Ids in order: `form_void_monstrosity form_spider form_beetle form_weaver form_vizier form_mechsuit`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. VOID MONSTROSITY - a hulking horror from the deep void, much larger than a man, hunched on thick arms, deep indigo and black hide, a cluster of glowing violet eyes, a mouth ringed with small tentacles, more tentacles from its back, purple void crackle.
2. SPIDER FORM - a giant armoured spider the size of a wolf, glossy black and dark green carapace, eight long jointed legs, a cluster of glowing green eyes, dripping fangs, faint green venom glow in its abdomen markings.
3. BEETLE FORM - a huge heavy scarab beetle the size of a bear, a thick domed bronze-green shell with gold edges, a great horn on its head, sturdy legs planted wide, small glowing amber eyes. A walking fortress.
4. WEAVER FORM - an upright spider-folk caster, a slim insectoid body on four spindly spider legs, two thin arms spinning glowing pale green threads of silk between its claws, a crest of chitin on its head, many small glowing eyes, ragged silk wraps.
5. VIZIER FORM - a tall elegant spider-folk noble upright on four spider legs, a long purple chitin body in flowing dark green and gold robes with a high collar, a gold headpiece, a staff topped with a glowing green crystal.
6. MECHSUIT - a bulky goblin-built walking battle suit, man-height and a half, two thick piston legs, riveted iron and brass plating, a round glass cockpit on top with nobody visible inside, one clamp-claw arm and one short cannon arm, steam vents, warning stripes on the shoulders.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F3: bear and cat looks (common, uncommon, rare)  (paste this whole block)

Ids in order: `form_bear_black form_bear_ironhide form_bear_frostmane form_cat_plains_lion form_cat_snow_leopard form_cat_starlight`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. BLACK BEAR (common) - a bear on all fours with glossy black fur, a tan muzzle and a cream patch on its chest, a simple leather band with a wooden bead at its neck.
2. IRONHIDE BEAR (uncommon) - a big grey bear on all fours whose shoulders and back are covered in thick plates of dark bark and moss like natural armour, small mushrooms growing on them, amber eyes.
3. FROSTMANE BEAR (rare) - a huge white polar bear on all fours, thick frosted fur, jagged ice crystals growing from its shoulders and spine, glowing pale blue eyes, cold mist curling off its fur.
4. PLAINS LION (common) - a tawny mountain lion on all fours, sandy gold fur, a pale belly, a long tail with a dark tip, green eyes.
5. SNOW LEOPARD (uncommon) - a thick-furred snow leopard on all fours, white and pale grey fur with dark rosettes, a very long fluffy tail, ice-blue eyes.
6. STARLIGHT PANTHER (rare) - a sleek panther on all fours with deep midnight-blue fur full of tiny glittering stars like a night sky, faint silver constellation lines, glowing silver eyes, a soft starry shimmer trailing off its tail.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F4: tree of life and spider looks (common, uncommon, rare)  (paste this whole block)

Ids in order: `form_tree_autumn form_tree_willow form_tree_moonwood form_spider_forest form_spider_sand form_spider_crystal_widow`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. AUTUMN TREE (common) - the walking tree spirit standing upright, brown oak bark, its leafy arms in red, orange and yellow autumn leaves, a few acorns, a warm amber glow at its heart.
2. WILLOW TREE (uncommon) - a tall walking willow spirit standing upright, grey-green bark, long trailing curtains of thin green fronds hanging from its arms and head like hair, small fireflies around it.
3. MOONWOOD TREE (rare) - a walking tree spirit standing upright, silvery-white bark that shines softly, leaves of glowing pale blue, small silver blossoms, motes of moonlight drifting around it.
4. FOREST SPIDER (common) - a giant hairy brown spider the size of a wolf, banded legs, a cluster of black shiny eyes, fangs.
5. SAND SPIDER (uncommon) - a giant desert spider, pale sandy yellow with black bands on its legs and back, long thin legs, red eyes.
6. CRYSTAL WIDOW (rare) - a giant spider whose body and legs are made of see-through violet crystal glowing from inside, a bright violet hourglass mark on its back, glowing white eyes, small crystal shards along its legs.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F5: beetle and moonkin looks (common, uncommon, rare)  (paste this whole block)

Ids in order: `form_beetle_dusk form_beetle_jade form_beetle_sunfire form_moonkin_snowy form_moonkin_dusk form_moonkin_solar`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. DUSK SCARAB (common) - a huge scarab beetle, a plain dark brown shell with a dull sheen, a short horn, sturdy legs.
2. JADE SCARAB (uncommon) - a huge scarab beetle with a shining metallic green shell like polished jade, a long curved horn, gold edges on its leg joints.
3. SUNFIRE SCARAB (rare) - a huge scarab beetle with a shell of polished gold covered in glowing orange runes, a sun-disc crest on its head, faint heat shimmer above it.
4. SNOWY MOONKIN (common) - the owl-bear standing upright, white feathers with a few black flecks, pale yellow eyes, small grey antlers.
5. DUSK MOONKIN (uncommon) - the owl-bear standing upright, dark slate-grey feathers with deep violet tips, glowing violet eyes, dark curved antlers, a few faint stars around it.
6. SOLAR MOONKIN (rare) - the owl-bear standing upright, golden and orange feathers that glow at the tips, bright gold eyes, antlers like rays of sunlight, a warm sun halo behind its head.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F6: auction house forms, part 1  (paste this whole block)

Ids in order: `tycoon_golem treasure_mimic pearl_murloc_king bronze_drakonid gilded_infernal spirit_ancestor`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. TYCOON GOLEM - a squat clockwork harvest golem plated entirely in polished gold, a round furnace belly with a glowing orange coin slot, one arm a small sickle and the other holding a fat sack of coins, a tiny top hat bolted to its head.
2. TREASURE MIMIC - a big wooden treasure chest on four stubby clawed legs, its lid open like a grinning mouth full of sharp teeth and a long purple tongue, gold coins and a necklace spilling out, little glowing eyes peeking over the rim.
3. PEARL MURLOC KING - a fat, smug murloc standing tall, teal and orange scales, a crown made from a giant clam shell set with pearls, a cape of red seaweed, a coral trident, strings of pearls round its neck.
4. BRONZE DRAKONID - a tall winged dragon-man standing upright, bronze-gold scales, a long tail, horns sweeping back, wings half folded, a gold breastplate, holding an hourglass that glows with sand.
5. GILDED INFERNAL - a hulking rock golem, black stone body cracked with bright green fel fire, gold bands riveted onto its huge fists and shoulders, green flame pouring from its head and joints.
6. SPIRIT ANCESTOR - a towering tauren elder made of glowing pale blue spirit light, see-through, a long braided beard, horns hung with feathers and beads, a carved totem staff, small motes of light rising around it.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F7: auction house forms, part 2  (paste this whole block)

Ids in order: `living_geode opulent_furbolg goldleaf_treant silken_harpy_matriarch ember_djinn goldtooth_pirate_ghost`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. LIVING GEODE - a stocky rock elemental whose rough grey stone is split open across the chest and arms to show glittering purple amethyst and blue crystal inside, glowing softly, crystal shards growing from its shoulders.
2. OPULENT FURBOLG - a big, cheerful bear-folk shaman standing upright, shaggy brown fur, gold beads braided into it, a necklace of big gems, an embroidered vest, a staff topped with a glowing gem.
3. GOLDLEAF TREANT - a walking ancient tree with a wise bark face and a long mossy beard, its crown of leaves shining autumn gold and amber, a few gold leaves drifting down, roots for feet.
4. SILKEN HARPY MATRIARCH - a proud harpy queen standing on bird talons, large wings of emerald and gold peacock-like feathers, a sharp fierce face, a gold circlet and silk sashes, a long feathered tail.
5. EMBER DJINN - a fire spirit like a genie, a muscular upper body of glowing orange and gold flame, the lower body a swirling tail of smoke and fire instead of legs, gold bracers, a jewelled gold earring, a grand smirk.
6. GOLDTOOTH PIRATE GHOST - a ghostly pirate captain, pale green and see-through, a big tricorn hat with a feather, a long coat, a peg leg, a cutlass and a lantern, a wide grin full of solid gold teeth.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F8: dire bear and void monstrosity looks (common, uncommon, rare)  (paste this whole block)

Ids in order: `form_dire_bear_brown form_dire_bear_thornhide form_dire_bear_ancient form_void_monstrosity_drowned form_void_monstrosity_ashen form_void_monstrosity_starving`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. BROWN DIRE BEAR (common) - a huge brown bear on all fours, darker and heavier than a normal bear, a hump of shoulder muscle, long claws, a torn ear.
2. THORNHIDE DIRE BEAR (uncommon) - a huge bear on all fours, dark green-brown fur, long curved thorns and briar vines growing along its spine and shoulders, small red berries in the vines, yellow eyes.
3. ANCIENT GUARDIAN BEAR (rare) - an enormous elder bear on all fours, fur of grey stone and moss, glowing green runes carved into stone plates on its shoulders and brow, antlers like old branches, glowing green eyes, small leaves drifting off it.
4. DROWNED HORROR (common) - the void monstrosity hunched on thick arms, its hide grey-green and slick like something from the sea floor, barnacles, hanging seaweed, pale dead eyes, tentacles at the mouth.
5. ASHEN HORROR (uncommon) - the void monstrosity, its hide cracked black stone with dull red light in the cracks, ash drifting off its back, smoking tentacles, ember-red eyes.
6. STARVING DARK (rare) - the void monstrosity made of pure black void with a starfield inside its body, see-through at the edges, dozens of small glowing white eyes, a ring of violet light around its maw, tentacles fading into wisps.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F9: shadowform and mechsuit looks (common, uncommon, rare)  (paste this whole block)

Ids in order: `form_shadowform_grey form_shadowform_ember form_shadowform_eclipse form_mechsuit_rustbucket form_mechsuit_cobalt form_mechsuit_goldplated`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. GREY SHADE (common) - the hooded robed shadow figure made of thin grey smoke, see-through at the edges, pale white eyes.
2. EMBER SHADE (uncommon) - the hooded robed shadow figure made of black smoke with glowing orange embers drifting through it like a dying fire, ember-orange eyes.
3. ECLIPSE SHADE (rare) - the hooded robed shadow figure of pure black with a ring of white-gold light like a solar eclipse behind its hood, faint golden runes floating round it, glowing white eyes.
4. RUSTBUCKET MECHSUIT (common) - the goblin walking battle suit patched with mismatched rusty plates, dents, one leg a different colour, a wonky smoke stack, a cracked glass cockpit with nobody inside.
5. COBALT MECHSUIT (uncommon) - the goblin walking battle suit in clean cobalt-blue enamel plates with white warning stripes, a bright blue glowing engine core in the chest.
6. GOLD-PLATED MECHSUIT (rare) - the goblin walking battle suit with every plate polished gold, ruby rivets, crimson leather trim, a glowing green coin-shaped core in the chest, a tiny gold flag on its back.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET F10: weaver and vizier looks (common, uncommon, rare)  (paste this whole block)

Ids in order: `form_weaver_dusk form_weaver_silkmother form_weaver_spectral form_vizier_bronze form_vizier_obsidian form_vizier_royal`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the creatures themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE CREATURE TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest and its front. You CANNOT see its back or its tail. Its body is foreshortened, front-on.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, back or tail toward the RIGHT edge. You CAN see one eye and one full side of the body. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back and its tail if it has one. You absolutely CANNOT see its face, its eyes, its mouth or its chest.

These are the SHAPESHIFTED FORMS OF HEROES in a Horde fantasy RPG: the player walks around the world as this creature, so it must look heroic and powerful, not like a common monster, and must NOT have a saddle or a rider. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six creatures in every row, each turned according to that row's rule):
1. DUSK WEAVER (common) - the upright spider-folk caster on four spindly legs, a dull brown chitin body, spinning plain grey-white silk between its claws.
2. SILKMOTHER WEAVER (uncommon) - the upright spider-folk caster in cream and white chitin, wrapped in layers of fine white silk like a robe, a small silk egg sac on its back, spinning shining white thread.
3. SPECTRAL WEAVER (rare) - the upright spider-folk caster made of see-through pale blue ghost light, glowing threads trailing from its claws, faint chains of spirit silk floating around it.
4. BRONZE VIZIER (common) - the tall spider-folk noble on four legs, a bronze chitin body, plain brown robes, a wooden staff with a small amber stone.
5. OBSIDIAN VIZIER (uncommon) - the tall spider-folk noble in glossy black chitin, deep crimson robes with silver trim, a silver headpiece, a staff topped with a red crystal.
6. ROYAL VIZIER (rare) - the tall spider-folk noble in deep royal purple chitin with gold inlay, white and gold robes, a tall gold headpiece set with emeralds, a gold staff holding a floating glowing green orb.

Every creature fills roughly 70-85% of its cell. Keep design, colours and markings identical across the four facings of the same creature. Fully opaque except where a creature is described as see-through, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one creature from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET I1: 36 icons for the form looks  (paste this whole block)

One Collection icon per F3, F4, F5, F8, F9 and F10 look: the token you buy or find that teaches it. Sliced to
`assets/icons/collection/`. Attach `qi_journal.png`, `qi_horn.png` and `qi_signet.png` as the style reference.

```
Generate ONE image, 2048x2048, a grid of 6 columns x 6 rows = 36 separate square inventory icons, each about 341x341. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no magenta or pink inside the icons. Each is a small magical token that lets a druid or shapeshifter take on a new look: carved idols, charms, vials, cogs and brooches. Rare ones (every third icon) glow softly.

Icons, row by row, left to right:
Row 1: 1 a carved black bear idol with a tan muzzle; 2 a grey bear idol with bark and moss plates; 3 a white bear idol with ice crystals and a blue glow; 4 a tawny sandy-gold lion idol; 5 a white snow leopard idol with dark rosettes; 6 a midnight-blue panther idol full of glittering stars.
Row 2: 7 a little carved tree idol with red and orange autumn leaves; 8 a willow tree idol with long trailing green fronds; 9 a silver-barked tree idol with glowing pale blue leaves; 10 a hairy brown spider idol; 11 a pale yellow spider idol with black bands; 12 a see-through violet crystal spider glowing from inside.
Row 3: 13 a dark brown scarab idol; 14 a shining metallic green jade scarab; 15 a gold scarab with glowing orange runes; 16 a white owl-bear idol with yellow eyes; 17 a slate-grey owl-bear idol with violet eyes; 18 a golden owl-bear idol with a sun halo.
Row 4: 19 a heavy brown bear claw carved with a tribal line; 20 a bear idol wrapped in thorny briar vines with red berries; 21 a grey stone bear head with glowing green runes and branch antlers; 22 a grey-green tentacled idol crusted with barnacles; 23 a cracked black stone tentacle idol glowing red in the cracks; 24 a black orb with a starfield inside and a ring of violet light.
Row 5: 25 a small grey smoke wisp shaped like a hooded figure in a glass vial; 26 a vial of black smoke with orange embers drifting inside; 27 a black disc with a white-gold eclipse ring of light; 28 a rusty dented goblin cog with a bent bolt; 29 a cobalt-blue enamel cog with a glowing blue core; 30 a polished gold cog with ruby rivets and a green core.
Row 6: 31 a spool of plain grey-white spider silk; 32 a white silk egg sac on a spool of shining thread; 33 a spool of see-through glowing pale blue ghost silk; 34 a bronze chitin brooch with an amber stone; 35 a black chitin brooch with a red crystal; 36 a purple and gold chitin brooch set with emeralds.
```

Slices in this order:
```
col_look_bear_black, col_look_bear_ironhide, col_look_bear_frostmane, col_look_cat_plains_lion, col_look_cat_snow_leopard, col_look_cat_starlight,
col_look_tree_autumn, col_look_tree_willow, col_look_tree_moonwood, col_look_spider_forest, col_look_spider_sand, col_look_spider_crystal_widow,
col_look_beetle_dusk, col_look_beetle_jade, col_look_beetle_sunfire, col_look_moonkin_snowy, col_look_moonkin_dusk, col_look_moonkin_solar,
col_look_dire_bear_brown, col_look_dire_bear_thornhide, col_look_dire_bear_ancient, col_look_void_monstrosity_drowned, col_look_void_monstrosity_ashen, col_look_void_monstrosity_starving,
col_look_shadowform_grey, col_look_shadowform_ember, col_look_shadowform_eclipse, col_look_mechsuit_rustbucket, col_look_mechsuit_cobalt, col_look_mechsuit_goldplated,
col_look_weaver_dusk, col_look_weaver_silkmother, col_look_weaver_spectral, col_look_vizier_bronze, col_look_vizier_obsidian, col_look_vizier_royal
```
