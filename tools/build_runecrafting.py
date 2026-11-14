#!/usr/bin/env python3
"""Runecrafting: runes imprinted on the soul. Idempotent.

    PYTHONPATH=. python3 tools/build_runecrafting.py
    PYTHONPATH=. python3 tools/vendor_trades.py        # then stock the shops

Kyle, 13 to 14 Nov 2026 (claude/runecrafting_DESIGN_ONLY.md, claude/runecrafting_decisions.md):
"runes will be imprinted on the players soul. They get to have 4 of them. Made by using enchanting
dust. Maybe have different tier. One Capstone rune (this will be meta defining)." It's its own
profession, all four slots are open from the start, every companion has their own four, and the
roulette Capstone averages a little under normal with a giant ceiling. Then: "We want this
profession to be like others. Clearly useful to have but not required to progress", "a range of
rune skills... a low level capstone might be 30% elemental conversion, mid is 70% high is 100%",
"I'd like other ones. Like dodging causes a retaliation hit. Hots or dots can last less turns but
are stronger. Or normal Heals will turn into hots", and "Runes should still be generic. Nothing
class specific."

THE SHAPE
  * Every rune comes in three ranks: Lesser, plain and Greater (low, mid and high level).
  * A soul holds three runes and one Capstone. No rune twice on one soul.
  * Runes change what a character does (procs, conversions, how heals and DoTs behave); the plain
    stat boosts are Enchanting's job.
  * Nothing names a class or an ability. A rune works off heals, HoTs, DoTs, crits, dodges, kills
    and elements, whoever has them.
  * A Capstone's rank is how often it happens: 30% of the time, 70%, always.

MATERIALS. Runes cost enchanting materials (dust, essence, shards, and a Nexus Crystal for a
Greater Capstone) plus a rune ink of their tier. Inks are made at every stretch of the skill
ladder, so there's always something to level on.

WRITES
  data/runecrafting/runes.json      every rune (read by world/runes.py)
  data/runecrafting/recipes.json    inks and runes
  data/gathering/materials.json     inks and runes as materials
  data/professions/professions.json, data/training/trainers.json   taught by the five enchanters
  assets/gathering_nodes/runes/     icons, borrowed from the Runemaster talent art
"""
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.build_jewelcrafting import load, save, skill_range  # noqa: E402
from tools.build_enchanting import TRAINER_NPCS  # noqa: E402

MATS = ROOT / "data/gathering/materials.json"
OUT_RUNES = ROOT / "data/runecrafting/runes.json"
OUT_RECIPES = ROOT / "data/runecrafting/recipes.json"
PROFS = ROOT / "data/professions/professions.json"
TRAINERS = ROOT / "data/training/trainers.json"
ICON_SRC = ROOT / "assets/icons/talents"
ART = ROOT / "assets/gathering_nodes/runes"

RANKS = ["Lesser", "", "Greater"]

#: (id, name, skill, dust, vial)
INKS = [
    ("rune_ink_strange", "Strange Rune Ink", 1, "strange_dust", "vial_empty"),
    ("rune_ink_soul", "Soul Rune Ink", 60, "soul_dust", "vial_empty"),
    ("rune_ink_vision", "Vision Rune Ink", 120, "vision_dust", "vial_leaded"),
    ("rune_ink_dream", "Dream Rune Ink", 180, "dream_dust", "vial_leaded"),
    ("rune_ink_illusion", "Illusion Rune Ink", 240, "illusion_dust", "vial_crystal"),
]

#: per rank: (required level, base skill, ink, essence, shard)
NORMAL_TIERS = [
    (20, 30, "rune_ink_soul", "lesser_astral_essence", None),
    (40, 140, "rune_ink_dream", "greater_mystic_essence", "small_radiant_shard"),
    (55, 250, "rune_ink_illusion", "greater_eternal_essence", "large_brilliant_shard"),
]
CAPSTONE_TIERS = [
    (25, 90, "rune_ink_vision", "greater_astral_essence", "large_glimmering_shard"),
    (45, 200, "rune_ink_dream", "greater_nether_essence", "large_radiant_shard"),
    (60, 285, "rune_ink_illusion", "greater_eternal_essence", "nexus_crystal"),
]
#: how often a Capstone happens, by rank (Kyle: 30% low, 70% mid, 100% high)
CAPSTONE_CHANCE = [0.30, 0.70, 1.00]


