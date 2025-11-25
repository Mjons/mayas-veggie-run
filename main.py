import pygame
import random
import math
import asyncio

# --- INITIAL SETUP ---
pygame.init()
pygame.mixer.init()  # Initialize sound mixer
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 450
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Maya's Veggie Run")
clock = pygame.time.Clock()
font = pygame.font.SysFont('Arial', 24)

# --- COLORS (PLACEHOLDERS FOR ART) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
MAYA_COLOR = (255, 105, 180)      # Hot Pink
FOOD_COLOR = (50, 205, 50)        # Green (Veggies)
OBSTACLE_COLOR = (139, 69, 19)    # Brown (Trees/Rocks)
PET_SLEEPING_COLOR = (160, 82, 45)# Similar Brown to rocks (Disguise)
PET_AWAKE_COLOR = (255, 215, 0)   # Gold (Love!)

# --- GAME CONSTANTS ---
GRAVITY = 0.8
JUMP_STRENGTH = -16
GROUND_Y = 390  # Adjusted so Maya's feet touch the visible ground

# --- SPRITE LOADING HELPER ---
def load_sprite_sheet(filepath, rows, cols):
    """Load a sprite sheet and return a 2D list of frames. Auto-calculates frame size."""
    sheet = pygame.image.load(filepath).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    frame_width = sheet_width // cols
    frame_height = sheet_height // rows

    frames = []
    for row in range(rows):
        row_frames = []
        for col in range(cols):
            x = col * frame_width
            y = row * frame_height
            frame = sheet.subsurface((x, y, frame_width, frame_height))
            row_frames.append(frame)
        frames.append(row_frames)
    return frames

# --- SOUND LOADING HELPER ---
def load_sound(filepath):
    """Load a sound file with error handling. Returns None if file not found."""
    try:
        return pygame.mixer.Sound(filepath)
    except:
        return None

# --- LOAD SOUNDS ---
sounds = {
    'jump': load_sound("assets/sounds/jump.ogg"),
    'collect': load_sound("assets/sounds/collect.ogg"),
    'hit': load_sound("assets/sounds/hit.ogg"),
    'love': load_sound("assets/sounds/love.ogg"),
    'game_over': load_sound("assets/sounds/game_over.ogg"),
}

# --- LOAD BACKGROUND MUSIC ---
try:
    pygame.mixer.music.load("assets/sounds/big and strong.ogg")
    pygame.mixer.music.set_volume(0.3)  # 30% volume for background music
    pygame.mixer.music.play(-1)  # Loop forever
except:
    pass  # No background music if file doesn't exist

# --- LOAD BACKGROUND IMAGE ---
background_image = pygame.image.load("assets/images/bg.png").convert()
# Scale up slightly and shift up to adjust ground position
bg_scale = 1.08  # Scale up by 8% to make it slightly bigger
bg_width = int(SCREEN_WIDTH * bg_scale)
bg_height = int(SCREEN_HEIGHT * bg_scale)
background_image = pygame.transform.scale(background_image, (bg_width, bg_height))
bg_y_offset = -15  # Move up by 15 pixels

class Player(pygame.sprite.Sprite):
    # Class variable to store Maya sprite frames (load once)
    maya_frames = None

    def __init__(self):
        super().__init__()

        # Load Maya sprite sheet if not already loaded
        # 7 rows, 5 columns - assuming row 0 = idle, row 1 = running, row 2 = jumping
        if Player.maya_frames is None:
            Player.maya_frames = load_sprite_sheet("assets/images/mayaSprite.png", 7, 5)

        # Animation variables
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_row = 1  # Start with running animation (row 1)

        # Set initial image
        self.image = Player.maya_frames[self.current_row][0]
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.bottom = GROUND_Y  # Position by bottom instead of top
        self.velocity_y = 0
        self.jumping = False
        self.health = 100

    def update(self):
        # Gravity
        self.velocity_y += GRAVITY
        self.rect.y += self.velocity_y

        # Floor collision
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.velocity_y = 0
            self.jumping = False
            # Only reset to running if not in hit animation (row 6)
            if self.current_row != 6:
                self.current_row = 1  # Running animation when on ground

        # Update animation
        if Player.maya_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(Player.maya_frames[self.current_row]):
                self.frame_index = 0
            self.image = Player.maya_frames[self.current_row][int(self.frame_index)]

    def jump(self):
        if not self.jumping:
            self.velocity_y = JUMP_STRENGTH
            self.jumping = True
            self.current_row = 2  # Switch to jumping animation (row 2)
            # Play jump sound
            if sounds['jump']:
                sounds['jump'].play()

