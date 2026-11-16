# Creature materials: icon sheet (48 icons)

The 48 crafting materials that particular monsters drop (`tools/build_mob_materials.py`, 15 Nov 2026).
Each one currently borrows a vendor-trash icon as a placeholder. Once this sheet is sliced into
`assets/gathering_nodes/mob_reagents/`, named for each material, the icons pick themselves up and the
placeholders are deleted.

Order is by level, low to high, 8 to a row.

```
Generate ONE sprite sheet image, 1536x1024, an 8 columns x 6 rows grid = 48 separate game icons (each cell 192x170). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style for crafting reagents: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. These are raw parts taken off monsters, so they look natural and a little rough, not crafted or polished. No hands, no text, no labels, no grid lines, no frames, no borders, no containers unless named. No magenta or pink inside any icon. Row by row, left to right:

Row 1:
1. SCORPID VENOM GLAND: a soft, translucent yellow sac of venom with a stub of black tail attached
2. COARSE BOAR BRISTLE: a tied bundle of stiff dark-brown bristles
3. WHIRLING GRIT: a small swirl of tan sand spinning in the air in a tight spiral, no container
4. KOLKAR WAR-BEAD: a single fat clay bead painted with red and white stripes, a bit of leather thong through it
5. RAPTOR TOOTH: one curved, serrated ivory tooth with a bloody brown root
6. SLICK MURLOC FIN: one webbed green-blue fin with spines, glistening wet
7. SIREN SCALE: one large iridescent blue-green scale, shimmering like mother-of-pearl
8. HARPY PLUME: one long barred brown-and-cream feather

Row 2:
9. BRISTLEBACK TUSK: one yellowed curved quilboar tusk, notched and sharpened on one edge
10. DREADMIST ICHOR: a lumpy glob of thick glowing green ichor with a wisp of smoke rising off it
11. TOUGH CROCOLISK SCALE: one thick ridged dark-green scale plate, rough as bark
12. GHOUL SINEW: a coiled length of dried grey sinew, tied in the middle
13. CURSED WORGEN FANG: one long yellow canine fang with a faint purple glow along the edge
14. SPIDER'S SILK STRAND: a neat coil of glossy white spider silk wound in a loop
15. DUSKBAT WING: one thin leathery bat wing, light glowing through the membrane
16. GRAVE DUST: a small heap of cold grey dust with a pale blue chill wisp above it

Row 3:
17. LIVING BARK: a curling strip of green-brown bark with a tiny living leaf sprouting from it
18. FEL EMBER: one glowing fel-green coal with green sparks
19. SATYR HORN: one curled black horn, sawn off flat at the base
20. THICK YETI FUR: a heavy tuft of thick shaggy white fur
21. KOBOLD CANDLE: a stubby melted tallow candle with a small flame still lit, wax dripping
22. ELKHORN ANTLER: one forked tine of pale antler
23. LYNX WHISKER: a few long stiff white whiskers bundled together, catching the light
24. BLOWDOWN ASH: a fist-sized lump of hard-packed grey volcanic ash with a faint orange glow in its cracks

Row 4:
25. SEQUOIA AMBER: a rough lump of clear golden amber glowing softly from inside
26. BASALT HEART: a dense rounded chunk of black basalt with a faint deep-red core showing through a crack
27. WINDSHEAR QUILL: one long grey-and-white flight feather with a faint swirl of wind around its tip
28. SALTPAN CRYSTAL: one clear cube-shaped salt crystal, glassy and white
29. WITHERBARK HEX BEAD: one carved bone bead covered in troll runes, a faint purple hex glow
30. MOOR ADDER VENOM: a small corked glass vial of milky white venom
31. BARROW DUST: a small heap of dry ancient brown-grey dust with a pale ghostly wisp rising
32. JUNGLE RAPTOR TALON: one large hooked black talon

Row 5:
33. COILVINE SCALE: one glossy green-and-gold snake scale, coin-sized and gleaming
34. SILVERBACK SINEW: a thick coiled cord of tough grey-brown sinew
35. LUMINOUS SPORE: a pinch of tiny glowing blue spores floating in a small cluster
36. LATTICE SHARD: one jagged shard of pale violet living crystal with a soft hum of light
37. CRUSTBACK SCORPID PLATE: one curved plate of salt-white scorpid shell, crusted and hard
38. BASILISK EYE: one round eyeball turned to grey stone, a faint yellow slit pupil still visible
39. SUNSTONE SHARD: one jagged shard of glowing orange-gold crystal, warm light around it
40. SALTSCALE PEARL: one large grey pearl on a short frayed cord

Row 6:
41. SINKHOLE ICHOR: a thick glob of black ichor with an oily sheen
42. VEINLIGHT MOTE: one small drifting mote of bright cyan-white light with a soft halo
43. IRONBARK HEARTWOOD: a short squared billet of dark dense heartwood with tight rings on the end grain
44. JADEFIRE EMBER: one glowing jade-green coal burning with cold green flame
45. HIVE RESIN: a sticky amber-brown lump of resin with a tiny insect leg trapped in it
46. SCORIA HEART: a rough black-and-red porous rock with a molten orange core glowing through its holes
47. CALDERA DRAKE SCALE: one large black scale edged in glowing orange, like cooling lava
48. ASHFUR MANE: a hank of coarse grey-red hair, singed and curled at the ends
```

After you generate it, send the image and I'll slice it into `assets/gathering_nodes/mob_reagents/`,
named for each material, and delete the placeholders.
