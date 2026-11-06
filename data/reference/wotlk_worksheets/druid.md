# Druid - real WotLK 3.3.5a reference vs ours

- WotLK talents: **85** across 3 trees
- already in our data by name: **67** (of those, **41** are pure scalars on our side)
- not in our data at all: **18**
- carry real-time assumptions needing translation: **27** (32%)
- ask for a mechanic this engine does not have: **7**

Source: the game's own `Spell.dbc`, via github.com/atosfr/WotLK-3.3.5-Talent-Calculator (`Talents.json` + `TalentDescriptions.json`). Slot counts independently cross-checked against the rendered wowtbc.gg calculator - all six checkable trees match.

`MATCH` - we already have a talent of this name. `scalar` means ours is a pure numeric bonus, which is the thing being replaced. `needs` lists the engine mechanic the real talent wants. **BLOCKED** means this engine has no way to express it, so that talent needs a substitute mechanic rather than a literal port - never a tooltip the engine cannot honour.

WotLK rows 0-10 map onto Frontier's SEVEN tiers (0-6, tier_requirements 0/5/10/15/20/25/30) as `tier = round(row * 6 / 10)`, so rows go 0/1/1/2/2/3/4/4/5/5/6 and the WotLK capstone row sits alone at tier 6. **Numbers are not ported**: WotLK assumes 80 levels, raid fights and real seconds; Frontier caps at 60 and fights run 2-3 turns on trash, 5-6 on a boss.


## Balance - 28 talents, 75 points

- **Starlight Wrath** (5 ranks) - row 0 -> tier 0 - MATCH druid_balance_starlight_wrath  [ours is scalar]
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the cast time of your Wrath and Starfire spells by 0.1 sec.
  - WotLK rank 5: Reduces the cast time of your Wrath and Starfire spells by 0.5 sec.
- **Genesis** (5 ranks) - row 0 -> tier 0 - MATCH druid_balance_genesis  [ours is scalar]
  - needs: heal
  - WotLK rank 1: Increases the damage and healing done by your periodic spell damage and healing effects by 1%.
  - WotLK rank 5: Increases the damage and healing done by your periodic spell damage and healing effects by 5%.
- **Moonglow** (3 ranks) - row 1 -> tier 1 - MATCH druid_balance_moonglow  [ours is scalar]
  - needs: cost-change, heal
  - WotLK rank 1: Reduces the Mana cost of your Moonfire, Starfire, Starfall, Wrath, Healing Touch, Nourish, Regrowth and Rejuvenation spells by 3%.
  - WotLK rank 3: Reduces the Mana cost of your Moonfire, Starfire, Starfall, Wrath, Healing Touch, Nourish, Regrowth and Rejuvenation spells by 9%.
- **Nature's Majesty** (2 ranks) - row 1 -> tier 1 - MATCH druid_balance_natures_majesty  [ours is scalar]
  - needs: proc-chance, crit, heal
  - WotLK rank 1: Increases the critical strike chance of your Wrath, Starfire, Starfall, Nourish and Healing Touch spells by 2%.
  - WotLK rank 2: Increases the critical strike chance of your Wrath, Starfire, Starfall, Nourish and Healing Touch spells by 4%.
- **Improved Moonfire** (2 ranks) - row 1 -> tier 1 - MATCH druid_balance_improved_moonfire  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases the damage and critical strike chance of your Moonfire spell by 5%.
  - WotLK rank 2: Increases the damage and critical strike chance of your Moonfire spell by 10%.
- **Brambles** (3 ranks) - row 2 -> tier 1 - MATCH druid_balance_brambles
  - needs: proc-chance, duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Damage from your Thorns and Entangling Roots increased by 25% and damage done by your Treants increased by 5%. In addition, damage from your Treants and attacks done to you while you have Barkskin active have a 5% chance to daze the target for 3 sec.
  - WotLK rank 3: Damage from your Thorns and Entangling Roots increased by 75% and damage done by your Treants increased by 15%. In addition, damage from your Treants and attacks done to you while you have Barkskin active have a 15% chance to daze the target for 3 sec.
- **Nature's Grace** (3 ranks) - row 2 -> tier 1 - MATCH druid_balance_natures_grace
  - requires: Nature's Majesty
  - needs: proc-chance, duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: All non-periodic spell criticals have a 33% chance to grace you with a blessing of nature, increasing your spell casting speed by 20% for 3 sec.
  - WotLK rank 3: All non-periodic spell criticals have a 100% chance to grace you with a blessing of nature, increasing your spell casting speed by 20% for 3 sec.
- **Nature's Splendor** (1 rank) - row 2 -> tier 1 - NEW - we have no talent of this name
  - requires: Nature's Majesty
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the duration of your Moonfire and Rejuvenation spells by 3 sec, your Regrowth spell by 6 sec, and your Insect Swarm and Lifebloom spells by 2 sec.
- **Nature's Reach** (2 ranks) - row 2 -> tier 1 - MATCH druid_balance_natures_reach  [ours is scalar]
  - needs: threat
  - WotLK rank 1: Increases the range of your Balance spells and Faerie Fire (Feral) ability by 10%, and reduces the threat generated by your Balance spells by 15%.
  - WotLK rank 2: Increases the range of your Balance spells and Faerie Fire (Feral) ability by 20%, and reduces the threat generated by your Balance spells by 30%.
