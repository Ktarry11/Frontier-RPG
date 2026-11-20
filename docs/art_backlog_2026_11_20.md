# Frontier art backlog (20 Nov 2026)

**Landed 20 Nov, the same afternoon: H14, I3, I2, M2 and K1 to K3, all sliced and in the game.** What's left is the new
player sprites (`docs/player_sprite_prompts.md`), then walk cycles on them.

Everything waiting on art, ready to paste into ChatGPT one sheet at a time. Each sheet says what to attach as the style
reference, the block to paste, and how it's sliced when it comes back (send the sheets back here and I'll slice and
wire them).

| Sheet | What | Count | Status |
|---|---|---|---|
| **I2** | Reins icons for the 12 wild and 16 Exalted mounts | 28 | Written 20 Nov, never pasted. All 28 show a stand-in |
| **M2** | Master crafting icons (Manticore, Chimera, Mending, Tidemail, Wildstalker, Brute, the jewellery, Dreamsilk) | 36 | Written 18 Nov, never pasted. They wear stand-ins |
| **H14** | **New Exalted mounts** for the five new factions (Kyle, 20 Nov: "will need new mounts for new factions") | 5 | New |
| **I3** | Their five reins, and the five new factions' tabards | 10 | New |
| **K1, K2, K3** | Keepsake icons, one per recruit (what each gives you when they become Sworn) | 98 | New. All 98 show a stand-in |
| **6A, 6B** | Recruit sheet 6: 16 new recruits (12 men, 4 women), sprites and portraits (`docs/recruit_art_prompts_sheet6.md`) | 32 | Written 20 Nov |
| **AE-M, AE-W** | 24 Aetherian men and 24 Aetherian women for NPCs, front view (`docs/recruit_art_prompts_sheet6.md`) | 48 | Written 20 Nov. Covers SKY-NPC's women |
| **SKY-NPC** | The two Crown allies' own figures (Ilaren Vey, Leandro Arrieta) and the Mural Shard's Collection icon | 3 | Not written yet. The Aetherian women moved to AE-W |
| **WALK** | Walk cycles | - | **Parked** (Kyle, 20 Nov: "Walk cycles will come after better sprites"). New player sprites first, about five a race, then walk cycles on those |

**Order I'd paste them in:** H14 and I3 first (the Feathermoon Sentinels and the Highbough Tribes are in the game today
with no mount at Exalted), then I2, M2 and the keepsakes. Walk cycles wait for the new player sprites.

