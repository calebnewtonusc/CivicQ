#!/usr/bin/env python3
"""
Database Management CLI

Helper script for common database operations in CivicQ.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings


def create_database():
    """Create the database if it doesn't exist"""
    # Parse database URL to get database name
    from urllib.parse import urlparse
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip('/')

    # Connect to postgres database to create our database
    base_url = f"{parsed.scheme}://{parsed.netloc}/postgres"
    engine = create_engine(base_url)

    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # Check if database exists
        result = conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        )
        exists = result.fetchone()

        if not exists:
            print(f"Creating database '{db_name}'...")
            conn.execute(text(f'CREATE DATABASE "{db_name}"'))
            print(f"Database '{db_name}' created successfully!")
        else:
            print(f"Database '{db_name}' already exists.")

    engine.dispose()


def drop_database():
    """Drop the database (WARNING: destructive!)"""
    from urllib.parse import urlparse
    parsed = urlparse(settings.DATABASE_URL)
    db_name = parsed.path.lstrip('/')

    response = input(f"Are you sure you want to drop database '{db_name}'? This cannot be undone! (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return

    # Connect to postgres database to drop our database
    base_url = f"{parsed.scheme}://{parsed.netloc}/postgres"
    engine = create_engine(base_url)

    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        # Terminate existing connections
        conn.execute(
            text(f"""
                SELECT pg_terminate_backend(pg_stat_activity.pid)
                FROM pg_stat_activity
                WHERE pg_stat_activity.datname = '{db_name}'
                AND pid <> pg_backend_pid()
            """)
        )

        # Drop database
        print(f"Dropping database '{db_name}'...")
        conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
        print(f"Database '{db_name}' dropped successfully!")

    engine.dispose()


def reset_database():
    """Drop and recreate the database"""
    drop_database()
    create_database()
    print("\nDatabase reset complete. Don't forget to run migrations:")
    print("  alembic upgrade head")


def install_extensions():
    """Install required PostgreSQL extensions"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        conn.execution_options(isolation_level="AUTOCOMMIT")

        print("Installing pgvector extension...")
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        print("Extensions installed successfully!")

    engine.dispose()


def check_connection():
    """Check database connection and show info"""
    try:
        engine = create_engine(settings.DATABASE_URL)

        with engine.connect() as conn:
            # Get PostgreSQL version
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"PostgreSQL version: {version.split(',')[0]}")

            # Check for pgvector extension
            result = conn.execute(
                text("SELECT installed_version FROM pg_available_extensions WHERE name = 'vector'")
            )
            pgvector = result.fetchone()
            if pgvector and pgvector[0]:
                print(f"pgvector extension: installed (version {pgvector[0]})")
            else:
                print("pgvector extension: NOT INSTALLED (required for question clustering)")

            # Get database size
            from urllib.parse import urlparse
            db_name = urlparse(settings.DATABASE_URL).path.lstrip('/')
            result = conn.execute(
                text(f"SELECT pg_size_pretty(pg_database_size('{db_name}'))")
            )
            size = result.fetchone()[0]
            print(f"Database size: {size}")

            # Get table count
            result = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                """)
            )
            table_count = result.fetchone()[0]
            print(f"Tables: {table_count}")

            print("\nConnection successful!")

        engine.dispose()
        return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False


def list_tables():
    """List all tables in the database"""
    engine = create_engine(settings.DATABASE_URL)

    with engine.connect() as conn:
        result = conn.execute(
            text("""
                SELECT table_name,
                       pg_size_pretty(pg_total_relation_size(quote_ident(table_name)::regclass)) as size
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """)
        )

        print("\nTables in database:")
        print("-" * 60)
        for row in result:
            print(f"  {row[0]:<30} {row[1]:>20}")
        print("-" * 60)

    engine.dispose()


def main():
    parser = argparse.ArgumentParser(
        description='CivicQ Database Management CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python db_manager.py create          # Create database
  python db_manager.py drop            # Drop database
  python db_manager.py reset           # Drop and recreate database
  python db_manager.py extensions      # Install required extensions
  python db_manager.py check           # Check connection and show info
  python db_manager.py tables          # List all tables
        """
    )

    parser.add_argument(
        'command',
        choices=['create', 'drop', 'reset', 'extensions', 'check', 'tables'],
        help='Command to execute'
    )

    args = parser.parse_args()

    commands = {
        'create': create_database,
        'drop': drop_database,
        'reset': reset_database,
        'extensions': install_extensions,
        'check': check_connection,
        'tables': list_tables,
    }

    try:
        commands[args.command]()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
