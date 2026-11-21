# Heroic stage 2: art prompt (sheet HB1)

Kyle, 21 Nov 2026: "Yeah build stage 2", "the badge vendor can have multiple tabs. We can organize it by armor slot and
type and weapon slot", "Ensure the vendor is well organized and sleek and sexy", "Do you need art?", then "Try to fill
it up so it's not a wasted sheet".

One 6 x 6 sheet: the Frontier Mark (the heroic currency; Kyle: "Don't call them badge of honor. We are Frontier
RPG"), the heroic emblem for the dungeon door, the Frontier Quartermaster's eight tab icons, and
icons of their own for the heroic-only items of the 26 highest dungeons (the ten lowest use stock icons).

**References to attach:** `assets/icons/gear/gear_wow_head_117.png` and `assets/icons/gear/gear_inv_sword_40.png`.

```
Generate ONE image, 2048x2048, a grid of 6 columns x 6 rows = 36 separate square game icons, flat pure #FF00FF magenta background between them, each icon fully inside its own cell with a wide margin, no text, no letters, no numbers, no grid lines. WoW Classic inventory-icon style matching the attached icons: painterly, semi-realistic, each icon a square filling about 80% of its cell, rich colour, crisp edges, lighting from the top-left, a thin dark bevelled border on every square.

Row 1: 1 FRONTIER MARK, the most important icon on the sheet: a heavy round medallion of bronze and gold, a raised compass rose on its face with a mountain peak at its centre, a small sky-blue crystal set at the top, a short deep-blue ribbon, worn and glinting; 2 HEROIC EMBLEM: a gold-crowned skull on a deep crimson field with flames behind it; 3 CLOTH: a folded robe of violet silk with gold trim; 4 LEATHER: a tooled brown leather jerkin with buckles; 5 MAIL: a draped shirt of bright chain mail; 6 PLATE: a polished steel breastplate with gold trim.
Row 2: 7 JEWELRY: a gold ring, a pendant with a blue gem and a folded blue cloak together on dark velvet; 8 MAIN HAND: a longsword, point up; 9 OFF HAND: a round shield with a crystal boss; 10 RANGED: a recurve bow with an arrow nocked; 11 a crown-like helm of white and gold plate ringed with floating sky-blue crystal shards; 12 a teardrop pendant of pale moonlit sea-glass on a silver chain, water inside it.
Row 3: 13 black plate sabatons with silver spurs and a faint deathly green glow; 14 a long crimson-and-white crusader's cloak with a gold flame emblem; 15 a black leather-bound register with a silver clasp and a skull on the cover; 16 a shield-shaped amulet of green glass crackling with a sickly glow; 17 a gold halo-crested plate helm, cracked, with dark red light leaking from the crack; 18 a bronze ring set with a blazing orange-and-blue engine crystal.
Row 4: 19 a curved pruning knife of black wood and fungus-grown steel, glowing spores on the blade; 20 mail gauntlets of dark iron with molten orange cracks; 21 leather wristguards glazed with golden royal jelly and insect chitin; 22 a huge stone-headed two-handed maul bound in black iron, runes faintly lit; 23 a gnarled staff of twisted dark wood with a burning green fel crystal at its head; 24 a silver ring with three thin bands that seem to hum, a pale violet gem.
Row 5: 25 a small gold miner's pick-axe with a gem-studded head; 26 a flintlock pistol of brass and dark wood with a skull on the grip; 27 a white-and-gold book of hours with a red ribbon, faint holy light; 28 a deep-blue cloth cowl stitched with tiny glowing script; 29 a heavy plate belt with a bull-horned buckle, battered and proud; 30 a two-handed battle axe with a red-lacquered blade.
Row 6: 31 a purple-and-gold robe with scorched hem and arcane sigils; 32 a fine longbow of pale wood carved with falcons; 33 a ragged green-black cloth sash with plague-blotched trim; 34 a mail hauberk woven with thorny brambles; 35 cloth shoulders stained dark red with a blood-red crystal at each point; 36 leather boots of black hide with nightmarish purple stitching.

Keep every icon fully separated in its own cell on flat magenta. Before you finish, check there are 36 separate square icons.
```

Slices (left to right, top to bottom): the mark to `assets/gathering_nodes/reagents/frontier_mark.png` (32 px),
the emblem and the tabs to `assets/icons/ui/` (`heroic_emblem`, `vendor_tab_cloth`, `_leather`, `_mail`, `_plate`,
`_jewelry`, `_main_hand`, `_off_hand`, `_ranged`), and the 26 item icons to `assets/icons/gear/hb_<item>.png` for, in
order: the Exarch, the Echo of the Queen, Baron Rivendare, Grand Crusader Victor Hale, Darkmaster Gandling, the
Wound's Heart, Grand Crusader Dathrohan, the Warheart, Xavras, the Caldera, Hive-Mother Ahn'thera, Thane Morrun,
Zar'gothrax, Resonance, Pitboss Grebble Vask, Bosun Grell Tarpot, Whitemane, the Index, Vek'tar, Herod, Arcanist Doan,
Lord Falconcrest, Zul'keth, Charlga Razorflank, Bloodmage Thalnos and Lord Nightmare (`tools/build_heroic_rewards.py`).
