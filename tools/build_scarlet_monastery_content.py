#!/usr/bin/env python3
"""The Scarlet Monastery's creatures, fighting kits, encounter tables, zone levels and boss loot. Idempotent.

    PYTHONPATH=. python3 tools/build_scarlet_monastery_content.py

The maps are tools/handbuilt_scarlet_monastery.py (its docstring has the layout and what each boss asks of a party).
Kyle, 16 Nov 2026: "So can you also make SM with the 4 different dungeons? The layout etc." His levels (Plan A):
Graveyard 28-32, Library 32-36, Armory 35-39, Cathedral 38-42.

THE NUMBERS are read off the game's own 28-44 dungeons (medians of every kit in the band, 16 Nov 2026), so these sit
with Plague Depths, Grom's Rest, Razorfen Kraul and Stromgarde rather than above them:
    boss basic   B(L) = 10 * L - 40        medians: 272 at 30, 324 at 36, 373 at 42
    trash basic  T(L) =  4 * L - 10        medians: 100 at 30, 139 at 36, 162 at 42
    boss health  2.3 optional, 2.5 required, 2.8 the last boss of a wing; the Cathedral's pair 2.4 and 2.3

FIVE ENCOUNTERS A WING (Kyle, 16 Nov 2026: "Lets aim for about 4-6 bosses per dungeon... this will help with the weird
ass 2 bosses per wing that classic suffers from", and "We can also take some creative liberties with bosses").
Classic's own where it has them (Ironspine is the Graveyard's third rare), new ones where it doesn't.
These are plain dungeon bosses (world/difficulty.py "boss", 3x and 3x), like every other boss in the band.

THE LAST FIGHT IN THE CATHEDRAL IS TWO AT ONCE, the shape of the Royal Hive's and the galleon's: Mograine is folded
into Whitemane's spawn (zone.boss_pack), they share one hoard of nine, and three drop (entities/boss_loot.py).
He holds the front and gets back up once; she mends herself and burns whoever is hitting him.

LOOT. Three items per boss, item level = the boss's level + 3, stats from the real formulas
(tools/build_durotar_content.make), and anything outside the item curve's band is put on it
(entities/item_budget.fit_to_curve). Every trinket does something. No flavour text: these are rares.
The named epics on the four last bosses are in tools/epic_table.py.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools import handbuilt_scarlet_monastery as SM  # noqa: E402

LOOT = ROOT / "data/loot/scarlet_monastery_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
REGION = "Eastern Tirisfal"
ZONE_LEVELS = {SM.GROUNDS: [28, 42], SM.GRAVEYARD: [28, 32], SM.LIBRARY: [32, 36], SM.ARMORY: [35, 39],
               SM.CATHEDRAL: [38, 42]}


def B(level):
    return 10 * level - 40


def T(level):
    return 4 * level - 10


# ============================================================================================== the roster
#: name -> (template, lo, hi, boss multiplier or None, sprite, wing)
G, L, A, C = SM.GRAVEYARD, SM.LIBRARY, SM.ARMORY, SM.CATHEDRAL
ROSTER = {
    # ---- the Graveyard
    "Scarlet Torturer":          ("humanoid_warrior", 28, 31, None, "executioner_hooded", G),
    "Scarlet Scryer":            ("humanoid_caster",  28, 31, None, "scarlet_priest", G),
    "Haunting Phantasm":         ("undead_caster",    29, 31, None, "spectre_1", G),
    "Anguished Dead":            ("undead_basic",     29, 31, None, "zombie_2", G),
    "Unfettered Spirit":         ("undead_caster",    30, 31, None, "spectre_2", G),
    "Interrogator Maelis":       ("humanoid_warrior", 30, 30, 2.5, "priest_hooded", G),
    "Ironspine":                 ("undead_warrior",   31, 31, 2.3, "skeleton_warrior_2", G),
    "Azshir the Sleepless":      ("undead_caster",    31, 31, 2.5, "wraith_pale", G),
    "The Fallen Champion":       ("undead_warrior",   31, 31, 2.3, "revenant_1", G),
    "Bloodmage Thalnos":         ("undead_caster",    32, 32, 2.8, "necromancer", G),
    # ---- the Library
    "Scarlet Adept":             ("humanoid_caster",  32, 35, None, "scarlet_priest", L),
    "Scarlet Gallant":           ("humanoid_warrior", 32, 35, None, "scarlet_crusader", L),
    "Scarlet Beastmaster":       ("humanoid_ranged",  33, 35, None, "houndmaster", L),
    "Scarlet Tracking Hound":    ("beast_fast",       33, 35, None, "worg_6", L),
    # the monks keep the Library's halls and the Cathedral's nave both
    "Scarlet Monk":              ("humanoid_rogue",   33, 40, None, "scarlet_crusader", (L, C)),
    "Inquisitor Vellan Rook":    ("humanoid_caster",  33, 33, 2.5, "scarlet_priest", L),
    "Houndmaster Loksey":        ("humanoid_ranged",  34, 34, 2.5, "houndmaster", L),
    "Archivist Dana Mercer":     ("humanoid_caster",  35, 35, 2.3, "scarlet_priest", L),
    "Curator Halbrecht":         ("humanoid_caster",  35, 35, 2.5, "cult_overseer", L),
    "Arcanist Doan":             ("humanoid_caster",  36, 36, 2.8, "archmage_robed", L),
    # ---- the Armory
    "Scarlet Trainee":           ("humanoid_warrior", 35, 36, None, "human_militia", A),
    "Scarlet Soldier":           ("humanoid_warrior", 35, 37, None, "scarlet_crusader", A),
    "Scarlet Myrmidon":          ("humanoid_warrior", 36, 38, None, "noble_armoured", A),
    "Scarlet Defender":          ("humanoid_warrior", 36, 38, None, "warden_armoured", A),
    "Scarlet Evoker":            ("humanoid_caster",  36, 38, None, "archmage_robed", A),
    "Sergeant Major Cole Brennan": ("humanoid_warrior", 36, 36, 2.5, "scarlet_crusader", A),
    "Quartermaster Bram Ellison": ("humanoid_warrior", 37, 37, 2.5, "warden_armoured", A),
    "Smithmaster Corra Bellweather": ("humanoid_warrior", 37, 37, 2.3, "human_militia", A),
    "Master-at-Arms Dorran Pike": ("humanoid_warrior", 38, 38, 2.5, "noble_armoured", A),
    "Herod":                     ("humanoid_warrior", 39, 39, 2.8, "champion_plate", A),
    # ---- the Cathedral
    "Scarlet Centurion":         ("humanoid_warrior", 38, 40, None, "noble_armoured", C),
    "Scarlet Sorcerer":          ("humanoid_caster",  38, 41, None, "archmage_robed", C),
    "Scarlet Champion":          ("humanoid_warrior", 38, 41, None, "champion_plate", C),
    "Scarlet Wizard":            ("humanoid_caster",  38, 41, None, "archmage_robed", C),
    "Scarlet Abbot":             ("humanoid_caster",  39, 41, None, "scarlet_priest", C),
    "Brother Garrick Thorne":    ("humanoid_caster",  39, 39, 2.5, "hunter_ranger", C),
    "Captain Elric Stane":       ("humanoid_warrior", 40, 40, 2.5, "warden_armoured", C),
    "High Inquisitor Aldric": ("undead_warrior",   40, 40, 2.3, "revenant_2", C),
    "Brother Corwin Ashe":       ("humanoid_caster",  41, 41, 2.5, "scarlet_priest", C),
    "High Inquisitor Whitemane": ("humanoid_caster",  42, 42, 2.4, "bloodelf_magister", C),
    "Scarlet Commander Mograine": ("humanoid_warrior", 42, 42, 2.3, "scarlet_crusader", C),
}
BOSSES = {n for n, r in ROSTER.items() if r[3]}
#: the wing's last boss, and the 2-for-1
FINALS = {G: "Bloodmage Thalnos", L: "Arcanist Doan", A: "Herod", C: "High Inquisitor Whitemane"}
PACK_MEMBER = {"Scarlet Commander Mograine": "High Inquisitor Whitemane"}
#: the Scarlets in here pay the Order of the Pale Flame (tools/build_plaguelands_factions.py); the dead don't
SCARLETS = sorted(n for n, r in ROSTER.items() if not r[3] and r[0].startswith("humanoid"))


# ============================================================================================== kit helpers
def opener(name, amount, school="physical", **mech):
    """The basic attack. With `mech`, a passive rides on the first swing as a buff for the whole fight."""
    e = dmg(name, amount, school=school, boss_rework=1)
    if mech:
        e["rider"] = {"effect": "buff", "duration": 99, "stat_mods": {}, "mechanics": mech}
    return e


def phase(name, level, school="physical", hp=0.35, pct=40):
    """The low-health enrage, as attack power (the only damage stat a Monster reads off its own buffs)."""
    return dict(name=name, kind="buff", amount=0, cooldown=99, mana_cost=0, school=school, duration=30,
                self_only=True, hp_below=hp, stat_mods={"attack_power": int(B(level) * pct / 100)})


def stun_hit(name, amount, cooldown=5, school="physical"):
    return dmg(name, amount, cooldown=cooldown, school=school, authored_mechanic="stun",
               rider={"effect": "debuff", "duration": 1, "is_stun": True, "stat_mods": {}})


def shell(name, cooldown, duration, absorb, school="physical", **mech):
    e = dict(name=name, kind="buff", amount=0, cooldown=cooldown, mana_cost=0, school=school, duration=duration,
             self_only=True, stat_mods={}, absorb=absorb)
    if mech:
        e["mechanics"] = mech
    return e


def heal(name, amount, cooldown=5, school="holy"):
    return dict(name=name, kind="heal", amount=amount, cooldown=cooldown, mana_cost=0, school=school)


def summon(name, creature, cooldown, max_alive, max_casts):
    return dict(name=name, kind="summon", amount=0, cooldown=cooldown, mana_cost=0,
                summon={"name": creature, "template": ROSTER[creature][0], "kit": kit_slug(creature),
                        "count": 1, "level_offset": -1, "max_alive": max_alive, "max_casts": max_casts})


def boss_kit(level, school, basic, second, heavy, spread, mechanic, phase_name, *, aoe=True, opener_mech=None,
             extra=(), phase_pct=40):
    b = B(level)
    kit = [opener(basic, b, school, **(opener_mech or {})),
           dmg(second, int(b * 0.88), cooldown=4, school=school),
           dmg(heavy, int(b * 1.3), cooldown=4, school=school)]
    if aoe:
        kit.append(dmg(spread, int(b * 0.68), cooldown=5, school=school, is_aoe=True))
    else:
        kit.append(dot(spread, int(b * 0.36), 5, 4, school=school))
    if mechanic:
        kit.append(mechanic)
    kit.extend(extra)
    kit.append(phase(phase_name, level, school, pct=phase_pct))
    return kit


# ============================================================================================== the kits
def kits():
    k = {}
    # ---- Graveyard trash (28-31)
    t = T(31)
    k["Scarlet Torturer"] = [dmg("Barbed Lash", t), dmg("Hot Iron", int(t * 0.86), cooldown=3, school="fire"),
                             debuff("Break the Will", 5, 3, {"attack_power": -30})]
    k["Scarlet Scryer"] = [dmg("Smite", t, school="holy"),
                           dot("Searing Gaze", int(t * 0.26), 4, 3, school="fire", dispel_type="magic"),
                           debuff("Seen Through", 5, 3, {"dodge_rating": -30})]
    k["Haunting Phantasm"] = [dmg("Ghostly Touch", t, school="shadow"),
                              dmg("Pass Through", int(t * 0.86), cooldown=3, school="shadow"),
                              debuff("Chill of the Grave", 5, 3, {"haste": -10}, school="frost")]
    k["Anguished Dead"] = [dmg("Grasping Hands", t), dmg("Drag Down", int(t * 0.86), cooldown=3),
                           dot("Grave Rot", int(t * 0.24), 4, 3, school="nature", dispel_type="disease")]
    k["Unfettered Spirit"] = [dmg("Wail", t, school="shadow"),
                              dmg("Keening", int(t * 0.64), cooldown=5, school="shadow", is_aoe=True),
                              dot("Haunting", int(t * 0.26), 4, 3, school="shadow", dispel_type="curse")]
    # ---- Graveyard bosses
    k["Interrogator Maelis"] = boss_kit(          # burns and breaks: cleanse, heal through
        30, "physical", "Interrogator's Lash", "Thumbscrew", "Break the Silence", "Searing Brand",
        debuff("Confess", 5, 3, {"armor": -180, "attack_power": -40}), "Tell Me Everything", aoe=False,
        extra=[dot("Branding Iron", int(B(30) * 0.4), 5, 4, school="fire", dispel_type="magic")])
    k["Ironspine"] = boss_kit(                    # a giant of bone among the graves: poison, and bone that turns blades
        31, "physical", "Bone Crush", "Trample", "Ribcage Slam", "Graveyard Poison",
        shell("Bone Armour", 6, 3, int(B(31) * 1.4)), "Ironspine Rises", aoe=False)
    k["Azshir the Sleepless"] = boss_kit(         # a wraith that drains: spread out
        31, "shadow", "Grave Touch", "Call of the Grave", "Terrify", "Wail of the Sleepless",
        dict(name="Siphon Soul", kind="heal", amount=int(B(31) * 0.9), cooldown=5, mana_cost=0, school="shadow"),
        "Never Sleeps", extra=[stun_hit("Paralysing Dread", int(B(31) * 0.6), cooldown=6, school="shadow")])
    k["The Fallen Champion"] = boss_kit(          # hits harder as it falls: two steps, at two thirds and a third
        31, "physical", "Rusted Greatsword", "Grave Cleave", "Champion's Blow", "Sweep of the Tomb",
        dict(phase("Remembers the Fight", 31, hp=0.66, pct=25), cooldown=99), "Will Not Yield", phase_pct=60,
        extra=[buff("Tomb-Plate", 6, 3, {"armor": 260})])
    k["Bloodmage Thalnos"] = boss_kit(            # spells feed his ward: hit him with steel
        32, "fire", "Flame Spike", "Shadow Bolt", "Blood Fire", "Flame Nova",
        dot("Blood Curse", int(B(32) * 0.34), 5, 4, school="shadow", dispel_type="curse"), "The Blood Boils",
        opener_mech={"damage_to_shield_pct": 40, "damage_to_shield_school": "magic"})
    # ---- Library trash (32-35)
    t = T(35)
    k["Scarlet Adept"] = [dmg("Holy Smite", t, school="holy"), heal("Heal", int(t * 1.4)),
                          dot("Holy Fire", int(t * 0.26), 4, 3, school="holy", dispel_type="magic")]
    k["Scarlet Gallant"] = [dmg("Crusader Strike", t), dmg("Holy Strike", int(t * 0.86), cooldown=3, school="holy"),
                            buff("Devotion", 6, 3, {"armor": 140})]
    k["Scarlet Beastmaster"] = [dmg("Shoot", t), dmg("Aimed Shot", int(t * 1.1), cooldown=4),
                                debuff("Hunter's Mark", 5, 3, {"dodge_rating": -36})]
    k["Scarlet Tracking Hound"] = [dmg("Bite", t), dmg("Pounce", int(t * 0.86), cooldown=3),
                                   debuff("Hamstring", 5, 3, {"agility": -30})]
    k["Scarlet Monk"] = [dmg("Open Palm", t), dmg("Spinning Kick", int(t * 0.86), cooldown=3),
                         stun_hit("Pressure Point", int(t * 0.6), cooldown=6)]
    # ---- Library bosses
    k["Inquisitor Vellan Rook"] = boss_kit(       # marks a heretic and judges him: the healers watch the mark
        33, "holy", "Searing Light", "Brand of Heresy", "Judgement", "Consecrated Floor",
        debuff("Marked as Heretic", 5, 3, {"armor": -220, "dodge_rating": -30}, school="holy"), "No Appeal",
        extra=[stun_hit("Hammer of the Inquisition", int(B(33) * 0.6), cooldown=6, school="holy")])
    k["Houndmaster Loksey"] = boss_kit(           # his hounds first, or they mend him
        34, "physical", "Kennel Whip", "Bloodhound's Shot", "Set the Dogs", "Volley",
        summon("Release the Hounds", "Scarlet Tracking Hound", 4, 2, 4), "Master of the Kennels",
        extra=[heal("The Pack Licks His Wounds", int(B(34) * 1.1), cooldown=5, school="physical")])
    k["Archivist Dana Mercer"] = boss_kit(        # silences casters: melee carries her
        35, "arcane", "Index Bolt", "Redaction", "Burn the Margins", "Shelf Collapse",
        debuff("Closed for Study", 5, 3, {"spell_power": -60, "intellect": -40}, school="arcane"),
        "Every Page Accounted For",
        extra=[debuff("Hush", 6, 2, {"haste": -20, "mp5": -10}, school="arcane")])
    k["Curator Halbrecht"] = boss_kit(            # the gallery's guards come to him: kill the monks, then the man
        35, "arcane", "Pointer Rod", "Do Not Touch", "Glass Case Shatters", "Alarm Bell",
        summon("Guards to the Gallery", "Scarlet Monk", 4, 2, 4), "Priceless",
        extra=[shell("Under Glass", 6, 3, int(B(35) * 1.2), school="arcane")])
    k["Arcanist Doan"] = boss_kit(                # detonates: get away from him at the brink
        36, "arcane", "Arcane Bolt", "Arcane Missiles", "Silence of the Stacks", "Arcane Explosion",
        stun_hit("Polymorph", int(B(36) * 0.5), cooldown=6, school="arcane"), "Shielded by Pages",
        extra=[dict(dmg("Detonation", int(B(36) * 1.7), cooldown=99, school="arcane", is_aoe=True), hp_below=0.3)])
    # ---- Armory trash (35-38)
    t = T(38)
    k["Scarlet Trainee"] = [dmg("Wooden Sword", int(t * 0.8)), dmg("Shield Bash", int(t * 0.7), cooldown=3),
                            buff("Eager", 6, 3, {"attack_power": 30})]
    k["Scarlet Soldier"] = [dmg("Crusader Strike", t), dmg("Sunder Armour", int(t * 0.86), cooldown=3),
                            debuff("Sundered", 5, 3, {"armor": -200})]
    k["Scarlet Myrmidon"] = [dmg("Heavy Blade", t + 8), dmg("Overhead Strike", int(t * 0.9), cooldown=3),
                             buff("Frenzy", 6, 3, {"attack_power": 50})]
    k["Scarlet Defender"] = [dmg("Shield Slam", t), dmg("Revenge", int(t * 0.86), cooldown=3),
                             buff("Shield Wall", 6, 3, {"armor": 220})]
    k["Scarlet Evoker"] = [dmg("Fireball", t, school="fire"),
                           dmg("Flamestrike", int(t * 0.64), cooldown=5, school="fire", is_aoe=True),
                           debuff("Frost Nova", 5, 2, {"haste": -15}, school="frost")]
    # ---- Armory bosses
    k["Sergeant Major Cole Brennan"] = boss_kit(  # his recruits come in waves
        36, "physical", "Drill Cane", "On Your Feet", "Parade-Ground Throw", "Squad Charge",
        summon("Fall In!", "Scarlet Trainee", 4, 2, 5), "Double Time",
        extra=[stun_hit("Knee to the Gut", int(B(36) * 0.6), cooldown=6)])
    k["Quartermaster Bram Ellison"] = boss_kit(   # armour you have to cut through
        37, "physical", "Requisitioned Maul", "Inventory Check", "Crate Drop", "Spilled Stock",
        shell("Spare Plate", 6, 3, int(B(37) * 2.0)), "Everything Signed For",
        extra=[buff("Polished Plate", 5, 4, {"armor": 600})])
    k["Smithmaster Corra Bellweather"] = boss_kit(  # hot iron: burns that stack, and plate she tempers as you hit it
        37, "fire", "Hot Hammer", "Sparks", "Fresh From the Anvil", "Slag Spill",
        dot("Molten Slag", int(B(37) * 0.34), 5, 4, school="fire", dispel_type="magic", is_aoe=True), "Stoke the Forge",
        extra=[buff("Temper", 5, 4, {"armor": 500})])
    k["Master-at-Arms Dorran Pike"] = boss_kit(   # parries and sends steel back: casters carry this one
        38, "physical", "Partisan Thrust", "Riposte", "Disarming Strike", "Sweeping Strikes",
        debuff("Disarmed", 6, 2, {"attack_power": -120}), "Every Weapon in the Hall",
        opener_mech={"reflect_pct": 20, "reflect_school": "physical", "reflect_melee_only": True})
    k["Herod"] = boss_kit(                        # whirlwinds and enrages: the party moves
        39, "physical", "Herod's Greataxe", "Cleave", "Rushing Charge", "Whirlwind",
        dict(dmg("Bladestorm", int(B(39) * 0.9), cooldown=4, is_aoe=True)), "Blades of Light", phase_pct=60,
        extra=[debuff("Intimidating Shout", 6, 2, {"attack_power": -60, "spell_power": -40})])
    # ---- Cathedral trash (38-41)
    t = T(41)
    k["Scarlet Centurion"] = [dmg("Shield Bash", t), dmg("Battle Shout", int(t * 0.86), cooldown=3),
                              buff("Defensive Stance", 6, 3, {"armor": 240})]
    k["Scarlet Sorcerer"] = [dmg("Frostbolt", t, school="frost"),
                             dmg("Blizzard", int(t * 0.64), cooldown=5, school="frost", is_aoe=True),
                             debuff("Slow", 5, 3, {"haste": -15}, school="arcane")]
    k["Scarlet Champion"] = [dmg("Crusader Strike", t + 8), dmg("Holy Cleave", int(t * 0.9), cooldown=3,
                                                              school="holy"),
                             buff("Retribution", 6, 3, {"attack_power": 50})]
    k["Scarlet Wizard"] = [dmg("Fireball", t, school="fire"),
                           dot("Pyroblast Burn", int(t * 0.3), 4, 3, school="fire", dispel_type="magic"),
                           buff("Mana Shield", 6, 3, {"armor": 160})]
    k["Scarlet Abbot"] = [dmg("Holy Smite", t, school="holy"), heal("Renew", int(t * 1.5)),
                          debuff("Inner Fire Turned", 5, 3, {"intellect": -40}, school="holy")]
    # ---- Cathedral bosses
    k["Brother Garrick Thorne"] = boss_kit(       # the gardener: thorns on everything, roots underfoot
        39, "nature", "Pruning Hook", "Rose-Thorn Lash", "Entangling Roots", "Bramble Burst",
        dot("Thorn in the Side", int(B(39) * 0.34), 5, 4, school="nature", dispel_type="poison"), "The Garden Defends",
        opener_mech={"reflect_pct": 15, "reflect_school": "physical", "reflect_melee_only": True},
        extra=[heal("Tend the Beds", int(B(39) * 1.1), cooldown=6, school="nature")])
    k["Captain Elric Stane"] = boss_kit(          # the doors of the chapel: his guard first
        40, "physical", "Longsword", "Shield Bash", "Captain's Cleave", "Hold the Line",
        summon("Guard, to Me!", "Scarlet Centurion", 4, 2, 4), "None Shall Pass",
        extra=[shell("Shield Wall", 6, 3, int(B(40) * 1.5))])
    k["High Inquisitor Aldric"] = boss_kit(    # a corpse that will not stay dead
        40, "shadow", "Cold Hand", "Curse of Blood", "Sleep", "Power Word: Pain",
        dot("Unburied", int(B(40) * 0.34), 5, 4, school="shadow", dispel_type="curse"), "Still Here",
        opener_mech={"death_prevent_pct": 20, "death_prevent_uses": 1, "death_prevent_lethal_only": True})
    k["Brother Corwin Ashe"] = boss_kit(          # his sermon shields the faithful
        41, "holy", "Censer", "Holy Fire", "Rebuke", "Sermon of the Nave",
        shell("Shield of Faith", 5, 3, int(B(41) * 1.6), school="holy"), "Every Pew Full",
        extra=[heal("Laying On of Hands", int(B(41) * 1.2), cooldown=6)])
    k["High Inquisitor Whitemane"] = boss_kit(    # she mends herself and burns whoever is on him
        42, "holy", "Smite", "Holy Fire", "Dominate", "Scarlet Resurrection",
        heal("Flash Heal", int(B(42) * 1.3), cooldown=4), "Arise, My Champion",
        extra=[stun_hit("Deep Sleep", int(B(42) * 0.5), cooldown=6, school="holy")])
    k["Scarlet Commander Mograine"] = boss_kit(   # he holds the front and gets back up once
        42, "physical", "Crusader Strike", "Hammer of Justice", "Commander's Blow", "Consecration",
        shell("Divine Shield", 6, 2, int(B(42) * 1.4), school="holy", damage_to_shield_pct=100,
              damage_to_shield_school=""), "For the Crusade!",
        opener_mech={"death_prevent_pct": 30, "death_prevent_uses": 1, "death_prevent_lethal_only": True})
    return k


# ============================================================================================== the loot
#: (name, slot, suffix, armour or weapon type, template) per boss, in run order. Item level = boss level + 3.
POOLS = {
    "Interrogator Maelis": [
        ("Maelis's Branding Iron", "main_hand", "of the Gladiator", ("w", "mace_1h"), "str_physical"),
        ("Questioner's Apron", "chest", "of the Assassin", ("a", "leather"), "agi_physical"),
        ("Cell-Keeper's Ring", "ring", "of the Prophet", None, "spi_healer")],
    "Ironspine": [
        ("Spine of the Restless", "main_hand", "of the Bear", ("w", "mace_2h"), "str_physical"),
        ("Grave-Iron Gauntlets", "hands", "of the Champion", ("a", "plate"), "str_physical"),
        ("Bonelinked Belt", "waist", "of the Marksman", ("a", "mail"), "agi_physical")],
    "Azshir the Sleepless": [
        ("Sleepless Shroud", "back", "of the Archmage", ("a", "cloth"), "int_caster"),
        ("Grave-Grasp Handwraps", "hands", "of Shadow Wrath", ("a", "cloth"), "int_caster"),
        ("Ghostweave Leggings", "legs", "of the Hunt", ("a", "mail"), "agi_int_hybrid")],
    "The Fallen Champion": [
        ("The Champion's Grave-Blade", "main_hand", "of the Breaker", ("w", "sword_2h"), "str_physical"),
        ("Tomb-Rusted Pauldrons", "shoulder", "of the Champion", ("a", "plate"), "str_physical"),
        ("Last Vigil Bracers", "wrist", "of the Physician", ("a", "mail"), "spi_healer")],
    "Bloodmage Thalnos": [
        ("Blood-Inked Staff", "main_hand", "of Fiery Wrath", ("w", "staff"), "int_caster"),
        ("Bloodmage's Mantle", "shoulder", "of the Invoker", ("a", "cloth"), "int_caster"),
        ("Chain of the Bone Chapel", "neck", "of the Owl", None, "spi_healer")],
    "Inquisitor Vellan Rook": [
        ("Vellan's Branding Rod", "ranged", "of Fiery Wrath", ("w", "wand"), "int_caster"),
        ("Judgement-Bound Bracers", "wrist", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Hood of the Hall of Judgement", "head", "of the Wellspring", ("a", "leather"), "spi_healer")],
    "Houndmaster Loksey": [
        ("Houndmaster's Longbow", "ranged", "of the Marksman", ("w", "bow"), "agi_physical"),
        ("Kennelmaster's Jerkin", "chest", "of the Bandit", ("a", "leather"), "agi_physical"),
        ("Leash-Hand Gauntlets", "hands", "of the Hunt", ("a", "mail"), "agi_int_hybrid")],
    "Archivist Dana Mercer": [
        ("The Archivist's Ledger", "off_hand", "of the Prophet", ("w", "tome"), "spi_healer"),
        ("Hood of the Closed Stacks", "head", "of the Inquisitor", ("a", "cloth"), "int_caster"),
        ("Index-Keeper's Sash", "waist", "of the Physician", ("a", "leather"), "spi_healer")],
    "Curator Halbrecht": [
        ("Halbrecht's Ceremonial Blade", "main_hand", "of the Invoker", ("w", "sword_1h"), "int_caster"),
        ("Gallery Warden's Cloak", "back", "of the Monkey", ("a", "cloth"), "agi_physical"),
        ("Velvet-Rope Sash", "waist", "of the Owl", ("a", "cloth"), "spi_healer")],
    "Arcanist Doan": [
        ("Doan's Detonator", "ranged", "of the Invoker", ("w", "wand"), "int_caster"),
        ("Robe of the Athenaeum", "chest", "of the Archmage", ("a", "cloth"), "int_caster"),
        ("Doan's Cracked Lens", "trinket", "of the Mind's Eye", None, "int_caster")],
    "Sergeant Major Cole Brennan": [
        ("Drill Sergeant's Halberd", "main_hand", "of the Gladiator", ("w", "polearm"), "str_physical"),
        ("Parade-Ground Greaves", "legs", "of the Soldier", ("a", "plate"), "str_physical"),
        ("The Sergeant's Whistle", "trinket", "of the Champion", None, "str_physical")],
    "Quartermaster Bram Ellison": [
        ("Quartermaster's Tower Shield", "off_hand", "of Stamina", ("w", "shield"), "str_physical"),
        ("Inventory-Keeper's Gauntlets", "hands", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Armoury Chain Coif", "head", "of the Marksman", ("a", "mail"), "agi_physical")],
    "Smithmaster Corra Bellweather": [
        ("Smithmaster's Hammer", "main_hand", "of the Soldier", ("w", "mace_1h"), "str_physical"),
        ("Forge-Apron Chestguard", "chest", "of the Champion", ("a", "plate"), "str_physical"),
        ("Quenching Gloves", "hands", "of the Physician", ("a", "leather"), "spi_healer")],
    "Master-at-Arms Dorran Pike": [
        ("Master-at-Arms' Partisan", "main_hand", "of the Vanquisher", ("w", "polearm"), "str_physical"),
        ("Duellist's Leggings", "legs", "of the Assassin", ("a", "leather"), "agi_physical"),
        ("Pike's Parrying Bracers", "wrist", "of the Hunt", ("a", "mail"), "agi_int_hybrid")],
    "Herod": [
        ("Herod's Greataxe", "main_hand", "of the Breaker", ("w", "axe_2h"), "str_physical"),
        ("Hall of Champions Mantle", "shoulder", "of the Elder", ("a", "mail"), "spi_healer"),
        ("Band of the Champions' Hall", "ring", "of the Assassin", None, "agi_physical")],
    "Brother Garrick Thorne": [
        ("Gardener's Pruning Hook", "main_hand", "of the Falcon", ("w", "axe_1h"), "agi_int_hybrid"),
        ("Thorn-Woven Vest", "chest", "of the Wellspring", ("a", "leather"), "spi_healer"),
        ("Signet of the Chapel Gardens", "ring", "of the Owl", None, "spi_healer")],
    "Captain Elric Stane": [
        ("Chapel Guard's Kite Shield", "off_hand", "of the Bulwark", ("w", "shield"), "str_physical"),
        ("Captain's Plate Greaves", "legs", "of the Defender", ("a", "plate"), "str_physical"),
        ("Doorwarden's Cloak", "back", "of the Sorcerer", ("a", "cloth"), "int_caster")],
    "High Inquisitor Aldric": [
        ("Cell-Warden's Wristguards", "wrist", "of the Hunt", ("a", "leather"), "agi_int_hybrid"),
        ("Unburied Girdle", "waist", "of the Gorilla", ("a", "plate"), "str_int_hybrid"),
        ("Inquisitor's Grave-Cloak", "back", "of the Monkey", ("a", "cloth"), "agi_physical")],
    "Brother Corwin Ashe": [
        ("Brother Ashe's Censer", "main_hand", "of the Restorer", ("w", "mace_1h"), "spi_healer"),
        ("Nave-Walker's Hauberk", "chest", "of the Falcon", ("a", "mail"), "agi_int_hybrid"),
        ("Pew-Worn Boots", "feet", "of the Prophet", ("a", "leather"), "spi_healer")],
    # the Cathedral's pair share this hoard; three of the nine drop
    "High Inquisitor Whitemane": [
        ("Scepter of the Scarlet Chancel", "main_hand", "of the Invoker", ("w", "mace_1h"), "int_caster"),
        ("The Commander's Longsword", "main_hand", "of the Gladiator", ("w", "sword_2h"), "str_physical"),
        ("Commander's Parrying Dagger", "main_hand", "of the Assassin", ("w", "dagger"), "agi_physical"),
        ("High Inquisitor's Mitre", "head", "of the Prophet", ("a", "cloth"), "spi_healer"),
        ("Crimson Commander's Pauldrons", "shoulder", "of the Champion", ("a", "plate"), "str_physical"),
        ("Chancel-Guard Leggings", "legs", "of the Bandit", ("a", "leather"), "agi_physical"),
        ("Scarlet Chain Girdle", "waist", "of the Hunt", ("a", "mail"), "agi_int_hybrid"),
        ("Ring of the Crimson Oath", "ring", "of the Gorilla", None, "str_int_hybrid"),
        ("The Chapel Reliquary", "trinket", "of the Prophet", None, "spi_healer")],
}

#: trinkets that do something (the same proc engine as the 51-58 rares, tools/build_tempest_loot.PROCS), sized
#: for item level 39 to 45
PROCS = {
    "Doan's Cracked Lens": {
        "trigger": "on_damage_cast", "chance": 8, "icd": 5,
        "apply_effect": {"effect_id": "doans_cracked_lens", "name": "Something Seen Clearly",
                         "effect_type": "buff", "duration": 3, "stat_mods": {"spell_power": 24}, "on_target": False},
        "describe": "Your damaging spells have a chance to grant 24 spell power for 3 turns.",
    },
    "The Sergeant's Whistle": {
        "trigger": "on_damage_taken", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "sergeants_whistle", "name": "Fall In",
                         "effect_type": "buff", "duration": 3, "stat_mods": {"armor": 300}, "on_target": False},
        "describe": "When you are hit, you have a chance to gain 300 armour for 3 turns.",
    },
    "The Chapel Reliquary": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "chapel_reliquary", "name": "Answered in the Chapel",
                         "effect_type": "buff", "duration": 3, "stat_mods": {"healing_power": 34},
                         "on_target": False},
        "describe": "Your healing spells have a chance to grant 34 healing power for 3 turns.",
    },
}


def build_loot():
    from tools.build_durotar_content import make
    from entities.item_budget import budget_ratio, fit_to_curve
    out, rows, moved = {}, [], 0
    for boss, items in POOLS.items():
        ilvl = ROSTER[boss][2] + 3
        built = []
        for (name, slot, suffix, typ, template) in items:
            kw = {}
            if typ and typ[0] == "a":
                kw["armor_type"] = typ[1]
            elif typ:
                kw["weapon_type"] = typ[1]
            d = make(name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            d["stat_template"] = template
            d["item_id"] = "sm_" + kit_slug(name)
            if name in PROCS:
                d["proc"] = PROCS[name]
            r = budget_ratio(d)
            if r is not None and not 0.65 <= r <= 1.45:      # the curve's band (tools/audit_item_curve.py)
                fit_to_curve(d)
                moved += 1
            built.append(d)
            kind = "weapon" if typ and typ[0] == "w" else "armor"
            rows.append((name, slot, kind, typ[1] if typ else None, template))
        out[boss] = built
    return out, rows, moved


# ============================================================================================== checks + write
def _wings(r):
    return r[5] if isinstance(r[5], tuple) else (r[5],)


def check(k, loot):
    bad = []
    if set(k) != set(ROSTER):
        bad.append(f"kits and roster differ: {sorted(set(k) ^ set(ROSTER))}")
    want_bosses = BOSSES - set(PACK_MEMBER)
    if set(POOLS) != want_bosses:
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ want_bosses)}")
    for b, items in loot.items():
        want = 9 if b in PACK_MEMBER.values() else 3
        if len(items) != want:
            bad.append(f"{b}: {len(items)} items, wanted {want}")
        for i in items:
            if i["item_level"] != ROSTER[b][2] + 3:
                bad.append(f"{i['name']}: item level {i['item_level']} on a level {ROSTER[b][2]} boss")
            if i["slot"] == "trinket" and not i.get("proc"):
                bad.append(f"{i['name']} is a trinket that does nothing")
    # every name the map spawns is a creature here, and every boss the map places is one of ours
    for wing, spec in SM.WING.items():
        spawned = {m for p in spec["trash"] for (_x, _y, m, _l) in p}
        placed = {n for (_x, _y, n, _r) in spec["bosses"]} | {m for ms in spec["pack"].values() for (*_p, m) in ms}
        ours = {n for n, r in ROSTER.items() if wing in _wings(r)}
        if not spawned <= ours:
            bad.append(f"{wing}: spawns creatures with no record: {sorted(spawned - ours)}")
        if placed != {n for n in ours if n in BOSSES}:
            bad.append(f"{wing}: bosses on the map differ from the roster: {sorted(placed ^ (ours & BOSSES))}")
        for p in spec["trash"]:
            for (_x, _y, m, lvl) in p:
                lo, hi = ROSTER[m][1], ROSTER[m][2]
                if not lo <= lvl <= hi:
                    bad.append(f"{wing}: {m} spawns at {lvl}, outside its {lo}-{hi}")
        lo, hi = ZONE_LEVELS[wing]
        for n in ours:
            if len(_wings(ROSTER[n])) > 1:
                continue                 # spans two wings: its spawns are checked above
            if not (lo <= ROSTER[n][1] and ROSTER[n][2] <= hi):
                bad.append(f"{n} ({ROSTER[n][1]}-{ROSTER[n][2]}) sits outside {wing} {lo}-{hi}")
    existing = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    kits_now = json.loads(KITS.read_text(encoding="utf-8"))["kits"]
    owners = {v.get("ability_kit"): n for n, v in existing.items()}
    for name, (_t, lo, hi, _m, sprite, _w) in ROSTER.items():
        s = kit_slug(name)
        if s in kits_now and owners.get(s, name) != name:
            bad.append(f"{name}'s kit '{s}' already belongs to {owners[s]}")
        prior = existing.get(name)
        if prior and prior.get("level_range") != [lo, hi]:
            bad.append(f"{name} already exists elsewhere at {prior.get('level_range')}; names never repeat")
        if not (ROOT / "assets/creatures" / f"{sprite}.png").exists():
            bad.append(f"{name}'s sprite {sprite} is not on disk")
    names = [i["name"] for v in loot.values() for i in v]
    dup = [n for n, c in Counter(names).items() if c > 1]
    if dup:
        bad.append(f"duplicate item names: {dup}")
    return bad


def main():
    k = kits()
    loot, rows, moved = build_loot()
    bad = check(k, loot)
    problems = loot_audit(rows)
    if bad or problems:
        print("FAILED - fix the data, not the check:")
        for b in bad + problems:
            print("  -", b)
        return 1

    creatures = {}
    for name, (template, lo, hi, mult, _sprite, _w) in ROSTER.items():
        e = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult), "ability_kit": kit_slug(name)}
        if mult:
            e["boss_multiplier"] = mult
        creatures[name] = e
    merge_json(CREATURES, "creatures", creatures, "creatures.json")
    merge_json(KITS, "kits", {kit_slug(n): v for n, v in k.items()}, "ability_kits.json")

    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    caves = enc["zones"].setdefault(REGION, {}).setdefault("caves", {})
    for wing in SM.WINGS:
        caves[wing] = {"name": wing, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items()
                                                   if wing in _wings(r)}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    print(f"  encounters.json: {REGION} caves + the four wings")

    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    indent, newline = _detect_format(lv, raw)
    lv["zones"].update(ZONE_LEVELS)
    LEVELS.write_text(json.dumps(lv, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")
    print(f"  zone_levels.json: {len(ZONE_LEVELS)} maps")

    out = {"_notes": ("Boss loot for the Scarlet Monastery's four wings (28-42). ONE item per kill from the boss's "
                      "three; the Cathedral's pair (Whitemane and Mograine) share nine and drop three. item_level = "
                      "boss level + 3. Hand-authored in tools/build_scarlet_monastery_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    n = sum(len(v) for v in loot.values())
    print(f"  {LOOT.relative_to(ROOT)}: {len(loot)} pools, {n} items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
