#!/usr/bin/env python3
"""Give Astranaar and Splintertree Post real vendors.

Kyle, 2026-10-31: "Each town should have vendors, yes."

Found while building the map's vendor icon: these two were the only TOWNS in the
game with no vendor at all. Both already had shop-flavoured AMBIENT NPCs - a
"Sentinel Weaponsmith", an "Astranaar Outfitter", a "Quartermaster" - standing
in the right places with nothing to sell. Which is worse than having no shop,
because the player walks up to the Outfitter and the Outfitter has no shop.

So this CONVERTS those three rather than adding new bodies beside them: the
ambient entry is removed and a real vendor takes its exact tile, keeping the
name, race and appearance the town was built with. Two provisioners are added
per town on top, since one weapon rack is not a town's worth of trade.

Every tile is checked walkable against the real generated zone, and every
consumable id is checked against ConsumableManager, because an invented id
would make a vendor that opens an empty shop - the same silent shape as having
no vendor at all.
"""
import sys, os, json, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent

#: Ashenvale sits around level 19-30, so stock is the "standard" band with a
#: little "superior" at the quartermasters - matching what Camp Taurajo and the
#: Ashenvale East fence already sell at this level.
PROVISIONS = ["healing_potion_minor", "healing_potion_standard", "mana_potion_minor",
              "mana_potion_standard", "meal_trailbread", "meal_river_fish",
              "drink_waterskin", "drink_spring_flask"]
FIELD_KIT = ["healing_potion_standard", "mana_potion_standard", "guardian_elixir_standard",
             "battle_elixir_standard", "elixir_of_fortitude", "meal_spiced_haunch",
             "drink_honeyed_mead", "sturdy_arrows", "rough_arrows"]
REAGENTS = ["vial_empty", "thread_coarse", "flux_weak", "parchment",
            "healing_potion_minor", "meal_tough_jerky", "drink_barley_beer"]

#: (vendor_id, name, zone_slug, x, y, race, variant, sells, gear_level, sells_gear,
#:  greeting, replaces_ambient_npc_id)
NEW = [
    # ---- Astranaar (night elf Sentinel town) ------------------------------------------
    ("astranaar_weaponsmith", "Sentinel Weaponsmith", "astranaar", 40, 53, "night_elf", 4,
     FIELD_KIT, 26, True,
     "Sentinel issue. It is maintained, it is sharp, and I will know if you neglect it.",
     "astranaar_weapon_vendor"),
    ("astranaar_outfitter", "Astranaar Outfitter", "astranaar", 40, 60, "night_elf", 6,
     REAGENTS, 26, True,
     "Everything here is cut for someone who has to move in it. Try it before you buy it.",
     "astranaar_armor_vendor"),
    ("astranaar_provisioner", "Provisioner Shaldrissa", "astranaar", 80, 55, "night_elf", 9,
     PROVISIONS, 14, False,
     "Food, water, and something for the pain. In that order, usually.",
     None),

    # ---- Splintertree Post (Horde outpost) --------------------------------------------
    ("splintertree_quartermaster_shop", "Quartermaster Huln", "splintertree_post", 67, 43,
     "tauren", 3, FIELD_KIT, 26, True,
     "The Overseer signs for it, you carry it, and it comes back in one piece. That is the arrangement.",
     "splintertree_quartermaster"),
    ("splintertree_provisioner", "Cook Grishna", "splintertree_post", 64, 59, "orc", 5,
     PROVISIONS, 14, False,
     "Eat before you go out. I am not sending anybody into that forest hungry.",
     None),
    ("splintertree_supplier", "Supplier Vokk", "splintertree_post", 72, 45, "orc", 8,
     REAGENTS, 22, False,
     "Rope, thread, flux, parchment. Unglamorous, and you will be back for all four.",
     None),
]

ZONE_OF_SLUG = {"astranaar": "Astranaar", "splintertree_post": "Splintertree Post"}


def main():
    from world.zone_generator import create_all_zones
    from entities.consumable_manager import get_consumable_manager

    zones = create_all_zones()
    cm = get_consumable_manager()
    materials = set(json.load(open(ROOT / "data/gathering/materials.json", encoding="utf-8"))["materials"])

    vpath = ROOT / "data/npcs/vendors.json"
    apath = ROOT / "data/npcs/ambient_npcs.json"
    vdoc = json.load(open(vpath, encoding="utf-8"))
    adoc = json.load(open(apath, encoding="utf-8"))

    existing = {v["vendor_id"] for v in vdoc["vendors"]}
    problems = []

    # --- validate before writing anything ---------------------------------------------
    for (vid, name, slug, x, y, race, variant, sells, glev, gear, greet, repl) in NEW:
        z = zones[ZONE_OF_SLUG[slug]]
        if not (0 <= x < z.width and 0 <= y < z.height):
            problems.append(f"{vid}: ({x},{y}) outside {z.name} {z.width}x{z.height}")
        elif z.collision_layer[y][x] is not None:
            problems.append(f"{vid}: ({x},{y}) is not walkable in {z.name}")
        # A vendor's `sells` list is not consumables-only: the crafting reagents
        # (vial_empty, thread_coarse, flux_weak, parchment) are gathering
        # MATERIALS, and Camp Taurajo's quartermaster already stocks them. So an
        # id is valid if ConsumableManager knows it OR it is a real material.
        # The first version of this check only asked ConsumableManager and
        # refused to write - which is the check doing its job, since the
        # alternative was a shop that silently opens empty.
        bad = [s for s in sells if not cm.has_consumable(s) and s not in materials]
        if bad:
            problems.append(f"{vid}: ids that resolve to nothing {bad}")
        if vid in existing:
            problems.append(f"{vid}: vendor_id already exists")

    if problems:
        print("REFUSING TO WRITE - validation failed:")
        for p in problems:
            print("   ", p)
        return 1

    # --- apply -------------------------------------------------------------------------
    replaced = [r for *_rest, r in NEW if r]
    before_amb = len(adoc["npcs"]) if isinstance(adoc.get("npcs"), list) else None
    if before_amb is None:
        print("unexpected ambient_npcs shape"); return 1
    adoc["npcs"] = [n for n in adoc["npcs"]
                            if n.get("npc_id") not in replaced]
    removed = before_amb - len(adoc["npcs"])

    for (vid, name, slug, x, y, race, variant, sells, glev, gear, greet, repl) in NEW:
        vdoc["vendors"].append({
            "vendor_id": vid, "name": name, "zone": slug, "x": x, "y": y,
            "tile_sprite": "npc", "sells": list(sells), "buys_from_player": True,
            "faction": "alliance" if slug == "astranaar" else "horde",
            "gear_level": glev, "sells_gear": gear, "race": race,
            "appearance_variant": variant, "greeting": greet,
        })

    json.dump(vdoc, open(vpath, "w", encoding="utf-8"), indent=2)
    json.dump(adoc, open(apath, "w", encoding="utf-8"), indent=2)
    print(f"added {len(NEW)} vendors; removed {removed} decorative ambient shopkeepers "
          f"they replace ({', '.join(replaced)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
