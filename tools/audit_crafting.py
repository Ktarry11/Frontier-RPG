#!/usr/bin/env python3
"""Is crafting a real way to gear a character from 1 to 60? Measure it against the other two paths.

    PYTHONPATH=. python3 tools/audit_crafting.py [--slots]

Kyle, 2026-10-28: "My vision is that players can have a fully viable end game loot from crafting or
raids. And we have dungeons and open world to gear up from 1 to 60, crafting shouldn't be any
different (eventually)."

THE TEST THAT MATTERS IS NOT "DO RECIPES EXIST". It is whether a player who picks a profession can
dress themselves out of it the whole way up, and arrive at 60 wearing something worth wearing. So
this compares crafting against the two paths that already work, at every five levels, on the three
things that decide whether gear is worth equipping:

    item level   - is the piece current, or is it already behind when you can first make it?
    rarity       - common and uncommon are filler; rare and epic are what people chase
    coverage     - can you fill every slot, in your own armour class?

TWO CONSTRAINTS MAKE THIS A LEVEL QUESTION AND NOT A SKILL QUESTION.

First, skill caps are gated by CHARACTER level, not by effort: Apprentice 75 at level 1, Journeyman
150 at 10, Expert 225 at 25, Artisan 300 at 40. So a recipe at skill 208 is unreachable before level
25 no matter how much you grind, and the honest question for each band is "what can someone of this
level actually have the skill to make".

Second, crafted gear is not meant to be judged bare. Upgrade kits are the mechanism that keeps it
competitive: two applications take a piece up two rarity steps and +5 item levels. A fair comparison
against a dungeon drop uses the upgraded figure, so this reports both.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

#: (character level required, skill cap) from data/professions/professions.json.
TIERS = [(1, 75), (10, 150), (25, 225), (40, 300)]

#: What two upgrade kits add - world/upgrade_manager ILVL_GAIN and the rarity ladder.
KIT_ILVL = 5
KIT_RARITY_STEPS = 2
RARITY_ORDER = ["poor", "common", "uncommon", "rare", "epic", "legendary"]

ARMOUR_SLOTS = ["head", "shoulder", "chest", "wrist", "hands", "waist", "legs", "feet", "back"]


def live_cap():
    """The highest level any creature in the game actually reaches.

    A material "first obtainable at level 60" is not obtainable at all while nothing is level 60,
    so every gate is tested against this as well as against the character's level. Without it the
    audit credits a level-60 character with gear whose leather comes off creatures that do not
    exist, which is the difference between what has been authored and what can be made.
    """
    creatures = json.loads((ROOT / "data/creatures/creatures.json").read_text(encoding="utf-8"))["creatures"]
    return max((max(c.get("level_range") or [1]) for c in creatures.values()), default=1)


LIVE = None


def skill_cap(level):
    cap = 0
    for req, c in TIERS:
        if level >= req:
            cap = c
    return cap


def bump(rarity, steps=KIT_RARITY_STEPS):
    if rarity not in RARITY_ORDER:
        return rarity
    return RARITY_ORDER[min(len(RARITY_ORDER) - 2, RARITY_ORDER.index(rarity) + steps)]


def material_gate():
    """{material: the character level at which the world first offers it}."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("qm", ROOT / "tools/qa_materials.py")
    qm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(qm)
    first = dict(qm.obtainable())
    from entities.material_tiers import HIGH_TIER, HIGH_TIER_FLOOR
    for m in HIGH_TIER:
        first[m] = max(first.get(m, HIGH_TIER_FLOOR), HIGH_TIER_FLOOR)
    # Intermediate steps inherit the gate of whatever they are made from: a Bolt of Thistledown is
    # only as reachable as the cloth that goes into it.
    # SMELTING IS NOT IN data/*/recipes.json. It lives in data/gathering/smelting_recipes.json and
    # it is the only route from ore to bars, so leaving it out gave every bar a gate of "never".
    # That reported blacksmithing as having 109 of its 115 recipes unmakeable and a ceiling of item
    # level 0 - a profession the game has shipped for months. The verifier was wrong, not the data.
    for _pass in range(4):
        for f in [ROOT / "data/gathering/smelting_recipes.json"] + \
                 sorted(ROOT.glob("data/*/recipes.json")):
            doc = json.loads(f.read_text(encoding="utf-8"))
            buckets = ([b.get("recipes", {}) for b in doc.get("professions", {}).values()]
                       if "professions" in doc else [doc.get("recipes", {})])
            for recipes in buckets:
                for r in recipes.values():
                    if not isinstance(r, dict):
                        continue
                    o = r.get("output") or {}
                    mid = o.get("material_id") if isinstance(o, dict) else o
                    if not mid or not r.get("inputs"):
                        continue
                    need = max((first.get(m, 999) for m in r["inputs"]), default=999)
                    if need < first.get(mid, 999):
                        first[mid] = need
    return first


