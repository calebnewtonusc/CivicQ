# Ballot Data Integration Guide

CivicQ now supports **automatic ballot data import** from real election APIs! This means you can onboard a new city in **MINUTES** instead of manually entering ballot data.

## Overview

The ballot data integration system fetches and normalizes data from three authoritative sources:

1. **Google Civic Information API** - Most authoritative, real-time ballot data
2. **Ballotpedia API** - Comprehensive candidate information and bios
3. **VoteAmerica API** - Additional ballot and registration data

The system:
- Fetches data from multiple sources simultaneously
- Merges and deduplicates information intelligently
- Normalizes to CivicQ's data format
- Automatically refreshes data on a schedule
- Provides data quality metrics

---

## Quick Start

### 1. Get API Keys

You'll need API keys for the services you want to use:

#### Google Civic Information API (Recommended)
- Visit: https://developers.google.com/civic-information
- Enable the API in Google Cloud Console
- Create an API key
- **Free tier**: 25,000 requests/day

#### Ballotpedia API (Recommended)
- Visit: https://ballotpedia.org/API-documentation
- Request API access (may require approval)
- Best for comprehensive candidate info

#### VoteAmerica API (Optional)
- Visit: https://www.voteamerica.com/api/
- Contact them for API access
- Great for voter registration data

### 2. Configure API Keys

Add your API keys to `backend/.env`:

```bash
# External Ballot Data APIs
GOOGLE_CIVIC_API_KEY=your_google_api_key_here
BALLOTPEDIA_API_KEY=your_ballotpedia_key_here
VOTE_AMERICA_API_KEY=your_voteamerica_key_here  # Optional
```

### 3. Start Background Workers

The ballot refresh system uses Celery for background jobs:

```bash
# Terminal 1: Start Redis (required for Celery)
redis-server

# Terminal 2: Start Celery worker
cd backend
celery -A app.tasks worker --loglevel=info

# Terminal 3: Start Celery Beat (for scheduled refreshes)
celery -A app.tasks beat --loglevel=info
```

### 4. Import Ballot Data

#### Option A: Via API (Recommended)

Use the admin API endpoints to import ballot data:

```bash
# Import by city
curl -X POST http://localhost:8000/api/admin/ballots/import \
  -H "Content-Type: application/json" \
  -d '{
    "city_name": "Los Angeles",
    "state": "CA",
    "election_date": "2024-11-05",
    "sources": ["google_civic", "ballotpedia"]
  }'
```

#### Option B: Via Python Script

```python
from app.services.ballot_data_service import BallotDataService
from app.models.base import SessionLocal

db = SessionLocal()
service = BallotDataService(db)

# Import by city
ballot = await service.import_ballot_by_city(
    city_name="Los Angeles",
    state="CA",
    election_date=date(2024, 11, 5),
)

print(f"Imported {len(ballot.contests)} contests")
print(f"Ballot ID: {ballot.id}")
```

---

## API Endpoints

### Import Ballot Data

```http
POST /api/admin/ballots/import
```

**Request Body:**
```json
{
  "city_name": "Los Angeles",
  "state": "CA",
  "election_date": "2024-11-05",
  "sources": ["google_civic", "ballotpedia", "vote_america"]
}
```

**Response:**
```json
{
  "success": true,
  "ballot_id": 123,
  "city_name": "Los Angeles",
  "election_date": "2024-11-05",
  "contests_imported": 15,
  "candidates_imported": 47,
  "measures_imported": 8,
  "sources_used": ["google_civic", "ballotpedia"],
  "warnings": [],
  "errors": []
}
```

### Refresh Ballot Data

```http
POST /api/admin/ballots/{ballot_id}/refresh
```

**Request Body:**
```json
{
  "ballot_id": 123,
  "sources": ["google_civic", "ballotpedia"]
}
```

Re-fetches data from external APIs to get latest candidate info.

### Get Import Status

```http
GET /api/admin/ballots/{ballot_id}/import-status
```

**Response:**
```json
{
  "ballot_id": 123,
  "city_name": "Los Angeles",
  "election_date": "2024-11-05",
  "version": 2,
  "is_published": false,
  "last_updated": "2024-10-15T10:30:00Z",
  "sources": ["google_civic", "ballotpedia"],
  "statistics": {
    "total_contests": 15,
    "total_candidates": 47,
    "candidates_with_contact": 35,
    "candidates_verified": 12,
    "contact_info_percentage": 74.5,
    "verification_percentage": 25.5
  }
}
```

### Bulk Update Candidate Contacts

```http
POST /api/admin/ballots/{ballot_id}/update-contacts
```

**Request Body:**
```json
{
  "ballot_id": 123,
  "candidates": [
    {
      "candidate_id": 456,
      "email": "candidate@example.com",
      "phone": "+1-555-0123",
      "website": "https://example.com"
    }
  ]
}
```

Manually add contact info for candidates not available via APIs.

### Publish Ballot

```http
POST /api/admin/ballots/{ballot_id}/publish
```

Makes the ballot visible to voters on the frontend.

---

## Background Jobs

### Automatic Refresh Schedule

Ballots are automatically refreshed on this schedule:

- **Elections within 2 weeks**: Refreshed **daily**
- **Elections within 60 days**: Refreshed **weekly**
- **Past elections**: No automatic refresh

### Manual Refresh Triggers

```bash
# Refresh a specific ballot
celery -A app.tasks call tasks.refresh_ballot --args='[123]'

# Refresh all upcoming ballots
celery -A app.tasks call tasks.refresh_all_upcoming_ballots --args='[60]'
```

### Monitoring Tasks

