#!/usr/bin/env python3
"""The enchanting and recipe-scroll art plan: what goes in every cell of the seven sheets, and the prompts.

    PYTHONPATH=. python3 tools/enchant_recipe_art.py          # writes docs/enchanting_recipe_art_prompts.md

Kyle, 17 Nov 2026: "Can you give me like.... 36 x 4 things for enchanting???" and "another 36 x 3 for other
recipies found in the game?! They dont need to be unique but they should be similar.....like each professions get
about 6-8 unique ones".

ENCHANTING (4 sheets x 36 = 144). The 176 enchant scrolls all draw one picture today. Each enchant FAMILY (a slot and
a stat: Bracer Stamina, Boots Swiftness...) gets a LESSER scroll for its lower ranks and a GREATER scroll for its
upper ranks (the one-rank families, the weapon procs and the shoulder inscriptions, get one icon each): 130 icons.
The other 14 are the four enchanted wand materials (lesser and greater of a material share one) and the ten
enchanting oils, which borrow pack icons today.

RECIPE SCROLLS (3 sheets x 36 = 108). Today every recipe scroll is one picture per profession. Each profession gets
ten: five skill bands (apprentice to master) x found (a drop) or bought (a vendor's or a faction's), and the six that
craft epics get an eleventh for an epic recipe. Plus Timbermaw Warhide (the one crafted epic still borrowing an icon)
and a plain default scroll.

The same lists drive the slicer when the sheets come back, so a cell's number here is its file.
"""
import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------------------------------- enchanting
SLOT = {"bracer": "a bracer", "boots": "a boot", "gloves": "a gauntlet", "cloak": "a cloak", "chest": "a breastplate",
        "shield": "a round shield", "weapon": "a one-handed sword", "2h": "a two-handed greatsword",
        "armor_kit": "a leather armour patch"}
COLOUR = {
    "sta": "deep crimson red", "str": "burnt orange", "agi": "leaf green", "int": "royal blue",
    "spi": "pale silver-white", "mp5": "aqua cyan", "heal": "warm gold", "sp": "deep violet",
    "valor": "half crimson, half royal blue", "wild": "half leaf green, half royal blue",
    "devotion": "half burnt orange, half warm gold", "swift": "half leaf green, half crimson",
    "vigor": "half burnt orange, half crimson", "storm": "half leaf green, half violet, with a tiny lightning fork",
    "battlemage": "half burnt orange, half violet", "armor": "steel grey", "warding": "steel grey with a crimson rim",
    "stats": "five small colours in a ring (crimson, orange, green, blue, silver)",
    "sagacity": "half royal blue, half silver-white", "block": "bronze", "armor_kit": "steel grey",
}
STAT_NAME = {"sta": "Stamina", "str": "Strength", "agi": "Agility", "int": "Intellect", "spi": "Spirit",
             "mp5": "Mana Regeneration", "heal": "Healing", "sp": "Spell Power", "valor": "Valor",
             "wild": "Wildheart", "devotion": "Devotion", "swift": "Swiftness", "vigor": "Vigor",
             "storm": "Stormcaller", "battlemage": "Battlemage", "armor": "Protection", "warding": "Warding",
             "stats": "Stats", "sagacity": "Sagacity", "block": "Blocking", "armor_kit": "Armor Kit"}
