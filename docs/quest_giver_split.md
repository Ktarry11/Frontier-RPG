# Quest givers: four each, at most (17 Nov 2026)

Kyle, 17 Nov 2026: "if there are NPCs who give too many quests, add new NPCs to account for it", then "Aim for 4
please".

## What changed

- **96 quests moved off 71 overloaded givers**, in three batches:

  | Batch | Places | Quests moved | New people |
  |---|---|---|---|
  | 1 | The Bulwark, Light's Hope Chapel, the Pale Watch | 22 | 7 |
  | 2 | Silverpine South, Deathknell, the Undercity, Bloodmoon Village, Eastern Tirisfal, the Sepulcher, Brill | 29 | 5 |
  | 3 | Kalimdor, the south, Arathi, Hillsbrad and the rest | 45 | 6 |

- **`tools/qa_quest_givers.py` now holds the ceiling at 4** (it was 7). Three givers stay over it on purpose and are
  listed in its `ALLOWED`: Sanu at the oasis, Ulla's survey and Peska's survey. Each is one voice on purpose.

## How a quest picks its new giver

1. **Someone already standing in the same town, with a reason to give it.** Examples:
   - the quartermaster who keeps the March's roll takes the deserters' dog tags;
   - the wind-rider who flies over Underlight takes the quest about its light;
   - the cook opens the shrikes' crops;
   - the market scribe who drew up the writ sends it.
2. **A new person, only where nobody fits.** Each new person has a reason to be there and a greeting saying it.
   Examples: Varden's runner, Old Wenna on Fenris, Fizzwick's old partner Nyx, and the second lookout on Zoram's wall.
3. **Chains stay readable.** Where a chain's step moved to a new giver, the hand-in of the step before now says who to
   see next. For example, Tolliver's hand-in sends you to Hob the stablemaster for Cartmaster Corin.
4. **Ashenvale's text is kept word for word wherever the new giver fits it.** Kyle likes that writing (10 Nov).
   - The grove singer now gives the two Astranaar quests that were always written about a "she".
   - The second lookout on Zoram's wall gives the Blackfathom quests unchanged.

Every other moved quest is rewritten in its new giver's voice, and the voice bar (`tools/audit_quest_voice.py`)
checks each line before anything is written.

## The tools

- **`tools/giver_split_data.py`** holds the data:
  - `NEW_NPCS`: who's new, where they stand and what they say;
  - `MOVES`: which quest moves to whom and why, with its new text;
  - `TEXT`: hand-in lines on quests that stay put but now point at a moved step.
- **`tools/build_giver_split.py`** applies it:
  - `PYTHONPATH=. python3 tools/build_giver_split.py` checks only;
  - `--write` places new people on a free walkable tile near the spot given, records the moves in
    `data/reference/quest_giver_moves.json`, and writes the text to `data/quests/text/zzzzzz_giver_moves.json`.
  - It refuses to write if any line fails the voice bar.
- **Stranglethorn is the exception.** Its voice overlay loads after the giver-moves overlay, so the two Grom'gol moves
  carry their text in `tools/stv_quest_voice.py`.

## Found on the way, left for the writing pass

- **The Plaguelands quest files have direction faults that were there before the split:** 8 WRONG and 13 SILENT in
  the south and north files, and a few in the east.
  - The four moved quests that had them were fixed in their rewrites.
  - The rest belong to the Plaguelands writing pass. The Plaguelands aren't in `tools/quest_overhaul_done.json` yet.
- **Silverpine, Deathknell, Fenris, Eastern Tirisfal and the Sepulcher still carry the old clever voice.** That means
  stage directions in brackets, capitals for stress, one-word sentences and aphorisms. The moved quests are plain
  now, but the quests around them aren't. They're next in the writing pass's league table.
