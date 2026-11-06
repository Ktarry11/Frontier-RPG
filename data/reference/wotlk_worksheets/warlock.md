# Warlock - real WotLK 3.3.5a reference vs ours

- WotLK talents: **81** across 3 trees
- already in our data by name: **64** (of those, **33** are pure scalars on our side)
- not in our data at all: **17**
- carry real-time assumptions needing translation: **30** (37%)
- ask for a mechanic this engine does not have: **15**

Source: the game's own `Spell.dbc`, via github.com/atosfr/WotLK-3.3.5-Talent-Calculator (`Talents.json` + `TalentDescriptions.json`). Slot counts independently cross-checked against the rendered wowtbc.gg calculator - all six checkable trees match.

`MATCH` - we already have a talent of this name. `scalar` means ours is a pure numeric bonus, which is the thing being replaced. `needs` lists the engine mechanic the real talent wants. **BLOCKED** means this engine has no way to express it, so that talent needs a substitute mechanic rather than a literal port - never a tooltip the engine cannot honour.

WotLK rows 0-10 map onto Frontier tiers 1-6 as `tier = row // 2 + 1`, capped at 6, so the capstone row sits alone at tier 6. **Numbers are not ported**: WotLK assumes 80 levels, raid fights and real seconds; Frontier caps at 60 and fights run 2-3 turns on trash, 5-6 on a boss.


## Affliction - 28 talents, 70 points

- **Improved Curse of Agony** (2 ranks) - row 0 -> tier 1 - NEW - we have no talent of this name
  - WotLK rank 1: Increases the damage done by your Curse of Agony by 5%.
  - WotLK rank 2: Increases the damage done by your Curse of Agony by 10%.
- **Suppression** (3 ranks) - row 0 -> tier 1 - MATCH warlock_affliction_suppression  [ours is scalar]
  - needs: proc-chance, cost-change
  - WotLK rank 1: Increases your chance to hit with spells by 1%, and reduces the mana cost of your Affliction spells by 2%.
  - WotLK rank 3: Increases your chance to hit with spells by 3%, and reduces the mana cost of your Affliction spells by 6%.
- **Improved Corruption** (5 ranks) - row 0 -> tier 1 - MATCH warlock_affliction_improved_corruption  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases the damage done by your Corruption by 2%, and increases the critical strike chance of your Seed of Corruption by 1%.
  - WotLK rank 5: Increases the damage done by your Corruption by 10%, and increases the critical strike chance of your Seed of Corruption by 5%.
- **Improved Curse of Weakness** (2 ranks) - row 1 -> tier 1 - NEW - we have no talent of this name
  - WotLK rank 1: Increases the amount of attack power reduced by your Curse of Weakness by 10%.
  - WotLK rank 2: Increases the amount of attack power reduced by your Curse of Weakness by 20%.
- **Improved Drain Soul** (2 ranks) - row 1 -> tier 1 - MATCH warlock_affliction_improved_drain_soul
  - needs: threat
  - WotLK rank 1: Returns 7% of your maximum mana if the target is killed by you while you drain its soul. In addition, your Affliction spells generate 10% less threat.
  - WotLK rank 2: Returns 15% of your maximum mana if the target is killed by you while you drain its soul. In addition, your Affliction spells generate 20% less threat.
- **Improved Life Tap** (2 ranks) - row 1 -> tier 1 - MATCH warlock_affliction_improved_life_tap  [ours is scalar]
  - WotLK rank 1: Increases the amount of Mana awarded by your Life Tap spell by 10%.
  - WotLK rank 2: Increases the amount of Mana awarded by your Life Tap spell by 20%.
- **Soul Siphon** (2 ranks) - row 1 -> tier 1 - MATCH warlock_affliction_soul_siphon
  - WotLK rank 1: Increases the amount drained by your Drain Life and Drain Soul spells by an additional 3% for each of your Affliction effects on the target, up to a maximum of 9% additional effect.
  - WotLK rank 2: Increases the amount drained by your Drain Life and Drain Soul spells by an additional 6% for each of your Affliction effects on the target, up to a maximum of 18% additional effect.
- **Improved Fear** (2 ranks) - row 2 -> tier 2 - NEW - we have no talent of this name
  - needs: duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Causes your Fear spell to inflict a Nightmare on the target when the fear effect ends. The Nightmare effect reduces the target's movement speed by 15% for 5 sec.
  - WotLK rank 2: Causes your Fear spell to inflict a Nightmare on the target when the fear effect ends. The Nightmare effect reduces the target's movement speed by 30% for 5 sec.
