# Treasure chests: art prompts (sheets CH1, CH2, CH3, 12 each)

Kyle, 22 Nov 2026: "Let's get some proper chest sprites too bro. Our current ones suck ass."

**What's wrong with the old set** (`assets/tiles/chests/ch_*.png`, one sheet of 24 from 14 Nov):
- It was generated on a gradient background, so the slicer had to cut each chest out with GrabCut. That left ragged
  edges and halos.
- Each chest was drawn from its own angle and at its own size, so they don't sit on the ground the same way.
- They're painted in a different style from the world's props.
- At the size the game draws them (about one and a quarter tiles wide), the detail turns to mush.

There are also no chests at all for the newer regions: Caelora, the World Tree, Dawnhaven, Azshara, Tanaris, Feralas,
Stranglethorn, Arathi, the Plaguelands, Deadwind, the Underdark, Tempest and the Dark Iron.

**This set:** three sheets of twelve, on flat magenta so they key cleanly. Every chest is drawn from one fixed camera
and at one size class, with a bold silhouette that reads at 40 pixels. The old names are kept, so
`world/chest_looks.py` picks them up without changes, and the new regional chests get wired into its `REGIONAL` and
`DUNGEONS` tables when they land.

| Sheet | What | Image | Grid (cell) | Key |
|---|---|---|---|---|
| CH1 | everyday chests and Kalimdor's regions | 2048x1536 | 4 x 3 (512 x 512) | magenta |
| CH2 | the Eastern Kingdoms' regions and the newer lands | 2048x1536 | 4 x 3 (512 x 512) | magenta |
| CH3 | dungeon chests and boss rewards | 2048x1536 | 4 x 3 (512 x 512) | magenta |

**References to attach:** two or three of the world's prop sheets (any zone's props) for the style.

The block below is shared. Paste it once with each sheet's own list of twelve after it.

---------------------------------------------------------------------
## THE SHARED BLOCK (paste this before each sheet's list)

```
Generate ONE sprite sheet image, 2048x1536, a grid of 4 columns x 3 rows = 12 separate treasure chest sprites (each cell 512x512). Flat pure #FF00FF magenta background everywhere. Each chest sits centred in its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No text, no letters, no labels, no grid lines, no ground, no shadow on the ground, no scenery.

CAMERA AND SIZE, the same for all 12: a fantasy RPG prop seen from a top-down 3/4 view, about 35 degrees above, the chest's front face toward the viewer and its lid on top, lid CLOSED. Every chest has the same footprint and sits on the same baseline in its cell, a little wider than it is tall, so a whole set of them sits on the ground the same way. (Boss chests on sheet CH3 are drawn one size larger, as the list says.)

STYLE: match the attached prop references exactly: crisp, detailed, hand-painted pixel art with a clean dark outline, rich colours, lit from the top-left. Bold, simple shapes first and detail second. Every chest must still read clearly as a treasure chest, and as ITS kind of chest, when the whole sprite is shrunk to 40 pixels wide: a strong silhouette, one or two main materials, and one signature detail big enough to see. No magenta or pink anywhere on the chests themselves.

The 12, in order, row by row:
```

---------------------------------------------------------------------
## SHEET CH1: EVERYDAY CHESTS AND KALIMDOR, 12

```
Row 1:
1. PLAIN BOX: a plain, sturdy pine box with a hinged lid, rope handles at the ends and a simple iron hasp. The most ordinary chest in the world.
2. ROPE CRATE: a slatted wooden crate with a lid, lashed shut with thick rope tied in a big knot on top.
3. IRON-BANDED CHEST: a dark oak chest with a rounded lid, two broad iron bands over it and a heavy iron lock plate on the front.
4. TRAVEL TRUNK: a leather-covered trunk with brass corners, two buckled leather straps and a carrying handle on top.
Row 2:
5. ORC HIDE CHEST (Durotar, Orgrimmar): a squat chest of rough red-brown planks, hide stretched over the lid and stitched with sinew, a boar tusk set into the front as a latch, and a red war-paint handprint on the hide.
6. SAVANNAH CHEST (the Barrens, the tauren): a woven-reed and kodo-leather chest, painted with tauren geometric patterns in ochre and blue, its lid tied down with braided cord and a feather charm.
7. TROLL TIKI CHEST (the Echo Isles, Stranglethorn): a bamboo-and-palm-wood chest carved with a grinning tiki face across the front, its lid edged in shells, with a pair of small tusks for a latch.
8. GOBLIN LOCKBOX (Ratchet, Booty Bay, Steamwheedle): a riveted green-painted metal strongbox with a brass combination dial on the front, exposed gears and pipes, and a little warning stripe.
Row 3:
9. MOONWOOD CHEST (Ashenvale, Astranaar, Felwood): a night elf chest of pale silver-violet wood with flowing curved lines, a crescent moon inlaid in silver on the lid and a small softly glowing moonstone.
10. SEA CHEST (the coasts and islands): a weathered sailor's chest, salt-bleached planks, rope handles, iron fittings gone green, a barnacle or two on its corner.
11. SANDSTONE COFFER (Tanaris, the Shimmering Flats): a squared chest carved from sun-baked sandstone with worn hieroglyph-like bands and a brass sun disc on the lid, sand caught in its grooves.
12. WILDWOOD CHEST (Feralas, Stonetalon): a chest grown more than built, its sides made of living wood and twisted roots, moss and a few small leaves on the lid, and a carved wooden toggle for a latch.
```

