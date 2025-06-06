import pygame
import random
from copy import deepcopy

CELL_SIZE = 30
COLS = 10
ROWS = 20
WIDTH = COLS * CELL_SIZE
HEIGHT = ROWS * CELL_SIZE
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
    def __init__(self, shape=None, color=None, x=None, y=None):
        self.shape = shape if shape else random.choice(SHAPES)
        self.color = color if color else random.choice(COLORS)
        self.x = x if x is not None else COLS // 2 - len(self.shape[0]) // 2
        self.y = y if y is not None else 0

    def rotate(self):
        self.shape = [list(row)[::-1] for row in zip(*self.shape)]

    def serialize(self):
        return {
            "shape": self.shape,
            "color": self.color,
            "x": self.x,
            "y": self.y
        }

    @staticmethod
    def deserialize(data):
        return Tetromino(data["shape"], data["color"], data["x"], data["y"])

def create_grid():
    return [[0 for _ in range(COLS)] for _ in range(ROWS)]

def draw_grid(screen, grid):
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            color = GRAY if not cell else cell
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, WHITE, rect, 1)

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
