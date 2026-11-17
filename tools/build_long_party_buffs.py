#!/usr/bin/env python3
"""Every class brings a long party buff, and mana buffs give real mp5. Idempotent.

    PYTHONPATH=. python3 tools/build_long_party_buffs.py [--check]

Kyle, 17 Nov 2026, on the support pass's two open questions:
  - the classes with no long (thirty-minute) party buff: "Each gets one"
  - mana regeneration buffs: "Real mp5, sized by level", and every healer class gets at least one way to give mana

THE EIGHT. Each gets a long buff on the party whose stat is sized by combat/support_formula.py (a share of what a
geared character of the rank's level has) and ranked every ten levels by tools/regrade_buff_ranks.py:

  Warrior        Commanding Shout      Stamina         (a NEW shout: Battle Shout stays the in-fight one, and Booming
                                                        Voice still lengthens it)
  Hunter         Trueshot Aura         attack power
  Rogue          Cutthroat's Edge      Agility
  Warlock        Demonic Pact          spell power
  Felsworn       Felbrand              Strength        (NEW: Fel Infusion stays the in-fight crit aura that Infernal's
                                                        Fel Infusion talent shortens)
  Templar        Templar's Oath        Stamina and armour
  Witch Doctor   Spirit Fetish         Spirit and mp5
  Witch Hunter   Hunter's Ward         Shadow resistance (on the 0-60 scale, like the resistance totems)

THE MANA BUFFS. mp5 is now sized like the other stats (combat/support_formula.py: a long buff's mp5 gives back about
what a geared caster's Spirit does on a turn they cast). The three that gave "maximum mana" become mp5:
Blessing of Wisdom, Mana Spring Totem and Water Shield. The healer classes that gave the party no mana get a way to:

  Priest         Divine Spirit          Spirit (new)
  Chronomancer   Borrowed Moments       mp5 (new)
  Starcaller     Moonwell's Blessing    mp5 (new)
  Cultist        Whispers of C'thun     + mp5
  Pyromancer     Inner Flame            + mp5

Two long self buffs had an authored mp5 bigger than the formula's at every rank, so they gave the same 18 (Aspect
of the Moonwell) and 15 (Vow of Grace) from level 6 to 60; their authored value is now 4 and the formula sizes them by
rank (done once by hand, 17 Nov 2026; tools/qa_long_party_buffs.py holds it).

(Druid's Mark of the Wild carries Spirit, Mage's Arcane Intellect Intellect; the rest already had one.)
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

NOTE = "17 Nov 2026: every class brings a long party buff, mana buffs give mp5 (tools/build_long_party_buffs.py)"


def long_buff(aid, name, resource, level, cost, stat_mods, desc):
    return {
        "ability_id": aid, "name": name, "resource_type": resource, "cooldown": 0, "effect_type": "buff",
        "duration": 0, "stat_mods": stat_mods, "description": desc, "target_type": "party", "icon_id": None,
        "buff_scope": "raid",
        "ranks": [{"rank": 1, "level_req": level, "cost": cost, "effect_value": 33}],
        "_tuning": [NOTE],
    }


#: class file -> new abilities
NEW = {
    "warrior": [long_buff("warrior_commanding_shout", "Commanding Shout", "rage", 20, 0, {"stamina": 3},
                          "A shout that steadies your party: increases their Stamina for thirty minutes.")],
    "hunter": [long_buff("hunter_trueshot_aura", "Trueshot Aura", "mana", 20, 40, {"attack_power": 30},
                         "Increases your party's attack power for thirty minutes.")],
    "rogue": [long_buff("rogue_cutthroats_edge", "Cutthroat's Edge", "energy", 20, 0, {"agility": 3},
                        "Tricks of the trade, passed round: increases your party's Agility for thirty minutes.")],
    "warlock": [long_buff("warlock_demonic_pact", "Demonic Pact", "mana", 20, 45, {"spell_power": 25},
                          "Shares your demon's power with your party: increases their spell power for thirty "
                          "minutes.")],
    "felsworn": [long_buff("felsworn_felbrand", "Felbrand", "felfury", 20, 0, {"strength": 3},
                           "Brands your party with fel: increases their Strength for thirty minutes.")],
    "templar": [long_buff("templar_templars_oath", "Templar's Oath", "combo", 20, 0, {"stamina": 3, "armor": 60},
                          "Your party swears the oath with you: increases their Stamina and armor for thirty "
                          "minutes.")],
    "witch_doctor": [long_buff("witch_doctor_spirit_fetish", "Spirit Fetish", "mana", 20, 40,
                               {"spirit": 3, "mp5": 4},
                               "Hangs a fetish on your party: increases their Spirit and mana per turn for thirty "
                               "minutes.")],
    "witch_hunter": [long_buff("witch_hunter_hunters_ward", "Hunter's Ward", "focus", 20, 0,
                               {"shadow_resistance": 12},
                               "Wards your party against dark magic: increases their Shadow Resistance for thirty "
                               "minutes.")],
    "priest": [long_buff("priest_divine_spirit", "Divine Spirit", "mana", 30, 60, {"spirit": 3},
                         "Increases your party's Spirit for thirty minutes.")],
    "chronomancer": [long_buff("chronomancer_borrowed_moments", "Borrowed Moments", "mana", 20, 40, {"mp5": 4},
                               "Lends your party moments from later: increases their mana per turn for thirty "
                               "minutes.")],
    "starcaller": [long_buff("starcaller_moonwells_blessing", "Moonwell's Blessing", "mana", 20, 40, {"mp5": 4},
                             "The moonwell's water, carried with you: increases your party's mana per turn for "
                             "thirty minutes.")],
}

#: (class file, ability name) -> stat_mods changes: None removes a key
CHANGE = {
    ("paladin", "Blessing of Wisdom"): ({"max_mana_pct": None, "mp5": 4},
                                        "Increases your party's mana per turn for thirty minutes."),
    ("shaman", "Mana Spring Totem"): ({"max_mana_pct": None, "mp5": 4},
                                      "A totem that increases your party's mana per turn."),
    ("shaman", "Water Shield"): ({"max_mana_pct": None, "mp5": 4}, None),
    ("cultist", "Whispers of C'thun"): ({"mp5": 3}, None),
    ("pyromancer", "Inner Flame"): ({"mp5": 3}, None),
}

#: spellbook tabs for the new ones (the classic nine: ui/spellbook_tree_map.py; the rest: spellbook_tabs_coa.json)
TABS = {
    "warrior_commanding_shout": "warrior_fury",
    "hunter_trueshot_aura": "hunter_marksmanship",
    "warlock_demonic_pact": "warlock_demonology",
    "priest_divine_spirit": "priest_discipline",
}


def rows_of(d):
    rows = d.get("abilities", d) if isinstance(d, dict) else d
    return rows if isinstance(rows, list) else list(rows.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    from tools.regrade_buff_ranks import regrade, ladder

    def ranked(a):
        """regrade() only ranks buffs with a sized stat; a resistance buff gets the same ladder, its value carried
        by effect_value 100% -> 184%, the resistance totems' own (Frost Resistance Totem: 12 at 20, 22 at 56)."""
        new = regrade(a)
        if new:
            return new
        first = a["ranks"][0]
        lv = ladder(first["level_req"])
        return [dict(first, rank=i + 1, level_req=v,
                     effect_value=int(round(100 + 84 * i / max(1, len(lv) - 1)))) for i, v in enumerate(lv)]
    done = []
    files = sorted(set(NEW) | {c for c, _n in CHANGE})
    for cls in files:
        fn = ROOT / f"data/abilities/{cls}.json"
        d = json.loads(fn.read_text(encoding="utf-8"))
        rows = rows_of(d)
        if not isinstance(d.get("abilities", d), list):
            raise SystemExit(f"{fn.name}: abilities is not a list, this tool would need teaching")
        have = {a.get("ability_id") for a in rows if isinstance(a, dict)}
        changed = False
        for a in NEW.get(cls, []):
            if a["ability_id"] in have:
                continue
            a["ranks"] = ranked(a)
            rows.append(a)
            changed = True
            done.append(f"+ {cls}: {a['name']} ({', '.join(a['stat_mods'])}; ranks at "
                        f"{', '.join(str(r['level_req']) for r in a['ranks'])})")
        for (c, name), (mods, desc) in CHANGE.items():
            if c != cls:
                continue
            a = next((x for x in rows if isinstance(x, dict) and x.get("name") == name), None)
            if a is None:
                raise SystemExit(f"{cls}: no ability named {name}")
            sm = dict(a.get("stat_mods") or {})
            want = dict(sm)
            for k, v in mods.items():
                if v is None:
                    want.pop(k, None)
                else:
                    want.setdefault(k, v)
            if want == sm and (desc is None or a.get("description") == desc):
                continue
            a["stat_mods"] = want
            if desc:
                a["description"] = desc
            if a.get("buff_scope") not in ("combat",):
                new = regrade(a)
                if new:
                    a["ranks"] = new
            t = a.setdefault("_tuning", [])
            if NOTE not in t:
                t.append(NOTE)
            changed = True
            done.append(f"~ {cls}: {name} {sm} -> {want}")
        if changed and not args.check:
            fn.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for line in done:
        print("  " + line)
    print(f"{len(done)} change(s){' (check only)' if args.check else ''}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
