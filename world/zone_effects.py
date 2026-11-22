"""Environment effects across Azeroth (docs/environment_effects_art_prompts.md, EFX1 to EFX10).

Kyle, 21 Nov 2026: "I gave you a shit load of visual effect art. You used it in the SC starting zone and also the sky
zones. Can you start to incorporate it through azeroth too." And: "let's test it with ONE zone!" Eastern Tirisfal went
first; once Kyle had seen it, the Underdark, Ashenvale and Azshara followed, then every other overworld map and town
in Azeroth through one preset per kind of country, then every cave, dungeon and hidden place, each assessed on its
own (21 Nov 2026). The standing rule for all of it: "supplement zones but NOT dominate them. They should complement the zone."

A map's effects are five optional layers, drawn by ui/tilemap_renderer.py over the world in this order:

  shade      {"layer": "shade_haunted", "strength": 0.3}, or a list     multiplied: a vignette, or with "tile" a
                                                                       drifting pattern (leaf shadow, cloud shadow)
  weather    [{"layer": "atm_ground_fog", "strength": 0.3, ...}, ...]   scrolling layers, added, each at its own speed
  particles  {"sprites": ["p_spore_plague"], "count": 6, ...}          small things drifting across the screen
  glows      {"strength": 0.8}                                         a pool of light round every lantern, brazier,
                                                                       campfire and cauldron on the map
  life       {"flyers": ["life_crow", "shadow_wyvern"], ...}           now and then a bird, or a shadow far above
  light      {"layer": "light_moonlight", "strength": 0.2}             added over everything, breathing slowly

Maps that set their own (Dawnhaven's three, the sky maps) are left alone.
"""

ZONES = {
    # Tirisfal: the Forsaken's grey country, cold and damp. A haunted vignette and a cool wet cast over everything,
    # low fog lying on the ground and drifting very slowly, thin moonlight through it, and the plague cauldrons
    # throwing their green into the murk. Kyle, 21 Nov 2026: "Let's stick with effects before we play with movement.
    # Fog, sun, dampness etc. Lights", so no particles or passing birds yet.
    "Eastern Tirisfal": {
        "shade": {"layer": "shade_haunted", "strength": 0.28},
        "weather": [
            {"layer": "atm_ground_fog", "strength": 0.32, "floor": 0.3, "tile": 18, "speed": (-4, 1), "parallax": 1.0},
        ],
        "glows": {"strength": 0.75},
        "light": {"layer": "light_moonlight", "strength": 0.16, "breathe": 0.1},
    },
}

# The Crystalline Underdark, its town and its two caves. Kyle, 21 Nov 2026: "I envision it as a gorgeous glowing
# mushroom and crystal biome." The cavern is dimmed a little and cooled toward blue so the light has somewhere to show,
# a faint arcane haze lies in it, and every mushroom, crystal, glow pool and spore vent lights the stone round it in its
# own colour. The big caps glow wide and soft; the small ones are little pools.
UNDERDARK_GLOWS = [
    (("crystal_cyan", "lattice", "glow_pool"), (70, 220, 255), 2.6, 0.5),
    (("crystal", "geode"), (190, 110, 255), 2.8, 0.45),
    (("shroom_tall_violet",), (200, 90, 255), 2.2, 0.3),
    (("shroom_cluster_blue", "shroom_small"), (80, 160, 255), 2.4, 0.55),
    (("shroom_canopy",), (60, 230, 200), 3.0, 0.4),
    (("fungal_node", "fungal_shelf", "shelf_fungus"), (90, 230, 170), 1.4, 0.5),
    (("spore_vent",), (140, 255, 120), 2.2, 0.5),
    (("arcane_brazier", "arcane_well"), (150, 140, 255), 3.0, 0.4),
]
UNDERDARK = {
    "shade": [{"layer": "shade_cave_vignette", "strength": 0.28},
              {"layer": "shade_night", "strength": 0.1}],
    "weather": [{"layer": "atm_void_wisps", "strength": 0.22, "floor": 0.25, "tile": 18, "speed": (-3, 1)}],
    "glows": {"strength": 0.85, "kinds": UNDERDARK_GLOWS},
    "light": {"layer": "light_crystal_cave", "strength": 0.2, "breathe": 0.1},
}
ZONES["The Crystalline Underdark"] = UNDERDARK
ZONES["Kael's Bastion"] = dict(UNDERDARK, shade=[{"layer": "shade_night", "strength": 0.14}])
ZONES["The Hollow Geode"] = dict(UNDERDARK, shade=[{"layer": "shade_cave_vignette", "strength": 0.38},
                                                   {"layer": "shade_night", "strength": 0.14}])
ZONES["The Deep Bloom"] = ZONES["The Hollow Geode"]

