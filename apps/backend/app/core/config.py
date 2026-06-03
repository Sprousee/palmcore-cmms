from pathlib import Path
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    PROJECT_NAME: str = Field("PalmCore CMMS", env="PROJECT_NAME")
    ENVIRONMENT: str = Field("development", env="ENVIRONMENT")
    DATABASE_URL: str = Field(..., env="DATABASE_URL")
    JWT_SECRET: str = Field(..., env="JWT_SECRET")
    JWT_ALGORITHM: str = Field("HS256", env="JWT_ALGORITHM")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(15, env="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(30, env="JWT_REFRESH_TOKEN_EXPIRE_DAYS")
    REDIS_URL: str = Field("redis://localhost:6379/0", env="REDIS_URL")
    QR_BASE_URL: str = Field("http://localhost:8000/equipment", env="QR_BASE_URL")

    class Config:
        resolved_path = Path(__file__).resolve()
        if len(resolved_path.parents) > 4:
            env_file_path = resolved_path.parents[4] / ".env"
        else:
            env_file_path = Path(".env")

        env_file = str(env_file_path)
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()
