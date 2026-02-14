# Database Quick Start Guide

## Prerequisites

1. PostgreSQL 14+ installed and running
2. pgvector extension installed
3. Python virtual environment activated
4. Dependencies installed: `pip install -r requirements.txt`

## Initial Setup

### 1. Create Database

```bash
# Using the helper script
python database/db_manager.py create

# Or manually with psql
createdb civicq
```

### 2. Install Extensions

```bash
# Using the helper script
python database/db_manager.py extensions

# Or manually with psql
psql -d civicq -c "CREATE EXTENSION vector"
```

### 3. Run Migrations

```bash
# Apply all migrations
alembic upgrade head
```

### 4. Verify Setup

```bash
# Check connection and show database info
python database/db_manager.py check

# List all tables
python database/db_manager.py tables
```

## Common Operations

### Check Migration Status

```bash
# Show current migration version
alembic current

# Show migration history
alembic history --verbose
```

### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Upgrade to specific version
alembic upgrade <revision_id>
```

### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade all (back to empty database)
alembic downgrade base
```

### Create New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Create empty migration for custom changes
alembic revision -m "Description of changes"
```

### Reset Database (Development Only)

```bash
# Drop and recreate database (WARNING: destroys all data)
python database/db_manager.py reset

# Then run migrations
alembic upgrade head
```

## Troubleshooting

### pgvector extension not found

Install pgvector:

**macOS (Homebrew):**
```bash
brew install pgvector
```

**Ubuntu/Debian:**
```bash
sudo apt-get install postgresql-14-pgvector
```

**From source:**
```bash
git clone https://github.com/pgvector/pgvector.git
cd pgvector
make
sudo make install
```

### Connection refused

Check that PostgreSQL is running:
```bash
# macOS
brew services list

# Linux
sudo systemctl status postgresql
```

Update connection settings in `.env`:
```
DATABASE_URL=postgresql://user:password@localhost:5432/civicq
```

### Permission denied

Ensure your database user has necessary permissions:
```sql
GRANT ALL PRIVILEGES ON DATABASE civicq TO your_user;
GRANT ALL ON SCHEMA public TO your_user;
```

### Migration conflicts

If you have conflicting migrations:
```bash
# Check current status
alembic current

# If needed, mark a specific version as current (use with caution)
alembic stamp <revision_id>
```

## Database Schema Overview

The CivicQ database consists of several main areas:

1. **Users & Verification** - User accounts and identity verification
2. **Ballots & Contests** - Election data, races, candidates, and measures
3. **Questions & Votes** - Voter-submitted questions and voting
4. **Answers & Rebuttals** - Candidate video responses
5. **Moderation** - Content moderation and audit logs
6. **Social Features** - User follows and notifications

See the full schema documentation in the [README.md](./migrations/README.md) file.

## Development Workflow

### Making Model Changes

1. Edit model files in `app/models/`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review generated migration file
4. Test migration: `alembic upgrade head`
5. If issues, rollback: `alembic downgrade -1`
6. Fix and repeat

### Best Practices

- Always review auto-generated migrations before applying
- Test migrations on a copy of production data
- Include both upgrade and downgrade paths
- Add comments for complex operations
- Keep migrations small and focused
- Never edit applied migrations (create new ones instead)

## Production Deployment

### Pre-deployment Checklist

- [ ] Backup production database
- [ ] Test migration in staging environment
- [ ] Review migration SQL
- [ ] Plan for potential downtime
- [ ] Have rollback plan ready

### Deployment Steps

```bash
# 1. Backup database
pg_dump civicq > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Check current version
alembic current

# 3. Apply migrations
alembic upgrade head

# 4. Verify success
python database/db_manager.py check
```

### Rollback if Needed

```bash
# Restore from backup
psql civicq < backup_YYYYMMDD_HHMMSS.sql

# Or rollback migration
alembic downgrade -1
```

## Resources

- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [pgvector Documentation](https://github.com/pgvector/pgvector)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
