"""
Valley of Trials cluster content pass (2026-10-21): creatures, encounter
tables and hand-crafted boss/rare loot for Valley of Trials, The Den and
Burning Blade Coven.  Idempotent - safe to re-run.

  python3 tools/monster_kits.py is the source of truth for ability kits
  (run tools/generate_creatures.py after editing it).  This script owns:
    * data/creatures/creatures.json   (new creatures + fixes)
    * data/creatures/encounters.json  (Valley of Trials zone entry)
    * data/loot/valley_of_trials_boss_loot.json  (boss + named-rare pools)

LOOT RULES FOLLOWED (real game rules, not guesses)
  * ONE item drops per kill, drawn from the boss's pool (entities/boss_loot.py).
  * Stat numbers use the real formulas in entities/loot_generator.py
    (STAT_BUDGET_BASE_MULT 0.36, rare 1.7x, slot weight tiers, stat costs).
  * Below item level 10 the game only allows PRIMARY-stat suffixes (no spell
    power / healing power / ratings / mp5) - see LootGenerator.LOW_LEVEL_STAT_CAP.
    Every VoT item respects that; wide class coverage comes from armour type,
    slot, weapon type and primary-stat mix (Str/Agi/Int/Stam/Spirit and every
    "of the <Animal>" blend).  Healing-power guns, spell-power 2H weapons etc.
    start in the 10+ zones.
  * item_level = boss/rare level + 3 ("dungeon loot slightly above normal").
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
# item builder - real formulas, deterministic
# ----------------------------------------------------------------------
def _stats(suffix, budget):
    assert suffix in LG.gear_suffixes, suffix
    prim, sec = {}, {}
    for stat, w in LG.gear_suffixes[suffix]["stats"].items():
        assert stat in PRIMARY, f"{suffix}: {stat} is not allowed below ilvl 10"
        v = round(budget * w / LG.stat_budget_costs.get(stat, 1.0))
        if v > 0:
            prim[stat] = v
    return prim, sec


def make(name, slot, suffix, ilvl, flavor, armor_type=None, weapon_type=None,
         req=None, rarity="rare"):
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
        # RELICS AND HELD OFF-HANDS ARE STAT STICKS, no auto-attack damage -
        # the same rule LootGenerator.generate_weapon applies. Only `shield`
        # short-circuited above, so every hand-authored Totem and Tome in the
        # game came out WITH weapon damage (8 totems at 20-85, a tome at
        # 72-98) while procedurally generated ones correctly had none. Keyed
        # on the type's own relic/non_weapon flags so Libram and Idol are
        # covered without anyone having to remember this line.
        if wt.get("relic") or wt.get("non_weapon"):
            return d
        tier = wt.get("damage_tier", "one_hand")
        mult = LG.weapon_types["damage_tiers"][tier]["dps_multiplier"]
        # Early boss two-handers only get a small premium over a one-hander: at the global 1.8x the
        # Husk-Cracker Maul hit ~65 per swing at level 5 (2.3x a starter weapon) and trivialised the Den boss.
        mult = min(mult, 1.1) if tier == "two_hand" else mult
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
# LOOT POOLS  (boss -> list of items, ONE drops per kill)
# ----------------------------------------------------------------------
def pools():
    P = {}
    # ---- The Den: Nest Guardian (L5 -> ilvl 8): tank / hybrid 2H / healer cloth / agi leather
    P["Nest Guardian"] = [
        make("Skitterhorn Bulwark", "off_hand", "of Stamina", 8,
             "A guardian's own horn-plate, split and riveted into a shield.",
             weapon_type="shield", req=5),
        make("Husk-Cracker Maul", "main_hand", "of the Gorilla", 8,
             "Built to crack chitin. It has opinions about anything else.",
             weapon_type="mace_2h", req=5),
        make("Silkweave Hood of the Den", "head", "of the Owl", 8,
             "Spun from the nest's own silk. Thread by thread it hums when you speak a kind word.",
             armor_type="cloth", req=5),
        make("Egg-Warden's Treads", "feet", "of the Monkey", 8,
             "Quiet, light and sticky in all the right places.",
             armor_type="leather", req=5),
    ]
    # ---- Burning Blade Coven: Yarrog Baneshadow (L5 -> ilvl 8): caster / agi-int / plate / wand
    P["Yarrog Baneshadow"] = [
        make("Fel-Stitched Vestments", "chest", "of the Eagle", 8,
             "The stitching is in a language you do not want to learn.",
             armor_type="cloth", req=5),
        make("Coven Ritual Dagger", "main_hand", "of the Falcon", 8,
             "Blessed, cursed and sharpened - in that order.",
             weapon_type="dagger", req=5),
        make("Fel-Iron Gauntlets", "hands", "of the Bear", 8,
             "Still warm. Please stop asking why.",
             armor_type="plate", req=5),
        make("Soul-Siphon Hexwand", "ranged", "of the Eagle", 8,
             "Yarrog never noticed it was draining him back.",
             weapon_type="wand", req=5),
    ]
    # ---- Scorpid Nest named rare: Broodmother Sarrix (L5 -> ilvl 8)
    P["Broodmother Sarrix"] = [
        make("Venom-Barbed Shortbow", "ranged", "of the Monkey", 8,
             "Every arrow is dipped before the string is drawn. It never dries.",
             weapon_type="bow", req=5),
        make("Brood-Silk Mantle", "shoulder", "of the Falcon", 8,
             "Egg-silk, tightly woven. Faintly sticky, always.",
             armor_type="mail", req=5),
        make("Egg-Mother's Locket", "neck", "of the Whale", 8,
             "The eggs inside never hatch. Nobody has checked why.",
             req=5),
    ]
    # ---- Sagebrush Flat rare: Old Tusk (L3 -> ilvl 6)
    P["Old Tusk"] = [
        make("Tusk-Tipped Spear", "main_hand", "of the Tiger", 6,
             "Old Tusk's last gift to a hunter who finally got close enough.",
             weapon_type="polearm", req=3),
        make("Boarhide Jerkin", "chest", "of the Bear", 6,
             "Thick enough to turn a tusk. It's been tested.",
             armor_type="leather", req=3),
        make("Broken Tusk Signet", "ring", "of Strength", 6,
             "A ring carved from the tusk that finally broke.",
             req=3),
    ]
    # ---- Trailwater Spring rare: Old Gulpjaw (L4 -> ilvl 7)
    P["Old Gulpjaw"] = [
        make("Gulpjaw's Slimecloak", "back", "of the Whale", 7,
             "It repels water. It also repels everyone at the campfire.",
             armor_type="accessory", req=4),
        make("Toadskin Gloves", "hands", "of the Owl", 7,
             "Supple, damp and strangely comforting.",
             armor_type="cloth", req=4),
        make("Reedwoven Band", "ring", "of the Eagle", 7,
             "Spring reeds braided around a river stone.",
             req=4),
    ]
    # ---- Sagewood Grove rare: Bramblethorn the Ancient (L5 -> ilvl 8)
    P["Bramblethorn the Ancient"] = [
        make("Heartwood Staff", "main_hand", "of the Owl", 8,
             "It grew this way. You are fairly certain it is listening.",
             weapon_type="staff", req=5),
        make("Sapbound Bracers", "wrist", "of the Wolf", 8,
             "Living bark that tightens when you run.",
             armor_type="leather", req=5),
        make("Sagewood Heart-Amulet", "neck", "of Spirit", 8,
             "Smells like rain on warm stone.",
             req=5),
    ]
    # ---- Windrift Dunes rare: Sandfang (L5 -> ilvl 8)
    P["Sandfang"] = [
        make("Sandfang's Pelt Mantle", "shoulder", "of the Tiger", 8,
             "Sun-bleached and quick to remember the hunt.",
             armor_type="leather", req=5),
        make("Dunestalker's Crossbow", "ranged", "of Agility", 8,
             "Built to bring down something faster than you.",
             weapon_type="crossbow", req=5),
        make("Windrift Sash", "waist", "of the Monkey", 8,
             "Woven from dune-grass and good intentions.",
             armor_type="mail", req=5),
    ]
    # ---- Cinderjaw Wastes rare: Smolderhide (L6 -> ilvl 9)
    P["Smolderhide"] = [
        make("Ashen Smolder-Mace", "main_hand", "of the Eagle", 9,
             "Cooler than it looks. Warmer than it should be.",
             weapon_type="mace_1h", req=6),
        make("Cinderscale Legguards", "legs", "of the Bear", 9,
             "Scales of a very patient basilisk. It has stopped being patient.",
             armor_type="plate", req=6),
        make("Ember-Etched Ring", "ring", "of Intellect", 9,
             "The ember inside never quite goes out.",
             req=6),
    ]
    return P


# ----------------------------------------------------------------------
# CREATURES
# ----------------------------------------------------------------------
NEW_CREATURES = {
    # open valley
    "Dustwind Jackal": {"template": "beast_fast", "level_range": [1, 4], "is_boss": False, "ability_kit": "dustwind_jackal"},
    "Carrion Vulture": {"template": "beast_fast", "level_range": [2, 5], "is_boss": False, "ability_kit": "carrion_vulture"},
    # scorpid nest
    "Sandpincer Crawler": {"template": "vermin_sneaky", "level_range": [3, 5], "is_boss": False, "ability_kit": "sandpincer_crawler"},
    # trailwater spring
    "Marsh Skimmer": {"template": "vermin_swarm", "level_range": [1, 3], "is_boss": False, "ability_kit": "marsh_skimmer"},
    # sagewood grove
    "Thornroot Sapling": {"template": "elemental_bruiser", "level_range": [3, 5], "is_boss": False, "ability_kit": "thornroot_sapling"},
    # windrift dunes
    "Dust Devil": {"template": "elemental_caster", "level_range": [4, 6], "is_boss": False, "ability_kit": "dust_devil"},
    # cinderjaw wastes
    "Ember Wisp": {"template": "elemental_caster", "level_range": [4, 6], "is_boss": False, "ability_kit": "ember_wisp"},
    # the den
    "Den Webspinner": {"template": "vermin_swarm", "level_range": [2, 4], "is_boss": False, "ability_kit": "den_spinner"},
    "Husk Crawler": {"template": "vermin_sneaky", "level_range": [3, 5], "is_boss": False, "ability_kit": "husk_crawler"},
    "Egg Tender": {"template": "vermin_sneaky", "level_range": [3, 5], "is_boss": False, "ability_kit": "egg_tender"},
    # burning blade coven
    "Burning Blade Acolyte": {"template": "humanoid_caster", "level_range": [4, 5], "is_boss": False, "ability_kit": "burning_blade_acolyte"},
    "Coven Ritual Guard": {"template": "humanoid_warrior", "level_range": [4, 5], "is_boss": False, "ability_kit": "coven_ritual_guard"},
    # named rares (subzone rares roll at ~6% per encounter)
    "Old Tusk": {"template": "beast_basic", "level_range": [3, 3], "is_boss": True, "boss_multiplier": 1.8, "ability_kit": "old_tusk"},
    "Old Gulpjaw": {"template": "vermin_sneaky", "level_range": [4, 4], "is_boss": True, "boss_multiplier": 1.8, "ability_kit": "old_gulpjaw"},
    "Bramblethorn the Ancient": {"template": "elemental_bruiser", "level_range": [5, 5], "is_boss": True, "boss_multiplier": 1.4, "ability_kit": "bramblethorn_the_ancient"},
    "Sandfang": {"template": "beast_fast", "level_range": [5, 5], "is_boss": True, "boss_multiplier": 1.8, "ability_kit": "sandfang"},
    "Smolderhide": {"template": "elemental_bruiser", "level_range": [6, 6], "is_boss": True, "boss_multiplier": 1.4, "ability_kit": "smolderhide"},
}
# fixes to existing entries
CREATURE_PATCH = {
    "Fel Pup": {"ability_kit": "fel_pup", "is_boss": False},
    "Nest Guardian": {"boss_multiplier": 2.6},
}

ENCOUNTERS = {
    "open_zone": {"name": "The Valley Floor", "creatures": {
        "Mottled Boar": 3, "Scorpid Worker": 1, "Dustwind Jackal": 2, "Carrion Vulture": 1}},
    "subzones": {
        "Sagebrush Flat": {"name": "Sagebrush Flat", "creatures": {
            "Mottled Boar": 3, "Dustwind Jackal": 2, "Old Tusk": 0}},
        "Scorpid Nest": {"name": "The Scorpid Nest", "creatures": {
            "Scorpid Worker": 3, "Venomtail Scorpid": 2, "Sandpincer Crawler": 2, "Broodmother Sarrix": 0}},
        "Trailwater Spring": {"name": "Trailwater Spring", "creatures": {
            "Trailwater Toad": 3, "Marsh Skimmer": 3, "Scorpid Worker": 1, "Old Gulpjaw": 0}},
        "Sagewood Grove": {"name": "Sagewood Grove", "creatures": {
            "Sagewood Sprite": 3, "Thornroot Sapling": 2, "Mottled Boar": 1, "Bramblethorn the Ancient": 0}},
        "Windrift Dunes": {"name": "Windrift Dunes", "creatures": {
            "Dustwind Jackal": 3, "Dust Devil": 2, "Carrion Vulture": 2, "Sandfang": 0}},
        "Cinderjaw Wastes": {"name": "Cinderjaw Wastes", "creatures": {
            "Cinderjaw Skitterling": 3, "Ashback Basilisk": 2, "Ember Wisp": 2, "Smolderhide": 0}},
    },
    "caves": {
        "The Den": {"name": "The Den", "creatures": {
            "Cave Skitterer": 3, "Den Webspinner": 3, "Husk Crawler": 2, "Egg Tender": 1, "Nest Guardian": 0}},
        "Burning Blade Coven": {"name": "Burning Blade Coven", "creatures": {
            "Burning Blade Initiate": 3, "Vile Familiar": 3, "Felstalker Whelp": 2, "Fel Pup": 2,
            "Burning Blade Acolyte": 1, "Coven Ritual Guard": 1, "Yarrog Baneshadow": 0}},
    },
}


def main():
    # creatures
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text())
    cr = data["creatures"]
    for n, d in NEW_CREATURES.items():
        cr[n] = d
    for n, patch in CREATURE_PATCH.items():
        cr[n].update(patch)
    p.write_text(json.dumps(data, indent=2) + "\n")

    # encounters
    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text())
    data["zones"]["Valley of Trials"] = ENCOUNTERS
    p.write_text(json.dumps(data, indent=2) + "\n")

    # loot
    out = {"_notes": "Valley of Trials cluster boss + named-rare loot (2026-10-21). One item "
                     "drops per kill from the boss's pool. Numbers from the real loot formulas "
                     "(tools/build_vot_content.py). Primary-stat only - ilvl<10 rule."}
    out.update(pools())
    (ROOT / "data/loot/valley_of_trials_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n_items = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, loot pools {len(out)-1}, items {n_items}")


if __name__ == "__main__":
    main()
