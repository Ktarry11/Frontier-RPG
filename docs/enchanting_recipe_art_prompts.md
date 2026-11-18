# Enchanting and recipe-scroll art (7 sheets, 252 icons)

Kyle, 17 Nov 2026: "Can you give me like.... 36 x 4 things for enchanting???" and "another 36 x 3 for other recipies found in the game?! They dont need to be unique but they should be similar.....like each professions get about 6-8 unique ones".

**Enchanting (sheets EN1-EN4, 144 icons).** Today all 176 enchant scrolls are one picture. Each enchant family (a slot and a stat, like Bracer Stamina) gets a lesser scroll for its lower ranks and a greater scroll for its upper ranks; the weapon procs and shoulder inscriptions get one each. That's 130. The other 14 are the four enchanted wands and the ten enchanting oils.

**Recipe scrolls (sheets RC1-RC3, 108 icons).** Today each profession's scrolls are one picture. Each profession gets ten: five skill grades, found (a drop) or bought (a vendor's or a faction's). The six that craft epics get an epic one too. Last come Timbermaw Warhide (the one crafted epic still borrowing an icon) and a plain default scroll. A profession runs across a sheet break in a few places; every cell describes itself, so that's fine.

Send each sheet back and I'll slice it in by cell number (tools/enchant_recipe_art.py holds the lists).

## Sheet EN1

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate enchanting icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE SCROLLS: every SCROLL is the same object, so they read as one family. A LESSER scroll is a small rolled parchment scroll, half unrolled, tied with plain twine; on its open part a rune circle glows softly in the colour named, and inside the circle is a small silhouette of the item named (a bracer, a boot, a gauntlet...). A GREATER scroll is the same idea grander: thick vellum on dark wooden rollers with gold caps and a wax seal, its rune circle blazing in the colour named, small sparks rising. Where a colour is 'half X, half Y', the rune circle is split down the middle in those two colours. An INSCRIPTION is a small engraved medallion instead of a scroll. Wands and oils are as described.

Row by row, left to right:

Row 1:
1. LESSER scroll, a bracer silhouette, glowing deep crimson red [BRACER STAMINA]
2. GREATER scroll, a bracer silhouette, glowing deep crimson red [BRACER STAMINA]
3. LESSER scroll, a bracer silhouette, glowing burnt orange [BRACER STRENGTH]
4. GREATER scroll, a bracer silhouette, glowing burnt orange [BRACER STRENGTH]
5. LESSER scroll, a bracer silhouette, glowing pale silver-white [BRACER SPIRIT]
6. GREATER scroll, a bracer silhouette, glowing pale silver-white [BRACER SPIRIT]

Row 2:
7. LESSER scroll, a bracer silhouette, glowing leaf green [BRACER AGILITY]
8. GREATER scroll, a bracer silhouette, glowing leaf green [BRACER AGILITY]
9. LESSER scroll, a bracer silhouette, glowing royal blue [BRACER INTELLECT]
10. GREATER scroll, a bracer silhouette, glowing royal blue [BRACER INTELLECT]
11. LESSER scroll, a bracer silhouette, glowing aqua cyan [BRACER MANA REGENERATION]
12. GREATER scroll, a bracer silhouette, glowing aqua cyan [BRACER MANA REGENERATION]

Row 3:
13. LESSER scroll, a bracer silhouette, glowing warm gold [BRACER HEALING]
14. GREATER scroll, a bracer silhouette, glowing warm gold [BRACER HEALING]
15. LESSER scroll, a bracer silhouette, glowing half crimson, half royal blue [BRACER VALOR]
16. GREATER scroll, a bracer silhouette, glowing half crimson, half royal blue [BRACER VALOR]
17. LESSER scroll, a bracer silhouette, glowing half leaf green, half royal blue [BRACER WILDHEART]
18. GREATER scroll, a bracer silhouette, glowing half leaf green, half royal blue [BRACER WILDHEART]

Row 4:
19. LESSER scroll, a bracer silhouette, glowing half burnt orange, half warm gold [BRACER DEVOTION]
20. GREATER scroll, a bracer silhouette, glowing half burnt orange, half warm gold [BRACER DEVOTION]
21. LESSER scroll, a boot silhouette, glowing deep crimson red [BOOTS STAMINA]
22. GREATER scroll, a boot silhouette, glowing deep crimson red [BOOTS STAMINA]
23. LESSER scroll, a boot silhouette, glowing leaf green [BOOTS AGILITY]
24. GREATER scroll, a boot silhouette, glowing leaf green [BOOTS AGILITY]

