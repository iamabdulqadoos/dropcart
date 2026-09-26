from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "DropCart API"
    database_url: str
    redis_url: str
    payment_gateway_url: str
    webhook_secret: str

    class Config:
        env_file = ".env"


settings = Settings()