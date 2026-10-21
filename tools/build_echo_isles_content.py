#!/usr/bin/env python3
"""Echo Isles content pass (2026-10-21).  Idempotent.

  python3 tools/build_echo_isles_content.py && python3 tools/generate_creatures.py

Map reference (160x160 archipelago, see tools/handbuilt_echo_isles.py)
  Echo Landing village .... (80,50) main island      Troll Camps ....... (111-147, 39-73) east island
  Naga Ruins .............. (10-42, 36-62) NW        The Lost Fleet .... (133-161, 9-35) NE
  Razorjaw Reef ........... (31-64, 128-150) SW      Zalazane's Hollow . cave mouth (141,117) SE island
  Sunken Temple Grotto .... cave mouth (24,98) W island
  shallow-water subzones (wade-able, `base_tiles=shallow_water`):
     Wreck Shallows (127-147, 26-46)    Drowned Causeway (120-140, 62-98)   Sunken Steps (18-38, 56-82)
     Razorjaw Shallows (55-77, 112-142) Tidal Flats (90-120, 114-138)

LEVEL LADDER   Isle Interior 10-12 | Tidal Flats 10-12 | Reef / Wreck Shallows 11-13 | Troll Camps 12-13
               Naga / Fleet / Causeway / Steps 12-14 | caves 12-14 | bosses Razorjaw / Ssaleth / Morrow 14,
               Gharesh / Zalazane 15.  Named rares 12-14.
LOOT           ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    # --- beaches / jungle
    "Isle Coconut Crab": C("beast_large", 10, 12, "coconut_crab"),
    "Isle Screecher": C("beast_fast", 10, 12, "isle_screecher"),
    # --- trolls
    "Zalazane Fetish-Carver": C("humanoid_caster", 12, 14, "fetish_carver"),
    "Hollow Skullbreaker": C("humanoid_warrior", 13, 14, "hollow_skullbreaker"),
    # --- wading / aquatic
    "Wreck Scavenger": C("beast_basic", 11, 13, "wreck_scavenger"),
    "Bilge Eel": C("vermin_sneaky", 11, 13, "bilge_eel"),
    "Causeway Siren": C("humanoid_caster", 12, 13, "causeway_siren"),
    "Murloc Spearfisher": C("aquatic_basic", 11, 13, "murloc_spearfisher"),
    "Stepstone Sentinel": C("elemental_bruiser", 12, 13, "stepstone_sentinel"),
    "Razorjaw Whelp": C("beast_fast", 11, 13, "razor_whelp"),
    "Flatfin Stinger": C("vermin_sneaky", 10, 12, "flatfin_stinger"),
    "Sand Burrower": C("beast_basic", 10, 12, "sand_burrower"),
    # --- named rares
    "Houndmaster Gor'tek": C("humanoid_warrior", 14, 14, "gortek_houndmaster", True, 1.7),
    "Mam'toth the Hexweaver": C("humanoid_caster", 14, 14, "mamtoth_hexweaver", True, 1.7),
    "Moj'bashi the Drowned": C("undead_basic", 13, 13, "mojbashi_drowned", True, 1.7),
    "Seer Sshara": C("humanoid_caster", 13, 13, "sshara_seer", True, 1.6),
    "Shellcrusher Kragg": C("beast_large", 12, 12, "kragg_shellcrusher", True, 1.7),
    "Old Barnacle-Beard": C("undead_basic", 13, 13, "barnacle_beard", True, 1.6),
}

FIXES = {
    "Bloodtalon Raptor": {"level_range": [10, 12]},
    "Jungle Panther": {"level_range": [10, 12]},
    "Isle Serpent": {"level_range": [10, 12]},
    "Voodoo Troll": {"level_range": [12, 13]},
    "Hex Troll": {"level_range": [12, 13]},
    "Zalazane Berserker": {"level_range": [12, 13]},
    "Isle Headhunter": {"level_range": [12, 13]},
    "Razorjaw Lurker": {"level_range": [11, 13]},
    "Reef Stalker": {"level_range": [11, 13]},
    "Naga Coastguard": {"level_range": [12, 14]},
    "Naga Tidecaller": {"level_range": [12, 14]},
    "Drowned Crewman": {"level_range": [12, 14]},
    "Waterlogged Gunner": {"level_range": [12, 14]},
    "Grotto Murloc": {"level_range": [12, 13]},
    "Tidal Elemental": {"level_range": [12, 14]},
    "Drowned Troll": {"level_range": [12, 14]},
    "Hexed Thrall": {"level_range": [13, 14]},
    "Voodoo Adept": {"level_range": [13, 14]},
    "Shadowfang Guardian": {"level_range": [13, 14]},
    "Tidelord Gharesh": {"level_range": [15, 15]},
    "Zalazane": {"level_range": [15, 15]},
}

RARES = ["Old Barnacle-Beard", "Seer Sshara", "Shellcrusher Kragg"]


def tbl(display, **c):
    return {"name": display, "creatures": c}


OPEN_ZONE = tbl("The Isle Interior", **{
    "Bloodtalon Raptor": 3, "Jungle Panther": 2, "Isle Serpent": 2,
    "Isle Coconut Crab": 2, "Isle Screecher": 2})

SUBZONES = {
    "Troll Camps": tbl("The Troll Camps", **{
        "Voodoo Troll": 2, "Hex Troll": 2, "Zalazane Berserker": 2, "Isle Headhunter": 2,
        "Zalazane Fetish-Carver": 1}),
    "Razorjaw Reef": tbl("Razorjaw Reef", **{
        "Razorjaw Lurker": 2, "Reef Stalker": 2, "Razorjaw Whelp": 2, "The Razorjaw": 0}),
    "Naga Ruins": tbl("Naga Ruins", **{
        "Naga Coastguard": 3, "Naga Tidecaller": 2, "Causeway Siren": 1, "Warden Ssaleth": 0}),
    "The Lost Fleet": tbl("The Lost Fleet", **{
        "Drowned Crewman": 3, "Waterlogged Gunner": 2, "Wreck Scavenger": 1, "Captain Morrow": 0}),
    "Wreck Shallows": tbl("Wreck Shallows", **{
        "Wreck Scavenger": 3, "Bilge Eel": 3, "Drowned Crewman": 1, "Old Barnacle-Beard": 0}),
    "Drowned Causeway": tbl("Drowned Causeway", **{
        "Murloc Spearfisher": 3, "Causeway Siren": 2, "Bilge Eel": 1, "Seer Sshara": 0}),
    "Sunken Steps": tbl("Sunken Steps", **{
        "Stepstone Sentinel": 2, "Murloc Spearfisher": 2, "Naga Coastguard": 1}),
    "Razorjaw Shallows": tbl("Razorjaw Shallows", **{
        "Razorjaw Whelp": 3, "Reef Stalker": 2, "Flatfin Stinger": 1}),
    "Tidal Flats": tbl("Tidal Flats", **{
        "Sand Burrower": 3, "Flatfin Stinger": 3, "Isle Coconut Crab": 1, "Shellcrusher Kragg": 0}),
}

CAVES = {
    "Sunken Temple Grotto": tbl("Sunken Temple Grotto", **{
        "Grotto Murloc": 3, "Murloc Spearfisher": 2, "Tidal Elemental": 2, "Drowned Troll": 2,
        "Naga Tidecaller": 1, "Naga Coastguard": 1, "Stepstone Sentinel": 1,
        "Moj'bashi the Drowned": 0, "Tidelord Gharesh": 0}),
    "Zalazane's Hollow": tbl("Zalazane's Hollow", **{
        "Hexed Thrall": 3, "Voodoo Adept": 2, "Shadowfang Guardian": 2, "Zalazane Fetish-Carver": 1,
        "Hollow Skullbreaker": 2, "Houndmaster Gor'tek": 0, "Mam'toth the Hexweaver": 0, "Zalazane": 0}),
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Isle Coconut Crab": [qd("sturdy_reef_coral", "Sturdy Reef Coral",
                             "Deep-red coral, tougher than the decorative kind. The crabs drag it up the beach to line their burrows.", 0.5)],
    "Bilge Eel": [qd("eel_hide_cord", "Eel-Hide Cord",
                     "A supple length of cured eel-skin. It will hold a net together through a storm. It will not hold a grudge.", 0.5)],
    "Drowned Crewman": [qd("waterlogged_chart", "Waterlogged Chart",
                           "A sea chart gone to pulp at the edges. The middle is still legible: a ring of islands and a cross in red.", 0.4)],
    "Waterlogged Gunner": [qd("waterlogged_chart", "Waterlogged Chart",
                              "A sea chart gone to pulp at the edges. The middle is still legible: a ring of islands and a cross in red.", 0.4)],
    "Naga Coastguard": [qd("tide_etched_scale", "Tide-Etched Naga Scale",
                           "A pearly scale scored with spiral runes. The marks move if you stare at them.", 0.45)],
    "Naga Tidecaller": [qd("tide_etched_scale", "Tide-Etched Naga Scale",
                           "A pearly scale scored with spiral runes. The marks move if you stare at them.", 0.5)],
    "Grotto Murloc": [qd("tide_touched_pearl", "Tide-Touched Pearl",
                         "A grey pearl that is damp no matter how long it sits in the sun.", 0.45)],
    "Tidal Elemental": [qd("tide_touched_pearl", "Tide-Touched Pearl",
                           "A grey pearl that is damp no matter how long it sits in the sun.", 0.4)],
    "Zalazane Fetish-Carver": [
        qd("hex_bone_shard", "Hex-Carved Bone Shard",
           "A sliver of bone with a Darkspear name cut into it, then crossed out. Zathra says that is the worst part.", 0.5),
        qd("hexed_darkspear_totem", "Hexed Darkspear Totem",
           "A Darkspear fetish, twisted by Zalazane's hex but not beyond recognizing. Still warm with old magic.", 0.4)],
}


def pools():
    P = {}
    # ---------------- bosses ------------------------------------------------
    P["The Razorjaw"] = [      # L14 -> 17  beast-apex: 2H melee / agi leather / tank shield / caster neck
        make("Razorjaw's Serrated Edge", "main_hand", "of the Gladiator", 17,
             "A tooth the length of a forearm in a driftwood hilt. It bites the way it was grown to.",
             weapon_type="sword_2h"),
        make("Sharkskin Reaver's Vest", "chest", "of the Bandit", 17,
             "Cured while it was still angry. The grain runs towards the wearer's prey.", armor_type="leather"),
        make("Apex-Jaw Bulwark", "off_hand", "of Blocking", 17,
             "Two plates of fused jawbone. Nothing has bitten through it since.", weapon_type="shield"),
        make("Reefcaller's Tidal Choker", "neck", "of the Sorcerer", 17,
             "A tooth, a pearl and a promise. The reef answers to it, politely.")]
    P["Warden Ssaleth"] = [    # L14 -> 17  naga ruin-warden: polearm / mail chest / healer cloth hood / tank belt
        make("Ssaleth's Tidal Trident", "main_hand", "of the Soldier", 17,
             "Three barbed tines and a shaft of fossil coral. It hums at high tide.", weapon_type="polearm"),
        make("Warden's Scalemail Hauberk", "chest", "of the Beast", 17,
             "Overlapping scales that shed water the way a roof sheds rain.", armor_type="mail"),
        make("Runekeeper's Drowned Cowl", "head", "of the Prophet", 17,
             "The inside is lined with tiny runes. Reading them aloud is discouraged.", armor_type="cloth"),
        make("Coil of the Ruin-Warden", "waist", "of the Defender", 17,
             "A belt of braided kelp-iron. It will outlast the temple it came from.", armor_type="plate")]
    P["Captain Morrow"] = [    # L14 -> 17  drowned captain: 1H sword / gun / tank plate coat / healer ring
        make("Captain Morrow's Boarding Cutlass", "main_hand", "of the Bandit", 17,
             "Pitted to the guard, still sharp where it counts.", weapon_type="sword_1h"),
        make("Dead Man's Flintlock", "ranged", "of the Marksman", 17,
             "It fired once more, the day they pulled it up. Nobody liked how it sounded.", weapon_type="gun"),
        make("Drowned Captain's Greatcoat", "chest", "of the Juggernaut", 17,
             "Heavy with brine and brass. It still stands up on its own.", armor_type="plate"),
        make("Barnacled Signet of the Tides", "ring", "of the Restorer", 17,
             "The crest on it is a lighthouse. The nearest one is four hundred miles away.")]
    P["Tidelord Gharesh"] = [  # L15 -> 18  tide elemental: frost staff / healer mail crown / tank greaves / agi cloak
        make("Tide-Heart Staff", "main_hand", "of Frozen Wrath", 18,
             "A column of standing water trapped in a staff. The pull of it is slightly unreasonable.",
             weapon_type="staff"),
        make("Crown of the Drowned Tidelord", "head", "of the Hierophant", 18,
             "Pearl and kelp-iron. The wearer breathes easier, and a little wetter.", armor_type="mail"),
        make("Surge-Wrought Greaves", "legs", "of the Bastion", 18,
             "Plates that move with the tide. They do not move with you, unless you ask nicely.",
             armor_type="plate"),
        make("Foam-Spun Cloak", "back", "of the Wolf", 18,
             "Spun from sea-foam and something stubborn. It never quite dries.", armor_type="cloth")]
    P["Zalazane"] = [          # L15 -> 18  witch-doctor: shadow scepter / healer mantle / hunter mail / 2H mace
        make("Zalazane's Hexcarved Scepter", "main_hand", "of Shadow Wrath", 18,
             "Every notch is a name. Some of the names are still listening.", weapon_type="mace_1h"),
        make("Mantle of the Darkspear Claimed", "shoulder", "of the Restorer", 18,
             "Woven of the feathers of a hundred prayers. Zalazane never answered a single one.",
             armor_type="cloth"),
        make("Bonewoven Spiritwalker Harness", "chest", "of the Hunt", 18,
             "Ribs of a dozen beasts, tied in a knot that only a hunter can untie.", armor_type="mail"),
        make("Hexbreaker's Maul", "main_hand", "of the Soldier", 18,
             "A club of petrified mangrove with a skull-shaped head. It was made to unmake hexes.",
             weapon_type="mace_2h")]
    # ---------------- named rares ------------------------------------------
    P["Houndmaster Gor'tek"] = [   # L14 -> 17  kennel: 1H axe / agi leather legs / mail shoulders / hunter neck
        make("Kennel-Keeper's Hooked Axe", "main_hand", "of Striking", 17,
             "One side for splitting, the other for dragging a stubborn hound home.", weapon_type="axe_1h"),
        make("Houndhide Leggings", "legs", "of the Monkey", 17,
             "Stitched from three different dogs. They would have gotten along.", armor_type="leather"),
        make("Pack-Bound Spaulders", "shoulder", "of the Beast", 17,
             "Chain links studded with teeth. Some of them are even the hound's.", armor_type="mail"),
        make("Whistle of the Kennelmaster", "neck", "of the Falcon", 17,
             "Silent to people. The hounds hear it three islands away.")]
    P["Mam'toth the Hexweaver"] = [  # L14 -> 17  hexweaver: void staff / necro legs / healer belt / shadow ring
        make("Hexweaver's Spindle", "main_hand", "of the Void", 17,
             "A drop-spindle wound with something that is not wool.", weapon_type="staff"),
        make("Threads of Mam'toth", "legs", "of the Necromancer", 17,
             "The hem moves a little when you are not looking at it.", armor_type="cloth"),
        make("Weaver's Binding Cord", "waist", "of the Physician", 17,
             "A hex cord, repurposed. Healers swear it is not so very different.", armor_type="cloth"),
        make("Hexbound Fetish Ring", "ring", "of Shadow Wrath", 17,
             "The fetish has a face. The face has opinions.")]
    P["Moj'bashi the Drowned"] = [   # L13 -> 16  drowned troll: 1H sword / tank leather boots / whale ring
        make("Drowned Warrior's Brineblade", "main_hand", "of the Squire", 16,
             "A Darkspear blade that spent forty years underwater and learned patience.", weapon_type="sword_1h"),
        make("Kelp-Slick Boots", "feet", "of the Ironfur", 16,
             "Slippery on the outside, steady on the inside. Which is the right way round.",
             armor_type="leather"),
        make("Tide-Bound Troll Ring", "ring", "of the Whale", 16,
             "A ring of braided sinew. It remembers breathing, and tries to remind you.")]
    P["Seer Sshara"] = [             # L13 -> 16  naga seer: healer mace / caster hood / mail bracers / caster neck
        make("Seer's Pearl Scepter", "main_hand", "of the Prophet", 16,
             "A black pearl in a coral claw. The reflection in it is slightly ahead of you.",
             weapon_type="mace_1h"),
        make("Sshara's Veil of Brine", "head", "of the Mind's Eye", 16,
             "Spider-fine silk that tastes of the sea. The wearer sees in two directions at once.",
             armor_type="cloth"),
        make("Seastrand Wristlets", "wrist", "of the Seer", 16,
             "Mail links the size of rice grains. The tide has polished every one.", armor_type="mail"),
        make("Siren's Tear", "neck", "of the Archmage", 16,
             "A drop of brine that never fell. It rings faintly when something sings nearby.")]
    P["Shellcrusher Kragg"] = [       # L12 -> 15  giant crab: plate pauldrons / 1H mace / shield
        make("Shellcrusher Pauldrons", "shoulder", "of the Juggernaut", 15,
             "Carapace plate the size of a dinner platter. The edges are surprisingly polite.",
             armor_type="plate"),
        make("Claw-Hammer of the Flats", "main_hand", "of the Gladiator", 15,
             "A claw, lashed to a haft. It has not forgotten its last meal.", weapon_type="mace_1h"),
        make("Crab-Shell Buckler", "off_hand", "of Stamina", 15,
             "Smaller than it looks, harder than it should be.", weapon_type="shield")]
    P["Old Barnacle-Beard"] = [       # L13 -> 16  drowned mate: axe / hunter hood / cloth sash / crossbow
        make("Barnacle-Beard's Boarding Axe", "main_hand", "of the Bandit", 16,
             "The edge has more barnacles than steel. It cuts anyway, out of spite.", weapon_type="axe_1h"),
        make("Salt-Stiffened Tricorn", "head", "of the Hunt", 16,
             "It has seen a lot of weather. None of it was good.", armor_type="leather"),
        make("Rum-Soaked Sash", "waist", "of the Owl", 16,
             "You can smell the past. You can also smell the rum. They overlap.", armor_type="cloth"),
        make("Boarding Crossbow", "ranged", "of the Marksman", 16,
             "A ship's crossbow, built to fire across a deck and not look back.", weapon_type="crossbow")]
    return P


def main():
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text())
    data["creatures"].update(NEW_CREATURES)
    for n, patch in FIXES.items():
        data["creatures"][n].update(patch)
    # the old generic "Drowned Troll" pinned rare is now a trash mob; Moj'bashi is the rare
    data["creatures"]["Drowned Troll"].update({"is_boss": False})
    p.write_text(json.dumps(data, indent=2) + "\n")

    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text())
    z = data["zones"]["Echo Isles"]
    z["open_zone"] = OPEN_ZONE
    z["subzones"] = SUBZONES
    z["caves"] = CAVES
    p.write_text(json.dumps(data, indent=2) + "\n")

    p = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(p.read_text())
    D = data["drops"]
    D.pop("Jungle Panther", None)     # the old coral source; coconut crabs carry it now
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    out = {"_notes": "Echo Isles boss + named-rare loot (2026-10-21). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/echo_isles_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, tables {len(SUBZONES)} subzones + 2 caves, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
