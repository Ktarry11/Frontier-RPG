#!/usr/bin/env python3
"""Every buff, debuff, DoT and HoT has a picture - no lettered tiles (backlog H).

    PYTHONPATH=. python3 tools/qa_effect_icons.py

Player effects take their ability's art. Monster effects ("mob_<name>", over a thousand) have
none of their own, so they take a stand-in chosen by what the effect is (ui/effect_tooltip.py).

  1. every stand-in file exists
  2. every monster ability that leaves an effect resolves to a picture
  3. the stand-in fits: a stun reads as a stun, a nature DoT as poison, a fire DoT as fire
"""
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.chdir(ROOT)
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")


def main():
    import pygame
    pygame.init()
    from combat.status_effects import StatusEffect, EffectType
    from ui import effect_tooltip as ET
    bad = []
    for key, name in ET._GENERIC.items():
        if not (ET._AB / f"{name}.png").exists():
            bad.append(f"stand-in for {key} is missing: {name}.png")

    def walk(n):
        if isinstance(n, dict):
            if "name" in n and "kind" in n:
                return [n]
            return [x for v in n.values() for x in walk(v)]
        if isinstance(n, list):
            return [x for v in n for x in walk(v)]
        return []
    kinds = {"dot": EffectType.DOT, "buff": EffectType.BUFF, "debuff": EffectType.DEBUFF}
    seen = 0
    for a in walk(json.load(open("data/creatures/ability_kits.json", encoding="utf-8"))["kits"]):
        if a["kind"] not in kinds:
            continue
        seen += 1
        e = StatusEffect(effect_id="mob_" + a["name"].lower().replace(" ", "_"), name=a["name"],
                         effect_type=kinds[a["kind"]], duration=a.get("duration", 2), potency=1,
                         damage_school=a.get("school"), dispel_type=a.get("dispel_type"),
                         stat_mods=dict(a.get("stat_mods") or {}), is_stun=bool(a.get("is_stun")))
        if ET.effect_icon_or_generic(e) is None:
            bad.append(f"{a['name']} has no picture")
    mk = lambda **kw: StatusEffect(effect_id="mob_x", name="X", duration=2, potency=1, **kw)
    want = [(mk(effect_type=EffectType.DEBUFF, is_stun=True), "stun"),
            (mk(effect_type=EffectType.DOT, damage_school="nature"), "dot_nature"),
            (mk(effect_type=EffectType.DOT, damage_school="fire"), "dot_fire"),
            (mk(effect_type=EffectType.DOT, damage_school="shadow", dispel_type="curse"), "dispel_curse"),
            (mk(effect_type=EffectType.DEBUFF, stat_mods={"armor": -50}), "armor"),
            (mk(effect_type=EffectType.HOT), "hot"), (mk(effect_type=EffectType.BUFF), "buff")]
    for e, key in want:
        if ET.generic_icon_key(e) != key:
            bad.append(f"expected the {key} stand-in, got {ET.generic_icon_key(e)}")
    print(f"{seen} monster effects checked, {len(ET._GENERIC)} stand-ins")
    if bad:
        for b in bad[:20]:
            print("  -", b)
        return 1
    print("\neffect icons OK - nothing shows as a lettered tile.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
