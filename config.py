import os

API_ID       = int(os.environ.get("API_ID", 0))
API_HASH     = os.environ.get("API_HASH", "")
BOT_TOKEN    = os.environ.get("BOT_TOKEN", "")
ADMIN_IDS    = [int(x) for x in os.environ.get("ADMIN_IDS", "0").split(",")]
DEFAULT_DAYS = int(os.environ.get("DEFAULT_DAYS", 30))
MONGO_URI    = os.environ.get("MONGO_URI", "mongodb://localhost:27017")
DB_NAME      = os.environ.get("DB_NAME", "autoremove_bot")
LOG_CHANNEL  = int(os.environ.get("LOG_CHANNEL", 0))
