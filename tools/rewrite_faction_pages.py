#!/usr/bin/env python3
"""The faction pages' write-ups, second pass (Kyle, 21 Nov 2026: "we need to update the Prestige write-ups. Some are
exceptionally done like the liquidators. Some are weird like TB", and "now that the first sky continent is named").

    PYTHONPATH=. python3 tools/rewrite_faction_pages.py [--show]

The Liquidators' page is the bar: specific, plain-spoken, real places and real reasons, no narrator winking at you.
The older pages were written in a dry, arch voice (no contractions, a knowing last line, a dash or two), and Thunder
Bluff's ended on its people agreeing "politely" with whoever pointed out their city's gone. These are rewritten in the
house voice, with the same facts; nothing about what happened changes. The Aetherians' page names Caelora and stops
dating the sky's dying from the change (it's centuries old, and only lately faster, docs/worldtree_brief.md), and the
Highbough Tribes' names the sky the tree's crown reached. Pages not listed here are kept as they are. The Unnamed's
page is never touched.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data/factions/factions.json"

#: faction id -> {"description": ..., "lore": [...]}; a key left out keeps what's there
PAGES = {
    "thunder_bluff": {
        "description": "The tauren of a city that fell when the world changed, still carrying its name.",
        "lore": [
            "Thunder Bluff stood on four rock spires above Mulgore, and no army ever took it. When the world changed, "
            "the ground under the spires gave way, and the city went down with it.",
            "Mulgore's still there, after a fashion. The grass grows and the sky's where it should be, but the plain "
            "itself is wrong now, and the things that walk it kill war parties without slowing down. The tauren have "
            "gone back for the spires four times. Three of those war parties came home.",
            "Cairne Bloodhoof was in the city when it fell, and nothing of him has been found. There's no body to "
            "burn and nothing to bury, so the chieftain's seat stands empty. Elder Longtread speaks for the tauren, "
            "and he's turned the title down every time it's been offered, because taking it would mean Cairne is "
            "dead, and nobody's proved that.",
            "They live as guests now: at Camp Taurajo, with the warbands in the southern Barrens, and in other "
            "people's towns, more of them every season. Every nation that took them in asked nothing for it. The "
            "tauren pay it back in work, on every wall and every road they're given.",
            "They still call themselves Thunder Bluff. It's the name of a people now, not of a place, and it'll stay "
            "that way until they stand on the spires again.",
        ],
    },
    "orgrimmar": {
        "lore": [
            "The Horde came ashore in Durotar with what it could carry, and Orgrimmar went up out of red stone and the "
            "timbers of the ships that brought it. The city still looks like what it is: built fast, by people who "
            "couldn't afford to be choosy.",
            "Thrall holds it. He was born in chains and got his people out of them, and it left him careful. He'd "
            "rather keep what the Horde has than reach for more, and there are voices in the city who say so, loudly "
            "and often.",
            "The city keeps its regard in quartermasters' ledgers: who held the Barrens road, who went down into the "
            "Chasm when the Burning Blade came up out of it, who was on the wall when it mattered.",
            "When the world changed, Orgrimmar opened its gates to the people it threw up faster than anywhere else on "
            "the continent, and with less argument. Thrall's never said why in public. The ones who were in the "
            "internment camps with him have never needed him to.",
        ],
    },
    "darkspear_tribe": {
        "lore": [
            "The Darkspear were down to their last island when the Horde found them. It was a bargain between two "
            "peoples with nothing, and the trolls have kept their half of it to the letter ever since.",
            "Then Zalazane took the isles. He went through the tribe with hex and voodoo until their own kin came out "
            "of the surf at them, and the Darkspear pulled back to the mainland and started again.",
            "They don't say the isles are lost. They say the ones still out on the water aren't back yet, and they'll "
            "correct you if you say it the other way.",
            "The tribe keeps its own spiritwalkers, its own trainers and its own account of who stood with it when "
            "things were bad. That account is older than the Horde's, and it isn't the same list.",
        ],
    },
    "the_forsaken": {
        "lore": [
            "The Scourge raised Lordaeron's dead and set them walking. Then its hold on them slipped, and what "
            "straightened up in the ruins remembered everything: names, houses, the faces of their families, and "
            "exactly what had been done to them.",
            "They took the undercroft beneath the palace and made a country of it. The throne room overhead still has "
            "the old king's blood dried into the floor, and nobody down there calls that a tragedy. It's theirs now.",
            "The Apothecarium sits at the heart of the city and worries everyone, allies included. It's the only "
            "place on the continent studying the plague that made them. Ask the apothecaries why and they'll tell you "
            "it's for a cure. Read their ledgers and you may come to another answer.",
            "What they won't forgive is the Scarlet Crusade, who kill them on sight for the crime of having been "
            "murdered, and the cults still working for the thing that did it. Standing with the Forsaken is mostly a "
            "tally of how many of either you've put back in the ground.",
            "They're tired, blackly funny and very hard to impress. They've been dead a while, and there isn't much "
            "left that surprises them.",
        ],
    },
    "steamwheedle_cartel": {
        "lore": [
            "The Cartel isn't a nation and has never pretended to be. It's a company with harbours, and those harbours "
            "are the only stretches of coast where a Horde ship and an Alliance ship tie up at the same pier and "
            "nothing happens.",
            "The neutrality is what it sells. Bring a war into Ratchet and the goblins won't take a side. They'll put "
            "you on a boat, bill your faction for the trouble, and have the dock working again by the evening tide.",
            "Gazlowe runs the port, and runs it better than its margins deserve. He's turned down three offers to "
            "move the whole operation somewhere richer, and nobody in Ratchet knows why.",
            "Their regard is bought rather than earned, and they're honest about it. Pirates on the water and bandits "
            "on the Barrens road cost the Cartel money. Anyone who brings that number down is good for business, and "
            "in Ratchet that's as close to friendship as it gets.",
        ],
    },
    "booty_bay_authority": {
        "lore": [
            "There's no road into Stranglethorn. The range closed the land route and never opened it again, which "
            "left two ways in: an airship berth the Horde flew in over the top, and this cove.",
            "That made Booty Bay the only deep-water harbour still joining anything to anything, and a harbour in "
            "that position stops taking instructions. The Baron didn't declare anything. He just started deciding "
            "which hulls left on which tide, and after the third season nobody was asking Ratchet.",
            "The Steamwheedle Cartel hasn't formally lost the port, and it'll tell you so at length. Factor Weezel "
            "still signs the manifests and still files them, and the Baron still decides what sails.",
            "What the Authority sells is what the Cartel always sold, a pier where two enemies can tie up and nothing "
            "happens, except that here it's enforced rather than negotiated. The bruisers are the law, the Baron is "
            "the court, and the tariff isn't up for discussion. People complain about the landing fee until the first "
            "time they need the harbour to hold.",
        ],
    },
    "aetherians": {
        "description": "The scholar houses of Aurelion, who rule Caelora, the Aetherians' continent above the clouds, "
                       "and the survey the House of the Patient Lens sent down to the World Tree.",
        "lore": [
            "Above the clouds there's a continent nobody on the ground knew about. The Aetherians call it Caelora, and "
            "they've lived on its floating islands for as long as their records go back. They're tall and pale, with "
            "crystal growing along their arms and light in their eyes, and Aurelion, their capital, floats on engines "
            "of crystal older than any kingdom below.",
            "Their sky has been dying for centuries, slowly, the way a fire goes out. The engines fail one by one, "
            "islands fall and the cloud thins, and lately it's all been going faster. The council of the scholar "
            "houses can't agree on why. Some houses say the World Tree should be studied before anyone touches it. "
            "The Ascendancy, their army, says the tree is the only thing in the sky still rising, and should simply "
            "be taken.",
            "The House of the Patient Lens sent a survey down to the tree to meet the people living on it. It's the "
            "first time in their history the Aetherians have come down to the ground, and most of them still think "
            "the ground is primitive. The ones who've met it are starting to change their minds.",
        ],
    },
    "highbough_tribes": {
        "lore": [
            "Three years ago a seed split the reef off Stranglethorn's west coast, and the tree that came out of it "
            "has never stopped growing. Its roots drink the sea, its branches carry whole villages, and its crown has "
            "gone up through the clouds into Caelora, the Aetherians' sky.",
            "Stranglethorn's trolls, squeezed between Grom'gol, the Bloodsail and their own feuding tribes, were the "
            "first to climb it. Darkspear kin and the tribes who'd broken with the Gurubashi feuds, with a few "
            "Skullsplitter and Bloodscalp who turned their backs on their own, built a landing at its roots and a "
            "city in its heart.",
            "They call the tree a loa that answered them when nothing else would. The Highbough Tribes hold it now, "
            "allied to the Horde without answering to it, and they remember who helps them keep it.",
        ],
    },
}


def main():
    raw = PATH.read_text(encoding="utf-8")
    doc = json.loads(raw)
    f = doc["factions"]
    assert "the_unnamed" not in PAGES
    from tools.build_tempest_quests import voice_problems
    bad = []
    for fid, page in PAGES.items():
        for para in page.get("lore", []) + [page.get("description", "")]:
            bad += [f"{fid}: {p}" for p in voice_problems(para)]
    if bad:
        raise SystemExit("FAILED:\n  " + "\n  ".join(bad))
    before = {fid: {k: f[fid].get(k) for k in page} for fid, page in PAGES.items()}
    if "--show" in sys.argv:
        for fid, page in PAGES.items():
            print(f"== {f[fid]['name']}")
            for k in page:
                print(f"  BEFORE {k}: {before[fid][k]}")
                print(f"  AFTER  {k}: {page[k]}")
        return
    for fid, page in PAGES.items():
        f[fid].update(page)
    PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{len(PAGES)} faction pages rewritten")


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    main()
