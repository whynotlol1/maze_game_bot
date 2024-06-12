from maze_game.bot import maze_generator
from os import listdir
from os import remove
from os import mkdir
from os import path
import json


dirs = {
    "save files": "maze_game/data/saves",
    "temp maze files": "maze_game/data/temp_maze_files",
    "system files": "maze_game/data/system",
    "items": "maze_game/data/system/items.json"
}
item_abilities = {
    1: ["invisibility", 6],
    2: ["break walls", 2]
}


def start_api():
    global dirs
    for dir_name in list(dirs.values())[:-1]:
        if not path.isdir(dir_name):
            mkdir(dir_name)
    if not path.isfile(dirs["items"]):
        with open(dirs["items"], "w") as file:
            items = {
                0: ["Empty", ""],
                1: ["Potion of Invisibility", "Makes you invisible to monsters for 5 moves."],
                2: ["The Maze Hammer", "Lets you break a wall block."]
            }
            file.write(json.dumps(items))


def check_if_user_has_save_file(*, user_id: int) -> bool:
    global dirs
    return user_id in listdir(dirs["save files"])


def create_new_game(*, user_id: int):
    global dirs
    player_position, maze_grid = maze_generator.generate(width=100, height=100, iterations=2)
    save_json = {
        "player": {
            "global maze position": player_position,
            "level": 0,
            "health": 20,
            "inventory": {
                "list": [0, 0, 0, 0, 0],
                "active slot": 0
            },
            "ability": {
                "active": "",
                "timer": 0
            }
        },
        "maze grid": maze_grid
    }
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_json))


def get_small_maze(*, user_id: int):
    global dirs
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
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
    global dirs
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        grid = save_data["maze grid"]
        coords = save_data["player"]["global maze position"]
        match direction:
            case "up":
                if grid[coords[0]][coords[1]-1] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]][coords[1]-1] in [0, 1]):
                    grid[coords[0]][coords[1]-1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-1]
                    return_value = "OK"
                elif grid[coords[0]][coords[1]-1] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]][coords[1]-2], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-2]
                    return_value = "OK"
                elif grid[coords[0]][coords[1]-1] == 4 and get_ability(user_id=user_id) != "invisibility":
                    coords = [coords[0], coords[1]-1]
                    return_value = "FIGHT"
            case "down":
                if grid[coords[0]][coords[1]+1] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]][coords[1]+1] in [0, 1]):
                    grid[coords[0]][coords[1]+1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+1]
                    return_value = "OK"
                elif grid[coords[0]][coords[1]+1] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]][coords[1]+2], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+2]
                    return_value = "OK"
                elif grid[coords[0]][coords[1]+1] == 4 and get_ability(user_id=user_id) != "invisibility":
                    coords = [coords[0], coords[1]+1]
                    return_value = "FIGHT"
            case "right":
                if grid[coords[0]+1][coords[1]] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]+1][coords[1]] in [0, 1]):
                    grid[coords[0]+1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+1, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]+1][coords[1]] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]+2][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+2, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]+1][coords[1]] == 4 and get_ability(user_id=user_id) != "invisibility":
                    coords = [coords[0]+1, coords[1]]
                    return_value = "FIGHT"
            case "left":
                if grid[coords[0]-1][coords[1]] == 0 or (get_ability(user_id=user_id) == "break walls" and grid[coords[0]-1][coords[1]] in [0, 1]):
                    grid[coords[0]-1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-1, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]-1][coords[1]] == 4 and get_ability(user_id=user_id) == "invisibility":
                    grid[coords[0]-2][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-2, coords[1]]
                    return_value = "OK"
                elif grid[coords[0]-1][coords[1]] == 4 and get_ability(user_id=user_id) != "invisibility":
                    coords = [coords[0]-1, coords[1]]
                    return_value = "FIGHT"
        save_data["maze grid"] = grid
        save_data["player"]["global maze position"] = coords
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))
    return return_value


def delete_save(*, user_id: int):
    global dirs
    remove(f"{dirs["save files"]}/save_{user_id}.json")


def get_inventory(*, user_id: int) -> list[list]:
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
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        save_data["player"]["inventory"]["active slot"] = slot
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def get_item(*, item_id: int) -> str:
    with open(dirs["items"], "r") as file:
        data = json.loads(file.read())
    return data[str(item_id)]


def get_active_slot(*, user_id: int):
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["player"]["inventory"]["active slot"]


def get_user_slot(*, user_id: int) -> int:
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["player"]["inventory"]["list"][save_data["player"]["inventory"]["active slot"]]


def use_item(*, user_id: int):
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
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        if save_data["player"]["ability"]["timer"] != 0:
            save_data["player"]["ability"]["timer"] -= 1
        if save_data["player"]["ability"]["timer"] == 0:
            save_data["player"]["ability"] = {
                "active": "",
                "timer": 0,
            }
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def get_ability(*, user_id: int):
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["player"]["ability"]["active"]
