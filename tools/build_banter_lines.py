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


def L(text, kind=O, topic=None):
    out = {"text": text, "kind": kind}
    if topic:
        out["topic"] = topic
    return out


# ------------------------------------------------------------------------------------------------
# SHARED EARTH TOPICS. Kyle, 29 Oct 2026: "lets give characters the option to back and forth with
# each other WHEN together in a group. Like it'd be cool if Tarek mentions back home and kouroush
# mentions his time in egypt. Players are integrated from earth, all players are."
#
# This is the one thing these strangers genuinely have in common, and it is what lets them have a
# real exchange WITHOUT breaking the independence rule. They never met and they have no history
# here - but they both remember a planet, so one can answer the other's subject. A topical reply
# answers the SUBJECT and never names or addresses the speaker, which keeps qa_banter's no-naming
# check intact while making the beat read as a conversation.
#
# Authored per character per topic, never per pair: 44 companions is 946 pairs and Kyle has said
# 50+, so anything quadratic was dead before it started. Adding a character is still one block.
#
# CITIES    somebody names where they are from; somebody else has been there, or has their own
# NIGHT     people whose working life happened between midnight and dawn
# COLD      people who worked outdoors in weather that could kill them
# WATER     people whose job was water - rivers, the sea, a quay
# FIRE      people for whom fire was a tool rather than a threat
# MEASURE   people paid to be exact, who find this world's casual estimates maddening
# ------------------------------------------------------------------------------------------------
CITIES, NIGHT, COLD, WATER, FIRE, MEASURE = (
    "cities", "night_work", "the_cold", "water", "fire", "measure")


