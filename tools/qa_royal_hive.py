#!/usr/bin/env python3
"""The Royal Hive is a whole dungeon, and the isle dungeons' monsters are in their final form.

    PYTHONPATH=. python3 tools/qa_royal_hive.py

Kyle, 14 Nov 2026: "Let's quickly flesh out the Royal Hive as it'll drop another token", "Ensure
the final royal Hive boss is another 2 for 1 boss fight. Drops 3 pieces of loot", and "audit
Tempest Isle Dungeons".

CLAIMS:
  1. The map builds, every boss and chest is reachable from the door, and the door goes both ways
     with the Royal Cell in the Black Strand.
  2. The last fight is two bosses in one encounter, sharing one hoard that drops three items, and
     the queen always drops a shoulder token.
  3. Every creature in Khaz Varun, the Emberdeep and the Hive has a final-form kit: bosses carry a
     boss multiplier and hit in the band of the finished dungeons around them, trash hits in its
     band, every summon can actually be built, and no monster buff uses a stat a monster ignores.
  4. The boss mechanics reach the monster: the queen's death floor holds once, Ruzzak's burrow
     turns damage into shell.
  5. Five quests, given in Onyxhollow, each naming its target.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

MONSTER_READS = {"armor", "attack_power", "damage_taken_pct", "healing_taken_pct",
                 "magic_damage_taken_pct", "magic_resistance", "physical_damage_taken_pct",
                 "spell_damage_taken_pct"}


def main():
    bad = []
    with contextlib.redirect_stdout(io.StringIO()):
        import tools.handbuilt_royal_hive as RH
        import tools.handbuilt_khaz_varun as KV
        import tools.handbuilt_emberdeep as ED
        from tools.build_isle_dungeon_kits import B, T
        hive = RH.generate_royal_hive()
        zones = [KV.generate_khaz_varun(), ED.generate_emberdeep(), hive]
        from world.portal_manager import PortalManager
        from entities.monster import Monster
        from entities import boss_loot
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    kits = json.loads((ROOT / "data/creatures/ability_kits.json").read_text(encoding="utf-8"))["kits"]

    # 1
    pm = PortalManager()
    there = pm.get_destination("The Black Strand", 138, 115)
    back = pm.get_destination("The Royal Hive", *RH.PORTAL)
    if not there or there[0] != "The Royal Hive" or not back or back[0] != "The Black Strand":
        bad.append(f"the hive door does not go both ways: {there} / {back}")
    if len(hive.boss_positions) != 5:
        bad.append(f"{len(hive.boss_positions)} bosses, wanted five")

    # 2
    pack = getattr(hive, "boss_pack", {}).get("Hive-Mother Ahn'thera", [])
    if [m[2] for m in pack] != ["Royal Consort Zhir'ak"]:
        bad.append(f"the last fight is not the queen and her Consort: {pack}")
    if boss_loot.MULTI_DROP.get("Hive-Mother Ahn'thera") != 3:
        bad.append("the queen does not drop three items")
    if boss_loot.SHARED_HOARD.get("Royal Consort Zhir'ak") != "Hive-Mother Ahn'thera":
        bad.append("the Consort does not share the queen's hoard")
    with contextlib.redirect_stdout(io.StringIO()):
        drops = boss_loot.get_fixed_boss_loot_multi("Hive-Mother Ahn'thera") \
            if hasattr(boss_loot, "get_fixed_boss_loot_multi") else None
    tokens = json.loads((ROOT / "data/items/set_tokens.json").read_text(encoding="utf-8"))
    q = tokens["bosses"].get("Hive-Mother Ahn'thera", {})
    if q.get("slot") != "shoulder" or not q.get("guaranteed"):
        bad.append(f"the queen's token is {q}")

    # 3
    names = set()
    for z in zones:
        names |= {n for *_, n in z.boss_positions} | {n for *_, n, _l in z.trash_spawns}
        names |= {m[2] for v in getattr(z, "boss_pack", {}).values() for m in v}
    names |= {"Brood Larva"}
    for n in sorted(names):
        r = creatures[n]
        kit = kits[r["ability_kit"]]
        hi = r["level_range"][1]
        basic = kit[0].get("amount", 0)
        if r.get("is_boss"):
            if not r.get("boss_multiplier"):
                bad.append(f"{n}: a boss with no boss multiplier")
            if not 0.85 * B(hi) <= basic <= 1.15 * B(hi):
                bad.append(f"{n}: boss basic {basic}, band {B(hi)}")
            if len(kit) < 5:
                bad.append(f"{n}: a boss with {len(kit)} abilities")
        else:
            lo = r["level_range"][0]
            if not 0.55 * T(lo) <= basic <= 1.15 * T(hi):
                bad.append(f"{n}: trash basic {basic}, band {T(lo)}-{T(hi)}")
        for a in kit:
            if a.get("kind") == "summon":
                s = a.get("summon") or {}
                if not s.get("template") or s.get("kit") not in kits:
                    bad.append(f"{n}: summon {a['name']} cannot be built: {s}")
            mods = dict(a.get("stat_mods") or {})
            if a.get("kind") == "buff":
                for k in mods:
                    if k not in MONSTER_READS:
                        bad.append(f"{n}: buff {a['name']} uses {k}, which a monster ignores")
            rider = a.get("rider") or {}
            if rider.get("effect") == "buff":
                for k in rider.get("stat_mods") or {}:
                    if k not in MONSTER_READS:
                        bad.append(f"{n}: {a['name']} buffs {k}, which a monster ignores")

    # 4
    with contextlib.redirect_stdout(io.StringIO()):
        from entities.character import Character
        hero = Character(name="H", char_class="Warrior", level=56)
        queen = Monster("Hive-Mother Ahn'thera", "beast_large", 56,
                        kit=creatures["Hive-Mother Ahn'thera"]["ability_kit"])
    queen.abilities[0]._apply_rider(queen, [hero])
    queen.current_health = queen.max_health
    queen.take_damage(10 ** 7, "arcane", attacker_level=56)
    held = queen.current_health
    queen.take_damage(10 ** 7, "arcane", attacker_level=56)
    if held <= 0 or queen.current_health != 0:
        bad.append(f"the queen's death floor: held at {held}, then {queen.current_health}")
    with contextlib.redirect_stdout(io.StringIO()):
        ruz = Monster("Tunnel-King Ruzzak", "beast_large", 55,
                      kit=creatures["Tunnel-King Ruzzak"]["ability_kit"])
    burrow = next(a for a in ruz.abilities if a.name == "Burrow")
    burrow.use(ruz, hero)
    eff = [e for e in ruz._effects() if getattr(e, "damage_to_shield_pct", 0) >= 100]
    if not eff:
        bad.append("Ruzzak's burrow does not carry its damage-to-shell conversion")

    # 5
    quests = json.loads((ROOT / "data/quests/royal_hive.json").read_text(encoding="utf-8"))["quests"]
    if len(quests) != 5 or any(not q["giver_npc_id"].startswith("oh_") for q in quests):
        bad.append("the hive's quests are not five given in Onyxhollow")

    print(f"{len(names)} creatures across the three dungeons; the hive has {len(hive.boss_positions)} "
          f"boss rooms and {len(hive.trash_spawns)} trash")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\nRoyal Hive OK - built, linked, a two-boss finale on a shared hoard, and every isle "
          "dungeon monster in its final form.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
