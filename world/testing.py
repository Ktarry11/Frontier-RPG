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
    from world.hidden_zones import is_hidden
    for name, z in sorted(zone_manager.zones.items()):
        if is_hidden(name):
            continue        # Kyle wants to find these himself (world/hidden_zones.py)
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
    if placement is None:
        return f"No room for {recruit.name}: the party and the bench are both full."
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
            # A learned trade starts at 1, the same as Character.learn_profession (Kyle, 16 Nov 2026: "WE START
            # PROFESSIONS AT LVL 1 AND NOT LVL 0"). This button skipped that rule and left every trade at 0.
            character.profession_skills[p] = max(1, character.profession_skills.get(p, 0))
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


# ------------------------------------------------------------------ switches
# Kyle, 20 Nov 2026: "automatically complete quests when you pick them up (toggled off/on in testing) so if i go to
# talk to someone who wants me to kill 4 boars, when i accept the quest i have 4/4 boars killed - this is so i can
# test quest chains. Also, the option to kill in one hit (toggle on/off)".
#
# The switches live outside every save slot, next to the Collection (data/saves/testing_flags.json), so they stay as
# you left them across characters and restarts. The overworld's TEST button turns red while any of them is on, so
# one never gets left on by accident.
import json as _json
from pathlib import Path as _Path

FLAGS_PATH = _Path(__file__).resolve().parent.parent / "data" / "saves" / "testing_flags.json"
SWITCHES = {
    "auto_quests": ("Quests complete when you accept them",
                    "Every objective is filled the moment you accept a quest, so you can walk a chain from giver to "
                    "giver. Turn-ins, rewards and the next quest in the chain all work as normal."),
    "one_hit": ("One-hit kills",
                "Any hit from you, your party or your pets kills an enemy outright: no dodge, no shield, no "
                "last stand. A boss with phases still goes through each one, one hit per phase."),
}
_flags = None


