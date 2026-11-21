# Dawnhaven: the blood elves' starting isle

Kyle, 21 Nov 2026: "our bloodelves are currently homeless. I suggest an island off the coast of Azshara. Has a level 1-6
and a level 5-9 zone that eventually has a boat to take you to Durotar from their main city. Quick, easy, new starting
zone." Then: "So let's build the starting zone the blood elf. We can do 2 zones, 2 caves in each zone, then their
capital city, it's not massive though. Not even close to a capital city. Perhaps a bloodelf spire city? But the zones
should be autumn style, very azshara / fall / bloodelf."

## What Kyle chose (21 Nov 2026)

| Question | His answer |
|---|---|
| The island's story | **An old outpost reclaimed**: an ancient high elf outpost from long before the change, taken back by the survivors |
| Whose home | **The Sunreach Conclave's**: Grand Magister Velanthe and her quartermaster move from Talrendis Landing to the city, and the start zones pay Sunreach reputation from level 1 |
| Names | **Dawnhaven** (the island) and **Firstlight Spire** (the city): "something that signifies the potential of a new home" |
| Zones | **Amberleaf Glade** (1-6) and **Duskfall Woods** (5-9), two caves in each |
| Enemies | **Naga on the coast, autumn wildlife, elementals, and the remnants of high elves** (undead: the outpost's own dead) |
| The Integration | **Transplants only**: the player and a few Earth people wake up here; the island itself is old elven ground |
| The boat | **A new pier on Durotar's north-east coast** (Kyle: "Razor hill isn't on the water") |
| The city | Small, a spire city, "not even close to a capital": **inn and flight path, class and trade trainers, bank and mailbox**, no auction house |
| Art | **Existing art now, sheets later**: Azshara's autumn ground, trees and ruins and the be_ blood elf buildings; prompts for what's missing |
| Recruits | **Unused recruits, at least a healer** ("We always want at least a Healer at the start of the game") |
| Caves | **Rafa picks, Kyle reviews**: rooms with loops |

**The bar** (Kyle, 21 Nov 2026): "Even though it's early game, we still wan to make it nice, good quest, good story! A
story of survival, rebirth, and progress."

## What that settles

- **The road:** you wake in Amberleaf Glade (1-6), go on through Duskfall Woods (5-9) to Firstlight Spire, and the
  Spire's boat takes you to Durotar's north-east coast. Character creation suggests Dawnhaven for blood elves and
  leaves every start open, the same as the others.
- **Nobody is born here.** Transplants wake up on the island the way they wake up in the Valley or Deathknell. The
  Conclave took the island back after the Integration took Quel'Thalas's last spires, and it takes in whoever wakes
  up on its shore.
- **The Conclave's seat.** Velanthe and her quartermaster stand in the Spire now. They still give no quests, so either
  can move again.

## What was built (21 Nov 2026)

| Piece | Where |
|---|---|
| Amberleaf Glade (150x130, 1-6) | `tools/handbuilt_dawnhaven_amberleaf.py`, baked to `assets/tiles/dawnhaven/baked_amberleaf` |
| Duskfall Woods (160x140, 5-9) | `tools/handbuilt_dawnhaven_duskfall.py`, baked to `assets/tiles/dawnhaven/baked_duskfall` |
| Firstlight Spire (104x92, the town) | `tools/handbuilt_firstlight_spire.py`, baked by `tools/bake_ashenvale_towns.py firstlight_spire` |
| The four caves | `tools/handbuilt_dawnhaven_caves.py`, baked by `tools/bake_dawnhaven_caves.py` |
| Creatures, rares, cave bosses, loot, gathering, fishing | `tools/build_dawnhaven_content.py` |
| People, services, the flight path, the Conclave's move, the recruits | `tools/build_dawnhaven_people.py` |
| Quests | `tools/dawnhaven_quests.py` (text), `tools/build_dawnhaven_quests.py` (builder and audits) |

**The island.** Amberleaf Glade is the south: the Waking Shore's beach where you wake, Amberwatch (the Conclave's camp
in the old outpost's ruined gatehouse), Leafwhisper Grove's gold woods, Amberleaf Mere, the Fallen Wardstones, Brinecoil
Cove where the naga landed, and the Silent Barrow, the outpost's burial ground. Duskfall Woods is the north, redder and
under a lower sun: Dawnrest (the old waystation with its roof back on), the Red Hollow, Duskmere, the Wildmana Thicket,
Saltspine Shore with the naga's main camp, the Withered Spires (the outpost's inner quarter) and the Lightwell Court.
The Spire road climbs the headland to Firstlight Spire, whose pier sends the boat to Durotar's north-east coast.

