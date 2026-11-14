#!/usr/bin/env python3
"""Every ability and talent description must say what the thing DOES.

Kyle has asked for this repeatedly: "a lot of the skills dont need these odd AI
flavor texts. theyre strange. all skills and spells should simply say WHAT they
do." And, after being told it was handled: "I keep asking. But I'll ask again as
it bothers me. Did you fix the weird written talents and skills... Fix it fully."

It had NOT been fixed. 694 of 1274 ability descriptions stated no mechanic at
all - the whole barbarian kit was flavour ("Thick Skull: Your skull has been
described, more than once, as a structural feature"). This check exists so the
answer to that question is a command instead of my recollection.

A description PASSES if it names any mechanic: a number, a percentage, a
resource, a duration, a status, a target. The bar is deliberately low. The
failure being guarded against is prose that tells the player how a thing FEELS
and leaves them guessing what it does.

Known-good exceptions are listed, not special-cased by pattern: a handful of
descriptions ("Makes your next cast instant") state their effect in words this
check's vocabulary does not happen to contain.
"""
import sys, os, json, glob, re
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

MECH = re.compile(
    r'\d|%|chance|increase|reduce|decreas|damage|heal|threat|cooldown|mana|rage|energy'
    r'|stack|duration|turn|range|crit|armou?r|resist|generat|absor|speed|haste|taunt'
    r'|interrupt|stun|slow|silence|summon|revive|shield|cleanse|dispel|snare|root'
    r'|charge|combo|rune|power|restore|immune|form|instant|remov|cure|totem',
    re.I)

#: A talent whose whole job is to GRANT an ability says so, and that ability
#: carries its own tooltip. "Teaches Chimera Shot, a heavy single-target shot"
#: is a complete answer to "what does this do", so it is not a failure.
TEACHES = re.compile(r'^\s*(Teaches|Learn|Grants|Unlocks)\b', re.I)

#: Descriptions that state their effect plainly in vocabulary MECH lacks.
ALLOW = {
    "Call of the Ancestors",
    # "Retaliation" and "High Guard" used to be excepted here because
    # guardian_vanguard was on a no-touch list during the Oct 31 description
    # rewrite. Kyle confirmed on 5 Nov 2026 that the rule was scoped to that
    # pass, not to the CoA class audit, so Vanguard was rebuilt and both
    # descriptions now name their own mechanics. The exceptions are gone;
    # removing them was verified to leave this check passing.
    # These DO state their effect, in words this check's vocabulary happens not
    # to contain ("an immediate extra attack", "causing them to bleed", a glyph
    # condition). Listed one by one on purpose: loosening MECH to swallow them
    # would also start passing the flavour prose this check exists to catch.
    "Primal Shred", "Judgements of the Just", "Flame Glyph", "Arcane Glyph",
}


def collect(pattern):
    out = []
    for f in sorted(glob.glob(pattern)):
        doc = json.load(open(f, encoding="utf-8"))

        def walk(o):
            if isinstance(o, dict):
                if "name" in o and isinstance(o.get("description"), str) and (
                        "ability_id" in o or "talent_id" in o):
                    out.append((os.path.basename(f), o["name"], o["description"]))
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(doc)
    return out


def main():
    ok = True
    for label, pattern in (("abilities", "data/abilities/*.json"),
                           ("talents", "data/talents/*.json")):
        rows = collect(pattern)
        bad = [(f, n, t) for f, n, t in rows
               if n not in ALLOW and not MECH.search(t) and not TEACHES.match(t)]
        print(f"  {len(rows):5d} {label}: {len(bad)} state no mechanic")
        for f, n, t in bad[:20]:
            print(f"      [{f}] {n}: {t[:90]}")
        if len(bad) > 20:
            print(f"      ... and {len(bad)-20} more")
        if bad:
            ok = False

    # Dev notes must never reach a player. One already had: Revive Pet carried
    # "KNOWN UI GAP: the normal target picker pulls from living_allies()...".
    DEV = re.compile(r'\b(KNOWN UI GAP|TODO|FIXME|XXX|dev note|see entities/|see combat/|see ui/)\b', re.I)
    leaked = [(f, n, t) for f, n, t in
              collect("data/abilities/*.json") + collect("data/talents/*.json")
              if DEV.search(t)]
    print(f"\n  dev notes visible to players: {len(leaked)}")
    for f, n, t in leaked:
        print(f"      [{f}] {n}: {t[:110]}")
    if leaked:
        ok = False

    print("\nPASS" if ok else "\nFAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
