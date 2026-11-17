# Quest writing pass: plain voice, zone by zone (started 17 Nov 2026)

Kyle, 17 Nov 2026: "Can you start to do a quest writing pass while we wait for art. Like I'm seeing issues in STV
with writing too. You have the template for what is good writing."

The bar is `claude/quest_writing_guide.md` and the 10 Nov playtest notes. A giver says who they are, what's
wrong, why it matters to them, and what to do and where, in their own voice. Out go aphorisms, mood narration,
riddle lines that hold back what's going on, missing contractions, dashes, one-word sentences and counts in prose.

## Done

**Stranglethorn (North, Central, South with Booty Bay): 90 quests and 27 talk topics.** Commit 4722c7e.

What the old text had wrong:
- Clever lines and aphorisms, such as "a river with ambitions".
- Mood narration and riddles.
- Sentences an earlier count-stripping pass had broken, such as "If you can manage ten, and look...", "Them
  between my rack and the notch" and "them will clear you a quarter of an hour".

The story beats were kept. Lore rates afterwards: South 30%, Central 33%, North 43%.

## How a zone goes through it

1. `PYTHONPATH=. python3 tools/audit_quest_voice.py` lists every zone, worst first, as the game shows its text.
   Add a zone name to see every finding in it.
2. `PYTHONPATH=. python3 tools/quest_targets.py <zone>` shows where each objective really is from its giver:
   the place, the bearing and the distance. Directions in the rewrite come from this, never from memory.
   - A target on another map is reached through a door, and that door's bearing is the one the direction audit
     judges by. When in doubt, name the place instead of giving a compass word.
3. Write the zone's text in a `tools/<zone>_quest_voice.py`, using the same shape as `tools/stv_quest_voice.py`.
   Compile it with a builder like `tools/build_stv_voice.py` into an overlay that loads last. The builder
   refuses to write any line that fails the bar.
4. Talk-quest topics live in `world/quest_dialogue_<zone>.py`, and their text needs the same pass
   (see `tools/stv_topic_voice.py`). Keep the topic ids, because a talk quest completes on them.
5. Run `audit_quest_directions`, `audit_quests` (prose counts), `qa_quest_lore` (rate bands) and
   `qa_quest_overhaul`.
6. Give the zone a `"voice"` entry in `tools/quest_overhaul_done.json`. From then on `qa_quest_overhaul`
   holds it at zero findings.

## Traps found on the way

- **Reading the whole quest.** The first draft's one-word sentences were my own habit ("Good.", "Done.",
  "Forty-one."), and so was "I have to". The checker catches those. A fix for a fragment can leave a clumsy
  joined sentence ("but water doesn't glow like that, but lamps do"), and only reading the text as the game
  shows it catches that.
- **Lore rates.** Plainer phrasing can drop a zone under its lore floor without losing any references, because
  the pattern wants the natives' own words ("where you're from", "you lot", "three years").
- **Turn-in speakers.** `tools/dump_quests_for_rewrite.py` reports the hand-in NPC wrongly. The truth is
  `turn_in_npc_id` in the quest file; check it before deciding who speaks the turn-in.

## League table (findings per quest, 17 Nov 2026, after Stranglethorn)

Worst first:

| Zone | Findings per quest |
|---|---|
| Crossroads | 6.0 |
| Southern Needles | 4.8 |
| Southern Barrens | 4.7 |
| Undercity | 4.7 |
| Echo Isles | 4.6 |
| Orgrimmar | 4.5 |
| Durotar | 4.5 |
| Sepulcher | 4.5 |
| Central Barrens hub | 4.3 |
| Tanaris | 4.3 |
| Shimmering Flats | 4.2 |

Ashenvale scores 3.6. Kyle said its writing is good and to leave it alone (10 Nov), so the count alone doesn't
decide. Read a zone before rewriting it.
