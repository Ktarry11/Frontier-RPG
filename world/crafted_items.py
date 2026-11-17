"""What a gear recipe makes. Shared by the crafting, blacksmithing and leatherworking managers, and by
the professions screen's preview, so what you see before you craft is what you get.

Kyle, 14 Nov 2026: "why does VOIDWEAVE....give these random ass stats ... I highly suggest we look into
how wow deals with some of this stuff." WoW's crafted items are written out: Felcloth Hood is the same
hood every time, and you can read it on the recipe before you make it. So a gear recipe now carries its
finished item under output["item"] (written by tools/build_crafted_gear.py), and that's what gets built.
A recipe that hasn't been authored yet still rolls through the loot generator, the old way.
"""


def is_gear(recipe):
    return (recipe or {}).get("output", {}).get("kind") in ("armor", "weapon")


def is_authored(recipe):
    return bool((recipe or {}).get("output", {}).get("item"))


def build(recipe):
    """The Item this armour or weapon recipe makes, or None if it isn't one."""
    out = (recipe or {}).get("output") or {}
    kind = out.get("kind")
    if kind not in ("armor", "weapon"):
        return None
    if out.get("item"):
        from entities.boss_loot import _item_from_def
        item = _item_from_def(out["item"])
    else:
        from entities.loot_generator import LootGenerator
        gen = LootGenerator()
        if kind == "armor":
            item = gen.generate_armor_piece(slot=out["slot"], armor_type=out["armor_type"],
                                            stat_template=out["stat_template"],
                                            item_level=out["item_level"], rarity=out["rarity"])
        else:
            item = gen.generate_weapon(slot=out["slot"], weapon_type=out["weapon_type"],
                                       stat_template=out["stat_template"],
                                       item_level=out["item_level"], rarity=out["rarity"])
        item.name = recipe["name"]
    if item is None:
        return None
    item.is_crafted = True
    # which upgrade kit fits it (world/upgrade_manager.py matches kits by material)
    item.crafting_material = out.get("material_tier")
    return item


_PREVIEWS = {}


def preview(recipe_id, recipe):
    """The item a recipe makes, for a tooltip. Authored recipes always make the same item, so the
    preview is exact; it's built once and kept. An unauthored one is rolled once, as an example."""
    key = recipe_id or (recipe or {}).get("name")
    if key not in _PREVIEWS:
        try:
            out = (recipe or {}).get("output") or {}
            if out.get("kind") == "bag":
                from entities.loot_generator import LootGenerator
                _PREVIEWS[key] = LootGenerator().generate_bag(bag_id=out["bag_id"])
            else:
                _PREVIEWS[key] = build(recipe)
        except Exception:
            _PREVIEWS[key] = None
    return _PREVIEWS[key]


#: short names for a recipe row's one-line summary; the tooltip has the full ones
SHORT = {"strength": "Str", "agility": "Agi", "stamina": "Stam", "intellect": "Int", "spirit": "Spi",
         "spell_power": "Spell Power", "healing_power": "Healing Power", "attack_power": "AP",
         "fire_spell_power": "Fire Power", "frost_spell_power": "Frost Power",
         "arcane_spell_power": "Arcane Power", "shadow_spell_power": "Shadow Power",
         "nature_spell_power": "Nature Power", "holy_spell_power": "Holy Power",
         "hit_rating": "Hit", "spell_hit_rating": "Spell Hit", "crit_chance_spell": "Spell Crit", "crit_chance_physical": "Crit",
         "haste": "Haste", "spell_penetration": "Spell Pen", "mp5": "Mp5", "defense_rating": "Defense",
         "dodge_rating": "Dodge", "parry_rating": "Parry", "block_rating": "Block",
         "block_value": "Block", "armor_penetration_pct": "Armor Pen"}


def summary(item):
    """'+64 Shadow Power, +19 Stam, +9 Int' for a recipe row: biggest first."""
    if item is None:
        return ""
    if getattr(item, "bag_capacity", 0):
        return f"{item.bag_capacity} slot bag"
    stats = {**(item.primary_stats or {}), **(item.secondary_stats or {})}
    parts = []
    for k, v in sorted(stats.items(), key=lambda kv: -kv[1]):
        label = SHORT.get(k, k.replace("_", " ").title())
        parts.append(f"+{v}{label}" if label.startswith("%") else f"+{v} {label}")
    return ", ".join(parts)
