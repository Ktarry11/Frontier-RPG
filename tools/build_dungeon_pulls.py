"""Regroup every fixed-spawn dungeon's trash into group pulls (Kyle, 2026-10-23).

Dungeons are run by full parties (tank + healer), so trash comes in PACKS of 3-4 mobs, roughly 3-4 pulls before each
boss, rather than a long chain of solo fights. This tool reads each dungeon's hand-authored mob list (or, for dungeons
that never had one, rolls a pool from its encounter table), then:

  1. assigns every mob to the boss it leads to (path distance over walkable tiles),
  2. decides how many pulls that boss gets (CONFIG p_main / p_rare, bounded by how many mobs there are),
  3. trims surplus mobs WITHOUT breaking any quest (kill counts and fetch-drop expectations are protected),
  4. clusters the rest into balanced packs of 3-4, mixes roles inside packs (melee / skirmisher / caster / ranged),
  5. places each pack on reachable floor, spaced out, away from the portal and the bosses,
  6. writes data/dungeons/trash_packs.json (applied by world/dungeon_packs.apply_packs in create_all_zones).

    PYTHONPATH=. python3 tools/build_dungeon_pulls.py [dungeon name ...]    (no args = all)
Deterministic (fixed seeds), idempotent, safe to re-run after layout changes.
"""
import collections
import glob
import json
import math
import os
import random
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "data", "dungeons", "trash_packs.json")

# p_main = pulls before each main boss, p_rare = pulls guarding a rare's nook, rares = optional-nook bosses.
CONFIG = {
    "Wailing Caverns": dict(p_main=3, p_rare=1, rares=("Old Hissfang", "Drowsyroot the Dreamer", "Sporeback the Bloated")),
    "The Broodspiral": dict(p_main=4, p_rare=1, rares=("Mother Amberwing", "Gnash the Hollow-Maw", "Chitterlord Skrix")),
    "Razorfen Kraul": dict(p_main=4, p_rare=1, rares=("Blind Hunter", "Earthcaller Halmgar", "Thornjaw the Gorger")),
    "Grom's Rest": dict(p_main=4, p_rare=1, rares=()),
    "Shadowfang Keep": dict(p_main=4, p_rare=1, rares=()),
    "Plague Depths": dict(p_main=4, p_rare=1, rares=()),
    "Ragefire Chasm": dict(p_main=3, p_rare=1, rares=()),
    "Blackfathom Deeps": dict(p_main=4, p_rare=1, rares=()),
    # Durnholde has five bosses and a ring you can walk either way, so three pulls each keeps the total
    # sane rather than four (Kyle: "about 3-4 groups between each boss. Sometimes less").
    "Durnholde Keep": dict(p_main=3, p_rare=1, rares=()),
}

ROLE = {"humanoid_warrior": "melee", "beast_large": "melee", "elemental_bruiser": "melee", "undead_basic": "melee",
        "beast_basic": "melee", "demon_hound": "melee", "aquatic_basic": "melee",
        "beast_fast": "skirm", "vermin_sneaky": "skirm", "humanoid_rogue": "skirm", "vermin_swarm": "skirm",
        "humanoid_caster": "caster", "elemental_caster": "caster", "demon_caster": "caster",
        "elemental_bruiser_": "melee", "humanoid_ranged": "ranged"}

NEIGH = ((1, 0), (-1, 0), (0, 1), (0, -1))


# ----------------------------------------------------------------------------------------------- map helpers
def bfs(zone, src):
    """Distance + parent maps over walkable tiles from src."""
    dist = {src: 0}
    par = {src: None}
    q = collections.deque([src])
    while q:
        x, y = q.popleft()
        for dx, dy in NEIGH:
            n = (x + dx, y + dy)
            if n not in dist and 0 <= n[0] < zone.width and 0 <= n[1] < zone.height and zone.is_walkable(*n):
                dist[n] = dist[(x, y)] + 1
                par[n] = (x, y)
                q.append(n)
    return dist, par


