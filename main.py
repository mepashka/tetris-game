import pygame
from tetris import *
from utils import save_game, load_game, save_stats, load_stats

pygame.init()

WIDTH, HEIGHT = COLS * CELL_SIZE, ROWS * CELL_SIZE
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tetris")
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 24)

def draw_text_center(text, y, color=(255, 255, 255)):
    render = font.render(text, True, color)
    screen.blit(render, (WIDTH // 2 - render.get_width() // 2, y))

def menu():
    running = True
    selected = 0
    options = ["Новая игра", "Загрузить игру", "Выход"]

    record = load_stats()["record"]

    while running:
        screen.fill((0, 0, 0))
        draw_text_center("ТЕТРИС", 60, (255, 255, 0))
        draw_text_center(f"Рекорд: {record}", 100)

        for i, option in enumerate(options):
            color = (255, 255, 255) if i != selected else (0, 255, 0)
            draw_text_center(option, 160 + i * 40, color)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected = (selected - 1) % len(options)
                elif event.key == pygame.K_DOWN:
                    selected = (selected + 1) % len(options)
                elif event.key == pygame.K_RETURN:
                    return options[selected].lower()

        clock.tick(30)

def game_loop(grid=None, current=None, next_piece=None, score=0):
    if grid is None:
        grid = create_grid()
    if current is None:
        current = Tetromino()
    if next_piece is None:
        next_piece = Tetromino()

    fall_time = 0
    fall_speed = 500
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

                elif paused and not game_over:
                    if event.key == pygame.K_s:
                        save_game(grid, current, next_piece, score)
                    elif event.key == pygame.K_r:
                        return game_loop()  # перезапуск
                    elif event.key == pygame.K_ESCAPE:
                        return  # выход в меню

                elif not paused and not game_over:
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
                    elif event.key == pygame.K_ESCAPE:
                        running = False



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
                    current = next_piece
                    next_piece = Tetromino()
                    if check_collision(grid, current.shape, current.x, current.y):
                        game_over = True
                        save_stats(score)

        save_game(grid, current, next_piece, score)

        score_text = font.render(f"Счёт: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        if paused and not game_over:
            overlay_height = 140
            overlay_rect = pygame.Surface((WIDTH, overlay_height))
            overlay_rect.set_alpha(200)
            overlay_rect.fill((0, 0, 0))
            screen.blit(overlay_rect, (0, HEIGHT // 2 - 70))

            pause_text = font.render("ПАУЗА", True, WHITE)
            save_text = font.render("S — Сохранить", True, WHITE)
            restart_text = font.render("R — Начать заново", True, WHITE)
            exit_text = font.render("ESC — Выйти в меню", True, WHITE)

            screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
            screen.blit(save_text, (WIDTH // 2 - save_text.get_width() // 2, HEIGHT // 2 - 15))
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 15))
            screen.blit(exit_text, (WIDTH // 2 - exit_text.get_width() // 2, HEIGHT // 2 + 45))


        if game_over:
            overlay_height = 100
            overlay_rect = pygame.Surface((WIDTH, overlay_height))
            overlay_rect.set_alpha(200)
            overlay_rect.fill((0, 0, 0))
            screen.blit(overlay_rect, (0, HEIGHT // 2 - 50))

            over_text = font.render("ИГРА ОКОНЧЕНА", True, (255, 0, 0))
            final_score = font.render(f"Ваш счёт: {score}", True, WHITE)
            prompt_text = font.render("Нажмите любую клавишу", True, WHITE)

            screen.blit(over_text, (WIDTH // 2 - over_text.get_width() // 2, HEIGHT // 2 - 40))
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 - 10))
            screen.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 + 20))

            pygame.display.flip()
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT or event.type == pygame.KEYDOWN:
                        waiting = False
                        running = False

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    while True:
        choice = menu()
        if choice == "новая игра":
            game_loop()
        elif choice == "загрузить игра":
            grid, current, next_piece, score = load_game()
            game_loop(grid, current, next_piece, score)
        elif choice == "выход":
            pygame.quit()
            break

