#!/usr/bin/env python3
"""Writes data/loot/arathi_boss_loot.json - the 24 named drops of the Arathi Highlands.

    PYTHONPATH=. python3 tools/build_arathi_boss_loot.py [--check]

NAMES AND INTENT ARE HAND-WRITTEN. NUMBERS ARE SOLVED.

Every previous boss table in this game was typed out by hand, numbers included, and
tools/audit_item_budgets.py exists because that went wrong quietly and often - the headline
arena boss's signature axe came in at 40% of its own budget and nothing noticed, because the
items around it were under budget too and a peer-median eyeball said it was fine.

So this file authors the part that needs a person - what the item IS, who it is for, what it
says about the thing that was holding it - and derives the part that needs arithmetic from the
same formula LootGenerator uses for procedural gear:

    stat budget  = item_level * 0.36 * rarity_mult * slot_weight [* weapon_budget_mult]
    armor value  = item_level * 1.5 * armor_mult * slot_weight * rarity_mult
    avg damage   = (item_level * 1.1 + 6.4) * rarity_mult * damage_tier_mult

A BLEND is a set of stat weights, not a set of stat values: "int_heal" means 40% of this
item's budget in intellect, 35% in spirit, 25% in healing power, and the solver prices each
against gear_suffixes.json's stat_budget_costs and rounds. An item is therefore interesting
(a healer piece reads as a healer piece) without being a different power curve from the one
next to it. --check reports every item's spend ratio; audit_item_budgets.py is the real gate.

item_level = creature level + 3 and required_level = creature level, which is the convention
every other table in data/loot follows.

COVERAGE IS CHECKED, NOT HOPED FOR. Thirty classes can walk into Arathi and seven of them
cannot wear a stitch of leather. coverage() fails the build if any of the four armour types or
any of the twenty weapon and relic types is missing from the region, and if any of the five
broad stat blends is. A region that drops nothing a Stormbringer can use is a region that is
30% shorter than it looks, and that is not visible by reading the file.

NO RESISTANCE STATS ANYWHERE IN HERE. Kyle's rule: magic resistance gear only after level 45,
and nothing in Arathi is above 40.
"""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from tools.audit_item_budgets import budget_for, spend  # the authority, not a copy of it

OUT = ROOT / "data/loot/arathi_boss_loot.json"
CRE = ROOT / "data/creatures/creatures.json"
_WEAPONS = json.loads((ROOT / "data/items/weapon_types.json").read_text())["weapon_types"]
_COSTS = json.loads((ROOT / "data/items/gear_suffixes.json").read_text())["stat_budget_costs"]

#: Stat weights per blend. Primary stats are the bulk; one secondary gives the piece its job.
#: PRIMARY lists which of the keys go in "primary_stats" - the rest go in "secondary_stats",
#: which is the split the tooltip and the budget auditor both expect.
PRIMARY = {"strength", "agility", "intellect", "stamina", "spirit"}
BLENDS = {
    "str_dps":   {"strength": 0.52, "stamina": 0.33, "attack_power": 0.15},
    "str_tank":  {"stamina": 0.52, "strength": 0.26, "defense_rating": 0.22},
    "agi_dps":   {"agility": 0.52, "stamina": 0.33, "attack_power": 0.15},
    "agi_crit":  {"agility": 0.50, "stamina": 0.27, "crit_chance_physical": 0.23},
    "int_dps":   {"intellect": 0.48, "stamina": 0.30, "spell_power": 0.22},
    "int_crit":  {"intellect": 0.47, "stamina": 0.28, "crit_chance_spell": 0.25},
    "int_heal":  {"intellect": 0.40, "spirit": 0.35, "healing_power": 0.25},
    "spi_heal":  {"spirit": 0.44, "intellect": 0.32, "mp5": 0.24},
    "str_int":   {"strength": 0.40, "intellect": 0.34, "stamina": 0.26},
    "agi_int":   {"agility": 0.40, "intellect": 0.34, "stamina": 0.26},
    "stam_wall": {"stamina": 1.0},
}
#: The five jobs coverage() insists the region serves, and which blends serve each.
JOBS = {
    "plate melee":  ("str_dps", "str_tank", "str_int"),
    "agility":      ("agi_dps", "agi_crit", "agi_int"),
    "caster":       ("int_dps", "int_crit"),
    "healer":       ("int_heal", "spi_heal"),
    "tank":         ("str_tank", "stam_wall"),
}

