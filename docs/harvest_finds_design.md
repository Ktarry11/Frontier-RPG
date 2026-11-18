# Harvest finds: quests from gathering, and fishing's junk, salvage, mounts and titles (built 18 Nov 2026)

Kyle, 18 Nov 2026: "Junk and salvage from fishing, yes. Lets have it as the occasional green item and maybe something
unique to fishing! Something fun. Also maybe some quest starts! OOOOOOOOH Why don't we have some quests starting FROM
harvesting. Like 'Odd living copper chunk - starts quest' or 'Mutated silverleaf' --- that'd be cool!"

His picks the same day: **about 16 starters, four a trade**; turn-ins **mixed** (trainers, transplants, druids, places);
for fishing, **Collection mounts, Earth junk, fishing-only gear and titles**; **an art sheet, with stand-ins until it
lands**.

| Piece | Where |
|---|---|
| Content (every name and line) | `tools/harvest_finds_content.py` |
| Builder and its audits | `tools/build_harvest_finds.py` (`--write`) |
| Runtime | `world/harvest_finds.py`, called from `ui/screens/overworld_screen._gather_node` and from skinning in `combat/combat_engine.py` |
| Junk and salvage pools | `world/gathering_manager._populate_fishing` |
| Fishing mounts and titles | Collection entries in `tools/build_collection.py`, marked `found_only` |
| Data | `data/gathering/harvest_finds.json`, `data/quests/harvest_finds.json` |
| QA | `tools/qa_harvest_finds.py` |
| Art | `docs/harvest_fishing_art_prompts.md` (sheets H1 and H2) |

## The quest starters

Sixteen, four for each gathering trade, spread across 1-60. A gather of the starter's own material (a skinned beast
of its level, for skinning) by a character in its level band turns it up one time in sixty. It never comes twice
while you hold it, have its quest or have finished it. Each starts a two-quest chain: the find goes to whoever would
know what it is, and they send you on.

| Trade | Find | From | Band | Goes to | Then |
|---|---|---|---|---|---|
| Mining | Ticking Copper Nugget | Copper Ore | 6-18 | Prizzle Boltwrench, Razor Hill | Keeper Ahnmar's shrine, the Barrens |
| Mining | Tin Ore With a Fossil Tooth | Tin Ore | 18-28 | Forge Baine, Camp Taurajo | Bonehunter Rurk, Southern Barrens |
| Mining | Singing Mithril Shard | Mithril Ore | 36-46 | Scholar Innik, the Ring in Arathi | round the Ring Road, listening |
| Mining | Thorium With a Fingerprint | Thorium Ore | 50-60 | Noor Haddad, the Black Strand | Kenji Watanabe's board of names, Ariden's Watch |
| Herbalism | Mutated Silverleaf | Silverleaf, Peacebloom | 5-14 | Apothecary Shazra, Orgrimmar | Apothecary Zurm tastes it |
| Herbalism | Kingsblood That Bleeds | Kingsblood | 24-34 | Nawa Greenmane, Sun Rock | the Venture Cutline's stumps |
| Herbalism | Fadeleaf That Won't Fade | Fadeleaf | 34-44 | Apothecary Vashka, Hammerfall | Dellwyn Voss's jars from the mere |
| Herbalism | Dreamfoil That Dreams | Dreamfoil | 50-60 | Herbwarden Mylla, Nighthaven | Dr. Sandvik counts its breaths |
| Skinning | Hide With a Map Scratched In | beasts 6-16 | 6-16 | Tanner Urzul, Razor Hill | the tusk rock on Kolkar Crag |
| Skinning | Tagged Ear (an Earth wildlife tag) | beasts 20-30 | 20-30 | Huntsman Dell Varrow, Tarren Mill | the herd on the Foothill Pastures |
| Skinning | Scale From Something Bigger | beasts 34-44 | 34-44 | Smith Dorgun, Grom'gol | the wake in the Snapjaw Marsh |
| Skinning | Stitched Hide | beasts 50-60 | 50-60 | Anders Holm, the Bulwark | Apothecary Dorian Vesk |
| Fishing | Message in a Bottle | any pool | 6-18 | Fishmonger Gribble, Ratchet | Snazz's last joke on the Merchant Coast |
| Fishing | Waterlogged Phone | any pool | 20-32 | Tinker Sprocket, Ratchet | Dr. Lindqvist and her jar of rice |
| Fishing | Kelp-Wrapped Journal | any pool | 34-46 | Netsetter Ulua, Stranglethorn | the mate's cove on the Drowned Coast |
| Fishing | Rubber Duck Named Mo | any pool | 50-60 | Ilyssa Moonwater, Nighthaven | Danny Kowalczyk |

No giver gives more than four quests (the builder checks), and nothing changes in the world when they're done.

## Fishing

- **Junk and salvage pools.** About one fishing spot in eight shows a junk pool (crates, barrels, floating rubbish)
  and one in seventeen a salvage pool (a sunken chest, a bottle, bones, an oil slick). They still give their fish.
- **Earth junk:** ten things that washed through with the transplants (car keys, a flip-flop, a garden gnome, a toy
  dinosaur...), vendor junk with a line each. Every catch from a junk pool, and now and then from any pool.
- **Salvage:** every catch from a salvage pool hauls up a salvage find worth real coin. Three hauls in ten have a
  green of your level for your class in them. One in twenty has a piece of **fishing-only gear**: eight greens and
  blues from level 16 to 58 (Barnacled Signet, Net-Woven Cloak, Kelpweave Sash, Tidewalker Boots, Saltcrust Bracers,
  Anchorline Girdle, Drowned Bell Pendant, Captain's Lost Cutlass), on the item curve, each with its own icon.
- **Fishing mounts:** six, one for each kind of water (a brine crab, a river otter, a glimmer frog, a walrus, a lava
  salamander, an abyssal lurker). One catch in two thousand from an ordinary pool of its water brings its reins.
  Found only: no trader lists them. They can be learned before their art lands, and ridden once it does.
- **Titles:** the Master Angler (a thousand fish), the Salvager (fifty salvage hauls), Who Fished Up the Duck (the
  duck), of the Deep (a mount). Found only, earned once each.

The counters (fish, salvage, mounts, the starters you've found) live on the character as `harvest_log` and save with
it.
