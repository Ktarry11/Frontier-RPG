#!/usr/bin/env python3
"""Hidden sellers: a pool of seven one-of-a-kind pieces each (four on the shelf at a time), at three quarters of the
old price. Idempotent.

    PYTHONPATH=. python3 tools/build_secret_rotation.py [--check]

Kyle, 17 Nov 2026, at a hidden seller: "His items are almost 4g. I think we should do 2 things. 1 make like 25%
cheaper for weapon and armor from these vendors. But 2, we have rotating stock in these secret vendors....like they
have 6 or 7 blue items but only 3 to 4 are at once. They can follow 12 hour rotations with the time passing like how
the AH passes. So it rewards returning to them."

  1. PRICE. Every one-of-a-kind piece a hidden seller carries (data/items/secret_uniques.json) costs 75% of what
     tools/build_secrets.price gave it. The original is kept as "price_full", so a second run changes nothing.
  2. THE POOL. A seller with three or four pieces gets new ones up to POOL, at the item level of the ones it
     already had. The shelf shows four at a time and turns over every twelve market hours (world/vendor_rotation.py).
     The new pieces:
       - are made by the game's own LootGenerator at rare, so their stats follow today's item formula (ratings,
         whole numbers), the same way the dungeon pools are made;
       - fill the gaps in what that seller had, drawn from one plan that walks every armour class, every stat
         template and the weapon types the hidden sellers never carried (fist weapons, crossbows, wands, thrown,
         one-hand maces, tomes), so the whole set spreads across the classes (Kyle's standing rule);
       - are named from the seller's own pieces and name (Talo Skyhide's "Windcaught Mantle" gives "Windcaught
         ..."), never twice in the game, and carry no flavour text (Kyle: flavour is for epics and up).
  Sellers that trade in something other than gold, and the few that never carried gear, are left as they are.
  Never says where a seller is: counts only (Kyle's rule for secrets).
"""
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

UNIQUES = ROOT / "data/items/secret_uniques.json"
VENDORS = ROOT / "data/npcs/vendors.json"
POOL = 7
PRICE_CUT = 0.75

#: (slot, kind, type, stat template). Walked in order across every seller that needs pieces, skipping what a seller
#: already has, so armour classes, templates and weapon types come out even over the set.
PLAN = [
    ("head", "armor", "cloth", "int_caster"), ("legs", "armor", "leather", "agi_physical"),
    ("main_hand", "weapon", "fist_weapon", "agi_physical"), ("shoulder", "armor", "mail", "agi_int_hybrid"),
    ("hands", "armor", "plate", "str_physical"), ("ranged", "weapon", "wand", "int_caster"),
    ("feet", "armor", "cloth", "spi_healer"), ("waist", "armor", "mail", "str_int_hybrid"),
    ("main_hand", "weapon", "mace_1h", "spi_healer"), ("wrist", "armor", "leather", "spi_healer"),
    ("chest", "armor", "plate", "str_int_hybrid"), ("ranged", "weapon", "crossbow", "agi_physical"),
    ("legs", "armor", "mail", "agi_physical"), ("head", "armor", "plate", "str_physical"),
    ("off_hand", "weapon", "tome", "int_caster"), ("shoulder", "armor", "leather", "agi_int_hybrid"),
    ("hands", "armor", "cloth", "int_caster"), ("main_hand", "weapon", "axe_2h", "str_physical"),
    ("waist", "armor", "leather", "agi_physical"), ("feet", "armor", "plate", "str_int_hybrid"),
    ("ranged", "weapon", "thrown", "agi_physical"), ("back", "armor", "cloth", "agi_physical"),
    ("chest", "armor", "mail", "spi_healer"), ("main_hand", "weapon", "dagger", "int_caster"),
    ("wrist", "armor", "plate", "str_physical"), ("legs", "armor", "cloth", "spi_healer"),
    ("off_hand", "weapon", "shield", "str_int_hybrid"), ("head", "armor", "leather", "agi_int_hybrid"),
    ("hands", "armor", "mail", "agi_physical"), ("main_hand", "weapon", "polearm", "agi_physical"),
    ("back", "armor", "cloth", "int_caster"), ("main_hand", "weapon", "sword_1h", "str_physical"),
]

