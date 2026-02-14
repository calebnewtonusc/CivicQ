# Ballot Import Examples

Real-world examples of importing ballot data into CivicQ.

---

## Example 1: Import Los Angeles City Elections

### Using the Python Script

```bash
cd /path/to/CivicQ
python scripts/import-ballot-data.py \
  --city "Los Angeles" \
  --state "CA" \
  --date "2024-11-05"
```

### Using the API

```bash
curl -X POST http://localhost:8000/api/admin/ballots/import \
  -H "Content-Type: application/json" \
  -d '{
    "city_name": "Los Angeles",
    "state": "CA",
    "election_date": "2024-11-05",
    "sources": ["google_civic", "ballotpedia"]
  }'
```

### Expected Output

```
======================================================
Importing ballot data for Los Angeles, CA
Election Date: 2024-11-05
Data Sources: google_civic, ballotpedia
======================================================

Fetched ballot from Google Civic API
Fetched ballot from Ballotpedia API
Merged 2 ballot sources

======================== SUCCESS! ====================

Ballot ID: 1
City: Los Angeles
Election Date: 2024-11-05
Version: 1

Imported:
  - 15 contests
  - 47 candidates
  - 8 ballot measures

Data Quality:
  - Contact info coverage: 68.1%
  - Candidates with contact: 32/47

======================================================
Next Steps:
  1. Review the ballot at: http://localhost:8000/api/ballots/1
  2. Add missing contact info via admin panel
  3. Publish the ballot to make it live
======================================================
```

---

## Example 2: Import by Voter Address

This is useful when you don't know the exact city boundaries.

### Using the Python Script

```bash
python scripts/import-ballot-data.py \
  --address "1600 Pennsylvania Avenue NW, Washington, DC 20500"
```

### Using the API

```bash
curl -X POST http://localhost:8000/api/admin/ballots/import \
  -H "Content-Type: application/json" \
  -d '{
    "address": "1600 Pennsylvania Avenue NW, Washington, DC 20500",
    "sources": ["google_civic"]
  }'
```

---

## Example 3: Refresh Existing Ballot

Update ballot with latest candidate information.

```bash
curl -X POST http://localhost:8000/api/admin/ballots/1/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "ballot_id": 1,
    "sources": ["google_civic", "ballotpedia"]
  }'
```

---

## Example 4: Check Import Status

```bash
curl http://localhost:8000/api/admin/ballots/1/import-status
```

### Response

```json
{
  "ballot_id": 1,
  "city_name": "Los Angeles",
  "election_date": "2024-11-05",
  "version": 2,
  "is_published": false,
  "last_updated": "2024-10-15T14:30:00Z",
  "sources": ["google_civic", "ballotpedia"],
  "statistics": {
    "total_contests": 15,
    "total_candidates": 47,
    "candidates_with_contact": 32,
    "candidates_verified": 8,
    "contact_info_percentage": 68.1,
    "verification_percentage": 17.0
  }
}
```

---

## Example 5: Bulk Update Candidate Contacts

After importing, you can manually add missing contact information:

```bash
curl -X POST http://localhost:8000/api/admin/ballots/1/update-contacts \
  -H "Content-Type: application/json" \
  -d '{
    "ballot_id": 1,
    "candidates": [
      {
        "candidate_id": 101,
        "email": "john.smith@campaign.com",
        "phone": "+1-555-0101",
        "website": "https://johnsmith.vote"
      },
      {
        "candidate_id": 102,
        "email": "jane.doe@campaign.com",
        "phone": "+1-555-0102",
        "website": "https://janedoe.vote"
      }
    ]
  }'
```

---

## Example 6: Publish Ballot

Once you've reviewed the data, make it live:

```bash
curl -X POST http://localhost:8000/api/admin/ballots/1/publish
```

Response:
```json
{
  "success": true,
  "ballot_id": 1,
  "message": "Ballot for Los Angeles published successfully"
}
```

---

## Example 7: Multiple Cities in One Script

Create a bash script to import multiple cities:

```bash
#!/bin/bash
# import-multiple-cities.sh

CITIES=(
  "Los Angeles,CA,2024-11-05"
  "San Francisco,CA,2024-11-05"
  "Oakland,CA,2024-11-05"
  "Berkeley,CA,2024-11-05"
)

for CITY_DATA in "${CITIES[@]}"; do
  IFS=',' read -r CITY STATE DATE <<< "$CITY_DATA"

  echo "Importing $CITY, $STATE..."

  python scripts/import-ballot-data.py \
    --city "$CITY" \
    --state "$STATE" \
    --date "$DATE"

  echo "Completed $CITY"
  echo "---"
done

echo "All cities imported!"
```

Run it:
```bash
chmod +x import-multiple-cities.sh
./import-multiple-cities.sh
```

---

## Example 8: Schedule Automatic Refresh

Use Celery to automatically refresh ballots daily:

