# Faction tabard icons (1 sheet, 16 icons)

Kyle, 18 Nov 2026: "You can give me a prompt for tabbards for the factions we have currently." One tabard icon per
faction tabard (`docs/tabards_design.md`). They replace the tinted stand-ins in `assets/icons/gear/`. Slice with
`python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png --ids=...` (a 4x4 sheet; see the order below).
Attach two or three existing icons (`gear_inv_shirt_guildtabard_01.png`, `qi_signet.png`) as the style reference.

## SHEET T1: 16 tabards  (paste this whole block)

```
Generate ONE image, 2048x2048, a grid of 4 columns x 4 rows = 16 separate square inventory icons, each about 512x512. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, seen straight from the front. No frames, no borders, no text, no letters or numbers anywhere, no magenta or pink inside the icons.

Every icon is the SAME SHAPE: a sleeveless cloth tabard laid flat, a long rectangular front panel with a V or round neck and a squared or pointed hem, the faction's emblem large in the middle of the chest. Only the colours, the trim and the emblem change, so the sixteen read as one set. Each emblem is a simple bold shape you could recognise at a glance.

Tabards, row by row, left to right:
Row 1: 1 deep crimson with gold trim, the emblem an open book with a glowing red eye on its pages; 2 blood red with black iron trim and rivets, the emblem a black spiked wolf's skull over crossed axes; 3 teal with a purple zig-zag border, the emblem a carved troll mask with tusks; 4 dark violet with sickly green trim, the emblem a pale skull with a green flame behind it.
Row 2: 5 green with gold trim, the emblem a gold coin with a cog cut into its edge; 6 earthy brown with cream trim, the emblem a tall carved totem pole with eagle wings, a little grey ash smear across it; 7 navy blue with gold rope trim, the emblem a ship's anchor through a gold coin; 8 charcoal grey with glowing orange trim like embers, the emblem a dwarven hammer over a molten anvil.
Row 3: 9 leaf green with cream trim, the emblem a sprouting oak leaf with a small crescent moon; 10 cream white with gold trim, the emblem a pale white-gold flame inside a ring; 11 silver-white with blue trim, the emblem a rising sun over a sword pointing up; 12 olive green with brown fur trim, the emblem a furbolg's paw print with a pine tree.
Row 4: 13 scarlet with gold filigree trim, the emblem a phoenix rising from a sun; 14 hazard yellow with black stripes at the hem, the emblem a black three-bladed hazard symbol inside a gas mask outline; 15 forest green with purple trim, the emblem a crescent moon cradling a leaf; 16 pale sky blue with soft gold trim, the emblem a closed sleeping eye opening, with a few blades of grass.
```

Slices in this order:

```
gear/tabard_crimson_codex, gear/tabard_orgrimmar, gear/tabard_darkspear_tribe, gear/tabard_the_forsaken,
gear/tabard_steamwheedle_cartel, gear/tabard_thunder_bluff, gear/tabard_booty_bay_authority, gear/tabard_the_ashclaim,
gear/tabard_emerald_reclamation, gear/tabard_pale_flame, gear/tabard_argent_dawn, gear/tabard_timbermaw_hold,
gear/tabard_sunreach_conclave, gear/tabard_the_liquidators, gear/tabard_cenarion_circle, gear/tabard_the_wakened
```