# Ashenvale: the night elves' twilight forest. Cool moonlight coming down through the canopy, leaf shadow on the floor,
# a few fireflies in the dusk, and the moon lanterns, furbolg bonfires and camp fires lighting their clearings.
ASHENVALE = {
    "shade": {"layer": "shade_canopy_dapple", "strength": 0.24, "tile": 11, "drift": (1.2, 0.3)},
    "weather": [{"layer": "atm_fireflies", "strength": 0.4, "floor": 0.15, "tile": 16, "speed": (-2, -1)}],
    "glows": {"strength": 0.75},
    "light": {"layer": "light_moonlight", "strength": 0.2, "breathe": 0.1},
}
# Azshara: forever autumn on the old high-elf coast. Warm low sun slanting through red leaves, leaf shadow, a few gold
# motes hanging in the light, and the braziers and lanterns of the ruins and camps.
AZSHARA = {
    "shade": {"layer": "shade_canopy_dapple", "strength": 0.2, "tile": 11, "drift": (1.2, 0.3)},
    "weather": [{"layer": "atm_golden_motes", "strength": 0.3, "floor": 0.15, "tile": 16, "speed": (-2, -1)}],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_autumn_rays", "strength": 0.3, "breathe": 0.12},
}
#: towns keep the light and the glows, with less shadow and no motes, so the people and the buildings stay clear
def _town(fx):
    """Towns keep the light and the glows, with half the shadow and no weather or sky events, so the people and the
    buildings stay clear."""
    sh = fx.get("shade")
    half = lambda d: dict(d, strength=d["strength"] * 0.5)  # noqa: E731
    out = {k: v for k, v in fx.items() if k not in ("weather", "events")}
    if sh:
        out["shade"] = [half(d) for d in sh] if isinstance(sh, list) else half(sh)
    return out


for _n in ("Ashenvale West", "Ashenvale East"):
    ZONES[_n] = ASHENVALE
for _n in ("Astranaar", "Zoram Strand", "Splintertree Post"):
    ZONES[_n] = _town(ASHENVALE)
for _n in ("West Azshara", "Central Azshara", "East Azshara"):
    ZONES[_n] = AZSHARA
for _n in ("Talrendis Landing", "Timbermaw Hold"):
    ZONES[_n] = _town(AZSHARA)

# ---------------------------------------------------------------------------------------------------------- the rest
# Kyle, 21 Nov 2026: "Stars? Light? Wind? Heatwave?", and the standing rule: "supplement zones but NOT dominate them".
# One preset per kind of country, each a light touch. The heat shimmer is a light overlay used as a scrolling layer.
_shimmer = lambda k: {"layer": "sky_heat_shimmer", "folder": "light", "strength": k, "floor": 0.1,  # noqa: E731
                      "tile": 14, "speed": (0, -5)}
