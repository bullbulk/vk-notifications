import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger
from sqlalchemy import exists

from app import Subscription
from app.db.session import SessionLocal


class SubscriptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="subscribe", description="Подписать канал на уведомления"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def subscribe(self, interaction: discord.Interaction):
        with SessionLocal() as session:
            if session.query(
                exists().where(Subscription.channel_id == interaction.channel.id)
            ).scalar():
                return await interaction.response.send_message(
                    ":x: Канал уже подписан на обновления.", ephemeral=True
                )

            logger.info(f"Writing subscribe: {interaction.channel.id}")

            # noinspection PyArgumentList
            session.add(Subscription(channel_id=interaction.channel.id))
            session.commit()

        return await interaction.response.send_message(
            ":white_check_mark: Канал подписан на обновления.", ephemeral=True
        )

    @subscribe.error
    async def handle_subscribe_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "Недостаточно прав для выполнения действия", ephemeral=True
            )
