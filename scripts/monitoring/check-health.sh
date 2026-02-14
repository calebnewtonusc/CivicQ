#!/bin/bash
#
# CivicQ Health Check Script
#
# This script performs comprehensive health checks on all CivicQ services.
# Use this for monitoring, deployment validation, and troubleshooting.
#
# Usage:
#   ./check-health.sh [options]
#
# Options:
#   -u, --url URL     Base URL to check (default: http://localhost:8000)
#   -v, --verbose     Verbose output
#   -j, --json        Output in JSON format
#   -h, --help        Show this help message

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default configuration
BASE_URL="${CIVICQ_API_URL:-http://localhost:8000}"
VERBOSE=false
JSON_OUTPUT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -u|--url)
      BASE_URL="$2"
      shift 2
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    -j|--json)
      JSON_OUTPUT=true
      shift
      ;;
    -h|--help)
      head -n 15 "$0" | tail -n +2 | sed 's/^# //'
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to check endpoint health
check_endpoint() {
  local endpoint=$1
  local name=$2
  local expected_status=${3:-200}

  if [ "$VERBOSE" = true ]; then
    echo "Checking $name..."
  fi

  response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint" || echo -e "\n000")
  http_code=$(echo "$response" | tail -n 1)
  body=$(echo "$response" | sed '$d')

  if [ "$http_code" -eq "$expected_status" ]; then
    if [ "$JSON_OUTPUT" = false ]; then
      echo -e "${GREEN}✓${NC} $name: OK"
    fi
    return 0
  else
    if [ "$JSON_OUTPUT" = false ]; then
      echo -e "${RED}✗${NC} $name: FAILED (HTTP $http_code)"
      if [ "$VERBOSE" = true ]; then
        echo "  Response: $body"
      fi
    fi
    return 1
  fi
}

# Function to check service with JSON response
check_service() {
  local endpoint=$1
  local name=$2

  if [ "$VERBOSE" = true ]; then
    echo "Checking $name..."
  fi

  response=$(curl -s "$BASE_URL$endpoint" || echo '{"status":"error"}')
  status=$(echo "$response" | jq -r '.status // "error"' 2>/dev/null || echo "error")

  if [ "$status" = "healthy" ]; then
    if [ "$JSON_OUTPUT" = false ]; then
      echo -e "${GREEN}✓${NC} $name: HEALTHY"
      if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
      fi
    fi
    return 0
  elif [ "$status" = "degraded" ]; then
    if [ "$JSON_OUTPUT" = false ]; then
      echo -e "${YELLOW}⚠${NC} $name: DEGRADED"
      if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
      fi
    fi
    return 0
  else
    if [ "$JSON_OUTPUT" = false ]; then
      echo -e "${RED}✗${NC} $name: UNHEALTHY"
      if [ "$VERBOSE" = true ]; then
        echo "$response" | jq '.' 2>/dev/null || echo "$response"
      fi
    fi
    return 1
  fi
}

# Start health checks
if [ "$JSON_OUTPUT" = false ]; then
  echo "========================================="
  echo "CivicQ Health Check"
  echo "========================================="
  echo "Base URL: $BASE_URL"
  echo ""
fi

# Track results
total_checks=0
passed_checks=0
failed_checks=0

# Basic liveness check
if check_endpoint "/health" "Basic Health"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# Readiness check
if check_service "/health/ready" "Readiness Check"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# Database health
if check_service "/health/db" "Database"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# Redis health
if check_service "/health/redis" "Redis"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# Celery health
if check_service "/health/celery" "Celery Workers"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# Storage health
if check_service "/health/storage" "Object Storage"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# System resources
if check_service "/health/system" "System Resources"; then
  ((passed_checks++))
else
  ((failed_checks++))
fi
((total_checks++))

# Summary
if [ "$JSON_OUTPUT" = true ]; then
  # JSON output
  cat <<EOF
{
  "base_url": "$BASE_URL",
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "total_checks": $total_checks,
  "passed": $passed_checks,
  "failed": $failed_checks,
  "status": "$([ $failed_checks -eq 0 ] && echo "healthy" || echo "unhealthy")"
}
EOF
else
  # Human-readable output
  echo ""
  echo "========================================="
  echo "Summary:"
  echo "  Total checks: $total_checks"
  echo -e "  Passed: ${GREEN}$passed_checks${NC}"
  echo -e "  Failed: ${RED}$failed_checks${NC}"
  echo "========================================="

  if [ $failed_checks -eq 0 ]; then
    echo -e "${GREEN}All health checks passed!${NC}"
    exit 0
  else
    echo -e "${RED}Some health checks failed!${NC}"
    exit 1
  fi
fi
