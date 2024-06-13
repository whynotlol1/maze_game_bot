from Crypto.Util.number import long_to_bytes
from maze_game.bot import data_api
from dotenv import load_dotenv
from base64 import b64decode
from telebot import TeleBot
from telebot import types
from time import sleep
from os import remove
from os import getenv
import requests

load_dotenv()

bot = TeleBot(token=b64decode(long_to_bytes(int(getenv("bottoken")))).decode())


@bot.callback_query_handler(lambda call: call.data.startswith("action"))
def callback_query_handler(call: types.CallbackQuery):
    match call.data.replace(":", ".").split(".")[1]:
        case "start":
            data_api.create_new_game(user_id=int(call.data.split(":")[2]))
            bot.edit_message_text(f"Welcome to <i>The Maze</i>!", call.message.chat.id, call.message.id, parse_mode="html")
            sleep(1)
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "load":
            bot.edit_message_text(f"Welcome back to <i>The Maze</i>!", call.message.chat.id, call.message.id, parse_mode="html")
            sleep(1)
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "about":
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Get back.", callback_data=f"action:back.user:{int(call.data.split(":")[2])}")
            )
            with open("maze_game/data/message_strings/about.txt", "r") as message_file:
                bot.edit_message_text(message_file.read(), call.message.chat.id, call.message.id, reply_markup=markup, parse_mode="html")
        case "back":
            start_command_handler(call.message)
            bot.delete_message(call.message.chat.id, call.message.id)


@bot.message_handler(commands=["start"])
def start_command_handler(message: types.Message):
    markup = types.InlineKeyboardMarkup()
    if data_api.check_if_user_has_save_file(user_id=message.from_user.id):
        markup.add(
            types.InlineKeyboardButton(text="Load saved game!", callback_data=f"action:load.user:{message.from_user.id}")
        )
    else:
        markup.add(
            types.InlineKeyboardButton(text="Start!", callback_data=f"action:start.user:{message.from_user.id}")
        )
    markup.add(
        types.InlineKeyboardButton(text="About the game.", callback_data=f"action:about.user:{message.from_user.id}")
    )
    with open("maze_game/data/message_strings/start.txt", "r") as message_file:
        message_text = message_file.read() + f"\nGame version: <b>{getenv("version")}</b>"
    bot.send_message(message.chat.id, message_text, parse_mode="html", reply_markup=markup)


