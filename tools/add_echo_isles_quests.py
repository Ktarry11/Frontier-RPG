"""
Echo Isles quest chain + Darkspear Refugee Camp (Kyle: "Echo island can
have about a good 7 to 8 quests... build a camp if we need to", and
explicitly flagged this session for getting kill-quest-heavy - this
chain deliberately mixes objective types).

REAL WOW LORE ANCHOR: Zalazane is a real named WoW villain - a renegade
troll shaman who hexed and enslaved his own Darkspear kin on these
islands. This maps directly onto the real creature data already in
data/creatures/encounters.json's Echo Isles table: "Hexed Thrall" and
"Drowned Troll" both use the undead_basic template (already-dead/
reanimated, not merely charmed), which sharpens the horror angle - this
isn't a generic "kill the boss" story, it's specifically about the troll
NPCs already placed in Echo Isles (Jin'zil, Zathra, Kang'ari) having
real personal stakes in a cult that hexes trolls specifically.

STRUCTURE (7 quests, deliberately NOT all kill-count):
1. echo_isles_beast_cull (KILL) - Isle Interior beasts, the one
   traditional kill-clear, establishing the island is genuinely
   dangerous before the real plot starts.
2. echo_isles_camp_supplies (FETCH) - gather coral/shell/jungle
   materials for the refugee camp, ties into the new camp's founding.
3. echo_isles_scout_camps (EXPLORE, position-gated to the Troll Camps
   subzone) - reconnaissance before combat, not a kill quest at all.
4. echo_isles_cultist_purge (KILL) - the actual Troll Camps fight,
   informed by what scouting revealed.
5. echo_isles_relic_recovery (GATHER, non-consumed - Kang'ari wants to
   SEE the hexed totems, not have them destroyed/handed over, so GATHER
   not FETCH) - recovering hexed Darkspear relics, thematically about
   rescue/recovery, not slaughter.
6. echo_isles_tidelord (KILL_BOSS) - Sunken Temple Grotto boss.
7. echo_isles_zalazane (KILL_BOSS) - the real finale.

That's 4 KILL/KILL_BOSS-family objectives and 3 non-kill objectives
(FETCH, EXPLORE, GATHER) across 7 quests - real variety, not a kill-quest
treadmill with different flavor text.

DARKSPEAR REFUGEE CAMP: 2 new troll NPCs added around the existing
Shu the Sage vendor (48,52) - not a new zone_generator layout change
(that's real engine/terrain work out of scope for a quest-content pass),
but a real named cluster of NPCs giving the central clearing an actual
identity as "the camp" rather than just being where the vendor happens
to stand. Terrain at both new spots confirmed grass/walkable before
writing.

ENGINE NOTE (learned from the Skull Rock mistake earlier this session):
Troll Camps is an open Durotar-style subzone tag on the same "Echo
Isles" Tilemap - zone-restricting objective 4's KILL would silently
never match, so it's unrestricted, relying on globally-unique creature
names (verified against creatures.json). Sunken Temple Grotto and
Zalazane's Hollow ARE real separate cave Tilemaps (confirmed via
portal_manager.py) - their KILL_BOSS objectives correctly use the real
normalized zone key (lower/underscore/no-apostrophe), verified against
the actual runtime string before writing, not assumed.

Run once. Adds 2 NPCs to ambient_npcs.json and a new data/quests/
echo_isles.json file.
"""
import json

NEW_NPCS = [
    {
        "npc_id": "echo_isles_camp_quartermaster", "name": "Rask'jin", "zone": "echo_isles",
        "x": 44, "y": 50, "race": "troll", "gender": "male", "appearance_variant": 2, "facing": "right",
        "greeting": "Camp don't build itself, mon. You want to help, dere's always somethin' need gatherin'."
    },
    {
        "npc_id": "echo_isles_camp_lookout", "name": "Vessa Palewind", "zone": "echo_isles",
        "x": 52, "y": 54, "race": "troll", "gender": "female", "appearance_variant": 4, "facing": "left",
        "greeting": "I watch da tree line. Somethin' move wrong out dere, I see it before it sees you."
    }
]

