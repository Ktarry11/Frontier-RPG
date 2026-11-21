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
and two recipes at Exalted, and a teal and red tabard. The mount is the Cloudtop Wyvern (sheet H14).

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

## The Upper Boughs, the Stormsplit and the Cloudbreak (20 Nov 2026)

Kyle: "So finish up the upper layers if not done".

**The Upper Boughs** (47-48, 180x150, `tools/handbuilt_worldtree_upper_boughs.py`): a pinwheel. The trunk stands in
the middle as a solid column with a walkable ring round it (the loa face carved into it, a tower house and a stair
cut into the bark), and six long boughs curve out from the ring like the arms of a storm: the Wyvern Roosts, the
Storm Bough, the Gale (two arms, joined by an old rope walk across the drop), the Thunderhawk Reach, and the Skiff
Wreck, where the Fallen Skiff lies across two branch tips as a deck over the gap. Highrest, the Windwardens' camp,
sits on a shelf below the ring. The drop is cloud, white and close. Ground: pale wind-scoured bark, lichen on the
sheltered side, storm bark only where lightning has burned it, and the first gold leaves at the tips.

Kyle, mid-build: "dont just drop shit on ub randomly", then "i mean like dropping totems in the middle of the thing or
on a branch isnt. greenery is fine". Greenery scatters; objects don't. Highrest is laid out as a camp (brazier at the
middle, lean-to, hammock, sap barrels, the lookout and the loa totem at the edge, wind charms on the rim), rope posts
stand in pairs at the rope walk's ends, nests and lightning stumps are where the creatures and the storms are. The
same pass moved the Middle Boughs' totem and braziers to guard the sealed Heartwood Hollow and put a stray charm by its
shrine, and clustered the Cloudbreak's charms round the Charm-Tree.

**The Stormsplit** (cave, 84x100, `tools/handbuilt_stormsplit.py`): the line of the lightning that split the trunk.
Kyle: "less zig zag for the tunnel, thatd be annoying to run up". Two long straight legs with one kink where the bolt
first struck, Thunder Hall at the bottom with the lightning still crawling across its floor (it lights the hall), and
a narrower split off the kink down to the Scorched Nest. Bosses: Old Charwing (the nest) and the Caught Storm (the
hall).

