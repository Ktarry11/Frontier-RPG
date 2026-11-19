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
   wanting to be better. A trump card on a cooldown, or a passive. Kyle, 19 Nov 2026: "no character traits will ever be
   'once per fight' they'll usually have 10-15 turn cooldowns depending on how strong they are". The stronger the
   trait, the longer the cooldown.

Plus a new **Collection tab** for keepsakes: each Sworn member gives one personal item, and it goes there. Kyle has
plans for it later. Built 19 Nov 2026 (`data/npcs/keepsakes.json`, `tools/qa_keepsakes.py`): a keepsake is found
only, given the moment its recruit becomes Sworn, and an ungiven one shows only who it's from. Each needs its own icon
(it shows a stand-in until then).

Where they live is where the game places them (Kyle, 19 Nov 2026: "keep their places and their location accurate").
Every place a profile names is a real place in the game; where the old recruit text named somewhere else, the profile
follows the game and says so.

Keepsakes can be Earth things (Kyle, 19 Nov 2026): "These people came through during integration and some of them
came with things on them. That's fine to have earth themed keepsakes too when appropriate." Deadwind's wheel stays the
only Earth object out in the world.

## Each profile has

At a glance; who they are; before; the Integration and what it cost; now; hopes, dreams and fears; how they've
changed; their goal and personal quest with both endings; their keepsake; voice notes; seeds for Waves 2 to 4; what
it changes in what's already written; and the calls for Kyle.

Rules that hold for every profile: Earth transplants only; factionless; nobody shares a past with another recruit;
outcomes vary, some better off and some worse; nothing that
hints the player made the wish; plain speech, contractions, no one- or two-word sentences, no dashes in their lines.

## How their stories end

Kyle, 19 Nov 2026: "So we can have ixture of sad and happy for some. aim for a good 50% happy, 35% sad, 15% still
unknown."

Wave 1 is drafted: across the 98 profiles (Asher untouched), the personal quests land **49 happy, 34 sad, 15 still unknown**. Any single ending can still
be bittersweet: a happy one can cost something, and a sad one can leave them better off.
- **Happy:** they get what they were after, or something close enough to live with.
- **Sad:** they find out, and it's bad.
- **Still unknown:** the quest ends with no answer. The trail goes cold, or the answer is somewhere nobody can reach.
  They make peace with not knowing, and that's what makes them Sworn.

The Ending column below keeps the count honest as we go.

## Who they love

Kyle, 19 Nov 2026: "make about 10% of the males recruits gay or bisexual please. only 2 females are lesbians. 1
bisexual female --- BUT DONT DO IT HEAVY HANDED - THEYRE NOT GAY CHARACTERS, THEYRE CHARACTERS WHO HAPPEN TO BE GAY!
big difference."

So about 7 or 8 of the 74 men, and 3 of the 25 women. It comes up the way anyone's partner comes up: a name, a past,
somebody they miss. It's never their story or their personality.

Kept count here as we go: men gay or bisexual: Tarek (gay), Sondre (gay), Sebastián (bisexual), Haruto (gay), Tomas (bisexual, already in his recruit text), Orlando (gay), Iker (gay). Women: Carolina (lesbian), Rosa (bisexual), Camille (lesbian). That's the women done.

## Wave 2: how they act (started 19 Nov 2026)

Each recruit's profile becomes one file, `tools/wave2/<recruit_id>.json`, with three blocks:

- **bond**: their friendship record in the system the pilot three already use. Personality dials
  (warmth, nerve, pride, restless), likes and dislikes, what they tell you at each of the five
  stages, the few moments where your reply matters, and the lines that name a cause (bored,
  leaving, wipes, a zone too high, gear, coming back, the talk after a walkout, teasing after
  neglect). What they won't talk about until a stage follows their profile's voice notes. Sworn is
  their ending.
- **banter**: what they say in the party when something happens. It never names another recruit,
  because they start as strangers. Wave 3 is where they meet.
- **recruit_text**: only the parts of their old game text that the profile changed, including
  every "moved to match the game".

