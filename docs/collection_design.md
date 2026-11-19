# The Collection: account-wide unlocks sold on the auction house

Kyle, 18 Nov 2026: "I want to do kind of like an account-wide heirloom and an AH expansion. So ascension used to have
things like 'book of ascension' or 'Book of professions' etc. These were quality of life things that were saved to an
account. I want to start building up some of these things in my game and have them tied to the player (like the guild
bank is) so it'd be a seperate tab and these items are randomly sold in the AH and have varying prices... and can be
many many many things. Like unique mounts, or callboards that offer daily quests, or feathers that can unlock flight
paths on a continent. Or unlocking unique cosmetic shape-shifting forms etc. This will need a new system tab that's
account-wide."

## Kyle's answers (18 Nov 2026)

| Question | Answer |
|---|---|
| What happens when you use one | **Learn once, every character has it**, old and new. A learned thing can't be resold. |
| Prices | First **50g to 750g** (I pushed back on 2000g: a level 55 quest pays about 1.5g, so 2000g was about 1,300 quests). Then, for the mass-made kinds: "Some are dirt cheap. Some are expensive." So **2g to 750g**. |
| How they show up | "These are in the AH as people sell them. Not a set price. They can just appear! Under collection tab." Traders list them at their own prices; rare ones turn up rarely. |
| How many | "I'd want 100s to 1000s of fun collection stuff", then "We don't need 1000s to start. We will build it." The AH's Collection section holds **dozens to about 100** at a time. |
| Other sources | **The auction house only.** |
| Mass-made kinds | **Creature forms, mount colours and titles.** |
| Mount colours | "don't full colour shift mounts. **Hue shift them.** And I'll get art." |
| First wave | **Unique mounts, flight feathers, cosmetic forms, and training books** ("a mobile class trainer or every profession trainer"). |
| Extras | **Heirloom gear, QoL tomes, a portable bank and a portable vendor to sell trash**, all on long cooldowns. My ten extra suggestions: all approved. |
| Portable cooldowns | **Once per market day** (the auction house's clock, so dungeons and the hearth move it on). |
| Heirlooms | **Scale with the wearer, and give XP: +80% in all.** A two-hander is +20%; a one-hander, shield or off-hand is +10% each. The other 60% is **six armour pieces at +10%**: head, shoulders, chest, legs, cloak and a trinket. **Ten pieces that fit whoever takes them.** |
| Forms | **Map only.** The party leader walks the overworld as the creature; combat and portraits stay normal. |
| Mounts | **Still need riding.** Learned for the account, ridden at the character's own riding speed. |
| Feathers | **Two: Kalimdor and the Eastern Kingdoms.** Islands go with the continent their flights connect to. |
| Where you see it | "We should be able to see our stuff from character. So anywhere. Not bank." |
| Later | Callboards and daily quests (a new daily-quest system, the biggest piece) come after this. |

## How it works

**The account file.** The Collection lives beside the guild bank in `data/saves/account_collection.json`, outside
every save slot, so it belongs to the player, not a character. Learning is one transaction, the same way the guild
bank does it: the item leaves the character's bags, the Collection writes its file, and the character is saved in
the same breath. If the save fails, the Collection rolls back, so an item can never be both learned and still in your
bags.

**The items.** Each collectable is a bag item (like a recipe scroll) with a `collection_id`. Right-click it to learn
it. Until it's learned it's an ordinary item: you can mail it, bank it, or put it back on the auction house.

**The tab.** The **Collection** screen opens from the overworld's tab column or with **U**, anywhere. It has six tabs
(**Mounts**, **Forms**, **Titles**, **Travel** with the feathers, hearths and tomes, **Services** and
**Heirlooms**), a filter (all, learned, missing) and a search you type into. Learned things come first in their
rarity colour, each with a button that does it: ride, wear, use a title, take the second hearth, call a service, or
take an heirloom copy. Missing ones are greyed with their name, so you can see what's still out there.

**The auction house.** A **Collection** category in both houses, with the same six subcategories. Traders keep
about 60 to 120 collectables listed across the two books (55 and 35 at full stock), each for about a market day.
New listings arrive through the day as old ones sell or end, picked by rarity, so common ones are always around and
the epic ones are a couple at a time at most. Each trader asks their own price around the market's going price for
that item, which wanders like everything else, and NPC collectors buy one now and then, so something you're
watching can vanish.

**The portable services.** Each is used from the Services tab, never in combat, and then waits one market day (24
market hours) before it can be used again. The wait belongs to the character, since the market clock lives in each
save.

**Heirlooms.** Kyle: "We should have the heirlooms as we need cloth, leather, mail, and plate. And all the weapons,
shields, OH, etc.", "You know how heirlooms work", and the families: "caster cloth, healer cloth, agi leather, healer
leather, caster leather, dps mail, caster mail, healer mail. Dps plate, tank plate, hybrid plate, healer plate." So each
heirloom is its own item: twelve armour families of four pieces (helm, shoulders, chest, legs), a cloak and a
trinket for each of the six stat families (caster, healer, agility, strength, tank, hybrid), and every weapon a spec
actually wields in its family, 106 in all. Learning one adds it to the Heirlooms tab, and any character who can wear
it can take a copy (one at a time). A copy is bound to the account, can't be sold or auctioned, is wearable from 1 to
60, and is remade at the wearer's level every level-up with its family's fixed stats, worth about 85% of a blue of
that level ("slightly worse than items of the same level as they have the exp boost in them"). The XP bonus is the
**leader's**: "They also affect the whole party so the main player wears them and party quest / kill exp improves so
the main character doesn't blow past his allies." A two-hander is +20%; a one-hander, shield or off-hand +10%; each
armour piece, cloak and trinket +10%; +80% at most; ranged-slot pieces give none; nothing at 60.

**Titles.** The leader wears one at a time; it shows under their name beside the map and on the character sheet.

## What's in it (837, built by `tools/build_collection.py`)

| Kind | Count | Price | Where it comes from |
|---|---|---|---|
| Mounts | 90 | 25g to 750g | Six unique mounts (their art is still to come) and the twelve mounts in seven hue-shifted colourways: Rose, Dawn and Spring (uncommon), Jade, Tide and Dusk (rare), Twilight (epic). The colourways are made from the mount's own art when drawn (`world/collection_art.py`), until Kyle's art replaces them. |
| Forms | 465 | 2g to 750g | Ten named in the design (Murloc, Kobold Miner, Gnoll Brute, Treant, Ooze, Carrion Vulture, Furbolg, Wandering Skeleton, Spirit Wolf, Shade of the Drowned Court), then one for every creature picture in the open world, named for the earliest ordinary creature that wears it. Level 1-10 creatures are a few gold; bosses are rare or epic. Nothing from a hidden place, nothing above 60. |
| Titles | 162 | 2g to 750g | `tools/collection_titles.py`: 50 common, 50 uncommon, 44 rare, 18 epic. |
| Travel | 4 | 300g to 400g | Windrider Feathers of Kalimdor and the Eastern Kingdoms, the Tome of the Swift Hearth (half the hearth's cooldown), the Hearthstone of the Second Home (its own bind at any innkeeper, its own cooldown). |
| Services | 6 | 150g to 250g | Travelling Bank, Peddler's Bell (sells anything), Courier's Horn (mail), Book of the Wandering Master (your class trainer), Book of Professions (every profession trainer, so you can learn a new one too), Alchemist's Satchel (reagents). |
| Tomes | 4 | 100g to 350g | Pack Mule (every backpack holds 12 more), Deep Vault (a free extra bank tab, the Collector's Shelf), Quick Study (Apprentice Riding costs nothing), First Steps (new characters start with a six-slot bag and 5g). |
| Heirlooms | 106 | 120g to 300g | Twelve armour families of four pieces, a cloak and a trinket per stat family, and every weapon a spec wields (above). |

Two of the approved extras came out slightly different from how I first wrote them:

- **Pack Mule:** it's 12 more backpack spaces, not a fifth bag slot. A fifth slot means reworking the bag row on every
  bag screen. I'll make it a real slot if Kyle wants.
- **Quick Study:** Apprentice Riding costs nothing at the riding trainer, rather than being handed out at 20.

## Art still to come (`docs/collection_art_prompts.md`)

1. **The six unique mounts**: delivered and sliced 18 Nov 2026.
2. **Mount colourway art** if Kyle wants hand-made versions to replace the hue shifts ("I'll get art").
3. **Icons:** delivered and sliced 18 Nov 2026 (`assets/icons/collection/`).

## Later

- **Callboards and daily quests**: a board in each capital that offers a few daily quests, account-learned so every
  character sees it. This is the next wave, and it needs its own design (what dailies are, what they pay, where the
  boards stand).
- **More of everything**, as Kyle thinks of it: the builder makes the catalogue, so adding a kind is a section there.

## Also built alongside (18 Nov 2026)

**The experience rate switch** (`world/xp_rate.py`), under the leader's bars beside the map. Kyle: "0.5x, 1x, 1.5x,
2x, 2.5x, or 3x EXP which will be for quests and kills. So people can pick their own level of fun." It's kept with the
save and applied last to every quest and kill reward, so the quest card shows what you'll actually get.

## Keepsakes (19 Nov 2026)

Kyle: "a new collection tab. Each sworn member will give something that goes there. it's personal to them and i have
plans for it later." The seventh tab. One keepsake per recruit, written from their Wave 1 profile
(`docs/recruits/`, `data/npcs/keepsakes.json`). It's given the moment they become Sworn (`world/bond_manager`), never
sold, and has no price. A keepsake you haven't been given shows only who it's from, and search won't find it. Each
gets its own icon (`col_keepsake_<name>`) and shows a stand-in until the art lands. QA: `tools/qa_keepsakes.py`.
