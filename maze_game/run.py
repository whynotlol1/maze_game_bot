"""
This file is only used to start the bot.
"""

from requests import exceptions
from datetime import datetime
from bot import data_api
from bot.bot import bot
from sys import stdout
from sys import argv
from os import execv

if __name__ == "__main__":
    print(f"[{datetime.now().strftime("%H:%M:%S")}] Attempting to start data API...")
    data_api.start_api()
    print(f"[{datetime.now().strftime("%H:%M:%S")}] Data API started.")
    print(f"[{datetime.now().strftime("%H:%M:%S")}] Starting the bot...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (exceptions.ConnectionError, exceptions.ReadTimeout) as e:
        stdout.flush()
        execv(argv[0], argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
