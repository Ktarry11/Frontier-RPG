# Three sheets: Forsaken town, goblin port town, market and mail props

Kyle, 15 Nov 2026: "give me some art prompts you need? Buildings? Mailboxes?", "i can generate THREE full sheets",
"doesnt need to be pure AH".

## Why these three

- **The Forsaken have almost no town.** `assets/buildings/` has 30 orc, 30 tauren and 30 of several other cultures,
  but only 3 Forsaken buildings (`forsaken_house_medium`, `forsaken_house_small`, `forsaken_town_hall`). Brill,
  Tarren Mill, the Sepulcher and the Undercity's surface borrow everyone else's. Sheet 1 is a whole Forsaken town,
  with its auction house, bank and post office.
- **The goblin ports are thin.** Booty Bay, Ratchet and Steamwheedle Port share 14 `bb_`/`sw_` buildings and now
  hold the Steamwheedle auction house. Sheet 2 is a goblin port town, with its auction house, bank and pneumatic
  post office.
- **The mailboxes are icons.** The 32 mailboxes by every inn are drawn with the four mailbox icons from the auction
  sheet, scaled up. Sheet 3 is proper world props: mailboxes per culture plus market and mail dressing for every
  town that has an auctioneer, a bank or an inn.

## Style references (attach 3)

- Sheet 1: `forsaken_town_hall.png`, `forsaken_house_medium.png`, `orc_war_hall.png` (for the camera angle)
- Sheet 2: `bb_counting_house.png`, `sw_workshop.png`, `bb_harbourmaster_tower.png`
- Sheet 3: `orc_auction_hall.png`, `forsaken_town_hall.png`, `bb_counting_house.png` (for scale and palette)

---

## Sheet 1: Forsaken town (30 buildings)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 5 rows grid = 30 separate building sprites (each cell about 341x410). Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. Match the attached reference buildings EXACTLY in style, camera angle, palette, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style, strong readable silhouette, soft dark outline, chunky simple shapes that stay legible at small size, soft lighting from the top-left. No ground, no dirt patch, no grass, no cast shadow, no people, no text, no letters, no signs with writing, no labels, no numbers, no grid lines, no frames or borders. Never use magenta or pink anywhere on the buildings themselves.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Consistency of angle across all 30 is critical.

Setting: a FORSAKEN (undead) town built over the bones of an old human farming village in Tirisfal: steep gothic slate roofs with iron spikes and finials along the ridges, dark timber frames, cold grey stone, crooked chimneys, pointed arched windows glowing a faint sickly green, black iron fittings, tattered purple and black Forsaken banners, bone and skull trim used sparingly, plague barrels, lanterns burning green. Old human houses that have been taken over, patched with black iron and purple cloth, rather than new buildings. Gloomy but cared for, not ruins.

Palette: slate grey, cold blue-grey stone, dark weathered timber, deep purple, black iron, bone white, with small sickly green glows. Muted and desaturated.

Buildings keep their RELATIVE scale: a small house is visibly smaller than the inn, a well far smaller than a house. Do not blow each one up to fill its own cell.

Row by row, left to right.

Row 1 - town services:
1. INN: a big two-storey gothic tavern with a deep covered porch, a crooked stone chimney at each end and a hanging green lantern.
2. BANK: a squat stone vault house with iron-banded doors, barred arched windows and two iron braziers burning green at the steps.
3. AUCTION HOUSE: a long gothic hall with tall arched windows, a raised stone porch with an auction block under an iron canopy, purple banners.
4. POST OFFICE: a narrow two-storey stone house with a wall of small pigeonhole hatches on its side and a bat roost on the roof.
5. APOTHECARY: a crooked timber shop with green-glowing bottles in the windows, pipes venting green vapour and plague barrels at the door.
6. GENERAL STORE: a timber shop with a wide shuttered counter facing the street, crates and sacks out front under a purple awning.

Row 2 - trades and trainers:
7. BLACKSMITH: a stone forge house with an open side, an anvil, a big chimney and black iron gates.
8. TAILOR AND LEATHERWORKER: a narrow shop with bolts of dark cloth and stretched hides on racks outside.
9. MAGE'S TOWER: a slim round stone tower with a pointed slate cap and violet light in the top window.
10. SHADOW CHAPEL: a small gothic chapel turned to the shadow, a broken steeple, purple glass, iron candles.
11. BAT HANDLER'S ROOST: a tall timber and stone tower with an open roost platform and hanging perches.
12. DEATHGUARD BARRACKS: a fortified stone barracks with arrow slits, a spiked iron gate and banners.

