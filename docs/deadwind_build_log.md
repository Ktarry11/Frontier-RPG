# Deadwind Pass: what was built (18 Nov 2026)

The vision is `docs/deadwind_brief.md` and the story `docs/deadwind_quest_plan.md`. This is what's in the game.

Kyle, along the way: "beautifully written quests. Lots of lore....they should be exciting to do", "Try to keep somewhat
authentic wow shape. Slightly modified though. Doesn't need to be perfect", "Make the caves and Dungeons actually
unique and beautiful. I love the history of Chernobyl in real life and I want this to do it justice."

## The maps

| Map | Levels | Builder | What it is |
|---|---|---|---|
| Deadwind West | 55-57 | `tools/handbuilt_deadwind_west.py` | The Cracked Tunnel in from Stranglethorn, Delgado's Fence, Deadman's Crossing in the north with the Watch's gate, Deadwind Ravine and Grosh'gok Compound in the north-west, the Widows' Wood, the Sickwater and the Black Tarn, Baba Hanna's homestead, Coachman's Bend and Morgan's Plot in the south-east. |
| Deadwind East | 56-58 | `tools/handbuilt_deadwind_east.py` | The Sleeping Gorge (the road goes down into it and along its floor), the broken bridge, Ariden's Camp on the rim, the Drowned Hollow, the Vice east to Karazhan in the south-east, the Stopped Places, the Hanging Slide, the rupture with the wheel and the containment spire, and the swamp road shut at a barricade. |
| Ariden's Watch | town | `tools/handbuilt_ariden_watch.py` | The liquidators' camp, built round the pyre: the gate and the wash troughs, the board of names, the command house, Kenji's survey tent, the infirmary, the laboratory and the sealed store, the inn, the quartermaster, the smithy, the bat roost. |
| The Widows' Nest | 56-58 | `tools/handbuilt_deadwind_caves.py` | THE FUNNEL: a wide silk sheet that narrows into one winding throat, retreat holes off its sides, the brood at the top. The Silk Mother. |
| The Drowned Seep | 57-58 | the same | THE DRAIN: one long meander with the seep down its middle, oxbow pools off the bends, the sump at the bottom. The Drowned Thing. |
| The Exclusion Zone | 57-60 | `tools/handbuilt_exclusion_zone.py` | THE WHEEL'S SHADOW: a rim walked three quarters of the way round, dead spokes, one open spoke to the hub. Six bosses. Fast exit in the hub. |

**Classic's shape, slightly modified.** The road crosses the north at Deadman's Crossing, the ogres hold the ravine in the
north-west, Morgan's Plot lies in the south-east toward Karazhan, and the way south runs down the Sleeping Gorge and
turns east into the Vice to the tower. What's new is the way in (a tunnel from Northern Stranglethorn, its mouth in
the fen's eastern shoulder at (182,115)) and the rupture in the middle.

**The art.** Kyle's eight Deadwind sheets. The ground sheet's rows were re-sliced on their measured seams (they came
back uneven and every tile had a strip of the next row on it). Each cave and the dungeon has its own light: the nest
lit by its eggs, the drain by the seep along its banks and a sick red in the sump; in the Exclusion Zone the seep's
green, the Elephant's Foot a deep red, the Ninety Seconds the pale blue of stopped time, the Stacks Karazhan's
violet.

## The dungeon's rooms carry the liquidators' names

| Room | Boss | The name |
|---|---|---|
| The Crater Floor | Gristlemaw (57) | |
| The Brood | Broodmother Vexis (58) | |
| The Bubbler Pools | The Glow-Eater (58) | The pools under Reactor 4, and the three men who waded into the flooded basement to drain them. |
| The Stacks | Archivist Nine (59) | |
| The Ninety Seconds | The Stopped Man (59) | The soldiers who cleared the reactor roof by hand, ninety seconds each. |
| The Elephant's Foot | The Wound's Heart (60) | The mass of melted fuel that set in the reactor's basement. Drops the T0 bracers token, always. |

Nothing from Earth is down there. The names are only words, the way people carry home with them.

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
