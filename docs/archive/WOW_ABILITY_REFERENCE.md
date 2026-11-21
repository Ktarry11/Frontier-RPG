# WoW Classic Ability Reference — Source of Truth

## Warrior (from Wowpedia)
**Arms**:
- Battle Stance (1, default)
- Heroic Strike (1, default)
- Charge (4, trainer)
- Rend (4, trainer)
- Thunder Clap (6, trainer)
- Hamstring (8, trainer)
- Overpower (12, trainer)
- Mocking Blow (16, trainer)
- Retaliation (20, trainer)

**Fury**:
- Battle Shout (1, trainer)
- Demoralizing Shout (14, trainer)
- Cleave (20, trainer)
- Intimidating Shout (22, trainer)
- Execute (24, trainer)
- Challenging Shout (26, trainer)
- Berserker Stance (30, quest)
- Intercept (30, quest)
- Slam (30, trainer)
- Berserker Rage (32, trainer)
- Whirlwind (36, trainer)
- Pummel (38, trainer)
- Recklessness (50, trainer)

**Protection**:
- Bloodrage (10, trainer)
- Defensive Stance (10, quest)
- Sunder Armor (10, quest)
- Taunt (10, quest)
- Shield Bash (12, trainer)
- Revenge (14, trainer)
- Shield Block (16, trainer)
- Disarm (18, trainer)
- Shield Wall (28, trainer)

## Priest (from Wowpedia - Classic)
**Holy**:
- Lesser Heal (1, default)
- Smite (1, default)
- Shadow Word: Pain (4, trainer)
- Fade (8, trainer)
- Renew (8, trainer)
- Desperate Prayer (10, quest)
- Resurrection (10, trainer)
- Cure Disease (14, trainer)
- Heal (16, trainer)
- Holy Fire (20, trainer)
- Fear Ward (20, quest)
- Flash Heal (20, trainer)
- Prayer of Healing (30, trainer)
- Abolish Disease (32, trainer)
- Greater Heal (40, trainer)

**Discipline**:
- Power Word: Fortitude (1, trainer)
- Power Word: Shield (6, trainer)
- Starshards (10, quest)
- Inner Fire (12, trainer)
- Dispel Magic (18, trainer)
- Elune's Grace (20, quest)
- Feedback (20, quest)
- Shackle Undead (20, trainer)
- Mana Burn (24, trainer)
- Levitate (34, trainer)
- Prayer of Fortitude (48, codex)
- Prayer of Spirit (60, trainer)

**Shadow**:
- Shadow Word: Pain (4, trainer)
- Fade (8, trainer)
- Hex of Weakness (10, quest)
- Mind Blast (10, trainer)
- Touch of Weakness (10, quest)
- Psychic Scream (14, trainer)
- Devouring Plague (20, quest)
- Mind Soothe (20, trainer)
- Shadowguard (20, quest)
- Mind Vision (22, trainer)
- Mind Control (30, trainer)
- Shadow Protection (30, trainer)
- Prayer of Shadow Protection (56, codex)

## Critical Differences from Our Current Data
1. **Power Word: Shield is level 6, not 1** (big deal for Priest balance)
2. **Many abilities come from quests, not trainers** (Defensive Stance, Berserker Stance, Fear Ward, etc.)
3. **Priests start with Lesser Heal + Smite, NOT Power Word: Heal**
4. **Shackle Undead is level 20, requires trainer visit** (not auto-learned)
5. **Multiple abilities locked behind quest items (Codex)** 

## Next Steps
1. Fetch full ability lists for Rogue, Mage, Warlock, Druid, Paladin, Hunter, Shaman
2. Build master JSON with all level requirements
3. Flag quest-only abilities and trainer locations
4. Audit current ability ranks to see if we have rank data for each
5. Test character creation: level-1 warrior should only see Heroic Strike + Battle Stance

## Rogue (Classic era, from warcraft.wiki.gg)
**Assassination**:
- Eviscerate (1, default)
- Slice and Dice (10, trainer)
- Expose Armor (14, trainer)
- Garrote (14, trainer)
- Ambush (18, trainer)
- Rupture (20, trainer)
- Cheap Shot (26, trainer)
- Kidney Shot (30, trainer)

**Combat**:
- Sinister Strike (1, default)
- Backstab (4, trainer)
- Gouge (6, trainer)
- Evasion (8, trainer)
- Sprint (10, trainer)
- Kick (12, trainer)
- Feint (16, trainer)

**Subtlety**:
- Stealth (1, trainer)
- Pick Pocket (4, trainer)
- Sap (10, trainer)
- Distract (22, trainer)
- Vanish (22, trainer)
- Detect Traps (24, trainer)
- Disarm Trap (30, trainer)
- Blind (34, trainer)
- Safe Fall (40, trainer)

**General**: Dual Wield (10), Parry (12), Pick Lock (16), Poisons (20, quest)

**Note**: Our current data has Rogue starting with "Attack" + "Sinister Strike" + "Backstab" — 
Backstab should be level 4, not level 1! Our current Rogue kit needs fixing.

