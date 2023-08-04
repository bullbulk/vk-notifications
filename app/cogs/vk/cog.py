import asyncio
import io
from pathlib import Path
from urllib.parse import urlparse

import aiohttp
import discord.utils
import vkbottle
from discord.ext import commands
from sqlalchemy import select
from vkbottle_types.codegen.objects import WallWallpostFull, WallWallpostAttachmentType
from vkbottle_types.responses import wall

from app import settings
from app.db.session import SessionLocal
from app.models.bot import Post, Subscription


def get_extension_from_url(url: str):
    parsed_url = urlparse(url)
    path = parsed_url.path
    return Path(path).suffix


class VkCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.vk_bot = vkbottle.Bot(settings.VK_SERVICE_KEY)

    @commands.Cog.listener()
    async def on_ready(self):
        await self.vk_listen()

    async def vk_listen(self):
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            try:
                posts = await self.get_posts()
                await self.process_wall_response(posts)
            except Exception:  # noqa
                continue
            await asyncio.sleep(20)  # task runs every 60 seconds

    async def get_posts(self):
        return await self.vk_bot.api.wall.get(owner_id=settings.VK_GROUP_ID)

    async def process_wall_response(
        self, posts: wall.GetResponseModel | wall.GetExtendedResponseModel
    ):
        if not posts.count:
            return

        hashes = list(map(lambda x: x.hash, posts.items))

        session = SessionLocal()

        db_posts = {
            v.hash: v
            for v in session.scalars(select(Post).where(Post.hash.in_(hashes))).all()
        }

        posts_to_process = []
        for post in posts.items:
            if post.hash not in db_posts:
                session.add(Post(hash=post.hash))  # noqa
            posts_to_process.append(post)

        session.commit()
        session.close()

        posts_to_process.reverse()

        for post in posts_to_process:
            await self.process_post(post)

    async def process_post(self, post: WallWallpostFull):
        with SessionLocal() as session:
            if db_obj := session.query(Post).where(Post.hash == post.hash).first():
                if db_obj.status != Post.PostStatus.OBTAINED:
                    return
            else:
                db_obj = Post(hash=post.hash)  # noqa

            db_obj.status = Post.PostStatus.IN_PROCESS
            session.add(db_obj)
            session.commit()

            subscribed_channels = await self.get_subscribed_channels()
            for channel in subscribed_channels:
                await self.send_post(channel, post)

            db_obj.status = Post.PostStatus.PROCESSED
            session.add(db_obj)
            session.commit()

    async def send_post(self, channel, post):
        message_text = post.text

        if settings.DISCORD_MENTION_ROLE:
            if role := discord.utils.get(
                channel.guild.roles, name=settings.DISCORD_MENTION_ROLE
            ):
                message_text = f"{role.mention} {message_text}"

        attachments = await self.build_attachments(post)

        await channel.send(message_text, files=attachments)

    async def get_subscribed_channels(self):
        with SessionLocal() as session:
            subscriptions = session.scalars(select(Subscription)).all()
            channels = []
            for sub in subscriptions:
                if channel := self.bot.get_channel(sub.channel_id):
                    channels.append(channel)
        return channels

    async def build_attachments(self, post: WallWallpostFull):
        files = []

        async with aiohttp.ClientSession() as session:
            for index, attachment in enumerate(post.attachments):
                if attachment.type.value == WallWallpostAttachmentType.PHOTO.value:
                    if url := attachment.photo.sizes[-1].url:
                        async with session.get(url) as resp:
                            img = await resp.read()
                            ext = get_extension_from_url(url)
                            filename = f"image_{index}{ext}"

                            with io.BytesIO(img) as fp:
                                files.append(
                                    discord.File(
                                        fp,
                                        filename=filename,
                                    )
                                )

        return files
