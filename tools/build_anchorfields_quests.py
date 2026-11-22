#!/usr/bin/env python3
"""
The Anchorfields' quests (51-54), and the Keel's: the engine country, three anchors a thousand years old and the third
slipping. Idempotent.

    PYTHONPATH=. python3 tools/build_anchorfields_quests.py

The text and the people are in tools/anchorfields_quests.py; the brief is docs/worldtree_brief.md. Writes
data/quests/anchorfields.json, the quest drops (data/creatures/quest_drops.json) and the reputation lists
(data/factions/factions.json). Every rule the Sunward Crown's builder holds is held here: every explore point is a
tile you can walk to from the aqueduct arm, every giver and turn-in exists, kill targets live in the zone's or the
cave's encounter table, at most four quests a giver, cave quests given in a hub, and about 70% of them given in the
hubs (Keelstone, the Observatory and Tiltside). The Aetherians pay the Aetherians; the Earthborn pay nobody.
"""
import collections
import contextlib
import io
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from tools import anchorfields_quests as SQ               # noqa: E402
from tools.build_tempest_quests import voice_problems  # noqa: E402

OUT = ROOT / "data/quests/anchorfields.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
FACTIONS = ROOT / "data/factions/factions.json"
RATE = 0.75
MAX_PER_GIVER = 4      # Kyle's standing rule
HUB_SHARE = 0.7        # Kyle's ~70%: Keelstone, the Observatory and Tiltside give most of them

#: who pays for a quest: the Aetherians pay the Aetherians; the Earthborn pay nobody (transplants are factionless)
FACTION_BY_GIVER = {g: "aetherians" for g in SQ.SKY_GIVERS}
DEFAULT_FACTION = None
FACTION_BY_STARTER = {}
ID_PREFIX = "afq_"
ITEM_PREFIX = "afg_"

#: quest zone key -> (map module, start attribute, encounter path)
MAPS = {
    SQ.AF: ("tools.handbuilt_worldtree_anchorfields", "START", ("The Anchorfields",)),
    "keelstone": ("tools.handbuilt_worldtree_keelstone", "START", None),     # a town: reachability only
    SQ.KL: (None, None, ("The Anchorfields", "The Keel")),
}
CAVES = {SQ.KL}

XP = lambda lvl: 80 * lvl - 360        # noqa: E731  (the scale every pass uses: 4040 at 55, 4440 at 60)
GOLD = lambda lvl: 300 * lvl - 600     # noqa: E731

# ------------------------------------------------------------------------------------------------- rewards
NOUNS = {
    ("cloth", "head"): ["Hood", "Cowl", "Circlet"], ("cloth", "chest"): ["Robe", "Vestments", "Tunic"],
    ("cloth", "shoulder"): ["Mantle", "Amice"], ("cloth", "hands"): ["Gloves", "Handwraps"],
    ("cloth", "legs"): ["Leggings", "Trousers"], ("cloth", "feet"): ["Slippers", "Sandals"],
    ("cloth", "wrist"): ["Cuffs", "Wristwraps"], ("cloth", "waist"): ["Sash", "Cord"],
    ("leather", "head"): ["Cap", "Hood"], ("leather", "chest"): ["Jerkin", "Tunic", "Vest"],
    ("leather", "shoulder"): ["Shoulderpads", "Mantle"], ("leather", "hands"): ["Grips", "Gloves"],
    ("leather", "legs"): ["Breeches", "Leggings"], ("leather", "feet"): ["Boots", "Moccasins"],
    ("leather", "wrist"): ["Bracers", "Armwraps"], ("leather", "waist"): ["Belt", "Strap"],
    ("mail", "head"): ["Coif", "Headguard"], ("mail", "chest"): ["Hauberk", "Chainshirt"],
    ("mail", "shoulder"): ["Spaulders", "Shoulderguards"], ("mail", "hands"): ["Gauntlets", "Mitts"],
    ("mail", "legs"): ["Legguards", "Kilt"], ("mail", "feet"): ["Greaves", "Treads"],
    ("mail", "wrist"): ["Wristguards", "Bindings"], ("mail", "waist"): ["Girdle", "Links"],
    ("plate", "head"): ["Helm", "Greathelm"], ("plate", "chest"): ["Breastplate", "Chestguard"],
    ("plate", "shoulder"): ["Pauldrons", "Shoulderplates"], ("plate", "hands"): ["Handguards", "Gauntlets"],
    ("plate", "legs"): ["Legplates", "Greaves"], ("plate", "feet"): ["Sabatons", "Stompers"],
    ("plate", "wrist"): ["Vambraces", "Bracers"], ("plate", "waist"): ["Waistguard", "Girdle"],
    (None, "back"): ["Cloak", "Cape", "Shawl"], (None, "neck"): ["Pendant", "Choker", "Talisman"],
    (None, "ring"): ["Band", "Ring", "Loop"], (None, "trinket"): ["Charm", "Token", "Idol"],
}
WEAPON_NOUNS = {"staff": ["Staff", "Walking Staff"], "mace_1h": ["Mace", "Cudgel"], "mace_2h": ["Maul", "Warhammer"],
                "axe_1h": ["Hatchet", "Axe"], "axe_2h": ["Greataxe", "Felling Axe"], "sword_1h": ["Blade", "Shortsword"],
                "sword_2h": ["Greatsword", "Claymore"], "dagger": ["Knife", "Dirk"], "polearm": ["Spear", "Glaive"],
                "bow": ["Longbow", "Bow"], "gun": ["Rifle", "Musket"], "crossbow": ["Crossbow", "Arbalest"],
                "shield": ["Shield", "Buckler"], "tome": ["Tome", "Field Journal"], "wand": ["Wand", "Rod"]}
