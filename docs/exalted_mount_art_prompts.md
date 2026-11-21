# Exalted faction mounts (3 sheets, 16 mounts) and reins icons for the new mounts

Kyle, 18 Nov 2026: "Hit me with as much as you can!" One mount per faction, the reward for reaching Exalted, so
every faction has a mount as well as its title. Sold by the faction's quartermaster at Exalted when built. Same layout
as the other mount sheets. Slice with `tools/asset_pipeline/slice_mount_sheet.py SHEET.png <the ids>`. Attach
`war_kodo_left.png` and `rune_saber_down.png` as the style reference.

---------------------------------------------------------------------
**Landed 20 Nov 2026**: H11 to H13 are sliced (`assets/mounts`) and built: 100g from each faction's first quartermaster at Exalted. I2 (reins) landed 20 Nov too, and sheet H14 drew the factions that came after (`docs/art_status.md`). The Feathermoon Sentinels came after these sheets; their war owl landed on H14.

## SHEET H11: Exalted mounts, part 1  (paste this whole block)

Ids in order: `crimson_codex_spellbound_construct orgrimmar_redstone_warwolf darkspear_voodoo_raptor forsaken_war_bat steamwheedle_trike thunder_bluff_totem_kodo`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are the PROUDEST RIDING MOUNTS in a Horde fantasy RPG, each the reward for reaching Exalted with one faction, shown with NO RIDER. Each wears grand tack in its faction's colours and style with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six animals in every row, each turned according to that row's rule):
1. SPELLBOUND CONSTRUCT (the Crimson Codex, blood elf arcanists) - a four-legged steed built of carved red sandstone and gold, no flesh at all, floating glowing crimson runes orbiting its body, a head like an elegant horse's skull of stone with eyes of bright red arcane light, a crimson and gold silk saddle.
2. REDSTONE WAR WOLF (Orgrimmar) - a massive black-furred war wolf in heavy spiked iron armour painted red, a horned iron helm, tusk trophies on the harness, a small red Horde war banner rising from the back of the saddle.
3. VOODOO RAPTOR (the Darkspear Tribe, jungle trolls) - a tall teal and purple striped raptor, a carved wooden voodoo mask strapped over its brow, bone and feather fetishes and shrunken-head charms on the harness, a crest of long blue feathers, a troll saddle of bamboo and hide.
4. FORSAKEN WAR BAT (the Forsaken) - a giant grey-brown bat standing on the ground on its folded wing-knuckles and hind feet like a vampire bat, huge ears, glowing yellow eyes, ragged wing membranes, wearing dark iron armour with green plague-glass vials and a black and purple Undercity saddle.
5. STEAMWHEEDLE TRIKE (the Steamwheedle Cartel, goblin traders) - a goblin three-wheeled riding machine, fantasy not modern: a big riveted brass engine block, one wide front wheel with spokes and two chunky back wheels, handlebars like ram horns, a padded leather seat, exhaust pipes puffing smoke, crates of trade goods strapped on the back. In the side views it reads as a trike; front and back views show the wheels head-on.
6. TOTEM KODO (Thunder Bluff, tauren of a city that no longer stands) - a great grey kodo with grey ash paint marks of mourning on its hide, carrying on its back a tall carved and painted totem pole lashed upright behind the saddle, eagle feathers and beads hanging from it, a tauren saddle of painted hide.

Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET H12: Exalted mounts, part 2  (paste this whole block)

Ids in order: `booty_bay_great_parrot ashclaim_core_hound emerald_bark_strider pale_flame_lion argent_charger timbermaw_great_badger`

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are the PROUDEST RIDING MOUNTS in a Horde fantasy RPG, each the reward for reaching Exalted with one faction, shown with NO RIDER. Each wears grand tack in its faction's colours and style with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other five.

