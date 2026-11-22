#!/usr/bin/env python3
"""The speed pass: every class's spells quick, normal or slow, sized for it, and checked.

    PYTHONPATH=. python3 tools/build_cast_speeds.py            # show what would change
    PYTHONPATH=. python3 tools/build_cast_speeds.py --apply    # write it into data/abilities
    PYTHONPATH=. python3 tools/build_cast_speeds.py --check    # the QA: fail if any class is missing a speed

Kyle, 20 Nov 2026, for the turn timeline (docs/turn_timeline_design.md): hovering Earth Shock barely moves the shaman,
Lesser Healing Wave lands him between the enemies, Greater Healing Wave pushes him to last. For that to mean something
in every class, every kit needs quick, normal and slow spells. Only seven classes had any (tools/apply_cast_speeds.py,
15 Nov, from Classic's cast times); this does the rest, and tags everything else "normal" so every castable ability
says what it is.

THE RULE, the same for every class, with each class's own exceptions in OVERRIDES:
  - Free actions (instant with a cooldown of 2 or more) and the basic attack never use up the turn, so they're left
    as they are.
  - SLOW: the big, deliberate casts. Names that say so (Greater, Aimed, Pyroblast, Tranquility, a summoning, a
    channel, a resurrection), then the class's biggest no-or-short-cooldown hit and its biggest heal.
  - QUICK: the snap actions. Names that say so (Shock, Flash, Lesser, Jab, Lance, Throw, Sting), interrupts and
    taunts, then the class's smallest hit and smallest heal.
  - Every class ends with at least two quick and one slow, and no more than about a third quick or a fifth slow.

SIZING, the 15 Nov rule, so a speed never makes a spell better or worse per turn of time: a slow spell is 1.5x for
1.15x the cost; a quick one 0.65x for 0.85x the cost. Only damage, healing and absorbs are sized; a slow summoning or
a quick taunt just costs the time. Idempotent: anything already tagged is left alone.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "abilities"
SIZE = {"slow": (1.5, 1.15), "quick": (0.65, 0.85)}
SIZED_TYPES = {"damage", "spell_damage", "ranged_damage", "heal", "damage_and_heal", "dot", "spell_dot", "hot",
               "absorb", "shield"}
HIT_TYPES = {"damage", "spell_damage", "ranged_damage", "damage_and_heal", "dot", "spell_dot"}
HEAL_TYPES = {"heal", "hot"}
SLOW_WORDS = re.compile(
    r"\b(greater|aimed|pyroblast|starfire|chaos bolt|soul fire|meteor|cataclysm|tranquility|rebirth|resurrect\w*|"
    r"revive|redemption|channel\w*|drain|blizzard|rain of|hurricane|requiem|apocalypse|armageddon|supernova|comet|"
    r"summon\w*|ritual|incantation|hymn|mass|grand|obliterat\w*|annihilat\w*)\b", re.I)
QUICK_WORDS = re.compile(
    r"\b(shock|flash|lesser|quick|swift|jab|lance|dart|flick|snap|spark|zap|sting|nip|kick|pummel|counter\w*|"
    r"rebuke|interrupt|taunt|throw|toss|lunge|renew|shiv|prick)\b", re.I)
SLOW_TYPES = {"revive", "summon_pet"}

#: per-class exceptions after reading the result: ability_id -> speed ("normal" to undo a rule's pick)
OVERRIDES = {
    # Chaos Bolt is the warlock's big slow cast, every summoning takes the time, and Drain Life is a channel
    "warlock": {"warlock_shadowburn": "quick", "warlock_chaos_bolt": "slow", "warlock_summon_imp": "slow", "warlock_summon_voidwalker": "slow",
                "warlock_summon_succubus": "slow", "warlock_summon_felhunter": "slow", "warlock_drain_life": "slow"},
    # the heavy blow is the slow one, the finisher the quick one; a bleed is a normal swing
    "warrior": {"warrior_rend": "normal", "warrior_mortal_strike": "slow", "warrior_execute": "quick"},
    # Ambush is the wind-up; Rupture is an ordinary finisher
    "rogue": {"rogue_rupture": "normal", "rogue_ambush": "slow"},
}


def castable(e):
    if e["ability_id"].endswith("_attack"):
        return False
    return not (e.get("is_instant") and (e.get("cooldown") or 0) >= 2)


def top(e):
    return (e.get("ranks") or [{}])[-1]


def picks_for(cls, abilities):
    """{ability_id: speed} for this class's untagged castable abilities."""
    pool = [e for e in abilities if castable(e)]
    out = {e["ability_id"]: e["cast_speed"] for e in pool if e.get("cast_speed")}
    free = [e for e in pool if not e.get("cast_speed")]
    n = len(pool)
    cap_q, cap_s = max(2, round(n * 0.33)), max(1, round(n * 0.2))
    count = lambda sp: sum(1 for v in out.values() if v == sp)  # noqa: E731

    def take(e, sp):
        if e["ability_id"] not in out and count(sp) < (cap_q if sp == "quick" else cap_s):
            out[e["ability_id"]] = sp

    # words and kinds first (small things first for quick, big things first for slow, so a cap keeps the right ones)
    by_val = sorted(free, key=lambda e: top(e).get("effect_value") or 0)
    for e in reversed(by_val):
        if SLOW_WORDS.search(e["name"]) or e.get("effect_type") in SLOW_TYPES:
            take(e, "slow")
    for e in by_val:
        if QUICK_WORDS.search(e["name"]) or e.get("taunt") or e.get("interrupt") or e.get("interrupts"):
            take(e, "quick")
    # then the class's own extremes: biggest and smallest repeatable hit and heal
    short = [e for e in free if (e.get("cooldown") or 0) <= 3 and e["ability_id"] not in out
             and (top(e).get("effect_value") or 0) > 0]
    hits = sorted([e for e in short if e.get("effect_type") in HIT_TYPES], key=lambda e: top(e)["effect_value"])
    heals = sorted([e for e in short if e.get("effect_type") in HEAL_TYPES], key=lambda e: top(e)["effect_value"])
    if len(heals) >= 2 and not any(out.get(e["ability_id"]) == "slow" for e in abilities
                                    if e.get("effect_type") in HEAL_TYPES):
        take(heals[-1], "slow")
    if len(heals) >= 2 and not any(out.get(e["ability_id"]) == "quick" for e in abilities
                                    if e.get("effect_type") in HEAL_TYPES):
        take(heals[0], "quick")
    for e in reversed(hits):
        if count("slow") >= 1 or len(hits) < 2:
            break
        take(e, "slow")
    for e in hits:
        if count("quick") >= 2:
            break
        if out.get(e["ability_id"]) is None:
            take(e, "quick")
    for e in pool:
        out.setdefault(e["ability_id"], "normal")
    out.update({k: v for k, v in OVERRIDES.get(cls, {}).items() if k in out})
    return out


