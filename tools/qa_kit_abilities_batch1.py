"""
Seven recruit signature abilities that did nothing now do what they say.

From the list of 34 inert personal-kit abilities (backlog group N). These four needed either
nothing new or one small mechanic:

  Carolina Santos   Deep in March, Aground in September   every enemy 25% to miss, 2 turns
                    (new: an attacker's own miss chance, from a debuff on it)
  Rosa Delgado      Stop Tracking, Start Anticipating     cannot miss for 4 turns
  Sophia Dias       Get the Register Right                spells land as the target's weakest school
  Kesten Ambrose    He Catalogues                         the commonest KIND of enemy takes
                    +20% damage (uses the creature types built for crowd control)

  Adrián Mendoza    He Still Has the Whistle              silences every enemy 2 turns
  Saoirse Ní B.     The Sliotar                           silences one enemy 2 turns
                    (new: silence - a monster can only make its basic attack; 1 turn on a boss)

Each is cast for real, on the recruit the game builds, and the outcome is measured.
"""
import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    from world.recruit_manager import get_recruit_manager
    from entities.monster import Monster
    from entities.character import Character
    random.seed(4)
    rm = get_recruit_manager()
    built = {}
    for rec in rm.recruits.values():
        c = rm.build_or_restore(rec, player_level=60)
        if c is not None:
            built[c.name] = c

    def kit(name, aid):
        c = built.get(name)
        if not check(c is not None, f"rig: no recruit {name}"):
            return None, None
        ab = c.ability_book.get_ability(aid)
        if not check(ab is not None, f"rig: {name} does not have {aid}"):
            return c, None
        ab.is_learned = True
        for attr in ("current_mana", "current_energy", "current_rage"):
            setattr(c, attr, 10 ** 5)
        return c, ab

    def mobs():
        return [Monster("Mottled Boar", "beast_basic", level=60), Monster("Naga Siren", "humanoid_caster", level=60),
                Monster("Thornhide Boar", "beast_basic", level=60)]

    # Carolina ----------------------------------------------------------------------------
    c, ab = kit("Carolina Santos", "personal_carolina_deep_in_march")
    if ab:
        foes = mobs()
        ok, msg = ab.use(c, foes, free=True)
        check(ok, f"Deep in March would not cast ({msg})")
        check(all(f.get_status_stat_mod("miss_chance_pct") == 25 for f in foes),
              f"Deep in March: enemies' miss chance is {[f.get_status_stat_mod('miss_chance_pct') for f in foes]}")
        victim = Character("V", "Mage", 60)
        victim.dodge = victim.parry = victim.block_chance = 0.0
        landed = 0
        for _ in range(2000):
            victim.current_health = victim.health
            if victim.take_damage(50, "magic", attacker=foes[0], attacker_level=60) > 0:
                landed += 1
        check(0.70 <= landed / 2000 <= 0.80, f"with a 25% miss chance, {landed / 20:.0f}% of 2000 attacks landed")
        clean = Monster("Mottled Boar", "beast_basic", level=60)
        landed = sum(1 for _ in range(300) if (setattr(victim, "current_health", victim.health) or victim.take_damage(50, "magic", attacker=clean, attacker_level=60)) > 0)
        check(landed == 300, f"an enemy with no debuff missed {300 - landed} of 300")

    # Rosa --------------------------------------------------------------------------------
    c, ab = kit("Rosa Delgado", "personal_rosa_stop_tracking_start_anticipating")
    if ab:
        before = c.hit_rating
        ok, msg = ab.use(c, c, free=True)
        c._recalculate_derived_stats()
        check(ok and c.hit_rating >= c.HIT_RATING_CAP, f"Stop Tracking: hit rating {before} -> {c.hit_rating}, cap is {c.HIT_RATING_CAP} ({msg})")

    # Sophia ------------------------------------------------------------------------------
    c, ab = kit("Sophia Dias", "personal_sophia_get_the_register_right")
    if ab:
        def burn(caster):
            imp = Monster("Mottled Boar", "beast_basic", level=60)
            imp.fire_resistance, imp.frost_resistance = 60, 0
            tot = 0
            for _ in range(300):
                imp.current_health = imp.max_health
                tot += imp.take_damage(1000, "fire", attacker=caster, attacker_level=60) or 0
            return tot
        plain = burn(c)
        ok, msg = ab.use(c, c, free=True)
        check(ok and c.get_status_stat_mod("weakest_school") > 0, f"Get the Register Right did not take ({msg})")
        tuned = burn(c)
        check(plain and tuned > plain * 1.5,
              f"fire into a fire-resistant target: {plain} before, {tuned} with the register right - it should land as the weakest school")

    # Kesten ------------------------------------------------------------------------------
    c, ab = kit("Kesten Ambrose", "personal_kesten_he_catalogues")
    if ab:
        foes = mobs()                                  # two beasts and a humanoid
        ok, msg = ab.use(c, foes, free=True)
        check(ok, f"He Catalogues would not cast ({msg})")
        got = [f.get_status_stat_mod("damage_taken_pct") for f in foes]
        check(got[0] == 0.2 and got[2] == 0.2, f"He Catalogues: the two beasts should take +20%; got {got}")
        check(got[1] == 0, f"He Catalogues: the naga is not a beast and should be untouched; got {got[1]}")
        hitter = Character("H", "Warrior", 60)
        plain = Monster("Mottled Boar", "beast_basic", level=60)
        a = b = 0
        for _ in range(400):
            foes[0].current_health = foes[0].max_health
            plain.current_health = plain.max_health
            a += foes[0].take_damage(1000, "fire", attacker=hitter, attacker_level=60) or 0
            b += plain.take_damage(1000, "fire", attacker=hitter, attacker_level=60) or 0
        check(b and 1.15 <= a / b <= 1.25, f"a catalogued boar took {a / max(1, b):.2f}x the damage of an ordinary one (want 1.20)")

    # Adrián and Saoirse: silence ---------------------------------------------------------
    def kit_mob(name, boss=False):
        import json as _j
        cr = _j.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
        m = Monster(name, cr[name]["template"], level=60)
        m.is_boss = boss
        return m
    caster_mob = next((n for n in ("Naga Siren", "Forsaken Mage", "Defias Pillager") if True), None)
    for who, aid, multi in (("Adrián Mendoza", "personal_adrian_he_still_has_the_whistle", True),
                            ("Saoirse Ni Bhraonain", "personal_saoirse_the_sliotar", False)):
        c, ab = kit(who, aid)
        if not ab:
            continue
        foe, boss = kit_mob(caster_mob), kit_mob(caster_mob, boss=True)
        if not check(len(foe.abilities) > 1, f"rig: {caster_mob} has only a basic attack"):
            continue
        victim = Character("V", "Mage", 60)
        free_picks = {foe.choose_action(victim).name for _ in range(60) if not foe.abilities[0].__setattr__("turns_remaining", 0)}
        check(len(free_picks) > 1 or foe.abilities[0].name not in free_picks,
              f"rig: an unsilenced {caster_mob} only ever uses {free_picks}")
        ok, msg = ab.use(c, [foe, boss] if multi else foe, free=True)
        check(ok and foe.get_status_stat_mod("silenced") > 0, f"{ab.name}: the target is not silenced ({msg})")
        for a2 in foe.abilities:
            a2.turns_remaining = 0
        picks = {getattr(foe.choose_action(victim), "name", None) for _ in range(60)}
        check(picks == {foe.abilities[0].name}, f"{ab.name}: a silenced {caster_mob} still used {picks}")
        if multi:
            eff = next((e for e in boss._effects() if (e.stat_mods or {}).get("silenced")), None)
            check(eff is not None and eff.duration == 1, f"{ab.name}: on a boss the silence should last 1 turn, got {getattr(eff, 'duration', None)}")
            eff = next((e for e in foe._effects() if (e.stat_mods or {}).get("silenced")), None)
            check(eff is not None and eff.duration == 2, f"{ab.name}: on an ordinary enemy the silence should last 2 turns, got {getattr(eff, 'duration', None)}")

    # Kiet: threat wipe + crit -------------------------------------------------------------
    c, ab = kit("Kiet Somsak", "personal_kiet_nobody_looks_twice")
    if ab:
        from combat.combat_engine import CombatEngine
        from entities.party import Party
        grunt, boss = kit_mob("Mottled Boar"), kit_mob("Mottled Boar", boss=True)
        eng = CombatEngine(c, grunt, party=Party(c), enemies=[grunt, boss])
        eng.gain_threat(c, grunt, 5000)
        eng.gain_threat(c, boss, 5000)
        eng.current_actor = c
        ok, msg = eng.execute_ability(c, "personal_kiet_nobody_looks_twice", c)
        check(ok, f"Nobody Looks Twice would not cast ({msg})")
        check(eng.get_threat(grunt, c) == 0, f"Kiet still has {eng.get_threat(grunt, c)} threat on an ordinary enemy")
        check(eng.get_threat(boss, c) >= 5000, f"a boss forgot Kiet (threat {eng.get_threat(boss, c)})")
        c._recalculate_derived_stats()
        check(c.crit_chance_physical >= 100, f"Kiet's crit is {c.crit_chance_physical:.0f}% - not guaranteed")

    # Marcus: an area effect lands on the ROW you aim at, all of it and only it ---------------
    # Kyle, 12 Nov: "stormbringer attack says it targets a row - it only applies dot to one
    # enemy." Its target type was "enemy_row", which nothing in the engine knew, so it fell
    # through to a single target.
    c, ab = kit("Marcus Okafor", "personal_marcus_where_the_strikes_land")
    if ab:
        from combat.combat_engine import CombatEngine
        from entities.party import Party
        landed_all = False
        for _try in range(8):                                 # a spell can be resisted
            front = [kit_mob("Mottled Boar"), kit_mob("Mottled Boar")]
            back = [kit_mob("Mottled Boar"), kit_mob("Mottled Boar")]
            for m in front:
                m.row = "front"
            for m in back:
                m.row = "back"
            eng = CombatEngine(c, front[0], party=Party(c), enemies=front + back)
            eng.current_actor = c
            c.current_mana = 10 ** 5
            ab.turns_remaining = 0
            ok, msg = eng.execute_ability(c, ab.ability_id, back[0])
            hit = lambda m: any(e.effect_id == ab.ability_id for e in m._effects())
            check(ok, f"Where the Strikes Land would not cast ({msg})")
            check(not any(hit(m) for m in front), "Where the Strikes Land, aimed at the back row, also hit the front row")
            if all(hit(m) for m in back):
                landed_all = True
                break
        check(landed_all, "Where the Strikes Land did not put its lightning on every enemy in the aimed row")

    # ...and no ability anywhere has a target type the engine does not know
    import glob as _g
    import json as _j
    KNOWN = {None, "self", "ally", "party", "enemy", "enemy_aoe", "all_enemies", "pet"}
    for f in sorted(_g.glob("data/abilities/*.json")) + ["data/npcs/personal_kits.json"]:
        blob = _j.loads(open(f, encoding="utf-8").read())
        entries = blob.get("abilities") if "abilities" in blob else [
            a for k in blob.values() if isinstance(k, dict) for a in (k.get("abilities") or [])]
        for a in entries:
            check(a.get("target_type") in KNOWN,
                  f"{a.get('ability_id')}: target_type {a.get('target_type')!r} is not one the engine handles")

    # none of the four still says it needs something
    import json
    kits = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
    for k in kits.values():
        for a in (k.get("abilities") or []) if isinstance(k, dict) else []:
            if a.get("ability_id") in ("personal_kiet_nobody_looks_twice", "personal_adrian_he_still_has_the_whistle", "personal_saoirse_the_sliotar", "personal_carolina_deep_in_march", "personal_rosa_stop_tracking_start_anticipating",
                                       "personal_sophia_get_the_register_right", "personal_kesten_he_catalogues"):
                check(not str(a.get("engine", "")).startswith("needs"), f"{a['ability_id']} is still marked {a.get('engine')!r}")
                check(a.get("stat_mods"), f"{a['ability_id']} has no effect")

    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:25]:
            print("  ", f)
        return 1
    print("kit abilities (batch 1) OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
