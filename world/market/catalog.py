"""The catalog: everything an NPC may list on the auction house, what it's worth, and where it goes in the tree.

docs/auction_house_design.md, section 3. Built once per run from the game's own data (materials, consumables,
recipes, named epics, boss loot, recipe scrolls) and cached. Nothing a hidden place hands out is ever in it: no
secret recipe, no secret seller's item, no hidden boss's loot, no material that only exists in a hidden place, and
nothing staged for after level 60.

Values are copper per unit at a level market (price index 1.0). The formulas, with Kyle's reasons:

    raw material     sell x (3.0 + 1.1 ln(1 + uses)) x tier          "crafting materials will be huge"
    made thing       max(inputs x 1.25 (1.10 for bars, bolts, planks), 3 x sell), worked recursively
    gear             sell x rarity x (0.55 + 0.9 want)                "epics have a larger sell price while blues
                                                                        and greens are closer to sales"

`want` is the share of the 97 specs (data/items/spec_gear.json, all thirty classes) that would wear or wield the
piece, so a purple nobody wants is cheap for a purple and a green that half the game wants sells above the vendor.
"""
import json
import math
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent

TIER_MULT = {"starter": 1.0, "early": 1.0, "kit": 1.0, "mid": 1.1, "late": 1.2, "endgame": 1.3}
TIER_LEVEL = {"starter": 1, "early": 10, "kit": 15, "mid": 25, "late": 40, "endgame": 52}
RARITY_G = {"poor": 0.6, "common": 0.9, "uncommon": 1.3, "rare": 2.2, "epic": 8.0, "legendary": 12.0}


def level_premium(level):
    """Gear's vendor price climbs with the square of its level and quest gold only in a line, so without this a
    level 10 green costs a fifth of one quest's gold and a level 58 one three. This lifts low-level gear so a piece
    worth wearing costs about one to two quests' gold at every level (x3.8 at 10, x2.4 at 30, x1 at 60)."""
    lv = max(1, min(60, int(level or 1)))
    return 1.0 + 3.5 * (1.0 - lv / 60.0) ** 1.3


def fit_mult(w):
    """How much a piece's fit moves its price: 0.5 for a piece almost nobody wants, 3.5 for one a dozen specs want.
    Steep on purpose. Kyle, 15 Nov 2026: "we dont want AH as just a free way to instantly gear up with no
    effort....it'll get EXPENSIVE fast to try to gear everyone with just AH". The pieces worth wearing cost real
    money; the odd rolls are cheap because nobody wants them."""
    return 0.5 + 3.0 * max(0.0, min(1.0, w)) ** 1.5
RARITY_ORDER = ["poor", "common", "uncommon", "rare", "epic", "legendary"]
#: intermediates take a smaller premium over their inputs than finished goods (design, section 3)
INTERMEDIATE = {"bar", "bolt", "plank", "fiber", "pages", "stick", "leather"}
#: a crafted consumable a vendor also sells can't be worth more than the shop's price
VENDOR_CAP = 1.05

# ------------------------------------------------------------------ the tree (design, section 12)
WEAPON_SUBS = [
    ("One-Handed Axes", {"axe_1h"}), ("Two-Handed Axes", {"axe_2h"}),
    ("One-Handed Maces", {"mace_1h"}), ("Two-Handed Maces", {"mace_2h"}),
    ("One-Handed Swords", {"sword_1h"}), ("Two-Handed Swords", {"sword_2h"}),
    ("Daggers", {"dagger"}), ("Fist Weapons", {"fist_weapon"}), ("Polearms", {"polearm"}),
    ("Staves", {"staff"}), ("Bows", {"bow"}), ("Crossbows", {"crossbow"}), ("Guns", {"gun"}),
    ("Wands", {"wand"}), ("Thrown", {"thrown"}), ("Relics", {"totem", "libram", "idol"}),
]
ARMOR_SUBS = ["Cloth", "Leather", "Mail", "Plate", "Shields", "Held in Off-hand", "Cloaks", "Neck and Rings",
              "Trinkets"]
