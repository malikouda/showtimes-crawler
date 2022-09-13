from pydantic import BaseSettings


class Settings(BaseSettings):
    PUSHOVER_APP_TOKEN: str
    PUSHOVER_USER_KEY: str


settings = Settings()
