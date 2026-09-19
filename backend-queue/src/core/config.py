from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    SECRET_KEY: str = "dev-secret-change-me"
    ALGORITHM: str = "HS256"
    DATABASE_URL: str = "sqlite:///./queue.db"

    # адрес backend-core и параметры HTTP-клиента
    CORE_API_URL: str = "http://localhost:8000"
    CORE_TIMEOUT: int = 5
    CORE_CACHE_TTL: int = 60 


settings = Settings()