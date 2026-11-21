# Blood elf townsfolk: art prompts (sheets BE-M and BE-W)

**Status (21 Nov 2026): delivered and in the game** (`tools/asset_pipeline/slice_recruit_sheet6.py blood_elves`). BE-W's
fourth figure, the hooded ranger, came back bearded, so he's filed with the men (see `world/race_registry.py`). Kyle: "Do we need additional blood elf NPCs? Might as well populate
the world a bit", then "So give me a prompt for 24 male and 24 female". The eleven blood elf looks we have
(`assets/npcs/blood_elf/blood_elf_1` to `_11`) are all fighters and casters in battle dress, so every blood elf in
Dawnhaven looks like he's about to pull a sword. These two sheets are the people who live there: the ones rebuilding the
outpost, fishing off the pier, cooking at Dawnrest and keeping the Spire's lamps. Same layout as the Aetherian AE-M and
AE-W sheets (`docs/recruit_art_prompts_sheet6.md`). See `docs/art_status.md` for every sheet.

| Sheet | What | Image | Grid | Key |
|---|---|---|---|---|
| BE-M | 24 blood elf men, townsfolk and workers | 2048x2048 or bigger | 6 x 4 | magenta |
| BE-W | 24 blood elf women, townsfolk and workers | 2048x2048 or bigger | 6 x 4 | magenta |

**References to attach:** `assets/npcs/blood_elf/blood_elf_2/down.png`, `assets/npcs/blood_elf/blood_elf_6/down.png`
and `assets/npcs/blood_elf/blood_elf_11/down.png` (the style, the eyes and the ears), plus the BE-M image for BE-W once
you have it.

---------------------------------------------------------------------
## SHEET BE-M: BLOOD ELF MEN, 24  (paste this whole block)

```
Generate ONE sprite sheet image, as large as you can make it (ideally 2048x2048 or bigger), a grid of 6 columns x 4 rows = 24 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each character stands fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. Every character is a single standing figure, FULL BODY head to feet, facing straight toward the viewer (front view, "facing down" on a top-down game map), relaxed idle pose, arms at their sides or hands clasped, slight 3/4 top-down camera angle. Each figure has the same sturdy proportion as the attached references, roughly 1 : 1.5 (width : height), and all 24 are the SAME height in the cell. No ground shadow, no ground plane, no text, no labels, no grid lines. Match the attached references EXACTLY in style: crisp detailed pixel art with a clean dark outline, the same head size, the same rich colours, consistent lighting from the top-left. No magenta or pink anywhere in the characters. Nothing large held in the hands; small tools are fine.

THE PEOPLE: BLOOD ELF MEN, the same people as the attached references, survivors who have reclaimed an ancient elven outpost on an island that is forever in autumn. Slender and graceful, fair skin, long swept-back pointed ears, softly glowing green eyes. Hair in every shade from platinum and pale gold to honey, copper, auburn, chestnut and silver, worn long, tied back, braided or cropped. Their clothes are blood elf style but WORKADAY, not battle dress: crimson, gold, deep green, russet, amber and cream, with fine gold trim, sun and phoenix motifs on clasps and buckles, leather belts and boots, a few autumn-coloured cloaks. These are townsfolk and working people, NOT warriors: no armour except where it says so, no swords, no staves. They are proud and handsome, a little weathered from a hard year, hopeful. Ages vary from young men to elders. Every one is a different person with a different job, and you could tell any two apart at a glance.

The 24, in order, row by row:
Row 1: 1 a young apprentice magister in a short crimson robe with gold cuffs, a small book under one arm; 2 an elderly magister with long white hair and a neat white beard, deep crimson and gold robes, a gold circlet; 3 a Spire gate guard in crimson and gold half-plate, his phoenix-crested helm under his arm; 4 a ranger in green and russet leathers with a hooded cloak, a longbow slung on his back; 5 a dragonhawk handler with a heavy leather falconry glove, red and orange feathers stuck in his sleeves; 6 a carpenter with a tool belt and a hammer at his hip, sawdust on his sleeves rolled to the elbow.
Row 2: 7 a stonemason in a cream work shirt and a leather apron white with marble dust; 8 a fisherman in wading boots and rolled trousers, a coiled net over one shoulder, a sun-faded red cap; 9 a cook in a white apron over a crimson shirt, a wooden spoon tucked in his belt; 10 an innkeeper in a gold waistcoat over a white shirt, a cloth over one shoulder, a warm smile; 11 a travelling merchant in layered amber and crimson silks with gold rings and a coin purse; 12 a blacksmith, broad for an elf, in a scorched leather apron with heavy gloves tucked in his belt.
Row 3: 13 a priest of the Light in white and gold vestments with a gold sun disc on his chest; 14 an archivist in deep green robes with ink-stained fingers and spectacles on a gold chain; 15 an herbalist with a leaf-filled satchel and a bundle of red and gold herbs at his belt; 16 a refugee from the fallen elven cities, his fine crimson coat torn and patched, a bundle on his back, tired but proud; 17 a young courier, lean, in a short russet tunic with a satchel across his chest; 18 a spellbreaker off duty in a dark crimson coat with a gold collar, no weapon, very stern.
Row 4: 19 a boatwright with tarred hands and a coil of rope at his hip, a striped sailor's shirt under a leather vest; 20 a tailor with a measuring tape round his neck and pins in his lapel, an elegant fitted coat; 21 a lamplighter in a long amber coat holding a small lit taper; 22 a scarred old veteran with an eyepatch, grey hair tied back, a plain red coat with faded medals, leaning on a slim cane; 23 a young student in a plain cream tunic with a stack of two small books; 24 an elven lord in an ornate crimson and gold long coat with a jewelled phoenix brooch.

Keep every figure the same height and fully separated. Before you finish, check that there are 24 different men, each standing alone in his own cell on flat magenta.
```

