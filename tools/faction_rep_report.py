#!/usr/bin/env python3
"""What it actually takes to reach each tier with each faction.

    PYTHONPATH=. python3 tools/faction_rep_report.py

WHY THIS EXISTS. Reputation pacing is the one number in this game that cannot be judged by reading the
data file. "350 a quest" tells you nothing; "the Forsaken own 370 quests, so that is Exalted by the
halfway mark" tells you everything, and the second number is six lines of arithmetic nobody was doing.

Kyle, 2026-10-28: "reaching max rep should take time too. Most quests should give 150-250 rep. Even with
the codex. A dungeon boss kill should be 75 each in the Dungeons linked to that faction."

So the three things this prints are the three things that decide whether that is true:
  * what the faction's whole quest pool is worth, and which tier that alone lands in
  * what one full clear of each linked dungeon is worth
  * how many clears close the gap to Exalted from there

A faction whose quest pool alone passes Exalted has no grind at all. A faction with no dungeon has no way
to finish. Both are visible in one screen here and in no other way.
"""
import importlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from world.zone_generator import create_all_zones          # noqa: E402
from world.zone_classification import DUNGEONS as ALL_DUNGEONS  # noqa: E402


#: Dungeons whose trash packs live in their own layout module rather than in trash_packs.json.
MODULE_PACKS = {
    "The Deep Bloom": "tools.handbuilt_deep_bloom",
    "Widow's Lair": "tools.handbuilt_widows_lair",
    "Ambermill Tower": "tools.handbuilt_ambermill_tower",
    "Shadowpine Altar": "tools.handbuilt_shadowpine_altar",
    # The Grotto has no handbuilt module and no entry in trash_packs.json - it is generated in
    # tools/ashenvale_silverpine_fenris_generators.py and its trash is not authored as a pack list, so
    # its per-clear number here is BOSSES ONLY and is a floor, not the real figure.
}


def tier_at(tiers, standing):
    out = tiers[0]["name"]
    for t in tiers:
        if standing >= t["at"]:
            out = t["name"]
    return out


def main():
    d = json.loads((ROOT / "data/factions/factions.json").read_text())
    tiers, F = d["tiers"], d["factions"]
    exalted = next(t["at"] for t in tiers if t["name"] == "Exalted")

    quests = []
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        data = json.loads(f.read_text())
        qs = data.get("quests", [])
        quests += qs if isinstance(qs, list) else list(qs.values())

    Z = create_all_zones()
    packs = json.loads((ROOT / "data/dungeons/trash_packs.json").read_text())
    boss_count, bosses_in, trash_in = {}, {}, {}
    for dn in ALL_DUNGEONS:
        z = Z.get(dn)
        bp = list(getattr(z, "boss_positions", None) or [])
        if not bp and getattr(z, "boss_position", None):
            bp = [z.boss_position]
        boss_count[dn] = len(bp)
        bosses_in[dn] = [b[2] for b in bp if len(b) > 2]
        # Every trash body in the dungeon, counted once per spawn - a clear kills all of them.
        #
        # PACKS LIVE IN TWO PLACES. Most dungeons keep theirs in data/dungeons/trash_packs.json, but five
        # (the Deep Bloom among them) keep a TRASH list in their own handbuilt module instead. Reading
        # only the json made the Deep Bloom look like 0 trash rep and the Codex look like a 72-clear
        # grind, when qa_factions - which imports the module - said 11.8 and was right. Read both.
        rows = packs.get(dn) or []
        trash_in[dn] = [m[2] for pack in rows for m in pack if len(m) > 2]
        if not trash_in[dn]:
            mod = MODULE_PACKS.get(dn)
            if mod:
                try:
                    M = importlib.import_module(mod)
                    trash_in[dn] = [t[2] for t in getattr(M, "TRASH", []) if len(t) > 2]
                    if not bosses_in[dn]:
                        bosses_in[dn] = list(getattr(M, "BOSSES", []))
                except Exception as exc:                       # a missing module is reportable, not fatal
                    print(f"  (could not read {dn} packs from {mod}: {exc})")

    print(f"Exalted = {exalted}\n")
    orphan_dungeons = set(ALL_DUNGEONS)
    for fid, f in F.items():
        qr, dr = f["quest_rep"], f.get("dungeon_rep", {})
        zs = set(qr.get("zones", [])) | set(qr.get("also", []))
        mine = [q for q in quests if q.get("zone") in zs]
        nb = sum(1 for q in mine
                 if any(o.get("type") == "kill_boss" for o in q.get("objectives", [])))
        caps = qr.get("capstones", {})
        qtotal = (len(mine) - nb) * qr["default"] + nb * qr["boss"] + sum(caps.values())

        per_boss = dr.get("per_boss", 0)
        dungs = dr.get("dungeons", [])
        orphan_dungeons -= set(dungs)
        kr = f.get("kill_rep", {}).get("creatures", {})
        # A FULL CLEAR IS NOT JUST THE BOSSES. The first version of this tool counted per_boss alone and
        # reported 72 clears for the Codex; qa_factions said 11.8 and qa_factions was right. A faction
        # that already names dungeon TRASH in its kill_rep gets paid for that trash too, and for the
        # Codex that is most of the value. Counting only the new rule made the old one invisible.
        per_clear = {}
        for x in dungs:
            v = sum(max(kr.get(n, 0), per_boss) for n in bosses_in.get(x, []))
            v += sum(kr.get(n, 0) for n in trash_in.get(x, []))
            per_clear[x] = v
        sweep = sum(per_clear.values())

        print(f"== {f['name']}  ({fid})")
        print(f"   quests  {len(mine):>4} in {len(zs)} zones  "
              f"({qr['default']}/{qr['boss']} boss, {len(caps)} capstones)  = {qtotal:>6}"
              f"   -> {tier_at(tiers, qtotal)}")
        if not dungs:
            print("   dungeons  NONE LINKED - this faction cannot reach Exalted by any route.")
        else:
            for x in dungs:
                nb_ = len(bosses_in.get(x, []))
                trash = sum(kr.get(n, 0) for n in trash_in.get(x, []))
                print(f"     {x:<28} {nb_:>2} bosses + {trash:>5} trash rep "
                      f"= {per_clear[x]:>5}/clear")
            gap = exalted - qtotal
            if gap <= 0:
                print(f"   Exalted on quests alone, {-gap} over. Dungeons are optional.")
            else:
                print(f"   gap to Exalted {gap:>6}  = {gap / sweep:>5.1f} full sweeps of all "
                      f"{len(dungs)} ({sweep}/sweep)")
        print()

    if orphan_dungeons:
        print("DUNGEONS LINKED TO NO FACTION (their bosses pay nobody):")
        for x in sorted(orphan_dungeons):
            print(f"  {x} ({boss_count.get(x, 0)} bosses)")


if __name__ == "__main__":
    main()
