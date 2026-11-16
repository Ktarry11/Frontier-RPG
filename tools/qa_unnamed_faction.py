#!/usr/bin/env python3
"""The "????" faction: 45 items for every class, standing only from frontier bosses, and silence about all of it.

    PYTHONPATH=. python3 tools/qa_unnamed_faction.py

Kyle, 15 Nov 2026 (tools/build_unnamed_faction.py has the full ask). This holds:
  - 15 honored blues at item level 69, 15 revered epics at 78, 15 exalted epics at 85, all worn at 60, every
    one buildable, every epic with a flavour line, and each tier serving tanks, healers, casters and fighters;
  - ALL 30 CLASSES, NOT THE CLASSIC 9 (Kyle: "wheres my tinkerer healer? My caster shield? My strength
    leather? ... STOOOOOOP DEFAULTING TO CLASSIC 9 CLASSES"). Against every one of the 97 specs in
    data/items/spec_gear.json: each finds at least one piece it can wear AND wants at every tier, and three
    across the shop; every armour type is made for every role that wears it (a mail healer, strength leather,
    plate casters, leather and mail tanks...); every weapon any spec carries is on sale, relics, wands, thrown,
    fist weapons and polearms included; every equipment slot; a caster's shield and a healer's shield; and
    trinkets that do something;
  - the faction is "????" with almost nothing to read: one cryptic line, and no lore, no leader, no home;
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
TANKS = {"tank", "shield_tank", "bear", "bear_weapon", "tank_weapon", "tank_any"}
SLOTS = {"head", "neck", "shoulder", "back", "chest", "wrist", "hands", "waist", "legs", "feet", "ring", "trinket",
         "main_hand", "off_hand", "ranged"}
bad = []


def tags(C, ident):
    """Who a piece is for, by its stats: tank, healer, caster, or a fighter by agility and/or strength."""
    w = C.IDENTITIES[ident][0]
    if ident in TANKS:
        return {"tank"}
    if "healing_power" in w:
        return {"healer"}
    if any(k.endswith("spell_power") for k in w):
        return {"caster"}
    out = set()
    if "agility" in w:
        out.add("agi")
    if "strength" in w:
        out.add("str")
    if "strength" in w and "intellect" in w:
        out.add("str_int")
    if ident == "physical":
        out |= {"agi", "str"}
    return out


def wants(spec):
    """What a spec wants, from its role and stat template (spec_gear.json)."""
    role, tpl = spec["role"], spec["stat_template"]
    if role in ("tank", "healer"):
        return {role}
    if tpl == "int_caster":
        return {"caster"}
    if tpl in ("agi_physical", "agi_int_hybrid"):
        return {"agi"}
    if tpl == "str_physical":
        return {"str"}
    return {"caster", "str_int"} if role == "ranged_dps" else {"str", "str_int"}


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
        check(len(ids) == 15, f"{tier}: {len(ids)} items, not 15")
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
            if d["identity"] in TANKS:
                roles.add("tank")
            elif "healing_power" in w:
                roles.add("healer")
            elif any(k.endswith("spell_power") for k in w):
                roles.add("caster")
            else:
                roles.add("fighter")
        check(roles == {"tank", "healer", "caster", "fighter"}, f"{tier}: serves only {sorted(roles)}")

    # ---- every class, every spec, every slot (not the classic 9)
    from entities.character import Character
    from entities.proficiency import can_equip
    specs = {k: v for k, v in json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8")).items()
             if isinstance(v, dict) and "class" in v}
    with quiet():
        chars = {sp["class"]: Character("QA", sp["class"], 60) for sp in specs.values()}
        built = {k: make_unique(k) for k in items}
    check(len(chars) == 30, f"{len(chars)} classes in spec_gear.json, not 30")
    thin = []
    for sid, sp in specs.items():
        total = 0
        for tier in want:
            n = sum(1 for uid in shelf.get(tier, []) if built.get(uid[7:]) is not None
                    and tags(C, items[uid[7:]]["identity"]) & wants(sp)
                    and can_equip(chars[sp["class"]], built[uid[7:]])[0])
            check(n >= 1, f"{sid}: nothing at {tier} it can use and wants")
            total += n
        thin.append(total)
        check(total >= 3, f"{sid}: only {total} pieces across the shop")
    for sid, sp in specs.items():
        made = [d for d in items.values() if d["slot"] not in ("back",) and d.get("armor_type") == sp["armor_type"]
                and tags(C, d["identity"]) & wants(sp)]
        check(made, f"nothing in {sp['armor_type']} made for {sid} ({sp['role']}, {sp['stat_template']})")
    sold = {d.get("weapon_type") for d in items.values()}
    for sid, sp in specs.items():
        for w in sp["weapons"].values():
            check(w is None or w in sold, f"{sid} carries a {w}, and none is sold")
    check(SLOTS <= {d["slot"] for d in items.values()}, f"no {sorted(SLOTS - {d['slot'] for d in items.values()})}")
    shields = [tags(C, d["identity"]) for d in items.values() if d.get("weapon_type") == "shield"]
    for need in ("tank", "healer", "caster"):
        check(any(need in t for t in shields), f"no {need}'s shield")
    trinkets = [d for d in items.values() if d["slot"] == "trinket"]
    check(len(trinkets) >= 3, f"{len(trinkets)} trinkets")
    for d in trinkets:
        check(bool((d.get("proc") or {}).get("describe")), f"{d['name']}: a trinket that does nothing")

    # ---- the faction says nothing
    check(rec.get("name") == "????" and rec.get("secret") is True, "the faction isn't the secret '????'")
    for field in ("lore", "leader", "home_zone", "home_name"):
        check(not rec.get(field), f"the faction advertises its {field}")
    # one cryptic line (Kyle: "Give a cryptic ass description too"), and it gives nothing away
    desc = rec.get("description") or ""
    check(bool(desc), "the faction has no cryptic line")
    for word in ("frontier", "boss", "skull", "hidden", "kill", "dungeon", "50", "standing", "rep"):
        check(word not in desc.lower().split() and f" {word}" not in f" {desc.lower()}",
              f"the cryptic line gives away '{word}'")
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

    print(f"'????': {len(items)} items for {len(specs)} specs of {len(chars)} classes (fewest any spec gets: "
          f"{min(thin)}), {len(frontiers)} frontier zones pay its standing, seller parked")
    if bad:
        print(f"FAIL: {len(bad)}")
        for b in bad:
            print("  - " + b)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
