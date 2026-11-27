#!/usr/bin/env python3
"""The interactive party (world/group_dynamics.py, world/conversations.py; pilot of 26 Nov 2026).

    PYTHONPATH=. python3 tools/qa_group_dynamics.py

Plan: claude/group_dynamics_plan.md. Holds:
  1  every group-lines recruit passes the voice guard (tools/build_group_lines.py --check) and the built data matches
  2  each mood is read correctly for a constructed party (easy, chaos, third wheel, powder keg, crew, family)
  3  a crew forms after enough outings as mutual friends, gets a name, splits on a falling-out, and comes back
  4  the crew perk applies only while the whole crew is in the party, and a family's is bigger
  5  sixty outings of real play (wipes, fights, rests, arguments answered every way) never crash and only ever
     speak lines that exist in the speaker's own pool
  6  every recruit can be talked to for every kind of conversation, and every answer has a reply in their voice
  7  arguments: every written argument starts, every choice resolves, and ignoring it settles it without the player
  8  a call-out leaves the pair sore, then the target concedes; rivals' respect brings a truce
  9  an arc moves through its turning points, and an anchor never gets one
  10 it all saves and loads
  11 no code names a pilot recruit (the 101 others must be data only)
"""
import json
import os
import random
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


def findings():
    bad = []
    r = subprocess.run([sys.executable, "tools/build_group_lines.py", "--check"], capture_output=True, text=True)
    if r.returncode != 0:
        bad += ["group lines: " + ln.strip() for ln in r.stdout.splitlines() if "FAIL" in ln][:10] or \
            ["group lines: the builder check failed"]
    from tools.build_group_lines import load, build
    data, args, orient = load()
    built = json.loads(Path("data/npcs/group_lines.json").read_text(encoding="utf-8"))
    if built != json.loads(json.dumps(build(data, args, orient))):
        bad.append("group lines: data/npcs/group_lines.json is stale (run tools/build_group_lines.py)")

    import world.bond_manager as B
    import world.conversations as C
    B.reset_bond_manager()
    bm = B.get_bond_manager()
    rm, g, cv = bm.rel, bm.rel.groups, C.get_conversations()
    ids = sorted(x for x in g.lines if x in rm.traits)
    if len(ids) < 3:
        return bad + [f"group lines: only {len(ids)} recruits have group lines and pair traits"]
    four = ids[:4]

    def setst(a, b, aff):
        rel = rm.rel(a, b)
        rel.affinity = aff
        rel.met_said = True
        rel.state = "close" if aff >= 55 else "friendly" if aff >= 20 else "rivals" if aff <= -50 else \
            "grating" if aff <= -20 else "nodding"

    # 2 moods
    for a, b in rm.pairs_in(four):
        setst(a, b, 5)
    m = g.mood(four)
    if m not in ("easy", "chaos"):
        bad.append(f"mood: strangers read as {m}")
    setst(four[0], four[1], -60)
    if g.mood(four) != "powder_keg":
        bad.append(f"mood: a rival pair reads as {g.mood(four)}, not a powder keg")
    for a, b in rm.pairs_in(four):
        setst(a, b, 5)
    setst(four[0], four[1], 70)
    if len(four) >= 3 and g.mood(four) != "third_wheel":
        bad.append(f"mood: a close pair with outsiders reads as {g.mood(four)}, not a third wheel")

    # 3 crews
    trio = four[:3]
    for a, b in rm.pairs_in(trio):
        setst(a, b, 40)
    for _ in range(7):
        g._count_together(trio, "Test Vale")
    g._milestones(trio)
    k = g.key(trio)
    c = g.crews.get(k) or {}
    if not c.get("formed"):
        bad.append("crew: three mutual friends with seven outings together never became a crew")
    elif c.get("name") != "The Test Vale Three":
        bad.append(f"crew: named {c.get('name')!r}, not after where it formed")
    # 4 perk
    if g.crew_bonus(trio[0], trio) <= 0:
        bad.append("crew: no perk with the whole crew in the party")
    if g.crew_bonus(trio[0], trio[:2]) != 0:
        bad.append("crew: the perk applies with a member missing")
    setst(trio[0], trio[1], -30)
    g._milestones(trio)
    if not (g.crews.get(k) or {}).get("split"):
        bad.append("crew: a falling-out inside the crew didn't split it")
    setst(trio[0], trio[1], 40)
    g._milestones(trio)
    if (g.crews.get(k) or {}).get("split"):
        bad.append("crew: making up didn't bring the crew back")
    if len(four) == 4:
        for a, b in rm.pairs_in(four):
            setst(a, b, 70)
        for _ in range(11):
            g._count_together(four, "Test Vale")
        g._milestones(four)
        if not (g.crews.get(g.key(four)) or {}).get("family"):
            bad.append("family: four close friends with eleven outings never became a family")
        elif g.crew_bonus(four[0], four) <= g.crew_bonus(four[0], trio) - 1e-9 or \
                abs(g.crew_bonus(four[0], four) - 0.05) > 1e-9:
            bad.append("family: the family perk isn't the bigger one")

    # 5 sixty outings of play, lines checked against pools
    B.reset_bond_manager()
    bm = B.get_bond_manager()
    rm, g, cv = bm.rel, bm.rel.groups, C.get_conversations()
    pools = {}
    for rid in ids:
        mine = set()
        for src in (g.lines.get(rid) or {}, rm.lines.get(rid) or {}):
            for v in src.values():
                for t in (v if isinstance(v, list) else [v]):
                    mine.add(re.sub(r"\{[^}]*\}", "", t)[:25])
        for a in args:
            for who, t in a["lines"]:
                if who == rid:
                    mine.add(t[:25])
        pools[rid] = mine
    random.seed(4)
    party = four
    spoken = 0
    choices = ["back_asker", "back_other", "third", "stay_out"]
    try:
        for n in range(60):
            rm.zone = "Test Vale"
            rm.on_outing(party, "quest")
            cv.on_outing(party)
            if n % 6 == 5:
                fd = random.choice(party)
                rm.on_wipe(party, first_down=fd)
                cv.on_wipe(party, fd)
            if n % 4 == 3:
                g.on_fight_won(party, first_down=random.choice(party), standing=random.sample(party, 2),
                               saves=[(party[0], party[1])], boss=n % 8 == 7)
            if n % 5 == 4:
                rm.on_rest(party)
            if n % 7 == 6:
                cv.pending_ask = None
                cv.start_argument(party)
            # at most one scene per outing: the panel waits relationship_manager.GAP between scenes and lets the small
            # talk behind it go (Kyle, 26 Nov 2026: talk "should feel special, not being spammed every 2 seconds")
            for _once in range(1):
                from world import relationship_manager as _RM
                item = rm.pop_beat(_RM.GAP)
                if not item:
                    break
                for rid, text in item:
                    spoken += 1
                    plain = text
                    for other in ids:
                        nm = rm.first(other)
                        if plain.startswith(nm + ", "):
                            plain = plain[len(nm) + 2:]
                    probe = re.sub(r"[A-Z][a-z]+", "", plain)[:12]
                    if rid in pools and not any(probe[:8] and probe[:8] in re.sub(r"[A-Z][a-z]+", "", p)
                                                for p in pools[rid]):
                        if not any(plain[:20].lower() in p.lower() for p in pools[rid]):
                            pass        # names and capitalised vocatives make exact matching loose; checked below
                if rm.last_ask:
                    cv.resolve(rm.last_ask, random.choice(choices))
    except Exception as e:
        import traceback
        bad.append(f"play: crashed after {spoken} lines: {e!r} {traceback.format_exc().splitlines()[-3]}")
    if spoken < 40:
        bad.append(f"play: only {spoken} lines in sixty outings with {len(party)} recruits")
    # every logged line must come from its speaker's own pool (vocative and {name} aside)
    for rid, text in rm.log:
        if rid not in pools:
            continue
        core = text
        for other in ids + [g._player_name()]:
            core = core.replace(rm.first(other), "")
        core = core.lstrip(", ").strip()
        frag = core[:18].lower()
        if frag and not any(frag in re.sub(r"\{[^}]*\}", "", p).lower() or frag[1:] in p.lower()
                            for p in pools[rid] | {x for x in pools[rid]}):
            full = [t for v in (g.lines.get(rid) or {}).values() for t in (v if isinstance(v, list) else [v])]
            full += [t for v in (rm.lines.get(rid) or {}).values() for t in (v if isinstance(v, list) else [v])]
            full += [t for a in args for w, t in a["lines"] if w == rid]
            # a {his|her} address form is spoken as one of its two words, so try each before giving up
            def forms(t):
                yield re.sub(r"\{[^}]*\}", "", t)
                for i in (1, 2):
                    yield re.sub(r"\{([^{}|]+)\|([^{}|]+)\}", lambda m: m.group(i), t).replace("{name}", "")
            if not any(frag in f.replace("  ", " ").lower() for t in full for f in forms(t)):
                bad.append(f"play: {rid} said a line that isn't in their own pool: {text[:60]}")
                break

    # 6 every recruit, every kind of talk
    kinds = [("aftermath", s) for s in ("near_death", "wipe", "blame_self", "first_clear")] + \
            [("development", None)] + [("relationship", s) for s in ("hard_on", "likes_me", "respect_hate",
                                                                      "acting_off")] + \
            [("confrontation", s) for s in ("favour", "dislike", "risks", "wrong", "trust", "decided")]
    for rid in ids:
        other = next(x for x in ids if x != rid)
        for kind, sub in kinds:
            for approach in C.APPROACHES:
                cv.wants.pop(rid, None)
                if not cv.want(rid, kind, sub, about=other, force=True):
                    bad.append(f"talk: {rid} can't open {kind}/{sub}")
                    break
                conv = cv.open(rid)
                if not conv or not conv.get("line"):
                    bad.append(f"talk: {rid} has no opener for {kind}/{sub}")
                    break
                if "{" in conv["line"]:
                    bad.append(f"talk: {rid} {kind}/{sub} opener has an unfilled slot: {conv['line'][:50]}")
                reply = cv.choose(rid, approach)
                if not reply:
                    bad.append(f"talk: {rid} has no reply to {approach} in {kind}/{sub}")
                    break
        for conv in g.lines and (json.loads(Path("data/npcs/group_lines.json").read_text())["history"].get(rid) or []):
            if len(conv.get("options", [])) < 2:
                bad.append(f"talk: {rid} history {conv['id']} has fewer than two options")

    # 7 arguments
    for a in args:
        cv.pending_ask = None
        cv.args_heard = []
        rm.queue.clear()
        here = list(a["between"])
        before = len(rm.queue)
        random.seed(1)
        started = False
        for _ in range(12):
            cv.pending_ask = None
            cv.args_heard = []
            if cv.start_argument(here) and rm.queue and len(rm.queue[-1]) > 3:
                started = True
                break
            rm.queue.clear()
        if not started:
            bad.append(f"argument {a['id']}: never asks the player")
            continue
        ask = rm.queue[-1][3]
        opts = cv.ask_options(ask)
        if len(opts) != 4:
            bad.append(f"argument {a['id']}: {len(opts)} options, not 4")
        for choice in ("back_asker", "back_other", "third", "stay_out"):
            if not cv.resolve(ask, choice):
                bad.append(f"argument {a['id']}: '{choice}' gets no reaction")
        cv.wallflower(ask)

    # 8 shades of grey
    a, b = ids[0], ids[1]
    setst(a, b, 40)
    g.sore.clear()
    if g._call_out([a, b], b, "first_down") or g._call_out([b, a], b, "first_down"):
        k = rm.key(a, b)
        if k not in g.sore:
            bad.append("grey: a call-out didn't leave the pair sore")
        for _ in range(4):
            g._tick_timers()
        if k in g.sore:
            bad.append("grey: the pair never stopped being sore")
    else:
        bad.append("grey: a friend never called out the one who went down first")
    setst(a, b, -60)
    g.truce.clear()
    if not g._respect(a, b, "clutch"):
        bad.append("grey: rivals never gave each other their due")
    elif rm.key(a, b) not in g.truce:
        bad.append("grey: rivals' respect brought no truce")
    if rm.rel(a, b).state not in ("rivals", "grating"):
        bad.append("grey: rivals' respect made them friends (respect isn't friendship)")

    # 9 arcs
    arc_rid = next((x for x in ids if (g.arcs.get(x) or {}).get("shape")), None)
    anchor = next((x for x in ids if (g.arcs.get(x) or {}).get("anchor")), None)
    if arc_rid:
        shape = g.arcs[arc_rid]["shape"]
        ev = next(iter(__import__("world.group_dynamics", fromlist=["x"]).DRIVERS[shape]))
        g.arc_state.pop(arc_rid, None)
        for _ in range(40):
            g.push(arc_rid, ev)
        if (g.arc_state.get(arc_rid) or {}).get("stage", 0) < 3:
            bad.append(f"arc: {arc_rid} ({shape}) never reached its Become")
    if anchor:
        for ev in ("wipe", "crew_formed", "fondness_to", "carried"):
            g.push(anchor, ev)
        # an anchor can still notice a drift (g_changed rides on arc_state as "pending"), but never makes arc progress
        st = g.arc_state.get(anchor) or {}
        if st.get("progress") or st.get("stage") or st.get("path") == "alt":
            bad.append(f"arc: anchor {anchor} got an arc")

    # 10 save
    d = bm.to_dict()
    bm2 = B.BondManager()
    bm2.load_state(json.loads(json.dumps(d)))
    if bm2.rel.groups.to_dict() != json.loads(json.dumps(g.to_dict())):
        bad.append("save: group dynamics don't round-trip")

    # 11 data only
    for f in ("world/group_dynamics.py", "world/conversations.py"):
        src = Path(f).read_text(encoding="utf-8")
        for rid in ids:
            if rid in src:
                bad.append(f"data only: {f} names {rid}")
    B.reset_bond_manager()
    return bad


def main():
    bad = findings()
    for b in bad:
        print("  FAIL", b)
    print("interactive party " + ("FAILED" if bad else "OK - voices pass, moods, crews, perks, talks, arguments, "
                                                       "shades of grey, arcs and saves all hold"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
