"""
Theme-based quest-reward generator for the Tirisfal quest pass (2026-10-22).

    from tools.tirisfal_gear import reward_pack
    reward_pack(qid, theme, ilvl, req, rarity, n=3)  ->  list of item defs (via build_deathknell_quests.pack)

Each theme has a prefix list ("Shore-Reed", "Scarlet Picket's"...) and flavor lines; each (slot, armor/weapon kind) has
a noun list and a suffix list (primary-only below item level 10, richer suffixes from 10).  Choices are seeded by the
quest id so re-running is byte-stable, and item names are unique across the whole pass.
"""
import random

THEMES = {
    "vale": (["Nightmare", "Gloamwood", "Dusk-Vale", "Moth-Eaten", "Hollow-Hunter's", "Thorn-Torn"],
             ["Cut for someone who lived in the dark, and liked it.", "Smells of loam and wolf. Both are mostly gone.",
              "The Vale never lets you wash it out.", "Worn thin by thorn and branch.",
              "Somebody left it where the road bends. You can see why."]),
    "manor": (["Cold Hearth", "Manor-Reaper's", "Ash-Hearth", "Mourning-Hall", "Chimney-Black", "Draught-Chilled"],
              ["The manor's chimney has been cold a long time. This remembers.", "Hung in the hall until the reapers rose.",
               "It was a servant's once. Someone rose from it in a hurry.", "Pale soot stains every seam."]),
    "shore": (["Shore-Reed", "Kelp-Woven", "Driftwood", "Brine-Stained", "Tide-Worn", "Salt-Crusted"],
              ["Smells of the bay and of what the bay keeps.", "Dried by wind, never by sun.",
               "The Vile Fins left it on the strand. Maybe a sacrifice.", "Wet to the touch even when it is dry.",
               "Wind off the water gets in the seams."]),
    "outpost": (["Crusader's", "Scarlet Picket's", "Recruit's", "Sentry-Post", "Banner-Red", "Oath-Stamped"],
                ["Crimson dye, fading in the rain.", "Standard issue, and mostly standard.",
                 "Whoever wore it believed every word of the sermon.", "The Crusade does not skimp on paint. Or on zeal."]),
    "farm": (["Solliden", "Harvest-Blighted", "Pumpkin-Vine", "Scarecrow's", "Furrow-Worn", "Tithe-Barn"],
             ["Straw in the seams and soil in the grain.", "The harvest rots where it stands. So does this.",
              "A farmer wore this to work in rain that never ends.", "Rough, practical, and faintly sour."]),
    "pond": (["Stillwater", "Silt-Caked", "Reed-Bound", "Bog-Slick", "Pond-Dredged", "Hermit's"],
             ["Fished from the muck. It dries out in a week, if you ignore the smell.", "Heavy with pond water.",
              "The pond keeps what falls in. This slipped through.", "Mud in every stitch."]),
    "mills": (["Agamand", "Millstone", "Mill-Race", "Servant's", "Grain-Dust", "Estate"],
              ["From the Agamand house, once fine. Now fine only in the sense of dust.", "Flour-pale and damp.",
               "The estate's servants wore them in life. They wear nothing in death.", "A good cut, wasted on a bad owner."]),
    "crypt": (["Crypt-Warden's", "Ancestral", "Tomb-Guard", "Wight-Bone", "Mausoleum", "Sepulchre"],
              ["Damp stone and older dust.", "The Agamand family kept their dead dressed. This is what they wore.",
               "Cold to the touch, in every season.", "Tomb-robbers left it. That says something."]),
    "haunt": (["Rot Hide", "Gnoll-Chewed", "Garren's", "Graverobber's", "Mongrel-Scrap", "Haunt-Stitched"],
              ["Stitched together by something with very little patience.", "Dog-chewed and worse.",
               "Whoever robbed the graves here took this off one.", "It stinks. It also works."]),
    "lake": (["Brightwater", "Lakeshore", "Frost-Rimed", "Cold-Water", "Shade-Haunted", "Iceshard"],
             ["The lake keeps things cold. This is still cold.", "Frost along the hem, even in summer.",
              "It was a fisher's before the lake started crying.", "Water beads and runs off, or doesn't."]),
    "faol": (["Faol's Rest", "Pilgrim's", "Gravekeeper's", "Weathered-Stone", "Tomb-Field", "Restless"],
             ["Taken from a grave that wasn't Faol's, but might have been.", "Graveyard moss in the weave.",
              "The old order buried their dead in this. Possibly with it.", "A small, solemn thing."]),
    "venom": (["Venomweb", "Web-Spun", "Vale-Walker's", "Chitin-Plated", "Skitterer's", "Silk-Lashed"],
              ["Sticky for the first hour. After that you stop noticing.", "Spun by something patient and fed on the unwary.",
               "Chitin, silk and nerve. Nothing wasted.", "Faint venom smell; likely harmless."]),
    "balnir": (["Balnir", "Stable-Hand's", "Hay-Dusted", "Farmstead", "Saddle-Worn", "Worg-Scarred"],
               ["Smells of hay and horse. The horses are gone.", "A stableboy's, with a stableboy's patches.",
                "The worgs have left bite-marks. Nobody objects.", "Worn by someone who still hoped."]),
    "cult": (["Damned", "Cultist's", "Ledger-Stained", "Dark-Vestment", "Fanatic's", "Sigil-Marked"],
             ["Stitched with a sigil you shouldn't look at for long.", "Warm in the wrong places.",
              "Found in a farm cellar. It was not alone.", "Whoever made it wanted to be remembered. Wrongly."]),
    "watch": (["Scarlet Watch", "Inquisitor's", "Zealot's", "Sunburst", "Preacher's", "Crimson Sentinel's"],
              ["Pressed, polished and utterly certain.", "Sunburst on the breast. There is no sun here.",
               "Whoever wore it expected to be praised for it.", "Heavy with doctrine."]),
    "ruins": (["Lordaeron", "Fallen-Throne", "Royal Guard's", "Weathered-Banner", "Old-Kingdom", "Ruin-Dust"],
              ["From a kingdom that doesn't remember itself.", "Gold braid, faded to grey.",
               "The lions on the crest have lost their teeth.", "Once somebody's best."]),
    "landing": (["Zeppelin-Crew's", "Landing-Dock", "Rope-Burned", "Cargo-Hauler's", "Brass-Fitted", "Goblin-Stitched"],
                ["Goblin work: sturdy, overpriced and slightly wrong.", "Smells of oil, rope and Undercity.",
                 "Whoever carried freight in this carried it well.", "Brass fittings still gleam."]),
    "brill": (["Brill", "Gallows' End", "Town-Crier's", "Ashen", "Belltower", "Square-Worn"],
              ["A village thing: cheap, mended and cared for.", "Brill makes do. This is proof.",
               "Survivors' stitching. Honest, even when it isn't pretty.", "It has been mended at least twice."]),
}

