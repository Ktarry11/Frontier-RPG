# Recruit profiles: the four waves

Kyle, 19 Nov 2026: "We go through EACH party member one by one and flesh them out fully as humans. So personality,
hopes, dreams, who they are....what they did where they are....their future goals and how they have changed etc.....
so their background and themselves FIRST." And: "this needs to be done in steps to ensure its excellent."

## The waves

1. **Who they are.** One profile per recruit, in this folder, signed off by Kyle one at a time.
2. **How they act.** Their profile drives what they say and do in dungeons, groups, quests and with each other.
3. **Each other.** Relationships form from personality: two sarcastic people become friends fast, two introverts
   barely talk.
4. **Sworn.** Swearing to the player unlocks a new skill that comes from resolving their trauma, their issues, or just
   wanting to be better. A trump card on a cooldown, or a passive.

Plus a new **Collection tab** for keepsakes: each Sworn member gives one personal item, and it goes there. Kyle has
plans for it later. Built 19 Nov 2026 (`data/npcs/keepsakes.json`, `tools/qa_keepsakes.py`): a keepsake is found
only, given the moment its recruit becomes Sworn, and an ungiven one shows only who it's from. Each needs its own icon
(it shows a stand-in until then).

## Each profile has

At a glance; who they are; before; the Integration and what it cost; now; hopes, dreams and fears; how they've
changed; their goal and personal quest with both endings; their keepsake; voice notes; seeds for Waves 2 to 4; what
it changes in what's already written; and the calls for Kyle.