Row 5:
25. LESSER scroll, a boot silhouette, glowing pale silver-white [BOOTS SPIRIT]
26. GREATER scroll, a boot silhouette, glowing pale silver-white [BOOTS SPIRIT]
27. LESSER scroll, a boot silhouette, glowing half leaf green, half crimson [BOOTS SWIFTNESS]
28. GREATER scroll, a boot silhouette, glowing half leaf green, half crimson [BOOTS SWIFTNESS]
29. LESSER scroll, a boot silhouette, glowing half burnt orange, half crimson [BOOTS VIGOR]
30. GREATER scroll, a boot silhouette, glowing half burnt orange, half crimson [BOOTS VIGOR]

Row 6:
31. LESSER scroll, a boot silhouette, glowing half leaf green, half violet, with a tiny lightning fork [BOOTS STORMCALLER]
32. GREATER scroll, a boot silhouette, glowing half leaf green, half violet, with a tiny lightning fork [BOOTS STORMCALLER]
33. An enchanted wand of plain pale wood tipped with a pale blue crystal
34. An enchanted wand of carved wood tipped with a green crystal, vine carving
35. An enchanted wand of dark wood tipped with a violet crystal, faint smoke
36. An enchanted wand of white-gold wood tipped with a radiant white gem
```

## Sheet EN2

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate enchanting icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE SCROLLS: every SCROLL is the same object, so they read as one family. A LESSER scroll is a small rolled parchment scroll, half unrolled, tied with plain twine; on its open part a rune circle glows softly in the colour named, and inside the circle is a small silhouette of the item named (a bracer, a boot, a gauntlet...). A GREATER scroll is the same idea grander: thick vellum on dark wooden rollers with gold caps and a wax seal, its rune circle blazing in the colour named, small sparks rising. Where a colour is 'half X, half Y', the rune circle is split down the middle in those two colours. An INSCRIPTION is a small engraved medallion instead of a scroll. Wands and oils are as described.

Row by row, left to right:

Row 1:
1. LESSER scroll, a gauntlet silhouette, glowing burnt orange [GLOVES STRENGTH]
2. GREATER scroll, a gauntlet silhouette, glowing burnt orange [GLOVES STRENGTH]
3. LESSER scroll, a gauntlet silhouette, glowing leaf green [GLOVES AGILITY]
4. GREATER scroll, a gauntlet silhouette, glowing leaf green [GLOVES AGILITY]
5. LESSER scroll, a gauntlet silhouette, glowing deep violet [GLOVES SPELL POWER]
6. GREATER scroll, a gauntlet silhouette, glowing deep violet [GLOVES SPELL POWER]

Row 2:
7. LESSER scroll, a gauntlet silhouette, glowing warm gold [GLOVES HEALING]
8. GREATER scroll, a gauntlet silhouette, glowing warm gold [GLOVES HEALING]
9. LESSER scroll, a gauntlet silhouette, glowing half burnt orange, half violet [GLOVES BATTLEMAGE]
10. GREATER scroll, a gauntlet silhouette, glowing half burnt orange, half violet [GLOVES BATTLEMAGE]
11. LESSER scroll, a gauntlet silhouette, glowing half leaf green, half violet, with a tiny lightning fork [GLOVES STORMCALLER]
12. GREATER scroll, a gauntlet silhouette, glowing half leaf green, half violet, with a tiny lightning fork [GLOVES STORMCALLER]

Row 3:
13. LESSER scroll, a gauntlet silhouette, glowing half crimson, half royal blue [GLOVES VALOR]
14. GREATER scroll, a gauntlet silhouette, glowing half crimson, half royal blue [GLOVES VALOR]
15. LESSER scroll, a breastplate silhouette, glowing deep crimson red [CHEST STAMINA]
16. GREATER scroll, a breastplate silhouette, glowing deep crimson red [CHEST STAMINA]
17. LESSER scroll, a breastplate silhouette, glowing royal blue [CHEST INTELLECT]
18. GREATER scroll, a breastplate silhouette, glowing royal blue [CHEST INTELLECT]

Row 4:
19. LESSER scroll, a breastplate silhouette, glowing five small colours in a ring (crimson, orange, green, blue, silver) [CHEST STATS]
20. GREATER scroll, a breastplate silhouette, glowing five small colours in a ring (crimson, orange, green, blue, silver) [CHEST STATS]
21. LESSER scroll, a breastplate silhouette, glowing pale silver-white [CHEST SPIRIT]
22. GREATER scroll, a breastplate silhouette, glowing pale silver-white [CHEST SPIRIT]
23. LESSER scroll, a breastplate silhouette, glowing half royal blue, half silver-white [CHEST SAGACITY]
24. GREATER scroll, a breastplate silhouette, glowing half royal blue, half silver-white [CHEST SAGACITY]

Row 5:
25. LESSER scroll, a breastplate silhouette, glowing half burnt orange, half crimson [CHEST VIGOR]
26. GREATER scroll, a breastplate silhouette, glowing half burnt orange, half crimson [CHEST VIGOR]
27. LESSER scroll, a breastplate silhouette, glowing half burnt orange, half warm gold [CHEST DEVOTION]
28. GREATER scroll, a breastplate silhouette, glowing half burnt orange, half warm gold [CHEST DEVOTION]
29. LESSER scroll, a cloak silhouette, glowing steel grey [CLOAK PROTECTION]
30. GREATER scroll, a cloak silhouette, glowing steel grey [CLOAK PROTECTION]

Row 6:
31. LESSER scroll, a cloak silhouette, glowing leaf green [CLOAK AGILITY]
32. GREATER scroll, a cloak silhouette, glowing leaf green [CLOAK AGILITY]
33. LESSER scroll, a cloak silhouette, glowing steel grey with a crimson rim [CLOAK WARDING]
34. GREATER scroll, a cloak silhouette, glowing steel grey with a crimson rim [CLOAK WARDING]
35. LESSER scroll, a leather armour patch silhouette, glowing steel grey [ARMOR KIT]
36. GREATER scroll, a leather armour patch silhouette, glowing steel grey [ARMOR KIT]
```