class Object(pygame.sprite.Sprite):
    # Class variable to store pet sprite frames (load once)
    pet_frames = None
    # Class variable to store food sprites (load once)
    food_sprites = None
    # Class variable to store unicorn sprite frames (load once)
    unicorn_frames = None
    # Class variable to store elmo sprite frames (load once)
    elmo_frames = None
    # Class variable to store rock sprite (load once)
    rock_sprite = None

    def __init__(self, obj_type, speed):
        super().__init__()
        self.type = obj_type # "food", "obstacle", "pet", "unicorn", "elmo"

        # Animation variables
        self.frame_index = 0
        self.animation_speed = 0.15
        self.current_row = 0  # 0 = sleeping, 1 = collision/awake
        self.collected = False  # Flag to prevent re-collision (for pets)

        # Dimensions based on type
        if self.type == "food":
            # Load food sprites if not already loaded
            if Object.food_sprites is None:
                Object.food_sprites = []
                # Load all 9 food sprites (3 rows x 3 cols)
                for row in range(3):
                    for col in range(3):
                        sprite = pygame.image.load(f"assets/images/sprite_r{row}_c{col}.png").convert_alpha()
                        Object.food_sprites.append(sprite)

            # Randomly select one of the 9 food sprites
            self.image = random.choice(Object.food_sprites)
            # Food spawns in air or ground (adjusted to be above ground)
            self.rect = self.image.get_rect()
            self.rect.bottom = random.choice([GROUND_Y - 10, GROUND_Y - 80, GROUND_Y - 140])

        elif self.type == "obstacle":
            # Load rock sprite if not already loaded
            if Object.rock_sprite is None:
                Object.rock_sprite = pygame.image.load("assets/images/rock.png").convert_alpha()

            self.image = Object.rock_sprite
            self.rect = self.image.get_rect()
            self.rect.bottom = GROUND_Y  # Position on ground

        elif self.type == "pet":
            # Load sprite sheet if not already loaded
            if Object.pet_frames is None:
                Object.pet_frames = load_sprite_sheet("assets/images/pet_sleeping.png", 2, 5)

            # Start with first frame of sleeping animation (row 0)
            self.image = Object.pet_frames[0][0]
            self.rect = self.image.get_rect()
            self.rect.bottom = GROUND_Y  # Position by bottom

        elif self.type == "unicorn":
            # Load unicorn sprite sheet if not already loaded (1 row, 5 columns)
            if Object.unicorn_frames is None:
                raw_frames = load_sprite_sheet("assets/images/unicorn_processed.png", 1, 5)
                # Flip all frames horizontally so unicorn runs left-to-right
                Object.unicorn_frames = [[pygame.transform.flip(frame, True, False) for frame in raw_frames[0]]]

            # Start with first frame of running animation
            self.image = Object.unicorn_frames[0][0]
            self.rect = self.image.get_rect()
            self.rect.bottom = GROUND_Y  # Position on ground

        elif self.type == "elmo":
            # Load elmo sprite sheet if not already loaded (1 row, 5 columns)
            if Object.elmo_frames is None:
                Object.elmo_frames = load_sprite_sheet("assets/images/elmo_processed.png", 1, 5)

            # Start with first frame
            self.image = Object.elmo_frames[0][0]
            self.rect = self.image.get_rect()
            self.rect.y = -100  # Start above screen
            self.rect.x = SCREEN_WIDTH + random.randint(100, 400)  # Random horizontal position
            # Elmo drops down instead of moving horizontally initially
            self.drop_speed = 3  # Speed of dropping
            self.target_y = random.randint(50, 150)  # Random drop height (higher on screen)
            self.is_dangling = False  # Track if Elmo has reached target and is dangling
            self.sway_offset = 0  # For swaying motion
            self.sway_speed = random.uniform(0.05, 0.1)  # Random sway speed
            self.sway_amplitude = random.randint(3, 8)  # Random sway distance
            self.base_x = self.rect.x  # Store base x position for swaying
            self.speed = speed  # Will scroll with game once at target height
            return  # Don't set x position below

        self.rect.x = SCREEN_WIDTH + random.randint(0, 100)
        self.speed = speed

    def update(self):
        # Special behavior for Elmo - drops down first, then dangles and sways
        if self.type == "elmo":
            if self.rect.y < self.target_y:
                # Still dropping
                self.rect.y += self.drop_speed
                # Update base_x as we scroll during drop
                self.base_x -= self.speed * 0.2
            else:
                # At target height, start dangling with sway
                if not self.is_dangling:
                    self.is_dangling = True
                    # base_x is already set during init

                # Apply swaying motion using sine wave
                self.sway_offset += self.sway_speed
                sway_x = math.sin(self.sway_offset) * self.sway_amplitude

                # Scroll slowly left while swaying
                self.base_x -= self.speed * 0.2
                self.rect.x = int(self.base_x + sway_x)
        else:
            # Normal horizontal scrolling for other objects
            self.rect.x -= self.speed

        # Animate pet sprite
        if self.type == "pet" and Object.pet_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(Object.pet_frames[self.current_row]):
                self.frame_index = 0
            self.image = Object.pet_frames[self.current_row][int(self.frame_index)]

        # Animate unicorn sprite
        if self.type == "unicorn" and Object.unicorn_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(Object.unicorn_frames[0]):
                self.frame_index = 0
            self.image = Object.unicorn_frames[0][int(self.frame_index)]

        # Animate elmo sprite
        if self.type == "elmo" and Object.elmo_frames:
            self.frame_index += self.animation_speed
            if self.frame_index >= len(Object.elmo_frames[0]):
                self.frame_index = 0
            self.image = Object.elmo_frames[0][int(self.frame_index)]

        # Kill if off screen
        if self.rect.right < 0:
            self.kill()

