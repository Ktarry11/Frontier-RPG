#!/usr/bin/env python3
"""Arathi in its people's own voices, and Hammerfall with the quests a hold should have. Idempotent.

    PYTHONPATH=. python3 tools/build_arathi_voice.py [--check]

Kyle, 16 Nov 2026: "why does hammerfall have like 3 quests only? ... Theyre also written in weird AI tics. Did
hammerfall get nuked and all the NPCs died?"

WHAT WAS WRONG.
  - Hammerfall had five givers and ten quests, and two of the ten were deep in the Drywhisker chain. A level-33
    player walking in saw four or five, all at 34-36. Thirteen of the hold's eighteen people gave nothing.
  - The text (data/quests/text/zz_overhaul_arathi.json, 35 of 46) was third-person descriptions of the giver, no
    contractions, and an aphorism to close nearly every turn-in.
  - Several objectives didn't match their own text: "Four Circles" sent you to the gaps between the circles, "The
    Answer" sent you east of Hammerfall to count a circle in the west, "Gallowmast" sent you to the Tidewrack,
    "What the Harbinger Hears" sent you south of Boulder'gor for charms in Witherbark Hollow, and "Ask Them First"
    completed on accept (it handed you a stone and asked you to deliver it to the giver herself).

WHAT THIS DOES.
  1. Ten new Hammerfall quests (hf_*) from eight of the hold's people who had none, at 33-35 (the town's first
     level), merged into data/quests/arathi.json by id, with their quest items in quest_drops.json and the two
     Forsaken givers' quests paying the Forsaken (factions.json "also"). Hammerfall goes from 10 to 20.
  2. The objective fixes above, in arathi.json, and "The Answer" now leads to "Boulderfist Hall", whose text
     depends on it.
  3. Every Arathi quest's text from tools/arathi_quest_voice.py, written as the overlay.
  4. Checks: the voice rules (tools/build_tempest_quests.voice_problems: no "it is not X, it is Y", contractions, no
     dashes, no fragments), a contraction in every accept line, every kill named, no count beside an objective word,
     every explore tile walkable and reachable from the zone's way in, at most five quests a giver.

tools/build_arathi_quests.py writes arathi.json from scratch and would drop the hf_ quests and the objective fixes;
it is not to be re-run (its own docstring says so now). This tool is the one to run.
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
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools import build_arathi_quests as B                 # noqa: E402
from tools.arathi_quest_voice import VOICE                 # noqa: E402
from tools.build_durotar_quests import fetch                # noqa: E402

QUESTS = ROOT / "data/quests/arathi.json"
OVERLAY = ROOT / "data/quests/text/zz_overhaul_arathi.json"
DROPS = ROOT / "data/creatures/quest_drops.json"
FACTIONS = ROOT / "data/factions/factions.json"
MAX_PER_GIVER = 5
RATE = 0.75          # Kyle: quest items drop about 75% of the time when a quest needs several

AC, AW, AE = B.AC, B.AW, B.AE
MOK, GATHROK, KESKA = B.MOK, B.GATHROK, B.KESKA
RUKKA, GRETTHA, URGA = "hammerfall_stablemaster", "hammerfall_innkeeper", "hammerfall_quartermaster"
KROL, DREKA, MOLG, SHELNA = ("hammerfall_weaponsmith", "hammerfall_windrider_master", "hammerfall_general_goods",
                             "hammerfall_reagent_vendor")
FORSAKEN_NEW = ["hf_meat_for_the_fire", "hf_by_the_measure"]

#: the four circles' centres (tools/handbuilt_arathi_central.RINGS) and the other places the fixes point at
RING = [(62, 88), (94, 88), (122, 88), (150, 90)]
HALL_MOUTH = (38, 43)            # Boulderfist Hall's cave mouth, the arrival tile below it
SHELF_LIP = (94, 40)             # the North Shelf, where the ogres come down
CRASH = (80, 28)                 # the North Shelf, up behind the lip
GALLOWMAST = (150, 62)
HOLLOW_DEEP = (150, 38)          # the deepest part of Witherbark Hollow

#: new quest items: (creature, item id, name, description, chance)
NEW_DROPS = [
    ("Boulderfist Shaman", "boulderfist_signal_horn", "Boulderfist Signal Horn",
     "Long and low, and another answers it from the west.", RATE),
    ("Highland Elk", "highland_elk_haunch", "Highland Elk Haunch",
     "A haunch off one of these does a whole table.", RATE),
    ("Witherbark Berserker", "hammerfall_supply_bundle", "Hammerfall Supply Bundle",
     "Salted pork, boot nails and lamp oil, cut loose from a cart and not touched since.", RATE),
    ("Boulderfist Mauler", "boulderfist_iron_band", "Boulderfist Iron Band",
     "Thick as a wrist, and older than the ogre wearing it.", RATE),
    ("Boulderfist Mauler", "wind_rider_harness", "Wind Rider Harness",
     "Hand-stitched at Hammerfall's roost. The strap has been cut, not torn.", 0.5),
    ("Witherbark Venomweaver", "venomweaver_venom_sac", "Venomweaver Venom Sac",
     "Whole, and it has to stay that way until Shelna has weighed it.", RATE),
]


def T(qid):
    v = VOICE[qid]
    return v["desc"], v["accept"], v["done"]


def new_quests():
    Q, k, ex = B.Q, B.k, B.explore
    out = []

    def add(qid, title, giver, lo, hi, theme, objs, **kw):
        d, a, t = T(qid)
        out.append(Q(qid, title, giver, AC, lo, hi, theme, d, objs, a, t, **kw))

    add("hf_orders_for_the_yard", "Orders for the Yard", GATHROK, 33, 33, "ogre",
        [B.deliver("gathrok_yard_orders", "Give the Overlord's orders to Sergeant Mok")],
        nxt="hf_the_north_shelf", turn_in_npc_id=MOK,
        grant_items=B.carry("gathrok_yard_orders", "The Overlord's Orders",
                            "Folded once, sealed with the hold's mark, and addressed to the muster yard."))
    add("hf_the_north_shelf", "The North Shelf", MOK, 33, 34, "ogre",
        [ex(AC, *SHELF_LIP, 7) | {"label": "the lip of the North Shelf"}, k("Boulderfist Mauler", 8, AC)],
        nxt="hf_horns_on_the_shelf")
    add("hf_horns_on_the_shelf", "Horns on the Shelf", MOK, 35, 35, "ogre",
        [fetch("boulderfist_signal_horn", 5)])
    add("hf_the_kodo_wont_settle", "The Kodo Won't Settle", RUKKA, 33, 33, "rings",
        [k("Ring Wisp", 10, AC)])
    add("hf_meat_for_the_fire", "Meat for the Fire", GRETTHA, 33, 33, "moor",
        [fetch("highland_elk_haunch", 6)])
    add("hf_the_supply_road", "The Supply Road", URGA, 34, 34, "witherbark",
        [k("Witherbark Berserker", 8, AC), fetch("hammerfall_supply_bundle", 5)])
    add("hf_ogre_iron", "Ogre Iron", KROL, 34, 34, "ogre",
        [fetch("boulderfist_iron_band", 6)])
    add("hf_the_downed_rider", "The Downed Rider", DREKA, 35, 35, "ogre",
        [ex(AC, *CRASH, 7) | {"label": "where the rider came down on the North Shelf"},
         fetch("wind_rider_harness", 1)])
    add("hf_a_parcel_for_keska", "A Parcel for Keska", MOLG, 33, 33, "moor",
        [B.deliver("molg_boots_parcel", "Give Molg's parcel to Runner Keska on the Refuge Road")],
        turn_in_npc_id=KESKA,
        grant_items=B.carry("molg_boots_parcel", "Molg's Parcel",
                            "A pair of new boots, wrapped in sacking and tied with more knots than it needs."))
    add("hf_by_the_measure", "By the Measure", SHELNA, 35, 35, "witherbark",
        [fetch("venomweaver_venom_sac", 6)])
    for q in out:
        for o in q["objectives"]:
            if o["type"] == "fetch":
                o["label"] = next(n for (_c, i, n, _d, _r) in NEW_DROPS if i == o["target"])
    return out


def fix_objectives(by_id):
    """The objectives that didn't match their own text. Returns what changed."""
    ch = []

    def ex(zone, xy, r, label):
        return dict(type="explore", target=zone, target_x=xy[0], target_y=xy[1], radius=r, label=label)

    q = by_id["arc_four_circles"]
    want = [ex(AC, RING[i], 5, f"the {n} circle on the Ring Road")
            for i, n in enumerate(("first", "second", "third", "fourth"))]
    if q["objectives"] != want:
        q["objectives"] = want
        ch.append("arc_four_circles: stands you in the four circles, not between them")
    q = by_id["arc_the_bound"]
    for o in q["objectives"]:
        if o["type"] == "explore" and (o["target_x"], o["target_y"]) != RING[3]:
            o.update(target_x=RING[3][0], target_y=RING[3][1], radius=6, label="the easternmost circle")
            ch.append("arc_the_bound: the easternmost circle itself")
    q = by_id["arc_ask_them"]
    want = [ex(AC, HALL_MOUTH, 6, "the mouth of Boulderfist Hall")]
    if q["objectives"] != want or q.get("grant_items"):
        q["objectives"] = want
        q.pop("grant_items", None)
        ch.append("arc_ask_them: you carry the stone to the hall's mouth (it completed on accept)")
    q = by_id["arc_the_answer"]
    for o in q["objectives"]:
        if o["type"] == "explore" and (o["target_x"], o["target_y"]) != RING[0]:
            o.update(target_x=RING[0][0], target_y=RING[0][1], radius=6, label="the westernmost circle")
            ch.append("arc_the_answer: counts the westernmost circle, not a field east of Hammerfall")
    if q.get("next_quest_id") != "arc_the_hall":
        q["next_quest_id"] = "arc_the_hall"
        ch.append("arc_the_answer -> arc_the_hall (the Overlord's quest says the Envoy has withdrawn)")
    q = by_id["are_gallowmast"]
    for o in q["objectives"]:
        if o["type"] == "explore" and (o["target_x"], o["target_y"]) != GALLOWMAST:
            o.update(target_x=GALLOWMAST[0], target_y=GALLOWMAST[1], radius=9, label="Gallowmast Isle")
            ch.append("are_gallowmast: Gallowmast Isle, not the Tidewrack")
    q = by_id["are_six_wrecks"]
    for o in q["objectives"]:
        if o["type"] == "explore" and (o["target_x"], o["target_y"]) == (58, 86):
            o.update(target_x=57, target_y=86)
            ch.append("are_six_wrecks: the hull below the Landing at a tile you can stand on (58,86 is rock)")
    q = by_id["arw_stro_the_claim"]
    for o in q["objectives"]:
        if o["type"] == "explore" and (o["target_x"], o["target_y"]) == (46, 140):
            o.update(target_y=141)
            ch.append("arw_stro_the_claim: (46,140) was the Antiquarian's own tile; she's in Refuge Pointe now")
    q = by_id["arw_what_veska_hears"]
    for o in q["objectives"]:
        if o["type"] == "explore" and (o["target_x"], o["target_y"]) != HOLLOW_DEEP:
            o.update(target_x=HOLLOW_DEEP[0], target_y=HOLLOW_DEEP[1], radius=8,
                     label="the deepest part of Witherbark Hollow")
            ch.append("arw_what_veska_hears: Witherbark Hollow, not south of Boulder'gor")
    return ch


