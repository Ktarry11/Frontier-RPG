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
    kind        mount | form | travel | service | tome | heirloom | keepsake (the tab it's on: tomes sit on Travel)
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
    if needs_art and kind == "mount" and all(
            (ROOT / f"assets/mounts/{cid}_{d}.png").exists() for d in ("down", "left", "right", "up")):
        needs_art = False   # its sheet has landed
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

# ---------------------------------------------------------------- heirlooms
# Kyle, 18 Nov 2026: "We should have the heirlooms as we need cloth, leather, mail, and plate. And all the weapons,
# shields, OH, etc.", "You know how heirlooms work", then the generalist families: "caster cloth, healer cloth, agi
# leather, healer leather, caster leather, dps mail, caster mail, healer mail. Dps plate, tank plate, hybrid plate,
# healer plate." And: "these armor pieces need to level up with the player! So they can be worn at lvl 1 or lvl 60.
# But obviously they will be slightly worse than items of the same level... They also affect the whole party."
# Each heirloom is its own item with a set armour (or weapon) type and family; world/collection.py makes it at the
# wearer's level with the family's fixed stats, a little under a blue. Twelve armour families x four pieces, a cloak
# and a trinket per family, and every weapon a spec actually wields in its family.
# XP (Kyle): a two-hander +20%; a one-hander, shield or off-hand +10%; each armour piece, cloak and trinket +10%;
# +80% at most, read off the leader for the whole party. Ranged-slot pieces scale but give no XP.
FAMILY_NAME = {"caster": ("Dusty", "Archmage"), "healer": ("Faded", "Lightwarden"), "agi": ("Worn", "Nightstalker"),
               "str": ("Bloodied", "Warbringer"), "tank": ("Battle-Worn", "Bulwark"),
               "hybrid": ("Burnished", "Crusader")}
FAMILY_WORDS = {"caster": "intellect and spell power", "healer": "intellect, spirit and healing",
                "agi": "agility", "str": "strength", "tank": "stamina, strength and defense",
                "hybrid": "strength and intellect"}
ARMOUR_WORDS = {"cloth": ("Hood", "Mantle", "Robe", "Leggings"), "leather": ("Cap", "Spaulders", "Tunic", "Breeches"),
                "mail": ("Coif", "Pauldrons", "Hauberk", "Legguards"),
                "plate": ("Helm", "Shoulderguards", "Breastplate", "Legplates")}
ARMOUR_SLOTS = (("head", 0, "col_heirloom_head"), ("shoulder", 1, "col_heirloom_shoulder"),
                ("chest", 2, "col_heirloom_chest"), ("legs", 3, "col_heirloom_chest"))
WEAPON_WORD = {"sword_1h": "Blade", "sword_2h": "Greatsword", "axe_1h": "Axe", "axe_2h": "Greataxe", "mace_1h": "Mace",
               "mace_2h": "Maul", "dagger": "Dagger", "fist_weapon": "Fist", "staff": "Staff", "polearm": "Halberd",
               "bow": "Longbow", "gun": "Rifle", "crossbow": "Crossbow", "wand": "Wand", "thrown": "Throwing Knives",
               "shield": "Shield", "tome": "Tome", "totem": "Totem", "libram": "Libram", "idol": "Idol"}
WEAPON_ICON = {"shield": "col_heirloom_shield", "tome": "col_book_master"}


def _spec_gear():
    return {k: v for k, v in json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8")).items()
            if not k.startswith("_")}


def _hands():
    return {k: v.get("hand") for k, v in json.loads((ROOT / "data/items/weapon_types.json").read_text(
        encoding="utf-8"))["weapon_types"].items()}


def heirlooms():
    from world.collection import ARMOUR_FAMILIES, weapon_family
    specs = _spec_gear()
    hands = _hands()
    weapon_fams = sorted({weapon_family(v) for v in specs.values()})
    weapons = sorted({(wt, weapon_family(v)) for v in specs.values() for wt in (v.get("weapons") or {}).values()
                      if wt} | {("shield", "tank")})
    for armour, fams in ARMOUR_FAMILIES.items():
        for fam in fams:
            adj, who = FAMILY_NAME[fam]
            for slot, k, icon in ARMOUR_SLOTS:
                word = ARMOUR_WORDS[armour][k]
                yield (f"heirloom_{armour}_{fam}_{slot}", f"{adj} {who}'s {word}",
                       150 if slot in ("head", "legs") else 180, "uncommon",
                       f"Heirloom {armour} with {FAMILY_WORDS[fam]}. It levels with whoever wears it, from 1 to 60, "
                       f"and gives the whole party +10% experience while the leader wears it.",
                       {"heirloom_slot": slot, "armor_type": armour, "family": fam, "xp_pct": 10}, icon)
    for fam in weapon_fams:
        adj, who = FAMILY_NAME[fam]
        yield (f"heirloom_{fam}_back", f"Inherited Cloak of the {who}", 120, "common",
               f"An heirloom cloak with {FAMILY_WORDS[fam]}. It levels with whoever wears it and gives the whole "
               f"party +10% experience while the leader wears it.",
               {"heirloom_slot": "back", "armor_type": "cloth", "family": fam, "xp_pct": 10}, "col_heirloom_back")
        yield (f"heirloom_{fam}_trinket", f"{who}'s Keepsake", 200, "uncommon",
               f"An heirloom trinket with {FAMILY_WORDS[fam]}. It levels with whoever carries it and gives the whole "
               f"party +10% experience while the leader carries it.",
               {"heirloom_slot": "trinket", "family": fam, "xp_pct": 10}, "col_hearthstone_2")
    for wt, fam in weapons:
        adj, who = FAMILY_NAME[fam]
        hand = hands.get(wt)
        xp = 20 if hand == "two_hand" else (10 if hand in ("main_or_off", "off_hand") else 0)
        slot = {"two_hand": "two_hand", "main_or_off": "one_hand", "off_hand": "off_hand"}.get(hand, "ranged")
        gold = {20: 300, 10: 150, 0: 120}[xp]
        line = (f"gives the whole party +{xp}% experience while the leader wields it" if xp
                else "gives no experience bonus (it's a ranged-slot piece)")
        yield (f"heirloom_{wt}_{fam}", f"{adj} {who}'s {WEAPON_WORD.get(wt, wt.title())}", gold,
               "rare" if xp == 20 else "uncommon",
               f"An heirloom with {FAMILY_WORDS[fam]}. It levels with whoever wields it and {line}.",
               {"heirloom_slot": slot, "weapon_type": wt, "family": fam, "xp_pct": xp},
               WEAPON_ICON.get(wt, "col_heirloom_two_hand"))


for cid, name, gold, rar, blurb, effect, icon in heirlooms():
    add(cid, name, "heirloom", gold, rar, blurb, effect, icon)


# ---------------------------------------------------------------- fishing (docs/harvest_finds_design.md)
# Kyle, 18 Nov 2026, on something unique to fishing: "Collection mounts" and "Titles". Caught or earned, so FOUND
# ONLY: no trader lists them (world/market/market._list_collectable). One you caught is still yours to sell.
import harvest_finds_content as _HFC  # noqa: E402

for cid, name, _pools, blurb in _HFC.MOUNTS:
    add(cid, f"Reins of the {name}", "mount", 500, "epic", blurb, {"mount_id": cid, "mount_name": name, "tier": 1},
        f"col_reins_{cid}", needs_art=True)
    ITEMS[-1].update(found_only=True, source="fishing")
for cid, title, how, _need in _HFC.TITLES:
    add(cid, f"Title: {title}", "title", 60, "rare", f"Shown with your name: You {title}. {how}",
        {"title": "{name} " + title}, "col_title_rare")
    ITEMS[-1].update(found_only=True, source="fishing")

# ---------------------------------------------------------------- auction house exclusives (sheet H4)
# Kyle, 18 Nov 2026: "3 art prompts for mounts that are AH exclusive" (docs/ah_mount_art_prompts.md). Only ever put
# up by the house's traders, like every collectable; these three have no other source at all, and are the dearest.
AH_EXCLUSIVE = (
    ("bazaar_brute", "Bazaar Brute", "A walking marketplace: a great brute with a goblin stall lashed to its back."),
    ("coinscale_raptor", "Coinscale Raptor", "A bronze raptor barded in a few hundred gold coins, and proud of it."),
    ("velvet_saber", "Velvet Saber", "A midnight sabre cat in plum velvet and pearls. Elegant, and very sharp."),
    # sheets H5 to H7, 18 Nov 2026: "4 more mounts please", "more!", "one more"
    ("ledger_tortoise", "Ledger Tortoise", "A gold-leaf tortoise with a padlocked vault on its back. Slow, and rich."),
    ("silkwind_strider", "Silkwind Strider", "A tall plumed strider in teal silk and little gold bells."),
    ("goldtusk_boar", "Goldtusk Boar", "A war boar whose tusks are capped in gold and ringed with rubies."),
    ("platinum_direwolf", "Platinum Direwolf", "A white direwolf in engraved platinum, with sapphires on its brow."),
    ("ruby_scorpid", "Ruby Scorpid", "A scorpid lacquered red and gold, with a ruby set in its golden sting."),
    ("golden_dromedary", "Golden Dromedary", "A haughty camel under a silk canopy, hung with rows of gold coins."),
    ("obsidian_rhino", "Obsidian Rhino", "A rhino plated in obsidian and gold, with a gold-sheathed horn."),
    ("jadehorn_elk", "Jadehorn Elk", "A great elk with antlers of carved jade, hung with little gold charms."),
    ("gilded_bone_steed", "Gilded Bone Steed", "A skeletal warhorse plated in gold, burning with violet ghost-fire."),
    ("gilded_mechanostrider", "Gilded Mechanostrider", "A gold-plated goblin strider. It smokes, and it's very shiny."),
    ("crowned_grizzly", "Crowned Grizzly", "A colossal black bear in a gold crown and an ermine-trimmed robe."),
    ("emerald_basilisk", "Emerald Basilisk", "A long low basilisk whose scales glitter like cut emeralds."),
)
for cid, name, blurb in AH_EXCLUSIVE:
    add(cid, f"Reins of the {name}", "mount", 750, "epic", blurb, {"mount_id": cid, "mount_name": name, "tier": 1},
        f"col_reins_{cid}", needs_art=True)
    ITEMS[-1].update(source="auction_house")

# AUCTION HOUSE FORMS (sheet F2, single pictures, 18 Nov 2026: "more special shape shift forms after to be sold on
# AH!"). Map only, like every form; put up only by the house's traders.
AH_FORMS = (
    ("tycoon_golem", "Tycoon Golem", "A gold clockwork golem with a coin slot for a belly and a hat for a head."),
    ("treasure_mimic", "Treasure Mimic", "A chest of gold on little clawed feet. It bites."),
    ("pearl_murloc_king", "Pearl Murloc King", "A very smug murloc in a crown of clam shell and pearls."),
    ("bronze_drakonid", "Bronze Drakonid", "A winged dragon-man in bronze scales, holding an hourglass of glowing sand."),
    ("gilded_infernal", "Gilded Infernal", "A fel-burning rock giant with gold bands riveted onto its fists."),
    ("spirit_ancestor", "Spirit Ancestor", "A tauren elder walking in pale blue spirit light."),
    ("living_geode", "Living Geode", "A rock elemental split open to show the amethyst inside."),
    ("opulent_furbolg", "Opulent Furbolg", "A cheerful furbolg in gold beads, gems and an embroidered vest."),
    ("goldleaf_treant", "Goldleaf Treant", "An old treant whose leaves have all turned to autumn gold."),
    ("silken_harpy_matriarch", "Silken Harpy Matriarch", "A harpy queen in emerald and gold feathers."),
    ("ember_djinn", "Ember Djinn", "A grinning fire spirit that trails off into smoke below the waist."),
    ("goldtooth_pirate_ghost", "Goldtooth Pirate Ghost", "A ghostly pirate captain with a grin full of gold."),
)
for cid, name, blurb in AH_FORMS:
    _fx = {"form_id": cid, "form_name": name, "sprite": f"assets/collection/forms/{cid}.png"}
    # sheets F6 and F7 (19 Nov 2026) turned each one four ways: walked in its facings once they're on disk
    if all((ROOT / f"assets/forms/{cid}_{d}.png").exists() for d in ("down", "left", "right", "up")):
        _fx["facings"] = f"assets/forms/{cid}"
    add(cid, f"Charm of the {name}", "form", 700, "epic", blurb, _fx, f"col_charm_{cid}")
    ITEMS[-1].update(source="auction_house")

# SHAPESHIFT LOOKS (sheets F3 to F5, 18 Nov 2026: "We need each form - Bears, beetles, cats, tree of life, spiders.
# All 4 angles. Some common and some rare!" and "throw some of these in the collection for alternative forms!").
# A look changes how a class form walks the map (world/collection.class_form_path); it doesn't change the form.
LOOK_PRICE = {"common": 40, "uncommon": 120, "rare": 400}
# stand-ins until sheet I1 (docs/form_art_prompts.md) gives every look its own icon
LOOK_ICON = {"bear": "col_charm_beast", "cat": "col_charm_beast", "moonkin": "col_charm_beast",
             "tree_of_life": "col_charm_plant", "spider": "col_charm_insect", "beetle": "col_charm_insect"}
FORM_LOOKS = (
    ("bear_black", "bear", "Black Bear", "common", "Bear Form in glossy black fur, with a tan muzzle."),
    ("bear_ironhide", "bear", "Ironhide Bear", "uncommon", "Bear Form armoured in bark and moss, mushrooms and all."),
    ("bear_frostmane", "bear", "Frostmane Bear", "rare", "Bear Form as a white bear with ice growing from its back."),
    ("cat_plains_lion", "cat", "Plains Lion", "common", "Cat Form as a tawny mountain lion."),
    ("cat_snow_leopard", "cat", "Snow Leopard", "uncommon", "Cat Form in white fur and dark rosettes."),
    ("cat_starlight", "cat", "Starlight Panther", "rare", "Cat Form in midnight fur full of stars."),
    ("tree_autumn", "tree_of_life", "Autumn Tree", "common", "Tree of Life in red and orange leaves."),
    ("tree_willow", "tree_of_life", "Willow Tree", "uncommon", "Tree of Life as a weeping willow, fireflies included."),
    ("tree_moonwood", "tree_of_life", "Moonwood Tree", "rare", "Tree of Life in silver bark and glowing blue leaves."),
    ("spider_forest", "spider", "Forest Spider", "common", "Spider Form as a big hairy brown spider."),
    ("spider_sand", "spider", "Sand Spider", "uncommon", "Spider Form in pale desert yellow and black bands."),
    ("spider_crystal_widow", "spider", "Crystal Widow", "rare", "Spider Form made of glowing violet crystal."),
    ("beetle_dusk", "beetle", "Dusk Scarab", "common", "Beetle Form in a plain dark brown shell."),
    ("beetle_jade", "beetle", "Jade Scarab", "uncommon", "Beetle Form in shining metallic green."),
    ("beetle_sunfire", "beetle", "Sunfire Scarab", "rare", "Beetle Form in gold with glowing orange runes."),
    ("moonkin_snowy", "moonkin", "Snowy Moonkin", "common", "Moonkin Form in white feathers."),
    ("moonkin_dusk", "moonkin", "Dusk Moonkin", "uncommon", "Moonkin Form in slate and violet."),
    ("moonkin_solar", "moonkin", "Solar Moonkin", "rare", "Moonkin Form in glowing golden feathers."),
    # sheets F8 to F10 (19 Nov 2026)
    ("dire_bear_brown", "dire_bear", "Brown Dire Bear", "common", "Dire Bear Form as a huge brown bear with a torn ear."),
    ("dire_bear_thornhide", "dire_bear", "Thornhide Dire Bear", "uncommon",
     "Dire Bear Form grown over with thorns and briar, red berries and all."),
    ("dire_bear_ancient", "dire_bear", "Ancient Guardian", "rare",
     "Dire Bear Form in moss and stone, green runes glowing on its shoulders."),
    ("void_monstrosity_drowned", "void_monstrosity", "Drowned Horror", "common",
     "The Void Monstrosity slick and grey-green, crusted with barnacles."),
    ("void_monstrosity_ashen", "void_monstrosity", "Ashen Horror", "uncommon",
     "The Void Monstrosity in cracked black stone, red light in the cracks."),
    ("void_monstrosity_starving", "void_monstrosity", "Starving Dark", "rare",
     "The Void Monstrosity made of a starfield, and far too many eyes."),
    ("shadowform_grey", "shadowform", "Grey Shade", "common", "Shadowform as thin grey smoke."),
    ("shadowform_ember", "shadowform", "Ember Shade", "uncommon", "Shadowform in black smoke with embers drifting through it."),
    ("shadowform_eclipse", "shadowform", "Eclipse Shade", "rare", "Shadowform with an eclipse's ring of light behind its hood."),
    ("mechsuit_rustbucket", "mechsuit", "Rustbucket Mechsuit", "common", "The Mechsuit patched with rusty, mismatched plates."),
    ("mechsuit_cobalt", "mechsuit", "Cobalt Mechsuit", "uncommon", "The Mechsuit in clean cobalt enamel with a blue core."),
    ("mechsuit_goldplated", "mechsuit", "Gold-Plated Mechsuit", "rare", "The Mechsuit in polished gold with ruby rivets."),
    ("weaver_dusk", "weaver", "Dusk Weaver", "common", "Weaver Form in dull brown chitin, spinning grey silk."),
    ("weaver_silkmother", "weaver", "Silkmother Weaver", "uncommon", "Weaver Form robed in fine white silk."),
    ("weaver_spectral", "weaver", "Spectral Weaver", "rare", "Weaver Form made of pale blue ghost light."),
    ("vizier_bronze", "vizier_form", "Bronze Vizier", "common", "Vizier Form in bronze chitin and plain brown robes."),
    ("vizier_obsidian", "vizier_form", "Obsidian Vizier", "uncommon", "Vizier Form in black chitin and crimson robes."),
    ("vizier_royal", "vizier_form", "Royal Vizier", "rare", "Vizier Form in royal purple and gold, emeralds in its crown."),
)
LOOK_ICON.update({"dire_bear": "col_charm_beast", "void_monstrosity": "col_charm_drowned", "shadowform": "col_charm_spirit",
                  "mechsuit": "col_charm_beast", "weaver": "col_charm_insect", "vizier_form": "col_charm_insect"})
#: Looks drawn (sheet F9) for something that isn't a form you walk the map in: the Tinker's Mechsuit is a timed buff
#: inside a fight, and the combat screen still draws the person (backlog section 10, "Class forms in combat"). Held
#: off the AH until a fight draws forms, so nobody buys a look that never shows. Their art stays in assets/forms.
HELD_LOOKS = {"mechsuit"}

for cid, base, name, rar, blurb in FORM_LOOKS:
    if base in HELD_LOOKS:
        continue
    # each look's own icon from sheet I1 (19 Nov 2026), the family charm until then
    _icon = f"col_look_{cid}" if (ROOT / f"assets/icons/collection/col_look_{cid}.png").exists() else LOOK_ICON[base]
    add(f"look_{cid}", f"Look: {name}", "form", LOOK_PRICE[rar], rar, blurb,
        {"form_id": f"look_{cid}", "form_name": name, "look_of": base, "facings": f"assets/forms/{cid}"}, _icon)

# ---------------------------------------------------------------- Exalted titles
# Kyle, 18 Nov 2026: "each faction should get a title for reaching exalted with them." Learned the moment a faction
# reaches Exalted (world/faction_manager.award -> world/collection.grant), never sold: FOUND ONLY. The faction's own
# name is in the blurb; "{name}" is where the character's name goes.
EXALTED_TITLES = {
    "orgrimmar": "{name} of Orgrimmar",
    "darkspear_tribe": "{name} of the Darkspear",
    "the_forsaken": "{name}, Champion of the Forsaken",
    "thunder_bluff": "{name}, Keeper of Thunder Bluff",
    "steamwheedle_cartel": "{name}, Partner of the Cartel",
    "booty_bay_authority": "{name}, Freeman of Booty Bay",
    "crimson_codex": "{name}, Keeper of the Crimson Codex",
    "the_ashclaim": "{name} of the Ashclaim",
    "emerald_reclamation": "{name} the Reclaimer",
    "pale_flame": "{name} of the Pale Flame",
    "argent_dawn": "{name} the Argent Champion",
    "timbermaw_hold": "{name}, Elder-Friend of Timbermaw Hold",
    "sunreach_conclave": "{name} of the Sunreach",
    "the_liquidators": "{name} the Liquidator",
    "cenarion_circle": "{name}, Guardian of Cenarius",
    "the_wakened": "{name} the Wakeful",
    "the_unnamed": "{name} the Unwritten",
    "feathermoon_sentinels": "{name}, Sentinel of Feathermoon",
}
_FACTIONS = json.loads((ROOT / "data/factions/factions.json").read_text(encoding="utf-8"))["factions"]
for _fid, _fmt in EXALTED_TITLES.items():
    _shown = _fmt.replace("{name}", "").lstrip(", ").strip()
    add(f"title_exalted_{_fid}", f"Title: {_shown}", "title", 750, "epic",
        f"Shown with your name: {_fmt.replace('{name}', 'You')}. Earned at Exalted with {_FACTIONS[_fid]['name']}.",
        {"title": _fmt}, "col_title_rare")
    ITEMS[-1].update(found_only=True, source=f"exalted:{_fid}")

# ---------------------------------------------------------------- wild mounts (sheets H9 and H10, 19 Nov 2026)
# Kyle, 18 Nov 2026: "Hit me with as much as you can!" Twelve mounts for the wild: each drops, rarely, from one
# open-world rare that fits it (world/collection.rare_drop, RARE_MOUNT_CHANCE a kill). FOUND ONLY: no trader lists
# them. Their reins wear a stand-in icon until sheet I2 (docs/exalted_mount_art_prompts.md).
RARE_MOUNT_CHANCE = 0.05
WILD_MOUNTS = (
    ("stormhide_thunder_lizard", "Stormhide Thunder Lizard", "Stormhide Patriarch",
     "A blue-grey thunder lizard with lightning crackling down the plates of its back."),
    ("plainstrider_matriarch", "Plainstrider Matriarch", "Old Mother Longhorn",
     "A huge plainstrider hen with a red and white crest, and opinions about where you're going."),
    ("ironback_crocolisk", "Ironback Crocolisk", "Mistvale Longjaw",
     "A long, low crocolisk armoured in iron-grey scutes. Slower than it looks, and it looks slow."),
    ("moonfeather_hippogryph", "Moonfeather Hippogryph", "Antilus the Soarer",
     "A white and silver hippogryph with small antlers and a calm gold eye."),
    ("sandreaver_silithid", "Sandreaver Silithid", "Hive Champion Khix'ar",
     "A desert silithid broken to the saddle. Nobody is sure how, least of all the silithid."),
    ("ashmane_hyena", "Ashmane Hyena", "Marrowmaw",
     "A hyena the size of a horse, with an ash-black mane and a grin it never puts away."),
    ("highpeak_ramgoat", "Highpeak Ramgoat", "Old Icehide",
     "A shaggy mountain goat with spiralling horns and a bell that never stops ringing."),
    ("mudback_hydra", "Mudback Hydra", "Old Mire-Maw",
     "A squat swamp hydra with two heads that rarely agree on a direction."),
    ("thunderhorn_bull", "Thunderhorn Bull", "Brontus",
     "A massive plains bull with a hump of dark wool and a tauren saddle of painted hide."),
    ("carrion_strider", "Carrion Strider", "Old Bonepicker",
     "A walking vulture as tall as a horse. It smells exactly as you'd expect."),
    ("emberquill_porcupine", "Emberquill Porcupine", "Old Ashback the Basilisk",
     "A porcupine the size of a kodo whose quills glow at the tips like embers."),
    ("shellback_snail", "Shellback Snail", "Old Mossback",
     "A giant snail with a garden growing on its shell and a lantern hung from a pole."),
)
for cid, name, rare, blurb in WILD_MOUNTS:
    add(cid, f"Reins of the {name}", "mount", 600, "epic", blurb,
        {"mount_id": cid, "mount_name": name, "tier": 1, "drops_from": rare, "drop_chance": RARE_MOUNT_CHANCE},
        f"col_reins_{cid}" if (ROOT / f"assets/icons/collection/col_reins_{cid}.png").exists() else "qi_trophy_cord",
        needs_art=True)
    ITEMS[-1].update(found_only=True, source=f"rare:{rare}")

# ---------------------------------------------------------------- Exalted mounts (sheets H11 to H13, 19 Nov 2026)
# One per faction, sold by its quartermaster once you're Exalted (world/faction_manager.vendor_unlocks puts it on the
# shelf; world/rep_items keeps it off the auction house and out of the mail). FOUND ONLY: no trader lists them.
EXALTED_MOUNTS = (
    ("crimson_codex", "crimson_codex_spellbound_construct", "Spellbound Construct",
     "A steed of carved red sandstone and gold, crimson runes turning round it."),
    ("orgrimmar", "orgrimmar_redstone_warwolf", "Redstone War Wolf",
     "A black war wolf in red-painted iron, a Horde banner rising behind the saddle."),
    ("darkspear_tribe", "darkspear_voodoo_raptor", "Voodoo Raptor",
     "A teal and purple raptor in a carved voodoo mask, hung with fetishes."),
    ("the_forsaken", "forsaken_war_bat", "Forsaken War Bat",
     "A giant bat in dark iron with green plague-glass vials on its harness."),
    ("steamwheedle_cartel", "steamwheedle_trike", "Steamwheedle Trike",
     "A riveted brass three-wheeler with ram-horn handlebars. It smokes. It's meant to."),
    ("thunder_bluff", "thunder_bluff_totem_kodo", "Totem Kodo",
     "A grey kodo in mourning paint, carrying a carved totem pole for a city that isn't there."),
    ("booty_bay_authority", "booty_bay_great_parrot", "Great Harbour Parrot",
     "A parrot as big as a horse, in a little tricorn hat and a gold earring."),
    ("the_ashclaim", "ashclaim_core_hound", "Ashclaim Core Hound",
     "A two-headed lava hound in dark iron plate, smoke rising off its back."),
    ("emerald_reclamation", "emerald_bark_strider", "Bark Strider",
     "A four-legged beast grown from living wood, moss and ferns along its back."),
    ("pale_flame", "pale_flame_lion", "Pale Flame Lion",
     "A white lion whose mane is pale holy fire that burns without smoke."),
    ("argent_dawn", "argent_charger", "Argent Charger",
     "A white warhorse in silver plate and a blue and white caparison."),
    ("timbermaw_hold", "timbermaw_great_badger", "Great Badger",
     "A badger the size of a bear, hung with furbolg totems and wooden beads."),
    ("sunreach_conclave", "sunreach_dragonhawk", "Sunreach Dragonhawk",
     "A flame-red and gold dragonhawk in elven barding and a gold filigree saddle."),
    ("the_liquidators", "liquidators_hazard_mule", "Hazard Mule",
     "A big armoured mule in lead plate and hazard stripes, a gas mask hanging off the saddle."),
    ("cenarion_circle", "cenarion_stormcrow", "Cenarion Stormcrow",
     "A crow as tall as a horse, glossy blue-black, silver moons on its harness."),
    ("the_wakened", "wakened_dream_jackalope", "Dream Jackalope",
     "A sleepy giant rabbit with small antlers and glowing flowers in its fur."),
    # sheet H14 (20 Nov 2026): the factions that came after H11 to H13. The same sheet drew the Aetherians' Lumen Stag,
    # Kyr'vahl's Galestrider and Ul'Kharad's Stoneback Aurochs (assets/mounts); they join this list with their factions.
    ("feathermoon_sentinels", "feathermoon_war_owl", "Feathermoon War Owl",
     "A snowy owl as big as a horse, in violet and silver barding with crescent moons on its chest."),
    ("highbough_tribes", "highbough_cloudtop_wyvern", "Cloudtop Wyvern",
     "A wild wyvern off the Upper Boughs, tamed the way Gu'lok tames them, in teal and red with a heartwood saddle."),
    ("aetherians", "aetherian_lumen_stag", "Lumen Stag",
     "A tall white stag with crystal antlers that hold the light, in the scholar houses' white and gold."),
)
for fid, cid, name, blurb in EXALTED_MOUNTS:
    add(cid, f"Reins of the {name}", "mount", 100, "epic", f"{blurb} Sold at Exalted with {_FACTIONS[fid]['name']}.",
        {"mount_id": cid, "mount_name": name, "tier": 1, "exalted_mount_of": fid},
        f"col_reins_{cid}" if (ROOT / f"assets/icons/collection/col_reins_{cid}.png").exists() else "qi_trophy_cord",
        needs_art=True)
    ITEMS[-1].update(found_only=True, source=f"exalted:{fid}")

# ---------------------------------------------------------------- keepsakes
# Kyle, 19 Nov 2026: "a new collection tab. Each sworn member will give something that goes there. it's personal to
# them and i have plans for it later." One per recruit, from data/npcs/keepsakes.json (written from each Wave 1
# profile in docs/recruits/). Given the moment they become Sworn (world/bond_manager), never sold: FOUND ONLY.
_KEEP = json.loads((ROOT / "data/npcs/keepsakes.json").read_text(encoding="utf-8"))["keepsakes"]
_RECRUITS = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))
_RECRUITS = {r["recruit_id"]: r for r in (_RECRUITS if isinstance(_RECRUITS, list) else _RECRUITS.get("recruits", []))}
for _rid, _k in _KEEP.items():
    add(f"keepsake_{_rid}", _k["name"], "keepsake", 0, "epic", _k["blurb"],
        {"recruit_id": _rid, "from": _RECRUITS[_rid]["name"]},
        _k["icon"] if (ROOT / "assets/icons/collection" / f"{_k['icon']}.png").exists() else _k["stand_in"])
    ITEMS[-1].update(found_only=True, source=f"sworn:{_rid}", art=_k["icon"])
