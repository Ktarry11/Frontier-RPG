# Talent & Ability System Rebuild — WoW Classic Alignment

## Current State
- 89 abilities across 9 WoW classes (mostly hand-authored)
- 30 talent trees (27 WoW + 3 Stormbringer CoA)
- Talents stored as JSON with hex coordinates (for visual layout)
- No actual prerequisite enforcement
- Talent effects applied as raw stat bonuses (no ability-specific modifiers)

## Issues to Fix

### 1. Ability Ranks & Level Requirements
**Current**: Abilities have multiple ranks baked into `ranks` array with `level_req` per rank.
**Problem**: Level requirements are arbitrary; not matching WoW.

**WoW Reality** (Warrior Attack for example):
- Rank 1: Level 1
- Rank 2: Level 10
- Rank 3: Level 20
- Rank 4: Level 30
- ... up to Rank 11 at level 60

**Solution**:
- Extract level-req progression from Wowpedia for all 9 classes
- Rebuild ability JSON with EXACT WoW Classic level progression
- Test: all abilities unlockable match WoW leveling curve

### 2. Talent Prerequisites
**Current**: Talents have a `connected_to` list showing visually-adjacent nodes, but no enforcement.
**Problem**: You can take Mortal Strike without Sweeping Strikes; or take Death Wish without 31 points in tree.

**WoW Rules**:
1. Can only spend points in Tier N if 5 points spent in Tier N-1
2. Some talents REQUIRE another talent to be 1/1 or fully ranked
3. Tree cap: 51 total points across 3 trees, level 60

**Solution**:
- Rebuild talent JSON structure: track `requires` field (talent_id + required_ranks)
- Enforce in talentscreen_screen.py: check all prerequisites before allowing point spend
- Implement 51-point budget with tier unlocks

### 3. Talent Effects That Work
**Current**: Talents apply raw effects like `{"ability_warrior_heroic_strike_cost": 1}` but:
- This is only checked if ability's `_talent()` lookup works
- The lookup is in combat/abilities.py and only queries a handful of keys
- Buff/debuff talents produce stat bonuses that don't actually affect ability scaling

**WoW Examples**:
- "Improved Heroic Strike" → reduces Rage cost by 1 per rank (works!)
- "Anger Management" → generates 1 Rage every 3 seconds (passive, untested)
- "Impale" → increases crit strike damage by 10% per rank on specific abilities
- "Deep Wounds" → physical attacks trigger a bleed DoT

**Solution**:
- Audit current talent effects: mark what actually works vs. what's cosmetic
- Implement missing passive effects (Anger Management, Auto Attack modifiers, etc.)
- Test each talent in combat before declaring a tree "done"

### 4. Missing Starter Abilities
**WoW provides these free at level 1 or trainer acquisition**:
- Warrior: Battle Stance, Heroic Strike (level 1); then level-gated trainer abilities
- Priest: Power Word: Shield (level 1!), Smite; but no instant heal until level 8+
- Rogue: Backstab, Evasion (level 1); Sinister Strike at 4
- Mage: Fireball (level 1); Frost Bolt (level 4)
- Shaman: Lightning Bolt (level 1)
- Etc.

**Current State**:
- We have abilities but not sure if level requirements match

**Solution**:
- Cross-check our JSON vs Wowpedia for all 9 classes
- Ensure level 1 abilities are actually teachable at level 1
- Mark any ability that should come from a quest/NPC

## Implementation Order

### Phase 1: Ability Audit & Rebuild (this session)
1. For each of the 9 WoW classes, fetch correct level progression from Wowpedia
2. Rewrite `data/abilities/{class}.json` with EXACT Blizzard level requirements
3. Smoke test: create level-1 character, check ability list matches WoW
4. Flag any abilities we're missing (e.g., Priest's Power Word: Shield at level 1)

### Phase 2: Talent Tree Audit & Rebuild
1. Extract full talent tree structure from Wowpedia for all 9 classes
2. Build `talent_tree_structure.json` with:
   - Talent ID, name, description
   - Ranks, effects
   - Prerequisites (if any): `requires: {"talent_id": min_ranks}`
   - Tier (0-10, where tier N unlocks after 5 points in tier N-1)
3. Rebuild all 30 talent JSON files to match WoW structure exactly
4. Test: Talent screen enforces prerequisites and tier unlocks

### Phase 3: Talent Effects Implementation
1. Go talent-by-talent through all 3 Warrior trees (78 talents total)
2. Audit each effect: "does this work in combat?"
3. For each broken talent, either:
   - Fix the implementation (add to `_talent()` lookup)
   - Remove it if it's a dupe or unnecessary
   - Mark as "WIP" if complex (e.g., passive procs)

### Phase 4: Integration Testing
1. Level a character 1-60 through the talent gains they'd get in real WoW
2. Verify each level's new ability actually becomes available
3. Verify each talent point spends correctly
4. Combat test: use a talent-dependent build (e.g., Fury Warrior with all Flurry ranks)

## Why This Matters
- Current talent system is cosmetic — you CAN pick Mortal Strike at level 10 before Sweeping Strikes exists
- Ability level requirements are loose guesses
- Players will notice immediately that class progression doesn't match their WoW muscle memory
- Talents not working breaks the core progression fantasy

## Data Sources
- **Wowpedia** (most reliable): Full talent trees, ability tables by level
- **Classicdb.ch** (JS-rendered, limited programmatic access)
- **Wowhead** (seasonal data, sometimes confusing between expansion versions)

Use Wowpedia as the source of truth for Classic / Vanilla progression.