## Sheet EN3

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate enchanting icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE SCROLLS: every SCROLL is the same object, so they read as one family. A LESSER scroll is a small rolled parchment scroll, half unrolled, tied with plain twine; on its open part a rune circle glows softly in the colour named, and inside the circle is a small silhouette of the item named (a bracer, a boot, a gauntlet...). A GREATER scroll is the same idea grander: thick vellum on dark wooden rollers with gold caps and a wax seal, its rune circle blazing in the colour named, small sparks rising. Where a colour is 'half X, half Y', the rune circle is split down the middle in those two colours. An INSCRIPTION is a small engraved medallion instead of a scroll. Wands and oils are as described.

Row by row, left to right:

Row 1:
1. LESSER scroll, a one-handed sword silhouette, glowing pale silver-white [WEAPON SPIRIT]
2. GREATER scroll, a one-handed sword silhouette, glowing pale silver-white [WEAPON SPIRIT]
3. LESSER scroll, a one-handed sword silhouette, glowing burnt orange [WEAPON STRENGTH]
4. GREATER scroll, a one-handed sword silhouette, glowing burnt orange [WEAPON STRENGTH]
5. LESSER scroll, a one-handed sword silhouette, glowing leaf green [WEAPON AGILITY]
6. GREATER scroll, a one-handed sword silhouette, glowing leaf green [WEAPON AGILITY]

Row 2:
7. LESSER scroll, a one-handed sword silhouette, glowing royal blue [WEAPON INTELLECT]
8. GREATER scroll, a one-handed sword silhouette, glowing royal blue [WEAPON INTELLECT]
9. LESSER scroll, a one-handed sword silhouette, glowing deep violet [WEAPON SPELL POWER]
10. GREATER scroll, a one-handed sword silhouette, glowing deep violet [WEAPON SPELL POWER]
11. LESSER scroll, a one-handed sword silhouette, glowing warm gold [WEAPON HEALING]
12. GREATER scroll, a one-handed sword silhouette, glowing warm gold [WEAPON HEALING]

Row 3:
13. LESSER scroll, a one-handed sword silhouette, glowing half crimson, half royal blue [WEAPON VALOR]
14. GREATER scroll, a one-handed sword silhouette, glowing half crimson, half royal blue [WEAPON VALOR]
15. LESSER scroll, a one-handed sword silhouette, glowing half leaf green, half royal blue [WEAPON WILDHEART]
16. GREATER scroll, a one-handed sword silhouette, glowing half leaf green, half royal blue [WEAPON WILDHEART]
17. LESSER scroll, a one-handed sword silhouette, glowing half burnt orange, half violet [WEAPON BATTLEMAGE]
18. GREATER scroll, a one-handed sword silhouette, glowing half burnt orange, half violet [WEAPON BATTLEMAGE]

