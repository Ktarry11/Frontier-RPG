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
    price       base price in copper, before the market's own price index moves it. Kyle: "50-750g", then for the
                mass-made kinds "Some are dirt cheap. Some are expensive", so 2g to 750g
    rarity      common | uncommon | rare | epic: how often it turns up on the auction house, and its name colour
    blurb       one line for the tooltip and the tab
    effect      what learning it does (world/collection.py reads it)
    icon_id     the bag icon. Stand-ins from the quest-item set until the Collection's own icon sheet lands
                (docs/collection_art_prompts.md); `art` names what the real icon will be called.
    needs_art   mounts and forms can be learned before their art lands, but not used until it does
"""
import json
import re
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
OUT = ROOT / "data" / "collection" / "collectables.json"
G = 10000

RARITY_WEIGHT = {"common": 10.0, "uncommon": 5.0, "rare": 2.0, "epic": 0.7}

ITEMS = []


def add(cid, name, kind, gold, rarity, blurb, effect, icon, needs_art=False):
    ITEMS.append({"id": cid, "name": name, "kind": kind, "price": int(gold * G), "rarity": rarity, "blurb": blurb,
                  "effect": effect, "icon_id": icon, "art": f"col_{cid}", "needs_art": needs_art})


# ---------------------------------------------------------------- mounts (still need riding; ridden at your speed)
for cid, name, gold, rar, blurb in (
        ("bone_white_kodo", "Bone-White Kodo", 300, "uncommon",
         "An elder's kodo from Thunder Bluff, pale as chalk and older than most towns."),
        ("steamwheedle_runabout", "Steamwheedle Runabout", 350, "uncommon",
         "A goblin's brass strider with a leaky boiler and no brakes worth the name."),
        ("tidecaller_sea_turtle", "Tidecaller Sea Turtle", 450, "rare",
         "A great turtle from the Tempest Isle shallows, slow to look at and quick under you."),
        ("dread_elk_of_felwood", "Dread Elk", 500, "rare",
         "A black elk with green fire in its antlers, from the edge of the corrupted woods."),
        ("sunreach_hawkstrider", "Sunreach Hawkstrider", 600, "epic",
         "A tall gold and white strider bred by the Sunreach Conclave."),
        ("ashen_nightmare", "Ashen Nightmare", 750, "epic",
         "A black horse with an ember mane, ridden out of the Plaguelands' worst night.")):
    add(cid, f"Reins of the {name}", "mount", gold, rar, blurb, {"mount_id": cid, "mount_name": name, "tier": 1},
        "qi_trophy_cord", needs_art=True)

# MOUNT COLOURWAYS (Kyle: "Mount colours", then "don't full colour shift mounts. Hue shift them. And I'll get art"):
# every mount in seven hue-shifted colourways, made from its own art when drawn (world/collection_art.py).
COLOUR_NAMES = {"rose": "Rose", "dawn": "Dawn", "spring": "Spring", "jade": "Jade", "tide": "Tide",
                "dusk": "Dusk", "twilight": "Twilight"}
COLOUR_BAND = {"rose": ("uncommon", (25, 60, 140)), "dawn": ("uncommon", (25, 60, 140)),
               "spring": ("uncommon", (25, 60, 140)), "jade": ("rare", (100, 180, 300)),
               "tide": ("rare", (100, 180, 300)), "dusk": ("rare", (120, 200, 320)),
               "twilight": ("epic", (350, 450, 600))}
COLOUR_LINE = {"rose": "in rose and wine colours", "dawn": "in the colours of first light",
               "spring": "in the colours of new leaves", "jade": "with a jade sheen",
               "tide": "in the blues of a turning tide", "dusk": "in the colours of dusk",
               "twilight": "in the deep colours of twilight"}


def _travel_mounts():
    return json.loads((ROOT / "data/travel/travel_data.json").read_text(encoding="utf-8"))["mounts"]


for m in _travel_mounts():
    for colour, cname in COLOUR_NAMES.items():
        rar, bands = COLOUR_BAND[colour]
        gold = bands[min(2, m["tier"] - 1)]
        mname = f"{cname} {m['name']}"
        add(f"{colour}_{m['id']}", f"Reins of the {mname}", "mount", gold, rar,
            f"A {m['name'].lower()} {COLOUR_LINE[colour]}.",
            {"mount_id": f"{colour}_{m['id']}", "mount_name": mname, "tier": m["tier"]}, "qi_trophy_cord")

# ---------------------------------------------------------------- forms (map only: the party leader walks as it)
# The ten named in the design, each worn with a creature picture the game already has (two tinted by
# tools/build_collection_art.py), then one form for every other creature picture in the open world.
CURATED_FORMS = (
    ("murloc", "Murloc", 15, "common", "Mrglglgl.", "assets/creatures/murloc_1.png"),
    ("kobold_miner", "Kobold Miner", 15, "common", "Candle included. You no take it.",
     "assets/creatures/kobold_1.png"),
    ("gnoll_brute", "Gnoll Brute", 40, "uncommon", "Hunched, hungry and very pleased with itself.",
     "assets/creatures/gnoll_2.png"),
    ("treant_sapling", "Treant", 60, "uncommon", "A walking sprig of Ashenvale.", "assets/creatures/treant_1.png"),
    ("little_ooze", "Ooze", 50, "uncommon", "It squelches. It's happy.", "assets/creatures/ooze_acid_1.png"),
    ("carrion_crow", "Carrion Vulture", 60, "uncommon", "Hops more than it flies.",
     "assets/creatures/pl_carrion_vulture.png"),
    ("furbolg_elder", "Furbolg", 150, "rare", "A grey-muzzled furbolg with a walking stick.",
     "assets/creatures/furbolg.png"),
    ("wandering_skeleton", "Wandering Skeleton", 200, "rare", "The Forsaken find it in poor taste.",
     "assets/creatures/skeleton_warrior_1.png"),
    ("spirit_wolf", "Spirit Wolf", 600, "epic", "A ghostly wolf that leaves no tracks.",
     "assets/collection/forms/spirit_wolf.png"),
    ("shade_of_the_drowned_court", "Shade of the Drowned Court", 700, "epic",
     "A drowned courtier of the old queen, walking in a cold blue light.",
     "assets/collection/forms/shade_of_the_drowned_court.png"))
for cid, name, gold, rar, blurb, sprite in CURATED_FORMS:
    add(cid, f"Charm of the {name}", "form", gold, rar, blurb, {"form_id": cid, "form_name": name, "sprite": sprite},
        "qi_totem")


def _jitter(key, lo, hi):
    """A steady price between lo and hi for this key, so a rebuild never reprices anything."""
    return lo + (zlib.crc32(key.encode("utf-8")) % 1000) / 999.0 * (hi - lo)


def creature_forms():
    """One form per creature picture used in the open world: named for the earliest ordinary creature that wears it
    (a boss's name only when nothing else does), priced and graded by that creature's level. Nothing that lives in a
    hidden place is ever a form, and nothing above 60."""
    import creature_sprites as CS
    from world.hidden_zones import creature_kinds
    hidden = set(creature_kinds()) | set(CS._hidden_sprites())
    raw = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))
    creatures = raw.get("creatures", raw)
    used = {sprite.split("/")[-1][:-4] for *_x, sprite in CURATED_FORMS}
    by = {}
    for name, c in creatures.items():
        if name in hidden or not isinstance(c, dict):
            continue
        lo, hi = (c.get("level_range") or [1, 1])[:2]
        if lo > 60:
            continue
        sid = CS.sprite_file(name, c.get("template"))
        if sid in used or not CS.sprite_path(sid).exists():
            continue
        by.setdefault(sid, []).append((bool(c.get("is_boss")), lo, len(name), name))
    taken = {e["name"] for e in ITEMS}
    out = []
    for sid in sorted(by):
        rows = sorted(by[sid])
        boss_only = all(r[0] for r in rows)
        for boss, lo, _n, name in rows:
            if f"Charm of the {name}" not in taken:
                break
        else:
            continue
        taken.add(f"Charm of the {name}")
        label = f"Charm of {name}" if boss_only or name.startswith("The ") else f"Charm of the {name}"
        if boss_only:
            rar, (a, b) = ("rare", (150, 300)) if lo < 30 else ("epic", (300, 750))
            gold = _jitter(sid, a, a + (b - a) * min(1.0, lo / 60.0))
            blurb = f"Walk the map as {name}, which most people only ever see at the end of a dungeon."
        else:
            bands = [(10, "common", 2, 8), (20, "common", 8, 25), (30, "uncommon", 25, 60), (40, "uncommon", 60, 120),
                     (50, "rare", 120, 220), (60, "rare", 220, 350)]
            top, rar, a, b = next(x for x in bands if lo <= x[0])
            gold = _jitter(sid, a, b)
            blurb = f"Walk the map as {'an' if name[0] in 'AEIOU' else 'a'} {name}."
        out.append((f"form_{sid}", name, label, max(2, int(round(gold))), rar, blurb, f"assets/creatures/{sid}.png"))
    return out


for cid, name, label, gold, rar, blurb, sprite in creature_forms():
    add(cid, label, "form", gold, rar, blurb, {"form_id": cid, "form_name": name, "sprite": sprite},
        "qi_totem")

# ---------------------------------------------------------------- titles (text with your name)
from collection_titles import COMMON, UNCOMMON, RARE, EPIC  # noqa: E402
for rar, titles, (a, b) in (("common", COMMON, (2, 15)), ("uncommon", UNCOMMON, (20, 80)),
                            ("rare", RARE, (100, 250)), ("epic", EPIC, (300, 750))):
    for t in titles:
        slug = re.sub(r"[^a-z0-9]+", "_", t.replace("{name}", "").lower()).strip("_")
        shown = t.replace("{name}", "...").replace(" ...", "").replace("... ", "").replace("...,", "").strip(" ,")
        add(f"title_{slug}", f"Title: {shown}", "title", int(round(_jitter(slug, a, b))), rar,
            f"Shown with your name: {t.replace('{name}', 'You')}.", {"title": t}, "qi_scroll")

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
        if not 2 * G <= i["price"] <= 750 * G:
            out.append(f"{i['id']}: price {i['price'] // G}g is outside 2-750g (Kyle: \"Some are dirt cheap. Some "
                       f"are expensive\", up to 750g)")
        if i["kind"] == "form" and not (ROOT / i["effect"]["sprite"]).exists():
            out.append(f"{i['id']}: no picture {i['effect']['sprite']}")
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
