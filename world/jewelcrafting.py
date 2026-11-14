"""Jewelcrafting: cut gems, sockets on gear, and putting gems in and taking them out.

Kyle, 14 Nov 2026: "How about we start to build jewel crafting. Since we have gemstones dropping
from ore. Which means we need colours, sockets inside armor (let's have only gear over 30 with
sockets). Jewel crafting also lets you craft rings, necklaces, trinkets." His four calls the same
morning:

  COLOURS   WoW TBC style. Sockets are red, yellow or blue. Orange gems fit red or yellow, green
            fit yellow or blue, purple fit red or blue, prismatic fit anything. Fill every socket
            with a gem that fits and the item's socket bonus turns on.
  SOCKETS   by rarity, paid from stats. Only gear required level 30 and up. A green sometimes
            has one, a blue one or two, an epic two or three. Each socket takes about one gem's
            worth of stats off the item, so an empty socket is a small loss and a well-gemmed
            item a small gain (the gems plus the bonus).
  PROSPECT  jewelcrafters can crush five ore for gems from that ore's list.
  REMOVING  a jeweller (the forge trainers who teach jewelcrafting) takes a gem out for a fee
            and gives it back. Putting a gem over another one without that destroys the old one.

ONE FORMULA (Kyle: "It can be home-brew but it MUST MUST be consistent"). A gem is worth
gem_budget(level) stat-budget points, the same points LootGenerator spends on every item
(item_level x 0.36 x rarity x slot weight), divided by each stat's real cost from
data/items/gear_suffixes.json. A socket on an item costs the item the budget of one gem of its own
level, so gems of the item's level put back exactly what the socket took, and the bonus is the
reward for matching.

Data: data/jewelcrafting/gems.json, written by tools/build_jewelcrafting.py.
"""
import json
import random
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GEMS = ROOT / "data" / "jewelcrafting" / "gems.json"

COLOURS = ("red", "yellow", "blue")
#: which socket colours each gem colour counts as
FITS = {
    "red": {"red"}, "yellow": {"yellow"}, "blue": {"blue"},
    "orange": {"red", "yellow"}, "green": {"yellow", "blue"}, "purple": {"red", "blue"},
    "prismatic": {"red", "yellow", "blue"},
}
SOCKET_LEVEL = 30                 # gear below this required level never has a socket
GEM_SHARE = 0.35                  # one gem is worth this share of an uncommon item's per-level budget
RARE_GEM = 1.35                   # a rare-quality stone is worth this much more than an uncommon one
BONUS_SHARE = 0.5                 # the socket bonus is worth half a gem
#: sockets by rarity: (guaranteed, chance of one more)
SOCKET_ROLLS = {"uncommon": (0, 0.25), "rare": (1, 0.35), "epic": (2, 0.40), "legendary": (3, 0.0)}
#: the most sockets a slot can carry
SLOT_MAX = {"chest": 3, "legs": 3, "head": 3, "two_hand": 3, "main_hand": 2, "shoulder": 2,
            "hands": 2, "feet": 2, "waist": 2, "wrist": 1, "back": 1, "neck": 1, "ring": 1,
            "ring1": 1, "ring2": 1, "off_hand": 1}
NO_SOCKETS = {"trinket", "trinket1", "trinket2", "ranged", "bag1", "bag2", "bag3", "bag4", "recipe"}
#: the colours a socket tends to be, by what the item is for
TEMPLATE_COLOURS = {
    "str_physical": {"red": 5, "yellow": 3, "blue": 2},
    "agi_physical": {"red": 5, "yellow": 3, "blue": 2},
    "int_caster": {"red": 4, "yellow": 4, "blue": 2},
    "spi_healer": {"red": 3, "yellow": 3, "blue": 4},
    "str_int_hybrid": {"red": 4, "yellow": 3, "blue": 3},
    "agi_int_hybrid": {"red": 4, "yellow": 3, "blue": 3},
}
TEMPLATE_BONUS = {"str_physical": "strength", "agi_physical": "agility", "int_caster": "intellect",
                  "spi_healer": "spirit", "str_int_hybrid": "stamina", "agi_int_hybrid": "stamina"}
#: what a jeweller charges to take one gem out, in copper per level of the gem
REMOVAL_FEE_PER_LEVEL = 25


@lru_cache(maxsize=1)
def data():
    try:
        return json.loads(GEMS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"cut_gems": {}, "raw_gems": {}}


@lru_cache(maxsize=1)
def stat_costs():
    d = json.loads((ROOT / "data/items/gear_suffixes.json").read_text(encoding="utf-8"))
    return d["stat_budget_costs"]