LINES = {
 "dan_warrior": {
   "town_arrive": [L("Walls, a gate, somebody watching it. I'll sleep tonight.")],
   "dungeon_clear": [L("Everybody walked out. That's the job, that's all the job ever is."),
                     L("Nobody got hurt being clever. I'll take it.", R)],
   "close_call": [L("That's on me. I was a step too far left.")],
   "boss_down": [L("Right. Check your straps before we move.", R)],
   "zone_arrive": [L("Ground's soft on the left. Walk the right side.")],
 },
 "ama_priest": {
   "town_arrive": [L("There'll be sick people here. There always are.")],
   "close_call": [L("Sit. I'm not asking you."),
                  L("You'll feel that tomorrow, and worse the day after. Sit down.", R)],
   "dungeon_clear": [L("I've stitched worse than that in a tent with no light.", R)],
   "boss_down": [L("Anyone bleeding who hasn't said so? That's most of you, usually.", R)],
 },
 "silas_rogue": {
   "town_arrive": [L("Three ways out of this square. Two of them are bad."),
                   L("Somebody here's already pricing our boots.", R)],
   "dungeon_clear": [L("Nothing down there was locked. That bothers me more than if it had been.")],
   "boss_down": [L("Check its hands before anybody checks its pockets.", R)],
   "zone_arrive": [L("Two ways out of here that I can see. I like to know.")],
 },
 "rosa_hunter": {
   "zone_arrive": [L("Give me a day. I'll know what hunts here at night.")],
   "boss_down": [L("It was guarding something. They always are.")],
   "dungeon_clear": [L("Nothing in there was hungry. That's not normal and I don't like it.", R)],
   "town_arrive": [L("Something's been hunting close to this place. The dogs here are wrong.")],
 },
 "marco_paladin": {
   "town_arrive": [L("Who keeps order here? Somebody does. I like knowing who.")],
   "boss_down": [L("Nobody's ever going to answer for what that thing did.")],
   "close_call": [L("We went in without knowing the ground. That's twice.", R)],
   "zone_arrive": [L("Twelve years I was the one people looked for. Hard habit.")],
 },
 "sophia_mage": {
   "dungeon_clear": [L("Pressure changed four times on the way down. Somebody built that.")],
   "boss_down": [L("It burned at the wrong temperature. I want to know why.")],
   "zone_arrive": [L("Air's drier here. Everything of mine is going to behave differently.", R)],
   "close_call": [L("That burned hotter than it should have. I want to know why.", R)],
 },
 "ryan_warlock": {
   "town_arrive": [L("Everyone in this square wants something. That's not cynicism, it's just true.")],
   "boss_down": [L("That had a price on it. We just didn't have to pay it.")],
   "dungeon_clear": [L("Somebody was owed something down there. Wasn't us.", R)],
   "zone_arrive": [L("Everything out here costs something. At least it says so up front.")],
 },
 "carolina_shaman": {
   "zone_arrive": [L("Ground here's saying something, and it's not happy.")],
   "town_arrive": [L("They've taken the water upstream. You can hear where it stops.", R)],
   "dungeon_clear": [L("That place was sick long before anything moved into it.")],
   "boss_down": [L("It wasn't evil. It was hungry and somebody put it here.", R)],
 },
 "amber_druid": {
   "zone_arrive": [L("Overgrazed. Two more seasons and the topsoil's gone.")],
   "town_arrive": [L("They're cutting faster than it grows. Somebody should tell them.", R)],
   "dungeon_clear": [L("Things were growing down there. In the dark. On what?")],
   "close_call": [L("Sit down before you fall down. I've watched people walk off worse and not get up.", R)],
 },
 "marcus_stormbringer": {
   "zone_arrive": [L("Pressure's dropping. Give it two hours.")],
   "town_arrive": [L("Every roof here's pitched the same way. That tells you where the wind comes from.", R)],
   "boss_down": [L("Did you feel the air go dead right before it dropped? I want that written down.")],
   "dungeon_clear": [L("Pressure dropped in there. I felt it in my teeth.", R)],
 },
 "ivan_warrior": {
   "boss_down": [L("Good. That one was worth the walk.")],
   "close_call": [L("You are standing. Then it does not count.")],
   "dungeon_clear": [L("Too cold out here. Find me another hole.", R)],
   "town_arrive": [L("Somewhere here sells food. That's all I want from a town.")],
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
   "boss_down": [L("Listen to the roof a minute before anybody celebrates.")],
 },
 "mateo_starcaller": {
   "zone_arrive": [L("Clear sky tonight. I'll be up. Don't wait on me in the morning.")],
   "town_arrive": [L("Too many lamps. I can't see anything that matters.", R)],
   "boss_down": [L("It went quiet the same moment the moon cleared the ridge. I noticed. I write these down.")],
   "close_call": [L("Fourteen years I watched a sky that never answered. Now it answers and it's rude.", R)],
 },
 "pasang_primalist": {
   "zone_arrive": [L("Slow. The ground will still be there.")],
   "dungeon_clear": [L("Down is easier than up. That is when people get hurt.")],
   "close_call": [L("You were tired an hour before that. I saw it, I said nothing. My fault.", R)],
   "town_arrive": [L("Beds. Good. Nobody climbs well tired.")],
 },
 "haruto_runemaster": {
   "dungeon_clear": [L("Those marks on the pillars were cut, not grown. Bad hand. In a hurry.")],
   "boss_down": [L("Whatever was written on that, it didn't wash off. It never does.")],
   "town_arrive": [L("Their letters lean left here. Somebody taught this whole town to write.", R)],
   "zone_arrive": [L("The marks change out here. Same hand did them, though. You can see it.")],
 },
 "liam_suncleric": {
   "close_call": [L("Look at me. Talk. Keep talking, I don't care what about.")],
   "dungeon_clear": [L("Everyone out and walking. That's a good night, that is.")],
   "town_arrive": [L("Where'd they take a burn case here? Worth knowing before we need it.", R)],
   "boss_down": [L("Right - who's hurt and lying about it? Someone always is.", R)],
 },
 "marta_tinker": {
   "dungeon_clear": [L("That tunnel was cut by somebody in a hurry. It'll be down inside five years.")],
   "boss_down": [L("Loud. I've heard louder, and I measured that one too.")],
   "close_call": [L("You were surprised. Don't be surprised. Surprised means somebody measured wrong.", R)],
   "town_arrive": [L("Nineteen years of blasting. I've never once jumped. People find that rude.")],
 },
 "callum_venomancer": {
   "boss_down": [L("Poor thing was terrified the whole time. They always are. Doesn't help anyone.")],
   "zone_arrive": [L("Something venomous lives here. I'll have found it by tomorrow.")],
   "close_call": [L("That's a clean puncture. You start sweating, you tell me, and you don't walk.", R)],
   "dungeon_clear": [L("Nothing in there was venomous. Bit disappointing, honestly.", R)],
 },
 "emre_rogue": {
   "town_arrive": [L("Every shutter on this street locks from the inside. They've had trouble.")],
   "dungeon_clear": [L("Four doors down there, and not one of them built to keep anything out.")],
   "boss_down": [L("It was guarding an empty room. Somebody cleared that out a long time ago.", R)],
   "zone_arrive": [L("Thirty doors a week in the bazaar. None of them stayed shut either.")],
 },
 "bakyt_hunter": {
   "zone_arrive": [L("Good ridge. You could work a bird off that.")],
   "town_arrive": [L("No birds over this town. Worth asking why.", R)],
   "dungeon_clear": [L("Nothing with wings went down there. There is a reason.")],
   "close_call": [L("You went too far from the rest. A bird that does that doesn't come back.", R)],
 },
 "henrik_mage": {
   "zone_arrive": [L("Forty below and clear, that's a good day. This is neither.")],
   "dungeon_clear": [L("Ice at the back of that was older than the stone around it. Shouldn't be possible.")],
   "boss_down": [L("I'd like to go back and measure it before it thaws.", R)],
   "town_arrive": [L("Warm here. I spent twenty years at forty below and I still don't trust warm.")],
 },
 "anjali_druid": {
   "town_arrive": [L("Their grain's stored wrong. One wet month and they lose the lot.")],
   "zone_arrive": [L("This soil's been asked for too much for too long.", R)],
   "dungeon_clear": [L("Patience, mostly. That's all that was. It usually is.")],
   "close_call": [L("You pushed past where you had anything left. A field does that once and then it's gone.", R)],
 },
 "hana_shaman": {
   "zone_arrive": [L("There's water under this. Lots of it, and it's moving.")],
   "close_call": [L("You panicked. Everyone does. Next time go with it, not across it.")],
   "town_arrive": [L("Nobody here can swim. I asked around. Not one of them.", R)],
   "dungeon_clear": [L("Everyone came out. On the beach that's the whole scoreboard.", R)],
 },
 "kesten_the_catalogued": {
   "dungeon_clear": [L("Somebody cut letters into that doorway. Nobody's read them in an age.")],
   "town_arrive": [L("No stones with names on them here. A town with no dead is a town that just started.")],
   "boss_down": [L("It will not get a marker. Most things do not. I think about that.", R)],
   "zone_arrive": [L("Good stone here. Wasted on whatever built that.")],
 },

 # ---------------------------------------------------------------- wave two (19)
 "tarek_templar": {
   "town_arrive": [L("Cairo had a street like this. Narrower. Louder. Better bread.", O, CITIES)],
   "dungeon_clear": [L("That carving by the door was cut by someone who was good at it.", O),
                     L("Nothing in there was looked after. That's what I keep noticing.", R)],
   "close_call": [L("I was slow. I'm always slow, but that was slower than I am.")],
   "zone_arrive": [L("Somebody made this road. People forget roads are made.")],
 },
 "kourosh_mage": {
   "town_arrive": [L("I spent eight days in Alexandria once, auditing a shipping firm. I've thought about those eight days more than the twelve years around them.", R, CITIES),
                   L("Tehran was louder than this and I could price every risk in it.", O, CITIES)],
   "boss_down": [L("Within tolerance. I had it at about one in nine against us.", O, MEASURE)],
   "close_call": [L("That was outside my estimate. I'll revise it.", R, MEASURE)],
   "zone_arrive": [L("I priced risk for twelve years. This place would have bankrupted me.")],
 },
 "fiona_witchhunter": {
   "zone_arrive": [L("Weather's coming off that water. Two hours, maybe three.", O, WATER)],
   "close_call": [L("Count your people. Do it now, not when we get in.")],
   "boss_down": [L("Fine. Nobody under it when it dropped, which is the only bit I care about.", R)],
   "town_arrive": [L("Three weeks on, three weeks off. I never did learn what to do with a town.")],
 },
 "pavlo_knight": {
   "zone_arrive": [L("Long road. Good. I'm worse when we stop.")],
   "town_arrive": [L("Lviv, when I was home, which was sixty nights a year. I wasn't good at being home.", O, CITIES)],
   "dungeon_clear": [L("One way in. One way out. I like a place like that.", R)],
   "close_call": [L("You stopped. Don't stop. Stopping is what gets you.", R)],
 },
 "junseo_reaper": {
   "dungeon_clear": [L("Closed spaces don't bother me. I welded inside hulls nobody had opened yet.", O, NIGHT)],
   "boss_down": [L("Good. Check your straps, check the ground, then we move.", R)],
   "zone_arrive": [L("Night shift suited me. The steel moves less when it's cool.", O, NIGHT)],
   "town_arrive": [L("Ulsan was a shipyard and a city pretending it wasn't. This is honest, at least.", O, CITIES)],
 },
 "minh_chronomancer": {
   "close_call": [L("You were going down a half-second before you knew it. I heard it.")],
   "town_arrive": [L("Listen. That gate hinge is a whole tone flat and there's nobody here but me can hear it.", O, MEASURE)],
   "boss_down": [L("A fraction early is the entire trade. A fraction late is a funeral.", R, MEASURE)],
   "zone_arrive": [L("Everything here is slightly out of tune and I'm the only one it bothers.")],
 },
 "alonso_pyromancer": {
   "boss_down": [L("Fire'll do what you ask if you ask properly. Twenty years and it never once surprised me.", O, FIRE)],
   "close_call": [L("Burns I can do. Burns are the easy part, which nobody believes.", R)],
   "town_arrive": [L("Guadalajara. Three benches and a furnace we never let go out.", O, CITIES)],
   "dungeon_clear": [L("Cold in there. I don't like a place with no fire in it.", R)],
 },
 "delroy_witchdoctor": {
   "town_arrive": [L("Somebody here's up at four making bread. There always is. I'll find them.", O, NIGHT)],
   "dungeon_clear": [L("Everybody gets something and nobody waits long. Same as any morning.", R)],
   "zone_arrive": [L("Thirty-one years I was awake when my city wasn't. I never saw it in daylight.", R, NIGHT)],
   "close_call": [L("Sit down and drink it. No, I'm not telling you what is in it.")],
   "boss_down": [L("Sit down and eat something. You'll argue, and then you'll do it.", R)],
 },
 "imelda_primalist": {
   "close_call": [L("Hands up. Not for show - up, where they do something.")],
   "boss_down": [L("I know how it looks. I hit it and you felt better. I can't explain it either.", R)],
   "zone_arrive": [L("The quay at five in the morning was louder than this.", O, NIGHT)],
   "town_arrive": [L("Somebody here fights for money. There always is. I'll find them.")],
 },
 "tomas_warrior": {
   "zone_arrive": [L("Tell me where you want me before it starts. Not during. Never during.")],
   "dungeon_clear": [L("Nothing fell on anybody. That's a good day by my old standards.", R)],
   "town_arrive": [L("Prague had better scaffolding than this and I say that with love.", O, CITIES)],
   "boss_down": [L("Check above you before you check the body. Always above you.", R)],
 },
 "eino_barbarian": {
   "zone_arrive": [L("This is warm. I'm not complaining. I'm noticing.", O, COLD)],
   "boss_down": [L("It's dead. We can go.", R)],
   "close_call": [L("You're fine. Walk it off or don't, but decide.")],
   "town_arrive": [L("I built a cabin badly on purpose so I could keep fixing it. I miss it.")],
 },
 "ziad_felsworn": {
   "boss_down": [L("I felt that one coming eight bars out. You learn it in a dark room.")],
   "town_arrive": [L("Beirut at two in the morning, four nights a week. This is quieter and I'm not sure that's better.", O, NIGHT)],
   "close_call": [L("Do not follow me in next time. That isn't modesty.", R)],
   "dungeon_clear": [L("Good room for sound, that. Wasted on whatever was living in it.", R)],
 },
 "pieter_guardian": {
   "boss_down": [L("Lovely. Who's next?")],
   "zone_arrive": [L("Look at that ground. Flat, drained, nobody cutting it. Criminal.")],
   "dungeon_clear": [L("Twenty-two years I watched other people run onto a field I made. Not any more.", R, CITIES)],
   "town_arrive": [L("Twenty-two years cutting a field nobody thanked me for. I'd do it again.", O, CITIES)],
 },
 "esteban_bloodmage": {
   "close_call": [L("I have it written down. What it cost me, exactly, to the drop.", O, MEASURE)],
   "boss_down": [L("Exposure's a trade, not a sin. The trick is knowing the number.", R, MEASURE),
                 L("Everybody here estimates. I was paid for twenty years not to.", R, MEASURE)],
   "town_arrive": [L("Rosario. Twenty years, three corridors, the same lead apron.", O, CITIES)],
   "zone_arrive": [L("Everyone here guesses at the dose. It's the only thing that frightens me.")],
 },
 "kiet_rogue": {
   "town_arrive": [L("Nine of the locks on this street are bad and two of them are insulting.")],
   "dungeon_clear": [L("There was a socket in that wall meant to take something. It isn't there now.", R)],
   "zone_arrive": [L("I'm quiet and I'm not brave. Different things.")],
   "close_call": [L("You went in loud. I'd have gone in quiet, but nobody asked.", R)],
 },
 "stelios_necromancer": {
   "dungeon_clear": [L("Nobody wrote any of that down. Four hundred men in my library and every one of them had a record.", O, NIGHT)],
   "town_arrive": [L("Corinth. A prison, a card catalogue, and four hundred readers who weren't supposed to matter.", O, CITIES)],
   "boss_down": [L("It's only angry about being forgotten. Most of them are.", R)],
   "zone_arrive": [L("Nobody has catalogued any of this. It's a scandal and I'm the only one scandalised.")],
 },
 "ratih_ranger": {
   "zone_arrive": [L("That water was higher. Look at the line on the rock - that isn't this year.", O, WATER)],
   "boss_down": [L("I shot from where the ground told me to stand. It usually does.", R)],
   "dungeon_clear": [L("I walked catchments for fifteen years. Water keeps better records than people.", R, WATER)],
   "town_arrive": [L("Nobody here has walked the whole catchment. I can tell.", O, MEASURE)],
   "close_call": [L("The ground told you that was bad footing. You weren't listening.", R)],
 },
 "driss_shaman": {
   "zone_arrive": [L("Wind's off. Not wrong - off. Sixteen years I listened to machines tell me that.", O, COLD)],
   "town_arrive": [L("Tangier, on a ridge where it didn't stop blowing from October to March.", O, CITIES),
                   L("Up on that ridge you could see the whole city and never have to be in it.", R, CITIES)],
   "boss_down": [L("It answered me. That part I'm still not used to.", R)],
   "dungeon_clear": [L("No air moving in there at all. I hated it.", R)],
 },
 "marisol_priest": {
   "boss_down": [L("Somebody should say something over it. Nobody will. I might.")],
   "close_call": [L("I've sat with more dead people than everyone here together. You're not one of them.", R)],
   "town_arrive": [L("Medellin. Twenty-four years, and a decade in the middle I don't discuss.", O, CITIES)],
   "dungeon_clear": [L("Somebody died in that room a long time ago and nobody marked it.", R)],
 },
}


def main():
    names = {r["recruit_id"]: r["name"].split()[0]
             for r in json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]}
    unknown = set(LINES) - set(names)
    if unknown:
        raise SystemExit(f"banter written for recruits that don't exist: {sorted(unknown)}")

    # THE RULE, ENFORCED. A line that names another companion assumes they're in the party, that the
    # two have met, and that there's a history. None of that's true.
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
                  "tools/build_banter_lines.py; don't hand-edit.",
        "lines": LINES,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n = sum(len(v) for b in LINES.values() for v in b.values())
    print(f"{n} lines across {len(LINES)} characters")
    missing = set(names) - set(LINES)
    if missing:
        print(f"  no banter yet: {sorted(missing)}")


if __name__ == "__main__":
    main()