@bot.callback_query_handler(lambda call: call.data.startswith("game"))
def callback_query_handler(call: types.CallbackQuery):
    def private_send_inventory():
        message_text = "<i>Inventory menu.</i>\n\n"
        inventory = data_api.get_inventory(user_id=int(call.data.split(":")[2]))
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(text=f"Slot 1", callback_data=f"game:inventory.slot_choose_0.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 2", callback_data=f"game:inventory.slot_choose_1.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 3", callback_data=f"game:inventory.slot_choose_2.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 4", callback_data=f"game:inventory.slot_choose_3.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 5", callback_data=f"game:inventory.slot_choose_4.user:{int(call.data.split(":")[2])}"),
        )
        markup.row(
            types.InlineKeyboardButton(text="Use item", callback_data=f"game:inventory.use_slot.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text="Back to maze", callback_data=f"game:continue.user:{int(call.data.split(":")[2])}")
        )
        for i in range(len(inventory)):
            message_text += f"<i>Slot {i + 1}</i>: <b>{data_api.get_item(item_id=inventory[i][0])[0]}</b>{f" | <i>Ability: {data_api.get_item(item_id=inventory[i][0])[1]}</i>" if data_api.get_item(item_id=inventory[i][0])[1] != "" else ""}{" | <b>(active)</b>" if inventory[i][1] == "active" else ""}\n"
        message_text += "\n<i>Choose active slot with the buttons below.</i>"
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, message_text, reply_markup=markup, parse_mode="html")

    match call.data.replace(":", ".").split(".")[1]:
        case "move_up":
            check = data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="up")
            bot.delete_message(call.message.chat.id, call.message.id)
            match check:
                case "OK":
                    process_game(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FIGHT":
                    msg = bot.send_message(call.message.chat.id, f"You met <i>The Maze Monster</i>! A fight will start in approximately 3 seconds!", parse_mode="html")
                    sleep(3)
                    bot.delete_message(msg.chat.id, msg.id)
                    process_fight(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FINISH":
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
                    )
                    bot.send_message(call.message.chat.id, "Congratulations! You have won <b>The Maze Game</b>!", reply_markup=markup, parse_mode="html")
                    remove(f"{data_api.dirs["save files"]}/save_{int(call.data.split(":")[2])}.json")
        case "move_left":
            check = data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="left")
            bot.delete_message(call.message.chat.id, call.message.id)
            match check:
                case "OK":
                    process_game(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FIGHT":
                    msg = bot.send_message(call.message.chat.id, f"You met <i>The Maze Monster</i>! A fight will start in approximately 3 seconds!", parse_mode="html")
                    sleep(3)
                    bot.delete_message(msg.chat.id, msg.id)
                    process_fight(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FINISH":
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
                    )
                    bot.send_message(call.message.chat.id, "Congratulations! You have won <b>The Maze Game</b>!", reply_markup=markup, parse_mode="html")
                    remove(f"{data_api.dirs["save files"]}/save_{int(call.data.split(":")[2])},json")
        case "move_down":
            check = data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="down")
            bot.delete_message(call.message.chat.id, call.message.id)
            match check:
                case "OK":
                    process_game(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FIGHT":
                    msg = bot.send_message(call.message.chat.id, f"You met <i>The Maze Monster</i>! A fight will start in approximately 3 seconds!", parse_mode="html")
                    sleep(3)
                    bot.delete_message(msg.chat.id, msg.id)
                    process_fight(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FINISH":
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
                    )
                    bot.send_message(call.message.chat.id, "Congratulations! You have won <b>The Maze Game</b>!", reply_markup=markup, parse_mode="html")
                    remove(f"{data_api.dirs["save files"]}/save_{int(call.data.split(":")[2])}.json")
        case "move_right":
            check = data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="right")
            bot.delete_message(call.message.chat.id, call.message.id)
            match check:
                case "OK":
                    process_game(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FIGHT":
                    msg = bot.send_message(call.message.chat.id, f"You met <i>The Maze Monster</i>! A fight will start in approximately 3 seconds!", parse_mode="html")
                    sleep(3)
                    bot.delete_message(msg.chat.id, msg.id)
                    process_fight(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FINISH":
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
                    )
                    bot.send_message(call.message.chat.id, "Congratulations! You have won <b>The Maze Game</b>!", reply_markup=markup, parse_mode="html")
                    remove(f"{data_api.dirs["save files"]}/save_{int(call.data.split(":")[2])}.json")
        case "inventory_menu":
            private_send_inventory()
        case "inventory":
            data = call.data.replace(":", ".").split(".")
            if data[2].startswith("slot_choose"):
                user_id = int(data[4])
                slot = int(data[2][-1])
                data_api.change_inventory_slot(user_id=user_id, slot=slot)
                private_send_inventory()
            elif data[2].startswith("use_slot"):
                user_id = int(data[4])
                if data_api.get_user_slot(user_id=user_id) != 0:
                    msg = bot.send_message(call.message.chat.id, f"Used item: {data_api.get_item(item_id=data_api.get_user_slot(user_id=user_id))[0]}")
                    data_api.use_item(user_id=user_id)
                    sleep(1)
                    bot.delete_message(call.message.chat.id, msg.id)
                    if "sent_from_game_menu" not in data:
                        private_send_inventory()
                    else:
                        bot.delete_message(call.message.chat.id, call.message.id)
                        process_game(message=call.message, user_id=user_id)
                else:
                    msg = bot.send_message(call.message.chat.id, f"No item to use.")
                    sleep(1)
                    bot.delete_message(call.message.chat.id, msg.id)
        case "settings_menu":
            markup = types.InlineKeyboardMarkup()
            markup.row(
                types.InlineKeyboardButton(text="Continue", callback_data=f"game:continue.user:{int(call.data.split(":")[2])}"),
                types.InlineKeyboardButton(text="Save & Quit", callback_data=f"game:stop.user:{int(call.data.split(":")[2])}"),
                types.InlineKeyboardButton(text="Delete game", callback_data=f"game:delete.user:{int(call.data.split(":")[2])}")
            )
            markup.add(
                types.InlineKeyboardButton(text="Console", callback_data=f"game:process_console.user:{int(call.data.split(":")[2])}")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"<i>Settings menu.</i>", reply_markup=markup, parse_mode="html")
        case "stop":
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Load the game!", callback_data=f"action:load.user:{int(call.data.split(":")[2])}")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"<i>Good bye, ranger!</i>", reply_markup=markup, parse_mode="html")
        case "continue":
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "delete":
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            data_api.delete_save(user_id=int(call.data.split(":")[2]))
            bot.send_message(call.message.chat.id, f"<i>Good bye, ranger!</i>\n<b>Game save file deleted successfully.</b>", reply_markup=markup, parse_mode="html")
        case "process_console":
            msg = bot.send_message(call.message.chat.id, f"<i>Entered console mode. Type `quit` to quit.</i>", parse_mode="html")
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.register_next_step_handler(msg, process_console, int(call.data.split(":")[2]), msg)


def process_game(*, message: types.Message, user_id: int):
    data_api.process_ability(user_id=user_id)
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton(text="Use item", callback_data=f"game:inventory.use_slot.user:{user_id}.sent_from_game_menu"),
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
    data_api.get_small_maze(user_id=user_id)
    with open(f"{data_api.dirs["temp files"]}/temp_maze_{user_id}.png", "rb") as file:
        bot.send_photo(message.chat.id, file, reply_markup=markup)
    remove(f"{data_api.dirs["temp files"]}/temp_maze_{user_id}.png")


def process_console(message: types.Message, user_id: int, message_to_delete: types.Message, message_to_delete2: types.Message = None):
    command = message.text.lower()
    commands = {
        "quit": "Quit console mode.",
        "help": "See this message.",
        "changelog": "See the changelog for the latest version.",
        "give": "Requires cheats on."
    }
    secret_commands = ["sv_cheats", "meow"]
    if command != "quit":
        if command.split(" ")[0] not in commands.keys() and command.split(" ")[0] not in secret_commands:
            msg = bot.send_message(message.chat.id, "Unknown console command.")
            if message_to_delete2 is not None:
                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
        else:
            match command:
                case "help":
                    message_text = "Currently available commands:\n"
                    for el in commands.keys():
                        message_text += f"<b>{el}</b> | <i>{commands[el]}</i>\n"
                    msg = bot.send_message(message.chat.id, message_text, parse_mode="html")
                    if message_to_delete2 is not None:
                        bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                    bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                case "changelog":
                    msg = bot.send_message(message.chat.id, f"Changelog for <b>{getenv("version")}</b>:{data_api.get_changelog()}", parse_mode="html")
                    if message_to_delete2 is not None:
                        bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                    bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                case "meow":
                    def private_get_cat() -> bool:
                        req = requests.get('https://api.thecatapi.com/v1/images/search')
                        if req.status_code == 200:
                            data = req.json()
                            url = data[0]["url"]
                            destination_filename = f"{data_api.dirs["temp files"]}random_cat_{user_id}.jpg"
                            req = requests.get(url, stream=True)
                            if req.status_code == 200:
                                with open(destination_filename, "wb") as img_file:
                                    img_file.write(req.content)
                                return True
                            else:
                                return False

                    msg = bot.send_message(message.chat.id, "Attempting to send a cat.")
                    bot.delete_message(msg.chat.id, msg.id)
                    if private_get_cat():
                        with open(f"{data_api.dirs["temp files"]}random_cat_{user_id}.jpg", "rb") as img_file:
                            msg = bot.send_photo(message.chat.id, img_file, caption="Here's your cat!")
                        remove(f"{data_api.dirs["temp files"]}random_cat_{user_id}.jpg")
                    else:
                        msg = bot.send_message(message.chat.id, "Semothing went wrong!")
                    if message_to_delete2 is not None:
                        bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                    bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)

            if command.startswith("sv_cheats"):
                if len(command.split(" ")) > 1:
                    if int(command.split(" ")[1]) not in [0, 1]:
                        msg = bot.send_message(message.chat.id, "Invalid synthax: <b>sv_cheats 0 | 1</b>.", parse_mode="html")
                        bot.register_next_step_handler(msg, process_console, user_id, message_to_delete)
                    else:
                        data_api.sv_cheats(user_id=user_id, value=int(command.split(" ")[1]))
                        msg = bot.send_message(message.chat.id, f"sv_cheats set to {int(command.split(" ")[1])}")
                        if message_to_delete2 is not None:
                            bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                        bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                else:
                    msg = bot.send_message(message.chat.id, "Invalid synthax: <b>sv_cheats 0 | 1</b>.", parse_mode="html")
                    if message_to_delete2 is not None:
                        bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                    bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
            elif command.startswith("give"):
                if len(command.split(" ")) > 1:
                    items = {
                        "potion": 1,
                        "hammer": 2
                    }
                    if command.split(" ")[1] == "all":
                        if data_api.get_sv_cheats(user_id=user_id):
                            for el in items.values():
                                data_api.grant_player(item=el, user_id=user_id)
                            msg = bot.send_message(message.chat.id, "Done.")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                        else:
                            msg = bot.send_message(message.chat.id, "Cheats are not allowed!")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                    elif command.split(" ")[1] in items.keys():
                        if data_api.get_sv_cheats(user_id=user_id):
                            data_api.grant_player(item=items[command.split(" ")[1]], user_id=user_id)
                            msg = bot.send_message(message.chat.id, "Done.")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                        else:
                            msg = bot.send_message(message.chat.id, "Cheats are not allowed!")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                    else:
                        msg = bot.send_message(message.chat.id, "Invalid synthax: <b>give hammer | potion | all</b>", parse_mode="html")
                        if message_to_delete2 is not None:
                            bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                        bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                else:
                    msg = bot.send_message(message.chat.id, "Invalid synthax: <b>give hammer | potion | all</b>", parse_mode="html")
                    if message_to_delete2 is not None:
                        bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                    bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
    else:
        bot.delete_message(message_to_delete.chat.id, message_to_delete.id)
        msg = bot.send_message(message.chat.id, "<i>Quitting console mode.</i>", parse_mode="html")
        sleep(1)
        bot.delete_message(msg.chat.id, msg.id)
        if message_to_delete2 is not None:
            bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
        process_game(message=message, user_id=user_id)


