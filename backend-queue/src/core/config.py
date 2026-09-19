from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env.example", extra="ignore")

    CORE_API_URL: str = "http://localhost:8000"
    CORE_TIMEOUT: int = 5

    DEFAULT_ACTIVE_WINDOWS: int = 1

    EVENT_API_KEY: str = ""


settings = Settings()