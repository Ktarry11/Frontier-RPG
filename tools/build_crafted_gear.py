#!/usr/bin/env python3
"""Author every crafted gear recipe: fixed stats, written once, the same every time you craft it.

    PYTHONPATH=. python3 tools/build_crafted_gear.py            # write
    PYTHONPATH=. python3 tools/build_crafted_gear.py --check    # audit only, write nothing

Kyle, 14 Nov 2026: "why does VOIDWEAVE....give these random ass stats ... For the love of God look at wow
crafting. I DO however like how we focus specific cloth or specific leather into specific gear types."

HOW WOW DOES IT, and so how this does it:
  - every crafted item has written stats (Felcloth Hood is always the same hood);
  - the material is the identity: Felcloth is the warlock's cloth, Mooncloth the healer's, Runecloth
    the all-rounder's. Here every material has an IDENTITY (a stat split) that fits its armour type;
  - a named line made of that material can have its own identity when its name says so. Silk made
    WoW's Azure (frost), Crimson (fire) and Shadoweave lines, and here Blazethread is fire whatever
    it's woven from. The name has to say it: nothing is assigned at random.

THE NUMBERS are the loot generator's own (entities/loot_generator.py): the same stat budget, the same
armour, weapon damage and price math, so a crafted piece sits beside a quest or dungeon piece of its
level. Only the split is authored. Stats are whole numbers, nothing under a floor (no +1 dribbles),
and whatever rounding takes off goes to the identity's lead stat.

The finished item is written into each recipe as output["item"], and world/crafted_items.py builds
that. RUN THIS LAST after any tool that rewrites the recipe files (build_recipe_expansion and the
like), because those write recipes without it.
"""
import argparse
import collections
import json
import random
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.item import whole                    # noqa: E402
from entities.loot_generator import LootGenerator  # noqa: E402
from world import jewelcrafting                    # noqa: E402

FILES = {
    "tailoring": ROOT / "data/crafting/recipes.json",
    "engineering": ROOT / "data/crafting/recipes.json",
    "blacksmithing": ROOT / "data/blacksmithing/recipes.json",
    "leatherworking": ROOT / "data/leatherworking/recipes.json",
}

PRIMARY = {"strength", "agility", "intellect", "stamina", "spirit"}
SCHOOLS = {"fire_spell_power", "frost_spell_power", "arcane_spell_power", "shadow_spell_power",
           "nature_spell_power", "holy_spell_power"}
CASTER = SCHOOLS | {"spell_power", "healing_power", "mp5", "crit_chance_spell", "spell_penetration"}
PHYSICAL = {"strength", "agility", "attack_power", "crit_chance_physical", "armor_penetration_pct"}
TANK = {"defense_rating", "dodge_rating", "parry_rating", "block_rating", "block_value"}

#: What each armour type may carry. A stat outside its armour type's set fails the audit.
ALLOWED = {
    "cloth": PRIMARY - {"strength", "agility"} | CASTER | {"hit_rating", "haste"},
}

