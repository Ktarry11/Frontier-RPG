"""
Gear style library (Kyle's correction, 2026-09-06): "broaden a bunch of
gear styles. Like caster plate, int mail, agi mail, int leather, spirit
leather, agi leather... build from there."

PROBLEM THIS FIXES: every hand-authored unique_item_def across 32
quests this session defaulted to exactly ONE stat lean per armor type -
cloth always got int_caster (int+spirit only), leather always got
agi_physical (agi+stamina only), mail always split str/agi, plate always
got str_physical. Zero spirit-leaning leather, zero int mail, zero
str+spirit plate, zero real hybrids anywhere. 22 hand-crafted items, the
exact same 5 stat shapes repeated.

WHY THIS IS SEPARATE FROM THE SUFFIX SYSTEM (Kyle's point): greens/blues
already get real stat variety through entities/loot_generator.py's
suffix roll (gear_suffixes.json) - that system was never the problem.
Hand-crafted quest/dungeon/raid rewards (unique_item_defs) don't touch
suffixes at all - their primary_stats are authored directly per item,
which is exactly where the repetition crept in. This library exists so
future hand-authoring pulls from real variety instead of muscle-memory
defaulting to "plate=str, leather=agi, cloth=int" every time.

DESIGN: covers every armor type crossed with every stat lean that makes
sense on it, matching Kyle's explicit examples plus filling out the
rest of the matrix. Not every combo is equally common in real WoW
(caster plate is rare - Paladins/Sun Clerics only), but the ENGINE
doesn't restrict armor type by stat lean at all (see entities/
proficiency.py's ARMOR_LADDER - it's a pure downgrade ladder, str/int/agi
mixing is never blocked), so nothing here is mechanically invalid.

Per Kyle's OG9-covers-CoA ruling: these presets are named/organized
around OG9 spec fantasy (the classic WoW comparisons he drew - Ret/Holy/
Prot Paladin, Balance/Feral/Resto Druid, etc.) since CoA classes already
map onto this gear via their own armor_type + primary stat lean (e.g.
Primalist = str/int hybrid, mail armor -> fits STR_MAIL or a hybrid mail
preset just as well as a "Ret Paladin"-flavored piece would).

Each preset is (primary_stats dict shape as WEIGHTS, not fixed numbers -
caller multiplies by an item-level-appropriate budget) plus a
suggested stat_template label for the UI and a short archetype name for
comment/reference purposes when hand-authoring.
"""

# armor_type -> list of (archetype_label, primary_stat_weights, stat_template_label)
# weights sum to roughly 1.0 (allocated across a level-appropriate stat
# budget by the caller) - NOT fixed point values, since items span many
# levels. stat_template_label is cosmetic/UI only (see world/quest.py -
# it's passed straight to Item(), nothing downstream gates on it).
GEAR_STYLES = {
    "cloth": [
        ("Caster (Int/Spirit)",   {"intellect": 0.7, "spirit": 0.3},                    "int_caster"),
        ("Healer (Spirit/Int)",   {"spirit": 0.55, "intellect": 0.35, "stamina": 0.1},   "spirit_healer"),
        ("Shadow (Int/Stamina)",  {"intellect": 0.6, "stamina": 0.4},                    "int_caster"),
        ("Battle-Mage (Int/Str)", {"intellect": 0.5, "strength": 0.3, "stamina": 0.2},   "str_int_hybrid"),
    ],
    "leather": [
        ("Feral/Melee (Agi/Sta)",  {"agility": 0.7, "stamina": 0.3},                     "agi_physical"),
        ("Caster Leather (Int)",   {"intellect": 0.65, "spirit": 0.25, "stamina": 0.1},  "int_caster"),
        ("Resto/Spirit Leather",   {"spirit": 0.5, "intellect": 0.3, "stamina": 0.2},    "spirit_healer"),
        ("Hybrid (Agi/Int)",       {"agility": 0.45, "intellect": 0.35, "stamina": 0.2}, "agi_int_hybrid"),
    ],
    "mail": [
        ("Enhancement (Agi/Str)",  {"agility": 0.5, "strength": 0.3, "stamina": 0.2},    "agi_physical"),
        ("Elemental (Int Mail)",   {"intellect": 0.65, "spirit": 0.2, "stamina": 0.15},  "int_caster"),
        ("Hunter/Ranged (Agi)",    {"agility": 0.65, "stamina": 0.35},                   "agi_physical"),
        ("Resto Mail (Spirit)",    {"spirit": 0.5, "intellect": 0.3, "stamina": 0.2},    "spirit_healer"),
        ("Hybrid (Agi/Int Mail)",  {"agility": 0.4, "intellect": 0.4, "stamina": 0.2},   "agi_int_hybrid"),
    ],
    "plate": [
        ("Fury/Arms (Str/Sta)",    {"strength": 0.65, "stamina": 0.35},                  "str_physical"),
        ("Protection (Sta/Str)",  {"stamina": 0.6, "strength": 0.4},                     "str_physical"),
        ("Retribution (Str/Sp)",  {"strength": 0.55, "spirit": 0.25, "stamina": 0.2},    "str_int_hybrid"),
        ("Holy/Caster Plate",     {"intellect": 0.5, "spirit": 0.3, "stamina": 0.2},     "str_int_hybrid"),
    ],
    "shield": [
        ("Tank (Sta)",             {"stamina": 0.7, "strength": 0.3},                    None),
        ("Spirit Shield (Healer)", {"stamina": 0.5, "spirit": 0.5},                      None),
    ],
    "accessory": [
        ("Strength/Stamina", {"strength": 0.5, "stamina": 0.5},   "str_physical"),
        ("Agility/Stamina",  {"agility": 0.5, "stamina": 0.5},    "agi_physical"),
        ("Intellect/Spirit", {"intellect": 0.5, "spirit": 0.5},   "int_caster"),
        ("Spirit/Stamina",   {"spirit": 0.5, "stamina": 0.5},     "spirit_healer"),
        ("Str/Int Hybrid",   {"strength": 0.4, "intellect": 0.4, "stamina": 0.2}, "str_int_hybrid"),
        ("Agi/Int Hybrid",   {"agility": 0.4, "intellect": 0.4, "stamina": 0.2},  "agi_int_hybrid"),
    ],
}


def roll_primary_stats(armor_type, style_index, budget):
    """Turn a (armor_type, style_index) pick + a total stat budget (int)
    into a real primary_stats dict, weights applied and rounded to whole
    numbers, minimum 1 per stat the style includes (never silently drops
    a stat the archetype is supposed to have - same "ceiling, not
    round-to-zero" principle used elsewhere for suffix rolls)."""
    styles = GEAR_STYLES.get(armor_type)
    if not styles:
        raise ValueError(f"No gear styles defined for armor_type={armor_type!r}")
    label, weights, template = styles[style_index]
    stats = {}
    for stat, weight in weights.items():
        stats[stat] = max(1, round(budget * weight))
    return label, stats, template