_CLOTH_LOW = ["of the Owl", "of the Eagle", "of the Whale", "of Spirit", "of Intellect", "of Stamina"]
_CLOTH_HI = ["of the Seer", "of the Restorer", "of the Archmage", "of the Invoker", "of the Sorcerer", "of the Prophet",
             "of the Physician", "of the Mind's Eye"]
_LEATHER_LOW = ["of the Monkey", "of the Wolf", "of the Falcon", "of Agility", "of Stamina"]
_LEATHER_HI = ["of the Assassin", "of the Bandit", "of the Hunt", "of the Duelist", "of the Beast"]
_MAIL_LOW = ["of the Bear", "of the Tiger", "of the Eagle", "of Stamina", "of the Boar"]
_MAIL_HI = ["of the Soldier", "of the Defender", "of the Hierophant", "of the Warder", "of the Tactician"]
_PLATE_LOW = ["of the Bear", "of Strength", "of Stamina", "of the Gorilla", "of the Boar"]
_PLATE_HI = ["of the Champion", "of the Soldier", "of the Bastion", "of the Bulwark", "of the Defender"]
_MELEE_LOW = ["of Strength", "of the Tiger", "of the Bear", "of the Gorilla"]
_MELEE_HI = ["of the Soldier", "of the Champion", "of the Duelist", "of the Juggernaut"]