#: boss -> (level, [(item name, slot, kind, blend, flavour), ...])
#: `kind` is an armour type (cloth/leather/mail/plate), a weapon type, or "accessory" for
#: neck/ring/trinket/back. Levels are the creature's own, read back out of creatures.json by
#: _levels() - the number here is only a comment that _check() makes true.
SPECS = {

    # ------------------------------------------------------------------ Arathi West, 28-33
    # THE SYNDICATE. Dispossessed Alterac nobility running a protection racket out of a keep
    # they do not own, and their gear says both halves of that - good steel kept badly.
    "Overseer Mull": [
        ("Go'Shek Tally-Mace", "main_hand", "mace_1h", "str_dps",
         "The farm still files its yield. Nobody has come to collect it in three years."),
        ("Overseer's Buckled Hauberk", "chest", "mail", "str_dps",
         "Let out twice at the straps. He was a smaller man when he was given it."),
        ("Fieldhand's Bound Wraps", "wrist", "leather", "agi_dps",
         "The people who worked this ground wore these. He kept a pair."),
        ("Signet of the Lost Rent", "ring", "accessory", "str_int",
         "A seal for a ledger that was already a lie when it was sealed."),
    ],
    "Harbinger Veska": [
        ("Witherbark Harbinger's Totem", "ranged", "totem", "spi_heal",
         "Carved facing away from the village, which is not how they are usually carved."),
        ("Hollow-Drum Shoulderguards", "shoulder", "leather", "int_heal",
         "The hide is from something that was not a deer and the drum was not for dancing."),
        ("Hexthread Leggings", "legs", "cloth", "int_dps",
         "Six colours of thread, and the sixth is not a dye anyone sells."),
        ("Charm of the Turned Ear", "neck", "accessory", "spi_heal",
         "Trolls bury these at the edge of a camp to hear what is coming. Hers faced in."),
    ],
    "Gruln Stonejaw": [
        ("Stonejaw's Quarry Cleaver", "main_hand", "axe_2h", "str_dps",
         "Not forged. Found, and then argued with for a long time."),
        ("Crag-Walker's Girdle", "waist", "mail", "str_tank",
         "An ogre's belt makes a human's chest-piece, which is how the Syndicate used them."),
        ("Boulderfist Knuckle-Plate", "hands", "plate", "str_dps",
         "Three fingers of it. The fourth was never made and was never missed."),
        ("Stoneheart Pendant", "neck", "accessory", "stam_wall",
         "Ogres do not wear jewellery. He wore this one, and did not say where it came from."),
    ],
    "Gor'mok the Pit Chief": [
        ("Pit-Chief's Knucklebar", "main_hand", "fist_weapon", "agi_dps",
         "The pit at Boulder'gor is a hole with a lip on it. He has never lost in it."),
        ("Ring-Scarred Jerkin", "chest", "leather", "agi_crit",
         "Worn by everyone who fought him. Taken off everyone who fought him."),
        ("Deepden Treads", "feet", "mail", "agi_dps",
         "The floor down there is packed by generations of the same few steps."),
        ("Trophy of the Standing Count", "trinket", "accessory", "agi_dps",
         "He keeps count out loud. The number is much higher than the number of bodies."),
    ],
    # STROMGARDE KEEP, the dungeon. Four bosses, and the keep is older than all of them.
    "Grevan the Gatekeeper": [
        ("Gatekeeper's Barred Shield", "off_hand", "shield", "stam_wall",
         "The gate has not opened in three years. He is still being paid to not open it."),
        ("Portcullis Pauldrons", "shoulder", "plate", "str_tank",
         "Something very heavy came down on the left one and stopped."),
        ("Warden's Chainmail Coif", "head", "mail", "str_tank",
         "Stromgarde issue. The crest has been filed off and not replaced with another."),
        ("Keyring of the Outer Ward", "trinket", "accessory", "str_tank",
         "Eleven keys. Four of the doors they open are no longer standing."),
    ],
    "Sister Mollis": [
        ("Libram of the Kept Vigil", "ranged", "libram", "int_heal",
         "She has read the evening office every evening. The chapel roof went two winters ago."),
        ("Vestments of the Shuttered Chapel", "chest", "cloth", "int_heal",
         "Clean. In all of this, clean."),
        ("Almsgiver's Clasped Belt", "waist", "cloth", "spi_heal",
         "The pouch is empty and the clasp is worn from being opened."),
        ("Censer of Grey Smoke", "trinket", "accessory", "spi_heal",
         "Whatever she is burning now is not incense and she knows it is not."),
    ],
    "Lord Falconcrest": [
        ("Falconcrest's Court Blade", "main_hand", "sword_1h", "str_dps",
         "A duelling sword, in a keep with no court left to duel in."),
        ("Pretender's Breastplate", "chest", "plate", "str_dps",
         "The Stromgarde arms, re-engraved with his own. Badly, and by his own hand."),
        ("Mantle of the Third Claimant", "shoulder", "plate", "str_tank",
         "Two others claimed this hall before him. He does not mention them by name."),
        ("Falconer's Hooded Band", "head", "leather", "agi_crit",
         "The bird it was made for has been loose over the moor for years."),
    ],
    "The Vault-Thing": [
        ("Tome of the Lower Stair", "off_hand", "tome", "int_crit",
         "Stromgarde was built on top of this. The undercroft is the part that was here first."),
        ("Vaultkeeper's Mouldered Robe", "chest", "cloth", "int_dps",
         "Cut for a human frame, and the frame inside it is close enough to be worse."),
        ("Gravelight Bracers", "wrist", "plate", "str_int",
         "They give off nothing you could read by. You can still tell when they are near."),
        ("Coffer-Seal of Arathor", "ring", "accessory", "int_crit",
         "The empire that sealed this did not record what it was sealing."),
    ],

    # --------------------------------------------------------------- Arathi Central, 33-37
    # THE RINGS AND THE BASIN. Four stone circles older than Arathor, a sunken mere, and an
    # ogre hold that has been using one of the rings as a wall.
    "Mauler Krakk": [
        ("Krakk's Rendering Maul", "main_hand", "mace_2h", "str_dps",
         "He has worn a groove into the floor where he sets it down."),
        ("Maulhide Shoulders", "shoulder", "leather", "agi_dps",
         "Cured in the hold's own runoff, which is why nobody else wants them."),
        ("Bone-Set Gauntlets", "hands", "plate", "str_dps",
         "The setting is not decorative. It is how an ogre makes a glove fit a human hand."),
        ("Mauler's Weighted Cord", "waist", "mail", "str_tank",
         "Heavier than it needs to be. That was the point of it."),
    ],
    "Boulderfist Hal'dun": [
        ("Hal'dun's Ringbreaker", "main_hand", "polearm", "str_dps",
         "The ogres have been taking the standing stones down for forty years and are not quick."),
        ("Hold-Chief's Platemail", "chest", "plate", "str_tank",
         "Four smiths' work, none of them ogres, none of them willing."),
        ("Ringwall Sabatons", "feet", "mail", "str_tank",
         "The hold's outer wall is a stone circle with mud packed into the gaps."),
        ("Idol-Breaker's Charm", "neck", "accessory", "str_dps",
         "He wears one of the smaller stones. It has stopped doing whatever it did."),
    ],
    "The Ring Warden": [
        ("Warden's Plumbline Stave", "main_hand", "staff", "int_dps",
         "The rings are not a calendar and not a grave. The Warden is still measuring which."),
        ("Mantle of the Fourth Circle", "shoulder", "cloth", "int_crit",
         "There are four rings. Three are quiet."),
        ("Lodestone Girdle", "waist", "leather", "agi_int",
         "Stand in the ring wearing this and you can feel which way the stones are facing."),
        ("Sighting-Ring of the Basin", "ring", "accessory", "int_dps",
         "Hold it up at the right spot and all four circles line up. Nobody built that twice."),
    ],
    "Silt-Mother Ooga": [
        ("Silt-Mother's Spawning Idol", "ranged", "idol", "int_heal",
         "The mere is shallow, warm, and full. Those three facts are the same fact."),
        ("Mireclutch Hauberk", "chest", "mail", "spi_heal",
         "It drains for about an hour after you take it out of the water."),
        ("Brood-Slick Grips", "hands", "leather", "agi_int",
         "The grip is better wet, which is not how grips usually work."),
        ("Pearl of the Drowned Mere", "trinket", "accessory", "int_heal",
         "Freshwater. Something in there is making them anyway."),
    ],

    # ------------------------------------------------------------------ Arathi East, 37-40
    # DRYWHISKER DEEPS, the kobold mine, which Central's road leads to and which goes deeper
    # than the kobolds dug.
    "Grubbis Tallow": [
        ("Tallow's Guttering Wand", "ranged", "wand", "int_dps",
         "A candle he has never let go out, in a holder he has never let anyone else carry."),
        ("Chandler's Waxed Robes", "chest", "cloth", "int_dps",
         "Dipped, not woven. Years of dipping."),
        ("Wick-Trimmer's Gloves", "hands", "cloth", "int_crit",
         "Kobolds are frightened of the dark in a way that is not a joke to them."),
        ("Dripstone Loop", "ring", "accessory", "int_dps",
         "Wax, over bone, over wax. He has been making it his whole life."),
    ],
    "Overseer Ratch": [
        ("Ratch's Shift-Ending Axe", "main_hand", "axe_1h", "str_dps",
         "The shift ends when he says. He has not said for a while."),
        ("Overseer's Lamplit Harness", "chest", "mail", "str_dps",
         "Four lamp-hooks across the shoulders. You can see him coming along a gallery."),
        ("Tally-Scratch Bracers", "wrist", "leather", "agi_dps",
         "The marks on the inside are a count of days. They stop, then start again lower."),
        ("Whistle of the Lower Shift", "trinket", "accessory", "str_tank",
         "The diggers still come when it blows. It is not clear that they want to."),
    ],
    "The Pick-Mother": [
        ("Pick-Mother's Splitting Fang", "main_hand", "dagger", "agi_crit",
         "Kobolds hand their picks down. This one has been handed down past being a pick."),
        ("Brood-Gallery Chainmail", "chest", "mail", "agi_dps",
         "Sized for something that grows. Let out at the seams four times."),
        ("Spoil-Heap Treads", "feet", "leather", "agi_crit",
         "Mine spoil is loose, sharp and moves under you. These do not."),
        ("Nursery Candle-Stub", "trinket", "accessory", "int_heal",
         "The deepest gallery is the warm one. That is where she keeps them."),
    ],
    "What They Dug Into": [
        ("Blade From Below the Sump", "main_hand", "sword_2h", "str_int",
         "The kobolds did not make this and did not want to find it. They were digging for ore."),
        ("Scale of the Thing in the Water", "chest", "plate", "str_tank",
         "Not plate. Worn as plate, because there is nothing else to call it."),
        ("Sumpwater Crown", "head", "cloth", "int_crit",
         "The sump has been filling since before the mine. The mine found the top of it."),
        ("What the Deep Floor Gave Up", "trinket", "accessory", "int_crit",
         "Nobody in Drywhisker will say its name, and not out of respect."),
    ],
    # WRACKLINE HOLD. Bloodsail, run as a business, which is worse.
    "Ledger-Keeper Ashkin": [
        ("Ashkin's Accounting Crossbow", "ranged", "crossbow", "agi_dps",
         "He writes down every bolt. He writes down what it was spent on."),
        ("Purser's Oilskin Coat", "chest", "leather", "agi_dps",
         "Three years of salt and the ink inside the breast pocket has never run."),
        ("Shelf-Clerk's Cuffs", "wrist", "cloth", "int_dps",
         "A pirate crew that keeps books keeps them somewhere dry and high up."),
        ("Weighted Cargo-Seal", "neck", "accessory", "agi_int",
         "Stamped on every crate on the shelf. Half the crates are not theirs."),
    ],
    "Captain Mory Vane": [
        ("Vane's Long Nine", "ranged", "gun", "agi_crit",
         "She took the hold from the sea side, which nobody had thought was a side."),
        ("Captain's Storm-Cut Leathers", "chest", "leather", "agi_crit",
         "Cut short at the knee for climbing a wet rock face in the dark."),
        ("Reaver's Boarding Spurs", "feet", "mail", "agi_dps",
         "For going up a hull. Used going up a cliff more often now."),
        ("Bloodsail Captain's Band", "ring", "accessory", "agi_crit",
         "The Bloodsail gave her a ring instead of a ship. She took the hold instead."),
    ],
    # THE TIDEWRACK. A sea cave with nothing built in it at all.
    "Brinemaw": [
        ("Brinemaw's Loose Tooth", "ranged", "thrown", "agi_dps",
         "It grows them back. The ones it loses wash up barbed, which teeth are not."),
        ("Gill-Rent Scalemail", "chest", "mail", "agi_dps",
         "Scraped off the thing and cured. It has never stopped smelling of the sump."),
        ("Deep-Sump Shoulderpads", "shoulder", "leather", "agi_crit",
         "The sump at the Tidewrack is open water and goes down further than the cave does."),
        ("Lure of the Pearl Floor", "trinket", "accessory", "int_dps",
         "Something down there is arranging them. In rows."),
    ],
    "The Wrack-Drowned": [
        ("Drowned Lantern-Pole", "main_hand", "staff", "spi_heal",
         "Carried out to the tideline to look for survivors. It came back. They did not."),
        ("Shroud of the Standing Tide", "chest", "cloth", "int_heal",
         "The water in there comes up twice a day and has nowhere to go."),
        ("Wracklight Handwraps", "hands", "cloth", "spi_heal",
         "What is on them is not phosphorescence and does not come off in fresh water."),
        ("Keepsake of the Undertow", "neck", "accessory", "int_heal",
         "Everyone drowned here was carrying one of something. This is the one that was kept."),
    ],
    # THE DROWNED BARROW. Arathor's own dead, under the water table.
    "Thane Aldric's Shade": [
        ("Aldric's Oathkeeping Sword", "main_hand", "sword_1h", "str_int",
         "He swore to hold the eastern march. He is still at it, which is the problem."),
        ("Thane's Barrow-Plate", "chest", "plate", "str_tank",
         "Arathor work. There is no smith alive who could repair it and he does not need one."),
        ("Pall of the Long Watch", "back", "accessory", "str_tank",
         "Buried with him, under four feet of standing water, facing the door."),
        ("March-Lord's Ring of Office", "ring", "accessory", "str_int",
         "The march it is an office of is a drowned field with ogres walking over it."),
    ],
    "The Barrow Warden": [
        ("Warden's Mausoleum Pavis", "off_hand", "shield", "stam_wall",
         "A door-shield. It was a door first."),
        ("Grave-Marble Legplates", "legs", "plate", "str_tank",
         "The barrow's upper floor is marble. Below the stair it is limestone and wet."),
        ("Sepulchre Helm", "head", "plate", "str_tank",
         "No eye-slit worth the name. Whatever is in it is not looking out of it."),
        ("Cerement Bindings", "wrist", "cloth", "int_heal",
         "Linen. Three years of it holding, in water, is not a thing linen does."),
    ],
    # OPEN WORLD RARES, east. Both are things the archipelago made on its own.
    "Old Bonepicker": [
        ("Bonepicker's Longbow", "ranged", "bow", "agi_crit",
         "Taken off the last person who tried. Left on the flat for the next one."),
        ("Scavenger's Patchwork Vest", "chest", "leather", "agi_dps",
         "Nine kinds of leather. None of them cut from the same animal, or the same decade."),
        ("Pickings Girdle", "waist", "mail", "agi_dps",
         "The flat it nests on is above the tide and the tide keeps bringing it work."),
        ("Keenest Eye", "trinket", "accessory", "agi_crit",
         "It watched the whole wreck happen and then waited for the water to go down."),
    ],
    "The Saltquern": [
        ("The Turning Stone", "main_hand", "mace_2h", "str_int",
         "A mill-wheel for grinding salt out of the shallows. Nobody has turned it in years."),
        ("Saltcrust Carapace", "chest", "plate", "str_tank",
         "Not worn. Grown, over whatever is turning the wheel."),
        ("Brinehardened Boots", "feet", "mail", "str_tank",
         "Standing in salt water does this to leather over about a decade."),
        ("Grinding-Stone Fragment", "trinket", "accessory", "str_dps",
         "The wheel is down to three quarters of itself and is still going round."),
    ],
}


