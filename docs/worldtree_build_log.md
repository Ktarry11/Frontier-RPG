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

## The Lower Boughs (44-45) and the Knothollow, done 20 Nov 2026

The first lived-on tier, up the Root Stair from Rootwater. Rootwater's last quest now hands off up the stair to Elder
Tal'vani in Mossroof.

| Piece | Where |
|---|---|
| Map (180x150) | `tools/handbuilt_worldtree_lower_boughs.py`, baked to `assets/tiles/worldtree/baked_lower_boughs` |
| The cave (84x100) | `tools/handbuilt_knothollow.py`, baked by `tools/bake_knothollow.py` |
| Creatures, rares, cave bosses, loot, encounters, gathering, fishing | `tools/build_lower_boughs_content.py` |
| People | `tools/build_lower_boughs_people.py` |
| Quests | `tools/lower_boughs_quests.py` (text), `tools/build_lower_boughs_quests.py` (builder and audits) |

**The shape:** the trunk is a wall of bark along the whole north edge (W1's trunk tiles are drawn straight-on), with a
ledge at its foot. Three great boughs run south from it over the drop, each as wide as a road: the Great Bough in the
middle with a river down its centre, the Howling Bough (the apes) to the west, the Silkwood (the spiders) to the east.
Plank bridges join the Great Bough's forks to the outer boughs. The Bloodscalp come up on ropes over the Great Bough's
far end, the Climbers' Cut. Mossroof, the trolls' village, sits where the Great Bough leaves the trunk.

**The drop.** It's the module's sea field, so the baker paints it, and `build_layout` turns it into collision (no water
tiles over the void, so nobody fishes off a branch; the river is the only fishing). The baker has a new depth pass for
any map that sets `DROP` (`tools/bake_ashenvale.drop_depth`): the canopy far below fades toward a green-gold haze, the
boughs throw a soft shadow down onto it from the top-left light, the bark darkens where each bough rounds away at its
edge, and the shore foam is switched off. Every tier and sky map over a drop can use it.

**The doors:** the Root Stair down to Rootwater (40,16), the Knothollow's knot in the trunk (62,16), and the Great Lift
(130,16) up to the Great Settlement, which opens when the city is built.

**The Knothollow** (Kyle, 19 Nov: caves "just going deeper into the world tree"): a knot in the trunk rotted hollow,
borer galleries eaten along the grain with dead-end bores off them, the Sapwell where the borers broke into a vein of
glowing sap (Gnawmother Ixx), and the heartward bore down to the heartwood (the Amber Glut, optional).

**The creatures:** 18 kinds in the open and 4 rares (Sunscale, Old Goldtooth, Mother Lattice, Ropemaster Vaz'jin), 7 in
the cave with its 2 bosses, 24 items in all. They wear W6's figures, some of them the same figure as a Rootwater
creature under a different name.

**The people:** Mossroof is a small group, not a town (no inn, no flight path): Elder Tal'vani, the bough-hunter, the
river's shaman, the bridgekeeper, a scholar from the Settlement buying sky-bones, and Aroha Tane, an arborist from New
Zealand who climbed for the view. Two traders, a stairwarden, the liftkeeper and two scouts.

**The quests:** 32, 23 of them given in Mossroof, 28 paying the Highbough Tribes. Threads: the Bloodscalp climbers (to
Vaz'jin, with a knotted cord off a ropecutter); the apes (to Old Goldtooth); the Silkwood and the bridges (to Mother
Lattice); the river's sap (to Sunscale, then into the trunk to the Amber Glut); the borers (into the Knothollow to
Gnawmother Ixx); sky-bones (the falling-sky thread: Vel'jani sends a humming piece down to Fizzle at Rootwater, who still
can't place it); and the Great Lift, once Vaz'jin and the Gnawmother are dead.

**Secrets:** 2. The secrets builder now refuses a hidden place that would hang over a drop (`OVER_THE_DROP` in
`tools/build_new_zone_secrets.py`): on a map like this one, they're cut into the tree.

**Kyle's calls, 19 Nov, in the brief:** three capitals in the sky, one for each people; the Great Settlement big but
below a capital; caves into the tree, one a tier, and the dungeon in the Middle Boughs' heartwood.

## Next

The Great Settlement and the Highbough shelf, the Middle and Upper Boughs (each with its cave) and the Cloudbreak, the
sky renderer, then the sky maps. See `docs/worldtree_brief.md` for the whole road.