Rules that hold for every profile: Earth transplants only; factionless; nobody shares a past with another recruit;
outcomes vary, some better off and some worse; no Earth objects (Deadwind's wheel is the only one); nothing that
hints the player made the wish; plain speech, contractions, no one- or two-word sentences, no dashes in their lines.

## How their stories end

Kyle, 19 Nov 2026: "So we can have ixture of sad and happy for some. aim for a good 50% happy, 35% sad, 15% still
unknown."

Across the 99, the personal quests land roughly **50 happy, 35 sad, 14 still unknown**. Any single ending can still
be bittersweet: a happy one can cost something, and a sad one can leave them better off.
- **Happy:** they get what they were after, or something close enough to live with.
- **Sad:** they find out, and it's bad.
- **Still unknown:** the quest ends with no answer. The trail goes cold, or the answer is somewhere nobody can reach.
  They make peace with not knowing, and that's what makes them Sworn.

The Ending column below keeps the count honest as we go.

## Order and progress

The pilot three first, then everyone else from the lowest level up.

| # | Recruit | Class | Where | Profile | Ending | Status |
|---|---|---|---|---|---|---|
| 1 | Kesten Ambrose | Runemaster 36 | Kael's Bastion | `kesten_ambrose.md` | Happy | Signed off 19 Nov 2026 |
| 2 | Adrián Mendoza | Templar 24 | Astranaar | `adrian_mendoza.md` | Happy (pilot) | Draft 1, waiting on Kyle |
| 3 | Tarek Mansour | Templar 26 | Ashenvale East |  | Sad (pilot) |  |
| 4 | Asher | Paladin 5 | Burning Blade Coven |  |  |  |
| 5 | Diego Salazar | Tinker 5 | Deathknell |  |  |  |
| 6 | Freja Lindqvist | Priest 6 | Valley of Trials |  |  |  |
| 7 | Ama Boateng | Priest 7 | Razor Hill |  |  |  |
| 8 | Marcus Okafor | Stormbringer 8 | Durotar |  |  |  |
| 9 | Sondre Haugen | Stormbringer 8 | Scarlet Crypt |  |  |  |
| 10 | Sebastián Cruz | Bloodmage 8 | Western Tirisfal |  |  |  |
| 11 | Marco Rossi | Paladin 10 | Undercity |  |  |  |
| 12 | Sophia Dias | Mage 11 | Undercity |  |  |  |
| 13 | Carolina Santos | Shaman 11 | Echo Isles |  |  |  |
| 14 | Ryan Murphy | Warlock 12 | Echo Isles |  |  |  |
| 15 | Hana Tamihana | Shaman 12 | Western Hillsbrad |  |  |  |
| 16 | Esteban Ruiz | Bloodmage 12 | Orgrimmar |  |  |  |
| 17 | Berat Yilmaz | Tinker 12 | Brill |  |  |  |
| 18 | Dan Okafor | Warrior 13 | Orgrimmar |  |  |  |
| 19 | Marisol Quintero | Priest 13 | Silverpine North |  |  |  |
| 20 | Silas Vance | Rogue 14 | Ratchet |  |  |  |
| 21 | Rosa Delgado | Hunter 14 | Central Barrens |  |  |  |
| 22 | Pavlo Hryn | Knight of Xoroth 14 | Silverpine North |  |  |  |
| 23 | Amber Whitehorse | Druid 15 | Central Barrens |  |  |  |
| 24 | Ivan Petrov | Warrior 15 | Ragefire Chasm |  |  |  |
| 25 | Haruto Nakamura | Runemaster 15 | Silverpine South |  |  |  |
| 26 | Marta Kowalski | Tinker 15 | Boulder Lode Mine |  |  |  |
| 27 | Lúcia Ferreira | Sun Cleric 15 | Crossroads |  |  |  |
| 28 | Minh Tran | Chronomancer 16 | Northern Barrens |  |  |  |
| 29 | Bakyt Asanov | Hunter 17 | Eastern Hillsbrad |  |  |  |
| 30 | Matías Fuentes | Reaper 17 | Sunken Grotto of the Deep |  |  |  |
| 31 | Tomas Havel | Warrior 18 | Fenris Isle |  |  |  |
| 32 | Cristóbal Muñoz | Knight of Xoroth 19 | Camp Taurajo |  |  |  |
| 33 | Callum Reid | Venomancer 20 | Southern Barrens |  |  |  |
| 34 | Giorgi Beridze | Primalist 21 | Tarren Mill |  |  |  |
| 35 | Camille Roussel | Ranger 22 | Wailing Caverns |  |  |  |
| 36 | Liam Hartigan | Sun Cleric 23 | Ashenvale East |  |  |  |
| 37 | Orlando Rivera | Witch Doctor 23 | Shadowpine Altar |  |  |  |
| 38 | Owen Pryce | Cultist 24 | Azurelode Mine |  |  |  |
| 39 | Anjali Nair | Druid 24 | Ashenvale West |  |  |  |
| 40 | Emre Kaya | Rogue 25 | Eastern Hillsbrad |  |  |  |
| 41 | Saoirse Ni Bhraonain | Starcaller 25 | Shadowfang Keep |  |  |  |
| 42 | Pasang Lama | Primalist 27 | The Aspen Wilderness |  |  |  |
| 43 | Nicolás Arce | Bloodmage 27 | Splintertree Post |  |  |  |
| 44 | Iker Etxeberria | Guardian 30 | Arathi West |  |  |  |
| 45 | Mateo Rojas | Starcaller 31 | Southern Thousand Needles |  |  |  |
| 46 | Imelda Salonga | Primalist 31 | Freewind Post |  |  |  |
| 47 | Ileana Dragomir | Necromancer 31 | Plague Depths |  |  |  |
| 48 | Rhys Morgan | Ranger 31 | Stonetalon West |  |  |  |
| 49 | Henrik Dahl | Mage 32 | The Frostward Descent |  |  |  |
| 50 | Eino Virtanen | Barbarian 32 | Northern Stranglethorn |  |  |  |
| 51 | Driss Alaoui | Shaman 32 | Freewind Post |  |  |  |
| 52 | Thiago Macedo | Paladin 33 | Grom'gol |  |  |  |
| 53 | Jun-seo Park | Reaper 34 | Central Stranglethorn |  |  |  |
| 54 | Skye Donnelly | Pyromancer 34 | The Drowning Floor |  |  |  |
| 55 | Enzo Marchetti | Cultist 34 | Scarlet Monastery Grounds |  |  |  |
| 56 | Alonso Vega | Pyromancer 35 | Central Stranglethorn |  |  |  |
| 57 | Vuk Jovanović | Knight of Xoroth 35 | Rocky Pass |  |  |  |
| 58 | Gunnar Sigurðsson | Barbarian 35 | Hammerfall |  |  |  |
| 59 | Kourosh Behzadi | Mage 36 | The Crystalline Underdark |  |  |  |
| 60 | Héctor Salinas | Witch Doctor 36 | Gurbashi Arena |  |  |  |
| 61 | Ziad Haddad | Felsworn 38 | Southern Stranglethorn |  |  |  |
| 62 | Ratih Pranoto | Ranger 38 | The Shimmering Flats |  |  |  |
| 63 | Fiona Strachan | Witch Hunter 39 | Southern Stranglethorn |  |  |  |
| 64 | Khalid Al Suwaidi | Hunter 39 | Saltwheel |  |  |  |
| 65 | Delroy Beckford | Witch Doctor 40 | Booty Bay |  |  |  |
| 66 | Karim Haddad | Felsworn 40 | The Undercrust |  |  |  |
| 67 | Osvaldo Beltrán | Warlock 40 | The Bloodsail Raider |  |  |  |
| 68 | Bashir Khalidi | Witch Hunter 41 | The Drowned Shrine |  |  |  |
| 69 | Pieter Malan | Guardian 42 | Northern Tanaris |  |  |  |
| 70 | Gianluca Ferri | Guardian 42 | Steamwheedle Port |  |  |  |
| 71 | Camila Ortega | Venomancer 43 | Northern Tanaris |  |  |  |
| 72 | Elias Peralta | Sun Cleric 44 | The Drownbell |  |  |  |
| 73 | Kiet Somsak | Rogue 46 | The Abyssal Sands |  |  |  |
| 74 | Rui Almeida | Cultist 46 | The Lashings |  |  |  |
| 75 | Stelios Dukas | Necromancer 48 | Glittervein |  |  |  |
| 76 | Nizar Haddad | Chronomancer 48 | The Crossing |  |  |  |
| 77 | Yusuf Al-Rawi | Venomancer 48 | The Bloodsail Anchorage |  |  |  |
| 78 | Réka Farkas | Necromancer 51 | The Black Strand |  |  |  |
| 79 | Ramiro Quispe | Primalist 51 | Onyxhollow |  |  |  |
| 80 | Graham Ashworth | Warlock 52 | The Pale Watch |  |  |  |
| 81 | Elie Khoury | Bloodmage 53 | Khaz Varun, the Black Hollow |  |  |  |
| 82 | Bruno Teixeira | Templar 53 | The Bulwark |  |  |  |
| 83 | Joaquín Duarte | Sun Cleric 54 | The Bulwark |  |  |  |
| 84 | Astrid Lindqvist | Starcaller 54 | North Felwood |  |  |  |
| 85 | Luka Perić | Stormbringer 54 | Tempest Shallows |  |  |  |
| 86 | Zofia Nowak | Cultist 55 | Western Plaguelands North |  |  |  |
| 87 | Omar Saleh | Venomancer 55 | The Royal Hive |  |  |  |
| 88 | Santiago Ríos | Runemaster 56 | The Ashen Reach |  |  |  |
| 89 | Emiliano Vargas | Pyromancer 56 | Cinderwharf |  |  |  |
| 90 | Mohammed Saleh | Chronomancer 56 | Talrendis Landing |  |  |  |
| 91 | Tobias Keller | Paladin 56 | Light's Hope Chapel |  |  |  |
| 92 | Isla Fraser | Witch Hunter 57 | Light's Hope Chapel |  |  |  |
| 93 | Taras Kovalenko | Witch Hunter 57 | Ariden's Watch |  |  |  |
| 94 | Mariana Treviño | Priest 57 | Ariden's Watch |  |  |  |
| 95 | Dale Brekke | Reaper 58 | Eastern Plaguelands East |  |  |  |
| 96 | Wes Dahlberg | Warrior 58 | Ariden's Watch |  |  |  |
| 97 | Neil Hartley | Felsworn 58 | Ariden's Watch |  |  |  |
| 98 | Valentina Soto | Starcaller 58 | Moonglade |  |  |  |
| 99 | Faris Al-Tamimi | Shaman 58 | Moonglade |  |  |  |
