#!/usr/bin/env python3
"""The speed pass: every class's spells instant, short, medium or long, sized for it, and checked.

    PYTHONPATH=. python3 tools/build_cast_speeds.py            # show what would change
    PYTHONPATH=. python3 tools/build_cast_speeds.py --apply    # write it into data/abilities
    PYTHONPATH=. python3 tools/build_cast_speeds.py --check    # the QA: fail if any class is missing a speed

Kyle, 20 Nov 2026, for the turn timeline (docs/turn_timeline_design.md): hovering Earth Shock barely moves the shaman,
Lesser Healing Wave lands him between the enemies, Greater Healing Wave pushes him to last. And on 21 Nov: "we have
instant, short, medium, long". So every castable ability in every class carries one of the four
(combat/abilities.CAST_SPEEDS: 0.6, 0.8, 1.0 and 1.5 of a turn).

THE RULE, the same for every class, with each class's own exceptions in OVERRIDES:
  - Free actions (instant with a cooldown of 2 or more) and the basic attack never use up the turn, so they're left
    as they are.
  - LONG: the big, deliberate casts. Names that say so (Greater, Aimed, Pyroblast, Tranquility, a summoning, a
    channel, a resurrection), then the class's biggest no-or-short-cooldown hit and its biggest heal.
  - INSTANT: the snap actions. Names that say so (Shock, Jab, Lance, Throw, Sting), interrupts and taunts, then the
    class's smallest hit.
  - SHORT: the quick casts that still take a moment. Names that say so (Flash, Lesser), the class's smallest direct
    heal, and its next smallest hit.
  - Every class ends with at least two instant, one short and one long.

SIZING, so a speed never makes a spell better or worse per turn of time: long is 1.5x for 1.15x the cost, short
0.82x for 0.92x, instant 0.65x for 0.85x. Only damage, healing and absorbs are sized; a long summoning or an instant
taunt just costs the time. Idempotent: anything already tagged is left alone.

The 21 Nov migration (run once, kept for the record): the three-speed tags became the four. Quick spells that are
Classic's 1.5-second casts (the Flash heals, Lesser Healing Wave, Mind Blast, Searing Pain, and any direct heal) became
short and were re-sized from the instant size to the short one; the rest became instant; normal became medium; slow
became long.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIR = ROOT / "data" / "abilities"
SIZE = {"long": (1.5, 1.15), "short": (0.82, 0.92), "instant": (0.65, 0.85)}
NAMES = ("instant", "short", "medium", "long")
OLD = {"quick": "instant", "normal": "medium", "slow": "long"}
SIZED_TYPES = {"damage", "spell_damage", "ranged_damage", "heal", "damage_and_heal", "dot", "spell_dot", "hot",
               "absorb", "shield"}
HIT_TYPES = {"damage", "spell_damage", "ranged_damage", "damage_and_heal", "dot", "spell_dot"}
HEAL_TYPES = {"heal", "hot"}
LONG_WORDS = re.compile(
    r"\b(greater|aimed|pyroblast|starfire|chaos bolt|soul fire|meteor|cataclysm|tranquility|rebirth|resurrect\w*|"
    r"revive|redemption|channel\w*|drain|blizzard|rain of|hurricane|requiem|apocalypse|armageddon|supernova|comet|"
    r"summon\w*|ritual|incantation|hymn|mass|grand|obliterat\w*|annihilat\w*)\b", re.I)
SHORT_WORDS = re.compile(r"\b(flash|lesser|mend|mind blast|searing pain)\b", re.I)
INSTANT_WORDS = re.compile(
    r"\b(shock|quick|swift|jab|lance|dart|flick|snap|spark|zap|sting|nip|kick|pummel|counter\w*|rebuke|interrupt|"
    r"taunt|throw|toss|lunge|renew|shiv|prick)\b", re.I)
LONG_TYPES = {"revive", "summon_pet"}

#: per-class exceptions after reading the result: ability_id -> speed ("medium" to undo a rule's pick)
OVERRIDES = {
    # Chaos Bolt is the warlock's big long cast, every summoning takes the time, and Drain Life is a channel
    "warlock": {"warlock_shadowburn": "instant", "warlock_corruption": "instant", "warlock_shadow_bolt": "medium",
                "warlock_chaos_bolt": "long", "warlock_summon_imp": "long",
                "warlock_summon_voidwalker": "long", "warlock_summon_succubus": "long",
                "warlock_summon_felhunter": "long", "warlock_drain_life": "long"},
    # the heavy blow is the long one, the finisher the instant one; a bleed is a medium swing
    "warrior": {"warrior_rend": "medium", "warrior_mortal_strike": "long", "warrior_execute": "instant"},
    # Ambush is the wind-up; Rupture is an ordinary finisher
    "rogue": {"rogue_rupture": "medium", "rogue_ambush": "long"},
    # Shadow Word: Pain goes on in an instant; Mind Sear is a channel
    "priest": {"priest_shadow_word_pain": "instant", "priest_mind_sear": "long"},
    # Regrowth is Classic's two-second heal; Swipe is a plain swing
    "druid": {"druid_regrowth": "short", "druid_swipe": "medium"},
    # raising the archers takes its time; the corpse going up is the quick one
    "necromancer": {"necromancer_animate_skeletal_archers": "medium", "necromancer_corpse_explosion": "short"},
}


def castable(e):
    if e["ability_id"].endswith("_attack"):
        return False
    return not (e.get("is_instant") and (e.get("cooldown") or 0) >= 2)


def top(e):
    return (e.get("ranks") or [{}])[-1]


def resize(e, mult, cmult):
    if e.get("effect_type") not in SIZED_TYPES:
        return False
    for r in e.get("ranks", []):
        if r.get("effect_value"):
            r["effect_value"] = max(1, round(r["effect_value"] * mult))
        if r.get("cost"):
            r["cost"] = max(1, round(r["cost"] * cmult))
    return True


def migrate(e):
    """The 21 Nov three-to-four step for one ability. Returns a note, or None if nothing changed."""
    old = e.get("cast_speed")
    if old not in OLD:
        return None
    new = OLD[old]
    if old == "quick" and (SHORT_WORDS.search(e["name"]) or e.get("effect_type") == "heal"):
        new = "short"
        (im, ic), (sm, sc) = SIZE["instant"], SIZE["short"]
        resize(e, sm / im, sc / ic)
        e.setdefault("_tuning", []).append(
            "21 Nov 2026: a short cast (Kyle: \"we have instant, short, medium, long\"), re-sized from the quick size "
            "to the short one (tools/build_cast_speeds.py)")
    e["cast_speed"] = new
    return f"{old} -> {new}"


def picks_for(cls, abilities):
    """{ability_id: speed} for this class's castable abilities that have none yet, plus a short one if it lacks it."""
    pool = [e for e in abilities if castable(e)]
    out = {e["ability_id"]: e["cast_speed"] for e in pool if e.get("cast_speed")}
    free = [e for e in pool if not e.get("cast_speed")]
    n = len(pool)
    caps = {"instant": max(2, round(n * 0.3)), "short": max(1, round(n * 0.15)), "long": max(1, round(n * 0.2))}
    count = lambda sp: sum(1 for v in out.values() if v == sp)  # noqa: E731

    def take(e, sp, over_medium=False):
        cur = out.get(e["ability_id"])
        if (cur is None or (over_medium and cur == "medium")) and count(sp) < caps[sp]:
            out[e["ability_id"]] = sp

    by_val = sorted(free, key=lambda e: top(e).get("effect_value") or 0)
    for e in reversed(by_val):
        if LONG_WORDS.search(e["name"]) or e.get("effect_type") in LONG_TYPES:
            take(e, "long")
    for e in by_val:
        if e["ability_id"] in out:
            continue
        if SHORT_WORDS.search(e["name"]):
            take(e, "short")
        elif INSTANT_WORDS.search(e["name"]) or e.get("taunt") or e.get("interrupt") or e.get("interrupts"):
            take(e, "instant")
    # the class's own extremes, from what's still plain
    plain = [e for e in pool if out.get(e["ability_id"]) in (None, "medium") and (e.get("cooldown") or 0) <= 3
             and (top(e).get("effect_value") or 0) > 0 and not e["ability_id"].endswith("_attack")]
    hits = sorted([e for e in plain if e.get("effect_type") in HIT_TYPES], key=lambda e: top(e)["effect_value"])
    heals = sorted([e for e in plain if e.get("effect_type") in HEAL_TYPES], key=lambda e: top(e)["effect_value"])
    if len(heals) >= 2 and count("long") < 1:
        take(heals[-1], "long")
    for e in reversed(hits):
        if count("long") >= 1 or len(hits) < 2:
            break
        take(e, "long")
    for e in hits:
        if count("instant") >= 2:
            break
        take(e, "instant", over_medium=True)
    if count("short") < 1:
        direct = [e for e in heals if e.get("effect_type") == "heal" and out.get(e["ability_id"]) in (None, "medium")]
        rest = [e for e in hits if out.get(e["ability_id"]) in (None, "medium")]
        for e in direct[:1] + rest[:1]:
            if count("short") >= 1:
                break
            take(e, "short", over_medium=True)
    for e in pool:
        out.setdefault(e["ability_id"], "medium")
    out.update({k: v for k, v in OVERRIDES.get(cls, {}).items() if k in out})
    return out