# kind -> (nouns by slot, suffixes low, suffixes high)
ARMOR = {
    "cloth": ({"head": ["Cowl", "Hood", "Veil", "Circlet"], "chest": ["Robe", "Vestments", "Tunic"],
               "shoulder": ["Mantle", "Shawl", "Wraps"], "hands": ["Gloves", "Wraps", "Mitts"],
               "legs": ["Leggings", "Breeches", "Skirt"], "feet": ["Sandals", "Slippers", "Wraps"],
               "wrist": ["Bracers", "Cuffs", "Bindings"], "waist": ["Sash", "Cord", "Belt"],
               "back": ["Cloak", "Shroud", "Mantle"]}, _CLOTH_LOW, _CLOTH_HI),
    "leather": ({"head": ["Cap", "Hood", "Coif"], "chest": ["Jerkin", "Vest", "Coat"],
                 "shoulder": ["Pauldrons", "Spaulders", "Epaulets"], "hands": ["Gloves", "Grips", "Gauntlets"],
                 "legs": ["Leggings", "Pants", "Chaps"], "feet": ["Boots", "Treads", "Shoes"],
                 "wrist": ["Bracers", "Wristguards", "Cuffs"], "waist": ["Belt", "Girdle", "Cord"],
                 "back": ["Cloak", "Mantle", "Cape"]}, _LEATHER_LOW, _LEATHER_HI),
    "mail": ({"head": ["Coif", "Helm", "Cap"], "chest": ["Hauberk", "Chainmail", "Byrnie"],
              "shoulder": ["Spaulders", "Pauldrons", "Shoulderguards"], "hands": ["Gauntlets", "Gloves", "Handguards"],
              "legs": ["Legguards", "Chausses", "Leggings"], "feet": ["Greaves", "Boots", "Sabatons"],
              "wrist": ["Bracers", "Armguards", "Cuffs"], "waist": ["Girdle", "Belt", "Chain Belt"]},
             _MAIL_LOW, _MAIL_HI),
    "plate": ({"head": ["Helm", "Greathelm", "Visor"], "chest": ["Breastplate", "Cuirass", "Chestguard"],
               "shoulder": ["Pauldrons", "Shoulderplates", "Spaulders"], "hands": ["Gauntlets", "Fists", "Handguards"],
               "legs": ["Legplates", "Greaves", "Cuisses"], "feet": ["Sabatons", "Boots", "Treads"],
               "wrist": ["Vambraces", "Bracers", "Armguards"], "waist": ["Girdle", "Waistguard", "Belt"]},
              _PLATE_LOW, _PLATE_HI),
}
WEAPONS = {
    "mace_1h": (["Mace", "Cudgel", "Hammer", "Flail"], _MELEE_LOW, _MELEE_HI),
    "sword_1h": (["Blade", "Sword", "Saber", "Longsword"], _MELEE_LOW, _MELEE_HI),
    "axe_1h": (["Hatchet", "Axe", "Cleaver"], _MELEE_LOW, _MELEE_HI),
    "dagger": (["Dirk", "Dagger", "Knife", "Stiletto"], ["of Agility", "of the Monkey", "of the Falcon"],
               ["of the Assassin", "of the Bandit", "of the Duelist"]),
    "staff": (["Staff", "Walking Stick", "Rod", "Crook"], ["of the Eagle", "of the Owl", "of Spirit", "of Intellect"],
              ["of the Invoker", "of the Archmage", "of the Restorer", "of the Prophet"]),
    "wand": (["Wand", "Rod", "Scepter"], ["of Intellect", "of Spirit", "of the Owl"],
             ["of the Invoker", "of the Sorcerer", "of the Seer"]),
    "polearm": (["Spear", "Halberd", "Pike", "Glaive"], _MELEE_LOW, _MELEE_HI),
    "bow": (["Shortbow", "Hunting Bow", "Longbow"], ["of the Falcon", "of Agility", "of the Monkey"],
            ["of the Marksman", "of the Hunt", "of the Beast"]),
    "shield": (["Shield", "Buckler", "Roundshield", "Targe"], ["of Stamina", "of the Bear", "of the Boar"],
               ["of the Bulwark", "of the Bastion", "of the Defender"]),
}
JEWEL = {"neck": (["Pendant", "Charm", "Necklace", "Talisman"], ["of the Eagle", "of the Falcon", "of the Bear",
                                                                  "of the Tiger", "of the Whale"],
                  ["of the Seer", "of the Soldier", "of the Prophet", "of the Tactician", "of the Hierophant"]),
         "ring": (["Ring", "Band", "Signet", "Loop"], ["of the Eagle", "of the Falcon", "of the Bear",
                                                         "of the Tiger", "of the Whale"],
                  ["of the Seer", "of the Soldier", "of the Prophet", "of the Tactician", "of the Hierophant"])}

