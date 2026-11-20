#!/usr/bin/env python3
"""A whole levelling run, 1 to 60, solo, questing the open world, through the real combat engine.

    PYTHONPATH=. python3 tools/sim_campaign.py [--specs warrior_protection:tank,priest_holy:healer,mage_fire:dps]
                                               [--tier geared] [--seed 1] [--json out.json] [--rares-only]

Kyle, 19 Nov 2026: "please do start a lvl 1 to 60 simulated run. As a tank, as a Healer, as a dps. See how it is to
quest open world solo etc. I know we saw overtuned rares last night....so there are cracks."

THE RUN. One character per spec starts at level 1 with no XP and plays the game's own quests, solo:
  * WHICH QUEST NEXT: the lowest-level quest it can take (level_min reached, its chain's earlier quests done) that
    isn't grey to it. With nothing left, it grinds the open world at its level until a quest opens up, and that
    grinding is counted: it's the hole in the content.
  * WHAT A QUEST COSTS: a kill objective is that many fights against the real target, spawned the way the game does
    (its own level range and the zone's overrides). A fetch is fights against whatever drops the item, rolled at the
    drop's own chance. A named target (kill_boss) found in an open-world table is fought alone, as the rare it is.
    One that only lives in a dungeon is a dungeon quest: skipped solo, and counted. Explore, deliver, gather,
    dialogue and craft cost no fight. Every quest also meets one random encounter on the road in its zone, rolled
    through the real encounter roll (CreatureManager.get_random_creature), so subzone rares turn up at the game's
    own 6%.
  * XP: kills by combat_engine's rule (con colour, the 1.75x named bonus, 1.2x in a subzone, the global 0.4), quests
    by Quest.get_scaled_exp_reward's (con colour on quest level, the global 0.5). A death costs 15% of the level's
    XP, as a wipe does.
  * BETWEEN PULLS it rests to full when health is under 60% or mana under 40%, and the rests are counted.
  * GEAR: re-dressed at every level-up at --tier (default "geared": greens under 20, blues from 20, built for the
    spec), with that role's talents, which is about what a player questing keeps up with.
  * Quests in hidden zones are left out, and this file and its output never name one.

THE RARE CENSUS (also --rares-only): every rare in an open-world subzone, fought five times by each spec at the
rare's own level. Kyle's target for an ordinary monster is "about a third of your health"; a rare should be a real
fight, but a soloable one for anyone at its level.
"""
import argparse
import collections
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
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

DEFAULT_SPECS = "warrior_protection:tank,priest_holy:healer,mage_fire:dps"
REST_HP, REST_MANA = 0.60, 0.40
DEATH_XP = 0.15
#: a quest with a fight that needs more than this many attempts is given up (an unkillable objective)
GIVE_UP = 6


@contextlib.contextmanager
def quiet():
    with contextlib.redirect_stdout(io.StringIO()):
        yield


