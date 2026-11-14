"""Fishing: a secondary profession that feeds Cooking and Alchemy.

    python3 tools/build_fishing.py [--pack "<WoW Icon Pack dir>"]

Kyle, 13 Nov 2026: "with things like cooking and fishing, these can be learnt as secondary
without using profession slots. I guess fishing can feed a bunch into cooking too. Also alchemy."

What this writes (safe to re-run; everything it made before is replaced, not added to):
  - professions.json     fishing, kind "secondary" (no slot, like Cooking)
  - trainers.json        every trainer who teaches Cooking also teaches Fishing
  - materials.json       22 fish (skill 1-280, the pre-60 ladder) and three fish oils
  - node_pools.json      a "fishing" pool for every zone with a real shoreline: the fish whose
                         skill fits the zone's level, the same window the other nodes use
  - recipes.json         one cooked dish per fish (Cooking) and oils + three elixirs (Alchemy)
  - consumable_types     the dishes and the elixirs
  - icons                from the WoW pack's 76 fish icons, when --pack is given

Fishing spots are gathering nodes on a shore tile (world/gathering_manager.py); you fish by
stepping on one, the same as picking a herb.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

#: id, name, skill, pack icon number, description
FISH = [
    ("fish_brilliant_smallfish", "Brilliant Smallfish", 1, "02", "Silver, quick, and gone the moment your shadow crosses the water."),
    ("fish_slitherskin_mackerel", "Slitherskin Mackerel", 1, "01", "Oily and plentiful. The first fish anybody catches."),
    ("fish_longjaw_mud_snapper", "Longjaw Mud Snapper", 25, "03", "Lives in the silt and tastes of it until you soak it."),
    ("fish_bristle_whisker_catfish", "Bristle Whisker Catfish", 50, "31", "All mouth and whiskers. Fights like a much bigger fish."),
    ("fish_loch_frenzy", "Loch Frenzy", 60, "25", "Teeth first. Mind your fingers getting the hook out."),
    ("fish_rainbow_fin_albacore", "Rainbow Fin Albacore", 75, "08", "The fins catch the light. The meat is firm and clean."),
    ("fish_sagefish", "Sagefish", 90, "04", "Shamans say eating one clears the head. Cooks agree."),
    ("fish_oily_blackmouth", "Oily Blackmouth", 105, "11", "Too greasy to eat. Alchemists press it for the oil."),
    ("fish_deviate_fish", "Deviate Fish", 115, "53", "Something in the water has got into it. Cook it thoroughly."),
    ("fish_firefin_snapper", "Firefin Snapper", 130, "36", "Warm to the touch for an hour after it is landed."),
    ("fish_rockscale_cod", "Rockscale Cod", 140, "28", "Scales like slate. Blunts a knife and is worth it."),
    ("fish_mithril_head_trout", "Mithril Head Trout", 155, "35", "The skull shines like the metal. Nobody knows why."),
    ("fish_greater_sagefish", "Greater Sagefish", 165, "39", "Older, deeper, and harder to fool than its cousin."),
    ("fish_spotted_yellowtail", "Spotted Yellowtail", 180, "19", "A strong swimmer from warm water. Good on a grill."),
    ("fish_stonescale_eel", "Stonescale Eel", 195, "47", "Comes up at night. The skin gives a grey oil that hardens."),
    ("fish_redgill", "Redgill", 205, "42", "Bright as a wound. Sweet under the skin."),
    ("fish_nightfin_snapper", "Nightfin Snapper", 215, "23", "Only bites after dark. Eating one settles the mind."),
    ("fish_sunscale_salmon", "Sunscale Salmon", 225, "43", "Only bites by day. Runs upriver gold."),
    ("fish_winter_squid", "Winter Squid", 235, "13", "Cold-water catch. Tough until you beat it flat."),
    ("fish_glossy_mightfish", "Glossy Mightfish", 250, "46", "Heavy, slow and stubborn. Takes two hands to land."),
    ("fish_darkclaw_lobster", "Darkclaw Lobster", 265, "14", "Not a fish. Nobody who has eaten one cares."),
    ("fish_lightning_eel", "Lightning Eel", 280, "37", "Wear gloves. Wear them afterwards too."),
]
#: the stat a fish dish gives, cycling so neighbours on the ladder differ: meat dishes already
#: cover stamina, spirit, attack power, spell power, healing and armour
DISH_STATS = ["agility", "intellect", "strength"]
#: fish -> (dish name, pantry input, flavour)
DISHES = {
    "fish_brilliant_smallfish": ("Fried Smallfish", "cook_flour", "A handful, floured and fried whole."),
    "fish_slitherskin_mackerel": ("Smoked Mackerel", "cook_spice", "Smoked hard so it keeps in a pack."),
    "fish_longjaw_mud_snapper": ("Mud Snapper Fillet", "cook_roots", "Soaked, then baked on roots."),
    "fish_bristle_whisker_catfish": ("Whisker Catfish Stew", "cook_water", "Thick, grey and far better than it looks."),
    "fish_loch_frenzy": ("Frenzy Skewers", "cook_spice", "The teeth come out first."),
    "fish_rainbow_fin_albacore": ("Seared Albacore", "cook_ale", "Seared hard and left pink."),
    "fish_sagefish": ("Sagefish Delight", "cook_honey", "Glazed, and it does clear the head."),
    "fish_deviate_fish": ("Savory Deviate Delight", "cook_spice", "Spiced until whatever was in it gives up."),
    "fish_firefin_snapper": ("Firefin Chowder", "cook_cheese", "Still warm from the fish before it meets the fire."),
    "fish_rockscale_cod": ("Rockscale Cod Pie", "cook_flour", "Slate-scaled fish under a crust."),
    "fish_mithril_head_trout": ("Mithril Head Trout", "cook_roots", "Baked whole. Leave the head."),
    "fish_greater_sagefish": ("Sagefish Feast", "cook_honey", "The big one, done properly."),
    "fish_spotted_yellowtail": ("Grilled Yellowtail", "cook_spice", "Straight onto the coals."),
    "fish_redgill": ("Redgill Steak", "cook_ale", "Cut thick across the bone."),
    "fish_nightfin_snapper": ("Nightfin Soup", "cook_water", "Dark broth. Drink it slowly."),
    "fish_sunscale_salmon": ("Poached Sunscale Salmon", "cook_fruit", "Poached with fruit until it flakes."),
    "fish_winter_squid": ("Winter Squid Fry", "cook_flour", "Beaten flat, floured, and fried fast."),
    "fish_glossy_mightfish": ("Mightfish Steak", "cook_spice", "A slab of it. Feeds a party."),
    "fish_darkclaw_lobster": ("Lobster Stew", "cook_cheese", "Rich enough to slow you down."),
    "fish_lightning_eel": ("Charred Lightning Eel", "cook_spice", "Charred until it stops twitching."),
}
#: oil id -> (name, fish, description)
OILS = {
    "oil_blackmouth": ("Blackmouth Oil", "fish_oily_blackmouth", "Pressed from Oily Blackmouth. Slick, dark, and it never quite washes off."),
    "oil_fire": ("Fire Oil", "fish_firefin_snapper", "Rendered from Firefin Snapper. Keep it away from lamps."),
    "oil_stonescale": ("Stonescale Oil", "fish_stonescale_eel", "From the skin of a Stonescale Eel. Sets hard on whatever it touches."),
}
#: elixir id -> (name, oil, herb, skill, required level, stat, description)
ELIXIRS = {
    "elixir_of_the_current": ("Elixir of the Current", "oil_blackmouth", "herb_stranglekelp", 120, 22, "haste",
                              "Slick as the fish it came from. You move like water."),
    "elixir_of_the_firefin": ("Elixir of the Firefin", "oil_fire", "herb_kingsblood", 145, 28, "spell_power",
                              "Warm going down, and warmer in the hands."),
    "elixir_of_stonescale": ("Elixir of Stonescale", "oil_stonescale", "herb_goldthorn", 205, 40, "armor",
                             "Your skin takes on a grey sheen and turns a blade."),
}
MINE = ("fishx_",)          # recipe id prefixes this tool owns


def window(lo, hi):
    return max(0, (lo - 15) * 5), hi * 5


def shore_counts():
    """{zone name: number of walkable tiles beside water} on the live overworld maps."""
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import pygame
    pygame.init()
    pygame.display.set_mode((64, 64))
    from world.zone_manager import ZoneManager
    from world.gathering_manager import shore_tiles
    from world.zone_classification import is_dungeon
    out = {}
    for name, z in ZoneManager().zones.items():
        tm = z["tilemap"]
        if getattr(tm, "is_town", False) or is_dungeon(name):
            continue
        out[name] = len(shore_tiles(tm))
    return out


def main():
    import build_cooking_expansion as C
    from world.zone_keys import zone_key
    C.LABEL.update({"agility": "Agility", "intellect": "Intellect", "strength": "Strength", "haste": "% Haste"})
    pack = Path(sys.argv[sys.argv.index("--pack") + 1]) if "--pack" in sys.argv else None
    load = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
    save = lambda p, d: (ROOT / p).write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # --- the profession and who teaches it
    prof = load("data/professions/professions.json")
    prof["professions"]["fishing"] = {
        "kind": "secondary", "name": "Fishing",
        "description": "Catch fish at the water's edge. They go into the cook's pot and the alchemist's press."}
    save("data/professions/professions.json", prof)
    tr = load("data/training/trainers.json")
    taught = 0
    for npc, v in tr["profession_trainers"].items():
        if isinstance(v, list) and "cooking" in v and "fishing" not in v:
            v.append("fishing")
        taught += isinstance(v, list) and "fishing" in v
    save("data/training/trainers.json", tr)

    # --- materials
    md = load("data/gathering/materials.json")
    mats = md["materials"]
    for k in [k for k, v in mats.items() if v.get("material_type") == "fish" or k in OILS]:
        del mats[k]
    for fid, name, skill, _icon, desc in FISH:
        mats[fid] = {"name": name, "material_type": "fish", "profession": "fishing",
                     "tier": "early" if skill < 100 else ("mid" if skill < 200 else "late"),
                     "description": desc, "stack_limit": 20, "sell_price": max(4, round(4 + skill * 0.45)),
                     "icon_id": fid[5:], "skill_range": [skill, skill + 25, skill + 50, skill + 75]}
    for oid, (name, _fish, desc) in OILS.items():
        mats[oid] = {"name": name, "material_type": "reagent", "profession": "alchemy", "tier": "mid",
                     "description": desc, "stack_limit": 20, "sell_price": 60, "icon_id": oid}
    save("data/gathering/materials.json", md)

    # --- where they are caught
    levels = {zone_key(k): v for k, v in load("data/zones/zone_levels.json")["zones"].items()}
    pools = load("data/gathering/node_pools.json")
    shores = shore_counts()
    zones_with = 0
    for z in pools["zones"].values():
        z.pop("fishing", None)
    for name, n in sorted(shores.items()):
        key = zone_key(name)
        lv = levels.get(key)
        if n < 25 or lv is None:
            continue
        s_lo, s_hi = window(*lv)
        fits = [(fid, skill) for fid, _n, skill, _i, _d in FISH if s_lo <= skill <= s_hi]
        if not fits:
            continue
        fits = sorted(fits, key=lambda f: -f[1])[:4]            # the four best the zone can hold
        pool = pools["zones"].setdefault(key, {"slots": 0, "active_percent": 0.0, "table": {}})
        pool["fishing"] = {"slots": max(4, min(14, n // 60)), "active_percent": 0.6,
                           "table": {fid: 3 if i else 2 for i, (fid, _s) in enumerate(fits)}}
        zones_with += 1
    save("data/gathering/node_pools.json", pools)
    # Caves and dungeons take their node pool from elsewhere (or none at all), so a fishing pool
    # there would never spawn. Keep only the pools that really put a spot on a shore.
    import world.gathering_manager as GM
    from world.zone_manager import ZoneManager
    GM._gathering_node_manager = None
    gm, zm = GM.get_gathering_node_manager(), ZoneManager()
    for name, z in zm.zones.items():
        key = zone_key(name)
        if not pools["zones"].get(key, {}).get("fishing"):
            continue
        tm = z["tilemap"]
        gm.populate(tm, name)
        if not any(mats.get(n.material_id, {}).get("material_type") == "fish" for n in gm.active_nodes):
            del pools["zones"][key]["fishing"]
            if not pools["zones"][key].get("table"):
                del pools["zones"][key]
            zones_with -= 1
        gm.clear()
    save("data/gathering/node_pools.json", pools)
    GM._gathering_node_manager = None

    # --- what they are for
    rd = load("data/crafting/recipes.json")
    cook = rd["professions"]["cooking"]
    cook = cook["recipes"] if "recipes" in cook else cook
    alch = rd["professions"]["alchemy"]
    alch = alch["recipes"] if "recipes" in alch else alch
    cd = load("data/consumables/consumable_types.json")
    for book in (cook, alch):
        for rid in [r for r in book if r.startswith(MINE)]:
            del book[rid]
    made = set()
    meals, elixirs = [], []
    for i, (fid, name, skill, icon, _d) in enumerate(FISH):
        if fid not in DISHES:
            continue
        dish, pantry, flavour = DISHES[fid]
        level = max(1, skill // 5)
        tier = min(C.TIERS, key=lambda t: abs(t[1] - level))
        tier = (tier[0], level, tier[2], tier[3], tier[4], max(6, round(6 + skill * 0.35)))
        stat = DISH_STATS[len(meals) % len(DISH_STATS)]
        cid = f"meal_cooked_{C.slug(dish)}"
        meals.append((C.meal(cid, dish, flavour, tier, {stat: 3 + round(level * 0.3)}), icon))
        made.add(cid)
        rskill = min(300, skill + 5)
        cook[f"fishx_{C.slug(dish)}"] = {
            "name": dish, "skill_required": rskill, "inputs": {fid: 1, pantry: 1}, "source": "trainer",
            "skill_range": [rskill + 5, rskill + 15, rskill + 25, rskill + 35],
            "output": {"kind": "consumable", "consumable_id": cid, "count": 1}}
    existing = [e for e in cd["elixirs"] if e["consumable_id"] not in ELIXIRS]
    for oid, (name, fish, _desc) in OILS.items():
        skill = next(s for f, _n, s, _i, _d in FISH if f == fish)
        alch[f"fishx_{oid}"] = {"name": name, "skill_required": skill, "inputs": {fish: 2, "vial_empty": 1},
                                "source": "trainer", "count": 1,
                                "skill_range": [skill + 5, skill + 15, skill + 25, skill + 35],
                                "output": {"kind": "material", "material_id": oid}}
    for eid, (name, oil, herb, skill, level, stat, desc) in ELIXIRS.items():
        # the same strength as the nearest elixir of that stat already in the game: a second
        # way to make it, not a better one
        same = [e for e in existing if list((e.get("stat_bonuses") or {}).keys()) == [stat]]
        ref = min(same, key=lambda e: abs(e.get("required_level", 1) - level))
        value = ref["stat_bonuses"][stat]
        label = C.LABEL.get(stat, stat.replace("_", " ").title())
        text = f"+{value}{label}" if label.startswith("%") else f"+{value} {label}"
        elixirs.append({"consumable_id": eid, "name": name, "consumable_type": "elixir",
                        "description": f"{desc} {text} for 30 min. {ref.get('buff_category', 'battle').title()} buff.",
                        "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0,
                        "required_level": level, "cooldown_seconds": 5, "stack_limit": 20,
                        "vendor_price": ref.get("vendor_price", 400), "sell_price": ref.get("sell_price", 100),
                        "buff_category": ref.get("buff_category", "battle"), "stat_bonuses": {stat: value}})
        alch[f"fishx_{eid}"] = {"name": name, "skill_required": skill, "inputs": {oil: 1, herb: 1, "vial_leaded": 1},
                                "source": "trainer", "count": 1,
                                "skill_range": [skill + 5, skill + 15, skill + 25, skill + 35],
                                "output": {"kind": "consumable", "consumable_id": eid}}
    cd["cooked_meals"] = [m for m in cd["cooked_meals"] if m["consumable_id"] not in made] + [m for m, _i in meals]
    cd["elixirs"] = existing + elixirs
    save("data/crafting/recipes.json", rd)
    save("data/consumables/consumable_types.json", cd)

    copied = 0
    if pack is not None:
        from PIL import Image
        src = pack / "Miscellaneous"
        (ROOT / "assets/gathering_nodes/fish").mkdir(parents=True, exist_ok=True)
        jobs = [(ROOT / f"assets/gathering_nodes/fish/{fid[5:]}.png", f"Fish_{icon}.png", 64) for fid, _n, _s, icon, _d in FISH]
        cooked = ["16", "17", "18", "15"]
        jobs += [(ROOT / f"assets/icons/consumables/{m['consumable_id']}.png", f"Fish_{cooked[i % 4]}.png", 96)
                 for i, (m, _icon) in enumerate(meals)]
        for dest, name, size in jobs:
            if (src / name).is_file():
                dest.parent.mkdir(parents=True, exist_ok=True)
                Image.open(src / name).convert("RGBA").resize((size, size), Image.LANCZOS).save(dest)
                copied += 1
    print(f"fishing: {len(FISH)} fish, {zones_with} zones with fishing spots, {len(meals)} dishes, "
          f"{len(OILS)} oils, {len(ELIXIRS)} elixirs, taught by {taught} trainers, {copied} icons")


if __name__ == "__main__":
    main()
