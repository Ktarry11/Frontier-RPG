# Secrets: the standing rules

The rules every secret, hidden seller, hidden zone and Easter egg follows. Builders: `tools/build_secrets.py`,
`tools/build_secrets_pass3.py`, `tools/build_new_zone_secrets.py`, `tools/build_secret_rotation.py`,
`tools/build_easter_eggs.py`. The engine: `world/secrets.py`, `world/hidden_zones.py`.

## Hidden means hidden
- **Truly hidden.** The way in looks like the rock, trees or wall it's cut from (world/secrets.py). Nothing on the map
  or in a quest points at one, and nothing in an NPC's lines does either, except the odd rumour (below).
- **Placed blind and never told.** Kyle is never told where a secret, a hidden seller, a hidden door or a hidden zone is:
  counts and names only. Builders print counts. No hints in docs or code comments.
- **Nothing in the way.** No secret touches a portal, an NPC, a road or another secret.
- **Never into a void.** On a map over a drop (the World Tree's tiers), a hidden place is cut into the tree itself, never
  hung over the drop (`OVER_THE_DROP` in tools/build_new_zone_secrets.py).
- **Check the registry** (`world.hidden_zones.registry()`) before naming any place.

## Kyle sees the shapes, never the places (20 Nov 2026)
Kyle: "I still want to see the structure of skull and frontier zones. Just not where they are. Prevents you from making
everything blobs."
- **Show the structure:** every new skull or frontier map goes in front of Kyle as its shape, on a sheet beside every
  hidden map that already exists. Names and shapes only, never the parent, the door or anything that points at either.
- **No two the same topology.** Check the sheet before anything ships. The tree's first cut copied two existing shapes
  (a ring round a lake; pods on necks) and was redrawn.

## Rumours (22 Nov 2026)
Kyle: "Let's put hidden zones hints inside NPC text sometimes like 'A friend of mine talked about a hidden x around/
direction of y.....but he likes to make up stories' and give super vague hints once in a while", "Not often, but a small
amount", "They can be subtle and not obvious."
- **A few, and secondhand.** Now and then a townsperson repeats something a cousin, a grandmother or a drinking friend
  swears is out there, and undercuts it in the same breath. Never more than one in a town, and only in a handful of towns.
- **Super vague.** A region and a quality at most ("somewhere off the western edge of the plains", "weeping pines"),
  never a landmark you could walk straight to, a coordinate, or the hidden zone's name.
- **Never told.** Kyle isn't told which townsfolk carry one or which places they point at, here or anywhere.
- **Never for** Azshara's hidden content, Hearthglen's chain, the ???? seller, or the unnamed faction.

## The secrets counter (22 Nov 2026)
Kyle, for a friend who asked: "Say there are 3 chests and 1 zone. It would show 0/4. But in the skull zone it won't show
anything. Caves and Dungeons won't either." The map (M) shows "Secrets found/total" bottom right for the zone you're in:
its hidden caches, hidden sellers and ways into hidden zones, one each, found once you've stood on their secret ground.
Open-world maps and towns only, never a cave, a dungeon or a hidden zone (`Secrets.counts_secrets`, `zone_progress`).
A counter is a count, so it obeys "counts and names only".

## Hidden sellers
- Rare pieces, no flavour text (flavour is for epics and up), at three quarters of the old price, from a pool of seven
  with four on the shelf at a time, turning over every twelve market hours (Kyle, 17 Nov 2026).
- Exploration is rewarded: people stand behind buildings on purpose (Kyle, 14 Nov 2026).

## Easter eggs (Kyle, 20 Nov 2026)
Kyle: "Add new rules for secrets. We can have memes and Easter eggs", "have references like that. Games, movies, earth
stuff", "But hidden and subtle..."
- **Memes and nods to games, movies and Earth are welcome, inside secrets only.** You find them by exploring, the way
  you find every secret.
- **Hidden and subtle.** A nod never announces itself: no titles, no winks at the camera, nothing that names where it's
  from. A name, a habit, an object, a turn of phrase that someone who knows catches and everyone else reads as just a
  character.
- **Our own words.** Lines are written fresh in the spirit of the thing, never quoted from it.
- **The world's rules still hold.** No Earth objects built into the world (the Ferris wheel in Deadwind stays the only
  one) unless Kyle says so; nothing hints at what the Integration was or who caused it.
- **Placed blind like any secret**, in one with no seller and no door yet, outside the hidden zones.

The eggs so far: Tiny Tina, a goblin sapper with a brick she's very fond of (`tools/build_easter_eggs.py`).
