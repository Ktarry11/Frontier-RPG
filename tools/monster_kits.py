"""
Monster ability kit data.

THE PROBLEM THIS SOLVES
-----------------------
Monster movesets used to live on the *template*, and templates are
mechanical (humanoid_caster = "squishy, high INT, has mana"). That meant
every single humanoid_caster in the game shared one moveset. A Scarlet
Crusade Chaplain, a Burning Blade cultist and a troll witch doctor were
all casting Shadow Bolt and Dark Mending, because mechanically they are
the same shape.

Kits split flavour from mechanics. The template still decides the stat
block and resource type; the KIT decides what the thing actually does.
A Scarlet zealot and a Burning Blade cultist can share humanoid_caster
and still cast completely different spells.

AUTHORING FORMAT
----------------
Each ability is a tuple:

    (name, kind, damage, cooldown, mana, school, extra)

  name     display name
  kind     "damage" | "heal" | "dot" | "buff" | "debuff"
  damage   direct damage (or heal amount for "heal", or per-turn potency
           for "dot"). 0 for pure buff/debuff.
  cooldown turns before reuse. 0 = every turn.
  mana     resource cost. 0 = free. Only meaningful for mana templates;
           rage/energy monsters treat everything as free (WoW-ish enough
           for a monster, and they don't have a resource bar in the UI).
  school   "physical" | "magic" — routes through armor vs magic resist
  extra    dict. Recognised keys:
             duration    turns, required for dot/buff/debuff
             stat_mods   {stat: delta} for buff/debuff
             self_only   True for buffs the caster puts on itself

The FIRST ability in every kit is the basic attack: it must be free,
zero-cooldown, and "damage". The AI always has it as a fallback.
"""

# ======================================================================
# BEASTS — no spells, no tactics, just teeth and mass
# ======================================================================
BEAST_KITS = {
    "boar": [
        ("Gore", "damage", 18, 0, 0, "physical", {}),
        ("Ripping Tusk", "dot", 7, 3, 0, "physical", {"duration": 3}),
    ],
    "prowler": [
        ("Claw", "damage", 16, 0, 0, "physical", {}),
        ("Pounce", "damage", 26, 2, 0, "physical", {}),
        ("Rending Bite", "dot", 6, 4, 0, "physical", {"duration": 3}),
    ],
    "savannah_patriarch": [
        # Apex-predator tier of the savannah cat line, on beast_large
        # (190 HP/24 atk) rather than prowler's beast_fast baseline
        # (100 HP/16 atk) - a real step up in every number, not just a
        # higher level tag on identical stats. "Patriarch" should hit
        # harder than the giraffe it's hunting, not softer.
        ("Crushing Claw", "damage", 26, 0, 0, "physical", {}),
        ("Savage Pounce", "damage", 40, 2, 0, "physical", {}),
        ("Rending Bite", "dot", 10, 4, 0, "physical", {"duration": 4}),
    ],
    "raptor": [
        ("Raptor Strike", "damage", 17, 0, 0, "physical", {}),
        ("Savage Rend", "dot", 7, 3, 0, "physical", {"duration": 3}),
        ("Leaping Slash", "damage", 27, 3, 0, "physical", {}),
    ],
    "elder_scythemaw": [
        # Elder Bloodtalon Scythemaw is level 18-24, the same tier as
        # Kodo/Savannah Patriarch, but "raptor" is tuned for the 9-16
        # tier it's shared with (Sunscale Screecher, base Bloodtalon
        # Raptor). A real step-up kit rather than reusing raptor's
        # numbers unchanged at nearly double the level.
        ("Scythe Claw", "damage", 23, 0, 0, "physical", {}),
        ("Savage Rend", "dot", 10, 3, 0, "physical", {"duration": 4}),
        ("Leaping Slash", "damage", 36, 3, 0, "physical", {}),
    ],
    "sunscale_lashtail": [
        # Sunscale Lashtail is level 18-24 (Screecher's higher-tier
        # sibling, which stays at 12-16 on the base raptor kit) - a
        # real venom DoT on top of raptor's shape, not just a level tag
        # on identical numbers.
        ("Tail Lash", "damage", 22, 0, 0, "physical", {}),
        ("Venomous Strike", "dot", 11, 3, 0, "magic", {"duration": 4}),
        ("Leaping Slash", "damage", 34, 3, 0, "physical", {}),
    ],
    "wolf": [
        ("Bite", "damage", 16, 0, 0, "physical", {}),
        ("Howl", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 8}}),
        ("Throat Tear", "damage", 27, 3, 0, "physical", {}),
    ],
    "vulture": [
        ("Talon Rake", "damage", 16, 0, 0, "physical", {}),
        ("Carrion Peck", "dot", 5, 3, 0, "physical", {"duration": 3}),
    ],
    "bat": [
        ("Wing Buffet", "damage", 15, 0, 0, "physical", {}),
        ("Bloodletting Bite", "dot", 6, 3, 0, "physical", {"duration": 3}),
    ],
    "large_beast": [
        ("Slam", "damage", 24, 0, 0, "physical", {}),
        ("Stomp", "damage", 36, 3, 0, "physical", {}),
        ("Thick Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
    ],
    "thunder_lizard": [
        ("Slam", "damage", 24, 0, 0, "physical", {}),
        ("Lightning Nova", "damage", 30, 3, 0, "magic", {}),
        ("Thick Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
    ],
    "crocolisk": [
        ("Snapping Bite", "damage", 23, 0, 0, "physical", {}),
        ("Death Roll", "dot", 14, 4, 0, "physical", {"duration": 3}),
    ],
    "razorjaw_apex": [
        # Razorjaw Reef's boss (new area, this session) - a genuine apex
        # predator: reef_predator's bleed shape plus a self-buff frenzy
        # (same "escalates as the fight goes" pattern as other reef/
        # beast bosses - Elder Bloodtalon's tier) rather than a flat
        # damage-up stat stick.
        ("Razor Bite", "damage", 28, 0, 0, "physical", {}),
        ("Thrashing Bleed", "dot", 13, 3, 0, "physical", {"duration": 3}),
        ("Blood Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    "kodo": [
        ("Trample", "damage", 25, 0, 0, "physical", {}),
        ("Kodo Stomp", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "is_aoe": True, "stat_mods": {"agility": -18}}),
    ],
    "giraffe": [
        ("Headbutt", "damage", 22, 0, 0, "physical", {}),
        ("Dazing Kick", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"hit_rating": -12}}),
    ],
    "plainstrider": [
        ("Beak Jab", "damage", 17, 0, 0, "physical", {}),
        ("Dust Cloud", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"hit_rating": -8}}),
    ],
    "zhevra": [
        ("Hoof Strike", "damage", 18, 0, 0, "physical", {}),
        ("Bolt", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"agility": 10}}),
    ],
}

