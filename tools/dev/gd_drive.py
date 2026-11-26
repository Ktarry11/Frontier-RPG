import random, sys
random.seed(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
from world.bond_manager import get_bond_manager
from world.conversations import get_conversations
bm = get_bond_manager(); rm = bm.rel; g = rm.groups; cv = get_conversations()
party = ["diego_tinker", "sebastian_bloodmage", "sondre_stormbringer", "rhodri_knight"]
for r in party:
    assert r in rm.traits, r
    assert g.has(r), r
def drain(tag):
    while True:
        item = rm.pop_beat(99)
        if not item: break
        print(f"--- {tag}" + (f"  [ASK: {rm.last_ask['asker']} wants your take]" if rm.last_ask else ""))
        for rid, t in item:
            print(f"   {rm.first(rid)}: {t}")
        if rm.last_ask:
            opts = cv.ask_options(rm.last_ask)
            pick = random.choice(opts)
            print(f"   >> you: {pick[0]}")
            for rid, t in cv.resolve(rm.last_ask, pick[1]):
                print(f"   {rm.first(rid)}: {t}")
for n in range(1, 31):
    rm.zone = "Tirisfal Glades"
    rm.on_outing(party, "quest")
    cv.on_outing(party)
    drain(f"outing {n} [{g.MOOD_NAMES[g.mood(party)]}]")
    if n % 7 == 0:
        fd = random.choice(party)
        rm.on_wipe(party, first_down=fd); cv.on_wipe(party, fd); drain(f"wipe ({rm.first(fd)} first down)")
    if n % 5 == 0:
        g.on_fight_won(party, first_down=random.choice(party), standing=random.sample(party, 2),
                       saves=[], boss=(n % 10 == 0)); drain("fight won")
    if n % 4 == 0:
        rm.on_rest(party); drain("rest")
print("\n=== STATE")
for a, b in rm.pairs_in(party):
    r = rm.rel(a, b); print(f"  {rm.first(a)}+{rm.first(b)}: {r.state} {r.affinity:.0f}")
for row in g.panel(party): print("  ", row)
print("  wants:", {rm.first(k): (v['kind'], v['sub']) for k, v in cv.wants.items()})
for rid in list(cv.wants)[:2]:
    c = cv.open(rid); print(f"\n  TALK {rm.first(rid)}: {c['line']}")
    choice = c["options"][0][1]; print(f"   you: {c['options'][0][0]}"); print(f"   {rm.first(rid)}: {cv.choose(rid, choice)}")
