from os import environ

import dotenv
from pydantic import PostgresDsn, computed_field
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    DB_SERVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    @computed_field  # noqa
    @property
    def DATABASE_URI(cls) -> str | None:  # noqa
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                username=cls.DB_USER,
                password=cls.DB_PASSWORD,
                host=cls.DB_SERVER,
                path=cls.DB_NAME or "",
            )
        )

    DISCORD_TOKEN: str = environ.get("DISCORD_TOKEN")

    class Config:
        case_sensitive = True


settings = Settings()
