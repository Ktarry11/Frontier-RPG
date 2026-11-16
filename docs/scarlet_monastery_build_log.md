# The Scarlet Monastery: build log

Kyle, 16 Nov 2026: "So can you also make SM with the 4 different dungeons? The layout etc."

Design and levels are in docs/plaguelands_design.md (Plan A: Graveyard 28-32, Library 32-36, Armory 35-39, Cathedral
38-42). No keys. Scarlet kills inside pay the Order of the Pale Flame, capped at Honored.

## Files

| What | Where |
|---|---|
| Maps (grounds and four wings), layout notes per boss | tools/handbuilt_scarlet_monastery.py |
| Bake (floors and walls) | tools/bake_scarlet_monastery.py, assets/tiles/scarlet_monastery/baked_* |
| Creatures, kits, encounter tables, zone levels, boss loot | tools/build_scarlet_monastery_content.py |
| Boss loot | data/loot/scarlet_monastery_boss_loot.json |
| Faction rep (Pale Flame) | tools/build_plaguelands_factions.py |
| Named epics on the four last bosses | tools/epic_table.py, data/loot/epic_drops.json |
| Sprites | creature_sprites.py (exact names, existing art until Kyle's Scarlet sheets) |
| Chests and fight backdrops | world/chest_looks.py, world/combat_backgrounds.py |
| Wiring | world/zone_generator.py, world/portal_manager.py, world/zone_classification.py, world/portal_art.py |
| QA | tools/qa_scarlet_monastery.py |

## The maps

- **Scarlet Monastery Grounds** (64x52): the walled close behind the barred gate in Eastern Tirisfal. No monsters.
  The Graveyard is down through a crypt chapel in the cemetery on the west side. The Library, Armory and Cathedral
  are three houses against the north wall, each over its own door: a chapel, a gatehouse and the Cathedral's front.
  The way in from Eastern Tirisfal is the gate at the top of the monastery road.
- **The wings follow WoW's.** Kyle, after the first pass: "cathedral has a courtyard THEN cathedral!" and "Look up
  authentic-style WoW dungeons for this bro". Each wing walks in the classic order and its rooms carry the classic
  names (warcraft.wiki.gg's subzone lists, the classic guides for who stands where):
  - **Graveyard** (100x84): the Penitents' Hall, the Chamber of Atonement (Maelis's torture room), the Forlorn
    Cloister (an open-air burial ground, rows of graves round a mausoleum, the Fallen Champion behind it, Azshir among
    the graves), Honor's Tomb (Thalnos at the altar).
  - **Library** (110x96): the Scriptorium, long halls that turn west and then north past the Hall of Judgement
    (Vellan Rook), Huntsman's Cloister (Loksey and
    his kennels round a square of lawn), the Closed Stacks off the north hall (Mercer), the Gallery of Treasures (a
    long passage with alcoves, Halbrecht), the Athenaeum (Doan among the shelves).
  - **Armory** (110x90): the Gate Hall, the Training Grounds (an open dirt yard with dummies and targets, Brennan
    drilling his recruits), the Footman's Armory (Ellison), the Crusader's Armory (Pike) with the Armory Forge off its north wall (Bellweather),
    the Hall of Champions (Herod).
  - **Cathedral** (120x110): the Chapel Gardens first, open air, grass with cobbled walks crossing at the fountain (Thorne tends it),
    statues, pines and willows, and the fountain at its centre; then up the wide steps past Captain Stane into the Crusader's Chapel, columns down both aisles and
    Brother Ashe preaching mid-nave; the Chancel at the far end (Whitemane and Mograine at the altar); the
    Inquisitor's Cell off the east aisle (Aldric).
- Rooms are chamfered rectangles joined by corridors, because a monastery is built, not dug. Each wing has a few side
  cells with a chest. The columns are a stone-grey recolour of the shared temple column (its own was sea-green).
- Trash is in packs, padded to four or five (world/dungeon_packs.attach_packs).
- Each wing is one map, so none of them is a multi-tiered dungeon and none needs a fast exit. Walking back out to
  the grounds is short.

### The bake

