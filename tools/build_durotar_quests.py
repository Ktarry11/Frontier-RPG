"""
Durotar quest pass (2026-10-21).  Idempotent: re-running rewrites the same
quests by quest_id and re-applies the same patches.

  python3 tools/build_durotar_quests.py

* Keeps the 7 original Durotar quests (their text is Kyle's) and only fixes
  level bands / geography; adds 19 quests so every new rare, subzone and
  ambient NPC of the rebuilt map matters.
* Rare-kill quests are the finales of short chains (trash objective -> rare).
  Their rewards are RARE and built with the real stat formulas
  (tools/build_durotar_content.make allows secondary stats at ilvl >= 10).
* Retargets the Razor Hill Kolkar quests (Kolkar Raider is shared with the
  Northern Barrens; Durotar uses the new Kolkar Warrider) and widens bands.
* Adds quest-item drops (Prowler Pelt, Glittering Mesa Ore, Razormane Toll
  Pouch) to data/creatures/quest_drops.json.

Geography the quest text respects
  Orgrimmar gate ...... north (y ~26)       Main highway ..... south to Razor Hill (centre, y ~108)
  Thunder Ridge ....... north-west, cave (55,45)
  Drygulch Ravine ..... north-east beside the gate road
  Zeppelin / Grotto / Skull Rock ... the north-east coast cliffs
  Barrens bridge ...... far west (5,85)     Kolkar Crag ...... bowl south-west of the Barrens road
  Rocktusk Farm ....... far south-west, Valley of Trials gateway beyond
  Scuttle Coast ....... south-east shore, Echo Isles pier   Tiragarde Keep ... south coast
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import build_durotar_content as DC          # noqa: E402
from tools import build_vot_content as VC               # noqa: E402

DUROTAR_FILE = ROOT / "data/quests/durotar.json"
RAZOR_FILE = ROOT / "data/quests/razor_hill.json"
DROPS_FILE = ROOT / "data/creatures/quest_drops.json"


def item(name, slot, suffix, ilvl, flavor, label, armor=None, weapon=None,
         req=None, rarity="uncommon"):
    maker = DC.make if ilvl >= 10 else VC.make
    d = maker(name, slot, suffix, ilvl, flavor, armor_type=armor, weapon_type=weapon,
              req=req, rarity=rarity)
    d["label"] = label
    if not d.get("secondary_stats"):
        d.pop("secondary_stats", None)
    return d


def kill(target, count, alt=None, zone=None):
    o = dict(type="kill", target=target, count=count)
    if alt:
        o["alt_targets"] = alt
    if zone:
        o["zone"] = zone
    return o


def fetch(target, count):
    return dict(type="fetch", target=target, count=count)


# ======================================================================
def new_quests():
    Q = []

    # ================= Orgrimmar gate: Rustfang chain ===================
    Q.append(dict(
        quest_id="dur_eyes_on_road", title="Eyes on the Road", giver_npc_id="durotar_orgrimmar_gate_guard",
        zone="durotar", level_min=6, level_max=9, next_quest_id="dur_old_redtooth",
        description=("The Outrider at the gate watches the highway for a living, and for three weeks the highway has been "
                     "watching back. Rustfang hyenas have started tailing the caravans out of Orgrimmar, hanging a hundred paces "
                     "behind the last wagon and picking off whatever falls behind. Wagons are late. Drivers are quitting. "
                     "The Outrider would deal with it herself, but the gate is hers to hold, and someone has to be seen to be doing something."),
        objectives=[kill("Rustfang Hyena", 8)],
        reward_exp=300, reward_gold=1200,
        accept_text=("Out on the Red Wastes, either side of the highway. They come in threes and fours, rust-red, "
                     "grinning like they know something. They do not know anything. Make that clear to them."),
        turn_in_text=("Fewer of them on the road already - I can hear it. Quiet, I mean. "
                      "There's a bigger one, though. The drivers talk about him like he's a tax collector. Take this and keep your eyes open."),
        rewards=[
            item("Outrider's Roadcloak", "back", "of the Monkey", 8,
                 "Dust-coloured on the outside. The inside is mostly pockets.",
                 "Cloak (Agi/Sta)", armor="accessory", req=5),
            item("Gate-Watch Brigandine", "chest", "of the Tiger", 8,
                 "Standard issue for the gate. Fits almost nobody exactly.",
                 "Mail Chest (Str/Agi)", armor="mail", req=5),
            item("Wasteland Spear", "main_hand", "of Strength", 8,
                 "A long spear for short tempers.", "Polearm (Str)", weapon="polearm", req=5),
            item("Hyena-Tooth Ring", "ring", "of the Falcon", 8,
                 "Strung on a leather thong; the thong has seen worse days.",
                 "Ring (Agi/Int)", req=5),
        ]))
    Q.append(dict(
        quest_id="dur_old_redtooth", title="Wanted: Old Redtooth", giver_npc_id="durotar_orgrimmar_gate_guard",
        zone="durotar", level_min=8, level_max=11, next_quest_id=None,
        description=("Every pack has a head, and the Rustfang's is a hyena the drivers call Old Redtooth. Scarred muzzle, "
                     "one ear torn to a notch, bigger than a pony and smarter than most of the guards at the gate. He doesn't charge. "
                     "He circles, he waits, he lets the others bleed you first. The Outrider has a bounty on him that's older than "
                     "some of the recruits."),
        objectives=[kill("Rustfang Hyena", 4), kill("Old Redtooth", 1)],
        reward_exp=760, reward_gold=2600,
        accept_text=("He keeps to the open ground off the highway, not far from the gate road. Don't fight him with your back to a hill - "
                     "he'll have two friends up there before you finish the thought."),
        turn_in_text=("That's the notch, right there. Redtooth's done. Good. Keep the pelt if you want, but I think you'll want what he guarded."),
        rewards=[
            item("Redtooth's Fang-Knife", "main_hand", "of the Assassin", 14,
                 "Pulled from the jaw of the alpha himself. Still thinks it's hunting.",
                 "Dagger (Agi/Hit/Crit)", weapon="dagger", rarity="rare"),
            item("Rustfang Hunter's Mask", "head", "of the Hunt", 14,
                 "Hyena-hide stitched around a skull that did not need it any more.",
                 "Leather Helm (Agi/Int/AP)", armor="leather", rarity="rare"),
            item("Pack-Mother's Charm", "neck", "of the Restorer", 14,
                 "Every pack has someone who keeps the others alive. This is what she wore.",
                 "Necklace (Healing/MP5)", rarity="rare"),
            item("Hauberk of the Alpha", "chest", "of the Beast", 14,
                 "Layers of hide and scale. It shrugs off teeth with a sort of smug patience.",
                 "Mail Chest (Str/Agi/Sta)", armor="mail", rarity="rare"),
        ]))

    # ================= Sentry: scorpids =================================
    Q.append(dict(
        quest_id="dur_scorpid_season", title="Scorpid Season", giver_npc_id="durotar_patrol_1",
        zone="durotar", level_min=6, level_max=9,
        description=("The Sentry's patrol cuts across the east side of the highway and every year around this time the armored scorpids "
                     "come out from under their rocks to mate, or fight, or - he's honestly never been clear which. What he is clear on "
                     "is that his boots are not made for it. Thin them out before they spread to the road."),
        objectives=[kill("Armored Scorpid", 8)],
        reward_exp=320, reward_gold=1300,
        accept_text=("Out past the road, near the rock shelves. The plates are thick, so hit the gaps. "
                     "They don't hunt you. They just don't move out of your way."),
        turn_in_text=("Quieter already. I'll be able to walk the whole beat in peace for a week. Take something from the stores - "
                      "Orgrimmar won't miss it, and if it does, it'll blame me."),
        rewards=[
            item("Scorpid-Plate Pauldrons", "shoulder", "of the Bear", 9,
                 "Sections of scorpid carapace on a plate frame. They clack when you shrug.",
                 "Plate Shoulders (Str/Sta)", armor="plate", req=6),
            item("Sentry's Quilted Wraps", "wrist", "of the Owl", 9,
                 "Padded cloth, because even sentries get tired of bruises.",
                 "Cloth Bracers (Int/Spi)", armor="cloth", req=6),
            item("Tail-Stinger Dirk", "main_hand", "of the Monkey", 9,
                 "A scorpid tail-spine on a hilt. It's better than it sounds.",
                 "Dagger (Agi/Sta)", weapon="dagger", req=6),
            item("Carapace Buckler", "off_hand", "of Stamina", 9,
                 "Small, round, and a little bit venomous looking.",
                 "Shield (Sta)", weapon="shield", req=6),
        ]))

    # ================= Grosk the Wanderer: pelts ========================
    Q.append(dict(
        quest_id="dur_warm_blanket", title="A Warm Blanket", giver_npc_id="durotar_traveler",
        zone="durotar", level_min=6, level_max=9,
        description=("Grosk the Wanderer has crossed the Wastes more times than he can count and has never once been cold, "
                     "which is why it took him three nights to notice that Grukk's boy is. The desert freezes after dark, and "
                     "the child has been sleeping on a bedroll thin enough to read through. Prowler pelts are the warmest thing for "
                     "a hundred miles. Grosk has too many knees to hunt them himself."),
        objectives=[fetch("durotar_prowler_pelt", 6)],
        reward_exp=300, reward_gold=1000,
        accept_text=("Durotar Prowlers - the big sand-coloured cats. They den in the rough ground west of the highway. "
                     "Six good pelts, no holes in them. The boy's small, but he's not that small."),
        turn_in_text=("Look at that. He's asleep already and I haven't even tucked it in. You've done a better thing than most do all year. "
                      "I'll not be needing this anymore - the road gave it to me, and it gave you a better deal."),
        rewards=[
            item("Wanderer's Prowlerhide Vest", "chest", "of the Wolf", 9,
                 "Warm on a cold night. Smells like campfire and apology.",
                 "Leather Chest (Agi/Spi)", armor="leather", req=6),
            item("Roadworn Walking Staff", "main_hand", "of the Whale", 9,
                 "Has walked further than you will. Has opinions on the matter.",
                 "Staff (Sta/Spi)", weapon="staff", req=6),
            item("Kid's Lucky Pebble", "trinket", "of the Eagle", 9,
                 "A smooth river-stone painted with a face. The face is smiling at something behind you.",
                 "Trinket (Int/Sta)", req=6),
            item("Dustproof Boots", "feet", "of the Boar", 9,
                 "Seams sealed with something sticky and mysterious.",
                 "Mail Boots (Str/Spi)", armor="mail", req=6),
        ]))

    # ================= Thunder Ridge chain ==============================
    Q.append(dict(
        quest_id="dur_thunder_approach", title="The Rumble Below", giver_npc_id="durotar_thunder_ridge_scout",
        zone="durotar", level_min=8, level_max=11, next_quest_id="dur_stormbinders",
        description=("Ridgewatch Kurr has watched Thunder Ridge for years and the ridge has never been this loud. "
                     "Thunder lizards and their cousins the thunderhides are wandering down off the slopes in numbers, "
                     "crowding the approach to the cave and snapping at anyone who gets between them and the water. "
                     "He wants the traffic thinned before something worse follows them down."),
        objectives=[kill("Thunder Lizard", 6, alt=["Crackling Thunderhide"])],
        reward_exp=420, reward_gold=1600,
        accept_text=("North-west of the highway, up the gravel basin. You'll hear them before you see them. "
                     "If the ground hums, step to the side. Seriously."),
        turn_in_text=("Better. Not good, but better. You noticed the other ones up there, though - the ones that talk? "
                      "That's the real problem. Finish what you started."),
        rewards=[
            item("Ridgewatcher's Hauberk", "chest", "of the Soldier", 10,
                 "Mail layered over ridge-lizard scale. It doesn't mind the weather.",
                 "Mail Chest (Str/Sta/Crit)", armor="mail", req=7),
            item("Static-Charged Gloves", "hands", "of the Archmage", 10,
                 "Rub them together and the hairs on your arms agree.",
                 "Cloth Gloves (Int/SP/MP5)", armor="cloth", req=7),
            item("Gravel-Runner Boots", "feet", "of the Marksman", 10,
                 "Grip the loose stone so you don't have to.",
                 "Leather Boots (Agi/Sta/Hit)", armor="leather", req=7),
            item("Thunderhide Girdle", "waist", "of the Champion", 10,
                 "Thick, stiff, and only a little bit singed.",
                 "Plate Belt (Str/Sta/Defense)", armor="plate", req=7),
        ]))
    Q.append(dict(
        quest_id="dur_stormbinders", title="Stormbinders", giver_npc_id="durotar_thunder_ridge_scout",
        zone="durotar", level_min=9, level_max=12, next_quest_id="dur_rumblejaw",
        description=("The lizards aren't coming down on their own. Something has been feeding the storm on the ridge - Kurr has "
                     "watched Ridge Stormbinders chanting at the cliff edge with their arms raised, and every time they finish, "
                     "a flock of static hatchlings spills out of the rocks. Whatever they're building toward, he doesn't want to be there for it."),
        objectives=[kill("Ridge Stormbinder", 5), kill("Static Hatchling", 6)],
        reward_exp=520, reward_gold=1800,
        accept_text=("Higher up the ridge, where the rock goes dark. Take the binders first - the hatchlings stop swarming when "
                     "the chanting stops. Don't stand in anything that's glowing."),
        turn_in_text=("Quiet. Truly quiet. Which means he's awake. Rumblejaw - the big one. "
                      "I've never seen him come down, but I've heard him through the stone."),
        rewards=[
            item("Stormbinder's Mantle", "shoulder", "of the Invoker", 11,
                 "Woven from a binder's own cloak, singed at the hem.",
                 "Cloth Shoulders (Int/SP/Crit)", armor="cloth", req=8),
            item("Hatchling-Shell Bracers", "wrist", "of the Ironfur", 11,
                 "Light, hard, and still faintly crackling.",
                 "Leather Bracers (Sta/Agi/Dodge)", armor="leather", req=8),
            item("Lightning-Rod Spear", "main_hand", "of the Gladiator", 11,
                 "Do not hold this during a storm. Do not hold this ever, if you can help it.",
                 "Polearm (Str/Hit/Crit)", weapon="polearm", req=8),
            item("Tempest Ward Band", "ring", "of the Defender", 11,
                 "A ring of fused sand. It repels lightning like a bad idea.",
                 "Ring (Sta/Defense/Dodge)", req=8),
        ]))
    Q.append(dict(
        quest_id="dur_rumblejaw", title="Wanted: Rumblejaw", giver_npc_id="durotar_thunder_ridge_scout",
        zone="durotar", level_min=10, level_max=12, next_quest_id=None,
        description=("There's a lizard on Thunder Ridge the length of two ox-carts with a jaw that cracks stone. The scouts call him Rumblejaw "
                     "because they feel him before they hear him. He's never been seen beyond the high shelves, but Kurr says that's changing: "
                     "the stormbinders have been feeding him. Cut the head off the problem."),
        objectives=[kill("Thunder Lizard", 4, alt=["Crackling Thunderhide"]), kill("Rumblejaw", 1)],
        reward_exp=840, reward_gold=2900,
        accept_text=("Top of the ridge, in the rock shelf above the basin. When the ground stops shaking, he's about to hit you. Move when it stops, not when it starts."),
        turn_in_text=("Rumblejaw's down? I can hear the quiet from here. That's the first real silence the ridge has had in ten years. Take whatever fits."),
        rewards=[
            item("Rumblejaw's Slab", "off_hand", "of Stamina", 15,
                 "A plate of fused ridge-stone. Rattles, faintly, when something big walks by.",
                 "Shield (Sta/Block)", weapon="shield", rarity="rare"),
            item("Thunderbitten Staff", "main_hand", "of the Invoker", 15,
                 "The wood is petrified. The lightning it holds is not.",
                 "Staff (Int/SP/Crit)", weapon="staff", rarity="rare"),
            item("Seer's Stoneplate Bracers", "wrist", "of the Seer", 15,
                 "Slate bracers. Listen to them and you can hear the ridge settling.",
                 "Mail Bracers (Int/Sta/MP5)", armor="mail", rarity="rare"),
            item("Quake-Walker's Greaves", "legs", "of the Soldier", 15,
                 "Heavy plates that don't care how the ground feels about it.",
                 "Plate Legs (Str/Sta/Crit)", armor="plate", rarity="rare"),
        ]))

    # ================= Skull Rock chain =================================
    Q.append(dict(
        quest_id="dur_cinders_on_wind", title="Cinders on the Wind", giver_npc_id="durotar_skull_rock_patrol",
        zone="durotar", level_min=8, level_max=11, next_quest_id="dur_houndmaster",
        description=("The Skull Rock Watcher has stood on the cliff above the approach for so long he's stopped seeing the ash, "
                     "but today it's coming up the path in clouds. Burning Blade torchbearers are burning their way across the approach to clear "
                     "ground for something, and a swarm of cinder imps follows them to feed on the embers. If that fire reaches the road, "
                     "the Wastes are going to burn for a week."),
        objectives=[kill("Cinder Imp", 6), kill("Burning Blade Torchbearer", 4)],
        reward_exp=480, reward_gold=1700,
        accept_text=("Down the cliff path, toward the cave mouth. Torchbearers first - they light everything they pass. "
                     "The imps are small, but they're quick, and they bite where you least expect."),
        turn_in_text=("The wind's clean for the first time since spring. I could cry. I won't, but I could. "
                      "There's a man down there with dogs - Kraygh. He lit the first fire. Finish it."),
        rewards=[
            item("Ash-Walker's Wraps", "wrist", "of the Eagle", 10,
                 "Fireproofed with something that doesn't smell as bad as it ought to.",
                 "Cloth Bracers (Int/Sta)", armor="cloth", req=7),
            item("Torchbearer's Cord", "waist", "of the Squire", 10,
                 "Singed in a few places. Strong in all the rest.",
                 "Mail Belt (Str/Sta/Hit)", armor="mail", req=7),
            item("Cinderproof Cloak", "back", "of the Whale", 10,
                 "Ash slides off it. So does a lot of other things.",
                 "Cloak (Sta/Spi)", armor="accessory", req=7),
            item("Imp-Bone Cudgel", "main_hand", "of the Tiger", 10,
                 "Small, ugly, and fond of finding the soft spot.",
                 "Mace (Str/Agi)", weapon="mace_1h", req=7),
        ]))
    Q.append(dict(
        quest_id="dur_houndmaster", title="The Houndmaster", giver_npc_id="durotar_skull_rock_patrol",
        zone="durotar", level_min=10, level_max=13, next_quest_id=None,
        description=("Houndmaster Kraygh keeps his dogs on the approach and his whip in his hand and he's never once been seen sleeping. "
                     "The Burning Blade bring him fresh hounds from the caves and he sets them on any traveler who looks too far in. "
                     "He's good with a whip. He's better with an excuse. The Watcher wants him gone before the hounds find a way down to the road."),
        objectives=[kill("Searing Blade Raider", 4), kill("Houndmaster Kraygh", 1)],
        reward_exp=900, reward_gold=3000,
        accept_text=("Down by the cave mouth, with his pack. Cut the guards down first - they hold the hounds back until he gives the word. "
                     "When the whip cracks, run. Not away. Past him."),
        turn_in_text=("The whip's silent. Do you hear that? Nothing's barking. Take his things. He won't be wanting them."),
        rewards=[
            item("Kraygh's Felwhip Wand", "ranged", "of Shadow Wrath", 16,
                 "The leather's burned into the grip. It cracks even when you're not holding it.",
                 "Wand (Shadow Power)", weapon="wand", rarity="rare"),
            item("Houndmaster's Fel-Pistol", "ranged", "of the Restorer", 16,
                 "Fires something that mends the hounds. You've just decided it mends you instead.",
                 "Gun (Healing/MP5)", weapon="gun", rarity="rare"),
            item("Kennel-Keeper's Plate", "chest", "of the Juggernaut", 16,
                 "Spiked and scorched in all the places a hound likes to bite.",
                 "Plate Chest (Sta/Armor/Parry)", armor="plate", rarity="rare"),
            item("Netherfire Handwraps", "hands", "of Netherfire", 16,
                 "They glow when the dark is close. They're glowing now.",
                 "Cloth Gloves (Shadow+Fire Power)", armor="cloth", rarity="rare"),
        ]))

    # ================= Fitz: glittering ore =============================
    Q.append(dict(
        quest_id="dur_glitter", title="All That Glitters", giver_npc_id="durotar_goblin_prospector",
        zone="durotar", level_min=7, level_max=10,
        description=("Gazlowe's Cousin Fitz has been mapping the mesas for ore for six months and has found exactly one thing: "
                     "the stonebiters chew it. Big rock-coloured beasts that gnaw on the mesa edges and, somewhere in that long digestive tract, "
                     "concentrate glittering ore. Fitz would love to know how. He'd love it more if someone brought him a sample "
                     "without making him go near the teeth."),
        objectives=[fetch("mesa_ore", 6)],
        reward_exp=400, reward_gold=1500,
        accept_text=("Mesa Stonebiters. Big, grey, hungry. They drop little glittering chunks when you cut them open - "
                     "yes, I know how that sounds. Six chunks. I'll pay a finder's cut and not ask questions."),
        turn_in_text=("Oh, that's lovely. It's practically jewelry. Don't tell Gazlowe, he'll want a cut. "
                      "Here - and take one of my spare prospecting finds for your trouble."),
        rewards=[
            item("Prospector's Greatcoat", "chest", "of the Falcon", 10,
                 "Pockets inside pockets. Most of them contain pebbles.",
                 "Leather Chest (Agi/Int)", armor="leather", req=7),
            item("Fitz's Pick-Hammer", "main_hand", "of the Gorilla", 10,
                 "Half pick, half hammer. Entirely sure which half it prefers.",
                 "Mace (Str/Int)", weapon="mace_1h", req=7),
            item("Glittering Ore Pendant", "neck", "of the Mind's Eye", 10,
                 "Ore, wire, and an optimistic goblin's idea of jewelry.",
                 "Necklace (Int/SP/Hit)", req=7),
            item("Mesa-Stride Greaves", "legs", "of the Defender", 10,
                 "Stout, scuffed, and quite fond of a good scramble.",
                 "Plate Legs (Sta/Defense/Dodge)", armor="plate", req=7),
        ]))

    # ================= Borka: the farm ==================================
    Q.append(dict(
        quest_id="dur_farmhands", title="Hands on the Farm", giver_npc_id="durotar_rocktusk_scout",
        zone="durotar", level_min=6, level_max=9, next_quest_id="dur_matron_sowbelly",
        description=("Borka the Watchful keeps one eye on the road and the other on Rocktusk Farm, where the quilboar have taken over a "
                     "stolen homestead and put the previous owners' razorbacks to work. The farmhands are quilboar who've learned that a "
                     "pitchfork works on people. The tamed razorbacks have learned much the same. Neither is a good neighbor."),
        objectives=[kill("Rocktusk Farmhand", 6), kill("Tamed Razorback", 4)],
        reward_exp=320, reward_gold=1300,
        accept_text=("South-west, through the gate in the farm palisade. The farmhands patrol the furrows; the razorbacks follow whoever's holding the slops. "
                     "Don't be holding the slops."),
        turn_in_text=("Farm's quieter. Mostly. There's a sow in the back barn - the Matron. She's been breeding war-pigs in there since spring. "
                      "I want her to stop."),
        rewards=[
            item("Hog-Tender's Jerkin", "chest", "of the Beast", 9,
                 "Greasy leather, but it takes a gore like a champion.",
                 "Leather Chest (Str/Agi/Sta)", armor="leather", req=6),
            item("Pitchfork of Leaning", "main_hand", "of the Wolf", 9,
                 "Hay-tipped and angry.", "Polearm (Agi/Spi)", weapon="polearm", req=6),
            item("Furrow-Cleat Boots", "feet", "of the Bear", 9,
                 "Clay-caked, but they hold the dirt.",
                 "Plate Boots (Str/Sta)", armor="plate", req=6),
            item("Thornwood Bracers", "wrist", "of the Owl", 9,
                 "Wrapped with thorn-vine and a reasonable amount of luck.",
                 "Cloth Bracers (Int/Spi)", armor="cloth", req=6),
        ]))
    Q.append(dict(
        quest_id="dur_matron_sowbelly", title="Wanted: Matron Sowbelly", giver_npc_id="durotar_rocktusk_scout",
        zone="durotar", level_min=8, level_max=10, next_quest_id=None,
        description=("She was an ordinary sow once, the farm's breeding stock, before the quilboar fed her whatever it is they feed things. "
                     "Now she's the size of a cart and twice as bitter. The razorbacks follow her. The farmhands pray to her. "
                     "Borka wants her gone before she decides the road is next."),
        objectives=[kill("Tamed Razorback", 4), kill("Matron Sowbelly", 1)],
        reward_exp=700, reward_gold=2400,
        accept_text=("Farm barn, back of the furrows. She hits hard and she smells worse. Don't fight her in the open - the razorbacks will join in."),
        turn_in_text=("Matron's down. That's a lot of bacon, though I wouldn't touch it. Take the good stuff - she's done with it."),
        rewards=[
            item("Farmyard Tenderiser", "main_hand", "of the Soldier", 13,
                 "A fence-post with ideas. The Matron had opinions about fences.",
                 "Mace (Str/Sta/Crit)", weapon="mace_1h", rarity="rare"),
            item("Sowbelly's Silk Shawl", "shoulder", "of the Prophet", 13,
                 "Somebody wove this for a farmer's wife. She never got to wear it.",
                 "Cloth Shoulders (Int/Spi/Healing)", armor="cloth", rarity="rare"),
            item("Matron's Ear-Tag", "trinket", "of the Defender", 13,
                 "Iron, numbered, and still warm. She was number one.",
                 "Trinket (Sta/Defense/Dodge)", rarity="rare"),
            item("Trough-Scrapers", "hands", "of the Champion", 13,
                 "Plate gauntlets, dented in a way that only makes sense if you have met the Matron.",
                 "Plate Gloves (Str/Sta/Defense)", armor="plate", rarity="rare"),
        ]))

    # ================= Sylthressa: the coast ============================
    Q.append(dict(
        quest_id="dur_net_and_hook", title="Net and Hook", giver_npc_id="durotar_beltelf_merchant",
        zone="durotar", level_min=7, level_max=10, next_quest_id="dur_gillfin",
        description=("Sylthressa Windmourne imports silk from places with names she says better than you could. She also imports it, regrettably, "
                     "through Scuttle Coast, where the murlocs have taken to stringing nets across the beach and the saltcrust crabs have taken to "
                     "living in them. Her caravans arrive late, tangled, and mildly crab-flavored. She would like this to stop."),
        objectives=[kill("Murloc Netcaster", 6), kill("Saltcrust Crab", 6)],
        reward_exp=420, reward_gold=1600,
        accept_text=("East, on the shore. The netcasters throw first and ask questions never. The crabs just pinch. "
                     "Clear both out and my silk can arrive dry."),
        turn_in_text=("Dry silk! You've no idea what that means to me. And there's something else on that coast - a murloc with a hook. "
                      "My drivers call him the Net-Cutter. Please do him next."),
        rewards=[
            item("Windmourne Silk Hood", "head", "of the Archmage", 10,
                 "Finest weave, finest threads. She's very particular about the threads.",
                 "Cloth Helm (Int/SP/MP5)", armor="cloth", req=7),
            item("Saltcrust Pauldrons", "shoulder", "of the Squire", 10,
                 "Crab-shell on a plate frame. Sea air hasn't touched it.",
                 "Plate Shoulders (Str/Sta/Hit)", armor="plate", req=7),
            item("Netweaver's Gloves", "hands", "of the Hunt", 10,
                 "Knots tied by hands that knew what they were doing.",
                 "Leather Gloves (Agi/Int/AP)", armor="leather", req=7),
            item("Tidepool Charm", "neck", "of the Physician", 10,
                 "A pearl and a wish, bound in kelp.",
                 "Necklace (Sta/Int/Healing)", req=7),
        ]))
    Q.append(dict(
        quest_id="dur_gillfin", title="Wanted: Gillfin the Net-Cutter", giver_npc_id="durotar_beltelf_merchant",
        zone="durotar", level_min=9, level_max=11, next_quest_id=None,
        description=("Every murloc tribe has one who learned to use a blade, and on Scuttle Coast it's Gillfin. He cuts nets, he cuts lines, "
                     "and when he's bored, he cuts the traders' ropes. Sylthressa's drivers swear he took a wagon wheel once, for the hub. "
                     "She'd like him out of business."),
        objectives=[kill("Murloc Netcaster", 4), kill("Gillfin the Net-Cutter", 1)],
        reward_exp=780, reward_gold=2700,
        accept_text=("Shoreline, east. He moves between the netted rocks, and he'll mend himself if you let him. Don't."),
        turn_in_text=("The Net-Cutter is done? Gods. I could kiss you. I won't - business first - but I will pay you extremely well in finery."),
        rewards=[
            item("Net-Cutter's Hooked Blade", "main_hand", "of the Duelist", 14,
                 "Half a sword, half a gaff. Entirely sure which half it prefers.",
                 "Sword (Dodge/Parry)", weapon="sword_1h", rarity="rare"),
            item("Driftwood Harpoon-Crossbow", "ranged", "of the Marksman", 14,
                 "Fires harpoons. The harpoons are mostly spite.",
                 "Crossbow (Agi/Sta/Hit)", weapon="crossbow", rarity="rare"),
            item("Tidewrack Wristwraps", "wrist", "of the Tactician", 14,
                 "Dry-rotted netting, enchanted by someone with a long memory of drowning.",
                 "Cloth Bracers (Int/SP/Hit)", armor="cloth", rarity="rare"),
            item("Pearl of the Net-Cutter", "neck", "of the Archmage", 14,
                 "Pried from a clam that took it personally.",
                 "Necklace (Int/SP/MP5)", rarity="rare"),
        ]))

    # ================= Wyll Marrow: Kolkar ==============================
    Q.append(dict(
        quest_id="dur_kolkar_reckoning", title="Kolkar Reckoning", giver_npc_id="durotar_human_prisoner_convert",
        zone="durotar", level_min=8, level_max=11, next_quest_id="dur_bloodhoof",
        description=("Wyll Marrow was a cartwright out of Stormwind when the Kolkar took his caravan at the Crag and left him alive "
                     "as an afterthought. The Horde found him two days later, half-starved and swearing, and he's never quite forgiven them "
                     "for the rescue or the centaur for the ambush. Now he wants the war-riders paid back, in the only currency they understand."),
        objectives=[kill("Kolkar Warrider", 8, alt=["Kolkar Outrunner", "Kolkar Wrangler", "Kolkar Pack Runner", "Kolkar Windchaser"])],
        reward_exp=470, reward_gold=1800,
        accept_text=("The Crag's the bowl south-west of the Barrens road. They ride in circles like they own it. "
                     "Fair enough - they do. Thin the war-riders out and I'll sleep easier."),
        turn_in_text=("There. Somewhere in a Stormwind graveyard, my brother's smiling. There's one of them I can't get out of my head - "
                      "a lame one with a limp he hides. Bloodhoof. He broke my wagon."),
        rewards=[
            item("Cartwright's Steel Gloves", "hands", "of the Gladiator", 10,
                 "Cartwright's hands, steel gauntlets, a very patient maker.",
                 "Plate Gloves (Str/Hit/Crit)", armor="plate", req=7),
            item("Marrow's Mended Cloak", "back", "of the Ironfur", 10,
                 "A cloak he's patched so often it's more patch than cloak.",
                 "Cloak (Sta/Agi/Dodge)", armor="accessory", req=7),
            item("Centaur-Hide Leggings", "legs", "of the Hunt", 10,
                 "Tough, supple, and cut for someone who never sits still.",
                 "Leather Legs (Agi/Int/AP)", armor="leather", req=7),
            item("Wagon-Spoke Staff", "main_hand", "of the Invoker", 10,
                 "A broken spoke, carved and varnished. Quite a lot of care went into it.",
                 "Staff (Int/SP/Crit)", weapon="staff", req=7),
        ]))
    Q.append(dict(
        quest_id="dur_bloodhoof", title="Wanted: Bloodhoof the Lamed", giver_npc_id="durotar_human_prisoner_convert",
        zone="durotar", level_min=10, level_max=12, next_quest_id=None,
        description=("The Kolkar tell stories about their outriders, and about the one called Bloodhoof they tell quieter. "
                     "A crippled rider with a withered foreleg who kept charging anyway, long after any sensible centaur would have retired. "
                     "He has taken more caravans than the rest of the Crag combined. Wyll wants him on his back, in the dust, where he put the wagons."),
        objectives=[kill("Kolkar Warrider", 4), kill("Bloodhoof the Lamed", 1)],
        reward_exp=860, reward_gold=3000,
        accept_text=("He rides alone, at the edge of the Crag, where the ground drops. He hits like a cart and runs like a deer. Don't chase him. Make him come to you."),
        turn_in_text=("Lamed Bloodhoof's down. I almost feel for him. Almost. Take whatever he carried - he won't be riding again."),
        rewards=[
            item("Lamed Outrider's Glaive", "main_hand", "of the Gladiator", 15,
                 "Balanced for a rider with one good leg. Rides on regardless.",
                 "Polearm (Str/Hit/Crit)", weapon="polearm", rarity="rare"),
            item("Outrider's Hunting Belt", "waist", "of the Hunt", 15,
                 "A Kolkar belt, studded with the tags of every kill he refused to stop counting.",
                 "Leather Belt (Agi/Int/AP)", armor="leather", rarity="rare"),
            item("Hoofbeat Greaves", "feet", "of the Tiger", 15,
                 "You can feel a gallop in the soles. Even standing still.",
                 "Mail Boots (Str/Agi)", armor="mail", rarity="rare"),
            item("Wrangler's Mending Band", "ring", "of the Restorer", 15,
                 "The ring he used on wounded mounts. It did a lot of mending, in the end.",
                 "Ring (Healing/MP5)", rarity="rare"),
        ]))

    # ================= Sunbleached Remains: one-shot ====================
    Q.append(dict(
        quest_id="dur_last_words", title="Last Words", giver_npc_id="durotar_skeleton_marker",
        zone="durotar", level_min=7, level_max=11,
        description=("The bones by the shore are a wagon-driver's, and clutched in them is a sealed letter and a cracked signet ring "
                     "that doesn't look like it belongs to the driver. The letter is addressed to someone named Tamsin, "
                     "care of the burnt caravan on the highway south-west of Grosk's camp. The ink's too faded to say who's expecting it. "
                     "It doesn't say it has to be delivered. But somebody has to."),
        objectives=[dict(type="explore", target="durotar", target_x=72, target_y=80, radius=6)],
        reward_exp=360, reward_gold=1100,
        accept_text=("(The bones don't speak. The letter is addressed in a shaky hand, and the ring is warm in your palm.) "
                     "The highway south-west of the traveler's camp. Where the wagons burned."),
        turn_in_text=("(You lay the letter among the ash, as best you can. When you return, the signet is a little less cracked than it was. "
                      "The wind carries something that might be thanks.)"),
        rewards=[
            item("Driver's Signet", "ring", "of the Whale", 10,
                 "A plain ring, polished smooth by an owner who wore it every day.",
                 "Ring (Sta/Spi)", req=7),
            item("Wagon-Wheel Charm", "trinket", "of the Monkey", 10,
                 "Small enough to hold, heavy enough to remember.",
                 "Trinket (Agi/Sta)", req=7),
            item("Tamsin's Last Letter", "neck", "of the Prophet", 10,
                 "Wax-sealed, unread. A little warm, somehow.",
                 "Necklace (Int/Spi/Healing)", req=7),
            item("Roadmender's Boots", "feet", "of the Defender", 10,
                 "Worn through. Somehow still keeping their word.",
                 "Plate Boots (Sta/Defense/Dodge)", armor="plate", req=7),
        ]))

    # ================= Grekka: the road to the Valley ===================
    Q.append(dict(
        quest_id="dur_safe_road_south", title="The Safe Road South", giver_npc_id="durotar_vot_road_traveler",
        zone="durotar", level_min=6, level_max=9,
        description=("Southbound Grekka has walked the road between Razor Hill and the Valley of Trials longer than most recruits have been alive. "
                     "Lately she can't make it past the Rocktusk Farm turnoff without a quilboar scout shaking her down for the privilege. "
                     "Recruits shouldn't have to start their first week on the Wastes with their coin purse already lighter."),
        objectives=[kill("Razormane Scout", 6), kill("Razormane Geomancer", 3)],
        reward_exp=340, reward_gold=1300,
        accept_text=("The road south of the gateway, near the farm. The scouts watch from above; the geomancers throw rocks from behind. "
                     "Take the geomancers first, if you can find them."),
        turn_in_text=("You're a good one. Now new recruits get a clean road and I get to keep what I earn. Here - a spare from my own pack."),
        rewards=[
            item("Wayfarer's Longcoat", "chest", "of the Wolf", 9,
                 "Long enough to keep out the wind. Short enough to run in.",
                 "Leather Chest (Agi/Spi)", armor="leather", req=6),
            item("Roadkeeper's Mace", "main_hand", "of the Bear", 9,
                 "A solid mace for solid people.", "Mace (Str/Sta)", weapon="mace_1h", req=6),
            item("Grekka's Spare Cloak", "back", "of the Eagle", 9,
                 "Thick wool, a little frayed at the hem.",
                 "Cloak (Int/Sta)", armor="accessory", req=6),
            item("Southbound Sash", "waist", "of the Monkey", 9,
                 "Tied around her waist for forty miles. It's earned its place.",
                 "Leather Belt (Agi/Sta)", armor="leather", req=6),
        ]))

    # ================= Bok: road tax ====================================
    Q.append(dict(
        quest_id="dur_road_tax", title="Road Tax", giver_npc_id="durotar_razorhill_road_merchant",
        zone="durotar", level_min=7, level_max=10,
        description=("Wandering Bok sells what he can on the road between Razor Hill and the gate and pays the Orgrimmar road tax out of his own pocket. "
                     "The quilboar have started doing the same - collecting it, that is. Their quilboar-sized toll pouches turn up in their packs every time "
                     "someone's gotten past them, and Bok figures that's his coin. He'd like his coin."),
        objectives=[fetch("razormane_toll_pouch", 6)],
        reward_exp=380, reward_gold=1500,
        accept_text=("Razormane quilboar, out on the Wastes. They carry leather pouches on their belts - you'll know them. "
                     "Six pouches, and I'll consider the road tax paid."),
        turn_in_text=("My coin! Smaller than I remembered, but still mine. Now take a cut - you've earned it, and I always pay my debts."),
        rewards=[
            item("Merchant's Mantle", "shoulder", "of the Physician", 10,
                 "Sewn by someone who was careful about the seams.",
                 "Cloth Shoulders (Sta/Int/Healing)", armor="cloth", req=7),
            item("Toll-Collector's Hauberk", "chest", "of the Beast", 10,
                 "Heavy mail with an extra layer of leather where the money goes.",
                 "Mail Chest (Str/Agi/Sta)", armor="mail", req=7),
            item("Strongbox Shield", "off_hand", "of Stamina", 10,
                 "A lid with a lock, and a fair bit of dent.",
                 "Shield (Sta/Block)", weapon="shield", req=7),
            item("Bok's Lucky Coin", "trinket", "of the Falcon", 10,
                 "Heads, he wins. Tails, he's thinking about it.",
                 "Trinket (Agi/Int)", req=7),
        ]))
    return Q


# ======================================================================
# EDITS TO EXISTING QUESTS (direct sets - safe to re-run)
# ======================================================================
def patch_existing(by_id):
    P = by_id
    # --- Durotar originals
    P["durotar_vulture_feathers"].update(level_min=6, level_max=9)
    p = P["durotar_prowler_den"]
    p.update(level_min=6, level_max=9)
    p["description"] = ("Borka the Watchful has noticed the Durotar prowlers denning closer to the road than usual, and he'd rather know exactly "
                        "where before Razor Hill sends anyone in after them properly. The cats have made a den in the dry basin west of the highway, "
                        "roughly halfway between the Orgrimmar gate and Razor Hill. He's not asking for a fight yet - just eyes on the den itself, "
                        "confirmed and reported back.")
    p["accept_text"] = ("North of here, in the dry basin west of the highway, about halfway to the Orgrimmar gate. "
                        "Get close enough to confirm the den and get out. I'd rather have a live scout with an answer than a dead hero with a guess.")
    p["objectives"][0].update(target_x=48, target_y=72, radius=8)
    P["durotar_skullrock_approach"].update(level_min=8, level_max=11)

    # --- Razor Hill quests that point into the rebuilt map
    r = P  # same dict, razor_hill quests are merged by caller
    return


def patch_razor(by_id):
    P = by_id
    P["razorhill_rocktusk_farm"].update(level_min=6, level_max=9)
    P["razorhill_thunder_ridge_approach"].update(level_min=8, level_max=11)
    P["razorhill_stormhide_patriarch"].update(level_min=10, level_max=12)
    k = P["razorhill_kolkar_approach"]
    k.update(level_min=8, level_max=11)
    k["objectives"][0].update(
        target="Kolkar Warrider",
        alt_targets=["Kolkar Outrunner", "Kolkar Wrangler", "Kolkar Pack Runner", "Kolkar Windchaser"])
    P["razorhill_warlord_krellian"].update(level_min=10, level_max=12)
    P["razorhill_scuttle_coast"].update(level_min=7, level_max=10)
    P["razorhill_scuttle_coast"]["objectives"][0].update(
        alt_targets=["Coastal Murloc", "Murloc Oracle", "Drowned Deckhand", "Murloc Netcaster"])


def main():
    data = json.loads(DUROTAR_FILE.read_text())
    by_id = {q["quest_id"]: q for q in data["quests"]}
    order = [q["quest_id"] for q in data["quests"]]
    patch_existing(by_id)
    for q in new_quests():
        rewards = q.pop("rewards")
        q["unique_item_defs"] = rewards
        q["gear_reward_gear_level"] = max(r["item_level"] for r in rewards)
        if max(r["item_level"] for r in rewards) >= 13:
            q["gear_reward_rarity"] = "rare"
        q.setdefault("next_quest_id", None)
        if q["quest_id"] not in by_id:
            order.append(q["quest_id"])
        by_id[q["quest_id"]] = q
    data["quests"] = [by_id[i] for i in order]
    DUROTAR_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    rd = json.loads(RAZOR_FILE.read_text())
    rby = {q["quest_id"]: q for q in rd["quests"]}
    patch_razor(rby)
    RAZOR_FILE.write_text(json.dumps(rd, indent=2, ensure_ascii=False) + "\n")

    # ---- quest-item drops
    drops = json.loads(DROPS_FILE.read_text())
    D = drops["drops"]
    D["Durotar Prowler"] = [{"item_id": "durotar_prowler_pelt", "name": "Prowler Pelt", "category": "quest",
                             "description": "A thick, sand-coloured pelt, still warm. Grosk says it's the best blanket money can't buy.",
                             "chance": 0.5}]
    D["Mesa Stonebiter"] = [{"item_id": "mesa_ore", "name": "Glittering Mesa Ore", "category": "quest",
                             "description": "A chunk of glittering ore, still faintly gnawed. Fitz would love to know how.",
                             "chance": 0.5}]
    D["Razormane Quilboar"] = [{"item_id": "razormane_toll_pouch", "name": "Razormane Toll Pouch", "category": "quest",
                                "description": "A small leather pouch, heavy with other people's coin. Bok recognises the stitching.",
                                "chance": 0.4}]
    DROPS_FILE.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n")
    print("durotar quests:", len(data["quests"]))


if __name__ == "__main__":
    main()
