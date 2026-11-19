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

## 1c. Mulgore: The Fallen Bluff, the Thunder Bluff raid (art prompts in progress, 18 Nov 2026)
- `docs/mulgore_raid_boss_prompt.md`: Kyle's first raid. Bosses by rise (Central 5 with the final boss unlocking
  last, Hunter 3, Spirit 3, Elder 3), drawn in batches of seven.

## 1d. Moonglade (built 18 Nov 2026, `docs/moonglade_build_log.md`)
- The three dungeons, doors already on the map: the Barrow Dens (corrupted druids), the Dreaming Arch (the Emerald
  Dream), under the lake (the island's stair). What's waking gets decided with the first of them.
- The Cenarion Circle and the Wakened only reach Friendly on quests; the dungeons are the road past it.

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

## 3a. Heroic dungeons (stage 1 built 18 Nov 2026, `docs/heroic_design.md`)
- **Stage 2:** a badge from every heroic boss and a badge vendor selling 66 gear; one heroic-only rare 66 per dungeon
  from its last boss.
- **Stage 3:** one heroic-only trick per boss; now and then a heroic-only boss ("for spice").
- **A crafting tier from the first top tiers: new gear for each profession** (Kyle, 18 Nov 2026: "I'll ALWAYS want
  crafting to be competitive to raiding/Dungeons" and "Then we can add crafting for new gear for each profession").
  The ten level-60 materials (Dreamsilk, Chronoweave, Manticore, Chimera, Frostforged Silver, Sylvanite, Voidwood,
  Dreamwillow, Glacier Sapphire, Sylvan Emerald) craft nothing yet. Needs recipes at the heroic and raid levels
  (66-68, the best maybe 71) in every gear trade, designed with Kyle. NEXT.
- **Later:** the skull zone (68) and frontier zone (69) heroics; tuning the elite multipliers (health x1.3, damage
  x1.15) once played.
- **The level-60 gear ladder** (Kyle, 18 Nov 2026), item levels: normal 60 dungeons 60-63, Honored rep 62, Revered
  rep 66 ("Ok revered at 66", level with heroic blues, since a tabard gets you to Revered through heroics), heroics 66
  (68 and 69 for the two special kinds), Exalted rep 68 (the same as T1 but no set bonus; 250-350g), the Fallen Bluff
  (T1) 68, Cairne Unmade 71. The rep gear and heroics are on it (see backlog_fixed); the raid's loot gets its
  numbers when it's built.

## 4. Classes, combat and balance
- **Tanks on the new armour curve**: the caster/tank shield split isn't built; tank abilities and block, dodge and
  parry haven't been re-tuned to carry more of the load. Look at it once Kyle has played a tank.
- **Primalist talents**: 18 talents point at abilities unlocked in another tree (`validate_class`). Kyle: "hold off on
  for now."
- **Runemaster**: the kit went from 63 abilities to 39 in the refine pass. Kyle to say whether it now plays smoothly
  turn-based, or whether the sigils and glyphs need their own overhaul.
- **Recruit kit text I changed** because the game has no such thing (the list in playtest_backlog_2026_11_10, group
  N): Kyle to veto any.
- **Shelved by Kyle:** an hp5 tank (a tank built round health regeneration).

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
- **Recruit personal quests and Sworn** aren't built. Tarek's ending and his trip and break numbers wait on Kyle.

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
- **Recipe-scroll sheet RC1** (claude/enchanting_recipe_art_prompts.md): Blacksmithing, Leatherworking, Tailoring and
  Woodworking's first three. Kyle, 17 Nov: "just missing blacksmithing - add that to backlog". Until it lands those
  scrolls keep their one picture per profession. (The 18 Nov drop sent RC2 again instead; its Woodworking epic was
  used.)
- **Still to paste from the 18 Nov prompt run** (Kyle: "you can backlog the others"):
  - `docs/form_art_prompts.md` F6 and F7 (the twelve AH forms in four facings; they're in now as one picture each),
    F8, F9 and F10 (looks for the dire bear, void monstrosity, shadowform, mechsuit, weaver and vizier), and I1 (an
    icon per look; the 18 looks in now share three family charms until it lands).
  - `docs/rare_mount_art_prompts.md` H9 and H10 (twelve wild mounts; not built yet, where each comes from is open).
  - `docs/exalted_mount_art_prompts.md` H11 to H13 (one Exalted mount per faction; not built yet, the
    quartermasters sell them at Exalted) and I2 (their reins and the wild mounts').
  - `docs/mulgore_raid_boss_prompt.md` (the Fallen Bluff's bosses).
- **Class forms in combat**: since 18 Nov a shifter walks the map as their form (assets/forms); the combat screen
  still shows the person. Kyle asked for "out of combat" only, so this is a question, not a bug.
- **The professions screen's own art**: tab art, frames and station art.
- **Walk cycles**: rolling out sheet by sheet by playable race (claude/walk_cycle_prompts.md).
- **The recoloured T0 set versions** are plain hue turns (some gold sets come out lime). Kyle's eye.

## 11. Tools

- **The baker darkens a whole map when any tile is sealed.** `tools/bake_ashenvale.build_scores` sets the woods field
  to at least 0.4 everywhere as soon as a map has one sealed tile (pockets props close off), so the whole map gets the
  deep-forest shadow. Found on Timbermaw Hold (it baked dark brown instead of gold), which now builds with nothing
  sealed. The fix is one line, but it re-lights every zone baked with sealed tiles the next time each is baked, so it
  needs a before-and-after look at each of them.

## 12. Parked by Kyle (not anytime soon)
- **The prestige constellation** (design only, docs/prestige_constellation.md).
- **Recruit bonds beyond the pilot three** (Kesten, Adrián, Tarek), after their personal quests.
