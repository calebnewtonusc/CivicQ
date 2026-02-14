# CivicQ Authentication System - Complete Guide

## Overview

CivicQ features a **production-ready, bulletproof authentication system** with enterprise-grade security features:

- Email verification with professional email templates
- Secure password reset flow
- Two-Factor Authentication (2FA/MFA) with TOTP
- OAuth 2.0 login (Google, Facebook)
- Redis-based session management
- Token blacklisting
- Rate limiting for brute force protection
- Comprehensive security logging

## Table of Contents

1. [Features](#features)
2. [Setup & Configuration](#setup--configuration)
3. [Email Service Setup](#email-service-setup)
4. [OAuth Provider Setup](#oauth-provider-setup)
5. [API Endpoints](#api-endpoints)
6. [Frontend Integration](#frontend-integration)
7. [Security Best Practices](#security-best-practices)
8. [Testing](#testing)

---

## Features

### 1. Email Verification

- **Automated email verification** on signup
- Professional HTML email templates with branding
- Secure token-based verification (24-hour expiration)
- Resend verification email functionality
- Welcome email after successful verification

**Email Templates:**
- `verification_email.html` - Account verification
- `welcome_email.html` - Post-verification welcome
- `password_reset.html` - Password reset instructions
- `password_changed.html` - Password change confirmation
- `2fa_code.html` - Two-factor authentication codes

### 2. Password Reset

- **Secure password reset flow** with email tokens
- One-hour token expiration for security
- Rate limiting (3 requests/hour per IP)
- No email enumeration (always returns success)
- Automatic session invalidation on password change
- Email notification on successful password change

### 3. Two-Factor Authentication (2FA)

- **TOTP-based 2FA** (compatible with Google Authenticator, Authy, 1Password, etc.)
- QR code generation for easy setup
- 10 single-use backup codes for account recovery
- Backup code regeneration
- Time-window tolerance for clock drift
- Optional 2FA for enhanced security

### 4. OAuth 2.0 Login

- **Google OAuth** integration
- **Facebook OAuth** integration
- Automatic account linking by email
- OAuth-only accounts supported
- Secure OAuth provider management
- Account unlinking with password requirement

### 5. Session Management

- **Redis-based session storage** for scalability
- Token blacklisting for logout
- Multi-device session tracking
- Logout from all devices functionality
- Session expiration management
- Remember me functionality (30 days)

### 6. Rate Limiting

- **Login attempts:** 5 per 15 minutes per email
- **Password reset:** 3 per hour per IP
- **Email verification:** 5 per hour per user
- **2FA verification:** 10 per 15 minutes per user
- Distributed rate limiting with Redis
- Automatic counter reset on success

---

## Setup & Configuration

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Update your `.env` file with the following settings:

```bash
# Email Service (SendGrid - Recommended for production)
SENDGRID_API_KEY=your-sendgrid-api-key-here

# Or use SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@example.com
SMTP_PASSWORD=your-email-password
EMAIL_FROM=noreply@civicq.org

# Frontend/Backend URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# OAuth - Google
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# OAuth - Facebook
FACEBOOK_CLIENT_ID=your-facebook-app-id
FACEBOOK_CLIENT_SECRET=your-facebook-app-secret

# Redis (Required for sessions and rate limiting)
REDIS_URL=redis://localhost:6379/0

# Session Settings
SESSION_EXPIRE_SECONDS=86400  # 24 hours
REMEMBER_ME_EXPIRE_SECONDS=2592000  # 30 days

# JWT Settings
SECRET_KEY=your-secret-key-here-generate-with-openssl-rand-hex-32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440  # 24 hours
```

### 3. Run Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Start Redis

```bash
# Using Docker
docker run -d -p 6379:6379 redis:alpine

# Or using local Redis
redis-server
```

---

## Email Service Setup

### Option 1: SendGrid (Recommended for Production)

1. **Create SendGrid account:** https://sendgrid.com
2. **Generate API key:** Settings → API Keys → Create API Key
3. **Set environment variable:** `SENDGRID_API_KEY=your-api-key`

**Benefits:**
- 100 emails/day free tier
- 99% deliverability rate
- Built-in analytics
- Email template management
- Spam protection

### Option 2: SMTP (Development)

Use any SMTP provider (Gmail, Outlook, etc.):

```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Use App Password for Gmail
EMAIL_FROM=noreply@civicq.org
```

**Gmail App Password Setup:**
1. Enable 2FA on your Google account
2. Go to: https://myaccount.google.com/apppasswords
3. Generate app password for "Mail"
4. Use generated password in `SMTP_PASSWORD`

---

## OAuth Provider Setup

### Google OAuth Setup

1. **Go to Google Cloud Console:** https://console.cloud.google.com
2. **Create a new project** or select existing one
3. **Enable Google+ API:**
   - APIs & Services → Library
   - Search "Google+ API"
   - Click "Enable"
4. **Create OAuth credentials:**
   - APIs & Services → Credentials
   - Create Credentials → OAuth client ID
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/api/v1/auth/oauth/google/callback`
5. **Copy credentials:**
   - Client ID → `GOOGLE_CLIENT_ID`
   - Client Secret → `GOOGLE_CLIENT_SECRET`

### Facebook OAuth Setup

1. **Go to Facebook Developers:** https://developers.facebook.com
2. **Create a new app** or select existing one
3. **Add Facebook Login product**
4. **Configure OAuth settings:**
   - Valid OAuth Redirect URIs: `http://localhost:8000/api/v1/auth/oauth/facebook/callback`
5. **Copy credentials:**
   - App ID → `FACEBOOK_CLIENT_ID`
   - App Secret → `FACEBOOK_CLIENT_SECRET`
6. **Enable required permissions:**
   - email
   - public_profile

---

## API Endpoints

### Authentication

#### POST `/api/auth/signup`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "full_name": "John Doe",
  "city": "Los Angeles"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "voter",
    "verification_status": "pending"
  }
}
```

#### POST `/api/auth/login`
Login with email and password.

**Rate Limit:** 5 attempts per 15 minutes per email

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

#### GET `/api/auth/me`
Get current user information (requires authentication).

---

### Password Reset

#### POST `/api/v1/auth/password/reset/request`
Request password reset email.

**Rate Limit:** 3 requests per hour per IP

**Request:**
```json
{
  "email": "user@example.com"
}
```

#### POST `/api/v1/auth/password/reset/confirm`
Reset password using token.

**Request:**
```json
{
  "token": "secure-reset-token-from-email",
  "new_password": "NewSecurePassword123!"
}
```

#### POST `/api/v1/auth/password/change`
Change password (authenticated users).

**Request:**
```json
{
  "current_password": "OldPassword123!",
  "new_password": "NewSecurePassword123!"
}
```

---

### Email Verification

#### POST `/api/v1/auth/email/verify/request`
Request email verification (requires authentication).

**Rate Limit:** 5 requests per hour

#### POST `/api/v1/auth/email/verify/confirm`
Verify email using token.

**Request:**
```json
{
  "token": "verification-token-from-email"
}
```

---

### Two-Factor Authentication

#### POST `/api/v1/auth/2fa/setup`
Setup 2FA and get QR code (requires authentication).

**Response:**
```json
{
  "secret": "JBSWY3DPEHPK3PXP",
  "qr_code": "data:image/png;base64,iVBORw0KG...",
  "backup_codes": [
    "A1B2-C3D4",
    "E5F6-G7H8",
    ...
  ]
}
```

#### POST `/api/v1/auth/2fa/enable`
Enable 2FA after verifying code.

**Request:**
```json
{
  "code": "123456",
  "secret": "JBSWY3DPEHPK3PXP"
}
```

#### POST `/api/v1/auth/2fa/verify`
Verify 2FA code during login.

**Request:**
```json
{
  "code": "123456"
}
```

#### POST `/api/v1/auth/2fa/disable`
Disable 2FA (requires authentication).

#### POST `/api/v1/auth/2fa/backup-codes/regenerate`
Regenerate backup codes (requires authentication).

---

### OAuth

#### GET `/api/v1/auth/oauth/{provider}/login`
Initiate OAuth login (provider: `google` or `facebook`).

**Example:**
```
GET /api/v1/auth/oauth/google/login
```

#### GET `/api/v1/auth/oauth/{provider}/callback`
OAuth callback endpoint (handled automatically).

#### POST `/api/v1/auth/oauth/unlink`
Unlink OAuth provider from account (requires authentication).

---

### Session Management

#### POST `/api/v1/auth/logout`
Logout current session.

#### POST `/api/v1/auth/logout/all`
Logout from all devices.

---

## Frontend Integration

### Add OAuth Buttons to Login/Register Pages

```tsx
import OAuthButtons from '../components/auth/OAuthButtons';

// In your login/register form
<OAuthButtons />
```

### Add "Forgot Password" Link

```tsx
<Link to="/forgot-password">Forgot your password?</Link>
```

### Add Routes to App.tsx

```tsx
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import TwoFactorSetupPage from './pages/TwoFactorSetupPage';
import TwoFactorVerifyPage from './pages/TwoFactorVerifyPage';
import OAuthCallbackPage from './pages/OAuthCallbackPage';

// Add routes
<Route path="/forgot-password" element={<ForgotPasswordPage />} />
<Route path="/reset-password" element={<ResetPasswordPage />} />
<Route path="/2fa/setup" element={<TwoFactorSetupPage />} />
<Route path="/2fa/verify" element={<TwoFactorVerifyPage />} />
<Route path="/auth/callback" element={<OAuthCallbackPage />} />
```

---

## Security Best Practices

### 1. Token Security
- ✅ JWT tokens expire after 24 hours
- ✅ Refresh tokens for extended sessions
- ✅ Tokens blacklisted on logout
- ✅ All tokens invalidated on password change

### 2. Password Security
- ✅ Minimum 8 characters required
- ✅ Bcrypt hashing with salt
- ✅ Password reset tokens expire in 1 hour
- ✅ No password hints or recovery questions

### 3. Rate Limiting
- ✅ Login attempts limited
- ✅ Password reset requests limited
- ✅ Email verification requests limited
- ✅ 2FA attempts limited

### 4. Email Security
- ✅ No email enumeration
- ✅ Verification links expire after 24 hours
- ✅ Password change notifications sent
- ✅ Professional email templates prevent phishing

### 5. Session Security
- ✅ Redis-based session storage
- ✅ Session expiration enforced
- ✅ Multi-device logout support
- ✅ Token blacklisting on logout

### 6. 2FA Security
- ✅ TOTP standard (RFC 6238)
- ✅ Backup codes hashed before storage
- ✅ Time-window tolerance for clock drift
- ✅ Backup codes single-use only

### 7. OAuth Security
- ✅ State parameter prevents CSRF
- ✅ Secure redirect URI validation
- ✅ Email verification from OAuth providers
- ✅ Account linking by verified email

---

## Testing

### Test Email Service (Development Mode)

When `SENDGRID_API_KEY` is not set, emails are logged to console:

```python
# Check backend logs for email content
[DEV MODE] Email to user@example.com: Verify Your Email
Content: Hi there, Thank you for signing up...
```

### Test 2FA

1. Setup 2FA: `POST /api/v1/auth/2fa/setup`
2. Scan QR code with Google Authenticator
3. Get 6-digit code from app
4. Enable 2FA: `POST /api/v1/auth/2fa/enable` with code
5. Login and verify: `POST /api/v1/auth/2fa/verify`

### Test OAuth

1. Configure OAuth credentials in `.env`
2. Visit: `http://localhost:3000/login`
3. Click "Continue with Google" or "Continue with Facebook"
4. Complete OAuth flow
5. Verify redirect to homepage

### Test Password Reset

1. Request reset: `POST /api/v1/auth/password/reset/request`
2. Check email (or console in dev mode)
3. Click reset link
4. Enter new password
5. Verify login with new password

---

## Production Deployment

### Pre-deployment Checklist

- [ ] Set strong `SECRET_KEY` (use `openssl rand -hex 32`)
- [ ] Configure SendGrid API key
- [ ] Setup OAuth credentials for production URLs
- [ ] Enable Redis with persistence
- [ ] Set appropriate CORS origins
- [ ] Configure rate limiting for production traffic
- [ ] Enable HTTPS for all endpoints
- [ ] Setup monitoring and alerting
- [ ] Configure backup codes storage encryption
- [ ] Review and test all email templates
- [ ] Test 2FA recovery flow
- [ ] Test OAuth flows from production domain

### Environment Variables for Production

```bash
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=<strong-random-key>
SENDGRID_API_KEY=<your-sendgrid-key>
REDIS_URL=<production-redis-url>
FRONTEND_URL=https://civicq.org
BACKEND_URL=https://api.civicq.org
GOOGLE_CLIENT_ID=<production-client-id>
FACEBOOK_CLIENT_ID=<production-app-id>
```

---

## Troubleshooting

### Email not sending

**Check:**
1. SendGrid API key is correct
2. Email service logs for errors
3. Sender email is verified in SendGrid
4. Check spam folder

### OAuth not working

**Check:**
1. Redirect URIs match exactly (including http/https)
2. OAuth credentials are correct
3. Required permissions enabled
4. App is in production mode (Facebook)

### 2FA code invalid

**Check:**
1. Device time is synced (NTP)
2. Code entered within 30-second window
3. Secret matches between app and server
4. Use backup code if device lost

### Rate limit errors

**Check:**
1. Redis is running
2. Rate limit counters in Redis
3. Adjust limits in settings if needed
4. Reset rate limit: `session_service.reset_rate_limit(key)`

---

## Support

For issues or questions:
- Check the logs: `backend/logs/`
- Review API documentation: `/docs` endpoint
- Test with Postman/curl
- Enable debug mode for detailed errors

---

## Summary

CivicQ's authentication system is **production-ready** with:

- ✅ **Email verification** with professional templates
- ✅ **Password reset** with secure token flow
- ✅ **2FA/MFA** with TOTP and backup codes
- ✅ **OAuth login** (Google, Facebook)
- ✅ **Session management** with Redis
- ✅ **Rate limiting** for security
- ✅ **Token blacklisting** on logout
- ✅ **Comprehensive security** logging

All features are fully tested, documented, and ready for deployment!
