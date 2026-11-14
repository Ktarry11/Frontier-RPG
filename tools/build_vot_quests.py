"""
Valley of Trials quest pass (2026-10-21).  Idempotent: re-running rewrites the
same quests by quest_id.

  python3 tools/build_vot_quests.py

* Keeps the 9 original quests (their text is Kyle's), fixes geography that no
  longer matched the rebuilt map, repairs chains, and widens reward choice
  sets so every armour type / many weapon types / jewellery show up.
* Adds 11 new quests so the new rares, subzones and cave creatures matter and
  every named NPC in camp has something to say.
* Reward items use the REAL stat formulas (tools/build_vot_content.make):
  primary stats only below item level 10, uncommon for normal quests, rare
  for boss quests, required_level = quest minimum level.
* Adds the two new quest-item drops (Den Silk Spool, Fel-Tainted Shard) to
  data/creatures/quest_drops.json.

Geography the text must respect (camp = centre of the valley):
  The Den ........ west of camp          Burning Blade Coven ... east, past the nest
  Sagebrush Flat . west (training yard)  Scorpid Nest .......... north-east
  Sagewood Grove . east                  Windrift Dunes ........ south-east
  Trailwater Spring (lake) . south       Cinderjaw Wastes ...... far south-west
  Exit to Durotar . east road
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_vot_content import make  # noqa: E402

QUEST_FILE = ROOT / "data/quests/valley_of_trials.json"
DROPS_FILE = ROOT / "data/creatures/quest_drops.json"

PRIMARY = {"strength", "agility", "intellect", "stamina", "spirit"}


def item(name, slot, suffix, ilvl, flavor, label, armor=None, weapon=None, req=1, rarity="uncommon"):
    d = make(name, slot, suffix, ilvl, flavor, armor_type=armor, weapon_type=weapon, req=req, rarity=rarity)
    d["label"] = label
    d.pop("secondary_stats", None) if not d.get("secondary_stats") else None
    return d


# ======================================================================
# NEW QUESTS
# ======================================================================
def new_quests():
    Q = []

    # ---- Grulnok (recruit watcher) ---------------------------------------
    Q.append(dict(
        quest_id="vot_old_tusk", title="Wanted: Old Tusk", giver_npc_id="vot_recruit_watcher",
        zone="valley_of_trials", level_min=2, level_max=4,
        description=("Grulnok has watched this ridge for six seasons and he knows every boar on it by its tracks. "
                     "One set of tracks he doesn't like: a boar the size of a cart, tusks worn yellow, with a habit of "
                     "walking straight through the training dummies on Sagebrush Flat as if they were an insult. "
                     "The recruits call it Old Tusk. Grulnok calls it a matter of time before someone's mother gets bad news. "
                     "Thin out the boars on the flat, and when the old one shows himself, put him down."),
        objectives=[dict(type="kill", target="Mottled Boar", count=3),
                    dict(type="kill", target="Old Tusk", count=1)],
        reward_exp=280, reward_gold=700,
        accept_text=("West of camp, on the flat. You'll know him when you see him - he's the one that doesn't run. "
                     "Don't fight him on open ground with your back to a hill. Use the dummies. He hates the dummies."),
        turn_in_text=("Tusk's down? Good. Good. That's a lot of years of that animal off the ridge in one afternoon. "
                      "Take these - the old boar's had them coming since before you woke up."),
        rewards=[
            item("Tuskplate Pauldrons", "shoulder", "of the Bear", 5,
                 "Two curved tusks, riveted to a strap. Nobody is asking where the third one went.",
                 "Plate Shoulders (Str/Sta)", armor="plate", req=2),
            item("Boarbristle Mitts", "hands", "of the Owl", 5,
                 "Stiff bristles across the knuckles, soft silk where it counts.",
                 "Cloth Gloves (Int/Spi)", armor="cloth", req=2),
            item("Ridgerunner Bracers", "wrist", "of the Monkey", 5,
                 "Cut from the part of the hide that doesn't squeak.",
                 "Leather Bracers (Agi/Sta)", armor="leather", req=2),
            item("Heavy Boarhide Belt", "waist", "of the Tiger", 5,
                 "Heavier than it looks and about as comfortable as it sounds.",
                 "Mail Belt (Str/Agi)", armor="mail", req=2),
        ]))

    # ---- Torgak (wounded grunt) -----------------------------------------
    Q.append(dict(
        quest_id="vot_carrion_circle", title="Carrion Circle", giver_npc_id="vot_wounded_grunt",
        zone="valley_of_trials", level_min=2, level_max=5,
        description=("Torgak can't walk the ridge yet and the carrion birds have noticed. They've started circling the camp "
                     "in the afternoons, patient as tax collectors, and the jackals that follow them keep creeping closer "
                     "to the fire. He says it's nothing personal. He says it with the look of someone who has taken it personally. "
                     "Clear out the vultures and the jackals running with them until the sky gets boring again."),
        objectives=[dict(type="kill", target="Carrion Vulture", count=4),
                    dict(type="kill", target="Dustwind Jackal", count=4)],
        reward_exp=250, reward_gold=650,
        accept_text=("They think I'm already dead. I'd like to change their minds. Vultures first - "
                     "the jackals only get brave when there's something circling. Don't tell Nakhtar I'm giving out quests."),
        turn_in_text=("Quiet sky. You have no idea how nice that is. Take something - Nakhtar says "
                      "I'm not allowed to hand out coin, but nobody said anything about gear I can't wear anymore."),
        rewards=[
            item("Vulture-Feather Cloak", "back", "of the Wolf", 5,
                 "Lighter than air, warmer than it has any right to be.",
                 "Cloak (Agi/Spi)", req=2),
            item("Scavenger's Cord", "waist", "of the Falcon", 5,
                 "Everything useful ends up tied to it eventually.",
                 "Leather Belt (Agi/Int)", armor="leather", req=2),
            item("Bonepicker's Legguards", "legs", "of Strength", 5,
                 "Plated with what the birds left behind.",
                 "Plate Legs (Str)", armor="plate", req=2),
            item("Torgak's Spare Crutch", "main_hand", "of the Owl", 5,
                 "It has a lot of opinions about leaning.",
                 "Staff (Int/Spi)", weapon="staff", req=2),
        ]))

    # ---- Old Marta (herbalist) ------------------------------------------
    Q.append(dict(
        quest_id="vot_troubled_waters", title="Troubled Waters", giver_npc_id="valley_vendor",
        zone="valley_of_trials", level_min=1, level_max=3, next_quest_id="vot_gulpjaw",
        description=("The spring at the lake south of camp has fed this valley since before the Horde had a name for it, "
                     "and lately Old Marta can't brew a clean batch with water from it. Marsh skimmers have been skating over "
                     "the shallows in numbers she's never seen, and the toads are bolder than toads should be. "
                     "She isn't asking for a massacre - just enough dead things that the water runs clear again."),
        objectives=[dict(type="kill", target="Marsh Skimmer", count=5),
                    dict(type="kill", target="Trailwater Toad", count=3)],
        reward_exp=180, reward_gold=450,
        accept_text=("Go south to the lake. Mind the mud, it's deeper than it looks. "
                     "Skimmers and toads - I don't care which you reach first, I just want the shallows still for an hour."),
        turn_in_text=("Clear water, at last. Smell that? That's a remedy that works. And look at you - "
                      "hardly wet. You're learning the trick of it faster than most."),
        rewards=[
            item("Reed-Wrapped Bracers", "wrist", "of the Whale", 3,
                 "Waterproof, mostly. Fragrant, definitely.",
                 "Cloth Bracers (Sta/Spi)", armor="cloth", req=1),
            item("Skimmer-Silk Sash", "waist", "of the Owl", 3,
                 "Spun from something that spends its life on water. It sheds it beautifully.",
                 "Cloth Belt (Int/Spi)", armor="cloth", req=1),
            item("Springstone Charm", "neck", "of Spirit", 3,
                 "A smooth stone from the lake bottom. It's calmer than you are.",
                 "Necklace (Spi)", req=1),
            item("Mudcaked Greaves", "feet", "of the Boar", 3,
                 "They've never been clean and never will be. They don't slip, either.",
                 "Mail Boots (Str/Spi)", armor="mail", req=1),
        ]))

    Q.append(dict(
        quest_id="vot_gulpjaw", title="The Spring's Warden", giver_npc_id="valley_vendor",
        zone="valley_of_trials", level_min=3, level_max=5,
        description=("The skimmers are only the symptom. Something huge has taken up residence at Trailwater Spring - "
                     "a toad bigger than a boar that the recruits have started calling Old Gulpjaw, mostly in the tone people "
                     "use for weather. It's been eating whatever drifts in, and now it's eating whatever walks in. "
                     "Marta needs the spring back. Bring a friend if you can find one. Bring a plan if you can't."),
        objectives=[dict(type="kill", target="Old Gulpjaw", count=1),
                    dict(type="kill", target="Trailwater Toad", count=2)],
        reward_exp=310, reward_gold=800,
        accept_text=("He sits at the bottom of the shallows and waits. Don't wade in. Pull him out onto the bank - "
                     "everything slow is worse in water than out of it."),
        turn_in_text=("Gulpjaw, gone. The water's already settling. You've done this valley more good than you know - "
                      "and I'll keep telling people so, whether you like it or not."),
        rewards=[
            item("Toadleather Hood", "head", "of the Wolf", 6,
                 "Smells of pond. Keeps the rain out like nothing else.",
                 "Leather Helm (Agi/Spi)", armor="leather", req=3),
            item("Spring-Warden's Mace", "main_hand", "of the Boar", 6,
                 "You've seen cartoon hammers like this. Now you own one.",
                 "Mace (Str/Spi)", weapon="mace_1h", req=3),
            item("Slick-Scale Legwraps", "legs", "of the Eagle", 6,
                 "Water beads right off. So, honestly, does most criticism.",
                 "Cloth Legs (Int/Sta)", armor="cloth", req=3),
            item("Lilypad Buckler", "off_hand", "of Stamina", 6,
                 "Surprisingly sturdy for something named after a plant.",
                 "Shield (Sta)", weapon="shield", req=3),
        ]))

    # ---- Marta again: the Grove ------------------------------------------
    Q.append(dict(
        quest_id="vot_heartwood", title="Heartwood and Thorn", giver_npc_id="valley_vendor",
        zone="valley_of_trials", level_min=3, level_max=5,
        description=("The petals did their job. Now Marta wants the thing that makes the petals worth gathering: "
                     "heartwood from the old sagewood in the Grove east of camp. Lately the saplings there have started "
                     "walking - thornroot saplings, quick and mean - and something older has begun to move among them. "
                     "Bramblethorn the Ancient has been in that grove longer than the valley has had a name. "
                     "She doesn't ask you to fell it. She asks that it stop."),
        objectives=[dict(type="kill", target="Thornroot Sapling", count=5),
                    dict(type="kill", target="Bramblethorn the Ancient", count=1)],
        reward_exp=350, reward_gold=900,
        accept_text=("It's the grove's own heart gone sour. Saplings first - they'll tell you where the old one is. "
                     "Fire works, if you have it. It also makes the grove very angry, so do it quickly."),
        turn_in_text=("The grove's quiet again. Listen to it. That is what a valley sounds like when it isn't being watched. "
                      "Take something. You've earned more than I'll ever be able to give."),
        rewards=[
            item("Sapling-Carved Wand", "ranged", "of Intellect", 6,
                 "You wave it, things happen. You're choosing not to ask for details.",
                 "Wand (Int)", weapon="wand", req=3),
            item("Bramblebound Leggings", "legs", "of the Wolf", 6,
                 "Woven so tightly even the thorns couldn't find the gaps.",
                 "Leather Legs (Agi/Spi)", armor="leather", req=3),
            item("Thornroot Spaulders", "shoulder", "of the Falcon", 6,
                 "Grown, not forged. Doesn't mind the weight.",
                 "Mail Shoulders (Agi/Int)", armor="mail", req=3),
            item("Greenwarden's Mantle", "shoulder", "of the Owl", 6,
                 "Warm, and quietly alive.",
                 "Cloth Shoulders (Int/Spi)", armor="cloth", req=3),
        ]))

    # ---- Kuraw (elder): the Den chain + the wastes -------------------------
    Q.append(dict(
        quest_id="vot_brood_below", title="The Brood Below", giver_npc_id="vot_elder",
        zone="valley_of_trials", level_min=3, level_max=5, next_quest_id="vot_nest_guardian",
        description=("You came back from the Den's mouth with an observant eye. Now Elder Kuraw wants the next lesson: "
                     "the deeper chambers where the eggs are kept. The Den is a scorpid-and-spider brood cave and "
                     "its guardians are only as dangerous as the numbers behind them. "
                     "Thin them out - skitterers and webspinners in the halls, egg tenders in the nursery - "
                     "so that whatever comes for the guardian does not come into a room full of its children."),
        objectives=[dict(type="kill", target="Cave Skitterer", count=3, zone="the_den"),
                    dict(type="kill", target="Den Webspinner", count=3, zone="the_den"),
                    dict(type="kill", target="Egg Tender", count=2, zone="the_den")],
        reward_exp=360, reward_gold=900,
        accept_text=("Caves lie. They tell you the next room is safe because it's quiet. "
                     "Then you step in and find out why it was quiet. Clear the halls, then the nursery. "
                     "One room at a time."),
        turn_in_text=("You walk different than you did. Good. Fewer of them behind you means fewer in front. "
                      "The guardian is next, and it's the last thing in that cave that matters."),
        rewards=[
            item("Skitterer-Chitin Helm", "head", "of the Bear", 5,
                 "Doesn't fit anyone. Fits you now.",
                 "Plate Helm (Str/Sta)", armor="plate", req=3),
            item("Webwoven Gloves", "hands", "of Agility", 5,
                 "Sticky on the inside only. Tested.",
                 "Leather Gloves (Agi)", armor="leather", req=3),
            item("Husk-Plated Vambraces", "wrist", "of the Boar", 5,
                 "Chitin plates over a boiled hide.",
                 "Mail Bracers (Str/Spi)", armor="mail", req=3),
            item("Egg-Tender's Wand", "ranged", "of the Owl", 5,
                 "It hums when you stand near anything fragile.",
                 "Wand (Int/Spi)", weapon="wand", req=3),
        ]))

    Q.append(dict(
        quest_id="vot_windrift_omens", title="Windrift Omens", giver_npc_id="vot_elder",
        zone="valley_of_trials", level_min=4, level_max=6, next_quest_id="vot_cinderjaw",
        description=("Elder Kuraw reads weather the way other orcs read faces, and the weather in the Windrift Dunes "
                     "southeast of camp is saying something he doesn't like. Dust devils have been walking the road with intent, "
                     "and sandpincer crawlers keep pushing up out of the sand where there was nothing before. "
                     "He wants the dunes quiet before whatever is stirring them decides to finish waking."),
        objectives=[dict(type="kill", target="Dust Devil", count=4),
                    dict(type="kill", target="Sandpincer Crawler", count=3)],
        reward_exp=360, reward_gold=950,
        accept_text=("Southeast, down the road to the dunes. Don't chase the dust. Let it come to you. "
                     "Sandpincers hide under the surface - if the sand moves, move first."),
        turn_in_text=("Quieter already. I can hear the road again. There's one more place that's wrong, "
                      "and it's the worst one. We'll talk about it."),
        rewards=[
            item("Dustveil Wraps", "chest", "of the Eagle", 6,
                 "Layered cloth, stained in the shape of a very long road.",
                 "Cloth Chest (Int/Sta)", armor="cloth", req=4),
            item("Sandglass Pendant", "neck", "of the Falcon", 6,
                 "The sand inside never finishes falling.",
                 "Necklace (Agi/Int)", req=4),
            item("Dunewalker's Crossbow", "ranged", "of the Monkey", 6,
                 "Lightweight, accurate, and forgiving of sand in the mechanism.",
                 "Crossbow (Agi/Sta)", weapon="crossbow", req=4),
            item("Crawler-Shell Cuirass", "chest", "of the Bear", 6,
                 "Heavy. Hot. Excellent against things that bite.",
                 "Plate Chest (Str/Sta)", armor="plate", req=4),
        ]))

    Q.append(dict(
        quest_id="vot_cinderjaw", title="The Cinderjaw Problem", giver_npc_id="vot_elder",
        zone="valley_of_trials", level_min=5, level_max=6,
        description=("There is a stretch of valley far to the south-west where the ground itself is burnt: the Cinderjaw Wastes. "
                     "Ember wisps drift there like loose sparks, ashback basilisks sleep on the warm stone, and something "
                     "called Smolderhide has been seen walking at night with fire on its back. "
                     "Elder Kuraw wants it dealt with before the wastes creep any closer to the lake. "
                     "This is the hardest thing he has ever asked of a recruit. He asks it quietly."),
        objectives=[dict(type="kill", target="Ember Wisp", count=4),
                    dict(type="kill", target="Ashback Basilisk", count=2),
                    dict(type="kill", target="Smolderhide", count=1)],
        reward_exp=500, reward_gold=1300,
        accept_text=("Go south, past the lake, and keep the road under your feet until it stops being a road. "
                     "Don't fight on the black stone. It holds heat. Smolderhide will find you - "
                     "it always finds you. Be ready when it does."),
        turn_in_text=("Smolderhide, dead. Then the valley's dangerous things are done, or as done as they get. "
                      "You have the look of someone who survived a lot. That's the only graduation I recognize."),
        rewards=[
            item("Cinderforged Greathelm", "head", "of Strength", 7,
                 "It's a bucket with ambitions. They're mostly justified.",
                 "Plate Helm (Str)", armor="plate", req=5),
            item("Ashwalker's Jerkin", "chest", "of the Tiger", 7,
                 "Singed in all the right places. Tough in all the others.",
                 "Leather Chest (Str/Agi)", armor="leather", req=5),
            item("Ember-Stitched Legguards", "legs", "of the Falcon", 7,
                 "The seams still glow faintly at night.",
                 "Mail Legs (Agi/Int)", armor="mail", req=5),
            item("Cinder Signet", "ring", "of Intellect", 7,
                 "A red-hot idea you had once, cooled into metal.",
                 "Ring (Int)", req=5),
        ]))

    # ---- Grosk the Younger: Sandfang -------------------------------------
    Q.append(dict(
        quest_id="vot_grosks_trophy", title="Grosk's Trophy", giver_npc_id="vot_young_orc",
        zone="valley_of_trials", level_min=4, level_max=6,
        description=("Grosk the Younger has decided that a real orc leaves the valley with a trophy, and he has decided on Sandfang - "
                     "the pale, scarred jackal that haunts the Windrift Dunes and has outrun every hunter in the valley. "
                     "He has not decided how he'll do it, which is why he is asking you. "
                     "Thin the pack, find the old one, and bring him proof. His mother has opinions about the whole idea. "
                     "She may be right. Do it anyway."),
        objectives=[dict(type="kill", target="Dustwind Jackal", count=4),
                    dict(type="kill", target="Sandfang", count=1)],
        reward_exp=400, reward_gold=1000,
        accept_text=("It's a white one. Scar over the left eye. Quick as anything, but it's old - old things get careless. "
                     "I'd do it myself except... my mother. You understand."),
        turn_in_text=("You actually did it! She's going to be so angry. I'm going to tell everyone you did it, I swear - "
                      "I'll say it was both of us. Here, take something. For the trouble."),
        rewards=[
            item("Dunestalker's Longspear", "main_hand", "of Strength", 6,
                 "Longer than a shopping cart and nearly as steerable.",
                 "Polearm (Str)", weapon="polearm", req=4),
            item("Trophy-Hunter's Sling", "ranged", "of the Monkey", 6,
                 "Not exactly a gentleman's weapon. You're not exactly a gentleman.",
                 "Thrown (Agi/Sta)", weapon="thrown", req=4),
            item("Dune-Stalker's Cloak", "back", "of Agility", 6,
                 "Sand-coloured, sand-stained, sand-proof.",
                 "Cloak (Agi)", req=4),
            item("Grosk's Lucky Bracers", "wrist", "of the Boar", 6,
                 "He wore them for a day. They did not feel lucky.",
                 "Plate Bracers (Str/Spi)", armor="plate", req=4),
        ]))

    # ---- Fizzcrank: fel shards ------------------------------------------
    Q.append(dict(
        quest_id="vot_fel_shards", title="Fizzcrank's Shiny Problem", giver_npc_id="vot_goblin_tinkerer",
        zone="valley_of_trials", level_min=3, level_max=5,
        description=("Fizzcrank Sprocketspin has discovered that the crystals lining the Burning Blade Coven give off a heat "
                     "he finds personally offensive: it should not be possible to be warm and wrong at the same time. "
                     "He wants five shards - tiny ones, pocket-sized, the kind the acolytes carry on their belts - "
                     "to measure what's wrong with them. He is fairly sure it's not dangerous. "
                     "He is also fairly sure it was on fire a moment ago."),
        objectives=[dict(type="fetch", target="fel_shard", count=5, zone="burning_blade_coven")],
        reward_exp=310, reward_gold=850,
        accept_text=("The acolytes keep them on their belts. Don't touch them with bare hands. "
                     "Use tongs. Or a stick. Or a different hand. I'll be here, doing my own science."),
        turn_in_text=("Oh, that's wonderful. That's - oh no. Okay, it's fine, nothing to see. "
                      "Take whatever you want from the bench - I'm going to be busy."),
        rewards=[
            item("Sprocketspin Rangefinder", "ranged", "of the Monkey", 5,
                 "It clicks. You aren't sure what it measures. You choose to trust it.",
                 "Gun (Agi/Sta)", weapon="gun", req=3),
            item("Goggles of Questionable Safety", "head", "of the Falcon", 5,
                 "Rated for two explosions. You've already worn it through four.",
                 "Leather Helm (Agi/Int)", armor="leather", req=3),
            item("Shard-Studded Gauntlets", "hands", "of the Eagle", 5,
                 "Tiny crystals hum at the knuckles. Do not make a fist near anything flammable.",
                 "Mail Gloves (Int/Sta)", armor="mail", req=3),
            item("Fuse-Wire Ring", "ring", "of the Eagle", 5,
                 "Shorter fuse, bigger idea.",
                 "Ring (Int/Sta)", req=3),
        ]))

    # ---- Rhaka: Den silk ------------------------------------------------
    Q.append(dict(
        quest_id="vot_silk_for_rhaka", title="Silk for Rhaka", giver_npc_id="vot_orc_mother",
        zone="valley_of_trials", level_min=2, level_max=4,
        description=("Rhaka's son went up the ridge to prove himself last week, and he came back. "
                     "She'd like to keep it that way, and in her experience the surest way to do that is a good cloak. "
                     "Not a ratty hide thing - silk, strong enough to turn a scorpid sting, the kind the webspinners "
                     "in the Den spin in their halls. Six spools. She has the loom. She does not have the nerve to go into that cave."),
        objectives=[dict(type="fetch", target="den_silk", count=6, zone="the_den")],
        reward_exp=240, reward_gold=650,
        accept_text=("Spools, from the webspinners. They keep them at their backs. Don't take the loose thread - "
                     "it's sticky. The spools are what you want. Be careful. Please."),
        turn_in_text=("This is good silk. Strong. Feel that? That'll turn a stinger. "
                      "Here - I made extra. It's the least I can do for the one who made me less afraid."),
        rewards=[
            item("Rhaka's Silkwoven Mantle", "shoulder", "of the Whale", 4,
                 "Made by a mother who has worried a lot and sewn better for it.",
                 "Cloth Shoulders (Sta/Spi)", armor="cloth", req=2),
            item("Mother's Travel Cloak", "back", "of Stamina", 4,
                 "It's not magic. It's just very well made.",
                 "Cloak (Sta)", req=2),
            item("Den-Silk Slippers", "feet", "of the Owl", 4,
                 "Quiet on stone, soft on blisters.",
                 "Cloth Boots (Int/Spi)", armor="cloth", req=2),
            item("Silk-Laced Marching Boots", "feet", "of the Wolf", 4,
                 "She added one extra stitch for luck.",
                 "Leather Boots (Agi/Spi)", armor="leather", req=2),
        ]))

    # ---- Nakhtar: the Broodmother ------------------------------------------
    Q.append(dict(
        quest_id="vot_mother_of_nest", title="Mother of the Nest", giver_npc_id="vot_greeter",
        zone="valley_of_trials", level_min=4, level_max=6, next_quest_id="vot_graduation",
        description=("The scorpids you've been killing have a mother. Broodmother Sarrix has held the north-eastern nest for longer "
                     "than the Horde has held the valley, and she is the reason the workers keep coming. "
                     "Nakhtar doesn't want you to fight her. He wants you to fight everything around her first, "
                     "and then to decide whether you're ready. He suspects you'll go anyway."),
        objectives=[dict(type="kill", target="Venomtail Scorpid", count=3),
                    dict(type="kill", target="Broodmother Sarrix", count=1)],
        reward_exp=430, reward_gold=1200,
        accept_text=("Northeast. Past the camp road, where the sand turns dark. She rarely leaves the nest and never leaves it unguarded. "
                     "Be sure of your health before you commit to the fight. It's long, and it's patient."),
        turn_in_text=("Sarrix is dead. The nest will keep moving without her for a season and then settle. "
                      "You did something this valley has needed for a long time. I won't forget it."),
        rewards=[
            item("Broodmother's Stinger", "main_hand", "of Agility", 7,
                 "A real stinger, dried and shaped. Still faintly twitches.",
                 "Dagger (Agi)", weapon="dagger", req=4),
            item("Queenhide Tunic", "chest", "of the Monkey", 7,
                 "The hide shrugs off everything except compliments.",
                 "Leather Chest (Agi/Sta)", armor="leather", req=4),
            item("Nestbreaker Legplates", "legs", "of the Bear", 7,
                 "Heavy, and it doesn't care.",
                 "Plate Legs (Str/Sta)", armor="plate", req=4),
            item("Chitin Aegis", "off_hand", "of Stamina", 7,
                 "A slab of broodmother carapace on a strap.",
                 "Shield (Sta)", weapon="shield", req=4),
        ]))

    # ---- Valley Grunt: the ritual -------------------------------------------
    Q.append(dict(
        quest_id="vot_ritual_disruption", title="Disrupting the Ritual", giver_npc_id="vot_guard_1",
        zone="valley_of_trials", level_min=4, level_max=5, next_quest_id="vot_yarrog_baneshadow",
        description=("The familiars were only the bait. Deeper in the Coven, the Burning Blade have been drawing a circle - "
                     "a real one, with a real summoning, in a hall the Valley Grunt has only seen from a distance. "
                     "Initiates guard the approaches and ritual guards stand between them and any fool with a sword. "
                     "Break up the ritual before it finishes, or there won't be a Baneshadow to fight. There will be something worse."),
        objectives=[dict(type="kill", target="Burning Blade Initiate", count=4, zone="burning_blade_coven"),
                    dict(type="kill", target="Coven Ritual Guard", count=2, zone="burning_blade_coven")],
        reward_exp=400, reward_gold=1000,
        accept_text=("Initiates in the outer halls. Ritual guards in the hall with the circle. "
                     "Kill the guards first if you can - they're the ones who'll finish it. "
                     "I'll hold the road behind you."),
        turn_in_text=("The circle's broken. The air smells normal again, and I didn't know I'd been smelling it. "
                      "There's only one left to finish. Take this and go."),
        rewards=[
            item("Shattered Ritual Blade", "main_hand", "of Strength", 6,
                 "Cracked down the middle and still sharp enough. Both halves are on the wall of your room back home.",
                 "Sword (Str)", weapon="sword_1h", req=4),
            item("Acolyte's Sash", "waist", "of the Eagle", 6,
                 "The sigil on the buckle is facing the wrong way. It's fine.",
                 "Cloth Belt (Int/Sta)", armor="cloth", req=4),
            item("Fel-Scorched Greaves", "feet", "of the Bear", 6,
                 "Blackened but sturdy. Don't kick anything flammable.",
                 "Plate Boots (Str/Sta)", armor="plate", req=4),
            item("Coven-Marked Band", "ring", "of the Tiger", 6,
                 "The mark has faded. The strength hasn't.",
                 "Ring (Str/Agi)", req=4),
        ]))
    return Q


# ======================================================================
# EDITS TO EXISTING QUESTS
# ======================================================================
def patch_existing(by_id):
    P = by_id
    P["vot_scorpid_trouble"]["description"] = P["vot_scorpid_trouble"]["description"].replace(
        "The scorpid nest south of camp", "The scorpid nest in the north-east of the valley")
    P["vot_scorpid_trouble"]["next_quest_id"] = "vot_mother_of_nest"
    P["vot_den_scout"]["description"] = P["vot_den_scout"]["description"].replace(
        "just north of camp", "just west of camp")
    P["vot_den_scout"]["next_quest_id"] = "vot_brood_below"
    P["vot_den_scout"]["objectives"][0].update(target_x=42, target_y=23, radius=6)
    P["vot_graduation"]["accept_text"] = P["vot_graduation"]["accept_text"].replace(
        "Follow the road north out of the valley", "Follow the road east out of the valley")
    P["vot_graduation"]["description"] = P["vot_graduation"]["description"].replace(
        "the boars, the scorpid", "the boars, the scorpid")
    P["vot_sagewood_petals"]["next_quest_id"] = "vot_heartwood"
    P["vot_vile_familiars"]["next_quest_id"] = "vot_ritual_disruption"
    # level bands to match the creatures they actually need
    P["vot_nest_guardian"].update(level_min=3, level_max=6)
    P["vot_yarrog_baneshadow"].update(level_min=4, level_max=6)
    P["vot_yarrog_baneshadow"].pop("gear_reward_slot", None)       # stale: unique defs take priority
    P["vot_graduation"].update(level_min=4, level_max=6)

    # --- widen reward sets (existing weapons stay; add armour / jewellery)
    P["vot_scorpid_trouble"]["unique_item_defs"].append(
        item("Stinger-Studded Bracers", "wrist", "of Strength", 4,
             "Spikes where the stingers were. Plates where they'd hit.",
             "Plate Bracers (Str)", armor="plate", req=2))
    P["vot_nest_guardian"]["unique_item_defs"] += [
        item("Carapace Breastplate", "chest", "of the Bear", 6,
             "A guardian's own plating, hammered flat and riveted.",
             "Plate Chest (Str/Sta)", armor="plate", req=3),
        item("Brood-Warden's Hauberk", "chest", "of the Falcon", 6,
             "Light, flexible, and smells faintly of damp stone.",
             "Mail Chest (Agi/Int)", armor="mail", req=3),
    ]
    P["vot_vile_familiars"]["unique_item_defs"] += [
        item("Familiar-Bone Charm", "neck", "of the Eagle", 5,
             "Warm to the touch for reasons it won't share.",
             "Necklace (Int/Sta)", req=3),
        item("Taint-Warded Leggings", "legs", "of the Owl", 5,
             "Stitched with a ward you can't read. It hasn't failed you yet.",
             "Cloth Legs (Int/Spi)", armor="cloth", req=3),
    ]
    P["vot_felstalkers"]["unique_item_defs"] += [
        item("Hound-Hide Boots", "feet", "of Agility", 5,
             "Scuffed in places no boot should be.",
             "Leather Boots (Agi)", armor="leather", req=3),
        item("Packleader's Spaulders", "shoulder", "of the Monkey", 5,
             "Taken from something with a very bad temper.",
             "Mail Shoulders (Agi/Sta)", armor="mail", req=3),
    ]
    P["vot_yarrog_baneshadow"]["unique_item_defs"] += [
        item("Baneshadow's Cowl", "head", "of the Eagle", 6,
             "The cowl speaks in a language you do not want to learn. It has stopped, for now.",
             "Cloth Helm (Int/Sta)", armor="cloth", req=4, rarity="rare"),
        item("Fel-Seared Bracers", "wrist", "of the Bear", 6,
             "Burned into shape and quenched in something dark.",
             "Plate Bracers (Str/Sta)", armor="plate", req=4, rarity="rare"),
    ]
    # graduation: a farewell set (jewellery / cloak)
    P["vot_graduation"]["unique_item_defs"] = [
        item("Recruit's Valor Cloak", "back", "of Stamina", 6,
             "Dust of three trials still caught in the weave.",
             "Cloak (Sta)", req=4),
        item("Nakhtar's Farewell Charm", "neck", "of the Owl", 6,
             "A feather and a knot of red cord. He tied it himself.",
             "Necklace (Int/Spi)", req=4),
        item("Valley-Forged Band", "ring", "of Strength", 6,
             "Plain, sturdy, and slightly too big. It will fit by Durotar.",
             "Ring (Str)", req=4),
        item("Graduate's Token", "trinket", "of Agility", 6,
             "A flat river stone, marked with a single claw-scratch.",
             "Trinket (Agi)", req=4),
    ]
    P["vot_graduation"]["gear_reward_gear_level"] = 6


def main():
    data = json.loads(QUEST_FILE.read_text(encoding="utf-8"))
    by_id = {q["quest_id"]: q for q in data["quests"]}
    # rewards are rebuilt from scratch on every run -> idempotent
    for k in list(by_id):
        by_id[k].pop("_new", None)
    order = [q["quest_id"] for q in data["quests"]]
    # make idempotent: restore the original unique_item_defs of existing quests before patching
    # (patching only appends; skip if already patched)
    already = "vot_old_tusk" in by_id
    if not already:
        patch_existing(by_id)
    for q in new_quests():
        rewards = q.pop("rewards")
        q["unique_item_defs"] = rewards
        q["gear_reward_gear_level"] = max(r["item_level"] for r in rewards)
        q.setdefault("next_quest_id", None)
        if q["quest_id"] not in by_id:
            order.append(q["quest_id"])
        by_id[q["quest_id"]] = q
    data["quests"] = [by_id[i] for i in order]
    QUEST_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- quest-item drops
    drops = json.loads(DROPS_FILE.read_text(encoding="utf-8"))
    D = drops["drops"]
    silk = {"item_id": "den_silk", "name": "Den Silk Spool", "category": "quest",
            "description": "A tight spool of webspinner silk, strong enough to turn a scorpid sting. Rhaka wants these.",
            "chance": 0.5}
    shard = {"item_id": "fel_shard", "name": "Fel-Tainted Shard", "category": "quest",
             "description": "A pocket-sized crystal shard, warm and wrong. Fizzcrank wants to measure it. Use tongs.",
             "chance": 0.4}
    D["Den Webspinner"] = [silk]
    D["Cave Skitterer"] = [dict(silk, chance=0.2)]
    D["Burning Blade Acolyte"] = [shard]
    D["Coven Ritual Guard"] = [dict(shard, chance=0.35)]
    D["Burning Blade Initiate"] = [dict(shard, chance=0.2)]
    DROPS_FILE.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("quests:", len(data["quests"]))


if __name__ == "__main__":
    main()