CONSUMABLE_SUBS = ["Potions", "Elixirs", "Food and Drink", "Explosives", "Gadgets", "Ammunition", "Other"]
TRADE_SUBS = ["Cloth", "Leather", "Metal and Stone", "Herbs", "Wood", "Cooking", "Elemental", "Creature Parts",
              "Parts", "Other"]
ENHANCE_SUBS = ["Enchants", "Enchanting Materials", "Gems", "Runes and Inks", "Upgrade Kits"]
RECIPE_SUBS = ["Alchemy", "Blacksmithing", "Cooking", "Enchanting", "Engineering", "Jewelcrafting",
               "Leatherworking", "Runecrafting", "Tailoring", "Woodworking", "Other"]

TREE = [
    ("Weapons", [s for s, _ in WEAPON_SUBS]),
    ("Armor", ARMOR_SUBS),
    ("Containers", []),
    ("Consumables", CONSUMABLE_SUBS),
    ("Trade Goods", TRADE_SUBS),
    ("Item Enhancements", ENHANCE_SUBS),
    ("Recipes", RECIPE_SUBS),
    # the Collection's account-wide unlocks (docs/collection_design.md)
    ("Collection", ["Mounts", "Forms", "Travel", "Services", "Heirlooms"]),
    ("Miscellaneous", []),
]

MATERIAL_SUB = {
    "cloth": ("Trade Goods", "Cloth"), "bolt": ("Trade Goods", "Cloth"), "fiber": ("Trade Goods", "Cloth"),
    "leather": ("Trade Goods", "Leather"),
    "ore": ("Trade Goods", "Metal and Stone"), "bar": ("Trade Goods", "Metal and Stone"),
    "herb": ("Trade Goods", "Herbs"),
    "wood": ("Trade Goods", "Wood"), "plank": ("Trade Goods", "Wood"), "stick": ("Trade Goods", "Wood"),
    "meat": ("Trade Goods", "Cooking"), "fish": ("Trade Goods", "Cooking"),
    "crystal": ("Trade Goods", "Elemental"),
    "mob_reagent": ("Trade Goods", "Creature Parts"),
    "part": ("Trade Goods", "Parts"), "reagent": ("Trade Goods", "Other"), "pages": ("Trade Goods", "Other"),
    "kit": ("Trade Goods", "Other"), "rod": ("Trade Goods", "Other"),
    "enchant_scroll": ("Item Enhancements", "Enchants"),
    "enchant_mat": ("Item Enhancements", "Enchanting Materials"),
    "gem": ("Item Enhancements", "Gems"), "cut_gem": ("Item Enhancements", "Gems"),
    "rune": ("Item Enhancements", "Runes and Inks"), "rune_ink": ("Item Enhancements", "Runes and Inks"),
    "upgrade_kit": ("Item Enhancements", "Upgrade Kits"),
}
CONSUMABLE_SUB = {
    "health_potion": "Potions", "mana_potion": "Potions", "status_potion": "Potions", "revive": "Potions",
    "elixir": "Elixirs", "food": "Food and Drink", "drink": "Food and Drink", "meal": "Food and Drink",
    "explosive": "Explosives", "gadget": "Gadgets", "ammo": "Ammunition", "lure": "Other",
}
#: Material rarity for the rarity filter and the colour of the name (materials carry none of their own).
MATERIAL_RARITY = {"cut_gem": "uncommon", "gem": "uncommon", "enchant_scroll": "uncommon", "rune": "uncommon",
                   "upgrade_kit": "uncommon", "rod": "rare"}


def _load(rel):
    p = ROOT / rel
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _slug(name):
    return str(name).lower().replace("'", "").replace(" ", "_")


# ================================================================== recipes
@lru_cache(maxsize=1)
def recipes():
    """[(profession, recipe_id, recipe)] for every recipe the open world can teach. Secret recipes (a hidden
    seller's, or anything marked secret), faction-locked hidden ones and content staged past 60 are left out."""
    out = []
    nested = _load("data/crafting/recipes.json").get("professions", {})
    for prof, g in nested.items():
        for rid, r in (g.get("recipes") or {}).items():
            out.append((prof, rid, r))
    for prof in ("leatherworking", "blacksmithing", "jewelcrafting", "enchanting", "runecrafting"):
        for rid, r in (_load(f"data/{prof}/recipes.json").get("recipes") or {}).items():
            out.append((prof, rid, r))
    keep = []
    for prof, rid, r in out:
        if rid.startswith("_") or rid.startswith("secret") or r.get("secret") or r.get("sold_by"):
            continue
        if r.get("staged_post_60"):
            continue
        keep.append((prof, rid, r))
    return keep


