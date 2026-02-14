# CivicQ Database Migrations

This directory contains Alembic database migrations for the CivicQ project.

## Setup

1. Ensure you have a PostgreSQL database running with the following extensions:
   - `pgvector` - for vector similarity search on question embeddings

2. Update the database URL in `alembic.ini` or use environment variables:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost:5432/civicq"
   ```

## Migration Files

### Initial Migration (d49625079456_initial_migration.py)

This migration creates all the core tables for CivicQ:

#### User & Verification Tables
- `users` - User accounts (voters, candidates, admins, moderators)
- `verification_records` - Identity verification records

#### Ballot & Contest Tables
- `ballots` - Election ballots for cities
- `contests` - Races and ballot measures
- `candidates` - Candidates running in races
- `measures` - Ballot measure details

#### Question & Voting Tables
- `questions` - Voter-submitted questions
- `question_versions` - Edit history for questions
- `votes` - Upvotes/downvotes on questions

#### Answer & Rebuttal Tables
- `video_answers` - Candidate video answers to questions
- `rebuttals` - Candidate rebuttals to other answers
- `claims` - Extracted claims from video answers with sources

#### Moderation Tables
- `reports` - User reports for moderation review
- `moderation_actions` - Moderation action history
- `audit_logs` - Immutable audit trail for integrity-sensitive operations

#### Social Features
- `follows` - User follows for contests, candidates, and issue tags

## Key Features

### PostgreSQL Extensions
- **pgvector**: Enables vector similarity search for question clustering and deduplication

### Indexes
- Standard B-tree indexes on foreign keys and frequently queried fields
- GIN index on `questions.issue_tags` for array searches
- IVFFlat vector index on `questions.embedding` for fast similarity search
- Unique composite indexes for preventing duplicates (e.g., one vote per user per question)

### Enum Types
All enum types are created as PostgreSQL native enums for type safety:
- `userrole`, `verificationstatus`, `verificationmethod`
- `contesttype`, `candidatestatus`
- `questionstatus`, `answerstatus`
- `reportstatus`, `reportreason`, `moderationactiontype`
- `auditeventtype`, `followtargettype`

### Foreign Key Constraints
All foreign keys include appropriate `ondelete` behavior:
- `CASCADE` - Child records deleted when parent is deleted
- `SET NULL` - Foreign key set to NULL when parent is deleted (for optional relationships)

## Running Migrations

### Apply migrations
```bash
cd backend
alembic upgrade head
```

### Check current version
```bash
alembic current
```

### View migration history
```bash
alembic history
```

### Rollback to previous version
```bash
alembic downgrade -1
```

### Rollback to specific version
```bash
alembic downgrade <revision_id>
```

## Creating New Migrations

### Auto-generate migration from model changes
```bash
alembic revision --autogenerate -m "Description of changes"
```

### Create empty migration
```bash
alembic revision -m "Description of changes"
```

After generating a migration, always review and test it before applying to production.

## Database Performance Notes

### Vector Search Configuration
The `questions.embedding` column uses IVFFlat indexing with 100 lists. This is optimized for databases with up to ~100,000 questions. For larger databases, consider:
- Increasing the number of lists (recommended: sqrt of total rows)
- Using HNSW indexing instead (better for larger datasets, requires pgvector 0.5.0+)

### Query Optimization
- The `questions` table includes indexes on frequently filtered columns: `contest_id`, `status`, `cluster_id`, `rank_score`
- The `votes` table has a unique composite index on `(user_id, question_id)` to prevent duplicate votes
- The `follows` table has a unique composite index on `(user_id, target_type, target_id, target_value)`

## Troubleshooting

### pgvector extension not found
```bash
# Install pgvector extension in PostgreSQL
# On macOS with Homebrew:
brew install pgvector

# On Ubuntu/Debian:
sudo apt-get install postgresql-14-pgvector

# Then connect to your database and enable it:
psql -d civicq -c "CREATE EXTENSION vector"
```

### Migration conflicts
If you encounter migration conflicts, you can:
1. Rollback to the last working version
2. Manually resolve conflicts in the migration file
3. Or use `alembic stamp` to mark a specific version as current (use with caution)

## Production Considerations

1. **Backup before migrations**: Always backup production data before running migrations
2. **Test in staging**: Run migrations in a staging environment first
3. **Monitor performance**: Large table alterations may lock tables temporarily
4. **Plan for downtime**: Some migrations may require brief downtime
5. **Vector index creation**: The vector index on `questions.embedding` may take time to build on large datasets
