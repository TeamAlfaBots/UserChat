"""
MongoDB layer.

Stores, per chat (group or DM):
- whether chat is enabled or disabled (.chatoff / .chaton)

Stores, per user:
- recent message history (for AI context)
- learned "style notes" (short summary of how the user talks, updated over time)
"""

from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient

import config

_client = AsyncIOMotorClient(config.MONGO_URI)
_db = _client[config.MONGO_DB_NAME]

chats_col = _db["chats"]        # chat_id -> {enabled: bool}
users_col = _db["users"]        # user_id -> {history: [...], style_notes: str}


# ---------- Chat on/off state ----------

async def is_chat_enabled(chat_id: int) -> bool:
    doc = await chats_col.find_one({"chat_id": chat_id})
    if doc is None:
        return True  # default: enabled
    return doc.get("enabled", True)


async def set_chat_enabled(chat_id: int, enabled: bool):
    await chats_col.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": enabled, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


# ---------- Per-user memory ----------

async def get_user(user_id: int) -> dict:
    doc = await users_col.find_one({"user_id": user_id})
    if doc is None:
        doc = {
            "user_id": user_id,
            "history": [],
            "style_notes": "",
        }
        await users_col.insert_one(doc)
    return doc


async def add_message_to_history(user_id: int, role: str, text: str):
    """role is 'user' or 'assistant'."""
    await users_col.update_one(
        {"user_id": user_id},
        {
            "$push": {
                "history": {
                    "$each": [
                        {
                            "role": role,
                            "text": text,
                            "ts": datetime.now(timezone.utc),
                        }
                    ],
                    "$slice": -config.MAX_HISTORY_MESSAGES,
                }
            }
        },
        upsert=True,
    )


async def get_history(user_id: int) -> list:
    doc = await get_user(user_id)
    return doc.get("history", [])


async def update_style_notes(user_id: int, style_notes: str):
    """Overwrite the short learned-style summary for a user."""
    await users_col.update_one(
        {"user_id": user_id},
        {"$set": {"style_notes": style_notes, "updated_at": datetime.now(timezone.utc)}},
        upsert=True,
    )


async def get_style_notes(user_id: int) -> str:
    doc = await get_user(user_id)
    return doc.get("style_notes", "")
