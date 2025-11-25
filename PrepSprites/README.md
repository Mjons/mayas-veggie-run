# Maya's Sprite Pipeline

A complete toolkit for processing sprite sheets from raw/AI-generated images to game-ready assets.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install pygame pillow numpy
   ```

2. **Add your sprite sheet to the `input/` folder**

3. **Run the pipeline:**
   ```bash
   python sprite_pipeline.py
   ```

4. **Follow the interactive prompts!**

## What It Does

The pipeline takes you through these steps:

### 1. Input Selection
- Automatically detects sprite sheets in the `input/` folder
- Choose which one to process

### 2. Cleaning & Optimization (Optional)
- **Alpha thresholding**: Removes fuzzy AI-generated edges
- **Downscaling**: Resizes to target pixel art size
- **Color quantization**: Reduces to pixel-art color palette
- **Contrast/Saturation boost**: Makes sprites pop
- **Orphan pixel removal**: Cleans up noise

### 3. Grid Configuration
- Define how many rows (animations) and columns (frames) your sprite sheet has
- Auto-calculates frame size

### 4. Frame Slicing
- Extracts all individual frames from the sprite sheet

### 5. Interactive Preview
- See your animations in action!
- **Controls:**
  - `SPACE`: Switch between animation rows
  - `UP/DOWN`: Adjust animation speed
  - `LEFT/RIGHT`: Navigate frames manually
  - `ESC`: Continue to export

### 6. Export
- Saves optimized sprite sheet to `output/` folder
- Creates a grid preview for verification

### 7. Code Generation
- Generates ready-to-use code snippets
- Copy/paste directly into your game!

## File Structure

```
PrepSprites/
├── sprite_pipeline.py    # Main pipeline tool
├── input/                # Put your raw sprites here
├── output/               # Processed sprites appear here
├── prep.py              # Legacy: Frame slicer only
├── spriteConverter/
│   └── pixel_fixer.py   # Legacy: Pixel cleanup only
└── README.md            # This file
```

## Tips for Best Results

### AI-Generated Sprites
- Use the cleaning step (answer 'yes')
- Start with target width 512 or 1024
- Use 16-32 colors for best pixel art look
- Boost contrast to 1.2-1.5 for vibrant colors

### Hand-Drawn Sprites
- Skip cleaning if already pixel-perfect
- Use cleaning only if you need color reduction

### Animation Rows
When previewing, note which row is which animation:
- Row 0: Idle
- Row 1: Running
- Row 2: Jumping
- etc.

Label these in your code for easy reference!

## Common Issues

**"No sprite sheets found"**
- Make sure your image is in the `input/` folder
- Supported formats: PNG, JPG, JPEG, WEBP, BMP

**Sprite looks blurry**
- Increase target width in cleaning step
- Try different num_colors values

**Animations too fast/slow in game**
- Adjust `animation_speed` in your game code (try 0.1 to 0.3)

**Colors look washed out**
- Increase contrast and saturation during cleaning

## Using Sprites in Your Game

After export, copy the sprite from `output/` to your game's `assets/images/` folder.

Then use the generated code snippet! It includes:
- How to load the sprite sheet
- How to animate it
- Frame management code

## Examples

### Processing Maya Character
1. Export Maya sprite from AI generator → `input/maya_character.png`
2. Run pipeline
3. Clean with: width=512, colors=16, contrast=1.2
4. Set grid: 7 rows × 5 columns
5. Preview and verify
6. Export → `output/maya_character_processed.png`
7. Copy to game → `assets/images/mayaSprite.png`

### Processing Pet Animations
1. AI pet sprite → `input/pet.png`
2. Run pipeline
3. Clean with: width=256, colors=12
4. Set grid: 2 rows × 5 columns
5. Export and use!

## Advanced Usage

### Batch Processing
Want to process multiple sprites? Run the pipeline multiple times, or modify the code to loop through all input files.

### Custom Parameters
Edit the configuration constants at the top of `sprite_pipeline.py`:
- `INPUT_FOLDER`: Change input directory
- `OUTPUT_FOLDER`: Change output directory
- `PREVIEW_SCALE`: Adjust preview window zoom

## Support

Issues? Check:
1. Dependencies installed? `pip list | grep -E "pygame|pillow|numpy"`
2. Files in correct folders?
3. Image format supported?

Still stuck? The script shows helpful error messages!

---

**Built for Maya's Veggie Run** 🥕
