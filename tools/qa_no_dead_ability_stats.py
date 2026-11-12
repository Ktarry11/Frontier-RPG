"""
Every stat an ability gives is one the game actually reads.

Kyle, 10 Nov, on Tinker's Magic Augmentation ("Ranged Ability Range +5" for 60 turns): there
is no range in this combat system, so the ability did nothing. "Audit every ability for
effects that do nothing in turn-based combat."

Found by this audit and re-purposed, 12 Nov: 16 abilities carrying 17 stat keys that nothing
read - range, movement speed, spell pushback, "% resist" under names the resistance system
does not use, enemy accuracy, CC duration, summon damage.

  1. every key in every ability's stat_mods is read somewhere in combat/, entities/ or world/
     (by name, as a "<target>_from_<stat>_pct" conversion, or as "<school>_damage_taken_pct")
  2. each re-purposed ability, cast for real, changes the thing its new text says it changes
  3. no ability's stat_mods mention range, movement speed or pushback
  4. an ability that hits or heals and ALSO carries stats applies them (13 did the damage
     and silently dropped the rest - Widowmaker's healing cut, Terrasurge's armour break)
"""
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

fails = []
SCHOOLS = ("fire", "frost", "nature", "shadow", "arcane", "holy", "physical", "magic", "spell")
NONSENSE = re.compile(r"range|movement|speed_floor|pushback|line_of_sight|distance")


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    src = ""
    for d in ("combat", "entities", "world"):
        for f in (ROOT / d).rglob("*.py"):
            src += f.read_text()
    from entities.character import STAT_CONVERSION_TARGETS

    def is_read(key):
        if re.search(r"""["']""" + re.escape(key) + r"""["']""", src):
            return True
        if key.endswith("_pct") and "_from_" in key:
            return key[:-4].split("_from_")[0] in STAT_CONVERSION_TARGETS
        m = re.fullmatch(r"([a-z]+)_damage_taken_pct", key)
        return bool(m and m.group(1) in SCHOOLS)

    abilities = {}
    for f in sorted((ROOT / "data/abilities").glob("*.json")):
        data = json.loads(f.read_text())
        for a in data.get("abilities", []) if isinstance(data, dict) else []:
            abilities[a["ability_id"]] = (f.stem, a)
            for key in (a.get("stat_mods") or {}):
                check(is_read(key), f"{a['ability_id']}: gives {key!r}, which nothing reads")
                check(not NONSENSE.search(key), f"{a['ability_id']}: {key!r} means nothing in turn-based combat")
    check(len(abilities) > 1200, f"rig: only {len(abilities)} abilities loaded")

    # 2. the re-purposed ones, cast
    from entities.character import Character
    from entities.monster import Monster
    from combat.abilities import _ability_from_data

    def cast(aid, on_enemy):
        _stem, entry = abilities[aid]
        ab = _ability_from_data(entry)
        ab.is_learned = True
        ab.requires_talent = False
        ab.requires_form = None
        c = Character("Hero", "Mage", 60)
        for attr in ("current_mana", "current_energy", "current_rage"):
            setattr(c, attr, 10 ** 5)
        c.current_health = c.health
        if hasattr(c, "resources"):
            for k in list(getattr(c, "resources", {}) or {}):
                c.resources[k] = 10 ** 5
        foe = Monster("Mottled Boar", "beast_basic", level=60)
        before = (c.armor_penetration_pct, c.crit_chance_spell, c.haste, c.dodge, c.attack_power, c.spell_power,
                  c.get_resistance("holy"), c.get_resistance("nature"))
        try:
            ok, msg = ab.use(c, foe if on_enemy else c, free=True)
        except TypeError:
            ok, msg = ab.use(c, foe if on_enemy else c)
        c._recalculate_derived_stats()
        after = (c.armor_penetration_pct, c.crit_chance_spell, c.haste, c.dodge, c.attack_power, c.spell_power,
                 c.get_resistance("holy"), c.get_resistance("nature"))
        return ok, msg, c, foe, before, after

    SELF = {   # ability -> index into the before/after tuple that must rise
        "tinker_magic_augmentation": 0, "tinker_aether_augmentation": 1,
        "runemaster_runic_tattoos_air": 3, "stormbringer_stabilizing_pressure": 2,
        "tinker_build_battle_turret_x13": 5, "cultist_protection_from_light": 6, "primalist_fae_dust": 7,
    }
    for aid, idx in SELF.items():
        ok, msg, c, foe, before, after = cast(aid, False)
        check(ok, f"{aid} would not cast ({msg})")
        check(after[idx] > before[idx], f"{aid}: cast, and the stat it names did not move ({before[idx]} -> {after[idx]})")
    ENEMY = {
        "stormbringer_crushing_pressure": ("damage_taken_pct", 1), "stormbringer_static_lock": ("damage_dealt_pct", -1),
        "stormbringer_raging_zephyr": ("damage_dealt_pct", -1), "stormbringer_atmospheric_pressure": ("spell_damage_taken_pct", 1),
        "venomancer_mycosis": ("healing_taken_pct", -1),
    }
    for aid, (key, sign) in ENEMY.items():
        for _try in range(12):                                   # a spell can be resisted
            ok, msg, c, foe, _b, _a = cast(aid, True)
            if foe.get_status_stat_mod(key):
                break
        check(ok, f"{aid} would not cast ({msg})")
        got = foe.get_status_stat_mod(key)
        check(got * sign > 0, f"{aid}: cast on an enemy, its {key} is {got}")
    # 4. riders: an ability that hits or heals AND carries stats applies them
    riders = 0
    for aid, (_stem, entry) in abilities.items():
        mods = {k: v for k, v in (entry.get("stat_mods") or {}).items() if k != "taunt"}
        et = entry.get("effect_type")
        if not mods or et in ("buff", "debuff"):
            continue
        riders += 1
        landed = False
        for _try in range(12):                                   # a hit can miss
            ok, msg, c, foe, _b, _a = cast(aid, et != "heal")
            holders = [c, foe]
            if any(e.effect_id == f"{aid}_rider" and set(e.stat_mods) <= set(mods) for h in holders for e in h._effects()):
                landed = True
                break
        check(landed, f"{aid} ({et}) carries {mods} and applies none of it")
    check(riders >= 10, f"rig: only {riders} rider abilities found")

    ok, msg, c, foe, _b, _a = cast("venomancer_venom_shield", False)
    check(ok and c.get_status_stat_mod("magic_damage_taken_pct") < 0, f"venom shield: magic damage taken not reduced ({msg})")

    print(f"{len(abilities)} abilities; every stat key is read; {len(SELF) + len(ENEMY) + 1} re-purposed abilities cast")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:30]:
            print("  ", f)
        return 1
    print("no dead ability stats.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
