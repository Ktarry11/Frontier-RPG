# The Plaguelands' dungeons: structure (16 Nov 2026)

Kyle: "carve out the structure and layout of the Dungeons... try to be true to the actual layout", "Dead is two
layers as it's massive. Live is one layer as its smaller", and "Hearthglen can be 2 layers as well". And: "Ensure
multi-layered Dungeons always have a portal after the final boss to teleport the players out of the dungeon. But
ensure these end of dungeon portals are ONE WAY".

**Structure only.** Each map is carved, checked (every door, boss, chest and trash pack can be walked to from the way
in, and every door has floor where you arrive), and drawn. Nothing is wired into the game until Kyle's dungeon tiles
land; then each takes the Scarlet Monastery's path: creatures and kits, loot, a baker, the doors, the fast exit.
Rosters are classic's, past the four-to-six rule, in classic's rooms and order. Trash is fixed packs, padded to four
or five when wired. Levels: Scholomance 56-60, Stratholme 57-60, Hearthglen 58-60.

## Scholomance: two floors (`tools/handbuilt_scholomance.py`)
The door is on Caer Darrow in South WPL. Drops the T0 **head**.

| Floor | Rooms in order | Bosses |
|---|---|---|
| Upper (56-58) | the Reliquary, the Herald's Balcony, the Hall of Secrets, the Chamber of Summoning, the Great Ossuary, the Viewing Room, the Laboratory, the stair down | Kirtonos the Herald, Jandice Barov, Rattlegore, Marduk Blackpool and Vectus, Ras Frostwhisper |
| Lower Halls (58-60) | the stairwell, the Great Hall, the Coven, the Shadow Vault, the Hall of the Damned, the Vault of the Ravenian, the Barov Family Vault, the Headmaster's Study | Instructor Malicia, Doctor Theolen Krastinov, Lorekeeper Polkelt, the Ravenian, Lord Alexei and Lady Illucia Barov, Darkmaster Gandling |

One-way fast exit in Gandling's study, out to Caer Darrow.

## Stratholme: the living side, one floor (`tools/handbuilt_stratholme.py`)
In at the Main Gate in West EPL. Drops the T0 **chest**. Pays the Order of the Pale Flame.

| Room | Boss |
|---|---|
| the Main Gate | Skul |
| King's Square | Hearthsinger Forresten |
| Market Row (and its four shops) | The Unforgiven |
| Crusaders' Square | Timmy the Cruel |
| the Scarlet Bastion: the Hall of the Crimson Legion, then the Hoard | Cannon Master Willey |
| the Archives | Archivist Galford |
| the Hall of High Command | Grand Crusader Dathrohan, who becomes Balnazzar at 40% (the boss phases) |

One floor, so no fast exit: you walk back through the gate.

## Stratholme: the dead side, two floors (`tools/handbuilt_stratholme.py`)
In at the service gate, a second door in West EPL beside the Main Gate. Drops the T0 **chest**. Pays the Argent Dawn.

| Floor | Rooms in order | Bosses |
|---|---|---|
| Service Entrance (58-59) | the Service Entrance, Elders' Square and the Alonsus Chapel, the Gauntlet, three ziggurats off it, the Portcullis | Magistrate Barthilas, Stonespine (walks the Gauntlet), Nerub'enkan, Baroness Anastari, Maleki the Pallid |
| Slaughter Square (59-60) | the Portcullis Yard, Slaughter Square with its houses and abomination pens, the Slaughterhouse | Ramstein the Gorger, Baron Rivendare |

One-way fast exit in the Slaughterhouse past the Baron, out to West EPL.

## Hearthglen: two floors (`tools/handbuilt_hearthglen.py`)
In at the gate at the top of North WPL's road. Drops the T0 **feet**. Pays the Order of the Pale Flame, no cap.
Ten bosses. The layout leaves room for Hearthglen's hidden chain.

| Floor | Rooms in order | Bosses |
|---|---|---|
| Hearthglen, the town (58-59) | the gate; the lower street round the hill to the Kennels and the Infirmary; the upper street back to the Town Square; the Chapel of the Flame; the Barbican | High Protector Tarsen, Huntsman Radley, Chirurgeon Maeve Ostrowski, High Clerist Hendrick, High Protector Lorik |
| Mardenholde Keep (59-60) | the Keep Gate, the Muster Yard, the Armoury and the Barracks off it, the Great Hall, the tower stair, the Tower Top | Scarlet Commander Marjhan, Armsmaster Grell, Drillmaster Osric Pell, High General Abbendis, Grand Crusader Victor Hale |

One-way fast exit on the Tower Top past Hale, out to North WPL.

## Shapes
No two maps share a plan. Scholomance: rooms off a central spine, then a great hall ringed by the masters' rooms.
Stratholme living: squares joined by a market street, then a walled bastion of halls. Stratholme dead: a long street
with three ziggurats off it, then one open square ringed by houses. Hearthglen: a loop of streets round a hill, then
a keep's courtyard with its halls and a tower.

## Shared code
`tools/plaguelands_dungeon_kit.py` carves a floor from its rooms, streets, walls and doors, checks it, and draws a
preview (`python3 tools/handbuilt_stratholme.py --preview DIR`).
