# Pocket Creature Adventure

A small top-down 2D Pokémon-inspired game built with [pygame](https://www.pygame.org/).
Roam the overworld, walk into tall grass to trigger random encounters, and battle
wild creatures with a turn-based combat system.

## Features

- **Exploration:** Move a trainer around a tile-based overworld using the arrow keys.
- **Random encounters:** Walking through tall grass has a chance to trigger a battle.
- **Turn-based battles:** Select from multiple moves, watch HP bars update, and choose to run away.
- **Persistent party:** Your partner keeps its HP between encounters and is healed when you are defeated.

## Getting started

1. Create and activate a virtual environment (optional but recommended).
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Launch the game:

   ```bash
   python -m src.game
   ```

The game opens in a window. Use the arrow keys to explore. During battles, press
`1`/`2` (or `A`) to select a move or `R` to try to run away. Press `Space` or
`Enter` to advance dialogue messages.

## Development tips

- All source code lives in the `src/` directory.
- The overworld layout is defined in `MAP_LAYOUT` inside `src/game.py` — update
  the strings to design your own map.
- Add new Pokémon or moves by editing `src/pokemon.py`.

Have fun building your own Pokémon-inspired adventure!
