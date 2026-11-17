"""What a recipe scroll says when you hover it, in your bags or on a vendor's shelf.

Kyle, 16 Nov 2026, hovering "Recipe: Redpepper Haunch" at a vendor: "when buying recipes it should say what it does.
Also what it requires! Like not a level but a 'Jewelcrafting - 200' for example." The vendor's card said "Common -
Recipe, Requires level 1". The bag's card already said more; both now draw from here, so they can't drift apart:

  * the trade and skill it needs, red when you're short ("Requires Jewelcrafting (200)");
  * what it teaches you to make, and WHAT THAT DOES: a piece's stats and the level to wear it, a dish's or a
    potion's effect, an enchantment's bonus, a material's use;
  * the materials one craft takes.
"""
GREY, RED, GREEN, BLUE, GOLD, STAT = ((170, 170, 170), (220, 70, 70), (120, 220, 140), (130, 180, 220),
                                      (200, 200, 140), (120, 200, 120))


def _material(mid):
    try:
        from world.gathering_manager import get_gathering_node_manager
        m = get_gathering_node_manager().make_material_instance(mid)
        if m is not None:
            return m
    except Exception:
        pass
    return None


def _material_name(mid):
    m = _material(mid)
    return getattr(m, "name", None) or str(mid).replace("_", " ").title()


def _effect_lines(out):
    """[(text, colour)] for what the recipe's product does."""
    lines = []
    kind = out.get("kind")
    item = out.get("item") or {}
    if kind in ("armor", "weapon"):
        what = [str(out.get("rarity", "")).title()]
        if kind == "armor" and out.get("armor_type") not in (None, "", "accessory"):
            what.append(str(out["armor_type"]).title())
        if kind == "weapon" and out.get("weapon_type"):
            what.append(str(out["weapon_type"]).replace("_", " ").title())
        what.append(str(out.get("slot", "")).replace("_", " ").title())
        lines.append((" ".join(w for w in what if w), GOLD))
        if item.get("weapon_damage_max"):
            lines.append((f"Damage: {item['weapon_damage_min']}-{item['weapon_damage_max']}", GREY))
        if item.get("armor_value"):
            lines.append((f"Armor: {item['armor_value']}", GREY))
        from entities.power_scale import item_stat_line
        for stat, val in (item.get("primary_stats") or {}).items():
            lines.append((f"+{val} {stat.replace('_', ' ').title()}", GREY))
        for stat, val in (item.get("secondary_stats") or {}).items():
            lines.append((item_stat_line(stat, val), STAT))
        if (item.get("proc") or {}).get("description"):
            lines.append((item["proc"]["description"], STAT))
        req = item.get("required_level") or out.get("required_level")
        if req:
            lines.append((f"Requires level {req} to wear", GREY))
    elif kind == "consumable":
        try:
            from entities.consumable_manager import get_consumable_manager
            c = get_consumable_manager().get_consumable(out.get("consumable_id"))
        except Exception:
            c = None
        if c is not None:
            if getattr(c, "description", ""):
                lines.append((c.description, STAT))
            if getattr(c, "required_level", 0):
                lines.append((f"Requires level {c.required_level} to use", GREY))
    elif kind == "material":
        mid = out.get("material_id")
        try:
            from world import enchanting
            e = enchanting.enchant(mid)
        except Exception:
            e = None
        if e:
            from entities.power_scale import item_stat_line
            for stat, val in (e.get("stats") or {}).items():
                lines.append((item_stat_line(stat, val), STAT))
            if (e.get("proc") or {}).get("description"):
                lines.append((e["proc"]["description"], STAT))
        m = _material(mid)
        if m is not None and getattr(m, "description", ""):
            lines.append((m.description, GREY))
    return lines


def recipe_lines(item, subject=None, show_state=True):
    """[(text, colour)] for a recipe scroll, everything but its name and price."""
    recipe_id = getattr(item, "recipe_id", None)
    profession = getattr(item, "recipe_profession", None) or ""
    try:
        from world.recipe_manager import get_recipe_info
        prof2, data = get_recipe_info(recipe_id)
    except Exception:
        prof2, data = None, None
    data = data or {}
    profession = profession or prof2 or ""
    skill = int(data.get("skill_required", 0) or 0)
    lines = []
    if profession:
        met = True
        if subject is not None:
            met = subject.knows_profession(profession) and subject.profession_skills.get(profession, 0) >= skill
        lines.append((f"Requires {profession.replace('_', ' ').title()} ({skill})", GREY if met else RED))
        if subject is not None and show_state and not subject.knows_recipe(recipe_id):
            if not subject.knows_profession(profession):
                lines.append((f"You have not learned {profession.replace('_', ' ').title()}.", RED))
            elif not met:
                lines.append((f"Your skill: {subject.profession_skills.get(profession, 0)}", (170, 120, 120)))
    out = data.get("output") or {}
    if data.get("name"):
        lines.append(("", GREY))
        count = data.get("count", 1)
        made = data["name"] + (f" x{count}" if count and count > 1 else "")
        lines.append((f"Teaches you to make: {made}", BLUE))
        lines.extend(_effect_lines(out))
    inputs = data.get("inputs") or {}
    if inputs:
        lines.append(("Materials:", GREY))
        for mid, n in inputs.items():
            lines.append((f"  {n} x {_material_name(mid)}", GREY))
    if subject is not None and show_state:
        if subject.knows_recipe(recipe_id):
            lines.append(("Already known.", GREY))
    return lines
