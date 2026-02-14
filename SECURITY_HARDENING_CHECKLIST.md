# CivicQ Production Security Hardening Checklist

This comprehensive checklist covers all critical security measures required before deploying CivicQ to production. Each item should be verified and checked off before launch.

**Last Updated:** 2026-02-14
**Version:** 1.0.0
**Environment:** Production

---

## 1. Application Security

### Environment Variables Security
- [ ] Generate new `SECRET_KEY` using `openssl rand -hex 32` (never use default)
- [ ] Ensure `SECRET_KEY` is at least 32 bytes (64 hex characters)
- [ ] Store all secrets in environment variables (not hardcoded)
- [ ] Set `DEBUG=false` in production
- [ ] Set `ENVIRONMENT=production` in production
- [ ] Verify `.env` file is in `.gitignore`
- [ ] Remove all `.env.example` sensitive data before committing
- [ ] Use different `SECRET_KEY` values for staging vs production
- [ ] Rotate `REDIS_PASSWORD` from default values
- [ ] Rotate `POSTGRES_PASSWORD` from default values

### Secret Management
- [ ] Use AWS Secrets Manager, HashiCorp Vault, or similar for production secrets
- [ ] Never commit API keys or passwords to version control
- [ ] Implement secret rotation procedures for:
  - [ ] `SECRET_KEY` (quarterly)
  - [ ] Database passwords (quarterly)
  - [ ] Redis passwords (quarterly)
  - [ ] S3 access keys (quarterly)
  - [ ] OAuth client secrets (annually)
  - [ ] API keys (quarterly)
- [ ] Document secret rotation procedures in runbook
- [ ] Set up alerts for expiring secrets
- [ ] Audit secret access logs regularly

### API Key Rotation
- [ ] Rotate `OPENAI_API_KEY` every 90 days
- [ ] Rotate `ANTHROPIC_API_KEY` every 90 days
- [ ] Rotate `SENDGRID_API_KEY` every 90 days
- [ ] Rotate `TWILIO_AUTH_TOKEN` every 90 days
- [ ] Rotate `S3_ACCESS_KEY` and `S3_SECRET_KEY` every 90 days
- [ ] Rotate `GOOGLE_CIVIC_API_KEY` every 90 days
- [ ] Set calendar reminders for all rotation schedules
- [ ] Test API key rotation in staging before production
- [ ] Implement zero-downtime key rotation (support 2 keys temporarily)

### Session Security
- [ ] Set `ACCESS_TOKEN_EXPIRE_MINUTES` to 60 or less for production
- [ ] Set `REFRESH_TOKEN_EXPIRE_DAYS` to 7 or less
- [ ] Configure `SESSION_EXPIRE_SECONDS` to 3600 (1 hour) or less
- [ ] Set `REMEMBER_ME_EXPIRE_SECONDS` to 604800 (7 days) or less
- [ ] Implement session invalidation on logout
- [ ] Invalidate all sessions on password change
- [ ] Store session tokens in Redis with automatic expiration
- [ ] Implement "concurrent session limit" per user
- [ ] Log all session creation and destruction events

### CSRF Protection
- [ ] Enable CSRF protection for all state-changing endpoints
- [ ] Use SameSite cookie attribute (`SameSite=Strict` or `Lax`)
- [ ] Implement double-submit cookie pattern for CSRF tokens
- [ ] Verify CSRF tokens on all POST, PUT, DELETE, PATCH requests
- [ ] Exclude API endpoints with proper authentication from CSRF
- [ ] Add CSRF token to all forms in frontend
- [ ] Rotate CSRF tokens after authentication
- [ ] Set CSRF cookie as `HttpOnly=True` and `Secure=True`

### XSS Prevention
- [ ] Sanitize all user input before rendering in frontend
- [ ] Use React's built-in XSS protection (JSX escaping)
- [ ] Implement Content Security Policy (CSP) headers (see section 5)
- [ ] Validate and sanitize rich text content (questions, answers)
- [ ] Use DOMPurify for sanitizing HTML if rendering user HTML
- [ ] Escape all data in API responses
- [ ] Never use `dangerouslySetInnerHTML` without sanitization
- [ ] Implement output encoding for all user-generated content
- [ ] Use `X-Content-Type-Options: nosniff` header

### SQL Injection Prevention
- [ ] Use SQLAlchemy ORM for all database queries (already implemented)
- [ ] Never concatenate user input into raw SQL queries
- [ ] Use parameterized queries for any raw SQL
- [ ] Enable SQLAlchemy query logging in staging to audit queries
- [ ] Implement least-privilege database user permissions
- [ ] Review all `.filter()`, `.query()`, and `.execute()` calls
- [ ] Use SQLAlchemy's text() with bound parameters for raw queries
- [ ] Disable database error messages in production responses

### Input Validation
- [ ] Validate all input using Pydantic models (FastAPI)
- [ ] Set maximum length constraints on all string fields
- [ ] Validate email addresses using `email-validator`
- [ ] Validate phone numbers (E.164 format)
- [ ] Implement file upload type validation (whitelist: video/mp4, image/jpeg, image/png)
- [ ] Validate file upload size limits (`MAX_VIDEO_DURATION_SECONDS`)
- [ ] Sanitize all search query inputs
- [ ] Validate ZIP codes and addresses
- [ ] Reject special characters in username/display name (or sanitize)
- [ ] Implement rate limiting on validation failures

### Output Encoding
- [ ] Encode all JSON responses properly (FastAPI handles this)
- [ ] Encode HTML entities in any server-rendered content
- [ ] Use proper content-type headers for all responses
- [ ] Encode URLs in email templates
- [ ] Sanitize data before logging (no PII in logs)

