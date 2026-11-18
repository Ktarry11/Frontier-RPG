# The Collection: account-wide unlocks sold on the auction house

Kyle, 18 Nov 2026: "I want to do kind of like an account-wide heirloom and an AH expansion. So ascension used to have
things like 'book of ascension' or 'Book of professions' etc. These were quality of life things that were saved to an
account. I want to start building up some of these things in my game and have them tied to the player (like the guild
bank is) so it'd be a seperate tab and these items are randomly sold in the AH and have varying prices... and can be
many many many things. Like unique mounts, or callboards that offer daily quests, or feathers that can unlock flight
paths on a continent. Or unlocking unique cosmetic shape-shifting forms etc. This will need a new system tab that's
account-wide."

## Kyle's answers (18 Nov 2026)

| Question | Answer |
|---|---|
| What happens when you use one | **Learn once, every character has it**, old and new. A learned thing can't be resold. |
| Prices | **50g to 750g** (I pushed back on 2000g: a level 55 quest pays about 1.5g, so 2000g was about 1,300 quests). |
| How they show up | **Rare and rotating**: both auction houses list a handful at a time, each for about a market day; the rarest turn up once every few days. Prices wander with the market. |
| Other sources | **The auction house only.** |
| First wave | **Unique mounts, flight feathers, cosmetic forms, and training books** ("can train skills anywhere or train professions anywhere"). |
| Extras | **Heirloom gear, QoL tomes, a portable bank and a portable vendor to sell trash**, all on long cooldowns. |
| Portable cooldowns | **Once per market day** (the auction house's clock, so dungeons and the hearth move it on). |
| Heirlooms | **Scale with the wearer, and give XP: +80% in all.** A two-hander is +20%; a one-hander, shield or off-hand is +10% each. The other 60% is **six armour pieces at +10%**: head, shoulders, chest, legs, cloak and a trinket. |
| Forms | **Map only.** The party leader walks the overworld as the creature; combat and portraits stay normal. |
| Mounts | **Still need riding.** Learned for the account, ridden at the character's own riding speed. |
| Feathers | **Two: Kalimdor and the Eastern Kingdoms.** Islands go with the continent their flights connect to. |
| Later | Callboards and daily quests (a new daily-quest system, the biggest piece) come after the first wave. |

## How it works

**The account file.** The Collection lives beside the guild bank in `data/saves/account_collection.json`, outside
every save slot, so it belongs to the player, not a character. Learning is one transaction, the same way the guild
bank does it: the item leaves the character's bags, the Collection writes its file, and the character is saved in
the same breath. If the save fails, the Collection rolls back, so an item can never be both learned and still in your
bags.

**The items.** Each collectable is a bag item (like a recipe scroll) with a `collection_id`. Right-click it to learn
it. Until it's learned it's an ordinary item: you can mail it, bank it, or put it back on the auction house.

**The tab.** A new **Collection** screen, opened from the game menu, with five tabs: **Mounts**, **Forms**,
**Travel** (the feathers and the hearth tome), **Services** (the portable bank, vendor and trainers) and
**Heirlooms**. Each shows what you have, what you're missing as a silhouette with its name, and what it does.

**The auction house.** A new **Collection** category in both houses. The market keeps a handful of collectables
listed across the two books at all times (about three to six), each listed by a trader for about a market day. When
one ends or sells, another takes its place, picked by rarity: common ones come back often, and the rarest turn up
once every few days. Prices are each item's base price times the market's own price index for it, so they drift up
and down like everything else, and the traders list a little above or below that. NPC collectors buy one now and
then, so something you're watching can vanish.

**The portable services.** Each is used from the Services tab, never in combat, never in a dungeon fight, and then
waits one market day (24 market hours) before it can be used again. The wait belongs to the character, since the
market clock lives in each save.

**Heirlooms.** Learning one adds it to the Heirlooms tab, and any character can take a copy from there (one copy of
each at a time). A copy is bound to the account, can't be sold or auctioned, and is blue quality at the wearer's
level: it fits itself to the character when it's taken (the right armour type and the stats their spec wants, the
right weapon type for their class) and re-fits itself every time they level. The XP bonus adds up across the pieces
they're wearing, to +80% at most, and stops at level 60 because there's nothing left to earn.

## The first wave (40 collectables)

Prices are the base, before the market moves them. Rarity is how often they turn up.

### Mounts (6, need riding; new art)

| Mount | Price | Rarity | What it is |
|---|---|---|---|
| Bone-White Kodo | 300g | uncommon | An elder's kodo from Thunder Bluff, pale as chalk and older than most towns. |
| Steamwheedle Runabout | 350g | uncommon | A goblin's brass strider with a leaky boiler and no brakes worth the name. |
| Tidecaller Sea Turtle | 450g | rare | A great turtle from the Tempest Isle shallows, slow to look at and quick under you. |
| Dread Elk of Felwood | 500g | rare | A black elk with green fire in its antlers, from the edge of the corrupted woods. |
| Sunreach Hawkstrider | 600g | epic | A tall gold and white strider bred by the Sunreach Conclave. |
| Ashen Nightmare | 750g | epic | A black horse with an ember mane, ridden out of the Plaguelands' worst night. |

