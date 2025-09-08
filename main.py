import asyncio
import sys

import discord

if sys.platform == "win32" and isinstance(
    asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy
):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app import logger
from app.bot import CustomBot
from app.config import settings

logger.init()

intents = discord.Intents.default()
intents.message_content = True

client = CustomBot("??", intents=intents)

client.run(settings.DISCORD_TOKEN)
