"""
Startup Environment Validation

Validates required environment variables on application startup.
Fails fast with helpful error messages if configuration is missing or invalid.
"""

import sys
import logging
from typing import List, Tuple, Optional
from app.core.config import settings

logger = logging.getLogger(__name__)


class StartupValidationError(Exception):
    """Raised when startup validation fails"""
    pass


def validate_required_env_vars() -> List[Tuple[str, str]]:
    """
    Validate required environment variables

    Returns:
        List of (variable_name, error_message) tuples for missing/invalid variables
    """
    errors = []

    # Critical Security Settings
    if not settings.SECRET_KEY or settings.SECRET_KEY == "CHANGEME-generate-with-openssl-rand-hex-32":
        errors.append((
            "SECRET_KEY",
            "SECRET_KEY is not set or using default value. Generate with: openssl rand -hex 32"
        ))

    if len(settings.SECRET_KEY) < 32:
        errors.append((
            "SECRET_KEY",
            f"SECRET_KEY is too short ({len(settings.SECRET_KEY)} chars). Must be at least 32 characters."
        ))

    # Database Configuration
    if not settings.DATABASE_URL:
        errors.append((
            "DATABASE_URL",
            "DATABASE_URL is not set. Format: postgresql://user:password@host:port/database"
        ))
    elif not settings.DATABASE_URL.startswith("postgresql://"):
        errors.append((
            "DATABASE_URL",
            "DATABASE_URL must use PostgreSQL (start with postgresql://)"
        ))

    # Redis Configuration
    if not settings.REDIS_URL:
        errors.append((
            "REDIS_URL",
            "REDIS_URL is not set. Format: redis://[password@]host:port/db"
        ))
    elif not settings.REDIS_URL.startswith("redis://"):
        errors.append((
            "REDIS_URL",
            "REDIS_URL must use Redis protocol (start with redis://)"
        ))

    # Application URLs
    if not settings.FRONTEND_URL:
        errors.append((
            "FRONTEND_URL",
            "FRONTEND_URL is not set. Required for OAuth callbacks and CORS."
        ))

    if not settings.BACKEND_URL:
        errors.append((
            "BACKEND_URL",
            "BACKEND_URL is not set. Required for OAuth redirect URIs."
        ))

    # CORS Configuration
    if not settings.ALLOWED_ORIGINS:
        errors.append((
            "ALLOWED_ORIGINS",
            "ALLOWED_ORIGINS is empty. Must specify allowed frontend origins."
        ))

    # Check for wildcard in production
    if settings.ENVIRONMENT == "production":
        if "*" in [origin.strip() for origin in str(settings.ALLOWED_ORIGINS).split(",")]:
            errors.append((
                "ALLOWED_ORIGINS",
                "ALLOWED_ORIGINS cannot contain wildcards (*) in production. Specify exact origins."
            ))

    return errors


