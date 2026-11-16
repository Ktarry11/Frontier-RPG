# The auction house: design and market math

Kyle, 15 Nov 2026: "an auction house, wow style. But where NPCs put stuff in there... crafting materials, gear,
food, buffs, etc....everything. Various prices. I want players to be able to sell stuff too... putting trash up
for 9999g wont EVER sell... it can be comprehensive and look like the WoW one... MAILBOX and MAIL SERVICE."

Then, while it was being planned:

- "the market can go up and down but it never goes to infinity and never crashes to nothing"
- "epics have a larger sell price while blues and greens are closer to sales... they can be above or below vendor
  price... crafting materials will be huge. not every player has all professions"
- "I want this to FEEL like actual online wow... like you're playing against other fuckers trying to undercut you
  or outbid you (SOMETIMES - NOT ALWAYS)"
- "sometimes people fuck up bad and list something for 1 silver instead of 10g and you get SUPER lucky and scoop it"
- "it'd be surreal if you're in the AH and the priest in your party puts up stuff for sale when you get to town
  after a dungeon"
- "we can model based on 30min, on hour, one dungeon completion, on quest completion etc."

His earlier answers: a shared Horde market plus a goblin market with a bigger cut; bids and buyouts with NPCs
outbidding between checks; NPCs list epics now and then (world drops, generated ones, sometimes dungeon loot) at a
wide spread of levels, expensive but not a fortune, some good and some trash; auction houses in the capitals and
the goblin towns, mail in every town with an inn.

This file is the plan. The numbers in it are the numbers in the code (`world/market/`), and
`tools/sim_auction_market.py` runs the model for thousands of simulated days and prints the tables at the bottom,
so a change to any constant shows up as a change in how the market feels.

## 1. The pieces

| Piece | Where | What it is |
| --- | --- | --- |
| Goods | `world/market/goods.py` | One way to pack any item (gear, loot, potion, material) into a listing and back |
| Catalog | `world/market/catalog.py` | Everything NPCs may list, with its fair value, category, level and demand |
| Market | `world/market/market.py` | Listings, the price index, traders, buyers, bids, the clock |
| Mail | `world/mail.py` | Letters with money and items, kept on the party and saved |
| Screens | `ui/screens/auction_screen.py`, `ui/screens/mail_screen.py` | The Classic layout with the modern extras |

There are two markets. **Horde** is one shared pool for Orgrimmar, Undercity and Freewind Post (and any Horde
capital added later): list in one, collect in another. **Steamwheedle** is the goblin pool for Booty Bay,
Ratchet and Steamwheedle Port. It trades with everyone, so it has more buyers for gear and more odd listings, and
it takes three times the cut.

| | Horde | Steamwheedle |
| --- | --- | --- |
| Cut on a sale | 5% | 15% |
| Deposit (of the vendor price, per 12h) | 15% | 25% |
| Buyer traffic | x1.0 | x1.2 gear, x1.0 the rest |
| Fat-finger and odd listings | x1.0 | x1.5 |
| NPC listings kept up | about 1,800 | about 1,200 |

## 2. Time: the market clock

The market has its own clock in **market hours**. Nothing happens in the market between checks; at a check the
clock jumps forward and everything that would have happened in those hours is worked out at once, an hour at a
time. That is how a WoW auction house feels from a single player's side anyway: you come back and things have
happened.

| Event | Market hours |
| --- | --- |
| Playing (overworld, fights, menus) | 1 per 150 s, so 12 per 30 min and a full market day per hour |
| A quest turned in | +1 |
| A dungeon left with its boss down | +6 |
| Resting at an inn (binding the hearth or reviving there) | +8 |

Kyle's 30-minute and hourly checks are the play-time row: every 30 minutes of play is half a market day. A long
jump (a long session with no events) is worked in whole hours up to 72, then in 6-hour steps, so a check is never
slow. Auctions run 12, 24 or 48 market hours, so a 24-hour auction posted before a dungeon run is usually decided
by the time you're back in town.

## 3. What things are worth

Every listable thing has a **fair value** V (copper per unit) when the market is level. Vendor prices are the
anchor because they're the only prices the game already agrees on; the multipliers are Kyle's shape.

**Raw materials** (ore, herbs, cloth, leather, wood, fish, meat, gems, crystals, creature parts) are where the
money is, because nobody has every profession:

    V = sell × D × T
    D = 3.0 + 1.1 × ln(1 + uses)        uses = recipes in the game that ask for it (capped at 40)
    T = 1.0 early, 1.1 mid, 1.2 late, 1.3 endgame

