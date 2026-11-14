"""
Populate Echo Isles with troll NPCs (Kyle: "populate echo isles"),
following up on the troll race art built this session (see
world/race_registry.py's _TROLL_VARIANTS and echo_isles population mix
update, and tools/recolor_trolls.py-equivalent work that produced
assets/npcs/troll/troll_1..6).

3 trolls, matching the population mix's 15% share against the existing
7-NPC Echo Isles roster (~2-3 trolls to ~5 orcs/goblin/skeleton feels
proportionate without overcrowding a small island zone). Written as
people who ended up on these isles alongside the orcs, not just
orc-flavored dialogue in troll skin - real troll cultural texture
(spirits, jungle/reef life before this, a different relationship to the
Horde than the orcs who founded it).

Coordinates checked against real generated Echo Isles terrain before
writing (all confirmed grass/walkable, no collision) - carving still
applies automatically via ZoneManager._place_ambient_npc_tiles as a
safety net regardless.

Run once. Appends to ambient_npcs.json's "npcs" list.
"""
import json

NEW_NPCS = [
    {
        "npc_id": "echo_isles_troll_beachcomber", "name": "Jin'zil", "zone": "echo_isles",
        "x": 35, "y": 58, "race": "troll", "gender": "male", "appearance_variant": 3, "facing": "down",
        "greeting": "Dis island remember more than da orcs who live on it now, mon. Da spirits still talk, if you know how to listen."
    },
    {
        "npc_id": "echo_isles_troll_healer", "name": "Zathra Voodoo-Eye", "zone": "echo_isles",
        "x": 52, "y": 38, "race": "troll", "gender": "female", "appearance_variant": 1, "facing": "right",
        "greeting": "You bleedin'? No? Den come back when you are. I don't do idle chat, mon, I do mendin'."
    },
    {
        "npc_id": "echo_isles_troll_elder", "name": "Elder Kang'ari", "zone": "echo_isles",
        "x": 70, "y": 52, "race": "troll", "gender": "male", "appearance_variant": 5, "facing": "left",
        "greeting": "My people wandered long before we washed up here. Da orcs gave us a place to stop wanderin'. Dat's worth somethin', mon."
    }
]


def main():
    path = "data/npcs/ambient_npcs.json"
    d = json.load(open(path, encoding="utf-8"))
    before = len(d["npcs"])
    d["npcs"].extend(NEW_NPCS)
    json.dump(d, open(path, "w", encoding="utf-8"), indent=2)
    print(f"Added {len(NEW_NPCS)} troll NPCs to Echo Isles ({before} -> {len(d['npcs'])} total ambient NPCs).")
    for n in NEW_NPCS:
        print(f"  {n['name']} ({n['npc_id']}) at ({n['x']},{n['y']})")


if __name__ == "__main__":
    main()
