#!/usr/bin/env python3
"""The recruit friendship pilot: Kesten, Adrián and Tarek. Writes data/npcs/bonds.json. Idempotent.

    PYTHONPATH=. python3 tools/build_recruit_bonds.py

Design: claude/recruit_bonds_DESIGN_ONLY.md (Kyle's fifteen answers, 13 Nov 2026). Pilot text:
claude/recruit_pilot_kesten_adrian_tarek.md, rewritten a third time here because Kyle read draft 2
and said "This is also all weirdly AI again. NO ONE talks like this." What he was pointing at, in
the pair banter above all: two lines that trade a neat point and land it, a stage aside telling
you how to read the line ("(He isn't.)"), a closing sentence that sums the person up ("I think
that was the best thing I've ever done on a field"), and a metaphor doing the work a plain
sentence should ("a pump with no seal").

So every line here is something a person would say to somebody they're travelling with. It says
the thing and stops. Contractions, whole sentences, no dashes, no asides.

WHAT IS IN EACH RECORD
  dials     warmth (how fast trust grows), nerve (wipes and zones above them), pride (minding
            their gear being taken), restless (how soon a stint ends). 1.0 is ordinary.
  likes / dislikes   from what the party actually does: dungeon, boss, quest, new_ground,
            undead, demon, beast, grinding, full_party
  stages    what they tell you at each of the five stages, in their own words
  moments   the few places you choose a reply, and what each reply does
  lines     what they say when something happens, each naming its cause
  pairs     banter that only appears after two of them have travelled together a good while

Tarek's goal ending is still Kyle's call (pilot doc, ruling 1), so both of his Sworn texts are
here and `ending` says which one is live. His personal quests are not built yet; Sworn is only
reachable from the test panel until they are.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_tempest_quests import voice_problems     # noqa: E402

OUT = ROOT / "data/npcs/bonds.json"

BONDS = {
    "kesten_the_catalogued": {
        "home": "Kael's Bastion",
        "dials": {"warmth": 0.6, "nerve": 0.9, "pride": 0.3, "restless": 0.7},
        "likes": ["new_ground", "undead", "dungeon"],
        "dislikes": ["grinding"],
        "stages": {
            "stranger": (
                "My name's Kesten. For a while I only had a number, and I picked this name "
                "myself afterwards, so I'd like you to use it. I worked in an archive for "
                "twenty-six years. If I stop in a doorway I'm probably reading something, and "
                "I'll catch you up."),
            "acquaintance": (
                "I'm from Tallinn. I worked at the city archive there, on the third floor, "
                "looking after parish registers and ships' passenger lists. Most people think "
                "that sounds dull but I liked it. The lists tell you who got on a boat and the "
                "registers tell you who came home, and I always knew which box everything was "
                "in."),
            "companion": (
                "When the worlds joined I landed in Tirisfal, and the Scourge took me about "
                "nine days later. They wrote down everyone they took, so for a couple of years "
                "I was a line in their book. When their hold on us broke I walked out with the "
                "others. The elves let me read in Gallery Three now, but they won't let me file "
                "anything."),
            "friend": (
                "I was married. I've got her name written on the first page of my notebook "
                "because I don't trust myself to remember it, and I don't usually tell people "
                "that. I've read my own entry in the Scourge's book a lot of times as well. It "
                "lists what they kept of me and what they threw away, and I've never told "
                "anyone what it says."),
            "sworn": (
                "Her name was Liis, and I can say it now without looking at the notebook. I've "
                "checked every morning for a month. I'm writing down how the Scourge worked "
                "from the inside, because none of the others who came out will do it. When "
                "the first volume's copied out I'd like you to have it, since you're in it."),
        },
        "moments": [
            {"id": "hire", "stage": "stranger", "when": "hire",
             "prompt": "He tells you his name and asks you to use it.",
             "options": [
                 {"text": "Good to meet you, Kesten.", "trust": 4, "joins": True,
                  "reply": "Thank you. I'll get my things."},
                 {"text": "What was your number?", "trust": 0, "joins": False,
                  "reply": "I've already told you what to call me. Come back another day and "
                           "we'll try again."},
             ]},
            {"id": "the_ledger", "stage": "companion", "when": "talk",
             "prompt": "He's just told you about the Scourge's book.",
             "options": [
                 {"text": "What did they keep of you?", "trust": 0,
                  "reply": "Ask me that again when we know each other better."},
                 {"text": "You don't have to tell me any of this.", "trust": 10,
                  "reply": "I know I don't. I'm glad you said it, though."},
                 {"text": "That must have been terrible.", "trust": 0,
                  "reply": "I honestly can't remember what it was like, and that's the part "
                           "that bothers me."},
             ]},
        ],
        "lines": {
            "bored_warning": (
                "We've killed a lot of these now and I haven't had anything new to write down in "
                "a while. Could we go somewhere I haven't been?"),
            "leaving_good": (
                "I've filled a whole notebook on this trip and I need to get back to the Bastion "
                "and copy it out before the damp gets into it. Come and find me there when you "
                "want me."),
            "leaving_bored": (
                "I'm going back to the Bastion. We've been doing the same thing for a while and "
                "I'd like to get my notes in order. Come and find me when you're going "
                "somewhere new."),
            "after_wipe": (
                "That's the second time we've died on this floor. I'd rather it stayed at two."),
            "wipe_warning": (
                "We keep dying in here. If it happens again I'll finish this run with you, but "
                "then I'm taking a break."),
            "wipe_leave": (
                "I'll walk out of here with you now we're done, but I'm not coming back in for a "
                "while. I'll be at the Bastion."),
            "zone_warning": (
                "Everything out here kills us in two hits. I'd like to go somewhere closer to my "
                "level before it gets any worse."),
            "zone_leave": (
                "I'm going to stop here. That place is too much for me right now, and I'd rather "
                "wait at the Bastion than die out there again."),
            "gear_refuse": (
                "I'd rather keep that for now, if you don't mind. We don't know each other well "
                "enough yet."),
            "gear_taken": (
                "You can take it. It was issued to me and it never really felt like mine. I'll "
                "manage without one for now."),
            "gear_short": (
                "I'm still missing the piece you took. I'd like something back in that slot "
                "when you get the chance."),
            "gear_upgrade": (
                "This is better than what I had. Thank you, I'm going to write down who gave it "
                "to me."),
            "back": "The copying's done. Tell me what you've been doing since I left.",
            "send_word": "Kesten has sent word from Kael's Bastion. He's finished his copying and "
                         "he's ready when you are.",
            "walkout_talk": (
                "I wrote down what happened in there and I wrote down that I walked out. I'll "
                "come back with you, but I'd like you to read what I wrote first."),
            "neglect": "It's been a long time. I'd started to think you'd forgotten about me.",
            "asked_to_stay": "All right, one more. I'll hold you to it.",
            "on_break": "Kesten is away copying out his notes. Come back after you've been out "
                        "for a while.",
        },
    },

    "adrian_templar": {
        "home": "Astranaar",
        "dials": {"warmth": 1.4, "nerve": 0.6, "pride": 0.8, "restless": 0.8},
        "likes": ["dungeon", "boss", "full_party"],
        "dislikes": ["grinding", "quest_abandoned"],
        "first_stint_short": True,
        "stages": {
            "stranger": (
                "I'm Adrián, and if you tell me the plan once and tell it properly, I won't "
                "need to ask again. If I think you've got something wrong I'll say so, and I'd like you "
                "to do the same for me."),
            "acquaintance": (
                "Back home I was a football referee for twelve years, in the second division in "
                "Spain, and before that I was a PE teacher. Both jobs were mostly people being "
                "annoyed with me, and I liked them anyway. I've still got my whistle in my left "
                "pocket, but I haven't blown it since I got here."),
            "companion": (
                "I lived over a bicycle shop in Valladolid. My parents died within a year of "
                "each other when I was twenty-eight, and I haven't got any brothers or sisters. "
                "I worked most weekends, so after a while people stopped inviting me to things. "
                "When all this happened I went and checked the lists for people I knew, and it "
                "didn't take long."),
            "friend": (
                "People here come and get me for meals and the watch and cards, and I always go "
                "and I enjoy it. But I've never once walked up to a fire and sat down without "
                "somebody waving me over first. I tell myself I don't want to get in the way. I "
                "think really I'm waiting for somebody to tell me to leave."),
            "sworn": (
                "Last night I sat down at the fire before anybody waved me over, and nobody "
                "said anything about it. Somebody passed me the bread. I've been thinking about "
                "it all day."),
        },
        "moments": [
            {"id": "first_goodbye", "stage": "stranger", "when": "first_stint_end",
             "prompt": "At the end of his first trip with you, he gets ready to go.",
             "line": "I expect you've got other people you'd rather bring, so I'll get out of "
                     "your way.",
             "options": [
                 {"text": "I'd like you to stay with us, if you're willing.", "trust": 14,
                  "stays": True, "flag": "asked_to_stay",
                  "reply": "Oh, yes, all right. Thank you for asking."},
                 {"text": "That's up to you. Go if you want to.", "trust": 0,
                  "reply": "I'll head back to Astranaar, then. It was good working with you."},
             ]},
            {"id": "first_wipe", "stage": "any", "when": "wipe",
             "prompt": "After the wipe, he tells you what went wrong.",
             "line": "We lost that because we pulled too many of them at once.",
             "options": [
                 {"text": "You're right, that one was my call.", "trust": 6, "mood": 5,
                  "reply": "Fair enough, same plan and we go slower."},
                 {"text": "Nobody could have seen that coming.", "trust": 0, "mood": -6,
                  "reply": "I did see it coming. I said so at the door."},
             ]},
        ],
        "lines": {
            "bored_warning": (
                "Can you tell me what we're doing this for? If there's a reason I'm happy to "
                "keep going, I'd just like to know what it is."),
            "leaving_good": "That was good work and I enjoyed it. I'll be in Astranaar when you "
                            "want me again.",
            "leaving_bored": (
                "I'm going to head back to Astranaar. I don't think we're getting anything done "
                "out here, and I don't want to keep killing things for no reason."),
            "after_wipe": "We lost that one at the pull. I'd keep the same plan and go slower.",
            "wipe_warning": (
                "That's a lot of wipes. I'll stay until the end of this run because I said I "
                "would, but I'll need a break after."),
            "wipe_leave": (
                "I said I'd see that one through and I have. Now I need some time where nobody "
                "dies in front of me. I'll be in Astranaar."),
            "zone_warning": (
                "We're out of our depth here. I'll stand wherever you put me, but I don't think "
                "this is fair on any of us."),
            "zone_leave": (
                "I'm stopping here. I told you I didn't think it was fair, and I still don't. "
                "I'll be in Astranaar."),
            "gear_refuse": (
                "I'd rather hold on to that. If somebody else needs it more, tell me who and "
                "I'll give it to them myself."),
            "gear_taken": (
                "You've left me without one and it's sitting in your bag. Can you tell me why?"),
            "gear_short": "I'm still short a piece. I'd like that sorted before the next fight.",
            "gear_to_ally": "He needs that more than I do, so that was the right call.",
            "gear_upgrade": "Is that for me? Thank you, I'll look after it.",
            "quest_abandoned": (
                "We told her we'd do that. I'd have liked to go back and tell her we weren't "
                "going to."),
            "back": "Good to see you. Where do you want me?",
            "send_word": "Adrián has sent word from Astranaar. He's ready whenever you want "
                         "him.",
            "walkout_talk": (
                "I left because I was angry, and I should have told you that before I went. "
                "Some of it was my fault and some of it was yours. Can we start again?"),
            "neglect": (
                "I thought you probably had a full group already. You don't need to apologise, "
                "I'm glad you came back."),
            "asked_to_stay": "All right, one more, and then we'll see.",
            "on_break": "Adrián has gone back to Astranaar for a while. Come back after you've "
                        "done a few more jobs.",
        },
    },

    "tarek_templar": {
        "home": "Ashenvale East",
        "dials": {"warmth": 1.0, "nerve": 0.85, "pride": 0.3, "restless": 1.3},
        "likes": ["undead", "demon", "quest"],
        "dislikes": ["grinding", "beast"],
        "ending": "bad",
        "stages": {
            "stranger": (
                "I'm Tarek, and if you tell me plainly where you need me, I'll be there. I look after "
                "the water around here, so if we pass a stream and I stop for a minute, I'm "
                "only checking it."),
            "acquaintance": (
                "I was a civil engineer in Cairo for fourteen years, and it was all water. "
                "Nobody thanks you for water until it stops coming out of the tap. I've sunk "
                "three wells since I got here and one of them has already failed. I can tell "
                "you why if you've got an hour and something to draw with."),
            "companion": (
                "This might sound strange, but this world has been better for me than the last "
                "one. Whatever's poisoning the water here is something I can see and fight, and "
                "I never had that before. Nobody here has asked me a question I had to lie "
                "about. The orcs have offered me a title twice and I've turned it down both "
                "times."),
            "friend": (
                "His name is Omar. He taught chemistry and he laughed at everything, including "
                "me. We were careful for six years, and then one time at a wedding we weren't, "
                "and somebody made a phone call. I was out of the country within a week. He had "
                "his parents and his sister and no money, so he told me to go, and that was the "
                "last time we talked. I go down to Astranaar every few months and read the Cairo "
                "lists. He's never been on them, and I know that doesn't tell me much."),
            "sworn_bad": (
                "Nadia wrote back. Omar got his class out into the school yard when it happened, "
                "and he didn't make it out himself. I cut his name into the lining of the fourth "
                "well, under the waterline. Nobody will ever read it, but I know it's there. "
                "I've stopped going down to the lists."),
            "sworn_soft": (
                "Nadia wrote back. Omar's alive and teaching in a town a long way south, and he "
                "asked her not to tell me where. I'm keeping the letter. I've stopped going down "
                "to the lists, and I go and sit by the fourth well when I want to think about "
                "him."),
        },
        "moments": [
            {"id": "hire", "stage": "stranger", "when": "hire",
             "prompt": "Before he says yes, he asks what the work actually is.",
             "options": [
                 {"text": "We kill what needs killing, and we get paid for it.", "trust": 4,
                  "joins": True, "reply": "Good, I can do that."},
                 {"text": "We're going to put the world right.", "trust": 0, "joins": False,
                  "reply": "Come back when you can tell me what the work is."},
             ]},
            {"id": "omar", "stage": "friend", "when": "talk",
             "prompt": "He's just told you about Omar.",
             "options": [
                 {"text": "He might still be out there somewhere.", "trust": 0,
                  "reply": "He might be. I've thought about that a lot more than you have."},
                 {"text": "Tell me about him.", "trust": 16,
                  "reply": "He used to mark my drawings in red pen, like they were homework. "
                           "He said somebody had to. I haven't talked about him like this in "
                           "a long time."},
                 {"text": "(Stay and keep him company.)", "trust": 12,
                  "reply": "Thanks for sitting with me."},
             ]},
        ],
        "lines": {
            "bored_warning": (
                "These animals haven't done anything to us. If we need the hides then tell me "
                "and I'll stop asking."),
            "leaving_good": (
                "The east spring needs looking at and it won't wait, so I'll be gone for a bit. "
                "You know the road to Splintertree if you want me."),
            "leaving_bored": (
                "I'm going to go and check on the wells. We've been killing things that didn't "
                "need killing for a while now."),
            "after_wipe": "I was slow on the second one. I'll stand further left this time. "
                          "Shall we go again?",
            "wipe_warning": (
                "That's the same thing going wrong again and again. We'll finish this one, and "
                "then I need to go home for a bit."),
            "wipe_leave": (
                "We're done, so I'm going home. When something fails the same way that many "
                "times it needs redrawing, and I can't do that in here."),
            "zone_warning": (
                "I don't mind hard work, but this is too much. We need to go somewhere we can "
                "actually handle."),
            "zone_leave": (
                "I'm stopping here. It's too dangerous out there for me right now. I'll be at "
                "Splintertree."),
            "gear_refuse": "I'd like to keep that for now, if that's all right.",
            "gear_taken": "You can have it. I'll need something in that slot before long, "
                          "though.",
            "gear_short": "I'm still missing that piece you took. It's starting to show.",
            "gear_upgrade": "That's well made. Somebody took real care over it. Thank you.",
            "back": "The spring's holding, so I'm yours for a while.",
            "send_word": "Tarek has sent word from Splintertree. The wells are fine and he's "
                         "ready to come out again.",
            "walkout_talk": (
                "I left before I said something I'd regret. I've thought about it since. Tell me "
                "what you'd do differently and I'll tell you what I would."),
            "neglect": (
                "I was starting to wonder if you'd forgotten the road up here. Come and sit "
                "down. Have you eaten?"),
            "asked_to_stay": "All right, one more trip. Then the wells.",
            "on_break": "Tarek is out checking his wells. Come back after you've been busy for a "
                        "while.",
        },
    },
}

PAIRS = [
    {"a": "tarek_templar", "b": "adrian_templar", "feel": "like", "lines": [
        ("tarek_templar", "You know you could be a bit nicer when you explain the plan."),
        ("adrian_templar", "I know I could, and I'll try."),
        ("adrian_templar", "Tarek keeps asking me if I've eaten. I don't mind. I do forget "
                           "sometimes."),
    ]},
    {"a": "kesten_the_catalogued", "b": "tarek_templar", "feel": "like", "lines": [
        ("tarek_templar", "You were stood at that doorway for ten minutes. What did it say?"),
        ("kesten_the_catalogued", "It said who paid for the door and how much it cost. I'll "
                                  "show you the next one."),
    ]},
    {"a": "kesten_the_catalogued", "b": "adrian_templar", "feel": "grate_then_like", "lines": [
        ("adrian_templar", "We said four pulls and that was five."),
        ("kesten_the_catalogued", "I counted five as well. Next time I'll tell you before we go "
                                  "over."),
    ]},
]

#: phrases that were in draft 2 and that Kyle quoted back; none may come back
BANNED = [r"\(he isn'?t\.?\)", r"since my mother", r"best thing I've ever done",
          r"pump with no seal", r"file you under", r"on a tuesday"]


def texts():
    for rid, b in BONDS.items():
        for k, t in b["stages"].items():
            yield f"{rid} stage {k}", t
        for k, t in b["lines"].items():
            yield f"{rid} line {k}", t
        for m in b["moments"]:
            if m.get("line"):
                yield f"{rid} moment {m['id']}", m["line"]
            for o in m["options"]:
                yield f"{rid} reply {m['id']}", o["reply"]
    for p in PAIRS:
        for rid, t in p["lines"]:
            yield f"pair {p['a']}/{p['b']}", t


def main():
    bad = []
    for where, t in texts():
        bad += [f"{where}: {x}" for x in voice_problems(t)]
        if "—" in t or " - " in t:
            bad.append(f"{where}: a dash")
        for rx in BANNED:
            if re.search(rx, t, re.I):
                bad.append(f"{where}: draft 2 phrase {rx}")
    recruits = {r["recruit_id"] for r in json.loads(
        (ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))["recruits"]}
    for rid in BONDS:
        if rid not in recruits:
            bad.append(f"{rid}: not a recruit")
    if bad:
        print("FAILED:")
        for b in bad:
            print("  -", b)
        return 1
    OUT.write_text(json.dumps({"_about": "Recruit friendship. Written by tools/build_recruit_bonds.py; "
                                         "read by world/bond_manager.py.",
                               "bonds": BONDS, "pairs": PAIRS}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    print(f"{len(BONDS)} recruits, {sum(1 for _ in texts())} lines -> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
