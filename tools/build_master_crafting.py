#!/usr/bin/env python3
"""Master crafting: level-60 gear from the ten level-60 materials, competitive with heroics and raids.

    PYTHONPATH=. python3 tools/build_master_crafting.py           # check
    PYTHONPATH=. python3 tools/build_master_crafting.py --write   # into each trade's recipes

Kyle, 18 Nov 2026: "I'll ALWAYS want crafting to be competitive to raiding/Dungeons", "Then we can add crafting for
new gear for each profession", "Keep going". His answers: a new Master tier, cap 325, from the Artisan trainers at
level 60 (data/professions/professions.json); level 60's materials are the two lowest top-tier rungs of each ladder
(entities/material_tiers.LEVEL60_TOP).

What it writes (docs/master_crafting.md):
  * two Tailoring bolts, Dreamsilk and Chronoweave (the planks, bars and cut gems already exist);
  * per gear trade, BLUES at item level 66 (level with a heroic's drops), worn at 60, taught by the trainer at skill
    300-318, made of the first rung (Dreamsilk, Manticore, Frostforged Silver, Voidwood, Glacier Sapphire); and EPICS
    at 68 (level with T1 and Exalted), skill 320-325, of the second rung (Chronoweave, Chimera, Sylvanite,
    Dreamwillow, Sylvan Emerald) plus a gem, whose patterns only drop from heroic bosses (source "heroic",
    world/heroic.roll_pattern);
  * the 32 Exalted rep patterns (68) lose their stand-in ingredients (build_faction_rewards' PLACEHOLDER, "until the
    rare ingredients exist") for their trade's second-rung materials.
Every item is authored like every other crafted piece (tools/build_crafted_gear.author: identity, icon, audit), then
put on the item curve (1.0), the same strength as a heroic drop of its level.
Re-running replaces what it wrote (ids "m60_"), and never touches anything else.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

BLUE_ILVL, EPIC_ILVL, WORN_AT = 66, 68, 60
PREFIX = "m60_"
TRADE_FILE = {"tailoring": "crafting", "woodworking": "crafting", "engineering": "crafting",
              "blacksmithing": "blacksmithing", "leatherworking": "leatherworking", "jewelcrafting": "jewelcrafting"}

#: a trade's first-rung (blue) and second-rung (epic) materials: (inputs for a big piece, material tier name)
MATS = {
    "tailoring": ({"bolt_dreamsilk": 8, "thread_silken": 2},
                  {"bolt_chronoweave": 10, "bolt_dreamsilk": 4, "thread_silken": 2, "gem_glacier_sapphire": 1},
                  "dreamsilk", "chronoweave"),
    "leatherworking": ({"leather_manticore": 10, "thread_silken": 2},
                       {"leather_chimera": 12, "leather_manticore": 4, "thread_silken": 2, "gem_sylvan_emerald": 1},
                       "manticore", "chimera"),
    "blacksmithing": ({"bar_frostforged_silver": 10, "flux_strong": 2},
                      {"bar_sylvanite": 12, "bar_frostforged_silver": 4, "flux_strong": 2, "gem_sylvan_emerald": 1},
                      "frostforged_silver", "sylvanite"),
    "woodworking": ({"plank_voidwood": 10, "fiber_warded": 2, "stick_ironbound": 1, "resin": 1},
                    {"plank_dreamwillow": 12, "plank_voidwood": 4, "fiber_warded": 2, "resin": 2,
                     "gem_glacier_sapphire": 1},
                    "voidwood", "dreamwillow"),
    "jewelcrafting": ({"bar_frostforged_silver": 2, "gem_glacier_sapphire": 2},
                      {"bar_sylvanite": 3, "gem_sylvan_emerald": 2, "gem_glacier_sapphire": 1},
                      "frostforged_silver", "sylvanite"),
    "engineering": ({"bar_frostforged_silver": 8, "part_gear_assembly": 2},
                    {"bar_sylvanite": 10, "bar_frostforged_silver": 4, "part_gear_assembly": 3,
                     "gem_glacier_sapphire": 1},
                    "frostforged_silver", "sylvanite"),
}
#: smaller pieces take less: slot -> share of the big piece's quantities
SLOT_SHARE = {"chest": 1.0, "legs": 1.0, "main_hand": 1.0, "head": 0.8, "shoulder": 0.7, "hands": 0.6, "feet": 0.6,
              "waist": 0.5, "wrist": 0.4, "back": 0.6, "off_hand": 0.7, "ranged": 0.7, "ring": 1.0, "neck": 1.0}

# (id, name, slot, kind, type, identity, flavour)
BLUES = {
    "tailoring": [
        ("dreamsilk_hood", "Dreamsilk Hood", "head", "armor", "cloth", "caster_crit", "Dreamsilk is spun from what drifts out of the Dream at night. It remembers being a thought."),
        ("dreamsilk_mantle", "Dreamsilk Mantle", "shoulder", "armor", "cloth", "high_healer", "Light on the shoulders, like a hand that means well."),
        ("dreamsilk_robe", "Dreamsilk Robe", "chest", "armor", "cloth", "caster", "It moves a moment after you do, as if it's still deciding."),
        ("dreamsilk_cuffs", "Dreamsilk Cuffs", "wrist", "armor", "cloth", "haste_caster", "Quick hands make quick spells. These help with the hands."),
        ("dreamsilk_gloves", "Dreamsilk Gloves", "hands", "armor", "cloth", "healer", "Every stitch was a wish for someone else's health."),
        ("dreamsilk_sash", "Dreamsilk Sash", "waist", "armor", "cloth", "precise_caster", "Tied once, and it never comes loose."),
        ("dreamsilk_leggings", "Dreamsilk Leggings", "legs", "armor", "cloth", "spirit_healer", "Soft enough to sleep in, which is rather the point."),
        ("dreamsilk_slippers", "Dreamsilk Slippers", "feet", "armor", "cloth", "arcane", "You can't hear them on stone. You can barely hear them on glass."),
        ("dreamsilk_cloak", "Dreamsilk Cloak", "back", "armor", "cloth", "caster_crit", "It's never quite the same colour twice."),
    ],
    "leatherworking": [
        ("manticore_helm", "Manticore Hide Helm", "head", "armor", "leather", "agility", "Manticore hide turns a blade by habit. The beast turned a few in its time."),
        ("manticore_spaulders", "Manticore Hide Spaulders", "shoulder", "armor", "leather", "rogue_crit", "The tail barbs were kept. Somebody always asks."),
        ("manticore_tunic", "Manticore Hide Tunic", "chest", "armor", "leather", "feral", "Thick at the chest, loose at the arms, built for something with claws."),
        ("manticore_bracers", "Manticore Hide Bracers", "wrist", "armor", "leather", "assassin", "Stitched with the beast's own sinew. It holds."),
        ("manticore_grips", "Manticore Hide Grips", "hands", "armor", "leather", "agility", "Rough palms, sure fingers."),
        ("manticore_belt", "Manticore Hide Belt", "waist", "armor", "leather", "rogue_crit", "Room for six knives. People always find a seventh."),
        ("manticore_leggings", "Manticore Hide Leggings", "legs", "armor", "leather", "feral", "Creased at the knee like it's ready to pounce."),
        ("manticore_boots", "Manticore Hide Boots", "feet", "armor", "leather", "assassin", "Soft soles, hard toes."),
        ("manticore_coif", "Manticore-Scale Coif", "head", "armor", "mail", "hunter", "Scales from the beast's mane, set in rings."),
        ("manticore_hauberk", "Manticore-Scale Hauberk", "chest", "armor", "mail", "mail_caster", "Heavier than it looks, lighter than it was on the manticore."),
        ("manticore_gauntlets", "Manticore-Scale Gauntlets", "hands", "armor", "mail", "hunter_crit", "Every knuckle a scale, every scale an argument."),
        ("manticore_girdle", "Manticore-Scale Girdle", "waist", "armor", "mail", "tide_healer", "A healer's belt with a hunter's patience."),
        ("manticore_legguards", "Manticore-Scale Legguards", "legs", "armor", "mail", "hunter", "Good for long walks and short arguments."),
        ("manticore_sabatons", "Manticore-Scale Sabatons", "feet", "armor", "mail", "mail_caster", "They ring a little on stone, like distant rain."),
    ],
    "blacksmithing": [
        ("frostforged_helm", "Frostforged Helm", "head", "armor", "plate", "tank", "Frostforged silver keeps its edge in the cold and its shape in the fire."),
        ("frostforged_pauldrons", "Frostforged Pauldrons", "shoulder", "armor", "plate", "strength", "Rimed at the edges whatever the weather."),
        ("frostforged_breastplate", "Frostforged Breastplate", "chest", "armor", "plate", "tank", "Quenched in snowmelt three times. The smith swears by it."),
        ("frostforged_bracers", "Frostforged Bracers", "wrist", "armor", "plate", "strength_crit", "Cold to put on. Colder to be hit by."),
        ("frostforged_gauntlets", "Frostforged Gauntlets", "hands", "armor", "plate", "strength_hit", "Your grip never slips. Your opponents' do."),
        ("frostforged_girdle", "Frostforged Girdle", "waist", "armor", "plate", "plate_healer", "A paladin's belt, buckled with a silver sun."),
        ("frostforged_legplates", "Frostforged Legplates", "legs", "armor", "plate", "tank", "Built to stand in a doorway and not move."),
        ("frostforged_sabatons", "Frostforged Sabatons", "feet", "armor", "plate", "strength", "Every step leaves a little frost behind."),
        ("frostforged_greatsword", "Frostforged Greatsword", "main_hand", "weapon", "sword_2h", "strength", "A blade as long as a dwarf, and twice as stubborn."),
        ("frostforged_longsword", "Frostforged Longsword", "main_hand", "weapon", "sword_1h", "strength_crit", "Balanced on a single finger, and fond of throats."),
        ("frostforged_bulwark", "Frostforged Bulwark", "off_hand", "weapon", "shield", "shield_tank", "Frost creeps across its face when something hits it."),
        ("frostforged_hammer", "Frostforged Hammer", "main_hand", "weapon", "mace_1h", "plate_healer", "A healer's hammer. It still breaks things."),
    ],
    "woodworking": [
        ("voidwood_staff", "Voidwood Staff", "main_hand", "weapon", "staff", "caster", "Voidwood grows towards the dark. A caster can feel it pulling."),
        ("voidwood_longbow", "Voidwood Longbow", "ranged", "weapon", "bow", "hunter", "Silent on the draw. Silent on the shot."),
        ("voidwood_codex", "Voidwood Codex", "off_hand", "weapon", "tome", "healer", "Its pages are the colour of a moonless night, and the words glow."),
        ("voidwood_wand", "Voidwood Wand", "ranged", "weapon", "wand", "caster_crit", "Point it at something you dislike."),
        ("voidwood_totem", "Voidwood Totem", "ranged", "weapon", "totem", "storm", "Carved with four faces. The fifth carved itself."),
    ],
    "jewelcrafting": [
        ("glacier_ring", "Glacier Sapphire Ring", "ring", "armor", None, "caster", "The sapphire is cold enough to fog the glass it's kept under."),
        ("glacier_pendant", "Glacier Sapphire Pendant", "neck", "armor", None, "healer", "Worn against the heart, it keeps it steady."),
        ("frostforged_band", "Frostforged Band", "ring", "armor", None, "agility", "Plain silver, perfectly round, and very sharp at one edge."),
        ("frostforged_choker", "Frostforged Choker", "neck", "armor", None, "strength", "A soldier's necklace: no stones to catch, nothing to grab."),
    ],
    "engineering": [
        ("frostforged_rifle", "Frostforged Rifle", "ranged", "weapon", "gun", "hunter", "Cold barrel, hot shot. The goblins call it balance."),
        ("spellsight_goggles", "Frostforged Spellsight Goggles", "head", "armor", "cloth", "caster_crit", "See the weave of a spell, and where to pull it."),
        ("scout_goggles", "Frostforged Scout Goggles", "head", "armor", "leather", "hunter", "Twelve lenses, one of which is pointing the right way."),
    ],
}
EPICS = {
    "tailoring": [
        ("chronoweave_cowl", "Chronoweave Cowl", "head", "armor", "cloth", "arcane_crit", "Chronoweave is spun from cloth that was in two places at once. The cowl still is, slightly."),
        ("chronoweave_vestments", "Chronoweave Vestments", "chest", "armor", "cloth", "high_healer", "Every wound it sees, it remembers how it looked before."),
        ("chronoweave_trousers", "Chronoweave Trousers", "legs", "armor", "cloth", "haste_caster", "You arrive a heartbeat before you meant to."),
        ("cloak_of_hours", "Chronoweave Cloak of Hours", "back", "armor", "cloth", "caster", "Twelve folds, one for every hour. The thirteenth is for emergencies."),
    ],
    "leatherworking": [
        ("chimera_jerkin", "Chimera Hide Jerkin", "chest", "armor", "leather", "rogue_crit", "Three heads' worth of hide, and it still argues with itself."),
        ("chimera_leggings", "Chimera Hide Leggings", "legs", "armor", "leather", "feral", "Built for a hunter who's half beast already."),
        ("chimera_hauberk", "Chimera-Scale Hauberk", "chest", "armor", "mail", "hunter_crit", "Every scale was taken from a chimera that wanted it back."),
        ("chimera_legguards", "Chimera-Scale Legguards", "legs", "armor", "mail", "mail_caster", "Cool as river stone, warm when it counts."),
    ],
    "blacksmithing": [
        ("sylvanite_warhelm", "Sylvanite Warhelm", "head", "armor", "plate", "tank", "Sylvanite rings like a bell when it's struck, so you always know who's hitting you."),
        ("sylvanite_breastplate", "Sylvanite Breastplate", "chest", "armor", "plate", "strength", "Green-silver, light as oak, harder than the anvil it was made on."),
        ("sylvanite_greataxe", "Sylvanite Greataxe", "main_hand", "weapon", "axe_2h", "strength_crit", "It chops through the first thing and keeps going out of politeness."),
        ("sylvanite_aegis", "Sylvanite Aegis", "off_hand", "weapon", "shield", "shield_tank", "Engraved with every name it's protected. There's room for more."),
    ],
    "woodworking": [
        ("dreamwillow_greatstaff", "Dreamwillow Greatstaff", "main_hand", "weapon", "staff", "high_healer", "Dreamwillow only grows where someone once slept well. It wants to help."),
        ("dreamwillow_warbow", "Dreamwillow Warbow", "ranged", "weapon", "bow", "hunter_crit", "The string hums a lullaby. The target never hears the end of it."),
    ],
    "jewelcrafting": [
        ("signet_of_frost", "Sylvanite Signet of Frost", "ring", "armor", None, "caster_crit", "A sapphire set in sylvanite. Breathe on it and it frosts."),
        ("sylvan_torc", "Sylvan Emerald Torc", "neck", "armor", None, "tank", "Three emeralds, three oaths, one neck to keep them on."),
    ],
    "engineering": [
        ("sylvanite_hand_cannon", "Sylvanite Hand Cannon", "ranged", "weapon", "gun", "hunter_crit", "Technically handheld. Technically a cannon. Technically legal."),
        ("gyro_goggles", "Sylvanite Gyro-Goggles", "head", "armor", "mail", "hunter", "The lenses spin on their own. Don't ask what they're looking for."),
    ],
}
BOLTS = [
    ("tail_bolt_dreamsilk", "Bolt of Dreamsilk", {"cloth_dreamsilk": 3}, "bolt_dreamsilk", 300, [305, 312, 318, 325]),
    ("tail_bolt_chronoweave", "Bolt of Chronoweave", {"cloth_chronoweave": 3}, "bolt_chronoweave", 310,
     [312, 318, 322, 328]),
]


def scaled(inputs, slot):
    k = SLOT_SHARE.get(slot, 0.7)
    return {m: max(1, int(round(n * k))) for m, n in inputs.items()}


def recipe(C, trade, rid, name, slot, kind, typ, ident, flav, rarity, ilvl, skill, inputs, tier, source):
    out = {"kind": kind, "slot": slot, "item_level": ilvl, "rarity": rarity, "required_level": WORN_AT,
           "stat_template": C.IDENTITIES[ident][1], "material_tier": tier, "fixed_item_level": True}
    if kind == "weapon":
        out["weapon_type"] = typ
        ident = C.weapon_identity(typ, ident)
    else:
        out["armor_type"] = typ
    item = C.author(rid, {"name": name, "output": out}, ident, flav)
    item["required_level"] = WORN_AT
    # ON THE CURVE, like a heroic drop (world/heroic.heroic_def): crafted is level with heroics and T1 at the same
    # item level, never above or below them (Kyle: "competitive to raiding/Dungeons")
    from entities.item_budget import fit_to_curve
    fit_to_curve(item, target=1.0)
    out["item"] = item
    rec = {"name": name, "inputs": inputs, "skill_required": skill,
           "skill_range": [skill + 3, skill + 8, skill + 13, skill + 18], "source": source, "output": out}
    if trade == "jewelcrafting":
        rec["tool"] = "jewelers_kit"
    return rec, C.audit_item(trade, rid, item)


def build():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    C.PICKER = Picker()
    made, bad = {}, []
    for trade, rows in BLUES.items():
        blue_in, _e, blue_tier, _t = MATS[trade]
        for n, (key, name, slot, kind, typ, ident, flav) in enumerate(rows):
            skill = min(318, 300 + 2 * n)
            rid = f"{PREFIX}{key}"
            rec, b = recipe(C, trade, rid, name, slot, kind, typ, ident, flav, "rare", BLUE_ILVL, skill,
                            scaled(blue_in, slot), blue_tier, "trainer")
            made[(trade, rid)] = rec
            bad += b
    for trade, rows in EPICS.items():
        _b, epic_in, _t, epic_tier = MATS[trade]
        for n, (key, name, slot, kind, typ, ident, flav) in enumerate(rows):
            skill = min(325, 320 + 2 * n)
            rid = f"{PREFIX}{key}"
            rec, b = recipe(C, trade, rid, name, slot, kind, typ, ident, flav, "epic", EPIC_ILVL, skill,
                            scaled(epic_in, slot), epic_tier, "heroic")
            made[(trade, rid)] = rec
            bad += b
    for rid, name, inputs, out_id, skill, rng in BOLTS:
        made[("tailoring", f"{PREFIX}{rid}")] = {"name": name, "inputs": inputs, "skill_required": skill,
                                                 "skill_range": rng, "source": "trainer",
                                                 "output": {"kind": "material", "material_id": out_id}}
    return made, bad


def assign_icons(made):
    """Each new piece its own icon, by tools/assign_crafted_icons' rules but from the art already installed (the WoW
    pack it draws on isn't here): nearest the collection's colour, never twice in a collection, an epic's never used
    by anything else, never a named epic's. Written to data/items/crafted_icons.json so a rebuild keeps them.
    -> names still on a shared or stand-in icon."""
    import collections
    import crafted_icon_palette as CP
    import assign_crafted_icons as A
    path = ROOT / "data/items/crafted_icons.json"
    doc = json.loads(path.read_text(encoding="utf-8"))
    assigned = doc["icons"]
    mine = {rec["output"]["item"]["name"]: rec["output"]["item"] for rec in made.values()
            if isinstance(rec.get("output", {}).get("item"), dict)}
    elsewhere = A.icons_used_elsewhere()
    ep = json.loads((ROOT / "data/loot/epic_drops.json").read_text(encoding="utf-8"))
    epic_owned = {d.get("icon_id") for k in ("world", "dungeon") for d in ep.get(k, [])}
    # every other crafted piece's icon as it stands in the recipes (some, like the rep epics, aren't in the map)
    used = collections.Counter()
    seen_names = set()
    epic_taken = set()          # an epic's icon is its alone: no blue may take one either
    for f in A.FILES:
        for it in A.walk(json.loads((ROOT / f).read_text(encoding="utf-8"))):
            if it["name"] not in mine and it["name"] not in seen_names and it.get("icon_id"):
                seen_names.add(it["name"])
                used[it["icon_id"]] += 1
                if it.get("rarity") in ("epic", "legendary"):
                    epic_taken.add(it["icon_id"])
    for n, i in assigned.items():
        if n not in mine and n not in seen_names:
            used[i] += 1
    by_set = collections.defaultdict(set)
    short = []
    order = sorted(mine, key=lambda n: (mine[n].get("rarity") != "epic", n))     # epics pick first
    for name in order:
        it = mine[name]
        if name in assigned and assigned[name] == it.get("icon_id") and used[assigned[name]] == 0:
            used[assigned[name]] += 1
            by_set[name.split()[0].lower()].add(assigned[name])
            if it.get("rarity") == "epic":
                epic_taken.add(assigned[name])
            continue
        epic = it.get("rarity") == "epic"
        pool = [i for i in CP.pool(it["slot"], it.get("armor_type"), it.get("weapon_type"))
                if i not in epic_owned and (GEAR / f"{i}.png").exists()]
        coll = name.split()[0].lower()
        if epic:
            pool = [i for i in pool if not used[i] and not elsewhere.get(i)]
        else:
            pool = [i for i in pool if i not in epic_taken]
        pool = [i for i in pool if i not in by_set[coll]] or pool
        want = CP.target(name, it.get("armor_type"))
        if not pool:
            # nothing unused of this kind: an epic gets its own recoloured copy of the nearest icon of its kind
            pool = [i for i in CP.pool(it["slot"], it.get("armor_type"), it.get("weapon_type"))
                    if (GEAR / f"{i}.png").exists()]
        if not pool:
            short.append(name)
            continue
        best = min(pool, key=lambda i: (CP.distance(want, CP.measure(i)) + (0 if epic else
                                        0.5 * used[i] + (1.0 if elsewhere.get(i) else 0.0)), i))
        if epic and (used[best] or elsewhere.get(best) or best in epic_owned):
            best = tinted(best, name, want)
        it["icon_id"] = best
        assigned[name] = best
        used[best] += 1
        by_set[coll].add(best)
        if epic:
            epic_taken.add(best)
        if used[best] > 1 or elsewhere.get(best):
            short.append(name)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return short


GEAR = ROOT / "assets/icons/gear"


def tinted(base, name, want):
    """A stand-in icon of its own for an epic whose kind has no unused art: `base` with its hue turned to the
    collection's colour (want = (hue, sat, value)), saved as gear_m60_<name>. Kyle okayed tinted stand-ins for the
    class abilities (18 Nov 2026); the real icon comes from an art sheet."""
    import re
    from PIL import Image
    slug = "gear_m60_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
    img = Image.open(GEAR / f"{base}.png").convert("RGBA")
    r, g, b, a = img.split()
    hsv = Image.merge("RGB", (r, g, b)).convert("HSV")
    h, s_, v = hsv.split()
    hue = int(want[0] / 360 * 255) % 256
    sat_floor = int(min(255, 90 + want[1] * 120))
    h = h.point(lambda _x: hue)
    s_ = s_.point(lambda x: max(x, sat_floor) if x > 25 else x)
    out = Image.merge("HSV", (h, s_, v)).convert("RGB")
    out.putalpha(a)
    out.save(GEAR / f"{slug}.png")
    return slug


def main():
    write = "--write" in sys.argv
    made, bad = build()
    trades = {}
    for (trade, rid) in made:
        trades[trade] = trades.get(trade, 0) + 1
    print(f"  {len(made)} recipes: " + ", ".join(f"{t} {n}" for t, n in sorted(trades.items())))
    if bad:
        print("  audit:\n    " + "\n    ".join(bad[:30]))
        return 1
    if not write:
        return 0
    short = assign_icons(made)
    if short:
        print(f"  {len(short)} pieces share or lack an icon of their own (art pending): {short[:8]}")
    docs = {}
    for (trade, rid), rec in made.items():
        path = ROOT / "data" / TRADE_FILE[trade] / "recipes.json"
        d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        book[rid] = rec
    # the Exalted rep patterns' real ingredients
    swapped = 0
    for trade, (_b, epic_in, _t, epic_tier) in MATS.items():
        path = ROOT / "data" / TRADE_FILE[trade] / "recipes.json"
        d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
        book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        for rid, r in book.items():
            if rid.startswith("rep_") and r.get("_rare_ingredients_todo"):
                out = r.get("output") or {}
                slot = out.get("slot")
                made_item = out.get("item") if isinstance(out.get("item"), dict) else out
                if made_item.get("rarity") == "epic":            # Exalted, 68: the second rung
                    r["inputs"], r["skill_required"], out["material_tier"] = scaled(epic_in, slot), 320, epic_tier
                elif (made_item.get("item_level") or 0) >= 66:   # Revered, 66: the first rung
                    r["inputs"], r["skill_required"], out["material_tier"] = scaled(MATS[trade][0], slot), 305, MATS[trade][2]
                else:                                           # Honored, 62: stays pre-60 (its stand-in)
                    import build_faction_rewards as F
                    pin, ptier = F.PLACEHOLDER[trade]
                    r["inputs"], r["skill_required"], out["material_tier"] = scaled(dict(pin), slot), 300, ptier
                s = r["skill_required"]
                r["skill_range"] = [s + 3, s + 8, s + 13, s + 18] if s > 300 else [300, 305, 310, 315]
                del r["_rare_ingredients_todo"]
                swapped += 1
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  written; {swapped} Exalted rep patterns got their real ingredients")
    return 0


if __name__ == "__main__":
    sys.exit(main())