Row 3 - homes:
13. LARGE HOUSE: a two-storey timber-framed house with a slate roof, a side wing and a little iron fence.
14. MEDIUM HOUSE: a one-and-a-half storey house with a steep roof, one dormer and a boarded window.
15. SMALL HOUSE: a single-room stone cottage with a crooked chimney and one green-lit window.
16. TALL TOWNHOUSE: a narrow three-storey house with an overhanging upper floor and iron balconies.
17. ROW OF HOUSES: three narrow joined houses under one long slate roofline, each with its own door.
18. CRAFTER'S HOUSE: a house with an open workshop bay, a workbench and coffins being built.

Row 4 - the dead and the town square:
19. MAUSOLEUM: a stone mausoleum with an iron door and a weeping statue on top.
20. CRYPT ENTRANCE: a small stone building over stairs going down, iron gates standing open.
21. TOWN WELL: a stone well under a little slate roof with an iron winch and a bucket (small footprint).
22. PLAGUE CAULDRON YARD: a fenced stone yard with a big bubbling green cauldron and barrels (small).
23. GALLOWS SQUARE: a raised timber platform with a bell tower beside it (no bodies).
24. TOWN HALL B: a second town hall, different from the reference, with a clock tower and purple banners.

Row 5 - work and walls:
25. GRANARY: a tall timber granary on stone stilts with a slate roof and a hoist.
26. STOREHOUSE: a long low stone storehouse with two wide doors and a hoist beam.
27. WINDMILL: an old human windmill with torn sails, patched with purple cloth.
28. WATCH TOWER: a tall square stone tower with a slate cap, narrow windows and a green signal lantern.
29. TOWN GATE: a gothic stone gate arch with spiked iron doors standing open and banners on both posts.
30. STABLE: a long timber stable with skeletal horses' stalls (no horses), hay and harness on the walls.
```

## Sheet 2: goblin port town (30 buildings)

```
Generate ONE sprite sheet image, 2048x2048, a 6 columns x 5 rows grid = 30 separate building sprites (each cell about 341x410). Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. Match the attached reference buildings EXACTLY in style, camera angle, palette, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style, strong readable silhouette, soft dark outline, chunky simple shapes that stay legible at small size, soft lighting from the top-left. No ground, no dirt patch, no grass, no cast shadow, no people, no text, no letters, no signs with writing, no labels, no numbers, no grid lines, no frames or borders. Never use magenta or pink anywhere on the buildings themselves.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. Consistency of angle across all 30 is critical.

Setting: a GOBLIN PORT TOWN of the Steamwheedle Cartel, like Booty Bay and Ratchet: buildings of salvaged ship timber and planks on stilts and pilings, riveted iron and brass plates bolted on, round porthole windows, smokestacks and brass pipes, gears and pressure gauges as trim, canvas awnings, rope, cargo nets, barrels and crates everywhere, little cranes and pulleys. Cheerful, crooked and noisy, built for money.

Palette: warm weathered timber, rusty iron, polished brass and copper, teal-green patina, faded red and yellow canvas, a little sea blue. Not a bright cartoon.

Buildings keep their RELATIVE scale: a small shack is visibly smaller than the auction house, a crane far smaller than a warehouse. Do not blow each one up to fill its own cell.

Row by row, left to right.

Row 1 - Steamwheedle business:
1. AUCTION HOUSE: a big two-storey trading hall on pilings with a wide balcony, a brass bell, a gold coin emblem on the gable (no letters) and a crane hoisting a crate.
2. BANK: a heavy riveted iron vault building with a round vault door on the front, brass trim and a steam pipe.
3. POST OFFICE: a narrow building covered in brass pneumatic tubes running up to the roof, a wall of parcel hatches and a little mail zeppelin mast.
4. GOBLIN INN: a tall crooked three-storey tavern on stilts with balconies, lanterns and a smokestack.
5. MERCHANT'S EMPORIUM: a shop with a wide awning, goods spilling onto the boardwalk and a big brass scale.
6. COUNTING HOUSE B: a squat money house with a clock on the front and a steam-powered adding machine on the roof.

