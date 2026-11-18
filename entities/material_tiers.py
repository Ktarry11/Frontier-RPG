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

#: THE LINE MOVED ON 13 NOV 2026. It used to sit at the top Classic rung (Runecloth, Rugged Leather),
#: which left 12 cloths and 9 leathers before 60 and about a hundred recipes at skill 300 or under
#: that nobody could make until 60. Kyle: "We will use roughly around 22 or so
#: herbs/leather/cloth/ore/gemstones/trees BEFORE lvl 60. As the rest of them will be basically like
#: 'Raid tiers'" - and, asked whether to move the line to skill 300: "Lets mix in some earlier tiered
#: cloth and leather, yes. We should have around 20 - 22. The crafting 300 gate will still be the
#: original wow stuff. Please move that line, yes."
#:
#: So the test is the material's own gathering skill: 300 or under is the pre-60 ladder (22 cloths,
#: 22 leathers), anything above is a raid tier and held to level 60. Read from the data, so a new
#: material lands on the right side of the line by its number and not by somebody remembering a list.
PRE_60_SKILL_CEILING = 300


def _ladder(kind):
    """[(material_id, skill)] for one material type, lowest skill first."""
    import json
    from pathlib import Path
    mats = json.loads((Path(__file__).resolve().parent.parent / "data/gathering/materials.json").read_text(encoding="utf-8"))
    mats = mats.get("materials", mats)
    return sorted(((mid, m["skill_range"][0]) for mid, m in mats.items()
                   if m.get("material_type") == kind and m.get("skill_range")), key=lambda t: (t[1], t[0]))


def pre60_ladder(kind):
    """The materials of this kind a player meets before level 60, lowest skill first."""
    return [(mid, s) for mid, s in _ladder(kind) if s <= PRE_60_SKILL_CEILING]


def pre60_bands(kind, backbone, rare=()):
    """Drop bands for levels 1-59, built from each material's skill.

    A material of skill S belongs to level S/5. It starts dropping three levels before that and
    stays for nine after, so neighbours overlap and every level has a few to roll. The Classic
    materials in `backbone` carry weight 3 - they are still what most of the 300 recipes are made
    of - and the Frontier tiers mixed in between them carry 1. Anything in `rare` is left out
    (it has its own hand-written band).
    """
    bands = []
    ladder = [(mid, max(1, round(skill / 5))) for mid, skill in pre60_ladder(kind) if mid not in rare]
    spine = [level for mid, level in ladder if mid in backbone]
    for mid, level in ladder:
        last = level + 9
        if mid in backbone:
            # a Classic material keeps dropping until the next Classic one has taken over, so the
            # recipes written for it are never starved by the tiers mixed in between
            later = [lv for lv in spine if lv > level]
            if later:
                last = max(last, later[0] + 3)
        bands.append((max(1, level - 3), min(HIGH_TIER_FLOOR - 1, last), {mid: 3 if mid in backbone else 1}))
    return bands


HIGH_TIER_CLOTH = {mid for mid, s in _ladder("cloth") if s > PRE_60_SKILL_CEILING}
HIGH_TIER_LEATHER = {mid for mid, s in _ladder("leather") if s > PRE_60_SKILL_CEILING}

HIGH_TIER = HIGH_TIER_CLOTH | HIGH_TIER_LEATHER

#: THE FIRST TOP TIERS: what level 60 gets of the endgame ladders. Kyle, 18 Nov 2026: "Only TWO of the top tier
#: crafting materials each bro. We want to keep a backup for higher tiers", "heroics can get the same 2 crafting
#: materials that We would put in the first few pure 60 zones. Do note which ones they are", and "So only take 2 from
#: the ore/cloth/leather/wood and these will be in heroics and lvl 60 zones to craft gear", then gems too.
#: The two lowest rungs above the pre-60 line, per kind:
#:     cloth    Dreamsilk (310), Chronoweave (320)        monsters in heroics
#:     leather  Manticore (310), Chimera (320)            skinning in heroics
#:     ore      Frostforged Silver (310), Sylvanite (310) heroic bosses and chests
#:     wood     Emberwood (310), Voidwood (310)           heroic bosses and chests
#:     gem      Glacier Sapphire (310), Sylvan Emerald (310)  heroic bosses and chests
#: and, when they're built, the level-60 zones' nodes and drops (Kyle: "Heroic bosses, chests and eventually the lvl 60
#: zones"). Everything above these two on each ladder is held back for higher content. docs/heroic_design.md.
FIRST_TOP_KINDS = ("cloth", "leather", "ore", "wood", "gem")
LEVEL60_TOP = {kind: [mid for mid, _s in _ladder(kind) if _s > PRE_60_SKILL_CEILING][:2] for kind in FIRST_TOP_KINDS}
HEROIC_TOP = LEVEL60_TOP
#: their weight in a pool, the first more common than the second
HEROIC_TOP_WEIGHTS = (3, 2)


