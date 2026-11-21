#!/usr/bin/env python3
"""Wave 3: the recruits get on, or don't, the way their profiles say they would.

    PYTHONPATH=. python3 tools/qa_relationships.py            # checks
    PYTHONPATH=. python3 tools/qa_relationships.py --sample   # also print beats from the real lines

Engine: world/relationship_manager.py. Text: tools/build_relationships.py from tools/wave3/.

  1. the text builds and passes its checker
  2. chemistry: pairs the profiles say would get on start warm, pairs they say would clash start
     cold, and neighbours start on nodding terms (Kyle: yes)
  3. the states hold on past the line that got them there, so they don't flicker
  4. a long campaign of random parties, wipes, close calls and gear passed around: every beat has
     two to four lines, every {name} is filled with the right person, a name only turns up between
     friends (Kyle: yes), and the whole range of states turns up, rivals included
     and the words for "you" that change with the listener (hermano, hermana) follow their gender
  5. rivals still travel together (Kyle: no refusals), and mood is the only thing that moves
  6. it all survives a save and load
"""
import contextlib
import io
import json
import os
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)


class M:
    def __init__(self, rid, name):
        self.recruit_id, self.name, self.level = rid, name, 30
        self.health = self.current_health = 100


class P:
    def __init__(self, members):
        self.members = list(members)

    def remove_member(self, m):
        if m in self.members:
            self.members.remove(m)