### File Upload Security
- [ ] Validate file MIME types against whitelist (mp4, jpg, png, pdf)
- [ ] Verify file signatures (magic bytes) not just extensions
- [ ] Set maximum upload size: 100MB for videos, 5MB for images
- [ ] Scan uploaded files for malware (ClamAV or cloud service)
- [ ] Store uploads in S3 with restricted access
- [ ] Generate random UUID filenames (never use user input)
- [ ] Implement virus scanning before processing videos
- [ ] Set S3 bucket to private (no public list/read)
- [ ] Use signed URLs for temporary access to uploads
- [ ] Implement file upload rate limiting per user

---

## 2. Authentication & Authorization

### Password Policies
- [ ] Enforce minimum password length: 12 characters
- [ ] Require mix of uppercase, lowercase, numbers, special characters
- [ ] Implement password strength meter in frontend
- [ ] Block common passwords (use password blacklist)
- [ ] Hash passwords with bcrypt (already using passlib[bcrypt])
- [ ] Set bcrypt work factor to 12 or higher
- [ ] Implement password history (prevent reuse of last 5 passwords)
- [ ] Force password reset every 180 days for admin accounts
- [ ] Never store passwords in plain text (obviously)
- [ ] Never log passwords (even hashed)

### MFA Enforcement
- [ ] Implement TOTP-based 2FA using `pyotp` (already in requirements)
- [ ] Require MFA for all admin and moderator accounts
- [ ] Encourage MFA for all users (optional but recommended)
- [ ] Provide QR code generation for TOTP setup
- [ ] Implement backup codes (10 single-use codes)
- [ ] Allow MFA recovery via SMS or email
- [ ] Log all MFA setup and removal events
- [ ] Invalidate all sessions when MFA is disabled
- [ ] Support SMS-based 2FA as backup (via Twilio)
- [ ] Consider WebAuthn/FIDO2 for future implementation

### Session Timeout
- [ ] Set idle timeout to 30 minutes for regular users
- [ ] Set idle timeout to 15 minutes for admin users
- [ ] Implement "Remember Me" with longer but limited duration (7 days max)
- [ ] Clear client-side tokens on timeout
- [ ] Show warning before timeout (frontend)
- [ ] Invalidate server-side sessions in Redis on timeout
- [ ] Log session timeout events

### OAuth Security
- [ ] Use HTTPS for all OAuth redirect URIs
- [ ] Implement state parameter for CSRF protection in OAuth flow
- [ ] Validate OAuth state parameter on callback
- [ ] Set `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` securely
- [ ] Set `FACEBOOK_CLIENT_ID` and `FACEBOOK_CLIENT_SECRET` securely
- [ ] Whitelist OAuth redirect URIs in provider consoles
- [ ] Use PKCE (Proof Key for Code Exchange) for OAuth flows
- [ ] Validate OAuth tokens before accepting user data
- [ ] Implement OAuth token refresh logic
- [ ] Revoke OAuth tokens on user logout

### JWT Token Security
- [ ] Use HS256 algorithm for JWT signing (already configured)
- [ ] Never expose `SECRET_KEY` in client-side code
- [ ] Set short expiration times (60 minutes max)
- [ ] Implement refresh token rotation
- [ ] Store JWTs in httpOnly cookies (not localStorage)
- [ ] Implement JWT blacklist/revocation in Redis
- [ ] Include `iat` (issued at) and `exp` (expiry) in all tokens
- [ ] Validate token signature on every request
- [ ] Include user role in JWT payload for fast authorization
- [ ] Consider using RS256 (asymmetric) for future scalability

### Role-Based Access Control (RBAC)
- [ ] Define roles: `user`, `verified_user`, `candidate`, `city_staff`, `moderator`, `admin`, `superuser`
- [ ] Implement role checks in all protected endpoints
- [ ] Use `get_current_admin()` for admin-only endpoints
- [ ] Use `get_current_verified_user()` for verified-only actions
- [ ] Implement resource-level permissions (e.g., candidates can only edit own profile)
- [ ] Log all permission denials
- [ ] Audit role assignments regularly
- [ ] Implement "principle of least privilege"
- [ ] Restrict role elevation (only admins can promote users)
- [ ] Implement role-based UI hiding in frontend

### Admin Access Restrictions
- [ ] Require MFA for all admin accounts (mandatory)
- [ ] Implement IP whitelist for admin access (optional but recommended)
- [ ] Log all admin actions with timestamps and IP addresses
- [ ] Implement admin session timeout (15 minutes idle)
- [ ] Require re-authentication for critical admin actions
- [ ] Limit number of admin accounts (follow least privilege)
- [ ] Implement "admin impersonation" audit trail
- [ ] Disable API documentation in production (`docs_url=None`)
- [ ] Restrict admin panel access to HTTPS only
- [ ] Implement admin activity dashboard for monitoring

---

## 3. Infrastructure Security

### Firewall Rules
- [ ] Configure VPC/Security Groups to allow only necessary ports
- [ ] Allow inbound HTTPS (443) from anywhere
- [ ] Allow inbound HTTP (80) only for SSL redirect
- [ ] Allow SSH (22) only from trusted IPs (bastion host)
- [ ] Block all other inbound ports by default
- [ ] Allow outbound HTTPS (443) for API calls
- [ ] Allow outbound SMTP (587) for email
- [ ] Block all other outbound ports by default
- [ ] Implement egress filtering (whitelist allowed external IPs)
- [ ] Use network ACLs in addition to security groups

### Network Security Groups
- [ ] Create separate security groups for: web tier, app tier, database tier
- [ ] Database security group: allow 5432 only from app tier
- [ ] Redis security group: allow 6379 only from app tier
- [ ] App tier: allow 8000 only from web tier
- [ ] Web tier: allow 80/443 from anywhere
- [ ] Implement principle of least privilege for all security groups
- [ ] Document all security group rules
- [ ] Review security groups quarterly
- [ ] Enable VPC Flow Logs for traffic analysis

