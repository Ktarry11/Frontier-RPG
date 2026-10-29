#!/usr/bin/env python3
"""Put each ability in the spellbook tab whose talent tree actually touches it.

THE PROBLEM. Six classes had every single ability in the "core" tab -
Bloodmage's 65 abilities in one flat scroll. Not a data error: tabs are
inferred by tools/wire_class.py from which tree's `unlock_ability` node
names an ability, and those classes' trees don't use unlock_ability, so
there was nothing to infer from.

THE SIGNAL. unlock_ability is not the only place a tree names an ability.
Talent effect keys do it constantly - `ability_witch_doctor_hex_of_malice_damage`
is Voodoo saying "Hex of Malice is mine" as plainly as an unlock would. So
does `ability_filter`, `cast_ability`, `reset_cooldown`, and a scale key.
Searching each tree's whole JSON for the ability_id catches all of them.

  id appears in exactly one tree  -> that tree's tab
  appears in two or more          -> core (shared across specs)
  appears in none                 -> core (baseline class kit)

WHY THIS AND NOT THE SPEC PAGES' PROSE. Each CoA spec page names the
abilities it plays with, so name-matching that prose is an obvious
alternative. Both were scored against the eight classes whose tabs came
from the CoA handoff's own explicit per-spec lists - a different source
answering the same question, so it works as an answer key:

    method        agreement        lands in a WRONG spec tab
    prose          55.4%                   13.1%
    references     60.1%                    4.5%
    both combined  61.6%                    7.0%

References win and combining makes it worse: the 1.5 points of extra
agreement cost 2.5 points of actively-wrong placements, which is the only
error that hurts. Looking in Sanguine for a Sanguine ability and not
finding it is a nuisance; finding it filed under Fleshweaver is a lie.

The dominant miss (124 of 160) is leaving a real spec ability in core. That
is the safe direction and it is also honest - core is documented as "class
kit / no single spec owns it", and an ability no tree mentions genuinely has
no owner to claim it.

Run --check to re-score against the answer key. Handoff classes are
REFUSED as targets: their explicit lists beat 60% inference, so this never
overwrites them.
"""

from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TABS = ROOT / "data/spellbook_tabs_coa.json"

#: Tabs taken from the CoA class-preservation handoff's explicit per-spec
#: ability lists. Authoritative - used as the answer key, never a target.
HANDOFF = [
    "Cultist", "Starcaller", "Sun Cleric", "Runemaster",
    "Stormbringer", "Tinker", "Venomancer", "Primalist",
]


def prefix(char_class: str) -> str:
    return char_class.lower().replace(" ", "_").replace("-", "_")


def ability_ids(char_class: str) -> list[str]:
    p = ROOT / f"data/abilities/{prefix(char_class)}.json"
    if not p.exists():
        return []
    return [a["ability_id"]
            for a in json.loads(p.read_text(encoding="utf-8")).get("abilities", [])
            if a.get("ability_id")]


def assign(char_class: str) -> dict[str, str]:
    """Strongest claim wins, and only a tie or a blank falls to core.

    Two strengths of claim, because they are not the same statement:

      UNLOCK  a node with `unlock_ability: <id>` - this tree is the only
              way to get this ability at all. Unambiguous ownership.
      MENTION the id appears anywhere else in the tree - an effect key
              buffing it, an ability_filter, a cast_ability. Means "this
              tree cares about it", which several trees can true at once.

    Flat equality between them regressed Guardian from 11 core abilities to
    33: an ability unlocked by Vanguard and merely buffed by Gladiator read
    as a two-tree tie and fell to core, discarding the unlock - the one
    claim that can't be contested. So unlocks are resolved first and a
    mention never outvotes one.
    """
    pre = prefix(char_class)
    ids = ability_ids(char_class)
    trees = sorted((ROOT / "data/talents").glob(pre + "_*.json"))

    unlocks: dict[str, set[str]] = collections.defaultdict(set)
    mentions: dict[str, set[str]] = collections.defaultdict(set)
    for tp in trees:
        text = tp.read_text(encoding="utf-8")
        tree = json.loads(text)
        nodes = tree.get("nodes") or tree.get("talents") or []
        # unlock_ability is an EFFECTS key, not a top-level node key -
        # TalentTree.get_total_effects() sums effects and collects the
        # non-numeric ones, which is how Character.get_talent_unlocked_
        # abilities() finds them. Reading it off the node instead found
        # nothing anywhere and made every talent-granted ability in the
        # game look unobtainable; the real count is one.
        unlocked = set()
        for n in nodes:
            v = (n.get("effects") or {}).get("unlock_ability")
            if v:
                unlocked.update(v if isinstance(v, list) else [v])
        for aid in ids:
            if aid in unlocked:
                unlocks[aid].add(tp.stem)
            elif aid in text:
                mentions[aid].add(tp.stem)

    out = {}
    for aid in ids:
        u = unlocks.get(aid, set())
        if len(u) == 1:
            out[aid] = next(iter(u))
            continue
        if u:                       # two trees unlock it - genuinely shared
            out[aid] = "core"
            continue
        m = mentions.get(aid, set())
        out[aid] = next(iter(m)) if len(m) == 1 else "core"
    return out


