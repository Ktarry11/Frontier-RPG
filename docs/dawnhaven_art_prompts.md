# Dawnhaven: art prompts (sheets DH1 to DH3)

**Status (21 Nov 2026): written, waiting on Kyle.** Kyle: "Existing art now, sheets later". Dawnhaven is built and
playable on Azshara's autumn ground and the be_ blood elf buildings (docs/dawnhaven_brief.md); these sheets give the
isle its own look. See `docs/art_status.md` for every sheet.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| DH1 | 24 ground tiles: Dawnhaven's gold and red autumn, elven paving, the shore and the Lightwell's water | 2048x1366 | 6 x 4 (about 341 x 341) | none (tiles fill their cells) |
| DH2 | 24 props: wardstones, the Lightwell, the Conclave's camp, the outpost's ruins, the naga's landing, the trees | 2048x1366 | 6 x 4 (about 341 x 341) | magenta |
| DH3 | 12 buildings: Firstlight Spire and the town round it, Dawnrest, Amberwatch's gatehouse | 2048x1366 | 4 x 3 (about 512 x 455) | magenta |

**References to attach:** `assets/buildings/be_grand_spire.png`, `assets/buildings/be_inn.png`,
`assets/tiles/azshara/props/az_autumn_tree.png` and `assets/tiles/azshara/ground/az_leaf_gold.png`.

---------------------------------------------------------------------
## SHEET DH1: GROUND (paste this whole block)

```
Generate ONE image, 2048x1366, a 6 columns x 4 rows grid = 24 separate SQUARE GROUND TILES, each about 341x341, each one filling its whole cell edge to edge. Every tile must be SEAMLESSLY TILEABLE on all four sides: anything crossing an edge continues exactly on the opposite edge. A thin dark gutter between tiles. No objects standing up, no shadows of objects, no characters, no text, no labels. Painterly semi-realistic WoW Classic style matching the attached references, seen from directly above, soft even light, rich warm autumn colour.

Setting: DAWNHAVEN, a blood elf island off the coast of Azshara, an ancient high elf outpost reclaimed. Forever autumn: gold and red trees, white marble and gold elven stonework, a turquoise sea.

Tiles, row by row, left to right:
Row 1, FOREST FLOORS: 1 gold leaf litter, thick and bright. 2 red leaf litter, deep crimson and rust. 3 crimson undergrowth, low red brush and fallen leaves. 4 gold autumn grass, short and soft. 5 dusk forest floor, red leaves in cool violet shadow. 6 moss and tiny toadstools among scattered gold leaves.
Row 2, ELVEN STONE: 7 white marble paving with thin gold inlay lines, a few leaves blown across it. 8 the same paving cracked and sunken, grass in the cracks. 9 mossy old elven flagstones. 10 a gold-cobbled road. 11 a dirt trail strewn with red and gold leaves. 12 white marble with a gold sun inlay, the plaza of a city.
Row 3, SHORE AND WATER: 13 pale gold shell beach. 14 wet sand with foam lines. 15 tidepool rock with barnacles. 16 shallow turquoise sea over sand. 17 deep blue-green sea. 18 a forest mere, dark amber water with floating red leaves.
Row 4, MAGIC AND DEATH: 19 grass with faint teal ley veins glowing through it. 20 grey-violet barrow earth with dead leaves. 21 coral sand with naga shell fragments. 22 glowing gold arcane water, the Lightwell's. 23 red sandstone cliff rock. 24 dark dead water, the Lightwell when it was dark.
```

Slices: `dh_leaf_gold`, `dh_leaf_red`, `dh_crimson_brush`, `dh_gold_grass`, `dh_dusk_floor`, `dh_moss_shroom`;
`dh_elven_paving`, `dh_paving_cracked`, `dh_mossy_flag`, `dh_gold_road`, `dh_leaf_trail`, `dh_sun_plaza`;
`dh_shell_beach`, `dh_wet_sand`, `dh_tidepool`, `dh_sea_shallow`, `dh_sea_deep`, `dh_mere_water`;
`dh_ley_grass`, `dh_barrow_earth`, `dh_coral_sand`, `dh_light_water`, `dh_red_cliff`, `dh_dark_water`.

---------------------------------------------------------------------
## SHEET DH2: PROPS (paste this whole block)