# ======================================================================
# VERMIN — poison, webs, numbers
# ======================================================================
VERMIN_KITS = {
    "scorpid": [
        ("Sting", "damage", 15, 0, 0, "physical", {}),
        ("Venomous Sting", "dot", 6, 3, 0, "magic", {"duration": 4}),
    ],
    "spider": [
        ("Bite", "damage", 15, 0, 0, "physical", {}),
        ("Poison Spit", "dot", 6, 3, 0, "magic", {"duration": 4}),
        ("Web", "debuff", 0, 4, 0, "magic",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "serpent": [
        ("Fang Strike", "damage", 16, 0, 0, "physical", {}),
        ("Neurotoxin", "dot", 7, 3, 0, "magic", {"duration": 4}),
    ],
    "swarm": [
        ("Swarm Bite", "damage", 11, 0, 0, "physical", {}),
        ("Skitter", "buff", 0, 3, 0, "physical",
         {"duration": 2, "self_only": True, "stat_mods": {"agility": 8}}),
    ],
    "silithid": [
        ("Chitinous Slash", "damage", 19, 0, 0, "physical", {}),
        ("Acid Spray", "dot", 7, 3, 0, "magic", {"duration": 3}),
    ],
    "deviate_viper": [
        # Distinct from deviate_python's flat-damage venom - a real DoT,
        # matching "Viper" being a poison-specialist snake distinct from
        # Python's constrict/venom-fangs pair.
        ("Venomous Bite", "damage", 20, 0, 0, "physical", {}),
        ("Crippling Poison", "dot", 9, 3, 0, "magic", {"duration": 4}),
    ],
    "deviate_shambler": [
        # Fandom: "Deviate Shamblers later can cast regeneration on
        # themselves, purge utterly counters this" - a real self-heal,
        # not the acid/DoT flavor Deviate Ooze already covers.
        ("Bog Slam", "damage", 24, 0, 0, "physical", {}),
        ("Regeneration", "heal", 30, 4, 0, "magic", {}),
    ],
    "deviate_ravager": [
        # Deviate Ravager previously had no ability_kit at all (silent
        # fallback to the beast_fast template default, "prowler" - which
        # is already a different Durotar creature's identity) plus dead
        # hp_mult/atk_mult fields the engine has never read. Real kit
        # gives it its own beetle/insect-flavored moveset instead.
        ("Mandible Crush", "damage", 30, 0, 0, "physical", {}),
        ("Frenzied Charge", "damage", 42, 3, 0, "physical", {}),
    ],
    "deviate_faerie_dragon": [
        # Real WC rare elite - Icy Veins: "has no mechanics required to
        # kill it," so kept simple but genuinely fey/arcane-flavored
        # rather than physical, matching a small magical dragon rather
        # than a beast.
        ("Arcane Spark", "damage", 26, 0, 22, "magic", {}),
        ("Mana Drain", "debuff", 0, 4, 20, "magic",
         {"duration": 3, "stat_mods": {"intellect": -14}}),
    ],
    "deviate_adder": [
        # Previously had no ability_kit at all - silently fell back to
        # vermin_sneaky's template default (scorpid), meaning every
        # Deviate Adder in the game was actually casting Scorpid Sting
        # with no mention of "Adder" anywhere in its own moveset. Distinct
        # from deviate_viper (bite+DoT) and deviate_python (constrict+
        # venom) - a quick double-strike snake instead.
        ("Quick Strike", "damage", 22, 0, 0, "physical", {}),
        ("Double Bite", "damage", 31, 2, 0, "physical", {}),
    ],
    "deviate_lasher": [
        # Previously had no ability_kit at all - silently fell back to
        # beast_fast's template default (prowler). "Lasher" in WoW is a
        # plant/tendril creature, not a beast - Whipping Vine and a real
        # root-effect debuff instead of generic claws.
        ("Whipping Vine", "damage", 28, 0, 0, "physical", {}),
        ("Entangle", "debuff", 0, 4, 0, "magic",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
}

# ======================================================================
# CENTAUR — the Kolkar. Lancers hit, archers SHOOT. No more "Gore".
# ======================================================================
CENTAUR_KITS = {
    "centaur_lancer": [
        ("Lance Thrust", "damage", 21, 0, 0, "physical", {}),
        ("Trample", "damage", 32, 3, 0, "physical", {}),
        ("War Stomp", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -14}}),
    ],
    "centaur_archer": [
        ("Shoot", "damage", 18, 0, 0, "physical", {}),
        ("Aimed Shot", "damage", 31, 3, 0, "physical", {}),
        ("Crippling Shot", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -10}}),
    ],
    "centaur_wrangler": [
        ("Barbed Whip", "damage", 19, 0, 0, "physical", {}),
        ("Ensnaring Lash", "debuff", 0, 3, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "centaur_windchaser": [
        ("Lightning Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Chain Lightning", "damage", 32, 3, 40, "magic", {}),
        ("Ancestral Mending", "heal", 40, 3, 35, "magic", {}),
    ],
    "kolkar_drudge": [
        # Kolkar's laborer/lesser-warrior tier - a bleed DoT rather than
        # a second flat hit, so "Drudge" plays as a grinding, sustained
        # fight distinct from Marauder's clean two-hit burst.
        ("Club Smash", "damage", 19, 0, 0, "physical", {}),
        ("Gash", "dot", 8, 3, 0, "physical", {"duration": 4}),
    ],
    "verog_the_dervish": [
        # Real confirmed ability (Wowpedia): "Rushing Charge - Charges
        # the target and causes the caster to inflict additional damage
        # on its next attack." Modeled as a self-buff (attack_power
        # spike) that precedes the follow-up hit, since this engine has
        # no separate charge/gap-closer mechanic.
        ("Slash", "damage", 36, 0, 0, "physical", {}),
        ("Rushing Charge", "buff", 0, 4, 0, "physical",
         {"duration": 1, "self_only": True, "stat_mods": {"attack_power": 40}}),
        ("Dervish Whirl", "damage", 42, 4, 0, "physical", {"is_aoe": True}),
    ],
}

# ======================================================================
# BRISTLEBACK — the Barrens quilboar tribe (distinct from Razormane).
# Shaman/Thornweaver/Geomancer abilities are real confirmed lore
# (Wowpedia/Wowhead): Shaman casts Lightning Bolt; Thornweaver uses
# Entangling Roots + a real Thorns reflect-damage buff; Geomancer is
# fire-flavored (Fireball/Flamestrike/Quick Flameward, see
# quilboar_geomancer above, which this tribe's Geomancer now uses).
# ======================================================================
BRISTLEBACK_KITS = {
    "bristleback_quilboar": [
        ("Tusk Gore", "damage", 22, 0, 0, "physical", {}),
        ("Rending Tusk", "dot", 8, 3, 0, "physical", {"duration": 3}),
    ],
    "bristleback_shaman": [
        ("Lightning Bolt", "damage", 26, 0, 22, "magic", {}),
        ("Earthbind", "debuff", 0, 4, 18, "magic",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "bristleback_thornweaver": [
        ("Wrath", "damage", 20, 0, 18, "magic", {}),
        ("Entangling Roots", "dot", 10, 3, 20, "magic", {"duration": 3}),
        ("Thorns", "buff", 0, 5, 24, "magic",
         {"duration": 6, "self_only": True, "stat_mods": {"armor": 18}}),
    ],
    "bristleback_water_seeker": [
        # Ranged skirmisher per the tribe's ranged "Water Seeker" role -
        # a real crippling shot (kites/slows) rather than a second flat
        # ranged hit, so it plays as hit-and-run rather than melee-
        # adjacent damage racing.
        ("Sling Shot", "damage", 20, 0, 0, "physical", {}),
        ("Crippling Shot", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "charlgas_enforcer": [
        # Charlga Razorflank's personal enforcer - elite melee tier with
        # a real debuff (a genuinely dangerous fight, not just bigger
        # numbers than rank-and-file Bristleback Quilboar).
        ("Crushing Gore", "damage", 30, 0, 0, "physical", {}),
        ("Enforcer's Wrath", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -20}}),
    ],
}

# ======================================================================
# BANDITS — human/humanoid raiders, plain mundane weapon kits (no magic,
# no named-lore abilities confirmed - ordinary trash).
# ======================================================================
BANDIT_KITS = {
    "bandit_cutthroat": [
        ("Backstab", "damage", 22, 0, 0, "physical", {}),
        ("Garrote", "dot", 8, 3, 0, "physical", {"duration": 4}),
    ],
    "bandit_outrider": [
        ("Shoot", "damage", 19, 0, 0, "physical", {}),
        ("Called Shot", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
}

# ======================================================================
# MURLOCS (Barrens variants) — Gaharrz the Drowned is an original named
# rare per Kyle's call (real murloc faction/flavor, not a literal WoW
# NPC match), given a slightly heavier kit than rank-and-file trash to
# read as a mini-boss.
# ======================================================================
BARRENS_MURLOC_KITS = {
    "murloc_flesheater": [
        ("Rend Flesh", "damage", 24, 0, 0, "physical", {}),
        ("Bloodlust", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "pool_murloc": [
        ("Spear Jab", "damage", 20, 0, 0, "physical", {}),
        ("Water Jet", "damage", 30, 3, 22, "magic", {}),
    ],
    "gaharrz_the_drowned": [
        ("Drowning Grasp", "damage", 32, 0, 0, "physical", {}),
        ("Riptide Slam", "damage", 44, 3, 0, "physical", {}),
        ("Murky Curse", "debuff", 0, 5, 0, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
    ],
}

# ======================================================================
# SILITHID / ELEMENTAL / VENTURE CO. — the remaining Barrens no-kit
# creatures. Venture Co. Overseer's Overseer's Poison is real confirmed
# lore (Wowpedia).
# ======================================================================
# ======================================================================
# DUROTAR — the ~40 no-kit creatures across Skull Rock, Tiragarde Keep,
# Dustwind Cave, Drygulch Ravine, Thunder Ridge, Kolkar Crag, and the
# coastal/scorpid open-zone roster. Gazz'uz's kit is real confirmed lore
# (Wowpedia/Warcraft Wiki): Demon Skin, Shadow Bolt, Corruption, Summon
# Voidwalker (approximated as a real damage/buff/dot trio - no summon
# mechanic in this engine). The other named bosses here (Captain
# Thalenvorde, Matriarch Vess'ra, Stormhide Patriarch, Warlord Krellian,
# Gorge the Corpsegrinder) share their names with unrelated real WoW
# NPCs in different zones entirely (confirmed via search) - these are
# original camp bosses, kept as project-original with authentic
# WoW-faction-appropriate kits per their actual camp context.
# ======================================================================
DUROTAR_KITS = {
    "gazzuz": [
        ("Shadow Bolt", "damage", 30, 0, 26, "shadow", {}),
        ("Corruption", "dot", 13, 3, 22, "shadow", {"duration": 4}),
        ("Demon Skin", "buff", 0, 5, 20, "shadow",
         {"duration": 5, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "neru_fireblade": [
        # Gazz'uz's warlock superior in Skull Rock's chain of command -
        # a heavier caster tier above him, same shadow/fel flavor family.
        ("Fel Bolt", "damage", 36, 0, 32, "shadow", {}),
        ("Immolate", "dot", 15, 3, 28, "fire", {"duration": 4}),
        ("Curse of Weakness", "debuff", 0, 5, 24, "shadow",
         {"duration": 4, "stat_mods": {"attack_power": -18}}),
    ],
    "kul_tiras_sailor": [
        # Tiragarde Keep's stranded sailors - real Kul Tiras faction
        # flavor (musket/cutlass), matching drowned_sailor's established
        # gunpowder-pirate shape without being a literal duplicate.
        ("Cutlass Slash", "damage", 21, 0, 0, "physical", {}),
        ("Musket Shot", "damage", 30, 3, 0, "physical", {}),
    ],
    "captain_thalenvorde": [
        # Commander of the stranded Kul Tiras garrison at Tiragarde Keep -
        # a real step up over rank-and-file sailors, with a rallying buff
        # matching a captain leading his crew.
        ("Officer's Blade", "damage", 32, 0, 0, "physical", {}),
        ("Rally the Crew", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
        ("Grapeshot Blast", "damage", 42, 4, 0, "physical", {"is_aoe": True}),
    ],
    "gorge_the_corpsegrinder": [
        # Dustwind Cave's boss - a brute beast matching the cave's
        # bone/scorpid theme, heavy physical hits.
        ("Bone Crunch", "damage", 34, 0, 0, "physical", {}),
        ("Corpsegrind", "dot", 14, 4, 0, "physical", {"duration": 3}),
    ],
    "dustwind_harpy": [
        ("Talon Rake", "damage", 20, 0, 0, "physical", {}),
        ("Gust", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "dustwind_savage": [
        ("Savage Claw", "damage", 22, 0, 0, "physical", {}),
        ("Rend", "dot", 9, 3, 0, "physical", {"duration": 3}),
    ],
    "dustwind_storm_witch": [
        ("Wind Bolt", "damage", 24, 0, 20, "magic", {}),
        ("Storm's Fury", "dot", 10, 3, 18, "nature", {"duration": 3}),
    ],
    "matriarch_vessra": [
        # Drygulch Ravine's boss - a harpy matriarch tier above the
        # Dustwind trash, storm/wind flavor escalated.
        ("Piercing Talon", "damage", 30, 0, 0, "physical", {}),
        ("Cyclone Slash", "damage", 40, 3, 0, "physical", {"is_aoe": True}),
        ("Screeching Gale", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "crackling_thunderhide": [
        ("Thunder Slam", "damage", 26, 0, 0, "physical", {}),
        ("Static Charge", "dot", 10, 3, 0, "magic", {"duration": 3}),
    ],
    "stormhide_patriarch": [
        # Thunder Ridge's apex thunder lizard - real step-up kit over
        # thunder_lizard/crackling_thunderhide, matching "Patriarch"
        # being the pack leader (same convention as Savannah Patriarch).
        ("Thunder Slam", "damage", 32, 0, 0, "physical", {}),
        ("Lightning Nova", "damage", 44, 3, 0, "magic", {"is_aoe": True}),
        ("Thick Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 26}}),
    ],
    "warlord_krellian": [
        # Kolkar Crag's centaur warlord - a real step up over Kolkar
        # Raider/Marauder, matching a warband leader.
        ("Warlord's Cleave", "damage", 34, 0, 0, "physical", {}),
        ("Battle Cry", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
}

BARRENS_MISC_KITS = {
    "silithid_creeper": [
        ("Mandible Bite", "damage", 20, 0, 0, "physical", {}),
        ("Acid Spray", "dot", 7, 3, 0, "magic", {"duration": 3}),
    ],
    "silithid_swarmer": [
        ("Swarm Bite", "damage", 14, 0, 0, "physical", {}),
        ("Skitter", "buff", 0, 3, 0, "physical",
         {"duration": 2, "self_only": True, "stat_mods": {"agility": 8}}),
    ],
    "cavern_rock_elemental": [
        ("Rock Fist", "damage", 26, 0, 0, "physical", {}),
        ("Rubble Slam", "damage", 38, 3, 0, "physical", {}),
        ("Harden", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "venture_co_miner": [
        ("Pickaxe Swing", "damage", 21, 0, 0, "physical", {}),
        ("Blasting Charge", "dot", 12, 4, 0, "fire", {"duration": 2}),
    ],
    "venture_co_overseer": [
        # Overseer's Poison is real confirmed lore (Wowpedia): "Nature
        # damage inflicted every 3 sec."
        ("Whip Crack", "damage", 22, 0, 0, "physical", {}),
        ("Overseer's Poison", "dot", 9, 3, 0, "magic", {"duration": 3}),
    ],
    "venture_co_tinkerer": [
        ("Wrench Throw", "damage", 18, 0, 0, "physical", {}),
        ("Net Launcher", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "foreman_grills": [
        # Named Venture Co. boss/foreman - a real burn DoT from the
        # overcharge rather than a second flat AoE hit, so the fight has
        # actual damage-over-time pressure a healer has to manage.
        ("Foreman's Hammer", "damage", 40, 0, 0, "physical", {}),
        ("Overcharged Blast", "dot", 17, 4, 0, "fire", {"duration": 3, "is_aoe": True}),
        ("Hardhat Brace", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 48}}),
    ],
    "supervisor_lugwizzle": [
        # Real confirmed lore: level 18, patrols the oil platform's
        # control room, no confirmed special combat ability beyond being
        # a quest target - given a straightforward boss-tier goblin kit
        # matching his level rather than an invented signature move.
        ("Wrench Bash", "damage", 34, 0, 0, "physical", {}),
        ("Oil Slick", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -22}}),
        ("Pressure Valve", "damage", 44, 5, 0, "fire", {"is_aoe": True}),
    ],
    "engineer_whirleygig": [
        # Real confirmed lore (Wowpedia): Compact Harvest Reaper (summons
        # a minion for 1 min) and Explosive Sheep (creates a self-
        # destructing charger). This engine has no summon-minion
        # mechanic, so both are approximated as their end effect - a
        # delayed burst (the reaper arriving) and a real AoE burst (the
        # sheep's explosion) - rather than dropped entirely.
        ("Wrench Throw", "damage", 20, 0, 0, "physical", {}),
        ("Compact Harvest Reaper", "damage", 32, 4, 0, "physical", {}),
        ("Explosive Sheep", "damage", 40, 5, 0, "fire", {"is_aoe": True}),
    ],
}

# ======================================================================
# QUILBOAR — Razormane and Razorfen. Tusks and earth magic, not shadow.
# ======================================================================
QUILBOAR_KITS = {
    "quilboar_warrior": [
        ("Tusk Slash", "damage", 20, 0, 0, "physical", {}),
        ("Thorned Charge", "damage", 32, 3, 0, "physical", {}),
    ],
    "quilboar_scout": [
        ("Shoot", "damage", 17, 0, 0, "physical", {}),
        ("Aimed Shot", "damage", 29, 3, 0, "physical", {}),
    ],
    "quilboar_geomancer": [
        # Fixed from an earth-flavored kit (Earth Shock/Healing Ward/
        # Stoneskin) that didn't match confirmed real lore. Bristleback
        # Geomancer's actual kit is fire-flavored: Fireball, Flamestrike
        # (AoE burn), Quick Flameward (self fire-immunity buff -
        # approximated as a magic-resist spike since this engine has no
        # damage-type immunity mechanic).
        ("Fireball", "damage", 22, 0, 20, "magic", {}),
        ("Flamestrike", "dot", 10, 4, 32, "magic", {"duration": 4, "is_aoe": True}),
        ("Quick Flameward", "buff", 0, 5, 22, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 25}}),
    ],
    "quilboar_battleguard": [
        ("Cleave", "damage", 23, 0, 0, "physical", {}),
        ("Battle Shout", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 12}}),
        ("Execute", "damage", 35, 3, 0, "physical", {}),
    ],
    "quilboar_blood_priest": [
        ("Blood Lance", "damage", 21, 0, 20, "magic", {}),
        ("Agony Thorns", "dot", 8, 3, 26, "magic", {"duration": 4}),
        ("Blood Mending", "heal", 45, 3, 38, "magic", {}),
    ],
}

# ======================================================================
# TROLLS — voodoo, hexes, thrown weapons
# ======================================================================
TROLL_KITS = {
    "troll_witchdoctor": [
        ("Shadow Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Voodoo Mending", "heal", 40, 3, 35, "magic", {}),
        ("Hex", "debuff", 0, 4, 30, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -18}}),
    ],
    "troll_headhunter": [
        ("Throw Axe", "damage", 19, 0, 0, "physical", {}),
        ("Bleeding Throw", "dot", 7, 3, 0, "physical", {"duration": 3}),
    ],
    "troll_berserker": [
        ("Cleave", "damage", 22, 0, 0, "physical", {}),
        ("Berserk", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True,
          "stat_mods": {"attack_power": 16, "agility": 10}}),
    ],
}

# ======================================================================
# TROGGS — Ragefire Chasm's cave-dwelling clan. Dumb, physical melee for
# the rank and file; the shaman variant throws a shock-type nuke, which
# real-guide advice on interrupting it (kick/shield bash/CC) implies is a
# cast-time spell rather than an instant, so it's modeled with a
# cooldown rather than free-spam like the melee troggs.
# ======================================================================
TROGG_KITS = {
    "ragefire_trogg": [
        ("Trogg Smash", "damage", 24, 0, 0, "physical", {}),
        ("Rock Throw", "damage", 33, 3, 0, "physical", {}),
    ],
    "ragefire_shaman": [
        ("Earth Shock", "damage", 26, 0, 22, "magic", {}),
        ("Rockbiter Weapon", "buff", 0, 5, 18, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
}

# ======================================================================
# HARPIES — wind magic and dive attacks
# ======================================================================
HARPY_KITS = {
    "harpy_melee": [
        ("Talon Slash", "damage", 18, 0, 0, "physical", {}),
        ("Dive Bomb", "damage", 30, 3, 0, "physical", {}),
    ],
    "harpy_windcaller": [
        ("Lightning Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Screeching Gale", "debuff", 0, 4, 28, "magic",
         {"duration": 3, "stat_mods": {"hit_rating": -10}}),
        ("Mending Winds", "heal", 38, 3, 32, "magic", {}),
    ],
}

# ======================================================================
# HUMANOID GENERIC — bandits, marines, goblins, dwarves
# ======================================================================
HUMANOID_KITS = {
    "soldier": [
        ("Slash", "damage", 20, 0, 0, "physical", {}),
        ("Battle Shout", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 12}}),
        ("Execute", "damage", 32, 3, 0, "physical", {}),
    ],
    "shield_soldier": [
        ("Shield Slam", "damage", 19, 0, 0, "physical", {}),
        ("Defensive Stance", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 26}}),
        ("Execute", "damage", 32, 3, 0, "physical", {}),
    ],
    "rogue": [
        ("Backstab", "damage", 21, 0, 0, "physical", {}),
        ("Eviscerate", "damage", 33, 3, 0, "physical", {}),
        ("Evasion", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"agility": 18}}),
    ],
    "marksman": [
        ("Shoot", "damage", 18, 0, 0, "physical", {}),
        ("Aimed Shot", "damage", 31, 3, 0, "physical", {}),
        ("Concussive Shot", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -12}}),
    ],
    "rifleman": [
        ("Rifle Shot", "damage", 19, 0, 0, "physical", {}),
        ("Blunderbuss", "damage", 32, 3, 0, "physical", {}),
        ("Frag Grenade", "dot", 7, 4, 0, "magic", {"duration": 3}),
    ],
    "goblin_tinker": [
        ("Wrench Bash", "damage", 18, 0, 0, "physical", {}),
        ("Bomb Toss", "damage", 30, 3, 0, "magic", {}),
        ("Shock Grenade", "debuff", 0, 4, 0, "magic",
         {"duration": 2, "stat_mods": {"hit_rating": -12}}),
    ],
    "dwarf_digger": [
        ("Pickaxe Swing", "damage", 20, 0, 0, "physical", {}),
        ("Cave In", "damage", 33, 3, 0, "physical", {}),
    ],
    "mage_arcane": [
        ("Frostbolt", "damage", 21, 0, 18, "magic", {}),
        ("Fire Blast", "damage", 33, 3, 40, "magic", {}),
        ("Frost Armor", "buff", 0, 5, 25, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
}

# ======================================================================
# SCARLET CRUSADE — HOLY. This is the fix Kyle asked for.
# Zealots, not necromancers. Light-based damage, real Priest healing,
# Power Word: Shield. Not one shadow spell in the faction.
# ======================================================================
SCARLET_KITS = {
    "scarlet_zealot": [
        ("Crusader Strike", "damage", 21, 0, 0, "physical", {}),
        ("Holy Smite", "damage", 26, 2, 22, "magic", {}),
        ("Seal of Righteousness", "buff", 0, 5, 20, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "scarlet_defender": [
        ("Shield Slam", "damage", 20, 0, 0, "physical", {}),
        ("Devotion Aura", "buff", 0, 5, 20, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 26}}),
        ("Holy Smite", "damage", 26, 3, 22, "magic", {}),
    ],
    "scarlet_chaplain": [
        ("Holy Smite", "damage", 21, 0, 20, "magic", {}),
        ("Holy Light", "heal", 46, 3, 38, "magic", {}),
        ("Power Word: Shield", "buff", 0, 5, 30, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 30}}),
    ],
    "scarlet_inquisitor": [
        ("Searing Light", "damage", 22, 0, 20, "magic", {}),
        ("Holy Fire", "dot", 8, 3, 30, "magic", {"duration": 4}),
        ("Renew", "heal", 36, 4, 30, "magic", {}),
    ],
    "scarlet_marksman": [
        ("Shoot", "damage", 18, 0, 0, "physical", {}),
        ("Aimed Shot", "damage", 31, 3, 0, "physical", {}),
        ("Blessed Bolt", "damage", 26, 4, 20, "magic", {}),
    ],
}

# ======================================================================
# BURNING BLADE / SHADOW CULTISTS — THIS is where dark magic belongs
# ======================================================================
CULTIST_KITS = {
    "cultist_shadow": [
        ("Shadow Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Curse of Agony", "dot", 8, 3, 28, "magic", {"duration": 4}),
        ("Dark Mending", "heal", 40, 4, 35, "magic", {}),
    ],
    "cultist_warlock": [
        ("Shadow Bolt", "damage", 22, 0, 20, "magic", {}),
        ("Immolate", "dot", 9, 3, 30, "magic", {"duration": 4}),
        ("Drain Life", "heal", 32, 3, 30, "magic", {}),
    ],
    "cultist_enforcer": [
        ("Fel Slash", "damage", 21, 0, 0, "physical", {}),
        ("Demonic Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "searing_blade_fanatic": [
        # Ragefire Chasm-tier Searing Blade trash. Distinct from
        # Skull Rock's Durotar-tier "Searing Blade Enforcer"/"Searing
        # Blade Warlock" (level 7-11) - those are a lower-level patrol
        # of the same cult, not this dungeon's roster, so this gets its
        # own kit id rather than sharing one across two very different
        # level tiers.
        ("Fel Slash", "damage", 30, 0, 0, "physical", {}),
        ("Searing Strike", "damage", 40, 3, 0, "physical", {}),
    ],
    "searing_blade_invoker": [
        # Casts a shadow nuke per every real-guide interrupt callout
        # ("use the same strategies as with the Ragefire Shaman to
        # pull") - modeled with a cooldown so it reads as interruptible
        # rather than a free-spam filler.
        ("Shadow Bolt", "damage", 34, 0, 30, "magic", {}),
        ("Curse of Weakness", "debuff", 0, 5, 26, "shadow",
         {"duration": 4, "stat_mods": {"attack_power": -14}}),
    ],
}

# ======================================================================
# RAGEFIRE CHASM — dungeon-specific trash and named bosses that don't
# fit an existing family bucket cleanly. Bazzalan's kit corrected below
# to match confirmed real lore (Icy Veins: "Bazzalan has two abilities,
# Sinister Strike and Deadly Poison") - the fel-claw/shadow-volley kit
# it shipped with previously wasn't accurate to the actual encounter.
# Earthborer corrected from an earlier (wrong) boss-tier caster kit to
# a simple trash-worm physical kit - real WoW Earthborer is confirmed
# trash, not a boss (see zone_generator.py's own docstring on this).
# ======================================================================
RAGEFIRE_BOSS_KITS = {
    "bazzalan": [
        ("Sinister Strike", "damage", 32, 0, 0, "physical", {}),
        ("Deadly Poison", "dot", 12, 3, 0, "physical", {"duration": 4}),
        # Final-boss additions (2026-10-21): a Searing Blade assassin who opens
        # from the shadows of his throne room.  PLANNED SUMMON HOOK: "Shadow
        # Acolytes" (2 adds at 50% HP) once monster summons exist.
        ("Gouging Cut", "damage", 46, 3, 0, "physical", {}),
        ("Void Shroud", "buff", 0, 6, 0, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"agility": 22}}),
    ],
    "earthborer": [
        ("Burrow Strike", "damage", 22, 0, 0, "physical", {}),
        ("Tremor", "damage", 30, 3, 0, "physical", {}),
    ],
    "molten_elemental": [
        ("Molten Touch", "damage", 27, 0, 0, "magic", {}),
        ("Lava Spit", "dot", 10, 3, 0, "magic", {"duration": 3}),
    ],
}

# ======================================================================
# WAILING CAVERNS — real Classic roster. The 4 Fanglords (Lady Anacondra,
# Lord Cobrahn, Lord Pythas, Lord Serpentis) share one literal kit per
# real WoW - every guide describes the same 3 abilities (Lightning Bolt,
# Healing Touch, Sleep/Druid's Slumber) for all four, with only level and
# HP differing between them. Lord Pythas previously had a warrior-style
# kit (Heavy Slash/Thunderclap) that didn't match his real caster
# abilities - his template is fixed alongside this in creatures.json
# from humanoid_warrior to humanoid_caster, since Heavy Slash/Thunderclap
# on a rage-resource warrior template was the actual mismatch bug.
# ======================================================================
# ======================================================================
# BLACKFATHOM DEEPS — real Classic 7-boss roster (Baron Aquanis, an 8th
# real boss, is a Horde-only quest-summon variant not modeled here yet).
# Confirmed real order: Ghamoo-ra -> Lady Sarevess -> Gelihast -> Lorgus
# Jett -> Old Serra'kis -> Twilight Lord Kelris -> Aku'mai. Ghamoo-ra's
# kit fixed to his one confirmed real ability, Trample (previously
# Crushing Bite/Tail Sweep, no Trample anywhere). Lady Sarevess's kit
# fixed to include her confirmed Forked Lightning (previously Frost
# Blade/Naga Fury/Tidal Ward, no lightning ability at all). The other
# five bosses have no confirmed named mechanics ("no mechanics worth
# mentioning" per every real guide), so their existing flavor kits are
# kept as-is.
# ======================================================================
# ======================================================================
# ECHO ISLES — Zalazane's confirmed real lore (Wowpedia/Warcraft Wiki):
# a shaman/witch doctor who "heals himself a lot" and "begins the fight
# by summoning undead, then uses death coil and other offensive spells."
# Modeled as Death Coil (shadow damage) + a real self-heal + a burst
# approximating the undead summon (no summon mechanic in this engine).
# Tidelord Gharesh has no confirmed real match (elemental/tidelord name
# not found in WoW lore searches) - kept original with authentic
# aquatic-elemental flavor matching its Sunken Temple Grotto home.
# ======================================================================
ECHO_ISLES_KITS = {
    "zalazane": [
        ("Death Coil", "damage", 30, 0, 26, "shadow", {}),
        ("Zalazane's Mending", "heal", 45, 3, 34, "shadow", {}),
        ("Raise Dead", "damage", 38, 4, 30, "shadow", {}),
    ],
    "voodoo_troll": [
        ("Hex Bolt", "damage", 22, 0, 18, "magic", {}),
        ("Voodoo Curse", "debuff", 0, 4, 16, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -12}}),
    ],
    "hex_troll": [
        ("Hexed Claw", "damage", 24, 0, 0, "physical", {}),
        ("Unsettling Hex", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "hexed_thrall": [
        # Undead-enslaved Darkspear - a rotting melee kit distinct from
        # the still-living Voodoo/Hex Trolls.
        ("Rotting Strike", "damage", 23, 0, 0, "physical", {}),
        ("Disease Bite", "dot", 9, 3, 0, "physical", {"duration": 3}),
    ],
    "zalazane_berserker": [
        ("Berserk Slash", "damage", 26, 0, 0, "physical", {}),
        ("Bloodrage", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "tidelord_gharesh": [
        ("Tidal Crush", "damage", 32, 0, 0, "magic", {}),
        ("Riptide Slam", "dot", 14, 3, 24, "magic", {"duration": 3}),
        ("Tidal Ward", "buff", 0, 5, 20, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 22}}),
    ],
    "tidal_elemental": [
        ("Water Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Wash Away", "debuff", 0, 4, 16, "magic",
         {"duration": 2, "stat_mods": {"agility": -10}}),
    ],
    "grotto_murloc": [
        ("Spear Jab", "damage", 18, 0, 0, "physical", {}),
        ("Murky Wail", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"attack_power": -10}}),
    ],
    "drowned_troll": [
        ("Waterlogged Strike", "damage", 22, 0, 0, "physical", {}),
        ("Drowning Grip", "dot", 9, 3, 0, "physical", {"duration": 3}),
    ],
    "shadowfang_guardian": [
        # Despite the name overlap with the Shadowfang Keep dungeon,
        # confirmed earlier this session as unrelated - an Echo Isles
        # demon-hound guardian, fel-hound flavor matching its template.
        ("Fel Bite", "damage", 24, 0, 0, "physical", {}),
        ("Shadow Howl", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "isle_headhunter": [
        ("Throwing Axe", "damage", 21, 0, 0, "physical", {}),
        ("Piercing Throw", "damage", 30, 3, 0, "physical", {}),
    ],
}

# ======================================================================
# VALLEY OF TRIALS — the tutorial zone's own low-level bosses. No
# confirmed real-lore matches for these names (project-original starter
# content), so kits are simple and appropriately gentle for a level 1-5
# zone - the point is giving the very first bosses a new player meets a
# real distinct fight, not silent generic-template damage.
# ======================================================================
# ======================================================================
# ASHENVALE — East (Burning Blade / demon incursion escalation ladder:
# Fel Imp -> Felstalker -> Lord Malgan -> Pit Lord Emissary, matching
# real WoW's Legion-incursion motif) and Twilight's Hammer cultist
# content. No confirmed exact real-NPC matches for these named bosses
# (per established pattern this session), so kits use authentic
# faction-appropriate escalating power rather than invented specials.
# ======================================================================
ASHENVALE_KITS = {
    "burning_blade_cultist_east": [
        # The original Ashenvale-tier Burning Blade Cultist (level
        # 12-15) - distinct from the Valley of Trials-tier Initiate
        # split off earlier this session. Shares cultist_shadow's real
        # shadow-caster shape rather than reinventing it, since it's the
        # same cult, just a higher tier.
        ("Shadow Bolt", "damage", 26, 0, 22, "magic", {}),
        ("Curse of Agony", "dot", 11, 3, 32, "magic", {"duration": 4}),
        ("Dark Mending", "heal", 46, 4, 40, "magic", {}),
    ],
    "felstalker_boss": [
        # First rung of the demon escalation ladder - a step up over
        # Felstalker Whelp/demon_hound trash.
        ("Rend", "damage", 30, 0, 0, "physical", {}),
        ("Savage Lash", "damage", 42, 3, 0, "physical", {}),
        ("Demon Howl", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "lord_malgan": [
        # Mid-tier demon caster commander.
        ("Fel Bolt", "damage", 38, 0, 34, "shadow", {}),
        ("Rain of Fire", "dot", 16, 4, 36, "fire", {"duration": 4, "is_aoe": True}),
        ("Demonic Ward", "buff", 0, 6, 30, "shadow",
         {"duration": 5, "self_only": True, "stat_mods": {"magic_resistance": 24}}),
    ],
    "pit_lord_emissary": [
        # Top of the escalation ladder - the heaviest hitter before
        # whatever real Pit Lord content this leads toward.
        ("Fel Cleave", "damage", 46, 0, 0, "physical", {"is_aoe": True}),
        ("Infernal Slam", "damage", 58, 3, 0, "fire", {}),
        ("Legion's Wrath", "buff", 0, 6, 0, "physical",
         {"duration": 5, "self_only": True, "stat_mods": {"attack_power": 26}}),
    ],
    "twilight_geomancer": [
        ("Earth Shock", "damage", 28, 0, 24, "magic", {}),
        ("Stoneskin Totem", "buff", 0, 5, 22, "magic",
         {"duration": 5, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "twilight_overseer": [
        # Twilight's Hammer field commander - a real step up over
        # Twilight Acolyte/Adept, physical warrior tier matching its
        # humanoid_warrior template.
        ("Overseer's Lash", "damage", 34, 0, 0, "physical", {}),
        ("Twilight Rally", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
        ("Crushing Blow", "damage", 46, 3, 0, "physical", {}),
    ],
    "keeper_rustveil": [
        # Real Keeper of the Grove archetype (Wowpedia): "greater force
        # of nature... animates trees," "many strange powers over
        # nature," and Keeper Ordanus specifically has confirmed Enrage.
        # Modeled as real nature damage + a root-flavored debuff (the
        # animate-trees effect) + the confirmed Enrage buff.
        ("Nature's Wrath", "damage", 36, 0, 32, "nature", {}),
        ("Animate Roots", "debuff", 0, 5, 30, "nature",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -20}}),
        ("Enrage", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 24}}),
    ],
    "ursal_the_mauler": [
        # Real confirmed ability (Wowpedia): "Maul - Adds damage to the
        # next attack." Modeled as a self-buff preceding a heavy follow-
        # up hit, same pattern used for Verog's Rushing Charge earlier
        # this session.
        ("Claw Swipe", "damage", 30, 0, 0, "physical", {}),
        ("Maul", "buff", 0, 4, 0, "physical",
         {"duration": 1, "self_only": True, "stat_mods": {"attack_power": 28}}),
    ],
    "elder_timberling": [
        # Timberling's elder/boss tier - a real step up over the base
        # ancient_treant kit, matching Stormhide Patriarch/Savannah
        # Patriarch's escalation convention.
        ("Slam", "damage", 34, 0, 0, "physical", {}),
        ("Root Grasp", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -18}}),
        ("Ancient Bark", "buff", 0, 6, 0, "physical",
         {"duration": 5, "self_only": True, "stat_mods": {"armor": 28}}),
    ],
    "dryad_sentinel": [
        ("Thorn Bolt", "damage", 26, 0, 22, "nature", {}),
        ("Entangling Roots", "dot", 10, 3, 20, "nature", {"duration": 3}),
    ],
    "nightsaber_stalker": [
        ("Claw", "damage", 24, 0, 0, "physical", {}),
        ("Pounce", "damage", 36, 3, 0, "physical", {}),
    ],
    "sentinel_scout": [
        ("Glaive Throw", "damage", 25, 0, 0, "physical", {}),
        ("Piercing Shot", "damage", 34, 3, 0, "physical", {}),
    ],
    "wisp": [
        ("Spark", "damage", 18, 0, 16, "nature", {}),
        ("Wisp Heal", "heal", 28, 4, 24, "nature", {}),
    ],
    "timberling": [
        ("Slam", "damage", 24, 0, 0, "physical", {}),
        ("Root Grasp", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -12}}),
    ],
}

# ======================================================================
# FENRIS ISLE / SILVERPINE — real confirmed lore: Lord Godfrey (Wowpedia/
# Warcraft Wiki) wields dual pistols, commands ghouls, and has confirmed
# Cursed Bullets (shadow DoT), Pistol Barrage (cone AoE), Mortal Wound
# (physical DoT + healing reduction). "Lord Godfrey's Remnant" is scaled
# down from his real raid-boss kit to fit this project's power level -
# same 3 signature effects, much smaller numbers. Baron Ashbury is a
# real named Gilnean noble referenced alongside Godfrey in Warcraft
# lore. No other confirmed matches for this cluster's names - kept
# original with authentic Forsaken/worgen/scourge faction flavor.
# ======================================================================
FENRIS_SILVERPINE_KITS = {
    "lord_godfreys_remnant": [
        ("Pistol Shot", "damage", 26, 0, 0, "physical", {}),
        ("Mortal Wound", "dot", 12, 3, 0, "physical", {"duration": 3}),
        ("Cursed Bullets", "dot", 15, 4, 0, "shadow", {"duration": 3}),
        ("Pistol Barrage", "damage", 40, 5, 0, "shadow", {"is_aoe": True}),
    ],
    "baron_ashbury": [
        ("Noble's Blade", "damage", 28, 0, 0, "physical", {}),
        ("Commanding Presence", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    "cursed_villager": [
        ("Frenzied Claw", "damage", 20, 0, 0, "physical", {}),
        ("Wretched Wail", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"attack_power": -10}}),
    ],
    "feral_packmaster": [
        ("Whip Crack", "damage", 24, 0, 0, "physical", {}),
        ("Call the Pack", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "worgen_keeper": [
        ("Feral Slash", "damage", 22, 0, 0, "physical", {}),
        ("Rabid Bite", "dot", 9, 3, 0, "physical", {"duration": 3}),
    ],
    "the_alpha_cur": [
        ("Alpha Bite", "damage", 32, 0, 0, "physical", {}),
        ("Pack Howl", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 22}}),
        ("Savage Rend", "dot", 12, 4, 0, "physical", {"duration": 3}),
    ],
    "corrupted_treant": [
        ("Blighted Slam", "damage", 26, 0, 0, "physical", {}),
        ("Rot", "dot", 10, 3, 0, "magic", {"duration": 3}),
    ],
    "muckmaw": [
        ("Bog Bite", "damage", 30, 0, 0, "physical", {}),
        ("Death Roll", "dot", 13, 4, 0, "physical", {"duration": 3}),
    ],
    "murky_crocolisk": [
        ("Murky Bite", "damage", 24, 0, 0, "physical", {}),
        ("Death Roll", "dot", 10, 4, 0, "physical", {"duration": 3}),
    ],
    "pyrewood_cultist": [
        ("Shadow Bolt", "damage", 24, 0, 20, "shadow", {}),
        ("Curse of Pyrewood", "dot", 10, 3, 18, "shadow", {"duration": 4}),
    ],
    "deathguard_captain": [
        ("Deathguard Strike", "damage", 32, 0, 0, "physical", {}),
        ("Rally the Deathguard", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
        ("Plague Slash", "dot", 12, 4, 0, "physical", {"duration": 3}),
    ],
    "forsaken_patrol": [
        ("Rusty Blade", "damage", 22, 0, 0, "physical", {}),
        ("Reckless Swing", "damage", 32, 3, 0, "physical", {}),
    ],
    "plagued_courier": [
        ("Poisoned Dagger", "damage", 21, 0, 0, "physical", {}),
        ("Plague Vial", "dot", 9, 3, 0, "magic", {"duration": 3}),
    ],
    "the_bloated_one": [
        ("Bloated Slam", "damage", 34, 0, 0, "physical", {}),
        ("Plague Burst", "dot", 15, 4, 0, "magic", {"duration": 3, "is_aoe": True}),
    ],
    "marsh_ooze": [
        ("Acid Splash", "damage", 22, 0, 18, "magic", {}),
        ("Corrosive Touch", "dot", 9, 3, 16, "magic", {"duration": 3}),
    ],
}

# ======================================================================
# TIRISFAL / BRILL / DEATHKNELL — Thurman Agamand is a real confirmed
# NPC (Wowpedia/Warcraft Wiki): a zombie boss at Agamand Mills. High
# Inquisitor Fairbanks and Interrogator Vishas are real confirmed
# Scarlet Crusade bosses (their real location is Scarlet Monastery, not
# Tirisfal open-world - a name/flavor collision like Ursal/Krellian
# earlier) with real confirmed abilities: Fairbanks has Curse of Blood
# (physical vulnerability) and Dispel Magic; Vishas has confirmed
# Immolate (fire DoT). Both kept at their real signature effects, scaled
# to this project's open-world tier rather than a 40-elite dungeon tier.
# ======================================================================
TIRISFAL_KITS = {
    "thurman_agamand": [
        ("Zombie Grasp", "damage", 24, 0, 0, "physical", {}),
        ("Rotting Wail", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"attack_power": -14}}),
        ("Undying Fury", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "high_inquisitor_fairbanks": [
        ("Holy Smite", "damage", 32, 0, 28, "magic", {}),
        ("Curse of Blood", "debuff", 0, 5, 24, "shadow",
         {"duration": 4, "stat_mods": {"armor": -20}}),
        ("Dispel Magic", "debuff", 0, 4, 20, "shadow",
         {"duration": 2, "stat_mods": {"attack_power": -10}}),
    ],
    "interrogator_vishas": [
        ("Interrogator's Blade", "damage", 30, 0, 0, "physical", {}),
        ("Immolate", "dot", 13, 3, 0, "fire", {"duration": 4}),
        ("Brand of Penance", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -18}}),
    ],
    "broodmother_neshka": [
        ("Venomous Sting", "damage", 26, 0, 0, "physical", {}),
        ("Brood Poison", "dot", 11, 3, 0, "magic", {"duration": 4}),
        ("Web Wrap", "debuff", 0, 5, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -16}}),
    ],
    "night_web_spider": [
        ("Fang Bite", "damage", 20, 0, 0, "physical", {}),
        ("Web Spray", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -10}}),
    ],
    "night_web_matriarch": [
        # Fixed from dead hp_mult/atk_mult fields the engine never read -
        # a real step-up kit over base Night Web Spider trash.
        ("Venomous Fang", "damage", 24, 0, 0, "physical", {}),
        ("Brood Web", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -14}}),
    ],
    "young_nightcrawler": [
        ("Nip", "damage", 12, 0, 0, "physical", {}),
        ("Skitter Bite", "damage", 18, 3, 0, "physical", {}),
    ],
    "scarlet_recruit": [
        # Convert/Initiate - the Scarlet Crusade's lowest, freshest
        # tiers, matching a plain trainee before the real Zealot/
        # Defender/Chaplain kits kick in at higher rank.
        ("Recruit's Slash", "damage", 18, 0, 0, "physical", {}),
        ("Zealous Strike", "damage", 27, 3, 0, "physical", {}),
    ],
    "darkeye_bonecaster": [
        ("Shadow Bolt", "damage", 16, 0, 14, "shadow", {}),
        ("Bone Armor", "buff", 0, 5, 12, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 14}}),
    ],
    "balnir_stableboy": [
        ("Undead Kick", "damage", 20, 0, 0, "physical", {}),
        ("Rotting Bite", "dot", 8, 3, 0, "physical", {"duration": 3}),
    ],
    "bleak_worg": [
        ("Bite", "damage", 22, 0, 0, "physical", {}),
        ("Howl", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 12}}),
    ],
    "solliden_farmhand": [
        ("Pitchfork Jab", "damage", 20, 0, 0, "physical", {}),
        ("Rotting Bite", "dot", 8, 3, 0, "physical", {"duration": 3}),
    ],
    "captured_farmer": [
        # Enslaved/captured, not yet undead - a weaker rank-and-file
        # human tier distinct from Solliden Farmhand's zombie flavor.
        ("Farm Tool Swing", "damage", 21, 0, 0, "physical", {}),
        ("Desperate Strike", "damage", 30, 3, 0, "physical", {}),
    ],
}

