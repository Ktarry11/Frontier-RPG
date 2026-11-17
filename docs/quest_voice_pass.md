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

## World-wide pass (17 Nov 2026)

Kyle: "audit and fix the quests with the voice and tone we want since we have the proper style now".

Every quest file now sits at zero: 50 files, 1,574 quests, 0 voice findings, 0 refrains, 0 prose tics. That
includes the dungeons and the hidden zones (Locations not described). All talk-topic files pass too.

Text lives in `tools/voice/<stem>.py` as `VOICE = {qid: (D, A, T)}`, with `None` keeping the live field.
`PYTHONPATH=. python3 tools/build_zone_voice.py <stem> --write` builds it into `zzzzzzzz_voice_<stem>.json`, the
last overlay, and `tools/mark_voice_done.py <stem>` locks it in. The build checks the merged text of every qid
listed, None fields included, and refuses to write on any problem.

### The bars now enforced

- **Voice** (`audit_quest_voice`): no "not X, it is Y", contractions where speech would use them, no " - "
  dashes, no fragments under three words, no aphorisms or filler, no thanks-only turn-ins, 760 characters max
  per field, ASCII only.
- **Refrains**: a zone fails if "thanks/thank you", "friend", "stranger", "outsider" or "take your pick" shows up
  in max(3, quests/5) or more of its quests.
- **Prose tics** (`tools/audit_quest_prose.py`): a number word matching an objective count, the aphorism
  stems ("which tells you", "I know how that sounds", "there is a difference"...), hand-ins that close on
  "Take this." / "Thank you." / "You've earned it.", [stage directions], and weary lines ("I no longer",
  "I have stopped").

### Traps from the world pass

- New contractions make new fragments ("Right, then.", "It's quiet."). Join them into a real clause.
- Uncontracted phrases hide inside longer ones ("lighting it is somebody's job"). Reword rather than force.
- Check each giver's gender in the NPC data before writing pronouns. Several were wrong in the old text.
- Forsaken zones put the speech in D and a short parting line in A. Most others narrate in D and speak in A.

### Still open

- Plaguelands direction faults.
- Sanu's gender reads differently between quests.
- hbe_impossible_yetis names Apothecary Lydon while the giver is Wren.