QUESTS = [
    {
        "quest_id": "echo_isles_beast_cull",
        "title": "The Isle Bites Back",
        "description": (
            "Elder Kang'ari doesn't waste words on the beasts of Echo "
            "Isles - raptors, panthers, serpents thick enough in the "
            "interior that the camp's own people can't gather safely "
            "past the tree line. Before anything else gets sorted out "
            "on this island, the immediate danger needs thinning. It's "
            "not glamorous work. It's necessary work."
        ),
        "giver_npc_id": "echo_isles_troll_elder",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "kill",
                "target": "Bloodtalon Raptor",
                "alt_targets": ["Jungle Panther", "Isle Serpent"],
                "count": 10
            }
        ],
        "reward_exp": 560,
        "reward_gold": 2200,
        "accept_text": (
            "Ten of them, any mix - raptor, panther, serpent, the "
            "interior's thick with all three right now. Nothing "
            "personal in this one. Just clearing ground."
        ),
        "turn_in_text": (
            "Good. Da tree line's quieter now. Not safe - dis island "
            "hasn't been safe in longer than you'd guess - but quieter. "
            "Dat's worth something."
        ),
        "next_quest_id": None,
        "level_min": 9,
        "level_max": 12,
        "unique_item_defs": [
            {
                "name": "Bloodtalon Fang Blade", "slot": "main_hand", "item_level": 10,
                "rarity": "uncommon", "weapon_type": "dagger", "stat_template": "agi_physical",
                "primary_stats": {"agility": 6, "stamina": 2},
                "weapon_damage_min": 16, "weapon_damage_max": 21, "attack_speed": 1.7,
                "label": "Dagger (Agi)"
            },
            {
                "name": "Panther-Hide Wraps", "slot": "hands", "item_level": 10,
                "rarity": "uncommon", "armor_type": "leather", "stat_template": "agi_physical",
                "primary_stats": {"agility": 5, "stamina": 3},
                "armor_value": 24,
                "label": "Leather (Agi)"
            }
        ]
    },
    {
        "quest_id": "echo_isles_camp_supplies",
        "title": "Building Something Permanent",
        "description": (
            "Rask'jin is trying to turn a temporary landing spot into an "
            "actual camp, and that means materials - good coral for "
            "binding, shell for tools, sturdy jungle wood, the kind of "
            "unglamorous groundwork nobody writes songs about. He's "
            "matter-of-fact about it: a real camp means the Darkspear "
            "who wash up here have somewhere to land besides open sand."
        ),
        "giver_npc_id": "echo_isles_camp_quartermaster",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "fetch",
                "target": "sturdy_reef_coral",
                "count": 6
            }
        ],
        "reward_exp": 300,
        "reward_gold": 900,
        "accept_text": (
            "Da reef coral you want is da tough kind, not da pretty kind "
            "- deep red, grows near where da current's strongest. Bring "
            "me six pieces and dis camp gets a real palisade instead of "
            "a prayer."
        ),
        "turn_in_text": (
            "Dis is good stock, mon. Palisade's going up by week's end. "
            "You didn't have to help build somethin' dat's not really "
            "your home. Means somethin' dat you did anyway."
        ),
        "next_quest_id": None,
        "level_min": 9,
        "level_max": 11,
        "unique_item_defs": [
            {
                "name": "Reef-Binder's Buckler", "slot": "off_hand", "item_level": 10,
                "rarity": "uncommon", "weapon_type": "shield", "stat_template": None,
                "primary_stats": {"stamina": 6},
                "armor_value": 26,
                "label": "Shield (Sta)"
            }
        ]
    },
    {
        "quest_id": "echo_isles_scout_camps",
        "title": "Eyes on the Cultists",
        "description": (
            "Vessa Palewind watches the tree line for a living, and "
            "she's seen enough movement toward the eastern camps to want "
            "real eyes on the ground before anyone commits to a fight. "
            "The Troll Camps aren't just hostile territory - they're "
            "Darkspear territory, held now by Zalazane's cultists, which "
            "makes every report back from there personal in a way Vessa "
            "doesn't bother hiding."
        ),
        "giver_npc_id": "echo_isles_camp_lookout",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "explore",
                "target": "Troll Camps",
                "target_x": 75,
                "target_y": 48,
                "radius": 10
            }
        ],
        "reward_exp": 280,
        "reward_gold": 800,
        "accept_text": (
            "Don't engage. I mean dat - just get eyes on da camp layout "
            "and get back here. We fight smart on dis one, not angry, "
            "no matter how angry it deserves to make you."
        ),
        "turn_in_text": (
            "Good. Now we know what we're walkin' into. Dat's worth more "
            "dan you'd think - most people who die out dere die because "
            "dey walked in blind."
        ),
        "next_quest_id": "echo_isles_cultist_purge",
        "level_min": 9,
        "level_max": 11
    },
    {
        "quest_id": "echo_isles_cultist_purge",
        "title": "The Camps Answer For It",
        "description": (
            "With Vessa's scouting report in hand, Elder Kang'ari is "
            "ready to send fighters into the Troll Camps for real. Voodoo "
            "trolls, hex trolls, Zalazane's berserkers and headhunters - "
            "all of them Darkspear once, all of them lost to whatever "
            "hold Zalazane has over them now. Kang'ari doesn't ask you to "
            "feel good about this fight. He asks you to finish it."
        ),
        "giver_npc_id": "echo_isles_troll_elder",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "kill",
                "target": "Voodoo Troll",
                "alt_targets": ["Hex Troll", "Zalazane Berserker", "Isle Headhunter"],
                "count": 12
            }
        ],
        "reward_exp": 620,
        "reward_gold": 2600,
        "accept_text": (
            "Twelve of dem. I won't lie to you about what dat means - "
            "every one of dem used to be someone's kin, someone's name "
            "before Zalazane took it. Do it anyway. Dey're not comin' "
            "back from what he did to dem."
        ),
        "turn_in_text": (
            "It's done. I felt every one of dose losses, even da ones "
            "dat happened years before you ever set foot on dis island. "
            "Da camps are quiet now. Zalazane still has da temple and "
            "his own hollow. Dat's where dis really ends."
        ),
        "next_quest_id": "echo_isles_relic_recovery",
        "level_min": 10,
        "level_max": 12,
        "unique_item_defs": [
            {
                "name": "Hexbreaker's Cleaver", "slot": "main_hand", "item_level": 11,
                "rarity": "uncommon", "weapon_type": "axe_1h", "stat_template": "str_physical",
                "primary_stats": {"strength": 6, "stamina": 4},
                "weapon_damage_min": 19, "weapon_damage_max": 25, "attack_speed": 2.5,
                "label": "Axe (Str)"
            },
            {
                "name": "Voodoo Adept's Totem-Rod", "slot": "main_hand", "item_level": 11,
                "rarity": "uncommon", "weapon_type": "wand", "stat_template": "int_caster",
                "primary_stats": {"intellect": 7},
                "weapon_damage_min": 12, "weapon_damage_max": 16, "attack_speed": 1.9,
                "label": "Wand (Int)"
            }
        ]
    },
    {
        "quest_id": "echo_isles_relic_recovery",
        "title": "What Zalazane Took",
        "description": (
            "Before the final push, Kang'ari wants something recovered, "
            "not destroyed - hexed Darkspear totems scattered through "
            "what's left of the camps, fetishes twisted by Zalazane's "
            "magic but not beyond recognizing. He wants to SEE them, "
            "study what was done, maybe find a way to undo some of it "
            "for the trolls still lost out there. This isn't about "
            "killing anything else. It's about understanding what "
            "happened here."
        ),
        "giver_npc_id": "echo_isles_troll_elder",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "gather",
                "target": "hexed_darkspear_totem",
                "count": 5
            }
        ],
        "reward_exp": 340,
        "reward_gold": 1000,
        "accept_text": (
            "Five totems. Just bring dem to me, don't touch da magic "
            "still on dem if you can help it - I've seen what dat kind "
            "of hex does to someone who handles it careless."
        ),
        "turn_in_text": (
            "Dis... dis tells me more dan I expected. Da hex isn't as "
            "permanent as I feared. Dere may be a way back for some of "
            "dem, someday. Not today. But someday. Keep dat hope wherever "
            "you carry hope, whatever dat looks like for you."
        ),
        "next_quest_id": "echo_isles_tidelord",
        "level_min": 10,
        "level_max": 12
    },
    {
        "quest_id": "echo_isles_tidelord",
        "title": "The Drowned Temple",
        "description": (
            "The Sunken Temple Grotto floods with the tide and empties "
            "with it, and something ancient has claimed the flooded "
            "chambers as its own - Tidelord Gharesh, an elemental bruiser "
            "that Kang'ari suspects Zalazane either summoned or simply "
            "failed to stop. Either way, it guards ground the Darkspear "
            "used to hold sacred, and Kang'ari wants it gone before "
            "anyone worries about reclaiming what's underneath."
        ),
        "giver_npc_id": "echo_isles_troll_elder",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Tidelord Gharesh",
                "count": 1,
                "zone": "sunken_temple_grotto"
            }
        ],
        "reward_exp": 880,
        "reward_gold": 3400,
        "accept_text": (
            "It moves with da tide - stronger when da water's high, "
            "slower when it's not. Time it right and dis fight is "
            "winnable. Time it wrong and you're fightin' a flood dat "
            "hits back."
        ),
        "turn_in_text": (
            "Da temple's quiet. Whatever dat thing was guardin', it's "
            "safe now, at least from dat. One name left, mon. Da one dat "
            "started all of dis."
        ),
        "next_quest_id": "echo_isles_zalazane",
        "level_min": 11,
        "level_max": 13,
        "unique_item_defs": [
            {
                "name": "Gharesh's Tidal Core", "slot": "off_hand", "item_level": 12,
                "rarity": "rare", "weapon_type": None, "stat_template": "int_caster",
                "primary_stats": {"intellect": 7, "spirit": 3},
                "flavor_text": "It shifts weight in your hand like it's still keeping time with a tide that isn't there anymore.",
                "label": "Off-Hand (Int)"
            }
        ]
    },
    {
        "quest_id": "echo_isles_zalazane",
        "title": "Zalazane",
        "description": (
            "Zalazane's Hollow is the last of it - the source, the "
            "witch doctor who turned his own kin into hexed and drowned "
            "things rather than lead them honestly. Kang'ari has waited "
            "a long time to say this name to someone capable of ending "
            "it. He doesn't dress up what this fight means to him. "
            "Zalazane didn't just attack the Darkspear. He took them, "
            "one hex at a time, and wore their loyalty like something "
            "he'd earned instead of stolen."
        ),
        "giver_npc_id": "echo_isles_troll_elder",
        "zone": "echo_isles",
        "objectives": [
            {
                "type": "kill_boss",
                "target": "Zalazane",
                "count": 1,
                "zone": "zalazanes_hollow"
            }
        ],
        "reward_exp": 1100,
        "reward_gold": 4600,
        "accept_text": (
            "He's da strongest hexer I've ever seen, and I've seen a "
            "few. He'll try to turn your own party against you before "
            "he ever raises a weapon himself. Break da hex fast or don't "
            "let it land at all. Dat's da whole fight, really."
        ),
        "turn_in_text": (
            "It's over. Zalazane is finished, and dis island belongs to "
            "da livin' again, not to whatever he was tryin' to make of "
            "it. I've carried dis a long time. I don't fully know how to "
            "put down a weight dat old, but I suspect I'll figure it out "
            "startin' today. Take what he had. You've more than earned "
            "it, and I mean dat as far more dan words."
        ),
        "next_quest_id": None,
        "level_min": 12,
        "level_max": 13,
        "unique_item_defs": [
            {
                "name": "Zalazane's Broken Fetish", "slot": "main_hand", "item_level": 13,
                "rarity": "rare", "weapon_type": "staff", "stat_template": "int_caster",
                "primary_stats": {"intellect": 9, "spirit": 5},
                "weapon_damage_min": 34, "weapon_damage_max": 44, "attack_speed": 3.0,
                "flavor_text": "The hex magic in it is dead now, snuffed out the moment he fell. It still hums faintly anyway, like habit.",
                "label": "Staff (Int)"
            },
            {
                "name": "Darkspear Reclamation Circlet", "slot": "head", "item_level": 13,
                "rarity": "rare", "stat_template": "str_physical",
                "primary_stats": {"strength": 6, "stamina": 7},
                "flavor_text": "Kang'ari says it belonged to a chieftain before Zalazane melted it down for parts. He had it reforged the moment word reached camp.",
                "label": "Head (Str/Sta)"
            }
        ]
    }
]


