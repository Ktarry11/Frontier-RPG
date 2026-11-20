# Player sprites: five male looks a race, four facings each

**Landed 20 Nov 2026, all seven sheets** (`tools/building_sheets/player_p1_human.png` to `player_p7_veyr.png`), sliced
into `<race>/<race>_p1` to `_p5` (`human/male/male_p1`...). Five of the seven drew both side rows facing right, so their
left is the right mirrored; the Tauren and Veyr drew a real left (in the other row). The new looks are on the end of each
male list in `world/race_registry.py` (`NEW_MALE_LOOKS`), and the creator and the barber offer only them. The Aetherian
and Veyr looks wait on disk for those races to be playable.

Kyle, 20 Nov 2026: "So lets have orcs, tauren, undead, aetherian, humans, and belfs" as the playable races, with an
Aetherian start zone and a blood elf one to come; then "Lets get the 5 birds as well" (the Veyr). Seven sheets
(P1 to P7).

Kyle, 20 Nov 2026: "Walk cycles will come after better sprites. I am thinking just doing about 5 sprites from each race
the player can pick from and then adding walk cyles to these later", "ensure that the sprites have 4 degrees of
movement. Start with male only, none of my friends play female", and "Ensure they dont carry stuff in their hands,
that fucks with movement as we saw".

Seven sheets, one per race: five men across, each turned four ways down the column (front, left, right,
back), the same layout as the mount sheets. Empty hands and no weapons anywhere, so the walk cycles can be drawn on
these later without anything floating.

**Attach three images with each sheet** (the most the chat takes): two recruit sprites for the style
(`assets/npcs/recruits/wes_warrior/down.png` and `assets/npcs/recruits/dale_reaper/down.png`, the best people art in the
game) and the one race reference the sheet names, for the race's look only (not its style or its pose).

**When they come back:** each look goes in its own folder (`male_p1`, `orc_p1` and so on) and is added to the END of
that race's male list in `world/race_registry.py`, so every saved character keeps the face it has (a save stores its
look as a place in that list). The character creator then offers only the new five for men; the older looks stay as
townsfolk and vendors, so the world keeps its variety. Women are unchanged for now.

---------------------------------------------------------------------

## SHEET P1: HUMAN men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/npcs/human/male/male_1/down.png` (what a human looks like).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Human man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His nose points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one ear, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His nose points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a braid, an earring, a shoulder piece, a tattoo, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head, his back, his shoulders and the heels of both feet. You CANNOT see his face, his eyes, his mouth or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's face, hair, skin, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

