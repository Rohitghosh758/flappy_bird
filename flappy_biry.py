import pygame
import random
import os # Import the os module to get the current working directory

# Initialize Pygame
pygame.init()

# --- Game Constants ---
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
GROUND_HEIGHT = 100
PIPE_WIDTH = 80
PIPE_GAP = 200 # Gap between top and bottom pipes
PIPE_SPAWN_INTERVAL = 1500 # milliseconds
PIPE_SPEED = 3

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0) # For pipes
BLUE = (0, 0, 255) # For bird

# --- Set up the display ---
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Biry") # Acknowledging the user's typo for fun!

# --- Fonts ---
font = pygame.font.Font(None, 74) # Default font, size 74
small_font = pygame.font.Font(None, 50)

# --- Game Assets (Placeholder Rectangles as we don't have images) ---
# In a real game, you'd load images for the bird, pipes, and background.
# For simplicity and to make it runnable without external files, we'll draw shapes.

# Bird properties
bird_width = 40
bird_height = 30
bird_x = 100
bird_y = SCREEN_HEIGHT // 2
bird_velocity = 0
gravity = 0.5
jump_power = -9 # Negative value means upward movement

# Ground properties
ground_x = 0
ground_y = SCREEN_HEIGHT - GROUND_HEIGHT

# --- Game State Variables ---
pipes = []
score = 0
game_active = False # True when the game is being played
last_pipe_spawn_time = pygame.time.get_ticks() # Time when the last pipe was spawned

# --- Functions ---

def draw_bird(x, y):
    """Draws the bird as a blue rectangle."""
    pygame.draw.rect(screen, BLUE, (x, y, bird_width, bird_height), border_radius=5)

def create_pipe():
    """Creates a new pair of top and bottom pipes."""
    # Randomly determine the height of the top pipe
    # Ensure there's enough space for the gap and bottom pipe
    max_top_pipe_height = SCREEN_HEIGHT - GROUND_HEIGHT - PIPE_GAP - 50 # 50px buffer from top
    min_top_pipe_height = 50 # 50px buffer from bottom of top pipe
    top_pipe_height = random.randint(min_top_pipe_height, max_top_pipe_height)

    bottom_pipe_height = SCREEN_HEIGHT - GROUND_HEIGHT - top_pipe_height - PIPE_GAP

    # x-position is off-screen to the right
    pipes.append({
        'x': SCREEN_WIDTH,
        'top_height': top_pipe_height,
        'bottom_height': bottom_pipe_height,
        'passed': False # To check if the bird has passed this pipe for scoring
    })

def draw_pipes(pipes):
    """Draws all the pipes."""
    for pipe in pipes:
        # Top pipe
        pygame.draw.rect(screen, GREEN, (pipe['x'], 0, PIPE_WIDTH, pipe['top_height']), border_radius=5)
        # Bottom pipe
        pygame.draw.rect(screen, GREEN, (pipe['x'], SCREEN_HEIGHT - pipe['bottom_height'] - GROUND_HEIGHT, PIPE_WIDTH, pipe['bottom_height']), border_radius=5)

def move_pipes(pipes):
    """Moves pipes from right to left."""
    for pipe in pipes:
        pipe['x'] -= PIPE_SPEED
    # Remove pipes that have moved off screen to save memory
    return [pipe for pipe in pipes if pipe['x'] + PIPE_WIDTH > 0]

def check_collision(bird_rect, pipes):
    """Checks for collisions between the bird and pipes or ground."""
    # Ground collision
    if bird_rect.bottom >= ground_y:
        return True

    # Pipe collision
    for pipe in pipes:
        top_pipe_rect = pygame.Rect(pipe['x'], 0, PIPE_WIDTH, pipe['top_height'])
        bottom_pipe_rect = pygame.Rect(pipe['x'], SCREEN_HEIGHT - pipe['bottom_height'] - GROUND_HEIGHT, PIPE_WIDTH, pipe['bottom_height'])

        if bird_rect.colliderect(top_pipe_rect) or bird_rect.colliderect(bottom_pipe_rect):
            return True
    return False

def update_score(bird_rect, pipes, current_score):
    """Updates the score when the bird passes a pipe."""
    for pipe in pipes:
        # Check if the pipe has passed the bird's x position and hasn't been scored yet
        if pipe['x'] + PIPE_WIDTH < bird_rect.left and not pipe['passed']:
            current_score += 1
            pipe['passed'] = True # Mark as passed so it's not scored again
    return current_score

def display_score(score):
    """Displays the current score on the screen."""
    score_text = font.render(str(score), True, BLACK) # Anti-aliasing, color
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
    screen.blit(score_text, score_rect)

def game_over_screen(score):
    """Displays the game over screen and restart instructions."""
    game_over_text = font.render("GAME OVER", True, BLACK)
    game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    score_text = small_font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))

    restart_text = small_font.render("Press SPACE to Restart", True, BLACK)
    restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))

    screen.blit(game_over_text, game_over_rect)
    screen.blit(score_text, score_rect)
    screen.blit(restart_text, restart_rect)

def start_screen():
    """Displays the start screen."""
    title_text = font.render("Flappy Biry", True, BLACK)
    title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))

    instructions_text = small_font.render("Press SPACE to Start", True, BLACK)
    instructions_rect = instructions_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

    screen.blit(title_text, title_rect)
    screen.blit(instructions_text, instructions_rect)

# --- Game Loop ---
running = True
clock = pygame.time.Clock()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if not game_active:
                    # Reset game variables if starting/restarting
                    bird_y = SCREEN_HEIGHT // 2
                    bird_velocity = 0
                    pipes = []
                    score = 0
                    game_active = True
                    last_pipe_spawn_time = pygame.time.get_ticks() # Reset spawn timer
                else:
                    # Bird jump during active game
                    bird_velocity = jump_power

    # --- Game Logic ---
    if game_active:
        # Apply gravity
        bird_velocity += gravity
        bird_y += bird_velocity

        # Keep bird within screen limits (top)
        if bird_y < 0:
            bird_y = 0
            bird_velocity = 0 # Stop upward movement if hitting top

        # Handle pipe spawning
        current_time = pygame.time.get_ticks()
        if current_time - last_pipe_spawn_time > PIPE_SPAWN_INTERVAL:
            create_pipe()
            last_pipe_spawn_time = current_time

        # Move and update pipes
        pipes = move_pipes(pipes)

        # Create bird rectangle for collision detection
        bird_rect = pygame.Rect(bird_x, bird_y, bird_width, bird_height)

        # Check for collisions
        if check_collision(bird_rect, pipes):
            game_active = False # Game over!

        # Update score
        score = update_score(bird_rect, pipes, score)

    # --- Drawing ---
    screen.fill(WHITE) # Fill background

    # Draw ground
    pygame.draw.rect(screen, (100, 200, 50), (ground_x, ground_y, SCREEN_WIDTH, GROUND_HEIGHT), border_radius=5) # Greenish ground

    if game_active:
        draw_pipes(pipes)
        draw_bird(bird_x, bird_y)
        display_score(score)
    elif score > 0: # Game over state (after playing)
        game_over_screen(score)
    else: # Start screen state (before playing for the first time)
        start_screen()
        draw_bird(bird_x, bird_y) # Show the bird on the start screen too

    pygame.display.update() # Update the full display

    # Cap the frame rate
    clock.tick(60) # 60 frames per second

pygame.quit() # Uninitialize Pygame