Row 4:
19. LESSER scroll, a one-handed sword silhouette, glowing half leaf green, half violet, with a tiny lightning fork [WEAPON STORMCALLER]
20. GREATER scroll, a one-handed sword silhouette, glowing half leaf green, half violet, with a tiny lightning fork [WEAPON STORMCALLER]
21. GREATER scroll, sword silhouette, bright orange flames curling up off the parchment
22. GREATER scroll, sword silhouette, violet ribbons of light flowing round it like music
23. GREATER scroll, an orange sword silhouette wreathed in violet runes
24. GREATER scroll, sword silhouette, black shadow tendrils drawing a thread of red light

Row 5:
25. GREATER scroll, a swirling spiral of bright blue mana rising from the rune circle
26. GREATER scroll, a gold sword silhouette with a soft green healing glow
27. GREATER scroll, a radiant white-gold starburst behind the sword silhouette, holy light
28. GREATER scroll, a tiny living ember (a glowing coal with two bright eyes) curled on the open parchment
29. INSCRIPTION: a small silver medallion with gold trim and a sun emblem, a raised sword on it
30. INSCRIPTION: a small silver medallion with gold trim and a sun emblem, an open book with a star

Row 6:
31. INSCRIPTION: a small silver medallion with gold trim and a sun emblem, a chalice on it
32. INSCRIPTION: a small silver medallion with gold trim and a sun emblem, a tower shield on it
33. INSCRIPTION: a bone-white medallion with a pale blue flame emblem, a hammer on it
34. INSCRIPTION: a bone-white medallion with a pale blue flame emblem, an arrow on it
35. INSCRIPTION: a bone-white medallion with a pale blue flame emblem, a small ember on it
36. INSCRIPTION: a bone-white medallion with a pale blue flame emblem, a mailed fist on it
```

## Sheet EN4

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate enchanting icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE SCROLLS: every SCROLL is the same object, so they read as one family. A LESSER scroll is a small rolled parchment scroll, half unrolled, tied with plain twine; on its open part a rune circle glows softly in the colour named, and inside the circle is a small silhouette of the item named (a bracer, a boot, a gauntlet...). A GREATER scroll is the same idea grander: thick vellum on dark wooden rollers with gold caps and a wax seal, its rune circle blazing in the colour named, small sparks rising. Where a colour is 'half X, half Y', the rune circle is split down the middle in those two colours. An INSCRIPTION is a small engraved medallion instead of a scroll. Wands and oils are as described.

Row by row, left to right:

Row 1:
1. LESSER scroll, a round shield silhouette, glowing deep crimson red [SHIELD STAMINA]
2. GREATER scroll, a round shield silhouette, glowing deep crimson red [SHIELD STAMINA]
3. LESSER scroll, a round shield silhouette, glowing pale silver-white [SHIELD SPIRIT]
4. GREATER scroll, a round shield silhouette, glowing pale silver-white [SHIELD SPIRIT]
5. LESSER scroll, a round shield silhouette, glowing bronze [SHIELD BLOCKING]
6. GREATER scroll, a round shield silhouette, glowing bronze [SHIELD BLOCKING]

Row 2:
7. LESSER scroll, a round shield silhouette, glowing royal blue [SHIELD INTELLECT]
8. GREATER scroll, a round shield silhouette, glowing royal blue [SHIELD INTELLECT]
9. LESSER scroll, a round shield silhouette, glowing steel grey with a crimson rim [SHIELD WARDING]
10. GREATER scroll, a round shield silhouette, glowing steel grey with a crimson rim [SHIELD WARDING]
11. LESSER scroll, a round shield silhouette, glowing half crimson, half royal blue [SHIELD VALOR]
12. GREATER scroll, a round shield silhouette, glowing half crimson, half royal blue [SHIELD VALOR]

Row 3:
13. LESSER scroll, a two-handed greatsword silhouette, glowing royal blue [2H INTELLECT]
14. GREATER scroll, a two-handed greatsword silhouette, glowing royal blue [2H INTELLECT]
15. LESSER scroll, a two-handed greatsword silhouette, glowing pale silver-white [2H SPIRIT]
16. GREATER scroll, a two-handed greatsword silhouette, glowing pale silver-white [2H SPIRIT]
17. LESSER scroll, a two-handed greatsword silhouette, glowing burnt orange [2H STRENGTH]
18. GREATER scroll, a two-handed greatsword silhouette, glowing burnt orange [2H STRENGTH]

Row 4:
19. LESSER scroll, a two-handed greatsword silhouette, glowing leaf green [2H AGILITY]
20. GREATER scroll, a two-handed greatsword silhouette, glowing leaf green [2H AGILITY]
21. LESSER scroll, a two-handed greatsword silhouette, glowing deep violet [2H SPELL POWER]
22. GREATER scroll, a two-handed greatsword silhouette, glowing deep violet [2H SPELL POWER]
23. LESSER scroll, a two-handed greatsword silhouette, glowing half crimson, half royal blue [2H VALOR]
24. GREATER scroll, a two-handed greatsword silhouette, glowing half crimson, half royal blue [2H VALOR]

Row 5:
25. LESSER scroll, a two-handed greatsword silhouette, glowing half leaf green, half royal blue [2H WILDHEART]
26. GREATER scroll, a two-handed greatsword silhouette, glowing half leaf green, half royal blue [2H WILDHEART]
27. A small plain vial of shimmering violet-blue oil
28. A slightly larger vial of shimmering violet-blue oil, a twine tie
29. A round flask of violet-blue oil sparkling with tiny stars
30. An ornate crystal flask of brilliant violet-blue oil, starry sparkles, silver collar

Row 6:
31. A small plain vial of glowing aqua oil
32. A slightly larger vial of glowing aqua oil, a twine tie
33. An ornate crystal flask of brilliant aqua oil, a silver collar, a soft glow
34. A squat flask of oil swirling orange and violet together
35. An ornate flask of oil swirling orange and violet, a gold collar, glowing
36. A slim flask of warm golden oil with a tiny sun charm on the neck, glowing gently
```