- **Vengeance** (5 ranks) - row 3 -> tier 2 - MATCH druid_balance_vengeance  [ours is scalar]
  - needs: crit
  - WotLK rank 1: Increases the critical strike damage bonus of your Starfire, Starfall, Moonfire, and Wrath spells by 20%.
  - WotLK rank 5: Increases the critical strike damage bonus of your Starfire, Starfall, Moonfire, and Wrath spells by 100%.
- **Celestial Focus** (3 ranks) - row 3 -> tier 2 - MATCH druid_balance_celestial_focus  [ours is scalar]
  - WotLK rank 1: Reduces the pushback suffered from damaging attacks while casting Starfire, Hibernate and Hurricane by 23% and increases your total spell haste by 1%.
  - WotLK rank 3: Reduces the pushback suffered from damaging attacks while casting Starfire, Hibernate and Hurricane by 70% and increases your total spell haste by 3%.
- **Lunar Guidance** (3 ranks) - row 4 -> tier 2 - MATCH druid_balance_lunar_guidance  [ours is scalar]
  - WotLK rank 1: Increases your spell power by 4% of your total Intellect.
  - WotLK rank 3: Increases your spell power by 12% of your total Intellect.
- **Insect Swarm** (1 rank) - row 4 -> tier 2 - MATCH druid_balance_insect_swarm
  - needs: proc-chance, dot-hot
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: The enemy target is swarmed by insects, decreasing their chance to hit by 3% and causing 144 Nature damage over 12 sec.
- **Improved Insect Swarm** (3 ranks) - row 4 -> tier 2 - NEW - we have no talent of this name
  - requires: Insect Swarm
  - needs: proc-chance, crit
  - WotLK rank 1: Increases your damage done by your Wrath spell to targets afflicted by your Insect Swarm by 1%, and increases the critical strike chance of your Starfire spell by 1% on targets afflicted by your Moonfire spell.
  - WotLK rank 3: Increases your damage done by your Wrath spell to targets afflicted by your Insect Swarm by 3%, and increases the critical strike chance of your Starfire spell by 3% on targets afflicted by your Moonfire spell.
- **Dreamstate** (3 ranks) - row 5 -> tier 3 - MATCH druid_balance_dreamstate
  - needs: dot-hot
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Regenerate mana equal to 4% of your Intellect every 5 sec, even while casting.
  - WotLK rank 3: Regenerate mana equal to 10% of your Intellect every 5 sec, even while casting.
- **Moonfury** (3 ranks) - row 5 -> tier 3 - MATCH druid_balance_moonfury  [ours is scalar]
  - WotLK rank 1: Increases the damage done by your Starfire, Moonfire and Wrath spells by 3%.
  - WotLK rank 3: Increases the damage done by your Starfire, Moonfire and Wrath spells by 10%.
- **Balance of Power** (2 ranks) - row 5 -> tier 3 - MATCH druid_balance_balance_of_power  [ours is scalar]
  - needs: proc-chance
  - WotLK rank 1: Increases your chance to hit with all spells by 2% and reduces your damage taken from all spells by 3%.
  - WotLK rank 2: Increases your chance to hit with all spells by 4% and reduces your damage taken from all spells by 6%.
- **Moonkin Form** (1 rank) - row 6 -> tier 4 - MATCH druid_balance_moonkin_form
  - needs: proc-chance, crit, heal, stun, aoe
  - WotLK rank 1: Shapeshift into Moonkin Form. While in this form the armor contribution from items is increased by 370%, damage taken while stunned is reduced by 15%, and all party and raid members within 100 yards have their spell critical chance increased by 5%. Single target spell critical strikes in this form have a chance to instantly regenerate 2% of your total mana. The Moonkin can not cast healing or resurrection spells while shapeshifted.

The act of shapeshifting frees the caster of Polymorph and Movement Impairing effects.
- **Improved Moonkin Form** (3 ranks) - row 6 -> tier 4 - NEW - we have no talent of this name
  - requires: Moonkin Form
  - WotLK rank 1: Your Moonkin Aura also causes affected targets to gain 1% haste and you to gain 10% of your spirit as additional spell damage.
  - WotLK rank 3: Your Moonkin Aura also causes affected targets to gain 3% haste and you to gain 30% of your spirit as additional spell damage.
- **Improved Faerie Fire** (3 ranks) - row 6 -> tier 4 - NEW - we have no talent of this name
  - needs: proc-chance, crit
  - WotLK rank 1: Your Faerie Fire spell also increases the chance the target will be hit by spell attacks by 1%, and increases the critical strike chance of your damage spells by 1% on targets afflicted by Faerie Fire.
  - WotLK rank 3: Your Faerie Fire spell also increases the chance the target will be hit by spell attacks by 3%, and increases the critical strike chance of your damage spells by 3% on targets afflicted by Faerie Fire.
