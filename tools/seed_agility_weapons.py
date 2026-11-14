#!/usr/bin/env python3
"""Convert a reviewed subset of hand-authored strength weapons to agility. Idempotent.

    PYTHONPATH=. python3 tools/seed_agility_weapons.py [--check]

Kyle, 29 Oct 2026:
"there should be polearms and a few 2H swords with agi. there should be agi swords anyways as rogues
can use swords. Also an agi 2H mace works for druid tanks."

THE MEASUREMENT HE IS RIGHT ABOUT. Counting every hand-authored weapon in data/quests/*.json and
data/loot/*.json by the primary stat that leads it:

    weapon      total   agility   generator allows agi_physical?
    dagger      111     88        yes
    mace_1h     108     1         yes   <- 1%
    sword_1h    90      9         yes   <- 10%
    polearm     88      7         yes   <- 8%
    axe_1h      70      3         yes   <- 4%

A Rogue can wield swords, axes and maces. The game authored 88 agility daggers against 9 agility
swords, 3 agility axes and 1 agility mace, so Rogues are funnelled into daggers by the loot table
rather than by any design decision. Hunters and feral Druids reach for polearms and find seven.
data/items/weapon_types.json has permitted agi_physical on all five of those types the whole time -
nobody ever authored it. This is an authoring gap, not an engine limit.

WHAT THIS PASS DOES. It renames the strength on 76 existing items to agility, on four weapon types
only: sword_1h, mace_1h, axe_1h, polearm. strength and agility both cost 1.0 a point in
data/items/gear_suffixes.json, so the rename is budget-neutral to the decimal - nothing is added,
removed, re-levelled or re-priced. stamina, every secondary stat, weapon damage, attack speed, name
and flavour text are all left exactly as authored.

  sword_2h and mace_2h are deliberately untouched: Kyle is handling those two himself.

HOW THE 76 WERE CHOSEN, AND WHY THE TABLE BELOW CARRIES A REASON PER ITEM. This is a judgment call
per item, not a sweep. An item converts when its name and flavour text ALREADY suggest speed,
precision, reach, hunting, stealth or a light build - "worn thin by thorn and branch", "a tooth the
size of a hand, hafted", "the balance is annoyingly perfect", "light in the hand, the way seasoned
aspen goes". An item stays strength when its whole identity is brute force. Three that were
considered and left alone, because they are the clearest cases:

  Driftwood Cudgel            "Honest and heavy." The flavour is the weight. An agility cudgel whose
                              text brags about being heavy is a worse item, not a more diverse one.
  Brood-Chamber Thumper       "Hits like a tunnel collapsing." Same.
  Dun Garok Mountaineer's     "Dwarven make, and it shows in the balance." Balance is an agility
  Hammer                      signal and this was the closest call in the pass, but it is a dwarven
                              warhammer off a Hillsbrad boss at pure strength 14 and it is what a
                              Templar or Barbarian comes to that boss for. Identity wins.

Items whose flavour is neutral - no strength and no agility signal - are fair game and were
preferred over forcing a bad fit. Conversions are spread across ilvl 1-10, 11-20, 21-30 and 31-45
and across many zones and files, because an agility sword that only exists at ilvl 40 does nothing
for a Rogue at 20.

ONE THING TO KNOW ABOUT THE COUNTS. On roughly half of these items strength was already the smaller
number next to a larger stamina - {"strength": 3, "stamina": 4}. Renaming the strength makes agility
the item's whole offensive primary, which is the thing that matters to a Rogue picking it up, but it
does NOT make agility the single largest number, so a census keyed on "largest primary stat" still
reads those as stamina items. Both censuses start from the same place (9 / 1 / 3 / 7), so the
targets are reported against "agility is the offensive primary", and the stricter
largest-stat census is reported alongside it. Hitting the targets on the strict census instead would
have meant converting 19 of the 23 strength-lead one-hand swords and leaving four, which trades one
lopsided loot table for the mirror image of it.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (item name, weapon_type) -> why this item is an agility weapon.
#: Keyed on the weapon type as well as the name because names repeat across types: there is a
#: mace_1h "Carapace-Splitter" in the Valley of Trials and an axe_1h "Carapace-Splitter" off the
#: Broodspiral Warden, and only one of them is in this pass.
CONVERSIONS = {
    # ---------------------------------------------------------------- sword_1h (Rogue, and any
    # agility class that can hold a blade). 9 -> 28 of 90.
    ("First Light Shortblade", "sword_1h"):
        "ilvl 2. A shortblade that 'feels right' in untrained hands - the lightest weapon in the "
        "starting kit, and the first thing a Rogue should be handed.",
    ("Baneshadow's Edge", "sword_1h"):
        "ilvl 6. Named for its edge, not its heft.",
    ("Manor-Reaper's Saber", "sword_1h"):
        "ilvl 8. A servant's saber, and 'someone rose from it in a hurry' - speed is the whole "
        "image. Already carried agility 1 beside strength 1.",
    ("Shade-Haunted Blade", "sword_1h"):
        "ilvl 9. 'It was a fisher's before the lake started crying' - a working fisher's blade, "
        "light, with nothing martial about its build.",
    ("Iceshard Blade", "sword_1h"):
        "ilvl 9. An ice shard is thin and keen by definition. Already half agility.",
    ("Korgal's Zealot Blade", "sword_1h"):
        "ilvl 12. 'keen enough that the blessing is almost beside the point' - keen, explicitly.",
    ("Spine-Walker's Saber", "sword_1h"):
        "ilvl 12. 'It was lighter before you knew where it came from.' Light, in its own text.",
    ("Hive-Cut Saber", "sword_1h"):
        "ilvl 17. A saber cut from chitin and silk - the thin-edged build Kyle asked for.",
    ("Brigand-Taker's Cutlass", "sword_1h"):
        "ilvl 17. 'Still sharp, still opinionated.' A brigand's blade, taken off a brigand.",
    ("Pilgrim's Reliquary Blade", "sword_1h"):
        "ilvl 19. 'A short sword in a reliquary-sheath. It sings, once, when you draw it.' Short "
        "and quick to draw.",
    ("Chitin-Forged Broadsword", "sword_1h"):
        "ilvl 20. 'The edge was ground from a broodguard's own mandible. It still bites.' A "
        "chitin-fine edge; the bite is in the cut, not the mass.",
    ("Manor-Born Saber", "sword_1h"):
        "ilvl 22. A duelling saber 'cut for a house that no longer stands'.",
    ("Wrathbringer's Falchion", "sword_1h"):
        "ilvl 24. 'A curved sword with a hooked tip' - a cutting and hooking blade.",
    ("Serpentis's Venom-Blade", "sword_1h"):
        "ilvl 25. 'A short blade whose edge weeps a faint green. Treat it as a wound.' Short blade, "
        "poison - a Rogue's item in everything but its stats.",
    ("Naralex's Memory-Blade", "sword_1h"):
        "ilvl 27. 'A long blade of pale wood' remembering a druid. Wood, not steel; and a feral "
        "Druid is exactly who should carry it.",
    ("Frostbrand of the Hunt-King", "sword_1h"):
        "ilvl 27. 'A hunter's blade ... it still remembers the sound a quarry makes.' Hunting, "
        "stated. Already carried agility 6 beside strength 6.",
    ("Vial-Pocket Saber", "sword_1h"):
        "ilvl 31. An apothecary's saber - 'every pocket holds a stopper'. Built to be carried, not "
        "swung from the shoulder.",
    ("Bloodsail Longsword", "sword_1h"):
        "ilvl 41. Neutral flavour (a crew's mark scratched over twice) and the ilvl 41 band had "
        "almost no agility sword at all.",
    ("Vantch's Shallows Cutlass", "sword_1h"):
        "ilvl 45. 'Short in the blade. She has never fought anybody on open deck in her life.' A "
        "below-decks knife-fighter's cutlass.",

    # ---------------------------------------------------------------- mace_1h (the worst gap in the
    # game at 1 of 108, and the one that needed the most care because maces are brute by default).
    # 1 -> 25 of 108.
    ("Rattlecage Femur Club", "mace_1h"):
        "ilvl 4. 'A genuine femur.' A bone club is light; the joke is the provenance, not the mass.",
    ("Linen-Wrapped Hammer", "mace_1h"):
        "ilvl 4. 'A maul wrapped in clean linen. For quiet work.' Quiet work is stealth.",
    ("Prospector's Pick-Mace", "mace_1h"):
        "ilvl 5. A pick with the point flattened - a precision tool repurposed. Already half "
        "agility.",
    ("Orchard-Keeper's Hoe", "mace_1h"):
        "ilvl 7. 'A garden tool turned bludgeon' - a hoe, not a maul.",
    ("Fitz's Pick-Hammer", "mace_1h"):
        "ilvl 10. 'Half pick, half hammer.' The pick half is the precise half.",
    ("Imp-Bone Cudgel", "mace_1h"):
        "ilvl 10. 'Small, ugly, and fond of finding the soft spot.' Finding the soft spot is what "
        "agility does. Already half agility.",
    ("Sigil-Marked Hammer", "mace_1h"):
        "ilvl 11. Neutral flavour ('warm in the wrong places'); taken to keep the 11-20 band from "
        "being empty of agility maces.",
    ("Gnawed Femur Cudgel", "mace_1h"):
        "ilvl 14. A thigh bone chewed to a handle. Light, improvised, nobody's siege weapon.",
    ("Spiral-Carved Mace", "mace_1h"):
        "ilvl 15. 'A short mace ... every blow feels slightly like a wave.' Short, and the image is "
        "flow rather than impact.",
    ("Claw-Hammer of the Flats", "mace_1h"):
        "ilvl 15. 'A claw, lashed to a haft. It has not forgotten its last meal.' A predator's "
        "claw on a stick - beast-kill flavour, which is Hunter and feral Druid territory.",
    ("Seamcutter's Warhammer", "mace_1h"):
        "ilvl 17. A miner's hammer with a smith's temper, cutting seams rather than breaking rock. "
        "Already carried agility 3 beside strength 3.",
    ("Wagon-Guard Cudgel", "mace_1h"):
        "ilvl 17. 'A short iron-banded club.' Short, carried on a wagon all day.",
    ("Hound-Tamer's Chain-Whip", "mace_1h"):
        "ilvl 20. 'A LIGHT chain on a leather grip.' Light, in its own text, and a houndsman's "
        "tool. Already carried agility 2.",
    ("Foreman's Bone Pick", "mace_1h"):
        "ilvl 21. 'A pick carved from a femur' - a pick, and bone.",
    ("Crossing-Keeper's Truncheon", "mace_1h"):
        "ilvl 22. 'Short, heavy and well-balanced.' Balanced, and short enough to use in a crowd. "
        "Already carried agility 3 beside strength 3.",
    ("Cutpurse Mace", "mace_1h"):
        "ilvl 23. 'It passed through three hands this month.' A cutpurse's weapon. There is no "
        "reading of this item on which it is a strength mace.",
    ("Herd-Mother's Gavel", "mace_1h"):
        "ilvl 23. 'A short-handled mace carved from a horn-tip.' Short-handled and hollow horn.",
    ("Rethilgore's Chain-Flail", "mace_1h"):
        "ilvl 24. A hound-master's three-link flail - a flail is swung, not shoved.",
    ("Boltcog's Dig-Hammer", "mace_1h"):
        "ilvl 25. 'Good for rocks, LOCKS and people who ask the wrong questions.' Locks.",
    ("Old-Cold Flail", "mace_1h"):
        "ilvl 31. Neutral flavour (came out of the ice this spring); a flail, and the 31+ band "
        "needed agility maces.",
    ("Figure-Cut Mace", "mace_1h"):
        "ilvl 33. Neutral flavour ('there are others, they are identical') - Underdark mass "
        "production, no weight claim either way.",
    ("Hexbinder's Mace", "mace_1h"):
        "ilvl 33. 'A bone-capped mace, carved with the names of those who stopped arguing.' Bone "
        "cap, and the threat is the carving rather than the heft.",
    ("Greyquill Hammer", "mace_1h"):
        "ilvl 36. Neutral flavour ('somebody wanted this forgotten').",
    ("Druse Flail", "mace_1h"):
        "ilvl 36. 'Still faintly growing, which is fine.' Grown crystal, neutral on weight.",

    # ---------------------------------------------------------------- axe_1h (Rogues and Barbarians
    # share these; hatchets and billhooks are the obvious agility half). 3 -> 18 of 70.
    ("Thorn-Torn Axe", "axe_1h"):
        "ilvl 6. 'Worn THIN by thorn and branch.' Thin, stated.",
    ("Gravekeeper's Hatchet", "axe_1h"):
        "ilvl 9. 'A small, solemn thing.' Small. Already half agility.",
    ("Lamplit Hatchet", "axe_1h"):
        "ilvl 9. 'Issued in the Rotunda, mended in the dark.' A hatchet carried through Undercity "
        "tunnels. Already half agility.",
    ("Skitterer's Axe", "axe_1h"):
        "ilvl 11. 'Chitin, silk and nerve. Nothing wasted.' Nothing wasted is the opposite of mass.",
    ("Razorjaw Tooth Hatchet", "axe_1h"):
        "ilvl 16. 'A tooth the size of a hand, hafted. Cuts like it still wants to.' A tooth in a "
        "light haft - the exact item Kyle described.",
    ("Quartermaster's Boarding Axe", "axe_1h"):
        "ilvl 17. 'A BALANCED boarding axe with a hook at the back. It parts a deck rail like "
        "paper.' Already carried agility 3 beside strength 3.",
    ("Kennel-Keeper's Hooked Axe", "axe_1h"):
        "ilvl 17. 'One side for splitting, the other for dragging a stubborn hound home.' The hook "
        "is handling, not force. Already carried agility 3.",
    ("Reed-Cutter's Billhook", "axe_1h"):
        "ilvl 18. 'A curved blade for cutting reeds. Also slugs.' A billhook cuts; it does not "
        "break.",
    ("Hyena-Tooth Hatchet", "axe_1h"):
        "ilvl 21. 'A small axe with a hyena tooth set in the pommel.' Small axe, tooth.",
    ("Cobrahn's Fanged Cleaver", "axe_1h"):
        "ilvl 23. 'A fang set into the head. It bites, then it lets go. That is how snakes do it.' "
        "A fang, and a strike-and-withdraw description.",
    ("Sergeant's Marching Axe", "axe_1h"):
        "ilvl 26. 'A short axe built for crowded places. FAST, honest, and meaner than it looks.' "
        "Fast, stated.",
    ("Bramble-Cutter", "axe_1h"):
        "ilvl 28. 'A short hooked blade for cutting thorn.' Short and hooked.",
    ("Barded Cleaver", "axe_1h"):
        "ilvl 31. 'Made to be worn at a canter for a whole day.' Carried on horseback - it has to "
        "be light enough to wear, which is the Outrider build.",
    ("Roogug's Vine-Cutter", "axe_1h"):
        "ilvl 31. 'A hooked axe made for cutting thorn and, when thorn is not available, other "
        "things.'",
    ("Powder-Burned Hatchet", "axe_1h"):
        "ilvl 41. A hatchet 'cut for a man who expected to spend his life wet' - neutral on weight, "
        "and the top band had no agility axe.",

    # ---------------------------------------------------------------- polearm (Hunters and feral
    # Druids; reach and stalking are already most of what these items say). 7 -> 25 of 88.
    ("Dunestalker's Longspear", "polearm"):
        "ilvl 6. A dunestalker's spear. Stalking is the name of the item.",
    ("Pond-Dredged Pike", "polearm"):
        "ilvl 7. Neutral flavour (the pond keeps what falls in); the 1-10 band needed agility "
        "polearms a Hunter can actually start with.",
    ("Valley-Walker's Spear", "polearm"):
        "ilvl 8. 'Ash-wood haft, iron head. It has WALKED out of the valley before.' A walker's "
        "spear, carried a long way. Already half agility.",
    ("Claim-Warden's Spear", "polearm"):
        "ilvl 8. 'A long spear made for long shafts' - reach is the entire point. Already half "
        "agility.",
    ("Talon-Wrapped Spear", "polearm"):
        "ilvl 14. 'Raptor talons lashed under the head. It TEARS as it goes in.' Already carried "
        "agility 9 beside strength 9.",
    ("Ssaleth's Warden-Pike", "polearm"):
        "ilvl 16. 'A coral pike, spiral-fluted ... and surprisingly WELL BALANCED for a human "
        "hand.' Balance, stated.",
    ("Mate's Boarding Pike", "polearm"):
        "ilvl 16. 'A SHORT boarding pike, hooked at the back to drag a rail.'",
    ("Salamander-Tooth Spear", "polearm"):
        "ilvl 19. 'A single curved fang on a charred haft. It WANTS TO BE THROWN.' A thrown spear "
        "is an agility weapon by definition. Already carried agility 10.",
    ("Gatebreaker's Spear", "polearm"):
        "ilvl 20. 'Taken from a night elf picket. The BALANCE is annoyingly PERFECT.' Elven work, "
        "perfectly balanced - the in-scope equivalent of the Moonglaive. The name is about what it "
        "was taken from, not how it hits.",
    ("Hollow-Guard's Spear", "polearm"):
        "ilvl 20. 'A long spear for REACHING nests. It also reaches harpies.' Reach, twice.",
    ("Longleg's Venom-Barbed Spear", "polearm"):
        "ilvl 20. 'A leg-spine as long as a man, HOLLOW, and still weeping.' Hollow bone and "
        "venom.",
    ("Ramp-Guard Spear", "polearm"):
        "ilvl 21. 'Long enough to reach over a rail. Short enough to still stab someone.' Reach "
        "and a stab, with no mention of weight.",
    ("Aspen Spear", "polearm"):
        "ilvl 28. 'LIGHT IN THE HAND, the way seasoned aspen goes.' Light, stated outright.",
    ("Dust-Caught Pike", "polearm"):
        "ilvl 29. Neutral flavour (two kinds of dirt on it) - a surveyor's pike carried across two "
        "zones.",
    ("Standing-Water Spear", "polearm"):
        "ilvl 34. 'Crocolisk hide, taken off the one that took the nets.' A hunting trophy spear.",
    ("Glacier-Jaw Pike", "polearm"):
        "ilvl 36. 'Ice in the sockets, and the sockets are not his.' A predator's jaw on a haft. "
        "Already carried agility 20 beside strength 20.",
    ("Lagoon-Damp Pike", "polearm"):
        "ilvl 39. Neutral flavour (mended twice on the boards, both times cheap).",
    ("Favourite's Gurbashi Pike", "polearm"):
        "ilvl 41. 'Longer than the pit is wide at the ends. She has never needed the ends.' An "
        "arena duellist who wins on footwork. Already carried agility 22 beside strength 23.",
}

#: Types this pass is allowed to touch at all. sword_2h and mace_2h are Kyle's.
ALLOWED_TYPES = {"sword_1h", "mace_1h", "axe_1h", "polearm"}

_COSTS = json.loads((ROOT / "data/items/gear_suffixes.json").read_text(encoding="utf-8"))["stat_budget_costs"]


def _spend(item):
    """What this item's stats cost, priced exactly as the generator prices them."""
    total = 0.0
    for block in ("primary_stats", "secondary_stats"):
        for stat, value in (item.get(block) or {}).items():
            total += float(value) * _COSTS.get(stat, 1.0)
    return total