**The Cloudbreak** (48, 64x124, `tools/handbuilt_worldtree_cloudbreak.py`): built only to be walked through. The last
branches rise nearly straight through the cloud (straightened for the same note) with two short rope ladders across
the gaps, from fog at the foot to gold at the top (the map's `LIGHT`, a new baker hook), and end on a platform of
living heartwood against an old stone wall with the mural on it. No monsters, no quest givers; the places are named
for the climbers who went before (Where Ruk'tan Turned Back, Zel'ji's Rope, the Charm-Tree, Old Vosh's Ladder).

**The first cutscene** (`world/cutscenes.py`, `ui/screens/cutscene_screen.py`, `docs/crown_cutscene.md`): walking up
to the mural plays the six Crown shots once per character (pan, zoom, crossfade, shake, the gold flood), then the
mural on the map is broken open for good. Escape, Enter or Space skips. Seen flags save with the character. When the
Sunward Crown exists, the cutscene ends with you standing on it; until then it hands you back to the Cloudbreak.

**The people:** Highrest's Windwarden Kazra'jin, Wyvern-Tamer Gu'lok, Stormcaller Ixi, Skywatcher Tal'mae, Old Muzzi
(who climbed with Ruk'tan and Zel'ji), and Ingrid Haugen, a mountaineer and meteorologist from Tromso. Two traders,
the Stairwarden at the root stair, Ladderkeeper Vosh at the foot of the Cloud Way (grandson of the Vosh who hung the
last ladder), and two scouts.

**The creatures:** 15 in the open (5 rares) and 6 in the Stormsplit (2 bosses), wearing the last of sheet W6.

**The quests:** 27, 23 given at Highrest, plus Ropehand Dezza's hand-off up from the Middle Boughs. Threads: the
ascent (Kazra'jin's chain ends at the top of the Cloudbreak, in front of the wall; it stops there, and the wall is the
cutscene's); the wyverns (to Stormcrest and to Old Charwing in the cave); the storm (storm-glass, the Lightning-Eater,
the Caught Storm); the boat with no water (the Fallen Skiff's guardians and warden, and its log down to Tel'zan: they
were sailing toward the tree, not past it); the climbers (Old Thunderbeak, and Muzzi's charm for Zel'ji tied on the
Charm-Tree); the weather (Ingrid's readings, the Gale's harpies and Gale Queen Skirra).

**Secrets:** 2, cut into the tree.

## The Sunward Crown (48-49) and Lenswatch, built 20 Nov 2026

Kyle: "Lets build cloud and floating island zones? Our home bre aetherian sky continent", "So these places can be
large! Don't hold back right bro", "the first zone players get into is where tension is super fucking high", and,
when the first draft came out as limbs off a hub again, "Stop reusing the same shape....clouds can be walked on too".
The story is Kyle's twenty answers (`docs/worldtree_brief.md`, "Twenty questions").

**The sky renderer.** A map with a `SKY` dict bakes see-through PNG chunks (`tools/bake_ashenvale.sky_cut`): the drop is
cut out, rock hangs under the land's south edges, and walkable cloud gets soft billows under it instead of rock (the
module's `SKY["cloud"]`). The renderer (`ui/tilemap_renderer._draw_sky`, `_draw_sun`) paints the far cloud sea with
parallax and drift, near wisps, and the sun's rays over everything. A sky map registers no obstacle copy of its chunks
(that doubled the soft edges into tile-shaped steps), and its "cliff" marker tiles aren't drawn.

**The Crown** (`tools/handbuilt_worldtree_sunward_crown.py`, 300x240, the biggest map in the game, about 43,800
walkable tiles): a horseshoe of golden canopy curled round the Hollow, the open heart where you look down the tree; its
mouth opens east onto the Cloud Shelf, walkable cloud torn by rifts, with the Stormbank's dark cloud in its south-east.
On the cloud: the Parley Stones, the Sunken Seal in its moat of open sky, the Annex, the Survey Dock. Off it: the
Chainhold and the Driftlets, on chains. Subzones: the Mural Gate, the Lookdown, Spearhold, the Goldenwood, the Taken
Crown, the Falls of Light, the Parley Stones, the Sunken Seal, the Chainhold, the Cloud Shelf, the Annex, the Survey
Dock, the Stormbank, the Driftlets. The fields are cached on a quarter-tile grid, so the bake takes minutes, not an hour.

**Lenswatch** (`tools/handbuilt_worldtree_lenswatch.py`, 130x96): the survey's town, an anchored island with the
Skiff Roost and the Lens Hall on islets of their own. Gangway on the west (it lies east of the dock). The inn and the
Crown's one flight path (the skiffs).

**The links.** The Cloudbreak's broken mural (32,13) <-> the Mural Gate (100,164); the cutscene's end puts you at the
gate. The Survey Dock (295,130) <-> Lenswatch (2,46).

**People** (`tools/build_sunward_crown_people.py`): 31 people and one thing. Spearhold's trolls under War-Leader
Rakkuzi and Envoy Garrok Blackmane from Orgrimmar; the survey's Aetherians (Surveyor-Captain Ilvaro Destren and
Lenswatch's keepers); the Annex's Earthborn (Leandro Arrieta, Dr. Rania Azar, Pavel Novak, Ewan Docherty, Beatriz Lobo);
the two allies, Ilaren Vey and Leandro. Aetherian is an NPC-only race now (`world/race_registry.py`); only the men are
drawn, so every Aetherian NPC is a man until the women's sheet lands.

**Creatures** (`tools/build_sunward_crown_content.py`): 32, seven of them rares (Old Sunantler, the Dewdrinker,
Centurion Valeth Krane, Lance-Captain Varos Thale, the Stone That Woke, the Hollow Storm, Mother Greatfin), 28 rare
items, gathering and fishing at 48-49. The sky sheets SK12 to SK14 are registered in `creature_sprites.py`; what the
Crown doesn't wear yet is parked for the zones it's for.

**The Aetherians** (`tools/build_aetherians_faction.py`): the faction, home Aurelion, leader the council's First
Speaker; the shelf comes with Aurelion.

**Quests** (`tools/sunward_crown_quests.py`, `tools/build_sunward_crown_quests.py`): 39, 28 of them from the three hubs.
The war, the proof (who called the soldiers down), the survey, the Earthborn, and the seal: it cracks with every side
standing at the ring, the council opens Aurelion to the ground, and the Chainhold's lance-captain goes so the council's
skiff can come down. Reputation: the Highbough Tribes 15, the Aetherians 14, Orgrimmar 2; the Earthborn pay nobody.

**Watching the cutscene again** (`docs/crown_cutscene.md`): the Mural Shard keepsake (learned the first time any
character sees it) and the fallen piece of the mural by the Mural Gate. A replay never moves you.

**Secrets:** three on the Crown, placed blind (counts only).

**QA** passed: portals, arrivals, NPC tiles and props, encounter tables, creature sprites and reachability, rares,
nodes, gathering, fishing pools, flight paths, town services, factions, faction rewards, vendors and stock, collection,
keepsakes, secrets, hidden zones, quest givers, hubs, levels and objectives, combat backgrounds, text encoding, start
zones, exits. qa_prop_overlap still counts 137 props cleared across the world against its cap of 120; the Crown and
Lenswatch clear none.

## The Celestial Expanse (49-51), the Golem Vault and the Storm-Well, built 20 Nov 2026

Kyle: "lets build the celestial expanse if the Sunward Crown is done". Mid-build: "dont make them too hard to travel on
with tiny paths and snag points....looks good - sucks to play", "i do like the concept of 'island waterfalls' where
some-fucking-how we have unlimited water pouring off the island lol", and "And we will have dungeons and caves too i
hope", then "remember that this is high level zone - so multiple floors are okay". The brief's line for it is "the old sky ruins wake (Kharad-age machinery, sky-golems); Ascendancy patrols; sky
beasts".

**The map** (`tools/handbuilt_worldtree_celestial_expanse.py`, 300x260, about 26,900 walkable tiles): open day sky
with the Great Sky River running from Aurelion's broken aqueduct at the north edge down a string of six islands (the
Spillway, Halcyon Rest, the Broad Isle, the Golem Fields, Crashfall, the Last Falls), pouring off each one onto the
next and off the last into nothing. Off the river: the Silent Forge, the Lancer's Perch, Tethertown's tethered rocks,
the Orbiting Ruins (six islets round a broken Kharad citadel, two spokes through the middle, one span of the ring
fallen) and the Whale Shallows, walkable cloud. Twelve subzones. The side islands' pools spill off their nearest edge
too (the wellstones: the islands' crystal pulls water out of the clouds, and the Aetherians can't tell you how).

