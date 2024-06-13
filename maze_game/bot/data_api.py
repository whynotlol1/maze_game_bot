"""
This file is what it says in the name - data API. 100% JSON-based
"""

from maze_game.bot import fight_processor
from maze_game.bot import maze_generator
from dotenv import load_dotenv
from random import choice
from os import listdir
from os import mkdir
from os import path
import json


# Global variables
dirs = {
    "save files": "maze_game/data/saves",
    "temp files": "maze_game/data/temp_files",
    "system files": "maze_game/data/system",
    "items": "maze_game/data/system/items.json"
}
item_abilities = {  # Format: <id>: [<ability short name>, <ability duration + 1>]
    1: ["invisibility", 6],
    2: ["break walls", 2]
}

load_dotenv()


def start_api():
    """
    Used to config data when bot is started for the very first time.
    """
    global dirs
    for dir_name in list(dirs.values())[:-1]:  # Making sure if every directory in the list exists
        if not path.isdir(dir_name):
            mkdir(dir_name)
    if not path.isfile(dirs["items"]):  # Creating items list
        with open(dirs["items"], "w") as file:
            items = {  # Fromat: <id>: [<name>, <ability>]
                0: ["Empty", ""],
                1: ["Potion of Invisibility", "Makes you invisible to monsters for 5 moves."],
                2: ["The Maze Hammer", "Lets you break a wall block."]
            }
            file.write(json.dumps(items))


def user_has_save(*, user_id: int) -> bool:
    """
    Checks whether user has a save file.
    
    :param user_id: User Telegram ID.
    :return: Whether user has a save file.
    :rtype: bool
    """
    global dirs
    return f"save_{user_id}.json" in listdir(dirs["save files"])


def new_save(*, user_id: int):
    """
    Creates a new save file.
    
    :param user_id: User Telegram ID.
    """
    global dirs
    player_position, maze_grid = maze_generator.generate(width=100, height=100, iterations=2)
    save_json = {  # Save file format
        "player": {
            "position": player_position,
            "inventory": {
                "list": [0, 0, 0, 0, 0],
                "active slot": 0
            },
            "ability": {
                "active": "",
                "timer": 0
            }
        },
        "sv cheats": 0,
        "maze grid": maze_grid
    }
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_json))


def get_small_maze(*, user_id: int):
    """
    Used with a function in maze_generator.py to draw the small portion of the maze around the player.
    
    :param user_id: User Telegram ID.
    """
    global dirs
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
    # Code below written by Phind AI model
    matrix = save_data["maze grid"]
    i, index = 0, 0
    for i, row in enumerate(matrix):
        try:
            index = row.index(3)
            break
        except ValueError:
            continue

    surrounding = []
    start_row = max(0, i - 10)
    end_row = min(i + 10, len(matrix))
    start_col = max(0, index - 10)
    end_col = min(index + 10, len(matrix[0]))

    for row in matrix[start_row:end_row]:
        surrounding.append(row[start_col:end_col])

    maze_generator.draw_small(grid=surrounding, n=len(surrounding), m=len(surrounding[0]), user_id=user_id)


