"""
The people of the Crystalline Underdark: Kael's Bastion (17) and the open zone (12).

Data only - tools/sync_underdark_npcs.py writes these into data/npcs/*.json and takes every coordinate from
the zone modules' NPC_POSITIONS, so the layout stays the only place a position is decided.

EVERYONE HERE IS A NEWCOMER, AND THAT IS THE ROSTER'S WHOLE JOB.

In every other zone the NPCs have always been here and the player is the transplant. Not here. The Crimson
Codex came down a fissure three years ago - the same three years the player has existed on this world - and
the cavern itself is three years old. Nobody has a prior claim on anything, the Codex know it, and it has
made them strange: they catalogue compulsively, because a thing properly written down is a thing owned.

So the usual distrust runs sideways. A Codex archivist does not look down on an Earth transplant for being
new. She looks at them and sees a rival claimant who arrived on the same day she did, and the politeness
gets a degree colder. That is in a handful of these greetings and a handful of the quests, never as the
default tone (see claude/quest_writing_guide.md).

VOICE: precise, dry, faintly superior, and much more rattled than any of them will admit. They are three
years into a project that has stopped obeying its own index and not one of them has written that down.

(record shapes: VENDORS -> name, race, gender, variant, stock, sells_gear, greeting
                AMBIENT -> name, race, gender, variant, greeting)
"""

# =====================================================================================================
# KAEL'S BASTION - the holdfast. One spine, four numbered galleries, and an argument in every one.
# =====================================================================================================
BASTION_VENDORS = {
    "kb_quartermaster": (
        "Quartermaster Sylvaine", "blood_elf", "female", 4,
        ["healing_potion_greater", "mana_potion_greater", "bread_and_cheese", "roasted_meat",
         "guardian_elixir_standard", "whetstone", "vial_empty"], True,
        "Everything here was carried down a fissure on somebody's back. Price it accordingly."),
    "kb_trader": (
        "Factor Anselm Dawnmere", "blood_elf", "male", 9,
        ["healing_potion_standard", "mana_potion_standard", "parchment", "thread_fine",
         "flux_standard", "lamp_oil"], False,
        "I trade in two directions and only one of them goes up the fissure. Guess which has the margin."),
    "kb_smith": (
        "Smith Harvald Emberlock", "blood_elf", "male", 17,
        ["whetstone", "flux_standard", "thread_coarse", "vial_empty"], True,
        "No coal down here worth the name. I burn what the Codex rules is expendable, and they rule often."),
    "kb_reagent_seller": (
        "Reagent-Keeper Ilthea", "blood_elf", "female", 6,
        ["mana_potion_greater", "vial_empty", "parchment", "thread_fine"], False,
        "Catalogued, labelled, shelved. If you want it unlabelled, go and pull it out of the ground yourself."),
    "kb_innkeeper": (
        "Innkeeper Maeven Sorrowglass", "blood_elf", "female", 12,
        ["bread_and_cheese", "roasted_meat", "healing_potion_standard", "mana_potion_standard"], False,
        "There is no night here. We decided there was one anyway, and I keep the hours. Somebody has to."),
    "kb_alchemist": (
        "Alchemist Terrowen", "blood_elf", "male", 20,
        ["healing_potion_greater", "mana_potion_greater", "guardian_elixir_standard", "vial_empty"], False,
        "Four years of samples and the reagents keep testing BETTER than their surface equivalents. I have "
        "stopped putting that in reports."),
}

