#!/usr/bin/env python3
"""The "????" faction: a reputation nobody tells you about, and a seller nobody can tell you where to find.

    PYTHONPATH=. python3 tools/build_unnamed_faction.py

Kyle, 15 Nov 2026: "I want another secret vendor. Honored will be blue ilvl 69. Revered will be epic ilvl 78,
Exalted will be ilvl 85. --- Faction is "????" - It will be INCREDIBLY WELL HIDDEN and rep will only be through
Frontier Bosses and not advertised where rep comes from. Frontier bosses give 50 rep a kill but we don't have an
indication of how much rep we have it's only advertised as "Current Status: Neutral / Friendly .... / Exalted"
... He will sell 8 from each rep - so 24 in total." Then: "design everything with the items and everything and
have the vendor but dont place him since he MUST be at the bottom of a high-end dungeon and be a bitch to get
to ... not implement him yet."

WHAT THIS BUILDS (and what it doesn't)
  - the faction, "????" (data/factions/factions.json the_unnamed): "secret": true, so the journal shows only
    "Current Status: <tier>" (no bar, no numbers, no description, no leader), and combat never prints its
    gains or its tier-ups. Its only source is "frontier_boss_rep": 50, paid by world/faction_manager for any
    boss killed inside a frontier zone (world/hidden_zones.kind == "frontier"). Nothing in the game names that.
  - 24 items in data/items/unnamed_rewards.json, sold as unique:<id>: 8 blues at honored (ilvl 69), 8 epics at
    revered (ilvl 78), 8 epics at exalted (ilvl 85), all worn at 60, every epic with its own flavour line.
    Stats from the crafted-gear identities on the bent budget past 60 (entities/item_budget.budget_level),
    each tier covering tanks, healers, casters and fighters (a direction, not a cage).
  - the seller, PARKED: his record is data/npcs/unplaced_vendors.json and his shelf is the faction's
    "vendor_stock_unplaced", which nothing reads. He is in no zone and no shop. Placing him is a later job,
    done without telling Kyle where (the SECRETS rule): at the bottom of a high-end dungeon, through a hidden
    zone, on a route that doesn't run straight.

THE THEME is the edge of the map: the ones who went past where the roads stop, and what they brought back.
Nothing here touches the embargoed lore.
Idempotent.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

FACTION = "the_unnamed"
VENDOR = "unnamed_wayless"
G = 10000

# (id, name, slot, kind, armour or weapon type, identity, price in gold, flavour)
HONORED = [   # blue, ilvl 69
    ("un_edgewalker_treads", "Edgewalker's Treads", "feet", "armor", "leather", "agility", 150,
     "Worn thin at the toe by roads that stopped being roads."),
    ("un_mapless_mantle", "Mapless Mantle", "shoulder", "armor", "cloth", "caster", 160,
     "Embroidered with a map, and every line on it trails off."),
    ("un_farwatch_gauntlets", "Farwatch Gauntlets", "hands", "armor", "plate", "tank", 150,
     "Made for holding a line that nobody else can see."),
    ("un_lantern_bearers_cord", "Lantern-Bearer's Cord", "waist", "armor", "cloth", "healer", 145,
     "A hook on the left hip for a lantern, and scorch marks where it hung."),
    ("un_trailblazers_legguards", "Trailblazer's Legguards", "legs", "armor", "mail", "hunter", 180,
     "Scratched by brush that doesn't grow anywhere you've been."),
    ("un_band_of_the_unmarked_road", "Band of the Unmarked Road", "ring", "armor", None, "strength_crit", 155,
     "There's no stone in it, only a groove where the road should be."),
    ("un_pendant_of_no_north", "Pendant of No North", "neck", "armor", None, "caster_crit", 155,
     "A compass rose with the north point filed off."),
    ("un_wayfinders_bracers", "Wayfinder's Bracers", "wrist", "armor", "mail", "tide_healer", 140,
     "Etched with stars. Not the ones you know."),
]
REVERED = [   # epic, ilvl 78
    ("un_edge_of_the_known", "Edge of the Known", "main_hand", "weapon", "sword_1h", "rogue_crit", 560,
     "Everything on this side of it has a name."),
    ("un_the_blank_atlas", "The Blank Atlas", "off_hand", "weapon", "tome", "healer", 520,
     "Every page is empty. Every page is somewhere you haven't been yet."),
    ("un_farwatch_bulwark", "Farwatch Bulwark", "off_hand", "weapon", "shield", "shield_tank", 540,
     "Somebody has to stand where the map runs out."),
    ("un_pathless_greatbow", "Pathless Greatbow", "ranged", "weapon", "bow", "hunter_crit", 600,
     "There's no road where you're aiming. There never was."),
    ("un_ridgebreaker_legplates", "Ridgebreaker Legplates", "legs", "armor", "plate", "strength", 580,
     "The ridge was in the way. Now it isn't."),
    ("un_hood_of_the_farthest_light", "Hood of the Farthest Light", "head", "armor", "cloth", "caster", 560,
     "The last lamp before the dark. Whoever wore it kept walking."),
    ("un_hide_of_the_long_dark", "Hide of the Long Dark", "chest", "armor", "leather", "bear", 600,
     "Whatever lives out past the edge didn't get through this. It tried."),
    ("un_hauberk_of_the_last_signal", "Hauberk of the Last Signal", "chest", "armor", "mail", "haste_caster", 600,
     "The last word anyone heard from out there came from someone wearing this."),
]
EXALTED = [   # epic, ilvl 85
    ("un_here_be_monsters", "Here Be Monsters", "main_hand", "weapon", "axe_2h", "strength_crit", 1200,
     "The old maps warned you. This is what the warning was for."),
    ("un_lodestar", "Lodestar", "main_hand", "weapon", "staff", "caster_crit", 1150,
     "It always points the same way. Nobody knows what's there."),
    ("un_warden_of_the_edge", "Warden of the Edge", "main_hand", "weapon", "sword_1h", "tank_weapon", 1050,
     "Nothing comes back over the edge while this is drawn."),
    ("un_farsight", "Farsight", "ranged", "weapon", "gun", "hunter_precise", 1000,
     "You can see a long way from the edge. Further than is comfortable."),
    ("un_the_long_way_home", "The Long Way Home", "main_hand", "weapon", "mace_1h", "high_healer", 1050,
     "Everyone who made it back came the long way."),
    ("un_unmapped", "Unmapped", "main_hand", "weapon", "dagger", "rogue_crit", 1000,
     "If it isn't on the map, it can't be found. Neither can you."),
    ("un_signet_of_the_final_mile", "Signet of the Final Mile", "ring", "armor", None, "precise_caster", 950,
     "Most turn back with a mile to go. This was made for the ones who didn't."),
    ("un_mask_of_the_farthest_hunt", "Mask of the Farthest Hunt", "head", "armor", "leather", "bear", 980,
     "Out past the last trail, something bigger than a bear is still hunting. So are you."),
]
TIERS = (("honored", HONORED, "rare", 69), ("revered", REVERED, "epic", 78), ("exalted", EXALTED, "epic", 85))

FACTION_RECORD = {
    "name": "????",
    "secret": True,
    "description": "",
    "home_zone": None,
    "home_name": "",
    "lore": [],
    "leader": {},
    "frontier_boss_rep": 50,
    "_comment": [
        "SECRET (tools/build_unnamed_faction.py, Kyle 15 Nov 2026). The journal shows only 'Current Status: <tier>';",
        "combat never prints its gains; nothing in the game says where it comes from (any boss in a frontier zone,",
        "50 a kill). Its seller is parked: vendor_stock_unplaced is read by nothing until he is placed."],
}

#: the seller, parked until he's placed (and his place is never told to Kyle)
SELLER = {
    "vendor_id": VENDOR, "name": "Wayless", "race": "human", "gender": "male", "appearance_variant": 7,
    "facing": "down", "tile_sprite": "npc", "faction": "neutral", "buys_from_player": True, "sells": [],
    "sells_gear": False, "gear_level": 60,
    "greeting": "You found me. Most people turn back long before here, so I don't get much company. Let's see "
                "what you've brought back from out there.",
    "placement_brief": "At the bottom of a high-end dungeon, reached THROUGH a hidden zone, on a route that "
                       "doesn't run straight (south, east, north, east, north again, with secrets along it). "
                       "Never visible from any main path. Never described to Kyle.",
    "_unplaced": True,
}


def main():
    import build_faction_rewards as B
    items, bad = {}, []
    shelf = {}
    for tier, rows, rarity, ilvl in TIERS:
        ids = []
        for iid, name, slot, kind, typ, ident, price, flav in rows:
            item, b = B.author_unique(iid, name, slot, kind, typ, ident, ilvl, rarity, flav, price)
            item["faction"] = FACTION
            items[iid] = item
            bad += b
            ids.append(f"unique:{iid}")
        shelf[tier] = ids
    if bad:
        raise SystemExit("audit failed:\n  " + "\n  ".join(bad))
    (ROOT / "data/items/unnamed_rewards.json").write_text(json.dumps(
        {"_doc": "The '????' faction's seller's stock (tools/build_unnamed_faction.py). Sold as unique:<id>.",
         "items": items}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fp = ROOT / "data/factions/factions.json"
    fd = json.loads(fp.read_text(encoding="utf-8"))
    rec = dict(FACTION_RECORD)
    rec["rewards"] = {"vendor_stock_unplaced": {VENDOR: shelf}}
    fd["factions"][FACTION] = rec
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    up = ROOT / "data/npcs/unplaced_vendors.json"
    ud = json.loads(up.read_text(encoding="utf-8")) if up.exists() else {
        "_doc": "Sellers designed but not yet in the world. Nothing loads this file.", "vendors": {}}
    ud["vendors"][VENDOR] = SELLER
    up.write_text(json.dumps(ud, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"'????': {len(items)} items ({', '.join(f'{t} {len(r)}' for t, r, _r, _i in TIERS)}); seller parked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