def flags():
    global _flags
    if _flags is None:
        try:
            _flags = dict(_json.loads(FLAGS_PATH.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            _flags = {}
    return _flags


def on(name):
    """True if a testing switch is on. Cheap: the game asks this on every quest accepted and every hit landed."""
    return bool(flags().get(name))


def any_on():
    return any(on(k) for k in SWITCHES)


def toggle(name):
    f = flags()
    f[name] = not f.get(name)
    try:
        FLAGS_PATH.parent.mkdir(parents=True, exist_ok=True)
        FLAGS_PATH.write_text(_json.dumps(f, indent=1), encoding="utf-8")
    except OSError:
        pass
    return f"{SWITCHES[name][0]}: {'ON' if f[name] else 'off'}."


def fill_objectives(quest):
    """Every objective of `quest` done, and the quest ready to hand in."""
    from world.quest import QuestStatus
    for o in quest.objectives:
        o.progress = o.count
        if getattr(o, "topics", None):
            o.topics_asked = list(o.topics)
    if quest.status == QuestStatus.ACTIVE:
        quest.status = QuestStatus.READY_TO_TURN_IN


def complete_active_quests():
    """Every quest you have now, done (for quests picked up before the switch was on)."""
    from world.quest import QuestStatus
    from world.quest_manager import get_quest_manager
    n = 0
    for q in get_quest_manager().quests.values():
        if q.status in (QuestStatus.ACTIVE, QuestStatus.READY_TO_TURN_IN):
            if q.status == QuestStatus.ACTIVE:
                n += 1
            fill_objectives(q)
    return f"{n} quests are ready to hand in." if n else "You have no unfinished quests."


def on_our_side(attacker):
    """The player, a recruit or a pet: whatever one-hit kills is for (an enemy hitting an enemy doesn't count)."""
    from entities.character import Character
    if isinstance(attacker, Character):
        return True
    try:
        from entities.pet import Pet
        return isinstance(attacker, Pet)
    except Exception:
        return False


# ------------------------------------------------------------------ the Collection
# Kyle, 20 Nov 2026: "a very important one is the option to REMOVE collection items (right now if i experiment and
# buy them, they are saved ot everyone)". Removing is the one thing the Collection never lets a player do; this is
# the test-only way back.
def learned_collectables():
    from world import collection as C
    return sorted(C.learned_entries(), key=lambda e: (e["kind"], e["name"]))


def remove_collectable(cid):
    """Unlearn `cid` for the whole account. Whatever the character being played was using it for (riding it,
    wearing it as a form or a title) is put down too. A feather's flight paths and a vault's bank tab stay where
    they are, because taking a bank tab away could take the things in it with it."""
    from world import collection as C
    col = C.collection()
    e = C.get_entry(cid)
    if cid not in col.learned:
        return "That isn't learned."
    del col.learned[cid]
    for k, v in list(col.prefs.items()):
        if v == cid:
            del col.prefs[k]
    col.save()
    try:
        from world.travel_manager import get_travel_manager
        tm = get_travel_manager()
        if getattr(tm, "active_mount", None) == cid:
            tm.mounted = False
            tm.active_mount = next((m for m in getattr(tm, "owned_mounts", []) if m != cid), None)
        if getattr(tm, "active_form", None) == cid:
            tm.active_form = None
        if getattr(tm, "active_title", None) == cid:
            tm.active_title = None
    except Exception:
        pass
    return f"Removed {e['name'] if e else cid} from the Collection, for every character."


def remove_all_collectables():
    ids = [e["id"] for e in learned_collectables()]
    for cid in ids:
        remove_collectable(cid)
    return f"Removed all {len(ids)} things from the Collection." if ids else "The Collection is already empty."


# ------------------------------------------------------------------ friendship
# Kyle, 20 Nov 2026: "i'd like the option to raise peoples friendship levels with myself and others to test their
# interactions". Trust with you goes through the bond's own rule (world/bond_manager.py), so a new stage logs its
# line, and Sworn hands over the keepsake and the Sworn skill. How two recruits get on goes through the relationship's
# own rule (world/relationship_manager.py), so crossing into friendly, close, grating or rivals plays that moment.
def bonded():
    """[(rid, name, Bond)] for everyone with friendship, sorted by name."""
    from world.bond_manager import get_bond_manager
    bm = get_bond_manager()
    return sorted(((rid, bm.name_of(rid), b) for rid, b in bm.bonds.items()), key=lambda t: t[1])


def stage_name(b):
    from world.bond_manager import STAGE_NAMES
    return STAGE_NAMES[b.stage_key]


def raise_stage(rid, party=None):
    """Trust up to the next stage. Sworn also needs their personal quest done; use make_sworn for that."""
    from world.bond_manager import get_bond_manager, THRESHOLDS, STAGES
    bm = get_bond_manager()
    b = bm.get(rid)
    if b is None:
        return "No friendship for them."
    if party is not None:
        bm.party = party
    top = len(STAGES) - 1 if "goal_done" in b.flags else len(STAGES) - 2
    if b.stage >= top:
        return (f"{bm.name_of(rid)} is already {stage_name(b)}." if b.stage == len(STAGES) - 1 else
                f"{bm.name_of(rid)} is a Friend. Sworn needs their personal quest done: use Make Sworn.")
    b.trust = THRESHOLDS[b.stage + 1]
    bm._trust(b, 0)
    st = stage_name(b)
    return f"{bm.name_of(rid)} is now {'an' if st[0] in 'AEIOU' else 'a'} {st} (trust {int(b.trust)})."


def make_sworn(rid, party=None):
    """Their personal quest counted as done, and trust all the way: the keepsake and the Sworn skill come with it."""
    from world.bond_manager import get_bond_manager, THRESHOLDS
    bm = get_bond_manager()
    b = bm.get(rid)
    if b is None:
        return "No friendship for them."
    if party is not None:
        bm.party = party
    if "goal_done" not in b.flags:
        b.flags.append("goal_done")
    b.trust = max(b.trust, THRESHOLDS[-1])
    bm._trust(b, 0)
    return f"{bm.name_of(rid)} is Sworn."


def fill_mood(rid):
    from world.bond_manager import get_bond_manager
    bm = get_bond_manager()
    b = bm.get(rid)
    if b is None:
        return "No friendship for them."
    b.mood, b.warned, b.leave_cause, b.angry, b.needs_talk = 100, None, None, False, False
    return f"{bm.name_of(rid)} is happy to be here (mood 100), and won't leave over anything that happened."


def raise_everyone(party=None):
    out = [raise_stage(rid, party) for rid, _n, _b in bonded()]
    return f"Everyone up a stage where they could go ({sum(1 for s in out if 'is now' in s)} moved)."


def pair_state(a, b):
    from world.bond_manager import get_bond_manager
    from world.relationship_manager import STATE_NAMES
    rm = get_bond_manager().rel
    r = rm.rels.get(rm.key(a, b))
    return STATE_NAMES[rm.state(a, b)], (r.affinity if r else 0.0)


def nudge_pair(a, b, step):
    """Move two recruits to the next state up (step > 0) or down: friendly, close friends, or grating, rivals.
    The moment that goes with crossing into it is queued for the banter panel, which says it back in the world."""
    from world.bond_manager import get_bond_manager
    from world.relationship_manager import FRIENDLY, CLOSE, GRATING, RIVALS, STATE_NAMES
    bm = get_bond_manager()
    rm = bm.rel
    r = rm.rel(a, b)
    ladder = [RIVALS - 2, GRATING - 2, 0, FRIENDLY + 2, CLOSE + 2]
    if step > 0:
        target = next((v for v in ladder if v > r.affinity + 0.5), ladder[-1])
    else:
        target = next((v for v in reversed(ladder) if v < r.affinity - 0.5), ladder[0])
    if r.state == "strangers":
        r.met_said = True
    key = rm._move(r, target - r.affinity)
    rm._milestone(r, key)
    return (f"{bm.name_of(a)} and {bm.name_of(b)}: {STATE_NAMES[r.state]} (affinity {int(r.affinity)}). "
            f"Their moment plays in the banter panel back in the world.")
