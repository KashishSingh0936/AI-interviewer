"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/ai_interview_db"
    sqlalchemy_echo: bool = True
    
    # JWT
    secret_key: str = "your-super-secret-key-change-this-in-production-min-32-chars"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # Groq API
    groq_api_key: str = ""
    
    # Server
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    environment: str = "development"
    
    # File Storage
    upload_dir: str = "./uploads"
    max_file_size: int = 52428800  # 50MB
    
    # Email
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    sender_email: Optional[str] = None
    sender_password: Optional[str] = None
    
    # CORS
    frontend_url: str = "http://localhost:3000"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
