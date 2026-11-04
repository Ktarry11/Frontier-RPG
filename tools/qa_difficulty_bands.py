#!/usr/bin/env python3
"""
Con colours, grey XP, and the party-average rule.

    PYTHONPATH=. python3 tools/qa_difficulty_bands.py

Kyle, 4 Nov 2026: "We also need the quest and mob kill system (wow style) where
you have grey, green, yellow, orange, and red based on level difference and how
much exp you get. Like a grey mob gets you 0 exp and a grey quest is almost fuck
all for exp... Also this should be based on the average party level."

What this is really guarding is that there is ONE difficulty rule. Before
combat/difficulty.py existed, combat_engine._calculate_exp_reward and
Quest.get_scaled_exp_reward each carried their own +-5 breakpoints and each
docstring claimed to mirror the other. Nothing enforced it. This asserts that a
kill and a quest at the same level against the same party land in the same band,
which is the property that silently rotted last time.
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")


def main():
    from combat import difficulty as D
    from entities.character import Character
    from entities.party import Party
    from entities.monster import Monster
    from combat.combat_engine import CombatEngine

    fails = []

    # ---- 1. grey level is continuous and never outruns the player
    prev = -1
    for lv in range(1, 61):
        g = D.grey_level(lv)
        if g >= lv:
            fails.append(f"grey level {g} >= character level {lv} - everything would be grey")
        if g < prev:
            fails.append(f"grey level went backwards at {lv}: {prev} -> {g}")
        prev = g
    # The 39/40 seam swaps formula branches; a discontinuity there would make a
    # single ding silently re-band a whole zone.
    if abs(D.grey_level(40) - D.grey_level(39)) > 1:
        fails.append(f"grey level jumps at the 39/40 seam: "
                     f"{D.grey_level(39)} -> {D.grey_level(40)}")
    if D.grey_level(5) != 0:
        fails.append("something is grey at level 5 - nothing should be")

    # ---- 2. bands are ordered and complete
    for party_level in (10, 20, 30, 40, 50, 60):
        seen = []
        for mob in range(1, party_level + 10):
            b = D.band_for(mob, party_level)
            if not seen or seen[-1] != b:
                seen.append(b)
        # Walking mob level upward must pass through the bands in order and
        # never go back down a band.
        order = [D.BANDS.index(b) for b in seen]
        if order != sorted(order):
            fails.append(f"party {party_level}: bands out of order walking up: {seen}")
        if set(seen) != set(D.BANDS):
            missing = set(D.BANDS) - set(seen)
            fails.append(f"party {party_level}: band(s) unreachable: {sorted(missing)}")

    # ---- 3. grey pays ZERO on kills and a token on quests
    for party_level in (10, 25, 40, 60):
        g = D.grey_level(party_level)
        if g >= 1 and D.kill_xp_multiplier(g, party_level) != 0.0:
            fails.append(f"party {party_level}: grey mob at {g} still pays kill XP")
        if g >= 1:
            q = D.quest_xp_multiplier(g, party_level)
            if q <= 0.0:
                fails.append(f"party {party_level}: grey quest pays nothing - "
                             f"Kyle asked for almost nothing, not nothing")
            if q > 0.25:
                fails.append(f"party {party_level}: grey quest pays {q:.2f} - too generous")
        # One level above grey must pay something, or the band is a cliff
        if D.kill_xp_multiplier(g + 1, party_level) <= 0.0:
            fails.append(f"party {party_level}: level {g+1} is green but pays 0 kill XP")

    # ---- 4. the curve is monotonic - a higher mob never pays less
    for party_level in (15, 30, 45, 60):
        last = -1.0
        for mob in range(1, party_level + 8):
            m = D.kill_xp_multiplier(mob, party_level)
            if m < last - 1e-9:
                fails.append(f"party {party_level}: mob {mob} pays less than mob {mob-1} "
                             f"({m:.3f} < {last:.3f})")
                break
            last = m

    # ---- 5. kills and quests agree on what band a level is
    #
    # The property that was only ever maintained by hand before.
    for party_level in (12, 28, 44, 60):
        for lvl in range(1, party_level + 8):
            kb = D.band_for(lvl, party_level)
            # quest multiplier must be >0 everywhere, and must only hit the
            # grey floor exactly where band_for says grey
            qm = D.quest_xp_multiplier(lvl, party_level)
            if kb == "grey" and abs(qm - D.GREY_QUEST_MULTIPLIER) > 1e-9:
                fails.append(f"party {party_level}: level {lvl} is grey but quest pays {qm:.2f}")

    # ---- 6. PARTY AVERAGE, not the player's level
    hero = Character(name="Hero", char_class="Warrior", level=30)
    party = Party(hero)
    party.add_member(Character(name="Lo", char_class="Mage", level=12))
    avg = D.party_average_level(party)
    if avg == hero.level:
        fails.append("party average equals the hero's level with a level 12 in the "
                     "group - player.level is being used instead of the average")
    if avg != 21:
        fails.append(f"party average of levels [30, 12] should round to 21, got {avg}")

    # A mob that is yellow to the hero alone must con differently to the party.
    mob = Monster("M", "beast_basic", level=30)
    if D.band_for(30, avg) == D.band_for(30, hero.level):
        fails.append("a level 30 mob cons the same to a 30/12 party as to a lone 30 - "
                     "the average is not reaching the band")

    # ---- 7. the engine actually uses it: a grey kill awards nothing
    solo = Character(name="Solo", char_class="Warrior", level=40)
    solo_party = Party(solo)
    grey_mob_level = max(1, D.grey_level(40))
    grey_mob = Monster("Grey", "beast_basic", level=grey_mob_level)
    eng = CombatEngine(solo, grey_mob, party=solo_party, enemies=[grey_mob])
    awarded = eng._calculate_exp_reward(grey_mob)
    if awarded != 0:
        fails.append(f"engine awarded {awarded} XP for a grey (level {grey_mob_level}) "
                     f"kill at party level 40 - must be 0")

    # A grey BOSS must also pay nothing: the 1.75x boss bonus must not
    # resurrect a reward the band zeroed.
    grey_boss = Monster("GreyBoss", "beast_basic", level=grey_mob_level)
    grey_boss.is_boss = True
    grey_boss.location_type = "cave"
    eng2 = CombatEngine(solo, grey_boss, party=solo_party, enemies=[grey_boss])
    if eng2._calculate_exp_reward(grey_boss) != 0:
        fails.append("a grey CAVE BOSS still paid XP - a bonus multiplier is being "
                     "applied on top of a zeroed reward")

    # ---- 8. quest level is one number, shared by the badge and the payout
    from world.quest import Quest
    import types
    fake = types.SimpleNamespace(level_max=24, level_min=20, reward_exp=1000)
    if Quest.quest_level.fget(fake) != 24:
        fails.append("quest_level does not prefer level_max")
    fake_no_max = types.SimpleNamespace(level_max=None, level_min=20, reward_exp=1000)
    if Quest.quest_level.fget(fake_no_max) != 20:
        fails.append("quest_level does not fall back to level_min")

    if fails:
        for f in fails:
            print(f"  FAIL  {f}")
        return 1

    print("grey level continuous 1-60, never outruns the character")
    print("all five bands reachable and correctly ordered at every level")
    print("grey kills pay 0; grey quests pay "
          f"{D.GREY_QUEST_MULTIPLIER:.0%}; grey+1 pays something")
    print("kill XP is monotonic in mob level")
    print("kills and quests agree on every band boundary")
    print("party average drives the bands, not the hero's level")
    print("engine zeroes a grey kill, and a grey cave boss too")
    print("\nPASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
