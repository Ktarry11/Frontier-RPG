#!/usr/bin/env python3
"""Easter eggs: memes and nods hidden in the world's secrets. Idempotent.

    PYTHONPATH=. python3 tools/build_easter_eggs.py

Kyle, 20 Nov 2026: "Add new rules for secrets. We can have memes and Easter eggs. Like a secret where you find a goblin
sapper named 'Tiny Tina' and she's playing with a brick. She talks like tiny Tina and shows off the brick."

THE RULES (docs/secret_rules.md): an Easter egg lives inside a secret, so it's found the way every secret is, by
exploring; it's placed blind, like every secret, and this script prints counts only, never where. Each egg stands in a
secret that has no seller and no door yet, outside the hidden zones (world.hidden_zones.registry()), and its seller is
a hidden vendor (world/secrets.py) like any other. Its lines are our own words in the character's spirit, never quoted
from anywhere. Gear keeps Kyle's rule: rare, no flavour text (flavour is for epics and up).

THE EGGS
  Tiny Tina, a goblin sapper with a brick she's very fond of. Sells explosives at the level of wherever she's hiding,
  and Brick, a one-handed mace.
"""
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

SECRETS = ROOT / "data/world/secrets.json"
VENDORS = ROOT / "data/npcs/vendors.json"
UNIQUES = ROOT / "data/items/secret_uniques.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
CONS = ROOT / "data/consumables/consumable_types.json"

#: egg id -> the seller
EGGS = {
    "egg_tiny_tina": dict(
        name="Tiny Tina", race="goblin", gender="female", appearance_variant=4,
        greeting=("Ohhh, a visitor! Nobody finds Tina's hidey-hole unless they're super sneaky or super lost, and "
                  "either way that makes you my new best friend. This is Brick. Say hello to Brick. He doesn't talk "
                  "much, but he's the strongest friend I've ever had, and he's never once blown up on me, which is "
                  "more than I can say for the others. Wanna buy something that goes boom?"),
        seed=2011,
        unique=("egg_brick", "Brick", "main_hand", "of the Bear", dict(weapon_type="mace_1h")),
    ),
}


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def zone_level(levels, zone):
    from world.zone_keys import zone_key
    by_key = {zone_key(k): v for k, v in levels.items()}
    band = levels.get(zone) or by_key.get(zone_key(zone))
    return int(band[1]) if band else None


def bombs_for(level, cons):
    """The explosives nearest the egg's level: two at or under it, the strongest first."""
    rows = [(x.get("required_level") or 1, x["consumable_id"]) for x in cons["explosives"]]
    fit = sorted((r for r in rows if r[0] <= level + 2), reverse=True)
    return [cid for _lv, cid in fit[:3]]


def main():
    from world import hidden_zones
    from tools.build_secrets import unique, price
    hidden = set()
    try:
        hidden = {h.get("zone") if isinstance(h, dict) else h for h in hidden_zones.registry()}
    except Exception:
        hidden = set()
    doc, vd, ud = load(SECRETS), load(VENDORS), load(UNIQUES)
    levels, cons = load(LEVELS)["zones"], load(CONS)
    vby = {v["vendor_id"]: v for v in vd["vendors"]}
    placed = 0
    for vid, egg in EGGS.items():
        mine = next((s for s in doc["secrets"] if s.get("vendor") == vid), None)
        if mine is None:
            pool = [s for s in doc["secrets"] if not s.get("vendor") and not s.get("door") and s.get("area")
                    and s["zone"] not in hidden and zone_level(levels, s["zone"])
                    and 15 <= zone_level(levels, s["zone"]) <= 55]
            pool.sort(key=lambda s: s["id"])
            mine = random.Random(egg["seed"]).choice(pool)
            mine["vendor"] = vid
            placed += 1
        lvl = zone_level(levels, mine["zone"])
        tiles = [tuple(t[:2]) for t in mine["area"] if isinstance(t, (list, tuple))]
        x, y = random.Random(egg["seed"] + 1).choice(sorted(tiles))
        uid, name, slot, suffix, kw = egg["unique"]
        _id, item = unique(uid, name, slot, suffix, lvl + 3, "", **kw)
        item.pop("flavor_text", None)
        item["price_full"] = price(lvl + 3, "rare")
        item["price"] = int(item["price_full"] * 0.75)
        ud["items"][uid] = item
        from world.zone_keys import zone_key
        rec = vby.get(vid) or {"vendor_id": vid}
        rec.update(name=egg["name"], zone=zone_key(mine["zone"]), x=x, y=y, tile_sprite="npc",
                   buys_from_player=True, faction="neutral", gear_level=lvl, sells_gear=False, race=egg["race"],
                   gender=egg["gender"], appearance_variant=egg["appearance_variant"], greeting=egg["greeting"],
                   hidden=True, sells=[f"unique:{uid}"] + bombs_for(lvl, cons))
        if vid not in vby:
            vd["vendors"].append(rec)
    SECRETS.write_text(json.dumps(doc, ensure_ascii=False) + "\n", encoding="utf-8")
    VENDORS.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    UNIQUES.write_text(json.dumps(ud, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(EGGS)} Easter egg(s) in the world's secrets, {placed} newly placed (where is never printed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
