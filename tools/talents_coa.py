"""
Talent data for the Conquest of Azeroth classes.

First entry is Stormbringer, sourced from Kyle's Stormbringer.docx export and
the in-client ability grid screenshots. The three specs are **Wind**,
**Maelstrom** and **Lightning** - note this corrects
COA_21_CLASS_RESOURCE_REFERENCE.md, which guessed "Lightning/Thunder/Winds"
from fan wikis before the client data was available.

Spec identities, taken from the in-game specialization descriptions:
  - Wind:      air magic, empowering allies, an Air Elemental companion that
               grows stronger the longer combat lasts.
  - Maelstrom: water + lightning; builds stacking debuffs then detonates them.
               Setup and payoff, rewarding players who manage stacks.
  - Lightning: pure speed. Builds and unleashes Static faster than any other
               spec, rapid casts with cooldown resets.

Because Stormbringer is a builder/spender, several talents here operate on
the Static economy itself (cheaper spenders, bigger builders) rather than
only on raw damage - that is the class's actual decision space.

Tuple format: (suffix, name, tier, column, max_points, effects, description)
See tools/talent_builder.py for the full effect-key reference.
"""

# ============================================================
# WIND - support, elemental companion, sustained scaling
# ============================================================
STORMBRINGER_WIND = [
    ("gift_of_air", "Gift of Air", 0, 0, 5,
     {"spell_power": 5},
     "Increases Spell Power by 5 per rank."),
    ("insulate", "Insulate", 0, 1, 3,
     {"magic_resistance": 8},
     "Increases Magic Resistance by 8 per rank."),
    ("improved_gale", "Improved Gale", 0, 2, 3,
     {"ability_stormbringer_gale_damage": 0.08},
     "Increases the damage of Gale by 8% per rank."),
    ("clear_skies", "Clear Skies", 0, 3, 2,
     {"hit_rating": 1.0},
     "Reduces your chance to miss with spells by 1% per rank."),

    ("comforting_winds", "Comforting Winds", 1, 0, 5,
     {"healing_done": 0.03},
     "Increases healing done by 3% per rank."),
    ("tailwind", "Tailwind", 1, 1, 5,
     {"haste": 2.0},
     "Increases Haste by 2% per rank."),
    ("battering_winds", "Battering Winds", 1, 2, 3,
     {"ability_stormbringer_aeroblast_damage": 0.10},
     "Increases the damage of Aeroblast by 10% per rank."),
    ("sturdy_as_the_storm", "Sturdy As The Storm", 1, 3, 3,
     {"armor": 12},
     "Increases Armor by 12 per rank."),

    ("invigorating_winds", "Invigorating Winds", 2, 0, 5,
     {"intellect": 3},
     "Increases Intellect by 3 per rank."),
    ("freewind", "Freewind", 2, 1, 3,
     {"ability_stormbringer_aeroblast_cost": 4},
     "Reduces the Static cost of Aeroblast by 4 per rank."),
    ("aeromancy", "Aeromancy", 2, 2, 3,
     {"spell_damage": 0.02},
     "Increases spell damage by 2% per rank."),
    ("haven", "Haven", 2, 3, 3,
     {"max_health_pct": 0.03},
     "Increases maximum Health by 3% per rank."),

    ("master_airbender", "Master Airbender", 3, 1, 1,
     {"spell_power": 25},
     "Mastery of the winds increases Spell Power by 25."),
    ("cloudsurfer", "Cloudsurfer", 3, 2, 5,
     {"crit_chance_spell": 1.0},
     "Increases spell critical strike chance by 1% per rank."),

    ("wicked_storms", "Wicked Storms", 4, 1, 3,
     {"ability_stormbringer_conjure_storm_damage": 0.08},
     "Increases the damage of Conjure Storm by 8% per rank."),
    ("unrelenting_winds", "Unrelenting Winds", 4, 2, 5,
     {"max_mana_pct": 0.03},
     "Increases maximum Mana by 3% per rank."),

    ("summon_air_elemental", "Summon: Air Elemental", 5, 1, 1,
     {"spell_damage": 0.05, "spell_power": 20},
     "Your bound Air Elemental lends its fury, increasing spell damage by 5% "
     "and Spell Power by 20."),
    ("aviana_blessing", "Aviana's Blessing", 5, 2, 3,
     {"spirit": 4},
     "Increases Spirit by 4 per rank."),

    ("master_elementalist", "Master Elementalist", 6, 2, 1,
     {"all_damage": 0.10},
     "Absolute command of air increases all damage you deal by 10%."),
]

