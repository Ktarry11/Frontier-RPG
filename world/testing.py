"""The Testing menu's actions (ui/screens/testing_screen.py). TEST ONLY.

Kyle, 14 Nov 2026: "I want a testing menu with subtabs... teleportation, so to go to any town in
the world and unlocking all the flight masters... recruits, so an option to force any recruit into
your party so we can test their character traits... give us gold so we can buy anything and test
shops / riding etc... professions. So one where we can learn every profession, move our skill level
to 75/150/225/300 (in addition to this we need one where can get every profession resource in the
game to test the systems). I want to be able to agitate the system and check it without spending
hours because right now this game is well over 100+ hours playtime."

Everything here goes through the game's own systems (level_up, add_member, add_material,
learn_trainer_recipes, transition_to_zone), so a test exercises the real paths and leaves a normal
save behind. Each action returns a line for the screen to show.
"""

# ------------------------------------------------------------------ travel
def towns(zone_manager):
    """Every town with an inn, the same list the Teleport button uses."""
    from world.fast_travel import destinations
    return destinations(zone_manager)


def zones(zone_manager):
    """[{label, zone, x, y}] for every zone in the world, landing on its first arrival point."""
    out = []
    for name, z in sorted(zone_manager.zones.items()):
        tm = z.get("tilemap") if isinstance(z, dict) else None
        arrivals = list(getattr(tm, "arrivals", None) or [])
        x, y = arrivals[0] if arrivals else (None, None)
        out.append({"label": name, "zone": name, "x": x, "y": y})
    return out


def teleport(zone_manager, dest):
    zone_manager.transition_to_zone(dest["zone"], dest.get("x"), dest.get("y"), via_portal=False)
    return f"Teleported to {dest['label']}."


def unlock_flights():
    from world.travel_manager import get_travel_manager, TravelManager
    tm = get_travel_manager()
    before = len(tm.known_nodes)
    for node_id in TravelManager.nodes():
        tm.known_nodes.add(node_id)
    return f"Every flight path is open ({len(tm.known_nodes)} flight masters, {len(tm.known_nodes) - before} new)."


# ------------------------------------------------------------------ recruits
def recruits():
    """[(recruit id, RecruitNPC)] sorted by name."""
    from world.recruit_manager import get_recruit_manager
    rm = get_recruit_manager()
    return sorted(rm.recruits.items(), key=lambda kv: kv[1].name)


def force_recruit(party, recruit_id):
    """Put a recruit in the party now: no level gate, no friendship, no walk to find them. They
    join at the player's level (or their own, if higher) so their kit and traits can be tried."""
    from world.recruit_manager import get_recruit_manager
    rm = get_recruit_manager()
    recruit = rm.recruits.get(recruit_id)
    if recruit is None:
        return "No such recruit."
    if any(getattr(m, "recruit_id", None) == recruit_id
           for m in list(party.members) + list(getattr(party, "bench", []))):
        return f"{recruit.name} is already with you."
    char = rm.build_or_restore(recruit, None)
    if char is None:
        return f"{recruit.name} couldn't be built."
    level = getattr(party.player, "level", 1)
    if char.level < level:
        char = rm._catch_up(char, level)
    placement = party.add_member(char)
    rm.mark_recruited(recruit_id)
    try:
        from world.bond_manager import get_bond_manager
        bm = get_bond_manager()
        if bm.has(recruit_id):
            bm.on_joined(recruit_id)
    except Exception:
        pass
    where = "joins the party" if placement == "active" else "waits on the bench (the party is full)"
    return f"{recruit.name} (level {char.level} {recruit.char_class}) {where}."


def send_home(party, member):
    from world.recruit_manager import get_recruit_manager
    if member is party.player:
        return "That's you."
    get_recruit_manager().dismiss(member)
    party.remove_member(member)
    return f"{member.name} goes home."


# ------------------------------------------------------------------ gold and levels
def add_gold(party, gold):
    party.add_currency(int(gold) * 10000)
    return f"+{gold:,} gold. The party has {party.get_currency_string()}."


