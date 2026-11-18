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
        ("heirloom", "Heirlooms"))
#: tomes sit on the Travel tab with the feathers and the hearths
TAB_OF = {"mount": "mount", "form": "form", "title": "title", "travel": "travel", "tome": "travel",
          "service": "service", "heirloom": "heirloom"}

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
    return it


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
    return [e["id"] for e in learned_entries("form") if art_ready(e["id"])]


def form_sprite_path(form_id):
    """The one picture a form is drawn with (ui/sprite_loader.get_form_sprite), relative to the game root."""
    e = get_entry(form_id) or {}
    return (e.get("effect") or {}).get("sprite")


# ------------------------------------------------------------------ titles
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
#: (heirloom slot -> the equipment slot it's made for)
HEIRLOOM_SLOTS = {"head": "head", "shoulder": "shoulder", "chest": "chest", "legs": "legs", "back": "back",
                  "trinket": "trinket1", "two_hand": "main_hand", "one_hand": "main_hand", "shield": "off_hand",
                  "off_hand": "off_hand"}
HEIRLOOM_WORDS = {"head": "Helm", "shoulder": "Shoulders", "chest": "Chestguard", "legs": "Legguards",
                  "back": "Cloak", "trinket": "Keepsake", "shield": "Shield", "off_hand": "Off-Hand"}


def _spec_of(character):
    from entities.proficiency import active_spec
    spec = active_spec(character)
    gear = _spec_gear()
    if spec in gear:
        return spec, gear[spec]
    for k, v in gear.items():
        if isinstance(v, dict) and v.get("class") == getattr(character, "char_class", None):
            return k, v
    return None, {}


_SPEC_GEAR = None


def _spec_gear():
    global _SPEC_GEAR
    if _SPEC_GEAR is None:
        _SPEC_GEAR = {k: v for k, v in json.loads((ROOT / "data/items/spec_gear.json").read_text(
            encoding="utf-8")).items() if not k.startswith("_")}
    return _SPEC_GEAR


_WEAPONS = None


def _weapons():
    global _WEAPONS
    if _WEAPONS is None:
        _WEAPONS = json.loads((ROOT / "data/items/weapon_types.json").read_text(encoding="utf-8"))
    return _WEAPONS


def _class_weapons(char_class):
    return list((_weapons().get("class_weapon_map", {}) or {}).get(char_class, []) or [])


def _hand(wt):
    return (_weapons()["weapon_types"].get(wt) or {}).get("hand")


def heirloom_weapon_type(slot, character):
    """Which weapon type an heirloom weapon becomes for this character, or None if their class can't use one."""
    _spec, sg = _spec_of(character)
    mine = _class_weapons(character.char_class)
    want = (sg.get("weapons") or {})
    caster = (sg.get("stat_template") or "").endswith(("caster", "healer"))
    if slot == "two_hand":
        if want.get("main_hand") in mine and _hand(want.get("main_hand")) == "two_hand":
            return want["main_hand"]
        order = (["staff"] if caster else []) + ["sword_2h", "axe_2h", "mace_2h", "polearm", "staff"]
        return next((w for w in order if w in mine), None)
    if slot == "one_hand":
        if want.get("main_hand") in mine and _hand(want.get("main_hand")) == "main_or_off":
            return want["main_hand"]
        order = (["mace_1h", "dagger"] if caster else []) + ["sword_1h", "axe_1h", "mace_1h", "dagger", "fist_weapon"]
        return next((w for w in order if w in mine), None)
    if slot == "shield":
        return "shield" if "shield" in mine else None
    if slot == "off_hand":
        if "tome" in mine:
            return "tome"
        from entities.proficiency import dual_wield_level
        if dual_wield_level(character):
            return heirloom_weapon_type("one_hand", character)
        return None
    return None


def can_take_heirloom(cid, character, party=None):
    """(ok, reason) for taking a copy of heirloom `cid` for `character` (one copy per save at a time)."""
    e = get_entry(cid)
    if e is None or e["kind"] != "heirloom":
        return False, "That isn't an heirloom."
    if not learned(cid):
        return False, "You haven't learned that heirloom yet."
    slot = e["effect"]["heirloom_slot"]
    if slot in ("two_hand", "one_hand", "shield", "off_hand") and heirloom_weapon_type(slot, character) is None:
        return False, f"A {character.char_class} can't use the {e['name']}."
    if heirloom_copy_exists(cid, party, character):
        return False, f"You already have the {e['name']} with you (one copy at a time)."
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
    """A blue heirloom copy of `cid`, fitted to `character` at their level. None if they can't use it."""
    e = get_entry(cid)
    if e is None:
        return None
    slot = e["effect"]["heirloom_slot"]
    spec, sg = _spec_of(character)
    template = sg.get("stat_template")
    school = sg.get("school")
    level = max(1, int(getattr(character, "level", 1)))
    gen = _generator()
    state = random.getstate()
    random.seed(f"{cid}|{character.char_class}|{spec}|{level}")
    try:
        if slot in ("two_hand", "one_hand", "shield", "off_hand"):
            wt = heirloom_weapon_type(slot, character)
            if wt is None:
                return None
            equip = "off_hand" if slot in ("shield", "off_hand") else "main_hand"
            item = gen.generate_item_for_class(character.char_class, level, slot=equip, rarity="rare",
                                               weapon_type=wt, stat_template=template, school=school)
        else:
            item = gen.generate_item_for_class(character.char_class, level, slot=HEIRLOOM_SLOTS[slot],
                                               rarity="rare", stat_template=template, school=school)
    finally:
        random.setstate(state)
    if item is None:
        return None
    item.heirloom_id = cid
    item.required_level = 1
    item.sell_price = 0
    word = HEIRLOOM_WORDS.get(slot)
    if slot in ("two_hand", "one_hand") or (slot == "off_hand" and item.weapon_type != "tome"):
        word = (_weapons()["weapon_types"].get(item.weapon_type) or {}).get("display_name", "Blade")
    elif slot == "off_hand":
        word = "Tome"
    item.name = f"Heirloom {word}"
    item.flavor_text = f"+{e['effect']['xp_pct']}% experience while worn, until level {XP_CAP_LEVEL}. " \
                       f"It grows with whoever wears it."
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


def heirloom_xp_pct(character):
    """The experience bonus from the heirlooms this character is wearing, capped at Kyle's +80%, 0 at 60."""
    if int(getattr(character, "level", 1)) >= XP_CAP_LEVEL:
        return 0
    eq = getattr(character, "equipment", None)
    total = 0
    for it in (getattr(eq, "slots", {}) or {}).values():
        cid = getattr(it, "heirloom_id", None) if it is not None else None
        if cid:
            e = get_entry(cid)
            if e is not None:
                total += int(e["effect"].get("xp_pct", 0))
    return min(XP_CAP_PCT, total)