Floors are seamless copies of Kyle's Plaguelands ground tiles plus Tirisfal's dead grass, grave gravel and old
cobble for the open-air parts: mossy flags and cracked slabs in the Graveyard's halls and tomb, grass and gravel walks
in its cloister; Light's Hope stone and keep floor in the Library with grass in the cloister; keep floor and a dirt
yard in the Armory; Andorhal paving and a pale chancel in the Cathedral, its gardens grass with cobbled walks. An
open-air room is ground from wall to wall (`_open`), and a walk across a lawn wins over it (`floor_weight`, a new
optional key in tools/bake_durotar_caves.py; every other bake is unchanged). **No repeating motifs** (Kyle, on the first Cathedral: "Avoid
tiles where they look like that in cathedral... having a repeating pattern like that looks weird"): the monastery
floor's flame emblem, the Scarlet flagstones' diamonds and the runner's stripes all tiled into wallpaper, so none of
them is used. His tiles carry a dark rim along the top
and bottom edge that tiled into a stripe every few metres, so the bake crops the rim and blends the edges once
(`_sl` in the bake script, saved beside the other shared interior materials). Walls are the shared keep and crypt
stone.

## Who is where

Five encounters a wing (Kyle: "Lets aim for about 4-6 bosses per dungeon... this will help with the weird ass 2
bosses per wing that classic suffers from", and "We can also take some creative liberties with bosses"). Classic's
own where it has them, new ones where it doesn't. Trash is fixed, in packs of four or five.

| Wing | Boss | Level | Role | What the fight asks |
|---|---|---|---|---|
| Graveyard | Interrogator Maelis | 30 | required | burns and breaks: cleanse the brand, heal through |
| Graveyard | Ironspine | 31 | optional | classic's third rare, a giant of bone: poison and bone armour |
| Graveyard | Azshir the Sleepless | 31 | required | a wraith among the graves that drains and wails: spread out |
| Graveyard | The Fallen Champion | 31 | optional | behind the mausoleum; hits harder at two thirds and again at a third |
| Graveyard | Bloodmage Thalnos | 32 | last | spells feed his ward: hit him with steel |
| Library | Inquisitor Vellan Rook (new) | 33 | required | marks a heretic and judges him: heal the mark |
| Library | Houndmaster Loksey | 34 | required | his hounds first, or he licks his wounds |
| Library | Archivist Dana Mercer | 35 | optional | an Earth transplant; shuts casters down, so melee carries her |
| Library | Curator Halbrecht (new) | 35 | required | calls the gallery's monks to him: kill them first |
| Library | Arcanist Doan | 36 | last | detonates at the brink: get away from him |
| Armory | Sergeant Major Cole Brennan | 36 | required | an Earth transplant drill instructor; his recruits come in waves |
| Armory | Quartermaster Bram Ellison | 37 | required | armour and spare plate you have to cut through |
| Armory | Smithmaster Corra Bellweather (new) | 37 | optional | the forge: slag that burns the whole party, plate she tempers |
| Armory | Master-at-Arms Dorran Pike (new) | 38 | required | parries steel back at melee: casters carry it |
| Armory | Herod | 39 | last | whirlwinds, a hard enrage: the party moves |
| Cathedral | Brother Garrick Thorne (new) | 39 | required | the gardener by the fountain: thorns back at melee, roots, poison |
| Cathedral | Captain Elric Stane (new) | 40 | required | the chapel doors: calls his centurions, shield wall |
| Cathedral | High Inquisitor Aldric | 40 | optional | a corpse that will not stay dead (gets up once) |
| Cathedral | Brother Corwin Ashe | 41 | required | an Earth transplant; his sermon shields him |
| Cathedral | High Inquisitor Whitemane and Scarlet Commander Mograine | 42 | last, one fight | he holds the front and gets back up once; she mends herself and puts people to sleep |

Two names changed from the first draft because they were already taken: Vishas and Fairbanks are the Scarlet Crypt's
bosses in Tirisfal. Names never repeat.

Trash: Graveyard (Scarlet Torturer, Scarlet Scryer, Haunting Phantasm, Anguished Dead, Unfettered Spirit), Library
(Scarlet Adept, Gallant, Beastmaster, Tracking Hound, Monk), Armory (Scarlet Trainee, Soldier, Myrmidon, Defender,
Evoker), Cathedral (Scarlet Centurion, Sorcerer, Champion, Wizard, Abbot, and the Monks again).

## The numbers

Read off the game's own 28-44 dungeon kits (medians, 16 Nov 2026), so the Monastery sits with Plague Depths, Grom's
Rest, Razorfen Kraul and Stromgarde rather than above them:

- boss basic attack `10 * level - 40` (272 / 324 / 373 measured at 30 / 36 / 42)
- trash basic attack `4 * level - 10` (100 / 139 / 162 measured)
- boss health multiplier 2.3 optional, 2.5 required, 2.8 a wing's last; Whitemane 2.4 and Mograine 2.3
- plain dungeon bosses for world/difficulty.py (3x and 3x), like the rest of the band

An unused level 8 kit called "scarlet_defender" sat in tools/monster_kits.py with no creature. It's gone, because a
regeneration would have put it back over the Armory's Scarlet Defender.

## Loot

- Three items per boss, one drops a kill. Item level is the boss's level plus three.
- Whitemane and Mograine share nine and drop three (entities/boss_loot.py MULTI_DROP and SHARED_HOARD).
- 66 items: armour 10 leather, 10 cloth, 9 mail, 9 plate, plus 8 jewellery and trinkets; thirteen weapon types, none
  more than four times; every stat template covered. Three trinkets, each with a proc.
- Stats from the real formulas; the eight that fell outside the item curve's band were put on it.

### Epics

- Thalnos, Doan and Herod roll the shared 30s pool at 2%, like the other 30-39 last bosses.
- Whitemane rolls 5% for one of her own two: **Whitemane's Book of Hours** (off-hand tome, healer) and **The Scarlet
  Commander's Breastplate** (plate chest, strength). Both icons are new from Kyle's pack and used by nothing else.

## Reputation

The Order of the Pale Flame: every boss in the four wings pays 75, and every Scarlet trash kill pays 10, all of it
stopping at Honored. The dead in the Graveyard pay nothing.

## Every boss has something dangerous

Kyle: "make sure bosses are not just debuffing. they should have something dangerous". A boss never spends a turn on a
plain debuff while it has an attack ready (`Monster.choose_action`), so a debuff on its own was a dead slot. Every
debuff now rides on a hit, and every boss carries a SIGNATURE: a hit near twice its basic, a blast across the party, a
stun with a hammer behind it, a curse that kills unless it's cleansed, or a once-only nuke at low health.
`tools/audit_boss_turns.py` fights each boss turn by turn; the Monastery's QA fails if one is passive or toothless.

Game-wide, the same audit found 523 bosses: 35 passive, 339 toothless (80 of them dungeon bosses). That pass is queued.

## Quests (`tools/scarlet_monastery_quests.py`, `tools/build_scarlet_monastery_quests.py`)

Nineteen, given in town, never at the door (Kyle: "We need quests pointing towards SM", "You can have some SM quests
from kalimdor too", "I want more links between EK and Kalimdor"):
- **Brill:** Flamewarden Teodor Novak (new: the Pale Flame's man watching the Monastery, a Brno firefighter before the
  Integration). His chain runs one quest a wing (a captured scout, the archivist's ledger of names, the smith's
  notebook, the captain who burned a transplant camp) and ends at Sorrow Hill at 50, handing Stane's signet to Rory.
  Gravedigger Hollis wants the Monastery's dead laid down.
- **The Undercity:** Deathstalker Rhyne (Herod, then Whitemane and Mograine), Master Apothecary Sable (Thalnos's
  bloodstone), Loremaster Sennarath (Doan's codex), Apothecary Marwen (the Crusade's zeal).
- **Tarren Mill:** Commander Thorne (Brennan's recruits), Scout Vask (Loksey's hounds), Chaplain Blackwood (Ashe).
- **Kalimdor:** Merrow Vane at Sun Rock (a letter to Novak), Spirit-Walker Enu at Freewind (Azshir), the warrior
  trainer in Orgrimmar (Pike), Corwin Hale at the Crossroads (his daughter's locket from Halbrecht's gallery).
  Back west: Sennarath sends the codex's chapter on the walking dead to Spiritwalker Tohana at Sun Rock.
- **Who knows what** (Kyle: every transplant knows they're from Earth; ordinary Azerothians don't, and only the people
  at the top know more): natives call transplants newcomers and never say Earth. `qa_quest_lore` now counts
  "newcomer" as touching the Integration.
- 57 rewards; every one of the 97 specs gets at least five it can wear and wants.

## Not done yet

- Kyle's Scarlet art: every creature here wears existing art (Whitemane borrows the red-robed magister for now).
- Dungeon quests in town.
