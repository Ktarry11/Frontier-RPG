#!/usr/bin/env python3
"""The Highbough Tribes: the World Tree's faction, its supply and its quartermaster's shelf. Idempotent.

    PYTHONPATH=. python3 tools/build_highbough_tribes.py

docs/worldtree_brief.md: the trolls who climbed the tree, led by High Chieftain Zan'kaji in the Great Settlement. "The
usual TBC shelf (Friendly supplies, Honored recipes, Revered ilvl 67 blues, Exalted ilvl 73 epics and the mount)", with
a direction, never a cage (Kyle, 15 Nov 2026): the tribes lean toward hunters, shamans and shadow hunters, mail and
leather, and the shelf still serves tanks, healers, casters and fighters. Built on Moonglade's shelf code
(tools/build_moonglade.shelves and write_factions), the same way tools/build_feathermoon_sentinels.py is. Reputation
comes from the island's and the tiers' quests by giver (tools/build_rootwater_quests.py and
tools/build_lower_boughs_quests.py), which write the faction's `also` list; write_factions keeps it.

The quartermaster (gs_quartermaster, tools/build_great_settlement.py) gives and takes no quests, so she can move.

THE MOUNT isn't here yet: the Exalted mounts were drawn before the tribes existed (sheets H11 to H13), like the
Sentinels'. It needs its own sheet cell (docs/backlog_nov17_onwards.md, section 10).
"""
import copy
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_moonglade as BM  # noqa: E402
import build_feathermoon_sentinels as SEN  # noqa: E402

FID = "highbough_tribes"
QM = {FID: "gs_quartermaster"}
HONORED = {FID: [("hbt_loa_tooth_necklace", "Loa-Tooth Necklace", "neck", "armor", None, "agility", 34,
                  "A crocolisk's tooth from the lagoons, strung on braided bark fibre and painted with the tribes' "
                  "teal. Every climber wears one.")]}
REVERED = {FID: [
    ("hbt_bough_hunters_jerkin", "Bough-Hunter's Jerkin", "chest", "armor", "leather", "agility", 58,
     "Python skin over ape hide, cut for running along a branch with nothing either side of you."),
    ("hbt_rivercallers_kilt", "Rivercaller's Scaled Kilt", "legs", "armor", "mail", "tide_healer", 56,
     "Worn by the shamans who listen to the river on the Great Bough. The scales are from fish nobody can name."),
    ("hbt_treetop_spaulders", "Treetop Spaulders", "shoulder", "armor", "mail", "hunter", 52,
     "Mail trimmed with leaves that never wilt. A hunter in these disappears into the boughs."),
    ("hbt_heartwood_guard_helm", "Heartwood Guard Helm", "head", "armor", "plate", "tank", 56,
     "The Settlement's gatewardens wear these, plate lined with heartwood that's harder than the iron over it."),
    ("hbt_loa_speakers_cuffs", "Loa-Speaker's Cuffs", "wrist", "armor", "cloth", "caster", 46,
     "Woven in the loa temple from Silkwood silk, and blessed with a drop of sap from the tree's heart."),
    ("hbt_band_of_the_high_chieftain", "Band of the High Chieftain", "ring", "armor", None, "strength_crit", 48,
     "Zan'kaji gives these to the ones he trusts with the bridges. It's carved from a single knot of the tree."),
]}
EXALTED = {FID: [
    ("hbt_treetop_longbow", "Treetop Longbow", "ranged", "weapon", "bow", "hunter_crit", 300,
     "Strung with Silkwood silk and carved from a branch the tree let fall. It shoots farther than it should, the "
     "way everything from the tree grows bigger than it should."),
    ("hbt_bough_breaker_greataxe", "Bough-Breaker Greataxe", "main_hand", "weapon", "axe_2h", "strength", 320,
     "A troll war-axe with a haft of heartwood, made for the Highbough's champions and never once used on the tree."),
    ("hbt_shadow_hunters_fetish", "Shadow Hunter's Fetish", "off_hand", "weapon", "tome", "caster", 280,
     "A bundle of bone, feather and painted bark that the shadow hunters of the Settlement carry into the dark."),
]}
EXALTED_RECIPES = {FID: [
    ("rep_hbt_pythonscale_hauberk", "leatherworking", "Pythonscale Hauberk", "chest", "armor", "mail", "hunter",
     "The tribes' own pattern: Bough Python scales laid over mail, gold-green and supple as a living snake.",
     "gear_wow_chest_chain_12"),
    ("rep_hbt_spiritweave_vestments", "tailoring", "Highbough Spiritweave Vestments", "chest", "armor", "cloth",
     "spirit_healer", "Woven by the loa-speakers from Silkwood silk, for the healers who climb with the hunters.",
     "gear_wow_chest_mail_03"),
]}
SHELF_PATTERNS = {FID: [
    ("rep_hbt_climbers_bracers", "leatherworking", "Climber's Grip Bracers", "wrist", "armor", "leather", "agility",
     "The first thing a Highbough tanner learns: bracers that grip the bark when your hands can't.",
     "gear_epic_shoulder_leather_1", "honored"),
    ("rep_hbt_lantern_ward_gauntlets", "blacksmithing", "Lantern Ward Gauntlets", "hands", "armor", "plate", "tank",
     "Made at the Settlement's forge for the wardens of the Lantern Ward, heavy enough to hold a rope bridge.",
     "gear_epic_shoulder_mail_1", "revered"),
]}
CONSUMABLES = {FID: ("elixirs", {
    "consumable_id": "hbt_heartsap_tonic", "name": "Heartsap Tonic", "consumable_type": "elixir",
    "description": ("Sap from the tree's heart cut with Khadgar's Whisker, the way Sapwatcher Uzo makes it, so it "
                    "heals without making you grow. +20 Stamina for 30 minutes. Guardian elixir: one at a time."),
    "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": 44,
    "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 80, "buff_category": "guardian",
    "stat_bonuses": {"stamina": 20},
})}
HONORED_SUPPLIES = {FID: ["flask_mending"]}
#: every unique item has ONE icon (Kyle, 16 Nov 2026): the epics' own, picked from icons nothing else uses
EPIC_ICONS = {"hbt_bough_breaker_greataxe": "gear_inv_axe_11"}
COLOURS = ((30, 120, 120), (200, 70, 40))       # teal and red: the tribes' colours, for the tabard


