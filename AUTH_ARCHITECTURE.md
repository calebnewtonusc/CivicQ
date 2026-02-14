# CivicQ Authentication Architecture

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │ Login Page   │  │ Register Page│  │ Settings Page│              │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │
│         │                 │                 │                       │
│  ┌──────▼────────────────▼─────────────────▼──────┐                │
│  │         OAuth Buttons Component                │                │
│  │  ┌───────────┐  ┌───────────┐                 │                │
│  │  │  Google   │  │ Facebook  │                 │                │
│  │  └───────────┘  └───────────┘                 │                │
│  └─────────────────────────────────────────────────┘                │
│                                                                      │
└──────────────────────────────┬───────────────────────────────────────┘
                               │
                               │ HTTPS/REST API
                               │
┌──────────────────────────────▼───────────────────────────────────────┐
│                      BACKEND (FastAPI)                                │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐ │
│  │                    API Endpoints Layer                          │ │
│  │                                                                 │ │
│  │  /api/auth/*              /api/v1/auth/*                       │ │
│  │  ├─ signup                ├─ password/reset/*                  │ │
│  │  ├─ login                 ├─ email/verify/*                    │ │
│  │  └─ me                    ├─ 2fa/*                             │ │
│  │                           ├─ oauth/{provider}/*                │ │
│  │                           └─ logout/*                          │ │
│  └──────────────┬────────────────────────────────────────┬─────────┘ │
│                 │                                        │           │
│  ┌──────────────▼────────────┐        ┌────────────────▼─────────┐ │
│  │    Rate Limiting           │        │   Authentication         │ │
│  │    Middleware              │        │   Middleware             │ │
│  │  ┌──────────────────────┐ │        │  ┌────────────────────┐ │ │
│  │  │ - Login: 5/15min     │ │        │  │ - JWT Validation   │ │ │
│  │  │ - Reset: 3/hour      │ │        │  │ - Token Blacklist  │ │ │
│  │  │ - Email: 5/hour      │ │        │  │ - User Context     │ │ │
│  │  │ - 2FA: 10/15min      │ │        │  └────────────────────┘ │ │
│  │  └──────────────────────┘ │        └──────────────────────────┘ │
│  └────────────┬───────────────┘                                     │
│               │                                                     │
│  ┌────────────▼─────────────────────────────────────────────────┐  │
│  │                    Service Layer                             │  │
│  │                                                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │   Auth      │  │    Email     │  │   Session    │       │  │
│  │  │  Service    │  │   Service    │  │   Service    │       │  │
│  │  │             │  │              │  │              │       │  │
│  │  │ - Signup    │  │ - SendGrid   │  │ - Redis      │       │  │
│  │  │ - Login     │  │ - Templates  │  │ - Blacklist  │       │  │
│  │  │ - Password  │  │ - Delivery   │  │ - Sessions   │       │  │
│  │  │ - Verify    │  │              │  │ - Tracking   │       │  │
│  │  └─────────────┘  └──────────────┘  └──────────────┘       │  │
│  │                                                              │  │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │  │
│  │  │  Two-Factor │  │    OAuth     │  │ Rate Limiter │       │  │
│  │  │   Service   │  │   Service    │  │              │       │  │
│  │  │             │  │              │  │              │       │  │
│  │  │ - TOTP      │  │ - Google     │  │ - Check      │       │  │
│  │  │ - QR Code   │  │ - Facebook   │  │ - Increment  │       │  │
│  │  │ - Backup    │  │ - Link       │  │ - Reset      │       │  │
│  │  │   Codes     │  │ - Unlink     │  │              │       │  │
│  │  └─────────────┘  └──────────────┘  └──────────────┘       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                     │
└───────────┬─────────────────────────────────────┬───────────────────┘
            │                                     │
            │                                     │
┌───────────▼─────────────┐         ┌─────────────▼──────────────────┐
│    PostgreSQL            │         │         Redis                  │
│                          │         │                                │
│  ┌────────────────────┐  │         │  ┌──────────────────────────┐ │
│  │ users              │  │         │  │ Sessions                 │ │
│  │ ├─ id              │  │         │  │ ├─ session:{id}          │ │
│  │ ├─ email           │  │         │  │ └─ user:sessions:{id}    │ │
│  │ ├─ hashed_password │  │         │  │                          │ │
│  │ ├─ email_verified  │  │         │  │ Token Blacklist          │ │
│  │ ├─ 2fa_enabled     │  │         │  │ ├─ blacklist:token:{jwt} │ │
│  │ ├─ 2fa_secret      │  │         │  │                          │ │
│  │ ├─ oauth_provider  │  │         │  │ Rate Limiting            │ │
│  │ ├─ oauth_id        │  │         │  │ ├─ rate:login:{email}    │ │
│  │ └─ ...             │  │         │  │ ├─ rate:reset:{ip}       │ │
│  │                    │  │         │  │ └─ rate:2fa:{user}       │ │
│  │ verification_      │  │         │  └──────────────────────────┘ │
│  │ records            │  │         │                                │
│  └────────────────────┘  │         └────────────────────────────────┘
│                          │
└──────────────────────────┘

┌─────────────────────────────────────────────────────────────────────┐
│                    External Services                                 │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  SendGrid    │  │ Google OAuth │  │Facebook OAuth│              │
│  │              │  │              │  │              │              │
│  │ - Email      │  │ - User Info  │  │ - User Info  │              │
│  │   Delivery   │  │ - Token      │  │ - Token      │              │
│  │ - Templates  │  │   Exchange   │  │   Exchange   │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Authentication Flow Diagrams

### 1. Email Verification Flow

```
┌─────────┐                ┌─────────┐                ┌──────────┐
│  User   │                │ Backend │                │ SendGrid │
└────┬────┘                └────┬────┘                └────┬─────┘
     │                          │                          │
     │ 1. POST /auth/signup     │                          │
     ├─────────────────────────>│                          │
     │                          │                          │
     │                          │ 2. Create user           │
     │                          │    Generate token        │
     │                          │                          │
     │                          │ 3. Send email            │
     │                          ├─────────────────────────>│
     │                          │                          │
     │                          │                          │ 4. Deliver
     │<─────────────────────────────────────────────────────┤   email
     │ 5. Click link            │                          │
     │                          │                          │
     │ 6. POST /email/verify/   │                          │
     │    confirm               │                          │
     ├─────────────────────────>│                          │
     │                          │                          │
     │                          │ 7. Verify token          │
     │                          │    Mark verified         │
     │                          │                          │
     │                          │ 8. Send welcome email    │
     │                          ├─────────────────────────>│
     │                          │                          │
     │ 9. Success response      │                          │
     │<─────────────────────────┤                          │
     │                          │                          │
```

### 2. Password Reset Flow

```
┌─────────┐                ┌─────────┐                ┌──────────┐
│  User   │                │ Backend │                │ SendGrid │
└────┬────┘                └────┬────┘                └────┬─────┘
     │                          │                          │
     │ 1. POST /password/       │                          │
     │    reset/request         │                          │
     ├─────────────────────────>│                          │
     │                          │                          │
     │                          │ 2. Generate token        │
     │                          │    Store expiration      │
     │                          │                          │
     │                          │ 3. Send reset email      │
     │                          ├─────────────────────────>│
     │                          │                          │
     │                          │                          │ 4. Deliver
     │<─────────────────────────────────────────────────────┤   email
     │ 5. Click reset link      │                          │
     │                          │                          │
     │ 6. POST /password/       │                          │
     │    reset/confirm         │                          │
     ├─────────────────────────>│                          │
     │                          │                          │
     │                          │ 7. Validate token        │
     │                          │    Check expiration      │
     │                          │    Hash new password     │
     │                          │    Invalidate sessions   │
     │                          │                          │
     │                          │ 8. Send confirmation     │
     │                          ├─────────────────────────>│
     │                          │                          │
     │ 9. Success response      │                          │
     │<─────────────────────────┤                          │
     │                          │                          │
```

### 3. Two-Factor Authentication Setup Flow

```
┌─────────┐                ┌─────────┐
│  User   │                │ Backend │
└────┬────┘                └────┬────┘
     │                          │
     │ 1. POST /2fa/setup       │
     ├─────────────────────────>│
     │                          │
     │                          │ 2. Generate TOTP secret
     │                          │    Create QR code
     │                          │    Generate backup codes
     │                          │
     │ 3. QR code + backup codes│
     │<─────────────────────────┤
     │                          │
     │ 4. Scan QR with          │
     │    authenticator app     │
     │                          │
     │ 5. POST /2fa/enable      │
     │    {code: "123456"}      │
     ├─────────────────────────>│
     │                          │
     │                          │ 6. Verify TOTP code
     │                          │    Enable 2FA
     │                          │
     │ 7. Success + backup codes│
     │<─────────────────────────┤
     │                          │
     │ 8. Save backup codes     │
     │    securely              │
     │                          │
```

### 4. OAuth Login Flow

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌────────────┐
│  User   │    │ Backend │    │ Frontend │    │   Google   │
└────┬────┘    └────┬────┘    └────┬─────┘    └─────┬──────┘
     │              │              │                 │
     │ 1. Click     │              │                 │
     │    "Google"  │              │                 │
     ├─────────────>│              │                 │
     │              │              │                 │
     │              │ 2. Redirect  │                 │
     │              │    to Google │                 │
     │              ├─────────────>│                 │
     │              │              │                 │
     │              │              │ 3. Auth request │
     │              │              ├────────────────>│
     │              │              │                 │
     │              │              │                 │ 4. User
     │              │              │                 │    authorizes
     │              │              │                 │
     │              │              │ 5. Callback     │
     │              │<─────────────┴─────────────────┤
     │              │    with code                   │
     │              │                                │
     │              │ 6. Exchange code for user info │
     │              ├───────────────────────────────>│
     │              │                                │
     │              │ 7. User info                   │
     │              │<───────────────────────────────┤
     │              │                                │
     │              │ 8. Find/create user            │
     │              │    Generate JWT                │
     │              │                                │
     │              │ 9. Redirect with token         │
     │              ├─────────────>│                 │
     │              │              │                 │
     │              │              │ 10. Store token │
     │<─────────────┴──────────────┤                 │
     │ 11. Logged in              │                 │
     │                            │                 │
```

### 5. Session Management & Rate Limiting

```
┌─────────┐    ┌─────────┐    ┌───────┐    ┌──────────┐
│  User   │    │ Backend │    │ Redis │    │PostgreSQL│
└────┬────┘    └────┬────┘    └───┬───┘    └────┬─────┘
     │              │              │             │
     │ 1. Login     │              │             │
     ├─────────────>│              │             │
     │              │              │             │
     │              │ 2. Check     │             │
     │              │    rate limit│             │
     │              ├─────────────>│             │
     │              │              │             │
     │              │ 3. Increment │             │
     │              │<─────────────┤             │
     │              │              │             │
     │              │ 4. Verify    │             │
     │              │    credentials            │
     │              ├──────────────────────────>│
     │              │              │             │
     │              │ 5. User data │             │
     │              │<──────────────────────────┤
     │              │              │             │
     │              │ 6. Generate JWT           │
     │              │              │             │
     │              │ 7. Store     │             │
     │              │    session   │             │
     │              ├─────────────>│             │
     │              │              │             │
     │              │ 8. Reset rate│             │
     │              │    limit     │             │
     │              ├─────────────>│             │
     │              │              │             │
     │ 9. JWT token │              │             │
     │<─────────────┤              │             │
     │              │              │             │
     │ 10. Logout   │              │             │
     ├─────────────>│              │             │
     │              │              │             │
     │              │ 11. Blacklist│             │
     │              │     token    │             │
     │              ├─────────────>│             │
     │              │              │             │
     │              │ 12. Delete   │             │
     │              │     session  │             │
     │              ├─────────────>│             │
     │              │              │             │
     │ 13. Success  │              │             │
     │<─────────────┤              │             │
     │              │              │             │
```

---

## Security Layers

```
┌────────────────────────────────────────────────────────┐
│                   Application Layer                     │
│  ┌──────────────────────────────────────────────────┐  │
│  │         HTTPS/TLS Encryption                     │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Rate Limiting Middleware                 │  │
│  │  - Prevents brute force attacks                 │  │
│  │  - IP-based and email-based limiting            │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         JWT Authentication                       │  │
│  │  - Token validation                              │  │
│  │  - Blacklist checking                            │  │
│  │  - Expiration enforcement                        │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Business Logic Layer                     │  │
│  │  - Password hashing (Bcrypt)                     │  │
│  │  - Token generation (secrets module)             │  │
│  │  - 2FA verification (TOTP)                       │  │
│  │  - OAuth validation                              │  │
│  └──────────────────────────────────────────────────┘  │
│                                                         │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Data Layer Security                      │  │
│  │  - SQL injection prevention (SQLAlchemy ORM)     │  │
│  │  - Parameterized queries                         │  │
│  │  - Encrypted sensitive data                      │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

---

## Technology Stack

```
Frontend:
├── React 18
├── TypeScript
├── React Router
├── Axios
└── Tailwind CSS

Backend:
├── FastAPI
├── SQLAlchemy
├── Pydantic
├── Python-JOSE (JWT)
└── Passlib (Bcrypt)

Authentication:
├── PyOTP (TOTP)
├── Authlib (OAuth)
├── QRCode
└── itsdangerous

Email:
├── SendGrid
├── Jinja2
└── Python email utils

Caching & Sessions:
├── Redis
└── redis-om

Database:
├── PostgreSQL
└── Alembic (migrations)

Security:
├── slowapi (rate limiting)
├── cryptography
└── secrets (token generation)
```

---

## Data Flow Summary

1. **User Registration** → Email Verification → Account Activated
2. **User Login** → JWT Generated → Session Created in Redis
3. **Password Reset** → Email Token → New Password → Sessions Invalidated
4. **2FA Setup** → TOTP Secret → QR Code → App Scan → Verification → Enabled
5. **OAuth Login** → Provider Auth → User Info → Account Link → JWT Generated
6. **Logout** → Token Blacklisted → Session Deleted from Redis

---

## Scalability Considerations

### Horizontal Scaling
- **Stateless API:** All auth state in Redis/PostgreSQL
- **Redis Cluster:** Distributed sessions and rate limiting
- **Load Balancer:** Multiple backend instances
- **CDN:** Email template assets

### Performance
- **Redis Caching:** O(1) session lookups
- **Database Indexing:** Email, tokens, OAuth IDs
- **Connection Pooling:** SQLAlchemy pool
- **Async Operations:** Email sending, token validation

### High Availability
- **Redis Persistence:** RDB + AOF
- **PostgreSQL Replication:** Master-slave setup
- **Health Checks:** Endpoint monitoring
- **Graceful Degradation:** Email failures don't block auth

---

**Architecture Status: ✅ Production Grade**

Designed for security, scalability, and maintainability.
