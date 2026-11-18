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

---

## 1. Azshara (in progress, in Kyle's order: "One thing at a time")

Brief: `docs/azshara_brief.md`. Done so far: Kyle's six art sheets, West Azshara, Talrendis Landing, Orgrimmar's north
gate and the Ashenvale East road.

1. **Timbermaw Hold**, the caldera city: the largest town yet, gate on the south (from West Azshara), the tunnel's
   door on the west. It has an inn but no flight point, and the sealed deep gate is there for the fel rot dungeon.
   - Kyle, 17 Nov: the Timbermaw **quartermaster and the leader (Elder Haldor) move up into the Hold**, out of the
     tunnel.
   - **The tunnel's east passage**: a long passage out of the Honey Galleries to a new door that leads to the Hold.
2. **Central Azshara** (54-57): the Highborne ruins and the salvage dig, Lake Mennar, the leylines, the satyr and
   demon camps, and the naga grotto's door on the Bay of Storms.
3. **East Azshara, the coast** (56-59): the drowned shore, reefs, temple ruins, the Tower of Eldara, in the drowned
   teal palette.
4. **The rising**: a save-flag swap that raises the drowned district at the end of the East chain, which puts the
   Vault's door in it.
5. **The caves**: the satyr den (Haldarr) and the naga grotto, with bosses, loot and encounter tables.
6. **The fel rot under the Hold** (dungeon, 55-58, 5 bosses): every boss pays Timbermaw.
7. **The Vault of Zin-Azshari** (dungeon, 59-60, 6 bosses over two floors), Scholomance-sized. Kyle settles the two
   dungeons' names and rosters (the art uses working names).
8. **People and content**:
   - Creature records from sheet 5 and encounter tables (West Azshara has none yet).
   - About 90 quests, about 70% given in the Landing and the Hold.
   - **The Sunreach Conclave** faction and its TBC shelf. Its leader and quartermaster stay quest-free, because the
     elves get an island later.
   - Two or three recruits: a blood elf magister, an orc salvager and a transplant.
   - The hidden content ("Surprise me"). Never described.
9. **Later, Kyle's call**: the Sunreach Conclave's island home.

## 2. Secrets and hidden zones (names and counts only)
- **The Gilded Vale** (a skull zone) leading to **the Emberwild** (its frontier), painted with the Azshara autumn
  set, "elsewhere in the world". The parent zone is chosen blind and never written down.

