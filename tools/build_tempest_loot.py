#!/usr/bin/env python3
"""Tempest Isle: loot for all 19 dungeon bosses, and the T0 set tokens they drop. Idempotent.

    PYTHONPATH=. python3 tools/build_tempest_loot.py

Writes data/loot/tempest_isle_boss_loot.json (the items) and data/items/set_tokens.json (the
tokens and which boss carries which). Kyle, 13 Nov 2026:

  * "We can add T0 for bracers, belt, and pants in these dungeons."
  * "maybe tokens would be better, yeah. based on type of armor they give?" - so TWELVE tokens:
    bracers, belt and legs, each in plate, mail, leather and cloth. An Artifact Keeper trades a
    token for that slot's piece of your own class set (world/set_tokens.py).
  * "bosses in the higher rank (52+ dungeons) can drop 6 items, 3/6 are class pieces" - every boss
    carries three items of its own and three of the four armour types of its token. The armour
    type a boss lacks rotates, so each type is on three bosses in every four.
  * "20% token drop. with one guaranteed from the last boss."
  * "KEEP IN MIND TRINKETS CAN DO THINGS NOW - MOVE THE 50+ TRINKETS SLOWLY FROM BEING BASIC
    STAT STICKS" - four of the 57 items are trinkets, and all four do something.

WHERE THE TOKENS ARE. Bracers on Khaz Varun's first floor, belts on its second, legs in the
Emberdeep. So the bosses' own items avoid those slots where their token is: no bracers or belts
in Khaz Varun, no legs in the Emberdeep.

NO FIRE RESISTANCE YET, though a volcano is the obvious place for it. The item formula prices
resistance at ten budget points each, so "of Fire Protection" on a level 54 breastplate comes out
at 2 fire resistance, which reads as a mistake. Older hand-made pieces carry about 21 from before
that price changed. Until the player-side resistance rescale is settled
(claude/resistance_player_side_rescale_PENDING.md) these pools carry none.

ONE ITEM PER KILL from a boss's three. Item level = the boss's top level + 3, the same offset as
the T0 pieces. Stats from the real formulas (tools/build_durotar_content.make). No flavour text:
these are rares.
"""
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make  # noqa: E402

OUT = ROOT / "data/loot/tempest_isle_boss_loot.json"
TOKENS_OUT = ROOT / "data/items/set_tokens.json"
ARMOUR = ("plate", "mail", "leather", "cloth")
TOKEN_CHANCE = 0.20

#: (zone, cave) -> bosses in run order, each with the slot of the token it carries
DUNGEONS = {
    ("Tempest Shallows", "Khaz Varun, the Black Hollow"): [
        ("Gatewarden Hrun", "wrist"), ("The Crusher", "wrist"), ("Smelter-Master Vaud", "wrist"),
        ("Powderkeg Nix", "wrist"), ("Overseer Grall", "wrist"), ("Forge-Lord Darrok", "wrist"),
        ("The Iron Mask", "waist"), ("The Ashwretch Brood", "waist"), ("The Rock-Borer Queen", "waist"),
        ("Flamespeaker Maud", "waist"), ("The Shadow of the Forge", "waist"),
        ("Thane Morrun the Unmade", "waist"),
    ],
    ("The Ashen Reach", "The Emberdeep"): [
        ("Pack-Alpha Cinderhound", "legs"), ("Thrass, the Geyser Spirit", "legs"),
        ("Basalt Guardian Vok", "legs"), ("The Molten Serpent", "legs"),
        ("Flame Oracle Ysmel", "legs"), ("The Mountain's Heart", "legs"), ("The Caldera", "legs"),
    ],
    # The Royal Hive under the Black Strand (tools/handbuilt_royal_hive.py), 54-56. Kyle, 14 Nov:
    # "Let's quickly flesh out the Royal Hive as it'll drop another token" - the shoulders.
    ("The Black Strand", "The Royal Hive"): [
        ("Hive-Warden Kasz'ar", "shoulder"), ("The Brood Nurse", "shoulder"),
        ("Resin-Mother Vex'ith", "shoulder"), ("Tunnel-King Ruzzak", "shoulder"),
        ("Hive-Mother Ahn'thera", "shoulder"),
    ],
}
#: The last boss of each dungeon always drops a token, of any armour type.
FINAL = ("Thane Morrun the Unmade", "The Caldera", "Hive-Mother Ahn'thera")
#: Bosses whose pool is nine because three drop at once (entities/boss_loot.MULTI_DROP).
MULTI = ("Hive-Mother Ahn'thera",)
#: Pack members whose loot is the lead's (entities/boss_loot.SHARED_HOARD).
SHARED_HOARD = ("Royal Consort Zhir'ak",)
#: The token slots each dungeon carries, so its own items stay out of them.
TOKEN_SLOTS = {"Khaz Varun, the Black Hollow": ("wrist", "waist"), "The Emberdeep": ("legs",),
               "The Royal Hive": ("shoulder",)}