def proc(trigger, describe, **kw):
    p = {"trigger": trigger, "chance": kw.pop("chance", 100), "icd": kw.pop("icd", 0), "describe": describe}
    p.update(kw)
    return p


# ------------------------------------------------------------------ regular runes
#: id -> (name, rank -> (effects, procs, words))
#: effects are talent-pool keys (fractions, as talents write them); procs ride the proc engine.
def _forms():
    try:
        from combat.forms import FORMS
        return sorted(FORMS)
    except Exception:
        return []


def _pct(v):
    return int(round(abs(v) * 100))


#: Kyle, 14 Nov 2026: "generate a big list of options. Since we need them for different type of
#: healers (st, aoe, hot), dps (physical, magical, critical based, st, aoe, hot) and tanks (evasion
#: tanks, Stam tanks, shapeshift tanks etc). Still keeping them general but everyone should have
#: options to adjust their style." And: "regular runes need trade offs... Minor ones that makes the
#: runes still appealing."
#:
#: Each row: id, name, role, the three ranks' values, how a rank becomes (effects, procs, words),
#: and the trade-off (key, three values, words) or None when the trade is built in.
def normal_runes():
    F = _forms()
    rows = [
        # ---------------- tanks
        ("riposte", "Riposte", "tank", (30, 70, 130),
         lambda v: ({}, [proc("on_avoid", f"When you dodge or parry, you strike back for {v}.", damage_flat=v, school="physical")],
                    f"Dodging or parrying strikes back for {v}."),
         ("magic_damage_taken_pct", (0.02, 0.03, 0.04), "you take {}% more magic damage")),
        ("thorns", "Thorns", "tank", (8, 20, 38),
         lambda v: ({}, [proc("on_damage_taken", f"Whoever hits you takes {v} damage.", damage_flat=v, school="physical")],
                    f"Whoever hits you takes {v} damage."),
         ("healing_received_pct", (-0.04, -0.05, -0.06), "heals on you are {}% weaker")),
        ("bulwark", "Bulwark", "tank", (0.03, 0.05, 0.08),
         lambda v: ({"physical_damage_taken_pct": -v}, [], f"You take {_pct(v)}% less physical damage."),
         ("magic_damage_taken_pct", (0.02, 0.03, 0.04), "you take {}% more magic damage")),
        ("warding", "Warding", "tank", (0.03, 0.05, 0.08),
         lambda v: ({"magic_damage_taken_pct": -v}, [], f"You take {_pct(v)}% less magic damage."),
         ("physical_damage_taken_pct", (0.02, 0.03, 0.04), "you take {}% more physical damage")),
        ("bastion", "the Bastion", "tank", (0.04, 0.07, 0.10),
         lambda v: ({"max_health_pct": v}, [], f"Your health is {_pct(v)}% higher."),
         ("all_damage", (-0.03, -0.04, -0.05), "you deal {}% less damage")),
        ("ironhide", "Ironhide", "tank", (120, 260, 450),
         lambda v: ({"armor": v}, [], f"+{v} armour."),
         ("dodge_rating", (-1, -2, -3), "you dodge {}% less often", True)),
        ("evasion", "Evasion", "tank", (1, 2, 3),
         lambda v: ({"dodge_rating": v}, [], f"You dodge {v}% more often."),
         ("armor", (-100, -200, -350), "you lose {} armour", True)),
        ("last_stand", "the Last Stand", "tank", (0.10, 0.15, 0.20),
         lambda v: ({"low_health_damage_reduction_pct": v}, [], f"Below 35% health you take {_pct(v)}% less damage."),
         ("max_health_pct", (-0.02, -0.03, -0.04), "your health is {}% lower")),
        ("second_wind", "Second Wind", "tank", (60, 120, 200),
         lambda v: ({}, [proc("on_damage_taken", f"Being hit can give you a second wind, healing {v}.", chance=12, icd=4, heal_flat=v)],
                    f"Being hit has a chance to heal you for {v}."),
         ("healing_received_pct", (-0.03, -0.04, -0.05), "heals on you are {}% weaker")),
        ("rampart", "the Rampart", "tank", (30, 70, 120),
         lambda v: ({}, [proc("on_block", f"Blocking heals you for {v}.", heal_flat=v)], f"Blocking a hit heals you for {v}."),
         ("magic_damage_taken_pct", (0.02, 0.03, 0.04), "you take {}% more magic damage")),
        ("wild_hide", "the Wild Hide", "tank", (150, 320, 550),
         lambda v: ({}, [proc("on_damage_taken", f"While shapeshifted, being hit can harden your hide for {v} armour, 2 turns.",
                              chance=25, icd=2, require_form=F,
                              apply_effect={"effect_id": "rune_wild_hide", "name": "Hardened Hide", "effect_type": "buff",
                                            "duration": 2, "stat_mods": {"armor": v}, "on_target": False})],
                    f"While in any shapeshift form, being hit can harden your hide: +{v} armour for 2 turns."),
         ("healing_done", (-0.04, -0.05, -0.06), "your heals are {}% weaker")),
        ("menace", "Menace", "tank", (0.15, 0.30, 0.50),
         lambda v: ({"threat_generation_pct": v}, [], f"You make {_pct(v)}% more threat."),
         ("all_damage", (-0.03, -0.04, -0.05), "you deal {}% less damage")),
        ("steadfast", "the Steadfast", "tank", (0.20, 0.35, 0.50),
         lambda v: ({"stun_duration_reduction_pct": v}, [], f"Stuns on you last {_pct(v)}% shorter."),
         ("all_damage", (-0.02, -0.03, -0.04), "you deal {}% less damage")),
        # ---------------- damage: physical, crits, single target, AoE, DoTs
        ("execution", "Execution", "damage", (0.08, 0.14, 0.20),
         lambda v: ({"low_health_damage_pct": v}, [], f"{_pct(v)}% more damage to targets under 35% health."),
         ("all_damage", (-0.03, -0.04, -0.05), "you deal {}% less damage all the time")),
        ("rupture", "Rupture", "damage", (25, 55, 100),
         lambda v: ({}, [proc("on_damage_cast", f"Your attacks can tear the target for {v} more damage.", chance=15, damage_flat=v, school="physical")],
                    f"Your attacks have a chance to tear for {v} more damage."),
         ("all_ability_cost_pct", (-0.03, -0.04, -0.05), "abilities cost {}% more")),
        ("bloodlust", "Bloodlust", "damage", (25, 55, 95),
         lambda v: ({}, [proc("on_kill", f"A kill grants {v} attack power and spell power for 3 turns.",
                              apply_effect={"effect_id": "rune_bloodlust", "name": "Bloodlust", "effect_type": "buff",
                                            "duration": 3, "stat_mods": {"attack_power": v * 2, "spell_power": v}, "on_target": False})],
                    f"Kills grant {v * 2} attack power and {v} spell power for 3 turns."),
         ("max_health_pct", (-0.02, -0.03, -0.04), "your health is {}% lower")),
        ("precision", "Precision", "damage", (2, 3, 4),
         lambda v: ({"crit_chance": v}, [], f"+{v}% critical strike chance."),
         ("crit_damage_pct", (-0.10, -0.15, -0.20), "your crits do {}% less")),
        ("devastation", "Devastation", "damage", (0.10, 0.18, 0.25),
         lambda v: ({"crit_damage_pct": v}, [], f"Your crits do {_pct(v)}% more."),
         ("crit_chance", (-1, -2, -2), "you crit {}% less often", True)),
        ("thunder", "Thunder", "damage", (25, 55, 95),
         lambda v: ({}, [proc("on_crit", f"Your critical hits call down lightning for {v} nature damage.", icd=1, damage_flat=v, school="nature")],
                    f"Critical hits call down lightning for {v}."),
         ("crit_damage_pct", (-0.05, -0.08, -0.10), "your crits do {}% less")),
        ("chain_reaction", "Chain Reaction", "damage", (0.20, 0.35, 0.50),
         lambda v: ({}, [proc("on_crit", f"Your critical hits splash {_pct(v)}% onto two other enemies.", icd=1,
                              splash_damage={"pct": v, "max_targets": 2})],
                    f"Critical hits splash {_pct(v)}% onto two other enemies."),
         ("threat_generation_pct", (0.10, 0.15, 0.20), "you make {}% more threat")),
        ("focus", "Focus", "damage", (0.04, 0.06, 0.08),
         lambda v: ({"all_damage": v}, [], f"You deal {_pct(v)}% more damage."),
         ("aoe_damage", (-0.10, -0.15, -0.20), "your area attacks do {}% less")),
        ("sweeping", "the Sweep", "damage", (0.10, 0.17, 0.25),
         lambda v: ({"aoe_damage": v}, [], f"Your area attacks do {_pct(v)}% more."),
         ("all_damage", (-0.03, -0.04, -0.05), "you deal {}% less damage overall")),
        ("overload", "Overload", "damage", ((0.05, 0.10), (0.09, 0.15), (0.13, 0.20)),
         lambda v: ({"all_damage": v[0], "all_ability_cost_pct": -v[1]}, [],
                    f"You deal {_pct(v[0])}% more damage. But abilities cost {_pct(v[1])}% more."),
         None),
        ("rot", "Rot", "damage", (0.10, 0.17, 0.25),
         lambda v: ({"dot_damage": v}, [], f"Your DoTs do {_pct(v)}% more."),
         ("all_damage", (-0.03, -0.04, -0.05), "everything else does {}% less")),
        ("piercing", "Piercing", "damage", (8, 16, 30),
         lambda v: ({"spell_penetration": v}, [], f"+{v} spell penetration: your spells ignore that much resistance."),
         ("all_ability_cost_pct", (-0.03, -0.04, -0.05), "abilities cost {}% more")),
        ("wellspring", "the Wellspring", "damage", (30, 60, 100),
         lambda v: ({}, [proc("on_cast", f"Your spells can give you {v} mana back.", chance=10, icd=2,
                              grant_resource={"resource": "mana", "amount": v})],
                    f"Casting has a chance to give you {v} mana back."),
         ("spell_damage", (-0.02, -0.03, -0.04), "your spells do {}% less damage")),
        ("reaping", "Reaping", "damage", (40, 90, 160),
         lambda v: ({}, [proc("on_kill", f"Killing an enemy gives you {v} mana.", grant_resource={"resource": "mana", "amount": v})],
                    f"Kills give {v} mana."),
         ("max_mana_pct", (-0.04, -0.06, -0.08), "your mana pool is {}% smaller")),
        ("devourer", "the Devourer", "damage", (0.03, 0.05, 0.08),
         lambda v: ({}, [proc("on_damage_cast", f"{_pct(v)}% of the damage you deal heals you.", leech_pct=v)],
                    f"{_pct(v)}% of your damage heals you."),
         ("all_damage", (-0.03, -0.04, -0.05), "you deal {}% less damage")),
        ("pack", "the Pack", "damage", (0.08, 0.14, 0.20),
         lambda v: ({"pet_damage": v}, [], f"Your pets and summons do {_pct(v)}% more damage."),
         ("all_damage", (-0.03, -0.04, -0.05), "you deal {}% less yourself")),
        # ---------------- over time, both sides
        ("condensing", "Condensing", "any", (0.10, 0.20, 0.30),
         lambda v: ({"rune_condense": v}, [], f"Your DoTs and HoTs last half as long and do {_pct(v)}% more in total."),
         ("all_ability_cost_pct", (-0.04, -0.06, -0.08), "abilities cost {}% more")),
        ("lingering", "Lingering", "any", (0.50, 0.75, 1.00),
         lambda v: ({"rune_linger": v}, [], f"Your DoTs and HoTs last {_pct(v)}% longer, each tick a quarter softer."),
         None),
        # ---------------- healers: single target, AoE, HoTs, mana, hybrids
        ("communion", "Communion", "healing", (0.15, 0.25, 0.35),
         lambda v: ({}, [proc("on_heal_cast", f"Your heals also heal another ally for {_pct(v)}%.", splash_heal={"pct": v, "max_targets": 1})],
                    f"Your heals also heal one more ally for {_pct(v)}%."),
         ("healing_done", (-0.04, -0.06, -0.08), "your heals are {}% weaker")),
        ("radiance", "the Halo", "healing", (0.08, 0.12, 0.16),
         lambda v: ({}, [proc("on_heal_cast", f"Your heals spill {_pct(v)}% onto up to three other allies.", splash_heal={"pct": v, "max_targets": 3})],
                    f"Your heals spill {_pct(v)}% onto up to three other allies."),
         ("all_ability_cost_pct", (-0.04, -0.06, -0.08), "abilities cost {}% more")),
        ("triage", "Triage", "healing", (0.10, 0.18, 0.25),
         lambda v: ({"low_health_healing_pct": v}, [], f"Your heals are {_pct(v)}% stronger on allies under 35% health."),
         ("healing_done", (-0.03, -0.04, -0.05), "your heals are {}% weaker all the time")),
        ("serenity", "Serenity", "healing", (0.05, 0.08, 0.12),
         lambda v: ({"heal_cost_pct": v}, [], f"Your heals cost {_pct(v)}% less."),
         ("healing_done", (-0.03, -0.04, -0.05), "your heals are {}% weaker")),
        ("martyr", "the Martyr", "healing", (0.06, 0.10, 0.14),
         lambda v: ({"healing_done": v}, [], f"Your heals are {_pct(v)}% stronger."),
         ("damage_taken_pct", (0.03, 0.04, 0.05), "you take {}% more damage")),
        ("atonement", "Atonement", "healing", (0.05, 0.08, 0.12),
         lambda v: ({}, [proc("on_damage_cast", f"Your damage heals up to two allies for {_pct(v)}% of it.", splash_heal={"pct": v, "max_targets": 2})],
                    f"Your damage heals up to two allies for {_pct(v)}% of it."),
         ("healing_done", (-0.05, -0.08, -0.10), "your heals are {}% weaker")),
        ("blood_pact", "the Blood Pact", "any", (0.06, 0.09, 0.12),
         lambda v: ({"all_ability_cost_pct": v}, [], f"Abilities cost {_pct(v)}% less."),
         ("max_health_pct", (-0.04, -0.06, -0.08), "your health is {}% lower")),
        ("fortune", "Fortune", "any", (0.10, 0.20, 0.30),
         lambda v: ({"gold_find_pct": v}, [], f"You find {_pct(v)}% more gold."),
         ("all_damage", (-0.02, -0.03, -0.04), "you deal {}% less damage")),
    ]
    R = {}
    for row in rows:
        rid, name, role, vals, make, cost = row
        ranks = []
        for i, v in enumerate(vals):
            fx, pr, text = make(v)
            fx = dict(fx)
            if cost:
                key, cvals, words = cost[0], cost[1], cost[2]
                flat = len(cost) > 3          # a flat amount (armour, rating), not a percentage
                fx[key] = fx.get(key, 0) + cvals[i]
                shown = abs(cvals[i]) if flat else _pct(cvals[i])
                text = f"{text} But {words.format(shown)}."
            ranks.append((fx, pr, text))
        R[rid] = (name, ranks, role)
    return R


