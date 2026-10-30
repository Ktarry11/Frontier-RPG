#!/usr/bin/env python3
"""Move thirteen of the new recruits to Kyle's layout, and RE-LEVEL them to their new zone.

    PYTHONPATH=. python3 tools/relocate_wave_two_recruits.py [--check]

Kyle, 29 Oct 2026: "We can add 4 of them into org, 3 in undercity. 3 in freewind post. Then Kesten
is in the underdark, lets add one more. So thats 12.... the other 8 can be in STV, 1000 needles,
more in ashenvale, then bootybay too"

and, crucially: "dont forget players are spec locked and leveled to the zone theyre found in"

THAT SECOND LINE IS WHY THIS IS NOT A COORDINATE EDIT. A recruit's level is a property of where the
player finds them, so moving somebody from Southern Stranglethorn to Orgrimmar takes them from 42 to
14 - and a level-14 character cannot still be the person whose `now` section has him clearing
Bloodsail off the cape road. The spec is locked and the life before the Integration is untouched;
what changes is the level, the zone, the tile, and the paragraph describing what they are doing
today. Thirteen of the nineteen move, and all thirteen get that paragraph rewritten.

LEVELS ARE TAKEN FROM THE ZONE, not invented. Measured off data/creatures/encounters.json and the
recruits already standing there:

    Orgrimmar                 creatures 13-17, Dan sits at 13        -> 12-15
    Undercity                 existing recruits at 10, 11, 12        -> 12-14
    Freewind Post             Southern Thousand Needles is 29-35     -> 31-33
    Crystalline Underdark     creatures 32-40, Kesten at 36          -> 36
    Ashenvale East            creatures 20-32, existing recruit 23   -> 26
    Northern Stranglethorn    creatures 30-34                        -> 32

Undercity is the one where the creature table disagrees with itself - it reads 30-34, which is the
sewers, while the three recruits already standing in it are levels 10 to 12. The recruits win,
because they are what a player actually meets there on the way out of Tirisfal.

EVERY COORDINATE WAS MEASURED. Each zone was built, flooded from its START - or, for Orgrimmar and
Undercity which have no START, from a known-good existing NPC tile - and the picks are reachable,
three clear of every NPC and vendor, and off the outer 8% border. verify() redoes all of it rather
than trusting the table.

THE SIX WHO DO NOT MOVE keep their zone, level and text untouched: Jun-seo and Alonso in Central
Stranglethorn, Fiona, Ziad and Pieter in Southern, Delroy in Booty Bay. They were already levelled
to where they stand.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

RECRUITS = ROOT / "data/npcs/recruits.json"

#: recruit_id -> (zone, level, x, y, new `now` paragraph, new `forward` or None to keep)
MOVES = {
    # ---- Orgrimmar (4). The Horde capital, and the first city most recruits see. ----------------
    "tomas_warrior": (
        "Orgrimmar", 14, 93, 87,
        "Orgrimmar, up in the scaffolding over the Valley of Strength, because the orcs build fast "
        "and tie off badly and he cannot walk past it. He is paid in food and the occasional "
        "argument. He has not drawn the sword on anything worse than a training post yet.",
        "He wants to build something that stays up. He has been looking at the way this city holds "
        "its roofs on with an expression the orcs find difficult."),
    "kiet_rogue": (
        "Orgrimmar", 13, 93, 82,
        "Orgrimmar, where there are more locks than anyone would expect and most of them are bad. "
        "He opens them for people who ask and occasionally for people who have not, and he has "
        "made himself quietly necessary to about nine households.",
        "He wants to know what the old stonework here is hiding, and he has worked out that the "
        "answer is a long way south, which has not deterred him."),
    "minh_chronomancer": (
        "Orgrimmar", 15, 88, 86,
        "Orgrimmar, near the drill grounds, where there is always somebody being carried off the "
        "sand. He has become the person the trainers send for before a bout rather than after one. "
        "He still strikes the fork when he is thinking, and the orcs have stopped remarking on it.",
        None),
    "esteban_bloodmage": (
        "Orgrimmar", 12, 98, 88,
        "Orgrimmar, doing the work the city's healers will not, which in a city this size is a "
        "steady trade. He keeps a ledger of his own use that nobody has asked to see and that he "
        "would show to anyone who did.",
        None),

    # ---- Undercity (3). Forsaken capital, and a short walk out of Tirisfal. ---------------------
    "stelios_necromancer": (
        "Undercity", 13, 106, 104,
        "The Undercity, among the Forsaken, writing down what the dead remember because nobody else "
        "is bothering. The Dark Lady's people regard him as a harmless infestation and let him "
        "work, which is the most comfortable he has been in years.",
        None),
    "marisol_priest": (
        "Undercity", 12, 101, 104,
        "The Undercity, where people stop being people and nobody marks the moment. She has started "
        "holding services for them, badly attended, and the Forsaken have begun to notice that she "
        "does not flinch and does not pity them either.",
        "She wants the forgotten dead of this city named. She is aware this is an absurd project "
        "and has allocated the rest of her life to it."),
    "pavlo_knight": (
        "Undercity", 14, 106, 109,
        "The Undercity, in the lower rings where the lamps are furthest apart. He takes the work "
        "nobody wants down a flooded corridor, and he is at his best in a place with one way out.",
        None),

    # ---- Freewind Post (3). Southern Thousand Needles, on the mesas. ----------------------------
    "driss_shaman": (
        "Freewind Post", 32, 89, 100,
        "Freewind Post, on a mesa where the wind does not stop between one month and the next, "
        "which is the first thing since he arrived that has felt like his old ridge. He is the only "
        "person up there who finds the weather legible rather than hostile.",
        "He wants to stay somewhere with weather, and having finally found it he has stopped "
        "putting off the question of what he does next."),
    "imelda_primalist": (
        "Freewind Post", 31, 88, 105,
        "Freewind Post, where the tauren walk the lifts and the drop does the rest, and the injured "
        "come in steadily. She has become something the Post asks for by name without being able to "
        "describe. She still wraps her hands before anything else, including breakfast.",
        None),
    "ratih_ranger": (
        "Freewind Post", 33, 84, 99,
        "Freewind Post, above a canyon floor that was under water once and is not now, which is a "
        "thing nobody up there has written down and she cannot stop thinking about. She is on good "
        "terms with exactly one tauren and no goblins.",
        None),

    # ---- The Crystalline Underdark (1, joining Kesten) ------------------------------------------
    "kourosh_mage": (
        "The Crystalline Underdark", 36, 85, 14,
        "The Crystalline Underdark, where the lattice does something to arcane magic that nobody "
        "has characterised, and he is characterising it. He has filled most of a case with "
        "measurements and has told two people, both of whom changed the subject.",
        None),

    # ---- Ashenvale East (1) ---------------------------------------------------------------------
    "tarek_templar": (
        "Ashenvale East", 26, 82, 115,
        "Eastern Ashenvale, among ruins that are older than the Integration and are being taken "
        "apart faster than anybody is recording them. He stands at the front of whoever is walking "
        "and, when there is a lull, writes down what the carvings said before the saws reach them.",
        "He wants the ruins recorded properly, not at a run, with somebody holding a lamp. He has "
        "not asked anyone yet because he knows how it sounds."),

    # ---- Northern Stranglethorn (1) --------------------------------------------------------------
    "eino_barbarian": (
        "Northern Stranglethorn", 32, 54, 95,
        "The Vine Road and the cutline fork, taking whatever the Grom'gol convoys will pay for and "
        "spending almost none of it. He is liked more than he has noticed and would be embarrassed "
        "to learn it.",
        None),
}


def main():
    check = "--check" in sys.argv
    doc = json.loads(RECRUITS.read_text())
    rows = doc["recruits"] if isinstance(doc, dict) and "recruits" in doc else doc
    by_id = {r["recruit_id"]: r for r in rows}

    missing = [k for k in MOVES if k not in by_id]
    if missing:
        raise SystemExit(f"not in recruits.json: {missing}")

    import hashlib
    asher = by_id.get("asher_coleman")
    if asher is None:
        raise SystemExit("asher_coleman missing - refusing to run")
    asher_before = hashlib.sha256(json.dumps(asher, sort_keys=True).encode()).hexdigest()

    print(f"{'recruit':24}{'from':34}{'to':34}level")
    changes = 0
    for rid, (zone, level, x, y, now, forward) in MOVES.items():
        r = by_id[rid]
        before = f"{r['zone']} ({r['x']},{r['y']}) L{r['level']}"
        after = f"{zone} ({x},{y}) L{level}"
        if (r["zone"], r["level"], r["x"], r["y"]) != (zone, level, x, y):
            changes += 1
        print(f"  {r['name']:22}{before:34}{after:34}{r['level']} -> {level}")
        if not check:
            r["zone"], r["level"], r["x"], r["y"] = zone, level, x, y
            r["background_sections"]["now"] = now
            if forward:
                r["background_sections"]["forward"] = forward

    if check:
        print(f"\n{changes} would move")
        return 1 if changes else 0

    RECRUITS.write_text(json.dumps(doc, indent=2) + "\n")
    after_doc = json.loads(RECRUITS.read_text())
    arows = after_doc["recruits"] if isinstance(after_doc, dict) and "recruits" in after_doc else after_doc
    a2 = next(r for r in arows if r["recruit_id"] == "asher_coleman")
    if hashlib.sha256(json.dumps(a2, sort_keys=True).encode()).hexdigest() != asher_before:
        raise SystemExit("Asher changed - this should be impossible")
    print(f"\nmoved {changes}; Asher unchanged")
    return 0


def verify():
    """Rebuild every zone that now holds a recruit and re-check each placement."""
    import importlib
    from collections import deque

    import numpy as np

    from world.zone_keys import zone_key as zk

    MODULES = {
        "Orgrimmar": "orgrimmar", "Undercity": "undercity", "Freewind Post": "freewind_post",
        "Ashenvale East": "ashenvale_east", "The Crystalline Underdark": "underdark",
        "Northern Stranglethorn": "stranglethorn_north",
        "Central Stranglethorn": "stranglethorn_central",
        "Southern Stranglethorn": "stranglethorn_south", "Booty Bay": "booty_bay",
    }
    doc = json.loads(RECRUITS.read_text())
    rows = doc["recruits"] if isinstance(doc, dict) and "recruits" in doc else doc
    amb = json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text())["npcs"]
    ven = json.loads((ROOT / "data/npcs/vendors.json").read_text())["vendors"]
    wave = set(MOVES) | {"junseo_reaper", "alonso_pyromancer", "fiona_witchhunter",
                         "ziad_felsworn", "pieter_guardian", "delroy_witchdoctor"}
    problems = []
    for zone, mod in MODULES.items():
        mine = [r for r in rows if r["zone"] == zone and r["recruit_id"] in wave]
        if not mine:
            continue
        m = importlib.import_module(f"tools.handbuilt_{mod}")
        L = m.build_layout()
        z, W, H = L.z, m.W, m.H
        walk = np.zeros((H, W), bool)
        for yy in range(H):
            for xx in range(W):
                walk[yy, xx] = z.is_walkable(xx, yy)
        occ = {(e["x"], e["y"]) for e in amb + ven if zk(e.get("zone", "")) == zk(zone)}
        seed = getattr(m, "START", None) or next((o for o in occ if walk[o[1], o[0]]), None)
        seen = np.zeros_like(walk)
        if seed:
            dq = deque([(int(seed[0]), int(seed[1]))])
            seen[int(seed[1]), int(seed[0])] = True
            while dq:
                x, y = dq.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < W and 0 <= ny < H and walk[ny, nx] and not seen[ny, nx]:
                        seen[ny, nx] = True
                        dq.append((nx, ny))
        for r in mine:
            x, y = r["x"], r["y"]
            if not (0 <= x < W and 0 <= y < H):
                problems.append(f"{r['name']}: ({x},{y}) outside {zone}")
            elif not walk[y, x]:
                problems.append(f"{r['name']}: ({x},{y}) not walkable in {zone}")
            elif seed and not seen[y, x]:
                problems.append(f"{r['name']}: ({x},{y}) walled off in {zone}")
            near = [o for o in occ if abs(o[0] - x) <= 2 and abs(o[1] - y) <= 2]
            if near:
                problems.append(f"{r['name']}: within 2 of an NPC at {near[0]}")
        print(f"  {zone:28} {len(mine)} recruit(s) checked")
    return problems


if __name__ == "__main__":
    code = main()
    if "--check" not in sys.argv:
        print("\nverifying placements:")
        probs = verify()
        if probs:
            print(f"\n{len(probs)} problem(s):")
            for p in probs:
                print(f"  {p}")
            raise SystemExit(1)
        print("  all placements walkable, reachable and clear")
    raise SystemExit(code)