**Not written yet** (tell me and I'll write them): the professions screen's own art (tab art, frames, station art);
the faint per-zone backgrounds for the quest dialog (these could reuse each zone's combat background, so maybe no new
art at all). **A question, not art:** class forms in combat. The Tinker's Mechsuit and its three looks are drawn but
only ever worn in a fight, and the combat screen still shows the person, so they're never seen.

---------------------------------------------------------------------

## SHEET H14: Exalted mounts for the new factions  (paste this whole block)

Attach `assets/mounts/war_kodo_left.png` and `assets/mounts/rune_saber_down.png` as the style reference (the H11 rules).
The Feathermoon Sentinels and the Highbough Tribes are in the game now; the Aetherians come with the Sunward Crown;
Kyr'vahl and Ul'Kharad come with their continents, but there's no harm drawing them now.

```
Generate ONE sprite sheet image, 1536x1024, a 5 columns x 4 rows grid = 20 separate sprites. Flat pure #FF00FF magenta background everywhere. Each sprite sits fully inside its own cell with wide margin and does NOT touch or overlap neighbours or the image edge. No ground shadow, no ground plane, no text, no labels, no grid lines. Painterly semi-realistic 3/4 top-down view, WoW Classic art style, matching the attached references exactly in style, outline and level of detail, consistent lighting from the top-left. Crisp clean edges, no magenta tint on the animals themselves (avoid pink/magenta colours inside any sprite).

THE MOST IMPORTANT PART OF THIS IMAGE IS THAT EACH COLUMN SHOWS ONE ANIMAL TURNED FOUR DIFFERENT WAYS. Each COLUMN is one creature. The four ROWS of that column are that same creature ROTATED ON THE SPOT and seen from four different angles. The four cells in a column must NOT be four copies of the same picture - if a column looks like the same pose four times, the image is wrong. Read these four rules before drawing anything:

Row 1 - FACING THE VIEWER (south). The creature looks straight at the camera. You CAN see its whole face, both eyes, its chest, and its front legs coming toward you. You CANNOT see its back or its tail. Its body is foreshortened, front-on, nose nearest the camera.

Row 2 - FACING LEFT (west), full side profile. Head near the LEFT edge of its cell, tail near the RIGHT edge. You CAN see one eye, one full side of the body, the whole back line from skull to tail, and all legs in profile. You CANNOT see its chest front-on and you CANNOT see both eyes.

Row 3 - FACING RIGHT (east), full side profile. The exact mirror of row 2: head near the RIGHT edge of its cell, tail near the LEFT edge.

Row 4 - FACING AWAY (north), seen from directly behind. You CAN see the back of its skull, its back, its rump and the tail coming toward the camera. You absolutely CANNOT see its face, its eyes, its mouth, its chest or its front legs.

In every row the saddle stays on the creature's back and is drawn from that same angle.

These are the PROUDEST RIDING MOUNTS in a Horde fantasy RPG, each the reward for reaching Exalted with one faction, shown with NO RIDER. Each wears grand tack in its faction's colours and style with the saddle seat clearly visible on the middle of its back, large enough for a humanoid rider to sit on. Standing idle pose, feet planted, head up, no motion blur. Each needs a silhouette you could pick out at a glance from the other four.

Columns, left to right (the same five animals in every row, each turned according to that row's rule):
1. FEATHERMOON WAR OWL (the Feathermoon Sentinels, night elf sentinels of a sea-cliff stronghold) - a giant snowy-white owl as big as a horse, standing upright on two thick feathered legs with black talons, huge round amber eyes, soft silver-grey bars across its wings, its wings folded tight to its sides; violet and silver-white barding with crescent-moon silver plates on its chest, a slim night elf saddle of violet leather with a tall curved back.
2. CLOUDTOP WYVERN (the Highbough Tribes, trolls who live in a colossal World Tree) - a lean blue-grey wyvern walking on all fours on the knuckles of its folded wings and its hind legs, a long barbed scorpion-like tail held high, a crest of stiff blue-grey feathers, a lion-like face with a short mane; teal and red troll tack, bone and wooden beads, a carved heartwood saddle with a few golden leaves tucked into the straps.
3. LUMEN STAG (the Aetherians, a tall crystal-grown people of floating sky cities) - a tall, elegant stag built of pale white stone and gold filigree rather than flesh, great antlers of glowing pale-blue crystal, eyes of soft blue light, its hooves hovering a hand's width above the ground with a faint blue glow beneath each one; a white and gold saddle with a small crystal set at its front.
4. GALESTRIDER (Kyr'vahl, the Last Updraft, a clan of feathered avian hunters of the storms) - a huge flightless storm bird like a giant cassowary or moa, powerful long legs with hooked talons, a tall crest of storm-blue feathers crackling with tiny threads of white lightning, slate-grey body plumage barred with white, a sharp hooked beak; light hunter's tack of grey leather and white feathers, a lean saddle with a quiver loop.
5. STONEBACK AUROCHS (Ul'Kharad, the First Stone, the oldest house of the cloud giants) - a massive aurochs whose hide is plates of grey slate stone, a thick shaggy mane and beard of cloud-white wool, two great forward-curving horns of pale amethyst crystal, small violet crystals growing along its spine; heavy stone-grey and cloud-white tack with carved runes, a broad square saddle of dark leather on a stone frame.

Every animal fills roughly 70-85% of its cell. Keep design, colours, markings and tack identical across the four facings of the same mount. Fully opaque, clean edges, no baked checkerboard or haze.

Before you finish, check the image: every column should show one animal from the front, then from its left side, then from its right side, then from behind. If any column shows the same view twice, redraw that column.
```

Sliced by `PYTHONPATH=. python3 tools/asset_pipeline/slice_mount_sheet.py SHEET.png feathermoon_war_owl highbough_cloudtop_wyvern aetherian_lumen_stag kyrvahl_galestrider ulkharad_stoneback_aurochs`.

---------------------------------------------------------------------

## SHEET I3: the new mounts' reins and the new factions' tabards  (paste this whole block)

Attach `assets/icons/gear/tabard_cenarion_circle.png` and `assets/icons/collection/col_reins_kodo.png` as the style reference.

```
Generate ONE image, 1536x1024, a grid of 5 columns x 2 rows = 10 separate inventory icons. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 70% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left. No frames, no borders, no text, no letters or numbers anywhere, no magenta or pink inside the icons.

Row 1 is five items that each summon a riding mount, seen in a slight 3/4 view, left to right: 1 a slim violet leather bridle with a silver crescent-moon charm and one white owl feather; 2 teal and red braided reins with a carved wooden wyvern-tooth clasp and a golden leaf; 3 a white and gold filigree bridle with a small glowing pale-blue crystal at its centre; 4 a storm-blue feather wrapped in grey leather, tiny white sparks along its edge; 5 a heavy cord of cloud-white wool through a ring of grey stone set with an amethyst crystal.

Row 2 is five faction tabards, seen straight from the front. Every tabard is the SAME SHAPE: a sleeveless cloth tabard laid flat, a long rectangular front panel with a V neck and a squared hem, the faction's emblem large in the middle of the chest; only the colours, the trim and the emblem change. Left to right: 6 deep violet with silver-white trim, the emblem a silver crescent moon with a single white feather laid across it; 7 teal with a red zig-zag border, the emblem a great tree whose roots curl into a pair of troll tusks; 8 white with gold trim, the emblem a floating island with a pale-blue crystal spire inside a gold sun ring; 9 storm grey-blue with white trim, the emblem a bird's talon gripping a white lightning bolt; 10 slate grey with cloud-white trim, the emblem a squared mountain stone crowned with a cloud and set with one amethyst crystal.
```

Sliced by `python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png --cols=5 --ids=col_reins_feathermoon_war_owl,col_reins_highbough_cloudtop_wyvern,col_reins_aetherian_lumen_stag,col_reins_kyrvahl_galestrider,col_reins_ulkharad_stoneback_aurochs,gear/tabard_feathermoon_sentinels,gear/tabard_highbough_tribes,gear/tabard_aetherians,gear/tabard_kyrvahl,gear/tabard_ulkharad`.

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

---------------------------------------------------------------------

Attach two or three existing gear icons (`gear_inv_helmet_36.png`, `gear_inv_misc_cape_06.png`) as the style reference.

## SHEET M2: 36 icons  (paste this whole block)

```
Generate ONE image, 2048x2048, a grid of 6 columns x 6 rows = 36 separate square inventory icons, each about 341x341. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no magenta or pink inside the icons. These are high-end crafted level-60 gear: well made, clean and handsome. Pieces from the same collection share its colours and motifs so they read as one set.

Icons, row by row, left to right:
Row 1: 1 a pair of mail gauntlets of tawny gold manticore scales with small barbed spikes; 2 a mail girdle of tawny gold manticore scales with small barbed spikes; 3 a pair of mail leggings of tawny gold manticore scales with small barbed spikes; 4 a pair of mail boots of tawny gold manticore scales with small barbed spikes; 5 a leather tunic of patchwork hide of three beasts, red, green and purple, with a spiny ridge, grander, with a soft glow (epic); 6 a pair of leather leggings of patchwork hide of three beasts, red, green and purple, with a spiny ridge, grander, with a soft glow (epic).
Row 2: 7 a mail hauberk of three-coloured overlapping scales, red, green and purple, grander, with a soft glow (epic); 8 a pair of mail leggings of three-coloured overlapping scales, red, green and purple, grander, with a soft glow (epic); 9 a scale brigandine vest of tawny gold manticore scales with small barbed spikes; 10 a pair of mail spaulders of tawny gold manticore scales with small barbed spikes; 11 a pair of mail bracers of tawny gold manticore scales with small barbed spikes; 12 a leather vest of soft green-dyed leather with little pouches of herbs and a leaf motif.
Row 3: 13 a pair of leather leggings of soft green-dyed leather with little pouches of herbs and a leaf motif; 14 a mail hauberk of blue-glazed scales that look wet, like river water; 15 a leather tunic of dark fur-lined leather stitched with faint glowing green runes; 16 a pair of leather leggings of dark fur-lined leather stitched with faint glowing green runes; 17 a mail vest of tawny manticore scale with a quiver hook and many pockets; 18 a leather chest harness of heavy tan leather made mostly of thick buckled straps and studs.
Row 4: 19 a pair of leather leggings of heavy tan leather made mostly of thick buckled straps and studs; 20 a mail coif of three-coloured overlapping scales, red, green and purple, grander, with a soft glow (epic); 21 a long leather robe of soft green-dyed leather with little pouches of herbs and a leaf motif, grander, with a soft glow (epic); 22 a leather tunic of dark fur-lined leather stitched with faint glowing green runes, grander, with a soft glow (epic); 23 a ring of icy pale-blue sapphire set in frosted silver; 24 a pendant on a fine chain of icy pale-blue sapphire set in frosted silver.
Row 5: 25 a ring of plain icy-blue silver with a frost-white edge; 26 a choker of plain frosted silver, no stones; 27 a signet ring of green-silver sylvanite set with an icy blue sapphire, frost on the band, grander, with a soft glow (epic); 28 a neck torc of green-silver metal set with three large emeralds, grander, with a soft glow (epic); 29 a cloth hood of pale lavender and silver silk that shimmers like moonlight; 30 a cloth mantle of pale lavender and silver silk that shimmers like moonlight.
Row 6: 31 a long cloth robe of pale lavender and silver silk that shimmers like moonlight; 32 a pair of cloth cuffs of pale lavender and silver silk that shimmers like moonlight; 33 a pair of cloth gloves of pale lavender and silver silk that shimmers like moonlight; 34 a cloth sash of pale lavender and silver silk that shimmers like moonlight; 35 a pair of cloth trousers of pale lavender and silver silk that shimmers like moonlight; 36 a pair of cloth slippers of pale lavender and silver silk that shimmers like moonlight.
```

Slices in this order:

```
gear/gear_m60_manticore_scale_gauntlets,gear/gear_m60_manticore_scale_girdle,gear/gear_m60_manticore_scale_legguards,gear/gear_m60_manticore_scale_sabatons,gear/gear_m60_chimera_hide_jerkin,gear/gear_m60_chimera_hide_leggings,gear/gear_m60_chimera_scale_hauberk,gear/gear_m60_chimera_scale_legguards,gear/gear_m60_manticore_scale_brigandine,gear/gear_m60_manticore_scale_spaulders,gear/gear_m60_manticore_scale_bracers,gear/gear_m60_manticore_mending_vest,gear/gear_m60_manticore_mending_leggings,gear/gear_m60_manticore_scale_tidemail,gear/gear_m60_manticore_wildstalker_jerkin,gear/gear_m60_manticore_wildstalker_leggings,gear/gear_m60_manticore_scale_huntsman_s_vest,gear/gear_m60_manticore_brute_s_harness,gear/gear_m60_manticore_brute_s_leggings,gear/gear_m60_chimera_scale_helm,gear/gear_m60_chimera_mending_robe,gear/gear_m60_chimera_wildstalker_tunic,gear/gear_m60_glacier_sapphire_ring,gear/gear_m60_glacier_sapphire_pendant,gear/gear_m60_frostforged_band,gear/gear_m60_frostforged_choker,gear/gear_m60_sylvanite_signet_of_frost,gear/gear_m60_sylvan_emerald_torc,gear/gear_m60_dreamsilk_hood,gear/gear_m60_dreamsilk_mantle,gear/gear_m60_dreamsilk_robe,gear/gear_m60_dreamsilk_cuffs,gear/gear_m60_dreamsilk_gloves,gear/gear_m60_dreamsilk_sash,gear/gear_m60_dreamsilk_leggings,gear/gear_m60_dreamsilk_slippers
```

The pieces, in order: Manticore-Scale Gauntlets, Manticore-Scale Girdle, Manticore-Scale Legguards, Manticore-Scale Sabatons, Chimera Hide Jerkin, Chimera Hide Leggings, Chimera-Scale Hauberk, Chimera-Scale Legguards, Manticore-Scale Brigandine, Manticore-Scale Spaulders, Manticore-Scale Bracers, Manticore Mending Vest, Manticore Mending Leggings, Manticore-Scale Tidemail, Manticore Wildstalker Jerkin, Manticore Wildstalker Leggings, Manticore-Scale Huntsman's Vest, Manticore Brute's Harness, Manticore Brute's Leggings, Chimera-Scale Helm, Chimera Mending Robe, Chimera Wildstalker Tunic, Glacier Sapphire Ring, Glacier Sapphire Pendant, Frostforged Band, Frostforged Choker, Sylvanite Signet of Frost, Sylvan Emerald Torc, Dreamsilk Hood, Dreamsilk Mantle, Dreamsilk Robe, Dreamsilk Cuffs, Dreamsilk Gloves, Dreamsilk Sash, Dreamsilk Leggings, Dreamsilk Slippers.

---------------------------------------------------------------------

## KEEPSAKES: 98 icons in three sheets (K1, K2, K3)

Kyle, 19 Nov 2026: each Sworn recruit gives you something personal, and it goes on the Collection's Keepsakes tab. These are the small real-world things each of them carried through, so they look like ordinary worn objects from our world, painted in the game's icon style. Attach `qi_journal.png`, `qi_horn.png` and `qi_signet.png` as the style reference.

### SHEET K1: keepsakes 1 to 35  (paste this whole block)

```
Generate ONE image, 2048x1463, a grid of 7 columns x 5 rows = 35 separate square inventory icons, each about 292x292. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no logos or brand marks, no magenta or pink inside the icons. Each is a small, well-worn personal keepsake from our own world, the kind of thing someone carried for years: scuffs, fading, polish from a hand. Where a description mentions writing, a name, a badge photo or a label, draw it as blank or unreadable marks. Draw only the object, never a person or a hand.

Icons, row by row, left to right:
Row 1: 1 the first bound volume of Kesten's record of the Scourge, in pencil; 2 the referee's whistle Adrián carried in his left pocket from the day he landed; 3 the pen Omar gave Tarek as a joke the year they met, the one he marked Tarek's drawings with; 4 the wooden midwife's horn Freja had in her pocket the night the worlds joined, polished dark from years of use; 5 the little blue plastic tool Diego used to open phones at a kiosk in Maracaibo, worn white at the tip; 6 a children's stethoscope from a London ward, with a scuffed plastic bear clipped to the tubing so frightened little ones would let Ama listen; 7 the handheld weather meter Marcus had clipped to his belt the day the worlds joined.
Row 2: 8 the little dinghy shackle key Sondre wore every day for four summers on the Hardangerfjord, worn smooth; 9 Sebastián's grandmother's chimichurri recipe in her own handwriting, stained with oil; 10 a half-cut brass key from Marco's shop in Naples, still in his hand when he landed; 11 Sophia's European Parliament pass on its blue lanyard, the photo faded; 12 Carolina's grandfather's brass compass, carried on the Amazon every day and never used; 13 a heavy gold watch Ryan bought with his first bonus in Boston; 14 Hana's red and yellow surf lifeguard's cap, faded nearly pink by fourteen summers on the beach at Port Waikato.
Row 3: 15 the badge Esteban wore on his collar through nineteen years of surgery under X-ray, its window long gone black; 16 the angled chrome dental mirror Berat kept behind his ear in his surgery in Izmir; 17 the faded orange high-visibility vest Dan landed in, from his first week at a warehouse in Sheffield; 18 Folding reading glasses in a scratched hard case, from the end of every night shift in Bogotá; 19 a Belgian two-euro coin worn smooth from three years of being flipped for every decision Silas didn't want to make; 20 Battered field binoculars from eight years in the Tanzanian bush, the strap mended three times; 21 a dented steel flask with no lid, given to Pavlo by his wife on his first day as a teacher.
Row 4: 22 a worn steel soil knife with a wooden handle, for digging plugs of sedge on the Oregon tide flats; 23 the heavy brass key to the driver's cab of Ivan's tram on Route 13 in Novosibirsk; 24 a bamboo roll of calligraphy brushes, his master's and his own; 25 a small brass oil can, dented and shiny from Marta's hand, carried on the Łódź sewing floor for nineteen years; 26 Lúcia's grandmother's list of everybody on their street in Goiânia, folded soft; 27 a steel tuning fork tuned to A, its tines worn bright; 28 Bakyt's thick leather eagle-hunting glove, worn shiny, which carried his first eagle for twenty-two years in the Tian Shan.
Row 5: 29 a brass bus conductor's ticket punch, Matías's father's, clicked twice before every fight for three years; 30 a steel climbing carabiner scratched to bare metal, clipped to Tomas's belt through eighteen years of rigging and the night he fell forty feet into this world; 31 a scorched and dented yellow wildfire helmet, the one Cristóbal walked out of a Barrens grass fire in on his first day; 32 a steel snake hook with a worn grip, used every day at a Queensland reptile sanctuary; 33 a small dented brass bell from the lead ewe of Giorgi's flock in Kazbegi, carried knotted silent for three years; 34 a slim silver bicycle-spoke wrench on a battered keyring, used to true wheels in Lyon; 35 Blunt-nosed paramedic's shears with HARTIGAN scratched into one handle.
```

Sliced by `python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png --cols=7 --ids=col_keepsake_kesten,col_keepsake_adrian,col_keepsake_tarek,col_keepsake_freja,col_keepsake_diego,col_keepsake_ama,col_keepsake_marcus,col_keepsake_sondre,col_keepsake_sebastian,col_keepsake_marco,col_keepsake_sophia,col_keepsake_carolina,col_keepsake_ryan,col_keepsake_hana,col_keepsake_esteban,col_keepsake_berat,col_keepsake_dan,col_keepsake_marisol,col_keepsake_silas,col_keepsake_rosa,col_keepsake_pavlo,col_keepsake_amber,col_keepsake_ivan,col_keepsake_haruto,col_keepsake_marta,col_keepsake_lucia,col_keepsake_minh,col_keepsake_bakyt,col_keepsake_matias,col_keepsake_tomas,col_keepsake_cristobal,col_keepsake_callum,col_keepsake_giorgi,col_keepsake_camille,col_keepsake_liam`.

### SHEET K2: keepsakes 36 to 70  (paste this whole block)

```
Generate ONE image, 2048x1463, a grid of 7 columns x 5 rows = 35 separate square inventory icons, each about 292x292. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no logos or brand marks, no magenta or pink inside the icons. Each is a small, well-worn personal keepsake from our own world, the kind of thing someone carried for years: scuffs, fading, polish from a hand. Where a description mentions writing, a name, a badge photo or a label, draw it as blank or unreadable marks. Draw only the object, never a person or a hand.

Icons, row by row, left to right:
Row 1: 1 a brass botanist's hand lens on a cord, scratched from forty years of field seasons; 2 a pearl-handled barber's razor, used every day in Santurce for eleven years; 3 the handset from Owen's lorry radio, its coiled cord snapped off, talked into through eight years of night driving; 4 the oldest pick in Emre's uncle's roll, given to him at nine to open a stuck deadbolt in Istanbul, worn thin and bright; 5 a scuffed, grass-stained camogie ball from Saoirse's last county season, thrown at the party for three years; 6 a wooden-handled ice axe carried on nineteen expeditions above eight thousand metres; 7 the folding windlass from a paramedic's tourniquet, clipped to Nicolás's jacket on the bike in Lima.
Row 2: 8 Iker's grandfather's black Basque beret, worn for every pelota match he played; 9 a battered red-filtered headlamp from seventeen years of nights in an observatory dome above the Elqui valley; 10 Soft cotton hand wraps from a gym above a tyre shop in Navotas, washed to grey and rewound every morning for nineteen years; 11 the black curved shoulder rest from Ileana's violin in Cluj, strapped to her back for three years with no violin to put it on; 12 the little brass falconry bell and leather swivel Tegan wore in Brecon; 13 a triangular aluminium engineer's scale rule from a building site in Copenhagen, worn smooth; 14 a strip of orange forestry marking tape, faded to salmon, the kind that marks trees to be left standing.
Row 3: 15 a short, stubby torque wrench from a Land Cruiser's toolkit, in Driss's hand under a truck in the Sahara when the worlds joined; 16 the last few turns of a roll of bright blue kinesiology tape from a clinic in Belo Horizonte, rationed for three years; 17 a flip-up welder's shade from a Busan shipyard, cracked across one lens; 18 a yellow, smoke-stained torch from a Country Fire Authority helmet, dead for years; 19 a white sabre glove from a fencing salle in Naples, never worn here; 20 Smoked-glass goggles from a Talavera pottery workshop in Puebla, for looking into the fire; 21 a cast-iron domino tile, double six, from a kafana in Novi Sad.
Row 4: 22 a brass brewer's hydrometer in a worn leather sleeve, from a brewery in Akureyri; 23 a slim silver mechanical pencil, finishing a sum in a Tehran office when the worlds joined; 24 Héctor's first lucha mask, black with silver flames, sewn by his wife for his debut at twenty; 25 a single foam earplug on a cord, for sleeping in an ambulance between calls in Beirut; 26 a small brass river-gauge plate stamped with depth marks, torn off a flood marker in Sumatra and sewn to Ratih's sleeve for years; 27 the yellow whistle from an orange helicopter survival suit, on a fraying lanyard; 28 a small tooled leather falconer's hood, sized for a saker falcon Khalid flew for eleven years in Al Ain.
Row 5: 29 a floury canvas apron from a bakery on Spanish Town Road in Kingston, never quite clean; 30 a brass surveyor's plumb bob on a worn cord, from the desert east of Amman; 31 a small brass name badge from a hotel band in Havana: Osvaldo, Trompeta; 32 a stonemason's chalk line reel, blue-dusted, from a yard in Nablus; 33 a groundsman's folding knife, the handle worn pale, from the mines outside Pretoria; 34 a brass barista's tamper, handle worn smooth, from a bar in Bologna at six in the morning; 35 Scratched lab safety glasses from an antivenom lab in Durango.
```

Sliced by `python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png --cols=7 --ids=col_keepsake_anjali,col_keepsake_orlando,col_keepsake_owen,col_keepsake_emre,col_keepsake_saoirse,col_keepsake_pasang,col_keepsake_nicolas,col_keepsake_iker,col_keepsake_mateo,col_keepsake_imelda,col_keepsake_ileana,col_keepsake_rhys,col_keepsake_henrik,col_keepsake_eino,col_keepsake_driss,col_keepsake_thiago,col_keepsake_junseo,col_keepsake_skye,col_keepsake_enzo,col_keepsake_alonso,col_keepsake_vuk,col_keepsake_gunnar,col_keepsake_kourosh,col_keepsake_hector,col_keepsake_ziad,col_keepsake_ratih,col_keepsake_fiona,col_keepsake_khalid,col_keepsake_delroy,col_keepsake_karim,col_keepsake_osvaldo,col_keepsake_bashir,col_keepsake_pieter,col_keepsake_gianluca,col_keepsake_camila`.

### SHEET K3: keepsakes 71 to 98  (paste this whole block)

```
Generate ONE image, 2048x1170, a grid of 7 columns x 4 rows = 28 separate square inventory icons, each about 292x292. Flat pure #FF00FF magenta background around each icon, with a wide margin, nothing touching the neighbours or the image edge. Each icon is ONE object, centred, filling about 75% of its cell, drawn as a classic WoW Classic inventory icon: painterly, rich colour, strong silhouette readable at 40 pixels, soft dark outline, lighting from the top-left, a slight 3/4 view. No frames, no borders, no text, no letters or numbers anywhere, no logos or brand marks, no magenta or pink inside the icons. Each is a small, well-worn personal keepsake from our own world, the kind of thing someone carried for years: scuffs, fading, polish from a hand. Where a description mentions writing, a name, a badge photo or a label, draw it as blank or unreadable marks. Draw only the object, never a person or a hand.

Icons, row by row, left to right:
Row 1: 1 a mechanic's telescoping inspection mirror from a tin-roofed workshop in Santo Domingo; 2 a brass key blank on a wire loop, cut for nothing; 3 a salt-bleached wooden net needle Rui's father carved, for mending nets on the Peniche sardine boats; 4 a brass date stamp with a wooden handle from an old library in Thessaloniki, used to stamp every name in Stelios's register of the dead; 5 Nizar's father's pocket watch, its crystal cracked on the boat from Beirut; 6 a scratched brass pill-counting tray from a pharmacy in Basra, where Yusuf's daughter counted pills doing her homework; 7 a tiny wooden artist's mannequin with a wire in its arm, the last thing Réka animated in Budapest.
Row 2: 8 a dented brass carbide headlamp from the silver mines of Potosí, out of fuel for three years and polished anyway; 9 the nurse's fob watch Graham's husband gave him the year they married, pinned upside down through nineteen years of hospice nights; 10 the small blue cap from the butterfly needle Elie used on his last blood draw in Beirut, clipped to his sleeve for three years; 11 a roll of black fighter's hand-wrap from Bruno's last fight in Curitiba, which he won; 12 a worn leather mate gourd with a silver bombilla, from a history teacher's desk in Rosario; 13 the lens cap from an aurora photographer's camera in Kiruna, worn on a cord after the camera died; 14 the brass whistle from the bridge of a Croatian car ferry, blown every evening at the time the last ferry left Split.
Row 3: 15 a black plastic headset clip from a call-centre desk in Łódź, worn like a medal; 16 the brass nozzle from a fumigation rig in Cairo, the only part of it that survived the landing; 17 the black and steel grip from a tattoo machine in a Medellín shop, cleaned every night for three years; 18 a plastic bottle of lamp oil with the label nearly worn off, carried at the traffic lights in Oaxaca; 19 the heavy brass front-door key of a divers' guesthouse in Aqaba, locked every night in Mohammed's head; 20 a stonemason's steel chisel from the Cologne Cathedral works crew, which carved a little hidden face into every stone Tobias ever set; 21 the worn steel buckle from a biathlon rifle sling her dad bought her when she shot for Scotland.
Row 4: 22 a yellow and black dosimeter badge worn on every tour of the Chernobyl Exclusion Zone; 23 a hospital ID badge on a teal lanyard from a cancer centre in Monterrey; 24 the green seed-company cap Dale wore on the combine outside Minot, on the last pass of the harvest; 25 a faded yellow hazmat hood from the Hanford tank farms, rolled through Wes's belt for three years; 26 a white Sellafield hard hat with a reflective stripe; 27 the little red-lens torch from every night tour in the Atacama, so nobody ruined their night eyes; 28 a grandfather's amber prayer beads from the date palms of the Shatt al-Arab.
```

Sliced by `python3 tools/asset_pipeline/slice_collection_icons.py SHEET.png --cols=7 --ids=col_keepsake_elias,col_keepsake_kiet,col_keepsake_rui,col_keepsake_stelios,col_keepsake_nizar,col_keepsake_yusuf,col_keepsake_reka,col_keepsake_ramiro,col_keepsake_graham,col_keepsake_elie,col_keepsake_bruno,col_keepsake_joaquin,col_keepsake_astrid,col_keepsake_luka,col_keepsake_zofia,col_keepsake_omar,col_keepsake_santiago,col_keepsake_emiliano,col_keepsake_mohammed,col_keepsake_tobias,col_keepsake_isla,col_keepsake_taras,col_keepsake_mariana,col_keepsake_dale,col_keepsake_wes,col_keepsake_neil,col_keepsake_valentina,col_keepsake_faris`.

---------------------------------------------------------------------

## WALK CYCLES: parked

Kyle, 20 Nov 2026: "Walk cycles will come after better sprites. I am thinking just doing about 5 sprites from each race
the player can pick from and then adding walk cycles to these later." So the 41-sheet queue for the old looks is
dropped: the new player sprites get drawn first, and their walk sheets are written against them. The walk-sheet rules
from the pilots still hold (`claude/walk_cycle_prompts.md`): empty hands, three characters a sheet, the left side
drawn rather than mirrored. Done on the old looks: forsaken_1, orc_5, orc_10, tauren_6.
