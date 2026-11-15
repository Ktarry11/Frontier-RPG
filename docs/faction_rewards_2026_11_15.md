# Reputation rewards: TBC-style quartermasters (15 Nov 2026)

Kyle wants every faction's quartermaster to sell by standing, the way TBC did it:
- "Revered give lvl 60 ilvl 67 blues and exalted gives lvl 60 ilvl 73 epics... aim for 6 blues per vendor AND 3 epics per vendor. There will also be crafting stuff for rep. I WANT THIS TO BE LIKE HOW TBC DEALS WITH REP!!!"
- Exalted epics cost 250-350g.
- "Exalted rep recipes make epics as well! Around Ilvl 73 (but needs a lot of rare ingredients! We can add these later)."
- All nine factions get a shelf, with one quartermaster per faction.

## How TBC did it (looked up first)

Sources: warcraft.wiki.gg "Burning Crusade reputation rewards", wowpedia "Cenarion Expedition", and Icy Veins' Sha'tar guide.

- **Friendly:** supplies and a cheap pattern or two.
- **Honored:** the big tier of patterns, plans, formulas and designs, plus the first gear.
- **Revered:** the faction's blues (on Sha'tar's shelf, a piece for every armour type) and its better recipes.
- **Exalted:** a handful of signature epics in the faction's own colours, plus its best recipes. Cenarion Expedition's Earthwarden, a feral tank's maul, cost 265g. Ashyen's Gift (a ring) and Windcaller's Orb (an off-hand) were 79g each. The Sha'tar had the Gavel of Pure Light.

Rep-sold patterns were sold only by the faction.

## What each shelf holds

