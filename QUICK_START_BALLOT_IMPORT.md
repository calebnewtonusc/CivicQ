# Quick Start: Ballot Data Import

Onboard a city in **5 minutes** with real ballot data!

## Prerequisites

1. Get API keys (5 minutes):
   - Google Civic: https://developers.google.com/civic-information
   - Ballotpedia: https://ballotpedia.org/API-documentation

2. Add to `.env`:
   ```bash
   GOOGLE_CIVIC_API_KEY=your_key_here
   BALLOTPEDIA_API_KEY=your_key_here
   ```

## 3-Step Import Process

### Step 1: Start Background Workers

```bash
# Terminal 1: Redis
redis-server

# Terminal 2: Celery Worker
cd backend
./scripts/start-celery-worker.sh

# Terminal 3: Celery Beat (optional - for auto-refresh)
./scripts/start-celery-beat.sh
```

### Step 2: Import Ballot Data

**Option A: CLI Script**
```bash
python scripts/import-ballot-data.py \
  --city "Los Angeles" \
  --state "CA" \
  --date "2024-11-05"
```

**Option B: API Call**
```bash
curl -X POST http://localhost:8000/api/admin/ballots/import \
  -H "Content-Type: application/json" \
  -d '{
    "city_name": "Los Angeles",
    "state": "CA",
    "election_date": "2024-11-05"
  }'
```

### Step 3: Publish the Ballot

```bash
curl -X POST http://localhost:8000/api/admin/ballots/1/publish
```

Done! The ballot is now live.

---

## What Gets Imported

- All races (Mayor, City Council, etc.)
- All ballot measures
- Candidate names and parties
- Candidate photos (if available)
- Measure text and summaries

## What to Add Manually (Optional)

- Candidate email addresses
- Candidate phone numbers
- Additional bio information

Use the bulk update endpoint:
```bash
curl -X POST http://localhost:8000/api/admin/ballots/1/update-contacts \
  -H "Content-Type: application/json" \
  -d '{
    "ballot_id": 1,
    "candidates": [
      {
        "candidate_id": 101,
        "email": "candidate@example.com",
        "phone": "+1-555-0123"
      }
    ]
  }'
```

---

## Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `POST /api/admin/ballots/import` | Import new ballot |
| `POST /api/admin/ballots/{id}/refresh` | Update existing ballot |
| `GET /api/admin/ballots/{id}/import-status` | Check data quality |
| `POST /api/admin/ballots/{id}/update-contacts` | Add contact info |
| `POST /api/admin/ballots/{id}/publish` | Make ballot live |

---

## Automatic Refresh

Ballots auto-refresh on this schedule:
- **2 weeks before election**: Daily
- **60 days before election**: Weekly
- **After election**: No refresh

---

## Troubleshooting

**No data found?**
- Check API keys in `.env`
- Verify election date is correct
- Try different data sources: `--sources google_civic`

**Missing contact info?**
- Normal - APIs don't provide contact info
- Add manually via bulk update endpoint

**Background jobs not running?**
- Check Redis: `redis-cli ping`
- Check Celery worker logs
- Restart Celery worker

---

## Full Documentation

- **Integration Guide**: `BALLOT_DATA_INTEGRATION.md`
- **Examples**: `docs/ballot-import-examples.md`
- **API Reference**: `http://localhost:8000/api/docs`

---

**Ready to import?** Run the script above and you're done!
