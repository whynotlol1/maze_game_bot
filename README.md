# --<>--<>--<>--maze_game_bot--<>--<>--<>--
# The Maze Game Telegram bot
This is the official repository of The Maze Game Telegram bot.
## Table of contents

1. [Requirements](#requirements)
2. [Setup](#setup)
3. [Credits](#credits)

## Requirements

1. Python 3.10+
2. Python packages: `PyCryptoDome, TeleBot, Pillow, requests, python-dotenv`
3. Own telegram bot (can be created using [BotFather](https://t.me/BotFather))

## Setup

1. Clone the repository
2. Use `PyCryptoDome and base64` Python packages to encrypt your Telegram bot token: `bytes_to_long(b64encode(%token%.encode()))` and paste the encrypted token to `maze_game/bot/.env`
3. Start the bot with `python3 maze_game/run.py`

## Credits

1. [@xsafter (GitHub)](https://github.com/xsafter) - Making the [maze generation algorithm](https://github.com/xsafter/map-generator)

# --<>--<>--<>--maze_game_bot--<>--<>--<>--
(c) cat dev 2024