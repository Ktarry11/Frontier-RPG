#!/usr/bin/env python3
"""Every faction's quartermaster sells by standing, TBC-style, and the shop really shows it.

    PYTHONPATH=. python3 tools/qa_faction_rewards.py

Kyle, 15 Nov 2026: "Revered give lvl 60 ilvl 67 blues and exalted gives lvl 60 ilvl 73 epics... aim for 6
blues per vendor AND 3 epics per vendor. There will also be crafting stuff for rep. I WANT THIS TO BE LIKE HOW
TBC DEALS WITH REP!!!", "I want the epics to be around 250g to 350g", and "exalted rep recipes make epics as
well! Around Ilvl 73". Built by tools/build_faction_rewards.py. Per faction this holds:
  - a quartermaster who exists;
  - revered: 6 rare items, ilvl 66, worn at 60; exalted: 3 epics, ilvl 68, worn at 60, priced 250-350g;
  - patterns at honored and revered, and 2 exalted recipes whose items are ilvl 68 epics worn at 60;
The levels moved on 18 Nov 2026 to Kyle's level-60 ladder (tools/relevel_rep_gear.py): Revered 66 like a heroic's
blues, Exalted 68 like the Fallen Bluff's epics, Honored 62.
  - nothing on the faction's shelves is also on a town's (a rep pattern is the faction's only);
  - the vendor screen shows all of it at exalted and none of it at neutral.
"""
import contextlib
import io
import json
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)

G = 10000
bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)