# Kyle, 20 Nov 2026: "can we have a little trigger or item that can be used to view the cutscene again if we want to"
# (docs/crown_cutscene.md). The account learns it the first time any character sees the Crown's cutscene
# (world/cutscenes.KEEPSAKES); using it plays the cutscene again, wherever you are, and moves you nowhere.
add("keepsake_mural_shard", "Mural Shard", "keepsake", 0, "epic",
    "A flake of old painted stone from the mural at the top of the World Tree, with a little of the golden sun still "
    "on it. Hold it up to the light and you're back in that chamber, watching the wall come down.",
    {"from": "the mural at the top of the World Tree", "cutscene": "crown"},
    "col_keepsake_mural_shard" if (ROOT / "assets/icons/collection/col_keepsake_mural_shard.png").exists()
    else "qi_tablet", needs_art=True)
ITEMS[-1].update(found_only=True, source="cutscene:crown")

# ---------------------------------------------------------------- the icons (Sheet D, delivered 18 Nov 2026)
UNIQUE_REINS = {"bone_white_kodo": "kodo", "steamwheedle_runabout": "runabout", "tidecaller_sea_turtle": "turtle",
                "dread_elk_of_felwood": "elk", "sunreach_hawkstrider": "hawkstrider", "ashen_nightmare": "nightmare",
                # the fishing mounts' reins, on the harvest finds sheet H1 (docs/harvest_fishing_art_prompts.md)
                "brine_crab": "brine_crab", "river_otter": "river_otter", "glimmer_frog": "glimmer_frog",
                "rimefin_walrus": "rimefin_walrus", "cinder_salamander": "cinder_salamander",
                "abyssal_lurker": "abyssal_lurker",
                # the wild and Exalted mounts (sheets H9 to H13, 19 Nov 2026): the nearest drawn reins until sheet I2
                # gives each its own (it then wins, above)
                "stormhide_thunder_lizard": "cinder_salamander", "plainstrider_matriarch": "hawkstrider",
                "ironback_crocolisk": "abyssal_lurker", "moonfeather_hippogryph": "dawn",
                "sandreaver_silithid": "ruby_scorpid", "ashmane_hyena": "coinscale_raptor",
                "highpeak_ramgoat": "jadehorn_elk", "mudback_hydra": "glimmer_frog", "thunderhorn_bull": "kodo",
                "carrion_strider": "twilight", "emberquill_porcupine": "goldtusk_boar", "shellback_snail": "spring",
                "crimson_codex_spellbound_construct": "rose", "orgrimmar_redstone_warwolf": "platinum_direwolf",
                "darkspear_voodoo_raptor": "coinscale_raptor", "forsaken_war_bat": "nightmare",
                "steamwheedle_trike": "runabout", "thunder_bluff_totem_kodo": "kodo",
                "booty_bay_great_parrot": "tide", "ashclaim_core_hound": "cinder_salamander",
                "emerald_bark_strider": "jade", "pale_flame_lion": "dawn", "argent_charger": "gilded_bone_steed",
                "timbermaw_great_badger": "crowned_grizzly", "sunreach_dragonhawk": "hawkstrider",
                "liquidators_hazard_mule": "golden_dromedary", "cenarion_stormcrow": "twilight",
                "wakened_dream_jackalope": "spring",
                }