DUROTAR_OPEN_KITS = {
    # ---- Red Wastes -----------------------------------------------------
    "rustfang_hyena": [
        ("Rending Bite", "damage", 18, 0, 0, "physical", {}),
        ("Pack Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 10}}),
        ("Rake", "dot", 8, 3, 0, "physical", {"duration": 3}),
    ],
    "redtooth": [
        # Old Redtooth, alpha of the Rustfang packs. PLANNED (engine): Howl
        # will call 2 hyenas at ~50% HP.
        ("Alpha Bite", "damage", 28, 0, 0, "physical", {}),
        ("Howl of the Pack", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 16}}),
        ("Hamstring Rake", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "mesa_stonebiter": [
        ("Stone Jaw", "damage", 22, 0, 0, "physical", {}),
        ("Sandstone Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 24}}),
    ],
    # ---- Thunder Ridge --------------------------------------------------
    "static_hatchling": [
        ("Nip", "damage", 14, 0, 0, "physical", {}),
        ("Static Spark", "dot", 7, 3, 0, "nature", {"duration": 3}),
    ],
    "ridge_stormbinder": [
        ("Lightning Lash", "damage", 26, 0, 20, "nature", {}),
        ("Storm Ward", "buff", 0, 6, 16, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
        ("Chain Shock", "damage", 34, 4, 26, "nature", {}),
    ],
    "rumblejaw": [
        # Thunder Ridge named rare. PLANNED (engine): Ground Tremor will stun.
        ("Seismic Bite", "damage", 34, 0, 0, "physical", {}),
        ("Ground Tremor", "damage", 30, 4, 0, "physical", {"is_aoe": True}),
        ("Hardened Plates", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 30}}),
    ],
    # ---- Kolkar Crag ----------------------------------------------------
    "bloodhoof_the_lamed": [
        # Kolkar Crag named rare - a crippled outrider who charges anyway.
        ("Crippled Charge", "damage", 32, 0, 0, "physical", {}),
        ("Rage of the Lamed", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
        ("Trample", "dot", 12, 4, 0, "physical", {"duration": 3}),
    ],
    # ---- Rocktusk Farm --------------------------------------------------
    "rocktusk_farmhand": [
        ("Pitchfork Jab", "damage", 17, 0, 0, "physical", {}),
        ("Thorn Salve", "heal", 12, 5, 0, "nature", {}),
    ],
    "tamed_razorback": [
        ("Gore", "damage", 20, 0, 0, "physical", {}),
        ("Trampling Charge", "damage", 28, 4, 0, "physical", {}),
    ],
    "matron_sowbelly": [
        # Rocktusk Farm named rare - the farm's breeding sow, enormous and furious.
        ("Gore", "damage", 28, 0, 0, "physical", {}),
        ("Sow's Fury", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
        ("Rotting Bile", "dot", 11, 4, 0, "nature", {"duration": 4}),
    ],
    # ---- Scuttle Coast --------------------------------------------------
    "saltcrust_crab": [
        ("Claw Snap", "damage", 16, 0, 0, "physical", {}),
        ("Shell Up", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
    ],
    "murloc_netcaster": [
        ("Net Slash", "damage", 15, 0, 0, "physical", {}),
        ("Tangling Net", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "gillfin_net_cutter": [
        ("Hooked Blade", "damage", 26, 0, 0, "physical", {}),
        ("Rending Net", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
        ("Tidal Mend", "heal", 22, 6, 0, "nature", {}),
    ],
    # ---- Skull Rock Approach -------------------------------------------
    "burning_blade_torchbearer": [
        ("Torch Strike", "damage", 24, 0, 0, "fire", {}),
        ("Ignite", "dot", 12, 3, 0, "fire", {"duration": 3}),
    ],
    "cinder_imp": [
        ("Firebolt", "damage", 20, 0, 12, "fire", {}),
        ("Fel Flicker", "dot", 9, 3, 10, "fire", {"duration": 3}),
    ],
    "houndmaster_kraygh": [
        # Skull Rock Approach named rare. PLANNED (engine): calls 2 Felhounds at ~60%.
        ("Fel Whip", "damage", 30, 0, 22, "shadow", {}),
        ("Rally the Hounds", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
        ("Shadow Brand", "debuff", 0, 4, 18, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
    ],

    # ---- previously missing Durotar kits ---------------------------------
    "quilboar_shaman": [
        ("Earth Bolt", "damage", 20, 0, 14, "nature", {}),
        ("Thorn Ward", "buff", 0, 6, 14, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
        ("Rejuvenating Mud", "heal", 18, 6, 16, "nature", {}),
    ],
    "drowned_sailor": [
        ("Rusted Cutlass", "damage", 16, 0, 0, "physical", {}),
        ("Seawater Retch", "dot", 8, 4, 0, "nature", {"duration": 3}),
    ],
    "felhound": [
        ("Fel Bite", "damage", 26, 0, 0, "shadow", {}),
        ("Mana Burn Howl", "debuff", 0, 5, 0, "shadow",
         {"duration": 3, "stat_mods": {"intellect": -14}}),
        ("Rending Claws", "dot", 11, 4, 0, "physical", {"duration": 3}),
    ],
}

VALLEY_OF_TRIALS_KITS = {
    "broodmother_sarrix": [
        # Scorpid Nest named rare - venom + a brood-protecting shell.
        ("Venomous Sting", "damage", 14, 0, 0, "physical", {}),
        ("Brood Poison", "dot", 6, 3, 0, "magic", {"duration": 4}),
        ("Egg-Guard Carapace", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 12}}),
    ],
    "nest_guardian": [
        # The Den's boss - the first fight in the game that is not a
        # stat-check. Three beats: an armor-up (Hardened Shell), a heavy
        # skewer on a cooldown you can see coming, and a Brood Cry that
        # pumps its own attack so a slow fight gets worse, not easier.
        # PLANNED (engine support not built yet): Brood Cry will also call
        # 2 Cave Skitterers at ~50% HP.
        ("Pincer Crush", "damage", 15, 0, 0, "physical", {}),
        ("Hardened Shell", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 14}}),
        ("Chitin Skewer", "damage", 28, 3, 0, "physical", {}),
        ("Brood Cry", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 10}}),
    ],
    "yarrog_baneshadow": [
        # Burning Blade Coven's boss - a fel caster that fights like one:
        # a curse that weakens the player's offence, a self-heal that
        # punishes slow burst, and a big Fel Eruption on a cooldown.
        # PLANNED (engine support not built yet): Summon Familiars at ~60%
        # and ~30% HP, matching the quest text.
        ("Shadow Bolt", "damage", 16, 0, 14, "shadow", {}),
        ("Baneful Curse", "debuff", 0, 4, 12, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -8}}),
        ("Drain Vitality", "heal", 14, 5, 16, "shadow", {}),
        ("Fel Eruption", "damage", 34, 3, 22, "shadow", {}),
    ],
    "burning_blade_initiate": [
        ("Fel Slash", "damage", 12, 0, 0, "physical", {}),
        ("Dark Zeal", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 8}}),
    ],
    "trailwater_toad": [
        # Trailwater Spring's own creature - a small nature-flavored
        # amphibian distinct from the Scorpid Nest's venom trash, giving
        # the new pond subzone its own identity rather than just reusing
        # Scorpid Worker under a different subzone label. Bulkier/slower
        # form (vermin_sneaky, the heavier vermin template): one solid
        # hop hit, no speed-based mechanic - a toad doesn't web or
        # outmaneuver anything, it just sits and lunges.
        ("Wet Hop", "damage", 14, 0, 0, "physical", {}),
        ("Sticky Tongue", "dot", 5, 3, 0, "physical", {"duration": 3}),
    ],
    "sagewood_sprite": [
        # Sagewood Grove's own creature - a small nature pest distinct
        # from the fel/demon trash in Burning Blade Coven, matching the
        # grove's real-plant flavor rather than the tainted north caves.
        ("Bramble Poke", "damage", 9, 0, 0, "physical", {}),
        ("Sap Drain", "dot", 4, 3, 0, "nature", {"duration": 3}),
    ],
    "claim_spider": [
        # The Overrun Claim's surface spiders - real confirmed lore
        # ("the goldmine to the northwest has been overrun by spiders").
        # Fast/fragile form (vermin_swarm, the lighter vermin template):
        # a quick light bite plus a real speed-debuff web, matching
        # spider agility rather than the toad's bulkier single lunge -
        # same "hit + effect" shape as the toad but a genuinely different
        # fight (DoT-and-tank vs. speed-control), not identical numbers
        # under different names.
        ("Quick Bite", "damage", 8, 0, 0, "physical", {}),
        ("Web Snare", "debuff", 0, 3, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -12}}),
    ],
    "restless_grave_dweller": [
        # Deathknell Graves' own creature - freshly-risen, not yet fully
        # coherent undead at the actual mass-grave starting area,
        # distinct from Shadow Grave's older, more composed Rattlecage
        # Skeleton (crypt-dwellers, longer dead). A weaker, more erratic
        # form: lower single-hit damage but a genuine self-buff (the
        # thing is still finding its footing, then gets more dangerous),
        # rather than Rattlecage's flat physical pair.
        ("Grasping Claw", "damage", 12, 0, 0, "physical", {}),
        ("Rising Fury", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 10}}),
    ],
    "rampart_watchman": [
        # Mor'shan Rampart's own creature - previously this subzone had
        # ZERO creatures of its own, just Harpy Roost's exact roster
        # copy-pasted (no identity distinct from the zone it borrows
        # from). Real WoW confirms Mor'shan Rampart is a Horde border
        # checkpoint, so this is a real defensive orc sentry rather than
        # more harpy trash - a genuinely different fight (a soldier with
        # a spear) at the gate itself, with the harpies remaining as
        # the wildlife that patrols around it.
        ("Spear Thrust", "damage", 22, 0, 0, "physical", {}),
        ("Checkpoint Vigil", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 16}}),
    ],
    "shadow_grave_wight": [
        # Shadow Grave's own creature - previously this crypt subzone
        # had zero creatures unique to it (Rattlecage Skeleton and
        # Wretched Zombie are both used elsewhere too). A genuine
        # crypt-dweller distinct from the shared skeleton/zombie roster:
        # a real drain-life mechanic (a wight feeds off the living),
        # not a plain physical hit like its neighbors.
        ("Withering Touch", "damage", 13, 0, 0, "shadow", {}),
        ("Life Drain", "heal", 10, 3, 0, "shadow", {}),
    ],
    "manor_reaper": [
        # Cold Hearth Manor's own creature - previously this real
        # confirmed farmstead subzone had zero creatures unique to it
        # (Wretched Zombie and Rotting Dead are both shared with other
        # subzones). Real lore ("infested with mindless Scourge
        # zombies") stays zombie-flavored, but with a real farm-tool
        # weapon and a genuine bleed the plain zombies don't have.
        ("Scythe Swing", "damage", 24, 0, 0, "physical", {}),
        ("Harvest Wound", "dot", 10, 3, 0, "physical", {"duration": 4}),
    ],
    # ---- Valley of Trials / Den / Coven diversity pass (2026-10-21) ----
    "dustwind_jackal": [
        # Fast pack hunter: weak bite, but it works itself up.
        ("Snap", "damage", 12, 0, 0, "physical", {}),
        ("Pack Cry", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 6}}),
    ],
    "carrion_vulture": [
        # Carrion feeder: bleeds you slowly, then circles.
        ("Talon Rake", "damage", 13, 0, 0, "physical", {}),
        ("Carrion Rot", "dot", 5, 3, 0, "physical", {"duration": 4}),
    ],
    "sandpincer_crawler": [
        # Armoured scorpid line: soft hit, hard shell.
        ("Pincer Snap", "damage", 14, 0, 0, "physical", {}),
        ("Chitin Plating", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 12}}),
    ],
    "marsh_skimmer": [
        # Trailwater dragonfly: tiny hit, speeds up.
        ("Wing Buzz", "damage", 8, 0, 0, "physical", {}),
        ("Skim", "buff", 0, 3, 0, "physical",
         {"duration": 2, "self_only": True, "stat_mods": {"agility": 10}}),
    ],
    "thornroot_sapling": [
        # Grove guardian: lash then root you down (agility debuff).
        ("Thorn Lash", "damage", 14, 0, 0, "physical", {}),
        ("Entangling Roots", "debuff", 0, 3, 0, "nature",
         {"duration": 2, "stat_mods": {"agility": -12}}),
    ],
    "dust_devil": [
        # Windrift Dunes caster: a gust and a blinding sandstorm that cuts
        # your attack power.
        ("Gritty Gust", "damage", 12, 0, 6, "magic", {}),
        ("Blinding Sand", "debuff", 0, 4, 8, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -7}}),
    ],
    "ember_wisp": [
        # Cinderjaw Wastes caster: fire dot.
        ("Cinder Spark", "damage", 13, 0, 6, "magic", {}),
        ("Smolder", "dot", 6, 3, 8, "magic", {"duration": 3}),
    ],
    "den_spinner": [
        # The Den's web-spinner: bite plus a speed-sapping web.
        ("Quick Bite", "damage", 9, 0, 0, "physical", {}),
        ("Sticky Web", "debuff", 0, 3, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -10}}),
    ],
    "husk_crawler": [
        # The Den's husk-carrier: mandible rend that bleeds.
        ("Rending Mandible", "damage", 13, 0, 0, "physical", {}),
        ("Brittle Husk Gash", "dot", 5, 3, 0, "physical", {"duration": 3}),
    ],
    "egg_tender": [
        # The Den's support mob - mends nest-mates and itself. Kill first.
        ("Tender Strike", "damage", 11, 0, 0, "physical", {}),
        ("Nurture", "heal", 12, 4, 0, "nature", {}),
    ],
    "burning_blade_acolyte": [
        # Coven healer-caster: Fel Flame plus a self mend.
        ("Fel Flame", "damage", 15, 0, 12, "magic", {}),
        ("Blade Mending", "heal", 13, 4, 14, "shadow", {}),
    ],
    "coven_ritual_guard": [
        # Coven bruiser: heavy cleaver, hardens up.
        ("Rusted Cleaver", "damage", 18, 0, 0, "physical", {}),
        ("Fel Fortitude", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 14}}),
    ],
    "fel_pup": [
        # Fix: creatures.json pointed Fel Pup at a kit named "felhound" that
        # never existed (spawn KeyError). Light pack biter.
        ("Nip", "damage", 12, 0, 0, "physical", {}),
        ("Fel Frenzy", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 7}}),
    ],
    # ---- named rares ----
    "old_tusk": [
        ("Gore", "damage", 20, 0, 0, "physical", {}),
        ("Bloodied Charge", "damage", 30, 3, 0, "physical", {}),
        ("Thick Hide", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 10}}),
    ],
    "old_gulpjaw": [
        ("Crushing Gulp", "damage", 18, 0, 0, "physical", {}),
        ("Bog Belch", "dot", 7, 3, 0, "nature", {"duration": 4}),
        ("Swollen Hide", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 12}}),
    ],
    "bramblethorn_the_ancient": [
        ("Thorn Lash", "damage", 18, 0, 0, "physical", {}),
        ("Rooting Grasp", "debuff", 0, 3, 0, "nature",
         {"duration": 2, "stat_mods": {"agility": -14}}),
        ("Bark Skin", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 18}}),
        ("Rejuvenating Sap", "heal", 14, 5, 0, "nature", {}),
    ],
    "sandfang": [
        ("Snap", "damage", 16, 0, 0, "physical", {}),
        ("Gnashing Rake", "dot", 7, 3, 0, "physical", {"duration": 3}),
        ("Pack Cry", "buff", 0, 4, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 9}}),
    ],
    "smolderhide": [
        ("Scorching Bite", "damage", 24, 0, 0, "physical", {}),
        ("Molten Hide", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 16}}),
        ("Ashen Breath", "dot", 9, 3, 0, "magic", {"duration": 3}),
    ],
}

BLACKFATHOM_DEEPS_KITS = {
    "ghamoo_ra": [
        # Real confirmed ability (Icy Veins/Warcraft Tavern): "Ghamoo-ra
        # has only one ability, Trample" - a random-party-member hit. SoD
        # lore also describes a periodic Aqua Shell armor buff. Modeled
        # as Trample (basic) + a self-armor buff on a cooldown.
        ("Trample", "damage", 44, 0, 0, "physical", {}),
        ("Aqua Shell", "buff", 0, 6, 0, "physical",
         {"duration": 5, "self_only": True, "stat_mods": {"armor": 26}}),
    ],
    "lady_sarevess": [
        # Real confirmed ability: Forked Lightning, "very similar to
        # chain lightning... if you have more than one melee on her it
        # will hit all of them" - modeled as a real AoE nature hit.
        ("Naga Fury", "damage", 40, 0, 0, "physical", {}),
        ("Forked Lightning", "damage", 34, 3, 30, "nature", {"is_aoe": True}),
        ("Tidal Ward", "buff", 0, 5, 24, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 20}}),
    ],
    # The remaining Blackfathom creatures had ability_kit ids in
    # creatures.json with NO matching kit, so spawning any of them raised
    # KeyError (Monster.__init__) - five of seven bosses plus the Murloc
    # Hydra trash were un-fightable. Modeled on their real Classic abilities.
    "murloc_hydra": [
        ("Hydra Bite", "damage", 24, 0, 0, "physical", {}),
        ("Spit Venom", "dot", 9, 3, 0, "magic", {"duration": 3}),
    ],
    "gelihast": [
        ("Tidal Bolt", "damage", 30, 0, 18, "nature", {}),
        ("Fishing Net", "debuff", 0, 4, 12, "physical",
         {"duration": 2, "stat_mods": {"agility": -20}}),
    ],
    "lorgus_jett": [
        ("Stormcaller's Strike", "damage", 38, 0, 0, "physical", {}),
        ("Lightning Shield", "buff", 0, 5, 0, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 18}}),
        ("Lightning Bolt", "damage", 42, 3, 0, "nature", {}),
    ],
    "old_serrakis": [
        ("Crushing Claw", "damage", 44, 0, 0, "physical", {}),
        ("Thundercrack", "damage", 34, 3, 0, "physical", {"is_aoe": True}),
    ],
    "twilight_lord_kelris": [
        ("Shadow Bolt", "damage", 34, 0, 18, "shadow", {}),
        ("Mind Blast", "damage", 46, 2, 22, "shadow", {}),
        ("Mind Sleep", "debuff", 0, 5, 20, "shadow",
         {"duration": 2, "stat_mods": {"agility": -22, "attack_power": -10}}),
    ],
    "akumai": [
        ("Venomous Bite", "damage", 46, 0, 0, "physical", {}),
        ("Poison Cloud", "dot", 18, 3, 0, "nature", {"duration": 4, "is_aoe": True}),
        ("Frenzied Rage", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 28}}),
    ],
}

