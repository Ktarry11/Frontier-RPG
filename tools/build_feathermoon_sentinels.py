#!/usr/bin/env python3
"""The Feathermoon Sentinels: Feralas's new faction, its supply and its quartermaster's shelf. Idempotent.

    PYTHONPATH=. python3 tools/build_feathermoon_sentinels.py

Kyle, 19 Nov 2026: "Feathermoon as a new faction" (docs/feralas_brief.md). TBC-style like every faction, built on
Moonglade's shelf code (tools/build_moonglade.shelves and write_factions, run here for this one faction): friendly the
Sentinels' own supply, honored a neck piece and a pattern, revered six ilvl 67 blues and a pattern, exalted three
ilvl 73 epics and two recipes. A direction, not a cage (Kyle, 15 Nov 2026): the Sentinels lean toward hunters, rangers
and archers, and the shelf still serves tanks, healers, casters and fighters. Reputation comes from Feralas's quests
by giver (tools/build_feralas_quests.py) and, later, from Dire Maul.

The quartermaster (fm_quartermaster, tools/build_feralas_towns.py) gives and takes no quests, so she can move.
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_moonglade as BM  # noqa: E402
from tools.build_feralas_quests import SENTINELS  # noqa: E402

FID = "feathermoon_sentinels"

FACTIONS = {FID: {k: v for k, v in SENTINELS.items() if k != "rewards"}}
QM = {FID: "fm_quartermaster"}
HONORED = {FID: [("fms_feathermoon_crescent", "Feathermoon Crescent", "neck", "armor", None, "agility", 34,
                  "A silver crescent on a cord of braided hippogryph feather. Every Sentinel on the walls wears one.")]}
REVERED = {FID: [
    ("fms_huntress_jerkin", "Feathermoon Huntress Jerkin", "chest", "armor", "leather", "agility", 58,
     "Cut close for running the coast at night, and dyed the deep violet of the island's banners."),
    ("fms_moonsilk_cowl", "Sentinel's Moonsilk Cowl", "head", "armor", "cloth", "caster", 52,
     "Worn by the priestesses who keep the moonwell, with a hood deep enough to hide the face in a storm."),
    ("fms_tidewatch_greaves", "Tidewatch Greaves", "legs", "armor", "plate", "tank", 56,
     "Pale plate for the Sentinels who hold the sandbar to Sardor Isle, built to stand in the surf."),
    ("fms_owlfeather_spaulders", "Owlfeather Spaulders", "shoulder", "armor", "mail", "hunter", 52,
     "Mail trimmed with owl feathers, so a huntress can turn her head without a sound."),
    ("fms_band_of_the_island", "Band of the Island", "ring", "armor", None, "healer", 48,
     "Carved from the pale stone of Feathermoon's walls. It's said the island never lets its sisters drown."),
    ("fms_sardor_watch_bracers", "Sardor Watch Bracers", "wrist", "armor", "mail", "tide_healer", 46,
     "The healers who wade out to the sandbar wear these, so the sea can't take the tools from their hands."),
]}
EXALTED = {FID: [
    ("fms_feathermoon_greatbow", "Feathermoon Moonbolt Crossbow", "ranged", "weapon", "crossbow", "hunter_crit", 300,
     "The Sentinels on the walls of Feathermoon keep these for the long shots out over the water, where a bow "
     "can't reach."),
    ("fms_crescent_glaive", "Crescent Moonblade", "main_hand", "weapon", "sword_1h", "rogue_crit", 290,
     "A curved Sentinel blade, light enough to throw and balanced to come back to the hand that knows it."),
    ("fms_staff_of_the_watchful_moon", "Staff of the Watchful Moon", "main_hand", "weapon", "staff", "high_healer",
     310, "Kindal Moonweaver's own staff, or one cut to the same pattern. It hums when the tide turns."),
]}
EXALTED_RECIPES = {FID: [
    ("rep_fms_shadowhide_vest", "leatherworking", "Sentinel's Shadowhide Vest", "chest", "armor", "leather", "agility",
     "The Sentinels' own pattern for a night patrol, dark as the coast without a moon.", "gear_wow_chest_leather_02_1"),
    ("rep_fms_moonweavers_robe", "tailoring", "Moonweaver's Robe", "chest", "armor", "cloth", "spirit_healer",
     "Kindal Moonweaver's pattern, woven with moonsilk and blessed in the island's moonwell.",
     "gear_inv_chest_cloth_40"),
]}
SHELF_PATTERNS = {FID: [
    ("rep_fms_tidewatch_bracers", "leatherworking", "Tidewatch Bracers", "wrist", "armor", "leather", "agility",
     "Salt-cured leather that stays supple in the surf, the first thing a Feathermoon tanner learns.",
     "gear_wow_wrist_80_1", "honored"),
    ("rep_fms_island_gauntlets", "blacksmithing", "Island Plate Gauntlets", "hands", "armor", "plate", "tank",
     "Feathermoon's armoury makes these for the Sentinels who hold the gate, pale and heavy and sure.",
     "gear_wow_hands_104_2", "revered"),
]}
CONSUMABLES = {FID: ("elixirs", {
    "consumable_id": "fms_sentinel_draught", "name": "Sentinel's Draught", "consumable_type": "elixir",
    "description": ("The bitter moonberry draught the Sentinels drink before a night on the walls. +20 Agility for 30 "
                    "minutes. Battle elixir: one at a time."),
    "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": 46,
    "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 80, "buff_category": "battle",
    "stat_bonuses": {"agility": 20},
})}
HONORED_SUPPLIES = {FID: ["flask_mending"]}
#: every unique item has ONE icon (Kyle, 16 Nov 2026): the two epics' own, picked from icons nothing else uses
EPIC_ICONS = {"fms_feathermoon_greatbow": "gear_inv_weapon_crossbow_08", "fms_crescent_glaive": "gear_inv_sword_47"}


def real_ingredients():
    """The rep patterns' real ingredients, the same rungs tools/build_master_crafting.py gives every faction's: an
    Exalted epic is made of level-60 materials, the Revered blue of the first rung, the Honored pattern stays pre-60."""
    import build_faction_rewards as F
    import build_master_crafting as MC
    ids = {r[0] for r in EXALTED_RECIPES[FID] + SHELF_PATTERNS[FID]}
    n = 0
    for trade in {r[1] for r in EXALTED_RECIPES[FID] + SHELF_PATTERNS[FID]}:
        path = ROOT / "data" / MC.TRADE_FILE[trade] / "recipes.json"
        d = json.loads(path.read_text(encoding="utf-8"))
        book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        for rid in ids & set(book):
            r = book[rid]
            if not r.get("_rare_ingredients_todo"):
                continue
            out = r.get("output") or {}
            slot = out.get("slot")
            made = out.get("item") if isinstance(out.get("item"), dict) else out
            if made.get("rarity") == "epic":
                r["inputs"], r["skill_required"], out["material_tier"] = MC.scaled(MC.MATS[trade][1], slot), 320, \
                    MC.MATS[trade][3]
            elif (made.get("item_level") or 0) >= 66:
                r["inputs"], r["skill_required"], out["material_tier"] = MC.scaled(MC.MATS[trade][0], slot), 305, \
                    MC.MATS[trade][2]
            else:
                pin, ptier = F.PLACEHOLDER[trade]
                r["inputs"], r["skill_required"], out["material_tier"] = MC.scaled(dict(pin), slot), 300, ptier
            s = r["skill_required"]
            r["skill_range"] = [s + 3, s + 8, s + 13, s + 18] if s > 300 else [300, 305, 310, 315]
            del r["_rare_ingredients_todo"]
            n += 1
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return n


def main():
    for name in ("FACTIONS", "QM", "HONORED", "REVERED", "EXALTED", "EXALTED_RECIPES", "SHELF_PATTERNS", "CONSUMABLES",
                 "HONORED_SUPPLIES"):
        setattr(BM, name, copy.deepcopy(globals()[name]))
    BM.EPIC_ICONS = dict(EPIC_ICONS)
    BM.OLD_NAMES = []
    bad = []
    cd, fr, picks, docs = BM.shelves(bad)
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    fd = BM.load("data/factions/factions.json")
    BM.write_factions(fd)
    fd["factions"][FID]["rewards"]["_comment"] = [
        "Gates, not a displayed ladder (the faction panel stays information only).",
        "TBC-style shelf (tools/build_feathermoon_sentinels.py, 19 Nov 2026): friendly the Sentinels' draught, honored "
        "a neck piece and a pattern, revered six ilvl 67 blues and a pattern, exalted three ilvl 73 epics and two "
        "recipes."]
    BM.save("data/factions/factions.json", fd)
    BM.save("data/items/faction_rewards.json", fr)
    BM.save("data/items/crafted_icons.json", picks)
    BM.save("data/consumables/consumable_types.json", cd)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    swapped = real_ingredients()
    # the tabard goes back on the friendly shelf (write_factions rewrites the shelf; tools/build_tabards.py adds it)
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/build_tabards.py"), "--write"], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"The Feathermoon Sentinels: 7 blues, 3 epics, 2 recipes, 2 patterns, a supply and a tabard; "
          f"{swapped} patterns on their real ingredients")
    return 0


if __name__ == "__main__":
    sys.exit(main())
