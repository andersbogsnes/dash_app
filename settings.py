from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_url: SecretStr = "postgresql+psycopg://postgres:postgres@localhost:5432/postgres"
