# Discord Alert

Discord channel monitoring with Telegram notifications.

This service runs as a Discord self-bot on a separate Discord account and forwards selected channel messages to Telegram.

> Operational note: using a Discord user token/self-bot can violate Discord's terms of service. Use only with accounts and channels where you understand the risk.

## Features

- Monitors one or more Discord channels by channel ID.
- Forwards messages, embeds, and attachment links to Telegram.
- Optional keyword filtering.
- Can run locally or as a systemd service.

## Get a Discord User Token

1. Open Discord in a browser.
2. Open Developer Tools (`F12`) → Network → filter by `api`.
3. Refresh the page and open any request to `discord.com/api`.
4. Copy the `Authorization` header value.

Alternative browser-console snippet:

```js
(webpackChunkdiscord_app.push([[''],{},e=>{m=[];for(let c in e.c)m.push(e.c[c])}]),m).find(m=>m?.exports?.default?.getToken!==void 0).exports.default.getToken()
```

## Get a Discord Channel ID

1. Discord → Settings → Advanced → enable Developer Mode.
2. Right-click the target channel.
3. Select **Copy Channel ID**.

## Installation

```bash
cd /home/gpt/discord-monitor
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env
```

Required environment variables:

- `DISCORD_TOKEN` — Discord user token.
- `TELEGRAM_BOT_TOKEN` — Telegram bot token from BotFather.
- `TELEGRAM_CHAT_ID` — Telegram chat/channel ID for notifications.
- `CHANNEL_IDS` — comma-separated Discord channel IDs.
- `KEYWORDS` — optional comma-separated keyword filter; empty means forward all messages.

## Test Run

```bash
source venv/bin/activate
python bot.py
```

## Deploy as systemd

```bash
sudo cp deploy/systemd/discord-monitor.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable discord-monitor
sudo systemctl start discord-monitor
sudo journalctl -u discord-monitor -f
```

## Security

- Do not commit `.env`.
- Keep the Discord token in a private environment file only.
- Rotate the token if it was ever exposed.
