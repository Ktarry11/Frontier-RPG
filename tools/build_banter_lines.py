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
   "town_arrive": [L("Walls, a gate, somebody watching it. I'll sleep tonight.")],
   "dungeon_clear": [L("Everybody walked out. That's the job, that's all the job ever is."),
                     L("Nobody got hurt being clever. I'll take it.", R)],
   "close_call": [L("That's on me. I was a step too far left.")],
   "boss_down": [L("Right. Check your straps before we move.", R)],
 },
 "ama_priest": {
   "town_arrive": [L("There'll be sick people here. There always are.")],
   "close_call": [L("Sit. I'm not asking you."),
                  L("You'll feel that tomorrow, and worse the day after. Sit down.", R)],
   "dungeon_clear": [L("I've stitched worse than that in a tent with no light.", R)],
 },
 "silas_rogue": {
   "town_arrive": [L("Three ways out of this square. Two of them are bad."),
                   L("Somebody here's already pricing our boots.", R)],
   "dungeon_clear": [L("Nothing down there was locked. That bothers me more than if it had been.")],
   "boss_down": [L("Check its hands before anybody checks its pockets.", R)],
 },
 "rosa_hunter": {
   "zone_arrive": [L("Give me a day. I'll know what hunts here at night.")],
   "boss_down": [L("It was guarding something. They always are.")],
   "dungeon_clear": [L("Nothing in there was hungry. That's not normal and I don't like it.", R)],
 },
 "marco_paladin": {
   "town_arrive": [L("Who keeps order here? Somebody does. I like knowing who.")],
   "boss_down": [L("Nobody's ever going to answer for what that thing did.")],
   "close_call": [L("We went in without knowing the ground. That's twice.", R)],
 },
 "sophia_mage": {
   "dungeon_clear": [L("Pressure changed four times on the way down. Somebody built that.")],
   "boss_down": [L("It burned at the wrong temperature. I want to know why.")],
   "zone_arrive": [L("Air's drier here. Everything of mine is going to behave differently.", R)],
 },
 "ryan_warlock": {
   "town_arrive": [L("Everyone in this square wants something. That's not cynicism, it's just true.")],
   "boss_down": [L("That had a price on it. We just didn't have to pay it.")],
   "dungeon_clear": [L("Somebody was owed something down there. Wasn't us.", R)],
 },
 "carolina_shaman": {
   "zone_arrive": [L("Ground here's saying something, and it's not happy.")],
   "town_arrive": [L("They've taken the water upstream. You can hear where it stops.", R)],
   "dungeon_clear": [L("That place was sick long before anything moved into it.")],
 },
 "amber_druid": {
   "zone_arrive": [L("Overgrazed. Two more seasons and the topsoil's gone.")],
   "town_arrive": [L("They're cutting faster than it grows. Somebody should tell them.", R)],
   "dungeon_clear": [L("Things were growing down there. In the dark. On what?")],
 },
 "marcus_stormbringer": {
   "zone_arrive": [L("Pressure's dropping. Give it two hours.")],
   "town_arrive": [L("Every roof here's pitched the same way. That tells you where the wind comes from.", R)],
   "boss_down": [L("Did you feel the air go dead right before it dropped? I want that written down.")],
 },
 "ivan_warrior": {
   "boss_down": [L("Good. That one was worth the walk.")],
   "close_call": [L("You are standing. Then it does not count.")],
   "dungeon_clear": [L("Too cold out here. Find me another hole.", R)],
 },
 "asher_coleman": {
   "town_arrive": [L("Folks look tired here. You wanna stop a while?")],
   "dungeon_clear": [L("You did all right in there. You know that, right?")],
   "close_call": [L("Hey. Hey, you're all right. Breathe out first. Then in.", R)],
   "boss_down": [L("Somebody oughta say somethin' over it. I will, if nobody minds.", R)],
 },
 "owen_cultist": {
   "dungeon_clear": [L("Count again. I'm not moving till somebody counts again.")],
   "zone_arrive": [L("There's old workings under this. You can feel it through your boots.")],
   "close_call": [L("That roof was talking for ten seconds before it went. Learn that sound.", R)],
 },
 "mateo_starcaller": {
   "zone_arrive": [L("Clear sky tonight. I'll be up. Don't wait on me in the morning.")],
   "town_arrive": [L("Too many lamps. I can't see anything that matters.", R)],
   "boss_down": [L("It went quiet the same moment the moon cleared the ridge. I noticed. I write these down.")],
 },
 "pasang_primalist": {
   "zone_arrive": [L("Slow. The ground will still be there.")],
   "dungeon_clear": [L("Down is easier than up. That is when people get hurt.")],
   "close_call": [L("You were tired an hour before that. I saw it, I said nothing. My fault.", R)],
 },
 "haruto_runemaster": {
   "dungeon_clear": [L("Those marks on the pillars were cut, not grown. Bad hand. In a hurry.")],
   "boss_down": [L("Whatever was written on that, it didn't wash off. It never does.")],
   "town_arrive": [L("Their letters lean left here. Somebody taught this whole town to write.", R)],
 },
 "liam_suncleric": {
   "close_call": [L("Look at me. Talk. Keep talking, I don't care what about.")],
   "dungeon_clear": [L("Everyone out and walking. That's a good night, that is.")],
   "town_arrive": [L("Where'd they take a burn case here? Worth knowing before we need it.", R)],
 },
 "marta_tinker": {
   "dungeon_clear": [L("That tunnel was cut by somebody in a hurry. It'll be down inside five years.")],
   "boss_down": [L("Loud. I've heard louder, and I measured that one too.")],
   "close_call": [L("You were surprised. Don't be surprised. Surprised means somebody measured wrong.", R)],
 },
 "callum_venomancer": {
   "boss_down": [L("Poor thing was terrified the whole time. They always are. Doesn't help anyone.")],
   "zone_arrive": [L("Something venomous lives here. I'll have found it by tomorrow.")],
   "close_call": [L("That's a clean puncture. You start sweating, you tell me, and you don't walk.", R)],
 },
 "emre_rogue": {
   "town_arrive": [L("Every shutter on this street locks from the inside. They've had trouble.")],
   "dungeon_clear": [L("Four doors down there, and not one of them built to keep anything out.")],
   "boss_down": [L("It was guarding an empty room. Somebody cleared that out a long time ago.", R)],
 },
 "bakyt_hunter": {
   "zone_arrive": [L("Good ridge. You could work a bird off that.")],
   "town_arrive": [L("No birds over this town. Worth asking why.", R)],
   "dungeon_clear": [L("Nothing with wings went down there. There is a reason.")],
 },
 "henrik_mage": {
   "zone_arrive": [L("Forty below and clear, that's a good day. This is neither.")],
   "dungeon_clear": [L("Ice at the back of that was older than the stone around it. Shouldn't be possible.")],
   "boss_down": [L("I'd like to go back and measure it before it thaws.", R)],
 },
 "anjali_druid": {
   "town_arrive": [L("Their grain's stored wrong. One wet month and they lose the lot.")],
   "zone_arrive": [L("This soil's been asked for too much for too long.", R)],
   "dungeon_clear": [L("Patience, mostly. That's all that was. It usually is.")],
 },
 "hana_shaman": {
   "zone_arrive": [L("There's water under this. Lots of it, and it's moving.")],
   "close_call": [L("You panicked. Everyone does. Next time go with it, not across it.")],
   "town_arrive": [L("Nobody here can swim. I asked around. Not one of them.", R)],
 },
 "kesten_the_catalogued": {
   "dungeon_clear": [L("Somebody cut letters into that doorway. Nobody's read them in an age.")],
   "town_arrive": [L("No stones with names on them here. A town with no dead is a town that just started.")],
   "boss_down": [L("It will not get a marker. Most things do not. I think about that.", R)],
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