- **Fel Concentration** (3 ranks) - row 2 -> tier 2 - MATCH warlock_affliction_fel_concentration  [ours is scalar]
  - WotLK rank 1: Reduces the pushback suffered from damaging attacks while casting Drain Life, Drain Mana, Drain Soul, Unstable Affliction, and Haunt by 23%.
  - WotLK rank 3: Reduces the pushback suffered from damaging attacks while casting Drain Life, Drain Mana, Drain Soul, Unstable Affliction, and Haunt by 70%.
- **Amplify Curse** (1 rank) - row 2 -> tier 2 - MATCH warlock_affliction_amplify_curse  [ours is scalar]
  - needs: cooldown-change
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the global cooldown of your Curses by 0.5 sec.
- **Grim Reach** (2 ranks) - row 3 -> tier 2 - NEW - we have no talent of this name
  - WotLK rank 1: Increases the range of your Affliction spells by 10%.
  - WotLK rank 2: Increases the range of your Affliction spells by 20%.
- **Nightfall** (2 ranks) - row 3 -> tier 2 - MATCH warlock_affliction_nightfall
  - needs: proc-chance
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - WotLK rank 1: Gives your Corruption and Drain Life spells a 2% chance to cause you to enter a Shadow Trance state after damaging the opponent. The Shadow Trance state reduces the casting time of your next Shadow Bolt spell by 100%.
  - WotLK rank 2: Gives your Corruption and Drain Life spells a 4% chance to cause you to enter a Shadow Trance state after damaging the opponent. The Shadow Trance state reduces the casting time of your next Shadow Bolt spell by 100%.
- **Empowered Corruption** (3 ranks) - row 3 -> tier 2 - MATCH warlock_affliction_empowered_corruption  [ours is scalar]
  - WotLK rank 1: Increases the damage of your Corruption spell by an amount equal to 12% of your spell power.
  - WotLK rank 3: Increases the damage of your Corruption spell by an amount equal to 36% of your spell power.
- **Shadow Embrace** (5 ranks) - row 4 -> tier 3 - MATCH warlock_affliction_shadow_embrace
  - needs: duration-window, heal
  - **BLOCKED**: BLOCKED:stacks - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your Shadow Bolt and Haunt spells apply the Shadow Embrace effect, increasing all shadow periodic damage dealt to the target by you by 1%, and reduces all periodic healing done to the target by 2%. Lasts for 12 sec. Stacks up to 3 times.
  - WotLK rank 5: Your Shadow Bolt and Haunt spells apply the Shadow Embrace effect, increasing all shadow periodic damage dealt to the target by you by 5%, and reduces all periodic healing done to the target by 10%. Lasts for 12 sec. Stacks up to 3 times.
- **Siphon Life** (1 rank) - row 4 -> tier 3 - MATCH warlock_affliction_siphon_life
  - needs: heal
  - WotLK rank 1: When you deal damage with your Corruption spell, you are instantly healed for 40% of the damage done. In addition, the damage done by your Corruption, Seed of Corruption and Unstable Affliction damage over time effects is increased by 5%.
- **Curse of Exhaustion** (1 rank) - row 4 -> tier 3 - MATCH warlock_affliction_curse_of_exhaustion  [ours is scalar]
  - requires: Amplify Curse
  - needs: duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the target's movement speed by 30% for 12 sec. Only one Curse per Warlock can be active on any one target.
- **Improved Felhunter** (2 ranks) - row 5 -> tier 3 - MATCH warlock_demonology_improved_felhunter
  - needs: cooldown-change
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your Felhunter regains 4% of its maximum mana each time it hits with its Shadow Bite ability and the cooldown on that ability is reduced by 2 sec. In addition, increases the effect of your Felhunter's Fel Intelligence by 5%.
  - WotLK rank 2: Your Felhunter regains 8% of its maximum mana each time it hits with its Shadow Bite ability and the cooldown on that ability is reduced by 4 sec. In addition, increases the effect of your Felhunter's Fel Intelligence by 10%.
- **Shadow Mastery** (5 ranks) - row 5 -> tier 3 - MATCH warlock_affliction_shadow_mastery  [ours is scalar]
  - requires: Siphon Life
  - WotLK rank 1: Increases the damage dealt or life drained by your Shadow spells and your Felhunter's Shadow Bite ability by 3%.
  - WotLK rank 5: Increases the damage dealt or life drained by your Shadow spells and your Felhunter's Shadow Bite ability by 15%.
- **Eradication** (3 ranks) - row 6 -> tier 4 - MATCH warlock_affliction_eradication
  - needs: proc-chance, duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When you deal damage with Corruption, you have 6% chance to increase your spell casting speed by 6% for 10 sec.
  - WotLK rank 3: When you deal damage with Corruption, you have 6% chance to increase your spell casting speed by 20% for 10 sec.
