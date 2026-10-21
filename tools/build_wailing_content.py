#!/usr/bin/env python3
"""Wailing Caverns content pass (2026-10-21).  Idempotent.

  PYTHONPATH=. python3 tools/build_wailing_content.py && python3 tools/generate_creatures.py

What was broken: Kresh pointed at an `ability_kit` ("kresh") that did not exist, six trash creatures used the dead
`"kit"` key (undefined kits -> no abilities), four Fanglords shared one reskinned `fanglord_druid` kit, Skum was L24 x1.0
(ladder says 21), Verdan/Skum/Mutanus had 3 abilities (20+ bosses get 4), no WC loot, no WC quests.

Ladder (Kyle's confirmed table): trash 16-22 | Lady Anacondra 19 | Lord Cobrahn 20 | Kresh 20 | Lord Pythas 21 | Skum 21 |
Lord Serpentis 21 | Verdan the Everliving 22 | Mutanus the Devourer 24.  Named rares: Old Hissfang 19, Drowsyroot the
Dreamer 21, Sporeback the Bloated 22 (side nooks).  Trash is HAND-PLACED (tools/handbuilt_wailing.TRASH).
LOOT: ONE item per kill from a pool of 3-4, item_level = creature level + 3, real formulas.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tools.build_durotar_content import make, C  # noqa: E402

NEW_CREATURES = {
    "Fang Initiate": C("humanoid_caster", 17, 20, "fang_initiate"),
    "Nightmare Wisp": C("elemental_caster", 19, 22, "nightmare_wisp"),
    "Deviate Broodling": C("vermin_swarm", 16, 19, "deviate_broodling"),
    "Old Hissfang": C("vermin_sneaky", 19, 19, "old_hissfang", True, 1.7),
    "Drowsyroot the Dreamer": C("humanoid_caster", 21, 21, "drowsyroot_the_dreamer", True, 1.7),
    "Sporeback the Bloated": C("beast_large", 22, 22, "sporeback_the_bloated", True, 1.2),
}
# existing creatures: dead "kit" key -> real "ability_kit"; bosses to exact ladder levels, unique kits, HP climbing
FIXES = {
    "Deviate Python": {"ability_kit": "deviate_python"},
    "Deviate Ooze": {"ability_kit": "deviate_ooze"},
    "Deviate Raptor": {"ability_kit": "deviate_raptor"},
    "Deviate Crocolisk": {"ability_kit": "deviate_crocolisk"},
    "Druid of the Fang": {"ability_kit": "druid_fang", "level_range": [17, 20]},
    "Dreadfang": {"ability_kit": "dreadfang"},
    "Nightmare Ectoplasm": {"ability_kit": "nightmare_wisp"},
    "Lady Anacondra": {"level_range": [19, 19], "ability_kit": "lady_anacondra", "boss_multiplier": 1.8},
    "Lord Cobrahn": {"level_range": [20, 20], "ability_kit": "lord_cobrahn", "boss_multiplier": 1.9},
    "Kresh": {"level_range": [20, 20], "ability_kit": "kresh", "boss_multiplier": 1.3},
    "Lord Pythas": {"level_range": [21, 21], "ability_kit": "lord_pythas", "boss_multiplier": 2.2},
    "Skum": {"level_range": [21, 21], "boss_multiplier": 1.35},
    "Lord Serpentis": {"level_range": [21, 21], "ability_kit": "lord_serpentis", "boss_multiplier": 2.4},
    "Verdan the Everliving": {"level_range": [22, 22], "boss_multiplier": 1.7},
    "Mutanus the Devourer": {"level_range": [24, 24], "boss_multiplier": 2.4},
}
CAVE = {
    "creatures": {
        "Deviate Python": 4, "Deviate Ooze": 3, "Deviate Raptor": 5, "Deviate Crocolisk": 3, "Deviate Adder": 4,
        "Deviate Lasher": 3, "Deviate Ravager": 3, "Deviate Viper": 3, "Deviate Shambler": 3,
        "Deviate Faerie Dragon": 2, "Druid of the Fang": 5, "Dreadfang": 3, "Fang Initiate": 4,
        "Nightmare Wisp": 3, "Deviate Broodling": 3,
        # bosses/rares ride in the same table at weight 0 (engine convention; placed only by zone.boss_positions pins)
        "Lady Anacondra": 0, "Lord Cobrahn": 0, "Kresh": 0, "Lord Pythas": 0, "Skum": 0, "Lord Serpentis": 0,
        "Verdan the Everliving": 0, "Mutanus the Devourer": 0,
        "Old Hissfang": 0, "Drowsyroot the Dreamer": 0, "Sporeback the Bloated": 0},
}


def qd(item_id, name, desc, chance):
    return {"item_id": item_id, "name": name, "category": "quest", "description": desc, "chance": chance}


QUEST_DROPS = {
    "Fang Initiate": [qd("fang_totem_shard", "Fang Totem Shard",
                         "A shard of green-glazed clay, scratched with a coiled serpent. Initiates break one at the end of each rite.", 0.5)],
    "Nightmare Wisp": [qd("nightmare_dewdrop", "Nightmare Dewdrop",
                          "A bead of dew that does not evaporate. It sees things; you would rather it did not tell you.", 0.5)],
    "Mutanus the Devourer": [qd("naralex_dream_pearl", "Naralex's Dream-Pearl",
                                "A pearl of green light, warm as a heartbeat. Naralex dreamed it, once, before the nightmare did the dreaming.", 1.0)],
}


def pools():
    P = {}
    # ---------------- bosses ----------------------------------------------------------------------------------
    P["Lady Anacondra"] = [        # L19 -> 22: leather bracers / healer staff / cloth head / ring
        make("Viperskin Bracers", "wrist", "of the Restorer", 22,
             "Bracers cut from a viper that made the mistake of being underfoot. They cool the pulse and sweeten the temper.",
             armor_type="leather"),
        make("Anacondra's Slumber-Staff", "main_hand", "of the Prophet", 22,
             "A staff of green wood and cold scales. Whoever holds it gets very calm, very quickly.", weapon_type="staff"),
        make("Serpentbloom Circlet", "head", "of the Sorcerer", 22,
             "A circlet of pale flowers that bloom only in the dark of the caverns. They smell of wet stone and sleep.",
             armor_type="cloth"),
        make("Lady's Coiled Signet", "ring", "of the Eagle", 22,
             "A thin gold ring coiled twice around the finger. It tightens when you lie, and Lady Anacondra never lied.")]
    P["Lord Cobrahn"] = [          # L20 -> 23: 1H axe / mail chest / cloak / leather belt
        make("Cobrahn's Fanged Cleaver", "main_hand", "of the Gladiator", 23,
             "A hand-axe with a fang set into the head. It bites, then it lets go. That is how snakes do it.", weapon_type="axe_1h"),
        make("Emerald Scale Chestguard", "chest", "of the Soldier", 23,
             "Green scale-mail that shifts colour when you are not paying attention. It is always listening.", armor_type="mail"),
        make("Drake-Hide Cloak", "back", "of the Falcon", 23,
             "A long cloak cut from a drake's shed skin. It takes the wind well and the daylight poorly.", armor_type="cloth"),
        make("Venomtouched Waistband", "waist", "of the Assassin", 23,
             "Leather stained a permanent, unhealthy green. A careful wearer never licks a finger.", armor_type="leather")]
    P["Kresh"] = [                 # L20 -> 23: plate shoulders / shield / mail boots / ring
        make("Kresh's Shellplate Spaulders", "shoulder", "of the Defender", 23,
             "Pauldrons carved from an old turtle's shell, hammered flat. They take hits and give nothing back, which is the point.",
             armor_type="plate"),
        make("Barnacled Bulwark", "off_hand", "of Blocking", 23,
             "A shield grown over with barnacles. They are, oddly, still alive, and still clinging.", weapon_type="shield"),
        make("Silt-Soaked Greaves", "feet", "of the Whale", 23,
             "Mail boots caked in river-silt. They keep a swimmer's footing and a waterlogged mood.", armor_type="mail"),
        make("Tidebound Band", "ring", "of the Bear", 23,
             "A ring of dull green shell. When you wear it you hear, very faintly, something stir.")]
    P["Lord Pythas"] = [           # L21 -> 24: caster staff / cloth shoulders / dagger / leather boots
        make("Pythas's Thunderstaff", "main_hand", "of the Archmage", 24,
             "A staff that crackles. Pythas called down thunder to defend his sleeping chamber; the staff remembers.",
             weapon_type="staff"),
        make("Slumberer's Mantle", "shoulder", "of the Prophet", 24,
             "A soft mantle that drags every thought toward a nap. Practiced wearers learn to sleep upright and cast anyway.",
             armor_type="cloth"),
        make("Fang-Lord's Pale Dagger", "main_hand", "of the Assassin", 24,
             "A dagger of bleached bone. It is quiet even when it is not quiet.", weapon_type="dagger"),
        make("Basin Walker's Boots", "feet", "of the Wolf", 24,
             "Leather boots laced with river-reed. They dry fast, and they walk soft.", armor_type="leather")]
    P["Skum"] = [                  # L21 -> 24: leather chest / 2H mace / neck / mail gloves
        make("Thunderhide Vest", "chest", "of the Bear", 24,
             "A vest of thick lizard hide. Static lifts the hairs on your arms whenever you put it on.", armor_type="leather"),
        make("Skum's Tail-Club", "main_hand", "of the Juggernaut", 24,
             "A great mace made from the tail-bone of something very large. It was not asked, and it did not volunteer.",
             weapon_type="mace_2h"),
        make("Thunder-Tooth Pendant", "neck", "of the Eagle", 24,
             "A tooth the length of a thumb, hung on a cord. It hums a note just below hearing."),
        make("Static-Charged Gauntlets", "hands", "of the Champion", 24,
             "Mail gauntlets that hum. If you clap in them, the cave notices.", armor_type="mail")]
    P["Lord Serpentis"] = [        # L21 -> 24: wand / cloth legs / 1H sword / leather helm
        make("Serpentis's Venom-Wand", "ranged", "of Nature's Wrath", 24,
             "A wand of petrified serpent spine. The tip beads with something you would rather not touch.", weapon_type="wand"),
        make("Fang-Weave Leggings", "legs", "of the Sorcerer", 24,
             "Cloth woven with fine green thread and shaped like scales. They shift when you walk, softly, like an exhale.",
             armor_type="cloth"),
        make("Wrathbringer's Falchion", "main_hand", "of the Champion", 24,
             "A curved sword with a hooked tip. Serpentis drew it when his rites were interrupted, and was seldom interrupted twice.",
             weapon_type="sword_1h"),
        make("Crest of the Fang", "head", "of the Beast", 24,
             "A leather cap crowned with a ridge of fang. It marks the wearer as a student of the Fang, which has implications.",
             armor_type="leather")]
    P["Verdan the Everliving"] = [  # L22 -> 25: plate chest / polearm / plate wrist / cloth belt
        make("Verdan's Rootbark Cuirass", "chest", "of the Bastion", 25,
             "Plate grown through with living root. It heals a little when sunlit, which in this cave means never.",
             armor_type="plate"),
        make("Everliving Greatstaff", "main_hand", "of the Juggernaut", 25,
             "A polearm of ironwood that still puts out leaves. They are, regrettably, very sharp.", weapon_type="polearm"),
        make("Bark-Wrapped Vambraces", "wrist", "of the Defender", 25,
             "Plate vambraces wrapped in bark. When struck, they sigh a little.", armor_type="plate"),
        make("Living Vine Cord", "waist", "of the Physician", 25,
             "A length of vine that tightens and slackens on its own. It will mend you, if you ask nicely.", armor_type="cloth")]
    P["Mutanus the Devourer"] = [   # L24 -> 27: plate head / caster staff / cloak / crossbow
        make("Mutanus's Devouring Helm", "head", "of the Gladiator", 27,
             "A helm with a jaw. The jaw does not close, but it does not entirely stay still.", armor_type="plate"),
        make("Nightmare-Touched Staff", "main_hand", "of the Prophet", 27,
             "A staff of dark wood and green light. It hums to itself, in a voice that sounds like someone sleeping.",
             weapon_type="staff"),
        make("Naralex's Dreamshroud", "back", "of the Archmage", 27,
             "A cloak the colour of a bad dream, light as a prayer. It remembers a druid who was kind.", armor_type="cloth"),
        make("Devourer's Nightbolt Crossbow", "ranged", "of the Marksman", 27,
             "A crossbow built around a jawbone. The bolts are carved from something that was once asleep.",
             weapon_type="crossbow")]
    # ---------------- named rares -----------------------------------------------------------------------------
    P["Old Hissfang"] = [           # L19 -> 22: dagger / leather gloves / ring
        make("Hissfang's Coil-Knife", "main_hand", "of the Tiger", 22,
             "A knife made from a single shed fang. It is exactly as sharp as a snake's apology.", weapon_type="dagger"),
        make("Shedskin Gloves", "hands", "of the Falcon", 22,
             "Gloves that feel wrong and fit right. They were, once, someone else's skin.", armor_type="leather"),
        make("Old Serpent's Eye-Ring", "ring", "of the Monkey", 22,
             "A ring set with a yellow slit-eye. It watches whatever you do not.")]
    P["Drowsyroot the Dreamer"] = [  # L21 -> 24: cloth shoulders / healer mace / neck
        make("Drowsyroot Mantle", "shoulder", "of the Restorer", 24,
             "A mantle of woven root. Wearing it, you hear the whole cave breathe slowly in and out.", armor_type="cloth"),
        make("Dreamer's Rootmace", "main_hand", "of the Prophet", 24,
             "A rod of living root, pulsing in time with a slumbering heart.", weapon_type="mace_1h"),
        make("Lullaby Pendant", "neck", "of the Whale", 24,
             "A pendant of spun glass. It plays a very quiet tune, and it never repeats a note.")]
    P["Sporeback the Bloated"] = [   # L22 -> 25: leather helm / fist weapon / ring
        make("Sporeback's Mushroom Cap", "head", "of the Bear", 25,
             "A helm grown from the cap of a very large fungus. It is damp and pleasantly absurd.", armor_type="leather"),
        make("Puffball Knuckles", "main_hand", "of the Tiger", 25,
             "Fist-bars of dried spore-sacs. They burst politely on impact.", weapon_type="fist_weapon"),
        make("Spore-Dusted Ring", "ring", "of the Soldier", 25,
             "A ring dusted with something that smells faintly of rain.")]
    return P


def main():
    cp = ROOT / "data/creatures/creatures.json"
    data = json.loads(cp.read_text())
    cr = data["creatures"]
    cr.update(NEW_CREATURES)
    for n, patch in FIXES.items():
        cr[n].update(patch)
        cr[n].pop("kit", None)          # the dead key - replaced by ability_kit
    cp.write_text(json.dumps(data, indent=2) + "\n")

    ep = ROOT / "data/creatures/encounters.json"
    data = json.loads(ep.read_text())
    data["zones"]["Central Barrens"].setdefault("caves", {})["Wailing Caverns"] = CAVE
    ep.write_text(json.dumps(data, indent=2) + "\n")

    qp = ROOT / "data/creatures/quest_drops.json"
    data = json.loads(qp.read_text())
    D = data["drops"]
    for creature, drops in QUEST_DROPS.items():
        D.setdefault(creature, [])
        keep = [d for d in D[creature] if d["item_id"] not in {x["item_id"] for x in drops}]
        D[creature] = keep + drops
    qp.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    out = {"_notes": "Wailing Caverns boss + named-rare loot (2026-10-21). ONE item drops per kill from the pool. "
                     "item_level = creature level + 3; real loot formulas (tools/build_durotar_content.make)."}
    out.update(pools())
    (ROOT / "data/loot/wailing_caverns_boss_loot.json").write_text(json.dumps(out, indent=2) + "\n")
    n = sum(len(v) for k, v in out.items() if not k.startswith("_"))
    print(f"creatures +{len(NEW_CREATURES)}, pools {len(out)-1}, items {n}")


if __name__ == "__main__":
    main()
