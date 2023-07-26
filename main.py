import discord

from app import logger
from app.bot import CustomBot
from app.config import settings

logger.init()

intents = discord.Intents.default()
intents.message_content = True

client = CustomBot("??", intents=intents)

client.run(settings.DISCORD_TOKEN)