# ------------------------------------------------------------------------------------------------ the world
class World:
    def __init__(self):
        from world.creature_manager import CreatureManager
        from world.hidden_zones import is_hidden
        from world.zone_keys import zone_key
        with quiet():
            self.cm = CreatureManager()
        enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
        self.enc = {z: t for z, t in enc.items() if not is_hidden(z)}
        self.by_key = {zone_key(z): z for z in self.enc}
        self.hidden_keys = {zone_key(z) for z in enc if is_hidden(z)}
        # creature -> [(zone, "open_zone"|"subzone", subzone)] wherever the open world has it
        self.where = collections.defaultdict(list)
        # A DUNGEON'S OR A CAVE'S TABLE IS FILED UNDER ITS PARENT ZONE'S SUBZONES (Durnholde Keep under Eastern
        # Hillsbrad, Jaedenar under North Felwood), but it's its own map: its named creatures are a dungeon's bosses
        # (3x, built for five) or a cave's, never open-world rares. The first census counted two of them as rares.
        from world.gathering_manager import CAVE_TO_PARENT_ZONE
        from world.zone_classification import DUNGEONS
        closed = set(DUNGEONS) | set(CAVE_TO_PARENT_ZONE)
        for z, t in self.enc.items():
            for n in (t.get("open_zone", {}).get("creatures") or {}):
                self.where[n].append((z, "open_zone", None))
            for sz, st in (t.get("subzones") or {}).items():
                if sz in closed:
                    continue
                for n in (st.get("creatures") or {}):
                    self.where[n].append((z, "subzone", sz))
        drops = json.loads((ROOT / "data/creatures/quest_drops.json").read_text(encoding="utf-8"))["drops"]
        self.droppers = collections.defaultdict(list)          # item id -> [(creature, chance)]
        for creature, items in drops.items():
            for it in items:
                self.droppers[it.get("item_id")].append((creature, float(it.get("chance", 0.5))))
        self.quests = []
        self.hidden_quests = 0
        for f in sorted((ROOT / "data/quests").glob("*.json")):
            try:
                qs = json.loads(f.read_text(encoding="utf-8")).get("quests", [])
            except ValueError:
                continue
            for q in qs:
                if zone_key(q.get("zone") or "") in self.hidden_keys or q.get("repeatable"):
                    self.hidden_quests += bool(zone_key(q.get("zone") or "") in self.hidden_keys)
                    continue
                self.quests.append(q)
        self.rares = sorted({(n, z, sz) for n, places in self.where.items() for (z, kind, sz) in places
                             if kind == "subzone" and self.cm.creatures.get(n, {}).get("is_boss")})

    def zone_for(self, q):
        from world.zone_keys import zone_key
        return self.by_key.get(zone_key(q.get("zone") or ""))

    def spawn(self, name, zone=None, level=None):
        with quiet():
            m = self.cm.spawn_creature(name, level=level, zone_name=zone)
        if m is not None:
            place = next((p for p in self.where.get(name, []) if p[0] == zone), None) or \
                (self.where.get(name) or [(None, "open_zone", None)])[0]
            m.location_type = place[1]
        return m

    def roll(self, zone, level):
        """One random encounter on the road in this zone: a subzone half the time (where rares live)."""
        from world.gathering_manager import CAVE_TO_PARENT_ZONE
        from world.zone_classification import DUNGEONS
        t = self.enc.get(zone) or {}
        subs = [s for s in (t.get("subzones") or {}) if s not in DUNGEONS and s not in CAVE_TO_PARENT_ZONE]
        with quiet():
            if subs and random.random() < 0.5:
                sz = random.choice(subs)
                m = self.cm.get_random_creature(zone, "subzone", sz)
                if m is not None:
                    m.location_type = "subzone"
                return m
            m = self.cm.get_random_creature(zone, "open_zone")
        if m is not None:
            m.location_type = "open_zone"
        return m

    def grind_pool(self, level):
        """Open-world trash within two levels of this one, from anywhere."""
        out = []
        for n, places in self.where.items():
            d = self.cm.creatures.get(n) or {}
            if d.get("is_boss"):
                continue
            lo, hi = (d.get("level_range") or [1, 1])[:2]
            if lo - 2 <= level <= hi + 2:
                out.append((n, places[0][0]))
        return out


