#!/usr/bin/env python3
"""Southern Barrens content pass (2026-10-21).  Idempotent.

  python3 tools/build_southern_barrens_content.py && python3 tools/generate_creatures.py

Map reference (260x240, see tools/handbuilt_southern_barrens.py)
  Camp Taurajo gate (130,2) | Bael'dun Keep ring (86,32), east gate (113,36) | Bael Modan quarry (34,64)
  Blackthorn Ridge (14-94, 84-130), Razormane camp (45,106) | The Rift canyon y~130 W-E, ramps (100,126) (176,144)
  Rift Waystation (139,118) north ramp | Razorfen Approach horseshoe (55,163), cave (55,175)
  Field of Giants (90-190, 150-222), tusk gate (124,168) | Raptor Grounds valley (196-248, 78-122)
  Hoodoo Spires NE (190-245, 44-75), hunter's blind (194,48) | Sinkhole Crater (222,212), stair (225,220)

LEVEL LADDER   open road / Rift 18-20 | Field of Giants 18-21 | Bael Modan 19-22 | Razorfen Approach 19-22
               Blackthorn 19-22 (Hagg 22, Brontus 24) | Raptor Grounds 20-23 | Hoodoo Spires 20-23
               Bael'dun Keep 21-24 (General Twinbraid 24) | Sinkhole Crater 21-24.  Named rares 20-24.
LOOT           ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    # --- the Rift
    "Rift Cliffhawk": C("beast_fast", 18, 20, "rift_cliffhawk"),
    "Gravel Skitterer": C("vermin_sneaky", 18, 21, "gravel_skitterer"),
    "Rift Sabertooth": C("beast_basic", 19, 21, "rift_sabertooth"),
    # --- Field of Giants
    "Giantbone Hyena": C("beast_basic", 18, 21, "giantbone_hyena"),
    "Bone-Dust Wraith": C("undead_basic", 19, 22, "bonedust_wraith"),
    # --- Razorfen approach / Blackthorn
    "Razorfen Bramble-Guard": C("humanoid_warrior", 20, 22, "razorfen_bramble_guard"),
    "Thornhide Boar": C("beast_basic", 19, 21, "thornhide_boar"),
    "Razormane Skinner": C("humanoid_rogue", 19, 22, "razormane_skinner"),
    "Blackthorn Boarhound": C("beast_fast", 19, 21, "blackthorn_boarhound"),
    # --- Bael Modan / Bael'dun Keep
    "Modan Overseer": C("humanoid_warrior", 20, 22, "modan_overseer"),
    "Dig-Site Golem": C("elemental_bruiser", 20, 22, "dig_site_golem"),
    "Bael'dun Rifleman": C("humanoid_ranged", 21, 23, "keep_rifleman"),
    "Bael'dun Sergeant": C("humanoid_warrior", 22, 24, "keep_sergeant"),
    "Keep Mastiff": C("beast_fast", 21, 23, "keep_mastiff"),
    # --- Raptor Grounds
    "Sunscale Stalker": C("beast_fast", 20, 23, "sunscale_stalker"),
    "Nest-Mother Raptor": C("beast_large", 21, 23, "nest_mother_raptor"),
    # --- Sinkhole Crater
    "Sinkhole Burrower": C("vermin_swarm", 21, 23, "sinkhole_burrower"),
    "Brood Tunnel-Guard": C("vermin_sneaky", 22, 24, "brood_tunnel_guard"),
    # --- Hoodoo Spires
    "Windspire Harpy": C("humanoid_ranged", 20, 22, "windspire_harpy"),
    "Spire Windcaller": C("humanoid_caster", 21, 23, "spire_windcaller"),
    "Hoodoo Dust Devil": C("elemental_caster", 20, 22, "hoodoo_dust_devil"),
    # --- named rares (roll at ~6% per encounter in their subzone)
    "Dustmaw the Rift-Lurker": C("beast_large", 20, 20, "dustmaw_rift_lurker", True, 1.7),
    "Thrumbone the Ancient": C("undead_basic", 21, 21, "thrumbone_ancient", True, 1.7),
    "Old Mother Longhorn": C("beast_large", 20, 20, "old_mother_longhorn", True, 1.7),
    "Bramblequeen Durga": C("humanoid_caster", 22, 22, "bramblequeen_durga", True, 1.6),
    "Skinwalker Garn": C("humanoid_rogue", 21, 21, "skinwalker_garn", True, 1.6),
    "Foreman Grubb Deepdelver": C("humanoid_warrior", 21, 21, "foreman_grubb", True, 1.7),
    "Sergeant Ironvein": C("humanoid_warrior", 23, 23, "sergeant_ironvein", True, 1.7),
    "Razorbeak the Nestbreaker": C("beast_fast", 23, 23, "razorbeak_nestbreaker", True, 1.6),
    "Vexa the Tunnel-Queen": C("vermin_sneaky", 24, 24, "vexa_tunnel_queen", True, 1.7),
    "Skyshriek Matron": C("humanoid_caster", 23, 23, "skyshriek_matron", True, 1.6),
}

FIXES = {
    # open road / Rift
    "Ancient Mottled Boar": {"level_range": [18, 20]},
    "Elder Bloodtalon Scythemaw": {"level_range": [18, 20]},
    # Field of Giants
    "Barrens Kodo": {"level_range": [18, 20]},
    "Aged Kodo": {"level_range": [19, 21]},
    "Savannah Patriarch": {"level_range": [20, 22]},
    # Raptor Grounds
    "Sunscale Lashtail": {"level_range": [20, 23]},
    # Razorfen approach
    "Bristleback Quilboar": {"level_range": [19, 22]},
    "Bristleback Water Seeker": {"level_range": [19, 22]},
    "Bristleback Shaman": {"level_range": [20, 22]},
    "Bristleback Thornweaver": {"level_range": [20, 22]},
    # Blackthorn
    "Razormane Stalker": {"level_range": [19, 22]},
    "Razormane Seer": {"level_range": [20, 22]},
    "Hagg Taurenbane": {"level_range": [22, 22], "boss_multiplier": 2.5},
    "Brontus": {"level_range": [24, 24], "boss_multiplier": 2.5},
    # dwarves: the old data used a dead "kit" key, so they fought with no abilities at all
    "Dwarf Miner": {"level_range": [19, 22], "ability_kit": "dwarf_miner"},
    "Dwarf Engineer": {"level_range": [20, 23], "ability_kit": "dwarf_engineer"},
    "Dwarf Explosives Expert": {"level_range": [21, 24], "ability_kit": "dwarf_explosives"},
    "General Twinbraid": {"level_range": [24, 24], "boss_multiplier": 2.6, "ability_kit": "general_twinbraid"},
}
DROP_KEYS = ("kit",)     # stale key removed from the dwarf creatures

OPEN_ZONE = {"name": "The Southern Plains", "creatures": {
    "Ancient Mottled Boar": 3, "Elder Bloodtalon Scythemaw": 2, "Rift Cliffhawk": 1, "Giantbone Hyena": 1}}


def tbl(display, **c):
    return {"name": display, "creatures": c}


SUBZONES = {
    "The Rift": tbl("The Rift", **{
        "Rift Cliffhawk": 3, "Gravel Skitterer": 3, "Rift Sabertooth": 2, "Dustmaw the Rift-Lurker": 0}),
    "Field of Giants": tbl("Field of Giants", **{
        "Barrens Kodo": 2, "Aged Kodo": 1, "Giantbone Hyena": 3, "Bone-Dust Wraith": 3, "Savannah Patriarch": 1,
        "Thrumbone the Ancient": 0, "Old Mother Longhorn": 0}),
    "Razorfen Approach": tbl("Razorfen Approach", **{
        "Bristleback Quilboar": 3, "Bristleback Water Seeker": 1, "Bristleback Shaman": 2,
        "Bristleback Thornweaver": 2, "Razorfen Bramble-Guard": 2, "Thornhide Boar": 2, "Bramblequeen Durga": 0}),
    "Bael Modan": tbl("Bael Modan", **{
        "Dwarf Miner": 5, "Dwarf Engineer": 3, "Dwarf Explosives Expert": 2, "Modan Overseer": 2,
        "Dig-Site Golem": 3, "Foreman Grubb Deepdelver": 0}),
    "Bael'dun Keep": tbl("Bael'dun Keep", **{
        "Dwarf Miner": 2, "Dwarf Engineer": 2, "Dwarf Explosives Expert": 3, "Bael'dun Rifleman": 4,
        "Bael'dun Sergeant": 2, "Keep Mastiff": 3, "Sergeant Ironvein": 0, "General Twinbraid": 0}),
    "Blackthorn Ridge": tbl("Blackthorn Ridge", **{
        "Razormane Stalker": 4, "Razormane Seer": 2, "Razormane Skinner": 3, "Blackthorn Boarhound": 3,
        "Skinwalker Garn": 0, "Hagg Taurenbane": 0, "Brontus": 0}),
    "Raptor Grounds": tbl("Raptor Grounds", **{
        "Sunscale Lashtail": 4, "Sunscale Stalker": 4, "Nest-Mother Raptor": 2, "Razorbeak the Nestbreaker": 0}),
    "Hoodoo Spires": tbl("Hoodoo Spires", **{
        "Windspire Harpy": 4, "Spire Windcaller": 2, "Hoodoo Dust Devil": 3, "Skyshriek Matron": 0}),
    "Sinkhole Crater": tbl("Sinkhole Crater", **{
        "Sinkhole Burrower": 4, "Brood Tunnel-Guard": 3, "Vexa the Tunnel-Queen": 0}),
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Gravel Skitterer": [qd("rift_geode", "Glittering Rift Geode",
                            "A fist-sized geode that was cracked open by something with a very tidy mind. Inside, the crystals hum.", 0.5)],
    "Bone-Dust Wraith": [qd("giant_knucklebone", "Giant's Knucklebone",
                            "A knuckle the size of your head, still faintly warm in the sun. Whatever it was attached to was not impressed by you.", 0.5)],
    "Bael'dun Sergeant": [qd("keep_dispatch", "Bael'dun Dispatch",
                             "A folded, wax-sealed order in tidy dwarven runes. The wax is red. So, increasingly, is the paper.", 0.5)],
    "Dwarf Explosives Expert": [qd("powder_charge", "Dwarven Powder Charge",
                                   "Brass-bound and stamped with a label that says CAREFUL in four languages. The fifth label has been scratched out.", 0.5)],
    "Dig-Site Golem": [qd("golem_core_shard", "Golem Core Shard",
                          "A chip of enchanted stone that remembers being told what to do, and is still waiting for the next order.", 0.5)],
    "Modan Overseer": [qd("dig_ledger_page", "Torn Dig-Ledger Page",
                          "A page of numbers: ore in, ore out, workers lost. The last column has been written in a much firmer hand.", 0.5)],
    "Razormane Skinner": [qd("skinner_trophy_cord", "Skinner's Trophy Cord",
                             "A braided cord hung with ears, claws and one small bell. The bell is not a trophy. The bell is a warning.", 0.5)],
    "Spire Windcaller": [qd("spire_wind_crystal", "Windspire Crystal",
                            "A shard of glassy sandstone that sings when held up to the wind. It does not stop when you put it down.", 0.5)],
    "Brood Tunnel-Guard": [qd("tunnel_guard_chitin", "Tunnel-Guard Chitin Plate",
                              "A curved plate of chitin, hard as iron and about as friendly. It rings when you tap it. Something below answers.", 0.5)],
}


def pools():
    P = {}
    # ---------------- bosses ----------------------------------------------------------------------------------
    P["General Twinbraid"] = [      # L24 -> 27  dwarf general: hammer / plate chest / shield / belt
        make("Twinbraid's Stormhammer", "main_hand", "of the Champion", 27,
             "A hammer built to be thrown and caught. The dwarf who built it did not account for a general's temper.",
             weapon_type="mace_2h"),
        make("General's Braided-Beard Cuirass", "chest", "of the Bastion", 27,
             "Plate in the old Bael'dun style, with a braided beard-pattern in the rivets. It smells of oil and fury.",
             armor_type="plate"),
        make("Bulwark of Bael'dun", "off_hand", "of Blocking", 27,
             "A tower shield with the keep's sigil beaten flat by many years of the wrong kind of visitor.",
             weapon_type="shield"),
        make("Quartermaster's Iron Girdle", "waist", "of the Bear", 27,
             "A heavy belt hung with brass keys. None of them open anything in the Barrens.", armor_type="plate")]
    P["Hagg Taurenbane"] = [        # L22 -> 25  quilboar slayer: axe / leather chest / mail gloves / ring
        make("Hagg's Taurenbane Hatchet", "main_hand", "of the Assassin", 25,
             "A short axe with notches filed in the haft. Hagg stopped counting at forty.", weapon_type="axe_1h"),
        make("Trophy-Hunter's Hide Vest", "chest", "of the Hunt", 25,
             "Hung with horn-tips and braided hair. The horn-tips are sorted by size. The hair is not.",
             armor_type="leather"),
        make("Gauntlets of the Ridge-Stalker", "hands", "of the Tiger", 25,
             "Thorn-wood knuckle plates over mail. Punching with them is not strictly advisable.",
             armor_type="mail"),
        make("Taurenbane's Bone Signet", "ring", "of the Bandit", 25,
             "A ring cut from a bull-horn tip. It's warm. It is not meant to be.")]
    P["Brontus"] = [                # L24 -> 27  giant bull-kodo: 2H / plate legs / tank neck / belt
        make("Brontus's Horn-Hewn Greatclub", "main_hand", "of the Gladiator", 27,
             "Cut from a single giant horn. Heavy enough to flatten a quilboar and everything behind him.",
             weapon_type="mace_2h"),
        make("Earthshaker Greaves", "legs", "of the Juggernaut", 27,
             "Plate over kodo-hide. Every step feels like you're about to stampede.", armor_type="plate"),
        make("Pendant of the Thunderhoof", "neck", "of the Ironfur", 27,
             "A bull's horn-tip set in iron. It rings, very softly, whenever the ground does."),
        make("Stampede-Hide Girdle", "waist", "of the Bear", 27,
             "Pale kodo-hide, tanned until it creaks like a drum. Hits to the ribs sound like thunder.",
             armor_type="plate")]
    # ---------------- named rares ----------------------------------------------------------------------------------
    P["Dustmaw the Rift-Lurker"] = [   # L20 -> 23  rift predator: dagger / leather boots / agi ring
        make("Dustmaw's Canyon-Fang", "main_hand", "of the Assassin", 23,
             "A tooth the length of a dagger, still gritty with canyon dust.", weapon_type="dagger"),
        make("Rift-Runner's Boots", "feet", "of the Monkey", 23,
             "Soft hide, ribbed soles. Climbing a wall in these feels like cheating, because it is.",
             armor_type="leather"),
        make("Gravel-Ground Signet", "ring", "of the Falcon", 23,
             "A band of rock-crystal. It rattles faintly when something's about to fall.")]
    P["Thrumbone the Ancient"] = [      # L21 -> 24  giant echo: 2H staff / cloth robe / healer neck
        make("Thrumbone's Marrow Staff", "main_hand", "of the Prophet", 24,
             "A giant's thigh-bone, hollow and very old. Wind whistles through it in a language nobody speaks.",
             weapon_type="staff"),
        make("Robes of the Rattling Dirge", "chest", "of the Necromancer", 24,
             "Cloth stitched with knucklebones. They click in time with your heartbeat. Mostly.",
             armor_type="cloth"),
        make("Giantbone Charm of Mending", "neck", "of the Physician", 24,
             "A tiny carved finger-bone on a cord. Wearing it, wounds seem to take less offence.")]
    P["Old Mother Longhorn"] = [        # L20 -> 23  kodo matriarch: plate shoulders / 1H mace / tank ring
        make("Matriarch's Horn-Plate Pauldrons", "shoulder", "of the Defender", 23,
             "Layered kodo horn over iron. They do the same job she did: stand in front of the herd.",
             armor_type="plate"),
        make("Herd-Mother's Gavel", "main_hand", "of the Soldier", 23,
             "A short-handled mace carved from a horn-tip. It rings like a gong.", weapon_type="mace_1h"),
        make("Band of the Last Calf", "ring", "of the Bear", 23,
             "A ring of small, old horn. Don't ask what it's from.")]
    P["Bramblequeen Durga"] = [         # L22 -> 25  quilboar druid-queen: staff / cloth hood / mail wrist
        make("Durga's Briar-Crowned Staff", "main_hand", "of Nature's Wrath", 25,
             "A staff grown, not carved. It keeps growing, if you don't mind the thorns.", weapon_type="staff"),
        make("Hood of the Bramble Court", "head", "of the Invoker", 25,
             "A cowl woven from thorn-vine. It gives you a headache and good ideas, in that order.",
             armor_type="cloth"),
        make("Briar-Binder's Bracers", "wrist", "of the Wolf", 25,
             "Mail over bramble-cord. The thorns point inward, so it hurts to take them off.",
             armor_type="mail")]
    P["Skinwalker Garn"] = [            # L21 -> 24  razormane skinner chief: dagger / leather legs / agi neck
        make("Garn's Flaying Knife", "main_hand", "of the Bandit", 24,
             "The blade is shaped like a leaf. The handle is wrapped in a stranger's hair.", weapon_type="dagger"),
        make("Skin-Stitched Leggings", "legs", "of the Hunt", 24,
             "Stitched from several different animals. One of them used to be a person. Probably.",
             armor_type="leather"),
        make("Charm of Many Hides", "neck", "of the Monkey", 24,
             "A pouch of small animal teeth. It rattles when you're about to be noticed.")]
    P["Foreman Grubb Deepdelver"] = [   # L21 -> 24  dwarven foreman: pick / plate helm / mail belt
        make("Grubb's Deepdelver Pickaxe", "main_hand", "of the Champion", 24,
             "A heavy iron pickaxe, balanced for one-handed swings and two-handed regrets.",
             weapon_type="axe_1h"),
        make("Foreman's Hard-Hat Helm", "head", "of the Bulwark", 24,
             "An iron cap with a lantern bracket. The bracket's been dented by every ceiling in the quarry.",
             armor_type="plate"),
        make("Quota-Keeper's Utility Belt", "waist", "of the Falcon", 24,
             "Loops for every tool, and a pocket for the paperwork nobody wanted to read.",
             armor_type="mail")]
    P["Sergeant Ironvein"] = [          # L23 -> 26  keep sergeant: shield / plate boots / tank ring
        make("Ironvein's Rampart", "off_hand", "of the Defender", 26,
             "A kite shield in dwarven steel. The dent at the top is where a general threw something.",
             weapon_type="shield"),
        make("Keep-Marcher's Sabatons", "feet", "of the Bastion", 26,
             "Steel boots with studs. They announce you from three rooms away.", armor_type="plate"),
        make("Signet of the Iron Vein", "ring", "of the Bear", 26,
             "A band of dark ore with a bright vein through it, like a scar.")]
    P["Razorbeak the Nestbreaker"] = [  # L23 -> 26  raptor alpha: bow / leather chest / agi cloak
        make("Razorbeak's Raptorbone Bow", "ranged", "of the Marksman", 26,
             "Strung with raptor sinew. It twangs like something remembering how to hunt.", weapon_type="bow"),
        make("Nestbreaker's Scale Jerkin", "chest", "of the Tiger", 26,
             "Overlapping raptor scales over soft hide. It sheds sand, and rumours.", armor_type="leather"),
        make("Cloak of the Stolen Egg", "back", "of the Eagle", 26,
             "Feathered and speckled. Smells distinctly like omelette.", armor_type="cloth")]
    P["Vexa the Tunnel-Queen"] = [      # L24 -> 27  silithid queen: caster mace / mail hood / healer ring
        make("Vexa's Brood-Scepter", "main_hand", "of the Spell Breaker", 27,
             "A scepter of fused chitin with a soft, pulsing grub-sac at the tip. Do not squeeze it. It knows.",
             weapon_type="mace_1h"),
        make("Tunnel-Queen's Chitin Cowl", "head", "of the Beast", 27,
             "Plates of hard shell, sewn with sinew. The cavities hold amber. The amber holds something.",
             armor_type="mail"),
        make("Hive-Amber Band", "ring", "of the Restorer", 27,
             "A hard bead of resin, warm to the touch. Something small inside kicks, once, whenever you heal.")]
    P["Skyshriek Matron"] = [           # L23 -> 26  harpy matron: wand / cloth shoulders / caster ring
        make("Skyshriek's Storm-Feather Wand", "ranged", "of Nature's Wrath", 26,
             "A wand with a harpy feather at the tip. The feather crackles when it's thinking.", weapon_type="wand"),
        make("Matron's Feathered Mantle", "shoulder", "of the Sorcerer", 26,
             "Feather-light, thunder-bright. It makes your hair do things.", armor_type="cloth"),
        make("Windspire Matron's Ring", "ring", "of the Archmage", 26,
             "A ring of wind-polished sandstone. The wind only blows from one direction here: toward you.")]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    data = json.loads(cp.read_text())
    cr = data["creatures"]
    cr.update(NEW_CREATURES)
    for n, patch in FIXES.items():
        cr[n].update(patch)
        for k in DROP_KEYS:
            cr[n].pop(k, None)
    cp.write_text(json.dumps(data, indent=2) + "\n")

    ep = ROOT / "data/creatures/encounters.json"
    data = json.loads(ep.read_text())
    z = data["zones"]["Southern Barrens"]
    z["open_zone"] = OPEN_ZONE
    z["subzones"] = SUBZONES
    ep.write_text(json.dumps(data, indent=2) + "\n")

    qp = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(qp.read_text())
    D = data["drops"]
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    out = {"_notes": "Southern Barrens boss + named-rare loot (2026-10-21). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/southern_barrens_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, tables {len(SUBZONES)} subzones, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
