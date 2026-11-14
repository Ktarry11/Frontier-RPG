"""
Deathknell cluster content pass (2026-10-22): creatures, level bands, encounter tables and hand-crafted
rare / boss loot for Deathknell (valley), Night Web's Hollow and Scarlet Crypt.  Idempotent.

  tools/monster_kits.py (DEATHKNELL_KITS) is the source of truth for ability kits
  (run tools/generate_creatures.py after editing it).  This script owns:
    * data/creatures/creatures.json   (new creatures, level bands)
    * data/creatures/encounters.json  (Deathknell open_zone + subzones + caves, level_overrides)
    * data/loot/deathknell_boss_loot.json (named-rare + cave-boss pools)

LEVEL LADDER                    Valley floor 1-4 | Deathknell Graves 1-3 | Shadow Grave 2-4 | Overrun Claim 3-5
                                Weeping Pond 3-5 | Burned Farmstead 4-6 | Scarlet Forecourt 5-6
                                Night Web's Hollow 5-7 (Nesh'ka 7) | Scarlet Crypt 6-8 (Fairbanks 8)
CAVE RULE                       Caves: random trash, boss + named rares pinned (handbuilt_deathknell_caves.py).
LOOT RULES                      Same as the VoT / Durotar passes: ONE item per kill from the creature's pool, real
  formulas, item_level = creature level + 3, primary stats only below item level 10.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import build_vot_content as LOW      # noqa: E402  (ilvl < 10, primary stats only)
from tools import build_durotar_content as HIGH  # noqa: E402  (ilvl >= 10, primary + secondary)


def mk(name, slot, suffix, ilvl, flavor, **kw):
    return (HIGH if ilvl >= 10 else LOW).make(name, slot, suffix, ilvl, flavor, **kw)


def C(template, lo, hi, kit, boss=False, mult=None):
    d = {"template": template, "level_range": [lo, hi], "is_boss": boss, "ability_kit": kit}
    if boss and mult:
        d["boss_multiplier"] = mult
    return d


NEW_CREATURES = {
    # valley floor / Deathknell Graves
    "Plagued Stray": C("beast_basic", 1, 4, "plagued_stray"),
    "Grave Rat": C("vermin_swarm", 1, 3, "grave_rat"),
    # The Overrun Claim
    "Dead Digger": C("undead_basic", 3, 5, "dead_digger"),
    # Weeping Pond
    "Drowned Wretch": C("undead_basic", 3, 5, "drowned_wretch"),
    "Weeping Shade": C("elemental_caster", 3, 5, "weeping_shade"),
    # Burned Farmstead
    "Blighted Scarecrow": C("elemental_bruiser", 4, 6, "blighted_scarecrow"),
    "Burned Farmhand": C("undead_basic", 4, 6, "burned_farmhand"),
    # Scarlet Forecourt
    "Scarlet Torchbearer": C("humanoid_caster", 5, 6, "scarlet_torchbearer"),
    "Scarlet Picket": C("humanoid_warrior", 5, 6, "scarlet_picket"),
    # Night Web's Hollow
    "Brood Hatchling": C("vermin_swarm", 5, 6, "brood_hatchling"),
    # named rares
    "Mawgrin the Gaunt": C("beast_basic", 3, 3, "mawgrin_the_gaunt", True, 1.8),
    "Ossric the Unburied": C("undead_basic", 4, 4, "ossric_the_unburied", True, 1.8),
    "Goldfang": C("vermin_sneaky", 5, 5, "goldfang", True, 1.8),
    "Mourning Wren": C("elemental_caster", 5, 5, "mourning_wren", True, 1.7),
    "Gaffer Thorne": C("undead_basic", 6, 6, "gaffer_thorne", True, 1.7),
    "Sergeant Halbrook": C("humanoid_warrior", 6, 6, "sergeant_halbrook", True, 1.7),
    "Hatchery Warden Skrix": C("vermin_sneaky", 6, 6, "hatchery_warden_skrix", True, 1.7),
    "The Pale Weaver": C("vermin_sneaky", 6, 6, "pale_weaver", True, 1.7),
    "Valdric Bonewarden": C("undead_basic", 8, 8, "valdric_bonewarden", True, 1.6),
    "Brother Wystan": C("humanoid_caster", 8, 8, "brother_wystan", True, 1.6),
}

# level bands (global ranges for creatures that only live in the Deathknell cluster)
LEVEL_PATCH = {
    "Restless Grave-Dweller": (1, 3), "Shadow Grave Wight": (2, 4), "Claim Spider": (3, 5),
    "Night Web Spider": (5, 6), "Night Web Matriarch": (6, 7), "Web Wrapped Corpse": (5, 6),
    "Ravenclaw Drudger": (6, 6),
    "Crypt Crawler": (6, 7), "Scarlet Initiate": (7, 8), "Scarlet Chaplain": (7, 8), "Restless Crypt Fiend": (7, 8),
}
BOSS_LEVEL_PATCH = {"Broodmother Nesh'ka": 7, "High Inquisitor Fairbanks": 8}
KIT_PATCH = {"Web Wrapped Corpse": "web_wrapped_corpse", "Ravenclaw Drudger": "ravenclaw_drudger",
             "Crypt Crawler": "crypt_crawler"}

# creatures shared with Tirisfal (which carries its own overrides): Deathknell-only bands
LEVEL_OVERRIDES = {
    "Mangy Duskbat": [1, 4], "Ragged Scavenger": [1, 3],
    "Rattlecage Skeleton": [2, 4], "Wretched Zombie": [2, 4],
}

ENCOUNTERS = {
    "open_zone": {"creatures": {"Mangy Duskbat": 3, "Ragged Scavenger": 2, "Plagued Stray": 2}},
    "subzones": {
        "Deathknell Graves": {"name": "Deathknell Graves", "creatures": {
            "Restless Grave-Dweller": 4, "Grave Rat": 2, "Plagued Stray": 2, "Mawgrin the Gaunt": 0}},
        "Shadow Grave": {"name": "Shadow Grave", "creatures": {
            "Shadow Grave Wight": 3, "Rattlecage Skeleton": 3, "Wretched Zombie": 2, "Ossric the Unburied": 0}},
        "The Overrun Claim": {"name": "The Overrun Claim", "creatures": {
            "Claim Spider": 4, "Dead Digger": 3, "Mangy Duskbat": 1, "Goldfang": 0}},
        "Weeping Pond": {"name": "The Weeping Pond", "creatures": {
            "Drowned Wretch": 3, "Weeping Shade": 3, "Grave Rat": 1, "Mourning Wren": 0}},
        "Burned Farmstead": {"name": "The Burned Farmstead", "creatures": {
            "Blighted Scarecrow": 3, "Burned Farmhand": 3, "Ragged Scavenger": 1, "Gaffer Thorne": 0}},
        "Scarlet Forecourt": {"name": "Scarlet Forecourt", "creatures": {
            "Scarlet Picket": 3, "Scarlet Torchbearer": 3, "Sergeant Halbrook": 0}},
    },
    "caves": {
        "Night Web's Hollow": {"name": "Night Web's Hollow", "creatures": {
            "Night Web Spider": 3, "Brood Hatchling": 3, "Night Web Matriarch": 1, "Web Wrapped Corpse": 1,
            "Ravenclaw Drudger": 1, "Broodmother Nesh'ka": 0, "Hatchery Warden Skrix": 0, "The Pale Weaver": 0}},
        "Scarlet Crypt": {"name": "Scarlet Crypt", "creatures": {
            "Crypt Crawler": 2, "Scarlet Initiate": 2, "Scarlet Chaplain": 1, "Restless Crypt Fiend": 2,
            "High Inquisitor Fairbanks": 0, "Valdric Bonewarden": 0, "Brother Wystan": 0}},
    },
}


# ----------------------------------------------------------------------
def pools():
    P = {}
    # ---- Deathknell Graves rare: Mawgrin the Gaunt (L3 -> ilvl 6)
    P["Mawgrin the Gaunt"] = [
        mk("Gaunt Fang Dirk", "main_hand", "of Agility", 6,
           "Pulled from a mouth that never stopped being hungry.", weapon_type="dagger"),
        mk("Stray-Hide Jerkin", "chest", "of the Monkey", 6,
           "Mangy, patched, and still smells like wet dog and grave dirt.", armor_type="leather"),
        mk("Mawgrin's Gnawed Collar", "neck", "of the Bear", 6,
           "Someone put this on him once. Someone regretted it."),
        mk("Plaguebitten Wristwraps", "wrist", "of the Whale", 6,
           "Stained past all washing. The stains do not seem to mind.", armor_type="cloth"),
    ]
    # ---- Shadow Grave rare: Ossric the Unburied (L4 -> ilvl 7)
    P["Ossric the Unburied"] = [
        mk("Sexton's Grave-Spade", "main_hand", "of the Bear", 7,
           "Heavy iron, still crusted. It has dug more than one hole twice.", weapon_type="mace_1h"),
        mk("Ossric's Burial Shroud", "chest", "of the Owl", 7,
           "Linen that was never meant to be worn by anyone still moving.", armor_type="cloth"),
        mk("Wightbone Bracers", "wrist", "of Stamina", 7,
           "Shaped from something that used to hold a sword.", armor_type="plate"),
        mk("Rattling Skull Charm", "neck", "of the Eagle", 7,
           "It rattles when the grave wind rises. Lately, that is always."),
    ]
    # ---- The Overrun Claim rare: Goldfang (L5 -> ilvl 8)
    P["Goldfang"] = [
        mk("Goldvein Staff", "main_hand", "of the Eagle", 8,
           "A prospector's staff, veined with something that glints and bites.", weapon_type="staff"),
        mk("Spiderglass Wand", "main_hand", "of Intellect", 8,
           "Hardened silk, brittle as glass. Handle with the tips of your fingers.", weapon_type="wand"),
        mk("Gilded Silk Cord", "waist", "of the Wolf", 8,
           "Gold dust spun into the web. The spider kept the best strands.", armor_type="leather"),
        mk("Webstrand Gloves", "hands", "of the Falcon", 8,
           "Sticky for the first hour. After that, you stop noticing.", armor_type="cloth"),
    ]
    # ---- Weeping Pond rare: Mourning Wren (L5 -> ilvl 8)
    P["Mourning Wren"] = [
        mk("Wren's Tear-Stained Veil", "head", "of the Owl", 8,
           "Damp at all times. It was never dry even before the pond.", armor_type="cloth"),
        mk("Keening Wand", "main_hand", "of Spirit", 8,
           "Hold it to your ear and you will hear someone calling a name.", weapon_type="wand"),
        mk("Pond-Reed Sandals", "feet", "of the Whale", 8,
           "Woven reeds, soft with age. They leave no tracks at the water's edge.", armor_type="cloth"),
        mk("Drowned Locket Ring", "ring", "of the Eagle", 8,
           "The picture inside has long since washed out. The ring remembers it anyway."),
    ]
    # ---- Burned Farmstead rare: Gaffer Thorne (L6 -> ilvl 9)
    P["Gaffer Thorne"] = [
        mk("Thorne's Rusted Scythe", "main_hand", "of Strength", 9,
           "A harvest tool, in a harvest that never ended.", weapon_type="polearm"),
        mk("Scarecrow-Straw Cloak", "back", "of the Monkey", 9,
           "Itchy, and stuffed with something that is probably not just straw.", armor_type="cloth"),
        mk("Burnt Farmer's Gauntlets", "hands", "of the Bear", 9,
           "Scorched leather over scorched knuckles. They still grip hard.", armor_type="mail"),
        mk("Hearth-Ward Shield", "off_hand", "of Stamina", 9,
           "A barn door, cut down and reinforced. It kept a family safe once.", weapon_type="shield"),
    ]
    # ---- Scarlet Forecourt rare: Sergeant Halbrook (L6 -> ilvl 9)
    P["Sergeant Halbrook"] = [
        mk("Halbrook's Halberd", "main_hand", "of the Bear", 9,
           "The Crusade's issue polearm, with notches along the haft for every tally.", weapon_type="polearm"),
        mk("Scarlet Sergeant's Pauldrons", "shoulder", "of Strength", 9,
           "Crimson enamel over dented plate. Someone polished them every day.", armor_type="plate"),
        mk("Picket's Stout Boots", "feet", "of the Bear", 9,
           "Good for long watches and for kicking down doors.", armor_type="mail"),
        mk("Crimson Tabard-Sash", "waist", "of the Tiger", 9,
           "Faded red cloth. It still looks righteous at a distance.", armor_type="mail"),
    ]
    # ---- Night Web's Hollow rares (L6 -> ilvl 9)
    P["Hatchery Warden Skrix"] = [
        mk("Skrix's Chitin Cap", "head", "of Agility", 9,
           "Chitin plates bound with silk. Light, strong, faintly twitching.", armor_type="leather"),
        mk("Hatchery Silk Mantle", "shoulder", "of the Eagle", 9,
           "Spun around a clutch that never hatched.", armor_type="cloth"),
        mk("Brood-Warden's Spur", "main_hand", "of the Monkey", 9,
           "A leg-spur from something much larger. Still sharp enough to matter.", weapon_type="dagger"),
        mk("Eggshell Buckler", "off_hand", "of Stamina", 9,
           "Hardened shell and silk. Surprisingly good at deflecting things.", weapon_type="shield"),
    ]
    P["The Pale Weaver"] = [
        mk("Weaver's Pale Leggings", "legs", "of the Owl", 9,
           "Fine silk, the colour of bone. It is a little too fine to be natural.", armor_type="cloth"),
        mk("Silkbound Gauntlets", "hands", "of the Tiger", 9,
           "Chain and web, woven together by something patient.", armor_type="mail"),
        mk("Pale Fang Wand", "main_hand", "of Intellect", 9,
           "A single curved fang, set in ivory-coloured wood.", weapon_type="wand"),
        mk("Cocooned Cloak", "back", "of the Wolf", 9,
           "Wrapped around something once. It kept the shape.", armor_type="leather"),
    ]
    # ---- Night Web's Hollow boss: Broodmother Nesh'ka (L7 -> ilvl 10)
    P["Broodmother Nesh'ka"] = [
        mk("Nesh'ka's Venom Dagger", "main_hand", "of the Assassin", 10,
           "Still wet. Do not lick it, bro.", weapon_type="dagger"),
        mk("Brood Mother's Silk Robe", "chest", "of the Sorcerer", 10,
           "Pearly silk, warm to the touch. It hums faintly when something skitters nearby.",
           armor_type="cloth"),
        mk("Spiderfang Shortbow", "main_hand", "of the Marksman", 10,
           "Strung with a single strand of her silk. It never frays.", weapon_type="bow"),
        mk("Carapace Bulwark", "off_hand", "of Stamina", 10,
           "A slab of her own shell, ground flat and strapped to a frame.", weapon_type="shield"),
    ]
    # ---- Scarlet Crypt rares (L8 -> ilvl 11)
    P["Valdric Bonewarden"] = [
        mk("Bonewarden's Maul", "main_hand", "of the Soldier", 11,
           "Femurs, lashed to a pillar of the ossuary. It hits like a sermon.", weapon_type="mace_2h"),
        mk("Ossuary Plate Girdle", "waist", "of the Champion", 11,
           "Welded from the plates of those who came to be buried.", armor_type="plate"),
        mk("Skullkeeper's Cowl", "head", "of the Mind's Eye", 11,
           "A hood stitched to a skull-cap. The skull is not decorative.", armor_type="cloth"),
        mk("Reliquary Bone Ring", "ring", "of the Seer", 11,
           "A vertebra, polished by centuries of nervous fingers."),
    ]
    P["Brother Wystan"] = [
        mk("Wystan's Censer Mace", "main_hand", "of the Hierophant", 11,
           "The chain is the only part that is not scorched.", weapon_type="mace_1h"),
        mk("Penitent's Hood", "head", "of the Restorer", 11,
           "Wool, cut for confession. It hides a great deal.", armor_type="cloth"),
        mk("Scarlet Vigil Hauberk", "chest", "of the Physician", 11,
           "Mail under crimson. It was blessed. The blessing is still mostly intact.", armor_type="mail"),
        mk("Brother's Rosary", "neck", "of the Archmage", 11,
           "Every bead is warm. The last one is a little too warm."),
    ]
    # ---- Scarlet Crypt boss: High Inquisitor Fairbanks (L8 -> ilvl 11)
    P["High Inquisitor Fairbanks"] = [
        mk("Fairbanks' Inquisitor Mace", "main_hand", "of the Hierophant", 11,
           "The flanges are engraved with confessions. Some of them are still being added.",
           weapon_type="mace_1h"),
        mk("Crimson Inquisitor's Robe", "chest", "of the Archmage", 11,
           "Silk the colour of old wine. It never wrinkles, and it never forgives.", armor_type="cloth"),
        mk("Sanctum Warplate Greaves", "legs", "of the Champion", 11,
           "Worn by a man who believed every step was a sermon.", armor_type="plate"),
        mk("Blood-Etched Longsword", "main_hand", "of the Gladiator", 11,
           "The blade is etched with names. Yours is not there. Yet.", weapon_type="sword_1h"),
    ]
    return P


def main():
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    cr = data["creatures"]
    for n, d in NEW_CREATURES.items():
        cr[n] = d
    for n, (lo, hi) in LEVEL_PATCH.items():
        cr[n]["level_range"] = [lo, hi]
    for n, lv in BOSS_LEVEL_PATCH.items():
        cr[n]["level_range"] = [lv, lv]
    for n, k in KIT_PATCH.items():
        cr[n]["ability_kit"] = k
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    z = data["zones"]["Deathknell"]
    z["open_zone"] = ENCOUNTERS["open_zone"]
    z["subzones"] = ENCOUNTERS["subzones"]
    z["caves"] = ENCOUNTERS["caves"]
    z["level_overrides"] = LEVEL_OVERRIDES
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    out = {"_notes": "Deathknell cluster named-rare + cave-boss loot (2026-10-22). One item drops per kill "
                     "from the creature's pool. Numbers from the real loot formulas "
                     "(tools/build_deathknell_content.py)."}
    out.update(pools())
    (ROOT / "data/loot/deathknell_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    n_items = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, level patches {len(LEVEL_PATCH)+len(BOSS_LEVEL_PATCH)}, "
          f"loot pools {len(out)-1}, items {n_items}")


if __name__ == "__main__":
    main()
