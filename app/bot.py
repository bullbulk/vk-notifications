import asyncio
import platform
import traceback

import discord

if platform.system() == "Windows":
    if isinstance(
        asyncio.get_event_loop_policy(), asyncio.WindowsProactorEventLoopPolicy
    ):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from discord import Message
from discord.ext import commands
from loguru import logger

from app import settings, cogs


class CustomBot(commands.Bot):
    last_command = None
    owner = None

    def __init__(self, command_prefix: str, *args, **kwargs):
        super().__init__(command_prefix=command_prefix, *args, **kwargs)
        asyncio.run(self.register_cogs())

    async def on_ready(self):
        logger.info(f"We have logged in as {self.user}")
        self.owner = await self.fetch_user(settings.DISCORD_OWNER_ID)
        await self.tree.sync()

    async def register_cogs(self):
        await self.add_cog(cogs.VkCog(self))
        await self.add_cog(cogs.SubscriptionCog(self))

    async def on_message(self, message: Message):
        if message.author == self.user:
            return

        await self.process_commands(message)

    async def on_command_error(self, ctx, exception):
        if exception.__class__ in (
            discord.ext.commands.errors.CommandNotFound,
            discord.app_commands.CommandNotFound,
        ):
            return

        tb = "".join(
            traceback.format_exception(
                type(exception), exception, exception.__traceback__
            )
        )

        logger.error(tb)
        await self.owner.send(tb)

    async def on_error(self, *args, **kwargs):
        tb = traceback.format_exc()

        logger.error(tb)
        await self.owner.send(tb)