WEAPON_SLOT = {"shield": "off_hand", "tome": "off_hand", "bow": "ranged", "gun": "ranged", "crossbow": "ranged",
               "wand": "ranged"}
#: a spec's stat template -> the item templates it takes (tools/qa_stonetalon.TAKES)
TAKES = {
    "str_physical": {"str_physical"}, "agi_physical": {"agi_physical"}, "int_caster": {"int_caster"},
    "spi_healer": {"spi_healer"}, "agi_int_hybrid": {"agi_int_hybrid", "agi_physical"},
    "str_int_hybrid": {"str_int_hybrid", "str_physical", "int_caster"},
}


def author_rewards(q, used):
    import build_crafted_gear as C
    is_boss = any(o["type"] == "kill_boss" for o in q["objectives"])
    hi = q["level_max"]
    ilvl = hi + 2 if (is_boss or q.get("elite")) else hi + 1
    rarity = "rare" if (is_boss or q.get("elite")) else "uncommon"
    out, bad = [], []
    for (slot, kind, typ, ident) in q["_rewards"]:
        if kind == "weapon":
            slot = WEAPON_SLOT.get(typ, "main_hand")
            nouns = WEAPON_NOUNS[typ]
        else:
            nouns = NOUNS[(typ, slot)]
        name = next((f"{q['_prefix']} {n}" for n in nouns if f"{q['_prefix']} {n}" not in used), None)
        if name is None:
            bad.append(f"{q['quest_id']}: no free name for a {typ} {slot}")
            continue
        used.add(name)
        o = {"kind": kind, "slot": slot, "item_level": ilvl, "rarity": rarity, "stat_template": C.IDENTITIES[ident][1]}
        if kind == "weapon":
            o["weapon_type"] = typ
            ident = C.weapon_identity(typ, ident)
        else:
            o["armor_type"] = typ
        rid = ITEM_PREFIX + re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
        d = C.author(rid, {"name": name, "output": o}, ident, "")
        # onto the curve, the way rare and boss loot is (tools/audit_item_curve.py): the crafted identities left
        # about one reward in eight too weak (two-handers) or too strong (heads, shoulders, shields)
        from entities.item_budget import budget_ratio, fit_to_curve
        r = budget_ratio(d)
        if r is not None and not 0.65 <= r <= 1.45:
            fit_to_curve(d)
        bad += C.audit_item("quest", rid, d)
        d.pop("flavor_text", None)
        d["required_level"] = q["level_min"]
        out.append(d)
    return out, ilvl, rarity, bad


# ------------------------------------------------------------------------------------------------- the maps
def _zones():
    import importlib
    from tools import ashenvale_engine as E
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    out = {}
    for key, (mod, start, path) in MAPS.items():
        if path is None:                     # a town: reachability from its gate, nothing spawns
            import collections as _c
            with contextlib.redirect_stdout(io.StringIO()):
                m = importlib.import_module(mod)
                L = m.build_layout()
            st = getattr(m, start)
            seen, q = {st}, _c.deque([st])
            while q:
                x, y = q.popleft()
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    n = (x + dx, y + dy)
                    if 0 <= n[0] < m.W and 0 <= n[1] < m.H and n not in seen and L.z.is_walkable(*n):
                        seen.add(n)
                        q.append(n)
            out[key] = (seen, set())
            continue
        if len(path) == 2:
            t = enc[path[0]]["caves"][path[1]]
            out[key] = (None, set(t["creatures"]))
            continue
        with contextlib.redirect_stdout(io.StringIO()):
            m = importlib.import_module(mod)
            L = m.build_layout()
        _n, _w, seen = E.reachable_report(L, getattr(m, start))
        t = enc[path[0]]
        spawns = set(t["open_zone"]["creatures"])
        for s in t["subzones"].values():
            spawns |= set(s["creatures"])
        out[key] = (seen, spawns)
    return out