SERVICE_ICON = {"bank": "col_satchel_bank", "peddler": "col_peddler_bell", "mail": "col_courier_horn",
                "class_trainer": "col_book_master", "profession_trainer": "col_book_professions",
                "reagents": "col_satchel_reagents"}
CHARM_WORDS = (("murloc", ("murloc",)),
               ("dragonkin", ("dragon", "drake", "whelp", "wyrm", "dragonkin", "drakonid", "dragonspawn")),
               ("insect", ("spider", "scorpid", "silithid", "beetle", "scarab", "crawler", "tick", "roach",
                           "nerubian", "widow", "tarantula", "recluse", "creeper", "skitterer", "mantis", "locust")),
               ("serpent", ("serpent", "snake", "naga", "basilisk", "lizard", "crocolisk", "hydra", "wyrm", "drake",
                            "dragon", "whelp", "scorpid", "slither", "viper", "cobra", "worm")),
               ("bird", ("crow", "vulture", "owl", "harpy", "bat", "bird", "hawk", "raven", "wyvern", "buzzard",
                         "gryphon", "roc", "condor", "moth", "wasp", "stinger")),
               ("spirit", ("spirit", "ghost", "shade", "wraith", "spectre", "specter", "phantom", "banshee", "wisp",
                           "apparition", "echo")),
               ("drowned", ("drowned", "sea", "tide", "coral", "reef", "deep", "siren", "brine", "wave", "kraken")),
               # the nine family charms from sheet H8, which split up the forms that all wore the wolf charm
               ("undead", ("skeleton", "zombie", "ghoul", "abomination", "lich", "bone", "plague", "scourge", "undead",
                           "mummy", "corpse", "rotting", "risen", "cadaver", "necro", "skull", "crypt", "geist")),
               ("demon", ("demon", "imp", "felguard", "fel ", "satyr", "succubus", "infernal", "voidwalker",
                          "doomguard", "felhound", "dreadlord", "hellcaller", "eredar")),
               ("elemental", ("elemental", "golem", "earth", "fire", "flame", "storm", "rock", "stone", "ember",
                              "ooze", "slime", "sludge", "magma", "lava", "cinder", "dust", "sand", "crystal",
                              "construct", "living")),
               ("plant", ("treant", "lasher", "bog", "plant", "flower", "vine", "mushroom", "fungal", "ancient",
                          "sapling", "thorn", "bloom", "moss", "root", "briar")),
               ("giant", ("ogre", "giant", "gronn", "ettin", "yeti", "behemoth", "colossus", "mountain", "brute")),
               ("humanoid", ("bandit", "cultist", "defias", "kobold", "gnoll", "quillboar", "centaur", "pirate",
                             "mage", "warrior", "scout", "guard", "priest", "smuggler", "thug", "dwarf", "human",
                             "elf", "orc", "troll", "tauren", "goblin", "gnome", "footpad", "raider", "poacher",
                             "hunter", "trapper", "sentry", "knight", "soldier", "crusader", "zealot", "witch",
                             "shaman", "mystic", "furbolg", "murk", "acolyte", "outrider", "rogue", "thief",
                             "worker", "miner", "merchant", "captain", "sailor", "deckhand", "marauder", "harvester",
                             "geomancer", "seer", "oracle", "apprentice", "scholar", "magus", "sorcer", "warlock")),
               ("beast", ("bear", "boar", "cat", "lion", "tiger", "panther", "saber", "raptor", "kodo", "hyena",
                          "gorilla", "ape", "crab", "turtle", "tortoise", "stag", "elk", "deer", "ram", "goat",
                          "rhino", "thunder", "plainstrider", "strider", "lynx", "cougar", "leopard", "rat", "bear",
                          "badger", "porcupine", "crocolisk", "hippo", "mammoth", "bison", "tallstrider", "stalker",
                          "prowler", "mauler", "frog", "toad", "spirit beast")))