def player_movement(*, user_id: int, direction: str) -> str:
    """
    Player movement processor.

    :param user_id: User Telegram ID.
    :param direction: Direction of movment.
    :return: Special code.
    :rtype: str
    """
    global dirs
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        grid = save_data["maze grid"]
        coords = save_data["player"]["position"]
        match direction:
            case "up":
                # Case 1: player just moves to the next tile
                if grid[coords[0]][coords[1]-1] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]][coords[1]-1] in [0, 1]):
                    grid[coords[0]][coords[1]-1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-1]
                    return_value = "OK"
                # Case 2: player "jumps over" a monster tile
                elif grid[coords[0]][coords[1]-1] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]][coords[1]-2], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-2]
                    return_value = "OK"
                # Case 3: player meets a monster and a fight starts
                elif grid[coords[0]][coords[1]-1] == 4 and get_ability(user_id=user_id) != "invisibility":
                    grid[coords[0]][coords[1]-1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-1]
                    return_value = "FIGHT"
                # Case 4: player finishes
                elif grid[coords[0]][coords[1]-1] == 2:
                    grid[coords[0]][coords[1]-1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-1]
                    return_value = "FINISH"
            case "down":
                """ Check comments for `case "up"` """
                if grid[coords[0]][coords[1]+1] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]][coords[1]+1] in [0, 1]):
                    grid[coords[0]][coords[1]+1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+1]
                    return_value = "OK"
                elif grid[coords[0]][coords[1]+1] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]][coords[1]+2], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+2]
                    return_value = "OK"
                elif grid[coords[0]][coords[1]+1] == 4 and get_ability(user_id=user_id) != "invisibility":
                    grid[coords[0]][coords[1]+1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+1]
                    return_value = "FIGHT"
                elif grid[coords[0]][coords[1]+1] == 2:
                    grid[coords[0]][coords[1]+1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+1]
                    return_value = "FINISH"
            case "right":
                """ Check comments for `case "up"` """
                if grid[coords[0]+1][coords[1]] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]+1][coords[1]] in [0, 1]):
                    grid[coords[0]+1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+1, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]+1][coords[1]] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]+2][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+2, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]+1][coords[1]] == 4 and get_ability(user_id=user_id) != "invisibility":
                    grid[coords[0]+1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+1, coords[1]]
                    return_value = "FIGHT"
                elif grid[coords[0]+1][coords[1]] == 2:
                    grid[coords[0]+1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+1, coords[1]]
                    return_value = "FINISH"
            case "left":
                """ Check comments for `case "up"` """
                if grid[coords[0]-1][coords[1]] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]-1][coords[1]] in [0, 1]):
                    grid[coords[0]-1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-1, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]-1][coords[1]] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]-2][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-2, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]-1][coords[1]] == 4 and get_ability(user_id=user_id) != "invisibility":
                    grid[coords[0]-1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-1, coords[1]]
                    return_value = "FIGHT"
                elif grid[coords[0]-1][coords[1]] == 2:
                    grid[coords[0]-1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-1, coords[1]]
                    return_value = "FINISH"
        # Applying changes
        save_data["maze grid"] = grid
        save_data["player"]["position"] = coords
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))
    try:
        return return_value  # Returning the special code
    except UnboundLocalError:  # Returning "OK" code if the code is undefined (should never happen)
        return "OK"


def get_inventory(*, user_id: int) -> list[list]:
    """
    Used to get the list of all user inventory slots.

    :param user_id: User Telegram ID.
    :return: Inventory list formatted [<item id>, <"active" | "not active">].
    :rtype: list
    """
    returned_list = []
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        for i in range(len(save_data["player"]["inventory"]["list"])):
            if i == save_data["player"]["inventory"]["active slot"]:
                returned_list.append([save_data["player"]["inventory"]["list"][i], "active"])
            else:
                returned_list.append([save_data["player"]["inventory"]["list"][i], "not active"])
    return returned_list


def change_inventory_slot(*, user_id: int, slot: int):
    """
    Changes the active inventory slot.

    :param user_id: User Telegram ID.
    :param slot: Slot index.
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        save_data["player"]["inventory"]["active slot"] = slot
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def get_active_slot(*, user_id: int) -> int:
    """
    Gets the user's current active slot.

    :param user_id: User Telegram ID.
    :return: Active slot index.
    :rtype: int
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["player"]["inventory"]["active slot"]


