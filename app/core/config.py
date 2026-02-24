from pydantic_settings import BaseSettings
from pydantic import Field
from pathlib import Path

class Settings(BaseSettings):
    # ENV MODE
    ENV: str = Field("DEV", env="ENV")  # DEV / STAGE / PROD

    # DATABASE
    DATABASE_URL: str = Field(..., env="DATABASE_URL")

    # STORAGE PATHS
    AGREEMENT_STORAGE_PATH: Path = Field("storage/generated_pdfs", env="AGREEMENT_STORAGE_PATH")
    SIGNED_PDF_PATH: Path = Field("storage/signed_pdfs", env="SIGNED_PDF_PATH")

    # ESIGN PROVIDER
    ESIGN_PROVIDER: str = Field(..., env="ESIGN_PROVIDER")
    ESIGN_BASE_URL: str = Field(..., env="ESIGN_BASE_URL")
    ESIGN_API_KEY: str = Field(..., env="ESIGN_API_KEY")
    ESIGN_CLIENT_SECRET: str = Field(..., env="ESIGN_CLIENT_SECRET")
    
    LOAN_SERVICE_BASE_URL: str = Field(..., env="LOAN_SERVICE_BASE_URL")

    # CALLBACK
    CALLBACK_URL: str = Field(..., env="CALLBACK_URL")
    ESIGN_CALLBACK_SECRET: str = Field(..., env="ESIGN_CALLBACK_SECRET")

    class Config:
        env_file = ".env"
        extra = "ignore"   # ignore unknown variables safely

settings = Settings()