# ---------------------------------------------------------------------------------------------------- checks
def _zones():
    from tools import handbuilt_arathi_west as W, handbuilt_arathi_central as C, handbuilt_arathi_east as E
    out = {}
    with contextlib.redirect_stdout(io.StringIO()):
        for key, mod, gen in ((AW, W, "generate_arathi_west"), (AC, C, "generate_arathi_central"),
                              (AE, E, "generate_arathi_east")):
            z = getattr(mod, gen)()
            start = tuple(getattr(mod, "START", None) or next(iter(mod.ARRIVALS)))
            seen, todo = {start}, [start]
            while todo:
                x, y = todo.pop()
                for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                    if (nx, ny) not in seen and 0 <= nx < z.width and 0 <= ny < z.height and z.is_walkable(nx, ny):
                        seen.add((nx, ny))
                        todo.append((nx, ny))
            out[key] = seen
    return out


def spawns():
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    names = {AW: "Arathi West", AC: "Arathi Central", AE: "Arathi East"}
    out = {}
    for key, nm in names.items():
        z = enc[nm]
        s = set(z["open_zone"]["creatures"])
        for sub in (z.get("subzones") or {}).values():
            s |= set(sub["creatures"])
        out[key] = s
        for cave, t in (z.get("caves") or {}).items():
            out[cave.lower().replace(" ", "_").replace("'", "")] = set(t["creatures"])
    return out


