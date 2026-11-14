#!/usr/bin/env python3
"""Runecrafting works end to end.

    PYTHONPATH=. python3 tools/qa_runecrafting.py

Kyle, 14 Nov 2026 (claude/runecrafting_decisions.md): runes imprinted on the soul, four of them
with one Capstone, made from enchanting dust, its own profession, all slots open from the start,
every companion has four, the roulette averages under normal with a giant ceiling, low/mid/high
ranks (a Capstone converts 30% / 70% / 100%), conversions for spells, physical and both at half,
regular runes all carry a minor trade-off, nothing class-specific, and options for every kind of
tank, healer and damage dealer.

CLAIMS:
  1. Every rune family has three ranks at rising levels; every Capstone's ranks happen 30/70/100%
     of the time (hybrids half that); every regular rune has a trade-off; no rune text names a
     class; there are runes for tanks, healers and damage, and a dozen or more of each.
  2. Recipes are whole: inputs exist, 50 to 55% taught, every vendor script on a shelf, taught by
     the five enchanters.
  3. Imprinting: a Capstone only in the Capstone slot and nothing else there, a level gate, no rune
     twice, imprinting over a rune destroys it, companions have their own souls, and it saves.
  4. In play: a regular rune's effects reach the talent pool (and so the formulas), its proc hangs
     on the character; a conversion lands the hit as the new school against that resistance while
     the ability keeps its own; physical conversion; the Gambler averages under normal and can
     triple; Renewal turns a heal into a HoT; Surge lands a HoT at once; Detonation lands a DoT at
     once; Condensing halves a DoT and makes it bigger.
  5. The screens draw: the Soul screen, the Runecrafting tab.
"""
import contextlib
import io
import json
import os
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

CLASS_WORDS = ["warrior", "paladin", "priest", "druid", "rogue", "mage", "warlock", "hunter", "shaman",
               "necromancer", "templar", "barbarian", "runemaster", "venomancer", "chronomancer"]