```bash
# View active tasks
celery -A app.tasks inspect active

# View scheduled tasks
celery -A app.tasks inspect scheduled

# View task results
celery -A app.tasks inspect stats
```

---

## Data Normalization

### How Data is Merged

When multiple sources provide data for the same ballot, the system:

1. **Prioritizes by source reliability:**
   - Google Civic Information API (most authoritative)
   - Ballotpedia (best for candidate details)
   - VoteAmerica (supplementary)

2. **Merges contests by title:**
   - Matches contests with similar titles
   - Deduplicates candidates by name
   - Preserves unique data from each source

3. **Enriches candidate profiles:**
   - Combines contact info from all sources
   - Merges profile fields (bio, party, etc.)
   - Preserves the most complete data

### Data Quality Metrics

The system tracks:
- **Contact Info Coverage**: % of candidates with email/phone
- **Verification Status**: % of candidates identity-verified
- **Last Updated**: When data was last refreshed
- **Data Sources**: Which APIs provided the data

---

## City Onboarding Workflow

### Fast Track (5 Minutes)

1. **Get API keys** (one-time setup)
2. **Configure `.env`** with API keys
3. **Import ballot data** via API:
   ```bash
   curl -X POST http://localhost:8000/api/admin/ballots/import \
     -H "Content-Type: application/json" \
     -d '{
       "city_name": "Your City",
       "state": "CA",
       "election_date": "2024-11-05"
     }'
   ```
4. **Check import status** to see data quality
5. **Manually add missing contact info** (optional)
6. **Publish ballot** to make it live

### What Gets Imported Automatically

From external APIs, you'll get:
- All races and ballot measures
- Candidate names and parties
- Candidate photos (if available)
- Candidate websites and social media
- Ballot measure text and summaries
- Office names and jurisdictions

### What You May Need to Add Manually

- Candidate email addresses (privacy restrictions)
- Candidate phone numbers
- Additional candidate bio information
- Pro/con statements for measures (if not in APIs)

---

## Troubleshooting

### No Data Returned

**Problem:** API returns empty response

**Solutions:**
- Check API keys are configured correctly
- Verify election date is correct
- Try different data sources
- Check API rate limits

### Missing Candidate Contact Info

**Problem:** Candidates imported without email/phone

**Solutions:**
- APIs rarely provide contact info due to privacy
- Use bulk contact update endpoint to add manually
- Reach out to candidates directly for their info

### Data Quality Issues

**Problem:** Duplicate or incorrect candidates

**Solutions:**
- Check import status endpoint for data quality metrics
- Manually remove duplicates via admin panel
- Report data issues to the source API providers

### Background Jobs Not Running

**Problem:** Ballots not refreshing automatically

**Solutions:**
- Check Celery worker is running: `celery -A app.tasks worker`
- Check Celery Beat is running: `celery -A app.tasks beat`
- Check Redis is running: `redis-cli ping`
- View Celery logs for errors

---

## Advanced Usage

### Custom Data Sources

To add a new data source, create a client in `ballot_data_clients.py`:

```python
class CustomAPIClient:
    """Client for Custom Ballot API"""

    async def get_ballot_by_city(self, city_name: str, state: str, election_date: date):
        # Fetch data from API
        data = await self._fetch_data(city_name, state, election_date)

        # Parse and return ImportedBallot
        return self._parse_ballot_data(data)
```

### Webhook Notifications

To receive notifications when ballot data is updated:

```python
# In ballot_data_service.py
async def _create_or_update_ballot(self, imported_ballot: ImportedBallot):
    # ... existing code ...

    # Send webhook notification
    await self._notify_ballot_update(ballot)
```

### Rate Limiting

APIs have rate limits. The system handles this by:
- Caching responses (15 minutes)
- Queueing refresh jobs sequentially
- Backing off on rate limit errors

---

## API Reference

### Supported Data Sources

| Source | Best For | Rate Limit | Free Tier |
|--------|----------|------------|-----------|
| Google Civic | Real-time ballot data | 25K/day | Yes |
| Ballotpedia | Candidate bios | Varies | Limited |
| VoteAmerica | Voter registration | Unknown | Contact them |

### Data Model Mapping

| CivicQ Model | Google Civic | Ballotpedia | VoteAmerica |
|--------------|--------------|-------------|-------------|
| Ballot | Election | Election | Ballot |
| Contest | Contest | Race/Measure | Contest |
| Candidate | Candidate | Candidate | Candidate |
| Measure | Referendum | Ballot Measure | Measure |

---

## Production Considerations

### Scaling

For high-volume production:
- Use Redis cluster for Celery
- Run multiple Celery workers
- Cache API responses aggressively
- Monitor API usage and costs

### Security

- Store API keys in environment variables (never commit!)
- Use read-only API keys where possible
- Implement rate limiting on admin endpoints
- Require authentication for import endpoints

### Monitoring

Track these metrics:
- API success/failure rates
- Data quality scores over time
- Background job queue length
- API response times

---

## Support

### External API Support

- **Google Civic API**: https://developers.google.com/civic-information/docs/support
- **Ballotpedia API**: support@ballotpedia.org
- **VoteAmerica API**: Contact through their website

### CivicQ Support

For issues with the integration system:
1. Check this documentation
2. Review logs: `tail -f celery.log`
3. Open an issue on GitHub
4. Contact the maintainers

---

## Future Enhancements

Planned improvements:
- Support for more data sources (VoteSmart, etc.)
- Machine learning for candidate matching
- Automated candidate outreach emails
- Real-time data streaming
- Multi-language support

---

## License

This integration system is part of CivicQ and shares the same open-source license.

---

**Questions?** Open an issue or check the main README for more info!
