#!/usr/bin/env python3
"""Hidden sellers, hidden caches and hidden paths (idempotent).

    PYTHONPATH=. python3 tools/build_secrets.py

Kyle, 14 Nov 2026: "Secret vendors... think of them like.... Grim Dawn hidden goodies!!!" and
"exploration is rewarded. Like pathways on maps that look like they can't be walked through, but
they can." See world/secrets.py for how a secret works at runtime.

Writes:
  data/world/secrets.json         every secret place (read by world/secrets.py)
  data/items/secret_uniques.json  the one-of-a-kind items hidden sellers carry ("unique:<id>")
  data/npcs/vendors.json          the hidden sellers themselves ("hidden": true, no map icon)

AUTHORED secrets are written out by hand below. Generated ones (glades cut into rock and trees,
islands with a ford, rooms in cave walls) come from data/world/secret_candidates.json, which
tools/find_secret_pockets.py writes.

Kyle asked not to be told where any of them are. Keep it that way in commit messages and replies:
counts, never places.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from build_durotar_content import make  # noqa: E402

UNIQUES_PATH = ROOT / "data/items/secret_uniques.json"
SECRETS_PATH = ROOT / "data/world/secrets.json"
VENDORS_PATH = ROOT / "data/npcs/vendors.json"


def price(ilvl, rarity):
    return int(ilvl * ilvl * (60 if rarity == "rare" else 140))


def unique(uid, name, slot, suffix, ilvl, flavor, rarity="rare", **kw):
    d = make(name, slot, suffix, ilvl, flavor, rarity=rarity, **kw)
    d["price"] = price(ilvl, rarity)
    return uid, d


# ---------------------------------------------------------------------------------------------
# AUTHORED
# ---------------------------------------------------------------------------------------------
#: Kyle, 14 Nov: "I do want 1 specifically in razor hill hidden behind a building so I can test
#: it. Let him sell a few potential rare weapons. Like lvl 9 to 12." Item levels 12-15 put the
#: required levels at 9-12.
RAZOR_HILL_UNIQUES = [
    unique("rh_quartermasters_mistake", "Quartermaster's Mistake", "main_hand", "of the Tiger", 12,
           "Logged as scrap. It isn't.", weapon_type="axe_1h"),
    unique("rh_sandpit_longbow", "Sandpit Longbow", "ranged", "of the Marksman", 13,
           "Strung with something that isn't sinew, and better for it.", weapon_type="bow"),
    unique("rh_gravel_tongue", "Gravel-Tongue", "ranged", "of Fiery Wrath", 13,
           "It mutters when it's warm. It's always warm.", weapon_type="wand"),
    unique("rh_thornjaw_maul", "Thornjaw Maul", "main_hand", "of the Bear", 14,
           "Somebody hammered raptor teeth into the head and never said why.", weapon_type="mace_2h"),
    unique("rh_ironbark_quarterstaff", "Ironbark Quarterstaff", "main_hand", "of the Owl", 14,
           "Cut from a tree that grew on the wrong side of the Barrens.", weapon_type="staff"),
    unique("rh_kneecapper", "Kneecapper", "main_hand", "of the Assassin", 15,
           "Short, ugly and very persuasive.", weapon_type="dagger"),
    unique("rh_barracks_door", "The Barracks Door", "off_hand", "of the Bulwark", 15,
           "Taken off its hinges one night. Nobody has noticed the draught.", weapon_type="shield"),
]

AUTHORED_VENDORS = [{
    "vendor_id": "secret_razorhill_fence",
    "name": "Rivet Nackle",
    "zone": "Razor Hill", "spot": (30, 10),
    "race": "goblin", "gender": "male", "appearance_variant": 3,
    "greeting": "Keep your voice down. The quartermaster thinks all of this went in the river. "
                "It didn't, and now it's yours, if your coin's good.",
    "uniques": RAZOR_HILL_UNIQUES,
    "supplies": ["healing_potion_minor", "sturdy_arrows"],
}]

#: The other hidden sellers. Each stands in a spot tools/find_secret_pockets.py found in its town,
#: behind a building if the town has one and in a hidden room if not. Two trades' worth of recipes
#: sold nowhere else, and three one-of-a-kind items at the town's level.
#:   (id, town, name, race, gender, greeting, [trades], [(item, slot, suffix, kind, type, flavor)])
SELLERS = [
    ("secret_brill_grisle", "Brill", "Mother Grisle", "forsaken", "female",
     "You found the back of the town hall. Most people never think to look behind anything. "
     "Buy something before you start telling people.",
     ["tailoring", "leatherworking"],
     [("Grisle's Stitched Mantle", "shoulder", "of the Owl", "armor", "cloth", "Stitched from three other mantles. You can see the seams if you look."),
      ("Embalmer's Scalpel", "main_hand", "of the Assassin", "weapon", "dagger", "Very sharp. Very clean. Mostly."),
      ("Bonepicker Gloves", "hands", "of the Monkey", "armor", "leather", "The fingertips are worn through from careful work.")]),
    ("secret_uc_edwin", "Undercity", "Quiet Edwin", "forsaken", "male",
     "I sell to people who know where to stand. You know where to stand. That's all the introduction we need.",
     ["engineering", "blacksmithing"],
     [("Sewer-Lantern Staff", "main_hand", "of the Sorcerer", "weapon", "staff", "The lantern still lights. Nobody has ever filled it."),
      ("Rat King's Buckler", "off_hand", "of the Bulwark", "weapon", "shield", "Gnawed round the rim, and none the weaker for it."),
      ("Drainwalker Boots", "feet", "of the Tiger", "armor", "leather", "They never quite dry out. They never quite need to.")]),
    ("secret_org_gashna", "Orgrimmar", "Gashna Two-Coins", "orc", "female",
     "The Warchief's quartermasters don't like what I sell, so I sell it here, quietly. "
     "You didn't see me and I didn't see you.",
     ["blacksmithing", "leatherworking"],
     [("Gashna's Spare Axe", "main_hand", "of the Champion", "weapon", "axe_2h", "She calls it her spare. Nobody has seen the first one."),
      ("Cleft-Shadow Hood", "head", "of the Bandit", "armor", "leather", "Smells of incense and bad decisions."),
      ("Hammer of Old Debts", "main_hand", "of the Squire", "weapon", "mace_1h", "Every dent is somebody who paid late.")]),
    ("secret_xroads_tazzle", "Crossroads", "Teeny Tazzle", "goblin", "male",
     "Customs, tariffs, inspections. I skip all of that and pass the savings on to you.",
     ["engineering", "jewelcrafting"],
     [("Tariff-Dodger's Boomstick", "ranged", "of the Marksman", "weapon", "gun", "Fires straight, mostly. Sounds expensive every time."),
      ("Bribe-Lined Vest", "chest", "of the Eagle", "armor", "mail", "There are coins sewn into the lining. Don't spend them."),
      ("Caravan Ledger", "off_hand", "of Intellect", "weapon", "tome", "Every column adds up to somebody else's loss.")]),
    ("secret_taurajo_brannoch", "Camp Taurajo", "Old Hoof Brannoch", "tauren", "male",
     "I carve what the trading post won't buy. Some of it's better than what they do sell.",
     ["woodworking", "leatherworking"],
     [("Plainsrunner Longbow", "ranged", "of the Hunt", "weapon", "bow", "Carved by hand, by somebody who has missed before and didn't like it."),
      ("Kodo-Hide Bracers", "wrist", "of the Bear", "armor", "mail", "Stiff for a month, then never again."),
      ("Brannoch's Walking Stick", "main_hand", "of the Elder", "weapon", "staff", "He says he doesn't need it any more. He's lying.")]),
    ("secret_ratchet_lissa", "Ratchet", "Lissa Undertow", "goblin", "female",
     "Salvage rights are a matter of who gets there first. I got there first.",
     ["engineering", "tailoring"],
     [("Wreck-Diver's Goggles", "head", "of the Falcon", "armor", "mail", "The left lens has a crack shaped like a shark."),
      ("Barnacled Cutlass", "main_hand", "of the Duelist", "weapon", "sword_1h", "Six weeks on the seabed and it still holds an edge."),
      ("Brine-Soaked Sash", "waist", "of the Prophet", "armor", "cloth", "Salt has worked into every thread. It hums at high tide.")]),
    ("secret_splinter_grokka", "Splintertree Post", "Grokka the Quiet", "orc", "male",
     "The lumber bosses think I quit. I didn't. I just moved round the back.",
     ["woodworking", "enchanting"],
     [("Felled Ancient's Branch", "main_hand", "of the Restorer", "weapon", "staff", "Cut from a tree that was older than the Horde. It hasn't forgiven anyone."),
      ("Splintered Warboard", "off_hand", "of the Defender", "weapon", "shield", "Made of the same planks as the palisade."),
      ("Sawdust Leggings", "legs", "of the Boar", "armor", "leather", "They never stop shedding.")]),
    ("secret_astranaar_sevalis", "Astranaar", "Sevalis Moonwhisper", "night_elf", "female",
     "The Sentinels would call this smuggling. I call it keeping old things in the right hands.",
     ["enchanting", "jewelcrafting"],
     [("Moonsilver Circlet", "head", "of the Seer", "armor", "cloth", "Cold even in sunlight."),
      ("Glaive of the Quiet Grove", "main_hand", "of the Tiger", "weapon", "sword_1h", "Older than Astranaar. Possibly older than the trees."),
      ("Owlfeather Cloak", "back", "of the Owl", "armor", None, "Every feather was given, not taken. She's sure of it.")]),
    ("secret_sepulcher_ashmund", "The Sepulcher", "Brother Ashmund", "forsaken", "male",
     "Grave goods. Everyone assumes they stay buried. I don't make that assumption.",
     ["leatherworking", "tailoring"],
     [("Ashmund's Burial Wraps", "chest", "of the Necromancer", "armor", "cloth", "Somebody was buried in these. They won't be needing them."),
      ("Gravewarden's Spade", "main_hand", "of Strength", "weapon", "polearm", "It digs. It also does the other thing."),
      ("Coffin-Nail Ring", "ring", "of Stamina", "armor", None, "Bent into a loop by somebody with very strong hands.")]),
    ("secret_tarrenmill_calloway", "Tarren Mill", "Widow Calloway", "forsaken", "female",
     "Mind the stairs. Nobody else uses them, which is the whole point of them.",
     ["tailoring", "blacksmithing"],
     [("Calloway's Mourning Veil", "head", "of the Invoker", "armor", "cloth", "Black lace, very fine, very old."),
      ("Millstone Crusher", "main_hand", "of the Bear", "weapon", "mace_2h", "Part of the old mill. The rest of it is still in the river."),
      ("Hillsbrad Harvest Gloves", "hands", "of the Physician", "armor", "leather", "Green-stained to the wrist.")]),
    ("secret_hammerfall_mog", "Hammerfall", "Mog Halfear", "orc", "male",
     "Arathi's full of things nobody's claimed. I claim them. Then I sell them.",
     ["blacksmithing", "leatherworking"],
     [("Stromgarde Trophy Blade", "main_hand", "of the Gladiator", "weapon", "sword_2h", "Pulled from a wall in Stromgarde. The wall didn't want to let go."),
      ("Ogre-Tooth Pauldrons", "shoulder", "of the Soldier", "armor", "mail", "The teeth are real. The ogre was not consulted."),
      ("Highland Stalker's Bow", "ranged", "of the Sharpshooter", "weapon", "bow", "Strung tight enough to hum in the wind.")]),
    ("secret_bootybay_vell", "Booty Bay", "Pocket Vell", "goblin", "female",
     "Everything in Booty Bay's for sale. The good stuff's just harder to find.",
     ["engineering", "jewelcrafting"],
     [("Smuggler's Hand Cannon", "ranged", "of the Marksman", "weapon", "gun", "Small enough to hide, loud enough to regret."),
      ("Revilgaz's Missing Ring", "ring", "of the Tiger", "armor", None, "The Baron says he never lost a ring. Vell says otherwise."),
      ("Bilge-Rat Jerkin", "chest", "of the Bandit", "armor", "leather", "Waterproof, smell-proof, conscience-proof.")]),
    ("secret_gromgol_zuni", "Grom'gol", "Zuni Hushfang", "troll", "female",
     "The jungle gives up its treasures to the patient. I'm patient. You pay.",
     ["leatherworking", "woodworking"],
     [("Hushfang's Fetish Staff", "main_hand", "of the Wellspring", "weapon", "staff", "The shrunken thing on top nods along when you talk."),
      ("Raptor-Scale Leggings", "legs", "of the Monkey", "armor", "leather", "Still warm. Don't ask."),
      ("Ziggurat Ward", "off_hand", "of the Warder", "weapon", "shield", "Carved stone, carried by somebody very strong once.")]),
    ("secret_freewind_talo", "Freewind Post", "Talo Skyhide", "tauren", "male",
     "The wind carries off a lot of things. I find where it puts them down.",
     ["leatherworking", "woodworking"],
     [("Windcaught Mantle", "shoulder", "of the Eagle", "armor", "mail", "Found on a spire nobody can climb. Talo won't say how."),
      ("Needlepoint Spear", "main_hand", "of the Spearhead", "weapon", "polearm", "Long enough to reach across a rope bridge, and he has."),
      ("Skyhide Wristwraps", "wrist", "of the Physician", "armor", "leather", "Soft as a cloud and about as warm.")]),
    ("secret_stw_fizzby", "Steamwheedle Port", "Fizzby Crankloot", "goblin", "male",
     "Off the books, off the docks, off the record. Take your pick.",
     ["engineering", "blacksmithing"],
     [("Crankloot's Overclocked Rifle", "ranged", "of the Sharpshooter", "weapon", "gun", "Runs hot. Runs very hot."),
      ("Gearbox Gauntlets", "hands", "of the Juggernaut", "armor", "plate", "Every knuckle is a cog."),
      ("Dune-Sealed Robes", "chest", "of the Prophet", "armor", "cloth", "Not one grain of sand gets in. Fizzby guarantees it.")]),
    ("secret_echo_zenji", "Echo Isles", "Mama Zenji", "troll", "female",
     "The spirits told me you'd come round the back. They don't usually bother telling me anything.",
     ["leatherworking", "tailoring"],
     [("Zenji's Bone Charm Staff", "main_hand", "of the Owl", "weapon", "staff", "Every bone on it belonged to somebody who owed her."),
      ("Tidecaller's Sandals", "feet", "of the Seer", "armor", "cloth", "Damp. Always damp."),
      ("Darkspear Throwing Glaive", "ranged", "of the Monkey", "weapon", "thrown", "It comes back. Usually.")]),
    ("secret_onyx_dagna", "Onyxhollow", "Dagna Coalbeard", "dwarf", "female",
     "My cousin runs the forge. I run what falls off the back of it.",
     ["blacksmithing", "jewelcrafting"],
     [("Fell-Off-the-Forge Warhammer", "main_hand", "of the Vanquisher", "weapon", "mace_2h", "It fell off the forge. Onto a cart. Which drove here."),
      ("Coalbeard's Heirloom Plate", "chest", "of the Bastion", "armor", "plate", "Three generations of Coalbeards wore it. Two survived."),
      ("Black Hollow Signet", "ring", "of the Champion", "armor", None, "Onyx, set in something darker.")]),
    ("secret_kael_lirael", "Kael's Bastion", "Lirael Sunstrand", "blood_elf", "female",
     "The Codex indexes everything. Almost everything. What it missed ended up with me, and I'd rather it stayed that way.",
     ["enchanting", "tailoring"],
     [("Unindexed Spellblade", "main_hand", "of Arcane Wrath", "weapon", "sword_1h", "There's no entry for it in any catalogue. She checked."),
      ("Marginalia Gloves", "hands", "of the Sorcerer", "armor", "cloth", "Ink-stained. The ink moves."),
      ("Sunstrand Pendant", "neck", "of Intellect", "armor", None, "Warm when somebody lies to you.")]),
]

FOUND = {
    "behind": ["Somebody's been hiding back here.", "There's more behind here than it looks.",
               "Nobody comes round this side. Somebody does."],
    "glade": ["There's a way through.", "This wall isn't a wall.", "You've found a way nobody marked.",
              "The rock gives way."],
    "island": ["Land, where the map shows only water.", "There's ground out here."],
}


def _level(zone, levels):
    band = levels.get(zone)
    return band[1] if band else 20


def _secret_recipes(seller_id, surname, trades, level):
    """Two recipes sold only by this seller: the best gear recipe of each trade near this level,
    made under the seller's name a step better than the common version."""
    from world.recipe_manager import _load_all_recipes
    allr = _load_all_recipes()
    want = level * 5
    out = []
    for trade in trades:
        pool = [(rid, r) for rid, (p, r) in allr.items() if p == trade and not r.get("secret")
                and (r.get("output") or {}).get("kind") in ("armor", "weapon")
                and r.get("skill_required", 0) <= max(25, want)]
        if not pool:
            continue
        rid, base = max(pool, key=lambda kv: (kv[1].get("skill_required", 0), kv[0]))
        new = json.loads(json.dumps(base))
        new["name"] = f"{surname}'s {base['name']}"
        new["source"] = "vendor"
        new["secret"] = True
        new["sold_by"] = [seller_id]
        o = new["output"]
        o["rarity"] = "epic" if o.get("rarity") == "rare" else "rare"
        o["item_level"] = int(o.get("item_level", level)) + 2
        out.append((trade, f"secret_{seller_id.split('_', 1)[1]}_{rid}", new))
    return out