# ---------------------------------------------------------------------------------------------
# IDENTITIES: name -> (stat weights, the stat template it reads as). The weights are a share of the
# budget before each stat's cost, so a 0.25 share of haste (cost 12) is far fewer points than a 0.25
# share of intellect (cost 1). At low item levels a rating rounds to nothing and that budget moves
# to the lead stat, which is right: a level 10 robe has no business carrying haste.
# ---------------------------------------------------------------------------------------------
IDENTITIES = {
    # ---- cloth. Kyle, 14 Nov: "most high end clothes should have sp or healing power primary." So
    # every cloth leads with its power (spell power, a school's power, or healing), like WoW's
    # Bloodvine Vest (27 spell damage over 13 Int) or the Mooncloth Circlet (48 healing over 18 Int).
    # The power phases in on its own: under its floor it's dropped and its share goes to the next
    # stat, so a level 8 linen robe is Int and Stamina, the way a WoW low green is.
    "starter_caster": ({"spell_power": 0.3, "intellect": 0.4, "stamina": 0.3}, "int_caster"),
    "spirit_healer": ({"healing_power": 0.4, "spirit": 0.3, "intellect": 0.3}, "spi_healer"),
    "sturdy_caster": ({"spell_power": 0.4, "intellect": 0.3, "stamina": 0.3}, "int_caster"),
    "traveller": ({"spell_power": 0.35, "stamina": 0.4, "spirit": 0.25}, "int_caster"),
    "caster": ({"spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "arcane": ({"arcane_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "arcane_crit": ({"arcane_spell_power": 0.5, "intellect": 0.2, "crit_chance_spell": 0.3}, "int_caster"),
    "precise_caster": ({"spell_power": 0.5, "intellect": 0.2, "hit_rating": 0.3}, "int_caster"),
    "shadow_sturdy": ({"shadow_spell_power": 0.55, "stamina": 0.45}, "int_caster"),
    "shadow": ({"shadow_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "frost": ({"frost_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "fire": ({"fire_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "spirit_caster": ({"spell_power": 0.55, "spirit": 0.45}, "int_caster"),
    "dark_haste": ({"shadow_spell_power": 0.45, "intellect": 0.25, "haste": 0.3}, "int_caster"),
    "healer": ({"healing_power": 0.55, "spirit": 0.25, "intellect": 0.2}, "spi_healer"),
    "nature": ({"nature_spell_power": 0.6, "spirit": 0.4}, "int_caster"),
    "blood": ({"spell_power": 0.6, "stamina": 0.4}, "int_caster"),
    "fel": ({"shadow_spell_power": 0.55, "stamina": 0.3, "intellect": 0.15}, "int_caster"),
    "death": ({"spell_power": 0.5, "intellect": 0.2, "spell_penetration": 0.3}, "int_caster"),
    "storm": ({"nature_spell_power": 0.45, "intellect": 0.25, "haste": 0.3}, "int_caster"),
    "hex": ({"shadow_spell_power": 0.55, "intellect": 0.45}, "int_caster"),
    "battlemage": ({"spell_power": 0.4, "stamina": 0.3, "crit_chance_spell": 0.3}, "int_caster"),
    "high_healer": ({"healing_power": 0.55, "intellect": 0.25, "spirit": 0.2}, "spi_healer"),
    "void": ({"shadow_spell_power": 0.5, "intellect": 0.3, "stamina": 0.2}, "int_caster"),
}

# ---------------------------------------------------------------------------------------------
# TAILORING. Cloth, for casters and healers. Each cloth: (identity, its line of flavour).
# ---------------------------------------------------------------------------------------------
TAILORING_CLOTH = {
    "linen": ("starter_caster", "Plain linen, stitched tight. Every tailor starts here."),
    "cotton": ("spirit_healer", "Soft cotton. Healers like it because it breathes."),
    "wool": ("sturdy_caster", "Heavy wool that keeps the cold out and the caster on their feet."),
    "hempen": ("traveller", "Rough hempen weave, made for the road and not for looking at."),
    "silk": ("caster", "Good silk. It takes a spell better than anything cheaper."),
    "mageweave": ("arcane", "Mageweave hums a little when you hold it near a ley line."),
    "spidersilk": ("precise_caster", "Spidersilk's light and tough, and it doesn't snag."),
    "netherweave": ("shadow_sturdy", "Netherweave is cold to the touch, and it stays that way."),
    "frostweave": ("frost", "Frostweave. There's always a little rime in the folds."),
    "emberweave": ("fire", "Emberweave stays warm in the snow, and it smells of smoke."),
    "dusk_velvet": ("spirit_caster", "Dusk velvet, dyed the colour of the sky an hour after sunset."),
    "gossamer": ("dark_haste", "Gossamer so thin you'd swear it couldn't hold a stitch."),
    "moonsilk": ("healer", "Moonsilk's spun at night, and healers swear by it."),
    "thistledown": ("nature", "Thistledown cloth, as light as the seed heads it's spun from."),
    "shadowsilk": ("shadow", "Shadowsilk drinks the light around it."),
    "starweave": ("arcane_crit", "Starweave. There are tiny points of light caught in the weave."),
    "bloodsilk": ("blood", "Bloodsilk's dyed in something the tailor won't name."),
    "felcloth": ("fel", "Felcloth. Warlocks pay well for it and don't ask where it came from."),
    "soulcloth": ("death", "Soulcloth is cold, and on quiet nights it whispers."),
    "windwool": ("storm", "Windwool never quite hangs still."),
    "imperial_silk": ("high_healer", "Imperial silk, the best a healer can wear that a tailor can make."),
    "voidweave": ("void", "Voidweave. Look at it too long and it looks back."),
}

#: Named lines that SAY what they are. First match wins. A name that only points at a place or a
#: person (Shadowfang, Taurajo, Silverpine, Arcane Scholar's) says nothing about its stats, so it
#: follows its cloth. And a line only overrides its cloth when it names a different school (see
#: FAMILY): Demonthread on gossamer is already dark cloth, so it stays gossamer's identity.
TAILORING_LINES = [
    (r"Bloodweave|Bloodsoaked", "blood", "A troll pattern. The red dye never fades, however often it's washed."),
    (r"Pilgrim's", "spirit_healer", "A pilgrim's piece, plain and well blessed."),
    (r"Hex Cloth|Fetish|Mojo", "hex", "Troll hexwork, with little charms sewn into the hem."),
    (r"Fireweave|Ember Cloth|Blazethread|Soulscorch", "fire", "Every stitch of it is a little too warm."),
    (r"Spiritweave|Mistweave", "spirit_healer", "A healer's robe, cut loose so it never gets in the way."),
    (r"Moonrobe|Verdant Druid|Scarlet", "healer", "Made for someone who keeps other people standing."),
    (r"Felweave|Felstitched|Fel-Stitched|Demonthread|Infernal", "fel", "Fel-stitched. The thread glows green in the dark."),
    (r"Darkweave|Shadowweave|Voidthread|Dark Elegance|Plagueweave", "shadow", "Dark cloth for dark work."),
    (r"Briarweave|Vine-Woven|Venom Cord|Virulent-Thread", "nature", "There's something green and growing woven through it."),
]

#: Identities in the same family don't override each other (see TAILORING_LINES).
FAMILY = {
    "shadow": {"shadow", "shadow_sturdy", "fel", "dark_haste", "void", "hex", "death"},
    "healer": {"spirit_healer", "healer", "high_healer"},
    "nature": {"nature", "storm"},
}


def family(ident):
    return next((f for f, members in FAMILY.items() if ident in members), ident)


TRADES = {
    "tailoring": {"materials": TAILORING_CLOTH, "lines": TAILORING_LINES, "armour": {"cloth"}},
}


# ---------------------------------------------------------------------------------------------
# the engine
# ---------------------------------------------------------------------------------------------
_GEN = LootGenerator()
COST = _GEN.stat_budget_costs


def identity_for(trade, recipe):
    """(identity, flavour, where it came from) for one recipe. A named line wins over its material."""
    t = TRADES[trade]
    tier = recipe["output"].get("material_tier")
    base = t["materials"].get(tier)
    for pat, ident, flav in t["lines"]:
        if re.search(pat, recipe["name"]):
            if base is None or family(ident) != family(base[0]):
                return ident, flav, "line"
            break
    if base is not None:
        return base[0], base[1], "material"
    return None, None, None


def budget(out):
    """The generator's stat budget for this recipe's slot, level and rarity, plus the 15% bonus a
    rolled green or better gets on top (LootGenerator._roll_stats' bonus rolls), so an authored piece
    isn't weaker than a random one of the same level."""
    rar = _GEN.rarity_tiers[out["rarity"]]
    if out["kind"] == "weapon":
        wd = _GEN.weapon_types["weapon_types"][out["weapon_type"]]
        tier = "weapon_two_hand" if wd["hand"] == "two_hand" else "weapon_medium"
        b = out["item_level"] * _GEN.STAT_BUDGET_BASE_MULT * rar["stat_budget_multiplier"] \
            * _GEN.slots["weight_tiers"][tier] * wd["budget_multiplier"]
    else:
        tier = _GEN.slots["slots"][out["slot"]]["weight_tier"]
        b = out["item_level"] * _GEN.STAT_BUDGET_BASE_MULT * rar["stat_budget_multiplier"] \
            * _GEN.slots["weight_tiers"][tier]
    return b * (1.15 if rar.get("bonus_stat_rolls") else 1.0)


#: A power stat (spell power, a school's power, healing, attack power) is only on an item once it's
#: worth having. Under this it's dropped and its share goes to the item's other stats.
POWER = CASTER - {"crit_chance_spell", "spell_penetration", "mp5"} | {"attack_power"}
POWER_FLOOR = 3


def floor_for(stat, item_level):
    """The smallest a stat may be (Kyle: "Biggest thing is dribble on stats"). Ratings are whole
    percents, so 1 is a real stat; a +1 or +2 primary on a level 30 robe isn't."""
    if stat in POWER:
        return POWER_FLOOR
    if stat in PRIMARY:
        return 2 if item_level < 20 else 3
    # a rating is a whole percent, and a lone +1% under 70 spell power reads as a leftover (Kyle's
    # Bloodvine Vest carries 2% hit). So it's 2% or it isn't on the item.
    return 2


RATINGS = {"hit_rating", "crit_chance_spell", "crit_chance_physical", "haste", "spell_penetration",
           "dodge_rating", "parry_rating", "block_rating", "defense_rating", "armor_penetration_pct"}
#: The most of an item's budget a 2% rating may take. Ratings are dear in this game (2% crit is 20
#: points, more than a level 60 pair of bracers is worth), so like WoW's Bloodvine set the rating is on
#: the pieces big enough to carry it and the small pieces are all power.
RATING_SHARE_MAX = 0.4


def split(weights, total, item_level):
    """Whole-number stats from a budget. A rating is 2% or it isn't there (see RATING_SHARE_MAX). Any
    other stat under its floor is dropped, and what it was worth goes, with whatever rounding took
    off, to the strongest stat that's left."""
    weights = dict(weights)
    keep = {}
    for r in [st for st in weights if st in RATINGS]:
        cost = COST.get(r, 1.0) * 2
        w = weights.pop(r)
        if cost <= total * RATING_SHARE_MAX:
            keep[r] = 2
            total -= cost
    if not weights:
        return {}, keep
    norm = sum(weights.values())
    weights = {st: w / norm for st, w in weights.items()}
    order = sorted(weights, key=weights.get, reverse=True)
    loss = 0.0
    for stat in order:
        cost = COST.get(stat, 1.0)
        raw = total * weights[stat] / cost
        v = whole(raw)
        if v < floor_for(stat, item_level):
            loss += raw * cost
            continue
        loss += (raw - v) * cost
        keep[stat] = v
    main = next((st for st in order if st in keep), None)
    if main is None:
        # nothing reached its floor (a level 2 item): it's all one primary
        main = next((st for st in order if st in PRIMARY), order[0])
        keep[main] = max(1, whole(total / COST.get(main, 1.0)))
    elif loss >= 0.5:
        keep[main] += whole(loss / COST.get(main, 1.0))
    prim = {st: v for st, v in keep.items() if st in PRIMARY}
    sec = {st: v for st, v in keep.items() if st not in PRIMARY}
    return prim, sec


def reference(rid, out):
    """The generator's own armour, damage, speed, block and price for this piece, seeded on the recipe
    so it never changes. Its rolled stats are thrown away."""
    state = random.getstate()
    random.seed(zlib.crc32(rid.encode("utf-8")))
    jewelcrafting._SUPPRESSED[0] += 1
    try:
        if out["kind"] == "weapon":
            return _GEN.generate_weapon(out["slot"], out["weapon_type"], out["stat_template"],
                                        out["item_level"], out["rarity"])
        return _GEN.generate_armor_piece(out["slot"], out["armor_type"], out["stat_template"],
                                         out["item_level"], out["rarity"])
    finally:
        jewelcrafting._SUPPRESSED[0] -= 1
        random.setstate(state)


def author(rid, recipe, ident, flavour):
    out = recipe["output"]
    weights, template = IDENTITIES[ident]
    prim, sec = split(weights, budget(out), out["item_level"])
    ref = reference(rid, out)
    item = {
        "name": recipe["name"], "slot": out["slot"], "item_level": out["item_level"],
        "rarity": out["rarity"], "armor_type": ref.armor_type, "weapon_type": ref.weapon_type,
        "stat_template": template, "primary_stats": prim, "secondary_stats": sec,
        "armor_value": ref.armor_value, "required_level": ref.required_level,
        "sell_price": ref.sell_price, "flavor_text": flavour, "identity": ident,
    }
    if out["kind"] == "weapon":
        item.update(weapon_damage_min=ref.weapon_damage_min, weapon_damage_max=ref.weapon_damage_max,
                    attack_speed=ref.attack_speed, block_value=ref.block_value)
    return item


#: From this item level, a cloth piece has to lead with its power (Kyle: "high end clothes should have
#: sp or healing power primary").
POWER_LEADS_FROM = 25


def audit_item(trade, rid, item):
    bad = []
    armour = item.get("armor_type")
    allowed = ALLOWED.get(armour)
    stats = {**item["primary_stats"], **item["secondary_stats"]}
    tag = f"{rid} ({item['name']})"
    if allowed is not None:
        for st in stats:
            if st not in allowed:
                bad.append(f"{tag}: {st} on {armour}")
    if item["item_level"] >= 10:
        for st, v in stats.items():
            if v < floor_for(st, item["item_level"]):
                bad.append(f"{tag}: +{v} {st} is a dribble")
    if not stats:
        bad.append(f"{tag}: no stats")
    if armour == "cloth" and item["item_level"] >= POWER_LEADS_FROM:
        powers = {st: v for st, v in stats.items() if st in POWER}
        if not powers:
            bad.append(f"{tag}: high-end cloth with no spell power or healing")
        elif max(powers.values()) < max(stats.values()):
            bad.append(f"{tag}: its power isn't its biggest stat {stats}")
    return bad


def run(write):
    docs, bad, report = {}, [], collections.defaultdict(collections.Counter)
    for trade in TRADES:
        path = FILES[trade]
        if path not in docs:
            docs[path] = json.loads(path.read_text(encoding="utf-8"))
        d = docs[path]
        recipes = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        for rid, r in recipes.items():
            out = r.get("output") or {}
            if out.get("kind") not in ("armor", "weapon"):
                continue
            ident, flav, why = identity_for(trade, r)
            if ident is None:
                bad.append(f"{trade} {rid} ({r['name']}): no identity for material {out.get('material_tier')}")
                continue
            item = author(rid, r, ident, flav)
            bad += audit_item(trade, rid, item)
            out["item"] = item
            report[trade][ident] += 1
    for trade, c in report.items():
        print(f"{trade}: {sum(c.values())} pieces authored; identities {dict(c.most_common())}")
    if bad:
        print(f"\nFAILED ({len(bad)}):")
        for b in bad[:80]:
            print("  -", b)
        return 1
    if write:
        for path, d in docs.items():
            path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    sys.exit(run(not ap.parse_args().check))
