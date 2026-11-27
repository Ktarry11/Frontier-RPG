"""What the Collection's things do (docs/collection_design.md).

The catalogue is data/collection/collectables.json (tools/build_collection.py); what this player has learned is
entities/account_collection.py. Everything here asks "has the account learned X?" and does X for whichever character
is being played. Nothing in here is stored per character except what has to be: a portable service's last use (the
market clock lives in each save), the form you're wearing and your second hearth's bind, which all ride in the
character's TravelManager.

Kyle's rules, 18 Nov 2026: learn once and every character has it; mounts still need riding; forms are map only;
feathers are Kalimdor and the Eastern Kingdoms; portable services are once per market day; heirlooms fit the wearer,
level with them and give +80% XP in all (2H 20%, 1H/shield/off-hand 10% each, six armour pieces 10% each).
"""
import json
import os
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "collection" / "collectables.json"

#: one market day (world/market/market.py's clock is in market hours)
SERVICE_COOLDOWN_HOURS = 24.0
#: an heirloom stops paying experience here, because there's none left to earn
XP_CAP_LEVEL = 60
#: Kyle: "+80% total"
XP_CAP_PCT = 80

TABS = (("mount", "Mounts"), ("form", "Forms"), ("title", "Titles"), ("travel", "Travel"), ("service", "Services"),
        ("heirloom", "Heirlooms"), ("keepsake", "Keepsakes"))
#: tomes sit on the Travel tab with the feathers and the hearths
TAB_OF = {"mount": "mount", "form": "form", "title": "title", "travel": "travel", "tome": "travel",
          "service": "service", "heirloom": "heirloom", "keepsake": "keepsake"}

FORM_DIR = ROOT / "assets" / "collection" / "forms"
MOUNT_DIR = ROOT / "assets" / "mounts"
DIRECTIONS = ("down", "left", "right", "up")

_DATA = None


def data():
    global _DATA
    if _DATA is None:
        _DATA = json.loads(DATA.read_text(encoding="utf-8"))
    return _DATA


def entries():
    return list(data()["collectables"])


def get_entry(cid):
    for e in data()["collectables"]:
        if e["id"] == cid:
            return e
    return None


def by_tab(tab):
    return [e for e in entries() if TAB_OF.get(e["kind"]) == tab]


def rarity_weight(rarity):
    return float(data()["rarity_weight"].get(rarity, 1.0))


def collection():
    from entities.account_collection import get_collection
    return get_collection()


def learned(cid):
    try:
        return collection().has(cid)
    except Exception:
        return False


def learned_entries(kind=None):
    return [e for e in entries() if learned(e["id"]) and (kind is None or e["kind"] == kind)]


def _effect_sum(key):
    return sum(e["effect"].get(key, 0) for e in learned_entries())


