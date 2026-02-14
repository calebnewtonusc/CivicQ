"""
Advanced Authentication API Routes

Enhanced authentication with password reset, 2FA, OAuth, and session management.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.base import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    PasswordResetRequest,
    PasswordResetConfirm,
    PasswordChange,
    EmailVerificationRequest,
    EmailVerificationConfirm,
    TwoFactorSetup,
    TwoFactorVerify,
    TwoFactorEnable,
    Token
)
from app.services.auth_service import AuthService
from app.services.two_factor_service import TwoFactorService
from app.services.oauth_service import OAuthService, oauth
from app.services.session_service import session_service
from app.core.security import get_current_user, create_access_token
from app.core.config import settings

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


# Password Reset Endpoints

@router.post("/password/reset/request", status_code=status.HTTP_200_OK)
@limiter.limit("3/hour")
async def request_password_reset(
    request: Request,
    data: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """
    Request password reset

    Send password reset email to user. Always returns success to prevent email enumeration.

    Rate limit: 3 requests per hour per IP

    Args:
        data: Email address
        db: Database session

    Returns:
        Success message
    """
    AuthService.request_password_reset(db, data.email)

    return {
        "message": "If an account exists with this email, a password reset link has been sent."
    }


@router.post("/password/reset/confirm", status_code=status.HTTP_200_OK)
async def confirm_password_reset(
    data: PasswordResetConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm password reset with token

    Reset password using the token from email.

    Args:
        data: Reset token and new password
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If token is invalid or expired
    """
    AuthService.reset_password(db, data.token, data.new_password)

    return {
        "message": "Password has been reset successfully. Please login with your new password."
    }


@router.post("/password/change", status_code=status.HTTP_200_OK)
async def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change password (authenticated users)

    Change password while logged in. Requires current password.

    Args:
        data: Current and new password
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If current password is incorrect
    """
    AuthService.change_password(
        db,
        current_user,
        data.current_password,
        data.new_password
    )

    return {
        "message": "Password changed successfully. All sessions have been logged out."
    }


# Email Verification Endpoints

@router.post("/email/verify/request", status_code=status.HTTP_200_OK)
@limiter.limit("5/hour")
async def request_email_verification(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Request email verification

    Send verification email to user.

    Rate limit: 5 requests per hour

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If email already verified
    """
    AuthService.request_email_verification(db, current_user)

    return {
        "message": "Verification email has been sent. Please check your inbox."
    }


@router.post("/email/verify/confirm", response_model=UserResponse)
async def confirm_email_verification(
    data: EmailVerificationConfirm,
    db: Session = Depends(get_db)
):
    """
    Confirm email verification with token

    Verify email using the token from email.

    Args:
        data: Verification token
        db: Database session

    Returns:
        Updated user profile

    Raises:
        HTTPException 400: If token is invalid or expired
    """
    user = AuthService.verify_email(db, data.token)

    return UserResponse.model_validate(user)


# Two-Factor Authentication Endpoints

@router.post("/2fa/setup", response_model=TwoFactorSetup)
async def setup_two_factor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Setup 2FA for user

    Generate TOTP secret and QR code for authenticator app setup.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        TOTP secret, QR code, and backup codes

    Raises:
        HTTPException 400: If 2FA already enabled
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is already enabled"
        )

    secret, qr_code, backup_codes = TwoFactorService.setup_2fa(current_user, db)

    return TwoFactorSetup(
        secret=secret,
        qr_code=qr_code,
        backup_codes=backup_codes
    )