- **Owlkin Frenzy** (3 ranks) - row 7 -> tier 4 - MATCH druid_balance_owlkin_frenzy
  - requires: Moonkin Form
  - needs: proc-chance, resource-grant, dot-hot
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Attacks done to you while in Moonkin form have a 5% chance to cause you to go into a Frenzy, increasing your damage by 10%, cause you to be immune to pushback while casting Balance spells and restore 2% base mana every 2 sec. Lasts 10 sec.
  - WotLK rank 3: Attacks done to you while in Moonkin form have a 15% chance to cause you to go into a Frenzy, increasing your damage by 10%, cause you to be immune to pushback while casting Balance spells and restore 2% base mana every 2 sec. Lasts 10 sec.
- **Wrath of Cenarius** (5 ranks) - row 7 -> tier 4 - MATCH druid_balance_wrath_of_cenarius  [ours is scalar]
  - WotLK rank 1: Your Starfire spell gains an additional 4% and your Wrath gains an additional 2% of your bonus damage effects.
  - WotLK rank 5: Your Starfire spell gains an additional 20% and your Wrath gains an additional 10% of your bonus damage effects.
- **Eclipse** (3 ranks) - row 8 -> tier 5 - MATCH druid_balance_eclipse
  - needs: proc-chance, cooldown-change, crit
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When you critically hit with Starfire, you have a 33% chance of increasing damage done by Wrath by 40%. When you critically hit with Wrath, you have a 20% chance of increasing your critical strike chance with Starfire by 40%. Each effect lasts 15 sec and each has a separate 30 sec cooldown.  Both effects cannot occur simultaneously.
  - WotLK rank 3: When you critically hit with Starfire, you have a 100% chance of increasing damage done by Wrath by 40%. When you critically hit with Wrath, you have a 60% chance of increasing your critical strike chance with Starfire by 40%. Each effect lasts 15 sec and each has a separate 30 sec cooldown.  Both effects cannot occur simultaneously.
- **Typhoon** (1 rank) - row 8 -> tier 5 - MATCH druid_balance_balance_mastery
  - requires: Moonkin Form
  - needs: duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: You summon a violent Typhoon that does 400 Nature damage when in contact with hostile targets, knocking them back and dazing them for 6 sec.
- **Force of Nature** (1 rank) - row 8 -> tier 5 - NEW - we have no talent of this name
  - needs: duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Summons 3 treants to attack enemy targets for 30 sec.
- **Gale Winds** (2 ranks) - row 8 -> tier 5 - MATCH druid_balance_gale_winds  [ours is scalar]
  - WotLK rank 1: Increases damage done by your Hurricane and Typhoon spells by 15%, and increases the range of your Cyclone spell by 2 yards.
  - WotLK rank 2: Increases damage done by your Hurricane and Typhoon spells by 30%, and increases the range of your Cyclone spell by 4 yards.
- **Earth and Moon** (3 ranks) - row 9 -> tier 5 - MATCH druid_balance_earth_and_moon
  - needs: proc-chance, duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your Wrath and Starfire spells have a 100% chance to apply the Earth and Moon effect, which increases spell damage taken by 4% for 12 sec.  Also increases your spell damage by 2%.
  - WotLK rank 3: Your Wrath and Starfire spells have a 100% chance to apply the Earth and Moon effect, which increases spell damage taken by 13% for 12 sec.  Also increases your spell damage by 6%.
- **Starfall** (1 rank) - row 10 -> tier 6 - MATCH druid_balance_starfall
  - needs: aoe
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: You summon a flurry of stars from the sky on all targets within 30 yards of the caster, each dealing 145 to 167 Arcane damage. Also causes 26 Arcane damage to all other enemies within 5 yards of the enemy target. Maximum 20 stars. Lasts 10 sec.  Shapeshifting into an animal form or mounting cancels the effect. Any effect which causes you to lose control of your character will suppress the starfall effect.

## Feral Combat - 30 talents, 78 points

- **Ferocity** (5 ranks) - row 0 -> tier 0 - MATCH druid_feral_ferocity  [ours is scalar]
  - needs: cost-change
  - WotLK rank 1: Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 1 Rage or Energy.
  - WotLK rank 5: Reduces the cost of your Maul, Swipe, Claw, Rake and Mangle abilities by 5 Rage or Energy.
- **Feral Aggression** (5 ranks) - row 0 -> tier 0 - MATCH druid_feral_feral_aggression  [ours is scalar]
  - WotLK rank 1: Increases the attack power reduction of your Demoralizing Roar by 8% and the damage caused by your Ferocious Bite by 3%.
  - WotLK rank 5: Increases the attack power reduction of your Demoralizing Roar by 40% and the damage caused by your Ferocious Bite by 15%.
- **Feral Instinct** (3 ranks) - row 1 -> tier 1 - MATCH druid_feral_feral_instinct  [ours is scalar]
  - needs: proc-chance
  - **BLOCKED**: BLOCKED:stealth - needs a substitute mechanic
  - WotLK rank 1: Increases the damage done by your Swipe ability by 10% and reduces the chance enemies have to detect you while Prowling.
  - WotLK rank 3: Increases the damage done by your Swipe ability by 30% and reduces the chance enemies have to detect you while Prowling.