**The caves** (Kyle: "Stop making every cave a circle"): Brinecoil Grotto (3-5) is a slanting sea inlet with a ledge
on each bank and two crossings; the Quiet Vault (5-6) is a square-built crypt, a nave and a cloister of four straight
walks round the ossuary; Saltspine Hollow (7-9) is sea terraces stepping down to a throne pool, a ramp down each side;
the Lightwell Deep (8-9) is the outpost's own underworks, square rooms round a long conduit hall, with the font chamber
above.

**The story** (Kyle: "A story of survival, rebirth, and progress"), 35 quests:
- *Survival* (Amberleaf Glade): you wake on the shore and Ranger-Captain Saelis Dawnbrook takes you up to Amberwatch.
  Food (Apothecary Thaelen), shelter (Rosa Quintero, a carpenter from Valparaiso), safety (Goldmane in the grove, Old
  Barnacle on the shore). Magistrix Iriel wakes the first of the broken wardstones with you; Scout Kaelen finds the
  naga were sent to find the hidden island, and you end Tidecaller Sszelith in Brinecoil Grotto; Priestess Aldaria
  gathers the dead's names, and you put Warden Isilien to rest in the Quiet Vault. Saelis sends you north.
- *Rebirth* (Duskfall Woods): Lightwarden Selanne wants the outpost back, and the Lightwell in its heart is dark.
  Huntress Lyra's hunt and the Hollow King; Magister Aeron's spilled magic, which didn't spill but ran from something;
  Scout Nerys finds the naga's way under Saltspine Shore, and you end Sea-Witch Ilthessa; Commander Halion
  Brightspear, still on watch with his dead garrison, gathers the spirit lanterns. Archivist Lorethas went down under
  the well and fed the outpost's dead to the hunger there to keep it quiet; you end him, then the Starved Light, and the
  Lightwell burns. Halion's garrison goes out with the lanterns at dawn, and he goes last.
- *Progress* (Firstlight Spire): the spire lights for the first time in a thousand years, Spire-Keeper Lorien opens a
  room for everyone the sea gives up, and Joost Achterberg (a harbour pilot from Rotterdam) takes you on the first
  crossing to Durotar with the Conclave's letter to Orgrimmar.

**The people.** Velanthe and Sylvaen moved from Talrendis Landing to the Spire's Conclave Hall (no quests, still
movable). The Spire has the inn, the island's one flight path (dragonhawks), MerchantTusk's bank, a mailbox, a class
trainer and four pairs of trade trainers; Amberwatch has a class trainer and the gathering trainers. Recruits: Liam
Hartigan (Sun Cleric healer) on the Waking Shore, and Haruto Nakamura (Runemaster) copying runes at the Withered Spires.

**The townsfolk** (Kyle: "Do we need additional blood elf NPCs? Might as well populate the world a bit"): sixteen more
people, guards at Amberwatch, Dawnrest and both Spire gates, a hauler and Rosa's helper, Dawnrest's carpenter and
hunter, a fisher on the pier, a student, an old lady from Silvermoon, and four transplants (two still wet on the Waking
Shore, one carrying water at Dawnrest, one settled in the Spire). Everyone wears the BE-M and BE-W townsfolk looks by job.

**The art** (21 Nov 2026, `docs/dawnhaven_art_prompts.md`): DH1 ground, DH2 props, DH3 buildings and DH4 town props are
in. The Spire is built from DH3 and DH4; the woods keep a few of Azshara's trees and crystals among the isle's own.

**The faction card:** the Sunreach Conclave's home is Firstlight Spire now (`tools/build_sunreach_conclave.py`); its
tabard, hawkstrider and exalted dragonhawk were already in. DH5 redraws the card's painting at the Spire (optional).

**The air** (`docs/environment_effects_art_prompts.md`): autumn god rays, leaf shadow and falling leaves in the Glade;
dusk light and red leaves in Duskfall; a gold bloom and motes in the Spire; bubbles, wisps and arcane motes in the caves.

**Secrets:** four, placed blind (counts only). Chests on both open maps.
