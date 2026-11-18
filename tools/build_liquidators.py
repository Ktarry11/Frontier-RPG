#!/usr/bin/env python3
"""The Liquidators: the faction, its quartermaster's shelf, and its two camp supplies. Idempotent.

    PYTHONPATH=. python3 tools/build_liquidators.py

docs/deadwind_brief.md and docs/deadwind_quest_plan.md. Kyle, 18 Nov 2026: "the liquidators get their own faction",
with a shelf like the Sunreach Conclave's. They're the Earth transplants who hold Ariden's Watch against the fallout
in Deadwind Pass, beside the Forsaken apothecaries.

THE REPUTATION
  * The Watch's quests pay it, by giver (tools/build_deadwind_quests.py).
  * Every mutated thing in the pass's open world: 10 a kill, to Honored.
  * The Exclusion Zone: 75 a boss, and its trash 10 a kill to Revered (the dungeon is how you get past Honored).
THE SHELF, TBC-style like every other faction (tools/build_faction_rewards.author_unique() and the crafted gear's
author(), neither of those scripts re-run):
  * friendly: the camp's two supplies, made here. Iodine Tincture is the Earth habit: in 1986 the people near
    Chernobyl were given potassium iodide so their thyroids would fill up with clean iodine before the fallout's could
    get in. Seep-Washed Bandages are what the infirmary rolls by the hundred.
  * honored: the Liquidator's Dosimeter, a neck piece anyone can wear (the plan said a tabard; the game has no tabard
    slot, and the dosimeter is the thing every liquidator actually carries), the camp's flask, and a tailoring
    pattern (Quarantine Wraps); revered adds a leatherworking one (Wireline Gloves)
  * revered: six ilvl 67 blues, every armour type and role
  * exalted: three ilvl 73 epics and two recipes (tailoring and leatherworking, the trades that make the suits)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build_faction_rewards as BFR  # noqa: E402

FID = "the_liquidators"
WATCH = "ariden_watch"
QM = "dw_quartermaster"

FACTION = {
    "name": "The Liquidators",
    "description": ("Earth transplants who've lived beside a fallout zone, or cleaned one up, holding the line in "
                    "Deadwind Pass with the Forsaken apothecaries."),
    "home_zone": WATCH,
    "home_name": "Ariden's Watch, in Deadwind Pass",
    "leader": {
        "title": "Chief Liquidator",
        "name": "Halyna Bondar",
        "npc_id": "dw_halyna",
        "location": "The command house, Ariden's Watch",
        "line": ("My father was a liquidator at Chernobyl in 1986. He came home, and he didn't talk about it, and "
                 "he kept his dosimeter on the kitchen shelf for the rest of his life. I know why now."),
    },
    "_lore_note": "Kyle, 18 Nov 2026: 'the liquidators get their own faction'.",
    "lore": [
        "When the worlds came together, the leylines under Deadwind Pass tore open, and the fallout came out of the "
        "tear. The Forsaken call it the Seep. The transplants who'd seen something like it before call it what it is.",
        "They came from Slavutych and Fukushima, from the farms under Windscale, from Semey beside the Polygon, from "
        "Rongelap and Goiania and Hanford and St. George, Utah. They came on purpose, and they took the word their "
        "parents' generation used for the people who went into Chernobyl: liquidators.",
        "They hold Ariden's Watch with the Forsaken apothecaries, who can walk where the living can't. Everyone "
        "scrubs at the troughs, everyone carries a dosimeter, and every name goes on the board by the pyre.",
        "The Undercity supplies them. Nobody commands them, which is why the Forsaken let them stay.",
    ],
    "quest_rep": {
        "_comment": "Per quest, by shape. Paid by giver (tools/build_deadwind_quests.FACTION_BY_GIVER).",
        "default": 325,
        "boss": 350,
        "capstones": {},
        "zones": [],
    },
}

#: (id, name, slot, kind, type, identity, price in gold, flavour)
HONORED = [
    ("liq_liquidators_dosimeter", "Liquidator's Dosimeter", "neck", "armor", None, "tank_any", 40,
     "Kenji builds them out of Seep-glass and cat gut. It clicks faster when you're somewhere you shouldn't be, which "
     "in Deadwind is most places."),
]
REVERED = [
    ("liq_decon_suit_robe", "Decontamination Suit", "chest", "armor", "cloth", "caster", 66,
     "Oilcloth over silk, sealed at every seam with wax. The Forsaken think the living wear far too many layers."),
    ("liq_pyre_tenders_gauntlets", "Pyre-Tender's Gauntlets", "hands", "armor", "plate", "plate_healer", 60,
     "Old Tobiah's spare pair. He says the green fire doesn't burn plate, only the hands inside it."),
    ("liq_wireline_boots", "Wireline Boots", "feet", "armor", "leather", "agility", 58,
     "Corporal Delgado's patrols wear through a pair a week walking the fence."),
    ("liq_sample_runners_hauberk", "Sample-Runner's Hauberk", "chest", "armor", "mail", "tide_healer", 68,
     "Mail for the runners who carry Morwen's samples back across the pass, washed at the troughs every time."),
    ("liq_quarantine_wardens_girdle", "Quarantine Warden's Girdle", "waist", "armor", "plate", "tank", 52,
     "Deathguard Harrow's own design, with a hook for the gate key and another for the ledger."),
    ("liq_board_of_names_band", "Band of the Board", "ring", "armor", None, "caster_crit", 55,
     "Every name on the board by the pyre is scratched inside it, very small, and there's room for more."),
]
EXALTED = [
    ("liq_staff_of_the_long_shift", "Staff of the Long Shift", "main_hand", "weapon", "staff", "high_healer", 300,
     "Cut from a dead Deadwind oak and capped with Seep-glass. It glows when the wound is close, so you'll know."),
    ("liq_liquidators_shovel", "The Liquidator's Spade", "main_hand", "weapon", "axe_2h", "strength_crit", 320,
     "The men on the reactor roof cleared the graphite with spades, ninety seconds at a time. This one's for the pass."),
    ("liq_fence_runners_knife", "Fence-Runner's Knife", "main_hand", "weapon", "dagger", "rogue_crit", 290,
     "Ray Delgado's, from before he came over. He won't say what he used it for in Utah, only that it was legal."),
]
#: (id, trade, name, slot, kind, type, identity, flavour, icon): the icon is the pack's, for no crafted epic shares one
EXALTED_RECIPES = [
    ("rep_liq_hazard_suit", "tailoring", "Liquidator's Hazard Suit", "chest", "armor", "cloth", "spirit_healer",
     "The full suit, hood to boots, the way the Watch's seamstresses cut it after the first year's losses.",
     "gear_wow_chest_cloth_12_1"),
    ("rep_liq_seep_proof_jerkin", "leatherworking", "Seep-Proof Jerkin", "chest", "armor", "leather", "agility",
     "Boiled leather sealed with apothecary wax, for the ones who have to go in close.",
     "gear_wow_chest_leather_16_1"),
]
#: (id, trade, name, slot, kind, type, identity, flavour, icon, tier): the patterns the shelf carries before exalted,
#: blue, made the same way the exalted recipes are
SHELF_PATTERNS = [
    ("rep_liq_quarantine_wraps", "tailoring", "Quarantine Wraps", "wrist", "armor", "cloth", "spirit_healer",
     "Linen bound twice round the wrist and waxed, so nothing gets in at the cuff. Dr. Seitkali's design.",
     "gear_wow_wrist_96", "honored"),
    ("rep_liq_wireline_gloves", "leatherworking", "Wireline Gloves", "hands", "armor", "leather", "agility",
     "Thick enough to handle the fence wire, thin enough to feel it hum. Corporal Delgado swears by them.",
     "gear_wow_hands_desecrated_leatherglove", "revered"),
]
FRIENDLY_SUPPLIES = ["liq_iodine_tincture", "liq_seep_washed_bandage"]
HONORED_SUPPLIES = ["flask_mending"]

#: the camp's two supplies, written into data/consumables/consumable_types.json
CONSUMABLES = {
    "elixirs": {
        "consumable_id": "liq_iodine_tincture", "name": "Liquidator's Iodine Tincture", "consumable_type": "elixir",
        "description": ("Iodine in a little spirit, a spoonful before you go out. In 1986 they gave the people near "
                        "Chernobyl iodine so the fallout's couldn't settle in them. +40 Nature Resistance for 30 "
                        "minutes. Guardian buff."),
        "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": 50,
        "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 60, "buff_category": "guardian",
        "stat_bonuses": {"nature_resistance": 40},
    },
    "health_potions": {
        "consumable_id": "liq_seep_washed_bandage", "name": "Seep-Washed Bandage", "consumable_type": "health_potion",
        "description": ("Boiled linen, washed three times at the troughs, rolled by the infirmary by the hundred. "
                        "Restores health at once."),
        "effect_value": 1050, "effect_duration": 0, "level_multiplier": 0.0, "required_level": 52,
        "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": 0, "sell_price": 90, "buff_category": None,
    },
}


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d):
    (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def payers():
    """(open world, the Exclusion Zone's trash, the Exclusion Zone's bosses), from the content builder's roster."""
    from tools import build_deadwind_content as DC
    open_world = sorted(n for n, r in DC.ROSTER.items() if r[5] in (DC.WEST, DC.EAST) and not r[3])
    return open_world, sorted(DC.EZ_TRASH), list(DC.EZ_BOSSES)