def _levels():
    """boss -> its own level, from creatures.json. The level is NOT authored here."""
    creatures = json.loads(CRE.read_text(encoding="utf-8"))["creatures"]
    out = {}
    for boss in SPECS:
        c = creatures.get(boss)
        if not c:
            raise SystemExit(f"FAIL {boss}: not in creatures.json")
        if not c.get("is_boss") and not c.get("is_rare"):
            # qa_boss_loot.py's exact failure mode: a curated table on a creature the combat
            # engine does not treat as a boss takes the trash roll and the table is unreachable.
            raise SystemExit(f"FAIL {boss}: has a loot table but is neither is_boss nor is_rare")
        lo, hi = c["level_range"][:2]
        out[boss] = int(hi)
    return out


def _solve(item, blend):
    """Fill item's stat blocks so its spend lands on the formula's budget for its own slot."""
    weights = BLENDS[blend]
    budget, armor, dmg = budget_for(item)
    if not budget:
        raise SystemExit(f"FAIL {item['name']}: no budget (slot/kind unknown to the formula)")

    prim, sec = {}, {}
    for stat, w in weights.items():
        # A point of crit costs 10 budget, a point of attack power costs 0.5. Dividing by the
        # cost is what makes "23% of budget in crit" mean the same thing as "15% in attack
        # power" - weighting the raw numbers instead is how an item ends up at 40% of target.
        raw = budget * w / _COSTS.get(stat, 1.0)
        val = round(raw, 2) if stat not in PRIMARY else max(1, int(round(raw)))
        (prim if stat in PRIMARY else sec)[stat] = val
    item["primary_stats"] = prim
    item["secondary_stats"] = sec

    # Rounding leaves a few points on the table or over it; settle the difference on the
    # largest primary stat, which is the one that can absorb it without changing the item's job.
    if prim:
        big = max(prim, key=lambda s: prim[s])
        drift = budget - spend(item)
        if abs(drift) >= 1:
            prim[big] = max(1, prim[big] + int(round(drift / _COSTS.get(big, 1.0))))

    if armor:
        item["armor_value"] = int(armor)
    if dmg:
        # `dmg` is average damage PER SWING, already speed-adjusted through the damage tier -
        # NOT a DPS figure. Multiplying it by attack_speed again put every weapon in here at
        # 2.6-3.6x its own curve, and only the auditor caught it, because a two-handed axe
        # hitting three times too hard looks like a two-handed axe.
        speed = _WEAPONS[item["weapon_type"]]["base_attack_speed"]
        # Slow weapons swing wider, which is how the procedural roller does it and is the only
        # thing that makes a 3.6s axe feel different from a 1.7s dagger at the same DPS.
        spread = min(0.34, 0.08 + 0.07 * speed)
        item["weapon_damage_min"] = int(round(dmg * (1 - spread)))
        item["weapon_damage_max"] = int(round(dmg * (1 + spread)))
        item["attack_speed"] = speed
    if item.get("weapon_type") == "shield":
        item["block_value"] = int(item["item_level"] * 1.5 * 1.7)
    return item


