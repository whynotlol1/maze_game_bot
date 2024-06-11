from Crypto.Util.number import long_to_bytes
from maze_game.bot import data_api
from dotenv import load_dotenv
from base64 import b64decode
from telebot import TeleBot
from telebot import types
from os import getenv
import telebot

load_dotenv()

bot = TeleBot(token=b64decode(long_to_bytes(int(getenv("bottoken")))).decode())


@bot.callback_query_handler(lambda call: call.data.startswith("action"))
def callback_query_handler(call: telebot.types.CallbackQuery):
    match call.data.replace(":", ".").split(".")[1]:
        case "start":
            uuid = data_api.create_new_game(user_id=int(call.data.split(":")[2]))
            with open("maze_game/data/message_strings/new_game.txt", "r") as message_file:
                bot.send_message(call.message.chat.id, f"{message_file.read()}\n<b>Your game UUID: {uuid}</b>", parse_mode="html")


@bot.message_handler(commands=["start"])
def start_command_handler(message: telebot.types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="Start!", callback_data=f"action:start.user:{message.from_user.id}")
    )
    if data_api.check_if_user_has_save_file(user_id=message.from_user.id):
        markup.add(
            types.InlineKeyboardButton(text="Load saved game!", callback_data=f"action:load;user:{message.from_user.id}")
        )
    with open("maze_game/data/message_strings/start.txt", "r") as message_file:
        bot.send_message(message.chat.id, message_file.read(), parse_mode="html", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def on_command_error(message: telebot.types.Message):
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Unknown command. Use <b>/help</b> for a list of commands.", parse_mode="html")
