"""An attack with no real cooldown must end the turn.

Playtest, 12 Nov: "Does maul have a stun hidden in it? Seems like every time I use it I can go
with my druid again right after. Can chain multiple maul attacks and just keep going until my
rage is empty." It was not a stun: Maul was marked instant, and instant means the cast does
not end your turn. Fourteen no-cooldown attacks were.
"""
import glob
import json
import os
import sys

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)


def main():
    from combat.abilities import _ability_from_data
    bad, seen, were = [], 0, 0
    entries = []
    for path in sorted(glob.glob("data/abilities/*.json")) + ["data/npcs/personal_kits.json", "data/races/racials.json"]:
        data = json.load(open(path))
        stack = [data]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if "ability_id" in node and "effect_type" in node:
                    entries.append(node)
                else:
                    stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    for entry in entries:
        try:
            ab = _ability_from_data(entry)
        except Exception:
            continue
        seen += 1
        hostile = ab.effect_type in ("damage", "dot", "debuff")
        if entry.get("is_instant") and hostile and (ab.cooldown or 0) < 2:
            were += 1
        if ab.is_instant and hostile and (ab.cooldown or 0) < 2:
            bad.append(f"{ab.name} ({ab.ability_id}) is a free action every turn")

    maul = next((e for e in entries if e["ability_id"] == "druid_maul"), None)
    if maul is None:
        bad.append("druid_maul is not in the data")
    else:
        ab = _ability_from_data(maul)
        if ab.is_instant:
            bad.append("Maul is still instant")

    print(f"{seen} abilities read; {were} no-cooldown attacks were authored instant and now cost the turn")
    if bad:
        print(f"\n{len(bad)} problem(s):")
        for b in bad:
            print("  -", b)
        return 1
    print("\ninstant attacks OK - nothing that hurts the enemy can be chained for free.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
