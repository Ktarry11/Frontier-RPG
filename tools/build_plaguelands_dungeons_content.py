#!/usr/bin/env python3
"""Scholomance, Stratholme (both halves) and Hearthglen: creatures, fighting kits, encounter tables, zone levels,
boss loot and the T0 head, chest and feet tokens. Idempotent.

    PYTHONPATH=. python3 tools/build_plaguelands_dungeons_content.py

The maps are tools/handbuilt_scholomance.py, tools/handbuilt_stratholme.py and tools/handbuilt_hearthglen.py (their
docstrings have the rooms and what each boss asks of a party); docs/plaguelands_dungeons_structure.md has the plan.
Kyle, 16 Nov 2026: "Ensure that scholomance and Stratholme live up to their wow parts. Multiple bosses", "Dead is two
layers as it's massive. Live is one layer as its smaller", "Hearthglen can be 2 layers as well". So classic's rosters,
in classic's rooms and order, thirty-six bosses over six floors.

THE NUMBERS are read off the game's own 54-60 bosses and trash (medians of every kit in the band, 16 Nov 2026), so these
sit with the Royal Hive and Jaedenar rather than above them:
    boss basic   B(L) = 10 * L - 200       medians: 360 at 56, 380 at 58, 400 at 60
    trash basic  T(L) =  4 * L - 10        medians: 215 at 56, 222 at 58, 230 at 60
    boss health  2.3 optional, 2.5 required, 2.8 the last boss of a floor
On top of that, world/difficulty.py's endgame_boss row makes every boss from 50 up hit a quarter harder.

THE T0 TOKENS (docs/plaguelands_design.md): Scholomance drops the head, Stratholme the chest (both halves), Hearthglen
the feet, 20% a boss and always from the last; so no boss in those dungeons carries an item in its token's slot.
Written into data/items/set_tokens.json beside the Tempest isle's (tools/build_tempest_loot.tokens reads PL_TOKENS
back from here, so a rebuild of either keeps both).

WHO PAYS. Scarlets killed in Stratholme and Hearthglen pay the Order of the Pale Flame; the Scourge in Scholomance and
Stratholme pays the Argent Dawn (tools/build_plaguelands_factions.py reads SCARLETS and SCOURGE from here).
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff, loot_audit)
from tools import handbuilt_scholomance as SCH  # noqa: E402
from tools import handbuilt_stratholme as STR  # noqa: E402
from tools import handbuilt_hearthglen as HG  # noqa: E402

LOOT = ROOT / "data/loot/plaguelands_dungeons_boss_loot.json"
LEVELS = ROOT / "data/zones/zone_levels.json"
TOKENS = ROOT / "data/items/set_tokens.json"

SU, SL = SCH.UPPER, SCH.LOWER
LV, D1, D2 = STR.LIVE, STR.DEAD_1, STR.DEAD_2
HT, HK = HG.TOWN, HG.KEEP
#: floor -> (region whose encounter table holds it, its levels, its spec)
FLOORS = {
    SU: (SCH.REGION, [56, 58], SCH.FLOOR[SU]), SL: (SCH.REGION, [58, 60], SCH.FLOOR[SL]),
    LV: (STR.REGION, [57, 59], STR.FLOOR[LV]), D1: (STR.REGION, [58, 59], STR.FLOOR[D1]),
    D2: (STR.REGION, [59, 60], STR.FLOOR[D2]),
    HT: (HG.REGION, [58, 59], HG.FLOOR[HT]), HK: (HG.REGION, [59, 60], HG.FLOOR[HK]),
}
ZONE_LEVELS = {f: v[1] for f, v in FLOORS.items()}


def B(level):
    return 10 * level - 200


def T(level):
    return 4 * level - 10


# ============================================================================================== the roster
#: name -> (template, lo, hi, boss multiplier or None, sprite, floor or floors)
ROSTER = {
    # ---------------------------------------------------------------- Scholomance, the upper floor (56-58)
    "Scholomance Student":       ("humanoid_caster",  56, 57, None, "pl_cult_neophyte", SU),
    "Scholomance Neophyte":      ("humanoid_caster",  56, 57, None, "pl_dark_caster", SU),
    "Scholomance Necrolyte":     ("humanoid_caster",  57, 58, None, "pl_necrolyte", SU),
    "Scholomance Dark Summoner": ("humanoid_caster",  57, 58, None, "pl_cult_lieutenant", SU),
    "Risen Guard":               ("undead_warrior",   57, 58, None, "skeleton_warrior_2", SU),
    "Necrofiend":                ("undead_beast",     57, 58, None, "pl_crypt_fiend", SU),
    "Reanimated Corpse":         ("undead_basic",     57, 57, None, "zombie_3", SU),
    "Plagued Hatchling":         ("beast_fast",       56, 56, None, "pl_plaguebat", SU),
    "Kirtonos the Herald":       ("undead_beast",     57, 57, 2.5, "scholo_boss_gargoyle", SU),
    "Jandice Barov":             ("undead_caster",    57, 57, 2.5, "scholo_boss_ghost_lady", SU),
    "Rattlegore":                ("undead_warrior",   58, 58, 2.5, "scholo_boss_bone_construct", SU),
    "Marduk Blackpool":          ("undead_warrior",   58, 58, 2.3, "pl_death_knight", SU),
    "Vectus":                    ("humanoid_caster",  58, 58, 2.3, "scholo_boss_alchemist", SU),
    "Ras Frostwhisper":          ("undead_caster",    58, 58, 2.8, "scholo_boss_frost_lich", SU),
    # ---------------------------------------------------------------- Scholomance, the Lower Halls (58-60)
    "Bone Minion":               ("undead_basic",     58, 59, None, "skeleton_warrior_1", SL),
    "Risen Aberration":          ("undead_beast",     58, 59, None, "pl_plague_eruptor", SL),
    "Risen Construct":           ("undead_warrior",   58, 60, None, "pl_flesh_golem", SL),
    "Scholomance Necromancer":   ("humanoid_caster",  58, 60, None, "pl_boss_cult_necromancer", SL),
    "Spectral Researcher":       ("undead_caster",    58, 59, None, "pl_wailing_spirit", SL),
    "Spectral Tutor":            ("undead_caster",    58, 60, None, "scholo_ghost_servant", SL),
    "Unstable Corpse":           ("undead_basic",     59, 59, None, "zombie_4", SL),
    "Instructor Malicia":        ("humanoid_caster",  59, 59, 2.5, "scholo_boss_instructor", SL),
    "Doctor Theolen Krastinov":  ("humanoid_warrior", 59, 59, 2.3, "pl_boss_abom_butcher", SL),
    "Lorekeeper Polkelt":        ("undead_caster",    59, 59, 2.3, "scholo_boss_librarian", SL),
    "The Ravenian":              ("undead_warrior",   59, 59, 2.5, "pl_boss_gate_guardian", SL),
    "Lord Alexei Barov":         ("undead_caster",    60, 60, 2.4, "scholo_boss_noble_lord", SL),
    "Lady Illucia Barov":        ("undead_caster",    60, 60, 2.3, "scholo_boss_noble_lady", SL),
    "Darkmaster Gandling":       ("humanoid_caster",  60, 60, 2.8, "scholo_boss_headmaster", SL),
    # ---------------------------------------------------------------- Stratholme, the living side (57-59)
    "Skeletal Guardian":         ("undead_warrior",   57, 57, None, "skeleton_warrior_2", LV),
    "Skeletal Berserker":        ("undead_warrior",   57, 57, None, "skeleton_warrior_1", LV),
    "Plague Ghoul":              ("undead_basic",     57, 57, None, "pl_frenzied_ghoul", LV),
    "Ghostly Citizen":           ("undead_caster",    57, 58, None, "pl_darrowshire_ghost", LV),
    "Spectral Citizen":          ("undead_caster",    57, 57, None, "spectre_1", LV),
    "Wailing Banshee":           ("undead_caster",    58, 58, None, "banshee", LV),
    "Fleshflayer Ghoul":         ("undead_basic",     58, 58, None, "ghoul_gaunt", LV),
    "Patchwork Horror":          ("undead_warrior",   58, 58, None, "abomination_1", LV),
    "Vengeful Phantom":          ("undead_caster",    58, 58, None, "spectre_2", LV),
    "Rockwing Gargoyle":         ("undead_beast",     58, 59, None, "pl_gargoyle", (LV, D1)),
    "Crimson Guardsman":         ("humanoid_warrior", 58, 59, None, "sc_centurion", LV),
    "Crimson Conjuror":          ("humanoid_caster",  58, 58, None, "sc_arcanist", LV),
    "Crimson Initiate":          ("humanoid_caster",  58, 58, None, "sc_tp_cleric", LV),
    "Crimson Gallant":           ("humanoid_warrior", 58, 59, None, "sc_knight", LV),
    "Crimson Defender":          ("humanoid_warrior", 58, 59, None, "sc_tp_crusader", LV),
    "Crimson Priest":            ("humanoid_caster",  58, 58, None, "sc_chaplain", LV),
    "Crimson Rifleman":          ("humanoid_ranged",  58, 59, None, "sc_tp_sniper", LV),
    "Crimson Monk":              ("humanoid_rogue",   58, 59, None, "sc_monk", LV),
    "Crimson Battle Mage":       ("humanoid_caster",  59, 59, None, "sc_adept", LV),
    "Crimson Sorcerer":          ("humanoid_caster",  59, 59, None, "sc_tp_inquisitor", LV),
    "Crimson Inquisitor":        ("humanoid_caster",  59, 59, None, "sc_inquisitor", LV),
    "Skul":                      ("undead_caster",    57, 57, 2.3, "pl_skeletal_mage", LV),
    "Hearthsinger Forresten":    ("undead_caster",    57, 57, 2.5, "pl_silver_hand_ghost", LV),
    "The Unforgiven":            ("undead_warrior",   58, 58, 2.5, "pl_boss_lich_magistrate", LV),
    "Timmy the Cruel":           ("undead_basic",     58, 58, 2.3, "strat_boss_ghoul_runt", LV),
    "Cannon Master Willey":      ("humanoid_ranged",  59, 59, 2.5, "strat_boss_cannon_master", LV),
    "Archivist Galford":         ("humanoid_caster",  59, 59, 2.5, "strat_boss_archivist", LV),
    "Grand Crusader Dathrohan":  ("humanoid_warrior", 59, 59, 2.8, "strat_boss_grand_crusader", LV),
    # ---------------------------------------------------------------- Stratholme, the Service Entrance (58-59)
    "Ghoul Ravener":             ("undead_basic",     58, 58, None, "ghoul_1", D1),
    "Mangled Cadaver":           ("undead_basic",     58, 59, None, "zombie_5", D1),
    "Broken Cadaver":            ("undead_basic",     58, 59, None, "zombie_6", D1),
    "Plagued Crypt Crawler":     ("undead_beast",     58, 59, None, "spider_4", D1),
    "Crypt Beast":               ("undead_beast",     58, 58, None, "pl_crypt_fiend", D1),
    "Undead Scarab":             ("vermin_swarm",     58, 58, None, "spider_hatchling", D1),
    "Thuzadin Acolyte":          ("humanoid_caster",  58, 59, None, "pl_cult_plaguebringer", (D1, D2)),
    "Thuzadin Shadowcaster":     ("humanoid_caster",  58, 59, None, "pl_dark_caster", D1),
    "Thuzadin Necromancer":      ("humanoid_caster",  59, 59, None, "necromancer", D1),
    "Rockwing Screecher":        ("undead_beast",     59, 59, None, "pl_plaguebat", D1),
    "Eye of Naxxramas":          ("undead_caster",    59, 59, None, "pl_boss_eye_construct", D1),
    "Magistrate Barthilas":      ("undead_caster",    58, 58, 2.5, "strat_boss_magistrate", D1),
    "Stonespine":                ("undead_beast",     58, 58, 2.3, "scholo_boss_gargoyle", D1),
    "Nerub'enkan":               ("undead_beast",     59, 59, 2.5, "strat_boss_crypt_lord", D1),
    "Baroness Anastari":         ("undead_caster",    59, 59, 2.5, "strat_boss_baroness", D1),
    "Maleki the Pallid":         ("undead_caster",    59, 59, 2.8, "strat_boss_lich", D1),
    # ---------------------------------------------------------------- Stratholme, Slaughter Square (59-60)
    "Venom Belcher":             ("undead_warrior",   59, 59, None, "pl_plague_eruptor", D2),
    "Bile Spewer":               ("undead_warrior",   59, 59, None, "abomination_2", D2),
    "Bile Slime":                ("undead_basic",     59, 59, None, "pl_plague_slime", D2),
    "Mindless Undead":           ("undead_basic",     60, 60, None, "zombie_1", D2),
    "Black Guard Sentry":        ("undead_warrior",   60, 60, None, "revenant_2", D2),
    "Ramstein the Gorger":       ("undead_warrior",   60, 60, 2.5, "strat_boss_flesh_golem", D2),
    "Baron Rivendare":           ("undead_warrior",   60, 60, 2.8, "strat_boss_baron", D2),
    # ---------------------------------------------------------------- Hearthglen, the town (58-59)
    "Hearthglen Arbalest":       ("humanoid_ranged",  58, 59, None, "sc_tp_sniper", HT),
    "Hearthglen Cleric":         ("humanoid_caster",  58, 59, None, "sc_tp_cleric", HT),
    "Hearthglen Field Medic":    ("humanoid_caster",  58, 58, None, "sc_chaplain", HT),
    "Hearthglen Mastiff":        ("beast_fast",       58, 58, None, "sc_war_hound", HT),
    "Hearthglen Templar":        ("humanoid_warrior", 58, 59, None, "sc_tp_crusader", HT),
    "Hearthglen Zealot":         ("humanoid_rogue",   58, 59, None, "sc_zealot", HT),
    "High Protector Tarsen":     ("humanoid_warrior", 58, 58, 2.5, "hg_boss_gatewarden", HT),
    "Huntsman Radley":           ("humanoid_ranged",  58, 58, 2.3, "hg_boss_kennelmaster", HT),
    "Chirurgeon Maeve Ostrowski": ("humanoid_caster", 58, 58, 2.3, "hg_boss_crimson_choir", HT),
    "High Clerist Hendrick":     ("humanoid_caster",  59, 59, 2.5, "hg_boss_high_inquisitor", HT),
    "High Protector Lorik":      ("humanoid_warrior", 59, 59, 2.8, "hg_boss_volkov", HT),
    # ---------------------------------------------------------------- Hearthglen, Mardenholde Keep (59-60)
    "Mardenholde Battle Priest": ("humanoid_caster",  59, 60, None, "sc_judicator", HK),
    "Mardenholde Crossbowman":   ("humanoid_ranged",  59, 60, None, "sc_tp_sniper", HK),
    "Mardenholde Halberdier":    ("humanoid_warrior", 59, 60, None, "sc_myrmidon", HK),
    "Mardenholde Knight":        ("humanoid_warrior", 59, 60, None, "sc_tp_champion", HK),
    "Scarlet Commander Marjhan": ("humanoid_caster",  59, 59, 2.5, "hg_boss_arcanist", HK),
    "Armsmaster Grell":          ("humanoid_warrior", 59, 59, 2.3, "hg_boss_quartermaster", HK),
    "Drillmaster Osric Pell":    ("humanoid_warrior", 60, 60, 2.5, "hg_boss_drillmaster", HK),
    "High General Abbendis":     ("humanoid_warrior", 60, 60, 2.5, "hg_boss_lady_marden", HK),
    "Grand Crusader Victor Hale": ("humanoid_warrior", 60, 60, 2.8, "hg_boss_victor_hale", HK),
}
BOSSES = {n for n, r in ROSTER.items() if r[3]}
#: one fight, two bosses: Lady Illucia stands with Lord Alexei, and their hoard is his
PACK_MEMBER = {"Lady Illucia Barov": "Lord Alexei Barov"}
#: who the Order of the Pale Flame pays for, and who the Argent Dawn does
SCARLETS = sorted(n for n, r in ROSTER.items() if not r[3] and n.startswith(("Crimson", "Hearthglen", "Mardenholde")))
SCOURGE = sorted(n for n, r in ROSTER.items() if not r[3] and n not in SCARLETS)

#: dungeon -> (its floors, the T0 token slot it carries, bosses in run order, the last boss)
DUNGEONS = {
    "Scholomance": ((SU, SL), "head",
                    ["Kirtonos the Herald", "Jandice Barov", "Rattlegore", "Marduk Blackpool", "Vectus",
                     "Ras Frostwhisper", "Instructor Malicia", "Doctor Theolen Krastinov", "Lorekeeper Polkelt",
                     "The Ravenian", "Lord Alexei Barov", "Darkmaster Gandling"], "Darkmaster Gandling"),
    "Stratholme": ((LV,), "chest",
                   ["Skul", "Hearthsinger Forresten", "The Unforgiven", "Timmy the Cruel", "Cannon Master Willey",
                    "Archivist Galford", "Grand Crusader Dathrohan"], "Grand Crusader Dathrohan"),
    "Stratholme: the Scourge's side": ((D1, D2), "chest",
                                       ["Magistrate Barthilas", "Stonespine", "Nerub'enkan", "Baroness Anastari",
                                        "Maleki the Pallid", "Ramstein the Gorger", "Baron Rivendare"],
                                       "Baron Rivendare"),
    "Hearthglen": ((HT, HK), "feet",
                   ["High Protector Tarsen", "Huntsman Radley", "Chirurgeon Maeve Ostrowski", "High Clerist Hendrick",
                    "High Protector Lorik", "Scarlet Commander Marjhan", "Armsmaster Grell", "Drillmaster Osric Pell",
                    "High General Abbendis", "Grand Crusader Victor Hale"], "Grand Crusader Victor Hale"),
}
ARMOUR = ("plate", "mail", "leather", "cloth")
TOKEN_CHANCE = 0.20
TOKEN_NAMES = {"head": "T0 Helm Token", "chest": "T0 Chest Token", "feet": "T0 Boots Token"}
SLOT_WORD = {"head": "helm", "chest": "chest", "feet": "boots"}
TOKEN_ICON_CLASS = {"plate": "warrior", "mail": "shaman", "leather": "rogue", "cloth": "priest"}


def PL_TOKENS():
    """-> (token defs, {boss: {slot, guaranteed, types}}), the same shape as tools/build_tempest_loot.tokens()."""
    defs = {}
    for slot, title in TOKEN_NAMES.items():
        for t in ARMOUR:
            defs[f"t0_token_{slot}_{t}"] = {
                "name": f"{title} ({t.title()})", "slot": slot, "armor_type": t, "tier": "T0",
                "icon_id": f"t0_{TOKEN_ICON_CLASS[t]}_{slot}",
                "description": (f"A token. Any Artifact Keeper will trade it for the T0 set "
                                f"{SLOT_WORD[slot]} of a class that wears {t}."),
            }
    bosses = {}
    for _floors, slot, run, last in DUNGEONS.values():
        for i, name in enumerate(run):
            fin = name == last
            bosses[name] = {"slot": slot, "guaranteed": fin,
                            "types": list(ARMOUR) if fin else [t for k, t in enumerate(ARMOUR) if k != i % 4]}
    return defs, bosses


# ============================================================================================== kit helpers
def opener(name, amount, school="physical", **mech):
    e = dmg(name, amount, school=school, boss_rework=1)
    if mech:
        e["rider"] = {"effect": "buff", "duration": 99, "stat_mods": {}, "mechanics": mech}
    return e


def phase(name, level, school="physical", hp=0.35, pct=40):
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


def hit_with(name, amount, stat_mods, duration=3, school="physical", on="debuff", **kw):
    """A hit that carries its buff or debuff (a boss never spends a turn on a plain debuff while it has an attack)."""
    return dmg(name, amount, school=school, rider={"effect": on, "duration": duration, "stat_mods": stat_mods}, **kw)


def last_gasp(name, level, school="physical", mult=1.6):
    """The once-only party blast at 30%."""
    return dict(dmg(name, int(B(level) * mult), cooldown=99, school=school, is_aoe=True), hp_below=0.3)


def boss_kit(level, school, basic, second, heavy, spread, mechanic, phase_name, *, signature, aoe=True,
             opener_mech=None, extra=(), phase_pct=40):
    """Every boss carries something dangerous (Kyle, 16 Nov 2026: "make sure bosses are not just debuffing. they
    should have something dangerous"): required, so no boss can be written without one."""
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
    kit.extend(signature if isinstance(signature, list) else [signature])
    kit.append(phase(phase_name, level, school, pct=phase_pct))
    return kit


#: trash shapes: each is (basic, second, third) laid onto one of these
def trash(kind, level, a, b, c, school="physical", dispel="magic"):
    t = T(level)
    s = school
    if kind == "melee":
        return [dmg(a, t, school=s), dmg(b, int(t * 0.86), cooldown=3, school=s),
                buff(c, 6, 3, {"attack_power": 50})]
    if kind == "tank":
        return [dmg(a, t, school=s), dmg(b, int(t * 0.86), cooldown=3, school=s), buff(c, 6, 3, {"armor": 240})]
    if kind == "caster":
        return [dmg(a, t, school=s), dmg(b, int(t * 0.64), cooldown=5, school=s, is_aoe=True),
                debuff(c, 5, 3, {"haste": -15}, school=s)]
    if kind == "dotcaster":
        return [dmg(a, t, school=s), dot(b, int(t * 0.26), 4, 3, school=s, dispel_type=dispel),
                debuff(c, 5, 3, {"intellect": -40}, school=s)]
    if kind == "healer":
        return [dmg(a, t, school=s), heal(b, int(t * 1.4)), dot(c, int(t * 0.26), 4, 3, school=s,
                                                               dispel_type="magic")]
    if kind == "ranged":
        return [dmg(a, t, school=s), dmg(b, int(t * 1.1), cooldown=4, school=s),
                debuff(c, 5, 3, {"dodge_rating": -36})]
    if kind == "beast":
        return [dmg(a, t), dmg(b, int(t * 0.86), cooldown=3), debuff(c, 5, 3, {"agility": -30})]
    if kind == "disease":
        return [dmg(a, t, school=s), dmg(b, int(t * 0.86), cooldown=3, school=s),
                dot(c, int(t * 0.24), 4, 3, school="nature", dispel_type="disease")]
    if kind == "poison":
        return [dmg(a, t, school=s), dmg(b, int(t * 0.86), cooldown=3, school=s),
                dot(c, int(t * 0.24), 4, 3, school="nature", dispel_type="poison")]
    if kind == "stunner":
        return [dmg(a, t, school=s), dmg(b, int(t * 0.86), cooldown=3, school=s),
                stun_hit(c, int(t * 0.6), cooldown=6, school=s)]
    if kind == "ghost":
        return [dmg(a, t, school="shadow"), dmg(b, int(t * 0.86), cooldown=3, school="shadow"),
                debuff(c, 5, 3, {"haste": -10}, school="frost")]
    if kind == "brute":
        return [dmg(a, t + 10, school=s), dmg(b, int(t * 0.64), cooldown=5, school=s, is_aoe=True),
                buff(c, 6, 3, {"attack_power": 60})]
    raise ValueError(kind)


TRASH = {
    # Scholomance, upper
    "Scholomance Student": ("dotcaster", 57, "Shadow Bolt", "Clumsy Curse", "Bad Homework", "shadow", "curse"),
    "Scholomance Neophyte": ("caster", 57, "Frostbolt", "Frost Nova", "Chill", "frost"),
    "Scholomance Necrolyte": ("dotcaster", 58, "Shadow Bolt", "Shadow Word: Pain", "Drain Will", "shadow"),
    "Scholomance Dark Summoner": ("caster", 58, "Shadow Bolt", "Dark Circle", "Bind the Will", "shadow"),
    "Risen Guard": ("tank", 58, "Rusted Halberd", "Shield Bash", "Bone Shield"),
    "Necrofiend": ("poison", 58, "Rend", "Web Spray", "Necrotic Poison"),
    "Reanimated Corpse": ("disease", 57, "Rotting Fist", "Pummel", "Corpse Rot"),
    "Plagued Hatchling": ("beast", 56, "Claw", "Wing Buffet", "Plague Breath"),
    # Scholomance, lower
    "Bone Minion": ("melee", 59, "Bone Blade", "Rib Rake", "Rattle"),
    "Risen Aberration": ("disease", 59, "Lash", "Bile Spit", "Aberrant Rot"),
    "Risen Construct": ("brute", 60, "Cleave", "Bone Sweep", "Enrage"),
    "Scholomance Necromancer": ("dotcaster", 60, "Shadow Bolt", "Curse of Agony", "Bone Armour", "shadow", "curse"),
    "Spectral Researcher": ("ghost", 59, "Arcane Touch", "Mana Burn", "Chill of the Stacks"),
    "Spectral Tutor": ("ghost", 60, "Ghostly Strike", "Image Projection", "Silence the Class"),
    "Unstable Corpse": ("disease", 59, "Lurch", "Burst", "Disease Cloud"),
    # Stratholme, the living side
    "Skeletal Guardian": ("tank", 57, "Guard's Blade", "Shield Slam", "Bone Shield"),
    "Skeletal Berserker": ("melee", 57, "Rusted Axe", "Frenzied Chop", "Berserk"),
    "Plague Ghoul": ("disease", 57, "Claw", "Ghoul Bite", "Ghoul Plague"),
    "Ghostly Citizen": ("ghost", 58, "Haunting Touch", "Spectral Grasp", "Chill of the Dead"),
    "Spectral Citizen": ("ghost", 57, "Grave Touch", "Wail", "Cold Hands"),
    "Wailing Banshee": ("caster", 58, "Shriek", "Deafening Wail", "Banshee Curse", "shadow"),
    "Fleshflayer Ghoul": ("disease", 58, "Flay", "Gnaw", "Fleshrot"),
    "Patchwork Horror": ("brute", 58, "Hook Slam", "Cleave", "Frenzy"),
    "Vengeful Phantom": ("ghost", 58, "Vengeful Touch", "Phantom Strike", "Despair"),
    "Rockwing Gargoyle": ("stunner", 59, "Stone Claw", "Dive", "Stone Stare"),
    "Crimson Guardsman": ("tank", 59, "Crusader Strike", "Shield Bash", "Shield Wall"),
    "Crimson Conjuror": ("caster", 58, "Fireball", "Flamestrike", "Frost Nova", "fire"),
    "Crimson Initiate": ("healer", 58, "Smite", "Heal", "Holy Fire", "holy"),
    "Crimson Gallant": ("melee", 59, "Crusader Strike", "Holy Strike", "Retribution"),
    "Crimson Defender": ("tank", 59, "Shield Slam", "Revenge", "Devotion"),
    "Crimson Priest": ("healer", 58, "Holy Smite", "Greater Heal", "Holy Fire", "holy"),
    "Crimson Rifleman": ("ranged", 59, "Shoot", "Aimed Shot", "Marked"),
    "Crimson Monk": ("stunner", 59, "Open Palm", "Spinning Kick", "Pressure Point"),
    "Crimson Battle Mage": ("caster", 59, "Fireball", "Blast Wave", "Slow", "fire"),
    "Crimson Sorcerer": ("caster", 59, "Frostbolt", "Blizzard", "Frost Nova", "frost"),
    "Crimson Inquisitor": ("dotcaster", 59, "Searing Light", "Brand of the Heretic", "Accused", "holy"),
    # Stratholme, the Service Entrance
    "Ghoul Ravener": ("disease", 58, "Ravening Claw", "Tear", "Ghoul Rot"),
    "Mangled Cadaver": ("disease", 59, "Flail", "Bone Snap", "Cadaver Worms"),
    "Broken Cadaver": ("disease", 59, "Lurch", "Burst Open", "Rot Cloud"),
    "Plagued Crypt Crawler": ("poison", 59, "Bite", "Web", "Crypt Venom"),
    "Crypt Beast": ("poison", 58, "Rend", "Crypt Scarabs", "Venom Spit"),
    "Undead Scarab": ("beast", 58, "Nip", "Swarm", "Chitin Bite"),
    "Thuzadin Acolyte": ("healer", 59, "Shadow Bolt", "Dark Mending", "Shadow Word: Pain", "shadow"),
    "Thuzadin Shadowcaster": ("dotcaster", 59, "Shadow Bolt", "Curse of Weakness", "Piercing Shadow", "shadow",
                              "curse"),
    "Thuzadin Necromancer": ("dotcaster", 59, "Shadow Bolt", "Soul Tap", "Bone Shield", "shadow"),
    "Rockwing Screecher": ("caster", 59, "Screech", "Terrifying Screech", "Deafen", "shadow"),
    "Eye of Naxxramas": ("caster", 59, "Gaze", "Summon Rockwing", "Dark Vision", "shadow"),
    # Stratholme, Slaughter Square
    "Venom Belcher": ("poison", 59, "Slam", "Venom Spit", "Venom"),
    "Bile Spewer": ("disease", 59, "Smash", "Spew Bile", "Bile Rot"),
    "Bile Slime": ("disease", 59, "Ooze", "Engulf", "Bile Sickness"),
    "Mindless Undead": ("disease", 60, "Claw", "Grab", "Mindless Rot"),
    "Black Guard Sentry": ("tank", 60, "Unholy Strike", "Shield Bash", "Black Guard"),
    # Hearthglen, the town
    "Hearthglen Arbalest": ("ranged", 59, "Bolt", "Heavy Bolt", "Pinned"),
    "Hearthglen Cleric": ("healer", 59, "Smite", "Flash Heal", "Holy Fire", "holy"),
    "Hearthglen Field Medic": ("healer", 58, "Shield Bash", "Bind Wounds", "Cauterise", "fire"),
    "Hearthglen Mastiff": ("beast", 58, "Bite", "Maul", "Hamstring"),
    "Hearthglen Templar": ("tank", 59, "Crusader Strike", "Hammer of Justice", "Devotion"),
    "Hearthglen Zealot": ("stunner", 59, "Fervent Blow", "Fanatic's Strike", "Zealous Bash"),
    # Hearthglen, Mardenholde Keep
    "Mardenholde Battle Priest": ("healer", 60, "Holy Smite", "Battle Prayer", "Holy Fire", "holy"),
    "Mardenholde Crossbowman": ("ranged", 60, "Bolt", "Volley Shot", "Pinned"),
    "Mardenholde Halberdier": ("brute", 60, "Halberd Thrust", "Sweep", "Hold the Line"),
    "Mardenholde Knight": ("tank", 60, "Crusader Strike", "Shield Slam", "Knight's Oath"),
}


# ============================================================================================== the boss kits
def kits():
    k = {n: trash(*spec) for n, spec in TRASH.items()}

    # ---- Scholomance, upper
    k["Kirtonos the Herald"] = boss_kit(         # a gargoyle on the wing: dives on the back line, silences
        57, "shadow", "Swoop", "Wing Flap", "Dive", "Shadow Bolt Volley",
        hit_with("Disarming Shriek", int(B(57) * 0.8), {"spell_power": -60, "attack_power": -60}, school="shadow"),
        "The Herald Takes Wing",
        extra=[dmg("Pierce Armour", int(B(57) * 0.9), cooldown=5, rider={"effect": "debuff", "duration": 3,
                                                                          "stat_mods": {"armor": -300}})],
        signature=dmg("Swoop From Above", int(B(57) * 2.0), cooldown=6, school="shadow"))
    k["Jandice Barov"] = boss_kit(               # splits into illusions: find the real one
        57, "shadow", "Curse of Blood", "Banish", "Shadow Lash", "Mirror Images",
        summon("Illusion of Jandice Barov", "Spectral Researcher", 4, 2, 4), "Not Here, Not There",
        extra=[dot("Curse of the Barovs", int(B(57) * 0.34), 5, 4, school="shadow", dispel_type="curse")],
        signature=dmg("Every Mirror Strikes", int(B(57) * 1.2), cooldown=6, school="shadow", is_aoe=True))
    k["Rattlegore"] = boss_kit(                  # a bone giant: knocks the tank flat
        58, "physical", "Bone Fist", "Knock Away", "Strike", "War Stomp",
        stun_hit("Grave Slam", int(B(58) * 0.7), cooldown=6), "Bones Stack Higher", aoe=True,
        extra=[shell("Bone Armour", 6, 3, int(B(58) * 1.4))],
        signature=dmg("Crushing Blow", int(B(58) * 2.2), cooldown=6))
    k["Marduk Blackpool"] = boss_kit(            # a death knight: shadow and fear
        58, "shadow", "Unholy Blade", "Shadow Bolt Volley", "Defile", "Death and Decay",
        hit_with("Fearsome Presence", int(B(58) * 0.7), {"attack_power": -80, "spell_power": -50}, school="shadow",
                 is_aoe=True, cooldown=6), "Runeblade Hungers",
        signature=dmg("Death Coil", int(B(58) * 2.0), cooldown=6, school="shadow"))
    k["Vectus"] = boss_kit(                      # a student with a flamethrower: fire on the floor
        58, "fire", "Flamethrower", "Blast Wave", "Fire Shield", "Fire on the Floor",
        dot("Burning Robes", int(B(58) * 0.34), 5, 4, school="fire", dispel_type="magic", is_aoe=True),
        "Top of the Class", aoe=False,
        signature=dmg("Firestorm", int(B(58) * 1.3), cooldown=6, school="fire", is_aoe=True))
    k["Ras Frostwhisper"] = boss_kit(            # a lich: freezes, then shatters
        58, "frost", "Frostbolt", "Chill Nova", "Frostbolt Volley", "Ice Armour",
        stun_hit("Freeze", int(B(58) * 0.6), cooldown=6, school="frost"), "Winter's Grip",
        extra=[shell("Ice Armour", 6, 3, int(B(58) * 1.2), school="frost")],
        signature=[dmg("Shatter", int(B(58) * 2.0), cooldown=6, school="frost"), last_gasp("Frozen Tomb", 58,
                                                                                       "frost")])
    # ---- Scholomance, the Lower Halls
    k["Instructor Malicia"] = boss_kit(          # calls her students in waves
        59, "shadow", "Corruption", "Call to the Class", "Shadow Bolt", "Shadow Volley",
        summon("Class Is in Session", "Scholomance Student", 4, 2, 5), "Detention",
        extra=[heal("Lesson Learned", int(B(59) * 1.1), cooldown=6, school="shadow")],
        signature=dmg("Final Examination", int(B(59) * 1.2), cooldown=6, school="shadow", is_aoe=True))
    k["Doctor Theolen Krastinov"] = boss_kit(    # the butcher: bleeds and rends
        59, "physical", "Butcher's Hook", "Rend Flesh", "Cleaver", "Backhand",
        dot("Rend", int(B(59) * 0.4), 5, 4, dispel_type="bleed"), "Frenzied Butcher", aoe=False, phase_pct=60,
        signature=dmg("Hack Apart", int(B(59) * 2.2), cooldown=6))
    k["Lorekeeper Polkelt"] = boss_kit(          # plague and corrosive bile: cleanse
        59, "nature", "Volatile Infection", "Corrosive Acid", "Noxious Catalyst", "Bile Splash",
        dot("Volatile Infection", int(B(59) * 0.4), 5, 4, school="nature", dispel_type="disease", is_aoe=True),
        "Read the Last Page",
        signature=dmg("Catalyst Erupts", int(B(59) * 1.3), cooldown=6, school="nature", is_aoe=True))
    k["The Ravenian"] = boss_kit(                # cleaves the whole front line
        59, "physical", "Trample", "Sunder Armour", "Cleave", "Knock Away",
        hit_with("Sundering Blow", int(B(59) * 0.9), {"armor": -400}), "The Ravenian Feeds", phase_pct=60,
        signature=dmg("Great Cleave", int(B(59) * 1.2), cooldown=4, is_aoe=True))
    k["Lord Alexei Barov"] = boss_kit(           # he rots the front line
        60, "shadow", "Unholy Aura", "Immolate", "Veil of Shadow", "Rot of the Barovs",
        dot("Barov Rot", int(B(60) * 0.4), 5, 4, school="shadow", dispel_type="disease", is_aoe=True),
        "The Family Endures",
        signature=dmg("Unholy Nova", int(B(60) * 1.3), cooldown=6, school="shadow", is_aoe=True))
    k["Lady Illucia Barov"] = boss_kit(          # she charms and fears
        60, "shadow", "Shadow Bolt", "Curse of Agony", "Dominate", "Silence",
        hit_with("Dominate Mind", int(B(60) * 0.9), {"attack_power": -100, "spell_power": -80}, school="shadow"),
        "Lady of the House",
        extra=[stun_hit("Fear", int(B(60) * 0.5), cooldown=6, school="shadow")],
        signature=dmg("Shadow Shock", int(B(60) * 2.0), cooldown=6, school="shadow"))
    k["Darkmaster Gandling"] = boss_kit(         # sends you to a cell and fights you alone
        60, "arcane", "Arcane Missiles", "Curse of the Darkmaster", "Shadow Shield", "Arcane Barrage",
        stun_hit("Shadow Portal", int(B(60) * 0.8), cooldown=5, school="shadow"), "The Headmaster's Wrath",
        extra=[shell("Shadow Shield", 6, 3, int(B(60) * 1.3), school="shadow"),
               dot("Curse of the Darkmaster", int(B(60) * 0.36), 5, 4, school="shadow", dispel_type="curse")],
        signature=[dmg("Expelled", int(B(60) * 2.2), cooldown=6, school="arcane"), last_gasp("School's Out", 60,
                                                                                        "arcane")])
    # ---- Stratholme, the living side
    k["Skul"] = boss_kit(                        # the gate guard nobody buried: frost and arcane
        57, "frost", "Frostbolt", "Arcane Bolt", "Frost Nova", "Blizzard",
        stun_hit("Frost Nova", int(B(57) * 0.5), cooldown=6, school="frost"), "Still on Duty",
        signature=dmg("Frost Lance", int(B(57) * 2.0), cooldown=6, school="frost"))
    k["Hearthsinger Forresten"] = boss_kit(      # a bard's ghost: his song takes the party's nerve
        57, "shadow", "Dirge", "Enchanting Lullaby", "Demoralising Shout", "Song of the Dead",
        hit_with("Enchanting Lullaby", int(B(57) * 0.7), {"haste": -25, "attack_power": -60}, school="shadow",
                 is_aoe=True, cooldown=6), "The Last Verse",
        signature=dmg("Shriek of the Hearth", int(B(57) * 1.3), cooldown=6, school="shadow", is_aoe=True))
    k["The Unforgiven"] = boss_kit(              # a death knight's shade with his court round him
        58, "frost", "Frost Strike", "Frost Shock", "Psychic Scream", "Frost Nova",
        summon("The Court Rises", "Vengeful Phantom", 4, 2, 4), "Unforgiving",
        extra=[stun_hit("Psychic Scream", int(B(58) * 0.5), cooldown=6, school="shadow")],
        signature=dmg("Cold-Hearted Strike", int(B(58) * 2.0), cooldown=6, school="frost"))
    k["Timmy the Cruel"] = boss_kit(             # the ghoul that runs out of the side street
        58, "physical", "Ravenous Claw", "Gnaw", "Ravenous Claw Flurry", "Pounce",
        dot("Ravenous Bite", int(B(58) * 0.4), 5, 4, dispel_type="disease"), "Cruel and Hungry", aoe=False,
        phase_pct=70,
        signature=dmg("Feeding Frenzy", int(B(58) * 2.2), cooldown=6))
    k["Cannon Master Willey"] = boss_kit(        # the Bastion's cannons and the riflemen who load them
        59, "fire", "Shoot", "Knock Away", "Pummel", "Cannon Shot",
        summon("Load the Cannons", "Crimson Rifleman", 4, 2, 4), "Fire at Will",
        signature=dmg("Cannon Barrage", int(B(59) * 1.3), cooldown=6, school="fire", is_aoe=True))
    k["Archivist Galford"] = boss_kit(           # burns the archive rather than let you read it
        59, "fire", "Fireball", "Burning Winds", "Pyroblast", "Fire Nova",
        dot("Burning Pages", int(B(59) * 0.36), 5, 4, school="fire", dispel_type="magic", is_aoe=True),
        "Burn the Records", aoe=False,
        signature=[dmg("Pyroblast", int(B(59) * 2.0), cooldown=6, school="fire"),
                   last_gasp("The Archive Burns", 59, "fire")])
    k["Grand Crusader Dathrohan"] = boss_kit(    # at 40% the Grand Crusader is Balnazzar
        59, "holy", "Crusader Strike", "Holy Strike", "Mind Blast", "Crusader's Hammer",
        stun_hit("Hammer of Justice", int(B(59) * 0.6), cooldown=6, school="holy"), "Balnazzar Revealed",
        phase_pct=70,
        extra=[dict(dmg("Shadow Shock", int(B(59) * 1.6), cooldown=4, school="shadow"), hp_below=0.4),
               dict(dot("Psychic Scream of the Dreadlord", int(B(59) * 0.4), 5, 4, school="shadow",
                        dispel_type="magic", is_aoe=True), hp_below=0.4)],
        signature=dmg("Judgement of the Crusade", int(B(59) * 2.0), cooldown=6, school="holy"))
    # ---- Stratholme, the Service Entrance
    k["Magistrate Barthilas"] = boss_kit(        # the city's magistrate, still keeping the key
        58, "shadow", "Draining Blow", "Crowd Pummel", "Mighty Blow", "Furious Anger",
        hit_with("Draining Blow", int(B(58) * 0.9), {"stamina": -40}, school="shadow"), "The Court Is Adjourned",
        phase_pct=60,
        signature=dmg("Mighty Blow", int(B(58) * 2.2), cooldown=6))
    k["Stonespine"] = boss_kit(                  # a gargoyle that walks the street between the ziggurats
        58, "physical", "Stone Claw", "Rend", "Stone Skin", "Wing Buffet",
        shell("Stoneskin", 6, 3, int(B(58) * 1.4)), "Stone Turns to Fury", aoe=True,
        signature=stun_hit("Crushing Dive", int(B(58) * 1.6), cooldown=6))
    k["Nerub'enkan"] = boss_kit(                 # crypt lord: scarabs and webs
        59, "nature", "Impale", "Crypt Scarabs", "Encasing Webs", "Locust Swarm",
        summon("Crypt Scarabs", "Undead Scarab", 4, 2, 5), "The Crypt Lord Burrows",
        extra=[stun_hit("Encasing Webs", int(B(59) * 0.5), cooldown=6, school="nature")],
        signature=dmg("Impale", int(B(59) * 2.0), cooldown=6))
    k["Baroness Anastari"] = boss_kit(           # banshee: she possesses one of you
        59, "shadow", "Banshee Wail", "Banshee Curse", "Silence", "Wail of the Banshee",
        hit_with("Possess", int(B(59) * 0.9), {"attack_power": -120, "spell_power": -100}, school="shadow",
                 duration=2),
        "The Baroness Screams",
        extra=[dot("Banshee Curse", int(B(59) * 0.36), 5, 4, school="shadow", dispel_type="curse")],
        signature=dmg("Wail of the Lost", int(B(59) * 1.3), cooldown=6, school="shadow", is_aoe=True))
    k["Maleki the Pallid"] = boss_kit(           # lich: frost, and drains your mana
        59, "frost", "Frostbolt", "Drain Life", "Ice Tomb", "Frost Nova",
        hit_with("Drain Mana", int(B(59) * 0.8), {"mp5": -15, "intellect": -50}, school="frost"), "Pallid Fury",
        extra=[stun_hit("Ice Tomb", int(B(59) * 0.6), cooldown=6, school="frost"),
               heal("Drain Life", int(B(59) * 1.1), cooldown=6, school="shadow")],
        signature=dmg("Frostbolt Barrage", int(B(59) * 2.0), cooldown=6, school="frost"))
    # ---- Stratholme, Slaughter Square
    k["Ramstein the Gorger"] = boss_kit(         # the abomination the square is kept for
        60, "physical", "Trample", "Knockout", "Gorge", "Stomp",
        stun_hit("Knockout", int(B(60) * 0.7), cooldown=6), "Still Hungry", phase_pct=60,
        signature=dmg("Gorging Trample", int(B(60) * 1.3), cooldown=6, is_aoe=True))
    k["Baron Rivendare"] = boss_kit(             # the Baron, and his deathcharger
        60, "shadow", "Runeblade Strike", "Mortal Strike", "Unholy Aura", "Shadow Bolt",
        dot("Unholy Aura", int(B(60) * 0.3), 5, 4, school="shadow", is_aoe=True), "Rivendare's Fury",
        extra=[summon("Raise the Dead", "Mindless Undead", 4, 2, 4),
               hit_with("Mortal Strike", int(B(60) * 1.0), {"healing_power": -120})],
        signature=[dmg("Death Pact", int(B(60) * 2.2), cooldown=6, school="shadow"),
                   last_gasp("The Baron's Last Charge", 60, "shadow")])
    # ---- Hearthglen, the town
    k["High Protector Tarsen"] = boss_kit(       # holds the gate with his dogs
        58, "physical", "Gate Mace", "Shield Bash", "Hold the Gate", "Hounds on the Gate",
        summon("Loose the Mastiffs", "Hearthglen Mastiff", 4, 2, 4), "None Shall Pass",
        extra=[hit_with("Shield Wall", int(B(58) * 0.8), {"armor": 500}, duration=4, on="buff")],
        signature=stun_hit("Crushing Shield", int(B(58) * 1.6), cooldown=6))
    k["Huntsman Radley"] = boss_kit(             # the kennels' master: arrows, traps and the pack
        58, "physical", "Shoot", "Multi-Shot", "Aimed Shot", "Volley",
        hit_with("Freezing Trap", int(B(58) * 0.6), {"haste": -30}, duration=2, school="frost"),
        "The Hunt Is On",
        extra=[summon("Release the Kennel", "Hearthglen Mastiff", 4, 2, 4)],
        signature=dmg("Killing Shot", int(B(58) * 2.0), cooldown=6))
    k["Chirurgeon Maeve Ostrowski"] = boss_kit(  # the Infirmary's surgeon and her orderlies: she mends them
        58, "physical", "Scalpel", "Bonesaw", "Amputate", "Ether Cloud",
        heal("Stitch Them Up", int(B(58) * 1.2), cooldown=5, school="holy"), "Triage",
        extra=[summon("Orderlies!", "Hearthglen Field Medic", 4, 2, 4),
               dot("Open Wound", int(B(58) * 0.36), 5, 4, dispel_type="bleed")],
        signature=dmg("Amputation", int(B(58) * 2.2), cooldown=6))
    k["High Clerist Hendrick"] = boss_kit(       # the Chapel of the Flame: holy fire and judgement
        59, "holy", "Holy Smite", "Holy Fire", "Judgement of the Flame", "Consecration",
        dot("Holy Fire", int(B(59) * 0.4), 5, 4, school="holy", dispel_type="magic"), "The Flame Purifies",
        extra=[heal("Greater Heal", int(B(59) * 1.2), cooldown=6)],
        signature=dmg("Purifying Flame", int(B(59) * 1.3), cooldown=6, school="holy", is_aoe=True))
    k["High Protector Lorik"] = boss_kit(        # the Barbican: the town's last wall
        59, "physical", "Greatsword", "Sweeping Strikes", "Shield Slam", "Whirlwind",
        hit_with("Intimidating Shout", int(B(59) * 0.6), {"attack_power": -80, "spell_power": -50}, is_aoe=True,
                 duration=2, cooldown=6), "The Barbican Holds", phase_pct=60,
        signature=dmg("Barbican Bladestorm", int(B(59) * 1.2), cooldown=4, is_aoe=True))
    # ---- Hearthglen, Mardenholde Keep
    k["Scarlet Commander Marjhan"] = boss_kit(   # the Muster Yard's battle-mage: fire, and shields on her people
        59, "fire", "Fireball", "Flame Wave", "Pyroblast", "Flamestrike",
        shell("Commander's Ward", 6, 3, int(B(59) * 1.2), school="fire"), "Muster the Yard",
        extra=[summon("To Arms!", "Mardenholde Knight", 5, 1, 3)],
        signature=dmg("Pyroblast", int(B(59) * 2.0), cooldown=6, school="fire"))
    k["Armsmaster Grell"] = boss_kit(            # the Armoury: a new weapon every turn
        59, "physical", "Warhammer", "Spear Thrust", "Axe Chop", "Hail of Daggers",
        hit_with("Disarm", int(B(59) * 0.9), {"attack_power": -120}, duration=2), "Every Weapon in the Rack",
        opener_mech={"reflect_pct": 15, "reflect_school": "physical", "reflect_melee_only": True},
        signature=dmg("The Armsmaster's Blow", int(B(59) * 2.2), cooldown=6))
    k["Drillmaster Osric Pell"] = boss_kit(      # the Barracks: his recruits come in waves
        60, "physical", "Drill Cane", "Shield Charge", "Knee to the Gut", "Squad Charge",
        summon("Fall In!", "Mardenholde Halberdier", 4, 2, 4), "Double Time",
        extra=[stun_hit("Knee to the Gut", int(B(60) * 0.6), cooldown=6)],
        signature=dmg("Charge the Line", int(B(60) * 1.2), cooldown=6, is_aoe=True))
    k["High General Abbendis"] = boss_kit(       # the Great Hall: the Crusade's general, holy steel
        60, "holy", "Crusader Strike", "Divine Storm", "Hammer of Wrath", "Consecration",
        stun_hit("Hammer of Justice", int(B(60) * 0.6), cooldown=6, school="holy"), "For the Crusade",
        extra=[heal("Lay on Hands", int(B(60) * 2.0), cooldown=99, school="holy")],
        signature=dmg("Divine Storm", int(B(60) * 1.3), cooldown=6, school="holy", is_aoe=True))
    k["Grand Crusader Victor Hale"] = boss_kit(  # the Tower Top: the man himself
        60, "fire", "Flamebrand", "Crusader Strike", "Burning Blade", "Pillar of Flame",
        dot("Brand of the Heretic", int(B(60) * 0.4), 5, 4, school="fire", dispel_type="magic"),
        "Hale Will Not Fall", phase_pct=60,
        extra=[stun_hit("Hammer of the Crusade", int(B(60) * 0.7), cooldown=6, school="holy"),
               heal("Divine Protection", int(B(60) * 1.0), cooldown=99, school="holy")],
        signature=[dmg("Burning Crusade", int(B(60) * 2.2), cooldown=6, school="fire"),
                   last_gasp("Nobody Leaves Hearthglen", 60, "fire", mult=1.8)])
    return k


# ============================================================================================== the loot
W = lambda t: ("w", t)   # noqa: E731
A = lambda t: ("a", t)   # noqa: E731
#: (name, slot, suffix, armour or weapon type, template) per boss, in run order. Item level = boss level + 3. No
#: piece sits in its dungeon's token slot: no helms in Scholomance, no chests in Stratholme, no boots in Hearthglen.
POOLS = {
    # ---------------------------------------------------------------- Scholomance (no helms: the head token)
    "Kirtonos the Herald": [
        ("Herald's Wingblade", "main_hand", "of the Assassin", W("sword_1h"), "agi_physical"),
        ("Balcony-Perch Mantle", "shoulder", "of Shadow Wrath", A("cloth"), "int_caster"),
        ("Talon-Scored Bracers", "wrist", "of the Gorilla", A("plate"), "str_int_hybrid")],
    "Jandice Barov": [
        ("Jandice's Mirror Staff", "main_hand", "of the Archmage", W("staff"), "int_caster"),
        ("Illusionist's Silk Leggings", "legs", "of the Prophet", A("cloth"), "spi_healer"),
        ("Barov Family Signet", "ring", "of the Falcon", None, "agi_int_hybrid")],
    "Rattlegore": [
        ("Rattlegore's Femur", "main_hand", "of the Bear", W("mace_2h"), "str_physical"),
        ("Ossuary Pit Girdle", "waist", "of the Champion", A("plate"), "str_physical"),
        ("Bone-Lacquered Gauntlets", "hands", "of the Bandit", A("leather"), "agi_physical")],
    "Marduk Blackpool": [
        ("Blackpool's Runed Cleaver", "main_hand", "of the Gladiator", W("axe_1h"), "str_physical"),
        ("Death-Knight's Viewing Cloak", "back", "of the Marksman", A("cloth"), "agi_physical"),
        ("Grave-Chain Leggings", "legs", "of the Hunt", A("mail"), "agi_int_hybrid")],
    "Vectus": [
        ("Vectus's Flamethrower", "ranged", "of Fiery Wrath", W("wand"), "int_caster"),
        ("Singed Laboratory Gloves", "hands", "of the Physician", A("leather"), "spi_healer"),
        ("Top Student's Sash", "waist", "of the Invoker", A("cloth"), "int_caster")],
    "Ras Frostwhisper": [
        ("Frostwhisper's Embrace", "main_hand", "of Frozen Wrath", W("staff"), "int_caster"),
        ("Laboratory Chill Mantle", "shoulder", "of the Elder", A("mail"), "spi_healer"),
        ("Frozen Phylactery Shard", "trinket", "of the Mind's Eye", None, "int_caster")],
    "Instructor Malicia": [
        ("Malicia's Pointer", "off_hand", "of the Sorcerer", W("tome"), "int_caster"),
        ("Coven-Mistress Bracers", "wrist", "of the Physician", A("cloth"), "spi_healer"),
        ("Detention Hall Leggings", "legs", "of the Bandit", A("leather"), "agi_physical")],
    "Doctor Theolen Krastinov": [
        ("The Doctor's Bonesaw", "main_hand", "of the Assassin", W("dagger"), "agi_physical"),
        ("Butcher's Apron Belt", "waist", "of the Soldier", A("mail"), "agi_physical"),
        ("Shadow Vault Gauntlets", "hands", "of the Champion", A("plate"), "str_physical")],
    "Lorekeeper Polkelt": [
        ("Polkelt's Catalogue", "off_hand", "of the Prophet", W("tome"), "spi_healer"),
        ("Bile-Proof Wristwraps", "wrist", "of the Hunt", A("mail"), "agi_int_hybrid"),
        ("Hall of the Damned Mantle", "shoulder", "of the Wellspring", A("leather"), "spi_healer")],
    "The Ravenian": [
        ("The Ravenian's Cleaver", "main_hand", "of the Breaker", W("axe_2h"), "str_physical"),
        ("Vault-Trampled Spaulders", "shoulder", "of the Champion", A("plate"), "str_physical"),
        ("Ravenous Fang Pendant", "neck", "of the Monkey", None, "agi_physical")],
    # the Barovs' one fight: three of nine drop
    "Lord Alexei Barov": [
        ("Barov Heirloom Longsword", "main_hand", "of the Gladiator", W("sword_2h"), "str_physical"),
        ("Lady Illucia's Fan", "off_hand", "of the Invoker", W("tome"), "int_caster"),
        ("Alexei's Signet Dagger", "main_hand", "of the Falcon", W("dagger"), "agi_int_hybrid"),
        ("Family Vault Leggings", "legs", "of the Champion", A("plate"), "str_physical"),
        ("Barov Velvet Gloves", "hands", "of Shadow Wrath", A("cloth"), "int_caster"),
        ("Heir's Riding Boots", "feet", "of the Assassin", A("leather"), "agi_physical"),
        ("Undying Family Mail", "chest", "of the Elder", A("mail"), "spi_healer"),
        ("Ring of the Barov Line", "ring", "of the Gorilla", None, "str_int_hybrid"),
        ("The Family Reliquary", "trinket", "of the Prophet", None, "spi_healer")],
    "Darkmaster Gandling": [
        ("Headmaster's Charge", "main_hand", "of the Invoker", W("staff"), "int_caster"),
        ("Darkmaster's Robe of Office", "chest", "of the Prophet", A("cloth"), "spi_healer"),
        ("Gandling's Expulsion Shield", "off_hand", "of the Bulwark", W("shield"), "str_physical")],
    # ---------------------------------------------------------------- Stratholme, the living side (no chests)
    "Skul": [
        ("Skul's Gate-Guard Staff", "main_hand", "of Frozen Wrath", W("staff"), "int_caster"),
        ("Unburied Gatekeeper's Boots", "feet", "of the Champion", A("plate"), "str_physical"),
        ("Rime-Bound Cord", "waist", "of the Hunt", A("mail"), "agi_int_hybrid")],
    "Hearthsinger Forresten": [
        ("Forresten's Lute-Blade", "main_hand", "of the Falcon", W("sword_1h"), "agi_int_hybrid"),
        ("Hearthsinger's Cloak", "back", "of the Owl", A("cloth"), "spi_healer"),
        ("Songweaver Leggings", "legs", "of the Archmage", A("cloth"), "int_caster")],
    "The Unforgiven": [
        ("Unforgiven Runeblade", "main_hand", "of the Breaker", W("sword_2h"), "str_physical"),
        ("Courtly Shade Gauntlets", "hands", "of the Marksman", A("mail"), "agi_physical"),
        ("Ring of the Unforgiving", "ring", "of the Physician", None, "spi_healer")],
    "Timmy the Cruel": [
        ("Timmy's Gnawed Club", "main_hand", "of the Bear", W("mace_1h"), "str_physical"),
        ("Side-Street Leggings", "legs", "of the Bandit", A("leather"), "agi_physical"),
        ("Crusaders' Square Bracers", "wrist", "of the Wellspring", A("leather"), "spi_healer")],
    "Cannon Master Willey": [
        ("Willey's Bastion Blunderbuss", "ranged", "of the Marksman", W("gun"), "agi_physical"),
        ("Powder-Burned Gloves", "hands", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("Cannoneer's Fuse", "trinket", "of the Champion", None, "agi_physical")],
    "Archivist Galford": [
        ("Galford's Burning Ledger", "off_hand", "of Fiery Wrath", W("tome"), "int_caster"),
        ("Archive-Ash Mantle", "shoulder", "of the Physician", A("cloth"), "spi_healer"),
        ("Scribe's Ink-Stained Belt", "waist", "of the Falcon", A("leather"), "agi_int_hybrid")],
    "Grand Crusader Dathrohan": [
        ("Dathrohan's Crusader Blade", "main_hand", "of the Gladiator", W("sword_2h"), "str_physical"),
        ("Dreadlord's Veil", "back", "of Shadow Wrath", A("cloth"), "int_caster"),
        ("Hall of High Command Greaves", "legs", "of the Restorer", A("plate"), "spi_healer")],
    # ---------------------------------------------------------------- Stratholme, the Scourge's side (no chests)
    "Magistrate Barthilas": [
        ("Magistrate's Gavel", "main_hand", "of the Restorer", W("mace_1h"), "spi_healer"),
        ("Elders' Square Sabatons", "feet", "of the Soldier", A("plate"), "str_physical"),
        ("Keeper of the Key's Wristguards", "wrist", "of the Bandit", A("leather"), "agi_physical")],
    "Stonespine": [
        ("Stonespine Claw", "main_hand", "of the Monkey", W("fist_weapon"), "agi_physical"),
        ("Gauntlet-Stone Pauldrons", "shoulder", "of the Hunt", A("mail"), "agi_int_hybrid"),
        ("Gargoyle-Hide Cloak", "back", "of the Champion", A("cloth"), "str_physical")],
    "Nerub'enkan": [
        ("Crypt Lord's Carapace Shield", "off_hand", "of the Bulwark", W("shield"), "str_physical"),
        ("Scarab-Shell Leggings", "legs", "of the Marksman", A("mail"), "agi_physical"),
        ("Encasing Web Wraps", "hands", "of the Physician", A("cloth"), "spi_healer")],
    "Baroness Anastari": [
        ("Anastari's Wail", "ranged", "of Shadow Wrath", W("wand"), "int_caster"),
        ("Banshee's Burial Slippers", "feet", "of the Archmage", A("cloth"), "int_caster"),
        ("Possessed Locket", "neck", "of the Wellspring", None, "spi_healer")],
    "Maleki the Pallid": [
        ("Pallid Frostcaller", "main_hand", "of the Sorcerer", W("staff"), "int_caster"),
        ("Ziggurat Frost-Mail Belt", "waist", "of the Elder", A("mail"), "spi_healer"),
        ("Lich's Drained Bracers", "wrist", "of the Gorilla", A("plate"), "str_int_hybrid")],
    "Ramstein the Gorger": [
        ("Ramstein's Meathook", "main_hand", "of the Breaker", W("polearm"), "str_physical"),
        ("Slaughter Square Gauntlets", "hands", "of the Assassin", A("leather"), "agi_physical"),
        ("Gorger's Stitched Girdle", "waist", "of the Champion", A("plate"), "str_physical")],
    "Baron Rivendare": [
        ("Runeblade of Baron Rivendare", "main_hand", "of the Vanquisher", W("sword_2h"), "str_physical"),
        ("Deathcharger's Reins", "trinket", "of the Falcon", None, "agi_int_hybrid"),
        ("The Baron's Unholy Mantle", "shoulder", "of the Invoker", A("cloth"), "int_caster")],
    # ---------------------------------------------------------------- Hearthglen (no boots: the feet token)
    "High Protector Tarsen": [
        ("Gate of Hearthglen Shield", "off_hand", "of the Defender", W("shield"), "str_physical"),
        ("Tarsen's Mastiff Leash", "waist", "of the Hunt", A("mail"), "agi_int_hybrid"),
        ("Tarsen's Gate-Warden Bracers", "wrist", "of the Physician", A("plate"), "spi_healer")],
    "Huntsman Radley": [
        ("Radley's Hunting Crossbow", "ranged", "of the Sharpshooter", W("crossbow"), "agi_physical"),
        ("Kennel-Master's Jerkin", "chest", "of the Bandit", A("leather"), "agi_physical"),
        ("Houndstooth Gloves", "hands", "of the Falcon", A("mail"), "agi_int_hybrid")],
    "Chirurgeon Maeve Ostrowski": [
        ("Chirurgeon's Lancet", "main_hand", "of the Restorer", W("dagger"), "spi_healer"),
        ("Infirmary Surgical Gown", "chest", "of the Prophet", A("cloth"), "spi_healer"),
        ("Bloodied Orderly's Gloves", "hands", "of the Champion", A("leather"), "str_physical")],
    "High Clerist Hendrick": [
        ("Hendrick's Flame Censer", "main_hand", "of Holy Wrath", W("mace_1h"), "int_caster"),
        ("Chapel of the Flame Vestments", "chest", "of the Elder", A("mail"), "spi_healer"),
        ("Clerist's Holy Signet", "ring", "of the Owl", None, "spi_healer")],
    "High Protector Lorik": [
        ("Lorik's Barbican Greatsword", "main_hand", "of the Breaker", W("sword_2h"), "str_physical"),
        ("Barbican Warplate Legguards", "legs", "of the Defender", A("plate"), "str_physical"),
        ("Protector's Crimson Cloak", "back", "of the Assassin", A("cloth"), "agi_physical")],
    "Scarlet Commander Marjhan": [
        ("Marjhan's Muster Rod", "ranged", "of Fiery Wrath", W("wand"), "int_caster"),
        ("Muster Yard Mantle", "shoulder", "of the Wellspring", A("leather"), "spi_healer"),
        ("Commander's Ward-Ring", "ring", "of the Gorilla", None, "str_int_hybrid")],
    "Armsmaster Grell": [
        ("Grell's Armoury Polearm", "main_hand", "of the Vanquisher", W("polearm"), "str_physical"),
        ("Rack-Polished Wristguards", "wrist", "of the Marksman", A("mail"), "agi_physical"),
        ("Armsmaster's Whetstone", "trinket", "of the Champion", None, "str_physical")],
    "Drillmaster Osric Pell": [
        ("Pell's Drill Halberd", "main_hand", "of the Gladiator", W("axe_2h"), "str_physical"),
        ("Barracks Mail Hauberk", "chest", "of the Hunt", A("mail"), "agi_int_hybrid"),
        ("Parade Sash of the Keep", "waist", "of the Archmage", A("cloth"), "int_caster")],
    "High General Abbendis": [
        ("Abbendis's Holy Warhammer", "main_hand", "of the Restorer", W("mace_2h"), "spi_healer"),
        ("General's Great Hall Legplates", "legs", "of the Gorilla", A("plate"), "str_int_hybrid"),
        ("Abbendis's Crusader Bow", "ranged", "of the Marksman", W("bow"), "agi_physical")],
    "Grand Crusader Victor Hale": [
        ("Hale's Flamebrand", "main_hand", "of the Gladiator", W("sword_1h"), "str_physical"),
        ("Tower Top Battle Robes", "chest", "of the Invoker", A("cloth"), "int_caster"),
        ("Grand Crusader's Shoulderguards", "shoulder", "of the Bandit", A("leather"), "agi_physical")],
}

#: trinkets that do something, sized for item level 60 to 63
PROCS = {
    "Frozen Phylactery Shard": {
        "trigger": "on_damage_cast", "chance": 8, "icd": 5,
        "apply_effect": {"effect_id": "frozen_phylactery_shard", "name": "Cold Clarity", "effect_type": "buff",
                         "duration": 3, "stat_mods": {"spell_power": 40}, "on_target": False},
        "describe": "Your damaging spells have a chance to grant 40 spell power for 3 turns."},
    "The Family Reliquary": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "barov_family_reliquary", "name": "The Family Endures", "effect_type": "buff",
                         "duration": 3, "stat_mods": {"healing_power": 56}, "on_target": False},
        "describe": "Your healing spells have a chance to grant 56 healing power for 3 turns."},
    "Cannoneer's Fuse": {
        "trigger": "on_hit", "chance": 8, "icd": 5,
        "apply_effect": {"effect_id": "cannoneers_fuse", "name": "Lit Fuse", "effect_type": "buff",
                         "duration": 3, "stat_mods": {"attack_power": 80}, "on_target": False},
        "describe": "Your attacks have a chance to grant 80 attack power for 3 turns."},
    "Deathcharger's Reins": {
        "trigger": "on_hit", "chance": 8, "icd": 5,
        "apply_effect": {"effect_id": "deathchargers_reins", "name": "Unholy Charge", "effect_type": "buff",
                         "duration": 3, "stat_mods": {"haste": 10}, "on_target": False},
        "describe": "Your attacks have a chance to grant 10% haste for 3 turns."},
    "Armsmaster's Whetstone": {
        "trigger": "on_damage_taken", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "armsmasters_whetstone", "name": "Honed Edge", "effect_type": "buff",
                         "duration": 3, "stat_mods": {"attack_power": 70, "armor": 300}, "on_target": False},
        "describe": "When you are hit, you have a chance to gain 70 attack power and 300 armour for 3 turns."},
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
            d["item_id"] = "pld_" + kit_slug(name)
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
def _floors(r):
    return r[5] if isinstance(r[5], tuple) else (r[5],)


