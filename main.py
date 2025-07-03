import pygame
import random
import sys
import math
import json
from enum import Enum


pygame.init()


GRID_WIDTH = 25
GRID_HEIGHT = 20
CELL_SIZE = 25
WIDTH = GRID_WIDTH * CELL_SIZE
HEIGHT = GRID_HEIGHT * CELL_SIZE + 100  
FPS = 60
MOVE_DELAY = 120  


COLORS = {
    'bg': (20, 25, 40),
    'grid': (40, 45, 60),
    'snake_head': (100, 255, 100),
    'snake_body': (60, 200, 60),
    'snake_tail': (40, 150, 40),
    'food': (255, 100, 100),
    'special_food': (255, 215, 0),
    'wall': (150, 75, 0),
    'text': (255, 255, 255),
    'ui_bg': (30, 35, 50),
    'button': (70, 130, 180),
    'button_hover': (100, 149, 237)
}

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    PAUSED = 3
    GAME_OVER = 4

class FoodType(Enum):
    NORMAL = 1
    SPECIAL = 2

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class Particle:
    def __init__(self, x, y, color, velocity, lifetime):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = random.randint(2, 5)
    
    def update(self, dt):
        self.x += self.velocity[0] * dt
        self.y += self.velocity[1] * dt
        self.lifetime -= dt
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] * 0.98)
    
    def draw(self, surface):
        alpha = max(0, self.lifetime / self.max_lifetime)
        color = (*self.color, int(255 * alpha))
        size = int(self.size * alpha)
        if size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), size)
    
    def is_alive(self):
        return self.lifetime > 0

class Food:
    def __init__(self, pos, food_type=FoodType.NORMAL):
        self.pos = pos
        self.type = food_type
        self.animation_time = 0
        self.scale = 1.0
        self.rotation = 0
    
    def update(self, dt):
        self.animation_time += dt
        self.scale = 1.0 + 0.1 * math.sin(self.animation_time * 0.005)
        self.rotation += dt * 0.002
    
    def draw(self, surface):
        x, y = self.pos[0] * CELL_SIZE + CELL_SIZE // 2, self.pos[1] * CELL_SIZE + CELL_SIZE // 2
        size = int(CELL_SIZE * 0.4 * self.scale)
        
        if self.type == FoodType.SPECIAL:
            # Draw special food with star shape
            color = COLORS['special_food']
            points = []
            for i in range(10):
                angle = self.rotation + i * math.pi / 5
                radius = size if i % 2 == 0 else size * 0.5
                px = x + radius * math.cos(angle)
                py = y + radius * math.sin(angle)
                points.append((px, py))
            if len(points) > 2:
                pygame.draw.polygon(surface, color, points)
        else:
            # Draw normal food as circle
            pygame.draw.circle(surface, COLORS['food'], (x, y), size)
            pygame.draw.circle(surface, (255, 150, 150), (x, y), size, 2)

class Button:
    def __init__(self, x, y, width, height, text, font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.hovered = False
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.hovered:
                return True
        return False
    
    def draw(self, surface):
        color = COLORS['button_hover'] if self.hovered else COLORS['button']
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, COLORS['text'], self.rect, 2)
        
        text_surface = self.font.render(self.text, True, COLORS['text'])
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

