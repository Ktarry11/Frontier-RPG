#!/usr/bin/env python3
"""
The Lashings quest pass. Idempotent. 44-48.

    PYTHONPATH=. python3 tools/build_lashings_quests.py
    PYTHONPATH=. python3 tools/audit_quests.py
    PYTHONPATH=. python3 tools/qa_quest_lore.py --zone lashings --show

TWELVE quests, all given in Steamwheedle Port, because a cove full of pirates is not a place with
anybody in it to give you a quest and the port four miles down the coast is full of people it is
happening to.

=========================================================================================================
THE SOUTHSEA STOPPED SAILING, AND THAT IS WHY THEY ARE A PROBLEM
=========================================================================================================
A fleet at sea takes a ship and goes away. A fleet rafted together four miles up the coast takes a
ship and is STILL THERE in the morning, and the port can see the masts from the Upper Yard on a
clear day. Steamwheedle has spent twenty years deciding that is somebody else's problem, because
the Southsea mostly take cargo rather than people and because four berths cannot be spared for a
war.

What changed is not the pirates. It is that Steamwheedle doubled in three years when Gadgetzan
emptied into it, and a port that has doubled has twice as much going out and the same four berths
and no slack at all. Ardessa Rake did not get greedier. The town got thinner.

NOBODY IN THIS PASS WANTS A BATTLE. Senna Coil wants her sailings to arrive. Nim Catchpenny wants
to stop recognising her own stock. Faz Quill wants his powder back and is embarrassed about how it
left. What they get is a player who walks up the coast and takes the cove apart one plank at a
time, which is the only thing that was ever going to work on a tree.

NO ESCORTS. All five kill_boss objectives are on PINNED bosses - every one of them stands on a
gangplank by construction. NO MAGIC RESISTANCE: Glittervein owns that theme at an overlapping band.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools import tirisfal_gear                          # noqa: E402
from tools.build_durotar_quests import kill, fetch       # noqa: E402
from tools.tirisfal_gear import reward_pack              # noqa: E402

OUT = ROOT / "data/quests/lashings.json"
DROPS = ROOT / "data/creatures/quest_drops.json"

LS = "the_lashings"
SP = "steamwheedle_port"

XP = {44: 3160, 45: 3240, 46: 3320, 47: 3400, 48: 3480}
GOLD = {44: 12600, 45: 12900, 46: 13200, 47: 13500, 48: 13800}

tirisfal_gear.THEMES.update({
    "lashed": (["Lashed", "Rafted", "Nine-Hull", "Twenty-Year", "Cove-Taken"],
               ["Off a deck that has not moved in twenty years.",
                "Salt got at it slowly, which is the worst way.",
                "Pirate kit - which is to say somebody else's kit, once.",
                "Rope-burn in the grain of it, from being hauled rather than carried."]),
    "prize": (["Prize-Court", "Share-Out", "Articles", "Logged", "Fair-Shares"],
              ["Logged, valued and divided by somebody with very neat handwriting.",
               "It came off a sailing out of Steamwheedle and it has a mark to prove it.",
               "Taken under articles, which the takers consider a meaningful distinction.",
               "There is a number inked on the inside of it and it is not the owner's."]),
})


def k(target, n, zone=LS):
    return kill(target, n, zone=zone)


def boss(target):
    return dict(type="kill_boss", target=target, count=1, zone=LS)


def explore(zone, x, y, radius=9):
    return dict(type="explore", target=zone, target_x=x, target_y=y, radius=radius)


def deliver(item, label, n=1):
    return dict(type="deliver", target=item, count=n, label=label)


def talk(*topics):
    return dict(type="dialogue", topics=list(topics))


def carry(item_id, name, desc, count=1):
    return {"on_accept": [dict(item_id=item_id, name=name, description=desc, count=count)]}


def Q(qid, title, giver, zone, lo, hi, theme, desc, objs, accept, done, nxt=None, salt="",
      **engine):
    is_boss = any(o["type"] == "kill_boss" for o in objs)
    ilvl = max(3, hi + 2 if is_boss else hi + 1)
    rarity = "rare" if is_boss else "uncommon"
    mult = 1.3 if is_boss else 1.0
    q = dict(quest_id=qid, title=title, giver_npc_id=giver, zone=zone, level_min=lo, level_max=hi,
             description=desc, objectives=objs,
             reward_exp=int(XP[hi] * mult), reward_gold=int(GOLD[hi] * mult),
             accept_text=accept, turn_in_text=done, next_quest_id=nxt,
             unique_item_defs=reward_pack(qid + salt, theme, ilvl, lo, rarity, 4 if is_boss else 3),
             gear_reward_gear_level=ilvl, gear_reward_rarity=rarity)
    q.update({kk: vv for kk, vv in engine.items() if vv})
    return q


# ---- givers. All already in tools/steamwheedle_npc_roster.py; this pass invents nobody.
SENNA = "stw_harbourmaster"     # four berths, turning ships away since the second winter
NIM = "stw_salvage_broker"      # buys what came off something and sells it onto something else
HALD = "stw_shipwright"         # a hull gets looked after or it gets burned for its nails
FAZ = "stw_engineer"            # mostly works, and is honest about the mostly
RULLO = "stw_caravan_agent"     # freight west, freight south, and a price for each
HESPER = "stw_tally_clerk"      # every crate in, every crate out, and which side it came from

FETCH_DROPS = {
    "Southsea Netcaster": [("lsh_cut_net", "Cut Boarding Net",
                            "Weighted at the hem. It is for people, not fish.", 0.38)],
    "Southsea Powdermonkey": [("lsh_short_keg", "Short-Weight Powder Keg",
                               "Steamwheedle cooperage, and the mark has been scraped at.",
                               0.36)],
    "Southsea Rigger": [("lsh_prize_tag", "Prize Tag",
                         "A cargo tag, re-inked. The first hand under it is Hesper Dunn's.",
                         0.40)],
    "Southsea Swabbie": [("lsh_ships_nail", "Pulled Ship's Nail",
                          "Drawn out of a hull that somebody was taking apart for the iron.",
                          0.42)],
}

STARTER_DROPS = {
    "Hulk Rat": [("lsh_chewed_articles", "Chewed Ship's Articles",
                  "The crew agreement of a vessel that is no longer a vessel, half eaten.",
                  0.24)],
}
STARTER_IDS = {"lsh_chewed_articles": "lsh_the_articles"}


def build():
    q = []

    # ---- the approach: why the port finally cares
    q.append(Q("lsh_four_berths", "You Can See the Masts From the Yard", SENNA, SP, 44, 44,
               "lashed",
               "The harbourmaster has lost three sailings this season and is done being patient.",
               [talk("lsh_the_cove", "lsh_the_arithmetic"), explore(LS, 68, 106, 8)],
               "Four berths, and I have been turning ships away since the second winter. Three "
               "years ago that was an inconvenience. Now it is the whole town's throat.\n\nAnd "
               "four miles up that coast there are nine hulls lashed together with about a "
               "hundred people on them taking one sailing in six.\n\nThis port has spent twenty "
               "years deciding that is somebody else's problem. Go and stand on the first deck and "
               "come back and tell me if it still is.",
               "They have not moved in twenty years. Not one of those hulls has moved.\n\nThat is "
               "the part I cannot get the yard to understand. A fleet that sails is weather. A "
               "fleet that sits there is a NEIGHBOUR, and you do not get to ignore a neighbour "
               "for twenty years and then be surprised.",
               nxt="lsh_recognising_my_own_stock"))

    q.append(Q("lsh_recognising_my_own_stock", "I Have Started Recognising It", NIM, SP, 44, 45,
               "prize",
               "The salvage broker keeps being offered things she sold last month.",
               [k("Southsea Rigger", 8), fetch("lsh_prize_tag", 5)],
               "I buy what came off something and I sell it onto something else and I have never "
               "once pretended otherwise.\n\nWhat I will not do is buy my own stock back. Twice "
               "this season somebody has put a crate on my counter that I SOLD, out of this shop, "
               "six weeks before.\n\nGet me the tags off them. Hesper inks every crate that leaves "
               "this port and they have been re-inking over the top, and badly.",
               "Her hand underneath and theirs on top. Every one.\n\nThat is not a pirate crew "
               "taking a prize at sea. That is somebody going through a manifest. They know what "
               "is on our ships before the ships leave.",
               salt="b"))

    q.append(Q("lsh_my_own_powder", "That Is My Powder", FAZ, SP, 45, 45, "prize",
               "The engineer's powder is in the cove and he is embarrassed about how it got there.",
               [k("Southsea Powdermonkey", 8), fetch("lsh_short_keg", 5)],
               "I build things that mostly work and I am honest about the mostly, so I am going to "
               "be honest about this: I sold them the powder.\n\nNot knowingly. A freight agent I "
               "will not name, a standing order, four years of it, and I never once asked where it "
               "went because the money was good and I had a workshop to replace.\n\nGo and get me "
               "a keg back. I want to see my own cooperage mark with a scrape through it.",
               "There it is. Scraped, not sanded - they were in a hurry and they did not care.\n\n"
               "Forty-one of those went up the coast. I have had three years of telling people my "
               "whole workshop is still in Gadgetzan and feeling sorry for myself, and in the same "
               "three years I armed a pirate fleet by not asking a question.",
               salt="c"))

    q.append(Q("lsh_the_boarding_nets", "Weighted at the Hem", HALD, SP, 45, 45, "lashed",
               "The nets are not for fish.",
               [k("Southsea Netcaster", 9), fetch("lsh_cut_net", 5)],
               "A fishing net is weighted evenly. A boarding net is weighted at the HEM so it "
               "drops flat over a deck and nobody under it can stand up.\n\nI have mended both for "
               "thirty years and I can tell them apart in the dark. Bring me what they are using "
               "and I will tell the harbourmaster exactly what her crews are walking into.",
               "Hem-weighted, every one, and the mesh is tight enough that a cutlass will not go "
               "through it.\n\nThey are not sinking anybody. They have never wanted to sink "
               "anybody. They want the deck and the crew standing still on it, and that is a much "
               "more frightening sentence than the other one."))

    # ---- the cove, one plank at a time
    q.append(Q("lsh_the_bosun", "Everybody On Deck", SENNA, LS, 46, 46, "lashed",
               "A bosun holds the first gangway, and there is no way round a gangway.",
               [boss("Bosun Grell Tarpot"), k("Southsea Swabbie", 6)],
               "Here is what I have worked out about that cove and it is the only useful thing "
               "anybody has said about it in twenty years.\n\nThey are hulls lashed together. One "
               "plank between each. There is no going round, for you OR for them - which means "
               "you can take it apart one deck at a time and they cannot flank you, and it also "
               "means every single plank has somebody standing on it.\n\nThe first one is Grell "
               "Tarpot. You will hear him before you see him.",
               "The whole cove heard that. Good.\n\nThey cannot reinforce past a man standing on a "
               "three-foot plank any more than you can get past one. Twenty years they have been "
               "safe behind that and today it is the thing holding them still.",
               nxt="lsh_the_sailmaker"))

    q.append(Q("lsh_the_sailmaker", "Nobody Has Unfurled Anything", HALD, LS, 46, 46, "lashed",
               "The sailmaker on a fleet that does not sail.",
               [boss("Sailmaker Oona Flay"), k("Hulk Rat", 7)],
               "There is a sailmaker on that fleet. I have thought about that more than is "
               "healthy.\n\nNobody on those hulls has unfurled a sail in twenty years. So either "
               "she has had nothing to do for two decades, or she has been making something "
               "else - and I have seen the nets, so I know which.\n\nShe will be on the careenage. "
               "That is the hull laid over to have its bottom scraped, and they never righted it, "
               "and I think about that one too.",
               "Her palm was worn through twice. Twice, on a fleet with no sails.\n\nI have mended "
               "canvas for thirty years. I would like it on record that I am sorry about this one "
               "in a way I am not sorry about the others."))

    q.append(Q("lsh_the_powder_master", "Forty-One Barrels", FAZ, LS, 47, 47, "prize",
               "His powder, and the man who has been counting it.",
               [boss("Powder-Master Juss Wick"), fetch("lsh_short_keg", 4)],
               "Juss Wick keeps the powder hulk, which is the third hull up, and he has been "
               "keeping it for longer than I have been selling to him.\n\nHe knows exactly where "
               "every barrel is. I know that because I know how much I sent and the harbourmaster "
               "knows how much has gone off in the last four years, and the difference has not "
               "been wasted by anybody.\n\nI would like my mark back and I would like him to not "
               "have it.",
               "Forty-one. He had it written on a board.\n\nI am going to pay for the cooperage to "
               "restamp everything in my shop with a mark that cannot be scraped. It will cost me "
               "more than the powder did. I am going to do it anyway.",
               nxt="lsh_the_prize_court"))

    q.append(Q("lsh_the_prize_court", "Everything Is Logged", NIM, LS, 47, 47, "prize",
               "They keep books. Better books than the port does.",
               [boss("Quartermaster Nadd Kell"), fetch("lsh_prize_tag", 4)],
               "The hull they call the prize court is where everything they take is logged and "
               "valued and divided, under articles, by a quartermaster.\n\nI want the books. Not "
               "to be righteous about it - I want to know who has been buying, because somebody "
               "in this port has, for twenty years, and it is not me and I would very much like "
               "to be able to prove that.",
               "[She reads for a long time.]\n\nFour names. Two of them are dead, one of them left "
               "with the Gadgetzan crowd, and one of them is still trading out of the Upper "
               "Yard.\n\nI am not going to tell you which. I am going to walk over there this "
               "afternoon and have a conversation, and whatever else happens, they are going to "
               "know that I know."))

    q.append(Q("lsh_the_articles", "Signed With a Cross", "item:lsh_chewed_articles", LS, 46, 47,
               "prize",
               "A crew agreement for a ship that is not a ship any more.",
               [deliver("lsh_chewed_articles", "the chewed articles, to Tally-Clerk Hesper Dunn")],
               "Ship's articles - the agreement every hand signs about shares, discipline and what "
               "happens to the wounded. Half of it has been eaten by something. The signatures are "
               "mostly intact.",
               "Ninety-one marks. Most of them crosses.\n\nThat is not a crew list, that is a "
               "CENSUS. Ninety-one people with a written agreement about who gets what if they are "
               "hurt - which is more than the yard has, and I have been asking for that in writing "
               "for three years.\n\nI am going to file this. I am not going to say where under.",
               salt="d"))

    q.append(Q("lsh_rake", "The One Who Is Good At It", SENNA, LS, 48, 48, "lashed",
               "Captain Ardessa Rake, aboard the only hull in that cove still kept like a ship.",
               [boss("Captain Ardessa Rake")],
               "Ardessa Rake has run that cove for twenty-two years and I want to tell you the "
               "thing about her that matters, because it is not that she is cruel.\n\nThere is a "
               "Southsea crew up in the Barrens under a man called Saltspray who is loud and bad "
               "at it. SHE sent him there. That is what you do with a man who is loud and bad at "
               "it when you are good at it and you intend to stay.\n\nShe keeps one hull like a "
               "ship. Nine of them and she keeps one. You will know it when you are standing on it.",
               "She was on the quarterdeck of a hull that has not moved since before I had this "
               "post.\n\nI am going to be straight with you, because the yard will not be: this "
               "port will take her cove's trade within a month and call it recovery, and half of "
               "what comes down that coast will be the same cargo that went up it.\n\nI still "
               "wanted it stopped. Both of those are true and I have stopped trying to make them "
               "sit comfortably together.",
               nxt="lsh_the_masts_are_gone"))

    q.append(Q("lsh_the_masts_are_gone", "You Cannot See Them From the Yard", RULLO, SP, 48, 48,
               "lashed",
               "What the port does the week after.",
               [talk("lsh_after"), explore(SP, 80, 54, 8)],
               "Forty years I have priced freight on this coast and every single price had the "
               "Southsea in it. A sixth for the cove, we called it. Nobody wrote it down, it was "
               "just in the number.\n\nI have spent this morning repricing everything and I do not "
               "mind telling you it has made me feel strange. Go and stand on the Upper Yard and "
               "look north and come back.",
               "You cannot see the masts. Twenty-two years of being able to see the masts from "
               "that yard and you cannot see them.\n\nI will run a cart west now. I have said for "
               "three years that there was nothing coming back worth the axle and that was true "
               "and it was also a thing I said instead of the real reason.",
               nxt="lsh_the_last_column"))

    q.append(Q("lsh_the_last_column", "Which Side It Came From", HESPER, SP, 48, 48, "prize",
               "The clerk who keeps the last two columns has one more to add.",
               [deliver("lsh_closing_entry", "the closing entry, to Harbourmaster Coil"),
                talk("lsh_two_columns")],
               "Every crate in, every crate out, which side of town it came from and which side it "
               "went to. People assume I keep the last two columns to be unpleasant.\n\nI keep "
               "them because in four years somebody is going to claim this town was always like "
               "this.\n\nWell. In four years somebody is also going to claim there was never a "
               "cove, or that it was nothing much, or that it fell apart on its own. Take Senna "
               "the closing entry and we will both have signed it.",
               "Signed, dated and filed.\n\nThat is the whole of my profession in one afternoon: "
               "something enormous happened, and the only part of it that will still exist in "
               "forty years is a line in a book that two people put their names to while everybody "
               "else was busy being relieved.",
               grant_items=carry("lsh_closing_entry", "The Closing Entry",
                                 "One line, two columns, and a space for a second signature.")))

    return q


def audit(quests):
    bad = []
    ids = {q["quest_id"] for q in quests}
    pinned = {"Bosun Grell Tarpot", "Sailmaker Oona Flay", "Powder-Master Juss Wick",
              "Quartermaster Nadd Kell", "Captain Ardessa Rake"}

    for q in quests:
        blob = " ".join(str(q.get(kk) or "") for kk in ("title", "description", "accept_text",
                                                        "turn_in_text"))
        if "escort" in blob.lower() or any(o["type"] == "escort" for o in q["objectives"]):
            bad.append(f"{q['quest_id']}: escort")
        for o in q["objectives"]:
            if o["type"] == "kill_boss" and o["target"] not in pinned:
                bad.append(f"{q['quest_id']}: kill_boss on {o['target']}, which is not pinned")
            if o["type"] in ("gather", "fetch") and str(o.get("target", "")).startswith(
                    ("herb_", "ore_", "crystal_", "wood_", "essence_")):
                bad.append(f"{q['quest_id']}: {o['type']}es the node material {o['target']}")
        for it in q.get("unique_item_defs", []):
            stats = dict(it.get("secondary_stats") or {}, **(it.get("primary_stats") or {}))
            if any("resistance" in kk for kk in stats):
                bad.append(f"{q['quest_id']}: {it['name']} carries resistance, which this pass "
                           f"leaves to Glittervein")

    droppable = {iid for rows in list(FETCH_DROPS.values()) + list(STARTER_DROPS.values())
                 for (iid, _n, _d, _c) in rows}
    for q in quests:
        granted = {g["item_id"]
                   for g in ((q.get("grant_items") or {}).get("on_accept") or [])}
        for o in q["objectives"]:
            if o["type"] == "deliver" and o["target"] not in granted | droppable:
                bad.append(f"{q['quest_id']}: delivers {o['target']}, which nothing grants or drops")
        nx = q.get("next_quest_id")
        if nx and nx not in ids:
            bad.append(f"{q['quest_id']}: chains to {nx}, which this pass does not define")

    # the engine's count rule: a number within two words of ANY objective target word
    NUMWORD = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
               "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "dozen": 12}
    for q in quests:
        words = {}
        for o in q["objectives"]:
            for w in str(o.get("target", "")).lower().replace("_", " ").split():
                if len(w) > 3:
                    words.setdefault(w, []).append(o.get("count", 1))
        blob = " ".join(str(q.get(kk) or "") for kk in ("description", "accept_text",
                                                        "turn_in_text"))
        low = [t.lower() for t in re.findall(r"[A-Za-z0-9']+", blob)]
        for i, t in enumerate(low):
            if t not in words:
                continue
            for x in low[max(0, i - 2):i + 3]:
                n = int(x) if x.isdigit() else NUMWORD.get(x)
                if n is not None and n not in words[t]:
                    bad.append(f"{q['quest_id']}: '{x} ... {t}' puts {n} beside an objective word "
                               f"whose count is {words[t]}")
                    break
    return bad


def main():
    import os
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    quests = build()
    ids = [q["quest_id"] for q in quests]
    if len(set(ids)) != len(ids):
        print("FAILED: duplicate quest ids")
        return 1
    bad = audit(quests)
    if bad:
        print("\nFAILED - fix the quests, not the check:")
        for b in bad:
            print(f"  - {b}")
        return 1

    OUT.write_text(json.dumps({"quests": quests}, indent=2, ensure_ascii=False) + "\n",
                   encoding="utf-8")
    dd = json.loads(DROPS.read_text(encoding="utf-8"))
    drops = dd["drops"]
    for cre, rows in list(FETCH_DROPS.items()) + list(STARTER_DROPS.items()):
        have_rows = {r["item_id"]: r for r in drops.get(cre, [])}
        for (iid, nm, desc, ch) in rows:
            rec = {"item_id": iid, "name": nm, "category": "quest", "description": desc,
                   "chance": ch}
            if iid in STARTER_IDS:
                rec["starts_quest_id"] = STARTER_IDS[iid]
            have_rows[iid] = rec
        drops[cre] = list(have_rows.values())
    DROPS.write_text(json.dumps(dd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    print(f"{len(quests)} quests -> {OUT.name}: "
          f"{sum(1 for q in quests if q.get('next_quest_id'))} chained")
    return 0


if __name__ == "__main__":
    sys.exit(main())
