#!/usr/bin/env python3
"""Reputation rewards, the way TBC did them: every faction's quartermaster sells by standing.

    PYTHONPATH=. python3 tools/build_faction_rewards.py         # write
    PYTHONPATH=. python3 tools/build_crafted_gear.py             # then author the exalted recipes' epics
    PYTHONPATH=. python3 tools/build_recipe_vendors.py           # then keep town shelves honest

Kyle, 15 Nov 2026: "Each exalted rep will give epic ilvl73 items... friendly and honored can give some stuff.
Revered give lvl 60 ilvl 67 blues and exalted gives lvl 60 ilvl 73 epics. The items should be reflective of the
faction and make sense logically! ... aim for 6 blues per vendor AND 3 epics per vendor. There will also be
crafting stuff for rep. I WANT THIS TO BE LIKE HOW TBC DEALS WITH REP!!!" Then: "I want the epics to be around
250g to 350g", and "exalted rep recipes make epics as well! Around Ilvl 73 (but needs a lot of rare
ingredients! We can add these later)". All nine factions, one quartermaster each (his answers, same day).

HOW TBC DID IT (looked up first: warcraft.wiki.gg "Burning Crusade reputation rewards", wowpedia "Cenarion
Expedition", icy-veins' Sha'tar guide). Friendly is supplies and a cheap pattern or two. Honored is the big
tier of patterns, plans and formulas. Revered is the faction's blues and its better recipes. Exalted is a
handful of signature epics in the faction's own colours (the Cenarion Expedition's Earthwarden, a feral
tank's maul, at 265g; Ashyen's Gift and Windcaller's Orb at 79g; the Sha'tar's Gavel of Pure Light) and its
best recipes. Here, per faction:

    friendly   supplies the faction would stock
    honored    more supplies and two patterns from its own trades (moved off town shelves: TBC rep
               recipes were only sold for standing)
    revered    6 blues, ilvl 67, worn at 60, 45-75g; two more patterns
    exalted    3 epics, ilvl 73, worn at 60, 250-350g; two recipes that craft ilvl 73 epics

A DIRECTION, NOT A CAGE (Kyle, 15 Nov 2026: "DONT tunnel people. Like if the codex rep only has arcane caster
gear....it's kind of trash for 99% of players... rarely is a single spell type a good idea bro unless it's an
exception, not a rule... Don't pigeon hole!!!"). Every faction's eleven pieces (6 blues, 3 epics, 2 crafted)
cover tanks, healers, casters and fighters across the armour types; the faction's flavour is in what the piece
is and is called, not in who can use it. Spell power is general: only two pieces in the whole set are one
school, as deliberate exceptions (the Ashclaim's fire scepter, Thunder Bluff's storm totem for a shaman).
tools/qa_faction_rewards.py holds both rules.

THE ITEMS SAY WHO SOLD THEM. Orgrimmar's are a grunt's and a farseer's, the Darkspear's a headhunter's and a
hexer's, the Forsaken's an apothecary's and a deathstalker's. Their stats come from the crafted-gear
identities (tools/build_crafted_gear.py IDENTITIES), so a caster's piece leads with spell power, a fighter's
with attack power, a tank's with Stamina, and nothing is a dribble: the same audit runs on them.

The exalted recipes use each trade's top materials for now, doubled, and carry "_rare_ingredients_todo": the
rare ingredients Kyle wants are for later.

Writes data/items/faction_rewards.json (sold as "unique:<id>", world/vendor_stock.make_unique), the exalted
recipes into their trade's recipe file, the rewards into data/factions/factions.json, and three new
quartermasters (Darkspear, Steamwheedle, Booty Bay had none). Idempotent.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

G = 10000                   # copper in a gold
BLUE_ILVL, EPIC_ILVL, WORN_AT = 67, 73, 60

#: faction -> its quartermaster, and the shop its patterns sit on (the same one unless said)
QM = {
    "crimson_codex": "kb_quartermaster",
    "orgrimmar": "orgrimmar_quartermaster",
    "darkspear_tribe": "ds_quartermaster",
    "the_forsaken": "uc_quartermaster",
    "steamwheedle_cartel": "ratchet_cartel_quartermaster",
    "thunder_bluff": "taurajo_quartermaster",
    "booty_bay_authority": "bootybay_port_quartermaster",
    "the_ashclaim": "cw_quartermaster",
    "emerald_reclamation": "es_quartermaster",
}
PATTERN_SHOP = {"emerald_reclamation": "es_timbermaw_trader"}

#: the three factions with nobody to sell for them: (vendor_id, name, zone, x, y, race, gender, variant,
#: facing, greeting, everyday stock)
NEW_QMS = [
    ("ds_quartermaster", "Quartermaster Zen'tabra", "echo_isles", 79, 59, "troll", "female", 6, "down",
     "The tribe remembers who stood with it when it had one island left. So do I. Ask what you can carry.",
     ["healing_potion_greater", "mana_potion_greater", "drink_spring_flask", "meal_river_fish", "kit_field_repair"]),
    ("ratchet_cartel_quartermaster", "Cartel Quartermaster Fizzwhistle", "ratchet", 28, 41, "goblin", "male", 5,
     "left", "Good standing with the Cartel is the only currency I take a discount in. Everything else is "
             "full price.",
     ["healing_potion_greater", "mana_potion_greater", "kit_field_repair", "drink_barley_beer", "meal_trailbread"]),
    ("bootybay_port_quartermaster", "Port Quartermaster Sprocka", "booty_bay", 32, 25, "goblin", "female", 4,
     "down", "The Baron decides which hulls sail. I decide who gets the good kit. Stay on both our lists.",
     ["healing_potion_major", "mana_potion_major", "kit_field_repair", "drink_birch_wine", "meal_kodo_ribs"]),
]

# ---------------------------------------------------------------------------------------------------------
# THE GEAR. (id, name, slot, kind, armour or weapon type, identity, price in gold, flavour)
# kind: "armor" or "weapon". Six revered blues and three exalted epics a faction.
# ---------------------------------------------------------------------------------------------------------
REVERED = {
    "crimson_codex": [
        ("cc_archivists_cowl", "Archivist's Cowl", "head", "armor", "cloth", "caster", 62,
         "A deep red cowl with a reading lens sewn into the brim."),
        ("cc_codex_bound_gloves", "Codex-Bound Gloves", "hands", "armor", "cloth", "precise_caster", 48,
         "Ink-stained to the knuckle. The Codex counts that as a qualification."),
        ("cc_marginalia_of_the_deep", "Marginalia of the Deep", "off_hand", "weapon", "tome", "healer", 58,
         "Notes in the margins of a book nobody has finished. Some of them are answers."),
        ("cc_bastion_warden_girdle", "Bastion Warden's Girdle", "waist", "armor", "plate", "tank", 52,
         "Worn by the blood elves who hold the Bastion's stair against whatever climbs it."),
        ("cc_lamplighter_boots", "Lamplighter's Boots", "feet", "armor", "leather", "rogue_crit", 50,
         "Soft-soled, for the ones who carry the lamps out past where the light reaches."),
        ("cc_signet_of_the_find", "Signet of the Find", "ring", "armor", None, "strength_hit", 55,
         "A find, not a discovery. A find was already there."),
    ],
    "orgrimmar": [
        ("og_grunts_warhelm", "Grunt's Warhelm", "head", "armor", "plate", "strength", 64,
         "Red iron with a nose guard. Every grunt's first helm looks like it, and the good ones keep it."),
        ("og_korkron_shoulderguards", "Kor'kron Shoulderguards", "shoulder", "armor", "plate", "tank", 60,
         "Spiked pauldrons in the Warchief's colours, made for standing in a doorway."),
        ("og_farseers_mail_vest", "Farseer's Mail Vest", "chest", "armor", "mail", "mail_caster", 70,
         "Hung with wolf-tooth charms that rattle before the lightning comes."),
        ("og_wolfrider_leggings", "Wolfrider's Leggings", "legs", "armor", "leather", "agility", 62,
         "Worn smooth on the inside of the knee by years in a wolf's saddle."),
        ("og_spiritwalker_bracers", "Spiritwalker's Bracers", "wrist", "armor", "mail", "tide_healer", 46,
         "Bound with blue cord, the way the old shaman bound them."),
        ("og_band_of_the_red_stone", "Band of the Red Stone", "ring", "armor", None, "battlemage", 55,
         "Cut from the same red rock as the city's walls."),
    ],
    "darkspear_tribe": [
        ("ds_headhunters_mask", "Headhunter's Mask", "head", "armor", "leather", "agility", 60,
         "A carved wooden mask with tusks. The eye holes are smaller than you'd expect."),
        ("ds_hexers_robe", "Hexer's Robe", "chest", "armor", "cloth", "caster", 68,
         "Stitched with little bone charms. The Darkspear's hexers wear it to remind Zalazane who's still here."),
        ("ds_bonecharm_necklace", "Bonecharm Necklace", "neck", "armor", None, "healer", 52,
         "Fish bones and a carved shell on a cord. A witch doctor blessed every one."),
        ("ds_tidewalker_waders", "Tidewalker Waders", "feet", "armor", "mail", "hunter", 54,
         "For wading out to the isles at low tide, where the drowned ones wait."),
        ("ds_shadow_hunters_bracers", "Shadow Hunter's Bracers", "wrist", "armor", "leather", "wildheart", 46,
         "Painted with the marks of a shadow hunter who never gave his name."),
        ("ds_spearguard_girdle", "Spearguard Girdle", "waist", "armor", "plate", "tank", 54,
         "A troll warrior's belt, notched where the spear rests."),
    ],
    "the_forsaken": [
        ("fs_apothecarys_gloves", "Apothecary's Gloves", "hands", "armor", "cloth", "caster", 48,
         "Waxed gloves from the Apothecarium. The stains won't come out, and nobody asks what they are."),
        ("fs_deathstalkers_hood", "Deathstalker's Hood", "head", "armor", "leather", "rogue_crit", 60,
         "Grey and close-fitting. Deathstalkers don't want to be remembered by their faces."),
        ("fs_dark_ranger_spaulders", "Dark Ranger's Spaulders", "shoulder", "armor", "mail", "hunter_precise", 60,
         "Black mail edged in silver, after the Banshee Queen's own rangers."),
        ("fs_deathguard_legplates", "Deathguard Legplates", "legs", "armor", "plate", "tank", 72,
         "The Deathguard hold Brill's road. These hold the Deathguard up."),
        ("fs_grave_cold_band", "Grave-Cold Band", "ring", "armor", None, "strength_crit", 55,
         "Cold to the touch, and it never warms however long you wear it."),
        ("fs_shroud_of_the_wakened", "Shroud of the Wakened", "back", "armor", "cloth", "healer", 50,
         "Cut from a burial shroud by someone who woke up in it."),
    ],
    "steamwheedle_cartel": [
        ("sc_bruisers_gauntlets", "Cartel Bruiser's Gauntlets", "hands", "armor", "plate", "strength", 54,
         "Brass knuckles built into the plate. The Cartel's neutrality is enforced."),
        ("sc_contractors_belt", "Contractor's Belt", "waist", "armor", "leather", "agility", 50,
         "Six pockets, and every one has a receipt in it."),
        ("sc_wharf_inspectors_coat", "Wharf Inspector's Coat", "chest", "armor", "mail", "hunter", 68,
         "Chain under a goblin's long coat. Inspections in Ratchet are occasionally contested."),
        ("sc_neutral_ground_mantle", "Neutral Ground Mantle", "shoulder", "armor", "cloth", "caster", 56,
         "Horde red on one shoulder, Alliance blue on the other. Diplomacy, the goblin way."),
        ("sc_tidepaid_ring", "Tidepaid Ring", "ring", "armor", None, "healer", 55,
         "Paid out by the tide's ledger. The Cartel insures its healers."),
        ("sc_harbourmasters_slippers", "Harbourmaster's Slippers", "feet", "armor", "cloth", "spirit_healer", 48,
         "Soft enough to walk the quay at night without waking the dockhands."),
    ],
    "thunder_bluff": [
        ("tb_spireborn_headdress", "Spireborn Headdress", "head", "armor", "leather", "healer", 62,
         "Feathers from the eagles that nested on the spires. There aren't any more of them."),
        ("tb_plainsrunner_leggings", "Plainsrunner's Leggings", "legs", "armor", "mail", "hunter", 70,
         "For running the Barrens. Nobody runs Mulgore any more."),
        ("tb_taurajo_bulwark_girdle", "Taurajo Bulwark Girdle", "waist", "armor", "plate", "tank", 52,
         "Heavy enough to anchor a tauren against a charging kodo, which is the test."),
        ("tb_windhoof_bracers", "Windhoof Bracers", "wrist", "armor", "leather", "feral", 46,
         "Kodo hide, bound with sinew. A druid's in cat form never notices them."),
        ("tb_earthmothers_mantle", "Earthmother's Mantle", "shoulder", "armor", "mail", "mail_caster", 58,
         "Carved stone beads on the shoulders, one for every spire."),
        ("tb_totem_of_the_lost_spires", "Totem of the Lost Spires", "ranged", "weapon", "totem", "storm", 52,
         "Four little spires carved on a single stick. The shaman who sells it won't talk about the fourth."),
    ],
    "booty_bay_authority": [
        ("bb_harbour_guard_helm", "Harbour Guard's Helm", "head", "armor", "plate", "tank", 64,
         "Dented by cannonballs, polished for the Baron."),
        ("bb_corsair_hunter_vest", "Corsair-Hunter's Vest", "chest", "armor", "leather", "rogue_crit", 68,
         "Light enough to swim in, which matters more on Booty Bay's payroll than it should."),
        ("bb_navigators_belt", "Navigator's Belt", "waist", "armor", "mail", "tide_healer", 50,
         "A sextant pouch on one hip and a lightning charm on the other."),
        ("bb_barons_waistcoat", "Baron's Silk Waistcoat", "chest", "armor", "cloth", "caster", 70,
         "Cut for the Baron's fitting and sold when he grew out of it."),
        ("bb_tide_readers_gloves", "Tide-Reader's Gloves", "hands", "armor", "cloth", "healer", 48,
         "Cold, and they always feel wet, and the tide tables are stitched on the palms."),
        ("bb_cannoneers_ring", "Cannoneer's Ring", "ring", "armor", None, "hunter_crit", 55,
         "A brass ring blackened by powder. It's been close to a lot of loud things."),
    ],
    "the_ashclaim": [
        ("ac_forgeguard_breastplate", "Ashhold Forgeguard Breastplate", "chest", "armor", "plate", "tank", 74,
         "Dark iron, hammered on the deed-holder's own anvil."),
        ("ac_riggers_gloves", "Cinderwharf Rigger's Gloves", "hands", "armor", "leather", "agility", 48,
         "Tarred palms for climbing rigging in the wind off the volcano."),
        ("ac_scoria_pauldrons", "Scoria-Plated Pauldrons", "shoulder", "armor", "mail", "earthen", 60,
         "Plates of cooled volcanic glass on a mail frame. Light, sharp and hot to the touch."),
        ("ac_pyremongers_hood", "Pyremonger's Hood", "head", "armor", "cloth", "caster", 62,
         "A Dark Iron fire-priest's hood, singed around the eye slits."),
        ("ac_deed_holders_signet", "Deed-Holder's Signet", "ring", "armor", None, "strength", 55,
         "A copy of the Ashhold seal. The original is in a vault the goblins insured."),
        ("ac_ashpriests_bindings", "Ashpriest's Bindings", "wrist", "armor", "cloth", "healer", 44,
         "Wraps a Dark Iron healer wears so the forge-burns on her wrists don't show."),
    ],
    "emerald_reclamation": [
        ("er_sentinel_glaivebelt", "Sentinel's Glaivebelt", "waist", "armor", "leather", "agility", 50,
         "A hook at the hip for a glaive, worn by the Sentinels on the Fel Line."),
        ("er_timbermaw_hide_leggings", "Timbermaw Hide Leggings", "legs", "armor", "leather", "bear", 66,
         "Furbolg-tanned and heavy. The Timbermaw make them for the ones who stand in front."),
        ("er_grovewardens_robe", "Grovewarden's Robe", "chest", "armor", "cloth", "high_healer", 70,
         "Green as the cleansed glade, and it smells of moonflowers."),
        ("er_reclaimers_hauberk", "Reclaimer's Hauberk", "chest", "armor", "mail", "hunter_precise", 70,
         "A Sentinel ranger's hauberk, cut down for a transplant who earned it."),
        ("er_treant_bark_wristguards", "Treant-Bark Wristguards", "wrist", "armor", "plate", "tank", 46,
         "Shed bark from an old treant, bound over steel. He said he didn't need it."),
        ("er_moonwell_pendant", "Moonwell Pendant", "neck", "armor", None, "caster", 52,
         "A drop of the Sanctuary's moonwell, sealed in glass. It glows faintly at night."),
    ],
}

EXALTED = {
    "crimson_codex": [
        ("cc_staff_of_the_hanging_light", "Staff of the Hanging Light", "main_hand", "weapon", "staff",
         "caster_crit", 335, "Its head is a sliver of whatever hangs at the centre of the Underdark. Nobody's "
                             "climbed up to check."),
        ("cc_crimson_spellblade", "Crimson Spellblade", "main_hand", "weapon", "sword_1h", "rogue_crit", 295,
         "A Sunstrider spellblade, red to the hilt. It cuts spells as well as it cuts anything else."),
        ("cc_cloak_of_the_long_descent", "Cloak of the Long Descent", "back", "armor", "cloth", "tank",
         255, "Lined with the dark of the fissure. It's still warm from the lamps that went down with it."),
    ],
    "orgrimmar": [
        ("og_warchiefs_due", "Warchief's Due", "main_hand", "weapon", "axe_2h", "strength_crit", 345,
         "Paid to the Warchief by every Horde forge, and handed on to whoever earned it."),
        ("og_bulwark_of_the_valley", "Bulwark of the Valley", "off_hand", "weapon", "shield", "shield_tank", 285,
         "Painted with the Valley of Trials, where every orc first learned to stand."),
        ("og_farseers_ancestral_mace", "Farseer's Ancestral Mace", "main_hand", "weapon", "mace_1h",
         "tide_healer", 290, "Carved with the names of farseers back to Draenor. There's room for a few more."),
    ],
    "darkspear_tribe": [
        ("ds_spear_of_the_last_island", "Spear of the Last Island", "main_hand", "weapon", "polearm", "agility",
         335, "Made from driftwood off the last island the Darkspear held. They mean to take the rest back with it."),
        ("ds_kangaris_hexing_staff", "Kang'ari's Spirit Staff", "main_hand", "weapon", "staff", "high_healer", 325,
         "Hung with the elder's own fetishes. It grumbles when it isn't used."),
        ("ds_senjin_throwing_axes", "Sen'jin's Throwing Axes", "ranged", "weapon", "thrown", "hunter_crit", 260,
         "A matched pair, balanced the old way. They come back to the hand if you know how to ask."),
    ],
    "the_forsaken": [
        ("fs_banshees_lament", "Banshee's Lament", "ranged", "weapon", "bow", "hunter_crit", 300,
         "A dark ranger's longbow. The string sighs when it's drawn."),
        ("fs_blade_of_the_wakened", "Blade of the Wakened", "main_hand", "weapon", "dagger", "rogue_crit", 290,
         "Taken out of a Scourge armoury by the first of the dead to wake. It never went back."),
        ("fs_plaguebearers_staff", "Plaguebearer's Staff", "main_hand", "weapon", "staff", "death", 330,
         "Topped with a sealed vial from the Apothecarium. Don't drop it."),
    ],
    "steamwheedle_cartel": [
        ("sc_profit_margin", "Profit Margin", "main_hand", "weapon", "dagger", "rogue_crit", 285,
         "A goblin's knife, thin and very sharp. It's the margin you don't see that does the damage."),
        ("sc_the_neutrality_clause", "The Neutrality Clause", "off_hand", "weapon", "shield", "shield_tank", 280,
         "A goblin tower shield with the Cartel's terms painted on the front. Breaking them is extra."),
        ("sc_arbiters_cloak", "Cartel Arbiter's Cloak", "back", "armor", "cloth", "caster", 250,
         "Worn by the goblins who settle disputes on the quay. Nobody argues twice."),
    ],
    "thunder_bluff": [
        ("tb_spire_wardens_staff", "Spire-Warden's Staff", "main_hand", "weapon", "staff", "bear", 340,
         "The staff of the druid who held the last spire's stair. A bear fights with it as well as a tauren."),
        ("tb_mulgore_greatbow", "Mulgore Greatbow", "ranged", "weapon", "bow", "hunter_precise", 295,
         "Strung for the plains as they were. The hunters who carry it mean to see them again."),
        ("tb_cloak_of_the_fallen_spires", "Cloak of the Fallen Spires", "back", "armor", "cloth", "high_healer",
         255, "Woven by the Elders' weavers, with four spires in the border and the ground beneath them missing."),
    ],
    "booty_bay_authority": [
        ("bb_revilgaz_cutlass", "Revilgaz's Cutlass", "main_hand", "weapon", "sword_1h", "rogue_crit", 300,
         "The Baron's spare. He has a lot of spares, and he's particular about who gets one."),
        ("bb_port_authority_blunderbuss", "Port Authority Blunderbuss", "ranged", "weapon", "gun",
         "hunter_precise", 290, "Licensed, stamped and loaded with whatever was cheap that week."),
        ("bb_cloak_of_the_deep_harbour", "Cloak of the Deep Harbour", "back", "armor", "cloth", "caster", 250,
         "Sea-blue and heavy with salt. The only deep-water harbour left, on your shoulders."),
    ],
    "the_ashclaim": [
        ("ac_thanes_claim", "Thane's Claim", "main_hand", "weapon", "mace_2h", "strength", 350,
         "A Dark Iron warhammer with the deed to Khaz Varun engraved down the haft."),
        ("ac_firebrand_scepter", "Firebrand Scepter", "main_hand", "weapon", "mace_1h", "fire", 295,
         "Cast from scoria and Dark Iron. It's warm in the hand and hot at the head."),
        ("ac_khaz_varun_deedstone", "Khaz Varun Deedstone", "neck", "armor", None, "tank", 265,
         "A chip of Khaz Varun's gate on a chain. Whoever holds the gate holds the hall."),
    ],
    "emerald_reclamation": [
        ("er_moonboughs_gift", "Moonbough's Gift", "ring", "armor", None, "healer", 255,
         "A ring of living wood, grown around a moonstone by the Arch Druid's own hand."),
        ("er_glaive_of_the_fel_line", "Glaive of the Fel Line", "main_hand", "weapon", "polearm", "agility",
         330, "A Sentinel's war glaive. The Fel Line moves north a little every week, and this is why."),
        ("er_windcallers_bough", "Windcaller's Bough", "off_hand", "weapon", "tome", "caster", 270,
         "A bound book with covers of living wood. Leaves still grow out of the spine in spring."),
    ],
}

# ---------------------------------------------------------------------------------------------------------
# THE CRAFTING. Patterns moved onto the faction's shelf (honored, revered) and the exalted recipes that make
# ilvl 73 epics. (recipe id) for moved ones; for exalted: (id, trade, name, slot, kind, type, identity, flavour)
# ---------------------------------------------------------------------------------------------------------
MOVED = {
    "crimson_codex": {"honored": ["ench_weapon_spellsurge", "ench_gloves_superior_battlemage"],
                      "revered": ["ench_weapon_major_spell_power", "ench_2h_major_spell_power"]},
    "orgrimmar": {"honored": ["bs300_bloodiron_legs", "ench_weapon_superior_strength"],
                  "revered": ["ench_2h_major_valor", "ench_weapon_major_valor"]},
    "darkspear_tribe": {"honored": ["cookx_bloodspice_steak", "ench_bracer_superior_wildheart"],
                        "revered": ["ench_weapon_major_wildheart", "ench_2h_major_wildheart"]},
    "the_forsaken": {"honored": ["lw_undercity_shade_vest", "alch_transmute_iron_gold_vendor"],
                     "revered": ["alch_transmute_arcanite", "ench_cloak_major_warding"]},
    "steamwheedle_cartel": {"honored": ["engx_scope_thorium", "cookx_keg_braised_shank"],
                            "revered": ["alch_flask_black_lotus", "ench_boots_major_vigor"]},
    "thunder_bluff": {"honored": ["lw_rugged_int_vest", "ench_bracer_superior_mana_regeneration"],
                      "revered": ["ench_weapon_major_stormcaller", "ench_boots_major_stormcaller"]},
    "booty_bay_authority": {"honored": ["fishx_mightfish_steak", "fishx_nightfin_soup"],
                            "revered": ["jc_cut_sparkling_azure_diamond", "jc_cut_delicate_black_diamond"]},
    "the_ashclaim": {"honored": ["bs300_truesilver_wrist", "bs300_kit_ashen_steel"],
                     "revered": ["bs_runed_arcanite_rod", "jc_cut_etched_cinder_agate"]},
    "emerald_reclamation": {"honored": ["wwx_starleaf_moon_idol", "ench_weapon_major_healing"],
                            "revered": ["wwx_blessed_sunheart_codex", "wwx_sunheart_tideguard",
                                        "wwx_sunheart_staff", "wwx_blessed_sunheart_staff", "wwx_sunheart_bow"]},
}

EXALTED_RECIPES = {
    "crimson_codex": [
        ("rep_cc_duskwaking_archivist_robe", "tailoring", "Duskwaking Archivist's Robe", "chest", "armor", "cloth",
         "caster_crit", "The robe Codex-Master Duskwaking wears to the lowest shelves. Copies are permitted."),
        ("rep_cc_pendant_of_the_hanging_light", "jewelcrafting", "Pendant of the Hanging Light", "neck", "armor",
         None, "healer", "A shard of crystal that points, always, at the light in the Underdark."),
    ],
    "orgrimmar": [
        ("rep_og_korkron_warplate", "blacksmithing", "Kor'kron Warplate", "chest", "armor", "plate",
         "strength_crit", "Black iron and red leather, the plate the Warchief's guard wears to war."),
        ("rep_og_farseers_chain_hauberk", "leatherworking", "Wolf-Rider's Chain Hauberk", "chest", "armor", "mail",
         "hunter", "Chain cut for a wolf-rider's back, with a strap where the bow rides."),
    ],
    "darkspear_tribe": [
        ("rep_ds_hexweavers_robe", "tailoring", "Hexweaver's Robe", "chest", "armor", "cloth", "precise_caster",
         "Woven on Echo Isles cloth before the tribe left, finished on the mainland after."),
        ("rep_ds_shadow_hunters_vest", "leatherworking", "Shadow Hunter's Vest", "chest", "armor", "leather",
         "wildheart", "Painted with the shadow hunters' marks. Each one is somebody who came back."),
    ],
    "the_forsaken": [
        ("rep_fs_deathwhisper_cowl", "tailoring", "Deathwhisper Cowl", "head", "armor", "cloth", "caster",
         "The hood muffles every voice but the one you're listening for."),
        ("rep_fs_deathstalker_leggings", "leatherworking", "Deathstalker's Leggings", "legs", "armor", "leather",
         "rogue_crit", "Grey leather that makes no sound on stone. The Deathstalkers' first rule."),
    ],
    "steamwheedle_cartel": [
        ("rep_sc_arbitrators_goggles", "engineering", "Cartel Arbitrator's Goggles", "head", "armor", "mail",
         "hunter_crit", "Twelve lenses, a ledger readout and a little brass shutter for the bad news."),
        ("rep_sc_steamwheedle_hand_cannon", "engineering", "Steamwheedle Hand Cannon", "ranged", "weapon", "gun",
         "hunter_precise", "Too big for a goblin, which is exactly why the goblins sell it."),
    ],
    "thunder_bluff": [
        ("rep_tb_bloodhoof_warhide", "leatherworking", "Bloodhoof Warhide Leggings", "legs", "armor", "leather",
         "bear", "Tanned the way the Bloodhoof did it, for druids who meet the charge head on."),
        ("rep_tb_totem_of_the_four_spires", "woodworking", "Totem of the Four Spires", "ranged", "weapon", "totem",
         "tide_healer", "Four spires carved in the round, and in the base a hollow where the fourth fell in."),
    ],
    "booty_bay_authority": [
        ("rep_bb_navigators_silk_mantle", "tailoring", "Navigator's Silk Mantle", "shoulder", "armor", "cloth",
         "caster_crit", "Sea-silk on the shoulders, stitched with the deep-water chart of the bay."),
        ("rep_bb_harbour_guard_greathelm", "blacksmithing", "Harbour Guard's Greathelm", "head", "armor", "plate",
         "tank", "The Port Authority's crest on the brow. Pirates know it on sight, and that's the point."),
    ],
    "the_ashclaim": [
        ("rep_ac_claimants_warplate", "blacksmithing", "Ashhold Claimant's Warplate", "chest", "armor", "plate",
         "strength_crit", "Forged for the thane's champion: whoever wears it walks into Khaz Varun first."),
        ("rep_ac_khaz_varun_siege_rifle", "engineering", "Khaz Varun Siege Rifle", "ranged", "weapon", "gun",
         "hunter_crit", "Built from a Dark Iron siege piece cut down to something a person can carry. Barely."),
    ],
    "emerald_reclamation": [
        ("rep_er_reclaimers_living_staff", "woodworking", "Reclaimer's Living Staff", "main_hand", "weapon",
         "staff", "high_healer", "Still growing. The druids say it'll flower the year Felwood's clean."),
        ("rep_er_timbermaw_ancestor_hide", "leatherworking", "Timbermaw Ancestor Hide", "chest", "armor",
         "leather", "feral", "Cut from a hide the Timbermaw kept for a hundred years, for the one who'd earn it."),
    ],
}

#: each trade's top gear recipe, doubled, until the rare ingredients exist (Kyle: "We can add these later")
TRADE_FILE = {"tailoring": "crafting", "woodworking": "crafting", "engineering": "crafting",
              "blacksmithing": "blacksmithing", "leatherworking": "leatherworking", "jewelcrafting": "jewelcrafting"}
PLACEHOLDER = {
    "tailoring": ({"bolt_voidweave": 16, "thread_silken": 2}, "voidweave"),
    "woodworking": ({"plank_sunheart": 14, "fiber_warded": 4, "stick_ironbound": 2, "resin": 2}, "sunheart"),
    "engineering": ({"bar_elementium": 10, "bar_arcanite": 4, "part_gear_assembly": 4}, "elementium"),
    "blacksmithing": ({"bar_elementium": 12, "flux_strong": 2, "whetstone": 2}, "elementium"),
    "leatherworking": ({"leather_frostscale": 10, "thread_silken": 2}, "frostscale"),
    "jewelcrafting": ({"setting_necklace_thorium": 1, "bar_thorium": 2, "gem_azure_diamond": 4}, "thorium"),
}

#: friendly and honored supplies, the faction's own (added to what the Codex, the Ashclaim and the
#: Reclamation already stock)
SUPPLIES = {
    "orgrimmar": {"friendly": ["meal_ember_glazed_ribs"], "honored": ["elixir_icecap"]},
    "darkspear_tribe": {"friendly": ["drink_starfall_wine"], "honored": ["mana_potion_supreme"]},
    "the_forsaken": {"friendly": ["healing_potion_supreme"], "honored": ["elixir_icecap"]},
    "steamwheedle_cartel": {"friendly": ["shot_thorium"], "honored": ["bomb_dark_iron"]},
    "thunder_bluff": {"friendly": ["meal_ember_glazed_ribs", "drink_starfall_wine"],
                      "honored": ["healing_potion_supreme"]},
    "booty_bay_authority": {"friendly": ["drink_starfall_wine"], "honored": ["high_table_feast"]},
}


def author_unique(rid, name, slot, kind, typ, ident, ilvl, rarity, flavour, price_g):
    import build_crafted_gear as C
    out = {"kind": kind, "slot": slot, "item_level": ilvl, "rarity": rarity, "required_level": WORN_AT,
           "stat_template": C.IDENTITIES[ident][1]}
    if kind == "weapon":
        out["weapon_type"] = typ
        ident = C.weapon_identity(typ, ident)
    else:
        out["armor_type"] = typ
    item = C.author(rid, {"name": name, "output": out}, ident, flavour)
    item["required_level"] = WORN_AT
    item["price"] = price_g * G
    item["sell_price"] = max(item.get("sell_price", 0), price_g * G // 8)
    return item, C.audit_item("reputation", rid, item)


def main():
    import build_crafted_gear as C
    from crafted_icon_palette import Picker
    C.PICKER = Picker()

    # ---- the gear
    items, bad = {}, []
    for fid, rows in REVERED.items():
        for row in rows:
            iid, name, slot, kind, typ, ident, price, flav = row
            items[iid], b = author_unique(iid, name, slot, kind, typ, ident, BLUE_ILVL, "rare", flav, price)
            items[iid]["faction"] = fid
            bad += b
    for fid, rows in EXALTED.items():
        for row in rows:
            iid, name, slot, kind, typ, ident, price, flav = row
            items[iid], b = author_unique(iid, name, slot, kind, typ, ident, EPIC_ILVL, "epic", flav, price)
            items[iid]["faction"] = fid
            bad += b
    if bad:
        raise SystemExit("audit failed:\n  " + "\n  ".join(bad))
    (ROOT / "data/items/faction_rewards.json").write_text(json.dumps(
        {"_doc": "Reputation quartermasters' gear (tools/build_faction_rewards.py). Sold as unique:<id>.",
         "items": items}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- the exalted recipes, into their trades
    docs = {}
    for fid, rows in EXALTED_RECIPES.items():
        for rid, trade, name, slot, kind, typ, ident, flav in rows:
            path = ROOT / "data" / TRADE_FILE[trade] / "recipes.json"
            d = docs.setdefault(path, json.loads(path.read_text(encoding="utf-8")))
            book = d["professions"][trade]["recipes"] if "professions" in d else d["recipes"]
            inputs, tier = PLACEHOLDER[trade]
            out = {"kind": kind, "slot": slot, "stat_template": C.IDENTITIES[ident][1], "item_level": EPIC_ILVL,
                   "rarity": "epic", "material_tier": tier, "identity": ident, "flavor": flav,
                   "fixed_item_level": True, "required_level": WORN_AT}
            if kind == "weapon":
                out["weapon_type"] = typ
            else:
                out["armor_type"] = typ
            if trade == "jewelcrafting":
                out["armor_type"] = None
            book[rid] = {"name": name, "inputs": dict(inputs), "skill_required": 300,
                         "output": out, "skill_range": [300, 305, 310, 315], "source": "vendor",
                         "faction": fid, "_rare_ingredients_todo": True}
    for path, d in docs.items():
        path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- the three new quartermasters
    from tools.npc_data_guard import safe_update
    vp = ROOT / "data/npcs/vendors.json"
    vd = json.loads(vp.read_text(encoding="utf-8"))
    by_v = {v["vendor_id"]: v for v in vd["vendors"]}
    for vid, name, zone, x, y, race, gender, var, facing, greet, sells in NEW_QMS:
        rec = dict(vendor_id=vid, name=name, zone=zone, x=x, y=y, tile_sprite="npc", sells=sells,
                   buys_from_player=True, faction="neutral", gear_level=WORN_AT, sells_gear=False, race=race,
                   appearance_variant=var, gender=gender, greeting=greet, facing=facing)
        if vid in by_v:
            safe_update(by_v[vid], rec)
        else:
            vd["vendors"].append(rec)
    # a pattern sold for standing comes off every town shelf (TBC: only the faction sold it)
    moved = {rid for f in MOVED.values() for tier in f.values() for rid in tier}
    for v in vd["vendors"]:
        if v.get("sells"):
            v["sells"] = [s for s in v["sells"] if s not in moved]
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ---- the rewards
    fp = ROOT / "data/factions/factions.json"
    fd = json.loads(fp.read_text(encoding="utf-8"))
    for fid, qm in QM.items():
        rw = fd["factions"][fid].setdefault("rewards", {})
        vs = rw.setdefault("vendor_stock", {})
        shelf = vs.setdefault(qm, {})
        pshop = PATTERN_SHOP.get(fid, qm)
        pshelf = vs.setdefault(pshop, {})
        mine = {f"unique:{i}" for i in items} | moved | {r[0] for rows in EXALTED_RECIPES.values() for r in rows}
        for s in (shelf, pshelf):           # clear what this script wrote last time, keep the rest
            for tier in list(s):
                s[tier] = [x for x in s[tier] if x not in mine]
        for tier, ids in SUPPLIES.get(fid, {}).items():
            shelf.setdefault(tier, [])
            shelf[tier] += [i for i in ids if i not in shelf[tier]]
        shelf.setdefault("revered", []).extend(f"unique:{r[0]}" for r in REVERED[fid])
        shelf.setdefault("exalted", []).extend(f"unique:{r[0]}" for r in EXALTED[fid])
        for tier, ids in MOVED[fid].items():
            pshelf.setdefault(tier, []).extend(ids)
        pshelf.setdefault("exalted", []).extend(r[0] for r in EXALTED_RECIPES[fid])
        for s in (shelf, pshelf):
            for tier in list(s):
                if not s[tier]:
                    del s[tier]
        rw["_comment"] = [
            "Gates, not a displayed ladder (the faction panel stays information only).",
            "TBC-style shelves (tools/build_faction_rewards.py, Kyle 15 Nov 2026): friendly supplies, honored "
            "patterns, revered six ilvl 67 blues, exalted three ilvl 73 epics (250-350g) and two epic recipes."]
    fp.write_text(json.dumps(fd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # ANY pattern a faction sells for standing comes off the town shelves, including ones authored before this
    # (the Ashclaim's invulnerability potion was on both)
    from world.recipe_manager import _load_all_recipes as _all
    known = _all()
    gated = {i for f in fd["factions"].values() for tiers in ((f.get("rewards") or {}).get("vendor_stock") or {})
             .values() for ids in tiers.values() for i in ids if i in known}
    vd = json.loads(vp.read_text(encoding="utf-8"))
    for v in vd["vendors"]:
        if v.get("sells"):
            v["sells"] = [s for s in v["sells"] if s not in gated]
    vp.write_text(json.dumps(vd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # the moved patterns are sold, so they're vendor recipes now
    from world.recipe_manager import _load_all_recipes
    srcs = _load_all_recipes()
    changed = {}
    for rid in moved:
        prof, r = srcs[rid]
        if r.get("source") != "vendor":
            changed[rid] = prof
    for path in [ROOT / "data" / f / "recipes.json" for f in ("crafting", "blacksmithing", "leatherworking",
                                                               "jewelcrafting")] + \
            sorted((ROOT / "data").glob("*/recipes.json")):
        if not path.exists() or not changed:
            continue
        d = json.loads(path.read_text(encoding="utf-8"))
        books = d["professions"].values() if "professions" in d else [d]
        hit = False
        for b in books:
            for rid in changed:
                if rid in b.get("recipes", {}):
                    b["recipes"][rid]["source"] = "vendor"
                    hit = True
        if hit:
            path.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    n_rec = sum(len(v) for v in EXALTED_RECIPES.values())
    print(f"{len(items)} items ({sum(len(v) for v in REVERED.values())} blues, "
          f"{sum(len(v) for v in EXALTED.values())} epics), {n_rec} exalted recipes, {len(moved)} patterns moved, "
          f"{len(NEW_QMS)} new quartermasters; {len(changed)} patterns became vendor recipes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
