#!/usr/bin/env python3
"""How dangerous is the game? Real creatures, real dungeon bosses, through the real combat engine.

    PYTHONPATH=. python3 tools/sim_difficulty.py [--world] [--dungeon] [--fights 6]

Kyle, 14 Nov 2026: "I want Dungeons to NEED a group of 5 and open world should still have danger
to it.....not tank and spanking Everything mindlessly." A playtester at 17: "I don't lose health
unless it is a boss."

TWO MEASUREMENTS, both on content that exists, not stat templates:

  OPEN WORLD   one geared player of each of five classes against 1, 2 and 3 real creatures drawn
               from an open zone at that level. Reports win rate and health left. The target Kyle
               was offered: one normal monster costs about a third of your health, two at once is
               risky, three at once usually kills you.
  DUNGEONS     a party of 5 (warrior, priest, mage, rogue, hunter) and a party of 3 (warrior,
               priest, mage) against real dungeon bosses at the dungeon's level. Target: 5 wins,
               3 loses.

The party is played by one simple policy for everyone (sim_class_balance.plan): heal the most hurt
ally when somebody is low and a heal is ready, otherwise use the hardest-hitting thing that works.
Characters are dressed from LootGenerator at their level (greens under 20, blues above), with no
talents spent, so real players with talents are somewhat stronger than this.
"""
import argparse
import contextlib
import io
import json
import os
import random
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

TICK, MAX_TICKS = 0.25, 16000
SOLO = ["Warrior", "Priest", "Druid", "Mage", "Rogue"]
PARTY5 = ["Warrior", "Priest", "Mage", "Rogue", "Hunter"]
PARTY3 = ["Warrior", "Priest", "Mage"]

#: (level, open zone) - a zone whose open-zone table sits at that level
WORLD_BANDS = [(10, "Durotar"), (17, "Silverpine North"), (25, "Ashenvale West"),
               (34, "Arathi Central"), (45, "The Abyssal Sands"), (54, "Tempest Shallows")]
#: (dungeon cave name, its bosses to fight, party level)
DUNGEON_BOSSES = [
    ("Ragefire Chasm", ["Oggleflint", "Taragaman the Hungerer", "Bazzalan"], 15),
    ("Wailing Caverns", ["Lady Anacondra", "Lord Pythas"], 20),
    ("Shadowfang Keep", ["Razorclaw the Butcher", "Archmage Arugal"], 23),
    ("Razorfen Kraul", ["Roogug", "Agathelos the Raging"], 30),
    ("The Drowning Floor", ["Yearmaw"], 35),
    ("The Cistern", ["Resonance", "The Thirst"], 52),
    ("Khaz Varun, the Black Hollow", ["Gatewarden Hrun", "Forge-Lord Darrok", "Thane Morrun the Unmade"], 54),
    ("The Emberdeep", ["Pack-Alpha Cinderhound", "The Molten Serpent", "The Caldera"], 58),
    ("The Royal Hive", ["Hive-Warden Kasz'ar", "Tunnel-King Ruzzak", "Hive-Mother Ahn'thera"], 56),
]


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def make(cls, level, gen):
    from entities.character import Character
    from tools.sim_class_balance import dress
    with quiet():
        c = Character(name=cls, char_class=cls, level=level)
        dress(c, gen, level)
    c.current_health = c.health
    if getattr(c, "mana", 0):
        c.current_mana = c.mana
    return c


def run(chars, enemies, rng):
    """One fight to its end. -> (won, {name: health fraction left}, turns)."""
    from combat.combat_engine import CombatEngine
    from entities.party import Party
    from tools.sim_class_balance import plan
    party = Party(chars[0])
    for c in chars[1:]:
        party.add_member(c) if hasattr(party, "add_member") else party.members.append(c)
    with quiet():
        engine = CombatEngine(chars[0], enemies[0], party=party, enemies=enemies)
    plans = {id(c): plan(c) for c in chars}
    last_heal = {id(c): -3 for c in chars}
    turns = 0
    for _ in range(MAX_TICKS):
        with quiet():
            engine.update(TICK)
        if not engine.is_active:
            break
        actor = engine.current_actor
        if actor is None:
            continue
        if actor not in chars:
            with quiet():
                engine.execute_monster_action()
            continue
        turns += 1
        heals, attacks, setup, defensives = plans[id(actor)]
        living = [c for c in chars if c.current_health > 0]
        hurt = min(living, key=lambda c: c.current_health / max(1, c.health))
        acted = False
        with quiet():
            if heals and hurt.current_health / max(1, hurt.health) < 0.55 and turns - last_heal[id(actor)] >= 2:
                for h in heals:
                    if engine.execute_ability(actor, h.ability_id, hurt)[0]:
                        last_heal[id(actor)] = turns
                        acted = True
                        break
            if not acted:
                # the engine's list, not ours: a summoned add joins the fight there
                foes = engine.living_enemies() if hasattr(engine, "living_enemies") else \
                    [e for e in enemies if e.is_alive()]
                foes = sorted(foes, key=lambda e: not getattr(e, "is_boss", False))
                if not foes:
                    break
                for a in attacks:
                    if engine.execute_ability(actor, a.ability_id, foes[0])[0]:
                        acted = True
                        break
            if not acted:
                engine.execute_defend(actor)
    won = bool(getattr(engine, "victory", False))
    return won, {c.name: max(0.0, c.current_health / max(1, c.health)) for c in chars}, turns


