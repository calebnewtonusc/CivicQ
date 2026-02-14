"""
OAuth Service

Handles OAuth authentication with Google, Facebook, and other providers.
"""

from authlib.integrations.starlette_client import OAuth
from typing import Optional, Dict, Any
import logging
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User, UserRole, VerificationStatus
from app.core.security import create_access_token

logger = logging.getLogger(__name__)

# Initialize OAuth
oauth = OAuth()

# Register Google OAuth
if hasattr(settings, 'GOOGLE_CLIENT_ID') and settings.GOOGLE_CLIENT_ID:
    oauth.register(
        name='google',
        client_id=settings.GOOGLE_CLIENT_ID,
        client_secret=settings.GOOGLE_CLIENT_SECRET,
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

# Register Facebook OAuth
if hasattr(settings, 'FACEBOOK_CLIENT_ID') and settings.FACEBOOK_CLIENT_ID:
    oauth.register(
        name='facebook',
        client_id=settings.FACEBOOK_CLIENT_ID,
        client_secret=settings.FACEBOOK_CLIENT_SECRET,
        access_token_url='https://graph.facebook.com/oauth/access_token',
        authorize_url='https://www.facebook.com/dialog/oauth',
        api_base_url='https://graph.facebook.com/',
        client_kwargs={
            'scope': 'email public_profile'
        }
    )


class OAuthService:
    """Service for OAuth authentication"""

    @staticmethod
    def get_oauth_client(provider: str):
        """
        Get OAuth client for provider

        Args:
            provider: OAuth provider name ('google', 'facebook')

        Returns:
            OAuth client or None
        """
        if provider == 'google':
            return oauth.google if hasattr(oauth, 'google') else None
        elif provider == 'facebook':
            return oauth.facebook if hasattr(oauth, 'facebook') else None
        return None

    @staticmethod
    def extract_user_info(provider: str, user_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract user information from OAuth provider response

        Args:
            provider: OAuth provider name
            user_data: User data from OAuth provider

        Returns:
            Dictionary with email, name, and oauth_id
        """
        if provider == 'google':
            return {
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'oauth_id': user_data.get('sub'),
                'picture': user_data.get('picture')
            }
        elif provider == 'facebook':
            return {
                'email': user_data.get('email'),
                'name': user_data.get('name'),
                'oauth_id': user_data.get('id'),
                'picture': user_data.get('picture', {}).get('data', {}).get('url')
            }
        return {}

    @staticmethod
    def find_or_create_oauth_user(
        db: Session,
        provider: str,
        user_info: Dict[str, str],
        city: Optional[str] = None
    ) -> Optional[User]:
        """
        Find existing user by OAuth provider or create new one

        Args:
            db: Database session
            provider: OAuth provider name
            user_info: User information from provider
            city: User's city (for new users)

        Returns:
            User object or None
        """
        email = user_info.get('email')
        oauth_id = user_info.get('oauth_id')
        name = user_info.get('name')

        if not email or not oauth_id:
            logger.error("Missing email or oauth_id from provider")
            return None

        # Check for existing user by OAuth ID and provider
        user = db.query(User).filter(
            User.oauth_provider == provider,
            User.oauth_id == oauth_id
        ).first()

        if user:
            logger.info(f"Found existing OAuth user: {user.id}")
            return user

        # Check for existing user by email
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Link OAuth account to existing user
            if not user.oauth_provider:
                user.oauth_provider = provider
                user.oauth_id = oauth_id
                # Mark email as verified since OAuth provider verified it
                user.email_verified = True
                user.verification_status = VerificationStatus.VERIFIED
                db.commit()
                logger.info(f"Linked OAuth to existing user: {user.id}")
            return user

        # Create new user
        user = User(
            email=email,
            full_name=name,
            hashed_password='',  # No password for OAuth users
            oauth_provider=provider,
            oauth_id=oauth_id,
            email_verified=True,  # OAuth providers verify email
            verification_status=VerificationStatus.VERIFIED,
            role=UserRole.VOTER,
            city_name=city
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        logger.info(f"Created new OAuth user: {user.id}")
        return user

    @staticmethod
    def authenticate_oauth_user(
        db: Session,
        provider: str,
        user_data: Dict[str, Any],
        city: Optional[str] = None
    ) -> tuple[Optional[User], Optional[str]]:
        """
        Authenticate user via OAuth

        Args:
            db: Database session
            provider: OAuth provider name
            user_data: User data from OAuth provider
            city: User's city

        Returns:
            Tuple of (User, access_token) or (None, None)
        """
        # Extract user info
        user_info = OAuthService.extract_user_info(provider, user_data)

        # Find or create user
        user = OAuthService.find_or_create_oauth_user(db, provider, user_info, city)

        if not user:
            return None, None

        # Check if user is active
        if not user.is_active:
            logger.warning(f"Inactive user attempted OAuth login: {user.id}")
            return None, None

        # Update last login
        from datetime import datetime
        user.last_active = datetime.utcnow()
        user.last_login = datetime.utcnow()
        db.commit()

        # Generate access token
        access_token = create_access_token(data={"sub": user.id})

        return user, access_token

    @staticmethod
    def unlink_oauth(user: User, db: Session) -> bool:
        """
        Unlink OAuth provider from user account

        Args:
            user: User object
            db: Database session

        Returns:
            True if unlinked successfully
        """
        # Don't allow unlinking if user has no password (OAuth-only account)
        if not user.hashed_password or user.hashed_password == '':
            logger.warning(f"Cannot unlink OAuth from password-less account: {user.id}")
            return False

        user.oauth_provider = None
        user.oauth_id = None
        db.commit()

        logger.info(f"OAuth unlinked for user: {user.id}")
        return True