## 3. Classes, combat and balance
- **Grovekeeper healing** (backlogged by Kyle): the Primalist melee healer falls short of its 75% target because its
  spec aura is capped. The fix goes in its kit (more or bigger heals, or Hammer of Life's splash), not the cap. The
  healer-kit pass is still to do (heal_formula.md: aim for 0.9-1.1).
- **A healer one-shot by a boss** (friend's playtest, 14 Nov): we need which boss and what hit. Check the 50+ boss
  kits for a single hit above a cloth healer's health.
- **Dungeon packs**: the 11 older dungeons in `build_dungeon_pulls.py` still make packs of 3-4. Raise them to 4-5, or
  keep 3-4 below level 30? (Kyle's call.)
- **A QA check that fails any fixed-spawn dungeon missing from trash_packs.json**, so no new dungeon ships with lone
  trash.
- **Tanks on the new armour curve**: the caster/tank shield split isn't built; tank abilities and block, dodge and
  parry haven't been re-tuned to carry more of the load. Look at it once Kyle has played a tank.
- **Dodge plus parry on an Agility rogue** still reaches the 50% combined cap at 60 (the target was under 40%).
- **`validate_class` fails two classes**: Primalist (18 talents point at abilities unlocked in another tree) and
  Starcaller (Keen Sight's Int-to-ranged-AP is 10x smaller than every other tree's).
- **audit_recruit_combat** still exits 1 on Ryan's Health Funnel healing his Felhunter.
- **Runemaster**: the kit went from 63 abilities to 39 in the refine pass. Kyle to say whether it now plays smoothly
  turn-based, or whether the sigils and glyphs need their own overhaul.
- **Other free or instant summons** (Hunter Tame Beast, Primalist Spirit Beast Master, the Witch Hunter whistle;
  Stormbringer Air Elemental, Tinker ZIGGI-6K, Ranger War Falcon and the Necromancer raises are instant): treat them
  like the Warlock's, or leave them as they are on purpose? (Kyle's call.)
- **Recruit kit text I changed** because the game has no such thing (the list in playtest_backlog_2026_11_10, group
  N): Kyle to veto any.
- **Shelved by Kyle:** an hp5 tank (a tank built round health regeneration).

## 4. UI
- **Icons on the battle screen** (Kyle, 15 Nov: "the next UI item after classes"): ability icons on the combat hotbar
  instead of labelled boxes. Hovering one shows the name, the damage, healing or potency range, cast speed, cost and
  cooldown. Party buffs and debuffs as icons with hover text.
- **Screen backgrounds** (Kyle, 14 Nov): a faint per-zone underlay inside the quest dialog (Barrens quests look
  Barrens), then the profession and Soul screens. It needs per-zone art prompts.
- **Combat log**: an "(as Frost)" note on hits a rune converted to another element.
- **Scroll wheel**: fixed on 14 Nov. Kyle to say if any screen still clicks on a wheel turn.

## 5. Quests and writing
- **22 SILENT direction findings** (outside Stonetalon): the text names no direction for a far target.
- **Quest mail** (designed with Kyle on 15 Nov, parked behind the Plaguelands): follow-ups, mail-start quests,
  thank-you rewards, hidden chains with no hints. A draft module exists (see the auction house build log).
- **New chains that connect zones and build to something** (left over from [37]).
- **Earth people throughout zones** (Kyle, 14 Nov: "we should start having more earth people throughout zones"):
  transplants with a purpose, more of them the higher the zone. Azshara has them built in; the older zones need a pass.
- **Recruit personal quests and Sworn** aren't built. Tarek's ending and his trip and break numbers wait on Kyle.

## 6. World and towns
- **NPCs into towns, part two**: quest givers meet the 70/30 rule in every zone (`qa_quest_hubs`). The rest of the
  town roles (trainers, vendors, innkeepers) standing outside their towns haven't been swept, and no check covers
  them yet.
- **The Crossing** (Kyle: "my favorite design concept of double dungeon via invasion"): a visual pass on the Booty
  Bay to Ratchet boat (deck, rigging, the sea round it).
- **33 authored pieces still missing from their maps** (measured 17 Nov): not a restore list. Only put back what a
  town of that size needs (`qa_authored_pieces_appear` lists them).
- **Ragefire Chasm** has an NPC tile at (100,100), inside solid rock, that no data file accounts for. Cause not found.
- **Fourth Peg**: look again at what was ugly round the old camp ground on the Abyssal Sands now that the town is
  its own map.
- **Southshore's QA leftovers**: verify_portals' one-way links to hidden maps, and qa_hillsbrad_quests (the giver of
  arw_through_the_wall, tarren_mill_flight_master, has no spot in Tarren Mill's layout).
- **Glittervein** (Kyle to look): the rim is a big ring of nearly empty sand, and the cliff texture's repeat shows
  when the whole zone is on screen.

## 7. Items, gear and economy
- **A QA check that no hand-authored item carries a percentage rating stat** (the ratings conversion is done; the
  guard isn't).
- **Gear sets** (parked by Kyle): 6-piece and 8-piece bonuses, drop tables for the T0 sets (waiting on the 50-60
  dungeons), T0.5, and 3- and 5-piece sets.
- **Isle epics** are in the global pool, not isle-only. Fire resistance gear waits on the player-side resistance
  rescale (resistance_player_side_rescale_PENDING).
- **Crafted intermediates** (scopes, pages, kits) aren't on the material price curve. Price them from their recipes.
- **Old saves**: quest-reward gear in a save from before the price curve keeps a 0 sell price.

## 8. Crafting
- **Upgrading found gear with your trade** (crafting_raid_upgrades_BACKLOG, Kyle and his friend, 16-17 Nov). The
  design is nearly settled: research a piece by destroying two or three duplicates, then pay materials for each
  upgrade, picking which stat to boost or add, worth about 2-3 item levels per upgrade. Still to hammer out: how
  many upgrades, which stats can be added, cost per stat, re-rolls, family or single item, and kits alongside or
  instead. Then build it.
- **A8. Recipe sources rebalanced**, so the best crafted pieces are found rather than trained.
- **Higher-end frontier dusts, essences and shards** (later).
- **Junk and salvage fishing catches**: the sprites are sliced but unused. They need their own catch table.

## 9. Art (prompts written; waiting on sheets, or on slicing)
- **The 82 crafted epics' own icons** (claude/crafting_epic_icon_prompts.md): 0 of 82 so far. They show the shared
  epic stand-ins until then.
- **The two crafting icon-fix sheets** (claude/crafting_icon_fix_prompts.md): slice when they arrive.
- **The professions screen's own art**: tab art, frames and station art.
- **Icons for the four new Alchemy items**: Elixir of Shadow Power, Flask of Mending, Free Action Potion and Potion
  of Invulnerability.
- **Greater Heal and Chain Heal** need proper icons (stand-ins today).
- **Walk cycles**: rolling out sheet by sheet by playable race (claude/walk_cycle_prompts.md).
- **The recoloured T0 set versions** are plain hue turns (some gold sets come out lime). Kyle's eye.
- **The Underdark's loot table** favours caster gear (68%; the check wants 40-60%).

## 10. Parked by Kyle (not anytime soon)
- **The prestige constellation** (design only, docs/prestige_constellation.md).
- **Recruit bonds beyond the pilot three** (Kesten, Adrián, Tarek), after their personal quests.
