import asyncio
import logging
import os

import discord
from dotenv import load_dotenv
from telegram import Bot
from telegram.constants import ParseMode
from telegram.error import TelegramError

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
CHANNEL_IDS = [int(x.strip()) for x in os.getenv("CHANNEL_IDS", "").split(",") if x.strip()]
KEYWORDS_RAW = os.getenv("KEYWORDS", "")
KEYWORDS = [k.strip().lower() for k in KEYWORDS_RAW.split(",") if k.strip()]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger(__name__)


def escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def format_message(message: discord.Message) -> str:
    server = escape_html(message.guild.name) if message.guild else "DM"
    channel = escape_html(getattr(message.channel, "name", "unknown"))
    author = escape_html(message.author.display_name)
    content = message.content or ""

    msg_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}" if message.guild else ""
    header = f'📢 <b>{server}</b> · <a href="{msg_link}">#{channel}</a>' if msg_link else f"📢 <b>{server}</b> · #{channel}"
    lines = [header, f"👤 {author}\n"]

    if content:
        lines.append(escape_html(content))

    for embed in message.embeds:
        parts = []
        if embed.title:
            parts.append(f"<b>{escape_html(embed.title)}</b>")
        if embed.url:
            parts.append(embed.url)
        if embed.description:
            parts.append(escape_html(embed.description[:800]))
        if parts:
            lines.append("\n".join(parts))

    for att in message.attachments:
        lines.append(f"📎 {att.url}")

    return "\n".join(lines)


def passes_filter(message: discord.Message) -> bool:
    if not KEYWORDS:
        return True
    haystack = (message.content or "").lower()
    for embed in message.embeds:
        haystack += " " + (embed.title or "").lower()
        haystack += " " + (embed.description or "").lower()
    return any(kw in haystack for kw in KEYWORDS)


class DiscordMonitor(discord.Client):
    def __init__(self):
        # guild_subscriptions=True — явно подписываемся на события гильдий
        # chunk_guilds_at_startup=False — не грузим всех участников, нам не нужно
        super().__init__(
            guild_subscriptions=True,
            chunk_guilds_at_startup=False,
        )
        self.tg = Bot(token=TELEGRAM_BOT_TOKEN)

    async def on_ready(self):
        log.info(f"Logged in as {self.user} | monitoring {len(CHANNEL_IDS)} channel(s)")
        if KEYWORDS:
            log.info(f"Keyword filter: {KEYWORDS}")

        # Подписываемся на гильдии; fetch_channel как fallback если канал не в кэше
        subscribed_guilds = set()
        ok_channels = []

        for channel_id in CHANNEL_IDS:
            channel = self.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await self.fetch_channel(channel_id)
                    log.info(f"Fetched channel {channel_id} via API")
                except Exception as e:
                    log.warning(f"Channel {channel_id} inaccessible: {e}")
                    continue

            ok_channels.append(channel_id)
            guild = getattr(channel, "guild", None)
            if guild and guild.id not in subscribed_guilds:
                try:
                    await guild.subscribe()
                    subscribed_guilds.add(guild.id)
                    log.info(f"Subscribed to guild: {guild.name} ({guild.id})")
                except Exception as e:
                    log.warning(f"Could not subscribe to guild {getattr(guild, 'name', guild)}: {e}")

        log.info(f"Active channels: {ok_channels}")

        # Startup notification in Telegram
        status_lines = []
        for cid in CHANNEL_IDS:
            mark = "✅" if cid in ok_channels else "❌ no access"
            status_lines.append(f"{mark} <code>{cid}</code>")
        await self.tg.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f"🔄 <b>discord-monitor restarted</b>\n\n" + "\n".join(status_lines),
            parse_mode=ParseMode.HTML,
        )

    async def on_message(self, message: discord.Message):
        if message.channel.id not in CHANNEL_IDS:
            return
        if message.author == self.user:
            return
        if not passes_filter(message):
            return

        text = format_message(message)
        try:
            await self.tg.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=text,
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=False,
            )
            log.info(f"Forwarded: {message.author} in #{getattr(message.channel, 'name', message.channel.id)}")
        except TelegramError as e:
            log.error(f"Telegram send error: {e}")


def main():
    if not DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN is not set")
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is not set")
    if not CHANNEL_IDS:
        raise RuntimeError("CHANNEL_IDS is empty — set at least one channel ID")

    client = DiscordMonitor()
    client.run(DISCORD_TOKEN)


if __name__ == "__main__":
    main()
