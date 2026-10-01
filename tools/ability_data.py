"""
Ability kit data for the 9 original WoW classes.

Each class gets ~8 abilities: an auto-attack, a signature spammable, and a
mix of DoTs, cooldowns, heals, buffs and debuffs appropriate to the class.

Tuple format:
    (ability_id_suffix, name, resource, num_ranks, level_learned,
     cost_start, cost_step, effect_start, effect_step,
     cooldown, effect_type, duration, stat_mods, description)

  resource      "rage" | "energy" | "mana"
  num_ranks     1-5; ranks landing past level 60 are dropped automatically
  cost_step     ignored for rage/energy (flat cost across ranks, WoW-correct)
  effect_type   damage | spell_damage | heal | dot | spell_dot | hot
                | buff | debuff
  duration      turns, for dot/hot/buff/debuff only
  stat_mods     base magnitude for buff/debuff; scaled per rank by
                effect_value treated as a percentage (100 = full value)

DoT/HoT effect_start is TOTAL damage/healing across the full duration, not
per turn - see Ability._apply_effect().

Talent JSON references these ability_ids, so renaming one means updating
tools/talents_*.py to match. tools/generate_talents.py will fail loudly if
they ever drift apart.
"""

# ============================================================
# WARRIOR - Plate, Strength, Rage
# ============================================================
WARRIOR = [
    ("attack", "Attack", "rage", 1, 1, 0, 0, 50, 0, 0, "damage", 0, None,
     "A basic melee attack."),
    ("heroic_strike", "Heroic Strike", "rage", 5, 1, 20, 0, 70, 35, 0, "damage", 0, None,
     "A powerful melee strike that deals additional damage."),
    ("rend", "Rend", "rage", 4, 1, 10, 0, 60, 45, 2, "dot", 3, None,
     "Wounds the target, causing bleed damage over 3 turns."),
    ("thunder_clap", "Thunder Clap", "rage", 3, 20, 20, 0, 45, 25, 1, "damage", 0, None,
     "Blasts nearby enemies with a concussive shockwave."),
    ("battle_shout", "Battle Shout", "rage", 4, 6, 10, 0, 100, 0, 4, "buff", 4,
     {"attack_power": 30},
     "A rallying cry that increases your Attack Power for 4 turns."),
    ("overpower", "Overpower", "rage", 4, 10, 5, 0, 90, 45, 3, "damage", 0, None,
     "Exploits an opening, striking with unavoidable force."),
    ("demoralizing_shout", "Demoralizing Shout", "rage", 3, 14, 10, 0, 100, 0, 3, "debuff", 3,
     {"attack_power": -35},
     "Reduces the enemy's Attack Power for 3 turns."),
    ("mortal_strike", "Mortal Strike", "rage", 4, 30, 30, 0, 160, 70, 2, "damage", 0, None,
     "A vicious strike that deals heavy weapon damage."),
    ("execute", "Execute", "rage", 3, 38, 15, 0, 220, 90, 3, "damage", 0, None,
     "Attempts to finish off a wounded foe with devastating force."),
]

# ============================================================
# ROGUE - Leather, Agility, Energy
# ============================================================
ROGUE = [
    ("attack", "Attack", "energy", 1, 1, 0, 0, 45, 0, 0, "damage", 0, None,
     "A basic melee attack."),
    ("sinister_strike", "Sinister Strike", "energy", 5, 1, 40, 0, 65, 32, 0, "damage", 0, None,
     "A vicious strike with your main hand weapon."),
    ("backstab", "Backstab", "energy", 5, 1, 60, 0, 95, 45, 2, "damage", 0, None,
     "Drives a dagger into the target's back for heavy damage."),
    ("eviscerate", "Eviscerate", "energy", 5, 8, 35, 0, 120, 55, 2, "damage", 0, None,
     "A brutal finishing move that tears into the target."),
    ("rupture", "Rupture", "energy", 4, 12, 25, 0, 110, 70, 3, "dot", 4,
     None, "Tears open the target, causing bleed damage over 4 turns."),
    ("evasion", "Evasion", "energy", 3, 16, 20, 0, 100, 0, 5, "buff", 3,
     {"dodge": 25, "parry": 10},
     "Heightened reflexes greatly increase Dodge and Parry for 3 turns."),
    ("expose_armor", "Expose Armor", "energy", 3, 22, 25, 0, 100, 0, 3, "debuff", 3,
     {"armor": -120},
     "Exposes a weak spot, reducing the enemy's Armor for 3 turns."),
    ("adrenaline_rush", "Adrenaline Rush", "energy", 2, 32, 0, 0, 100, 0, 6, "buff", 3,
     {"attack_power": 45, "haste": 15},
     "Floods you with adrenaline, boosting Attack Power and Haste."),
]