- **Savage Fury** (2 ranks) - row 1 -> tier 1 - MATCH druid_feral_savage_fury  [ours is scalar]
  - WotLK rank 1: Increases the damage caused by your Claw, Rake, Mangle (Cat), Mangle (Bear), and Maul abilities by 10%.
  - WotLK rank 2: Increases the damage caused by your Claw, Rake, Mangle (Cat), Mangle (Bear), and Maul abilities by 20%.
- **Thick Hide** (3 ranks) - row 1 -> tier 1 - MATCH druid_feral_thick_hide  [ours is scalar]
  - WotLK rank 1: Increases your Armor contribution from cloth and leather items by 4%.
  - WotLK rank 3: Increases your Armor contribution from cloth and leather items by 10%.
- **Feral Swiftness** (2 ranks) - row 2 -> tier 1 - NEW - we have no talent of this name
  - needs: proc-chance
  - WotLK rank 1: Increases your movement speed by 15% in Cat Form and increases your chance to dodge while in Cat Form, Bear Form and Dire Bear Form by 2%.
  - WotLK rank 2: Increases your movement speed by 30% in Cat Form and increases your chance to dodge while in Cat Form, Bear Form and Dire Bear Form by 4%.
- **Survival Instincs** (1 rank) - row 2 -> tier 1 - NEW - we have no talent of this name
  - needs: duration-window, heal
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When activated, this ability temporarily grants you 30% of your maximum health for 20 sec while in Bear Form, Cat Form, or Dire Bear Form. After the effect expires, the health is lost.
- **Sharpened Claws** (3 ranks) - row 2 -> tier 1 - MATCH druid_feral_sharpened_claws  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases your critical strike chance while in Bear, Dire Bear or Cat Form by 2%.
  - WotLK rank 3: Increases your critical strike chance while in Bear, Dire Bear or Cat Form by 6%.
- **Shredding Attacks** (2 ranks) - row 3 -> tier 2 - MATCH druid_feral_shredding_attacks  [ours is scalar]
  - needs: cost-change
  - WotLK rank 1: Reduces the energy cost of your Shred ability by 9 and the rage cost of your Lacerate ability by 1.
  - WotLK rank 2: Reduces the energy cost of your Shred ability by 18 and the rage cost of your Lacerate ability by 2.
- **Predatory Strikes** (3 ranks) - row 3 -> tier 2 - MATCH druid_feral_predatory_strikes
  - needs: proc-chance
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases your melee attack power in Cat, Bear and Dire Bear Forms by 50% of your level and 7% of any attack power on your equipped weapon.  In addition, your finishing moves have a 7% chance per combo point to make your next Nature spell with a base casting time less than 10 sec. become an instant cast spell.
  - WotLK rank 3: Increases your melee attack power in Cat, Bear and Dire Bear Forms by 150% of your level and 20% of any attack power on your equipped weapon.  In addition, your finishing moves have a 20% chance per combo point to make your next Nature spell with a base casting time less than 10 sec. become an instant cast spell.
- **Primal Fury** (2 ranks) - row 3 -> tier 2 - MATCH druid_feral_primal_fury
  - requires: Sharpened Claws
  - needs: proc-chance, crit
  - WotLK rank 1: Gives you a 50% chance to gain an additional 5 Rage anytime you get a critical strike while in Bear and Dire Bear Form and your critical strikes from Cat Form abilities that add combo points  have a 50% chance to add an additional combo point.
  - WotLK rank 2: Gives you a 100% chance to gain an additional 5 Rage anytime you get a critical strike while in Bear and Dire Bear Form and your critical strikes from Cat Form abilities that add combo points  have a 100% chance to add an additional combo point.
- **Primal Precision** (2 ranks) - row 3 -> tier 2 - NEW - we have no talent of this name
  - requires: Sharpened Claws
  - needs: cost-change
  - WotLK rank 1: Increases your expertise by 5, and you are refunded 40% of the energy cost of a finishing move if it fails to land.
  - WotLK rank 2: Increases your expertise by 10, and you are refunded 80% of the energy cost of a finishing move if it fails to land.
- **Brutal Impact** (2 ranks) - row 4 -> tier 2 - MATCH druid_feral_brutal_impact  [ours is scalar]
  - needs: cooldown-change, stun
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the stun duration of your Bash and Pounce abilities by 0.5 sec and decreases the cooldown of Bash by 15 sec.
  - WotLK rank 2: Increases the stun duration of your Bash and Pounce abilities by 1 sec and decreases the cooldown of Bash by 30 sec.
- **Feral Charge** (1 rank) - row 4 -> tier 2 - NEW - we have no talent of this name
  - needs: duration-window, cooldown-change
  - **BLOCKED**: BLOCKED:interrupt, BLOCKED:position, BLOCKED:charges - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Teaches Feral Charge (Bear) and Feral Charge (Cat).

