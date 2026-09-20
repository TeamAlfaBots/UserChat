import asyncio
import random
import logging

from pyrogram import Client, filters
from pyrogram.enums import ChatAction, ChatType
from pyrogram.types import Message

import config
import database
import ai
from health import start_health_server

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("eco-userbot")

app = Client(
    "eco_userbot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    session_string=config.SESSION_STRING,
)


def is_owner(user_id: int) -> bool:
    return config.OWNER_ID is not None and user_id == config.OWNER_ID


async def send_with_typing(message: Message, text: str):
    """Show a realistic typing animation before sending the reply."""
    try:
        await app.send_chat_action(message.chat.id, ChatAction.TYPING)
        # Simulate typing speed roughly proportional to reply length
        delay = min(max(len(text) * 0.04, 1.0), 4.0)
        await asyncio.sleep(delay)
    except Exception:
        pass
    await message.reply_text(text)


def was_mentioned_or_replied(message: Message) -> bool:
    """True if this message is a reply to someone, or @mentions someone."""
    if message.reply_to_message is not None:
        return True
    if message.entities:
        for e in message.entities:
            if e.type.name in ("MENTION", "TEXT_MENTION"):
                return True
    return False


# ---------------- Owner control commands ----------------

@app.on_message(
    filters.me
    & filters.command("chatoff", prefixes=config.COMMAND_PREFIX)
)
async def chat_off(client: Client, message: Message):
    chat_id = message.chat.id
    await database.set_chat_enabled(chat_id, False)
    await message.edit_text("🔴 Chat disabled here.")


@app.on_message(
    filters.me
    & filters.command("chaton", prefixes=config.COMMAND_PREFIX)
)
async def chat_on(client: Client, message: Message):
    chat_id = message.chat.id
    await database.set_chat_enabled(chat_id, True)
    await message.edit_text("🟢 Chat enabled here.")


# ---------------- Core chat handler ----------------

@app.on_message(
    filters.text
    & ~filters.me
    & ~filters.bot
    & ~filters.via_bot
)
async def handle_message(client: Client, message: Message):
    chat_id = message.chat.id
    user = message.from_user
    if user is None:
        return
    user_id = user.id

    # Owner runs commands via filters.me above; don't also chat-reply to self
    if is_owner(user_id) and message.text.startswith(config.COMMAND_PREFIX):
        return

    if not await database.is_chat_enabled(chat_id):
        return

    is_private = message.chat.type == ChatType.PRIVATE

    if is_private:
        should_reply = True
    else:
        # Group: only consider messages that do NOT mention/reply to someone
        # (keeps the bot out of other people's conversations), then reply
        # randomly to keep it natural instead of replying to every message.
        if was_mentioned_or_replied(message):
            return
        should_reply = random.random() < config.GROUP_REPLY_CHANCE

    if not should_reply:
        # Still remember the message for context/style learning even if we don't reply
        await database.add_message_to_history(user_id, "user", message.text)
        return

    await database.add_message_to_history(user_id, "user", message.text)

    reply_text = await ai.generate_reply(user_id, message.text)

    await send_with_typing(message, reply_text)
    await database.add_message_to_history(user_id, "assistant", reply_text)

    # Occasionally refresh the learned style note for this user
    history = await database.get_history(user_id)
    if len(history) % 6 == 0:
        asyncio.create_task(ai.maybe_update_style_notes(user_id))


async def main():
    await start_health_server()
    log.info("Health server started on port %s", config.PORT)

    await app.start()
    log.info("Userbot started.")

    me = await app.get_me()
    log.info("Logged in as %s (id=%s)", me.first_name, me.id)

    await asyncio.Event().wait()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