---------------------------------------------------------------------
## SHEET BE-W: BLOOD ELF WOMEN, 24  (paste this whole block)

Attach the same three references, plus the Sheet BE-M image once you have it.

```
Generate ONE sprite sheet image, as large as you can make it (ideally 2048x2048 or bigger), a grid of 6 columns x 4 rows = 24 separate full-body character sprites. Flat pure #FF00FF magenta background everywhere. Each character stands fully inside its own cell with a wide margin and does NOT touch or overlap neighbours or the image edge. Every character is a single standing figure, FULL BODY head to feet, facing straight toward the viewer (front view, "facing down" on a top-down game map), relaxed idle pose, arms at their sides or hands clasped, slight 3/4 top-down camera angle. Each figure has the same sturdy proportion as the attached references, roughly 1 : 1.5 (width : height), and all 24 are the SAME height in the cell, the same height as the attached blood elf men. No ground shadow, no ground plane, no text, no labels, no grid lines. Match the attached references EXACTLY in style: crisp detailed pixel art with a clean dark outline, the same head size, the same rich colours, consistent lighting from the top-left. No magenta or pink anywhere in the characters. Nothing large held in the hands; small tools are fine.

THE PEOPLE: BLOOD ELF WOMEN, the same people as the attached references and the attached men, survivors who have reclaimed an ancient elven outpost on an island that is forever in autumn. Slender and graceful, fair skin, long swept-back pointed ears, softly glowing green eyes. Hair in every shade from platinum and pale gold to honey, copper, auburn, chestnut and silver, worn long, braided, crowned, pinned up or tied back for work. Their clothes are blood elf style but WORKADAY, not battle dress: crimson, gold, deep green, russet, amber and cream, with fine gold trim, sun and phoenix motifs on clasps and circlets, leather belts and boots, a few autumn-coloured cloaks. These are townsfolk and working people, NOT warriors: no armour except where it says so, no swords, no staves. They are proud and beautiful, a little weathered from a hard year, hopeful, with no heavy makeup and modest, practical clothing suited to their work. Ages vary from young women to elders. Every one is a different person with a different job, and you could tell any two apart at a glance.

The 24, in order, row by row:
Row 1: 1 a young apprentice magistrix in a short crimson robe with gold cuffs, a small book under one arm; 2 an elderly magistrix with silver hair in a crown of braids, deep crimson and gold robes, a gold circlet; 3 a Spire guard captain in crimson and gold half-plate, her phoenix-crested helm under her arm; 4 a ranger in green and russet leathers with a hooded cloak, a longbow slung on her back; 5 a dragonhawk handler with a heavy leather falconry glove and red and orange feathers braided into her hair; 6 a carpenter with a tool belt and a pencil behind her ear, sleeves rolled up, sawdust on her apron.
Row 2: 7 a weaver in a simple green dress with a shawl of shimmering gold cloth over her shoulders; 8 a fisherwoman in wading boots and rolled trousers, a coiled net over one shoulder, her hair under a red kerchief; 9 a baker in a flour-dusted white apron over a russet dress; 10 an innkeeper in a gold waistcoat and a long crimson skirt with an apron, keys at her belt; 11 a merchant in layered amber and crimson silks with gold bangles and a coin purse; 12 an enchanter in violet and gold with a small glowing gold rune floating over her palm.
Row 3: 13 a priestess of the Light in white and gold vestments with a gold sun disc on her chest; 14 a healer in cream and pale green robes with a satchel of bandages and a small crystal vial; 15 an herbalist with a leaf-filled satchel and a wreath of red and gold leaves in her hair; 16 a refugee from the fallen elven cities, her fine crimson gown torn and patched, a bundle in her arms, tired but proud; 17 a young courier, lean, in a short russet tunic and leggings with a satchel across her chest; 18 an orchard keeper in earth-green work clothes with a basket of red apples on her hip.
Row 4: 19 a scribe in a neat cream dress with a writing case on a strap; 20 a tailor with a measuring tape round her neck and pins in her collar, an elegant fitted coat; 21 a lamplighter in a long amber coat holding a small lit taper; 22 a sharp-eyed old matriarch with white hair pinned up, a dark crimson shawl and a slim cane; 23 a young student in a plain cream tunic with a stack of two small books; 24 an elven lady in an ornate crimson and gold gown with a jewelled phoenix brooch.

Keep every figure the same height and fully separated. Before you finish, check that there are 24 different women, each standing alone in her own cell on flat magenta.
```