# ============================================================
# MAELSTROM - stacking debuffs, setup and detonation
# ============================================================
STORMBRINGER_MAELSTROM = [
    ("conductive", "Conductive", 0, 0, 5,
     {"spell_power": 5},
     "Increases Spell Power by 5 per rank."),
    ("drown", "Drown", 0, 1, 3,
     {"ability_stormbringer_conjure_rainstorm_damage": 0.08},
     "Increases the damage of Conjure Rainstorm by 8% per rank."),
    ("undertow", "Undertow", 0, 2, 3,
     {"crit_chance_spell": 1.0},
     "Increases spell critical strike chance by 1% per rank."),
    ("orb_siphon", "Orb Siphon", 0, 3, 3,
     {"max_mana_pct": 0.02},
     "Increases maximum Mana by 2% per rank."),

    ("deluge", "Deluge", 1, 0, 5,
     {"spell_damage": 0.02},
     "Increases spell damage by 2% per rank."),
    ("flow_of_wrath", "Flow of Wrath", 1, 1, 5,
     {"haste": 2.0},
     "Increases Haste by 2% per rank."),
    ("amped_flow", "Amped Flow", 1, 2, 3,
     {"ability_stormbringer_volt_damage": 0.10},
     "Increases the damage of Volt by 10% per rank."),
    ("kinetic_energy", "Kinetic Energy", 1, 3, 3,
     {"magic_resistance": 8},
     "Increases Magic Resistance by 8 per rank."),

    ("stormflow", "Stormflow", 2, 0, 5,
     {"intellect": 3},
     "Increases Intellect by 3 per rank."),
    ("whirling_maelstrom", "Whirling Maelstrom", 2, 1, 3,
     {"ability_stormbringer_conjure_storm_cost": 4},
     "Reduces the Static cost of Conjure Storm by 4 per rank."),
    ("stormcloud", "Stormcloud", 2, 2, 3,
     {"spell_power": 8},
     "Increases Spell Power by 8 per rank."),
    ("residual_power", "Residual Power", 2, 3, 3,
     {"spirit": 3},
     "Increases Spirit by 3 per rank."),

    ("lethal_current", "Lethal Current", 3, 1, 1,
     {"spell_damage": 0.06},
     "Channeled current increases spell damage by 6%."),
    ("superconductor", "Superconductor", 3, 2, 5,
     {"crit_chance_spell": 1.0},
     "Increases spell critical strike chance by 1% per rank."),

    ("disciple_of_thorim", "Disciple of Thorim", 4, 1, 3,
     {"ability_stormbringer_electrocute_damage": 0.08},
     "Increases the damage of Electrocute by 8% per rank."),
    ("tempest_sovereign", "Tempest Sovereign", 4, 2, 5,
     {"stamina": 4},
     "Increases Stamina by 4 per rank."),

    ("prodigy_of_lei_shen", "Prodigy of Lei Shen", 5, 1, 1,
     {"spell_power": 30},
     "The storm lord's favour increases Spell Power by 30."),
    ("kiss_of_the_clouds", "Kiss of the Clouds", 5, 2, 3,
     {"healing_done": 0.04},
     "Increases healing done by 4% per rank."),

    ("thunder_ward", "Thunder Ward", 6, 2, 1,
     {"all_damage": 0.10},
     "The gathered maelstrom increases all damage you deal by 10%."),
]