---------------------------------------------------------------------
## SHEET CH2: THE EASTERN KINGDOMS AND THE NEWER LANDS, 12

```
Row 1:
1. UNDEAD RUSTED CHEST (Tirisfal, Silverpine, Hillsbrad, the Forsaken): a grey, half-rotted coffin-shaped chest with rusted iron bands, a sickly green stain and a small Forsaken lock shaped like a skull.
2. CHAINED CURSED CHEST (the Plaguelands, Felwood's north): a black chest wrapped in heavy chains with a padlock, faint green plague mist seeping from under the lid, and a cracked warning seal.
3. VINE-BOUND CHEST (Stranglethorn's jungle): a jungle-rotted wooden chest overgrown with thick green vines and a few bright flowers, its old troll carving half hidden under the leaves.
4. HIGHLAND CHEST (Arathi, the Alterac foothills): a stout grey stone-and-oak chest bound with dark iron, a carved knotwork band across the front and a heavy ring handle.
Row 2:
5. DARK IRON STRONGBOX (Onyxhollow, the Dark Iron): a squat chest of blackened iron with glowing orange seams like cooling metal, a thick riveted lock and an anvil sigil on the front.
6. ELVEN GILDED CHEST (Dawnhaven, the Sunreach Conclave): a blood elf chest of crimson-lacquered wood with gold filigree, a phoenix crest on the lid, and a few autumn leaves resting on top.
7. HIGHBORNE RUIN CHEST (Azshara): an ancient chest of cracked blue-white marble with flowing elven carving, a dull arcane crystal set in the lid, and a little ivy on one corner.
8. BARK HOLLOW CHEST (the World Tree): a chest carved straight out of a thick piece of golden bark, lashed with vine rope, a troll loa mark burned into the front.
Row 3:
9. AETHERIAN COFFER (Caelora, the sky): an elegant white-marble chest with gold trim and a deep royal-blue panel, a sky-blue crystal set into the lid glowing softly.
10. GEODE CHEST (the Underdark): a chest made from a split geode, rough grey stone outside and a lid lined with glittering purple and blue crystal, bound with copper bands.
11. STORM DRIFTWOOD CHEST (the Tempest isles): a chest built from storm-blackened driftwood and whale bone, its lid scorched by lightning in a jagged line and tied down with fishing net.
12. GRAVE-WARD CHEST (Deadwind Pass): a narrow, dark stone chest like a small tomb, a raven carved on the lid and a faded ward rune that glows faintly violet.
```

---------------------------------------------------------------------
## SHEET CH3: DUNGEON CHESTS AND BOSS REWARDS, 12

```
Row 1 (dungeon side rooms):
1. DARK OAK CHEST: a big, heavy chest of almost black oak with iron studs, a domed lid and a large keyhole.
2. STEEL STRONGBOX: a squared steel strongbox with thick riveted edges, two side handles and a heavy padlock.
3. STONE COFFER: a carved stone chest like a small sarcophagus, worn runes round its lid, moss in the cracks.
4. SUNKEN CORAL CHEST: a sea-drowned chest crusted with pink and orange coral and pale shells, a starfish on the lid and seaweed hanging off one side.
Row 2 (boss rewards, all drawn ONE SIZE LARGER than every other chest on the three sheets):
5. FROST-RIMED CHEST: a chest encased in pale blue ice and frost, icicles hanging from the lid's edge, the dark wood just visible through the ice.
6. FEL-FORGED CHEST: a black-iron chest with jagged spikes on the corners and glowing fel-green runes running along its seams.
7. CRYSTAL RELIQUARY: a reliquary of clear blue crystal panels in a silver frame, a soft light glowing inside it.
8. ORNATE GOLD CHEST: a royal chest of polished gold with jewelled corners, a big red gem on the lock and a crown motif across the lid.
Row 3 (boss rewards, ONE SIZE LARGER):
9. ROYAL GOLD CHEST: a deep-red lacquered chest with heavy gold bands and corners, a gold lion's-head lock plate, and coins peeking from under the closed lid.
10. OSSUARY: a chest built of bones and skulls bound with dark iron, a grinning skull as its lock, faint violet light in the eye sockets.
11. VOID OBSIDIAN CHEST: a chest of glossy black obsidian with swirling purple void light trapped inside its glassy surface and a few floating shards above the lid.
12. MOLTEN CHEST: a chest of cracked black rock with lava glowing orange through every crack, heat haze above the lid, and an iron lock half melted.
```

---------------------------------------------------------------------
## After you generate them

Each sheet slices to `assets/tiles/chests/ch_<name>.png` with the leader slicer's magenta key and one shared canvas
per sheet, so every chest sits on the same baseline. The old names stay the same (plain_box, rope_crate,
iron_banded, travel_trunk, orc_hide, savannah, troll_tiki, goblin_lockbox, moonwood, sea_chest, undead_rusted,
chained_cursed, dark_oak, steel_strongbox, stone_coffer, sunken_coral, frost_rimed, fel_forged, crystal_reliquary,
ornate_gold, royal_gold, ossuary, void_obsidian), and the old burlap_crate retires. The new ones are sandstone_coffer,
wildwood, vine_bound, highland, dark_iron, elven_gilded, highborne_ruin, bark_hollow, aetherian_coffer, geode,
storm_driftwood, grave_ward and molten. They're added to `world/chest_looks.py`, each region to its own look, and
the boss chests are drawn larger in game the same way they are on the sheet.
