#!/usr/bin/env python3
"""Everything a recruit says or has written about them, in one place, for the rewrite pass.

    PYTHONPATH=. python3 tools/dump_recruit_text.py kourosh_mage tarek_templar ...
    PYTHONPATH=. python3 tools/dump_recruit_text.py --list            # every recruit id, in order

Prints the greeting, the flat backstory, the four background tabs, the five bond stages, the moment prompts, the
traits' names and the keepsake, so a rewrite keeps every fact the recruit already has.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    rec = {r["recruit_id"]: r for r in json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]}
    bonds = json.loads((ROOT / "data/npcs/bonds.json").read_text(encoding="utf-8"))["bonds"]
    keeps = {}
    try:
        kd = json.loads((ROOT / "data/npcs/keepsakes.json").read_text(encoding="utf-8"))
        for k in (kd.get("keepsakes") if isinstance(kd, dict) else kd) or []:
            if isinstance(k, dict) and k.get("recruit_id"):
                keeps[k["recruit_id"]] = k
    except Exception:                                            # noqa: BLE001
        pass
    if "--list" in sys.argv:
        print(" ".join(sorted(rec)))
        return
    for rid in sys.argv[1:]:
        r, b = rec.get(rid), bonds.get(rid, {})
        if r is None:
            print(f"## {rid}: NO SUCH RECRUIT")
            continue
        print(f"## {rid} | {r['name']} | {r.get('gender')} | {r.get('char_class')} ({r.get('spec')}) | L{r.get('level')}"
              f" | stands in {r.get('zone')} | home {r.get('home_town')}")
        print("GREETING:", r.get("greeting"))
        print("BACKSTORY:", r.get("backstory"))
        for k, v in (r.get("background_sections") or {}).items():
            print(f"[{k}]", v.replace("\n\n", " / "))
        for k, v in (b.get("stages") or {}).items():
            print(f"<{k}>", v)
        for m in b.get("moments", []):
            print(f"  moment {m.get('id')} ({m.get('when')}): {m.get('prompt')}")
        k = keeps.get(rid)
        if k:
            print("KEEPSAKE:", k.get("name"), "|", k.get("description"))
        print()


if __name__ == "__main__":
    main()
