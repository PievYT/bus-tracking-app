from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "BusSync API"
    envrioment: str = "development"
    database_url: str = "sqlite:///./bussync.db"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()