- **Friendly and honored:** the faction's own supplies (added to what the Codex, the Ashclaim and the Reclamation already stocked).
- **Honored and revered:** two patterns at each, moved off every town shelf (39 patterns; the Reclamation's revered tier also takes the five Sunheart patterns).
- **Revered:** 6 blues. Item level 67, worn at 60, 44-74g.
- **Exalted:** 3 epics (item level 73, worn at 60, 250-350g), plus 2 recipes that craft item level 73 epics.

### Where the stats come from

- Stats come from the crafted-gear identities in `tools/build_crafted_gear.py`, with the same audit.
- A caster's piece leads with spell power, a fighter's with attack power, and a tank's with Stamina.
- No piece has a stat too small to matter.
- Rings, necks, trinkets and non-shield weapons no longer pick up stray bonus armour. This also cleared a few jewelcrafted necks.

### Where it's sold

- The new gear is in `data/items/faction_rewards.json` and sold as `unique:<id>`.
- Quartermasters already existed for the Codex, Orgrimmar, the Forsaken, Thunder Bluff (Camp Taurajo), the Ashclaim and the Reclamation.
- Three are new:
  - Quartermaster Zen'tabra, Echo Isles (Darkspear).
  - Cartel Quartermaster Fizzwhistle, Ratchet (Steamwheedle).
  - Port Quartermaster Sprocka, Booty Bay.
- The Reclamation's patterns sit with its Timbermaw trader.

### Exalted recipe ingredients

- The exalted recipes use each trade's top materials, doubled, as a stand-in for the rare ingredients Kyle wants.
- Each one carries `_rare_ingredients_todo: true`, so they're easy to find later.

## A direction, not a cage (Kyle, 15 Nov: "DONT tunnel people... Don't pigeon hole!!!")

- **Every faction serves everyone.** Its 11 pieces (6 blues, 3 epics, 2 crafted) cover tanks, healers, casters and fighters, across the armour types.
- **The faction shows in the name and the look, not in who can use it.** The Codex is arcanists, but it also sells a bastion warden's tank belt, a lamplighter's rogue boots, a spellbreaker's blade and a tank cloak.
- **Spell power is general.** Only two pieces in the whole set are one school, as deliberate exceptions:
  - the Ashclaim's Firebrand Scepter (fire), for its Dark Iron fire-priests;
  - Thunder Bluff's Totem of the Lost Spires (nature), a shaman's relic.
- **Renamed to match:**
  - Kang'ari's Hexing Staff is now Kang'ari's Spirit Staff (a healer's).
  - The Farseer's Chain Hauberk recipe is now Wolf-Rider's Chain Hauberk (a hunter's).
- **`tools/qa_faction_rewards.py` holds both rules:** every faction serves all four roles, and single-school pieces stay exceptions.

## The items

### The Crimson Codex  (quartermaster `kb_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Archivist's Cowl | cloth head | caster | 62g |
| Revered (blue) | Codex-Bound Gloves | cloth hands | caster (spell hit) | 48g |
| Revered (blue) | Marginalia of the Deep | tome off_hand | healer | 58g |
| Revered (blue) | Bastion Warden's Girdle | plate waist | tank | 52g |
| Revered (blue) | Lamplighter's Boots | leather feet | agility melee (crit) | 50g |
| Revered (blue) | Signet of the Find |  ring | strength melee (hit) | 55g |
| Exalted (epic) | Staff of the Hanging Light | staff main_hand | caster (crit) | 335g |
| Exalted (epic) | Crimson Spellblade | sword_1h main_hand | agility melee (crit) | 295g |
| Exalted (epic) | Cloak of the Long Descent | cloth back | tank | 255g |
| Exalted (recipe, tailoring) | Duskwaking Archivist's Robe | cloth chest | caster (crit) | crafted |
| Exalted (recipe, jewelcrafting) | Pendant of the Hanging Light |  neck | healer | crafted |

Patterns moved here: honored ench_weapon_spellsurge, ench_gloves_superior_battlemage; revered ench_weapon_major_spell_power, ench_2h_major_spell_power.

### Orgrimmar  (quartermaster `orgrimmar_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Grunt's Warhelm | plate head | strength melee | 64g |
| Revered (blue) | Kor'kron Shoulderguards | plate shoulder | tank | 60g |
| Revered (blue) | Farseer's Mail Vest | mail chest | caster (mail) | 70g |
| Revered (blue) | Wolfrider's Leggings | leather legs | agility melee | 62g |
| Revered (blue) | Spiritwalker's Bracers | mail wrist | healer (mp5) | 46g |
| Revered (blue) | Band of the Red Stone |  ring | caster (crit, Stamina) | 55g |
| Exalted (epic) | Warchief's Due | axe_2h main_hand | strength melee (crit) | 345g |
| Exalted (epic) | Bulwark of the Valley | shield off_hand | shield tank | 285g |
| Exalted (epic) | Farseer's Ancestral Mace | mace_1h main_hand | healer (mp5) | 290g |
| Exalted (recipe, blacksmithing) | Kor'kron Warplate | plate chest | strength melee (crit) | crafted |
| Exalted (recipe, leatherworking) | Wolf-Rider's Chain Hauberk | mail chest | hunter | crafted |

Patterns moved here: honored bs300_bloodiron_legs, ench_weapon_superior_strength; revered ench_2h_major_valor, ench_weapon_major_valor.

### The Darkspear Tribe  (quartermaster `ds_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Headhunter's Mask | leather head | agility melee | 60g |
| Revered (blue) | Hexer's Robe | cloth chest | caster | 68g |
| Revered (blue) | Bonecharm Necklace |  neck | healer | 52g |
| Revered (blue) | Tidewalker Waders | mail feet | hunter | 54g |
| Revered (blue) | Shadow Hunter's Bracers | leather wrist | agility / Intellect hybrid | 46g |
| Revered (blue) | Spearguard Girdle | plate waist | tank | 54g |
| Exalted (epic) | Spear of the Last Island | polearm main_hand | agility melee | 335g |
| Exalted (epic) | Kang'ari's Spirit Staff | staff main_hand | healer | 325g |
| Exalted (epic) | Sen'jin's Throwing Axes | thrown ranged | hunter (crit) | 260g |
| Exalted (recipe, tailoring) | Hexweaver's Robe | cloth chest | caster (spell hit) | crafted |
| Exalted (recipe, leatherworking) | Shadow Hunter's Vest | leather chest | agility / Intellect hybrid | crafted |

Patterns moved here: honored cookx_bloodspice_steak, ench_bracer_superior_wildheart; revered ench_weapon_major_wildheart, ench_2h_major_wildheart.

### The Forsaken  (quartermaster `uc_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Apothecary's Gloves | cloth hands | caster | 48g |
| Revered (blue) | Deathstalker's Hood | leather head | agility melee (crit) | 60g |
| Revered (blue) | Dark Ranger's Spaulders | mail shoulder | hunter (hit) | 60g |
| Revered (blue) | Deathguard Legplates | plate legs | tank | 72g |
| Revered (blue) | Grave-Cold Band |  ring | strength melee (crit) | 55g |
| Revered (blue) | Shroud of the Wakened | cloth back | healer | 50g |
| Exalted (epic) | Banshee's Lament | bow ranged | hunter (crit) | 300g |
| Exalted (epic) | Blade of the Wakened | dagger main_hand | agility melee (crit) | 290g |
| Exalted (epic) | Plaguebearer's Staff | staff main_hand | caster (spell pen) | 330g |
| Exalted (recipe, tailoring) | Deathwhisper Cowl | cloth head | caster | crafted |
| Exalted (recipe, leatherworking) | Deathstalker's Leggings | leather legs | agility melee (crit) | crafted |

Patterns moved here: honored lw_undercity_shade_vest, alch_transmute_iron_gold_vendor; revered alch_transmute_arcanite, ench_cloak_major_warding.

### The Steamwheedle Cartel  (quartermaster `ratchet_cartel_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Cartel Bruiser's Gauntlets | plate hands | strength melee | 54g |
| Revered (blue) | Contractor's Belt | leather waist | agility melee | 50g |
| Revered (blue) | Wharf Inspector's Coat | mail chest | hunter | 68g |
| Revered (blue) | Neutral Ground Mantle | cloth shoulder | caster | 56g |
| Revered (blue) | Tidepaid Ring |  ring | healer | 55g |
| Revered (blue) | Harbourmaster's Slippers | cloth feet | healer (Spirit) | 48g |
| Exalted (epic) | Profit Margin | dagger main_hand | agility melee (crit) | 285g |
| Exalted (epic) | The Neutrality Clause | shield off_hand | shield tank | 280g |
| Exalted (epic) | Cartel Arbiter's Cloak | cloth back | caster | 250g |
| Exalted (recipe, engineering) | Cartel Arbitrator's Goggles | mail head | hunter (crit) | crafted |
| Exalted (recipe, engineering) | Steamwheedle Hand Cannon | gun ranged | hunter (hit) | crafted |

Patterns moved here: honored engx_scope_thorium, cookx_keg_braised_shank; revered alch_flask_black_lotus, ench_boots_major_vigor.

### Thunder Bluff  (quartermaster `taurajo_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Spireborn Headdress | leather head | healer | 62g |
| Revered (blue) | Plainsrunner's Leggings | mail legs | hunter | 70g |
| Revered (blue) | Taurajo Bulwark Girdle | plate waist | tank | 52g |
| Revered (blue) | Windhoof Bracers | leather wrist | feral / agility | 46g |
| Revered (blue) | Earthmother's Mantle | mail shoulder | caster (mail) | 58g |
| Revered (blue) | Totem of the Lost Spires | totem ranged | shaman, nature (exception) | 52g |
| Exalted (epic) | Spire-Warden's Staff | staff main_hand | bear / beetle tank | 340g |
| Exalted (epic) | Mulgore Greatbow | bow ranged | hunter (hit) | 295g |
| Exalted (epic) | Cloak of the Fallen Spires | cloth back | healer | 255g |
| Exalted (recipe, leatherworking) | Bloodhoof Warhide Leggings | leather legs | bear / beetle tank | crafted |
| Exalted (recipe, woodworking) | Totem of the Four Spires | totem ranged | healer (mp5) | crafted |

Patterns moved here: honored lw_rugged_int_vest, ench_bracer_superior_mana_regeneration; revered ench_weapon_major_stormcaller, ench_boots_major_stormcaller.

### The Booty Bay Port Authority  (quartermaster `bootybay_port_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Harbour Guard's Helm | plate head | tank | 64g |
| Revered (blue) | Corsair-Hunter's Vest | leather chest | agility melee (crit) | 68g |
| Revered (blue) | Navigator's Belt | mail waist | healer (mp5) | 50g |
| Revered (blue) | Baron's Silk Waistcoat | cloth chest | caster | 70g |
| Revered (blue) | Tide-Reader's Gloves | cloth hands | healer | 48g |
| Revered (blue) | Cannoneer's Ring |  ring | hunter (crit) | 55g |
| Exalted (epic) | Revilgaz's Cutlass | sword_1h main_hand | agility melee (crit) | 300g |
| Exalted (epic) | Port Authority Blunderbuss | gun ranged | hunter (hit) | 290g |
| Exalted (epic) | Cloak of the Deep Harbour | cloth back | caster | 250g |
| Exalted (recipe, tailoring) | Navigator's Silk Mantle | cloth shoulder | caster (crit) | crafted |
| Exalted (recipe, blacksmithing) | Harbour Guard's Greathelm | plate head | tank | crafted |

Patterns moved here: honored fishx_mightfish_steak, fishx_nightfin_soup; revered jc_cut_sparkling_azure_diamond, jc_cut_delicate_black_diamond.

### The Ashclaim  (quartermaster `cw_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Ashhold Forgeguard Breastplate | plate chest | tank | 74g |
| Revered (blue) | Cinderwharf Rigger's Gloves | leather hands | agility melee | 48g |
| Revered (blue) | Scoria-Plated Pauldrons | mail shoulder | strength / Intellect hybrid | 60g |
| Revered (blue) | Pyremonger's Hood | cloth head | caster | 62g |
| Revered (blue) | Deed-Holder's Signet |  ring | strength melee | 55g |
| Revered (blue) | Ashpriest's Bindings | cloth wrist | healer | 44g |
| Exalted (epic) | Thane's Claim | mace_2h main_hand | strength melee | 350g |
| Exalted (epic) | Firebrand Scepter | mace_1h main_hand | fire caster (exception) | 295g |
| Exalted (epic) | Khaz Varun Deedstone |  neck | tank | 265g |
| Exalted (recipe, blacksmithing) | Ashhold Claimant's Warplate | plate chest | strength melee (crit) | crafted |
| Exalted (recipe, engineering) | Khaz Varun Siege Rifle | gun ranged | hunter (crit) | crafted |

Patterns moved here: honored bs300_truesilver_wrist, bs300_kit_ashen_steel; revered bs_runed_arcanite_rod, jc_cut_etched_cinder_agate.

### The Emerald Reclamation  (quartermaster `es_quartermaster`)

| Standing | Item | Slot | For | Price |
|---|---|---|---|---|
| Revered (blue) | Sentinel's Glaivebelt | leather waist | agility melee | 50g |
| Revered (blue) | Timbermaw Hide Leggings | leather legs | bear / beetle tank | 66g |
| Revered (blue) | Grovewarden's Robe | cloth chest | healer | 70g |
| Revered (blue) | Reclaimer's Hauberk | mail chest | hunter (hit) | 70g |
| Revered (blue) | Treant-Bark Wristguards | plate wrist | tank | 46g |
| Revered (blue) | Moonwell Pendant |  neck | caster | 52g |
| Exalted (epic) | Moonbough's Gift |  ring | healer | 255g |
| Exalted (epic) | Glaive of the Fel Line | polearm main_hand | agility melee | 330g |
| Exalted (epic) | Windcaller's Bough | tome off_hand | caster | 270g |
| Exalted (recipe, woodworking) | Reclaimer's Living Staff | staff main_hand | healer | crafted |
| Exalted (recipe, leatherworking) | Timbermaw Ancestor Hide | leather chest | feral / agility | crafted |

Patterns moved here: honored wwx_starleaf_moon_idol, ench_weapon_major_healing; revered wwx_blessed_sunheart_codex, wwx_sunheart_tideguard, wwx_sunheart_staff, wwx_blessed_sunheart_staff, wwx_sunheart_bow.

## Epic icons: 45 to draw (sheets R1 and R2)

Every exalted epic, sold or crafted, uses the shared epic stand-ins until its own art lands.

1. Slice each sheet into `assets/icons/gear/gear_epic_crafted_<name>.png`, where `<name>` is the item name in lower case with each run of spaces or punctuation replaced by `_`. For example, `Warchief's Due` becomes `gear_epic_crafted_warchief_s_due.png`.
2. Re-run `tools/build_faction_rewards.py` and then `tools/build_crafted_gear.py`, which pick the new art up.

Each faction's pieces share one look:
- **Codex:** blood-elf crimson and gold, with pale crystal light.
- **Orgrimmar:** red iron with black leather and wolf-tooth charms.
- **Darkspear:** carved wood and bone, with teal voodoo glow.
- **Forsaken:** grey-black and silver, with sickly green vials.
- **Steamwheedle:** brass, rivets, a ledger motif and green goblin trim.
- **Thunder Bluff:** kodo hide, carved totem wood and eagle feathers.
- **Booty Bay:** sea-blue, brass and salt-stained rope.
- **Ashclaim:** Dark Iron, black and ember-orange, with volcanic glass.
- **Reclamation:** living green wood, moonstone and Timbermaw fur.

### Sheet R1 (7 x 4 = 28)

```
Generate ONE sprite sheet image, 1536x1024, a 7 columns x 4 rows grid = 28 separate game icons (each cell about 219x256). Flat pure #FF00FF magenta background everywhere. Each icon is ONE single object, centred in its own cell with a WIDE empty margin on every side: nothing touches a neighbour or the image edge. Painterly semi-realistic WoW Classic inventory-icon style for EPIC (purple-quality) faction rewards: rich materials, ornate trim, a faint glow, strong readable silhouette, soft dark outline, lighting from the top-left, slight 3/4 view. No hands, no bodies, no text, no labels, no grid lines, no frames, no borders. No magenta or pink inside any icon. Row by row, left to right:

Row 1 - CRIMSON CODEX (blood-elf crimson and gold, pale crystal light) and ORGRIMMAR (red iron, black leather, wolf-tooth charms):
1. STAFF OF THE HANGING LIGHT: a slender gold-and-crimson staff whose head cradles a floating shard of pale crystal light
2. CRIMSON SPELLBLADE: a one-handed elven sword with a crimson blade etched in gold runes, a phoenix-wing crossguard
3. CLOAK OF THE LONG DESCENT: a deep crimson cloak lined with starless black, a gold clasp with a tiny lamp
4. WARCHIEF'S DUE: a huge two-handed orcish axe of red iron, black-wrapped haft, wolf teeth hanging from the beard
5. BULWARK OF THE VALLEY: a round orcish shield of red iron and timber, painted with a canyon and a rising sun, spiked rim
6. FARSEER'S ANCESTRAL MACE: a one-handed mace with a carved stone head, blue spirit glow, feathers and wolf-tooth charms
7. DUSKWAKING ARCHIVIST'S ROBE: a long crimson and gold scholar's robe with ink-blue cuffs and a crystal at the collar

Row 2 - ORGRIMMAR crafted, DARKSPEAR (carved wood, bone, teal voodoo glow):
8. KOR'KRON WARPLATE: a heavy black-iron breastplate with red leather straps and tusk-shaped pauldron mounts
9. WOLF-RIDER'S CHAIN HAUBERK: a red-iron mail hauberk with wolf-fur at the collar and a leather bow strap across it
10. SPEAR OF THE LAST ISLAND: a long troll spear of pale driftwood with a bone-and-flint head and teal feathers
11. KANG'ARI'S SPIRIT STAFF: a crooked wooden staff topped with a carved voodoo mask, soft teal spirit-light and hanging fetishes
12. SEN'JIN'S THROWING AXES: a matched pair of crossed troll throwing axes with bone handles and teal-painted blades
13. HEXWEAVER'S ROBE: a troll robe of rough woven cloth hung with little bone charms, teal voodoo patterns glowing faintly
14. SHADOW HUNTER'S VEST: a leather vest painted with tribal marks, a carved bone clasp, purple-teal shadow wisps

Row 3 - FORSAKEN (grey-black and silver, sickly green vials) and STEAMWHEEDLE (brass, rivets, ledger motif, green goblin trim):
15. BANSHEE'S LAMENT: a dark ranger's black-and-silver longbow, a pale ghostly string with a faint wail-mist
16. BLADE OF THE WAKENED: a long grey dagger with a skull pommel and a faint green edge
17. PLAGUEBEARER'S STAFF: a tall black staff topped with a sealed glass vial of glowing green plague in silver claws
18. DEATHWHISPER COWL: a deep grey hood with silver trim whose opening is shadow with two green glints
19. DEATHSTALKER'S LEGGINGS: close-fitting grey-black leather leggings with silver buckles at the knee
20. PROFIT MARGIN: a thin goblin dagger with a brass knuckle-guard and a gold coin set in the pommel
21. THE NEUTRALITY CLAUSE: a goblin tower shield of riveted brass, half painted Horde red and half Alliance blue

Row 4 - STEAMWHEEDLE, THUNDER BLUFF (kodo hide, carved totem wood, eagle feathers) and BOOTY BAY (sea-blue, brass, salt-stained rope):
22. CARTEL ARBITER'S CLOAK: a long green goblin coat-cloak with brass buttons and a coin-shaped clasp
23. CARTEL ARBITRATOR'S GOGGLES: brass goggles with twelve stacked lenses, a little readout dial and a shutter
24. STEAMWHEEDLE HAND CANNON: an oversized brass hand cannon with a flared muzzle, a wooden grip and a goblin crest
25. SPIRE-WARDEN'S STAFF: a thick tauren fighting staff of dark wood, banded with bark guards, carved with four spires
26. MULGORE GREATBOW: a huge tauren longbow of pale wood wrapped in kodo hide, eagle feathers at the tips
27. CLOAK OF THE FALLEN SPIRES: a woven tauren cloak with a border of four spires and the earth missing beneath them
28. BLOODHOOF WARHIDE LEGGINGS: heavy kodo-hide leggings with fur at the knee and carved bone toggles
```

### Sheet R2 (7 x 3 = 21; the last 4 cells empty)

```
Generate ONE sprite sheet image, 1536x768, a 7 columns x 3 rows grid; the last FOUR cells of row 3 are left EMPTY magenta, so 17 separate game icons (each cell about 219x256). Flat pure #FF00FF magenta background everywhere. Same rules and style as sheet R1. Row by row, left to right:

Row 1 - THUNDER BLUFF, BOOTY BAY (sea-blue, brass, salt-stained rope):
1. TOTEM OF THE FOUR SPIRES: a carved tauren totem with four spires, one cracked off at the base, soft blue water glow
2. REVILGAZ'S CUTLASS: a curved goblin cutlass with a brass basket hilt and a sea-blue gem
3. PORT AUTHORITY BLUNDERBUSS: a flared brass blunderbuss stamped with an anchor crest, rope-wrapped stock
4. CLOAK OF THE DEEP HARBOUR: a heavy sea-blue cloak crusted with salt at the hem, an anchor clasp
5. NAVIGATOR'S SILK MANTLE: a pair of sea-silk shoulder mantles embroidered with a chart of the bay, frosty blue glow
6. HARBOUR GUARD'S GREATHELM: a full plate greathelm with an anchor crest on the brow, brass rivets and a sea-blue plume
7. THANE'S CLAIM: a massive Dark Iron two-handed warhammer, black with ember-orange cracks, a deed scroll engraved on the haft

Row 2 - ASHCLAIM (Dark Iron, black and ember-orange, volcanic glass) and EMERALD RECLAMATION (living green wood, moonstone, Timbermaw fur):
8. FIREBRAND SCEPTER: a one-handed scepter of scoria and Dark Iron with a glowing ember-orange head
9. KHAZ VARUN DEEDSTONE: a necklace with a chip of carved black gate-stone set in Dark Iron, ember glow in the cracks
10. ASHHOLD CLAIMANT'S WARPLATE: a heavy Dark Iron breastplate with ember-orange seams and a gate sigil
11. KHAZ VARUN SIEGE RIFLE: a long, heavy Dark Iron rifle cut down from a siege piece, glowing ember vents
12. MOONBOUGH'S GIFT: a ring of living green wood grown around a pale moonstone, a tiny leaf sprouting
13. GLAIVE OF THE FEL LINE: a night elf war glaive, crescent blades of moonsilver on a green-wood haft
14. WINDCALLER'S BOUGH: a book with covers of living wood, leaves growing from the spine, faint green light

Row 3 - EMERALD RECLAMATION (crafted):
15. RECLAIMER'S LIVING STAFF: a tall staff of living green wood still putting out leaves and a single white flower
16. TIMBERMAW ANCESTOR HIDE: a heavy leather chest of old Timbermaw fur with carved wooden toggles and green bead strands
17. PENDANT OF THE HANGING LIGHT: a crimson-and-gold pendant holding a sliver of pale crystal that glows
(cells 18-21 empty)
```
