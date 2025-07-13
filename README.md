# Tiny Sword Survival

A 2D survival action game built with Python and Pygame where you fight waves of enemies with your sword.

## Features

### Core Gameplay
- **Health System**: Player and enemies have health bars with damage and healing mechanics
- **Wave-based Combat**: Fight increasingly difficult waves of enemies
- **Enemy AI**: Different enemy types with unique behaviors (Goblins, Archers, Warriors)
- **Combat System**: Sword attacks with combo system and directional attacks

### Power-ups
- **Health**: Instant healing
- **Speed**: Temporary speed boost
- **Damage**: Temporary damage multiplier
- **Invulnerability**: Temporary invincibility
- **Rapid Fire**: Faster attack speed

### Audio System
- **Sound Effects**: Attack sounds, enemy death, power-up pickups, etc.
- **Background Music**: Atmospheric background music
- **Volume Controls**: Adjustable SFX and music volume

### User Interface
- **Main Menu**: Start game, settings, quit
- **Pause Menu**: Resume, settings, return to main menu
- **Settings Menu**: Audio volume controls
- **HUD**: Health bar, wave counter, enemy count, active effects
- **Game Over Screen**: Final score and restart options

### Enemy Types
- **Goblins**: Fast, low health, close combat
- **Archers**: Medium speed, ranged attacks
- **Warriors**: Slow, high health, strong attacks

## Controls

- **WASD**: Move player
- **Mouse**: Attack in direction of mouse
- **ESC**: Pause game / Open menu
- **R**: Restart (on game over screen)
- **M**: Return to main menu (on game over screen)

## Installation

1. Install Python 3.7 or higher
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Game

```bash
python src/addfeaturetest.py
```

## Game Structure

```
src/
├── addfeaturetest.py      # Main game file
├── player.py              # Player class with health and combat
├── enemy_system.py        # Enemy AI and wave management
├── powerup_system.py      # Power-up spawning and effects
├── health_system.py       # Health and damage system
├── audio_system.py        # Sound effects and music
├── ui_system.py           # Menus and HUD
├── utils.py               # Animation and input systems
├── settings.py            # Game configuration
└── map_loader.py          # Map loading and rendering

assets/
├── Factions/              # Character sprites
├── UI/                    # UI elements
└── sounds/                # Audio files (auto-created)

tiled_map/                 # Map files
```

## Game Mechanics

### Health System
- Player starts with 100 health
- Enemies have different health values
- Invulnerability frames after taking damage
- Health bars show current status

### Wave System
- Waves get progressively harder
- More enemies spawn each wave
- Boss waves every 5 waves
- Enemies spawn around the player

### Power-up System
- Power-ups spawn randomly around the map
- Different types with varying effects
- Visual indicators for active effects
- Timed duration for temporary effects

### Combat System
- Directional sword attacks
- Combo system for multiple hits
- Attack cooldowns and recovery
- Collision detection for hits

## Development

The game is built with a modular architecture:
- Each system is self-contained
- Easy to add new features
- Clean separation of concerns
- Extensible design

## Future Enhancements

- More enemy types
- Different weapons
- Level progression
- Save/load system
- Multiplayer support
- More power-up types
- Achievement system 
>>>>>>> master
