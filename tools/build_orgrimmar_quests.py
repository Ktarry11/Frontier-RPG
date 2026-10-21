"""
Orgrimmar quest pass (2026-10-21).  Idempotent: rewrites data/quests/orgrimmar.json.

    python3 tools/build_orgrimmar_quests.py

Nothing used to send low levels to Ragefire Chasm.  Nine quests from six Orgrimmar
NPCs now do, one per layer of the dungeon:
  Thrall ........ chain: Embers Beneath the Valley -> Hunger in the Lake (Taragaman)
                  -> The Sinister Edge (Bazzalan)
  Shade of Thalorien (rogues) ... Whispers in the Cleft (Searing Blade trash)
  Malzhet the Bound (warlocks) .. Binding the Invoker (Jergosh + Voidwalkers)
  Krunk Anvilfist (smith) ....... Ore of the Deep -> The Pitbreaker (rare Grulgash)
  Apothecary Zurm ............... Hexed Ash (rare Acolyte Zhurra Bloodhex)
  Rethok the Hunter ............. Cinderfang (rare salamander)
Rewards are hand-crafted with the real stat formulas (secondary stats, ilvl >= 10).
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_quests import item, kill, fetch   # noqa: E402

OUT = ROOT / "data/quests/orgrimmar.json"


def quests():
    Q = []

    # ============================== THRALL: the dungeon chain =========================
    Q.append(dict(
        quest_id="org_embers_beneath", title="Embers Beneath the Valley", giver_npc_id="org_thrall",
        zone="orgrimmar", level_min=12, level_max=16, next_quest_id="org_hunger_in_the_lake",
        description=("The warm vents under the Cleft of Shadow used to be only warm. For a month now they have been "
                     "loud: picks, drums, and a smell of sulphur that does not belong to nature. Troggs who have not "
                     "come near the city in a generation are streaming up out of Ragefire Chasm, and behind them there "
                     "is something with a purpose. Thrall does not like things with a purpose that he has not given them."),
        objectives=[kill("Ragefire Trogg", 8), kill("Ragefire Shaman", 5)],
        reward_exp=900, reward_gold=3600,
        accept_text=("Go down through the Cleft. The troggs first - they are the loud part - and their shamans, who are "
                     "keeping them loud. Bring me back what the chasm has become. I will not send a tide of warriors "
                     "into a place I do not understand."),
        turn_in_text=("So it is not only troggs. Good - I would rather know. The Cleft is quieter already. "
                      "But something down there is feeding that fire. Take this, and listen to me again."),
        rewards=[
            item("Cleft-Watch Tunic", "chest", "of the Beast", 14,
                 "Hardened hide with a cinder-stain at the cuff. The Cleft's own.", "Leather Chest (Str/Agi/Sta)",
                 armor="leather", req=11),
            item("Trogg-Bone Shield", "off_hand", "of Blocking", 14,
                 "Two thighbones and a prayer. It has already survived a trogg.", "Shield (Str/Block)",
                 weapon="shield", req=11),
            item("Emberdew Charm", "neck", "of the Archmage", 14,
                 "A sliver of obsidian that stays warm. The shamans guarded it jealously.",
                 "Necklace (Int/SP/MP5)", req=11),
        ]))
    Q.append(dict(
        quest_id="org_hunger_in_the_lake", title="Hunger in the Lake", giver_npc_id="org_thrall",
        zone="orgrimmar", level_min=14, level_max=17, next_quest_id="org_sinister_edge",
        description=("The cultists did not find the lava lake - they found what lives in it. Taragaman the Hungerer is an "
                     "elemental older than the city, and for ten thousand years he has done nothing but burn and wait. "
                     "Someone has been feeding him, binding him, and pointing him at Orgrimmar. A bound spirit of that "
                     "size is not a weapon. It is a fuse."),
        objectives=[kill("Taragaman the Hungerer", 1)],
        reward_exp=1500, reward_gold=5600,
        accept_text=("Beyond the antechamber the chasm opens onto a lake of fire with two stone bridges across it. "
                     "Taragaman sits where they cross. Do not fight him on the bridges for longer than you must."),
        turn_in_text=("He is out. The Hungerer is out. I felt the vents quiet from here. Thank you - for the first time in "
                      "a month the city is breathing right. There is still the one who held his chain."),
        rewards=[
            item("Hungerer's Cinderstaff", "main_hand", "of Fiery Wrath", 18,
                 "Burned from the inside out. The grain still glows.", "Staff (Fire Spell Power)",
                 weapon="staff", req=15, rarity="rare"),
            item("Lava-Seared Breastplate", "chest", "of the Champion", 18,
                 "It leaves a char mark on anything that touches it. Anything that touches it deserves it.",
                 "Plate Chest (Str/Sta/Def)", armor="plate", req=15, rarity="rare"),
            item("Smolderfang Band", "ring", "of the Hunt", 18,
                 "Ring-bone from a lake creature that bit back. Still hot.", "Ring (Agi/Int/AP)", req=15, rarity="rare"),
            item("Cinderspirit's Mending Wraps", "wrist", "of the Restorer", 18,
                 "Woven from ash-silk that mends faster than it burns.", "Cloth Bracers (Healing/MP5)",
                 armor="cloth", req=15, rarity="rare"),
        ]))
    Q.append(dict(
        quest_id="org_sinister_edge", title="The Sinister Edge", giver_npc_id="org_thrall",
        zone="orgrimmar", level_min=15, level_max=18, next_quest_id=None,
        description=("Every cult needs a blade, and the Searing Blade's is a trogg-hater named Bazzalan. He sits on an "
                     "obsidian throne at the end of the chasm, in a hall that was an orc shrine before it was theirs. "
                     "He does not shout. He does not pose. He waits for you to look at the wrong corner of the room."),
        objectives=[kill("Searing Blade Fanatic", 6), kill("Bazzalan", 1)],
        reward_exp=1700, reward_gold=6400,
        accept_text=("His walkway lies beyond the Invoker's ritual hall. Take your time and your healers. "
                     "A cult is a body, and Bazzalan is the knife it holds in the dark."),
        turn_in_text=("Bring the throne to dust, they said, and you did more than that. The Searing Blade's hold on my "
                      "city is broken - at least for now. Wear this with pride. The Horde remembers who stands in the "
                      "dark so others may sleep."),
        rewards=[
            item("Thrall's Gift: Hammerfall", "main_hand", "of the Juggernaut", 19,
                 "Forged in Orgrimmar's own forges for a champion Thrall did not have to name.",
                 "Mace (Sta/Armor/Parry)", weapon="mace_1h", req=16, rarity="rare"),
            item("Dark-Edge Duelist's Blade", "main_hand", "of the Assassin", 19,
                 "Sharper than its owner was careful. Still sharp.", "Sword (Agi/Hit/Crit)",
                 weapon="sword_1h", req=16, rarity="rare"),
            item("Mantle of the Third Fire", "shoulder", "of the Prophet", 19,
                 "Orgrimmar's own shamans wove the cord. It knows your name.", "Cloth Shoulders (Int/Spi/Healing)",
                 armor="cloth", req=16, rarity="rare"),
            item("Horde Marshal's Sabatons", "feet", "of the Soldier", 19,
                 "Heavy plate that remembers every road Orgrimmar ever paved.", "Plate Boots (Str/Sta/Crit)",
                 armor="plate", req=16, rarity="rare"),
        ]))

    # ============================== SHADE OF THALORIEN ===============================
    Q.append(dict(
        quest_id="org_whispers_cleft", title="Whispers in the Cleft", giver_npc_id="org_rogue_trainer",
        zone="orgrimmar", level_min=13, level_max=16, next_quest_id=None,
        description=("The Cleft of Shadow has always belonged to the quiet kind of orc. That does not mean it belongs to "
                     "whoever claims the quiet. A cult calling itself the Searing Blade has been using the Cleft's own "
                     "back tunnels to run their ritual stock into the chasm below. The Shade is not pleased. A thief has "
                     "a code, and the code does not include sacrifices."),
        objectives=[kill("Searing Blade Cultist", 6), kill("Searing Blade Fanatic", 4), kill("Searing Blade Invoker", 3)],
        reward_exp=1000, reward_gold=3800,
        accept_text=("They hide behind candlelight. You can use that. Go in through the gate in the Cleft and take them "
                     "as they come - the cultists first, the fanatics who guard them, the invokers who command them."),
        turn_in_text=("Their whispers have gone quiet. Good. I will be back to my usual clientele by dusk. "
                      "Here - a small thank-you from a very small ghost."),
        rewards=[
            item("Shade-Silk Hood", "head", "of the Wolf", 15,
                 "Dark enough to lose a shadow in. It does not lose you.", "Leather Hood (Agi/Spi)",
                 armor="leather", req=12),
            item("Cleftrunner's Dirk", "main_hand", "of the Assassin", 15,
                 "A knife for someone who prefers a quiet exit.", "Dagger (Agi/Hit/Crit)", weapon="dagger", req=12),
            item("Whisper-Thread Cloak", "back", "of the Monkey", 15,
                 "The weave swallows sound. Small ones, anyway.", "Cloak (Agi/Sta)", armor="cloth", req=12),
        ]))

    # ============================== MALZHET THE BOUND ================================
    Q.append(dict(
        quest_id="org_binding_invoker", title="Binding the Invoker", giver_npc_id="org_warlock_trainer",
        zone="orgrimmar", level_min=15, level_max=18, next_quest_id=None,
        description=("Malzhet has spent a lifetime learning where a warlock's contract ends. Jergosh the Invoker has "
                     "built a chamber in the chasm and a cult around the idea that it ends nowhere. Voidwalkers he did "
                     "not earn walk his ritual hall. Malzhet recognises the shape of the mistake - it is his own, "
                     "twenty years ago - and has no wish to see it repeated at city scale."),
        objectives=[kill("Voidwalker Minion", 5), kill("Jergosh the Invoker", 1)],
        reward_exp=1550, reward_gold=5800,
        accept_text=("Jergosh's chamber lies north of the lake. Mind the voidwalkers - they are his hands, and he has "
                     "never once had to use his own. When he falls, break the circle. Do not read what is in it."),
        turn_in_text=("The circle is broken. Then the debt is paid, at least in part. Take it - a better warlock than "
                      "I was used to carry it. I would be pleased if you were better than either of us."),
        rewards=[
            item("Binder's Grimoire", "main_hand", "of the Necromancer", 18,
                 "A cracked spine, warm pages. The marginalia is not in a language the living use.",
                 "Staff (Int/Sta/Hit)", weapon="staff", req=15, rarity="rare"),
            item("Voidtouched Robes", "chest", "of the Void", 18,
                 "Cut for someone comfortable being looked at by things that are not there.",
                 "Cloth Chest (Shadow/Arcane SP)", armor="cloth", req=15, rarity="rare"),
            item("Soul-Anchor Pendant", "neck", "of the Whale", 18,
                 "Stops you from drifting. A soul is a heavy thing to carry alone.", "Necklace (Sta/Spi)",
                 req=15, rarity="rare"),
            item("Invoker's Ward-Gloves", "hands", "of the Elder", 18,
                 "A little heavier than they look. Cults pay in leather as well as blood.",
                 "Leather Gloves (Int/Sta/MP5)", armor="leather", req=15, rarity="rare"),
        ]))

    # ============================== KRUNK ANVILFIST =================================
    Q.append(dict(
        quest_id="org_ore_deep", title="Ore of the Deep", giver_npc_id="org_smith",
        zone="orgrimmar", level_min=12, level_max=16, next_quest_id="org_pitbreaker",
        description=("Krunk keeps one piece of black rock above his anvil, and he has been staring at it for a week. "
                     "It came from the mining spur under the Cleft, and it is the best ore he has ever put a hammer to. "
                     "He wants more. The troggs digging it up and the elementals warming it down below are, in his view, "
                     "a very small obstacle."),
        objectives=[fetch("ragefire_ore_sample", 8)],
        reward_exp=900, reward_gold=3400,
        accept_text=("Troggs mine it. Elementals nest in it. Bring me eight lumps - black, shot with orange. "
                     "You will know it when you pick it up. It will want to burn your hand."),
        turn_in_text=("Look at that grain. Look at it. I could make a blade from this that would sing. "
                      "Not today - but I will not forget who brought it. Here, something from the racks."),
        rewards=[
            item("Anvilfist's Spare Maul", "main_hand", "of the Bear", 14,
                 "He made six of them. This is the one that did not hit the wall.", "Mace (Str/Sta)",
                 weapon="mace_2h", req=11),
            item("Forgeguard Bracers", "wrist", "of the Defender", 14,
                 "Riveted twice, because Krunk does not trust anything done once.", "Plate Bracers (Sta/Def/Dodge)",
                 armor="plate", req=11),
            item("Spark-Ember Belt", "waist", "of the Falcon", 14,
                 "Studded with rejected rivets. The sparks are a feature.", "Leather Belt (Agi/Int)",
                 armor="leather", req=11),
        ]))
    Q.append(dict(
        quest_id="org_pitbreaker", title="The Pitbreaker", giver_npc_id="org_smith",
        zone="orgrimmar", level_min=14, level_max=17, next_quest_id=None,
        description=("The best ore in the spur belongs to a trogg called Grulgash. He is not a warlord - he is a miner, "
                     "with a miner's grudge, and a hammer that has broken more pit-props than Krunk has forged blades. "
                     "Nobody mines the black seam while Grulgash is breathing. Krunk would pay a fair bit to see "
                     "that change."),
        objectives=[kill("Ragefire Digger", 6), kill("Grulgash the Pitbreaker", 1)],
        reward_exp=1250, reward_gold=4800,
        accept_text=("West of the warrens, past the supply racks. The diggers first - they keep him informed. "
                     "Grulgash is bigger than he looks and angrier than he sounds."),
        turn_in_text=("The seam is open. I'll have the smiths down there before the week is out. "
                      "As for the hammer - I do not need it. You do. Take your pick."),
        rewards=[
            item("Seamcutter's Warhammer", "main_hand", "of Striking", 17,
                 "A miner's hammer with a smith's temper. It has nothing left to prove.", "Mace (Str/Agi/Sta)",
                 weapon="mace_1h", req=14, rarity="rare"),
            item("Black-Seam Chainmail", "chest", "of the Marksman", 17,
                 "Mail woven from wire drawn from that seam. It does not rust, and it does not apologise.",
                 "Mail Chest (Agi/Sta/Hit)", armor="mail", req=14, rarity="rare"),
            item("Lantern-Hook Ring", "ring", "of the Defender", 17,
                 "A hook, a band, and enough stubbornness to hold a mine up.", "Ring (Sta/Def/Dodge)",
                 req=14, rarity="rare"),
            item("Dust-Wrap Mitts", "hands", "of the Prophet", 17,
                 "Soft inside, plated outside, and very good at not being noticed.", "Cloth Gloves (Int/Spi/Healing)",
                 armor="cloth", req=14, rarity="rare"),
        ]))

    # ============================== APOTHECARY ZURM =================================
    Q.append(dict(
        quest_id="org_hexed_ash", title="Hexed Ash", giver_npc_id="orgrimmar_alchemist",
        zone="orgrimmar", level_min=13, level_max=17, next_quest_id=None,
        description=("The Searing Blade does not burn its offerings for flavour. The ash is a reagent, and the "
                     "reagent is a curse, and a curse needs a hand. Zurm has been analysing the ash his customers "
                     "brought back for a week, and he has learned that every sample points the same way: down the "
                     "chasm, to a priestess called Zhurra Bloodhex."),
        objectives=[fetch("searing_ritual_ash", 6), kill("Acolyte Zhurra Bloodhex", 1)],
        reward_exp=1300, reward_gold=5000,
        accept_text=("Pyromancers and cultists carry the ash. Zhurra is the one who makes it mean something. "
                     "She holds the altar in the antechamber, behind the cages. Do not touch the ash with bare skin."),
        turn_in_text=("I will not ask what you saw. I will say that the sample matches. "
                      "Her curse is broken at the root. I would like you to have something from my own stock."),
        rewards=[
            item("Apothecary's Mending Mantle", "shoulder", "of the Hierophant", 17,
                 "Smells of lavender and tincture. The knots hold - they have been tested.",
                 "Cloth Shoulders (Healing/Spi/Sta)", armor="cloth", req=14, rarity="rare"),
            item("Zhurra's Kris, Reforged", "main_hand", "of the Tactician", 17,
                 "A blade cleaned of its work. It still remembers its work.", "Dagger (Int/Hit/SP)",
                 weapon="dagger", req=14, rarity="rare"),
            item("Vial-Bandolier", "waist", "of the Physician", 17,
                 "A belt with a dozen empty loops and an honest smell of alcohol.", "Leather Belt (Sta/Int/Healing)",
                 armor="leather", req=14, rarity="rare"),
            item("Hexbreaker Talisman", "neck", "of the Spell Breaker", 17,
                 "A paper charm in a glass bead. Zurm made it in an afternoon and will deny it.",
                 "Necklace (Spell Power/Pen)", req=14, rarity="rare"),
        ]))

    # ============================== RETHOK THE HUNTER ===============================
    Q.append(dict(
        quest_id="org_cinderfang", title="Cinderfang", giver_npc_id="org_hunter",
        zone="orgrimmar", level_min=14, level_max=17, next_quest_id=None,
        description=("Rethok does not hunt for sport. He hunts what threatens the herd, and a salamander the size of a "
                     "wolf has taken to the shores of the lava lake beneath the city. The troggs call it Cinderfang. "
                     "They keep their distance. Rethok keeps a list of animals he has failed to bring home, and the "
                     "list is short."),
        objectives=[kill("Cinder Salamander", 6), kill("Cinderfang", 1)],
        reward_exp=1350, reward_gold=5200,
        accept_text=("It lairs on the north-east shore of the lake. The lesser ones lead you to it - they are always "
                     "near a bigger one. Keep to the stone, do not touch the lava, and do not run."),
        turn_in_text=("A clean kill. I have seen that pelt on a trogg's wall once. Not now. "
                      "Pick whichever you will use - I would only have it hung."),
        rewards=[
            item("Cinderfang's Bow", "ranged", "of the Falcon", 18,
                 "Strung with salamander-gut. It sings when drawn.", "Bow (Agi/Int)", weapon="bow", req=15, rarity="rare"),
            item("Embersilk Jerkin", "chest", "of the Hunt", 18,
                 "Leather lined with ash-silk. Warm in the cold; lightly warm in the heat.",
                 "Leather Chest (Agi/Int/AP)", armor="leather", req=15, rarity="rare"),
            item("Salamander-Scale Greaves", "legs", "of the Beast", 18,
                 "Scales still glinting. A hunter's trophy, and a hunter's armour.", "Mail Legs (Str/Agi/Sta)",
                 armor="mail", req=15, rarity="rare"),
            item("Hunter's Ember-Totem", "ranged", "of the Restorer", 18,
                 "Carved from the shore-stone where the salamander denned. Warm enough to hold in winter.",
                 "Totem (Healing/MP5)", weapon="totem", req=15, rarity="rare"),
        ]))
    return Q


def main():
    Q = quests()
    out = []
    for q in Q:
        rewards = q.pop("rewards")
        q["unique_item_defs"] = rewards
        q["gear_reward_gear_level"] = max(r["item_level"] for r in rewards)
        if max(r["item_level"] for r in rewards) >= 15:
            q["gear_reward_rarity"] = "rare"
        q.setdefault("next_quest_id", None)
        out.append(q)
    OUT.write_text(json.dumps({"quests": out}, indent=2, ensure_ascii=False) + "\n")
    print("orgrimmar quests:", len(out), "items:", sum(len(q["unique_item_defs"]) for q in out))


if __name__ == "__main__":
    main()
