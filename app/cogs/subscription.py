import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger
from sqlalchemy import select

from app import Subscription
from app.db.session import get_session


class SubscriptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="subscribe", description="Подписать канал на уведомления"
    )
    @app_commands.checks.has_permissions(administrator=True)
    async def subscribe(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        try:
            async with get_session() as session:
                stmt = select(Subscription).where(
                    Subscription.channel_id == interaction.channel.id
                )

                result = await session.execute(stmt)
                existing_sub = result.scalars().first()

                if existing_sub:
                    await session.delete(existing_sub)
                    message = ":x: Канал отписан от обновлений."
                else:
                    logger.info(f"Subscribing channel: {interaction.channel.id}")
                    session.add(Subscription(channel_id=interaction.channel.id))
                    message = ":white_check_mark: Канал подписан на обновления."

            await interaction.followup.send(message, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in subscribe command: {str(e)}")
            if interaction.response.is_done():
                await interaction.followup.send(
                    "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.",
                    ephemeral=True,
                )
            else:
                await interaction.response.send_message(
                    "Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже.",
                    ephemeral=True,
                )

    @subscribe.error
    async def handle_subscribe_error(self, interaction: discord.Interaction, error):
        if isinstance(error, discord.app_commands.errors.MissingPermissions):
            await interaction.response.send_message(
                "Недостаточно прав для выполнения действия", ephemeral=True
            )
