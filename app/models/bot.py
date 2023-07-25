from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class Subscription(Base):
    __tablename__ = "subscription"

    channel_id: Mapped[int] = mapped_column(BigInteger, server_default="0", unique=True)