**Built to play, not just to look at.** The bridges are about eight tiles wide, the ring's spans as wide as the main
ones, and the island and cloud fields are blurred on the cached grid before anything reads them, which rounds the
coasts and fills the one-tile notches you'd catch on (`_SMOOTH_TILES`). Measured: one connected piece; a body three
tiles wide reaches all of it and a body five wide reaches 99.5%. The interiors are grass and clover with rock only at
the rims (`EXPANSE_SHEET` in `tools/bake_ashenvale.py`).

**The Golem Vault and the Storm-Well** (a cave of two floors, 84x100 each, `tools/handbuilt_golem_vault.py` and
`tools/handbuilt_storm_well.py`, baked by `tools/bake_golem_vault.py` and `tools/bake_storm_well.py`): the sky's first
cave, the Kharad's vault under the Golem Fields, through a knotwork door on the fields' west side. Kyle on the first
draft: "Also hallway simulators are boring and uninspired". So it's rooms, each with its own thing, joined by short wide
ways, with more than one way through. The first floor: the Muster Hall, where the golems that were never sent out stand
in ranks with an aisle down the middle; three ways down out of it, to the Wrights' Hall (the forge and the crane,
Vault-Thane Brask, optional), the Assembly Floor (the last golem half-built in its scaffold) and the Sleepers' Hall (the
crews on their stone biers); all three meeting again in the Deep Hall, and the Deep Stair down. The second floor: the
Binding Hall (a ring of chained binding stones) with the Core Racks off it, three ramps down into the Well, one great
round cavern with the bound storm in the middle as a pool of dark storm-cloud you can't walk into, and four bridges
across it to the dais where Stormwright Yrvald keeps it (the storm is read off the map's water tiles, so the dais and
the bridges bake dry). A body three tiles wide reaches every room on both floors. The crews are Kharad, the giants who
were here first.

**The links.** Lenswatch's Skiff Roost (119,13) <-> the skiff landing on Crashfall (103,206). The Golem Fields' vault
door (90,156) <-> the Golem Vault (42,2); the Deep Stair (42,97) <-> the Storm-Well (42,2). The sky-bridge's foot (226,2) is Aurelion's, later.

