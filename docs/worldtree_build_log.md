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

## The Great Settlement (44-48) and the Highbough Tribes, done 20 Nov 2026

**The city** (`tools/handbuilt_worldtree_great_settlement.py`, 184x160): the Highbough Tribes' home, a town but not a
capital (Kyle, 19 Nov: "Great settlement will be large but not capital city large"). Six districts on lobed shelves of
bough joined by bridges over the drop: the market, the trades, the Lantern Ward, the Roost, the falls and the garden
terrace, with Zan'kaji's Heart Palace on the Chieftain's Rise. The Great Lift comes up from the Lower Boughs; a second
lift waits for the Middle Boughs. Walk-tested: all 12,630 walkable tiles reachable from the lift, every person standing
somewhere you can reach. Kyle, 20 Nov: "Let's have a bit more land mass for gs", so the shelves were widened.

**Services:** inn, flight path (the bat Roost), auction house, bank, mailbox, a class trainer for every class and seven
pairs of profession trainers. 31 people and the mailbox (`tools/build_great_settlement.py`).

**The Highbough Tribes** (`tools/build_highbough_tribes.py`): the shelf at the quartermaster, the TBC way: Heartsap
Tonic at Friendly, a neck piece and a pattern at Honored, six ilvl 67 blues and a pattern at Revered, three ilvl 73 epics
and two recipes at Exalted, and a teal and red tabard. The mount waits for its art.

**The quests:** 12, every one given in the city, 9 paying the tribes and 1 paying Orgrimmar. Threads: the audience
(Ozenna's pass to Zan'kaji, then the Bloodscalp war leaders below); Horde ground (the envoy's year-long wait ends, and
Zan'kaji's answer goes to Thrall); sky-bones (the scholars' wall, the spiders' web-hall, and Tel'zan's record, which
says the pieces are getting bigger); the ward (Ozai's lanterns, a bat lost in the webs, the loa's Goldthorn, soil for
the terrace); and two transplants, Kofi Mensah from Accra cooking for market day and Hana Sato from a Kyoto tea house.

**Found on the way, and fixed for every zone:**
- **Kills and explores in every "The ..." zone could never count.** The game reports where you are as
  `the_lower_boughs`, quests were written `lower_boughs`, and the quest manager compared them raw. 46 explores and every
  zone-tied kill across Feralas's three regions, the Lower Boughs and the Knothollow were impossible to finish. Both
  sides now go through `zone_key` (`same_zone` in `world/quest_manager.py`), and `tools/audit_quests.py` judges the way
  the game does: 180 blocking problems to 0.
- **20 quest-reward weapons hit for 0-0.** Older hand-written rewards had no damage; `tools/quest_weapon_damage.py` gives
  them the generator's numbers, and the reward audit no longer counts tomes, orbs and relics, which aren't swung.
- **Two stale builders.** The Ashenvale quest builders are older than their data, and rerunning one undid the voice pass
  and the loot ratings. They now refuse to run without `--force`.

## The Middle Boughs (45-47) and Shriekhollow, done 20 Nov 2026

The tree's heart above the city, up the High Lift (the city's High Lift opened the same day).

| Piece | Where |
|---|---|
| Map (180x150) | `tools/handbuilt_worldtree_middle_boughs.py`, baked to `assets/tiles/worldtree/baked_middle_boughs` |
| The cave (84x100) | `tools/handbuilt_shriekhollow.py`, baked by `tools/bake_shriekhollow.py` |
| Creatures, rares, cave bosses, loot, encounters, gathering, fishing | `tools/build_middle_boughs_content.py` |
| People | `tools/build_middle_boughs_people.py` |
| Quests | `tools/middle_boughs_quests.py` (text), `tools/build_middle_boughs_quests.py` (builder and audits) |

