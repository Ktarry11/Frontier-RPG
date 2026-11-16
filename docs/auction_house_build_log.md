# Auction house and mail: build log

The plan and every number: `docs/auction_house_design.md`. This is what was built, in order, and why.

## 15 Nov 2026

### Art
- Kyle's two halls filed: `assets/ui/auction/horde_hall.jpg`, `goblin_hall.jpg` (1376x768, scaled to the screen).
- His 24-icon sheet sliced by `tools/slice_auction_icons.py` into `assets/ui/auction/icons/` (coins, gavel, paddle,
  four hourglasses, star, magnifier, six letters, four mailboxes, two flags). The mailboxes reached across the row
  line, so icons are found as whole objects and assigned to the nearest grid slot; the hourglass glass and the lens
  show the key through, so they're de-spilled all over.
- Three more sheets asked for (`docs/market_town_art_prompts.md`): a Forsaken town (the Forsaken had 3 buildings),
  a goblin port town, and market and mail props (real mailboxes to replace the icons by the inns).

### The market (`world/market/`)
- `goods.py`: one way to carry gear, loot, consumables and materials through an auction or a letter (each class's
  own to_dict), give it back into the right pouch, and refuse quest items and set tokens.
- `catalog.py`: everything NPCs may list (3,917 things): open-world materials and consumables, crafted gear from
  open recipes, named world and dungeon epics, open-world boss and rare loot, drop recipes, bags. Nothing a hidden
  place hands out. Fair values per the design; recursive for made things.
  - Kyle mid-build: "crafting materials will be huge" (materials 3x to 7x vendor), then "we dont want AH as just a
    free way to instantly gear up... it'll get EXPENSIVE fast". Gear now prices by fit, steeply, with a low-level
    premium: a wanted green costs about 2 quests' gold at every level, a blue about 6, an epic 30 to 40.
  - Craftable vendor potions are listed under the shop price (Kyle's healing potion example).
- `market.py`: the two books, the clock, the clamped mean-reverting price index, traders, buyers, bids and rival
  bidders, undercutters, snipers, fat fingers, meme listings, recruits listing after a dungeon, cash on delivery,
  meme mail, save rows.
  - Clock: 1 market hour per 150 s of play, +1 a quest, +6 the last boss of a dungeon (once per visit), +8 the
    hearth. Kyle: "the inn isn't cheeseable... +8 when we HEARTH only". Free until the AH or mail is first used.
  - Listings: 2,600 Horde and 1,700 Steamwheedle (raised from 1,800/1,200: "try to have a lot of listings... a lvl
    10 CAN see lvl 60 items"), spread evenly over levels 1 to 60.
  - Each auction remembers its value, demand and spread when listed, so an hour is 30 to 40 ms and a loaded game
    never re-rolls the gear to price it. Saved as compact rows (1.6 MB for a full market).
- `news.py`: 32 rumours that shock a family of goods, open-world places only.
- `meme_mail.py`: 62 letters across nine moments, 2 to 3 sentences each (Kyle: "50 or so mails... go wild").

### Mail (`world/mail.py`)
- Letters with money, up to 12 items, a kind and an icon; COD; return to sender; plain letters keep 30 days,
  letters with money or items never expire, COD offers go back after 3.
- Send to recruits in the party or on the bench, delivered into their bags an hour later (30c postage an item),
  and they sometimes write back.

### Screens
- `ui/screens/auction_screen.py`: Browse (name, exact, level range, rarity, usable, favourites, category tree,
  sortable columns, per-unit toggle, pages, bid box, Bid, Buyout), Bids (winning or outbid), Auctions (bag picker,
  stack size and number of stacks, starting bid, buyout, 12/24/48h, deposit, going price and trend, the other
  listings of the same thing, your auctions, Cancel). Seller tooltips say who they are and where from; a recruit
  in your party shows green.
- `ui/screens/mail_screen.py`: Inbox (7 a page, icons by kind, unread bright, COD tag, days left), the letter
  (body on parchment, money and Take, item grid, Take All, Delete when empty, Return, Pay COD), Send Mail.
- `ui/market_widgets.py`: text boxes, gold/silver/copper box, check boxes, dropdown, coins with Kyle's icons,
  item icons and tooltips.
- Overworld HUD: the raised red flag and "New mail" when there's unread mail.

### The world
- `tools/place_market_npcs.py`: a mailbox on a clear tile in front of every innkeeper (28), drawn in its town's
  culture; four new auctioneers (Grizzik in Orgrimmar, Fazzle in Booty Bay, Snork in Ratchet, Kizzle in
  Steamwheedle Port) beside the bank or inn; "auction" service on them and on the Undercity and Freewind
  auctioneers. Walking up to a mailbox opens the mail; talking to an auctioneer offers Browse Auctions.

### Measured (tools/sim_auction_market.py)
- Herbs at the going price sell within the day and get undercut about a quarter of the time first; at 2x almost
  never; at 2.6x never.
- A green at its going price sells about 38% of the time in 24 hours.
- Rival bidders take your bid 42% / 32% / 15% / 2% of the time at 0.6x / 0.8x / 1.0x / 1.2x of going.
- Fat fingers: about two a market day across both books, living about 2.5 hours.
- A hostile year reaches both ends of the clamp and never leaves it.

### QA (`tools/qa_auction_house.py`): green
Clamp, greed, no farming the NPCs, list/cancel costs the deposit and conserves items, no hidden leaks, coin
conserved through bids, save/load, mail (COD, full bags, delete only when empty, send to a recruit), COD rate,
every inn has a mailbox, every screen tab renders and takes clicks.

### Also found
- `zone.boss_defeated` was read by the dungeon-clear banter but never set anywhere, so "dungeon_clear" banter never
  fired. The last-boss hook now sets it.
- `gear_icons._icons_for_prefixes` re-scanned every gear icon file name on every call; cached per prefix set.

### QA suites adjusted for the auction house and the mail
- `qa_onyxhollow`, `qa_tempest_quests`: the people on a town's map are checked against its builder's list; the
  mailboxes are placed by `tools/place_market_npcs.py`, so those checks skip `is_mailbox`.
- `qa_quest_overhaul`: every mailbox has its own greeting, naming the innkeeper who sorts the letters.
- `qa_cooking`, `qa_enchanting`: stale since earlier passes (creature materials count as a source; formulas on rep
  quartermaster shelves count as shelved; the wand recipe's own inputs are given).
- `qa_kit_abilities_batch4`: Absolute Precision's "always crits" check now forces a hit, so a miss from random
  starter gear can't read as a missing crit.
- Already failing before this work, untouched: `qa_gathering_legality`, `qa_crafted_icons`, `qa_jewelcrafting`,
  `qa_recipe_sources`, `qa_underdark_content` (casting share 69%).
