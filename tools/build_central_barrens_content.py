#!/usr/bin/env python3
"""Central Barrens content pass (2026-10-21).  Idempotent.

  python3 tools/build_central_barrens_content.py && python3 tools/generate_creatures.py

Map reference (300x300, see tools/handbuilt_central_barrens.py)
  Crossroads gate ....... (150,150) dead centre            Northern Barrens pass (150,4) / Taurajo pass (150,296)
  Durotar landing ....... (270,30) across the Southfury bridge (subzone Southfury Banks)
  Kolkar Plains ......... east half; Kolkar Outpost (222,160), Kodo Graveyard (205,120), Kolkar War Camp (238,112)
  Sentinel Rocks ........ mesa cluster north of the Crossroads (112-182, 82-114); Kodo Herder at (142,82)
  Dreadmist Peak ........ NW massif; Dreadmist Den (box canyon, 50,44)
  Forgotten Pools ....... NW oasis chain (55-107, 62-110)
  Grol'dom Farm (85,145)   Shrine of the Fallen Warrior (50,140)   Lushwater Oasis (75,198)   Wailing mouth (75,223)
  Bramblescar (130,250) / Agama'gor (170,250) flank the south Gold Road
  Raider's Rest Oasis ... SE (225,214), island camp; Ratchet pier (264-291, 270)

LEVEL LADDER   Plains / Sentinel Rocks / Southfury Banks 12-15 | Lushwater, Farm 13-15 | Shrine 14-16
               Kolkar 13-17 | Pools 14-17 | Bramblescar 13-17 | Agama'gor 15-18 | Dreadmist 13-17 (bosses 17)
               Raider's Rest 15-19.  Named rares 14-18.  Bosses Gaharrz / Rathorian / Xelnaz 17.
LOOT           ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    # --- Golden Plains / Sentinel Rocks
    "Plains Thunderhawk": C("beast_fast", 13, 15, "plains_thunderhawk"),
    "Barrens Hyena": C("beast_basic", 12, 14, "barrens_hyena"),
    "Redstone Scorpid": C("vermin_sneaky", 13, 15, "redstone_scorpid"),
    # --- oases
    "Oasis Tangle-Vine": C("elemental_bruiser", 13, 15, "oasis_tangle_vine"),
    "Drowned Pilgrim": C("undead_basic", 14, 17, "drowned_pilgrim"),
    # --- Kodo Graveyard
    "Boneyard Vulture": C("beast_fast", 14, 16, "cb_carrion_vulture"),
    "Kodo Wraith": C("undead_basic", 14, 16, "kodo_wraith"),
    # --- Kolkar
    "Kolkar Taskmaster": C("humanoid_warrior", 14, 17, "kolkar_taskmaster"),
    "Kolkar Windseer": C("humanoid_caster", 14, 17, "kolkar_windseer"),
    # --- Raider's Rest
    "Raider's Rest Smuggler": C("humanoid_rogue", 15, 18, "raiders_smuggler"),
    "Bandit Bombardier": C("humanoid_ranged", 16, 19, "bandit_bombardier"),
    # --- quilboar
    "Razormane Quillthrower": C("humanoid_ranged", 13, 16, "quillthrower"),
    "Bristleback Battleboar": C("beast_basic", 15, 18, "bristleback_battleboar"),
    "Bristleback Briarweaver": C("humanoid_caster", 15, 18, "cb_bristleback_thornweaver"),
    # --- Dreadmist
    "Dreadmist Imp": C("demon_caster", 13, 16, "dreadmist_imp"),
    # --- farm / shrine / banks
    "Farm Poacher": C("humanoid_rogue", 13, 15, "farm_poacher"),
    "Mourning Spirit": C("elemental_caster", 14, 16, "mourning_spirit"),
    "Riverbank Snapper": C("beast_basic", 12, 14, "riverbank_snapper"),
    # --- named rares
    "Old Sunhide": C("beast_large", 14, 14, "old_sunhide", True, 1.7),
    "Stormwing the Skyrider": C("beast_fast", 15, 15, "stormwing_skyrider", True, 1.6),
    "Redrock Matriarch": C("vermin_sneaky", 15, 15, "redrock_matriarch", True, 1.7),
    "Queen Skitterwing": C("vermin_sneaky", 15, 15, "queen_skitterwing", True, 1.7),
    "Maeve the Weeping": C("undead_basic", 16, 16, "maeve_weeping", True, 1.6),
    "Hollowhorn": C("undead_basic", 16, 16, "hollowhorn", True, 1.7),
    "Warbringer Gorrak": C("humanoid_warrior", 17, 17, "warbringer_gorrak", True, 1.7),
    "Silas Quickfinger": C("humanoid_rogue", 18, 18, "silas_quickfinger", True, 1.6),
    "Wardchief Thulg": C("humanoid_warrior", 16, 16, "wardchief_thulg", True, 1.7),
    "Sow-Mother Grunka": C("beast_basic", 17, 17, "sowmother_grunka", True, 1.7),
    "Voidcaller Veshra": C("humanoid_caster", 16, 16, "veshra_voidcaller", True, 1.6),
    "Echo of the Fallen Warrior": C("undead_basic", 15, 15, "fallen_warrior_echo", True, 1.6),
    "Looter-Chief Bazz": C("humanoid_rogue", 14, 14, "bazz_lootchief", True, 1.7),
}

FIXES = {
    # Central-only creatures: pull the level band into the zone ladder
    "Greater Plainstrider": {"level_range": [12, 14]},
    "Zhevra Courser": {"level_range": [12, 14]},
    "Savannah Prowler": {"level_range": [13, 15]},
    "Barrens Giraffe": {"level_range": [12, 14]},
    "Silithid Swarmer": {"level_range": [13, 15]},
    "Silithid Creeper": {"level_range": [13, 15]},
    "Murloc Flesheater": {"level_range": [14, 17]},
    "Watering Hole Crocolisk": {"level_range": [15, 17]},
    "Water Elemental": {"level_range": [13, 15], "ability_kit": "water_elemental"},
    "Dreadmist Cultist": {"level_range": [13, 16], "ability_kit": "dreadmist_cultist"},
    "Dreadmist Warlock": {"level_range": [15, 17], "ability_kit": "dreadmist_warlock"},
    "Rathorian": {"ability_kit": "rathorian", "boss_multiplier": 2.3},
    "Xelnaz": {"ability_kit": "xelnaz"},
    "Gaharrz the Drowned": {"boss_multiplier": 2.4},
}

OPEN_ZONE = {"name": "The Golden Plains", "creatures": {
    "Greater Plainstrider": 3, "Zhevra Courser": 2, "Savannah Prowler": 2, "Plains Thunderhawk": 2,
    "Barrens Hyena": 2, "Barrens Giraffe": 1, "Sunscale Screecher": 1,
    "Old Sunhide": 0, "Stormwing the Skyrider": 0}}


def tbl(display, **c):
    return {"name": display, "creatures": c}


SUBZONES = {
    "Sentinel Rocks": tbl("Sentinel Rocks", **{
        "Redstone Scorpid": 3, "Barrens Hyena": 2, "Plains Thunderhawk": 1, "Redrock Matriarch": 0}),
    "Southfury Banks": tbl("Southfury Banks", **{
        "Riverbank Snapper": 3, "Sunscale Screecher": 2, "Pool Murloc": 1}),
    "Lushwater Oasis": tbl("Lushwater Oasis", **{
        "Silithid Swarmer": 3, "Silithid Creeper": 2, "Oasis Tangle-Vine": 2, "Savannah Prowler": 1,
        "Water Elemental": 1, "Queen Skitterwing": 0}),
    "The Forgotten Pools": tbl("The Forgotten Pools", **{
        "Pool Murloc": 2, "Murloc Flesheater": 2, "Drowned Pilgrim": 2, "Water Elemental": 1,
        "Gaharrz the Drowned": 0, "Maeve the Weeping": 0}),
    "Kolkar Plains": tbl("Kolkar Plains", **{
        "Kolkar Stormer": 2, "Kolkar Drudge": 2, "Kolkar Marauder": 1, "Kolkar Windseer": 1}),
    "Kodo Graveyard": tbl("Kodo Graveyard", **{
        "Boneyard Vulture": 3, "Kodo Wraith": 3, "Barrens Hyena": 2, "Hollowhorn": 0}),
    "Kolkar War Camp": tbl("Kolkar War Camp", **{
        "Kolkar Marauder": 2, "Kolkar Drudge": 2, "Kolkar Taskmaster": 2, "Kolkar Windseer": 2,
        "Kolkar Stormer": 1, "Warbringer Gorrak": 0}),
    "Kolkar Outpost": tbl("Kolkar Outpost", **{
        "Kolkar Drudge": 2, "Kolkar Stormer": 2, "Kolkar Taskmaster": 1, "Kolkar Marauder": 1}),
    "Raider's Rest Oasis": tbl("Raider's Rest Oasis", **{
        "Bandit Outrider": 2, "Bandit Cutthroat": 2, "Raider's Rest Smuggler": 2, "Bandit Bombardier": 1,
        "Watering Hole Crocolisk": 1, "Silas Quickfinger": 0}),
    "Bramblescar": tbl("Bramblescar", **{
        "Razormane Veteran": 4, "Razormane Warcaller": 2, "Razormane Quillthrower": 3, "Wardchief Thulg": 0}),
    "Agama'gor": tbl("Agama'gor", **{
        "Bristleback Raider": 4, "Bristleback Raider Shaman": 2, "Bristleback Battleboar": 3,
        "Bristleback Briarweaver": 2, "Sow-Mother Grunka": 0}),
    "Dreadmist Peak": tbl("Dreadmist Peak", **{
        "Dreadmist Cultist": 4, "Dreadmist Warlock": 2, "Dreadmist Imp": 3, "Voidcaller Veshra": 0}),
    "Dreadmist Den": tbl("Dreadmist Den", **{
        "Dreadmist Cultist": 3, "Dreadmist Warlock": 3, "Dreadmist Imp": 2, "Rathorian": 0, "Xelnaz": 0}),
    "Grol'dom Farm": tbl("Grol'dom Farm", **{
        "Farm Poacher": 3, "Kolkar Drudge": 1, "Barrens Hyena": 1, "Looter-Chief Bazz": 0}),
    "Shrine of the Fallen Warrior": tbl("Shrine of the Fallen Warrior", **{
        "Mourning Spirit": 3, "Kodo Wraith": 1, "Echo of the Fallen Warrior": 0}),
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Plains Thunderhawk": [qd("thunderhawk_pinion", "Thunderhawk Pinion",
                              "A flight feather as long as a forearm, faintly charged. Your hair stands up when you hold it.", 0.5)],
    "Kolkar Windseer": [qd("kolkar_windseer_totem", "Kolkar Windseer Totem",
                           "A bundle of kodo-hair and bone that spins on its own when the wind is wrong. The wind is usually wrong.", 0.5)],
    "Kolkar Stormer": [qd("kolkar_windseer_totem", "Kolkar Windseer Totem",
                          "A bundle of kodo-hair and bone that spins on its own when the wind is wrong. The wind is usually wrong.", 0.25)],
    "Farm Poacher": [qd("groldom_seed_sack", "Grol'dom's Seed Sack",
                        "Burlap, stamped with a hoe. Somebody's whole next season, slung over a thief's shoulder.", 0.5)],
    "Oasis Tangle-Vine": [qd("tangle_vine_heart", "Tangle-Vine Heart",
                             "A knot of green vine that beats, slowly, like it hasn't been told it is dead.", 0.5)],
    "Drowned Pilgrim": [qd("pilgrim_prayer_beads", "Pilgrim's Prayer Beads",
                           "Wooden beads worn smooth by one thumb, over a very long walk to a very dry pool.", 0.5)],
    "Bandit Bombardier": [qd("bandit_powder_keg", "Bandit Powder Keg",
                             "A small keg, a long fuse and a label that says DO NOT in three languages.", 0.5)],
    "Razormane Quillthrower": [qd("razormane_quill_bundle", "Razormane Quill Bundle",
                                  "Thick quills bound in sinew, still tacky with dried poison. Handle by the string.", 0.5)],
    "Razormane Veteran": [qd("razormane_quill_bundle", "Razormane Quill Bundle",
                             "Thick quills bound in sinew, still tacky with dried poison. Handle by the string.", 0.25)],
    "Bristleback Battleboar": [qd("battleboar_tusk", "Battleboar Tusk",
                                  "A yellowed tusk with a notch cut in it for every fight the boar won. There are a lot of notches.", 0.5)],
    "Riverbank Snapper": [qd("snapper_shell_plate", "Snapper Shell Plate",
                             "A palm-wide plate of river-turtle shell, thick as a sword guard and a good deal less polite.", 0.5)],
    "Dreadmist Imp": [qd("smouldering_imp_heart", "Smouldering Imp-Heart",
                         "A cinder the size of a plum. It is still warm, and it still, faintly, giggles.", 0.5)],
}


def pools():
    P = {}
    # ---------------- bosses (L17 -> ilvl 20) ----------------------------------
    P["Gaharrz the Drowned"] = [   # murloc warlord: trident / mail chest / healer cloak / tank shield
        make("Gaharrz's Drowning Trident", "main_hand", "of the Soldier", 20,
             "The tines are barnacled. The shaft is warm. Do not ask whose hand it was last in.", weapon_type="polearm"),
        make("Warlord's Reef-Scale Hauberk", "chest", "of the Beast", 20,
             "Scales off something large and angry, stitched with kelp-cord. It smells exactly how you think.",
             armor_type="mail"),
        make("Cloak of the Forgotten Pools", "back", "of the Restorer", 20,
             "Pool-water has a way of turning clean the longer you wear it. It will not turn the wearer clean.",
             armor_type="cloth"),
        make("Mudscale Tide-Shield", "off_hand", "of Blocking", 20,
             "Forged in a place with no forge. The dent in the middle is the shape of a prayer.", weapon_type="shield")]
    P["Rathorian"] = [             # Dreadmist cult-lord: dark staff / cloth robes / dagger / necro ring
        make("Rathorian's Void-Touched Staff", "main_hand", "of Shadow Wrath", 20,
             "A twisted bough with a lump of something hungry in the fork. It purrs when it's fed.",
             weapon_type="staff"),
        make("Dreadmist Cultmaster's Robes", "chest", "of the Necromancer", 20,
             "Black cloth, red thread. The thread is not thread.", armor_type="cloth"),
        make("Seal-Cutter's Knife", "main_hand", "of the Assassin", 20,
             "A ritual knife for opening things that should stay shut.", weapon_type="dagger"),
        make("Signet of the Seed", "ring", "of the Sorcerer", 20,
             "A ring cut from the same stone as the Seal. It whispers when you take it off. It's worse when you don't.")]
    P["Xelnaz"] = [                # felhound alpha: fang dagger / leather legs / mail belt / hunter ring
        make("Xelnaz's Rending Fang", "main_hand", "of the Bandit", 20,
             "A fang as long as a dagger, set in a hilt of black iron. Something in it is still hungry.",
             weapon_type="dagger"),
        make("Felhide Stalker's Leggings", "legs", "of the Hunt", 20,
             "Cut from hide that was never meant to be cut. The seams hiss faintly at night.",
             armor_type="leather"),
        make("Hound-Master's Chain Belt", "waist", "of the Falcon", 20,
             "Hook-links, heavy as a leash. A leash is what it was.", armor_type="mail"),
        make("Brand of the Hound-Lord", "ring", "of the Tiger", 20,
             "A ring-shaped scar in iron. It is warm. It is always warm.")]
    # ---------------- named rares ------------------------------------------------
    P["Old Sunhide"] = [           # L14 -> 17  giant giraffe: leather chest / hammer / tank belt
        make("Sunhide Hunter's Jerkin", "chest", "of the Monkey", 17,
             "Hide the colour of dry grass, cured till it stopped being a giraffe. The spots are still there.",
             armor_type="leather"),
        make("Hoofbeat Maul", "main_hand", "of the Gladiator", 17,
             "A hoof, a haft and a lot of upward momentum.", weapon_type="mace_2h"),
        make("Tall-Grass Girdle", "waist", "of the Bear", 17,
             "A belt you can't see in a savannah. Many have tried.", armor_type="plate")]
    P["Stormwing the Skyrider"] = [  # L15 -> 18  thunderhawk: bow / mail shoulders / caster cloak / agi ring
        make("Stormwing's Longbow", "ranged", "of the Marksman", 18,
             "Strung with thunderhawk sinew. It hums in the rain. Nobody has survived the lightning to explain why.",
             weapon_type="bow"),
        make("Skyrider's Pinion Spaulders", "shoulder", "of the Eagle", 18,
             "Flight-feathers over chain. They lift slightly when you lie.", armor_type="mail"),
        make("Cape of Charged Wings", "back", "of the Sorcerer", 18,
             "It stands up on end before a storm, like a cat, or a wizard.", armor_type="cloth")]
    P["Redrock Matriarch"] = [       # L15 -> 18  scorpid queen: plate shoulders / venom dagger / caster ring
        make("Matriarch's Carapace Pauldrons", "shoulder", "of the Defender", 18,
             "Chitin plate, ridge on ridge. Nothing bites you through it twice.", armor_type="plate"),
        make("Redrock Venom-Blade", "main_hand", "of the Assassin", 18,
             "The groove along the edge is for the venom. The venom is optional. The edge is not.",
             weapon_type="dagger"),
        make("Brood-Queen's Clasp", "ring", "of the Owl", 18,
             "A tiny pincer holds a tinier gem. Don't think about it.")]
    P["Queen Skitterwing"] = [       # L15 -> 18  silithid queen: caster mace / leather helm / healer ring
        make("Skitterwing's Chitin Rod", "main_hand", "of Nature's Wrath", 18,
             "A rod of fused chitin with a pulsing grub-sac at the tip. Do not squeeze.", weapon_type="mace_1h"),
        make("Hivecrown Cowl", "head", "of the Wolf", 18,
             "Chitin plates sewn onto hide. Insects stop biting you the day you put it on. That should worry you.",
             armor_type="leather"),
        make("Queen's Amber Signet", "ring", "of the Restorer", 18,
             "A droplet of old hive-resin, with something inside that remembers being alive.")]
    P["Maeve the Weeping"] = [       # L16 -> 19  drowned pilgrim: healer staff / cloth legs / mail wrists / neck
        make("Staff of the Weeping Pilgrim", "main_hand", "of the Prophet", 19,
             "A pilgrim's walking staff, still walking. The tip is always damp.", weapon_type="staff"),
        make("Pool-Sodden Pilgrim's Skirt", "legs", "of the Physician", 19,
             "Heavy with prayer and forty years of water. It dries when someone is healed.",
             armor_type="cloth"),
        make("Wristbands of Unanswered Prayers", "wrist", "of the Seer", 19,
             "Mail links stamped with names. All of them were asking for the same thing.", armor_type="mail"),
        make("Tear of the Forgotten Pool", "neck", "of the Archmage", 19,
             "A teardrop of pool-glass on a leather cord. It rings softly when something nearby is sad.")]
    P["Hollowhorn"] = [              # L16 -> 19  kodo wraith: 2H axe / plate legs / tank neck
        make("Hollowhorn's Gravetusk Cleaver", "main_hand", "of the Champion", 19,
             "A kodo tusk split lengthwise, ground to an edge. It remembers the herd.", weapon_type="axe_2h"),
        make("Boneyard Plate Leggings", "legs", "of the Juggernaut", 19,
             "Kodo ribs, riveted and lacquered. They creak the way graveyard gates do.", armor_type="plate"),
        make("Herd-Memory Pendant", "neck", "of the Ironfur", 19,
             "A small carved kodo on a cord. It is heavier than it looks, and it is not heavy.")]
    P["Warbringer Gorrak"] = [       # L17 -> 20  Kolkar warlord: lance / mail chest / tank helm / hunter ring
        make("Gorrak's Warbringer Lance", "main_hand", "of the Soldier", 20,
             "A centaur's lance, cut for a man's hand. It is still lopsided, because he is not.",
             weapon_type="polearm"),
        make("Kolkar Warlord's Hauberk", "chest", "of the Tiger", 20,
             "Hide, bone and brass bolted over mail. It reads like a banner if you stand far enough away.",
             armor_type="mail"),
        make("Helm of the Hoofed Horde", "head", "of the Bulwark", 20,
             "A bull-skull helm with the horns sawed off to fit a doorway.", armor_type="plate"),
        make("Warbringer's Rallying Band", "ring", "of the Hunt", 20,
             "A warlord's ring. Armies were raised on it. None of them were polite.")]
    P["Silas Quickfinger"] = [       # L18 -> 21  bandit boss: dagger / leather gloves / gun / agi trinket
        make("Quickfinger's Lamp-Oil Stiletto", "main_hand", "of the Assassin", 21,
             "Thin as a rumor. It slides in so fast you don't notice till later.", weapon_type="dagger"),
        make("Gloves of Light Pockets", "hands", "of the Monkey", 21,
             "Your coin purse will remember them. It just won't be able to prove anything.",
             armor_type="leather"),
        make("Quickfinger's Smuggled Pistol", "ranged", "of the Marksman", 21,
             "Bought from a man who didn't have a stall. Fires like it's late for something.", weapon_type="gun"),
        make("Charm of the Third Pocket", "neck", "of the Bandit", 21,
             "A tiny silver lock. Open it and there's another lock. Silas thinks it's funny.")]
    P["Wardchief Thulg"] = [         # L16 -> 19  Razormane wardchief: 2H mace / mail boots / tank off-hand
        make("Thulg's Boarhide Cleaver", "main_hand", "of the Gladiator", 19,
             "A quilboar's idea of an axe: wide, heavy and deeply insulted.", weapon_type="axe_2h"),
        make("Wardchief's Thorn-Tied Boots", "feet", "of the Bear", 19,
             "Boar-hide wrapped around thorn-wood soles. Hurts to step on. Hurts more to be stepped on.",
             armor_type="mail"),
        make("Razormane Thorn Bulwark", "off_hand", "of the Defender", 19,
             "A shield of woven thorn. Yes, it hurts to hold. That is the design.", weapon_type="shield")]
    P["Sow-Mother Grunka"] = [       # L17 -> 20  Bristleback sow: caster mace / leather bracers / healer cloak
        make("Sow-Mother's Brood-Bell", "main_hand", "of the Spell Breaker", 20,
             "A bone bell, struck to call the brood. The brood has stopped answering. Interesting.",
             weapon_type="mace_1h"),
        make("Bristle-Woven Bracers", "wrist", "of the Wolf", 20,
             "Boar bristle, braided into a bracer. It is much more comfortable than it sounds.",
             armor_type="leather"),
        make("Mantle of the Brood-Mother", "back", "of the Restorer", 20,
             "A cloak of sow-hide. It's gentler than its wearer was, which is to say not much.",
             armor_type="cloth")]
    P["Voidcaller Veshra"] = [       # L16 -> 19  Dreadmist voidcaller: shadow wand / cloth hood / tank ring
        make("Veshra's Rift-Whisper Wand", "ranged", "of Shadow Wrath", 19,
             "A wand carved from a bone nobody asked about. It whispers at night.", weapon_type="wand"),
        make("Voidcaller's Cowl", "head", "of the Invoker", 19,
             "Black cloth, red lining. Peering into it is how the lining got red.", armor_type="cloth"),
        make("Hollow Ward Signet", "ring", "of the Warder", 19,
             "The stone is empty. The emptiness is the point.")]
    P["Echo of the Fallen Warrior"] = [   # L15 -> 18  shrine echo: 1H sword / plate wrist / healer neck
        make("Fallen Warrior's Echo-Blade", "main_hand", "of the Champion", 18,
             "A spirit-forged sword from a shrine that doesn't remember its name. The edge does.",
             weapon_type="sword_1h"),
        make("Vambraces of Valour Remembered", "wrist", "of the Bastion", 18,
             "Plate vambraces that carry the weight of a battle no one was alive to finish.",
             armor_type="plate"),
        make("Shrine-Keeper's Amulet", "neck", "of the Hierophant", 18,
             "A small, quiet stone on a leather cord. Wearing it feels a little like being forgiven.")]
    P["Looter-Chief Bazz"] = [       # L14 -> 17  farm looter: pitchfork / leather vest / agi ring
        make("Bazz's Stolen Pitchfork", "main_hand", "of the Squire", 17,
             "Three tines, one of them bent. It was stolen from a farm, and it knows it.", weapon_type="polearm"),
        make("Looter's Padded Vest", "chest", "of the Bandit", 17,
             "Layers of stolen cloth, sewn with prejudice. There's an extra pocket for everything.",
             armor_type="leather"),
        make("Scrap-Iron Signet", "ring", "of the Monkey", 17,
             "A ring made of whatever Bazz had in his pockets. Somehow it's stylish.")]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    data = json.loads(cp.read_text(encoding="utf-8"))
    cr = data["creatures"]
    cr.update(NEW_CREATURES)
    for n, patch in FIXES.items():
        cr[n].update(patch)
    cr["Water Elemental"].pop("kit", None)
    cp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    ep = ROOT / "data/creatures/encounters.json"
    data = json.loads(ep.read_text(encoding="utf-8"))
    z = data["zones"]["Central Barrens"]
    z["open_zone"] = OPEN_ZONE
    z["subzones"] = SUBZONES
    ep.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    qp = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(qp.read_text(encoding="utf-8"))
    D = data["drops"]
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    out = {"_notes": "Central Barrens boss + named-rare loot (2026-10-21). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/central_barrens_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, tables {len(SUBZONES)} subzones, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
