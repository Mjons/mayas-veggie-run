import pygame
import os

# --- CONFIGURATION ---
FILENAME = 'maya_sheet.png'  # Make sure your image is named this
OUTPUT_FOLDER = 'processed_sprites'
ROWS = 7
COLS = 5
# We will auto-detect the sprite size based on the image size / cols

def slice_and_save():
    pygame.init()
    
    # 1. Load the Sheet
    try:
        sheet = pygame.image.load(FILENAME)
    except:
        print(f"Error: Could not find {FILENAME}. Please make sure the image is in the same folder as this script.")
        return

    sheet_w, sheet_h = sheet.get_size()
    sprite_w = sheet_w // COLS
    sprite_h = sheet_h // ROWS

    print(f"Sheet Size: {sheet_w}x{sheet_h}")
    print(f"Calculated Sprite Size: {sprite_w}x{sprite_h}")

    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    # 2. Slice and Save
    frames = []
    print("Slicing sprites...")
    
    screen = pygame.display.set_mode((400, 400))
    pygame.display.set_caption("Sprite Preview - Press SPACE to change Row")
    
    # Extract all frames into a 2D list (List of Rows, where each Row is a list of Images)
    all_animations = []
    
    for row in range(ROWS):
        current_row_frames = []
        for col in range(COLS):
            # Create a blank surface
            frame = pygame.Surface((sprite_w, sprite_h), pygame.SRCALPHA)
            # Copy the specific area from the sheet onto the blank surface
            rect = pygame.Rect(col * sprite_w, row * sprite_h, sprite_w, sprite_h)
            frame.blit(sheet, (0, 0), rect)
            
            current_row_frames.append(frame)
            
            # Save to file
            # Naming convention: maya_row_0_col_0.png
            save_name = f"{OUTPUT_FOLDER}/maya_row_{row}_col_{col}.png"
            pygame.image.save(frame, save_name)
            
        all_animations.append(current_row_frames)

    print(f"Done! Saved all frames to folder: '{OUTPUT_FOLDER}'")
    print("Starting Preview Window...")

    # 3. Preview Loop
    clock = pygame.time.Clock()
    running = True
    current_row = 2 # Start with the Run animation (Row 2 based on your image)
    frame_index = 0
    timer = 0
    
    font = pygame.font.SysFont('Arial', 20)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    current_row = (current_row + 1) % ROWS
                    frame_index = 0

        # Animation Logic
        timer += 1
        if timer > 10: # Speed of animation
            frame_index = (frame_index + 1) % COLS
            timer = 0

        # Draw
        screen.fill((50, 50, 50)) # Dark Grey background
        
        # Draw the sprite scaled up 2x so we can see it clearly
        current_sprite = all_animations[current_row][frame_index]
        scaled_sprite = pygame.transform.scale(current_sprite, (sprite_w * 4, sprite_h * 4))
        
        # Center it
        x_pos = 200 - (sprite_w * 2)
        y_pos = 200 - (sprite_h * 2)
        screen.blit(scaled_sprite, (x_pos, y_pos))

        # Text
        text = font.render(f"Previewing Row: {current_row} (Press SPACE to switch)", True, (255, 255, 255))
        screen.blit(text, (10, 10))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    slice_and_save()