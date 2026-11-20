#!/usr/bin/env python3
"""Writes docs/sky_art_prompts.md: the sky's art stock (stage 2 of the World Tree, docs/worldtree_brief.md).

    python3 tools/write_sky_art_prompts.py

Kyle, 19 Nov 2026: "Lets build up a stock of tiles and props for these future zones since chatgpt works best in massive
batches", after "i want the sky islands to be beyond gorgeous!" and the idea (for after) of a sky starting zone, 1 to
24, for a playable sky race. So the stock covers the 48-60 sky zones AND a low-level start's meadows, farms and critters.

Every sheet shares one rule block per kind (tiles, props, buildings, landmarks, creatures), so the prompts can't drift
apart, and each sheet's slice table comes from the same rows as its prompt.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "docs/sky_art_prompts.md"

SKY = ("THE SKY above Azeroth: a whole world above the clouds that nobody on the ground knew existed, continents and "
       "islands of floating stone and solid cloud adrift on an endless sea of cloud under a huge bright sun. Three peoples "
       "live there. The AETHERIANS: tall, imposing humanoids with pale blue-grey or bronze skin, luminous eyes and natural "
       "crystal growths along their bodies; ancient floating cities of titan-scale pale stone and bronze, enormous "
       "sky-forges and crystal-powered engines, magitech and gravity manipulation; titan architecture mixed with gnomish "
       "engineering but much grander; highly structured, scholarly, imperial. The VEYR: avian humanoids with feathered "
       "arms, powerful talons and hooked beaks; cities carved into impossibly high stone spires and built across enormous "
       "natural arches; wind machinery, lightning batteries and storm-forged weapons; clan-based, honour-driven, "
       "militaristic and predatory. The KHARAD: cloud giants, broad and huge, with stone-like skin, cloud-white hair and "
       "mineral growths; massive floating citadels, suspended bridges and enormous temples; gravity stones and ancient "
       "elemental machinery; a civilization older than any kingdom on the ground. Their world is dying: its crystal "
       "engines are failing and its islands are breaking apart and falling. Above everything else this art must be "
       "BREATHTAKING: luminous, airy, full of light and depth, beautiful.")

STYLE = ("Painterly semi-realistic WoW Classic style: strong readable silhouette, soft dark outline, chunky simple "
         "shapes legible at small size, consistent soft lighting from the top-left.")

HEAD = {
    "tiles": ("Generate ONE texture sheet image, {W}x{H}, laid out as a strict {C} columns x {R} rows grid = {N} separate "
              "seamless ground, water and wall textures, each cell exactly 256x256. Each cell is COMPLETELY FILLED by "
              "its texture, edge to edge, touching its neighbours with no gap. No border, no background colour, no "
              "magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. Every texture must TILE "
              "SEAMLESSLY with itself on all four sides: no single large feature that would obviously repeat, no "
              "emblem, rune or pattern repeated in every tile, no lighting gradient across the cell, flat even "
              "illumination, no vignette, no baked shadows, no objects or props standing on the ground. Straight "
              "top-down view, no perspective. Nothing built by people from our world.\n\n"
              "Match the attached reference tiles EXACTLY in style, scale of detail and level of saturation: they are "
              "from the same set. Painterly semi-realistic WoW Classic ground texture style, rich and luminous but not "
              "neon, readable at small size, not too busy."),
    "props": ("Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each cell "
              "about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single object, "
              "centred in its own cell with a wide margin, not touching or overlapping its neighbours or the image "
              "edge. No ground, no grass patch, no dirt patch, no water puddle under it unless the prompt puts the "
              "water inside the object itself, no cast shadow, no glow halo bleeding onto the background, no people, "
              "no creatures, no text, no labels, no numbers, no grid lines, no frames, no borders. Never use magenta "
              "or pink anywhere on the objects themselves (flowers are white, gold, pale blue or lavender, never "
              "pink).\n\nMatch the attached references EXACTLY in style, camera angle, outline and level of detail: "
              "they are from the same set. " + STYLE + "\n\nCamera: isometric three-quarter view elevated about 45 "
              "degrees. EVERY object is turned the same way, front face toward the lower-right. Things that grow "
              "stand upright with their base at the bottom of the cell; things that float hover with a little space "
              "under them. Consistency of angle across all 36 is critical."),
    "buildings": ("Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate sprites, each "
                  "cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each sprite is ONE single "
                  "building or object, centred in its own cell with a wide margin, not touching or overlapping its "
                  "neighbours or the image edge. No ground, no grass patch, no dirt patch, no water under it unless "
                  "the prompt puts the water inside the object itself, no cast shadow, no glow halo bleeding onto the "
                  "background, no people, no animals, no text, no labels, no numbers, no grid lines, no frames, no "
                  "borders. Never use magenta or pink anywhere on the buildings themselves.\n\nMatch the attached "
                  "references EXACTLY in style, camera angle, palette, outline and level of detail. " + STYLE +
                  " Grand and beautiful.\n\nCamera: isometric three-quarter view elevated about 45 degrees. EVERY "
                  "building and object is turned the same way, front face toward the lower-right and one side wall "
                  "toward the lower-left, so two faces of each building are visible. Doors and gates are on the front "
                  "face. Consistency of angle across all 36 is critical."),
    "landmarks": ("Generate ONE sprite sheet image, 2048x2048, a 3 columns x 3 rows grid = 9 separate landmark "
                  "sprites, each cell about 682x682. Flat pure #FF00FF magenta background everywhere. Each landmark is "
                  "ONE single structure, centred in its own cell with a wide margin, not touching or overlapping its "
                  "neighbours or the image edge. No ground plane beyond the landmark's own base, no cast shadow, no "
                  "glow halo bleeding onto the background, no people, no creatures, no text, no labels, no numbers, no "
                  "grid lines, no frames, no borders. Never use magenta or pink anywhere on the landmarks "
                  "themselves.\n\nMatch the attached references EXACTLY in style, camera angle, outline and level of "
                  "detail. " + STYLE + " These are breathtaking set pieces that fill most of their cell: make them "
                  "beautiful.\n\nCamera: isometric three-quarter view elevated about 45 degrees. EVERY landmark is "
                  "turned the same way, front face toward the lower-right. Entrances, stairs and openings are on the "
                  "front face and clearly readable as a way in or up. Consistency of angle across all 9 is critical."),
    "creatures": ("Generate ONE sprite sheet image, 2048x2048, a 6 columns x 6 rows grid = 36 separate creature "
                  "sprites, each cell about 341x341. Flat pure #FF00FF magenta background everywhere. Each creature "
                  "is ONE single figure, centred in its own cell with a wide margin, not touching or overlapping its "
                  "neighbours or the image edge. No ground, no dirt patch, no water under it, no cast shadow, no glow "
                  "halo bleeding onto the background, no text, no labels, no numbers, no grid lines, no frames, no "
                  "borders. Never use magenta or pink anywhere on the creatures themselves.\n\nMatch the attached "
                  "reference creatures EXACTLY in style, camera angle, outline and level of detail: they are from the "
                  "same set. " + STYLE + "\n\nCamera: every creature faces three-quarters toward the lower-right, full "
                  "body, feet, tail or base included and nothing cropped. Flying creatures hover with their lowest "
                  "point near the bottom of the cell. Consistency of angle across all 36 is critical."),
}
SIZE = {"tiles": ("2048x1536", "8 x 6 (256 x 256)", "**NO magenta**"),
        "props": ("2048x2048", "6 x 6 (about 341 x 341)", "magenta"),
        "buildings": ("2048x2048", "6 x 6 (about 341 x 341)", "magenta"),
        "landmarks": ("2048x2048", "3 x 3 (about 682 x 682)", "magenta"),
        "creatures": ("2048x2048", "6 x 6 (about 341 x 341)", "magenta")}
NOUN = {"tiles": "Tiles", "props": "Props", "buildings": "Sprites", "landmarks": "Landmarks", "creatures": "Creatures"}

# key, kind, title, out dir, refs, setting, scale line (or None), rows [(row title, [(text, id), ...]), ...]
SHEETS = []
#: Sheets Kyle has sent, sliced (tools/slice_tile_sheet.py sky_sk1/sky_sk2, tools/slice_building_sheet.py sky_sk3 to
#: sky_sk10; the raw sheets are tools/building_sheets/sky_sk<N>.png).
BK_LANDED = {"BK1", "BK6", "BK7", "BK8", "BK9", "BK10", "BK11", "BK12"}
LANDED = {**{f"SK{i}": "19 Nov" for i in range(1, 20)}, "SK17": "19 Nov (36 of 48: the rest is SK20)"}


def sheet(key, kind, title, out, refs, setting, scale, rows, redo_of=None):
    SHEETS.append(dict(key=key, kind=kind, title=title, out=out, refs=refs, setting=setting, scale=scale, rows=rows,
                       redo_of=redo_of))


# ===================================================================================== GROUND
sheet("SK1", "tiles", "the cloud sea, the sunlit islands and the sky meadows", "assets/tiles/sky/ground/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "assets/tiles/feralas/ground/fe_highland_meadow.png",
       "assets/tiles/feralas/ground/fe_sea_shallow.png"],
      "These are the ground of the sunlit sky: the cloud sea seen from above, the golden islands of the Sunward Crown, "
      "floating stone and sky rivers, and gentle high meadows and farms for the quieter islands. Palette: brilliant "
      "white and gold cloud, warm golden grass, fresh greens, pale warm stone, clear turquoise and deep blue water, "
      "soft blue crystal light.",
      None,
      [("THE CLOUD SEA (seen from above, looking down past the edge; unwalkable, like water)", [
          ("a bright white cloud sea in full sun, soft billows with gentle shading", "sk_cloud_sun"),
          ("the cloud sea in warm golden evening light", "sk_cloud_gold"),
          ("the cloud sea in cool blue shadow", "sk_cloud_shadow"),
          ("thin broken cloud with deep blue empty sky showing through the gaps", "sk_cloud_thin"),
          ("a storm cloud sea, dark grey-blue, lit from inside by soft lightning glow", "sk_cloud_storm"),
          ("the open sky far below the clouds, clear blue deepening to dark blue", "sk_sky_deep"),
          ("a violet dusk cloud sea, the colour of a dying sky", "sk_cloud_dusk"),
          ("SOLID WALKABLE CLOUD: dense, springy white cloud packed firm like fresh snow, soft billowy texture",
           "sk_cloud_solid")]),
       ("THE SUNWARD CROWN (golden islands)", [
          ("golden meadow grass, warm and sunlit", "sk_gold_grass"),
          ("a meadow of small gold and white wildflowers", "sk_gold_flowers"),
          ("golden forest floor of fallen gold leaves", "sk_gold_leaves"),
          ("a sun-bleached pale earth path", "sk_pale_path"),
          ("soft gold-green moss", "sk_gold_moss"),
          ("warm pale sandstone bedrock", "sk_sandstone"),
          ("lush cloud-damp clover meadow, bright green", "sk_clover"),
          ("dew-bright grass with tiny white flowers", "sk_dew_grass")]),
       ("FLOATING STONE AND SKY WATER", [
          ("the weathered pale rock top of a floating island", "sk_island_rock"),
          ("pale rock with veins of glowing blue crystal", "sk_crystal_veins"),
          ("a sky river, clear bright turquoise water flowing", "sk_river"),
          ("sky river shallows over pale round pebbles", "sk_river_shallows"),
          ("white foam water where a sky river falls", "sk_river_foam"),
          ("a still sky pool reflecting blue sky and passing clouds", "sk_sky_pool"),
          ("an ISLAND EDGE CLIFF seen straight on as a wall: layered pale rock with roots dangling from it",
           "sk_island_cliff"),
          ("the rock underside of a floating island seen straight on as a wall, hung with small blue crystals",
           "sk_island_underside")]),
       ("THE QUIET ISLANDS (high meadows, farms and orchards)", [
          ("soft bright spring grass", "sk_spring_grass"),
          ("short high turf with small stones", "sk_turf_stones"),
          ("lavender-blue heather", "sk_heather"),
          ("long wind-combed grass, silver-green", "sk_wind_grass"),
          ("a packed dirt trail", "sk_dirt_trail"),
          ("a country path of pale fitted cobbles", "sk_cobble_path"),
          ("tilled dark farm earth with faint furrows", "sk_farm_earth"),
          ("orchard grass scattered with fallen white petals", "sk_orchard_grass")]),
       ("THE ANCIENT RUINS (older than any kingdom)", [
          ("huge ancient paving slabs, pale grey, cracked, with grass in the joints", "sk_ancient_slabs"),
          ("ancient stone with faded gold inlay lines running in irregular paths, no repeating symbol",
           "sk_ancient_inlay"),
          ("a ruin floor strewn with rubble", "sk_ruin_rubble"),
          ("ancient stone swallowed by moss", "sk_ruin_moss"),
          ("ancient bronze-green metal floor plates, corroded", "sk_ancient_bronze"),
          ("ground glittering with shattered crystal glass", "sk_crystal_glass"),
          ("an ancient wall of colossal fitted blocks, seen straight on", "sk_ancient_wall"),
          ("an ancient wall of colossal blocks overgrown with vines, seen straight on", "sk_ancient_wall_vines")]),
       ("STORM, SUN AND THE CROWN", [
          ("dark storm-wet rock, shining", "sk_storm_rock"),
          ("rock scorched glassy by lightning", "sk_lightning_rock"),
          ("rain-flattened dark grass", "sk_rain_grass"),
          ("stone scattered with hailstones", "sk_hail_stone"),
          ("sun-baked white stone", "sk_white_stone"),
          ("white sand of a sky-lake beach", "sk_lake_sand"),
          ("deep blue sky-lake water", "sk_lake_deep"),
          ("the gold-lit bark of the World Tree's crown, high above the clouds", "sk_crown_bark")])])

sheet("SK2", "tiles", "the three peoples' ground and the dying sky", "assets/tiles/sky/ground/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "assets/tiles/azshara/ground/az_barnacle_marble.png", "assets/tiles/feralas/ground/fe_elven_paving.png"],
      "These are the ground of the sky's three peoples and of their dying world: the Aetherians' cities and "
      "sky-forges, the Veyr's storm-lashed spires and arches, the Kharad's colossal citadels and temples, and the "
      "Fading Firmament where the sky is coming apart. Palette: pale stone, white marble, bronze and gold with blue "
      "crystal light for the Aetherians; slate, storm blue and weathered copper for the Veyr; cloud-white marble, "
      "granite and mineral colours (amethyst violet, quartz white, gold, deep blue) for the Kharad; violet dusk, grey "
      "ash and black void for the Firmament.",
      None,
      [("THE AETHERIAN CITY", [
          ("grand pale stone paving of huge slabs with precise joints", "ae_grand_paving"),
          ("polished white marble with thin bronze seams", "ae_marble_bronze"),
          ("a bronze grate floor over a glowing blue light below", "ae_bronze_grate"),
          ("dark blue stone flecked with tiny glowing crystal", "ae_crystal_stone"),
          ("pale stone with fine gold engraved lines in irregular circuit-like paths, no repeating symbol",
           "ae_engraved_stone"),
          ("terrace garden soil with silver-blue grass", "ae_garden_soil"),
          ("sky-forge floor of scorched dark metal plates with glowing seams", "ae_forge_floor"),
          ("a walkway of crystal-glass panels with the sky visible far below through them, walkable",
           "ae_glass_walk")]),
       ("AETHERIAN WALLS, WATER AND FAILURE", [
          ("an Aetherian wall of pale stone bound with bronze bands, seen straight on", "ae_wall"),
          ("an Aetherian wall with narrow crystal-lit windows, seen straight on", "ae_wall_lit"),
          ("an arcane coolant canal, water glowing soft blue", "ae_coolant"),
          ("a still reflecting pool of pale clear water", "ae_reflecting_pool"),
          ("a gravity well: small stone fragments floating just above a dark stone base", "ae_gravity_well"),
          ("cracked pale paving with blue light leaking up through the cracks", "ae_cracked_paving"),
          ("rubble of pale stone and bronze from a fallen ring of the city", "ae_fallen_rubble"),
          ("a floor of polished bronze plates", "ae_bronze_floor")]),
       ("THE VEYR SPIRES", [
          ("spire rock: dark grey-blue slate, wind-carved", "vy_spire_rock"),
          ("slate ledges scattered with feathers and down", "vy_feather_ledge"),
          ("stone carved with sweeping talon-mark grooves, irregular", "vy_talon_stone"),
          ("storm-lit rock wet with rain, blue highlights", "vy_storm_rock"),
          ("a Veyr nest floor of woven branches and storm grass", "vy_nest_floor"),
          ("rock run through with veins of weathered copper", "vy_copper_veins"),
          ("a sheer spire face of dark rock, seen straight on", "vy_spire_wall"),
          ("a spire face carved with ledges and dark windows, seen straight on", "vy_carved_wall")]),
       ("THE VEYR AND THE STORMS", [
          ("wind-flattened silver grass", "vy_silver_grass"),
          ("stone pocked by hail", "vy_hail_stone"),
          ("gravel of crushed slate", "vy_slate_gravel"),
          ("a parade ground of packed dark earth scuffed by talons", "vy_parade_ground"),
          ("hammered copper plates gone green with weather", "vy_copper_plates"),
          ("dark rainwater pooled on stone", "vy_rain_pool"),
          ("the worn smooth rock top of a giant natural stone arch", "vy_arch_top"),
          ("ground fused to rippled glass by lightning", "vy_lightning_glass")]),
       ("THE KHARAD CITADELS", [
          ("colossal blocks of cloud-white marble", "kh_white_marble"),
          ("grey granite veined with mineral crystal (quartz white, amethyst violet, gold)", "kh_mineral_granite"),
          ("gravity-stone paving: blue-black stone with faint motes drifting up from it", "kh_gravity_paving"),
          ("temple floor of huge slabs polished smooth by ages", "kh_temple_floor"),
          ("a floor of natural mineral stones of many colours fitted together, irregular, no repeating pattern",
           "kh_mineral_mosaic"),
          ("cold pale stone touched with frost", "kh_frost_stone"),
          ("a Kharad citadel wall of giant blocks, seen straight on", "kh_citadel_wall"),
          ("a temple wall carved with weathered reliefs of giant ancestors, seen straight on", "kh_relief_wall")]),
       ("THE FADING FIRMAMENT", [
          ("stone crumbling into motes that drift upward", "ff_crumbling_stone"),
          ("dead grey grass with all the colour gone", "ff_dead_grass"),
          ("cracked ground lit violet from below, dark void showing in the cracks", "ff_void_cracks"),
          ("grey glittering ash of burnt-out crystal", "ff_crystal_ash"),
          ("dimmed crystal ground, dark blue and fading", "ff_dim_crystal"),
          ("rubble of a fallen island", "ff_island_rubble"),
          ("THE VOID below the sky (unwalkable): deep violet-black with faint stars", "ff_void"),
          ("TORN SKY (unwalkable): the cloud sea ripped open onto violet void", "ff_torn_sky")])])

# ===================================================================================== NATURE
sheet("SK3", "props", "sky nature", "assets/tiles/sky/props/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "assets/tiles/feralas/props/fe_giant_tree.png",
       "assets/tiles/feralas/props/fe_small_falls.png"],
      "These props are the living sky: golden trees, floating rocks, waterfalls that pour off the edges of islands "
      "into the cloud, crystals and flowers, plus the quiet things of a high meadow. Palette: gold and warm green "
      "leaves, white and silver bark, pale stone, turquoise water and white foam, blue and gold crystal light, white "
      "cloud.",
      "Objects keep their RELATIVE scale: the golden tree, the floating rock cluster and the edge waterfall are the "
      "largest sprites on the sheet; a flower clump, a tiny floating crystal and a grass tuft are small. Do not blow "
      "each one up to fill its own cell.",
      [("SKY TREES", [
          ("a great golden-leafed tree with a broad canopy", "sk_gold_tree"),
          ("a slender white-barked sky birch with pale gold leaves", "sk_sky_birch"),
          ("a tree with silver-blue leaves that shimmer", "sk_silver_tree"),
          ("a weeping tree hung with long strands of golden leaves", "sk_weeping_gold"),
          ("a twisted wind tree clinging to a rock, roots wrapped around it", "sk_wind_tree"),
          ("a tree whose long roots trail down off the edge into empty air", "sk_trailing_roots")]),
       ("FLOATING ROCKS", [
          ("a small floating rock topped with grass and a flower or two", "sk_float_rock"),
          ("a cluster of three floating rocks of different sizes", "sk_float_cluster"),
          ("a tiny floating crystal turning slowly", "sk_float_crystal"),
          ("a floating rock with a thin waterfall spilling off it", "sk_float_falls"),
          ("a chunk of island rock with roots dangling beneath it", "sk_root_chunk"),
          ("a tall pale rock pillar weathered by wind", "sk_rock_pillar")]),
       ("WATER AND CLOUD", [
          ("a waterfall pouring off the edge of an island down into cloud (the water falling below the lip)",
           "sk_edge_falls"),
          ("a cascade of a sky river tumbling over rocks", "sk_cascade"),
          ("a fountain of mist rising from a crack in the rock", "sk_mist_fountain"),
          ("a clump of pale sky lilies floating on water (the water inside a small rim)", "sk_sky_lilies"),
          ("a soft low bank of cloud resting on the ground, fluffy and white", "sk_cloud_bank"),
          ("a small drifting wisp of cloud", "sk_cloud_wisp")]),
       ("CRYSTALS", [
          ("a cluster of glowing blue crystals", "sk_crystal_blue"),
          ("a cluster of glowing gold crystals", "sk_crystal_gold"),
          ("a tall single crystal spire, glowing", "sk_crystal_spire"),
          ("a cracked crystal gone dim and grey", "sk_crystal_dim"),
          ("crystals grown through a mossy boulder", "sk_crystal_boulder"),
          ("a ring of small crystals around a mossy stone", "sk_crystal_ring")]),
       ("FLOWERS AND GRASSES", [
          ("tall golden sun lilies", "sk_sun_lilies"),
          ("a white skyblossom bush", "sk_skyblossom"),
          ("a tuft of silver wind grass", "sk_wind_tuft"),
          ("a patch of clover with tiny white flowers", "sk_clover_patch"),
          ("a clump of lavender-blue heather", "sk_heather_clump"),
          ("a bed of tall pale blue bellflowers", "sk_bellflowers")]),
       ("STONES AND QUIET THINGS", [
          ("a pale weathered boulder", "sk_boulder"),
          ("a mossy boulder lit gold by the sun", "sk_gold_boulder"),
          ("a small natural stone arch", "sk_small_arch"),
          ("a jagged crag of pale rock", "sk_crag"),
          ("a fruit tree heavy with pale gold fruit", "sk_fruit_tree"),
          ("a fallen log covered in moss and small white flowers", "sk_flower_log")])])

sheet("SK4", "props", "the ancient ruins", "assets/tiles/sky/props/",
      ["assets/tiles/feralas/props/fe_highborne_arch.png", "assets/tiles/feralas/props/fe_statue_head.png",
       "assets/tiles/feralas/props/fe_ivy_column.png"],
      "These props are the ancient ruins of the Celestial Expanse, older than the Aetherians, left by the Kharad's "
      "ancestors when the sky was young: colossal pale stone, faded gold, corroded bronze-green metal, and old "
      "machinery that is starting to wake, its cores pulsing soft blue-white. Overgrown with moss, vines and small "
      "golden flowers, lit by bright sky light.",
      "Objects keep their RELATIVE scale: everything here was built by giants, so the arch, the statue and the dome "
      "fragment are the largest sprites on the sheet; a bell, a lantern pillar and a rubble pile are small. Do not blow "
      "each one up to fill its own cell.",
      [("COLUMNS AND ARCHES", [
          ("a colossal broken column, its top sheared off", "sk_broken_column"),
          ("a colossal column lying toppled in pieces", "sk_fallen_column"),
          ("a giant ancient arch, still standing", "sk_ancient_arch"),
          ("a giant arch half fallen", "sk_half_arch"),
          ("a column wrapped in vines and golden flowers", "sk_vine_column"),
          ("a corner of ruined wall with an empty window", "sk_ruin_corner")]),
       ("STATUES AND STONES", [
          ("the head of a giant statue lying in the grass", "sk_giant_head"),
          ("a giant statue toppled on its side", "sk_toppled_statue"),
          ("a tall carved ancestral pillar, weathered", "sk_ancestor_pillar"),
          ("a carved obelisk with worn reliefs (no readable writing)", "sk_obelisk"),
          ("a stone dais with steps on every side", "sk_dais"),
          ("a fragment of a collapsed dome", "sk_dome_fragment")]),
       ("THE OLD MACHINES", [
          ("an ancient machine of bronze-green metal half buried, dormant", "sk_buried_machine"),
          ("a dormant giant sky-golem lying on its back, overgrown", "sk_dormant_golem"),
          ("a golem's core, a round cage of metal with a pulsing blue-white heart", "sk_golem_core"),
          ("a gravity stone held floating in a cradle of chains", "sk_gravity_cradle"),
          ("an ancient engine pylon, cracked, faintly humming with light", "sk_engine_pylon"),
          ("a giant gear standing on edge, half sunk in the ground", "sk_giant_gear")]),
       ("STAIRS AND WAYS", [
          ("a broken stair rising into nothing", "sk_stair_nowhere"),
          ("the stub of a broken bridge ending in empty air", "sk_bridge_stub"),
          ("an overgrown stair of giant steps", "sk_giant_stair"),
          ("a ruined gate of two giant pillars", "sk_ruin_gate"),
          ("a chain as thick as a tree trunk hanging down into the clouds from a stone anchor", "sk_sky_chain"),
          ("a floating fragment of ruin, a slab with a broken column, hovering", "sk_float_ruin")]),
       ("RELICS", [
          ("an ancient bronze bell fallen on its side", "sk_ancient_bell"),
          ("a dry ancient fountain of carved stone", "sk_dry_fountain"),
          ("an ancient brazier, cold", "sk_cold_brazier"),
          ("an ancient lantern pillar, its crystal dark", "sk_lantern_pillar"),
          ("a giant's sword of stone and bronze driven into the ground", "sk_giant_sword"),
          ("a mosaic fragment of coloured stone half buried", "sk_mosaic_fragment")]),
       ("NATURE TAKING IT BACK", [
          ("a crystal cluster grown up through a broken slab", "sk_crystal_slab"),
          ("a golden tree growing out of a ruin's wall", "sk_ruin_tree"),
          ("a pile of rubble with moss and flowers", "sk_rubble_flowers"),
          ("a ruined wall section overgrown with ivy", "sk_ivy_wall"),
          ("a sky river channel of carved stone, broken, water spilling out (the water inside the channel)",
           "sk_broken_channel"),
          ("a nest of a great sky bird built on top of a broken column", "sk_column_nest")])])

# ===================================================================================== THE AETHERIANS
AET = ("These are the AETHERIANS' buildings: titan-scale architecture mixed with gnomish engineering but much grander. "
       "White marble and pale stone trimmed with gold filigree; tall slender spires and pinnacles with long narrow "
       "windows of glowing sky-blue crystal; domed halls with gold-ribbed domes and columned rotundas; arched bridges "
       "hung with deep blue banners bearing a gold sigil; circular plazas inlaid with gold rings; winged guardian "
       "statues; floating parts held by gravity magic; fine bronze gears and rings worked into the stone. Palette: "
       "white marble, warm gold, sky-blue crystal light, deep royal blue cloth, touches of bronze. Ancient, proud, "
       "radiant, built by a people who think the ground is primitive.")
sheet("SK5", "buildings", "Aurelion, the Aetherian city (the city's services and homes)", "assets/buildings/",
      ["docs/zone_refs/aurelion_ref_spires.png", "docs/zone_refs/aurelion_ref_domes.png",
       "assets/buildings/fm_great_hall.png"],
      AET + " This sheet is AURELION, their suspended capital: its grand halls, the services a city needs, and its "
            "homes.",
      "Objects keep their RELATIVE scale: the palace spire, the archive and the guesthouse are the largest sprites on "
      "the sheet; a lamp post, a bench and a mail pylon are small. Do not blow each one up to fill its own cell.",
      [("THE GREAT HALLS", [
          ("the Spire Palace, a soaring tower of pale stone and bronze with floating rings around its top",
           "ae_spire_palace"),
          ("the Grand Archive, a domed library with tall crystal windows", "ae_archive"),
          ("the guesthouse (the inn), a graceful hall with terraces and glowing lanterns", "ae_guesthouse"),
          ("the exchange (the auction house), a colonnaded hall with a bronze dome", "ae_exchange"),
          ("the vault (the bank), a heavy round building of pale stone with bronze doors", "ae_vault"),
          ("the skiff dock (the flight master's), a tall tower with a landing ring and a small moored sky-skiff",
           "ae_skiff_dock")]),
       ("LEARNING AND CRAFT", [
          ("an academy of the arcane, a hall with an observatory dome", "ae_academy"),
          ("an observatory with a great bronze telescope", "ae_observatory"),
          ("an alchemy laboratory with glass towers of glowing liquid", "ae_laboratory"),
          ("an enchanter's sanctum, a small temple with a crystal at its heart", "ae_sanctum"),
          ("a fine forge of bronze and stone with a crystal-blue hearth", "ae_forge"),
          ("a trainers' hall with an open practice court", "ae_trainers_hall")]),
       ("HOMES", [
          ("a grand residence with floating balconies", "ae_residence_large"),
          ("a medium house of pale stone with a bronze-roofed tower", "ae_house_medium"),
          ("a small house with a round crystal window", "ae_house_small"),
          ("a tall slender residence tower", "ae_residence_tower"),
          ("a terrace garden pavilion with silver-blue plants", "ae_garden_pavilion"),
          ("a row of elegant townhouses joined by arches", "ae_townhouses")]),
       ("MARKETS AND SQUARES", [
          ("a market kiosk under a bronze canopy with crystal wares", "ae_kiosk_crystal"),
          ("a market kiosk with scrolls and instruments", "ae_kiosk_scrolls"),
          ("a market kiosk with fine cloth and silver jewellery", "ae_kiosk_cloth"),
          ("a fountain with a floating sphere of water above its basin (the water inside the basin)",
           "ae_fountain"),
          ("a statue of an Aetherian magister in robes, crystals on the shoulders", "ae_magister_statue"),
          ("a hover cart, a bronze cart floating a hand's width above the ground", "ae_hover_cart")]),
       ("THE CITY'S WORKINGS", [
          ("a gravity lift, a pillar with a floating platform beside it", "ae_gravity_lift"),
          ("a bridge pylon with arcs of blue light reaching out from it", "ae_bridge_pylon"),
          ("a city gate, an arch of pale stone with bronze rings turning in it", "ae_city_gate"),
          ("an arcane engine pylon that holds the city up, glowing", "ae_engine_pylon"),
          ("a mail pylon, a small bronze column with a glowing slot", "ae_mail_pylon"),
          ("a guard post with a crystal-tipped lance rack", "ae_guard_post")]),
       ("SMALL PIECES", [
          ("a crystal lamp post", "ae_lamp_post"),
          ("a curved stone bench with bronze armrests", "ae_bench"),
          ("a stone planter of silver-blue flowers", "ae_planter"),
          ("a tall banner of deep blue and gold showing a crystal and a ring (no text)", "ae_banner"),
          ("crates of bronze and glass holding glowing crystals", "ae_crystal_crates"),
          ("a floating orb lantern on a bronze stand", "ae_orb_lantern")])])

sheet("SK6", "buildings", "the Ascendancy, the sky-forges and the engines", "assets/buildings/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "assets/buildings/fm_sentinel_tower.png",
       "assets/tiles/worldtree/props/wt_crashed_construct.png"],
      AET + " This sheet is their power and their military, the ASCENDANCY: enormous sky-forges, crystal engines, "
            "suspended fortresses, storm artillery, arcane bombards and the docks of their war-skiffs; and the first "
            "of their works to fail.",
      "Objects keep their RELATIVE scale: the sky-forge, the crystal engine and the fortress keep are the largest "
      "sprites on the sheet; an ammunition rack, a crate and a standard are small. Do not blow each one up to fill its "
      "own cell.",
      [("SKY-FORGES AND ENGINES", [
          ("an enormous sky-forge, a great hall of bronze and stone with a molten crystal heart glowing through its "
           "doors", "ae_sky_forge"),
          ("a giant crystal engine, a huge blue crystal turning inside rings of bronze", "ae_crystal_engine"),
          ("a gravity anchor: a bronze pylon with a chain running down into the clouds", "ae_gravity_anchor"),
          ("a storm collector, a tall mast with copper coils and crackling light", "ae_storm_collector"),
          ("a construct assembly cradle holding a half-built flying construct", "ae_construct_cradle"),
          ("a shield pylon throwing up a dome of faint blue light", "ae_shield_pylon")]),
       ("FORTRESSES", [
          ("a suspended fortress keep, tall and grim, floating stones around its base", "ae_fortress_keep"),
          ("a barracks of pale stone with bronze shutters", "ae_barracks"),
          ("a watch spire with a crystal lookout", "ae_watch_spire"),
          ("a straight section of fortress wall with bronze crenellations", "ae_fortress_wall"),
          ("a round fortress wall tower", "ae_wall_tower"),
          ("a fortress gate with heavy bronze doors", "ae_fortress_gate")]),
       ("THE WAR MACHINE", [
          ("storm artillery: a great cannon of bronze and crystal on a turntable, crackling", "ae_storm_artillery"),
          ("an arcane bombard tower, squat and heavy, with a glowing barrel", "ae_bombard_tower"),
          ("a lancer hangar with open doors and racks of sky-lances", "ae_lancer_hangar"),
          ("a landed survey skiff, a small graceful airship of white and bronze with fin-like glowing sails",
           "ae_survey_skiff"),
          ("an Ascendancy war-skiff, larger and armed, moored and hovering", "ae_war_skiff"),
          ("a docking cradle for a skiff, a frame of bronze arms", "ae_dock_cradle")]),
       ("THE CAMP OF A LANDING", [
          ("an officer's field pavilion of deep blue cloth on bronze poles", "ae_field_pavilion"),
          ("a soldiers' tent of pale cloth", "ae_soldier_tent"),
          ("a rack of crystal ammunition", "ae_ammo_rack"),
          ("a stack of supply crates stamped with bronze plates (no text)", "ae_supply_crates"),
          ("an Ascendancy war standard of deep blue and silver (no text)", "ae_war_standard"),
          ("a portable crystal beacon on a tripod", "ae_crystal_beacon")]),
       ("WHAT IS FAILING", [
          ("a crystal engine gone dark, its rings stopped, cracked", "ae_dead_engine"),
          ("a tower leaning and cracking, stones breaking away", "ae_leaning_tower"),
          ("a broken section of a city's outer ring, hanging off its supports", "ae_broken_ring"),
          ("a shield pylon flickering and sparking", "ae_failing_pylon"),
          ("a pile of bronze and pale stone rubble", "ae_rubble"),
          ("an evacuation skiff loaded with crates and bundles", "ae_evac_skiff")]),
       ("THE REFUGEES", [
          ("a refugee pavilion of patched fine cloth", "ae_refugee_pavilion"),
          ("bundles and chests of belongings piled together", "ae_belongings"),
          ("a small crystal heater with blankets round it", "ae_crystal_heater"),
          ("a soup kitchen table with bronze pots", "ae_soup_table"),
          ("a memorial of small crystals set in a stone ring", "ae_crystal_memorial"),
          ("a damaged house with its roof gone", "ae_damaged_house")])])

# ===================================================================================== THE VEYR
sheet("SK7", "buildings", "the Veyr, the Stormborn", "assets/buildings/",
      ["assets/tiles/feralas/props/fe_hippogryph_nest.png", "assets/buildings/fm_hippogryph_roost.png",
       "assets/tiles/stranglethorn/props/stv_troll_arch.png"],
      "These are the VEYR's buildings: a militaristic, predatory sky people of avian humanoids who carve their cities "
      "into impossibly high stone spires and build across enormous natural arches. Dark slate and storm-grey stone, "
      "carved in sharp sweeping shapes like wings and talons; great nests of woven branches; wind-driven machines of "
      "wood, sailcloth and copper; lightning batteries of copper and glass crackling blue; clan colours in deep red, "
      "gold and storm blue with feathers everywhere. Clan-based, honour-driven, fierce.",
      "Objects keep their RELATIVE scale: the spire hall, the clan longhall and the thunder temple are the largest "
      "sprites on the sheet; a wind chime, a perch and a drum are small. Do not blow each one up to fill its own cell.",
      [("CARVED IN THE SPIRES", [
          ("a hall carved into a rock pinnacle, with ledges and a great open door", "vy_spire_hall"),
          ("a clan longhall of dark stone and timber with a roof like folded wings", "vy_clan_longhall"),
          ("a house built across a stone arch, open below", "vy_arch_house"),
          ("a small dwelling carved into a rock with a woven nest roof", "vy_rock_dwelling"),
          ("a watch perch on a slim stone needle", "vy_watch_perch"),
          ("a stone gate carved like two great raised wings", "vy_wing_gate")]),
       ("ROOSTS AND NESTS", [
          ("a great eyrie roost, a huge woven nest on a stone platform", "vy_eyrie"),
          ("a war-roost for dive bombers, a tower of perches and launch ledges", "vy_war_roost"),
          ("a talon cavalry stable for great war-birds, with perches and a meat trough", "vy_cavalry_stable"),
          ("a nest bowl of woven branches lined with down", "vy_nest_bowl"),
          ("a hanging cage of branches for prisoners", "vy_hanging_cage"),
          ("a feather-lined chieftain's seat on a rock", "vy_chief_seat")]),
       ("THE STORM", [
          ("the thunder temple, a tall stone temple crowned by a copper lightning rod, crackling", "vy_thunder_temple"),
          ("a lightning battery: big glass jars and copper coils crackling with blue light", "vy_lightning_battery"),
          ("a wind engine with sailcloth vanes turning on a timber tower", "vy_wind_engine"),
          ("a storm-forge with a hearth lit by lightning", "vy_storm_forge"),
          ("a storm altar of dark stone with a copper bowl", "vy_storm_altar"),
          ("a weathervane totem of copper feathers", "vy_weathervane")]),
       ("THE CLANS AT WAR", [
          ("a rack of storm-forged spears with glowing blue tips", "vy_spear_rack"),
          ("a wind archers' range of three targets on posts", "vy_archery_range"),
          ("a clan totem carved with feathers and a beaked face", "vy_clan_totem"),
          ("a trophy pole hung with feathers, beaks and broken weapons", "vy_trophy_pole"),
          ("a war drum of stretched hide on a carved frame", "vy_war_drum"),
          ("a feather banner in deep red and gold (no text)", "vy_feather_banner")]),
       ("CROSSING THE SKY", [
          ("a rope-and-plank hanging bridge segment", "vy_hanging_bridge"),
          ("a launch ledge, a stone platform jutting out over nothing", "vy_launch_ledge"),
          ("a wind chime array of copper and bone", "vy_wind_chimes"),
          ("a signal fire on a stone post", "vy_signal_fire"),
          ("a glider frame of wood and sailcloth on a rack", "vy_glider_rack"),
          ("a carved stone stair winding up a spire's flank", "vy_spire_stair")]),
       ("SMALL PIECES", [
          ("a brazier shaped like a raised talon", "vy_talon_brazier"),
          ("a market perch with meat and feathers for trade", "vy_market_perch"),
          ("a kiln of stone with a copper chimney", "vy_kiln"),
          ("a prayer stone wrapped in feathered cords", "vy_prayer_stone"),
          ("a stack of woven baskets", "vy_baskets"),
          ("a water trough carved from a single stone", "vy_trough")])])

# ===================================================================================== THE KHARAD
sheet("SK8", "buildings", "the Kharad, the Cloud Giants", "assets/buildings/",
      ["assets/tiles/feralas/props/fe_highborne_arch.png", "assets/buildings/fe_twin_colossal.png",
       "assets/tiles/feralas/props/fe_statue_head.png"],
      "These are the KHARAD's buildings: the works of cloud giants, a civilization older than any kingdom on the ground "
      "and obsessed with ancestry and monumental construction. Everything is colossal: cloud-white marble and grey "
      "granite in giant blocks, veins of mineral crystal (quartz white, amethyst violet, gold, deep blue), gravity "
      "stones floating in cradles, ancient elemental machinery of stone and dark metal with cores of wind, earth, "
      "water and lightning, and endless statues of ancestors. Cold, high, ancient, awe-inspiring.",
      "Objects keep their RELATIVE scale: these are built for giants, so the temple, the citadel keep and the ancestor "
      "statue are the largest sprites on the sheet; a giant's urn and a brazier are still bigger than a human house "
      "but are the smallest here. Do not blow each one up to fill its own cell.",
      [("CITADELS", [
          ("a colossal temple with a stepped roof and giant pillars", "kh_temple"),
          ("a citadel keep of giant blocks with floating stones around its crown", "kh_citadel_keep"),
          ("an ancestor hall lined with statues outside its doors", "kh_ancestor_hall"),
          ("a giant's house of white marble with a heavy roof", "kh_giant_house"),
          ("a giant's throne on a high dais", "kh_throne"),
          ("monumental doors of stone and bronze set in a wall", "kh_great_doors")]),
       ("ANCESTORS", [
          ("a colossal statue of a Kharad ancestor holding a hammer", "kh_ancestor_statue"),
          ("a statue of a kneeling giant holding up a floating stone", "kh_kneeling_statue"),
          ("a carved monolith of ancestral faces stacked one above another", "kh_face_monolith"),
          ("an obelisk of granite with mineral veins", "kh_obelisk"),
          ("a giant urn of ashes on a plinth", "kh_urn"),
          ("an ancestral shrine with a gold-veined altar", "kh_ancestor_shrine")]),
       ("THE ANCIENT MACHINERY", [
          ("a gravity stone engine: a huge dark stone floating inside a frame of stone arms", "kh_gravity_engine"),
          ("a wind core machine, a cage of stone around a swirling white storm", "kh_wind_core"),
          ("an earth core machine, a cage of stone around a glowing amber boulder", "kh_earth_core"),
          ("a water core machine, a basin with a floating sphere of water (the water inside)", "kh_water_core"),
          ("a lightning core machine, two stone horns with lightning arcing between", "kh_lightning_core"),
          ("a great chain anchor, a stone block with a giant chain running off into the sky", "kh_chain_anchor")]),
       ("BRIDGES AND WAYS", [
          ("a suspended bridge pylon of white stone with chains", "kh_bridge_pylon"),
          ("a monumental arch", "kh_monument_arch"),
          ("a stair of giant steps", "kh_giant_steps"),
          ("a gate tower for a citadel wall", "kh_gate_tower"),
          ("a siege platform, a great floating stone deck with a stone thrower on it", "kh_siege_platform"),
          ("a thunder mage's tower with a crystal at its peak", "kh_thunder_tower")]),
       ("ENDLESS BUILDING", [
          ("scaffolding of huge timbers around half a statue", "kh_scaffold"),
          ("a stone-cutter's crane of timber and chain", "kh_crane"),
          ("a stack of giant quarried blocks", "kh_quarry_blocks"),
          ("a giant's forge with an anvil the size of a cart", "kh_forge"),
          ("a mason's yard with a half-cut block and giant tools", "kh_mason_yard"),
          ("a gravity sled for moving blocks, a floating stone slab with chains", "kh_gravity_sled")]),
       ("SMALL PIECES (still giant)", [
          ("a giant brazier of granite with a white flame", "kh_brazier"),
          ("a giant's water jug and cup on a stone table", "kh_table"),
          ("a giant's bench of a single stone block", "kh_bench"),
          ("a tall lantern of crystal in a stone cage", "kh_lantern"),
          ("a pile of ore and mineral crystals", "kh_ore_pile"),
          ("a standard of cloud-white cloth with a gold stone sewn in it (no text)", "kh_standard")])])

# ===================================================================================== THE FIRMAMENT
sheet("SK9", "props", "the Fading Firmament and the war", "assets/tiles/sky/props/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "assets/tiles/worldtree/props/wt_crashed_construct.png",
       "assets/tiles/feralas/props/fe_dead_snag.png"],
      "These props are the dying heart of the Aetherian world and the war over what's left: islands breaking apart, "
      "dead crystal, dark engines, abandoned homes, and the Ascendancy's siege lines. Violet dusk light, grey ash, black "
      "void, dimmed blue crystal and scorched bronze, with a few things still glowing defiantly.",
      "Objects keep their RELATIVE scale: the falling island chunk, the dead engine and the wrecked war-skiff are the "
      "largest sprites on the sheet; a crystal shard, a lantern and a barricade post are small. Do not blow each one up "
      "to fill its own cell.",
      [("THE SKY COMING APART", [
          ("a chunk of island breaking away and starting to fall, rocks and roots trailing", "ff_falling_chunk"),
          ("a crumbling edge of ground with motes rising off it", "ff_crumbling_edge"),
          ("a rift in the air, a tear of violet void", "ff_sky_rift"),
          ("a floating rock gone grey and cracked, sinking", "ff_sinking_rock"),
          ("a dead crystal tree, its leaves turned to grey glass", "ff_dead_crystal_tree"),
          ("a bed of dead grey flowers", "ff_dead_flowers")]),
       ("WHAT THEY LEFT", [
          ("an abandoned Aetherian home with its door open", "ff_abandoned_home"),
          ("a toppled statue of an Aetherian magister", "ff_toppled_magister"),
          ("an empty market kiosk, its canopy torn", "ff_empty_kiosk"),
          ("a fallen orb lantern, still faintly glowing", "ff_fallen_lantern"),
          ("a child's toy, a little bronze floating bird, on the ground", "ff_toy_bird"),
          ("a garden gone grey, its planters cracked", "ff_grey_garden")]),
       ("DEAD ENGINES", [
          ("a vast crystal engine gone black, cracked down the middle", "ff_dead_engine"),
          ("a gravity anchor whose chain has snapped", "ff_snapped_anchor"),
          ("a sky-forge's hearth gone cold and dark", "ff_cold_forge"),
          ("dim crystal shards scattered on the ground", "ff_dim_shards"),
          ("a broken pylon, its light flickering out", "ff_broken_pylon"),
          ("a heap of burnt-out crystal", "ff_burnt_crystal")]),
       ("THE ASCENDANCY'S SIEGE", [
          ("a storm artillery emplacement behind a bronze shield", "ff_artillery_post"),
          ("a barricade of bronze plates and stone", "ff_barricade"),
          ("a crater with a glowing crystal at its heart", "ff_crystal_crater"),
          ("a trench line of stacked stone", "ff_trench"),
          ("a command table with a glowing map of the sky", "ff_command_table"),
          ("a rack of sky-lances", "ff_lance_rack")]),
       ("WRECKAGE", [
          ("a wrecked war-skiff broken in two", "ff_wrecked_skiff"),
          ("a destroyed construct, a heap of bronze limbs", "ff_dead_construct"),
          ("a shattered shield pylon", "ff_shattered_pylon"),
          ("a burnt pavilion", "ff_burnt_pavilion"),
          ("a toppled Veyr clan totem", "ff_fallen_totem"),
          ("a broken Kharad statue's hand", "ff_giant_hand")]),
       ("STILL HOLDING ON", [
          ("a small shrine where crystals are still lit", "ff_lit_shrine"),
          ("a single bright blue crystal growing out of grey ground", "ff_last_crystal"),
          ("a refugee camp fire with crystal stones round it", "ff_camp_fire"),
          ("a patched tent of blue cloth", "ff_patched_tent"),
          ("a stack of salvaged bronze and crystal", "ff_salvage"),
          ("a small floating island with one green tree still alive on it", "ff_last_tree")])])

# ===================================================================================== LANDMARKS
sheet("SK10", "landmarks", "the sky's great places, part 1", "assets/buildings/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "docs/zone_refs/world_tree_trunk_city.jpg",
       "assets/buildings/fe_twin_colossal.png"],
      "These are the sky's giant set pieces, the views people will remember.",
      None,
      [("ROW 1", [
          ("THE CROWN OF THE WORLD TREE, the top of a colossal tree rising out of a sea of cloud on its own island, "
           "golden leaves, waterfalls pouring off the island's edges down into the cloud, sunset gold light",
           "sk_tree_crown"),
          ("THE SPIRE OF AURELION, the Aetherian capital's central tower of pale stone and bronze, rings of floating "
           "stone turning around it, crystal glowing at its peak, the city's terraces around its foot",
           "ae_aurelion_spire"),
          ("THE GREAT SKY-FORGE, a monstrous forge-hall of bronze and stone, glowing crystal fire pouring from its "
           "vents, chains holding it to floating rocks", "ae_great_forge")]),
       ("ROW 2", [
          ("THE TALON ARCH, a natural stone arch as big as a mountain with a Veyr city built across its top and "
           "carved into its legs, nests and banners, storm clouds behind", "vy_talon_arch"),
          ("THE TEMPLE OF THE FIRST KHARAD, a colossal temple of white marble on its own floating rock, with "
           "ancestor statues lining a giant stair up to it", "kh_first_temple"),
          ("THE WAKING ENGINE, an ancient machine of colossal stone and bronze-green metal in the ruins, its core "
           "opening and glowing blue-white for the first time in ages", "sk_waking_engine")]),
       ("ROW 3", [
          ("A FALLING ISLAND, a whole island with trees and a ruined house breaking apart in mid-air, pieces "
           "falling away into violet void", "ff_falling_island"),
          ("THE SURVEY SHIP AT THE CROWN, a graceful Aetherian airship of white stone, bronze and blue crystal moored "
           "on a gold branch, its gangway lowered (the first contact)", "ae_first_ship"),
          ("THE GREAT AIRSHIP DOCK, a tower of bronze and pale stone with three landing arms and a large airship "
           "moored at one", "ae_airship_dock")])])

sheet("SK11", "landmarks", "the sky's great places, part 2 (doors and wonders)", "assets/buildings/",
      ["docs/zone_refs/world_tree_crown_island.jpg", "docs/zone_refs/world_tree_great_settlement.jpg",
       "assets/buildings/fe_dire_maul_gate.png"],
      "These are more of the sky's giant set pieces: the doors to its dungeons and its wonders.",
      None,
      [("ROW 1", [
          ("THE FORGE GATE, the armoured entrance of an Aetherian sky-forge, huge bronze doors half open with crystal "
           "light pouring out (a dungeon door, readable as a way in)", "ae_forge_gate"),
          ("THE HEART ENGINE, the colossal crystal heart of the Aetherian world inside a cage of bronze rings, "
           "cracked, flickering between brilliant blue and dark (a raid door)", "ae_heart_engine"),
          ("THE ANCESTOR VAULT, a giant stone door set into a floating rock, carved with Kharad ancestors, sealed with "
           "a floating gravity stone", "kh_ancestor_vault")]),
       ("ROW 2", [
          ("THE THUNDER PEAK, the highest Veyr spire with a temple at its summit, a lightning bolt striking its "
           "copper crown", "vy_thunder_peak"),
          ("THE WELLSPRING, a floating island with a spring that pours a sky river off all its edges in great "
           "waterfalls, rainbows in the mist", "sk_wellspring"),
          ("THE CHAINED STONE, a gravity stone as big as a hill held in the air by giant chains to four "
           "anchor-towers", "kh_chained_stone")]),
       ("ROW 3", [
          ("THE CLOUD HARBOUR LIGHTHOUSE, a tall tower of pale stone with a crystal lamp shining across the cloud "
           "sea, a little harbour of sky-skiffs below it", "sk_lighthouse"),
          ("THE STAR OBSERVATORY, an ancient domed observatory in the ruins, its dome split open, a great crystal "
           "lens still pointing at the sky", "sk_observatory_ruin"),
          ("THE VOID RIFT, a great tear in the sky over the Firmament, cloud pouring down into it, violet light and "
           "dark beyond", "ff_void_rift")])])

# ===================================================================================== CREATURES
sheet("SK12", "creatures", "the Aetherians and the Ascendancy", "assets/creatures/",
      ["assets/creatures/az_arcane_construct.png", "assets/creatures/elemental_arcane.png",
       "assets/creatures/fe_naga_guardian.png"],
      "These are the AETHERIANS (tall, imposing humanoids with pale blue-grey or bronze skin, luminous eyes and natural "
      "crystal growths along their bodies) and their military, the ASCENDANCY: sky lancers, storm artillery crews, "
      "arcane bombardiers and mechanical flying constructs of bronze, pale stone and blue crystal. Armour is fitted "
      "bronze and white enamel with deep blue cloth; weapons are long lances and staves tipped with crystal. Rows 1 to "
      "4 are Ascendancy enemies and their machines; rows 5 and 6 are Aetherian civilians and scholars, peaceful, for "
      "the city and the quest givers.",
      "Creatures keep their RELATIVE scale: an Aetherian stands taller than a human; a repair drone and a scout "
      "construct are small; the construct titan and the siege walker are the largest sprites on the sheet. Do not blow "
      "each one up to fill its own cell.",
      [("THE ASCENDANCY", [
          ("a sky lancer in bronze and white armour with a long crystal-tipped lance", "ae_sky_lancer"),
          ("a legionary with a tall shield and a short crystal blade", "ae_legionary"),
          ("an arcane bombardier with a glowing bombard on his shoulder", "ae_bombardier"),
          ("a storm artillerist with a crackling rod and copper gauntlets", "ae_artillerist"),
          ("a gravity binder, a caster with floating stones circling her hands", "ae_gravity_binder"),
          ("an Ascendancy officer in a tall crested helm with a cape", "ae_officer")]),
       ("THE ASCENDANCY'S ELITE", [
          ("a warden in heavy armour with a tower shield of crystal", "ae_warden"),
          ("a crystal-weaver mage, crystals grown large on her shoulders", "ae_crystal_weaver"),
          ("a storm caller with lightning around a raised staff", "ae_storm_caller"),
          ("a sky lancer riding a flying construct steed of bronze", "ae_lancer_mounted"),
          ("an Ascendancy inquisitor in a mask of white enamel", "ae_inquisitor"),
          ("an Ascendancy high commander in ornate gold armour, crystals like a crown (a boss)", "ae_high_commander")]),
       ("CONSTRUCTS", [
          ("a scout construct, a small flying machine with a crystal eye", "ae_scout_construct"),
          ("a construct hound of bronze plates and a crystal heart", "ae_construct_hound"),
          ("a bomber construct, a floating machine with bomb-pods", "ae_bomber_construct"),
          ("a repair drone with tiny arms", "ae_repair_drone"),
          ("a sentinel automaton, a tall bronze guardian with a halberd", "ae_sentinel"),
          ("a crystal golem, a walking mass of blue crystal in bronze bands", "ae_crystal_golem")]),
       ("WAR MACHINES", [
          ("a siege walker, a four-legged bronze machine with a storm cannon", "ae_siege_walker"),
          ("a construct titan, a giant bronze and stone humanoid machine (the largest here)", "ae_construct_titan"),
          ("a flying gunship construct with wing-blades", "ae_gunship"),
          ("a shield drone projecting a disc of blue light", "ae_shield_drone"),
          ("a malfunctioning construct, sparking and missing an arm", "ae_broken_construct"),
          ("a storm-charged construct crackling with lightning", "ae_storm_construct")]),
       ("AETHERIAN PEOPLE (peaceful)", [
          ("an Aetherian scholar in long blue robes holding a glowing tablet", "ae_scholar"),
          ("an Aetherian magister in white and gold, crystals on the brow", "ae_magister"),
          ("an Aetherian engineer with tools and a monocle lens", "ae_engineer"),
          ("an Aetherian envoy in travelling robes, holding a staff", "ae_envoy"),
          ("an Aetherian city guard in light armour", "ae_city_guard"),
          ("an Aetherian merchant with a floating case of wares", "ae_merchant")]),
       ("AETHERIAN PEOPLE (the dying world)", [
          ("an Aetherian refugee wrapped in a blanket, crystals dim", "ae_refugee"),
          ("an old Aetherian sage with a long white beard and crystal growths like a crown", "ae_sage"),
          ("an Aetherian child holding a little bronze bird", "ae_child"),
          ("an Aetherian healer with a glowing crystal in her hands", "ae_healer"),
          ("an Aetherian sky-skiff pilot in goggles and a leather coat", "ae_pilot"),
          ("an Aetherian forge-worker in a heavy apron", "ae_forge_worker")])])

sheet("SK13", "creatures", "the Veyr and the Kharad", "assets/creatures/",
      ["assets/creatures/harpy_1.png", "assets/creatures/fe_forest_giant.png",
       "assets/creatures/st_windshear_harpy.png"],
      "These are the VEYR (avian humanoids with feathered arms, powerful talons, hooked beaks or partly humanoid faces; "
      "clan warriors in leather, copper and storm-forged steel, clan colours deep red, gold and storm blue) and the "
      "KHARAD (cloud giants: large, broad humanoids with stone-like skin, cloud-white hair and mineral crystals growing "
      "from their shoulders and brows; robes and armour of white, grey and gold). Rows 1 to 3 are Veyr, rows 4 to 6 "
      "are Kharad.",
      "Creatures keep their RELATIVE scale: a Veyr stands about as tall as a human; a Kharad is a giant three times "
      "that, the largest sprites on the sheet; the gravity golem and the ancestral spirit are as big as a Kharad. Do "
      "not blow each one up to fill its own cell.",
      [("THE VEYR WARRIORS", [
          ("a Veyr warrior with a storm-forged spear, feathered arms spread", "vy_warrior"),
          ("a Veyr wind archer drawing a long bow", "vy_wind_archer"),
          ("a Veyr dive bomber, wings folded, diving with talons out", "vy_dive_bomber"),
          ("a Veyr thunder priest with lightning crackling in his talons", "vy_thunder_priest"),
          ("a Veyr talon cavalry rider on a great war-bird", "vy_talon_rider"),
          ("a Veyr scout, lean and fast, with two hook blades", "vy_scout")]),
       ("THE VEYR CLANS", [
          ("a Veyr clan chief with a crest of red feathers and a great axe (a boss)", "vy_clan_chief"),
          ("a Veyr storm shaman wrapped in charms", "vy_storm_shaman"),
          ("a Veyr veteran, scarred, one eye, a broken beak", "vy_veteran"),
          ("a Veyr hunter with a net and a bola", "vy_hunter"),
          ("a Veyr elder with grey feathers leaning on a staff (peaceful)", "vy_elder"),
          ("a Veyr fledgling warrior, young and fierce (peaceful)", "vy_fledgling")]),
       ("THE VEYR'S BEASTS", [
          ("a great war-bird, the Veyr's cavalry mount, armoured", "vy_war_bird"),
          ("a storm hawk, crackling", "vy_storm_hawk"),
          ("a Veyr riding raptor-bird, tall and flightless", "vy_raptor_bird"),
          ("a stormfeather matriarch, a huge bird with a lightning crest (a rare)", "vy_stormfeather_rare"),
          ("a Veyr lightning-bound captive elemental in copper chains", "vy_bound_elemental"),
          ("a Veyr clan champion in full storm-steel armour", "vy_champion")]),
       ("THE KHARAD", [
          ("a Kharad giant infantryman with a stone hammer and a slab shield", "kh_infantry"),
          ("a Kharad thunder mage with lightning gathering between his hands", "kh_thunder_mage"),
          ("a Kharad stonewarden in heavy granite armour", "kh_stonewarden"),
          ("a Kharad temple guardian with a giant halberd", "kh_temple_guardian"),
          ("a Kharad mason with giant tools (peaceful)", "kh_mason"),
          ("a Kharad elder in white robes with a beard like cloud (peaceful)", "kh_elder")]),
       ("THE KHARAD'S POWERS", [
          ("a gravity golem, a servant of floating stones bound together", "kh_gravity_golem"),
          ("an ancestral spirit, a ghostly white giant", "kh_ancestral_spirit"),
          ("a Kharad siege engineer on a floating stone platform", "kh_siege_engineer"),
          ("a storm-bound elemental chained by gold bands", "kh_bound_storm"),
          ("an earth elemental of mineral crystal", "kh_mineral_elemental"),
          ("a Kharad youngling, still huge, curious (peaceful)", "kh_youngling")]),
       ("THE KHARAD'S GREAT", [
          ("a Kharad champion in gold-trimmed armour with a giant sword", "kh_champion"),
          ("a Kharad high priest with a crown of crystal (a boss)", "kh_high_priest"),
          ("a waking ancient guardian, a giant statue come alive, cracking", "kh_waking_guardian"),
          ("a Kharad king on a floating stone throne (a boss)", "kh_king"),
          ("an old Kharad sentinel construct of stone and dark metal", "kh_sentinel_construct"),
          ("the Unbound Core, an ancient elemental machine broken free, a storm in a stone cage (a rare)",
           "kh_unbound_core_rare")])])

sheet("SK14", "creatures", "the sky's beasts, elementals and critters", "assets/creatures/",
      ["assets/creatures/elemental_air_1.png", "assets/creatures/fe_skystalker.png",
       "assets/creatures/az_serpent_hatchling.png"],
      "These are the wild creatures of the sky: great beasts that swim through cloud, storm elementals, sky beasts, "
      "and the gentle animals of the high meadows and farms (for a quiet starting island). Beautiful and strange: "
      "translucent fins, luminous markings, cloud-white and gold, storm blue, crystal glints.",
      "Creatures keep their RELATIVE scale: a sky hare, a puffball and a meadow fowl are small; a sky ray and a cloud "
      "serpent are big; the sky whale is the largest sprite on the sheet. Do not blow each one up to fill its own cell.",
      [("GREAT SKY BEASTS", [
          ("a sky whale, huge and serene, with long fins and glowing markings (the largest here)", "sk_sky_whale"),
          ("a sky ray, a great manta gliding with translucent wing-edges", "sk_sky_ray"),
          ("a cloud serpent, long and white-gold, with feathered frills", "sk_cloud_serpent"),
          ("a thunderbird, a vast eagle crackling with lightning", "sk_thunderbird"),
          ("a sky eel with luminous blue spots", "sk_sky_eel"),
          ("a wind wyrm, a lean winged serpent of storm grey", "sk_wind_wyrm")]),
       ("SKY HUNTERS", [
          ("a sky lion, a golden great-cat with small feathered wings", "sk_sky_lion"),
          ("a cloud stalker, a pale cat that blends with cloud", "sk_cloud_stalker"),
          ("a gale hawk", "sk_gale_hawk"),
          ("a crystal-backed sky boar", "sk_crystal_boar"),
          ("a great sky moth with gold and blue wings", "sk_sky_moth"),
          ("a cloud jelly, a floating translucent jellyfish trailing glowing threads", "sk_cloud_jelly")]),
       ("ELEMENTALS", [
          ("a storm elemental, a towering swirl of dark cloud and lightning", "sk_storm_elemental"),
          ("a cloud elemental, soft white and billowing", "sk_cloud_elemental"),
          ("a lightning elemental, a jagged figure of blue-white bolts", "sk_lightning_elemental"),
          ("a gale elemental, a whirlwind full of leaves and stones", "sk_gale_elemental"),
          ("a crystal elemental, a walking cluster of blue crystal", "sk_crystal_elemental"),
          ("a sunlit wisp, a floating mote of warm gold light", "sk_gold_wisp")]),
       ("THE DYING SKY", [
          ("a void-touched creature, a sky beast gone grey with violet cracks", "sk_void_touched"),
          ("a fading wisp, a mote of light going out", "sk_fading_wisp"),
          ("a rift crawler, a dark many-legged thing come through a tear in the sky", "sk_rift_crawler"),
          ("a hollow storm, a storm elemental eaten away to a shell", "sk_hollow_storm"),
          ("a falling-star beast, a burning crystal creature trailing light", "sk_falling_star"),
          ("the Last Whale, an ancient sky whale grey with age and scars (a rare)", "sk_last_whale_rare")]),
       ("MEADOW AND FARM ANIMALS (for a quiet island)", [
          ("a cloud sheep, woolly and white like a little cloud", "sk_cloud_sheep"),
          ("a sky goat with spiral horns", "sk_sky_goat"),
          ("a meadow fowl, plump with gold feathers", "sk_meadow_fowl"),
          ("a sky hare with long ears and pale fur", "sk_sky_hare"),
          ("a puffball floater, a round fluffy critter that drifts in the air", "sk_puffball"),
          ("a golden stag with crystal-tipped antlers", "sk_golden_stag")]),
       ("YOUNG AND SMALL (low-level foes)", [
          ("a young sky boar", "sk_young_boar"),
          ("a sky crab with a pale shell, living on the island edges", "sk_sky_crab"),
          ("a gust sprite, a tiny mischievous swirl of wind", "sk_gust_sprite"),
          ("a thistle beetle with a crystal shell", "sk_thistle_beetle"),
          ("a cloud wolf pup's mother, a white wolf with a mane like cloud", "sk_cloud_wolf"),
          ("a moss tortoise with a small garden on its back", "sk_moss_tortoise")])])


# ===================================================================================== AURELION, MORE
AUR = (AET + " This sheet is more of AURELION, the Aetherian capital, which must be INCREDIBLE (match the two "
       "attached pictures of it): a soaring white-and-gold Spire Palace with blue crystal windows and great wing-like "
       "fins at its peak; domed basilicas and columned rotundas; districts on separate floating islands of rock, each "
       "edge pouring waterfalls into the cloud below, green trees on the terraces; circular plazas inlaid with gold "
       "and centred on fountains; a grand avenue with a glowing blue channel down its middle; long arched bridges hung "
       "with deep blue banners; huge winged guardian statues; colossal statues holding platforms; giant crystal "
       "engines glowing beneath; elegant airships with golden sail-fins coming and going; all lit warm gold by a low "
       "sun. Grander than anything on the ground.")
sheet("SK15", "buildings", "Aurelion's grandeur", "assets/buildings/",
      ["docs/zone_refs/aurelion_ref_spires.png", "docs/zone_refs/aurelion_ref_domes.png",
       "assets/buildings/ae_spire_palace.png"],
      AUR,
      "Objects keep their RELATIVE scale: the Hall of Magisters, the Ring Gate, the colossus and the conservatory are "
      "the largest sprites on the sheet; a lamp, a sun-dial and a guard statue are small. Do not blow each one up to "
      "fill its own cell.",
      [("THE MONUMENTS", [
          ("the Hall of Magisters, a vast colonnaded council hall under a bronze dome ringed with floating stones",
           "ae_magister_hall"),
          ("the Crystal Conservatory, a great glass dome full of silver-blue trees and glowing flowers",
           "ae_conservatory"),
          ("the Ring Gate, a colossal standing ring of bronze and pale stone with a slower ring of light turning "
           "inside it", "ae_ring_gate"),
          ("a colossus: a giant statue of an ancient magister holding a platform up on his shoulders",
           "ae_colossus"),
          ("the Grand Amphitheatre, a curved tier of white marble seats around a crystal stage", "ae_amphitheatre"),
          ("a sky aqueduct of bronze arches carrying a glowing stream that spills off its end as a waterfall",
           "ae_aqueduct")]),
       ("THE GREAT HOUSES", [
          ("a terraced mansion in three tiers, gardens hanging from each terrace", "ae_terrace_mansion"),
          ("a spiral library tower with balconies winding round it", "ae_spiral_library"),
          ("an ambassador's palace with tall windows and a floating balcony", "ae_ambassador_palace"),
          ("the embassy of the ground folk, a fine Aetherian house hung with troll banners, a little out of place",
           "ae_ground_embassy"),
          ("a noble's villa on its own small floating rock with a tiny bridge", "ae_floating_villa"),
          ("a guildhall of engineers with bronze gears turning on its face", "ae_engineer_guildhall")]),
       ("BRIDGES, STAIRS AND LIGHT", [
          ("a pair of light-bridge pylons, arcs of solid blue light spanning between them", "ae_light_bridge"),
          ("a bronze arch bridge span with lanterns along its rail", "ae_arch_bridge"),
          ("a floating stair, its steps hanging in the air one above another", "ae_floating_stair"),
          ("a gravity fountain where water flows upward in a spiral into a floating bowl", "ae_gravity_fountain"),
          ("a tower with small moon-stones orbiting its top", "ae_orbit_tower"),
          ("a tall aurora lantern tower casting ribbons of soft blue and gold light", "ae_aurora_tower")]),
       ("THE ENGINES BENEATH", [
          ("a crystal anchor column reaching down into the clouds, glowing along its length", "ae_anchor_column"),
          ("a ring rail, a bronze ring section turning slowly on a pylon", "ae_ring_rail"),
          ("vents breathing soft blue light and mist", "ae_light_vents"),
          ("a lift of nested bronze rings carrying a floating platform", "ae_ring_lift"),
          ("a cooling tower with a waterfall pouring down its face (the water on the tower)", "ae_cooling_tower"),
          ("an engine bay hatch in the ground, open, crystal light pouring up", "ae_engine_hatch")]),
       ("GARDENS", [
          ("a crystal tree with leaves of glass catching the light", "ae_crystal_tree"),
          ("a grove of silver-blue trees in a bronze-rimmed bed", "ae_silver_grove"),
          ("a reflecting pool pavilion with slender columns (the water inside the pool)", "ae_pool_pavilion"),
          ("a sky orchard tree heavy with glowing gold fruit", "ae_gold_orchard"),
          ("a floating meditation dais with a single crystal above it", "ae_meditation_dais"),
          ("an avenue column topped with a statue of a scholar", "ae_avenue_column")]),
       ("GRAND SMALL PIECES", [
          ("a golden sun-dial on a marble pedestal", "ae_sun_dial"),
          ("an ornate lamp of three floating orbs", "ae_triple_lamp"),
          ("a great bronze astrolabe sculpture, rings within rings", "ae_astrolabe"),
          ("a ceremonial brazier with a blue-white flame", "ae_ceremonial_brazier"),
          ("a section of grand stair with bronze balustrades", "ae_grand_stair"),
          ("an honour-guard statue of a sky lancer", "ae_guard_statue")])])

sheet("SK16", "landmarks", "the wonders of Aurelion", "assets/buildings/",
      ["docs/zone_refs/aurelion_ref_spires.png", "docs/zone_refs/aurelion_ref_domes.png",
       "assets/buildings/ae_spire_palace.png"],
      AUR + " These are its greatest set pieces.",
      None,
      [("ROW 1", [
          ("THE CROWN OF THE SPIRE PALACE, the palace's upper tiers, terraces and gardens on every level, three rings "
           "of floating stone turning around it, a great crystal blazing at its tip", "ae_palace_crown"),
          ("THE RING GATE OF AURELION, the city's entrance: a ring of bronze and stone taller than a tower, standing "
           "on a floating platform, a bridge of light running through it", "ae_great_ring_gate"),
          ("THE COLOSSUS OF THE FIRST MAGISTER, a statue as tall as a mountain holding a whole city district on its "
           "raised hands", "ae_first_colossus")]),
       ("ROW 2", [
          ("THE FALLS OF AURELION, the edge of a district where a dozen waterfalls pour off into the cloud sea, "
           "rainbows in the mist, terraces above", "ae_city_falls"),
          ("THE GREAT CONSERVATORY, a vast glass dome on its own island, a forest of crystal trees glowing inside",
           "ae_great_conservatory"),
          ("THE HALL OF THE SKY-COUNCIL, a round hall of white marble on a floating dais, every seat a floating "
           "stone", "ae_council_hall")]),
       ("ROW 3", [
          ("THE UNDERSPIRE ENGINE, the city's heart seen from below: a colossal crystal engine hanging under the "
           "rings, chains and bronze arms holding it, light pouring down into the clouds", "ae_underspire"),
          ("THE GRAND DOCK, a great bronze tower with five landing arms, airships of many sizes moored and coming in",
           "ae_grand_dock"),
          ("THE BROKEN RING, a section of the city's outer ring cracked away and tilting, buildings sliding off it, "
           "held up only by straining chains", "ae_broken_ring_landmark")])])

# ===================================================================================== FROM KYLE'S MOOD BOARD
# docs/zone_refs/sky_moodboard.jpg (19 Nov 2026): twenty scenes. What the sheets above didn't cover yet: rune circles and
# rune pillars, the tree's glowing teal heart (the crystal door in the roots, the prismatic glass cathedral between the
# roots), the airship deck and bridge, the observatory, the engine room, the golden throne room, the mountain temple.
sheet("SK17", "tiles", "interiors, decks and the glowing heart", "assets/tiles/sky/ground/",
      ["docs/zone_refs/sky_moodboard.jpg", "docs/zone_refs/aurelion_ref_spires.png",
       "assets/tiles/sky/ground/ae_marble_bronze.png"],
      "These are the floors of INTERIORS and DECKS (the Aetherian palace and throne room, an observatory, an engine "
      "room, the deck of a great airship) and of THE GLOWING HEART: the deep inside of the World Tree's roots and "
      "heartwood, where moss, roots and water glow soft teal and crystal light breaks through prismatic glass, plus the "
      "stone of storm platforms and a mountain temple island above the clouds. Palette: white marble and gold, polished "
      "honey-gold wood and brass, deep starry blue, dark bronze, glowing teal and aqua, prismatic rainbow light on "
      "pale stone, storm grey with blue rune light.",
      None,
      [("THE AIRSHIP", [
          ("polished golden-brown deck planks with brass nail lines, running one way", "sk_deck_planks"),
          ("deck planks with long brass inlay strips", "sk_deck_brass"),
          ("a scrubbed pale deck, weathered by wind", "sk_deck_pale"),
          ("a brass deck grating over a glowing blue engine below", "sk_deck_grating"),
          ("a rich blue carpet with a gold border, the bridge of a ship (the border along all edges is fine as "
           "long as it tiles)", "sk_ship_carpet"),
          ("dark lacquered wood floor of a ship's cabin", "sk_cabin_floor"),
          ("an airship's hull side seen straight on as a wall: curved golden wood planks with brass bands",
           "sk_hull_wall"),
          ("an airship cabin wall of panelled wood with a brass rail, seen straight on", "sk_cabin_wall")]),
       ("THE PALACE AND THE THRONE ROOM", [
          ("polished white marble with thin gold veins", "ae_palace_marble"),
          ("gold-tiled floor glowing warm", "ae_gold_floor"),
          ("pale stone with flowing blue-glowing rune lines in irregular paths, no repeating symbol", "ae_rune_floor"),
          ("deep blue stone with tiny gold stars set in it, scattered at random", "ae_star_floor"),
          ("a palace wall of white marble with gold pilasters, seen straight on", "ae_palace_wall"),
          ("a palace wall of tall arched windows with sky beyond, seen straight on", "ae_window_wall"),
          ("a royal blue carpet runner texture with gold thread", "ae_royal_carpet"),
          ("a mirror-still pool floor of shallow water over gold tiles", "ae_gold_pool")]),
       ("THE OBSERVATORY AND THE ENGINE ROOM", [
          ("dark polished wood with brass compass lines, irregular", "ae_observatory_floor"),
          ("night-blue stone floor scattered with tiny glowing star points", "ae_night_floor"),
          ("dark bronze floor plates with rivets and oil sheen", "ae_engine_plates"),
          ("a walkway of iron grating over moving gears far below", "ae_gear_grating"),
          ("scorched dark metal with glowing seams", "ae_hot_metal"),
          ("a wall of bronze pipes and gauges, seen straight on", "ae_pipe_wall"),
          ("a wall of turning gears behind glass, seen straight on", "ae_gear_wall"),
          ("an observatory wall of dark panels and brass star charts with no writing, seen straight on",
           "ae_chart_wall")]),
       ("THE GLOWING HEART (deep in the tree)", [
          ("glowing teal moss over dark roots", "wt_glow_moss"),
          ("dark roots woven tight, veins of teal light running through the bark", "wt_glow_roots"),
          ("a forest floor of the glowing heart: dark soil, teal ferns, small glowing mushrooms", "wt_glow_floor"),
          ("still water glowing aqua from below", "wt_glow_water"),
          ("pale stone washed with pools of prismatic rainbow light from stained glass above", "wt_prism_stone"),
          ("a floor of polished heartwood with a soft teal sheen", "wt_glow_heartwood"),
          ("a wall of giant roots twisted together with teal light glowing between them, seen straight on",
           "wt_glow_root_wall"),
          ("a wall of prismatic stained glass in pale gold, aqua, violet and amber panes between dark root ribs, "
           "seen straight on (no repeating motif)", "wt_prism_wall")]),
       ("STORM PLATFORMS", [
          ("storm-grey stone platform with blue-glowing rune grooves in irregular paths", "vy_rune_platform"),
          ("cracked storm stone with blue lightning glowing in the cracks", "vy_lightning_cracks"),
          ("wet dark flagstones under rain", "vy_wet_flags"),
          ("pale stone of an old ruined platform, cracked and tilted", "sk_ruined_platform"),
          ("broken wooden boards over stone, torn up", "sk_torn_boards"),
          ("swirling cloud around a golden glow (unwalkable, a vortex seen from above)", "sk_vortex"),
          ("a storm platform's edge wall of rune-cut stone, seen straight on", "vy_rune_wall"),
          ("sheer storm-cloud wall, dark and lit by flashes (unwalkable edge)", "vy_storm_wall")]),
       ("THE MOUNTAIN TEMPLE ISLAND", [
          ("worn grey temple flagstones with moss", "sk_temple_flags"),
          ("red-brown temple steps' stone, smooth", "sk_temple_steps"),
          ("raked white gravel of a temple garden", "sk_raked_gravel"),
          ("mountain grass with small white and gold blossoms fallen in it", "sk_blossom_grass"),
          ("bare mountain rock with lichen", "sk_mountain_rock"),
          ("a temple garden pond, clear water with gold fish shapes faint below", "sk_temple_pond"),
          ("a mountain cliff of grey rock with gold-lit ledges, seen straight on", "sk_mountain_cliff"),
          ("a temple wall of plaster and dark timber, seen straight on", "sk_temple_wall")])])

sheet("SK18", "props", "rune circles, glass and the glowing heart", "assets/tiles/sky/props/",
      ["docs/zone_refs/sky_moodboard.jpg", "assets/tiles/sky/props/sk_crystal_blue.png",
       "assets/tiles/worldtree/props/wt_knot_hole.png"],
      "These props come from the mood board: glowing rune circles and rune pillars, platforms struck by lightning, "
      "ruins orbiting a golden core, and THE GLOWING HEART deep in the World Tree's roots, where teal light runs through "
      "the wood, a crystal door glows between the roots and a cathedral of prismatic stained glass has grown between "
      "them. Palette: gold and sky-blue light, storm grey, glowing teal and aqua, prismatic rainbow glass between dark "
      "roots, dark old wood.",
      "Objects keep their RELATIVE scale: the rune circle, the glass cathedral window and the crystal door are the "
      "largest sprites on the sheet; a rune stone, a glowing mushroom and a candle cluster are small. The rune circles "
      "are FLAT on the ground, seen from the camera angle as an ellipse. Do not blow each one up to fill its own cell.",
      [("RUNE CIRCLES (flat on the ground)", [
          ("a large magic circle of gold rings and glowing blue runes inlaid in a floor", "sk_rune_circle_gold"),
          ("a magic circle of glowing teal runes on dark stone", "sk_rune_circle_teal"),
          ("a storm circle of blue lightning runes, crackling", "sk_rune_circle_storm"),
          ("a broken magic circle, cracked, half its runes dark", "sk_rune_circle_broken"),
          ("a small round rune plate glowing, a step-on switch", "sk_rune_plate"),
          ("a ring of standing rune stones around a glowing point", "sk_rune_ring")]),
       ("RUNE PILLARS AND STORM", [
          ("a square rune pillar of storm-grey stone with glowing blue runes", "vy_rune_pillar"),
          ("a rune pillar crackling with a lightning arc to the sky", "vy_rune_pillar_lit"),
          ("a short broken rune pillar", "vy_rune_pillar_broken"),
          ("a platform slab torn open by a blue lightning strike, splinters of wood and stone around it",
           "sk_lightning_breach"),
          ("a lightning spire of dark stone with a crystal tip, bolts striking it", "vy_lightning_spire"),
          ("a floating ruin cluster orbiting a glowing golden core", "sk_orbiting_ruins")]),
       ("THE GLOWING HEART", [
          ("a crystal door glowing teal, set in an arch of twisting roots", "wt_crystal_door"),
          ("a giant prismatic stained-glass window grown between root ribs, light pouring through",
           "wt_prism_window"),
          ("a teal-glowing tree, its bark veined with light", "wt_glow_tree"),
          ("a cluster of glowing aqua crystals in roots", "wt_glow_crystals"),
          ("a bed of glowing teal ferns and mushrooms", "wt_glow_ferns"),
          ("a small temple of white stone caught in giant roots", "wt_root_temple")]),
       ("WATER AND LIGHT", [
          ("a glowing teal spring in a ring of roots (the water inside)", "wt_glow_spring"),
          ("a curtain of glowing hanging roots", "wt_glow_curtain"),
          ("drifting motes of teal light around a seed of light", "wt_light_seed"),
          ("a root arch with a rune circle glowing under it", "wt_rune_arch"),
          ("a fallen glass pane, prismatic, leaning on a root", "wt_glass_pane"),
          ("candles and offerings in a hollow of roots", "wt_root_offerings")]),
       ("THE MOUNTAIN TEMPLE", [
          ("a temple hall with sweeping curved roofs, dark timber and gold trim", "sk_temple_hall"),
          ("a tiered pagoda tower", "sk_pagoda"),
          ("a temple gate with a curved roof", "sk_temple_gate"),
          ("a stone lantern", "sk_stone_lantern"),
          ("a blossom tree with white and gold flowers on twisted branches", "sk_blossom_tree"),
          ("a temple bell under a small roof", "sk_temple_bell")]),
       ("GOLD AND GLORY", [
          ("a golden throne under a tall carved canopy, a blue crystal in its back", "ae_golden_throne"),
          ("a gold-framed doorway with a glowing blue crystal keystone", "ae_gold_doorway"),
          ("a winged guardian statue with a spear, gold-trimmed", "ae_winged_guardian"),
          ("a gold stand holding a floating blue crystal", "ae_crystal_stand"),
          ("a tall gold candelabra of crystal flames", "ae_candelabra"),
          ("a banner of deep blue with a gold sigil of a winged crystal (no text)", "ae_sigil_banner")])])

sheet("SK19", "buildings", "airships, decks and rooms", "assets/buildings/",
      ["docs/zone_refs/sky_moodboard.jpg", "docs/zone_refs/aurelion_ref_spires.png",
       "assets/buildings/ae_survey_skiff.png"],
      AET + " This sheet is their AIRSHIPS (graceful ships of golden wood, white and brass with fin-like golden "
            "sails and glowing blue crystal engines) and the FURNISHINGS of their decks and great rooms: the bridge of "
            "an airship, the observatory, the engine room and the throne room.",
      "Objects keep their RELATIVE scale: the great airship, the galleon and the telescope are the largest sprites on "
      "the sheet; a chair, a gauge panel and a crate are small. Do not blow each one up to fill its own cell.",
      [("AIRSHIPS (seen whole, hovering)", [
          ("a great Aetherian airship, a galleon of golden wood and white with tall golden fin-sails", "ae_airship_great"),
          ("a sleek courier airship with swept fins", "ae_airship_courier"),
          ("a cargo airship with crates lashed to its deck", "ae_airship_cargo"),
          ("a small sky-skiff for two", "ae_skiff_small"),
          ("an Ascendancy warship, armoured with bronze, cannons along its side", "ae_airship_war"),
          ("a passenger liner airship with windows along its hull, for the long route to the ground",
           "ae_airship_liner")]),
       ("ON DECK", [
          ("a ship's wheel of gold and brass on a pedestal", "ae_ship_wheel"),
          ("a mast with a golden fin-sail", "ae_mast"),
          ("a deck cannon of brass and crystal", "ae_deck_cannon"),
          ("a capstan with coiled rope", "ae_capstan"),
          ("a gangway ramp with brass rails", "ae_gangway"),
          ("a stack of cargo crates and rope nets", "ae_deck_cargo")]),
       ("THE BRIDGE", [
          ("a curved console of brass dials and glowing blue crystal panels", "ae_bridge_console"),
          ("a captain's chair of blue leather and brass", "ae_captain_chair"),
          ("a navigator's table with a floating glowing map of islands", "ae_nav_table"),
          ("a speaking-tube column with brass bells", "ae_speaking_tube"),
          ("a gauge panel of dials and levers", "ae_gauge_panel"),
          ("a tall curved bridge window frame in brass (seen as a wall piece)", "ae_bridge_window")]),
       ("THE OBSERVATORY", [
          ("a giant brass telescope on a geared mount", "ae_great_telescope"),
          ("an armillary sphere of gold rings on a stand", "ae_armillary"),
          ("a desk of star charts and instruments", "ae_chart_desk"),
          ("a celestial globe glowing faintly", "ae_star_globe"),
          ("a shelf of brass instruments and books", "ae_instrument_shelf"),
          ("a lens-grinding bench with crystal lenses", "ae_lens_bench")]),
       ("THE ENGINE ROOM", [
          ("a great engine core, a crystal turning in brass rings, crackling", "ae_engine_core"),
          ("a bank of big turning gears", "ae_gear_bank"),
          ("a boiler of bronze with glowing blue windows", "ae_crystal_boiler"),
          ("a catwalk segment of iron grating with a rail", "ae_catwalk"),
          ("a hanging chain hoist with a crystal crate", "ae_chain_hoist"),
          ("a workbench of tools and a half-repaired construct arm", "ae_engine_bench")]),
       ("THE THRONE ROOM", [
          ("a gold-edged dais with three steps", "ae_dais"),
          ("a tall pillar of white marble wrapped with gold filigree", "ae_gold_pillar"),
          ("a gilded column with a winged capital", "ae_winged_column"),
          ("a long council table of white stone with high-backed chairs", "ae_council_table"),
          ("a fountain of light rising from a gold basin", "ae_light_fountain"),
          ("a tall arched window frame with gold tracery, sky beyond (seen as a wall piece)", "ae_arched_window")])])

# SK17 came back 6 x 6 (19 Nov 2026): the first 36 of its 48, in order. These are the 12 it left out.
_sk17 = next(x for x in SHEETS if x["key"] == "SK17")
_sk17_cells = [cell for _t, items in _sk17["rows"] for cell in items]
sheet("SK20", "tiles", "the storm walls and the mountain temple (what SK17 left out)", "assets/tiles/sky/ground/",
      ["assets/tiles/sky/ground/vy_rune_platform.png", "assets/tiles/sky/ground/sk_ruined_platform.png",
       "docs/zone_refs/sky_moodboard.jpg"],
      "These are the last floors and walls of the set: storm platforms above the clouds, and a mountain temple island "
      "of grey flagstones, red-brown steps, raked gravel and plaster walls above the cloud sea. Palette: storm grey with "
      "blue rune light, pale and weathered wood, grey temple stone, red-brown, white gravel, mountain green with white "
      "and gold blossoms.",
      None,
      [("STORM PLATFORMS", _sk17_cells[36:40]),
       ("THE MOUNTAIN TEMPLE ISLAND", _sk17_cells[40:44]),
       ("THE MOUNTAIN TEMPLE ISLAND, CONTINUED", _sk17_cells[44:48])],
      redo_of="SK17")

# ===================================================================================== BACKDROPS AND LIGHT
#: Not grids: one image each. How they're drawn: the cloud layers scroll behind the islands, slower than the ground (the
#: drop gets real depth); the light overlay is added over the screen; the panoramas are each zone's entry card.
BACKDROPS = [
    # Kyle, 19 Nov 2026: "merge the BK tileables to one prompt". The five tileable layers (first written as BK1 to BK5)
    # are one sheet of six cells now; BK6 to BK12 keep their numbers.
    ("BK1", "the sky layers: five cloud seas and the drifting wisps, one sheet (was BK1 to BK5)",
     "assets/tiles/sky/backdrop/",
     "Generate ONE texture sheet image, 1536x1024, laid out as a strict 3 columns x 2 rows grid = 6 separate square "
     "textures, each cell 512x512. Each cell is COMPLETELY FILLED by its texture, edge to edge, touching its neighbours "
     "with no gap. No border, no magenta, no frames, no gutters, no grid lines, no text, no labels, no numbers. EVERY "
     "CELL IS ITS OWN SEAMLESS TILEABLE TEXTURE: it must tile with itself on all four sides, with no single feature "
     "that obviously repeats, no vignette, no lighting gradient across the cell. All six are seen from STRAIGHT ABOVE, "
     "from very high up, looking down on cloud: no horizon, no sky above, no perspective, no islands, no birds, no "
     "objects, only cloud. Painterly semi-realistic, soft and luminous, matching a WoW Classic painted style.\n\n"
     "Cells are numbered row by row, left to right, top to bottom:\n\n"
     "Row 1: 1 THE GOLDEN CLOUD SEA: soft rolling billows of white and pale gold cloud in warm golden afternoon "
     "sunlight, gentle blue shadows between them, a few deeper gaps showing hazy blue far below; 2 THE MIDDAY CLOUD "
     "SEA: brilliant white billows in clear noon light, crisp soft blue shadows, a few gaps onto deep blue sky far "
     "below; 3 THE STORM CLOUD SEA: dark grey-blue billows lit from inside here and there by soft blue lightning glow, "
     "rain-dark gaps.\n\n"
     "Row 2: 4 THE DYING SKY: thin lavender and grey billows in a failing violet dusk, torn in places onto a deep "
     "violet-black void with faint stars, beautiful and sad; 5 THE DAWN CLOUD SEA: pale silver-blue billows in cool "
     "early light with a faint gold edge on their tops; 6 DRIFTING WISPS on PURE BLACK: soft white and pale gold cloud "
     "wisps and thin veils of mist scattered across a black cell, covering about a third of it, continuing across all "
     "four edges (this one is blended over the others, so black means clear)."),
    ("BK6", "the golden sunlight overlay", "assets/tiles/sky/backdrop/sun_rays.png",
     "Generate ONE wide image, 2048x1152, on a PURE BLACK background: warm golden sunlight streaming in from a low sun "
     "just beyond the TOP-RIGHT corner: a soft gold glow in that corner, long soft light shafts and rays fanning down "
     "and left across the image, fading out before the bottom-left, a little drifting golden haze and a few soft "
     "lens-glow circles. No sun disc fully inside the image, no objects, no clouds, no text. (This is added over the "
     "screen, so black means no light.)"),
    ("BK7", "the Sunward Crown, panorama", "assets/tiles/sky/panorama/pano_sunward_crown.png",
     "Generate ONE wide landscape painting, 1536x1024. The view from the crown of a colossal World Tree that has burst "
     "up through the clouds: in the foreground golden-leafed branches as wide as roads and a glimpse of a jungle troll "
     "lookout; beyond, an endless sea of white and gold cloud stretching to the horizon, and a huge golden sun low in "
     "the sky in the distance, its light pouring across the clouds; far away, the silhouettes of floating islands with "
     "waterfalls falling off them, and the faint shape of a graceful bronze-and-white airship approaching. "
     "Breathtaking, warm, hopeful. Painterly semi-realistic, in the style of WoW Classic loading-screen art. No "
     "people in focus, no text, no logo."),
    ("BK8", "the Celestial Expanse, panorama", "assets/tiles/sky/panorama/pano_celestial_expanse.png",
     "Generate ONE wide landscape painting, 1536x1024. A sky full of floating islands of pale stone and gold grass at "
     "different heights, sky rivers flowing between them and falling off their edges as waterfalls into the cloud sea "
     "far below; on the nearest island the colossal ruins of an ancient giant civilization, toppled columns and a "
     "great half-buried machine starting to glow blue-white; a golden sun in the distance; huge serene sky whales "
     "swimming through the clouds far off. Breathtaking, airy, ancient. Painterly semi-realistic, in the style of WoW "
     "Classic loading-screen art. No text, no logo."),
    # Kyle, 19 Nov 2026: "needs to be described in more detail!" Composed in layers, front to back, so the picture has
    # a real foreground, middle and distance rather than a list of features.
    ("BK9", "Aurelion, panorama", "assets/tiles/sky/panorama/pano_aurelion.png",
     "Generate ONE wide landscape painting, 1536x1024, matching the two attached pictures of the city in architecture, "
     "palette and grandeur. Painterly semi-realistic fantasy art in the style of a World of Warcraft loading screen: "
     "rich detail, soft painted edges, glowing light. No text, no logo, no watermark, no frame, nothing from our real "
     "world, no pink or magenta anywhere.\n\n"
     "THE SUBJECT: AURELION, the capital of the Aetherians, a people of the sky: the most incredible city in the sky, a "
     "suspended city of white marble, gold and glowing blue crystal floating high above an endless sea of cloud.\n\n"
     "CAMERA: a high aerial three-quarter view from just above and outside the city's outer edge, looking across the "
     "city toward the low sun. The city fills the centre and right two-thirds of the image; the left third opens onto "
     "sky, cloud and distant islands. Deep atmospheric perspective: crisp detail up close, softening into golden haze "
     "with distance.\n\n"
     "LIGHT: golden hour. A huge golden sun sits low near the horizon in the upper left, half veiled in thin cloud. Its "
     "warm light rakes across the whole city from the left: long soft god rays through the mist, gold rim light on "
     "every spire and dome, long cool blue shadows across the plazas. The city's own blue crystal light glows in "
     "windows, channels and engines and contrasts with the gold. The sky runs from warm gold and peach near the sun to "
     "soft clear blue at the top right; the cloud sea below is cream and gold, shadowed blue in its hollows.\n\n"
     "FOREGROUND (bottom of the image): the GRAND AVENUE runs from the bottom centre up into the heart of the city: a "
     "broad road of white marble edged with gold inlay, a straight channel of glowing blue water down its middle, "
     "slim crystal lamp posts and neat green trees in gold-rimmed planters along both sides. At its foot stand two "
     "colossal WINGED GUARDIAN STATUES of white stone trimmed in gold, wings raised, spears grounded. In the bottom "
     "left corner, the rocky edge of a floating district breaks away into empty air: its underside is rough pale rock "
     "with hanging roots and small blue crystals, and two long waterfalls pour off it down into the clouds, trailing "
     "mist and a faint rainbow. In the bottom right corner, the top of a great bronze DOCKING TOWER with curved landing "
     "arms, an elegant airship moored at one of them.\n\n"
     "MIDDLE GROUND (the heart of the city): the avenue opens into a great CIRCULAR PLAZA paved in white marble with "
     "concentric rings of gold inlaid in the stone, a fountain of glowing blue water at its centre, more winged "
     "guardian statues standing around its rim. Beyond it rises THE SPIRE PALACE, the tallest thing in the image, "
     "reaching almost to the top edge: a soaring cathedral-like tower of white marble ribbed with gold filigree, built "
     "of clustered spires that climb in tiers, every face cut with tall narrow lancet windows of glowing blue crystal, "
     "a great arched doorway at its foot glowing blue-white. Near its peak two enormous wing-like fins of white and "
     "gold sweep up and outward, and its tip is a blazing blue crystal finial. Three rings of floating stone blocks "
     "orbit slowly around the palace at different heights, catching the sun.\n\n"
     "THE DISTRICTS: around the palace, the city is built in CONCENTRIC RINGS of separate floating islands, each one a "
     "district standing on its own mass of rock, some higher and some lower. Each district is crowded with "
     "architecture: domed basilicas with gold-ribbed blue-grey domes and lanterns on top, columned rotundas, slender "
     "towers with crystal-tipped spires, terraced mansions with balconies and hanging gardens, all white marble and "
     "gold with blue crystal windows. Green trees grow on the terraces. Every district edge pours waterfalls: dozens "
     "of long white ribbons of water falling from the city into the clouds below, with mist and small rainbows where "
     "they catch the sun.\n\n"
     "BRIDGES: the districts are joined by long ARCHED BRIDGES of white stone and bronze, their rails hung with tall "
     "deep royal blue banners bearing a gold sigil of a winged crystal; the farthest islands are joined by thin arcs of "
     "glowing blue light instead. Tiny robed figures walk the bridges, showing the scale.\n\n"
     "THE COLOSSI: on the right side, two COLOSSAL STATUES of ancient Aetherian magisters, robed, with crystals growing "
     "from their shoulders and brows, stand on lower islands and hold whole platforms of buildings up on their "
     "shoulders and raised hands.\n\n"
     "BENEATH THE CITY: under the central island, partly visible through the gap between districts, hangs a VAST "
     "CRYSTAL ENGINE: a giant glowing blue crystal turning inside nested rings of bronze, held by chains and bronze "
     "arms, pouring a column of soft blue light down into the clouds.\n\n"
     "AIRSHIPS: several elegant AIRSHIPS fly around the city at different distances: long hulls of golden wood and "
     "white with brass trim, tall fin-like golden sails spread like wings, small glowing blue crystal engines at the "
     "stern. A large one comes in to dock in the foreground; smaller sky-skiffs cross between districts; two more are "
     "silhouetted against the sun.\n\n"
     "THE DISTANCE: on the left and far behind, smaller floating islands drift in the golden haze, a few with their own "
     "small castles and spires; the snow-touched tips of mountain peaks poke up through the cloud sea far away; the "
     "cloud sea stretches to a glowing horizon.\n\n"
     "A QUIET SIGN OF TROUBLE (small, far side, not dominating): one of the outermost rings on the far right is "
     "cracked and tilting, its towers leaning, held up only by straining chains, a few stones falling away into the "
     "clouds.\n\n"
     "THE FEELING: breathtaking, radiant and proud, the most beautiful place in the world, with the faint sadness of "
     "something beginning to fail. Titan architecture mixed with gnomish engineering, but far grander."),
    ("BK10", "the Talon Spires, panorama", "assets/tiles/sky/panorama/pano_talon_spires.png",
     "Generate ONE wide landscape painting, 1536x1024. Impossibly tall dark stone spires rising out of a storm-cloud "
     "sea, cities carved into their faces and built across enormous natural stone arches between them, great woven "
     "nests and red and gold banners whipping in the wind; avian warriors with feathered arms diving between the "
     "spires; lightning striking a copper-crowned temple on the highest peak; the golden sun breaking through the "
     "storm in the distance. Fierce and dramatic. Painterly semi-realistic, in the style of WoW Classic loading-screen "
     "art. No text, no logo."),
    ("BK11", "the Elder Citadels, panorama", "assets/tiles/sky/panorama/pano_elder_citadels.png",
     "Generate ONE wide landscape painting, 1536x1024. Massive floating citadels of cloud-white marble and grey granite "
     "hanging in a cold clear sky, joined by suspended bridges on chains, colossal temples and statues of giant "
     "ancestors, gravity stones floating in cradles of stone arms; cloud giants with stone-like skin and cloud-white "
     "hair walking a bridge, tiny by comparison to their works; a pale golden sun in the distance. Ancient, vast, "
     "awe-inspiring. Painterly semi-realistic, in the style of WoW Classic loading-screen art. No text, no logo."),
    ("BK12", "the Fading Firmament, panorama", "assets/tiles/sky/panorama/pano_fading_firmament.png",
     "Generate ONE wide landscape painting, 1536x1024. The dying heart of a sky civilization at violet dusk: floating "
     "islands breaking apart and falling, a dark crystal engine cracked in two, abandoned towers of pale stone and "
     "bronze leaning, a tear in the sky opening onto violet void with cloud pouring down into it; a few warships of "
     "white and bronze still in the air; one small island with a single living green tree; a dim golden sun sinking "
     "in the distance. Beautiful and tragic. Painterly semi-realistic, in the style of WoW Classic loading-screen art. "
     "No text, no logo."),
]


def render():
    out = ["# The Sky: art prompts, stage 2 (the art stock, 48-60 and a future sky start)", "",
           "Written by `tools/write_sky_art_prompts.py` (edit the script, not this file). For `docs/worldtree_brief.md`; "
           "the tree's own sheets (stage 1) are `docs/worldtree_art_prompts.md`.", "",
           "Kyle, 19 Nov 2026: \"Lets build up a stock of tiles and props for these future zones since chatgpt works "
           "best in massive batches\". So this is a stock: enough for the six sky maps from 48 to 60 (the Sunward "
           "Crown, the Celestial Expanse, Aurelion, the Talon Spires, the Elder Citadels, the Fading Firmament) and "
           "for a quiet sky starting zone later (meadows, farms, orchards, gentle animals: Kyle's idea for after, a sky "
           "race's 1-24 start ending at their capital with airships to Orgrimmar or the Undercity).", "",
           "Every prompt below is complete on its own: paste one block and nothing else. Nothing built from our world "
           "appears anywhere.", "",
           "| Sheet | What | Image | Grid (cell) | Key | Landed |", "|---|---|---|---|---|---|"]
    for s in SHEETS:
        img, grid, key = SIZE[s["kind"]]
        if s["kind"] == "tiles" and len(s["rows"]) != 6:
            c, r = len(s["rows"][0][1]), len(s["rows"])
            img, grid = f"{c * 256}x{r * 256}", f"{c} x {r} (256 x 256)"
        n = sum(len(items) for _t, items in s["rows"])
        out.append(f"| {s['key']} | {n} {s['title']} | {img} | {grid} | {key} | {LANDED.get(s['key'], '')} |")
    out += ["", "**Priority:** SK1 and SK2 (the ground is most of the look), BK1 and BK6 (the sky and the sun), "
            "SK3, SK5, SK15 and SK16 (Aurelion), SK10, then the rest in any order. Kyle's pictures: "
            "`docs/zone_refs/aurelion_ref_spires.png` and `aurelion_ref_domes.png` (Aurelion), "
            "`docs/zone_refs/sky_moodboard.jpg` (the mood board, twenty scenes: SK17 to SK19 come from it).", "", "**References to attach** (at most 3 per sheet; a path to a piece of another sheet means attach it "
            "once that sheet has landed; once a sheet lands, its own sliced pieces are the best references for the "
            "next one):"]
    for s in SHEETS:
        out.append(f"- {s['key']}: " + ", ".join(f"`{r}`" for r in s["refs"]))
    out.append("")
    for s in SHEETS:
        kind = s["kind"]
        head = HEAD[kind]
        if kind == "tiles":
            c, r = len(s["rows"][0][1]), len(s["rows"])
            head = head.replace("{W}", str(c * 256)).replace("{H}", str(r * 256)).replace("{C}", str(c)) \
                .replace("{R}", str(r)).replace("{N}", str(c * r))
        if s.get("redo_of"):
            out += ["---", "", f"*{s['key']} redraws what {s['redo_of']} left out; slice its cells under the same names.*"]
        out += ["---", "", f"## SHEET {s['key']}: {sum(len(i) for _t, i in s['rows'])} {s['title']} "
                f"({'NO magenta' if kind == 'tiles' else 'MAGENTA KEY'})", "", "```", head, "",
                f"Setting: {SKY} {s['setting']}"]
        if s["scale"]:
            out += ["", s["scale"]]
        out += ["", f"{NOUN[kind]} are numbered row by row, left to right, top to bottom:", ""]
        k = 1
        lines = []
        for title, items in s["rows"]:
            parts = []
            for text, _id in items:
                parts.append(f"{k} {text}")
                k += 1
            label = title if kind != "landmarks" else title.title()
            lines.append(f"{label}: " + "; ".join(parts) + ".")
        out += ["\n\n".join(lines), "```", "", f"### Slice order (`{s['out']}`)", ""]
        cols = len(s["rows"][0][1])
        out.append("| row | " + " | ".join(str(c + 1) for c in range(cols)) + " |")
        out.append("|---|" + "---|" * cols)
        for r, (_t, items) in enumerate(s["rows"]):
            out.append(f"| {r + 1} | " + " | ".join(i for _x, i in items) + " |")
        out.append("")
    out += ["---", "", "## BACKDROPS AND LIGHT (one image each, not grids)", "",
            "How they're drawn: BK1's first five cells are the far cloud sea, scrolled behind the islands slower than the "
            "ground so the drop has real depth (one per mood: gold for the Crown and Aurelion, day for the Expanse, "
            "storm for the Spires, dusk for the Firmament, dawn for a quiet start). Its sixth cell, the wisps, drifts "
            "over that a little faster. BK6 is added over the whole "
            "screen: the golden sun in the distance. BK7 to BK12 are each zone's entry card, the view people remember.",
            ""]
    for key, title, path, prompt in BACKDROPS:
        out += [f"### {key}: {title} (`{path}`)" + (" (landed 19 Nov)" if key in BK_LANDED else ""), "", "```", prompt,
                "```", ""]
    return "\n".join(out)


def check():
    ids = [i for s in SHEETS if not s.get("redo_of") for _t, items in s["rows"] for _x, i in items]
    dup = {i for i in ids if ids.count(i) > 1}
    assert not dup, f"duplicate ids: {sorted(dup)}"
    want = {"tiles": (6, 8), "props": (6, 6), "buildings": (6, 6), "landmarks": (3, 3), "creatures": (6, 6)}
    for s in SHEETS:
        rows, cols = want[s["kind"]]
        if s.get("redo_of"):
            rows, cols = len(s["rows"]), len(s["rows"][0][1])
        assert len(s["rows"]) == rows, (s["key"], len(s["rows"]))
        for t, items in s["rows"]:
            assert len(items) == cols, (s["key"], t, len(items))
        for _t, items in s["rows"]:
            for text, _i in items:
                assert "pink" not in text.lower() and "magenta" not in text.lower(), (s["key"], text)
    return len(ids)


if __name__ == "__main__":
    n = check()
    OUT.write_text(render() + "\n", encoding="utf-8")
    print(f"{len(SHEETS)} sheets, {n} cells -> {OUT.relative_to(ROOT)}")