**People** (`tools/build_celestial_expanse_people.py`): 20. On Crashfall, the survivors of the council's skiff (Ilaren
Vey and Leandro Arrieta, Skiff-Pilot Varo Senn, Herald Cassian Orel) and the survey's landing hand; at Tethertown, the
Earthborn (Kaisa Lehtonen, Gustavo Pires, Annelies de Vries, Yasmin Darwish); at Halcyon Rest, Keeper Ithren Lorrow,
Skiffmaster Davin Sorell (the zone's one flight path), Teodric Ashlane from the fallen Eighth Ring, Dace Morrow who put
his lance down, and two traders; out on the islands, Scholar Idris Marrowell of the House of Long Memory, Dr. Ana
Kealoha with the whales, Elder Merek Vale at the Last Falls, Aqueduct-Warden Lorne Ishay and Bridgewarden Caldus Rhee.

**Creatures** (`tools/build_celestial_expanse_content.py`): 32 in the open, seven of them rares (Old Goldmane, the
Unbound Core, Forge-Elder Ommun, Ringwarden Kozh, the Pale Serpent, Spire-Captain Alun Vesk, the Old Mouth of the
Spill), and 7 in the vault's two floors (2 bosses); 36 items; gathering and fishing at 49-51.

**Quests** (`tools/celestial_expanse_quests.py`, `tools/build_celestial_expanse_quests.py`): 43, 33 of them from the
three hubs. The crash (the wards that shot the skiff down were Kharad), the Kharad (the golems getting up, the core
under the sword, the forge and its elder, the vault and the storm at its bottom, which shuts the wards off), Tethertown (the last few Earthborn, the ropes, the garden),
Halcyon Rest (the river road, the ring's bells, the broken citadel, the skiffs flying dark), the Lancer's Perch (the
deserter and the captain who gave the order), the whales, the Spillway, and the bridge: the herald's seal goes to the
bridgewarden and the bridge is lowered for you. Reputation: the Aetherians 29; the Earthborn pay nobody.

**A reputation fix.** The Aetherians listed the Sunward Crown as one of their zones, and a zone pays for every quest in
it, so the Crown's Earthborn quests were paying the Aetherians. Only Lenswatch is a zone now; the Crown's and the
Expanse's Aetherian quests are listed one by one.

**The sky's one mystery** (Kyle, 20 Nov 2026, `docs/worldtree_brief.md`): the three peoples built the floating world
together, the alliance fell, and what they built is dying; the mural is the first evidence. The Expanse's piece is the
Unbound Core: Kharad stone round Aetherian-cut crystal, holding a storm the Veyr sang into it.

**Secrets:** three on the Expanse, placed blind (counts only).

**QA** passed: portals, arrivals, NPC tiles and props, town services, encounter tables (both cave floors resolve
their own tables), creature sprites and reachability, rares, nodes, gathering, fishing pools, flight paths, factions,
faction rewards, vendors and stock, collection, keepsakes, secrets, hidden zones, quest givers, hubs, lore, levels,
objectives and drops, combat backgrounds, exits, chests, start zones, cave smoothing, text encoding. Fixed on the way:
the Crown's two thin quest drops, its Lenswatch shelf drawn through the archive, and its quests' lore lines (the check
had no words for the sky's Earthborn places or the Aetherians' "the change"). qa_building_overlap now skips a pair a
cutscene swaps (the Cloudbreak's mural); it still fails on ten older pairs in the Great Settlement, the Middle Boughs
and Rootwater Isle, and qa_prop_overlap still counts 137 against its cap of 120, both from before this build.

## The Anchorfields (51-54) and the Keel, built 20 Nov 2026

Kyle: "we wont build raids yet. We need quest lines. So keep building zones and eventually the grand city", and,
building it, "do keep in mind aurelion is ancient, we are new. we are learning lore not having it being new to the
world". Also "keep your progress report up to date bro": the build ran on the task list.

**The road without the city.** The Expanse's sky-bridge stays shut: the council's second letter says the outer rings
can't take visitors while the Third Anchor slips (`ceq_word_to_the_wardens`, Caldus to the Warden-Prime), and the old
aqueduct arm runs east off the Spillway (295,30) to the Anchorfields (3,74). Saving the Third Anchor earns the bridge.

**The map** (`tools/handbuilt_worldtree_anchorfields.py`, 300x250, about 42,400 walkable tiles): a shattered plate. One
great shelf of stone, cracked by gravity going wrong into five big shards with open sky in the cracks and wide stone
bridges over every one: the Estates (House Vaelith's old estate), the First Anchor in its chain-field with Keelstone
at its foot, the Gearwork's engines, the Seized Anchor (the Ascendancy's camp) and the Slipping Anchor. Off the shelf:
the House of Measures' Observatory, the Listing Isle with Tiltside on it, a chain-held islet, the aqueduct arm, and the
Dropfield, walkable cloud strewn with the island that fell centuries ago. A dawn sky. Measured: one piece, and a body
five tiles wide reaches all of it. Every pool spills off its nearest edge (the wellstones).

**Ancient, not new.** The anchors are a thousand years old; the wardens' links are named for wrights dead nine hundred
years; the house has written the shelf's lean every night for as long; the Dropfield is the Fourth Anchor's island,
whose story the old warden carries word for word. The failing is a long decline that's lately got faster, and the
player walks into the middle of it.

**The Keel** (cave, 96x96, `tools/handbuilt_keel.py`, baked by `tools/bake_keel.py`): the Third Anchor's root. Rooms,
not halls: the Root Stair, the Chainwell (a round hall round the shaft, the anchor chain going down into open sky
through the floor; walk the rim either way), the Ballast Halls, the Wardens' Last Post (Warden-Captain Oris Hale,
optional), and the Crystal Keel, cracked, with the Keel-Heart grown out of the crack. A five-wide body reaches every
room.

**People** (`tools/build_anchorfields_people.py`): 21. Keelstone's Anchor-Wardens (Warden-Prime Aldric Sorne, the
chainwright, the engineer, the scout, Old Warden Ebbe Tharn, the skiffmaster and two traders); the House of Measures
(Master Ivo Kestrel, the star-reader, the archivist); Tiltside's Earthborn (Margit Halvorsen, Bartosz Wierzbicki,
Dr. Ngozi Eze, Daisuke Moriyama); House Vaelith's steward and heir; the armwarden, the engine-tender, the warden at the
Third Anchor, and Wade Prentiss scavenging the Dropfield.