## Sheet RC1

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate recipe scroll icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE RECIPES: each profession has ONE object, described in its cells, and every one of its cells is that same object at a different grade. The five grades climb: APPRENTICE plain and simple, JOURNEYMAN clean with bronze, EXPERT crisp with silver, ARTISAN fine with gold and a faint glow, MASTER grand with gold and gems and a clear glow. FOUND ones are a little torn and dirt-stained; BOUGHT ones are tied with a blue ribbon and a red wax seal. EPIC ones are the same object on black parchment with gold ink and a purple glow.

Row by row, left to right:

Row 1:
1. [BLACKSMITHING PLANS, APPRENTICE, FOUND] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; plain and simple; a little torn and dirt-stained at one edge
2. [BLACKSMITHING PLANS, JOURNEYMAN, FOUND] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; clean, with a bronze clasp; a little torn and dirt-stained at one edge
3. [BLACKSMITHING PLANS, EXPERT, FOUND] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; crisp, with silver fittings; a little torn and dirt-stained at one edge
4. [BLACKSMITHING PLANS, ARTISAN, FOUND] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
5. [BLACKSMITHING PLANS, MASTER, FOUND] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
6. [BLACKSMITHING PLANS, APPRENTICE, BOUGHT] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; plain and simple; tied with a blue ribbon and a red wax seal

Row 2:
7. [BLACKSMITHING PLANS, JOURNEYMAN, BOUGHT] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
8. [BLACKSMITHING PLANS, EXPERT, BOUGHT] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
9. [BLACKSMITHING PLANS, ARTISAN, BOUGHT] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
10. [BLACKSMITHING PLANS, MASTER, BOUGHT] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
11. [BLACKSMITHING PLANS, EPIC] A rolled sheet of grey-blue parchment with an anvil drawn on it and a small smith's hammer laid across it, but on black parchment with gold ink, gold fittings and a purple glow
12. [LEATHERWORKING PATTERN, APPRENTICE, FOUND] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; plain and simple; a little torn and dirt-stained at one edge

Row 3:
13. [LEATHERWORKING PATTERN, JOURNEYMAN, FOUND] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; clean, with a bronze clasp; a little torn and dirt-stained at one edge
14. [LEATHERWORKING PATTERN, EXPERT, FOUND] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; crisp, with silver fittings; a little torn and dirt-stained at one edge
15. [LEATHERWORKING PATTERN, ARTISAN, FOUND] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
16. [LEATHERWORKING PATTERN, MASTER, FOUND] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
17. [LEATHERWORKING PATTERN, APPRENTICE, BOUGHT] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; plain and simple; tied with a blue ribbon and a red wax seal
18. [LEATHERWORKING PATTERN, JOURNEYMAN, BOUGHT] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal

