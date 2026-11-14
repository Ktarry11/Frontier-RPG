"""Gemstones: 50 of them, each found in a particular ore vein.

Kyle, 12 Nov: "we get crystals from ore! ... Start adding gemstones and crystals to ore (think
of wow!)" and "give me a list of 50 crystal icons (I want original ones and also frontier
level ones! This will be for jewel crafting)."

In WoW a copper vein sometimes gives up a Malachite or a Tigerseye, a mithril vein a Citrine
or a Star Ruby, thorium an Arcane Crystal. Same here: every one of the 40 ores has gems of
its own, at a few percent a swing, and the better the vein the better the stone.

This writes the 50 gems into data/gathering/materials.json (material_type "gem") and the
drop table into data/gathering/gem_drops.json. Safe to re-run: it replaces its own entries.

Each gem is (id, name, source ore, chance, colour/shape for the art, description).
The first 20 are the classic real-world stones; the last 30 are Frontier's own, one for each
of the higher ores.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
MATS = ROOT / "data/gathering/materials.json"
DROPS = ROOT / "data/gathering/gem_drops.json"

#: Sell price: the skill curve an ore uses, times this. A gem is rare and small.
GEM_WEIGHT = 6.0

GEMS = [
    # --- classic stones ---------------------------------------------------------------------
    ("gem_malachite", "Malachite", "ore_copper", 0.05, "banded green", "A soft green stone with darker bands running through it. The first gem most miners ever find."),
    ("gem_tigerseye", "Tigerseye", "ore_copper", 0.03, "golden brown with a moving band of light", "Brown and gold, with a line of light that slides across it as you turn it."),
    ("gem_rock_crystal", "Rock Crystal", "ore_weakstone", 0.04, "clear, six-sided point", "A clear six-sided point, worth little, but it takes a clean edge."),
    ("gem_bloodstone", "Bloodstone", "ore_rough_iron", 0.04, "dark green flecked with red", "Dark green, spotted red as if something bled on it and it never washed off."),
    ("gem_moss_agate", "Moss Agate", "ore_tin", 0.04, "milky stone with green fern-like growths inside", "A cloudy stone with what looks like moss growing inside it. It is not moss."),
    ("gem_shadowgem", "Shadowgem", "ore_tin", 0.03, "smoky violet-black", "Smoke-dark and faintly violet. Jewellers like it; lamps do not seem to light it."),
    ("gem_lesser_moonstone", "Lesser Moonstone", "ore_silver", 0.05, "pale blue-white with a soft inner glow", "Pale as milk with a blue light somewhere inside it that is never quite where you look."),
    ("gem_carnelian", "Carnelian", "ore_bronze_vein", 0.04, "warm orange-red, waxy", "A warm orange-red stone, smooth as wax."),
    ("gem_jet", "Jet", "ore_coal", 0.05, "matte black, light as wood", "Black, light in the hand, and warm to the touch. Coal that took its time."),
    ("gem_honey_amber", "Honey Amber", "ore_living_copper", 0.04, "translucent golden amber with a leaf trapped inside", "Gold and clear, with something small and green caught in it."),
    ("gem_jade", "Jade", "ore_iron", 0.04, "deep even green, polished", "Even green all the way through, cool, and heavier than it looks."),
    ("gem_citrine", "Citrine", "ore_iron", 0.03, "clear lemon yellow, faceted", "Clear yellow, the colour of weak tea held up to a window."),
    ("gem_rime_opal", "Rime Opal", "ore_frostveined_tin", 0.04, "white opal with blue frost fractures", "White, with frost-blue cracks that never spread and never close."),
    ("gem_topaz", "Topaz", "ore_gold", 0.05, "rich golden yellow, sharp facets", "Golden, hard, and cut by nature into something close to a jewel already."),
    ("gem_peridot", "Verdant Peridot", "ore_verdant_iron", 0.04, "bright olive green, glassy", "Bright olive green. Found where iron has been lying under old forest."),
    ("gem_aquamarine", "Aquamarine", "ore_mithril", 0.04, "pale sea blue, long crystal", "Pale sea-blue and long in the crystal. Sailors pay over the odds for it."),
    ("gem_star_ruby", "Star Ruby", "ore_mithril", 0.02, "deep red with a six-rayed star of light", "Deep red, with a six-pointed star that sits on its surface under any light."),
    ("gem_blue_sapphire", "Blue Sapphire", "ore_thorium", 0.03, "deep royal blue, faceted", "A blue so deep it looks black until the light gets behind it."),
    ("gem_large_opal", "Large Opal", "ore_thorium", 0.03, "white with shifting flecks of every colour", "White, and full of small fires in every colour that move when you do."),
    ("gem_huge_emerald", "Huge Emerald", "ore_truesilver", 0.03, "large vivid green, rectangular cut", "Too big to be real, and real. Vivid green and flawed in the way all true ones are."),
    # --- Frontier's own --------------------------------------------------------------------
    ("gem_felfire_shard", "Felfire Shard", "ore_felslag", 0.04, "jagged sickly green shard with a yellow core, glowing", "A splinter of green fire that set hard. It is warm, and it should not be."),
    ("gem_heartsblood_garnet", "Heartsblood Garnet", "ore_bloodiron", 0.04, "dark blood-red, rounded like a drop", "Dark red and round as a drop. Miners will not put one in a pocket over the heart."),
    ("gem_deepearth_geode", "Deepearth Geode", "ore_deepearth", 0.04, "split grey stone with purple crystals inside", "A dull grey lump that splits to show a hollow lined with violet teeth."),
    ("gem_black_diamond", "Black Diamond", "ore_dark_iron", 0.03, "opaque black diamond with red glints", "A diamond that swallowed the forge it grew beside. Black, with a red spark deep in."),
    ("gem_truesilver_zircon", "Moonsilver Zircon", "ore_truesilver", 0.02, "colourless brilliant with a silver sheen", "Colourless and brighter than glass has any right to be."),
    ("gem_cinder_agate", "Cinder Agate", "ore_ashen_steel", 0.04, "grey agate banded with glowing orange", "Grey bands and orange bands, and the orange ones are still faintly alight."),
    ("gem_elementium_prism", "Elementium Prism", "ore_elementium", 0.04, "four-coloured prism: red, blue, green, white", "A prism in four colours that will not mix: flame, water, leaf and cloud."),
    ("gem_glacier_sapphire", "Glacier Sapphire", "ore_frostforged_silver", 0.04, "ice-blue sapphire, frosted at the edges", "Ice blue. It fogs when you breathe on it and takes a long time to clear."),
    ("gem_sylvan_emerald", "Sylvan Emerald", "ore_sylvanite", 0.04, "leaf-green emerald with gold veins", "Green shot through with fine gold, like a leaf with the sun behind it."),
    ("gem_magma_ruby", "Magma Ruby", "ore_molten_coreite", 0.04, "molten red-orange, light moving inside", "Red going to orange, and something moves in it as slow as cooling rock."),
    ("gem_sunstone", "Sunstone", "ore_sunforged_gold", 0.04, "radiant gold-orange, rays inside", "Gold and orange, with rays in it. It casts a shadow of its own at noon."),
    ("gem_nightshard_onyx", "Nightshard Onyx", "ore_nightshard", 0.04, "black onyx splinter with a thin violet edge", "A black splinter edged in violet. It is always the last thing in the room you see."),
    ("gem_abyssal_pearlstone", "Abyssal Pearlstone", "ore_abyssal_iron", 0.04, "dark teal sphere with a pearl sheen", "A dark teal bead with a pearl's sheen, grown where no oyster ever was."),
    ("gem_void_amethyst", "Void Amethyst", "ore_voidstone", 0.04, "deep purple with a black hollow at the centre", "Deep purple round a centre that is not a colour at all."),
    ("gem_stormglass", "Stormglass", "ore_stormveined", 0.04, "clear crystal with a lightning fork frozen inside", "Clear, with a fork of lightning caught in the middle of striking."),
    ("gem_ebon_spinel", "Ebon Spinel", "ore_ebonrend", 0.04, "black octahedron with crimson reflections", "A black eight-sided stone that throws back crimson from any light."),
    ("gem_sundered_tourmaline", "Sundered Tourmaline", "ore_sunderedsteel", 0.04, "pink and green crystal split by a clean crack", "Half pink, half green, and cracked clean along the line between."),
    ("gem_starfall_diamond", "Starfall Diamond", "ore_starforged_iron", 0.03, "white diamond with pinpoint stars inside", "A white diamond with points of light in it that are in the right places for the sky."),
    ("gem_astral_moonstone", "Astral Moonstone", "ore_astral_platinum", 0.03, "silver-blue cabochon with a crescent of light", "Silver-blue, with a crescent of light that waxes and wanes with the month."),
    ("gem_hourglass_topaz", "Hourglass Topaz", "ore_chronium", 0.03, "amber topaz with a pinched hourglass shape inside", "Amber, with a shape like an hourglass in it. The sand in it runs upward."),
    ("gem_titans_eye", "Titan's Eye", "ore_titansteel", 0.03, "large steel-blue orb with a golden ring iris", "Steel blue with a ring of gold round a dark centre. It does not blink first."),
    ("gem_wyrmheart_ruby", "Wyrmheart Ruby", "ore_wyrmscale", 0.03, "scaled-texture crimson ruby, ember core", "Crimson, faceted like scales, and warm enough to keep a hand from stiffening."),
    ("gem_cataclysm_opal", "Cataclysm Opal", "ore_cataclysmic", 0.03, "black opal with red and orange fissures", "Black, split by fissures of red and orange that are wider than they were yesterday."),
    ("gem_dreamers_jade", "Dreamer's Jade", "ore_dreamsteel", 0.03, "misty green jade, soft glow, drifting motes", "Misty green. People who carry one report sleeping well and remembering nothing."),
    ("gem_primordial_amber", "Primordial Amber", "ore_primordium", 0.03, "deep amber with a spiral shell inside", "Old amber with a coiled thing in it that has no living relatives."),
    ("gem_worldheart_crystal", "Worldheart Crystal", "ore_worldheart", 0.02, "radiant multi-faceted crystal, green and gold, pulsing", "Green and gold, and it beats. Slowly. About once for every twenty of yours."),
    # --- rare extras ------------------------------------------------------------------------
    ("gem_fire_opal", "Fire Opal", "ore_bloodiron", 0.02, "orange-red opal with inner flame", "Orange and red, lit from inside like a coal seen through a curtain."),
    ("gem_azure_diamond", "Skyglass Diamond", "ore_thorium", 0.015, "flawless pale blue diamond", "Flawless and faintly blue. The stone every apprentice is told they will never cut."),
    ("gem_pyrite_star", "Fool's Star", "ore_gold", 0.02, "brassy pyrite cluster of cubes", "A cluster of brassy cubes. Not gold. Jewellers buy it anyway, for the shapes."),
    ("gem_prismatic_shard", "Prismatic Shard", "ore_elementium", 0.015, "long shard splitting light into a rainbow", "A long shard that breaks any light into every colour and hands them back in order."),
]


def main():
    from reprice_materials import curve
    raw = MATS.read_text(encoding="utf-8")
    data = json.loads(raw)
    mats = data.get("materials", data)
    assert len(GEMS) == 50 and len({g[0] for g in GEMS}) == 50, len(GEMS)
    for gid in [k for k, v in mats.items() if v.get("material_type") == "gem"]:
        del mats[gid]
    drops = {}
    for gid, name, ore, chance, _art, desc in GEMS:
        src = mats.get(ore)
        assert src is not None and src["material_type"] == "ore", f"{gid}: no ore {ore}"
        skill = src["skill_range"][0]
        mats[gid] = {
            "name": name, "material_type": "gem", "profession": "mining", "tier": src["tier"],
            "description": desc + f" Found in {src['name'].replace(' Ore', '')} veins.",
            "stack_limit": 20, "sell_price": max(25, int(round(curve(skill, "ore") * GEM_WEIGHT))),
            "icon_id": gid[4:], "skill_range": list(src["skill_range"]),
        }
        drops.setdefault(ore, []).append([gid, chance])
    style = next(((i, asc) for i in (2, 4, 1, None) for asc in (True, False)
                  if json.dumps(json.loads(raw), indent=i, ensure_ascii=asc) == raw.rstrip("\n")), (2, True))
    MATS.write_text(json.dumps(data, indent=style[0], ensure_ascii=style[1]) + ("\n" if raw.endswith("\n") else ""), encoding="utf-8")
    DROPS.write_text(json.dumps({
        "_doc": "ore material id -> [[gem id, chance per gather], ...]. Built by tools/build_gems.py. "
                "Each gem rolls on its own, in order; a vein gives at most one gem per swing.",
        "drops": drops}, indent=2) + "\n", encoding="utf-8")
    missing = [k for k, v in mats.items() if v.get("material_type") == "ore" and k not in drops]
    print(f"{len(GEMS)} gems across {len(drops)} ores; ores with no gem: {missing}")


if __name__ == "__main__":
    main()