Columns, left to right (the same six animals in every row, each turned according to that row's rule):
1. GREAT HARBOUR PARROT (the Booty Bay Port Authority, goblin harbour) - a huge parrot as big as a horse, standing on two thick scaly legs, brilliant red, blue and yellow feathers, a big curved beak, a pirate's gold earring through one ear-feather, a little tricorn hat strapped on its head, a ship's-leather saddle with brass fittings.
2. ASHCLAIM CORE HOUND (the Ashclaim, Dark Iron dwarves and goblins) - a huge two-headed lava hound on four thick legs, cracked black rock hide with glowing orange magma in the cracks, two heavy toothy heads, smoke rising off its back, wearing dark iron dwarven plate and a riveted iron saddle.
3. BARK STRIDER (the Emerald Reclamation, forest folk) - a four-legged beast grown from living wood: a body of twisted roots and bark, legs like tree trunks, a long neck with an elk-like head of carved wood, moss and ferns growing along its back, small green glowing eyes, a saddle of woven vines.
4. PALE FLAME LION (the Order of the Pale Flame, a holy order) - a powerful white lion with a mane of pale white-gold holy fire that burns without smoke, calm gold eyes, wearing white and pale-gold plate barding with a small flame emblem, a white leather saddle.
5. ARGENT CHARGER (the Argent Dawn) - a strong white warhorse in polished silver plate barding, a flowing blue and white caparison, a silver chanfron with a small sun emblem, a white mane and tail, a blue leather saddle.
6. GREAT BADGER (Timbermaw Hold, furbolgs) - a giant badger the size of a bear, low and wide, thick grey fur with the white and black striped face, big digging claws, wearing furbolg totems, carved wooden beads and a saddle of pine-green felt and bark.

Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET H13: Exalted mounts, part 3  (paste this whole block)

Ids in order: `sunreach_dragonhawk liquidators_hazard_mule cenarion_stormcrow wakened_dream_jackalope`

```
Generate ONE sprite sheet image, 1024x1024, a 4 columns x 4 rows grid = 16 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are the PROUDEST RIDING MOUNTS in a Horde fantasy RPG, each the reward for reaching Exalted with one faction, shown with NO RIDER. Each wears grand tack in its faction's colours and style with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other three.

Columns, left to right (the same four animals in every row, each turned according to that row's rule):
1. SUNREACH DRAGONHAWK (the Sunreach Conclave, blood elf magisters) - a lean dragonhawk standing on the ground with its wings folded: a long serpentine neck, a sharp beaked dragon-like head, flame-red and gold scales and feathers, a long tail ending in a feather fan, wearing red and gold elven barding and a gold filigree saddle.
2. HAZARD MULE (the Liquidators, transplants who clean up fallout) - a huge, tough armoured mule with long ears, wearing thick grey lead-plate barding with hazard yellow and black stripes, a canvas saddle with a modern gas mask and a spare filter hanging from it, a lamp on the bridle.
3. CENARION STORMCROW (the Cenarion Circle, druids) - a huge black crow as tall as a horse, standing on two strong legs with wings half folded, glossy blue-black feathers, a long curved beak, glowing pale blue eyes, a druid saddle of leather and leaves, small silver moon charms on the harness.
4. DREAM JACKALOPE (the Wakened, transplants woken in Moonglade) - a giant rabbit the size of a horse with tall ears, soft grey-brown fur, a pair of small deer antlers, sleepy half-closed eyes, little glowing flowers and grass tangled in its fur, a saddle of woven dreamgrass with a tiny lantern.

Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET I2: 28 reins icons for the wild and Exalted mounts  (paste this whole block)

The H9 and H10 wild mounts (1-12), then the H11 to H13 Exalted mounts (13-28). Sliced to `assets/icons/collection/` as
`col_reins_<mount id>`. Attach `qi_journal.png`, `qi_horn.png` and `qi_signet.png` as the style reference.

```
Generate ONE image, 2048x1170, a grid of 7 columns x 4 rows = 28 separate square inventory icons, each about 292x292. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no magenta or pink inside the icons. Each is the item that summons a riding mount: reins, a bridle, a collar, a whistle, a charm or a key.

Icons, row by row, left to right:
Row 1: 1 blue-grey hide reins with a little lightning-bolt charm of white quartz; 2 painted hide reins with a red and white plume; 3 reins with an iron-grey crocodile scute clasp; 4 a silver-blue feather on a white leather bridle; 5 reins with a curved sandy chitin mandible clasp; 6 a rough collar of ash-black mane hair with a bone tooth; 7 a spiralled horn on a rope bridle with a small brass bell.
Row 2: 8 a double bridle for two heads, olive leather, joined by one ring; 9 a heavy curved horn on a painted hide strap with feathers; 10 a dark brown vulture feather and a bone on a cord; 11 a single long quill with a glowing orange ember tip; 12 a tiny spiral snail shell with moss, tied to a lantern hook; 13 a small red sandstone rune-key glowing crimson; 14 a spiked red iron wolf collar.
Row 3: 15 a tiny carved voodoo mask on teal beads; 16 a bat-wing whistle of dark iron with a green glass bead; 17 a brass ignition key with a little cog; 18 a small carved totem pole charm with eagle feathers; 19 a gold earring and a red parrot feather; 20 a black rock collar with glowing magma cracks; 21 a living wooden bridle sprouting green leaves.
Row 4: 22 a white leather bridle with a pale white-gold flame charm; 23 a silver chanfron with a small sun emblem; 24 a wooden furbolg bead string with a badger claw; 25 a red and gold elven filigree bridle with a flame-red feather; 26 a heavy lead tag on hazard yellow and black reins; 27 a glossy black crow feather with a silver moon charm; 28 a tiny pair of antlers tied with dreamgrass and a glowing flower.
```

Slices in this order:
```
col_reins_stormhide_thunder_lizard, col_reins_plainstrider_matriarch, col_reins_ironback_crocolisk, col_reins_moonfeather_hippogryph, col_reins_sandreaver_silithid, col_reins_ashmane_hyena, col_reins_highpeak_ramgoat, col_reins_mudback_hydra, col_reins_thunderhorn_bull, col_reins_carrion_strider, col_reins_emberquill_porcupine, col_reins_shellback_snail, col_reins_crimson_codex_spellbound_construct, col_reins_orgrimmar_redstone_warwolf, col_reins_darkspear_voodoo_raptor, col_reins_forsaken_war_bat, col_reins_steamwheedle_trike, col_reins_thunder_bluff_totem_kodo, col_reins_booty_bay_great_parrot, col_reins_ashclaim_core_hound, col_reins_emerald_bark_strider, col_reins_pale_flame_lion, col_reins_argent_charger, col_reins_timbermaw_great_badger, col_reins_sunreach_dragonhawk, col_reins_liquidators_hazard_mule, col_reins_cenarion_stormcrow, col_reins_wakened_dream_jackalope
```
