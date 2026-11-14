#!/usr/bin/env python3
"""Nineteen more recruits: 4 tanks, 4 healers, 11 damage. Idempotent.

    PYTHONPATH=. python3 tools/build_wave_two_recruits.py [--check]

Kyle, 29 Oct 2026: "Write about another 19 ... Lets add in another 4 tanks, 4 healers, Kesten is DPS
so another 11 DPS. We can sprinkle some more in throughout new zones."

WHY NINETEEN AND NOT SEVENTY-TWO. Recruits are spec-locked, and 25 of the game's 97 specs had a
recruit, so 72 specs had nobody. The binding constraint is not writing, it is ART: recruit portraits
and sprites are per-character, keyed on recruit_id, sliced from magenta sheets against a hardcoded
24-entry list in tools/asset_pipeline/slice_recruit_sheet.py. Kesten Ambrose already exists with no
portrait and no sprite, so 19 new plus Kesten is 20 characters - one more sheet, with room spare.

WHICH NINETEEN, and the one rule behind the choice: every class that had NO recruit at all now has
one. That was thirteen classes - Reaper, Templar, Witch Hunter, Knight of Xoroth, Chronomancer,
Pyromancer, Witch Doctor, Barbarian, Felsworn, Guardian, Bloodmage, Necromancer, Ranger - and the
remaining six fill obvious spec holes in classes that already had somebody.

EXCLUDED on Kyle's instruction: guardian_vanguard, druid_feral and druid_restoration. "do NOT touch
guardian (tank) druid or resto druid yet." guardian_gladiator is a different spec and is in. Asher
Coleman is untouched, as always.

GENDER: Kyle, same day - "i prefer men. So lets do 80% men and 20% females." 15 male, 4 female.

PLACEMENT is not typed, it is measured. Every (x, y) below was chosen by building the real zone,
flooding from START, and taking a tile that is walkable, reachable, at least three clear of every
existing NPC and vendor, off the outer 8% border, and - in wilderness - close to the road, because a
companion nobody walks past is a companion nobody finds. The towns place near the existing crowd
instead. verify() re-checks all of it rather than trusting these numbers.

THE `look` FIELD is new and is not read by the game. It feeds the art prompts for the next sheet, in
the format of claude/recruit_art_prompts.md: nationality, apparent age, build, hair, face, the
fantasy gear their spec implies, and ONE small object carried over from their old life. That last
detail is the best thing in the existing twenty-four and worth keeping deliberate.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RECRUITS = ROOT / "data/npcs/recruits.json"


def R(rid, name, cls, spec, level, zone, x, y, row, colour, theme, gender, variant,
      look, backstory, greeting, before, adjustment, now, forward,
      home_town=None, home_x=None, home_y=None, home_note=None):
    return {
        "recruit_id": rid, "name": name, "char_class": cls, "spec": spec, "level": level,
        "zone": zone, "x": x, "y": y, "row": row, "npc_color": colour,
        "backstory": backstory, "greeting": greeting, "gear_theme": theme,
        "home_town": home_town, "home_x": home_x, "home_y": home_y, "home_note": home_note,
        "gender": gender, "appearance_variant": variant,
        "background_sections": {"before": before, "adjustment": adjustment,
                                "now": now, "forward": forward},
        "look": look,
    }


NEW = [
    # ------------------------------------------------------------------ TANKS (4)
    R("tarek_templar", "Tarek Mansour", "Templar", "templar_oathkeeper", 31,
      "Northern Stranglethorn", 54, 95, "front", "#C9A227", "tank", "male", 11,
      "Egyptian man in his late 30s, medium height and thickening at the middle, close-cropped "
      "black hair receding at the temples, heavy brows, a careful unhurried face. Dark leather "
      "tank harness over a padded gambeson in sand and oxblood, a broad round shield, a short "
      "heavy blade kept sheathed. A pair of white cotton conservator's gloves folded through his "
      "belt, laundered grey.",
      "Spent eleven years in a Cairo museum basement with a scalpel and a loupe, stabilising "
      "things older than any country. The job was standing between the public and the artefact "
      "and being boring about it. He does the same work now. The artefact is whoever is behind him.",
      "I will take the front. Understand what that means: it means when it goes wrong you do not "
      "come back for me, you finish what you were doing. People get that backwards and then two of "
      "us are on the floor instead of one.",
      "A conservation lab under the Egyptian Museum, eleven years of it. Linen, consolidant, a "
      "scalpel ground thinner than a scalpel should be. He was the man who said no to the "
      "exhibition schedule, which made him unpopular with everyone except the objects.",
      "Three years ago he came through holding a tray he had been carrying down a corridor, and he "
      "set it down very carefully on grass before he looked up. He has said since that the setting "
      "down was the only part he is proud of.",
      "The Vine Road, where the Grom'gol convoys come south and the Stonehand come down off the "
      "crag at them. He stands at the front of whoever is walking. He is unhurried in a way that "
      "reads as calm and is actually just a man who has never once been able to rush.",
      "He wants to see the Zul'Marosh stonework properly, not at a run, with somebody holding a "
      "lamp. He has not asked anyone yet because he knows how it sounds."),

    R("fiona_witchhunter", "Fiona Strachan", "Witch Hunter", "witch_hunter_black_knight", 39,
      "Southern Stranglethorn", 97, 16, "front", "#4F6D7A", "tank", "female", 12,
      "Scottish woman in her mid 40s, tall and square-built, sandy-grey hair cut short and shoved "
      "back, weather-ruined face, pale eyes set deep. Blackened mail over a long coat in slate and "
      "rust, a heavy tower shield slung at her back, a flanged mace at her hip. A yellow offshore "
      "survival-suit whistle still clipped to her collar on a fraying lanyard.",
      "Twenty-two years operating cranes on North Sea platforms - the job of moving something "
      "enormous over the heads of people who trust you, in bad weather, without ever once being "
      "interesting about it. She has the same relationship with a shield. Nobody on the deck "
      "clapped either.",
      "You want me at the front, aye. I have put forty tonnes down on a mark the size of a dinner "
      "plate in a force eight. Standing still while something hits me is not the hard part of my "
      "day and never has been.",
      "A crane cab on a platform a hundred and twenty miles off Aberdeen, twelve hours on, twelve "
      "off, three weeks on the water and three at home. She was good and she was known for it, in "
      "the small way a crane operator is known.",
      "Three years ago she came through mid-lift and spent the first fortnight unable to stop "
      "looking up for a load that was not there. That passed. What did not pass is that she still "
      "counts the people around her before she moves.",
      "The cape road and the drowned terraces below Zul'Kundaraz, where the Saltscale come up out "
      "of water she does not trust. She has made herself the person who goes in first, which the "
      "Bay finds useful and does not pay extra for.",
      "She wants a reason to be somewhere specific rather than wherever the work is, and she has "
      "started saying so out loud, which for her is enormous."),

    R("pavlo_knight", "Pavlo Hryn", "Knight of Xoroth", "knight_of_xoroth_defiance", 37,
      "Booty Bay", 34, 27, "front", "#6B2737", "tank", "male", 13,
      "Ukrainian man in his early 50s, huge through the shoulders and gone soft over it, shaved "
      "head, grey stubble, a nose broken long ago and badly set. Dark iron plate with a black "
      "tabard and a greatshield, faint ember-red light in the seams of the gauntlets. A steel "
      "thermos flask, dented and lidless, strapped where a water flask should go.",
      "Drove long-haul out of Lviv for twenty-six years, mostly alone, mostly at night, across "
      "borders that changed under him more than once. He is not frightened of the dark or of "
      "distance and he is extremely frightened of stopping, which is a thing the Bay has not "
      "noticed and he has no plans to mention.",
      "I stand in front. You do not have to like me and you do not have to talk. The talking is "
      "what people want from a crew and it is the one thing I never learned on the road.",
      "Twenty-six years of cab and road and radio, and a flat in Lviv he was in for maybe sixty "
      "nights a year. A wife for eleven of those years and then not. He knew every bad bend "
      "between Lviv and Rotterdam by the feel of the wheel.",
      "Three years ago he came through and walked for nine days before he spoke to anybody, which "
      "he describes as the most normal nine days he has had since.",
      "The Booty Bay ramp, where the bruisers will not go and the Baron will not pay. He takes the "
      "work nobody wants down a flooded hall, and he is at his best in a place with one way out.",
      "He wants to stop moving and he does not know how to start. He has begun asking what it "
      "costs to keep a room by the month, which is as close as he has come."),

    R("junseo_reaper", "Jun-seo Park", "Reaper", "reaper_domination", 34,
      "Central Stranglethorn", 108, 91, "front", "#3F4756", "tank", "male", 0,
      "South Korean man in his early 40s, wiry and slightly stooped, black hair shot with grey and "
      "flattened by a helmet, a long patient face, deep smile lines he does not use often. Grey-"
      "black mail with a hooded mantle and a scythe-headed polearm carried butt-down. A welder's "
      "flip-up shade, cracked across one lens, pushed up on his forehead.",
      "Nineteen years welding hulls in a Ulsan shipyard, inside compartments that had not been "
      "opened yet, where a man watches the gas meter and his own hands. He is unbothered by "
      "confined dark places and openly puzzled that this is considered a personality.",
      "People hear the spec and expect something from me. A mood, maybe. I welded ships. I am "
      "going to stand where the hit lands and you are going to do your work behind me, and that "
      "is all this is.",
      "A drydock in Ulsan, nineteen years, mostly night shift because the steel moves less when "
      "it is cool. He had two apprentices he liked and one he could not teach, and he still "
      "thinks about the third one.",
      "Three years ago he came through with the shade down and the arc still in his eyes, and he "
      "has said the worst part was how quiet it was.",
      "The arena apron and the Veilfall's dry shoulder, taking the hits for whoever is working. He "
      "has no interest in the drums at all and finds the betting faintly embarrassing.",
      "He wants to teach somebody something properly, start to finish, and have it hold. He has "
      "not found anyone who will stand still long enough."),

    # ------------------------------------------------------------------ HEALERS (4)
    R("minh_chronomancer", "Minh Tran", "Chronomancer", "chronomancer_time", 33,
      "Grom'gol", 31, 30, "back", "#7FD1D9", "healer", "male", 1,
      "Vietnamese man in his late 30s, slight and neat, black hair parted and kept flat, round "
      "wire glasses, an attentive head-tilted way of standing. Pale blue and bone-white robes with "
      "long cuffs and a brass-ringed orrery at the belt, a slim staff with a slow-turning ring at "
      "its head. A tuning fork on a cord round his neck, the tines worn bright.",
      "Tuned pianos in Hanoi for fourteen years, which is a job about hearing the moment a thing "
      "goes wrong a fraction before anyone else does. He heals the same way - a beat early, while "
      "it is still cheap to fix. People find it unnerving and then they find it indispensable.",
      "I will keep you standing. I would rather do it two seconds before you need it than one "
      "second after, so if I move and you did not feel anything yet - that is the job working, not "
      "me wasting your time.",
      "Fourteen years of other people's pianos, in houses and schools and one concert hall that "
      "could not afford him and had him anyway. He could hear a unison go sour through a closed "
      "door and across a courtyard.",
      "Three years ago he came through with a fork in his hand and no piano in the world to use it "
      "on, and he admits the first year was mostly grief for an instrument.",
      "Grom'gol, in the shade by the pens, where he has become the person the camp sends for "
      "before a convoy rather than after one. He still carries the fork and still strikes it when "
      "he is thinking, which the orcs have stopped remarking on.",
      "He wants to hear something built here that is worth tuning. He has been listening to the "
      "Zul'Marosh vinespeakers' knot-cords and suspects they are music, and has told nobody."),

    R("alonso_pyromancer", "Alonso Vega", "Pyromancer", "pyromancer_flameweaving", 35,
      "Central Stranglethorn", 124, 95, "back", "#E07A3F", "healer", "male", 2,
      "Mexican man in his mid 40s, broad and short, thick black hair pushed back off a high "
      "forehead, forearms shiny with old burn scars, a wide easy face. Deep orange and ash-grey "
      "robes cut short at the sleeve for the heat, a censer-headed staff trailing warm light. A "
      "pair of smoked-glass glassblower's goggles hung at his throat.",
      "Blew glass in Guadalajara for twenty years, in a shop where the furnace never went out and "
      "fire was a tool you respected rather than a thing you feared. Healing with it was not a "
      "leap for him. Everyone else finds it a leap.",
      "Yes, it is fire. It was always fire - I spent twenty years keeping something alive at "
      "eleven hundred degrees. Hold still. It will feel like standing too close to an oven and "
      "then it will feel like nothing.",
      "A hot shop off a side street in Guadalajara, his father's before his, three benches and a "
      "furnace they fed in shifts so it never cooled. He made vases nobody needed and one window "
      "for a church that is still there.",
      "Three years ago he came through with a blowpipe and a gather still on the end of it, and he "
      "watched the glass go solid in the grass because there was no annealer in the world any more.",
      "The Veilfall basin and the arena apron, where the burns come in regularly and most healers "
      "flinch at them. He does not flinch at burns. He is also the camp's only source of flat "
      "glass, which he finds funny.",
      "He wants a furnace. He has picked the spot, worked out the clay, and started badgering "
      "Booty Bay about sand, and he is entirely serious about it."),

    R("delroy_witchdoctor", "Delroy Beckford", "Witch Doctor", "witch_doctor_brewing", 40,
      "Booty Bay", 34, 33, "back", "#8FBF5F", "healer", "male", 3,
      "Jamaican man in his early 50s, tall and lean with a slight permanent stoop, grey locs tied "
      "back, a long lined face that goes from grave to delighted with no warning. Leather and "
      "woven-grass healer's gear in moss and bone, a cauldron-bowl slung at the hip and a short "
      "paddle-like stave. A floury canvas apron, folded and tied at the waist, never quite clean.",
      "Ran the night shift in a Kingston bakery for thirty-one years, in from eleven and out at "
      "seven, measuring by hand and feel. A brew is a dough with different patience. He treats a "
      "wounded party exactly like an order going out at dawn: everybody gets something, nobody "
      "waits long, and the complaining is part of the process.",
      "Sit. Drink that. No, I am not telling you what is in it, you would not thank me. Thirty "
      "years I fed a city breakfast and not one of them asked what was in the bread either.",
      "Thirty-one years of nights in a bakery on Spanish Town Road, where he knew the weather by "
      "how the dough behaved and the regulars by what they bought. He has never in his life been "
      "awake at the same hours as everyone else.",
      "Three years ago he came through at four in the morning his time, which is the only reason, "
      "he says, that he was not asleep when it happened.",
      "Booty Bay, on the lower gallery, where the pier work breaks people steadily and the Baron "
      "does not care. He works nights out of habit and has a following among the bruisers, who "
      "pretend not to queue.",
      "He wants an oven and an apprentice, in that order, and has made it clear he will not be "
      "hurried on either."),

    R("imelda_primalist", "Imelda Salonga", "Primalist", "primalist_grovekeeper", 32,
      "Northern Stranglethorn", 58, 106, "front", "#5FA86B", "healer", "female", 4,
      "Filipina woman in her mid 30s, compact and visibly strong through the shoulders, black hair "
      "in a short practical knot, flat nose, a scar through one eyebrow. Mail and green hide cut "
      "for movement, wrapped fists, no shield and no staff at all. A pair of soft hand-wraps from "
      "a boxing gym, washed to grey, rewound every morning.",
      "Sold fish on a Navotas quay from five in the morning and boxed amateur in the evenings, "
      "with a record she describes as honest. Her healing is not gentle and does not look like "
      "healing: she hits things and her people get better, which took the Vine Road about a week "
      "to accept and now nobody questions.",
      "I know how it looks. Stay behind me and watch - when I land one, you will feel it. I never "
      "could explain it in my own language either.",
      "A fish stall and a gym, the same six streets for her whole life, and a mother who thought "
      "the boxing was a phase for nineteen years. She fought at ten fights a year and won more "
      "than she lost.",
      "Three years ago she came through at the market hour with her hands already wrapped, which "
      "she has decided was luck.",
      "The Vine Road and Mistvale Lagoon, where she has become something the convoys ask for by "
      "name without being able to describe. She still wraps her hands before anything else, "
      "including breakfast.",
      "She wants to find out whether there is anybody here who fights properly, with rules and a "
      "count, and she has started asking around the arena about it."),

    # ------------------------------------------------------------------ MELEE DPS (6)
    R("tomas_warrior", "Tomas Havel", "Warrior", "warrior_arms", 30,
      "Northern Stranglethorn", 64, 118, "front", "#A6553F", "melee_dps", "male", 0,
      "Czech man in his early 40s, rangy and long-armed, dark hair cut short, a thin face with a "
      "permanent squint from years of looking up into lights. Battered plate with the pauldrons "
      "stripped off for reach, a two-handed sword worn across the back. A steel carabiner clipped "
      "to his belt loop, scratched to bare metal.",
      "Rigged stages in Prague for eighteen years - up in the grid at four in the morning hanging "
      "weight over people who would never look up. The job was leverage, timing and never being "
      "the reason something fell. He swings a two-hander like a man who has spent his life moving "
      "heavy things through small gaps.",
      "Big sword, lots of room. Tell me where you want me standing before it starts, not during. "
      "I have worked with people who shout during and I did not enjoy any of it.",
      "Eighteen years in the grid, on tour and in houses, and a bad shoulder from a truss in 2014 "
      "that he worked through because the show was that night.",
      "Three years ago he came through forty feet up, which should have killed him, and he has "
      "never managed to make that story sound like anything other than a brag.",
      "The Green Cut and the cutline fork, clearing Stonehand off a road he has decided is his "
      "business. He is early for everything, which he says is not a virtue, just rigging.",
      "He wants to build something that stays up. He has been looking at the Grom'gol palisade "
      "with an expression the orcs find difficult."),

    R("eino_barbarian", "Eino Virtanen", "Barbarian", "barbarian_brutality", 36,
      "Central Stranglethorn", 138, 99, "front", "#8C6239", "melee_dps", "male", 1,
      "Finnish man in his late 30s, enormous and pale, red-blond hair and a thick beard, small "
      "light eyes, a face that gives away nothing. Heavy hide and fur over bare arms, a hand axe "
      "in each fist. A length of orange pipeline marking tape knotted round one bicep, faded to "
      "salmon.",
      "Welded pipeline in Lapland and then in places colder, in two-week rotations, in weather "
      "where a mistake takes a hand off. He talks about as much as the job required, which is "
      "almost not at all, and he fights with both hands because he has never once been able to "
      "pick a favourite.",
      "Two axes. You will not need to tell me twice. If I stop talking it is because there is "
      "nothing to say, not because something is wrong.",
      "Eleven years on pipeline, fourteen days on and fourteen off, and a cabin he built badly on "
      "purpose because he wanted to keep improving it. A brother he phoned every Sunday.",
      "Three years ago he came through in his rotation gear with a flask of coffee that stayed hot "
      "for the first hour, which is the detail he always mentions.",
      "The Gurbashi flats and the Mosh'Ogg shelf, taking ogre work for coin he does not spend. He "
      "is liked more than he has noticed and would be embarrassed to learn it.",
      "He wants to build the cabin again, properly badly, and has been pricing timber out of "
      "Grom'gol with a seriousness nobody expected."),

    R("ziad_felsworn", "Ziad Haddad", "Felsworn", "felsworn_slayer", 38,
      "Southern Stranglethorn", 93, 32, "front", "#7A4FA3", "melee_dps", "male", 2,
      "Lebanese man in his early 30s, slim and quick, black curls kept long on top, a sharp "
      "handsome face he is aware of, dark eyes with a faint green cast now. Purple-black leathers "
      "cut close with a half-cape, twin curved blades, a thin fel shimmer on the edges. A single "
      "foam earplug on a cord, tucked behind his collar.",
      "Mixed sound in Beirut clubs for nine years, four nights a week, reading a room in the dark "
      "and riding the exact moment it turned. He fights on the same instinct and is good enough "
      "that it worries people. He knows the bargain he made and declines to discuss it in a way "
      "that is almost charming.",
      "I go in first and I come out fast. Do not follow me in - that is not modesty, you will "
      "genuinely be in my way.",
      "Nine years behind a desk in rooms with no windows, and a flat above a bakery in Mar "
      "Mikhael. He could tell you what a crowd was going to want eight bars before it did.",
      "Three years ago he came through at two in the morning with the set still running, and the "
      "silence afterwards is the thing he cannot describe properly.",
      "The Bloodsail shallows and the wrecks off Jaguero Spit, where he is paid well and asked "
      "nothing. The green in his eyes has got stronger in the last year and he has started wearing "
      "a hood.",
      "He wants to know whether what he took can be given back. He has asked two people and both "
      "of them laughed, so he has stopped asking."),

    R("pieter_guardian", "Pieter Malan", "Guardian", "guardian_gladiator", 41,
      "Southern Stranglethorn", 89, 48, "front", "#B8A14A", "melee_dps", "male", 3,
      "South African man in his mid 40s, heavy and sunburnt, thinning blond hair, a flat pugnacious "
      "face, forearms like a man who has swung things for a living. Dull gold plate worn open at "
      "the throat, a one-handed mace and a shield he uses offensively. A groundsman's folding knife "
      "on a belt loop, handle worn pale.",
      "Kept a provincial rugby ground outside Bloemfontein for twenty-two years - grass, lines, "
      "drainage, and Saturdays spent watching other people use what he had made. He is a tank by "
      "class and refuses to play like one, on the grounds that he has done enough standing about.",
      "I have a shield and I am going to hit you with it. Twenty-two years I watched other people "
      "run onto a field I cut. I am not standing at the back of anything again.",
      "A ground, a mower, a line marker and a shed, and a wife who ran the clubhouse bar. He knew "
      "every soft patch on that pitch and could tell you the drainage history of all of it.",
      "Three years ago he came through on a Saturday morning with the lines half cut, and says the "
      "worst of it is not knowing whether anyone finished them.",
      "The cape road and the Bloodsail wrecks, in the thick of it, loudly. He has made himself "
      "popular in Booty Bay and mildly notorious with anyone who has tried to organise him.",
      "He wants a patch of flat ground and permission to cut it. He is aware this is not what "
      "anyone expects him to say and says it anyway."),

    R("esteban_bloodmage", "Esteban Ruiz", "Bloodmage", "bloodmage_accursed", 34,
      "Grom'gol", 37, 31, "front", "#A3243B", "melee_dps", "male", 4,
      "Argentinian man in his late 30s, medium build and going grey early at the front, neat beard, "
      "an unsettlingly calm bedside manner. Dark red leathers with a lamellar chest and a thin "
      "crimson blade, faint red light under the skin of his forearms. A radiation-badge dosimeter "
      "clipped at his collar, the window long since gone black.",
      "Twenty years a radiographer in Rosario, which is a job about standing people in front of "
      "something harmful in exactly the right dose. He took the Bloodmage path reasoning that he "
      "already understood the trade-off better than most, and he still measures everything, "
      "including himself.",
      "I use my own blood. Before you say anything - I spent twenty years calculating exposure for "
      "a living, and I am the only person in this camp who writes down what it costs me.",
      "Twenty years of imaging suites and lead aprons and the same three corridors, and a daughter "
      "studying in Cordoba whose last message to him was about a bus.",
      "Three years ago he came through between patients with the apron still on, and the apron is "
      "the thing he kept longest before it finally fell apart.",
      "Grom'gol and the Rotvine fen, doing work the camp healers will not. He keeps a ledger of "
      "his own use that nobody has asked to see and that he would show anyone who did.",
      "He wants somebody qualified to check his arithmetic, and has worked out there is nobody on "
      "this world who can, which he is handling less well than he lets on."),

    R("kiet_rogue", "Kiet Somsak", "Rogue", "rogue_subtlety", 31,
      "Grom'gol", 31, 36, "front", "#4A5D4E", "melee_dps", "male", 5,
      "Thai man in his late 20s, small and economical in his movements, black hair cut short, a "
      "quiet watchful face, hands that are never still. Matte grey-green leathers with a soft hood "
      "down, a thin dagger at the small of the back. A brass key blank on a loop of wire at his "
      "belt, cut for nothing.",
      "Cut keys and opened doors in Chiang Mai for people who had locked themselves out and, "
      "occasionally, for people who had not. He is incurious about violence and extremely curious "
      "about mechanisms, and he has already got further into Zul'Marosh than anyone has authorised.",
      "I am quiet and I am not brave, and those are two different things worth paying for. Point me "
      "at what is shut.",
      "A locksmith's booth off a lane near Tha Phae, a scooter, and a reputation for being "
      "discreet. He had opinions about every lock in the old city and a favourite he would not "
      "name.",
      "Three years ago he came through with a customer's key in his hand and has kept it, uncut "
      "and useless, for reasons he does not explain.",
      "Grom'gol, nominally, and the Zul'Marosh steps in practice, where the stonework has sockets "
      "in it that are plainly meant to take something. He has not told the camp what he has found.",
      "He wants to know what the sockets are for, and he has worked out that the answer is further "
      "south and underwater, which has not deterred him."),

    # ------------------------------------------------------------------ RANGED DPS (5)
    R("stelios_necromancer", "Stelios Dukas", "Necromancer", "necromancer_death", 26,
      "The Sepulcher", 40, 48, "back", "#5C6670", "ranged_dps", "male", 6,
      "Greek man in his early 50s, tall and gaunt, grey hair worn too long, a dry ironic face, "
      "half-moon reading glasses on a chain. Charcoal and bone robes with a high collar, a staff "
      "topped with a bound sheaf of pages. A librarian's date stamp, brass and wooden-handled, "
      "carried in a robe pocket.",
      "Ran the library in a Corinth prison for seventeen years, a job about cataloguing people "
      "nobody else wanted catalogued and treating them as readers. The Forsaken make perfect sense "
      "to him and he makes uncomfortable sense to them, which is the most comfortable he has been "
      "in years.",
      "I keep records. You will find that less sinister than you think and more useful than you "
      "expect. Most of what walks here is only angry about being forgotten.",
      "Seventeen years of a prison library, a card catalogue he refused to digitise, and a "
      "readership of four hundred men who were not supposed to matter. He knew every one of their "
      "borrowing histories.",
      "Three years ago he came through at the issue desk with the stamp in his hand, and set it "
      "down on nothing, and picked it back up.",
      "The Sepulcher, among the Forsaken, writing down what the dead remember because nobody else "
      "is bothering. The Dark Lady's people regard him as a harmless infestation and let him work.",
      "He wants the catalogue finished and left somewhere it will be read. He is aware that this is "
      "the only ambition he has ever had."),

    R("ratih_ranger", "Ratih Pranoto", "Ranger", "ranger_archery", 39,
      "Southern Stranglethorn", 84, 64, "back", "#3E7A5E", "ranged_dps", "female", 7,
      "Indonesian woman in her late 30s, slim and weathered, black hair in a tight braid, a direct "
      "unsmiling face, fine squint lines. Green and grey leathers with a quiver worn high, a long "
      "recurve bow. A brass river-gauge plate, stamped with marks, sewn flat onto her sleeve.",
      "Measured rivers for the Indonesian water service for fifteen years, mostly alone, mostly "
      "walking - the job of knowing where water will be next week. She reads this coast the same "
      "way, which is why she saw the tide line move before anyone in Booty Bay did and why nobody "
      "believed her.",
      "I shoot from where the ground tells me to stand. If I say move, move - I have been right "
      "about water for fifteen years and I am right about this.",
      "Fifteen years of gauging stations up and down Java, a motorbike, a notebook that got wet "
      "constantly, and a habit of being the only person who had walked the whole catchment.",
      "Three years ago she came through mid-survey and has not stopped surveying, because there is "
      "a whole world of water here that nobody has written down.",
      "The drowned coast below Zul'Kundaraz, where the sea came a hand and a half further than it "
      "was given and she can prove it. She is on good terms with exactly one goblin and no trolls.",
      "She wants somebody to write it down with her, and has begun approaching strangers about it "
      "in a way she knows is going badly."),

    R("kourosh_mage", "Kourosh Behzadi", "Mage", "mage_arcane", 33,
      "Central Stranglethorn", 147, 102, "back", "#6E78C4", "ranged_dps", "male", 8,
      "Iranian man in his late 30s, slender and slightly formal in his bearing, black hair neatly "
      "cut, close beard, a face that looks faintly amused at all times. Indigo and silver robes "
      "with precise geometric trim, a staff of nested rotating rings. A slim mechanical pencil, "
      "silver, clipped inside the collar of his robe.",
      "Priced mortality for a Tehran insurer for twelve years - a job of working out, very "
      "carefully, how likely a thing is. He finds arcane magic restful by comparison, because for "
      "once the numbers hold still. He is the only person in Stranglethorn who has calculated his "
      "own odds and he will not tell you the figure.",
      "I am going to stand back here and be extremely precise. You are welcome to be brave; "
      "somebody in a group should be, and it was never going to be the actuary.",
      "Twelve years of tables and reserving and a good office with a bad view, and a mother he "
      "called on Fridays who thought the job was beneath him.",
      "Three years ago he came through mid-calculation, and the first thing he did on this world "
      "was finish the sum, which he says was not bravery but momentum.",
      "The Veilfall basin and the arena rim, where he has quietly become the person the bookmakers "
      "do not want near the odds. He has never bet and finds the suggestion insulting.",
      "He wants to publish something. There is no press, no journal and no readership, and he is "
      "writing it anyway, longhand, in a case he keeps dry."),

    R("driss_shaman", "Driss Alaoui", "Shaman", "shaman_elemental", 35,
      "The Crystalline Underdark", 85, 14, "back", "#45A0B8", "ranged_dps", "male", 9,
      "Moroccan man in his mid 40s, lean and long-limbed, black hair greying at the temples under a "
      "wrapped headscarf, a narrow thoughtful face. Blue-grey mail and layered cloth with a totem "
      "stave and a horn at his belt, static lifting the loose ends of the scarf. A torque wrench, "
      "short and stubby, slung in a loop at his hip.",
      "Maintained wind turbines on the ridges above Tangier for sixteen years, climbing inside "
      "towers to listen to something enormous turn. He already thought of weather as a colleague "
      "with moods. The elements here answer him back, which he describes as the only genuinely new "
      "thing that has happened to him.",
      "Sixteen years I climbed inside a machine to hear what the wind was doing to it. Now the wind "
      "tells me directly. I have not decided whether that is better.",
      "Sixteen years of nacelles and gearboxes and a van full of tools, on a ridge where the wind "
      "did not stop between October and March. He could tell a bearing was going from the sound "
      "two weeks out.",
      "Three years ago he came through two hundred feet up inside a tower, and arrived underground, "
      "which he has never found funny.",
      "The Crystalline Underdark, where the air moves wrong and the crystal carries sound, and he "
      "is the only person down there who finds it legible rather than frightening.",
      "He wants to go back up. Not home - up, outside, somewhere with weather, and he has been "
      "putting it off for a year for reasons he does not examine."),

    R("marisol_priest", "Marisol Quintero", "Priest", "priest_shadow", 42,
      "Booty Bay", 40, 28, "back", "#6B4C7A", "ranged_dps", "female", 10,
      "Colombian woman in her mid 40s, small and very upright, black hair in a severe low bun, a "
      "composed face that reveals nothing at all. Deep violet and black robes with a plain white "
      "collar, a slim dark staff, shadow pooling at the hem. A pair of folding reading glasses in "
      "a hard case, carried in one sleeve.",
      "Buried people in Medellin for twenty-four years, in a family firm, through years when there "
      "was far too much work. She is unshockable, exceptionally kind in a way that frightens "
      "people, and the only member of any party who will say the plain thing out loud about what "
      "just happened.",
      "I have sat with more dead people than everyone on this quay together. I am not frightened of "
      "the shadow and I am not impressed by it either. Shall we go?",
      "Twenty-four years of a funeral home on a street in Medellin, her grandmother's business, "
      "through a decade when the city gave them more than they could carry. She knows the correct "
      "thing to say to anyone, in any state.",
      "Three years ago she came through during a wake, and she says the family will have assumed "
      "the worst of her, which is the part that bothers her.",
      "Booty Bay, where people vanish off hulls and nobody holds a service. She has started "
      "holding them anyway, badly attended, and the Bay has begun to notice.",
      "She wants the drowned of Zul'Kundaraz named. She is aware this is an absurd project and has "
      "allocated the rest of her life to it."),
]


def verify():
    """Rebuild each zone and confirm every placement is walkable, reachable and clear."""
    import importlib
    from collections import deque

    import numpy as np

    from world.zone_keys import zone_key as zk

    MODULES = {
        "Northern Stranglethorn": "stranglethorn_north",
        "Central Stranglethorn": "stranglethorn_central",
        "Southern Stranglethorn": "stranglethorn_south",
        "Grom'gol": "gromgol", "Booty Bay": "booty_bay",
        "The Crystalline Underdark": "underdark", "The Sepulcher": "sepulcher",
    }
    amb = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]
    ven = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    problems = []
    for zone, mod in MODULES.items():
        mine = [r for r in NEW if r["zone"] == zone]
        if not mine:
            continue
        m = importlib.import_module(f"tools.handbuilt_{mod}")
        L = m.build_layout()
        z, W, H = L.z, m.W, m.H
        walk = np.zeros((H, W), bool)
        for y in range(H):
            for x in range(W):
                walk[y, x] = z.is_walkable(x, y)
        sx, sy = m.START
        seen = np.zeros_like(walk)
        dq = deque([(int(sx), int(sy))])
        seen[int(sy), int(sx)] = True
        while dq:
            x, y = dq.popleft()
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < W and 0 <= ny < H and walk[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    dq.append((nx, ny))
        occ = {(e["x"], e["y"]) for e in amb + ven if zk(e.get("zone", "")) == zk(zone)}
        for r in mine:
            x, y = r["x"], r["y"]
            if not (0 <= x < W and 0 <= y < H):
                problems.append(f"{r['name']}: ({x},{y}) outside {zone} ({W}x{H})")
            elif not walk[y, x]:
                problems.append(f"{r['name']}: ({x},{y}) is not walkable in {zone}")
            elif not seen[y, x]:
                problems.append(f"{r['name']}: ({x},{y}) is walled off from START in {zone}")
            close = [o for o in occ if abs(o[0] - x) <= 2 and abs(o[1] - y) <= 2]
            if close:
                problems.append(f"{r['name']}: ({x},{y}) is within 2 of an NPC at {close[0]}")
        print(f"  {zone:28} {len(mine)} placed, {int(seen.sum())} reachable tiles")
    return problems


def main():
    check = "--check" in sys.argv
    doc = json.loads(RECRUITS.read_text(encoding="utf-8"))
    rows = doc["recruits"] if isinstance(doc, dict) and "recruits" in doc else doc
    have = {r["recruit_id"] for r in rows}

    # Guard the things Kyle told me not to touch.
    asher = next((r for r in rows if r["recruit_id"] == "asher_coleman"), None)
    if asher is None:
        raise SystemExit("asher_coleman is missing from recruits.json - refusing to run")
    import hashlib
    asher_before = hashlib.sha256(json.dumps(asher, sort_keys=True).encode()).hexdigest()

    banned = {"guardian_vanguard", "druid_feral", "druid_restoration"}
    bad = [r["name"] for r in NEW if r["spec"] in banned]
    if bad:
        raise SystemExit(f"these use an excluded spec: {bad}")

    specs_taken = {r["spec"] for r in rows}
    dupe_spec = [r["name"] for r in NEW if r["spec"] in specs_taken]
    if dupe_spec:
        raise SystemExit(f"spec already has a recruit: {dupe_spec}")
    ids = [r["recruit_id"] for r in NEW]
    if len(set(ids)) != len(ids):
        raise SystemExit("duplicate recruit_id inside this table")
    clash = [i for i in ids if i in have]
    if clash:
        print(f"already merged: {clash}")

    for r in NEW:
        talent = ROOT / f"data/talents/{r['spec']}.json"
        if not talent.exists():
            raise SystemExit(f"{r['name']}: spec {r['spec']} has no talent tree")

    from collections import Counter
    print(f"{len(NEW)} new recruits")
    print(f"  gender      {dict(Counter(r['gender'] for r in NEW))}")
    print(f"  gear_theme  {dict(Counter(r['gear_theme'] for r in NEW))}")
    print(f"  row         {dict(Counter(r['row'] for r in NEW))}")
    print(f"  levels      {sorted(r['level'] for r in NEW)}")
    print(f"  zones       {dict(Counter(r['zone'] for r in NEW))}")
    print("\nplacement:")
    problems = verify()
    if problems:
        print(f"\n{len(problems)} placement problem(s):")
        for p in problems:
            print(f"  {p}")
        raise SystemExit("refusing to write")
    print("  all placements walkable, reachable and clear")

    if check:
        return 0 if set(ids) <= have else 1

    todo = [r for r in NEW if r["recruit_id"] not in have]
    if not todo:
        print("\nnothing to do - already merged")
        return 0
    rows.extend(todo)
    RECRUITS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")

    after = json.loads(RECRUITS.read_text(encoding="utf-8"))
    arows = after["recruits"] if isinstance(after, dict) and "recruits" in after else after
    a2 = next(r for r in arows if r["recruit_id"] == "asher_coleman")
    if hashlib.sha256(json.dumps(a2, sort_keys=True).encode()).hexdigest() != asher_before:
        raise SystemExit("Asher's record changed - this should be impossible")
    print(f"\nmerged {len(todo)}; recruits.json now holds {len(arows)}; Asher unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