So a herb that ten recipes want is worth about 5.6x its vendor price, and one nobody uses is worth 3x (still
worth listing, never worth much). Vendor-sold reagents (thread, vials, flux) aren't listed by NPCs at all: the
vendor sells them, so nobody would buy them here.

**Made things** (bars, bolts, planks, potions, elixirs, flasks, food, enchant scrolls, runes, cut gems, kits)
are worth what went into them plus the work:

    V = max( Σ V(input) × qty / made × P,   3 × sell )
    P = 1.25 for consumables and scrolls, 1.10 for intermediates (bars, bolts, planks)

Worked recursively, so an enchant scroll knows what its dusts and essences are worth, and a flask knows its
herbs. A potion a vendor also sells is capped at 1.05 × the vendor price, because nobody pays the AH more than
the shop.

**Gear** sits closer to the vendor for greens and blues and far above it for epics:

    V = sell × G × Q
    G = poor 0.6, common 0.9, uncommon 1.5, rare 2.4, epic 9.0
    Q = 0.55 + 0.9 × want      want = share of the 97 specs whose stat template, armour and weapons fit it

So an epic that suits a lot of specs is worth about 13x its vendor price, and a strange one (spirit and block on a
dagger) about 6x: a good epic is a real purchase and a trash one is cheap for a purple. A green that fits many
specs lands around 2x its vendor price, an oddly rolled green below 1x, which is exactly where Kyle wanted it:
above or below the vendor depending on the piece. Crafted gear takes the higher of that and its materials.

At level 50 that puts a good blue chest around 3g and a good epic chest around 25 to 35g; the named world epics
and dungeon epics land between 15g and 120g across levels 30 to 58. Journeyman riding is 50g at 30 and Master is
200g at 40, so an epic is a real decision and never a fortune.

## 4. The price index: up and down, never to infinity, never to nothing

Each item key has a **price index** I (1.0 means level). The going price is V × I. Every market hour:

    ln I ← ln I × (1 − θ) + ε + shocks
    θ = 0.035         (the pull back toward level: half the gap gone in about 20 market hours)
    ε ~ Normal(0, s)  s = 0.025 materials and consumables, 0.035 gear
    I is clamped to [0.35, 3.0] after every step

The clamp is the hard guarantee: nothing is ever worth more than 3x its fair value or less than 0.35x, no matter
what anyone does. The pull back toward 1.0 is the soft one: a spike or a crash wears off over a day or two by
itself.

Shocks move it:

- **You list a lot.** Each unit you post knocks ln I down by 0.22 / depth, where depth is the number of units the
  market normally trades in a day (demand × 24 × average stack). Dumping two days' supply of copper ore drops the
  price about a third, and it recovers once your ore is gone.
- **You buy a lot.** Each unit bought pushes ln I up by 0.12 / depth.
- **Market news.** About once every 40 market hours per market, something happens to a family of goods: "The
  spiders of Silverpine have gone to ground, and silk is getting scarce" lifts silk cloth and spider silk 40 to
  90%; "A caravan of copper got through from Ratchet" drops copper 20 to 40%. The auctioneer mentions the latest
  news at the top of the window. News only ever names open-world places.

## 5. The traders (the other players)

Every NPC listing has a seller, and every seller is a **trader** with a habit. The roster per market is built
from the world's real NPCs (vendors, townsfolk, guards, quest givers who aren't in a hidden zone) and the
recruits you haven't recruited, about 140 names in each market, each given one habit:

| Habit | Share | What they do |
| --- | --- | --- |
| Farmer | 30% | Lists raw materials in stacks at 0.9 to 1.15 × going price |
| Crafter | 20% | Lists made things and crafted gear at materials + 10 to 30% |
| Undercutter | 12% | Watches what you list and goes under it, sometimes |
| Flipper | 8% | Buys anything listed under 0.65 × going price and relists it near 1.0 |
| Casual | 18% | Lists drops at whatever they feel like: often fine, sometimes silly, now and then a fat finger |
| Collector | 6% | Bids on epics and rares, sometimes chases a bid |
| Bargain hunter | 6% | Bids low on everything and wins the auctions nobody else wanted |

