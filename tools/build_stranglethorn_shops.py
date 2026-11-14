#!/usr/bin/env python3
"""Give Stranglethorn's ten shops stock that matches the people running them. Idempotent.

    PYTHONPATH=. python3 tools/build_stranglethorn_shops.py [--check]

Kyle, 29 Oct 2026: "we also need to ensure shops are properly done in STV - NEVER EVER default to
garbage generic shops."

WHAT WAS WRONG. The greetings were hand-written and good. The stock behind them was defaulted, and
the two halves had stopped describing the same person:

  Weaponsmith Trag       sold no weapons. Whetstones, flux, coal - and bread and potions.
  Dealer Sark            sold no weapons either. He sold elixirs. He is an alchemist by stock.
  Gurgle the fishmonger  sold roasted meat and spiced haunch. Those are not fish.
  Herbalist Mossa        sold finished potions and no herbs or reagents worth the name.
  All ten               sold gear to nobody, while gear_level sat set on every row - and
                         vendor_manager's own policy comment says gear vendors "are all
                         quartermasters, smiths, weaponsmiths, bowyers and engineers". STV has a
                         quartermaster, a weaponsmith and a weapon dealer. None of them sold gear.

And the shelves were interchangeable. Eleven items filled 53 of 109 slots across the ten shops:
roasted_meat on seven of them, bread_and_cheese on six, healing_potion_standard on five. Four of
Grom'gol's five vendors sold the same bread and the same meat. A dock town's trader stocked the same
sewing thread as an inland village. You could walk into any of the ten and see the same shelf.

THE RULE THIS APPLIES. Food belongs to the people who sell food. A smith sells what you do to a
blade and the blade itself. A clerk sells what you do to a crate. A fishmonger sells fish. Where two
vendors legitimately overlap - both ports stock rope and salt - they overlap on purpose and on
different items. Tarren Mill is the house standard and already works this way: its apothecary sells
only elixirs, its bowyer only fletching, sinew and string.

WHAT THIS ALSO FIXES, game-wide. Explosives, gadgets and ammo - 30 authored consumables - were sold
by ZERO vendors in the entire game. Nobody could buy a bomb, a grapple launcher or a quiver of heavy
arrows anywhere. Booty Bay is a goblin port and Dealer Sark says "I do not ask what for, I do ask for
coin first", so that is where they go. Grom'gol's weaponsmith gets the ammo, because a garrison
issues arrows.

Standard potions and elixirs are also replaced with the superior and greater tiers across the board.
Both towns sit at levels 30-42 and the standard tier caps out below that, so every shop in the
region was selling a healing potion the player had outgrown before arriving.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

VENDORS = ROOT / "data/npcs/vendors.json"

#: vendor_id -> (sells, sells_gear, gear_level or None to leave alone, why this shelf)
#:
#: GROM'GOL is a garrison at the end of a supply line: nothing here was chosen, it was issued or it
#: came up the stair off an airship. Levels 30-34.
#: BOOTY BAY is a goblin port where everything came off a boat that was going somewhere else, and
#: nobody asks what for. Levels 38-42.
SHOPS = {
    # ---- Grom'gol -------------------------------------------------------------------------------
    "gromgol_quartermaster": (
        # "Signed for, issued, and I want it back." Issued kit, and the only place in camp that
        # hands out armour. A quartermaster is a gear vendor by the engine's own policy.
        ["healing_potion_superior", "mana_potion_superior", "guardian_elixir_superior",
         "meal_trailbread", "meal_tough_jerky", "drink_waterskin",
         "whetstone", "flux_medium"],
        True, 33,
        "issued kit: field rations, the two potions a sentry carries, and the armoury",
    ),
    "gromgol_trader": (
        # "Whatever came up the stair this week, I have some of it." Trade goods off the airship -
        # the things the jungle cannot make. No food: that is Nakka's shelf, four metres away.
        ["parchment", "thread_coarse", "thread_fine", "vial_empty", "glue", "salt",
         "dye_mild", "bleach", "resin"],
        False, None,
        "airship freight: everything the jungle cannot make for itself",
    ),
    "gromgol_provisioner": (
        # "Eat before you go south. People forget." THE food vendor. All of Grom'gol's food and
        # drink lives here and nowhere else, which is the whole point of having her.
        ["bread_and_cheese", "roasted_meat", "spiced_stew", "meal_trailbread", "meal_tough_jerky",
         "meal_river_fish", "meal_spiced_haunch", "drink_waterskin", "drink_barley_beer",
         "drink_spring_flask"],
        False, None,
        "the camp's food, all of it, so nobody else has to carry bread",
    ),
    "gromgol_weaponsmith": (
        # "Oil it every night down here or it will not be yours by morning." Upkeep, ammunition and
        # actual weapons. He is a weaponsmith; he sells weapons now.
        ["whetstone", "flux_medium", "flux_strong", "coal", "sinew", "fletching",
         "component_string", "heavy_arrows", "heavy_bolts"],
        True, 33,
        "upkeep, ammunition and the rack - a garrison issues arrows",
    ),
    "gromgol_herbalist": (
        # "Half of what grows out there will kill you. I sell the other half." A troll herbalist in
        # a jungle sells what she picks and what she puts it in - reagents and glassware, not a
        # shelf of finished potions competing with the quartermaster.
        ["elixir_of_greater_agility", "elixir_of_greater_endurance", "elixir_of_ironskin",
         "elixir_of_the_sage", "vial_empty", "vial_leaded", "vial_crystal", "tanning_reagent"],
        False, None,
        "what she picks, and what she puts it in",
    ),
    # ---- Booty Bay ------------------------------------------------------------------------------
    "bootybay_trader": (
        # "Everything on this shelf came off a boat that was going somewhere else." Salvage: the
        # high tiers, because what a port skims off cargo is better than what a village makes.
        ["healing_potion_superior", "mana_potion_superior", "healing_potion_mega",
         "mana_potion_mega", "thread_silken", "vial_crystal", "parchment", "glue"],
        False, None,
        "salvage off other people's cargo, which is why it is better than it should be",
    ),
    "bootybay_tavern_keeper": (
        # "Drink it inside. What you spill out there, the tide keeps." A tavern. Food and drink,
        # the best in the region, and nothing else at all.
        ["spiced_wine", "spiced_stew", "mushroom_broth", "roasted_meat", "bread_and_cheese",
         "meal_cooked_feast_roast", "meal_kodo_ribs", "drink_barley_beer", "drink_honeyed_mead",
         "drink_birch_wine"],
        False, None,
        "a tavern: food, drink, and not one other thing",
    ),
    "bootybay_shipping_clerk": (
        # "Manifest, weight, destination. In that order or not at all." What you do to a crate:
        # pack it, seal it, cure what is in it, write what it is on the outside.
        ["parchment", "glue", "thread_coarse", "thread_silken", "curing_salt", "tanning_reagent",
         "salt", "resin", "vial_leaded"],
        False, None,
        "what you do to a crate before it goes on a hull",
    ),
    "bootybay_fishmonger": (
        # "Caught this morning. Some of it caught itself." Fish. He was selling roasted meat and
        # spiced haunch, which are not fish, which is how you can tell nobody chose this shelf.
        ["meal_river_fish", "mushroom_broth", "salt", "curing_salt", "drink_spring_flask"],
        False, None,
        "fish, and the salt to keep it - no haunches",
    ),
    "bootybay_weapon_dealer": (
        # "I do not ask what for. I do ask for coin first." Weapons, and the goblin hardware nobody
        # in the game sold: explosives, a grapple launcher, a repair bot. This is the only shelf in
        # Frontier where you can buy a bomb.
        ["bomb_sapper", "bomb_ember_cluster", "bomb_emberglass", "bomb_voidsplit",
         "device_grapple", "device_repair_bot", "heavy_arrows", "shot_charged",
         "flux_strong", "whetstone"],
        True, 38,
        "weapons, bombs and goblin hardware - the only place in Frontier selling any of it",
    ),
}


def valid_ids():
    """Every id that resolves: consumables, plus the trade-goods ids other towns already sell."""
    cons = set()
    for _cat, rows in json.loads(
            (ROOT / "data/consumables/consumable_types.json").read_text(encoding="utf-8")).items():
        for row in rows:
            if row.get("consumable_id"):
                cons.add(row["consumable_id"])
    doc = json.loads(VENDORS.read_text(encoding="utf-8"))
    supplies = {i for v in doc["vendors"] for i in v["sells"]} - cons
    return cons | supplies


def report(doc):
    """Print the region's shelves and return the number of problems."""
    by_id = {v["vendor_id"]: v for v in doc["vendors"]}
    known = valid_ids()
    bad = 0

    from collections import Counter
    spread = Counter(i for vid in SHOPS for i in by_id[vid]["sells"])
    dup = {i: n for i, n in spread.items() if n >= 4}

    print(f"{'vendor':30}{'gear':6}{'n':4}shelf")
    for vid, (_sells, _gear, _lvl, _why) in SHOPS.items():
        v = by_id.get(vid)
        if v is None:
            print(f"  {vid:28} -- MISSING FROM vendors.json --")
            bad += 1
            continue
        unknown = [i for i in v["sells"] if i not in known]
        flag = "GEAR" if v.get("sells_gear") else "-"
        print(f"  {v['name']:28}{flag:6}{len(v['sells']):<4}{', '.join(v['sells'][:5])}...")
        if unknown:
            print(f"      unresolvable ids: {unknown}")
            bad += 1

    if dup:
        print(f"\n{len(dup)} item(s) on 4+ of the 10 shelves - the generic-shop signature:")
        for i, n in sorted(dup.items(), key=lambda kv: -kv[1]):
            print(f"   {n}x  {i}")
        bad += len(dup)

    gear_vendors = [by_id[v]["name"] for v in SHOPS if by_id.get(v, {}).get("sells_gear")]
    print(f"\ngear vendors: {len(gear_vendors)} ({', '.join(gear_vendors) or 'none'})")
    print(f"distinct items across the ten shelves: {len(spread)}  total slots: {sum(spread.values())}")
    return bad