def main(argv):
    bad = []

    def check(ok, msg):
        if not ok:
            bad.append(msg)

    import subprocess
    r = subprocess.run([sys.executable, "tools/build_relationships.py"], capture_output=True, text=True)
    check(r.returncode == 0, "build_relationships failed:\n" + r.stdout[-3000:])

    from world import bond_manager as BM
    from world import relationship_manager as RM
    BM.reset_bond_manager()
    bm = BM.get_bond_manager()
    rm = bm.rel
    names = {rid: bm.name_of(rid) for rid in rm.traits}
    # every recruit with a Wave 3 file (98 at first; Dawnhaven's three bears joined 21 Nov 2026) has traits
    wave3 = len([p for p in (ROOT / "tools/wave3").glob("*.json") if not p.stem.startswith("_")])
    check(len(rm.traits) == wave3, f"{len(rm.traits)} recruits have traits, expected {wave3} (one per Wave 3 file)")

    # 2. chemistry
    for a, b in (("dan_warrior", "ivan_warrior"), ("astrid_starcaller", "minh_chronomancer"),
                 ("bakyt_hunter", "giorgi_primalist"), ("ama_priest", "freja_priest"),
                 ("marta_tinker", "diego_tinker"), ("liam_suncleric", "ziad_felsworn")):
        check(rm.chem(a, b) >= 6, f"{a} and {b} should start warm, chemistry {rm.chem(a, b):.1f}")
    for a, b in (("emiliano_pyromancer", "alonso_pyromancer"), ("haruto_runemaster", "saoirse_starcaller"),
                 ("camille_ranger", "lucia_suncleric"), ("osvaldo_warlock", "iker_guardian")):
        check(rm.chem(a, b) < 0, f"{a} and {b} should start cold, chemistry {rm.chem(a, b):.1f}")
    check(rm.state("wes_warrior", "neil_felsworn") == "nodding", "neighbours at Ariden's Watch aren't nodding")
    check(rm.state("wes_warrior", "dan_warrior") == "strangers", "two strangers start as strangers")

    # 3. states with slack
    ns = RM.next_state
    check(ns("nodding", 19) == "nodding" and ns("nodding", 20) == "friendly", "friendly at 20")
    check(ns("friendly", 16) == "friendly" and ns("friendly", 14) == "nodding", "friendly holds to 15")
    check(ns("close", 50) == "close" and ns("close", 47) == "friendly", "close holds to 48")
    check(ns("grating", -15) == "grating" and ns("grating", -13) == "nodding", "grating holds to -14")
    check(ns("rivals", -45) == "rivals" and ns("rivals", -41) == "grating", "rivals hold to -42")

    # 4. a long campaign. Anyone whose lines aren't written yet gets stand-ins, so every path runs.
    real = {rid: dict(v) for rid, v in rm.lines.items()}
    for rid, t in rm.traits.items():
        pool = rm.lines.setdefault(rid, {})
        for k in list(RM.KEYS) + [f"common_{x}" for x in t.get("tags", [])]:
            if not pool.get(k):
                pool[k] = f"STAND-IN {k}, {{name}}." if k in RM.NAMED else f"STAND-IN {k}."
    random.seed(7)
    ids = sorted(rm.traits)
    seen_states = {}
    beats = 0
    named_wrong = []
    for stint in range(160):
        crew = random.sample(ids, 4)
        party = P([M(rid, names[rid]) for rid in crew])
        bm.party = party
        for rid in crew:
            bm.bonds[rid].away = False
            bm.on_joined(rid)
        for outing in range(random.randint(6, 14)):
            if random.random() < 0.12:
                bm.on_wipe(party)
            if random.random() < 0.25:
                hurt = random.choice(party.members)
                hurt.current_health = 10
                bm.on_close_call(party, [hurt])
                hurt.current_health = 100
            if random.random() < 0.08 and len(party.members) >= 2:
                g, t = random.sample(party.members, 2)
                bm._last_taken = (g.recruit_id, "head", bm.deeds)
                bm.rel.on_gear_moved(g.recruit_id, t.recruit_id, True)
            bm.on_deed(random.choice(["quest", "dungeon"]), party)
            while True:
                lines = rm.pop_beat(99)
                if not lines:
                    break
                beats += 1
                check(1 <= len(lines) <= 6, f"a beat with {len(lines)} lines")
                for rid, text in lines:
                    check("{" not in text, f"unfilled brace: {text!r}")
                    for other in ids:
                        first = names[other].split()[0]
                        if other != rid and "STAND-IN" in text and re.search(rf", {re.escape(first)}\.$", text) \
                                and rm.state(rid, other) not in ("friendly", "close"):
                            named_wrong.append((rid, other, rm.state(rid, other), text))
            for m in list(party.members):
                b = bm.bonds[m.recruit_id]
                b.in_party = True
        for rid in crew:
            b = bm.bonds[rid]
            if b.in_party:
                bm.depart(b, "stint", quiet=True)
            b.away = False
            b.break_left = 0
    for r in rm.rels.values():
        seen_states[r.state] = seen_states.get(r.state, 0) + 1
    print(f"campaign: {beats} beats, {len(rm.rels)} pairs met, states {seen_states}")
    check(beats > 300, f"only {beats} beats in a long campaign")
    for s in ("friendly", "close", "grating"):
        check(seen_states.get(s, 0) > 0, f"nobody ended up {s}")
    check(not named_wrong, f"{len(named_wrong)} names used outside a friendship, e.g. {named_wrong[:2]}")

    # 4b. a steady crew: a pair who click become close, a pair who clash end up rivals
    for a, b, want, n in (("bakyt_hunter", "giorgi_primalist", ("close",), 30),
                          ("emiliano_pyromancer", "haruto_runemaster", ("rivals",), 40),
                          ("dan_warrior", "camille_ranger", ("friendly", "close", "nodding"), 60),
                          # "grates with careless people at first, and then likes them if they try"
                          ("adrian_templar", "callum_venomancer", ("grating", "nodding"), 80)):
        rm.rels.pop(rm.key(a, b), None)
        for _ in range(n):
            rm.on_outing([a, b], "quest")
        st = rm.state(a, b)
        print(f"steady crew: {a} and {b} after {n} outings: {st} ({rm.rel(a, b).affinity:.0f})")
        check(st in want, f"{a} and {b} after {n} outings are {st}, expected {want}")
    rm.queue.clear()

    # 4c. hermano to a man, hermana to a woman
    check(rm.address("Hola, {hermano|hermana}.", "amber_druid") == "Hola, hermana.", "a woman was called hermano")
    check(rm.address("Hola, {hermano|hermana}.", "dan_warrior") == "Hola, hermano.", "a man was called hermana")

    # 5. rivals are forced together and nothing refuses
    a, b = "emiliano_pyromancer", "alonso_pyromancer"
    r = rm.rel(a, b)
    r.affinity, r.state = -80, "rivals"
    party = P([M(a, names[a]), M(b, names[b])])
    bm.party = party
    for rid in (a, b):
        bm.bonds[rid].away = False
        bm.on_joined(rid)
    before = bm.bonds[a].mood
    bm.rel.queue.clear()
    bm.on_deed("quest", party)
    check(len(party.members) == 2, "rivals refused to share a party")
    check(bm.bonds[a].mood < before + 3, "rivals along should wear the mood down")

    # 6. save and load
    saved = json.loads(json.dumps(bm.to_dict()))
    BM.reset_bond_manager()
    bm2 = BM.get_bond_manager()
    bm2.load_state(saved)
    k = rm.key(a, b)
    check(k in bm2.rel.rels and bm2.rel.rels[k].state == "rivals", "relationships lost in a save")
    check(len(bm2.rel.rels) == len(rm.rels), "pairs lost in a save")

    if "--sample" in argv:
        sample(real)
    for x in argv:
        if x.startswith("--pair="):
            pair_sample(real, *x.split("=", 1)[1].split(","))

    for x in bad:
        print("FAIL:", x)
    print("qa_relationships:", "OK" if not bad else f"{len(bad)} problems")
    return 1 if bad else 0


