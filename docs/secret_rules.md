# Secrets: the standing rules

The rules every secret, hidden seller, hidden zone and Easter egg follows. Builders: `tools/build_secrets.py`,
`tools/build_secrets_pass3.py`, `tools/build_new_zone_secrets.py`, `tools/build_secret_rotation.py`,
`tools/build_easter_eggs.py`. The engine: `world/secrets.py`, `world/hidden_zones.py`.

## Hidden means hidden
- **Truly hidden.** The way in looks like the rock, trees or wall it's cut from (world/secrets.py). Nothing on the map,
  in a quest or in an NPC's lines points at one.
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
