from string import ascii_letters
from dotenv import load_dotenv
from hashlib import sha512
from random import randint
from random import sample
from os import getenv
import sqlite3


conn = sqlite3.connect(database="maze_game/data/data.db", check_same_thread=False)
cur = conn.cursor()


def start_api(*, secretkey: str) -> str:
    load_dotenv()
    if secretkey == getenv("secretkey"):
        cur.execute("""
        create table if not exists users (
            telegram_id integer,
            uuid text,
            save_file_name text
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
    string = to_str(sample(ascii_letters, randint(15, 25))) + str(user_id) + __to_str(sample(ascii_letters, randint(15, 25)))
    uuid = sha512(string.encode()).hexdigest()
    return uuid

