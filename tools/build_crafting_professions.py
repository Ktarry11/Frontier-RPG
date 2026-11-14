#!/usr/bin/env python3
"""Crafting professions data (Oct 2026): Alchemy, Tailoring, Woodworking + the Sawmill (logs -> planks).

Idempotent.  Writes / merges:
  data/gathering/materials.json      mid herbs + woods, planks, fiber, pages, cloth, bolts, upgrade kits
  data/gathering/node_pools.json     mid herbs / woods in the zones that should have them
  data/consumables/consumable_types.json   "ammo" list (arrows / bolts; a timed buff, there is no ammo mechanic)
  data/crafting/recipes.json         every recipe for the four stations below
  data/professions/professions.json  profession list, tiers (caps, costs)

Run from the repo root:   python3 tools/build_crafting_professions.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load(p):
    return json.loads((ROOT / p).read_text(encoding="utf-8"))


def save(p, d, indent=2, nl=True):
    (ROOT / p).write_text(json.dumps(d, indent=indent) + ("\n" if nl else ""), encoding="utf-8")


# ------------------------------------------------------------------------------------------------ materials
def sr(lo):
    """skill_range [orange, yellow, green, grey] spaced like the existing materials."""
    return [lo, lo + 20, lo + 35, lo + 50]


MATERIALS = {
    # ---- mid herbs (Alchemy) - art already staged in assets/gathering_nodes/herbs
    "herb_bruiseweed": dict(name="Bruiseweed", material_type="herb", profession="herbalism", tier="mid", icon_id="bruiseweed",
                            description="A thick, purple-veined stem. It stains your fingers and cures most of what ails you.", sell_price=10, skill_range=sr(45)),
    "herb_liferoot": dict(name="Liferoot", material_type="herb", profession="herbalism", tier="mid", icon_id="liferoot",
                          description="A pale root that bleeds a warm, sweet sap when torn.", sell_price=12, skill_range=sr(55)),
    "herb_kingsblood": dict(name="Kingsblood", material_type="herb", profession="herbalism", tier="mid", icon_id="kingsblood",
                            description="Crimson petals on a tall stalk. Said to grow only where a king once fell.", sell_price=14, skill_range=sr(60)),
    "herb_goldthorn": dict(name="Goldthorn", material_type="herb", profession="herbalism", tier="mid", icon_id="goldthorn",
                           description="A bramble tipped with golden thorns. Rare, and well worth the scratches.", sell_price=16, skill_range=sr(70)),
    # ---- mid woods (Woodcutting) - art already staged in assets/gathering_nodes/wood
    "wood_ironbark_stump": dict(name="Ironbark Stump", material_type="wood", profession="woodcutting", tier="mid", icon_id="ironbark_stump",
                                description="Dense, dark timber that blunts axes and arrows alike.", sell_price=12, skill_range=sr(45)),
    "wood_frostpine": dict(name="Frostpine", material_type="wood", profession="woodcutting", tier="mid", icon_id="frostpine",
                           description="A pale pine that never quite thaws, even in summer.", sell_price=14, skill_range=sr(55)),
    "wood_bramblewood": dict(name="Bramblewood", material_type="wood", profession="woodcutting", tier="mid", icon_id="bramblewood",
                             description="Thorny, tough and stubbornly alive long after it is cut.", sell_price=16, skill_range=sr(65)),
}

# planks (sawmill): id, wood id, name, tier, skill to saw, sell
PLANKS = [
    ("plank_softpine", "wood_softpine", "Softpine Plank", "early", 0, 6),
    ("plank_ashwood", "wood_ashwood", "Ashwood Plank", "early", 0, 7),
    ("plank_oakheart", "wood_oakheart_stump", "Oakheart Plank", "early", 15, 9),
    ("plank_driftwood", "wood_driftwood_stump", "Driftwood Plank", "early", 25, 10),
    ("plank_ironbark", "wood_ironbark_stump", "Ironbark Plank", "mid", 50, 15),
    ("plank_frostpine", "wood_frostpine", "Frostpine Plank", "mid", 60, 17),
    ("plank_bramblewood", "wood_bramblewood", "Bramblewood Plank", "mid", 70, 19),
]
for pid, wood, name, tier, req, price in PLANKS:
    MATERIALS[pid] = dict(name=name, material_type="plank", profession="woodcutting", tier=tier, icon_id=pid,
                          description="Sawn and planed at a sawmill. The start of every bow, shield and staff.", sell_price=price,
                          skill_range=[req + 5, req + 20, req + 35, req + 50])

# woodworking intermediates (plank -> fiber / pages).  Three bands, so three art sets each.
FIBERS = {"fiber_coarse": ("Coarse Fiber", 3, "Stringy fibre rasped from soft planks. Good for bowstrings and cordage."),
          "fiber_supple": ("Supple Fiber", 6, "Long, pliable fibres. Strong enough for a longbow."),
          "fiber_tough": ("Tough Fiber", 11, "Wiry fibre pulled from heartwood. It will not snap.")}
PAGES = {"pages_rough": ("Rough Pages", 3, "Thin wood-pulp sheets, pressed flat. Ink bleeds a little."),
         "pages_pressed": ("Pressed Pages", 6, "Smooth, tightly pressed pages that take ink well."),
         "pages_fine": ("Fine Pages", 11, "Pale, durable pages fit for a scholar's tome.")}
for mid, (name, price, desc) in FIBERS.items():
    MATERIALS[mid] = dict(name=name, material_type="fiber", profession="woodworking", tier="early" if mid != "fiber_tough" else "mid",
                          icon_id=mid, description=desc, sell_price=price, skill_range=None)
for mid, (name, price, desc) in PAGES.items():
    MATERIALS[mid] = dict(name=name, material_type="pages", profession="woodworking", tier="early" if mid != "pages_fine" else "mid",
                          icon_id=mid, description=desc, sell_price=price, skill_range=None)

# cloth (dropped by humanoids) and bolts (tailoring)
MATERIALS["cloth_linen"] = dict(name="Linen Cloth", material_type="cloth", profession="tailoring", tier="early", icon_id="cloth_linen",
                                description="Coarse cloth cut from the clothes of fallen humanoids.", sell_price=4, skill_range=None)
MATERIALS["cloth_wool"] = dict(name="Wool Cloth", material_type="cloth", profession="tailoring", tier="mid", icon_id="cloth_wool",
                               description="Warm, heavy cloth. It smells faintly of sheep.", sell_price=9, skill_range=None)
MATERIALS["cloth_silk"] = dict(name="Silk Cloth", material_type="cloth", profession="tailoring", tier="mid", icon_id="cloth_silk",
                               description="Fine, smooth cloth with a faint shimmer.", sell_price=16, skill_range=None)
MATERIALS["bolt_linen"] = dict(name="Bolt of Linen Cloth", material_type="bolt", profession="tailoring", tier="early", icon_id="bolt_linen",
                               description="Linen cloth woven into a tight bolt.", sell_price=9, skill_range=[5, 20, 35, 50])
MATERIALS["bolt_wool"] = dict(name="Bolt of Wool Cloth", material_type="bolt", profession="tailoring", tier="mid", icon_id="bolt_wool",
                              description="Wool cloth woven into a thick bolt.", sell_price=24, skill_range=[45, 60, 75, 90])
MATERIALS["bolt_silk"] = dict(name="Bolt of Silk Cloth", material_type="bolt", profession="tailoring", tier="mid", icon_id="bolt_silk",
                              description="Silk cloth woven into a gleaming bolt.", sell_price=52, skill_range=[95, 110, 125, 140])

# upgrade kits (every crafter makes their own)
KITS = {
    "upgrade_kit_linen": ("Linen Upgrade Kit", "tailoring", 22, "Needles and fine thread, used to refine any Linen-tier crafted item up one rarity rank. Only works on Tailored Linen gear."),
    "upgrade_kit_wool": ("Wool Upgrade Kit", "tailoring", 48, "A tailor's heavier kit for Wool-tier crafted items. Only works on Tailored Wool gear."),
    "upgrade_kit_silk": ("Silk Upgrade Kit", "tailoring", 95, "Silver needles and silk thread for Silk-tier crafted items. Only works on Tailored Silk gear."),
    "upgrade_kit_ashwood": ("Ashwood Upgrade Kit", "woodworking", 22, "Rasps, oils and a little glue, used to refine any Ashwood-tier crafted item up one rarity rank. Only works on Woodworked early-tier gear."),
    "upgrade_kit_ironbark": ("Ironbark Upgrade Kit", "woodworking", 60, "Heavier tools for dense timber, used to refine any Ironbark-tier crafted item up one rarity rank. Only works on Woodworked mid-tier gear."),
}
for kid, (name, prof, price, desc) in KITS.items():
    MATERIALS[kid] = dict(name=name, material_type="upgrade_kit", profession=prof, tier="kit", icon_id=kid, description=desc,
                          sell_price=price, skill_range=None)

# ---------------------------------------------------------------------------------------------- node pools
POOL_ADD = {
    # zone -> {material: weight}
    "central_barrens": {"herb_bruiseweed": 1},
    "southern_barrens": {"herb_bruiseweed": 2, "herb_liferoot": 1, "herb_kingsblood": 1, "wood_ironbark_stump": 1},
    "western_tirisfal": {"herb_bruiseweed": 1, "wood_ironbark_stump": 1},
    "eastern_tirisfal": {"herb_bruiseweed": 1, "wood_ironbark_stump": 1},
    "silverpine_north": {"herb_bruiseweed": 2, "herb_liferoot": 1, "herb_kingsblood": 1, "wood_ironbark_stump": 2, "wood_frostpine": 1},
    "silverpine_south": {"herb_bruiseweed": 2, "herb_liferoot": 2, "herb_kingsblood": 1, "herb_goldthorn": 1, "wood_ironbark_stump": 2, "wood_frostpine": 2},
    "ashenvale_west": {"herb_bruiseweed": 2, "herb_liferoot": 2, "herb_kingsblood": 2, "herb_goldthorn": 1, "wood_ironbark_stump": 2,
                       "wood_frostpine": 1, "wood_bramblewood": 2},
    "ashenvale_east": {"herb_bruiseweed": 2, "herb_liferoot": 2, "herb_kingsblood": 2, "herb_goldthorn": 2, "wood_ironbark_stump": 2,
                       "wood_frostpine": 2, "wood_bramblewood": 2},
}

# ---------------------------------------------------------------------------------------------- consumables
AMMO = [
    ("rough_arrows", "Rough Arrows", 1, 4, "Crude arrows for a bow."),
    ("rough_bolts", "Rough Bolts", 1, 4, "Crude bolts for a crossbow."),
    ("sturdy_arrows", "Sturdy Arrows", 15, 9, "Well-fletched arrows with sharpened heads."),
    ("sturdy_bolts", "Sturdy Bolts", 15, 9, "Straight, weighted bolts with iron tips."),
    ("heavy_arrows", "Heavy Arrows", 30, 15, "Broad-headed arrows that hit like a hammer."),
    ("heavy_bolts", "Heavy Bolts", 30, 15, "Heavy bolts that punch through plate."),
]


def ammo_defs():
    out = []
    for cid, name, lvl, ap, flavor in AMMO:
        out.append({"consumable_id": cid, "name": name, "consumable_type": "ammo",
                    "description": f"{flavor} Grants +{ap} Attack Power for 30 minutes. Ammo buff (one quiver at a time).",
                    "effect_value": 0, "effect_duration": 1800, "level_multiplier": 0.0, "required_level": lvl,
                    "cooldown_seconds": 5, "stack_limit": 20, "vendor_price": ap * 6, "sell_price": ap * 2,
                    "buff_category": "ammo", "stat_bonuses": {"attack_power": ap}})
    return out


# ---------------------------------------------------------------------------------------------- recipes
def il(req):
    return max(1, round(3 + req * 0.2))


def rarity_for(req, big=False):
    if req >= 120 and big:
        return "rare"
    if req >= 50:
        return "uncommon"
    return "common"


def recipes():
    R = {}

    def add(prof, rid, name, inputs, req, output, count=1, station=None):
        R.setdefault(prof, {})[rid] = {"name": name, "inputs": inputs, "skill_required": req, "output": output}
        if count != 1:
            R[prof][rid]["count"] = count
        if station:
            R[prof][rid]["station"] = station

    # ---- Sawmill (Woodcutting skill; at a Sawmill)
    for pid, wood, name, tier, req, _ in PLANKS:
        add("woodcutting", pid, name, {wood: 1}, req, {"kind": "material", "material_id": pid}, station="sawmill")

    # ---- Alchemy
    A = [
        ("alch_minor_healing", "Minor Healing Potion", {"herb_peacebloom": 1, "herb_silverleaf": 1}, 0, "healing_potion_minor"),
        ("alch_minor_mana", "Minor Mana Potion", {"herb_mageroyal": 1, "herb_dewgrass": 1}, 10, "mana_potion_minor"),
        ("alch_guardian_minor", "Minor Guardian Elixir", {"herb_silverleaf": 2, "herb_earthroot": 1}, 15, "guardian_elixir_minor"),
        ("alch_battle_minor", "Minor Battle Elixir", {"herb_earthroot": 2, "herb_peacebloom": 1}, 15, "battle_elixir_minor"),
        ("alch_agility", "Elixir of Agility", {"herb_fadeleaf": 2, "herb_dewgrass": 1}, 40, "elixir_of_agility"),
        ("alch_healing_standard", "Healing Potion", {"herb_bruiseweed": 1, "herb_briarthorn": 1}, 45, "healing_potion_standard"),
        ("alch_arcane", "Arcane Elixir", {"herb_mageroyal": 2, "herb_fadeleaf": 1}, 45, "arcane_elixir"),
        ("alch_mana_standard", "Mana Potion", {"herb_mageroyal": 2, "herb_briarthorn": 1}, 55, "mana_potion_standard"),
        ("alch_warding", "Elixir of Warding", {"herb_liferoot": 2, "herb_earthroot": 1}, 65, "elixir_of_warding"),
        ("alch_guardian_standard", "Guardian Elixir", {"herb_liferoot": 1, "herb_kingsblood": 1}, 75, "guardian_elixir_standard"),
        ("alch_battle_standard", "Battle Elixir", {"herb_kingsblood": 1, "herb_bruiseweed": 1}, 80, "battle_elixir_standard"),
        ("alch_firepower", "Elixir of Firepower", {"herb_goldthorn": 1, "herb_briarthorn": 1}, 100, "elixir_of_firepower"),
        ("alch_healing_superior", "Superior Healing Potion", {"herb_kingsblood": 2, "herb_liferoot": 2}, 110, "healing_potion_superior"),
        ("alch_mana_superior", "Superior Mana Potion", {"herb_goldthorn": 2, "herb_kingsblood": 1}, 115, "mana_potion_superior"),
        ("alch_battle_superior", "Superior Battle Elixir", {"herb_goldthorn": 2, "herb_bruiseweed": 1}, 125, "battle_elixir_superior"),
        ("alch_guardian_superior", "Superior Guardian Elixir", {"herb_goldthorn": 2, "herb_liferoot": 2}, 125, "guardian_elixir_superior"),
        ("alch_greater_arcane", "Greater Arcane Elixir", {"herb_goldthorn": 2, "herb_mageroyal": 2}, 135, "greater_arcane_elixir"),
        ("alch_greater_agility", "Elixir of Greater Agility", {"herb_goldthorn": 2, "herb_fadeleaf": 2}, 135, "elixir_of_greater_agility"),
    ]
    for rid, name, inputs, req, cid in A:
        add("alchemy", rid, name, inputs, req, {"kind": "consumable", "consumable_id": cid})

    # ---- Tailoring
    add("tailoring", "tail_bolt_linen", "Bolt of Linen Cloth", {"cloth_linen": 2}, 0, {"kind": "material", "material_id": "bolt_linen"})
    add("tailoring", "tail_bolt_wool", "Bolt of Wool Cloth", {"cloth_wool": 3}, 40, {"kind": "material", "material_id": "bolt_wool"})
    add("tailoring", "tail_bolt_silk", "Bolt of Silk Cloth", {"cloth_silk": 4}, 90, {"kind": "material", "material_id": "bolt_silk"})

    def cloth(tier, bolt, base, slots, bag, bag_req, kit_req, kit_inputs):
        # slots: (suffix, name, slot, bolts, req_offset)
        for suffix, name, slot, bolts, off in slots:
            req = base + off
            big = slot in ("chest", "head")
            add("tailoring", f"tail_{tier}_{suffix}", f"{tier.title()} {name}", {bolt: bolts}, req,
                {"kind": "armor", "slot": slot, "armor_type": "cloth", "stat_template": "int_caster", "item_level": il(req),
                 "rarity": rarity_for(req, big), "material_tier": tier})
        bag_id, bag_name = bag
        add("tailoring", f"tail_{tier}_bag", bag_name, {bolt: 4}, bag_req, {"kind": "bag", "bag_id": bag_id})
        add("tailoring", f"tail_kit_{tier}", f"{tier.title()} Upgrade Kit", kit_inputs, kit_req,
            {"kind": "material", "material_id": f"upgrade_kit_{tier}"})

    cloth("linen", "bolt_linen", 5, [("boots", "Boots", "feet", 2, 0), ("cloak", "Cloak", "back", 2, 5), ("belt", "Belt", "waist", 2, 10),
                                     ("bracers", "Bracers", "wrist", 2, 15), ("gloves", "Gloves", "hands", 3, 20),
                                     ("robe", "Robe", "chest", 4, 25), ("hood", "Hood", "head", 3, 30)],
          ("clasped_traveling_bag", "Clasped Traveling Bag"), 20, 35, {"bolt_linen": 4})
    cloth("wool", "bolt_wool", 50, [("boots", "Boots", "feet", 2, 0), ("cloak", "Cloak", "back", 2, 5), ("belt", "Belt", "waist", 2, 10),
                                    ("bracers", "Bracers", "wrist", 2, 15), ("gloves", "Gloves", "hands", 3, 20),
                                    ("robe", "Robe", "chest", 4, 25), ("hood", "Hood", "head", 3, 30)],
          ("sage_clasped_bag", "Sage Clasped Bag"), 70, 80, {"bolt_wool": 4})
    cloth("silk", "bolt_silk", 100, [("boots", "Boots", "feet", 2, 0), ("cloak", "Cloak", "back", 2, 5), ("belt", "Belt", "waist", 2, 10),
                                     ("bracers", "Bracers", "wrist", 2, 15), ("gloves", "Gloves", "hands", 3, 20),
                                     ("robe", "Robe", "chest", 4, 25), ("hood", "Hood", "head", 3, 30)],
          ("locked_drawstring_pack", "Locked Drawstring Pack"), 110, 120, {"bolt_silk": 4})

    # ---- Woodworking
    ww = lambda rid, name, inputs, req, output, count=1: add("woodworking", rid, name, inputs, req, output, count)
    # planks -> fiber / pages
    band = {"plank_softpine": ("fiber_coarse", "pages_rough"), "plank_ashwood": ("fiber_coarse", "pages_rough"),
            "plank_oakheart": ("fiber_supple", "pages_pressed"), "plank_driftwood": ("fiber_supple", "pages_pressed"),
            "plank_ironbark": ("fiber_tough", "pages_fine"), "plank_frostpine": ("fiber_tough", "pages_fine"),
            "plank_bramblewood": ("fiber_tough", "pages_fine")}
    for pid, wood, name, tier, req, _ in PLANKS:
        fib, pg = band[pid]
        short = name.replace(" Plank", "")
        ww(f"ww_fiber_{pid[6:]}", f"{short} Fiber", {pid: 1}, req, {"kind": "material", "material_id": fib}, 2)
        ww(f"ww_pages_{pid[6:]}", f"{short} Pages", {pid: 1}, req + 5, {"kind": "material", "material_id": pg}, 2)

    def tier_tag(req):
        return "ashwood" if req < 50 else "ironbark"

    def weapon(rid, name, inputs, req, slot, wtype, template, big=False):
        ww(rid, name, inputs, req, {"kind": "weapon", "slot": slot, "weapon_type": wtype, "stat_template": template, "item_level": il(req),
                                    "rarity": rarity_for(req, big), "material_tier": tier_tag(req)})

    def armor(rid, name, inputs, req, slot, atype, template, big=False):
        ww(rid, name, inputs, req, {"kind": "armor", "slot": slot, "armor_type": atype, "stat_template": template, "item_level": il(req),
                                    "rarity": rarity_for(req, big), "material_tier": tier_tag(req)})

    P = {"soft": "plank_softpine", "ash": "plank_ashwood", "oak": "plank_oakheart", "drift": "plank_driftwood",
         "iron": "plank_ironbark", "frost": "plank_frostpine", "bram": "plank_bramblewood"}
    # staves
    weapon("ww_softpine_staff", "Softpine Quarterstaff", {P["soft"]: 3, "fiber_coarse": 1}, 5, "main_hand", "staff", "int_caster")
    weapon("ww_ashwood_staff", "Ashwood Staff", {P["ash"]: 4, "fiber_coarse": 2}, 20, "main_hand", "staff", "int_caster")
    weapon("ww_oakheart_staff", "Oakheart Staff", {P["oak"]: 4, "fiber_supple": 2}, 40, "main_hand", "staff", "str_int_hybrid")
    weapon("ww_driftwood_staff", "Driftwood Staff", {P["drift"]: 4, "fiber_supple": 2}, 50, "main_hand", "staff", "int_caster")
    weapon("ww_ironbark_staff", "Ironbark Staff", {P["iron"]: 5, "fiber_tough": 2}, 80, "main_hand", "staff", "str_int_hybrid")
    weapon("ww_frostpine_staff", "Frostpine Staff", {P["frost"]: 5, "fiber_tough": 2}, 100, "main_hand", "staff", "int_caster")
    weapon("ww_bramblewood_staff", "Bramblewood Staff", {P["bram"]: 6, "fiber_tough": 3}, 125, "main_hand", "staff", "int_caster", True)
    # bows
    weapon("ww_softpine_bow", "Softpine Shortbow", {P["soft"]: 3, "fiber_coarse": 2}, 10, "ranged", "bow", "agi_physical")
    weapon("ww_ashwood_bow", "Ashwood Hunting Bow", {P["ash"]: 4, "fiber_coarse": 3}, 25, "ranged", "bow", "agi_physical")
    weapon("ww_oakheart_bow", "Oakheart Longbow", {P["oak"]: 4, "fiber_supple": 3}, 45, "ranged", "bow", "agi_physical")
    weapon("ww_ironbark_bow", "Ironbark Recurve", {P["iron"]: 5, "fiber_tough": 3}, 85, "ranged", "bow", "agi_physical")
    weapon("ww_frostpine_bow", "Frostpine Longbow", {P["frost"]: 5, "fiber_tough": 3}, 105, "ranged", "bow", "agi_physical")
    weapon("ww_bramblewood_bow", "Bramblewood War Bow", {P["bram"]: 6, "fiber_tough": 4}, 125, "ranged", "bow", "agi_physical", True)
    # crossbows (planks + fiber string + a bar for the lock)
    weapon("ww_ashwood_crossbow", "Ashwood Crossbow", {P["ash"]: 3, "fiber_coarse": 2, "bar_copper": 2}, 20, "ranged", "crossbow", "agi_physical")
    weapon("ww_oakheart_crossbow", "Oakheart Crossbow", {P["oak"]: 3, "fiber_supple": 2, "bar_tin": 2}, 50, "ranged", "crossbow", "agi_physical")
    weapon("ww_ironbark_crossbow", "Ironbark Crossbow", {P["iron"]: 4, "fiber_tough": 2, "bar_iron": 2}, 85, "ranged", "crossbow", "agi_physical")
    weapon("ww_frostpine_crossbow", "Frostpine Crossbow", {P["frost"]: 4, "fiber_tough": 2, "bar_steel": 2}, 110, "ranged", "crossbow", "agi_physical")
    # shields (planks + a bar for the rim)
    weapon("ww_softpine_buckler", "Softpine Buckler", {P["soft"]: 4, "bar_copper": 1}, 5, "off_hand", "shield", None)
    weapon("ww_ashwood_shield", "Ashwood Shield", {P["ash"]: 4, "bar_copper": 2}, 20, "off_hand", "shield", None)
    weapon("ww_oakheart_shield", "Oakheart Shield", {P["oak"]: 5, "bar_tin": 2}, 40, "off_hand", "shield", None)
    weapon("ww_driftwood_targe", "Driftwood Targe", {P["drift"]: 5, "bar_bronze": 2}, 55, "off_hand", "shield", None)
    weapon("ww_ironbark_shield", "Ironbark Shield", {P["iron"]: 6, "bar_iron": 3}, 80, "off_hand", "shield", None)
    weapon("ww_frostpine_shield", "Frostpine Shield", {P["frost"]: 6, "bar_steel": 3}, 105, "off_hand", "shield", None)
    weapon("ww_bramblewood_bulwark", "Bramblewood Bulwark", {P["bram"]: 7, "bar_steel": 4}, 125, "off_hand", "shield", None, True)
    # tomes (off-hand, bound pages)
    weapon("ww_softpine_primer", "Softpine Primer", {"pages_rough": 4, "fiber_coarse": 1, P["soft"]: 1}, 10, "off_hand", "tome", "int_caster")
    weapon("ww_ashwood_tome", "Ashwood Tome", {"pages_rough": 6, "fiber_coarse": 2, P["ash"]: 1}, 30, "off_hand", "tome", "int_caster")
    weapon("ww_oakheart_grimoire", "Oakheart Grimoire", {"pages_pressed": 6, "fiber_supple": 2, P["oak"]: 1}, 55, "off_hand", "tome", "int_caster")
    weapon("ww_ironbark_codex", "Ironbark Codex", {"pages_fine": 6, "fiber_tough": 2, P["iron"]: 1}, 90, "off_hand", "tome", "int_caster")
    weapon("ww_frostpine_grimoire", "Frostpine Grimoire", {"pages_fine": 8, "fiber_tough": 3, P["frost"]: 1}, 110, "off_hand", "tome", "int_caster")
    weapon("ww_bramblewood_codex", "Bramblewood Codex", {"pages_fine": 10, "fiber_tough": 4, P["bram"]: 2}, 130, "off_hand", "tome", "int_caster", True)
    # head pieces (occasional)
    armor("ww_driftwood_mask", "Driftwood Mask", {P["drift"]: 4, "fiber_supple": 3}, 50, "head", "leather", "agi_physical")
    armor("ww_ironbark_helm", "Ironbark Helm", {P["iron"]: 5, "fiber_tough": 3, "bar_iron": 3}, 85, "head", "mail", "str_physical")
    armor("ww_bramblewood_crown", "Bramblewood Crown", {P["bram"]: 6, "fiber_tough": 4, "herb_goldthorn": 2}, 125, "head", "leather", "agi_int_hybrid", True)
    # trinkets (rare)
    armor("ww_oakheart_charm", "Carved Oakheart Charm", {P["oak"]: 3, "fiber_supple": 2, "herb_kingsblood": 1}, 70, "trinket", "accessory", "int_caster")
    armor("ww_heartwood_idol", "Heartwood Idol", {P["bram"]: 4, "fiber_tough": 3, "herb_goldthorn": 2}, 130, "trinket", "accessory", "str_int_hybrid", True)
    # ammo (stacks of 5)
    ww("ww_rough_arrows", "Rough Arrows (5)", {P["soft"]: 1, "fiber_coarse": 1}, 0, {"kind": "consumable", "consumable_id": "rough_arrows"}, 5)
    ww("ww_rough_bolts", "Rough Bolts (5)", {P["ash"]: 1, "fiber_coarse": 1}, 5, {"kind": "consumable", "consumable_id": "rough_bolts"}, 5)
    ww("ww_sturdy_arrows", "Sturdy Arrows (5)", {P["drift"]: 1, "fiber_supple": 1}, 40, {"kind": "consumable", "consumable_id": "sturdy_arrows"}, 5)
    ww("ww_sturdy_bolts", "Sturdy Bolts (5)", {P["oak"]: 1, "fiber_supple": 1, "bar_tin": 1}, 45, {"kind": "consumable", "consumable_id": "sturdy_bolts"}, 5)
    ww("ww_heavy_arrows", "Heavy Arrows (5)", {P["iron"]: 1, "fiber_tough": 1}, 90, {"kind": "consumable", "consumable_id": "heavy_arrows"}, 5)
    ww("ww_heavy_bolts", "Heavy Bolts (5)", {P["frost"]: 1, "fiber_tough": 1, "bar_iron": 1}, 95, {"kind": "consumable", "consumable_id": "heavy_bolts"}, 5)
    # upgrade kits
    ww("ww_kit_ashwood", "Ashwood Upgrade Kit", {P["ash"]: 4, "fiber_coarse": 2}, 30, {"kind": "material", "material_id": "upgrade_kit_ashwood"})
    ww("ww_kit_ironbark", "Ironbark Upgrade Kit", {P["iron"]: 4, "fiber_tough": 2}, 85, {"kind": "material", "material_id": "upgrade_kit_ironbark"})

    # keep each profession's list ordered by skill_required (stable)
    for prof in R:
        R[prof] = dict(sorted(R[prof].items(), key=lambda kv: kv[1]["skill_required"]))
    return R


# ---------------------------------------------------------------------------------------------- professions
PROFESSIONS = {
    "mining": {"name": "Mining", "kind": "gathering", "description": "Dig ore from veins. Smelt it into bars at a forge."},
    "herbalism": {"name": "Herbalism", "kind": "gathering", "description": "Gather herbs. The ingredients for Alchemy."},
    "woodcutting": {"name": "Woodcutting", "kind": "gathering", "description": "Fell trees. Saw logs into planks at a sawmill."},
    "blacksmithing": {"name": "Blacksmithing", "kind": "crafting", "description": "Forge armor, weapons and upgrade kits from bars."},
    "alchemy": {"name": "Alchemy", "kind": "crafting", "description": "Brew healing and mana potions and elixirs from herbs."},
    "tailoring": {"name": "Tailoring", "kind": "crafting", "description": "Weave cloth into bolts, cloth armor and bags."},
    "woodworking": {"name": "Woodworking", "kind": "crafting", "description": "Craft shields, staves, bows, crossbows, tomes and arrows from planks."},
}
TIERS = [
    {"name": "Apprentice", "cap": 75, "required_level": 1, "cost": 500},
    {"name": "Journeyman", "cap": 150, "required_level": 10, "cost": 20000},
    {"name": "Expert", "cap": 225, "required_level": 25, "cost": 150000},
    {"name": "Artisan", "cap": 300, "required_level": 40, "cost": 600000},
]


def main():
    mats = load("data/gathering/materials.json")
    for mid, d in MATERIALS.items():
        d = dict(d)
        d.setdefault("stack_limit", 20)
        mats["materials"][mid] = {"name": d["name"], "material_type": d["material_type"], "profession": d["profession"], "tier": d["tier"],
                                  "description": d["description"], "stack_limit": d["stack_limit"], "sell_price": d["sell_price"],
                                  "icon_id": d["icon_id"], "skill_range": d["skill_range"]}
    save("data/gathering/materials.json", mats, nl=False)

    pools = load("data/gathering/node_pools.json")
    for zone, add in POOL_ADD.items():
        t = pools["zones"][zone]["table"]
        for mid, w in add.items():
            t[mid] = w
    save("data/gathering/node_pools.json", pools, indent=2)

    cons = load("data/consumables/consumable_types.json")
    cons["ammo"] = ammo_defs()
    save("data/consumables/consumable_types.json", cons, nl=False)

    (ROOT / "data" / "crafting").mkdir(exist_ok=True)
    R = recipes()
    save("data/crafting/recipes.json", {
        "_comment": "Recipes for the generic crafting stations (world/crafting_manager.py). Generated by tools/build_crafting_professions.py. "
                    "Guaranteed success; skill only gates access. 'count' = units produced per craft. 'station' = must stand at a sawmill. "
                    "Gear 'output' specs feed LootGenerator like data/blacksmithing/recipes.json.",
        "professions": {p: {"recipes": r} for p, r in R.items()}})

    (ROOT / "data" / "professions").mkdir(exist_ok=True)
    save("data/professions/professions.json", {
        "_comment": "Profession list and training tiers. cost is copper; 3 primary professions per character.",
        "max_primary": 3, "professions": PROFESSIONS, "tiers": TIERS})
    print({p: len(r) for p, r in R.items()}, "materials:", len(MATERIALS))


if __name__ == "__main__":
    main()