def crafted():
    """[(profession, skill, ilvl, rarity, kind, slot, armour_type)] for every craftable piece.

    `gate` on each row is the character level at which the RAREST input first exists in the world.
    Without it this audit measures what has been authored rather than what can be made: the entire
    item-level 44 to 68 leatherworking tier - 22 recipes, the only crafted gear above dungeon
    quality anywhere - needs leather off level-60 creatures, and no creature in the game is above
    level 40. Judged on paper leatherworking is the one profession that reaches the endgame. Judged
    on what a player can actually hold, it stops where everything else does.
    """
    gates = material_gate()
    out = []
    for f in sorted(ROOT.glob("data/*/recipes.json")):
        doc = json.loads(f.read_text(encoding="utf-8"))
        buckets = ([(p, b.get("recipes", {})) for p, b in doc.get("professions", {}).items()]
                   if "professions" in doc else [(f.parent.name, doc.get("recipes", {}))])
        for prof, recipes in buckets:
            for rid, r in recipes.items():
                if not isinstance(r, dict):
                    continue
                o = r.get("output") or {}
                if o.get("kind") not in ("armor", "weapon"):
                    continue
                gate = max((gates.get(m, 999) for m in (r.get("inputs") or {})), default=1)
                out.append((prof, r.get("skill_required", 0), o.get("item_level") or 1,
                            o.get("rarity", "common"), o["kind"], o.get("slot"),
                            o.get("armor_type") or o.get("weapon_type"), r.get("name", rid), gate))
    return out


def dungeon_loot():
    """[(item_level, rarity, required_level, slot)] from every hand-authored boss table."""
    out = []
    for f in sorted((ROOT / "data/loot").glob("*_boss_loot.json")):
        for boss, pool in json.loads(f.read_text(encoding="utf-8")).items():
            if boss.startswith("_") or not isinstance(pool, list):
                continue
            for it in pool:
                if isinstance(it, dict):
                    out.append((it.get("item_level") or 1, it.get("rarity", "common"),
                                it.get("required_level") or 1, it.get("slot")))
    return out


def quest_gear():
    """[(gear_level, level_min)] for every quest that rewards gear."""
    out = []
    for f in sorted((ROOT / "data/quests").glob("*.json")):
        for q in json.loads(f.read_text(encoding="utf-8")).get("quests") or []:
            if not isinstance(q, dict):
                continue
            gl = q.get("gear_reward_gear_level")
            if gl:
                out.append((gl, q.get("level_min", 1), q.get("gear_reward_rarity")))
            for d in q.get("unique_item_defs") or []:
                if isinstance(d, dict) and d.get("item_level"):
                    out.append((d["item_level"], q.get("level_min", 1), d.get("rarity")))
    return out