# ============================================================
# HUNTER - Mail, Agility, Mana
# ============================================================
HUNTER = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 45, 0, 0, "damage", 0, None,
     "A basic ranged attack."),
    ("steady_shot", "Steady Shot", "mana", 5, 1, 20, 10, 70, 34, 0, "damage", 0, None,
     "A steady, well-aimed shot."),
    ("multi_shot", "Multi-Shot", "mana", 4, 6, 35, 18, 90, 42, 2, "damage", 0, None,
     "Fires several shots in rapid succession."),
    ("aimed_shot", "Aimed Shot", "mana", 5, 10, 40, 22, 130, 58, 3, "damage", 0, None,
     "A carefully aimed shot that deals heavy damage."),
    ("serpent_sting", "Serpent Sting", "mana", 4, 4, 25, 14, 100, 65, 2, "spell_dot", 4,
     None, "Poisons the target, dealing nature damage over 4 turns."),
    ("hunters_mark", "Hunter's Mark", "mana", 3, 8, 20, 10, 100, 0, 3, "debuff", 4,
     {"armor": -90, "dodge": -8},
     "Marks the target, reducing its Armor and Dodge for 4 turns."),
    ("aspect_of_the_hawk", "Aspect of the Hawk", "mana", 4, 12, 30, 15, 100, 0, 4, "buff", 4,
     {"attack_power": 40, "haste": 8},
     "Assumes the Hawk's aspect, increasing Attack Power and Haste."),
    ("explosive_trap", "Explosive Trap", "mana", 3, 26, 45, 24, 120, 60, 3, "spell_dot", 3,
     None, "Sets a fire trap that burns the target over 3 turns."),
]

# ============================================================
# MAGE - Cloth, Intellect, Mana
# ============================================================
MAGE = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 30, 0, 0, "damage", 0, None,
     "A weak melee strike. You are a Mage - use your spells."),
    ("fireball", "Fireball", "mana", 5, 1, 30, 18, 80, 40, 0, "spell_damage", 0, None,
     "Hurls a fiery ball that burns the target."),
    ("frostbolt", "Frostbolt", "mana", 5, 1, 25, 15, 70, 36, 0, "spell_damage", 0, None,
     "Launches a bolt of frost, chilling the target."),
    ("arcane_explosion", "Arcane Explosion", "mana", 4, 8, 45, 24, 95, 45, 2, "spell_damage", 0, None,
     "Detonates arcane energy around you."),
    ("living_flame", "Living Flame", "mana", 4, 6, 30, 16, 105, 68, 2, "spell_dot", 4,
     None, "Sets the target ablaze, burning them over 4 turns."),
    ("arcane_intellect", "Arcane Intellect", "mana", 4, 10, 40, 20, 100, 0, 5, "buff", 5,
     {"intellect": 12, "spell_power": 25},
     "Sharpens the mind, increasing Intellect and Spell Power."),
    ("frost_nova", "Frost Nova", "mana", 3, 14, 35, 18, 100, 0, 3, "debuff", 3,
     {"haste": -20, "dodge": -10},
     "Freezes the target in place, slowing it for 3 turns."),
    ("pyroblast", "Pyroblast", "mana", 4, 24, 60, 32, 190, 85, 3, "spell_damage", 0, None,
     "A massive fiery boulder that deals devastating damage."),
    ("ice_barrier", "Ice Barrier", "mana", 3, 30, 50, 26, 100, 0, 5, "buff", 4,
     {"armor": 150, "magic_resistance": 60},
     "Surrounds you with ice, absorbing incoming damage."),
]