# ============================================================
# LIGHTNING - raw speed, fastest Static generation
# ============================================================
STORMBRINGER_LIGHTNING = [
    ("electrical_charge", "Electrical Charge", 0, 0, 5,
     {"spell_power": 5},
     "Increases Spell Power by 5 per rank."),
    ("conductivity", "Conductivity", 0, 1, 3,
     {"ability_stormbringer_forked_lightning_cost": 3},
     "Reduces the Mana cost of Forked Lightning by 3 per rank."),
    ("flux_arc", "Flux Arc", 0, 2, 3,
     {"crit_chance_spell": 1.0},
     "Increases spell critical strike chance by 1% per rank."),
    ("static_lock", "Static Lock", 0, 3, 2,
     {"hit_rating": 1.0},
     "Reduces your chance to miss with spells by 1% per rank."),

    ("arc_lightning", "Arc Lightning", 1, 0, 5,
     {"ability_stormbringer_forked_lightning_damage": 0.08},
     "Increases the damage of Forked Lightning by 8% per rank."),
    ("electrifying_aura", "Electrifying Aura", 1, 1, 5,
     {"haste": 2.0},
     "Increases Haste by 2% per rank."),
    ("electrocutioner", "Electrocutioner", 1, 2, 3,
     {"ability_stormbringer_electrocute_damage": 0.10},
     "Increases the damage of Electrocute by 10% per rank."),
    ("magic_elimination", "Magic Elimination", 1, 3, 3,
     {"magic_resistance": 8},
     "Increases Magic Resistance by 8 per rank."),

    ("fluxcasting", "Fluxcasting", 2, 0, 5,
     {"intellect": 3},
     "Increases Intellect by 3 per rank."),
    ("storm_channeling", "Storm Channeling", 2, 1, 3,
     {"ability_stormbringer_electrocute_cooldown": 1},
     "Reduces the cooldown of Electrocute by 1 turn per rank."),
    ("invoking_storms", "Invoking Storms", 2, 2, 3,
     {"spell_damage": 0.02},
     "Increases spell damage by 2% per rank."),
    ("gathered_energy", "Gathered Energy", 2, 3, 3,
     {"max_mana_pct": 0.03},
     "Increases maximum Mana by 3% per rank."),

    ("master_of_lightning", "Master of Lightning", 3, 1, 1,
     {"spell_damage": 0.06},
     "Mastery of raw current increases spell damage by 6%."),
    ("crackling_devastation", "Crackling Devastation", 3, 2, 5,
     {"crit_chance_spell": 1.0},
     "Increases spell critical strike chance by 1% per rank."),

    ("ride_the_lightning", "Ride the Lightning", 4, 1, 3,
     {"ability_stormbringer_aeroblast_cost": 4},
     "Reduces the Static cost of Aeroblast by 4 per rank."),
    ("thunder_and_lightning", "Thunder and Lightning", 4, 2, 5,
     {"spell_power": 8},
     "Increases Spell Power by 8 per rank."),

    ("titanic_thunderbolt", "Titanic Thunderbolt", 5, 1, 1,
     {"crit_chance_spell": 5.0},
     "Increases spell critical strike chance by 5%."),
    ("unbound_lightning", "Unbound Lightning", 5, 2, 3,
     {"ability_stormbringer_volt_damage": 0.08},
     "Increases the damage of Volt by 8% per rank."),

    ("storm_ascendance", "Storm Ascendance", 6, 2, 1,
     {"all_damage": 0.10},
     "Ascend as a living storm, increasing all damage you deal by 10%."),
]

TREES = [
    ("stormbringer_wind", "Stormbringer Wind",
     "Masters of air magic, empowering allies and controlling the battlefield.",
     STORMBRINGER_WIND),
    ("stormbringer_maelstrom", "Stormbringer Maelstrom",
     "Combines water magic to supercharge lightning attacks.",
     STORMBRINGER_MAELSTROM),
    ("stormbringer_lightning", "Stormbringer Lightning",
     "Pure elemental fury, channeling raw electricity at blinding speed.",
     STORMBRINGER_LIGHTNING),
]
