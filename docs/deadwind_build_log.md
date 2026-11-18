# Deadwind Pass: what was built (18 Nov 2026)

The vision is `docs/deadwind_brief.md` and the story `docs/deadwind_quest_plan.md`. This is what's in the game.

Kyle, along the way: "beautifully written quests. Lots of lore....they should be exciting to do", "Try to keep somewhat
authentic wow shape. Slightly modified though. Doesn't need to be perfect", "Make the caves and Dungeons actually
unique and beautiful. I love the history of Chernobyl in real life and I want this to do it justice.", and once it
was in: "make the exclusion zone multiple layers and kind of nuclear reactor mixed with the wheel...make the wheel
massive and iconic!"

## The maps

| Map | Levels | Builder | What it is |
|---|---|---|---|
| Deadwind West | 55-57 | `tools/handbuilt_deadwind_west.py` | The Cracked Tunnel in from Stranglethorn, Delgado's Fence, Deadman's Crossing in the north with the Watch's gate, Deadwind Ravine and Grosh'gok Compound in the north-west, the Widows' Wood, the Sickwater and the Black Tarn, Baba Hanna's homestead, Coachman's Bend and Morgan's Plot in the south-east. |
| Deadwind East | 56-58 | `tools/handbuilt_deadwind_east.py` | The Sleeping Gorge (the road goes down into it and along its floor), the broken bridge, Ariden's Camp on the rim, the Drowned Hollow, the Vice east to Karazhan in the south-east, the Stopped Places, the Hanging Slide, the rupture with the wheel and the containment spire, and the swamp road shut at a barricade. The wheel is 44 tiles tall, the tallest thing in the pass (taller than Karazhan), standing in a fenced lot nobody can walk behind, with the glow crater and the dungeon's door at its foot. |
| Ariden's Watch | town | `tools/handbuilt_ariden_watch.py` | The liquidators' camp, built round the pyre: the gate and the wash troughs, the board of names, the command house, Kenji's survey tent, the infirmary, the laboratory and the sealed store, the inn, the quartermaster, the smithy, the bat roost. |
| The Widows' Nest | 56-58 | `tools/handbuilt_deadwind_caves.py` | THE FUNNEL: a wide silk sheet that narrows into one winding throat, retreat holes off its sides, the brood at the top. The Silk Mother. |
| The Drowned Seep | 57-58 | the same | THE DRAIN: one long meander with the seep down its middle, oxbow pools off the bends, the sump at the bottom. The Drowned Thing. |
| The Exclusion Zone | 57-60 | `tools/handbuilt_exclusion_zone.py` | Three floors, six bosses (below). Fast exit past the last boss. |

**Classic's shape, slightly modified.** The road crosses the north at Deadman's Crossing, the ogres hold the ravine in the
north-west, Morgan's Plot lies in the south-east toward Karazhan, and the way south runs down the Sleeping Gorge and
turns east into the Vice to the tower. What's new is the way in (a tunnel from Northern Stranglethorn, its mouth in
the fen's eastern shoulder at (182,115)) and the rupture in the middle.

**The art.** Kyle's eight Deadwind sheets. The ground sheet's rows were re-sliced on their measured seams (they came
back uneven and every tile had a strip of the next row on it). Each cave and the dungeon has its own light: the nest
lit by its eggs, the drain by the seep along its banks and a sick red in the sump; the Exclusion Zone's floors are
described below.

## The Exclusion Zone: the wheel, then the reactor, then the Foot

The tear keeps a copy of everything that dies near it, and it has been reading the people who came through it. Under
the wheel it grew a copy of the wheel; under that, the building the transplants see whenever they look at the wheel.
Nothing from Earth is down there, only the shapes, and the deeper you go the better the copy gets.