### Forms (6, map only; new art)

| Form | Price | Rarity | |
|---|---|---|---|
| Murloc | 150g | common | Mrglglgl. |
| Kobold Miner | 150g | common | Candle included. You no take it. |
| Treant Sapling | 250g | uncommon | A walking sprig of Ashenvale. |
| Carrion Crow | 300g | uncommon | Hops more than it flies. |
| Wandering Skeleton | 400g | rare | The Forsaken find it in poor taste. |
| Spirit Wolf | 600g | epic | A ghostly wolf that leaves no tracks. |

### Travel (3)

| Item | Price | Rarity | Effect |
|---|---|---|---|
| Windrider Feather of Kalimdor | 400g | rare | Every Kalimdor flight path is open to every character. |
| Windrider Feather of the Eastern Kingdoms | 400g | rare | Every Eastern Kingdoms flight path is open to every character. |
| Tome of the Swift Hearth | 300g | uncommon | The hearthstone's cooldown is halved. |

### Services (5, once per market day each)

| Item | Price | Rarity | Effect |
|---|---|---|---|
| Satchel of the Travelling Bank | 250g | uncommon | Opens your bank anywhere. |
| Peddler's Bell | 150g | common | Calls a pack-mule peddler who buys anything you're carrying (and sells back what you sold him by mistake). |
| Courier's Horn | 150g | common | A courier brings your mail and takes letters out. |
| Book of the Wandering Master | 200g | uncommon | Opens your class trainer anywhere. |
| Book of Professions | 200g | uncommon | Opens a profession trainer anywhere, for any of your professions. |

### Heirlooms (10)

| Heirloom | XP | Price | Rarity |
|---|---|---|---|
| Heirloom Helm | +10% | 150g | common |
| Heirloom Shoulders | +10% | 150g | common |
| Heirloom Chest | +10% | 180g | uncommon |
| Heirloom Legs | +10% | 180g | uncommon |
| Heirloom Cloak | +10% | 120g | common |
| Heirloom Trinket | +10% | 200g | uncommon |
| Heirloom Two-Hander | +20% | 300g | rare |
| Heirloom One-Hander | +10% | 150g | common |
| Heirloom Shield | +10% | 120g | common |
| Heirloom Off-Hand | +10% | 120g | common |

Ten heirlooms cover every class because each one fits itself to its wearer. A cloth caster taking the Shoulders gets
cloth shoulders with spell power; a warrior gets plate with strength. They're named for that when taken (the
Heirloom Shoulders become, say, "Heirloom Spaulders of the Wandering Blade").

Full kit: weapons +20% (a two-hander, or a one-hander with a shield or off-hand), plus the six armour pieces at +60%,
for +80%.

### Ten to round it out (my suggestions: Kyle to veto any)

Ten more so the market has something to say on most days, all of the kinds Kyle named. These are proposals, not
answers:

- **Mounts:** none more until the art is in.
- **Travel:** a **Hearthstone of the Second Home** (300g, rare): a second hearthstone with its own bind and cooldown.
- **Services:** an **Alchemist's Satchel** (200g, uncommon), which opens a reagent vendor anywhere.
- **QoL tomes:**
  - **Tome of the Pack Mule** (350g, rare): an extra bag slot for every character.
  - **Tome of the Deep Vault** (300g, rare): an extra bank tab for every character, free.
  - **Tome of the Quick Study** (250g, uncommon): characters start with Apprentice Riding at 20 for free.
  - **Book of First Steps** (100g, common): new characters start with a bag and 5g.
- **Forms:**
  - **Gnoll Brute** (200g, uncommon)
  - **Little Ooze** (250g, uncommon)
  - **Furbolg Elder** (350g, rare)
  - **Shade of the Drowned Court** (700g, epic)

These four forms need their art in the same sheet as the six above.

## Art (three sheets; prompts in `docs/collection_art_prompts.md`)

1. **Mounts:** 6 mounts in 4 directions each, matching the existing mount sprites.
2. **Forms:** 10 forms in 4 directions each.
3. **Icons:** 40 item icons (each collectable's bag icon), with the Collection tab's own frame and tab art.

Until the art lands, mounts and forms are sold and learned, but they can't be used yet and are marked "art coming".
Everything else works the day it's built.

## Later

- **Callboards and daily quests**: a board in each capital that offers a few daily quests, account-learned so every
  character sees it. This is the next wave, and it needs its own design (what dailies are, what they pay, where the
  boards stand).
- More of everything, as Kyle thinks of it.