def gem_budget(level, quality="uncommon"):
    """Stat-budget points one gem of this level is worth."""
    level = max(1, min(60, int(level)))
    return level * 0.36 * 1.3 * GEM_SHARE * (RARE_GEM if quality == "rare" else 1.0)


def stats_for(weights, budget):
    """Spend a budget across stats by weight, through each stat's real cost. Whole numbers, and a
    gem never shows a zero: a stat it names is worth at least one point."""
    costs = stat_costs()
    return {s: max(1, int(budget * w / costs.get(s, 1.0) + 0.5)) for s, w in weights.items()}


#: how a stat reads on a gem
STAT_NAMES = {"crit_chance_physical": "Crit", "crit_chance_spell": "Spell Crit", "hit_rating": "Hit",
              "mp5": "Mana per 5", "spell_power": "Spell Power", "healing_power": "Healing",
              "attack_power": "Attack Power", "defense_rating": "Defense", "dodge_rating": "Dodge",
              "spell_penetration": "Spell Penetration", "haste": "Haste"}


def stat_name(stat):
    return STAT_NAMES.get(stat, stat.replace("_", " ").title())


def stat_text(stats):
    return ", ".join(f"+{v} {stat_name(k)}" for k, v in stats.items())


def cut(cut_id):
    return data()["cut_gems"].get(cut_id)


def is_cut_gem(material_id):
    return material_id in data()["cut_gems"]


def fits(gem_colour, socket_colour):
    return socket_colour in FITS.get(gem_colour, set())


# ---------------------------------------------------------------- sockets on an item
def sockets(item):
    """The item's sockets as [{"color", "gem"}]. Older saves carried a bare list or nothing."""
    out = []
    for s in getattr(item, "sockets", None) or []:
        if isinstance(s, dict):
            out.append(s)
        elif isinstance(s, str):
            out.append({"color": s, "gem": None})
    item.sockets = out
    return out


def bonus_active(item):
    ss = sockets(item)
    if not ss or not getattr(item, "socket_bonus", None):
        return False
    for s in ss:
        g = cut(s.get("gem")) if s.get("gem") else None
        if g is None or not fits(g["color"], s["color"]):
            return False
    return True


def socket_stats(item):
    """Stats the item gains from its gems and, when every socket matches, its bonus."""
    out = {}
    for s in sockets(item):
        g = cut(s.get("gem")) if s.get("gem") else None
        if g:
            for k, v in g["stats"].items():
                out[k] = out.get(k, 0) + v
    if bonus_active(item):
        for k, v in item.socket_bonus.items():
            out[k] = out.get(k, 0) + v
    return out


_SUPPRESSED = [0]


class no_sockets:
    """with no_sockets(): ... generates gear without sockets - for a reference item whose stats
    get copied somewhere else (world/upgrade_manager.py), where a socket's cost would come
    across without the socket."""
    def __enter__(self):
        _SUPPRESSED[0] += 1

    def __exit__(self, *exc):
        _SUPPRESSED[0] -= 1


def roll_sockets(item, total_budget, rng=random):
    """Give a freshly generated item its sockets, paid for out of its own stats. Called by
    LootGenerator for every armour piece and weapon; does nothing below level 30, on white or
    grey gear, or on slots that never have sockets."""
    if _SUPPRESSED[0] or getattr(item, "required_level", 1) < SOCKET_LEVEL or item.slot in NO_SOCKETS:
        return item
    roll = SOCKET_ROLLS.get(item.rarity)
    if not roll or total_budget <= 0:
        return item
    n = roll[0] + (1 if rng.random() < roll[1] else 0)
    wt = getattr(item, "weapon_type", None) or ""
    two_hand = "_2h" in wt or wt in ("staff", "polearm")
    n = min(n, SLOT_MAX.get("two_hand" if two_hand else item.slot, 2))
    if n <= 0:
        return item
    weights = TEMPLATE_COLOURS.get(item.stat_template, {"red": 1, "yellow": 1, "blue": 1})
    colours = rng.choices(list(weights), weights=list(weights.values()), k=n)
    item.sockets = [{"color": c, "gem": None} for c in sorted(colours, key=COLOURS.index)]
    if META_ENABLED and item.slot in META_SLOTS and item.rarity in ("epic", "legendary"):
        item.sockets.insert(0, {"color": "meta", "gem": None})
    gb = gem_budget(item.item_level)
    # PAID FROM STATS: every stat comes down by the share of the budget the sockets took
    keep = max(0.3, 1.0 - n * gb / total_budget)
    from entities.item import whole
    for group in (item.primary_stats, item.secondary_stats):
        for k, v in list(group.items()):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                group[k] = max(1, whole(v * keep))
    stat = TEMPLATE_BONUS.get(item.stat_template, "stamina")
    item.socket_bonus = stats_for({stat: 1.0}, gb * BONUS_SHARE)
    return item


