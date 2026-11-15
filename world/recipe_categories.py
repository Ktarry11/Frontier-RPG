"""Which sub-tab a recipe sits under on the professions screen.

Kyle, 14 Nov 2026: "Can we make sub tabs within crafting as well to sort by things....like gem type, armor
slot, etc....like rather than going through ALL tailoring, i might just want bags."

Decided from what the recipe MAKES, so a new recipe sorts itself: gear by slot, bags, cut gems by colour,
enchantments by what they go on, runes by role, consumables by kind, and anything else by the kind of
material it is.
"""
import json
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SLOT = {"head": "Head", "shoulder": "Shoulders", "chest": "Chest", "wrist": "Wrists", "hands": "Hands",
        "waist": "Waist", "legs": "Legs", "feet": "Feet", "back": "Cloaks", "neck": "Jewellery",
        "ring": "Jewellery", "ring1": "Jewellery", "ring2": "Jewellery", "trinket": "Trinkets",
        "trinket1": "Trinkets", "trinket2": "Trinkets"}
RANGED = {"gun": "Guns", "bow": "Bows", "crossbow": "Bows", "wand": "Wands", "thrown": "Weapons"}

#: the consumables file's sections, by what a player would call them
CONSUMABLE = {"food": "Food & Drink", "meals": "Food & Drink", "cooked_meals": "Food & Drink",
              "drinks": "Food & Drink", "health_potions": "Potions", "mana_potions": "Potions",
              "elixirs": "Elixirs", "flasks": "Elixirs", "explosives": "Explosives", "gadgets": "Gadgets",
              "ammo": "Ammo", "ammos": "Ammo", "lures": "Lures", "oils": "Oils", "weapon_oils": "Oils",
              "status_potions": "Potions", "revive_items": "Potions"}

MATERIAL = {"bolt": "Cloth", "cloth": "Cloth", "bar": "Bars", "ingot": "Bars", "leather": "Leather",
            "hide": "Leather", "upgrade_kit": "Upgrade Kits", "plank": "Planks", "lumber": "Planks",
            "thread": "Thread", "dye": "Dyes", "part": "Parts", "component": "Parts", "flux": "Flux",
            "rod": "Rods", "enchant_rod": "Rods", "scope": "Scopes", "attachment": "Scopes"}

#: a consumable by its own type, or failing that by the first word of its id
BY_TYPE = {"health_potion": "Potions", "mana_potion": "Potions", "potion": "Potions", "elixir": "Elixirs",
           "flask": "Elixirs", "food": "Food & Drink", "meal": "Food & Drink", "drink": "Food & Drink",
           "explosive": "Explosives", "bomb": "Explosives", "gadget": "Gadgets", "ammo": "Ammo",
           "lure": "Lures"}

#: enchantments by what they go on, in the same words as the gear tabs
ENCHANT_GROUP = {"2h": "Two-Handers", "weapon": "Weapons", "bracer": "Wrists", "bracers": "Wrists",
                 "boots": "Feet", "gloves": "Hands", "cloak": "Cloaks", "shield": "Shields",
                 "chest": "Chest", "head": "Head", "legs": "Legs", "shoulder": "Shoulders"}

#: the order the sub-tabs run in; anything not listed goes on the end, alphabetically
ORDER = ["Head", "Shoulders", "Chest", "Wrists", "Hands", "Waist", "Legs", "Feet", "Cloaks",
         "Weapons", "Two-Handers", "Shields", "Off-hands", "Quivers", "Guns", "Bows", "Wands", "Trinkets", "Jewellery", "Bags",
         "Red", "Orange", "Yellow", "Green", "Blue", "Purple", "Meta", "Prismatic", "Prospecting",
         "Tank", "Damage", "Healing", "Any role", "Capstones",
         "Food & Drink", "Potions", "Elixirs", "Transmutes", "Oils", "Explosives", "Gadgets", "Ammo", "Lures",
         "Figurines", "Cloth", "Leather", "Bars", "Planks", "Thread", "Parts", "Rods", "Scopes",
         "Upgrade Kits", "Materials"]


@lru_cache(maxsize=1)
def _consumable_sections():
    try:
        d = json.loads((ROOT / "data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    out = {}
    for section, entries in d.items():
        for e in (entries if isinstance(entries, list) else []):
            if isinstance(e, dict) and e.get("consumable_id"):
                out[e["consumable_id"]] = section
    return out


def category(recipe):
    """The sub-tab label for one recipe."""
    out = (recipe or {}).get("output") or {}
    kind = out.get("kind")
    if kind in ("armor", "weapon"):
        wt = out.get("weapon_type")
        if wt == "shield":
            return "Shields"
        if wt in RANGED:
            return RANGED[wt]
        if wt in ("totem", "idol", "libram", "tome", "orb", "off_hand"):
            return "Off-hands"
        if wt:
            return "Weapons"
        if out.get("slot") == "ranged":
            return "Quivers"
        return SLOT.get(out.get("slot"), "Gear")
    if kind == "bag":
        return "Bags"
    if kind == "prospect":
        return "Prospecting"
    if kind == "fixed":
        return SLOT.get((out.get("item") or {}).get("slot"), "Figurines") if (out.get("item") or {}).get("slot") \
            not in ("trinket", "trinket1", "trinket2") else "Figurines"
    if kind == "consumable":
        cid = out.get("consumable_id") or ""
        section = _consumable_sections().get(cid)
        if section in CONSUMABLE:
            return CONSUMABLE[section]
        # one that lives in another file: ask what kind of thing it is
        try:
            from entities.consumable_manager import get_consumable_manager
            ctype = getattr(get_consumable_manager().get_consumable(cid), "consumable_type", "") or ""
        except Exception:
            ctype = ""
        if "transmute" in cid:
            return "Transmutes"
        return BY_TYPE.get(ctype) or BY_TYPE.get(cid.split("_")[0], "Consumables")
    if kind == "material":
        mid = out.get("material_id")
        try:
            from world.jewelcrafting import cut
            g = cut(mid)
            if g:
                return g["color"].capitalize()
        except Exception:
            pass
        try:
            from world.runes import rune
            r = rune(mid)
            if r:
                if r.get("capstone"):
                    return "Capstones"
                return {"tank": "Tank", "damage": "Damage", "healing": "Healing"}.get(r.get("role"), "Any role")
        except Exception:
            pass
        try:
            from world.enchanting import enchant
            e = enchant(mid)
            if e:
                g = str(e.get("group") or "")
                return ENCHANT_GROUP.get(g.lower(), g.replace("_", " ").title() or "Enchants")
        except Exception:
            pass
        try:
            from world.gathering_manager import get_gathering_node_manager
            mt = (get_gathering_node_manager().get_material_def(mid) or {}).get("material_type", "")
        except Exception:
            mt = ""
        return MATERIAL.get(mt, "Materials")
    return "Other"


def ordered(labels):
    """Sub-tab labels in display order."""
    rank = {k: i for i, k in enumerate(ORDER)}
    return sorted(set(labels), key=lambda s: (rank.get(s, len(ORDER)), s))