### VPC Configuration
- [ ] Deploy application in private VPC
- [ ] Use public subnets only for load balancer/reverse proxy
- [ ] Deploy database and Redis in private subnets
- [ ] Configure NAT Gateway for outbound internet access from private subnets
- [ ] Enable VPC Flow Logs
- [ ] Implement network segmentation (separate subnets for web/app/db)
- [ ] Use VPC endpoints for AWS services (S3, SES, etc.)
- [ ] Enable DNS resolution and hostnames in VPC
- [ ] Configure route tables correctly (no public routes to private subnets)

### Database Security
- [ ] Use managed PostgreSQL (AWS RDS, GCP Cloud SQL, etc.)
- [ ] Enable SSL/TLS for database connections
- [ ] Disable public database access (no public IP)
- [ ] Use strong database password (32+ characters, random)
- [ ] Enable automatic backups (daily at minimum)
- [ ] Set backup retention to 30 days
- [ ] Enable point-in-time recovery
- [ ] Encrypt database at rest (use managed encryption)
- [ ] Enable database audit logging
- [ ] Implement least-privilege database users:
  - [ ] App user: SELECT, INSERT, UPDATE, DELETE only
  - [ ] Migration user: DDL permissions
  - [ ] Read-only user: SELECT only for analytics
- [ ] Disable `postgres` superuser for application
- [ ] Configure connection pooling (SQLAlchemy pool_size)
- [ ] Enable slow query logging
- [ ] Set up database monitoring and alerting
- [ ] Test database restore procedures quarterly

### Redis Security
- [ ] Use managed Redis (AWS ElastiCache, GCP Memorystore, etc.)
- [ ] Set strong `REDIS_PASSWORD` (32+ characters)
- [ ] Disable public Redis access (private subnet only)
- [ ] Enable Redis AUTH (password authentication)
- [ ] Enable Redis encryption in transit (TLS)
- [ ] Enable Redis encryption at rest
- [ ] Configure Redis maxmemory policy: `allkeys-lru`
- [ ] Set appropriate maxmemory limit based on instance size
- [ ] Enable Redis persistence (AOF or RDB)
- [ ] Disable dangerous Redis commands: FLUSHALL, FLUSHDB, CONFIG, EVAL
- [ ] Enable Redis slow log
- [ ] Monitor Redis memory usage
- [ ] Set up Redis failover/replication for high availability

### S3 Bucket Policies
- [ ] Create dedicated S3 bucket for CivicQ media (`civicq-media-prod`)
- [ ] Block all public access to S3 bucket
- [ ] Enable S3 bucket versioning
- [ ] Enable S3 server-side encryption (SSE-S3 or SSE-KMS)
- [ ] Configure S3 bucket policy to deny non-HTTPS requests
- [ ] Enable S3 access logging to separate audit bucket
- [ ] Configure S3 lifecycle policies for old data
- [ ] Use IAM roles for S3 access (not access keys if possible)
- [ ] Implement S3 bucket policy for least privilege access
- [ ] Enable S3 object lock for compliance (if needed)
- [ ] Set CORS policy on S3 bucket (whitelist frontend domain only)
- [ ] Enable MFA delete for production bucket
- [ ] Review S3 access logs monthly
- [ ] Implement S3 event notifications for sensitive operations

**Example S3 Bucket Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyInsecureTransport",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::civicq-media-prod",
        "arn:aws:s3:::civicq-media-prod/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

### CDN Security
- [ ] Use CloudFront or Cloudflare CDN for static assets
- [ ] Enable HTTPS-only on CDN
- [ ] Configure CDN to forward Host header
- [ ] Implement CDN access logs
- [ ] Enable CDN DDoS protection
- [ ] Configure CDN to cache only public content
- [ ] Set proper Cache-Control headers
- [ ] Implement signed URLs for private content
- [ ] Configure CDN to strip sensitive headers
- [ ] Enable CDN WAF (Web Application Firewall)
- [ ] Set up CDN geo-restrictions if needed
- [ ] Configure CDN rate limiting

---

## 4. SSL/TLS

### Certificate Installation
- [ ] Obtain SSL certificate from Let's Encrypt, AWS ACM, or commercial CA
- [ ] Install certificate on load balancer or reverse proxy (Nginx)
- [ ] Configure certificate for primary domain (e.g., `civicq.com`)
- [ ] Configure certificate for www subdomain (`www.civicq.com`)
- [ ] Configure certificate for API subdomain (`api.civicq.com`)
- [ ] Configure certificate for app subdomain (`app.civicq.com`)
- [ ] Use wildcard certificate (*.civicq.com) or SAN certificate
- [ ] Store private key securely (encrypted, restricted permissions)
- [ ] Never commit SSL private keys to version control
- [ ] Document certificate installation procedure

### HTTPS Enforcement
- [ ] Redirect all HTTP (port 80) traffic to HTTPS (port 443)
- [ ] Configure Nginx to return 301 permanent redirect for HTTP
- [ ] Set `Secure` flag on all cookies
- [ ] Update all `FRONTEND_URL` and `BACKEND_URL` to use https://
- [ ] Update OAuth redirect URIs to use https://
- [ ] Disable plain HTTP on backend (HTTPS only)
- [ ] Configure load balancer for SSL termination
- [ ] Test HTTPS enforcement with curl/browser

**Example Nginx HTTP to HTTPS redirect:**
```nginx
server {
    listen 80;
    server_name civicq.com www.civicq.com;
    return 301 https://$host$request_uri;
}
```

### HSTS Headers
- [ ] Enable HTTP Strict Transport Security (HSTS)
- [ ] Set HSTS max-age to 31536000 (1 year)
- [ ] Include `includeSubDomains` directive
- [ ] Include `preload` directive for HSTS preload list
- [ ] Submit domain to HSTS preload list (hstspreload.org)
- [ ] Test HSTS headers in browser dev tools
- [ ] Monitor HSTS compliance