# --- MAIN GAME FUNCTION ---
async def main():
    running = True
    game_active = True

    player = Player()
    player_group = pygame.sprite.GroupSingle(player)
    object_group = pygame.sprite.Group()

    # Game Logic Variables
    game_speed = 5
    score = 0
    spawn_timer = 0

    # Message timer for "LOVE!" text
    love_message_timer = 0

    # Pause timer for puppy love moment
    pause_timer = 0

    # Hit timer for showing hit animation
    hit_timer = 0

    # Background scrolling variables
    bg_x1 = 0
    bg_x2 = bg_width  # Use scaled background width for positioning
    bg_scroll_speed = 2  # Background scrolls slower than game objects for parallax effect

    while running:
        # 1. Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if game_active:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        player.jump()
            else:
                # Restart game
                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    game_active = True
                    player.health = 100
                    game_speed = 5
                    score = 0
                    object_group.empty()
                    # Reset background scroll
                    bg_x1 = 0
                    bg_x2 = bg_width

        if game_active:
            # Check if we're in pause mode (puppy love moment)
            if pause_timer > 0:
                pause_timer -= 1
                # During pause, only update animations, not physics/positions
                # Update Maya's animation only (no gravity/movement)
                if Player.maya_frames:
                    player.frame_index += player.animation_speed
                    if player.frame_index >= len(Player.maya_frames[player.current_row]):
                        player.frame_index = 0
                    player.image = Player.maya_frames[player.current_row][int(player.frame_index)]

                # Update animations for objects but don't move them
                for obj in object_group:
                    if obj.type == "pet" and Object.pet_frames:
                        obj.frame_index += obj.animation_speed
                        if obj.frame_index >= len(Object.pet_frames[obj.current_row]):
                            obj.frame_index = 0
                        obj.image = Object.pet_frames[obj.current_row][int(obj.frame_index)]
            else:
                # Normal gameplay
                # Countdown hit timer
                if hit_timer > 0:
                    hit_timer -= 1
                    if hit_timer == 0 and not player.jumping:
                        # Hit animation finished, return to running
                        player.current_row = 1

                # Update background scrolling
                bg_x1 -= bg_scroll_speed
                bg_x2 -= bg_scroll_speed

                # Reset background positions for infinite scroll
                if bg_x1 <= -bg_width:
                    bg_x1 = bg_width
                if bg_x2 <= -bg_width:
                    bg_x2 = bg_width

                # 2. Spawning Logic
                spawn_timer += 1
                # Spawn faster as game speeds up
                if spawn_timer > max(30, 100 - (score // 5)):
                    spawn_timer = 0
                    rng = random.randint(1, 100)

                    # 5% unicorn, 5% elmo, 10% pet, 35% obstacle, 45% food
                    if rng <= 5:
                        # Unicorn runs faster than Maya
                        obj = Object("unicorn", game_speed * 1.5)
                    elif rng <= 10:
                        # Elmo drops from the sky
                        obj = Object("elmo", game_speed)
                    elif rng <= 20:
                        obj = Object("pet", game_speed)
                    elif rng <= 55:
                        obj = Object("obstacle", game_speed)
                    else:
                        obj = Object("food", game_speed)
                    object_group.add(obj)

                # 3. Updates
                player_group.update()
                object_group.update()

            # Remove collected pets after pause ends
            if pause_timer == 0:
                for obj in object_group:
                    if obj.type == "pet" and obj.collected:
                        obj.kill()

            # 4. Collision & Rules Logic
            # Only check collisions when not paused
            if pause_timer == 0:
                # Check for collisions
                collided_dict = pygame.sprite.groupcollide(player_group, object_group, False, False)
                if collided_dict:
                    for player_sprite, objects in collided_dict.items():
                        for obj in objects:
                            if obj.type == "obstacle":
                                player.health -= 2
                                game_speed += 0.2 # Hit obstacle -> Panic -> Speed up
                                player.current_row = 6  # Trigger hit animation (row 6)
                                player.frame_index = 0  # Reset animation to start
                                hit_timer = 20  # Show hit animation for 20 frames
                                obj.kill()
                                # Play hit sound
                                if sounds['hit']:
                                    sounds['hit'].play()

                            elif obj.type == "food":
                                player.health = min(100, player.health + 5)
                                score += 1
                                obj.kill()
                                # Play collect sound
                                if sounds['collect']:
                                    sounds['collect'].play()

                            elif obj.type == "pet" and not obj.collected:
                                # THE HUG MECHANIC
                                player.health = 100 # Full heal
                                love_message_timer = 90 # Show message for 90 frames
                                pause_timer = 60 # Pause for 1 second (60 frames) to enjoy the moment
                                player.current_row = 5  # Trigger hug animation (row 5)
                                player.frame_index = 0  # Reset animation to start
                                obj.current_row = 1 # Switch to awake animation (row 1)
                                obj.frame_index = 0 # Reset animation to start
                                obj.collected = True # Mark as collected to prevent re-collision
                                # Play love sound
                                if sounds['love']:
                                    sounds['love'].play()

                # Check for Missed Food (The "Eat your veggies" rule)
                for obj in object_group:
                    if obj.rect.right < 0: # Went off screen
                        if obj.type == "food":
                            # Missed food -> Game gets harder
                            game_speed += 0.5

            # Game Over check
            if player.health <= 0:
                game_active = False
                # Play game over sound
                if sounds['game_over']:
                    sounds['game_over'].play()

            # 5. Drawing
            # Draw scrolling background (two tiles for seamless loop)
            screen.blit(background_image, (bg_x1, bg_y_offset))
            screen.blit(background_image, (bg_x2, bg_y_offset))

            player_group.draw(screen)
            object_group.draw(screen)

            # Draw string for dangling Elmo
            for obj in object_group:
                if obj.type == "elmo":
                    # Draw a thin white line from top of screen to Elmo's top center
                    # String attaches at the top center of Elmo's sprite
                    string_start = (obj.rect.centerx, 0)
                    string_end = (obj.rect.centerx, obj.rect.top + 5)  # Slightly into sprite for better attachment
                    pygame.draw.line(screen, WHITE, string_start, string_end, 2)

            # UI
            health_text = font.render(f"Energy: {int(player.health)}%", True, BLACK)
            score_text = font.render(f"Speed: {game_speed:.1f}", True, BLACK)
            screen.blit(health_text, (10, 10))
            screen.blit(score_text, (10, 40))

            if love_message_timer > 0:
                love_text = font.render("IT'S A PUPPY! LOVE! +HEALTH", True, (255, 0, 0))
                screen.blit(love_text, (300, 200))
                love_message_timer -= 1

        else:
            # Game Over Screen
            screen.fill(BLACK)
            game_over_text = font.render("OUT OF ENERGY!", True, WHITE)
            restart_text = font.render("Press SPACE to try again", True, WHITE)
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 - 50))
            screen.blit(restart_text, (SCREEN_WIDTH//2 - 120, SCREEN_HEIGHT//2 + 10))

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # Required for web deployment

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())
