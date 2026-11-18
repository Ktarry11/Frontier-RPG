#!/usr/bin/env python3
"""Build the harvest finds: the runtime tables, the sixteen quest chains, the fishing gear and the stand-in icons.

    PYTHONPATH=. python3 tools/build_harvest_finds.py            # check everything, write nothing
    PYTHONPATH=. python3 tools/build_harvest_finds.py --write    # and write it

Content is tools/harvest_finds_content.py, the design docs/harvest_finds_design.md, the runtime world/harvest_finds.py.
The fishing mounts and titles are Collection entries, written by tools/build_collection.py from the same content.

Writes:
  data/gathering/harvest_finds.json    the starters, the Earth junk, the salvage, the fishing gear, mounts and titles
  data/quests/harvest_finds.json       32 quests: each starter's quest and the follow-up its turn-in gives
  stand-in icons for every new item that has no art yet (hue-shifted from a related icon, each one unique); the art
  sheet's slices replace them (docs/harvest_fishing_art_prompts.md) and a stand-in never overwrites real art.

Holds every line to Kyle's voice rules, every giver to four quests, every NPC, map, subzone and material to existing,
every explore point to walkable ground, and every icon to one item.
"""
import collections
import contextlib
import glob
import hashlib
import io
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import harvest_finds_content as H                       # noqa: E402
from tools.build_tempest_quests import voice_problems   # noqa: E402

OUT_DATA = ROOT / "data/gathering/harvest_finds.json"
OUT_QUESTS = ROOT / "data/quests/harvest_finds.json"
MAX_PER_GIVER = 4
ICONS = ROOT / "assets/icons"

#: Earth junk sells for a little, salvage for real coin (copper)
JUNK_PRICE = {"ej_garden_gnome": 150, "ej_wristwatch": 120}
JUNK_DEFAULT = 60
SALVAGE_PRICE = {"sv_barnacled_lockbox": 900, "sv_sodden_coin_purse": 600, "sv_goblin_canister": 400,
                 "sv_wreck_crate": 300}
#: stand-in sources by kind (globs under assets/icons)
STAND_IN = {"mining": "materials/inv_ore_*.png", "herbalism": "materials/inv_misc_herb_*.png",
            "skinning": "materials/inv_misc_leather*.png", "fishing": "quest_items/qi_*.png",
            "junk": "vendor_trash/vt_*[!0-9].png", "reins": "collection/col_reins_*.png"}
#: the reward slot for each chain's second quest, cycled so the sixteen don't all hand out chests
SLOTS = ["chest", "legs", "hands", "feet", "waist", "shoulder", "head", "wrist"]