@lru_cache(maxsize=1)
def _uses():
    """{material_id: number of open recipes that ask for it}"""
    n = {}
    for _p, _rid, r in recipes():
        for mid in (r.get("inputs") or {}):
            n[mid] = n.get(mid, 0) + 1
    for r in (_load("data/gathering/smelting_recipes.json").get("recipes") or {}).values():
        for mid in (r.get("inputs") or {}):
            n[mid] = n.get(mid, 0) + 1
    return n


@lru_cache(maxsize=1)
def _producers():
    """{output id: [(inputs, made, profession, recipe)]} for materials and consumables made by open recipes."""
    out = {}
    for prof, _rid, r in recipes():
        o = r.get("output") or {}
        if r.get("no_xp"):
            continue                       # swapping three lesser essences for a greater isn't making anything
        oid = o.get("material_id") if o.get("kind") == "material" else (
            o.get("consumable_id") if o.get("kind") == "consumable" else None)
        if oid:
            out.setdefault(oid, []).append((r.get("inputs") or {}, max(1, int(r.get("count", 1) or 1)), prof, r))
    for bar, r in (_load("data/gathering/smelting_recipes.json").get("recipes") or {}).items():
        out.setdefault(r.get("output", bar), []).append((r.get("inputs") or {}, 1, "smelting", r))
    return out


@lru_cache(maxsize=1)
def _vendor_stock():
    """Ids a public vendor sells. Nobody buys those on the auction house."""
    s = set()
    for v in (_load("data/npcs/vendors.json").get("vendors") or []):
        if v.get("hidden"):
            continue
        for i in v.get("sells", []) or []:
            s.add(i if isinstance(i, str) else (i.get("id") or i.get("item_id") or ""))
    return s


# ================================================================== materials
@lru_cache(maxsize=1)
def _hidden_zone_slugs():
    try:
        from world.hidden_zones import registry
        return {_slug(z) for z in registry()}
    except Exception:
        return set()


@lru_cache(maxsize=1)
def _raw_sources():
    """Material ids the open world hands out raw (gathered, fished, dropped, skinned, prospected)."""
    ok = set()
    hidden = _hidden_zone_slugs()
    for zone, z in (_load("data/gathering/node_pools.json").get("zones") or {}).items():
        if _slug(zone) in hidden:
            continue
        ok.update((z.get("table") or {}).keys())
        ok.update(((z.get("fishing") or {}).get("table") or {}).keys())
    for ore, rows in (_load("data/gathering/gem_drops.json").get("drops") or {}).items():
        for gid, _c in rows:
            ok.add(gid)
    for mod in ("cloth_drops", "skinning_drops", "meat_drops"):
        try:
            m = __import__(f"entities.{mod}", fromlist=["BANDS"])
            for _lo, _hi, table in m.BANDS:
                ok.update(table.keys())
        except Exception:
            pass
    try:
        from world.gathering_manager import GatheringNodeManager
        for ids in GatheringNodeManager.CRYSTAL_FROM_VEIN.values():
            ok.update(ids)
    except Exception:
        pass
    ok.update((_load("data/creatures/mob_materials.json").get("materials") or {}).keys())
    # DISENCHANTING (world/enchanting.py): green, blue and purple gear breaks into dust, essences and shards, and
    # at the top a Nexus Crystal. Left out, nothing an enchanter or a runecrafter makes was "obtainable", so the
    # auction house carried no enchanting materials, no rune inks, no runes and no enchant scrolls at all.
    for row in (_load("data/enchanting/enchants.json").get("disenchant") or []):
        for k in ("dust", "essence", "shard"):
            if row.get(k):
                ok.add(row[k])
    if "nexus_crystal" in materials():
        ok.add("nexus_crystal")
    return ok