# ------------------------------------------------------------------------------------------------ the hero
class Hero:
    def __init__(self, spec, role, tier, gen):
        self.spec, self.role, self.tier, self.gen = spec, role, tier, gen
        self.level, self.xp = 1, 0
        self.char = None
        self.dress()
        self.log = collections.defaultdict(lambda: collections.Counter())
        self.lists = collections.defaultdict(lambda: collections.defaultdict(list))
        self.deaths = []
        self.rares = []

    def dress(self):
        import sim_viability as V
        with quiet():
            self.char = V.make(self.spec, self.role, self.level, self.tier, self.gen)
        self.full()

    def full(self):
        c = self.char
        c.current_health = c.health
        if getattr(c, "mana", 0):
            c.current_mana = c.mana

    def band(self):
        return (self.level - 1) // 5 * 5 + 1

    def gain(self, xp, source):
        from config import get_exp_needed_for_level
        if self.level >= 60:
            return
        self.log[self.band()][f"xp_{source}"] += xp
        self.xp += xp
        up = False
        while self.level < 60 and self.xp >= get_exp_needed_for_level(self.level):
            self.xp -= get_exp_needed_for_level(self.level)
            self.level += 1
            up = True
        if up:
            self.dress()

    def fight(self, foes, what):
        """One pull. Returns won. Rests first if low, as a player would."""
        import sim_viability as V
        c = self.char
        low_mana = getattr(c, "mana", 0) and c.current_mana < c.mana * REST_MANA
        if c.current_health < c.health * REST_HP or low_mana:
            self.full()
            self.log[self.band()]["rests"] += 1
        for a in c.get_learned_abilities():
            a.turns_remaining = 0
        try:
            won, _d, turns, hp = V.fight([c], {id(c): self.role}, foes)
        except Exception as e:                                   # noqa: BLE001
            self.log[self.band()]["errors"] += 1
            self.lists[self.band()]["errors"].append(f"{type(e).__name__}: {e}"[:120])
            won, turns, hp = False, 0, {c.name: 0.0}
        b = self.log[self.band()]
        b["fights"] += 1
        b["turns"] += turns
        left = hp.get(c.name, 0.0)
        if won:
            b["wins"] += 1
            self.lists[self.band()]["hp_left"].append(left)
            from combat.difficulty import kill_xp_multiplier
            from config import KILL_EXP_MULTIPLIER
            for f in foes:
                mult = kill_xp_multiplier(f.level, self.level)
                if mult <= 0:
                    continue
                r = f.get_exp_reward() * mult
                if getattr(f, "is_boss", False):
                    r *= 1.75
                if getattr(f, "location_type", "") == "subzone":
                    r *= 1.2
                self.gain(max(1, int(r * KILL_EXP_MULTIPLIER)), "kills")
        else:
            b["deaths"] += 1
            self.deaths.append((self.level, what, [f"{f.name} L{f.level}" for f in foes]))
            from config import get_exp_needed_for_level
            if self.level < 60:
                self.xp = max(0, self.xp - int(get_exp_needed_for_level(self.level) * DEATH_XP))
            self.full()
        return won


# ------------------------------------------------------------------------------------------------ the run
def quest_level(q):
    return q.get("level_max") if q.get("level_max") is not None else q.get("level_min", 1)


def run(spec, role, tier, world, gen, seed):
    from combat.difficulty import grey_level, quest_xp_multiplier
    from config import QUEST_EXP_MULTIPLIER
    random.seed(seed)
    h = Hero(spec, role, tier, gen)
    done, skipped = set(), set()
    pending = list(world.quests)
    dungeon_xp_left = collections.Counter()
    safety = 0
    while h.level < 60 and safety < 200000:
        safety += 1
        ok = [q for q in pending
              if q.get("level_min", 1) <= h.level
              and quest_level(q) > grey_level(h.level)
              and all(r in done or r in skipped for r in (q.get("requires_quests") or []))]
        if not ok:
            # NOTHING TO DO: grind the open world at this level until something opens up (a level-up)
            pool = world.grind_pool(h.level)
            if not pool:
                break
            n, z = random.choice(pool)
            foe = world.spawn(n, z, level=max(1, h.level + random.choice((-1, 0, 0, 1))))
            if foe is not None:
                h.log[h.band()]["grind_fights"] += 1
                h.fight([foe], f"grinding {n}")
            continue
        q = min(ok, key=quest_level)
        pending.remove(q)
        zone = world.zone_for(q)
        result = do_quest(h, q, world, zone)
        b = h.log[h.band()]
        if result == "dungeon":
            skipped.add(q["quest_id"])
            b["dungeon_quests_skipped"] += 1
            dungeon_xp_left[h.band()] += q.get("reward_exp", 0)
            continue
        if result == "failed":
            skipped.add(q["quest_id"])
            b["quests_failed"] += 1
            h.lists[h.band()]["failed"].append(q["title"])
            continue
        done.add(q["quest_id"])
        b["quests"] += 1
        if q.get("elite"):
            b["elite_quests_done"] += 1
        xp = int(q.get("reward_exp", 0) * quest_xp_multiplier(quest_level(q), h.level) * QUEST_EXP_MULTIPLIER)
        h.gain(max(1, xp), "quests")
    return h, dungeon_xp_left, len(pending)