def main():
    doc = json.loads(VENDORS.read_text(encoding="utf-8"))

    if "--check" in sys.argv:
        raise SystemExit(1 if report(doc) else 0)

    known = valid_ids()
    problems = []
    for vid, (sells, _g, _l, _why) in SHOPS.items():
        for item in sells:
            if item not in known:
                problems.append(f"{vid}: {item!r} does not resolve to any consumable or supply id")
    if problems:
        for p in problems:
            print(f"  {p}")
        raise SystemExit("refusing to write unresolvable stock")

    by_id = {v["vendor_id"]: v for v in doc["vendors"]}
    missing = [v for v in SHOPS if v not in by_id]
    if missing:
        raise SystemExit(f"vendors not in vendors.json: {missing}")

    changed = 0
    for vid, (sells, sells_gear, gear_level, _why) in SHOPS.items():
        v = by_id[vid]
        before = (list(v["sells"]), v.get("sells_gear"), v.get("gear_level"))
        v["sells"] = list(sells)
        v["sells_gear"] = sells_gear
        if gear_level is not None:
            v["gear_level"] = gear_level
        if before != (list(v["sells"]), v.get("sells_gear"), v.get("gear_level")):
            changed += 1

    VENDORS.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"rewrote {changed} of {len(SHOPS)} shelves\n")
    if report(doc):
        raise SystemExit("a shelf is still wrong after the pass")


if __name__ == "__main__":
    main()