**Example HSTS header:**
```nginx
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
```

### Certificate Renewal
- [ ] Set up automatic certificate renewal with Certbot or ACM
- [ ] Configure Certbot renewal cron job (runs twice daily)
- [ ] Test certificate renewal process in staging
- [ ] Set up alerts for certificate expiration (30 days before)
- [ ] Document manual renewal procedure (for disaster recovery)
- [ ] Monitor certificate validity daily
- [ ] Keep backup of previous certificates

**Certbot auto-renewal setup:**
```bash
# Add to docker-compose.production.yml (already included)
certbot renew --dry-run  # Test renewal
```

### TLS Version Enforcement
- [ ] Disable SSLv2 and SSLv3 (vulnerable)
- [ ] Disable TLS 1.0 and TLS 1.1 (deprecated)
- [ ] Enable TLS 1.2 and TLS 1.3 only
- [ ] Configure strong cipher suites (forward secrecy)
- [ ] Use Mozilla SSL Configuration Generator for best practices
- [ ] Test TLS configuration with SSL Labs (ssllabs.com/ssltest)
- [ ] Aim for A+ rating on SSL Labs

**Example Nginx TLS configuration:**
```nginx
ssl_protocols TLSv1.2 TLSv1.3;
ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
ssl_prefer_server_ciphers off;
```

---

## 5. Security Headers

### Content-Security-Policy
- [ ] Implement strict Content Security Policy (CSP)
- [ ] Set `default-src 'self'`
- [ ] Allow scripts only from trusted CDNs (React, etc.)
- [ ] Set `img-src 'self' data: https:`
- [ ] Set `style-src 'self' 'unsafe-inline'` (minimize inline styles)
- [ ] Set `font-src 'self' https://fonts.gstatic.com`
- [ ] Set `connect-src 'self' https://api.civicq.com`
- [ ] Set `frame-ancestors 'none'` (prevent clickjacking)
- [ ] Report CSP violations to monitoring endpoint
- [ ] Test CSP in report-only mode first
- [ ] Gradually tighten CSP policy

**Example CSP header:**
```nginx
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://api.civicq.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
```

### X-Frame-Options
- [ ] Set `X-Frame-Options: DENY` to prevent clickjacking
- [ ] Alternative: use CSP `frame-ancestors 'none'`
- [ ] Test that application doesn't load in iframes
- [ ] Verify header in browser dev tools

**Example header:**
```nginx
add_header X-Frame-Options "DENY" always;
```

### X-Content-Type-Options
- [ ] Set `X-Content-Type-Options: nosniff`
- [ ] Prevents MIME type sniffing attacks
- [ ] Verify header in all responses

**Example header:**
```nginx
add_header X-Content-Type-Options "nosniff" always;
```

### Referrer-Policy
- [ ] Set `Referrer-Policy: strict-origin-when-cross-origin`
- [ ] Prevents leaking sensitive URLs to third parties
- [ ] Verify header in browser dev tools

**Example header:**
```nginx
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
```

### Permissions-Policy
- [ ] Set `Permissions-Policy` to restrict browser features
- [ ] Disable geolocation if not needed: `geolocation=()`
- [ ] Disable microphone: `microphone=()`
- [ ] Disable camera: `camera=()`
- [ ] Allow only necessary features

