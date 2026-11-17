"""
Leatherworking's armor kits: Light, Medium and Thick. Kyle, 16 Nov 2026: "Armor kits dont work, I'm trying to use a light
armor kit and its not working."

They were made (data/leatherworking/recipes.json) and filed as upgrade kits, but the upgrade system only knows the
material kits (copper, linen, ashwood...), so nothing ever read them. Now they're what they are in classic WoW: an
enchantment you read onto chest, legs, hands or feet with the Enchant button, adding armor. Like any enchantment it
takes the item's one enchant slot, so it replaces whatever was there. Anyone can use one; no skill needed.

NUMBERS. Held to the same formula as every enchantment (tools/qa_enchanting.py): the kit's level (its recipe's skill
over five, plus one) x 0.36 x 1.3 x the group's share, at 0.2 points an armor point. A share of 0.5 gives 6, 19 and 36
armor, close to classic's 8, 16 and 32.

install() is idempotent and tools/build_enchanting.py calls it after it rewrites enchants.json.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENCH = ROOT / "data/enchanting/enchants.json"
MATS = ROOT / "data/gathering/materials.json"

GROUP = ("armor_kit", {"label": "Armor Kit", "share": 0.5})
#: id -> (title, tier, level, armor, description)
KITS = {
    "upgrade_kit_light_armor": ("Light Armor Kit", 0, 5, 6, "Stitched leather padding."),
    "upgrade_kit_medium_armor": ("Medium Armor Kit", 1, 16, 19, "Layered leather panels."),
    "upgrade_kit_thick_armor": ("Thick Armor Kit", 2, 31, 36, "Dense plates of thick leather riveted together."),
}
SLOTS = ("chest", "legs", "hands", "feet")


def install():
    d = json.loads(ENCH.read_text(encoding="utf-8"))
    d["groups"][GROUP[0]] = dict(GROUP[1])
    md = json.loads(MATS.read_text(encoding="utf-8"))
    for kid, (title, tier, level, armor, desc) in KITS.items():
        d["enchants"][kid] = {"name": title, "title": title, "group": "armor_kit", "family": "armor_kit",
                              "tier": tier, "rank": tier, "level": level, "skill": 1, "stats": {"armor": armor},
                              "hybrid": False}
        m = md["materials"].get(kid)
        if m is not None:
            m["description"] = (f"{desc} Adds {armor} armor to a chest, legs, gloves or boots. Read it on with the "
                                "Enchant button in your bags; it replaces any enchantment already there.")
    ENCH.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MATS.write_text(json.dumps(md, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return len(KITS)


if __name__ == "__main__":
    print(install(), "armor kits")