# ============================================================
# WARLOCK - Cloth, Intellect, Mana
# ============================================================
WARLOCK = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 30, 0, 0, "damage", 0, None,
     "A weak melee strike. Your power lies in shadow."),
    ("shadow_bolt", "Shadow Bolt", "mana", 5, 1, 30, 18, 78, 39, 0, "spell_damage", 0, None,
     "Sends a bolt of dark magic at the target."),
    ("corruption", "Corruption", "mana", 5, 1, 25, 14, 95, 60, 0, "spell_dot", 4,
     None, "Corrupts the target, dealing shadow damage over 4 turns."),
    ("immolate", "Immolate", "mana", 5, 4, 30, 16, 110, 65, 2, "spell_dot", 3,
     None, "Engulfs the target in flame, burning them over 3 turns."),
    ("curse_of_weakness", "Curse of Weakness", "mana", 4, 8, 25, 12, 100, 0, 3, "debuff", 4,
     {"attack_power": -40},
     "Curses the target, reducing its Attack Power for 4 turns."),
    ("drain_life", "Drain Life", "mana", 4, 10, 40, 20, 90, 48, 2, "spell_damage", 0, None,
     "Siphons the target's life force into raw shadow damage."),
    ("demon_armor", "Demon Armor", "mana", 4, 12, 45, 22, 100, 0, 5, "buff", 5,
     {"armor": 120, "stamina": 10},
     "Demonic wards increase your Armor and Stamina."),
    ("unstable_affliction", "Unstable Affliction", "mana", 4, 26, 50, 26, 165, 90, 3, "spell_dot", 3,
     None, "Volatile shadow magic that ravages the target over 3 turns."),
    ("shadowburn", "Shadowburn", "mana", 3, 32, 55, 28, 195, 88, 3, "spell_damage", 0, None,
     "Blasts the target with a burst of pure shadow."),
]

# ============================================================
# PRIEST - Cloth, Intellect/Spirit, Mana
# ============================================================
PRIEST = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 30, 0, 0, "damage", 0, None,
     "A weak melee strike. The Light is your weapon."),
    ("smite", "Smite", "mana", 5, 1, 25, 15, 72, 36, 0, "spell_damage", 0, None,
     "Smites the target with holy energy."),
    ("heal", "Heal", "mana", 5, 1, 40, 24, 120, 62, 1, "heal", 0, None,
     "Heals your wounds with the Light."),
    ("shadow_word_pain", "Shadow Word: Pain", "mana", 5, 1, 28, 15, 92, 58, 0, "spell_dot", 4,
     None, "Words of agony that torment the target over 4 turns."),
    ("renew", "Renew", "mana", 4, 6, 35, 18, 130, 70, 2, "hot", 4, None,
     "Heals you steadily over 4 turns."),
    ("power_word_fortitude", "Power Word: Fortitude", "mana", 4, 8, 40, 20, 100, 0, 5, "buff", 5,
     {"stamina": 14, "max_health_pct": 0},
     "Fortifies the spirit, increasing Stamina."),
    ("mind_blast", "Mind Blast", "mana", 5, 10, 45, 24, 125, 56, 2, "spell_damage", 0, None,
     "Assaults the target's mind with shadow energy."),
    ("power_word_shield", "Power Word: Shield", "mana", 4, 14, 45, 24, 100, 0, 4, "buff", 3,
     {"armor": 140, "magic_resistance": 50},
     "A shield of Light absorbs incoming damage for 3 turns."),
    ("holy_fire", "Holy Fire", "mana", 4, 22, 50, 26, 150, 72, 2, "spell_damage", 0, None,
     "Consumes the target in holy flame."),
]

# ============================================================
# DRUID - Leather, Intellect/Spirit, Mana
# ============================================================
DRUID = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 42, 0, 0, "damage", 0, None,
     "A basic claw attack."),
    ("wrath", "Wrath", "mana", 5, 1, 25, 15, 74, 37, 0, "spell_damage", 0, None,
     "Calls upon nature to strike the target."),
    ("moonfire", "Moonfire", "mana", 5, 1, 30, 16, 96, 60, 0, "spell_dot", 3,
     None, "Burns the target with lunar fire over 3 turns."),
    ("rejuvenation", "Rejuvenation", "mana", 5, 1, 35, 20, 135, 72, 1, "hot", 4, None,
     "Nature's energy restores your health over 4 turns."),
    ("mark_of_the_wild", "Mark of the Wild", "mana", 4, 6, 40, 20, 100, 0, 5, "buff", 5,
     {"strength": 6, "agility": 6, "intellect": 6, "spirit": 6, "stamina": 6},
     "Blesses you with the wild's favor, increasing all attributes."),
    ("mangle", "Mangle", "mana", 4, 10, 30, 16, 115, 55, 1, "damage", 0, None,
     "Mangles the target with savage claws."),
    ("entangling_roots", "Entangling Roots", "mana", 3, 14, 35, 18, 100, 0, 3, "debuff", 3,
     {"haste": -18, "dodge": -12},
     "Roots ensnare the target, slowing it for 3 turns."),
    ("starfire", "Starfire", "mana", 4, 20, 50, 26, 155, 74, 2, "spell_damage", 0, None,
     "Calls down a burst of stellar energy."),
    ("healing_touch", "Healing Touch", "mana", 4, 26, 55, 30, 175, 85, 2, "heal", 0, None,
     "A powerful healing spell drawn from nature."),
]

