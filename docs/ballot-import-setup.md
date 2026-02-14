# Ballot Import System Setup Guide

Complete setup instructions for the ballot data import system.

---

## Prerequisites

### 1. System Requirements

- Python 3.9+
- PostgreSQL 12+
- Redis 6+
- 2GB RAM minimum
- Internet connection for API calls

### 2. API Keys

You'll need at least one API key (Google Civic recommended):

#### Google Civic Information API (Recommended)
1. Go to: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable "Google Civic Information API"
4. Create credentials → API Key
5. Restrict key to Civic Information API
6. Free tier: 25,000 requests/day

#### Ballotpedia API (Recommended)
1. Go to: https://ballotpedia.org/API-documentation
2. Request API access
3. Wait for approval (may take a few days)
4. Provides comprehensive candidate information

#### VoteAmerica API (Optional)
1. Visit: https://www.voteamerica.com/api/
2. Contact them for API access
3. Provides voter registration data

---

## Installation

### Step 1: Install Dependencies

```bash
cd backend

# Install Python packages
pip install -r requirements.txt

# Or use the specific new packages
pip install celery==5.3.6 celery-beat==2.5.0
```

### Step 2: Install and Start Redis

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

**Test Redis:**
```bash
redis-cli ping
# Should return: PONG
```

### Step 3: Configure Environment

```bash
cd backend

# Copy example env file
cp .env.example .env

# Edit .env and add your API keys
nano .env
```

Add your API keys:
```bash
# External Ballot Data APIs
GOOGLE_CIVIC_API_KEY=your_google_api_key_here
BALLOTPEDIA_API_KEY=your_ballotpedia_key_here
VOTE_AMERICA_API_KEY=your_voteamerica_key_here  # Optional
```

### Step 4: Database Migration (Optional)

The ballot import system uses existing tables, but if you need to add metadata:

```bash
cd backend

# Generate migration
alembic revision --autogenerate -m "Add ballot import metadata"

# Review the migration file
cat database/migrations/versions/XXXX_add_ballot_import_metadata.py

# Apply migration
alembic upgrade head
```

---

## Starting the System

### Development Mode

#### Terminal 1: Redis
```bash
redis-server
```

#### Terminal 2: FastAPI Backend
```bash
cd backend
source venv/bin/activate  # or activate your virtualenv
uvicorn app.main:app --reload --port 8000
```

#### Terminal 3: Celery Worker
```bash
cd backend
source venv/bin/activate
./scripts/start-celery-worker.sh
```

#### Terminal 4: Celery Beat (Optional - for auto-refresh)
```bash
cd backend
source venv/bin/activate
./scripts/start-celery-beat.sh
```

### Production Mode

Use supervisor or systemd to manage processes.

**Example systemd service (`/etc/systemd/system/civicq-celery.service`):**
```ini
[Unit]
Description=CivicQ Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=civicq
WorkingDirectory=/var/www/civicq/backend
Environment="PATH=/var/www/civicq/venv/bin"
ExecStart=/var/www/civicq/venv/bin/celery -A app.tasks worker \
    --loglevel=info \
    --concurrency=4 \
    --pidfile=/var/run/celery/%n.pid \
    --logfile=/var/log/celery/%n%I.log
Restart=always

[Install]
WantedBy=multi-user.target
```

Start services:
```bash
sudo systemctl start civicq-celery
sudo systemctl enable civicq-celery
```

---

## Verification

### Test Redis Connection

```bash
redis-cli ping
# Expected: PONG
```

### Test Celery Worker

```bash
# In Python shell
from app.tasks.ballot_refresh import refresh_ballot_task
result = refresh_ballot_task.delay(1)
print(result.id)

# Check task status
celery -A app.tasks inspect active
```

### Test API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Import endpoint (will fail without data, but tests connection)
curl -X POST http://localhost:8000/api/admin/ballots/import \
  -H "Content-Type: application/json" \
  -d '{"city_name": "Test", "state": "CA", "election_date": "2024-11-05"}'
```

### Test External APIs

```bash
# Test Google Civic API
curl "https://www.googleapis.com/civicinfo/v2/elections?key=YOUR_API_KEY"

# Should return list of elections
```

---

## First Import

### Quick Test Import

```bash
# Import a small city to test
python scripts/import-ballot-data.py \
  --city "Berkeley" \
  --state "CA" \
  --date "2024-11-05"
```

### Expected Output

```
======================================================
Importing ballot data for Berkeley, CA
Election Date: 2024-11-05
Data Sources: google_civic, ballotpedia
======================================================

Fetched ballot from Google Civic API
Fetched ballot from Ballotpedia API
Merged 2 ballot sources

======================== SUCCESS! ====================

Ballot ID: 1
City: Berkeley
Election Date: 2024-11-05

Imported:
  - 8 contests
  - 15 candidates
  - 3 ballot measures

Data Quality:
  - Contact info coverage: 73.3%
  - Candidates with contact: 11/15

======================================================
```

---

## Monitoring

### View Celery Tasks

```bash
# Active tasks
celery -A app.tasks inspect active

# Scheduled tasks
celery -A app.tasks inspect scheduled

# Registered tasks
celery -A app.tasks inspect registered

# Worker stats
celery -A app.tasks inspect stats
```

### View Logs

```bash
# Celery worker logs
tail -f celery.log

