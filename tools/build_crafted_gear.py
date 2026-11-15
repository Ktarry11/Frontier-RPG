#!/usr/bin/env python3
"""Author every crafted gear recipe: fixed stats, written once, the same every time you craft it.

    PYTHONPATH=. python3 tools/build_crafted_gear.py            # write
    PYTHONPATH=. python3 tools/build_crafted_gear.py --check    # audit only, write nothing

Kyle, 14 Nov 2026: "why does VOIDWEAVE....give these random ass stats ... For the love of God look at wow
crafting. I DO however like how we focus specific cloth or specific leather into specific gear types."

HOW WOW DOES IT, and so how this does it:
  - every crafted item has written stats (Felcloth Hood is always the same hood);
  - the material is the identity: Felcloth is the warlock's cloth, Mooncloth the healer's, Runecloth
    the all-rounder's. Here every material has an IDENTITY (a stat split) that fits its armour type;
  - a named line made of that material can have its own identity when its name says so. Silk made
    WoW's Azure (frost), Crimson (fire) and Shadoweave lines, and here Blazethread is fire whatever
    it's woven from. The name has to say it: nothing is assigned at random.

THE NUMBERS are the loot generator's own (entities/loot_generator.py): the same stat budget, the same
armour, weapon damage and price math, so a crafted piece sits beside a quest or dungeon piece of its
level. Only the split is authored. Stats are whole numbers, nothing under a floor (no +1 dribbles),
and whatever rounding takes off goes to the identity's lead stat.

The finished item is written into each recipe as output["item"], and world/crafted_items.py builds
that. RUN THIS LAST after any tool that rewrites the recipe files (build_recipe_expansion and the
like), because those write recipes without it.
"""
import argparse
import collections
import json
import random
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from entities.item import whole                    # noqa: E402
from entities.loot_generator import LootGenerator  # noqa: E402
from world import jewelcrafting                    # noqa: E402

FILES = {
    "woodworking": ROOT / "data/crafting/recipes.json",
    "jewelcrafting": ROOT / "data/jewelcrafting/recipes.json",
    "tailoring": ROOT / "data/crafting/recipes.json",
    "engineering": ROOT / "data/crafting/recipes.json",
    "blacksmithing": ROOT / "data/blacksmithing/recipes.json",
    "leatherworking": ROOT / "data/leatherworking/recipes.json",
}

PRIMARY = {"strength", "agility", "intellect", "stamina", "spirit"}
SCHOOLS = {"fire_spell_power", "frost_spell_power", "arcane_spell_power", "shadow_spell_power",
           "nature_spell_power", "holy_spell_power"}
CASTER = SCHOOLS | {"spell_power", "healing_power", "mp5", "crit_chance_spell", "spell_penetration", "spell_hit_rating"}
PHYSICAL = {"strength", "agility", "attack_power", "crit_chance_physical", "armor_penetration_pct"}
TANK = {"defense_rating", "dodge_rating", "parry_rating", "block_rating", "block_value"}

#: What each armour type may carry. A stat outside its armour type's set fails the audit.
ALLOWED = {
    "cloth": PRIMARY - {"strength", "agility"} | CASTER | {"hit_rating", "haste"},
    # leather and mail serve both sides (rogues and druids; hunters and shaman), but never a shield's stats
    "leather": PRIMARY | CASTER | PHYSICAL | {"hit_rating", "haste", "dodge_rating"},
    # defense on mail: the Tinker tanks in it (Mechanics)
    "mail": PRIMARY | CASTER | PHYSICAL | {"hit_rating", "haste", "dodge_rating", "defense_rating"},
    "plate": PRIMARY | CASTER | PHYSICAL | TANK | {"hit_rating", "haste"},
}