# ------------------------------------------------------------------ Capstones
#: Kyle, 14 Nov: "For element swaps we can actually do things like.... 'magic damage converts to
#: element' or 'physical damage converts' or for hybrids we can also have 'half of magic and
#: physical damage converts' to open up more styles." So each element has three Capstones: one
#: for spells (any magic school), one for physical (the elemental cat), and a hybrid one that
#: converts both, half as often.
ELEMENTS = [
    # (element, spell rune, physical rune, hybrid rune)
    ("fire", "Flame", "Cinders", "the Emberblade"),
    ("frost", "Frost", "Rime", "the Frostblade"),
    ("nature", "Storms", "the Tempest", "the Stormblade"),
    ("shadow", "Shadows", "the Abyss", "the Shadowblade"),
    ("holy", "Radiance", "Dawn", "the Sunblade"),
    ("arcane", "Arcana", "the Arcanist", "the Arcblade"),
]


def capstones():
    C = {}
    for dst, spell, phys, hybrid in ELEMENTS:
        for cid, name, src, share in ((f"{dst}_spells", spell, "magic", 1.0),
                                      (f"{dst}_weapons", phys, "physical", 1.0),
                                      (f"{dst}_hybrid", hybrid, "both", 0.5)):
            what = {"magic": "spell damage (any school)", "physical": "physical damage",
                    "both": "spell and physical damage"}[src]
            C[cid] = (name, [
                ({"kind": "convert", "from": src, "to": dst, "chance": round(ch * share, 2)},
                 f"{int(round(ch * share * 100))}% of your {what} lands as {dst}. Abilities keep their own "
                 f"school for talents and bonuses; the target's {dst} resistance decides the hit.")
                for ch in CAPSTONE_CHANCE])
    C["chaos"] = ("Chaos", [
        ({"kind": "chaos", "chance": ch},
         f"{int(ch * 100)}% of your hits land as a random element.") for ch in CAPSTONE_CHANCE])
    # the roulette: lands a lot under normal most of the time, sometimes far over it
    C["gambler"] = ("the Gambler", [
        ({"kind": "gamble", "low": lo, "high": hi, "jackpot": jp, "jackpot_low": jl, "jackpot_high": jh},
         f"Your damage rolls anywhere from {int(lo * 100)}% to {int(jh * 100)}% of normal, "
         f"a little under normal on average. Heals aren't touched.")
        for lo, hi, jp, jl, jh in ((0.60, 1.05, 0.20, 1.20, 1.60),
                                   (0.30, 1.05, 0.20, 1.30, 2.20),
                                   (0.01, 1.10, 0.20, 1.50, 3.00))])
    # RISKY CAPSTONES. Kyle, 14 Nov 2026: "I'm also partial to the idea of risky tanking. Like
    # Capstone rune that adds 25% dodge but makes you take 30% more physical damage. Or the inverse
    # where dodge falls to 0 but you take 30% less physical damage. Things like this." All-in bets,
    # bigger than a regular rune's trade-off, for tanks and everyone else.
    def risky(cid, name, ranks, words):
        C[cid] = (name, [({"kind": "stats", "effects": fx}, words(i, fx)) for i, fx in enumerate(ranks)])
    risky("dancer", "the Dancer",
          [{"dodge_rating": d, "physical_damage_taken_pct": p} for d, p in ((8, 0.10), (16, 0.20), (25, 0.30))],
          lambda i, fx: f"You dodge {fx['dodge_rating']}% more often, but take {int(fx['physical_damage_taken_pct'] * 100)}% more physical damage.")
    risky("anvil", "the Anvil",
          [{"rune_no_dodge": 1, "physical_damage_taken_pct": -p} for p in (0.10, 0.20, 0.30)],
          lambda i, fx: f"You never dodge, but take {int(-fx['physical_damage_taken_pct'] * 100)}% less physical damage.")
    risky("colossus", "the Colossus",
          [{"max_health_pct": h, "healing_received_pct": -r} for h, r in ((0.20, 0.15), (0.35, 0.25), (0.50, 0.35))],
          lambda i, fx: f"Your health is {int(fx['max_health_pct'] * 100)}% higher, but heals on you are {int(-fx['healing_received_pct'] * 100)}% weaker.")
    risky("mirror", "the Mirror",
          [{"magic_damage_taken_pct": -m, "physical_damage_taken_pct": p} for m, p in ((0.10, 0.08), (0.20, 0.15), (0.30, 0.20))],
          lambda i, fx: f"You take {int(-fx['magic_damage_taken_pct'] * 100)}% less magic damage, but {int(fx['physical_damage_taken_pct'] * 100)}% more physical.")
    risky("glass_cannon", "the Glass Cannon",
          [{"all_damage": d, "damage_taken_pct": d} for d in (0.10, 0.18, 0.25)],
          lambda i, fx: f"You deal {int(fx['all_damage'] * 100)}% more damage, and take {int(fx['damage_taken_pct'] * 100)}% more.")
    risky("blood_rite", "the Blood Rite",
          [{"healing_done": h, "max_health_pct": -l} for h, l in ((0.10, 0.10), (0.18, 0.15), (0.25, 0.20))],
          lambda i, fx: f"Your heals are {int(fx['healing_done'] * 100)}% stronger, but your health is {int(-fx['max_health_pct'] * 100)}% lower.")
    risky("hunger", "the Hunger",
          [{"all_ability_cost_pct": c, "max_mana_pct": -m} for c, m in ((0.15, 0.15), (0.25, 0.25), (0.35, 0.35))],
          lambda i, fx: f"Abilities cost {int(fx['all_ability_cost_pct'] * 100)}% less, but your mana pool is {int(-fx['max_mana_pct'] * 100)}% smaller.")
    # THE ECHO. Kyle, 14 Nov 2026: "an overload rune... that rewards high crit characters. You deal
    # 25% less damage but crits will cast the same spell a second time. This spell can not critically
    # hit. (Obviously doesn't work with dots)." General, so weapon strikes echo too.
    C["echo"] = ("the Echo", [
        ({"kind": "echo", "chance": ch, "effects": {"all_damage": -pen}},
         f"{int(ch * 100)}% of your critical hits land a second time at normal size (the echo can't crit). "
         f"DoTs don't echo. But you deal {int(pen * 100)}% less damage.")
        for ch, pen in zip(CAPSTONE_CHANCE, (0.10, 0.18, 0.25))])
    C["renewal"] = ("Renewal", [
        ({"kind": "heal_to_hot", "chance": ch, "mult": 1.25, "turns": 3},
         f"{int(ch * 100)}% of your direct heals become a HoT over 3 turns that heals 25% more in total.")
        for ch in CAPSTONE_CHANCE])
    C["surge"] = ("Surge", [
        ({"kind": "hot_to_heal", "chance": ch, "mult": 0.85},
         f"{int(ch * 100)}% of your HoTs land all at once, healing 85% of their total.")
        for ch in CAPSTONE_CHANCE])
    C["detonation"] = ("Detonation", [
        ({"kind": "dot_to_hit", "chance": ch, "mult": 0.90},
         f"{int(ch * 100)}% of your DoTs hit all at once for 90% of their total.")
        for ch in CAPSTONE_CHANCE])
    return C


