import enum

from sqlalchemy import BigInteger, Enum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscription"

    channel_id: Mapped[int] = mapped_column(BigInteger, server_default="0", unique=True)


class Post(Base):
    class PostStatus(enum.Enum):
        OBTAINED = 0
        PROCESSED = 1
        IN_PROCESS = 2

    __tablename__ = "post"

    hash: Mapped[str] = mapped_column(unique=True)
    status: Mapped[int] = mapped_column(Enum(PostStatus), default=PostStatus.OBTAINED)
