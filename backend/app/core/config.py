"""
CivicQ Configuration

Centralized configuration management using Pydantic settings.
Loads from environment variables and .env file.
"""

from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, validator


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # API Settings
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "CivicQ"

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v: str) -> str:
        if not v or len(v) < 32:
            raise ValueError(
                "SECRET_KEY must be set in environment variables and be at least 32 characters long. "
                "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )
        return v

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    @validator("ALLOWED_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse ALLOWED_ORIGINS from comma-separated string or list"""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        raise ValueError(v)

    @validator("ALLOWED_ORIGINS")
    def validate_cors_origins(cls, v: List[str], values: dict) -> List[str]:
        """Validate CORS origins are not wildcards in production"""
        environment = values.get("ENVIRONMENT", "development")

        if environment == "production":
            if "*" in v or "http://*" in v or "https://*" in v:
                raise ValueError(
                    "ALLOWED_ORIGINS cannot contain wildcards (*) in production. "
                    "Specify exact frontend origins (e.g., https://civicq.com)"
                )

        return v

    # Database
    DATABASE_URL: str = "postgresql://civicq:civicq@localhost:5432/civicq"
    DATABASE_ECHO: bool = False

    # Redis (for caching and rate limiting)
    REDIS_URL: str = "redis://localhost:6379/0"

    # S3 / Object Storage
    S3_BUCKET: Optional[str] = None
    S3_REGION: Optional[str] = None
    S3_ACCESS_KEY: Optional[str] = None
    S3_SECRET_KEY: Optional[str] = None
    S3_ENDPOINT: Optional[str] = None  # For S3-compatible services

    # CDN
    CDN_URL: Optional[str] = None

    # Video Processing
    MAX_VIDEO_DURATION_SECONDS: int = 180  # 3 minutes max
    VIDEO_TIME_LIMIT_COUNCIL: int = 90  # City council candidates
    VIDEO_TIME_LIMIT_MAYOR: int = 120   # Mayor candidates
    VIDEO_TIME_LIMIT_MEASURE: int = 180  # Ballot measures

    # Transcription Service
    TRANSCRIPTION_SERVICE: str = "whisper"  # Options: whisper, deepgram, assemblyai
    OPENAI_API_KEY: Optional[str] = None
    DEEPGRAM_API_KEY: Optional[str] = None
    ASSEMBLYAI_API_KEY: Optional[str] = None

    # AI/LLM Features
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4-5-20250929"
    ENABLE_AI_FEATURES: bool = True

    # Embeddings for Question Clustering
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    SIMILARITY_THRESHOLD: float = 0.85  # For duplicate detection

    # Question Ranking
    TOP_QUESTIONS_COUNT: int = 100
    CLUSTER_MAX_QUESTIONS: int = 5  # Max questions per semantic cluster
    MINORITY_CONCERN_SLOTS: int = 10  # Reserved slots for minority concerns

    # Rate Limiting
    RATE_LIMIT_QUESTIONS_PER_DAY: int = 10
    RATE_LIMIT_VOTES_PER_HOUR: int = 100

    # Verification
    VERIFICATION_METHOD: str = "sms"  # Options: sms, email, id_proofing
    VERIFICATION_CODE_EXPIRE_MINUTES: int = 15

    # SMS Service (for verification)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # Email Service
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "noreply@civicq.org"
    SENDGRID_API_KEY: Optional[str] = None

    # Frontend/Backend URLs
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # OAuth Settings
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    FACEBOOK_CLIENT_ID: Optional[str] = None
    FACEBOOK_CLIENT_SECRET: Optional[str] = None

    # Session Settings
    SESSION_EXPIRE_SECONDS: int = 86400  # 24 hours
    REMEMBER_ME_EXPIRE_SECONDS: int = 2592000  # 30 days

    # Moderation
    AUTO_MODERATE: bool = True
    TOXICITY_THRESHOLD: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"

    # Sentry (Error Tracking)
    SENTRY_DSN: Optional[str] = None
    SENTRY_RELEASE: Optional[str] = None

    # Monitoring
    ENABLE_METRICS: bool = True
    ENABLE_SLOW_QUERY_DETECTION: bool = False  # Enable in staging/production with pg_stat_statements

    # Celery (Task Queue)
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/1"

    # Feature Flags
    ENABLE_VIDEO_RECORDING: bool = True
    ENABLE_REBUTTALS: bool = True
    ENABLE_SOURCE_ATTACHMENTS: bool = True
    ENABLE_VIEWPOINT_CLUSTERING: bool = True

    # External Ballot Data APIs
    GOOGLE_CIVIC_API_KEY: Optional[str] = None
    VOTE_AMERICA_API_KEY: Optional[str] = None
    BALLOTPEDIA_API_KEY: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
