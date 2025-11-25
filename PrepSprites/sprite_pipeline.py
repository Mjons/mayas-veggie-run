"""
Maya's Sprite Pipeline
======================
Complete pipeline to process sprite sheets from AI/raw images to game-ready assets.

Usage:
    python sprite_pipeline.py

Then follow the interactive prompts!
"""

import pygame
import os
import sys
from PIL import Image, ImageEnhance
import numpy as np
from collections import Counter

# --- CONFIGURATION ---
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"
PREVIEW_SCALE = 4  # Scale factor for preview window

class SpritePipeline:
    def __init__(self):
        self.input_path = None
        self.output_path = None
        self.rows = None
        self.cols = None
        self.sprite_width = None
        self.sprite_height = None
        self.cleaned_image = None
        self.aligned_image = None  # Image after alignment
        self.sprite_offsets = {}  # Store sprite positions: (row, col) -> (x_offset, y_offset)
        self.frames = []

    def run(self):
        """Main pipeline execution"""
        print("\n" + "="*60)
        print("    MAYA'S SPRITE PIPELINE")
        print("="*60)

        # Step 1: Get input file
        if not self.get_input_file():
            return

        # Step 2: Ask if they want to clean/optimize the sprite
        if self.ask_yes_no("\nDo you want to clean/optimize this sprite? (AI cleanup, pixel-perfect)"):
            self.clean_sprite()
        else:
            # Just load the original
            self.cleaned_image = Image.open(self.input_path).convert("RGBA")

        # Step 3: Get grid dimensions
        self.get_grid_dimensions()

        # Step 4 & 5: Auto-align sprites and interactive adjustment (with loop back if needed)
        while True:
            if not hasattr(self, '_alignment_done'):
                self.auto_align_sprites()
                self.clean_cell_artifacts()
                self._alignment_done = True

            self.interactive_alignment_tool()

            # Step 6: Slice the sprite sheet (from aligned image)
            self.slice_sprite_sheet()

            # Step 7: Preview and adjust (can return to alignment if needed)
            should_continue = self.preview_animations()

            if should_continue:
                break  # Continue to export
            else:
                # User wants to go back to alignment
                print("\n↩ Returning to alignment tool...")
                continue

        # Step 7: Export final sprite sheet
        self.export_sprite_sheet()

        # Step 8: Generate code snippet
        self.generate_code_snippet()

        print("\n" + "="*60)
        print("    PIPELINE COMPLETE!")
        print("="*60)
        print(f"\nYour sprite is ready at: {self.output_path}")
        print("Copy it to your game's assets/images/ folder and use the code snippet above!")

    def get_input_file(self):
        """Get input sprite sheet from user"""
        print("\n--- STEP 1: Input File ---")

        # Create input folder if it doesn't exist
        if not os.path.exists(INPUT_FOLDER):
            os.makedirs(INPUT_FOLDER)

        # List available files
        files = [f for f in os.listdir(INPUT_FOLDER)
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.webp', '.bmp'))]

        if not files:
            print(f"\nNo sprite sheets found in '{INPUT_FOLDER}/' folder.")
            print("Please add your sprite sheet there and run again.")
            return False

        print(f"\nFound {len(files)} sprite sheet(s):")
        for i, f in enumerate(files, 1):
            print(f"  {i}. {f}")

        while True:
            try:
                choice = int(input(f"\nSelect file (1-{len(files)}): "))
                if 1 <= choice <= len(files):
                    self.input_path = os.path.join(INPUT_FOLDER, files[choice-1])
                    print(f"✓ Selected: {files[choice-1]}")
                    return True
            except ValueError:
                pass
            print("Invalid choice, try again.")

    def clean_sprite(self):
        """Clean and optimize sprite for pixel art"""
        print("\n--- STEP 2: Cleaning Sprite ---")

        # Get parameters
        target_width = self.ask_number("Target width in pixels", default=512, min_val=32, max_val=2048)
        num_colors = self.ask_number("Number of colors", default=16, min_val=4, max_val=256)
        contrast = self.ask_number("Contrast boost", default=1.2, min_val=0.5, max_val=2.0, is_float=True)
        saturation = self.ask_number("Saturation boost", default=1.2, min_val=0.5, max_val=2.0, is_float=True)

        print("\nProcessing...")

        img = Image.open(self.input_path).convert("RGBA")

        # 1. Alpha thresholding (hard cutout)
        datas = img.getdata()
        newData = []
        for item in datas:
            if item[3] < 128:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        img.putdata(newData)

        # 2. Downscale
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)
        img_small = img.resize((target_width, target_height), resample=Image.Resampling.BILINEAR)

        # 3. Enhance
        enhancer = ImageEnhance.Contrast(img_small)
        img_small = enhancer.enhance(contrast)
        enhancer = ImageEnhance.Color(img_small)
        img_small = enhancer.enhance(saturation)

        # 4. Color quantization
        rgb_img = img_small.convert("RGB")
        quantized = rgb_img.quantize(colors=num_colors, method=1, kmeans=num_colors, dither=Image.NONE)
        final_img = quantized.convert("RGBA")

        # 5. Re-apply alpha
        source_alpha = img_small.split()[-1]
        binary_alpha = source_alpha.point(lambda x: 255 if x > 100 else 0, mode='1')
        final_img.putalpha(binary_alpha)

        # 6. Remove orphan pixels
        final_img = self.remove_orphan_pixels(final_img)

        self.cleaned_image = final_img
        print("✓ Sprite cleaned and optimized!")

    def remove_orphan_pixels(self, img):
        """Remove noise pixels"""
        data = np.array(img)
        height, width = data.shape[:2]
        clean_data = data.copy()

        for y in range(1, height - 1):
            for x in range(1, width - 1):
                current_pixel = data[y, x]

                if current_pixel[3] == 0:
                    continue

                neighbors = [
                    data[y-1, x], data[y+1, x],
                    data[y, x-1], data[y, x+1]
                ]

                matches = sum(1 for n in neighbors if np.array_equal(n, current_pixel))

                if matches == 0:
                    valid_neighbors = [tuple(n) for n in neighbors if n[3] > 0]
                    if valid_neighbors:
                        most_common = Counter(valid_neighbors).most_common(1)[0][0]
                        clean_data[y, x] = most_common
                    else:
                        clean_data[y, x] = [0, 0, 0, 0]

        return Image.fromarray(clean_data)

    def get_grid_dimensions(self):
        """Get sprite sheet grid dimensions"""
        print("\n--- STEP 3: Grid Dimensions ---")

        width, height = self.cleaned_image.size
        print(f"Sprite sheet size: {width}x{height}")

        self.rows = self.ask_number("Number of rows (animations)", default=1, min_val=1, max_val=20)
        self.cols = self.ask_number("Number of columns (frames per animation)", default=5, min_val=1, max_val=20)

        self.sprite_width = width // self.cols
        self.sprite_height = height // self.rows

        print(f"✓ Each sprite will be {self.sprite_width}x{self.sprite_height} pixels")

    def auto_align_sprites(self):
        """Automatically align sprites within their grid cells"""
        print("\n--- STEP 4: Auto-Aligning Sprites ---")
        print("Detecting and aligning sprites in grid cells...")

        # Convert to numpy for easier manipulation
        img_array = np.array(self.cleaned_image)

        # Create a new image for aligned sprites
        aligned = Image.new('RGBA', self.cleaned_image.size, (0, 0, 0, 0))
        aligned_array = np.array(aligned)

        # Process each grid cell
        sprites_aligned = 0
        for row in range(self.rows):
            for col in range(self.cols):
                # Extract cell
                x_start = col * self.sprite_width
                y_start = row * self.sprite_height
                cell = img_array[y_start:y_start + self.sprite_height,
                                 x_start:x_start + self.sprite_width]

                # Find sprite bounding box (non-transparent pixels)
                alpha = cell[:, :, 3]
                non_transparent = np.where(alpha > 0)

                if len(non_transparent[0]) == 0:
                    # Empty cell
                    continue

                # Get bounding box
                min_y, max_y = non_transparent[0].min(), non_transparent[0].max()
                min_x, max_x = non_transparent[1].min(), non_transparent[1].max()

                sprite = cell[min_y:max_y+1, min_x:max_x+1]
                sprite_h, sprite_w = sprite.shape[:2]

                # Determine alignment
                # If sprite is in top 1/3 of original position, center vertically (jumping/flying)
                # Otherwise, align to bottom (standing/walking)
                sprite_center_y = min_y + sprite_h / 2
                is_jumping = sprite_center_y < (self.sprite_height / 3)

                if is_jumping:
                    # Center vertically
                    y_offset = (self.sprite_height - sprite_h) // 2
                else:
                    # Bottom align
                    y_offset = self.sprite_height - sprite_h

                # Center horizontally (or left align if too wide)
                if sprite_w <= self.sprite_width:
                    x_offset = (self.sprite_width - sprite_w) // 2
                else:
                    x_offset = 0

                # Store offset for this cell
                self.sprite_offsets[(row, col)] = (x_offset, y_offset)

                # Place sprite in aligned position
                dest_y = y_start + y_offset
                dest_x = x_start + x_offset
                aligned_array[dest_y:dest_y + sprite_h,
                            dest_x:dest_x + sprite_w] = sprite

                sprites_aligned += 1

        # Convert back to PIL Image
        self.aligned_image = Image.fromarray(aligned_array)
        print(f"✓ Auto-aligned {sprites_aligned} sprites")
        print("  - Bottom-aligned: ground sprites")
        print("  - Center-aligned: jumping/flying sprites")

    def clean_cell_artifacts(self):
        """Remove stray pixels outside each sprite's bounding box"""
        print("\nCleaning cell artifacts...")
        pixels_removed = self._clean_cell_artifacts_silent()
        print(f"✓ Removed {pixels_removed} stray pixels")

    def _clean_cell_artifacts_silent(self):
        """Remove stray pixels without printing (for use during interactive adjustments)"""
        img_array = np.array(self.aligned_image)
        cleaned = Image.new('RGBA', self.aligned_image.size, (0, 0, 0, 0))
        cleaned_array = np.array(cleaned)

        pixels_removed = 0

        for row in range(self.rows):
            for col in range(self.cols):
                # Extract cell
                x_start = col * self.sprite_width
                y_start = row * self.sprite_height
                cell = img_array[y_start:y_start + self.sprite_height,
                                x_start:x_start + self.sprite_width]

                # Find sprite bounding box
                alpha = cell[:, :, 3]
                non_transparent = np.where(alpha > 0)

                if len(non_transparent[0]) == 0:
                    # Empty cell, skip
                    continue

                # Get bounding box
                min_y, max_y = non_transparent[0].min(), non_transparent[0].max()
                min_x, max_x = non_transparent[1].min(), non_transparent[1].max()

                # Add small margin (2 pixels) to avoid clipping
                margin = 2
                min_y = max(0, min_y - margin)
                max_y = min(self.sprite_height - 1, max_y + margin)
                min_x = max(0, min_x - margin)
                max_x = min(self.sprite_width - 1, max_x + margin)

                # Create mask for valid region
                mask = np.zeros((self.sprite_height, self.sprite_width), dtype=bool)
                mask[min_y:max_y+1, min_x:max_x+1] = True

                # Count pixels that will be removed
                before_count = np.sum(alpha > 0)
                after_count = np.sum((alpha > 0) & mask)
                pixels_removed += (before_count - after_count)

                # Apply mask - only keep pixels within bounding box
                cleaned_cell = cell.copy()
                cleaned_cell[~mask] = [0, 0, 0, 0]  # Make pixels outside mask transparent

                # Place cleaned cell back
                cleaned_array[y_start:y_start + self.sprite_height,
                            x_start:x_start + self.sprite_width] = cleaned_cell

        self.aligned_image = Image.fromarray(cleaned_array)
        return pixels_removed

    def interactive_alignment_tool(self):
        """Interactive tool to manually adjust sprite positions"""
        print("\n--- STEP 5: Interactive Alignment ---")
        print("\nOpening alignment tool...")
        print("Controls:")
        print("  Click: Select cell (or erase if in eraser mode)")
        print("  Arrow keys: Move sprite 1px")
        print("  Shift+Arrow: Move sprite 5px")
        print("  E: Toggle eraser mode")
        print("  [ ]: Adjust eraser size (or +/-)")
        print("  Ctrl-Z: Undo last erase")
        print("  C: Center horizontally")
        print("  B: Align to bottom")
        print("  T: Align to top")
        print("  R: Reset to auto-alignment")
        print("  Enter: Accept and continue")

        # Cache sprites once at the start to preserve eraser edits during movement
        if not hasattr(self, 'sprite_cache'):
            self._cache_sprites()

        pygame.init()

        # Calculate window size to fit the whole grid
        scale = min(800 // self.cleaned_image.width, 600 // self.cleaned_image.height, 4)
        scale = max(1, scale)  # At least 1x

        window_width = self.cleaned_image.width * scale + 40
        window_height = self.cleaned_image.height * scale + 100

        screen = pygame.display.set_mode((window_width, window_height))
        pygame.display.set_caption("Sprite Alignment Tool - E: Eraser | Enter: Done")

        clock = pygame.time.Clock()
        running = True
        selected_cell = None  # (row, col)
        eraser_mode = False
        eraser_size = 3  # Radius in pixels (on the actual image, not scaled)
        mouse_pressed = False
        undo_stack = []  # Stack for undo history
        current_erase_cell = None  # Track which cell we're currently erasing in
        font = pygame.font.SysFont('Arial', 16)

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        running = False
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_e:
                        # Toggle eraser mode
                        eraser_mode = not eraser_mode
                        if eraser_mode:
                            selected_cell = None  # Deselect cell when entering eraser mode
                    elif event.key == pygame.K_z and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        # Undo (Ctrl-Z)
                        if undo_stack:
                            self.aligned_image = undo_stack.pop()
                            # Re-cache sprites after undo to stay in sync
                            self._cache_sprites()
                    elif event.key == pygame.K_RIGHTBRACKET or event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        # Increase eraser size (], +, or =)
                        eraser_size = min(20, eraser_size + 1)
                    elif event.key == pygame.K_LEFTBRACKET or event.key == pygame.K_MINUS:
                        # Decrease eraser size ([, or -)
                        eraser_size = max(1, eraser_size - 1)
                    elif selected_cell and not eraser_mode:
                        row, col = selected_cell
                        x_off, y_off = self.sprite_offsets.get((row, col), (0, 0))
                        shift_pressed = pygame.key.get_mods() & pygame.KMOD_SHIFT
                        move = 5 if shift_pressed else 1

                        if event.key == pygame.K_LEFT:
                            x_off -= move
                        elif event.key == pygame.K_RIGHT:
                            x_off += move
                        elif event.key == pygame.K_UP:
                            y_off -= move
                        elif event.key == pygame.K_DOWN:
                            y_off += move
                        elif event.key == pygame.K_c:
                            # Center horizontally
                            x_off = 0  # Will be recalculated
                        elif event.key == pygame.K_b:
                            # Bottom align
                            y_off = 0  # Will be recalculated
                        elif event.key == pygame.K_t:
                            # Top align
                            y_off = 0
                        elif event.key == pygame.K_r:
                            # Reset to auto - trigger auto-align for this cell
                            pass

                        # Update offset
                        self.sprite_offsets[(row, col)] = (x_off, y_off)
                        # Rebuild aligned image
                        self._rebuild_aligned_image()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pressed = True
                    mx, my = event.pos
                    # Adjust for border
                    mx -= 20
                    my -= 50

                    if eraser_mode:
                        # Save state for undo (limit stack to 20 states)
                        undo_stack.append(self.aligned_image.copy())
                        if len(undo_stack) > 20:
                            undo_stack.pop(0)

                        # Determine which cell we're in and lock to it
                        grid_x = mx // (self.sprite_width * scale)
                        grid_y = my // (self.sprite_height * scale)

                        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                            current_erase_cell = (grid_y, grid_x)
                        else:
                            current_erase_cell = None

                        # Erase at this position (constrained to cell)
                        self._erase_at_position(mx, my, scale, eraser_size, current_erase_cell)
                    else:
                        # Click to select cell
                        # Convert to grid coordinates
                        grid_x = mx // (self.sprite_width * scale)
                        grid_y = my // (self.sprite_height * scale)

                        if 0 <= grid_x < self.cols and 0 <= grid_y < self.rows:
                            selected_cell = (grid_y, grid_x)

                elif event.type == pygame.MOUSEBUTTONUP:
                    mouse_pressed = False
                    current_erase_cell = None  # Clear erase cell when releasing mouse

                elif event.type == pygame.MOUSEMOTION:
                    if mouse_pressed and eraser_mode and current_erase_cell:
                        # Erase while dragging (stay within the same cell)
                        mx, my = event.pos
                        mx -= 20
                        my -= 50
                        self._erase_at_position(mx, my, scale, eraser_size, current_erase_cell)

            # Draw
            screen.fill((30, 30, 30))

            # Draw the aligned sprite sheet
            # Convert PIL to pygame surface
            mode = self.aligned_image.mode
            size = self.aligned_image.size
            data = self.aligned_image.tobytes()
            py_image = pygame.image.fromstring(data, size, mode)

            # Scale up
            scaled_size = (self.aligned_image.width * scale, self.aligned_image.height * scale)
            scaled_image = pygame.transform.scale(py_image, scaled_size)

            # Draw checkerboard background
            checker_size = 16
            for y in range(0, scaled_size[1], checker_size):
                for x in range(0, scaled_size[0], checker_size):
                    if ((x // checker_size) + (y // checker_size)) % 2 == 0:
                        pygame.draw.rect(screen, (40, 40, 40), (20 + x, 50 + y, checker_size, checker_size))

            screen.blit(scaled_image, (20, 50))

            # Draw grid lines
            for row in range(self.rows + 1):
                y = 50 + row * self.sprite_height * scale
                pygame.draw.line(screen, (100, 100, 100), (20, y), (20 + scaled_size[0], y), 1)
            for col in range(self.cols + 1):
                x = 20 + col * self.sprite_width * scale
                pygame.draw.line(screen, (100, 100, 100), (x, 50), (x, 50 + scaled_size[1]), 1)

            # Highlight selected cell
            if selected_cell and not eraser_mode:
                row, col = selected_cell
                x = 20 + col * self.sprite_width * scale
                y = 50 + row * self.sprite_height * scale
                w = self.sprite_width * scale
                h = self.sprite_height * scale
                pygame.draw.rect(screen, (255, 255, 0), (x, y, w, h), 2)

            # Draw eraser cursor
            if eraser_mode:
                mx, my = pygame.mouse.get_pos()
                eraser_radius = eraser_size * scale
                pygame.draw.circle(screen, (255, 100, 100), (mx, my), eraser_radius, 2)
                pygame.draw.line(screen, (255, 100, 100), (mx - eraser_radius, my), (mx + eraser_radius, my), 1)
                pygame.draw.line(screen, (255, 100, 100), (mx, my - eraser_radius), (mx, my + eraser_radius), 1)

            # UI Text
            title = font.render("Sprite Alignment Tool", True, (255, 255, 255))

            if eraser_mode:
                mode_text = font.render(f"ERASER MODE (Size: {eraser_size}px)", True, (255, 100, 100))
                help_text = font.render("Drag: Erase in Cell | []: Size | Ctrl-Z: Undo | E: Exit | Enter: Done", True, (180, 180, 180))
                screen.blit(mode_text, (20, 25))
            else:
                help_text = font.render("E: Eraser | Click: Select | Arrows: Move | C/B/T: Align | Enter: Done", True, (180, 180, 180))

                if selected_cell:
                    cell_text = font.render(f"Selected: Row {selected_cell[0]}, Col {selected_cell[1]}", True, (255, 255, 0))
                    offset = self.sprite_offsets.get(selected_cell, (0, 0))
                    offset_text = font.render(f"Offset: ({offset[0]}, {offset[1]})", True, (200, 200, 200))
                    screen.blit(cell_text, (20, 25))
                    screen.blit(offset_text, (250, 25))

            screen.blit(title, (window_width // 2 - 80, 5))
            screen.blit(help_text, (20, window_height - 25))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
        print("✓ Alignment complete")

    def _cache_sprites(self):
        """Extract and cache all sprites from aligned_image to preserve edits during movement"""
        self.sprite_cache = {}
        img_array = np.array(self.aligned_image)

        for row in range(self.rows):
            for col in range(self.cols):
                # Extract cell from aligned image
                x_start = col * self.sprite_width
                y_start = row * self.sprite_height
                cell = img_array[y_start:y_start + self.sprite_height,
                                x_start:x_start + self.sprite_width]

                # Store the entire cell (including transparency/erased areas)
                self.sprite_cache[(row, col)] = cell.copy()

    def _rebuild_aligned_image(self):
        """Rebuild the aligned image based on current offsets using cached sprites"""
        aligned = Image.new('RGBA', self.aligned_image.size, (0, 0, 0, 0))
        aligned_array = np.array(aligned)

        for row in range(self.rows):
            for col in range(self.cols):
                # Get cached sprite (preserves eraser edits)
                if (row, col) not in self.sprite_cache:
                    continue

                cell = self.sprite_cache[(row, col)]

                # Find sprite bounding box
                alpha = cell[:, :, 3]
                non_transparent = np.where(alpha > 0)
                if len(non_transparent[0]) == 0:
                    continue

                min_y, max_y = non_transparent[0].min(), non_transparent[0].max()
                min_x, max_x = non_transparent[1].min(), non_transparent[1].max()
                sprite = cell[min_y:max_y+1, min_x:max_x+1]
                sprite_h, sprite_w = sprite.shape[:2]

                # Get offset
                x_offset, y_offset = self.sprite_offsets.get((row, col), (0, 0))

                # Calculate grid position + offset
                x_start = col * self.sprite_width
                y_start = row * self.sprite_height
                dest_y = y_start + y_offset
                dest_x = x_start + x_offset

                # Bounds check
                if dest_y + sprite_h <= aligned_array.shape[0] and dest_x + sprite_w <= aligned_array.shape[1]:
                    aligned_array[dest_y:dest_y + sprite_h,
                                dest_x:dest_x + sprite_w] = sprite

        self.aligned_image = Image.fromarray(aligned_array)

        # Clean artifacts after rebuilding
        self._clean_cell_artifacts_silent()

    def _erase_at_position(self, mx, my, scale, radius, cell=None):
        """Erase pixels at the given position (in screen coordinates)

        Args:
            mx, my: Mouse position in screen coordinates (after border adjustment)
            scale: Display scale factor
            radius: Eraser brush radius in image pixels
            cell: Optional (row, col) tuple to constrain erasing to that cell only
        """
        # Convert screen coordinates to image coordinates
        img_x = mx // scale
        img_y = my // scale

        # Bounds check
        if img_x < 0 or img_y < 0 or img_x >= self.aligned_image.width or img_y >= self.aligned_image.height:
            return

        # Calculate cell bounds if a cell is specified
        if cell is not None:
            row, col = cell
            cell_x_min = col * self.sprite_width
            cell_x_max = (col + 1) * self.sprite_width - 1
            cell_y_min = row * self.sprite_height
            cell_y_max = (row + 1) * self.sprite_height - 1
        else:
            # No cell constraint
            cell_x_min, cell_y_min = 0, 0
            cell_x_max = self.aligned_image.width - 1
            cell_y_max = self.aligned_image.height - 1

        # Get image as numpy array
        img_array = np.array(self.aligned_image)

        # Erase in a circular area
        for dy in range(-radius, radius + 1):
            for dx in range(-radius, radius + 1):
                # Check if within circle
                if dx*dx + dy*dy <= radius*radius:
                    px = img_x + dx
                    py = img_y + dy

                    # Bounds check (image bounds AND cell bounds)
                    if (0 <= px < img_array.shape[1] and
                        0 <= py < img_array.shape[0] and
                        cell_x_min <= px <= cell_x_max and
                        cell_y_min <= py <= cell_y_max):
                        # Make pixel transparent
                        img_array[py, px] = [0, 0, 0, 0]

        # Update aligned image
        self.aligned_image = Image.fromarray(img_array)

        # Also update the sprite cache for the affected cell
        if cell is not None and hasattr(self, 'sprite_cache'):
            row, col = cell
            x_start = col * self.sprite_width
            y_start = row * self.sprite_height
            # Extract the updated cell from aligned image
            updated_cell = img_array[y_start:y_start + self.sprite_height,
                                    x_start:x_start + self.sprite_width]
            self.sprite_cache[(row, col)] = updated_cell.copy()

    def slice_sprite_sheet(self):
        """Slice sprite sheet into individual frames"""
        print("\n--- STEP 6: Slicing Frames ---")

        # Use aligned image if available, otherwise use cleaned image
        source_image = self.aligned_image if self.aligned_image else self.cleaned_image

        # Convert PIL image to Pygame surface
        mode = source_image.mode
        size = source_image.size
        data = source_image.tobytes()

        py_image = pygame.image.fromstring(data, size, mode)

        self.frames = []
        for row in range(self.rows):
            row_frames = []
            for col in range(self.cols):
                frame = pygame.Surface((self.sprite_width, self.sprite_height), pygame.SRCALPHA)
                rect = pygame.Rect(
                    col * self.sprite_width,
                    row * self.sprite_height,
                    self.sprite_width,
                    self.sprite_height
                )
                frame.blit(py_image, (0, 0), rect)
                row_frames.append(frame)
            self.frames.append(row_frames)

        print(f"✓ Sliced into {self.rows} animations with {self.cols} frames each")

    def preview_animations(self):
        """Interactive preview window - Returns True to continue, False to go back to alignment"""
        print("\n--- STEP 7: Preview Animations ---")
        print("\nOpening preview window...")
        print("Controls:")
        print("  SPACE: Switch animation row")
        print("  UP/DOWN: Adjust animation speed")
        print("  LEFT/RIGHT: Navigate frames manually")
        print("  A: Go back to alignment tool")
        print("  ESC or Enter: Continue to export")

        pygame.init()
        screen_width = self.sprite_width * PREVIEW_SCALE + 100
        screen_height = self.sprite_height * PREVIEW_SCALE + 150
        screen = pygame.display.set_mode((screen_width, screen_height))
        pygame.display.set_caption("Sprite Preview - Press SPACE to switch animations")

        clock = pygame.time.Clock()
        running = True
        current_row = 0
        frame_index = 0
        timer = 0
        animation_speed = 8  # Frames to wait between animation frames
        manual_mode = False

        font = pygame.font.SysFont('Arial', 18)

        go_back_to_alignment = False

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        running = False
                    elif event.key == pygame.K_a:
                        go_back_to_alignment = True
                        running = False
                    elif event.key == pygame.K_SPACE:
                        current_row = (current_row + 1) % self.rows
                        frame_index = 0
                        manual_mode = False
                    elif event.key == pygame.K_UP:
                        animation_speed = max(1, animation_speed - 1)
                    elif event.key == pygame.K_DOWN:
                        animation_speed = min(30, animation_speed + 1)
                    elif event.key == pygame.K_LEFT:
                        frame_index = (frame_index - 1) % self.cols
                        manual_mode = True
                    elif event.key == pygame.K_RIGHT:
                        frame_index = (frame_index + 1) % self.cols
                        manual_mode = True

            # Animation logic
            if not manual_mode:
                timer += 1
                if timer > animation_speed:
                    frame_index = (frame_index + 1) % self.cols
                    timer = 0

            # Draw
            screen.fill((40, 40, 40))

            # Draw current frame scaled up
            current_sprite = self.frames[current_row][frame_index]
            scaled_sprite = pygame.transform.scale(
                current_sprite,
                (self.sprite_width * PREVIEW_SCALE, self.sprite_height * PREVIEW_SCALE)
            )

            x_pos = (screen_width - self.sprite_width * PREVIEW_SCALE) // 2
            y_pos = 70

            # Checkerboard background to show transparency
            checker_size = 10
            for cy in range(0, self.sprite_height * PREVIEW_SCALE, checker_size):
                for cx in range(0, self.sprite_width * PREVIEW_SCALE, checker_size):
                    if ((cx // checker_size) + (cy // checker_size)) % 2 == 0:
                        pygame.draw.rect(screen, (60, 60, 60),
                                       (x_pos + cx, y_pos + cy, checker_size, checker_size))

            screen.blit(scaled_sprite, (x_pos, y_pos))

            # UI Text
            title = font.render(f"Animation Row {current_row} of {self.rows-1}", True, (255, 255, 255))
            frame_text = font.render(f"Frame: {frame_index + 1}/{self.cols}", True, (200, 200, 200))
            speed_text = font.render(f"Speed: {animation_speed} | UP/DOWN to adjust", True, (200, 200, 200))
            help_text = font.render("SPACE: Next | LEFT/RIGHT: Manual | A: Back to Align | ENTER/ESC: Done", True, (150, 150, 150))

            screen.blit(title, (20, 20))
            screen.blit(frame_text, (20, 45))
            screen.blit(speed_text, (screen_width - 250, 20))
            screen.blit(help_text, (20, screen_height - 30))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

        if go_back_to_alignment:
            print("↩ Going back to alignment tool...")
            return False  # Go back to alignment
        else:
            print("✓ Preview complete")
            return True  # Continue to export

    def export_sprite_sheet(self):
        """Export the final optimized sprite sheet"""
        print("\n--- STEP 8: Export ---")

        # Ask for export format
        print("\nExport options:")
        print("  1. Full sprite sheet (single file)")
        print("  2. Separate files (one per sprite)")

        export_choice = input("Choose export format [1]: ").strip()
        if not export_choice:
            export_choice = "1"

        # Ask for output filename
        base_name = os.path.splitext(os.path.basename(self.input_path))[0]
        default_name = f"{base_name}_processed.png"

        # Create output folder
        if not os.path.exists(OUTPUT_FOLDER):
            os.makedirs(OUTPUT_FOLDER)

        final_image = self.aligned_image if self.aligned_image else self.cleaned_image

        if export_choice == "2":
            # Export as separate files
            folder_name = input(f"Folder name for separate sprites [{base_name}_sprites]: ").strip()
            if not folder_name:
                folder_name = f"{base_name}_sprites"

            output_folder = os.path.join(OUTPUT_FOLDER, folder_name)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            self.output_path = output_folder  # Store folder path for code generation

            # Save each sprite as a separate file
            sprite_count = 0
            for row in range(self.rows):
                for col in range(self.cols):
                    # Extract sprite region
                    x = col * self.sprite_width
                    y = row * self.sprite_height
                    sprite_img = final_image.crop((
                        x, y,
                        x + self.sprite_width,
                        y + self.sprite_height
                    ))

                    # Save with row_col naming
                    sprite_path = os.path.join(output_folder, f"sprite_r{row}_c{col}.png")
                    sprite_img.save(sprite_path)
                    sprite_count += 1

            print(f"✓ Saved {sprite_count} separate sprites to: {output_folder}")
            print(f"  Format: sprite_r[row]_c[col].png")

        else:
            # Export as full sprite sheet (original behavior)
            output_name = input(f"Output filename [{default_name}]: ").strip()
            if not output_name:
                output_name = default_name
            if not output_name.endswith('.png'):
                output_name += '.png'

            self.output_path = os.path.join(OUTPUT_FOLDER, output_name)

            # Save the aligned image (or cleaned image if no alignment)
            final_image.save(self.output_path)

            # Also save a preview image with grid lines
            preview_img = final_image.copy()
            from PIL import ImageDraw
            draw = ImageDraw.Draw(preview_img)

            # Draw grid lines
            for row in range(1, self.rows):
                y = row * self.sprite_height
                draw.line([(0, y), (preview_img.width, y)], fill=(255, 0, 0, 128), width=1)
            for col in range(1, self.cols):
                x = col * self.sprite_width
                draw.line([(x, 0), (x, preview_img.height)], fill=(255, 0, 0, 128), width=1)

            preview_path = self.output_path.replace('.png', '_grid_preview.png')
            preview_img.save(preview_path)

            print(f"✓ Saved sprite sheet: {self.output_path}")
            print(f"✓ Saved preview with grid: {preview_path}")

    def generate_code_snippet(self):
        """Generate code snippet for using the sprite in-game"""
        print("\n--- STEP 9: Code Snippet ---")

        sprite_name = os.path.splitext(os.path.basename(self.output_path))[0]
        class_name = ''.join(word.capitalize() for word in sprite_name.split('_'))

        print("\nAdd this to your game code:")
        print("-" * 60)
        print(f"""
# Load sprite sheet
{sprite_name}_frames = load_sprite_sheet("assets/images/{os.path.basename(self.output_path)}", {self.rows}, {self.cols})

# Example: In your sprite class __init__:
self.frames = {sprite_name}_frames
self.current_row = 0  # Animation row (0 to {self.rows-1})
self.frame_index = 0
self.animation_speed = 0.15

# Example: In your sprite class update():
self.frame_index += self.animation_speed
if self.frame_index >= len(self.frames[self.current_row]):
    self.frame_index = 0
self.image = self.frames[self.current_row][int(self.frame_index)]

# Animation rows in your sprite:
# Row 0: [Animation name]
# Row 1: [Animation name]
# ... (Label these based on your sprite!)
""")
        print("-" * 60)

    def ask_yes_no(self, question):
        """Ask a yes/no question"""
        while True:
            answer = input(f"{question} (y/n): ").strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            print("Please answer 'y' or 'n'")

    def ask_number(self, question, default, min_val=None, max_val=None, is_float=False):
        """Ask for a number with validation"""
        while True:
            answer = input(f"{question} [{default}]: ").strip()
            if not answer:
                return default
            try:
                value = float(answer) if is_float else int(answer)
                if min_val is not None and value < min_val:
                    print(f"Value must be at least {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"Value must be at most {max_val}")
                    continue
                return value
            except ValueError:
                print("Please enter a valid number")

def main():
    """Main entry point"""
    try:
        pipeline = SpritePipeline()
        pipeline.run()
    except KeyboardInterrupt:
        print("\n\nPipeline cancelled by user.")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Check dependencies
    try:
        import pygame
        import PIL
        import numpy
    except ImportError as e:
        print("Missing required package!")
        print("\nPlease install dependencies:")
        print("  pip install pygame pillow numpy")
        sys.exit(1)

    main()
