"""
EduTrack AI - Configuration Settings
"""
import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_NAME: str = "EduTrack AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./edutrack.db"
    # For PostgreSQL: postgresql://user:password@localhost:5432/edutrack
    
    # JWT
    SECRET_KEY: str = "edutrack-ai-super-secret-key-change-in-production-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"]
    
    # Upload
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Grading (default, configurable via DB)
    MIN_ATTENDANCE_PERCENT: float = 75.0
    LOW_ATTENDANCE_ALERT: float = 65.0
    MIN_PASS_MARKS_PERCENT: float = 40.0
    
    # ML
    ML_MODEL_DIR: str = "ml_models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