# ============================================================
# SHAMAN - Mail, Intellect/Spirit, Mana
# ============================================================
SHAMAN = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 44, 0, 0, "damage", 0, None,
     "A basic melee attack."),
    ("lightning_bolt", "Lightning Bolt", "mana", 5, 1, 28, 16, 76, 38, 0, "spell_damage", 0, None,
     "Hurls a bolt of lightning at the target."),
    ("earth_shock", "Earth Shock", "mana", 5, 1, 32, 17, 88, 42, 2, "spell_damage", 0, None,
     "Shocks the target with the fury of the earth."),
    ("lava_burst", "Lava Burst", "mana", 5, 10, 45, 24, 140, 62, 3, "spell_damage", 0, None,
     "Hurls molten lava that deals heavy fire damage."),
    ("flame_shock", "Flame Shock", "mana", 4, 6, 30, 16, 100, 62, 2, "spell_dot", 3,
     None, "Sears the target with flame over 3 turns."),
    ("healing_wave", "Healing Wave", "mana", 5, 4, 40, 24, 125, 64, 1, "heal", 0, None,
     "A wave of restorative energy heals your wounds."),
    ("lightning_shield", "Lightning Shield", "mana", 4, 8, 35, 18, 100, 0, 4, "buff", 4,
     {"spell_power": 22, "armor": 60},
     "Surrounds you with crackling lightning, boosting Spell Power and Armor."),
    ("frost_shock", "Frost Shock", "mana", 3, 16, 38, 20, 100, 0, 3, "debuff", 3,
     {"haste": -16, "attack_power": -25},
     "Chills the target, slowing and weakening it for 3 turns."),
    ("chain_lightning", "Chain Lightning", "mana", 4, 24, 55, 28, 160, 76, 3, "spell_damage", 0, None,
     "Arcing lightning that leaps between foes."),
]

# ============================================================
# PALADIN - Plate, Strength/Intellect, Mana
# ============================================================
PALADIN = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 48, 0, 0, "damage", 0, None,
     "A basic melee attack."),
    ("crusader_strike", "Crusader Strike", "mana", 5, 1, 25, 15, 68, 36, 0, "damage", 0, None,
     "A holy-infused melee strike."),
    ("holy_light", "Holy Light", "mana", 5, 1, 45, 26, 110, 58, 1, "heal", 0, None,
     "A burst of holy light that heals your wounds."),
    ("judgement", "Judgement", "mana", 4, 12, 30, 18, 60, 34, 1, "spell_damage", 0, None,
     "Judges the target, dealing holy damage."),
    ("consecration", "Consecration", "mana", 4, 8, 40, 20, 105, 62, 2, "spell_dot", 3,
     None, "Consecrates the ground, burning the target over 3 turns."),
    ("blessing_of_might", "Blessing of Might", "mana", 4, 6, 35, 18, 100, 0, 5, "buff", 5,
     {"attack_power": 40, "strength": 8},
     "Blesses you with might, increasing Attack Power and Strength."),
    ("hammer_of_justice", "Hammer of Justice", "mana", 3, 16, 35, 18, 100, 0, 4, "debuff", 2,
     {"haste": -25, "attack_power": -30},
     "Stuns the target with a hammer of Light for 2 turns."),
    ("divine_shield", "Divine Shield", "mana", 3, 22, 50, 26, 100, 0, 6, "buff", 3,
     {"armor": 180, "magic_resistance": 80},
     "The Light shields you from harm for 3 turns."),
    ("hammer_of_wrath", "Hammer of Wrath", "mana", 4, 28, 45, 24, 175, 80, 3, "spell_damage", 0, None,
     "Hurls a hammer of holy energy at a wounded foe."),
]