# ---------------------------------------------------------------- hand-made gear
#: Kyle, 14 Nov 2026: "go back through items post lvl 30 and add more gem slots while reducing
#: stats accordingly. Like a small stat reduction on some blues and add 1 to 2 gem slots. Like 25%
#: of the gear." Boss drops, quest rewards, named epics and set pieces are written by hand, so
#: they never went through roll_sockets. A quarter of the blues and epics from level 30 now carry
#: one or two sockets, paid for the same way: a gem's worth of stats per socket.
AUTHORED_SHARE = 25          # percent of eligible hand-made items that get sockets
AUTHORED_RARITIES = ("rare", "epic")
AUTHORED_COST = 0.6          # each socket takes this share of one gem's worth off the item
AUTHORED_KEEP_FLOOR = 0.8    # and the item always keeps at least this much of its stats


def _template_of(item):
    """The stat family of a hand-made item that names none: whatever its stats lean toward."""
    if item.stat_template in TEMPLATE_COLOURS:
        return item.stat_template
    st = dict(item.primary_stats or {})
    st.update(item.secondary_stats or {})
    score = {
        "str_physical": st.get("strength", 0) + st.get("attack_power", 0) / 2,
        "agi_physical": st.get("agility", 0),
        "int_caster": st.get("intellect", 0) + st.get("spell_power", 0),
        "spi_healer": st.get("spirit", 0) + st.get("healing_power", 0) + st.get("mp5", 0),
    }
    best = max(score, key=score.get)
    return best if score[best] > 0 else "str_physical"


def _authored_budget(item):
    """The stat budget the generator would give an item of this level, rarity and slot."""
    d = json.loads((ROOT / "data/items/rarity.json").read_text(encoding="utf-8"))["rarity_tiers"]
    slots = json.loads((ROOT / "data/items/slots.json").read_text(encoding="utf-8"))
    rm = d.get(item.rarity, d["rare"])["stat_budget_multiplier"]
    tier = (slots["slots"].get(item.slot) or {}).get("weight_tier", "medium")
    return item.item_level * 0.36 * rm * slots["weight_tiers"].get(tier, 1.0)


def socket_authored(item, seed=None):
    """Give a hand-made item its sockets if it's one of the quarter that gets them. The choice and
    the colours are seeded on the item (a set piece on its set and slot, so every spec's version
    of a piece matches), so the same item always comes out the same. Returns the item."""
    import zlib
    if item is None or getattr(item, "sockets", None):
        return item
    if getattr(item, "required_level", 1) < SOCKET_LEVEL or item.rarity not in AUTHORED_RARITIES \
            or item.slot in NO_SOCKETS:
        return item
    key = seed or (f"set:{item.set_id}:{item.slot}" if getattr(item, "set_id", None) else f"item:{item.name}")
    h = zlib.crc32(key.encode("utf-8"))
    if h % 100 >= AUTHORED_SHARE:
        return item
    rng = random.Random(h)
    n = 2 if (item.rarity == "epic" and rng.random() < 0.6) or rng.random() < 0.3 else 1
    wt = getattr(item, "weapon_type", None) or ""
    two_hand = "_2h" in wt or wt in ("staff", "polearm")
    n = min(n, SLOT_MAX.get("two_hand" if two_hand else item.slot, 2))
    template = _template_of(item)
    weights = TEMPLATE_COLOURS[template]
    colours = rng.choices(list(weights), weights=list(weights.values()), k=n)
    item.sockets = [{"color": c, "gem": None} for c in sorted(colours, key=COLOURS.index)]
    return charge_sockets(item)