def check(k, loot):
    bad = []
    if set(k) != set(ROSTER):
        bad.append(f"kits and roster differ: {sorted(set(k) ^ set(ROSTER))}")
    want_bosses = BOSSES - set(PACK_MEMBER)
    if set(POOLS) != want_bosses:
        bad.append(f"loot pools and bosses differ: {sorted(set(POOLS) ^ want_bosses)}")
    token_slot = {b: d[1] for d in DUNGEONS.values() for b in d[2]}
    for b, items in loot.items():
        want = 9 if b in PACK_MEMBER.values() else 3
        if len(items) != want:
            bad.append(f"{b}: {len(items)} items, wanted {want}")
        for i in items:
            if i["item_level"] != ROSTER[b][2] + 3:
                bad.append(f"{i['name']}: item level {i['item_level']} on a level {ROSTER[b][2]} boss")
            if i["slot"] == "trinket" and not i.get("proc"):
                bad.append(f"{i['name']} is a trinket that does nothing")
            if i["slot"] == token_slot.get(b) and b not in PACK_MEMBER.values():
                bad.append(f"{i['name']} is a {i['slot']} piece in the dungeon whose token that is")
    run = [b for d in DUNGEONS.values() for b in d[2]]
    if sorted(run) != sorted(want_bosses):
        bad.append(f"the token runs and the bosses differ: {sorted(set(run) ^ want_bosses)}")
    for floor, (_reg, (lo, hi), spec) in FLOORS.items():
        spawned = {m for p in spec["trash"] for (_x, _y, m, _l) in p}
        placed = {b[2] for b in spec["bosses"]} | {m[2] for ms in (spec.get("pack") or {}).values() for m in ms}
        ours = {n for n, r in ROSTER.items() if floor in _floors(r)}
        if not spawned <= ours:
            bad.append(f"{floor}: spawns creatures with no record: {sorted(spawned - ours)}")
        if placed != {n for n in ours if n in BOSSES}:
            bad.append(f"{floor}: bosses on the map differ from the roster: {sorted(placed ^ (ours & BOSSES))}")
        for p in spec["trash"]:
            for (_x, _y, m, lvl) in p:
                if m in ROSTER and not ROSTER[m][1] <= lvl <= ROSTER[m][2]:
                    bad.append(f"{floor}: {m} spawns at {lvl}, outside its {ROSTER[m][1]}-{ROSTER[m][2]}")
        for n in ours:
            if not (lo <= ROSTER[n][1] and ROSTER[n][2] <= hi) and len(_floors(ROSTER[n])) == 1:
                bad.append(f"{n} ({ROSTER[n][1]}-{ROSTER[n][2]}) sits outside {floor} {lo}-{hi}")
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
    from tools.build_plaguelands_quests import taken_names
    clash = sorted(set(names) & taken_names({LOOT.name}))
    if clash:
        bad.append(f"item names already in the game: {clash}")
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
    for floor, (region, _lv, _spec) in FLOORS.items():
        caves = enc["zones"].setdefault(region, {}).setdefault("caves", {})
        caves[floor] = {"name": floor, "creatures": {n: (0 if r[3] else 4) for n, r in ROSTER.items()
                                                     if floor in _floors(r)}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False) + ("\n" if newline else ""),
                          encoding="utf-8")
    print(f"  encounters.json: {len(FLOORS)} floors")

    raw = LEVELS.read_text(encoding="utf-8")
    lv = json.loads(raw)
    indent, newline = _detect_format(lv, raw)
    lv["zones"].update(ZONE_LEVELS)
    LEVELS.write_text(json.dumps(lv, indent=indent, ensure_ascii=False) + ("\n" if newline else ""), encoding="utf-8")
    print(f"  zone_levels.json: {len(ZONE_LEVELS)} floors")

    out = {"_notes": ("Boss loot for Scholomance, Stratholme (both halves) and Hearthglen (56-60). ONE item per kill "
                      "from the boss's three; the Barovs share nine and drop three. item_level = boss level + 3. "
                      "Hand-authored in tools/build_plaguelands_dungeons_content.py.")}
    out.update(loot)
    LOOT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    t = json.loads(TOKENS.read_text(encoding="utf-8"))
    defs, bosses = PL_TOKENS()
    t["tokens"].update(defs)
    t["bosses"].update(bosses)
    TOKENS.write_text(json.dumps(t, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"  set_tokens.json: {len(defs)} tokens, {len(bosses)} bosses carry the head, chest and feet")

    import subprocess
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True, stdout=subprocess.DEVNULL)
    n = sum(len(v) for v in loot.values())
    print(f"  {LOOT.relative_to(ROOT)}: {len(loot)} pools, {n} items ({moved} put on the item curve)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