@lru_cache(maxsize=1)
def _band_levels():
    """{material_id: typical level} from the drop bands (cloth, leather, meat) and creature materials."""
    lv = {}
    for mod in ("cloth_drops", "skinning_drops", "meat_drops"):
        try:
            m = __import__(f"entities.{mod}", fromlist=["BANDS"])
            for lo, hi, table in m.BANDS:
                for mid in table:
                    lv.setdefault(mid, []).append((lo + min(hi, 60)) / 2)
        except Exception:
            pass
    for mid, d in (_load("data/creatures/mob_materials.json").get("materials") or {}).items():
        lo, hi = d.get("levels", [1, 60])
        lv.setdefault(mid, []).append((lo + hi) / 2)
    return {k: sum(v) / len(v) for k, v in lv.items()}


@lru_cache(maxsize=1)
def materials():
    return _load("data/gathering/materials.json").get("materials", {})


@lru_cache(maxsize=1)
def consumables():
    out = {}
    for cat, rows in _load("data/consumables/consumable_types.json").items():
        if isinstance(rows, list):
            for c in rows:
                if isinstance(c, dict) and c.get("consumable_id"):
                    out[c["consumable_id"]] = c
    return out


@lru_cache(maxsize=1)
def obtainable():
    """Material and consumable ids the open world can actually produce: raw sources, then anything an open
    recipe makes from obtainable inputs (worked to a fixed point), plus whatever a public vendor sells."""
    ok = set(_raw_sources()) | set(_vendor_stock())
    mats = materials()
    ok = {m for m in ok if not (mats.get(m) or {}).get("secret")}
    changed = True
    prods = _producers()
    while changed:
        changed = False
        for oid, ways in prods.items():
            if oid in ok:
                continue
            for inputs, _made, _prof, _r in ways:
                if inputs and all(i in ok for i in inputs):
                    ok.add(oid)
                    changed = True
                    break
    return ok


def _level_of_skill(skill):
    return max(1, min(60, int(round(1 + (skill or 0) / 5))))


@lru_cache(maxsize=None)
def material_level(mid):
    bl = _band_levels().get(mid)
    if bl is not None:
        return max(1, min(60, int(round(bl))))
    m = materials().get(mid) or {}
    sr = m.get("skill_range")
    if sr:
        return _level_of_skill(sr[0])
    ways = _producers().get(mid)
    if ways:
        inputs, _made, _prof, r = ways[0]
        if r.get("skill_required") is not None and r is not None:
            return _level_of_skill(r.get("skill_required", 0))
        lv = [material_level(i) for i in inputs if i in materials()]
        if lv:
            return max(lv)
    return TIER_LEVEL.get(m.get("tier"), 20)


_VALUE_STACK = set()


@lru_cache(maxsize=None)
def value(item_key_id, kind="material"):
    """Fair copper per unit for a material or consumable id (design, section 3). 0 when unknown."""
    if item_key_id in _VALUE_STACK:          # a cycle in the recipes: fall back to the plain rule
        return 0
    _VALUE_STACK.add(item_key_id)
    try:
        return _value(item_key_id, kind)
    finally:
        _VALUE_STACK.discard(item_key_id)


def _value(mid, kind):
    if kind == "consumable":
        c = consumables().get(mid) or {}
        sell = int(c.get("sell_price", 0) or 0)
        made = _made_value(mid, finished=True)
        v = max(made, 3 * sell) if made else 4 * sell
        if mid in _vendor_stock() and c.get("vendor_price"):
            v = min(v, int(c["vendor_price"] * 0.9))
        return max(1, int(round(v)))
    m = materials().get(mid) or {}
    sell = int(m.get("sell_price", 0) or 0)
    mtype = m.get("material_type")
    made = _made_value(mid, finished=mtype not in INTERMEDIATE)
    uses = min(40, _uses().get(mid, 0))
    raw = sell * (3.0 + 1.1 * math.log(1 + uses)) * TIER_MULT.get(m.get("tier"), 1.0)
    if made:
        v = max(made, 3 * sell)
        if mid in _raw_sources():            # a gem you can prospect OR cut: whichever is dearer
            v = max(v, raw)
    else:
        v = raw
    if mid in _vendor_stock() and m.get("vendor_price"):
        v = min(v, int(m["vendor_price"] * VENDOR_CAP))
    v *= premium(mid, mtype)
    return max(1, int(round(v)))


