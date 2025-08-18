from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    PUSHOVER_APP_TOKEN: str
    PUSHOVER_USER_KEY: str
    CTXT_URL: str = "https://ctxt.io/new"


settings = Settings()
