from maze_game.bot import maze_generator
from string import ascii_letters
from dotenv import load_dotenv
from hashlib import sha512
from random import randint
from random import sample
from os import listdir
from os import getenv
from os import mkdir
from os import path
import sqlite3
import json


conn = sqlite3.connect(database="maze_game/data/data.db", check_same_thread=False)
cur = conn.cursor()
dirs = {
    "save files": "maze_game/data/saves",
    "maze files": "maze_game/data/saves/mazes",
    "temp maze files": "maze_game/data/temp_maze_files"
}


def start_api(*, secretkey: str) -> str:
    global dirs
    for dir_name in dirs.values():
        if not path.isdir(dir_name):
            mkdir(dir_name)
    load_dotenv()
    if secretkey == getenv("secretkey"):
        cur.execute("""
        create table if not exists users (
            telegram_id integer,
            uuid text
        )
        """)
        conn.commit()
        return "Started."
    else:
        return "Access denied."


def to_str(to_convert: list) -> str:
    converted = ""
    for el in to_convert:
        converted += el
    return converted


def gen_uuid(user_id: int) -> str:
    string = f"{to_str(sample(ascii_letters, randint(5, 15)))}_{str(user_id)}_{to_str(sample(ascii_letters, randint(5, 15)))}"
    uuid = sha512(string.encode()).hexdigest()
    return uuid


def check_if_user_has_save_file(*, user_id: int) -> bool:
    check = cur.execute("select uuid from users where telegram_id=?", (user_id,)).fetchone()
    return check is not None


def create_new_game(*, user_id: int) -> str:
    global dirs
    uuid = gen_uuid(user_id=user_id)
    player_position, maze_grid = maze_generator.generate(width=300, height=300, iterations=2, uuid=uuid)
    save_json = {
        "player": {
            "global maze position": player_position,
            "level": 0,
            "health": 20,
            "mana": 50,
            "inventory": [0, 0, 0, 0, 0],
            "spells can be used": []
        },
        "maze grid": maze_grid
    }
    with open(f"{dirs["save files"]}/save_{uuid}.json", "w") as save_file:
        save_file.write(json.dumps(save_json))
    cur.execute("insert into users values (?, ?)", (user_id, uuid))
    conn.commit()
    return uuid


def get_maze(*, user_id: int) -> str:
    global dirs
    uuid = cur.execute("select uuid from users where telegram_id=?", (user_id,)).fetchone()[0]
    files = listdir(dirs["maze files"])
    for file in files:
        if file.find(uuid) != -1:
            return file


def get_uuid(*, user_id: int) -> str:
    return cur.execute("select uuid from users where telegram_id=?", (user_id,)).fetchone()[0]


def find_surrounding(matrix, target_value=2):
    for i, row in enumerate(matrix):
        try:
            index = row.index(target_value)
            break
        except ValueError:
            continue

    surrounding = []
    start_row = max(0, i - 2)
    end_row = min(i + 3, len(matrix))
    start_col = max(0, index - 2)
    end_col = min(index + 3, len(matrix[0]))

    for row in matrix[start_row:end_row]:
        surrounding.append(row[start_col:end_col])

    return surrounding


def get_small_maze(uuid: str):
    global dirs
    with open(f"{dirs["save files"]}/save_{uuid}.json", "r") as save_file:
        save_data = json.loads(save_file.read())
    matrix = save_data["maze grid"]
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

    maze_generator.draw_small(grid=surrounding, n=len(surrounding), m=len(surrounding[0]), uuid=uuid)