TOKEN_NAMES = {"wrist": "Bindings of the Black Hollow", "waist": "Girdle of the Black Hollow",
               "legs": "Legguards of the Emberdeep", "shoulder": "Mantle of the Royal Hive"}
SLOT_WORD = {"wrist": "bracers", "waist": "belt", "legs": "legs", "shoulder": "shoulders"}
#: A set piece of the right slot and armour type, borrowed as the token's picture.
TOKEN_ICON_CLASS = {"plate": "warrior", "mail": "shaman", "leather": "rogue", "cloth": "priest"}

#: Trinkets that do something. Same proc engine as the epics' (tools/build_epic_drops.PROCS),
#: sized a step below them because these are rares.
PROCS = {
    "Gatewarden's Horn": {
        "trigger": "on_damage_taken", "chance": 10, "icd": 5, "heal_flat": 150,
        "describe": "When you are hit, you have a chance to heal for 150.",
    },
    "Cinder-Prayer Beads": {
        "trigger": "on_heal_cast", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "cinder_prayer_answered", "name": "Prayer Answered",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"healing_power": 45}, "on_target": False},
        "describe": "Your healing spells have a chance to grant 45 healing power for 3 turns.",
    },
    "Alpha's Dewclaw": {
        "trigger": "on_crit", "chance": 15, "icd": 5,
        "apply_effect": {"effect_id": "alphas_dewclaw_blooded", "name": "Blooded",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"attack_power": 50}, "on_target": False},
        "describe": "Your critical strikes have a chance to grant 50 attack power for 3 turns.",
    },
    "Shard of the Mountain's Heart": {
        "trigger": "on_damage_cast", "chance": 8, "icd": 5,
        "apply_effect": {"effect_id": "mountains_heart_pulse", "name": "Heartbeat of Stone",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"spell_power": 32}, "on_target": False},
        "describe": "Your damaging spells have a chance to grant 32 spell power for 3 turns.",
    },
    "Drop of Royal Amber": {
        "trigger": "on_damage_taken", "chance": 10, "icd": 5,
        "apply_effect": {"effect_id": "royal_amber_set", "name": "Set in Amber",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"armor": 420}, "on_target": False},
        "describe": "When you are hit, you have a chance to gain 420 armour for 3 turns.",
    },
    "Ahn'thera's Last Egg": {
        "trigger": "on_damage_cast", "chance": 8, "icd": 5,
        "apply_effect": {"effect_id": "last_egg_hatches", "name": "The Egg Hatches",
                         "effect_type": "buff", "duration": 3,
                         "stat_mods": {"spell_power": 36, "haste": 4}, "on_target": False},
        "describe": "Your damaging spells have a chance to grant 36 spell power and 4 haste for 3 turns.",
    },
}


def levels():
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    return {n: creatures[n]["level_range"][1] for bosses in DUNGEONS.values() for n, _ in bosses}


