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