#: Kyle, 16 Nov 2026: "we can also sell runes at a ridiculous price....as well as scrolls that contain the enchants on
#: them and can be used... Like wow, these will be cheap for trash ones to stupid expensive for rare ones."
#: An enchant scroll is worth its inputs times this, by its tier (0 the first minor ones, 5 the Major ones at 58),
#: and a proc enchantment (Crusader, Fiery Weapon) far more. A rune is worth its inputs times RUNE_PREMIUM by rank.
SCROLL_PREMIUM = {0: 1.0, 1: 1.3, 2: 1.8, 3: 2.6, 4: 4.0, 5: 6.0}
PROC_PREMIUM = 12.0
RUNE_PREMIUM = {1: 8.0, 2: 12.0, 3: 18.0}


def premium(mid, mtype):
    if mtype == "enchant_scroll":
        try:
            from world.enchanting import enchant
            e = enchant(mid) or {}
        except Exception:
            e = {}
        if e.get("proc"):
            return PROC_PREMIUM
        return SCROLL_PREMIUM.get(int(e.get("tier", 0) or 0), 1.0)
    if mtype == "rune":
        rank = mid.rsplit("_", 1)[-1]
        return RUNE_PREMIUM.get(int(rank) if rank.isdigit() else 1, 8.0)
    return 1.0


def _made_value(oid, finished=True):
    ways = _producers().get(oid)
    if not ways:
        return 0
    best = None
    for inputs, made, _prof, _r in ways:
        cost = 0
        for iid, q in inputs.items():
            k = "consumable" if iid in consumables() and iid not in materials() else "material"
            v = value(iid, k)
            if not v:
                cost = None
                break
            cost += v * q
        if cost is None:
            continue
        per = cost / made * (1.25 if finished else 1.10)
        best = per if best is None else min(best, per)     # the cheapest way anybody makes it
    return best or 0


# ================================================================== gear
@lru_cache(maxsize=1)
def specs():
    return _load("data/items/spec_gear.json")


def infer_template(item):
    t = getattr(item, "stat_template", None)
    if t:
        return t
    p = getattr(item, "primary_stats", None) or {}
    s, a, i, sp = p.get("strength", 0), p.get("agility", 0), p.get("intellect", 0), p.get("spirit", 0)
    top = max(s, a, i)
    if top <= 0:
        return "spi_healer" if sp else None
    if i == top and sp > i * 0.6:
        return "spi_healer"
    if i == top and max(s, a) >= i * 0.6:
        return "str_int_hybrid" if s >= a else "agi_int_hybrid"
    if (s == top or a == top) and i >= top * 0.6:
        return "str_int_hybrid" if s == top else "agi_int_hybrid"
    return {s: "str_physical", a: "agi_physical", i: "int_caster"}[top]


HYBRID_PARTS = {"str_int_hybrid": ("str_physical", "int_caster"), "agi_int_hybrid": ("agi_physical", "int_caster")}


def want(item):
    """Share of the 97 specs that would put this on, 0..1 (1 at twelve or more)."""
    t = infer_template(item)
    slot = str(getattr(item, "slot", "") or "")
    armor = getattr(item, "armor_type", None)
    weapon = getattr(item, "weapon_type", None)
    n = 0.0
    for sp in specs().values():
        st = sp.get("stat_template")
        if t is None:
            fit = 0.3
        elif st == t:
            fit = 1.0
        elif t in HYBRID_PARTS and st in HYBRID_PARTS[t]:
            fit = 0.5
        elif st in HYBRID_PARTS and t in HYBRID_PARTS[st]:
            fit = 0.5
        else:
            fit = 0.0
        if not fit:
            continue
        if weapon:
            if weapon not in (sp.get("weapons") or {}).values():
                continue
        elif armor in ("cloth", "leather", "mail", "plate"):
            if sp.get("armor_type") != armor:
                continue
        n += fit
    return min(1.0, n / 12.0)


