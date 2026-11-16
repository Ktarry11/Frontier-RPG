# Dungeon bosses: no buffing, no punching bags (16 Nov 2026)

Kyle: "How about you screen through all dungeon bosses in the game to ensure none of them are buffing / debuffing /
punching bags". Earlier the same day: "make sure bosses are not just debuffing. they should have something
dangerous".

## The test
`tools/audit_boss_turns.py` fights each boss for 40 turns (the same harness as `audit_monster_combat`) and flags:
- **Passive:** more than 30% of the turns it acted went on buffs, debuffs or heals that hurt nobody.
- **Dead slot:** a buff or debuff it carries and never used. `Monster.choose_action` never spends a turn on a plain
  buff or debuff while an attack is ready, so on a boss with attacks they're decoration.
- **Toothless:** in 40 turns it never threw anything the party has to answer: a big hit (1.6x its basic or more), a
  party blast (0.9x across everyone), a stun with a hammer behind it, a DoT worth 1.5x a basic hit, a desperation
  move at low health, or adds.

## What it found
174 dungeon bosses (a dungeon's, a tuned dungeon's, a hidden level's, a deep frontier's): **97 failing.** 81 were
toothless, 12 passive, and 8 carried dead slots (the old "Ward" buffs among them).

## The fix (`tools/fix_dungeon_boss_turns.py`, idempotent)
- **54 plain buffs and debuffs now ride attacks**: 85% of the boss's basic hit (60% if it hit the whole party),
  the same name, cooldown, school, duration and stat changes, plus any shield, stun or mechanic. A buff lands on
  the boss; a debuff on whoever it hits. Low-health phase buffs are left alone.
- **81 signature moves** in the boss's own school: 46 big hits (1.8x every fourth turn; 1.7x every fifth under
  level 20, so the first dungeons stay first dungeons) and 35 party blasts (0.95x every fifth turn), picked by name.
  Four bosses whose blast sat behind a bigger single hit forever (the AI throws its biggest ready attack) got a 2x
  big hit every third turn instead.
- Every changed or added ability carries `"boss_rework": "turns_pass"`.
- Result: **174 of 174 pass.**

## Keeping it fixed
`tools/qa_dungeon_boss_turns.py` fails if any dungeon boss slides back, which is what happens if a zone builder or
`tools/generate_creatures.py` rewrites a kit. Run the fixer again and it re-applies only what's needed.

## Then the open world and the caves
Kyle: "Yup, open world and caves next". A cave that isn't a dungeon counts its boss as a field boss, so caves came
with the open world: field bosses, caves' bosses, skull zones' and open frontiers'. **356 bosses, 275 failing**
(258 toothless, 23 passive, 2 with dead slots).
- **107 plain buffs and debuffs now ride attacks**, the same rule as the dungeons.
- **258 signature moves, all big hits** (1.7x the basic, every fifth turn) and no party blasts, because a field
  boss is often fought by one or two people.
- Result: **356 of 356 pass**, and with the dungeons, **530 of 530**.

`tools/qa_dungeon_boss_turns.py` now holds every boss in the game. `tools/fix_dungeon_boss_turns.py --scope
dungeon|open|all` re-applies whichever part a builder undoes.