#: the one-of-a-kind weapon procs and shoulder inscriptions: family -> what's on the scroll
SINGLE = {
    "fiery": "GREATER scroll, sword silhouette, bright orange flames curling up off the parchment",
    "bladesong": "GREATER scroll, sword silhouette, violet ribbons of light flowing round it like music",
    "spellblade": "GREATER scroll, an orange sword silhouette wreathed in violet runes",
    "lifestealing": "GREATER scroll, sword silhouette, black shadow tendrils drawing a thread of red light",
    "spellsurge": "GREATER scroll, a swirling spiral of bright blue mana rising from the rune circle",
    "battlemaster": "GREATER scroll, a gold sword silhouette with a soft green healing glow",
    "crusader": "GREATER scroll, a radiant white-gold starburst behind the sword silhouette, holy light",
    "secret": "GREATER scroll, a tiny living ember (a glowing coal with two bright eyes) curled on the open parchment",
    "argent_ap": "INSCRIPTION: a small silver medallion with gold trim and a sun emblem, a raised sword on it",
    "argent_sp": "INSCRIPTION: a small silver medallion with gold trim and a sun emblem, an open book with a star",
    "argent_heal": "INSCRIPTION: a small silver medallion with gold trim and a sun emblem, a chalice on it",
    "argent_tank": "INSCRIPTION: a small silver medallion with gold trim and a sun emblem, a tower shield on it",
    "pale_str_int": "INSCRIPTION: a bone-white medallion with a pale blue flame emblem, a hammer on it",
    "pale_agi_int": "INSCRIPTION: a bone-white medallion with a pale blue flame emblem, an arrow on it",
    "pale_sp": "INSCRIPTION: a bone-white medallion with a pale blue flame emblem, a small ember on it",
    "pale_str": "INSCRIPTION: a bone-white medallion with a pale blue flame emblem, a mailed fist on it",
}
WANDS = [("lesser_magic_wand", "an enchanted wand of plain pale wood tipped with a pale blue crystal"),
         ("lesser_mystic_wand", "an enchanted wand of carved wood tipped with a green crystal, vine carving"),
         ("lesser_nether_wand", "an enchanted wand of dark wood tipped with a violet crystal, faint smoke"),
         ("lesser_eternal_wand", "an enchanted wand of white-gold wood tipped with a radiant white gem")]
OILS = [("minor_wizard_oil", "a small plain vial of shimmering violet-blue oil"),
        ("lesser_wizard_oil", "a slightly larger vial of shimmering violet-blue oil, a twine tie"),
        ("wizard_oil", "a round flask of violet-blue oil sparkling with tiny stars"),
        ("brilliant_wizard_oil", "an ornate crystal flask of brilliant violet-blue oil, starry sparkles, silver collar"),
        ("minor_mana_oil", "a small plain vial of glowing aqua oil"),
        ("lesser_mana_oil", "a slightly larger vial of glowing aqua oil, a twine tie"),
        ("brilliant_mana_oil", "an ornate crystal flask of brilliant aqua oil, a silver collar, a soft glow"),
        ("battlemage_oil", "a squat flask of oil swirling orange and violet together"),
        ("superior_battlemage_oil", "an ornate flask of oil swirling orange and violet, a gold collar, glowing"),
        ("oil_of_devotion", "a slim flask of warm golden oil with a tiny sun charm on the neck, glowing gently")]
GROUP_ORDER = [["bracer", "boots", "wands"], ["gloves", "chest", "cloak", "armor_kit"], ["weapon", "shoulder"],
               ["shield", "2h", "oils"]]


def enchant_families():
    e = json.loads((ROOT / "data/enchanting/enchants.json").read_text(encoding="utf-8"))["enchants"]
    fam = collections.OrderedDict()
    for eid, v in e.items():
        fam.setdefault((v["group"], v["family"]), []).append((v["rank"], eid))
    return {k: [eid for _r, eid in sorted(v)] for k, v in fam.items()}


def enchant_cells():
    """[(sheet, [(stem, description, [enchant or item ids it draws])])] in reading order."""
    fam = enchant_families()
    sheets = []
    for groups in GROUP_ORDER:
        cells = []
        for g in groups:
            if g == "wands":
                for stem, d in WANDS:
                    cells.append((f"ench_{stem}", d.upper()[:1] + d[1:], [stem, stem.replace("lesser", "greater")]))
                continue
            if g == "oils":
                for stem, d in OILS:
                    cells.append((stem, d[0].upper() + d[1:], [stem]))
                continue
            for (gg, f), ids in fam.items():
                if gg != g:
                    continue
                if f in SINGLE:
                    cells.append((f"enchant_scroll_{g}_{f}", SINGLE[f], ids))
                    continue
                half = (len(ids) + 1) // 2
                for look, part in (("lesser", ids[:half]), ("greater", ids[half:])):
                    if not part:
                        continue
                    label = STAT_NAME[f].upper() if g == "armor_kit" else f"{g.upper()} {STAT_NAME[f].upper()}"
                    cells.append((f"enchant_scroll_{g}_{f}_{look}",
                                  f"{look.upper()} scroll, {SLOT[g]} silhouette, glowing {COLOUR[f]} [{label}]", part))
        sheets.append(cells)
    return sheets


