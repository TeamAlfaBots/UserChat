# Eco Userbot

A Telegram **userbot** (runs on your personal account via session string,
not a BotFather bot) that chats casually with people — friendly, caring,
witty tone, powered by DeepSeek. It remembers each user and slowly learns
their chatting style.

## How it behaves

- **Groups:** if a message is a normal message (not a reply, not an
  @mention of someone), the bot may jump in and reply, based on
  `GROUP_REPLY_CHANCE` (default 35%) — so it feels natural, not spammy.
- **DMs:** replies to every message.
- **Memory:** each user's recent messages are stored in MongoDB and used
  as context. Every few messages, the bot asks DeepSeek to summarize how
  that user types (casual/formal, emoji use, etc.) and saves a short note
  to sound more natural to them over time.
- **Owner control:** only the owner account (`OWNER_ID`) can run:
  - `.chatoff` — disables the bot's replies in that chat (group or DM)
  - `.chaton` — re-enables it
- **Typing animation:** shows "typing..." for a moment before every reply
  so it feels like a real person.

**Persona note:** the bot is designed to be warm, caring and a little
witty — but it will not engage romantically/flirtatiously, and it
deflects heavy topics (medical, legal, technical, etc.) since it's built
for casual chat only, not to give advice on serious topics.

## Project structure

```
.
├── main.py              # entrypoint, Pyrogram handlers
├── config.py             # loads all settings from environment
├── database.py            # MongoDB (per-chat on/off, per-user memory)
├── ai.py                 # DeepSeek API calls + style learning
├── health.py              # HTTP server for Render + UptimeRobot
├── generate_session.py     # one-time script to create your SESSION_STRING
├── requirements.txt
├── Dockerfile
├── render.yaml
└── .env.example
```

## 1. Get your Telegram API credentials

1. Go to https://my.telegram.org → **API development tools**
2. Create an app, note down `API_ID` and `API_HASH`

## 2. Generate a session string

This logs the bot in as **your own account**. Run this on your own
computer (needs your phone + OTP):

```bash
pip install pyrogram tgcrypto
python generate_session.py
```

Follow the prompts, copy the printed session string — this goes in
`SESSION_STRING`. **Never share this string with anyone** — it's
equivalent to your account password.

## 3. Get your Telegram user ID (for OWNER_ID)

Message [@userinfobot](https://t.me/userinfobot) on Telegram — it replies
with your numeric user ID.

## 4. Get a DeepSeek API key

Sign up at https://platform.deepseek.com and generate an API key.

## 5. Set up MongoDB

Create a free cluster at https://www.mongodb.com/cloud/atlas, get your
connection string (`MONGO_URI`).

## 6. Configure environment

Copy `.env.example` to `.env` and fill in all values:

```bash
cp .env.example .env
```

## 7. Run locally

```bash
pip install -r requirements.txt
python main.py
```

## 8. Deploy on Render

1. Push this project to a GitHub repo
2. On Render, create a **New Web Service**, connect the repo — it will
   auto-detect `render.yaml` and `Dockerfile`
3. Fill in the environment variables marked `sync: false` in the Render
   dashboard (API_ID, API_HASH, SESSION_STRING, OWNER_ID,
   DEEPSEEK_API_KEY, MONGO_URI)
4. Deploy

### Keeping it awake (Render free tier)

Render's free web services sleep after inactivity. Point
[UptimeRobot](https://uptimerobot.com) (or any uptime pinger) at:

```
https://<your-render-app>.onrender.com/ping
```

every 5 minutes, so it never sleeps.

## Commands (owner only, sent from your own account)

| Command    | Effect                              |
|------------|--------------------------------------|
| `.chatoff` | Disable bot replies in this chat     |
| `.chaton`  | Re-enable bot replies in this chat   |

## Notes on safety / ToS

This is a **userbot** — it runs on your real account, not a bot account.
Telegram's terms discourage automation on user accounts; keep the reply
chance reasonable in groups and avoid aggressive/spammy behavior to
reduce the risk of limits on your account.