def audit(quests, drop_rows):
    bad = []
    ids = {q["quest_id"] for q in quests}
    Z = _zones()
    npcs = {r["npc_id"]: r for r in json.loads((ROOT / "data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))["npcs"]}
    item_source = {iid: cre for (cre, iid) in drop_rows}
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))["materials"]
    givers = collections.Counter(q["giver_npc_id"] for q in quests if not q["giver_npc_id"].startswith("item:"))
    for g, n in givers.items():
        if n > MAX_PER_GIVER:
            bad.append(f"{g} gives {n} quests")
        if g not in npcs:
            bad.append(f"giver {g} doesn't exist")
    hub = sum(1 for q in quests if q["giver_npc_id"] in SQ.HUB_GIVERS)
    if hub < HUB_SHARE * len(quests):
        bad.append(f"only {hub} of {len(quests)} quests are given in a hub")
    for q in quests:
        qid = q["quest_id"]
        text = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text", "turn_in_text"))
        if not text.isascii():
            bad.append(f"{qid}: non-ASCII text")
        for key in ("accept_text", "turn_in_text", "description"):
            for p in voice_problems(q[key]):
                bad.append(f"{qid} {key}: {p}")
        if "'" not in q["accept_text"]:
            bad.append(f"{qid}: no contraction in the accept line")
        if q.get("turn_in_npc_id") and q["turn_in_npc_id"] not in npcs:
            bad.append(f"{qid}: turns in to {q['turn_in_npc_id']}, who doesn't exist")
        if q["giver_npc_id"].startswith("item:") and q["giver_npc_id"][5:] not in SQ.STARTER_IDS:
            bad.append(f"{qid}: started by an item nothing drops")
        granted = {g["item_id"] for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            t = o["type"]
            if t in ("kill", "kill_boss"):
                oz = o["zone"]
                if oz not in Z:
                    bad.append(f"{qid}: sends you to {oz}, which this pass can't check")
                elif o["target"] not in Z[oz][1]:
                    bad.append(f"{qid}: {o['target']} doesn't spawn in {oz}")
                if o["target"] not in text:
                    bad.append(f"{qid}: never names {o['target']}")
                if oz in CAVES and q["giver_npc_id"] not in SQ.HUB_GIVERS:
                    bad.append(f"{qid}: a cave or dungeon quest that isn't given in a hub")
            if t == "fetch" and o["target"] not in item_source:
                bad.append(f"{qid}: fetches {o['target']}, which nothing drops")
            if t == "deliver" and o["target"] not in granted | set(SQ.STARTER_IDS):
                bad.append(f"{qid}: delivers {o['target']}, which nothing grants")
            if t == "gather" and o["target"] not in mats:
                bad.append(f"{qid}: gathers {o['target']}, which isn't a material")
            if t == "explore":
                seen, _s = Z[o["target"]]
                if seen is not None and (o["target_x"], o["target_y"]) not in seen:
                    bad.append(f"{qid}: {o['label']} ({o['target_x']},{o['target_y']}) is not a tile you can walk to")
        for nx in list(q.get("excludes_quests") or []):
            if nx not in ids:
                bad.append(f"{qid}: excludes {nx}, which this pass doesn't define")
            elif qid not in (next(x for x in quests if x["quest_id"] == nx).get("excludes_quests") or []):
                bad.append(f"{qid} excludes {nx}, but not the other way round")
        for nx in [q.get("next_quest_id")] + list(q.get("requires_quests") or []):
            if nx and nx not in ids:
                bad.append(f"{qid}: refers to {nx}, which this pass doesn't define")
        if re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+"
                     r"(haunch\w*|pelt\w*|snare\w*|hide\w*|scroll\w*|resin|lump\w*|cut\w*|fur|relic\w*|page\w*|"
                     r"scale\w*|stag\w*|bear\w*|wolves|gnoll\w*|ogre\w*|naga|yeti\w*|lotus|sungrass|whisker)\b", text, re.I):
            bad.append(f"{qid}: a count in the prose beside an objective word")
    return bad


def spec_audit(items):
    """Every spec of every class gets at least two quest rewards it can wear and wants."""
    from entities.character import Character
    from entities.proficiency import can_equip
    from entities.item import Item
    specs = {k: v for k, v in json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8")).items()
             if isinstance(v, dict) and "class" in v}
    with contextlib.redirect_stdout(io.StringIO()):
        chars = {sp["class"]: Character("QA", sp["class"], 60) for sp in specs.values()}
    objs = [Item.from_dict(dict(d, item_id=d.get("item_id") or d["name"])) for d in items]
    bad, fewest = [], 99
    for sid, sp in specs.items():
        n = sum(1 for it in objs if it.stat_template in TAKES[sp["stat_template"]] and can_equip(chars[sp["class"]], it)[0])
        fewest = min(fewest, n)
        if n < 2:
            bad.append(f"{sid} ({sp['class']}): {n} quest rewards it can wear and wants")
    combos = {(it.weapon_type if it.weapon_type else it.armor_type, it.stat_template) for it in objs}
    for need in (("leather", "str_physical"), ("mail", "spi_healer"), ("shield", "int_caster"),
                 ("plate", "spi_healer"), ("staff", "agi_physical")):
        if need not in combos:
            bad.append(f"no {need[0]} {need[1]} among the quest rewards")
    return bad, fewest, len(specs), len(chars)


def main():
    qs = SQ.build()
    ids = [q["quest_id"] for q in qs]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids", [i for i, n in collections.Counter(ids).items() if n > 1])
        return 1
    # a chain is a chain: the quest named as next requires the one that names it
    by = {q["quest_id"]: q for q in qs}
    for q in qs:
        nx = q.get("next_quest_id")
        if nx and nx in by:
            req = by[nx].setdefault("requires_quests", [])
            if q["quest_id"] not in req:
                req.append(q["quest_id"])
    rows = []
    for cre, rr in SQ.FETCH_DROPS.items():
        for r in rr:
            rows.append((cre, r[0], r[1], r[2], r[3] if len(r) > 3 else RATE, None))
    for cre, rr in SQ.STARTER_DROPS.items():
        for (iid, nm, desc, ch) in rr:
            rows.append((cre, iid, nm, desc, ch, SQ.STARTER_IDS[iid]))
    bad = audit(qs, [(r[0], r[1]) for r in rows])

    used, all_items = set(), []
    for q in qs:
        items, ilvl, rarity, b = author_rewards(q, used)
        bad += b
        is_boss = any(o["type"] == "kill_boss" for o in q["objectives"])
        mult = 1.5 if q.get("elite") else (1.3 if is_boss else 1.0)
        q["reward_exp"] = int(XP(q["level_max"]) * mult)
        q["reward_gold"] = int(GOLD(q["level_max"]) * mult)
        from tools.reward_icons import unclash
        for it in items:
            unclash(it)             # an epic's icon stays the epic's (Kyle, 16 Nov: "only have ONE icon")
        q["unique_item_defs"] = items
        q["gear_reward_gear_level"] = ilvl
        q["gear_reward_rarity"] = rarity
        if q.get("elite") and not q["title"].endswith("(Elite)"):
            q["title"] += " (Elite)"
        q.pop("_prefix", None)
        q.pop("_rewards", None)
        all_items += items
    sb, fewest, nspecs, nclasses = spec_audit(all_items)
    bad += sb
    if bad:
        print(f"\nFAILED ({len(bad)}) - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    OUT.write_text(json.dumps({"quests": qs}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for cre, iid, nm, desc, ch, starts in rows:
        have = {r["item_id"]: r for r in drops.get(cre, [])}
        rec = {"item_id": iid, "name": nm, "category": "quest", "description": desc, "chance": ch}
        if starts:
            rec["starts_quest_id"] = starts
        have[iid] = rec
        drops[cre] = list(have.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fd = json.loads(FACTIONS.read_text(encoding="utf-8"))
    pay = collections.Counter()
    for f in fd["factions"].values():
        qr = f.get("quest_rep")
        if qr and "also" in qr:
            qr["also"] = [x for x in qr["also"] if not x.startswith(ID_PREFIX)]
    for q in qs:
        g = q["giver_npc_id"]
        fid = FACTION_BY_STARTER.get(q["quest_id"]) if g.startswith("item:") else FACTION_BY_GIVER.get(g, DEFAULT_FACTION)
        if fid is None:
            continue
        fd["factions"][fid]["quest_rep"].setdefault("also", []).append(q["quest_id"])
        pay[fid] += 1
    FACTIONS.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    by_zone = collections.Counter(q["zone"] for q in qs)
    kinds = collections.Counter(o["type"] for q in qs for o in q["objectives"])
    hub = sum(1 for q in qs if q["giver_npc_id"] in SQ.HUB_GIVERS)
    gated = sum(1 for q in qs if q.get("requires_quests"))
    starters = sum(1 for q in qs if q["giver_npc_id"].startswith("item:"))
    print(f"{len(qs)} quests {dict(by_zone)}")
    print(f"  {hub} given in a hub, {starters} started by a dropped item, {gated} unlocked by earlier quests")
    print(f"  objectives {dict(kinds)}")
    print(f"  reputation {dict(pay)}")
    print(f"  {len(all_items)} rewards for {nspecs} specs of {nclasses} classes (fewest any spec gets: {fewest})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
