from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    GOOGLE_API_KEY: str
    MODEL_NAME: str

    class Config:
        env_file = ".env"

settings = Settings()