def charge_sockets(item):
    """Take the sockets' cost off a hand-made item's stats and set its bonus. Called when the
    sockets are added, and again when a set piece is exchanged for another spec's version (the
    exchange writes that version's full stats back, and the gems in the sockets stay put)."""
    n = len(sockets(item))
    if not n:
        return item
    # A SMALL reduction (Kyle: "a small stat reduction on some blues"): the sockets take back
    # most of a gem's worth each, measured against what the item's own stats are actually worth,
    # and never more than a fifth of them.
    gb = gem_budget(item.item_level)
    costs = stat_costs()
    worth = sum(v * costs.get(k, 1.0) for g in (item.primary_stats, item.secondary_stats)
                for k, v in (g or {}).items() if isinstance(v, (int, float)) and not isinstance(v, bool))
    keep = max(AUTHORED_KEEP_FLOOR, 1.0 - n * gb * AUTHORED_COST / max(worth, 1.0))
    from entities.item import whole
    for group in (item.primary_stats, item.secondary_stats):
        for k, v in list(group.items()):
            if isinstance(v, (int, float)) and not isinstance(v, bool) and v > 0:
                group[k] = max(1, whole(v * keep))
    item.socket_bonus = stats_for({TEMPLATE_BONUS[_template_of(item)]: 1.0}, gb * BONUS_SHARE)
    return item


# ---------------------------------------------------------------- putting gems in, taking them out
def place(character, item, index, cut_id):
    """Put a cut gem from the character's bags into a socket. Anything already in that socket is
    destroyed (Kyle's rule: take it to a jeweller first if you want it back).
    -> (ok, message)"""
    ss = sockets(item)
    if not 0 <= index < len(ss):
        return False, "That item has no such socket."
    g = cut(cut_id)
    if g is None:
        return False, "That isn't a cut gem."
    if character.get_material_quantity(cut_id) < 1:
        return False, f"You don't have a {g['name']}."
    old = ss[index].get("gem")
    character.consume_material(cut_id, 1)
    ss[index]["gem"] = cut_id
    _refresh(character)
    msg = f"Set {g['name']} in {item.name}."
    if old:
        msg += f" The {cut(old)['name'] if cut(old) else 'old gem'} was destroyed."
    return True, msg


def removal_fee(item):
    total = 0
    for s in sockets(item):
        g = cut(s.get("gem")) if s.get("gem") else None
        if g:
            total += max(1, g.get("level", 1)) * REMOVAL_FEE_PER_LEVEL
    return total


def remove(character, item, index, party=None):
    """A jeweller takes the gem out of one socket and hands it back, for a fee from the party
    purse. -> (ok, message)"""
    ss = sockets(item)
    if not 0 <= index < len(ss) or not ss[index].get("gem"):
        return False, "There's no gem in that socket."
    cid = ss[index]["gem"]
    g = cut(cid) or {"name": cid, "level": 1}
    fee = max(1, g.get("level", 1)) * REMOVAL_FEE_PER_LEVEL
    purse = party if party is not None and hasattr(party, "copper") else character
    if getattr(purse, "copper", 0) < fee:
        from ui.coin_format import format_coins
        return False, f"That costs {format_coins(fee)}, and you don't have it."
    from world.gathering_manager import get_gathering_node_manager
    m = get_gathering_node_manager().make_material_instance(cid)
    if m is None:
        return False, "Something went wrong with that gem."
    m.quantity = 1
    if not character.add_material(m):
        return False, "Your bags are full."
    purse.copper -= fee
    ss[index]["gem"] = None
    _refresh(character)
    from ui.coin_format import format_coins
    return True, f"Took the {g['name']} out of {item.name} for {format_coins(fee)}."


def _refresh(character):
    """Gems change stats; recompute anything the wearer derives from gear."""
    fn = getattr(character, "_recalculate_derived_stats", None)
    if fn:
        fn()


def describe_socket(s):
    """('Red Socket' | gem name, stat text, fits) for a tooltip line."""
    colour = s["color"].capitalize()
    g = cut(s.get("gem")) if s.get("gem") else None
    if not g:
        return f"{colour} Socket", "", False
    return g["name"], stat_text(g["stats"]), fits(g["color"], s["color"])


#: tooltip colours by kind, shared by every screen that draws an item card
SOCKET_COLOURS = {"red": (230, 90, 90), "yellow": (235, 210, 90), "blue": (110, 150, 240)}
TOOLTIP_PALETTE = {"empty": (150, 150, 150), "gem": (255, 255, 255), "bonus_on": (30, 255, 0),
                   "bonus_off": (128, 128, 128)}
#: a gem's line on an item card is drawn in the gem's own colour (Kyle, 14 Nov 2026: "Colour the
#: names ... based on colour of gems. So a +9 str would be red")
GEM_TEXT_COLOURS = {"red": (235, 85, 85), "yellow": (240, 215, 90), "blue": (105, 150, 245),
                    "orange": (245, 150, 60), "green": (90, 205, 110), "purple": (190, 110, 235),
                    "prismatic": (235, 235, 245), "meta": (200, 200, 210)}


