"""A proc's tooltip line with the numbers it really delivers.

Flat proc payloads (damage_flat, heal_flat, smart_heal) are multiplied by the world curve at the WEARER'S level
(combat/status_effects.py, 15 Nov 2026), but the item's "describe" text was written with the base number - an
Arcanite Dragonling Core said "160 fire damage" and scorched for ~460 at 60. This puts the real number in.
"""
import re

_FLAT_KEYS = ("damage_flat", "heal_flat")


def describe(proc, level=None):
    text = (proc or {}).get("describe") or ""
    if not text or level is None:
        return text
    try:
        from combat.world_curve import world_scale
        ws = world_scale(level)
    except Exception:                                          # noqa: BLE001
        return text
    for key in _FLAT_KEYS:
        base = proc.get(key)
        if isinstance(base, (int, float)) and base > 0:
            real = int(round(base * ws))
            if real != int(base):
                text = re.sub(rf"(?<![\d.]){int(base)}(?![\d.%])", str(real), text, count=1)
    return text
