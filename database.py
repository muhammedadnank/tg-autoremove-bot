"""
database.py — MongoDB Handler
Auto-Remove Bot
"""

from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from config import MONGO_URI, DB_NAME, DEFAULT_DAYS

# ── Connection (lazy — init_db() വിളിക്കുമ്പോൾ മാത്രം connect ചെയ്യും) ──────────
# Python 3.14-ൽ import time-ൽ MongoClient create ചെയ്താൽ asyncio loop conflict
# ഉണ്ടാകും. അതുകൊണ്ട് None ആയി വെക്കുന്നു, init_db()-ൽ initialize ചെയ്യും.

_client      = None
_db          = None

channels_col = None
members_col  = None
states_col   = None
settings_col = None


def init_db():
    global _client, _db, channels_col, members_col, states_col, settings_col

    _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    _db     = _client[DB_NAME]

    channels_col = _db["channels"]
    members_col  = _db["members"]
    states_col   = _db["user_states"]
    settings_col = _db["settings"]

    # Indexes
    channels_col.create_index("chat_id", unique=True)
    members_col.create_index(
        [("user_id", ASCENDING), ("chat_id", ASCENDING)], unique=True)
    members_col.create_index("remove_at")
    members_col.create_index("removed")
    members_col.create_index("chat_id")
    states_col.create_index("user_id", unique=True)
    print("✅ MongoDB connected & indexes ready")


# ══════════════════════════════════════════════════════
#  CHANNEL FUNCTIONS
# ══════════════════════════════════════════════════════

def add_channel(chat_id: int, title: str, username: str, days: int):
    channels_col.update_one(
        {"chat_id": chat_id},
        {"$set": {
            "chat_id":     chat_id,
            "title":       title or "Unknown",
            "username":    username or "",
            "remove_days": days,
            "active":      True,
            "added_at":    datetime.now(),
        }},
        upsert=True
    )


def remove_channel(chat_id: int):
    channels_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"active": False, "removed_at": datetime.now()}}
    )


def get_channels() -> list:
    return list(channels_col.find(
        {"active": True}, {"_id": 0}
    ).sort("added_at", DESCENDING))


def get_channel(chat_id: int) -> dict | None:
    return channels_col.find_one({"chat_id": chat_id}, {"_id": 0})


def set_channel_days(chat_id: int, days: int):
    channels_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"remove_days": days}}
    )


def channel_active(chat_id: int) -> bool:
    ch = channels_col.find_one({"chat_id": chat_id}, {"active": 1})
    return bool(ch and ch.get("active"))


def get_channel_days(chat_id: int) -> int:
    ch = channels_col.find_one({"chat_id": chat_id}, {"remove_days": 1})
    return ch["remove_days"] if ch else DEFAULT_DAYS


# ══════════════════════════════════════════════════════
#  MEMBER FUNCTIONS
# ══════════════════════════════════════════════════════

def add_member(user_id: int, username: str, chat_id: int,
               channel_name: str, joined_at: datetime, remove_at: datetime):
    members_col.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {
            "user_id":      user_id,
            "username":     username or str(user_id),
            "chat_id":      chat_id,
            "channel_name": channel_name,
            "joined_at":    joined_at,
            "remove_at":    remove_at,
            "removed":      False,
            "removed_at":   None,
        }},
        upsert=True
    )


def get_expired(now: datetime) -> list:
    return list(members_col.find(
        {"remove_at": {"$lte": now}, "removed": False},
        {"_id": 0}
    ))


def get_pending(chat_id: int = None) -> list:
    query = {"removed": False}
    if chat_id is not None:
        query["chat_id"] = chat_id
    return list(members_col.find(query, {"_id": 0}).sort("remove_at", ASCENDING))


def mark_removed(user_id: int, chat_id: int):
    members_col.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"removed": True, "removed_at": datetime.now()}}
    )


def mark_left(user_id: int, chat_id: int):
    """Member സ്വയം leave ചെയ്തപ്പോൾ"""
    members_col.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"removed": True, "removed_at": datetime.now(), "left_on_own": True}}
    )


def member_exists(user_id: int, chat_id: int) -> bool:
    return bool(members_col.find_one(
        {"user_id": user_id, "chat_id": chat_id, "removed": False}
    ))


def get_member(user_id: int, chat_id: int) -> dict | None:
    return members_col.find_one(
        {"user_id": user_id, "chat_id": chat_id}, {"_id": 0}
    )


def set_member_remove_date(user_id: int, chat_id: int, new_date: datetime):
    members_col.update_one(
        {"user_id": user_id, "chat_id": chat_id},
        {"$set": {"remove_at": new_date}}
    )


# ══════════════════════════════════════════════════════
#  STATS
# ══════════════════════════════════════════════════════

def total_stats() -> dict:
    total   = members_col.count_documents({})
    pending = members_col.count_documents({"removed": False})
    removed = members_col.count_documents({"removed": True})
    return {"total": total, "pending": pending, "removed": removed}


def channel_stats(chat_id: int) -> dict:
    total   = members_col.count_documents({"chat_id": chat_id})
    pending = members_col.count_documents({"chat_id": chat_id, "removed": False})
    removed = members_col.count_documents({"chat_id": chat_id, "removed": True})
    return {"total": total, "pending": pending, "removed": removed}


# ══════════════════════════════════════════════════════
#  STATE MACHINE  (manual channel ID input flow)
# ══════════════════════════════════════════════════════

def set_state(user_id: int, state: str, data: str = ""):
    states_col.update_one(
        {"user_id": user_id},
        {"$set": {"user_id": user_id, "state": state, "data": data}},
        upsert=True
    )


def get_state(user_id: int) -> tuple:
    r = states_col.find_one({"user_id": user_id})
    return (r["state"], r.get("data", "")) if r else (None, None)


def clear_state(user_id: int):
    states_col.delete_one({"user_id": user_id})


# ── init_db() ഇവിടെ call ചെയ്യരുത്! bot.py-ലെ main()-ൽ നിന്ന് call ചെയ്യണം ──