Feral Charge (Bear) - Causes you to charge an enemy, immobilizing and interrupting any spell being cast for 4 sec. This ability can be used in Bear Form and Dire Bear Form. 15 second cooldown.

Feral Charge (Cat) - Causes you to leap behind an enemy, dazing them for 3 sec. 30 second cooldown.
- **Nurturing Instinct** (2 ranks) - row 4 -> tier 2 - MATCH druid_feral_nurturing_instinct  [ours is scalar]
  - needs: heal
  - WotLK rank 1: Increases your healing spells by up to 35% of your Agility, and increases healing done to you by 10% while in Cat form.
  - WotLK rank 2: Increases your healing spells by up to 70% of your Agility, and increases healing done to you by 20% while in Cat form.
- **Natural Reaction** (3 ranks) - row 5 -> tier 3 - MATCH druid_feral_natural_reaction
  - WotLK rank 1: Increases your dodge while in Bear Form or Dire Bear Form by 2%, and you regenerate 1 rage every time you dodge while in Bear Form or Dire Bear Form.
  - WotLK rank 3: Increases your dodge while in Bear Form or Dire Bear Form by 6%, and you regenerate 3 rage every time you dodge while in Bear Form or Dire Bear Form.
- **Heart of the Wild** (5 ranks) - row 5 -> tier 3 - MATCH druid_feral_heart_of_the_wild  [ours is scalar]
  - requires: Predatory Strikes
  - WotLK rank 1: Increases your Intellect by 4%.  In addition, while in Bear or Dire Bear Form your Stamina is increased by 2% and while in Cat Form your attack power is increased by 2%.
  - WotLK rank 5: Increases your Intellect by 20%.  In addition, while in Bear or Dire Bear Form your Stamina is increased by 10% and while in Cat Form your attack power is increased by 10%.
- **Survival of the Fittest** (3 ranks) - row 5 -> tier 3 - MATCH druid_feral_survival_of_the_fittest  [ours is scalar]
  - needs: proc-chance
  - WotLK rank 1: Increases all attributes by 2%, reduces the chance you'll be critically hit by melee attacks by 2%, and increases your armor contribution from cloth and leather items in Bear Form and Dire Bear Form by 11%.
  - WotLK rank 3: Increases all attributes by 6%, reduces the chance you'll be critically hit by melee attacks by 6%, and increases your armor contribution from cloth and leather items in Bear Form and Dire Bear Form by 33%.
- **Leader of the Pack** (1 rank) - row 6 -> tier 4 - MATCH druid_feral_leader_of_the_pack
  - needs: proc-chance, aoe
  - WotLK rank 1: While in Cat, Bear or Dire Bear Form, the Leader of the Pack increases ranged and melee critical chance of all party and raid members within 100 yards by 5%.
- **Improved Leader of the Pack** (2 ranks) - row 6 -> tier 4 - NEW - we have no talent of this name
  - requires: Leader of the Pack
  - needs: dot-hot, heal
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your Leader of the Pack ability also causes affected targets to heal themselves for 2% of their total health when they critically hit with a melee or ranged attack.  The healing effect cannot occur more than once every 6 sec.  In addition, you gain 4% of your maximum mana when you benefit from this heal.
  - WotLK rank 2: Your Leader of the Pack ability also causes affected targets to heal themselves for 4% of their total health when they critically hit with a melee or ranged attack.  The healing effect cannot occur more than once every 6 sec.  In addition, you gain 8% of your maximum mana when you benefit from this heal.
- **Primal Tenacity** (3 ranks) - row 6 -> tier 4 - NEW - we have no talent of this name
  - needs: stun
  - WotLK rank 1: Reduces the duration of fear effects by 10%, reduces all damage taken while stunned by 10% while in Cat Form.
  - WotLK rank 3: Reduces the duration of fear effects by 30%, reduces all damage taken while stunned by 30% while in Cat Form.
- **Protector of the Pack** (3 ranks) - row 7 -> tier 4 - MATCH druid_feral_protector_of_the_pack  [ours is scalar]
  - requires: Leader of the Pack
  - WotLK rank 1: Increases your attack power by 2% and reduces the damage you take by 4%, while in Bear or Dire Bear Form.
  - WotLK rank 3: Increases your attack power by 6% and reduces the damage you take by 12%, while in Bear or Dire Bear Form.
- **Predatory Instincts** (3 ranks) - row 7 -> tier 4 - MATCH druid_feral_feral_mastery
  - needs: crit
  - WotLK rank 1: While in Cat Form increases your damage from melee critical strikes by 3% and reduces the damage taken from area of effect attacks by 10%.
  - WotLK rank 3: While in Cat Form increases your damage from melee critical strikes by 10% and reduces the damage taken from area of effect attacks by 30%.
- **Infected Wounds** (3 ranks) - row 7 -> tier 4 - MATCH druid_feral_infected_wounds
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your Shred, Maul, and Mangle attacks cause an Infected Wound in the target. The Infected Wound reduces the movement speed of the target by 16% and the attack speed by 6%. Lasts 12 sec.
  - WotLK rank 3: Your Shred, Maul, and Mangle attacks cause an Infected Wound in the target. The Infected Wound reduces the movement speed of the target by 50% and the attack speed by 20%. Lasts 12 sec.
