from Crypto.Util.number import long_to_bytes
from maze_game.bot import data_api
from dotenv import load_dotenv
from base64 import b64decode
from telebot import TeleBot
from telebot import types
from os import remove
from os import getenv
import telebot

load_dotenv()

bot = TeleBot(token=b64decode(long_to_bytes(int(getenv("bottoken")))).decode())


@bot.callback_query_handler(lambda call: call.data.startswith("action"))
def callback_query_handler(call: telebot.types.CallbackQuery):
    match call.data.replace(":", ".").split(".")[1]:
        case "start":
            data_api.create_new_game(user_id=int(call.data.split(":")[2]))
            bot.edit_message_text(f"Welcome to <i>The Maze</i>!", call.message.chat.id, call.message.id, parse_mode="html")
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "load":
            bot.edit_message_text(f"Welcome back to <i>The Maze</i>!", call.message.chat.id, call.message.id, parse_mode="html")
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))


@bot.message_handler(commands=["start"])
def start_command_handler(message: telebot.types.Message):
    markup = types.InlineKeyboardMarkup()
    if data_api.check_if_user_has_save_file(user_id=message.from_user.id):
        markup.add(
            types.InlineKeyboardButton(text="Load saved game!", callback_data=f"action:load.user:{message.from_user.id}")
        )
    else:
        markup.add(
            types.InlineKeyboardButton(text="Start!", callback_data=f"action:start.user:{message.from_user.id}")
        )
    with open("maze_game/data/message_strings/start.txt", "r") as message_file:
        bot.send_message(message.chat.id, message_file.read(), parse_mode="html", reply_markup=markup)


@bot.callback_query_handler(lambda call: call.data.startswith("game"))
def callback_query_handler(call: telebot.types.CallbackQuery):
    match call.data.replace(":", ".").split(".")[1]:
        case "move_up":
            data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="up")
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "move_left":
            data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="left")
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "move_down":
            data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="down")
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "move_right":
            data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="right")
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "spells_menu":  # TODO v0.0.8b
            pass
        case "inventory_menu":
            message_text = ""
            inventory = data_api.get_inventory(user_id=int(call.data.split(":")[2]))
            markup = types.InlineKeyboardMarkup()
            for i in range(5):
                markup.add(
                    types.InlineKeyboardButton(text=f"Slot {i+1} {"(active)" if inventory[i][1] == "active" else ""}", callback_data=f"game:inventory.inventroy:slot_choose_{i}.user:{int(call.data.split(":")[2])}"),
                )
            markup.add(types.InlineKeyboardButton(text="Back to maze.", callback_data=f"game:continue.user:{int(call.data.split(":")[2])}"))
            for i in range(len(inventory)):
                message_text += f"<i>Slot {i+1}</i>: <b>TODO: data_api.get_item(item_id={inventory[i][0]})</b>\n"  # TODO v0.0.9b
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, message_text, reply_markup=markup,  parse_mode="html")
        case "settings_menu":
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(text="Save game and quit.", callback_data=f"game:stop.user:{int(call.data.split(":")[2])}"),
                types.InlineKeyboardButton(text="Continue.", callback_data=f"game:continue.user:{int(call.data.split(":")[2])}")
            )
            markup.row(
                types.InlineKeyboardButton(text="Delete game save.", callback_data=f"game:delete.user:{int(call.data.split(":")[2])}"),
                types.InlineKeyboardButton(text="Coming soon.", callback_data="WIP_button_callback_data")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"<i>Settings menu.</i>", reply_markup=markup, parse_mode="html")
        case "stop":
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"<i>Good bye, ranger!</i>", parse_mode="html")
        case "continue":
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "delete":
            bot.delete_message(call.message.chat.id, call.message.id)
            data_api.delete_save(user_id=int(call.data.split(":")[2]))
            bot.send_message(call.message.chat.id, f"<i>Good bye, ranger!</i>\n<b>Game save file deleted successfully.</b>", parse_mode="html")


def process_game(*, message: telebot.types.Message, user_id: int):
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(text="Spells", callback_data=f"game:spells_menu.user:{user_id}"),
        types.InlineKeyboardButton(text="Go up", callback_data=f"game:move_up.user:{user_id}"),
        types.InlineKeyboardButton(text="Inventory", callback_data=f"game:inventory_menu.user:{user_id}"),
    )
    markup.row(
        types.InlineKeyboardButton(text="Go left", callback_data=f"game:move_left.user:{user_id}"),
        types.InlineKeyboardButton(text="Go down", callback_data=f"game:move_down.user:{user_id}"),
        types.InlineKeyboardButton(text="Go right", callback_data=f"game:move_right.user:{user_id}"),
    )
    markup.add(
        types.InlineKeyboardButton(text="Settings", callback_data=f"game:settings_menu.user:{user_id}")
    )
    data_api.get_small_maze(uuid=data_api.get_uuid(user_id=user_id))
    with open(f"{data_api.dirs["temp maze files"]}/temp_maze_{data_api.get_uuid(user_id=user_id)}.png", "rb") as file:
        bot.send_photo(message.chat.id, file, reply_markup=markup)
    remove(f"{data_api.dirs["temp maze files"]}/temp_maze_{data_api.get_uuid(user_id=user_id)}.png")


@bot.message_handler(content_types=["text"])
def on_command_error(message: telebot.types.Message):
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, "Unknown command. Use <b>/help</b> for a list of commands.", parse_mode="html")
