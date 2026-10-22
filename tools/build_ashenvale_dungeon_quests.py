#!/usr/bin/env python3
"""Dungeon quests for Moonwell Hollow, Howling Barrows and Grom's Rest -> data/quests/ashenvale_dungeons.json.  Idempotent.

    python3 tools/build_ashenvale_dungeon_quests.py && python3 tools/retier_quest_rewards.py

Kyle's rules: dungeon quests are kill / fetch / boss ONLY (no escorts), dungeons are party content.  Quest givers are existing
NPCs (Astranaar for the West dungeon, Splintertree Post for the East ones).  XP/gold follow the same level medians as the open
world (tools/relevel_ashenvale); boss kills pay more.  Reward stats are re-derived from the item level by retier_quest_rewards.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.relevel_ashenvale import _XP, _GOLD, _base  # noqa: E402

QUESTS = []


def item(name, slot, ilvl, flavor, stats, rarity="uncommon", armor_type=None, weapon_type=None):
    d = {"name": name, "slot": slot, "item_level": ilvl, "rarity": rarity, "flavor_text": flavor, "primary_stats": stats}
    if armor_type:
        d["armor_type"] = armor_type
    if weapon_type:
        d["weapon_type"] = weapon_type
    return d


def quest(qid, title, giver, zone, lo, hi, desc, objectives, accept, turn_in, items=(), mult=1.0, nxt=None, boss=False):
    ilvl = hi if boss else hi - 1
    q = {
        "quest_id": qid, "title": title, "giver_npc_id": giver, "zone": zone, "level_min": lo, "level_max": hi,
        "description": desc, "objectives": objectives,
        "reward_exp": int(round(_base(_XP, lo, 100) * mult / 50.0) * 50),
        "reward_gold": int(round(_base(_GOLD, lo, 270) * mult / 100.0) * 100),
        "accept_text": accept, "turn_in_text": turn_in,
    }
    if nxt:
        q["next_quest_id"] = nxt
    if items:
        q["gear_reward_gear_level"] = ilvl
        q["unique_item_defs"] = [dict(i, item_level=ilvl) for i in items]
    QUESTS.append(q)


def kill(target, n, zone, alt=None):
    o = {"type": "kill", "target": target, "count": n, "zone": zone}
    if alt:
        o["alt_targets"] = alt
    return o


def boss(target, zone):
    return {"type": "kill_boss", "target": target, "count": 1, "zone": zone}


def fetch(target, n):
    return {"type": "fetch", "target": target, "count": n}


# ===================================================================================== MOONWELL HOLLOW (West, 22-25)
MW = "moonwell_hollow"
quest("moonwell_blighted_roots", "Roots of the Blight", "astranaar_grove_warden", "astranaar", 22, 24,
      "Grove Warden Pennarin has seen the Moonwell's roots come up black at the edges. She wants samples from the Twilight "
      "Rootbinders who tend them, taken before the rot reaches the Grove proper.",
      [fetch("moonwell_root_sample", 5)],
      "Rootbinders. They sing to the roots and the roots sing back, and the song is wrong. Bring me what they're carrying.",
      "Black at the core, and warm. That is not sap. Thank you. Now we know how deep it goes.",
      items=[item("Pennarin's Rootwoven Cord", "waist", 23, "Braided from roots that were green when she wove them.",
                  {"agility": 4, "stamina": 3}, armor_type="leather")])
quest("moonwell_gloomcap_sacs", "A Fungus Among Us", "astranaar_sentinel_liaison", "astranaar", 22, 24,
      "Sentinel Liaison Valea needs gloomcap spore sacs from the Sporelings below the Moonwell, to learn whether the spread "
      "can be burned out or must be cut out.",
      [fetch("gloomcap_spore_sac", 6)],
      "Gently. They burst, and then you will smell it for a week. Bring me six, unbroken.",
      "Unbroken. I'm impressed. The healers will want to know what these are feeding on.",
      items=[item("Valea's Sporeguard Wraps", "wrist", 23, "Cloth wrapped twice, then waxed. For the smell.",
                  {"intellect": 3, "spirit": 3}, armor_type="cloth")])
quest("moonwell_hollow_cull", "Silence the Hollow", "astranaar_grove_warden", "astranaar", 22, 25,
      "The corrupted things beneath the Moonwell are growing bolder. Thin the Rotlashers and Moon Guards so the next party "
      "can reach the grove at the bottom.",
      [kill("Hollow Rotlasher", 8, MW), kill("Corrupted Moon Guard", 6, MW), kill("Twilight Rootbinder", 4, MW)],
      "Go down in company. The Hollow was never meant to be walked alone, and it is not what it was.",
      "You came back. That is more than the last party managed, and they were braver than they were wise.",
      nxt="moonwell_mosshide")
quest("moonwell_mosshide", "The Gloomcap Elder", "astranaar_grove_warden", "astranaar", 23, 25,
      "An old gloomcap the size of a house sits at the heart of the Hollow's spread. The Sentinels call it Mosshide. Cut it down "
      "and the rot loses its anchor.",
      [boss("Mosshide the Gloomcap Elder", MW)],
      "Mosshide has been there longer than the Moonwell's lamps. Longer than the Sentinels. It will not go quietly.",
      "Then the spread has a hole in it. Good. Rest. Maelwyn is next, and she will be harder.",
      items=[item("Elder's Mosscloak", "back", 25, "Moss grown so thick it has its own weather.",
                  {"stamina": 4, "agility": 3}, rarity="rare", armor_type="cloth")],
      mult=1.3, nxt="moonwell_maelwyn", boss=True)
quest("moonwell_maelwyn", "Maelwyn Blightbloom", "astranaar_grove_warden", "astranaar", 24, 25,
      "Maelwyn was a Moonwell keeper once. Now she is the Blight's flower. End her at the Moonwell, and let the water run clean.",
      [boss("Maelwyn Blightbloom", MW)],
      "She still has the face I remember. Do not let that slow your hand. Do it for her.",
      "...Thank you. I will tell the others the water is clear. I will not tell them how it looked.",
      items=[item("Blightbloom's Last Bloom", "neck", 25, "A white flower pressed in glass. It stopped wilting.",
                  {"intellect": 5, "spirit": 4}, rarity="rare"),
             item("Keeper's Mended Boots", "feet", 25, "Re-stitched by someone who loved them.",
                  {"stamina": 4, "agility": 4}, rarity="rare", armor_type="leather")],
      mult=1.5, boss=True)

# =================================================================================== HOWLING BARROWS (East, 21-24)
HB = "howling_barrows"
quest("barrows_hunters_horns", "Horns of the Wild Hunt", "splintertree_grunt", "splintertree_post", 21, 23,
      "The huntsmen buried in the Barrows carry their horns even in death. Grunt Bloodfang wants them gone, and some of the "
      "horn-bone might ring true for a Horde signal.",
      [fetch("hunters_horn_shard", 5)],
      "I don't care whose horns they are. If they stop calling the dead out of the hill, I'm happy.",
      "Hm. It still howls when the wind touches it. Gives me the chills. Good work.",
      items=[item("Bloodfang's Signal Horn", "ranged", 22, "A hunting horn that no longer needs breath.",
                  {"agility": 4, "stamina": 2}, weapon_type="bow")])
quest("barrows_rimebone_cull", "Rimebone and Wight", "splintertree_interrogator", "splintertree_post", 21, 24,
      "Vashj needs the Barrows quiet. The frozen hounds and wights keep the Hunt-King's road, and as long as they walk the "
      "place will keep singing the Hunt's old song.",
      [kill("Rimebone Hound", 8, HB), kill("Barrow Wight", 6, HB), kill("Howling Wraith", 4, HB)],
      "Dead things in a cold hole. It is not complicated. Go in with friends, come out with the job done.",
      "The howling's thinner. Not gone. Not yet. That's your next job.",
      nxt="barrows_wintermaw")
quest("barrows_wintermaw", "Wintermaw the Howling", "splintertree_interrogator", "splintertree_post", 22, 23,
      "A hound the size of a warhorse is chained in the Houndkeepers' Crypt. The chains are old. The grudge is older.",
      [boss("Wintermaw the Howling", HB)],
      "It will not come to you. You will go to it. Take a healer and take a good reason.",
      "That howl has stopped. I did not know how much of the wind it was until it stopped.",
      items=[item("Houndkeeper's Mended Gloves", "hands", 23, "Whoever repaired these did it badly and with love.",
                  {"strength": 4, "stamina": 3}, armor_type="mail")],
      mult=1.2, nxt="barrows_hunt_king", boss=True)
quest("barrows_hunt_king", "The Hunt-King's Rest", "splintertree_war_mage", "splintertree_post", 23, 24,
      "At the end of the Barrows lies the Hunt-King Valorin, still hunting in his sleep. War Mage Grimtotem will not have a dead "
      "king's hunt ranging over Horde land.",
      [boss("Hunt-King Valorin", HB)],
      "The Wild Hunt never ended, it just went underground. Let's make sure it stays there.",
      "He rode out of the world a long time ago. Now he's finally ridden all the way home.",
      items=[item("Valorin's Rime-Rimmed Cloak", "back", 24, "Frost clings to it in the warmest room.",
                  {"agility": 5, "stamina": 3}, rarity="rare", armor_type="cloth"),
             item("Frostbrand Whetstone Charm", "trinket", 24, "A sharpening stone on a cord. The blade it sharpened is long gone.",
                  {"strength": 3, "agility": 3, "stamina": 2}, rarity="rare")],
      mult=1.4, boss=True)

# ====================================================================================== GROM'S REST (East, 26-32)
GR = "groms_rest"
quest("groms_garrison_cull", "Thin the Garrison", "splintertree_war_mage", "splintertree_post", 26, 29,
      "Grom's Rest has become a demon barracks. Satyrs, imps and fel-touched hounds crowd the hall beyond the gate. War Mage "
      "Grimtotem wants the garrison thinned so a real party can push through.",
      [kill("Satyr Cultist", 10, GR), kill("Dread Imp", 8, GR), kill("Corrupted Felhound", 6, GR)],
      "This is a dungeon, not a stroll. Bring a full party and bring your potions. Then bring me proof the hall is clearer.",
      "Good. The gate is no longer a wall of bodies. Now find out what they are guarding.",
      items=[item("Grimtotem's Wardstone", "neck", 28, "A pebble of warded basalt. It hums when demons are close.",
                  {"intellect": 4, "stamina": 3})])
quest("groms_legion_brands", "Legion Brands", "splintertree_interrogator", "splintertree_post", 27, 30,
      "Felguard Legionnaires wear a fel-iron plate stamped with the Legion's mark. Vashj needs a handful to trace where the "
      "Legion's gold is coming from.",
      [fetch("legion_brand_plate", 5)],
      "Take them off the dead, not the living. The living will object.",
      "These are stamped in a Legion foundry I know. Someone is shipping weapons through Ashenvale, and I know who to ask.",
      items=[item("Interrogator's Brand-Plate Bracers", "wrist", 29, "Stamped by the Legion; reforged by a Horde smith.",
                  {"strength": 4, "stamina": 4}, armor_type="plate")])
quest("groms_satyr_warlord", "Warlord of the Ritual Hall", "splintertree_interrogator", "splintertree_post", 27, 28,
      "The Satyr Warlord rules the western hall of Grom's Rest. He is a detour, not a duty, but his head would send a message.",
      [boss("Satyr Warlord", GR)],
      "Skippable, I know. Do it anyway. A Warlord left alive is a Warlord that recruits.",
      "Good. That kind of loud ends in a very particular silence.",
      items=[item("Warlord's Trophy Axe", "main_hand", 28, "Notched, horned and smug.",
                  {"strength": 6, "stamina": 4}, rarity="rare", weapon_type="axe_1h")],
      mult=1.3, boss=True)
quest("groms_void_handmaiden", "The Void Handmaiden", "splintertree_war_mage", "splintertree_post", 28, 29,
      "In the eastern gathering of Grom's Rest, a Void Handmaiden binds satyrs to something that was not made to be bound.",
      [boss("Void Handmaiden", GR)],
      "Void magic is not like fel. Fel burns. Void forgets. Take someone who remembers you.",
      "I feel lighter. I think it is lighter. Thank you.",
      items=[item("Handmaiden's Forgotten Veil", "head", 29, "It fits like it has been waiting for you.",
                  {"intellect": 6, "spirit": 4}, rarity="rare", armor_type="cloth")],
      mult=1.3, boss=True)
quest("groms_doomguard", "The Doomguard's Approach", "splintertree_war_mage", "splintertree_post", 28, 29,
      "The only road to the throne runs north from the hub, and a Doomguard Sentinel stands in it. It has never once left its post.",
      [boss("Doomguard Sentinel", GR)],
      "It does not tire, it does not sleep, it does not move. You will have to persuade it. Forcefully.",
      "One down. Three rooms behind it, and the throne beyond. Press on.",
      items=[item("Sentinel's Ashen Greaves", "legs", 29, "Ash still falls from the seams.",
                  {"strength": 6, "stamina": 5}, rarity="rare", armor_type="plate")],
      mult=1.3, nxt="groms_corrupted_ancient", boss=True)
quest("groms_corrupted_ancient", "The Corrupted Grove", "splintertree_war_mage", "splintertree_post", 29, 30,
      "Deeper in, an ancient has been bent into a demon's horror. What was once a grove warden is now only a thing that rots.",
      [boss("Corrupted Ancient", GR)],
      "It was a protector once. Remember that when your hand slows. Then remember that it cannot be saved.",
      "I'll tell the druids it fell fighting. That is as close to the truth as they can bear.",
      items=[item("Ancient's Heartwood Charm", "trinket", 30, "A knot of wood that still, very slowly, wants to grow.",
                  {"intellect": 3, "spirit": 3, "stamina": 2}, rarity="rare")],
      mult=1.3, nxt="groms_felguard_overseer", boss=True)
quest("groms_felguard_overseer", "The Bone Hall Overseer", "splintertree_interrogator", "splintertree_post", 30, 31,
      "The Felguard Overseer holds the Bone Hall, last gate before the Inner Sanctum. If the Legion has a hand in Ashenvale, "
      "its fingerprints are on him.",
      [boss("Felguard Overseer", GR)],
      "Bring me his collar. It will tell us who he answered to.",
      "A Legion collar, as I thought. Now we know who has been sending the demons.",
      items=[item("Overseer's Chained Pauldrons", "shoulder", 31, "The chains clink when you do not move.",
                  {"strength": 6, "stamina": 6}, rarity="rare", armor_type="plate")],
      mult=1.35, nxt="groms_lord_nightmare", boss=True)
quest("groms_lord_nightmare", "Lord Nightmare", "splintertree_war_mage", "splintertree_post", 31, 32,
      "At the heart of Grom's Rest sits the eldritch horror that the demons have been feeding. Kill it, and the throne is empty.",
      [boss("Lord Nightmare", GR)],
      "I have no better advice than this: do not look at it directly. And do not die.",
      "...The silence is unbelievable. Rest, hero. You earned the quiet.",
      items=[item("Nightmare-Touched Signet", "ring", 32, "A band of black glass. It does not reflect, but it does watch.",
                  {"intellect": 5, "stamina": 5}, rarity="rare"),
             item("Sanctum Warden's Mantle", "shoulder", 32, "Cloth that fell from a ceiling that is no longer there.",
                  {"intellect": 6, "spirit": 5}, rarity="rare", armor_type="cloth")],
      mult=1.6, boss=True)


# ===================================================================== BLACKFATHOM DEEPS (West, 24-27, bosses 26)
BF = "blackfathom_deeps"
quest("bfd_garrison", "The Drowned Garrison", "zoram_sentinel", "zoram_strand", 24, 26,
      "Lookout Taelanor has watched the naga come and go from a flooded temple under the cliffs for weeks. It's a garrison, not a raid. "
      "She wants its warriors thinned before it empties onto the Strand.",
      [kill("Naga Warrior", 8, BF)],
      "I've counted them going in. I haven't counted them coming out. That's the part that frightens me. Go down in company and thin them.",
      "Eight. They'll replace them, but not tonight. I wrote the number down. I'm glad it isn't higher.",
      nxt="bfd_ghamoo_ra")
quest("bfd_ghamoo_ra", "The Shell of Ghamoo-ra", "zoram_sentinel", "zoram_strand", 25, 26,
      "A giant turtle the naga revere as a god guards the outer caverns. Taelanor wants the beast ended, and its shell broken, so the way inward is open.",
      [boss("Ghamoo-ra", BF)],
      "They worship it. I'd find that sweet if it weren't the size of a boat and hungry. Break it, and take the way.",
      "A god, they said. It died as easily as a turtle. I will remember that when I next hear the naga pray.",
      items=[item("Ghamoo-ra's Shell Plate", "chest", 26, "Thick as a doorframe, and a little too warm.",
                  {"stamina": 7, "strength": 5}, rarity="rare", armor_type="mail")],
      mult=1.3, nxt="bfd_lady_sarevess", boss=True)
quest("bfd_lady_sarevess", "Lady Sarevess", "zoram_sentinel", "zoram_strand", 25, 26,
      "Lady Sarevess commands the naga of the Deeps' upper halls. If she falls, her warriors will fight each other for her chair.",
      [boss("Lady Sarevess", BF)],
      "She will offer you terms. I wouldn't read them. Cut her down and spare me the sound of her voice in my dreams.",
      "Without her, the halls will fight over her chair for a month. That's a month the Strand sleeps. Thank you.",
      items=[item("Sarevess's Tidal Bracers", "wrist", 26, "Cool to the touch, and always a little wet.",
                  {"intellect": 5, "spirit": 4}, rarity="rare", armor_type="cloth")],
      mult=1.35, boss=True)
quest("bfd_gelihast", "The Murloc King", "zoram_boatwright", "zoram_strand", 25, 26,
      "Gelihast has gathered the Deeps' murlocs under one nasty banner. Illyen wants the net he wears as a crown, and wants the rest to scatter.",
      [boss("Gelihast", BF)],
      "He wears my boat's net as a crown. MY net. Bring it back. It's patched and stinks, and I want it.",
      "That's my knot! Look at that, he left it. The fool. Thank you. I'll sink another boat in his honour.",
      items=[item("Gelihast's Knotted Crown", "head", 26, "A net that remembers being a boat's.",
                  {"agility": 6, "stamina": 5}, rarity="rare", armor_type="leather")],
      mult=1.3, boss=True)
quest("bfd_hydra_fangs", "Hydra Fangs", "zoram_boatwright", "zoram_strand", 25, 27,
      "The murloc hydras of the Deeps shed fangs that hold an edge better than steel. Illyen wants six for her tool-rack.",
      [fetch("hydra_fang", 6)],
      "A hydra fang will cut a rope under tension and never go dull. Six of them and I'll have a tool rack to show off.",
      "Six. And not a chip. These are going straight in the rack. I'll sharpen nothing for a year.")
quest("bfd_tide_callers", "The Tide-Callers", "zoram_sentinel", "zoram_strand", 26, 27,
      "Two of the Deeps' deeper masters hold its inner temple: Lorgus Jett, who commands the tide, and Old Serra'kis, who commands what the tide has swallowed.",
      [boss("Lorgus Jett", BF), boss("Old Serra'kis", BF)],
      "Two of them, deeper in. You'll have to go through both. It's not a job for fewer than a full party, Lookout or not.",
      "Both. I felt the water settle. I'd have missed it if I'd been looking at the sea instead of at you.",
      items=[item("Serra'kis's Fangmantle", "shoulder", 27, "Teeth, sewn into silk. It doesn't rattle. It listens.",
                  {"agility": 7, "stamina": 5}, rarity="rare", armor_type="leather")],
      mult=1.4, nxt="bfd_kelris", boss=True)
quest("bfd_kelris", "The Twilight Lord", "zoram_sentinel", "zoram_strand", 26, 27,
      "Twilight Lord Kelris hides at the temple's heart, putting the Twilight's Hammer's work in the mouths of dying men. Taelanor wants him silent.",
      [boss("Twilight Lord Kelris", BF)],
      "He works in whispers. Do not listen. Cut him down.",
      "Silent. I'd forgotten silence could be so loud. One more below him, and it ends.",
      items=[item("Kelris's Whispering Robe", "chest", 27, "It hums a lullaby, wrong in every key.",
                  {"intellect": 8, "spirit": 5}, rarity="rare", armor_type="cloth")],
      mult=1.4, nxt="bfd_aku_mai", boss=True)
quest("bfd_aku_mai", "Aku'mai the Devourer", "zoram_sentinel", "zoram_strand", 27, 27,
      "At the bottom of Blackfathom sleeps Aku'mai, a thing the naga call the Devourer. If it wakes, the Strand will be the least of the world's worries.",
      [boss("Aku'mai", BF)],
      "It is the last thing in the Deeps. Kill it while it sleeps, or don't go at all. I'll be on the wall. I will be watching the water.",
      "Then it's over. I'll sleep tonight. You earned that, and the Strand's gratitude. Take the pearl, if it still glows.",
      items=[item("Aku'mai's Deepwater Pearl", "trinket", 27, "It still glows. It never stops. It reminds you of the dark.",
                  {"intellect": 5, "stamina": 5, "spirit": 3}, rarity="rare"),
             item("Devourer's Barbed Spear", "main_hand", 27, "Barbs that curve back on themselves, wanting to be somewhere deeper.",
                  {"agility": 8, "stamina": 5}, rarity="rare", weapon_type="polearm")],
      mult=1.7, boss=True)


def main():
    out = ROOT / "data/quests/ashenvale_dungeons.json"
    ids = [q["quest_id"] for q in QUESTS]
    assert len(ids) == len(set(ids)), "duplicate quest ids"
    nxt = {q.get("next_quest_id") for q in QUESTS} - {None}
    assert nxt <= set(ids), nxt - set(ids)
    out.write_text(json.dumps({"quests": QUESTS}, indent=2, ensure_ascii=False) + "\n")
    print(f"{len(QUESTS)} dungeon quests -> {out.name}")


if __name__ == "__main__":
    main()
