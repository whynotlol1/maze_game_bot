from Crypto.Util.number import bytes_to_long
from base64 import b64encode

if __name__ == "__main__":
    print(f"Paste the following string in the .env file: bottoken={bytes_to_long(b64encode(input("Paste your Telegram bot token there: ").encode()))}")
