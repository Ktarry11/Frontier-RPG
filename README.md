# Frontier RPG - Phase 0

An open-world party-based RPG built in Python + Pygame.

## Setup

### Requirements
- Python 3.8+
- Pygame

### Installation

1. Clone/download this folder
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Game

```bash
python main.py
```

## Phase 0 Features

- **Main Menu**: New Game / Load Game / Quit
- **Character Creation**: Choose from 4 classes (Warrior, Shaman, Rogue, Priest)
- **Character Sheet**: View stats, health, mana
- **Overworld**: Explore 2 test zones, move between them
- **Combat**: FFX-style turn-based with continuous AGI-based turn meter
- **Save/Load**: Character data persists (versioned JSON format)

## Game Flow

1. Start → Main Menu
2. New Game → Character Creation (pick class)
3. Overworld → Explore zones
4. Search for Encounter → Combat
5. Win/Lose → Return to Overworld

## Technical Notes

- **Portable**: Entire folder uses relative paths. Copy to any computer and it works.
- **Placeholder Art**: All visuals are rectangles and text (no sprites yet — Phase 11)
- **Clean Architecture**: Modular systems for easy expansion in future phases
- **Versioned Saves**: Save format includes version number for forward compatibility

## Roadmap

- Phase 0: Foundation (current)
- Phase 1: Character progression
- Phase 2: Zones & world building
- Phase 3: Combat polish
- Phase 4: Skills & abilities
- Phase 5-12: See handoff document

---

Built with care. Scope is your enemy. Ship early, iterate often.