# ---------------------------------------------------------------------------------------------------- recipes
PROFS = [
    ("blacksmithing", "BLACKSMITHING PLANS", "a rolled sheet of grey-blue parchment with an anvil drawn on it and a "
                                             "small smith's hammer laid across it"),
    ("leatherworking", "LEATHERWORKING PATTERN", "a sheet of tanned leather with stitched edges and an armour outline "
                                                 "drawn on it, a bone needle pushed through"),
    ("tailoring", "TAILORING PATTERN", "a folded cloth-paper sewing pattern with a dotted outline, a sewing pin and "
                                       "a small spool of thread"),
    ("woodworking", "WOODWORKING SCHEMATIC", "a thin wooden board with a bow and staff outline burned into it, a "
                                             "small chisel beside it"),
    ("engineering", "ENGINEERING SCHEMATIC", "a blueprint sheet of blue paper with white lines drawing a cog, a small "
                                             "brass gear pinned to it"),
    ("jewelcrafting", "JEWELCRAFTING DESIGN", "a stiff card on dark velvet with a cut gem drawn on it, a tiny real "
                                              "gem pinned at the corner"),
    ("alchemy", "ALCHEMY RECIPE", "a curled parchment with a flask drawn on it, a potion drip stain and a tiny cork"),
    ("cooking", "COOKING RECIPE", "a recipe card with a cooking pot drawn on it, a small wooden spoon and a grease "
                                  "stain"),
    ("enchanting", "ENCHANTING FORMULA", "a parchment with a faintly glowing rune circle drawn on it and a small "
                                         "runed rod"),
    ("runecrafting", "RUNECRAFTING RUNE SCRIPT", "a small slate tablet carved with runes that glow faintly, a stub "
                                                 "of chalk"),
]
EPIC_PROFS = {"blacksmithing", "leatherworking", "tailoring", "woodworking", "engineering", "jewelcrafting"}
BANDS = [("apprentice", "plain and simple"),
         ("journeyman", "clean, with a bronze clasp"),
         ("expert", "crisp, with silver fittings"),
         ("artisan", "fine, with gold fittings and a faint glow"),
         ("master", "grand, with gold and gem fittings and a clear glow")]
VARIANT = {"found": "a little torn and dirt-stained at one edge", "bought": "tied with a blue ribbon and a red wax seal"}
EXTRAS = [
    ("gear_epic_crafted_timbermaw_warhide",
     "[TIMBERMAW WARHIDE, an epic leather chestpiece, not a recipe] A heavy furbolg-made leather chest of dark brown "
     "hide with honey-gold stitching, carved wooden toggles and a trim of bear claws, a faint warm golden glow"),
    ("recipe_default", "[PLAIN RECIPE SCROLL] A plain rolled parchment scroll tied with string, nothing drawn on it"),
]


def recipe_cells():
    cells = []
    for prof, title, obj in PROFS:
        for variant in ("found", "bought"):
            for i, (band, look) in enumerate(BANDS, 1):
                cells.append((f"recipe_{prof}_{i}_{variant}",
                              f"[{title}, {band.upper()}, {variant.upper()}] {obj[0].upper() + obj[1:]}; {look}; {VARIANT[variant]}"))
        if prof in EPIC_PROFS:
            cells.append((f"recipe_{prof}_epic",
                          f"[{title}, EPIC] {obj[0].upper() + obj[1:]}, but on black parchment with gold ink, gold "
                          f"fittings and a purple glow"))
    cells.extend(EXTRAS)
    return [cells[i:i + 36] for i in range(0, len(cells), 36)]


# ---------------------------------------------------------------------------------------------------- the doc
STYLE = ("Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell "
         "with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly "
         "semi-realistic WoW Classic inventory-icon style: strong readable silhouette, soft dark outline, chunky "
         "simple shapes, soft lighting from the top-left, a slight 3/4 view. No hands, no text, no letters, no "
         "numbers, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon.")
