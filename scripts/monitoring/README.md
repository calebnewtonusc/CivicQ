# CivicQ Monitoring Scripts

Automated monitoring and health check scripts for CivicQ production operations.

## Scripts

### check-health.sh

Comprehensive health check script that validates all CivicQ services.

**Features**:
- Checks all health endpoints
- JSON or human-readable output
- Verbose mode for debugging
- Exit codes for automation
- Color-coded status indicators

**Usage**:
```bash
# Basic health check
./check-health.sh

# Check specific environment
./check-health.sh --url https://api.civicq.com

# JSON output (for automation/CI/CD)
./check-health.sh --json

# Verbose output (for troubleshooting)
./check-health.sh --verbose

# Combine options
./check-health.sh --url https://staging.civicq.com --verbose
```

**Exit Codes**:
- `0` - All health checks passed
- `1` - One or more health checks failed

**Health Checks Performed**:
1. Basic liveness (`/health`)
2. Readiness check (`/health/ready`)
3. Database connectivity (`/health/db`)
4. Redis connectivity (`/health/redis`)
5. Celery workers (`/health/celery`)
6. Object storage (`/health/storage`)
7. System resources (`/health/system`)

**Example Output**:
```
=========================================
CivicQ Health Check
=========================================
Base URL: http://localhost:8000

✓ Basic Health: OK
✓ Readiness Check: HEALTHY
✓ Database: HEALTHY
✓ Redis: HEALTHY
⚠ Celery Workers: DEGRADED
✓ Object Storage: HEALTHY
✓ System Resources: HEALTHY

=========================================
Summary:
  Total checks: 7
  Passed: 6
  Failed: 0
=========================================
All health checks passed!
```

---

### uptime-monitor.sh

Continuous uptime monitoring with alerting capabilities.

**Features**:
- Single or continuous monitoring
- Slack webhook integration
- Email alerting
- State change detection
- Configurable check interval

**Usage**:
```bash
# Single check
./uptime-monitor.sh

# Continuous monitoring (every 60 seconds)
./uptime-monitor.sh --continuous --interval 60

# With Slack alerts
./uptime-monitor.sh --continuous --webhook https://hooks.slack.com/services/xxx

# With email alerts
./uptime-monitor.sh --continuous --email ops@civicq.com

# Full monitoring with all alerts
./uptime-monitor.sh --continuous \
  --interval 60 \
  --webhook $SLACK_WEBHOOK_URL \
  --email ops@civicq.com
```

**State Tracking**:
- Stores state in `/tmp/civicq-uptime-state`
- Alerts only on state changes (healthy → unhealthy or vice versa)
- Prevents alert fatigue from repeated notifications

**Alerts Sent**:
- **Service Down**: When health checks start failing
- **Service Recovered**: When health checks pass again

**Example Output**:
```
Starting continuous monitoring (interval: 60s)
Press Ctrl+C to stop

[2024-02-14 12:00:00] Status: healthy (0 failed checks)
[2024-02-14 12:01:00] Status: healthy (0 failed checks)
[2024-02-14 12:02:00] ALERT: CivicQ services are experiencing issues. 2 health checks failed.
[2024-02-14 12:03:00] Status: unhealthy (2 failed checks)
[2024-02-14 12:04:00] RECOVERY: CivicQ services have recovered. All health checks passing.
```

---

## Integration Examples

### Cron Job

Run health checks every 5 minutes and log results:

```bash
# Add to crontab
crontab -e

# Add line:
*/5 * * * * /path/to/scripts/monitoring/check-health.sh --json >> /var/log/civicq-health.log 2>&1
```

### CI/CD Pipeline

Use in GitHub Actions, GitLab CI, or similar:

```yaml
# .github/workflows/deploy.yml
- name: Health Check
  run: |
    ./scripts/monitoring/check-health.sh --url https://api.civicq.com
  # Will fail deployment if health checks fail
```

### Docker Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
```

### Kubernetes Liveness/Readiness

```yaml
livenessProbe:
  exec:
    command:
    - /app/scripts/monitoring/check-health.sh
    - --json
  initialDelaySeconds: 30
  periodSeconds: 10