- **King of the Jungle** (3 ranks) - row 8 -> tier 5 - MATCH druid_feral_king_of_the_jungle
  - needs: resource-grant, cost-change
  - WotLK rank 1: While using your Enrage ability in Bear Form or Dire Bear Form, your damage is increased by 5%, and your Tiger's Fury ability also instantly restores 20 energy.  In addition, the mana cost of Bear Form, Cat Form, and Dire Bear Form is reduced by 20%.
  - WotLK rank 3: While using your Enrage ability in Bear Form or Dire Bear Form, your damage is increased by 15%, and your Tiger's Fury ability also instantly restores 60 energy.  In addition, the mana cost of Bear Form, Cat Form, and Dire Bear Form is reduced by 60%.
- **Mangle** (1 rank) - row 8 -> tier 5 - MATCH druid_feral_mangle
  - requires: Leader of the Pack
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Mangle the target, inflicting damage and causing the target to take additional damage from bleed effects for 1 min.  This ability can be used in Cat Form or Dire Bear Form.
- **Improved Mangle** (3 ranks) - row 8 -> tier 5 - NEW - we have no talent of this name
  - requires: Mangle
  - needs: cooldown-change, cost-change
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the cooldown of your Mangle (Bear) ability by 0.5 sec., and reduces the energy cost of your Mangle (Cat) ability by 2.
  - WotLK rank 3: Reduces the cooldown of your Mangle (Bear) ability by 1.5 sec., and reduces the energy cost of your Mangle (Cat) ability by 6.
- **Rend and Tear** (5 ranks) - row 9 -> tier 5 - MATCH druid_feral_rend_and_tear  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases damage done by your Maul and Shred attacks on bleeding targets by 4%, and increases the critical strike chance of your Ferocious Bite ability on bleeding targets by 5%.
  - WotLK rank 5: Increases damage done by your Maul and Shred attacks on bleeding targets by 20%, and increases the critical strike chance of your Ferocious Bite ability on bleeding targets by 25%.
- **Primal Gore** (1 rank) - row 9 -> tier 5 - NEW - we have no talent of this name
  - requires: Rend and Tear
  - WotLK rank 1: Grants the periodic damage from your Lacerate and Rip abilities the ability to critically hit.
- **Berserk** (1 rank) - row 10 -> tier 6 - MATCH druid_feral_berserk
  - needs: cooldown-change, cost-change
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When activated, this ability causes your Mangle (Bear) ability to hit up to 3 targets and have no cooldown, and reduces the energy cost of all your Cat Form abilities by 50%. Lasts 15 sec. You cannot use Tiger's Fury while Berserk is active.

Clears the effect of Fear and makes you immune to Fear for the duration.

## Restoration - 27 talents, 80 points

- **Improved Mark of the Wild** (2 ranks) - row 0 -> tier 0 - MATCH druid_restoration_improved_mark_of_the_wild  [ours is scalar]
  - WotLK rank 1: Increases the effects of your Mark of the Wild and Gift of the Wild spells by 20%, and increases all of your total attributes by 1%.
  - WotLK rank 2: Increases the effects of your Mark of the Wild and Gift of the Wild spells by 40%, and increases all of your total attributes by 2%.
- **Nature's Focus** (3 ranks) - row 0 -> tier 0 - MATCH druid_restoration_natures_focus
  - needs: heal
  - WotLK rank 1: Reduces the pushback suffered from damaging attacks  while casting Healing Touch, Wrath, Entangling Roots, Cyclone, Nourish, Regrowth and Tranquility by 23%.
  - WotLK rank 3: Reduces the pushback suffered from damaging attacks  while casting Healing Touch, Wrath, Entangling Roots, Cyclone, Nourish, Regrowth and Tranquility by 70%.
- **Furor** (5 ranks) - row 0 -> tier 0 - MATCH druid_restoration_furor  [ours is scalar]
  - needs: proc-chance
  - WotLK rank 1: Gives you 20% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form, and you keep up to 20 of your Energy when you shapeshift into Cat Form, and increases your total Intellect while in Moonkin form by 2%.
  - WotLK rank 5: Gives you 100% chance to gain 10 Rage when you shapeshift into Bear and Dire Bear Form, and you keep up to 100 of your Energy when you shapeshift into Cat Form, and increases your total Intellect while in Moonkin form by 10%.
- **Naturalist** (5 ranks) - row 1 -> tier 1 - MATCH druid_restoration_naturalist  [ours is scalar]
  - needs: heal
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the cast time of your Healing Touch spell by 0.1 sec and increases the damage you deal with physical attacks in all forms by 2%.
  - WotLK rank 5: Reduces the cast time of your Healing Touch spell by 0.5 sec and increases the damage you deal with physical attacks in all forms by 10%.
