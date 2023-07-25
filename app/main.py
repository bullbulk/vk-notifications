import discord
from sqlalchemy import exists

from app import Subscription
from app.config import settings
from app.db.session import SessionLocal

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("??subscribe"):
        session = SessionLocal()
        print(
            session.query(Subscription)
            .where(Subscription.channel_id == message.channel.id)
            .exists()
        )
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


client.run(settings.DISCORD_TOKEN)
