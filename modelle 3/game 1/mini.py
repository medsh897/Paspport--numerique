#'                  ___.       _____     __      ___.           
#'    __  _  __ ____\_ |__    /  |  |   |__| ____\_ |__   ______
#'    \ \/ \/ // __ \| __ \  /   |  |_  |  |/  _ \| __ \ /  ___/
#'     \     /\  ___/| \_\ \/    ^   /  |  (  <_> ) \_\ \\___ \ 
#'      \/\_/  \___  >___  /\____   /\__|  |\____/|___  /____  >
#'                 \/    \/      |__\______|          \/     \/           
import pygame
import random
import json
import os

# التهيئة
pygame.init()
pygame.mixer.init()

# الإعدادات
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
FPS = 10

# الألوان
BLACK, WHITE, GREEN, RED, BLUE = (0,0,0), (255,255,255), (0,255,0), (255,0,0), (0,0,255)

# إنشاء الأصوات بطريقة أبسط
def create_beep(frequency=440, duration=100):
    sample_rate = 44100
    n_samples = int(sample_rate * duration / 1000.0)
    buf = bytearray()
    
    for i in range(n_samples):
        sample = int(127 * (1 if (i // (sample_rate // frequency)) % 2 == 0 else -1))
        buf.append(127 + sample)
        buf.append(127 + sample)  # ستيريو
    
    return pygame.mixer.Sound(buffer=bytes(buf))

# إنشاء الأصوات
try:
    eat_sound = create_beep(800, 200)
    game_over_sound = create_beep(300, 500)
    move_sound = create_beep(400, 100)
except:
    # إذا فشل إنشاء الأصوات، نستخدم أصوات صامتة
    eat_sound = pygame.mixer.Sound(buffer=bytes([]))
    game_over_sound = pygame.mixer.Sound(buffer=bytes([]))
    move_sound = pygame.mixer.Sound(buffer=bytes([]))

class Snake:
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.positions = [(15, 15)]
        self.direction = (1, 0)
        self.length = 3
        self.score = 0
        for i in range(1, self.length):
            self.positions.append((15-i, 15))
    
    def move(self):
        head = self.positions[0]
        new_head = ((head[0] + self.direction[0]) % 30, (head[1] + self.direction[1]) % 30)
        if new_head in self.positions[1:]:
            return False
        self.positions.insert(0, new_head)
        if len(self.positions) > self.length:
            self.positions.pop()
        return True
    
    def grow(self):
        self.length += 1
        self.score += 10
        eat_sound.play()
    
    def change_direction(self, new_dir):
        if (new_dir[0] * -1, new_dir[1] * -1) != self.direction:
            self.direction = new_dir
            move_sound.play()

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Snake Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('Arial', 24)
        self.snake = Snake()
        self.food = self.new_food()
        self.high_score = self.load_high_score()
        self.game_over = False
    
    def new_food(self):
        while True:
            pos = (random.randint(0, 29), random.randint(0, 29))
            if pos not in self.snake.positions:
                return pos
    
    def load_high_score(self):
        try:
            if os.path.exists("highscore.json"):
                with open("highscore.json", "r") as f:
                    return json.load(f).get("high_score", 0)
        except:
            return 0
    
    def save_high_score(self):
        try:
            with open("highscore.json", "w") as f:
                json.dump({"high_score": self.high_score}, f)
        except:
            pass
    
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.KEYDOWN:
                    if self.game_over and event.key == pygame.K_SPACE:
                        self.snake.reset()
                        self.food = self.new_food()
                        self.game_over = False
                    elif not self.game_over:
                        if event.key == pygame.K_UP: self.snake.change_direction((0, -1))
                        elif event.key == pygame.K_DOWN: self.snake.change_direction((0, 1))
                        elif event.key == pygame.K_LEFT: self.snake.change_direction((-1, 0))
                        elif event.key == pygame.K_RIGHT: self.snake.change_direction((1, 0))
            
            if not self.game_over:
                if not self.snake.move():
                    self.game_over = True
                    game_over_sound.play()
                    if self.snake.score > self.high_score:
                        self.high_score = self.snake.score
                        self.save_high_score()
                
                if self.snake.positions[0] == self.food:
                    self.snake.grow()
                    self.food = self.new_food()
            
            # الرسم
            self.screen.fill(BLACK)
            
            # رسم الثعبان
            for i, pos in enumerate(self.snake.positions):
                color = BLUE if i == 0 else GREEN
                pygame.draw.rect(self.screen, color, (pos[0]*20, pos[1]*20, 20, 20))
            
            # رسم الطعام
            pygame.draw.rect(self.screen, RED, (self.food[0]*20, self.food[1]*20, 20, 20))
            
            # النتائج
            score_text = self.font.render(f"Score: {self.snake.score}", True, WHITE)
            high_text = self.font.render(f"High: {self.high_score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            self.screen.blit(high_text, (500, 10))
            
            if self.game_over:
                overlay = pygame.Surface((WIDTH, HEIGHT))
                overlay.set_alpha(180)
                overlay.fill(BLACK)
                self.screen.blit(overlay, (0, 0))
                game_over_text = self.font.render("Game Over! Press SPACE", True, RED)
                self.screen.blit(game_over_text, (200, 300))
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    Game().run()