# ---------------------------------------------------------------------------------------------
# IDENTITIES: name -> (stat weights, the stat template it reads as). The weights are a share of the
# budget before each stat's cost, so a 0.25 share of haste (cost 12) is far fewer points than a 0.25
# share of intellect (cost 1). At low item levels a rating rounds to nothing and that budget moves
# to the lead stat, which is right: a level 10 robe has no business carrying haste.
# ---------------------------------------------------------------------------------------------
IDENTITIES = {
    # ---- cloth. Kyle, 14 Nov: "most high end clothes should have sp or healing power primary." So
    # every cloth leads with its power (spell power, a school's power, or healing), like WoW's
    # Bloodvine Vest (27 spell damage over 13 Int) or the Mooncloth Circlet (48 healing over 18 Int).
    # The power phases in on its own: under its floor it's dropped and its share goes to the next
    # stat, so a level 8 linen robe is Int and Stamina, the way a WoW low green is.
    "starter_caster": ({"spell_power": 0.3, "intellect": 0.4, "stamina": 0.3}, "int_caster"),
    "spirit_healer": ({"healing_power": 0.4, "spirit": 0.3, "intellect": 0.3}, "spi_healer"),
    "sturdy_caster": ({"spell_power": 0.4, "intellect": 0.3, "stamina": 0.3}, "int_caster"),
    "traveller": ({"spell_power": 0.35, "stamina": 0.4, "spirit": 0.25}, "int_caster"),
    "caster": ({"spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "arcane": ({"arcane_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "arcane_crit": ({"arcane_spell_power": 0.5, "intellect": 0.2, "crit_chance_spell": 0.3}, "int_caster"),
    # SPELL hit (15 Nov 2026: hit and spell hit are separate stats - Kyle, "We need to have spell hit, physical hit")
    "precise_caster": ({"spell_power": 0.5, "intellect": 0.2, "spell_hit_rating": 0.3}, "int_caster"),
    "shadow_sturdy": ({"shadow_spell_power": 0.55, "stamina": 0.45}, "int_caster"),
    "shadow": ({"shadow_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "frost": ({"frost_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "fire": ({"fire_spell_power": 0.6, "intellect": 0.4}, "int_caster"),
    "spirit_caster": ({"spell_power": 0.55, "spirit": 0.45}, "int_caster"),
    "dark_haste": ({"shadow_spell_power": 0.45, "intellect": 0.25, "haste": 0.3}, "int_caster"),
    "healer": ({"healing_power": 0.55, "spirit": 0.25, "intellect": 0.2}, "spi_healer"),
    "nature": ({"nature_spell_power": 0.6, "spirit": 0.4}, "int_caster"),
    "blood": ({"spell_power": 0.6, "stamina": 0.4}, "int_caster"),
    "fel": ({"shadow_spell_power": 0.55, "stamina": 0.3, "intellect": 0.15}, "int_caster"),
    "death": ({"spell_power": 0.5, "intellect": 0.2, "spell_penetration": 0.3}, "int_caster"),
    "storm": ({"nature_spell_power": 0.45, "intellect": 0.25, "haste": 0.3}, "int_caster"),
    "hex": ({"shadow_spell_power": 0.55, "intellect": 0.45}, "int_caster"),
    "battlemage": ({"spell_power": 0.4, "stamina": 0.3, "crit_chance_spell": 0.3}, "int_caster"),
    "high_healer": ({"healing_power": 0.55, "intellect": 0.25, "spirit": 0.2}, "spi_healer"),
    "void": ({"shadow_spell_power": 0.5, "intellect": 0.3, "stamina": 0.2}, "int_caster"),
    # holy damage (Sun Cleric, Templar, a smiting Priest): Sunheart, the woodworking expansion's top wood
    "holy": ({"holy_spell_power": 0.6, "intellect": 0.4}, "int_caster"),

    # ---- leather and mail. Kyle, 14 Nov: "It's just so odd to see high end gear with no attack
    # power." So every physical identity leads with attack power (2 AP for a point of Strength or
    # Agility), and it phases in the same way a cloth's power does.
    "agi_starter": ({"attack_power": 0.3, "agility": 0.4, "stamina": 0.3}, "agi_physical"),
    "agility": ({"attack_power": 0.45, "agility": 0.35, "stamina": 0.2}, "agi_physical"),
    "feral": ({"attack_power": 0.45, "agility": 0.3, "stamina": 0.25}, "agi_physical"),
    "rogue_crit": ({"attack_power": 0.4, "agility": 0.3, "crit_chance_physical": 0.3}, "agi_physical"),
    "assassin": ({"attack_power": 0.4, "agility": 0.3, "hit_rating": 0.3}, "agi_physical"),
    "hunter": ({"attack_power": 0.45, "agility": 0.3, "intellect": 0.25}, "agi_int_hybrid"),
    "hunter_precise": ({"attack_power": 0.4, "agility": 0.3, "hit_rating": 0.3}, "agi_physical"),
    "hunter_crit": ({"attack_power": 0.4, "agility": 0.3, "crit_chance_physical": 0.3}, "agi_physical"),
    "bruiser": ({"attack_power": 0.45, "strength": 0.35, "stamina": 0.2}, "str_physical"),
    "earthen": ({"attack_power": 0.4, "strength": 0.3, "intellect": 0.3}, "str_int_hybrid"),
    "wildheart": ({"attack_power": 0.35, "agility": 0.35, "intellect": 0.3}, "agi_int_hybrid"),
    "bear": ({"stamina": 0.45, "agility": 0.3, "dodge_rating": 0.25}, "agi_physical"),
    "tide_healer": ({"healing_power": 0.55, "intellect": 0.3, "mp5": 0.15}, "spi_healer"),
    "mail_caster": ({"spell_power": 0.55, "intellect": 0.3, "crit_chance_spell": 0.15}, "int_caster"),

    # ---- plate (and the smith's mail and weapons)
    "melee_starter": ({"attack_power": 0.3, "strength": 0.35, "stamina": 0.35}, "str_physical"),
    "strength": ({"attack_power": 0.45, "strength": 0.35, "stamina": 0.2}, "str_physical"),
    "strength_crit": ({"attack_power": 0.4, "strength": 0.3, "crit_chance_physical": 0.3}, "str_physical"),
    "strength_hit": ({"attack_power": 0.4, "strength": 0.3, "hit_rating": 0.3}, "str_physical"),
    "crusader": ({"attack_power": 0.4, "strength": 0.3, "intellect": 0.3}, "str_int_hybrid"),
    "tank": ({"stamina": 0.5, "strength": 0.2, "defense_rating": 0.3}, "str_physical"),
    "shield_tank": ({"stamina": 0.55, "strength": 0.2, "block_value": 0.25}, "str_physical"),
    "plate_healer": ({"healing_power": 0.55, "intellect": 0.3, "mp5": 0.15}, "spi_healer"),
}

# ---------------------------------------------------------------------------------------------
# TAILORING. Cloth, for casters and healers. Each cloth: (identity, its line of flavour).
# ---------------------------------------------------------------------------------------------
TAILORING_CLOTH = {
    "linen": (None, "starter_caster", "Plain linen, stitched tight. Every tailor starts here."),
    "cotton": (None, "spirit_healer", "Soft cotton. Healers like it because it breathes."),
    "wool": (None, "sturdy_caster", "Heavy wool that keeps the cold out and the caster on their feet."),
    "hempen": (None, "traveller", "Rough hempen weave, made for the road and not for looking at."),
    "silk": (None, "caster", "Good silk. It takes a spell better than anything cheaper."),
    "mageweave": (None, "arcane", "Mageweave hums a little when you hold it near a ley line."),
    "spidersilk": (None, "precise_caster", "Spidersilk's light and tough, and it doesn't snag."),
    "netherweave": (None, "shadow_sturdy", "Netherweave is cold to the touch, and it stays that way."),
    "frostweave": (None, "frost", "Frostweave. There's always a little rime in the folds."),
    "emberweave": (None, "fire", "Emberweave stays warm in the snow, and it smells of smoke."),
    "dusk_velvet": (None, "spirit_caster", "Dusk velvet, dyed the colour of the sky an hour after sunset."),
    "gossamer": (None, "dark_haste", "Gossamer so thin you'd swear it couldn't hold a stitch."),
    "moonsilk": (None, "healer", "Moonsilk's spun at night, and healers swear by it."),
    "thistledown": (None, "nature", "Thistledown cloth, as light as the seed heads it's spun from."),
    "shadowsilk": (None, "shadow", "Shadowsilk drinks the light around it."),
    "starweave": (None, "arcane_crit", "Starweave. There are tiny points of light caught in the weave."),
    "bloodsilk": (None, "blood", "Bloodsilk's dyed in something the tailor won't name."),
    "felcloth": (None, "fel", "Felcloth. Warlocks pay well for it and don't ask where it came from."),
    "soulcloth": (None, "death", "Soulcloth is cold, and on quiet nights it whispers."),
    "windwool": (None, "storm", "Windwool never quite hangs still."),
    "imperial_silk": (None, "high_healer", "Imperial silk, the best a healer can wear that a tailor can make."),
    "voidweave": (None, "void", "Voidweave. Look at it too long and it looks back."),
}

#: Named lines that SAY what they are. First match wins. A name that only points at a place or a
#: person (Shadowfang, Taurajo, Silverpine, Arcane Scholar's) says nothing about its stats, so it
#: follows its cloth. And a line only overrides its cloth when it names a different school (see
#: FAMILY): Demonthread on gossamer is already dark cloth, so it stays gossamer's identity.
TAILORING_LINES = [
    (r"Bloodweave|Bloodsoaked", None, "blood", "A troll pattern. The red dye never fades, however often it's washed."),
    (r"Pilgrim's", None, "spirit_healer", "A pilgrim's piece, plain and well blessed."),
    (r"Hex Cloth|Fetish|Mojo", None, "hex", "Troll hexwork, with little charms sewn into the hem."),
    (r"Fireweave|Ember Cloth|Blazethread|Soulscorch", None, "fire", "Every stitch of it is a little too warm."),
    (r"Spiritweave|Mistweave", None, "spirit_healer", "A healer's robe, cut loose so it never gets in the way."),
    (r"Moonrobe|Verdant Druid|Scarlet", None, "healer", "Made for someone who keeps other people standing."),
    (r"Felweave|Felstitched|Fel-Stitched|Demonthread|Infernal", None, "fel", "Fel-stitched. The thread glows green in the dark."),
    (r"Darkweave|Shadowweave|Voidthread|Dark Elegance|Plagueweave", None, "shadow", "Dark cloth for dark work."),
    (r"Briarweave|Vine-Woven|Venom Cord|Virulent-Thread", None, "nature", "There's something green and growing woven through it."),
]

#: Identities in the same family don't override each other (see TAILORING_LINES).
FAMILY = {
    "shadow": {"shadow", "shadow_sturdy", "fel", "dark_haste", "void", "hex", "death"},
    "healer": {"spirit_healer", "healer", "high_healer"},
    "nature": {"nature", "storm"},
}


def family(ident):
    return next((f for f, members in FAMILY.items() if ident in members), ident)


# ---------------------------------------------------------------------------------------------
# LEATHERWORKING. Leather for rogues and druids, mail for hunters and shaman. Each hide:
# (the armour it makes, its identity, its flavour). A name that says Leather is leather and one that
# says Mail or Scale is mail, whatever its hide (ARMOUR_WORDS), so a "Heavy Leather Vest" is never
# chain. A named line (Moonleaf, Earthbound, Hexhide) keeps the role it announces.
# ---------------------------------------------------------------------------------------------
LEATHER_HIDES = {
    "scrap": ("leather", "agi_starter", "Scraps of leather, stitched together by someone still learning how."),
    "light": ("leather", "agility", "Light leather, soft and quiet, for anyone who'd rather not be heard."),
    "medium": ("leather", "feral", "Medium leather, oiled and supple, made for moving fast and hitting hard."),
    "heavy": ("mail", "hunter", "Heavy hide boiled hard and laced with rings, the way hunters like it."),
    "cragscale": ("mail", "earthen", "Cragscale, prised off basilisks. It's heavy and it doesn't dent."),
    "stormscale": ("mail", "storm", "Stormscale crackles a little when it's dry."),
    "thick": ("leather", "rogue_crit", "Thick leather, tanned for days. A blade has to want it to get through."),
    "dredged": ("mail", "tide_healer", "Dredged up from the deep and cured in salt. Shaman say the sea's still in it."),
    "fiendish": ("leather", "assassin", "Fiendish hide. It's warm, and it shouldn't be."),
    "stonebound": ("leather", "bear", "Stonebound hide, stiff as bark and made for standing in front."),
    "rugged": ("leather", "healer", "Rugged leather, the kind druids trust out in the wilds."),
    "hydra": ("mail", "hunter_precise", "Hydra scale. Every plate's a little different, and every one is tough."),
    "pristine": ("leather", "agility", "Pristine leather without a single flaw. Somebody was very patient."),
    "savage": ("leather", "feral", "Savage hide, still rough at the edges, like whoever wears it."),
    "frostscale": ("mail", "mail_caster", "Frostscale's cold to the touch, and so are the spells cast through it."),
    "emberscale": ("mail", "hunter_crit", "Emberscale, off something that breathed fire. It's never quite cool."),
    "mossback": ("mail", "tide_healer", "Mossback shell, with something green still growing in the cracks."),
    "netherdrake": ("mail", "earthen", "Netherdrake scale. It shifts colour when you aren't looking at it."),
    "duskfang": ("leather", "rogue_crit", "Duskfang leather drinks the light, and whoever wears it goes unnoticed."),
    "bloodtanned": ("leather", "feral", "Bloodtanned, the best hide a leatherworker can get, and it was paid for."),
}

LEATHER_LINES = [
    (r"Spirithide|Spirit Gloves|Mistweave|Moonleaf|Wildwood|Archdruid|Grovewalker|Shade-Blessed|Tidal",
     "leather", "healer", "Druid work. It smells faintly of moss and rain."),
    (r"Roughhide|Scrapbound|Toughened|Warbear|Ironhide|Warband|Ironweald|Wolfhide|Fang Leather|Quilboar|"
     r"Razorfen Tusk|Chitinous", "leather", "bruiser", "Thick, heavy leather cut for someone who swings big."),
    (r"Hexhide|Hexer's|Voodoo|Hexbinder|Scaled Isle", "leather", "wildheart",
     "Troll work, with fetishes stitched where the seams meet."),
    (r"Ironweave Mail|Earthbound|Earthwalker", "mail", "earthen",
     "Mail for a shaman who'd rather be in the middle of the fight."),
    (r"Serpent Mail|Galewind|Brine Mail|Stormcaller|Mistscale", "mail", "storm",
     "The rings chime faintly whenever a storm's coming."),
    (r"Verdant Scale|Predator|Chitinscale|Razorboar|Rotscale|Fenris|Cursed Mail", "mail", "hunter",
     "Hunter's mail, cut loose at the shoulder for drawing a bow."),
    (r"Plagued|Putrescent|Cursed Leather|Broodvenom|Venom Sac|Shadowpelt|Shadowfell|Demonhide|Nightstalker",
     "leather", "assassin", "Dark leather for work that's done quietly."),
]

# ---------------------------------------------------------------------------------------------
# BLACKSMITHING. Plate for warriors, paladins and tanks, mail for hunters and shaman, and weapons.
# Every role has a metal at every level band:
#   plate damage   tin, bronze, felslag, bloodiron, dark iron, elementium
#   plate tank     iron, mithril, thorium
#   plate holy     frostveined tin, truesilver (a paladin's strength and Intellect), arcanite
#   hunter mail    weakstone, bronze vein, deepearth, ashen steel
#   shaman mail    living copper, verdant iron
# Each metal's pieces keep the armour they were written with; the names already say plate or chain.
# ---------------------------------------------------------------------------------------------
SMITH_METALS = {
    "copper": (None, "melee_starter", "Copper, hammered thin and riveted. Every smith's first set of chain."),
    "weakstone": (None, "hunter", "Weakstone links, light enough for a hunter just starting out."),
    "tin": (None, "strength", "Tin plate. It's soft as metals go, but it turns a blade well enough."),
    "bronze_vein": (None, "hunter", "Bronze-veined scale, flexible and quiet in the brush."),
    "bronze": (None, "strength", "Bronze, the first plate a warrior can really trust."),
    "living_copper": (None, "tide_healer", "Living copper. It's warm, and it hums when someone nearby is hurt."),
    "frostveined_tin": (None, "plate_healer", "Frostveined tin with a blue sheen. Paladins say it keeps a clear head."),
    "verdant_iron": (None, "storm", "Verdant iron, green with something that isn't rust."),
    "felslag": (None, "strength_crit", "Felslag, poured from what was left after the fel fires. It bites."),
    "iron": (None, "tank", "Good, honest iron, made for standing in the line and staying there."),
    "bloodiron": (None, "strength", "Bloodiron. Orc smiths quench it in something they won't name."),
    "mithril": (None, "tank", "Mithril's light for its strength, so a defender can wear more of it."),
    "deepearth": (None, "hunter", "Deepearth scale, dark as a mine shaft and twice as tough."),
    "dark_iron": (None, "strength_hit", "Dark iron, forged hot and true. It doesn't miss what it's swung at."),
    "truesilver": (None, "crusader", "Truesilver, for a paladin who heals with one hand and hits with the other."),
    "thorium": (None, "tank", "Thorium plate. It's heavy, and nothing gets through it easily."),
    "ashen_steel": (None, "hunter_crit", "Ashen steel, grey and cold, and every link of it is sharp."),
    "arcanite": (None, "plate_healer", "Arcanite, the finest a smith can work. Healers who wear it rarely fall."),
    "elementium": (None, "strength_crit", "Elementium. It's the best metal there is, and it hits like it."),
}

SMITH_LINES = [
    (r"Chaplain|Shroudsteel|Arcane Plate|Tidesurge|Tideguard", None, "plate_healer",
     "Blessed plate, made for the one keeping everyone else alive."),
    (r"Crusader|Thunderfist|Fangplate|Silverfang|Duskplate|Earthshaker|Bronze Warhammer|Iron Warhammer|"
     r"Iron Halberd|Felhewn|Accursed|Runeplate", None, "crusader", "Crusader's work: plate for a fighter who also prays."),
    (r"Spellchain|Mystic|Runic|Bonegraft|Moonhowl|Naga Scale|Deepsea|Runescale|Putrid", None, "storm",
     "Mail with runes cut into the rings, for a shaman's spells."),
    (r"Warden|Plains Scale|Stonemace|Stonehoof|Stormblessed", None, "earthen",
     "Mail for a shaman who fights up close."),
    (r"Hunter's|Copper Scale|Saltcrusted|Carapace|Venomed|Thornscale|Serpentscale|Iron Scale|Blademark|"
     r"Demonshard|Troll-Wrought", None, "hunter", "Hunter's mail, light at the shoulder so the bow draws clean."),
    (r"Tower Shield|Plagued Iron|Rotboned", None, "tank", "Made for whoever stands at the front."),
]

# ---------------------------------------------------------------------------------------------
# ENGINEERING. Goggles for every role (each pair says what it's for and what it's made of), the
# hunter's guns, a few belts and gloves, and trinkets that DO things. Kyle, 10 Nov: "theyre NOT stat
# sticks. They do stuff." Every engineering trinket carries a proc (see ENGINEERING_PROCS), not
# just the ones over 50 that the rule requires: a gadget that does nothing isn't a gadget.
# ---------------------------------------------------------------------------------------------
ENGINEERING_METALS = {m: (None, "agility", "It's loud, it kicks, and it hits what it's pointed at.")
                      for m in ("copper", "bronze", "iron", "steel", "gold", "mithril", "voidglass",
                                "truesilver", "dark", "thorium", "arcanite", "elementium")}

ENGINEERING_LINES = [
    (r"Tinted Goggles", "cloth", "caster", "Tinted lenses, so a caster can look straight into a fireball."),
    (r"Magnifying Goggles", "cloth", "precise_caster", "Lenses ground fine enough to read a rune at forty paces."),
    (r"Prism Goggles", "cloth", "healer", "The prisms split the light, and somehow it's easier to see who's hurt."),
    (r"Embersight", "cloth", "fire", "Lenses of fired glass. Everything looks a little warmer through them."),
    (r"Tinker's Gloves", "cloth", "caster", "Fingerless, so a tinker can still feel the wires."),
    (r"Copper Eyeshields", "leather", "agility", "Copper shields over the eyes, for sparks and for sand."),
    (r"Smoked Lenses", "leather", "rogue_crit", "Smoked glass, so nobody sees where you're looking."),
    (r"Welder's|Seamfinder|Sparkproof", "plate", "strength", "Heavy, scorched, and made for someone who works close to the fire."),
    (r"Rangefinder|Voidsight", "mail", "hunter_precise", "A dial on the side clicks off the range to whatever you're aiming at."),
    (r"Field Goggles", "mail", "tide_healer", "A field engineer's goggles, with a lens that shows who's bleeding."),
    (r"Gilded Marksman's", "mail", "hunter", "Marksman's lenses with a little brass sight on the rim."),
    (r"Gyro-Visor", "mail", "hunter_crit", "A spinning gyroscope keeps the lens steady, however fast you move."),
    (r"Bandolier", "mail", "hunter", "Loops for every kind of charge, and a few spares besides."),
    (r"Shellguard", "mail", "tank", "Thorium plates over the knuckles, made for a mechsuit's hands."),
    (r"Siege Harness", "mail", "hunter_crit", "A harness built to carry a siege gun's kick. It carries a hunter's fine."),
    # GUNS IN THREE ROLES (Kyle, 15 Nov: "we need dps guns, tank guns, Healer guns"). The gun users
    # are hunters and the like (damage), Warrior Protection and Tinker Mechanics (tanks), and Tinker
    # Invention, the field engineer who loads medicine rounds (healer). Blunderbusses and the bombard
    # are short and heavy, for the front line; the scattergun and the repeaters spray healing.
    (r"Bronze Blunderbuss|Mithril Blunderbuss|Dark Iron Bombard", None, "tank",
     "Short, heavy and loud, for someone at the front who wants every eye on them."),
    (r"Ratchet Scattergun|Emberglass Repeater|Truesilver Repeater", None, "tide_healer",
     "Loaded with medicine rounds. Point it at a friend and pull the trigger."),
    (r"Voidglass Longrifle", None, "hunter_precise", "The voidglass scope sees a little further than it should."),
    (r"Arcanite Longrifle", None, "hunter_crit", "It's loud, it kicks, and it hits what it's pointed at."),
    # trinkets
    (r"Spark Coil", None, "agility", "A coil of copper wire that's always looking for something to touch."),
    (r"Pocket Orrery", None, "caster", "Tiny brass planets turn inside it, and they keep better time than the sky."),
    (r"Net-o-Matic", None, "strength", "Point it at whatever's hitting you. Most of the time it works."),
    (r"Resonance Housing", None, "caster", "It hums along with your spells, and sometimes it sings back."),
    (r"Mechanical Dragonling", None, "agility", "A clockwork whelp that sleeps in your pack until there's a fight."),
    (r"Tidewright's Astrolabe", None, "healer", "It points at whoever needs healing most. It's usually right."),
    (r"Gold Power Core", None, "tank", "A gold-wired core that flares when it's knocked."),
    (r"Targeting Scope", None, "hunter", "A voidglass scope. It finds the weak spot before you do."),
    (r"Arcanite Dragonling Core", None, "caster", "The heart of a clockwork dragon, still warm."),
]

#: The procs, by the trinket's name (a named variant, "Edwin's Pocket Orrery", shares its base's).
#: Sized off the trinkets that already exist (claude/trinkets_must_do_things.md): at 55, an 8% proc
#: with a 5-turn cooldown is +40 spell power for 3 turns, or a shield of 8% of your health, or 90
#: mana. Every one has an internal cooldown.
ENGINEERING_PROCS = [
    (r"Spark Coil", {"trigger": "on_weapon_swing", "chance": 12, "icd": 3, "damage_flat": 15, "school": "nature",
                     "describe": "Your attacks have a chance to zap the target for 15 nature damage."}),
    (r"Pocket Orrery", {"trigger": "on_damage_cast", "chance": 10, "icd": 4,
                        "grant_resource": {"resource": "mana", "amount": 30},
                        "describe": "Your damaging spells have a chance to restore 30 mana."}),
    (r"Net-o-Matic", {"trigger": "on_damage_taken", "chance": 8, "icd": 6,
                      "apply_effect": {"effect_id": "netomatic_net", "name": "Netted", "effect_type": "debuff",
                                       "duration": 1, "is_stun": True, "stat_mods": {}, "on_target": True},
                      "describe": "When you're struck, you have a chance to throw a net over the attacker, "
                                  "stopping it for a turn."}),
    (r"Resonance Housing", {"trigger": "on_damage_cast", "chance": 8, "icd": 5,
                            "apply_effect": {"effect_id": "resonance_hum", "name": "Resonance", "effect_type": "buff",
                                             "duration": 3, "stat_mods": {"spell_power": 15}, "on_target": False},
                            "describe": "Your damaging spells have a chance to grant 15 spell power for 3 turns."}),
    (r"Mechanical Dragonling", {"trigger": "on_weapon_swing", "chance": 10, "icd": 3, "damage_flat": 55, "school": "fire",
                                "describe": "Your attacks have a chance to wake your dragonling, which breathes "
                                            "fire on the target for 55."}),
    (r"Tidewright's Astrolabe", {"trigger": "on_heal_cast", "chance": 10, "icd": 4,
                                 "apply_effect": {"effect_id": "astrolabe_tide", "name": "Turning Tide",
                                                  "effect_type": "buff", "duration": 3,
                                                  "stat_mods": {"healing_power": 25}, "on_target": False},
                                 "describe": "Your healing spells have a chance to grant 25 healing power for 3 turns."}),
    (r"Gold Power Core", {"trigger": "on_damage_taken", "chance": 10, "icd": 5,
                          "apply_effect": {"effect_id": "power_core_flare", "name": "Core Flare", "effect_type": "buff",
                                           "duration": 3, "absorb_pct_max_health": 0.06, "stat_mods": {},
                                           "on_target": False},
                          "describe": "When you're struck, the core has a chance to flare into a shield that "
                                      "absorbs 6% of your health."}),
    (r"Targeting Scope", {"trigger": "on_crit", "chance": 15, "icd": 4,
                          "apply_effect": {"effect_id": "scope_lock", "name": "Target Locked", "effect_type": "buff",
                                           "duration": 3, "stat_mods": {"attack_power": 50}, "on_target": False},
                          "describe": "Your critical hits have a chance to grant 50 attack power for 3 turns."}),
    (r"Arcanite Dragonling Core", {"trigger": "on_damage_cast", "chance": 10, "icd": 4, "damage_flat": 160,
                                   "school": "fire",
                                   "describe": "Your damaging spells have a chance to wake the core, which scorches "
                                               "the target for 160 fire damage."}),
]


def proc_for(name):
    for pat, proc in ENGINEERING_PROCS + WOOD_PROCS:
        if re.search(pat, name):
            return json.loads(json.dumps(proc))
    return None


# ---------------------------------------------------------------------------------------------
# WOODWORKING. Staves, wands and off-hand tomes for casters and healers, bows and crossbows for
# hunters, spears, shields for shaman, and two trinkets that do things. Each wood is one school for
# its casting weapons (staff, wand, tome), and one hunter role for its bows and spears.
# ---------------------------------------------------------------------------------------------
WOODS = {
    "ashwood": (None, "starter_caster", "Ashwood, light and straight-grained. Every woodworker learns on it."),
    "ironbark": (None, "caster", "Ironbark's as hard as its name, and it holds a spell well."),
    "silverbark": (None, "arcane", "Silverbark gleams faintly, even in the dark."),
    "duskwood": (None, "shadow", "Duskwood is black to the heart, and it's always a little cold."),
    "goldenleaf": (None, "spirit_healer", "Goldenleaf wood, warm to the hand. Healers favour it."),
    "nightshade": (None, "nature", "Nightshade's poisonous to carve and lovely once it's done."),
    "sapglow": (None, "spirit_caster", "Sapglow still weeps a little light where it was cut."),
    "redbark": (None, "fire", "Redbark smoulders if you work it too fast."),
    "thornveil": (None, "healer", "Thornveil. The thorns come off, and the healing stays in."),
    "bloodroot": (None, "blood", "Bloodroot bleeds red sap, and it never quite dries."),
    "marshwillow": (None, "frost", "Marshwillow, soaked and supple, and as cold as the bog it grew in."),
    "bloodwood": (None, "death", "Bloodwood. Necromancers swear it remembers every death near its roots."),
    "felbark": (None, "fel", "Felbark, twisted by the fel and humming with it."),
    "moonpetal": (None, "high_healer", "Moonpetal wood, pale as moonlight and blessed by it."),
    "starleaf": (None, "arcane_crit", "Starleaf glitters like a clear night sky."),
    "stormoak": (None, "storm", "Stormoak grew where lightning struck, and it hasn't forgotten."),
    # woodworking expansion (15 Nov 2026): the four planks that fed nothing but sticks and fibre
    "emberwood": (None, "fire", "Emberwood's always warm, and it crackles when it casts."),
    "frostheart": (None, "frost", "Frostheart. The core of the trunk never thaws, even in a fire."),
    "ebonthorn": (None, "void", "Ebonthorn is black all the way through, and the thorns grow back."),
    "sunheart": (None, "holy", "Sunheart wood holds the light it grew in, and gives it back slowly."),
}

#: a wood's bows, crossbows and spears: precise woods for steady shots, crit woods for big ones
WOOD_RANGED = {"silverbark": "hunter_precise", "duskwood": "hunter_precise", "nightshade": "hunter_precise",
               "moonpetal": "hunter_precise", "redbark": "hunter_crit", "bloodroot": "hunter_crit",
               "bloodwood": "hunter_crit", "felbark": "hunter_crit", "starleaf": "hunter_crit",
               "stormoak": "hunter_crit", "emberwood": "hunter_crit", "frostheart": "hunter_precise",
               "ebonthorn": "hunter_crit", "sunheart": "hunter_precise"}
WOOD_SPEAR = {"hunter_precise": "assassin", "hunter_crit": "rogue_crit"}

#: Named lines, for a wood's casting weapons only: a bow called Venomthorn is still a bow.
WOOD_LINES = [
    # STAVES AREN'T ONLY FOR CASTERS (Kyle, 15 Nov 2026: "Beetle tanks and bear tanks (venomancer and
    # druids) can use staves....so agi staves and tank staves are real"). Prowler's and Stalker's staves
    # are a cat druid's or a hunter's (attack power and Agility); Barkguard staves are a bear druid's or a
    # Venomancer beetle's (Stamina, Agility and dodge). Both read agi_physical, as those tanks do.
    (r"Prowler's|Stalker's", None, "feral", "A fighting staff, weighted at both ends and wrapped for grip."),
    (r"Barkguard", None, "bear", "Bark-plated and heavy. It's made to take a blow as much as give one."),
    (r"Healer's|Scarlet|Blessed|Piety|Grove|Lifebark|Taurajo Spirit|Amberwood|Pilgrim's", None, "healer",
     "Carved for a healer, smooth where the hand rests."),
    (r"Hexwood|Bone-Tipped|Tiki|Shadowroot|Darkthorn", None, "hex", "Troll work, hung with little bone charms."),
    (r"Emberwood", None, "fire", "Emberwood's always warm, and it crackles when it casts."),
    (r"Frostpine|Naga Driftwood", None, "frost", "There's frost in the grain that never melts."),
    (r"Serpentwood|Venomwood|Brood-Stung|Bramblewood", None, "nature", "Green wood, still alive in places."),
    (r"Shadow-Burned|Shadow-Etched|Undercity Cursed|Demon-Touched|Plague-Bleached", None, "shadow",
     "Burned dark, and the dark stayed in."),
    (r"Felwood Staff", None, "fel", "Cut in Felwood, and it glows green at the knots."),
    (r"Stormcaller's", None, "storm", "It hums before a storm."),
    (r"Amber-Etched|Mystic Oak", None, "arcane", "Runes etched in amber run down its length."),
    (r"Warden's|Oakheart Staff|Crusader's", None, "crusader", "Heavy enough to fight with, and blessed besides."),
]

WOOD_TRINKET_LINES = [
    (r"Hawk Fetish", None, "agility", "A hawk carved from one piece of wood, feathers and all."),
    (r"Barkguard Ward", None, "bear", "A disc of layered bark. Hit it hard and it hardens."),
    (r"Moonpetal Blossom", None, "high_healer", "A moonpetal flower carved in wood so thin the light shows through."),
    (r"Emberwood Brand", None, "fire", "A branding iron of emberwood. It never quite cools."),
    (r"Stormoak Heart", None, "storm", "The heart of a lightning-struck oak, still charged."),
    (r"Carved Oakheart Charm", None, "caster", "An oak heart, carved small. It's lucky, or it's angry."),
    (r"Heartwood Idol", None, "healer", "A druid's idol, cut from the heart of a very old tree."),
]
WOOD_HEAD_LINES = [
    (r"Driftwood Mask", "leather", "feral", "Driftwood, carved into a beast's face."),
    (r"Ironbark Helm", "mail", "earthen", "Ironbark plates laced over a leather cap."),
    (r"Bramblewood Crown", "leather", "wildheart", "A crown of living bramble. It still flowers in spring."),
    (r"Bloodroot Mask", "leather", "feral", "A snarling mask of bloodroot. The sap stains the wearer's face."),
    (r"Felbark Helm", "mail", "earthen", "Felbark plates over a mail coif. The green glow is the wood, not you."),
    (r"Starleaf Crown", "leather", "wildheart", "A circlet of starleaf twigs, and it glitters at night."),
]

#: RELICS (totems, idols, librams: the ranged slot of a shaman, druid or paladin). The name says the
#: role, the way a WoW relic's did. First match wins, so "Moonpetal Grove Idol" is a healer's.
WOOD_RELIC_LINES = [
    (r"Barkguard", "bear", "Carved for a bear's hide. It gets heavier the harder you're hit."),
    (r"Claw", "feral", "A clawed paw, carved in the round and worn smooth by a druid's grip."),
    (r"Grove", "healer", "A seedling carved in the grove's own wood. It still smells of rain."),
    (r"Mercy", "plate_healer", "Psalms of mercy, bound between boards of good wood."),
    (r"Tide", "tide_healer", "Carved with the tide's runes. Hold it to your ear and it sounds like the sea."),
    (r"Zeal", "crusader", "Battle-prayers, bound in wood and banded for a soldier's belt."),
    (r"Bulwark", "tank", "Oaths of the shield wall, bound in boards thick enough to stop a blade."),
    (r"Earthshaker", "earthen", "A squat totem, heavy as a stone. It thrums when you strike."),
    (r"Storm", "storm", "The wood's split along a lightning scar, and the scar still crackles."),
    (r"Moon Idol", "nature", "A crescent moon cut into pale wood. It brightens at night."),
]
RELICS = {"totem", "idol", "libram"}

WOOD_PROCS = [
    # woodworking expansion (15 Nov 2026), sized off ENGINEERING_PROCS at the trinket's level
    (r"Hawk Fetish", {"trigger": "on_crit", "chance": 15, "icd": 4,
                      "apply_effect": {"effect_id": "hawk_fetish_eye", "name": "Hawk's Eye", "effect_type": "buff",
                                       "duration": 3, "stat_mods": {"attack_power": 35}, "on_target": False},
                      "describe": "Your critical hits have a chance to grant 35 attack power for 3 turns."}),
    (r"Barkguard Ward", {"trigger": "on_damage_taken", "chance": 10, "icd": 5,
                         "apply_effect": {"effect_id": "barkguard_ward", "name": "Barkguard", "effect_type": "buff",
                                          "duration": 3, "absorb_pct_max_health": 0.05, "stat_mods": {},
                                          "on_target": False},
                         "describe": "When you're struck, you have a chance to harden into bark that absorbs "
                                     "5% of your health."}),
    (r"Moonpetal Blossom", {"trigger": "on_heal_cast", "chance": 10, "icd": 4,
                            "grant_resource": {"resource": "mana", "amount": 70},
                            "describe": "Your healing spells have a chance to restore 70 mana."}),
    (r"Emberwood Brand", {"trigger": "on_damage_cast", "chance": 10, "icd": 4, "damage_flat": 110, "school": "fire",
                          "describe": "Your damaging spells have a chance to brand the target for 110 fire damage."}),
    (r"Stormoak Heart", {"trigger": "on_damage_cast", "chance": 8, "icd": 5,
                         "apply_effect": {"effect_id": "stormoak_heart", "name": "Gathering Storm",
                                          "effect_type": "buff", "duration": 3,
                                          "stat_mods": {"spell_power": 45}, "on_target": False},
                         "describe": "Your damaging spells have a chance to grant 45 spell power for 3 turns."}),
    (r"Carved Oakheart Charm", {"trigger": "on_damage_cast", "chance": 10, "icd": 4, "damage_flat": 30,
                                "school": "nature", "describe": "Your damaging spells have a chance to lash "
                                                                "the target with thorns for 30 nature damage."}),
    (r"Heartwood Idol", {"trigger": "on_heal_cast", "chance": 10, "icd": 4,
                         "apply_effect": {"effect_id": "heartwood_bloom", "name": "Heartwood Bloom",
                                          "effect_type": "buff", "duration": 3,
                                          "stat_mods": {"healing_power": 20}, "on_target": False},
                         "describe": "Your healing spells have a chance to grant 20 healing power for 3 turns."}),
]

CASTING_WEAPONS = {"staff", "wand", "tome", "orb", "idol", "totem", "libram"}


def wood_identity(recipe, base_ident):
    """A wood's identity for this piece: casting weapons take the wood's school (or a named line's),
    bows and crossbows its hunter role, spears the matching melee role, shields a shaman's."""
    out = recipe["output"]
    wt = out.get("weapon_type")
    tier = out.get("material_tier")
    name = recipe["name"]
    if out["slot"] in ("trinket", "trinket1", "trinket2"):
        return next(((a, i, f) for p, a, i, f in WOOD_TRINKET_LINES if re.search(p, name)), (None, "caster", None))
    if out["kind"] == "armor":
        return next(((a, i, f) for p, a, i, f in WOOD_HEAD_LINES if re.search(p, name)), (None, "feral", None))
    if wt in ("bow", "crossbow"):
        return None, WOOD_RANGED.get(tier, "hunter"), "Strung tight and true. It won't miss for want of a good bow."
    if wt in RELICS:
        return next(((None, i, f) for p, i, f in WOOD_RELIC_LINES if re.search(p, name)),
                    (None, {"totem": "storm", "idol": "nature", "libram": "crusader"}[wt], None))
    if wt == "polearm":
        if re.search(r"Warpike", name):
            return None, "strength", "A long, heavy war-pike. Wood this good doesn't snap on armour."
        if re.search(r"Warden's", name):
            return None, "crusader", "Heavy enough to fight with, and blessed besides."
        if re.search(r"Razortusk", name):
            return None, "strength", "Tusks bound to a heavy haft. It's made for swinging."
        return None, WOOD_SPEAR.get(WOOD_RANGED.get(tier), "agility"), "A long haft of good wood and a sharp point."
    if wt == "shield":
        if re.search(r"Thunder|Storm", name):
            return None, "storm", "A wooden shield with a copper boss. Lightning likes it."
        return None, "tide_healer", "A wooden shield, carved with tide runes for a shaman's arm."
    for pat, arm, ident, flav in WOOD_LINES:
        if re.search(pat, name):
            return arm, ident, flav
    return None, base_ident, None


#: Jewellery: the setting decides the role, the stone and its tier decide the rest. Signets are
#: strength, pendants a tank's, bands agility, chokers and loops a caster's, lockets and circles a healer's.
JEWEL_METALS = {m: (None, None, None) for m in ("copper", "silver", "gold", "mithril", "truesilver", "thorium")}
JEWEL_SETTINGS = [
    (r"Signet", "strength", "A heavy signet. It leaves a mark when it hits."),
    (r"Pendant", "tank", "A solid pendant on a short chain, made to sit under armour."),
    (r"Band", "agility", "A thin band that never catches on a grip."),
    (r"Choker", "caster", "The stone sits at the throat, close to where the words come from."),
    (r"Loop", "precise_caster", "A plain loop of metal and one clean stone."),
    (r"Locket|Circle", "healer", "Cool to the touch, and it settles a healer's hands."),
]


def jewel_identity(recipe):
    for pat, ident, flav in JEWEL_SETTINGS:
        if re.search(pat, recipe["name"]):
            if ident == "agility" and recipe["output"]["item_level"] >= 50:
                ident = "rogue_crit"
            return None, ident, flav
    return None, None, None


TWO_HANDED = {"sword_2h", "axe_2h", "mace_2h", "polearm", "staff"}
CASTING = {"tide_healer", "plate_healer", "storm", "healer", "mail_caster"}


#: A mail piece from a plate metal takes the mail role nearest its metal's: hunters and shaman don't tank.
MAIL_FALLBACK = {"tank": "earthen", "strength": "earthen", "strength_crit": "earthen",
                 "strength_hit": "earthen", "crusader": "earthen", "plate_healer": "tide_healer",
                 "melee_starter": "melee_starter"}


def weapon_identity(weapon_type, ident):
    """A weapon follows its metal, with two exceptions. A shield from a fighting metal is a tank's
    shield (Stamina and block), and a two-hander from a tank metal hits like a strength weapon: no
    one tanks with a greataxe."""
    if weapon_type == "shield" and ident not in CASTING:
        return "shield_tank"
    # ...except a staff: a bear druid or a Venomancer beetle really does tank with one (Kyle, 15 Nov 2026)
    if weapon_type == "staff" and ident == "bear":
        return ident
    if weapon_type in TWO_HANDED and ident in ("tank", "shield_tank", "bear"):
        return "strength"
    return ident


#: Two recipes each, with different items (the older run sat above its skill). The older one takes
#: a new name; the 300 pass keeps the plain one.
RENAMES = {
    "lw_emberscale_helm": "Emberscale Coif",
    "lw_bloodtanned_vest": "Bloodtanned Jerkin",
    "lw_bloodtanned_helm": "Bloodtanned Mask",
    "ww_duskwood_bow": "Duskwood Recurve",
}

TRADES = {
    "tailoring": {"materials": TAILORING_CLOTH, "lines": TAILORING_LINES, "family_rule": True},
    "blacksmithing": {"materials": SMITH_METALS, "lines": SMITH_LINES, "curve": True},
    "engineering": {"materials": ENGINEERING_METALS, "lines": ENGINEERING_LINES, "curve": True},
    "woodworking": {"materials": WOODS, "lines": [], "curve": True, "resolver": "wood"},
    "jewelcrafting": {"materials": JEWEL_METALS, "lines": [], "resolver": "jewel"},
    "leatherworking": {"materials": LEATHER_HIDES, "lines": LEATHER_LINES, "armour_words": True,
                       "curve": True,
                       "named_materials": ("cragscale", "stormscale", "stonebound", "dredged", "fiendish",
                                           "hydra", "pristine", "savage", "frostscale", "emberscale",
                                           "mossback", "netherdrake", "duskfang", "bloodtanned", "rugged")},
}


def armour_from_name(name):
    """'leather' or 'mail' when the name says so, else None. Leather is checked first, so a
    "Deepscale Leather Vest" is leather."""
    if re.search(r"\bLeather\b", name):
        return "leather"
    if re.search(r"Mail|scale\b|Scale\b|Scaled|Coif", name):
        return "mail"
    return None


def curve_level(recipe):
    """The item level a recipe's skill earns: skill / 5 + 1, and 2 more for a named variant
    ("Grisle's Wool Belt"). Tailoring already sits on it; a run of leatherworking sat 6 to 9 above."""
    lvl = recipe.get("skill_required", 0) // 5 + 1
    return lvl + 2 if "'s " in recipe["name"] else lvl


# ---------------------------------------------------------------------------------------------
# the engine
# ---------------------------------------------------------------------------------------------
_GEN = LootGenerator()
COST = _GEN.stat_budget_costs


def identity_for(trade, recipe):
    """(armour or None, identity, flavour) for one recipe. A named line wins over its material (in
    tailoring, only when it names a different school)."""
    t = TRADES[trade]
    tier = recipe["output"].get("material_tier")
    # a piece named after another material is that material's piece ("Cragscale Bracers" made from
    # thick leather is still Cragscale)
    for other in t.get("named_materials", ()):
        if other != tier and other.replace("_", " ").title() in recipe["name"].title():
            tier = other
            break
    base = t["materials"].get(tier)
    for pat, arm, ident, flav in t["lines"]:
        if re.search(pat, recipe["name"]):
            if not t.get("family_rule") or base is None or family(ident) != family(base[1]):
                return arm, ident, flav
            break
    if base is not None:
        return base
    return None, None, None


def budget(out):
    """The generator's stat budget for this recipe's slot, level and rarity, plus the 15% bonus a
    rolled green or better gets on top (LootGenerator._roll_stats' bonus rolls), so an authored piece
    isn't weaker than a random one of the same level."""
    rar = _GEN.rarity_tiers[out["rarity"]]
    if out["kind"] == "weapon":
        wd = _GEN.weapon_types["weapon_types"][out["weapon_type"]]
        tier = "weapon_two_hand" if wd["hand"] == "two_hand" else "weapon_medium"
        b = out["item_level"] * _GEN.STAT_BUDGET_BASE_MULT * rar["stat_budget_multiplier"] \
            * _GEN.slots["weight_tiers"][tier] * wd["budget_multiplier"]
    else:
        tier = _GEN.slots["slots"][out["slot"]]["weight_tier"]
        b = out["item_level"] * _GEN.STAT_BUDGET_BASE_MULT * rar["stat_budget_multiplier"] \
            * _GEN.slots["weight_tiers"][tier]
    return b * (1.15 if rar.get("bonus_stat_rolls") else 1.0)


#: A power stat (spell power, a school's power, healing, attack power) is only on an item once it's
#: worth having. Under this it's dropped and its share goes to the item's other stats.
POWER = CASTER - {"crit_chance_spell", "spell_penetration", "mp5"} | {"attack_power"}
POWER_FLOOR = 3
#: the item level power starts to appear on gear
POWER_FROM = 12


def floor_for(stat, item_level):
    """The smallest a stat may be (Kyle: "Biggest thing is dribble on stats"). Ratings are whole
    percents, so 1 is a real stat; a +1 or +2 primary on a level 30 robe isn't."""
    if stat in POWER:
        # A low green is Agility and Stamina, or Intellect and Spirit, the way WoW's are. Power is
        # cheap (2 AP a point), so at a low budget it would swallow the whole item: "+6 AP" gloves.
        return POWER_FLOOR if item_level >= POWER_FROM else 10 ** 6
    if stat in PRIMARY:
        return 2 if item_level < 20 else 3
    # a rating is RATING_PER_PCT points to the percent since 15 Nov (entities/power_scale.py), so a
    # rating under half a percent is the leftover Kyle calls dribble
    return RATING_FLOOR


RATINGS = {"hit_rating", "spell_hit_rating", "crit_chance_spell", "crit_chance_physical", "haste", "spell_penetration",
           "dodge_rating", "parry_rating", "block_rating", "defense_rating", "armor_penetration_pct"}
#: the smallest rating on an item: half a percent
RATING_FLOOR = 5
#: (UNUSED since ratings, 15 Nov.) The most of an item's budget a 2% rating may take. Ratings are dear in this game (2% crit is 20
#: points, more than a level 60 pair of bracers is worth), so like WoW's Bloodvine set the rating is on
#: the pieces big enough to carry it and the small pieces are all power.
RATING_SHARE_MAX = 0.4


def split(weights, total, item_level):
    """Whole-number stats from a budget. A rating is 2% or it isn't there (see RATING_SHARE_MAX). Any
    other stat under its floor is dropped, and what it was worth goes, with whatever rounding took
    off, to the strongest stat that's left."""
    # Ratings are ordinary stats since 15 Nov: 10 points to the percent and priced to match, so they
    # split the budget like anything else and climb with item level (a gem or a robe at 30 has a
    # little crit, at 60 a lot more), with the floor above keeping off the dribble.
    weights = dict(weights)
    keep = {}
    order = sorted(weights, key=weights.get, reverse=True)
    loss = 0.0
    for stat in order:
        cost = COST.get(stat, 1.0)
        raw = total * weights[stat] / cost
        v = whole(raw)
        # RATINGS FROM THE EARLY LEVELS (Kyle, 15 Nov 2026: "slap in some ratings for easier transition from 1 to
        # max level so not every rating is just dropped post 50"). A rating that comes out at 60% of its floor or
        # more is rounded UP to the floor (5, half a percent) and the lead stat pays the difference, so a level
        # 15-25 piece of a rating collection carries its rating instead of losing it to the floor.
        if stat in RATINGS and item_level >= 10 and v < RATING_FLOOR and raw >= RATING_FLOOR * 0.6:
            loss += (raw - RATING_FLOOR) * cost          # negative: the lead stat gives it up
            keep[stat] = RATING_FLOOR
            continue
        if v < floor_for(stat, item_level):
            loss += raw * cost
            continue
        loss += (raw - v) * cost
        keep[stat] = v
    main = next((st for st in order if st in keep), None)
    if main is None:
        # nothing reached its floor (a level 2 item): it's all one primary
        main = next((st for st in order if st in PRIMARY), order[0])
        keep[main] = max(1, whole(total / COST.get(main, 1.0)))
    elif loss >= 0.5 or loss <= -0.5:
        keep[main] = max(1, keep[main] + whole(loss / COST.get(main, 1.0)))
    prim = {st: v for st, v in keep.items() if st in PRIMARY}
    sec = {st: v for st, v in keep.items() if st not in PRIMARY}
    return prim, sec


def reference(rid, out):
    """The generator's own armour, damage, speed, block and price for this piece, seeded on the recipe
    so it never changes. Its rolled stats are thrown away."""
    state = random.getstate()
    random.seed(zlib.crc32(rid.encode("utf-8")))
    jewelcrafting._SUPPRESSED[0] += 1
    try:
        if out["kind"] == "weapon":
            return _GEN.generate_weapon(out["slot"], out["weapon_type"], out["stat_template"],
                                        out["item_level"], out["rarity"])
        return _GEN.generate_armor_piece(out["slot"], out["armor_type"], out["stat_template"],
                                         out["item_level"], out["rarity"])
    finally:
        jewelcrafting._SUPPRESSED[0] -= 1
        random.setstate(state)


def epic_icon_id(name):
    """Where a crafted epic's own art goes: assets/icons/gear/gear_epic_crafted_<name>.png."""
    return "gear_epic_crafted_" + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


#: Kyle, 15 Nov: "You can shift some icons to use for crafting. Blues I don't much care about. For epics
#: we will use proper art." Greens and blues borrow pack icons matched to their collection's colour
#: (tools/crafted_icon_palette.py); an epic uses its own art once it's in, else the epic pool's stand-in.
PICKER = None


def icon_for(name, slot, armor_type, weapon_type, rarity):
    from entities.boss_loot import resolve_icon
    if rarity in ("epic", "legendary"):
        return resolve_icon(slot=slot, armor_type=armor_type, weapon_type=weapon_type, rarity=rarity,
                            seed=f"fixedboss:{name}", explicit=epic_icon_id(name))
    got = PICKER.pick(name, slot, armor_type, weapon_type) if PICKER else None
    return got or resolve_icon(slot=slot, armor_type=armor_type, weapon_type=weapon_type, rarity=rarity,
                               seed=f"fixedboss:{name}", explicit=None)


#: A FIGHTER'S STAFF IS A TWO-HANDED WEAPON. A staff's damage tier is "staff" (0.55, a caster's stick)
#: and its stat budget 1.8 to make up for it (data/items/weapon_types.json). For a bear druid, a Venomancer
#: beetle, a cat or a ret paladin that's a trap: they swing it, so it gave up most of a two-hander's damage
#: for stats they'd have had anyway. These identities' staves are built as two-handers - a two-hander's
#: damage, speed and budget - and stay staves (Kyle, 15 Nov 2026: "agi staves and tank staves are real").
FIGHTING_STAFF = {"feral", "bear", "crusader", "strength", "agility"}


def as_built(out, ident):
    """The recipe's output as the generator should price it: a fighter's staff priced as a two-hander."""
    if out.get("weapon_type") == "staff" and ident in FIGHTING_STAFF:
        return {**out, "weapon_type": "mace_2h", "stat_template": IDENTITIES[ident][1]}
    return out


def author(rid, recipe, ident, flavour):
    out = recipe["output"]
    weights, template = IDENTITIES[ident]
    built = as_built(out, ident)
    prim, sec = split(weights, budget(built), out["item_level"])
    ref = reference(rid, built)
    # NO STRAY ARMOUR. The reference item's random rolls can include "+armor", which Item folds into its
    # armour value: a wand with 138 armour, a caster's trinket with 185. That's a drip stat (Kyle, 15 Nov 2026:
    # "The crafted items need to be logical and not full of drip stats"), so only armour, shields and the
    # slots that are armour keep it.
    keeps_armour = out["kind"] == "armor" and out["slot"] not in ("trinket", "trinket1", "trinket2", "ring",
                                                                  "ring1", "ring2", "neck") \
        or ref.weapon_type == "shield"
    item = {
        "name": recipe["name"], "slot": out["slot"], "item_level": out["item_level"],
        "rarity": out["rarity"], "armor_type": ref.armor_type, "weapon_type": out.get("weapon_type") or ref.weapon_type,
        "stat_template": template, "primary_stats": prim, "secondary_stats": sec,
        "armor_value": ref.armor_value if keeps_armour else 0,
        # a reputation epic is ilvl 73 worn at 60 (Kyle, 15 Nov 2026), so its output can pin the level
        "required_level": out.get("required_level") or ref.required_level,
        "sell_price": ref.sell_price, "flavor_text": flavour, "identity": ident,
    }
    # ONE ICON PER CRAFT (Kyle, 15 Nov: "Ensure crafting makes ONE icon per craft. Not random"). The
    # icon is chosen once, here, seeded on the item's name exactly as boss_loot._item_from_def would,
    # and written into the recipe, so it can't drift if the icon picker ever changes.
    item["icon_id"] = icon_for(recipe["name"], out["slot"], ref.armor_type, ref.weapon_type, out["rarity"])
    proc = proc_for(recipe["name"]) if out["slot"] in ("trinket", "trinket1", "trinket2") else None
    if not flavour:
        flavour = ""
    if proc:
        item["proc"] = proc
    if out["kind"] == "weapon":
        item.update(weapon_damage_min=ref.weapon_damage_min, weapon_damage_max=ref.weapon_damage_max,
                    attack_speed=ref.attack_speed, block_value=ref.block_value)
    return item


#: From this item level, a cloth piece has to lead with its power (Kyle: "high end clothes should have
#: sp or healing power primary").
POWER_LEADS_FROM = 25


def audit_item(trade, rid, item):
    bad = []
    armour = item.get("armor_type")
    # a cloak is cloth for everyone (slots.json), so a rogue's cloak carries a rogue's stats
    allowed = None if item["slot"] == "back" else ALLOWED.get(armour)
    stats = {**item["primary_stats"], **item["secondary_stats"]}
    tag = f"{rid} ({item['name']})"
    if allowed is not None:
        for st in stats:
            if st not in allowed:
                bad.append(f"{tag}: {st} on {armour}")
    if item["item_level"] >= 10:
        for st, v in stats.items():
            if v < floor_for(st, item["item_level"]):
                bad.append(f"{tag}: +{v} {st} is a dribble")
    if not stats:
        bad.append(f"{tag}: no stats")
    if item["slot"] in ("trinket", "trinket1", "trinket2") and trade in ("engineering", "woodworking") \
            and not item.get("proc"):
        bad.append(f"{tag}: an engineering trinket that does nothing")
    weights = IDENTITIES[item["identity"]][0]
    if item["item_level"] >= POWER_LEADS_FROM:
        wanted = [st for st in weights if st in POWER]
        if wanted:
            # Kyle: high-end cloth leads with spell power or healing, and physical gear with AP
            powers = {st: v for st, v in stats.items() if st in POWER}
            if not powers:
                bad.append(f"{tag}: high-end gear with none of its power ({wanted[0]})")
            elif max(powers.values()) < max(stats.values()):
                bad.append(f"{tag}: its power isn't its biggest stat {stats}")
    return bad


def run(write):
    docs, bad, report = {}, [], collections.defaultdict(collections.Counter)
    global PICKER
    from crafted_icon_palette import Picker
    PICKER = Picker()
    for trade in TRADES:
        path = FILES[trade]
        if path not in docs:
            docs[path] = json.loads(path.read_text(encoding="utf-8"))
        d = docs[path]
        recipes = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
        for rid, r in recipes.items():
            out = r.get("output") or {}
            if out.get("kind") not in ("armor", "weapon"):
                continue
            t = TRADES[trade]
            if rid in RENAMES:
                r["name"] = RENAMES[rid]
            # slots that don't exist: a staff or spear in "two_hand" goes in the main hand, and a wand
            # is a ranged weapon wherever it was written (the 300 pass wrote both wrong)
            if out.get("slot") == "two_hand":
                out["slot"] = "main_hand"
            if out.get("weapon_type") == "wand":
                out["slot"] = "ranged"
            arm, ident, flav = identity_for(trade, r)
            # A REPUTATION RECIPE SAYS WHAT IT IS (tools/build_faction_rewards.py): its output names its
            # identity, armour and flavour outright, because its name is the faction's, not a material's.
            pinned = out.get("identity")
            if pinned:
                arm, ident, flav = out.get("armor_type"), pinned, out.get("flavor")
            elif t.get("resolver") == "wood":
                base = WOODS.get(out.get("material_tier"), (None, "caster", None))
                arm2, ident, flav2 = wood_identity(r, base[1])
                arm, flav = arm2 or arm, flav2 or base[2]
            elif t.get("resolver") == "jewel":
                arm, ident, flav = jewel_identity(r)
            if t.get("armour_words") and out["kind"] == "armor" and not pinned:
                arm = armour_from_name(r["name"]) or arm
            if arm and out["kind"] == "armor" and _GEN.slots["slots"][out["slot"]]["armor_slot"]:
                out["armor_type"] = arm
            if t.get("curve") and not out.get("fixed_item_level") and abs(out["item_level"] - curve_level(r)) > 3:
                out["item_level"] = curve_level(r)
            if ident is not None and out["kind"] == "weapon":
                ident = weapon_identity(out["weapon_type"], ident)
            if ident is not None and out["kind"] == "armor" and out.get("armor_type") == "mail" and trade == "blacksmithing":
                ident = MAIL_FALLBACK.get(ident, ident)
            if ident is None:
                bad.append(f"{trade} {rid} ({r['name']}): no identity for material {out.get('material_tier')}")
                continue
            item = author(rid, r, ident, flav)
            bad += audit_item(trade, rid, item)
            out["item"] = item
            report[trade][ident] += 1
    for trade, c in report.items():
        print(f"{trade}: {sum(c.values())} pieces authored; identities {dict(c.most_common())}")
    if bad:
        print(f"\nFAILED ({len(bad)}):")
        for b in bad[:80]:
            print("  -", b)
        return 1
    if write:
        for path, d in docs.items():
            path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print("written")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    sys.exit(run(not ap.parse_args().check))
