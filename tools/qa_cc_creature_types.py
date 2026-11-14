"""
Crowd control works on the creatures it should, and nothing else.

Kyle, 10 Nov: "why can i BANISH a naga?"

  1. every creature in the game resolves to a WoW creature type, and named ones resolve to the
     right one (a naga is a humanoid, a whelp is dragonkin, a golem is mechanical)
  2. cast through the real ability on real monsters:
       Banish      lands on a demon and an elemental, refused on a naga and a boar
       Polymorph   lands on a humanoid and a beast, refused on an elemental and undead
       Hibernate   beast / dragonkin only        Scare Beast  beasts only
       Turn Evil   undead / demon only           Sap          humanoids only
       Fear        refused on undead and mechanical, lands on a humanoid
  3. a refused cast costs NOTHING - no mana, no cooldown - and says why
  4. the tooltip says who it works on
  5. type-specific control does not land on a boss; an ordinary stun still does
  6. an ordinary stun still lands on every type
  7. every rule names real creature types and a real ability
"""
import json
import os
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


NAMED = {
    "Naga Siren": "humanoid", "Naga Myrmidon": "humanoid", "Murloc Tidehunter": "humanoid",
    "Mottled Boar": "beast", "Giant Spider": "beast", "Thornhide Boar": "beast",
    "Razorjaw Whelp": "dragonkin", "Smoke Drake": "dragonkin",
    "Iron Golem": "mechanical", "Felhound": "demon", "Arugal's Voidwalker": "demon",
    "Water Elemental": "elemental", "Deviate Ooze": "elemental",
    "Forsaken Mage": "undead", "Weeping Shade": "undead", "Boulderfist Ogre": "humanoid",
    "Silithid Guardian": "beast", "Felstalker Whelp": "demon", "Harpy": "humanoid",
}


