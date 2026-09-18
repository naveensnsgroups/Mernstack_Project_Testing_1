import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    mongo_uri: str = "mongodb://localhost:27017"
    port: int = 5000
    node_env: str = "development"
    client_url: str = "http://localhost:5173"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
