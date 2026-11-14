#!/usr/bin/env python3
"""Give single-rank class abilities a real rank progression (Kyle, 2026-10-24: "a lot of skills lack any meaningful rank
progression and we don't get the sense of power growth").

Why: 514 of 652 class abilities had ONE rank.  Multi-rank damage/heal spells climb from a median value of ~52 at level 1-9
to ~154 at level 50+, but single-rank ones sat at ~76 from level 20 to 59 and never grew.

What this does (idempotent: only touches abilities that still have exactly one rank):
  * Eligible abilities:
      - payload abilities  : damage, spell_damage, ranged_damage, dot, spell_dot, heal, hot, damage_and_heal
      - flat-stat buffs / debuffs (attack_power, spell_power, armor, strength, resistances ... scaled by effect_value)
      - proc buffs (seals, imbues, shields): numeric proc payload scaled through a per-rank "proc" override
    Left single-rank on purpose: stuns / dispels / shapeshifts / summons / pets / totem loadouts / instant-cast enablers /
    cooldown resets, and buffs whose mods are percentages, haste, crit, taunt or immunities (scaling those would break
    caps; their value is the effect, not the number).
  * Rank levels come from combat/rank_generator.py (front-loaded gaps, every rank on an even level, nothing past 60).
  * Values follow the same growth the existing multi-rank spells have:  value(level) = v0 * C(level) / C(learned),
    C(L) = 46 + 2L  (fit to the median of all existing multi-rank damage/heal values per level band).
  * Mana costs scale with the value (existing convention); rage / energy / other resources stay flat.

    python3 tools/expand_single_ranks.py            # apply
    python3 tools/expand_single_ranks.py --dry-run  # report only
"""
import glob
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from combat.rank_generator import generate_rank_levels, MAX_LEVEL  # noqa: E402

PAYLOAD_TYPES = {"damage", "spell_damage", "ranged_damage", "dot", "spell_dot", "heal", "hot", "damage_and_heal"}
AURA_TYPES = {"buff", "debuff"}
# stat_mods keys that must NOT be scaled by effect_value (percent / flag / chance style stats)
NONFLAT_EXACT = {"haste", "taunt", "cc_immune", "stunned", "silenced", "rooted", "mp5", "max_mana_pct"}
NONFLAT_PARTS = ("_pct", "crit", "dodge", "parry", "block", "hit", "resist_pct", "threat", "immune")
SKIP_IDS_SUFFIX = ("_attack",)   # basic attacks scale with gear, not rank
# Hand-authored rank tables live in their own build scripts (tools/build_shaman_imbues.py)
HANDMADE = {"shaman_rockbiter_weapon", "shaman_flametongue_weapon", "shaman_windfury_weapon", "shaman_windfury_totem"}


def curve(level):
    return 46.0 + 2.0 * level


def ranks_wanted(learned_level):
    """How many ranks the span from `learned_level` to the level cap can hold (gap tables live in rank_generator)."""
    remaining = MAX_LEVEL - max(1, learned_level)
    for need, n in ((50, 9), (42, 8), (28, 5), (20, 4), (12, 3), (8, 2)):
        if remaining >= need:
            return n
    return 1


def flat_only(stat_mods):
    for k in stat_mods:
        if k in NONFLAT_EXACT or any(p in k for p in NONFLAT_PARTS):
            return False
    return bool(stat_mods)


def scale_proc(proc, ratio):
    """Numeric payload keys of a proc scaled by `ratio` -> partial override dict (empty if nothing scalable)."""
    out = {}
    if "bonus_pct" in proc:
        out["bonus_pct"] = round(proc["bonus_pct"] * ratio, 3)
    if "heal_flat" in proc:
        out["heal_flat"] = int(round(proc["heal_flat"] * ratio))
    if "smart_heal" in proc:
        out["smart_heal"] = int(round(proc["smart_heal"] * ratio))
    if isinstance(proc.get("grant_resource"), dict) and "amount" in proc["grant_resource"]:
        g = dict(proc["grant_resource"])
        g["amount"] = int(round(g["amount"] * ratio))
        out["grant_resource"] = g
    if isinstance(proc.get("on_judgement"), dict) and "damage" in proc["on_judgement"]:
        j = dict(proc["on_judgement"])
        j["damage"] = int(round(j["damage"] * ratio))
        out["on_judgement"] = j
    return out


def classify(a):
    """-> kind string if this ability should get ranks, else None."""
    if len(a.get("ranks", [])) != 1:
        return None
    if a["ability_id"].endswith(SKIP_IDS_SUFFIX) or a["ability_id"] in HANDMADE or a.get("is_stun"):
        return None
    et = a["effect_type"]
    r0 = a["ranks"][0]
    if et in PAYLOAD_TYPES:
        return "payload" if r0["effect_value"] > 0 else None
    if et in AURA_TYPES:
        if a.get("proc"):
            return "proc" if scale_proc(a["proc"], 1.0) else None
        if flat_only(a.get("stat_mods") or {}):
            return "aura"
    return None


def expand(a, kind):
    r0 = a["ranks"][0]
    l0 = r0["level_req"]
    n = ranks_wanted(l0)
    levels = generate_rank_levels(l0, n)
    if len(levels) < 2:
        return False
    mana = a.get("resource_type", "mana") == "mana"
    ranks = []
    for i, lvl in enumerate(levels):
        ratio = curve(lvl) / curve(l0)
        rk = dict(r0)
        rk["rank"] = i + 1
        rk["level_req"] = lvl
        if i:
            rk["effect_value"] = int(round(r0["effect_value"] * ratio)) if kind != "proc" else r0["effect_value"]
            if mana and r0.get("cost", 0) > 0:
                rk["cost"] = int(round(r0["cost"] * ratio))
            if "heal_value" in r0:
                rk["heal_value"] = int(round(r0["heal_value"] * ratio))
            if kind == "proc":
                rk["proc"] = scale_proc(a["proc"], ratio)
        ranks.append(rk)
    a["ranks"] = ranks
    return True


def main(dry=False):
    summary = []
    for path in sorted(glob.glob(str(ROOT / "data" / "abilities" / "*.json"))):
        if path.endswith("_universal.json") or path.endswith("asher_unique.json"):
            continue
        raw = Path(path).read_text(encoding="utf-8")
        data = json.loads(raw)
        changed = 0
        for a in data["abilities"]:
            kind = classify(a)
            if kind and expand(a, kind):
                changed += 1
                summary.append((data["class"], a["ability_id"], kind, [r["level_req"] for r in a["ranks"]]))
        if changed and not dry:
            Path(path).write_text(json.dumps(data, indent=2) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    by_class = {}
    for cls, aid, kind, lv in summary:
        by_class.setdefault(cls, []).append((aid, kind, lv))
    for cls, rows in sorted(by_class.items()):
        print(f"{cls}: {len(rows)} abilities ranked")
    print("TOTAL", len(summary), "(dry run)" if dry else "")
    return summary


if __name__ == "__main__":
    main("--dry-run" in sys.argv)
