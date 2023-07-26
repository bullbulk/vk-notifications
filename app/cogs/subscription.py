from discord import Message
from discord.ext import commands
from sqlalchemy import exists

from app import Subscription
from app.db.session import SessionLocal


class SubscriptionCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def subscribe(self, message: Message):
        session = SessionLocal()

        if session.query(
            exists().where(Subscription.channel_id == message.channel.id)
        ).scalar():
            session.close()
            return await message.channel.send(":x: Канал уже подписан на обновления.")

        session.add(Subscription(channel_id=message.channel.id))  # noqa
        session.commit()
        session.close()
        return await message.channel.send(
            ":white_check_mark: Канал подписан на обновления."
        )