def do_quest(h, q, world, zone):
    """'done', 'dungeon' (a target only found in a dungeon) or 'failed' (couldn't win it in GIVE_UP tries)."""
    from world.zone_classification import is_dungeon
    if zone:
        foe = world.roll(zone, h.level)
        if foe is not None:
            if getattr(foe, "is_boss", False):
                h.log[h.band()]["rares_met"] += 1
            won = h.fight([foe], f"on the road in {zone}: {foe.name}")
            if getattr(foe, "is_boss", False):
                h.rares.append((h.level, foe.name, foe.level, won))
                h.log[h.band()]["rares_won" if won else "rares_lost"] += 1
    for o in q.get("objectives") or []:
        t, target, count = o.get("type"), o.get("target"), int(o.get("count") or 1)
        if t in ("kill", "kill_boss"):
            names = [target] + list(o.get("alt_targets") or [])
            name = next((n for n in names if n in world.where), None)
            if name is None:
                # NOT IN THE OPEN WORLD: a dungeon's or a cave's boss, or something from a hidden place. A solo
                # open-world run doesn't fight those (19 Nov 2026: Ragefire Chasm's bosses, sent for by Orgrimmar's
                # quests, were being fought alone and counted as walls).
                from world.hidden_zones import creature_kinds
                if is_dungeon(q.get("zone") or "") or target in creature_kinds() or (
                        target in world.cm.creatures and world.cm.creatures[target].get("is_boss")):
                    return "dungeon"
                if target not in world.cm.creatures:
                    continue                                 # a target the sim can't spawn: not counted
                name = target
            z = next((p[0] for p in world.where.get(name, []) if p[0] == zone), None) or \
                (world.where.get(name) or [(zone, None, None)])[0][0]
            for _ in range(count):
                if not fight_until(h, lambda: world.spawn(name, z), f"{q['title']}: {name}"):
                    return "failed"
            if t == "kill_boss" and name in world.cm.creatures and world.cm.creatures[name].get("is_boss"):
                h.log[h.band()]["named_quest_kills"] += 1
        elif t == "fetch":
            src = [(c, ch) for c, ch in world.droppers.get(target, []) if c in world.where or c in world.cm.creatures]
            if not src:
                continue
            got = 0
            tries = 0
            while got < count and tries < count * 6:
                tries += 1
                c, ch = random.choice(src)
                z = next((p[0] for p in world.where.get(c, []) if p[0] == zone), None) or \
                    (world.where.get(c) or [(zone, None, None)])[0][0]
                foe = world.spawn(c, z)
                if foe is None:
                    break
                if h.fight([foe], f"{q['title']}: {c}"):
                    if random.random() < ch:
                        got += 1
            if got < count:
                return "failed"
    return "done"


def fight_until(h, make, what):
    for _ in range(GIVE_UP):
        foe = make()
        if foe is None:
            return True
        if h.fight([foe], what):
            return True
    return False


