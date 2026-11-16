# The Forsaken and goblin towns, re-dressed with Kyle's town sheets

Kyle, 16 Nov 2026: "Yeah fix up the towns with new buildings bro (where appropriate)". Earlier, on 15 Nov: "i guess
you can expand out forsaken towns and goblin towns after AH is 100% done" and "feel free to lightly tint goblin
buildings for different towns if needed."

The sprites came from the two building sheets Kyle generated for the auction house work (sliced by
`tools/slice_building_sheet.py`, sets `forsaken_town` and `goblin_town`). Buildings are placed when a zone is built,
so nothing had to be re-baked. Every swap went through the builder's own placement checks, and anything they refused
was moved until it was accepted, so no building silently dropped out.

## How a swap was chosen

A town kept its bespoke pieces where they already said something (Booty Bay's harbour inn and counting house,
Saltwheel's own racing-town set, the Broken Keel in Ratchet, Tarren Mill's human village on the west bank). A swap
went in where a borrowed or generic building stood in for something the new sheet draws properly: an apothecary
drawn as a plain cottage, a bank that was only a vault door, an orc hut in a goblin port. New buildings went only into
open ground that already read as part of the town, never across a road, a quest giver or a mailbox.

## Forsaken towns

**Brill** was done first (pushed earlier): the tavern keeps its old sprite because the new inn is wider and covered
the innkeeper, the tanner and the mailbox.

**The Sepulcher**
- The Hollow Cask is now the Forsaken inn, and the mortician's next door is the small Forsaken house.
- The apothecary on the middle terrace is the Forsaken apothecary, and the bone carver works out of the crafter's house.
- The farm well in the lower court is now the Forsaken well.
- New: the bat handler's roost beside the chapel yard, and a row of lodgings on the lower terrace by the stalls.

**Deathknell**
- The house west of the square is a Forsaken townhouse, and the house south of the chapel is the crafter's house.
- The square's well is the Forsaken well.
- New: a storehouse west of the town hall, a cauldron yard on the west lane, and a small house on the east lane.

**Tarren Mill** keeps the human village on the west bank, which is the point of the place. The Forsaken side of the
river gained the Society's barracks by the north bridge, the bat handler's roost on the east track, and a cauldron
yard by the south watchtower.

**The Undercity**
- The Trade Quarter's inn is the Forsaken inn, and the post office stands beside it, by the inn's mailbox.
- The Bank of Undercity is a real building now instead of a vault door on its own.
- The Auction House is the Forsaken auction house, with Auctioneer Dross out front.
- The Royal Quarter's house is the large Forsaken house, the Magic Quarter has a mage tower and a shadow chapel, the
  War Quarter's barracks is the Forsaken barracks, and the hunter's yard has a stable.

## Goblin ports and the tint

`tools/tint_goblin_buildings.py` writes a lightly tinted copy of the goblin set for each port into
`assets/buildings/tinted/<town>/`. The wash keeps each pixel's brightness and only shifts the colour of the light, so
the drawings read the same:

| Port | Light |
|---|---|
| Booty Bay | the originals; the jungle and the sea already colour it |
| Ratchet | dusty and warm, like the Barrens |
| Steamwheedle Port | bleached toward Tanaris sand |
| Saltwheel | cooled toward salt flat and sea spray |

A builder asks for a tinted sprite with `path_for(town, sprite)`. Run the tool again after changing a tint.

**Booty Bay** keeps its harbour inn, counting house and market row. The back walk's shack is a goblin house and one
market shop is now an alchemy lab. On the outer harbour, the warehouse, the fish market, the dock office, the
shipwright and a small house came from the goblin sheet.

**Ratchet** was the town most in need: its houses were orc huts and generic shacks. They're goblin houses, stacked
houses, a boarding house and a warehouse now, the trading post is a goblin emporium, and Snork has a goblin podium by
the Broken Keel to sell from. Gazlowe's office, the docks warehouse and the harbour tower stay.

**Saltwheel** keeps its own set. On the pit side, two shacks became a racing garage and a salvage yard, kept low so
the mechanics in front of them aren't drawn under a roof.

## Steamwheedle Port, rebuilt

Kyle, 16 Nov 2026: "Can we redesign steamwheedle....it's very ugly and needs water in the east".

**Why it looked so bad.** The old layout put the sea along the north edge in the tile data, but the ground bake never
painted water (its spec had no `tile_water`), so the port drew as one flat slab of sand with buildings standing on it
and no sea anywhere. The quay, the street and the yard were all the same colour, so nothing told you where anything was.

**The new town faces east.**
- The sea runs down the whole east side with a wandering shoreline, a shallow lip and deep water past it.
- Three planked piers run out from the quay, with lamps, bollards, a dock crane, a cargo winch and boats moored off them.
- The quay is grey flagstone along the water: the harbourmaster's tower at the north pier, the fish market, the inn,
  the bank, the dock office, the shipwright, the customs house and a lighthouse at the south end.
- Gadget Row is the one paved street, straight from the desert gate to the middle pier, with a square halfway down
  where the two halves of the town meet. The auction house stands on the square, beside the inn.
- The Upper Yard is beaten orange hardpan inland: the forge, an engineering workshop, the scrapyard, the supply depot,
  a salvage yard, a shredder hangar, the water tower and the old warehouse.
- The goblin buildings use the Tanaris tint.

**What moved with it.**
- The portal is at the west gate now, where the road comes in off the dunes. Both sides of the contract in
  `world/portal_manager.py` changed together.
- Every NPC was given a new spot in `NPC_POSITIONS` and synced into the data with `tools/sync_steamwheedle_npcs.py`.
  The mailbox and Auctioneer Kizzle were re-placed beside the new inn by `tools/place_market_npcs.py`.
- The enchanter's and gem trader's spots changed in their builders too, so a rebuild keeps them where they are.
- The two Steamwheedle explore objectives (the Quay, the Upper Yard) point at the new quay and yard, in both the
  quest data and the quest builders.
- The recruit who waits here has a new spot.
- The port's hidden places were found again for the new ground and rebuilt. Locations not described. Only this
  zone's entries changed; everything else in the secrets data is byte for byte the same.
- `verify()` checks the new shape: the sea is on the east, none of the west half is water, the quay fronts onto the
  sea for most of its length, and both halves of the town have their people.
- `tools/bake_tanaris_places.py` paints the ground from the layout's own constants, so the paint and the walkable
  ground can't drift apart.

## Tools

- `tools/zone_dressed_preview.py` now knows the Undercity, Steamwheedle Port and Saltwheel, and it refuses an unknown
  zone name instead of quietly drawing a default zone.
- A caution for whoever rebuilds secrets next: `tools/build_secrets.py` also rewrites the crafting recipe and
  material files from its own copy, which undoes later passes over them. Those files were restored after this run.
  Rebuild secrets, then put the crafting files back from git unless the run was meant to change them.
- The QA that guards all of this: building overlap, NPCs clear of props, authored pieces appear, prop overlap and
  thinning, NPC tiles, portals, quest hubs, creature reachability, world view clipping and the quest overhaul suite.
