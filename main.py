
import pygame
import random
import json
from copy import deepcopy

# Константы
CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = CELL_SIZE * COLS
HEIGHT = CELL_SIZE * ROWS
FPS = 60
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
COLORS = [(0, 255, 255), (0, 0, 255), (255, 165, 0),
          (255, 255, 0), (0, 255, 0), (128, 0, 128), (255, 0, 0)]

SHAPES = [
    [[1, 1, 1, 1]],                         # I
    [[1, 1], [1, 1]],                       # O
    [[0, 1, 0], [1, 1, 1]],                 # T
    [[1, 1, 0], [0, 1, 1]],                 # S
    [[0, 1, 1], [1, 1, 0]],                 # Z
    [[1, 0, 0], [1, 1, 1]],                 # J
    [[0, 0, 1], [1, 1, 1]]                  # L
]

class Tetromino:
    def __init__(self, shape=None):
        self.shape = shape if shape else random.choice(SHAPES)
        self.color = random.choice(COLORS)
        self.x = COLS // 2 - len(self.shape[0]) // 2
        self.y = 0

    def rotate(self):
        self.shape = [list(row)[::-1] for row in zip(*self.shape)]

def check_collision(grid, shape, x, y):
    for row_idx, row in enumerate(shape):
        for col_idx, cell in enumerate(row):
            if cell:
                nx = x + col_idx
                ny = y + row_idx
                if nx < 0 or nx >= COLS or ny >= ROWS or (ny >= 0 and grid[ny][nx]):
                    return True
    return False

def merge(grid, tetromino):
    for row_idx, row in enumerate(tetromino.shape):
        for col_idx, cell in enumerate(row):
            if cell:
                grid[tetromino.y + row_idx][tetromino.x + col_idx] = tetromino.color

def clear_lines(grid):
    new_grid = [row for row in grid if any(cell == 0 for cell in row)]
    lines_cleared = ROWS - len(new_grid)
    for _ in range(lines_cleared):
        new_grid.insert(0, [0] * COLS)
    return new_grid, lines_cleared

def create_grid():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def draw_grid(screen, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GRAY if not cell else cell
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 20)

    grid = create_grid()
    current = Tetromino()
    next_shape = Tetromino()
    fall_time = 0
    fall_speed = 500  # ms
    score = 0
    paused = False
    running = True
    game_over = False

    while running:
        screen.fill((0, 0, 0))
        draw_grid(screen, grid)

        for row_idx, row in enumerate(current.shape):
            for col_idx, cell in enumerate(row):
                if cell:
                    x = current.x + col_idx
                    y = current.y + row_idx
                    pygame.draw.rect(screen, current.color, (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused

                if not paused and not game_over:
                    if event.key in [pygame.K_LEFT, pygame.K_a]:
                        if not check_collision(grid, current.shape, current.x - 1, current.y):
                            current.x -= 1
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        if not check_collision(grid, current.shape, current.x + 1, current.y):
                            current.x += 1
                    elif event.key == pygame.K_DOWN:
                        if not check_collision(grid, current.shape, current.x, current.y + 1):
                            current.y += 1
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        rotated = deepcopy(current)
                        rotated.rotate()
                        if not check_collision(grid, rotated.shape, rotated.x, rotated.y):
                            current.rotate()

        if not paused and not game_over:
            fall_time += clock.get_time()
            if fall_time > fall_speed:
                fall_time = 0
                if not check_collision(grid, current.shape, current.x, current.y + 1):
                    current.y += 1
                else:
                    merge(grid, current)
                    grid, lines = clear_lines(grid)
                    score += lines * 100
                    current = next_shape
                    next_shape = Tetromino()
                    if check_collision(grid, current.shape, current.x, current.y):
                        game_over = True

        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if paused and not game_over:
            pause_text = font.render("PAUSED", True, WHITE)
            screen.blit(pause_text, (WIDTH // 2 - 40, HEIGHT // 2))

        if game_over:
            # затемнённый фон под текст
            overlay_height = 100
            overlay_rect = pygame.Surface((WIDTH, overlay_height))
            overlay_rect.set_alpha(200)  # прозрачность: 0–255
            overlay_rect.fill((0, 0, 0))  # чёрный фон
            screen.blit(overlay_rect, (0, HEIGHT // 2 - 50))

            # текст поверх фона
            over_text = font.render("GAME OVER", True, (255, 0, 0))
            final_score = font.render(f"Ваш счёт: {score}", True, WHITE)
            prompt_text = font.render("Нажмите любую клавишу, чтобы выйти", True, WHITE)

            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 - 10))
            screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 20))


        pygame.display.flip()
        clock.tick(FPS)

        if game_over:
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        waiting = False
                        running = False

    pygame.quit()

if __name__ == "__main__":
    main()
