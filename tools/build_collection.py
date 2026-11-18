#!/usr/bin/env python3
"""The Collection's catalogue: every account-wide collectable, written to data/collection/collectables.json.

    python3 tools/build_collection.py            # dry run: counts and problems
    python3 tools/build_collection.py --write

docs/collection_design.md is the design and Kyle's answers (18 Nov 2026). Each entry is one thing you can buy on the
auction house, learn from your bags once, and then have on every character: a mount, a form, a travel unlock, a
portable service, a quality-of-life tome or an heirloom.

FIELDS
    id          collection id; the bag item carries it as `collection_id`
    name        the bag item's name, which is also what the Collection tab shows
    kind        mount | form | travel | service | tome | heirloom (the tab it's on: tomes sit on Travel)
    price       base price in copper, before the market's own price index moves it (Kyle: "50-750g")
    rarity      common | uncommon | rare | epic: how often it turns up on the auction house, and its name colour
    blurb       one line for the tooltip and the tab
    effect      what learning it does (world/collection.py reads it)
    icon_id     the bag icon. Stand-ins from the quest-item set until the Collection's own icon sheet lands
                (docs/collection_art_prompts.md); `art` names what the real icon will be called.
    needs_art   mounts and forms can be learned before their art lands, but not used until it does
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "collection" / "collectables.json"
G = 10000

RARITY_WEIGHT = {"common": 10.0, "uncommon": 5.0, "rare": 2.0, "epic": 0.7}

ITEMS = []


def add(cid, name, kind, gold, rarity, blurb, effect, icon, needs_art=False):
    ITEMS.append({"id": cid, "name": name, "kind": kind, "price": int(gold * G), "rarity": rarity, "blurb": blurb,
                  "effect": effect, "icon_id": icon, "art": f"col_{cid}", "needs_art": needs_art})


# ---------------------------------------------------------------- mounts (still need riding; ridden at your speed)
for cid, name, gold, rar, blurb in (
        ("bone_white_kodo", "Reins of the Bone-White Kodo", 300, "uncommon",
         "An elder's kodo from Thunder Bluff, pale as chalk and older than most towns."),
        ("steamwheedle_runabout", "Key to the Steamwheedle Runabout", 350, "uncommon",
         "A goblin's brass strider with a leaky boiler and no brakes worth the name."),
        ("tidecaller_sea_turtle", "Tidecaller Sea Turtle", 450, "rare",
         "A great turtle from the Tempest Isle shallows, slow to look at and quick under you."),
        ("dread_elk_of_felwood", "Reins of the Dread Elk", 500, "rare",
         "A black elk with green fire in its antlers, from the edge of the corrupted woods."),
        ("sunreach_hawkstrider", "Sunreach Hawkstrider", 600, "epic",
         "A tall gold and white strider bred by the Sunreach Conclave."),
        ("ashen_nightmare", "Reins of the Ashen Nightmare", 750, "epic",
         "A black horse with an ember mane, ridden out of the Plaguelands' worst night.")):
    add(cid, name, "mount", gold, rar, blurb, {"mount_id": cid}, "qi_trophy_cord", needs_art=True)

# ---------------------------------------------------------------- forms (map only: the party leader walks as it)
for cid, name, gold, rar, blurb in (
        ("murloc", "Murloc", 150, "common", "Mrglglgl."),
        ("kobold_miner", "Kobold Miner", 150, "common", "Candle included. You no take it."),
        ("gnoll_brute", "Gnoll Brute", 200, "uncommon", "Hunched, hungry and very pleased with itself."),
        ("treant_sapling", "Treant Sapling", 250, "uncommon", "A walking sprig of Ashenvale."),
        ("little_ooze", "Little Ooze", 250, "uncommon", "It squelches. It's happy."),
        ("carrion_crow", "Carrion Crow", 300, "uncommon", "Hops more than it flies."),
        ("furbolg_elder", "Furbolg Elder", 350, "rare", "A grey-muzzled furbolg with a walking stick."),
        ("wandering_skeleton", "Wandering Skeleton", 400, "rare", "The Forsaken find it in poor taste."),
        ("spirit_wolf", "Spirit Wolf", 600, "epic", "A ghostly wolf that leaves no tracks."),
        ("shade_of_the_drowned_court", "Shade of the Drowned Court", 700, "epic",
         "A drowned courtier of the old queen, walking in a cold blue light.")):
    add(cid, f"Charm of the {name}" if cid != "shade_of_the_drowned_court" else "Charm of the Drowned Shade",
        "form", gold, rar, blurb, {"form_id": cid, "form_name": name}, "qi_totem", needs_art=True)

# ---------------------------------------------------------------- travel
add("feather_kalimdor", "Windrider Feather of Kalimdor", "travel", 400, "rare",
    "Every flight path in Kalimdor is open to every character.", {"feather": "kalimdor"}, "qi_pennant")
add("feather_eastern_kingdoms", "Windrider Feather of the Eastern Kingdoms", "travel", 400, "rare",
    "Every flight path in the Eastern Kingdoms is open to every character.", {"feather": "eastern_kingdoms"},
    "qi_pennant")
add("tome_swift_hearth", "Tome of the Swift Hearth", "travel", 300, "uncommon",
    "The hearthstone's cooldown is halved, for every character.", {"hearth_cooldown_mult": 0.5}, "qi_journal")
add("second_hearthstone", "Hearthstone of the Second Home", "travel", 300, "rare",
    "A second hearthstone, with its own bind and its own cooldown.", {"second_hearth": True}, "qi_heart_stone")

# ---------------------------------------------------------------- services (once per market day each)
for cid, name, gold, rar, service, blurb, icon in (
        ("travelling_bank", "Satchel of the Travelling Bank", 250, "uncommon", "bank",
         "Opens your bank anywhere.", "qi_strongbox"),
        ("peddlers_bell", "Peddler's Bell", 150, "common", "peddler",
         "Calls a pack-mule peddler who buys anything you're carrying.", "qi_lantern"),
        ("couriers_horn", "Courier's Horn", 150, "common", "mail",
         "A courier brings your mail and takes your letters out.", "qi_horn"),
        ("book_wandering_master", "Book of the Wandering Master", 200, "uncommon", "class_trainer",
         "Opens your class trainer anywhere.", "qi_ledger"),
        ("book_of_professions", "Book of Professions", 200, "uncommon", "profession_trainer",
         "Opens a profession trainer anywhere, for any profession.", "qi_ledger"),
        ("alchemists_satchel", "Alchemist's Satchel", 200, "uncommon", "reagents",
         "Opens a reagent seller anywhere.", "qi_coin_pouch")):
    add(cid, name, "service", gold, rar, blurb + " Once per market day.", {"service": service}, icon)

# ---------------------------------------------------------------- quality-of-life tomes
add("tome_pack_mule", "Tome of the Pack Mule", "tome", 350, "rare",
    "Every character's backpack holds 12 more.", {"backpack_bonus": 12}, "qi_journal")
add("tome_deep_vault", "Tome of the Deep Vault", "tome", 300, "rare",
    "Every character's bank gets one more tab, free: the Collector's Shelf.", {"bonus_bank_tabs": 1}, "qi_journal")
add("tome_quick_study", "Tome of the Quick Study", "tome", 250, "uncommon",
    "Apprentice Riding costs nothing at the riding trainer, for every character.", {"free_riding_rank": 1}, "qi_journal")
add("book_first_steps", "Book of First Steps", "tome", 100, "common",
    "New characters start with a six-slot bag and 5 gold.", {"new_character": {"copper": 5 * G, "bag": True}},
    "qi_journal")

# ---------------------------------------------------------------- heirlooms (fit the wearer; +80% XP in all)
for cid, name, slot, xp, gold, rar in (
        ("heirloom_head", "Heirloom Helm", "head", 10, 150, "common"),
        ("heirloom_shoulder", "Heirloom Shoulders", "shoulder", 10, 150, "common"),
        ("heirloom_chest", "Heirloom Chest", "chest", 10, 180, "uncommon"),
        ("heirloom_legs", "Heirloom Legs", "legs", 10, 180, "uncommon"),
        ("heirloom_back", "Heirloom Cloak", "back", 10, 120, "common"),
        ("heirloom_trinket", "Heirloom Trinket", "trinket", 10, 200, "uncommon"),
        ("heirloom_two_hand", "Heirloom Two-Hander", "two_hand", 20, 300, "rare"),
        ("heirloom_one_hand", "Heirloom One-Hander", "one_hand", 10, 150, "common"),
        ("heirloom_shield", "Heirloom Shield", "shield", 10, 120, "common"),
        ("heirloom_off_hand", "Heirloom Off-Hand", "off_hand", 10, 120, "common")):
    add(cid, name, "heirloom", gold, rar,
        f"Fits whoever takes it, levels with them, and gives +{xp}% experience while worn (until 60).",
        {"heirloom_slot": slot, "xp_pct": xp}, "qi_signet")


def problems():
    out = []
    ids = [i["id"] for i in ITEMS]
    if len(ids) != len(set(ids)):
        out.append("duplicate ids")
    names = [i["name"] for i in ITEMS]
    if len(names) != len(set(names)):
        out.append("duplicate names")
    for i in ITEMS:
        if not 50 * G <= i["price"] <= 750 * G:
            out.append(f"{i['id']}: price {i['price'] // G}g is outside Kyle's 50-750g")
        if i["rarity"] not in RARITY_WEIGHT:
            out.append(f"{i['id']}: rarity {i['rarity']}")
        if not (ROOT / "assets/icons/quest_items" / f"{i['icon_id']}.png").exists():
            out.append(f"{i['id']}: no icon {i['icon_id']}")
    xp = sum(i["effect"]["xp_pct"] for i in ITEMS if i["kind"] == "heirloom"
             and i["effect"]["heirloom_slot"] not in ("one_hand", "shield", "off_hand"))
    if xp != 80:
        out.append(f"a full heirloom set with a two-hander gives {xp}%, not Kyle's 80%")
    return out


def main():
    p = problems()
    kinds = {}
    for i in ITEMS:
        kinds[i["kind"]] = kinds.get(i["kind"], 0) + 1
    print(f"  {len(ITEMS)} collectables: " + ", ".join(f"{n} {k}" for k, n in kinds.items()))
    for x in p:
        print("  PROBLEM " + x)
    if "--write" in sys.argv and not p:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps({"_about": "Built by tools/build_collection.py; docs/collection_design.md",
                                   "rarity_weight": RARITY_WEIGHT, "collectables": ITEMS},
                                  indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"  written {OUT.relative_to(ROOT)}")
    return 1 if p else 0


if __name__ == "__main__":
    sys.exit(main())
