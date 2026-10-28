#!/usr/bin/env python3
"""Party banter lines. Idempotent.

  PYTHONPATH=. python3 tools/build_banter_lines.py

Writes data/banter/lines.json. See world/banter_manager.py for why this is authored per character per
trigger instead of per pair - 24 companions is 276 pairs and Kyle has said 50+, so pairwise was never
going to survive contact with the roster.

THE RULE EVERY LINE OBEYS: it never names another companion and never implies a shared past with one.
Kyle: "These people are all independent and don't know each other." A line talks about the event, about
the speaker's own life, or to the player. tools/qa_banter.py fails the build if one slips.

VOICE IS THE WHOLE POINT. Kyle: "Players are real and need distinct personalities." Each line has to be
placeable to its speaker with the name covered up, which is the only test that matters here. The
backgrounds did the work already - Marta has never been surprised by a bang and resents people who are;
Pasang is sixty-one and says a mountain is a mountain; Ivan does not think about Earth. The lines are
those people reacting, not twenty-five variations on a quip.

Not every character speaks on every trigger, deliberately. Somebody with nothing to say about walking
into a town should not say something about walking into a town, and the manager simply picks from
whoever does.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

O = "open"
R = "reply"


def L(text, kind=O):
    return {"text": text, "kind": kind}


LINES = {
 "dan_warrior": {
   "town_arrive": [L("Walls, a gate and somebody watching it. I will sleep tonight.")],
   "dungeon_clear": [L("Everybody came out. That is the whole scorecard."),
                     L("Nobody got hurt doing something clever. Good.", R)],
   "close_call": [L("That is on me. I was a step too far left.")],
   "boss_down": [L("Right. Check your straps before we move on.", R)],
 },
 "ama_priest": {
   "town_arrive": [L("There will be sick people here. There always are.")],
   "close_call": [L("Sit down. I am not asking."),
                  L("You will feel that tomorrow and the day after. Sit.", R)],
   "dungeon_clear": [L("I have stitched worse in a tent with no light.", R)],
 },
 "silas_rogue": {
   "town_arrive": [L("Three ways out of this square. Two of them are bad."),
                   L("Somebody here is already pricing our boots.", R)],
   "dungeon_clear": [L("Nothing in there was locked. That bothers me more than if it had been.")],
   "boss_down": [L("Check its hands before anyone checks its pockets.", R)],
 },
 "rosa_hunter": {
   "zone_arrive": [L("Give me a day and I will know what hunts here at night.")],
   "boss_down": [L("It was protecting something. They always are.")],
   "dungeon_clear": [L("Nothing in there was hungry. That is not normal and I do not like it.", R)],
 },
 "marco_paladin": {
   "town_arrive": [L("Who keeps order here? Somebody always does. I like to know who.")],
   "boss_down": [L("Nobody will ever be asked to answer for what that thing did.")],
   "close_call": [L("We went in without knowing the ground. That is twice now.", R)],
 },
 "sophia_mage": {
   "dungeon_clear": [L("The air pressure changed four times on the way down. Somebody built that.")],
   "boss_down": [L("It burned at the wrong temperature. I would like to know why.")],
   "zone_arrive": [L("Different air here. Drier. It will change how everything of mine behaves.", R)],
 },
 "ryan_warlock": {
   "town_arrive": [L("Everyone in this square wants something. That is not cynicism, it is just true.")],
   "boss_down": [L("It had a price. Everything does. We simply did not have to pay it.")],
   "dungeon_clear": [L("Somebody was owed something down there, and it was not us.", R)],
 },
 "carolina_shaman": {
   "zone_arrive": [L("The ground here is saying something and it is not pleased.")],
   "town_arrive": [L("They have taken the water from upstream. You can hear where it stops.", R)],
   "dungeon_clear": [L("That place was sick long before anything moved into it.")],
 },
 "amber_druid": {
   "zone_arrive": [L("Overgrazed. Two more seasons of this and the topsoil is gone.")],
   "town_arrive": [L("They are cutting faster than it grows. Somebody should say so.", R)],
   "dungeon_clear": [L("Things were still growing in there. In the dark. I would like to know on what.")],
 },
 "marcus_stormbringer": {
   "zone_arrive": [L("Pressure is dropping. Give it two hours.")],
   "town_arrive": [L("Their roofs are all pitched the same way. That tells you where the wind comes from.", R)],
   "boss_down": [L("Did you feel the air go dead right before it dropped? I want that written down.")],
 },
 "ivan_warrior": {
   "boss_down": [L("Good. That one was worth the walk.")],
   "close_call": [L("You are up. Then it does not count.")],
   "dungeon_clear": [L("Too cold out here. Let us find another hole.", R)],
 },
 "asher_coleman": {
   "town_arrive": [L("Folks look tired here. You want to stop a while?")],
   "dungeon_clear": [L("You did all right in there. You know that, right?")],
   "close_call": [L("Hey. Hey. You are fine. Breathe out first, then in.", R)],
   "boss_down": [L("Somebody ought to say something over it. I will, if nobody minds.", R)],
 },
 "owen_cultist": {
   "dungeon_clear": [L("Count again. I will not move until somebody counts again.")],
   "zone_arrive": [L("There is old workings under this. You can feel it through your boots.")],
   "close_call": [L("That roof was talking for ten seconds before it went. Learn that sound.", R)],
 },
 "mateo_starcaller": {
   "zone_arrive": [L("Clear sky tonight. I will be up. Do not wait on me in the morning.")],
   "town_arrive": [L("Too many lamps here. I cannot see anything that matters.", R)],
   "boss_down": [L("It went quiet at the same moment the moon cleared the ridge. I noticed. I write these down.")],
 },
 "pasang_primalist": {
   "zone_arrive": [L("Slow down. The ground will still be there.")],
   "dungeon_clear": [L("Down is always easier than up. That is when people get hurt.")],
   "close_call": [L("You were tired an hour before that happened. I saw it and said nothing. My fault.", R)],
 },
 "haruto_runemaster": {
   "dungeon_clear": [L("Those marks on the pillars were cut by a hand, not grown. A bad hand, in a hurry.")],
   "boss_down": [L("Whatever was written on it, it did not wash off. It never does.")],
   "town_arrive": [L("Their letters lean left here. Somebody taught the whole town to write.", R)],
 },
 "liam_suncleric": {
   "close_call": [L("Look at me. Talk. Keep talking, I do not care what about.")],
   "dungeon_clear": [L("Everyone out and walking. That is a good night.")],
   "town_arrive": [L("Where would they take a burn case here? Worth knowing before we need it.", R)],
 },
 "marta_tinker": {
   "dungeon_clear": [L("That tunnel was cut by somebody in a hurry and it will come down inside five years.")],
   "boss_down": [L("Loud. I have heard louder and I measured that one too.")],
   "close_call": [L("You were surprised. Do not be surprised. Being surprised means somebody measured wrong.", R)],
 },
 "callum_venomancer": {
   "boss_down": [L("It was frightened the whole time. They always are, and it never helps anybody.")],
   "zone_arrive": [L("Something venomous lives here. I will find out what by tomorrow.")],
   "close_call": [L("That is a clean puncture. If you start sweating, tell me immediately and do not walk.", R)],
 },
 "emre_rogue": {
   "town_arrive": [L("Every shutter on this street locks from the inside. They have had trouble.")],
   "dungeon_clear": [L("Four doors in there and not one of them was built to keep anything out.")],
   "boss_down": [L("It was guarding a room with nothing in it. Somebody emptied that a long time ago.", R)],
 },
 "bakyt_hunter": {
   "zone_arrive": [L("Good ridge. You could work a bird off that.")],
   "town_arrive": [L("No birds over this town. That is worth asking about.", R)],
   "dungeon_clear": [L("Nothing with wings went down there. There is a reason for that.")],
 },
 "henrik_mage": {
   "zone_arrive": [L("Forty below and clear would be a good day. This is neither.")],
   "dungeon_clear": [L("The ice at the back of that was older than the stone around it. That should not be possible.")],
   "boss_down": [L("I would like to go back and measure it before it thaws.", R)],
 },
 "anjali_druid": {
   "town_arrive": [L("Their grain is stored wrong. One wet month and they lose all of it.")],
   "zone_arrive": [L("This soil has been asked for too much for too long.", R)],
   "dungeon_clear": [L("Patience, mostly. That is all that was. It usually is.")],
 },
 "hana_shaman": {
   "zone_arrive": [L("There is water under this. A lot of it, and it is moving.")],
   "close_call": [L("You panicked. Everybody does. Next time go with it, not across it.")],
   "town_arrive": [L("Nobody here can swim. I asked. Nobody.", R)],
 },
 "kesten_the_catalogued": {
   "dungeon_clear": [L("Somebody cut letters into that doorway and nobody has read them in an age.")],
   "town_arrive": [L("No stones here with names on them. A town with no dead is a town that just started.")],
   "boss_down": [L("It will not get a marker. Most things do not. I still think about it.", R)],
 },
}


def main():
    names = {r["recruit_id"]: r["name"].split()[0]
             for r in json.loads((ROOT / "data/npcs/recruits.json").read_text())["recruits"]}
    unknown = set(LINES) - set(names)
    if unknown:
        raise SystemExit(f"banter written for recruits that do not exist: {sorted(unknown)}")

    # THE RULE, ENFORCED. A line that names another companion assumes they are in the party, that the
    # two have met, and that there is a history. None of that is true.
    others = {}
    for rid, blocks in LINES.items():
        for trigger, entries in blocks.items():
            for e in entries:
                for other_id, first in names.items():
                    if other_id == rid:
                        continue
                    if first in e["text"].split() or other_id in e["text"]:
                        others.setdefault(rid, []).append((first, e["text"][:60]))
    if others:
        raise SystemExit("lines naming another companion:\n  " +
                         "\n  ".join(f"{r}: {n} in {t!r}" for r, v in others.items() for n, t in v))

    out = ROOT / "data/banter/lines.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "_notes": "Party banter, authored per character per trigger (never per pair - see "
                  "world/banter_manager.py). A line never names another companion: the recruits are "
                  "strangers who happen to share an employer. Generated by "
                  "tools/build_banter_lines.py; do not hand-edit.",
        "lines": LINES,
    }, indent=2, ensure_ascii=False) + "\n")

    n = sum(len(v) for b in LINES.values() for v in b.values())
    print(f"{n} lines across {len(LINES)} characters")
    missing = set(names) - set(LINES)
    if missing:
        print(f"  no banter yet: {sorted(missing)}")


if __name__ == "__main__":
    main()
