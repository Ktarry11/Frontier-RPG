# Tier 1: four raids, class sets, and earning the way in

Kyle, 20 Nov 2026: "I hate how wow classic has 1 T1 dungeon. I'm thinking we have The Fallen Bluff (14 bosses) I'd also
like 3 other 'smaller' T1 raids. One in the celestial advance with about 7 bosses. One that is rising from the coast of
Tempest isles as Naga are summoning a water elemental god from the deep to wipe out EK (4 bosses) and a small one in the
underdark where the Bastion dug too deep and unearthed a ancient antechamber with 3 bosses. The raids will all drop
identical loot level except Cairne Unmade (he alone drops higher level). And for T1 ... T1 onward will be 6 pieces only
since we have 30 classes. So 180 pieces. T1 onward, each spec will get their own unique set (but we DONT need to recolor
between sets ...)."

Then: "Quests to unlock raids. The raids should take effort to unlock and the 'collectable' can be stored on the
character with an option to buy a rare item off the AH to allow these raid unlocks to transfer between characters."

And on the sets (asked, 20 Nov): "One set per class then the ability to swap out pieces as we have for T0", in head,
shoulders, chest, hands, legs and feet.

## The four raids (28 bosses)

| Raid | Where | Bosses | What it is |
|---|---|---|---|
| **The Fallen Bluff** | Mulgore (Thunder Bluff) | 14 | Already designed and drawn (`docs/mulgore_raid_boss_prompt.md`, sprites `fb_`): the Central rise 5 with the final boss last, Hunter 3, Spirit 3, Elder 3. Cairne Unmade is its last boss. |
| **The Celestial raid** (name to come) | the Celestial Expanse, on the Aetherian sky continent | about 7 | Kyle's "celestial advance". The Expanse holds the ancient aerial ruins older than anyone up there, with Kharad-age machinery waking in them (docs/worldtree_brief.md); a raid in their deepest ruin, or an Ascendancy advance, is the obvious pair. Kyle to say which. |
| **The Tempest raid** (name to come) | rising from the coast of the Tempest Isles | 4 | The naga are summoning a water elemental god from the deep to wipe out the Eastern Kingdoms; the raid rises out of the sea off the isles. The god is our own, not a borrowed one. |
| **The Underdark raid** (name to come) | the Crystalline Underdark, under Kael's Bastion | 3 | The Bastion dug too deep and broke into an ancient antechamber. A small raid: what's behind it stays for later. |

**The loot is one level for all four**: every T1 raid drops item level 68 (the ladder in
`docs/backlog_nov17_onwards.md` section 3a), so no raid is the "right" one to farm. **Cairne Unmade alone drops
higher**, item level 71.

## The sets: one per class, a version per spec, six pieces

- **30 sets of 6 = 180 pieces**, in head, shoulders, chest, hands, legs and feet. Wrists, waist and everything else
  stay loose raid drops.
- **The T0 model** (`tools/qa_gear_sets.py`, claim 8): one set per class, with a version of each piece for every spec.
  A version has its own name, its own stats and its own 2, 4 and 6 piece bonuses; slot, level, rarity and the set don't
  change. Pieces swap between versions free at an Artifact Keeper, so respeccing never means farming again.
- **No recolouring between versions**: a class's specs share the icons. A holy, a retribution and a protection paladin
  look identical and read differently.
- **How they drop**: as tokens for a slot and an armour type, the way T0's do (`world/set_tokens.py`), redeemed at an
  Artifact Keeper for the set piece of whoever wears that armour. Proposal: **every T1 raid drops tokens**, so any of
  the four can finish a set; the small raids simply drop fewer a week. Kyle to say if he'd rather split the slots
  between raids.

## Earning the way in

- **Each raid is unlocked by a quest chain that takes real effort** (Kyle, 20 Nov 2026: "Attunement chains should span
  multiple zones or be quest chains inside the region.. like mulgore to unlock bluffs. But Tempest Isle sends you all
  over...for the sky you need to unlock the first capital to even in the raid etc."):
  - **The Fallen Bluff**: a chain inside its region, Mulgore and Thunder Bluff.
  - **The Tempest raid**: a chain that sends you all over the world before the sea gives the raid up.
  - **The Celestial raid**: first you have to unlock the sky's first capital (Aurelion, through the Aetherian
    continent's own story); only then does the chain to the raid open.
  - **The Underdark raid**: a chain through the Crystalline Underdark and Kael's Bastion (its region), the same way
    as the Bluff's, unless Kyle wants it to range wider.
- **The unlock is a collectable kept on the character**, shown with their other unlocks.
- **A rare item on the auction house** lets the unlock carry to the player's other characters: bought once, it makes
  that raid's unlock account-wide. It fits the Collection (`docs/collection_design.md`), where the AH already sells
  account-wide unlocks. Proposal: one item per raid, priced like a rare collectable. Kyle to set the price and whether
  it's per raid or one for all four.

## Order of work (Kyle's call)

The World Tree is being built now. When the raids come, the natural order is the Fallen Bluff first (its art is done),
then the Underdark raid (3 bosses), the Tempest raid (4), and the Celestial raid once the sky continent's Expanse exists.
Each raid needs its boss art, the 180-piece set sheet work (icons shared per class) and the attunement chains.
