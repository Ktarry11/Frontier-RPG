#!/usr/bin/env python3
"""Final-form fighting kits for the three 51-58 dungeons. Idempotent.

    PYTHONPATH=. python3 tools/build_isle_dungeon_kits.py

KHAZ VARUN and THE EMBERDEEP were built with their bosses' mechanics written down in
claude/tempest_isle_build_design.md and never put into the kits. Measured 14 Nov 2026: all nineteen
bosses hit for 88-130 with three abilities and no boss health multiplier, and their trash for
58-110. A rare out in the open world at the same level hits for about 500 and the Green Belt's
raptors for 200. The dungeons were the easiest thing on the island.

THE ROYAL HIVE is new (tools/handbuilt_royal_hive.py) and its creatures are written here too.

THE NUMBERS come from the finished dungeons either side of these, the Cistern and the Mother Vein
(48-53), extended by level:
    boss basic   B(L) = 300 + 10 * (L - 50)        Cistern: 311 at 52, 331 at 53
    trash basic  T(L) = 186 +  4 * (L - 48)        Mother Vein: 188-196 at 48-52
    boss health  2.3 optional, 2.5 required, 2.8 the last boss
Bosses get five or six abilities: the basic, a second hit, a heavy, one AoE or DoT, the mechanic
the design promised, and a phase at low health.

THE MECHANICS use the five interception hooks Monster.take_damage has run since 8 Nov, which kits
can reach as of today through a buff's `mechanics` (entities/monster.py, MECHANIC_FIELDS). A
mechanic that must be on from the first swing rides on the boss's opener as a long buff.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_return_voyage_content import (  # noqa: E402
    CREATURES, KITS, ENCOUNTERS, kit_slug, merge_json, _detect_format, dmg, dot, debuff, buff)


def B(level):
    return 300 + 10 * (level - 50)


def T(level):
    return 186 + 4 * (level - 48)


def opener(name, amount, school="physical", **mech):
    """The basic attack. If `mech` is given it rides on the first swing as a buff that lasts the
    fight, which is how a passive (reflect, a death floor) gets onto a boss."""
    e = dmg(name, amount, school=school, boss_rework=1)
    if mech:
        e["rider"] = {"effect": "buff", "duration": 99, "stat_mods": {}, "mechanics": mech}
    return e


def phase(name, level, school="physical", hp=0.35, pct=40, **extra):
    """The low-health enrage. ATTACK POWER, not damage_dealt_pct: a Monster reads only armor,
    attack_power and the *_damage_taken_pct family off its own buffs (tools/audit_monster_combat.py,
    INERT MONSTER BUFF), and attack_power is added flat to every hit it lands. So +40% is 40% of
    its basic attack, added to each swing."""
    return dict(name=name, kind="buff", amount=0, cooldown=99, mana_cost=0, school=school,
                duration=30, self_only=True, hp_below=hp,
                stat_mods={"attack_power": int(B(level) * pct / 100), **extra})


def stun_hit(name, amount, cooldown=5, school="physical"):
    return dmg(name, amount, cooldown=cooldown, school=school, authored_mechanic="stun",
               rider={"effect": "debuff", "duration": 1, "is_stun": True, "stat_mods": {}})


def shell(name, cooldown, duration, absorb, school="physical", **mech):
    e = dict(name=name, kind="buff", amount=0, cooldown=cooldown, mana_cost=0, school=school,
             duration=duration, self_only=True, stat_mods={}, absorb=absorb)
    if mech:
        e["mechanics"] = mech
    return e


#: The summoned creature's template and kit, read from the roster or creatures.json. A summon spec
#: needs both: MonsterAbility._summon builds a Monster from spec["template"] and spec["kit"], and the
#: old "creature"-only form these dungeons shipped with raised inside its try and FIZZLED every
#: time (14 Nov 2026) - Vaud never had his oozes, Morrun never called his garrison.
_SUMMON_SOURCES = {}


def summon(name, creature, cooldown, max_alive, max_casts):
    if creature in HIVE_ROSTER:
        template = HIVE_ROSTER[creature][0]
    else:
        template = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"][creature]["template"]
    return dict(name=name, kind="summon", amount=0, cooldown=cooldown, mana_cost=0,
                summon={"name": creature, "template": template, "kit": kit_slug(creature),
                        "count": 1, "level_offset": -2, "max_alive": max_alive,
                        "max_casts": max_casts})


def boss_kit(level, school, basic, second, heavy, spread, mechanic, phase_name, *, aoe=True,
             opener_mech=None, extra=()):
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
    kit.append(phase(phase_name, level, school))
    return kit


# =============================================================================== THE ROYAL HIVE
#: name -> (template, lo, hi, boss multiplier or None)
HIVE_ROSTER = {
    "Royal Hive Drone":      ("vermin_sneaky",    54, 55, None),
    "Royal Hive Guard":      ("humanoid_warrior", 55, 56, None),
    "Resin Weaver":          ("humanoid_caster",  54, 55, None),
    "Hive Tunneler":         ("vermin_swarm",     55, 56, None),
    "Brood Larva":           ("vermin_swarm",     54, 54, None),
    "Venomwing Wasp":        ("beast_fast",       55, 56, None),
    "Hive-Warden Kasz'ar":   ("humanoid_warrior", 54, 54, 2.5),
    "The Brood Nurse":       ("vermin_swarm",     54, 55, 2.3),
    "Resin-Mother Vex'ith":  ("humanoid_caster",  55, 55, 2.5),
    "Tunnel-King Ruzzak":    ("beast_large",      55, 56, 2.5),
    # THE LAST FIGHT IS TWO BOSSES AT ONCE (Kyle, 14 Nov: "Ensure the final royal Hive boss is another
    # 2 for 1 boss fight. Drops 3 pieces of loot"), the same shape as the galleon's cabin: one
    # encounter, the Consort folded into the queen's spawn (zone.boss_pack), one shared hoard.
    # Each is a little lighter than a lone final boss would be, because there are two of them.
    "Hive-Mother Ahn'thera": ("beast_large",      56, 56, 2.4),
    "Royal Consort Zhir'ak": ("humanoid_warrior", 56, 56, 2.3),
}


def hive_kits():
    t54, t55 = T(54), T(55)
    k = {
        "Royal Hive Drone": [dmg("Mandible Snap", t54), dmg("Carry It Off", int(t54 * 0.88), cooldown=3),
                             dot("Hive Spittle", int(t54 * 0.24), 4, 3, school="nature",
                                 dispel_type="poison")],
        "Royal Hive Guard": [dmg("Bladed Forelimb", t55 + 8), dmg("Shield the Way", int(t55 * 0.88), cooldown=3,
                             rider={"effect": "buff", "duration": 3, "stat_mods": {"armor": 160}}),
                             debuff("Pinned Under Chitin", 5, 3, {"dodge_rating": -40})],
        "Resin Weaver": [dmg("Resin Bolt", t54, school="nature"),
                         dot("Hardening Resin", int(t54 * 0.26), 4, 3, school="nature", dispel_type="poison"),
                         debuff("Gummed Joints", 5, 3, {"haste": -12}, school="nature")],
        "Hive Tunneler": [dmg("Bore Through", t55), dmg("Out of the Floor", int(t55 * 0.88), cooldown=3),
                          buff("Hard Head", 6, 3, {"armor": 140})],
        "Brood Larva": [dmg("Gnaw", int(t54 * 0.6)), dot("Feeding", int(t54 * 0.18), 4, 3)],
        "Venomwing Wasp": [dmg("Sting", t55, school="nature"),
                           dot("Venom in the Blood", int(t55 * 0.26), 4, 3, school="nature", dispel_type="poison"),
                           dmg("Swarm Dive", int(t55 * 0.66), cooldown=4, school="nature", is_aoe=True)],
    }
    k["Hive-Warden Kasz'ar"] = boss_kit(
        54, "physical", "Warden's Scythe", "Barred Way", "Sentence of the Hive", "Sweep the Threshold",
        None, "The Warden Will Not Fall",
        # the first time it drops below 40%, the carapace closes: a shield of 25% of its health
        opener_mech={"on_low_health_pct": 40, "on_low_health_shield_pct": 25, "on_low_health_uses": 1},
        extra=[shell("Carapace Locks", 6, 3, int(B(54) * 2.0))])
    k["The Brood Nurse"] = boss_kit(
        54, "nature", "Feeding Tube", "Spit Royal Jelly", "Smother", "Brood Stench",
        summon("Wake the Clutch", "Brood Larva", 4, 3, 5), "Every Egg at Once", aoe=False,
        extra=[dict(name="Feed on the Clutch", kind="heal", amount=int(B(54) * 1.2), cooldown=5,
                    mana_cost=0, school="nature")])
    k["Resin-Mother Vex'ith"] = boss_kit(
        55, "nature", "Resin Lash", "Pour the Cell Shut", "Seal in Amber", "Acid Rain",
        stun_hit("Encase", int(B(55) * 0.7), cooldown=5, school="nature"), "The Mother's Fury",
        extra=[dot("Dissolving Coat", int(B(55) * 0.34), 5, 4, school="nature", dispel_type="poison",
                   is_aoe=True)])
    k["Tunnel-King Ruzzak"] = boss_kit(
        55, "physical", "Grinding Maw", "Tunnel Collapse", "Burst From Below", "The Floor Gives Way",
        # while burrowed, everything that lands on it becomes shell instead: stop hitting it
        shell("Burrow", 6, 3, int(B(55) * 1.2), damage_to_shield_pct=100, damage_to_shield_school=""),
        "King of the Deep")
    k["Hive-Mother Ahn'thera"] = boss_kit(
        56, "nature", "Royal Talon", "Command the Swarm", "The Queen's Judgement", "Hive Song",
        summon("Call the Royal Guard", "Royal Hive Guard", 5, 2, 3), "The Hive Will Not End",
        # holds at the brink once: the kill needs a second commitment
        opener_mech={"death_prevent_pct": 10, "death_prevent_uses": 1, "death_prevent_lethal_only": True},
        extra=[stun_hit("Deafening Screech", int(B(56) * 0.6), cooldown=6, school="nature")])
    # The Consort stands in front of her. He hits hard, wears his shell like a wall and sends
    # some of what lands on it back at whoever is hitting him in melee.
    k["Royal Consort Zhir'ak"] = boss_kit(
        56, "physical", "Twin Scythes", "Guard the Queen", "Consort's Verdict", "Cleave the Court",
        dmg("Living Wall", int(B(56) * 0.6), cooldown=4,
            rider={"effect": "buff", "duration": 4, "stat_mods": {"armor": 700}}),
        "For the Queen",
        opener_mech={"reflect_pct": 15, "reflect_school": "physical", "reflect_melee_only": True})
    return k


# =============================================================================== KHAZ VARUN
KV_BOSSES = {
    # name: (level, school, basic, second, heavy, spread, aoe?, mechanic builder, phase, mult)
    "Gatewarden Hrun": (52, "physical", "Gate Shield", "Shield Crack", "Bar the Gate", "Shield Sweep", True,
                        lambda L: dmg("Warden's Stance", int(B(L) * 0.6), cooldown=4,
                                      rider={"effect": "buff", "duration": 4,
                                             "stat_mods": {"physical_damage_taken_pct": -40,
                                                           "magic_damage_taken_pct": -15}}),
                        "The Gate Holds", 2.5),
    "The Crusher": (52, "physical", "Piston Fall", "Walking Frame", "Stamp", "Shrapnel", True,
                    None, "Overpressure", 2.3, {"reflect_pct": 30, "reflect_school": "physical",
                                                "reflect_melee_only": True}),
    "Smelter-Master Vaud": (53, "fire", "Tapping Spout", "Ladle of Slag", "Pour", "Spill the Crucible", True,
                            lambda L: summon("Call the Slag", "Slag Ooze", 4, 3, 4),
                            "The Crucible Cracks", 2.5),
    "Powderkeg Nix": (53, "fire", "Lit Fuse", "Thrown Charge", "Packed in Tight", "Detonation", True,
                      None, "Last Keg", 2.3, {"death_prevent_pct": 10, "death_prevent_uses": 1}),
    "Overseer Grall": (53, "physical", "Cane Across the Back", "Docked Pay", "Make an Example", "Reading the Ledger",
                       False, lambda L: dmg("Same Again", int(B(L) * 0.7), cooldown=2,
                                            rider={"effect": "buff", "duration": 8,
                                                   "stat_mods": {"attack_power": int(B(L) * 0.15)}}),
                       "Nobody Leaves", 2.5),
    "Forge-Lord Darrok": (54, "fire", "Molten Blade", "Bellows Roar", "Quenching Strike", "Forge Breath", True,
                          lambda L: shell("Quenched in Magic", 6, 4, int(B(L) * 1.0),
                                          damage_to_shield_pct=40, damage_to_shield_school="magic"),
                          "White Heat", 2.5),
    "The Iron Mask": (54, "physical", "Riveted Shut", "Masked Silence", "Iron Brow", "Sermon of Rivets", False,
                      lambda L: stun_hit("Nothing Gets In", int(B(L) * 0.7), cooldown=5),
                      "Unmasked", 2.5, None,
                      [shell("Visor Down", 7, 3, int(B(54) * 0.8), dot_immune=True)]),
    "The Ashwretch Brood": (54, "shadow", "Swarming Claws", "Dragged Down", "Pile On", "More of Them", True,
                            lambda L: summon("Wake the Pits", "Ash-Wretch", 4, 3, 4),
                            "All of Them at Once", 2.3),
    "The Rock-Borer Queen": (54, "physical", "Queen's Maw", "Burrowing Young", "Tunnel Charge", "Cave-In", True,
                             lambda L: dmg("Carapace", int(B(L) * 0.6), cooldown=4,
                                           rider={"effect": "buff", "duration": 4, "stat_mods": {"armor": 900}}),
                             "The Queen Digs Deep", 2.3),
    "Flamespeaker Maud": (54, "fire", "Speak Fire", "The Flame Listens", "Kindle", "Wreathed", True,
                          None, "The Fire Answers", 2.5, {"damage_to_heal_pct": 50, "damage_to_heal_school": "fire"}),
    "The Shadow of the Forge": (54, "shadow", "Smoke and Ember", "Soot in the Eyes", "Banked Coals",
                                "Choking Smoke", True, None, "It Will Not Go Out", 2.5,
                                {"reflect_pct": 20, "reflect_school": "shadow",
                                 "on_low_health_pct": 35, "on_low_health_shield_pct": 20,
                                 "on_low_health_uses": 1}),
    "Thane Morrun the Unmade": (54, "physical", "Ancestral Hammer", "Oath-Breaker", "The Thane's Due",
                                "Hall of Ashhold", True,
                                lambda L: summon("Call the Garrison", "Molten Thane", 5, 2, 3),
                                "Half-Fused with Stone", 2.8,
                                {"death_prevent_hp": 1, "death_prevent_uses": 1}),
}

# =============================================================================== THE EMBERDEEP
ED_BOSSES = {
    "Pack-Alpha Cinderhound": (56, "fire", "Alpha's Jaws", "Hamstring", "Tear Out", "Run Them Down", True,
                               lambda L: dmg("Blood Up", int(B(L) * 0.7), cooldown=2, school="fire",
                                             rider={"effect": "buff", "duration": 8,
                                                    "stat_mods": {"attack_power": int(B(L) * 0.15)}}),
                               "The Pack's Blood", 2.5),
    "Thrass, the Geyser Spirit": (56, "frost", "Scalding Jet", "Steam Lash", "Boiling Column", "The Geyser Breaks",
                                  True, lambda L: dmg("Eruption Cycle", int(B(L) * 0.9), cooldown=3,
                                                      school="frost", is_aoe=True),
                                  "Full Pressure", 2.5),
    "Basalt Guardian Vok": (57, "physical", "Carved Hammer", "Rune Shock", "Hexagon Slam", "Columnar Fall", True,
                            lambda L: dmg("Columnar", int(B(L) * 0.6), cooldown=4,
                                          rider={"effect": "buff", "duration": 4,
                                                 "stat_mods": {"armor": 700,
                                                               "physical_damage_taken_pct": -20}}),
                            "Unbroken Stone", 2.5),
    "The Molten Serpent": (57, "fire", "Coil and Crush", "Lava in the Wound", "Strike From the Lake", "Lava Wave",
                           True, lambda L: shell("Submerged", 6, 3, int(B(L) * 1.2),
                                                 damage_to_shield_pct=100, damage_to_shield_school=""),
                           "Boiling Over", 2.5),
    "Flame Oracle Ysmel": (58, "fire", "Prophecy of Ash", "Read to the Weakest", "The Ring Answers",
                           "Everything Burns the Same", True,
                           lambda L: dict(name="Read Every Weakness", kind="debuff", amount=0, cooldown=5,
                                          mana_cost=0, school="fire", duration=4, is_aoe=True,
                                          stat_mods={"magic_damage_taken_pct": 15,
                                                     "physical_damage_taken_pct": 15}),
                           "The Last Prophecy", 2.5),
    "The Mountain's Heart": (58, "fire", "Stone Through the Crack", "Shoulder the Floor", "Molten Core Exposed",
                             "Heat of the Deep", False, None, "The Heart Beats Faster", 2.3,
                             {"death_prevent_pct": 1, "death_prevent_uses": 1,
                              "on_low_health_pct": 30, "on_low_health_shield_pct": 20,
                              "on_low_health_uses": 1}),
    "The Caldera": (58, "fire", "Falling Lava", "Crater Wall", "Eruption", "Rain of Fire", True,
                    lambda L: summon("The Mountain Stirs", "Lava Lord", 5, 2, 3), "The Volcano Wakes", 2.8),
}


def reworked_boss(spec):
    level, school, basic, second, heavy, spread, aoe, mech, ph, mult = spec[:10]
    opener_mech = spec[10] if len(spec) > 10 else None
    extra = spec[11] if len(spec) > 11 else []
    return boss_kit(level, school, basic, second, heavy, spread, mech(level) if mech else None, ph,
                    aoe=aoe, opener_mech=opener_mech, extra=extra), mult


#: A second attack for the trash that was written with only one. Named for what the creature is.
SECOND_HIT = {
    "magma_elemental": "Lava Knuckle", "crazed_miner": "Wild Overhand", "masked_zealot": "Hammer of Faith",
    "ash_wretch": "Drag Down", "chained_berserker": "Swinging Chain", "fire_worshipper": "Hurled Coal",
    "iron_golem": "Hammer Arm", "stone_golem": "Crushing Step", "steam_automaton": "Piston Punch",
    "rock_borer": "Bore In", "deep_spider": "Leg Spike", "slag_ooze": "Engulf",
    "shadow_of_the_forge": "Cinder Grasp", "molten_thane": "Slag-Fist", "fire_sprite": "Spark Burst",
    "flame_elemental": "Searing Arm", "ash_wraith": "Ash Touch", "earth_elemental": "Rockfall",
    "obsidian_shardling": "Splinter", "basalt_guardian": "Stone Fist", "steam_elemental": "Scald",
    "sulphur_crawler": "Pincer Snap", "ember_swarm": "Swarm of Sparks", "molten_serpent": "Tail Lash",
    "flame_oracle": "Rune of Flame",
}


def reworked_trash(old_kit, level, kit_id=""):
    """Keep the names and the shape the trash was written with; set the numbers to the band."""
    t = T(level)
    out, hits = [], 0
    for a in old_kit:
        a = dict(a)
        if a["kind"] == "damage":
            a["amount"] = t if hits == 0 else int(t * (0.66 if a.get("is_aoe") else 0.88))
            a["cooldown"] = 0 if hits == 0 else max(3, a.get("cooldown", 3))
            hits += 1
        elif a["kind"] == "buff" and a.get("self_only"):
            # only what a monster reads off its own buff (see phase())
            mods, keep = dict(a.get("stat_mods") or {}), {}
            for k2, v in mods.items():
                if k2 == "damage_dealt_pct":
                    keep["attack_power"] = int(t * v / 100)
                elif k2 in ("dodge", "dodge_rating", "parry", "parry_rating"):
                    keep["physical_damage_taken_pct"] = -min(30, abs(int(v)))
                elif k2 in ("armor", "attack_power", "damage_taken_pct", "magic_damage_taken_pct",
                            "physical_damage_taken_pct", "spell_damage_taken_pct", "magic_resistance"):
                    keep[k2] = v
            a["stat_mods"] = keep or {"attack_power": int(t * 0.15)}
        elif a["kind"] == "dot":
            a["amount"] = int(t * 0.24)
            a["cooldown"] = max(4, a.get("cooldown", 4))
            a["duration"] = max(3, a.get("duration", 3))
        out.append(a)
    if hits == 0:
        out.insert(0, dmg("Strike", t))
    if hits < 2:
        out.append(dmg(SECOND_HIT.get(kit_id, "Second Strike"), int(t * 0.88), cooldown=3,
                       school=out[0].get("school", "physical")))
    return out


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    import contextlib
    import io
    with contextlib.redirect_stdout(io.StringIO()):
        import tools.handbuilt_khaz_varun as KVM
        import tools.handbuilt_emberdeep as EDM
        import tools.handbuilt_royal_hive as RH
        kvz, edz = KVM.generate_khaz_varun(), EDM.generate_emberdeep()
        rhz, _ = RH.build_royal_hive()

    creatures = json.loads(CREATURES.read_text(encoding="utf-8"))["creatures"]
    kits_all = json.loads(KITS.read_text(encoding="utf-8"))["kits"]
    new_c, new_k = {}, {}

    # ---- the two isle dungeons: bosses re-authored, trash rescaled
    for zone, table in ((kvz, KV_BOSSES), (edz, ED_BOSSES)):
        bosses = {n for *_, n in zone.boss_positions}
        if bosses != set(table):
            print(f"FAILED: {zone.name} bosses and the table differ: {sorted(bosses ^ set(table))}")
            return 1
        for name, spec in table.items():
            kit, mult = reworked_boss(spec)
            rec = dict(creatures[name])
            rec["boss_multiplier"] = mult
            rec["ability_kit"] = kit_slug(name)
            new_c[name] = rec
            new_k[kit_slug(name)] = kit
        for name in sorted({n for *_, n, _l in zone.trash_spawns}):
            rec = creatures[name]
            lo, hi = rec["level_range"]
            old = [x for x in kits_all[rec["ability_kit"]] if not x["name"].endswith(" Again")]
            new_k[rec["ability_kit"]] = reworked_trash(old, (lo + hi) // 2, rec["ability_kit"])

    # ---- the hive: new
    hk = hive_kits()
    if set(hk) != set(HIVE_ROSTER):
        print(f"FAILED: hive roster and kits differ: {sorted(set(hk) ^ set(HIVE_ROSTER))}")
        return 1
    placed = {n for *_, n in rhz.boss_positions} | {n for *_, n, _l in RH._snap(rhz, RH._trash())}
    summoned = {"Brood Larva", "Royal Hive Guard"}
    placed |= {m[2] for v in getattr(rhz, "boss_pack", {}).values() for m in v}
    if (placed | summoned) != set(HIVE_ROSTER):
        print(f"FAILED: hive map and roster differ: {sorted((placed | summoned) ^ set(HIVE_ROSTER))}")
        return 1
    for name, (template, lo, hi, mult) in HIVE_ROSTER.items():
        rec = {"template": template, "level_range": [lo, hi], "is_boss": bool(mult),
               "ability_kit": kit_slug(name)}
        if mult:
            rec["boss_multiplier"] = mult
        new_c[name] = rec
        new_k[kit_slug(name)] = hk[name]

    merge_json(CREATURES, "creatures", new_c, "creatures.json")
    merge_json(KITS, "kits", new_k, "ability_kits.json")

    # ---- the hive's own table, under its parent zone's caves (the level banner reads it)
    raw = ENCOUNTERS.read_text(encoding="utf-8")
    enc = json.loads(raw)
    indent, newline = _detect_format(enc, raw)
    caves = enc["zones"]["The Black Strand"].setdefault("caves", {})
    caves[RH.NAME] = {"name": RH.NAME, "creatures": {n: 0 if m else 4 for n, (_t, _lo, _hi, m)
                                                      in HIVE_ROSTER.items()}}
    ENCOUNTERS.write_text(json.dumps(enc, indent=indent, ensure_ascii=False)
                          + ("\n" if newline else ""), encoding="utf-8")
    nb = sum(1 for n in new_c if new_c[n].get("is_boss"))
    print(f"{len(new_c)} creatures written ({nb} bosses), {len(new_k)} kits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
