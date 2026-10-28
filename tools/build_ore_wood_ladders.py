#!/usr/bin/env python3
"""Build the ore and wood ladders out to 40 tiers, using the names the ART already uses. Idempotent.

    PYTHONPATH=. python3 tools/build_ore_wood_ladders.py [--apply]

Kyle, 2026-10-28: "The ore and wood have more, they're just not Implemented. We should have them in
the files."

THE FIRST VERSION OF THIS INVENTED THE NAMES, WHICH WAS THE WHOLE MISTAKE. assets/gathering_nodes
already holds 40 ore, 40 wood, 40 bar and 40 plank icons, drawn long ago for the full ladder - which
is exactly what "they're just not implemented" meant. Writing my own names (Khorium, Saronite,
Titanium, Thornwood, Everbark...) produced 26 ore and 33 wood tiers with no art, while 26 ore and 33
wood icons sat unreferenced in the same folder. Perfectly symmetric, entirely self-inflicted. The
tables below are read off the art, so every tier has its picture from the moment it exists.

Seven of the invented names happened to collide with real ones the art already had - Gold, Mithril,
Truesilver, Thorium, Dark Iron, Elementium, Dreamsteel - which is why the orphan count was 26 rather
than 33, and why the mismatch did not stand out.

BANDS COME FROM THE CLOTH LADDER, NOT FROM ME. Cloth already spans 40 tiers from skill 5 to 460 with
spacing somebody tuned, and three ladders drifting apart is how the skill-versus-material gap
appeared in the first place. Each new tier takes a cloth tier's skill_range and tier label wholesale,
starting from the rung above where the existing tiers stop. The seven existing tiers of each are
untouched: they are in live zones and working recipes.

NOTHING NEW GOES INTO A NODE POOL. Kyle's call: these are levels 41-60 materials, the game's highest
creature is level 40, and putting endgame ore in a level-30 zone to fix blacksmithing today would be
a worse problem than the one it solves. They sit in the files with their smelting and plank recipes
and wait, exactly as cloth's own tiers 11-40 already do.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (stem, display name, description). The stem IS the icon filename in assets/gathering_nodes/ore.
NEW_ORE = [
    ("bronze_vein", "Bronze Vein Ore", "Copper and tin grown together in the rock, already half alloyed."),
    ("living_copper", "Living Copper Ore", "The seam has moved since it was surveyed. Twice."),
    ("verdant_iron", "Verdant Iron Ore", "Green through the break, and no smith has agreed on why."),
    ("frostveined_tin", "Frostveined Tin Ore", "White lines through the grey that do not melt on the palm."),
    ("gold", "Gold Ore", "Soft, heavy and worth more melted than swung."),
    ("mithril", "Mithril Ore", "Light for its strength. Smiths talk about it the way cooks talk about salt."),
    ("truesilver", "Truesilver Ore", "Holds an edge and will not tarnish. Expensive for both reasons."),
    ("thorium", "Thorium Ore", "Takes a brutal heat to work and pays it back."),
    ("dark_iron", "Dark Iron Ore", "Drinks heat instead of taking it. A normal forge will not touch it."),
    ("felslag", "Felslag Ore", "The waste left by something that was smelting down here first."),
    ("bloodiron", "Bloodiron Ore", "Rusts the moment it is cut, in a colour rust does not come in."),
    ("deepearth", "Deepearth Ore", "Comes up warm and takes a week to stop being warm."),
    ("ashen_steel", "Ashen Steel Ore", "Already steel in the ground, which should not be possible."),
    ("frostforged_silver", "Frostforged Silver Ore", "Tempered by cold rather than heat, somewhere, by something."),
    ("sunforged_gold", "Sunforged Gold Ore", "Too bright to work by lamplight. Smiths do it at dawn."),
    ("nightshard", "Nightshard Ore", "Breaks into splinters that are hard to look directly at."),
    ("elementium", "Elementium Ore", "Will not sit still in the crucible."),
    ("voidstone", "Voidstone Ore", "Takes no shine at all, at any angle, under any light."),
    ("stormveined", "Stormveined Ore", "Hums faintly. Nobody leaves it near a compass."),
    ("sylvanite", "Sylvanite Ore", "Found tangled through roots, as though the tree put it there."),
    ("molten_coreite", "Molten Coreite Ore", "Carried in stone buckets. Nobody has tried a sack twice."),
    ("dreamsteel", "Dreamsteel Ore", "Smiths disagree about what it looked like the day before."),
    ("abyssal_iron", "Abyssal Iron Ore", "Pulled from below the level where the lamps stop helping."),
    ("ebonrend", "Ebonrend Ore", "The seam is a tear rather than a vein."),
    ("sunderedsteel", "Sunderedsteel Ore", "Shattered in the ground and healed back wrong."),
    ("starforged_iron", "Starforged Iron Ore", "Fell, rather than formed. The seam is a crater."),
    ("astral_platinum", "Astral Platinum Ore", "Weighs differently depending on the hour."),
    ("chronium", "Chronium Ore", "Older at one end of the bar than the other, measurably."),
    ("titansteel", "Titansteel Ore", "A single bar is a two-man carry and worth the second man."),
    ("wyrmscale", "Wyrmscale Ore", "Lies in overlapping plates, like something shed it."),
    ("cataclysmic", "Cataclysmic Ore", "Only found where the ground gave way during the Integration."),
    ("primordium", "Primordium Ore", "Older than the rock it is sitting in."),
    ("worldheart", "Worldheart Ore", "From deep enough that nobody has agreed which world."),
]

#: (stem, display name, description). The stem IS the icon filename in assets/gathering_nodes/wood.
#: The plank keeps the stem minus any _tree or _stump, matching the existing plank art.
NEW_WOOD = [
    ("silverbark_tree", "Silverbark Log", "Pale wood off a pale tree. Takes a finish beautifully."),
    ("goldenleaf_tree", "Goldenleaf Log", "Drops its leaves gold and keeps dropping them all year."),
    ("redbark_tree", "Redbark Log", "Red through the grain. The sap stains and the stain stays."),
    ("sapglow_stump", "Sapglow Stump", "The cut end still shows light an hour after felling."),
    ("marshwillow", "Marshwillow Log", "Waterlogged through and somehow not rotten."),
    ("duskwood_stump", "Duskwood Stump", "Dark enough that a joint in it is invisible."),
    ("nightshade_stump", "Nightshade Stump", "Has to be stripped before it can be worked, carefully."),
    ("thornveil_stump", "Thornveil Stump", "The thorns grow inward as well as out."),
    ("bloodroot_stump", "Bloodroot Stump", "The root, not the trunk. Harder than the trunk."),
    ("bloodwood_tree", "Bloodwood Log", "Warm in the hand, and the warmth does not come from the sun."),
    ("felbark_tree", "Felbark Log", "Grew wrong somewhere and the wrongness is in the grain."),
    ("moonpetal_tree", "Moonpetal Log", "Cut at night, by people who insist it matters."),
    ("emberwood_stump", "Emberwood Stump", "Burns slowly and reluctantly, which is why it is valued."),
    ("frostheart_tree", "Frostheart Log", "Grew under ice. The rings are almost too close to count."),
    ("ebonthorn_stump", "Ebonthorn Stump", "Black all the way through, thorns included."),
    ("starleaf_tree", "Starleaf Log", "Flecked through with something that catches light from inside."),
    ("stormoak_tree", "Stormoak Log", "Struck and survived. The scar runs the whole length."),
    ("sunheart_stump", "Sunheart Stump", "Warm to the touch on the shaded side."),
    ("voidwood_tree", "Voidwood Log", "Casts a shadow in the wrong direction and nobody enjoys it."),
    ("dreamwillow", "Dreamwillow Log", "Carvers report finishing work they do not remember starting."),
    ("wyrmscak_tree", "Wyrmscak Log", "Something large slept against this trunk for a long time."),
    ("astral_birch", "Astral Birch Log", "The bark peels in sheets that hold their curl."),
    ("sylvanheart_tree", "Sylvanheart Log", "Still putting out leaves, cut and stacked."),
    ("radiant_ashenwood_tree", "Radiant Ashenwood Log", "Grey, and brighter than grey has any business being."),
    ("molten_ironwood_stump", "Molten Ironwood Stump", "Hard as the name promises and twice as heavy."),
    ("abysswood_tree", "Abysswood Log", "Grew where there is no light to grow by."),
    ("chronoak_stump", "Chronoak Stump", "One ring is a century. The stump is a section of one ring."),
    ("starforged_oak", "Starforged Oak Log", "Something came down through the canopy and the tree kept going."),
    ("sunderedwood_stump", "Sunderedwood Stump", "Split to the root and grown back around the split."),
    ("cataclysm_root_stump", "Cataclysm Root Stump", "Only found where the ground moved during the Integration."),
    ("genesis_bough_tree", "Genesis Bough", "Puts out new growth on the woodpile, in the dark, in winter."),
    ("worldbranch_tree", "Worldbranch Log", "A branch with no tree anybody has found."),
    ("worldtree_heartwood_stump", "Worldtree Heartwood", "From a tree that predates the forest around it."),
]

#: Where a bar's art is not filed under its ore's stem. bronze_vein smelts into the bronze that is
#: already in the game, so it borrows that bar's icon rather than getting one of its own.
BAR_ICON = {"bronze_vein": "bronze"}

#: Suffixes the plank art drops: wood_oakheart_stump -> plank_oakheart.
PLANK_STRIP = ("_tree", "_stump")


def plank_stem(stem):
    for suffix in PLANK_STRIP:
        if stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def cloth_ladder(mats):
    """[(skill_range, tier, sell_price)] for the 40 cloth tiers, in ladder order."""
    cloth = [(v["skill_range"], v.get("tier"), v.get("sell_price"))
             for v in mats.values() if v.get("material_type") == "cloth" and v.get("skill_range")]
    return sorted(cloth, key=lambda c: (c[0][0], c[0][-1]))


def main():
    apply = "--apply" in sys.argv
    mp = ROOT / "data/gathering/materials.json"
    sp = ROOT / "data/gathering/smelting_recipes.json"
    rp = ROOT / "data/crafting/recipes.json"
    mdoc = json.loads(mp.read_text())
    mats = mdoc["materials"]
    sdoc = json.loads(sp.read_text())
    rdoc = json.loads(rp.read_text())

    # ---- every stem must have its art, or this is the same bug again
    art_missing = []
    for stem, _n, _d in NEW_ORE:
        if not (ROOT / f"assets/gathering_nodes/ore/{stem}.png").exists():
            art_missing.append(f"ore/{stem}")
        bar_icon = BAR_ICON.get(stem, stem)
        if not (ROOT / f"assets/gathering_nodes/bars/{bar_icon}.png").exists():
            art_missing.append(f"bars/{bar_icon}")
    for stem, _n, _d in NEW_WOOD:
        if not (ROOT / f"assets/gathering_nodes/wood/{stem}.png").exists():
            art_missing.append(f"wood/{stem}")
        ps = plank_stem(stem)
        if not (ROOT / f"assets/gathering_nodes/planks/plank_{ps}.png").exists():
            art_missing.append(f"planks/plank_{ps}")
    if art_missing:
        print(f"FAILED: {len(art_missing)} tiers would have no icon - fix the table, not the check:")
        for a in art_missing:
            print(f"  - {a}")
        return 1

    # ---- clear out anything an earlier run of this tool invented
    keep_ore = {s for s, _n, _d in NEW_ORE}
    keep_wood = {s for s, _n, _d in NEW_WOOD}
    original = {"ore_weakstone", "ore_copper", "ore_tin", "ore_rough_iron", "ore_coal",
                "ore_iron", "ore_silver", "wood_softpine", "wood_ashwood",
                "wood_oakheart_stump", "wood_driftwood_stump", "wood_ironbark_stump",
                "wood_frostpine", "wood_bramblewood"}
    stale = []
    for mid, v in list(mats.items()):
        t = v.get("material_type")
        if t == "ore" and mid not in original and mid[4:] not in keep_ore:
            stale.append(mid)
        elif t == "wood" and mid not in original and mid[5:] not in keep_wood:
            stale.append(mid)
        elif t == "bar" and not (ROOT / f"assets/gathering_nodes/bars/"
                                 f"{v.get('icon_id', '')}.png").exists():
            stale.append(mid)
        elif t == "plank" and not (ROOT / f"assets/gathering_nodes/planks/"
                                   f"{v.get('icon_id', '')}.png").exists():
            stale.append(mid)
    for mid in stale:
        mats.pop(mid, None)
        sdoc.get("recipes", {}).pop(mid, None)
        rdoc["professions"].get("woodcutting", {}).get("recipes", {}).pop(mid, None)

    added = {"ore": 0, "bar": 0, "wood": 0, "plank": 0, "smelt": 0, "plankrec": 0}
    bands = cloth_ladder(mats)

    def bands_above(mtype, count, mine):
        top = max((v["skill_range"][0] for mid, v in mats.items()
                   if v.get("material_type") == mtype and v.get("skill_range") and mid not in mine),
                  default=0)
        higher = [b for b in bands if b[0][0] > top]
        if len(higher) < count:
            print(f"FAILED: only {len(higher)} cloth bands sit above {mtype}'s original top of "
                  f"{top}, need {count}")
            sys.exit(1)
        return higher[:count]

    ore_bands = bands_above("ore", len(NEW_ORE), {f"ore_{s}" for s, _n, _d in NEW_ORE})
    wood_bands = bands_above("wood", len(NEW_WOOD), {f"wood_{s}" for s, _n, _d in NEW_WOOD})

    def put(mid, record, key):
        if mid in mats:
            return
        mats[mid] = record
        added[key] += 1

    for (stem, name, desc), (rng, tier, sell) in zip(NEW_ORE, ore_bands):
        put(f"ore_{stem}", {
            "name": name, "material_type": "ore", "tier": tier, "skill_range": rng,
            "sell_price": sell, "stack_limit": 20, "profession": "mining",
            "icon_id": stem, "description": desc,
        }, "ore")
        bar_icon = BAR_ICON.get(stem, stem)
        put(f"bar_{stem}", {
            "name": name.replace(" Ore", " Bar") if name.endswith(" Ore") else f"{name} Bar",
            "material_type": "bar", "tier": tier,
            "skill_range": [v + 10 for v in rng],
            "sell_price": int(sell * 1.4), "stack_limit": 20, "profession": "mining",
            "icon_id": bar_icon,
            "description": f"Refined {name.replace(' Ore', '').lower()}.",
        }, "bar")
        rid = f"bar_{stem}"
        if rid not in sdoc.setdefault("recipes", {}):
            sdoc["recipes"][rid] = {"inputs": {f"ore_{stem}": 1}, "output": rid,
                                    "skill_required": rng[0]}
            added["smelt"] += 1

    wc = rdoc["professions"].setdefault("woodcutting", {"recipes": {}}).setdefault("recipes", {})
    for (stem, name, desc), (rng, tier, sell) in zip(NEW_WOOD, wood_bands):
        put(f"wood_{stem}", {
            "name": name, "material_type": "wood", "tier": tier, "skill_range": rng,
            "sell_price": sell, "stack_limit": 20, "profession": "woodcutting",
            "icon_id": stem, "description": desc,
        }, "wood")
        ps = plank_stem(stem)
        base = name.rsplit(" ", 1)[0] if name.rsplit(" ", 1)[-1] in ("Log", "Stump") else name
        put(f"plank_{ps}", {
            "name": f"{base} Plank", "material_type": "plank", "tier": tier,
            "skill_range": [v + 10 for v in rng],
            "sell_price": int(sell * 1.4), "stack_limit": 20, "profession": "woodcutting",
            "icon_id": f"plank_{ps}",
            "description": f"Cut and squared {base.lower()}.",
        }, "plank")
        if f"plank_{ps}" not in wc:
            wc[f"plank_{ps}"] = {
                "name": mats[f"plank_{ps}"]["name"],
                "inputs": {f"wood_{stem}": 1},
                "skill_required": rng[0],
                "output": {"kind": "material", "material_id": f"plank_{ps}"},
                "source": "trainer",
            }
            added["plankrec"] += 1

    if apply:
        mp.write_text(json.dumps(mdoc, indent=2, ensure_ascii=False) + "\n")
        sp.write_text(json.dumps(sdoc, indent=2, ensure_ascii=False) + "\n")
        rp.write_text(json.dumps(rdoc, indent=2, ensure_ascii=False) + "\n")

    def count(t):
        return sum(1 for v in mats.values() if v.get("material_type") == t)

    if stale:
        print(f"removed {len(stale)} tiers an earlier run invented with no art: "
              f"{', '.join(sorted(stale)[:6])}...")
    print(f"added {added['ore']} ore, {added['bar']} bars, {added['wood']} wood, "
          f"{added['plank']} planks, {added['smelt']} smelting and {added['plankrec']} plank recipes")
    print(f"ladders now: ore {count('ore')}, bar {count('bar')}, wood {count('wood')}, "
          f"plank {count('plank')}  (cloth {count('cloth')}, leather {count('leather')})")
    if not apply:
        print("\n(dry run - pass --apply to write)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