- **Contagion** (5 ranks) - row 6 -> tier 4 - MATCH warlock_affliction_contagion  [ours is scalar]
  - needs: proc-chance, dispel
  - WotLK rank 1: Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 1% and reduces the chance your helpful Affliction spells and damage over time effects will be dispelled by an additional 6%.
  - WotLK rank 5: Increases the damage of Curse of Agony, Corruption and Seed of Corruption by 5% and reduces the chance your helpful Affliction spells and damage over time effects will be dispelled by an additional 30%.
- **Dark Pact** (1 rank) - row 6 -> tier 4 - MATCH warlock_affliction_dark_pact
  - needs: pet
  - WotLK rank 1: Drains 305 of your summoned demon's Mana, returning 100% to you.
- **Improved Howl of Terror** (2 ranks) - row 7 -> tier 4 - NEW - we have no talent of this name
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the casting time of your Howl of Terror spell by 0.8 sec.
  - WotLK rank 2: Reduces the casting time of your Howl of Terror spell by 1.5 sec.
- **Malediction** (3 ranks) - row 7 -> tier 4 - MATCH warlock_affliction_malediction  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases your spell damage by 1%, and increases the periodic critical strike chance of your Corruption and Unstable Affliction spells by 3%.
  - WotLK rank 3: Increases your spell damage by 3%, and increases the periodic critical strike chance of your Corruption and Unstable Affliction spells by 9%.
- **Death's Embrace** (3 ranks) - row 8 -> tier 5 - MATCH warlock_affliction_death_embrace  [ours is scalar]
  - needs: hp-threshold, heal
  - WotLK rank 1: Increases the amount drained by your Drain Life by 10% while your health is at or below 20% health, and increases the damage done by your Shadow spells by 4% when your target is at or below 35% health.
  - WotLK rank 3: Increases the amount drained by your Drain Life by 30% while your health is at or below 20% health, and increases the damage done by your Shadow spells by 12% when your target is at or below 35% health.
- **Unstable Affliction** (1 rank) - row 8 -> tier 5 - MATCH warlock_affliction_unstable_affliction
  - requires: Contagion
  - needs: dot-hot, duration-window, dispel
  - **BLOCKED**: BLOCKED:interrupt - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Shadow energy slowly destroys the target, causing 550 damage over 15 sec. In addition, if the Unstable Affliction is dispelled it will cause 990 damage to the dispeller and silence them for 5 sec. Only one Unstable Affliction or Immolate per Warlock can be active on any one target.
- **Pandemic** (1 rank) - row 8 -> tier 5 - MATCH warlock_affliction_pandemic
  - requires: Unstable Affliction
  - needs: crit
  - WotLK rank 1: Grants the periodic damage from your Corruption and Unstable Affliction spells the ability to critically hit for 100% increased damage, and increases the critical strike damage bonus of your Haunt spell by 100%.
- **Everşasting Affliction** (5 ranks) - row 9 -> tier 5 - NEW - we have no talent of this name
  - needs: proc-chance
  - WotLK rank 1: Your Corruption and Unstable Affliction spells gain an additional 1% of your bonus spell damage, and your Drain Life, Drain Soul, Shadow Bolt, and Haunt spells have a 20% chance to reset the duration of your Corruption spell on the target.
  - WotLK rank 5: Your Corruption and Unstable Affliction spells gain an additional 5% of your bonus spell damage, and your Drain Life, Drain Soul, Shadow Bolt, and Haunt spells have a 100% chance to reset the duration of your Corruption spell on the target.
- **Haunt** (1 rank) - row 10 -> tier 6 - MATCH warlock_affliction_haunt
  - needs: duration-window, heal, dispel
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: You send a ghostly soul into the target, dealing 405 to 473 Shadow damage and increasing all damage done by your Shadow damage-over-time effects on the target by 20% for 12 sec. When the Haunt spell ends or is dispelled, the soul returns to you, healing you for 100% of the damage it did to the target.

## Demonology - 27 talents, 71 points

- **Improved Healthstone** (2 ranks) - row 0 -> tier 1 - MATCH warlock_demonology_improved_healthstone
  - needs: heal
  - WotLK rank 1: Increases the amount of Health restored by your Healthstone by 10%.
  - WotLK rank 2: Increases the amount of Health restored by your Healthstone by 20%.
- **Improved Imp** (3 ranks) - row 0 -> tier 1 - MATCH warlock_demonology_improved_imp  [ours is scalar]
  - WotLK rank 1: Increases the effect of your Imp's Firebolt, Fire Shield, and Blood Pact spells by 10%.
  - WotLK rank 3: Increases the effect of your Imp's Firebolt, Fire Shield, and Blood Pact spells by 30%.
- **Demonic Embrace** (3 ranks) - row 0 -> tier 1 - MATCH warlock_demonology_demonic_embrace  [ours is scalar]
  - WotLK rank 1: Increases your total Stamina by 4%.
  - WotLK rank 3: Increases your total Stamina by 10%.