def gear_value(item, crafted_inputs=None):
    from entities.pricing import gear_sell_price
    sell = int(getattr(item, "sell_price", 0) or 0) or gear_sell_price(
        getattr(item, "item_level", 1), getattr(item, "rarity", "common"), getattr(item, "slot", "chest"),
        getattr(item, "weapon_type", None))
    if getattr(item, "bag_capacity", 0):
        vp = getattr(item, "vendor_price", None) or sell * 4
        return max(1, int(vp * 0.9))
    if getattr(item, "recipe_id", None):
        return recipe_scroll_value(item)
    g = RARITY_G.get(getattr(item, "rarity", "common"), 1.0)
    v = sell * g * fit_mult(want(item)) * level_premium(getattr(item, "required_level", 1))
    if crafted_inputs:
        cost = sum(value(i, "material") * n for i, n in crafted_inputs.items())
        v = max(v, cost * 1.10)
    return max(1, int(round(v)))


def recipe_scroll_value(item):
    lvl = int(getattr(item, "item_level", 1) or 1)
    return max(int(getattr(item, "sell_price", 0) or 0) * 6, int(40 * lvl ** 1.6))


def gear_category(item):
    """(category, subcategory) for a piece of gear, a bag or a recipe scroll."""
    cid = getattr(item, "collection_id", None)
    if cid:
        from world.collection import get_entry, TAB_OF, TABS
        kind = (get_entry(cid) or {}).get("kind")
        return "Collection", dict(TABS).get(TAB_OF.get(kind), "")
    if getattr(item, "recipe_id", None) or getattr(item, "slot", None) == "recipe":
        prof = str(getattr(item, "recipe_profession", "") or "").replace("_", " ").title()
        return "Recipes", prof if prof in RECIPE_SUBS else "Other"
    if getattr(item, "bag_capacity", 0) or getattr(item, "armor_type", None) == "bag":
        return "Containers", ""
    w = getattr(item, "weapon_type", None)
    if w == "shield":
        return "Armor", "Shields"
    if w == "tome":
        return "Armor", "Held in Off-hand"
    if w:
        for sub, types in WEAPON_SUBS:
            if w in types:
                return "Weapons", sub
        return "Weapons", ""
    slot = str(getattr(item, "slot", "") or "").rstrip("0123456789")
    if slot == "back":
        return "Armor", "Cloaks"
    if slot in ("neck", "ring"):
        return "Armor", "Neck and Rings"
    if slot == "trinket":
        return "Armor", "Trinkets"
    if slot == "off_hand":
        return "Armor", "Held in Off-hand"
    a = getattr(item, "armor_type", None)
    if a in ("cloth", "leather", "mail", "plate"):
        return "Armor", a.title()
    return "Miscellaneous", ""


def category_of(good):
    """(category, subcategory) for any good."""
    from world.market import goods as G
    k = good["kind"]
    d = good["data"]
    if k == G.MATERIAL:
        return MATERIAL_SUB.get(d.get("material_type"), ("Trade Goods", "Other"))
    if k == G.CONSUMABLE:
        return "Consumables", CONSUMABLE_SUB.get(d.get("consumable_type"), "Other")
    if k == G.LOOT:
        return "Miscellaneous", ""
    return gear_category(G.unpack(good))


def level_of(good):
    """The level shown in the Lvl column and used by the level filter."""
    from world.market import goods as G
    k, d = good["kind"], good["data"]
    if k == G.MATERIAL:
        return material_level(d.get("material_id"))
    if k == G.CONSUMABLE:
        return int(d.get("required_level") or 1)
    if k == G.LOOT:
        return 0
    if d.get("recipe_id") or d.get("slot") == "recipe":
        return int(d.get("item_level") or 1)     # make_recipe_scroll maps the skill to a level here
    return int(d.get("required_level") or 1)


def rarity_of(good):
    from world.market import goods as G
    if good["kind"] == G.MATERIAL:
        return MATERIAL_RARITY.get(good["data"].get("material_type"), "common")
    return G.rarity(good)


