import os
from dotenv import load_dotenv

load_dotenv()


def _get_int(key: str, default=None):
    val = os.environ.get(key)
    if val is None or val == "":
        return default
    return int(val)


def _get_list(key: str):
    val = os.environ.get(key, "")
    if not val:
        return []
    return [int(x.strip()) for x in val.split(",") if x.strip()]


# ---- Telegram (userbot login) ----
API_ID = _get_int("API_ID")
API_HASH = os.environ.get("API_HASH")
SESSION_STRING = os.environ.get("SESSION_STRING")

# ---- Owner ----
# Owner's own Telegram user ID. Only this ID can run .chatoff / .chaton
OWNER_ID = _get_int("OWNER_ID")

# ---- DeepSeek AI ----
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
DEEPSEEK_API_URL = os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com/chat/completions")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# ---- MongoDB ----
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "eco_userbot")

# ---- Behaviour tuning ----
# In groups, don't reply to every single message — reply with this probability
# to messages that aren't a mention/reply to the bot (0.0 - 1.0)
GROUP_REPLY_CHANCE = float(os.environ.get("GROUP_REPLY_CHANCE", "0.35"))

# Max messages of history kept per user for context + style learning
MAX_HISTORY_MESSAGES = _get_int("MAX_HISTORY_MESSAGES", 20)

# Command prefix for owner control commands
COMMAND_PREFIX = os.environ.get("COMMAND_PREFIX", ".")

# ---- Health server (for Render + UptimeRobot) ----
PORT = _get_int("PORT", 8080)
