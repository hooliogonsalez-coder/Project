from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://biometric:password@db/biometric_db"
    API_KEY: str = "your-secret-api-key"
    SECRET_KEY: str = "your-secret-key"


settings = Settings()