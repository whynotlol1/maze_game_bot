import telebot.types
from Crypto.Util.number import long_to_bytes
from dotenv import load_dotenv
from base64 import b64decode
from telebot import TeleBot
from telebot import types
from os import getenv
import telebot

load_dotenv()

bot = TeleBot(token=b64decode(long_to_bytes(int(getenv("bottoken")))).decode())


@bot.callback_query_handler(lambda call: True)
def callback_query_handler(call: telebot.types.CallbackQuery):
    match call.data.split(":")[0]:
        case "action":
            match call.data.replace(":", ";").split(";")[1]:
                case "start":
                    pass


@bot.message_handler(commands=["start"])
def start_command_handler(message: telebot.types.Message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton(text="Start!", callback_data=f"action:start;user:{message.from_user.id}")
    )
    with open("maze_game/data/message_strings/start.txt", "r") as message_file:
        bot.send_message(message.chat.id, message_file.read(), parse_mode="html", reply_markup=markup)
