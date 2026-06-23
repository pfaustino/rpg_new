# RPG New — Architecture (full scope)

Minimal scaffold extracting `rpg_modules` items/UI from phaser_rpg. Inventory + equipment + item generator demo — no combat or quests.

## Stack

Python 3, Pygame 2.6+ (`setup.py` editable install).

## Entry

`python game.py` (monolithic ~455 lines).

## Layout

```
game.py              # Loop, map, inline Player/Inventory/Camera
rpg_modules/
  core/constants.py
  entities/player.py   # exists but game.py uses inline Player
  items/               # weapon, armor, consumable, generator
  ui/                  # inventory, equipment, item_generator
```

## Game loop

Poll events → UI mode gate (`explore` | equip `I` | generator `G`) → movement when no UI → draw map + overlays → `clock.tick(60)`.

## UI modes

`current_mode` blocks movement while inventory or item generator panels are open.

## Relationship to phaser_rpg

Subset of shared `rpg_modules` (~19 files vs full library). **Canonical RPG work:** prefer `phaser_rpg` or `simple_rpg` for full game loop.

## Persistence

None in this scaffold.

## Docs

`README.md`, `docs/adr/`.