def spread(mapping: dict[str, str]) -> tuple[int, dict[str, int]]:
    counts: dict[str, int] = {}
    for tab in mapping.values():
        counts[tab] = counts.get(tab, 0) + 1
    return counts.pop("core", 0), counts


def check() -> int:
    truth = json.loads(TABS.read_text(encoding="utf-8"))
    print("Scored against the CoA handoff's explicit per-spec ability lists")
    print("=" * 78)
    ta = tc = tw = 0
    for cls in HANDOFF:
        t = truth.get(cls, {})
        if not t:
            continue
        mine = assign(cls)
        shared = [a for a in t if a in mine]
        agree = [a for a in shared if t[a] == mine[a]]
        wrong = [a for a in shared
                 if t[a] != "core" and mine[a] != "core" and t[a] != mine[a]]
        to_core = [a for a in shared if t[a] != "core" and mine[a] == "core"]
        ta += len(agree); tc += len(shared); tw += len(wrong)
        print(f"{cls:<14}{len(agree):>3}/{len(shared):<3} "
              f"({100.0 * len(agree) / len(shared):5.1f}%)   "
              f"left in core {len(to_core):<3} wrong spec {len(wrong)}")
    print("-" * 78)
    print(f"overall {ta}/{tc} ({100.0 * ta / tc:.1f}%), "
          f"wrong spec {tw} ({100.0 * tw / tc:.1f}%)")
    return 0


def main(argv: list[str]) -> int:
    if "--check" in argv:
        return check()
    targets = [a for a in argv if not a.startswith("-")]
    if not targets:
        print(__doc__)
        return 1
    existing = json.loads(TABS.read_text(encoding="utf-8")) if TABS.exists() else {}
    for cls in targets:
        if cls in HANDOFF:
            print(f"{cls:<18} handoff data is authoritative - refusing")
            continue
        mapping = assign(cls)
        if not mapping:
            print(f"{cls:<18} no abilities found")
            continue
        # Never trade a richer mapping for a poorer one. Guardian already
        # had 30 of its 41 abilities in spec tabs from a better source than
        # talent references (its trees contain no unlock_ability at all and
        # mention only 8 abilities), so inference here would have thrown 22
        # correct placements away. Whatever that source was, it beat this
        # method, and a tool that can silently downgrade good data is worse
        # than no tool.
        before = existing.get(cls) or {}
        placed_before = sum(1 for v in before.values() if v != "core")
        placed_now = sum(1 for v in mapping.values() if v != "core")
        if before and placed_now < placed_before:
            print(f"{cls:<18} refusing: would place {placed_now} in spec tabs, "
                  f"existing data places {placed_before} - keeping existing")
            continue
        existing[cls] = mapping
        core, counts = spread(mapping)
        was = f"  (was core={sum(1 for v in before.values() if v == 'core')})" if before else ""
        print(f"{cls:<18} core={core:<4} " +
              ", ".join(f"{k[len(prefix(cls)) + 1:]}={v}"
                        for k, v in sorted(counts.items())) + was)
    TABS.write_text(json.dumps(existing, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8")
    print(f"\nwrote {TABS.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