`tools/wave2_text.py` checks every file (voice, no names, nothing missing, section length), and
`tools/qa_recruit_bonds.py` fails if any file is wrong or doesn't load. Kesten, Adrián and Tarek
stay in `tools/build_recruit_bonds.py` as the pilot. Asher is never touched.

Profiles corrected during Wave 2 (all mirrored to the project): `haruto_nakamura.md` (Hrunn from Thousand Needles), `matias_fuentes.md` (brother Benjamín), `nicolas_arce.md` (partner Gladys Huamán), `driss_alaoui.md` (son Hamza), Sophia's Wouter and Hana's Ashenvale coast.

**Wave 2 done:** Diego, Freja, Ama, Marcus, Sondre, Sebastián, Marco, Sophia, Carolina, Ryan, Hana, Esteban, Berat, Dan, Marisol, Silas, Rosa, Pavlo, Amber, Ivan, Haruto, Marta, Lúcia, Minh, Bakyt, Matías, Tomas, Cristóbal, Callum, Giorgi, Camille, Liam, Orlando, Owen, Anjali, Emre, Saoirse, Pasang, Nicolás, Iker, Mateo, Imelda, Ileana, Rhys, Henrik, Eino, Driss, Thiago, Jun-seo, Skye, Enzo, Alonso, Vuk, Gunnar, Kourosh, Héctor, Ziad, Ratih, Fiona, Khalid, Delroy, Karim, Osvaldo, Bashir, Pieter, Gianluca, Camila, Elias, Kiet, Rui, Stelios, Nizar, Yusuf, Réka, Ramiro, Graham, Elie, Bruno, Joaquín, Astrid, Luka, Zofia, Sherif, Santiago, Emiliano, Mohammed, Tobias, Isla, Taras, Mariana, Dale, Wes, Neil, Valentina, Faris.

**Wave 2 complete, 19 Nov 2026:** all 95 recruits (98 profiles less the pilot three and Asher).

**Realism pass (Kyle: "These are real people").** Read back to back, the first files shared skeletons that no single line showed: hometown banter written as postcards, "Everybody out, everybody counted", every goodbye opening "I'm going back to", every return opening "I'm back, and", and half the cast telling you where they landed with one sentence shape. All of it was rewritten line type by line type across the whole cast, so each person sounds like themselves. `tools/wave2_text.py` now also fails on stock phrases, the "it's not X, it's Y" line, any four words that three recruits' banter shares or eight recruits' bond lines share, and any line type where four recruits open with the same three words.

## Order and progress

The pilot three first, then everyone else from the lowest level up, unless Kyle picks someone (he picked Freja
fourth).

