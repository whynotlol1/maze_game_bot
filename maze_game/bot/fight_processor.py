# (c) cat dev 2024

import random


def fight_processor(action: str = None, *, user_hp: int, monster_hp: int, turn: int) -> list:
    """
    User-Monster fight processor for The Maze Game Telegram bot.

    :param str action: User action if turn == 1
    :param int user_hp: User HP got from the save file.
    :param int monster_hp: Monster HP. Default value is 40.
    :param int turn: [1/2] 1 - User's turn, 2 - Monster's turn
    :return: list [new_user_hp, new_monster_hp, deltas[], <monster_action> if turn  == 2 else <>]
    :rtype: list
    """

    def private_gen_monster_action():
        __a = random.random()
        __b = random.random()
        __c = random.random()
        if 0.1 <= __a <= 0.4:
            if 0.5 <= __b <= 0.9:
                if 0.1 <= __c <= 0.4:
                    monster_action = "punch"
                else:
                    monster_action = "punch"
            else:
                monster_action = "pass"
        else:
            if 0.5 <= __b <= 0.9:
                if 0.1 <= __c <= 0.4:
                    monster_action = "punch"
                else:
                    monster_action = "pass"
            else:
                monster_action = "punch"

        return monster_action  # ~70% punch, ~30% pass

    deltas = [0, 0]
    match turn:
        case 1:
            match action:
                case "punch":
                    deltas = [0, -random.randint(1, 5)]
                case "pass":
                    deltas = [random.randint(1, 3), 0]
        case 2:
            monster_action = private_gen_monster_action()
            match monster_action:
                case "punch":
                    deltas = [-random.randint(1, 5), 0]
                case "pass":
                    deltas = [0, random.randint(1, 3)]

    if user_hp + deltas[0] <= 20:
        new_user_hp = user_hp + deltas[0]
    else:
        new_user_hp = 20
    if monster_hp + deltas[1] <= 20:
        new_monster_hp = monster_hp + deltas[1]
    else:
        new_monster_hp = 20

    returned_vals = [new_user_hp, new_monster_hp, deltas]

    return returned_vals  # [new_user_hp, new_monster_hp, deltas[]]