def _npcs():
    out = {}
    for f in glob.glob(str(ROOT / "data/npcs/*.json")):
        doc = json.loads(Path(f).read_text(encoding="utf-8"))

        def walk(o):
            if isinstance(o, dict):
                if o.get("npc_id") and o.get("name"):
                    out.setdefault(o["npc_id"], o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(doc)
    return out


def _existing_quests():
    givers, ids = collections.Counter(), set()
    for f in glob.glob(str(ROOT / "data/quests/*.json")):
        if Path(f) == OUT_QUESTS:
            continue
        for q in json.loads(Path(f).read_text(encoding="utf-8")).get("quests", []):
            givers[q.get("giver_npc_id")] += 1
            ids.add(q["quest_id"])
    return givers, ids


def _median_rewards():
    """The game's own XP and gold for a quest of each level, so these pay like their neighbours."""
    xp, gold = collections.defaultdict(list), collections.defaultdict(list)
    for f in glob.glob(str(ROOT / "data/quests/*.json")):
        if Path(f) == OUT_QUESTS:
            continue
        for q in json.loads(Path(f).read_text(encoding="utf-8")).get("quests", []):
            lvl = q.get("level_max") or q.get("level_min")
            if lvl and q.get("reward_exp"):
                xp[int(lvl)].append(q["reward_exp"])
                gold[int(lvl)].append(q.get("reward_gold", 0) or 0)

    def med(table, lvl):
        for d in range(0, 6):
            for k in (lvl - d, lvl + d):
                if table.get(k):
                    vals = sorted(table[k])
                    return vals[len(vals) // 2]
        return 0
    return (lambda lvl: med(xp, lvl)), (lambda lvl: med(gold, lvl))


def _place_town(npc):
    """'Name, Town' for a delivery label."""
    from world.zone_keys import zone_key
    z = str(npc.get("zone") or "")
    town = z.replace("_", " ").title().replace("'S", "'s") if z else ""
    names = {"razor_hill": "Razor Hill", "central_barrens": "the Central Barrens", "camp_taurajo": "Camp Taurajo",
             "southern_barrens": "the Southern Barrens", "arathi_central": "Arathi", "the_black_strand": "the Black Strand",
             "aridens_watch": "Ariden's Watch", "orgrimmar": "Orgrimmar", "sun_rock_retreat": "Sun Rock Retreat",
             "hammerfall": "Hammerfall", "moonglade": "Nighthaven", "tarren_mill": "Tarren Mill", "gromgol": "Grom'gol",
             "bulwark": "the Bulwark", "ratchet": "Ratchet", "central_stranglethorn": "Stranglethorn"}
    return f"{npc['name']}, {names.get(zone_key(z), town)}"


def _explore_point(zm, map_name, subzone):
    """A walkable tile in the middle of the subzone's largest rectangle, nearest its centre."""
    t = zm.zones[map_name]["tilemap"]
    rects = [s for s in t.subzones if s.get("name") == subzone]
    if not rects:
        return None
    r = max(rects, key=lambda s: s["w"] * s["h"])
    cx, cy = r["x"] + r["w"] // 2, r["y"] + r["h"] // 2
    best = None
    for y in range(r["y"], r["y"] + r["h"]):
        for x in range(r["x"], r["x"] + r["w"]):
            if t.is_walkable(x, y):
                d = abs(x - cx) + abs(y - cy)
                if best is None or d < best[0]:
                    best = (d, x, y)
    return best and (best[1], best[2])


# ------------------------------------------------------------------------------------------------- stand-in icons
def _hash(img):
    return hashlib.md5(img.convert("RGBA").resize((56, 56)).tobytes()).hexdigest()


def _taken_hashes():
    from PIL import Image
    out = set()
    for p in ICONS.rglob("*.png"):
        try:
            out.add(_hash(Image.open(p)))
        except Exception:
            pass
    return out


def stand_ins(wanted, write):
    """wanted: [(dest_path, kind, seed)]. Makes each missing one by hue-shifting a source of its kind until the
    picture is like no other icon in the game. Never touches a file that's already there (that's real art)."""
    from PIL import Image
    import colorsys
    taken = None
    made, problems = [], []
    for dest, kind, seed in wanted:
        if dest.exists():
            continue
        if taken is None:
            taken = _taken_hashes()
        srcs = sorted(glob.glob(str(ICONS / STAND_IN[kind])))
        if not srcs:
            problems.append(f"no stand-in source for {dest.name}")
            continue
        h = int(hashlib.md5(seed.encode()).hexdigest(), 16)
        done = False
        for attempt in range(24):
            src = srcs[(h + attempt) % len(srcs)]
            base = Image.open(src).convert("RGBA")
            shift = ((h >> 8) % 360 + attempt * 37) % 360 / 360.0
            px = base.load()
            img = base.copy()
            out = img.load()
            for y in range(base.size[1]):
                for x in range(base.size[0]):
                    r, g, b, a = px[x, y]
                    hh, ss, vv = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
                    r2, g2, b2 = colorsys.hsv_to_rgb((hh + shift) % 1.0, ss, vv)
                    out[x, y] = (int(r2 * 255), int(g2 * 255), int(b2 * 255), a)
            hv = _hash(img)
            if hv in taken:
                continue
            taken.add(hv)
            if write:
                dest.parent.mkdir(parents=True, exist_ok=True)
                img.save(dest)
            made.append(dest.name)
            done = True
            break
        if not done:
            problems.append(f"couldn't make a unique stand-in for {dest.name}")
    return made, problems


# ------------------------------------------------------------------------------------------------- the gear
def fishing_gear():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    from tools.reward_icons import unclash
    C.PICKER = Picker()
    out, bad = [], []
    for gid, name, slot, kind, typ, ident, ilvl, rarity, flav in H.FISH_GEAR:
        o = {"kind": kind, "slot": slot, "item_level": ilvl, "rarity": rarity, "required_level": max(1, ilvl - 2),
             "stat_template": C.IDENTITIES[ident][1]}
        if kind == "weapon":
            o["weapon_type"] = typ
            ident = C.weapon_identity(typ, ident)
        else:
            o["armor_type"] = typ
        item = C.author(gid, {"name": name, "output": o}, ident, flav)
        item["required_level"] = max(1, ilvl - 2)
        item["item_id"] = gid
        unclash(item)
        bad += C.audit_item("fishing", gid, item)
        from entities.item_budget import budget_ratio, fit_to_curve
        r = budget_ratio(item)
        if r and not 0.65 <= r <= 1.45:          # the audit band (tools/audit_item_curve.py): back onto the line
            fit_to_curve(item)
        item.pop("identity", None)
        out.append(item)
    return out, bad


# ------------------------------------------------------------------------------------------------- the quests
def build(write=False):
    import pygame
    pygame.init()
    pygame.display.set_mode((8, 8))
    with contextlib.redirect_stdout(io.StringIO()):
        from world.zone_manager import ZoneManager
        zm = ZoneManager()
    from world.zone_keys import zone_key

    problems = []
    npcs = _npcs()
    givers, existing = _existing_quests()
    xp, gold = _median_rewards()
    mats = json.loads((ROOT / "data/gathering/materials.json").read_text(encoding="utf-8"))
    mats = mats.get("materials", mats)

    quests, starters = [], []
    new_gives = collections.Counter()
    for n, s in enumerate(H.STARTERS):
        short = s["id"][3:]
        q1id, q2id = f"hf_{short}_1", f"hf_{short}_2"
        for m in s.get("mats", []):
            if m not in mats:
                problems.append(f"{s['id']}: material {m} doesn't exist")
        q1, q2 = s["q1"], s["q2"]
        to = npcs.get(q1["to"])
        if not to:
            problems.append(f"{s['id']}: {q1['to']} doesn't exist")
            continue
        starters.append({"id": s["id"], "item_id": s["id"], "name": s["name"], "desc": s["desc"], "trade": s["trade"],
                         "mats": s.get("mats", []), "band": list(s["band"]), "quest": q1id,
                         "icon": s["id"]})
        lo1, hi1 = q1["lvl"]
        quests.append({
            "quest_id": q1id, "title": q1["title"], "giver_npc_id": f"item:{s['id']}", "zone": zone_key(to["zone"]),
            "level_min": lo1, "level_max": hi1, "description": q1["desc"],
            "objectives": [{"type": "deliver", "target": s["id"], "count": 1, "label": _place_town(to)}],
            "turn_in_npc_id": q1["to"], "accept_text": q1["accept"], "turn_in_text": q1["done"],
            "reward_exp": int(xp(hi1) * 0.6), "reward_gold": int(gold(hi1) * 0.6), "next_quest_id": q2id,
        })
        lo2, hi2 = q2["lvl"]
        kind = q2["obj"][0]
        q = {"quest_id": q2id, "title": q2["title"], "giver_npc_id": q1["to"], "zone": zone_key(to["zone"]),
             "level_min": lo2, "level_max": hi2, "description": q2["desc"], "accept_text": q2["accept"],
             "turn_in_text": q2["done"], "reward_exp": xp(hi2), "reward_gold": gold(hi2), "next_quest_id": None,
             "requires_quests": [q1id], "gear_reward_gear_level": hi2, "gear_reward_slot": SLOTS[n % len(SLOTS)],
             "gear_reward_rarity": "rare" if hi2 >= 45 else "uncommon"}
        if kind == "deliver":
            dest = npcs.get(q2["obj"][1])
            if not dest:
                problems.append(f"{q2id}: {q2['obj'][1]} doesn't exist")
                continue
            carried = f"{s['id']}_carried"
            q["grant_items"] = {"on_accept": [{"item_id": carried, "name": s["name"], "description": s["desc"],
                                               "count": 1, "icon_id": s["id"]}]}
            q["objectives"] = [{"type": "deliver", "target": carried, "count": 1, "label": _place_town(dest)}]
            q["turn_in_npc_id"] = q2["obj"][1]
        else:
            _, map_name, subzone = q2["obj"]
            if map_name not in zm.zones:
                problems.append(f"{q2id}: no map {map_name}")
                continue
            pt = _explore_point(zm, map_name, subzone)
            if not pt:
                problems.append(f"{q2id}: no walkable ground in {subzone} on {map_name}")
                continue
            q["objectives"] = [{"type": "explore", "target": zone_key(map_name), "target_x": pt[0], "target_y": pt[1],
                                "radius": 6, "label": f"Look round {subzone}"}]
        quests.append(q)
        new_gives[q1["to"]] += 1

    # ---- the rules
    ids = [q["quest_id"] for q in quests]
    if len(set(ids)) != len(ids) or set(ids) & existing:
        problems.append("a quest id is taken")
    for g, n in new_gives.items():
        if givers[g] + n > MAX_PER_GIVER:
            problems.append(f"{g} would give {givers[g] + n} quests (at most {MAX_PER_GIVER})")
    for q in quests:
        for field in ("description", "accept_text", "turn_in_text"):
            for p in voice_problems(q.get(field, "")):
                problems.append(f"{q['quest_id']} {field}: {p}")
        if "'" not in q["accept_text"] and "’" not in q["accept_text"]:
            problems.append(f"{q['quest_id']}: the accept line has no contraction")

    # ---- the tables
    junk = [{"id": i, "name": n, "desc": d, "price": JUNK_PRICE.get(i, JUNK_DEFAULT), "icon": i}
            for i, n, d in H.EARTH_JUNK]
    salvage = [{"id": i, "name": n, "desc": d, "price": SALVAGE_PRICE[i], "icon": i} for i, n, d in H.SALVAGE]
    gear, bad = fishing_gear()
    problems += [f"fishing gear: {b}" for b in bad]
    tables = {"_about": "Built by tools/build_harvest_finds.py from tools/harvest_finds_content.py; read by "
                        "world/harvest_finds.py. docs/harvest_finds_design.md.",
              "starters": starters, "earth_junk": junk, "salvage": salvage, "fish_gear": gear,
              "mounts": [{"id": m, "name": n, "pools": list(p)} for m, n, p, _b in H.MOUNTS],
              "titles": [{"id": t, "title": n, "needs": need} for t, n, _h, need in H.TITLES]}

    # ---- stand-in icons, and one icon per item
    wanted = [(ICONS / "quest_items" / f"{s['id']}.png", s["trade"], s["id"]) for s in starters]
    wanted += [(ICONS / "vendor_trash" / f"{r['id']}.png", "junk", r["id"]) for r in junk + salvage]
    wanted += [(ICONS / "collection" / f"col_reins_{m}.png", "reins", m) for m, *_r in H.MOUNTS]
    made, icon_bad = stand_ins(wanted, write)
    problems += icon_bad
    gear_icons = collections.Counter(g.get("icon_id") for g in gear)
    problems += [f"two fishing gear pieces share {i}" for i, c in gear_icons.items() if c > 1]

    print(f"  {len(starters)} starters, {len(quests)} quests, {len(junk)} Earth junk, {len(salvage)} salvage, "
          f"{len(gear)} fishing gear, {len(H.MOUNTS)} mounts, {len(H.TITLES)} titles")
    print(f"  givers: " + ", ".join(f"{g} {givers[g]}+{n}" for g, n in sorted(new_gives.items())))
    print(f"  stand-in icons {'made' if write else 'to make'}: {len(made)}")
    for p in problems:
        print("  PROBLEM", p)
    if write and not problems:
        OUT_DATA.write_text(json.dumps(tables, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        OUT_QUESTS.write_text(json.dumps({"_about": tables["_about"], "quests": quests}, indent=2,
                                         ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  written {OUT_DATA.relative_to(ROOT)}, {OUT_QUESTS.relative_to(ROOT)}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(build("--write" in sys.argv))
