#!/usr/bin/env python3
"""Does a same-level tank in greens or blues survive a 5-man pull everywhere? (Kyle, 27 Nov 2026)

    "smoke test with aggro on tanks that when they're in 5man groups in open world, skull zones, frontier zones,
    Dungeons, and dungeon skull zones that an appropriate level tank in greens to blues isn't instantly slaughtered"

Real creatures from every kind of place, at their own level, against a full party: a specced tank in its tank posture
and a Combat Rogue in the front row, a Fire Mage, a Holy Priest and a Marksmanship Hunter behind. The tank is dressed
all green or all blue at its level; the others in the sims' usual gear.

    open           an open zone's own creatures, packs of three        (world bands 10 to 54)
    skull_zone     a hidden open-world map's trash packs, and its bosses
    frontier_open  a frontier open map's trash packs, and its bosses
    dungeon        a real dungeon's trash packs (cave), and its bosses
    hidden_layer   a hidden level under a dungeon (the dungeon skull zone): trash packs and bosses
    frontier_deep  a frontier cave or dungeon: trash packs and bosses

What it reports, per place, tank and gear: the party's wins, how often the tank is still standing at the end, how
often it was SLAUGHTERED (dead within its first three hits taken, which is what "instantly" means here), and the
biggest single hit it took as a share of its health.

The sim's party plays simply: everyone attacks, the healer heals anyone under 55%, nobody presses a defensive cooldown
or a taunt. A player does better, so treat these as a floor.

    PYTHONPATH=. python3 tools/sim_tank_survival.py [--fights 3] [--tanks warrior_protection,paladin_protection]
                                                     [--only dungeon] [--gear green,blue]
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

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: every tank in the game: Classic's three, the twelve CoA tanks, and the Enhancement Shaman's Earthen Guardian
DEFAULT_TANKS = ["warrior_protection", "paladin_protection", "druid_feral", "shaman_enhancement",
                 "felsworn_tyrant", "bloodmage_eternal", "templar_oathkeeper", "starcaller_moon_guard",
                 "witch_hunter_black_knight", "venomancer_fortitude", "sun_cleric_seraphim",
                 "primalist_mountain_king", "reaper_domination", "guardian_vanguard", "knight_of_xoroth_defiance",
                 "cultist_dreadnought"]
DPS = [("rogue_combat", "melee_dps"), ("mage_fire", "ranged_dps"), ("priest_holy", "healer"),
       ("hunter_marksmanship", "ranged_dps")]
#: every healer in the game (Kyle, 27 Nov 2026: "Check all tanks and healers if possible"). The healer slot cycles
#: through these fight by fight, so every healer meets every kind of place without multiplying the run by fourteen.
HEALERS = ["priest_holy", "priest_discipline", "paladin_holy", "druid_restoration", "shaman_restoration",
           "tinker_invention", "pyromancer_flameweaving", "starcaller_moon_priest", "cultist_heretic",
           "sun_cleric_blessings", "witch_doctor_brewing", "venomancer_vizier", "chronomancer_time",
           "primalist_grovekeeper",
           # the Frost Mage's Cryotherapist (Kyle: "Cryotherapist for mage too. Frost Healer"): Frostbolt and Ice Lance
           # heal the neediest ally off the damage they deal, so it heals by attacking
           "mage_frost"]
WORLD_BANDS = [(10, "Durotar"), (17, "Silverpine North"), (25, "Ashenvale West"),
               (34, "Arathi Central"), (45, "The Abyssal Sands"), (54, "Tempest Shallows")]
#: the dungeons to sample (cave name -> its overworld zone in encounters.json is looked up)
DUNGEONS = ["Ragefire Chasm", "Wailing Caverns", "Shadowfang Keep", "Razorfen Kraul"]
SLAUGHTER_HITS = 3


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def dress_as(char, gen, level, rarity):
    """Every slot at this rarity (the sims' dress() picks green under 20 and blue above)."""
    from tools.sim_class_balance import GEAR_SLOTS, TWO_HANDED_TYPES
    for slot in GEAR_SLOTS:
        try:
            item = gen.generate_item_for_class(char.char_class, level, slot=slot, rarity=rarity)
        except Exception:                                      # noqa: BLE001
            continue
        if item is None:
            continue
        if slot == "off_hand":
            mh = char.equipment.slots.get("main_hand")
            if mh is not None and getattr(mh, "weapon_type", "") in TWO_HANDED_TYPES:
                continue
        char.inventory.append(item)
        if not char.equip_item(item) and item in char.inventory:
            char.inventory.remove(item)


def make_tank(spec, level, gen, rarity):
    from tools import sim_role_balance as SR
    from tools.sim_class_balance import dress
    with quiet():
        t = SR.build(spec, level, gen, dress, role="tank")
        t = t[0] if isinstance(t, tuple) else t
        dress_as(t, gen, level, rarity)
        if t.char_class == "Warrior":
            t.current_stance = "defensive"
        elif t.char_class == "Shaman":
            t.guardian_stance_active = True
        elif t.char_class == "Bloodmage" and getattr(t, "current_form", None) != "eternal":
            t.shift_form("eternal")
        elif hasattr(t, "toggle_tank_stance") and not getattr(t, "tank_stance", None):
            from combat.tank_stance import stance_for_class, in_tank_posture
            if stance_for_class(t.char_class) and not in_tank_posture(t):
                t.toggle_tank_stance()
        if hasattr(t, "_recalculate_derived_stats"):
            t._recalculate_derived_stats()
    t.name = "Tank"
    t.current_health = t.health
    if getattr(t, "mana", 0):
        t.current_mana = t.mana
    return t


def make_party(spec, level, gen, rarity, healer="priest_holy"):
    from entities.party import FRONT_ROW, BACK_ROW
    from tools import sim_role_balance as SR
    from tools.sim_class_balance import dress
    tank = make_tank(spec, level, gen, rarity)
    others = []
    with quiet():
        for s, role in DPS:
            if role == "healer":
                s = healer
            o = SR.build(s, level, gen, dress, role=role)
            o = o[0] if isinstance(o, tuple) else o
            o.current_health = o.health
            if getattr(o, "mana", 0):
                o.current_mana = o.mana
            others.append(o)
    names = ["Rogue", "Mage", "Healer", "Hunter"]
    for o, n in zip(others, names):
        o.name = n
    tank.row = FRONT_ROW
    others[0].row = FRONT_ROW
    for o in others[1:]:
        o.row = BACK_ROW
    return [others[0], tank] + others[1:], tank


def fight(chars, tank, foes, rng):
    """One fight. -> (won, tank alive, slaughtered, biggest hit share, healer's lowest mana share, healer's end
    mana share)"""
    from combat.combat_engine import CombatEngine
    from tools import sim_difficulty as SD
    hits = []
    f = tank.take_damage
    healer = next((c for c in chars if c.name == "Healer"), None)
    low = [1.0]
    hs = healer.spend_resource if healer is not None and hasattr(healer, "spend_resource") else None

    def watch(*a, **k):
        r = hs(*a, **k)
        if healer.mana:
            low[0] = min(low[0], healer.current_mana / healer.mana)
        return r
    if hs is not None:
        healer.spend_resource = watch

    def wrap(*a, **k):
        before = tank.current_health
        r = f(*a, **k)
        lost = max(0, before - tank.current_health)
        if lost:
            hits.append(lost)
        return r
    tank.take_damage = wrap
    try:
        won, hp, _turns = SD.run(chars, foes, rng)
    finally:
        tank.take_damage = f
        if hs is not None:
            healer.spend_resource = hs
    alive = hp.get(tank.name, 0) > 0
    slaughtered = (not alive) and len(hits) <= SLAUGHTER_HITS
    biggest = max(hits) / max(1, tank.health) if hits else 0.0
    if healer is None or not getattr(healer, "mana", 0):
        return won, alive, slaughtered, biggest, None, None          # a healer with no mana pool
    end = healer.current_mana / healer.mana
    low[0] = min(low[0], end)
    return won, alive, slaughtered, biggest, low[0], end


def pools(cm):
    """{place: [(level, [creature names] for a pack, is_boss_fight)]}"""
    from world.hidden_zones import creature_kinds
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    out = collections.defaultdict(list)

    def lvl(n):
        return (cm.creatures[n].get("level_range") or [1, 1])[1]

    for level, zone in WORLD_BANDS:
        table = enc.get(zone, {}).get("open_zone", {}).get("creatures", {})
        pool = [n for n, w in table.items() if w and n in cm.creatures and not cm.creatures[n].get("is_boss")]
        if pool:
            out["open"].append((level, pool, False))

    kinds = creature_kinds()
    for kind in ("skull_zone", "frontier_open", "hidden_layer", "frontier_deep"):
        names = [n for n, k in kinds.items() if k == kind and n in cm.creatures]
        trash = [n for n in names if not cm.creatures[n].get("is_boss")]
        bosses = [n for n in names if cm.creatures[n].get("is_boss")]
        # trash grouped by level: a pack is three creatures within two levels of each other
        by_level = collections.defaultdict(list)
        for n in trash:
            by_level[lvl(n)].append(n)
        for L in sorted(by_level)[:: max(1, len(by_level) // 4)][:4]:
            near = [n for n in trash if abs(lvl(n) - L) <= 2]
            out[kind].append((L, near, False))
        for b in sorted(bosses, key=lvl)[:: max(1, len(bosses) // 3)][:3]:
            out[kind].append((lvl(b), [b], True))

    for zone, info in enc.items():
        for cave, cinfo in (info.get("caves") or {}).items():
            if cave not in DUNGEONS:
                continue
            names = [n for n, w in (cinfo.get("creatures") or {}).items() if w and n in cm.creatures]
            trash = [n for n in names if not cm.creatures[n].get("is_boss")]
            if trash:
                L = round(statistics.median(lvl(n) for n in trash))
                out["dungeon"].append((L, trash, False))
    from tools.sim_difficulty import DUNGEON_BOSSES
    for cave, bosses, _ in DUNGEON_BOSSES:
        if cave in DUNGEONS:
            for b in bosses:
                if b in cm.creatures:
                    out["dungeon"].append((lvl(b), [b], True))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fights", type=int, default=3)
    ap.add_argument("--tanks", default=",".join(DEFAULT_TANKS))
    ap.add_argument("--only", default=None)
    ap.add_argument("--gear", default="green,blue")
    ap.add_argument("--chain", type=int, default=3, help="trash pulls back to back for the healer-mana read")
    args = ap.parse_args()

    from entities.loot_generator import LootGenerator
    from world.creature_manager import CreatureManager
    with quiet():
        gen, cm = LootGenerator(), CreatureManager()
    rng = random.Random(7)
    random.seed(7)
    rarities = {"green": "uncommon", "blue": "rare"}
    tanks = [t.strip() for t in args.tanks.split(",") if t.strip()]
    places = pools(cm)

    print("TANK SURVIVAL - 5-man party, tank in its posture, same-level creatures")
    print(f"{args.fights} fights per creature and gear. won = party won; up = tank standing at the end; slain = tank "
          f"dead within {SLAUGHTER_HITS} hits; hit = biggest single hit / tank health (median, worst); healer = the "
          "Holy Priest's lowest mana (median), and how often it fell under 10%")
    R = collections.defaultdict(lambda: {"n": 0, "won": 0, "up": 0, "slain": 0, "hit": [], "low": [], "oom": 0})
    H = collections.defaultdict(lambda: {"n": 0, "won": 0, "low": [], "end": [], "oom": 0, "band": [], "band_oom": 0,
                                         "chain": [], "chain_band": []})
    worst = []
    cycle = [0]
    for place, cells in places.items():
        if args.only and args.only not in place:
            continue
        for level, pool, is_boss in cells:
            what = pool[0] if is_boss else "pack"
            for gear in args.gear.split(","):
                for spec in tanks:
                    cell = {"n": 0, "slain": 0, "up": 0}
                    for _ in range(args.fights):
                        healer = HEALERS[cycle[0] % len(HEALERS)]
                        cycle[0] += 1
                        with quiet():
                            chars, tank = make_party(spec, level, gen, rarities[gear], healer)
                            from tools.sim_difficulty import spawn
                            foes = [spawn(cm, pool[0] if is_boss else rng.choice(pool), level)
                                    for _ in range(1 if is_boss else 3)]
                        foes = [f for f in foes if f is not None]
                        if not foes:
                            continue
                        loc = "open" if place in ("open", "skull_zone", "frontier_open") else "cave"
                        for f in foes:
                            f.location_type = loc
                        with quiet():
                            w, a, sl, b, lo, end_m = fight(chars, tank, foes, rng)
                        for key in ((place, spec), (place, "ALL")):
                            r = R[key]
                            r["n"] += 1; r["won"] += w; r["up"] += a; r["slain"] += sl
                            r["hit"].append(b)
                            if lo is not None:
                                r["low"].append(lo); r["oom"] += lo < 0.10
                        # THREE PULLS BACK TO BACK (trash only): health topped up, mana carried, so the healer's mana
                        # reads the way it does through a run rather than one fight from full.
                        if not is_boss and lo is not None and args.chain > 1:
                            chain_low = lo
                            for _pull in range(args.chain - 1):
                                for c in chars:
                                    c.current_health = c.health
                                with quiet():
                                    more = [spawn(cm, rng.choice(pool), level) for _ in range(3)]
                                more = [f for f in more if f is not None]
                                for f in more:
                                    f.location_type = loc
                                with quiet():
                                    _w, _a, _s, _b, lo2, _e = fight(chars, tank, more, rng)
                                if lo2 is not None:
                                    chain_low = min(chain_low, lo2)
                            H[healer]["chain"].append(chain_low)
                            if 10 <= level <= 25:
                                H[healer]["chain_band"].append(chain_low)
                        h = H[healer]
                        h["n"] += 1; h["won"] += w
                        if lo is not None:
                            h["low"].append(lo); h["end"].append(end_m); h["oom"] += lo < 0.10
                            if 10 <= level <= 25:
                                h["band"].append(lo); h["band_oom"] += lo < 0.10
                        cell["n"] += 1; cell["slain"] += sl; cell["up"] += a
                    if cell["n"] and cell["slain"] * 2 >= cell["n"]:
                        worst.append(f"{place} L{level} {what} {gear}: {spec} slain {cell['slain']}/{cell['n']}")
        print(f"\n== {place}")
        print(f"   {'tank':<28}{'fights':>7}{'won':>7}{'up':>7}{'slain':>7}   {'hit med/worst':<15}{'healer low':>11}{'<10%':>7}")
        for spec in tanks + ["ALL"]:
            r = R.get((place, spec))
            if not r or not r["n"]:
                continue
            n = r["n"]
            print(f"   {spec:<28}{n:>7}{r['won'] / n:>7.0%}{r['up'] / n:>7.0%}{r['slain'] / n:>7.0%}   "
                  f"{statistics.median(r['hit']):>4.0%}/{max(r['hit']):<9.0%}"
                  f"{(statistics.median(r['low']) if r['low'] else 1):>11.0%}{r['oom'] / max(1, len(r['low'])):>7.0%}")
    print("\nHEALERS - every place together. low = lowest mana in a fight (median); end = mana left at the end "
          "(median); <10% = fights it fell under a tenth; 10-25 = the same two for fights at levels 10 to 25; "
          "3 pulls = lowest mana over three trash pulls back to back (median, and at 10-25)")
    print(f"   {'healer':<26}{'fights':>7}{'won':>7}{'low':>7}{'end':>7}{'<10%':>7}{'10-25 low':>11}{'<10%':>7}"
          f"{'3 pulls':>9}{'10-25':>7}")
    for hs in HEALERS:
        h = H.get(hs)
        if not h or not h["n"]:
            continue
        if not h["low"]:
            print(f"   {hs:<26}{h['n']:>7}{h['won'] / h['n']:>7.0%}   (no mana pool)")
            continue
        bl = (f"{statistics.median(h['band']):>11.0%}{h['band_oom'] / len(h['band']):>7.0%}" if h["band"]
              else f"{'-':>11}{'-':>7}")
        bl += f"{statistics.median(h['chain']):>9.0%}" if h["chain"] else f"{'-':>9}"
        bl += f"{statistics.median(h['chain_band']):>7.0%}" if h["chain_band"] else f"{'-':>7}"
        print(f"   {hs:<26}{h['n']:>7}{h['won'] / h['n']:>7.0%}{statistics.median(h['low']):>7.0%}"
              f"{statistics.median(h['end']):>7.0%}{h['oom'] / len(h['low']):>7.0%}{bl}")
    if worst:
        print("\nCELLS WHERE THE TANK WAS SLAUGHTERED HALF THE TIME OR MORE")
        for w in worst:
            print("  " + w)


if __name__ == "__main__":
    main()