**Example header:**
```nginx
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### Complete Security Headers Configuration
**Add to Nginx configuration:**
```nginx
# Security Headers
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
add_header X-Frame-Options "DENY" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self' https://api.civicq.com; frame-ancestors 'none'; base-uri 'self'; form-action 'self';" always;
```

---

## 6. Rate Limiting

### API Rate Limits
- [ ] Implement global API rate limit: 100 requests/minute per IP
- [ ] Use `slowapi` for rate limiting (already installed)
- [ ] Configure Redis for rate limit storage
- [ ] Implement endpoint-specific rate limits:
  - [ ] `/api/auth/login`: 5 attempts/15 minutes per IP
  - [ ] `/api/auth/register`: 3 attempts/hour per IP
  - [ ] `/api/questions`: 10 submissions/day per user (already configured)
  - [ ] `/api/votes`: 100 votes/hour per user (already configured)
  - [ ] `/api/videos/upload`: 5 uploads/hour per user
  - [ ] `/api/admin/*`: 1000 requests/hour per admin
- [ ] Return 429 Too Many Requests with Retry-After header
- [ ] Log rate limit violations
- [ ] Implement IP-based and user-based rate limiting
- [ ] Consider implementing progressive rate limiting (increasing delays)

**Example rate limiting:**
```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/auth/login")
@limiter.limit("5/15minutes")
async def login(request: Request):
    # Login logic
    pass
```

### Login Attempt Limits
- [ ] Limit login attempts: 5 failed attempts per 15 minutes per IP
- [ ] Limit login attempts: 10 failed attempts per hour per username
- [ ] Implement exponential backoff after failed attempts
- [ ] Lock account after 10 consecutive failed attempts
- [ ] Require email verification to unlock account
- [ ] Send email notification on account lock
- [ ] Log all failed login attempts with IP and timestamp
- [ ] Implement CAPTCHA after 3 failed attempts
- [ ] Monitor for brute force attack patterns
- [ ] Consider implementing device fingerprinting

### Email Sending Limits
- [ ] Limit verification emails: 3 per hour per user
- [ ] Limit password reset emails: 3 per hour per user
- [ ] Limit notification emails: 50 per day per user
- [ ] Implement global email rate limit per domain
- [ ] Monitor email bounce rates
- [ ] Implement email sending delays (prevent spam)
- [ ] Use email queue (Celery) for rate-limited sending
- [ ] Log all email sending attempts

### Upload Limits
- [ ] Limit video uploads: 5 per hour per user
- [ ] Limit video uploads: 20 per day per user
- [ ] Limit image uploads: 10 per hour per user
- [ ] Enforce maximum file size: 100MB for videos, 5MB for images
- [ ] Implement total storage quota per user (e.g., 500MB)
- [ ] Monitor S3 storage usage
- [ ] Implement upload bandwidth throttling
- [ ] Reject duplicate file uploads (hash-based deduplication)

---

## 7. Monitoring & Logging

### Security Event Logging
- [ ] Enable application logging (already using Python logging)
- [ ] Set `LOG_LEVEL=INFO` for production
- [ ] Log all authentication events (login, logout, failed attempts)
- [ ] Log all authorization failures (permission denials)
- [ ] Log all admin actions (user role changes, data modifications)
- [ ] Log all password changes and resets
- [ ] Log all MFA setup/removal events
- [ ] Log all session creation/destruction
- [ ] Log all rate limit violations
- [ ] Never log sensitive data (passwords, tokens, PII)
- [ ] Use structured logging (JSON format)
- [ ] Include correlation IDs in all logs (request tracking)
- [ ] Implement log rotation (daily, keep 90 days)
- [ ] Send critical security events to monitoring system (Sentry)

**Example security event logging:**
```python
logger.info(
    "User login successful",
    extra={
        "event": "auth.login.success",
        "user_id": user.id,
        "ip_address": request.client.host,
        "user_agent": request.headers.get("user-agent"),
    }
)
```

### Failed Login Tracking
- [ ] Log all failed login attempts with timestamp, IP, username
- [ ] Store failed attempts in Redis with expiration
- [ ] Implement anomaly detection for failed login patterns
- [ ] Alert on suspicious patterns (many IPs trying same username)
- [ ] Alert on account enumeration attempts
- [ ] Send email notification after 3 failed attempts
- [ ] Lock account after 10 failed attempts
- [ ] Create dashboard for failed login monitoring
- [ ] Review failed login reports weekly

### Audit Trail
- [ ] Implement comprehensive audit trail for all critical actions
- [ ] Log database record creation, updates, and deletions
- [ ] Track who made changes and when
- [ ] Store audit logs in separate database table
- [ ] Include before/after values for updates
- [ ] Implement audit log for:
  - [ ] User account changes
  - [ ] Role assignments
  - [ ] Question submissions and edits
  - [ ] Vote casting
  - [ ] Content moderation actions
  - [ ] Admin actions
  - [ ] Configuration changes
- [ ] Make audit logs immutable (append-only)
- [ ] Retain audit logs for 7 years (compliance)
- [ ] Implement audit log search and filtering
- [ ] Export audit logs for compliance audits

### Intrusion Detection
- [ ] Implement anomaly detection for:
  - [ ] Unusual login patterns (location, time, device)
  - [ ] Rapid succession of failed logins
  - [ ] Unusual API usage patterns
  - [ ] Large data exports
  - [ ] Privilege escalation attempts
- [ ] Set up alerts for:
  - [ ] SQL injection attempts
  - [ ] XSS attempts
  - [ ] Path traversal attempts
  - [ ] CSRF token violations
  - [ ] Unusual admin activity
- [ ] Use WAF (Web Application Firewall) for attack detection
- [ ] Monitor application logs for attack patterns
- [ ] Implement IP blacklist for detected attackers
- [ ] Integrate with SIEM system (Splunk, ELK, etc.)

### Log Retention
- [ ] Retain application logs for 90 days minimum
- [ ] Retain audit logs for 7 years (compliance)
- [ ] Retain access logs (Nginx) for 90 days
- [ ] Retain database logs for 30 days
- [ ] Compress old logs (gzip) to save storage
- [ ] Archive logs to S3 Glacier for long-term retention
- [ ] Implement automated log cleanup
- [ ] Document log retention policy
- [ ] Test log restoration procedures

**Log Retention Schedule:**
- Application logs: 90 days (hot), 1 year (cold/S3)
- Audit logs: 7 years (compliance)
- Access logs: 90 days
- Security events: 2 years
- Error logs: 1 year

---

## 8. Compliance

### GDPR Compliance Checklist
- [ ] Implement "right to access" - users can download their data
- [ ] Implement "right to erasure" - users can delete their accounts
- [ ] Implement "right to rectification" - users can edit their data
- [ ] Implement "right to data portability" - export data in JSON/CSV
- [ ] Obtain explicit consent for data collection (checkbox on signup)
- [ ] Provide clear privacy policy (link in footer)
- [ ] Provide clear cookie policy
- [ ] Implement cookie consent banner
- [ ] Allow users to opt-out of non-essential cookies
- [ ] Document data processing activities
- [ ] Implement data minimization (collect only necessary data)
- [ ] Designate Data Protection Officer (DPO) if required
- [ ] Implement data breach notification procedure (72 hours)
- [ ] Conduct Privacy Impact Assessment (PIA)
- [ ] Sign Data Processing Agreements (DPA) with vendors

**GDPR Data Subject Rights:**
- [ ] Right to access (data export)
- [ ] Right to erasure (account deletion)
- [ ] Right to rectification (profile editing)
- [ ] Right to data portability (JSON/CSV export)
- [ ] Right to object (opt-out of processing)
- [ ] Right to restriction of processing
- [ ] Rights related to automated decision making

### CCPA Compliance Checklist
- [ ] Provide "Do Not Sell My Personal Information" option
- [ ] Implement mechanisms for users to opt-out of data sales
- [ ] Provide clear notice of data collection at/before collection
- [ ] Allow users to request disclosure of collected data
- [ ] Allow users to request deletion of personal information
- [ ] Provide non-discriminatory service (same price/service for opt-outs)
- [ ] Respond to CCPA requests within 45 days
- [ ] Verify identity before fulfilling CCPA requests
- [ ] Update privacy policy with CCPA disclosures
- [ ] Train staff on CCPA compliance

### Data Encryption at Rest
- [ ] Enable database encryption at rest (RDS encryption)
- [ ] Enable Redis encryption at rest
- [ ] Enable S3 bucket encryption (SSE-S3 or SSE-KMS)
- [ ] Encrypt backup files
- [ ] Encrypt logs containing sensitive data
- [ ] Use AWS KMS or similar for key management
- [ ] Rotate encryption keys annually
- [ ] Document encryption methods used

**Encryption Checklist:**
- [ ] PostgreSQL: Encrypted at rest (RDS/Cloud SQL)
- [ ] Redis: Encrypted at rest (ElastiCache/Memorystore)
- [ ] S3: Encrypted at rest (SSE-S3)
- [ ] Backups: Encrypted (automatic with RDS)
- [ ] Logs: Encrypted (CloudWatch/S3)

### Data Encryption in Transit
- [ ] Use HTTPS/TLS for all client-server communication
- [ ] Use TLS for database connections
- [ ] Use TLS for Redis connections
- [ ] Use HTTPS for S3 uploads/downloads
- [ ] Use TLS for email (SMTP over TLS)
- [ ] Use TLS for API calls to third parties
- [ ] Disable insecure protocols (SSLv3, TLS 1.0, TLS 1.1)
- [ ] Verify TLS certificates in code

### Data Retention Policies
- [ ] Define data retention periods for each data type
- [ ] Implement automated deletion of expired data
- [ ] Retain user accounts for 30 days after deletion request (soft delete)
- [ ] Permanently delete data after 30-day grace period
- [ ] Retain audit logs for 7 years (compliance)
- [ ] Delete inactive accounts after 2 years (with notification)
- [ ] Archive old elections after 4 years (move to cold storage)
- [ ] Document retention policy in privacy policy
- [ ] Review and update retention policy annually

**Data Retention Schedule:**
- User accounts (active): Indefinite
- User accounts (deleted): 30 days soft delete, then permanent
- Inactive accounts: 2 years, then delete (with email warning)
- Questions/votes: Tied to user account
- Audit logs: 7 years
- Access logs: 90 days
- Session data: Auto-expire per session timeout
- Video uploads: Indefinite (tied to contest)
- Expired elections: 4 years, then archive

### Right to Erasure (GDPR Article 17)
- [ ] Implement "Delete My Account" button in user settings
- [ ] Delete or anonymize all personal data on account deletion:
  - [ ] User profile (name, email, phone)
  - [ ] Questions submitted (anonymize or delete)
  - [ ] Votes cast (anonymize voter ID)
  - [ ] Comments and interactions
  - [ ] Video uploads (if personal)
  - [ ] Session data
  - [ ] Audit logs (anonymize user ID, keep for compliance)
- [ ] Provide confirmation email after deletion
- [ ] Allow 30-day grace period for account recovery
- [ ] Permanently purge data after grace period
- [ ] Update third-party systems (SendGrid, Twilio) to remove data
- [ ] Document erasure procedure

### Data Breach Procedures
- [ ] Designate incident response team
- [ ] Document data breach response plan
- [ ] Implement breach detection monitoring
- [ ] Notify affected users within 72 hours (GDPR requirement)
- [ ] Notify regulatory authorities within 72 hours
- [ ] Document all breaches in incident log
- [ ] Conduct post-mortem after each breach
- [ ] Update security measures based on lessons learned
- [ ] Maintain cyber insurance policy
- [ ] Conduct annual breach response drills

**Data Breach Response Plan:**
1. **Detection** - Identify and confirm breach (monitoring, alerts)
2. **Containment** - Isolate affected systems, stop data loss
3. **Assessment** - Determine scope, affected data, number of users
4. **Notification** - Notify users and authorities within 72 hours
5. **Remediation** - Fix vulnerability, restore services
6. **Post-Mortem** - Document lessons learned, update procedures
7. **Monitoring** - Enhanced monitoring for 90 days post-breach

---

## 9. Regular Maintenance

### Dependency Updates
- [ ] Review dependencies for security updates weekly
- [ ] Update dependencies in staging environment first
- [ ] Run automated dependency scanning (Dependabot, Snyk)
- [ ] Subscribe to security advisories for key dependencies:
  - [ ] FastAPI security advisories
  - [ ] React security advisories
  - [ ] SQLAlchemy security advisories
  - [ ] Redis security updates
  - [ ] PostgreSQL security updates
- [ ] Review `npm audit` output weekly
- [ ] Review `pip check` output weekly
- [ ] Test application after dependency updates
- [ ] Update dependencies in production within 48 hours of security patch

**Commands for dependency checking:**
```bash
# Frontend
npm audit
npm audit fix

# Backend
pip list --outdated
pip-audit  # Install with: pip install pip-audit
```

### Security Patches
- [ ] Apply OS security patches monthly (Ubuntu/Debian)
- [ ] Apply Docker base image updates monthly
- [ ] Apply database security patches within 7 days
- [ ] Apply web server (Nginx) security patches within 7 days
- [ ] Enable automatic security updates (unattended-upgrades)
- [ ] Test patches in staging before production
- [ ] Schedule maintenance windows for critical patches
- [ ] Document patch management procedure

**Enable automatic security updates:**
```bash
apt-get install unattended-upgrades
dpkg-reconfigure -plow unattended-upgrades
```

### Vulnerability Scanning
- [ ] Run automated vulnerability scans weekly (OWASP ZAP, Nessus)
- [ ] Scan Docker images for vulnerabilities (Trivy, Clair)
- [ ] Scan dependencies for known CVEs (Snyk, Dependabot)
- [ ] Review scan results within 24 hours
- [ ] Prioritize critical/high vulnerabilities for immediate remediation
- [ ] Fix medium vulnerabilities within 30 days
- [ ] Document all vulnerability findings and remediation
- [ ] Conduct manual code review for critical components quarterly

**Tools for vulnerability scanning:**
- Frontend: `npm audit`, Snyk
- Backend: `pip-audit`, Bandit (Python security linter)
- Infrastructure: Nessus, OpenVAS
- Containers: Trivy, Clair
- Web app: OWASP ZAP, Burp Suite

**Run Bandit for Python security issues:**
```bash
pip install bandit
bandit -r app/ -f json -o security-report.json
```

### Penetration Testing
- [ ] Conduct external penetration test annually (hire third-party firm)
- [ ] Conduct internal penetration test semi-annually
- [ ] Test for OWASP Top 10 vulnerabilities
- [ ] Test authentication and authorization mechanisms
- [ ] Test API security (fuzzing, injection attacks)
- [ ] Test infrastructure security (network, firewall)
- [ ] Document all findings in penetration test report
- [ ] Remediate critical findings within 7 days
- [ ] Remediate high findings within 30 days
- [ ] Retest after remediation
- [ ] Obtain executive sign-off on pentest results

**Penetration Testing Scope:**
- Web application (frontend + API)
- Authentication/authorization
- File upload functionality
- Video processing pipeline
- Admin panel
- Database security
- API endpoints
- Third-party integrations

### Security Audits
- [ ] Conduct internal security audit quarterly
- [ ] Conduct external security audit annually (hire security firm)
- [ ] Review access controls and permissions
- [ ] Review security configurations (firewall, WAF, etc.)
- [ ] Review security logs and monitoring
- [ ] Review incident response procedures
- [ ] Review compliance with security policies
- [ ] Update security documentation based on audit findings
- [ ] Track security audit findings in ticketing system

**Security Audit Checklist:**
- [ ] Review user accounts and roles
- [ ] Review admin access logs
- [ ] Review firewall rules
- [ ] Review SSL/TLS configuration
- [ ] Review security headers
- [ ] Review rate limiting configuration
- [ ] Review backup and disaster recovery procedures
- [ ] Review vendor security (third-party services)

---

## 10. Incident Response

### Security Incident Procedure
1. **Detection & Identification**
   - [ ] Monitor alerts from Sentry, CloudWatch, or monitoring systems
   - [ ] Identify type of incident (data breach, DDoS, intrusion, etc.)
   - [ ] Assess initial severity (critical, high, medium, low)
   - [ ] Document incident details (time, type, affected systems)

2. **Containment**
   - [ ] Isolate affected systems (disable access, network segmentation)
   - [ ] Preserve evidence (logs, snapshots, memory dumps)
   - [ ] Stop active attacks (block IPs, disable accounts)
   - [ ] Prevent further damage (revoke credentials, patch vulnerabilities)

3. **Eradication**
   - [ ] Identify root cause of incident
   - [ ] Remove malware or malicious access
   - [ ] Patch vulnerabilities exploited in attack
   - [ ] Reset compromised credentials
   - [ ] Verify systems are clean before restoration

4. **Recovery**
   - [ ] Restore systems from clean backups
   - [ ] Verify system integrity after restoration
   - [ ] Gradually restore services (start with non-critical)
   - [ ] Monitor systems closely for 72 hours post-recovery
   - [ ] Communicate restoration status to stakeholders

5. **Post-Incident Activities**
   - [ ] Conduct incident post-mortem meeting
   - [ ] Document lessons learned
   - [ ] Update security controls to prevent recurrence
   - [ ] Update incident response plan
   - [ ] Provide training based on incident findings
   - [ ] Submit report to management and compliance teams

### Contact Information

**Security Team:**
- Security Lead: [Name, email, phone]
- DevOps Lead: [Name, email, phone]
- CTO/Technical Lead: [Name, email, phone]

**External Contacts:**
- Hosting Provider Support: [Support email, phone, escalation number]
- Security Consultant: [Firm name, contact, phone]
- Legal Counsel: [Law firm, attorney name, phone]
- Cyber Insurance: [Provider, policy number, claims phone]

**Regulatory Contacts (for data breaches):**
- GDPR: Data Protection Authority (DPA) in relevant EU country
- CCPA: California Attorney General (privacy@oag.ca.gov)
- FBI Cyber Division: IC3 (ic3.gov)

**Third-Party Vendors:**
- AWS Support: [Account number, support plan]
- Sentry: [Account email, support contact]
- SendGrid: [Support email]
- Twilio: [Support contact]

### Escalation Process

**Severity Levels:**
- **Critical (P0):** Data breach, service outage, active attack
  - Response time: Immediate (within 15 minutes)
  - Escalate to: Security Lead, CTO, CEO
  - Communication: Hourly updates to stakeholders

- **High (P1):** Security vulnerability, failed security control, potential breach
  - Response time: Within 1 hour
  - Escalate to: Security Lead, DevOps Lead
  - Communication: Daily updates

- **Medium (P2):** Suspicious activity, minor security issue
  - Response time: Within 4 hours
  - Escalate to: DevOps on-call
  - Communication: As needed

- **Low (P3):** Security recommendation, non-urgent issue
  - Response time: Within 1 business day
  - Escalate to: DevOps team
  - Communication: Weekly summary

**Escalation Path:**
1. DevOps on-call engineer (first responder)
2. Security Lead (within 30 minutes for P0/P1)
3. CTO (within 1 hour for P0, 4 hours for P1)
4. CEO (within 2 hours for P0 data breaches)
5. Legal counsel (for data breaches, regulatory issues)
6. Public Relations (for public-facing incidents)

### Communication Templates

**Internal Communication (Slack/Email):**
```
SECURITY INCIDENT - [SEVERITY]

Time Detected: [timestamp]
Incident Type: [data breach, DDoS, intrusion, etc.]
Affected Systems: [list of systems]
Current Status: [contained, investigating, recovering, resolved]
Impact: [user data, service availability, etc.]
Next Steps: [immediate actions]
Incident Commander: [name]

Updates to follow every [frequency based on severity].
```

**User Communication (Email):**
```
Subject: Security Notice - [Brief Description]

Dear CivicQ User,

We are writing to inform you of a security incident that may have affected your account.

What Happened:
[Clear, non-technical explanation of the incident]

What Information Was Involved:
[List of potentially affected data types]

What We Are Doing:
[Steps taken to secure systems and protect users]

What You Should Do:
[Recommended user actions: password reset, monitor accounts, etc.]

Additional Information:
[Link to FAQ, contact information, resources]

We sincerely apologize for this incident and are committed to protecting your data.

The CivicQ Security Team
[contact email]
```

**Regulatory Notification (GDPR/CCPA):**
```
[Use legal counsel for drafting regulatory notifications]

Required Information:
- Nature of the breach
- Categories of data affected
- Approximate number of data subjects affected
- Likely consequences of the breach
- Measures taken to address the breach
- Contact point for more information
```

**Public Statement (if needed):**
```
[Work with PR and legal counsel]

CivicQ Security Statement

On [date], we discovered [brief description of incident]. We immediately took steps to [containment actions].

We have no evidence that [specific user data] was compromised. Out of an abundance of caution, we are [user recommendations].

We take security seriously and have [enhanced security measures]. We will continue to monitor our systems and keep users informed.

For more information: [link to security page]
```

---

## Final Pre-Launch Security Review

### Critical Items (Must Be Complete Before Launch)
- [ ] `SECRET_KEY` generated and secured (never use default)
- [ ] `DEBUG=false` in production
- [ ] HTTPS enabled with valid SSL certificate
- [ ] All secrets stored in environment variables (not hardcoded)
- [ ] Database and Redis passwords changed from defaults
- [ ] Database and Redis not publicly accessible
- [ ] S3 bucket is private (no public access)
- [ ] CORS configured with production domains only
- [ ] Rate limiting enabled on authentication endpoints
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options, etc.)
- [ ] Admin accounts have MFA enabled
- [ ] Password policy enforced (minimum 12 characters)
- [ ] Session timeouts configured
- [ ] Logging and monitoring enabled (Sentry, CloudWatch, etc.)
- [ ] Backups configured and tested
- [ ] Incident response plan documented
- [ ] Security contact information updated

### High Priority (Complete Within 30 Days of Launch)
- [ ] Penetration testing completed
- [ ] Vulnerability scanning scheduled (weekly)
- [ ] Security audit completed
- [ ] Compliance documentation (GDPR, CCPA) finalized
- [ ] SSL Labs rating: A or higher
- [ ] All dependencies up to date with security patches
- [ ] Disaster recovery plan tested
- [ ] Security training for team completed
- [ ] IP whitelist for admin access (if applicable)
- [ ] WAF (Web Application Firewall) configured

### Medium Priority (Complete Within 90 Days of Launch)
- [ ] Automated security scanning in CI/CD pipeline
- [ ] Advanced monitoring and anomaly detection
- [ ] Security headers tested in all browsers
- [ ] HSTS preload list submission
- [ ] Third-party security vendor contracts signed
- [ ] Cyber insurance policy obtained
- [ ] GDPR Data Protection Impact Assessment (DPIA)
- [ ] Security metrics dashboard created
- [ ] Quarterly security review scheduled

---

## Security Review Sign-Off

**Completed by:** ___________________________
**Date:** ___________________________
**Reviewed by:** ___________________________
**Approved for Production:** [ ] YES  [ ] NO

**Notes:**
_______________________________________________________________________________
_______________________________________________________________________________
_______________________________________________________________________________

---

## Additional Resources

### Security Best Practices
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)
- [CWE Top 25](https://cwe.mitre.org/top25/)
- [NIST Cybersecurity Framework](https://www.nist.gov/cyberframework)
- [Mozilla Web Security Guidelines](https://infosec.mozilla.org/guidelines/web_security)
- [Google Cloud Security Best Practices](https://cloud.google.com/security/best-practices)
- [AWS Security Best Practices](https://aws.amazon.com/security/best-practices/)

### Security Testing Tools
- **OWASP ZAP** - Web application security scanner
- **Burp Suite** - Web vulnerability scanner
- **Nmap** - Network security scanner
- **Trivy** - Docker image vulnerability scanner
- **Snyk** - Dependency vulnerability scanner
- **Bandit** - Python security linter
- **SSL Labs** - SSL/TLS configuration tester
- **SecurityHeaders.com** - Security headers checker

### Compliance Resources
- [GDPR Official Text](https://gdpr-info.eu/)
- [CCPA Official Text](https://oag.ca.gov/privacy/ccpa)
- [HIPAA Security Rule](https://www.hhs.gov/hipaa/for-professionals/security/) (if handling health data)
- [PCI DSS](https://www.pcisecuritystandards.org/) (if handling credit cards)

### Monitoring & Incident Response
- [Sentry](https://sentry.io/) - Error tracking and monitoring
- [PagerDuty](https://www.pagerduty.com/) - Incident response and alerting
- [AWS CloudWatch](https://aws.amazon.com/cloudwatch/) - AWS monitoring
- [Datadog](https://www.datadoghq.com/) - Infrastructure monitoring
- [Splunk](https://www.splunk.com/) - Log analysis and SIEM

---

**Document Version:** 1.0.0
**Last Updated:** 2026-02-14
**Next Review Date:** 2026-05-14 (Quarterly review)

**Maintained by:** CivicQ Security Team
**Contact:** security@civicq.org

---

*This checklist is a living document and should be updated as new threats emerge and security best practices evolve. Review and update quarterly.*