# ================================================================== the NPC catalog
class Entry:
    """One thing NPCs list. `make()` returns a fresh good with one unit (gear) or a unit stack."""
    __slots__ = ("key", "kind", "id", "name", "level", "rarity", "cat", "sub", "value", "demand", "weight",
                 "stacks", "template", "source", "family")

    def __init__(self, **kw):
        for k in self.__slots__:
            setattr(self, k, kw.get(k))

    def make(self, qty=1):
        from world.market import goods as G
        if self.kind == G.MATERIAL:
            from world.gathering_manager import get_gathering_node_manager
            m = get_gathering_node_manager().make_material_instance(self.id)
            return G.pack(m, qty) if m else None
        if self.kind == G.CONSUMABLE:
            from entities.consumable_manager import get_consumable_manager
            c = get_consumable_manager().get_consumable(self.id, 1)
            return G.pack(c, qty) if c else None
        return {"kind": G.GEAR, "data": dict(self.template)}


def _material_demand(mid, m):
    uses = _uses().get(mid, 0)
    pop = {"starter": 1.2, "early": 1.2, "kit": 0.6, "mid": 1.0, "late": 0.9, "endgame": 0.8}.get(m.get("tier"), 1.0)
    return max(0.12, min(1.2, (0.22 + 0.16 * math.log(1 + uses)) * pop))


def _family(mid, m):
    """A word for market news to group things by: 'silk', 'copper', 'herb', ..."""
    t = m.get("material_type", "")
    name = str(m.get("name", "")).lower()
    for w in ("linen", "wool", "silk", "mageweave", "runecloth", "cotton", "copper", "tin", "bronze", "iron",
              "silver", "gold", "mithril", "thorium", "peacebloom", "silverleaf", "kingsblood", "fish", "meat"):
        if w in name or w in mid:
            return w
    return t


@lru_cache(maxsize=1)
def entries():
    """Every NPC-listable thing, keyed by market key."""
    from world.market import goods as G
    out = {}
    vendor = _vendor_stock()
    ok = obtainable()
    mats = materials()
    for mid, m in mats.items():
        if mid not in ok or mid in vendor or m.get("secret"):
            continue
        from world.rep_items import is_rep_key
        if is_rep_key(mid):
            continue
        if m.get("material_type") in ("reagent", "kit", "rod") or int(m.get("sell_price", 0) or 0) <= 0:
            continue
        v = value(mid, "material")
        cat, sub = MATERIAL_SUB.get(m.get("material_type"), ("Trade Goods", "Other"))
        lim = int(m.get("stack_limit", 20) or 20)
        stacks = [s for s in (1, 5, 10, 20) if s <= lim] or [1]
        if m.get("material_type") in ("cut_gem", "gem", "enchant_scroll", "rune", "upgrade_kit"):
            stacks = [1, 1, 2, 3, 5]
        d = _material_demand(mid, m)
        out["m:" + mid] = Entry(key="m:" + mid, kind=G.MATERIAL, id=mid, name=m["name"],
                                level=material_level(mid), rarity=MATERIAL_RARITY.get(m.get("material_type"),
                                                                                       "common"),
                                cat=cat, sub=sub, value=v, demand=d, weight=d, stacks=stacks,
                                source="material", family=_family(mid, m))
    for cid, c in consumables().items():
        if cid not in ok:
            continue
        # a vendor's potion is only on the auction house when somebody can make it, and then it sells under the
        # shop's price (crafters undercut the vendor; that's why anybody buys it here)
        if cid in vendor and cid not in _producers():
            continue
        if int(c.get("sell_price", 0) or 0) <= 0:
            continue
        v = value(cid, "consumable")
        ctype = c.get("consumable_type")
        d = {"health_potion": 0.8, "mana_potion": 0.7, "elixir": 0.45, "meal": 0.35, "food": 0.35,
             "drink": 0.35, "explosive": 0.3, "ammo": 0.4, "gadget": 0.2}.get(ctype, 0.25)
        out["c:" + cid] = Entry(key="c:" + cid, kind=G.CONSUMABLE, id=cid, name=c["name"],
                                level=int(c.get("required_level") or 1), rarity="common",
                                cat="Consumables", sub=CONSUMABLE_SUB.get(ctype, "Other"), value=v, demand=d,
                                weight=d, stacks=[1, 5, 5, 10, 20], source="consumable", family=ctype)
    _add_gear(out)
    return out


