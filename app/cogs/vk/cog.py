import asyncio

import vkbottle
from discord.ext import commands
from sqlalchemy import select
from vkbottle_types.codegen.objects import WallWallpostFull
from vkbottle_types.responses import wall

from app import settings
from app.db.session import SessionLocal
from app.models.bot import Post, Subscription


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
            posts = await self.get_posts()
            await self.process_wall_response(posts)
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
                await channel.send(post.text)
            db_obj.status = Post.PostStatus.PROCESSED
            session.add(db_obj)
            session.commit()

    async def get_subscribed_channels(self):
        with SessionLocal() as session:
            subscriptions = session.scalars(select(Subscription)).all()
            channels = []
            for sub in subscriptions:
                if channel := self.bot.get_channel(sub.channel_id):
                    channels.append(channel)
        return channels