**Creatures** (`tools/build_anchorfields_content.py`): 29 in the open, seven of them rares (the Gardener, Starfall the
Burning Shard, Engine Seven, Anchor-Marshal Corvan Sael, the Unmoored, Old Ballast, Old Hornback), and 6 in the Keel (2
bosses); 36 items; gathering and fishing at 51-54.

**Quests** (`tools/anchorfields_quests.py`, `tools/build_anchorfields_quests.py`): 37, 29 of them from the three hubs.
The wardens (walk the three anchors; the named links and anchorlight; reading the Third and what comes up out of its
cracks, to the Unmoored; the Ascendancy's own drift logs, to the anchor-marshal; the old warden's story, down into the
Keel to relieve Captain Hale; the Keel-Heart, which stops the slipping and earns the bridge); the House of Measures
(the ledger that's too small, the survey marks, the lights that move, a new lens, and the three-handed plate); Tiltside
(the tilt the Earthborn measure because nobody else will); the estate, the Gearwork, the Dropfield. Reputation: the
Aetherians 29; the Earthborn pay nobody.

**The sky's one mystery, the Anchorfields' piece:** the House of Measures' oldest records were copied from plates in a
hand nobody reads, and a plate off the fallen island shows why: three columns side by side, old Aetherian, Kharad runes
and Veyr song-notation, saying the same thing. The old warden's oldest line, "The first anchor was raised by three, and
three kept it", stops meaning three wardens.

**Secrets:** three on the Anchorfields, placed blind (counts only).

**QA** passed: portals, arrivals, NPC tiles and props, town services, encounter tables, creature sprites and
reachability, rares, nodes, gathering, fishing pools, flight paths, factions, faction rewards, vendors and stock,
collection, keepsakes, secrets, hidden zones, quest givers, hubs, lore, levels, objectives and drops, combat
backgrounds, exits, chests, start zones, cave smoothing, dungeon packs and boss turns, text encoding. The lore check
learned the Anchorfields' Earthborn places. qa_building_overlap's ten older pairs and qa_prop_overlap's 137 are
unchanged from before this build; the Anchorfields and the Keel add none.

## Next

The Ascendant Bastions (54-57), then the Fading Firmament (57-60), and then Aurelion, the Aetherian capital, whose
bridge the Keel-Heart's death earns (Kyle: zones first, "eventually the grand city"). The raids wait. The Aetherian
start zone is parked until 60 is done (its first two maps are named: the White Expanse, 1-6, and the Shattered
Reaches, 6-11). The Celestial raid, the Stormhold, is designed for turn-based combat in the brief and waits behind the
cracked seal until raids are built.
The Heartwood Hollow is the tree's dungeon when Kyle calls it. See `docs/worldtree_brief.md` for the whole road.
