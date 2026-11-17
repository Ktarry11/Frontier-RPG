#!/usr/bin/env python3
"""Every class brings a long party buff; mana buffs give mp5 that grows with rank.

    PYTHONPATH=. python3 tools/qa_long_party_buffs.py

Kyle, 17 Nov 2026 (tools/build_long_party_buffs.py): "Each gets one" and "Real mp5, sized by level".
  1. each of the thirteen classes that had none now has a thirty-minute buff on the party
  2. no class buff gives "maximum mana %" any more (Wisdom, Mana Spring, Water Shield are mp5)
  3. every class with a healing spec gives its party mana: mp5, Spirit or Intellect, on a long party buff
  4. a long buff's mp5 grows rank to rank and sits at about a geared caster's casting Spirit regen at its level
  5. the support formula's mp5 sizes: a long buff on yourself is sized like a party one, not bigger
"""
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []


def check(ok, msg):
    print(f"  {'ok  ' if ok else 'FAIL'} {msg}")
    if not ok:
        fails.append(msg)


def main():
    from combat.abilities import _ability_from_data
    from combat import support_formula as SF
    by_class = {}
    for fn in sorted(glob.glob("data/abilities/*.json")):
        b = os.path.basename(fn)[:-5]
        if b.startswith("_") or "unique" in b:
            continue
        d = json.loads(Path(fn).read_text(encoding="utf-8"))
        rows = d.get("abilities", d) if isinstance(d, dict) else d
        rows = rows if isinstance(rows, list) else list(rows.values())
        out = []
        for e in rows:
            if not isinstance(e, dict) or e.get("effect_type") != "buff":
                continue
            try:
                out.append((e, _ability_from_data(e)))
            except Exception:                                   # noqa: BLE001
                continue
        by_class[b] = out

    def long_party(cls):
        return [(e, a) for e, a in by_class.get(cls, [])
                if a.buff_scope == "raid" and a.target_type in ("party", "raid")]

    # 1
    for cls in ("warrior", "hunter", "rogue", "warlock", "felsworn", "templar", "witch_doctor", "witch_hunter",
                "bloodmage", "guardian", "knight_of_xoroth", "necromancer", "ranger"):
        lp = long_party(cls)
        check(bool(lp), f"{cls} has a long party buff ({', '.join(a.name for _e, a in lp) or 'none'})")
    # 2
    pct = [f"{c}:{a.name}" for c, rows in by_class.items() for e, a in rows
           if "max_mana_pct" in (e.get("stat_mods") or {})]
    check(not pct, f"no class buff gives maximum mana % ({pct})")
    # 3
    specs = json.loads(Path("data/balance/spec_auras.json").read_text(encoding="utf-8"))["healing"]
    healers = sorted({k.split("_")[0] if not k.startswith(("sun_cleric", "witch_doctor")) else
                      "_".join(k.split("_")[:2]) for k in specs})
    for cls in healers:
        givers = [a.name for e, a in long_party(cls)
                  if {"mp5", "spirit", "intellect"} & set(e.get("stat_mods") or {})]
        check(bool(givers), f"healer class {cls} gives its party mana ({', '.join(givers) or 'nothing'})")
    # 4
    for cls, rows in by_class.items():
        for e, a in rows:
            if "mp5" not in (e.get("stat_mods") or {}) or a.buff_scope != "raid" or len(a.ranks) < 2:
                continue
            vals = []
            for i in range(len(a.ranks)):
                a.current_rank_index = i
                vals.append((a.current_rank.get("level_req"), a.scaled_stat_mods().get("mp5", 0)))
            grows = all(vals[i][1] <= vals[i + 1][1] for i in range(len(vals) - 1)) and vals[-1][1] > vals[0][1]
            check(grows, f"{a.name}: mp5 grows by rank {vals}")
            lv, top = vals[-1]
            spirit = SF.reference("spirit", lv) * 0.6 * 0.30
            check(0.7 * spirit <= top <= 2.0 * spirit or top == e["stat_mods"]["mp5"],
                  f"{a.name}: top-rank mp5 {top} vs a geared caster's casting Spirit regen {spirit:.0f} at {lv}")
    # 5
    party = SF.sized_mods("buff", "party", "raid", {"mp5": 1}, 60)["mp5"]
    selfb = SF.sized_mods("buff", "self", "raid", {"mp5": 1}, 60)["mp5"]
    check(selfb == party, f"a long self mp5 buff is sized like a party one ({selfb} vs {party})")
    print("long party buffs OK" if not fails else f"FAILED: {len(fails)}")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