def icon_for(i):
    k, eff, cid = i["kind"], i["effect"], i["id"]
    if k == "mount":
        if (ROOT / "assets/icons/collection" / f"col_reins_{cid}.png").exists():
            return f"col_reins_{cid}"     # its own reins (sheets H1, H8, I2)
        if cid in UNIQUE_REINS:
            return f"col_reins_{UNIQUE_REINS[cid]}"
        colour = cid.split("_")[0]
        return f"col_reins_{'twilight' if colour == 'dusk' else colour}"
    if k == "form":
        if i["icon_id"].startswith("col_") and (ROOT / "assets/icons/collection" / f"{i['icon_id']}.png").exists():
            return i["icon_id"]          # given its own charm (sheet H8) or a look's stand-in
        name = eff["form_name"].lower()
        if cid == "spirit_wolf":
            return "col_charm_spirit"
        if cid == "shade_of_the_drowned_court":
            return "col_charm_drowned"
        for charm, words in CHARM_WORDS:
            if any(w in name for w in words):
                return f"col_charm_{charm}"
        return "col_charm_wolf"
    if k == "title":
        return "col_title_rare" if i["rarity"] in ("rare", "epic") else "col_title_common"
    if eff.get("feather"):
        return "col_feather_kalimdor" if eff["feather"] == "kalimdor" else "col_feather_eastern"
    if eff.get("second_hearth"):
        return "col_hearthstone_2"
    if k == "service":
        return SERVICE_ICON[eff["service"]]
    if k in ("travel", "tome"):
        return "col_tome_hearth"
    return i["icon_id"]