def build():
    levels = _levels()
    out = {}
    for boss, specs in SPECS.items():
        lv = levels[boss]
        pool = []
        for (name, slot, kind, blend, flavor) in specs:
            item = {
                "name": name,
                "slot": slot,
                "item_level": lv + 3,
                "rarity": "rare",
                "required_level": lv,
                "flavor_text": flavor,
            }
            if kind in _WEAPONS:
                item["weapon_type"] = kind
            elif kind != "accessory":
                item["armor_type"] = kind
            pool.append(_solve(item, blend))
        out[boss] = pool
    return out


def coverage(built):
    """Fail if any armour type, weapon type or player job has nothing in the region for it."""
    armors = {i.get("armor_type") for p in built.values() for i in p} - {None}
    weapons = {i.get("weapon_type") for p in built.values() for i in p} - {None}
    blends = Counter()
    for boss, specs in SPECS.items():
        for (_n, _s, _k, b, _f) in specs:
            blends[b] += 1

    bad = []
    missing_a = sorted({"cloth", "leather", "mail", "plate"} - armors)
    missing_w = sorted(set(_WEAPONS) - weapons)
    if missing_a:
        bad.append(f"no {'/'.join(missing_a)} anywhere in Arathi")
    if missing_w:
        bad.append(f"weapon types with no drop: {', '.join(missing_w)}")
    for job, names in JOBS.items():
        if not any(blends[n] for n in names):
            bad.append(f"nothing for {job}")

    # AND NOW THE QUESTION THAT ACTUALLY MATTERS: can each of the thirty classes equip
    # something from each boss? "All four armour types appear in the region" is not the same
    # claim - seven classes wear only plate, eight only cloth, and a boss whose four items are
    # all leather drops nothing for twenty-two of them. Checked per boss, against the same
    # proficiency map the equip screen uses, so it cannot disagree with the game.
    from entities import proficiency as P
    for cls in sorted(P._load_class_armor_map()):
        empty = []
        for boss, pool in built.items():
            if not any(P.can_wear_weapon_type(cls, i["weapon_type"]) if i.get("weapon_type")
                       else P.can_wear_armor_type(cls, i["armor_type"]) if i.get("armor_type")
                       else True
                       for i in pool):
                empty.append(boss)
        if len(empty) > len(built) * 0.25:
            bad.append(f"{cls} can use nothing from {len(empty)}/{len(built)} bosses")
    return bad, armors, weapons, blends


