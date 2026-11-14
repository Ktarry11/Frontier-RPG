#!/usr/bin/env python3
"""Add the 24 sheet-3 companions to data/npcs/recruits.json.

Kyle, 31 Oct 2026: "i want the new 24 people in the game."

PLACEMENT IS THE HARD PART, because of two rules Kyle set the same day:

  "Let's never put recruits at the end of a dungeon! If we can limit it to
   before the first boss."
  "Let's keep them all before level 49. This way we can recruit them by lvl 45."

The level rule is a number. The dungeon rule needed a real measurement, and the
obvious proxy is wrong: straight-line distance to a boss says nothing about
whether you reach the companion BEFORE or AFTER that boss on the way in. What
matters is path order from the door.

So this walks the zone. BFS from the tile you actually arrive on (recovered
from world/portal_manager.py's destination table, since zones do not record
their own entrance), then a companion is only placed on a tile whose walking
distance from that door is LESS than the first boss chamber's. In a zone with
no bosses the same walk just keeps them off the doormat and off other NPCs.

A candidate tile must also be: walkable, not inside any boss chamber's radius,
not on a vendor, trainer, ambient NPC, existing recruit or portal, and at least
8 steps in so they are not standing in the entrance.
"""
import sys, os, json, re, math, collections, pathlib
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT = pathlib.Path(__file__).resolve().parent.parent

CLASS_OF = {
    "tinker_mechanics": "Tinker", "priest_discipline": "Priest",
    "stormbringer_wind": "Stormbringer", "tinker_invention": "Tinker",
    "reaper_soul": "Reaper", "primalist_wildwalker": "Primalist",
    "ranger_brigand": "Ranger", "witch_doctor_voodoo": "Witch Doctor",
    "templar_crusader": "Templar", "starcaller_moon_guard": "Starcaller",
    "bloodmage_eternal": "Bloodmage", "necromancer_rime": "Necromancer",
    "paladin_holy": "Paladin", "pyromancer_incineration": "Pyromancer",
    "knight_of_xoroth_war": "Knight of Xoroth", "felsworn_tyrant": "Felsworn",
    "guardian_vanguard": "Guardian", "sun_cleric_seraphim": "Sun Cleric",
    "cultist_heretic": "Cultist", "chronomancer_infinite": "Chronomancer",
    "venomancer_vizier": "Venomancer", "witch_hunter_inquisition": "Witch Hunter",
    "warlock_destruction": "Warlock", "hunter_survival": "Hunter",
}

