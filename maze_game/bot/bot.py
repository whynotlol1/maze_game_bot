"""
This is the main file of the project.
"""

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


"""
About callback query handlers:
All the callback data is formatetd in a specific way.
It is not very important so I won't explain this.
"""


@bot.callback_query_handler(lambda call: call.data.startswith("action"))
def callback_query_handler(call: types.CallbackQuery):
    """
    Callback query handler used for menu buttons.
    """
    match call.data.replace(":", ".").split(".")[1]:
        case "start":  # Starting the game
            data_api.new_save(user_id=int(call.data.split(":")[2]))
            bot.edit_message_text(f"Welcome to <i>The Maze</i>!", call.message.chat.id, call.message.id, parse_mode="html")
            sleep(1)
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "load":  # Loading an already existing game
            bot.edit_message_text(f"Welcome back to <i>The Maze</i>!", call.message.chat.id, call.message.id, parse_mode="html")
            sleep(1)
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "about":  # Showing the about game message
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Get back.", callback_data=f"action:back.user:{int(call.data.split(":")[2])}")
            )
            with open("maze_game/data/message_strings/about.txt", "r") as message_file:
                bot.edit_message_text(message_file.read(), call.message.chat.id, call.message.id, reply_markup=markup, parse_mode="html")
        case "back":  # Getting back to the menu from about game message
            start_command_handler(call.message)
            bot.delete_message(call.message.chat.id, call.message.id)