DESERT = {          # Durotar, the Needles' canyons: hard noon light and heat coming off the ground
    "weather": [_shimmer(0.16)],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_desert_glare", "strength": 0.2, "breathe": 0.1},
}
SAVANNA = {         # the Barrens: big sky, cloud shadow sliding over the grass, a little heat
    "shade": {"layer": "shade_cloud_shadows", "strength": 0.18, "tile": 16, "drift": (3.0, 1.0)},
    "weather": [_shimmer(0.1)],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_desert_glare", "strength": 0.14, "breathe": 0.1},
}
DUNES = {           # Tanaris and the salt flats: a dusty haze, strong glare and heavy shimmer
    "shade": {"layer": "shade_dust_haze", "strength": 0.14},
    "weather": [_shimmer(0.22)],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_desert_glare", "strength": 0.26, "breathe": 0.1},
}
ASPEN = {           # the Aspen Wilderness: gold aspens in low sun
    "shade": {"layer": "shade_canopy_dapple", "strength": 0.18, "tile": 11, "drift": (1.2, 0.3)},
    "weather": [{"layer": "atm_golden_motes", "strength": 0.24, "floor": 0.15, "tile": 16, "speed": (-2, -1)}],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_autumn_rays", "strength": 0.24, "breathe": 0.12},
}
TIRISFAL = ZONES["Eastern Tirisfal"]
PINEWOOD = {        # Silverpine and Fenris: dark pines, low fog, cold light
    "shade": {"layer": "shade_canopy_dapple", "strength": 0.2, "tile": 11, "drift": (1.0, 0.3)},
    "weather": [{"layer": "atm_ground_fog", "strength": 0.28, "floor": 0.3, "tile": 18, "speed": (-4, 1)}],
    "glows": {"strength": 0.75},
    "light": {"layer": "light_moonlight", "strength": 0.14, "breathe": 0.1},
}
HILLS = {           # Hillsbrad and Arathi: open country, cloud shadow, soft morning light
    "shade": {"layer": "shade_cloud_shadows", "strength": 0.2, "tile": 16, "drift": (3.0, 1.0)},
    "glows": {"strength": 0.7},
    "light": {"layer": "light_dawn", "strength": 0.14, "breathe": 0.1},
}
PLAGUE = {          # the Plaguelands: a sick yellow-green haze in the low places and a miasma in the light
    "shade": {"layer": "shade_haunted", "strength": 0.28},
    "weather": [{"layer": "atm_plague_fog", "strength": 0.2, "floor": 0.3, "tile": 18, "speed": (-3, 1)}],
    "glows": {"strength": 0.75},
    "light": {"layer": "light_plague_miasma", "strength": 0.16, "breathe": 0.12},
}
# Deadwind Pass is a fallout zone, not a haunted wood (Kyle, 21 Nov 2026: "Why is deadwind pass haunted? It's more
# complex. Look at the liquidators"). docs/deadwind_brief.md: the Seep's sick green-yellow glow gets into soil, water
# and flesh; time is broken round the tear; the colours are dead grey-brown, sickly green-yellow, bruise purple and
# rust, and the only warm light is the Watch's pyre. So: a bruised vignette, a low yellow-green haze, fallout dust
# hanging in the air, the Seep glowing up from below, and everything that's contaminated lighting its ground green.
# Round the rupture in the east the tear itself pulses now and then.
DEADWIND_GLOWS = [
    (("seep_pool", "seep_boulder", "glow_crater", "slag", "fume_vent", "egg_sacs", "tumour", "eye_mushroom",
      "flesh_pods", "flesh_mass", "flesh_sac", "black_well", "ooze", "heart_mass", "wound_pit", "eye_cluster",
      "open_pod"), (170, 230, 60), 2.6, 0.5),
    (("fz_crystal_pillar", "fz_glass_shard", "stopped_blast"), (180, 120, 255), 2.4, 0.45),
    (("air_tear", "rift_crack", "time_doorway", "false_reflection", "glass_spire", "floating_rock"),
     (180, 120, 255), 2.6, 0.45),
    (("containment_spire",), (120, 220, 255), 3.0, 0.3),
    (("copper_still", "vial_rack", "laboratory"), (150, 230, 70), 2.0, 0.6),
    (("great_pyre", "burn_bin"), (255, 140, 50), 3.6, 0.55),
    (("stopped_fire", "ember_ash"), (255, 120, 40), 2.0, 0.6),
]
DEADWIND = {
    "shade": {"layer": "shade_haunted", "strength": 0.22},
    "weather": [{"layer": "atm_plague_fog", "strength": 0.16, "floor": 0.3, "tile": 18, "speed": (-3, 1)},
                {"layer": "wx_ashfall", "strength": 0.14, "floor": 0.12, "tile": 14, "speed": (-3, 6)}],
    "glows": {"strength": 0.8, "kinds": DEADWIND_GLOWS},
    "light": {"layer": "light_plague_miasma", "strength": 0.16, "breathe": 0.12},
}
DEADWIND_RUPTURE = dict(
    DEADWIND,
    shade={"layer": "shade_haunted", "strength": 0.26},
    weather=[{"layer": "atm_plague_fog", "strength": 0.22, "floor": 0.3, "tile": 18, "speed": (-3, 1)},
             {"layer": "wx_ashfall", "strength": 0.16, "floor": 0.12, "tile": 14, "speed": (-3, 6)}],
    events=[{"layer": "sky_rift_glow", "every": (25, 50), "dur": 1.2, "strength": 0.22, "flash": True}],
    light={"layer": "light_plague_miasma", "strength": 0.22, "breathe": 0.15},
)
FEL = {             # Felwood: the corruption lights the mist green from below
    "shade": {"layer": "shade_haunted", "strength": 0.26},
    "weather": [{"layer": "atm_swamp_mist", "strength": 0.24, "floor": 0.25, "tile": 18, "speed": (-3, 1)}],
    "glows": {"strength": 0.8},
    "light": {"layer": "light_fel_glow", "strength": 0.2, "breathe": 0.15},
}
HIGHWOOD = {        # Stonetalon's west: tall old trees, gold light down through them
    "shade": {"layer": "shade_canopy_dapple", "strength": 0.2, "tile": 11, "drift": (1.2, 0.3)},
    "glows": {"strength": 0.7},
    "light": {"layer": "light_golden_canopy", "strength": 0.22, "breathe": 0.12},
}
BLASTED = {         # Stonetalon's east, burned out: ash still coming down, embers glowing low
    "shade": {"layer": "shade_dust_haze", "strength": 0.12},
    "weather": [{"layer": "wx_ashfall", "strength": 0.24, "floor": 0.12, "tile": 14, "speed": (-6, 14)}],
    "glows": {"strength": 0.8},
    "light": {"layer": "light_ember_underglow", "strength": 0.14, "breathe": 0.15},
}
JUNGLE = {          # Stranglethorn, Feralas, the World Tree: shafts of light through a thick canopy, damp mist
    "shade": {"layer": "shade_jungle_canopy", "strength": 0.2, "tile": 12, "drift": (1.0, 0.3)},
    "weather": [{"layer": "atm_swamp_mist", "strength": 0.14, "floor": 0.3, "tile": 18, "speed": (-3, 1)}],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_jungle_shafts", "strength": 0.24, "breathe": 0.12},
}
ISLES = {           # the Echo Isles and the Crossing: bright sea light, cloud shadow, a little spray
    "shade": {"layer": "shade_cloud_shadows", "strength": 0.15, "tile": 16, "drift": (3.0, 1.0)},
    "weather": [{"layer": "wx_sea_spray", "strength": 0.12, "floor": 0.2, "tile": 14, "speed": (-20, 4)}],
    "glows": {"strength": 0.7},
    "light": {"layer": "light_sun_bloom", "strength": 0.2, "breathe": 0.1},
}
STORM = {           # the Tempest Shallows: storm gloom, light rain and lightning now and then
    "shade": {"layer": "shade_storm_gloom", "strength": 0.3},
    "weather": [{"layer": "wx_rain_light", "strength": 0.26, "floor": 0.1, "tile": 14, "speed": (-40, 220)}],
    "glows": {"strength": 0.8},
    "events": [{"layer": "sky_lightning_flash", "every": (18, 40), "dur": 0.9, "strength": 0.4, "flash": True}],
    "light": {"layer": "light_overcast", "strength": 0.08, "breathe": 0.1},
}
EMBERS = {          # the Ashen Reach: volcanic, ash in the air and fire under everything
    "shade": {"layer": "shade_dust_haze", "strength": 0.14},
    "weather": [{"layer": "wx_ashfall", "strength": 0.26, "floor": 0.12, "tile": 14, "speed": (-6, 14)}],
    "glows": {"strength": 0.8},
    "light": {"layer": "light_ember_underglow", "strength": 0.22, "breathe": 0.15},
}
MOONGLADE = {       # Moonglade: always twilight, fireflies, moonlight, and a shooting star now and then
    "shade": {"layer": "shade_night", "strength": 0.22},
    "weather": [{"layer": "atm_fireflies", "strength": 0.4, "floor": 0.15, "tile": 16, "speed": (-2, -1)}],
    "glows": {"strength": 0.8},
    "events": [{"layer": "sky_shooting_stars", "every": (20, 45), "dur": 1.8, "strength": 0.55},
               {"layer": "sky_falling_star", "every": (60, 120), "dur": 2.2, "strength": 0.5}],
    "light": {"layer": "light_moonlight", "strength": 0.26, "breathe": 0.12},
}
UNDERCITY = {       # under the ruins: a dark vault lit green by the canals and the cauldrons
    "shade": {"layer": "shade_cave_vignette", "strength": 0.3},
    "glows": {"strength": 0.8},
    "light": {"layer": "light_plague_miasma", "strength": 0.14, "breathe": 0.12},
}

