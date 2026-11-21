"""Environment effects across Azeroth (docs/environment_effects_art_prompts.md, EFX1 to EFX10).

Kyle, 21 Nov 2026: "I gave you a shit load of visual effect art. You used it in the SC starting zone and also the sky
zones. Can you start to incorporate it through azeroth too." And: "let's test it with ONE zone!" Eastern Tirisfal went
first; once Kyle had seen it, the Underdark, Ashenvale and Azshara followed, then every other overworld map and town
in Azeroth through one preset per kind of country (21 Nov 2026). Caves are still to come. The standing rule for all
of it: "supplement zones but NOT dominate them. They should complement the zone."

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
HAUNTED = {         # Deadwind: dead quiet, fog on the ground, moonlight
    "shade": {"layer": "shade_haunted", "strength": 0.34},
    "weather": [{"layer": "atm_ground_fog", "strength": 0.3, "floor": 0.3, "tile": 18, "speed": (-3, 1)}],
    "glows": {"strength": 0.8},
    "light": {"layer": "light_moonlight", "strength": 0.18, "breathe": 0.1},
}
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
    (HAUNTED, ("Deadwind West", "Deadwind East"), ("Ariden's Watch",)),
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
