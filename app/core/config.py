from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Database
    database_url: str = "postgresql://postgres:postgres@localhost:5432/taskmanager"

    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"

    # Teams webhook
    teams_webhook_url: Optional[str] = None

    # App
    app_name: str = "Task Manager"
    debug: bool = False


settings = Settings()
