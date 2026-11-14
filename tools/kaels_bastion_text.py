#!/usr/bin/env python3
"""Kael's Bastion, written again in plain speech. Idempotent.

    PYTHONPATH=. python3 tools/kaels_bastion_text.py

Kyle, 14 Nov 2026: "I was in Kael's bastion and the text there is really lackluster." It was. The
greetings were people reciting their job title, the quests ended on lines written to land ("One
organism.", "Four hundred and ten."), an earlier pass had cut the counts off the front of five
quests ("Sets. That is three weeks of the Archive's work"), and one quest repeated its directions
three times. The frostpine quest also sent you to the wrong place: frostpine doesn't grow in the
Underdark, the nearest is Eastern Hillsbrad.

Writes three overlays, which the game lays over the generated files:
  data/quests/text/zzz_kaels_bastion.json        the nine Bastion quests
  data/npcs/greetings/kaels_bastion.json         the thirteen townsfolk
  data/npcs/vendor_greetings/kaels_bastion.json  the six shopkeepers

The rules (Kyle, 13 Nov 2026: "NO ONE talks like this"): say what's wrong, where to go and what to
bring back, then thank them and stop. Contractions, no dashes, no one-word sentences, no line that
sums somebody up.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_tempest_quests import voice_problems     # noqa: E402

QUESTS = {
    "kb_arrival": dict(
        title="Signing In at the Gate",
        description="Go up to the Long Shelf, the second gallery of Kael's Bastion, then come back "
                    "to Gate-Warden Vessaria.",
        accept_text=(
            "Everyone who comes through this gate gets written into the Codex, and I've written "
            "you in. When you leave I'll ask what you're taking out with you, so keep track of "
            "anything you pick up in the cavern.\n\n"
            "Go up the main walkway to the Long Shelf. It's the second gallery, the wide one with "
            "the open square in the middle. The inn and the traders are up there, and people will "
            "want to meet you. Come back and tell me when you've had a look round."),
        turn_in_text=(
            "Good, you found it. You're the four hundred and tenth person through this gate since "
            "we came down three years ago.\n\n"
            "People here will be polite to you, but some of them won't know what to make of you "
            "yet. You arrived on this world the same year we arrived in this cavern, and a few of "
            "them find that strange. Give them time. Thanks for coming back."),
    ),
    "kb_index_failing": dict(
        title="Things That Don't Fit",
        description="Bring Archivist Nessaly 5 Worked Dalaran Fragments from the Archive Revenants "
                    "and 5 Lattice Cores from the Lattice.",
        accept_text=(
            "Every find in this cavern gets a number and a heading in the Codex. Forty-one of them "
            "don't fit under any heading we have, and that number keeps going up.\n\n"
            "Two of them are bothering me most. The revenants in the Weeping Colonnade carry "
            "pieces of worked Dalaran stone, and nobody ever brought Dalaran stone down here. The "
            "sentries and diviners in the Lattice carry crystal cores that look cut, not grown. I "
            "want five of each on my bench so I can compare them.\n\n"
            "The Colonnade is south of the gate. The Lattice is north-east."),
        turn_in_text=(
            "Look at the edges on these. The fragments and the cores were both cut, and whatever "
            "cut them did it in one pass without any mistakes. I think they were made the same "
            "way.\n\n"
            "That means I'll need a new heading in the Codex, and I don't know what to call it "
            "yet. Thank you. This will keep me busy for a while."),
    ),
    "kb_pages": dict(
        title="Out of Paper",
        description="Press 8 sets of Frostpine Pages for Archivist Nessaly. Frostpine grows up on "
                    "the surface, the nearest in Eastern Hillsbrad.",
        accept_text=(
            "We're running out of paper. Everything we write on had to be carried down here, and "
            "there are no trees in this cavern. The fungus won't press into anything you can "
            "write on, I've tried.\n\n"
            "Frostpine makes good pages. It grows up on the surface, and the nearest place is "
            "Eastern Hillsbrad, back up the way you came in. Cut the wood, plane it, and press "
            "eight sets of pages for me. Press them somewhere warm. Pages pressed in the cold "
            "crack, and we lost four months of field notes that way."),
        turn_in_text=(
            "That's about three weeks of work for the Archive, so these eight sets help a lot. "
            "I've been asking people to write smaller.\n\n"
            "Thank you for going all the way up for these."),
    ),
    "kb_reagents": dict(
        title="Better Than They Should Be",
        description="Brew 4 Elixirs of Arcane Fury for Alchemist Terrowen, using herbs you "
                    "gather in the Underdark.",
        accept_text=(
            "For three years every herb I've picked down here has tested stronger than the same "
            "herb picked on the surface. I don't know why, and nobody in the Codex believes me.\n\n"
            "I need a fair test. Brew four Elixirs of Arcane Fury, and use herbs you pick in this "
            "cavern yourself, not anything from my shelves. Arcane Fury is hard to get right. If "
            "it comes out at full strength from Underdark herbs, then it isn't me or my stock "
            "making the difference, it's something about this place."),
        turn_in_text=(
            "All four came out at full strength, and this one is stronger than it should be. "
            "That's what I've been seeing for three years.\n\n"
            "I'll take these up to the Codex-Master myself this time. Thank you."),
    ),
    "kb_naturalist_funding": dict(
        title="One Big Fungus",
        description="Bring Naturalist Orienne 8 Live Bloom Threads from the Mycelial Husks in the "
                    "Mycelial Reach.",
        accept_text=(
            "I've asked the Codex to let me survey the fungus four times now, and they've said no "
            "every time. They have it written down as scenery.\n\n"
            "I think every bit of fungus in this cavern is one living thing, growing under all of "
            "it, this town included. If I can show the threads from different places are the same "
            "organism, they'll have to listen.\n\n"
            "The Mycelial Husks out in the Mycelial Reach, south-west of the gate, carry live "
            "threads. Bring me eight. If you can, take them from husks in different parts of the "
            "Reach."),
        turn_in_text=(
            "They're all the same organism, every one of them. This town is sitting on top of it.\n\n"
            "I'll write it up for the Codex tonight. They'll probably make me write it twice. "
            "Thank you for getting these."),
    ),
    "kb_enchanter_debt": dict(
        title="Where the Power Comes From",
        description="Bring Enchanter Vaelios 4 Lattice Cores from the Shard Diviners in the "
                    "Lattice, and put down 10 of the diviners while you're there.",
        accept_text=(
            "The crystal down here gives off so much arcane power that I haven't had to use my "
            "own in two years. I don't know where it comes from, and that worries me.\n\n"
            "The Shard Diviners in the Lattice draw on it the same way I do. I need ten of them "
            "dead and four of their cores on my bench. I want to leave the cores on my bench overnight and "
            "see whether they keep drawing power when nobody's using them.\n\n"
            "The Lattice is north-east of the gate, past the Sporefall."),
        turn_in_text=(
            "I left them on the bench all night and they kept drawing power the whole time. "
            "Whatever is putting it out isn't asking for anything back.\n\n"
            "I'd still like to know what happens if it stops. Thank you for bringing these."),
    ),
    "kb_sentinel_wager": dict(
        title="The Cold Floor",
        description="Bring Hall-Sentinel Durannis 7 Dim Residues from the Dim-Walkers in the Dim "
                    "Reaches.",
        accept_text=(
            "The floor of the Codex Hall was cut from stone we quarried in the Dim Reaches. For "
            "the last month it's been cold, and only along the lines where the stones were laid. "
            "The air in the hall is fine. It's the stone that's cold.\n\n"
            "I want to know if it's still connected to where it came from. The Dim-Walkers out in "
            "the Dim Reaches leave a residue behind. Bring me seven scrapings of it and I'll see "
            "if it does the same thing.\n\n"
            "The Dim Reaches are the dark corner in the far south-west of the cavern. Take a light "
            "and go further in than the edge."),
        turn_in_text=(
            "I kept these in a jar in a warm room for three days and they went cold in the same "
            "pattern as the floor. So the stone is still connected to the Dim Reaches somehow.\n\n"
            "I'll show the jar to the magisters. Thanks for going out there."),
    ),
    "kb_the_question": dict(
        title="The Codex-Master's Question",
        description="Visit the Weeping Colonnade and bring Codex-Master Ilarien 4 Worked Dalaran "
                    "Fragments from the Archive Revenants.",
        accept_text=(
            "I'd like you to go and stand in the Weeping Colonnade. It's south of the gate, and "
            "it's full of Dalaran stonework that nobody brought down here. While you're there, "
            "bring me four worked fragments from the revenants.\n\n"
            "When you come back I want to ask you something. You came to this world three years "
            "ago, and we came down here the same year, when this cavern first opened. I want to "
            "know whether the Colonnade feels to you like something we found, or something that "
            "was left here for whoever came first."),
        turn_in_text=(
            "You said it feels like both. That's what Scholar Veridan told me too, and it's what "
            "I think myself.\n\n"
            "I still don't know how to write it down. Thank you for going, and for answering."),
    ),
    "kb_sealed_entry": dict(
        title="Your Entry in the Codex",
        description="Bring Codex-Master Ilarien 3 Worked Dalaran Fragments, 3 Druses With an "
                    "Inclusion and 3 Grown Leaves, and press 2 sets of Frostpine Pages.",
        accept_text=(
            "Everyone in the Bastion has an entry in the Codex, and we keep adding to them. I've "
            "never closed one. I'd like to close yours, and seal it, because of what you've done "
            "down here.\n\n"
            "Bring me something from each of the places you've been. Three worked fragments from "
            "the revenants in the Weeping Colonnade, south of the gate. Three druses from the "
            "Druse Crawlers in the Hollow Geode, east past the Lattice. Three leaves from the "
            "Shelf-Grown in the Deep Bloom, whose door is in the Dim Reaches to the south-west.\n\n"
            "And press two sets of frostpine pages yourself for the entry. The Archive can't "
            "spare the paper."),
        turn_in_text=(
            "It's written and sealed, and it can't be changed now. I've never been sure enough of "
            "anything down here to do that before.\n\n"
            "Thank you for everything you've done for the Codex. You'll always be welcome here."),
    ),
}

GREETINGS = {
    "kb_gate_warden": (
        "This is the gate of Kael's Bastion. I'm Vessaria, and I keep it. Tell me your name and "
        "what you're here for. Anything you bring in from the cavern has to be shown to me first "
        "so it can be written into the Codex."),
    "kb_porter": (
        "I'm Dunhal, the only Forsaken on this expedition. They wanted someone who doesn't "
        "mind the dark. I carry crates between the gate and the galleries all day, so if "
        "something came in from the cavern, I've probably carried it."),
    "kb_stablemaster": (
        "None of these animals were born underground, and the low roof makes them nervous. Leave "
        "your mount with me and I'll keep it calm."),
    "kb_cartographer": (
        "I've surveyed this cavern four times now and none of my maps match. The cavern isn't "
        "moving, I've checked that. Something changes every time I measure it and I can't work "
        "out what. If you're walking out there, I'd like to hear how far you went."),
    "kb_naturalist": (
        "I study the fungus out in the Sporefall and the Mycelial Reach. I think it's all one "
        "living thing, growing under the whole cavern, this town included. The Codex has it down "
        "as scenery, and I'm trying to get that changed."),
    "kb_enchanter": (
        "The crystal down here gives off so much arcane power that enchanting is about twice as "
        "easy as it was in Silvermoon. Bring me anything you want enchanted, or anything you want "
        "broken down for materials."),
    "kb_magister": (
        "I study the Hollow Geode, the crystal cave east of the Lattice. The crystal in there has "
        "started growing inward, toward the middle, and something in the middle is guarding it. "
        "If you go in, be careful."),
    "kb_archivist": (
        "I keep the records for the Sunken Archive and the Deep Bloom. You came to this world the "
        "same year we came down here. Most of the Codex doesn't like to talk about that, but I "
        "wrote it down anyway. If you're looking for work, I've got some."),
    "kb_codex_master": (
        "Welcome to Kael's Bastion. I'm Ilarien Duskwaking, and I run the Crimson Codex. "
        "Silvermoon sent us down here three years ago to write down everything in this cavern. "
        "We've recorded thousands of things so far, and we keep finding more we can't explain. "
        "If you go out there, I'd like to hear what you find."),
    "kb_hall_adjutant": (
        "I keep the Codex-Master's appointments. She'll see you whenever you like, she sees "
        "everyone who comes down. If you've found something out in the cavern, tell me and I'll "
        "get it written into the Codex."),
    "kb_hall_sentinel": (
        "I'm Durannis, and I guard the Codex Hall. I'm a soldier and I don't know much about crystal, "
        "but the floor in here has gone cold over the last month, and the stone came out of the "
        "Dim Reaches. If you're heading out that way, talk to me first."),
    "kb_flight_master": (
        "The crack in the roof is wide enough to fly through, so I can take you up to any flight "
        "point you've already been to on the surface. It took most of a season to get the "
        "hippogryphs used to it."),
    "ak_kb": (
        "I look after set pieces for anyone who needs them. If a piece of your set doesn't suit "
        "the way you fight now, give it to me and I'll swap it for the version that does. It "
        "won't cost you anything."),
}

VENDOR_GREETINGS = {
    "kb_quartermaster": (
        "Everything on these shelves had to be carried down through the crack in the roof, so it "
        "costs a bit more than it would up top. If you're heading out into the cavern, I've got "
        "what you'll need."),
    "kb_trader": (
        "I buy what comes out of the cavern and send it up to the surface, and I sell what comes "
        "down. Crystal and fungus sell well up top, if you've got any."),
    "kb_smith": (
        "There's no good coal down here, so I burn whatever the Codex says it can spare. The "
        "forge still gets hot enough. I can sell you plans and supplies, or fix what you're "
        "wearing."),
    "kb_reagent_seller": (
        "Everything here is labelled with where it was picked and when. If you need reagents for "
        "spells or for brewing, ask me and I'll find them."),
    "kb_innkeeper": (
        "There's no day or night down here, so we picked hours and stick to them. Supper is "
        "whenever you get in. Sit down and I'll bring you something."),
    "kb_alchemist": (
        "Herbs picked down here test stronger than the same herbs picked on the surface. I don't "
        "know why yet, but it makes for good potions, and I've got plenty of them."),
}


def main():
    bad = []
    for qid, f in QUESTS.items():
        for k, t in f.items():
            if k != "title":
                bad += [f"{qid} {k}: {p}" for p in voice_problems(t)]
            if "—" in t or " - " in t:
                bad.append(f"{qid} {k}: a dash")
    for src in (GREETINGS, VENDOR_GREETINGS):
        for nid, t in src.items():
            bad += [f"{nid}: {p}" for p in voice_problems(t)]
            if "—" in t or " - " in t:
                bad.append(f"{nid}: a dash")
    quests = {q["quest_id"]: q for q in
              json.loads((ROOT / "data/quests/underdark.json").read_text(encoding="utf-8"))["quests"]}
    for qid in QUESTS:
        if qid not in quests:
            bad.append(f"{qid}: no such quest")
            continue
        text = QUESTS[qid]["accept_text"] + QUESTS[qid]["description"]
        for o in quests[qid]["objectives"]:
            n = o.get("count")
            words = {3: "three", 4: "four", 5: "five", 7: "seven", 8: "eight", 10: "ten", 2: "two"}
            if n and str(n) not in QUESTS[qid]["description"]:
                bad.append(f"{qid}: the summary never says {n}")
            if n and words.get(n, "#") not in text.lower() and str(n) not in text:
                bad.append(f"{qid}: never says how many ({n})")
    if bad:
        print("FAILED:")
        for b in bad:
            print("  -", b)
        return 1

    out = ROOT / "data/quests/text/zzz_kaels_bastion.json"
    out.write_text(json.dumps(QUESTS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # the older overlay's Bastion entries are the ones with the cut-off counts; drop them so
    # only one version of each quest's text exists
    old = ROOT / "data/quests/text/zz_overhaul_underdark.json"
    o = json.loads(old.read_text(encoding="utf-8"))
    o = {k: v for k, v in o.items() if k not in QUESTS}
    old.write_text(json.dumps(o, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    g = ROOT / "data/npcs/greetings/kaels_bastion.json"
    g.write_text(json.dumps(GREETINGS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    v = ROOT / "data/npcs/vendor_greetings/kaels_bastion.json"
    v.write_text(json.dumps(VENDOR_GREETINGS, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Kael's Bastion: {len(QUESTS)} quests, {len(GREETINGS)} greetings, "
          f"{len(VENDOR_GREETINGS)} shopkeepers")
    return 0


if __name__ == "__main__":
    sys.exit(main())
