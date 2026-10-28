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
