#!/usr/bin/env python3
"""The "????" faction: 24 items as asked, standing only from frontier bosses, and silence about all of it.

    PYTHONPATH=. python3 tools/qa_unnamed_faction.py

Kyle, 15 Nov 2026 (tools/build_unnamed_faction.py has the full ask). This holds:
  - 8 honored blues at item level 69, 8 revered epics at 78, 8 exalted epics at 85, all worn at 60, every
    one buildable, every epic with a flavour line, and each tier serving tanks, healers, casters and fighters;
  - the faction is "????" with nothing to read: no description, no lore, no leader, no home;
  - a frontier BOSS pays 50, and nothing else pays anything: not trash in a frontier, not a boss elsewhere,
    not a quest;
  - a real combat victory over a frontier boss prints no reputation line and no tier-up for it;
  - the journal draws "Current Status: <tier>" and no numbers for it, in the list and on its page;
  - the seller is parked: in no zone, on no shop's shelf, read by nothing until he is placed.
Locations are never printed (and the seller has none yet).
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

FID = "the_unnamed"
bad = []


def check(ok, msg):
    if not ok:
        bad.append(msg)


def quiet():
    return contextlib.redirect_stdout(io.StringIO())


def main():
    import build_crafted_gear as C
    import build_unnamed_faction as U
    from world.vendor_stock import make_unique
    from world.faction_manager import get_faction_manager, reward_stock
    from world.hidden_zones import registry, kind

    # ---- the items
    items = json.loads((ROOT / "data/items/unnamed_rewards.json").read_text(encoding="utf-8"))["items"]
    fd = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
    rec = fd.get(FID, {})
    shelf = (rec.get("rewards") or {}).get("vendor_stock_unplaced", {}).get(U.VENDOR, {})
    want = {"honored": ("rare", 69), "revered": ("epic", 78), "exalted": ("epic", 85)}
    for tier, (rarity, ilvl) in want.items():
        ids = shelf.get(tier, [])
        check(len(ids) == 8, f"{tier}: {len(ids)} items, not 8")
        roles = set()
        for uid in ids:
            d = items.get(uid[7:])
            check(d is not None, f"{uid}: not in unnamed_rewards.json")
            if d is None:
                continue
            check((d["rarity"], d["item_level"], d["required_level"]) == (rarity, ilvl, 60),
                  f"{d['name']}: {d['rarity']} ilvl {d['item_level']} worn at {d['required_level']}")
            if rarity == "epic":
                check(bool((d.get("flavor_text") or "").strip()), f"{d['name']}: an epic with no flavour line")
            check(make_unique(uid[7:]) is not None, f"{d['name']}: doesn't build")
            w = C.IDENTITIES[d["identity"]][0]
            if d["identity"] in ("tank", "shield_tank", "bear", "bear_weapon", "tank_weapon"):
                roles.add("tank")
            elif "healing_power" in w:
                roles.add("healer")
            elif any(k.endswith("spell_power") for k in w):
                roles.add("caster")
            else:
                roles.add("fighter")
        check(roles == {"tank", "healer", "caster", "fighter"}, f"{tier}: serves only {sorted(roles)}")

    # ---- the faction says nothing
    check(rec.get("name") == "????" and rec.get("secret") is True, "the faction isn't the secret '????'")
    for field in ("description", "lore", "leader", "home_zone", "home_name"):
        check(not rec.get(field), f"the faction advertises its {field}")
    check("vendor_stock" not in (rec.get("rewards") or {}), "the seller's shelf is live, but he isn't placed")
    check(not any(v[0] == FID for v in reward_stock().values()), "a shop already sells the '????' stock")

    # ---- the seller is parked
    vendors = json.loads((ROOT / "data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]
    check(all(v["vendor_id"] != U.VENDOR for v in vendors), "the seller is standing in the world")
    parked = json.loads((ROOT / "data/npcs/unplaced_vendors.json").read_text(encoding="utf-8"))["vendors"]
    check(U.VENDOR in parked and parked[U.VENDOR].get("_unplaced"), "the seller's record is missing")

    # ---- standing: frontier bosses, 50, and nothing else
    fm = get_faction_manager()
    f = fm.get(FID)
    check(f is not None and f.secret and f.frontier_boss_rep == 50, "the faction didn't load as secret, 50 a boss")
    frontiers = [z for z, info in registry().items() if info.get("kind") == "frontier"]
    check(frontiers, "no frontier zones to test with")
    ordinary = next((z for z, info in registry().items() if info.get("kind") and info.get("kind") != "frontier"),
                    "Ashenvale East")
    if f is not None and frontiers:
        def paid(**kw):
            before = f.standing
            fm.award_for_kill("Somebody", **kw)
            return f.standing - before
        check(paid(zone=frontiers[0], is_boss=True) == 50, "a frontier boss didn't pay 50")
        check(paid(zone=frontiers[0], is_boss=False) == 0, "frontier trash paid standing")
        check(paid(zone=ordinary, is_boss=True) == 0, "a boss outside a frontier paid standing")
        check(paid(zone="Ashenvale East", is_boss=True) == 0, "an open-world boss paid standing")

        # ---- a real victory over a frontier boss: standing moves, the log says nothing about it
        from combat.combat_engine import CombatEngine
        from entities.character import Character
        from world.creature_manager import CreatureManager
        with quiet():
            cm = CreatureManager()
            hero = Character("QA", "Druid", 60)
            boss_name = (registry()[frontiers[0]].get("bosses") or [None])[0]
            boss = cm.spawn_creature(boss_name, zone_name=frontiers[0]) if boss_name else None
        check(boss is not None, "couldn't spawn a frontier boss")
        if boss is not None:
            boss.is_boss = True
            f.standing = 2980            # one kill from Friendly, so a tier-up would be due
            with quiet():
                ce = CombatEngine(hero, boss, zone=frontiers[0])
                for e in ce.enemies:
                    e.current_health = 0
                ce._resolve_victory()
            check(f.standing == 3030, f"the victory moved '????' to {f.standing}, not 3030")
            log = " ".join(str(x) for x in ce.combat_log)
            check("????" not in log, "the combat log names '????'")
            check(FID not in ce.faction_gains, "the victory screen counts '????' gains")
        f.standing = 0

        # ---- the journal: "Current Status", never a number
        import pygame
        pygame.init()
        surf = pygame.display.set_mode((1280, 720))
        from tools.shot_screen import StubSM, build
        from ui.screens.quest_journal_screen import QuestJournalScreen
        with quiet():
            player, party = build("Druid", 60)
        f.standing = 12345
        drawn = []
        scr = QuestJournalScreen(StubSM(player, party))
        real = scr.renderer.draw_text

        def spy(screen, text, *a, **k):
            drawn.append(str(text))
            return real(screen, text, *a, **k)
        scr.renderer.draw_text = spy
        scr.active_tab = "reputation"
        with quiet():
            scr._render_reputation(surf) if hasattr(scr, "_render_reputation") else scr.render(surf)
            scr.selected_faction_id = FID
            scr._render_faction_detail(surf)
        f.standing = 0
        check(any(t.startswith("Current Status: ") for t in drawn), "the journal never says 'Current Status'")
        check(not any("12345" in t or "3345" in t for t in drawn), "the journal shows '????' standing as a number")

    print(f"'????': {len(items)} items, {len(frontiers)} frontier zones pay its standing, seller parked")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