- **Fel Synergy** (2 ranks) - row 0 -> tier 1 - NEW - we have no talent of this name
  - needs: proc-chance, heal, pet
  - WotLK rank 1: You have a 50% chance to heal your pet for 15% of the amount of spell damage done by you.
  - WotLK rank 2: You have a 100% chance to heal your pet for 15% of the amount of spell damage done by you.
- **Improved Health Funnel** (2 ranks) - row 1 -> tier 1 - NEW - we have no talent of this name
  - needs: cost-change, heal, pet
  - WotLK rank 1: Increases the amount of Health transferred by your Health Funnel spell by 10% and reduces the health cost by 10%. In addition, your summoned Demon takes 15% less damage while under the effect of your Health Funnel.
  - WotLK rank 2: Increases the amount of Health transferred by your Health Funnel spell by 20% and reduces the health cost by 20%. In addition, your summoned Demon takes 30% less damage while under the effect of your Health Funnel.
- **Demonic Brutality** (3 ranks) - row 1 -> tier 1 - MATCH warlock_demonology_demonic_brutality
  - needs: pet
  - WotLK rank 1: Increases the effectiveness of your Voidwalker's Torment, Consume Shadows, Sacrifice and Suffering spells by 10%, and increases the attack power bonus on your Felguard's Demonic Frenzy effect by 1%.
  - WotLK rank 3: Increases the effectiveness of your Voidwalker's Torment, Consume Shadows, Sacrifice and Suffering spells by 30%, and increases the attack power bonus on your Felguard's Demonic Frenzy effect by 3%.
- **Fel Vitality** (3 ranks) - row 1 -> tier 1 - MATCH warlock_demonology_fel_vitality
  - needs: heal
  - WotLK rank 1: Increases the Stamina and Intellect of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 5% and increases your maximum health and mana by 1%.
  - WotLK rank 3: Increases the Stamina and Intellect of your Imp, Voidwalker, Succubus, Felhunter and Felguard by 15% and increases your maximum health and mana by 3%.
- **Improved Scubbus** (3 ranks) - row 2 -> tier 2 - NEW - we have no talent of this name
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - WotLK rank 1: Reduces the cast time of your Succubus' Seduction by 22%, and increases the duration of your Succubus' Seduction and Lesser Invisibility spells by 10%.
  - WotLK rank 3: Reduces the cast time of your Succubus' Seduction by 66%, and increases the duration of your Succubus' Seduction and Lesser Invisibility spells by 30%.
- **Soul Link** (1 rank) - row 2 -> tier 2 - MATCH warlock_demonology_soul_link
  - needs: pet
  - WotLK rank 1: When active, 20% of all damage taken by the caster is taken by your Imp, Voidwalker, Succubus, Felhunter, Felguard, or enslaved demon instead. That damage cannot be prevented. Lasts as long as the demon is active and controlled.
- **Fel Domination** (1 rank) - row 2 -> tier 2 - NEW - we have no talent of this name
  - needs: cost-change
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your next Imp, Voidwalker, Succubus, Felhunter or Felguard Summon spell has its casting time reduced by 5.5 sec and its Mana cost reduced by 50%.
- **Demonic Aegis** (3 ranks) - row 2 -> tier 2 - MATCH warlock_demonology_demonic_aegis  [ours is scalar]
  - needs: pet
  - WotLK rank 1: Increases the effectiveness of your Demon Armor and Fel Armor spells by 10%.
  - WotLK rank 3: Increases the effectiveness of your Demon Armor and Fel Armor spells by 30%.
- **Unholy Power** (5 ranks) - row 3 -> tier 2 - MATCH warlock_demonology_unholy_power  [ours is scalar]
  - requires: Soul Link
  - WotLK rank 1: Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 4%.
  - WotLK rank 5: Increases the damage done by your Voidwalker, Succubus, Felhunter and Felguard's melee attacks and your Imp's Firebolt by 20%.
- **Master Summoner** (2 ranks) - row 3 -> tier 2 - MATCH warlock_demonology_master_summoner  [ours is scalar]
  - requires: Fel Domination
  - needs: cost-change
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the casting time of your Imp, Voidwalker, Succubus, Felhunter and Fel Guard Summoning spells by 2 sec and the Mana cost by 20%.
  - WotLK rank 2: Reduces the casting time of your Imp, Voidwalker, Succubus, Felhunter and Fel Guard Summoning spells by 4 sec and the Mana cost by 40%.
- **Mana Feed** (1 rank) - row 4 -> tier 3 - NEW - we have no talent of this name
  - requires: Unholy Power
  - needs: pet
  - WotLK rank 1: When you gain mana from Drain Mana or Life Tap spells, your summoned demon gains 100% of the mana you gain.