@router.post("/2fa/enable", status_code=status.HTTP_200_OK)
async def enable_two_factor(
    data: TwoFactorEnable,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Enable 2FA after verifying initial code

    Verify TOTP code and enable 2FA for the user.

    Args:
        data: TOTP code and secret
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If code is invalid or 2FA already enabled
    """
    if current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is already enabled"
        )

    success = TwoFactorService.enable_2fa(current_user, data.code, data.secret, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )

    return {
        "message": "Two-factor authentication has been enabled successfully"
    }


@router.post("/2fa/verify", response_model=Token)
async def verify_two_factor(
    data: TwoFactorVerify,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verify 2FA code during login

    Verify TOTP or backup code and complete login.

    Args:
        data: TOTP or backup code
        current_user: Authenticated user (partial session)
        db: Database session

    Returns:
        Access token and user profile

    Raises:
        HTTPException 401: If code is invalid
    """
    success = TwoFactorService.verify_2fa(current_user, data.code, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid verification code"
        )

    # Generate full access token
    access_token = create_access_token(data={"sub": current_user.id})

    return Token(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(current_user)
    )


@router.post("/2fa/disable", status_code=status.HTTP_200_OK)
async def disable_two_factor(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Disable 2FA for user

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message
    """
    TwoFactorService.disable_2fa(current_user, db)

    return {
        "message": "Two-factor authentication has been disabled"
    }


@router.post("/2fa/backup-codes/regenerate")
async def regenerate_backup_codes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Regenerate backup codes

    Generate new backup codes for 2FA recovery.

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        New backup codes

    Raises:
        HTTPException 400: If 2FA not enabled
    """
    if not current_user.two_factor_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Two-factor authentication is not enabled"
        )

    backup_codes = TwoFactorService.regenerate_backup_codes(current_user, db)

    return {
        "backup_codes": backup_codes,
        "message": "Backup codes have been regenerated. Save these in a secure location."
    }


# OAuth Endpoints

@router.get("/oauth/{provider}/login")
async def oauth_login(provider: str, request: Request):
    """
    Initiate OAuth login

    Redirect to OAuth provider for authentication.

    Args:
        provider: OAuth provider ('google' or 'facebook')
        request: FastAPI request

    Returns:
        Redirect to OAuth provider

    Raises:
        HTTPException 400: If provider not supported
    """
    client = OAuthService.get_oauth_client(provider)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' is not configured"
        )

    redirect_uri = f"{settings.BACKEND_URL}/api/v1/auth/oauth/{provider}/callback"

    return await client.authorize_redirect(request, redirect_uri)


@router.get("/oauth/{provider}/callback")
async def oauth_callback(
    provider: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    OAuth callback endpoint

    Handle OAuth provider callback and authenticate user.

    Args:
        provider: OAuth provider ('google' or 'facebook')
        request: FastAPI request
        db: Database session

    Returns:
        Redirect to frontend with auth token

    Raises:
        HTTPException 400: If authentication fails
    """
    client = OAuthService.get_oauth_client(provider)

    if not client:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth provider '{provider}' is not configured"
        )

    try:
        # Get access token from provider
        token = await client.authorize_access_token(request)

        # Get user info from provider
        if provider == 'google':
            user_data = token.get('userinfo')
        elif provider == 'facebook':
            resp = await client.get('me?fields=id,name,email,picture')
            user_data = resp.json()
        else:
            user_data = {}

        # Authenticate or create user
        user, access_token = OAuthService.authenticate_oauth_user(
            db,
            provider,
            user_data
        )

        if not user or not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="OAuth authentication failed"
            )

        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/callback?token={access_token}"
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"OAuth authentication failed: {str(e)}"
        )


@router.post("/oauth/unlink", status_code=status.HTTP_200_OK)
async def unlink_oauth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Unlink OAuth provider from account

    Args:
        current_user: Authenticated user
        db: Database session

    Returns:
        Success message

    Raises:
        HTTPException 400: If account is OAuth-only (no password)
    """
    success = OAuthService.unlink_oauth(current_user, db)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlink OAuth from account without a password. Please set a password first."
        )

    return {
        "message": "OAuth provider has been unlinked from your account"
    }


# Session Management Endpoints

@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """
    Logout user

    Invalidate current session and blacklist token.

    Args:
        request: FastAPI request
        current_user: Authenticated user

    Returns:
        Success message
    """
    # Get token from header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        session_service.blacklist_token(token)

    return {
        "message": "Logged out successfully"
    }


@router.post("/logout/all", status_code=status.HTTP_200_OK)
async def logout_all(
    current_user: User = Depends(get_current_user)
):
    """
    Logout from all devices

    Invalidate all sessions for the current user.

    Args:
        current_user: Authenticated user

    Returns:
        Success message
    """
    session_service.delete_all_user_sessions(current_user.id)

    return {
        "message": "Logged out from all devices successfully"
    }
