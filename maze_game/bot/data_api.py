from maze_game.bot import fight_processor
from maze_game.bot import maze_generator
from dotenv import load_dotenv
from random import choice
from os import listdir
from os import remove
from os import mkdir
from os import path
import json


dirs = {
    "save files": "maze_game/data/saves",
    "temp files": "maze_game/data/temp_files",
    "system files": "maze_game/data/system",
    "items": "maze_game/data/system/items.json"
}
item_abilities = {
    1: ["invisibility", 6],
    2: ["break walls", 2]
}

load_dotenv()


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
    return f"save_{user_id}.json" in listdir(dirs["save files"])


def create_new_game(*, user_id: int):
    global dirs
    player_position, maze_grid = maze_generator.generate(width=100, height=100, iterations=2)
    save_json = {
        "player": {
            "global maze position": player_position,
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
                    grid[coords[0]][coords[1]-1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-1]
                    return_value = "FIGHT"
                elif grid[coords[0]][coords[1]-1] == 2:
                    grid[coords[0]][coords[1]-1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]-1]
                    return_value = "FINISH"
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
                    grid[coords[0]][coords[1]+1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+1]
                    return_value = "FIGHT"
                elif grid[coords[0]][coords[1]+1] == 2:
                    grid[coords[0]][coords[1]+1], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0], coords[1]+1]
                    return_value = "FINISH"
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
                    grid[coords[0]+1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+1, coords[1]]
                    return_value = "FIGHT"
                elif grid[coords[0]+1][coords[1]] == 2:
                    grid[coords[0]+1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]+1, coords[1]]
                    return_value = "FINISH"
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
                    grid[coords[0]-1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-1, coords[1]]
                    return_value = "FIGHT"
                elif grid[coords[0]-1][coords[1]] == 2:
                    grid[coords[0]-1][coords[1]], grid[coords[0]][coords[1]] = grid[coords[0]][coords[1]], 0
                    coords = [coords[0]-1, coords[1]]
                    return_value = "FINISH"
        save_data["maze grid"] = grid
        save_data["player"]["global maze position"] = coords
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))
    try:
        return return_value
    except UnboundLocalError:
        return "OK"


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
        return save_data["player"]["inventory"]["list"][get_active_slot(user_id=user_id)]


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


def handle_fight_processor(user_action: str = "None", *, user_id: int) -> list:
    global dirs
    if path.isfile(f"{dirs["temp files"]}/fight_save_{user_id}.json"):
        with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "r") as file:
            data = json.loads(file.read())
        match data["turn"]:
            case 1:
                data_returned = fight_processor.fight_processor(action=user_action, user_hp=data["user_hp"], monster_hp=data["monster_hp"], turn=1)
                data["user_hp"] = data_returned[0]
                data["monster_hp"] = data_returned[1]
                data["turn"] = 2
                with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "w") as file:
                    file.write(json.dumps(data))
                data_returned.append(data["turn"])
                if data_returned[0] <= 0:
                    data_returned[0] = 0
                if data_returned[1] <= 0:
                    data_returned[1] = 0
                return data_returned
            case 2:
                data_returned = fight_processor.fight_processor(user_hp=data["user_hp"], monster_hp=data["monster_hp"], turn=2)
                data["user_hp"] = data_returned[0]
                data["monster_hp"] = data_returned[1]
                data["turn"] = 1
                with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "w") as file:
                    file.write(json.dumps(data))
                data_returned.append(data["turn"])
                if data_returned[0] <= 0:
                    data_returned[0] = 0
                if data_returned[1] <= 0:
                    data_returned[1] = 0
                return data_returned
    else:
        with open(f"{dirs["temp files"]}/fight_save_{user_id}.json", "w") as file:
            data = {
                "user_hp": 20,
                "monster_hp": 20,
                "turn": 1
            }
            file.write(json.dumps(data))
        return [20, 20, [0, 0], 1]


def grant_player(item: int = -1, *, user_id: int):
    global item_abilities
    if item == -1:
        item = choice(list(item_abilities.keys()))
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
    for i in range(len(save_data["player"]["inventory"]["list"])):
        if save_data["player"]["inventory"]["list"][i] == 0:
            save_data["player"]["inventory"]["list"][i] = item
            break
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def sv_cheats(*, user_id: int, value: int):
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
    save_data["sv cheats"] = value
    with open(f"{dirs["save files"]}/save_{user_id}.json", "w") as save_file:
        save_file.write(json.dumps(save_data))


def get_sv_cheats(*, user_id: int):
    with open(f"{dirs["save files"]}/save_{user_id}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
        return save_data["sv cheats"]