**The shape:** you've climbed round the trunk, so it's the **west** wall now. The ledge at its foot is the Old Terraces,
the first climbers' stone: towers, cairns and shrines carried up a tree a block at a time. Heartwatch, the shadow
hunters' outpost, stands on a stone platform built out over the drop. Three boughs run east: the Lichen Reach (pale
lichen, an old shrine, and the construct that fell out of the sky across its tip), the Rotting Bough (rot pits, sap
blight, the things that live in the rot) and the Hollow Bough (the harpies' nests in the hollows of the bark). Four
plank bridges join them. The drop is mist now, the canopy long gone below it (`DROP` haze cool grey).

**The doors in the trunk:** the High Lift down to the city (16,128); Shriekhollow, the harpies' hollow (16,82); and two
drawn and waiting: the Root Stair on up to the Upper Boughs (16,18), and **the Heartwood Hollow** behind Heartwatch
(16,46), the dungeon door (the brief: "a door for later, its own call"). The shadow hunters keep it sealed.

**Shriekhollow:** grown, not eaten. The Roost is a ring of ledges round the Well, where the hollow's floor drops away;
the Throat climbs on with nests hung in side hollows; Matron Vyssa keeps the Eyrie at the top; past it the Rotdark goes
down to Old Splinterheart, a treant that grew in the dark on the rot, fed by the harpies (optional).

**The creatures:** 14 kinds in the open and 4 rares (Hushwing, the Wakened Surveyor, Old Barkrot, Old Raggedwing), 5 in
the cave with its 2 bosses, 24 items. W6's rot treant, blighted harpy, scout construct and gear drone are in use now;
the harpies and owls borrow older figures under their own names.

**The people:** Heartwatch is a small group, not a town: Shadow Hunter Vokra, Loa-Speaker Ganjo, Bark-Doctor Ezzi,
Huntmaster Raz'gul, Stonekeeper Jo'than, Scholar Nyara from the Settlement, and Dr. Priya Raman, a plant pathologist
from Bengaluru who came up to study the rot. Two traders, the ropehand at the lift and two scouts.

**The quests:** 31, 27 given at Heartwatch. Threads: the watch (the rot pushed back to Old Barkrot, then listening at the
sealed Heartwood Hollow: chewing, slow and steady); the tree's voice (Ganjo listening at the first climbers' stones);
the cure (Ezzi cutting out the rot, Priya working out that it's a fungus that feeds like an animal and goes down, not
out, into Shriekhollow to Old Splinterheart, her notes to Vokra); the harpies (to Old Raggedwing and Matron Vyssa); the
fallen construct (the falling-sky thread: the Wakened Surveyor's core is full of measurements of the tree, some made
before it was this tall, and Tel'zan writes "someone up there has been watching it grow"); the first climbers'
names (one is cut higher up the trunk than anyone has been). The city's Liftwarden Tagu sends you up.

**Secrets:** 2, cut into the tree.

**Found on the way:** the tree scatter and the rope posts were plugging the plank bridges (the baker painted the cut-off
planks as canopy, which is how it showed). Bridges and Heartwatch's stone now keep their tiles clear.

## The tree's hidden places (20 Nov 2026)

Kyle: "Yeah please do" (a skull zone and a frontier for the tree), and "I still want to see the structure of skull and
frontier zones. Just not where they are. Prevents you from making everything blobs". Names and shapes only; where they
are isn't written anywhere.

- **The Raincatch** (skull): terraced rain pools stepping down the bark, each held behind a curved lip of moss, with
  switchbacks between the lips, two fords, a drowned shrine on the middle terrace, and the trunk's bark walling the
  basin in. Old Ma'luu, who climbed up to pray for rain as a girl, and four quests (the third elite).
- **The Kapok Crowns** (frontier, open): a stretch of the Amazon canopy that came through the merge, laid out as a tree
  seen from above: one great limb forking and forking again out to its crowns, two branches touching to make one
  loop, and a flooded fork where Boiuna lives. Dr. Luana Ferreira, a canopy ecologist from Manaus, and four quests.

The first cut of each copied a shape that already existed (a ring round a lake, like the Drowned Idols; pods on
necks, like the Saltgrave and the Tanglewood Shoals). Checked against a sheet of every skull and frontier map and
redrawn before anything shipped.

`tools/build_hidden_content.py` now keeps existing kits, loot and quests and only adds new ones (`--rebuild` for a
fresh write): re-running it for this pair had put 32 boss kits, 11 bosses' loot and 17 quests back to how they were first
written. `tools/build_new_zone_secrets.py` cuts the doors for hidden zones on the maps it covers.

## Next

The Upper Boughs (with its cave) and the Cloudbreak, the sky renderer, then the sky maps. The Heartwood Hollow is the
tree's dungeon when Kyle calls it. See `docs/worldtree_brief.md` for the whole road.