def _add_gear(out):
    from world.market import goods as G
    hidden_creatures = set()
    try:
        from world.hidden_zones import creature_kinds
        hidden_creatures = set(creature_kinds())
    except Exception:
        pass
    secret_ids = set()
    for name in ("secret_uniques.json", "faction_rewards.json", "unnamed_rewards.json"):
        for iid, r in (_load(f"data/items/{name}").get("items") or {}).items():
            secret_ids.add(iid)
            if isinstance(r, dict) and r.get("name"):
                secret_ids.add(r["name"])

    def add(item, source, demand, weight, inputs=None):
        if item is None:
            return
        if item.item_id in secret_ids or item.name in secret_ids:
            return
        # a reputation reward, a rep recipe's scroll or what it makes: never on the auction house (world/rep_items.py)
        from world.rep_items import is_rep_item
        if is_rep_item(item):
            return
        d = item.to_dict()
        cat, sub = gear_category(item)
        key = "g:" + str(item.item_id)
        if key in out:
            return
        lvl = item.item_level if getattr(item, "recipe_id", None) else getattr(item, "required_level", 1)
        lvl = min(60, int(lvl or 1))     # a recipe for item level 61 gear is still a level 60 recipe
        out[key] = Entry(key=key, kind=G.GEAR, id=item.item_id, name=item.name,
                         level=int(lvl or 1), rarity=item.rarity, cat=cat, sub=sub,
                         value=gear_value(item, inputs), demand=demand * (0.55 + 0.9 * want(item)),
                         weight=weight, stacks=[1], template=d, source=source, family=cat)

    # crafted gear and bags from open recipes
    from world import crafted_items
    for prof, rid, r in recipes():
        o = r.get("output") or {}
        if o.get("kind") in ("armor", "weapon"):
            try:
                it = crafted_items.build(r)
            except Exception:
                it = None
            if it is not None:
                it.item_id = "crafted_" + rid
            add(it, "crafted", 0.03, 0.25, r.get("inputs"))
        elif o.get("kind") == "fixed":
            from entities.boss_loot import _item_from_def
            it = _item_from_def(o["item"])
            it.is_crafted = True
            it.item_id = "crafted_" + rid
            add(it, "crafted", 0.03, 0.2, r.get("inputs"))
    # named epics: world and dungeon
    from entities.item import Item
    ep = _load("data/loot/epic_drops.json")
    for bucket in ("world", "dungeon"):
        for row in ep.get(bucket, []):
            it = Item.from_dict({**row, "power_scale": 3})
            add(it, "epic_" + bucket, 0.02, 0.06)
    # dungeon and rare loot, from open-world bosses and rares only
    from entities.boss_loot import _item_from_def
    for path in sorted((ROOT / "data/loot").glob("*.json")):
        if path.name in ("epic_drops.json",) or "hidden" in path.name:
            continue
        doc = _load(f"data/loot/{path.name}")
        for boss, rows in doc.items():
            if boss.startswith("_") or boss in hidden_creatures or not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                try:
                    it = _item_from_def(row)
                except Exception:
                    continue
                it.item_id = "boss_" + _slug(boss) + "_" + _slug(row.get("name", "x"))
                add(it, "dungeon", 0.025, 0.08 if it.rarity == "epic" else 0.15)
    # recipe scrolls that drop in the open world
    try:
        from world.recipe_manager import all_recipes_by_source, make_recipe_scroll
        open_ids = {rid for _p, rid, _r in recipes()}
        for rid in all_recipes_by_source("drop"):
            if rid not in open_ids:
                continue
            it = make_recipe_scroll(rid)
            if it is not None:
                add(it, "recipe", 0.03, 0.12)
    except Exception:
        pass
    # bags: hand-priced, sold by vendors too, so few listings
    for row in (_load("data/items/bags.json").get("bags") or []):
        try:
            from entities.loot_generator import LootGenerator
            it = LootGenerator().generate_bag(bag_id=row.get("bag_id") or row.get("id"))
        except Exception:
            it = None
        add(it, "bag", 0.03, 0.1)


@lru_cache(maxsize=1)
def by_level_band():
    """{band: [entry keys]} with bands of five levels, for picking listings at a spread of levels."""
    bands = {}
    for k, e in entries().items():
        bands.setdefault(min(11, max(0, (int(e.level or 1) - 1) // 5)), []).append(k)
    return bands