def validate_feature_dependencies() -> List[Tuple[str, str]]:
    """
    Validate dependencies for enabled features

    Returns:
        List of (feature_name, error_message) tuples for misconfigured features
    """
    errors = []

    # Video Recording Feature
    if settings.ENABLE_VIDEO_RECORDING:
        if not settings.S3_BUCKET:
            errors.append((
                "S3_BUCKET",
                "ENABLE_VIDEO_RECORDING is true but S3_BUCKET is not set. Video uploads require S3."
            ))

        if not settings.S3_ACCESS_KEY or settings.S3_ACCESS_KEY == "your-access-key":
            errors.append((
                "S3_ACCESS_KEY",
                "ENABLE_VIDEO_RECORDING is true but S3_ACCESS_KEY is not configured."
            ))

        if not settings.S3_SECRET_KEY or settings.S3_SECRET_KEY == "your-secret-key":
            errors.append((
                "S3_SECRET_KEY",
                "ENABLE_VIDEO_RECORDING is true but S3_SECRET_KEY is not configured."
            ))

    # SMS Verification
    if settings.VERIFICATION_METHOD == "sms":
        if not settings.TWILIO_ACCOUNT_SID or settings.TWILIO_ACCOUNT_SID == "your-twilio-account-sid":
            errors.append((
                "TWILIO_ACCOUNT_SID",
                "VERIFICATION_METHOD=sms but TWILIO_ACCOUNT_SID is not configured."
            ))

        if not settings.TWILIO_AUTH_TOKEN or settings.TWILIO_AUTH_TOKEN == "your-twilio-auth-token":
            errors.append((
                "TWILIO_AUTH_TOKEN",
                "VERIFICATION_METHOD=sms but TWILIO_AUTH_TOKEN is not configured."
            ))

        if not settings.TWILIO_PHONE_NUMBER or settings.TWILIO_PHONE_NUMBER == "+1234567890":
            errors.append((
                "TWILIO_PHONE_NUMBER",
                "VERIFICATION_METHOD=sms but TWILIO_PHONE_NUMBER is not configured."
            ))

    # Email Verification
    if settings.VERIFICATION_METHOD == "email" or not settings.SENDGRID_API_KEY:
        if not settings.SMTP_HOST:
            errors.append((
                "SMTP_HOST",
                "Email verification requires SMTP_HOST or SENDGRID_API_KEY to be configured."
            ))

        if not settings.SMTP_USER or settings.SMTP_USER == "your-email@example.com":
            errors.append((
                "SMTP_USER",
                "SMTP email requires SMTP_USER to be configured."
            ))

    # AI Features
    if settings.ENABLE_AI_FEATURES:
        if not settings.ANTHROPIC_API_KEY:
            logger.warning(
                "ENABLE_AI_FEATURES is true but ANTHROPIC_API_KEY is not set. "
                "AI features will not work."
            )

    # Transcription
    if settings.TRANSCRIPTION_SERVICE == "whisper":
        if not settings.OPENAI_API_KEY:
            logger.warning(
                "TRANSCRIPTION_SERVICE=whisper but OPENAI_API_KEY is not set. "
                "Video transcription will fail."
            )
    elif settings.TRANSCRIPTION_SERVICE == "deepgram":
        if not settings.DEEPGRAM_API_KEY:
            logger.warning(
                "TRANSCRIPTION_SERVICE=deepgram but DEEPGRAM_API_KEY is not set. "
                "Video transcription will fail."
            )
    elif settings.TRANSCRIPTION_SERVICE == "assemblyai":
        if not settings.ASSEMBLYAI_API_KEY:
            logger.warning(
                "TRANSCRIPTION_SERVICE=assemblyai but ASSEMBLYAI_API_KEY is not set. "
                "Video transcription will fail."
            )

    # OAuth
    if settings.GOOGLE_CLIENT_ID and not settings.GOOGLE_CLIENT_SECRET:
        errors.append((
            "GOOGLE_CLIENT_SECRET",
            "GOOGLE_CLIENT_ID is set but GOOGLE_CLIENT_SECRET is missing."
        ))

    if settings.FACEBOOK_CLIENT_ID and not settings.FACEBOOK_CLIENT_SECRET:
        errors.append((
            "FACEBOOK_CLIENT_SECRET",
            "FACEBOOK_CLIENT_ID is set but FACEBOOK_CLIENT_SECRET is missing."
        ))

    return errors


def validate_production_settings() -> List[Tuple[str, str]]:
    """
    Validate production-specific security settings

    Returns:
        List of (setting_name, error_message) tuples for insecure production settings
    """
    if settings.ENVIRONMENT != "production":
        return []

    errors = []

    # Debug mode check
    if settings.DEBUG:
        errors.append((
            "DEBUG",
            "DEBUG=true is not allowed in production. Set DEBUG=false."
        ))

    # HTTPS check for production URLs
    if not settings.FRONTEND_URL.startswith("https://"):
        errors.append((
            "FRONTEND_URL",
            f"Production FRONTEND_URL must use HTTPS. Current: {settings.FRONTEND_URL}"
        ))

    if not settings.BACKEND_URL.startswith("https://"):
        errors.append((
            "BACKEND_URL",
            f"Production BACKEND_URL must use HTTPS. Current: {settings.BACKEND_URL}"
        ))

    # Check for localhost in production
    if "localhost" in settings.FRONTEND_URL or "127.0.0.1" in settings.FRONTEND_URL:
        errors.append((
            "FRONTEND_URL",
            "FRONTEND_URL cannot use localhost in production."
        ))

    if "localhost" in settings.BACKEND_URL or "127.0.0.1" in settings.BACKEND_URL:
        errors.append((
            "BACKEND_URL",
            "BACKEND_URL cannot use localhost in production."
        ))

    # Sentry recommendation
    if not settings.SENTRY_DSN:
        logger.warning(
            "SENTRY_DSN is not set in production. "
            "Error tracking is highly recommended for production deployments."
        )

    return errors


