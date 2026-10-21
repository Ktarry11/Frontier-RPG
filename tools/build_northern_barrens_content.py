#!/usr/bin/env python3
"""Northern Barrens content pass (2026-10-21).  Idempotent.

  PYTHONPATH=. python3 tools/build_northern_barrens_content.py && PYTHONPATH=. python3 tools/generate_creatures.py

What was broken: seven creatures pointed at kits that did not exist or used the dead `"kit"` key (Slug, Bog Creature, Road
Bandit, Southsea Brigand/Cannoneer, all three Witchwing harpies, Serena Bloodfeather, Harpy Matriarch, Captain Saltspray), the
Mor'shan Rampart (a HORDE wall) rolled hostile Horde sentries, Dry Hills mixed L14 plainstriders with L20 harpies, no NB
creature had a level ladder, and no NB boss/rare had loot.

MAP (280x260, tools/handbuilt_northern_barrens.py)
  Gold Road N-S spine: south gate (150,256) -> Mor'shan Rampart gate (150,4)   Base Camp (145,65)   Slug Fens W, Serena's cave (60,150)
  Dry Hills NW | Harpy Roost NE crags | Sludge Fen oil basin (228,64), Boulder Lode adit (255,45) | Stagnant Oasis (200,175)
  Far Watch Post headland (258,130) | Merchant Coast bay SE

LEVEL LADDER (south -> north; Kyle's confirmed cave rows: Boulder Lode 13-17 / Foreman Grills 17, Serena's Hollow 14-20 / Matriarch 20)
  Merchant Coast 13-17 | Gold Road 14-18 | Far Watch 15-17 | Slug Fens 15-18 | Base Camp 15-18 | Harpy Roost 16-19
  Mor'shan Rampart 17-20 | Sludge Fen 17-20 | Stagnant Oasis 17-20 | Dry Hills 19-22.  Named rares 16-20.
LOOT   ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    # --- Slug Fens
    "Mire Leech": C("vermin_swarm", 15, 17, "mire_leech"),
    "Peat Shambler": C("elemental_bruiser", 16, 18, "peat_shambler"),
    "Fenwater Crocolisk": C("beast_large", 16, 18, "fenwater_crocolisk"),
    # --- Harpy Roost / Serena's Hollow
    "Roost Bonepicker": C("beast_fast", 16, 18, "roost_bonepicker"),
    "Harpy Sky-Sentry": C("humanoid_warrior", 17, 19, "harpy_sky_sentry"),
    # --- Mor'shan Rampart (night-elf pickets)
    "Sentinel Picket": C("humanoid_warrior", 17, 19, "sentinel_picket"),
    "Sentinel Archer": C("humanoid_ranged", 17, 20, "sentinel_archer"),
    "Sentinel Moonspeaker": C("humanoid_caster", 18, 20, "sentinel_moonspeaker"),
    # --- Base Camp / Far Watch
    "Kolkar Scoutrider": C("humanoid_ranged", 15, 17, "kolkar_scoutrider"),
    "Kolkar Warbrand": C("humanoid_warrior", 16, 18, "kolkar_warbrand"),
    # --- Sludge Fen
    "Venture Co. Oil Driller": C("humanoid_warrior", 17, 19, "oil_driller"),
    "Pumpjack Guard": C("humanoid_ranged", 18, 20, "pumpjack_guard"),
    "Sludge Elemental": C("elemental_bruiser", 18, 20, "sludge_elemental"),
    # --- Stagnant Oasis
    "Kolkar Dervish": C("humanoid_warrior", 17, 19, "kolkar_dervish"),
    "Kolkar Stormcaller": C("humanoid_caster", 18, 20, "kolkar_stormcaller"),
    "Dervish Hound": C("beast_fast", 17, 19, "dervish_hound"),
    # --- Merchant Coast
    "Tide-Wrecker Crab": C("aquatic_basic", 13, 15, "tidewrecker_crab"),
    # --- Dry Hills
    "Hillcrest Stalker": C("beast_basic", 19, 21, "hillcrest_stalker"),
    "Stonepeck Vulture": C("beast_fast", 19, 21, "stonepeck_vulture"),
    # --- Boulder Lode Mine
    "Mine Hound": C("beast_fast", 13, 15, "mine_hound"),
    "Ore Sprite": C("elemental_caster", 14, 16, "ore_sprite"),
    # --- named rares (roll ~6% per encounter in their subzone; cave rares are pinned)
    "Old Mire-Maw": C("beast_large", 17, 17, "old_mire_maw", True, 1.4),
    "Skyfang the Plunderer": C("beast_fast", 18, 18, "skyfang_plunderer", True, 1.8),
    "Warden Ilthae": C("humanoid_warrior", 20, 20, "warden_ilthae", True, 1.8),
    "Scout-Captain Vrek": C("humanoid_ranged", 17, 17, "scoutcaptain_vrek", True, 1.7),
    "Kragg the Wall-Breaker": C("humanoid_warrior", 17, 17, "kragg_wallbreaker", True, 1.8),
    "Prospector Delvik": C("humanoid_ranged", 16, 16, "prospector_delvik", True, 1.7),
    "Windcaller Skreeva": C("humanoid_caster", 18, 18, "windcaller_skreeva", True, 1.7),
}
# pre-existing creatures: repaired kits, exact ladder levels, boss HP
FIXES = {
    "Plainstrider": {"level_range": [14, 17]},
    "Zhevra Runner": {"level_range": [14, 17]},
    "Harpy": {"level_range": [15, 18]},
    "Harpy Windcaller": {"level_range": [16, 19]},
    "Slug": {"level_range": [15, 17], "ability_kit": "slug"},
    "Bog Creature": {"level_range": [15, 18], "ability_kit": "bog_creature"},
    "Road Bandit": {"level_range": [14, 16]},
    "Kolkar Raider": {"level_range": [15, 17]},
    "Southsea Brigand": {"level_range": [13, 16], "ability_kit": "southsea_brigand"},
    "Southsea Cannoneer": {"level_range": [14, 17], "ability_kit": "southsea_cannoneer"},
    "Witchwing Harpy": {"level_range": [19, 21], "ability_kit": "witchwing_harpy"},
    "Witchwing Windcaller": {"level_range": [20, 22], "ability_kit": "witchwing_windcaller"},
    "Witchwing Slayer": {"level_range": [19, 21], "ability_kit": "witchwing_slayer"},
    "Venture Co. Miner": {"level_range": [13, 16]},
    "Venture Co. Tinkerer": {"level_range": [14, 17]},
    "Venture Co. Overseer": {"level_range": [15, 17]},
    "Foreman Grills": {"level_range": [17, 17], "boss_multiplier": 2.3},
    "Supervisor Lugwizzle": {"level_range": [18, 18], "boss_multiplier": 1.6},
    "Engineer Whirleygig": {"level_range": [19, 19], "boss_multiplier": 1.7},
    "Verog the Dervish": {"level_range": [19, 19], "boss_multiplier": 1.7},
    "Captain Saltspray": {"level_range": [17, 17], "ability_kit": "captain_saltspray", "boss_multiplier": 1.6},
    "Serena Bloodfeather": {"level_range": [20, 20], "ability_kit": "serena_bloodfeather", "boss_multiplier": 2.0},
    "Harpy Matriarch": {"level_range": [20, 20], "ability_kit": "harpy_matriarch", "boss_multiplier": 3.3},
}
DROP_KEYS = ("kit",)          # the dead key: replaced by ability_kit


def tbl(display, **c):
    return {"name": display, "creatures": c}


OPEN_ZONE = {"name": "The Northern Plains", "creatures": {
    "Plainstrider": 4, "Zhevra Runner": 3, "Harpy": 2, "Harpy Windcaller": 1}}

SUBZONES = {
    "Gold Road": tbl("Gold Road", **{
        "Road Bandit": 4, "Bandit Cutthroat": 2, "Bandit Outrider": 2, "Zhevra Runner": 2, "Plainstrider": 2}),
    "Slug Fens": tbl("Slug Fens", **{
        "Slug": 3, "Bog Creature": 3, "Mire Leech": 3, "Peat Shambler": 2, "Fenwater Crocolisk": 2, "Old Mire-Maw": 0}),
    "Harpy Roost": tbl("Harpy Roost", **{
        "Harpy": 4, "Harpy Windcaller": 2, "Roost Bonepicker": 3, "Harpy Sky-Sentry": 2, "Skyfang the Plunderer": 0}),
    "Mor'shan Rampart": tbl("Mor'shan Rampart", **{
        "Sentinel Picket": 3, "Sentinel Archer": 3, "Sentinel Moonspeaker": 2, "Harpy": 1, "Warden Ilthae": 0}),
    "Mor'shan Base Camp": tbl("Mor'shan Base Camp", **{
        "Kolkar Raider": 3, "Kolkar Scoutrider": 3, "Kolkar Warbrand": 2, "Kolkar Drudge": 1, "Scout-Captain Vrek": 0}),
    "Sludge Fen": tbl("Sludge Fen", **{
        "Venture Co. Oil Driller": 3, "Pumpjack Guard": 3, "Sludge Elemental": 3,
        "Supervisor Lugwizzle": 0, "Engineer Whirleygig": 0}),
    "Stagnant Oasis": tbl("Stagnant Oasis", **{
        "Kolkar Dervish": 3, "Kolkar Stormcaller": 2, "Dervish Hound": 3, "Verog the Dervish": 0}),
    "Far Watch Post": tbl("Far Watch Post", **{
        "Kolkar Raider": 4, "Kolkar Scoutrider": 2, "Kolkar Drudge": 2, "Kragg the Wall-Breaker": 0}),
    "Merchant Coast": tbl("Merchant Coast", **{
        "Southsea Brigand": 4, "Southsea Cannoneer": 3, "Pool Murloc": 2, "Tide-Wrecker Crab": 3, "Captain Saltspray": 0}),
    "Dry Hills": tbl("Dry Hills", **{
        "Witchwing Harpy": 4, "Witchwing Windcaller": 2, "Witchwing Slayer": 3, "Hillcrest Stalker": 3,
        "Stonepeck Vulture": 2, "Serena Bloodfeather": 0}),
}
CAVES = {
    # bosses/rares ride in the same table at weight 0 (engine convention; placed only by zone.boss_positions pins)
    "Boulder Lode Mine": {"name": "Boulder Lode Mine", "creatures": {
        "Venture Co. Miner": 3, "Venture Co. Tinkerer": 2, "Venture Co. Overseer": 2, "Cavern Rock Elemental": 2,
        "Mine Hound": 3, "Ore Sprite": 2, "Foreman Grills": 0, "Prospector Delvik": 0}},
    "Serena's Hollow": {"name": "Serena's Hollow", "creatures": {
        "Harpy": 4, "Harpy Windcaller": 2, "Roost Bonepicker": 3, "Harpy Sky-Sentry": 2,
        "Harpy Matriarch": 0, "Windcaller Skreeva": 0}},
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Slug": [qd("slug_venom_gland", "Slug Venom Gland",
                "A wet, mustard-coloured gland. It is warmer than it has any right to be, and it twitches.", 0.5)],
    "Peat Shambler": [qd("peat_heart", "Peat Heart",
                         "A fist of dense black peat that holds its shape like muscle. It is faintly, unnervingly pulsing.", 0.45)],
    "Sentinel Picket": [qd("sentinel_signal_horn", "Sentinel Signal Horn",
                           "A curved silver horn, still warm from a night-elf mouth. One long call and the pickets know where the Horde is.", 0.45)],
    "Kolkar Raider": [qd("kolkar_warpennant", "Kolkar War-Pennant",
                         "A strip of dyed hide on a bone pole. Every pennant is a boast, and each of these is a boast that did not pan out.", 0.4)],
    "Pumpjack Guard": [qd("oil_pressure_gauge", "Pumpjack Pressure Gauge",
                          "A brass gauge, needle pinned at the red. The Venture Co. does not stamp its name on these. It stamps a price.", 0.5)],
    "Sludge Elemental": [qd("crude_sludge_sample", "Crude Sludge Sample",
                            "A stoppered flask of the sludge that is not strictly oil, anymore, and not strictly dead.", 0.5)],
    "Kolkar Dervish": [qd("dervish_curved_blade", "Dervish Curved Blade",
                          "A short, hooked blade, hot to the touch. Dervishes spin until they glow. The blades take longer to cool.", 0.5)],
    "Road Bandit": [qd("highwayman_ledger", "Highwayman's Ledger",
                       "A greasy tally of caravans, with prices, in a very neat hand. The neatness is the disturbing part.", 0.45)],
    "Southsea Brigand": [qd("salvaged_cargo_crate", "Salvaged Cargo Crate",
                            "A small crate with a Ratchet customs stamp half burned out. It rattles. It might be rum.", 0.45)],
    "Witchwing Windcaller": [qd("witchwing_hex_totem", "Witchwing Hex-Totem",
                                "Feathers, knucklebone and a thread of human hair. It hums in a key that makes your fillings ache.", 0.5)],
    "Cavern Rock Elemental": [qd("vein_core_sample", "Vein Core Sample",
                                 "A palm-sized core of crystal-veined rock, still ringing from the drill that did not finish it.", 0.5)],
    "Ore Sprite": [qd("ore_sprite_shard", "Ore Sprite Shard",
                      "A shard of living crystal that hums quietly and goes cold when you look at it for too long.", 0.5)],
    "Roost Bonepicker": [qd("harpy_roost_down", "Roost Down",
                            "A handful of grey-brown down. Harpies line their nests with it, and the nests are not clean.", 0.5)],
}


def pools():
    P = {}
    # ---------------- cave bosses -------------------------------------------------------------------------------
    P["Foreman Grills"] = [      # L17 -> 20: 1H mace / plate helm / leather chest / neck
        make("Foreman's Rivet-Hammer", "main_hand", "of the Champion", 20,
             "A wrench-mallet with a head shaped like a rivet. It sorts problems into 'struck' and 'not yet struck'.",
             weapon_type="mace_1h"),
        make("Venture Co. Hardhat", "head", "of the Defender", 20,
             "A dented iron hat with the company logo scraped half off. It has, evidently, been dropped on a lot of heads.",
             armor_type="plate"),
        make("Blast-Proof Foreman's Apron", "chest", "of the Bear", 20,
             "Heavy leather, singed to a shade of brown that no one ordered. Smells of pitch and grudges.",
             armor_type="leather"),
        make("Tinkered Pressure-Gauge Pendant", "neck", "of the Seer", 20,
             "A watch-sized gauge on a chain. The needle points to wherever someone is about to be hit.")]
    P["Harpy Matriarch"] = [     # L20 -> 23: nature staff / cloth robe / fist weapon / mail boots
        make("Matriarch's Pinion Staff", "main_hand", "of Nature's Wrath", 23,
             "A staff hung with grey flight feathers. In a wind it chimes, one note over and over.", weapon_type="staff"),
        make("Roost-Mother's Plumage Robe", "chest", "of the Restorer", 23,
             "A robe of layered feathers. Warm, and impossible to stop preening.", armor_type="cloth"),
        make("Skyreach Talons", "main_hand", "of the Falcon", 23,
             "A pair of curved harpy claws on a bone grip. They want to be thrown, and they're never quite sorry.",
             weapon_type="fist_weapon"),
        make("Cliff-Walker's Talonguards", "feet", "of the Beast", 23,
             "Mail boots with a talon on each toe. You feel steadier in a gale, and a little predatory.",
             armor_type="mail")]
    # ---------------- named rares -------------------------------------------------------------------------------
    P["Serena Bloodfeather"] = [  # L20 -> 23
        make("Bloodfeather's Hunting Bow", "ranged", "of the Marksman", 23,
             "A recurve bow lashed with red-tipped feathers. It sings softly just before the string slips.", weapon_type="bow"),
        make("Witchwing Hunter's Spaulders", "shoulder", "of the Hunt", 23,
             "Leather pauldrons fringed with grey-and-crimson feathers. They flutter, with intent.", armor_type="leather"),
        make("Serena's Blood-Tipped Signet", "ring", "of the Eagle", 23,
             "A ring of red-dyed bone. Wear it, and the sky seems closer, and slightly more hostile.")]
    P["Supervisor Lugwizzle"] = [  # L18 -> 21
        make("Lugwizzle's Spill-Proof Buckler", "off_hand", "of Blocking", 21,
             "A round shield with a drip-tray on the rim. It was supposed to catch oil. It catches other things.",
             weapon_type="shield"),
        make("Control-Room Toolbelt", "waist", "of the Bear", 21,
             "A heavy belt hung with wrenches. Every one of them has a slightly different opinion about who was in charge.",
             armor_type="plate"),
        make("Signet of Quarterly Targets", "ring", "of the Squire", 21,
             "A brass ring stamped 'APPROVED'. It never says by whom.")]
    P["Engineer Whirleygig"] = [   # L19 -> 22
        make("Whirleygig's Sheep-Launcher", "ranged", "of the Marksman", 22,
             "A rifle-sized launcher with a small wool-covered hopper. Do not ask what is in the hopper.", weapon_type="gun"),
        make("Gadgeteer's Goggles", "head", "of the Seer", 22,
             "Brass goggles with seven lenses, all slightly different shades of wrong. You see farther. You see worse.",
             armor_type="leather"),
        make("Tinker's Spark-Stitched Gloves", "hands", "of the Sorcerer", 22,
             "Cloth gloves with copper thread in the fingertips. They tingle during a thunderstorm.", armor_type="cloth")]
    P["Verog the Dervish"] = [     # L19 -> 22
        make("Verog's Whirling Scimitar", "main_hand", "of the Duelist", 22,
             "A curved blade, balanced for a spin. Verog's grip left a groove in the handle the size of a thumb.",
             weapon_type="sword_1h"),
        make("Dervish-Stalker's Leggings", "legs", "of the Wolf", 22,
             "Dust-colored leather leggings that cut the wind. You'll find sand in them for weeks.", armor_type="leather"),
        make("Stagnant Oasis Talisman", "neck", "of the Whale", 22,
             "A charm of tarnished brass on a leather thong. It smells strongly of a pond that has seen things.")]
    P["Captain Saltspray"] = [     # L17 -> 20
        make("Saltspray's Boarding Cutlass", "main_hand", "of the Bandit", 20,
             "A cutlass with a barnacle-crusted guard. The point has seen more ropes than ribs, which is unusual for a pirate.",
             weapon_type="sword_1h"),
        make("Captain's Salt-Stained Tricorn", "head", "of the Monkey", 20,
             "A tricorn bent into a permanent defiant tilt. It's never dry, and it's never apologized.",
             armor_type="leather"),
        make("Southsea Doubloon Ring", "ring", "of the Falcon", 20,
             "A heavy gold ring stamped with a skull that is just slightly too happy.")]
    P["Old Mire-Maw"] = [          # L17 -> 20
        make("Mire-Maw's Hide Cloak", "back", "of the Whale", 20,
             "A cloak cut from the mud-brown hide of something that really, really liked its mud.", armor_type="cloth"),
        make("Snapper-Tooth Dagger", "main_hand", "of the Tiger", 20,
             "A tooth the length of your hand, notched for the grip. It still smells slightly of fen.",
             weapon_type="dagger"),
        make("Boglord's Band", "ring", "of the Bear", 20,
             "A ring of pressed peat and old bone. It keeps its shape through the wettest week.")]
    P["Skyfang the Plunderer"] = [  # L18 -> 21
        make("Skyfang's Pinion Wand", "ranged", "of Nature's Wrath", 21,
             "A wand tipped with a single dark primary feather. Static pops off it when anyone lies nearby.", weapon_type="wand"),
        make("Plunderer's Talon Gloves", "hands", "of the Assassin", 21,
             "Fingerless leather gloves, each knuckle capped with a harpy talon. Excellent for picking pockets and fights.",
             armor_type="leather"),
        make("Windrider's Cloak", "back", "of the Eagle", 21,
             "A long grey cloak that never quite sits flat. In a gale it lifts you a little, spiritually.", armor_type="cloth")]
    P["Warden Ilthae"] = [         # L20 -> 23
        make("Ilthae's Moonglaive", "main_hand", "of the Champion", 23,
             "A silver-edged glaive that cuts cleaner than it should. It does not like the Barrens at all.",
             weapon_type="polearm"),
        make("Sentinel's Moonweave Mantle", "shoulder", "of the Prophet", 23,
             "Pale cloth woven with something that is not thread. It cools, like a hand laid on your shoulder.",
             armor_type="cloth"),
        make("Warden's Quiver-Belt", "waist", "of the Hunt", 23,
             "A belt of dark leather with a hidden quiver at the back. A night-elf waistline in every way that matters.",
             armor_type="leather")]
    P["Scout-Captain Vrek"] = [    # L17 -> 20
        make("Vrek's Scout-Longbow", "ranged", "of the Marksman", 20,
             "A tall bow of horn and sinew. Built to be shot from a galloping centaur, and good at the other thing too.",
             weapon_type="bow"),
        make("Kolkar Hide Bracers", "wrist", "of the Falcon", 20,
             "Hide bracers dyed with red clay and a thousand miles of road.", armor_type="leather"),
        make("Wind-Bell Ring", "ring", "of the Monkey", 20,
             "A ring with a tiny bell. When you run it chimes, and the centaurs call that 'being found'.")]
    P["Kragg the Wall-Breaker"] = [  # L17 -> 20
        make("Wallbreaker's Maul", "main_hand", "of the Juggernaut", 20,
             "A two-handed maul with a head the size of a gate. It was built for gates. It's open to other suggestions.",
             weapon_type="mace_2h"),
        make("Siege-Plate Vambraces", "wrist", "of the Defender", 20,
             "Plate vambraces cut from a Kolkar siege-ram's iron shoulder. They have a deep, satisfied clang.",
             armor_type="plate"),
        make("Kolkar War-Charm", "neck", "of the Bear", 20,
             "A charm of horn and iron. Each notch is a wall. There are many notches.")]
    P["Prospector Delvik"] = [     # L16 -> 19
        make("Delvik's Blasting Pick", "main_hand", "of the Gladiator", 19,
             "A pickaxe with a tiny fuse-holder in the haft. A prospector does not so much dig as persuade.",
             weapon_type="axe_1h"),
        make("Prospector's Dented Hardhat", "head", "of the Soldier", 19,
             "A dented mining helmet with a candle-bracket. It is almost always still faintly warm.",
             armor_type="mail"),
        make("Dynamite Bandolier", "waist", "of the Marksman", 19,
             "A bandolier of empty dynamite loops. The full ones are, wisely, not included.", armor_type="leather")]
    P["Windcaller Skreeva"] = [    # L18 -> 21
        make("Skreeva's Gale-Wand", "ranged", "of the Archmage", 21,
             "A wand carved from a harpy wing-bone. The shriek, when it casts, is very much on purpose.", weapon_type="wand"),
        make("Windspeaker's Cowl", "head", "of the Archmage", 21,
             "A feathered cowl that muffles every sound except wind. Spellcasting in it feels like speaking in a gale.",
             armor_type="cloth"),
        make("Featherbound Mending-Bracers", "wrist", "of the Physician", 21,
             "Cloth bracers bound with small, warm feathers. Wounds nearby close a little faster, and a little reluctantly.",
             armor_type="cloth")]
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
    z = data["zones"]["Northern Barrens"]
    z["open_zone"] = OPEN_ZONE
    z["subzones"] = SUBZONES
    z["caves"] = CAVES
    ep.write_text(json.dumps(data, indent=2) + "\n")

    qp = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(qp.read_text())
    D = data["drops"]
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    out = {"_notes": "Northern Barrens boss + named-rare loot (2026-10-21). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/northern_barrens_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, tables {len(SUBZONES)} subzones + {len(CAVES)} caves, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
