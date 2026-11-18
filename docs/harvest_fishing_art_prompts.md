# Art drop, 18 Nov 2026: harvest finds, fishing mounts, Deadwind backgrounds (3 sheets)

Kyle, 18 Nov 2026: "How about you give me the art drop. I can do 3 sheets right now." The three:

1. **Sheet H1: 36 icons** for the harvest finds and the fishing extras (`docs/harvest_finds_design.md`): the
   sixteen quest starters you find while mining, picking herbs, skinning and fishing, the Earth junk and salvage
   that comes up in a fishing net, and the reins for the six fishing mounts.
2. **Sheet H2: six fishing mounts**, one for each kind of water, each the rarest thing its pools can give.
3. **Sheet H3: eight Deadwind combat backgrounds.** The pass and the Exclusion Zone borrow other zones' art today.

Until H1 and H2 land, the finds use stand-in icons and the mounts can be learned but not ridden (the card says so),
the same as the Collection's six did.

---------------------------------------------------------------------
## SHEET H1: 36 icons  (paste this whole block)

Square bag icons, sliced to `assets/icons/quest_items/` (the starters) and `assets/icons/vendor_trash/` (the junk and
salvage) and `assets/icons/collection/` (the reins). Attach two or three existing icons (`qi_journal.png`,
`qi_horn.png`, `qi_signet.png`) as the style reference.

```
Generate ONE image, 2048x2048, a grid of 6 columns x 6 rows = 36 separate square inventory icons, each about 341x341. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere (not even on the modern objects), no magenta or pink inside the icons. Nothing modern except where a cell says so.

Icons, row by row, left to right:
Row 1 (strange ore, found while mining): 1 a lump of raw copper ore with veins that glow warm orange like a slow heartbeat, a faint pulse of light around it; 2 a grey lump of tin ore with a huge brown fossil tooth, long and serrated, half sunk in it; 3 a shard of pale blue-silver mithril ore with thin rings of light rippling off it like sound; 4 a chunk of dark teal thorium ore with one glassy flat face, and pressed clearly into that glass, a single human fingerprint.
Row 1 continued (strange herbs): 5 a sprig of silverleaf with one extra leaf growing where it shouldn't, the leaves veined in sickly purple; 6 a red kingsblood flower on its stem, thick red sap dripping from the cut end like blood.
Row 2: 7 a pale fadeleaf leaf that is half see-through, its outline shimmering, as if it's only half there; 8 a sprig of blue-green dreamfoil whose leaves curl like closed sleeping eyelids, a soft green glow around it; (strange hides, found while skinning) 9 a scrap of tanned hide with a crude map scratched into it, a path and an X; 10 a beast's furry ear with a bright yellow plastic wildlife tracking tag clipped through it (modern, a real ear tag); 11 one single enormous scale, dark green with a bronze edge, as big as a shield; 12 a patch of hide made of two different animals' skins crudely stitched together with black thread, pale and rotting at the seam.
Row 3 (strange catches, found while fishing): 13 a green glass bottle with a cork, a rolled note inside, barnacles on the glass; 14 a modern smartphone, the screen cracked, a strand of seaweed caught on it, water droplets (modern); 15 a sailor's leather journal wrapped in kelp and tied with rope, swollen with seawater; 16 a small yellow rubber bath duck, faded, with a name tag tied round its neck on string (no writing visible) (modern).
Row 3 continued (Earth junk, all modern objects washed through with the transplants): 17 a ring of car keys with a fob and a little plastic keyring charm (modern); 18 a single worn flip-flop, blue rubber (modern).
Row 4 (more Earth junk, modern): 19 a pair of dark sunglasses with one lens cracked; 20 a dented aluminium soda can, faded red, no writing; 21 a steel wristwatch with a cracked face and a leather strap; 22 a fuzzy yellow-green tennis ball, waterlogged; 23 a white ceramic coffee mug with a chip in the rim, no writing; 24 a black TV remote control with rubber buttons.
Row 5: 25 a garden gnome with a red hat, chipped paint, covered in algae (modern); 26 a small green plastic toy dinosaur (modern); (salvage from the sunken wrecks) 27 a small iron-bound lockbox crusted with barnacles, its lock rusted; 28 a sodden leather coin purse spilling a few gold coins; 29 a dented goblin fuel canister, green paint, leaking a rainbow oil slick; 30 a broken wooden crate, waterlogged, with a ship's rope still knotted round it.
Row 6 (reins for six fishing mounts, each a leather bridle with a charm of its animal): 31 rope reins with a charm of a crab's claw; 32 brown leather reins with a charm of an otter's paw; 33 green reins with a charm of a frog carved in jade; 34 white reins with a charm of a walrus tusk; 35 black reins with a glowing ember-red salamander charm; 36 dark blue reins with a small glowing lantern charm like an anglerfish lure.
```

