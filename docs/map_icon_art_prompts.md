# Map icons: art prompt (sheet MI1, 24 icons)

Kyle, 22 Nov 2026: "Let's just get an art prompt for all the map icons bro." Every glyph on the zone map
(`ui/screens/map_screen.py`) is drawn in code right now, out of circles and lines. They work at 16 pixels, but they
look like placeholders. This sheet replaces all of them with painted medallions in one shared style. It covers the
twelve service glyphs, the four gathering dots, the map's points of interest and the player marker, plus three new
ones the map doesn't have yet (bank, dungeon door, faction leader).

The Frontier Mark already has real art (`assets/icons/ui/frontier_mark.png`), so it isn't on the sheet. It keeps its
gold ring, and the new medallions are drawn to sit beside it.

| Sheet | Image | Grid (cell) | Key |
|---|---|---|---|
| MI1 | 1536x1024 | 6 x 4 (256 x 256) | magenta |

**What matters most:** every icon is drawn at 16 to 24 pixels on the map, so each one needs a bold silhouette you can
read at thumbnail size, a strong rim and one main colour. The colours below match the glyphs the game draws now, so
the legend and the player's memory carry over.

---------------------------------------------------------------------
## SHEET MI1: MAP ICONS, 24 (paste this whole block)

```
Generate ONE icon sheet image, 1536x1024, a grid of 6 columns x 4 rows = 24 separate map icons (each cell 256x256). Flat pure #FF00FF magenta background everywhere. Each icon is centred in its own cell with a wide margin and does NOT touch or overlap its neighbours or the image edge. No text, no letters, no numbers, no labels, no grid lines.

STYLE: every icon is a round medallion, a fantasy RPG map marker in the World of Warcraft Classic style. A dark charcoal disc, a thick metal rim in the icon's own colour with a thin dark outline outside it, and one bold, simple symbol in the middle in that same colour with a light highlight. Painted, slightly bevelled, lit from the top-left, crisp clean edges. The symbol must read clearly when the whole medallion is shrunk to 16 pixels: big shapes, few details, high contrast against the dark disc. All 24 medallions are the same size and the same construction, so they look like one set. No magenta or pink anywhere in the icons themselves.

The 24, in order, row by row:
Row 1:
1. SHOP: a single gold coin with a square hole in its middle. Rim and coin in warm yellow gold.
2. REPUTATION QUARTERMASTER: a merchant's balance scale, two pans hanging from a beam on a post, with a small pennant flying from the top of the post. Rim and symbol in bright lime green, with a thin gold outer ring to set it apart from the plain shop.
3. FLIGHT MASTER: a pair of spread wings, like a wyvern's or a bat's, seen from the front. Rim and symbol in emerald green.
4. INNKEEPER: a little timber house with a peaked roof and a lit doorway. Rim and symbol in warm amber.
5. HEARTH BOUND HERE: a five-pointed star glowing over a small hearthstone. Rim and symbol in bright gold, the star brighter than everything else on the sheet.
6. RIDING TRAINER AND MOUNTS: a horseshoe, open end up. Rim and symbol in tan leather brown.
Row 2:
7. CLASS TRAINER: a sword and a staff crossed behind a small shield. Rim and symbol in violet.
8. PROFESSION TRAINER: a smith's hammer crossed with a pair of tongs. Rim and symbol in teal.
9. FORGE: an anvil with a tongue of flame rising behind it. Rim and symbol in hot orange.
10. SAWMILL: a round saw blade with teeth, a log under it. Rim and symbol in pale wood tan.
11. MAILBOX: a sealed envelope with a wax seal. Rim and symbol in pale silver white.
12. AUCTION HOUSE: an auctioneer's gavel striking its block. Rim and symbol in rose.
Row 3:
13. ORE VEIN: a chunk of rock with a vein of metal ore running through it. Rim and symbol in copper.
14. HERB: a single leafy plant with a small flower. Rim and symbol in leaf green.
15. TREE FOR WOODCUTTING: a felling axe stuck in the top of a cut log. Rim and symbol in bark brown.
16. FISHING POOL: a fish leaping over a ring of ripples. Rim and symbol in sea blue.
17. PORTAL OR CAVE ENTRANCE: a dark stone archway with swirling light inside it. Rim and symbol in purple.
18. BOAT CROSSING: a small sailing ship on a wave. Rim and symbol in deep blue.
Row 4:
19. TREASURE: a small wooden chest with gold spilling from its open lid. Rim and symbol in orange gold.
20. POINT OF INTEREST: an exclamation mark inside a diamond. Rim and symbol in pale cyan.
21. YOU ARE HERE (the player): an arrowhead pointing straight up, bold and solid. Rim and symbol in bright red, the arrow edged in white so it stands out from everything else.
22. BANK: a strongbox with a heavy lock and iron bands. Rim and symbol in dull gold and iron grey.
23. DUNGEON ENTRANCE: a skull above a portcullis. Rim and symbol in blood crimson, darker than the player's red.
24. FACTION LEADER: a crown over a raised banner. Rim and symbol in royal purple and gold.

Keep every icon fully separated in its own cell. Before you finish, check that there are 24 different icons, each a round medallion alone in its own cell on flat magenta, and that no two share a colour except where the list above says so.
```

---------------------------------------------------------------------
## After you generate it

It gets sliced to `assets/icons/map/<name>.png` (shop, rep, flight, inn, hearth, ride, class, prof, forge, sawmill, mail,
auction, ore, herb, wood, fish, portal, boat, chest, poi, player, bank, dungeon, leader). Then
`MapScreen._draw_service_icon` draws the painted medallion where it can, with the old procedural glyph kept as the
fallback if a file is missing, the same way the Frontier Mark works today. The legend uses the same drawing code, so it
updates with them. Bank, dungeon door and faction leader get wired onto the map at the same time.
