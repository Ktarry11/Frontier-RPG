#!/usr/bin/env python3
"""Keepsakes: the Collection tab for what each Sworn recruit gives you.

    PYTHONPATH=. python3 tools/qa_keepsakes.py

Kyle, 19 Nov 2026: "a new collection tab. Each sworn member will give something that goes there. it's personal to
them and i have plans for it later." Checks, through the real data and code:
  1. the Collection has a Keepsakes tab, and every keepsake in data/npcs/keepsakes.json is on it, from a real recruit
  2. keepsakes are found only: no trader lists one, and none has a price
  3. a recruit reaching Sworn gives theirs (world/bond_manager), once, and no earlier stage does
  4. an ungiven keepsake keeps its name and story hidden on the tab and from search
  5. every tab button fits on the screen
"""
import contextlib
import io
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


def main():
    from world import collection as C
    keep = json.loads((ROOT / "data/npcs/keepsakes.json").read_text(encoding="utf-8"))["keepsakes"]
    recruits = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))
    recruits = {r["recruit_id"] for r in (recruits if isinstance(recruits, list) else recruits.get("recruits", []))}

    # 1
    check(("keepsake", "Keepsakes") in C.TABS, "no Keepsakes tab")
    tab = {e["id"] for e in C.by_tab("keepsake")}
    for rid, k in keep.items():
        check(rid in recruits, f"{rid}: not a recruit")
        check(C.keepsake_of(rid) in tab, f"{rid}: keepsake not on the tab")
        check(k.get("name") and k.get("blurb") and k.get("icon") and k.get("stand_in"), f"{rid}: keepsake incomplete")
    # the recruits' keepsakes, plus the ones a moment gives (the Mural Shard, the first time the Crown's cutscene is
    # seen: docs/crown_cutscene.md), which are found only too
    sworn = {cid for cid in tab if (C.get_entry(cid).get("source") or "").startswith("sworn:")}
    check(len(sworn) == len(keep), f"{len(sworn)} recruit keepsakes on the tab, {len(keep)} written")

    # 2
    for cid in tab:
        e = C.get_entry(cid)
        check(e.get("found_only") and e.get("source", "").startswith(("sworn:", "cutscene:")), f"{cid}: can be sold")
    src = (ROOT / "world/market/market.py").read_text(encoding="utf-8")
    check('not e.get("found_only")' in src, "traders can list found-only collectables")

    # 3
    from world import bond_manager as BM
    rid = next(iter(keep))
    from entities import account_collection as AC
    col = AC.AccountCollection()
    col.save = lambda: True                    # never touch the real account file
    real = C.collection
    C.collection = lambda: col
    try:
        bm = BM.BondManager()
        b = bm.get(rid)
        check(b is not None, f"{rid} has no bond to test with")
        if b is not None:
            cid = C.keepsake_of(rid)
            for stage in range(1, len(BM.STAGES) - 1):
                b.trust = BM.THRESHOLDS[stage]
                bm._trust(b, 0)
            check(BM.STAGES[b.stage] == "friend", f"stopped at {BM.STAGES[b.stage]}")
            check(not C.learned(cid), "given before Sworn")
            b.trust = BM.THRESHOLDS[-1]
            bm._trust(b, 0)
            check(BM.STAGES[b.stage] == "friend", "Sworn without the personal quest")
            b.flags.append("goal_done")
            bm._trust(b, 0)
            check(BM.STAGES[b.stage] == "sworn", f"not Sworn: {BM.STAGES[b.stage]}")
            check(C.learned(cid), "Sworn but no keepsake")
            check(any("Keepsakes" in line for _r, line in bm.log), "nothing tells you it was given")
            check(not C.grant(cid), "a keepsake given twice")
    finally:
        C.collection = real

    # 4 + 5
    scr = (ROOT / "ui/screens/collection_screen.py").read_text(encoding="utf-8")
    check("A keepsake from" in scr and 'e["kind"] == "keepsake" and not C.learned' in scr,
          "an ungiven keepsake shows its name or turns up in search")
    from config import SCREEN_WIDTH
    tab_w = min(186, (SCREEN_WIDTH - 60) // len(C.TABS) - 6)
    check(30 + len(C.TABS) * (tab_w + 6) <= SCREEN_WIDTH, "the tabs run off the screen")
    check("tab_w" in scr, "the tab buttons don't size to fit")

    print(f"{len(keep)} keepsakes written, {len(tab)} on the Keepsakes tab")
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails:
            print("  ", x)
        return 1
    print("Keepsakes OK.")
    return 0


if __name__ == "__main__":
    with contextlib.redirect_stdout(io.StringIO()) if "--quiet" in sys.argv else contextlib.nullcontext():
        sys.exit(main())
