from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OCR + GenAI App"
    debug: bool = False
    project_id: str
    location: str
    credentials: str
    database: str
    firebase_credentials: str

    class Config:
        env_file = ".env"


settings = Settings()