# FastAPI logs
tail -f app.log

# Redis logs
tail -f /var/log/redis/redis-server.log
```

### Monitor with Flower (Optional)

```bash
# Install Flower
pip install flower

# Start Flower web interface
celery -A app.tasks flower --port=5555

# Access at: http://localhost:5555
```

---

## Troubleshooting

### Redis Not Connecting

**Error:** `ConnectionError: Error 111 connecting to localhost:6379`

**Solution:**
```bash
# Check Redis is running
redis-cli ping

# Start Redis if not running
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# Check Redis port
redis-cli info | grep tcp_port
```

### Celery Worker Not Starting

**Error:** `ImportError: No module named 'celery'`

**Solution:**
```bash
# Make sure virtualenv is activated
source venv/bin/activate

# Reinstall celery
pip install celery==5.3.6 celery-beat==2.5.0
```

### API Key Not Working

**Error:** `403 Forbidden` or `401 Unauthorized`

**Solution:**
```bash
# Check API key is set
echo $GOOGLE_CIVIC_API_KEY

# Or check .env file
cat backend/.env | grep API_KEY

# Test API key directly
curl "https://www.googleapis.com/civicinfo/v2/elections?key=YOUR_KEY"
```

### No Ballot Data Found

**Error:** `ValueError: No ballot data found for this address`

**Solution:**
- Verify election date is correct
- Try different data sources: `--sources ballotpedia`
- Check address format is correct
- Use city-based import instead: `--city "City" --state "CA"`

### Database Connection Error

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep civicq

# Check DATABASE_URL in .env
cat backend/.env | grep DATABASE_URL
```

---

## Performance Tuning

### Celery Workers

Adjust concurrency based on your system:

```bash
# More workers for better throughput
celery -A app.tasks worker --concurrency=8

# Limit memory usage
celery -A app.tasks worker --max-tasks-per-child=100
```

### Redis Configuration

For high load, tune Redis:

```bash
# Edit redis.conf
nano /etc/redis/redis.conf

# Increase max memory
maxmemory 2gb
maxmemory-policy allkeys-lru
```

### Database Connection Pool

Tune SQLAlchemy pool size:

```python
# In config.py
engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40,
)
```

---

## Security Checklist

- [ ] API keys stored in environment variables (not code)
- [ ] .env file added to .gitignore
- [ ] Redis protected with password (production)
- [ ] Admin endpoints require authentication
- [ ] HTTPS enabled (production)
- [ ] Rate limiting configured
- [ ] API keys restricted to specific IPs (production)
- [ ] Logs don't contain API keys
- [ ] Celery secured with authentication (production)

---

## Backup and Recovery

### Backup Ballots

```bash
# Export ballot data
curl http://localhost:8000/api/admin/ballots/1/export > ballot_1.json

# Backup database
pg_dump civicq > civicq_backup.sql
```

### Restore After Import Failure

```bash
# Database rollback
psql civicq < civicq_backup.sql

# Re-import with different sources
python scripts/import-ballot-data.py \
  --city "Los Angeles" --state "CA" --date "2024-11-05" \
  --sources google_civic  # Try single source
```

---

## Scaling for Production

### Multiple Workers

```bash
# Start multiple worker processes
for i in {1..4}; do
  celery -A app.tasks worker \
    --hostname=worker$i@%h \
    --loglevel=info &
done
```

### Redis Cluster

For high availability:

```bash
# Use Redis Sentinel or Cluster
CELERY_BROKER_URL=redis-sentinel://sentinel:26379/mymaster
```

### Load Balancing

Use nginx to load balance API requests:

```nginx
upstream civicq_api {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    location / {
        proxy_pass http://civicq_api;
    }
}
```

---

## Maintenance

### Weekly Tasks

- Check Celery worker health
- Review import logs for errors
- Monitor API usage (rate limits)
- Verify scheduled refreshes running

### Before Each Election

- Refresh all ballots (30 days before)
- Verify candidate contact info
- Test import with new addresses
- Check data quality metrics

### After Each Election

- Archive ballot data
- Clean up old tasks
- Review import statistics
- Update documentation with lessons learned

---

## Getting Help

### Debug Mode

Enable verbose logging:

```bash
# In .env
LOG_LEVEL=DEBUG

# Run Celery with debug
celery -A app.tasks worker --loglevel=debug
```

### Check System Status

```bash
# All services status
./scripts/check-status.sh

# Or manually:
redis-cli ping
pg_isready
celery -A app.tasks inspect ping
curl http://localhost:8000/health
```

### Common Commands Reference

```bash
# Start everything
redis-server &
cd backend && uvicorn app.main:app &
./scripts/start-celery-worker.sh &

# Import ballot
python scripts/import-ballot-data.py --city "City" --state "ST" --date "YYYY-MM-DD"

# Check status
celery -A app.tasks inspect active

# Stop everything
pkill -f celery
pkill -f uvicorn
redis-cli shutdown
```

---

## Next Steps

1. Complete setup checklist above
2. Import your first ballot
3. Review data quality metrics
4. Set up automated refreshes
5. Configure monitoring alerts
6. Read examples: `docs/ballot-import-examples.md`
7. Review full guide: `BALLOT_DATA_INTEGRATION.md`

---

**Questions?** Check the troubleshooting section or open an issue!
