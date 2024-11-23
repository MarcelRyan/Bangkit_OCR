from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "OCR + GenAI App"
    debug: bool = False
    ocr_model_path: str = "./models"

    class Config:
        env_file = ".env"


settings = Settings()