def pools():
    lv = levels()
    P = {}

    def boss(name, *rows):
        ilvl = lv[name] + 3
        out = []
        for row in rows:
            item_name, slot, suffix = row[:3]
            kw = row[3] if len(row) > 3 else {}
            d = make(item_name, slot, suffix, ilvl, "", **kw)
            d.pop("flavor_text", None)
            if item_name in PROCS:
                d["proc"] = PROCS[item_name]
            out.append(d)
        P[name] = out

    A = lambda t: {"armor_type": t}      # noqa: E731
    W = lambda t: {"weapon_type": t}     # noqa: E731

    # ---------------- KHAZ VARUN, floor 1: the Upper Works ----------------
    boss("Gatewarden Hrun",                       # a shield wall at the gate
         ("Gatewarden's Tower Shield", "off_hand", "of Stamina", W("shield")),
         ("Hrun's Watch-Helm", "head", "of the Defender", A("plate")),
         ("Gatewarden's Horn", "trinket", "of the Champion"))
    boss("The Crusher",                           # the ore crusher, still running
         ("Crusher's Counterweight", "main_hand", "of the Gladiator", W("mace_2h")),
         ("Slagplate Sabatons", "feet", "of the Soldier", A("plate")),
         ("Stone-Dust Mantle", "shoulder", "of the Sorcerer", A("cloth")))
    boss("Smelter-Master Vaud",                   # he and his slag oozes
         ("Vaud's Slag Ladle", "main_hand", "of the Invoker", W("staff")),
         ("Smelter's Apron", "chest", "of the Physician", A("leather")),
         ("Crucible-Tender's Gloves", "hands", "of the Falcon", A("mail")))
    boss("Powderkeg Nix",                         # a goblin who went native
         ("Nix's Bolt-Thrower", "ranged", "of the Sharpshooter", W("crossbow")),
         ("Blast-Scorched Hood", "head", "of the Assassin", A("leather")),
         ("Powder-Monkey's Boots", "feet", "of the Hunt", A("mail")))
    boss("Overseer Grall",                        # and the ledger he keeps
         ("The Overseer's Ledger", "off_hand", "of the Archmage", W("tome")),
         ("Grall's Tally-Blade", "main_hand", "of the Bandit", W("sword_1h")),
         ("Taskmaster's Pauldrons", "shoulder", "of the Vanquisher", A("plate")))
    boss("Forge-Lord Darrok",                     # turns magic into armour
         ("Darrok's Forge Hammer", "main_hand", "of the Prophet", W("mace_1h")),
         ("Forge-Lord's Breastplate", "chest", "of the Squire", A("plate")),
         ("Emberglass Band", "ring", "of the Invoker"))

    # ---------------- KHAZ VARUN, floor 2: the Deeps ----------------
    boss("The Iron Mask",                         # the jailer
         ("Mask of the Silent Warden", "head", "of the Hunt", A("mail")),
         ("Jailer's Hooked Axe", "main_hand", "of the Champion", W("axe_1h")),
         ("Warden's Shackle-Cloak", "back", "of the Warder", A("cloth")))
    boss("The Ashwretch Brood",                   # many small dead things
         ("Broodwrap Robe", "chest", "of the Owl", A("cloth")),
         ("Ash-Bitten Athame", "main_hand", "of the Mind's Eye", W("dagger")),
         ("Gravedust Treads", "feet", "of the Monkey", A("leather")))
    boss("The Rock-Borer Queen",                  # enormous armour
         ("Queen's Mandible", "main_hand", "of the Monkey", W("polearm")),
         ("Borer-Chitin Spaulders", "shoulder", "of the Bandit", A("mail")),
         ("Tunnel-Mother's Hauberk", "chest", "of the Elder", A("mail")))
    boss("Flamespeaker Maud",                     # heals off fire
         ("Maud's Kindling Rod", "ranged", "of Fiery Wrath", W("wand")),
         ("Flamespeaker's Cowl", "head", "of the Invoker", A("cloth")),
         ("Cinder-Prayer Beads", "trinket", "of the Prophet"))
    boss("The Shadow of the Forge",               # what the forge left behind
         ("Shadowforged Greatsword", "main_hand", "of the Soldier", W("sword_2h")),
         ("Sootveil Gloves", "hands", "of Shadow Wrath", A("cloth")),
         ("Forge-Shade Leggings", "legs", "of the Falcon", A("leather")))
    boss("Thane Morrun the Unmade",               # the thane's ancestor, half stone
         ("Morrun's Stone-Fused Crown", "head", "of the Gorilla", A("plate")),
         ("Knuckles of the Unmade", "main_hand", "of the Tiger", W("fist_weapon")),
         ("Signet of Khaz Varun", "ring", "of the Champion"))

    # ---------------- THE EMBERDEEP ----------------
    boss("Pack-Alpha Cinderhound",
         ("Alpha's Fang", "main_hand", "of the Assassin", W("dagger")),
         ("Cinderhound Hide Jerkin", "chest", "of the Bandit", A("leather")),
         ("Alpha's Dewclaw", "trinket", "of the Sharpshooter"))
    boss("Thrass, the Geyser Spirit",
         ("Scaldwater Staff", "main_hand", "of the Wellspring", W("staff")),
         ("Steam-Wreathed Shoulderpads", "shoulder", "of the Physician", A("leather")),
         ("Thrass's Boiling Wraps", "wrist", "of the Sorcerer", A("cloth")))
    boss("Basalt Guardian Vok",
         ("Vok's Basalt Bulwark", "off_hand", "of Stamina", W("shield")),
         ("Columnar Greathelm", "head", "of the Warder", A("plate")),
         ("Guardian's Hexagon Girdle", "waist", "of the Marksman", A("mail")))
    boss("The Molten Serpent",
         ("Serpent-Spine Longbow", "ranged", "of the Marksman", W("bow")),
         ("Magma-Scale Gauntlets", "hands", "of the Elder", A("mail")),
         ("Lava-Shed Cloak", "back", "of the Eagle", A("cloth")))
    boss("Flame Oracle Ysmel",
         ("Oracle's Burning Tome", "off_hand", "of the Breach", W("tome")),
         ("Ysmel's Seeing Circlet", "head", "of the Prophet", A("cloth")),
         ("Ashen Prophecy Mantle", "shoulder", "of the Wellspring", A("mail")))
    boss("The Mountain's Heart",                  # optional, off the main chain
         ("Shard of the Mountain's Heart", "trinket", "of the Sorcerer"),
         ("Deep-Stone Sabatons", "feet", "of the Champion", A("plate")),
         ("Magma-Vein Bracers", "wrist", "of the Tiger", A("leather")))
    boss("The Caldera",
         ("Caldera's Fury", "main_hand", "of the Breaker", W("axe_2h")),
         ("Rimfire Gloves", "hands", "of the Archmage", A("cloth")),
         ("Crater-Forged Hauberk", "chest", "of the Hunt", A("mail")))

    # ---------------- THE ROYAL HIVE ----------------
    boss("Hive-Warden Kasz'ar",                   # the carapace at the door
         ("Warden's Chitin Glaive", "main_hand", "of the Soldier", W("polearm")),
         ("Carapace Breastplate", "chest", "of the Defender", A("plate")),
         ("Royal Sentry Girdle", "waist", "of the Bandit", A("leather")))
    boss("The Brood Nurse",                       # optional, the nursery
         ("Nursery Wand", "ranged", "of the Wellspring", W("wand")),
         ("Larva-Silk Leggings", "legs", "of the Owl", A("cloth")),
         ("Brood-Warmed Signet", "ring", "of the Physician"))
    boss("Resin-Mother Vex'ith",                  # seals you in amber
         ("Resin-Sealed Gauntlets", "hands", "of the Champion", A("plate")),
         ("Drop of Royal Amber", "trinket", "of the Defender"),
         ("Resin-Mother's Cudgel", "main_hand", "of the Prophet", W("mace_1h")))
    boss("Tunnel-King Ruzzak",                    # burrows
         ("Tunnel-King's Mandible", "main_hand", "of the Gladiator", W("axe_2h")),
         ("Burrower's Treads", "feet", "of the Tiger", A("leather")),
         ("Earthen Coil", "neck", "of the Gorilla"))
    # The queen and her Consort: ONE hoard, three items off it per kill (entities/boss_loot.py
    # MULTI_DROP and SHARED_HOARD), so the pool is nine and covers the whole party.
    boss("Hive-Mother Ahn'thera",
         ("The Royal Stinger", "main_hand", "of the Assassin", W("sword_1h")),
         ("Consort's Sundering Glaive", "main_hand", "of the Champion", W("polearm")),
         ("Chitin-Strung Longbow", "ranged", "of the Hunt", W("bow")),
         ("Crown of the Hive", "head", "of the Elder", A("mail")),
         ("Zhir'ak's Carapace", "chest", "of the Defender", A("plate")),
         ("Robes of the Queen's Bower", "chest", "of the Prophet", A("cloth")),
         ("Attendant's Gloves", "hands", "of the Bandit", A("leather")),
         ("Ring of the Twin Thrones", "ring", "of the Invoker"),
         ("Ahn'thera's Last Egg", "trinket", "of the Sorcerer"))
    return P