def main():
    global LIVE
    LIVE = live_cap()
    craft, dung, quests = crafted(), dungeon_loot(), quest_gear()
    blocked = [c for c in craft if c[8] > LIVE]
    print(f"== the highest-level creature in the game is {LIVE}, so {len(blocked)} of "
          f"{len(craft)} craftable pieces have materials that do not drop from anything yet")

    print(f"== {len(craft)} craftable pieces, {len(dung)} hand-authored dungeon drops, "
          f"{len(quests)} quest gear rewards\n")

    print("GEARING PATHS SIDE BY SIDE. 'best craftable' is the highest item level someone of this")
    print("level has the SKILL CAP to make; '+kits' is that piece with two upgrade kits on it.\n")
    print(f"  {'level':<7}{'skill cap':<11}{'best craftable':<16}{'+kits':<8}"
          f"{'best dungeon':<14}{'best quest':<12}{'verdict':<26}{'limited by'}")
    for level in range(5, 61, 5):
        cap = skill_cap(level)
        # A piece has to be WEARABLE at this level, not merely makeable. Crafted gear's
        # required_level is item_level - 2 (loot_generator.generate_armor_piece), and the first
        # version of this ignored that - so it compared an ilvl-20 robe you cannot equip until 18
        # against a dungeon drop usable at 5, and reported crafting "competitive" at every level
        # including the ones where nothing exists.
        mine = [c for c in craft if c[1] <= cap and max(1, c[2] - 2) <= level and c[8] <= min(level, LIVE)]
        best = max((c[2] for c in mine), default=0)
        best_rar = max((RARITY_ORDER.index(c[3]) for c in mine if c[2] == best), default=0)
        d = [x for x in dung if x[2] <= level]
        bd = max((x[0] for x in d), default=0)
        q = [x for x in quests if x[1] <= level]
        bq = max((x[0] for x in q), default=0)
        upgraded = best + KIT_ILVL
        peers = max(bd, bq)
        if peers == 0:
            verdict = "no peer content at this level"
        elif upgraded >= peers:
            verdict = "competitive"
        else:
            verdict = f"behind by {peers - upgraded}"
        # Which constraint is doing the work. The question is whether LIFTING THE SKILL CAP would
        # let this character wear anything better - not whether some higher-ilvl recipe exists,
        # which it almost always does and which told us nothing.
        no_cap = [c for c in craft if max(1, c[2] - 2) <= level and c[8] <= min(level, LIVE)]
        binding = "skill cap" if max((c[2] for c in no_cap), default=0) > best else "authored content"
        print(f"  {level:<7}{cap:<11}{best:<4}{RARITY_ORDER[best_rar]:<12}{upgraded:<8}"
              f"{bd:<14}{bq:<12}{verdict:<26}{binding}")

    # ---------------------------------------------------------------- rarity ceiling
    print("\nRARITY. What crafting can produce at all, before and after kits:")
    counts = defaultdict(int)
    for c in craft:
        counts[c[3]] += 1
    for r in RARITY_ORDER:
        if counts[r]:
            print(f"  {r:<12}{counts[r]:>4} recipes   -> {bump(r)} with two kits")
    dr = defaultdict(int)
    for x in dung:
        dr[x[1]] += 1
    print("  dungeon drops for comparison: "
          + ", ".join(f"{n} {r}" for r, n in sorted(dr.items(), key=lambda kv: -kv[1])))

    # ---------------------------------------------------------------- coverage
    print("\nCOVERAGE. Can you fill every slot in your own armour class, at each cap?")
    for level, label in ((9, "1-9  (Apprentice 75)"), (24, "10-24 (Journeyman 150)"),
                         (39, "25-39 (Expert 225)"), (60, "40-60 (Artisan 300)")):
        cap = skill_cap(level)
        print(f"\n  {label}")
        for atype in ("cloth", "leather", "mail", "plate"):
            have = {c[5] for c in craft if c[1] <= cap and c[4] == "armor" and c[6] == atype
                    and c[5] in ARMOUR_SLOTS and c[8] <= min(level, LIVE)}   # 'ranged'/'trinket' aren't body slots
            missing = [s for s in ARMOUR_SLOTS if s not in have]
            state = "all nine slots" if not missing else f"missing {', '.join(missing)}"
            print(f"     {atype:<9}{len(have)}/9   {state}")
        wt = sorted({c[6] for c in craft if c[1] <= cap and c[4] == "weapon" and c[6]
                     and c[8] <= min(level, LIVE)})
        print(f"     weapons  {len(wt):<4} {', '.join(wt) if wt else 'none'}")

    # ---------------------------------------------------------------- the top end
    print("\nTHE TOP END. Kyle's bar is that crafting can dress you at 60.")
    top = sorted(craft, key=lambda c: -c[2])[:8]
    print(f"  highest item levels crafting offers at all:")
    for prof, skill, ilvl, rar, kind, slot, atype, name, gate in top:
        reach = "makeable" if gate <= 40 else f"NEEDS LEVEL {gate} MATERIALS"
        print(f"     ilvl {ilvl:<4} {rar:<9} skill {skill:<4} {prof:<15}{name:<30}{reach}")
    dtop = max((x[0] for x in dung), default=0)
    print(f"  highest hand-authored dungeon item level: {dtop}")
    print(f"  highest crafted, with two kits:            {max(c[2] for c in craft) + KIT_ILVL}")

    # ---------------------------------------------------------------- the level-60 question
    print("\nDRESSING A LEVEL 60. Pieces that a level 60 can both make (skill cap 300) and wear:")
    at60 = [c for c in craft if c[1] <= 300 and max(1, c[2] - 2) <= 60 and c[8] <= min(60, LIVE)]
    for atype in ("cloth", "leather", "mail", "plate"):
        slots = {}
        for c in at60:
            if c[4] == "armor" and c[6] == atype and c[5] in ARMOUR_SLOTS:
                if c[5] not in slots or c[2] > slots[c[5]][2]:
                    slots[c[5]] = c
        missing = [sl for sl in ARMOUR_SLOTS if sl not in slots]
        avg = sum(c[2] for c in slots.values()) / len(slots) if slots else 0
        print(f"  {atype:<9}{len(slots)}/9 slots   best-in-slot average ilvl {avg:5.1f}   "
              + ("full set" if not missing else f"no {', '.join(missing)}"))
    skills = sorted(c[1] for c in craft)
    print(f"  highest skill any recipe asks for: {skills[-1]} (the Artisan cap is 300, so "
          f"{300 - skills[-1]} points of skill have nothing to make)")

    if "--slots" in sys.argv:
        print("\nEVERY CRAFTED PIECE BY SLOT AND ARMOUR TYPE")
        by = defaultdict(list)
        for c in craft:
            by[(c[6], c[5])].append(c)
        for key in sorted(by, key=lambda k: (str(k[0]), str(k[1]))):
            pieces = sorted(by[key], key=lambda c: c[2])
            print(f"  {str(key[0]):<12}{str(key[1]):<10}{len(pieces):>3}  "
                  f"ilvl {pieces[0][2]}-{pieces[-1][2]}")
    return 0


def _level_for(skill):
    """Lowest character level whose skill cap reaches this recipe."""
    for req, cap in TIERS:
        if skill <= cap:
            return req
    return 40


if __name__ == "__main__":
    sys.exit(main())
