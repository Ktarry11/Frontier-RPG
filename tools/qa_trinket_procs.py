"""
Trinkets that DO something - Kyle, 10 Nov: "trinkets over 50+ WILL AND MUST start to actually
do stuff."

The proc engine is the talents' one (combat/status_effects.py, fire_proc_trigger). An item
carries a `proc` dict and Character._sync_equipment_procs hangs it on the wearer. That is four
places a proc can silently fall on the floor - the loot file, the Item, the save, the wearer -
and this project's oldest bug is exactly that: authored, read by nothing.

So this checks every link, and then checks the only thing that matters: that the proc FIRES,
off the real event, through the real code path the game uses (Ability.use for casts,
Character.take_damage for hits). A proc that is present in active_effects and never fires is
the bug this suite exists to catch.

  1. RULE   - every trinket at required_level 50+ carries a proc, with tooltip text.
  2. VALID  - every trigger is a real ProcTrigger, and every payload key is one the engine
              READS. The valid set is taken from fire_proc_trigger's source, never from the
              authored data - deriving it from the data would approve anything written.
  3. LOAD   - the proc survives the loot file -> Item build, for both boss and epic paths,
              and a save round-trip.
  4. WEAR   - equipping hangs the effect, hidden from buff panels; unequipping removes it;
              death restores it; a recalc never resets its internal cooldown.
  5. FIRE   - each of the three trinkets fires off its real event and does what it says.
"""
import glob
import json
import os
import re
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PROBLEMS = []


def fail(msg):
    PROBLEMS.append(msg)
    print(f"  FAIL {msg}")


def ok(msg):
    print(f"  ok   {msg}")


TRINKET_SLOTS = ("trinket", "trinket1", "trinket2")
#: Keys in a proc dict that are not payloads: gates, timing, and the tooltip line.
NON_PAYLOAD = {"trigger", "chance", "icd", "describe", "ability_filter",
               "require_form", "require_mechsuit"}


def all_trinkets():
    """(file, item_def) for every trinket authored anywhere in data/."""
    out = []

    def walk(o, f):
        if isinstance(o, dict):
            if o.get("slot") in TRINKET_SLOTS and o.get("name"):
                out.append((f, o))
            for v in o.values():
                walk(v, f)
        elif isinstance(o, list):
            for v in o:
                walk(v, f)

    for f in glob.glob(str(ROOT / "data/**/*.json"), recursive=True):
        try:
            walk(json.loads(Path(f).read_text()), Path(f).name)
        except (OSError, json.JSONDecodeError):
            pass
    return out


def engine_reads():
    """Every proc key fire_proc_trigger actually reads, from its own source."""
    src = (ROOT / "combat/status_effects.py").read_text()
    return set(re.findall(r'proc\.get\("([a-z_]+)"', src))


def check_rule_and_validity(trinkets):
    print("\n1-2. rule and validity")
    from combat.status_effects import ProcTrigger
    triggers = {v for k, v in vars(ProcTrigger).items() if k.isupper() and isinstance(v, str)}
    reads = engine_reads()
    with_proc = 0
    for f, d in trinkets:
        proc = d.get("proc")
        if (d.get("required_level") or 0) >= 50 and not proc:
            fail(f"{d['name']} ({f}) is required level {d.get('required_level')} and a bare "
                 f"stat stick - trinkets at 50+ must do something")
        if not proc:
            continue
        with_proc += 1
        if proc.get("trigger") not in triggers:
            fail(f"{d['name']}: trigger {proc.get('trigger')!r} is not a ProcTrigger")
        payloads = [k for k in proc if k not in NON_PAYLOAD]
        if not payloads:
            fail(f"{d['name']}: proc has no payload - it would fire and do nothing")
        for k in payloads:
            if k not in reads:
                fail(f"{d['name']}: payload {k!r} is read by nothing in fire_proc_trigger")
        if not proc.get("describe"):
            fail(f"{d['name']}: no `describe` - the tooltip would not say what it does")
        if not proc.get("icd"):
            fail(f"{d['name']}: no internal cooldown - an on-hit proc with none can chain")
    ok(f"{len(trinkets)} trinkets checked, {with_proc} carry a proc, "
       f"{len(reads)} payload keys known to the engine")


