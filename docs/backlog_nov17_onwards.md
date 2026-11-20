# Backlog: 17 Nov 2026 onwards (open items only)

Kyle, 17 Nov 2026: "make a new backlog file that only has open stuff... anything that is not done so it's easier to
see what still is on there and what still needs to be completed."

How this file works:
- **Only open work lives here.** When something's finished it comes off this list, and the record of how it was
  done goes in that area's build log or design doc, not here.
- **It was built from every older backlog**: playtest_backlog_2026_10_31, 11_02, 11_10 and 11_14,
  crafting_revamp_backlog, crafting_raid_upgrades_BACKLOG and plaguelands_quests_towns_BACKLOG. Before anything was
  listed, the doubtful items were checked against the code on 17 Nov, so things finished later but never ticked
  (quest voice, heal formula, stun diminishing, vendor levels, the Plaguelands dungeons) aren't here. Those older
  files are history now.
- **Secrets are counts and names only, never where**, the same rule as everywhere else.
- **Check it's still open before fixing it** (Kyle, 18 Nov: "Update fixed things so they don't get fixed 50 times").
  Re-measure an item before starting on it, and the moment it's fixed or found already fixed, it comes off here in
  the same commit and goes on `docs/backlog_fixed.md` with what fixed it and the check that now guards it. Look
  there first: if it's listed, it's done.

---

## 1. Azshara (in progress, in Kyle's order: "One thing at a time")

Brief: `docs/azshara_brief.md`. Done so far: Kyle's six art sheets, West Azshara, Talrendis Landing, Timbermaw Hold,
Central Azshara, East Azshara (the Drowned Court already risen), both caves, the Rotroot Deeps (the dungeon under the
Hold, 18 Nov), the Drowned Palace (two floors off the Drowned Court, 18 Nov), Orgrimmar's north gate and the Ashenvale
East road.

1. **What's left** (the Conclave, the open world and 81 quests are in, 18 Nov):
   - The hidden content ("Surprise me"). Never described.
   - Maybe a handful more quests out of the zone (the plan's Silvermoon and Undercity chains) to reach about 90.
2. **Later, Kyle's call**: the Sunreach Conclave's island home.

**Recruits, sheet 5** (18 Nov): 16 written, kitted and sliced (`docs/recruit_art_prompts_sheet5.md`). Eight are
in the game, and Deadwind's four and Moonglade's two have been placed since (18 Nov). Winterspring's two are still
waiting: re-run `tools/build_sheet5_recruits.py --write` once Winterspring exists, and it places them.

## 1a. The Collection (account-wide unlocks on the AH, 18 Nov 2026)
- Built: `docs/collection_design.md`, 741 collectables, the Collection screen (U), the AH's Collection category.
- **Art:** the Collection's own sheets are all in (C, D, and the 18 Nov drop). Still to paste: see section 10.
- **Next wave:** callboards and daily quests (needs its own design). More of everything as Kyle thinks of it.
- **Pack Mule** is +12 backpack spaces, not a fifth bag slot; Kyle to say if he wants the real slot.

## 1c. Mulgore: The Fallen Bluff, the Thunder Bluff raid (boss art done, 18 Nov 2026)
- `docs/mulgore_raid_boss_prompt.md`: Kyle's first raid. Bosses by rise (Central 5 with the final boss unlocking
  last, Hunter 3, Spirit 3, Elder 3). Every boss is drawn (sheets A, B, C v2 and Cairne's phase 4 in
  `tools/building_sheets/mulgore_raid_*.png`), sliced 19 Nov to `assets/creatures/_src/mulgore/` (18 sprites, `fb_`).
  Still to do: build the raid.

