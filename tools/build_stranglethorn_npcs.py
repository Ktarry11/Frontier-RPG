#!/usr/bin/env python3
"""Populate Grom'gol and Booty Bay. Idempotent.

    PYTHONPATH=. python3 tools/build_stranglethorn_npcs.py

POSITIONS ARE READ FROM THE ZONE MODULES, never retyped. Every earlier town in this game drifted the
same way - the NPC roster and the layout were authored in two places and the coordinates slid apart
until somebody was standing inside a building (Razor Hill, Crossroads, Ratchet and Camp Taurajo all had
it, and it never surfaces as a crash, only as "I walked there and nothing happened"). Here the
NPC_POSITIONS dict in tools/handbuilt_gromgol.py / tools/handbuilt_booty_bay.py is the single source,
and this script fails loudly if an id in the roster below has no position in it.

WHAT EACH TOWN IS FOR, because it decides who lives in it:

  GROM'GOL is a supply line with a fence round it. Nobody here chose Stranglethorn; they were posted to
  it. The roster is a garrison - command, the berth, the trades that keep a garrison standing - plus one
  Darkspear attaché who is the only person in the camp who is actually FROM here, and knows it.

  BOOTY BAY is a port authority behaving like a government. The roster is the people who take a cut:
  the toll, the harbourmaster, the dockmaster, the Baron. Plus the Cartel's factor, who still signs for
  Ratchet and will tell you the port has not formally left the company - which is exactly the tension
  the faction is built on (claude/stranglethorn_design.md).

VENDORS SELL CONSUMABLES AND TRADE GOODS ONLY. No gear: an item id invented here would be a dangling
reference, and the standing rule is that no magic-resistance gear exists below 45 and no high-tier
material before 60 - Stranglethorn tops out at 42, so a gear vendor here has nothing new it is allowed
to stock that the loot tables do not already give.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools import handbuilt_booty_bay as BB     # noqa: E402
from tools import handbuilt_gromgol as GG       # noqa: E402

# npc_id -> (name, race, gender, greeting)
GROMGOL = {
    "gromgol_commander": ("Overseer Mokra", "orc", "female",
                          "The camp holds. That is the whole of my report and it has been for three years."),
    "gromgol_berth_master": ("Berth-Master Zekka", "troll", "male",
                             "Everything you see here came off that airship. Including me."),
    "gromgol_signalman": ("Signalman Grut", "orc", "male",
                          "Two flags means they are coming in. Three means they are not stopping."),
    "gromgol_scout": ("Scout Hanzo", "orc", "male",
                      "I have walked as far south as the seam and back. I do not recommend the walk."),
    "gromgol_drillmaster": ("Drillmaster Ukko", "orc", "male",
                            "Half of them have never fought anything that climbs."),
    "gromgol_south_sentry": ("Sentry Vrak", "orc", "female",
                             "Road's that way. Keep to it and the jungle mostly keeps to itself."),
    "gromgol_wounded_runner": ("Runner Teza", "troll", "female",
                               "I made it back. Took the long way round the fen and I would do it again."),
    "gromgol_field_medic": ("Field-Medic Sulaa", "orc", "female",
                            "Bring them to me standing if you can. Bring them to me either way."),
    "gromgol_cartographer": ("Mapmaker Ashi", "orc", "female",
                             "The map is wrong. It is less wrong than it was. That is the job."),
    "gromgol_troll_attache": ("Attaché Zul'jana", "troll", "female",
                              "You all keep calling it a jungle. It has a name. Several."),
    "gromgol_storesman": ("Storesman Pell", "orc", "male",
                          "Count it in, count it out. The jungle takes what it wants in between."),
    "gromgol_beast_handler": ("Beast-Handler Kozza", "troll", "female",
                              "They are not tame. They are fed. There is a difference and I respect it."),
    "gromgol_smith": ("Smith Dorgun", "orc", "male",
                      "Damp eats steel faster than any enemy I ever met."),
    # services. The hearth and the roost: the two reasons a camp counts as somewhere you can come back to.
    "gromgol_innkeeper": ("Innkeeper Rukha", "orc", "female",
                          "Twelve bunks and a fire. Set your hearth here and the jungle stops being a one-way trip."),
    "gromgol_flight_master": ("Windrider-Keeper Pazzik", "goblin", "male",
                              "Only one other roost worth flying to from here, and the Baron charges me to land on it."),
}
GROMGOL_VENDORS = {
    "gromgol_quartermaster": ("Quartermaster Ghal", "orc", "female", 33,
                              "Signed for, issued, and I want it back."),
    "gromgol_trader": ("Trader Burg", "orc", "male", 31,
                       "Whatever came up the stair this week, I have some of it."),
    "gromgol_provisioner": ("Provisioner Nakka", "orc", "female", 30,
                            "Eat before you go south. People forget."),
    "gromgol_weaponsmith": ("Weaponsmith Trag", "orc", "male", 33,
                            "Oil it every night down here or it will not be yours by morning."),
    "gromgol_herbalist": ("Herbalist Mossa", "troll", "female", 30,
                          "Half of what grows out there will kill you. I sell the other half."),
}

BOOTY_BAY = {
    "bootybay_baron": ("Baron Revilgaz", "goblin", "male",
                       "Nothing leaves this cove without my name on it. Not even you."),
    "bootybay_baron_aide": ("Aide Fipple", "goblin", "male",
                            "The Baron is reviewing it. The Baron is always reviewing it."),
    "bootybay_toll_collector": ("Tollkeeper Nizzik", "goblin", "female",
                                "Landing fee. You have already landed, so we are only arguing about the amount."),
    "bootybay_harbourmaster": ("Harbourmaster Sprocket", "goblin", "male",
                               "Tide, berth, weather, and who is lying about which. That is the whole tower."),
    "bootybay_gate_guard": ("Bruiser Kolk", "orc", "male",
                            "Trouble on the quay is my trouble. Trouble up here is yours."),
    "bootybay_lookout": ("Lookout Minzi", "goblin", "female",
                         "Clear to the cape. Which only means I cannot see them yet."),
    "bootybay_dockmaster": ("Dockmaster Brek", "goblin", "male",
                            "Three piers, one crane, and everybody wants the middle one."),
    "bootybay_crane_hand": ("Crane-Hand Durgo", "orc", "male",
                            "Stand under it once and you will not do it twice."),
    "bootybay_shipwright": ("Shipwright Vella", "goblin", "female",
                            "Salt, worm and rot. Pick two and I can still float it."),
    "bootybay_cartel_factor": ("Factor Weezel", "goblin", "male",
                               "The port has not left the company. I have the paperwork. Nobody reads it."),
    "bootybay_fence": ("The Quiet Man", "human", "male",
                       "I did not see you come in and I will not see you leave."),
    "bootybay_bloodsail_captive": ("Dagger-Hand Oona", "human", "female",
                                   "They have not hanged me and they have not let me go. Make of that what you like."),
    "bootybay_troll_pilot": ("Pilot Zan'rek", "troll", "male",
                             "The reef moves. Not fast. Fast enough."),
    "bootybay_street_kid": ("Scrip", "goblin", "male",
                            "Carry your crate? Watch your crate? Both is cheaper."),
    # services
    "bootybay_banker": ("MerchantTusk", "goblin", "male",
                        "The vault is under the waterline and it has never flooded. Think about that."),
    "bootybay_flight_master": ("Wind-Rider Zekki", "troll", "female",
                               "North to the camp, and that is the whole map. Nobody flies out of this jungle."),
}
BOOTY_BAY_VENDORS = {
    "bootybay_trader": ("Trader Nixxle", "goblin", "female", 38,
                        "Everything on this shelf came off a boat that was going somewhere else."),
    "bootybay_tavern_keeper": ("Keeper Marla", "human", "female", 36,
                               "Drink it inside. What you spill out there, the tide keeps."),
    "bootybay_shipping_clerk": ("Clerk Bexx", "goblin", "male", 36,
                                "Manifest, weight, destination. In that order or not at all."),
    "bootybay_fishmonger": ("Gurgle", "troll", "male", 34,
                            "Caught this morning. Some of it caught itself."),
    "bootybay_weapon_dealer": ("Dealer Sark", "goblin", "male", 38,
                               "I do not ask what for. I do ask for coin first."),
}

#: Bankers are an ambient-NPC flag, not a travel service - world/ambient_npc_manager.py reads
#: is_banker and ui/screens/bank_screen.py defaults the name to "MerchantTusk" when it has none.
BANKERS = {"bootybay_banker"}

GENERAL = ["healing_potion_standard", "mana_potion_standard", "bread_and_cheese", "roasted_meat",
           "meal_river_fish", "meal_spiced_haunch", "drink_spring_flask", "drink_honeyed_mead"]
TRADE = ["whetstone", "flux_medium", "flux_strong", "coal", "thread_fine", "thread_silken",
         "vial_empty", "vial_leaded", "resin", "curing_salt", "tanning_reagent"]
ALCHEMY = ["healing_potion_superior", "mana_potion_superior", "guardian_elixir_standard",
           "battle_elixir_standard", "elixir_of_toughness", "elixir_of_agility", "arcane_elixir"]
TAVERN = ["spiced_wine", "spiced_stew", "mushroom_broth", "roasted_meat", "bread_and_cheese",
          "drink_barley_beer", "drink_honeyed_mead"]

STOCK = {
    "gromgol_quartermaster": GENERAL + ["healing_potion_superior", "mana_potion_superior",
                                        "guardian_elixir_standard", "whetstone", "flux_medium"],
    "gromgol_trader": GENERAL + ["parchment", "thread_fine", "vial_empty", "glue", "salt"],
    "gromgol_provisioner": ["bread_and_cheese", "roasted_meat", "spiced_stew", "meal_trailbread",
                            "meal_river_fish", "drink_waterskin", "drink_barley_beer"],
    "gromgol_weaponsmith": ["whetstone", "flux_medium", "flux_strong", "coal", "resin", "sinew",
                            "fletching", "component_string"] + GENERAL[:4],
    "gromgol_herbalist": ALCHEMY + ["vial_empty", "vial_leaded", "dye_mild", "bleach"],
    "bootybay_trader": GENERAL + TRADE[:6],
    "bootybay_tavern_keeper": TAVERN + ["healing_potion_standard", "mana_potion_standard"],
    "bootybay_shipping_clerk": TRADE + ["parchment", "glue"],
    "bootybay_fishmonger": ["meal_river_fish", "meal_spiced_haunch", "roasted_meat", "salt",
                            "curing_salt", "drink_spring_flask"],
    "bootybay_weapon_dealer": ALCHEMY + ["whetstone", "flux_strong", "component_string", "sinew"],
}


def rows(roster, vendors, M, zone_key):
    pos = M.NPC_POSITIONS
    missing = [k for k in list(roster) + list(vendors) if k not in pos]
    if missing:
        raise SystemExit(f"{zone_key}: no position in NPC_POSITIONS for {missing}")
    npcs, vend = [], []
    for i, (nid, (name, race, gender, line)) in enumerate(roster.items()):
        x, y = pos[nid]
        row = {"npc_id": nid, "name": name, "zone": zone_key, "x": x, "y": y,
               "greeting": line, "gender": gender, "race": race,
               "appearance_variant": i % 24, "facing": "down"}
        if nid in BANKERS:
            row["is_banker"] = True
        npcs.append(row)
    for i, (vid, (name, race, gender, lvl, line)) in enumerate(vendors.items()):
        x, y = pos[vid]
        vend.append({"vendor_id": vid, "name": name, "zone": zone_key, "x": x, "y": y,
                     "tile_sprite": "npc", "sells": STOCK[vid], "buys_from_player": True,
                     "faction": "neutral", "gear_level": lvl, "sells_gear": False,
                     "race": race, "appearance_variant": (i * 5 + 3) % 24, "greeting": line})
    return npcs, vend


def merge(path, key, id_field, new):
    data = json.loads(path.read_text(encoding="utf-8"))
    by_id = {e[id_field]: e for e in data[key]}
    added = sum(1 for e in new if e[id_field] not in by_id)
    for e in new:
        by_id[e[id_field]] = e
    data[key] = [by_id[k] for k in by_id]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return added, len(new) - added


def main():
    gn, gv = rows(GROMGOL, GROMGOL_VENDORS, GG, GG.KEY)
    bn, bv = rows(BOOTY_BAY, BOOTY_BAY_VENDORS, BB, BB.KEY)

    # Every id the stock table names must already be sold by SOME existing shop. There is no single
    # item registry to check against - consumables, food, trade goods and crafted gear are authored in
    # four different files - so the honest check is that nothing here is a name I made up: if another
    # vendor in the game already stocks it, it resolves.
    existing = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    known = {s for v in existing for s in v.get("sells", [])}
    bad = sorted({s for v in gv + bv for s in v["sells"] if s not in known})
    if bad:
        raise SystemExit(f"vendor stock names items no existing shop sells: {bad}")

    a1, u1 = merge(ROOT / "data/npcs/ambient_npcs.json", "npcs", "npc_id", gn + bn)
    a2, u2 = merge(ROOT / "data/npcs/vendors.json", "vendors", "vendor_id", gv + bv)
    print(f"ambient NPCs: +{a1} new, {u1} updated   vendors: +{a2} new, {u2} updated")
    print(f"  Grom'gol  {len(gn)} npcs, {len(gv)} vendors")
    print(f"  Booty Bay {len(bn)} npcs, {len(bv)} vendors")


if __name__ == "__main__":
    main()