def main():
    import build_faction_rewards as B
    from world.faction_manager import get_faction_manager
    from world.vendor_manager import get_vendor_manager
    from world.recipe_manager import _load_all_recipes
    from world.vendor_stock import resolve_vendor_item, make_unique
    items = json.loads((ROOT / "data/items/faction_rewards.json").read_text(encoding="utf-8"))["items"]
    fd = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    town_stock = {s for v in vendors for s in v.get("sells", [])}
    recipes = _load_all_recipes()
    fm, vm = get_faction_manager(), get_vendor_manager()

    import pygame
    pygame.init()
    pygame.display.set_mode((1280, 720))
    from entities.character import Character
    from entities.party import Party
    from ui.screens.vendor_screen import VendorScreen

    class SM:
        def __init__(self):
            with contextlib.redirect_stdout(io.StringIO()):
                self.player = Character(name="Buyer", char_class="Warrior", level=60)
            self._party = Party(self.player)

        def get_party(self):
            return self._party

        def transition_to(self, *a, **k):
            pass

    def shown(vid):
        with contextlib.redirect_stdout(io.StringIO()):
            scr = VendorScreen(SM(), vm.vendors[vid])
        return {getattr(i, "_sells_id", None) for i in scr.vendor_inventory}

    # EVERY faction with a shelf, not only the nine build_faction_rewards.py wrote (Kyle, 17 Nov 2026: "Ensuring
    # variation in all rep vendors?"): the Pale Flame and the Argent Dawn (build_plaguelands_rewards.py) and the
    # Timbermaw (build_timbermaw_hold.py) are held to the same rules
    import build_plaguelands_rewards as PR
    import build_timbermaw_hold as TM
    import build_sunreach_conclave as SC          # the Sunreach Conclave (18 Nov 2026)
    import build_liquidators as LQ          # Deadwind's Liquidators (18 Nov 2026)
    import build_moonglade as MGF           # Moonglade's Cenarion Circle and the Wakened (18 Nov 2026)
    import build_feathermoon_sentinels as FMS   # Feralas's Feathermoon Sentinels (19 Nov 2026)
    QMS = {**B.QM, **PR.QM, TM.FID: TM.QM_ID, SC.FID: SC.QM, LQ.FID: LQ.QM, **MGF.QM, **FMS.QM}
    REVERED = {**B.REVERED, **PR.REVERED, TM.FID: TM.REVERED, SC.FID: SC.REVERED, LQ.FID: LQ.REVERED,
               **MGF.REVERED, **FMS.REVERED}
    EXALTED = {**B.EXALTED, **PR.EXALTED, TM.FID: TM.EXALTED, SC.FID: SC.EXALTED, LQ.FID: LQ.EXALTED,
               **MGF.EXALTED, **FMS.EXALTED}
    EXALTED_RECIPES = {**B.EXALTED_RECIPES, **PR.EXALTED_RECIPES, TM.FID: TM.EXALTED_RECIPES,
                       SC.FID: [r[:8] for r in SC.EXALTED_RECIPES], LQ.FID: [r[:8] for r in LQ.EXALTED_RECIPES],
                       **{f: [r[:8] for r in v] for f, v in MGF.EXALTED_RECIPES.items()},
                       **{f: [r[:8] for r in v] for f, v in FMS.EXALTED_RECIPES.items()}}
    shelved = {fid for fid, f in fd.items() if not f.get("secret") and (f.get("rewards") or {}).get("vendor_stock")}
    check(shelved <= set(QMS), f"factions with a shelf this check doesn't know: {sorted(shelved - set(QMS))}")
    totals = {"blue": 0, "epic": 0, "recipes": 0}
    for fid, qm in QMS.items():
        check(qm in vm.vendors, f"{fid}: quartermaster {qm} doesn't exist")
        if qm not in vm.vendors:
            continue
        stock = (fd[fid].get("rewards") or {}).get("vendor_stock") or {}
        shelf = stock.get(qm, {})
        rev = [i for i in shelf.get("revered", []) if i.startswith("unique:")]
        exa = [i for i in shelf.get("exalted", []) if i.startswith("unique:")]
        check(len(rev) == 6, f"{fid}: {len(rev)} revered items, not 6")
        check(len(exa) == 3, f"{fid}: {len(exa)} exalted items, not 3")
        for uid in rev + exa:
            d = items.get(uid[7:])
            check(d is not None, f"{fid}: {uid} isn't in faction_rewards.json")
            if d is None:
                continue
            want = ("rare", 66) if uid in rev else ("epic", 68)
            check((d["rarity"], d["item_level"]) == want, f"{d['name']}: {d['rarity']} ilvl {d['item_level']}, "
                                                           f"wanted {want}")
            check(d["required_level"] == 60, f"{d['name']}: worn at {d['required_level']}, not 60")
            if uid in exa:
                check(250 * G <= d["price"] <= 350 * G, f"{d['name']}: {d['price'] // G}g, not 250-350g")
            check(make_unique(uid[7:]) is not None, f"{d['name']}: doesn't build")
            check(uid not in town_stock, f"{d['name']}: also sold in a town")
        totals["blue"] += len(rev)
        totals["epic"] += len(exa)
        # the crafting
        pats = {t: [] for t in ("honored", "revered", "exalted")}
        for vid, tiers in stock.items():
            for tier, ids in tiers.items():
                for i in ids:
                    if i in recipes and tier in pats:
                        pats[tier].append(i)
        check(pats["honored"] and pats["revered"], f"{fid}: no patterns at honored or revered")
        check(len(pats["exalted"]) >= 2, f"{fid}: {len(pats['exalted'])} exalted recipes")
        for rid in pats["exalted"]:
            out = recipes[rid][1].get("output") or {}
            it = out.get("item") or {}
            check(it.get("rarity") == "epic" and it.get("item_level") == 68 and it.get("required_level") == 60,
                  f"{rid}: makes {it.get('rarity')} ilvl {it.get('item_level')} worn at {it.get('required_level')}")
        for tier, ids in pats.items():
            for rid in ids:
                check(rid not in town_stock, f"{rid}: a {fid} pattern is also on a town shelf")
                check(resolve_vendor_item(rid) is not None, f"{rid}: no scroll")
        totals["recipes"] += sum(len(v) for v in pats.values())
        # the shop shows it at exalted and hides it at neutral
        f = fm.factions[fid]
        before = f.standing
        for vid, tiers in stock.items():
            if vid not in vm.vendors:
                check(False, f"{fid}: shelf on missing vendor {vid}")
                continue
            gated = {i for ids in tiers.values() for i in ids}
            base = set(vm.vendors[vid].sells)
            f.standing = 0
            low = shown(vid)
            f.standing = 10 ** 6
            high = shown(vid)
            check(gated <= high, f"{vid}: at exalted the shop misses {sorted(gated - high)[:4]}")
            check(not ((gated - base) & low), f"{vid}: at neutral it already shows {sorted((gated - base) & low)[:4]}")
        f.standing = before

    # A DIRECTION, NOT A CAGE (Kyle, 15 Nov 2026: "DONT tunnel people... Don't pigeon hole!!!"): every faction
    # serves tanks, healers, casters and fighters, and single-school spell power is a rare exception
    import build_crafted_gear as C
    ROLE = {"tank": "tank", "shield_tank": "tank", "bear": "tank", "bear_weapon": "tank", "tank_weapon": "tank", "healer": "healer", "high_healer": "healer",
            "tide_healer": "healer", "spirit_healer": "healer", "plate_healer": "healer"}
    SCHOOL = {"fire", "frost", "nature", "shadow", "arcane", "holy"}
    one_school = []
    for fid in QMS:
        rows = [(r[1], r[5]) for r in REVERED[fid] + EXALTED[fid]] + \
               [(r[2], r[6]) for r in EXALTED_RECIPES[fid]]
        roles = set()
        for name, ident in rows:
            w = C.IDENTITIES[ident][0]
            if ident in ROLE:
                roles.add(ROLE[ident])
            elif any(k.endswith("spell_power") for k in w):
                roles.add("caster")
            else:
                roles.add("fighter")
            if [k for k in w if k.replace("_spell_power", "") in SCHOOL]:
                one_school.append(name)
        for need in ("tank", "healer", "caster", "fighter"):
            check(need in roles, f"{fid}: nothing for a {need} - a direction, not a cage")
    check(len(one_school) <= 3, f"{len(one_school)} single-school pieces ({', '.join(one_school)}): an exception, "
                                f"not a rule")

    print(f"{len(QMS)} factions: {totals['blue']} revered blues, {totals['epic']} exalted epics, {totals['recipes']} patterns "
          f"and recipes")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad[:60]:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