def faction_base():
    fd = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))
    rec = copy.deepcopy(fd["factions"][FID])
    rec.pop("rewards", None)
    rec["leader"]["npc_id"] = "gs_zankaji"
    rec["leader"]["location"] = "The Heart Palace, on the Chieftain's Rise in the Great Settlement"
    qr = rec.setdefault("quest_rep", {})
    qr["_comment"] = ("Per quest, paid by giver (tools/build_rootwater_quests.py, tools/build_lower_boughs_quests.py, "
                      "tools/build_great_settlement_quests.py, tools/build_middle_boughs_quests.py, "
                      "tools/build_upper_boughs_quests.py).")
    qr["zones"] = ["rootwater_isle", "lower_boughs", "knothollow", "great_settlement", "middle_boughs", "shriekhollow",
                   "upper_boughs", "stormsplit"]
    return rec


def real_ingredients():
    """The rep patterns on their real ingredients, the Sentinels' way (tools/build_feathermoon_sentinels)."""
    for name in ("EXALTED_RECIPES", "SHELF_PATTERNS"):
        setattr(SEN, name, {SEN.FID: globals()[name][FID]})
    return SEN.real_ingredients()


def tabard_colours():
    p = ROOT / "tools/build_tabards.py"
    s = p.read_text(encoding="utf-8")
    if f'"{FID}"' in s:
        return
    a = '    "feathermoon_sentinels": ((80, 55, 140), (205, 205, 225)),\n'
    assert a in s
    p.write_text(s.replace(a, a + f'    "{FID}": {COLOURS!r},\n'), encoding="utf-8")


def main():
    BM.FACTIONS = {FID: faction_base()}
    for name in ("QM", "HONORED", "REVERED", "EXALTED", "EXALTED_RECIPES", "SHELF_PATTERNS", "CONSUMABLES",
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
        "TBC-style shelf (tools/build_highbough_tribes.py, 20 Nov 2026): friendly the tribes' Heartsap Tonic, honored "
        "a neck piece and a pattern, revered six ilvl 67 blues and a pattern, exalted three ilvl 73 epics and two "
        "recipes. The Exalted mount waits for its art."]
    BM.save("data/factions/factions.json", fd)
    BM.save("data/items/faction_rewards.json", fr)
    BM.save("data/items/crafted_icons.json", picks)
    BM.save("data/consumables/consumable_types.json", cd)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    swapped = real_ingredients()
    tabard_colours()
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/build_tabards.py"), "--write"], check=True,
                   stdout=subprocess.DEVNULL)
    print(f"The Highbough Tribes: 7 blues, 3 epics, 2 recipes, 2 patterns, a supply and a tabard; "
          f"{swapped} patterns on their real ingredients")
    return 0


if __name__ == "__main__":
    sys.exit(main())
