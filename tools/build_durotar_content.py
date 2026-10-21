"""
Durotar content pass (2026-10-21): creatures, level bands, encounter tables and
hand-crafted rare / boss loot for the Durotar open world.  Idempotent.

  tools/monster_kits.py (DUROTAR_OPEN_KITS) is the source of truth for ability
  kits (run tools/generate_creatures.py after editing it).  This script owns:
    * data/creatures/creatures.json   (new creatures, level bands, fixes)
    * data/creatures/encounters.json  (Durotar open_zone + subzones; caves untouched)
    * data/loot/durotar_boss_loot.json (named-rare + open-world boss pools)

LEVEL BANDS (open world)       Red Wastes 6-10 | Rocktusk Farm 6-10 | Scuttle Coast 7-10
                               Thunder Ridge 8-12 | Kolkar Crag 8-12 | Skull Rock Approach 8-12
LOOT RULES                      identical to the VoT pass, except item level is now >= 10 so
  the game allows secondary stats (spell power, healing power, ratings, mp5 ...).  Those
  go into `secondary_stats`, rounded to one decimal exactly like LootGenerator._roll_stats.
  ONE item drops per kill (entities/boss_loot.py); item_level = creature level + 3.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.loot_generator import LootGenerator  # noqa: E402

LG = LootGenerator()
PRIMARY = {"strength", "agility", "intellect", "stamina", "spirit"}


# ----------------------------------------------------------------------
# item builder - real formulas, primary + secondary stats (ilvl >= 10)
# ----------------------------------------------------------------------
def _stats(suffix, budget):
    assert suffix in LG.gear_suffixes, suffix
    prim, sec = {}, {}
    for stat, w in LG.gear_suffixes[suffix]["stats"].items():
        raw = budget * w / LG.stat_budget_costs.get(stat, 1.0)
        if stat in PRIMARY:
            v = round(raw)
            if v > 0:
                prim[stat] = v
        else:
            v = round(raw, 1)
            if v > 0:
                sec[stat] = v
    return prim, sec


def make(name, slot, suffix, ilvl, flavor, armor_type=None, weapon_type=None,
         req=None, rarity="rare"):
    assert ilvl >= 10, "use tools/build_vot_content.make below item level 10"
    r = LG.rarity_tiers[rarity]["stat_budget_multiplier"]
    d = {"name": name, "slot": slot, "item_level": ilvl, "rarity": rarity,
         "required_level": req if req is not None else max(1, ilvl - 3),
         "flavor_text": flavor}
    if weapon_type:
        wt = LG.weapon_types["weapon_types"][weapon_type]
        d["weapon_type"] = weapon_type
        if weapon_type == "shield":
            budget = ilvl * LG.STAT_BUDGET_BASE_MULT * r * 0.75
            d["primary_stats"] = {"stamina": max(1, int(budget * 0.6))}
            d["armor_value"] = int(ilvl * 1.2 * r)
            d["block_value"] = int(ilvl * 1.5 * r)
            return d
        hand = wt["hand"]
        wtier = "weapon_two_hand" if hand == "two_hand" else "weapon_medium"
        budget = (ilvl * LG.STAT_BUDGET_BASE_MULT * r
                  * LG.slots["weight_tiers"][wtier] * wt["budget_multiplier"])
        d["primary_stats"], d["secondary_stats"] = _stats(suffix, budget)
        tier = wt.get("damage_tier", "one_hand")
        mult = LG.weapon_types["damage_tiers"][tier]["dps_multiplier"]
        avg = (ilvl * 1.1 + 6.4) * r * mult
        d["weapon_damage_min"] = max(1, int(avg * 0.85))
        d["weapon_damage_max"] = max(d["weapon_damage_min"] + 1, int(avg * 1.15))
        d["attack_speed"] = wt["base_attack_speed"]
        return d
    sd = LG.slots["slots"][slot]
    w = LG.slots["weight_tiers"][sd["weight_tier"]]
    budget = ilvl * LG.STAT_BUDGET_BASE_MULT * r * w
    d["primary_stats"], d["secondary_stats"] = _stats(suffix, budget)
    if sd["armor_slot"] and armor_type:
        d["armor_type"] = armor_type
        mult = LG.armor_types["armor_types"][armor_type]["armor_multiplier"]
        d["armor_value"] = int(ilvl * 1.5 * mult * w * r)
    return d


# ----------------------------------------------------------------------
# LOOT POOLS
# ----------------------------------------------------------------------
def pools():
    P = {}
    # ---- Red Wastes rare: Old Redtooth (L11 -> ilvl 14): rogue / hunter / healer / mail
    P["Old Redtooth"] = [
        make("Redtooth's Fang-Knife", "main_hand", "of the Assassin", 14,
             "Pulled from the jaw of the alpha himself. Still thinks it's hunting.",
             weapon_type="dagger"),
        make("Rustfang Hunter's Mask", "head", "of the Hunt", 14,
             "Hyena-hide, stitched around a skull that did not need it any more.",
             armor_type="leather"),
        make("Pack-Mother's Charm", "neck", "of the Restorer", 14,
             "Every pack has someone who keeps the others alive. This is what she wore.",
             ),
        make("Hauberk of the Alpha", "chest", "of the Beast", 14,
             "Layers of hide and scale. It shrugs off teeth with a sort of smug patience.",
             armor_type="mail"),
    ]
    # ---- Thunder Ridge rare: Rumblejaw (L12 -> ilvl 15): tank / caster 2H / healer mail / plate
    P["Rumblejaw"] = [
        make("Rumblejaw's Slab", "off_hand", "of Stamina", 15,
             "A plate of fused ridge-stone. Rattles, faintly, when something big walks by.",
             weapon_type="shield"),
        make("Thunderbitten Staff", "main_hand", "of the Invoker", 15,
             "The wood is petrified. The lightning it holds is not.",
             weapon_type="staff"),
        make("Seer's Stoneplate Bracers", "wrist", "of the Seer", 15,
             "Slate bracers. Listen to them and you can hear the ridge settling.",
             armor_type="mail"),
        make("Quake-Walker's Greaves", "legs", "of the Soldier", 15,
             "Heavy plates that don't care how the ground feels about it.",
             armor_type="plate"),
    ]
    # ---- Kolkar Crag rare: Bloodhoof the Lamed (L12 -> ilvl 15): 2H melee / agi leather / mail boots / healer ring
    P["Bloodhoof the Lamed"] = [
        make("Lamed Outrider's Glaive", "main_hand", "of the Gladiator", 15,
             "Balanced for a rider with one good leg. Rides on regardless.",
             weapon_type="polearm"),
        make("Outrider's Hunting Belt", "waist", "of the Hunt", 15,
             "A Kolkar belt, studded with the tags of every kill he refused to stop counting.",
             armor_type="leather"),
        make("Hoofbeat Greaves", "feet", "of the Tiger", 15,
             "You can feel a gallop in the soles. Even standing still.",
             armor_type="mail"),
        make("Wrangler's Mending Band", "ring", "of the Restorer", 15,
             "The ring he used on wounded mounts. It did a lot of mending, in the end.",
             ),
    ]
    # ---- Rocktusk Farm rare: Matron Sowbelly (L10 -> ilvl 13): tank 1H / healer cloth / trinket / plate hands
    P["Matron Sowbelly"] = [
        make("Farmyard Tenderiser", "main_hand", "of the Soldier", 13,
             "A fence-post with ideas. The Matron had opinions about fences.",
             weapon_type="mace_1h"),
        make("Sowbelly's Silk Shawl", "shoulder", "of the Prophet", 13,
             "Somebody wove this for a farmer's wife. She never got to wear it.",
             armor_type="cloth"),
        make("Matron's Ear-Tag", "trinket", "of the Defender", 13,
             "Iron, numbered, and still warm. She was number one.",
             ),
        make("Trough-Scrapers", "hands", "of the Champion", 13,
             "Plate gauntlets, dented in a way that only makes sense if you have met the Matron.",
             armor_type="plate"),
    ]
    # ---- Scuttle Coast rare: Gillfin the Net-Cutter (L11 -> ilvl 14): rogue / ranged / caster cloth / neck
    P["Gillfin the Net-Cutter"] = [
        make("Net-Cutter's Hooked Blade", "main_hand", "of the Duelist", 14,
             "Half a sword, half a gaff. Entirely sure which half it prefers.",
             weapon_type="sword_1h"),
        make("Driftwood Harpoon-Crossbow", "ranged", "of the Marksman", 14,
             "Fires harpoons. The harpoons are mostly spite.",
             weapon_type="crossbow"),
        make("Tidewrack Wristwraps", "wrist", "of the Tactician", 14,
             "Dry-rotted netting, enchanted by someone with a long memory of drowning.",
             armor_type="cloth"),
        make("Pearl of the Net-Cutter", "neck", "of the Archmage", 14,
             "Pried from a clam that took it personally.",
             ),
    ]
    # ---- Skull Rock Approach rare: Houndmaster Kraygh (L13 -> ilvl 16): wand / gun / plate chest / cloth hands
    P["Houndmaster Kraygh"] = [
        make("Kraygh's Felwhip Wand", "ranged", "of Shadow Wrath", 16,
             "The leather's burned into the grip. It cracks even when you're not holding it.",
             weapon_type="wand"),
        make("Houndmaster's Fel-Pistol", "ranged", "of the Restorer", 16,
             "Fires something that mends the hounds. You've just decided it mends you instead.",
             weapon_type="gun"),
        make("Kennel-Keeper's Plate", "chest", "of the Juggernaut", 16,
             "Spiked and scorched in all the places a hound likes to bite.",
             armor_type="plate"),
        make("Netherfire Handwraps", "hands", "of Netherfire", 16,
             "They glow when the dark is close. They're glowing now.",
             armor_type="cloth"),
    ]
    # ---- Kolkar Crag boss: Warlord Krellian (L12 -> ilvl 15)
    P["Warlord Krellian"] = [
        make("Krellian's Cleaver", "main_hand", "of the Gladiator", 15,
             "A Kolkar war-axe, longer than the hand that held it.",
             weapon_type="axe_2h"),
        make("Warlord's Hierophant Cloak", "back", "of the Hierophant", 15,
             "Sun-faded scarlet. Smells of smoke, hides, and a prayer to someone who stopped answering.",
             armor_type="accessory"),
        make("Crag-Scale Legguards", "legs", "of the Defender", 15,
             "Mail laced with small plates, each stamped with a Kolkar brand.",
             armor_type="mail"),
        make("Kolkar Horn Bow", "ranged", "of the Hunt", 15,
             "Drawn from the horn of a beast older than the Kolkar are.",
             weapon_type="bow"),
    ]
    # ---- Thunder Ridge boss: Stormhide Patriarch (L12 -> ilvl 15)
    P["Stormhide Patriarch"] = [
        make("Patriarch's Thunderhammer", "main_hand", "of the Spell Breaker", 15,
             "The spark inside never goes out. It's been trying to for a while.",
             weapon_type="mace_2h"),
        make("Stormhide Pauldrons", "shoulder", "of the Ironfur", 15,
             "Thick, static-crackling hide. Rubs the wrong way on cold mornings.",
             armor_type="leather"),
        make("Cracked-Plate Girdle", "waist", "of the Bastion", 15,
             "Scales fused into a belt by a bolt of lightning that nobody asked for.",
             armor_type="plate"),
        make("Storm-Eye Idol", "trinket", "of the Mind's Eye", 15,
             "Stare at it long enough and it stares back with the weather.",
             ),
    ]
    return P


# ----------------------------------------------------------------------
# CREATURES
# ----------------------------------------------------------------------
def C(template, lo, hi, kit, boss=False, mult=None):
    d = {"template": template, "level_range": [lo, hi], "is_boss": boss, "ability_kit": kit}
    if boss and mult:
        d["boss_multiplier"] = mult
    return d


NEW_CREATURES = {
    # open Red Wastes
    "Rustfang Hyena": C("beast_fast", 6, 9, "rustfang_hyena"),
    "Mesa Stonebiter": C("beast_large", 7, 10, "mesa_stonebiter"),
    # Thunder Ridge
    "Static Hatchling": C("vermin_swarm", 8, 10, "static_hatchling"),
    "Ridge Stormbinder": C("elemental_caster", 9, 12, "ridge_stormbinder"),
    # Kolkar Crag (Durotar-only version of the lancer; Kolkar Raider is shared with N. Barrens)
    "Kolkar Warrider": C("humanoid_warrior", 9, 12, "centaur_lancer"),
    # Rocktusk Farm
    "Rocktusk Farmhand": C("humanoid_warrior", 6, 9, "rocktusk_farmhand"),
    "Tamed Razorback": C("beast_basic", 6, 9, "tamed_razorback"),
    # Scuttle Coast
    "Saltcrust Crab": C("aquatic_basic", 7, 10, "saltcrust_crab"),
    "Murloc Netcaster": C("aquatic_basic", 7, 10, "murloc_netcaster"),
    # Skull Rock Approach
    "Burning Blade Torchbearer": C("humanoid_warrior", 9, 12, "burning_blade_torchbearer"),
    "Cinder Imp": C("demon_caster", 8, 11, "cinder_imp"),
    # named rares (roll at ~6% per encounter in their subzone)
    "Old Redtooth": C("beast_fast", 11, 11, "redtooth", True, 1.7),
    "Rumblejaw": C("beast_large", 12, 12, "rumblejaw", True, 1.6),
    "Bloodhoof the Lamed": C("humanoid_warrior", 12, 12, "bloodhoof_the_lamed", True, 1.7),
    "Matron Sowbelly": C("beast_basic", 10, 10, "matron_sowbelly", True, 1.9),
    "Gillfin the Net-Cutter": C("aquatic_basic", 11, 11, "gillfin_net_cutter", True, 1.7),
    "Houndmaster Kraygh": C("humanoid_caster", 13, 13, "houndmaster_kraygh", True, 1.6),
}

# level bands for creatures that only live in Durotar's open world
LEVEL_PATCH = {
    "Razormane Quilboar": (6, 10), "Armored Scorpid": (6, 9), "Durotar Prowler": (6, 10),
    "Sunbaked Vulture": (6, 9), "Elder Mottled Boar": (6, 9),
    "Bloodtalon Scythemaw": (7, 10), "Southfury Crocolisk": (7, 10),
    "Thunder Lizard": (8, 11), "Crackling Thunderhide": (8, 12),
    "Razormane Battleguard": (6, 10), "Razormane Scout": (6, 10), "Razormane Geomancer": (6, 10),
    "Kolkar Outrunner": (8, 12), "Kolkar Pack Runner": (8, 12),
    "Kolkar Windchaser": (8, 12), "Kolkar Wrangler": (8, 12),
    "Coastal Murloc": (7, 10), "Murloc Tidehunter": (7, 10), "Murloc Oracle": (7, 10),
    "Drowned Deckhand": (7, 10),
    "Searing Blade Scout": (8, 12), "Searing Blade Raider": (8, 12), "Coastal Harpy": (8, 11),
}
BOSS_LEVEL_PATCH = {"Warlord Krellian": 12, "Stormhide Patriarch": 12}

ENCOUNTERS = {
    "open_zone": {"name": "The Red Wastes", "creatures": {
        "Razormane Quilboar": 2, "Armored Scorpid": 1, "Durotar Prowler": 1,
        "Rustfang Hyena": 2, "Mesa Stonebiter": 1, "Sunbaked Vulture": 1,
        "Elder Mottled Boar": 1, "Old Redtooth": 0,
        "Bloodtalon Scythemaw": 0, "Southfury Crocolisk": 0}},
    "subzones": {
        "Thunder Ridge": {"name": "Thunder Ridge", "creatures": {
            "Thunder Lizard": 2, "Crackling Thunderhide": 1, "Static Hatchling": 2,
            "Ridge Stormbinder": 1, "Rumblejaw": 0, "Stormhide Patriarch": 0}},
        "Rocktusk Farm": {"name": "Rocktusk Farm", "creatures": {
            "Razormane Battleguard": 2, "Rocktusk Farmhand": 2, "Tamed Razorback": 2,
            "Razormane Scout": 1, "Razormane Geomancer": 1, "Matron Sowbelly": 0}},
        "Kolkar Crag": {"name": "Kolkar Crag", "creatures": {
            "Kolkar Warrider": 2, "Kolkar Outrunner": 1, "Kolkar Wrangler": 1,
            "Kolkar Pack Runner": 1, "Kolkar Windchaser": 1,
            "Bloodhoof the Lamed": 0, "Warlord Krellian": 0}},
        "Scuttle Coast": {"name": "Scuttle Coast", "creatures": {
            "Coastal Murloc": 2, "Murloc Tidehunter": 1, "Murloc Oracle": 1,
            "Murloc Netcaster": 1, "Saltcrust Crab": 2, "Drowned Deckhand": 1,
            "Gillfin the Net-Cutter": 0}},
        "Skull Rock Approach": {"name": "Skull Rock Approach", "creatures": {
            "Searing Blade Scout": 2, "Searing Blade Raider": 1, "Burning Blade Torchbearer": 1,
            "Cinder Imp": 2, "Coastal Harpy": 1, "Houndmaster Kraygh": 0}},
    },
}


def main():
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text())
    cr = data["creatures"]
    for n, d in NEW_CREATURES.items():
        cr[n] = d
    for n, (lo, hi) in LEVEL_PATCH.items():
        cr[n]["level_range"] = [lo, hi]
    for n, lv in BOSS_LEVEL_PATCH.items():
        cr[n]["level_range"] = [lv, lv]
    p.write_text(json.dumps(data, indent=2) + "\n")

    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text())
    z = data["zones"]["Durotar"]
    z["open_zone"] = ENCOUNTERS["open_zone"]
    z["subzones"] = ENCOUNTERS["subzones"]
    p.write_text(json.dumps(data, indent=2) + "\n")

    out = {"_notes": "Durotar open-world named-rare + boss loot (2026-10-21). One item drops per "
                     "kill from the creature's pool. Numbers from the real loot formulas "
                     "(tools/build_durotar_content.py); ilvl>=10 so secondary stats are allowed."}
    out.update(pools())
    (ROOT / "data/loot/durotar_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n_items = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, level patches {len(LEVEL_PATCH)+len(BOSS_LEVEL_PATCH)}, "
          f"loot pools {len(out)-1}, items {n_items}")


if __name__ == "__main__":
    main()
