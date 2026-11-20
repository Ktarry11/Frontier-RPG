# The World Tree: what was built

The vision, Kyle's answers and the full road are in `docs/worldtree_brief.md`. The art is in
`docs/worldtree_art_prompts.md` (W1-W6) and `docs/sky_art_prompts.md` (SK1-SK19, SK17B, BK1-BK12). All of it landed
on 19 Nov 2026 and is sliced.

## Rootwater Isle (42-44), done 20 Nov 2026

The first map of the tree: the island the roots split out of the reef, with the trunk rising out of its middle.

| Piece | Where |
|---|---|
| Map (180x150) | `tools/handbuilt_worldtree_rootwater_isle.py`, baked to `assets/tiles/worldtree/baked_rootwater_isle` |
| Creatures, rares, loot, encounters, gathering, fishing | `tools/build_rootwater_isle_content.py` |
| People and the Highbough Tribes faction | `tools/build_rootwater_isle_people.py` |
| Quests (text) | `tools/rootwater_quests.py` |
| Quests (builder and audits) | `tools/build_rootwater_quests.py`, writes `data/quests/rootwater_isle.json` |
| Secrets | `tools/build_new_zone_secrets.py` (counts only) |

**The way in:** Boatman Grik'zul's boat from Grom'gol's pier, and Boatwoman Zaela's from Zoram Strand on
Ashenvale's coast (Kyle: "Let's also connect Zoram Strand to Rootwater."). The Root Stair at the trunk's east foot is
drawn and waits for the Lower Boughs, which opens it.

**The landing:** Headwoman Zula Rootcaller runs it. It's a landing, not a town: two traders (Provisioner Mojo'tu and
Trader Sen'kaa), no inn and no flight path. Those are in the Great Settlement, up the tree.

**The creatures:** 22 kinds and 4 rares (The Rootmaw, Tapmaster Grell, Zul'gash the Climber, The Rot-Mother), with 16
rare items. The tree's sap is a new mob material, Golden Tree-Sap, used by alchemy and woodworking. The ooze is the
Goldensap Ooze, because Stonetalon already has a Sap Ooze.

**The quests:** 32, all 42-44. 24 are given at the landing, 1 is started by a dropped item, and 8 are unlocked by
earlier ones. The trolls' quests pay the Highbough Tribes (28 quests); Marta Kowalczyk's pay nobody. The threads:
- The hungry tree: the sap makes what drinks it big and wrong, and the bark is rotting. Witch Doctor Tazjin's chain
  ends at the Rot-Mother; Sapwatcher Uzo measures the sap and finds out who's buying it.
- The Bloodsail tap: Zula's chain against the sap camp and Tapmaster Grell; Fizzle Brasswinch wants his winch avenged.
- The Bloodscalp climb: Huntress Ka'lisa and Marta against the war camp, ending at Zul'gash the Climber, with a raid
  plan that drops off a war-climber.
- The lagoons: Scout Jinzo's chain ends at the Rootmaw.
- The falling sky: a bronze wing nobody on the ground could have made. Fizzle can't place it, and neither can Marta.
  It's the first thread of the one that ends at the Crown.
- Out by both boats: word to Attache Zul'jana at Grom'gol and a letter to Boatwright Illyen at Zoram Strand.
- Up: Zula sends you to the foot of the Root Stair once the Rot-Mother and Grell are dead.

**The faction:** the Highbough Tribes, led by High Chieftain Zan'kaji in the Great Settlement. The faction exists and
the island's quests pay it; its shelf, quartermaster and the leader's NPC come with the Great Settlement.

**Faction pages:** every faction but the secret one has its painting behind its page (Kyle: "very opaque and unique
for each one"). The text sits on a dark card on the left with the painting clear on the right (Kyle, 19 Nov: "make the
text easier to read bro...its still blending into the background").

## Next

The Lower Boughs (44-45), the Great Settlement and the Highbough shelf, the Middle and Upper Boughs and the Cloudbreak,
the sky renderer, then the sky maps. See `docs/worldtree_brief.md` for the whole road.
