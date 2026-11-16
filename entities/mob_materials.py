"""Crafting materials that particular monsters drop (Kyle, 15 Nov 2026: "add some bro and add some of it to
crafting requirements"). WoW's scorpid scales and Un'Goro guardian stones: a Harpy Plume comes off harpies and
nothing else, so a crafter who needs one knows exactly where to go.

The data is data/creatures/mob_materials.json, written by tools/build_mob_materials.py. Rolled once per enemy,
like cloth and meat, and not gated on a profession: anyone can pull a quill off a harpy, and you need the trade
to do anything with it. A boss or rare that carries one always drops it, one or two.
"""
import json
import random
from functools import lru_cache
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "data" / "creatures" / "mob_materials.json"


@lru_cache(maxsize=1)
def _by_creature():
    """creature name -> [(material_id, chance, (boss_lo, boss_hi))]"""
    try:
        data = json.loads(_PATH.read_text(encoding="utf-8")).get("materials", {})
    except (OSError, ValueError):
        return {}
    out = {}
    for mid, d in data.items():
        for name in d.get("creatures", []):
            out.setdefault(name, []).append((mid, float(d.get("chance", 0.3)), tuple(d.get("boss_qty", (1, 2)))))
    return out


def sources(material_id):
    """(creature names, zone names) for a material, for its tooltip."""
    try:
        d = json.loads(_PATH.read_text(encoding="utf-8")).get("materials", {}).get(material_id)
    except (OSError, ValueError):
        d = None
    return (list(d.get("creatures", [])), list(d.get("zones", []))) if d else ([], [])


def roll_mob_materials(enemy, rng=random):
    """[(material_id, qty)] for one defeated enemy."""
    rows = _by_creature().get(getattr(enemy, "name", ""))
    if not rows:
        return []
    out = []
    boss = bool(getattr(enemy, "is_boss", False))
    for mid, chance, (lo, hi) in rows:
        if boss:
            out.append((mid, rng.randint(lo, hi)))
        elif rng.random() < chance:
            out.append((mid, 1))
    return out