#: recruit_id -> (display name, spec, role, row, level, zone, gender, variant, colour, look)
ROSTER = [
 ("diego_tinker","Diego Salazar","tinker_mechanics","melee_dps","front",5,"Deathknell","male",1,"#C9A227"),
 ("freja_priest","Freja Lindqvist","priest_discipline","healer","back",6,"Valley of Trials","female",2,"#E8E0C8"),
 ("sondre_stormbringer","Sondre Haugen","stormbringer_wind","ranged_dps","back",8,"Scarlet Crypt","male",3,"#6FA8DC"),
 ("berat_tinker","Berat Yilmaz","tinker_invention","healer","back",12,"Brill","male",4,"#B5651D"),
 ("matias_reaper","Matías Fuentes","reaper_soul","melee_dps","front",17,"Sunken Grotto of the Deep","male",5,"#6B5B8A"),
 ("giorgi_primalist","Giorgi Beridze","primalist_wildwalker","melee_dps","front",21,"Tarren Mill","male",6,"#6E8B3D"),
 ("camille_ranger","Camille Roussel","ranger_brigand","melee_dps","front",22,"Wailing Caverns","female",7,"#4F7942"),
 ("orlando_witchdoctor","Orlando Rivera","witch_doctor_voodoo","ranged_dps","back",23,"Shadowpine Altar","male",8,"#3B5BA5"),
 ("adrian_templar","Adrián Mendoza","templar_crusader","melee_dps","front",24,"Astranaar","male",9,"#C0392B"),
 ("saoirse_starcaller","Saoirse Ni Bhraonain","starcaller_moon_guard","tank","front",25,"Shadowfang Keep","female",10,"#9FB6CD"),
 ("nicolas_bloodmage","Nicolás Arce","bloodmage_eternal","tank","front",27,"Splintertree Post","male",11,"#8B1A1A"),
 ("ileana_necromancer","Ileana Dragomir","necromancer_rime","ranged_dps","back",31,"Plague Depths","female",12,"#AFDDE9"),
 ("thiago_paladin","Thiago Macedo","paladin_holy","healer","back",33,"Grom'gol","male",13,"#E6C229"),
 ("skye_pyromancer","Skye Donnelly","pyromancer_incineration","ranged_dps","back",34,"The Drowning Floor","female",14,"#E2703A"),
 ("vuk_knight","Vuk Jovanović","knight_of_xoroth_war","melee_dps","front",35,"Rocky Pass","male",15,"#4A4A4A"),
 ("khalid_hunter","Khalid Al Suwaidi","hunter_survival","ranged_dps","back",39,"Saltwheel","male",16,"#C2B280"),
 ("karim_felsworn","Karim Haddad","felsworn_tyrant","tank","front",40,"The Undercrust","male",17,"#5B8C2A"),
 ("osvaldo_warlock","Osvaldo Beltrán","warlock_destruction","ranged_dps","back",40,"The Bloodsail Raider","male",18,"#B7410E"),
 ("bashir_witchhunter","Bashir Khalidi","witch_hunter_inquisition","melee_dps","front",41,"The Drowned Shrine","male",19,"#2F4F4F"),
 ("gianluca_guardian","Gianluca Ferri","guardian_vanguard","tank","front",42,"Steamwheedle Port","male",20,"#4682B4"),
 ("elias_suncleric","Elias Peralta","sun_cleric_seraphim","tank","front",44,"The Drownbell","male",21,"#F5DEB3"),
 ("rui_cultist","Rui Almeida","cultist_heretic","healer","back",46,"The Lashings","male",22,"#5D3FD3"),
 ("nizar_chronomancer","Nizar Haddad","chronomancer_infinite","ranged_dps","back",48,"The Crossing","male",23,"#3C8D8D"),
 ("yusuf_venomancer","Yusuf Al-Rawi","venomancer_vizier","healer","back",48,"The Bloodsail Anchorage","male",24,"#2E7D32"),
]

MIN_STEPS_IN = 8           # not standing in the doorway
BOSS_CLEAR = 10            # never inside a boss chamber


def arrival_points():
    src = (ROOT / "world/portal_manager.py").read_text(encoding="utf-8")
    out = collections.defaultdict(list)
    for m in re.finditer(
            r'\(\s*\d+\s*,\s*\d+\s*\)\s*:\s*\(\s*"([^"]+)"\s*,\s*(\d+)\s*,\s*(\d+)\s*\)', src):
        out[m.group(1)].append((int(m.group(2)), int(m.group(3))))
    return out


def bfs(zone, start):
    W, H = zone.width, zone.height
    sx, sy = start
    if not (0 <= sx < W and 0 <= sy < H):
        return {}
    if zone.collision_layer[sy][sx] is not None:
        # arrive tile itself blocked; step out to the nearest open tile
        best = None
        for y in range(H):
            for x in range(W):
                if zone.collision_layer[y][x] is None:
                    d = (x - sx) ** 2 + (y - sy) ** 2
                    if best is None or d < best[0]:
                        best = (d, x, y)
        if best is None:
            return {}
        sx, sy = best[1], best[2]
    dist = {(sx, sy): 0}
    q = collections.deque([(sx, sy)])
    while q:
        x, y = q.popleft()
        d = dist[(x, y)]
        for nx, ny in ((x+1, y), (x-1, y), (x, y+1), (x, y-1)):
            if 0 <= nx < W and 0 <= ny < H and (nx, ny) not in dist:
                if zone.collision_layer[ny][nx] is None:
                    dist[(nx, ny)] = d + 1
                    q.append((nx, ny))
    return dist