# ------------------------------------------------------------------ the bag item
def make_item(cid):
    """The bag item for collectable `cid`: what the auction house sells and the mail delivers."""
    from entities.item import Item
    e = get_entry(cid)
    if e is None:
        return None
    it = Item(item_id=f"collectable_{cid}", name=e["name"], slot="collection", item_level=1, rarity=e["rarity"],
              required_level=1, sell_price=max(1, e["price"] // 40), icon_id=e["icon_id"],
              flavor_text=e["blurb"])
    it.collection_id = cid
    # what a seller asks for it (a quartermaster's Exalted mount; ui/screens/vendor_screen._unit_price)
    it.vendor_price = int(e["price"])
    return it


# ------------------------------------------------------------------ found in the world
def rare_drop(creature_name, rng=None):
    """The Collection id a kill of this open-world rare drops, or None (sheets H9 and H10, 19 Nov 2026: each wild
    mount drops, rarely, from one rare that fits it; tools/build_collection.py WILD_MOUNTS)."""
    import random
    roll = (rng or random).random
    for e in entries():
        eff = e.get("effect") or {}
        if eff.get("drops_from") == creature_name and roll() < float(eff.get("drop_chance", 0.0)):
            return e["id"]
    return None


def exalted_mount_of(faction_id):
    """The Collection id of the mount a faction's quartermaster sells at Exalted (sheets H11 to H13), or None."""
    for e in entries():
        if (e.get("effect") or {}).get("exalted_mount_of") == faction_id:
            return e["id"]
    return None


def art_ready(cid):
    """Mounts and forms can be learned before their art lands, but not used until it does."""
    e = get_entry(cid)
    if e is None:
        return False
    if e["kind"] == "mount":
        mid = e["effect"]["mount_id"]
        from world.collection_art import split_colourway
        cw = split_colourway(mid)
        base = cw[1] if cw else mid
        return all((MOUNT_DIR / f"{base}_{d}.png").exists() for d in DIRECTIONS)
    if e["kind"] == "form":
        if e["effect"].get("facings"):
            return all((ROOT / f"{e['effect']['facings']}_{d}.png").exists() for d in DIRECTIONS)
        return (ROOT / e["effect"]["sprite"]).exists() if e["effect"].get("sprite") else False
    return True


def on_learned(cid, party=None, player=None):
    """Whatever has to happen the moment something is learned, for the character being played."""
    e = get_entry(cid)
    if e is None:
        return
    try:
        from world.travel_manager import get_travel_manager
        tm = get_travel_manager()
    except Exception:
        tm = None
    eff = e["effect"]
    if tm is not None and eff.get("feather"):
        apply_feathers(tm)
    if eff.get("bonus_bank_tabs") and party is not None and getattr(party, "bank", None) is not None:
        apply_bank_bonus(party.bank)


# ------------------------------------------------------------------ mounts
def mount_def(mount_id):
    """A learned-or-not collection mount in TravelManager's mount shape, or None if it isn't one."""
    e = get_entry(mount_id)
    if e is None or e["kind"] != "mount":
        return None
    return {"id": mount_id, "name": e["effect"].get("mount_name") or e["name"], "tier": e["effect"].get("tier", 1),
            "price": 0, "vendors": [], "blurb": e["blurb"], "collection": True}


def collection_mount_ids():
    """Learned mounts that can be ridden (their art is in)."""
    return [e["id"] for e in learned_entries("mount") if art_ready(e["id"])]


# ------------------------------------------------------------------ forms
def form_ids():
    """Disguises you can wear on the map: learned, drawn, and not a class form's look."""
    return [e["id"] for e in learned_entries("form") if art_ready(e["id"]) and not e["effect"].get("look_of")]


#: class shapeshift forms drawn on the map in four facings (assets/forms/<form>_<facing>.png, sheets F1 and F2).
#: Kyle, 18 Nov 2026: "We need basic forms for shape shifting out of combat too for shifters."
CLASS_FORM_DIR = ROOT / "assets" / "forms"


def look_of(cid):
    """The class form a Collection look dresses (\"bear\"), or None."""
    e = get_entry(cid) or {}
    return (e.get("effect") or {}).get("look_of")


def look_slot(form_id):
    """The look a class form wears: its own, except the Bloodmage's three curses (Blood Curse, Accursed, Eternal), which
    share one, keyed "cursed" (Kyle, 27 Nov 2026: one worgen as the baseline, eleven looks sold on the AH for all of
    them)."""
    try:
        from combat.forms import CURSED_FORMS
    except Exception:
        CURSED_FORMS = ()
    return "cursed" if form_id in CURSED_FORMS else form_id


def class_form_path(form_id, facing, looks=None):
    """The picture a character in a class form walks the map as, relative to the game root, or None if that form
    isn't drawn. `looks` is TravelManager.form_looks: a learned, drawn look replaces the plain form."""
    if not form_id:
        return None
    slot = look_slot(form_id)
    cid = (looks or {}).get(slot)
    if cid and look_of(cid) == slot and learned(cid) and art_ready(cid):
        return f"{get_entry(cid)['effect']['facings']}_{facing}.png"
    if (CLASS_FORM_DIR / f"{form_id}_{facing}.png").exists():
        return f"assets/forms/{form_id}_{facing}.png"
    return None


def form_sprite_path(form_id):
    """The one picture a form is drawn with (ui/sprite_loader.get_form_sprite), relative to the game root."""
    e = get_entry(form_id) or {}
    return (e.get("effect") or {}).get("sprite")


def form_facing_path(form_id, facing):
    """A Collection form turned the way it's walking (sheets F6 and F7 turned the auction house's forms four ways,
    19 Nov 2026), relative to the game root, or None when it only has its one picture."""
    base = ((get_entry(form_id) or {}).get("effect") or {}).get("facings")
    if base and facing in ("down", "left", "right", "up") and (ROOT / f"{base}_{facing}.png").exists():
        return f"{base}_{facing}.png"
    return None


# ------------------------------------------------------------------ titles
def exalted_title(faction_id):
    """The title a faction gives at Exalted (tools/build_collection.py EXALTED_TITLES)."""
    return f"title_exalted_{faction_id}"


def grant(cid, commit=True):
    """Learn an EARNED collectable outright, with no bag item: an Exalted title is given the moment you reach it
    (Kyle, 18 Nov 2026: "each faction should get a title for reaching exalted with them"). True if newly learned.
    commit=False writes only the collection file (a catch-up while a save is loading, when there's no character
    to commit alongside it)."""
    import time
    if get_entry(cid) is None or learned(cid):
        return False
    col = collection()

    def go():
        col.learned[cid] = int(time.time())
        return True
    if commit:
        return bool(col.transact(go))
    go()
    return bool(col.save())


def keepsake_of(recruit_id):
    """The Collection id of the keepsake a recruit gives when they become Sworn (data/npcs/keepsakes.json)."""
    return f"keepsake_{recruit_id}"


def exalted_line(faction_id):
    """'You've earned a title: Guardian of Cenarius.' once a faction's Exalted title is learned, else ''."""
    cid = exalted_title(faction_id)
    e = get_entry(cid)
    if e is None or not learned(cid):
        return ""
    return f"You've earned a title: {e['name'].replace('Title: ', '')}."


def title_ids():
    return [e["id"] for e in learned_entries("title")]


def titled_name(name, title_id):
    """'Kyle the Undercutter' for a learned title, or the plain name."""
    e = get_entry(title_id) if title_id else None
    if e is None or e["kind"] != "title" or not learned(title_id):
        return name
    return e["effect"]["title"].replace("{name}", name)


# ------------------------------------------------------------------ travel
def feather_continents():
    return {e["effect"]["feather"] for e in learned_entries() if e["effect"].get("feather")}


def apply_feathers(tm):
    """Open every flight node on a learned feather's continent. Returns how many were new."""
    from world.travel_manager import travel_data
    conts = feather_continents()
    if not conts:
        return 0
    new = 0
    for node_id, node in travel_data()["flight_nodes"].items():
        if node.get("continent", "kalimdor") in conts and node_id not in tm.known_nodes:
            tm.known_nodes.add(node_id)
            new += 1
    return new


def hearth_cooldown_mult():
    m = 1.0
    for e in learned_entries():
        m *= float(e["effect"].get("hearth_cooldown_mult", 1.0))
    return m


def has_second_hearth():
    return any(e["effect"].get("second_hearth") for e in learned_entries())


def backpack_bonus():
    return int(_effect_sum("backpack_bonus"))


def bonus_bank_tabs():
    return int(_effect_sum("bonus_bank_tabs"))


def apply_bank_bonus(bank):
    """Open the free tab(s) the Deep Vault gives, past the bank's bought ones. Returns how many were added."""
    want = bonus_bank_tabs()
    have = getattr(bank, "bonus_tabs", 0)
    added = 0
    while have < want:
        bank.add_bonus_tab()
        have += 1
        added += 1
    return added


def free_riding_rank():
    return max([int(e["effect"].get("free_riding_rank", 0)) for e in learned_entries()] or [0])


def new_character_gifts():
    """{"copper": n, "bag": bool} for a brand new character (the Book of First Steps)."""
    out = {"copper": 0, "bag": False}
    for e in learned_entries():
        nc = e["effect"].get("new_character")
        if nc:
            out["copper"] += int(nc.get("copper", 0))
            out["bag"] = out["bag"] or bool(nc.get("bag"))
    return out


# ------------------------------------------------------------------ services
SERVICE_LABEL = {"bank": "Open your bank", "peddler": "Call the peddler", "mail": "Call the courier",
                 "class_trainer": "Open your class trainer", "profession_trainer": "Open a profession trainer",
                 "reagents": "Open the reagent seller"}


def service_ready(tm, cid, clock):
    """(ready, hours_left) for a portable service on this character."""
    used = (getattr(tm, "collection_used", None) or {}).get(cid)
    if used is None:
        return True, 0.0
    left = SERVICE_COOLDOWN_HOURS - (clock - used)
    return (left <= 0), max(0.0, left)


def mark_service_used(tm, cid, clock):
    if not hasattr(tm, "collection_used") or tm.collection_used is None:
        tm.collection_used = {}
    tm.collection_used[cid] = float(clock)


def peddler_vendor():
    """A pack-mule peddler who buys anything and sells nothing."""
    from world.vendor_manager import VendorNPC
    return VendorNPC("collection_peddler", "Gritt the Peddler", "", 0, 0, None, [], True, "neutral",
                     sells_gear=False, race="goblin",
                     greeting="Got junk? I buy junk. Got treasure? I buy that too, for less than it's worth.")


def reagent_vendor():
    """The Alchemist's Satchel: the Orgrimmar reagent vendor's shelf, carried."""
    from world.vendor_manager import VendorNPC, get_vendor_manager
    src = get_vendor_manager().get_vendor("org_reagent_vendor")
    sells = list(getattr(src, "sells", []) or [])
    return VendorNPC("collection_reagents", "Alchemist's Satchel", "", 0, 0, None, sells, True, "neutral",
                     sells_gear=False, greeting="Every reagent you'd want, in a satchel that clinks.")


class PortableTrainer:
    """What the travel service screen needs to know about a trainer you carry in a book."""

    def __init__(self, name, portable_class=None, portable_professions=None):
        self.name = name
        self.npc_id = None
        self.vendor_id = None
        self.portable_class = portable_class
        self.portable_professions = portable_professions


def all_professions():
    from world import profession_manager as pm
    profs = pm.professions()
    return list(profs.keys()) if isinstance(profs, dict) else [p.get("id") for p in profs]


# ------------------------------------------------------------------ heirlooms
# Kyle, 18 Nov 2026: "We should have the heirlooms as we need cloth, leather, mail, and plate. And all the weapons,
# shields, OH, etc.", "You know how heirlooms work", and then the families: "caster cloth, healer cloth, agi leather,
# healer leather, caster leather, dps mail, caster mail, healer mail. Dps plate, tank plate, hybrid plate, healer
# plate. So we can have some generalist stuff". Each heirloom is its own item with a set armour (or weapon) type and
# a set stat family, and it levels with whoever wears it. Its stats are a fixed recipe for the family (no random
# suffix), sized by the game's own item budget at the wearer's level.
EQUIP_SLOT = {"head": "head", "shoulder": "shoulder", "chest": "chest", "legs": "legs", "back": "back",
              "trinket": "trinket", "two_hand": "main_hand", "one_hand": "main_hand", "off_hand": "off_hand",
              "ranged": "ranged"}

#: Kyle's twelve armour families: armour type -> {family: words}
ARMOUR_FAMILIES = {"cloth": ("caster", "healer"), "leather": ("agi", "healer", "caster"),
                   "mail": ("agi", "caster", "healer"), "plate": ("str", "tank", "hybrid", "healer")}
#: the stat template each family stands in for, so everything that reads stat_template keeps working
FAMILY_TEMPLATE = {"caster": "int_caster", "healer": "spi_healer", "agi": "agi_physical", "str": "str_physical",
                   "tank": "str_physical", "hybrid": "str_int_hybrid"}
#: an heirloom's stats against a blue of the same level (Kyle: "slightly worse")
HEIRLOOM_BUDGET = 0.85
#: the share of the item's budget each stat gets
RECIPES = {
    "caster": {"intellect": .40, "stamina": .25, "spell_power": .25, "crit_chance_spell": .10},
    "healer": {"intellect": .35, "spirit": .20, "stamina": .20, "healing_power": .25},
    "agi": {"agility": .50, "stamina": .30, "attack_power": .10, "crit_chance_physical": .10},
    "str": {"strength": .50, "stamina": .30, "attack_power": .10, "crit_chance_physical": .10},
    "tank": {"stamina": .45, "strength": .25, "defense_rating": .15, "dodge_rating": .15},
    "hybrid": {"strength": .35, "intellect": .25, "stamina": .25, "spell_power": .15},
}


def armour_family(spec):
    """Which of Kyle's twelve armour families a spec (a spec_gear.json entry) wears."""
    a, t, role = spec["armor_type"], spec["stat_template"], spec.get("role")
    if t == "spi_healer":
        return "healer"
    if t == "int_caster":
        return "healer" if a == "plate" else "caster"
    if a == "plate":
        if role == "tank":
            return "tank"
        return "hybrid" if t == "str_int_hybrid" else "str"
    return "agi"


def weapon_family(spec):
    """The stat family a spec's heirloom weapons, cloak and trinket come in."""
    t, role = spec["stat_template"], spec.get("role")
    if role == "tank" and spec["armor_type"] == "plate":
        return "tank"
    return {"int_caster": "caster", "spi_healer": "healer", "str_physical": "str", "str_int_hybrid": "hybrid",
            "agi_physical": "agi", "agi_int_hybrid": "agi"}[t]


_BLUE = {}


def _blue_points(gen, slot, level, armour, family, weapon_type=None):
    """What a blue of this slot and level is really worth, in budget points: the mean of a dozen rolls of the loot
    generator itself (sockets, rounding and bonus rolls included), so an heirloom tracks real drops at every level."""
    key = (slot, level, armour, weapon_type, family)
    if key in _BLUE:
        return _BLUE[key]
    cost = gen.stat_budget_costs
    tpl = FAMILY_TEMPLATE[family]
    state = random.getstate()
    pts = []
    try:
        for k in range(12):
            random.seed(f"blue|{key}|{k}")
            if weapon_type:
                it = gen.generate_weapon(slot, weapon_type, tpl, level, "rare")
            else:
                it = gen.generate_armor_piece(slot, armour, tpl, level, "rare")
            if it is not None:
                pts.append(sum(v * cost.get(st, 1.0) for d in (it.primary_stats, it.secondary_stats)
                               for st, v in d.items()))
    finally:
        random.setstate(state)
    _BLUE[key] = (sum(pts) / len(pts)) if pts else 0.0
    return _BLUE[key]


def _heirloom_stats(gen, slot, level, family, armour=None, weapon_type=None):
    """The family's recipe, worth HEIRLOOM_BUDGET of a blue of the same slot and level (Kyle: "slightly worse than
    items of the same level as they have the exp boost in them")."""
    from entities.item import whole
    from entities.loot_generator import RATING_FLOOR, _RATING_KEYS
    total = _blue_points(gen, slot, level, armour, family, weapon_type) * HEIRLOOM_BUDGET
    prim, sec, spare = {}, {}, 0.0
    primary = {"strength", "agility", "intellect", "stamina", "spirit"}
    for stat, w in RECIPES[family].items():
        cost = gen.stat_budget_costs.get(stat, 1.0)
        raw = total * w / cost
        v = whole(raw)
        if (stat in _RATING_KEYS and v < RATING_FLOOR) or v <= 0:
            spare += raw * cost
            continue
        spare += (raw - v) * cost
        (prim if stat in primary else sec)[stat] = v
    main = max(prim, key=prim.get) if prim else "stamina"
    if spare >= 1:
        prim[main] = prim.get(main, 0) + whole(spare)
    if not prim:
        prim[main] = 1
    return prim, sec


def can_take_heirloom(cid, character, party=None):
    """(ok, reason) for taking a copy of heirloom `cid` for `character` (one copy per save at a time)."""
    e = get_entry(cid)
    if e is None or e["kind"] != "heirloom":
        return False, "That isn't an heirloom."
    if not learned(cid):
        return False, "You haven't learned that heirloom yet."
    item = make_heirloom(cid, character)
    if item is None:
        return False, "That heirloom couldn't be made."
    from entities.proficiency import can_equip
    ok, why = can_equip(character, item)
    if not ok and "level" not in why.lower():
        return False, why
    if heirloom_copy_exists(cid, party, character):
        return False, "You already have a copy with you (one at a time)."
    return True, ""


def _all_items(party, character):
    who = list(getattr(party, "members", None) or []) if party is not None else []
    if character is not None and character not in who:
        who.append(character)
    for m in who:
        for it in (getattr(m, "inventory", None) or []):
            yield it
        eq = getattr(m, "equipment", None)
        for it in (getattr(eq, "slots", {}) or {}).values():
            if it is not None:
                yield it
    bank = getattr(party, "bank", None) if party is not None else None
    for tab in (getattr(bank, "tabs", None) or []):
        for it in tab:
            if it is not None:
                yield it


def heirloom_copy_exists(cid, party, character=None):
    return any(getattr(it, "heirloom_id", None) == cid for it in _all_items(party, character))


def make_heirloom(cid, character):
    """A blue copy of heirloom `cid` at `character`'s level: its own armour or weapon type and stat family."""
    e = get_entry(cid)
    if e is None or e["kind"] != "heirloom":
        return None
    eff = e["effect"]
    slot = EQUIP_SLOT[eff["heirloom_slot"]]
    family = eff["family"]
    tpl = FAMILY_TEMPLATE[family]
    level = max(1, int(getattr(character, "level", 1)))
    gen = _generator()
    state = random.getstate()
    random.seed(f"{cid}|{level}")
    try:
        if eff.get("weapon_type"):
            item = gen.generate_weapon(slot, eff["weapon_type"], tpl, level, "rare")
        else:
            item = gen.generate_armor_piece(slot, eff.get("armor_type"), tpl, level, "rare")
        if item is None:
            return None
        if eff.get("weapon_type") != "shield":
            item.primary_stats, item.secondary_stats = _heirloom_stats(gen, slot, level, family, eff.get("armor_type"),
                                                                       eff.get("weapon_type"))
    except Exception:
        return None
    finally:
        random.setstate(state)
    item.sockets = []
    item.heirloom_id = cid
    item.required_level = 1
    item.sell_price = 0
    item.name = e["name"]
    xp = eff.get("xp_pct", 0)
    item.flavor_text = ((f"+{xp}% experience while worn, until level {XP_CAP_LEVEL}. " if xp else "")
                        + "It grows with whoever wears it.")
    return item


_GEN = None


def _generator():
    global _GEN
    if _GEN is None:
        from entities.loot_generator import LootGenerator
        _GEN = LootGenerator()
    return _GEN


def refit_heirloom(item, character):
    """Re-make an heirloom copy's stats at the wearer's level, in place. True if it changed."""
    cid = getattr(item, "heirloom_id", None)
    if not cid:
        return False
    fresh = make_heirloom(cid, character)
    if fresh is None or fresh.item_level == item.item_level and fresh.primary_stats == item.primary_stats:
        return False
    keep = {"enchant_id": item.enchant_id, "sockets": item.sockets}
    for k in ("item_level", "primary_stats", "secondary_stats", "armor_value", "weapon_damage_min",
              "weapon_damage_max", "attack_speed", "block_value", "armor_type", "weapon_type", "stat_template",
              "name", "icon_id", "proc"):
        setattr(item, k, getattr(fresh, k))
    item.enchant_id = keep["enchant_id"]
    item.sockets = keep["sockets"]
    return True


def refit_worn_heirlooms(character):
    """Called on level up: every heirloom the character is wearing or carrying grows with them."""
    n = 0
    for it in list(getattr(character, "inventory", None) or []):
        n += refit_heirloom(it, character)
    eq = getattr(character, "equipment", None)
    for it in (getattr(eq, "slots", {}) or {}).values():
        if it is not None:
            n += refit_heirloom(it, character)
    return n


_LEADER = None


def set_leader(character):
    """Who the party's heirloom bonus is read from (entities/party.py sets it to the player)."""
    global _LEADER
    _LEADER = character


def leader_heirloom_pct():
    """The bonus from the heirlooms the party LEADER is wearing, capped at Kyle's +80%."""
    eq = getattr(_LEADER, "equipment", None)
    total = 0
    for it in (getattr(eq, "slots", {}) or {}).values():
        cid = getattr(it, "heirloom_id", None) if it is not None else None
        if cid:
            e = get_entry(cid)
            if e is not None:
                total += int(e["effect"].get("xp_pct", 0))
    return min(XP_CAP_PCT, total)


def heirloom_xp_pct(character):
    """The experience bonus `character` gets from heirlooms. Kyle, 18 Nov 2026: "They also affect the whole party
    so the main player wears them and party quest / kill exp improves so the main character doesn't blow past his
    allies." So it's the LEADER's heirlooms that count, for everyone in the party; nothing at 60."""
    if int(getattr(character, "level", 1)) >= XP_CAP_LEVEL:
        return 0
    return leader_heirloom_pct()
