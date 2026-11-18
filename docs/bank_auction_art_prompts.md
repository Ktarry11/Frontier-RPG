# Bank and auction house art: one sheet, 12 grand buildings in 6 styles

Kyle, 17 Nov 2026: "I think we also need a uniform Auction House and a Uniform bank rather than just slapping
merchanttusk and the auctioneers in the middle of nowhere", then "We need goblin bank and goblin AH as well as horde
bank and horde AH and eventually an alliance AH and alliance bank style... about 12 on a sheet for grand design!", and
"Make them grand and lavish if we are only having 12, so basically for 6 different styles". He picked the six: Orc,
Forsaken, Tauren, Blood elf, Goblin and Human.

**What it's for.** Every bank in the game becomes a MerchantTusk bank and every auction house an auction house you
can spot at a glance, in the style of the town it stands in. MerchantTusk and the auctioneer then stand at the door of
their building in every town that has them (a pass over all of them once this lands; `docs/backlog_nov17_onwards.md`).
- **Orc**: Orgrimmar, and the orc towns and camps.
- **Forsaken**: the Undercity, and the Forsaken towns.
- **Tauren**: Freewind Post, Sun Rock Retreat, and Timbermaw Hold for now (wood and hide sit well among the furbolgs).
- **Blood elf**: Kael's Bastion, and the Sunreach Conclave's island later.
- **Goblin**: Booty Bay, Ratchet, Steamwheedle Port and the other goblin ports.
- **Human**: for the Alliance later.

**Two signs make them read at a glance, whatever the style:**
- **The bank**: a big round gold coin stamped with a curved white tusk, hung over the door. That's MerchantTusk's
  sign: "Dere is only one bank, mon, and dere is only one me."
- **The auction house**: a gold gavel crossed over a pair of balance scales, hung over the door.

| | Bank | Auction house | Bank | Auction house |
|---|---|---|---|---|
| **Row 1** | 1 Orc | 2 Orc | 3 Forsaken | 4 Forsaken |
| **Row 2** | 5 Tauren | 6 Tauren | 7 Blood elf | 8 Blood elf |
| **Row 3** | 9 Goblin | 10 Goblin | 11 Human | 12 Human |

**Style references to attach (at most 3):** `orc_bank.png`, `gob_auction_house.png`, `forsaken_bank.png` (for camera,
outline and level of detail).

---

```
Generate ONE sprite sheet image, 2048x1536, a 4 columns x 3 rows grid = 12 separate building sprites, each cell 512x512. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single building, centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image edge. No ground, no dirt patch, no grass, no cast shadow, no people, no text, no letters, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta or pink anywhere on the buildings themselves.

Match the attached reference buildings EXACTLY in style, camera angle, outline and level of detail: they are from the same set. Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple shapes legible at small size, consistent soft lighting from the top-left.

Camera: isometric three-quarter view elevated about 45 degrees. EVERY building is turned the same way, front face toward the lower-right and one side wall toward the lower-left, so two faces of each building are visible. The front door is on the front face, with its sign hung directly above it. Consistency of angle across all 12 is critical.

Setting: the grand banks and auction houses of a fantasy world's capitals, in six cultural styles. These are the richest buildings in their cities: GRAND AND LAVISH, two or three storeys, wide fronts, gold everywhere, banners, braziers or lanterns at the door, the finest materials their culture builds with. Columns 1 and 3 are banks; columns 2 and 4 are auction houses. Two signs are drawn the same on every one, so a player can spot them in any city:
- THE BANK SIGN, on all six banks: a big round gold coin stamped with a curved white tusk, hung from a heavy bracket over the door.
- THE AUCTION HOUSE SIGN, on all six auction houses: a gold gavel crossed over a pair of gold balance scales, hung from a heavy bracket over the door.
Banks look like strongholds for treasure: thick walls, a huge reinforced vault door, barred windows, gold coin piles and strongboxes glimpsed inside, guard braziers either side of the steps. Auction houses look like grand trading halls: a wide open front or arcade, a raised auction block with a lectern at the front, rich goods (rugs, crates, weapons, gems) displayed under awnings.

Buildings keep their RELATIVE scale: all twelve are large, important buildings of about the same size; none is a small shop. Do not blow some up and shrink others.

Buildings are numbered row by row, left to right, top to bottom:

Row 1: 1 the ORC bank: a fortified strongroom of black stone and dark iron, spiked roof ridges with tusks, red Horde banners, a massive iron vault door with the bank sign above it, fire braziers at the steps; 2 the ORC auction house: a huge timber-and-hide trading hall on a stone base, a wide open front with a raised auction block, red banners and tusks along the roof, the auction sign over the entrance; 3 the FORSAKEN bank: a gothic stone vault house with a steep slate roof, iron spikes, pointed barred windows glowing faint green, purple banners, a heavy iron vault door with the bank sign; 4 the FORSAKEN auction house: a long gothic stone hall with tall pointed arches open to the street, an auction block under an iron canopy, purple banners, green-burning lanterns, the auction sign over the door.

Row 2: 5 the TAUREN bank: a great round longhouse of carved wood and stretched painted hides on a stone footing, totem poles at the door, a heavy carved wooden vault door bound in bronze, the bank sign; 6 the TAUREN auction house: a broad open-sided hide pavilion on carved wooden posts, painted totems, rugs and goods on display, a raised auction block, the auction sign; 7 the BLOOD ELF bank: an elegant white and gold spired building with red roofs, golden filigree, glowing gold arcane crystals floating at the corners, an ornate gold vault door, the bank sign; 8 the BLOOD ELF auction house: a graceful arcade of white marble and red-and-gold silk with slender gold spires, floating orbs of light, a raised auction block, the auction sign.

Row 3: 9 the GOBLIN bank: a tall riveted brass and copper counting house, green-painted wood, pipes and a smoking chimney, a round vault door like a ship's hatch with spinning gears, gold coins spilling from chutes, the bank sign; 10 the GOBLIN auction house: a big brass-and-timber trading hall with a cargo crane over the open front, gauges and pipes, crates swinging from the crane, a raised auction block, the auction sign; 11 the HUMAN bank: a grand pale stone building with white columns, a blue slate roof, gold trim, blue banners with a gold lion's head, a heavy bronze vault door, the bank sign; 12 the HUMAN auction house: a long pale stone hall with an arcaded front, blue slate roof, blue and gold banners, a raised auction block, the auction sign.
```

Re-roll any building whose sign is missing or hard to read. That's the whole point of the sheet: a bank reads as a
bank and an AH as an AH at a glance, in any city.

### Slice order (`tools/slice_building_sheet.py`, a new `bank_auction` set, to `assets/buildings/`)

| row | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| 1 | bank_orc | ah_orc | bank_forsaken | ah_forsaken |
| 2 | bank_tauren | ah_tauren | bank_blood_elf | ah_blood_elf |
| 3 | bank_goblin | ah_goblin | bank_human | ah_human |