Row 4:
19. [LEATHERWORKING PATTERN, EXPERT, BOUGHT] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
20. [LEATHERWORKING PATTERN, ARTISAN, BOUGHT] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
21. [LEATHERWORKING PATTERN, MASTER, BOUGHT] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
22. [LEATHERWORKING PATTERN, EPIC] A sheet of tanned leather with stitched edges and an armour outline drawn on it, a bone needle pushed through, but on black parchment with gold ink, gold fittings and a purple glow
23. [TAILORING PATTERN, APPRENTICE, FOUND] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; plain and simple; a little torn and dirt-stained at one edge
24. [TAILORING PATTERN, JOURNEYMAN, FOUND] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; clean, with a bronze clasp; a little torn and dirt-stained at one edge

Row 5:
25. [TAILORING PATTERN, EXPERT, FOUND] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; crisp, with silver fittings; a little torn and dirt-stained at one edge
26. [TAILORING PATTERN, ARTISAN, FOUND] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
27. [TAILORING PATTERN, MASTER, FOUND] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
28. [TAILORING PATTERN, APPRENTICE, BOUGHT] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; plain and simple; tied with a blue ribbon and a red wax seal
29. [TAILORING PATTERN, JOURNEYMAN, BOUGHT] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
30. [TAILORING PATTERN, EXPERT, BOUGHT] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; crisp, with silver fittings; tied with a blue ribbon and a red wax seal

Row 6:
31. [TAILORING PATTERN, ARTISAN, BOUGHT] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
32. [TAILORING PATTERN, MASTER, BOUGHT] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
33. [TAILORING PATTERN, EPIC] A folded cloth-paper sewing pattern with a dotted outline, a sewing pin and a small spool of thread, but on black parchment with gold ink, gold fittings and a purple glow
34. [WOODWORKING SCHEMATIC, APPRENTICE, FOUND] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; plain and simple; a little torn and dirt-stained at one edge
35. [WOODWORKING SCHEMATIC, JOURNEYMAN, FOUND] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; clean, with a bronze clasp; a little torn and dirt-stained at one edge
36. [WOODWORKING SCHEMATIC, EXPERT, FOUND] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; crisp, with silver fittings; a little torn and dirt-stained at one edge
```

## Sheet RC2

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate recipe scroll icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE RECIPES: each profession has ONE object, described in its cells, and every one of its cells is that same object at a different grade. The five grades climb: APPRENTICE plain and simple, JOURNEYMAN clean with bronze, EXPERT crisp with silver, ARTISAN fine with gold and a faint glow, MASTER grand with gold and gems and a clear glow. FOUND ones are a little torn and dirt-stained; BOUGHT ones are tied with a blue ribbon and a red wax seal. EPIC ones are the same object on black parchment with gold ink and a purple glow.

Row by row, left to right:

Row 1:
1. [WOODWORKING SCHEMATIC, ARTISAN, FOUND] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
2. [WOODWORKING SCHEMATIC, MASTER, FOUND] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
3. [WOODWORKING SCHEMATIC, APPRENTICE, BOUGHT] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; plain and simple; tied with a blue ribbon and a red wax seal
4. [WOODWORKING SCHEMATIC, JOURNEYMAN, BOUGHT] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
5. [WOODWORKING SCHEMATIC, EXPERT, BOUGHT] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
6. [WOODWORKING SCHEMATIC, ARTISAN, BOUGHT] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal

Row 2:
7. [WOODWORKING SCHEMATIC, MASTER, BOUGHT] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
8. [WOODWORKING SCHEMATIC, EPIC] A thin wooden board with a bow and staff outline burned into it, a small chisel beside it, but on black parchment with gold ink, gold fittings and a purple glow
9. [ENGINEERING SCHEMATIC, APPRENTICE, FOUND] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; plain and simple; a little torn and dirt-stained at one edge
10. [ENGINEERING SCHEMATIC, JOURNEYMAN, FOUND] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; clean, with a bronze clasp; a little torn and dirt-stained at one edge
11. [ENGINEERING SCHEMATIC, EXPERT, FOUND] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; crisp, with silver fittings; a little torn and dirt-stained at one edge
12. [ENGINEERING SCHEMATIC, ARTISAN, FOUND] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge

Row 3:
13. [ENGINEERING SCHEMATIC, MASTER, FOUND] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
14. [ENGINEERING SCHEMATIC, APPRENTICE, BOUGHT] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; plain and simple; tied with a blue ribbon and a red wax seal
15. [ENGINEERING SCHEMATIC, JOURNEYMAN, BOUGHT] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
16. [ENGINEERING SCHEMATIC, EXPERT, BOUGHT] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
17. [ENGINEERING SCHEMATIC, ARTISAN, BOUGHT] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
18. [ENGINEERING SCHEMATIC, MASTER, BOUGHT] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal

Row 4:
19. [ENGINEERING SCHEMATIC, EPIC] A blueprint sheet of blue paper with white lines drawing a cog, a small brass gear pinned to it, but on black parchment with gold ink, gold fittings and a purple glow
20. [JEWELCRAFTING DESIGN, APPRENTICE, FOUND] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; plain and simple; a little torn and dirt-stained at one edge
21. [JEWELCRAFTING DESIGN, JOURNEYMAN, FOUND] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; clean, with a bronze clasp; a little torn and dirt-stained at one edge
22. [JEWELCRAFTING DESIGN, EXPERT, FOUND] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; crisp, with silver fittings; a little torn and dirt-stained at one edge
23. [JEWELCRAFTING DESIGN, ARTISAN, FOUND] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
24. [JEWELCRAFTING DESIGN, MASTER, FOUND] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge

Row 5:
25. [JEWELCRAFTING DESIGN, APPRENTICE, BOUGHT] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; plain and simple; tied with a blue ribbon and a red wax seal
26. [JEWELCRAFTING DESIGN, JOURNEYMAN, BOUGHT] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
27. [JEWELCRAFTING DESIGN, EXPERT, BOUGHT] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
28. [JEWELCRAFTING DESIGN, ARTISAN, BOUGHT] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
29. [JEWELCRAFTING DESIGN, MASTER, BOUGHT] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
30. [JEWELCRAFTING DESIGN, EPIC] A stiff card on dark velvet with a cut gem drawn on it, a tiny real gem pinned at the corner, but on black parchment with gold ink, gold fittings and a purple glow

Row 6:
31. [ALCHEMY RECIPE, APPRENTICE, FOUND] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; plain and simple; a little torn and dirt-stained at one edge
32. [ALCHEMY RECIPE, JOURNEYMAN, FOUND] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; clean, with a bronze clasp; a little torn and dirt-stained at one edge
33. [ALCHEMY RECIPE, EXPERT, FOUND] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; crisp, with silver fittings; a little torn and dirt-stained at one edge
34. [ALCHEMY RECIPE, ARTISAN, FOUND] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
35. [ALCHEMY RECIPE, MASTER, FOUND] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
36. [ALCHEMY RECIPE, APPRENTICE, BOUGHT] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; plain and simple; tied with a blue ribbon and a red wax seal
```

