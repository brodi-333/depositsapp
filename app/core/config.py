from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_ignore_empty=True, extra="ignore"
    )

    PROJECT_NAME: str
    PROJECT_NAME_HTML: str
    APP_VERSION: str = "0.1.0"
    SECRET_KEY: str = "89d1095c8b484388434918f110697900e0c71d7b1226b8ee1b2d9fe5a95e2b9f"
    SECURITY_ALGORITHM: str = "HS256"
    SECURITY_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30


settings = Settings()