## 1d. Moonglade (built 18 Nov 2026, `docs/moonglade_build_log.md`)
- The three dungeons, doors already on the map: the Barrow Dens (corrupted druids), the Dreaming Arch (the Emerald
  Dream), under the lake (the island's stair). What's waking gets decided with the first of them.
- The Cenarion Circle and the Wakened only reach Friendly on quests; the dungeons are the road past it.

## 1e. Filling 44 to 51: Feralas and the World Tree (Kyle, 19 Nov 2026)
- **Feralas: built without art (Kyle, 19-20 Nov 2026), `docs/feralas_build_log.md`.** Three maps, Camp Mojache,
  Feathermoon Stronghold, the Zukk'ash Hive and its tunnel to the Dry Deep, 83 quests, the Feathermoon Sentinels.
  Open: Kyle's nine art sheets (`docs/feralas_art_prompts.md`), then the swap-over in the build log's last section;
  Dire Maul at 55-60. (Names approved, Zukk'ash Hive included: Kyle, "Names are fine".)
- **The World Tree and the Sky, 42 to 60 (started 19 Nov 2026): `docs/worldtree_brief.md`.** Kyle: boat from
  Grom'gol, the island 42-44, three tier maps 44-48 with a massive troll city (the Great Settlement, the Highbough
  Tribes) in the middle, then the sky all the way to 60: the Sunward Crown, the Celestial Expanse, Aurelion (the
  Aetherian capital), the Talon Spires (the Veyr), the Elder Citadels (the Kharad), the Fading Firmament. First
  contact with the Aetherians, whose world is dying. Art stock written: `docs/worldtree_art_prompts.md` (W1-W6) and
  `docs/sky_art_prompts.md` (SK1-SK19; BK1, the sky layers in one sheet, and BK6-BK12). **Landed 19 Nov: the whole sky stock** (SK1 to SK19, the sky layers BK1, the sun overlay BK6 and all six
  panoramas), sliced: 132 tiles, 144 props, 216 buildings, 27 landmarks, 108 creatures, 6 sky layers. Still to come:
  nothing: SK17B (SK17's missing twelve plus 36 spares) and the tree's W1 to W6 landed the same night (48 tree tiles,
  72 props, 45 buildings and landmarks, 36 creatures). Next: build the tree on existing art (like Feralas) while the sheets
  are made. Kyle, 19 Nov: all three sky peoples get factions (four new factions with the trolls). Names and the Aetherian split settled ("This is good"). 20 Nov: Rootwater Isle (42-44) built complete: map, 22 creatures and 4 rares, the landing's people, the Highbough Tribes faction, 32 quests, gathering, fishing and secrets (docs/worldtree_build_log.md). 20 Nov: the Lower Boughs (44-45) and its cave, the Knothollow, built the same way. Kyle: three capitals in the sky, the Great Settlement big but below them, caves into the tree. 20 Nov: the Great Settlement built (city, services, 31 people, 12 quests) with the Highbough Tribes' shelf; on the way, kills and explores in every "The ..." zone were fixed (they could never count) and 20 zero-damage reward weapons armed. 20 Nov: the Middle Boughs (45-47) and Shriekhollow built (31 quests); the Heartwood Hollow (the tree's dungeon) is drawn and sealed, waiting for Kyle's call. 20 Nov: the Upper Boughs (47-48) with the Stormsplit, and the Cloudbreak (48) with the game's first cutscene at the mural (27 quests, plus the hand-off up from the Middle Boughs); the tunnel and the climb straightened for Kyle ("less zig zag"). Next: the sky renderer and the Sunward Crown, so the cutscene has somewhere to land.
- **Saved for after:** a sky race's starting zone, 1-24 over four maps, ending at their capital with airships to
  Orgrimmar or the Undercity (the brief's last section).
- The Zukk'ash Hive (Feralas's silithid hive, Kyle's "writhing deep") tunnels through to the Dry Deep under the Abyssal Sands (Kyle: "the
  silithids are digging").

## 1f. The forward base: an endless descent into the uncharted (idea, Kyle, 19 Nov 2026; after Feralas)
- Kyle: "give players the option to actually embody the 'Frontier' aspect and build a forward base into the uncharted?
  Like an unlimited procedure generated dungeon that keeps going until you die?" Saved as an idea; Feralas comes first.
- What exists to build on: `world/zone_generator.py` already makes terrain procedurally, dungeons run on packs of 3-4
  with a boss (`world/dungeon_packs.py`), `world/difficulty.py` and the sim tools (`tools/sim_viability.py`,
  `tools/sim_campaign.py`) can tune depth before anyone plays it.
- The base is a small built-up camp: crafting stations, a mailbox, the bench, a hearth point, upgraded over time.
- Calls to make first (Rafa's pushback): scaling past 60 so depth means something (Mythic+/rift style); loot that
  doesn't outrun raid and hidden-boss gear (depth pays materials and base upgrades, gear capped under raid tier); what
  death costs (the run's loot at risk, recruits kept safe given the bond system); the lore hook (the Integration keeps
  pushing out new ground). It's a home-brew exception to "every dungeon is hand-crafted", so that's Kyle's call too.
- First cut if wanted: a level 60 only descent from one base camp, one tileset, sim-tuned, then expand.

## 2. Banks, auction houses and mail (Kyle, 17 Nov 2026)
- **Every bank, auction house and mailbox stands together** (Kyle: "generally we will want an auction house, a bank,
  and a mailbox close together"), using the new grand buildings (`docs/bank_auction_art_prompts.md`, sliced to
  `bank_<style>` and `ah_<style>`: orc, Forsaken, tauren, blood elf, goblin, human), with MerchantTusk at the bank's
  door and the auctioneer at the AH's. Timbermaw Hold is done this way. Still to do: Orgrimmar, the Undercity,
  Freewind Post, Booty Bay, Ratchet and Steamwheedle Port (and any other town with a banker or an auctioneer), which
  today use their own culture's older art or stand in the open.

## 3. Secrets and hidden zones (names and counts only)
- **The Gilded Vale** (a skull zone) leading to **the Emberwild** (its frontier), painted with the Azshara autumn
  set, "elsewhere in the world". The parent zone is chosen blind and never written down.

## 3b. Tier 1: four raids (Kyle, 20 Nov 2026, `docs/raid_tier1_design.md`)
- The Fallen Bluff (14), a Celestial raid in the sky's Expanse (about 7), a Tempest raid rising off the Tempest
  Isles (4), an Underdark raid under Kael's Bastion (3). All drop item level 68; Cairne Unmade alone drops 71.
- Sets: one per class (30 x 6 = 180 pieces: head, shoulders, chest, hands, legs, feet), a version per spec with
  its own name, stats and 2/4/6 bonuses, swapped free at an Artifact Keeper like T0; icons shared per class.
- Attunement chains to unlock each raid, kept on the character; a rare AH item makes an unlock account-wide.
- Open: the three new raids' names and themes, slot split between raids, the AH item's price.

## 3a. Heroic dungeons (stage 1 built 18 Nov 2026, `docs/heroic_design.md`)
- **Stage 2:** a badge from every heroic boss and a badge vendor selling 66 gear; one heroic-only rare 66 per dungeon
  from its last boss.
- **Stage 3:** one heroic-only trick per boss; now and then a heroic-only boss ("for spice").
- **Master crafting, more of it** (built 18 Nov 2026, `docs/master_crafting.md`): the 71 showpieces wait for the raid's
  materials; epic cloaks, belts and bracers; Alchemy and Enchanting at Master. **Art:** sheets M1 and M3 of `docs/master_crafting_icon_prompts.md` landed 18 Nov (56 icons); M2 (36: the
  Manticore-Scale mail, Chimera epics, Mending/Tidemail/Wildstalker/Brute pieces, the jewellery, Dreamsilk) is still
  to paste. Until then those pieces wear a shared or recoloured stand-in.
- **Later:** the skull zone (68) and frontier zone (69) heroics; tuning the elite multipliers (health x1.3, damage
  x1.15) once played.
- **The level-60 gear ladder** (Kyle, 18 Nov 2026), item levels: normal 60 dungeons 60-63, Honored rep 62, Revered
  rep 66 ("Ok revered at 66", level with heroic blues, since a tabard gets you to Revered through heroics), heroics 66
  (68 and 69 for the two special kinds), Exalted rep 68 (the same as T1 but no set bonus; 250-350g), the Fallen Bluff
  (T1) 68, Cairne Unmade 71. The rep gear and heroics are on it (see backlog_fixed); the raid's loot gets its
  numbers when it's built.

## 4. Classes, combat and balance
- **The turn timeline** (Kyle, 20 Nov 2026): a turn-order bar on the right of combat, allies right and enemies left,
  time running down, with a ghost of where a spell would drop you when you hover it, so Haste and cast speed
  can be seen and planned. Needs a cast-speed pass over every class first. `docs/turn_timeline_design.md`.
- **Tanks on the new armour curve**: the caster/tank shield split isn't built; tank abilities and block, dodge and
  parry haven't been re-tuned to carry more of the load. Look at it once Kyle has played a tank.
- **Primalist talents**: 18 talents point at abilities unlocked in another tree (`validate_class`). Kyle: "hold off on
  for now."
- **Runemaster**: the kit went from 63 abilities to 39 in the refine pass. Kyle to say whether it now plays smoothly
  turn-based, or whether the sigils and glyphs need their own overhaul.
- **Recruit kit text I changed** because the game has no such thing (the list in playtest_backlog_2026_11_10, group
  N): Kyle to veto any.
- **Shelved by Kyle:** an hp5 tank (a tank built round health regeneration).
- **From the 19 Nov levelling run (after the rares were split from bosses):**
  - **XP pacing** is Kyle's call: kill XP is about twice quest XP from the 30s on, so a quester out-levels the zones.

## 5. UI
- **Screen backgrounds** (Kyle, 14 Nov): a faint per-zone underlay inside the quest dialog (Barrens quests look
  Barrens), then the profession and Soul screens. It needs per-zone art prompts.
- **Scroll wheel**: fixed on 14 Nov. Kyle to say if any screen still clicks on a wheel turn.

## 6. Quests and writing
- **Quest mail** (designed with Kyle on 15 Nov, parked behind the Plaguelands): follow-ups, mail-start quests,
  thank-you rewards, hidden chains with no hints. A draft module exists (see the auction house build log).
- **New chains that connect zones and build to something** (left over from [37]).
- **Earth people throughout zones** (Kyle, 14 Nov: "we should start having more earth people throughout zones"):
  transplants with a purpose, more of them the higher the zone. Azshara has them built in; the older zones need a pass.
- **Recruit personal quests** aren't built (the Sworn skills are, Wave 4, 19 Nov). Tarek's ending and his trip and
  break numbers wait on Kyle, and so do Neil's ending, Valentina's sun and Marisol's brother.

## 7. World and towns
- **The Crossing** (Kyle: "my favorite design concept of double dungeon via invasion"): a visual pass on the Booty
  Bay to Ratchet boat (deck, rigging, the sea round it).
- **33 authored pieces still missing from their maps** (measured 17 Nov): not a restore list. Only put back what a
  town of that size needs (`qa_authored_pieces_appear` lists them).
- **Fourth Peg**: look again at what was ugly round the old camp ground on the Abyssal Sands now that the town is
  its own map.
- **Glittervein** (Kyle to look): the rim is a big ring of nearly empty sand, and the cliff texture's repeat shows
  when the whole zone is on screen.

## 8. Items, gear and economy
- **Quest rewards off the item curve** (found 20 Nov 2026 by `audit_item_curve`, which has been failing with 1,441
  off-curve items): the crafted-identity reward maker leaves about one quest reward in eight outside 0.65-1.45 of its
  slot's budget (two-handers weak; heads, shoulders and shields strong). Fixed for the World Tree's four quest
  builders (they now call `fit_to_curve`). Still off: Feralas, Moonglade, Azshara, Deadwind, Stonetalon and the other
  builders with `author_rewards`, plus older hand-written files. Re-running those changes shipped rewards' stats, so
  it waits for a look at which builders are still safe to re-run (two Ashenvale ones aren't: they refuse without
  `--force`).
- **Gear sets** (parked by Kyle): 6-piece and 8-piece bonuses, drop tables for the T0 sets (waiting on the 50-60
  dungeons), T0.5, and 3- and 5-piece sets.
- **Isle epics** are in the global pool, not isle-only. Fire resistance gear waits on the player-side resistance
  rescale (resistance_player_side_rescale_PENDING).

## 9. Crafting
- **Upgrading found gear with your trade** (crafting_raid_upgrades_BACKLOG, Kyle and his friend, 16-17 Nov). The
  design is nearly settled: research a piece by destroying two or three duplicates, then pay materials for each
  upgrade, picking which stat to boost or add, worth about 2-3 item levels per upgrade. Still to hammer out: how
  many upgrades, which stats can be added, cost per stat, re-rolls, family or single item, and kits alongside or
  instead. Then build it.
- **A8. Recipe sources rebalanced**, so the best crafted pieces are found rather than trained.
- **Higher-end frontier dusts, essences and shards** (later).

## 10. Art (prompts written; waiting on sheets, or on slicing)
- **Landed 20 Nov ("lol go wild")**: RC1 (36 recipe scrolls; the second RC1 in the drop came back garbled and was
  set aside), F6 and F7 (the twelve AH forms now turn four ways on the map), F8 to F10 (18 class-form looks; of two F8s
  the first was used) and I1 (an icon per look), H9 and H10 (the twelve wild mounts: each drops at 5% from one
  open-world rare that fits it, `tools/build_collection.py` WILD_MOUNTS) and H11 to H13 (sixteen Exalted mounts, 100g
  each from the faction's first quartermaster once you're Exalted; bound to the buyer like every rep item).
- **Landed 20 Nov (the art backlog, `docs/art_backlog_2026_11_20.md`)**: I2 (28 reins), M2 (36 Master crafting icons), H14
  (the Feathermoon War Owl and the Cloudtop Wyvern at Exalted, and the Aetherians', Kyr'vahl's and Ul'Kharad's mounts
  drawn and waiting for their factions), I3 (their reins and five tabards) and K1 to K3 (all 98 keepsakes). Two
  keepsakes came back as the wrong object and can be re-rolled any time: Esteban's radiation badge (drawn as a sheriff's
  star) and Emre's first lock pick (drawn as a pickaxe).
- **The Feathermoon Sentinels' Exalted mount**: done (the Feathermoon War Owl, sheet H14).
- **Class forms in combat**: since 18 Nov a shifter walks the map as their form (assets/forms); the combat screen
  still shows the person. Kyle asked for "out of combat" only, so this is a question, not a bug. The Tinker's
  Mechsuit is only ever worn inside a fight, so its picture and its three looks (sheet F9, 20 Nov) are drawn but
  never shown; the looks are held off the AH (`HELD_LOOKS` in `tools/build_collection.py`) until this is decided.
- **The professions screen's own art**: tab art, frames and station art.
- **Keepsake icons, 98**: landed 20 Nov (K1 to K3).
- **Player sprites** (Kyle, 20 Nov 2026): five male looks for each playable race, four facings, empty hands
  (`docs/player_sprite_prompts.md`, sheets P1 to P7, the Veyr's too; sliced by `tools/asset_pipeline/slice_player_sheet.py`). The
  playable races are to be orcs, tauren, Forsaken, Aetherians, humans and blood elves; an Aetherian start zone and a
  blood elf one come later. When the sheets land, the new looks go on the END of each male list in
  `world/race_registry.py` (saves store a place in that list) and the creator offers only the new five. Women later.
- **Player sprites landed 20 Nov** (all seven races) and are in the creator; the barber's chair catches any save whose
  look is gone.
- **Walk cycles**: one sheet a race, drawn from that race's turnaround sheet as the single reference
  (`docs/player_sprite_prompts.md`, "Walk cycles"; sliced by `tools/asset_pipeline/slice_walk_rows.py`).
- **The recoloured T0 set versions** are plain hue turns (some gold sets come out lime). Kyle's eye.

## 11. Tools

- **The baker darkens a whole map when any tile is sealed.** `tools/bake_ashenvale.build_scores` sets the woods field
  to at least 0.4 everywhere as soon as a map has one sealed tile (pockets props close off), so the whole map gets the
  deep-forest shadow. Found on Timbermaw Hold (it baked dark brown instead of gold), which now builds with nothing
  sealed. The fix is one line, but it re-lights every zone baked with sealed tiles the next time each is baked, so it
  needs a before-and-after look at each of them.

## 12. Parked by Kyle (not anytime soon)
- **The prestige constellation** (design only, docs/prestige_constellation.md).