for _p, _maps, _towns in (
    (DESERT, ("Valley of Trials", "Durotar", "Southern Thousand Needles"),
     ("Razor Hill", "Orgrimmar", "Ratchet", "Freewind Post", "Zeppelin Tower")),
    (SAVANNA, ("Northern Barrens", "Central Barrens", "Southern Barrens"), ("Crossroads", "Camp Taurajo")),
    (DUNES, ("Northern Tanaris", "The Abyssal Sands", "The Black Strand", "Glittervein", "The Shimmering Flats"),
     ("Steamwheedle Port", "Fourth Peg", "Onyxhollow", "Saltwheel")),
    (ASPEN, ("The Aspen Wilderness",), ()),
    (TIRISFAL, ("Western Tirisfal", "Deathknell", "Scarlet Monastery Grounds"),
     ("Brill", "Undercity Zeppelin Tower")),
    (PINEWOOD, ("Silverpine North", "Silverpine South", "Fenris Isle"), ("The Sepulcher", "Bloodmoon Village")),
    (HILLS, ("Eastern Hillsbrad", "Western Hillsbrad", "Arathi West", "Arathi Central", "Arathi East"),
     ("Tarren Mill", "Southshore", "Hammerfall", "Saltspur Landing")),
    (PLAGUE, ("Western Plaguelands South", "Western Plaguelands North", "Eastern Plaguelands West",
              "Eastern Plaguelands East"), ("The Bulwark", "The Pale Watch", "Light's Hope Chapel")),
    (DEADWIND, ("Deadwind West",), ("Ariden's Watch",)),
    (DEADWIND_RUPTURE, ("Deadwind East",), ()),
    (FEL, ("North Felwood", "South Felwood"), ("Emerald Sanctuary", "Timbermaw Tunnel")),
    (HIGHWOOD, ("Stonetalon West",), ("Sun Rock Retreat",)),
    (BLASTED, ("Stonetalon East",), ()),
    (JUNGLE, ("Northern Stranglethorn", "Central Stranglethorn", "Southern Stranglethorn", "The High Wilderness",
              "The Forgotten Coast", "The Twin Colossals", "Rootwater Isle", "The Lower Boughs", "The Middle Boughs",
              "The Upper Boughs", "The Cloudbreak"),
     ("Grom'gol", "Booty Bay", "Grom'gol Zeppelin Tower", "Camp Mojache", "Feathermoon Stronghold",
      "The Great Settlement")),
    (ISLES, ("Echo Isles", "The Crossing", "The Bloodsail Anchorage"), ()),
    (STORM, ("Tempest Shallows",), ()),
    (EMBERS, ("The Ashen Reach",), ("Cinderwharf",)),
):
    for _n in _maps:
        ZONES[_n] = _p
    for _n in _towns:
        ZONES[_n] = _town(_p)