def _items_in(doc):
    """Every hand-authored item dict in a quest file or a loot file, in place."""
    for quest in doc.get("quests", []) or []:
        for item in (quest.get("unique_item_defs") or []) + (quest.get("rewards") or []):
            if isinstance(item, dict):
                yield item
    if "quests" not in doc:
        rows = doc.get("bosses", doc)
        if isinstance(rows, dict):
            for owner, items in rows.items():
                if owner.startswith("_") or not isinstance(items, list):
                    continue
                for item in items:
                    if isinstance(item, dict):
                        yield item


def convert(item):
    """Rename this item's strength to agility in place. Budget-neutral. Returns True if changed."""
    primaries = item.get("primary_stats") or {}
    if "strength" not in primaries:
        return False
    moved = primaries.pop("strength")
    primaries["agility"] = primaries.get("agility", 0) + moved
    item["primary_stats"] = primaries
    if item.get("stat_template") == "str_physical":
        item["stat_template"] = "agi_physical"
    return True


def main():
    check = "--check" in sys.argv[1:]

    seen = defaultdict(list)       # (name, wtype) -> [(path, before_spend)]
    changed_paths = {}
    touched = 0
    budget_errors = []

    paths = sorted((ROOT / "data/quests").glob("*.json")) + \
        sorted((ROOT / "data/loot").glob("*.json"))

    for path in paths:
        doc = json.loads(path.read_text(encoding="utf-8"))
        dirty = False
        for item in _items_in(doc):
            key = (item.get("name"), item.get("weapon_type"))
            if key not in CONVERSIONS:
                continue
            if key[1] not in ALLOWED_TYPES:            # belt and braces
                continue
            before = _spend(item)
            seen[key].append((path.name, before))
            if convert(item):
                after = _spend(item)
                if abs(after - before) > 1e-9:
                    budget_errors.append(
                        f"{item['name']} ({path.name}): spend {before:.2f} -> {after:.2f}")
                touched += 1
                dirty = True
        if dirty:
            changed_paths[path] = doc

    missing = [k for k in CONVERSIONS if k not in seen]

    for (name, wtype), hits in sorted(seen.items()):
        files = ", ".join(sorted({f for f, _ in hits}))
        print(f"  {wtype:<9} {name:<34} x{len(hits)}  [{files}]")

    print()
    print(f"items in table : {len(CONVERSIONS)}")
    print(f"rows matched   : {sum(len(v) for v in seen.values())}")
    print(f"rows converted : {touched}" + ("  (already agility - nothing to do)" if not touched
                                           else ""))
    print(f"files to write : {len(changed_paths)}")

    if missing:
        print("\nTABLE ERRORS - these names matched nothing, fix the table:")
        for name, wtype in sorted(missing):
            print(f"  {wtype} / {name}")
    if budget_errors:
        print("\nBUDGET ERRORS - a conversion changed an item's spend, which must never happen:")
        for line in budget_errors:
            print(f"  {line}")
        return 1

    if check:
        print("\n--check: nothing written.")
        return 1 if missing else 0

    for path, doc in changed_paths.items():
        path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"\nwrote {len(changed_paths)} files.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