```python
from app.tasks.ballot_refresh import schedule_ballot_refreshes_task

# This task is automatically scheduled to run daily
# via Celery Beat (see app/tasks/ballot_refresh.py)

# You can also trigger it manually:
result = schedule_ballot_refreshes_task.delay()
print(f"Task ID: {result.id}")
```

---

## Example 9: Monitor Background Jobs

Check the status of background refresh jobs:

```bash
# View active Celery tasks
celery -A app.tasks inspect active

# View scheduled tasks
celery -A app.tasks inspect scheduled

# View task results
celery -A app.tasks result <task-id>
```

---

## Example 10: Import with Specific Sources Only

If you only want to use Google Civic Information API:

```bash
python scripts/import-ballot-data.py \
  --city "Austin" \
  --state "TX" \
  --date "2024-11-05" \
  --sources google_civic
```

Or only Ballotpedia:

```bash
python scripts/import-ballot-data.py \
  --city "Austin" \
  --state "TX" \
  --date "2024-11-05" \
  --sources ballotpedia
```

---

## Example 11: Python Script for Custom Processing

```python
import asyncio
from datetime import date
from app.models.base import SessionLocal
from app.services.ballot_data_service import BallotDataService
from app.schemas.ballot_import import ImportSource

async def main():
    db = SessionLocal()
    service = BallotDataService(db)

    # Import ballot
    ballot = await service.import_ballot_by_city(
        city_name="Austin",
        state="TX",
        election_date=date(2024, 11, 5),
        sources=[ImportSource.GOOGLE_CIVIC, ImportSource.BALLOTPEDIA],
    )

    print(f"Imported ballot {ballot.id}")

    # Get candidates without email
    for contest in ballot.contests:
        for candidate in contest.candidates:
            if not candidate.email:
                print(f"Missing email: {candidate.name}")

    # Get import status
    status = await service.get_import_status(ballot.id)
    print(f"Data quality: {status['statistics']['contact_info_percentage']:.1f}%")

    db.close()

if __name__ == "__main__":
    asyncio.run(main())
```

---

## Example 12: Error Handling

```python
import asyncio
from app.services.ballot_data_service import BallotDataService
from app.models.base import SessionLocal

async def safe_import(city, state, election_date):
    db = SessionLocal()
    service = BallotDataService(db)

    try:
        ballot = await service.import_ballot_by_city(
            city_name=city,
            state=state,
            election_date=election_date,
        )
        print(f"Success: Imported {ballot.city_name}")
        return ballot

    except ValueError as e:
        print(f"Validation error: {e}")
        return None

    except Exception as e:
        print(f"Import failed: {e}")
        return None

    finally:
        db.close()

# Use it
asyncio.run(safe_import("Los Angeles", "CA", "2024-11-05"))
```

---

## Example 13: Testing in Development

Before using in production, test with a sample city:

```bash
# 1. Start services
redis-server &
./scripts/start-celery-worker.sh &

# 2. Import a small city for testing
python scripts/import-ballot-data.py \
  --city "Berkeley" \
  --state "CA" \
  --date "2024-11-05"

# 3. Check the results
curl http://localhost:8000/api/admin/ballots/1/import-status

# 4. If it looks good, publish it
curl -X POST http://localhost:8000/api/admin/ballots/1/publish
```

---

## Example 14: Production Deployment

In production, use environment variables for API keys:

```bash
# Set in your production environment
export GOOGLE_CIVIC_API_KEY="your_production_key"
export BALLOTPEDIA_API_KEY="your_production_key"

# Import via API with authentication
curl -X POST https://api.civicq.org/api/admin/ballots/import \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "city_name": "Los Angeles",
    "state": "CA",
    "election_date": "2024-11-05"
  }'
```

---

## Troubleshooting Examples

### No Data Found

```bash
# Check API keys are configured
cat backend/.env | grep API_KEY

# Test Google Civic API directly
curl "https://www.googleapis.com/civicinfo/v2/elections?key=YOUR_KEY"

# Try different data sources
python scripts/import-ballot-data.py \
  --city "Test City" \
  --state "CA" \
  --date "2024-11-05" \
  --sources ballotpedia
```

### Rate Limit Errors

```python
# If you hit rate limits, space out imports:
import time

cities = ["Los Angeles", "San Francisco", "Oakland"]

for city in cities:
    # Import city
    result = import_city(city, "CA", "2024-11-05")

    # Wait 2 seconds between imports
    time.sleep(2)
```

---

## Integration Tests

Test the full workflow:

```bash
# Test import
pytest backend/tests/test_ballot_import.py

# Test with real APIs (requires API keys)
pytest backend/tests/test_ballot_import.py --real-apis

# Test specific source
pytest backend/tests/test_ballot_import.py -k "test_google_civic"
```

---

**Questions?** Check the main documentation at `BALLOT_DATA_INTEGRATION.md`