def size(e, speed):
    mult, cmult = SIZE[speed]
    if e.get("effect_type") not in SIZED_TYPES:
        return False
    for r in e.get("ranks", []):
        if r.get("effect_value"):
            r["effect_value"] = max(1, round(r["effect_value"] * mult))
        if r.get("cost"):
            r["cost"] = max(1, round(r["cost"] * cmult))
    return True


def check():
    problems = []
    for path in sorted(DIR.glob("*.json")):
        cls = path.stem
        if cls.startswith("_") or cls == "asher_unique":
            continue
        abilities = json.loads(path.read_text(encoding="utf-8"))["abilities"]
        pool = [e for e in abilities if castable(e)]
        untagged = [e["ability_id"] for e in pool if not e.get("cast_speed")]
        if untagged:
            problems.append(f"{cls}: {len(untagged)} castable abilities have no speed (e.g. {untagged[0]})")
        speeds = [e.get("cast_speed") for e in pool]
        if speeds.count("quick") < 2 or speeds.count("slow") < 1:
            problems.append(f"{cls}: {speeds.count('quick')} quick and {speeds.count('slow')} slow "
                            f"(needs at least 2 and 1)")
        for e in pool:
            if e.get("cast_speed") not in (None, "quick", "normal", "slow"):
                problems.append(f"{cls}: {e['ability_id']} has speed {e.get('cast_speed')!r}")
    for p in problems:
        print("  -", p)
    print(f"cast speeds: {'OK' if not problems else str(len(problems)) + ' problems'}")
    return 1 if problems else 0


def main():
    if "--check" in sys.argv:
        return check()
    apply = "--apply" in sys.argv
    totals = {"quick": 0, "normal": 0, "slow": 0}
    for path in sorted(DIR.glob("*.json")):
        cls = path.stem
        if cls.startswith("_") or cls == "asher_unique":
            continue
        doc = json.loads(path.read_text(encoding="utf-8"))
        picks = picks_for(cls, doc["abilities"])
        shown = {"quick": [], "slow": []}
        for e in doc["abilities"]:
            sp = picks.get(e["ability_id"])
            # an override can still turn a plain "normal" into quick or slow on a later run; nothing else is re-tagged
            retag = e.get("cast_speed") == "normal" and OVERRIDES.get(cls, {}).get(e["ability_id"]) in SIZE
            if not sp or (e.get("cast_speed") and not retag):
                continue
            if retag:
                totals["normal"] -= 1
            e["cast_speed"] = sp
            totals[sp] += 1
            if sp != "normal":
                sized = size(e, sp)
                mult, cmult = SIZE[sp]
                e.setdefault("_tuning", []).append(
                    f"21 Nov 2026: a {sp} cast for the turn timeline (tools/build_cast_speeds.py)"
                    + (f", sized {mult}x for {cmult}x the cost" if sized else ""))
                shown[sp].append(e["name"])
        print(f"{cls:16} quick: {', '.join(shown['quick']) or '-'}")
        print(f"{'':16} slow:  {', '.join(shown['slow']) or '-'}")
        if apply:
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{totals} {'written' if apply else 'would be written'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
