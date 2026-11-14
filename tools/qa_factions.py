#!/usr/bin/env python3
"""QA the faction / reputation system.

    PYTHONPATH=. python3 tools/qa_factions.py

Tests the LOOP, not the parts. Every piece of this passed in isolation while I was building it; what
matters is whether turning in a real quest moves real standing, whether that standing actually opens the
shelf and the companion it is supposed to, and whether it survives a save and load.

  1  the ladder is the WoW one, shared by every faction, with the right spans
  2  quest rep lands where the design says: the cluster's quests carry a player to Revered and no further
  3  Exalted is reachable on kills, in a sane number of dungeon clears
  4  kill rep is NARROW - the wildlife pays nothing, which is the whole argument against a flat
     "dungeon mobs give rep" rule
  5  every reward the data promises points at something that exists (quest ids, recruit id, vendor id,
     consumable ids) - a gate onto a ghost is a reward nobody can ever collect and nothing would warn
  6  gates are shut below the threshold and open at it
  7  a real quest turn-in awards standing through QuestManager, not just through the helper
  8  standing round-trips through a save and does not leak between loads
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

pygame.init()
pygame.display.set_mode((64, 64))

from world.faction_manager import FactionManager  # noqa: E402

#: The WoW ladder, which is the contract Kyle asked for. Hard-coded here on purpose: if someone edits the
#: data file's thresholds, this test should fail rather than quietly agree with the new numbers.
WOW = [("hated", -42000), ("hostile", -6000), ("unfriendly", -3000), ("neutral", 0),
       ("friendly", 3000), ("honored", 9000), ("revered", 21000), ("exalted", 42000)]


def _exalted_at(fm, rows):
    """Which quest number, playing level order, crosses Exalted. Level order rather than file order is
    the point: it is the order a player actually turns them in."""
    need = next(t["at"] for t in fm.tiers if t["name"] == "Exalted")
    run = 0
    for i, (_lvl, amt) in enumerate(sorted(rows), 1):
        run += amt
        if run >= need:
            return i
    return len(rows)


def main():
    fails = []
    fm = FactionManager()

    print("== the ladder")
    got = [(t["id"], t["at"]) for t in fm.tiers]
    print("  " + "  ".join(f"{i}:{a}" for i, a in got))
    if got != WOW:
        fails.append(f"ladder is not the WoW ladder: {got}")
    f = fm.get("crimson_codex")
    for fid, fac in fm.factions.items():
        if fac.tiers is not fm.tiers:
            fails.append(f"{fid} carries its own ladder - every faction must share one")
    spans = []
    for st, want in ((0, 3000), (3000, 6000), (9000, 12000), (21000, 21000)):
        f.standing = st
        spans.append(f.progress()[1])
        if f.progress()[1] != want:
            fails.append(f"span at {st} is {f.progress()[1]}, want {want}")
    print(f"  spans {spans}  {'ok' if not fails else 'FAIL'}")

    print("\n== where quests land, per faction")
    # NO TWO FACTIONS MAY CLAIM THE SAME ZONE. With one faction this could not happen; with five it is the
    # first thing that goes wrong, and it goes wrong SILENTLY - quest_reward returns the first match, so a
    # contested zone would pay whichever faction happened to sit earlier in the file.
    claims = {}
    for fid, fac in fm.factions.items():
        for z in fac.quest_rep.get("zones", []):
            claims.setdefault(z, []).append(fid)
    contested = {z: who for z, who in claims.items() if len(who) > 1}
    print(f"  {len(claims)} zones claimed, {len(contested)} contested")
    for z, who in contested.items():
        fails.append(f"zone '{z}' is claimed by {who} - a quest there would pay whoever is listed first")

    totals = {fid: 0 for fid in fm.factions}
    counts = {fid: 0 for fid in fm.factions}
    quests_by_faction = {fid: [] for fid in fm.factions}
    all_zones = set()
    for fn in sorted(Path("data/quests").glob("*.json")):
        qd = json.loads(fn.read_text(encoding="utf-8"))
        for q in (qd["quests"] if "quests" in qd else qd):
            all_zones.add(q["zone"])
            fid, amt = fm.quest_reward(q)
            if fid:
                totals[fid] += amt
                counts[fid] += 1
                quests_by_faction[fid].append((q.get("level_min", 0), amt))
    for fid, fac in fm.factions.items():
        fac.standing = totals[fid]
        # The real invariant is not "everyone reaches Revered" - factions own wildly different amounts of
        # content and a starting-zone tribe should not max out from its own beach. It is that questing
        # meaningfully advances you and NEVER finishes the job.
        tier = fac.tier["name"]
        print(f"  {fac.name:26s} {counts[fid]:4d} quests {totals[fid]:7d} rep -> {tier}")
        if counts[fid] and fac.tier_id in ("neutral",):
            fails.append(f"{fid}: {counts[fid]} quests and still Neutral - the rate is too low to notice")
        # "QUESTS MUST NEVER FINISH THE JOB" was written when the Codex was the only faction and owned
        # 50 quests. It does not survive contact with the Forsaken, who own 370 across twelve zones: at
        # Kyle's band floor of 150 they reach Exalted at quest 255, which is 69% of their pool and is by
        # any measure a long road. Forcing them under the bar would mean paying ~110 a quest, below the
        # band Kyle set on 2026-10-28, so the rule is the thing that was too simple, not the number.
        #
        # What actually matters is WHEN in the pool it happens. Exalted at 69% is a campaign; Exalted at
        # 20% is a faction whose last three tiers are scenery. So the check measures the fraction.
        if fac.tier_id == "exalted":
            at = _exalted_at(fm, quests_by_faction[fid])
            frac = at / max(1, counts[fid])
            print(f"      ...Exalted at quest {at} of {counts[fid]} ({frac:.0%} of the pool)")
            if frac < 0.60:
                fails.append(f"{fid}: Exalted at {frac:.0%} of its quest pool - the last tiers are "
                             f"scenery. Lower the rate or split the territory.")
    unclaimed = sorted(all_zones - set(claims))
    print(f"  zones with no faction: {unclaimed}")

    print("\n== Exalted on kills (the Codex, whose dungeon is authored)")
    from tools import handbuilt_deep_bloom as DB
    DB.build_deep_bloom()
    f.standing = totals["crimson_codex"]
    clear = sum(f.kill_rep.get(c, 0) for (_x, _y, c, _l) in DB.TRASH) \
        + sum(f.kill_rep.get(b, 0) for b in DB.BOSSES)
    need = 42000 - totals["crimson_codex"]
    clears = need / clear if clear else 999
    print(f"  one full clear {clear} rep; {need} to go = {clears:.1f} clears")
    # The band was 3-15 when a Codex quest paid 350. Kyle reset the economy on 2026-10-28 ("most quests
    # should give 150-250... a dungeon boss kill should be 75") and deliberately wanted the top tier to
    # take time, so the ceiling moved. The FLOOR is the part worth asserting: a faction you can Exalt in
    # under three clears has no grind at all. The real pacing picture, per faction, is
    # tools/faction_rep_report.py - this check cannot see the other five.
    if clears < 3:
        fails.append(f"{clears:.1f} dungeon clears to Exalted - under 3 is no grind at all")
    elif clears > 40:
        print(f"  NOTE: {clears:.1f} clears is a long way past what any other faction asks. The Codex "
              f"has 50 quests and one 5-boss dungeon; this is a content gap, not a tuning one.")

    print("\n== kill rep is narrow and real")
    # ONE CREATURE, ONE FACTION - still the rule for NAMED creatures in kill_rep, though no longer for
    # the reason it was written. award_for_kill used to return on the first match, so a creature in two
    # lists silently paid whoever sat earlier in the file. It now pays every faction with a stake, which
    # is deliberate for SHARED DUNGEONS (the Barrens is orc and tauren country both). A named creature in
    # two kill_rep tables is still almost always a copy-paste, so it stays a failure here.
    owners = {}
    for fid, fac in fm.factions.items():
        for c in fac.kill_rep:
            owners.setdefault(c, []).append(fid)
    shared = {c: who for c, who in owners.items() if len(who) > 1}
    print(f"  {len(owners)} creatures pay reputation, {len(shared)} claimed twice")
    for c, who in shared.items():
        fails.append(f"'{c}' pays reputation to {who} - only the first would ever be credited")
    cre = json.loads(Path("data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    wildlife = ["Sporeback Grazer", "Hoarfrost Yeti", "Glimmerjaw", "Lumen Leech", "Barrens Giraffe",
                "Crystalback Skitterer", "Frostward Prowler", "Elder Mottled Boar", "Barrens Hyena"]
    for fid, fac in fm.factions.items():
        paid = [c for c in wildlife if fac.kill_rep.get(c)]
        unknown = [c for c in fac.kill_rep if c not in cre]
        print(f"  {fac.name:26s} {len(fac.kill_rep):2d} enemies, "
              f"{len(unknown)} unknown, {len(paid)} wildlife")
        if paid:
            fails.append(f"{fid}: pays reputation for wildlife: {paid}")
        if unknown:
            fails.append(f"{fid}: kill_rep names creatures that do not exist: {unknown}")

    print("\n== every promised reward exists")
    all_q = set()
    for p in sorted(Path("data/quests").glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        all_q |= {q["quest_id"] for q in (d["quests"] if "quests" in d else d)}
    recruits = {r["recruit_id"] for r in json.loads(Path("data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]}
    vendors = {v["vendor_id"] for v in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]}
    # A vendor's shelf is consumables AND trade materials - vial_empty and whetstone are materials, not
    # consumables, and 38 vendors sell them. Checking consumables alone would have called most of the
    # game broken. Run properly, this found exactly four ghost ids in the whole project, all four of
    # them introduced by the Underdark NPC pass: two potion tiers that do not exist (greater, where the
    # real ladder is minor/standard/superior/mega), a flux tier that does not exist, and lamp_oil, which
    # was never a thing at all. None of them crash. They are just shelves with nothing on them.
    cd = json.loads(Path("data/consumables/consumable_types.json").read_text(encoding="utf-8"))
    cons = {r.get("consumable_id") for v in cd.values() if isinstance(v, list) for r in v}
    mats = json.loads(Path("data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    cons |= set(mats) if isinstance(mats, dict) else {m.get("material_id") for m in mats}
    # A shelf may also hold RECIPE SCROLLS, named by recipe id. 57 recipes carry source "vendor" and
    # are stocked by the vendor they were authored for, so a check that knows only about consumables
    # and materials calls all 57 of them ghosts. This verifier was wrong before the data was - again.
    from world.recipe_manager import _load_all_recipes
    cons |= set(_load_all_recipes())
    # ...AND BAGS WERE THE FOURTH CATEGORY. This set was rebuilt here by
    # hand from whichever data files came to mind, and it had already been
    # wrong twice (see the comment above). All 21 bags in
    # data/items/bags.json are real, buyable and correctly shelved, and
    # this reported 13 of them as items that "do not exist" across roughly
    # 200 vendors. Rather than add a fourth file to the list and wait for
    # the fifth, anything not already recognised is now put to the SAME
    # resolver the vendor screen uses to build its shelves
    # (world/vendor_stock.resolve_vendor_item) - if the game can put it on
    # a shelf, it exists, by definition rather than by a list somebody
    # maintains.
    from world.vendor_stock import resolve_vendor_item
    from world.gathering_manager import GatheringNodeManager
    from entities.consumable_manager import get_consumable_manager
    from entities.loot_generator import LootGenerator
    _cm, _gm, _lg = get_consumable_manager(), GatheringNodeManager(), LootGenerator()

    def sellable(item_id):
        if item_id in cons:
            return True
        return resolve_vendor_item(item_id, consumable_manager=_cm,
                                   gathering_manager=_gm,
                                   loot_generator=_lg) is not None
    for fid, fac in fm.factions.items():
        rw = fac.rewards
        for qid, tier in rw.get("quests", {}).items():
            if qid not in all_q:
                fails.append(f"{fid}: gates quest '{qid}', which does not exist")
            if tier not in {t['id'] for t in fm.tiers}:
                fails.append(f"{fid}: quest '{qid}' gated at unknown tier '{tier}'")
        rec = rw.get("recruit", {})
        if rec and rec.get("recruit_id") not in recruits:
            fails.append(f"{fid}: gates recruit '{rec.get('recruit_id')}', which does not exist")
        for vid, table in rw.get("vendor_stock", {}).items():
            if vid not in vendors:
                fails.append(f"{fid}: unlocks stock for vendor '{vid}', which does not exist")
            for tier, items in table.items():
                if tier not in {t['id'] for t in fm.tiers}:
                    fails.append(f"{fid}: vendor stock gated at unknown tier '{tier}'")
                for it in items:
                    if not sellable(it):
                        fails.append(f"{fid}: unlocks '{it}', which nothing can put on a shelf")
    print(f"  checked {sum(len(f2.rewards.get('quests', {})) for f2 in fm.factions.values())} quest gates, "
          f"{sum(len(t) for f2 in fm.factions.values() for t in f2.rewards.get('vendor_stock', {}).values())} "
          f"stock tiers, {sum(1 for f2 in fm.factions.values() if f2.rewards.get('recruit'))} recruit gates")

    ghosts = {}
    for v in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]:
        for it in v["sells"]:
            if not sellable(it):
                ghosts.setdefault(it, []).append(v["vendor_id"])
    print(f"  vendor shelves holding items that do not exist: {len(ghosts)}")
    for it, who in sorted(ghosts.items()):
        print(f"    {it} -> {who}")
        fails.append(f"vendors sell '{it}', which does not exist: {who}")

    print("\n== detail panel content")
    npcs = {r["npc_id"] for r in json.loads(Path("data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]}
    npcs |= {r["vendor_id"] for r in json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))["vendors"]}
    for fid, fac in fm.factions.items():
        if not fac.lore:
            fails.append(f"{fid}: no lore - the detail panel would open on an empty page")
        led = fac.leader or {}
        if not led.get("name"):
            fails.append(f"{fid}: no leader named")
        nid = led.get("npc_id")
        # A leader the player can actually go and find. A name with no NPC behind it is a dead end the
        # panel advertises.
        if nid and nid not in npcs:
            fails.append(f"{fid}: leader npc_id '{nid}' is not an NPC in the world")
        print(f"  {fac.name}: {len(fac.lore)} lore paragraphs, "
              f"leader {led.get('title','')} {led.get('name','-')}".rstrip()
              + f", npc {'ok' if nid in npcs else 'MISSING' if nid else 'not linked'}")
        # The reward ladder is deliberately NOT shown (Kyle, 2026-10-27) - rewards will span gear,
        # recipes, recruits, quests and zones, and half a ladder teaches the wrong shape. The gates are
        # still checked above; they just are not advertised.
        if getattr(fac, "perks", None):
            fails.append(f"{fid}: still carries a perk ladder - the panel is information only")

    print("\n== gates open at the threshold and not before")
    rows = []
    for st in (0, 3000, 9000, 21000, 42000):
        f.standing = st
        rows.append((f.tier["name"], len(fm.vendor_unlocks("kb_quartermaster")),
                     fm.quest_requirement_met("ud_archive_deeper"),
                     fm.quest_requirement_met("kb_sealed_entry")))
        print(f"  {st:6d} {f.tier['name']:11s} stock={rows[-1][1]} archive={rows[-1][2]!s:5s} "
              f"sealed={rows[-1][3]!s:5s}")
    if rows[0][1] != 0 or rows[0][2] or rows[0][3]:
        fails.append("something is unlocked at Neutral that should not be")

    # NO RECRUIT IS REPUTATION-GATED, and that is the rule rather than a gap.
    # This block used to assert that kesten_the_catalogued was locked at
    # Neutral, which was true until 2026-10-31 and then stopped being true on
    # purpose - Kyle: "Don't rep lock Kesten". The gate came out of
    # data/factions/factions.json in b30559a, recruit_requirement_met went
    # vacuously True for everybody, and this script has been failing on its own
    # stale expectation ever since. Checking the rule he actually set means a
    # gate reappearing gets noticed, instead of its absence being reported
    # forever as a fault.
    gated = [(fid, fac.rewards["recruit"]) for fid, fac in fm.factions.items()
             if fac.rewards.get("recruit")]
    print(f"  recruits behind a reputation gate: {len(gated)} (the rule is none)")
    for fid, r in gated:
        fails.append(f"{fid}: gates recruit '{r.get('recruit_id')}' at "
                     f"'{r.get('standing')}' - no companion is reputation-gated "
                     f"(Kyle, 2026-10-31)")
    if not rows[-1][3]:
        fails.append("Exalted does not unlock everything it should")
    if rows[1][2]:
        fails.append("the Honored-gated quest is offered at Friendly")
    if [r[1] for r in rows] != sorted(r[1] for r in rows):
        fails.append("vendor stock does not grow monotonically with standing")

    print("\n== a real quest turn-in moves real standing")
    from world.quest_manager import QuestManager, QuestStatus
    import world.faction_manager as FMOD
    FMOD._faction_manager = FactionManager()
    live = FMOD.get_faction_manager()
    qm = QuestManager()
    qid = "fd_hoarfang"
    quest = qm.quests.get(qid)
    if quest is None:
        fails.append(f"{qid} did not load, cannot test the turn-in path")
    else:
        class _P:
            inventory = []
            level = 36          # turn_in_quest scales exp off it
        class _Party:
            def award_experience(self, *_a, **_k): return []
            def add_currency(self, *_a, **_k): pass
        quest.status = QuestStatus.READY_TO_TURN_IN
        before = live.standing("crimson_codex")
        qm.turn_in_quest(qid, _P(), _Party())
        after = live.standing("crimson_codex")
        gain = after - before
        print(f"  turning in '{qid}' ({quest.title}): {before} -> {after}  (+{gain})")
        if gain <= 0:
            fails.append("turning in a real quest awarded no reputation")
        if getattr(qm, "faction_gain", None) is None:
            fails.append("QuestManager.faction_gain not set - the dialog has nothing to show")

    print("\n== save round-trip")
    live.get("crimson_codex").standing = 12345
    blob = live.to_dict()
    fresh = FactionManager()
    fresh.load_from_dict(blob)
    print(f"  saved {blob} -> reloaded {fresh.standing('crimson_codex')}")
    if fresh.standing("crimson_codex") != 12345:
        fails.append("standing did not survive a save round-trip")
    empty = FactionManager()
    empty.load_from_dict(None)
    print(f"  a pre-v9 save with no factions block loads at {empty.standing('crimson_codex')} "
          f"({empty.get('crimson_codex').tier['name']})")
    if empty.standing("crimson_codex") != 0:
        fails.append("a save with no factions block did not load at Neutral")

    print("\n" + ("PASS" if not fails else f"FAIL ({len(fails)})"))
    for x in fails:
        print("  -", x)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
