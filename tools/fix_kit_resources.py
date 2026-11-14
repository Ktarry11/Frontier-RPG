#!/usr/bin/env python3
"""Kit abilities must cost a resource their owner's CLASS actually has.

    PYTHONPATH=. python3 tools/fix_kit_resources.py [--apply]

Idempotent. Derives every value from the class's own ability data rather than
a hand-written map, so it stays correct when a class is rebuilt.

=============================================================================
THE BUG
=============================================================================

75 personal-kit abilities across 25 recruits named a resource their class
does not use, and 13 were outright UNCASTABLE because the named pool has a
maximum of zero:

    Templar     uses combo       (39 of its own abilities)  kits said mana
    Necromancer uses life_force  (40)                       kits said mana
    Felsworn    uses felfury     (43)                       kits said mana/rage

Found when Tarek Mansour's dispel failed with "Not enough mana (need 30)"
against a character whose max mana is 0. Three of his abilities, three of
Adrian's, three each for Stelios and Ileana, two for Ziad - thirteen
abilities that could never fire at any level with any gear.

The rest are castable but draw from the wrong bar: a Guardian kit costing
rage where the class runs on energy, a Hunter kit costing focus where the
class runs on mana. Castable because every Character carries rage and energy
pools of 100 whether or not its class uses them, which is exactly why this
went unnoticed - the ability works, it just spends the wrong currency.

Kyle's call, asked directly: kits follow the class.

=============================================================================
WHAT "FOLLOW THE CLASS" MEANS WHEN A CLASS HAS TWO RESOURCES
=============================================================================

Half the classes are MIXED - a primary plus a CoA secondary (Cultist's
Insanity, Knight of Xoroth's Deathfire, Reaper's Souls, Runemaster's Runes,
Stormbringer's Static, Tinker's Scrap, Bloodmage's Health and Vitality).
Flattening every class to its single most common resource would have
rewritten kits that were already right:

    Primalist  mana 29 + RAGE 12   - three recruits' kits cost rage, legitimately
    Venomancer mana 34 + rage 6 + ENERGY 5 - Callum's kit costs energy, legitimately

So the rule is NOT "use the primary". It is:

    if the kit's resource is one the class actually uses -> leave it alone
    otherwise                                           -> use the primary

That fixes every real problem and touches nothing that was already correct.
A class with no resource data at all is skipped rather than guessed at.
"""
import argparse
import collections
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
KITS = ROOT / "data" / "npcs" / "personal_kits.json"

#: Not a real class file - the shared pool and Asher's locked record.
SKIP_FILES = {"_universal", "asher_unique"}


def class_resources():
    """{class_slug: (primary, {every resource it uses})} from the real data."""
    out = {}
    for f in sorted(glob.glob(str(ROOT / "data" / "abilities" / "*.json"))):
        slug = Path(f).stem
        if slug in SKIP_FILES:
            continue
        try:
            d = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        rows = d if isinstance(d, list) else list(d.values())
        flat = []
        for r in rows:
            flat.extend(r if isinstance(r, list) else [r])
        c = collections.Counter(a.get("resource_type") for a in flat
                                if isinstance(a, dict) and a.get("resource_type"))
        if c:
            out[slug] = (c.most_common(1)[0][0], set(c))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    from world.recruit_manager import get_recruit_manager

    res = class_resources()
    doc = json.loads(KITS.read_text(encoding="utf-8"))
    rm = get_recruit_manager()
    recs = {getattr(r, "recruit_id", None): r
            for r in (rm.recruits.values() if isinstance(rm.recruits, dict)
                      else rm.recruits)}

    changed, kept, unknown = [], [], []

    for kid, kit in doc.items():
        if kid.startswith("_") or not isinstance(kit, dict):
            continue
        r = recs.get(kid)
        if r is None:
            continue
        ch = r.build_character()
        slug = str(getattr(ch, "char_class", "")).lower().replace(" ", "_")
        if slug not in res:
            unknown.append((kit.get("name"), slug))
            continue
        primary, every = res[slug]
        for a in (kit.get("abilities") or []):
            got = a.get("resource_type")
            if not got:
                continue
            if got in every:
                # the class really does use this one - not a bug, leave it
                if got != primary:
                    kept.append((kit.get("name"), slug, a.get("name"), got, primary))
                continue
            changed.append((kit.get("name"), slug, a.get("name"), got, primary))
            if args.apply:
                a["resource_type"] = primary

    print(f"  {len(changed)} ability/abilities moved onto their class's resource")
    if kept:
        print(f"  {len(kept)} left alone - a SECONDARY their class genuinely uses")
    if unknown:
        print(f"  {len(unknown)} recruit(s) whose class has no resource data: "
              f"{sorted({u[1] for u in unknown})}")
    print()

    if changed:
        byclass = collections.defaultdict(list)
        for who, slug, name, got, primary in changed:
            byclass[(slug, got, primary)].append(who)
        print(f"  {'class':16}{'was':18}{'now':18}{'n':>3}  recruits")
        for (slug, got, primary), whos in sorted(byclass.items()):
            print(f"  {slug[:14]:16}{got[:16]:18}{primary[:16]:18}{len(whos):>3}  "
                  f"{', '.join(sorted(set(whos)))[:46]}")

    if kept:
        print(f"\n  LEFT ALONE - the class uses this resource too, so the kit is right:")
        for who, slug, name, got, primary in kept:
            print(f"    {str(who)[:15]:17}{slug[:12]:14}{got:16}"
                  f"(class primary is {primary})")

    if args.apply:
        KITS.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"\n  wrote {KITS.relative_to(ROOT)}")
    else:
        print("\n  dry run - pass --apply to write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