# ============================================================
# STORMBRINGER (CoA) - Cloth, Intellect, Mana + Static
# ============================================================
# First CoA class implemented. Sourced from Kyle's Stormbringer.docx export
# and the in-client ability grid screenshots.
#
# THE MECHANIC: Stormbringer is a builder/spender. Mana-cost abilities BANK
# Static (Electrocute/Gale/Volt "Generates 20 Static"); Static-cost abilities
# spend it for the big payoffs (Aeroblast/Conjure Storm "Depletes 50 Static").
# Static caps at 100 and decays out of combat like Rage, so you cannot walk
# into a fight pre-loaded. This is why Ability supports `generates` and why
# CLASS_RESOURCE_MAP maps Stormbringer to (MANA, STATIC).
#
# Static costs are FLAT across ranks (non-Mana resource, WoW-correct) - the
# generator enforces this, matching real CoA where "Depletes 50 Static" does
# not scale with rank.
#
# The three specs are Wind, Maelstrom and Lightning (NOT the
# Lightning/Thunder/Winds guessed in COA_21_CLASS_RESOURCE_REFERENCE.md -
# corrected from the client screenshots).
STORMBRINGER = [
    ("attack", "Attack", "mana", 1, 1, 0, 0, 42, 0, 0, "damage", 0, None,
     "A basic staff strike."),

    # --- Static builders (cost Mana, generate Static) ---
    ("forked_lightning", "Forked Lightning", "mana", 5, 1, 26, 15, 72, 36, 0,
     "spell_damage", 0, None,
     "Shoot lightning at an enemy, bouncing between nearby targets.",
     {"resource": "static", "amount": 15}),
    ("electrocute", "Electrocute", "mana", 5, 10, 30, 16, 96, 44, 2,
     "spell_damage", 0, None,
     "Electrocute an enemy with a surge of raw current.",
     {"resource": "static", "amount": 20}),
    ("gale", "Gale", "mana", 4, 16, 28, 14, 84, 40, 1,
     "spell_damage", 0, None,
     "Blast an enemy with a powerful gust of wind.",
     {"resource": "static", "amount": 20}),
    ("volt", "Volt", "mana", 4, 22, 24, 12, 96, 52, 0,
     "spell_dot", 3, None,
     "Fuse lightning into an enemy, dealing Nature damage over time.",
     {"resource": "static", "amount": 10}),

    # --- Static spenders (cost Static, flat cost, big payoff) ---
    ("aeroblast", "Aeroblast", "static", 4, 12, 50, 0, 150, 70, 0,
     "spell_damage", 0, None,
     "Crush an enemy with the weight of the winds, striking a second time."),
    ("conjure_storm", "Conjure Storm", "static", 4, 18, 50, 0, 130, 60, 3,
     "spell_dot", 3, None,
     "Conjure a storm over the target, dealing Nature damage over time."),
    ("conjure_rainstorm", "Conjure Rainstorm", "static", 3, 20, 20, 0, 88, 46, 2,
     "spell_damage", 0, None,
     "Conjure a freezing rainstorm, dealing Froststorm damage."),

    # --- Utility ---
    ("aerodynamics", "Aerodynamics", "static", 2, 40, 40, 0, 100, 20, 4,
     "buff", 3, {"spell_power": 40, "attack_power": 40},
     "Envelop yourself in magical mist, increasing attack and spell power."),
    ("storm_alert", "Storm Alert", "mana", 3, 8, 22, 12, 100, 15, 5,
     "debuff", 2, {"attack_power": -30},
     "Disturb an enemy with a vision of the coming storm, unnerving them."),
]

CLASS_KITS = {
    "Warrior": ("warrior", WARRIOR),
    "Rogue": ("rogue", ROGUE),
    "Hunter": ("hunter", HUNTER),
    "Mage": ("mage", MAGE),
    "Warlock": ("warlock", WARLOCK),
    "Priest": ("priest", PRIEST),
    "Druid": ("druid", DRUID),
    "Shaman": ("shaman", SHAMAN),
    "Paladin": ("paladin", PALADIN),

    # First of the 21 CoA classes.
    "Stormbringer": ("stormbringer", STORMBRINGER),
}