# slot pools per armor kind (what a quest pack can offer)
SLOTS = {"cloth": ["head", "chest", "shoulder", "hands", "legs", "feet", "wrist", "waist", "back"],
         "leather": ["head", "chest", "shoulder", "hands", "legs", "feet", "wrist", "waist", "back"],
         "mail": ["head", "chest", "shoulder", "hands", "legs", "feet", "wrist", "waist"],
         "plate": ["head", "chest", "shoulder", "hands", "legs", "feet", "wrist", "waist"]}
WEAPON_SLOT = {"shield": "off_hand"}

_USED = set()


def _rank(r, lst):
    return r.choice(lst)


def specs(qid, theme, ilvl, n=3):
    """n (name, slot, suffix, flavor, kind) tuples for one quest; deterministic per quest id."""
    r = random.Random(qid)
    prefixes, flavors = THEMES[theme]
    high = ilvl >= 10
    # one slot-type per pack member: always cover several armor kinds, add a weapon/jewel
    plan = ["armor", "armor", "weapon_or_jewel", "armor"][:n]
    kinds = r.sample(["cloth", "leather", "mail", "plate"], 4)
    out = []
    ki = 0
    for kind_slot in plan:
        for _ in range(60):
            if kind_slot == "armor":
                k = kinds[ki % 4]
                slot = r.choice(SLOTS[k])
                nouns, low, hi = ARMOR[k]
                noun = r.choice(nouns[slot])
                kind = k
            else:
                if r.random() < 0.6:
                    kind = r.choice(list(WEAPONS))
                    nouns, low, hi = WEAPONS[kind]
                    slot = WEAPON_SLOT.get(kind, "main_hand")
                    noun = r.choice(nouns)
                else:
                    slot = r.choice(["neck", "ring"])
                    nouns, low, hi = JEWEL[slot]
                    noun = r.choice(nouns)
                    kind = None
            name = f"{r.choice(prefixes)} {noun}"
            if name not in _USED:
                _USED.add(name)
                break
        else:
            raise RuntimeError(f"no free name for {qid}")
        if kind_slot == "armor":
            ki += 1
        suffix = r.choice(hi if high else low)
        out.append((name, slot, suffix, r.choice(flavors), kind))
    return out


def reward_pack(qid, theme, ilvl, req, rarity, n=3):
    from tools.build_deathknell_quests import pack
    return pack(ilvl, req, rarity, specs(qid, theme, ilvl, n))