The asking price of an NPC listing is going price × a habit factor × e^(0.12 Z) (Z standard normal), with the
bid set to 70 to 90% of the buyout. Some casual listings have no buyout at all (bid only, like Classic).

**Your own recruits** are traders too. When you leave a dungeon with its boss down, each recruit in the party has
a 15% chance to put one to three things up for sale in the Horde market: materials and drops of the dungeon's
level, priced like a casual. They're in the Seller column under their own name, and hovering the name says
they're in your party. If you buy from them, the coin goes to them (it's their loot).

## 6. Buyers: why fair prices sell and greed never does

For each item key the market has a **demand rate** λ, the number of buyers who come looking per market hour.

| Kind | λ per hour |
| --- | --- |
| Raw material | 0.25 to 1.2 (more for common tiers and for materials more recipes want) |
| Made consumable or scroll | 0.25 to 0.8 |
| A particular piece of gear | 0.025 × Q (greens and blues), 0.02 × Q (epics), × 1.2 at Steamwheedle |

Each buyer has a **reservation price**: the most they'll pay per unit.

    R = V × I × e^(σ Z)          Z standard normal
    σ = 0.22 materials and consumables, 0.35 gear, 0.45 epics
    R is never more than 2.5 × V × I

A buyer looks at the auctions for that key **cheapest per unit first** and buys out the first one at or under R.
That one rule makes the whole thing behave like WoW:

- **Undercutting matters.** If somebody is a copper under you, the next buyer takes theirs, not yours.
- **Fair prices sell.** A material at the going price (ratio 1.0) has an even chance of being under any buyer's
  limit, so with 0.6 buyers an hour it's usually gone in two to four hours if it's the cheapest.
- **Greedy prices don't.** At 1.5 × the going price, a material buyer goes that high about 3% of the time; at 2x
  never in practice (0.08%); at 2.5x and up never at all, by the cap. Grey junk at 9999g has a buyer at no
  price, ever.
- **Gear is slow.** A fair green has about a one in three chance of selling in 24 hours; drop it to 70% of the
  going price and it's about one in two. An epic at its going price has about a 30% chance in 24 hours, and
  better at 48.

## 7. Bids

Every auction has a starting bid, an optional buyout, the current bid and who holds it. The next bid has to be at
least the current bid plus 5% (at least 1 copper). Your bid leaves your purse when you place it.

NPC bidders come for an auction with a buyout over their limit, or no buyout at all, at half the key's demand rate.
A bidder whose limit R covers the next bid puts in the next bid (70% of the time) or jumps to 85% of R (30%).
Collectors and bargain hunters come for epics and for bid-only auctions; nobody bids over their own limit, so a
bid war always stops.

**When you're outbid**, your coin comes back to you by mail ("Outbid on Thick Spider's Silk") and you can bid
again. How often that happens is the "sometimes, not always" Kyle asked for:

| Your bid as a share of the going price | Chance you get outbid on a 24h auction (fair-valued green) |
| --- | --- |
| 60% | about 55% |
| 80% | about 35% |
| 100% | about 15% |
| 120% | about 4% |

When an auction ends with a bid, the high bidder wins it. If that's you, the item comes by mail ("Auction won").

## 8. Undercutters

When you list a stackable thing (materials, consumables, scrolls, gems) or a named item (a named epic, a crafted
piece), each hour there's a chance an undercutter in that market posts the same thing under you:

    chance per hour = u × (1 + 2 e^(−t/3)) × want_k     t = hours since you listed
    u = 0.012
    want_k = 0.5 to 1.5 by how much that key trades