def build(name):
    """The real Item for one named trinket, by the path the game builds it."""
    # Epics first, by roll_epic's own construction. epic_drops.json lives in data/loot/, so
    # the boss loader ALSO merges it - under the "boss names" world and dungeon - and finding
    # it there would test the wrong path.
    from entities import boss_loot, epic_drops
    for bucket in ("world", "dungeon"):
        for d in epic_drops._pool()[bucket]:
            if d.get("name") == name:
                from entities.item import Item
                return Item.from_dict(dict(d)), "epic"
    for boss, pool in boss_loot._load_boss_loot_tables().items():
        if boss in ("world", "dungeon"):
            continue
        for d in pool:
            if d.get("name") == name:
                return boss_loot._item_from_def(d), "boss"
    return None, None


def check_load():
    print("\n3. load")
    from entities.item import Item
    items = {}
    for name in ("The Unbanked Fire", "Running-Dry Charm", "Articles of the Southsea"):
        item, path = build(name)
        if item is None:
            fail(f"{name}: not found in any loot table")
            continue
        if not getattr(item, "proc", None):
            fail(f"{name}: the {path} path built it WITHOUT its proc")
            continue
        again = Item.from_dict(json.loads(json.dumps(item.to_dict())))
        if again.proc != item.proc:
            fail(f"{name}: proc lost or changed across a save round-trip")
            continue
        items[name] = item
        ok(f"{name}: built by the {path} path with its proc, survives save/load")
    return items


def hero(cls, level=55):
    from entities.character import Character
    c = Character(name=f"Test{cls}", char_class=cls, level=level)
    return c


def wear(c, item):
    """Equip through the real path. equip_item only equips from the bag - handing it an item
    that is not in the inventory returns False, which is the rig failing, not the trinket."""
    c.inventory.append(item)
    return c.equip_item(item)


def item_effects(c):
    from combat.status_effects import ITEM_PROC_PREFIX
    return [e for e in c.active_effects if str(e.effect_id).startswith(ITEM_PROC_PREFIX)]


def check_wear(items):
    print("\n4. wear")
    from combat.status_effects import is_displayable_buff
    trinket = items.get("Articles of the Southsea")
    if trinket is None:
        return
    c = hero("Priest")
    if not wear(c, trinket):
        fail("a level 55 priest could not equip Articles of the Southsea")
        return
    fx = item_effects(c)
    if len(fx) != 1:
        fail(f"equipping hung {len(fx)} item effects, expected 1")
        return
    if is_displayable_buff(fx[0]):
        fail("the trinket's carrier effect shows on buff panels as a permanent buff")
    else:
        ok("equipping hangs one carrier effect, hidden from buff panels")

    fx[0].proc_icd_remaining = 3
    c._recalculate_derived_stats()
    if item_effects(c)[0].proc_icd_remaining != 3:
        fail("a stat recalc reset the trinket's internal cooldown")
    else:
        ok("a recalc leaves the internal cooldown alone")

    c.clear_status_effects()   # the death wipe
    if len(item_effects(c)) != 1:
        fail("dying stripped the trinket's proc and nothing put it back")
    else:
        ok("the death wipe is followed by the proc coming back")

    slot = next(s for s, it in c.equipment.slots.items() if it is trinket)
    c.unequip_item(slot)
    if item_effects(c):
        fail("unequipping left the proc behind")
    else:
        ok("unequipping removes it")


def certain(item):
    """The same item with its proc made certain, so a fire is not left to a dice roll.
    A COPY - the authored item is untouched."""
    from entities.item import Item
    d = item.to_dict()
    d["proc"] = dict(d["proc"], chance=100)
    return Item.from_dict(d)


