# Cloudflare CDN Configuration Guide

Complete guide for setting up Cloudflare CDN for CivicQ to optimize static asset delivery and improve performance globally.

## Overview

Cloudflare provides:
- Global CDN with 300+ data centers
- Automatic SSL/TLS
- DDoS protection
- Web Application Firewall (WAF)
- Image optimization
- Caching and compression

## Setup Instructions

### 1. Domain Configuration

1. **Add Domain to Cloudflare**
   ```bash
   # Go to Cloudflare Dashboard
   # Add your domain (e.g., civicq.org)
   # Update nameservers at your registrar
   ```

2. **DNS Records**
   ```
   Type    Name              Content                 Proxy Status
   A       @                 <server-ip>            Proxied
   A       www               <server-ip>            Proxied
   CNAME   api               backend.civicq.org     Proxied
   CNAME   cdn               static.civicq.org      Proxied
   ```

### 2. Page Rules for Caching

Create the following page rules (order matters):

1. **API Endpoints - Bypass Cache**
   ```
   URL: api.civicq.org/*
   Settings:
     - Cache Level: Bypass
   ```

2. **Static Assets - Aggressive Caching**
   ```
   URL: cdn.civicq.org/static/*
   Settings:
     - Cache Level: Cache Everything
     - Edge Cache TTL: 1 month
     - Browser Cache TTL: 1 week
   ```

3. **Images - Optimize and Cache**
   ```
   URL: cdn.civicq.org/images/*
   Settings:
     - Cache Level: Cache Everything
     - Edge Cache TTL: 1 week
     - Polish: Lossless
     - WebP: On
   ```

4. **Videos - Cache with Long TTL**
   ```
   URL: cdn.civicq.org/videos/*
   Settings:
     - Cache Level: Cache Everything
     - Edge Cache TTL: 1 month
     - Rocket Loader: Off (for video players)
   ```

### 3. Caching Configuration

**Caching Level**: Standard
- Cloudflare caches static files by default
- Custom rules above for specific paths

**Browser Cache Expiration**: Respect Existing Headers
- Let application control cache headers
- Override only for static assets

**Always Online**: Enabled
- Serves cached version if origin is down

### 4. Optimization Settings

**Auto Minify**:
- [x] JavaScript
- [x] CSS
- [x] HTML

**Brotli Compression**: Enabled
- Better compression than gzip
- Supported by all modern browsers

**HTTP/2**: Enabled
- Multiplexing for faster page loads

**HTTP/3 (QUIC)**: Enabled
- Improved performance on poor networks

**Rocket Loader**: Disabled for main site, enabled for marketing pages
- Can break some JavaScript functionality
- Test thoroughly before enabling

### 5. Image Optimization

**Polish**: Lossless
- Automatically optimizes images
- Reduces file size without quality loss

**WebP**: On
- Serves WebP to supporting browsers
- Falls back to original format

**Mirage**: On
- Lazy loads images
- Serves lower resolution on slow connections

### 6. Security Settings

**SSL/TLS Mode**: Full (Strict)
- Encrypt traffic between visitors and Cloudflare
- Encrypt traffic between Cloudflare and origin

**Always Use HTTPS**: On
- Redirect HTTP to HTTPS

**Minimum TLS Version**: 1.2
- Disable older, insecure protocols

**HSTS**: Enabled
```
Max Age: 31536000 (1 year)
Include Subdomains: Yes
Preload: Yes
```

**WAF (Web Application Firewall)**: Enabled
- Managed rules for common vulnerabilities
- Rate limiting rules

### 7. Rate Limiting

Create rate limiting rules:

1. **API Rate Limit**
   ```
   If incoming requests match:
     - URL Path contains "/api/"
   Then:
     - Block if > 100 requests per minute
     - Block duration: 10 minutes
   ```

2. **Video Upload Rate Limit**
   ```
   If incoming requests match:
     - URL Path contains "/api/videos/upload"
     - Method is POST
   Then:
     - Block if > 10 requests per hour
     - Block duration: 1 hour
   ```

### 8. Performance Monitoring

**Analytics**:
- Monitor cache hit ratio (aim for >80%)
- Track bandwidth savings
- Identify slow pages

**Speed Test**:
- Use Cloudflare Observatory
- Test from multiple locations
- Monitor Core Web Vitals

## Cache Invalidation

### Purge Cache via Dashboard

1. Go to Caching > Configuration
2. Select purge type:
   - Purge Everything (use sparingly)
   - Purge by URL (specific files)
   - Purge by Tag (tagged content)
   - Purge by Prefix (directory paths)

### Purge Cache via API

