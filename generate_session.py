"""
Run this ONCE locally (not on Render) to generate your SESSION_STRING.

    python generate_session.py

It will ask for your API_ID, API_HASH, phone number, and the OTP Telegram
sends you. It then prints a session string — copy that into your .env file
(or Render environment variables) as SESSION_STRING.

Keep this string secret: anyone with it has full access to your Telegram
account, exactly like your password + OTP.
"""

from pyrogram import Client

api_id = int(input("Enter your API_ID: ").strip())
api_hash = input("Enter your API_HASH: ").strip()

with Client("session_gen", api_id=api_id, api_hash=api_hash, in_memory=True) as app:
    session_string = app.export_session_string()
    print("\n\nYour SESSION_STRING (copy this into .env):\n")
    print(session_string)
    print()
