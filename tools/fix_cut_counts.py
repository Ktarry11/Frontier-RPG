#!/usr/bin/env python3
"""Mend the sentences that lost their opening number. Idempotent.

    PYTHONPATH=. python3 tools/fix_cut_counts.py

Kyle, 14 Nov 2026, on the text audit: "Contain these ones: broken counts." An older script
(tools/strip_prose_counts.py, commit bde5618) took counts out of quest prose, which is Kyle's
standing rule, but where the number opened a sentence it left the rest behind: "Six glands and
whatever bruiseweed" became "Glands and whatever bruiseweed", "Ten pages." became "Pages.", and a
few that were written after it copied the same clipped shape. Each one here gets the words it
needs to be a sentence again, still without the number.

Writes data/quests/text/zzzy_count_fixes.json, laid over the older text. Each entry names the
quest, the field, the broken opening and its mend; if the broken opening is no longer there (a
later rewrite fixed it) the entry is skipped and reported.
"""
import contextlib
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
OUT = ROOT / "data/quests/text/zzzy_count_fixes.json"

A, T, D = "accept_text", "turn_in_text", "description"
FIXES = [
    ("arw_adder_season", A, "Glands and whatever bruiseweed",
     "Bring me adder glands, and whatever bruiseweed"),
    ("arw_what_veska_hears", A, "Charms, and I want them",
     "Bring me the charms, and I want them"),
    ("arc_the_refuge_road", T, "Maulers and the stone ones, and",
     "You've dealt with the maulers and the stone ones, and"),
    ("arc_the_bound", A, "Cores. They have a stone", "Bring me their cores. They have a stone"),
    ("arc_the_mere", A, "Bladders, intact, and intact", "Bring me their bladders intact, and intact"),
    ("arc_the_silt_mother", A, "Pearls off the bed and", "I want pearls off the bed and"),
    ("arc_dry_the_brood", A, "Shells and a look at the sump.",
     "I want some of their shells and a look at the sump."),
    ("arc_dry_below", T, "Offerings. Arranged,", "They're offerings, and they were arranged,"),
    ("are_wrack_drowned", T, "Keepsakes an' t'ree of dem", "Dese keepsakes, an' t'ree of dem"),
    ("are_they_are_holding", A, "Watch orders, off three different islands.",
     "Bring me their watch orders, off three different islands."),
    ("bst_the_lights_go_out", T, "Swarmers, in the wood.", "So it was swarmers in the wood."),
    ("cb_snapper_season", T, "Plates thick as slabs.", "These plates are as thick as slabs."),
    ("cb_dewdrops_of_the_dream", T, "Drops, and not one spilled.",
     "You brought the drops back and didn't spill one."),
    ("cb_fang_and_flame", T, "Shards. And they fit together.", "Look, these shards fit together."),
    ("cr_arrows_south", T, "Arrows. From the Crossroads.", "These arrows came from the Crossroads."),
    ("fen_noble_signets", T, "Houses, four names.", "Every one of these is from a different house."),
    ("hbw_ram_horns", A, "Horns off the foothill rams and", "Bring me horns off the foothill rams and"),
    ("hbw_militia", A, "In the fields, and I want you",
     "Deal with the ones in the fields, and I want you"),
    ("hbe_ditch_samples", A, "Samples - and not jars of ditchwater",
     "I need samples, and not jars of ditchwater"),
    ("hbe_route_card", T, "Tallies, six hands, one ledger",
     "These tallies are in six different hands, all from one ledger"),
    ("nb_signal_horns", T, "Horns. Fewer calls for help.",
     "Those are their horns, so that's fewer calls for help."),
    ("razorhill_supply_run", A, "Crates, wherever you find them",
     "Bring back any crates you find"),
    ("razorhill_supply_run", T, "Crates of pure profit", "That's crates of pure profit"),
    ("sep_wasp_stings", T, "Stings and no stinging.", "You got the stings and didn't get stung."),
    ("swf_salt_cart", A, "Barbs as well.", "Bring me barbs as well."),
    ("sps_hunter_pelts", D, "Pelts. Clean ones.", "I want pelts, and clean ones."),
    ("sps_pond_samples", A, "Bladders off the bloated ones", "Bring me bladders off the bloated ones"),
    ("sps_ferry_crates", A, "Crates off the pier,", "Bring the crates off the pier,"),
    ("sb_grubbs_ledger", A, "Pages off the overseers' satchels", "Bring me the pages off the overseers' satchels"),
    ("sb_grubbs_ledger", D, "Pages off the overseers' satchels", "Get the pages off the overseers' satchels"),
    ("sb_mastiffs_at_the_gate", T, "Dispatches. Orders for the east gate.",
     "These dispatches are orders for the east gate."),
    ("sb_cut_the_fuse", T, "Charges, all intact.", "You brought the charges back, all intact."),
    ("stvc_zuljana_names", T, "Stones, four names, and", "These stones have four names on them, and"),
    ("stvc_zuljana_font", A, "Cords and the chamber they are read in.",
     "I want the cords, and I want to know the chamber they're read in."),
    ("stn_what_the_wood_is_for", A, "Battens. Thin, dressed,", "They're battens, thin, dressed,"),
    ("stn_including_me", A, "Bundles, whatever is left dry inside them.",
     "Bring me the bundles, and whatever's left dry inside them."),
    ("stn_the_long_haul", A, "Blocks. The rootgrubbers give you the fat.",
     "I need the blocks. The rootgrubbers give you the fat."),
    ("bb_thirty_one", A, "Brass, numbered, punched at the shoulder.",
     "Bring me their brass tags, numbered and punched at the shoulder."),
    ("tan_gad_salvage", A, "Fittings, pages.", "Bring me fittings and pages."),
    ("tan_zf_the_offer", A, "Fetishes. And come back", "Bring me their fetishes, and come back"),
    ("tan_cove_two_went_down", A, "Shells off the bilge crawlers,", "Bring me shells off the bilge crawlers,"),
    ("tan_cove_the_warden", A, "Whistles, focuses.", "Bring me their whistles and focuses."),
    ("tan_cove_whose_claim", A, "Off the shore, tallies, and the crawler shells",
     "Bring me tallies off the shore, and the crawler shells"),
    ("tan_berth_done", A, "More off the shore and the bosuns' whistles",
     "Bring me more off the shore, and the bosuns' whistles"),
    ("tan_solo_salt_air", T, "Cores is a season of mornings", "These cores are a season of mornings"),
    ("ucq_kolven_ledger", T, "Pages.", "These are the pages."),
    ("ucq_pd_sump", A, "Vials, stoppers on.", "Bring the vials back with the stoppers on."),
    ("ucq_pd_ledger", A, "Ledgers, any condition.", "Bring me any ledgers you find, whatever state they're in."),
    ("ud_shard_crates", A, "Cores, and take them out", "Bring me cores, and take them out"),
    ("ud_lattice_repeats", A, "Sentries, and I want them", "Go after the sentries, and I want them"),
    ("ud_archive_unissued", T, "Slips. Numbers, all ahead of my sequence",
     "These slips have numbers all ahead of my sequence"),
    ("ud_bloom_argument", A, "Husks from the Reach,", "Bring me husks from the Reach,"),
    ("arw_the_gap", T, "Slips and all of them agree", "I've got the slips, and all of them agree"),
    ("arw_the_overseer", T, "Leaves and the house in uproar.", "You got the leaves, and the house is in uproar."),
    ("are_six_wrecks", T, "Tins, manifests, and three of them",
     "These tins have manifests in them, and three of them"),
]


def main():
    with contextlib.redirect_stdout(io.StringIO()):
        from world.quest_manager import QuestManager
        qm = QuestManager()
    out, gone, done = {}, [], 0
    if OUT.exists():
        out = json.loads(OUT.read_text(encoding="utf-8"))
    for qid, field, old, new in FIXES:
        q = qm.quests.get(qid)
        cur = getattr(q, field, "") if q else ""
        if q is None:
            gone.append(f"{qid}: no such quest")
            continue
        if new in cur:
            done += 1
            continue
        if old not in cur:
            gone.append(f"{qid} {field}: '{old[:40]}' isn't there any more")
            continue
        out.setdefault(qid, {})[field] = cur.replace(old, new, 1)
        done += 1
    OUT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"{done} of {len(FIXES)} broken openings mended -> {OUT.relative_to(ROOT)}")
    for g in gone:
        print("  skipped:", g)
    return 0


if __name__ == "__main__":
    sys.exit(main())