```bash
# Purge everything (use sparingly)
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"purge_everything":true}'

# Purge specific files
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"files":["https://cdn.civicq.org/static/main.js"]}'

# Purge by tag
curl -X POST "https://api.cloudflare.com/client/v4/zones/{zone_id}/purge_cache" \
  -H "Authorization: Bearer {api_token}" \
  -H "Content-Type: application/json" \
  --data '{"tags":["ballot-data"]}'
```

### Automated Cache Invalidation

Add to deployment script:
```bash
#!/bin/bash
# After deploying new frontend build

curl -X POST "https://api.cloudflare.com/client/v4/zones/${CF_ZONE_ID}/purge_cache" \
  -H "Authorization: Bearer ${CF_API_TOKEN}" \
  -H "Content-Type: application/json" \
  --data '{"files":[
    "https://cdn.civicq.org/static/main.*.js",
    "https://cdn.civicq.org/static/main.*.css"
  ]}'
```

## Cache Headers

Set appropriate cache headers in your application:

### Backend (FastAPI)

```python
# For static assets
@app.get("/static/{path}")
async def serve_static(path: str):
    return FileResponse(
        path,
        headers={
            "Cache-Control": "public, max-age=31536000, immutable",
            "Vary": "Accept-Encoding",
        }
    )

# For API responses
@app.get("/api/ballots/{ballot_id}")
async def get_ballot(ballot_id: int):
    data = get_ballot_data(ballot_id)
    return JSONResponse(
        content=data,
        headers={
            "Cache-Control": "public, max-age=3600",  # 1 hour
            "Vary": "Accept, Accept-Encoding",
            "ETag": calculate_etag(data),
        }
    )
```

### Frontend (React)

```typescript
// Cache-busting for builds
// webpack automatically adds hashes to filenames
// main.[hash].js, main.[hash].css

// Service worker for offline caching (optional)
// See: workbox-webpack-plugin
```

## Testing CDN Performance

### Test Cache Status

```bash
# Check if resource is cached
curl -I https://cdn.civicq.org/static/main.js | grep -i cf-cache-status

# Possible values:
# HIT - Served from cache
# MISS - Not in cache, fetched from origin
# EXPIRED - Cache expired, revalidating
# BYPASS - Cache bypassed per rule
```

### Measure Performance

```bash
# Test from multiple locations
curl -w "@curl-format.txt" -o /dev/null -s https://civicq.org

# curl-format.txt:
#   time_namelookup:  %{time_namelookup}s\n
#   time_connect:  %{time_connect}s\n
#   time_appconnect:  %{time_appconnect}s\n
#   time_pretransfer:  %{time_pretransfer}s\n
#   time_redirect:  %{time_redirect}s\n
#   time_starttransfer:  %{time_starttransfer}s\n
#   time_total:  %{time_total}s\n
```

## Best Practices

1. **Set Appropriate TTLs**
   - Static assets (JS/CSS with hashes): 1 year
   - Images: 1 week
   - API responses: 5-60 minutes based on data freshness
   - HTML: No cache or very short (for SPA, cache in service worker)

2. **Use Cache Tags**
   - Tag related content for efficient invalidation
   - Example: All ballot data tagged with `ballot-{id}`

3. **Monitor Cache Hit Ratio**
   - Aim for >80% hit ratio
   - Investigate low hit ratios (might indicate cache rules issues)

4. **Version Static Assets**
   - Use hash-based filenames for cache busting
   - Example: `main.abc123.js` instead of `main.js`

5. **Optimize Images**
   - Use Cloudflare Polish for automatic optimization
   - Serve WebP to supporting browsers
   - Use responsive images with srcset

6. **Enable Compression**
   - Brotli for modern browsers
   - Gzip fallback for older browsers

## Troubleshooting

**Low Cache Hit Ratio**:
- Check cache rules
- Verify cache headers from origin
- Look for query strings preventing caching

**Stale Content**:
- Purge cache for updated files
- Check cache TTLs
- Verify ETag implementation

**Slow Origin Requests**:
- Optimize backend performance
- Enable Argo Smart Routing (premium feature)
- Use Workers for edge computing (premium feature)

## Cost Optimization

Cloudflare Free Tier includes:
- Unlimited bandwidth
- Basic DDoS protection
- Shared SSL certificate
- Limited Page Rules (3)

Pro Tier ($20/month) adds:
- 20 Page Rules
- Image optimization (Polish, Mirage)
- Better performance
- Mobile optimization

Business Tier ($200/month) adds:
- Custom SSL certificates
- Advanced DDoS protection
- 100% uptime SLA
- Priority support

For CivicQ, start with Pro tier for image optimization and additional page rules.
