# Rare wild mounts (2 sheets, 12 mounts)

Kyle, 18 Nov 2026: "Hit me with as much as you can!" Twelve more Collection mounts for the wild: rare tames and finds,
not the auction house. Where each one comes from is decided when they're built. Same layout as the Collection's
Sheet C: 6 columns x 4 rows, 1536x1024, magenta key, no rider. Slice with
`tools/asset_pipeline/slice_mount_sheet.py SHEET.png <the six ids>`. Attach `war_kodo_left.png` and
`rune_saber_down.png` as the style reference.

---------------------------------------------------------------------
**Landed 20 Nov 2026**: H9 and H10 are sliced (`assets/mounts`) and built: each mount drops at 5% from one open-world rare that fits it (`tools/build_collection.py` WILD_MOUNTS). Their reins wait on I2.

## SHEET H9: six rare wild mounts  (paste this whole block)

Ids in order: `stormhide_thunder_lizard plainstrider_matriarch ironback_crocolisk moonfeather_hippogryph sandreaver_silithid ashmane_hyena`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are RARE RIDING MOUNTS in a Horde fantasy RPG, the kind a lucky hero tames or wins out in the wild, shown with NO RIDER. Each wears rugged tribal tack (leather, bone, beads, feathers, painted hide) with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six animals in every row, each turned according to that row's rule):
1. STORMHIDE THUNDER LIZARD - a big, heavy, four-legged lizard with a thick blue-grey hide, a tall crest of bony plates down its back crackling with small white-blue lightning, a blunt horned head, a thick tail, bright yellow eyes.
2. PLAINSTRIDER MATRIARCH - a huge flightless savanna bird on two long powerful legs, a big round body of brown and cream feathers, a long neck, a hooked orange beak, a tall crest of red and white feathers. Painted hide saddle with bone beads.
3. IRONBACK CROCOLISK - a long, low crocodile on four short legs, dark green hide with thick iron-grey armoured scutes along its back, a long toothy snout, a heavy tail, small orange eyes. A saddle strapped between the scutes.
4. MOONFEATHER HIPPOGRYPH - standing on the ground with wings folded: the front half a great white-and-silver eagle with a hooked beak, the back half a deer with pale hooves, long feathered wings with silver-blue tips, small antlers, calm gold eyes.
5. SANDREAVER SILITHID - a large desert insect beast on six jointed legs, a sandy gold and brown chitin shell, a long armoured head with scything mandibles, a segmented tail curling up, many small black eyes. A saddle of bone and hide strapped to its shell.
6. ASHMANE HYENA - a big rangy hyena the size of a horse, sloped back, spotted tan and grey fur, a shaggy dark ash-black mane down its neck and spine, a wide toothy grin, rounded ears, a short bushy tail.

Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET H10: six more rare wild mounts  (paste this whole block)

Ids in order: `highpeak_ramgoat mudback_hydra thunderhorn_bull carrion_strider emberquill_porcupine shellback_snail`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are RARE RIDING MOUNTS in a Horde fantasy RPG, the kind a lucky hero tames or wins out in the wild, shown with NO RIDER. Each wears rugged tribal tack (leather, bone, beads, feathers, painted hide) with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six animals in every row, each turned according to that row's rule):
1. HIGHPEAK RAMGOAT - a big sure-footed mountain goat, shaggy white and grey coat, a long beard, two huge spiralling horns curling back, cloven hooves. A sturdy mountaineer's saddle with rope and a small bell.
2. MUDBACK HYDRA - a four-legged swamp beast with a heavy squat body and TWO long necks each ending in its own snake-like head, olive-green and brown mottled hide, frills on each head, a short thick tail.
3. THUNDERHORN BULL - a massive plains bison with a huge hump of dark brown wool, two thick curved horns, a heavy shaggy beard, small eyes, a tufted tail. A tauren saddle of painted hide and feathers.
4. CARRION STRIDER - a huge walking vulture as tall as a horse, wings half folded at its sides, ragged dark brown feathers, a bald red-grey neck and head, a heavy hooked beak, strong scaly legs.
5. EMBERQUILL PORCUPINE - a giant round porcupine the size of a kodo, a thick coat of long quills whose tips glow orange like embers, a small dark face with a brown nose, stubby legs. A saddle set into a cleared patch of quills.
6. SHELLBACK SNAIL - a giant riding snail with a huge spiral shell covered in moss, ferns and small mushrooms, a soft grey-green body, two long eye stalks, a lantern hanging from a pole fixed to the shell. A saddle sat on top of the shell.

Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```