Columns, left to right (the same five Human men in every row, each turned according to that row's rule):
1. A white man of about 30, short sandy-blond hair, light stubble, clear blue eyes, an open, very handsome face; a dark green linen tunic under a brown leather jerkin, a belt with one small pouch, dark trousers, worn brown boots.
2. A Latino man of about 32, thick black wavy hair pushed back, a short neat beard, warm brown skin, dark eyes, a strikingly handsome face; a rust-red tunic with the sleeves rolled to the elbow, a dark leather vest, grey trousers, boots.
3. A Middle Eastern man of about 35, short black hair, a well-groomed full black beard, olive skin, dark eyes, a strong, very handsome face; a deep blue tunic with an embroidered collar, a wide sand-coloured sash for a belt, dark trousers, low boots.
4. A Black man of about 28, tall and athletic, close-cropped hair, clean-shaven, deep brown skin, a very handsome face with a calm look; a pale grey linen shirt under a fitted brown leather jerkin, dark trousers, boots.
5. A white man of about 40, dark brown hair going grey at the temples, a short beard, green eyes, a rugged, very handsome weathered face; a cream shirt under a short dark leather coat that stops at the hip, brown trousers, scuffed boots.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png human/male/male_p1 human/male/male_p2 human/male/male_p3 human/male/male_p4 human/male/male_p5`.

---------------------------------------------------------------------

## SHEET P2: ORC men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/npcs/orc/orc_5/down.png` (what a orc looks like).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Orc man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His nose points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one ear, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His nose points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a braid, an earring, a shoulder piece, a tattoo, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head, his back, his shoulders and the heels of both feet. You CANNOT see his face, his eyes, his mouth or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's face, hair, skin, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

Columns, left to right (the same five Orc men in every row, each turned according to that row's rule):
1. A young green-skinned orc, lean and muscular, a black topknot with the sides shaved, small lower tusks, amber eyes; a leather chest harness over bare skin, cloth wraps on the forearms, fur-trimmed brown trousers, wrapped feet.
2. A dark-green veteran orc, broad and heavy, a shaved head with black tribal tattoos over the scalp, big lower tusks, a scar across the nose; a studded leather vest, a wide belt, dark trousers, heavy boots.
3. A brown-skinned orc, powerful, long black hair in thick braids and a beard braided with bone beads, medium tusks; a hide jerkin laced at the front, hide trousers, fur boots.
4. A grey-skinned orc, tall and rangy, a black mohawk, three iron rings in one ear, a heavy brow, sharp tusks; a sleeveless dark red tunic, one leather pauldron on his left shoulder only, black trousers, boots.
5. An olive-green orc in his prime, very strong, long grey hair tied back, a short grey goatee, deep-set eyes, chipped tusks; a cream linen shirt open at the chest, a red sash belt, brown trousers, sandals.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png orc/orc_p1 orc/orc_p2 orc/orc_p3 orc/orc_p4 orc/orc_p5`.

---------------------------------------------------------------------

## SHEET P3: BLOOD ELF men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/npcs/blood_elf/blood_elf_1/down.png` (what a blood elf looks like).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Blood Elf man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His nose points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one ear, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His nose points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a braid, an earring, a shoulder piece, a tattoo, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head, his back, his shoulders and the heels of both feet. You CANNOT see his face, his eyes, his mouth or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's face, hair, skin, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

Columns, left to right (the same five Blood Elf men in every row, each turned according to that row's rule):
1. A slender blood elf man, long straight platinum-blond hair, long swept-back pointed ears, glowing pale green eyes, a beautiful, sharp-featured face; a crimson tunic with gold trim and a high collar, a gold-buckled belt, fitted dark trousers, tall boots.
2. A blood elf man with long red hair in a high ponytail, long pointed ears, glowing pale green eyes, a strikingly handsome face; a fitted black and dark red doublet, a short red mantle on the shoulders, dark trousers, boots.
3. A blood elf man with shoulder-length black hair, long pointed ears, glowing pale green eyes, a handsome, cool face; a white and gold tunic with fine embroidery, a slim gold belt, white trousers, gold-trimmed boots.
4. A blood elf man with short silver-white hair swept back, long pointed ears, glowing pale green eyes, a handsome, sharp face with high cheekbones; a forest green and gold tunic, a brown leather belt, dark trousers, boots.
5. A blood elf man with golden hair in one long braid over his right shoulder, long pointed ears, glowing pale green eyes, a beautiful, warm face; burgundy leathers with gold stitching, a fitted vest over a cream shirt, dark trousers, boots.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png blood_elf/blood_elf_p1 blood_elf/blood_elf_p2 blood_elf/blood_elf_p3 blood_elf/blood_elf_p4 blood_elf/blood_elf_p5`.

---------------------------------------------------------------------

## SHEET P4: FORSAKEN men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/npcs/forsaken/forsaken_1/down.png` (what a forsaken looks like).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Forsaken man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His nose points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one ear, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His nose points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a braid, an earring, a shoulder piece, a tattoo, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head, his back, his shoulders and the heels of both feet. You CANNOT see his face, his eyes, his mouth or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's face, hair, skin, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

Columns, left to right (the same five Forsaken men in every row, each turned according to that row's rule):
1. A tall, gaunt Forsaken man, grey-green skin, long lank black hair, glowing yellow eyes, part of his jawbone showing through the skin on one side, still a striking face; a long-sleeved dark grey shirt, a black leather vest, dark trousers, worn boots.
2. A Forsaken man with a bald, stitched scalp, pale grey-blue skin, glowing yellow eyes, a sharp, hollow-cheeked face; a tattered purple tunic, a black sash, dark trousers, wrapped shins.
3. A Forsaken man with stringy white hair to his shoulders, ashen skin, glowing yellow eyes, a thin face with a fixed half-grin; a faded brown coat cut short at the waist over a grey shirt, belted, dark trousers, boots.
4. A hunched Forsaken man, short brown hair, grey-green skin, glowing yellow eyes, a few ribs showing through a tear in his shirt; a torn cream shirt, a dark leather jerkin, black trousers, one boot buckled higher than the other.
5. A Forsaken man with a dark ponytail and the remains of a beard, mottled grey skin, glowing yellow eyes, a once very handsome face; a fitted black leather vest over a dark green shirt, a belt with rusted buckles, dark trousers, boots.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png forsaken/forsaken_p1 forsaken/forsaken_p2 forsaken/forsaken_p3 forsaken/forsaken_p4 forsaken/forsaken_p5`.

---------------------------------------------------------------------

## SHEET P5: TAUREN men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/npcs/tauren/tauren_1/down.png` (what a tauren looks like).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Tauren man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His nose points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one ear, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His nose points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a braid, an earring, a shoulder piece, a tattoo, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head, his back, his shoulders and the heels of both feet. You CANNOT see his face, his eyes, his mouth or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's face, hair, skin, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

Columns, left to right (the same five Tauren men in every row, each turned according to that row's rule):
1. A big brown-furred tauren man, great curved horns, a brass nose ring, two long braids hanging from behind the horns; a painted hide vest, a hide kilt, bare hooves.
2. A black-furred tauren man with a white muzzle, short thick horns, broad and heavy; a deep red sash across the chest, a leather kilt with bone toggles, bare hooves.
3. A tan, golden-furred tauren man, long straight horns hung with small beads, feathered braids, a calm face; a cream woven tunic with a blue zig-zag band, a belt of braided leather, bare hooves.
4. An elder tauren man with grey-white spotted fur, one horn cracked at the tip, white paint lines on the face, still strong; a fringed hide shirt, a hide kilt, bare hooves.
5. A reddish-brown tauren man with a white blaze down the face, horns bound with bronze bands, a short mane; a teal cloth wrap over one shoulder, a leather kilt, bare hooves.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png tauren/tauren_p1 tauren/tauren_p2 tauren/tauren_p3 tauren/tauren_p4 tauren/tauren_p5`.

---------------------------------------------------------------------

## SHEET P6: AETHERIAN men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/creatures/ae_scholar.png` (what an Aetherian looks like; anything he holds is NOT wanted).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Aetherian man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His nose points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one ear, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His nose points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a braid, an earring, a shoulder piece, a tattoo, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head, his back, his shoulders and the heels of both feet. You CANNOT see his face, his eyes, his mouth or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's face, hair, skin, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

WHAT AN AETHERIAN LOOKS LIKE (match the attached Aetherian exactly in these): taller and longer-limbed than a human, slender and upright, with a narrow, slightly elongated skull and long, swept-back pointed ears. Skin smooth like polished stone, either pale blue-grey or warm bronze. Eyes glow evenly with no visible pupil. Natural crystals GROW out of them like geodes breaking through the skin: always a crown of crystal points rising from the top of the head, and on some, smaller crystals along the brow, the cheekbones, the shoulders or the backs of the hands. Their clothes are high-collared and fitted, white, blue and cream trimmed with gold, with small bronze fittings and a crystal set at the chest; elegant and a little imperial. They are NOT birds and have no feathers or beaks.

Columns, left to right (the same five Aetherian men in every row, each turned according to that row's rule):
1. A tall Aetherian man with pale blue-grey skin, short silver-white hair swept back, luminous pale-blue eyes, small blue crystals growing along his brow and cheekbones, a proud, strikingly handsome face; a long-sleeved white and gold tunic to mid-thigh with a high collar, a slim gold belt, fitted grey trousers, soft white boots.
2. A tall Aetherian man with warm bronze skin, a shaved head, luminous gold eyes, a ridge of small amber crystals along the top of his skull and the backs of his hands, a strong, very handsome face; a royal blue tunic with gold filigree at the hem, a white sash, dark trousers, bronze-buckled boots.
3. A tall Aetherian man with pale blue-grey skin, long straight black hair tied low at the neck, luminous violet eyes, a cluster of violet crystals on his left shoulder only, a calm, beautiful face; a fitted grey-white scholar's coat cut at the hip over a dark shirt, a belt of bronze rings, dark trousers, boots.
4. A tall Aetherian man with bronze skin, short copper-red hair, luminous sky-blue eyes, thin lines of blue crystal tracing his jaw and neck, an open, very handsome young face; a sleeveless white and sky-blue tunic, a bronze bracer on each forearm, white trousers, sandals.
5. A tall, older Aetherian man with pale blue-grey skin, a short white beard and white hair to his shoulders, luminous pale-gold eyes, larger crystals crowning his brow like a circlet, a severe, handsome face; a deep blue tunic with a gold-embroidered collar, a short white mantle over the shoulders, grey trousers, boots.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png aetherian/aetherian_p1 aetherian/aetherian_p2 aetherian/aetherian_p3 aetherian/aetherian_p4 aetherian/aetherian_p5`. The Aetherians aren't a playable race yet; the folder and the race entry are made when their start zone is built.

---------------------------------------------------------------------

## SHEET P7: VEYR men  (paste this whole block)

Attach `assets/npcs/recruits/wes_warrior/down.png`, `assets/npcs/recruits/dale_reaper/down.png` (style) and `assets/creatures/vy_scout.png` (what a Veyr looks like; the blades he holds are NOT wanted).

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 4 rows = 20 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Painterly semi-realistic WoW Classic art style matching the attached style references exactly in outline, shading and level of detail, a slight 3/4 top-down camera, consistent soft lighting from the top-left, crisp clean edges. Never use magenta or pink on the characters.

THESE ARE THE LOOKS A PLAYER PICKS FOR THEIR OWN CHARACTER, so each is one ordinary Veyr man in plain, class-neutral starting clothes from his own people's culture (no armour, no robes of any one class), handsome and strong in a grounded, lived-in way: good bone structure, good posture, clear features, not airbrushed, not exaggerated.

HANDS ARE EMPTY. Nothing is held, nothing is carried, and there is no weapon ANYWHERE: not in the hands, not on the back, not on the belt, no staff, no shield, no bag, no torch. Arms hang relaxed at the sides with open hands. No long cloak or loose cape (it fights with walking later); a short mantle or a sash is fine. The game draws walking on these later, and anything held breaks it.

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE MAN TURNED FOUR DIFFERENT WAYS. Each COLUMN is one character. The four ROWS of that column are that same man ROTATED ON THE SPOT and seen from four different directions. If a column looks like the same picture four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (walking down the screen). You see his whole face, both eyes, his chest, and the toes of both feet pointing at the camera.

Row 2 - FACING LEFT, a full side profile. His beak points to the LEFT edge of his cell and the back of his head to the right. You see one eye, one side of his body, the near arm in front of the body, and both legs in profile. You do NOT see his chest front-on or both eyes.

Row 3 - FACING RIGHT, a full side profile. His beak points to the RIGHT edge of his cell. DRAW this side, don't mirror row 2: anything worn on one side (a bead, a band, a shoulder piece, a scar) stays on the same side of his body, so it's on the far side here.

Row 4 - FACING AWAY (walking up the screen), seen from directly behind. You see the back of his head and crest, his back, his tail feathers and the heels of both feet. You CANNOT see his face, his eyes, his beak or his chest.

Standing neutral in every row: feet slightly apart, weight even, no stride yet. Every figure is the SAME height as the others of his race, centred in his cell, feet on the same baseline near the bottom of the cell, filling about 80% of the cell's height. Keep each man's head, plumage, clothes, colours and proportions identical across his four rows.

Before you finish, check the image: every column shows one man from the front, then his left side, then his right side, then his back, and nobody is holding anything. If any column shows the same view twice, or anyone holds something, redraw that column.

WHAT A VEYR LOOKS LIKE (match the attached Veyr exactly in these): an avian humanoid, a man's height and build but a bird of prey above the shoulders. A hawk's or eagle's head with a strong hooked beak and sharp, bright eyes, a crest of long feathers sweeping back from the crown. Feathers cover the head, neck and shoulders and run down the outside of each forearm in a short fringe of flight feathers (folded close to the arm, never spread like wings). Hands are four-fingered and clawed, and EMPTY. Legs bend like a bird's and end in big scaled talons, no boots. A short fan of tail feathers. Lean and muscular, proud and predatory. They dress light for flying: leather harnesses and chest straps, short kilts or wrapped trousers, copper and storm-blue fittings, clan beads and feathers. They are NOT Aetherians and have no crystals.

Columns, left to right (the same five Veyr men in every row, each turned according to that row's rule):
1. A Veyr man with an eagle's head, a vivid red crest and a white face, a golden beak, amber eyes; a brown leather chest harness with copper buckles, a red and brown clan kilt, copper bands on his upper arms.
2. A Veyr man with a slate-grey storm hawk's head, a crest of storm-blue feathers, a dark grey beak, pale yellow eyes, grey barred plumage; a dark blue sleeveless jerkin, a wide belt with lightning-bolt copper studs, wrapped grey trousers.
3. A Veyr man with a golden-brown hawk's head, a cream throat and a barred chest, a short tawny crest, a black-tipped yellow beak, dark eyes; a light leather vest laced at the front, a green sash, a short leather kilt.
4. A Veyr man with a glossy black raven-like head and a heavy black beak, a ragged black crest with one silver bead tied in it, grey eyes; a black and silver harness over bare feathers, a dark kilt, a silver ring on each forearm.
5. A Veyr man with a white falcon's head speckled with grey, a short white crest, a pale blue-grey beak, dark eyes, white plumage down his arms; a cream tunic cut short with a storm-blue border, a braided leather belt, wrapped cream trousers.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_player_sheet.py SHEET.png veyr/veyr_p1 veyr/veyr_p2 veyr/veyr_p3 veyr/veyr_p4 veyr/veyr_p5`. The Veyr aren't a playable race yet; the folder and the race entry are made when they are.

---------------------------------------------------------------------

## WALK CYCLES: one sheet a race, from its turnaround sheet

**Landed 20 Nov 2026 (Kyle tried three men a sheet, then two: "could i maybe have 3 figures side by side?"):** walk
cycles for every human, orc, blood elf, Forsaken and tauren look (`tools/building_sheets/walk_*.png`). The references were
each race's turnaround cut into its first three and last two men, one picture each. Blood elves 1 to 3 came back with
five rows, missing the last walking-right step, so they walk front and back and stand still sideways until that
sheet is re-rolled. The Veyr and the Aetherians are next.

Kyle, 20 Nov 2026: "when i upload to chatgpt i can only upload 3 pics....so can we bunch these characters up". The
race's own turnaround sheet already has all five men turned four ways in ONE picture, so it's the only reference
needed. The game walks left foot, stand, right foot, stand, and the stand is the turnaround's own frame, so each
direction needs just two new frames; walking left is walking right mirrored. Five men, three directions, two steps:
30 figures on one sheet.

**Attach ONE image: that race's turnaround sheet** (the one ChatGPT made you), and paste this, putting the race's name
where it says RACE:

```
Generate ONE sprite sheet image, 1024x1536 (portrait), a grid of 5 columns x 6 rows = 30 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each figure sits fully inside its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No ground, no ground shadow, no text, no labels, no numbers, no grid lines, no frames. Never use magenta or pink on the characters.

The attached image is a turnaround sheet of five RACE men: each COLUMN is one man, shown from the front, his left side, his right side and his back. Redraw the SAME five men, in the SAME column order, EXACTLY as they appear there: same face, hair, skin, fur or feathers, clothes, colours, proportions, height and painterly style. Nothing about them changes except that now they are WALKING.

Their hands stay EMPTY: nothing held, nothing carried, no weapons anywhere. Arms swing naturally and opposite to the legs, a relaxed walking stride, not a run, not a march.

Each column is one man; the six rows are six frames of him walking:
Row 1 - walking TOWARD the viewer (facing front, as in his front view), LEFT foot stepping forward, right arm swinging forward.
Row 2 - walking TOWARD the viewer (facing front), RIGHT foot stepping forward, left arm swinging forward.
Row 3 - walking AWAY from the viewer (seen from behind, as in his back view), LEFT foot stepping forward, right arm swinging forward.
Row 4 - walking AWAY from the viewer (seen from behind), RIGHT foot stepping forward, left arm swinging forward.
Row 5 - walking to the RIGHT (side profile facing right, as in his right-facing view), LEFT foot stepping forward, right arm swinging forward.
Row 6 - walking to the RIGHT (side profile facing right), RIGHT foot stepping forward, left arm swinging forward.

Every figure the same height as he is in the attached sheet, centred in his cell, the planted foot on the same baseline near the bottom of the cell. Keep the stride small and readable so the frames loop smoothly with his standing pose between them.

Before you finish, check the image: five columns, the same five men in the attached order; rows 1-2 face front, rows 3-4 show their backs, rows 5-6 face right; in each pair one frame has the left foot forward and the other the right; and nobody is holding anything. Redraw any column that breaks a rule.
```

| Race | Attach | Slice |
|---|---|---|
| Human | `tools/building_sheets/player_p1_human.png` | `slice_walk_rows.py SHEET.png human/male/male_p1 human/male/male_p2 human/male/male_p3 human/male/male_p4 human/male/male_p5` |
| Orc | `player_p2_orc.png` | `slice_walk_rows.py SHEET.png orc/orc_p1 orc/orc_p2 orc/orc_p3 orc/orc_p4 orc/orc_p5` |
| Blood Elf | `player_p3_blood_elf.png` | `slice_walk_rows.py SHEET.png blood_elf/blood_elf_p1 ... blood_elf/blood_elf_p5` |
| Forsaken | `player_p4_forsaken.png` | `slice_walk_rows.py SHEET.png forsaken/forsaken_p1 ... forsaken/forsaken_p5` |
| Tauren | `player_p5_tauren.png` | `slice_walk_rows.py SHEET.png tauren/tauren_p1 ... tauren/tauren_p5` |
| Aetherian | `player_p6_aetherian.png` | `slice_walk_rows.py SHEET.png aetherian/aetherian_p1 ... aetherian/aetherian_p5` |
| Veyr | `player_p7_veyr.png` | `slice_walk_rows.py SHEET.png veyr/veyr_p1 ... veyr/veyr_p5` |

(`PYTHONPATH=. python3 tools/asset_pipeline/slice_walk_rows.py`, which writes `walk_<down|up|right|left>_<1|2|3>.png` into
each look's folder; frame 2 is the standing turnaround frame.)

Then the women's looks, when Kyle wants them.