WAILING_CAVERNS_KITS = {
    "fanglord_druid": [
        ("Lightning Bolt", "damage", 40, 0, 35, "nature", {}),
        ("Healing Touch", "heal", 55, 4, 45, "nature", {}),
        ("Druid's Slumber", "debuff", 0, 6, 40, "nature",
         {"duration": 2, "stat_mods": {"attack_power": -999}}),
    ],
    "verdan_the_everliving": [
        # Real kit: heavy melee hits (guides specifically call out very
        # high melee damage even through warrior shields) plus Grasping
        # Vines - an uninterruptible root+stun AoE, and a Stomp. Modeled
        # as a debuff (root = severe agility penalty) rather than a stun
        # kind since this engine has no separate stun mechanic; the
        # heavy -agility approximates "can't act effectively" without
        # a hard skip-turn the combat engine doesn't support.
        ("Crushing Blow", "damage", 50, 0, 0, "physical", {}),
        ("Grasping Vines", "debuff", 0, 6, 0, "physical",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -999}}),
        ("Stomp", "damage", 38, 3, 0, "physical", {"is_aoe": True}),
        ("Everliving Bark", "buff", 0, 7, 0, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 55}}),
    ],
    "mutanus_the_devourer": [
        # Real kit: Fear + Sleep (Basin Wiki), Thundercrack AoE (multiple
        # sources), partial Shadow resistance noted by Vanilla WoW Wiki -
        # approximated here as high magic_resist via stat_overrides on
        # the creature entry rather than a literal damage-type immunity
        # this engine doesn't model.
        ("Devour", "damage", 55, 0, 0, "physical", {}),
        ("Thundercrack", "damage", 44, 3, 0, "magic", {"is_aoe": True}),
        ("Nightmare Sleep", "debuff", 0, 5, 0, "magic",
         {"duration": 2, "stat_mods": {"attack_power": -999}}),
        ("Terrifying Screech", "debuff", 0, 6, 0, "magic",
         {"duration": 3, "is_aoe": True, "stat_mods": {"attack_power": -45, "agility": -30}}),
    ],
    "skum": [
        # Confirmed "Thunder Lizard" type - reuses thunder_lizard's real
        # kit shape (Slam/Lightning Nova/Thick Hide) rather than
        # inventing a near-identical fourth lizard kit.
        ("Slam", "damage", 34, 0, 0, "physical", {}),
        ("Lightning Nova", "damage", 40, 3, 0, "magic", {"is_aoe": True}),
        ("Thick Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 24}}),
        ("Thunder Roar", "debuff", 0, 6, 0, "nature",
         {"duration": 3, "is_aoe": True, "stat_mods": {"attack_power": -35}}),
    ],
}

# Wailing Caverns content pass (2026-10-21): unique kits for the Fanglords + Kresh, trash kits for the creatures whose
# "kit" key was dead (never loaded), and the new WC trash/rares.  Power is flat per the L16-24 band (trash 20-34,
# bosses 44-70 first ability).
WAILING_CONTENT_KITS = {
    # ---- bosses ----------------------------------------------------------------------------------------------------
    "lady_anacondra": [
        ("Lightning Bolt", "damage", 44, 0, 24, "nature", {}),
        ("Healing Touch", "heal", 90, 5, 40, "nature", {}),
        ("Drowsy Dream", "debuff", 0, 5, 30, "nature", {"duration": 3, "stat_mods": {"agility": -30}}),
    ],
    "lord_cobrahn": [
        ("Venom Spit", "damage", 46, 0, 0, "nature", {}),
        ("Poison Cloud", "dot", 20, 4, 0, "nature", {"duration": 4, "is_aoe": True}),
        ("Serpent Form", "buff", 0, 7, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 48}}),
        ("Cobrahn's Lightning", "damage", 62, 4, 30, "nature", {}),
    ],
    "kresh": [
        ("Shell Slam", "damage", 42, 0, 0, "physical", {}),
        ("Withdraw", "buff", 0, 7, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 90}}),
        ("Water Jet", "damage", 58, 4, 0, "nature", {}),
        ("Barnacle Rend", "dot", 18, 5, 0, "physical", {"duration": 4}),
    ],
    "lord_pythas": [
        ("Lightning Bolt", "damage", 48, 0, 26, "nature", {}),
        ("Thunderclap", "debuff", 0, 5, 0, "physical", {"duration": 3, "is_aoe": True, "stat_mods": {"attack_power": -40}}),
        ("Slumber", "debuff", 0, 6, 30, "nature", {"duration": 2, "stat_mods": {"agility": -38}}),
        ("Healing Touch", "heal", 110, 6, 45, "nature", {}),
    ],
    "lord_serpentis": [
        ("Lightning Bolt", "damage", 50, 0, 26, "nature", {}),
        ("Wrath of the Fang", "dot", 22, 4, 28, "nature", {"duration": 4}),
        ("Serpent's Gaze", "debuff", 0, 5, 28, "nature", {"duration": 3, "stat_mods": {"armor": -42}}),
        ("Fangbound Ward", "buff", 0, 8, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 50}}),
    ],
    # ---- rares -----------------------------------------------------------------------------------------------------
    "old_hissfang": [
        ("Crushing Coil", "damage", 38, 0, 0, "physical", {}),
        ("Venom Fangs", "dot", 17, 3, 0, "nature", {"duration": 4}),
        ("Hiss", "debuff", 0, 5, 0, "nature", {"duration": 3, "stat_mods": {"attack_power": -30}}),
    ],
    "drowsyroot_the_dreamer": [
        ("Dream Thorn", "damage", 40, 0, 24, "nature", {}),
        ("Lullaby", "debuff", 0, 5, 26, "nature", {"duration": 2, "stat_mods": {"attack_power": -999}}),
        ("Rootmend", "heal", 80, 5, 36, "nature", {}),
    ],
    "sporeback_the_bloated": [
        ("Bloated Slam", "damage", 40, 0, 0, "physical", {}),
        ("Spore Cloud", "dot", 18, 4, 0, "nature", {"duration": 4, "is_aoe": True}),
        ("Swell", "buff", 0, 7, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 55}}),
    ],
    # ---- previously-dead-kit trash (L16-22) ------------------------------------------------------------------------
    "deviate_python": [
        ("Constrict", "damage", 24, 0, 0, "physical", {}),
        ("Python Venom", "dot", 10, 3, 0, "nature", {"duration": 4}),
    ],
    "deviate_ooze": [
        ("Acid Splash", "damage", 25, 0, 14, "nature", {}),
        ("Corroding Touch", "debuff", 0, 4, 14, "nature", {"duration": 3, "stat_mods": {"armor": -22}}),
    ],
    "deviate_raptor": [
        ("Raptor Strike", "damage", 26, 0, 0, "physical", {}),
        ("Savage Leap", "damage", 33, 4, 0, "physical", {}),
    ],
    "deviate_crocolisk": [
        ("Gator Bite", "damage", 27, 0, 0, "physical", {}),
        ("Death Roll", "dot", 11, 4, 0, "physical", {"duration": 3}),
    ],
    "druid_fang": [
        ("Wrath", "damage", 26, 0, 16, "nature", {}),
        ("Rejuvenating Moss", "heal", 42, 4, 24, "nature", {}),
        ("Entangling Roots", "debuff", 0, 5, 18, "nature", {"duration": 3, "stat_mods": {"agility": -24}}),
    ],
    "dreadfang": [
        ("Fang Bite", "damage", 25, 0, 0, "physical", {}),
        ("Dread Venom", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    # ---- new trash ------------------------------------------------------------------------------------------------
    "fang_initiate": [
        ("Fang Strike", "damage", 25, 0, 0, "physical", {}),
        ("Initiate's Ward", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
    ],
    "nightmare_wisp": [
        ("Dream Bolt", "damage", 28, 0, 18, "arcane", {}),
        ("Lull", "debuff", 0, 5, 18, "arcane", {"duration": 3, "stat_mods": {"attack_power": -26}}),
    ],
    "deviate_broodling": [
        ("Nip", "damage", 20, 0, 0, "physical", {}),
        ("Swarm Frenzy", "buff", 0, 6, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
}

# ======================================================================
# DEMONS
# ======================================================================
DEMON_KITS = {
    "demon_imp": [
        ("Firebolt", "damage", 18, 0, 16, "magic", {}),
        ("Immolate", "dot", 8, 3, 28, "magic", {"duration": 4}),
    ],
    "demon_hound": [
        ("Rend", "damage", 21, 0, 0, "physical", {}),
        ("Mana Burn", "debuff", 0, 3, 0, "magic",
         {"duration": 3, "stat_mods": {"intellect": -14}}),
        ("Savage Lash", "damage", 32, 3, 0, "physical", {}),
    ],
    "demon_felguard": [
        ("Cleave", "damage", 24, 0, 0, "physical", {}),
        ("Fel Strike", "damage", 36, 3, 0, "physical", {}),
    ],
}

# ======================================================================
# ELEMENTALS
# ======================================================================
ELEMENTAL_KITS = {
    "elemental_fire": [
        ("Fire Blast", "damage", 22, 0, 20, "magic", {}),
        ("Fireball", "damage", 34, 2, 42, "magic", {}),
        ("Scorch", "dot", 8, 4, 28, "magic", {"duration": 3}),
    ],
    "elemental_water": [
        ("Water Bolt", "damage", 21, 0, 20, "magic", {}),
        ("Tidal Wave", "damage", 33, 3, 42, "magic", {}),
        ("Elemental Ward", "buff", 0, 5, 30, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 30}}),
    ],
    "elemental_earth": [
        ("Crush", "damage", 24, 0, 0, "physical", {}),
        ("Stone Shatter", "damage", 36, 3, 35, "magic", {}),
        ("Stoneskin", "buff", 0, 5, 28, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
    ],
}

# ======================================================================
# AQUATIC — murlocs, naga
# ======================================================================
AQUATIC_KITS = {
    "murloc_hunter": [
        ("Spear Jab", "damage", 18, 0, 0, "physical", {}),
        ("Water Jet", "damage", 28, 3, 22, "magic", {}),
    ],
    "murloc_oracle": [
        ("Water Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Tidal Mending", "heal", 42, 3, 36, "magic", {}),
        ("Chilling Wave", "debuff", 0, 4, 28, "magic",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "naga_warrior": [
        ("Trident Thrust", "damage", 22, 0, 0, "physical", {}),
        ("Tail Sweep", "damage", 34, 3, 0, "physical", {}),
    ],
    "sea_hag": [
        ("Hex Bolt", "damage", 27, 0, 27, "magic", {}),
        ("Curse of the Tides", "dot", 13, 3, 13, "magic", {"duration": 3}),
    ],
    "crab_giant": [
        # Sunken Grotto of the Deep mini-boss (Crab Den). Pincer Crush is
        # the free basic attack; Shell Harden is a defensive self-buff
        # (armor spike, matches the Thick Hide pattern) that makes the
        # fight drag if the player doesn't burn cooldowns through it;
        # Scuttle is a short evasive buff on top so the crab occasionally
        # dodges a beat instead of just tanking hits behind its shell.
        ("Pincer Crush", "damage", 26, 0, 0, "physical", {}),
        ("Shell Harden", "buff", 0, 5, 0, "physical",
         {"duration": 4, "stat_mods": {"armor": 24}, "self_only": True}),
        ("Scuttle", "buff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": 14}, "self_only": True}),
    ],
    "naga_shrine_guardian": [
        # Sunken Grotto of the Deep main boss (naga statue). Naga Warrior's
        # melee kit (Trident Thrust / Tail Sweep AoE) plus a hex/curse
        # caster layer on top so the fight has a magic-damage track the
        # player has to heal/mitigate through in addition to the physical
        # hits - "Naga Warrior + a caster layer" per spec.
        ("Trident Thrust", "damage", 24, 0, 0, "physical", {}),
        ("Tail Sweep", "damage", 36, 3, 0, "physical", {"is_aoe": True}),
        ("Shrine Curse", "dot", 16, 4, 20, "magic", {"duration": 3}),
        ("Riptide Hex", "debuff", 0, 5, 24, "magic",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "naga_ruin_warden": [
        # Echo Isles' Naga Ruins (new area, this session). Distinct from
        # naga_shrine_guardian (Sunken Grotto of the Deep's own boss) -
        # same naga-guardian shape (melee + a hex layer) but built around
        # a stacking debuff instead of a DoT+slow pair, so the two naga
        # bosses don't play identically even sharing a faction.
        ("Trident Thrust", "damage", 23, 0, 0, "physical", {}),
        ("Tidal Slam", "damage", 33, 3, 0, "physical", {"is_aoe": True}),
        ("Weakening Curse", "debuff", 0, 4, 22, "magic",
         {"duration": 4, "stat_mods": {"armor": -16}}),
    ],
    "naga_coastguard": [
        # Trash tier for Naga Ruins - naga_warrior's melee shape plus a
        # light hex bolt so the subzone doesn't read as pure physical
        # like Troll Camps already does.
        ("Trident Thrust", "damage", 21, 0, 0, "physical", {}),
        ("Hex Bolt", "damage", 25, 3, 20, "magic", {}),
    ],
    "reef_predator": [
        # Razorjaw Reef trash (new area, this session) - reuses
        # crocolisk's death-roll DoT shape (same reef-predator family)
        # with a bleed instead of a flat DoT so repeated hits stack
        # rather than refresh, giving the reef a slightly nastier bite
        # than Durotar's river crocolisks.
        ("Razor Bite", "damage", 24, 0, 0, "physical", {}),
        ("Thrashing Bleed", "dot", 11, 3, 0, "physical", {"duration": 3}),
    ],
}

# ======================================================================
# UNDEAD / SCOURGE — plague, bone, frost. Distinct from Scarlet holy.
# ======================================================================
UNDEAD_KITS = {
    "undead_ghoul": [
        ("Rotting Strike", "damage", 19, 0, 0, "physical", {}),
        ("Disease Bite", "dot", 7, 3, 0, "magic", {"duration": 4}),
        ("Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "undead_skeleton": [
        ("Bone Slash", "damage", 19, 0, 0, "physical", {}),
        ("Bone Shield", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 24}}),
    ],
    "undead_pirate_captain": [
        # Sunken Grotto of the Deep mini-boss (Shipwreck Cove) - the twin
        # to crab_giant on the opposite fork. Deliberately a different
        # shape: a rotting DoT instead of the crab's clean physical hits,
        # and a debuff (cursed blade weakening the target's own attack)
        # instead of a self-buff, so the two mini-bosses read as distinct
        # fights rather than the same kit with a new name.
        ("Cutlass Slash", "damage", 25, 0, 0, "physical", {}),
        ("Rotting Wound", "dot", 9, 3, 0, "magic", {"duration": 4}),
        ("Cursed Blade", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"attack_power": -12}}),
    ],
    "undead_bonecaster": [
        ("Shadow Bolt", "damage", 20, 0, 18, "magic", {}),
        ("Drain Life", "heal", 34, 3, 30, "magic", {}),
        ("Bone Armor", "buff", 0, 5, 26, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 26}}),
    ],
    "undead_banshee": [
        ("Wail", "damage", 21, 0, 20, "magic", {}),
        ("Terrifying Screech", "debuff", 0, 4, 28, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
        ("Drain Life", "heal", 34, 3, 30, "magic", {}),
    ],
    "undead_plaguebearer": [
        ("Plague Strike", "damage", 20, 0, 0, "physical", {}),
        ("Contagion", "dot", 9, 3, 0, "magic", {"duration": 4}),
    ],
    "scourge_abomination": [
        ("Meat Hook", "damage", 34, 0, 0, "physical", {}),
        ("Disease Cloud", "dot", 13, 3, 0, "magic", {"duration": 4}),
        ("Bone Shatter", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -20}}),
        ("Frenzy", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    "scourge_necromancer": [
        ("Shadow Bolt", "damage", 27, 0, 14, "magic", {}),
        ("Unholy Blight", "dot", 11, 3, 18, "magic", {"duration": 4}),
        ("Unholy Frenzy", "buff", 0, 5, 18, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    "scourge_lich": [
        ("Frostbolt", "damage", 23, 0, 20, "magic", {}),
        ("Frost Nova", "debuff", 0, 4, 32, "magic",
         {"duration": 3, "stat_mods": {"agility": -18}}),
        ("Death Coil", "heal", 44, 3, 40, "magic", {}),
    ],
    "undead_zombie": [
        ("Rotting Claw", "damage", 18, 0, 0, "physical", {}),
        ("Retch", "dot", 7, 4, 0, "magic", {"duration": 3}),
    ],
    "drowned_crewman": [
        # The Lost Fleet's trash (new Echo Isles area, this session) -
        # drowned_sailor's musket shape (Drowned Deckhand, Scuttle
        # Coast) but with a cutlass/bleed melee swap so the fleet's
        # crew don't play identically to Deckhand despite the shared
        # "waterlogged sailor" flavor.
        ("Waterlogged Cutlass", "damage", 22, 0, 0, "physical", {}),
        ("Barnacle Scrape", "dot", 8, 3, 0, "physical", {"duration": 3}),
    ],
    "fleet_captain": [
        # The Lost Fleet's boss - distinct from Undead Pirate Captain
        # (Sunken Grotto of the Deep's own boss): a curse/debuff caster
        # layer instead of a rotting-DoT melee hybrid, so the two
        # undead-pirate bosses read as different fights, not a reskin.
        ("Waterlogged Cutlass", "damage", 26, 0, 0, "physical", {}),
        ("Captain's Curse", "debuff", 0, 4, 0, "physical",
         {"duration": 4, "stat_mods": {"attack_power": -18}}),
        ("Call the Crew", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
}



# ======================================================================
# SILVERPINE DUNGEONS — Widow's Lair + Shadowfang Keep. Every creature in
# these two dungeons used a dead "kit" key in creatures.json (the loader
# only reads "ability_kit") and most of those kit ids never existed, so
# every fight here ran on bare template defaults. Real kits for all of them.
# ======================================================================
SILVERPINE_DUNGEON_KITS = {
    # --- Widow's Lair ---
    "giant_spider": [
        ("Fang Bite", "damage", 20, 0, 0, "physical", {}),
        ("Web Spray", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -10}}),
    ],
    "spider_cultist": [
        ("Shadow Bolt", "damage", 18, 0, 10, "shadow", {}),
        ("Venom Curse", "dot", 8, 3, 12, "shadow", {"duration": 3}),
    ],
    "broodmother_silka": [
        ("Venomous Fang", "damage", 30, 0, 0, "physical", {}),
        ("Brood Poison", "dot", 13, 3, 0, "magic", {"duration": 4}),
        ("Web Wrap", "debuff", 0, 5, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -16}}),
    ],
    "weaver_skitter": [
        ("Silk Lash", "damage", 32, 0, 0, "physical", {}),
        ("Entangling Silk", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -18}}),
        ("Skitter Frenzy", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "matriarch_velaxis": [
        ("Widow's Bite", "damage", 38, 0, 0, "physical", {}),
        ("Necrotic Venom", "dot", 16, 3, 0, "shadow", {"duration": 4}),
        ("Smothering Web", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -16}}),
        ("Brood Call", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    # --- Shadowfang Keep ---
    "forsaken_warrior": [
        ("Rusty Cleave", "damage", 24, 0, 0, "physical", {}),
        ("Undying Resolve", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 14}}),
    ],
    "forsaken_knight": [
        ("Lance Thrust", "damage", 28, 0, 0, "physical", {}),
        ("Shield Bash", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"attack_power": -10}}),
    ],
    "worgen_warrior": [
        ("Savage Claw", "damage", 26, 0, 0, "physical", {}),
        ("Rend Flesh", "dot", 11, 3, 0, "physical", {"duration": 3}),
    ],
    "rethilgore": [
        ("Savage Bite", "damage", 40, 0, 0, "physical", {}),
        ("Rend", "dot", 16, 3, 0, "physical", {"duration": 4}),
        ("Kennel Frenzy", "damage", 30, 3, 0, "physical", {"is_aoe": True}),
        ("Howl of Rage", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 24}}),
    ],
    "razorclaw": [
        ("Butcher's Cleave", "damage", 40, 0, 0, "physical", {}),
        ("Gushing Wound", "dot", 17, 3, 0, "physical", {"duration": 4}),
        ("Meat Hook", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"armor": -22}}),
        ("Bloodlust", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 26}}),
    ],
    "baron_silverlaine": [
        ("Noble's Strike", "damage", 40, 0, 0, "physical", {}),
        ("Cursed Blood", "dot", 15, 3, 0, "shadow", {"duration": 4}),
        ("Banshee Wail", "damage", 30, 3, 0, "shadow", {"is_aoe": True}),
        ("Veil of Shadow", "debuff", 0, 4, 0, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
    ],
    "fenrus_devourer": [
        ("Crushing Bite", "damage", 44, 0, 0, "physical", {}),
        ("Toxic Spittle", "dot", 18, 3, 0, "nature", {"duration": 4}),
        ("Devour", "damage", 54, 3, 0, "physical", {}),
        ("Devouring Rage", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 26}}),
    ],
    "archmage_arugal": [
        ("Arcane Bolt", "damage", 40, 0, 12, "magic", {}),
        ("Void Bolt", "damage", 52, 2, 18, "shadow", {}),
        ("Curse of the Wolf", "debuff", 0, 4, 15, "shadow",
         {"duration": 3, "stat_mods": {"agility": -18}}),
        ("Arugal's Curse", "dot", 22, 3, 18, "shadow", {"duration": 4}),
    ],
}

# Durotar cave residents (2026-10-21 cave pass). First ability of every kit is a
# 0-cd basic attack (kit_to_json contract).
DUROTAR_CAVE_KITS = {
    # ---- Dustwind Cave (scorpid burrow) ---------------------------------
    "burrow_stalker": [
        ("Ambush Sting", "damage", 18, 0, 0, "physical", {}),
        ("Paralytic Venom", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -12}}),
    ],
    "hive_carapace_guard": [
        ("Pincer Slam", "damage", 17, 0, 0, "physical", {}),
        ("Chitin Plating", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    # ---- Tiragarde Keep -------------------------------------------------
    "stranded_cannoneer": [
        ("Powder Shot", "damage", 20, 0, 0, "physical", {}),
        ("Grapeshot Volley", "damage", 26, 4, 0, "physical", {"is_aoe": True}),
    ],
    "ships_surgeon": [
        ("Scalpel Jab", "damage", 14, 0, 6, "physical", {}),
        ("Field Dressing", "heal", 26, 4, 12, "magic", {}),
        ("Bad Anesthetic", "dot", 6, 3, 8, "magic", {"duration": 3}),
    ],
    # ---- Drygulch Ravine ------------------------------------------------
    "roost_warden": [
        ("Talon Rake", "damage", 20, 0, 0, "physical", {}),
        ("Wing Buffet", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -14}}),
    ],
    "gale_caller": [
        ("Wind Slash", "damage", 26, 0, 10, "nature", {}),
        ("Choking Gust", "dot", 10, 3, 14, "nature", {"duration": 3}),
        ("Cyclone Veil", "buff", 0, 5, 12, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
    ],
    # ---- Thunder Ridge --------------------------------------------------
    "thunderbrood_guardian": [
        ("Tail Slam", "damage", 26, 0, 0, "physical", {}),
        ("Static Hide", "buff", 0, 5, 0, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 24}}),
        ("Thunderclap", "debuff", 0, 5, 0, "nature",
         {"duration": 3, "is_aoe": True, "stat_mods": {"agility": -16}}),
    ],
    "thunder_broodmother": [
        # Cave boss. PLANNED (engine): Brood Roar will call 2 Static
        # Hatchlings each time it is cast.
        ("Stormclaw Rend", "damage", 36, 0, 0, "physical", {}),
        ("Brood Roar", "buff", 0, 6, 0, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
        ("Chain Lightning", "damage", 44, 4, 0, "nature", {"is_aoe": True}),
        ("Static Nest", "dot", 15, 4, 0, "nature", {"duration": 4}),
    ],
    # ---- Sunken Grotto of the Deep --------------------------------------
    "naga_coralspeaker": [
        ("Tidal Bolt", "damage", 28, 0, 12, "frost", {}),
        ("Mending Tide", "heal", 34, 5, 18, "magic", {}),
        ("Riptide", "dot", 12, 3, 14, "frost", {"duration": 3}),
    ],
    "drowned_buccaneer": [
        ("Rusted Cutlass", "damage", 24, 0, 0, "physical", {}),
        ("Boarding Hook", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
        ("Dead Man's Grit", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 20}}),
    ],
}

