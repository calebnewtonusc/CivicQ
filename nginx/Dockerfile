FROM node:18-alpine AS frontend-builder

WORKDIR /app

# Copy frontend source
COPY ../frontend/package*.json ./
RUN npm ci --only=production

COPY ../frontend/ ./

# Build React app
ARG REACT_APP_API_URL
ARG REACT_APP_BASE_URL
ARG REACT_APP_ENV=production
ARG REACT_APP_SENTRY_DSN
ARG REACT_APP_GOOGLE_ANALYTICS_ID

ENV REACT_APP_API_URL=$REACT_APP_API_URL
ENV REACT_APP_BASE_URL=$REACT_APP_BASE_URL
ENV REACT_APP_ENV=$REACT_APP_ENV
ENV REACT_APP_SENTRY_DSN=$REACT_APP_SENTRY_DSN
ENV REACT_APP_GOOGLE_ANALYTICS_ID=$REACT_APP_GOOGLE_ANALYTICS_ID

RUN npm run build

# Production Nginx image
FROM nginx:1.25-alpine

# Install curl for health checks
RUN apk add --no-cache curl openssl

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/build /usr/share/nginx/html

# Create cache directories
RUN mkdir -p /var/cache/nginx/api /var/cache/nginx/static && \
    chown -R nginx:nginx /var/cache/nginx

# Create SSL directory
RUN mkdir -p /etc/nginx/ssl

# Generate DH parameters for SSL (this takes a while, consider pre-generating)
# RUN openssl dhparam -out /etc/nginx/ssl/dhparam.pem 2048

# Create directories for Let's Encrypt
RUN mkdir -p /var/www/certbot

# Expose ports
EXPOSE 80 443

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