ZONES["Moonglade"] = MOONGLADE
ZONES["Undercity"] = UNDERCITY

# ---------------------------------------------------------------------------------------------- caves and dungeons
# Kyle, 21 Nov 2026: "we can do some caves and skull/frontier zones. Since the hidden zones don't always follow logic
# they need to be assessed properly." Each cave below was looked at on its own (its props, its name, what it's for)
# and given the treatment that fits it, not its parent's. Underground, the props carry most of the light: the
# vignette keeps the edges dark so the braziers, crystals and glowing things have somewhere to show.
def _cave(vig=0.26, **extra):
    fx = {"shade": [{"layer": "shade_cave_vignette", "strength": vig}], "glows": {"strength": 0.8}}
    tint = extra.pop("tint", None)
    if tint:
        fx["shade"].append(tint)
    fx.update(extra)
    return fx


_fog = lambda layer, k, floor=0.3: {"layer": layer, "strength": k, "floor": floor, "tile": 18,  # noqa: E731
                                    "speed": (-3, 1)}
_lt = lambda layer, k: {"layer": layer, "strength": k, "breathe": 0.12}  # noqa: E731
EARTH = _cave()                                                        # dens, burrows, beast caves
MINE = _cave(0.3, tint={"layer": "shade_dust_haze", "strength": 0.08})    # dust in the lamplight
DAYLIT = _cave(0.2, light=_lt("light_cave_skylight", 0.18))            # open to the sky somewhere
FIRE = _cave(0.28, weather=[_fog("atm_steam", 0.16, 0.25)], light=_lt("light_ember_underglow", 0.2))
GROTTO = _cave(0.28, tint={"layer": "shade_underwater", "strength": 0.14})  # sea caves: a cool green-blue cast
DROWNED = _cave(0.28, tint={"layer": "shade_underwater", "strength": 0.18})
CRYPT = _cave(0.28, tint={"layer": "shade_haunted", "strength": 0.16}, weather=[_fog("atm_ground_fog", 0.18)])
PLAGUE_CAVE = _cave(0.28, tint={"layer": "shade_haunted", "strength": 0.16}, weather=[_fog("atm_plague_fog", 0.16)],
                    light=_lt("light_plague_miasma", 0.12))
HALLS = _cave(0.24)                                                    # keeps, monasteries: built and lit rooms
CATHEDRAL = _cave(0.22, light=_lt("light_holy_column", 0.14))
FEL_CAVE = _cave(0.3, light=_lt("light_fel_glow", 0.14))
NEST = _cave(0.3, tint={"layer": "shade_haunted", "strength": 0.12})  # webs and hives: close and dark
HIVE = _cave(0.28, tint={"layer": "shade_dust_haze", "strength": 0.1})
ICE = _cave(0.28, tint={"layer": "shade_night", "strength": 0.1}, light=_lt("light_winter_sun", 0.14))
CRYSTAL = _cave(0.3, tint={"layer": "shade_night", "strength": 0.1}, light=_lt("light_crystal_cave", 0.16))
GREEN = _cave(0.26, weather=[_fog("atm_swamp_mist", 0.14)], light=_lt("light_cave_skylight", 0.12))
MOONWELL = _cave(0.26, light=_lt("light_moonlight", 0.16))
SHIP = _cave(0.28)
ARCANE = _cave(0.26, light=_lt("light_arcane_shimmer", 0.12))
STORM_CAVE = _cave(0.26, weather=[{"layer": "wx_rain_light", "strength": 0.16, "floor": 0.1, "tile": 14,
                                   "speed": (-40, 220)}],
                   events=[{"layer": "sky_lightning_flash", "every": (15, 35), "dur": 0.9, "strength": 0.35,
                            "flash": True}])
