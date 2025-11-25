# Maya's Veggie Run

A fun endless runner game where Maya runs to collect healthy veggies, avoid obstacles, and find her beloved puppy!

## Play Now!

**[Play in your browser!](https://mjons.github.io/mayas-veggie-run/)**

## About the Game

Maya loves veggies and her puppy! Help her run through a colorful world collecting healthy foods while avoiding rocks and other obstacles.

### Game Features

- **Endless Runner Gameplay** - The game gets faster as you play!
- **Collect Veggies** - Gather healthy foods to maintain Maya's energy
- **Avoid Obstacles** - Jump over rocks to keep running
- **Find the Puppy** - Encounter Maya's adorable puppy for a heartwarming hug moment
- **Special Characters** - Watch out for unicorns and dangling Elmos!
- **Dynamic Difficulty** - Miss veggies and the game speeds up!
- **Sound Effects & Music** - Full audio experience with background music

### How to Play

- **SPACE** - Jump
- **Goal** - Collect veggies to maintain energy
- **Warning** - Don't miss veggies or the game speeds up!
- **Special** - Find the puppy for full health restoration

## Running Locally

### Desktop Version (Python)

Requirements:
- Python 3.7+
- Pygame

```bash
# Install dependencies
pip install pygame

# Run the game
python Maya.py
```

### Web Version

See [WEB_DEPLOYMENT.md](WEB_DEPLOYMENT.md) for detailed instructions on building and deploying the web version.

Quick start (requires Python 3.8+):
```bash
pip install pygbag
pygbag main.py
```

## Project Structure

```
MayasAdventure/
├── main.py              # Web version (with asyncio)
├── Maya.py              # Desktop version
├── assets/
│   ├── images/          # All game sprites and backgrounds
│   └── sounds/          # Sound effects and music
├── PrepSprites/         # Sprite processing tools
├── generate_sounds.py   # Sound effect generator
├── README.md            # This file
└── WEB_DEPLOYMENT.md    # Web deployment guide
```

## Game Mechanics

### Energy System
- Start with 100% energy
- Collecting food: +5% energy
- Hitting obstacles: -2% energy
- Finding puppy: Restore to 100% energy
- Game over when energy reaches 0%

### Difficulty Scaling
- Game speed increases when you hit obstacles
- Missing vegetables makes the game harder
- The longer you play, the faster things spawn

### Special Characters
- **Puppy** - Maya's best friend! Grants full health and a special moment
- **Unicorn** - Runs faster than Maya
- **Elmo** - Dangles from above on a string with swaying motion

## Credits

- **Game Design & Development** - Built with Pygame
- **Sprites** - Custom sprite sheets processed with custom pipeline
- **Sound Effects** - Generated using numpy-based synthesizer
- **Background Music** - "Big and Strong"

## License

This is a personal project created for fun and learning.

## Technical Details

- Built with **Pygame**
- Web version uses **pygbag** (Pygame to WebAssembly)
- Custom sprite processing pipeline
- Procedural sound generation
- Asyncio support for web deployment

---

Made with ❤️ for Maya
