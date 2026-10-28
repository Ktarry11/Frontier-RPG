#!/usr/bin/env python3
"""Build the ore and wood ladders out to 40 tiers, like cloth and leather. Idempotent.

    PYTHONPATH=. python3 tools/build_ore_wood_ladders.py [--apply]

Kyle, 2026-10-28: "The ore and wood have more, they're just not Implemented. We should have them in
the files."

The crafting audit found blacksmithing and woodworking stuck in a way the re-tier pass could not
fix: cloth and leather carry 40 authored tiers each, while ore had 7 and wood had 7, so those two
ladders simply ended. A smith at skill 200 was still smelting bronze because bronze is near the top
of what exists. This writes the rest of both ladders.

BANDS ARE COPIED FROM THE CLOTH LADDER RATHER THAN INVENTED. Cloth already spans skill 5 to 460
across 40 tiers with a spacing somebody tuned, and three ladders drifting apart is how the
skill-versus-material gap appeared in the first place. So each new tier takes a cloth tier's
skill_range and tier label wholesale, starting from the rung just above where the existing ore or
wood tiers stop. The seven existing tiers of each are left exactly as they are - they are in live
zones and in working recipes, and renumbering them would move content players can already reach.

REAL NAMES FIRST, FRONTIER NAMES AT THE TOP, which is how the cloth ladder is built: recognisable
anchors most of the way up (Mithril, Truesilver, Thorium, Dark Iron, Adamantite, Titanium...) and
Frontier's own inventions past the point the real ladder stops.

NOTHING NEW GOES INTO A NODE POOL. These tiers are for levels 41-60, and the highest-level creature
in the game is 40, so adding them to a zone's gathering table would put endgame ore in a level-30
zone. They go in the files, with their smelting and plank recipes, and wait - exactly as cloth's own
tiers 11-40 already do. Placing a few of the lower new ones (Gold, Mithril, Truesilver, Thorium) in
the existing level 32-40 zones is a separate decision, and it is the one that would actually give
blacksmithing a material ladder up to skill 200 today.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (ore id stem, display name, description). Order is the ladder.
NEW_ORE = [
    ("gold", "Gold Ore", "Soft, heavy and worth more melted than swung."),
    ("mithril", "Mithril Ore", "Light for its strength. Smiths talk about it the way cooks talk about salt."),
    ("truesilver", "Truesilver Ore", "Holds an edge and will not tarnish. Expensive for both reasons."),
    ("thorium", "Thorium Ore", "Takes a brutal heat to work and pays it back."),
    ("dark_iron", "Dark Iron Ore", "Drinks heat instead of taking it. A normal forge will not touch it."),
    ("fel_iron", "Fel Iron Ore", "Green in the seam. Nobody has agreed on whether that matters."),
    ("adamantite", "Adamantite Ore", "Barely yields. What comes out of it barely bends."),
    ("khorium", "Khorium Ore", "Rare enough that finding a seam is a story people tell."),
    ("cobalt", "Cobalt Ore", "Blue through the break, and tougher than it looks."),
    ("saronite", "Saronite Ore", "Cold to hold. Miners work it in short shifts."),
    ("titanium", "Titanium Ore", "The kind of metal a bridge is made of, if you could afford it."),
    ("obsidium", "Obsidium Ore", "Black glass with iron in it. Cuts the hands that mine it."),
    ("elementium", "Elementium Ore", "Will not sit still in the crucible."),
    ("pyrite", "Pyrite Ore", "Looks like gold to everybody except a smith."),
    ("ghost_iron", "Ghost Iron Ore", "Grey and quiet and a great deal harder than grey and quiet suggests."),
    ("kyparite", "Kyparite Ore", "Splits along lines nobody can predict."),
    ("trillium", "Trillium Ore", "Three seams twisted together. Separating them is the work."),
    ("blackrock", "Blackrock Ore", "Comes out of the deepest heat and remembers it."),
    ("felslate", "Felslate", "Flakes like slate and holds an edge like steel."),
    ("empyrium", "Empyrium Ore", "Found high up, where there is no reason for ore to be."),
    ("storm_silver", "Storm Silver Ore", "Hums faintly. Nobody leaves it near a compass."),
    ("osmenite", "Osmenite Ore", "Dense past the point of sense. A single bar is a day's carry."),
    ("phaedrite", "Phaedrite Ore", "Veined with something that catches the lamp and holds it."),
    ("serevite", "Serevite Ore", "Common where it occurs and it occurs almost nowhere."),
    ("draconium", "Draconium Ore", "Warm in the hand. Smiths have stopped asking why."),
    ("riftstone", "Riftstone Ore", "Came through with everything else and does not belong to either world."),
    ("voidiron", "Voidiron Ore", "Takes no shine at all, at any angle, under any light."),
    ("sunforged", "Sunforged Ore", "Already tempered by something before anyone dug it up."),
    ("glacium", "Glacium Ore", "Will not warm. A bar of it frosts the anvil."),
    ("emberite", "Emberite Ore", "Still holds a coal's worth of heat days out of the ground."),
    ("starmetal", "Starmetal Ore", "Fell, rather than formed. The seam is a crater."),
    ("dreamsteel", "Dreamsteel Ore", "Smiths disagree about what it looked like the day before."),
    ("worldcore", "Worldcore Ore", "From deep enough that nobody has agreed which world."),
]

#: (wood id stem, display name, description).
NEW_WOOD = [
    ("silverleaf_bough", "Silverleaf Bough", "Pale wood off a pale tree. Takes a finish beautifully."),
    ("yewheart", "Yewheart Log", "Springy and patient. Every bowyer's first real wood."),
    ("thornwood", "Thornwood Log", "Has to be stripped before it can be worked, carefully."),
    ("bloodbark", "Bloodbark Log", "Red through the grain. The sap stains and the stain stays."),
    ("duskwillow", "Duskwillow Log", "Bends further than it should before it goes."),
    ("felwood", "Felwood Log", "Grew wrong somewhere and the wrongness is in the grain."),
    ("moonwood", "Moonwood Log", "Cut at night, by people who insist it matters."),
    ("vinewood", "Vinewood Coil", "Not one tree so much as a knot of several."),
    ("ghostwood", "Ghostwood Log", "Light as paper and will not break."),
    ("emberoak", "Emberoak Log", "Burns slowly and reluctantly, which is why it is valued."),
    ("glacierpine", "Glacierpine Log", "Grew under ice. The rings are almost too close to count."),
    ("shadowbark", "Shadowbark Log", "Dark enough that a joint in it is invisible."),
    ("ironroot", "Ironroot Log", "The root, not the trunk. Harder than the trunk."),
    ("petrified_heartwood", "Petrified Heartwood", "Stone that still shows the grain it had."),
    ("stormwood", "Stormwood Log", "Struck and survived. The scar runs the whole length."),
    ("sunbark", "Sunbark Log", "Warm to the touch on the shaded side."),
    ("voidwillow", "Voidwillow Log", "Hangs in a direction the wind is not going."),
    ("dreamwood", "Dreamwood Log", "Carvers report finishing work they do not remember starting."),
    ("wyrmwood", "Wyrmwood Log", "Something large slept against this trunk for a long time."),
    ("runebark", "Runebark Log", "Markings in the bark that are not writing and are not random."),
    ("starwood", "Starwood Log", "Flecked through with something that catches light from inside."),
    ("soulbark", "Soulbark Log", "Warm, and the warmth does not come from the sun."),
    ("titanbark", "Titanbark Log", "One ring is a century. The log is a section of one ring."),
    ("phoenixwood", "Phoenixwood Log", "Regrows from the stump within a season, every time."),
    ("abyssal_root", "Abyssal Root", "Pulled from deeper than any tree has business reaching."),
    ("chronowood", "Chronowood Log", "Older at one end than the other, measurably."),
    ("spiritbark", "Spiritbark Log", "Carvers work it in silence. They do not explain why."),
    ("nightmare_bough", "Nightmare Bough", "Nobody sleeps near the woodpile."),
    ("lightwood", "Lightwood Log", "Casts no shadow worth the name."),
    ("genesis_bough", "Genesis Bough", "Still putting out leaves, cut and stacked."),
    ("primordial_heartwood", "Primordial Heartwood", "From a tree that predates the forest around it."),
    ("worldroot", "Worldroot Log", "A root with no tree anybody has found."),
    ("everbark", "Everbark Log", "Does not season, does not warp, does not rot. Does not explain itself."),
]


def cloth_ladder(mats):
    """[(skill_range, tier, sell_price)] for the 40 cloth tiers, in ladder order."""
    cloth = [(v["skill_range"], v.get("tier"), v.get("sell_price"))
             for v in mats.values() if v.get("material_type") == "cloth" and v.get("skill_range")]
    return sorted(cloth, key=lambda c: (c[0][0], c[0][-1]))


def existing_top(mats, mtype, mine):
    """Highest skill_range[0] among the tiers that were there BEFORE this tool ran.

    It has to exclude this tool's own output or the tool is not idempotent: the first run raised
    ore's top from 50 to 378, so the second run looked for 33 cloth bands above 378, found 2, and
    failed instead of reporting that there was nothing left to add.
    """
    return max((v["skill_range"][0] for mid, v in mats.items()
                if v.get("material_type") == mtype and v.get("skill_range")
                and mid not in mine), default=0)


def main():
    apply = "--apply" in sys.argv
    mp = ROOT / "data/gathering/materials.json"
    mdoc = json.loads(mp.read_text())
    mats = mdoc["materials"]

    bands = cloth_ladder(mats)

    def bands_above(mtype, count, mine):
        """`count` cloth bands, starting at the first rung above this ladder's original top."""
        top = existing_top(mats, mtype, mine)
        higher = [b for b in bands if b[0][0] > top]
        if len(higher) < count:
            print(f"FAILED: only {len(higher)} cloth bands sit above {mtype}'s current top of "
                  f"{top}, need {count}")
            sys.exit(1)
        return higher[:count]

    ore_bands = bands_above("ore", len(NEW_ORE), {f"ore_{s_[0]}" for s_ in NEW_ORE})
    wood_bands = bands_above("wood", len(NEW_WOOD), {f"wood_{s_[0]}" for s_ in NEW_WOOD})

    added = {"ore": 0, "bar": 0, "wood": 0, "plank": 0}

    def put(mid, record):
        if mid in mats:
            return False
        mats[mid] = record
        return True

    # ------------------------------------------------------------------ ore and its bars
    for (stem, name, desc), (rng, tier, sell) in zip(NEW_ORE, ore_bands):
        if put(f"ore_{stem}", {
            "name": name, "material_type": "ore", "tier": tier, "skill_range": rng,
            "sell_price": sell, "stack_limit": 20, "profession": "mining",
            "icon_id": stem, "description": desc,
        }):
            added["ore"] += 1
        bar_name = name.replace(" Ore", " Bar") if name.endswith(" Ore") else f"{name} Bar"
        if put(f"bar_{stem}", {
            "name": bar_name, "material_type": "bar", "tier": tier,
            # A bar is worth a little more than its ore and sits one notch further up the skill
            # ladder, matching how every existing bar relates to its ore.
            "skill_range": [v + 10 for v in rng],
            "sell_price": int(sell * 1.4), "stack_limit": 20, "profession": "mining",
            "icon_id": stem, "description": f"Refined {name.replace(' Ore', '').lower()}.",
        }):
            added["bar"] += 1

    # ------------------------------------------------------------------ wood and its planks
    for (stem, name, desc), (rng, tier, sell) in zip(NEW_WOOD, wood_bands):
        if put(f"wood_{stem}", {
            "name": name, "material_type": "wood", "tier": tier, "skill_range": rng,
            "sell_price": sell, "stack_limit": 20, "profession": "woodcutting",
            "icon_id": stem, "description": desc,
        }):
            added["wood"] += 1
        plank = name.rsplit(" ", 1)[0] if name.split(" ")[-1] in ("Log", "Bough", "Coil") else name
        if put(f"plank_{stem}", {
            "name": f"{plank} Plank", "material_type": "plank", "tier": tier,
            "skill_range": [v + 10 for v in rng],
            "sell_price": int(sell * 1.4), "stack_limit": 20, "profession": "woodcutting",
            "icon_id": stem, "description": f"Cut and squared {plank.lower()}.",
        }):
            added["plank"] += 1

    # ------------------------------------------------------------------ smelting
    sp = ROOT / "data/gathering/smelting_recipes.json"
    sdoc = json.loads(sp.read_text())
    srec = sdoc.setdefault("recipes", {})
    smelt = 0
    for (stem, _n, _d), (rng, _t, _s) in zip(NEW_ORE, ore_bands):
        rid = f"bar_{stem}"
        if rid not in srec:
            srec[rid] = {"inputs": {f"ore_{stem}": 1}, "output": f"bar_{stem}",
                         "skill_required": rng[0]}
            smelt += 1

    # ------------------------------------------------------------------ planks
    rp = ROOT / "data/crafting/recipes.json"
    rdoc = json.loads(rp.read_text())
    wc = rdoc["professions"].setdefault("woodcutting", {"recipes": {}})
    wcr = wc.setdefault("recipes", {})
    planks = 0
    for (stem, name, _d), (rng, _t, _s) in zip(NEW_WOOD, wood_bands):
        rid = f"plank_{stem}"
        if rid not in wcr:
            wcr[rid] = {
                "name": mats[f"plank_{stem}"]["name"],
                "inputs": {f"wood_{stem}": 1},
                "skill_required": rng[0],
                "output": {"kind": "material", "material_id": f"plank_{stem}"},
                "source": "trainer",
            }
            planks += 1

    if apply:
        mp.write_text(json.dumps(mdoc, indent=2, ensure_ascii=False) + "\n")
        sp.write_text(json.dumps(sdoc, indent=2, ensure_ascii=False) + "\n")
        rp.write_text(json.dumps(rdoc, indent=2, ensure_ascii=False) + "\n")

    def count(t):
        return sum(1 for v in mats.values() if v.get("material_type") == t)

    print(f"added {added['ore']} ore, {added['bar']} bars, {added['wood']} wood, "
          f"{added['plank']} planks; {smelt} smelting and {planks} plank recipes")
    print(f"ladders now: ore {count('ore')}, bar {count('bar')}, wood {count('wood')}, "
          f"plank {count('plank')}  (cloth {count('cloth')}, leather {count('leather')})")
    if not apply:
        print("\n(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
