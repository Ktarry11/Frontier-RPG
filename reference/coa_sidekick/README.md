# Conquest of Azeroth reference — ascensionsidekick.com

Rendered text of every class and spec page from https://ascensionsidekick.com/,
captured 2026-10-28. The site is a React SPA, so a plain HTTP fetch returns an
empty shell; these were captured with a headless browser after JS execution.

`CLASS_<class>.txt`  — class overview: primary stat, resource, lore blurb,
                       recommended leveling spec, and the spec roster with
                       role labels and PvE/PvP tier ratings.
`SPEC_<class>__<spec>.txt` — per spec: role, tier ratings, the "retail feel"
                       comparison to a real WoW spec, talent point layout,
                       playstyle, strengths/weaknesses, stat priority, and
                       solo + dungeon rotations.

21 classes, 70 specs. Spec counts vary — most classes have 4, some have 3.

WHAT THIS IS: a fan-made community theorycrafting companion, not official data.
Its own disclaimer says "COA is pre-meta - treat as a planning heuristic,
verify in play." Use it for spec IDENTITY, role, resource mechanics, stat
priority and rotation shape. Frontier's numbers are Frontier's own.

WHY IT MATTERS HERE: Frontier's 13 unbuilt classes (Barbarian, Bloodmage,
Chronomancer, Felsworn, Guardian, Knight of Xoroth, Necromancer, Pyromancer,
Ranger, Reaper, Templar, Witch Doctor, Witch Hunter) had stats, armour types
and resources defined but no abilities and no talent trees. These pages are
the design brief for authoring them, and they have already corrected several
assumptions about the 17 classes that DO exist - see
claude/coa_reference_corrections_2026_10_28.md in the project.

## talents/ — the real talent trees

`talents/<class>.json`, built by `tools/build_coa_talent_reference.py` from
`tools/scrape_coa_talents.js`. 21 classes, 801 class-tree nodes and 2,811
spec-tree nodes: every talent's name, full description, point cost, rank
count and tier gate.

The page TEXT contains no talent data — the builder grid renders bare point
counts like "3/3" — but each node's tooltip is already in the DOM as
`span.btooltip`, structured `<b>name</b> · description · <i>cost</i> ·
<i>requirement</i>`.

**AE is a class-tree point, TE a spec-tree point.** CoA gives every class one
shared class tree plus one tree per spec, and a spec page renders both, so
the class tree repeats across that class's pages and is deduplicated here.

**Tier comes from the gate**, not a tier field: "Requires 8 TE in this tree"
is CoA's own gate and converts directly into Frontier's `tier_requirements`.

### Structural difference worth knowing before using this

CoA and Frontier do not shape trees the same way:

| | CoA | Frontier |
|---|---|---|
| nodes per tree | ~40 | ~23 |
| point gates | 3 (e.g. 0 / 8 / 23 TE) | 7 tiers (0/5/10/15/20/25/30) |
| free passives | yes — one per 10 levels, "Level 40 Passive", costing nothing | none |

So this is **not** a file to transcribe. Use it for identity, names, and what
each talent actually does; select the ~23 that carry a spec and lay them out
on Frontier's 7 tiers. Numbers stay Frontier's — the site's own disclaimer is
that COA is pre-meta.