NOUN = {
    ("head", "cloth"): "Hood", ("head", "leather"): "Cowl", ("head", "mail"): "Coif", ("head", "plate"): "Helm",
    ("shoulder", "cloth"): "Mantle", ("shoulder", "leather"): "Shoulderpads", ("shoulder", "mail"): "Spaulders",
    ("shoulder", "plate"): "Pauldrons", ("chest", "cloth"): "Robe", ("chest", "leather"): "Jerkin",
    ("chest", "mail"): "Hauberk", ("chest", "plate"): "Breastplate", ("hands", "cloth"): "Gloves",
    ("hands", "leather"): "Grips", ("hands", "mail"): "Handguards", ("hands", "plate"): "Gauntlets",
    ("waist", "cloth"): "Sash", ("waist", "leather"): "Belt", ("waist", "mail"): "Girdle",
    ("waist", "plate"): "Waistguard", ("legs", "cloth"): "Leggings", ("legs", "leather"): "Breeches",
    ("legs", "mail"): "Legguards", ("legs", "plate"): "Legplates", ("feet", "cloth"): "Slippers",
    ("feet", "leather"): "Boots", ("feet", "mail"): "Treads", ("feet", "plate"): "Sabatons",
    ("wrist", "cloth"): "Cuffs", ("wrist", "leather"): "Bracers", ("wrist", "mail"): "Wristguards",
    ("wrist", "plate"): "Vambraces", ("back", "cloth"): "Cloak",
    "fist_weapon": "Knuckles", "wand": "Wand", "mace_1h": "Mace", "crossbow": "Crossbow", "tome": "Tome",
    "axe_2h": "Greataxe", "thrown": "Throwing Axes", "dagger": "Knife", "shield": "Shield", "polearm": "Halberd",
    "sword_1h": "Blade",
}

#: words that make a poor first word for a new name ("Seed of the First Grove" gives no "Seed Gloves")
STOP = {"the", "a", "an", "seed", "robes", "robe", "gloves", "boots", "band", "ring", "pendant", "amulet", "cloak",
        "staff", "sword", "blade", "helm", "hood", "mantle", "shield", "bow", "gun", "rifle", "dagger", "knife",
        "wand", "tome", "totem", "idol", "libram", "mace", "axe", "spear", "maul", "hammer", "belt", "girdle",
        "bracers", "vest", "jerkin", "tunic", "shawl", "sash", "kneecapper", "codex", "lantern", "charm",
        "talisman", "signet", "crown", "circlet", "barkskin", "fused", "scribe's", "ink-drinker",
        # single words that make a silly name on their own ("Monkey Hauberk", "Dead Helm")
        "monkey", "rat", "dead", "field", "spare", "hoof", "red", "black", "quiet", "racing", "digger", "burial",
        "scribe"}
#: words that read as a title rather than a name
TITLES = {"the", "sister", "brother", "old", "mother", "father", "widow", "factor", "keeper", "trader", "fence"}


def stems(vendor, items):
    out = []
    for d in items:
        words = d["name"].replace("'s ", "'s|").split()
        if " of " in d["name"] or len(words) < 2:
            continue
        w = words[0].split("|")[0]
        if w.lower().rstrip("'s") in {x.lower() for x in vendor["name"].split()}:
            continue                       # "Grisle's ..." is the seller's name, added below
        if w.lower() not in STOP and re.match(r"^[A-Z][A-Za-z'-]+$", w):
            out.append(w)
    # the seller's own name: the given name as theirs ("Velaren's Breastplate"), a surname or byname as a word
    # ("Skyhide Crossbow"); a seller called "The Something" has no name to lend
    parts = vendor["name"].split()
    if parts and parts[0].lower() != "the":
        for i, w in enumerate(parts):
            if w.lower() in TITLES or w.lower() in STOP or not re.match(r"^[A-Z][a-z][A-Za-z'-]+$", w) \
                    or len(w) <= 3 or w.endswith("'s"):
                continue
            out.append(w + ("'" if w.endswith("s") else "'s") if i == 0 else w)
    seen, uniq = set(), []
    for w in out:
        if w.lower() not in seen:
            seen.add(w.lower())
            uniq.append(w)
    return uniq