Send it back and it's sliced in this order:

```
hf_ticking_copper, hf_tin_fossil_tooth, hf_singing_mithril, hf_thorium_fingerprint, hf_mutated_silverleaf, hf_bleeding_kingsblood,
hf_unfading_fadeleaf, hf_dreaming_dreamfoil, hf_scratched_hide_map, hf_tagged_ear, hf_great_scale, hf_stitched_hide,
hf_message_bottle, hf_waterlogged_phone, hf_kelp_journal, hf_rubber_duck, ej_car_keys, ej_flip_flop,
ej_sunglasses, ej_soda_can, ej_wristwatch, ej_tennis_ball, ej_coffee_mug, ej_tv_remote,
ej_garden_gnome, ej_toy_dinosaur, sv_barnacled_lockbox, sv_sodden_coin_purse, sv_goblin_canister, sv_wreck_crate,
col_reins_brine_crab, col_reins_river_otter, col_reins_glimmer_frog, col_reins_rimefin_walrus, col_reins_cinder_salamander, col_reins_abyssal_lurker
```

---------------------------------------------------------------------
## SHEET H2: six fishing mounts, 4 facings each  (paste this whole block)

Same shape, slicer and rules as the Collection's Sheet C: 6 columns x 4 rows, 1536x1024, magenta key, no rider.
Sliced by `tools/asset_pipeline/slice_mount_sheet.py SHEET.png brine_crab river_otter glimmer_frog rimefin_walrus
cinder_salamander abyssal_lurker`. Attach two or three existing mount facings (`war_kodo_left.png`,
`rune_saber_down.png`, `tidecaller_sea_turtle_right.png` if it's in by then) as the style reference.

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no water, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from head to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its head, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are RARE RIDING MOUNTS that a fisherman hauls out of the water, for a Horde fantasy RPG, shown with NO RIDER. Each wears a saddle and tack made by fishermen, with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose on land, feet planted, head up, no motion blur, a little wet and gleaming. Each needs a silhouette you could pick out at a glance from the other five, and each should look special and a bit funny-wonderful, the prize of years at the water's edge.

Columns, left to right (the same six animals in every row, each turned according to that row's rule):
1. BRINE CRAB - a giant shore crab the size of a kodo, standing high on its jointed legs, a broad sandy-red shell crusted with barnacles and a few limpets, two big claws held up in front, eyes on stalks. A saddle lashed onto the shell with tarred rope, a fishing-net blanket, cork floats hanging off it.
2. RIVER OTTER - a huge sleek river otter the size of a horse, rich brown wet-look fur, a pale cream chest, whiskers, small round ears, a long thick tail, a cheerful face. A brown leather saddle with brass rivets, a creel basket hung at one side.
3. GLIMMER FROG - a giant swamp frog the size of a kodo, squatting on its powerful back legs, smooth green skin with gold speckles that faintly glow, big golden eyes, a wide grin. A saddle of woven reeds and green cloth, a string of small lily pads and a lantern hanging off it.
4. RIMEFIN WALRUS - a great walrus on its flippers, heavy and wrinkled, grey-brown hide with frost on its back and whiskers, two long ivory tusks, a bristly moustache, small calm eyes. A saddle of white fur and walrus-hide straps, ice-fishing gear (an auger, a little drum) hung off it.
5. CINDER SALAMANDER - a long low lava salamander the size of a horse, black rocky skin with glowing orange cracks, a ridge of small flame-like frills along its back, bright ember eyes, a thick tail with a glowing tip. A saddle of dark iron and scorched leather that doesn't burn.
6. ABYSSAL LURKER - a strange deep-sea anglerfish creature walking on four stubby fin-legs, dark blue-black skin, a huge mouth full of needle teeth set in a goofy grin, little pale eyes, and a long glowing lure dangling from its forehead on a stalk, lighting its own face. A saddle of dark leather and old ship's brass, a diver's lamp at the horn.

Scale: keep sizes consistent with real proportions: the crab and the frog are the widest; the walrus is heavy and low; the otter and the salamander are long and low; the lurker is round and squat. Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

---------------------------------------------------------------------
## SHEET H3: eight Deadwind combat backgrounds  (paste this whole block)

A contact sheet of eight finished paintings, sliced by `tools/asset_pipeline/slice_background_sheet.py SHEET.png
assets/backgrounds/deadwind` (it finds the panels itself). Wired in `world/combat_backgrounds.py` when they land.

```
Generate ONE image, 2048x1024: a contact sheet of 8 separate finished paintings in a grid of 4 columns x 2 rows, each painting 16:9, on a flat solid near-black (#101010) backing with a clear gutter between them and round the edge. No captions, no labels, no text anywhere, no frames, no borders.

Every painting is a wide painted battle backdrop for a turn-based fantasy RPG, World of Warcraft Classic art style: painterly, semi-realistic, rich colour, visible brushwork, no photorealism. A ground-level view of a place where a fight happens. The lower third of each painting is open, fairly flat ground where the fighters will stand, kept clear of big objects. The interest is in the middle distance and at the left and right edges. No people, no creatures, no characters, no vignette. The whole set is one region, a cursed mountain pass where time has stopped in places, so they share one mood: grey-violet dusk, dead trees, bone-dry ground, cold light.

Paintings, row by row, left to right:
1. THE DEAD FOREST: a road through a forest of tall dead grey trees with no leaves, bark peeling, roots like claws; low mist between the trunks; a few ravens' nests; a broken wooden fence along the road; the sky a bruised violet dusk.
2. THE WIDOWS' WOOD: the same dead trees thick with white spider silk, sheets of web strung between the trunks and over the ground, wrapped bundles hanging from branches, a dim greenish glow from clusters of eggs in the silk.
3. THE SLEEPING GORGE: the floor of a deep narrow gorge with a river that has stopped: the water hangs frozen in mid-splash over the rocks, glassy and still, droplets suspended in the air like beads; sheer grey cliffs on both sides; a thin strip of pale sky high above.
4. THE RUPTURE: a scorched rocky field split open by a long glowing crack in the ground, green-white light leaking out of it; in the middle distance an enormous old rusted wheel, like a great wheel of hanging cars at an abandoned fair, standing tall and still against the dusk; a fenced lot round it, warning poles leaning, ash drifting. Eerie, silent, iconic.
5. UNDER THE WHEEL: a huge underground hollow beneath the wheel: tall shelves of black glass in rows like an archive, things sealed in the glass; rusted cars hanging from chains overhead; a pale green glow from a shaft in the floor; dust in the air.
6. THE REACTOR HALL: a vast ruined hall of rusted machinery: a row of enormous turbines, collapsed walkways, a flooded basement floor with oily water reflecting a sickly glow, black chunks of fallen stone, a sealed central block in the distance. Fantasy-industrial, ancient and dead.
7. THE FOOT: the deepest chamber: a lake of slowly glowing molten slag, orange and sickly green, filling the cavern floor, a crust forming on its surface, four channels of glowing melt pouring in from the walls, an island of rock in the middle with a dark pulsing shape on it; heat haze. The fighters stand on a rock shelf at the front.
8. THE DROWNED SEEP: a long winding drain cave, a stream of glowing green-grey seep running down its middle, slick black walls, oxbow pools off the bends, a faint sick red glow from far down at the bottom.
```

Sliced in this order (left to right, top to bottom):

```
dw_dead_forest, dw_widows_wood, dw_sleeping_gorge, dw_rupture, ez_under_the_wheel, ez_reactor_hall, ez_the_foot, dw_drowned_seep
```

They go to: the dead forest and the Widows' Wood for Deadwind West and the Widows' Nest; the gorge and the rupture for
Deadwind East (the rupture for the wheel's lot); one for each of the Exclusion Zone's three floors; the seep for the
Drowned Seep. Ariden's Watch keeps the dead forest.
