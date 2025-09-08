import dotenv
from pydantic import PostgresDsn, model_validator, Field
from pydantic_settings import BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    DB_SERVER: str = Field(alias="DB_SERVER")
    DB_USER: str = Field(alias="DB_USER")
    DB_PASSWORD: str = Field(alias="DB_PASSWORD")
    DB_NAME: str = Field(alias="DB_NAME")
    DATABASE_URI: str | None = Field(alias="DATABASE_URI")

    @model_validator(mode="before")
    def assemble_db_connection(cls, v):  # noqa
        if v.get("DATABASE_URI"):
            return v
        v["DATABASE_URI"] = str(
            PostgresDsn.build(
                scheme="postgresql+psycopg",
                username=v.get("DB_USER"),
                password=v.get("DB_PASSWORD"),
                host=v.get("DB_SERVER"),
                path=f"{v.get('DB_NAME') or ''}",
            )
        )
        return v

    DISCORD_TOKEN: str
    DISCORD_OWNER_ID: int
    DISCORD_MENTION_ROLE: str | None = "Колокольчик"

    VK_SERVICE_KEY: str
    VK_GROUP_ID: int

    class Config:
        case_sensitive = True


settings = Settings()