def audit(quests, overlay):
    from tools.build_tempest_quests import voice_problems
    bad = []
    seen = _zones()
    sp = spawns()
    drops = json.loads(DROPS.read_text(encoding="utf-8"))
    table = drops.get("drops", drops)
    dropped = {d["item_id"] for rows in table.values() for d in rows}
    item_names = {d["item_id"]: d.get("name", "") for rows in table.values() for d in rows}
    dropped |= {r[1] for r in NEW_DROPS}           # in --check they aren't written yet
    item_names.update({r[1]: r[2] for r in NEW_DROPS})
    givers = collections.Counter(q["giver_npc_id"] for q in quests)
    for g, n in givers.items():
        if n > MAX_PER_GIVER:
            bad.append(f"{g} gives {n} quests")
    for q in quests:
        qid = q["quest_id"]
        o = overlay.get(qid, {})
        t = {k: o.get(k) or q.get(k) or "" for k in ("title", "description", "accept_text", "turn_in_text")}
        text = " ".join(t.values())
        if qid not in VOICE:
            bad.append(f"{qid}: no voice written")
        if not text.isascii():
            bad.append(f"{qid}: non-ASCII text")
        for key in ("description", "accept_text", "turn_in_text"):
            for p in voice_problems(t[key]):
                bad.append(f"{qid} {key}: {p}")
            if len(t[key]) > 900:
                bad.append(f"{qid} {key}: {len(t[key])} characters")
        if "'" not in t["accept_text"]:
            bad.append(f"{qid}: no contraction in the accept line")
        granted = {g["item_id"] for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        words = set()
        for ob in q["objectives"]:
            ty = ob["type"]
            if ty in ("kill", "kill_boss"):
                if ob["target"] not in text:
                    bad.append(f"{qid}: never names {ob['target']}")
                z = ob.get("zone")
                if z in sp and ob["target"] not in sp[z]:
                    bad.append(f"{qid}: {ob['target']} doesn't spawn in {z}")
            if ty == "fetch" and ob["target"] not in dropped:
                bad.append(f"{qid}: fetches {ob['target']}, which nothing drops")
            if ty == "deliver" and ob["target"] not in granted:
                bad.append(f"{qid}: delivers {ob['target']}, which nothing grants")
            if ty == "explore" and ob["target"] in seen:
                if (ob["target_x"], ob["target_y"]) not in seen[ob["target"]]:
                    bad.append(f"{qid}: {ob.get('label')} ({ob['target_x']},{ob['target_y']}) can't be walked to")
            if ty in ("kill", "kill_boss", "fetch"):
                name = item_names.get(ob["target"], ob["target"]) if ty == "fetch" else ob["target"]
                words.add(re.sub(r"(es|s)$", "", name.split()[-1].lower()))
        if words and re.search(r"\b(two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|\d+)\s+(\w+\s+)?("
                               + "|".join(re.escape(w) for w in words) + r")\w*\b", text, re.I):
            bad.append(f"{qid}: a count in the prose beside an objective word")
    return bad


def hub_report(quests):
    town = ("hammerfall_", "saltspur_", "arathi_refuge_")
    by = collections.defaultdict(lambda: [0, 0])
    for q in quests:
        by[q["zone"]][0] += q["giver_npc_id"].startswith(town)
        by[q["zone"]][1] += 1
    return {z: f"{a}/{n} from a town" for z, (a, n) in sorted(by.items())}


def main():
    check = "--check" in sys.argv
    doc = json.loads(QUESTS.read_text(encoding="utf-8"))
    quests = doc["quests"]
    by_id = {q["quest_id"]: q for q in quests}
    changes = fix_objectives(by_id)
    added = 0
    for q in new_quests():
        if q["quest_id"] in by_id:
            continue
        quests.append(q)
        by_id[q["quest_id"]] = q
        added += 1
    unknown = sorted(set(VOICE) - set(by_id))
    if unknown:
        raise SystemExit(f"voice written for quests that don't exist: {unknown}")
    overlay = {}
    for qid, v in VOICE.items():
        e = {"description": v["desc"], "accept_text": v["accept"], "turn_in_text": v["done"]}
        if v.get("title"):
            e["title"] = v["title"]
        overlay[qid] = e
        # the record carries the same words, so a tool reading arathi.json alone sees what the player does
        q = by_id[qid]
        q["description"], q["accept_text"], q["turn_in_text"] = e["description"], e["accept_text"], e["turn_in_text"]

    if not check:
        QUESTS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        OVERLAY.write_text(json.dumps(overlay, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        drops = json.loads(DROPS.read_text(encoding="utf-8"))
        table = drops.setdefault("drops", drops)
        for cre, iid, name, desc, ch in NEW_DROPS:
            rows = [d for d in table.get(cre, []) if d["item_id"] != iid]
            rows.append({"item_id": iid, "name": name, "category": "quest", "description": desc, "chance": ch})
            table[cre] = rows
        DROPS.write_text(json.dumps(drops, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        fx = json.loads(FACTIONS.read_text(encoding="utf-8"))
        also = fx["factions"]["the_forsaken"].setdefault("also", [])
        for qid in FORSAKEN_NEW:
            if qid not in also:
                also.append(qid)
        FACTIONS.write_text(json.dumps(fx, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    for c in changes:
        print(f"  fixed {c}")
    print(f"{added} new Hammerfall quests; {len(VOICE)} quests voiced; arathi.json holds {len(quests)}")
    print("  " + ", ".join(f"{z} {r}" for z, r in hub_report(quests).items()))
    hf = sum(1 for q in quests if q["giver_npc_id"].startswith("hammerfall_"))
    print(f"  Hammerfall gives {hf}")
    bad = audit(quests, overlay)
    for b in bad:
        print("  FAIL " + b)
    print("arathi voice OK" if not bad else f"FAILED: {len(bad)}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
