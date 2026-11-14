#!/usr/bin/env python3
"""Death costs something, and only a res undoes it.

    PYTHONPATH=. python3 tools/qa_revival.py

Kyle, 12 Nov 2026: "any class that can heal gets a revival skill. res spell. When people all
die the entire group loses 15% of their EXP and they go back to either the start of the
dungeon, start of the cave, or if theyre in open world then they go back to the nearest town
entrance. IF one character is alive after a win, only that character gets exp for the kill and
they better hope to hell they have a res lol."

Before this, leaving ANY fight - won or lost - stood every fallen member back up at full
health, so a death was a thing that happened on one screen and was gone by the next.

NINE CLAIMS:

  1. EVERY CLASS THAT CAN HEAL A FRIEND CAN RAISE ONE, and a class that cannot heal has no res.
  2. A RES CAN ACTUALLY BE AIMED AT THE DEAD, in a fight and out of one. The three revives the
     game already had were only ever offered the living, and answered "is not dead!".
  3. A WIN LEAVES THE DEAD DEAD, and they earn nothing from it.
  4. NOTHING BUT A RES RAISES THEM - not a heal, a potion, a meal, standing still, or a level.
  5. A WIPE COSTS 15% OF EVERYONE'S EXPERIENCE (never a level) and stands the group back up.
  6. A WIPE IN A DUNGEON PUTS THE PARTY AT THE DOOR THEY CAME IN BY - the first door, even when
     they died two levels down - without bringing back what they had already killed.
  7. A WIPE IN THE OPEN WORLD PUTS THEM AT A TOWN ENTRANCE, from every open zone in the game.
  9. AN INNKEEPER RAISES THE FALLEN, free, and only offers to while somebody is down (Kyle:
     "if the only healer is dead ... people can res at an inn keeper").
  8. THE OLD BLANKET REVIVE IS GONE from the combat screen, and a win reads as a win even when
     the player's own character is the one on the floor.
"""
import glob
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import contextlib  # noqa: E402
import io  # noqa: E402

with contextlib.redirect_stdout(io.StringIO()):
    import pygame
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    from core.game_state import GameStateManager
    from entities.character import Character
    from entities.monster import Monster
    from entities.party import Party
    from combat.combat_engine import CombatEngine
    from combat.abilities import get_class_abilities

#: Classes whose only "heals" cannot reach a fallen friend: war-cries over the whole party,
#: or a heal for the caster's own pet.
NO_RES = {"barbarian", "hunter", "warlock"}


def make(cls, level=40, name=None):
    with contextlib.redirect_stdout(io.StringIO()):
        c = Character(name=name or cls, char_class=cls, level=level)
    c.current_health = c.health
    c.current_mana = c.mana
    return c


def kill(c):
    c.current_health = 0


def res_of(c):
    return next((a for a in c.ability_book.abilities.values() if a.effect_type == "revive"), None)


