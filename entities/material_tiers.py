"""One rule, in one place: high-tier material never appears before level 60.

Kyle, 2026-10-28: "we can have frontier stuff in there. That is 100% fine. But none of the high-tier
stuff will EVER appear before lvl 60!"

THE LINE IS TIER HEIGHT, NOT WHERE THE NAME CAME FROM. An earlier pass got this wrong and held back
four Frontier-invented cloths (Spidersilk, Dusk Velvet, Gossamer, Thistledown) purely for being
Frontier's own. They are mid-ladder fillers slotted between Silk and Mageweave, they drop from level
25-42, and they belong exactly where they are. Origin is not the test. The test is: does this material
sit ABOVE the last rung of the real ladder?

So the boundary is drawn per ladder, at the top Classic rung:

    cloth    -> Runecloth   (Felcloth is a zone-locked side-grade at the same height, not above it)
    leather  -> Rugged Leather
    ore      -> Thorium

Everything above that rung is the endgame ladder, authored years before the zones that will hold it.
Those tiers are FILTERED OUT of any drop roll below level 60 - not deleted, not renumbered. The bands
in each drop module stay as written, because they are the real design; the floor just refuses to serve
them early. When content for 60+ lands, the bands are already correct and nothing here needs touching.

WHAT IS DELIBERATELY NOT HERE. Weakstone, Rough Iron and Coal are Frontier ore BELOW copper - filler at
the bottom of the ladder, not the top - so no ore is listed. Meat has one ladder of five tiers, all of
it in reach, so meat_drops needs no floor.
"""

#: No material listed below may be rolled under this level.
HIGH_TIER_FLOOR = 60

#: Cloth above Runecloth. Felcloth is NOT here: it is Classic's level-53 zone-locked drop, the same
#: height as Runecloth rather than above it, and holding it to 60 would break a real Classic behaviour.
HIGH_TIER_CLOTH = {
    "cloth_netherweave", "cloth_frostweave", "cloth_emberweave", "cloth_moonsilk",
    "cloth_shadowsilk", "cloth_bloodsilk", "cloth_starweave", "cloth_soulcloth",
    "cloth_imperial_silk", "cloth_windwool", "cloth_sunthread", "cloth_voidweave",
    "cloth_dreamsilk", "cloth_abyssal_velvet", "cloth_chronoweave", "cloth_stormweave",
    "cloth_lightwoven", "cloth_phoenix_cloth", "cloth_wyrmsilk", "cloth_arcanoweave",
    "cloth_titanweave", "cloth_nightmare_lace", "cloth_spiritwoven", "cloth_genesis_cloth",
    "cloth_ghostgauze", "cloth_primordial_weave", "cloth_starsilk", "cloth_worldweave",
}

#: Leather above Rugged.
HIGH_TIER_LEATHER = {
    "leather_dredged", "leather_fiendish", "leather_pristine", "leather_savage",
    "leather_frostscale", "leather_emberscale", "leather_wyvern", "leather_duskfang",
    "leather_mossback", "leather_basilisk", "leather_bloodtanned", "leather_hydra",
    "leather_netherdrake", "leather_behemoth", "leather_frostwyrm", "leather_manticore",
    "leather_chimera", "leather_phoenix", "leather_kraken", "leather_lavahound",
    "leather_nightsaber", "leather_thunderlizard", "leather_dreamstag", "leather_sandwurm",
    "leather_voidstalker", "leather_chronodrake", "leather_sunhawk", "leather_abyssal",
    "leather_genesis", "leather_primordial", "leather_worldserpent",
}

HIGH_TIER = HIGH_TIER_CLOTH | HIGH_TIER_LEATHER


def in_reach(weights, level):
    """Drop weights with everything above level `level`'s tier ceiling removed.

    Returns the table unchanged at or above the floor, and strictly filtered below it - INCLUDING
    down to an empty table. The first version of this returned the unfiltered table when filtering
    emptied it, meaning to fail loudly rather than silently; what it actually did was leak. A
    level-58 humanoid sits in a band of four high tiers and nothing else, so the fallback fired and
    handed out Moonsilk. Bands that empty are normal near the boundary and the caller skips them;
    a caller left with no band at all picks its own floor material.
    """
    if level >= HIGH_TIER_FLOOR:
        return weights
    return {m: w for m, w in weights.items() if m not in HIGH_TIER}