If the generator makes two 6x2 images instead of one 6x4, that's fine: the slicer reads the figures in order either way.

---------------------------------------------------------------------
## After you generate them

- **BE-M and BE-W** slice into `assets/npcs/blood_elf/blood_elf_m1` to `blood_elf_m24` and `blood_elf_w1` to
  `blood_elf_w24` (`down.png` each), in the sheets' order:
  - men: apprentice, elder magister, gate guard, ranger, hawk handler, carpenter, stonemason, fisherman, cook,
    innkeeper, merchant, blacksmith, priest, archivist, herbalist, refugee, courier, spellbreaker, boatwright, tailor,
    lamplighter, veteran, student, lord;
  - women: apprentice, elder magistrix, guard captain, ranger, hawk handler, carpenter, weaver, fisherwoman, baker,
    innkeeper, merchant, enchanter, priestess, healer, herbalist, refugee, courier, orchard keeper, scribe, tailor,
    lamplighter, matriarch, student, lady.
- They're front-only, like the furbolgs and the Aetherian townsfolk, so they're **NPC looks, not player looks**: the
  blood elf is playable and its character-creation pool (`_BLOOD_ELF_VARIANTS`, the eleven four-direction looks) stays as
  it is. The new looks get their own NPC list in `world/race_registry.py`, split male and female, which ends the
  unisex blood elf pool for NPCs.
- Then Dawnhaven's people (`tools/build_dawnhaven_people.py`) swap onto them by job: the guards, the carpenter, the
  fisher, the cook, the innkeeper, the priestess, the courier and so on. The rest go to the blood elves elsewhere
  (Kael's Bastion, the Crimson Codex, the Crystalline Underdark).
