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
        with open(_DATA_PATH, "r", encoding="utf-8") as f:
            _cfg = json.load(f)
    return _cfg


def _template_of(name):
    global _templates
    if _templates is None:
        try:
            with open(_CREATURES_PATH, "r", encoding="utf-8") as f:
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
    r"\b(gnoll|quilboar|centaur|ogre|kobold|troll|orc|goblin|razormane|bristleback|kolkar|harpy)s?\b", re.I)
#: HARPIES ARE PEOPLE. They used to sit in _NOT_SENTIENT, which skipped the humanoid path entirely and
#: dropped every harpy in the game into `beast` - so they yielded LEATHER and no coin. Kyle, 2026-10-27:
#: "harpies should drop cloth bro." They speak, they use tools, they take prisoners, and in Warcraft they
#: have always been Humanoid. Moving them here makes them a cloth and coin source like every other
#: speaking enemy, across all nine of them, not just the ones added with this zone.
# Not sentient even if the template is humanoid_* (rare); keeps beasts/constructs out of the purse.
_NOT_SENTIENT = re.compile(r"golem|elemental|wisp|spirit|skeleton|ghoul(?!master)|zombie|corpse|construct|\bimps?\b|\bghost\b|"
                           r"wraith|hydra|faerie dragon|battleboar|abomination|amber sentinel|brood tender|chitterlord|"
                           r"resin spitter|shadow corruption|flame guardian|dryad", re.I)

#: Animal head nouns. A name whose LAST word is one of these is an animal with a descriptive
#: modifier, not a plant - "Sporelit Bat" is a bat that grows fungus, not a fungus shaped like a bat.
#:
#: WHY THIS IS NEEDED. Family is inferred from the name, and a plant keyword anywhere in the name
#: wins outright. So Sporelit Bat classified as `plant`, and plants cannot be skinned: a level-31
#: beast in Rotvine Hollow yielded no leather at all, with nothing to see but an empty corpse.
#:
#: WHY IT IS NOT JUST "AN EXPLICIT TEMPLATE BEATS A LOOSE KEYWORD", which is what this function
#: already does for `elemental`: the templates are STAT templates, not family declarations. Ancient
#: Treant, Verdan the Everliving and Fenrot Creeper are all `beast_large` because that is the stat
#: block a big slow thing wants, and letting the template win would have made twelve treants,
#: saplings and spore clouds skinnable. The head noun is the part of the name that says what the
#: creature IS; everything before it is decoration. Of the fourteen collisions game-wide this flips
#: exactly the two animals - Sporelit Bat and Sporeback Grazer - and leaves the twelve plants alone.
_ANIMAL_HEAD = re.compile(
    r"(bat|grazer|boar|ape|gorilla|panther|raptor|cat|wolf|bear|stag|hound|"
    r"serpent|adder|python|toad|crab|beetle|spider|scorpion|moth|wasp|hornet|"
    r"rat|hare|ox|kodo|ram|goat|bird|hawk|owl|vulture|eel|shark|turtle)s?$", re.I)

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
            # A plant keyword loses to an animal head noun on a beast/vermin stat template - see
            # _ANIMAL_HEAD. Both conditions are required: the head noun says it is an animal, and
            # the template says somebody built it as one.
            if (fam == "plant" and _ANIMAL_HEAD.search(name)
                    and template in ("beast_basic", "beast_fast", "beast_large",
                                     "vermin_sneaky", "vermin_swarm")):
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


def _band_suffix(level):
    """Icon band for a creature level: "", "_t2" or "_t3".

    THE BAND BOUNDARIES LIVE IN THE DATA, not here and not in the reskin tool, because both have
    to agree about which levels get which art, and two copies of one rule is the bug this project
    keeps re-finding. tools/reskin_vendor_trash_icons.py reads the same list.
    """
    for b in _config().get("icon_bands", []):
        if level <= b["max_level"]:
            return b["suffix"]
    return ""


