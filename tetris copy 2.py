from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
from telegram.ext import MessageHandler, filters
import os
import random
import sys
from copy import deepcopy

MOVE_LEFT = 'move_left'
MOVE_RIGHT = 'move_right'
ROTATE_ANTICLOCKWISE = 'rotate_anticlockwise'
ROTATE_CLOCKWISE = 'rotate_clockwise'
NO_MOVE = 'no_move'
QUIT_GAME = 'quit_game'

BOARD_SIZE = 20
EFF_BOARD_SIZE = BOARD_SIZE + 2

PIECES = [
    [[1], [1], [1], [1]],
    [[1, 0],
     [1, 0],
     [1, 1]],
    [[0, 1],
     [0, 1],
     [1, 1]],
    [[0, 1],
     [1, 1],
     [1, 0]],
    [[1, 1],
     [1, 1]]
]

def print_board(board, cur_piece, piece_pos, error_message=''):
    board_copy = deepcopy(board)
    curr_piece_size_x = len(cur_piece)
    curr_piece_size_y = len(cur_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            board_copy[piece_pos[0]+i][piece_pos[1]+j] = cur_piece[i][j] | board[piece_pos[0]+i][piece_pos[1]+j]

    # Print the board to a string
    board_str = ""
    for i in range(EFF_BOARD_SIZE):
        for j in range(EFF_BOARD_SIZE):
            if board_copy[i][j] == 1:
                board_str += "*"
            else:
                board_str += " "
        board_str += "\n"

    board_str += "Quick play instructions:\n"
    board_str += " - Use buttons to move and rotate the piece\n"
    if error_message:
        board_str += error_message + "\n"
    return board_str

def init_board():
    board = [[0 for x in range(EFF_BOARD_SIZE)] for y in range(EFF_BOARD_SIZE)]
    for i in range(EFF_BOARD_SIZE):
        board[i][0] = 1
    for i in range(EFF_BOARD_SIZE):
        board[EFF_BOARD_SIZE-1][i] = 1
    for i in range(EFF_BOARD_SIZE):
        board[i][EFF_BOARD_SIZE-1] = 1
    return board

def get_random_piece():
    piece_index = random.randrange(len(PIECES))
    return PIECES[piece_index]

def get_random_position(curr_piece):
    curr_piece_size = len(curr_piece)

    # This x refers to rows, rows go along y-axis
    x = 0
    # This y refers to columns, columns go along x-axis
    y = random.randrange(1, EFF_BOARD_SIZE-curr_piece_size)
    return [x, y]

def overlap_check(board, curr_piece, piece_pos):
    curr_piece_size_x = len(curr_piece)
    curr_piece_size_y = len(curr_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            if board[piece_pos[0]+i][piece_pos[1]+j] == 1 and curr_piece[i][j] == 1:
                return False
    return True

def can_move_left(board, curr_piece, piece_pos):
    piece_pos = [piece_pos[0], piece_pos[1] - 1]
    return overlap_check(board, curr_piece, piece_pos)

def can_move_right(board, curr_piece, piece_pos):
    piece_pos = [piece_pos[0], piece_pos[1] + 1]
    return overlap_check(board, curr_piece, piece_pos)

def can_move_down(board, curr_piece, piece_pos):
    piece_pos = [piece_pos[0] - 1, piece_pos[1]]
    return overlap_check(board, curr_piece, piece_pos)

def can_rotate_anticlockwise(board, curr_piece, piece_pos):
    curr_piece = rotate_anticlockwise(curr_piece)
    return overlap_check(board, curr_piece, piece_pos)

def can_rotate_clockwise(board, curr_piece, piece_pos):
    curr_piece = rotate_clockwise(curr_piece)
    return overlap_check(board, curr_piece, piece_pos)

def rotate_clockwise(piece):
    piece_copy = deepcopy(piece)
    reverse_piece = piece_copy[::-1]
    return list(list(elem) for elem in zip(*reverse_piece))

def rotate_anticlockwise(piece):
    piece_copy = deepcopy(piece)
    piece_1 = rotate_clockwise(piece_copy)
    piece_2 = rotate_clockwise(piece_1)
    return rotate_clockwise(piece_2)

def merge_board_and_piece(board, curr_piece, piece_pos):
    curr_piece_size_x = len(curr_piece)
    curr_piece_size_y = len(curr_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            board[piece_pos[0]+i][piece_pos[1]+j] = curr_piece[i][j] | board[piece_pos[0]+i][piece_pos[1]+j]

    empty_row = [0]*EFF_BOARD_SIZE
    empty_row[0] = 1
    empty_row[EFF_BOARD_SIZE-1] = 1

    filled_row = [1]*EFF_BOARD_SIZE

    filled_rows = 0
    for row in board:
        if row == filled_row:
            filled_rows += 1

    filled_rows -= 1

    for i in range(filled_rows):
        board.remove(filled_row)

    for i in range(filled_rows):
        board.insert(0, empty_row)

def is_game_over(board, curr_piece, piece_pos):
    if not can_move_down(board, curr_piece, piece_pos) and piece_pos[0] == 0:
        return True
    return False

async def tetris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    board = init_board()
    curr_piece = get_random_piece()
    piece_pos = get_random_position(curr_piece)
    board_str = print_board(board, curr_piece, piece_pos)

    keyboard = [
        [InlineKeyboardButton("Left", callback_data=MOVE_LEFT),
         InlineKeyboardButton("Right", callback_data=MOVE_RIGHT)],
        [InlineKeyboardButton("Rotate CCW", callback_data=ROTATE_ANTICLOCKWISE),
         InlineKeyboardButton("Rotate CW", callback_data=ROTATE_CLOCKWISE)],
        [InlineKeyboardButton("Move Down", callback_data=NO_MOVE),
         InlineKeyboardButton("Quit", callback_data=QUIT_GAME)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await update.message.reply_text(board_str, reply_markup=reply_markup)
    
    context.user_data["board"] = board
    context.user_data["curr_piece"] = curr_piece
    context.user_data["piece_pos"] = piece_pos
    context.user_data["message_id"] = message.message_id

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    board = context.user_data["board"]
    curr_piece = context.user_data["curr_piece"]
    piece_pos = context.user_data["piece_pos"]

    player_move = query.data
    ERR_MSG = ""
    do_move_down = False

    if player_move == MOVE_LEFT:
        if can_move_left(board, curr_piece, piece_pos):
            piece_pos[1] -= 1
        else:
            ERR_MSG = "Cannot move left"
    elif player_move == MOVE_RIGHT:
        if can_move_right(board, curr_piece, piece_pos):
            piece_pos[1] += 1
        else:
            ERR_MSG = "Cannot move right"
    elif player_move == ROTATE_CLOCKWISE:
        if can_rotate_clockwise(board, curr_piece, piece_pos):
            curr_piece = rotate_clockwise(curr_piece)
        else:
            ERR_MSG = "Cannot rotate clockwise"
    elif player_move == ROTATE_ANTICLOCKWISE:
        if can_rotate_anticlockwise(board, curr_piece, piece_pos):
            curr_piece = rotate_anticlockwise(curr_piece)
        else:
            ERR_MSG = "Cannot rotate anticlockwise"
    elif player_move == NO_MOVE:
        if can_move_down(board, curr_piece, piece_pos):
            piece_pos[0] += 1
        else:
            merge_board_and_piece(board, curr_piece, piece_pos)
            curr_piece = get_random_piece()
            piece_pos = get_random_position(curr_piece)
            if is_game_over(board, curr_piece, piece_pos):
                await query.edit_message_text("Game over")
                return
        do_move_down = True
    elif player_move == QUIT_GAME:
        await query.edit_message_text("Game over")
        return
    
    board_str = print_board(board, curr_piece, piece_pos, ERR_MSG)
    
    if not do_move_down:
        await query.edit_message_text(board_str, reply_markup=query.message.reply_markup)
    
    context.user_data["board"] = board
    context.user_data["curr_piece"] = curr_piece
    context.user_data["piece_pos"] = piece_pos

def main():
    application = ApplicationBuilder().token("6501099925:AAHr2X9g1QdM82VWIcNFBK2_p_0Gym6I6RI").build()

    application.add_handler(CommandHandler("tetris", tetris))
    application.add_handler(CallbackQueryHandler(button))

    application.run_polling()

if __name__ == "__main__":
    main()