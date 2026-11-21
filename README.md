# Frontier RPG

A WoW Classic-inspired, party-based, turn-based RPG in Python and Pygame. Earth transplants, a merged world, levels
1 to 60, dungeons with heroics, reputation, crafting, recruits and an auction house.

## Running it

```bash
pip install -r requirements.txt
python main.py
```

Python 3.10 or newer. Saves are versioned JSON, and the folder runs from anywhere (every path is relative).

## Where things are

| Folder | What's in it |
|---|---|
| `main.py`, `core/` | the entry point and the game-state machine |
| `world/` | zones, portals, quests, factions, heroics, vendors, the market |
| `entities/`, `combat/` | characters, items, loot; the turn-based combat engine |
| `ui/` | every screen |
| `data/` | the game's content as JSON: creatures, kits, encounters, quests, loot, items, NPCs |
| `assets/` | sliced art and baked map chunks (WebP), everything the game loads |
| `tools/` | the builders that write `data/` (`build_*`), the hand-built maps (`handbuilt_*`), the bakers (`bake_*`) and the checks (`qa_*`) |
| `docs/` | design briefs, build logs and art prompts; `docs/art_status.md` says which art is in and what's still to make |

## Checks

```bash
PYTHONPATH=. python3 tools/qa_<name>.py               # one check
QA_JOBS=3 bash tools/run_qa.sh qa_portals qa_heroic   # several in parallel; logs in /tmp/frontier_qa
```

## Art sources

Kyle's full art sheets live on the `art-sources` branch (`tools/*_sheets/`, `assets/**/_src/`), so `main` stays small.
Everything sliced from them is on `main`.

Old session handoffs and the Phase 0 notes are in `docs/archive/`.