BASTION_AMBIENT = {
    "kb_gate_warden": (
        "Gate-Warden Vessaria", "blood_elf", "female", 2,
        "Name, business, and whether you intend to take anything out. The third one is the question that "
        "matters."),
    "kb_porter": (
        "Porter Dunhal", "forsaken", "male", 14,
        "Blood elves everywhere and one of me. They needed somebody who does not mind the dark and does not "
        "need to breathe."),
    "kb_stablemaster": (
        "Stable-Hand Corwin", "blood_elf", "male", 8,
        "Nothing stabled here was born here. They do not like the ceiling. Neither do I, and I have had "
        "three years."),
    "kb_cartographer": (
        "Cartographer Elandrin", "blood_elf", "male", 11,
        "Fourth full survey. The first three disagree with each other and with this one, and the cavern is "
        "not moving. I have checked."),
    "kb_naturalist": (
        "Naturalist Orienne", "blood_elf", "female", 5,
        "Everyone calls the fungus scenery. The fungus is the largest single organism any of us has ever "
        "stood on, and nobody will fund me."),
    "kb_enchanter": (
        "Enchanter Vaelios", "blood_elf", "male", 19,
        "The ambient arcane here does half my work and I do not know what it wants in return. Probably "
        "nothing. Probably."),
    "kb_magister": (
        "Magister Saeltheris", "blood_elf", "male", 3,
        "We are not colonists. We are cataloguers. The distinction is important to me and to nobody else."),
    "kb_archivist": (
        "Archivist Nessaly", "blood_elf", "female", 16,
        "You arrived the same year we did, which the Codex finds easier to ignore than to address. I do "
        "not ignore things."),
    "kb_codex_master": (
        "Codex-Master Ilarien Duskwaking", "blood_elf", "female", 10,
        "Three years, eleven thousand entries, and one cavern that keeps producing things I have no column "
        "for. Welcome to the Crimson Codex."),
    "kb_hall_adjutant": (
        "Adjutant Pell", "blood_elf", "male", 21,
        "The Codex-Master will see you. She sees everyone. It is the filing afterwards that takes the time."),
    "kb_hall_sentinel": (
        "Hall-Sentinel Durannis", "orc", "male", 7,
        "They hired me because I do not care what the crystal says. Three years on, I still do not."),
}

# =====================================================================================================
# THE CRYSTALLINE UNDERDARK - the open zone. Codex field posts, strung out across a roofed country.
# =====================================================================================================
UNDERDARK_VENDORS = {
    "ud_geode_campkeeper": (
        "Campkeeper Threnn", "blood_elf", "female", 13,
        ["healing_potion_standard", "mana_potion_standard", "bread_and_cheese", "lamp_oil",
         "whetstone", "vial_empty"], False,
        "Last supplies before the Geode. I am required to tell you that and required not to tell you why."),
}

UNDERDARK_AMBIENT = {
    "ud_dawn_watch": (
        "Watcher Kaelen Mornstride", "blood_elf", "male", 1,
        "Everyone stops here. Three years and I have not met one person who walked out of that passage "
        "without stopping."),
    "ud_dawn_cartographer": (
        "Surveyor Aelwyn", "blood_elf", "female", 18,
        "I map the far wall from here because there is no closer place to stand. That should tell you "
        "something about the scale."),
    "ud_shard_harvester": (
        "Harvester Delvin Brightsunder", "blood_elf", "male", 15,
        "Shardfields work. Hard on the hands, hard on the eyes, and the Codex counts every crate."),
    "ud_lattice_surveyor": (
        "Surveyor Pelorien", "blood_elf", "male", 22,
        "It grows in exact repeating figures. Geology does not do that. I have been told to write "
        "'unusual mineralisation' and I have written it."),
    "ud_marsh_naturalist": (
        "Naturalist Imrelle", "blood_elf", "female", 4,
        "The water is lit from underneath and the light keeps time with the Lumen. Ask me what that means "
        "and I will tell you honestly that I do not know."),
    "ud_colonnade_scholar": (
        "Scholar Veridan", "blood_elf", "male", 6,
        "Dalaran masonry. Two hundred spans underground, in a cavern that is three years old. Nobody "
        "carried it down."),
    "ud_archive_overseer": (
        "Overseer Thaleon Greyquill", "blood_elf", "male", 20,
        "The Archive is the reason we are all still here, and the reason half of us want to leave."),
    "ud_archive_digger": (
        "Digger Sarenne", "blood_elf", "female", 9,
        "I shift rock and they file what comes out. Last week what came out had a Codex catalogue number "
        "on it that we have not issued yet."),
    "ud_dim_scout": (
        "Scout Rhennik", "blood_elf", "male", 12,
        "The Lumen does not reach past that ridge. Everything I know about what does live out there, I "
        "learned at a run."),
    "ud_bloom_warden": (
        "Bloom-Warden Ysolde Emberquill", "blood_elf", "female", 7,
        "There is something growing down there in the shape of a library. The Codex wants it read. I want "
        "it burned. We have been arguing for eleven months."),
    "ud_sporefall_forager": (
        "Forager Mikael", "forsaken", "male", 11,
        "The caps are safe, the stalks are not, and the ones that look like faces are fine. I have eaten "
        "all three so you do not have to."),
}
