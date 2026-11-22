# Quest writing standard

Kyle, 21-22 Nov 2026: no quests handed out in third person; a story of at least 5-6 coherent sentences; "YOU MUST update
your ways of working on writing quests". This is the bar every quest is written to. `tools/audit_quest_voice.py` checks
the mechanical parts; the rest is on whoever writes it.

## The three fields

| Field | What it is | Where the player sees it |
|---|---|---|
| `description` | The giver talking, first person, 5-6 whole sentences. The story. | The offer window's body **and** the quest journal. |
| `accept_text` | One short beat under 200 characters, said as you take it. A practical tip or a reaction. Never a restatement. | Under the body when you accept. |
| `turn_in_text` | The giver reacting to what you actually did, and moving the story on. Never thanks alone. | The hand-in window. |

The offer window picks `accept_text` as the body when it's longer than `description`, so the accept line stays short and
the description carries the story. That's how one text ends up in both the window and the journal, and how a narrator
never shows up in either.

## The shape of a description

Five or six sentences, roughly in this order. It isn't a template, and a good quest can move the beats around.

1. **What's happening.** Concrete: the named beast, the place, the number, the day it started.
2. **Why it matters to this person.** Not to the world. To them.
3. **One personal beat.** Who they are, a memory, a detail only they'd know.
4. **The ask.**
5. **Where to go,** folded in the way a person gives directions ("past the totems, down by the water").

## How it should sound

- **A real person talking to someone standing in front of them.** Read it aloud. If nobody would say it, rewrite it.
- **Each giver sounds like themselves.** A quartermaster counts things. A Forsaken is dry. A troll keeps "da" and "mon".
  A scared farmer doesn't talk like a general.
- **Vary the openings.** A zone where twenty quests start "I want" or "I need" reads like a form letter.
- **Concrete over vague.** "Four knots on the cord this moon" beats "fewer people are arriving".
- **Never:** fragments, dashes, missing contractions ("I have", "it is"), fortune-cookie aphorisms, meme lines, filler
  ("that's all I ask"), stacked triplets for rhythm, Earth objects (the Ferris wheel aside).
- **Chains move forward.** Step three doesn't recap step one. It picks up where the last turn-in left off.

## What a rewrite keeps and never adds

- **Keeps** every fact, name, number and direction the quest already has, and the good lines it already has. A strong
  accept speech gets folded into the new description, not thrown away.
- **May add** small personal colour that fits the giver (a buried traveller's pack, a grandmother's balcony).
- **Never adds** new places, new lore, world changes, or anything near hidden content or the embargoes.

## Example

Before, the journal (narrator): *"The Longtooth Runners have learned that the people coming down off the mountain are
tired, and they hunt the bottom of the pass now. Wapi would like them to learn something else."*

After:

> "The Longtooth Runners have worked out that the people coming down off the mountain are exhausted, and they hunt the
> bottom of the pass now. I've buried two travellers this season who made it over the whole range and died a mile from
> the camp. One of them still had his pack on, with a letter inside for somebody in Mojache. I'd like those wolves to
> learn that the bottom of this trail isn't easy hunting any more. Thin them out where the descent levels off, and don't
> stop until they think twice."

Accept: *"Go in loud. Wolves that hunt tired people don't expect anyone to fight back."* It's a new beat. It doesn't
repeat "where the descent levels off" from the speech above it.

## Process

- One zone at a time, as `tools/voice/<zone>.py` compiled by `tools/build_zone_voice.py <zone> --write`.
- One commit per zone, pushed when it's done.
- Kyle reads the first zone of a batch before the rest goes ahead.
- A finished zone goes on the story-done list in `tools/audit_quest_voice.py`, which makes "under 5 sentences" and "the
  journal narrates" hard failures there, so it can't slip back.
- **Accept echo is a hard failure too.** If 60% or more of the accept line's content words are already in the speech,
  the build refuses to write. The accept line must say something the speech didn't: a warning, a tip, an aside, a
  reaction. Copying the speech's last sentence into the accept slot is the commonest way this goes wrong.
- **Write every accept line with the whole speech in front of you.** Not a cut-down dump, and not the last 300
  characters. Batching is fine; writing blind is not. Passing the checks is the floor, not the bar: read each line
  against its speech and ask whether it adds anything.