FADED = _cave(0.28, weather=[_fog("atm_void_wisps", 0.14, 0.25)], light=_lt("light_dusk", 0.12))
FOUNDRY = _cave(0.26, weather=[_fog("atm_steam", 0.12, 0.25)], light=_lt("light_ember_underglow", 0.12))
BLOODY = _cave(0.32, light=_lt("light_ember_underglow", 0.12))
DEEP_DARK = _cave(0.36, tint={"layer": "shade_underwater", "strength": 0.14})
DREAM = _cave(0.28, weather=[_fog("atm_swamp_mist", 0.16)], light=_lt("light_arcane_shimmer", 0.1))
FALLOUT_CAVE = lambda k: _cave(  # noqa: E731
    0.28, tint={"layer": "shade_haunted", "strength": 0.12}, weather=[_fog("atm_plague_fog", 0.12 + k * 0.3)],
    glows={"strength": 0.85, "kinds": DEADWIND_GLOWS}, light=_lt("light_plague_miasma", 0.14 + k * 0.4))

CAVES = [
    (EARTH, ("The Den", "Dustwind Cave", "Boulder'gor", "Boulderfist Hall", "Razorfen Kraul", "The Broodspiral",
            "The Thornheart Warren")),
    (MINE, ("Azurelode Mine", "Boulder Lode Mine", "Windshear Mine", "Drywhisker Deeps")),
    (DAYLIT, ("Thunder Ridge", "Drygulch Ravine", "Serena's Hollow", "The Eldest's Crown", "The Eldest Sequoia",
             "Shriekhollow", "The Sunken Kraal")),
    (FIRE, ("Ragefire Chasm", "The Emberdeep", "The Ashvent", "The Cinderwell")),
    (GROTTO, ("Sunken Grotto of the Deep", "The Tidewrack", "Wrackline Hold", "Sunken Temple Grotto",
             "Hetaera's Grotto", "The Lashings", "The Drownbell")),
    (DROWNED, ("Blackfathom Deeps", "The Drowned Shrine", "The Drowned Barrow", "The Drowning Floor",
              "The Drowned Palace", "The Drowned Palace: The Queen's Vault")),
    (CRYPT, ("Scholomance", "Scholomance: Lower Halls", "Scarlet Crypt", "The Marris Crypt", "Shadowfang Keep",
            "The Ossuary Below", "Scourge Cave")),
    (PLAGUE_CAVE, ("Stratholme", "Stratholme: Service Entrance", "Stratholme: Slaughter Square", "Plague Depths",
                  "The Writhing Deep", "The Weeping Cave", "The Bone Mines")),
    (HALLS, ("Hearthglen", "Hearthglen: Mardenholde Keep", "Scarlet Monastery: Graveyard",
            "Scarlet Monastery: Library", "Scarlet Monastery: Armory", "Durnholde Keep", "Dun Garok",
            "Stromgarde Keep", "Tiragarde Keep", "Ambermill Tower", "Gurbashi Arena", "Zalazane's Hollow")),
    (CATHEDRAL, ("Scarlet Monastery: Cathedral",)),
    (FEL_CAVE, ("Burning Blade Coven", "Skull Rock", "Jaedenar", "Shadowpine Altar", "Haldarr Den", "Grom's Rest",
               "The Rotroot Deeps")),
    (NEST, ("Night Web's Hollow", "Widow's Lair", "The Zukk'ash Hive")),
    (HIVE, ("The Royal Hive", "The Undercrust", "The Dry Deep")),
    (ICE, ("The Frostward Descent", "The Weeping Ice", "Howling Barrows")),
    (CRYSTAL, ("The Mother Vein", "The Cistern")),
    (GREEN, ("Wailing Caverns", "Rotvine Hollow", "Veilfall Cave", "The Knothollow", "The World-Root Hollow")),
    (MOONWELL, ("Moonwell Hollow",)),
    (SHIP, ("The Bloodsail Raider", "The Raider's Hold", "The Galleon's Hold", "The Captain's Cabin")),
    (ARCANE, ("The Golem Vault", "The Keel", "The Ascendant Spire", "The Ascendant Spire: The Command Spire")),
    (STORM_CAVE, ("The Stormsplit", "The Storm-Well")),
    (FADED, ("The Hearthdeep", "The Wellspring", "The Hollow Engine")),
    (FOUNDRY, ("The Gravity Foundry", "The Gravity Foundry: The Keelworks", "Khaz Varun, the Black Hollow")),
    (BLOODY, ("The Blood Pits",)),
    (DEEP_DARK, ("The Lightless Reach",)),
    (DREAM, ("The Dreaming Root",)),
]
for _p, _names in CAVES:
    for _n in _names:
        ZONES[_n] = _p