| Floor | Levels | Rooms | Bosses |
|---|---|---|---|
| **The Wheel's Shadow** (`The Exclusion Zone`, 200x200) | 57-59 | The wheel laid flat: the Crater Floor at the rim's bottom, the rim walked three quarters of the way round past three small cars hung off it, the Brood (west), the Stacks (north, black-glass shelving), the Hanging Cars (east, cages from the roof over the volunteers' last camp), the Open Spoke in to the Axle, a shaft ringed with the seep and a stair cut into its island. The other three spokes end against stopped time. | Gristlemaw, Broodmother Vexis, Archivist Nine |
| **The Reactor Hall** (180x160) | 58-60 | The shaft comes down at the north end. The core is a sealed block in the middle, and the way in is the long way round: west down the Turbine Hall (five turbines in a row), east across the flooded basement (the Bubbler Pools), north up the Ninety Seconds (the roof, copied inside out, graphite where it fell), and in through the breach to the Lid, standing on its edge, with the stair down beside it. | The Glow-Eater, The Stopped Man |
| **The Foot** (150x150) | 59-60 | The Sandfall at the bottom of the shaft, heaped with everything dropped down it; the Steam Corridor three sides round the basement; the Elephant's Foot, a lake of the melt wall to wall with four channels pouring in, the Heart on its island, a second bridge out to the fast exit. | The Wound's Heart (always drops the T0 bracers token) |

The names are the liquidators', the way their parents' generation talked about Reactor Four: the Bubbler Pools (the
three men who waded into the flooded basement in May 1986 to drain them), the Ninety Seconds (the soldiers who cleared
the roof by hand, ninety seconds each), the Lid (the upper shield the explosion threw up and dropped on its edge), the
Sandfall (the sand, clay, lead and boron the helicopters dropped in), the Steam Corridor and the Elephant's Foot (where
the melted core ran down and set).

The light gets stronger as you go down: the seep's green round the axle and the Stacks' violet on the first floor;
the pools, the pale blue of stopped time up the roof gallery and the core lit green from below on the second; on the
third the melt itself, lit from inside, and a deep red on the Heart's island.

## The people

**Ariden's Watch:** Chief Liquidator Halyna Bondar, Kenji Watanabe, Deathguard Harrow, Old Tobiah, Dr. Aigerim
Seitkali, Master Apothecary Morwen Ashgrave, Apothecary Lisbeth Vane, Luiz Ferreira, Rine Lajuon, Innkeeper Sela
Crowe, Quartermaster Dale Henning (the Liquidators' shelf), Peg Thwaite (food), Ironmonger Edric Vail, Bat Handler
Ossian Reed (the flight path). The four sheet-5 recruits stand at their posts: Taras and Kashtan at the wash troughs,
Wes on the fence, Mariana at the infirmary, Neil at the sample racks.

**Out in the pass:** Corporal Ray Delgado at his fence, Agatha Morgan at the Plot, Grull the Younger on the ravine road,
Baba Hanna at her homestead, Ariden at his camp, the Bridge Echo on the bridge, Deathstalker Vessa Morrow at the
Stopped Places. Storesman Pell in Grom'gol gives the first quest.

Where each of them came from: Slavutych, Fukushima, St. George in Utah, Semey by the Polygon, Goiania, Rongelap,
Windscale's farms, Hanford, Kupuvate inside the Chernobyl zone.

Grull and the Bridge Echo wear their creature art through two NPC-only races (`ogre`, `echo`).

## The Liquidators (faction, `tools/build_liquidators.py`)

Quests at the Watch pay it, and so does every mutated thing in the pass to Honored. The Exclusion Zone's bosses pay
75 and its trash pays to Revered. Shelf: friendly, Liquidator's Iodine Tincture and Seep-Washed Bandages (made for it);
honored, the Liquidator's Dosimeter (a neck piece anyone can wear, in place of the tabard the plan named: the game has
no tabard slot) and the Flask of Mending; revered, six blues; exalted, three epics and two recipes (tailoring and
leatherworking).

## The creatures (`tools/build_deadwind_content.py`)

68 creatures: the open world's mutated wild and stuck dead, the caves' trash and bosses, the dungeon's sixteen trash and
six bosses. Rares: the Wagon Driver (Coachman's Bend), Mog'grak the Twice-Born (Grosh'gok), Old Three-Heads (the
Stopped Places), the Crow King (the Drowned Hollow). Gathering on both maps.

## The quests (`tools/deadwind_quests.py`, `tools/build_deadwind_quests.py`)

63 quests, every arc in the plan. 35 are given in the Watch, and nobody gives more than four. The threads a player
follows the whole way: Tomas the runner, Mykola (the echo, the Stopped Man, the board), Morwen's arm and Lisbeth's
two reports, Agatha and her son Edwin the coachman, Grull and his father, Ariden's evening, and the board of names
read at the start and again at the end.

One new engine rule came with it: a quest can list `excludes_quests`, and taking one of them closes it for good
(`world/quest_manager.py`). The Widows' Nest's last egg goes to Morwen or to Dr. Seitkali, never both.

## Settled along the way

- "The Seep" is the Forsaken's word for the fallout (the plan's pick; Kyle can still veto it).
- Recruits can't be above 58 (`tools/qa_recruit_placement.py`), so Neil and the three waiting for Moonglade and
  Winterspring came down to 58.