- **Master Conjuror** (2 ranks) - row 4 -> tier 3 - NEW - we have no talent of this name
  - WotLK rank 1: Increases the combat ratings gained from your conjured Firestone and Spellstone by 150%.
  - WotLK rank 2: Increases the combat ratings gained from your conjured Firestone and Spellstone by 300%.
- **Master Demonologist** (5 ranks) - row 5 -> tier 3 - MATCH warlock_demonology_master_demonologist
  - requires: Unholy Power
  - needs: proc-chance, pet
  - WotLK rank 1: Grants both the Warlock and the summoned demon an effect as long as that demon is active.

Imp - Increases your Fire damage by 1%, and increases the critical effect chance of your Fire spells by 1%.

Voidwalker - Reduces Physical damage taken by 2%.

Succubus - Increases your Shadow damage by 1%, and increases the critical effect chance of your Shadow spells by 1%.

Felhunter - Reduces all spell damage taken by 2%.

Felguard - Increases all damage done by 1%, and reduces all damage taken by 1%.
  - WotLK rank 5: Grants both the Warlock and the summoned demon an effect as long as that demon is active.

Imp - Increases your Fire damage by 5%, and increases the critical effect chance of your Fire spells by 5%.

Voidwalker - Reduces Physical damage taken by 10%.

Succubus - Increases your Shadow damage by 5%, and increases the critical effect chance of your Shadow spells by 5%.

Felhunter - Reduces all spell damage taken by 10%.

Felguard - Increases all damage done by 5%, and reduces all damage taken by 5%.
- **Molten Core** (3 ranks) - row 5 -> tier 3 - MATCH warlock_demonology_molten_core  [ours is scalar]
  - needs: proc-chance, crit
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the duration of your Immolate by 3 sec, and you have a 4% chance to gain the Molten Core effect when your Corruption deals damage. The Molten Core effect empowers your next 3 Incinerate or Soul Fire spells cast within 15 sec.

Incinerate - Increases damage done by 6% and reduces cast time by 10%.

Soul Fire - Increases damage done by 6% and increases critical strike chance by 5%.
  - WotLK rank 3: Increases the duration of your Immolate by 9 sec, and you have a 12% chance to gain the Molten Core effect when your Corruption deals damage. The Molten Core effect empowers your next 3 Incinerate or Soul Fire spells cast within 15 sec.

Incinerate - Increases damage done by 18% and reduces cast time by 30%.

Soul Fire - Increases damage done by 18% and increases critical strike chance by 15%.
- **Demonic Resilience** (3 ranks) - row 6 -> tier 4 - MATCH warlock_demonology_demonic_resilience  [ours is scalar]
  - needs: proc-chance, pet
  - WotLK rank 1: Reduces the chance you'll be critically hit by melee and spells by 1% and reduces all damage your summoned demon takes by 5%.
  - WotLK rank 3: Reduces the chance you'll be critically hit by melee and spells by 3% and reduces all damage your summoned demon takes by 15%.
- **Demonic Empowerment** (1 rank) - row 6 -> tier 4 - MATCH warlock_demonology_demonic_empowerment  [ours is scalar]
  - requires: Master Demonologist
  - needs: proc-chance, duration-window, crit, heal, stun, threat, pet, dispel
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Grants the Warlock's summoned demon Empowerment.

Imp - Increases the Imp's spell critical strike chance by 20% for 30 sec.

Voidwalker - Increases the Voidwalker's health by 20%, and its threat generated from spells and attacks by 20% for 20 sec.

Succubus - Instantly vanishes, causing the Succubus to go into an improved Invisibility state. The vanish effect removes all stuns, snares and movement impairing effects from the Succubus.

Felhunter - Dispels all magical effects from the Felhunter.

Felguard - Increases the Felguard's attack speed by 20% and breaks all stun, snare and movement impairing effects and makes your Felguard immune to them for 15 sec.
- **Demonic Knowledge** (3 ranks) - row 6 -> tier 4 - MATCH warlock_demonology_demonic_knowledge  [ours is scalar]
  - needs: pet
  - WotLK rank 1: Increases your spell damage by an amount equal to 4% of the total of your active demon's Stamina plus Intellect.
  - WotLK rank 3: Increases your spell damage by an amount equal to 12% of the total of your active demon's Stamina plus Intellect.
- **Demonic Tactics** (5 ranks) - row 7 -> tier 4 - MATCH warlock_demonology_demonic_tactics  [ours is scalar]
  - needs: proc-chance, crit, pet
  - WotLK rank 1: Increases melee and spell critical strike chance for you and your summoned demon by 2%.
  - WotLK rank 5: Increases melee and spell critical strike chance for you and your summoned demon by 10%.
