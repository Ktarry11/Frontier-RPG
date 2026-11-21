# Auction house and mail: art prompts

**Status (21 Nov 2026): delivered and sliced (the auction house backgrounds and icons are in the game).** See `docs/art_status.md` for every sheet.

For the auction house and mail update (Kyle, 15 Nov 2026). Three images. The two backgrounds sit behind the
auction house screen the way battle backgrounds sit behind a fight: the window, tabs, lists and buttons are drawn
over them by the game. So they're composed with a calm, darker middle where the window goes, and all the detail
and colour round the edges. The third is a small icon sheet for the parts of the screen that need real art.

## 1. The Horde auction hall (16:9)

Behind the auction house in Orgrimmar, Undercity and Freewind Post (the shared Horde market).

```
Generate ONE wide 16:9 background painting, 1920x1080, no characters in the foreground, no text anywhere. Painterly semi-realistic World of Warcraft Classic style, rich and warm, slightly dark so a game window can sit on top of it.

The scene: the inside of a big Horde trading hall under Orgrimmar, built of red rock, thick timber beams and iron, like the inside of a war-tent made permanent. Warm amber light from hanging iron braziers and goblin lanterns; a cool shaft of daylight falling from a smoke hole in the roof at the top left.

Round the EDGES of the picture, packed with things being sold: on the left, tall wooden shelving and racks crammed with goods (rolled bolts of cloth in different colours, stacked leather hides, crates of ore and gleaming metal bars, bundles of herbs hanging to dry, bottles and potions in rows glowing red, blue and green, a rack of axes, swords and staves, a mannequin wearing a mail hauberk, a shield hung on a beam). On the right, a long auctioneer's counter of dark wood with a brass bell, a set of brass scales, stacks of ledgers and coin piles of gold, silver and copper, an iron strongbox, a goblin's adding machine with a paper roll, hanging tags and tickets on strings, a big tally board on the wall covered in chalk scribbles that are not readable letters. Small far-away silhouettes of orc, tauren, troll, Forsaken and goblin traders browsing in the background, out of focus, none of them close or large.

THE MIDDLE THIRD of the picture is calmer and darker: an open stretch of worn rug and stone floor and a dim back wall in soft shadow, so a game window can cover it without anything important hidden behind. No strong light, no detail and no faces in the middle.

Bottom edge: the corner of a crate of goods and a coin purse in the near foreground, slightly blurred, framing the scene. Warm reds, browns, amber and brass, with small cool blue and green accents from potions and gems. No text, no letters, no numbers, no logos, no UI, no frames.
```

## 2. The goblin auction house (16:9)

Behind the neutral Steamwheedle auction house (Booty Bay, Ratchet, Steamwheedle Port and the other goblin towns),
which trades with everyone and takes a bigger cut.

```
Generate ONE wide 16:9 background painting, 1920x1080, no characters in the foreground, no text anywhere. Painterly semi-realistic World of Warcraft Classic style, warm and slightly dark so a game window can sit on top of it.

The scene: the inside of a goblin auction house in a busy port town, built out of a ship's hull and harbour timber, with brass pipes, gears and riveted iron plates bolted on everywhere. Round porthole windows at the top letting in bright tropical daylight and a glimpse of blue sea; hanging oil lamps and a big brass chandelier made of ship's wheels.

Round the EDGES: on the left, a brass pneumatic tube system with message canisters, a wall of pigeonholes stuffed with parcels and rolled scrolls, cargo nets and barrels stamped with shipping marks (no readable letters), a crane hook with a crate on it. On the right, a raised auctioneer's podium of polished wood and brass with a gavel, a speaking trumpet, piles of gold coins, a steam-powered counting machine with dials and a punched paper tape, a chalkboard of prices in scribbles that are not readable, display cases of glittering gems, rings and a jewelled dagger. Small far-away silhouettes of goblins, trolls and pirates bidding in the background, out of focus, none of them close or large.

THE MIDDLE THIRD is calmer and darker: an open stretch of plank floor with a worn ship's-map rug and a dim back wall in shadow, so a game window can cover it without anything important hidden behind. No strong light, no detail and no faces in the middle.

Bottom edge: a coil of rope and the corner of a treasure chest in the near foreground, slightly blurred. Brass, teal, warm wood and gold, with a little sea blue. No text, no letters, no numbers, no logos, no UI, no frames.
```

## 3. Auction and mail icons (one sheet, 6 x 4 = 24)

```
Generate ONE sprite sheet image, 1536x1024, a 6 columns x 4 rows grid = 24 separate game icons (each cell 256x256). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no numbers, no grid lines, no frames, no borders. No magenta or pink inside any icon. Row by row, left to right:

Row 1 (money and the auction):
1. GOLD COIN: one thick shiny gold coin, slightly tilted
2. SILVER COIN: one thick shiny silver coin, slightly tilted
3. COPPER COIN: one thick copper-brown coin, slightly tilted
4. COIN PILE: a small heap of gold, silver and copper coins
5. AUCTIONEER'S GAVEL: a dark wooden gavel with a brass band
6. BID PADDLE: a round wooden bidding paddle on a short handle, blank face

Row 2 (time left on an auction, one hourglass family):
7. HOURGLASS FULL: a brass hourglass with almost all its sand in the top
8. HOURGLASS HALF: the same hourglass with the sand half run through
9. HOURGLASS LOW: the same hourglass with only a little sand left in the top
10. HOURGLASS EMPTY: the same hourglass with all the sand run through, a faint red glow
11. STAR FAVOURITE: a five-pointed gold star, bright and simple
12. MAGNIFYING GLASS: a brass-rimmed magnifying glass, for the search box

Row 3 (mail):
13. SEALED LETTER: a folded parchment letter with a red wax seal
14. OPEN LETTER: an unfolded parchment letter with lines of scribble that aren't readable letters
15. PARCEL: a small parcel wrapped in brown paper and tied with string
16. COIN LETTER: a folded letter with a small pile of gold coins on top of it
17. RETURNED LETTER: a folded letter with a torn corner and a dark smudged seal, sent back
18. AUCTION LETTER: a folded letter sealed with a gold wax seal stamped with a little gavel shape

Row 4 (mailboxes, one per culture, these are the props as small icons):
19. ORC MAILBOX: a sturdy box of dark wood and spiked iron on a wooden post, with a slot and a little red flag
20. FORSAKEN MAILBOX: a gothic box of black iron with purple trim on a crooked post, with a slot
21. TAUREN MAILBOX: a box of carved pale wood painted with tauren patterns on a totem post, with a slot
22. GOBLIN MAILBOX: a riveted brass box with pipes and a pressure gauge on a metal post, with a slot
23. EMPTY MAILBOX FLAG: the little red mailbox flag on its own, lowered
24. NEW MAIL FLAG: the same little red mailbox flag raised, with a small glow, meaning new mail
```

After you generate them, send the images and I'll file the backgrounds in `assets/backgrounds/` and slice the
icons into `assets/icons/ui/`. The mailboxes in the world (the props you walk up to) will want their own prop sheet
once the screens work. I'll write that prompt when we get there.
