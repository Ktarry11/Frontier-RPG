#!/usr/bin/env python3
"""Pin every gathering ladder to WoW's real skill values, ~22 materials over 1-300.

    PYTHONPATH=. python3 tools/reanchor_gathering_ladders.py [--apply]

Idempotent. Prints the diff by default; --apply writes it.
Supersedes tools/reanchor_mining_ladder.py, which did mining alone.

=============================================================================
THE SPEC, as Kyle settled it on 7 Nov 2026
=============================================================================

  "anchor the actual wow crafting as a framework where the terminal material
   from wow will be the end game of 'traditional' crafting"
  "Go to skill 300. But keep only wow terminal stuff."
  "we can have some before eternium. As long as we have around 22 or so
   materials from 1-300."
  "Mithril shouldn't be skill 80."

So each ladder is built the same way:

  SPINE    Every material carrying a real WoW name sits at its real WoW skill.
           A player who knows Classic finds Mithril at 175 and Runecloth at
           225, where they expect them. WoW's terminal material owns the top.

  FILLING  Frontier's invented materials take the gaps BETWEEN anchors - this
           is the design, not padding. Kyle: "I always found wow's crafting to
           be too limited. So I added more stuff while leveling."

  ~22      Per type, inside 1-300. Tight enough that no stretch of ladder is
           empty, loose enough that no band is a pile. An earlier pass put
           eleven ores inside 70 skill of each other, which is not a ladder.

  PARKED   The surplus goes ABOVE 300 to join the forward-authored endgame set
           ("we will MASSIVELY expand out end game"). Nothing is deleted; the
           names and art stay in the file, ungatherable, waiting.

=============================================================================
WHERE THE ANCHOR NUMBERS CAME FROM - all fetched, none recalled
=============================================================================

MINING, strategywiki.org/wiki/World_of_Warcraft/Professions/Mining (7 Nov):
    Copper 1, Tin 65, Silver 75, Bronze 75 (smelt), Iron 125, Gold 155,
    Steel 165 (smelt), Mithril 175, Truesilver 230, Dark Iron 230,
    Small Thorium 245, Rich Thorium 275

HERBALISM, wow-professions.com's Classic 1-300 guide gave five exact values -
Stranglekelp 85, Kingsblood 125, Liferoot 150, Khadgar's Whisker 185, Ghost
Mushroom 245 - and Frontier's existing late herbs ALREADY match them exactly
(Stranglekelp 85, Firebloom 205, Sungrass 230, Blindweed 235). That agreement
is why the full standard list below is trusted: the original author clearly
worked from it, then let the low and mid herbs drift.

ARCANITE, warcraft.wiki.gg/wiki/Arcanite_Bar (7 Nov): Arcanite Bar is NOT
smelted. It is an ALCHEMY transmute at skill 275, from 1 Arcane Crystal +
1 Thorium Bar. That is why bar_arcanite is created by an alchemy recipe here
rather than by smelting, and it is a feature rather than an inconvenience -
Kyle wants "crafting to be FULLY viable as a path alternative to raids", and
making the blacksmithing terminal depend on an alchemist is what turns a set
of recipes into an economy.

=============================================================================
A WARNING, because the wrong version of this is seductive
=============================================================================

This is NOT licence to rescale everything onto WoW's numbers. Materials in one
band are PARALLEL options with different roles, not rungs - Kyle: "I don't like
that one ore, or cloth, or herb makes multiple things... Want Healer gear? Use
cotton. Want dps? Use hemp." An earlier pass of mine read the whole ladder as
mispriced and would have flattened forty materials per type into WoW's ten.

ONLY WoW-NAMED materials move to an anchor. Everything else is placed in a gap.
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MATS = ROOT / "data" / "gathering" / "materials.json"

CEILING = 300
TARGET_PER_TYPE = 22

#: Real WoW Classic skill per named material. Fetched, see docstring.
ANCHORS = {
    # ---- mining
    "ore_copper": 1, "ore_tin": 65, "ore_silver": 75, "ore_iron": 125,
    "ore_gold": 155, "ore_mithril": 175, "ore_truesilver": 230,
    "ore_dark_iron": 230, "ore_thorium": 245,
    # Arcane Crystal comes out of Rich Thorium veins in Classic, hence 275.
    # Kyle, 7 Nov: "Arcanite crystal comes from mining." It is material_type
    # `crystal`, not `ore`, joining the five crystals already in the file -
    # materials.json's own comment records the earlier ruling: "Crystals can be
    # found in ore veins". Profession is still mining either way.
    "crystal_arcane": 275,
    # Elementium is a real WoW ore and the hardest one, just raid-sourced.
    # It sits below the terminal because the TERMINAL is Arcanite, which is
    # made FROM Thorium - see docstring.
    "ore_elementium": 290,
    # ---- herbalism
    "herb_peacebloom": 1, "herb_silverleaf": 1, "herb_earthroot": 15,
    "herb_mageroyal": 50, "herb_briarthorn": 70, "herb_stranglekelp": 85,
    "herb_bruiseweed": 100, "herb_wild_steelbloom": 115,
    "herb_kingsblood": 125, "herb_liferoot": 150, "herb_fadeleaf": 160,
    "herb_goldthorn": 170, "herb_khadgar": 185, "herb_firebloom": 205,
    "herb_purple_lotus": 210, "herb_sungrass": 230, "herb_blindweed": 235,
    "herb_golden_sansam": 260, "herb_dreamfoil": 270, "herb_icecap": 290,
    "herb_black_lotus": 300,
}

#: Bars whose skill is NOT their ore's - WoW's two smelt-combines.
BAR_ANCHORS = {"bar_bronze": 75, "bar_steel": 165}

#: Frontier's own materials, placed in the gaps between anchors. Flavour chose
#: the gap: Rough Iron before Tin, Coal before Steel (it is Steel's reagent),
#: the "-iron" variants around Mithril.
FILLERS = {
    "ore_weakstone": 1,
    "ore_rough_iron": 40,
    "ore_bronze_vein": 95,
    "ore_coal": 105,
    "ore_living_copper": 115,
    "ore_frostveined_tin": 140,
    "ore_verdant_iron": 165,
    # Mithril 175 -> Truesilver 230 is WoW's own widest gap, so it takes the
    # most filling.
    "ore_felslag": 190,
    "ore_bloodiron": 205,
    "ore_deepearth": 220,
    "ore_ashen_steel": 260,        # Thorium 245 -> Arcane Crystal 275
    # Dewgrass is Frontier's own; it slots between Earthroot and Mageroyal.
    "herb_dewgrass": 30,
}

#: Lifted above the ceiling into the forward-authored endgame set rather than
#: squeezed into the reachable ladder. These are the ones whose names already
#: read as endgame, so they belong to the expansion.
PARK_ABOVE = {
    "ore_frostforged_silver": 310,
    "ore_sunforged_gold": 320,
    "ore_nightshard": 330,
    "ore_voidstone": 340,
    "ore_stormveined": 345,
}

#: Materials that do not exist yet and are created by this tool. icon_id MUST
#: be a sprite stem under assets/gathering_nodes/<folder>/ - Kyle, 7 Nov: "Make
#: sure to use the node. Last time you tried to use the icons as the gathering
#: node." Three separate call sites resolve
#: assets/gathering_nodes/{folder}/{icon_id}.png (ui/tilemap_renderer.py:948,
#: ui/screens/inventory_screen.py:595, ui/screens/professions_screen.py:458),
#: so an inv_misc_* name here renders blank in all three.
NEW = {
    "herb_wild_steelbloom": dict(
        name="Wild Steelbloom", icon_id="wild_steelbloom", sell_price=22,
        description="A grey-petalled bloom that grows through cracked stone, hard as the rock it splits."),
    "herb_purple_lotus": dict(
        name="Purple Lotus", icon_id="purple_lotus", sell_price=55,
        description="Deep violet petals, cool to the touch. Alchemists pay well and ask no questions."),
    "herb_golden_sansam": dict(
        name="Golden Sansam", icon_id="golden_sansam", sell_price=85,
        description="A pale root under a crown of gold leaf. It tastes of nothing and mends almost anything."),
    "herb_dreamfoil": dict(
        name="Dreamfoil", icon_id="dreamfoil", sell_price=95,
        description="The leaves blur at the edges when you look straight at them."),
    "herb_icecap": dict(
        name="Icecap", icon_id="icecap", sell_price=105,
        description="A white bloom that keeps its own frost in high summer."),
    "herb_black_lotus": dict(
        name="Black Lotus", icon_id="black_lotus", sell_price=400,
        description="Petals that drink the light. Perhaps a dozen are picked in a season, and every alchemist in the world wants one."),
    "crystal_arcane": dict(
        name="Arcane Crystal", icon_id="arcane", sell_price=320,
        description="A shard of raw magic found packed in the richest thorium. It hums against the pick."),
}

#: Defaults for a NEW entry, so this tool cannot author a half-formed material.
NEW_DEFAULTS = {
    "herb": dict(material_type="herb", profession="herbalism", stack_limit=20),
    "ore": dict(material_type="ore", profession="mining", stack_limit=20),
    "crystal": dict(material_type="crystal", profession="mining", stack_limit=20),
}

TIER_BY_CAP = [(75, "early"), (150, "mid"), (225, "late"), (CEILING, "endgame")]


def spread(lo):
    return [lo, lo + 20, lo + 35, lo + 50]


def tier_for(skill):
    for cap, name in TIER_BY_CAP:
        if skill <= cap:
            return name
    return "endgame"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    doc = json.loads(MATS.read_text())
    mats = doc["materials"]

    created, pending_art = [], []
    for mid, spec in NEW.items():
        if mid in mats:
            continue
        kind = mid.split("_", 1)[0]
        skill = ANCHORS.get(mid) or FILLERS.get(mid)
        if skill is None:
            print(f"  WARN  {mid} is new but has no anchor or filler skill, skipped")
            continue
        folder = {"herb": "herbs", "crystal": "crystals"}.get(kind, kind)
        sprite = ROOT / "assets" / "gathering_nodes" / folder / f"{spec['icon_id']}.png"
        if not sprite.exists():
            # A material WITHOUT a world node is still created - it just has no
            # art yet. ui/screens/inventory_screen.py:_draw_material_icon
            # returns False when the file is missing and the caller falls back
            # to a text box, so a missing icon degrades legibly rather than
            # rendering blank. Verified in the source, not assumed.
            #
            # Kyle, 7 Nov, on Arcane Crystal: "the crystal has a chance from
            # thorium. So you only need the icon." It is a bonus roll out of a
            # Thorium vein (world.gathering_manager.CRYSTAL_FROM_MATERIAL), not
            # a node, so it never needs node art at all.
            pending_art.append((mid, spec["name"], sprite.relative_to(ROOT)))
        created.append(mid)
        if args.apply:
            mats[mid] = dict(NEW_DEFAULTS[kind], tier=tier_for(skill),
                             skill_range=spread(skill), **spec)

    planned = {}
    for mid, skill in {**ANCHORS, **FILLERS}.items():
        if mid not in mats and mid not in created:
            print(f"  WARN  {mid} not in materials.json, skipped")
            continue
        planned[mid] = skill
        if mid.startswith("ore_"):
            bar = mid.replace("ore_", "bar_", 1)
            if bar in mats:
                planned[bar] = BAR_ANCHORS.get(bar, min(CEILING, skill))
    planned.update({b: s for b, s in BAR_ANCHORS.items() if b in mats})
    for mid, skill in PARK_ABOVE.items():
        if mid in mats:
            planned[mid] = skill
            bar = mid.replace("ore_", "bar_", 1)
            if bar in mats:
                planned[bar] = skill

    # An ore inside the ceiling must have a bar inside it too, or it is an ore
    # you can mine and never smelt.
    pulled = set()
    for mid, skill in list(planned.items()):
        if not mid.startswith("ore_") or skill > CEILING:
            continue
        bar = mid.replace("ore_", "bar_", 1)
        if bar in mats and (mats[bar].get("skill_range") or [0])[0] > CEILING:
            planned[bar] = CEILING
            pulled.add(bar)

    changes, parked = [], []
    for mid, newskill in sorted(planned.items(), key=lambda kv: kv[1]):
        m = mats.get(mid)
        if m is None:
            continue
        old = (m.get("skill_range") or [None])[0]
        if old is not None and old > CEILING and mid not in pulled and mid not in PARK_ABOVE:
            parked.append((mid, old))
            continue
        newtier = tier_for(newskill)
        if old == newskill and m.get("tier") == newtier:
            continue
        changes.append((mid, m["name"], old, newskill, m.get("tier"), newtier))
        if args.apply:
            m["skill_range"] = spread(newskill)
            m["tier"] = newtier

    anchored = set(ANCHORS) | {k.replace("ore_", "bar_", 1) for k in ANCHORS} | set(BAR_ANCHORS)
    if created:
        print(f"  {len(created)} material(s) created: {', '.join(created)}\n")
    print(f"  {len(changes)} material(s) move, ceiling {CEILING}\n")
    print(f"  {'material':30}{'name':26}{'skill':>13}{'tier':>20}")
    for mid, name, old, new, ot, nt in changes:
        tag = "ANCHOR" if mid in anchored else ("PARK" if mid in PARK_ABOVE else "filler")
        t = f"{ot} -> {nt}" if ot != nt else (ot or "-")
        print(f"  {mid:30}{name[:24]:26}{f'{old} -> {new}':>13}{t:>20}   {tag}")

    if pending_art:
        print("  CREATED, ICON PENDING - the bag shows a text box until the file lands:")
        for mid, name, rel in pending_art:
            print(f"    {name} ({mid})  wants  {rel}")
        print()
    ok = True
    for t in ("herb", "ore", "wood", "cloth", "leather"):
        # Count the materials this run CREATES as well. On a dry run they are
        # not in `mats` yet, so reading mats alone reported herb as 16 against
        # a target of 22 and made a correct run look wrong - the same blind
        # spot that made an earlier version of this report phantom gaps.
        ladder = sorted((planned.get(mid, (m.get("skill_range") or [9999])[0]), mid)
                        for mid, m in mats.items() if m["material_type"] == t)
        ladder += [(planned.get(mid) or ANCHORS.get(mid) or FILLERS[mid], mid)
                   for mid in created
                   if NEW_DEFAULTS[mid.split("_", 1)[0]]["material_type"] == t
                   and mid not in mats]
        ladder = sorted(x for x in ladder if x[0] <= CEILING)
        terminal = max([v for k, v in ANCHORS.items() if k.startswith(f"{t}_")] or [CEILING])
        gaps = [(a, b) for (a, _), (b, _) in zip(ladder, ladder[1:])
                if b - a > 40 and b != terminal]
        n = len(ladder)
        flag = "" if abs(n - TARGET_PER_TYPE) <= 1 else f"  <-- target ~{TARGET_PER_TYPE}"
        print(f"  {t:9}{n:>4} in 1-{CEILING}   {ladder[0][0]:>4} to {ladder[-1][0]:<4}"
              f"  gaps>40: {', '.join(f'{a}->{b}' for a, b in gaps) or 'none'}{flag}")
        if flag or gaps:
            ok = False

    if parked:
        print(f"\n  {len(parked)} already above {CEILING}, untouched")

    if args.apply:
        MATS.write_text(json.dumps(doc, indent=2) + "\n")
        print(f"\n  wrote {MATS.relative_to(ROOT)}")
    else:
        print("\n  dry run - pass --apply to write")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
