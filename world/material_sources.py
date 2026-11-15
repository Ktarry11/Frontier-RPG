"""Where a material comes from, for its tooltip.

Kyle's crafting backlog (B8): a material's tooltip says where it comes from - gathered where, sold by
whom, dropped by what - so a crafter short of Felcloth knows where to go instead of guessing.

Built once from the data the game already runs on: the zones' gathering and fishing tables, the cloth
and skinning bands, the ore a gem is prospected or mined from, the smelting and crafting recipes, and
the shops. THE SECRETS STAY SECRET (Kyle's standing rule): a hidden zone is never named, and a hidden
seller is never listed, even when it's the only place something can be had.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_PLACES = 4
MAX_SELLERS = 3


def _load(rel):
    try:
        return json.loads((ROOT / rel).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def _slug(name):
    s = re.sub(r"[^a-z0-9]+", "_", str(name).lower()).strip("_")
    return s[4:] if s.startswith("the_") else s


@lru_cache(maxsize=1)
def _zone_names():
    """slug -> display name for every zone the game names, and the slugs of the hidden ones."""
    names = {}
    for name in (_load("data/zones/zone_levels.json").get("zones") or {}):
        if not str(name).startswith("_"):
            names[_slug(name)] = name
    hidden = set()
    try:
        from world import hidden_zones
        for name in (hidden_zones.registry() or {}):
            hidden.add(_slug(name))
    except Exception:
        pass
    for q in (_load("data/quests/hidden_zones.json").get("quests") or []):
        hidden.add(_slug(q.get("zone", "")))
    return names, hidden


def _zone(slug):
    """The display name of a zone, or None for a hidden one."""
    names, hidden = _zone_names()
    s = _slug(slug)
    if s in hidden:
        return None
    return names.get(s) or " ".join(w.capitalize() for w in s.split("_"))


def _places(zones):
    seen = []
    for z in zones:
        n = _zone(z)
        if n and n not in seen:
            seen.append(n)
    if not seen:
        return ""
    if len(seen) > MAX_PLACES:
        return ", ".join(seen[:MAX_PLACES]) + f" and {len(seen) - MAX_PLACES} more"
    return ", ".join(seen)


def _band_text(bands, mid):
    lo = [a for a, b, table in bands if mid in table]
    hi = [b for a, b, table in bands if mid in table]
    if not lo:
        return ""
    return f"levels {min(lo)}-{min(max(hi), 60) if min(lo) < 60 else max(hi)}"


@lru_cache(maxsize=1)
def _index():
    idx = {}

    def add(mid, kind, value):
        idx.setdefault(mid, {}).setdefault(kind, []).append(value)

    pools = _load("data/gathering/node_pools.json").get("zones", {})
    for zone, z in pools.items():
        for mid in (z.get("table") or {}):
            add(mid, "gathered", zone)
        for mid in ((z.get("fishing") or {}).get("table") or {}):
            add(mid, "fished", zone)
    for ore, rows in (_load("data/gathering/gem_drops.json").get("drops") or {}).items():
        for gid, _chance in rows:
            add(gid, "from_ore", ore)
    for bar, r in (_load("data/gathering/smelting_recipes.json").get("recipes") or {}).items():
        for ore in (r.get("inputs") or {}):
            add(r.get("output", bar), "smelted", ore)
    # crafted: which trades make it
    crafting = _load("data/crafting/recipes.json").get("professions", {})
    files = {p: g.get("recipes", {}) for p, g in crafting.items()}
    for prof, rel in (("blacksmithing", "data/blacksmithing/recipes.json"),
                      ("leatherworking", "data/leatherworking/recipes.json"),
                      ("jewelcrafting", "data/jewelcrafting/recipes.json"),
                      ("enchanting", "data/enchanting/recipes.json"),
                      ("runecrafting", "data/runecrafting/recipes.json")):
        files[prof] = _load(rel).get("recipes", {})
    for prof, recipes in files.items():
        for rid, r in recipes.items():
            if rid.startswith("secret"):
                continue
            out = r.get("output") or {}
            if out.get("kind") == "material":
                add(out.get("material_id"), "crafted", "Sawmill" if prof == "woodcutting" else prof.title())
                ins = r.get("inputs") or {}
                if ins:
                    # the main thing it's made from (a bolt's cloth, a plank's wood)
                    add(out.get("material_id"), "made_from", max(ins, key=ins.get))
    # sold by: public shops only
    for v in (_load("data/npcs/vendors.json").get("vendors") or []):
        if v.get("hidden") or _zone(v.get("zone", "")) is None:
            continue
        for i in v.get("sells", []):
            add(i, "sold", v.get("name") or v.get("vendor_id"))
    return idx


def lines(material_id, _depth=0):
    """Short lines for a tooltip: "Gathered in Durotar, Razor Hill", "Sold by Grezz the Smith". Empty
    when nothing public is known (a secret's material says nothing rather than give it away)."""
    if not material_id:
        return []
    src = _index().get(material_id, {})
    out = []
    g = _places(src.get("gathered", []))
    if g:
        out.append(f"Gathered in {g}")
    f = _places(src.get("fished", []))
    if f:
        out.append(f"Fished in {f}")
    try:
        from entities import cloth_drops
        t = _band_text(cloth_drops.BANDS, material_id)
        if t:
            out.append(f"Dropped by humanoids, {t}")
    except Exception:
        pass
    try:
        from entities import skinning_drops
        t = _band_text(skinning_drops.BANDS, material_id)
        if t:
            out.append(f"Skinned from beasts, {t}")
    except Exception:
        pass
    if src.get("from_ore"):
        from world.gathering_manager import get_gathering_node_manager
        gm = get_gathering_node_manager()
        ores = []
        for ore in src["from_ore"]:
            n = (gm.get_material_def(ore) or {}).get("name", ore)
            if n not in ores:
                ores.append(n)
        out.append(f"Found mining or prospecting {', '.join(ores[:3])}")
    if src.get("smelted"):
        from world.gathering_manager import get_gathering_node_manager
        gm = get_gathering_node_manager()
        ores = list(dict.fromkeys(src["smelted"]))
        out.append("Smelted from " + ", ".join((gm.get_material_def(o) or {}).get("name", o) for o in ores))
        if len(ores) == 1 and _depth < 1:
            oname = (gm.get_material_def(ores[0]) or {}).get("name", ores[0])
            out.extend(f"{oname}: {t[0].lower() + t[1:]}" for t in lines(ores[0], _depth + 1)
                       if not t.startswith("Sold by"))
    crafted = list(dict.fromkeys(src.get("crafted", [])))
    if crafted:
        made = ("Made at the " if crafted == ["Sawmill"] else "Made with ") + ", ".join(crafted)
        base = list(dict.fromkeys(src.get("made_from", [])))
        if len(base) == 1 and _depth < 1:
            # one step back: a bolt says where its cloth comes from, a bar where its ore is mined
            from world.gathering_manager import get_gathering_node_manager
            bname = (get_gathering_node_manager().get_material_def(base[0]) or {}).get("name", base[0])
            made += f" from {bname}"
            out.append(made)
            out.extend(f"{bname}: {t[0].lower() + t[1:]}" for t in lines(base[0], _depth + 1)
                       if not t.startswith("Sold by"))
        else:
            out.append(made)
    sold = list(dict.fromkeys(src.get("sold", [])))
    if sold:
        more = f" and {len(sold) - MAX_SELLERS} more" if len(sold) > MAX_SELLERS else ""
        out.append(f"Sold by {', '.join(sold[:MAX_SELLERS])}{more}")
    return out


def reset_caches():
    _index.cache_clear()
    _zone_names.cache_clear()
