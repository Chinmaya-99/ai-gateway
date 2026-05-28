from pydantic import BaseSettings

class Settings(BaseSettings):
    app_name: str = "AI Gateway"
    debug: bool = True

settings = Settings()