- **Decimation** (2 ranks) - row 7 -> tier 4 - MATCH warlock_demonology_decimation  [ours is scalar]
  - needs: hp-threshold, duration-window, cost-change, heal
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When you Shadowbolt, Incinerate or Soul Fire a target that is at or below 35% health, the cast time of Soul Fire spell is reduced by 20% for 10 sec. Soul Fires cast under the effect of Decimation cost no shard.
  - WotLK rank 2: When you Shadowbolt, Incinerate or Soul Fire a target that is at or below 35% health, the cast time of your Soul Fire spell is reduced by 40% for 10 sec. Soul Fires cast under the effect of Decimation cost no shard.
- **Improved Demonic Tactics** (3 ranks) - row 8 -> tier 5 - NEW - we have no talent of this name
  - requires: Demonic Tactics
  - needs: proc-chance, crit, pet
  - WotLK rank 1: Increases your summoned demon's critical strike chance equal to 10% of your critical strike chance.
  - WotLK rank 3: Increases your summoned demon's critical strike chance equal to 30% of your critical strike chance.
- **Summon Felguard** (1 rank) - row 8 -> tier 5 - NEW - we have no talent of this name
  - WotLK rank 1: Summons a Felguard under the command of the Warlock.
- **Nemesis** (3 ranks) - row 8 -> tier 5 - MATCH warlock_demonology_demonology_mastery
  - needs: cooldown-change, pet
  - WotLK rank 1: Reduces the cooldown of your Demonic Empowerment, Metamorphosis, and Fel Domination spells by 10%.
  - WotLK rank 3: Reduces the cooldown of your Demonic Empowerment, Metamorphosis, and Fel Domination spells by 30%.
- **Demonic Pact** (5 ranks) - row 9 -> tier 5 - MATCH warlock_demonology_demonic_pact
  - needs: duration-window, cooldown-change, pet
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases your spell damage by 2%, and your pet's criticals apply the Demonic Pact effect to your party or raid members. Demonic Pact increases spell power by 2% of your Spell Damage for 45 sec. This effect has a 20 sec cooldown. Does not work on Enslaved demons.
  - WotLK rank 5: Increases your spell damage by 10%, and your pet's criticals apply the Demonic Pact effect to your party or raid members. Demonic Pact increases spell power by 10% of your Spell Damage for 45 sec. This effect has a 20 sec cooldown. Does not work on Enslaved demons.
- **Metamorphosis** (1 rank) - row 10 -> tier 6 - MATCH warlock_demonology_metamorphosis
  - needs: proc-chance, duration-window, cooldown-change, stun, pet
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: You transform into a Demon for 30 sec. This form increases your armor by 600%, damage by 20%, reduces the chance you'll be critically hit by melee attacks by 6% and reduces the duration of stun and snare effects by 50%. You gain some unique demon abilities in addition to your normal abilities. 3 minute cooldown.

## Destruction - 26 talents, 75 points

- **Improved Shadow Bolt** (5 ranks) - row 0 -> tier 1 - MATCH warlock_destruction_improved_shadow_bolt  [ours is scalar]
  - needs: proc-chance, crit
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the damage done by your Shadow Bolt spell by 2%, and your Shadow Bolt has a 20% chance to cause your target to be vulnerable to spell damage, increasing spell critical strike chance against that target by 5%. Effect lasts 30 sec.
  - WotLK rank 5: Increases the damage done by your Shadow Bolt spell by 10%, and your Shadow Bolt has a 100% chance to cause your target to be vulnerable to spell damage, increasing spell critical strike chance against that target by 5%. Effect lasts 30 sec.
- **Bane** (5 ranks) - row 0 -> tier 1 - MATCH warlock_destruction_bane  [ours is scalar]
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the casting time of your Shadow Bolt. Chaos Bolt and Immolate spells by 0.1 sec and your Soul Fire spell by 0.4 sec.
  - WotLK rank 5: Reduces the casting time of your Shadow Bolt. Chaos Bolt and Immolate spells by 0.5 sec and your Soul Fire spell by 2 sec.
- **Aftermath** (2 ranks) - row 1 -> tier 1 - MATCH warlock_destruction_aftermath
  - needs: proc-chance, duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the periodic damage done by your Immolate by 3%, and your Conflagrate has a 50% chance to daze the target for 5 sec.
  - WotLK rank 2: Increases the periodic damage done by your Immolate by 6%, and your Conflagrate has a 100% chance to daze the target for 5 sec.
- **Molten Skin** (3 ranks) - row 1 -> tier 1 - NEW - we have no talent of this name
  - WotLK rank 1: Reduces all damage taken by 2%.
  - WotLK rank 3: Reduces all damage taken by 6%.
- **Cataclysm** (3 ranks) - row 1 -> tier 1 - MATCH warlock_destruction_cataclysm  [ours is scalar]
  - needs: cost-change
  - WotLK rank 1: Reduces the Mana cost of your Destruction spells by 4%
  - WotLK rank 3: Reduces the Mana cost of your Destruction spells by 10%
