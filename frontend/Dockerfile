# ============================================================================
# CivicQ Frontend - Multi-Stage Production Dockerfile
# ============================================================================
# This Dockerfile creates optimized production builds for the React frontend
#
# Build stages:
# 1. dependencies - Install npm dependencies
# 2. development - Development environment with hot reload
# 3. builder - Build production React bundle
# 4. production - Nginx serving static files
# ============================================================================

# ============================================================================
# Stage 1: Dependencies - Install NPM Packages
# ============================================================================
FROM node:18-alpine AS dependencies

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install dependencies
# Use ci for faster, reliable builds in CI/CD
RUN npm ci --only=production --silent && \
    npm cache clean --force

# ============================================================================
# Stage 2: Development - Development Environment
# ============================================================================
FROM node:18-alpine AS development

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (including devDependencies)
RUN npm ci --silent

# Copy source code
COPY . .

# Expose port
EXPOSE 3000

# Set environment
ENV NODE_ENV=development

# Start development server with hot reload
CMD ["npm", "start"]

# ============================================================================
# Stage 3: Builder - Build Production Bundle
# ============================================================================
FROM node:18-alpine AS builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package.json package-lock.json ./

# Install all dependencies (needed for build)
RUN npm ci --silent

# Copy source code
COPY . .

# Build arguments for environment variables
ARG REACT_APP_API_URL
ARG REACT_APP_BASE_URL
ARG REACT_APP_ENV=production
ARG REACT_APP_SENTRY_DSN
ARG REACT_APP_GOOGLE_ANALYTICS_ID
ARG REACT_APP_VERSION

# Set environment variables for build
ENV REACT_APP_API_URL=$REACT_APP_API_URL \
    REACT_APP_BASE_URL=$REACT_APP_BASE_URL \
    REACT_APP_ENV=$REACT_APP_ENV \
    REACT_APP_SENTRY_DSN=$REACT_APP_SENTRY_DSN \
    REACT_APP_GOOGLE_ANALYTICS_ID=$REACT_APP_GOOGLE_ANALYTICS_ID \
    REACT_APP_VERSION=$REACT_APP_VERSION \
    NODE_ENV=production \
    GENERATE_SOURCEMAP=false

# Build production bundle
RUN npm run build && \
    # Remove source maps if they exist (security)
    find build -name "*.map" -type f -delete && \
    # Verify build output
    ls -la build/

# ============================================================================
# Stage 4: Production - Nginx Static File Server
# ============================================================================
FROM nginx:1.25-alpine AS production

# Install utilities
RUN apk add --no-cache \
    curl \
    bash \
    tzdata

# Set timezone
ENV TZ=UTC

# Remove default Nginx configuration
RUN rm -rf /etc/nginx/conf.d/* && \
    rm -f /etc/nginx/nginx.conf

# Copy custom Nginx configuration for SPA
COPY nginx.conf /etc/nginx/nginx.conf

# Create nginx user and set permissions
RUN addgroup -g 101 -S nginx || true && \
    adduser -S -D -H -u 101 -h /var/cache/nginx -s /sbin/nologin -G nginx -g nginx nginx || true

# Copy built files from builder stage
COPY --from=builder --chown=nginx:nginx /app/build /usr/share/nginx/html

# Create cache and log directories with proper permissions
RUN mkdir -p /var/cache/nginx/client_temp \
    /var/cache/nginx/proxy_temp \
    /var/cache/nginx/fastcgi_temp \
    /var/cache/nginx/uwsgi_temp \
    /var/cache/nginx/scgi_temp \
    /var/log/nginx && \
    chown -R nginx:nginx /var/cache/nginx /var/log/nginx /usr/share/nginx/html && \
    chmod -R 755 /var/cache/nginx /var/log/nginx

# Create custom error pages
RUN echo '<!DOCTYPE html><html><head><title>404 Not Found</title></head><body><h1>404 - Page Not Found</h1><p>Return to <a href="/">home</a></p></body></html>' > /usr/share/nginx/html/404.html && \
    echo '<!DOCTYPE html><html><head><title>50x Error</title></head><body><h1>Server Error</h1><p>Please try again later.</p></body></html>' > /usr/share/nginx/html/50x.html

# Switch to non-root user for security
USER nginx

# Expose ports
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
