# Auction house, rep items and crafting pass (16 Nov 2026)

Kyle's notes from playing, the same evening, and what each one became.

## Auction house
- **"Some lvl 61 items"**: gear above item level 62 came out "Requires level 61" and up, which nobody can wear. Four
  Bone Colossus drops and seven secret-seller pieces. Required level is now capped at 60 where gear is made
  (`entities/loot_generator.MAX_REQUIRED_LEVEL`, `tools/build_durotar_content.make`), and the data is patched. A
  recipe for item level 61 gear lists as level 60.
- **"Green markings on some weapons"**: the green lines are secondary stats (crit rating, attack power, healing), the
  same as WoW's green "Equip:" lines. Primary stats are white.
- **"Never allow rep items to be sold"**: `world/rep_items.py`. A rep item is anything a quartermaster sells from
  Honored up (their gear, the shoulder inscriptions, rep recipes and the gear those recipes make). It can't be
  listed or mailed, the AH's own sellers never list one, and a save that had one listed drops it on load.
- **"They should have a rep requirement"**: a quartermaster's gear and the inscriptions now need the standing they're
  sold at to wear or read on, and every tooltip says so ("Requires The Argent Dawn - Revered"). Gear you craft from
  a rep recipe needs no standing.
- **"Populate the AH by around 300% more", then "fleshed out 5 times over"**: 13,000 Horde and 8,500 Steamwheedle
  listings (2,600 and 1,700 before). Restocking trickles in a couple of listings a frame instead of all at once each
  hour, so a market hour costs about a tenth of a second. The books are compressed in the save (about 2 MB).
- **Mob materials, runes, enchant scrolls, enchanting materials**: mob drops were already listed. The others were
  missing because disenchanting wasn't counted as a source of dust, essence and shards, so nothing made from them
  was either. Now on the AH: 24 enchanting materials, 5 rune inks, 210 runes, 163 enchant scrolls. Prices run from
  cheap to absurd, as asked: a minor scroll about 6 silver, Crusader about 120 gold, runes up to about 400 gold.
- **Enchant scrolls anyone can use**: already true. Reading a scroll on needs no Enchanting skill; only disenchanting
  does.
- **COD letters**: "offer expires in three days" while the mail said 2 days was the countdown rounding down. It
  rounds up now. And "a max of around 5% of the time": no stranger's letter (COD, fat finger, sniped) goes out more
  than one time in twenty. Payouts and deliveries always come.

## HUD and inventory
- **Mail and Encounters**: both moved to the bottom left under the action buttons. New mail is a gold badge that
  breathes, with the flag and a count bubble; Encounters sits beside it in a fixed spot and can be clicked (E still
  works).
- **Inventory top row**: all five buttons share one look; the open tab is gold. The skills line no longer runs
  under the Close button.
- **Potion tooltips repeating**: the card works out the effect line itself and now drops any sentence of the item's
  description that says it again. The level is said once, in red when you're under it. Durations read "30 minutes".

## Crafting
- **Armor kits did nothing**: Light, Medium and Thick Armor Kits now read on like an enchantment (chest, legs,
  gloves, boots) for 6, 19 and 36 armor. They take the item's enchant slot, as in classic. `tools/armor_kits.py`.
- **Runecrafting progression**: every rune is written with the newest ink you can already make, and each rank's
  families are spread across their own stretch: Lesser runes 5 to 55, Lesser Capstones 65 to 115, runes 125 to
  175, Capstones 185 to 235, Greater runes 245 to 281, Greater Capstones 285 to 300.
- **Start at skill 0**: every trade's first recipe is at 0 (nothing needs exactly 1), Strange Rune Ink at 0, and
  enchanting's first formulas spread from 0 to 30. `tools/qa_recipes_start_at_zero.py`.
- **Leather conversions**: 3 Scrap to Light (0), 4 Light to Medium (100), 5 Medium to Heavy (150), 6 Heavy to Thick
  (200), 6 Thick to Rugged (250), trainer-taught, and they skill you up. `tools/qa_leather_conversions.py`.

## Also the same day
- Dying in the Valley of Trials wakes you at the Valley camp (Deathknell at its graves); Durotar and the Echo Isles
  at Razor Hill; a map with no town of its own at the nearest town or camp by road.
- Every creature under level 10 deals 20% less damage and has 15% less health.
- Map icons for mailboxes and auction houses.