def classes():
    for path in sorted(DIR.glob("*.json")):
        if path.stem.startswith("_") or path.stem == "asher_unique":
            continue
        yield path


def check():
    problems = []
    for path in classes():
        cls = path.stem
        pool = [e for e in json.loads(path.read_text(encoding="utf-8"))["abilities"] if castable(e)]
        bad = [e["ability_id"] for e in pool if e.get("cast_speed") not in NAMES]
        if bad:
            problems.append(f"{cls}: {len(bad)} castable abilities have no speed of the four (e.g. {bad[0]})")
        speeds = [e.get("cast_speed") for e in pool]
        need = {"instant": 2, "short": 1, "long": 1}
        short_of = [f"{speeds.count(k)} {k}" for k, v in need.items() if speeds.count(k) < v]
        if short_of:
            problems.append(f"{cls}: only {', '.join(short_of)} (needs 2 instant, 1 short, 1 long)")
    for p in problems:
        print("  -", p)
    print(f"cast speeds: {'OK' if not problems else str(len(problems)) + ' problems'}")
    return 1 if problems else 0


def main():
    if "--check" in sys.argv:
        return check()
    apply = "--apply" in sys.argv
    totals = {k: 0 for k in NAMES}
    migrated = 0
    for path in classes():
        cls = path.stem
        doc = json.loads(path.read_text(encoding="utf-8"))
        for e in doc["abilities"]:
            if migrate(e):
                migrated += 1
        picks = picks_for(cls, doc["abilities"])
        shown = {"instant": [], "short": [], "long": []}
        for e in doc["abilities"]:
            sp = picks.get(e["ability_id"])
            cur = e.get("cast_speed")
            # an existing tag only moves from medium: to short or instant when the class is missing one, or by an override
            moves = cur == "medium" and (sp in ("short", "instant")
                                         or OVERRIDES.get(cls, {}).get(e["ability_id"]) == sp)
            if not sp or sp == cur or (cur and not moves):
                continue
            e["cast_speed"] = sp
            totals[sp] += 1
            if sp in SIZE:
                mult, cmult = SIZE[sp]
                sized = resize(e, mult, cmult)
                e.setdefault("_tuning", []).append(
                    f"21 Nov 2026: a {sp} cast for the turn timeline (tools/build_cast_speeds.py)"
                    + (f", sized {mult}x for {cmult}x the cost" if sized else ""))
                shown[sp].append(e["name"])
        if any(shown.values()):
            print(f"{cls:16} " + "  ".join(f"{k}: {', '.join(v)}" for k, v in shown.items() if v))
        if apply:
            path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{migrated} migrated from three speeds to four; new picks {totals} "
          f"{'written' if apply else 'would be written'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