def icon_for(n):
    icons = sorted(p.name for p in ICON_SRC.glob("runemaster_*.png"))
    return icons[n % len(icons)]


def main():
    doc = load(MATS)
    mats = doc["materials"]
    for k in [k for k, v in mats.items() if v.get("profession") == "runecrafting"]:
        del mats[k]
    ART.mkdir(parents=True, exist_ok=True)

    runes, recipes = {}, {}

    # ---- inks
    for iid, name, skill, dust, vial in INKS:
        mats[iid] = {"name": name, "material_type": "rune_ink", "profession": "runecrafting", "tier": "early",
                     "description": f"Ground {mats[dust]['name'].lower()} in oil. Runes of this tier are written with it.",
                     "stack_limit": 20, "sell_price": mats[dust]["sell_price"] * 2, "icon_id": iid}
        src = ROOT / "assets/icons/consumables/minor_mana_oil.png"
        if src.exists() and not (ART / f"{iid}.png").exists():
            shutil.copyfile(src, ART / f"{iid}.png")
        recipes[f"rc_{iid}"] = {"name": name, "inputs": {dust: 2, vial: 1}, "skill_required": skill,
                                "output": {"kind": "material", "material_id": iid}, "count": 1,
                                "skill_range": skill_range(skill), "source": "trainer"}

    n = 0
    # ---- regular runes
    for fam_i, (fid, (fname, ranks, role)) in enumerate(normal_runes().items()):
        icon = f"rune_{fid}"
        if not (ART / f"{icon}.png").exists():
            shutil.copyfile(ICON_SRC / icon_for(n), ART / f"{icon}.png")
        n += 1
        for r, (effects, procs, words) in enumerate(ranks):
            level, base, ink, ess, shard = NORMAL_TIERS[r]
            rid = f"rune_{fid}_{r + 1}"
            title = f"{RANKS[r]} Rune of {fname}".strip()
            runes[rid] = {"name": title, "family": fid, "rank": r + 1, "capstone": False, "role": role,
                          "level": level, "effects": effects, "procs": procs, "text": words}
            skill = min(300, base + (fam_i % 5) * 8)
            inp = {ink: 1, ess: 1 + r}
            if shard:
                inp[shard] = 1
            recipes[f"rc_{rid}"] = {"name": title, "inputs": inp, "skill_required": skill,
                                    "output": {"kind": "material", "material_id": rid}, "count": 1,
                                    "skill_range": skill_range(skill),
                                    # Kyle's 50-55% trainer rule: every Lesser rune, a third of the plain
                                    # ones and half the Greater ones are taught; the rest are found
                                    "source": "trainer" if (r == 0 or (r == 1 and fam_i % 3 == 0)
                                                            or (r == 2 and fam_i % 2 == 0))
                                              else ("vendor" if (fam_i + r) % 2 else "drop")}
    # ---- Capstones
    for fam_i, (fid, (fname, ranks)) in enumerate(capstones().items()):
        icon = f"rune_{fid}"
        if not (ART / f"{icon}.png").exists():
            shutil.copyfile(ICON_SRC / icon_for(n * 3 + 1), ART / f"{icon}.png")
        n += 1
        for r, (cap, words) in enumerate(ranks):
            level, base, ink, ess, shard = CAPSTONE_TIERS[r]
            rid = f"capstone_{fid}_{r + 1}"
            title = f"{RANKS[r]} Capstone Rune of {fname}".strip()
            cap = dict(cap)
            runes[rid] = {"name": title, "family": fid, "rank": r + 1, "capstone": True,
                          "level": level, "effects": cap.pop("effects", {}), "procs": [],
                          "capstone_effect": cap, "text": words}
            skill = min(300, base + (fam_i % 4) * 4)
            inp = {ink: 2, ess: 2 + r, shard: 1 if r < 2 else 1}
            recipes[f"rc_{rid}"] = {"name": title, "inputs": inp, "skill_required": skill,
                                    "output": {"kind": "material", "material_id": rid}, "count": 1,
                                    "skill_range": skill_range(skill),
                                    "source": "trainer" if r == 0 else ("vendor" if (r + fam_i) % 2 else "drop")}

    for rid, rn in runes.items():
        mats[rid] = {"name": rn["name"], "material_type": "rune", "profession": "runecrafting", "tier": "early",
                     "description": rn["text"] + (" A Capstone: one per soul." if rn["capstone"] else "")
                                    + f" Imprint it on a soul (level {rn['level']}) from the Soul screen.",
                     "stack_limit": 5, "sell_price": rn["level"] * (60 if rn["capstone"] else 25),
                     # each rank has its own tinted icon (tools/slice_rune_sheets.py) once the art is in
                     "icon_id": rid if (ART / f"{rid}.png").exists() else f"rune_{rn['family']}"}
    for r in recipes.values():
        for m in r["inputs"]:
            assert m in mats, f"{r['name']}: no material {m}"

    profs = load(PROFS)
    profs["professions"]["runecrafting"] = {
        "name": "Runecrafting", "kind": "crafting",
        "description": "Write runes from enchanting dust and essence, and imprint them on a soul: three "
                       "runes and one Capstone each, for you and every companion."}
    save(PROFS, profs)
    tr = load(TRAINERS)
    for nid in TRAINER_NPCS:
        plist = tr["profession_trainers"].setdefault(nid, [])
        for p in ("enchanting", "runecrafting"):
            if p not in plist:
                plist.append(p)
    save(TRAINERS, tr)
    for path in (ROOT / "data/npcs/ambient_npcs.json", ROOT / "data/npcs/vendors.json"):
        d = load(path)
        for row in d.get("npcs") or d.get("vendors") or []:
            if (row.get("npc_id") or row.get("vendor_id")) in TRAINER_NPCS:
                row["trains_profession"] = ["enchanting", "runecrafting"]
        save(path, d)

    save(MATS, doc)
    save(OUT_RUNES, {"_doc": "Written by tools/build_runecrafting.py; read by world/runes.py.",
                     "slots": 4, "capstone_slot": 3, "runes": runes})
    save(OUT_RECIPES, {"_comment": "Runecrafting. Written by tools/build_runecrafting.py.", "recipes": recipes})
    by = {}
    for r in recipes.values():
        by[r["source"]] = by.get(r["source"], 0) + 1
    caps = sum(1 for r in runes.values() if r["capstone"])
    print(f"{len(runes) - caps} runes and {caps} Capstones in {len(set(r['family'] for r in runes.values()))} "
          f"families, {len(recipes)} recipes {by} ({100 * by['trainer'] // len(recipes)}% trainer)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