def main():
    from world import creature_types as CT
    from entities.character import Character
    from entities.monster import Monster

    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    counts = {}
    for name, entry in creatures.items():
        t = CT.classify(name, entry.get("template", ""))
        check(t in CT.ALL, f"{name}: resolves to {t!r}, which is not a creature type")
        counts[t] = counts.get(t, 0) + 1
    for name, want in NAMED.items():
        if check(name in creatures, f"rig: no creature called {name}"):
            got = CT.classify(name, creatures[name]["template"])
            check(got == want, f"{name} should be {want}, resolves to {got}")

    def mob(name, boss=False):
        m = Monster(name, creatures[name]["template"], level=40)
        m.is_boss = boss
        return m

    def caster(cls, ability_id):
        c = Character("Hero", cls, 60)
        ab = c.ability_book.get_ability(ability_id)
        if not check(ab is not None, f"rig: a level 60 {cls} has no {ability_id}"):
            return c, None
        ab.is_learned = True
        return c, ab

    def cast(cls, ability_id, target_name, boss=False):
        c, ab = caster(cls, ability_id)
        if ab is None:
            return None
        if getattr(ab, "requires_form", None):
            ab.requires_form = None
        c.current_mana = c.mana
        c.current_energy = getattr(c, "max_energy", 100)
        c.current_rage = getattr(c, "max_rage", 100)
        t = mob(target_name, boss)
        before = (c.current_mana, c.current_energy, c.current_rage)
        ok, msg = ab.use(c, t)
        landed = t.is_stunned
        spent = (c.current_mana, c.current_energy, c.current_rage) != before
        return ok, msg, landed, spent, ab

    LAND, NO = True, False
    table = [
        ("Warlock", "warlock_banish", "Felhound", LAND), ("Warlock", "warlock_banish", "Water Elemental", LAND),
        ("Warlock", "warlock_banish", "Naga Siren", NO), ("Warlock", "warlock_banish", "Mottled Boar", NO),
        ("Mage", "mage_polymorph", "Naga Siren", LAND), ("Mage", "mage_polymorph", "Mottled Boar", LAND),
        ("Mage", "mage_polymorph", "Water Elemental", NO), ("Mage", "mage_polymorph", "Forsaken Mage", NO),
        ("Druid", "druid_hibernate", "Mottled Boar", LAND), ("Druid", "druid_hibernate", "Razorjaw Whelp", LAND),
        ("Druid", "druid_hibernate", "Naga Siren", NO),
        ("Hunter", "hunter_scare_beast", "Mottled Boar", LAND), ("Hunter", "hunter_scare_beast", "Felhound", NO),
        ("Paladin", "paladin_turn_evil", "Forsaken Mage", LAND), ("Paladin", "paladin_turn_evil", "Felhound", LAND),
        ("Paladin", "paladin_turn_evil", "Mottled Boar", NO),
        ("Rogue", "rogue_sap", "Naga Siren", LAND), ("Rogue", "rogue_sap", "Mottled Boar", NO),
        ("Warlock", "warlock_fear", "Naga Siren", LAND), ("Warlock", "warlock_fear", "Forsaken Mage", NO),
        ("Warlock", "warlock_fear", "Iron Golem", NO),
        # 6. plain stuns are untouched
        ("Paladin", "paladin_hammer_of_justice", "Water Elemental", LAND),
        ("Paladin", "paladin_hammer_of_justice", "Iron Golem", LAND),
        ("Paladin", "paladin_hammer_of_justice", "Forsaken Mage", LAND),
    ]
    for cls, aid, target, want in table:
        r = cast(cls, aid, target)
        if r is None:
            continue
        ok, msg, landed, spent, ab = r
        if want:
            check(ok and landed, f"{ab.name} on {target} should land; ok={ok} stunned={landed} ({msg})")
        else:
            check(not ok, f"{ab.name} on {target} should be refused, but the cast went through ({msg})")
            check(not landed, f"{ab.name} on {target} should do nothing, but {target} is incapacitated")
            check(not spent, f"{ab.name} refused on {target} still spent the caster's resource")
            check(ab.is_available(), f"{ab.name} refused on {target} still went on cooldown")
            check(target in str(msg) and "does not work" in str(msg),
                  f"{ab.name} on {target}: the refusal should say why; it says {msg!r}")

    # 4. tooltip
    for cls, aid, needle in (("Warlock", "warlock_banish", "Only works on Demons and Elementals."),
                             ("Mage", "mage_polymorph", "Only works on Humanoids, Beasts and Critters."),
                             ("Warlock", "warlock_fear", "Does not work on Undead or Mechanicals.")):
        _c, ab = caster(cls, aid)
        if ab is not None:
            check(needle in ab.get_tooltip_lines(), f"{ab.name}'s tooltip should say {needle!r}")

    # 5. bosses
    r = cast("Warlock", "warlock_banish", "Felhound", boss=True)
    if r:
        check(not r[0] and not r[2] and not r[3], f"Banish should not land on a boss demon ({r[1]})")
        check("too powerful" in str(r[1]), f"Banish on a boss should say why; it says {r[1]!r}")
    r = cast("Paladin", "paladin_hammer_of_justice", "Felhound", boss=True)
    if r:
        check(r[0] and r[2], f"an ordinary stun should still land on a boss ({r[1]})")

    # the same rule when the effect arrives without a cast (area effects, procs)
    from combat.status_effects import StatusEffect, EffectType
    naga = mob("Naga Siren")
    msg = naga.apply_status_effect(StatusEffect("warlock_banish", "Banish", EffectType.DEBUFF, 2,
                                                is_stun=True, real_time_seconds=None))
    check(not naga.is_stunned, f"a Banish effect applied directly still incapacitated a naga ({msg})")

    # 3b. in a real fight: refused, logged, and still your turn
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    lock, ab = caster("Warlock", "warlock_banish")
    if ab is not None:
        lock.current_mana = lock.mana
        naga2 = mob("Naga Siren")
        eng = CombatEngine(lock, naga2, party=Party(lock), enemies=[naga2])
        eng.current_actor = lock
        mana = lock.current_mana
        ok, msg = eng.execute_ability(lock, "warlock_banish", naga2)
        check(not ok and "does not work" in str(msg), f"in combat, Banish on a naga: ok={ok} {msg!r}")
        check(eng.current_actor is lock, "a refused Banish ended the warlock's turn")
        check(lock.current_mana == mana, "a refused Banish spent mana in combat")
        check(not naga2.is_stunned, "a refused Banish incapacitated the naga in combat")

    # 7. the rules themselves
    ids = set()
    n_rules = 0
    for f in (ROOT / "data/abilities").glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        for a in data.get("abilities", []) if isinstance(data, dict) else []:
            ids.add(a.get("ability_id"))
            for key in ("creature_types", "immune_creature_types"):
                for t in a.get(key) or []:
                    check(t in CT.ALL, f"{a['ability_id']}.{key}: {t!r} is not a creature type")
                if a.get(key):
                    n_rules += 1
                    check(a.get("is_stun"), f"{a['ability_id']} has {key} but is not crowd control")
    check(n_rules >= 15, f"only {n_rules} crowd-control rules authored")

    print(f"{len(creatures)} creatures typed: " + ", ".join(f"{v} {k}" for k, v in sorted(counts.items(), key=lambda kv: -kv[1])))
    print(f"{len(table)} casts checked, {n_rules} rules authored")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:40]:
            print("  ", f)
        return 1
    print("crowd control OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