def get_user_slot(*, user_id: int) -> int:
    """
    Gets the ID of an item in user's active slot.

    :param user_id: User Telegram ID.
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["player"]["inventory"]["list"][get_active_slot(user_id=user_id)]


def get_item(*, item_id: int) -> str:
    """
    Returns the item by its ID.

    :param item_id: Item ID.
    :return: Item name.
    :rtype: str
    """
    with open(dirs["items"], "r") as file:
        data = json.loads(file.read())
        return data[str(item_id)]


def use_item(*, user_id: int):
    """
    Item use processor.

    :param user_id: User Telegram ID.
    """
    global item_abilities
    slot = get_user_slot(user_id=user_id)
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        save_data["player"]["inventory"]["list"][get_active_slot(user_id=user_id)] = 0
        save_data["player"]["ability"] = {
            "active": item_abilities[int(slot)][0],
            "timer": item_abilities[int(slot)][1],
        }
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def process_ability(*, user_id: int):
    """
    Ability processor.

    :param user_id: User Telegram ID.
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        if save_data["player"]["ability"]["timer"] != 0:  # If timer is not 0
            save_data["player"]["ability"]["timer"] -= 1  # Decrease by 1
        if save_data["player"]["ability"]["timer"] == 0:  # Else
            save_data["player"]["ability"] = {  # Set ability to "" (no ability)
                "active": "",
                "timer": 0,
            }
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def get_ability(*, user_id: int) -> str:
    """
    Gets the user's active ability.

    :param user_id: User Telegram ID
    :return: Ability short name.
    :rtype: str
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["player"]["ability"]["active"]


def sv_cheats(*, user_id: int, value: int):
    """
    Sets sv_cheats value for user.

    :param user_id: User Telegram ID.
    :param value: sv_cheats value.
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
    save_data["sv cheats"] = value
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def get_sv_cheats(*, user_id: int) -> int:
    """
    gets sv_cheats value for user.

    :param user_id: User Telegram ID.
    :return: sv_cheats value.
    :rtype: int
    """
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["sv cheats"]


def handle_fight_processor(user_action: str = "None", *, user_id: int) -> list:
    """
    Player-Monster fight processor 2.

    :param user_action: User action if specified.
    :param user_id: User Telegram ID.
    :return: Same list fight_processor returns.
    :rtype: list
    """
    global dirs
    if path.isfile(f"{dirs["temp files"]}/fight_save_{user_id}.json"):  # If fight is already started
        with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "r") as file:
            data = json.loads(file.read())
        match data["turn"]:
            case 1:  # User's turn
                data_returned = fight_processor.fight_processor(action=user_action, user_hp=data["user_hp"], monster_hp=data["monster_hp"], turn=1)
                data["user_hp"] = data_returned[0]
                data["monster_hp"] = data_returned[1]
                data["turn"] = 2
                with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "w") as file:
                    file.write(json.dumps(data))
                data_returned.append(data["turn"])
                # Check if HP is below 0
                if data_returned[0] <= 0:
                    data_returned[0] = 0
                if data_returned[1] <= 0:
                    data_returned[1] = 0
                return data_returned  # Return the list
            case 2:  # Monster's turn
                data_returned = fight_processor.fight_processor(user_hp=data["user_hp"], monster_hp=data["monster_hp"], turn=2)
                data["user_hp"] = data_returned[0]
                data["monster_hp"] = data_returned[1]
                data["turn"] = 1
                with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "w") as file:
                    file.write(json.dumps(data))
                data_returned.append(data["turn"])
                # Check if HP is below 0
                if data_returned[0] <= 0:
                    data_returned[0] = 0
                if data_returned[1] <= 0:
                    data_returned[1] = 0
                return data_returned  # Return the list
    else:  # Else
        with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "w") as file:  # Create a fight
            data = {
                "user_hp": 20,
                "monster_hp": 20,
                "turn": 1
            }
            file.write(json.dumps(data))
        return [20, 20, [0, 0], 1]  # Return the 0th turn list


def grant_player(item: int = -1, *, user_id: int):
    """
    Grants player a random item if it's not specified or a specified item.

    :param item: Item ID.
    :param user_id: User Telegram ID.
    """
    global item_abilities
    if item == -1:  # If item is not specified
        item = choice(list(item_abilities.keys()))  # Choose a random one
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
    for i in range(len(save_data["player"]["inventory"]["list"])):  # Add it to the first free inventory slot
        if save_data["player"]["inventory"]["list"][i] == 0:
            save_data["player"]["inventory"]["list"][i] = item
            break  # Do this only 1 time
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))
