from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str
    DB_USE_NULL_POOL: bool = True
    DB_POOL_RECYCLE_SECONDS: int = 300
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    RESET_TOKEN_EXPIRE_MINUTES: int = 60
    EMAIL_OTP_EXPIRE_MINUTES: int = 10

    # Email provider mode: auto | sendgrid | smtp | mailtrap
    EMAIL_PROVIDER: str = "auto"

    # SendGrid settings
    SENDGRID_API_KEY: Optional[str] = None

    # SMTP settings (generic)
    SMTP_SERVER: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None

    # Mailtrap SMTP settings
    MAILTRAP_HOST: str = "live.smtp.mailtrap.io"
    MAILTRAP_PORT: int = 587
    MAILTRAP_USER: Optional[str] = None
    MAILTRAP_PASSWORD: Optional[str] = None

    EMAILS_FROM_NAME: str = "Tapafix"
    EMAILS_FROM_EMAIL: Optional[str] = None
    FRONTEND_PASSWORD_RESET_URL: Optional[str] = None

    DEBUG: bool = False
    PROJECT_NAME: str = "Tapafix API"
    API_V1_PREFIX: str = "/api/v1"

    GOOGLE_CLIENT_ID: Optional[str] = None
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    APPLE_CLIENT_ID: Optional[str] = None

    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_SUCCESS_URL: str = "http://localhost:3000/payment/success"
    STRIPE_CANCEL_URL: str = "http://localhost:3000/payment/cancel"


settings = Settings()