def main():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from tools.reward_icons import unclash
    C.PICKER = Picker()
    bad = []

    open_world, ez_trash, _ez_bosses = payers()
    creatures = load("data/creatures/creatures.json")["creatures"]
    missing = [c for c in open_world + ez_trash if c not in creatures]
    if missing:
        bad.append(f"kill rep for creatures that don't exist: {missing}")
    fd = load("data/factions/factions.json")
    for fid, f in fd["factions"].items():
        if fid == FID:
            continue
        clash = set((f.get("kill_rep") or {}).get("creatures", {})) & set(open_world + ez_trash)
        if clash:
            bad.append(f"{sorted(clash)} already pay {fid}; a creature pays one faction")

    # ---- the supplies
    cd = load("data/consumables/consumable_types.json")
    for cat, rec in CONSUMABLES.items():
        lst = cd[cat]
        lst[:] = [x for x in lst if x.get("consumable_id") != rec["consumable_id"]] + [dict(rec)]

    # ---- the gear
    fr = load("data/items/faction_rewards.json")
    items = fr["items"]
    for (iid, name, slot, kind, typ, ident, price, flav) in HONORED + REVERED:
        items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.BLUE_ILVL, "rare", flav, price)
        items[iid]["faction"] = FID
        unclash(items[iid])
        bad += b
    for (iid, name, slot, kind, typ, ident, price, flav) in EXALTED:
        items[iid], b = BFR.author_unique(iid, name, slot, kind, typ, ident, BFR.EPIC_ILVL, "epic", flav, price)
        items[iid]["faction"] = FID
        bad += b

    # ---- the exalted recipes
    docs = {}
    picks = load("data/items/crafted_icons.json")
    for rid, trade, name, slot, kind, typ, ident, flav, icon, *tier in (EXALTED_RECIPES + SHELF_PATTERNS):
        blue = bool(tier)
        path = ROOT / "data" / BFR.TRADE_FILE[trade] / "recipes.json"
        d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        inputs, mtier = BFR.PLACEHOLDER[trade]
        out = {"kind": kind, "slot": slot, "stat_template": C.IDENTITIES[ident][1],
               "item_level": BFR.BLUE_ILVL if blue else BFR.EPIC_ILVL, "rarity": "rare" if blue else "epic",
               "material_tier": mtier, "identity": ident, "flavor": flav,
               "fixed_item_level": True, "required_level": BFR.WORN_AT}
        if kind == "weapon":
            out["weapon_type"] = typ
            ident = C.weapon_identity(typ, ident)
        else:
            out["armor_type"] = typ
        item = C.author(rid, {"name": name, "output": dict(out)}, ident, flav)
        bad += C.audit_item("reputation recipe", rid, item)
        item["required_level"] = BFR.WORN_AT
        item["icon_id"] = icon
        out["item"] = item
        book[rid] = {"name": name, "inputs": dict(inputs), "skill_required": 300, "output": out,
                     "skill_range": [300, 305, 310, 315], "source": "vendor", "faction": FID,
                     "_rare_ingredients_todo": True}
        picks["icons"][name] = icon
    if bad:
        print("FAILED - fix the data, not the check:")
        for b in bad:
            print("  -", b)
        return 1

    # ---- write
    rec = fd["factions"].get(FID, {})
    keep_rewards = rec.get("rewards")
    keep_also = (rec.get("quest_rep") or {}).get("also")
    rec.update(json.loads(json.dumps(FACTION)))
    if keep_also:
        rec["quest_rep"]["also"] = keep_also
    rec["kill_rep"] = {
        "_comment": ["Deadwind's mutated wild and stuck dead: 10 a kill to Honored. The Exclusion Zone's trash: 10 a "
                     "kill to Revered, since the dungeon is the road past Honored."],
        "creatures": {**{n: [10, "honored"] for n in open_world}, **{n: [10, "revered"] for n in ez_trash}},
    }
    rec["dungeon_rep"] = {"_comment": "A boss kill in the Exclusion Zone pays 75 (tools/build_deadwind_content.py).",
                          "per_boss": 75,
                          "dungeons": ["The Exclusion Zone", "The Exclusion Zone: The Reactor Hall",
                                       "The Exclusion Zone: The Foot"]}
    rw = keep_rewards or {}
    rw["vendor_stock"] = {QM: {
        "friendly": list(FRIENDLY_SUPPLIES),
        "honored": list(HONORED_SUPPLIES) + [f"unique:{r[0]}" for r in HONORED]
                   + [r[0] for r in SHELF_PATTERNS if r[-1] == "honored"],
        "revered": [f"unique:{r[0]}" for r in REVERED] + [r[0] for r in SHELF_PATTERNS if r[-1] == "revered"],
        "exalted": [f"unique:{r[0]}" for r in EXALTED] + [r[0] for r in EXALTED_RECIPES],
    }}
    rw["_comment"] = ["Gates, not a displayed ladder (the faction panel stays information only).",
                      "TBC-style shelf (tools/build_liquidators.py, 18 Nov 2026): friendly the camp's supplies, "
                      "honored the dosimeter, revered six ilvl 67 blues, exalted three ilvl 73 epics and two recipes."]
    rw.setdefault("quests", {})
    rec["rewards"] = rw
    fd["factions"][FID] = rec
    save("data/factions/factions.json", fd)
    save("data/items/faction_rewards.json", fr)
    save("data/items/crafted_icons.json", picks)
    save("data/consumables/consumable_types.json", cd)
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{FACTION['name']}: {len(open_world)} open-world creatures to Honored, {len(ez_trash)} Exclusion Zone trash "
          f"to Revered, its bosses 75; shelf {len(HONORED) + len(REVERED)} blues, {len(EXALTED)} epics, "
          f"{len(EXALTED_RECIPES)} recipes, {len(CONSUMABLES)} supplies")
    return 0


if __name__ == "__main__":
    sys.exit(main())