def validate_url_consistency() -> List[Tuple[str, str]]:
    """
    Validate URL consistency between settings

    Returns:
        List of (setting_name, error_message) tuples for inconsistent URLs
    """
    errors = []

    # Check if FRONTEND_URL is in ALLOWED_ORIGINS
    if settings.FRONTEND_URL and settings.ALLOWED_ORIGINS:
        allowed_origins_list = [origin.strip() for origin in str(settings.ALLOWED_ORIGINS).split(",")]
        if settings.FRONTEND_URL not in allowed_origins_list:
            errors.append((
                "ALLOWED_ORIGINS",
                f"FRONTEND_URL ({settings.FRONTEND_URL}) must be included in ALLOWED_ORIGINS. "
                f"Current ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}"
            ))

    return errors


def run_startup_checks(fail_on_error: bool = True) -> bool:
    """
    Run all startup validation checks

    Args:
        fail_on_error: If True, raise exception on errors. If False, log warnings.

    Returns:
        True if all checks pass, False otherwise

    Raises:
        StartupValidationError: If validation fails and fail_on_error is True
    """
    logger.info("Running startup environment validation...")

    all_errors = []

    # Run all validation checks
    all_errors.extend(validate_required_env_vars())
    all_errors.extend(validate_feature_dependencies())
    all_errors.extend(validate_production_settings())
    all_errors.extend(validate_url_consistency())

    if not all_errors:
        logger.info("All startup checks passed successfully")
        return True

    # Format error messages
    error_messages = [
        f"  - {var_name}: {message}"
        for var_name, message in all_errors
    ]

    error_output = (
        "\n" + "=" * 80 + "\n"
        "STARTUP VALIDATION FAILED\n"
        "=" * 80 + "\n"
        f"Found {len(all_errors)} configuration error(s):\n\n"
        + "\n".join(error_messages) + "\n\n"
        "Please fix these issues in your .env file before starting the application.\n"
        "See backend/.env.example for configuration examples.\n"
        "=" * 80
    )

    if fail_on_error:
        logger.error(error_output)
        raise StartupValidationError(error_output)
    else:
        logger.warning(error_output)
        return False


def print_startup_info():
    """Print startup configuration information"""
    logger.info("=" * 80)
    logger.info("CivicQ Backend Starting")
    logger.info("=" * 80)
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"Debug Mode: {settings.DEBUG}")
    logger.info(f"Backend URL: {settings.BACKEND_URL}")
    logger.info(f"Frontend URL: {settings.FRONTEND_URL}")
    logger.info(f"Database: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else 'Not configured'}")
    logger.info(f"Redis: {settings.REDIS_URL.split('@')[-1] if '@' in settings.REDIS_URL else settings.REDIS_URL}")
    logger.info(f"Video Recording: {'Enabled' if settings.ENABLE_VIDEO_RECORDING else 'Disabled'}")
    logger.info(f"AI Features: {'Enabled' if settings.ENABLE_AI_FEATURES else 'Disabled'}")
    logger.info(f"Verification Method: {settings.VERIFICATION_METHOD}")
    logger.info("=" * 80)


if __name__ == "__main__":
    # Allow running validation checks standalone
    try:
        run_startup_checks(fail_on_error=True)
        print_startup_info()
        print("\nAll checks passed!")
        sys.exit(0)
    except StartupValidationError:
        print("\nValidation failed. Please fix the errors above.")
        sys.exit(1)