# ======================================================================
# RAGEFIRE CHASM content pass (2026-10-21) - bosses, rares, new trash.
# Oggleflint / Taragaman / Jergosh / Voidwalker Minion previously had NO kit.
# Planned summon hooks (engine work later): Oggleflint "Warband Horn" (2 troggs),
# Taragaman "Lava Spawn" (cinder adds from the lake), Jergosh "Invoke Voidwalker".
# ======================================================================
RAGEFIRE_CONTENT_KITS = {
    "oggleflint": [
        ("Cleave", "damage", 28, 0, 0, "physical", {}),
        ("Warband Bellow", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 30}}),
        ("Boulder Maul", "damage", 46, 3, 0, "physical", {}),
        ("Crushing Roar", "debuff", 0, 4, 0, "physical",
         {"duration": 4, "stat_mods": {"armor": -18}}),
    ],
    "taragaman_the_hungerer": [
        ("Fire Nova", "damage", 30, 0, 0, "magic", {}),
        ("Hungering Flames", "dot", 14, 3, 0, "magic", {"duration": 4}),
        ("Molten Hide", "buff", 0, 6, 0, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 30, "magic_resistance": 20}}),
        ("Lava Burst", "damage", 52, 4, 0, "magic", {}),
    ],
    "jergosh_the_invoker": [
        ("Shadow Bolt", "damage", 34, 0, 30, "magic", {}),
        ("Immolate", "dot", 13, 3, 34, "magic", {"duration": 4}),
        ("Curse of Agony", "dot", 11, 4, 30, "magic", {"duration": 5}),
        ("Searing Chains", "debuff", 0, 5, 26, "magic",
         {"duration": 4, "stat_mods": {"agility": -18, "attack_power": -12}}),
        ("Dark Mending", "heal", 70, 6, 45, "magic", {}),
    ],
    "void_construct": [
        ("Void Bolt", "damage", 24, 0, 18, "magic", {}),
        ("Consuming Gaze", "debuff", 0, 4, 22, "magic",
         {"duration": 3, "stat_mods": {"intellect": -12}}),
    ],
    "ragefire_digger": [
        ("Pick Throw", "damage", 31, 0, 0, "physical", {}),
        ("Rending Pick", "dot", 9, 3, 0, "physical", {"duration": 4}),
    ],
    "trogg_skullcrusher": [
        ("Skull Crush", "damage", 34, 0, 0, "physical", {}),
        ("Shattering Blow", "debuff", 0, 4, 0, "physical",
         {"duration": 4, "stat_mods": {"armor": -14}}),
        ("Rampage", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    "searing_blade_pyromancer": [
        ("Fireball", "damage", 36, 0, 30, "magic", {}),
        ("Pyroblaze", "dot", 12, 3, 32, "magic", {"duration": 4}),
        ("Flame Ward", "buff", 0, 6, 28, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 25}}),
    ],
    "searing_blade_wardpriest": [
        ("Searing Smite", "damage", 26, 0, 20, "magic", {}),
        ("Blood Mending", "heal", 62, 3, 40, "magic", {}),
        ("Dark Fortitude", "buff", 0, 6, 24, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "cinder_salamander": [
        ("Searing Bite", "damage", 25, 0, 0, "magic", {}),
        ("Ember Spit", "dot", 10, 3, 0, "magic", {"duration": 4}),
    ],
    "grulgash_pitbreaker": [
        ("Pit-Hammer", "damage", 32, 0, 0, "physical", {}),
        ("Quake Slam", "damage", 48, 3, 0, "physical", {}),
        ("Miner's Fury", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 22, "armor": 15}}),
    ],
    "cinderfang": [
        ("Searing Fangs", "damage", 30, 0, 0, "magic", {}),
        ("Cinderstorm", "dot", 13, 3, 0, "magic", {"duration": 4}),
        ("Ember Frenzy", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 24, "agility": 12}}),
    ],
    "zhurra_bloodhex": [
        ("Shadow Bolt", "damage", 31, 0, 28, "magic", {}),
        ("Bloodhex", "dot", 12, 3, 30, "magic", {"duration": 5}),
        ("Hex of Weakness", "debuff", 0, 5, 26, "magic",
         {"duration": 4, "stat_mods": {"attack_power": -18}}),
        ("Blood Mending", "heal", 64, 5, 42, "magic", {}),
    ],
}


# ======================================================================
# ECHO ISLES CONTENT PASS (2026-10-21) - wading creatures for the five
# shallow-water subzones, jungle/beach additions, Hollow trolls and the
# six named rares.  Every kit has its own shape (no reskins of reef_predator).
# ======================================================================
ECHO_CONTENT_KITS = {
    # ---- Isle Interior / beaches ---------------------------------------
    "coconut_crab": [
        ("Crushing Claw", "damage", 22, 0, 0, "physical", {}),
        ("Husk Armor", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 26}}),
    ],
    "isle_screecher": [
        ("Talon Rake", "damage", 19, 0, 0, "physical", {}),
        ("Shrill Cry", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"attack_power": -12}}),
    ],
    # ---- Troll Camps / Zalazane's Hollow -------------------------------
    "fetish_carver": [
        ("Bone Hex", "damage", 22, 0, 18, "magic", {}),
        ("Mending Fetish", "heal", 40, 3, 30, "nature", {}),
    ],
    "hollow_skullbreaker": [
        ("Skull Crack", "damage", 27, 0, 0, "physical", {}),
        ("Dazing Blow", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    # ---- Wreck Shallows -------------------------------------------------
    "wreck_scavenger": [
        ("Pincer Pull", "damage", 21, 0, 0, "physical", {}),
        ("Rusted Snap", "dot", 9, 3, 0, "physical", {"duration": 3}),
    ],
    "bilge_eel": [
        ("Eel Bite", "damage", 20, 0, 0, "physical", {}),
        ("Static Jolt", "damage", 30, 3, 0, "nature", {}),
    ],
    # ---- Drowned Causeway ----------------------------------------------
    "causeway_siren": [
        ("Siren's Lash", "damage", 22, 0, 18, "magic", {}),
        ("Entrancing Song", "debuff", 0, 5, 24, "magic",
         {"duration": 3, "stat_mods": {"intellect": -14}}),
    ],
    "murloc_spearfisher": [
        ("Barbed Spear", "damage", 20, 0, 0, "physical", {}),
        ("Net Throw", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    # ---- Sunken Steps ----------------------------------------------------
    "stepstone_sentinel": [
        ("Slab Slam", "damage", 25, 0, 0, "physical", {}),
        ("Barnacled Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 28}}),
    ],
    # ---- Razorjaw Shallows -----------------------------------------------
    "razor_whelp": [
        ("Rending Bite", "damage", 25, 0, 0, "physical", {}),
        ("Blood Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    # ---- Tidal Flats -----------------------------------------------------
    "flatfin_stinger": [
        ("Barb Strike", "damage", 18, 0, 0, "physical", {}),
        ("Venom Barb", "dot", 10, 3, 0, "nature", {"duration": 4}),
    ],
    "sand_burrower": [
        ("Sand Claw", "damage", 19, 0, 0, "physical", {}),
        ("Burrow Dodge", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"agility": 16}}),
    ],
    # ---- named rares -----------------------------------------------------
    "gortek_houndmaster": [
        ("Whip Crack", "damage", 30, 0, 0, "physical", {}),
        ("Sic 'Em", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
        ("Hamstring Lash", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "mamtoth_hexweaver": [
        ("Shadow Bolt", "damage", 30, 0, 24, "shadow", {}),
        ("Weaving Hex", "debuff", 0, 4, 20, "shadow",
         {"duration": 4, "stat_mods": {"intellect": -16}}),
        ("Hex Mend", "heal", 44, 4, 32, "shadow", {}),
    ],
    "mojbashi_drowned": [
        ("Drowned Fist", "damage", 28, 0, 0, "physical", {}),
        ("Waterlogged Rot", "dot", 13, 3, 0, "physical", {"duration": 3}),
        ("Tidebound Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 26}}),
    ],
    "sshara_seer": [
        ("Tide Bolt", "damage", 30, 0, 26, "magic", {}),
        ("Drowning Whisper", "dot", 13, 3, 22, "magic", {"duration": 3}),
        ("Sea Veil", "buff", 0, 5, 20, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 22}}),
    ],
    "kragg_shellcrusher": [
        ("Shellcrusher Slam", "damage", 30, 0, 0, "physical", {}),
        ("Barnacle Plate", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
        ("Rending Pincer", "dot", 13, 3, 0, "physical", {"duration": 3}),
    ],
    "barnacle_beard": [
        ("Rusted Boarding Axe", "damage", 28, 0, 0, "physical", {}),
        ("Rotgut Roar", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"attack_power": -14}}),
        ("Salt-Crusted Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 24}}),
    ],
}

# ======================================================================
# CENTRAL BARRENS content pass (2026-10-21).  Ladder: Plains 12-15, Lushwater 13-15,
# Pools 14-17, Kolkar 13-17, quilboar 13-18, Dreadmist 13-18, Raider's Rest 16-19.
# ======================================================================
CENTRAL_BARRENS_KITS = {
    # ---- Golden Plains ---------------------------------------------------
    "plains_thunderhawk": [
        ("Talon Dive", "damage", 23, 0, 0, "physical", {}),
        ("Static Shriek", "damage", 31, 3, 0, "nature", {}),
    ],
    "barrens_hyena": [
        ("Gnaw", "damage", 21, 0, 0, "physical", {}),
        ("Rabid Howl", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    # ---- Sentinel Rocks ----------------------------------------------------
    "redstone_scorpid": [
        ("Claw Pinch", "damage", 22, 0, 0, "physical", {}),
        ("Redstone Venom", "dot", 10, 3, 0, "nature", {"duration": 4}),
    ],
    # ---- Lushwater Oasis ---------------------------------------------------
    "oasis_tangle_vine": [
        ("Whip Lash", "damage", 22, 0, 0, "nature", {}),
        ("Entangling Roots", "debuff", 0, 4, 0, "nature",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    # ---- Forgotten Pools -----------------------------------------------------
    "drowned_pilgrim": [
        ("Waterlogged Strike", "damage", 24, 0, 0, "physical", {}),
        ("Weeping Chill", "debuff", 0, 4, 22, "magic",
         {"duration": 3, "stat_mods": {"intellect": -14}}),
    ],
    # ---- Kodo Graveyard --------------------------------------------------------
    "cb_carrion_vulture": [
        ("Carrion Peck", "damage", 21, 0, 0, "physical", {}),
        ("Festering Wound", "dot", 9, 3, 0, "nature", {"duration": 4}),
    ],
    "kodo_wraith": [
        ("Bone-Crush Stomp", "damage", 27, 0, 0, "physical", {}),
        ("Grave Chill", "debuff", 0, 4, 20, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -14}}),
    ],
    # ---- Kolkar War Camp --------------------------------------------------------
    "kolkar_taskmaster": [
        ("Lash of Command", "damage", 25, 0, 0, "physical", {}),
        ("Rally the Herd", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
        ("Crippling Whip", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "kolkar_windseer": [
        ("Gale Bolt", "damage", 24, 0, 20, "nature", {}),
        ("Wind Ward", "heal", 42, 4, 32, "nature", {}),
    ],
    # ---- Raider's Rest -----------------------------------------------------------
    "raiders_smuggler": [
        ("Poisoned Dirk", "damage", 25, 0, 0, "physical", {}),
        ("Crippling Poison", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    "bandit_bombardier": [
        ("Powder Toss", "damage", 28, 0, 0, "fire", {}),
        ("Smoke Bomb", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    # ---- Bramblescar / Agama'gor -----------------------------------------------------
    "quillthrower": [
        ("Quill Volley", "damage", 24, 0, 0, "physical", {}),
        ("Thorn Barb", "dot", 9, 3, 0, "physical", {"duration": 4}),
    ],
    "bristleback_battleboar": [
        ("Gore", "damage", 26, 0, 0, "physical", {}),
        ("Trampling Rush", "damage", 36, 4, 0, "physical", {}),
        ("Boar Fury", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "cb_bristleback_thornweaver": [
        ("Thorn Bolt", "damage", 26, 0, 22, "nature", {}),
        ("Briar Mending", "heal", 46, 4, 34, "nature", {}),
    ],
    # ---- Dreadmist ------------------------------------------------------------------------
    "dreadmist_cultist": [
        ("Shadow Bolt", "damage", 24, 0, 20, "shadow", {}),
        ("Curse of Weakness", "debuff", 0, 4, 22, "shadow",
         {"duration": 4, "stat_mods": {"attack_power": -14}}),
    ],
    "dreadmist_warlock": [
        ("Immolate", "damage", 30, 0, 26, "fire", {}),
        ("Corruption", "dot", 12, 3, 28, "shadow", {"duration": 4}),
        ("Fel Armor", "buff", 0, 6, 24, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 22}}),
    ],
    "dreadmist_imp": [
        ("Firebolt", "damage", 23, 0, 16, "fire", {}),
        ("Blood Pact", "buff", 0, 6, 0, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"intellect": 14}}),
    ],
    # ---- Grol'dom Farm / Shrine / Southfury ------------------------------------------------------
    "farm_poacher": [
        ("Cheap Shot", "damage", 22, 0, 0, "physical", {}),
        ("Snare Trap", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "mourning_spirit": [
        ("Spirit Bolt", "damage", 25, 0, 20, "magic", {}),
        ("Mourning Wail", "debuff", 0, 4, 22, "magic",
         {"duration": 3, "stat_mods": {"intellect": -14}}),
    ],
    "riverbank_snapper": [
        ("Snapping Jaws", "damage", 22, 0, 0, "physical", {}),
        ("Shell Retreat", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 28}}),
    ],
    # ---- bosses that never had kits -----------------------------------------------------------------
    "rathorian": [
        ("Shadow Bolt", "damage", 38, 0, 28, "shadow", {}),
        ("Siphon Soul", "dot", 15, 3, 32, "shadow", {"duration": 4}),
        ("Curse of Tongues", "debuff", 0, 5, 26, "shadow",
         {"duration": 4, "stat_mods": {"intellect": -20}}),
        ("Dark Mending", "heal", 60, 5, 36, "shadow", {}),
    ],
    "xelnaz": [
        ("Fel Bite", "damage", 38, 0, 0, "physical", {}),
        ("Rending Claws", "dot", 16, 3, 0, "physical", {"duration": 4}),
        ("Terrifying Howl", "debuff", 0, 5, 0, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -20}}),
        ("Bloodlust", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 22}}),
    ],
    "water_elemental": [
        ("Water Bolt", "damage", 24, 0, 18, "magic", {}),
        ("Tidal Surge", "damage", 33, 3, 28, "magic", {}),
    ],
    # ---- named rares ------------------------------------------------------------------------------------
    "old_sunhide": [
        ("Sunhide Stomp", "damage", 30, 0, 0, "physical", {}),
        ("Thick Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
        ("Ground Tremor", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "stormwing_skyrider": [
        ("Thunder Dive", "damage", 32, 0, 0, "nature", {}),
        ("Storm Cry", "debuff", 0, 4, 0, "nature",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
        ("Tailwind", "buff", 0, 5, 0, "nature",
         {"duration": 4, "self_only": True, "stat_mods": {"agility": 20}}),
    ],
    "redrock_matriarch": [
        ("Matriarch's Pincer", "damage", 32, 0, 0, "physical", {}),
        ("Brood Venom", "dot", 14, 3, 0, "nature", {"duration": 4}),
        ("Carapace Harden", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 32}}),
    ],
    "queen_skitterwing": [
        ("Chitin Lash", "damage", 31, 0, 0, "physical", {}),
        ("Swarm Call", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"agility": 22}}),
        ("Hive Sting", "dot", 14, 3, 0, "nature", {"duration": 4}),
    ],
    "maeve_weeping": [
        ("Weeping Touch", "damage", 33, 0, 26, "magic", {}),
        ("Drowning Sorrow", "dot", 14, 3, 24, "magic", {"duration": 4}),
        ("Tears of the Pool", "heal", 52, 5, 34, "magic", {}),
    ],
    "hollowhorn": [
        ("Hollowhorn Gore", "damage", 36, 0, 0, "physical", {}),
        ("Boneyard Dirge", "debuff", 0, 4, 22, "magic",
         {"duration": 3, "stat_mods": {"attack_power": -18}}),
        ("Deathless Hide", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 36}}),
    ],
    "warbringer_gorrak": [
        ("Warbringer's Cleave", "damage", 38, 0, 0, "physical", {}),
        ("Battle Roar", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 26}}),
        ("Hamstring", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "silas_quickfinger": [
        ("Quickfinger Stab", "damage", 38, 0, 0, "physical", {}),
        ("Lamp-Oil Poison", "dot", 16, 3, 0, "nature", {"duration": 4}),
        ("Vanishing Powder", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"agility": 26}}),
    ],
    "wardchief_thulg": [
        ("Thulg's Cleaver", "damage", 34, 0, 0, "physical", {}),
        ("Wardchief's Command", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 30}}),
        ("Ruinous Strike", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
    ],
    "sowmother_grunka": [
        ("Sow-Mother's Gore", "damage", 36, 0, 0, "physical", {}),
        ("Brood Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 24}}),
        ("Rending Tusks", "dot", 15, 3, 0, "physical", {"duration": 4}),
    ],
    "veshra_voidcaller": [
        ("Void Lance", "damage", 36, 0, 28, "shadow", {}),
        ("Rift Corruption", "dot", 15, 3, 28, "shadow", {"duration": 4}),
        ("Hollow Ward", "buff", 0, 6, 24, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 26}}),
    ],
    "fallen_warrior_echo": [
        ("Spectral Blade", "damage", 31, 0, 0, "physical", {}),
        ("Echo of Valour", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
        ("Mournful Cry", "debuff", 0, 4, 22, "magic",
         {"duration": 3, "stat_mods": {"intellect": -16}}),
    ],
    "bazz_lootchief": [
        ("Pitchfork Jab", "damage", 29, 0, 0, "physical", {}),
        ("Sticky Fingers", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -16}}),
        ("Scrap Plate", "buff", 0, 5, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 28}}),
    ],
}

SOUTHERN_BARRENS_KITS = {
    # ---- the dwarves (Bael Modan / Bael'dun Keep) - previously had no kit at all -----------------------
    "dwarf_miner": [
        ("Pickaxe Swing", "damage", 25, 0, 0, "physical", {}),
        ("Rock-Dust Cloud", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "dwarf_engineer": [
        ("Wrench Bash", "damage", 24, 0, 0, "physical", {}),
        ("Rivet Gun", "damage", 33, 3, 0, "physical", {}),
        ("Patch Armour", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
    ],
    "dwarf_explosives": [
        ("Pry-Bar Jab", "damage", 24, 0, 0, "physical", {}),
        ("Dynamite Toss", "damage", 36, 3, 0, "fire", {}),
        ("Short Fuse", "dot", 12, 3, 0, "fire", {"duration": 4}),
    ],
    # ---- Bael Modan ---------------------------------------------------------------------------------------
    "modan_overseer": [
        ("Overseer's Whip", "damage", 28, 0, 0, "physical", {}),
        ("Work Harder", "buff", 0, 5, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 22}}),
        ("Docked Pay", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -18}}),
    ],
    "dig_site_golem": [
        ("Granite Fist", "damage", 30, 0, 0, "physical", {}),
        ("Seismic Slam", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
    # ---- Bael'dun Keep --------------------------------------------------------------------------------------
    "keep_rifleman": [
        ("Rifle Shot", "damage", 33, 0, 0, "physical", {}),
        ("Pinning Fire", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "keep_sergeant": [
        ("Hammer Blow", "damage", 31, 0, 0, "physical", {}),
        ("Hold the Line", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
        ("Shield Bash", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -20}}),
    ],
    "keep_mastiff": [
        ("Mastiff Bite", "damage", 28, 0, 0, "physical", {}),
        ("Savage Worry", "dot", 12, 3, 0, "physical", {"duration": 4}),
    ],
    "general_twinbraid": [
        ("Twinbraid's Hammer", "damage", 54, 0, 0, "physical", {}),
        ("Stormhammer Throw", "damage", 70, 4, 0, "nature", {}),
        ("Dwarven Resolve", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"armor": 55, "attack_power": 30}}),
        ("Sundering Stomp", "debuff", 0, 5, 0, "physical", {"duration": 4, "stat_mods": {"attack_power": -26}}),
    ],
    # ---- Blackthorn / Razorfen --------------------------------------------------------------------------------
    "razormane_skinner": [
        ("Skinning Knife", "damage", 26, 0, 0, "physical", {}),
        ("Gutting Cut", "dot", 12, 3, 0, "physical", {"duration": 4}),
    ],
    "blackthorn_boarhound": [
        ("Tusk Rake", "damage", 25, 0, 0, "physical", {}),
        ("Frenzied Charge", "damage", 36, 3, 0, "physical", {}),
    ],
    "razorfen_bramble_guard": [
        ("Thorn-Club Smash", "damage", 28, 0, 0, "physical", {}),
        ("Bramble Armour", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 36}}),
    ],
    "thornhide_boar": [
        ("Thorn Gore", "damage", 26, 0, 0, "physical", {}),
        ("Rending Thorns", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    "hagg_taurenbane": [
        ("Taurenbane Cleave", "damage", 50, 0, 0, "physical", {}),
        ("Trophy Hunter", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 34}}),
        ("Hamstring Chop", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -24}}),
        ("Gouge the Hide", "dot", 18, 4, 0, "physical", {"duration": 4}),
    ],
    "brontus": [
        ("Earthshaking Stomp", "damage", 58, 0, 0, "physical", {}),
        ("Raging Charge", "damage", 74, 4, 0, "physical", {}),
        ("Thunderous Roar", "debuff", 0, 5, 0, "physical", {"duration": 4, "stat_mods": {"attack_power": -28}}),
        ("Hide of Stone", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"armor": 60}}),
    ],
    # ---- The Rift ------------------------------------------------------------------------------------------------
    "rift_cliffhawk": [
        ("Cliff Dive", "damage", 25, 0, 0, "physical", {}),
        ("Rending Talons", "dot", 10, 3, 0, "physical", {"duration": 4}),
    ],
    "gravel_skitterer": [
        ("Gravel Pinch", "damage", 24, 0, 0, "physical", {}),
        ("Slate Venom", "dot", 12, 3, 0, "nature", {"duration": 4}),
    ],
    "rift_sabertooth": [
        ("Rend", "damage", 29, 0, 0, "physical", {}),
        ("Pounce", "damage", 38, 3, 0, "physical", {}),
        ("Bleeding Claws", "dot", 12, 4, 0, "physical", {"duration": 4}),
    ],
    # ---- Field of Giants -----------------------------------------------------------------------------------------
    "giantbone_hyena": [
        ("Bone-Crack Bite", "damage", 26, 0, 0, "physical", {}),
        ("Marrow Frenzy", "buff", 0, 5, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    "bonedust_wraith": [
        ("Knuckle Slam", "damage", 29, 0, 0, "physical", {}),
        ("Giant's Dread", "debuff", 0, 4, 24, "magic", {"duration": 3, "stat_mods": {"strength": -18}}),
    ],
    # ---- Raptor Grounds ------------------------------------------------------------------------------------------
    "sunscale_stalker": [
        ("Raking Claws", "damage", 27, 0, 0, "physical", {}),
        ("Leaping Rend", "damage", 37, 3, 0, "physical", {}),
    ],
    "nest_mother_raptor": [
        ("Maternal Fury", "damage", 33, 0, 0, "physical", {}),
        ("Brood Shriek", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 24}}),
        ("Tearing Beak", "dot", 14, 3, 0, "physical", {"duration": 4}),
    ],
    # ---- Sinkhole Crater ----------------------------------------------------------------------------------------
    "sinkhole_burrower": [
        ("Mandible Snap", "damage", 25, 0, 0, "physical", {}),
        ("Acid Spit", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    "brood_tunnel_guard": [
        ("Chitin Slash", "damage", 31, 0, 0, "physical", {}),
        ("Hardened Shell", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 38}}),
        ("Paralytic Sting", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -22}}),
    ],
    # ---- Hoodoo Spires ---------------------------------------------------------------------------------------------
    "windspire_harpy": [
        ("Wind-Talon Rake", "damage", 26, 0, 0, "physical", {}),
        ("Screech", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"intellect": -16}}),
    ],
    "spire_windcaller": [
        ("Lightning Gust", "damage", 30, 0, 24, "nature", {}),
        ("Gale Mending", "heal", 50, 4, 32, "nature", {}),
    ],
    "hoodoo_dust_devil": [
        ("Grit Lash", "damage", 27, 0, 0, "nature", {}),
        ("Blinding Dust", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
    # ---- named rares ----------------------------------------------------------------------------------------------
    "dustmaw_rift_lurker": [
        ("Maw of the Rift", "damage", 44, 0, 0, "physical", {}),
        ("Rock-Slide Roar", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -24}}),
        ("Canyon Frenzy", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 30}}),
    ],
    "thrumbone_ancient": [
        ("Colossal Backhand", "damage", 46, 0, 0, "physical", {}),
        ("Titan's Dread", "debuff", 0, 4, 26, "magic", {"duration": 3, "stat_mods": {"strength": -24}}),
        ("Rattling Dirge", "dot", 16, 3, 24, "shadow", {"duration": 4}),
    ],
    "old_mother_longhorn": [
        ("Matriarch's Gore", "damage", 45, 0, 0, "physical", {}),
        ("Protective Trample", "damage", 56, 4, 0, "physical", {}),
        ("Herd-Mother's Roar", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 44}}),
    ],
    "bramblequeen_durga": [
        ("Thorn Bolt", "damage", 44, 0, 30, "nature", {}),
        ("Strangling Briar", "dot", 18, 3, 30, "nature", {"duration": 4}),
        ("Bark of the Queen", "buff", 0, 6, 28, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 44}}),
    ],
    "skinwalker_garn": [
        ("Trophy Stab", "damage", 42, 0, 0, "physical", {}),
        ("Flay", "dot", 18, 3, 0, "physical", {"duration": 4}),
        ("Hide Cloak", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"agility": 32}}),
    ],
    "foreman_grubb": [
        ("Foreman's Hammer", "damage", 46, 0, 0, "physical", {}),
        ("Quota Enforcement", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 32}}),
        ("Shoddy Scaffold", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -24}}),
    ],
    "sergeant_ironvein": [
        ("Ironvein's Maul", "damage", 50, 0, 0, "physical", {}),
        ("Stand Fast", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 56}}),
        ("Sundering Blow", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"armor": -40}}),
    ],
    "razorbeak_nestbreaker": [
        ("Nestbreaker Rake", "damage", 46, 0, 0, "physical", {}),
        ("Diving Rend", "damage", 60, 4, 0, "physical", {}),
        ("Shrill Frenzy", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 34}}),
    ],
    "vexa_tunnel_queen": [
        ("Queen's Mandibles", "damage", 50, 0, 0, "physical", {}),
        ("Toxic Brood-Spit", "dot", 20, 3, 0, "nature", {"duration": 4}),
        ("Skitter Swarm", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -28}}),
    ],
    "skyshriek_matron": [
        ("Matron's Lightning", "damage", 50, 0, 30, "nature", {}),
        ("Skyshriek", "debuff", 0, 4, 28, "magic", {"duration": 3, "stat_mods": {"intellect": -26}}),
        ("Storm Feathers", "buff", 0, 6, 26, "nature", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 36}}),
    ],
}