def snap(dist, x, y, rad=6):
    """Nearest reachable tile to (x, y)."""
    best = None
    ix, iy = int(round(x)), int(round(y))
    for dy in range(-rad, rad + 1):
        for dx in range(-rad, rad + 1):
            t = (ix + dx, iy + dy)
            if t in dist:
                d = dx * dx + dy * dy
                if best is None or d < best[0]:
                    best = (d, t)
    return None if best is None else best[1]


def cheb(a, b):
    return max(abs(a[0] - b[0]), abs(a[1] - b[1]))


def eu(a, b):
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ----------------------------------------------------------------------------------------------- quest protection
def load_game_data():
    creatures = json.load(open(os.path.join(ROOT, "data/creatures/creatures.json")))["creatures"]
    drops = json.load(open(os.path.join(ROOT, "data/creatures/quest_drops.json")))["drops"]
    quests = []
    for f in glob.glob(os.path.join(ROOT, "data/quests/*.json")):
        d = json.load(open(f))
        quests += d["quests"] if isinstance(d, dict) else d
    return creatures, drops, quests


def requirements(zone_name, creatures, drops, quests):
    """[(frozenset(names), count)] kill groups and [(item_id, count)] fetches that the dungeon must be able to supply."""
    slug = zone_name.lower().replace(" ", "_").replace("'", "")
    kills, fetches = [], []
    for q in quests:
        in_zone = q.get("zone") == slug or any(o.get("zone") == slug for o in q["objectives"])
        if not in_zone:
            continue
        for o in q["objectives"]:
            if o["type"] == "kill" and (o.get("zone") == slug or q.get("zone") == slug):
                t = o["target"]
                if t in creatures and not creatures[t].get("is_boss"):
                    kills.append((frozenset([t] + list(o.get("alt_targets") or [])), int(o["count"])))
            elif o["type"] == "fetch":
                fetches.append((o["target"], int(o["count"])))
    item_src = collections.defaultdict(dict)       # item -> {creature: chance}
    for cname, lst in drops.items():
        if creatures.get(cname, {}).get("is_boss"):
            continue
        for d in lst:
            item_src[d["item_id"]][cname] = d.get("chance", 1.0)
    fetches = [(i, c) for (i, c) in fetches if i in item_src]
    return kills, fetches, item_src


class Supply:
    """Tracks whether a candidate mob list still satisfies every quest need."""

    def __init__(self, kills, fetches, item_src, initial, strict=False):
        have = collections.Counter(initial)
        # normal: never drop below what the original list already offered (capped at need + 1); strict: the full target
        self.kills = [(names, (c + 1) if strict else min(c + 1, sum(have[n] for n in names))) for names, c in kills]
        self.fetches = []
        for item, c in fetches:
            exp = sum(have[n] * ch for n, ch in item_src[item].items())
            self.fetches.append((item, c * 1.4 if strict else min(c * 1.4, exp)))
        self.item_src = item_src
        self.unsatisfiable = [(sorted(n), c) for n, c in kills if sum(have[x] for x in n) < c]
        self.unsatisfiable_f = [(i, c) for i, c in fetches if sum(have[n] * ch for n, ch in item_src[i].items()) < c]

    def ok(self, counter):
        for names, need in self.kills:
            if sum(counter[n] for n in names) < need:
                return False
        for item, need in self.fetches:
            if sum(counter[n] * ch for n, ch in self.item_src[item].items()) < need - 1e-9:
                return False
        return True

    def deficits(self, counter):
        out = []
        for names, need in self.kills:
            if sum(counter[n] for n in names) < need:
                out.append(("kill", names, need - sum(counter[n] for n in names)))
        for item, need in self.fetches:
            have = sum(counter[n] * ch for n, ch in self.item_src[item].items())
            if have < need - 1e-9:
                out.append(("fetch", item, need - have))
        return out


# ----------------------------------------------------------------------------------------------- clustering
def role_of(creatures, name):
    return ROLE.get(creatures.get(name, {}).get("template"), "melee")


def pack_score(creatures, pack):
    roles = {role_of(creatures, m[2]) for m in pack}
    names = collections.Counter(m[2] for m in pack)
    return min(len(roles), 3) * 2 - sum(max(0, c - 2) for c in names.values())