```

### Systemd Service

Create a systemd service for continuous monitoring:

```ini
# /etc/systemd/system/civicq-monitor.service
[Unit]
Description=CivicQ Uptime Monitor
After=network.target

[Service]
Type=simple
User=civicq
WorkingDirectory=/opt/civicq
ExecStart=/opt/civicq/scripts/monitoring/uptime-monitor.sh --continuous --interval 60 --webhook https://hooks.slack.com/services/xxx
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable civicq-monitor
sudo systemctl start civicq-monitor
sudo systemctl status civicq-monitor
```

### Slack Integration

Set up Slack webhook:

1. Go to https://api.slack.com/apps
2. Create new app
3. Enable Incoming Webhooks
4. Add webhook to workspace
5. Copy webhook URL
6. Use with `--webhook` flag

**Alert Format**:
```json
{
  "attachments": [{
    "color": "danger",
    "title": "CivicQ Uptime Alert",
    "text": "CivicQ services are experiencing issues. 2 health checks failed.",
    "ts": 1707912000
  }]
}
```

### PagerDuty Integration

For critical alerts, integrate with PagerDuty:

```bash
# In uptime-monitor.sh, add PagerDuty call
curl -X POST https://events.pagerduty.com/v2/enqueue \
  -H "Content-Type: application/json" \
  -d '{
    "routing_key": "'$PAGERDUTY_ROUTING_KEY'",
    "event_action": "trigger",
    "payload": {
      "summary": "CivicQ service down",
      "severity": "critical",
      "source": "uptime-monitor"
    }
  }'
```

## Troubleshooting

### Health Check Fails Locally

```bash
# Check if API is running
curl http://localhost:8000/health

# Check logs
docker logs civicq-api --tail=50

# Check with verbose mode
./check-health.sh --verbose
```

### jq Command Not Found

Install jq for JSON parsing:

```bash
# Ubuntu/Debian
sudo apt-get install jq

# macOS
brew install jq

# CentOS/RHEL
sudo yum install jq
```

### Permission Denied

Make scripts executable:

```bash
chmod +x check-health.sh uptime-monitor.sh
```

### Slack Alerts Not Sending

1. Verify webhook URL is correct
2. Test webhook manually:
```bash
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{"text":"Test message"}'
```

### Email Alerts Not Sending

1. Verify mail command is available: `which mail`
2. Install mailutils if needed: `sudo apt-get install mailutils`
3. Configure SMTP settings in `/etc/postfix/main.cf`

## Environment Variables

Configure via environment variables:

```bash
# Default API URL
export CIVICQ_API_URL=https://api.civicq.com

# Slack webhook
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx

# PagerDuty
export PAGERDUTY_ROUTING_KEY=xxx

# Email
export ALERT_EMAIL=ops@civicq.com

# Use in scripts
./check-health.sh  # Will use CIVICQ_API_URL
```

## Best Practices

1. **Multiple Environments**: Create separate monitoring for each environment
   ```bash
   ./check-health.sh --url https://staging.civicq.com > /var/log/staging-health.log
   ./check-health.sh --url https://api.civicq.com > /var/log/prod-health.log
   ```

2. **Alert Routing**: Use different Slack channels for different severities
   ```bash
   # Critical alerts to #alerts-critical
   # Warning alerts to #alerts-warning
   ```

3. **Log Retention**: Rotate logs to prevent disk space issues
   ```bash
   # /etc/logrotate.d/civicq-health
   /var/log/civicq-health.log {
       daily
       rotate 30
       compress
       missingok
       notifempty
   }
   ```

4. **Monitoring the Monitor**: Set up a separate watchdog to ensure monitoring is running
   ```bash
   # Check if monitor process is running
   pgrep -f uptime-monitor.sh || systemctl restart civicq-monitor
   ```

## Related Documentation

- [MONITORING_GUIDE.md](../../MONITORING_GUIDE.md) - Complete monitoring setup
- [RUNBOOK.md](../../RUNBOOK.md) - Incident response procedures
- [ALERT_REFERENCE.md](../../ALERT_REFERENCE.md) - Alert definitions
