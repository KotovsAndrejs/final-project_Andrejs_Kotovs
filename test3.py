import curses
import random
import time

# Конфигурация игры
BOARD_WIDTH = 10
BOARD_HEIGHT = 20
TETROMINOS = [
    [[1, 1, 1, 1]],                # I
    [[1, 1, 1], [0, 1, 0]],        # T
    [[1, 1], [1, 1]],              # O
    [[1, 1, 0], [0, 1, 1]],        # S
    [[0, 1, 1], [1, 1, 0]],        # Z
    [[1, 1, 1], [1, 0, 0]],        # L
    [[1, 1, 1], [0, 0, 1]]         # J
]

# Функции для работы с тетрисом
def create_board():
    return [[0 for _ in range(BOARD_WIDTH)] for _ in range(BOARD_HEIGHT)]

def draw_board(stdscr, board, score):
    stdscr.clear()
    for y, row in enumerate(board):
        for x, cell in enumerate(row):
            stdscr.addch(y, x, '#' if cell else '.')
    stdscr.addstr(BOARD_HEIGHT, 0, f'Score: {score}')
    stdscr.refresh()

def check_collision(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                if (y + off_y >= BOARD_HEIGHT or
                    x + off_x >= BOARD_WIDTH or
                    x + off_x < 0 or
                    board[y + off_y][x + off_x]):
                    return True
    return False

def merge_shape(board, shape, offset):
    off_x, off_y = offset
    for y, row in enumerate(shape):
        for x, cell in enumerate(row):
            if cell:
                board[y + off_y][x + off_x] = cell

def remove_full_lines(board):
    new_board = [row for row in board if any(cell == 0 for cell in row)]
    full_lines = BOARD_HEIGHT - len(new_board)
    new_board = [[0] * BOARD_WIDTH for _ in range(full_lines)] + new_board
    return new_board, full_lines

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    board = create_board()
    current_shape = random.choice(TETROMINOS)
    current_pos = [0, BOARD_WIDTH // 2 - len(current_shape[0]) // 2]
    score = 0

    while True:
        draw_board(stdscr, board, score)
        next_pos = current_pos[:]
        key = stdscr.getch()

        if key == curses.KEY_DOWN:
            next_pos[0] += 1
        if key == curses.KEY_LEFT:
            next_pos[1] -= 1
        if key == curses.KEY_RIGHT:
            next_pos[1] += 1
        if key == curses.KEY_UP:
            rotated_shape = rotate(current_shape)
            if not check_collision(board, rotated_shape, current_pos):
                current_shape = rotated_shape

        if not check_collision(board, current_shape, next_pos):
            current_pos = next_pos
        else:
            if next_pos[0] == current_pos[0] + 1:
                merge_shape(board, current_shape, current_pos)
                board, lines = remove_full_lines(board)
                score += lines
                current_shape = random.choice(TETROMINOS)
                current_pos = [0, BOARD_WIDTH // 2 - len(current_shape[0]) // 2]
                if check_collision(board, current_shape, current_pos):
                    break

        current_pos[0] += 1
        if check_collision(board, current_shape, current_pos):
            current_pos[0] -= 1

        merge_shape(board, [[0] * len(row) for row in current_shape], current_pos)
        merge_shape(board, current_shape, current_pos)
        time.sleep(0.1)

    stdscr.addstr(BOARD_HEIGHT // 2, BOARD_WIDTH // 2 - 5, "Game Over")
    stdscr.refresh()
    time.sleep(2)

curses.wrapper(main)