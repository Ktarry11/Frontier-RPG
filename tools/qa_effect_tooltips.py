"""
Every buff and debuff on screen can be hovered, and the tooltip says what it does.

Kyle, 10 Nov: "we need to be able to hover over enemy buffs and debuffs (THIS IS HUGE) - same
with OUR characters." 12 Nov: "hovering over OUR buff/debuff in combat should say what it is
(curse/poison? Disease?), the effects, turns left - hots, dots, buffs, debuffs."

A real fight, real abilities cast through the engine, the real combat screen rendered:

  1. every displayable effect on every combatant has a hover rect this frame - on the enemy
     card, on the party roster, and in the targeting screen
  2. putting the mouse on it draws a tooltip (pixels change) and names that effect
  3. the text carries the type (and dispel school when it has one), the real numbers, and the
     time left - for a DoT, a HoT, a stat buff, a stat debuff, a shield and a stun
  4. the same on the Party screen's Buffs tab
  5. player-ability effects get the ability's real icon, not a lettered tile
"""
import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

import pygame  # noqa: E402

fails = []


def check(ok, msg):
    if not ok:
        fails.append(msg)
    return ok


def main():
    pygame.init()
    from config import SCREEN_WIDTH, SCREEN_HEIGHT
    surf = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    from tools.shot_screen import StubSM
    from entities.character import Character
    from entities.party import Party
    from entities.monster import Monster
    from combat.status_effects import StatusEffect, EffectType, DispelType, is_displayable_buff
    from ui.screens.combat_screen import CombatScreen
    from ui.effect_tooltip import effect_lines, effect_icon_path

    player = Character("Hero", "Priest", 40)
    party = Party(player)
    sm = StubSM(player, party)
    foe = Monster("Mangy Wolf", "beast_basic", level=40)
    sm.current_enemy, sm.current_enemies = foe, [foe]
    scr = CombatScreen(sm)
    scr._init_combat()

    # --- effects, one of each shape -------------------------------------------------------
    T = None   # turn-counted
    cases = {
        "dot": (foe, StatusEffect("priest_shadow_word_pain", "Shadow Word: Pain", EffectType.DOT, 6,
                                  potency=31, damage_school="shadow", source_name="Hero",
                                  dispel_type=DispelType.MAGIC)),
        "debuff": (foe, StatusEffect("t_sunder", "Sunder Armor", EffectType.DEBUFF, 5,
                                     stat_mods={"armor": -120}, source_name="Hero",
                                     real_time_seconds=T)),
        "stun": (foe, StatusEffect("t_stun", "Hammer of Justice", EffectType.DEBUFF, 2,
                                   is_stun=True, source_name="Hero", real_time_seconds=T)),
        "hot": (player, StatusEffect("priest_renew", "Renew", EffectType.HOT, 5, potency=44,
                                     source_name="Hero")),
        "buff": (player, StatusEffect("priest_power_word_fortitude", "Power Word: Fortitude",
                                      EffectType.BUFF, 0, stat_mods={"stamina": 20},
                                      source_name="Hero")),
        "shield": (player, StatusEffect("priest_power_word_shield", "Power Word: Shield",
                                        EffectType.BUFF, 4, absorb=250, source_name="Hero",
                                        real_time_seconds=T)),
        "curse": (player, StatusEffect("t_curse", "Curse of Weakness", EffectType.DEBUFF, 4,
                                       stat_mods={"attack_power": -30}, source_name="Mangy Wolf",
                                       dispel_type=DispelType.CURSE, real_time_seconds=T)),
    }
    for holder, eff in cases.values():
        holder.apply_status_effect(eff)

    def live(c):
        return [e for e in c._effects()
                if is_displayable_buff(e) or e.effect_type in (EffectType.DOT, EffectType.HOT)]

    # --- 3. the words ---------------------------------------------------------------------
    def text(key):
        holder, eff = cases[key]
        cur = next((e for e in holder._effects() if e.effect_id == eff.effect_id), None)
        if not check(cur is not None, f"rig: {key} did not land on {holder.name}"):
            return ""
        return " | ".join(t for t, _ in effect_lines(cur, holder))

    want = {
        "dot": ["Shadow Word: Pain", "Damage over time - Magic", "31 shadow damage each turn",
                "6 turns left", "From Hero"],
        "debuff": ["Sunder Armor", "Debuff - cannot be dispelled", "-120 Armor", "5 turns left"],
        "stun": ["Hammer of Justice", "Stunned - cannot act", "2 turns left"],
        "hot": ["Renew", "Heal over time", "Heals 44 each turn", "5 turns left"],
        "buff": ["Power Word: Fortitude", "Buff", "+20 Stamina", "min left"],
        "shield": ["Power Word: Shield", "Absorbs the next 250 damage", "4 turns left"],
        "curse": ["Curse of Weakness", "Debuff - Curse", "-30 Attack Power", "4 turns left",
                  "From Mangy Wolf"],
    }
    for key, needles in want.items():
        got = text(key)
        for n in needles:
            check(n in got, f"{key}: tooltip should say {n!r}; it says: {got}")
    # our own buffs do not say "From Hero" on Hero
    check("From Hero" not in text("hot"), "an effect you put on yourself should not say 'From <you>'")

    # --- 1 + 2. the combat screen ---------------------------------------------------------
    def hover_all(label):
        scr.mouse_pos = (-50, -50)
        scr.render(surf)
        hits = list(scr._effect_hits)
        for c in (foe, player):
            for e in live(c):
                mine = [r for r, he, h in hits if he is e]
                if not check(mine, f"{label}: {e.name} on {c.name} is drawn nowhere hoverable"):
                    continue
                r = mine[0]
                check(surf.get_rect().contains(r), f"{label}: {e.name}'s square {tuple(r)} is off screen")
                scr.mouse_pos = (-50, -50)
                scr.render(surf)
                before = pygame.image.tostring(surf, "RGB")
                scr.mouse_pos = r.center
                scr.render(surf)
                after = pygame.image.tostring(surf, "RGB")
                check(before != after, f"{label}: hovering {e.name} on {c.name} draws nothing")
                check(scr.hovered_effect is e,
                      f"{label}: hovering {e.name} shows {getattr(scr.hovered_effect, 'name', None)}")
        # squares must not sit on top of each other, or one can never be hovered
        for i, (ra, ea, _) in enumerate(hits):
            for rb, eb, _ in hits[i + 1:]:
                check(not ra.colliderect(rb), f"{label}: {ea.name} and {eb.name} squares overlap")
        scr.mouse_pos = (-50, -50)
        scr.render(surf)
        check(scr.hovered_effect is None, f"{label}: a tooltip shows with the mouse nowhere near")
        return len(hits)

    n_main = hover_all("combat")
    if "--shot" in sys.argv:
        out = sys.argv[sys.argv.index("--shot") + 1]
        for tag, key in (("enemy", "dot"), ("ours", "curse")):
            holder, eff = cases[key]
            cur = next(e for e in holder._effects() if e.effect_id == eff.effect_id)
            scr.mouse_pos = (-50, -50); scr.render(surf)
            surf.fill((0, 0, 0))
            scr.mouse_pos = next(r for r, he, _ in scr._effect_hits if he is cur).center
            scr.render(surf)
            pygame.image.save(surf, out.replace(".png", f"_{tag}.png"))

    # targeting screen
    book = player.ability_book
    heal = book.get_ability("priest_renew") or next(
        (book.get_ability(a) for a in getattr(book, "known_abilities", []) or []), None)
    check(heal is not None, "rig: no priest_renew ability to target with")
    scr.targeting_mode = ("priest_renew", 0, heal, player)
    scr.targeting_valid_targets = [player, foe]
    try:
        n_target = hover_all("targeting")
    except Exception as exc:                                   # a rig problem, say so plainly
        n_target = 0
        check(False, f"rig: targeting screen would not render ({type(exc).__name__}: {exc})")
    scr.targeting_mode = None

    # --- 4. Party screen, Buffs tab -------------------------------------------------------
    from ui.screens.party_screen import PartyScreen
    ps = PartyScreen(sm)
    tab_attr = next((a for a in ("detail_tab", "tab", "active_tab", "current_tab") if hasattr(ps, a)), None)
    n_party = 0
    if check(tab_attr is not None, "rig: cannot find the party screen's tab attribute"):
        setattr(ps, tab_attr, "buffs")
        ps._mouse_override = (-50, -50)
        ps.render(surf)
        hits = list(ps._effect_hits)
        n_party = len(hits)
        shown = [e for e in player._effects() if is_displayable_buff(e)]
        for e in shown:
            mine = [r for r, he, _ in hits if he is e]
            if not check(mine, f"party buffs tab: {e.name} has no hoverable row"):
                continue
            ps._mouse_override = (-50, -50); ps.render(surf)
            before = pygame.image.tostring(surf, "RGB")
            ps._mouse_override = mine[0].center; ps.render(surf)
            check(before != pygame.image.tostring(surf, "RGB"),
                  f"party buffs tab: hovering {e.name} draws nothing")
        if "--shot" in sys.argv and hits:
            surf.fill((0, 0, 0)); ps._mouse_override = hits[0][0].center; ps.render(surf)
            pygame.image.save(surf, sys.argv[sys.argv.index("--shot") + 1].replace(".png", "_party.png"))

    # --- 5. real icons --------------------------------------------------------------------
    for key in ("dot", "hot", "buff", "shield"):
        eff = cases[key][1]
        check(effect_icon_path(eff) is not None,
              f"{eff.name} ({eff.effect_id}) has ability art on disk but the effect square does not find it")

    print(f"{n_main} hoverable effects in combat, {n_target} while targeting, {n_party} on the Party Buffs tab")
    if fails:
        print(f"FAIL {len(fails)}:")
        for f in fails[:40]:
            print("  ", f)
        return 1
    print("effect tooltips OK.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
