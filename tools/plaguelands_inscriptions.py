"""
Shoulder inscriptions, bought from the Plaguelands' two quartermasters at Revered (the Argent Dawn's at Light's Hope,
the Order of the Pale Flame's at Sorrow Hill). Kyle, 16 Nov 2026: "Shoulder enchants we can add, tabards are
pointless."

Shoulders take nothing from an enchanter (world/enchanting.py, as in classic); an inscription is the one thing that
goes on them. It's an enchantment scroll like any other (material_type "enchant_scroll", read onto the shoulders
with the Enchant button), in its own group, "shoulder", and nobody can make one: they're only sold.

NUMBERS. The enchantment formula every other enchantment is held to (tools/qa_enchanting.py): level 58 x 0.36 x 1.3
x the group's share. Shoulders take a share of 0.5, between a bracer's 0.3 and a weapon's 0.55, which is about
14 points split over two or three stats.

WHO GETS WHAT. Eight, so every spec has one: the Argent Dawn's four are the classic roles (a fighter's, a caster's,
a healer's and a tank's), and the Pale Flame's four are its own: the two hybrids, a caster's with spirit in it, and
a strength fighter's.

    PYTHONPATH=. python3 tools/build_plaguelands_rewards.py      (installs these and shelves them)

install() is idempotent, and tools/build_enchanting.py calls it after it rewrites enchants.json, so a rebuild keeps
them.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENCH = ROOT / "data/enchanting/enchants.json"
MATS = ROOT / "data/gathering/materials.json"

GROUP = ("shoulder", {"label": "Shoulder", "share": 0.5})
LEVEL = 58
PRICE = 200000        # 20 gold at the quartermaster, about half a Revered blue
SELL = 2500           # what a vendor gives back for one

#: faction -> [(id, title, family, stats, hybrid, flavour)]
INSCRIPTIONS = {
    "argent_dawn": [
        ("inscription_argent_vengeance", "Argent Vengeance", "argent_ap", {"attack_power": 14, "stamina": 7}, False,
         "The Argent Dawn's mark for those who do the killing."),
        ("inscription_argent_discipline", "Argent Discipline", "argent_sp", {"spell_power": 12, "intellect": 6},
         False, "The Argent Dawn's mark for its battle mages."),
        ("inscription_argent_faith", "Argent Faith", "argent_heal", {"healing_power": 18, "mp5": 2}, False,
         "The Argent Dawn's mark for the ones who keep everyone else standing."),
        ("inscription_argent_warding", "Argent Warding", "argent_tank", {"stamina": 9, "armor": 23}, False,
         "The Argent Dawn's mark for whoever stands at the front."),
    ],
    "pale_flame": [
        ("inscription_pale_crusader", "the Pale Crusader", "pale_str_int",
         {"strength": 5, "intellect": 5, "stamina": 4}, True,
         "The Order's mark for those who fight with a blade and a prayer."),
        ("inscription_pale_pathfinder", "the Pale Pathfinder", "pale_agi_int",
         {"agility": 5, "intellect": 5, "stamina": 4}, True,
         "The Order's mark for its scouts, who fight with a bow and a spell."),
        ("inscription_pale_ember", "the Pale Ember", "pale_sp", {"spell_power": 9, "spirit": 4, "intellect": 4},
         False, "The Order's mark for its casters. It stays warm."),
        ("inscription_pale_zealot", "the Pale Zealot", "pale_str", {"strength": 7, "attack_power": 13}, False,
         "The Order's mark for the ones who walked out of the Crusade and kept their swords."),
    ],
}


def ids(faction):
    return [r[0] for r in INSCRIPTIONS[faction]]


def install():
    """Upsert the shoulder group, the eight inscriptions and their scrolls. -> number installed."""
    d = json.loads(ENCH.read_text(encoding="utf-8"))
    d["groups"][GROUP[0]] = dict(GROUP[1])
    md = json.loads(MATS.read_text(encoding="utf-8"))
    mats = md["materials"]
    n = 0
    for faction, rows in INSCRIPTIONS.items():
        for (iid, title, family, stats, hybrid, flavour) in rows:
            d["enchants"][iid] = {"name": f"Inscription of {title}", "title": title, "group": "shoulder",
                                  "family": family, "tier": 4, "rank": 4, "level": LEVEL, "skill": 1,
                                  "stats": dict(stats), "hybrid": hybrid, "faction": faction}
            mats[iid] = {"name": f"Inscription of {title}", "material_type": "enchant_scroll",
                         "profession": "enchanting", "tier": "late",
                         "description": f"{flavour} Read it onto your shoulders with the Enchant button in your bags.",
                         "stack_limit": 20, "sell_price": SELL, "vendor_price": PRICE,
                         "icon_id": "enchant_scroll"}
            n += 1
    ENCH.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    MATS.write_text(json.dumps(md, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return n