@bot.callback_query_handler(lambda call: call.data.startswith("game"))
def callback_query_handler(call: types.CallbackQuery):
    """
    Callback query handler used for game buttons.
    """
    def private_send_inventory():
        """
        This function is used to send the inventory list formatted the way it needs to be formatted.
        """
        message_text = "<i>Inventory menu.</i>\n\n"
        inventory = data_api.get_inventory(user_id=int(call.data.split(":")[2]))
        markup = types.InlineKeyboardMarkup()
        markup.row(  # Buttons to choose the active slot
            types.InlineKeyboardButton(text=f"Slot 1", callback_data=f"game:inventory.slot_choose_0.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 2", callback_data=f"game:inventory.slot_choose_1.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 3", callback_data=f"game:inventory.slot_choose_2.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 4", callback_data=f"game:inventory.slot_choose_3.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text=f"Slot 5", callback_data=f"game:inventory.slot_choose_4.user:{int(call.data.split(":")[2])}"),
        )
        markup.row(  # Buttons to use the item or get back to the game
            types.InlineKeyboardButton(text="Use item", callback_data=f"game:inventory.use_slot.user:{int(call.data.split(":")[2])}"),
            types.InlineKeyboardButton(text="Back to maze", callback_data=f"game:continue.user:{int(call.data.split(":")[2])}")
        )
        for i in range(len(inventory)):
            message_text += f"<i>Slot {i + 1}</i>: <b>{data_api.get_item(item_id=inventory[i][0])[0]}</b>{f" | <i>Ability: {data_api.get_item(item_id=inventory[i][0])[1]}</i>" if data_api.get_item(item_id=inventory[i][0])[1] != "" else ""}{" | <b>(active)</b>" if inventory[i][1] == "active" else ""}\n"
        message_text += "\n<i>Choose active slot with the buttons below.</i>"
        bot.delete_message(call.message.chat.id, call.message.id)
        bot.send_message(call.message.chat.id, message_text, reply_markup=markup, parse_mode="html")

    match call.data.replace(":", ".").split(".")[1]:
        # Case 1: movement
        case "move_up":  # up
            # Moving
            check = data_api.player_movement(user_id=int(call.data.split(":")[2]), direction="up")
            bot.delete_message(call.message.chat.id, call.message.id)
            match check:
                case "OK":  # If you're good to go, just moving on
                    process_game(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FIGHT":  # Else start a fight
                    msg = bot.send_message(call.message.chat.id, f"You met <i>The Maze Monster</i>! A fight will start in approximately 3 seconds!", parse_mode="html")
                    sleep(3)
                    bot.delete_message(msg.chat.id, msg.id)
                    process_fight(message=call.message, user_id=int(call.data.split(":")[2]))
                case "FINISH":  # Or finish the game
                    markup = types.InlineKeyboardMarkup()
                    markup.add(
                        types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
                    )
                    bot.send_message(call.message.chat.id, "Congratulations! You have won <b>The Maze Game</b>!", reply_markup=markup, parse_mode="html")
                    remove(f"{data_api.dirs["save files"]}/save_{int(call.data.split(":")[2])}.json")
        case "move_left":  # left
            """ Check comments for `case "move_up"` """
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
        case "move_down":  # down
            """ Check comments for `case "move_up"` """
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
        case "move_right":  # right
            """ Check comments for `case "move_up"` """
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
        # Case 2: inventory
        case "inventory_menu":  # Just sending the inventory
            private_send_inventory()
        case "inventory":  # Or
            data = call.data.replace(":", ".").split(".")
            if data[2].startswith("slot_choose"):  # Choosing an active slot
                user_id = int(data[4])
                slot = int(data[2][-1])
                data_api.change_inventory_slot(user_id=user_id, slot=slot)
                private_send_inventory()  # Updating
            elif data[2].startswith("use_slot"):  # Or using the item
                user_id = int(data[4])
                if data_api.get_user_slot(user_id=user_id) != 0:
                    msg = bot.send_message(call.message.chat.id, f"Used item: {data_api.get_item(item_id=data_api.get_user_slot(user_id=user_id))[0]}")
                    data_api.use_item(user_id=user_id)
                    sleep(1)
                    bot.delete_message(call.message.chat.id, msg.id)
                    if "sent_from_game_menu" not in data:  # If the button is used from inventory
                        private_send_inventory()  # Update inventory
                    else:  # Else process game
                        bot.delete_message(call.message.chat.id, call.message.id)
                        process_game(message=call.message, user_id=user_id)
                else:  # If there is no item to use
                    msg = bot.send_message(call.message.chat.id, f"No item to use.")  # Notifying the user
                    sleep(1)
                    bot.delete_message(call.message.chat.id, msg.id)
        # Case 3: settings
        case "settings_menu":
            markup = types.InlineKeyboardMarkup()
            markup.row(  # Constructing the menu buttons
                types.InlineKeyboardButton(text="Continue", callback_data=f"game:continue.user:{int(call.data.split(":")[2])}"),
                types.InlineKeyboardButton(text="Save & Quit", callback_data=f"game:stop.user:{int(call.data.split(":")[2])}"),
                types.InlineKeyboardButton(text="Delete game", callback_data=f"game:delete.user:{int(call.data.split(":")[2])}")
            )
            markup.add(  # Constructing the menu buttons
                types.InlineKeyboardButton(text="Console", callback_data=f"game:process_console.user:{int(call.data.split(":")[2])}")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            # Sending the menu
            bot.send_message(call.message.chat.id, f"<i>Settings menu.</i>", reply_markup=markup, parse_mode="html")
        case "stop":  # If you choose to save & quit
            # Saving & quitting
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Load the game!", callback_data=f"action:load.user:{int(call.data.split(":")[2])}")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.send_message(call.message.chat.id, f"<i>Good bye, ranger!</i>", reply_markup=markup, parse_mode="html")
        case "continue":  # If you choose to continue
            # Continuing
            bot.delete_message(call.message.chat.id, call.message.id)
            process_game(message=call.message, user_id=int(call.data.split(":")[2]))
        case "delete":  # If you choose to delte the game
            # Deleting the game
            markup = types.InlineKeyboardMarkup()
            markup.add(
                types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{int(call.data.split(":")[2])}")
            )
            bot.delete_message(call.message.chat.id, call.message.id)
            remove(f"{data_api.dirs["save files"]}/save_{int(call.data.split(":")[2])}.json")
            bot.send_message(call.message.chat.id, f"<i>Good bye, ranger!</i>\n<b>Game save file deleted successfully.</b>", reply_markup=markup, parse_mode="html")
        case "process_console":  # If you want to use the console
            # Using the console
            msg = bot.send_message(call.message.chat.id, f"<i>Entered console mode. Type `quit` to quit.</i>", parse_mode="html")
            bot.delete_message(call.message.chat.id, call.message.id)
            bot.register_next_step_handler(msg, process_console, int(call.data.split(":")[2]), msg)


@bot.message_handler(commands=["start"])
def start_command_handler(message: types.Message):
    """
    /start command handler
    """
    markup = types.InlineKeyboardMarkup()
    if data_api.user_has_save(user_id=message.from_user.id):  # Adding load game button if user has a save file
        markup.add(
            types.InlineKeyboardButton(text="Load saved game!", callback_data=f"action:load.user:{message.from_user.id}")
        )
    else:  # Else adding the start button
        markup.add(
            types.InlineKeyboardButton(text="Start!", callback_data=f"action:start.user:{message.from_user.id}")
        )
    markup.add(  # Also adding the about button
        types.InlineKeyboardButton(text="About the game.", callback_data=f"action:about.user:{message.from_user.id}")
    )
    with open("maze_game/data/message_strings/start.txt", "r") as message_file:
        message_text = message_file.read() + f"\nGame version: <b>{getenv("version")}</b>"
    bot.send_message(message.chat.id, message_text, parse_mode="html", reply_markup=markup)


def process_game(*, message: types.Message, user_id: int):
    """
    Main game processor.
    """
    data_api.process_ability(user_id=user_id)
    markup = types.InlineKeyboardMarkup()
    markup.row(  # Constructing the reply markup
        types.InlineKeyboardButton(text="Use item", callback_data=f"game:inventory.use_slot.user:{user_id}.sent_from_game_menu"),
        types.InlineKeyboardButton(text="Go up", callback_data=f"game:move_up.user:{user_id}"),
        types.InlineKeyboardButton(text="Inventory", callback_data=f"game:inventory_menu.user:{user_id}"),
    )
    markup.row(  # Constructing the reply markup
        types.InlineKeyboardButton(text="Go left", callback_data=f"game:move_left.user:{user_id}"),
        types.InlineKeyboardButton(text="Go down", callback_data=f"game:move_down.user:{user_id}"),
        types.InlineKeyboardButton(text="Go right", callback_data=f"game:move_right.user:{user_id}"),
    )
    markup.add(  # Constructing the reply markup
        types.InlineKeyboardButton(text="Settings", callback_data=f"game:settings_menu.user:{user_id}")
    )
    data_api.get_small_maze(user_id=user_id)  # Creating
    with open(f"{data_api.dirs["temp files"]}/temp_maze_{user_id}.png", "rb") as file:
        bot.send_photo(message.chat.id, file, reply_markup=markup)  # And sending a maze picture with reply markup
    remove(f"{data_api.dirs["temp files"]}/temp_maze_{user_id}.png")


def process_console(message: types.Message, user_id: int, message_to_delete: types.Message, message_to_delete2: types.Message = None):
    """
    Console processor.
    """
    command = message.text.lower()
    commands = {  # Format: <command>: <description>
        "quit": "Quit console mode.",
        "help": "See this message.",
        "give": "Requires cheats on."
    }
    secret_commands = ["sv_cheats", "meow"]  # commands that should not be in the help list
    if command != "quit":
        if command.split(" ")[0] not in commands.keys() and command.split(" ")[0] not in secret_commands:  # If the command is invalid
            msg = bot.send_message(message.chat.id, "Unknown console command.")
            if message_to_delete2 is not None:
                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
        else:  # Else
            match command:
                case "help":  # help message
                    message_text = "Currently available commands:\n"
                    for el in commands.keys():
                        message_text += f"<b>{el}</b> | <i>{commands[el]}</i>\n"
                    msg = bot.send_message(message.chat.id, message_text, parse_mode="html")
                    if message_to_delete2 is not None:
                        bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                    bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                case "meow":  # Secret command: cat picture
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

            if command.startswith("sv_cheats"):  # sv_cheats <value>
                if len(command.split(" ")) > 1:  # Check if argument is provided
                    if int(command.split(" ")[1]) not in [0, 1]:  # Check for valid synthax
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
            elif command.startswith("give"):  # give <item>
                if len(command.split(" ")) > 1:  # Check if argument is provided
                    items = {
                        "potion": 1,
                        "hammer": 2
                    }
                    if command.split(" ")[1] == "all":  # Check if you want to get every item
                        if data_api.get_sv_cheats(user_id=user_id):
                            for el in items.values():
                                data_api.grant_player(item=el, user_id=user_id)
                            msg = bot.send_message(message.chat.id, "Done.")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                        else:  # Only do this if sv_cheats is set to 1
                            msg = bot.send_message(message.chat.id, "Cheats are not allowed!")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                    elif command.split(" ")[1] in items.keys():  # Check for valid synthax
                        if data_api.get_sv_cheats(user_id=user_id):
                            data_api.grant_player(item=items[command.split(" ")[1]], user_id=user_id)
                            msg = bot.send_message(message.chat.id, "Done.")
                            if message_to_delete2 is not None:
                                bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
                            bot.register_next_step_handler(msg, process_console, user_id, message_to_delete, msg)
                        else:  # Only do this if sv_cheats is set to 1
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
    else:  # quit command
        bot.delete_message(message_to_delete.chat.id, message_to_delete.id)
        msg = bot.send_message(message.chat.id, "<i>Quitting console mode.</i>", parse_mode="html")
        sleep(1)
        bot.delete_message(msg.chat.id, msg.id)
        if message_to_delete2 is not None:
            bot.delete_message(message_to_delete2.chat.id, message_to_delete2.id)
        process_game(message=message, user_id=user_id)


@bot.callback_query_handler(lambda call: call.data.startswith("fight"))
def callback_query_handler(call: types.CallbackQuery):
    """
    Callback query handler used for fight processor.
    """
    bot.delete_message(call.message.chat.id, call.message.id)
    process_fight(user_action=call.data.replace(":", ".").split(".")[1], message=call.message, user_id=int(call.data.replace(":", ".").split(".")[3]))


def process_fight(user_action: str = None, *, message: types.Message, user_id: int):
    """
    Frontend of a fight processor.
    """
    markup = None
    if user_action is None:  # 0th monster turns
        data = data_api.handle_fight_processor(user_id=user_id)
    else:
        data = data_api.handle_fight_processor(user_action=user_action, user_id=user_id)
    message_text = ""
    message_text += f"<b>You got {data[0]} HP {f"({"+" if data[2][0] > 0 else "-"}{abs(data[2][0])})" if data[2][0] != 0 else ""}</b>\n"
    message_text += f"<b>The monster got {data[1]} HP {f"({"+" if data[2][1] > 0 else "-"}{abs(data[2][1])})" if data[2][1] != 0 else ""}</b>\n"
    if data[len(data) - 1] == 1:  # Action choice menu for player
        message_text += "\n<b>Choose an action.</b>"
        markup = types.InlineKeyboardMarkup()
        markup.row(
            types.InlineKeyboardButton(text="Pass", callback_data=f"fight:pass.user:{user_id}"),
            types.InlineKeyboardButton(text="Punch", callback_data=f"fight:punch.user:{user_id}"),
        )
    else:
        message_text += "\n<b>Monster is choosing an action.</b>"  # Or a beautiful message
    # Sending the info
    if markup is not None:
        msg_ = bot.send_message(message.chat.id, message_text, reply_markup=markup, parse_mode="html")
    else:
        msg_ = bot.send_message(message.chat.id, message_text, parse_mode="html")
        sleep(1.5)
        bot.delete_message(msg_.chat.id, msg_.id)
    if data[0] <= 0:  # If user loses the fight
        if msg_ is not None:
            bot.delete_message(msg_.chat.id, msg_.id)
        remove(f"{data_api.dirs["temp files"]}/fight_save_{user_id}.json")
        remove(f"{data_api.dirs["save files"]}/save_{user_id}.json")  # Delete the game
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(text="Start new game!", callback_data=f"action:start.user:{user_id}")
        )
        bot.send_message(message.chat.id, "You lost the fight!", reply_markup=markup)
        sleep(0.5)
    if data[1] <= 0:  # If user wins the fight
        msg = bot.send_message(message.chat.id, "You won the fight!")
        remove(f"{data_api.dirs["temp files"]}/fight_save_{user_id}.json")
        data_api.grant_player(user_id=user_id)  # Grant user a random item
        sleep(0.5)
        bot.delete_message(msg.chat.id, msg.id)
        process_game(message=message, user_id=user_id)
    if data[0] > 0 and data[1] > 0:
        if data[len(data) - 1] == 2:
            process_fight(message=message, user_id=user_id)  # Autoprocessing monster turns


@bot.message_handler(content_types=["text"])
def on_command_error(message: types.Message):
    """
    Basically an on_command_error method.
    """
    if message.text.startswith("/"):
        # Only trigger if a message looks like a command and no other message handlers are triggered.
        bot.send_message(message.chat.id, f"Unknown command: <b>{message.text}</b>.\nUse <b>/start</b> to start the game.", parse_mode="html")