def sample(real):
    """Beats from the real lines only, between recruits who have them, to read through."""
    from world import bond_manager as BM
    BM.reset_bond_manager()
    bm = BM.get_bond_manager()
    rm = bm.rel
    rm.lines = real
    done = sorted(rid for rid, v in real.items() if len(v) >= 40)
    if len(done) < 2:
        print("sample: not enough finished recruits yet")
        return
    random.seed(int(os.environ.get("SEED", "3")))
    for stint in range(40):
        crew = random.sample(done, min(4, len(done)))
        party = P([M(rid, bm.name_of(rid)) for rid in crew])
        bm.party = party
        for rid in crew:
            bm.bonds[rid].away = False
            bm.on_joined(rid)
        for outing in range(10):
            if random.random() < 0.1:
                bm.on_wipe(party)
            if random.random() < 0.2:
                bm.on_close_call(party, [random.choice(party.members)])
            bm.on_deed("dungeon", party)
            while (lines := rm.pop_beat(99)):
                print("---", " / ".join(f"{bm.name_of(a)}+{bm.name_of(b)}:{rm.state(a, b)}"
                                       for a, b in rm.pairs_in({x for x, _ in lines})))
                for rid, text in lines:
                    print(f"  {bm.name_of(rid).split()[0]}: {text}")
        for rid in crew:
            b = bm.bonds[rid]
            if b.in_party:
                bm.depart(b, "stint", quiet=True)
            b.away, b.break_left = False, 0


def pair_sample(real, a, b, outings=90):
    """Every beat between two recruits over a long shared stint, to read their signature arc in order."""
    from world import bond_manager as BM
    BM.reset_bond_manager()
    bm = BM.get_bond_manager()
    rm = bm.rel
    rm.lines = real
    random.seed(int(os.environ.get("SEED", "3")))
    party = P([M(rid, bm.name_of(rid)) for rid in (a, b)])
    bm.party = party
    for rid in (a, b):
        bm.bonds[rid].away = False
        bm.on_joined(rid)
    for n in range(outings):
        bm.on_deed("dungeon", party)
        if n % 7 == 6:
            rm.on_rest({a, b})
        while (lines := rm.pop_beat(99)):
            r = rm.rel(a, b)
            print(f"--- outing {r.outings} {r.state} {r.affinity:.0f} sig {r.sig_step}")
            for rid, text in lines:
                print(f"  {bm.name_of(rid).split()[0]}: {text}")


if __name__ == "__main__":
    with contextlib.redirect_stderr(io.StringIO()):
        pass
    sys.exit(main(sys.argv[1:]))
