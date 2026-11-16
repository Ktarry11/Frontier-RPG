#!/usr/bin/env python3
"""The "????" faction: a reputation nobody tells you about, and a seller nobody can tell you where to find.

    PYTHONPATH=. python3 tools/build_unnamed_faction.py

Kyle, 15 Nov 2026: "I want another secret vendor. Honored will be blue ilvl 69. Revered will be epic ilvl 78,
Exalted will be ilvl 85. --- Faction is "????" - It will be INCREDIBLY WELL HIDDEN and rep will only be through
Frontier Bosses and not advertised where rep comes from. Frontier bosses give 50 rep a kill but we don't have an
indication of how much rep we have it's only advertised as "Current Status: Neutral / Friendly .... / Exalted"
... He will sell 8 from each rep - so 24 in total." Then 15 a tier, 45 in all, for every CoA class and slot. Then: "design everything with the items and everything and
have the vendor but dont place him since he MUST be at the bottom of a high-end dungeon and be a bitch to get
to ... not implement him yet."

WHAT THIS BUILDS (and what it doesn't)
  - the faction, "????" (data/factions/factions.json the_unnamed): "secret": true, so the journal shows only
    "Current Status: <tier>" and one cryptic line (no bar, no numbers, no leader), and combat never prints its
    gains or its tier-ups. Its only source is "frontier_boss_rep": 50, paid by world/faction_manager for any
    boss killed inside a frontier zone (world/hidden_zones.kind == "frontier"). Nothing in the game names that.
  - 45 items in data/items/unnamed_rewards.json, sold as unique:<id>: 15 blues at honored (ilvl 69), 15 epics at
    revered (ilvl 78), 15 epics at exalted (ilvl 85), all worn at 60, every epic with its own flavour line.
    Stats from the crafted-gear identities on the bent budget past 60 (entities/item_budget.budget_level),
    covering all 97 specs of the 30 classes at every tier (see EVERY CLASS, EVERY SLOT below).
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

# EVERY CLASS, EVERY SLOT (Kyle, 15 Nov 2026: "lets do 15/15/15 ... Don't forget ALL the CoA classes, all the
# equipment slots....everything. Don't be limited! Like trinkets", then "wheres my tinkerer healer? My caster
# shield? My strength leather? ... STOOOOOOP DEFAULTING TO CLASSIC 9 CLASSES"). The shop is checked against all
# 97 specs of the 30 classes (data/items/spec_gear.json) by tools/qa_unnamed_faction.py: every spec finds
# something it wants at every tier; every armour type is made for every role that wears it (strength leather
# for the Barbarian, a mail healer for the Tinker and the Vizier, plate casters for the Starcaller and the
# Cultist); every weapon any spec carries is sold, relics, wands and thrown included; a caster's shield and a
# healer's shield; and trinkets that do something.
#
# (id, name, slot, kind, armour or weapon type, identity, price in gold, flavour)
HONORED = [   # blue, ilvl 69
    ("un_edgewalker_treads", "Edgewalker's Treads", "feet", "armor", "leather", "agility", 150,
     "Worn thin at the toe by roads that stopped being roads."),
    ("un_mapless_spaulders", "Mapless Spaulders", "shoulder", "armor", "plate", "caster", 165,
     "Engraved with a map, and every line on it trails off."),
    ("un_farwatch_gauntlets", "Farwatch Gauntlets", "hands", "armor", "plate", "tank", 150,
     "Made for holding a line that nobody else can see."),
    ("un_lantern_bearers_cord", "Lantern-Bearer's Cord", "waist", "armor", "cloth", "healer", 145,
     "A hook on the left hip for a lantern, and scorch marks where it hung."),
    ("un_trailblazers_legguards", "Trailblazer's Legguards", "legs", "armor", "mail", "hunter", 180,
     "Scratched by brush that doesn't grow anywhere you've been."),
    ("un_band_of_the_unmarked_road", "Band of the Unmarked Road", "ring", "armor", None, "tank_any", 155,
     "There's no stone in it, only a groove where the road should be."),
    ("un_pendant_of_no_north", "Pendant of No North", "neck", "armor", None, "caster_crit", 155,
     "A compass rose with the north point filed off."),
    ("un_wayfinders_bracers", "Wayfinder's Bracers", "wrist", "armor", "mail", "tide_healer", 140,
     "Etched with stars. Not the ones you know."),
    ("un_flare_of_the_lost_party", "Flare of the Lost Party", "ranged", "weapon", "gun", "tide_healer", 170,
     "Built to call for help. Turns out it can be the help."),
    ("un_cragstriders_jerkin", "Cragstrider's Jerkin", "chest", "armor", "leather", "strength", 175,
     "Cut loose and heavy across the shoulders, for someone who climbs with their arms."),
    ("un_hollowridge_headguard", "Hollowridge Headguard", "head", "armor", "mail", "bear", 165,
     "The dents all face forward."),
    ("un_lamplighters_wand", "Lamplighter's Wand", "ranged", "weapon", "wand", "caster", 150,
     "It was a lamp-lighting taper once. It still finds the dark."),
    ("un_compass_of_bad_directions", "Compass of Bad Directions", "trinket", "armor", None, "physical", 160,
     "It points at trouble. It has never once been wrong."),
    ("un_surveyors_gloves", "Surveyor's Gloves", "hands", "armor", "leather", "caster_crit", 150,
     "Ink-stained at the fingertips from maps nobody finished."),
    ("un_the_last_handhold", "The Last Handhold", "main_hand", "weapon", "axe_1h", "wildheart", 170,
     "A climber's axe, the last grip before the drop. Somebody pried it loose and kept it."),
]
REVERED = [   # epic, ilvl 78
    ("un_edge_of_the_known", "Edge of the Known", "main_hand", "weapon", "fist_weapon", "rogue_crit", 560,
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
    ("un_ten_foot_pole", "Ten-Foot Pole", "main_hand", "weapon", "polearm", "agility", 580,
     "For prodding the things you'd rather not get any closer to."),
    ("un_where_the_road_ends", "Where the Road Ends", "main_hand", "weapon", "sword_2h", "strength_crit", 600,
     "It isn't a figure of speech. You'll know the place when you see it."),
    ("un_holdfast", "Holdfast", "main_hand", "weapon", "mace_2h", "bear_weapon", 580,
     "Plant it, and nothing gets past. Not even you."),
    ("un_cairn_totem", "Cairn Totem", "ranged", "weapon", "totem", "mail_caster", 520,
     "Stones stacked where the trail ends. Whoever passes adds one more."),
    ("un_last_light_aegis", "Last Light Aegis", "off_hand", "weapon", "shield", "healer", 560,
     "Polished bright enough to signal with. Whoever held it wanted to be found."),
    ("un_the_last_lantern", "The Last Lantern", "trinket", "armor", None, "high_healer", 560,
     "It's never been lit. It's never gone out."),
    ("un_lightkeepers_pauldrons", "Lightkeeper's Pauldrons", "shoulder", "armor", "plate", "plate_healer", 560,
     "Somebody kept the light at the edge burning for years, and kept everyone near it alive."),
]
EXALTED = [   # epic, ilvl 85
    ("un_here_be_monsters", "Here Be Monsters", "main_hand", "weapon", "axe_2h", "strength_crit", 1200,
     "The old maps warned you. This is what the warning was for."),
    ("un_lodestar", "Lodestar", "main_hand", "weapon", "staff", "caster_crit", 1150,
     "It always points the same way. Nobody knows what's there."),
    ("un_warden_of_the_edge", "Warden of the Edge", "main_hand", "weapon", "sword_1h", "tank_weapon", 1050,
     "Nothing comes back over the edge while this is drawn."),
    ("un_farsight", "Farsight", "ranged", "weapon", "crossbow", "hunter_precise", 1000,
     "You can see a long way from the edge. Further than is comfortable."),
    ("un_the_long_way_home", "The Long Way Home", "main_hand", "weapon", "mace_1h", "high_healer", 1050,
     "Everyone who made it back came the long way."),
    ("un_unmapped", "Unmapped", "main_hand", "weapon", "dagger", "rogue_crit", 1000,
     "If it isn't on the map, it can't be found. Neither can you."),
    ("un_signet_of_the_final_mile", "Signet of the Final Mile", "ring", "armor", None, "precise_caster", 950,
     "Most turn back with a mile to go. This was made for the ones who didn't."),
    ("un_trophy_of_the_farthest_hunt", "Trophy of the Farthest Hunt", "trinket", "armor", None, "bear", 1000,
     "Out past the last trail, something bigger than a bear is still hunting. So are you."),
    ("un_ward_of_the_last_map", "Ward of the Last Map", "off_hand", "weapon", "shield", "mail_caster", 1000,
     "The only map of the far side is painted on the inside of this shield. Don't lose it."),
    ("un_idol_of_the_last_grove", "Idol of the Last Grove", "ranged", "weapon", "idol", "healer", 950,
     "Carved from the last tree before the edge. It still has roots."),
    ("un_libram_of_the_final_entry", "Libram of the Final Entry", "ranged", "weapon", "libram", "crusader", 950,
     "The last page was written by someone who was still walking."),
    ("un_stone_from_the_edge", "Stone from the Edge", "ranged", "weapon", "thrown", "rogue_crit", 950,
     "Thrown from the very last step. It came back."),
    ("un_signal_fire_breastplate", "Signal-Fire Breastplate", "chest", "armor", "plate", "crusader", 1150,
     "Lit at the edge, so the next ones would know how far the last ones got."),
    ("un_lifeline_harness", "Lifeline Harness", "chest", "armor", "leather", "high_healer", 1100,
     "Tied to the one behind you, so nobody goes over the edge alone."),
    ("un_cloak_of_the_last_horizon", "Cloak of the Last Horizon", "back", "armor", None, "physical", 1000,
     "Dyed the colour of the sky right where it meets the edge."),
]
#: Trinkets do things (claude/trinkets_must_do_things.md). Sized up from the woodworking trinkets for item level
#: 69 to 85; flat numbers are curved to the wearer's level at runtime (combat/proc_text).
PROCS = {
    "un_compass_of_bad_directions": {
        "trigger": "on_crit", "chance": 15, "icd": 4,
        "apply_effect": {"effect_id": "unnamed_bad_directions", "name": "Wrong Way, Right Place",
                         "effect_type": "buff", "duration": 3, "stat_mods": {"attack_power": 60},
                         "on_target": False},
        "describe": "Your critical hits have a chance to grant 60 attack power for 3 turns."},
    "un_the_last_lantern": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 4,
        "apply_effect": {"effect_id": "unnamed_last_lantern", "name": "Lantern-Light", "effect_type": "buff",
                         "duration": 3, "stat_mods": {"healing_power": 90}, "on_target": False},
        "grant_resource": {"resource": "mana", "amount": 60},
        "describe": "Your healing spells have a chance to restore 60 mana and grant 90 healing power for 3 turns."},
    "un_trophy_of_the_farthest_hunt": {
        "trigger": "on_damage_taken", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "unnamed_farthest_hunt", "name": "Bigger Than a Bear", "effect_type": "buff",
                         "duration": 3, "absorb_pct_max_health": 0.08, "stat_mods": {}, "on_target": False},
        "describe": "When you're struck, you have a chance to shrug it off: a shield that absorbs 8% of your "
                    "health."},
}
TIERS = (("honored", HONORED, "rare", 69), ("revered", REVERED, "epic", 78), ("exalted", EXALTED, "epic", 85))

FACTION_RECORD = {
    "name": "????",
    "secret": True,
    # Kyle, 15 Nov 2026: "Give a cryptic ass description too." It's the only thing the page says, and it says
    # nothing about where standing comes from (tools/qa_unnamed_faction.py holds it to that).
    "description": ("Somebody keeps a ledger of the places that were never on any map, and of everyone who's "
                    "walked out of one alive. You've never met them. Your name is in it anyway, and the line "
                    "under it gets a little longer every time."),
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
            if iid in PROCS:
                item["proc"] = json.loads(json.dumps(PROCS[iid]))
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