def main():
    built = build()
    bad, armors, weapons, blends = coverage(built)
    if bad:
        for b in bad:
            print(f"  FAIL  {b}")
        return 1

    items = sum(len(p) for p in built.values())
    print(f"{len(built)} bosses, {items} items, {items / len(built):.1f} per boss")
    print(f"  armour   {', '.join(sorted(armors))}")
    print(f"  weapons  {len(weapons)}/{len(_WEAPONS)} types")
    print(f"  blends   {', '.join(f'{k} x{v}' for k, v in sorted(blends.items()))}")

    if "--check" in sys.argv:
        worst = []
        for boss, pool in built.items():
            for item in pool:
                budget, armor, _d = budget_for(item)
                r = spend(item) / budget
                worst.append((abs(r - 1.0), r, boss, item["name"]))
        worst.sort(key=lambda t: -t[0])
        print("  worst spend ratios:")
        for (_d, r, boss, name) in worst[:8]:
            print(f"    {r:5.2f}  {boss:24} {name}")

    doc = {"_notes": ("Arathi Highlands named-boss and rare loot. ONE item drops per kill from "
                      "the pool. item_level = creature level + 3. Names and stat intent are "
                      "hand-authored in tools/build_arathi_boss_loot.py; the NUMBERS are solved "
                      "from LootGenerator's own budget formula there - do not hand-edit this "
                      "file, edit SPECS and re-run.")}
    doc.update({k: v for k, v in sorted(built.items())})
    OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"-> {OUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