ZONES["The Widows' Nest"] = FALLOUT_CAVE(0.0)
ZONES["The Drowned Seep"] = FALLOUT_CAVE(0.15)
ZONES["The Exclusion Zone"] = FALLOUT_CAVE(0.1)
ZONES["The Exclusion Zone: The Reactor Hall"] = FALLOUT_CAVE(0.2)
ZONES["The Exclusion Zone: The Foot"] = dict(FALLOUT_CAVE(0.3), events=[
    {"layer": "sky_rift_glow", "every": (20, 40), "dur": 1.2, "strength": 0.24, "flash": True}])
ZONES["The Galleon's Weather Deck"] = ISLES          # out on deck, under the open sky
ZONES["Rocky Pass"] = ASPEN                        # a pass through the aspens, open to the sky

# ------------------------------------------------------------------------------------- the hidden places (spoilers)
# Each from its own brief in its builder, never from the map it hides in: they don't follow their neighbours' logic.
_storm_bolts = [{"layer": "sky_lightning_flash", "every": (10, 25), "dur": 0.9, "strength": 0.4, "flash": True},
                {"layer": "sky_lightning_a", "every": (25, 50), "dur": 0.6, "strength": 0.5, "flash": True},
                {"layer": "sky_lightning_b", "every": (25, 50), "dur": 0.6, "strength": 0.5, "flash": True}]