# ------------------------------------------------------------------------------------------------ the rares
def rare_census(world, specs, tier, gen, fights=5, seed=2):
    import sim_viability as V
    random.seed(seed)
    out = []
    for name, zone, sz in world.rares:
        d = world.cm.creatures[name]
        lv = int(sum(d.get("level_range", [1, 1])[:2]) // 2)
        row = {"name": name, "level": lv, "zone_kind": "subzone"}
        for spec, role in specs:
            wins, left = 0, []
            for _ in range(fights):
                with quiet():
                    c = V.make(spec, role, lv, tier, gen)
                foe = world.spawn(name, zone, level=lv)
                try:
                    won, _d, turns, hp = V.fight([c], {id(c): role}, [foe])
                except Exception:                           # noqa: BLE001
                    won, hp = False, {}
                wins += won
                left.append(hp.get(c.name, 0.0) if won else 0.0)
            row[spec] = (wins / fights, statistics.mean(left))
        out.append(row)
    return out


# ------------------------------------------------------------------------------------------------ report
def report(h, dungeon_xp, unfinished):
    from config import get_exp_needed_for_level
    print(f"\n=== {h.spec} ({h.role}): reached level {h.level}, {unfinished} quests never done")
    print("levels | quests  failed dungeon | fights  win%  deaths  grind | hp left  turns | rests/fight | rares met (lost) | XP quests / kills / needed")
    for b in sorted(h.log):
        L = h.log[b]
        need = sum(get_exp_needed_for_level(l) for l in range(b, min(b + 5, 60)))
        hp = h.lists[b]["hp_left"]
        f = max(1, L["fights"])
        print(f"{b:2}-{b + 4:2}  | {L['quests']:5} {L['quests_failed']:6} {L['dungeon_quests_skipped']:7} | "
              f"{L['fights']:6} {100 * L['wins'] / f:5.1f} {L['deaths']:6} {L['grind_fights']:6} | "
              f"{(statistics.mean(hp) if hp else 0):7.2f} {L['turns'] / f:6.1f} | {L['rests'] / f:11.2f} | "
              f"{L['rares_met']:5} ({L['rares_lost']}) | {L['xp_quests']:7} / {L['xp_kills']:7} / {need}")
    killers = collections.Counter(tuple(foes) and foes[0].rsplit(" L", 1)[0] for _lv, _w, foes in h.deaths)
    if killers:
        print("killed by:", ", ".join(f"{n} x{c}" for n, c in killers.most_common(12)))
    lost = [r for r in h.rares if not r[3]]
    if lost:
        print("rares that killed it:", ", ".join(f"{n} (L{fl}, you L{pl})" for pl, n, fl, _w in lost[:12]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--specs", default=DEFAULT_SPECS)
    ap.add_argument("--tier", default="geared")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--json")
    ap.add_argument("--rares-only", action="store_true")
    ap.add_argument("--no-rares", action="store_true")
    ap.add_argument("--zones", help="census only the rares of these zones, comma separated (e.g. a new zone's maps)")
    args = ap.parse_args()
    import pygame
    pygame.init()
    from entities.loot_generator import LootGenerator
    with quiet():
        gen = LootGenerator()
    world = World()
    specs = [tuple(s.split(":")) for s in args.specs.split(",")]
    if args.zones:
        keep = set(args.zones.split(","))
        world.rares = [r for r in world.rares if r[1] in keep]
    print(f"{len(world.quests)} quests ({world.hidden_quests} in hidden places left out), "
          f"{len(world.enc)} open-world zones, {len(world.rares)} subzone rares")
    out = {"runs": {}, "rares": []}
    if not args.rares_only:
        for spec, role in specs:
            h, dxp, unfinished = run(spec, role, args.tier, world, gen, args.seed)
            report(h, dxp, unfinished)
            out["runs"][spec] = {"role": role, "level": h.level,
                                 "bands": {b: dict(v) for b, v in h.log.items()},
                                 "hp_left": {b: statistics.mean(v["hp_left"]) if v["hp_left"] else None
                                             for b, v in h.lists.items()},
                                 "deaths": h.deaths, "rares": h.rares}
            sys.stdout.flush()
    if not args.no_rares:
        rows = rare_census(world, specs, args.tier, gen)
        out["rares"] = rows
        print(f"\n=== rare census: {len(rows)} subzone rares, 5 fights per spec at the rare's level")
        bad = [r for r in rows if any(r[s][0] < 0.6 for s, _r in specs)]
        print(f"{len(bad)} rares that a spec beats under 60% of the time:")
        for r in sorted(bad, key=lambda r: min(r[s][0] for s, _ in specs)):
            cells = "  ".join(f"{s.split('_')[0]} {100 * r[s][0]:3.0f}% {r[s][1]:.2f}" for s, _ in specs)
            print(f"  L{r['level']:2} {r['name'][:34]:34} {cells}")
        easy = [r for r in rows if all(r[s][0] == 1.0 and r[s][1] > 0.75 for s, _ in specs)]
        print(f"{len(easy)} rares every spec beats with over 75% health left (too soft for a rare)")
    if args.json:
        Path(args.json).write_text(json.dumps(out, default=str, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