Row 2 - trades:
7. ENGINEERING WORKSHOP: an open-fronted workshop full of gears, a robot arm and sparks from a forge.
8. ALCHEMY LAB: a round building with glass domes, coloured smoke from chimneys and bubbling tanks outside.
9. SHIPWRIGHT'S YARD: a covered slipway with half a ship's hull on blocks inside.
10. TAVERN SHACK: a small grog shop made from an upturned boat hull with a door cut in it.
11. FISH MARKET: an open stall building on pilings with fish hung on hooks and barrels of ice.
12. ZEPPELIN TOWER: a tall riveted iron tower with a docking platform and mooring lines (no zeppelin).

Row 3 - homes and shacks:
13. GOBLIN HOUSE LARGE: a two-storey house of ship timber with a porthole window, a smokestack and a satellite-dish-like gear on the roof.
14. GOBLIN HOUSE MEDIUM: a single-storey house on short stilts with a brass door and a crooked chimney.
15. GOBLIN HOUSE SMALL: a tiny box house of corrugated iron and planks with a round window.
16. STACKED HOUSES: three small houses stacked crookedly on top of each other with ladders between them.
17. HOUSEBOAT: a little house built on a floating raft with barrels for floats.
18. BOARDING HOUSE: a narrow tall house with many small rooms and laundry lines strung across it.