def everyone(party):
    return list(party.members) + list(getattr(party, "bench", []))


def level_party(party, levels):
    """Through Character.level_up(), so stats, ranks, talent points and pets all follow."""
    from config import MAX_LEVEL
    gained = 0
    for m in everyone(party):
        for _ in range(levels):
            if m.level >= MAX_LEVEL:
                break
            m.level_up()
            gained += 1
        m.experience = 0
        for pet in (getattr(m, "all_pets", None) or [getattr(m, "active_pet", None)]):
            if pet is not None and hasattr(pet, "sync_to_owner_level"):
                pet.sync_to_owner_level()
    return (f"Party levelled: you're level {party.player.level}." if gained
            else f"Everyone is already level {MAX_LEVEL}.")


def heal_party(party):
    for m in everyone(party):
        m.current_health = m.health
        if hasattr(m, "mana"):
            m.current_mana = m.mana
    return "Everyone is at full health and mana."


# ------------------------------------------------------------------ professions
def professions():
    from world import profession_manager as pm
    return list(pm.professions())


def learn_all_professions(character):
    """Every profession, past the three-primary limit (a Craftsman's Codex lifts it in play)."""
    new = 0
    for p in professions():
        if p not in character.known_professions:
            character.known_professions.append(p)
            character.profession_tiers.setdefault(p, 0)
            character.profession_skills.setdefault(p, 0)
            new += 1
    return f"Learned {new} professions; you know all {len(character.known_professions)}."


TIER_FOR_SKILL = {75: 0, 150: 1, 225: 2, 300: 3}


def _all_recipes():
    from world.recipe_manager import _load_all_recipes
    return _load_all_recipes()


def set_profession_skill(character, skill):
    """Every known profession to `skill` (75, 150, 225 or 300), with the trainer tier that allows
    it, and every trainer recipe up to it taught, as a trainer visit would."""
    tier = TIER_FOR_SKILL[skill]
    by_prof = {}
    for rid, (prof, recipe) in _all_recipes().items():
        by_prof.setdefault(prof, {})[rid] = recipe
    taught = 0
    for p in character.known_professions:
        character.profession_tiers[p] = tier
        character.profession_skills[p] = skill
        taught += len(character.learn_trainer_recipes(p, by_prof.get(p, {})))
    return f"Every profession you know is at {skill}; {taught} trainer recipes taught."


def learn_every_recipe(character):
    """Every recipe in the game, trainer, vendor and drop, for the professions you know."""
    n = 0
    for rid, (prof, _r) in _all_recipes().items():
        if prof in character.known_professions or (prof == "fishing" and "cooking" in character.known_professions):
            if rid not in character.known_recipes:
                character.known_recipes.add(rid)
                n += 1
    return f"Learned {n} more recipes."


def material_categories():
    """[(key, label)] matching the bags' Materials subtabs."""
    from ui.screens.inventory_screen import MATERIAL_SUBTABS
    return [(k, label) for k, label, _t in MATERIAL_SUBTABS]


def give_materials(character, category="all", count=20):
    """`count` of every material in a category (the bags' Materials subtabs), or all of them."""
    from world.gathering_manager import get_gathering_node_manager
    from ui.screens.inventory_screen import material_subtab
    gm = get_gathering_node_manager()
    n = 0
    for mid in list(gm.materials):
        m = gm.make_material_instance(mid)
        if m is None:
            continue
        if category != "all" and material_subtab(m) != category:
            continue
        want = min(count, getattr(m, "stack_limit", count) or count)   # one rod, one kit
        have = character.get_material_quantity(mid)
        if have >= want:
            continue
        m.quantity = want - have
        # a stack that is already full would make a second one; top the first one up instead
        stack = next((s for s in character.materials if s.material_id == mid), None)
        if stack is not None:
            stack.quantity = want
        else:
            character.add_material(m)
        n += 1
    return f"Topped up {n} materials to {count} each."
