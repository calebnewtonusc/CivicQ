#!/bin/bash
#
# CivicQ Uptime Monitor
#
# Continuously monitors CivicQ services and sends alerts on failures.
# Designed to run as a cron job or systemd service.
#
# Usage:
#   ./uptime-monitor.sh [options]
#
# Options:
#   -i, --interval SECONDS    Check interval in seconds (default: 60)
#   -w, --webhook URL         Slack webhook URL for alerts
#   -e, --email EMAIL         Email address for alerts
#   -c, --continuous          Run continuously instead of single check
#   -h, --help                Show this help message

set -euo pipefail

# Configuration
INTERVAL=60
SLACK_WEBHOOK=""
ALERT_EMAIL=""
CONTINUOUS=false
STATE_FILE="/tmp/civicq-uptime-state"

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    -i|--interval)
      INTERVAL="$2"
      shift 2
      ;;
    -w|--webhook)
      SLACK_WEBHOOK="$2"
      shift 2
      ;;
    -e|--email)
      ALERT_EMAIL="$2"
      shift 2
      ;;
    -c|--continuous)
      CONTINUOUS=true
      shift
      ;;
    -h|--help)
      head -n 16 "$0" | tail -n +2 | sed 's/^# //'
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Function to send Slack alert
send_slack_alert() {
  local message=$1
  local severity=${2:-warning}

  if [ -z "$SLACK_WEBHOOK" ]; then
    return
  fi

  local color="warning"
  if [ "$severity" = "critical" ]; then
    color="danger"
  elif [ "$severity" = "good" ]; then
    color="good"
  fi

  curl -X POST "$SLACK_WEBHOOK" \
    -H 'Content-Type: application/json' \
    -d @- <<EOF
{
  "attachments": [
    {
      "color": "$color",
      "title": "CivicQ Uptime Alert",
      "text": "$message",
      "ts": $(date +%s)
    }
  ]
}
EOF
}

# Function to send email alert
send_email_alert() {
  local subject=$1
  local body=$2

  if [ -z "$ALERT_EMAIL" ]; then
    return
  fi

  echo "$body" | mail -s "$subject" "$ALERT_EMAIL"
}

# Function to check service
check_service() {
  local script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  "$script_dir/check-health.sh" --json > /tmp/civicq-health-check.json

  # Parse result
  status=$(jq -r '.status' /tmp/civicq-health-check.json)
  failed=$(jq -r '.failed' /tmp/civicq-health-check.json)

  echo "$status:$failed"
}

# Load previous state
prev_status="healthy"
if [ -f "$STATE_FILE" ]; then
  prev_status=$(cat "$STATE_FILE")
fi

# Main monitoring loop
run_check() {
  result=$(check_service)
  current_status=$(echo "$result" | cut -d: -f1)
  failed_count=$(echo "$result" | cut -d: -f2)

  timestamp=$(date '+%Y-%m-%d %H:%M:%S')

  # Save current state
  echo "$current_status" > "$STATE_FILE"

  # Check for state change
  if [ "$current_status" != "$prev_status" ]; then
    if [ "$current_status" = "unhealthy" ]; then
      # Service went down
      message="CivicQ services are experiencing issues. $failed_count health checks failed."
      echo "[$timestamp] ALERT: $message"
      send_slack_alert "$message" "critical"
      send_email_alert "CivicQ Uptime Alert - Service Down" "$message"
    else
      # Service recovered
      message="CivicQ services have recovered. All health checks passing."
      echo "[$timestamp] RECOVERY: $message"
      send_slack_alert "$message" "good"
      send_email_alert "CivicQ Uptime Alert - Service Recovered" "$message"
    fi

    prev_status="$current_status"
  else
    echo "[$timestamp] Status: $current_status ($failed_count failed checks)"
  fi
}

# Run monitoring
if [ "$CONTINUOUS" = true ]; then
  echo "Starting continuous monitoring (interval: ${INTERVAL}s)"
  echo "Press Ctrl+C to stop"
  echo ""

  while true; do
    run_check
    sleep "$INTERVAL"
  done
else
  run_check
fi