def first_top_tiers():
    """Every material level-60 content is allowed from the endgame ladders: the two per kind above."""
    return {m for ms in LEVEL60_TOP.values() for m in ms}


def heroic_top(kind):
    """{material id: weight} a heroic monster adds to its level-59 pool: the two lowest top-tier rungs of `kind`."""
    return dict(zip(HEROIC_TOP.get(kind, []), HEROIC_TOP_WEIGHTS))


#: THE ZONE DECIDES, NOT THE CREATURE. Kyle, 16 Nov 2026: "this is CRITICAL that no post-game materials
#: drop and no post-game gathering nodes in zones that are NOT pure 60. So even though these zones go to
#: 60, they are not at pure 60." A level 60 elite in a 55-60 zone used to clear HIGH_TIER_FLOOR on its own
#: level. Now a roll is only allowed past the floor when the zone it happens in is PURE 60: a band of
#: exactly 60 to 60 (Kyle chose "60-60 only"). Anywhere else, and anywhere unknown, the roll is held at
#: 59, the top of the pre-60 ladder.
_ACTIVE_ZONE = None


def set_active_zone(zone_name):
    """Combat sets this before it rolls loot, so every material roll knows where it is."""
    global _ACTIVE_ZONE
    _ACTIVE_ZONE = zone_name


def is_pure_60(zone_name):
    """True only for a zone whose level band is exactly 60 to 60."""
    if not zone_name:
        return False
    from world.zone_levels import band, _load
    b = band(zone_name)
    if not b:
        # combat passes a key ("eastern_plaguelands"), the bands are keyed by display name
        key = str(zone_name).lower().replace(" ", "_").replace("'", "")
        b = next((v for k, v in _load().items() if k.lower().replace(" ", "_").replace("'", "") == key), None)
    return bool(b) and int(b[0]) >= HIGH_TIER_FLOOR and int(b[1]) >= HIGH_TIER_FLOOR


def tier_level(level, zone_name=None):
    """The level a material roll is allowed to use: the creature's own level in a pure 60 zone, and
    never more than 59 anywhere else (an unknown zone counts as anywhere else)."""
    level = int(level)
    if level < HIGH_TIER_FLOOR:
        return level
    return level if is_pure_60(zone_name if zone_name is not None else _ACTIVE_ZONE) else HIGH_TIER_FLOOR - 1


def is_postgame(material_id, materials=None):
    """True for anything that may only appear in a pure 60 zone.

    One test for every ladder, so nodes, drops and tables all ask the same question: is it above the
    pre-60 line? That line is skill 300 (PRE_60_SKILL_CEILING), where Kyle put the top of traditional
    crafting ("Go to skill 300. But keep only wow terminal stuff"), plus HIGH_TIER for cloth and leather.
    Frontier fillers between the WoW anchors and 300 (Ashen Steel, Starleaf) are pre-60 by that canon,
    whatever their tier label says; the label "endgame" is also on Thorium and Runecloth.
    """
    if material_id in HIGH_TIER:
        return True
    if materials is None:
        import json
        from pathlib import Path
        materials = json.loads((Path(__file__).resolve().parent.parent / "data/gathering/materials.json")
                               .read_text(encoding="utf-8")).get("materials", {})
    m = materials.get(material_id)
    if not m:
        return False
    return (m.get("skill_range") or [0])[0] > PRE_60_SKILL_CEILING


def in_reach(weights, level):
    """Drop weights with everything above level `level`'s tier ceiling removed.

    Returns the table unchanged at or above the floor, and strictly filtered below it - INCLUDING
    down to an empty table. The first version of this returned the unfiltered table when filtering
    emptied it, meaning to fail loudly rather than silently; what it actually did was leak. A
    level-58 humanoid sits in a band of four high tiers and nothing else, so the fallback fired and
    handed out Moonsilk. Bands that empty are normal near the boundary and the caller skips them;
    a caller left with no band at all picks its own floor material.
    """
    if tier_level(level) >= HIGH_TIER_FLOOR:
        return weights
    return {m: w for m, w in weights.items() if m not in HIGH_TIER}