- **Subtlety** (3 ranks) - row 1 -> tier 1 - MATCH druid_restoration_subtlety  [ours is scalar]
  - needs: proc-chance, threat, dispel
  - WotLK rank 1: Reduces the threat generated by your restoration spells by 10% and reduces the chance your helpful spells, Moonfire, and Insect Swarm will be dispelled by 10%.
  - WotLK rank 3: Reduces the threat generated by your restoration spells by 30% and reduces the chance your helpful spells, Moonfire, and Insect Swarm will be dispelled by 30%.
- **Natural Shapeshifter** (3 ranks) - row 1 -> tier 1 - NEW - we have no talent of this name
  - needs: cost-change
  - WotLK rank 1: Reduces the mana cost of all shapeshifting by 10%.
  - WotLK rank 3: Reduces the mana cost of all shapeshifting by 30%.
- **Intensity** (3 ranks) - row 2 -> tier 1 - MATCH druid_restoration_intensity  [ours is scalar]
  - needs: resource-grant
  - WotLK rank 1: Allows 17% of your Mana regeneration to continue while casting and causes your Enrage ability to instantly generate 4 rage.
  - WotLK rank 3: Allows 50% of your Mana regeneration to continue while casting and causes your Enrage ability to instantly generate 10 rage.
- **Omen of Clarity** (1 rank) - row 2 -> tier 1 - NEW - we have no talent of this name
  - needs: proc-chance, cost-change, heal
  - WotLK rank 1: Each of the Druid's damage, healing spells and auto attacks has a chance of causing the caster to enter a Clearcasting state. The Clearcasting state reduces the Mana, Rage or Energy cost of your next damage, healing spell or offensive ability by 100%.
- **Master Shapeshifter** (2 ranks) - row 2 -> tier 1 - NEW - we have no talent of this name
  - requires: Natural Shapeshifter
  - needs: proc-chance, crit, heal
  - WotLK rank 1: Grants an effect which lasts while the Druid is within the respective shapeshift form.

Bear Form - Increases physical damage by 2%.

Cat Form - Increases critical strike chance by 2%.

Moonking Form - Increases spell damage by 2%.

Tree of Life Form - Increases healing by 2%.
  - WotLK rank 2: Grants an effect which lasts while the Druid is within the respective shapeshift form.

Bear Form - Increases physical damage by 4%.

Cat Form - Increases critical strike chance by 4%.

Moonking Form - Increases spell damage by 4%.

Tree of Life Form - Increases healing by 4%.
- **Tranquil Spirit** (5 ranks) - row 3 -> tier 2 - MATCH druid_restoration_tranquil_spirit  [ours is scalar]
  - needs: cost-change, heal
  - WotLK rank 1: Reduces the mana cost of your Healing Touch, Nourish and Tranquility spells by 2%.
  - WotLK rank 5: Reduces the mana cost of your Healing Touch, Nourish and Tranquility spells by 10%.
- **Improved Rejuvenation** (3 ranks) - row 3 -> tier 2 - MATCH druid_restoration_improved_rejuvenation  [ours is scalar]
  - WotLK rank 1: Increases the effect of your Rejuvenation spell by 5%.
  - WotLK rank 3: Increases the effect of your Rejuvenation spell by 15%.
- **Nature's Swiftness** (1 rank) - row 4 -> tier 2 - MATCH druid_restoration_natures_swiftness
  - requires: Intensity
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When activated, your next Nature spell with a base casting time less than 10 sec. becomes an instant cast spell.
- **Gift of Nature** (5 ranks) - row 4 -> tier 2 - MATCH druid_restoration_gift_of_nature  [ours is scalar]
  - needs: heal
  - WotLK rank 1: Increases the effect of all healing spells by 2%.
  - WotLK rank 5: Increases the effect of all healing spells by 10%.
- **Improved Tranquility** (2 ranks) - row 4 -> tier 2 - MATCH druid_restoration_improved_tranquility  [ours is scalar]
  - needs: cooldown-change, threat
  - WotLK rank 1: Reduces threat caused by Tranquility by 50%, and reduces the cooldown by 30%.
  - WotLK rank 2: Reduces threat caused by Tranquility by 100%, and reduces the cooldown by 60%.
- **Empowered Touch** (2 ranks) - row 5 -> tier 3 - MATCH druid_restoration_empowered_touch  [ours is scalar]
  - needs: heal
  - WotLK rank 1: Your Healing Touch spell gains an additional 20% and your Nourish spell gains an additional 10% of your bonus healing effects.
  - WotLK rank 2: Your Healing Touch spell gains an additional 40% and your Nourish spell gains an additional 20% of your bonus healing effects.
- **Nature's Bounty** (5 ranks) - row 5 -> tier 3 - MATCH druid_restoration_natures_bounty  [ours is scalar]
  - requires: Improved Rejuvenation
  - needs: proc-chance
  - WotLK rank 1: Increases the critical effect chance of your Regrowth and Nourish spells by 5%.
  - WotLK rank 5: Increases the critical effect chance of your Regrowth and Nourish spells by 25%.
- **Living Spirit** (3 ranks) - row 6 -> tier 4 - MATCH druid_restoration_living_spirit  [ours is scalar]
  - WotLK rank 1: Increases your total Spirit by 5%.
  - WotLK rank 3: Increases your total Spirit by 15%.
