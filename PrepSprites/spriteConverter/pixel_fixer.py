import sys
import os
from PIL import Image
import numpy as np
from collections import Counter

def pixel_perfect_cleanup(image_path, output_path, target_width=64, num_colors=16, contrast=1.2, saturation=1.2):
    """
    Converts a high-res AI sprite into a clean, pixel-perfect sprite.
    """
    try:
        # 1. Load Image
        img = Image.open(image_path).convert("RGBA")
        
        # 2. Hard Cutout (Alpha Thresholding)
        # AI images have fuzzy semi-transparent edges. We need to make them 100% solid or 100% transparent.
        datas = img.getdata()
        newData = []
        for item in datas:
            # If the alpha (transparency) is less than 128, make it invisible. Otherwise, solid.
            if item[3] < 128:
                newData.append((0, 0, 0, 0))
            else:
                newData.append(item)
        img.putdata(newData)

        # 3. Downscale
        # We use Bilinear first to smooth out AI noise, then we will snap to grid later.
        aspect_ratio = img.height / img.width
        target_height = int(target_width * aspect_ratio)
        img_small = img.resize((target_width, target_height), resample=Image.Resampling.BILINEAR)

        # 4. Enhance (Optional but recommended for AI images)
        # AI images are often washed out. Pixel art pops with high contrast.
        from PIL import ImageEnhance
        enhancer = ImageEnhance.Contrast(img_small)
        img_small = enhancer.enhance(contrast)
        enhancer = ImageEnhance.Color(img_small)
        img_small = enhancer.enhance(saturation)

        # 5. Color Quantization (The "Pixel Art" look)
        # This forces the image to use only 'num_colors'. 
        # dither=Image.NONE is CRITICAL. It stops the "checkerboard" pattern.
        
        # We convert to RGB to quantize colors, then re-apply the alpha channel later
        rgb_img = img_small.convert("RGB")
        quantized = rgb_img.quantize(colors=num_colors, method=1, kmeans=num_colors, dither=Image.NONE)
        
        # Convert back to RGBA
        final_img = quantized.convert("RGBA")

        # 6. Re-apply clean Alpha Mask
        # Quantization can mess up transparency, so we use the alpha from the downscaled image
        source_alpha = img_small.split()[-1]
        # Threshold the alpha again to ensure hard edges
        binary_alpha = source_alpha.point(lambda x: 255 if x > 100 else 0, mode='1')
        final_img.putalpha(binary_alpha)

        # 7. Orphan Pixel Cleanup (Despeckling)
        # This removes single random pixels that don't match their neighbors
        final_img = remove_orphan_pixels(final_img)

        # 8. Save the result
        final_img.save(output_path)
        print(f"✅ Success! Saved to {output_path}")
        
        # OPTIONAL: Save an upscaled version for viewing (4x zoom)
        upscaled = final_img.resize((target_width * 8, target_height * 8), resample=Image.Resampling.NEAREST)
        upscaled.save(output_path.replace(".png", "_preview.png"))
        print(f"🔍 Created 8x preview at {output_path.replace('.png', '_preview.png')}")

    except Exception as e:
        print(f"❌ Error: {e}")

def remove_orphan_pixels(img):
    """
    A simple algorithm to remove single 'noise' pixels that are surrounded 
    by transparent pixels or totally different colors.
    """
    # Convert to numpy array for faster processing
    data = np.array(img)
    height, width = data.shape[:2]
    
    # Make a copy to modify
    clean_data = data.copy()

    # Loop through inner pixels (skipping borders for simplicity)
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            current_pixel = data[y, x]
            
            # Skip if current pixel is transparent
            if current_pixel[3] == 0:
                continue

            # Get neighbors (Up, Down, Left, Right)
            neighbors = [
                data[y-1, x], # N
                data[y+1, x], # S
                data[y, x-1], # W
                data[y, x+1]  # E
            ]

            # Check if pixel is isolated (all neighbors are transparent or significantly different)
            # For simplicity in pixel art, we often just check if it matches NO neighbors.
            matches = 0
            for n in neighbors:
                if np.array_equal(n, current_pixel):
                    matches += 1
            
            # If the pixel has 0 neighbors of the same color, it's likely noise.
            # We replace it with the most common neighbor color.
            if matches == 0:
                # Find most common valid neighbor color
                valid_neighbors = [tuple(n) for n in neighbors if n[3] > 0]
                if valid_neighbors:
                    most_common = Counter(valid_neighbors).most_common(1)[0][0]
                    clean_data[y, x] = most_common
                else:
                    # If all neighbors are transparent, kill this pixel
                    clean_data[y, x] = [0, 0, 0, 0]

    return Image.fromarray(clean_data)

# --- CONFIGURATION ---
INPUT_FOLDER = "input"   # Put your AI images in this folder
OUTPUT_FOLDER = "output"
SUPPORTED_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')

def process_folder(input_folder, output_folder, target_width=512, num_colors=16):
    """
    Process all images in the input folder and save results to output folder.
    """
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Get all image files in input folder
    if not os.path.exists(input_folder):
        print(f"Creating input folder: {input_folder}")
        os.makedirs(input_folder, exist_ok=True)
        print(f"Please add your images to the '{input_folder}' folder and run again.")
        return

    image_files = [f for f in os.listdir(input_folder)
                   if f.lower().endswith(SUPPORTED_EXTENSIONS)]

    if not image_files:
        print(f"No images found in '{input_folder}'. Supported formats: {SUPPORTED_EXTENSIONS}")
        return

    print(f"Found {len(image_files)} image(s) to process...\n")

    for filename in image_files:
        input_path = os.path.join(input_folder, filename)
        # Always output as PNG for transparency support
        output_filename = os.path.splitext(filename)[0] + ".png"
        output_path = os.path.join(output_folder, output_filename)

        print(f"Processing: {filename}")
        pixel_perfect_cleanup(input_path, output_path, target_width=target_width, num_colors=num_colors)
        print()

    print(f"Done! Processed {len(image_files)} image(s).")

# Run batch processing
process_folder(INPUT_FOLDER, OUTPUT_FOLDER, target_width=512, num_colors=16)