- **Demonic Power** (2 ranks) - row 2 -> tier 2 - NEW - we have no talent of this name
  - needs: cooldown-change
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Reduces the cooldown of your Succubus' Lash of Pain spell by 3 sec. and reduces the casting time of your Imp's Firebolt spell by 0.25 sec.
  - WotLK rank 2: Reduces the cooldown of your Succubus' Lash of Pain spell by 6 sec. and reduces the casting time of your Imp's Firebolt spell by 0.5 sec.
- **Shadowburn** (1 rank) - row 2 -> tier 2 - MATCH warlock_destruction_shadowburn
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Instantly blasts the target for 87 to 99 Shadow damage. If the target dies within 5 sec of Shadowburn, and yields experience or honor, the caster gains a Soul Shard.
- **Ruin** (5 ranks) - row 2 -> tier 2 - MATCH warlock_destruction_ruin
  - needs: crit
  - WotLK rank 1: Increases the critical strike damage bonus of your Destruction spells and your Imp's Firebolt spell by 20%.
  - WotLK rank 5: Increases the critical strike damage bonus of your Destruction spells and your Imp's Firebolt spell by 100%.
- **Intensity** (2 ranks) - row 3 -> tier 2 - MATCH warlock_destruction_intensity
  - **BLOCKED**: BLOCKED:channel - needs a substitute mechanic
  - WotLK rank 1: Reduces the pushback suffered from damaging attacks while casting or channeling any Destruction spell by 35%.
  - WotLK rank 2: Reduces the pushback suffered from damaging attacks while casting or channeling any Destruction spell by 70%.
- **Destructive Reach** (2 ranks) - row 3 -> tier 2 - MATCH warlock_destruction_destructive_reach  [ours is scalar]
  - needs: threat
  - WotLK rank 1: Increases the range of your Destruction spells by 10% and reduces threat caused by Destruction spells by 10%.
  - WotLK rank 2: Increases the range of your Destruction spells by 20% and reduces threat caused by Destruction spells by 20%.
- **Improved Searing Pain** (3 ranks) - row 3 -> tier 2 - MATCH warlock_destruction_improved_searing_pain  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases the critical strike chance of your Searing Pain spell by 4%.
  - WotLK rank 3: Increases the critical strike chance of your Searing Pain spell by 10%.
- **Backlash** (3 ranks) - row 4 -> tier 3 - MATCH warlock_destruction_backlash
  - requires: Intensity
  - needs: proc-chance, dot-hot, crit
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases your critical strike chance with spells by an additional 1% and gives you a 8% chance when hit by a physical attack to reduce the cast time of your next Shadow Bolt or Incinerate spell by 100%. This effect lasts 8 sec and will not occur more than once every 8 seconds.
  - WotLK rank 3: Increases your critical strike chance with spells by an additional 3% and gives you a 25% chance when hit by a physical attack to reduce the cast time of your next Shadow Bolt or Incinerate spell by 100%. This effect lasts 8 sec and will not occur more than once every 8 seconds.
- **Improved Immolate** (3 ranks) - row 4 -> tier 3 - MATCH warlock_destruction_improved_immolate  [ours is scalar]
  - WotLK rank 1: Increases the damage done by your Immolate spell by 10%.
  - WotLK rank 3: Increases the damage done by your Immolate spell by 30%.
- **Devastation** (1 rank) - row 4 -> tier 3 - MATCH warlock_destruction_devastation  [ours is scalar]
  - requires: Ruin
  - needs: proc-chance, crit
  - WotLK rank 1: Increases the critical strike chance of your Destruction spells by 5%.
- **Nether Protection** (3 ranks) - row 5 -> tier 3 - MATCH warlock_destruction_nether_protection  [ours is scalar]
  - needs: proc-chance, duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: After being hit with a spell, you have a 10% chance to gain Nether Protection, reducing all damage by that spell school by 30% for 8 sec.
  - WotLK rank 3: After being hit with a spell, you have a 30% chance to gain Nether Protection, reducing all damage by that spell school by 30% for 8 sec.
- **Emberstorm** (5 ranks) - row 5 -> tier 3 - MATCH warlock_destruction_emberstorm  [ours is scalar]
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the damage done by your Fire spells by 3% and reduces the cast time of your Incinerate spell by 0.05 sec.
  - WotLK rank 5: Increases the damage done by your Fire spells by 15% and reduces the cast time of your Incinerate spell by 0.25 sec.