def line_colour(kind, socket=None):
    """The colour an item card draws one socket line in."""
    if kind.startswith("gem:"):
        return GEM_TEXT_COLOURS.get(kind[4:], TOOLTIP_PALETTE["gem"])
    if kind == "empty" and socket:
        return SOCKET_COLOURS.get(socket.get("color"), TOOLTIP_PALETTE["empty"])
    return TOOLTIP_PALETTE.get(kind, TOOLTIP_PALETTE["gem"])


def tooltip_lines(item):
    """[(text, kind)] for an item card: each socket, then the bonus (lit when earned). kind is
    "gem:<colour>", "empty", "bonus_on" or "bonus_off"; line_colour() turns it into a colour."""
    ss = sockets(item)
    if not ss:
        return []
    out = []
    for s in ss:
        name, stats, _fits = describe_socket(s)
        if stats:
            g = cut(s.get("gem")) or {}
            out.append((f"{name}: {stats}", f"gem:{g.get('color', '')}"))
        else:
            out.append((name, "empty"))
    bonus = getattr(item, "socket_bonus", None) or {}
    if bonus:
        out.append((f"Socket Bonus: {stat_text(bonus)}", "bonus_on" if bonus_active(item) else "bonus_off"))
    return out


# ================================================================ META GEMS (written, switched off)
# Kyle, 14 Nov 2026: "Let's do meta gem code but not integrate it yet." The TBC idea, adapted: an
# epic helm can carry one META socket, which takes only a meta gem. A meta gem is strong, a stat
# plus an effect, and it only works while the wearer's OTHER gems meet its condition ("at least
# two blue gems", "more red gems than blue"), counting every gem the wearer has on: a purple gem
# counts as red and as blue, a prismatic one as all three.
#
# Nothing below runs in the game yet. META_ENABLED is False, so roll_sockets never makes a meta
# socket and no recipe cuts a meta gem; the definitions sit in data/jewelcrafting/gems.json under
# "meta_gems". To turn it on: set META_ENABLED, add the meta cuts to the builder's recipes, and
# call meta_stats(character) from Equipment.get_total_stat_bonuses' owner.
META_ENABLED = False
META_SLOTS = {"head"}
FITS["meta"] = {"meta"}


def meta_gem(cut_id):
    return (data().get("meta_gems") or {}).get(cut_id)


def colour_counts(character):
    """{red, yellow, blue: how many of the wearer's socketed gems count as that colour}."""
    counts = {c: 0 for c in COLOURS}
    for it in character.equipment.get_all_equipped():
        for s in sockets(it):
            g = cut(s.get("gem")) if s.get("gem") else None
            if g:
                for c in FITS.get(g["color"], ()):
                    if c in counts:
                        counts[c] += 1
    return counts


def requirement_met(req, counts):
    """req is one of:
         {"at_least": {"blue": 2}}            two or more gems that count as blue
         {"more": ["red", "blue"]}            more red than blue
         {"each": 1}                          at least one of every colour
    """
    if "at_least" in req:
        return all(counts.get(c, 0) >= n for c, n in req["at_least"].items())
    if "more" in req:
        a, b = req["more"]
        return counts.get(a, 0) > counts.get(b, 0)
    if "each" in req:
        return all(counts.get(c, 0) >= req["each"] for c in COLOURS)
    return False


def requirement_text(req):
    if "at_least" in req:
        return "Requires at least " + " and ".join(f"{n} {c}" for c, n in req["at_least"].items()) + " gems"
    if "more" in req:
        return f"Requires more {req['more'][0]} gems than {req['more'][1]} gems"
    if "each" in req:
        return "Requires at least one red, one yellow and one blue gem"
    return ""


def meta_stats(character):
    """(stats, effects) from every meta gem the wearer has whose condition holds. Effects are
    {key: value} for the engine to read once it's wired (crit_damage_pct, stun_resist_pct...)."""
    stats, effects = {}, {}
    if not META_ENABLED:
        return stats, effects
    counts = colour_counts(character)
    for it in character.equipment.get_all_equipped():
        for s in sockets(it):
            if s.get("color") != "meta" or not s.get("gem"):
                continue
            g = meta_gem(s["gem"])
            if g and requirement_met(g["requires"], counts):
                for k, v in g["stats"].items():
                    stats[k] = stats.get(k, 0) + v
                for k, v in (g.get("effects") or {}).items():
                    effects[k] = effects.get(k, 0) + v
    return stats, effects
