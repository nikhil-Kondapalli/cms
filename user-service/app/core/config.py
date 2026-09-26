from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str

    app_version: str

    debug: bool

    host: str

    port: int

    database_url: str

    jwt_public_key_path: str

    jwt_algorithm: str

    jwt_issuer: str

    jwt_audience: str

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()  # type: ignore