ENCH_RULES = ("THE SCROLLS: every SCROLL is the same object, so they read as one family. A LESSER scroll is a small "
              "rolled parchment scroll, half unrolled, tied with plain twine; on its open part a rune circle glows "
              "softly in the colour named, and inside the circle is a small silhouette of the item named (a bracer, "
              "a boot, a gauntlet...). A GREATER scroll is the same idea grander: thick vellum on dark wooden rollers "
              "with gold caps and a wax seal, its rune circle blazing in the colour named, small sparks rising. Where "
              "a colour is 'half X, half Y', the rune circle is split down the middle in those two colours. An "
              "INSCRIPTION is a small engraved medallion instead of a scroll. Wands and oils are as described.")
RECIPE_RULES = ("THE RECIPES: each profession has ONE object, described in its cells, and every one of its cells is "
                "that same object at a different grade. The five grades climb: APPRENTICE plain and simple, "
                "JOURNEYMAN clean with bronze, EXPERT crisp with silver, ARTISAN fine with gold and a faint glow, "
                "MASTER grand with gold and gems and a clear glow. FOUND ones are a little torn and dirt-stained; "
                "BOUGHT ones are tied with a blue ribbon and a red wax seal. EPIC ones are the same object on black "
                "parchment with gold ink and a purple glow.")


def prompt(cells, rules, what):
    lines = [f"Generate ONE sprite sheet image, 1024x1024, a 6 columns x 6 rows grid = 36 separate {what} icons "
             f"(each cell about 170x170). {STYLE} Words in square brackets are notes for you: never draw them.", "", rules, "", "Row by row, left to right:"]
    for i, cell in enumerate(cells, 1):
        if (i - 1) % 6 == 0:
            lines.append(f"\nRow {(i - 1) // 6 + 1}:")
        lines.append(f"{i}. {cell[1]}")
    return "\n".join(lines)


def main():
    ench, rec = enchant_cells(), recipe_cells()
    assert [len(s) for s in ench] == [36] * 4, [len(s) for s in ench]
    assert [len(s) for s in rec] == [36] * 3, [len(s) for s in rec]
    out = ["# Enchanting and recipe-scroll art (7 sheets, 252 icons)", "",
           "Kyle, 17 Nov 2026: \"Can you give me like.... 36 x 4 things for enchanting???\" and \"another 36 x 3 for "
           "other recipies found in the game?! They dont need to be unique but they should be similar.....like each "
           "professions get about 6-8 unique ones\".", "",
           "**Enchanting (sheets EN1-EN4, 144 icons).** Today all 176 enchant scrolls are one picture. Each enchant "
           "family (a slot and a stat, like Bracer Stamina) gets a lesser scroll for its lower ranks and a greater "
           "scroll for its upper ranks; the weapon procs and shoulder inscriptions get one each. That's 130. The "
           "other 14 are the four enchanted wands and the ten enchanting oils.", "",
           "**Recipe scrolls (sheets RC1-RC3, 108 icons).** Today each profession's scrolls are one picture. Each "
           "profession gets ten: five skill grades, found (a drop) or bought (a vendor's or a faction's). The six "
           "that craft epics get an epic one too. Last come Timbermaw Warhide (the one crafted epic still borrowing "
           "an icon) and a plain default scroll. A profession runs across a sheet break in a few places; every cell "
           "describes itself, so that's fine.", "",
           "Send each sheet back and I'll slice it in by cell number (tools/enchant_recipe_art.py holds the lists).",
           ""]
    for i, cells in enumerate(ench, 1):
        out += [f"## Sheet EN{i}", "", "```", prompt(cells, ENCH_RULES, "enchanting"), "```", ""]
    for i, cells in enumerate(rec, 1):
        out += [f"## Sheet RC{i}", "", "```", prompt(cells, RECIPE_RULES, "recipe scroll"), "```", ""]
    p = ROOT / "docs/enchanting_recipe_art_prompts.md"
    p.write_text("\n".join(out), encoding="utf-8")
    print(f"{p.relative_to(ROOT)}: {sum(map(len, ench))} enchanting + {sum(map(len, rec))} recipe cells")


if __name__ == "__main__":
    main()
