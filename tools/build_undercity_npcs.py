"""
Undercity cast: ambient NPCs, vendors, recruits, forge and travel services.  Idempotent - upserts by id.

    python3 tools/build_undercity_npcs.py

Positions come from tools/handbuilt_undercity.NPC_POSITIONS / RECRUITS / FORGE (so the map and the data cannot drift).
Ambient NPCs are flavour + quest givers (data/quests); vendors are in data/npcs/vendors.json; `uc_innkeeper` and
`uc_riding_trainer` carry travel services (data/travel/travel_data.json "services").
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from tools.handbuilt_undercity import NPC_POSITIONS, RECRUITS, FORGE   # noqa: E402

F, M = "female", "male"
# id: (name, race, gender, variant, facing, greeting)
AMBIENT = {
    # ---- the Long Descent
    "uc_guard_1": ("Forsaken Guardsman", "forsaken", M, 3, "down",
                   "The Dark Lady watches over this city. Mind your business and she'll mind hers."),
    "uc_guard_2": ("Deathguard Halloran", "forsaken", M, 9, "left",
                   "Keep to the avenue. The canal is not for swimming, and I'm tired of fishing out tourists."),
    # ---- the Trade Quarter
    "uc_banker": ("MerchantTusk", "troll", M, 3, "down",
                  # The same troll who runs the vault in Orgrimmar and Freewind Post. Replaces
                  # Banker Moravin, who was ambient flavour with no quest or service ties.
                  "Dere is only one bank, mon, and dere is only one me. Do not ask how dat works. Hand me ya things and go be a hero."),
    "uc_auctioneer": ("Auctioneer Dross", "forsaken", M, 12, "down",
                      "Going once, going twice... going to the lady with the suspiciously large coin purse!"),
    "uc_undertaker": ("Mortician Gravelle", "forsaken", F, 7, "right",
                      "Business is slow. Strange, for an undertaker, in a city of the dead."),
    "uc_trader": ("Grukthar Deepdweller", "orc", M, 20, "down",
                  "An orc, in Undercity? The Horde is stranger and stronger for it. I go where the coin goes."),
    "uc_market_embalmer": ("Embalmer Pell", "forsaken", M, 2, "down",
                           "Preservative salts, wax, and thread. Everything a body needs to keep its shape."),
    "uc_market_food": ("Cook Marrowbone", "forsaken", F, 10, "down",
                       "Taste is optional down here. Nutrition, I'm told, is merely a habit."),
    "uc_market_herbs": ("Herbalist Thistledown", "forsaken", F, 13, "down",
                        "Grave-moss, deadnettle, a little foxglove. Nothing here will kill you. Probably."),
    "uc_market_scribe": ("Scribe Ormsby", "forsaken", M, 6, "down",
                         "Letters of passage, last wills, and the occasional love note. Don't ask which is which."),
    "uc_market_gems": ("Gemcutter Voss", "forsaken", F, 5, "down",
                       "Eyes, mostly. Glass ones. The jewels are to put in them."),
    "uc_market_tailor": ("Tailor Yarrow", "forsaken", F, 11, "down",
                         "Burial shrouds, travelling cloaks, whatever you can stitch from a sheet. Hems are free."),
    "uc_market_relics": ("Relic-Hunter Crane", "forsaken", M, 8, "down",
                         "Everything you see was found somewhere it shouldn't have been. That's what makes it valuable."),
    "uc_market_butcher": ("Butcher Grimsby", "forsaken", M, 15, "down",
                          "Fresh as the day it was... well. Fresh as it gets. Don't ask."),
    # ---- the Royal Quarter
    "uc_sylvanas": ("Lady Sylvanas Windrunner", "forsaken", F, 1, "down",
                    "The Horde stands with the Forsaken. Prove yourself worthy of that trust, and you shall not regret it."),
    "uc_royal_guard_1": ("Royal Guard Ashworth", "forsaken", M, 1, "down",
                         "The Banshee Queen receives only those who have earned the audience. State your business."),
    "uc_royal_guard_2": ("Royal Guard Venn", "forsaken", F, 3, "down",
                         "Eyes front. Weapons sheathed. Breathing is optional, but quiet is not."),
    "uc_executor": ("Executor Wrenfall", "forsaken", M, 5, "down",
                    "The Dark Lady's will does not wait. If you've the stomach for real work, I have it."),
    "uc_deathstalker": ("Deathstalker Rhyne", "forsaken", F, 14, "left",
                        "If you can see me, I wanted you to. Keep that in mind."),
    "uc_wanderer": ("Restless Corpse", "forsaken", M, 11, "up", "..."),
    # ---- the Magic Quarter
    "uc_mage_trainer": ("Magistrix Valdis", "forsaken", F, 6, "down",
                        "Frost, fire, arcane. The grave is cold, so I've a certain appreciation for frost."),
    "uc_warlock_trainer": ("Dreadmaster Kol'ven", "forsaken", M, 10, "down",
                           "The Burning Legion bargains for souls. I have learned to drive a harder deal."),
    "uc_priest_trainer": ("Dark Cleric Beryl", "forsaken", F, 2, "down",
                          "Shadow does not mean evil. It means honest about the dark. Come, learn."),
    "uc_summoning_master": ("Summoner Aldric Voss", "forsaken", M, 12, "down",
                            "Stand within the circle, and not one foot beyond. The last apprentice learned that the hard way."),
    "uc_enchanter": ("Enchantress Maeve Dunmoor", "forsaken", F, 9, "down",
                     "Bring me your best blade and a bad attitude. I'll improve one of the two."),
    "uc_scholar": ("Loremaster Sennarath", "blood_elf", M, 6, "left",
                   "I came to the Undercity for the archives, not the company. Though the company grows on you."),
    # ---- the War Quarter
    "uc_warrior_trainer": ("Battlemaster Grakk", "orc", M, 8, "down",
                           "Strength isn't built from comfort. Pick up a weapon and show me you're not afraid of bruises."),
    "uc_hunter_trainer": ("Ranger Isolde", "forsaken", F, 15, "down",
                          "Every hunter learns patience. The dead just learn it sooner."),
    "uc_beastmaster": ("Beastmaster Kovach", "forsaken", M, 7, "down",
                       "The bat doesn't mind that you're dead. That's why I trust it more than most people."),
    "uc_rogue_trainer": ("Shadowblade Kess", "forsaken", F, 5, "right",
                         "Quiet feet, quiet blades. If I hear you coming, we start over."),
    "uc_blacksmith": ("Smith Ironbrow", "forsaken", M, 4, "down",
                      "The forge is still hot. That's more than I can say for myself."),
    "uc_weaponsmith": ("Weaponsmith Torvald", "forsaken", M, 0, "down",
                       "A good edge lasts. I'd know. I've held mine for forty years past dying."),
    "uc_drillmaster": ("Drillmaster Hask", "forsaken", M, 12, "down",
                       "Again! The Scourge won't wait for you to catch your breath."),
    # ---- the Apothecarium
    "uc_apothecary": ("Apothecary Marwen", "forsaken", F, 1, "right",
                      "Plague research isn't for the squeamish. Neither is Undercity, come to that."),
    "uc_master_apothecary": ("Master Apothecary Lorrane Sable", "forsaken", F, 13, "down",
                             "Some of my own Society have turned their craft on the Dark Lady. The vaults below are theirs now. I want them cleaned out, and I want the ringleaders brought to account."),
    "uc_alchemist": ("Alchemist Dunmere", "forsaken", M, 3, "down",
                     "Stir clockwise. Always clockwise. The one time I didn't, I lost an arm. Again."),
    "uc_surgeon": ("Surgeon Halvard", "forsaken", M, 9, "left",
                   "Hold still. I do my best work on patients who are already past the screaming."),
    "uc_lab_assistant": ("Lab Assistant Pip", "forsaken", F, 11, "down",
                         "Don't touch the green one. Or the blue one. Or the one that looks like jam."),
    # ---- the Deeps Gate
    "uc_gatewarden": ("Gatewarden Sorrel", "forsaken", M, 6, "down",
                      "Beyond the gate lie the Plague Depths, and a cabal of Apothecary traitors who want the Dark Lady dead. If you hear screaming down there, it isn't mine."),
    "uc_deeps_guard": ("Deathguard Marik", "forsaken", M, 2, "down",
                       "Nobody's gone through that gate who wasn't ordered to. Remember that when you feel brave."),
    "uc_riding_trainer": ("Riding Instructor Cask", "forsaken", M, 15, "down",
                          "A skeletal horse is a patient steed. It will carry you forever, and it will never complain "
                          "about the road."),
}

# id: (name, race, gender, variant, facing, greeting, sells, gear_level, sells_gear)
VENDORS = {
    "uc_innkeeper": ("Innkeeper Nethra", "forsaken", F, 10, "left",
                     "Rest, if you can. If you can't, drink. Either way, it's a room with a roof.",
                     ["bread_and_cheese", "roasted_meat", "spiced_wine", "mushroom_broth"], 12, False),
    "uc_quartermaster": ("Quartermaster Dolan", "forsaken", M, 8, "down",
                         "The Royal Guard supplies, signed for in triplicate. I'll accept coin in lieu of a signature.",
                         ["healing_potion_minor", "healing_potion_standard"], 16, True),
    "uc_provisioner": ("Provisioner Nell", "forsaken", F, 14, "down",
                       "Rations, field kits, bandages. If you're going down to the Depths, take more than you think.",
                       ["bread_and_cheese", "roasted_meat", "spiced_stew", "healing_potion_minor"], 12, False),
    "uc_arcane_vendor": ("Arcanist Welsh", "forsaken", M, 6, "down",
                         "Reagents, focus crystals, and the finest mana draughts in Lordaeron's ruins.",
                         ["mana_potion_minor", "mana_potion_standard", "arcane_elixir"], 14, False),
    "uc_demonic_vendor": ("Imp-Keeper Zalnak", "forsaken", M, 10, "left",
                          "Soul shards, sacrifices, and small sulking imps. Please don't feed the imps after midnight.",
                          ["mana_potion_minor", "mana_potion_standard"], 14, False),
    "uc_elixir_trader": ("Elixir Dealer Quill", "forsaken", F, 7, "left",
                         "Elixirs for every occasion. The label is just a suggestion. Taste is up to you.",
                         ["battle_elixir_minor", "guardian_elixir_minor", "battle_elixir_standard",
                          "guardian_elixir_standard"], 16, False),
    "uc_reagent_vendor": ("Reagent Dealer Hollis", "forsaken", M, 13, "down",
                          "Powdered bone, grave-dirt, a hint of nightshade. Alchemists swear by it.",
                          ["healing_potion_minor", "mana_potion_minor", "elixir_of_warding"], 12, False),
    "uc_poison_vendor": ("Poisoner Sable", "forsaken", F, 3, "down",
                         "A single drop is plenty. Treat every bottle as if it were your last.",
                         ["elixir_of_agility", "battle_elixir_minor"], 14, False),
}

RECRUIT_NOTES = {"marco_paladin": "In the Trade Quarter, keeping the peace by the Seal.",
                 "sophia_mage": "In the Magic Quarter, surrounded by research.",
                 "ryan_warlock": "In the Magic Quarter, making deals by the summoning circle."}
SERVICES = {"uc_innkeeper": ["inn"], "uc_riding_trainer": ["riding"]}


def _upsert(data, key, id_key, rec):
    for i, r in enumerate(data[key]):
        if r.get(id_key) == rec[id_key]:
            data[key][i] = {**r, **rec}
            return 0
    data[key].append(rec)
    return 1


def main():
    amb = json.loads(Path("data/npcs/ambient_npcs.json").read_text(encoding="utf-8"))
    ven = json.loads(Path("data/npcs/vendors.json").read_text(encoding="utf-8"))
    added = 0
    for nid, (name, race, gender, var, facing, greet) in AMBIENT.items():
        x, y = NPC_POSITIONS[nid]
        added += _upsert(amb, "npcs", "npc_id", dict(npc_id=nid, name=name, zone="Undercity", x=x, y=y, greeting=greet,
                                                      gender=gender, race=race, appearance_variant=var, facing=facing))
    for vid, (name, race, gender, var, facing, greet, sells, gl, sg) in VENDORS.items():
        x, y = NPC_POSITIONS[vid]
        added += _upsert(ven, "vendors", "vendor_id", dict(
            vendor_id=vid, name=name, zone="undercity", x=x, y=y, tile_sprite="npc", sells=sells, buys_from_player=True,
            faction="forsaken", gear_level=gl, sells_gear=sg, race=race, appearance_variant=var, gender=gender,
            greeting=greet))
    # a vendor id must not also appear as ambient
    amb["npcs"] = [n for n in amb["npcs"] if n["npc_id"] not in VENDORS]
    Path("data/npcs/ambient_npcs.json").write_text(json.dumps(amb, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    Path("data/npcs/vendors.json").write_text(json.dumps(ven, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    rec = json.loads(Path("data/npcs/recruits.json").read_text(encoding="utf-8"))
    for r in rec["recruits"]:
        pos = RECRUITS.get(r["recruit_id"])
        if pos:
            r["x"], r["y"] = pos
            r["home_x"], r["home_y"] = pos
            if r["recruit_id"] in RECRUIT_NOTES:
                r["home_note"] = RECRUIT_NOTES[r["recruit_id"]]
    Path("data/npcs/recruits.json").write_text(json.dumps(rec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    fp = Path("data/npcs/forges.json")
    forges = json.loads(fp.read_text(encoding="utf-8"))
    f = next((q for q in forges["forges"] if q["forge_id"] == "undercity_forge"), None)
    if f is None:
        forges["forges"].append({"forge_id": "undercity_forge", "name": "Undercity Forge", "zone": "undercity",
                                 "x": FORGE[0], "y": FORGE[1]})
    else:
        f["x"], f["y"] = FORGE
    fp.write_text(json.dumps(forges, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    tp = Path("data/travel/travel_data.json")
    t = json.loads(tp.read_text(encoding="utf-8"))
    t["services"].update(SERVICES)
    tp.write_text(json.dumps(t, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"ambient {len(AMBIENT)}, vendors {len(VENDORS)}, +{added} new records")


if __name__ == "__main__":
    main()
