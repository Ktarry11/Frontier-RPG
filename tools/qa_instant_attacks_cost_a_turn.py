#!/usr/bin/env python3
"""Only cooldown buffs are free actions. Everything else ends the turn.

    PYTHONPATH=. python3 tools/qa_instant_attacks_cost_a_turn.py

Playtest, 12 Nov: "Can chain multiple maul attacks and just keep going until my rage is empty." Maul was
marked instant, and instant means the cast does not end your turn. The fix named three effect types.

Playtest, 15 Nov: "His searing pain is instant and I can just rapid fire him to oom". Searing Pain is
"spell_damage", a fourth type, and walked past - as did Polymorph, Fear, Charge, every instant heal and
every pet summon. Kyle: "I meant only to have buffs like icy veins, or power infusion etc. Or natures
swiftness."

  1. Every ability that is still instant - class kits, recruit kits, racials and pet abilities - is a
     free action by the rule: a buff, a next-cast-instant, a cooldown reset or a resource burst, aimed at
     your own side, with a real cooldown.
  2. The ones from the playtests are not free: Searing Pain, Maul, Ice Lance, Polymorph, Fear, Swiftmend.
     The ones Kyle named still are: Icy Veins, Nature's Swiftness.
  3. In a real fight: Searing Pain hands the turn on; Icy Veins doesn't.
"""
import glob
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

COST_THE_TURN = ["warlock_searing_pain", "druid_maul", "mage_ice_lance", "mage_polymorph", "warlock_fear",
                 "druid_swiftmend", "warlock_conflagrate", "warrior_charge"]
STAY_FREE = ["mage_icy_veins", "druid_natures_swiftness"]


def entries():
    out = []
    paths = sorted(glob.glob("data/abilities/*.json")) + ["data/npcs/personal_kits.json", "data/races/racials.json"]
    nodes = [json.load(open(p, encoding="utf-8")) for p in paths if os.path.exists(p)]
    from combat import pet_templates
    nodes.append({k: v for k, v in vars(pet_templates).items() if isinstance(v, (dict, list))})
    while nodes:
        node = nodes.pop()
        if isinstance(node, dict):
            if "ability_id" in node and "effect_type" in node:
                out.append(node)
            else:
                nodes.extend(node.values())
        elif isinstance(node, list):
            nodes.extend(node)
    return out


def main():
    from combat.abilities import _ability_from_data, is_free_action
    bad = []
    built = {}
    authored = still = 0
    for e in entries():
        try:
            ab = _ability_from_data(e)
        except Exception:
            continue
        built.setdefault(ab.ability_id, ab)
        authored += bool(e.get("is_instant"))
        if ab.is_instant:
            still += 1
            if not is_free_action(ab.effect_type, ab.target_type, ab.cooldown):
                bad.append(f"{ab.name} ({ab.ability_id}, {ab.effect_type}, cd {ab.cooldown}) is a free action")
    print(f"1. {len(built)} abilities read; {authored} authored instant, {still} still free actions, "
          f"all of them cooldown buffs")

    for aid in COST_THE_TURN:
        ab = built.get(aid)
        if ab is None:
            bad.append(f"{aid} is not in the data")
        elif ab.is_instant:
            bad.append(f"{ab.name} is still a free action")
    for aid in STAY_FREE:
        ab = built.get(aid)
        if ab is None:
            bad.append(f"{aid} is not in the data")
        elif not ab.is_instant:
            bad.append(f"{ab.name} should stay a free action")
    print(f"2. checked {len(COST_THE_TURN)} that must cost the turn and {len(STAY_FREE)} that stay free")

    # 3. a real fight
    from entities.character import Character
    from entities.monster import Monster
    from combat.combat_engine import CombatEngine

    def turn_after(char_class, aid):
        p = Character(name="Tester", char_class=char_class, level=60)
        p.current_mana = p.mana
        dummy = Monster("Target Dummy", "beast_basic", level=60)
        dummy.current_health = dummy.max_health = 100000
        ce = CombatEngine(p, dummy)
        if not p.ability_book.get_ability(aid):
            p.ability_book.add_ability(built[aid])
        p.ability_book.get_ability(aid).is_learned = True     # Icy Veins is a talent; skip the tree
        ce.current_actor = p
        ce.combat_phase = "action"
        ok, msg = ce.execute_ability(p, aid, p if built[aid].target_type == "self" else dummy)
        return ok, msg, ce.current_actor is p

    ok, msg, kept = turn_after("Warlock", "warlock_searing_pain")
    if not ok:
        bad.append(f"Searing Pain didn't cast in the fight test: {msg}")
    elif kept:
        bad.append("in a fight, Searing Pain left the warlock with the turn")
    ok, msg, kept = turn_after("Mage", "mage_icy_veins")
    if not ok:
        bad.append(f"Icy Veins didn't cast in the fight test: {msg}")
    elif not kept:
        bad.append("in a fight, Icy Veins ended the mage's turn")
    print("3. in a fight: Searing Pain hands the turn on, Icy Veins keeps it")

    if bad:
        print(f"\nFAILED - {len(bad)}:")
        for b in bad:
            print("  -", b)
        return 1
    print("\nfree actions OK - only cooldown buffs skip the end of the turn.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