## Data Gathering Status
- ✅ Warrior — full Classic table pulled
- ✅ Priest — full Classic table pulled  
- ✅ Rogue — full Classic table pulled (abilities + talents)
- ⏳ Mage — not yet pulled
- ⏳ Warlock — not yet pulled
- ⏳ Druid — not yet pulled
- ⏳ Paladin — not yet pulled
- ⏳ Hunter — not yet pulled
- ⏳ Shaman — not yet pulled

## Source note
warcraft.wiki.gg works reliably (wowpedia.fandom.com returns 402 errors).
Use pattern: https://warcraft.wiki.gg/wiki/{Class}_abilities_(Classic)

## Mage (Classic era, from warcraft.wiki.gg) — combat-relevant only
**Arcane**:
- Arcane Intellect (1, trainer)
- Conjure Water (4, trainer)
- Conjure Food (6, trainer)
- Arcane Missiles (8, trainer)
- Polymorph (8, trainer)
- Dampen Magic (12, trainer)
- Slow Fall (12, trainer)
- Arcane Explosion (14, trainer)
- Detect Magic (16, trainer)
- Amplify Magic (18, trainer)
- Remove Lesser Curse (18, trainer)
- Blink (20, trainer)
- Evocation (20, trainer)
- Mana Shield (20, trainer)
- Counterspell (24, trainer)
- Mage Armor (34, trainer)
(Portals/Teleports/Conjure Mana Gems skipped — travel/utility, not combat)

**Fire**:
- Fireball (1, default)
- Fire Blast (6, trainer)
- Flamestrike (16, trainer)
- Fire Ward (20, trainer)
- Scorch (22, trainer)

**Frost**:
- Frost Armor (1, default)
- Frostbolt (4, trainer)
- Frost Nova (10, trainer)
- Blizzard (20, trainer)
- Frost Ward (22, trainer)
- Cone of Cold (26, trainer)
- Ice Armor (30, trainer)

**Note**: Our current Mage kit has "Fireball" as level-1 default — correct!
But missing Frost Armor / Frost Armor as a level-1 default option, and 
Frostbolt should be level 4 not whatever we have. Need audit.

## Data Gathering Status (Updated)
- ✅ Warrior, Priest, Rogue, Mage — full Classic tables pulled
- ⏳ Warlock, Druid, Paladin, Hunter, Shaman — still needed

Given token budget, remaining classes will use faster targeted fetches 
(skip teleport/portal/quest-item tables, focus on core combat kit).

## Warlock (Classic era) — combat-relevant only
**Affliction**:
- Corruption (4, trainer)
- Curse of Weakness (4, trainer)
- Life Tap (6, trainer)
- Curse of Agony (8, trainer)
- Fear (8, trainer)
- Drain Soul (10, trainer)
- Curse of Recklessness (14, trainer)
- Drain Life (14, trainer)
- Drain Mana (24, trainer)
- Curse of Tongues (26, trainer)
- Curse of the Elements (32, trainer)
- Howl of Terror (40, trainer)
- Death Coil (42, trainer)
- Curse of Doom (60, trainer)

**Demonology**:
- Demon Skin (1, default)
- Summon Imp (1, class quest)
- Summon Voidwalker (10, quest)
- Health Funnel (12, trainer)
- Demon Armor (20, trainer)
- Summon Succubus (20, quest)
- Summon Felhunter (30, quest)

**Destruction**:
- Shadow Bolt (1, default)
- Immolate (1, trainer)
- Searing Pain (18, trainer)
- Rain of Fire (20, trainer)
- Hellfire (30, trainer)
- Soul Fire (48, trainer)

**Note**: Warlock kit is pet-centric — Imp/Voidwalker/Succubus/Felhunter each 
have their own separate ability lists. Our engine likely doesn't model pets 
yet; this is worth flagging as a design gap.

## Data Gathering Status (Updated)
- ✅ Warrior, Priest, Rogue, Mage, Warlock — pulled
- ⏳ Druid, Paladin, Hunter, Shaman — still needed

## Druid (partial — Classic era, from ZAM wiki)
- Wrath (1, default) — nature damage
- Moonfire (4) — instant, front-loaded arcane dmg + DoT
- Rejuvenation (4) — instant HoT
- Entangling Roots, Faerie Fire, Hibernate, Mark of the Wild, Thorns — untimed, need level lookup
- Regrowth (10) — heal + HoT
- Nature's Grasp (10, Balance talent)
- Cure Poison (14, quest-gated)
- Rebirth (20) — druid's battle-res
- Faerie Fire (18) — armor debuff
**Feral**: Bear Form, Cat Form, Growl, Enrage, Bash, Maul, Claw, Demoralizing Roar, 
Prowl, Rip, Shred, Rake, Swipe, Tiger's Fury (levels not confirmed — need dedicated fetch)

**STATUS: INCOMPLETE** — need a dedicated fetch pass for exact levels on 
Feral abilities and full Balance/Restoration confirmation.

## STILL NEEDED (not yet pulled)
- Paladin — full ability table
- Hunter — full ability table  
- Shaman — full ability table
- Druid — complete the Feral levels, confirm Balance/Restoration

## Talent trees NOT yet pulled for any class
All 9 classes need their talent prerequisite chains, tier-lock structure, 
and the 51-point budget rule documented. This is separate from ability 
level requirements and is its own large fetch pass.
