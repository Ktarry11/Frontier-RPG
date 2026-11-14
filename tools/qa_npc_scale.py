"""
No NPC is drawn oversized by accident.

Kyle, 10 Nov: "Girzzik Vaultkeep in BB is like...a fucking giant."

sprite_scale 2.0 belongs to ONE character: MerchantTusk, the troll banker who is deliberately
enormous in Orgrimmar, Undercity and Freewind Post. Girzzik was made from a copy of him - he
was once a goblin "banker" wearing MerchantTusk's name - and when that was corrected the size
came along. A size override is allowed only on an NPC that is a banker; anything else fails.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    bad, sized, seen = [], 0, 0
    for rel in ("data/npcs/ambient_npcs.json", "data/npcs/vendors.json"):
        stack = [json.loads((ROOT / rel).read_text(encoding="utf-8"))]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if node.get("name") and ("npc_id" in node or "vendor_id" in node):
                    seen += 1
                    scale = node.get("sprite_scale")
                    if scale not in (None, 1, 1.0):
                        sized += 1
                        if not node.get("is_banker"):
                            bad.append(f"{node['name']} ({node.get('zone')}): sprite_scale {scale} "
                                       f"and not a banker")
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)
    if seen < 500:
        print(f"FAIL only {seen} NPCs read - the rig is not seeing the NPC files")
        return 1
    print(f"{seen} NPCs, {sized} with a size override")
    if bad:
        print("FAIL:")
        for b in bad:
            print("  ", b)
        return 1
    print("NPC sizes OK - only the bankers are oversized.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
