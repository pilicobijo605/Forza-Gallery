from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "API Forza"
    database_url: str = "sqlite+aiosqlite:///./forza.db"
    secret_key: str = "cambia-esto"
    access_token_expire_minutes: int = 1440
    admin_username: str = "admin"
    admin_email: str = "admin@forzagram.com"
    admin_password: str = "admin1234"

    model_config = {"env_file": ".env"}


settings = Settings()