def spawn(cm, name, level):
    with quiet():
        return cm.spawn_creature(name, level=level)


def world(fights, rng, gen, cm):
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    print("\nOPEN WORLD - one geared player against 1, 2 and 3 same-level creatures from the zone")
    print(f"{'level':>5} {'zone':<20} {'class':<8} " + "  ".join(f"{n} at once: win/hp left" for n in (1, 2, 3)))
    for level, zone in WORLD_BANDS:
        table = enc.get(zone, {}).get("open_zone", {}).get("creatures", {})
        pool = [n for n, w in table.items() if w and n in cm.creatures
                and not cm.creatures[n].get("is_boss")]
        if not pool:
            print(f"{level:>5} {zone:<20} (no open-zone creatures)")
            continue
        for cls in SOLO:
            cells = []
            for count in (1, 2, 3):
                wins, left = 0, []
                for _ in range(fights):
                    c = make(cls, level, gen)
                    foes = [spawn(cm, rng.choice(pool), level) for _ in range(count)]
                    won, hp, _t = run([c], foes, rng)
                    wins += won
                    left.append(hp[c.name] if won else 0.0)
                cells.append(f"{wins}/{fights} {statistics.mean(left):>4.0%}")
            print(f"{level:>5} {zone:<20} {cls:<8} " + "        ".join(cells))


def dungeon(fights, rng, gen, cm, only=None):
    print("\nDUNGEONS - a party of 5 and a party of 3 against real bosses at the dungeon's level")
    for cave, bosses, level in DUNGEON_BOSSES:
        if not bosses or (only and only.lower() not in cave.lower()):
            continue
        for b in bosses:
            # the party is the boss's own level: a group meets each boss at about its level
            level = cm.creatures[b]["level_range"][1]
            out = []
            for size, comp in (("5", PARTY5), ("3", PARTY3)):
                wins, alive = 0, []
                for _ in range(fights):
                    chars = [make(cls, level, gen) for cls in comp]
                    for i, c in enumerate(chars):
                        c.name = f"{c.name}{i}"
                    foes = [spawn(cm, b, level)]
                    if b == "Hive-Mother Ahn'thera":
                        foes.append(spawn(cm, "Royal Consort Zhir'ak", level))
                    for f in foes:
                        f.location_type = "cave"
                    won, hp, _t = run(chars, foes, rng)
                    wins += won
                    alive.append(sum(1 for v in hp.values() if v > 0))
                out.append(f"party of {size}: won {wins}/{fights}, {statistics.mean(alive):.1f} standing")
            print(f"  {cave[:24]:<24} {b:<28} " + "   ".join(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", action="store_true")
    ap.add_argument("--dungeon", action="store_true")
    ap.add_argument("--fights", type=int, default=6)
    ap.add_argument("--only", default=None, help="only dungeons whose name contains this")
    ap.add_argument("--set", default=None,
                    help='try a table without saving it, e.g. \'{"open":{"damage":1.6}}\'')
    args = ap.parse_args()
    both = not (args.world or args.dungeon)
    import pygame
    pygame.init()
    if args.set:
        from world import difficulty
        t = dict(difficulty.table())
        for k, v in json.loads(args.set).items():
            t[k] = {**t.get(k, {}), **v}
        difficulty.table.cache_clear()
        difficulty.table = lambda: t          # noqa: E731
        print("trying", {k: t[k] for k in ("open", "cave", "boss")})
    with quiet():
        from entities.loot_generator import LootGenerator
        from world.creature_manager import CreatureManager
        gen, cm = LootGenerator(), CreatureManager()
    rng = random.Random(7)
    random.seed(7)
    if args.world or both:
        world(args.fights, rng, gen, cm)
    if args.dungeon or both:
        dungeon(args.fights, rng, gen, cm, args.only)
    return 0


if __name__ == "__main__":
    sys.exit(main())
