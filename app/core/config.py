import os
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    APP_ENV: str = 'development'
    HOST: str = '0.0.0.0'
    PORT: int = 8000
    DATABASE_URL: str = 'sqlite:///./app.db'

    # LLM Settings
    LLM_PROVIDER: str = 'groq'
    GROQ_API_KEY: str = ''
    GROQ_MODEL: str = 'llama-3.3-70b-versatile'
    
    NVIDIA_API_KEY: str = ''
    NVIDIA_MODEL: str = 'nvidia/nemotron-3.5-lightning-30b-a3b'
    NVIDIA_BASE_URL: str = 'https://integrate.api.nvidia.com/v1'

    # Policy & Confidence Thresholds
    AUTO_RESOLUTION_THRESHOLD: float = 0.90
    HUMAN_REVIEW_THRESHOLD: float = 0.70
    AMOUNT_VARIANCE_THRESHOLD: float = 0.10

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'
        extra = 'ignore'


settings = Settings()