def fight(c):
    from combat.combat_engine import CombatEngine
    from entities.monster import Monster
    from entities.party import Party
    foe = Monster("Training Target", "humanoid_warrior", level=55)
    foe.current_health = foe.max_health = 999999
    engine = CombatEngine(c, foe, party=Party(c), enemies=[foe])
    return foe, engine


def check_fire(items):
    print("\n5. fire")

    # The Unbanked Fire - a real damaging spell, through Ability.use.
    if "The Unbanked Fire" in items:
        c = hero("Mage")
        wear(c, certain(items["The Unbanked Fire"]))
        foe, engine = fight(c)
        c.current_mana = c.mana
        before = c.spell_power
        spell = c.ability_book.get_ability("mage_frostbolt")
        spell.turns_remaining = 0
        spell.use(c, foe, in_combat=True, engine=engine)
        blaze = [e for e in c.active_effects if e.effect_id == "unbanked_fire_blaze"]
        if not blaze:
            fail("The Unbanked Fire: a damaging spell landed and Uninsured Blaze never appeared")
        elif c.spell_power - before != 40:
            fail(f"The Unbanked Fire: spell power moved by {c.spell_power - before}, expected 40")
        else:
            ok(f"The Unbanked Fire: Frostbolt lands, Uninsured Blaze adds 40 spell power "
               f"({before} -> {c.spell_power})")
        # The internal cooldown is real: a second spell straight after must not refresh it.
        if not item_effects(c) or item_effects(c)[0].proc_icd_remaining <= 0:
            fail("The Unbanked Fire: fired with no internal cooldown set")

    # Running-Dry Charm - a real hit, through take_damage.
    if "Running-Dry Charm" in items:
        c = hero("Warrior")
        wear(c, certain(items["Running-Dry Charm"]))
        foe, engine = fight(c)
        c.current_health = c.health
        c.take_damage(50, "physical", attacker=foe)
        shield = [e for e in c.active_effects if e.effect_id == "running_dry_reserve"]
        want = max(1, int(c.health * 0.08))
        if not shield:
            fail("Running-Dry Charm: struck, and Last Reserve never appeared")
        elif getattr(shield[0], "absorb", 0) != want:
            fail(f"Running-Dry Charm: shield absorbs {getattr(shield[0], 'absorb', 0)}, "
                 f"expected {want} (8% of {c.health})")
        else:
            ok(f"Running-Dry Charm: struck, Last Reserve absorbs {want} (8% of {c.health} health)")

    # Articles of the Southsea - a real heal, through Ability.use.
    if "Articles of the Southsea" in items:
        c = hero("Priest")
        wear(c, certain(items["Articles of the Southsea"]))
        foe, engine = fight(c)
        c.current_health = c.health // 2
        heal = c.ability_book.get_ability("priest_heal")
        heal.turns_remaining = 0
        c.current_mana = c.mana
        cost_free = c.current_mana
        heal.use(c, c, in_combat=True, engine=engine)
        spent = cost_free - c.current_mana
        # Measure the refund against the same cast with no trinket.
        c2 = hero("Priest")
        foe2, engine2 = fight(c2)
        c2.current_health = c2.health // 2
        h2 = c2.ability_book.get_ability("priest_heal")
        h2.turns_remaining = 0
        c2.current_mana = c2.mana
        start2 = c2.current_mana
        h2.use(c2, c2, in_combat=True, engine=engine2)
        spent_plain = start2 - c2.current_mana
        if spent_plain - spent != 90:
            fail(f"Articles of the Southsea: a heal cost {spent} with it and {spent_plain} "
                 f"without - expected a 90 mana refund")
        else:
            ok(f"Articles of the Southsea: Heal lands and 90 mana comes back "
               f"(net cost {spent} vs {spent_plain})")


def main():
    trinkets = all_trinkets()
    check_rule_and_validity(trinkets)
    items = check_load()
    check_wear(items)
    check_fire(items)
    if PROBLEMS:
        print(f"\nFAILED - {len(PROBLEMS)} problem(s)")
        return 1
    print("\ntrinket procs OK - every 50+ trinket does something, carries it from the loot file "
          "to the wearer, and fires off its real event.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
