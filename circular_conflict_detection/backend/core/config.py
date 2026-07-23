import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Circular Conflict Detector API"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    class Config:
        case_sensitive = True

settings = Settings()