_rainbow = {"layer": "sky_rainbow", "every": (70, 140), "dur": 8.0, "strength": 0.28}
HIDDEN = {
    # grey sand, grey water, the old dead under it
    "The Saltgrave": {"shade": {"layer": "shade_storm_gloom", "strength": 0.22},
                      "weather": [_fog("atm_ground_fog", 0.24), {"layer": "wx_sea_spray", "strength": 0.1,
                                  "floor": 0.2, "tile": 14, "speed": (-20, 4)}],
                      "glows": {"strength": 0.8}, "light": _lt("light_overcast", 0.06)},
    # sand fired to glass, fire still walking about
    "The Glasswaste": {"shade": {"layer": "shade_dust_haze", "strength": 0.12}, "weather": [_shimmer(0.26)],
                       "glows": {"strength": 0.8}, "light": _lt("light_desert_glare", 0.24)},
    # a dead pine wood in a fog that never lifts
    "The Weeping Pines": {"shade": [{"layer": "shade_haunted", "strength": 0.28},
                                    {"layer": "shade_canopy_dapple", "strength": 0.16, "tile": 11,
                                     "drift": (1.0, 0.3)}],
                          "weather": [_fog("atm_ground_fog", 0.38), _fog("atm_fog_bank", 0.12, 0.35)],
                          "glows": {"strength": 0.8}, "light": _lt("light_moonlight", 0.12)},
    # mangroves in water gone green with sap
    "The Tanglewood Shoals": dict(JUNGLE, weather=[_fog("atm_swamp_mist", 0.24)]),
    # a lagoon where drowned gods are still listening
    "The Drowned Idols": dict(JUNGLE, shade=[JUNGLE["shade"], {"layer": "shade_haunted", "strength": 0.14}],
                              weather=[_fog("atm_swamp_mist", 0.2)]),
    # a caravan under the dunes, the sand moving
    "The Buried Caravan": dict(DUNES, weather=[_shimmer(0.18), {"layer": "wx_sandstorm", "strength": 0.12,
                                               "floor": 0.15, "tile": 16, "speed": (-30, 4)}]),
    # a grove the moon has never once seen
    "The Moonless Glade": {"shade": [{"layer": "shade_night", "strength": 0.3},
                                     {"layer": "shade_haunted", "strength": 0.2}],
                           "weather": [_fog("atm_void_wisps", 0.14, 0.25)], "glows": {"strength": 0.85}},
    # a moor always under a storm, lightning called down on the stones
    "The Stormcrag": dict(STORM, events=_storm_bolts),
    # the plague got to the lost orchard first
    "The Ashen Orchard": {"shade": {"layer": "shade_haunted", "strength": 0.24},
                          "weather": [_fog("atm_plague_fog", 0.16), {"layer": "wx_ashfall", "strength": 0.12,
                                      "floor": 0.12, "tile": 14, "speed": (-3, 6)}],
                          "glows": {"strength": 0.75}, "light": _lt("light_plague_miasma", 0.12)},
    # a caldera of boiling springs and steaming flats
    "The Painted Springs": {"weather": [_fog("atm_steam", 0.2, 0.25), _shimmer(0.1)], "glows": {"strength": 0.75},
                            "light": _lt("light_sun_bloom", 0.16)},
    # a forest from before forests, black water, air thick enough to drink
    "The Coal Forest": {"shade": {"layer": "shade_jungle_canopy", "strength": 0.24, "tile": 12, "drift": (1.0, 0.3)},
                        "weather": [_fog("atm_swamp_mist", 0.24)], "glows": {"strength": 0.75},
                        "light": _lt("light_jungle_shafts", 0.18)},
    # a cold fen where lights move over the water at night
    "The Lanternmere": {"shade": {"layer": "shade_haunted", "strength": 0.2},
                        "weather": [_fog("atm_ground_fog", 0.3), {"layer": "atm_fireflies", "strength": 0.3,
                                    "floor": 0.15, "tile": 16, "speed": (-2, -1)}],
                        "glows": {"strength": 0.8}, "light": _lt("light_moonlight", 0.18)},
    # sealed in its wardstones, late afternoon forever
    "The Sunward Waystation": {"shade": {"layer": "shade_canopy_dapple", "strength": 0.16, "tile": 11,
                                         "drift": (1.2, 0.3)},
                               "weather": [{"layer": "atm_golden_motes", "strength": 0.26, "floor": 0.15, "tile": 16,
                                            "speed": (-2, -1)}],
                               "glows": {"strength": 0.75}, "light": _lt("light_golden_canopy", 0.3)},
    # a steppe under snow since the Integration
    "The Long Winter": {"shade": {"layer": "shade_storm_gloom", "strength": 0.12},
                        "weather": [{"layer": "wx_snow_light", "strength": 0.3, "floor": 0.1, "tile": 14,
                                     "speed": (-8, 30)}],
                        "glows": {"strength": 0.8}, "light": _lt("light_winter_sun", 0.22)},
    # terraces of rain pools on the bark, and a rainbow now and then
    "The Raincatch": {"shade": {"layer": "shade_jungle_canopy", "strength": 0.16, "tile": 12, "drift": (1.0, 0.3)},
                      "weather": [{"layer": "wx_drizzle", "strength": 0.2, "floor": 0.1, "tile": 14,
                                   "speed": (-10, 60)}],
                      "events": [_rainbow], "glows": {"strength": 0.75}, "light": _lt("light_overcast", 0.06)},
    # the Amazon's tallest crowns, caught in the tree
    "The Kapok Crowns": dict(JUNGLE, weather=[{"layer": "atm_golden_motes", "strength": 0.18, "floor": 0.15,
                                               "tile": 16, "speed": (-2, -1)}]),
    # an eyrie under a thunderhead that never moves
    "The Stormroost": dict(STORM, events=_storm_bolts),
    # a model of the heavens: stars cross it
    "The Orrery": {"shade": {"layer": "shade_night", "strength": 0.14},
                   "events": [{"layer": "sky_shooting_stars", "every": (15, 35), "dur": 1.8, "strength": 0.55},
                              {"layer": "sky_falling_star", "every": (40, 80), "dur": 2.2, "strength": 0.5}],
                   "glows": {"strength": 0.8}, "light": _lt("light_arcane_shimmer", 0.16)},
    # a cloud shelf full of lost ships
    "The Cloudwreck": {"shade": {"layer": "shade_cloud_shadows", "strength": 0.18, "tile": 16, "drift": (3.0, 1.0)},
                       "weather": [_fog("atm_fog_bank", 0.16, 0.35)], "glows": {"strength": 0.75},
                       "light": _lt("light_sun_bloom", 0.16)},
    # a table mountain in the sky, waterfalls pouring off into nothing
    "The Lost Tepui": {"shade": {"layer": "shade_cloud_shadows", "strength": 0.16, "tile": 16, "drift": (3.0, 1.0)},
                       "weather": [_fog("atm_waterfall_mist", 0.16, 0.35)], "events": [_rainbow],
                       "glows": {"strength": 0.75}, "light": _lt("light_sun_bloom", 0.2)},
    # the hidden libraries under the Underdark
    "The Unwritten Stacks": dict(UNDERDARK, light=_lt("light_arcane_shimmer", 0.14)),
    "The Palimpsest Vault": dict(UNDERDARK, light=_lt("light_arcane_shimmer", 0.18)),
}
ZONES.update(HIDDEN)

KEYS = ("shade", "weather", "glows", "particles", "life", "events", "light")


def apply(zones):
    """Put each map's effects on it. `zones` is {name: tilemap}. Returns how many maps got effects."""
    n = 0
    for name, tm in zones.items():
        fx = ZONES.get(name)
        if not fx or getattr(tm, "sky", None) or any(getattr(tm, k, None) for k in KEYS):
            continue
        for k in KEYS:
            if k in fx:
                v = fx[k]
                setattr(tm, k, [dict(x) for x in v] if isinstance(v, list) else dict(v))
        n += 1
    return n
