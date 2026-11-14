#!/usr/bin/env python3
"""The six "the party sees what the enemy will do" abilities show it.

    python3 tools/qa_reveal_intent.py

Six recruit abilities promised foresight and showed nothing. Cast each in a real fight: the log
must name what an enemy will do, and the enemy must then do exactly that.
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party
    from world.recruit_manager import get_recruit_manager

    doc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict) else rm.recruits)}
    bad, n = [], 0
    for kid, kit in doc.items():
        if kid.startswith("_"):
            continue
        for a in kit["abilities"]:
            mode = a.get("reveals_intent")
            if not mode:
                continue
            n += 1
            ch = recs[kid].build_character()
            foes = [Monster("Kolkar Outrunner", "humanoid_warrior", ch.level),
                    Monster("Kolkar Stormer", "humanoid_caster", ch.level + 2)]
            party = Party(ch) if True else None
            eng = CombatEngine(ch, foes[0], party=party, enemies=foes)
            for res in ("rage", "energy", "mana", "focus", "power"):
                for attr in (f"max_{res}", f"current_{res}"):
                    if isinstance(getattr(ch, attr, None), (int, float)):
                        setattr(ch, attr, 9999)
            ab = next(x for x in ch.ability_book.get_all_abilities() if x.ability_id == a["ability_id"])
            try:
                rtype = ab._effective_resource_type(ch)
                ch.set_resource(rtype, max(ch.get_resource_max(rtype) or 0, 9999))
            except Exception:
                pass
            if eng.revealed_intents():
                bad.append(f"{kit['name']}: intents visible before {a['name']} is cast")
            target = foes[0] if a["target_type"] in ("enemy",) else (foes if "enem" in a["target_type"] else ch)
            ok, msg = ab.use(ch, target, party=[ch], engine=eng)
            seen = eng.revealed_intents()
            want = 2 if (mode == "all" and a["target_type"] != "enemy") else 1
            if not ok or len(seen) != want:
                bad.append(f"{kit['name']} / {a['name']}: cast={ok} ({msg!r}), {len(seen)} enemies revealed, wanted {want}")
                continue
            eng.announce_intents()
            if not any(l.startswith("Foreseen: ") for l in eng.combat_log):
                bad.append(f"{kit['name']} / {a['name']}: nothing in the combat log")
            # and it is TRUE: the enemy then does what was foreseen
            for foe, text in seen.items():
                name = text.split(" on ")[0]
                did = foe.choose_action(eng.default_target_for(foe)).name
                if did != name:
                    bad.append(f"{kit['name']} / {a['name']}: foresaw {name!r}, {foe.name} does {did!r}")
    print(f"{n} foresight abilities")
    if n != 7:
        bad.append(f"expected 7 abilities carrying reveals_intent, found {n}")
    if bad:
        print("FAIL:")
        for b in bad:
            print("  " + b)
        return 1
    print("OK: each one tells the party what the enemy will do, and the enemy does it")
    return 0


if __name__ == "__main__":
    sys.exit(main())