| # | Recruit | Class | Where | Profile | Ending | Status |
|---|---|---|---|---|---|---|
| 1 | Kesten Ambrose | Runemaster 36 | Kael's Bastion | `kesten_ambrose.md` | Happy | Signed off 19 Nov 2026 |
| 2 | Adrián Mendoza | Templar 24 | Astranaar | `adrian_mendoza.md` | Happy | Signed off 19 Nov 2026 |
| 3 | Tarek Mansour | Templar 26 | Ashenvale East | `tarek_mansour.md` | Sad | Signed off 19 Nov 2026 |
| 4 | Asher | Paladin 5 | Burning Blade Coven | Not touched | | Kyle: "DONT TOUCH ASHER" |
| 5 | Diego Salazar | Tinker 5 | Deathknell | `diego_salazar.md` | Happy | Draft 1 |
| 6 | Freja Lindqvist | Priest 6 | Valley of Trials | `freja_lindqvist.md` | Happy | Signed off 19 Nov 2026 |
| 7 | Ama Boateng | Priest 7 | Razor Hill | `ama_boateng.md` | Happy | Draft 1 |
| 8 | Marcus Okafor | Stormbringer 8 | Durotar | `marcus_okafor.md` | Sad | Draft 1 |
| 9 | Sondre Haugen | Stormbringer 8 | Scarlet Crypt | `sondre_haugen.md` | Sad | Draft 1 |
| 10 | Sebastián Cruz | Bloodmage 8 | Western Tirisfal | `sebastian_cruz.md` | Still unknown | Draft 1 |
| 11 | Marco Rossi | Paladin 10 | Undercity | `marco_rossi.md` | Happy | Draft 1 |
| 12 | Sophia Dias | Mage 11 | Undercity | `sophia_dias.md` | Sad | Draft 1 |
| 13 | Carolina Santos | Shaman 11 | Echo Isles | `carolina_santos.md` | Happy | Draft 1 |
| 14 | Ryan Murphy | Warlock 12 | Echo Isles | `ryan_murphy.md` | Sad | Draft 1 |
| 15 | Hana Tamihana | Shaman 12 | Western Hillsbrad | `hana_tamihana.md` | Still unknown | Draft 1 |
| 16 | Esteban Ruiz | Bloodmage 12 | Orgrimmar | `esteban_ruiz.md` | Happy | Draft 1 |
| 17 | Berat Yilmaz | Tinker 12 | Brill | `berat_yilmaz.md` | Happy | Draft 1 |
| 18 | Dan Okafor | Warrior 13 | Orgrimmar | `dan_okafor.md` | Still unknown | Draft 1 |
| 19 | Marisol Quintero | Priest 13 | Silverpine North | `marisol_quintero.md` | Sad | Draft 1 |
| 20 | Silas Vance | Rogue 14 | Ratchet | `silas_vance.md` | Happy | Draft 1 |
| 21 | Rosa Delgado | Hunter 14 | Central Barrens | `rosa_delgado.md` | Happy | Draft 1 |
| 22 | Pavlo Hryn | Knight of Xoroth 14 | Silverpine North | `pavlo_hryn.md` | Sad | Draft 1 |
| 23 | Amber Whitehorse | Druid 15 | Central Barrens | `amber_whitehorse.md` | Happy | Draft 1 |
| 24 | Ivan Petrov | Warrior 15 | Ragefire Chasm | `ivan_petrov.md` | Happy | Draft 1 |
| 25 | Haruto Nakamura | Runemaster 15 | Silverpine South | `haruto_nakamura.md` | Sad | Draft 1 |
| 26 | Marta Kowalski | Tinker 15 | Boulder Lode Mine | `marta_kowalski.md` | Still unknown | Draft 1 |
| 27 | Lúcia Ferreira | Sun Cleric 15 | Crossroads | `lucia_ferreira.md` | Happy | Draft 1 |
| 28 | Minh Tran | Chronomancer 16 | Northern Barrens | `minh_tran.md` | Sad | Draft 1 |
| 29 | Bakyt Asanov | Hunter 17 | Eastern Hillsbrad | `bakyt_asanov.md` | Happy | Draft 1 |
| 30 | Matías Fuentes | Reaper 17 | Sunken Grotto of the Deep | `matias_fuentes.md` | Sad | Draft 1 |
| 31 | Tomas Havel | Warrior 18 | Fenris Isle | `tomas_havel.md` | Happy | Draft 1 |
| 32 | Cristóbal Muñoz | Knight of Xoroth 19 | Camp Taurajo | `cristobal_munoz.md` | Happy | Draft 1 |
| 33 | Callum Reid | Venomancer 20 | Southern Barrens | `callum_reid.md` | Sad | Draft 1 |
| 34 | Giorgi Beridze | Primalist 21 | Tarren Mill | `giorgi_beridze.md` | Still unknown | Draft 1 |
| 35 | Camille Roussel | Ranger 22 | Wailing Caverns | `camille_roussel.md` | Happy | Draft 1 |
| 36 | Liam Hartigan | Sun Cleric 23 | Ashenvale East | `liam_hartigan.md` | Happy | Draft 1 |
| 37 | Orlando Rivera | Witch Doctor 23 | Shadowpine Altar | `orlando_rivera.md` | Sad | Draft 1 |
| 38 | Owen Pryce | Cultist 24 | Azurelode Mine | `owen_pryce.md` | Sad | Draft 1 |
| 39 | Anjali Nair | Druid 24 | Ashenvale West | `anjali_nair.md` | Happy | Draft 1 |
| 40 | Emre Kaya | Rogue 25 | Eastern Hillsbrad | `emre_kaya.md` | Still unknown | Draft 1 |
| 41 | Saoirse Ni Bhraonain | Starcaller 25 | Shadowfang Keep | `saoirse_ni_bhraonain.md` | Happy | Draft 1 |
| 42 | Pasang Lama | Primalist 27 | The Aspen Wilderness | `pasang_lama.md` | Sad | Draft 1 |
| 43 | Nicolás Arce | Bloodmage 27 | Splintertree Post | `nicolas_arce.md` | Happy | Draft 1 |
| 44 | Iker Etxeberria | Guardian 30 | Arathi West | `iker_etxeberria.md` | Still unknown | Draft 1 |
| 45 | Mateo Rojas | Starcaller 31 | Southern Thousand Needles | `mateo_rojas.md` | Happy | Draft 1 |
| 46 | Imelda Salonga | Primalist 31 | Freewind Post | `imelda_salonga.md` | Sad | Draft 1 |
| 47 | Ileana Dragomir | Necromancer 31 | Plague Depths | `ileana_dragomir.md` | Happy | Draft 1 |
| 48 | Rhys Morgan | Ranger 31 | Stonetalon West | `rhys_morgan.md` | Still unknown | Draft 1 |
| 49 | Henrik Dahl | Mage 32 | The Frostward Descent | `henrik_dahl.md` | Sad | Draft 1 |
| 50 | Eino Virtanen | Barbarian 32 | Northern Stranglethorn | `eino_virtanen.md` | Happy | Draft 1 |
| 51 | Driss Alaoui | Shaman 32 | Freewind Post | `driss_alaoui.md` | Happy | Draft 1 |
| 52 | Thiago Macedo | Paladin 33 | Grom'gol | `thiago_macedo.md` | Sad | Draft 1 |
| 53 | Jun-seo Park | Reaper 34 | Central Stranglethorn | `junseo_park.md` | Still unknown | Draft 1 |
| 54 | Skye Donnelly | Pyromancer 34 | The Drowning Floor | `skye_donnelly.md` | Happy | Draft 1 |
| 55 | Enzo Marchetti | Cultist 34 | Scarlet Monastery Grounds | `enzo_marchetti.md` | Sad | Draft 1 |
| 56 | Alonso Vega | Pyromancer 35 | Central Stranglethorn | `alonso_vega.md` | Sad | Draft 1 |
| 57 | Vuk Jovanović | Knight of Xoroth 35 | Rocky Pass | `vuk_jovanovic.md` | Happy | Draft 1 |
| 58 | Gunnar Sigurðsson | Barbarian 35 | Hammerfall | `gunnar_sigurdsson.md` | Happy | Draft 1 |
| 59 | Kourosh Behzadi | Mage 36 | The Crystalline Underdark | `kourosh_behzadi.md` | Still unknown | Draft 1 |
| 60 | Héctor Salinas | Witch Doctor 36 | Gurbashi Arena | `hector_salinas.md` | Happy | Draft 1 |
| 61 | Ziad Haddad | Felsworn 38 | Southern Stranglethorn | `ziad_haddad.md` | Sad | Draft 1 |
| 62 | Ratih Pranoto | Ranger 38 | The Shimmering Flats | `ratih_pranoto.md` | Happy | Draft 1 |
| 63 | Fiona Strachan | Witch Hunter 39 | Southern Stranglethorn | `fiona_strachan.md` | Sad | Draft 1 |
| 64 | Khalid Al Suwaidi | Hunter 39 | Saltwheel | `khalid_al_suwaidi.md` | Happy | Draft 1 |
| 65 | Delroy Beckford | Witch Doctor 40 | Booty Bay | `delroy_beckford.md` | Happy | Draft 1 |
| 66 | Karim Haddad | Felsworn 40 | The Undercrust | `karim_haddad.md` | Sad | Draft 1 |
| 67 | Osvaldo Beltrán | Warlock 40 | The Bloodsail Raider | `osvaldo_beltran.md` | Happy | Draft 1 |
| 68 | Bashir Khalidi | Witch Hunter 41 | The Drowned Shrine | `bashir_khalidi.md` | Still unknown | Draft 1 |
| 69 | Pieter Malan | Guardian 42 | Northern Tanaris | `pieter_malan.md` | Sad | Draft 1 |
| 70 | Gianluca Ferri | Guardian 42 | Steamwheedle Port | `gianluca_ferri.md` | Happy | Draft 1 |
| 71 | Camila Ortega | Venomancer 43 | Northern Tanaris | `camila_ortega.md` | Happy | Draft 1 |
| 72 | Elias Peralta | Sun Cleric 44 | The Drownbell | `elias_peralta.md` | Sad | Draft 1 |
| 73 | Kiet Somsak | Rogue 46 | The Abyssal Sands | `kiet_somsak.md` | Happy | Draft 1 |
| 74 | Rui Almeida | Cultist 46 | The Lashings | `rui_almeida.md` | Happy | Draft 1 |
| 75 | Stelios Dukas | Necromancer 48 | Glittervein | `stelios_dukas.md` | Still unknown | Draft 1 |
| 76 | Nizar Haddad | Chronomancer 48 | The Crossing | `nizar_haddad.md` | Sad | Draft 1 |
| 77 | Yusuf Al-Rawi | Venomancer 48 | The Bloodsail Anchorage | `yusuf_al_rawi.md` | Happy | Draft 1 |
| 78 | Réka Farkas | Necromancer 51 | The Black Strand | `reka_farkas.md` | Happy | Draft 1 |
| 79 | Ramiro Quispe | Primalist 51 | Onyxhollow | `ramiro_quispe.md` | Sad | Draft 1 |
| 80 | Graham Ashworth | Warlock 52 | The Pale Watch | `graham_ashworth.md` | Happy | Draft 1 |
| 81 | Elie Khoury | Bloodmage 53 | Khaz Varun, the Black Hollow | `elie_khoury.md` | Still unknown | Draft 1 |
| 82 | Bruno Teixeira | Templar 53 | The Bulwark | `bruno_teixeira.md` | Sad | Draft 1 |
| 83 | Joaquín Duarte | Sun Cleric 54 | The Bulwark | `joaquin_duarte.md` | Sad | Draft 1 |
| 84 | Astrid Nyström | Starcaller 54 | North Felwood | `astrid_nystrom.md` | Happy | Draft 1 |
| 85 | Luka Perić | Stormbringer 54 | Tempest Shallows | `luka_peric.md` | Happy | Draft 1 |
| 86 | Zofia Nowak | Cultist 55 | Western Plaguelands North | `zofia_nowak.md` | Sad | Draft 1 |
| 87 | Sherif Gamal | Venomancer 55 | The Royal Hive | `sherif_gamal.md` | Happy | Draft 1 |
| 88 | Santiago Ríos | Runemaster 56 | The Ashen Reach | `santiago_rios.md` | Still unknown | Draft 1 |
| 89 | Emiliano Vargas | Pyromancer 56 | Cinderwharf | `emiliano_vargas.md` | Happy | Draft 1 |
| 90 | Mohammed Saleh | Chronomancer 56 | Talrendis Landing | `mohammed_saleh.md` | Happy | Draft 1 |
| 91 | Tobias Keller | Paladin 56 | Light's Hope Chapel | `tobias_keller.md` | Sad | Draft 1 |
| 92 | Isla Fraser | Witch Hunter 57 | Light's Hope Chapel | `isla_fraser.md` | Sad | Draft 1 |
| 93 | Taras Kovalenko | Witch Hunter 57 | Ariden's Watch | `taras_kovalenko.md` | Still unknown | Draft 1 |
| 94 | Mariana Treviño | Priest 57 | Ariden's Watch | `mariana_trevino.md` | Happy | Draft 1 |
| 95 | Dale Brekke | Reaper 58 | Eastern Plaguelands East | `dale_brekke.md` | Happy | Draft 1 |
| 96 | Wes Dahlberg | Warrior 58 | Ariden's Watch | `wes_dahlberg.md` | Sad | Draft 1 |
| 97 | Neil Hartley | Felsworn 58 | Ariden's Watch | `neil_hartley.md` | Sad | Draft 1 |
| 98 | Valentina Soto | Starcaller 58 | Moonglade | `valentina_soto.md` | Sad | Draft 1 |
| 99 | Faris Al-Tamimi | Shaman 58 | Moonglade | `faris_al_tamimi.md` | Happy | Draft 1 |
