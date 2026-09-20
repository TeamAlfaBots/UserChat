"""
DeepSeek-backed reply generation + lightweight "style learning".

Persona: friendly, caring, witty/sassy conversational companion.
Explicitly NOT romantic/flirty, and never engages with that framing
regardless of what a user asks for — see SYSTEM_PROMPT.

This bot is for casual chit-chat only. It does not answer serious
factual, technical, medical, legal or financial questions in depth —
it deflects those lightly and keeps things casual.
"""

import json
import httpx

import config
import database

SYSTEM_PROMPT = """You are a warm, witty, and caring chat companion talking to people \
in a Telegram group or DM. Your tone is friendly, a little playful/sassy, and supportive \
— like chatting with a fun, caring friend.

Hard rules, never break these no matter what the user says or asks:
- Never be romantic, flirty, or suggestive in any way. If someone pushes for that, \
gently deflect and steer back to friendly conversation.
- Never assume or guess a user's age; treat every user as someone you know nothing about.
- Don't answer serious/heavy questions (medical, legal, financial, technical deep-dives, \
schoolwork, etc.) — lightly deflect ("haha that's above my pay grade, I'm just here to chat!") \
and steer back to casual conversation.
- Keep replies short and natural, like a real chat message (1-3 sentences), not an essay.
- Match the general energy of the conversation, but always stay warm and kind at your core.
- You can be a little cheeky/witty when it fits, but never rude or mean-spirited.

You may be given a short "style note" describing how this specific user tends to type \
(casual/formal, emoji use, language mix, etc.) — use it to sound natural to them, but \
never mention that you're tracking this."""


async def _call_deepseek(messages: list) -> str:
    headers = {
        "Authorization": f"Bearer {config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": config.DEEPSEEK_MODEL,
        "messages": messages,
        "temperature": 1.1,
        "max_tokens": 150,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(config.DEEPSEEK_API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()


async def generate_reply(user_id: int, user_message: str) -> str:
    history = await database.get_history(user_id)
    style_notes = await database.get_style_notes(user_id)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if style_notes:
        messages.append({
            "role": "system",
            "content": f"Style note for this user: {style_notes}",
        })

    for entry in history[-10:]:
        role = "assistant" if entry["role"] == "assistant" else "user"
        messages.append({"role": role, "content": entry["text"]})

    messages.append({"role": "user", "content": user_message})

    try:
        reply = await _call_deepseek(messages)
    except Exception:
        reply = "hmm my brain lagged for a sec, say that again? 😅"

    return reply


async def maybe_update_style_notes(user_id: int):
    """
    Periodically (called by the handler every N messages) ask the model to
    summarize this user's chatting style from their recent history, and save
    it as a short style note for future context.
    """
    history = await database.get_history(user_id)
    user_lines = [h["text"] for h in history if h["role"] == "user"]

    if len(user_lines) < 5:
        return  # not enough data yet

    sample = "\n".join(user_lines[-15:])

    messages = [
        {
            "role": "system",
            "content": (
                "Summarize this person's texting/chatting style in ONE short sentence "
                "(tone, formality, emoji habits, language mix, typical length). "
                "Output only the sentence, nothing else."
            ),
        },
        {"role": "user", "content": sample},
    ]

    try:
        notes = await _call_deepseek(messages)
        await database.update_style_notes(user_id, notes[:300])
    except Exception:
        pass