Row 4 - docks and storage:
19. WAREHOUSE B: a long warehouse with big sliding doors and a crane on the roof.
20. CARGO CRANE: a tall timber and iron crane on a stone base with a hook and a crate (small footprint).
21. DOCK OFFICE: a small office on stilts with a big window and a ship's bell.
22. LIGHTHOUSE: a short striped lighthouse with a brass lamp room.
23. CUSTOMS HOUSE: a two-storey building with a balcony, a weighing scale and stacks of crates out front.
24. GOBLIN BARRACKS: a fortified riveted building with a gun turret on the roof (the bruisers' station).

Row 5 - odd goblin things:
25. RACING GARAGE: an open garage with a half-built racing cart inside and tools on the wall.
26. GNOMISH SALVAGE YARD: a fenced yard piled with scrap metal and a shed in the middle.
27. GOBLIN SHREDDER HANGAR: a tall open hangar with a big empty walking machine frame inside.
28. WATER TOWER: a riveted iron water tank on tall stilts with pipes coming down.
29. FIREWORKS SHOP: a small shop with rockets on racks out front and burn marks on the walls.
30. TOWN GATE: a gate arch of riveted iron and timber with two brass lamps and a hanging gong.
```

## Sheet 3: market and mail props (30 props)

```
Generate ONE sprite sheet image, 2048x1536, a 6 columns x 5 rows grid = 30 separate prop sprites (each cell about 341x307). Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single prop, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. Match the attached reference buildings in style, camera angle, palette, outline and level of detail, at PROP scale: these stand next to those buildings in the same towns. Painterly semi-realistic WoW Classic style, strong readable silhouette, soft dark outline, chunky simple shapes that stay legible at small size, soft lighting from the top-left. No ground, no dirt patch, no grass, no cast shadow, no people, no text, no letters, no numbers, no grid lines, no frames or borders. Never use magenta or pink anywhere on the props themselves.

Camera: isometric three-quarter view elevated about 45 degrees, every prop turned the same way (front toward the lower-right), the same as the buildings.

Props keep their RELATIVE scale: a mailbox is about as tall as a person, a crate is knee high, a market stall is the size of a small shed. Do not blow each one up to fill its own cell.

Row by row, left to right.

Row 1 - mailboxes (each a box with a letter slot and a little red flag on the side):
1. ORC MAILBOX: dark wood and spiked iron on a thick wooden post, a red flag, a tusk on top.
2. ORC MAILBOX B: a squat iron-banded wooden chest on a stone base with a slot in the lid and a red flag.
3. TROLL MAILBOX: a carved and painted wooden box on a bamboo post with feathers and beads, a red flag.
4. FORSAKEN MAILBOX: a gothic black iron box with purple trim on a crooked iron post, a red flag.
5. FORSAKEN MAILBOX B: a small stone and iron pillar box with a pointed slate cap and a green lantern.
6. TAUREN MAILBOX: a box of pale carved wood painted with tauren patterns on a small totem post, a red flag.

Row 2 - more mailboxes and mail:
7. TAUREN MAILBOX B: a woven basket box with a hide lid on a carved pole, feathers hanging off it.
8. GOBLIN MAILBOX: a riveted brass box with pipes and a pressure gauge on a metal post, a red flag.
9. GOBLIN PNEUMATIC MAIL TUBE: a brass tube pillar with a hatch, a dial and a canister sticking out.
10. PARCEL CART: a small two-wheeled handcart loaded with wrapped parcels and a sack of letters.
11. MAIL SACKS: a pile of three bulging canvas mail sacks with a few letters spilling out.
12. NOTICE BOARD: a timber board on two posts covered in pinned papers with scribbles (no readable writing).

Row 3 - the auction block:
13. ORC AUCTIONEER'S PODIUM: a raised wooden podium with iron bands, a gavel and a clan banner behind.
14. GOBLIN AUCTIONEER'S PODIUM: a brass and wood podium with a speaking trumpet, a bell and a coin pile.
15. FORSAKEN AUCTION BLOCK: a stone lectern with an iron canopy, a ledger and a green candle.
16. TAUREN TRADING ROCK: a flat painted standing stone used as a counter, with goods laid on a hide.
17. GOODS ON DISPLAY: a long trestle table with weapons, armour, potions and folded cloth laid out.
18. PRICE BOARD: a big chalkboard on legs covered in chalk scribbles and tally marks (no readable writing).

Row 4 - market dressing:
19. CRATE STACK: three stacked wooden crates with stamped shipping marks (no letters).
20. BARREL GROUP: four barrels, one open showing apples, one with fish tails sticking out.
21. ORE AND BARS PILE: a low pile of ore and stacked metal bars on a pallet.
22. CLOTH BOLTS ON A RACK: a wooden rack holding rolled bolts of cloth in several colours.
23. HERB DRYING RACK: a timber rack with bundles of herbs hanging upside down.
24. HIDES ON A FRAME: a frame with two stretched animal hides drying.

Row 5 - money and odds:
25. STRONGBOX: an iron-banded strongbox with a big padlock and a few gold coins on the lid.
26. MERCHANT'S SCALES: a big brass balance scale on a wooden stand with a weight on one pan.
27. GOBLIN COUNTING MACHINE: a brass adding machine on a little table with a paper tape spilling out.
28. COIN CHEST: an open treasure chest overflowing with gold coins and a jewelled goblet.
29. AUCTION GONG: a big round bronze gong hanging in a wooden frame with a striker.
30. SMALL MARKET STALL: a little stall with a striped canvas roof, a counter and goods under it.
```

## Slice order

Sheet 1 files: `forsaken_inn, forsaken_bank, forsaken_auction_house, forsaken_post_office, forsaken_apothecary,
forsaken_general_store, forsaken_blacksmith, forsaken_tailor, forsaken_mage_tower, forsaken_shadow_chapel,
forsaken_bat_roost, forsaken_barracks, forsaken_house_large, forsaken_house_medium_b, forsaken_house_small_b,
forsaken_townhouse, forsaken_house_row, forsaken_crafter_house, forsaken_mausoleum, forsaken_crypt_entrance,
forsaken_well, forsaken_cauldron_yard, forsaken_gallows_square, forsaken_town_hall_b, forsaken_granary,
forsaken_storehouse, forsaken_windmill, forsaken_watch_tower, forsaken_town_gate, forsaken_stable`

Sheet 2 files: `gob_auction_house, gob_bank, gob_post_office, gob_inn, gob_emporium, gob_counting_house_b,
gob_engineering_workshop, gob_alchemy_lab, gob_shipwright, gob_tavern_shack, gob_fish_market, gob_zeppelin_tower,
gob_house_large, gob_house_medium, gob_house_small, gob_stacked_houses, gob_houseboat, gob_boarding_house,
gob_warehouse_b, gob_cargo_crane, gob_dock_office, gob_lighthouse, gob_customs_house, gob_barracks,
gob_racing_garage, gob_salvage_yard, gob_shredder_hangar, gob_water_tower, gob_fireworks_shop, gob_town_gate`

Sheet 3 files (assets/props/market/): `mailbox_orc, mailbox_orc_b, mailbox_troll, mailbox_forsaken,
mailbox_forsaken_b, mailbox_tauren, mailbox_tauren_b, mailbox_goblin, mail_tube_goblin, parcel_cart, mail_sacks,
notice_board, podium_orc, podium_goblin, auction_block_forsaken, trading_rock_tauren, goods_table, price_board,
crate_stack, barrel_group, ore_bar_pile, cloth_rack, herb_rack, hide_frame, strongbox, merchant_scales,
counting_machine, coin_chest, auction_gong, market_stall_small`

The mailboxes replace the icons by every inn as soon as they're sliced (each town gets its own culture's box, and
the B versions alternate). The podiums go under the auctioneers. The rest dress the markets, banks and docks.
