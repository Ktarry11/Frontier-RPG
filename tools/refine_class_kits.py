#!/usr/bin/env python3
"""The spellbook refine pass: fewer, better buttons for a turn-based game.

    PYTHONPATH=. python3 tools/refine_class_kits.py [--check]

Kyle, 14 Nov 2026: "we don't need every single ability as they become too heavy. I mean look at
runemaster. So abilities need to be refined for turn based, 'usable while moving' is pointless.
Some CoA are coming off as clunky messes."

So the CoA port is trimmed class by class. For each class below:
  CUT     abilities that leave the game: a near-duplicate of something kept, a stance that repeats
          another stance, a rider that only means something in real time. The entry leaves the
          class file and the spellbook tabs, any talent number that only tuned it goes with it, and
          it is listed in data/reference/retired_abilities.json so an old save drops it off the hotbar.
  REWORD  description fixes, mostly deleting real-time clauses ("Usable while moving.").
  PASSIVE a talent node that used to unlock a cut ability becomes a passive that strengthens what
          is left, so a tree keeps its shape, its tiers and its point count.

Idempotent: running it again changes nothing. --check reports what it would do and exits 1 if
anything is still to be done.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
AB = ROOT / "data" / "abilities"
TABS = ROOT / "data" / "spellbook_tabs_coa.json"
TALENTS = ROOT / "data" / "talents"
RETIRED = ROOT / "data" / "reference" / "retired_abilities.json"

#: real-time clauses that mean nothing on a turn-based board
REALTIME = [r"\s*Usable while (?:moving|stealthed|stunned|casting)[^.]*\.",
            r"\s*Cannot move while active[^.]*\.", r"\s*Can be cast while moving[^.]*\."]

def P(name, description, effects, drop_proc=False):
    """A talent node rewritten as a passive."""
    out = {"name": name, "description": description, "node_type": "passive", "effects": effects,
           "_refined": "14 Nov 2026 spellbook refine (tools/refine_class_kits.py)"}
    if drop_proc:
        out["proc"] = None
    return out


CLASSES = {
    "Runemaster": {
        "CUT": {
            # baseline: stances and riders that repeat each other
            "runemaster_weapon_engraving_earth": "five Weapon Engravings is four choices nobody makes; Fire, Ice and Air stay",
            "runemaster_weapon_engraving_water": "five Weapon Engravings is four choices nobody makes; Fire, Ice and Air stay",
            "runemaster_runic_tattoos_frost": "slows attackers, a movement effect; Earth (armour) and Water (mana) stay",
            "runemaster_runic_tattoos_air": "haste again - the Air Engraving already does it",
            "runemaster_palm_sigil_fire": "a next-spell rider that costs a turn to set up; Earth (stun) and Arcane (silence) stay",
            "runemaster_palm_sigil_water": "a next-spell rider that costs a turn to set up; Earth (stun) and Arcane (silence) stay",
            "runemaster_palm_sigil_frost": "a next-spell rider that costs a turn to set up; Earth (stun) and Arcane (silence) stay",
            "runemaster_etching_of_the_dextrous": "+10 Agility to the party when Etching of the Leylines gives +10% to everything",
            "runemaster_inscription_leyline": "a debuff you put on your own ally",
            "runemaster_leyline_adjustment": "a threat redirect at level 60",
            # talent unlocks: a second of something each tree already has
            "runemaster_manuscription": "a second Glyphic AoE beside Primordial Pulse",
            "runemaster_devour_mana": "a mana burn in a game where few enemies run on mana",
            "runemaster_silencing_rune": "a delayed silence zone when Ley Lock already interrupts",
            "runemaster_rune_master": "a third burst cooldown that also says 'cannot move'",
            "runemaster_runic_tempest": "a button that only resets Fist of the Ancients",
            "runemaster_runes_of_quickness": "a second haste aura beside Leyline Disturbance",
            "runemaster_resonance_rune": "an area dispel when Leyfeed already dispels",
            "runemaster_power_engraving": "a third damage zone",
            "runemaster_turbulence": "a second Nature AoE zone beside Hurricane",
            "runemaster_echo_rune": "'warp back to your mark' means nothing on a turn-based board",
            "runemaster_ley_power_riftblade": "a copy of Engravement's Ley Power",
            "runemaster_elder_magi_rune": "a third Riftblade AoE",
            "runemaster_runecarve": "clears Sigils to no purpose",
            "runemaster_aspect_of_the_rune_knight": "an Aspect stance on top of Tattoos and Engravings",
        },
        "REWORD": {},
        "PASSIVE": {
            # Glyphic
            "runemaster_glyphic_manuscription": P("Lingering Script", "Primordial Pulse deals 15% more damage.",
                                                  {"ability_runemaster_primordial_pulse_damage": 0.15}),
            "runemaster_glyphic_devour_mana": P("Leyline Thirst", "Primordial Blast deals 8% more damage.",
                                                {"ability_runemaster_primordial_blast_damage": 0.08}),
            "runemaster_glyphic_silencing_rune": P("Silent Script", "Ley Lock's cooldown is 1 turn shorter.",
                                                   {"ability_runemaster_ley_lock_cooldown": 1}),
            "runemaster_glyphic_rune_master": P("Rune Master", "Your spells have 3% more critical strike chance.",
                                                {"crit_chance_spell": 3.0}),
            # Engravement
            "runemaster_engravement_runic_tempest": P("Ancient Momentum", "Fist of the Ancients' cooldown is 1 turn shorter.",
                                                      {"ability_runemaster_fist_of_the_ancients_cooldown": 1}),
            "runemaster_engravement_leyline_disturbance_boost": P("Quickened Leylines", "Increases your haste by 2.",
                                                                  {"haste": 2.0}),
            "runemaster_engravement_resonance_rune": P("Resonant Wards", "Guarding Rune's cooldown is 20% shorter.",
                                                       {"ability_runemaster_guarding_rune_cooldown_pct": 0.2}),
            "runemaster_engravement_power_engraving": P("Power Engraving", "Your Arcane, Fire, Frost and Nature damage is increased by 4%.",
                                                        {"arcane_fire_frost_nature_damage_pct": 0.04}),
            "runemaster_engravement_rune_of_the_kirin_tor": P("Rune of the Kirin Tor", "Zenith lasts 2 turns longer.",
                                                              {"ability_runemaster_zenith_duration": 2}, drop_proc=True),
            # Riftblade
            "runemaster_riftblade_echo_rune": P("Echoing Ward", "Augur's Shield's cooldown is 20% shorter.",
                                                {"ability_runemaster_augurs_shield_cooldown_pct": 0.2}),
            "runemaster_riftblade_turbulence": P("Gale Force", "Hurricane deals 15% more damage.",
                                                 {"ability_runemaster_hurricane_damage": 0.15}),
            "runemaster_riftblade_aspect_of_the_rune_knight": P("Rune Knight's Bearing", "Increases your maximum Mana by 4%.",
                                                                {"max_mana_pct": 0.04}),
            "runemaster_riftblade_ley_power": P("Riftborn Fury", "Your attacks have 2% more critical strike chance.",
                                                {"crit_chance_physical": 2.0}),
            "runemaster_riftblade_elder_magi_rune": P("Elder Runes", "Hoarfrost deals 10% more damage.",
                                                      {"ability_runemaster_hoarfrost_damage": 0.1}),
            "runemaster_riftblade_runecarve": P("Carved Edge", "Your attacks have 1% more critical strike chance.",
                                                {"crit_chance_physical": 1.0}),
        },
    },
    # Bloodmage had 65 buttons and no talent unlocks - every one of them on every Bloodmage. Four specs
    # (Sanguine caster, Accursed melee, Eternal tank, Fleshweaver healer) each had a second of
    # something. The talents say what each spec is built around (the three Blood Princes, Vampiric
    # Fang, Sanguine Rupture, Crimson Tide), so those stay and the copies beside them go.
    "Bloodmage": {
        "CUT": {
            "bloodmage_transfusion": "a second single-target heal beside Fleshcraft and Sanguine Mend",
            "bloodmage_shadow_howl": "crowd-control immunity again - Blood Craving does it",
            "bloodmage_wicked_howl": "+25% max health again - Eternal Resolve does it",
            "bloodmage_aneurysm": "a 1-turn interrupt beside Hemostasis's 2-turn one",
            "bloodmage_scarlet_delirium": "one of five area DoTs; every spec keeps its own",
            "bloodmage_hypovolemic_shock": "a third single-target DoT",
            "bloodmage_ravenous_bite": "the same leeching bite as Ravenous Strike",
            "bloodmage_bare_fangs": "a threat button beside Eternal's Blood Howl",
            "bloodmage_blood_cursed_armor": "a self armour buff on the healing spec",
            "bloodmage_sacrificial_rite": "a third Sanguine cooldown",
            "bloodmage_puncturing_fangs": "a second plain Accursed strike beside Crimson Maw",
            "bloodmage_hemoburst": "Veinburst again, later",
            "bloodmage_infuse": "a second Fleshweaver DoT beside Vampyr's Kiss",
        },
        "REWORD": {},
        "PASSIVE": {},
        "TALENT_TEXT": {
            "Cursed Strikes": "Increases the damage of Rotclaw by up to 27%.",
        },
    },
    # Witch Hunter: four specs (Black Knight tank, Boltslinger ranged, Houndmaster pets, Inquisition
    # melee), 53 buttons on everyone. Cut what no talent is built around and something else covers.
    "Witch Hunter": {
        "CUT": {
            "witch_hunter_burrow_bolt": "a fourth plain ranged shot",
            "witch_hunter_vampiric_tonic": "an unnamed self-buff no talent touches",
            "witch_hunter_death_trap": "a third trap that is just a DoT",
            "witch_hunter_knights_seal": "a second Black Knight Shadow DoT beside Shadow Brand",
            "witch_hunter_daring_escape": "Vault again, a little bigger",
            "witch_hunter_hunt": "a plain Inquisition strike with nothing of its own",
            "witch_hunter_darkslayers_lantern": "an area stun beside Shadow Trap's",
        },
        "REWORD": {},
        "PASSIVE": {
            "witch_hunter_boltslinger_escape_artist": P("Escape Artist", "Vault's cooldown is 1 turn shorter.",
                                                        {"ability_witch_hunter_vault_cooldown": 0.34}, drop_proc=True),
            "witch_hunter_inquisition_the_hunt_continues": P("The Hunt Continues", "Purifier's Edge costs 15% less Focus.",
                                                             {"ability_witch_hunter_purifiers_edge_cost_pct": 0.05}, drop_proc=True),
            "witch_hunter_inquisition_duskwood_renegade": P("Duskwood Renegade", "Shadowblast deals 6% more damage.",
                                                            {"ability_witch_hunter_shadowblast_damage": 0.02}),
        },
        "TALENT_TEXT": {
            "Calm Under Pressure": "Reduces the cooldown of Stoicism by 39%.",
        },
    },
    # Ranger: 53 buttons. Farstrider alone carried eight party buffs; Brigand four plain strikes.
    "Ranger": {
        "CUT": {
            "ranger_snatch": "a small Attack Power debuff no talent touches",
            "ranger_cutthroat": "a damage-and-stun beside Knockout's interrupt-and-stun",
            "ranger_skirmish": "Elude again (+15% crit)",
            "ranger_backstep": "a smaller Briar Veil",
            "ranger_brutal_shot": "a third Archery area shot between Hunting Shot and Incendiary Shot",
            "ranger_rusty_shiv": "a plain strike beside Wild Strike",
            "ranger_hookshot": "a plain strike with nothing of its own",
            "ranger_outmaneuver": "a plain strike with nothing of its own",
            "ranger_bushwhack": "a damage-and-stun beside Knockout",
            "ranger_battle_prowess": "+2 hit as a party buff, beside four better ones",
            "ranger_defense_of_the_ancients": "a party armour buff on the archer spec",
            "ranger_queldorei_poison": "a second Farstrider DoT beside Thalassian Brand",
            "ranger_falcons_call": "a third slow beside Crippling Shot and Throatpunch",
        },
        "REWORD": {},
        "PASSIVE": {},
        "TALENT_TEXT": {
            "Excessive But Necessary": "Reduces the cooldown of Elude and Knockout by 36%.",
        },
    },
    # Witch Doctor: 50 buttons, six of them personal defensives and five party buffs.
    "Witch Doctor": {
        "CUT": {
            "witch_doctor_mirage": "a fourth personal defensive (threat and dodge)",
            "witch_doctor_slither": "a fifth personal defensive (dodge and haste)",
            "witch_doctor_stasis_ward": "a 1-turn area stun beside Amphibimorph's 2-turn interrupt",
            "witch_doctor_swift_idol": "a small party haste buff nothing is built around",
            "witch_doctor_cursed_effigy": "a party damage-reduction buff beside Frog Bones and Big Bad Voodoo",
            "witch_doctor_shadow_avatar": "a core damage cooldown when every spec has its own",
            "witch_doctor_tiki_splash": "a second party heal beside Splash Potion",
            "witch_doctor_base_beast_blood": "a third party damage-reduction buff",
            "witch_doctor_shadowstalker": "a dodge-and-threat escape on the damage spec",
        },
        "REWORD": {},
        "PASSIVE": {},
    },
}


def load(p):
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p, doc, indent=2):
    p.write_text(json.dumps(doc, indent=indent, ensure_ascii=False) + "\n", encoding="utf-8")


def _drop_from_lists(node, cut, fname, tid):
    """Take cut ids out of any list in a talent node (a proc's ability_filter, a cooldown reset).
    A list left empty means the talent only ever touched cut abilities: that needs a PASSIVE."""
    changed = False
    if isinstance(node, dict):
        for v in node.values():
            changed |= _drop_from_lists(v, cut, fname, tid)
    elif isinstance(node, list):
        if any(isinstance(x, str) and x in cut for x in node):
            kept = [x for x in node if not (isinstance(x, str) and x in cut)]
            if not kept:
                raise SystemExit(f"{fname}: {tid} only names cut abilities {node} - give it a PASSIVE")
            node[:] = kept
            changed = True
        for v in node:
            changed |= _drop_from_lists(v, cut, fname, tid)
    return changed


def strip_realtime(text):
    for pat in REALTIME:
        text = re.sub(pat, "", text)
    return text.strip()


def refine(cls, spec, dry):
    todo = []
    prefix = cls.lower().replace(" ", "_")
    path = AB / f"{prefix}.json"
    doc = load(path)
    cut = spec["CUT"]
    keep = [a for a in doc["abilities"] if a["ability_id"] not in cut]
    if len(keep) != len(doc["abilities"]):
        todo.append(f"{cls}: remove {len(doc['abilities']) - len(keep)} abilities")
    for a in keep:
        new = spec["REWORD"].get(a["ability_id"]) or strip_realtime(a.get("description", ""))
        if new != a.get("description", ""):
            todo.append(f"{cls}: reword {a['name']}")
            a["description"] = new
    doc["abilities"] = keep

    tabs = load(TABS)
    t = tabs.get(cls, {})
    gone = [k for k in t if k in cut]
    if gone:
        todo.append(f"{cls}: {len(gone)} spellbook tab entries")
        for k in gone:
            del t[k]

    talent_docs = {}
    for tp in sorted(TALENTS.glob(f"{prefix}_*.json")):
        td = load(tp)
        changed = False
        for n in td.get("nodes", []):
            if n["talent_id"] in spec["PASSIVE"] and n.get("_refined") is None:
                n.update(spec["PASSIVE"][n["talent_id"]])
                if n.get("proc", 0) is None:
                    del n["proc"]
                changed = True
            eff = n.get("effects") or {}
            had = bool(eff)
            for k in list(eff):
                if any(k.startswith(f"ability_{c}_") for c in cut):
                    del eff[k]
                    changed = True
            if had and not eff and not n.get("proc") and n["talent_id"] not in spec["PASSIVE"]:
                raise SystemExit(f"{tp.name}: {n['talent_id']} only tuned cut abilities - give it a PASSIVE")
            if _drop_from_lists(n, cut, tp.name, n["talent_id"]):
                changed = True
            u = eff.get("unlock_ability")
            if u in cut:
                rep = spec["PASSIVE"].get(n["talent_id"])
                if not rep:
                    raise SystemExit(f"{tp.name}: {n['talent_id']} unlocks cut {u} and has no PASSIVE")
                n.update(rep)
                changed = True
            if "proc" in n and n["proc"] is None:
                del n["proc"]
            txt = spec.get("TALENT_TEXT", {}).get(n.get("name"))
            if txt and n.get("description") != txt:
                n["description"] = txt
                changed = True
        if changed:
            todo.append(f"{cls}: talents in {tp.name}")
            talent_docs[tp] = td

    retired = load(RETIRED) if RETIRED.exists() else {"ids": {}}
    new_ret = {k: v for k, v in cut.items() if k not in retired["ids"]}
    if new_ret:
        todo.append(f"{cls}: {len(new_ret)} ids to the retired list")
        retired["ids"].update(new_ret)

    if not dry and todo:
        dump(path, doc)
        dump(TABS, tabs)
        for tp, td in talent_docs.items():
            dump(tp, td)
        retired["_note"] = ("Abilities taken out in the spellbook refine pass (tools/refine_class_kits.py). "
                            "A save that still has one on its hotbar drops it on load.")
        dump(RETIRED, retired)
    return todo


def main():
    dry = "--check" in sys.argv
    todo = []
    for cls, spec in CLASSES.items():
        todo += refine(cls, spec, dry)
    for t in todo:
        print(" ", t)
    print(f"{len(todo)} change(s) {'to make' if dry else 'made'}")
    return 1 if (dry and todo) else 0


if __name__ == "__main__":
    sys.exit(main())