def main():
    write = "--write" in sys.argv
    import importlib.util
    from world.zone_generator import create_all_zones
    from world.ambient_npc_manager import get_ambient_npc_manager
    from world.vendor_manager import get_vendor_manager

    prose = {}
    for part in ("1", "2", "3"):
        spec = importlib.util.spec_from_file_location(
            f"p{part}", ROOT / f"tools/writing/sheet3_part{part}.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        prose.update(mod.BATCH)

    looks = {}
    doc_looks = (ROOT / "tools/writing/sheet3_looks.json")
    if doc_looks.exists():
        looks = json.loads(doc_looks.read_text(encoding="utf-8"))

    zones = create_all_zones()
    arrive = arrival_points()
    amb = get_ambient_npc_manager()
    vm = get_vendor_manager()

    rdoc = json.load(open(ROOT / "data/npcs/recruits.json", encoding="utf-8"))
    existing = rdoc["recruits"]
    taken_ids = {r["recruit_id"] for r in existing}

    rows, problems = [], []
    for (rid, name, spec_id, theme, row, level, zname, gender, variant, colour) in ROSTER:
        if rid in taken_ids:
            problems.append(f"{rid}: already in recruits.json")
            continue
        if rid not in prose:
            problems.append(f"{rid}: no prose written")
            continue
        z = zones.get(zname)
        if z is None:
            problems.append(f"{rid}: zone '{zname}' does not exist")
            continue

        starts = arrive.get(zname) or []
        if not starts:
            problems.append(f"{rid}: no arrival point known for {zname}")
            continue
        dist = bfs(z, starts[0])
        if not dist:
            problems.append(f"{rid}: could not walk {zname} from its entrance")
            continue

        bosses = [b for b in (getattr(z, "boss_positions", None) or []) if b]
        if not bosses and getattr(z, "boss_position", None):
            bosses = [z.boss_position]
        boss_d = sorted(d for d in (dist.get((b[0], b[1])) for b in bosses) if d is not None)
        first_boss = boss_d[0] if boss_d else None

        occupied = set()
        for n in list(amb.get_npcs_in_zone(zname)) + list(vm.get_vendors_in_zone(zname)):
            occupied.add((n.x, n.y))
        for r in existing:
            if r.get("zone") == zname:
                occupied.add((r.get("x"), r.get("y")))

        cands = []
        for (x, y), d in dist.items():
            if d < MIN_STEPS_IN or (x, y) in occupied:
                continue
            if first_boss is not None and d >= first_boss:
                continue
            if any(math.dist((x, y), (b[0], b[1])) < BOSS_CLEAR for b in bosses):
                continue
            cands.append((d, x, y))
        if not cands:
            problems.append(f"{rid}: no tile in {zname} is before the first boss and clear")
            continue

        # Sit them about 55% of the way to the first boss: past the entrance, well
        # short of the fight. In a boss-less zone, a comfortable walk from the door.
        if first_boss is not None:
            target = first_boss * 0.55
        else:
            target = max(d for d, _x, _y in cands) * 0.35
        d, x, y = min(cands, key=lambda c: abs(c[0] - target))

        rec = {
            "recruit_id": rid, "name": name,
            "char_class": CLASS_OF[spec_id], "spec": spec_id,
            "level": level, "zone": zname, "x": x, "y": y,
            "row": row, "npc_color": colour,
            "backstory": prose[rid]["backstory"],
            "greeting": prose[rid]["greeting"],
            "gear_theme": theme,
            "home_town": None, "home_x": None, "home_y": None, "home_note": None,
            "gender": gender, "appearance_variant": variant,
            "background_sections": {k: prose[rid][k]
                                    for k in ("before", "adjustment", "forward", "now")},
            "look": looks.get(rid, ""),
        }
        existing.append(rec)
        rows.append((rid, zname, level, x, y, d, first_boss))

    print(f"  {len(rows)} placed, {len(problems)} problems\n")
    print(f"  {'id':24s} {'lvl':>3s} {'at':>9s} {'steps in':>8s} {'first boss':>10s}  zone")
    for rid, zname, level, x, y, d, fb in rows:
        print(f"  {rid:24s} {level:3d} {f'({x},{y})':>9s} {d:8d} "
              f"{(str(fb) if fb else 'none'):>10s}  {zname}")
    for p in problems:
        print(f"  PROBLEM {p}")

    if write and not problems:
        json.dump(rdoc, open(ROOT / "data/npcs/recruits.json", "w", encoding="utf-8"), indent=2)
        print(f"\n  written: recruits.json now holds {len(existing)} companions")
    elif write:
        print("\n  REFUSING TO WRITE while there are problems")
        return 1
    else:
        print("\n  dry run - pass --write")
    return 0


if __name__ == "__main__":
    sys.exit(main())
