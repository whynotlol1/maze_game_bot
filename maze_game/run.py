from requests import exceptions
from dotenv import load_dotenv
from datetime import datetime
from bot import data_api
from bot.bot import bot
import sys
import os

if __name__ == "__main__":
    load_dotenv()
    print(f"[{datetime.now().strftime("%H:%M:%S")}] Attempting to start data API...")
    data_api.start_api()
    print(f"[{datetime.now().strftime("%H:%M:%S")}] Data API started.")
    print(f"[{datetime.now().strftime("%H:%M:%S")}] Starting the bot...")
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except (exceptions.ConnectionError, exceptions.ReadTimeout) as e:
        print(f"[{datetime.now().strftime("%H:%M:%S")}] Caught exception {e}. Restarting the bot...")
        sys.stdout.flush()
        os.execv(sys.argv[0], sys.argv)
    else:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