class ObstacleSnake:
    def __init__(self, body, direction):
        self.body = body  # list of (x, y)
        self.direction = direction  # Direction enum
        self.move_delay = 200
        self.last_move = 0

    def move(self, grid_width, grid_height, walls, main_snake):
        # Simple AI: move forward, turn if about to hit wall or itself or main snake
        dx, dy = self.direction.value
        head = (self.body[0][0] + dx, self.body[0][1] + dy)
        if (head[0] < 0 or head[0] >= grid_width or
            head[1] < 0 or head[1] >= grid_height or
            head in self.body or head in walls or head in main_snake):
            # Try turning right, then left
            for turn in [1, -1]:
                new_dir = self.turn_direction(turn)
                dx, dy = new_dir.value
                new_head = (self.body[0][0] + dx, self.body[0][1] + dy)
                if (0 <= new_head[0] < grid_width and 0 <= new_head[1] < grid_height and
                    new_head not in self.body and new_head not in walls and new_head not in main_snake):
                    self.direction = new_dir
                    head = new_head
                    break
        self.body.insert(0, head)
        self.body.pop()

    def turn_direction(self, turn):
        dirs = [Direction.UP, Direction.RIGHT, Direction.DOWN, Direction.LEFT]
        idx = dirs.index(self.direction)
        return dirs[(idx + turn) % 4]

    def draw(self, surface):
        for i, pos in enumerate(self.body):
            x, y = pos[0] * CELL_SIZE, pos[1] * CELL_SIZE
            color = (200, 50, 200) if i == 0 else (150, 0, 150)
            pygame.draw.rect(surface, color, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Enhanced Snake Game')
        self.clock = pygame.time.Clock()
        
        
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 48)
        self.font_huge = pygame.font.Font(None, 72)
        
        
        self.state = GameState.MENU
        
        
        self.last_move = 0
        self.move_delay = MOVE_DELAY
        
        
        self.particles = []
        
        
        self.level = 1
        self.max_level = 20
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.obstacle_snakes = []
        self.reset_game()
        
        
        self.create_buttons()
        
        # High score
        self.high_score = self.load_high_score()
        
    def create_buttons(self):
        button_width, button_height = 200, 50
        center_x = WIDTH // 2 - button_width // 2
        
        self.play_button = Button(center_x, 200, button_width, button_height, "PLAY", self.font_medium)
        self.restart_button = Button(center_x, 300, button_width, button_height, "RESTART", self.font_medium)
        self.quit_button = Button(center_x, 400, button_width, button_height, "QUIT", self.font_medium)
    
    def reset_game(self):
        self.level = 1
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.snake = [(self.grid_width // 2, self.grid_height // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.food = None
        self.special_food_timer = 0
        self.walls = []
        self.place_food()
        self.game_over = False
        self.particles.clear()
        self.move_delay = MOVE_DELAY
        self.obstacle_snakes = []
        self.spawn_obstacle_snakes()
        
    def place_food(self):
        while True:
            pos = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
            if pos not in self.snake and pos not in self.walls and all(pos not in obs.body for obs in self.obstacle_snakes):
                self.food = Food(pos, FoodType.NORMAL)
                break
    
    def load_high_score(self):
        try:
            with open('snake_highscore.json', 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open('snake_highscore.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def add_particle_explosion(self, x, y, color, count=10):
        screen_x = x * CELL_SIZE + CELL_SIZE // 2
        screen_y = y * CELL_SIZE + CELL_SIZE // 2
        
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(50, 150)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(500, 1000)
            self.particles.append(Particle(screen_x, screen_y, color, velocity, lifetime))
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_high_score()
                return False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP and self.direction != Direction.DOWN:
                        self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                        self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                        self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                        self.next_direction = Direction.RIGHT
                    elif event.key == pygame.K_SPACE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                
                elif self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = GameState.PLAYING
            
            # Handle button clicks
            if self.play_button.handle_event(event) and self.state == GameState.MENU:
                self.reset_game()
                self.state = GameState.PLAYING
            
            if self.restart_button.handle_event(event) and self.state == GameState.GAME_OVER:
                self.reset_game()
                self.state = GameState.PLAYING
            
            if self.quit_button.handle_event(event):
                self.save_high_score()
                return False
        
        return True
    
    def update_game(self, dt):
        if self.state != GameState.PLAYING:
            return
        
        # Update food animation
        if self.food:
            self.food.update(dt)
        
        # Move snake
        current_time = pygame.time.get_ticks()
        if current_time - self.last_move >= self.move_delay:
            self.last_move = current_time
            self.move_snake()
        
        # Update particles
        for particle in self.particles[:]:
            particle.update(dt)
            if not particle.is_alive():
                self.particles.remove(particle)
        
        # Move obstacle snakes
        for obs in self.obstacle_snakes:
            obs.last_move += dt
            if obs.last_move > obs.move_delay:
                obs.move(self.grid_width, self.grid_height, self.walls, self.snake)
                obs.last_move = 0
    
    def move_snake(self):
        self.direction = self.next_direction
        dx, dy = self.direction.value
        head = (self.snake[0][0] + dx, self.snake[0][1] + dy)
        
        # Check collisions
        if (head[0] < 0 or head[0] >= self.grid_width or
            head[1] < 0 or head[1] >= self.grid_height or
            head in self.snake or head in self.walls):
            self.game_over = True
            self.state = GameState.GAME_OVER
            
            # Update high score
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            
            # Explosion effect
            self.add_particle_explosion(self.snake[0][0], self.snake[0][1], COLORS['snake_head'], 20)
            return
        
        # Check collision with obstacle snakes
        for obs in self.obstacle_snakes:
            if head in obs.body:
                self.game_over = True
                self.state = GameState.GAME_OVER
                return
        
        self.snake.insert(0, head)
        
        # Check food collision
        if self.food and head == self.food.pos:
            self.score += 1
            self.add_particle_explosion(head[0], head[1], COLORS['food'], 8)
            
            # Increase speed slightly
            self.move_delay = max(60, self.move_delay - 2)
            
            self.place_food()
            
            # Level up every 5 points
            if self.score % 5 == 0:
                self.level_up()
        else:
            self.snake.pop()
    
    def draw_grid(self):
        for x in range(self.grid_width + 1):
            pygame.draw.line(self.screen, COLORS['grid'], 
                           (x * CELL_SIZE, 0), (x * CELL_SIZE, self.grid_height * CELL_SIZE))
        for y in range(self.grid_height + 1):
            pygame.draw.line(self.screen, COLORS['grid'], 
                           (0, y * CELL_SIZE), (self.grid_width * CELL_SIZE, y * CELL_SIZE))
        
        # Draw walls
        for wall in self.walls:
            x, y = wall[0] * CELL_SIZE, wall[1] * CELL_SIZE
            pygame.draw.rect(self.screen, COLORS['wall'], (x+2, y+2, CELL_SIZE-4, CELL_SIZE-4))
    
    def draw_snake(self):
        for i, pos in enumerate(self.snake):
            x, y = pos[0] * CELL_SIZE, pos[1] * CELL_SIZE
            
            if i == 0:  # Head
                color = COLORS['snake_head']
                # Draw head with eyes
                pygame.draw.rect(self.screen, color, (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                
                # Eyes based on direction
                eye_size = 3
                if self.direction == Direction.UP:
                    eye1_pos = (x + 6, y + 8)
                    eye2_pos = (x + CELL_SIZE - 9, y + 8)
                elif self.direction == Direction.DOWN:
                    eye1_pos = (x + 6, y + CELL_SIZE - 11)
                    eye2_pos = (x + CELL_SIZE - 9, y + CELL_SIZE - 11)
                elif self.direction == Direction.LEFT:
                    eye1_pos = (x + 8, y + 6)
                    eye2_pos = (x + 8, y + CELL_SIZE - 9)
                else:  # RIGHT
                    eye1_pos = (x + CELL_SIZE - 11, y + 6)
                    eye2_pos = (x + CELL_SIZE - 11, y + CELL_SIZE - 9)
                
                pygame.draw.circle(self.screen, COLORS['text'], eye1_pos, eye_size)
                pygame.draw.circle(self.screen, COLORS['text'], eye2_pos, eye_size)
                
            elif i == len(self.snake) - 1:  # Tail
                color = COLORS['snake_tail']
                pygame.draw.rect(self.screen, color, (x + 3, y + 3, CELL_SIZE - 6, CELL_SIZE - 6))
            else:  # Body
                color = COLORS['snake_body']
                pygame.draw.rect(self.screen, color, (x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2))
        
        # Draw obstacle snakes
        for obs in self.obstacle_snakes:
            obs.draw(self.screen)
    
    def draw_ui(self):
        # UI background
        ui_rect = pygame.Rect(0, self.grid_height * CELL_SIZE, self.grid_width * CELL_SIZE, 100)
        pygame.draw.rect(self.screen, COLORS['ui_bg'], ui_rect)
        pygame.draw.line(self.screen, COLORS['grid'], (0, self.grid_height * CELL_SIZE), (self.grid_width * CELL_SIZE, self.grid_height * CELL_SIZE), 2)
        
        # Score
        score_text = self.font_medium.render(f"Score: {self.score}", True, COLORS['text'])
        self.screen.blit(score_text, (10, self.grid_height * CELL_SIZE + 10))
        
        # High Score
        high_score_text = self.font_medium.render(f"High Score: {self.high_score}", True, COLORS['text'])
        self.screen.blit(high_score_text, (10, self.grid_height * CELL_SIZE + 40))
        
        # Level
        level_text = self.font_medium.render(f"Level: {self.level}", True, COLORS['special_food'])
        self.screen.blit(level_text, (self.grid_width * CELL_SIZE - 180, self.grid_height * CELL_SIZE + 10))
        
        # Speed indicator
        speed_text = self.font_small.render(f"Speed: {int((MOVE_DELAY - self.move_delay + 60) / 10)}", True, COLORS['text'])
        self.screen.blit(speed_text, (self.grid_width * CELL_SIZE - 180, self.grid_height * CELL_SIZE + 40))
        
        # Length
        length_text = self.font_small.render(f"Length: {len(self.snake)}", True, COLORS['text'])
        self.screen.blit(length_text, (self.grid_width * CELL_SIZE - 180, self.grid_height * CELL_SIZE + 60))
        
        # Controls
        if self.state == GameState.PLAYING:
            controls_text = self.font_small.render("SPACE: Pause", True, COLORS['text'])
            self.screen.blit(controls_text, (self.grid_width * CELL_SIZE - 180, self.grid_height * CELL_SIZE + 80))
    
    def draw_menu(self):
        # Title
        title_text = self.font_huge.render("SNAKE", True, COLORS['text'])
        title_rect = title_text.get_rect(center=(WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.font_medium.render("Enhanced Edition", True, COLORS['snake_head'])
        subtitle_rect = subtitle_text.get_rect(center=(WIDTH // 2, 150))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # High score
        if self.high_score > 0:
            high_score_text = self.font_medium.render(f"High Score: {self.high_score}", True, COLORS['text'])
            high_score_rect = high_score_text.get_rect(center=(WIDTH // 2, 500))
            self.screen.blit(high_score_text, high_score_rect)
        
        # Controls
        controls = [
            "Arrow Keys: Move",
            "Space: Pause",
            "Enter: Quick Start"
        ]
        
        for i, control in enumerate(controls):
            control_text = self.font_small.render(control, True, COLORS['text'])
            control_rect = control_text.get_rect(center=(WIDTH // 2, 550 + i * 25))
            self.screen.blit(control_text, control_rect)
        
        # Buttons
        self.play_button.draw(self.screen)
        self.quit_button.draw(self.screen)
    
    def draw_pause(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.font_huge.render("PAUSED", True, COLORS['text'])
        pause_rect = pause_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        continue_text = self.font_medium.render("Press SPACE to continue", True, COLORS['text'])
        continue_rect = continue_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
        self.screen.blit(continue_text, continue_rect)
    
    def draw_game_over(self):
        # Semi-transparent overlay
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        game_over_text = self.font_huge.render("GAME OVER", True, COLORS['food'])
        game_over_rect = game_over_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100))
        self.screen.blit(game_over_text, game_over_rect)
        
        # Final score
        final_score_text = self.font_large.render(f"Final Score: {self.score}", True, COLORS['text'])
        final_score_rect = final_score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30))
        self.screen.blit(final_score_text, final_score_rect)
        
        # High score achievement
        if self.score == self.high_score and self.score > 0:
            new_record_text = self.font_medium.render("NEW HIGH SCORE!", True, COLORS['special_food'])
            new_record_rect = new_record_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10))
            self.screen.blit(new_record_text, new_record_rect)
        
        # Instructions
        restart_text = self.font_medium.render("R: Restart    M: Menu", True, COLORS['text'])
        restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
        
        # Restart button
        self.restart_button.draw(self.screen)
    
    def draw(self):
        self.screen.fill(COLORS['bg'])
        
        if self.state == GameState.MENU:
            self.draw_menu()
        
        elif self.state in [GameState.PLAYING, GameState.PAUSED, GameState.GAME_OVER]:
            # Draw game elements
            self.draw_grid()
            self.draw_snake()
            
            # Draw food
            if self.food:
                self.food.draw(self.screen)
            
            # Draw particles
            for particle in self.particles:
                particle.draw(self.screen)
            
            self.draw_ui()
            
            # Draw overlays
            if self.state == GameState.PAUSED:
                self.draw_pause()
            elif self.state == GameState.GAME_OVER:
                self.draw_game_over()
        
        pygame.display.flip()
    
    def run(self):
        running = True
        dt = 0
        
        while running:
            dt = self.clock.tick(FPS)
            
            running = self.handle_events()
            self.update_game(dt)
            self.draw()
        
        pygame.quit()
        sys.exit()

    def spawn_obstacle_snakes(self):
        self.obstacle_snakes = []
        if self.level >= 5:
            for i in range(min((self.level - 4), 3)):
                # Place obstacle snake at random location
                while True:
                    pos = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
                    if pos not in self.snake and pos not in self.walls:
                        break
                direction = random.choice(list(Direction))
                body = [pos]
                self.obstacle_snakes.append(ObstacleSnake(body, direction))

    def level_up(self):
        if self.level < self.max_level:
            self.level += 1
            # Increase grid size every 3 levels, up to a max
            if self.level % 3 == 0 and self.grid_width < 40 and self.grid_height < 30:
                self.grid_width += 2
                self.grid_height += 2
                self.screen = pygame.display.set_mode((self.grid_width * CELL_SIZE, self.grid_height * CELL_SIZE + 100))
            # Increase speed
            self.move_delay = max(40, self.move_delay - 8)
            # Add more walls
            for _ in range(self.level // 2):
                while True:
                    pos = (random.randint(0, self.grid_width - 1), random.randint(0, self.grid_height - 1))
                    if pos not in self.snake and pos not in self.walls and (self.food is None or pos != self.food.pos):
                        self.walls.append(pos)
                        break
            # Add more obstacle snakes
            self.spawn_obstacle_snakes()

if __name__ == '__main__':
    game = SnakeGame()
    game.run()