They only do it if your price per unit is at least 0.85 × the going price (under that they'd lose money), and they
go under by one copper (40%), to a round number below (30%), or by 2 to 8% (30%). Their stack is about the size of
yours. Over a 24-hour auction of a fairly priced material that's roughly a one in three chance of being
undercut, most of it in the first few hours, which is when real undercutters pounce. Undercutters also undercut
each other a little, so the bottom of a busy material's list is always moving.

Procedurally rolled gear can't be undercut by the same item (every roll is unique), but similar pieces are listed
by casuals all the time, and buyers for that slot and level pick the cheapest one that suits them.

## 9. Snipers and fat fingers

**Fat fingers.** About one NPC listing in 600 (x1.5 at Steamwheedle) is a mistake: the decimal is in the wrong
place, so it's listed at a tenth (60% of mistakes), a hundredth (35%) or a thousandth (5%) of what it should be.
They show up most often on gear and stacks of good materials, because those are the listings with enough digits
to fumble.

**Snipers.** Flippers buy anything under 0.65 × the going price at 0.25 per hour (0.5 for a fat finger). So a
fat finger usually lives about two market hours: you'll see one if you check the AH often, and you'll catch it
if you're quick. The same flippers buy your mistakes, so listing a stack of Mageroyal at 1 silver instead of
1 gold sells it almost at once, to somebody very happy.

Flippers relist what they bought at about the going price, so a snipe shows up again later at a fair price.

## 10. Your auctions

| Rule | Value |
| --- | --- |
| Durations | 12, 24 or 48 market hours |
| Deposit | 15% (Horde) or 25% (Steamwheedle) of the vendor sell price × quantity, per 12 hours; at least 1 copper |
| Deposit back | On a sale (with the money); kept if it expires or you cancel |
| Cut | 5% or 15% of the final price |
| Cancel | Deposit kept; the item comes back by mail; a cancelled auction with a bid pays the bidder back and costs you the cut on the bid |
| Expired | The item comes back by mail |
| Sold | The money (price − cut + deposit) comes by mail |
| Things you can't list | Quest items, set tokens, soulbound-to-quest things, anything a hidden place gave you |

The sell panel shows the going price, the lowest listing per unit and the other listings of the same thing, like
the modern auction house, and suggests a price a copper under the lowest (the WoW habit) with a buyout to match.

## 11. Mail

Letters live on the party (saved with the purse and the bank). A letter has a sender, a subject, a body, money,
up to 12 items, the market hour it arrived, and a kind (auction won, sold, outbid, expired, cancelled, letter,
returned). The auction house's letters arrive at once; letters you send arrive in an hour.

- **Inbox**: seven letters to a page, newest first, with the right icon for each kind; an unread letter is bright.
  Opening one shows the body, the money with Take, the items in a grid you click to take, Take All, Delete, and
  Return for a letter a person sent.
- **Send**: to anyone you've recruited, in the party or on the bench, with a subject, a short note, money and up
  to 12 items. 30 copper postage per item, 30 for a letter with none. The item goes into their bags when they next
  join the party (or straight in if they're in it). It's how you hand gear to a benched recruit without swapping
  them in.
- Letters with money or items never expire. Plain letters keep 30 market days.
- A raised red flag on the HUD means unread mail.

Mailboxes stand outside every inn (28 towns), drawn in their town's culture: orc, Forsaken, tauren or goblin.

## 12. The screen

Classic's three tabs over Kyle's two painted halls (Horde, goblin), plus the modern extras:

- **Browse**: name search (with exact match), level range, rarity dropdown (any, poor and up), usable items
  (your class and level), favourites, Search and Reset; a category tree on the left with subcategories; result
  columns Rarity/Name, Level, Time Left (hourglass, Short/Medium/Long/Very Long), Seller, Current Bid, Buyout,
  each sortable both ways; a per-unit or per-stack toggle; Prev/Next with page x of y; a bid box in gold, silver
  and copper; Bid, Buyout, Close; your money at the bottom left; the item's tooltip on hover; the seller's
  tooltip on the name.
- **Bids**: every auction you've bid on, with whether you're winning or outbid, and Bid/Buyout from there.
- **Auctions**: the sell panel (pick from your bags, stack size, starting bid, buyout, duration, deposit, going
  price and the competition), and your own auctions with their bids and Cancel.

Time Left: Short is under 2 hours, Medium 2 to 8, Long 8 to 24, Very Long over 24.

## 13. What can't be broken

QA (`tools/qa_auction_house.py`) tries to break it:

1. Every price index stays inside [0.35, 3.0] through a simulated year of hostile play (dumping, buying out, news).
2. Nothing listed at 2.5 × its going price or more ever sells in a simulated year.
3. Buying every NPC listing and selling it to a vendor loses money on average (fat fingers aside).
4. Listing, cancelling and relisting never makes money (the deposit is lost each time).
5. No hidden-zone item, hidden-zone NPC or hidden-zone place appears anywhere in the market or the news.
6. Money in equals money out: coin a bid takes is always either returned by mail or paid for the item.
7. Every item that goes in comes back out exactly once (sold, won, returned or cancelled), never twice.
8. Saving and loading in the middle of everything keeps every auction, bid and letter.