## Sheet RC3

```
Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate recipe scroll icons (each cell about 170x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Words in square brackets are notes for you: never draw them.

THE RECIPES: each profession has ONE object, described in its cells, and every one of its cells is that same object at a different grade. The five grades climb: APPRENTICE plain and simple, JOURNEYMAN clean with bronze, EXPERT crisp with silver, ARTISAN fine with gold and a faint glow, MASTER grand with gold and gems and a clear glow. FOUND ones are a little torn and dirt-stained; BOUGHT ones are tied with a blue ribbon and a red wax seal. EPIC ones are the same object on black parchment with gold ink and a purple glow.

Row by row, left to right:

Row 1:
1. [ALCHEMY RECIPE, JOURNEYMAN, BOUGHT] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
2. [ALCHEMY RECIPE, EXPERT, BOUGHT] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
3. [ALCHEMY RECIPE, ARTISAN, BOUGHT] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
4. [ALCHEMY RECIPE, MASTER, BOUGHT] A curled parchment with a flask drawn on it, a potion drip stain and a tiny cork; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
5. [COOKING RECIPE, APPRENTICE, FOUND] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; plain and simple; a little torn and dirt-stained at one edge
6. [COOKING RECIPE, JOURNEYMAN, FOUND] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; clean, with a bronze clasp; a little torn and dirt-stained at one edge

Row 2:
7. [COOKING RECIPE, EXPERT, FOUND] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; crisp, with silver fittings; a little torn and dirt-stained at one edge
8. [COOKING RECIPE, ARTISAN, FOUND] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
9. [COOKING RECIPE, MASTER, FOUND] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
10. [COOKING RECIPE, APPRENTICE, BOUGHT] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; plain and simple; tied with a blue ribbon and a red wax seal
11. [COOKING RECIPE, JOURNEYMAN, BOUGHT] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
12. [COOKING RECIPE, EXPERT, BOUGHT] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; crisp, with silver fittings; tied with a blue ribbon and a red wax seal

Row 3:
13. [COOKING RECIPE, ARTISAN, BOUGHT] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
14. [COOKING RECIPE, MASTER, BOUGHT] A recipe card with a cooking pot drawn on it, a small wooden spoon and a grease stain; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
15. [ENCHANTING FORMULA, APPRENTICE, FOUND] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; plain and simple; a little torn and dirt-stained at one edge
16. [ENCHANTING FORMULA, JOURNEYMAN, FOUND] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; clean, with a bronze clasp; a little torn and dirt-stained at one edge
17. [ENCHANTING FORMULA, EXPERT, FOUND] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; crisp, with silver fittings; a little torn and dirt-stained at one edge
18. [ENCHANTING FORMULA, ARTISAN, FOUND] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge

Row 4:
19. [ENCHANTING FORMULA, MASTER, FOUND] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
20. [ENCHANTING FORMULA, APPRENTICE, BOUGHT] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; plain and simple; tied with a blue ribbon and a red wax seal
21. [ENCHANTING FORMULA, JOURNEYMAN, BOUGHT] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
22. [ENCHANTING FORMULA, EXPERT, BOUGHT] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
23. [ENCHANTING FORMULA, ARTISAN, BOUGHT] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
24. [ENCHANTING FORMULA, MASTER, BOUGHT] A parchment with a faintly glowing rune circle drawn on it and a small runed rod; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal

Row 5:
25. [RUNECRAFTING RUNE SCRIPT, APPRENTICE, FOUND] A small slate tablet carved with runes that glow faintly, a stub of chalk; plain and simple; a little torn and dirt-stained at one edge
26. [RUNECRAFTING RUNE SCRIPT, JOURNEYMAN, FOUND] A small slate tablet carved with runes that glow faintly, a stub of chalk; clean, with a bronze clasp; a little torn and dirt-stained at one edge
27. [RUNECRAFTING RUNE SCRIPT, EXPERT, FOUND] A small slate tablet carved with runes that glow faintly, a stub of chalk; crisp, with silver fittings; a little torn and dirt-stained at one edge
28. [RUNECRAFTING RUNE SCRIPT, ARTISAN, FOUND] A small slate tablet carved with runes that glow faintly, a stub of chalk; fine, with gold fittings and a faint glow; a little torn and dirt-stained at one edge
29. [RUNECRAFTING RUNE SCRIPT, MASTER, FOUND] A small slate tablet carved with runes that glow faintly, a stub of chalk; grand, with gold and gem fittings and a clear glow; a little torn and dirt-stained at one edge
30. [RUNECRAFTING RUNE SCRIPT, APPRENTICE, BOUGHT] A small slate tablet carved with runes that glow faintly, a stub of chalk; plain and simple; tied with a blue ribbon and a red wax seal

Row 6:
31. [RUNECRAFTING RUNE SCRIPT, JOURNEYMAN, BOUGHT] A small slate tablet carved with runes that glow faintly, a stub of chalk; clean, with a bronze clasp; tied with a blue ribbon and a red wax seal
32. [RUNECRAFTING RUNE SCRIPT, EXPERT, BOUGHT] A small slate tablet carved with runes that glow faintly, a stub of chalk; crisp, with silver fittings; tied with a blue ribbon and a red wax seal
33. [RUNECRAFTING RUNE SCRIPT, ARTISAN, BOUGHT] A small slate tablet carved with runes that glow faintly, a stub of chalk; fine, with gold fittings and a faint glow; tied with a blue ribbon and a red wax seal
34. [RUNECRAFTING RUNE SCRIPT, MASTER, BOUGHT] A small slate tablet carved with runes that glow faintly, a stub of chalk; grand, with gold and gem fittings and a clear glow; tied with a blue ribbon and a red wax seal
35. [TIMBERMAW WARHIDE, an epic leather chestpiece, not a recipe] A heavy furbolg-made leather chest of dark brown hide with honey-gold stitching, carved wooden toggles and a trim of bear claws, a faint warm golden glow
36. [PLAIN RECIPE SCROLL] A plain rolled parchment scroll tied with string, nothing drawn on it
```