def main():
    bad = []

    # ---- 1. healers have a res, non-healers do not
    healers, with_res = [], []
    for path in sorted(glob.glob("data/abilities/*.json")):
        cid = os.path.basename(path)[:-5]
        if cid.startswith("_") or cid == "asher_unique":
            continue
        raw = json.load(open(path, encoding="utf-8")).get("abilities", [])
        heals_ally = any(a.get("effect_type") in ("heal", "hot") and a.get("target_type") == "ally"
                         and not a.get("requires_talent") for a in raw)
        book = get_class_abilities(cid.replace("_", " ").title())
        has = any(a.effect_type == "revive" for a in book.abilities.values())
        if has:
            with_res.append(cid)
        if heals_ally and cid not in NO_RES:
            healers.append(cid)
            if not has:
                bad.append(f"{cid} can heal an ally and has no res spell")
        elif has and not any(a.get("effect_type") == "revive" for a in raw):
            bad.append(f"{cid} was given a res spell and cannot heal an ally")
    # each res spell has art of its own, not its class's heal icon
    for cid, entry in json.load(open("data/resurrection_spells.json", encoding="utf-8"))["spells"].items():
        if not os.path.exists(f"assets/icons/abilities/{entry['ability_id']}.png"):
            bad.append(f"{entry['name']} has no icon (assets/icons/abilities/{entry['ability_id']}.png)")
        if entry.get("icon_id"):
            bad.append(f"{entry['name']} still borrows {entry['icon_id']} though it has its own icon")
    for cid in ("warrior", "rogue", "mage"):
        if cid in with_res:
            bad.append(f"{cid} has a res spell")
    # ...and somebody of that class actually KNOWS it at a level they would have it by.
    priest = make("Priest", 40)
    spell = res_of(priest)
    if spell is None or not getattr(spell, "is_learned", True):
        bad.append("a level 40 Priest does not know Resurrection")

    # ---- 2 & 4. only a res raises the dead; and it can be aimed at them
    friend = make("Warrior", 40, "Fallen")
    kill(friend)
    friend.heal(500)
    if friend.is_alive():
        bad.append("a plain heal raised the dead")
    friend._meal_regen = {"left": 20.0, "per_second": 50.0}
    friend.tick_consumable_regen(5.0)
    friend.tick_out_of_combat_regen(30.0, is_moving=False)
    if friend.is_alive():
        bad.append("food or standing still raised the dead")
    heal = next((a for a in priest.ability_book.abilities.values()
                 if a.effect_type == "heal" and a.target_type == "ally" and getattr(a, "is_learned", True)), None)
    if heal is not None:
        heal.use(priest, friend, in_combat=False)
        if friend.is_alive():
            bad.append(f"{heal.name} cast out of combat raised the dead")
    from entities.consumable import Consumable
    import inspect
    if "current_health" not in inspect.getsource(Consumable.can_use):
        bad.append("Consumable.can_use does not turn the dead away, so a potion is spent on a corpse")
    if spell is not None:
        ok, msg = spell.use(priest, friend, in_combat=False)
        if not ok or not friend.is_alive():
            bad.append(f"Resurrection cast out of combat did not raise the dead ({msg})")
        elif not (0 < friend.current_health < friend.health):
            bad.append("a res should bring someone back hurt, not at full health")
        ok, _msg = spell.use(priest, friend, in_combat=False)
        if ok:
            bad.append("a res could be cast on the living")

    # the pickers: the cast panel and the combat screen both offer the FALLEN to a res
    for mod, cls in (("ui.screens.cast_panel", None), ("ui.screens.cast_screen", None),
                     ("ui.screens.combat_screen", None)):
        src = Path(mod.replace(".", "/") + ".py").read_text(encoding="utf-8")
        if '"revive"' not in src:
            bad.append(f"{mod} never asks whether an ability is a revive, so it can only offer "
                       f"the living as targets")

    # ---- 3. a win: the dead stay dead and earn nothing
    a, b = make("Warrior", 20, "Alive"), make("Priest", 20, "Dead")
    party = Party(a)
    party.add_member(b) if hasattr(party, "add_member") else party.members.append(b)
    if b not in party.members:
        party.members.append(b)
    foe = Monster("Kobold Miner", "humanoid_warrior", level=18)
    with contextlib.redirect_stdout(io.StringIO()):
        eng = CombatEngine(a, foe, party=party, enemies=[foe])
    kill(b)
    xa, xb, la, lb = a.experience, b.experience, a.level, b.level
    foe.current_health = 0
    with contextlib.redirect_stdout(io.StringIO()):
        eng._check_combat_end()
    if not eng.victory:
        bad.append("killing the last enemy with one member standing was not a victory")
    if b.is_alive():
        bad.append("a member who died came out of a WON fight alive")
    if (b.experience, b.level) != (xb, lb):
        bad.append("a dead member was paid experience for the kill")
    if (a.experience, a.level) == (xa, la):
        bad.append("the survivor was paid nothing for the kill")

    # ---- 5. a wipe
    a.experience, b.experience = 1000, 401
    la, lb = a.level, b.level
    kill(a)
    kill(b)
    if not party.is_wiped():
        bad.append("a party of corpses is not 'wiped'")
    lost = dict((m.name, n) for m, n in party.wipe_penalty())
    if a.experience != 850 or lost.get("Alive") != 150:
        bad.append(f"1000 experience should become 850 after a wipe, got {a.experience}")
    if b.experience != 341:
        bad.append(f"401 experience should become 341 after a wipe, got {b.experience}")
    if (a.level, b.level) != (la, lb):
        bad.append("a wipe cost somebody a level")
    if not (a.is_alive() and b.is_alive() and a.current_health == a.health):
        bad.append("a wipe did not stand the whole group back up at full health")

    # ---- 9. the innkeeper
    kill(b)
    raised = party.revive_at_inn()
    if raised != [b] or not b.is_alive() or b.current_health != b.health:
        bad.append("an innkeeper did not raise the one fallen member to full health")
    if party.revive_at_inn():
        bad.append("an innkeeper 'raised' somebody with nobody down")
    qd = Path("ui/screens/quest_dialog_screen.py").read_text(encoding="utf-8")
    if 'out.insert(out.index("inn"), "revive")' not in qd or '"revive": "Revive the Fallen"' not in qd \
            or "revive_at_inn()" not in qd:
        bad.append("the innkeeper's dialog does not offer Revive the Fallen")

    # ---- 6 & 7. where they wake
    with contextlib.redirect_stdout(io.StringIO()):
        sm = GameStateManager(screen)
        sm.player = make("Priest", 60, "Hero")
        zm = sm._live_zone_manager()
    lookup = zm.portal_manager._lookup
    # into a cave from outside
    door = next(((src, x, y, dest) for (src, x, y), dest in lookup.items()
                 if src not in zm.cave_names and dest[0] in zm.cave_names), None)
    with contextlib.redirect_stdout(io.StringIO()):
        zm.transition_to_zone(door[0], door[1], door[2] + 1, via_portal=False)
        zm.transition_to_zone(*door[3])
    cave = zm.current_zone.name
    start = (zm.player_x, zm.player_y)
    def spawn_ids():
        return (id(zm.cave_spawns.spawns), [id(sp) for sp in zm.cave_spawns.spawns])
    spawns_before = spawn_ids()
    # wander off, then wipe
    far = None
    for y in range(zm.current_zone.height):
        for x in range(zm.current_zone.width):
            if zm.current_zone.is_walkable(x, y) and abs(x - start[0]) + abs(y - start[1]) > 12:
                far = (x, y)
    if far:
        zm.player_x, zm.player_y = far
    zone_name, x, y, label = zm.respawn_point()
    if zone_name != cave or (x, y) != start:
        bad.append(f"a wipe in {cave} should wake the party where it came in {start}, got "
                   f"{zone_name} {(x, y)}")
    zm.send_to_respawn()
    if (zm.current_zone.name, zm.player_x, zm.player_y) != (cave, start[0], start[1]):
        bad.append("send_to_respawn did not put the party on the dungeon's entry tile")
    if spawn_ids() != spawns_before:
        bad.append("a wipe laid the dungeon's spawns out again - the dead came back with the party")
    # two levels down: the mark stays on the FIRST door
    deeper = next(((src, x, y, dest) for (src, x, y), dest in lookup.items()
                   if src in zm.cave_names and dest[0] in zm.cave_names and dest[0] != src), None)
    if deeper:
        outer = next(((s, x, y, d) for (s, x, y), d in lookup.items()
                      if s not in zm.cave_names and d[0] == deeper[0]), None)
        if outer:
            with contextlib.redirect_stdout(io.StringIO()):
                zm.transition_to_zone(outer[0], outer[1], outer[2], via_portal=False)
                zm.transition_to_zone(*outer[3])
                first = (zm.current_zone.name, zm.player_x, zm.player_y)
                zm.transition_to_zone(*deeper[3])
            got = zm.respawn_point()[:3]
            if got != first:
                bad.append(f"died in {deeper[3][0]}, one level below {first[0]}: should wake at "
                           f"the first door {first}, got {got}")

    # every open zone resolves to a town entrance or a settlement's edge
    nowhere, open_zones = [], 0
    for name, entry in zm.zones.items():
        tm = entry["tilemap"]
        if name in zm.cave_names or getattr(tm, "is_town", False):
            continue
        open_zones += 1
        zm.current_zone = tm
        zm.player_x, zm.player_y = tm.width // 2, tm.height // 2
        zone_name, x, y, label = zm.respawn_point()
        dest = zm.zones[zone_name]["tilemap"]
        in_town = getattr(dest, "is_town", False)
        in_settlement = (zone_name == name and (dest.get_subzone_at(x, y) or {}).get("table_key")
                         and zm.creature_manager.is_safe_subzone(name, dest.get_subzone_at(x, y)["table_key"]))
        if not (in_town or in_settlement):
            nowhere.append(f"{name} -> {zone_name} ({label})")
    if nowhere:
        bad.append(f"{len(nowhere)} open zone(s) have no town entrance to wake at: {nowhere[:8]}")

    # ---- 8. the blanket revive is gone
    cs = Path("ui/screens/combat_screen.py").read_text(encoding="utf-8")
    if "member.current_health = member.health" in cs:
        bad.append("the combat screen still stands every fallen member up on the way out of a fight")
    if "resolve_wipe()" not in cs:
        bad.append("the combat screen never resolves a wipe")
    if "player.is_alive()" in cs:
        bad.append("the result screen still decides Victory/Defeat by whether the PLAYER is "
                   "alive - a win with the player down would read as a defeat")

    print(f"{len(healers)} healing classes, {len(with_res)} classes with a res: {', '.join(sorted(with_res))}")
    print(f"  {open_zones} open zones all resolve to a town entrance")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for line in bad:
            print("  -", line)
        return 1
    print("\nrevival OK - healers can raise the dead and can aim at them, a win leaves the dead "
          "dead and unpaid, nothing but a res raises them, a wipe costs 15% and sends the party "
          "to the dungeon door or a town entrance.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
