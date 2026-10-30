#!/usr/bin/env python3
"""Rework boss ability kits so bosses stop being "glorified punching bags" (Kyle, 2026-10-24).

The problem: ~2/3 of the 216 bosses had kits of  basic attack + a weak 3-4 turn self-buff (+20 Attack Power, +24 Armor)
+ a weak debuff/DoT.  The monster AI recast the buff every time it lapsed, so a typical boss spent 12% of its turns
(some 43%) doing nothing but buffing itself.

What this does (idempotent; reads the pre-rework kit from tools/boss_kits_base.json):
  * every pure self-buff becomes an ATTACK that grants the same buff as a rider  ("Bloodlust" now hits you AND enrages)
  * every pure debuff becomes an ATTACK that applies the same debuff as a rider  ("Meat Hook" now hits AND sunders)
    
  * DoTs, heals, AoEs and existing damage abilities are kept untouched
  * bosses with fewer than 4 attacks get a signature heavy hit (and an AoE if still short), school-flavoured
  * every boss without a heal gets a one-shot PHASE ability at 35% health: an enrage that adds +60% of its basic
    attack to every hit for the rest of the fight
  * bosses whose kit is shared with ordinary mobs get their own copy (boss_<slug>), creatures.json points at it

Run after tools/generate_creatures.py (which regenerates the raw kits):   python3 tools/rework_boss_kits.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CREAT = ROOT / "data" / "creatures" / "creatures.json"
KITS = ROOT / "data" / "creatures" / "ability_kits.json"
TEMPL = ROOT / "data" / "creatures" / "templates.json"
BASE = ROOT / "tools" / "boss_kits_base.json"

RIDER_SCALE = 1.0
BUFF_STRIKE = 0.8         # x basic attack amount (tuned with the boss simulator: bosses end up ~+23% damage/turn,
DEBUFF_STRIKE = 0.65      # almost all of it from no longer wasting turns)
HEAVY_MULT = 1.3
AOE_MULT = 0.7
MIN_ATTACKS = 4          # basic + 3 distinct attacks, not counting the phase ability
ENRAGE_HP = 0.35
ENRAGE_AP_RATIO = 0.60

HEAVY = {"physical": "Crushing Blow", "fire": "Searing Blast", "frost": "Frost Lance", "nature": "Thorned Lash",
         "shadow": "Shadow Rend", "arcane": "Arcane Burst", "holy": "Holy Smite"}
AOE = {"physical": "Sweeping Cleave", "fire": "Fire Nova", "frost": "Frost Nova", "nature": "Thrashing Storm",
       "shadow": "Wave of Dread", "arcane": "Arcane Wave", "holy": "Consecrated Wave"}
ENRAGE = {"physical": "Enrage", "fire": "Inferno Surge", "frost": "Killing Chill", "nature": "Wild Surge",
          "shadow": "Dark Frenzy", "arcane": "Arcane Overload", "holy": "Zealous Fury"}


def slug(name):
    return re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")


def scaled_mods(mods):
    out = {}
    for k, v in (mods or {}).items():
        out[k] = int(round(v * RIDER_SCALE)) if abs(v) >= 1 else v
    return out


def strike(src, amount, cooldown, effect):
    return {
        "name": src["name"], "kind": "damage", "amount": amount, "cooldown": cooldown, "mana_cost": src.get("mana_cost", 0),
        "school": src.get("school", "physical"),
        "rider": {"effect": effect, "duration": max(3, src.get("duration", 3)), "stat_mods": scaled_mods(src.get("stat_mods"))},
    }


def rework(kit):
    """-> new kit list from a raw (pre-rework) kit."""
    basic = dict(kit[0])
    base = max(1, basic["amount"])
    out = [basic]
    school_amount = {}
    for e in kit[1:]:
        e = dict(e)
        if e["kind"] == "buff":
            out.append(strike(e, int(round(base * BUFF_STRIKE)), max(3, e.get("cooldown", 5) - 2), "buff"))
        elif e["kind"] == "debuff" and not e.get("self_only"):
            out.append(strike(e, int(round(base * DEBUFF_STRIKE)), max(3, e.get("cooldown", 4) - 1), "debuff"))
        else:
            out.append(e)
    for e in out:
        if e["kind"] == "damage":
            school_amount[e["school"]] = school_amount.get(e["school"], 0) + e["amount"]
    school = max(school_amount, key=school_amount.get) if school_amount else "physical"
    school = {"lightning": "nature"}.get(school, school)
    if school not in HEAVY:
        school = "arcane"          # legacy generic "magic" school
    names = {e["name"] for e in out}

    def add(entry):
        if entry["name"] in names:
            entry["name"] += " II"
        names.add(entry["name"])
        out.append(entry)

    def attacks():
        return sum(1 for e in out if e["kind"] == "damage")

    if attacks() < MIN_ATTACKS:
        add({"name": HEAVY[school], "kind": "damage", "amount": int(round(base * HEAVY_MULT)), "cooldown": 4, "mana_cost": 0,
             "school": school})
    if attacks() < MIN_ATTACKS:
        add({"name": AOE[school], "kind": "damage", "amount": int(round(base * AOE_MULT)), "cooldown": 5, "mana_cost": 0,
             "school": school, "is_aoe": True})
    if not any(e["kind"] == "heal" for e in out):
        add({"name": ENRAGE[school], "kind": "buff", "amount": 0, "cooldown": 99, "mana_cost": 0, "school": school,
             "duration": 30, "self_only": True, "hp_below": ENRAGE_HP,
             "stat_mods": {"attack_power": int(round(base * ENRAGE_AP_RATIO))}})
    out[0]["boss_rework"] = 1
    return out


def main(dry=False):
    creatures = json.loads(CREAT.read_text())
    kits_doc = json.loads(KITS.read_text())
    kits = kits_doc["kits"]
    tmpl = json.loads(TEMPL.read_text())["templates"]
    base_store = json.loads(BASE.read_text()) if BASE.exists() else {}

    def kit_of(c):
        return c.get("ability_kit") or tmpl[c["template"]].get("default_kit")

    #: kits that arrived already in their final form and must not be reworked again
    prebuilt = set()

    def raw_kit(kid):
        k = kits[kid]
        if k and k[0].get("boss_rework"):
            # HAND-AUTHORED BOSS KITS EXIST AND THIS USED TO CRASH ON THEM.
            #
            # boss_rework was treated as proof that THIS script had reworked the kit, so the
            # untouched original must be sitting in base_store. That is true for everything this
            # script generates and false for everything the per-zone content builders write: they
            # author boss kits straight into ability_kits.json already carrying boss_rework, and
            # this script has never seen those, so the lookup raised KeyError - on
            # bosun_harl_greave, which took down the whole run and with it every boss kit after it
            # in the loop. Hezrul Bloodmark's kit was simply never generated as a result.
            #
            # A kit flagged as reworked with no cached original was authored in its final form.
            # It is not an error and it must not be run through rework() a second time, which
            # would stack another enrage phase on top of the one it already has.
            if kid not in base_store:
                prebuilt.add(kid)
                return k
            return base_store[kid]
        base_store[kid] = k           # fresh / regenerated raw kit: remember it
        return k

    # who else uses a kit besides bosses?
    nonboss_use = {kit_of(c) for c in creatures["creatures"].values() if not c.get("is_boss")}
    done = {}
    changed = 0
    for name, c in creatures["creatures"].items():
        if not c.get("is_boss"):
            continue
        base_id = c.get("boss_kit_base") or kit_of(c)
        if base_id in nonboss_use:
            target = "boss_" + slug(name)
            c["ability_kit"] = target
            c["boss_kit_base"] = base_id
            if target in kits and kits[target][0].get("boss_rework"):
                src = base_store[target]
            else:
                src = kits[base_id]
                base_store[target] = src
        else:
            target = base_id
            src = raw_kit(target)
            # AND POINT THE CREATURE AT IT. This branch used to leave ability_kit alone, which is
            # harmless for every boss whose ability_kit already equals its base - i.e. all of them,
            # until one does not. Hezrul Bloodmark carried ability_kit "boss_hezrul_bloodmark" from
            # an earlier run, back when his base kit WAS shared with trash; once it stopped being
            # shared he fell down here, the boss_ kit was never regenerated, and nothing updated him
            # to say so. He pointed at a kit that did not exist and crashed on spawn - the single
            # creature in the game that could not be summoned.
            c["ability_kit"] = target
        if target not in done:
            kits[target] = src if target in prebuilt else rework(src)
            done[target] = name
            changed += 1
    if not dry:
        KITS.write_text(json.dumps(kits_doc, indent=2))
        CREAT.write_text(json.dumps(creatures, indent=2) + "\n")
        BASE.write_text(json.dumps(base_store, indent=1) + "\n")
    print(f"reworked {changed} boss kits" + (" (dry run)" if dry else ""))
    return done


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