def _icon_file(icon, level):
    """The banded icon if that art exists, else the base art, else None. Never a broken path."""
    if not icon:
        return None
    for cand in (f"{icon}{_band_suffix(level)}", icon):
        if os.path.exists(os.path.join(_ICON_DIR, f"{cand}.png")):
            return cand
    return None


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
    # A premium entry is already a named thing - "Gilded Death Mask", "Deepwater Pearl" - and
    # stacking the tier word on top gives "Immaculate Gilded Death Mask", which is the adjective
    # ladder eating the item's own identity. Those entries carry their name and take no prefix.
    if not entry.get("no_adjective") and not name.startswith(tier["adjective"]):
        name = f"{tier['adjective']} {name}"       # "Crude Idol" at the Crude tier stays as it is
    icon_id = _icon_file(icon, level)
    # "Worth a few coppers" was written when the top tier paid 33 * 14 = 462c and was already a
    # lie then; a Peerless Core at level 55 sells for over eight silver. The line now scales with
    # what the thing is actually worth, because the description is the only place the player is
    # told whether a grey item is worth the bag slot.
    worth = ("Worth a few coppers to any merchant." if price < 100 else
             "A merchant will give you decent silver for this." if price < 400 else
             "Merchants pay well for salvage this clean.")
    return {"item_id": item_id, "name": name, "price": price, "icon_id": icon_id,
            "description": f"Vendor trash. {worth}"}


def icon_for_item_id(item_id):
    """Icon id for a trash item id of the form vt_<family>_<entry>[_<element>]_<tier> (None if unknown / no art)."""
    parts = str(item_id).split("_")
    if len(parts) < 4 or parts[0] != "vt":
        return None
    cfg = _config()
    entries = cfg["families"].get(parts[1], [])
    for entry in entries:
        if entry["id"] != parts[2]:
            continue
        icon = entry.get("icon")
        if entry.get("element") and len(parts) >= 5:
            icon = f"{icon}_{parts[3]}"
        # the tier index is the last part, and it picks the art band: an item sitting in a bag
        # must show the icon it showed when it dropped.
        try:
            tier = cfg["tiers"][int(parts[-1])]
        except (ValueError, IndexError, KeyError):
            return _icon_file(icon, 1)
        return _icon_file(icon, tier["max_level"])
    return None


def _pick(family, level, name):
    entries = _config()["families"][family]
    # LEVEL GATES. Kyle: "We dont need trash chance we need new vendor trash." Without these every
    # entry drops at every level, so the only thing separating a level 3 kill from a level 55 one
    # was an adjective - a level 55 demon dropping "Peerless Tattered Rags". min_level introduces
    # items that only exist deep in the game; max_level retires the scraps that should stop.
    gated = [e for e in entries
             if e.get("min_level", 0) <= level <= e.get("max_level", 10 ** 9)]
    entries = gated or entries      # never leave a family with nothing at all to drop
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

    def _coin(scale):
        base = level * cfg["coin"]["per_level"]
        c = base + int(base * rng.random() * cfg["coin"]["bonus_max"])
        return max(1, int(c * rates["coin_mult"] * scale
                          * (cfg["boss"]["coin_mult"] if boss else 1.0)))

    if coin:
        out["copper"] = _coin(1.0)
        n = rng.randint(*cfg["boss"]["junk_items"]) if boss else (1 if rng.random() < rates["junk_chance"] else 0)
        for _ in range(n):
            out["items"].append(_pick("junk", level, name))
    else:
        # A DUNGEON PAYS FOR BEING A DUNGEON, and it pays in trash rather than coin because a
        # beast carries no purse anywhere in this game. 14 of 47 dungeons used to pay under 1.5x
        # an open zone of their own level and three paid LESS than the open world outside them,
        # because the cave bonus multiplies a base that swings on bestiary and a beast dungeon
        # has no coin to multiply. trash_count is the lever: more pieces per kill, not a richer
        # purse. See _cave_notes in the data.
        if boss:
            n = rng.randint(*cfg["boss"]["trash_items"])
        elif rng.random() < rates["trash_chance"]:
            n = rng.randint(*rates.get("trash_count", [1, 1]))
        else:
            n = 0
        for _ in range(n):
            out["items"].append(_pick(family, level, name))
    return out