def every_item_name():
    names = set()

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("name"), str) and ("slot" in x or "armor_type" in x or "weapon_type" in x):
                names.add(x["name"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
    for f in list((ROOT / "data/items").glob("*.json")) + list((ROOT / "data/loot").glob("*.json")) \
            + list((ROOT / "data/quests").glob("*.json")):
        try:
            walk(json.loads(f.read_text(encoding="utf-8")))
        except ValueError:
            pass
    return names


def make_piece(gen, slot, kind, atype, template, ilvl):
    if kind == "armor":
        it = gen.generate_armor_piece(slot, atype, template, ilvl, "rare")
    else:
        it = gen.generate_weapon(slot, atype, template, ilvl, "rare", strict=True)
    if it is None:
        return None
    d = it.to_dict()
    # ON THE CURVE. LootGenerator spends a rare's budget as a plain sum, and the item curve reads it through a
    # norm, so a generated rare lands anywhere from a tenth of its level to double it (tools/fit_rares_to_curve.py).
    # Put each one on the line, after giving it its template's lead stat if it rolled none.
    from tools.fit_rares_to_curve import give_lead
    from entities.item_budget import fit_to_curve
    d["stat_template"] = template
    give_lead(d)
    fit_to_curve(d)
    return d


def main():
    check = "--check" in sys.argv
    udoc = json.loads(UNIQUES.read_text(encoding="utf-8"))
    items = udoc["items"]
    vdoc = json.loads(VENDORS.read_text(encoding="utf-8"))
    from tools.build_secrets import price as full_price
    from entities.loot_generator import LootGenerator
    gen = LootGenerator()

    # 1. the price
    cut = 0
    for uid, d in items.items():
        if "price_full" not in d:
            d["price_full"] = d.get("price") or full_price(d["item_level"], d.get("rarity", "rare"))
            d["price"] = int(round(d["price_full"] * PRICE_CUT))
            cut += 1

    # 2. the pools
    taken = every_item_name()
    plan_at = 0
    added, sellers, unnamed = 0, 0, []
    for v in vdoc["vendors"]:
        if not v.get("hidden") or v.get("barter"):
            continue
        mine = [s[len("unique:"):] for s in v["sells"] if s.startswith("unique:")]
        have = [items[u] for u in mine if u in items]
        if len(have) < 3 or len(have) >= POOL:
            continue
        sellers += 1
        ilvl = sorted(d["item_level"] for d in have)[len(have) // 2]
        had = {(d.get("slot"), d.get("armor_type") or d.get("weapon_type")) for d in have}
        words = stems(v, have)
        prefix = v["vendor_id"].replace("secret_", "")
        n_word = 0
        while len(have) < POOL:
            slot, kind, atype, template = PLAN[plan_at % len(PLAN)]
            plan_at += 1
            if (slot, atype) in had:
                continue
            noun = NOUN.get((slot, atype)) or NOUN.get(atype)
            name = None
            for k in range(len(words)):
                cand = f"{words[(n_word + k) % len(words)]} {noun}"
                if cand not in taken:
                    name = cand
                    n_word += k + 1
                    break
            if name is None:
                unnamed.append(f"{v['vendor_id']} {noun}")
                continue
            d = make_piece(gen, slot, kind, atype, template, ilvl)
            if d is None:
                continue
            uid = f"{prefix}_{re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')}"
            d["name"] = name
            d["item_id"] = uid
            d.pop("flavor_text", None)
            d["price_full"] = full_price(ilvl, "rare")
            d["price"] = int(round(d["price_full"] * PRICE_CUT))
            d["_source"] = "rotating stock, 17 Nov 2026 (tools/build_secret_rotation.py)"
            items[uid] = d
            v["sells"].insert(len(mine), f"unique:{uid}")
            mine.append(uid)
            have.append(d)
            had.add((slot, atype))
            taken.add(name)
            added += 1
            if not check:
                print(f"  + {name} ({slot}, {atype}, {template}, ilvl {ilvl})")

    spread = Counter(d.get("armor_type") or d.get("weapon_type") or d.get("slot") for d in items.values())
    print(f"{cut} prices cut to {int(PRICE_CUT * 100)}%; {added} new pieces across {sellers} hidden sellers "
          f"(pool of {POOL}, four on the shelf at a time)")
    print("  spread: " + ", ".join(f"{k} {n}" for k, n in spread.most_common()))
    if unnamed:
        print(f"  FAILED to name: {unnamed}")
        return 1
    if not check:
        UNIQUES.write_text(json.dumps(udoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        VENDORS.write_text(json.dumps(vdoc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
