#!/usr/bin/env python3
"""Normal dungeons stop paying rep at Revered; a faction's tabard moves a heroic dungeon's kill rep to that faction.

    PYTHONPATH=. python3 tools/qa_tabards_and_dungeon_cap.py

Kyle, 18 Nov 2026: "drop rep gain from Dungeons that are not heroic beyond revered" and "wearing a factions tabbard
will shift all rep gained to that faction". His answers: dungeon kills only, heroics only (docs/tabards_design.md).
Checks, through the real code:
  1. one tabard per faction but the secret one, sold by its quartermaster at Friendly, a real item in the tabard
     slot with no stats and its own icon, and never on the auction house
  2. a character wears it in the tabard slot, and a save keeps it
  3. a normal dungeon's boss pays a faction at Honored and nothing at Revered; the open world still pays at Revered
  4. a heroic pays past Revered
  5. in a heroic with a tabard on, the tabard's faction takes the kill and nobody else gets anything; in a normal
     dungeon or out in the world the tabard does nothing; the secret faction never has a tabard and its rep never
     moves
  6. the combat engine hands the leader's tabard to the rep award
"""
import contextlib
import io
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    import json
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    from world import faction_manager as FM
    from world import tabards as T
    from world.vendor_stock import make_unique
    from world.rep_items import is_rep_item

    fm = FM.get_faction_manager()
    tiers = {t["id"]: t["at"] for t in fm.tiers}
    data = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
    tabs = json.loads((ROOT / "data/items/tabards.json").read_text(encoding="utf-8"))["items"]

    # 1
    want = {fid for fid, f in data.items() if not f.get("secret")}
    have = {d["tabard_of"] for d in tabs.values()}
    check(have == want, f"tabards for {sorted(have ^ want)} are wrong (missing or extra)")
    for tid, d in tabs.items():
        fid = d["tabard_of"]
        sold = [qm for qm, t in data[fid]["rewards"]["vendor_stock"].items() if f"unique:{tid}" in t.get("friendly", [])]
        check(len(sold) == 1, f"{tid} is sold at Friendly by {sold}")
        item = make_unique(tid)
        if check(item is not None, f"{tid} doesn't make an item"):
            check(item.slot == "tabard" and not item.primary_stats and not item.secondary_stats,
                  f"{tid} isn't a plain tabard")
            check(T.faction_of(item) == fid, f"{tid} champions {T.faction_of(item)}")
            check(is_rep_item(item), f"{tid} could go on the auction house")
        check((ROOT / f"assets/icons/gear/{d['icon_id']}.png").exists(), f"{tid} has no icon")
    check(len({d["icon_id"] for d in tabs.values()}) == len(tabs), "two tabards share an icon")

    # 2
    from entities.character import Character
    with contextlib.redirect_stdout(io.StringIO()):
        ch = Character(name="QA", char_class="Warrior", level=60)
    tab = make_unique("tabard_orgrimmar")
    ch.equipment.equip(tab)
    check(ch.equipment.slots.get("tabard") is tab, f"the tabard went to {[k for k, v in ch.equipment.slots.items() if v is tab]}")
    check(T.worn_by(ch) == "orgrimmar", f"worn_by reads {T.worn_by(ch)}")
    from entities.equipment import Equipment
    again = Equipment.from_dict(ch.equipment.to_dict())
    check(T.faction_of(again.slots.get("tabard")) == "orgrimmar", "a save lost the tabard")

    # 3-5, on Orgrimmar's own dungeon
    rfc = "Ragefire Chasm"
    og = fm.factions["orgrimmar"]
    check(FM._zkey(rfc) in og.dungeons and og.dungeon_per_boss > 0, "the rig's dungeon doesn't pay Orgrimmar")

    def standing(fid, tier):
        fm.factions[fid].standing = tiers[tier] + 10

    def paid(**kw):
        return {fid: g for fid, g, _t in fm.award_for_kill("QA Boss", zone=rfc, is_boss=True, **kw)}

    try:
        fm.reset()
        standing("orgrimmar", "honored")
        check(paid().get("orgrimmar", 0) > 0, "a normal dungeon paid nothing at Honored")
        fm.reset()
        standing("orgrimmar", "revered")
        check(paid().get("orgrimmar", 0) == 0, "a normal dungeon paid past Revered")
        check(paid(heroic=True).get("orgrimmar", 0) > 0, "a heroic paid nothing past Revered")
        # the open world isn't capped
        kill = next(((n, a) for n, a in og.kill_rep.items() if a), None)
        if kill:
            fm.reset()
            standing("orgrimmar", "revered")
            got = {fid: g for fid, g, _t in fm.award_for_kill(kill[0], zone="Durotar")}
            check(got.get("orgrimmar", 0) > 0 or og.kill_caps.get(kill[0]),
                  "an open-world kill stopped paying at Revered")
        # 5. the tabard
        fm.reset()
        before = {fid: f.standing for fid, f in fm.factions.items()}
        got = paid(heroic=True, tabard="cenarion_circle")
        check(set(got) == {"cenarion_circle"} and got["cenarion_circle"] > 0,
              f"a heroic in the Cenarion tabard paid {got}")
        moved = {fid for fid, f in fm.factions.items() if f.standing != before[fid]}
        check(moved == {"cenarion_circle"}, f"the tabard kill moved {moved}")
        fm.reset()
        got = paid(tabard="cenarion_circle")
        check("cenarion_circle" not in got and got.get("orgrimmar", 0) > 0,
              f"in a normal dungeon the tabard changed the pay: {got}")
        fm.reset()
        standing("cenarion_circle", "revered")
        got = paid(heroic=True, tabard="cenarion_circle")
        check(got.get("cenarion_circle", 0) > 0, "the tabard's faction stopped at Revered in a heroic")
        check(all(not f.secret for f in (fm.factions[d["tabard_of"]] for d in tabs.values())),
              "a tabard points at a secret faction")
    finally:
        fm.reset()

    # 6
    src = (ROOT / "combat/combat_engine.py").read_text(encoding="utf-8")
    check("tabard=_tabard" in src and "worn_by(self.player)" in src, "combat doesn't pass the leader's tabard")

    print(f"{len(tabs)} tabards; normal dungeons stop at Revered; heroics and tabards checked")
    if fails:
        print(f"FAIL {len(fails)}:")
        for x in fails[:25]:
            print("  ", x)
        return 1
    print("tabards and the dungeon cap OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
