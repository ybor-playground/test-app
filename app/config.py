from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    blob_account_url: str
    blob_container: str
    blob_prefix: str = "dumps/"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