BROODSPIRAL_KITS = {
    # ---- trash ----------------------------------------------------------------------------------------------------
    "silithid_guardian": [
        ("Mandible Crush", "damage", 26, 0, 0, "physical", {}),
        ("Chitin Plating", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
    ],
    "silithid_stinger": [
        ("Stinger Jab", "damage", 24, 0, 0, "physical", {}),
        ("Neurotoxin", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    "hive_drone": [
        ("Drone Slash", "damage", 22, 0, 0, "physical", {}),
        ("Swarm Rush", "damage", 31, 3, 0, "physical", {}),
    ],
    "hive_skulker": [
        ("Ambush Strike", "damage", 27, 0, 0, "physical", {}),
        ("Crippling Venom", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
    "resin_spitter": [
        ("Resin Glob", "damage", 29, 0, 0, "nature", {}),
        ("Sticky Resin", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -24}}),
    ],
    "brood_tender": [
        ("Venom Lash", "damage", 25, 0, 18, "nature", {}),
        ("Tend the Brood", "heal", 55, 4, 30, "nature", {}),
    ],
    "carapace_crusher": [
        ("Crushing Claw", "damage", 33, 0, 0, "physical", {}),
        ("Shell Slam", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -22}}),
    ],
    "gorged_larva": [
        ("Acid Burp", "damage", 27, 0, 0, "nature", {}),
        ("Corrosive Bile", "dot", 12, 3, 0, "nature", {"duration": 4}),
    ],
    "hive_weaver": [
        ("Amber Bolt", "damage", 31, 0, 22, "nature", {}),
        ("Resin Bind", "debuff", 0, 4, 20, "nature", {"duration": 3, "stat_mods": {"agility": -26}}),
        ("Amber Ward", "buff", 0, 6, 24, "nature", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 30}}),
    ],
    "amber_sentinel": [
        ("Sentinel Strike", "damage", 35, 0, 0, "physical", {}),
        ("Hold Amber", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 44}}),
        ("Shatter Guard", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -24}}),
    ],
    # ---- bosses (levels 19 / 21 / 22 / 24; sub-20 = 3 abilities, 20+ = 4) --------------------------------------------
    "carapace_warden": [
        ("Chitin Slam", "damage", 44, 0, 0, "physical", {}),
        ("Carapace Hardening", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 52}}),
        ("Rending Mandibles", "dot", 16, 4, 0, "physical", {"duration": 4}),
    ],
    "the_broodkeeper": [   # PLANNED summon: "Hatching Call" should hatch 2-3 Hive Drones once the engine supports it
        ("Venom Bolt", "damage", 48, 0, 28, "nature", {}),
        ("Brood Mending", "heal", 95, 6, 34, "nature", {}),
        ("Hatching Call", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 32}}),
        ("Caustic Cloud", "dot", 20, 4, 30, "nature", {"duration": 4}),
    ],
    "larval_broodguard": [  # PLANNED phase: "Larval Molt" should drop its armour and enrage at 50% hp
        ("Acid Spit", "damage", 52, 0, 0, "nature", {}),
        ("Venom Barrage", "damage", 68, 4, 0, "nature", {}),
        ("Paralytic Ichor", "debuff", 0, 5, 0, "nature", {"duration": 4, "stat_mods": {"agility": -30}}),
        ("Larval Molt", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"armor": 46}}),
    ],
    "broodspiral_queen": [  # PLANNED summon: "Hivemind Screech" should call 2 Silithid Stingers
        ("Queen's Rend", "damage", 62, 0, 0, "physical", {}),
        ("Hivemind Screech", "debuff", 0, 5, 0, "magic", {"duration": 4, "stat_mods": {"attack_power": -32}}),
        ("Brood Frenzy", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 42}}),
        ("Corrosive Ichor", "dot", 24, 4, 0, "nature", {"duration": 4}),
    ],
    # ---- named rares (pinned in the nurseries) -------------------------------------------------------------------------
    "mother_amberwing": [
        ("Amberwing Lash", "damage", 42, 0, 0, "physical", {}),
        ("Egg-Mother's Rage", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 30}}),
        ("Sticky Web", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -26}}),
    ],
    "gnash_hollow_maw": [
        ("Hollow Maw", "damage", 50, 0, 0, "physical", {}),
        ("Bone-Crunch", "dot", 18, 3, 0, "physical", {"duration": 4}),
        ("Gnash Frenzy", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 34}}),
    ],
    "chitterlord_skrix": [
        ("Chitter Bolt", "damage", 52, 0, 30, "nature", {}),
        ("Skrix's Swarm", "dot", 22, 3, 28, "nature", {"duration": 4}),
        ("Chitin Veil", "buff", 0, 6, 26, "nature", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 40}}),
    ],
}

RAZORFEN_KITS = {
    # ---- trash (L25-32) -------------------------------------------------------------------------------------------
    "razorfen_spearhide": [
        ("Spear Thrust", "damage", 36, 0, 0, "physical", {}),
        ("Barbed Skewer", "dot", 14, 3, 0, "physical", {"duration": 4}),
    ],
    "razorfen_defender": [
        ("Shield Slam", "damage", 33, 0, 0, "physical", {}),
        ("Thornwall", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 62}}),
    ],
    "razorfen_beast_trainer": [
        ("Whip Crack", "damage", 35, 0, 0, "physical", {}),
        ("Rally the Pack", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 32}}),
    ],
    "razorfen_handler": [
        ("Thorn Dart", "damage", 37, 0, 0, "nature", {}),
        ("Poisoned Dart", "dot", 15, 3, 0, "nature", {"duration": 4}),
    ],
    "razorfen_geomancer": [
        ("Earth Spike", "damage", 40, 0, 22, "nature", {}),
        ("Rooting Thorns", "debuff", 0, 4, 22, "nature", {"duration": 3, "stat_mods": {"agility": -30}}),
        ("Stoneskin", "buff", 0, 7, 20, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 44}}),
    ],
    "razorfen_totemic": [
        ("Totem Strike", "damage", 38, 0, 0, "physical", {}),
        ("Mending Totem", "heal", 70, 4, 30, "nature", {}),
        ("Brand of Thorns", "debuff", 0, 5, 0, "nature", {"duration": 3, "stat_mods": {"armor": -36}}),
    ],
    "razorfen_ward_keeper": [
        ("Ward Bolt", "damage", 41, 0, 22, "arcane", {}),
        ("Sealing Pulse", "debuff", 0, 5, 20, "arcane", {"duration": 3, "stat_mods": {"attack_power": -32}}),
        ("Ward Barrier", "buff", 0, 6, 24, "arcane", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 48}}),
    ],
    "deaths_head_acolyte": [
        ("Shadow Bolt", "damage", 42, 0, 24, "shadow", {}),
        ("Curse of Agony", "dot", 17, 3, 22, "shadow", {"duration": 5}),
        ("Siphon Essence", "heal", 60, 5, 28, "shadow", {}),
    ],
    "deaths_head_cultist": [
        ("Death Touch", "damage", 40, 0, 22, "shadow", {}),
        ("Withering Hex", "debuff", 0, 4, 22, "shadow", {"duration": 3, "stat_mods": {"attack_power": -34}}),
        ("Soul Rend", "dot", 18, 3, 26, "shadow", {"duration": 4}),
    ],
    "kraul_bristleboar": [
        ("Gore", "damage", 34, 0, 0, "physical", {}),
        ("Bristle", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 52}}),
    ],
    "raging_agamar": [
        ("Savage Gore", "damage", 40, 0, 0, "physical", {}),
        ("Frenzy", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 38}}),
        ("Rend", "dot", 16, 3, 0, "physical", {"duration": 4}),
    ],
    "thornback_sow": [
        ("Trample", "damage", 37, 0, 0, "physical", {}),
        ("Thorn Spray", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -28}}),
        ("Wallow", "heal", 56, 6, 0, "nature", {}),
    ],
    # ---- named rares (3 abilities) ----------------------------------------------------------------------------------
    "blind_hunter": [
        ("Blind Shot", "damage", 54, 0, 0, "physical", {}),
        ("Hunter's Mark", "debuff", 0, 5, 0, "physical", {"duration": 4, "stat_mods": {"armor": -42}}),
        ("Serrated Arrow", "dot", 21, 4, 0, "physical", {"duration": 5}),
    ],
    "earthcaller_halmgar": [
        ("Earthshock", "damage", 58, 0, 30, "nature", {}),
        ("Stoneclaw Ward", "heal", 105, 6, 36, "nature", {}),
        ("Earthbind", "debuff", 0, 5, 26, "nature", {"duration": 4, "stat_mods": {"agility": -34}}),
    ],
    "thornjaw_the_gorger": [
        ("Gorging Bite", "damage", 60, 0, 0, "physical", {}),
        ("Thorn-Hide", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"armor": 72}}),
        ("Ravenous Rend", "dot", 22, 4, 0, "physical", {"duration": 5}),
    ],
    # ---- bosses (levels 28 / 30 / 30 / 32 / 32 / 34; all 4 abilities) -------------------------------------------------
    "roogug": [
        ("Brutal Cleave", "damage", 62, 0, 0, "physical", {}),
        ("Rend Flesh", "dot", 24, 4, 0, "physical", {"duration": 4}),
        ("Roogug's Fury", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"attack_power": 40}}),
        ("Crushing Blow", "damage", 84, 5, 0, "physical", {}),
    ],
    "aggem_thorncurse": [   # PLANNED summon: "Call of the Boar Spirits" should raise 2 spirit boars once the engine supports it
        ("Thorn Bolt", "damage", 66, 0, 30, "nature", {}),
        ("Thorn Curse", "dot", 26, 4, 32, "nature", {"duration": 5}),
        ("Spirit Ward", "buff", 0, 7, 0, "nature", {"duration": 5, "self_only": True, "stat_mods": {"magic_resistance": 52}}),
        ("Call of the Boar Spirits", "damage", 82, 5, 36, "nature", {}),
    ],
    "death_speaker_jargba": [   # PLANNED: "Dominate Mind" should be a real mind-control once the engine supports it
        ("Shadow Bolt", "damage", 68, 0, 30, "shadow", {}),
        ("Dominate Mind", "debuff", 0, 5, 30, "shadow", {"duration": 4, "stat_mods": {"attack_power": -46}}),
        ("Death's Head Hex", "dot", 27, 4, 30, "shadow", {"duration": 5}),
        ("Dark Mending", "heal", 120, 8, 40, "shadow", {}),
    ],
    "overlord_ramtusk": [
        ("Tusk Gore", "damage", 74, 0, 0, "physical", {}),
        ("Trampling Charge", "damage", 98, 4, 0, "physical", {}),
        ("War Cry", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"attack_power": 46}}),
        ("Bleeding Gouge", "dot", 28, 4, 0, "physical", {"duration": 5}),
    ],
    "agathelos_the_raging": [   # PLANNED phase: "Savage Roar" should become a true enrage at 30% hp
        ("Rending Maul", "damage", 76, 0, 0, "physical", {}),
        ("Raging Charge", "damage", 100, 4, 0, "physical", {}),
        ("Savage Roar", "buff", 0, 7, 0, "physical", {"duration": 5, "self_only": True, "stat_mods": {"attack_power": 50}}),
        ("Frenzied Bite", "dot", 30, 4, 0, "physical", {"duration": 5}),
    ],
    "charlga_razorflank": [   # PLANNED: Earthgrab Totem / Lightning Shield / heal-ward summons once the engine supports them
        ("Razorflank Bolt", "damage", 80, 0, 34, "nature", {}),
        ("Chieftain's Mending", "heal", 150, 6, 40, "nature", {}),
        ("Mighty Cursing", "debuff", 0, 5, 30, "shadow", {"duration": 4, "stat_mods": {"armor": -52}}),
        ("Thornwrack", "dot", 32, 4, 34, "nature", {"duration": 5}),
    ],
}

# Northern Barrens content pass (2026-10-21): kits for the creatures whose "kit" key was dead (Slug, Bog Creature, Road Bandit,
# Southsea Brigand/Cannoneer, Witchwing x3, Serena, Harpy Matriarch, Captain Saltspray), plus the new NB roster.
# Power for L13-22: trash 20-32 first ability, rares 36-48, cave bosses 40-70.
NORTHERN_BARRENS_KITS = {
    # ---- repaired (formerly dead / undefined kit ids) -----------------------------------------------------------
    "slug": [
        ("Acid Spit", "damage", 22, 0, 0, "nature", {}),
        ("Slime Trail", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "bog_creature": [
        ("Mire Slam", "damage", 25, 0, 0, "physical", {}),
        ("Suffocating Mud", "dot", 10, 4, 0, "nature", {"duration": 4}),
    ],
    "road_bandit": [
        ("Cheap Shot", "damage", 21, 0, 0, "physical", {}),
        ("Pocket Sand", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "southsea_brigand": [
        ("Cutlass Slash", "damage", 22, 0, 0, "physical", {}),
        ("Dirty Trick", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -14}}),
    ],
    "southsea_cannoneer": [
        ("Grapeshot", "damage", 26, 0, 0, "physical", {}),
        ("Powder Burn", "dot", 11, 4, 0, "fire", {"duration": 3}),
    ],
    "witchwing_harpy": [
        ("Razor Talon", "damage", 28, 0, 0, "physical", {}),
        ("Hexed Screech", "debuff", 0, 4, 0, "magic", {"duration": 3, "stat_mods": {"attack_power": -18}}),
    ],
    "witchwing_windcaller": [
        ("Lightning Bolt", "damage", 29, 0, 24, "nature", {}),
        ("Wind Hex", "debuff", 0, 4, 26, "nature", {"duration": 3, "stat_mods": {"agility": -22}}),
        ("Mending Gale", "heal", 52, 4, 34, "nature", {}),
    ],
    "witchwing_slayer": [
        ("Slayer's Talon", "damage", 29, 0, 0, "physical", {}),
        ("Rending Dive", "dot", 12, 3, 0, "physical", {"duration": 4}),
    ],
    # ---- Slug Fens ----------------------------------------------------------------------------------------------
    "mire_leech": [
        ("Leech Bite", "damage", 18, 0, 0, "physical", {}),
        ("Drain Blood", "dot", 9, 3, 0, "physical", {"duration": 4}),
    ],
    "peat_shambler": [
        ("Peat Fist", "damage", 26, 0, 0, "physical", {}),
        ("Bog Hide", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
    ],
    "fenwater_crocolisk": [
        ("Fen Bite", "damage", 27, 0, 0, "physical", {}),
        ("Death Spin", "damage", 36, 4, 0, "physical", {}),
    ],
    # ---- Harpy Roost / Serena's Hollow ---------------------------------------------------------------------------------
    "roost_bonepicker": [
        ("Carrion Claw", "damage", 23, 0, 0, "physical", {}),
        ("Gnaw Marrow", "dot", 10, 3, 0, "physical", {"duration": 4}),
    ],
    "harpy_sky_sentry": [
        ("Spear Dive", "damage", 27, 0, 0, "physical", {}),
        ("Guarded Perch", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 36}}),
    ],
    # ---- Mor'shan Rampart (night-elf pickets probing the Horde wall) -------------------------------------------------
    "sentinel_picket": [
        ("Glaive Strike", "damage", 28, 0, 0, "physical", {}),
        ("Shield of Elune", "buff", 0, 6, 0, "magic", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 28}}),
    ],
    "sentinel_archer": [
        ("Moonbow Shot", "damage", 29, 0, 0, "physical", {}),
        ("Hamstring Arrow", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -24}}),
    ],
    "sentinel_moonspeaker": [
        ("Moonfire", "damage", 29, 0, 22, "arcane", {}),
        ("Mending Moonlight", "heal", 50, 4, 32, "arcane", {}),
        ("Entangling Roots", "debuff", 0, 5, 24, "nature", {"duration": 3, "stat_mods": {"agility": -22}}),
    ],
    # ---- Mor'shan Base Camp / Far Watch -------------------------------------------------------------------------------
    "kolkar_scoutrider": [
        ("Javelin Throw", "damage", 24, 0, 0, "physical", {}),
        ("Hobbling Dart", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "kolkar_warbrand": [
        ("Warbrand Cleave", "damage", 28, 0, 0, "physical", {}),
        ("Brand of War", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 26}}),
    ],
    # ---- Sludge Fen -----------------------------------------------------------------------------------------------------
    "oil_driller": [
        ("Drill Strike", "damage", 28, 0, 0, "physical", {}),
        ("Oil Splash", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
    "pumpjack_guard": [
        ("Rifle Shot", "damage", 29, 0, 0, "physical", {}),
        ("Flare Round", "dot", 12, 4, 0, "fire", {"duration": 3}),
    ],
    "sludge_elemental": [
        ("Sludge Slam", "damage", 29, 0, 0, "physical", {}),
        ("Tar Coat", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"armor": -26}}),
        ("Congeal", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
    ],
    # ---- Stagnant Oasis -------------------------------------------------------------------------------------------------
    "kolkar_dervish": [
        ("Whirling Slash", "damage", 28, 0, 0, "physical", {}),
        ("Dervish Spin", "damage", 34, 4, 0, "physical", {"is_aoe": True}),
    ],
    "kolkar_stormcaller": [
        ("Stormbolt", "damage", 30, 0, 24, "nature", {}),
        ("Static Cloud", "debuff", 0, 5, 24, "nature", {"duration": 3, "stat_mods": {"attack_power": -22}}),
    ],
    "dervish_hound": [
        ("Maul", "damage", 24, 0, 0, "physical", {}),
        ("Rabid Frenzy", "buff", 0, 5, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    # ---- Merchant Coast -----------------------------------------------------------------------------------------------
    "tidewrecker_crab": [
        ("Pincer Snap", "damage", 20, 0, 0, "physical", {}),
        ("Shell Up", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 30}}),
    ],
    # ---- Dry Hills ------------------------------------------------------------------------------------------------------
    "hillcrest_stalker": [
        ("Pounce", "damage", 30, 0, 0, "physical", {}),
        ("Rend", "dot", 13, 3, 0, "physical", {"duration": 4}),
    ],
    "stonepeck_vulture": [
        ("Beak Rake", "damage", 27, 0, 0, "physical", {}),
        ("Carrion Dive", "damage", 37, 4, 0, "physical", {}),
    ],
    # ---- Boulder Lode Mine ----------------------------------------------------------------------------------------------
    "mine_hound": [
        ("Tunnel Bite", "damage", 20, 0, 0, "physical", {}),
        ("Baying Howl", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -14}}),
    ],
    "ore_sprite": [
        ("Spark Shard", "damage", 23, 0, 16, "arcane", {}),
        ("Crystal Resonance", "debuff", 0, 4, 18, "arcane", {"duration": 3, "stat_mods": {"intellect": -16}}),
    ],
    # ---- named rares (3 abilities) --------------------------------------------------------------------------------------
    "old_mire_maw": [
        ("Mire-Maw Snap", "damage", 38, 0, 0, "physical", {}),
        ("Bog Rot", "dot", 15, 3, 0, "nature", {"duration": 4}),
        ("Wallow", "buff", 0, 7, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 50}}),
    ],
    "skyfang_plunderer": [
        ("Plunder Dive", "damage", 38, 0, 0, "physical", {}),
        ("Shrieking Gale", "debuff", 0, 5, 0, "nature", {"duration": 3, "stat_mods": {"agility": -26}}),
        ("Talon Rake", "dot", 15, 4, 0, "physical", {"duration": 4}),
    ],
    "warden_ilthae": [
        ("Moonglaive", "damage", 44, 0, 0, "arcane", {}),
        ("Elune's Grasp", "debuff", 0, 5, 26, "nature", {"duration": 3, "stat_mods": {"agility": -28}}),
        ("Starfall Ward", "buff", 0, 7, 0, "arcane", {"duration": 4, "self_only": True, "stat_mods": {"magic_resistance": 44}}),
    ],
    "scoutcaptain_vrek": [
        ("Piercing Javelin", "damage", 38, 0, 0, "physical", {}),
        ("Cripple", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -26}}),
        ("Rally the Scouts", "buff", 0, 7, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 34}}),
    ],
    "kragg_wallbreaker": [
        ("Wallbreaker Slam", "damage", 42, 0, 0, "physical", {}),
        ("Shattering Blow", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"armor": -40}}),
        ("Siegeform", "buff", 0, 7, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 36}}),
    ],
    "prospector_delvik": [
        ("Blasting Pick", "damage", 36, 0, 0, "physical", {}),
        ("Dynamite Stick", "dot", 16, 4, 0, "fire", {"duration": 3, "is_aoe": True}),
        ("Hard Hat Drill", "buff", 0, 7, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 44}}),
    ],
    "windcaller_skreeva": [
        ("Skreeva's Bolt", "damage", 38, 0, 28, "nature", {}),
        ("Gale Hex", "debuff", 0, 5, 28, "nature", {"duration": 3, "stat_mods": {"agility": -28}}),
        ("Mending Gale", "heal", 70, 4, 36, "nature", {}),
    ],
    "serena_bloodfeather": [
        ("Bloodfeather Rake", "damage", 44, 0, 0, "physical", {}),
        ("Hunting Shriek", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"attack_power": -30}}),
        ("Blood Frenzy", "buff", 0, 7, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 36}}),
    ],
    "captain_saltspray": [
        ("Cutlass Flurry", "damage", 38, 0, 0, "physical", {}),
        ("Grog Splash", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"agility": -26}}),
        ("Broadside", "damage", 50, 5, 0, "fire", {"is_aoe": True}),
    ],
    # ---- Serena's Hollow boss (L20 -> 4 abilities) ----------------------------------------------------------------------
    "harpy_matriarch": [
        ("Matriarch's Talons", "damage", 50, 0, 0, "physical", {}),
        ("Shrieking Gale", "debuff", 0, 5, 0, "nature", {"duration": 3, "is_aoe": True,
                                                         "stat_mods": {"attack_power": -34, "agility": -24}}),
        ("Roost Mending", "heal", 80, 5, 40, "nature", {}),
        ("Wing-Storm", "damage", 64, 4, 0, "physical", {"is_aoe": True}),
    ],
}