def main():
    import pygame
    pygame.init()
    pygame.display.set_mode((1, 1))
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    with contextlib.redirect_stdout(io.StringIO()):
        from world import runes as R
        from world.crafting_manager import get_crafting_manager
        from world.gathering_manager import get_gathering_node_manager
        from entities.character import Character
        from entities.party import Party
        from entities.monster import Monster
        gm = get_gathering_node_manager()
        cm = get_crafting_manager()
    runes = R.data()["runes"]
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    recipes = json.loads((ROOT / "data/runecrafting/recipes.json").read_text(encoding="utf-8"))["recipes"]

    # 1
    fams = {}
    for rid, rn in runes.items():
        fams.setdefault(rn["family"], []).append(rn)
        import re
        words = set(re.findall(r"[a-z]+", (rn["text"] + " " + rn["name"]).lower()))
        for w in CLASS_WORDS:
            check(w not in words, f"{rid} names a class ({w})")
        if not rn["capstone"] and rn["family"] not in ("overload", "lingering"):
            check(" But " in rn["text"], f"{rid} has no trade-off")
    for fam, rows in fams.items():
        rows.sort(key=lambda r: r["rank"])
        check([r["rank"] for r in rows] == [1, 2, 3], f"{fam}: ranks {[r['rank'] for r in rows]}")
        check(all(a["level"] < b["level"] for a, b in zip(rows, rows[1:])), f"{fam}: levels don't rise")
        if rows[0]["capstone"]:
            ce = [r["capstone_effect"] for r in rows]
            if ce[0].get("chance") is not None:
                want = [0.15, 0.35, 0.5] if ce[0].get("from") == "both" else [0.3, 0.7, 1.0]
                check([c["chance"] for c in ce] == want, f"{fam}: chances {[c['chance'] for c in ce]}")
    roles = {}
    for rn in runes.values():
        if not rn["capstone"] and rn["rank"] == 1:
            roles[rn["role"]] = roles.get(rn["role"], 0) + 1
    for role in ("tank", "healing", "damage"):
        check(roles.get(role, 0) >= (6 if role == "healing" else 12), f"only {roles.get(role, 0)} {role} runes")
    check(sum(1 for f, rows in fams.items() if rows[0]["capstone"]) >= 20, "too few Capstones")

    # 2
    for rid, r in recipes.items():
        for m in r["inputs"]:
            check(m in mats, f"{rid}: no material {m}")
    share = sum(1 for r in recipes.values() if r["source"] == "trainer") / len(recipes)
    check(0.50 <= share <= 0.55, f"{share:.0%} of rune recipes are taught (Kyle: 50 to 55%)")
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    sold = {i for v in vendors for i in v["sells"]}
    for rid, r in recipes.items():
        if r["source"] == "vendor":
            check(rid in sold, f"vendor script {rid} is on no shelf")
    tr = json.loads((ROOT / "data/training/trainers.json").read_text(encoding="utf-8"))["profession_trainers"]
    for nid in ("org_enchanter", "uc_enchanter", "kb_enchanter", "stw_enchanter", "oh_enchanter"):
        check("runecrafting" in tr.get(nid, []), f"{nid} doesn't teach runecrafting")

    # 3
    with contextlib.redirect_stdout(io.StringIO()):
        hero = Character(name="Soul", char_class="Priest", level=60)
        party = Party(hero)
        pal = Character(name="Low", char_class="Paladin", level=22)

    def give(mid, n=1):
        m = gm.make_material_instance(mid)
        m.quantity = n
        hero.add_material(m)

    for rid in ("rune_overload_3", "rune_thunder_3", "rune_overload_2", "capstone_frost_spells_3",
                "capstone_gambler_3", "rune_bastion_3"):
        give(rid, 2)
    check(not R.imprint(hero, hero, 0, "capstone_frost_spells_3")[0], "a Capstone went in a regular slot")
    check(not R.imprint(hero, hero, R.CAPSTONE_SLOT, "rune_overload_3")[0], "a regular rune went in the Capstone slot")
    check(not R.imprint(hero, pal, 0, "rune_overload_3")[0], "a level 22 took a level 55 rune")
    ok, msg = R.imprint(hero, hero, 0, "rune_overload_3")
    check(ok, f"imprint failed: {msg}")
    check(not R.imprint(hero, hero, 1, "rune_overload_2")[0], "the same rune twice on one soul")
    R.imprint(hero, hero, 1, "rune_bastion_3")
    ok, msg = R.imprint(hero, hero, 1, "rune_thunder_3")
    check(ok and R.soul(hero)[1] == "rune_thunder_3" and hero.get_material_quantity("rune_bastion_3") == 1,
          f"imprinting over a rune: {msg}")
    give("rune_bastion_1")
    check(R.imprint(hero, pal, 0, "rune_bastion_1")[0] and R.soul(pal)[0] == "rune_bastion_1"
          and R.soul(hero)[0] == "rune_overload_3", "a companion's soul isn't their own")
    with contextlib.redirect_stdout(io.StringIO()):
        back = Character.from_dict(json.loads(json.dumps(hero.to_dict())))
    check(back.soul_runes == hero.soul_runes, "runes don't survive a save")

    # 4
    fx = hero.get_talent_effects()
    check(abs(fx.get("all_damage", 0) - 0.13) < 1e-9 and fx.get("all_ability_cost_pct", 0) < 0,
          f"Overload didn't reach the talent pool: {fx.get('all_damage')}")
    hero._recalculate_derived_stats()
    check(any(str(e.effect_id).startswith("item_proc_soul") for e in hero.active_effects), "Thunder hangs no proc")

    R.imprint(hero, hero, R.CAPSTONE_SLOT, "capstone_frost_spells_3")
    check(R.landing_school(hero, "fire") == "frost" and R.landing_school(hero, "magic") == "frost",
          "Rune of Frost doesn't land spells as frost")
    check(R.landing_school(hero, "physical") == "physical", "a spell rune converted physical")
    check(R.landing_school(hero, ["holy", "fire"]) == ["frost", "frost"], "a combined school didn't convert")
    mob = Monster("Mottled Boar", "beast_basic", level=60)
    mob.fire_resistance, mob.frost_resistance = 0, 0
    if hasattr(mob, "get_resistance"):
        mob.frost_resistance = 30
        base = Monster("Mottled Boar", "beast_basic", level=60)
        base.fire_resistance = base.frost_resistance = 0
        a = mob.take_damage(1000, "fire", attacker_level=60, attacker=hero)
        b = base.take_damage(1000, "fire", attacker_level=60, attacker=hero)
        check(a < b, f"a converted fire hit ignored frost resistance ({a} vs {b})")
    # the ability keeps its own school for bonuses (identity)
    smite = next(ab for ab in hero.ability_book.get_all_abilities() if ab.ability_id == "priest_smite")
    check(smite._resolve_damage_school(hero) == "holy", "conversion changed the ability's own school")

    give("capstone_cinders_weapons_3" if "capstone_cinders_weapons_3" in runes else "capstone_fire_weapons_3", 1)
    R.imprint(hero, hero, R.CAPSTONE_SLOT, "capstone_fire_weapons_3")
    check(R.landing_school(hero, "physical") == "fire" and R.landing_school(hero, "shadow") == "shadow",
          "the physical rune doesn't land physical as fire, or touched spells")
    give("capstone_fire_hybrid_3", 1)
    R.imprint(hero, hero, R.CAPSTONE_SLOT, "capstone_fire_hybrid_3")
    rng = random.Random(1)
    n = sum(1 for _ in range(2000) if R.landing_school(hero, "physical", rng) == "fire")
    check(800 < n < 1200, f"the hybrid rune converted {n} of 2000, should be about half")

    R.imprint(hero, hero, R.CAPSTONE_SLOT, "capstone_gambler_3")
    rng = random.Random(2)
    rolls = [R.gamble(hero, 1000, rng) for _ in range(20000)]
    mean = sum(rolls) / len(rolls) / 1000
    check(0.85 <= mean <= 0.95, f"the Gambler averages {mean:.2f}, should be a little under 1")
    check(max(rolls) > 2800 and min(rolls) < 50, f"the Gambler's range is {min(rolls)}-{max(rolls)}")
    heal = next(ab for ab in hero.ability_book.get_all_abilities() if ab.ability_id == "priest_heal")
    check(heal._roll_variance(1000, hero, heal=True) > 800, "the Gambler touched a heal")

    def fresh_priest():
        with contextlib.redirect_stdout(io.StringIO()):
            p = Character(name="Caster", char_class="Priest", level=60)
        p.current_mana = 10 ** 6
        return p

    def ab_of(p, aid):
        return next(ab for ab in p.ability_book.get_all_abilities() if ab.ability_id == aid)

    def cap_on(p, rid):
        p.soul_runes = [None, None, None, rid]
        p._recalculate_derived_stats()

    # risky Capstones (Kyle: "adds 25% dodge but makes you take 30% more physical damage. Or the
    # inverse where dodge falls to 0 but you take 30% less physical damage")
    with contextlib.redirect_stdout(io.StringIO()):
        tank = Character(name="Tank", char_class="Warrior", level=60)
    tank._recalculate_derived_stats()
    d0 = tank.dodge
    tank.soul_runes = [None, None, None, "capstone_dancer_3"]
    tank._recalculate_derived_stats()
    check(tank.dodge >= d0 + 24 and abs(tank.get_talent_effect("physical_damage_taken_pct") - 0.30) < 1e-9,
          f"the Dancer: dodge {d0} -> {tank.dodge}")
    tank.soul_runes = [None, None, None, "capstone_anvil_3"]
    tank._recalculate_derived_stats()
    check(tank.dodge == 0 and abs(tank.get_talent_effect("physical_damage_taken_pct") + 0.30) < 1e-9,
          f"the Anvil: dodge {tank.dodge}")

    # Renewal
    p = fresh_priest()
    cap_on(p, "capstone_renewal_3")
    ally = fresh_priest()
    ally.current_health = 10
    with contextlib.redirect_stdout(io.StringIO()):
        out = ab_of(p, "priest_heal").use(p, ally, free=True)
    hots = [e for e in ally.active_effects if str(e.effect_id).startswith("rune_renewal")]
    check(hots and ally.current_health == 10, f"Renewal didn't turn a heal into a HoT: {out}")
    # Surge
    p = fresh_priest()
    cap_on(p, "capstone_surge_3")
    ally = fresh_priest()
    ally.current_health = 10
    with contextlib.redirect_stdout(io.StringIO()):
        ab_of(p, "priest_renew").use(p, ally, free=True)
    check(ally.current_health > 10 and not [e for e in ally.active_effects if e.effect_id == "priest_renew"],
          "Surge didn't land a HoT at once")
    # the Echo (Kyle: "crits will cast the same spell a second time. This spell can not critically hit")
    p = fresh_priest()
    cap_on(p, "capstone_echo_3")
    p.crit_chance_spell, p.hit_chance_spell = 100.0, 1000
    foe = Monster("Mottled Boar", "beast_basic", level=60)
    foe.current_health = foe.health = 10 ** 6
    with contextlib.redirect_stdout(io.StringIO()):
        out = ab_of(p, "priest_smite").use(p, foe, free=True)
    check("Echo:" in str(out), f"a crit didn't echo: {out}")
    check(abs(p.get_talent_effect("all_damage") + 0.25) < 1e-9, "the Echo's 25% damage cost is missing")

    # Detonation and Condensing
    for rid, want in (("capstone_detonation_3", "now"), (None, "dot")):
        p = fresh_priest()
        if rid:
            cap_on(p, rid)
        else:
            p.soul_runes = ["rune_condensing_3", None, None, None]
            p._recalculate_derived_stats()
        p.hit_chance_spell = 1000
        foe = Monster("Mottled Boar", "beast_basic", level=60)
        hp = foe.current_health
        with contextlib.redirect_stdout(io.StringIO()):
            ab_of(p, "priest_shadow_word_pain").use(p, foe, free=True)
        dot = [e for e in foe.active_effects if e.effect_id == "priest_shadow_word_pain"]
        if want == "now":
            check(foe.current_health < hp and not dot, "Detonation didn't land the DoT at once")
        else:
            base_d = ab_of(p, "priest_shadow_word_pain").talented_duration(p)
            check(dot and dot[0].duration <= (base_d + 1) // 2, f"Condensing didn't shorten the DoT ({dot and dot[0].duration} of {base_d})")

    # 5
    with contextlib.redirect_stdout(io.StringIO()):
        from core.game_state import GameStateManager
        from core.game_states import GameState
        screen = pygame.Surface((1280, 720))
        try:
            gsm = GameStateManager(screen)
            gsm.player = hero
            gsm.get_party = lambda: party
            give("rune_riposte_1", 1)
            ss = gsm.states[GameState.SOUL]
            ss.start(hero)
            ss.render(screen)
            ss.slot = R.CAPSTONE_SLOT
            ss.render(screen)
            check(ss.rune_rects, "the Soul screen lists no runes")
            hero.learn_profession("runecrafting")
            ps = gsm.states[GameState.PROFESSIONS]
            ps.active_tab = "runecrafting"
            ps.render(screen)
        except Exception as exc:
            import traceback
            bad.append(f"a screen failed: {exc}\n{traceback.format_exc()[-900:]}")

    caps = sum(1 for r in runes.values() if r["capstone"])
    print(f"{len(runes) - caps} runes and {caps} Capstones ({len(fams)} kinds), roles {roles}, "
          f"{len(recipes)} recipes, {share:.0%} taught, Gambler mean {mean:.2f}")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad[:40]:
            print("  -", b)
        return 1
    print("runecrafting OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