for _i in ITEMS:
    _i["icon_id"] = icon_for(_i)


def problems():
    out = []
    ids = [i["id"] for i in ITEMS]
    if len(ids) != len(set(ids)):
        out.append("duplicate ids")
    names = [i["name"] for i in ITEMS]
    if len(names) != len(set(names)):
        out.append("duplicate names")
    for i in ITEMS:
        if i["kind"] != "keepsake" and not 2 * G <= i["price"] <= 750 * G:     # a keepsake is given, never priced
            out.append(f"{i['id']}: price {i['price'] // G}g is outside 2-750g (Kyle: \"Some are dirt cheap. Some "
                       f"are expensive\", up to 750g)")
        if i["kind"] == "form" and i["effect"].get("facings"):
            for d in ("down", "left", "right", "up"):
                if not (ROOT / f"{i['effect']['facings']}_{d}.png").exists():
                    out.append(f"{i['id']}: no picture {i['effect']['facings']}_{d}.png")
        elif i["kind"] == "form" and not (ROOT / i["effect"]["sprite"]).exists():
            out.append(f"{i['id']}: no picture {i['effect']['sprite']}")
        if i["rarity"] not in RARITY_WEIGHT:
            out.append(f"{i['id']}: rarity {i['rarity']}")
        if not any((ROOT / "assets/icons" / d / f"{i['icon_id']}.png").exists() for d in ("quest_items", "collection")):
            out.append(f"{i['id']}: no icon {i['icon_id']}")
    # a full kit is +80%: four armour pieces, a cloak and a trinket (60) and a two-hander (20)
    if 4 * 10 + 10 + 10 + 20 != 80 or not any(i["effect"].get("xp_pct") == 20 for i in ITEMS):
        out.append("a full heirloom kit isn't Kyle's +80%")
    from world.collection import armour_family, weapon_family
    have = {i["id"] for i in ITEMS}
    for k, v in _spec_gear().items():
        want = [f"heirloom_{v['armor_type']}_{armour_family(v)}_chest", f"heirloom_{weapon_family(v)}_back"]
        want += [f"heirloom_{wt}_{weapon_family(v)}" for wt in (v.get("weapons") or {}).values() if wt]
        out += [f"{k} has no {w}" for w in want if w not in have]
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