- **Conflagrate** (1 rank) - row 6 -> tier 4 - MATCH warlock_destruction_conflagrate
  - requires: Improved Immolate
  - needs: dot-hot
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Consumes an Immolate or Shadowflame effect on the enemy target to instantly deal damage equal to 60% of your Immolate or Shadowflame, and causes an additional 40% damage over 6 sec.
- **Soul Leech** (3 ranks) - row 6 -> tier 4 - MATCH warlock_destruction_soul_leech
  - needs: proc-chance, heal
  - WotLK rank 1: Gives your Shadow Bolt, Shadowburn, Chaos Bolt, Soul Fire, Incinerate, Searing Pain and Conflagrate spells a 10% chance to return health equal to 20% of the damage caused.
  - WotLK rank 3: Gives your Shadow Bolt, Shadowburn, Chaos Bolt, Soul Fire, Incinerate, Searing Pain and Conflagrate spells a 30% chance to return health equal to 20% of the damage caused.
- **Pyroclasm** (3 ranks) - row 6 -> tier 4 - MATCH warlock_destruction_pyroclasm
  - needs: duration-window
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When you critically strike with Searing Pain or Conflagrate, your Fire and Shadow spell damage is increased by 2% for 10 sec.
  - WotLK rank 3: When you critically strike with Searing Pain or Conflagrate, your Fire and Shadow spell damage is increased by 6% for 10 sec.
- **Shadow and Flame** (5 ranks) - row 7 -> tier 4 - MATCH warlock_destruction_shadow_and_flame  [ours is scalar]
  - WotLK rank 1: Your Shadow Bolt, Shadowburn, Chaos Bolt and Incinerate spells gain an additional 4% of your bonus spell damage effects.
  - WotLK rank 5: Your Shadow Bolt, Shadowburn, Chaos Bolt and Incinerate spells gain an additional 20% of your bonus spell damage effects.
- **Improved Soul Leech** (2 ranks) - row 7 -> tier 4 - NEW - we have no talent of this name
  - requires: Soul Leech
  - needs: proc-chance, resource-grant, duration-window, pet
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Your Soul Leech effect also restores mana to you and your summoned demon equal to 1% of maximum mana, and has a 50% chance to grant up to 10 party or raid members mana regeneration equal to 1% of maximum mana per 5 sec. Lasts for 15 sec.
  - WotLK rank 2: Your Soul Leech effect also restores mana to you and your summoned demon equal to 2% of maximum mana, and has a 100% chance to grant up to 10 party or raid members mana regeneration equal to 1% of maximum mana per 5 sec. Lasts for 15 sec.
- **Backdraft** (3 ranks) - row 8 -> tier 5 - MATCH warlock_destruction_destruction_mastery
  - requires: Conflagrate
  - needs: cooldown-change
  - **BLOCKED**: BLOCKED:cast-time - needs a substitute mechanic
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: When you cast Conflagrate, the cast time and global cooldown of your next three Destruction spells is reduced by 10%. Lasts 15 sec.
  - WotLK rank 3: When you cast Conflagrate, the cast time and global cooldown of your next three Destruction spells is reduced by 30%. Lasts 15 sec.
- **Shadowfury** (1 rank) - row 8 -> tier 5 - MATCH warlock_destruction_shadowfury
  - needs: duration-window, stun, aoe
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Shadowfury is unleashed, causing 343 to 407 Shadow damage and stunning all enemies within 8 yds for 3 sec.
- **Empowered Imp** (3 ranks) - row 8 -> tier 5 - MATCH warlock_destruction_empowered_imp
  - needs: proc-chance
  - TURN-BASED: real seconds -> turns (~3 sec per turn; re-derive, do not divide)
  - WotLK rank 1: Increases the damage done by your Imp by 10%, and all critical hits done by your Imp have a 33% chance to increase your spell critical hit chance for your next spell by 100%. This effect lasts 8 sec.
  - WotLK rank 3: Increases the damage done by your Imp by 30%, and all critical hits done by your Imp have a 100% chance to increase your spell critical hit chance for your next spell by 100%. This effect lasts 8 sec.
- **Fire and Brimstone** (5 ranks) - row 9 -> tier 5 - MATCH warlock_destruction_fire_and_brimstone  [ours is scalar]
  - needs: proc-chance, crit
  - WotLK rank 1: Increases the damage done by your Incinerate and Chaos Bolt spells to targets afflicted by your Immolate by 2%, and the critical strike chance of your Conflagrate spell is increased by 5%.
  - WotLK rank 5: Increases the damage done by your Incinerate and Chaos Bolt spells to targets afflicted by your Immolate by 10%, and the critical strike chance of your Conflagrate spell is increased by 25%.
- **Chaos Bolt** (1 rank) - row 10 -> tier 6 - MATCH warlock_destruction_chaos_bolt
  - WotLK rank 1: Sends a bolt of chaotic fire at the enemy, dealing 837 to 1061 Fire damage. Chaos Bolt cannot be resisted, and pierces through all absorption effects.