def balanced_clusters(mobs, k, rng):
    """Split mobs ([(x,y,name,lvl)]) into k spatial groups of 3-4 (sizes differ by at most 1)."""
    n = len(mobs)
    sizes = [n // k + (1 if i < n % k else 0) for i in range(k)]
    # init: contiguous chunks along the route-sorted list, then a few k-means passes
    order = sorted(range(n), key=lambda i: (mobs[i][4], mobs[i][0]))
    cents, i0 = [], 0
    for s in sizes:
        chunk = order[i0:i0 + s]
        i0 += s
        cents.append((sum(mobs[i][0] for i in chunk) / s, sum(mobs[i][1] for i in chunk) / s))
    assign = [0] * n
    for _ in range(12):
        cap = list(sizes)
        pairs = sorted(((eu(mobs[i][:2], cents[c]), i, c) for i in range(n) for c in range(k)))
        taken = set()
        for d, i, c in pairs:
            if i in taken or cap[c] == 0:
                continue
            assign[i] = c
            cap[c] -= 1
            taken.add(i)
        new = []
        for c in range(k):
            ms = [mobs[i] for i in range(n) if assign[i] == c]
            new.append((sum(m[0] for m in ms) / len(ms), sum(m[1] for m in ms) / len(ms)))
        if all(eu(a, b) < 0.3 for a, b in zip(cents, new)):
            cents = new
            break
        cents = new
    return [[mobs[i] for i in range(n) if assign[i] == c] for c in range(k)]


def mix_roles(creatures, groups, rng, max_move=22.0, iters=400):
    """Swap members between neighbouring packs when it makes both packs more mixed (melee / skirmisher / caster / ranged)."""
    cents = [(sum(m[0] for m in g) / len(g), sum(m[1] for m in g) / len(g)) for g in groups]
    for _ in range(iters):
        if len(groups) < 2:
            break
        a, b = rng.sample(range(len(groups)), 2)
        ia, ib = rng.randrange(len(groups[a])), rng.randrange(len(groups[b]))
        ma, mb = groups[a][ia], groups[b][ib]
        if ma[2] == mb[2] or eu(ma[:2], cents[b]) > max_move or eu(mb[:2], cents[a]) > max_move:
            continue
        before = pack_score(creatures, groups[a]) + pack_score(creatures, groups[b])
        groups[a][ia], groups[b][ib] = mb, ma
        after = pack_score(creatures, groups[a]) + pack_score(creatures, groups[b])
        if after <= before:
            groups[a][ia], groups[b][ib] = ma, mb
    return groups


# ----------------------------------------------------------------------------------------------- placement
def place_pack(dist, members, anchor_xy, taken, rng):
    """Put `members` ([(x,y,name,lvl,d)]) on reachable floor around anchor_xy, >=2 apart, clear of `taken` tiles."""
    ax, ay = anchor_xy
    cands = []
    for dy in range(-4, 5):
        for dx in range(-4, 5):
            t = (ax + dx, ay + dy)
            if t in dist and all(cheb(t, o) >= 3 for o in taken):
                cands.append((dx * dx + dy * dy, t))
    cands.sort()
    chosen = []
    for _, t in cands:
        if all(cheb(t, c) >= 2 for c in chosen):
            chosen.append(t)
            if len(chosen) == len(members):
                break
    if len(chosen) < len(members):
        return None
    # lead (index 0) is the member nearest the anchor; the rest spread
    rng.shuffle(members)
    return [(t[0], t[1], m[2], m[3]) for t, m in zip(chosen, members)]


def free_anchor(dist, want, anchors, start, bosses, min_gap, start_gap, boss_gap, taken_tiles):
    """Reachable tile closest to `want` that is clear of other packs, the portal and the bosses."""
    wx, wy = want
    best = None
    for dy in range(-14, 15):
        for dx in range(-14, 15):
            t = (int(wx) + dx, int(wy) + dy)
            if t not in dist:
                continue
            if eu(t, start) < start_gap or any(eu(t, b) < boss_gap for b in bosses):
                continue
            if any(eu(t, a) < min_gap for a in anchors):
                continue
            # needs room for a pack: at least 8 reachable tiles within 2
            room = sum(1 for ex in range(-2, 3) for ey in range(-2, 3) if (t[0] + ex, t[1] + ey) in dist)
            if room < 9:
                continue
            d = dx * dx + dy * dy
            if best is None or d < best[0]:
                best = (d, t)
    return None if best is None else best[1]


# ----------------------------------------------------------------------------------------------- generated pools
def route_pool(zone, creatures, cm, dist_s, par_s, start, bosses, cfg, rng):
    """For dungeons with no authored trash: a pool of mobs from the cave's encounter table placed along the route to each boss."""
    table = cm.get_encounter_table(zone.region, "cave", zone.name)
    names = [n for n, w in table.items() if w > 0 and n in creatures and not creatures[n].get("is_boss")]
    weights = [table[n] for n in names]
    if not names:
        raise SystemExit(f"{zone.name}: no trash table")
    used = {start}
    mobs = []
    order = sorted(bosses, key=lambda b: dist_s.get((b[0], b[1]), 10 ** 9))
    for bx, by, bname in order:
        k = cfg["p_rare"] if bname in cfg["rares"] else cfg["p_main"]
        node, path = (bx, by), []
        while node is not None and node not in used:
            path.append(node)
            node = par_s[node]
        path.reverse()                                   # junction -> boss
        usable = path[4:max(5, len(path) - 12)] or path[:max(1, len(path) - 8)]
        for i in range(k):
            t = usable[int((i + 0.5) / k * len(usable))] if usable else path[len(path) // 2]
            size = 4 if (i + 1) % 2 == 0 or k == 1 else 3
            for _ in range(size):
                nm = rng.choices(names, weights=weights, k=1)[0]
                mobs.append((t[0] + rng.randint(-2, 2), t[1] + rng.randint(-2, 2), nm, None, dist_s.get(t, 0)))
        used.update(path)
    return mobs


creatures_ref = {}


def fix_supply(groups_flat, sup, table_names, rng):
    """Swap surplus mobs for deficit ones until every quest need is met (generated pools only)."""
    for _ in range(400):
        cnt = collections.Counter(m[2] for m in groups_flat)
        defs = sup.deficits(cnt)
        if not defs:
            return True
        kind, key, _need = defs[0]
        want = None
        if kind == "kill":
            want = sorted(key)[0]
        else:
            srcs = sorted(sup.item_src[key], key=lambda n: -sup.item_src[key][n])
            want = srcs[0] if srcs else None
        if want is None:
            return False
        protected = set()
        for names, _n in sup.kills:
            protected |= set(names)
        # replace a member whose name is the most common unprotected-or-surplus one
        pick = sorted(range(len(groups_flat)), key=lambda i: (-cnt[groups_flat[i][2]], rng.random()))
        for i in pick:
            m = groups_flat[i]
            if m[2] == want:
                continue
            trial = list(groups_flat)
            lo, hi = creatures_ref[want]["level_range"]
            lvl = m[3] if m[3] is None else min(max(m[3], lo), hi)
            trial[i] = (m[0], m[1], want, lvl, m[4])
            tc = collections.Counter(x[2] for x in trial)
            if len(sup.deficits(tc)) <= len(defs) and sum(v for *_a, v in sup.deficits(tc)) < sum(v for *_a, v in defs):
                groups_flat[i] = trial[i]
                break
        else:
            return False
    return False


# ----------------------------------------------------------------------------------------------- main per dungeon
def build_dungeon(zone, cfg, cm, creatures, drops, quests):
    rng = random.Random(zone.name)
    portal = [(x, y) for y in range(zone.height) for x in range(zone.width) if zone.interaction_layer[y][x] == "portal"]
    start = (portal[0][0], portal[0][1] - 2)
    dist_s, par_s = bfs(zone, start)
    bosses = [(b[0], b[1], b[2]) for b in zone.boss_positions]
    bpos = [(b[0], b[1]) for b in bosses]
    boss_dist = {b: bfs(zone, (b[0], b[1]))[0] for b in bosses}

    kills, fetches, item_src = requirements(zone.name, creatures, drops, quests)
    authored = getattr(zone, "authored_trash_spawns", None)
    if authored is None:
        authored = list(getattr(zone, "trash_spawns", None) or [])
    generated = not authored
    if generated:
        pool = route_pool(zone, creatures, cm, dist_s, par_s, start, bosses, cfg, rng)
    else:
        pool = []
        for (x, y, n, *rest) in authored:
            t = snap(dist_s, x, y)
            if t is None:
                continue
            pool.append((t[0], t[1], n, rest[0] if rest else None, dist_s[t]))

    # ---- 1. segment by boss (path distance)
    seg = collections.defaultdict(list)
    for m in pool:
        t = (m[0], m[1])
        best = min(bosses, key=lambda b: boss_dist[b].get(t, 10 ** 9))
        seg[best].append(m)

    # fetch quests whose drop chance cannot reach 1.6x the need from this dungeon's supply get their chance scaled up
    have0 = collections.Counter(m[2] for m in pool)
    for item, need in fetches:
        srcs = item_src[item]
        exp = sum(have0[n] * ch for n, ch in srcs.items())
        if 0 < exp < need * 1.45:
            f = (need * 1.6) / exp
            for cname in srcs:
                for d in drops[cname]:
                    if d["item_id"] == item:
                        old = d["chance"]
                        d["chance"] = round(min(1.0, old * f), 2)
                        TUNED.append((zone.name, cname, item, old, d["chance"]))
    kills, fetches, item_src = requirements(zone.name, creatures, drops, quests)
    sup = Supply(kills, fetches, item_src, [m[2] for m in pool])
    strict = Supply(kills, fetches, item_src, [m[2] for m in pool], strict=True)
    counter = collections.Counter(m[2] for m in pool)

    # ---- 2/3. pulls per boss and trimming
    k_cfg = {b: (cfg["p_rare"] if b[2] in cfg["rares"] else cfg["p_main"]) for b in bosses}
    mobs_of = {b: list(seg.get(b, [])) for b in bosses}
    for ms in mobs_of.values():
        rng.shuffle(ms)
    # a segment with fewer mobs than one pack (rares: fewer than 2) hands its mobs to the nearest segment that can use them
    for b in bosses:
        need_min = 2 if b[2] in cfg["rares"] else 3
        if 0 < len(mobs_of[b]) < need_min:
            for m in mobs_of[b]:
                t = (m[0], m[1])
                others = [o for o in bosses if o != b and len(mobs_of[o]) >= 3]
                if others:
                    mobs_of[min(others, key=lambda o: boss_dist[o].get(t, 10 ** 9))].append(m)
            mobs_of[b] = []

    cap = {b: 4 * k_cfg[b] for b in bosses}
    # phase A: drop surplus mobs wherever a quest does not need them
    for b in bosses:
        mobs = mobs_of[b]
        while len(mobs) > cap[b]:
            for i in sorted(range(len(mobs)), key=lambda i: (-counter[mobs[i][2]], rng.random())):
                counter[mobs[i][2]] -= 1
                if sup.ok(counter):
                    mobs.pop(i)
                    break
                counter[mobs[i][2]] += 1
            else:
                break
    # phase B: what is left over (all quest-needed) moves to the nearest boss that still has room: same creature, placed
    # at one of that segment's own mobs (so the room stays coherent) and levelled like it
    for b in bosses:
        mobs = mobs_of[b]
        while len(mobs) > cap[b]:
            rec = [o for o in bosses if o != b and mobs_of[o] and len(mobs_of[o]) < cap[o]]
            if not rec:
                break
            o = min(rec, key=lambda o: eu(o[:2], b[:2]))
            m = mobs.pop(rng.randrange(len(mobs)))
            home = rng.choice(mobs_of[o])
            mobs_of[o].append((home[0], home[1], m[2], home[3], home[4]))
    # phase C: still over capacity -> extra pulls for that boss
    plan = {}
    for b in bosses:
        mobs = mobs_of[b]
        if not mobs:
            plan[b] = (0, mobs)
            continue
        k = max(-(-len(mobs) // 4), min(k_cfg[b], len(mobs) // 3), 1)
        plan[b] = (k, mobs)

    # ---- 4. cluster + role mix
    all_groups = []
    for b, (k, mobs) in plan.items():
        if k == 0 or not mobs:
            continue
        k = max(-(-len(mobs) // 4), min(k, len(mobs) // 3), 1)
        k = min(k, len(mobs))
        groups = balanced_clusters(mobs, k, rng)
        mix_roles(creatures, groups, rng)
        for g in groups:
            all_groups.append((b, g))

    # ---- 5. placement
    all_groups.sort(key=lambda bg: sum(m[4] for m in bg[1]) / len(bg[1]))
    anchors, taken, packs, dropped_packs = [], [], [], 0
    for b, g in all_groups:
        want = (sum(m[0] for m in g) / len(g), sum(m[1] for m in g) / len(g))
        placed = None
        for gap, sgap, bgap in ((11, 10, 9), (9, 9, 8), (7, 8, 7)):
            a = free_anchor(dist_s, want, anchors, start, bpos, gap, sgap, bgap, taken)
            if a is None:
                continue
            placed = place_pack(dist_s, [list(m) for m in g], a, taken, rng)
            if placed:
                anchors.append(a)
                break
        if placed is None:
            dropped_packs += 1
            continue
        taken.extend((m[0], m[1]) for m in placed)
        packs.append((sum(dist_s[(m[0], m[1])] for m in placed) / len(placed), placed, b))

    packs.sort(key=lambda p: p[0])
    result = [p[1] for p in packs]
    # ---- 6. top up any quest need the list still cannot meet by swapping members' creature types (same tiles)
    flat = [(m[0], m[1], m[2], m[3], 0) for p in result for m in p]
    if strict.deficits(collections.Counter(m[2] for m in flat)):
        fix_supply(flat, strict, None, rng)
        it = iter(flat)
        result = [[(m[0], m[1], *(lambda f: (f[2], f[3]))(next(it))) for m in p] for p in result]

    flat_names = collections.Counter(m[2] for p in result for m in p)
    report = dict(
        zone=zone.name, authored=len(authored), packs=len(result), mobs=sum(len(p) for p in result),
        sizes=dict(collections.Counter(len(p) for p in result)), dropped_packs=dropped_packs,
        pulls_per_boss={b[2]: sum(1 for p in packs if p[2] == b) for b in bosses},
        mixed=sum(1 for p in result if len({role_of(creatures, m[2]) for m in p}) >= 2),
        unsatisfiable=sup.unsatisfiable + sup.unsatisfiable_f,
        deficits=strict.deficits(flat_names),
    )
    return result, report, (start, bpos)


TUNED = []


def main(argv):
    from world.zone_generator import create_all_zones
    from world.creature_manager import CreatureManager
    zones = create_all_zones()
    cm = CreatureManager()
    creatures, drops, quests = load_game_data()
    creatures_ref.update(creatures)
    try:
        out = json.load(open(OUT))
    except (OSError, json.JSONDecodeError):
        out = {}
    names = argv or list(CONFIG)
    for name in names:
        zone = zones[name]
        packs, rep, _ = build_dungeon(zone, CONFIG[name], cm, creatures, drops, quests)
        out[name] = [[list(m) for m in p] for p in packs]
        print(f"== {name}: {rep['authored']} authored mobs -> {rep['packs']} packs / {rep['mobs']} mobs, sizes {rep['sizes']}, "
              f"mixed-role packs {rep['mixed']}/{rep['packs']}, unplaced packs {rep['dropped_packs']}")
        print("   pulls per boss:", rep["pulls_per_boss"])
        if rep["unsatisfiable"]:
            print("   (quest needs the ORIGINAL list could not meet:", rep["unsatisfiable"], ")")
        if rep["deficits"]:
            print("   QUEST DEFICITS AFTER REGROUP:", rep["deficits"])
    with open(OUT, "w") as f:
        json.dump(out, f, separators=(",", ":"))
    print("wrote", OUT)
    if TUNED:
        qd = os.path.join(ROOT, "data/creatures/quest_drops.json")
        full = json.load(open(qd))
        for (_z, cname, item, _old, new) in TUNED:
            for d in full["drops"][cname]:
                if d["item_id"] == item:
                    d["chance"] = new
        with open(qd, "w") as f:
            json.dump(full, f, indent=2, ensure_ascii=False)
            f.write("\n")
        for t in TUNED:
            print("   drop chance tuned:", t)


if __name__ == "__main__":
    main(sys.argv[1:])
