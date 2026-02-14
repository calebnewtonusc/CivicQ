"""
Authentication API Routes

Handles user signup, login, verification, and session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import Optional

from app.models.base import get_db
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserLogin,
    Token,
    VerificationStart,
    VerificationComplete,
    UserResponse
)
from app.services.auth_service import AuthService
from app.core.security import get_current_user
from app.core.rate_limit import RateLimiter

router = APIRouter()


@router.post("/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user account

    Creates a new user with the provided credentials and profile information.
    Returns an access token and user profile.

    Args:
        user_data: User registration data (email, password, name, city)
        db: Database session

    Returns:
        Token object with access token and user profile

    Raises:
        HTTPException 400: If email is already registered
    """
    # Create user
    user = AuthService.create_user(db, user_data)

    # Generate access token
    user, access_token = AuthService.authenticate_user(
        db,
        UserLogin(email=user_data.email, password=user_data.password)
    )

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )


@router.post("/login", response_model=Token)
async def login(
    db: Session = Depends(get_db),
    username: Optional[str] = Form(None),
    password: Optional[str] = Form(None),
    login_data: Optional[UserLogin] = None
):
    """
    User login

    Authenticates a user with email and password.
    Accepts both JSON and form-urlencoded data.
    Returns an access token for subsequent requests.

    Rate limit: 5 attempts per 15 minutes per email

    Args:
        db: Database session
        username: Email (form-urlencoded format, username field)
        password: Password (form-urlencoded format)
        login_data: Login credentials (email and password) - JSON format

    Returns:
        Token object with access token and user profile

    Raises:
        HTTPException 401: If credentials are invalid
        HTTPException 403: If account is inactive
        HTTPException 429: If rate limit exceeded
    """
    # Handle both JSON and form-urlencoded formats
    if username and password:
        # Form-urlencoded format (username field contains email)
        credentials = UserLogin(email=username, password=password)
    elif login_data:
        # JSON format
        credentials = login_data
    else:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Either provide JSON body or form data (username, password)"
        )

    # Check login rate limit
    RateLimiter.check_login_attempts(credentials.email)

    try:
        user, access_token = AuthService.authenticate_user(db, credentials)

        # Reset login attempts on successful login
        RateLimiter.reset_login_attempts(credentials.email)

        return Token(
            access_token=access_token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
    except HTTPException:
        # Don't reset on failed login
        raise


@router.post("/verify/start")
async def verify_start(
    verification_data: VerificationStart,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start verification process

    Initiates identity verification for the current user.
    Sends a verification code via the specified method (SMS, email, mail).

    Args:
        verification_data: Verification method and contact information
        current_user: Authenticated user
        db: Database session

    Returns:
        Verification record with ID for completing verification

    Raises:
        HTTPException 400: If user is already verified or invalid method
    """
    verification = AuthService.start_verification(db, current_user, verification_data)

    return {
        "message": "Verification started",
        "verification_id": str(verification.id),
        "method": verification.method.value,
        "expires_at": verification.expires_at.isoformat() if verification.expires_at else None,
        # For testing/development only - remove in production
        "code": verification.metadata.get("code") if verification.metadata else None
    }


@router.post("/verify/complete", response_model=UserResponse)
async def verify_complete(
    verification_data: VerificationComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Complete verification process

    Completes identity verification by validating the verification code.
    Updates user's verification status to verified.

    Args:
        verification_data: Verification code and record ID
        current_user: Authenticated user
        db: Database session

    Returns:
        Updated user profile

    Raises:
        HTTPException 400: If code is invalid or expired
        HTTPException 404: If verification record not found
    """
    user = AuthService.complete_verification(db, current_user, verification_data)

    return UserResponse.model_validate(user)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user info

    Returns the profile information for the currently authenticated user.

    Args:
        current_user: Authenticated user from token

    Returns:
        User profile information
    """
    return UserResponse.model_validate(current_user)
