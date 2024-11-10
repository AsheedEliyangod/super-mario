import pygame
import os

# Initialize Pygame
pygame.init()

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 570
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Super Mario")

# Define paths
current_path = os.path.dirname(__file__)  # Get the directory of the script
image_folder = os.path.join(current_path, 'images')

# Load and resize images
try:
    super_image_raw = pygame.image.load(os.path.join(image_folder, 'super.png'))
    background_image_raw = pygame.image.load(os.path.join(image_folder, 'background.png'))
    pipe_image_raw = pygame.image.load(os.path.join(image_folder, 'pipe.png'))  # Load pipe image

    # Resize images
    super_image = pygame.transform.scale(super_image_raw, (75, 75))
    background_image = pygame.transform.scale(background_image_raw, (750, 550))
    pipe_image = pygame.transform.scale(pipe_image_raw, (83, 105))  # Rescale pipe image

    print("Images loaded and resized successfully!")
except FileNotFoundError as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    exit()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Super class for the character
class Super(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = super_image
        self.rect = self.image.get_rect()
        self.rect.x = 50  # Start from the left side of the screen
        self.rect.y = 200  # Start with a small height above the ground for falling effect
        self.vel_y = 0
        self.jump = False
        self.jump_force = -15
        self.gravity = 1
        self.jump_hold_time = 0
        self.max_jump_hold = 15
        self.world_x = 0  # Track character's position in the world

    def update(self, keys, obstacles):
        # Jumping mechanism
        if keys[pygame.K_SPACE]:
            if not self.jump:
                self.vel_y = self.jump_force
                self.jump = True
                self.jump_hold_time = 0
            elif self.jump and self.jump_hold_time < self.max_jump_hold:
                self.vel_y = self.jump_force
                self.jump_hold_time += 1
        else:
            self.jump_hold_time = self.max_jump_hold

        # Apply gravity and update position
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Control player's baseline height from the bottom of the screen
        player_ground_level = SCREEN_HEIGHT - 68
        if self.rect.bottom >= player_ground_level:
            self.rect.bottom = player_ground_level
            self.vel_y = 0
            self.jump = False

        # Move character left or right
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.world_x -= 5
        if keys[pygame.K_RIGHT] and self.rect.centerx < SCREEN_WIDTH // 2:
            self.rect.x += 5  # Move the player until it reaches the center of the screen
        elif keys[pygame.K_RIGHT]:
            self.world_x += 5  # Scroll the world when player is at the center

        # Check for collision with obstacles (pipe)
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                # Check if standing on top of the obstacle
                if self.rect.bottom <= obstacle.rect.top + 10 and self.vel_y >= 0:
                    self.rect.bottom = obstacle.rect.top
                    self.vel_y = 0
                    self.jump = False
                elif self.rect.right > obstacle.rect.left and self.rect.left < obstacle.rect.right:
                    # Block movement into the obstacle from the side if not jumping
                    if self.vel_y >= 0:
                        if self.rect.centerx < obstacle.rect.centerx:
                            self.rect.right = obstacle.rect.left
                        else:
                            self.rect.left = obstacle.rect.right

# Obstacle (Pipe) class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, x):
        super().__init__()
        self.image = pipe_image
        self.rect = self.image.get_rect()
        self.initial_x = x
        self.rect.x = x
        player_ground_level = SCREEN_HEIGHT - 68
        self.rect.bottom = player_ground_level

    def update(self, world_x):
        self.rect.x = self.initial_x - world_x

# Function to generate new pipes as the player moves forward
def generate_infinite_pipes(last_pipe_x, distance_between_pipes):
    new_pipe = Obstacle(last_pipe_x + distance_between_pipes)
    return new_pipe

# Main game loop
def main():
    clock = pygame.time.Clock()
    character = Super()

    # Create sprite groups
    all_sprites = pygame.sprite.Group()
    all_sprites.add(character)

    obstacles = pygame.sprite.Group()

    # Add initial pipe
    pipe = Obstacle(400)
    obstacles.add(pipe)

    # Distances for generating new pipes
    last_pipe_x = 400
    pipe_spawn_distance = 500

    # Initialize score
    score = 0
    font = pygame.font.Font(None, 36)

    running = True
    while running:
        clock.tick(60)
        
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    main()

        # Update character and obstacle positions
        character.update(keys, obstacles)
        obstacles.update(character.world_x)

        # Generate new pipes as the player progresses
        if character.world_x > last_pipe_x - SCREEN_WIDTH:
            new_pipe = generate_infinite_pipes(last_pipe_x, pipe_spawn_distance)
            obstacles.add(new_pipe)
            last_pipe_x += pipe_spawn_distance

            # Increase score every time a new pipe is generated
            score += 1

        # Background scrolls based on character's world position for looping effect
        bg_x = -(character.world_x % 750)

        screen.fill(WHITE)
        screen.blit(background_image, (bg_x, 0))
        screen.blit(background_image, (bg_x + 750, 0))

        # Draw all objects
        all_sprites.draw(screen)
        obstacles.draw(screen)

        # Render and display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
