#!/usr/bin/env python3
"""Extend the potion / food / meal / drink ladders out to level 55.

    PYTHONPATH=. python3 tools/extend_consumable_ladder.py [--check]

Kyle, 5 Nov 2026: "Yup, let's expand it out to lvl 55."

The vendor overhaul found this: 6 of 450 vendor/category pairs could not sell
anything appropriate, not because the vendor was wrong but because nothing
existed. Health and mana potions stopped at level 40, plain food at 25, and
meals and drinks at 38, so a level 48 shop in Glittervein had no choice but
to sell level 40 potions and level 25 stew.

The gaps in the MIDDLE were as bad as the missing top. Potions ran 1, 10, 25,
40 - fifteen level stretches where a player's potions never improved, which
is why so many vendors looked under-stocked even when correctly tiered.

New ladders, max gap 9 levels:

    potions   1, 10, 18, 25, 33, 40, 48, 55     (was 1, 10, 25, 40)
    food      1, 10, 25, 40, 55                 (was 1, 10, 25)
    meals     1, 10, 20, 30, 38, 46, 55         (was 1, 10, 20, 30, 38)
    drinks    1, 10, 20, 30, 38, 46, 55         (was 1, 10, 20, 30, 38)

NOTHING EXISTING IS RENUMBERED OR RETUNED. Only new entries are appended.
Save files and quest rewards reference consumable_id, and existing potions
are priced into the economy the player already knows - moving them would
rewrite the value of everything in everyone's bags to fix a gap at the top.

Effect values and prices are extrapolated from each ladder's own existing
curve rather than invented, so a new tier sits where the next one would have
if the ladder had simply continued. Fitted per category, since they do not
share a curve: potions scale roughly linearly in level while prices scale
geometrically.

Idempotent.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

CONSUMABLES = ROOT / "data/consumables/consumable_types.json"


def _interp(points, level):
    """Linear interpolation/extrapolation through (level, value) points."""
    points = sorted(points)
    if level <= points[0][0]:
        return float(points[0][1])
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if level <= x1:
            t = (level - x0) / float(x1 - x0)
            return y0 + (y1 - y0) * t
    # Past the top: continue the last segment's slope rather than flat-lining.
    (x0, y0), (x1, y1) = points[-2], points[-1]
    slope = (y1 - y0) / float(x1 - x0)
    return y1 + slope * (level - x1)


def _round_price(v):
    """Prices land on readable numbers - nobody charges 743 copper."""
    v = max(1, int(round(v)))
    if v >= 1000:
        return int(round(v / 100.0)) * 100
    if v >= 100:
        return int(round(v / 25.0)) * 25
    return int(round(v / 5.0)) * 5


#: (category, new_level, consumable_id, display name, description template).
NEW_TIERS = [
    ("health_potions", 18, "healing_potion_greater", "Greater Healing Potion",
     "Restores {eff} health."),
    ("health_potions", 33, "healing_potion_major", "Major Healing Potion",
     "Restores {eff} health."),
    ("health_potions", 48, "healing_potion_masterwork", "Masterwork Healing Potion",
     "Restores {eff} health."),
    ("health_potions", 55, "healing_potion_supreme", "Supreme Healing Potion",
     "Restores {eff} health."),
    ("mana_potions", 18, "mana_potion_greater", "Greater Mana Potion",
     "Restores {eff} mana."),
    ("mana_potions", 33, "mana_potion_major", "Major Mana Potion",
     "Restores {eff} mana."),
    ("mana_potions", 48, "mana_potion_masterwork", "Masterwork Mana Potion",
     "Restores {eff} mana."),
    ("mana_potions", 55, "mana_potion_supreme", "Supreme Mana Potion",
     "Restores {eff} mana."),
    ("meals", 46, "meal_saltback_roast", "Saltback Roast",
     "Salt-cured and slow-cooked. Restores {eff} health over {dur} seconds "
     "while you rest. Taking damage stops it."),
    ("meals", 55, "meal_ember_glazed_ribs", "Ember-Glazed Ribs",
     "Glazed over coals until the fat catches. Restores {eff} health over "
     "{dur} seconds while you rest. Taking damage stops it."),
    ("drinks", 46, "drink_deepwell_cordial", "Deepwell Cordial",
     "Cold enough to ache. Restores {eff} mana over {dur} seconds while you "
     "rest. Taking damage stops it."),
    ("drinks", 55, "drink_starfall_wine", "Starfall Wine",
     "Bottled the night the sky fell. Restores {eff} mana over {dur} seconds "
     "while you rest. Taking damage stops it."),
]

#: Plain food grants a stat buff rather than regen, so its new tiers carry
#: hand-set stat_bonuses continuing the existing progression (+10 STR / +7 STA
#: at 25) rather than an interpolated effect_value, which is always 0 here.
NEW_FOOD = [
    (40, "hunters_brace_platter", "Hunter's Brace Platter",
     "Heavy enough to walk off. Grants +15 Strength and +11 Stamina for 30 minutes.",
     {"strength": 15, "stamina": 11}),
    (55, "high_table_feast", "High Table Feast",
     "The kind of meal somebody else paid for. Grants +21 Strength and +16 Stamina "
     "for 30 minutes.",
     {"strength": 21, "stamina": 16}),
]


def main():
    check = "--check" in sys.argv
    doc = json.loads(CONSUMABLES.read_text(encoding="utf-8"))
    added = []

    for category, level, cid, name, desc in NEW_TIERS:
        rows = doc.get(category) or []
        if any(r.get("consumable_id") == cid for r in rows):
            continue
        template = rows[-1]
        eff_pts = [(r["required_level"], r["effect_value"]) for r in rows]
        price_pts = [(r["required_level"], r["vendor_price"]) for r in rows]
        dur_pts = [(r["required_level"], r.get("effect_duration", 0)) for r in rows]

        eff = int(round(_interp(eff_pts, level) / 10.0)) * 10
        dur = int(round(_interp(dur_pts, level))) if template.get("effect_duration") else 0
        price = _round_price(_interp(price_pts, level))

        entry = {
            "consumable_id": cid,
            "name": name,
            "consumable_type": template["consumable_type"],
            "description": desc.format(eff=eff, dur=dur),
            "effect_value": eff,
            "effect_duration": dur,
            "level_multiplier": template.get("level_multiplier", 0.0),
            "required_level": level,
            "cooldown_seconds": template.get("cooldown_seconds", 5),
            "stack_limit": template.get("stack_limit", 20),
            "vendor_price": price,
            "sell_price": max(1, price // 4),
            "buff_category": template.get("buff_category"),
        }
        rows.append(entry)
        rows.sort(key=lambda r: r["required_level"])
        doc[category] = rows
        added.append((category, level, cid, eff, price))

    rows = doc.get("food") or []
    for level, cid, name, desc, bonuses in NEW_FOOD:
        if any(r.get("consumable_id") == cid for r in rows):
            continue
        price_pts = [(r["required_level"], r["vendor_price"]) for r in rows
                     if r.get("buff_category") == "food" or r.get("stat_bonuses")]
        if not price_pts:
            price_pts = [(r["required_level"], r["vendor_price"]) for r in rows]
        price = _round_price(_interp(price_pts, level))
        rows.append({
            "consumable_id": cid,
            "name": name,
            "consumable_type": "food",
            "description": desc,
            "effect_value": 0,
            "effect_duration": 1800,
            "level_multiplier": 0.0,
            "required_level": level,
            "cooldown_seconds": 5,
            "stack_limit": 20,
            "vendor_price": price,
            "sell_price": max(1, price // 4),
            "buff_category": "food",
            "stat_bonuses": bonuses,
        })
        added.append(("food", level, cid, 0, price))
    rows.sort(key=lambda r: r["required_level"])
    doc["food"] = rows

    print(f"new consumable tiers: {len(added)}")
    for category, level, cid, eff, price in added:
        print(f"   {category:<15} lvl {level:<3} {cid:<28} eff {eff:<5} {price}c")

    print("\nladders now:")
    for category in ("health_potions", "mana_potions", "food", "meals", "drinks"):
        levels = sorted(r["required_level"] for r in doc.get(category, []))
        gaps = [b - a for a, b in zip(levels, levels[1:])]
        print(f"   {category:<15} {levels}   max gap {max(gaps) if gaps else 0}")

    if check:
        print("\n--check: nothing written")
        return 0
    CONSUMABLES.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {CONSUMABLES.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