def main():
    npc_path = "data/npcs/ambient_npcs.json"
    npc_data = json.load(open(npc_path))
    existing_ids = {n["npc_id"] for n in npc_data["npcs"]}
    added_npcs = []
    for n in NEW_NPCS:
        if n["npc_id"] in existing_ids:
            continue
        npc_data["npcs"].append(n)
        added_npcs.append(n["npc_id"])
    json.dump(npc_data, open(npc_path, "w"), indent=2)
    print(f"Added {len(added_npcs)} camp NPCs: {added_npcs}")

    # Register the FETCH item drop (sturdy_reef_coral) - Vulture/panther/
    # raptor kills in the interior are the natural drop source, matching
    # the "gathering materials while clearing the interior" framing.
    qd_path = "data/creatures/quest_drops.json"
    qd_data = json.load(open(qd_path))
    if "Jungle Panther" not in qd_data["drops"]:
        qd_data["drops"]["Jungle Panther"] = []
    qd_data["drops"]["Jungle Panther"].append({
        "item_id": "sturdy_reef_coral",
        "name": "Sturdy Reef Coral",
        "category": "quest",
        "description": "Deep-red reef coral, tougher than the decorative kind - good for binding a palisade together.",
        "chance": 0.45
    })
    # hexed_darkspear_totem drops from the Troll Camps cultists themselves
    for creature in ["Voodoo Troll", "Hex Troll"]:
        if creature not in qd_data["drops"]:
            qd_data["drops"][creature] = []
        qd_data["drops"][creature].append({
            "item_id": "hexed_darkspear_totem",
            "name": "Hexed Darkspear Totem",
            "category": "quest",
            "description": "A Darkspear fetish, twisted by Zalazane's hex but not beyond recognizing. Still warm with old magic.",
            "chance": 0.5
        })
    json.dump(qd_data, open(qd_path, "w"), indent=2)
    print("Registered sturdy_reef_coral and hexed_darkspear_totem quest drops")

    q_path = "data/quests/echo_isles.json"
    q_data = {"quests": QUESTS}
    json.dump(q_data, open(q_path, "w"), indent=2)
    print(f"Wrote {len(QUESTS)} quests to {q_path}")


if __name__ == "__main__":
    main()
