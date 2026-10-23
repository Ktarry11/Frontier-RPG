"""Vendor trash + coin drops (Kyle, 2026-10-23).

WoW logic: only HUMANOID-type creatures (anything sentient and carrying a purse: gnolls, murlocs, satyrs, Forsaken
soldiers...) drop copper/silver. Everything else drops vendor trash by STYLE (beasts: pelts / claws / fangs, insects:
chitin / stingers, elementals: cores / shards in the creature's element, ...). Higher-level mob = higher-priced trash.
Dungeon (cave) mobs drop trash more often and pay more coin. Humanoids also carry the occasional piece of junk.

Data: data/items/vendor_trash.json.  Hooked into CombatEngine._resolve_victory (once PER ENEMY, so a 4-mob pull rolls four
times).  Vendor trash is LootItem(category="trash"): grey, sellable, stacks to 20; the vendor screen has "Sell Junk" and a
global auto-sell tick-box.  Cloth for tailoring is reserved for humanoid-shaped creatures (NOT murlocs) once professions exist.
"""
import json
import os
import random
import re

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "items", "vendor_trash.json")
_CREATURES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "creatures", "creatures.json")
_ICON_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons", "vendor_trash")

_cfg = None
_templates = None


def _config():
    global _cfg
    if _cfg is None:
        with open(_DATA_PATH, "r") as f:
            _cfg = json.load(f)
    return _cfg


def _template_of(name):
    global _templates
    if _templates is None:
        try:
            with open(_CREATURES_PATH, "r") as f:
                _templates = {n: v.get("template", "") for n, v in json.load(f)["creatures"].items()}
        except (OSError, ValueError, KeyError):
            _templates = {}
    return _templates.get(name, "")


# ------------------------------------------------------------------------------------------ classification
# First match wins. Each rule: (regex on creature name, family or None, coin?)   family None = coin only (humanoid junk).
# Sentient creatures (they carry a purse) -> coin.
_SENTIENT = re.compile(
    r"murloc|satyr|drowned (buccaneer|crewman|deckhand|ferryman|fisherman|pilgrim|sailor|troll)|waterlogged gunner|"
    r"forsaken|footman|officer|guardsman|captain|baron|noble|farmhand|stableboy|servant|servitor|deserter|watchman|"
    r"pirate|gaffer|goodman|thurman|thrall|drudger|worgen|bonewarden|berard|ashbury|reaper-lord|ghoulmaster|hexed|"
    r"\b(gnoll|quilboar|centaur|ogre|kobold|troll|orc|goblin|razormane|bristleback|kolkar|harpy handler)s?\b", re.I)
# Not sentient even if the template is humanoid_* (rare); keeps beasts/constructs out of the purse.
_NOT_SENTIENT = re.compile(r"golem|elemental|wisp|spirit|skeleton|ghoul(?!master)|zombie|corpse|construct|\bimps?\b|\bghost\b|"
                           r"wraith|hydra|faerie dragon|harpy|battleboar|abomination|amber sentinel|brood tender|chitterlord|"
                           r"resin spitter|shadow corruption|flame guardian|dryad", re.I)

_FAMILY_RULES = [
    (re.compile(r"brood tender|resin spitter|chitterlord|amber sentinel|hive weaver|carapace|silithid|brood|skitter|scorpid|spider|web|wasp|larva|drone|stinger|crawler|hatchling|"
                r"weaver|husk crawler|egg tender|amberwing|nightcrawler|skulker|tunnel-guard|nest guardian", re.I), "insect"),
    (re.compile(r"treant|timberling|sapling|tangle-vine|rotlasher|gloomcap|spore|bramble|mosshide|orchardkeeper|grave moss|"
                r"peat shambler|deviate shambler|thornroot|scarecrow|oasis|sprite|creeper|ancient protector|corrupted ancient|"
                r"ancient treant|elder timberling|verdan|dryad", re.I), "plant"),
    (re.compile(r"adder|python|viper|serpent|eel|toad|slug|leech|rat\b|rats\b|hissfang|lasher|ravager|raptor|croc", re.I), "beast"),
    (re.compile(r"crab|snapper|turtle|crocolisk|lurker|murky|gulpjaw|kragg|shellcrusher", re.I), "aquatic"),
    (re.compile(r"wraith|banshee|shade|ghost|ectoplasm|mourning|restless|wight|revenant|bonewalker|bone-dust|echo of|spirit|abomination|zombie|"
                r"ghoul|skeleton|corpse", re.I), "undead"),
    (re.compile(r"imp\b|imps\b|felhound|felstalker|voidwalker|fel pup|felguard|doomguard|pit lord|familiar|rot hound|"
                r"shadowfang guardian|xelnaz|baneshadow|malgan|gazz", re.I), "demon"),
    (re.compile(r"construct|shadow corruption|flame guardian|elemental|golem|wisp|devil|stormbinder|naiad|ooze|sludge|sentinel|spellblade|ore sprite|iceshard|"
                r"warden|lava|magma|molten|ember|cinder|smolder|stone|rock|rime|tidal|basilisk|magmus|crusher", re.I), "elemental"),
]