def tokens():
    """-> {"chance", "tokens": {id: {...}}, "bosses": {name: {slot, types, guaranteed}}}"""
    defs = {}
    for slot, title in TOKEN_NAMES.items():
        for t in ARMOUR:
            defs[f"t0_token_{slot}_{t}"] = {
                "name": f"{title} ({t.title()})", "slot": slot, "armor_type": t, "tier": "T0",
                "icon_id": f"t0_{TOKEN_ICON_CLASS[t]}_{slot}",
                "description": (f"A token. Any Artifact Keeper will trade it for the T0 set "
                                f"{SLOT_WORD[slot]} of a class that wears {t}."),
            }
    bosses = {}
    for run in DUNGEONS.values():
        for i, (name, slot) in enumerate(run):
            last = name in FINAL
            bosses[name] = {"slot": slot, "guaranteed": last,
                            "types": list(ARMOUR) if last else [t for k, t in enumerate(ARMOUR) if k != i % 4]}
    return {"_about": "T0 set tokens. BUILT by tools/build_tempest_loot.py - edit that, not this. "
                      "Rolled and redeemed by world/set_tokens.py.",
            "chance": TOKEN_CHANCE, "tokens": defs, "bosses": bosses}


def audit(P, T):
    bad = []
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    enc = json.loads((ROOT / "data/creatures/encounters.json").read_text(encoding="utf-8"))["zones"]
    lv = levels()
    for (zone, cave), run in DUNGEONS.items():
        real = {n for n in enc[zone]["caves"][cave]["creatures"] if creatures.get(n, {}).get("is_boss")}
        real -= set(SHARED_HOARD)              # a pack member drops nothing of its own
        if real != {n for n, _ in run}:
            bad.append(f"{cave}: bosses differ from the dungeon's own: {sorted(real ^ {n for n, _ in run})}")
        for name, token_slot in run:
            pool = P.get(name, [])
            want = 9 if name in MULTI else 3
            if len(pool) != want:
                bad.append(f"{name}: {len(pool)} items, wanted {want}")
            for i in pool:
                if i["item_level"] != lv[name] + 3:
                    bad.append(f"{i['name']}: item level {i['item_level']}, {name} is level {lv[name]}")
                clash = TOKEN_SLOTS[cave]
                if i["slot"] in clash:
                    bad.append(f"{i['name']} is a {i['slot']} piece in the dungeon whose token that is")
                if i["slot"].startswith("trinket") and not i.get("proc"):
                    bad.append(f"{i['name']} is a trinket that does nothing")
    items = [i for v in P.values() for i in v]
    dup = [n for n, c in Counter(i["name"] for i in items).items() if c > 1]
    if dup:
        bad.append(f"duplicate names: {dup}")
    arm = Counter(i["armor_type"] for i in items if i.get("armor_type"))
    for t in ARMOUR:
        if not 6 <= arm[t] <= 12:
            bad.append(f"{arm[t]} {t} pieces of {sum(arm.values())}: the spread is lopsided")
    weapons = Counter(i["weapon_type"] for i in items if i.get("weapon_type"))
    if max(weapons.values()) > 3:
        bad.append(f"a weapon type appears more than twice: {dict(weapons)}")
    if len(weapons) < 14:
        bad.append(f"only {len(weapons)} weapon types used")
    # every armour type's token is on at least four bosses per slot, and the last boss has all four
    for slot in TOKEN_NAMES:
        for t in ARMOUR:
            n = sum(1 for b in T["bosses"].values() if b["slot"] == slot and t in b["types"])
            if n < 4:
                bad.append(f"the {t} {slot} token is only on {n} bosses")
    if len(T["tokens"]) != 4 * len(TOKEN_NAMES):
        bad.append(f"{len(T['tokens'])} tokens, wanted {4 * len(TOKEN_NAMES)}")
    return bad, arm, weapons


def main():
    P, T = pools(), tokens()
    bad, arm, weapons = audit(P, T)
    if bad:
        print("FAILED - fix the pools, not the check:")
        for b in bad:
            print("  -", b)
        return 1
    out = {"_notes": "Boss loot for the 51-58 dungeons: Khaz Varun and the Emberdeep (Tempest Isle) and the Royal Hive (under the Black Strand). ONE item drops "
                     "per kill from the pool of three. item_level = boss level + 3. T0 tokens are "
                     "separate (data/items/set_tokens.json). Hand-authored in tools/build_tempest_loot.py."}
    out.update(P)
    OUT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    TOKENS_OUT.write_text(json.dumps(T, indent=2) + "\n", encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "tools/whole_number_gear.py")], check=True,
                   stdout=subprocess.DEVNULL)
    n = sum(len(v) for v in P.values())
    print(f"{len(P)} bosses, {n} items -> {OUT.name}; {len(T['tokens'])} tokens -> {TOKENS_OUT.name}")
    print(f"  armour {dict(arm)}")
    print(f"  weapons {dict(weapons)}")
    print(f"  trinkets with a proc: {sum(1 for v in P.values() for i in v if i.get('proc'))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