@bot.callback_query_handler(lambda call: call.data.startswith("fight"))
def callback_query_handler(call: types.CallbackQuery):
    bot.delete_message(call.message.chat.id, call.message.id)
    process_fight(user_action=call.data.replace(":", ".").split(".")[1], message=call.message, user_id=int(call.data.replace(":", ".").split(".")[3]))


def process_fight(user_action: str = None, *, message: types.Message, user_id: int):
    markup = None
    if user_action is None:
        data = data_api.handle_fight_processor(user_id=user_id)
    else:
        data = data_api.handle_fight_processor(user_action=user_action, user_id=user_id)
    message_text = ""
    message_text += f"<b>You got {data[0]} HP {f"({"+" if data[2][0] > 0 else "-"}{abs(data[2][0])})" if data[2][0] != 0 else ""}</b>\n"
    message_text += f"<b>The monster got {data[1]} HP {f"({"+" if data[2][1] > 0 else "-"}{abs(data[2][1])})" if data[2][1] != 0 else ""}</b>\n"
    if data[len(data) - 1] == 1:
        message_text += "\n<b>Choose an action.</b>"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(text="Pass", callback_data=f"fight:pass.user:{user_id}"),
            types.InlineKeyboardButton(text="Punch", callback_data=f"fight:punch.user:{user_id}"),
        )
    else:
        message_text += "\n<b>Monster is choosing an action.</b>"
    if markup is not None:
        bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode="html")
    else:
        msg = bot.send_message(message.chat.id, message_text, parse_mode="html")
        sleep(1.5)
        bot.delete_message(msg.chat.id, msg.id)
    if data[0] <= 0:
        remove(f"{data_api.dirs["temp files"]}/fight_save_{user_id}.json")
        remove(f"{data_api.dirs["save files"]}/save_{user_id}.json")
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{user_id}")
        )
        msg = bot.send_message(message.chat.id, "You lost the fight!", reply_markup=markup)
        sleep(0.5)
        bot.delete_message(msg.chat.id, msg.id)
    if data[1] <= 0:
        msg = bot.send_message(message.chat.id, "You won the fight!")
        remove(f"{data_api.dirs["temp files"]}/fight_save_{user_id}.json")
        data_api.grant_player(user_id=user_id)
        sleep(0.5)
        bot.delete_message(msg.chat.id, msg.id)
        process_game(message=message, user_id=user_id)
    if data[0] > 0 and data[1] > 0:
        if data[len(data) - 1] == 2:
            process_fight(message=message, user_id=user_id)


@bot.message_handler(content_types=["text"])
def on_command_error(message: types.Message):
    if message.text.startswith("/"):
        bot.send_message(message.chat.id, f"Unknown command: <b>{message.text}</b>.\nUse <b>/start</b> to start the game.", parse_mode="html")
