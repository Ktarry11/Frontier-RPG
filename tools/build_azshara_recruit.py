#!/usr/bin/env python3
"""Azshara's one recruit: Mohammed Saleh, Chronomancer, at Talrendis Landing. Idempotent.

    PYTHONPATH=. python3 tools/build_azshara_recruit.py            # dry run
    PYTHONPATH=. python3 tools/build_azshara_recruit.py --write

Kyle, 18 Nov 2026: recruits are only ever Earth transplants ("we can ONLY recruit earth transplants"), Azshara gets
one, and of the four offered: "Make Mohammad there". Then: "We never loose an innkeeper though for our hearth", so
his sister Layla keeps the Landing's inn (tools/build_talrendis_landing.py) and he stands by its door.

WHY A CHRONOMANCER (Artificer, the one Chronomancer spec nobody had). Half the Landing dreams of the drowned street,
and Mohammed dreams it clearest: the Promenade as it was ten thousand years ago, with the queen's court walking it
(the quests "Ghosts in His Dreams" and "The Moonguard Revenant" are his dreams). Here the dreams turned into seeing
time. Every ability below quotes the line of his story it comes from and is built only from mechanics other recruit
kits already use (tools/build_sheet4_recruits.py), with five ranks by tools/rank_kit_abilities.py's rule.

ART comes later (docs/azshara_recruit_art_prompt.md): until his sprite and portrait are sliced, the map draws him as
the generic human the Landing already drew him as (ui/tilemap_renderer.py's fallback).
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

from build_sheet4_recruits import A, P, COST  # noqa: E402

RID = "mohammed_chronomancer"
NAME, SPEC, CLS, LEVEL, ZONE = "Mohammed Saleh", "chronomancer_artificer", "Chronomancer", 56, "Talrendis Landing"
POS = (20, 30)                 # by the inn's door, where he kept it before his sister took it on
GENDER, COLOUR, ROW, VARIANT = "male", "#3FA7B5", "back", 4

PROSE = dict(
    greeting=("Sit down, you look tired. Layla keeps the inn now, and I keep the dreams. Lately the dreams are the "
              "busier job."),
    backstory=(
        "Mohammed and his sister Layla ran a guesthouse in Aqaba, on the Red Sea, full of divers who came for the "
        "coral. He's warm, chatty and remembers every guest's name and how they take their tea. When they came "
        "through, he took the first job going, keeping the inn at Talrendis Landing, and then the dreams started: "
        "the same white street running into the sea, every night, with the queen's court walking it. Here the "
        "dreams turned into something he can use, and now he sees a little way along time, backward and forward."),
    before=(
        "Twelve rooms over a dive shop, a rooftop where the guests ate breakfast looking at Sinai, and a sister who "
        "did the books because he was hopeless at them.\n\n"
        "He made the tea himself, every morning, and he never let a guest leave without a second glass."),
    adjustment=(
        "He kept doing what he knew, which was keeping people fed and rested, and it held him together.\n\n"
        "The dreams frightened him until Farseer Thrag told him they were true. After that they mostly made him "
        "curious."),
    forward=(
        "He wants to walk the Drowned Promenade awake, once, and see if it looks the way it does at night.\n\n"
        "Layla wants him to stop dreaming and help with the laundry. He says he can do both."),
    now=(
        "By the inn door at Talrendis Landing, with a glass of tea going cold beside him.\n\n"
        "The brass key on a cord round his neck is the guesthouse's front door key. He still locks up at night, "
        "somewhere in his head."),
    look=("Jordanian man, 41, medium build, warm brown skin, short dark curly hair going grey at the temples, a neat "
          "short beard, kind dark eyes with laugh lines. Deep teal and sand chronomancer robes with brass trim and a "
          "small hourglass at the belt, a staff with a glass orb full of slow-turning sand, a brass key on a cord "
          "round his neck."),
)

KIT = (P("Thirty Guests a Night", "'He's warm, chatty and remembers every guest's name and how they take their tea.'",
         mp5=6, arcane_resistance=10), [
    A(RID, "The Same Street Every Night", "'the same white street running into the sea, every night'",
      "live: reveals_intent and sure_target", "debuff", "enemy", 12, 3, 0,
      "For 3 turns, shows what the target will do next, and the party's attacks on it can't miss.",
      reveals_intent="all", sure_target=True),
    A(RID, "A Second Glass", "'he never let a guest leave without a second glass'",
      "live: immediate repeat_last", "buff", "self", 12, 0, 100,
      "Casts his last ability again at once.", immediate={"action": "repeat_last"}),
    A(RID, "The Sea Gives It Back", "'he sees a little way along time, backward and forward'",
      "live: delayed", "spell_damage", "enemy_aoe", 12, 2, 100,
      "Arcane damage that lands on one enemy row two turns from now.", damage_school="arcane",
      delayed={"turns": 2, "mult": 1.0}),
])


def main():
    write = "--write" in sys.argv
    import contextlib
    import io
    from combat.abilities import get_class_resource
    import rank_kit_abilities as RK
    with contextlib.redirect_stdout(io.StringIO()):
        from tools import handbuilt_talrendis_landing as M
        from tools import ashenvale_town_kit as AK
        L = AK.build(M)
    problems = []
    if not L.z.is_walkable(*POS):
        problems.append(f"{RID}: {POS} isn't walkable in {ZONE}")
    if any(abs(POS[0] - x) + abs(POS[1] - y) < 3 for (x, y) in M.NPC_POSITIONS.values()):
        problems.append(f"{RID}: {POS} is on top of one of the Landing's people")
    from tools.build_tempest_quests import voice_problems
    for k_, v in PROSE.items():
        if k_ != "look":
            problems += [f"{RID} {k_}: {p}" for p in voice_problems(v)]
    gear = json.loads((ROOT / "data/items/spec_gear.json").read_text(encoding="utf-8"))
    if SPEC not in gear:
        problems.append(f"{RID}: no spec {SPEC}")

    rdoc = json.loads((ROOT / "data/npcs/recruits.json").read_text(encoding="utf-8"))
    kdoc = json.loads((ROOT / "data/npcs/personal_kits.json").read_text(encoding="utf-8"))
    rec = {"recruit_id": RID, "name": NAME, "char_class": CLS, "spec": SPEC, "level": LEVEL, "zone": ZONE,
           "x": POS[0], "y": POS[1], "row": ROW, "npc_color": COLOUR, "backstory": PROSE["backstory"],
           "greeting": PROSE["greeting"], "gear_theme": gear.get(SPEC, {}).get("role", "ranged_dps"),
           "home_town": None, "home_x": None, "home_y": None, "home_note": None,
           "gender": GENDER, "appearance_variant": VARIANT,
           "background_sections": {k_: PROSE[k_] for k_ in ("before", "adjustment", "forward", "now")},
           "look": PROSE["look"]}
    res = getattr(get_class_resource(CLS), "value", str(get_class_resource(CLS)))
    passive, abilities = KIT
    for a in abilities:
        a["resource_type"] = res
        if a["ranks"][0]["cost"] is None:
            a["ranks"][0]["cost"] = COST.get(res, 30)
    kdoc[RID] = {"name": NAME, "passives": passive, "abilities": abilities}
    ranked = 0
    for a in kdoc[RID]["abilities"]:
        if RK.grows(a):
            a["ranks"] = RK.ranks_for(a, kdoc)
            ranked += 1
    rdoc["recruits"] = [r for r in rdoc["recruits"] if r["recruit_id"] != RID] + [rec]
    art = [p for p in (f"assets/npcs/recruits/{RID}/down.png", f"assets/ui/portraits/{RID}.png")
           if not (ROOT / p).exists()]
    print(f"  {RID}: {CLS} ({SPEC}) level {LEVEL} at {ZONE} {POS}, {ranked} abilities ranked to 60"
          + (f"; art still to come: {', '.join(art)}" if art else ""))
    for p in problems:
        print("  PROBLEM " + p)
    if write and not problems:
        (ROOT / "data/npcs/recruits.json").write_text(json.dumps(rdoc, indent=2, ensure_ascii=False) + "\n",
                                                      encoding="utf-8")
        (ROOT / "data/npcs/personal_kits.json").write_text(json.dumps(kdoc, indent=2, ensure_ascii=False) + "\n",
                                                           encoding="utf-8")
        print(f"  written: {len(rdoc['recruits'])} recruits")
    elif write:
        print("  REFUSING TO WRITE while there are problems")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
