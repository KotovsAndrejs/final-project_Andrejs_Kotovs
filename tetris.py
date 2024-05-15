# 
# https://docs.python-telegram-bot.org/en/v21.0.1/index.html
# 
# 1. Uzinstalē bibliotēku
# > pip3 install python-telegram-bot
# 
# 2. Uztaisi jaunu Telegram botu un saņem "token" - https://core.telegram.org/bots/features#creating-a-new-bot
#
# 3. Samaini kodā YOUR_TOKEN ar savu token
# 
# 4. Palaid kodu un ieraksti čatā /start
# 
# 5. Apskaties citas komandas - /hello un /echo
#
# 6. Izmantojot kodu no iepriekšēja piemēra (1_faker.py), izveido jaunu komandu /fakeperson, kura uzģenerē personas vārdu, uzvārdu ar telefona numuru, adresi un personas kodu
# 
# 7. Izmantojot kodu no iepriekšēja piemēra (2_chuck_norris.py), izveido jaunu komandu /chuck, kura uzģenerē jaunu joku par programmetājiem

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from faker import Faker
import requests
fake = Faker()
# izveido bota pieslēgumu Telegram
app = ApplicationBuilder().token("6501099925:AAHr2X9g1QdM82VWIcNFBK2_p_0Gym6I6RI").build()

# komanda /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I'm test bot. Type /hello or /echo")

# komanda /hello
async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(update.effective_user)
    await update.message.reply_text("Hello " + update.effective_user.first_name)

# komanda /echo
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("I hear: " + update.message.text)

# komanda /fakeperson
async def fakeperson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Fake person: " + fake.name() + " " + fake.phone_number() + " " + fake.street_address() + " " + fake.ssn())

def init_board():

    board = [[0 for x in range(edges_board_size)] for y in range(edges_board_size)]
    for i in range(edges_board_size):
        board[i][0] = 1
    for i in range(edges_board_size):
        board[edges_board_size-1][i] = 1
    for i in range(edges_board_size):
        board[i][edges_board_size-1] = 1
    return board
board_size = 20
edges_board_size = board_size+2

async def tetris(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Quick play instructions:")
    await update.message.reply_text(" - a (return): move piece left")
    await update.message.reply_text(" - d (return): move piece right")
    await update.message.reply_text(" - w (return): rotate piece counter clockwise")
    await update.message.reply_text(" - s (return): rotate piece clockwise")
    await update.message.reply_text(" - e (return): move the piece downwards")
    await update.message.reply_text(" - q (return): to quit the game anytime")
    #if error_message:
    #    await update.message.reply_text(error_message)
    await update.message.reply_text("Your move:")




# savieno čata komandu ar funkciju
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("hello", hello))
app.add_handler(CommandHandler("echo", echo))
app.add_handler(CommandHandler("fakeperson", fakeperson))
app.add_handler(CommandHandler("tetris", tetris))


# sāk bota darbību
app.run_polling()