- **Swiftmend** (1 rank) - row 6 -> tier 4 - MATCH druid_restoration_swiftmend
  - requires: Gift of Nature
  - needs: heal
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Consumes a Rejuvenation or Regrowth effect on a friendly target to instantly heal them an amount equal to 12 sec. of Rejuvenation or 18 sec. of Regrowth.
- **Natural Perfection** (3 ranks) - row 6 -> tier 4 - MATCH druid_restoration_natural_perfection  [ours is scalar]
  - needs: proc-chance, crit
  - **BLOCKED**: BLOCKED:stacks - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your critical strike chance with all spells is increased by 1% and critical strikes against you give you the Natural Perfection effect reducing all damage taken by 2%.  Stacks up to 3 times.  Lasts 8 sec.
  - WotLK rank 3: Your critical strike chance with all spells is increased by 3% and critical strikes against you give you the Natural Perfection effect reducing all damage taken by 4%.  Stacks up to 3 times.  Lasts 8 sec.
- **Empowered Rejuvenation** (5 ranks) - row 7 -> tier 4 - MATCH druid_restoration_restoration_mastery  [ours is scalar]
  - needs: heal
  - WotLK rank 1: The bonus healing effects of your healing over time spells is increased by 4%.
  - WotLK rank 5: The bonus healing effects of your healing over time spells is increased by 20%.
- **Living Seed** (3 ranks) - row 7 -> tier 4 - MATCH druid_restoration_living_seed
  - needs: proc-chance, heal
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When you critically heal your target with Swiftmend, Regrowth, Nourish or Healing Touch spell you have a 33% chance to plant a Living Seed on the target for 30% of the amount healed. The Living Seed will bloom when the target is next attacked. Lasts 15 sec.
  - WotLK rank 3: When you critically heal your target with Swiftmend, Regrowth, Nourish or Healing Touch spell you have a 100% chance to plant a Living Seed on the target for 30% of the amount healed. The Living Seed will bloom when the target is next attacked. Lasts 15 sec.
- **Revitalize** (3 ranks) - row 8 -> tier 5 - MATCH druid_restoration_revitalize
  - needs: proc-chance, resource-grant
  - WotLK rank 1: Your Rejuvenation and Wild Growth spells have a 5% chance to restore 8 Energy, 4 Rage, 1% Mana or 16 Runic Power per tick.
  - WotLK rank 3: Your Rejuvenation and Wild Growth spells have a 15% chance to restore 8 Energy, 4 Rage, 1% Mana or 16 Runic Power per tick.
- **Tree of Life** (1 rank) - row 8 -> tier 5 - MATCH druid_restoration_tree_of_life
  - requires: Empowered Rejuvenation
  - needs: cost-change, heal, aoe
  - WotLK rank 1: Instant Reduces the mana cost of your healing over time spells by 20% and grants the ability to shapeshift into the Tree of Life. While in this form you increase healing received by 6% for all party and raid members within 100 yards, and you can only cast Restoration spells in addition to Innervate, Barkskin, Nature's Grasp and Thorns spells.

The act of shapeshifting frees the caster of Polymorph and Movement Impairing effects.
- **Improved Tree of Life** (3 ranks) - row 8 -> tier 5 - NEW - we have no talent of this name
  - requires: Tree of Life
  - needs: heal
  - WotLK rank 1: Increases your armor contribution from items while in Tree of Life Form by 67%, and increases your healing spell power by 5% of your spirit while in Tree of Life Form.
  - WotLK rank 3: Increases your armor contribution from items while in Tree of Life Form by 200%, and increases your healing spell power by 15% of your spirit while in Tree of Life Form.
- **Improved Barkskin** (2 ranks) - row 9 -> tier 5 - NEW - we have no talent of this name
  - needs: proc-chance, dispel
  - WotLK rank 1: Grants 80% additional armor contribution from cloth and leather items while in Travel Form or while not shapeshifted, increases the damage reduction granted by your Barkskin spell by 5% and reduces the chance your Barkskin is dispelled by 35%.
  - WotLK rank 2: Grants 160% additional armor contribution from cloth and leather items while in Travel Form or while not shapeshifted, increases the damage reduction granted by your Barkskin spell by 10% and reduces the chance your Barkskin is dispelled by 70%.
- **Gift of the Earthmother** (5 ranks) - row 9 -> tier 5 - MATCH druid_restoration_gift_of_the_earthmother  [ours is scalar]
  - needs: cooldown-change
  - WotLK rank 1: Increases your total spell haste by 2% and reduces the base cooldown of your Lifebloom spell by 2%.
  - WotLK rank 5: Increases your total spell haste by 10% and reduces the base cooldown of your Lifebloom spell by 10%.
- **Wild Growth** (1 rank) - row 10 -> tier 6 - MATCH druid_restoration_wild_growth
  - requires: Tree of Life
  - needs: dot-hot, heal, aoe
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Heals up to 5 friendly party or raid members within 15 yards of the target for 686 over 7 sec. The amount healed is applied quickly at first, and slows down as the Wild Growth reaches its full duration.
