from typing import Any

import dotenv
from pydantic import PostgresDsn, validator, BaseSettings

dotenv.load_dotenv()


class Settings(BaseSettings):
    DB_SERVER: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    DATABASE_URI: str | None

    @validator("DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: str | None, values: dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        return str(
            PostgresDsn.build(
                scheme="postgresql",
                user=values.get("DB_USER"),
                password=values.get("DB_PASSWORD"),
                host=values.get("DB_SERVER"),
                path=f'/{values.get("DB_NAME") or ""}',
            )
        )

    DISCORD_TOKEN: str
    DISCORD_OWNER_ID: int
    VK_SERVICE_KEY: str
    VK_GROUP_ID: int

    class Config:
        case_sensitive = True


settings = Settings()