#: Where each profession's recipes live, so a secret recipe goes in the file that profession reads.
FLAT = {"blacksmithing": "data/blacksmithing/recipes.json", "leatherworking": "data/leatherworking/recipes.json",
        "jewelcrafting": "data/jewelcrafting/recipes.json", "enchanting": "data/enchanting/recipes.json",
        "runecrafting": "data/runecrafting/recipes.json"}
NESTED = "data/crafting/recipes.json"


def _write_recipes(recipes):
    """Remove every old secret recipe, then add these. recipes: [(trade, id, recipe)]."""
    docs = {}
    for trade, path in FLAT.items():
        docs[path] = json.loads((ROOT / path).read_text(encoding="utf-8"))
        r = docs[path]["recipes"]
        for k in [k for k, v in r.items() if isinstance(v, dict) and v.get("secret")]:
            del r[k]
    nested = json.loads((ROOT / NESTED).read_text(encoding="utf-8"))
    for prof in nested["professions"].values():
        r = prof.get("recipes", {})
        for k in [k for k, v in r.items() if isinstance(v, dict) and v.get("secret")]:
            del r[k]
    for trade, rid, rec in recipes:
        if trade in FLAT:
            docs[FLAT[trade]]["recipes"][rid] = rec
        else:
            nested["professions"].setdefault(trade, {"recipes": {}})["recipes"][rid] = rec
    for path, doc in docs.items():
        (ROOT / path).write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (ROOT / NESTED).write_text(json.dumps(nested, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    levels = json.loads((ROOT / "data/zones/zone_levels.json").read_text(encoding="utf-8"))["zones"]
    cand_path = ROOT / "data/world/secret_candidates.json"
    cands = json.loads(cand_path.read_text(encoding="utf-8")) if cand_path.exists() else {}
    uniques, recipes, secrets = {}, [], []
    vendors_doc = json.loads(VENDORS_PATH.read_text(encoding="utf-8"))
    vendors = [v for v in vendors_doc["vendors"] if not v["vendor_id"].startswith("secret_")]
    from entities.consumable_manager import get_consumable_manager
    cm = get_consumable_manager()
    taken = {}      # zone -> spots used

    def add_vendor(vid, name, zone, spot, race, gender, greeting, stock, level, kind):
        zone_key = zone.lower().replace(" ", "_").replace("'", "")
        vendors.append({
            "vendor_id": vid, "name": name, "zone": zone_key, "x": spot[0], "y": spot[1],
            "tile_sprite": "npc", "sells": stock, "buys_from_player": True, "faction": "neutral",
            "gear_level": level, "sells_gear": False, "race": race, "gender": gender,
            "appearance_variant": 2, "greeting": greeting, "hidden": True})
        taken.setdefault(zone, []).append(tuple(spot))

    # the one Kyle asked for by name
    for v in AUTHORED_VENDORS:
        stock = []
        for uid, d in v["uniques"]:
            uniques[uid] = d
            stock.append(f"unique:{uid}")
        stock += [s for s in v.get("supplies", []) if cm.has_consumable(s)]
        add_vendor(v["vendor_id"], v["name"], v["zone"], v["spot"], v["race"], v["gender"],
                   v["greeting"], stock, 12, "behind")
        secrets.append({"id": v["vendor_id"], "zone": v["zone"], "kind": "behind", "passage": [],
                        "area": [list(v["spot"])], "mask": None, "cache": None,
                        "vendor": v["vendor_id"], "found_text": FOUND["behind"][0]})

    def use(zone, cand):
        spot = tuple(cand["spot"])
        if any(abs(spot[0] - t[0]) + abs(spot[1] - t[1]) < 12 for t in taken.get(zone, [])):
            return False
        return True

    # hidden sellers, each in its own town
    for (vid, zone, name, race, gender, greeting, trades, items) in SELLERS:
        opts = [c for c in cands.get(zone, []) if c["kind"] in ("behind", "glade") and use(zone, c)]
        opts.sort(key=lambda c: (c["kind"] != "behind", -c["depth"]))
        if not opts:
            print(f"  no hidden spot for {name} in {zone}")
            continue
        c = opts[0]
        level = _level(zone, levels)
        ilvl = level + 3
        stock = []
        for (iname, slot, suffix, kind, typ, flavor) in items:
            uid = vid.replace("secret_", "") + "_" + iname.lower().replace("'", "").replace(" ", "_").replace("-", "_")
            kw = {}
            if kind == "weapon":
                kw["weapon_type"] = typ
            elif typ:
                kw["armor_type"] = typ
            rarity = "epic" if level >= 45 else "rare"
            _, d = unique(uid, iname, slot, suffix, ilvl, flavor, rarity=rarity, **kw)
            uniques[uid] = d
            stock.append(f"unique:{uid}")
        surname = name.split()[-1] if " " in name else name
        for trade, rid, rec in _secret_recipes(vid, surname, trades, level):
            recipes.append((trade, rid, rec))
            stock.append(rid)
        add_vendor(vid, name, zone, c["spot"], race, gender, greeting, stock, level, c["kind"])
        secrets.append({"id": vid, "zone": zone, "kind": c["kind"], "passage": c["passage"],
                        "area": c["area"] if c["kind"] != "behind" else [c["spot"]],
                        "mask": c.get("mask"), "cache": None, "vendor": vid,
                        "found_text": FOUND[c["kind"]][len(secrets) % len(FOUND[c["kind"]])]})

    # caches everywhere else: up to three a map, one in a town
    n = 0
    for zone, cs in sorted(cands.items()):
        level = _level(zone, levels)
        # two a map, three on a big one; plenty, but each one still worth finding
        size = cs[0].get("map_area") or (max(c["spot"][0] for c in cs) * max(c["spot"][1] for c in cs))
        limit = 3 if size >= 30000 else 2
        placed = 0
        for c in sorted(cs, key=lambda c: (c["kind"] == "behind", -c["depth"])):
            if placed >= limit or not use(zone, c):
                continue
            n += 1
            sid = f"cache_{n:03d}"
            spot = list(c["spot"])
            secrets.append({"id": sid, "zone": zone, "kind": c["kind"], "passage": c["passage"],
                            "area": c["area"] if c["kind"] != "behind" else [spot],
                            "mask": c.get("mask"), "ground": c.get("ground"), "shallow": c.get("shallow"),
                            "cache": {"x": spot[0], "y": spot[1], "level": level}, "vendor": None,
                            "found_text": FOUND[c["kind"]][n % len(FOUND[c["kind"]])]})
            taken.setdefault(zone, []).append(tuple(spot))
            placed += 1

    _write_recipes(recipes)
    vendors_doc["vendors"] = vendors
    VENDORS_PATH.write_text(json.dumps(vendors_doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    UNIQUES_PATH.write_text(json.dumps({
        "_notes": "One-of-a-kind items carried by hidden sellers. Written by tools/build_secrets.py; "
                  "a seller lists one as \"unique:<id>\" (world/vendor_stock.make_unique).",
        "items": uniques}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    SECRETS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SECRETS_PATH.write_text(json.dumps({
        "_notes": "Hidden places. Written by tools/build_secrets.py, read by world/secrets.py. "
                  "Kyle asked not to be told where these are.",
        "secrets": secrets}, ensure_ascii=False) + "\n", encoding="utf-8")
    from collections import Counter
    kinds = Counter(s["kind"] for s in secrets)
    print(f"{len(secrets)} secrets ({dict(kinds)}): {sum(1 for v in vendors if v.get('hidden'))} hidden sellers, "
          f"{sum(1 for s in secrets if s.get('cache'))} caches, {len(uniques)} one-of-a-kind items, "
          f"{len(recipes)} secret recipes, across {len({s['zone'] for s in secrets})} maps")


if __name__ == "__main__":
    main()
