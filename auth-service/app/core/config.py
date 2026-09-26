from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str

    environment: str

    database_url: str

    host: str

    port: int

    log_level: str

    jwt_private_key_path: str

    jwt_public_key_path: str

    jwt_algorithm: str

    jwt_issuer: str

    jwt_audience: str

    access_token_expire_minutes: int

    refresh_token_expire_days: int

    user_service_url: str = "http://localhost:8001"
    enable_opportunistic_cleanup: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
    )


settings = Settings()  # type: ignore
