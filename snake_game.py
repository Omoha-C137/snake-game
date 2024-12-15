import pygame
import random
import time

# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH = 800
HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GOLD = (255, 215, 0)  # Color for special food
GREEN = (0, 128, 0)  # Darker green for more realistic snake
LIGHT_GREEN = (0, 255, 0)  # Lighter green for snake highlights

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Snake Game')

# Clock to control game speed
clock = pygame.time.Clock()

# Font for score
font = pygame.font.Font(None, 36)

class Snake:
    def __init__(self):
        self.body = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.grow = False

    def move(self):
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        
        # Wrap around screen
        new_head = (new_head[0] % GRID_WIDTH, new_head[1] % GRID_HEIGHT)
        
        self.body.insert(0, new_head)
        
        if not self.grow:
            self.body.pop()
        else:
            self.grow = False

    def grow_snake(self):
        self.grow = True

    def check_collision(self):
        return len(self.body) != len(set(self.body))

    def draw(self, surface):
        for i, segment in enumerate(self.body):
            # Create a more realistic snake with gradient and shading
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            
            # Head is a bit different
            if i == 0:
                pygame.draw.rect(surface, GREEN, rect)
                # Add some highlights to make it look more interesting
                highlight = pygame.Rect(
                    segment[0] * GRID_SIZE + GRID_SIZE // 4, 
                    segment[1] * GRID_SIZE + GRID_SIZE // 4, 
                    GRID_SIZE // 2, 
                    GRID_SIZE // 2
                )
                pygame.draw.rect(surface, LIGHT_GREEN, highlight)
            else:
                # Body segments with slight variation
                shade = max(0, 128 - i * 2)  # Gradually darken body segments
                body_color = (0, shade, 0)
                pygame.draw.rect(surface, body_color, rect)
                
                # Add subtle border to create depth
                pygame.draw.rect(surface, (0, shade-20, 0), rect, 2)

class Food:
    def __init__(self, snake, is_special=False):
        self.position = self.generate_position(snake)
        self.is_special = is_special
        self.spawn_time = time.time()

    def generate_position(self, snake):
        while True:
            pos = (random.randint(0, GRID_WIDTH-1), random.randint(0, GRID_HEIGHT-1))
            if pos not in snake.body:
                return pos

    def draw(self, surface):
        if self.is_special:
            # Larger, golden special food
            rect = pygame.Rect(
                self.position[0] * GRID_SIZE, 
                self.position[1] * GRID_SIZE, 
                GRID_SIZE * 2, 
                GRID_SIZE * 2
            )
            pygame.draw.rect(surface, GOLD, rect)
            # Add a glow effect
            pygame.draw.rect(surface, (255, 235, 100), rect.inflate(10, 10), 3)
        else:
            # Regular food
            rect = pygame.Rect(self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(surface, RED, rect)
            # Add a small highlight
            highlight = pygame.Rect(
                self.position[0] * GRID_SIZE + GRID_SIZE // 4, 
                self.position[1] * GRID_SIZE + GRID_SIZE // 4, 
                GRID_SIZE // 2, 
                GRID_SIZE // 2
            )
            pygame.draw.rect(surface, (255, 100, 100), highlight)

def main():
    snake = Snake()
    food = Food(snake)
    special_food = None
    special_food_timer = time.time()
    score = 0

    # Game loop
    running = True
    while running:
        current_time = time.time()

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Handle key presses for direction
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and snake.direction != (0, 1):
                    snake.direction = (0, -1)
                elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                    snake.direction = (0, 1)
                elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                    snake.direction = (-1, 0)
                elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                    snake.direction = (1, 0)

        # Move snake
        snake.move()

        # Check for food collision
        if snake.body[0] == food.position:
            snake.grow_snake()
            food = Food(snake)
            score += 1

        # Check for special food collision
        if special_food and len(set(snake.body) & set([(special_food.position), 
                                                       (special_food.position[0]+1, special_food.position[1]),
                                                       (special_food.position[0], special_food.position[1]+1),
                                                       (special_food.position[0]+1, special_food.position[1]+1)])):
            snake.grow_snake()
            snake.grow_snake()  # Grow extra for special food
            special_food = None
            score += 5
            special_food_timer = current_time

        # Spawn special food every 20 seconds
        if not special_food and current_time - special_food_timer >= 20:
            special_food = Food(snake, is_special=True)
            special_food_timer = current_time

        # Remove special food after 10 seconds
        if special_food and current_time - special_food.spawn_time >= 10:
            special_food = None
            special_food_timer = current_time

        # Check for self-collision
        if snake.check_collision():
            running = False

        # Clear screen
        screen.fill(BLACK)

        # Draw food
        food.draw(screen)

        # Draw special food if exists
        if special_food:
            special_food.draw(screen)

        # Draw snake
        snake.draw(screen)

        # Render score on screen
        score_text = font.render(f'Score: {score}', True, WHITE)
        screen.blit(score_text, (10, 10))

        # Update display
        pygame.display.flip()

        # Control game speed
        clock.tick(10)  # 10 FPS

    # Game over screen
    screen.fill(BLACK)
    game_over_text = font.render(f'Game Over! Final Score: {score}', True, WHITE)
    text_rect = game_over_text.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(game_over_text, text_rect)
    pygame.display.flip()

    # Wait before closing
    pygame.time.wait(2000)

    # Quit Pygame
    pygame.quit()

if __name__ == '__main__':
    main()
