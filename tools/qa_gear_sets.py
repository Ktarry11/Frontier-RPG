#!/usr/bin/env python3
"""Gear sets: the engine counts pieces, pays bonuses, and says so on the card.

    PYTHONPATH=. python3 tools/qa_gear_sets.py

Kyle, [95]: "We NEED to start working on getting gear sets." Item.set_id had been stored and
saved since the item class was written and nothing read it.

EIGHT CLAIMS:

  1. A BONUS ARRIVES AT ITS PIECE COUNT and not one piece sooner.
  2. BONUSES STACK UP THE LADDER - at four pieces you have the two-piece bonus too.
  3. TAKING A PIECE OFF TAKES THE BONUS OFF, at once.
  4. A SET BONUS IS WORTH EXACTLY WHAT THE SAME STAT ON A RING IS - it goes through the pool
     gear does, so it cannot be double-counted or mis-scaled.
  5. A PIECE SURVIVES A SAVE with its set intact.
  6. THE CARD LISTS the set, every piece (worn ones marked), and every bonus (earned ones
     marked) - for whoever is reading it.
  8. ONE SET, A VERSION PER SPEC. Kyle: "we have hybrid classes too... keep the SET name, but
     change the stuff inside... we wont mix and match. A shaman who uses 5 enhancement and 3
     elemental gets 2 and 4 piece enhancement bonus and 2 piece elemental." Each version is
     counted on its own and pays its own bonuses; a piece can be exchanged, free, for another
     spec's version by an Artifact Keeper (Orgrimmar, Undercity, Kael's Bastion, Freewind
     Post, Booty Bay) - name, stats and version
     change; slot, level, rarity and set do not.
  7. EVERY SET THAT SHIPS IS WELL FORMED: real slots, a class that exists, bonuses whose stats
     actually move a character sheet, and thresholds that can be reached.
"""
import contextlib
import io
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

with contextlib.redirect_stdout(io.StringIO()):
    from entities.character import Character
    from entities.item import Item
    from entities.equipment import EQUIPMENT_SLOTS
    from world import gear_sets as GS

TEST = "qa_test_set"
SLOTS = ["head", "shoulder", "chest", "hands", "legs", "feet"]


def make(cls="Warrior"):
    with contextlib.redirect_stdout(io.StringIO()):
        return Character(name="T", char_class=cls, level=60)


def piece(slot, set_id=TEST):
    return Item(f"qa_{slot}", f"Test {slot}", slot, 60, "rare", armor_type="plate", set_id=set_id)


def wear(c, slots, set_id=TEST):
    for s in SLOTS:
        c.equipment.slots[s] = None
    for s in slots:
        c.equipment.slots[s] = piece(s, set_id)
    c._recalculate_derived_stats()


