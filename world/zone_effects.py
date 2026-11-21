"""Environment effects across Azeroth (docs/environment_effects_art_prompts.md, EFX1 to EFX10).

Kyle, 21 Nov 2026: "I gave you a shit load of visual effect art. You used it in the SC starting zone and also the sky
zones. Can you start to incorporate it through azeroth too." And: "let's test it with ONE zone!" So this starts with
Eastern Tirisfal alone, and the rest of Azeroth joins it once Kyle has seen it.

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

KEYS = ("shade", "weather", "glows", "particles", "life", "light")


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