_TEMPLATE_FAMILY = {
    "beast_basic": "beast", "beast_fast": "beast", "beast_large": "beast",
    "vermin_sneaky": "insect", "vermin_swarm": "insect",
    "aquatic_basic": "aquatic", "undead_basic": "undead",
    "elemental_bruiser": "elemental", "elemental_caster": "elemental",
    "demon_caster": "demon", "demon_hound": "demon",
}

_ELEMENT_RULES = [
    ("fire", re.compile(r"ember|magma|molten|lava|cinder|smolder|fire|flame|charred|magmus|salamander", re.I)),
    ("ice", re.compile(r"rime|ice|frost|iceshard|wintermaw", re.I)),
    ("water", re.compile(r"water|tidal|tide|naiad|lake|marsh|sludge|ooze|bog|peat|oasis", re.I)),
    ("air", re.compile(r"dust devil|storm|thunder|wind|gale", re.I)),
    ("shadow", re.compile(r"shade|nightmare|void|weeping|mourning|ectoplasm|shadow|wraith|banshee", re.I)),
    ("arcane", re.compile(r"spell|wisp|sprite|arcane|ambermill|naga", re.I)),
    ("nature", re.compile(r"sapling|timber|treant|thorn|vine|moss|spore|gloomcap|verdant", re.I)),
]


def classify(name, template=None):
    """-> (family, coin). family in beast/insect/aquatic/undead/elemental/demon/plant/humanoid; coin True for coin droppers."""
    template = template or _template_of(name)
    mindless = bool(_NOT_SENTIENT.search(name))
    if template.startswith("humanoid") and not mindless:
        return "humanoid", True
    if not mindless and _SENTIENT.search(name):
        return "humanoid", True
    for rx, fam in _FAMILY_RULES:
        if rx.search(name):
            # an explicit template beats a loose keyword for plain beasts/insects/undead/demons
            if fam == "elemental" and template in ("beast_basic", "beast_fast", "beast_large", "vermin_sneaky", "vermin_swarm"):
                continue
            if fam == "beast" and template.startswith(("undead", "elemental", "demon")):
                continue
            return fam, False
    return _TEMPLATE_FAMILY.get(template, "beast"), False


def element_of(name):
    for el, rx in _ELEMENT_RULES:
        if rx.search(name):
            return el
    return "earth"


# ------------------------------------------------------------------------------------------ items
def _tier(level):
    for i, t in enumerate(_config()["tiers"]):
        if level <= t["max_level"]:
            return i, t
    t = _config()["tiers"][-1]
    return len(_config()["tiers"]) - 1, t


def make_item(family, entry, level, element=None):
    """-> dict(item_id, name, price, icon_id, description) for one trash item at a creature level."""
    cfg = _config()
    ti, tier = _tier(level)
    price = max(1, int(round(tier["price_level"] * cfg["price_per_level"] * entry["price"])))
    name = entry["name"]
    item_id = f"vt_{family}_{entry['id']}_{ti}"
    icon = entry.get("icon")
    if entry.get("element") and element:
        name = f"{cfg['elements'][element]} {name}"
        item_id = f"vt_{family}_{entry['id']}_{element}_{ti}"
        icon = f"{icon}_{element}"
    name = f"{tier['adjective']} {name}"
    icon_id = icon if icon and os.path.exists(os.path.join(_ICON_DIR, f"{icon}.png")) else None
    return {"item_id": item_id, "name": name, "price": price, "icon_id": icon_id,
            "description": "Vendor trash. Worth a few coppers to any merchant."}


def _pick(family, level, name):
    entries = _config()["families"][family]
    element = None
    if family == "elemental":
        element = element_of(name)
        entries = [e for e in entries if element in e.get("elements", [element])] or entries
    entry = random.choices(entries, weights=[e.get("weight", 1) for e in entries], k=1)[0]
    return make_item(family, entry, level, element)


def roll_drops(enemy, rng=random):
    """What one defeated enemy drops besides gear/quest items.

    -> {"copper": int, "items": [item dict, ...]}.  `enemy` needs .name .level and optionally .is_boss / .location_type.
    """
    cfg = _config()
    name = enemy.name
    level = max(1, int(getattr(enemy, "level", 1)))
    boss = bool(getattr(enemy, "is_boss", False))
    place = "cave" if getattr(enemy, "location_type", "open_zone") == "cave" else "open_zone"
    rates = cfg["rates"][place]
    family, coin = classify(name)
    out = {"copper": 0, "items": []}

    if coin:
        base = level * cfg["coin"]["per_level"]
        copper = base + int(base * rng.random() * cfg["coin"]["bonus_max"])
        copper = int(copper * rates["coin_mult"] * (cfg["boss"]["coin_mult"] if boss else 1.0))
        out["copper"] = max(1, copper)
        n = rng.randint(*cfg["boss"]["junk_items"]) if boss else (1 if rng.random() < rates["junk_chance"] else 0)
        for _ in range(n):
            out["items"].append(_pick("junk", level, name))
    else:
        n = rng.randint(*cfg["boss"]["trash_items"]) if boss else (1 if rng.random() < rates["trash_chance"] else 0)
        for _ in range(n):
            out["items"].append(_pick(family, level, name))
    return out