ASHENVALE_DUNGEON_KITS = {
    # ================= MOONWELL HOLLOW (L13-16) ====================================================================
    "hollow_rotlasher": [
        ("Lash", "damage", 29, 0, 0, "physical", {}),
        ("Rooting Grasp", "debuff", 0, 5, 0, "nature", {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "gloomcap_sporeling": [
        ("Spore Burst", "damage", 24, 0, 0, "nature", {}),
        ("Choking Spores", "dot", 9, 4, 0, "nature", {"duration": 4}),
    ],
    "moonwell_mothwing": [
        ("Dust Wing", "damage", 27, 0, 0, "arcane", {}),
        ("Lunar Powder", "debuff", 0, 5, 0, "arcane", {"duration": 3, "stat_mods": {"attack_power": -18}}),
    ],
    "corrupted_moon_guard": [
        ("Glaive Cleave", "damage", 31, 0, 0, "physical", {}),
        ("Fallen Vigil", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 34}}),
    ],
    "twilight_rootbinder": [
        ("Withering Bolt", "damage", 30, 0, 18, "nature", {}),
        ("Entangle", "debuff", 0, 5, 18, "nature", {"duration": 3, "stat_mods": {"agility": -18}}),
        ("Rootmend", "heal", 52, 5, 24, "nature", {}),
    ],
    "mosshide_elder": [      # named rare, L15
        ("Crushing Moss", "damage", 36, 0, 0, "nature", {}),
        ("Gloomcap Cloud", "dot", 13, 4, 0, "nature", {"duration": 4, "is_aoe": True}),
        ("Mossy Hide", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 52}}),
        ("Smothering Spores", "debuff", 0, 5, 0, "nature", {"duration": 3, "stat_mods": {"attack_power": -22}}),
    ],
    "maelwyn_blightbloom": [   # boss, L16 (3 abilities)
        ("Blight Bolt", "damage", 38, 0, 20, "nature", {}),
        ("Rotbloom", "dot", 15, 4, 24, "nature", {"duration": 5}),
        ("Choking Roots", "debuff", 0, 6, 26, "nature", {"duration": 3, "stat_mods": {"agility": -26}}),
        ("Sap the Well", "heal", 70, 6, 30, "nature", {}),
    ],
    # ================= HOWLING BARROWS (L21-24) ====================================================================
    "rimebone_hound": [
        ("Frost Bite", "damage", 30, 0, 0, "frost", {}),
        ("Chilling Howl", "debuff", 0, 5, 0, "frost", {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "barrow_wight": [
        ("Grave Chill", "damage", 29, 0, 0, "frost", {}),
        ("Rattling Dread", "debuff", 0, 5, 0, "shadow", {"duration": 3, "stat_mods": {"attack_power": -20}}),
    ],
    "frostbitten_huntsman": [
        ("Frozen Arrow", "damage", 33, 0, 0, "frost", {}),
        ("Hunter's Snare", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
    "howling_wraith": [
        ("Wailing Bolt", "damage", 32, 0, 18, "shadow", {}),
        ("Keening Wail", "dot", 10, 4, 22, "shadow", {"duration": 4}),
        ("Gravewind", "heal", 55, 6, 26, "frost", {}),
    ],
    "rimeguard_sentinel": [
        ("Glacial Slam", "damage", 34, 0, 0, "frost", {}),
        ("Rime Plate", "buff", 0, 6, 0, "frost", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
    ],
    "wintermaw_howling": [     # named rare, L23 (4 abilities)
        ("Rending Bite", "damage", 40, 0, 0, "physical", {}),
        ("Howl of the Hunt", "debuff", 0, 5, 0, "frost", {"duration": 3, "stat_mods": {"attack_power": -24}}),
        ("Frozen Maw", "dot", 14, 4, 0, "frost", {"duration": 4}),
        ("Rime Hide", "buff", 0, 6, 0, "frost", {"duration": 4, "self_only": True, "stat_mods": {"armor": 58}}),
    ],
    "hunt_king_valorin": [     # boss, L24 (4 abilities)
        ("Frostbrand Strike", "damage", 44, 0, 0, "frost", {}),
        ("Winter's Grasp", "dot", 17, 4, 0, "frost", {"duration": 5}),
        ("Rimed Shackles", "debuff", 0, 5, 0, "frost", {"duration": 3, "stat_mods": {"agility": -28}}),
        ("The Hunt Rides", "buff", 0, 7, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 34}}),
    ],
    # ---------------------------------------------------------------- Grom's Rest (L26-32, 6 bosses, 4 abilities each)
    "groms_felguard_legionnaire": [
        ("Fel Cleave", "damage", 32, 0, 0, "shadow", {}),
        ("Sunder Armor", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"armor": -22}}),
        ("Fel Resolve", "buff", 0, 6, 0, "shadow", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 22}}),
    ],
    "groms_doomguard_warden": [
        ("Warden's Slam", "damage", 31, 0, 0, "fire", {}),
        ("Hellfire Lash", "dot", 12, 4, 0, "fire", {"duration": 4}),
        ("Infernal Hide", "buff", 0, 6, 0, "fire", {"duration": 3, "self_only": True, "stat_mods": {"armor": 48}}),
    ],
    "groms_satyr_warlord": [             # optional west wing, L28
        ("Warlord's Cleave", "damage", 46, 0, 0, "physical", {}),
        ("Fel Rampage", "damage", 58, 3, 0, "shadow", {}),
        ("Rend Flesh", "dot", 18, 4, 0, "physical", {"duration": 5}),
        ("Warlord's Roar", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 36}}),
    ],
    "groms_void_handmaiden": [           # optional east wing, L29
        ("Void Lance", "damage", 48, 0, 30, "shadow", {}),
        ("Enveloping Dark", "dot", 19, 3, 34, "shadow", {"duration": 5}),
        ("Siphon Hope", "debuff", 0, 5, 36, "shadow", {"duration": 3, "stat_mods": {"intellect": -30}}),
        ("Veil of the Void", "buff", 0, 7, 40, "shadow", {"duration": 4, "self_only": True, "stat_mods": {"armor": 60}}),
    ],
    "groms_doomguard_sentinel": [         # chain boss 1, L29
        ("Doom Cleave", "damage", 48, 0, 0, "fire", {}),
        ("Burning Ground", "dot", 18, 4, 0, "fire", {"duration": 5}),
        ("Crushing Stomp", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"agility": -30}}),
        ("Infernal Plating", "buff", 0, 7, 0, "fire", {"duration": 4, "self_only": True, "stat_mods": {"armor": 72}}),
    ],
    "groms_corrupted_ancient": [          # chain boss 2, L30
        ("Rotting Slam", "damage", 50, 0, 0, "physical", {}),
        ("Choking Roots", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -32}}),
        ("Fel Blight", "dot", 20, 3, 0, "nature", {"duration": 5}),
        ("Bark of Ages", "buff", 0, 7, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 78}}),
    ],
    "groms_felguard_overseer": [          # chain boss 3, L31
        ("Overseer's Blade", "damage", 52, 0, 0, "physical", {}),
        ("Mortal Rend", "dot", 21, 4, 0, "physical", {"duration": 5}),
        ("Demoralizing Roar", "debuff", 0, 5, 0, "shadow", {"duration": 3, "stat_mods": {"strength": -30}}),
        ("Fel Frenzy", "buff", 0, 7, 0, "shadow", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 42}}),
    ],
    "groms_lord_nightmare": [             # final boss, L32 (the Inner Sanctum Horror)
        ("Nightmare Bolt", "damage", 54, 0, 40, "shadow", {}),
        ("Eldritch Horror", "damage", 70, 3, 55, "shadow", {}),
        ("Void Corruption", "debuff", 0, 4, 45, "shadow", {"duration": 3, "stat_mods": {"armor": -30}}),
        ("Consuming Dread", "dot", 22, 5, 50, "shadow", {"duration": 5}),
    ],
}


DEATHKNELL_KITS = {
    # ---- Deathknell content pass (2026-10-22): the valley's subzone rosters, rares and the two starter caves ----
    # Valley floor / Deathknell Graves (L1-3)
    "plagued_stray": [
        ("Gnaw", "damage", 9, 0, 0, "physical", {}),
        ("Plague Bite", "dot", 4, 3, 0, "nature", {"duration": 3}),
    ],
    "grave_rat": [
        ("Scurry Bite", "damage", 7, 0, 0, "physical", {}),
        ("Frenzied Nibbles", "damage", 10, 3, 0, "physical", {}),
    ],
    # The Overrun Claim (L3-5)
    "dead_digger": [
        ("Pickaxe Swing", "damage", 11, 0, 0, "physical", {}),
        ("Miner's Grit", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 8}}),
    ],
    # Weeping Pond (L3-5)
    "drowned_wretch": [
        ("Sodden Fist", "damage", 11, 0, 0, "physical", {}),
        ("Choking Silt", "dot", 4, 4, 0, "nature", {"duration": 3}),
    ],
    "weeping_shade": [
        ("Mournful Wail", "damage", 10, 0, 6, "shadow", {}),
        ("Chill of Grief", "debuff", 0, 4, 8, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -8}}),
    ],
    # Burned Farmstead (L4-6)
    "blighted_scarecrow": [
        ("Straw Flail", "damage", 14, 0, 0, "physical", {}),
        ("Cawing Mob", "dot", 5, 4, 0, "physical", {"duration": 3}),
    ],
    "burned_farmhand": [
        ("Charred Pitchfork", "damage", 13, 0, 0, "physical", {}),
        ("Ash Cloud", "debuff", 0, 4, 0, "fire",
         {"duration": 2, "stat_mods": {"agility": -8}}),
    ],
    # Scarlet Forecourt (L5-6)
    "scarlet_torchbearer": [
        ("Torch Hurl", "damage", 15, 0, 10, "fire", {}),
        ("Kindle", "dot", 5, 4, 8, "fire", {"duration": 3}),
    ],
    "scarlet_picket": [
        ("Halberd Chop", "damage", 16, 0, 0, "physical", {}),
        ("Sunder", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -12}}),
    ],
    # Night Web's Hollow (L5-7) - shared names get their own kits instead of the generic zombie kit
    "brood_hatchling": [
        ("Hatchling Bite", "damage", 12, 0, 0, "physical", {}),
        ("Skitter Nip", "damage", 14, 3, 0, "physical", {}),
    ],
    "web_wrapped_corpse": [
        ("Cocoon Slam", "damage", 15, 0, 0, "physical", {}),
        ("Silk Bind", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -10}}),
    ],
    "ravenclaw_drudger": [
        ("Drudger's Blow", "damage", 16, 0, 0, "physical", {}),
        ("Rotting Bite", "dot", 6, 3, 0, "physical", {"duration": 3}),
    ],
    # Scarlet Crypt (L6-8)
    "crypt_crawler": [
        ("Chitin Snap", "damage", 14, 0, 0, "physical", {}),
        ("Burrow Venom", "dot", 5, 3, 0, "nature", {"duration": 3}),
    ],
    # ---- named rares (3 abilities each) ----
    "mawgrin_the_gaunt": [
        ("Rending Bite", "damage", 14, 0, 0, "physical", {}),
        ("Plague Bite", "dot", 5, 3, 0, "nature", {"duration": 3}),
        ("Pack Howl", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 10}}),
    ],
    "ossric_the_unburied": [
        ("Grave Cleave", "damage", 17, 0, 0, "physical", {}),
        ("Soul Rot", "dot", 6, 4, 0, "shadow", {"duration": 3}),
        ("Shroud of Dust", "buff", 0, 6, 0, "shadow",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 14}}),
    ],
    "goldfang": [
        ("Goldfang Bite", "damage", 18, 0, 0, "physical", {}),
        ("Gilded Venom", "dot", 6, 3, 0, "nature", {"duration": 3}),
        ("Web Snare", "debuff", 0, 5, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -14}}),
    ],
    "mourning_wren": [
        ("Keening Bolt", "damage", 18, 0, 10, "shadow", {}),
        ("Grief-Struck", "debuff", 0, 5, 10, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -12}}),
        ("Lament", "heal", 26, 6, 14, "shadow", {}),
    ],
    "gaffer_thorne": [
        ("Rusted Scythe", "damage", 20, 0, 0, "physical", {}),
        ("Harvest Wound", "dot", 7, 4, 0, "physical", {"duration": 3}),
        ("Hard Cold Earth", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 16}}),
    ],
    "sergeant_halbrook": [
        ("Halberd Cleave", "damage", 21, 0, 0, "physical", {}),
        ("Sunder Armor", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -14}}),
        ("Rally Cry", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "hatchery_warden_skrix": [
        ("Skrix's Fang", "damage", 19, 0, 0, "physical", {}),
        ("Silk Spit", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -14}}),
        ("Egg Guard", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 14}}),
    ],
    "pale_weaver": [
        ("Pale Fang", "damage", 20, 0, 0, "physical", {}),
        ("Weaver's Venom", "dot", 7, 3, 0, "nature", {"duration": 3}),
        ("Shroud Web", "debuff", 0, 5, 0, "physical",
         {"duration": 2, "is_aoe": True, "stat_mods": {"agility": -16}}),
    ],
    "valdric_bonewarden": [
        ("Bone Hammer", "damage", 28, 0, 0, "physical", {}),
        ("Marrow Rot", "dot", 9, 4, 0, "shadow", {"duration": 3}),
        ("Bone Armor", "buff", 0, 6, 0, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "brother_wystan": [
        ("Wystan's Smite", "damage", 26, 0, 20, "holy", {}),
        ("Cleansing Flame", "dot", 9, 4, 16, "fire", {"duration": 3}),
        ("Penitent Prayer", "heal", 40, 6, 24, "holy", {}),
    ],
}

TIRISFAL_REBUILD_KITS = {
    # ---- Tirisfal rebuild content pass (2026-10-22): Western / Eastern Tirisfal rosters on the real subzones ----
    # Western: Whispering Shore (L6-9)
    "vile_fin_puddlejumper": [
        ("Spear Poke", "damage", 17, 0, 0, "physical", {}),
        ("Gurgling Cry", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -10}}),
    ],
    "vile_fin_oracle": [
        ("Tidal Bolt", "damage", 19, 0, 10, "nature", {}),
        ("Soothing Tide", "heal", 24, 6, 12, "nature", {}),
    ],
    # Stillwater Pond (L5-8)
    "stillwater_lurker": [
        ("Pincer Snap", "damage", 17, 0, 0, "physical", {}),
        ("Silt Cloud", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -10}}),
    ],
    # Agamand Family Crypt (L8-10)
    "agamand_crypt_wight": [
        ("Grave Strike", "damage", 24, 0, 0, "physical", {}),
        ("Crypt Chill", "debuff", 0, 4, 0, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -12}}),
    ],
    # Garren's Haunt (L5-9)
    "rot_hide_mongrel": [
        ("Mangy Bite", "damage", 16, 0, 0, "physical", {}),
        ("Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 10}}),
    ],
    "rot_hide_gnoll": [
        ("Club Smash", "damage", 21, 0, 0, "physical", {}),
        ("Sickly Roar", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -10}}),
    ],
    "rot_hide_graverobber": [
        ("Shovel Bash", "damage", 22, 0, 0, "physical", {}),
        ("Grave Dust", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -10}}),
    ],
    # Eastern: Faol's Rest, Venomweb Vale, Ruins of Lordaeron, Cult of the Damned (L8-11)
    "faols_restless": [
        ("Rusted Blade", "damage", 26, 0, 0, "physical", {}),
        ("Tomb Chill", "debuff", 0, 4, 0, "shadow",
         {"duration": 3, "stat_mods": {"armor": -14}}),
    ],
    "venomweb_skitterer": [
        ("Venom Bite", "damage", 24, 0, 0, "physical", {}),
        ("Web Spit", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "lordaeron_remnant": [
        ("Fallen Banner Strike", "damage", 23, 0, 0, "physical", {}),
        ("Dust of Ages", "debuff", 0, 4, 0, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -12}}),
    ],
    "cult_acolyte": [
        ("Shadow Bolt", "damage", 26, 0, 12, "shadow", {}),
        ("Drain Strength", "debuff", 0, 4, 10, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -14}}),
    ],
    "cult_fanatic": [
        ("Cultist Dagger", "damage", 25, 0, 0, "physical", {}),
        ("Frenzied Devotion", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    # ---- named rares / bosses (3 abilities each, sub-20) ----
    "ressan_the_needler": [
        ("Needle Bite", "damage", 18, 0, 0, "physical", {}),
        ("Needle Venom", "dot", 6, 3, 0, "nature", {"duration": 3}),
        ("Shrill Screech", "debuff", 0, 5, 0, "physical",
         {"duration": 3, "stat_mods": {"attack_power": -10}}),
    ],
    "old_gillrot": [
        ("Brine Bolt", "damage", 23, 0, 12, "nature", {}),
        ("Gill Rot", "dot", 8, 3, 10, "nature", {"duration": 3}),
        ("Mending Brine", "heal", 30, 6, 14, "nature", {}),
    ],
    "meven_korgal": [
        ("Crusader Strike", "damage", 24, 0, 0, "physical", {}),
        ("Zealous Smite", "damage", 26, 2, 16, "magic", {}),
        ("Oath of the Crusade", "buff", 0, 6, 12, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "goodman_solliden": [
        ("Pitchfork Thrust", "damage", 25, 0, 0, "physical", {}),
        ("Sour Harvest", "dot", 9, 3, 0, "physical", {"duration": 3}),
        ("Scarecrow's Vigil", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 16}}),
    ],
    "murk_the_bloated": [
        ("Bloated Slam", "damage", 22, 0, 0, "physical", {}),
        ("Bog Rot", "dot", 8, 3, 0, "nature", {"duration": 4}),
        ("Swell", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 14}}),
    ],
    "captain_dargol": [
        ("Family Blade", "damage", 29, 0, 0, "physical", {}),
        ("Dargol's Curse", "debuff", 0, 4, 0, "shadow",
         {"duration": 3, "stat_mods": {"armor": -16}}),
        ("Ancestral Fury", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "maggot_eye": [
        ("Maggot Club", "damage", 26, 0, 0, "physical", {}),
        ("Festering Wound", "dot", 10, 3, 0, "physical", {"duration": 4}),
        ("Gnoll War Cry", "buff", 0, 6, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "reaper_lord_aldous": [
        ("Harvest Cleave", "damage", 27, 0, 0, "physical", {}),
        ("Soul Reap", "dot", 10, 3, 0, "shadow", {"duration": 4}),
        ("Death's Hour", "buff", 0, 6, 0, "shadow",
         {"duration": 3, "self_only": True, "stat_mods": {"armor": 16}}),
    ],
    "bethor_iceshard": [
        ("Iceshard Bolt", "damage", 30, 0, 14, "magic", {}),
        ("Frostbite Shackle", "debuff", 0, 5, 12, "magic",
         {"duration": 3, "stat_mods": {"agility": -16}}),
        ("Ice Barrier", "buff", 0, 6, 14, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "captain_melrache": [
        ("Zealot's Cleave", "damage", 32, 0, 0, "physical", {}),
        ("Crusader's Wrath", "dot", 11, 3, 0, "physical", {"duration": 4}),
        ("Rallying Banner", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    "crusader_brennic": [
        ("Crusader Strike", "damage", 27, 0, 0, "physical", {}),
        ("Shield Bash", "debuff", 0, 4, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -14}}),
        ("Righteous Fury", "buff", 0, 6, 12, "magic",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "mother_venomweb": [
        ("Venomous Fang", "damage", 30, 0, 0, "physical", {}),
        ("Venom Cloud", "dot", 12, 3, 0, "nature", {"duration": 4}),
        ("Web Cocoon", "debuff", 0, 5, 0, "physical",
         {"duration": 2, "stat_mods": {"agility": -18}}),
    ],
    "captain_vachon": [
        ("Vachon's Blade", "damage", 29, 0, 0, "physical", {}),
        ("Piercing Strike", "debuff", 0, 4, 0, "physical",
         {"duration": 3, "stat_mods": {"armor": -16}}),
        ("Stand Fast", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 22}}),
    ],
    "cult_overseer_thaddeus": [
        ("Shadow Lash", "damage", 31, 0, 14, "shadow", {}),
        ("Curse of Weakness", "debuff", 0, 5, 12, "shadow",
         {"duration": 3, "stat_mods": {"attack_power": -16}}),
        ("Dark Vigor", "buff", 0, 6, 14, "shadow",
         {"duration": 4, "self_only": True, "stat_mods": {"armor": 18}}),
    ],
    # ---- Scourge Cave (L10-13): the Cult of the Damned's cellar opens onto the bones of an Abomination
    "scourge_warrior": [      # was only in legacy_kits.json (12/15 damage); rescaled to the L10-12 band
        ("Bone Blade", "damage", 26, 0, 0, "physical", {}),
        ("Undying Swing", "damage", 31, 3, 0, "physical", {}),
    ],
    "scourge_ghoul": [
        ("Rending Claws", "damage", 27, 0, 0, "physical", {}),
        ("Ghoulish Frenzy", "buff", 0, 5, 0, "physical",
         {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 14}}),
    ],
    "ghoulmaster_krag": [
        ("Bone Cleaver", "damage", 32, 0, 0, "physical", {}),
        ("Rotting Grip", "dot", 12, 4, 0, "shadow", {"duration": 4}),
        ("Call the Pack", "buff", 0, 6, 0, "physical",
         {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    "plaguemaster_orvyn": [
        ("Plague Bolt", "damage", 30, 0, 14, "nature", {}),
        ("Festering Wound", "dot", 11, 4, 10, "nature", {"duration": 4}),
        ("Virulent Mist", "debuff", 0, 5, 12, "nature",
         {"duration": 3, "stat_mods": {"armor": -16}}),
    ],
}


PLAGUE_DEPTHS_KITS = {
    # ================= PLAGUE DEPTHS (L30-34, 5 bosses, 4 abilities each; trash 2-3) ===============================
    # Cistern vermin (28-31)
    "pd_plagued_rat": [
        ("Infected Bite", "damage", 27, 0, 0, "physical", {}),
        ("Plague Spit", "dot", 10, 3, 0, "nature", {"duration": 4}),
    ],
    "pd_rot_worm": [
        ("Decaying Bite", "damage", 30, 0, 0, "nature", {}),
        ("Rotting Wound", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    "pd_plagued_hound": [
        ("Diseased Bite", "damage", 31, 0, 0, "physical", {}),
        ("Pounce", "damage", 40, 3, 0, "physical", {}),
        ("Pestilent Scratch", "dot", 11, 3, 0, "nature", {"duration": 4}),
    ],
    "pd_plague_spore": [
        ("Spore Cloud", "damage", 25, 0, 0, "nature", {"is_aoe": True}),
        ("Choking Dust", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -22}}),
    ],
    "pd_plague_zombie": [
        ("Shambling Fist", "damage", 32, 0, 0, "physical", {}),
        ("Putrid Slam", "damage", 43, 3, 0, "shadow", {}),
        ("Undead Tenacity", "buff", 0, 6, 0, "shadow", {"duration": 3, "self_only": True, "stat_mods": {"armor": 44}}),
    ],
    # The Court (29-32)
    "pd_forsaken_traitor": [
        ("Betrayer's Blade", "damage", 33, 0, 0, "physical", {}),
        ("Sinister Strike", "damage", 41, 3, 0, "physical", {}),
        ("Curse of Betrayal", "debuff", 0, 4, 0, "shadow", {"duration": 3, "stat_mods": {"attack_power": -24}}),
    ],
    "pd_forsaken_witch": [
        ("Shadow Bolt", "damage", 34, 0, 22, "shadow", {}),
        ("Life Drain", "damage", 37, 3, 26, "shadow", {}),
        ("Hex Curse", "debuff", 0, 4, 24, "shadow", {"duration": 3, "stat_mods": {"intellect": -24}}),
    ],
    "pd_infected_retainer": [
        ("Rusted Halberd", "damage", 34, 0, 0, "physical", {}),
        ("Retainer's Duty", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 52}}),
        ("Sepsis", "dot", 12, 3, 0, "nature", {"duration": 4}),
    ],
    "pd_blighted_courtier": [
        ("Gilded Venom", "damage", 34, 0, 22, "nature", {}),
        ("Whispered Rot", "dot", 13, 3, 24, "shadow", {"duration": 4}),
        ("Fawning Curse", "debuff", 0, 5, 22, "shadow", {"duration": 3, "stat_mods": {"strength": -24}}),
    ],
    # The Lab (30-33)
    "pd_plague_surgeon": [
        ("Plague Injection", "damage", 34, 0, 22, "nature", {}),
        ("Corpse Explosion", "damage", 49, 4, 30, "shadow", {"is_aoe": True}),
        ("Dark Mending", "heal", 56, 5, 28, "shadow", {}),
    ],
    "pd_blight_cultist": [
        ("Plague Bolt", "damage", 34, 0, 22, "shadow", {}),
        ("Blight", "dot", 13, 3, 24, "nature", {"duration": 4}),
        ("Wither", "debuff", 0, 4, 22, "shadow", {"duration": 3, "stat_mods": {"stamina": -20}}),
    ],
    "pd_failed_experiment": [
        ("Flailing Limbs", "damage", 36, 0, 0, "physical", {}),
        ("Unstable Mass", "damage", 50, 4, 0, "nature", {"is_aoe": True}),
        ("Stitched Hide", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 60}}),
    ],
    "pd_plague_abomination": [
        ("Crushing Blow", "damage", 40, 0, 0, "physical", {}),
        ("Putrid Explosion", "damage", 52, 3, 0, "shadow", {"is_aoe": True}),
        ("Plague Aura", "debuff", 0, 5, 0, "shadow", {"duration": 3, "is_aoe": True, "stat_mods": {"armor": -26}}),
    ],
    # ---- bosses
    "pd_plagueweaver_vex": [        # L31 - the Weaving Hall: a thread of plague for everyone
        ("Plague Wave", "damage", 45, 0, 40, "shadow", {"is_aoe": True}),
        ("Pestilence", "dot", 19, 3, 38, "shadow", {"duration": 5}),
        ("Wasting Thread", "debuff", 0, 4, 36, "shadow", {"duration": 3, "stat_mods": {"attack_power": -30, "intellect": -30}}),
        ("Shadow Shield", "buff", 0, 7, 45, "shadow", {"duration": 4, "self_only": True, "stat_mods": {"armor": 74}}),
    ],
    "pd_infected_noble": [          # L32 - the Throne of Rot
        ("Noble's Blade", "damage", 50, 0, 0, "physical", {}),
        ("Corruption Strike", "damage", 61, 3, 0, "shadow", {}),
        ("Curse of Nobility", "debuff", 0, 4, 0, "shadow", {"duration": 3, "stat_mods": {"strength": -32, "intellect": -32}}),
        ("Undead Might", "buff", 0, 7, 0, "shadow", {"duration": 4, "self_only": True, "stat_mods": {"attack_power": 50}}),
    ],
    "pd_plague_keeper_voss": [      # L32 - the Blight Archive: keeps the plague like a library
        ("Archive Strike", "damage", 49, 0, 40, "shadow", {}),
        ("Forbidden Knowledge", "damage", 65, 3, 55, "shadow", {}),
        ("Plague Transmission", "dot", 21, 3, 38, "nature", {"duration": 5, "is_aoe": True}),
        ("Keeper's Vigor", "heal", 86, 6, 50, "shadow", {}),
    ],
    "pd_vile_plague_abomination": [  # L33 - the Vault of Flesh
        ("Corrupted Slam", "damage", 54, 0, 0, "physical", {}),
        ("Putrid Explosion", "damage", 68, 3, 0, "shadow", {"is_aoe": True}),
        ("Plague Aura", "debuff", 0, 4, 0, "shadow", {"duration": 3, "is_aoe": True, "stat_mods": {"armor": -42}}),
        ("Abomination Roar", "buff", 0, 7, 0, "shadow", {"duration": 4, "self_only": True, "stat_mods": {"armor": 90, "stamina": 40}}),
    ],
    "pd_dark_sorcerer_zulketh": [   # L34 - the Plague Heart (final boss)
        ("Plague Bolt", "damage", 56, 0, 48, "shadow", {}),
        ("Plague Heart Power", "damage", 79, 3, 70, "shadow", {}),
        ("Corruption Hex", "dot", 24, 3, 45, "shadow", {"duration": 5}),
        ("Sorcerer's Aegis", "buff", 0, 7, 60, "shadow", {"duration": 4, "self_only": True, "stat_mods": {"armor": 84, "intellect": 40}}),
    ],
}

SILVERPINE_NORTH_KITS = {
    # ================= SILVERPINE NORTH rebuild (2026-10-23): L12-17 =============================================
    # Olsen's Farthing (12-14)
    "farthing_hound": [
        ("Rabid Bite", "damage", 24, 0, 0, "physical", {}),
        ("Feral Lunge", "damage", 31, 3, 0, "physical", {}),
    ],
    "risen_farmhand": [
        ("Pitchfork Jab", "damage", 25, 0, 0, "physical", {}),
        ("Grave Rot", "dot", 8, 4, 0, "nature", {"duration": 4}),
    ],
    "old_hob": [                      # rare hound, Olsen's Farthing (L14)
        ("Maul", "damage", 33, 0, 0, "physical", {}),
        ("Rending Bite", "dot", 12, 3, 0, "physical", {"duration": 4}),
        ("Hob's Howl", "buff", 0, 5, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    # The Dead Field (13-15)
    "dead_field_harrower": [
        ("Rusty Scythe", "damage", 27, 0, 0, "physical", {}),
        ("Harrowing Gaze", "debuff", 0, 4, 0, "shadow", {"duration": 3, "stat_mods": {"attack_power": -14}}),
    ],
    "blighted_crow": [
        ("Carrion Peck", "damage", 22, 0, 0, "physical", {}),
        ("Pestilent Cry", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -14}}),
    ],
    "gaunt_scarecrow_king": [         # rare, the Dead Field (L15)
        ("Straw-King's Blow", "damage", 35, 0, 0, "physical", {}),
        ("Crow Swarm", "damage", 26, 3, 0, "physical", {"is_aoe": True}),
        ("Hollow Crown", "debuff", 0, 5, 0, "shadow", {"duration": 3, "stat_mods": {"armor": -18}}),
    ],
    # Malden's Orchard (14-16)
    "orchard_shambler": [
        ("Rotting Fist", "damage", 28, 0, 0, "physical", {}),
        ("Windfall Rot", "dot", 9, 4, 0, "nature", {"duration": 4}),
    ],
    "windfall_wasp": [
        ("Stinger", "damage", 24, 0, 0, "nature", {}),
        ("Fevered Sting", "dot", 8, 3, 0, "nature", {"duration": 4}),
    ],
    "orchardkeeper_gnarl": [          # rare treant, Malden's Orchard (L16)
        ("Root Slam", "damage", 37, 0, 0, "physical", {}),
        ("Thorn Barrage", "damage", 30, 3, 0, "nature", {"is_aoe": True}),
        ("Bark Hide", "buff", 0, 6, 0, "nature", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
    ],
    # The Skittering Dark (15-17)
    "venomfang_skitterer": [
        ("Venomfang Bite", "damage", 29, 0, 0, "physical", {}),
        ("Venom Spit", "dot", 10, 3, 0, "nature", {"duration": 4}),
    ],
    "longleg_the_stalker": [          # rare spider, the Skittering Dark (L17)
        ("Stalker's Lunge", "damage", 38, 0, 0, "physical", {}),
        ("Paralytic Venom", "dot", 14, 3, 0, "nature", {"duration": 4}),
        ("Web Snare", "debuff", 0, 5, 0, "physical", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
}

SILVERPINE_SOUTH_KITS = {
    # ================= SILVERPINE SOUTH rebuild (2026-10-23): L15-20 =============================================
    # Bucklebree Farm (15-17)
    "blightfed_hog": [
        ("Tusk Gore", "damage", 28, 0, 0, "physical", {}),
        ("Festering Tusk", "dot", 9, 4, 0, "nature", {"duration": 4}),
    ],
    "barn_ghoul": [
        ("Hay-Rot Claw", "damage", 30, 0, 0, "physical", {}),
        ("Mouldering Touch", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"armor": -16}}),
    ],
    "tusk_mother_gorra": [            # rare sow, Bucklebree Farm (L17)
        ("Gore", "damage", 40, 0, 0, "physical", {}),
        ("Trampling Charge", "damage", 30, 3, 0, "physical", {"is_aoe": True}),
        ("Mother's Rage", "buff", 0, 6, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 24}}),
    ],
    # Deep Elem Mine (16-18)
    "deep_elem_digger": [
        ("Pick Strike", "damage", 31, 0, 0, "physical", {}),
        ("Rock Throw", "damage", 38, 3, 0, "physical", {}),
    ],
    "mine_shambler": [
        ("Crushing Fist", "damage", 33, 0, 0, "physical", {}),
        ("Cave Dust", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "gnawbone_foreman": [             # rare kobold foreman, Deep Elem Mine (L18)
        ("Bone Cleaver", "damage", 42, 0, 0, "physical", {}),
        ("Cave-In", "damage", 32, 3, 0, "physical", {"is_aoe": True}),
        ("Foreman's Roar", "buff", 0, 6, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 24}}),
    ],
    # Valgan's Field (16-18)
    "field_deserter": [
        ("Backstab", "damage", 33, 0, 0, "physical", {}),
        ("Bleeding Cut", "dot", 11, 3, 0, "physical", {"duration": 4}),
    ],
    "battlefield_wight": [
        ("Rusted Sword", "damage", 34, 0, 0, "physical", {}),
        ("Dread Chill", "debuff", 0, 4, 0, "shadow", {"duration": 3, "stat_mods": {"attack_power": -16}}),
    ],
    # Berard's Talon (17-19)
    "crag_stalker": [
        ("Pounce", "damage", 35, 0, 0, "physical", {}),
        ("Rake", "dot", 11, 3, 0, "physical", {"duration": 4}),
    ],
    "talon_wraith": [
        ("Shadow Bolt", "damage", 35, 0, 18, "shadow", {}),
        ("Keening Wail", "debuff", 0, 4, 16, "shadow", {"duration": 3, "stat_mods": {"intellect": -16}}),
    ],
    "berard_the_forgotten": [         # rare ghost, Berard's Talon (L19)
        ("Phantom Blow", "damage", 44, 0, 0, "shadow", {}),
        ("Soul Rend", "dot", 15, 3, 0, "shadow", {"duration": 4}),
        ("Wailing Grief", "debuff", 0, 5, 0, "shadow", {"duration": 3, "stat_mods": {"armor": -20}}),
    ],
    # Beren's Peril (18-20)
    "peril_packmaster": [
        ("Savage Claw", "damage", 37, 0, 0, "physical", {}),
        ("Rend Flesh", "dot", 12, 3, 0, "physical", {"duration": 4}),
        ("Pack Howl", "buff", 0, 6, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    "bloodmaw_alpha": [               # rare alpha worgen, Beren's Peril (L20)
        ("Maul", "damage", 46, 0, 0, "physical", {}),
        ("Rending Bite", "dot", 16, 3, 0, "physical", {"duration": 4}),
        ("Alpha's Howl", "buff", 0, 6, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 26}}),
    ],
    # Greymane Wall (18-20)
    "wallbreaker_worgen": [
        ("Leap Slash", "damage", 36, 0, 0, "physical", {}),
        ("Frenzy", "buff", 0, 5, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 18}}),
    ],
    "wall_wraith": [
        ("Spectral Blade", "damage", 37, 0, 0, "shadow", {}),
        ("Grave Chill", "debuff", 0, 4, 0, "shadow", {"duration": 3, "stat_mods": {"armor": -18}}),
    ],
    "wall_warden": [                  # rare ghost warden, the Greymane Wall (L20)
        ("Warden's Strike", "damage", 46, 0, 0, "physical", {}),
        ("Cleave", "damage", 34, 3, 0, "physical", {"is_aoe": True}),
        ("Shield Wall", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 50}}),
    ],
    # Ambermill (18-20)
    "ambermill_ghost_mage": [
        ("Frostbolt", "damage", 36, 0, 20, "frost", {}),
        ("Arcane Missiles", "damage", 44, 3, 26, "arcane", {}),
    ],
    "ambermill_warden": [
        ("Arcane Slam", "damage", 37, 0, 0, "arcane", {}),
        ("Ward of the Mill", "buff", 0, 6, 0, "arcane", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
    ],
    "magister_quillfire": [           # rare ghost magister, Ambermill (L20)
        ("Arcane Barrage", "damage", 46, 0, 28, "arcane", {}),
        ("Quill-Fire", "dot", 16, 3, 24, "fire", {"duration": 4}),
        ("Mana Ward", "buff", 0, 6, 26, "arcane", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40, "intellect": 24}}),
    ],
    # The Decrepit Ferry (16-18)
    "drowned_deckhand": [
        ("Boat Hook", "damage", 31, 0, 0, "physical", {}),
        ("Waterlogged", "debuff", 0, 4, 0, "nature", {"duration": 3, "stat_mods": {"agility": -16}}),
    ],
    "drowned_ferryman": [             # rare ghost, the Decrepit Ferry (L18)
        ("Oar Smash", "damage", 41, 0, 0, "physical", {}),
        ("Drowning Pull", "dot", 14, 3, 0, "nature", {"duration": 4}),
        ("Lakewater Curse", "debuff", 0, 5, 0, "nature", {"duration": 3, "stat_mods": {"attack_power": -20}}),
    ],
}