def main():
    bad = []
    GS.register(TEST, {"name": "Test Battlegear", "class": "Warrior",
                       "pieces": {s: f"Test {s}" for s in SLOTS},
                       "bonuses": {"2": {"stats": {"strength": 20}},
                                   "4": {"stats": {"attack_power": 40}},
                                   "6": {"stats": {"stamina": 30}, "text": "+30 Stamina, said by hand"}}})
    c = make()
    wear(c, [])
    s0, ap0 = c.effective_strength, c.attack_power

    # 1. not one piece sooner
    wear(c, SLOTS[:1])
    if c.effective_strength != s0:
        bad.append("one piece of a set paid the two-piece bonus")
    wear(c, SLOTS[:2])
    if c.effective_strength - s0 != 20:
        bad.append(f"two pieces should give +20 Strength, gave {c.effective_strength - s0}")
    ap2 = c.attack_power
    wear(c, SLOTS[:3])
    if c.attack_power != ap2:
        bad.append("three pieces paid the four-piece bonus")

    # 2. up the ladder
    wear(c, SLOTS[:4])
    if c.effective_strength - s0 != 20:
        bad.append("at four pieces the two-piece bonus was lost or doubled")
    if c.attack_power - ap2 != 40:
        bad.append(f"four pieces should add 40 attack power, added {c.attack_power - ap2}")
    if GS.active_bonuses(c) != {"strength": 20, "attack_power": 40}:
        bad.append(f"active_bonuses at four pieces is {GS.active_bonuses(c)}")

    # 3. off comes the bonus
    wear(c, SLOTS[:3])
    if c.attack_power != ap2:
        bad.append("dropping from four pieces to three kept the four-piece bonus")
    wear(c, [])
    if (c.effective_strength, c.attack_power) != (s0, ap0):
        bad.append("taking the whole set off did not return the sheet to where it started")

    # a piece of ANOTHER set does not count
    wear(c, SLOTS[:1])
    c.equipment.slots[SLOTS[1]] = piece(SLOTS[1], "some_other_set")
    c._recalculate_derived_stats()
    if c.effective_strength != s0:
        bad.append("a piece of a different set counted toward this one")

    # 4. worth exactly what gear is
    plain = make()
    plain.equipment.slots["ring1"] = Item("qa_ring", "Ring", "ring1", 60, "rare",
                                          primary_stats={"strength": 20})
    plain._recalculate_derived_stats()
    wear(c, SLOTS[:2])
    bare = make()
    if (c.effective_strength - s0) != (plain.effective_strength - bare.effective_strength):
        bad.append("a +20 Strength set bonus and a +20 Strength ring move the sheet by different amounts")

    # 5. save round trip
    back = Item.from_dict(piece("head").to_dict())
    if getattr(back, "set_id", None) != TEST:
        bad.append("a set piece came back from a save without its set")

    # 6. the card
    wear(c, SLOTS[:2])
    lines = GS.tooltip_lines(piece("head"), c)
    kinds = [k for _t, k in lines]
    if not lines or lines[0] != ("Test Battlegear (2/6)", "title"):
        bad.append(f"the card's set heading is {lines[:1]}")
    if kinds.count("have") != 2 or kinds.count("missing") != 4:
        bad.append(f"the card marks {kinds.count('have')} pieces worn and {kinds.count('missing')} missing; want 2 and 4")
    if kinds.count("active") != 1 or kinds.count("inactive") != 2:
        bad.append("the card does not light exactly the one earned bonus")
    if ("(2) Set: +20 Strength", "active") not in lines:
        bad.append(f"the two-piece line reads wrongly: {[t for t, k in lines if k == 'active']}")
    if not any(t == "(6) Set: +30 Stamina, said by hand" for t, _k in lines):
        bad.append("an authored bonus text was not used")
    if GS.tooltip_lines(Item("x", "Plain", "head", 60, "rare"), c):
        bad.append("an item in no set shows a set block")
    src = Path("ui/screens/inventory_screen.py").read_text(encoding="utf-8")
    if "tooltip_lines(item, self._get_subject())" not in src:
        bad.append("the inventory's item card does not draw the set block")

    # 8. one set, a version per spec - each version counted on its own
    H = "qa_hybrid_set"
    GS.register(H, {"name": "Test Harness", "class": "Shaman", "variants": {
        "enh": {"label": "Enhancement",
                "pieces": {s: {"name": f"Enh {s}", "primary_stats": {"strength": 10}} for s in SLOTS},
                "bonuses": {"2": {"stats": {"attack_power": 30}}, "4": {"stats": {"stamina": 15}}}},
        "ele": {"label": "Elemental",
                "pieces": {s: {"name": f"Ele {s}", "primary_stats": {"intellect": 10}} for s in SLOTS},
                "bonuses": {"2": {"stats": {"spell_power": 30}}, "4": {"stats": {"spirit": 15}}}}}})

    def hybrid(slot, variant):
        it = Item(f"qa_h_{slot}", "raw", slot, 60, "rare", armor_type="mail", set_id=H)
        GS.exchange(it, variant)
        return it

    def dress(ch, layout):
        for s in SLOTS:
            ch.equipment.slots[s] = None
        for slot, variant in layout.items():
            ch.equipment.slots[slot] = hybrid(slot, variant)
        ch._recalculate_derived_stats()

    sh = make("Shaman")
    # Kyle's own example, scaled to six slots: 4 Enhancement + 2 Elemental
    dress(sh, {"head": "enh", "shoulder": "enh", "chest": "enh", "hands": "enh", "legs": "ele", "feet": "ele"})
    if GS.version_counts(sh, H) != {"enh": 4, "ele": 2}:
        bad.append(f"4 Enhancement + 2 Elemental counted as {GS.version_counts(sh, H)}")
    want = {"attack_power": 30, "stamina": 15, "spell_power": 30}
    if GS.active_bonuses(sh) != want:
        bad.append(f"4 Enhancement + 2 Elemental should pay Enhancement's 2 and 4 and Elemental's 2 "
                   f"({want}); paid {GS.active_bonuses(sh)}")
    # NO MIXING: three of one and one of the other is not a four-piece anything
    dress(sh, {"head": "enh", "shoulder": "enh", "chest": "enh", "hands": "ele"})
    if GS.active_bonuses(sh) != {"attack_power": 30}:
        bad.append(f"3 Enhancement + 1 Elemental should pay only Enhancement's 2-piece; paid "
                   f"{GS.active_bonuses(sh)} - versions are being mixed")
    it = sh.equipment.slots["head"]
    if (it.name, it.set_variant, it.primary_stats) != ("Enh head", "enh", {"strength": 10}):
        bad.append(f"an Enhancement piece is {it.name} / {it.set_variant} / {it.primary_stats}")
    if [k for k, _l, _n in GS.exchange_options(it)] != ["ele"]:
        bad.append("an Enhancement piece does not offer exactly the Elemental exchange")
    lvl, rar, slot = it.item_level, it.rarity, it.slot
    if not GS.exchange(it, "ele") or (it.name, it.set_variant, it.primary_stats) != ("Ele head", "ele", {"intellect": 10}):
        bad.append("exchanging to Elemental did not change the name, version and stats")
    if (it.item_level, it.rarity, it.slot, it.set_id) != (lvl, rar, slot, H):
        bad.append("an exchange changed the piece's level, rarity, slot or set")
    if GS.exchange(it, "ele") or GS.exchange(it, "no_such_spec"):
        bad.append("an exchange to the same version, or to one the set does not have, 'succeeded'")
    sh._recalculate_derived_stats()
    # now 2 Enhancement (shoulder, chest) + 2 Elemental (head, hands)
    if GS.active_bonuses(sh) != {"attack_power": 30, "spell_power": 30}:
        bad.append(f"after exchanging the helm, 2 + 2 should pay both 2-piece bonuses; paid {GS.active_bonuses(sh)}")
    back2 = Item.from_dict(it.to_dict())
    if back2.set_variant != "ele" or back2.name != "Ele head":
        bad.append("an exchanged piece did not survive a save as the version it was exchanged to")
    card = GS.tooltip_lines(it, sh)
    if not card or card[0][0] != "Test Harness - Elemental (2/6)":
        bad.append(f"the card heading for an Elemental piece with 2 Elemental worn reads {card[:1]}")
    if [k for _t, k in card].count("active") != 1:
        bad.append("the card for a 2-piece version does not light exactly its 2-piece bonus")
    if not any(t.startswith("Exchange for: Enh head (Enhancement)") for t, _k in card):
        bad.append("the card does not say what the piece can be exchanged for")

    # the exchange itself: free, at the capitals, Freewind Post and Booty Bay
    from entities.party import Party
    party = Party(sh)
    spare = hybrid("legs", "enh")
    sh.inventory.append(spare)
    offers = GS.exchangeable(party)
    if len(offers) != 5 or not any(o[1] is spare and o[2] == "in bags" for o in offers):
        bad.append(f"the exchange should offer the 4 worn pieces and the 1 in the bags; it offers {len(offers)}")
    sh.inventory.remove(spare)
    import json
    services = json.load(open("data/travel/travel_data.json", encoding="utf-8"))["services"]
    # ...by an Artifact Keeper - a person of their own, not the innkeeper or the banker
    keepers = {"ak_org": "Orgrimmar", "ak_uc": "Undercity", "ak_kb": "Kael's Bastion",
               "ak_freewind": "Freewind Post", "ak_bootybay": "Booty Bay"}
    people = {n["npc_id"]: n for n in json.load(open("data/npcs/ambient_npcs.json", encoding="utf-8"))["npcs"]}
    for npc, place in keepers.items():
        if services.get(npc) != ["set_exchange"]:
            bad.append(f"the Artifact Keeper in {place} does not offer the set exchange (and only that)")
        if npc not in people or not people[npc]["name"].startswith("Artifact Keeper "):
            bad.append(f"there is no Artifact Keeper standing in {place}")
    offering = sorted(n for n, v in services.items() if "set_exchange" in v)
    if offering != sorted(keepers):
        bad.append(f"the set exchange is offered by {offering}; it should be the five Keepers and nobody else")
    spots = [(people[k]["zone"], people[k]["x"], people[k]["y"]) for k in keepers if k in people]
    taken = [(n["zone"], n["x"], n["y"]) for n in people.values() if n["npc_id"] not in keepers]
    if any(s in taken for s in spots):
        bad.append("an Artifact Keeper is standing on somebody else's tile")
    svc = Path("ui/screens/travel_service_screen.py").read_text(encoding="utf-8")
    if 'self.kind == "set_exchange"' not in svc or "price=None, label=\"Exchange\"" not in svc:
        bad.append("the service screen has no free set-exchange list")
    if '"set_exchange": "Exchange Set Gear"' not in Path("ui/screens/quest_dialog_screen.py").read_text(encoding="utf-8"):
        bad.append("the NPC dialog has no Exchange Set Gear button")
    GS.all_sets().pop(H, None)

    # 7. shipped sets
    GS.all_sets().pop(TEST, None)
    import glob
    classes = {os.path.basename(p)[:-5] for p in glob.glob("data/abilities/*.json")
               if not os.path.basename(p).startswith("_") and "asher" not in p}
    shipped = GS.all_sets()
    proven = {}                      # a bonus dict that has been shown to move a sheet
    pieces_total = 0
    for sid, d in shipped.items():
        cls = str(d.get("class", "")).lower().replace(" ", "_")
        if cls not in classes:
            bad.append(f"{sid}: class {d.get('class')!r} does not exist")
        kinds = GS.variants(d) or {None: d}
        frames = d.get("slots") or {}
        names_by_slot, totals_by_slot = {}, {}
        for key, v in kinds.items():
            pieces = v.get("pieces") or {}
            for slot, spec in pieces.items():
                pieces_total += 1
                if slot not in EQUIPMENT_SLOTS:
                    bad.append(f"{sid}: '{slot}' is not an equipment slot")
                if isinstance(spec, dict):
                    names_by_slot.setdefault(slot, []).append(spec["name"])
                    totals_by_slot.setdefault(slot, set()).add(sum(spec["primary_stats"].values()))
                    it = GS.make_piece(sid, slot, key)
                    if it is None or it.set_variant != key or it.name != spec["name"]:
                        bad.append(f"{sid}/{key}: make_piece does not make the {slot}")
                    elif it.required_level != frames[slot]["required_level"]:
                        bad.append(f"{sid}: {it.name} requires level {it.required_level}, the set says "
                                   f"{frames[slot]['required_level']}")
            for need, bonus in GS.bonuses_for(d, key):
                if need > len(pieces):
                    bad.append(f"{sid}/{key}: a {need}-piece bonus on a set of {len(pieces)}")
                sig = (d.get("class"), json.dumps(bonus.get("stats"), sort_keys=True))
                if sig not in proven:
                    probe = make(d.get("class", "Warrior"))
                    before = {k: v for k, v in vars(probe).items() if isinstance(v, (int, float))}
                    GS.register("_probe", {"pieces": {"head": "p"}, "bonuses": {"1": bonus}})
                    probe.equipment.slots["head"] = piece("head", "_probe")
                    probe._recalculate_derived_stats()
                    after = vars(probe)
                    proven[sig] = sorted(k for k, v in before.items() if after.get(k) != v)
                    GS.all_sets().pop("_probe", None)
                moved = proven[sig]
                for stat in (bonus.get("stats") or {}):
                    want = {"spirit": "effective_spirit", "stamina": "effective_stamina", "strength": "effective_strength",
                            "agility": "effective_agility", "intellect": "effective_intellect"}.get(stat, stat)
                    if want not in moved:
                        bad.append(f"{sid}/{key}: the {need}-piece bonus says +{stat} and {want} does not "
                                   f"move on a {d.get('class')} (moved: {moved[:6]})")
        for slot, names in names_by_slot.items():
            if len(set(names)) != len(names):
                bad.append(f"{sid}: two versions share a {slot} name: {names}")
        for slot, totals in totals_by_slot.items():
            if len(totals) != 1:
                bad.append(f"{sid}: the {slot} is worth {sorted(totals)} primary points depending on "
                           f"version - an exchange must never be an upgrade")

    # THE T0 SETS: every class has one, eight pieces, levels 53-59
    t0 = {d["class"]: (sid, d) for sid, d in shipped.items() if d.get("tier") == "T0"}
    missing = sorted(c for c in classes if c.replace("_", " ").title() not in {k.title() for k in t0})
    if missing:
        bad.append(f"no T0 set for: {missing}")
    for cls, (sid, d) in t0.items():
        reqs = sorted(f["required_level"] for f in d["slots"].values())
        # Kyle, 13 Nov 2026: "The T0 item set will be from lvl 53 to lvl 59 (So ilvl 56 to ilvl 62)".
        # One level later than Classic's 52-58, and item level THREE above the required level.
        if reqs != [53, 54, 55, 55, 56, 57, 58, 59]:
            bad.append(f"{sid}: required levels are {reqs}; T0 is 53,54,55,55,56,57,58,59")
        off = {f["item_level"] - f["required_level"] for f in d["slots"].values()}
        if off != {3}:
            bad.append(f"{sid}: item level sits {sorted(off)} above the required level; T0 is three above")
        for key, v in d["variants"].items():
            if len(v["pieces"]) != 8:
                bad.append(f"{sid}/{key}: {len(v['pieces'])} pieces, T0 is eight")
            if sorted(v["bonuses"]) != ["2", "4"]:
                bad.append(f"{sid}/{key}: bonuses at {sorted(v['bonuses'])}; 2 and 4 are designed, 6 and 8 are not yet")
            two = v["bonuses"]["2"]["stats"]
            if sum(two.values()) != 30:
                bad.append(f"{sid}/{key}: the 2-piece bonus totals {sum(two.values())}, Kyle said +30")
            four = set(v["bonuses"]["4"]["stats"])
            if not four <= {"attack_power", "ranged_attack_power", "spell_power", "healing_power"}:
                bad.append(f"{sid}/{key}: the 4-piece bonus is {sorted(four)}; it is power of one kind or two")
    if t0:
        if "cryotherapist" not in t0["Mage"][1]["variants"]:
            bad.append("the Mage set has no Cryotherapist version (Kyle's home-brew DPS healer)")
        if t0["Mage"][1]["variants"].get("cryotherapist", {}).get("label") != "Cryotherapist":
            bad.append("the Mage healer version is not labelled Cryotherapist")
        if "enhancement_tank" not in t0["Shaman"][1]["variants"]:
            bad.append("the Shaman set has no Enhancement Tank version (Kyle's home-brew)")
        if len(t0["Necromancer"][1]["variants"]) != 1:
            bad.append("the Necromancer set has more than one version - every tree is dps")
        ret = [v for v in t0["Paladin"][1]["variants"].values() if "Retribution" in v["label"]]
        if not ret or set(ret[0]["bonuses"]["4"]["stats"]) != {"attack_power", "spell_power"}:
            bad.append("Retribution's 4-piece is not attack power AND spell power")
        # Kyle's example, on the real set
        sham = make("Shaman")
        sid = t0["Shaman"][0]
        for s in EQUIPMENT_SLOTS:
            sham.equipment.slots[s] = None
        sham._recalculate_derived_stats()
        ap0, sp0, agi0, int0 = sham.attack_power, sham.spell_power, sham.effective_agility, sham.effective_intellect
        order = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet"]
        for s in order[:5]:
            sham.equipment.slots[s] = GS.make_piece(sid, s, "melee")
        for s in order[5:]:
            sham.equipment.slots[s] = GS.make_piece(sid, s, "caster")
        sham._recalculate_derived_stats()
        if GS.active_bonuses(sham) != {"agility": 30, "attack_power": 40, "intellect": 30}:
            bad.append(f"a Shaman in 5 Enhancement + 3 Elemental should have Enhancement's 2 and 4 and "
                       f"Elemental's 2; has {GS.active_bonuses(sham)}")
        # the generator and the data file agree
        import subprocess
        fresh = subprocess.run([sys.executable, "tools/build_t0_sets.py", "--dry-run"],
                               capture_output=True, text=True).stdout
        if f"{len(t0)} sets" not in fresh:
            bad.append("tools/build_t0_sets.py no longer builds the sets that are in the data file")

    print(f"{len(shipped)} sets shipped ({sum(len(GS.variants(d)) for d in shipped.values())} versions, "
          f"{pieces_total} pieces); engine checked on a six-piece test set")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\ngear sets OK - bonuses arrive at their piece count, stack up the ladder, leave with "
          "the piece, are worth what gear is, survive a save, and are listed on the card.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