```
Generate ONE sprite sheet image, 2048x1366, a 6 columns x 4 rows grid = 24 separate sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, centred in its own cell with a wide margin, not touching its neighbours or the image edge. No ground patch under anything, no text, no labels, no grid lines, no magenta or pink anywhere in the art. Glows are painted as OPAQUE soft colour, never transparent. Match the attached references EXACTLY in style, camera angle (isometric three-quarter view from about 45 degrees, front face toward the lower-right), outline and level of detail. Painterly semi-realistic WoW Classic style, soft dark outline, lit from the top-left.

Setting: DAWNHAVEN, a blood elf island off Azshara, an ancient high elf outpost the Sunreach Conclave has reclaimed. Blood elf style: white marble, gold trim, crimson cloth, elegant curving lines, phoenix and sun motifs. Forever autumn.

Sprites, row by row, left to right:
Row 1, THE OUTPOST'S MAGIC: 1 a WARDSTONE, lit: a tall pale stone with a curving gold cap and a teal glowing crack down its face. 2 the same wardstone BROKEN and dark, its top lying beside it. 3 the LIGHTWELL, dark: a round white marble well with gold rim, its water black and still. 4 the LIGHTWELL, lit: the same well blazing with gold light rising from it. 5 a fading runed obelisk, gold runes half worn away. 6 a rune circle set in the ground, gold lines on white stone.
Row 2, THE CONCLAVE'S CAMP: 7 a crimson and gold Conclave banner on a slim gold pole with a sun emblem. 8 an elegant elven lamp post, gold, with a warm crystal lamp. 9 a camp hearth with a gold elven kettle over it. 10 bedrolls and travel chests under a crimson awning. 11 a stack of supply crates stamped with the sun. 12 a dragonhawk roost perch, a tall curved gold perch with a red cushioned ledge.
Row 3, THE OUTPOST'S RUINS AND ITS DEAD: 13 a memorial stone covered in carved names, candles at its foot. 14 a spirit lantern on a tall post, a pale blue flame in a gold cage. 15 a toppled elven statue of a ranger, moss on it. 16 a broken white archway with gold trim, one side fallen. 17 an elven boat-stair going down into water, a short flight of marble steps. 18 an old elven skiff wrecked on its side, a red sail torn.
Row 4, THE NAGA AND THE WOODS: 19 a naga landing totem, coral and shell on a driftwood pole. 20 a great red and gold autumn tree, broad and full. 21 a slender gold maple sapling. 22 a fallen red log with leaves on it. 23 a low crimson shrub. 24 a pile of fallen red and gold leaves with a small mushroom.
```

Slices: `dh_wardstone_lit`, `dh_wardstone_broken`, `dh_lightwell_dark`, `dh_lightwell_lit`, `dh_runed_obelisk`,
`dh_rune_circle`; `dh_conclave_banner`, `dh_lamp_post`, `dh_camp_hearth`, `dh_bedrolls`, `dh_sun_crates`,
`dh_hawk_perch`; `dh_memorial_stone`, `dh_spirit_lantern`, `dh_toppled_ranger`, `dh_broken_arch`, `dh_boat_stair`,
`dh_wrecked_skiff`; `dh_naga_totem`, `dh_autumn_tree`, `dh_maple_sapling`, `dh_red_log`, `dh_crimson_shrub`,
`dh_leaf_pile`.

---------------------------------------------------------------------
## SHEET DH3: FIRSTLIGHT SPIRE (paste this whole block)

```
Generate ONE sprite sheet image, 2048x1366, a 4 columns x 3 rows grid = 12 separate buildings, each cell about 512x455. Flat pure #FF00FF magenta background everywhere. Each building is ONE single structure, centred in its cell with a margin, not touching its neighbours or the image edge. No ground patch except a small footprint of paving where noted, no text, no labels, no grid lines, no magenta or pink anywhere in the art. Match the attached references EXACTLY in style, camera angle (isometric three-quarter view from about 45 degrees, front face toward the lower-right), outline and level of detail. Painterly semi-realistic WoW Classic style, lit from the top-left.

Setting: FIRSTLIGHT SPIRE, a small blood elf town on the headland of Dawnhaven, built round one great spire the ancient founders raised and the Sunreach Conclave has lit again. Not a capital: graceful, modest, hopeful. White marble, gold trim, crimson roofs and banners, sun and phoenix motifs, warm light in every window.

Buildings, row by row, left to right:
Row 1: 1 FIRSTLIGHT SPIRE: one very tall slender white and gold spire with a crimson-roofed crown, a great gold crystal blazing at the top, a stair winding up its base. 2 the SPIRE'S INN: a two-storey elven inn with crimson roof, round windows, a sun sign over the door. 3 the CONCLAVE HALL: a wide elegant hall with tall arched windows and crimson banners either side of the doors. 4 the DRAGONHAWK ROOST: an open round pavilion with gold perches and a crimson canopy.
Row 2: 5 the LIBRARY TOWER: a round tower of white stone with gold bands and book-filled windows. 6 a SMALL ELVEN HOUSE, one storey, crimson roof, a little garden at the door. 7 an ELVEN TOWNHOUSE, two storeys, narrow and tall, a balcony. 8 the SPIRE'S FORGE: an elven smithy with a curved gold chimney and an anvil under an awning.
Row 3: 9 the ALCHEMIST: a domed shop with coloured glass windows and bottles on a rack outside. 10 the HARBOUR HOUSE: a small pier house with a lantern tower, at the head of a short wooden pier. 11 DAWNREST: an old elven waystation, its new crimson roof bright against weathered stone. 12 AMBERWATCH GATEHOUSE: a ruined elven gatehouse, one tower standing and one fallen, a crimson tent pitched in its lee.
```

Slices: `dh_firstlight_spire`, `dh_spire_inn`, `dh_conclave_hall`, `dh_hawk_roost`; `dh_library_tower`,
`dh_house_small`, `dh_townhouse`, `dh_forge`; `dh_alchemist`, `dh_harbour_house`, `dh_dawnrest`, `dh_amberwatch_gate`.

When these land: DH1 becomes a `DAWNHAVEN_SHEET` in `tools/bake_ashenvale.py` (both maps and the town re-baked), DH2 and
DH3 swap in for the az_ and be_ stand-ins in the three map modules. The world doesn't change with the quests (Kyle's
standing rule), so each place shows one state: the Fallen Wardstones mostly broken with the one lit stone, and the
Lightwell lit, as the Conclave keeps it.