SILVERPINE_DUNGEON_KITS_2 = {
    # ================= SILVERPINE dungeon pass (2026-10-23): Widow's Lair 17-19, Ambermill Tower 21-23, Shadowfang Keep 19-25 =====
    # Widow's Lair
    "lair_hatchling": [
        ("Needle Bite", "damage", 27, 0, 0, "physical", {}),
        ("Hatchling Venom", "dot", 8, 3, 0, "nature", {"duration": 4}),
    ],
    "silkbound_weaver": [
        ("Silk Bolt", "damage", 31, 0, 14, "nature", {}),
        ("Binding Silk", "debuff", 0, 4, 12, "physical", {"duration": 3, "stat_mods": {"agility": -18}}),
    ],
    "brood_warden": [
        ("Chitin Slam", "damage", 33, 0, 0, "physical", {}),
        ("Harden Carapace", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
    ],
    "venom_stalker": [
        ("Ambush Fang", "damage", 35, 0, 0, "physical", {}),
        ("Paralytic Sting", "dot", 12, 3, 0, "nature", {"duration": 4}),
    ],
    # Ambermill Tower
    "tome_wraith": [
        ("Page-Cut Bolt", "damage", 38, 0, 16, "shadow", {}),
        ("Forgotten Footnote", "debuff", 0, 4, 14, "shadow", {"duration": 3, "stat_mods": {"intellect": -20}}),
    ],
    "animated_spellblade": [
        ("Rune-Etched Slash", "damage", 40, 0, 0, "magic", {}),
        ("Arcane Ward", "buff", 0, 6, 0, "magic", {"duration": 3, "self_only": True, "stat_mods": {"magic_resistance": 30}}),
    ],
    "forsaken_alchemist": [
        ("Acid Flask", "damage", 38, 0, 14, "nature", {}),
        ("Unstable Brew", "dot", 13, 3, 14, "nature", {"duration": 4}),
    ],
    "magister_hawren": [              # boss, the Archivist's Gallery (L22)
        ("Arcane Missiles", "damage", 38, 0, 14, "magic", {}),
        ("Frost Nova", "damage", 30, 3, 0, "frost", {"is_aoe": True}),
        ("Archivist's Hex", "debuff", 0, 4, 12, "magic", {"duration": 3, "stat_mods": {"intellect": -20}}),
        ("Mana Shield", "buff", 0, 6, 0, "magic", {"duration": 4, "self_only": True, "stat_mods": {"armor": 45}}),
    ],
    "apothecary_helbrim": [           # boss, the Alchemy Lab (L23)
        ("Acid Splash", "damage", 40, 0, 14, "nature", {}),
        ("Volatile Mixture", "dot", 19, 3, 14, "nature", {"duration": 4}),
        ("Rot Flask", "damage", 32, 3, 12, "nature", {"is_aoe": True}),
        ("Elixir of Fury", "buff", 0, 6, 0, "nature", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 26}}),
    ],
    "archmage_atiesh": [              # final boss, the Observatory (L23)
        ("Arcane Barrage", "damage", 42, 0, 14, "magic", {}),
        ("Orrery Beam", "damage", 54, 2, 16, "magic", {}),
        ("Void Collapse", "damage", 34, 3, 12, "shadow", {"is_aoe": True}),
        ("Banishing Pulse", "debuff", 0, 4, 14, "magic", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
    # Shadowfang Keep
    "keep_worg": [
        ("Ripping Bite", "damage", 32, 0, 0, "physical", {}),
        ("Gnashing Frenzy", "buff", 0, 5, 0, "physical", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 16}}),
    ],
    "slavering_worg": [
        ("Maul", "damage", 34, 0, 0, "physical", {}),
        ("Slavering Wound", "dot", 11, 3, 0, "physical", {"duration": 4}),
    ],
    "wolfguard_worg": [
        ("Shoulder Barge", "damage", 36, 0, 0, "physical", {}),
        ("Thick Hide", "buff", 0, 6, 0, "physical", {"duration": 4, "self_only": True, "stat_mods": {"armor": 40}}),
    ],
    "shadowfang_moonwalker": [
        ("Moonlit Bolt", "damage", 37, 0, 16, "shadow", {}),
        ("Howling Dirge", "debuff", 0, 4, 14, "shadow", {"duration": 3, "stat_mods": {"attack_power": -16}}),
    ],
    "shadowfang_darksoul": [
        ("Shadow Bolt", "damage", 38, 0, 16, "shadow", {}),
        ("Curse of Agony", "dot", 13, 3, 14, "shadow", {"duration": 4}),
    ],
    "arugal_voidwalker": [
        ("Torment", "damage", 38, 0, 0, "shadow", {}),
        ("Consuming Shadows", "dot", 13, 3, 0, "shadow", {"duration": 4}),
    ],
    "haunted_servitor": [
        ("Spectral Strike", "damage", 38, 0, 0, "shadow", {}),
        ("Chilling Touch", "debuff", 0, 4, 0, "shadow", {"duration": 3, "stat_mods": {"armor": -22}}),
    ],
    "tormented_officer": [
        ("Phantom Blade", "damage", 40, 0, 0, "shadow", {}),
        ("Last Orders", "buff", 0, 6, 0, "shadow", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 20}}),
    ],
    "wailing_guardsman": [
        ("Guardsman's Thrust", "damage", 35, 0, 0, "physical", {}),
        ("Wail of the Fallen", "debuff", 0, 4, 12, "shadow", {"duration": 3, "stat_mods": {"intellect": -16}}),
    ],
    "deathsworn_captain": [
        ("Captain's Cleave", "damage", 42, 0, 0, "physical", {}),
        ("Death's Oath", "buff", 0, 6, 0, "shadow", {"duration": 3, "self_only": True, "stat_mods": {"attack_power": 24}}),
    ],
    "son_of_arugal": [
        ("Lupine Slash", "damage", 42, 0, 0, "physical", {}),
        ("Rending Claws", "dot", 15, 3, 0, "physical", {"duration": 4}),
    ],
    "lupine_horror": [
        ("Crushing Lunge", "damage", 46, 0, 0, "physical", {}),
        ("Horrid Howl", "debuff", 0, 4, 0, "physical", {"duration": 3, "stat_mods": {"agility": -20}}),
    ],
}

ALL_KITS = {}
for _group in (BEAST_KITS, VERMIN_KITS, CENTAUR_KITS, QUILBOAR_KITS,
               TROLL_KITS, TROGG_KITS, HARPY_KITS, HUMANOID_KITS, SCARLET_KITS,
               CULTIST_KITS, RAGEFIRE_BOSS_KITS, ECHO_ISLES_KITS, VALLEY_OF_TRIALS_KITS,
               ASHENVALE_KITS, FENRIS_SILVERPINE_KITS, TIRISFAL_KITS,
               BLACKFATHOM_DEEPS_KITS, WAILING_CAVERNS_KITS,
               BRISTLEBACK_KITS, BANDIT_KITS, DUROTAR_KITS, DUROTAR_OPEN_KITS, DUROTAR_CAVE_KITS, RAGEFIRE_CONTENT_KITS, ECHO_CONTENT_KITS, CENTRAL_BARRENS_KITS, SOUTHERN_BARRENS_KITS, BROODSPIRAL_KITS, RAZORFEN_KITS, WAILING_CONTENT_KITS, NORTHERN_BARRENS_KITS,
               BARRENS_MURLOC_KITS, BARRENS_MISC_KITS, DEMON_KITS,
               ELEMENTAL_KITS, AQUATIC_KITS, UNDEAD_KITS,
               SILVERPINE_DUNGEON_KITS, ASHENVALE_DUNGEON_KITS, DEATHKNELL_KITS, TIRISFAL_REBUILD_KITS, PLAGUE_DEPTHS_KITS, SILVERPINE_NORTH_KITS, SILVERPINE_SOUTH_KITS, SILVERPINE_DUNGEON_KITS_2):
    for _k, _v in _group.items():
        if _k in ALL_KITS:
            raise ValueError(f"Duplicate kit id: {_k}")
        ALL_KITS[_k] = _v


def kit_to_json(abilities):
    """Expand the authoring tuples into the runtime JSON shape."""
    out = []
    for i, (name, kind, dmg, cd, mana, school, extra) in enumerate(abilities):
        entry = {
            "name": name,
            "kind": kind,
            "amount": dmg,
            "cooldown": cd,
            "mana_cost": mana,
            "school": school,
        }
        entry.update(extra)
        if i == 0:
            # Contract: the basic attack must always be usable, or the AI
            # can deadlock with every option on cooldown or unaffordable.
            if kind != "damage" or cd != 0:
                raise ValueError(
                    f"First ability of a kit must be a 0-cd damage "
                    f"attack; got {name} ({kind}, cd={cd})")
            # For mana casters, the basic attack is typically their filler spell.
            # It must be low-cost but not free (so they eventually run dry if
            # they keep spamming). For rage/energy, cost is ignored anyway.
        if kind in ("dot", "buff", "debuff") and "duration" not in entry:
            raise ValueError(f"{name}: {kind} requires a duration")
        if kind in ("buff", "debuff") and not entry.get("stat_mods"):
            raise ValueError(f"{name}: {kind} requires stat_mods")
        out.append(entry)
    return out


def build():
    kits = {k: kit_to_json(v) for k, v in ALL_KITS.items()}
    # kits that were hand-added straight into ability_kits.json before they had a source here (Ashenvale East commit 2427e14);
    # regenerating used to silently delete them and crash the first spawn of an Ashenvale Wraith.
    import json
    from pathlib import Path
    legacy = Path(__file__).with_name("legacy_kits.json")
    if legacy.exists():
        for k, v in json.loads(legacy.read_text()).items():
            kits.setdefault(k, v)
    return {"kits": kits}
