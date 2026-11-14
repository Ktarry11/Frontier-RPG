#!/usr/bin/env python3
"""Durotar cave content pass (2026-10-21).

Creatures, per-cave encounter tables and hand-crafted boss loot pools for the six
hand-built Durotar caves (tools/handbuilt_durotar_caves.py).

 * One item drops per boss kill, drawn from a pool of 4.
 * item_level = boss level + 3; ilvl >= 10 so primary + secondary stats.
 * Pools are spread across archetypes so every one of the original 9 + 21 CoA
   classes has something to chase somewhere in the Durotar cave set.

Run:  python3 tools/build_durotar_cave_content.py && python3 tools/generate_creatures.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_durotar_content import make, C  # noqa: E402

# ----------------------------------------------------------------------
# CREATURES
# ----------------------------------------------------------------------
NEW_CREATURES = {
    # Dustwind Cave
    "Burrow Stalker": C("vermin_sneaky", 5, 8, "burrow_stalker"),
    "Hive Carapace Guard": C("vermin_sneaky", 6, 8, "hive_carapace_guard"),
    # Tiragarde Keep
    "Stranded Cannoneer": C("humanoid_ranged", 5, 8, "stranded_cannoneer"),
    "Ship's Surgeon": C("humanoid_caster", 5, 8, "ships_surgeon"),
    # Drygulch Ravine
    "Dustwind Roost Warden": C("beast_fast", 8, 11, "roost_warden"),
    "Dustwind Gale-Caller": C("humanoid_caster", 8, 11, "gale_caller"),
    # Thunder Ridge (cave)
    "Thunderbrood Guardian": C("beast_large", 10, 12, "thunderbrood_guardian"),
    "Thunder Broodmother": C("beast_large", 13, 13, "thunder_broodmother", True, 2.2),
    # Sunken Grotto
    "Naga Coralspeaker": C("humanoid_caster", 10, 12, "naga_coralspeaker"),
    "Drowned Buccaneer": C("undead_basic", 9, 12, "drowned_buccaneer"),
}

CAVES = {
    "Dustwind Cave": {"name": "Dustwind Cave", "creatures": {
        "Cave Scorpid": 2, "Sand Skitterling": 2, "Burrow Stalker": 1,
        "Hive Carapace Guard": 1, "Gorge the Corpsegrinder": 0}},
    "Tiragarde Keep": {"name": "Tiragarde Keep", "creatures": {
        "Stranded Marine": 2, "Stranded Deckhand": 1, "Kul Tiras Sharpshooter": 1,
        "Stranded Cannoneer": 1, "Ship's Surgeon": 1, "Captain Thalenvorde": 0}},
    "Skull Rock": {"name": "Skull Rock", "creatures": {
        "Searing Blade Enforcer": 2, "Searing Blade Warlock": 1, "Felhound": 1,
        "Burning Blade Torchbearer": 1, "Cinder Imp": 2,
        "Neru Fireblade": 0, "Gazz'uz": 0}},
    "Drygulch Ravine": {"name": "Drygulch Ravine", "creatures": {
        "Dustwind Harpy": 2, "Dustwind Savage": 1, "Dustwind Storm-Witch": 1,
        "Dustwind Roost Warden": 1, "Dustwind Gale-Caller": 1, "Matriarch Vess'ra": 0}},
    "Thunder Ridge": {"name": "Thunder Ridge", "creatures": {
        "Thunder Lizard": 2, "Crackling Thunderhide": 1, "Static Hatchling": 2,
        "Ridge Stormbinder": 1, "Thunderbrood Guardian": 1, "Thunder Broodmother": 0}},
    "Sunken Grotto of the Deep": {"name": "Sunken Grotto of the Deep", "creatures": {
        "Naga Myrmidon": 2, "Naga Siren": 2, "Naga Coralspeaker": 1,
        "Drowned Buccaneer": 1, "Drowned Deckhand": 1, "Saltcrust Crab": 1,
        "Giant Crab": 0, "Undead Pirate Captain": 0, "Naga Shrine Guardian": 0}},
}

# ----------------------------------------------------------------------
# LOOT POOLS  (boss level -> ilvl = level + 3)
# ----------------------------------------------------------------------
def pools():
    P = {}
    # Dustwind Cave - Gorge the Corpsegrinder (L8 -> 11): 2H bruiser / plate tank / healer / rogue
    P["Gorge the Corpsegrinder"] = [
        make("Corpsegrinder's Jaw-Maul", "main_hand", "of the Bear", 11,
             "Two scorpid mandibles lashed to a haft. It still tries to close.",
             weapon_type="mace_2h"),
        make("Chitin-Plate Pauldrons", "shoulder", "of the Defender", 11,
             "Overlapping carapace plates. Heavy, ugly, and very hard to bite through.",
             armor_type="plate"),
        make("Burrowmother's Silkwrap", "wrist", "of the Restorer", 11,
             "Spun in the dark by something that cared about its brood. Soft as breath.",
             armor_type="cloth"),
        make("Venom-Barb Stiletto", "main_hand", "of the Assassin", 11,
             "A stinger the length of your forearm, cured and hilted. Handle with care.",
             weapon_type="dagger"),
    ]
    # Tiragarde Keep - Captain Thalenvorde (L8 -> 11): duelist / mail dps / ranged / tank ring
    P["Captain Thalenvorde"] = [
        make("Thalenvorde's Officer Cutlass", "main_hand", "of the Bandit", 11,
             "Kul Tiras steel, kept sharp long after there was anyone to salute.",
             weapon_type="sword_1h"),
        make("Garrison Sea-Coat", "chest", "of the Hunt", 11,
             "Salt-stiffened mail under a blue coat that has seen better tides.",
             armor_type="mail"),
        make("Stormwrecked Flintlock", "ranged", "of the Marksman", 11,
             "Powder long dried out, but the lock still clicks like a promise.",
             weapon_type="gun"),
        make("Captain's Signet of the Tide", "ring", "of the Bastion", 11,
             "Press it to wax and a garrison answers. Nobody is left to hear it."),
    ]
    # Skull Rock - Neru Fireblade (L11 -> 14): wand caster / leather agi / plate dps / fist
    P["Neru Fireblade"] = [
        make("Neru's Ember Wand", "ranged", "of Fiery Wrath", 14,
             "A blade-spirit's last candle, whittled thin. It sputters when he's near.",
             weapon_type="wand"),
        make("Cowl of Burning Oaths", "head", "of the Tiger", 14,
             "Leather scorched at the brow where the oath was branded in.",
             armor_type="leather"),
        make("Fireblade's Warkilt", "legs", "of the Champion", 14,
             "Plate skirting heat-blued like a smith's apron. Warm to the touch.",
             armor_type="plate"),
        make("Ashen Rending-Claws", "main_hand", "of the Gladiator", 14,
             "Fist-blades quenched in cinders. They leave brands, not cuts.",
             weapon_type="fist_weapon"),
    ]
    # Skull Rock - Gazz'uz (L11 -> 14): shadow staff / cloth shoulder / druid-healer leather / pendant
    P["Gazz'uz"] = [
        make("Shadowhoof Staff", "main_hand", "of Shadow Wrath", 14,
             "Cloven-hoof finial. Its owner stopped being polite a long time ago.",
             weapon_type="staff"),
        make("Mantle of Gazz'uz's Pact", "shoulder", "of the Necromancer", 14,
             "Felcloth stitched with a signature you wouldn't want on a contract.",
             armor_type="cloth"),
        make("Demon-Hide Girdle", "waist", "of the Restorer", 14,
             "Tanned from something that lied to you first.",
             armor_type="leather"),
        make("Binder's Pendant", "neck", "of the Spell Breaker", 14,
             "Every ward in Skull Rock was keyed to this. Now the keyhole's yours."),
    ]
    # Drygulch Ravine - Matriarch Vess'ra (L11 -> 14): cloak / bow / holy robe / mail gloves
    P["Matriarch Vess'ra"] = [
        make("Vess'ra's Stormfeather Cloak", "back", "of Nature's Wrath", 14,
             "Every feather hums. The wind in Drygulch listens to whoever wears it.",
             armor_type="cloth"),
        make("Talon-Strung Windbow", "ranged", "of the Falcon", 14,
             "Sinew from a roost-mother's wing, strung on a spine of red cane.",
             weapon_type="bow"),
        make("Matriarch's Windwoven Robes", "chest", "of the Prophet", 14,
             "Light as a thermal. It keeps the faith better than most of Drygulch's shrines.",
             armor_type="cloth"),
        make("Roost-Warden's Gauntlets", "hands", "of the Soldier", 14,
             "Mail gauntlets with talon-guards. The harpies knew exactly how a fist works.",
             armor_type="mail"),
    ]
    # Thunder Ridge - Thunder Broodmother (L13 -> 16): polearm / plate tank / totem / cloth boots
    P["Thunder Broodmother"] = [
        make("Broodmother's Stormspire", "main_hand", "of the Juggernaut", 16,
             "A shard of ridge-lightning set in a horn haft. It wants to strike twice.",
             weapon_type="polearm"),
        make("Thunderhide Hauberk", "chest", "of the Bulwark", 16,
             "Static crawls over the scales like a held breath. Nothing strikes it twice.",
             armor_type="plate"),
        make("Stormwatcher's Totem", "ranged", "of Nature's Wrath", 16,
             "Carved from the nest-stone at the heart of the ridge. Hold it and your hair lifts.",
             weapon_type="totem"),
        make("Eggshell Slippers", "feet", "of the Physician", 16,
             "Pearl-white shell fragments, lined with down. The Broodmother does not take loss gently.",
             armor_type="cloth"),
    ]
    # Sunken Grotto - Giant Crab (L13 -> 16): shield / plate boots / dps trinket / 2H
    P["Giant Crab"] = [
        make("Cracked Pincer Shield", "off_hand", "of the Bulwark", 16,
             "Still twitching, somehow.", weapon_type="shield"),
        make("Barnacled Greatboots", "feet", "of the Defender", 16,
             "Waterlogged, but they'll outlast you.", armor_type="plate"),
        make("Crab-Shell Talisman", "trinket", "of the Tiger", 16,
             "Warm to the touch, even now."),
        make("Claw-Cleaver of the Deep", "main_hand", "of Striking", 16,
             "One pincer, ground to an edge by a century of tide.",
             weapon_type="axe_2h"),
    ]
    # Sunken Grotto - Undead Pirate Captain (L13 -> 16): cutlass / leather head / mail healer / ring
    P["Undead Pirate Captain"] = [
        make("Drowned Captain's Cutlass", "main_hand", "of the Assassin", 16,
             "Still tastes of brine and mutiny.", weapon_type="sword_1h"),
        make("Tricorn of the Drowned", "head", "of the Monkey", 16,
             "The feather never dries.", armor_type="leather"),
        make("Sunken Officer's Vestment", "chest", "of the Seer", 16,
             "Rank insignia, barnacle-crusted but legible.", armor_type="mail"),
        make("Gold-Rotted Signet", "ring", "of the Sorcerer", 16,
             "He was buried with it. He did not stay buried."),
    ]
    # Sunken Grotto - Naga Shrine Guardian (L13 -> 16): polearm / ritual dagger / plate hands / bracers
    P["Naga Shrine Guardian"] = [
        make("Tidebound Trident", "main_hand", "of the Champion", 16,
             "The shrine's own weapon, still humming with tidal current.",
             weapon_type="polearm"),
        make("Naga Ritual Dagger", "main_hand", "of the Archmage", 16,
             "Etched with tidal runes no living tongue can read.",
             weapon_type="dagger"),
        make("Guardian's Warplate Gauntlets", "hands", "of the Warder", 16,
             "Forged to grip a trident that no longer needs gripping.",
             armor_type="plate"),
        make("Shrine-Blessed Bracers", "wrist", "of the Hierophant", 16,
             "The naga's shrine still answers to a new wearer.",
             armor_type="leather"),
    ]
    return P


def main():
    p = ROOT / "data/creatures/creatures.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["creatures"].update(NEW_CREATURES)
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    p = ROOT / "data/creatures/encounters.json"
    data = json.loads(p.read_text(encoding="utf-8"))
    data["zones"]["Durotar"]["caves"] = CAVES
    p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    out = {"_notes": "Durotar cave boss loot (2026-10-21). One item drops per kill from the "
                     "boss's pool of 4. item_level = boss level + 3; real loot formulas "
                     "(tools/build_durotar_content.make), primary + secondary stats."}
    out.update(pools())
    (ROOT / "data/loot/durotar_cave_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    # Grotto pool now lives in the cave file; drop the old ilvl-13 file so the
    # bosses aren't defined twice.
    old = ROOT / "data/loot/sunken_grotto_boss_loot.json"
    if old.exists():
        old.unlink()
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, caves {len(CAVES)}, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
