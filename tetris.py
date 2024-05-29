from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import random
from copy import deepcopy
import json
import os

move_left = 'move_left'
move_right = 'move_right'
rotate_protivchas = 'rotate_protivchas'
rotate_pochas = 'rotate_pochas'
move_down = 'move_down'
quit_game = 'quit_game'

board_size = 10
new_board_size = board_size + 2
scores = []
scores_file = open('global_score.json') # opening JSON file
scores = json.load(scores_file) # returns JSON object as a dictionary
scores_file.close() # Closing file
pieces = [
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
    [[0, 1],
     [1, 1],
     [0, 1]],
    [[1, 0],
     [1, 1],
     [0, 1]],
    [[1, 1],
     [1, 1]]
]

def load_total_score():
    with open('total_score.json', 'r') as file:
        return json.load(file)

def save_total_score(total_score):
    with open('total_score.json', 'w') as file:
        json.dump(total_score, file)

def print_board(board, cur_piece, piece_pos, error_message='', score=0):
    board_copy = deepcopy(board)
    curr_piece_size_x = len(cur_piece)
    curr_piece_size_y = len(cur_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            board_copy[piece_pos[0] + i][piece_pos[1] + j] = cur_piece[i][j] | board[piece_pos[0] + i][piece_pos[1] + j]

    board_str = ""
    for i in range(new_board_size):
        for j in range(new_board_size):
            if board_copy[i][j] == 1:
                board_str += "1"
            else:
                board_str += ">"
        board_str += "\n"

    board_str += f"Score: {score}\n"
    board_str += "Quick play instructions:\n"
    board_str += " - Use buttons to move and rotate the piece\n"
    if error_message:
        board_str += error_message + "\n"
    return board_str

def init_board():
    board = [[0 for b in range(new_board_size)] for c in range(new_board_size)]
    for i in range(new_board_size):
        board[i][0] = 1
        board[i][new_board_size-1] = 1
    for i in range(new_board_size):
        board[new_board_size-1][i] = 1
    return board

def get_random_piece():
    piece_index = random.randrange(len(pieces))
    return pieces[piece_index]

def get_random_position(curr_piece):
    curr_piece_len = len(curr_piece[0])
    x = 0
    y = random.randrange(1, new_board_size - curr_piece_len - 1)
    return [x, y]

def overlap_check(board, curr_piece, piece_pos):
    curr_piece_len_x = len(curr_piece)
    curr_piece_len_y = len(curr_piece[0])
    for i in range(curr_piece_len_x):
        for j in range(curr_piece_len_y):
            if board[piece_pos[0] + i][piece_pos[1] + j] == 1 and curr_piece[i][j] == 1:
                return False
    return True

def can_move_left(board, curr_piece, piece_pos):
    piece_pos = [piece_pos[0], piece_pos[1] - 1]
    return overlap_check(board, curr_piece, piece_pos)

def can_move_right(board, curr_piece, piece_pos):
    piece_pos = [piece_pos[0], piece_pos[1] + 1]
    return overlap_check(board, curr_piece, piece_pos)

def can_move_down(board, curr_piece, piece_pos):
    piece_pos = [piece_pos[0] + 1, piece_pos[1]]
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
    global score
    curr_piece_size_x = len(curr_piece)
    curr_piece_size_y = len(curr_piece[0])
    for i in range(curr_piece_size_x):
        for j in range(curr_piece_size_y):
            board[piece_pos[0] + i][piece_pos[1] + j] = curr_piece[i][j] | board[piece_pos[0] + i][piece_pos[1] + j]

    empty_row = [0] * new_board_size
    empty_row[0] = 1
    empty_row[new_board_size-1] = 1

    filled_row = [1] * new_board_size

    filled_rows = 0
    for i in range(1, new_board_size - 1):
        if board[i] == filled_row:
            filled_rows += 1

    for a in range(filled_rows):
        board.remove(filled_row)
        board.insert(1, empty_row)  
        score += 100
        score_2 = {"Score":score
                    }
        scores.append(score_2)

def is_game_over(board, curr_piece, piece_pos):
    if not can_move_down(board, curr_piece, piece_pos) and piece_pos[0] == 0:
        return True
    return False

async def tetris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global score
    score = 0
    board = init_board()
    curr_piece = get_random_piece()
    piece_pos = get_random_position(curr_piece)
    board_str = print_board(board, curr_piece, piece_pos, score=score)

    keyboard = [
        [InlineKeyboardButton("Left", callback_data=move_left),
         InlineKeyboardButton("Right", callback_data=move_right)],
        [InlineKeyboardButton("Rotate CCW", callback_data=rotate_protivchas),
         InlineKeyboardButton("Rotate CW", callback_data=rotate_pochas)],
        [InlineKeyboardButton("Move Down", callback_data=move_down),
         InlineKeyboardButton("Quit", callback_data=quit_game)]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message = await update.message.reply_text(board_str, reply_markup=reply_markup)
    
    context.user_data["board"] = board
    context.user_data["curr_piece"] = curr_piece
    context.user_data["piece_pos"] = piece_pos
    context.user_data["message_id"] = message.message_id

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global score
    query = update.callback_query
    await query.answer()

    board = context.user_data["board"]
    curr_piece = context.user_data["curr_piece"]
    piece_pos = context.user_data["piece_pos"]

    player_move = query.data
    err_message = ""
    do_move_down = False

    if player_move == move_left:
        if can_move_left(board, curr_piece, piece_pos):
            piece_pos[1] -= 1
        else:
            err_message = "Cannot move left"
    elif player_move == move_right:
        if can_move_right(board, curr_piece, piece_pos):
            piece_pos[1] += 1
        else:
            err_message = "Cannot move right"
    elif player_move == rotate_pochas:
        if can_rotate_clockwise(board, curr_piece, piece_pos):
            curr_piece = rotate_clockwise(curr_piece)
        else:
            err_message = "Cannot rotate clockwise"
    elif player_move == rotate_protivchas:
        if can_rotate_anticlockwise(board, curr_piece, piece_pos):
            curr_piece = rotate_anticlockwise(curr_piece)
        else:
            err_message = "Cannot rotate anticlockwise"
    elif player_move == move_down:
        if can_move_down(board, curr_piece, piece_pos):
            piece_pos[0] += 1
        else:
            merge_board_and_piece(board, curr_piece, piece_pos)
            curr_piece = get_random_piece()
            piece_pos = get_random_position(curr_piece)
            if is_game_over(board, curr_piece, piece_pos):
                await query.edit_message_text("Game over")
                with open("global_score.json", "w") as file:
                    json.dump(scores, file)
                return
        do_move_down = True
    elif player_move == quit_game:
        await query.edit_message_text("Game over")
        with open("global_score.json", "w") as file:
            json.dump(scores, file)
        return

    board_str = print_board(board, curr_piece, piece_pos, err_message, score)
    
    if not do_move_down:
        await query.edit_message_text(board_str, reply_markup=query.message.reply_markup)
    else:
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
