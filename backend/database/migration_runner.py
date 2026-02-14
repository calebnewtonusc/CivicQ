#!/usr/bin/env python3
"""
Migration Runner for CivicQ Database

Provides a comprehensive CLI for managing database migrations with safety checks,
rollback procedures, and automatic backup creation.
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional, List
import argparse

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text, inspect
from app.core.config import settings


class MigrationRunner:
    """Handles database migrations with safety checks and backups"""

    def __init__(self):
        self.db_url = settings.DATABASE_URL
        self.engine = create_engine(self.db_url)
        self.backup_dir = Path(__file__).parent / "backups"
        self.backup_dir.mkdir(exist_ok=True)

    def _run_command(self, cmd: List[str], check: bool = True) -> subprocess.CompletedProcess:
        """Run a shell command and return the result"""
        print(f"Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if check and result.returncode != 0:
            raise RuntimeError(f"Command failed with exit code {result.returncode}")

        return result

    def check_connection(self) -> bool:
        """Verify database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("Database connection: OK")
            return True
        except Exception as e:
            print(f"Database connection failed: {e}", file=sys.stderr)
            return False

    def get_current_revision(self) -> Optional[str]:
        """Get the current alembic revision"""
        result = self._run_command(["alembic", "current"], check=False)
        if result.returncode == 0 and result.stdout:
            # Parse output like "d49625079456 (head)"
            parts = result.stdout.strip().split()
            if parts:
                return parts[0]
        return None

    def get_pending_migrations(self) -> List[str]:
        """Get list of pending migrations"""
        current = self.get_current_revision()
        result = self._run_command(["alembic", "heads"], check=False)

        if result.returncode != 0:
            return []

        # Simple check: if current != head, there are pending migrations
        head = result.stdout.strip().split()[0] if result.stdout else None
        if current != head:
            return ["Migrations pending"]
        return []

    def create_backup(self, label: str = "") -> Optional[Path]:
        """Create a database backup before migration"""
        from urllib.parse import urlparse

        parsed = urlparse(self.db_url)
        db_name = parsed.path.lstrip('/')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if label:
            filename = f"{db_name}_{label}_{timestamp}.sql"
        else:
            filename = f"{db_name}_backup_{timestamp}.sql"

        backup_path = self.backup_dir / filename

        print(f"\nCreating backup: {backup_path}")

        # Build pg_dump command
        cmd = [
            "pg_dump",
            "-h", parsed.hostname or "localhost",
            "-p", str(parsed.port or 5432),
            "-U", parsed.username or "civicq",
            "-F", "p",  # Plain SQL format
            "-f", str(backup_path),
            db_name
        ]

        # Set password environment variable if provided
        env = os.environ.copy()
        if parsed.password:
            env["PGPASSWORD"] = parsed.password

        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Backup created successfully: {backup_path}")
                return backup_path
            else:
                print(f"Backup failed: {result.stderr}", file=sys.stderr)
                return None
        except FileNotFoundError:
            print("pg_dump not found. Install PostgreSQL client tools.", file=sys.stderr)
            return None

    def upgrade(self, revision: str = "head", create_backup: bool = True) -> bool:
        """Run database migrations"""
        print("\n" + "="*60)
        print("RUNNING DATABASE MIGRATIONS")
        print("="*60)

        # Check connection
        if not self.check_connection():
            return False

        # Show current state
        current = self.get_current_revision()
        print(f"\nCurrent revision: {current or 'None (empty database)'}")

        # Create backup if requested
        if create_backup:
            backup_path = self.create_backup("pre_migration")
            if not backup_path:
                response = input("\nBackup failed. Continue anyway? (yes/no): ")
                if response.lower() != "yes":
                    print("Migration aborted.")
                    return False

        # Run migration
        print(f"\nUpgrading to: {revision}")
        result = self._run_command(["alembic", "upgrade", revision], check=False)

        if result.returncode == 0:
            print("\nMigrations completed successfully!")
            new_revision = self.get_current_revision()
            print(f"New revision: {new_revision}")
            return True
        else:
            print("\nMigration failed! Database may be in inconsistent state.", file=sys.stderr)
            print("Check the error above and consider restoring from backup.", file=sys.stderr)
            return False

    def downgrade(self, revision: str = "-1") -> bool:
        """Rollback database migrations"""
        print("\n" + "="*60)
        print("ROLLING BACK DATABASE MIGRATIONS")
        print("="*60)

        # Check connection
        if not self.check_connection():
            return False

        # Show current state
        current = self.get_current_revision()
        print(f"\nCurrent revision: {current}")

        # Create mandatory backup before downgrade
        backup_path = self.create_backup("pre_rollback")
        if not backup_path:
            print("\nBackup failed. Cannot proceed with rollback without backup.", file=sys.stderr)
            return False

        # Confirm rollback
        print(f"\nThis will rollback to revision: {revision}")
        response = input("Are you sure? This operation may cause data loss! (yes/no): ")
        if response.lower() != "yes":
            print("Rollback aborted.")
            return False

        # Run rollback
        result = self._run_command(["alembic", "downgrade", revision], check=False)

        if result.returncode == 0:
            print("\nRollback completed successfully!")
            new_revision = self.get_current_revision()
            print(f"New revision: {new_revision}")
            return True
        else:
            print("\nRollback failed!", file=sys.stderr)
            print(f"Restore from backup: {backup_path}", file=sys.stderr)
            return False

    def status(self):
        """Show current migration status"""
        print("\n" + "="*60)
        print("DATABASE MIGRATION STATUS")
        print("="*60)

        # Connection check
        if not self.check_connection():
            return

        # Current revision
        current = self.get_current_revision()
        print(f"\nCurrent revision: {current or 'None (empty database)'}")

        # Pending migrations
        pending = self.get_pending_migrations()
        if pending:
            print(f"Pending migrations: {len(pending)}")
        else:
            print("Database is up to date")

        # Show migration history
        print("\nMigration history:")
        self._run_command(["alembic", "history", "--verbose"], check=False)

        # Show table count
        with self.engine.connect() as conn:
            result = conn.execute(text("""
                SELECT COUNT(*)
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """))
            count = result.fetchone()[0]
            print(f"\nTotal tables: {count}")

    def generate(self, message: str):
        """Generate a new migration"""
        print(f"\nGenerating migration: {message}")

        # Check connection
        if not self.check_connection():
            return

        # Generate migration
        result = self._run_command(
            ["alembic", "revision", "--autogenerate", "-m", message],
            check=False
        )

        if result.returncode == 0:
            print("\nMigration generated successfully!")
            print("Review the migration file before applying it.")
        else:
            print("\nMigration generation failed!", file=sys.stderr)

    def list_backups(self):
        """List all available backups"""
        print("\n" + "="*60)
        print("AVAILABLE BACKUPS")
        print("="*60)

        backups = sorted(self.backup_dir.glob("*.sql"), reverse=True)

        if not backups:
            print("\nNo backups found.")
            return

        print(f"\nFound {len(backups)} backup(s):\n")
        for backup in backups:
            size_mb = backup.stat().st_size / (1024 * 1024)
            print(f"  {backup.name:60s} {size_mb:>8.2f} MB")

    def restore_backup(self, backup_file: str):
        """Restore database from backup"""
        from urllib.parse import urlparse

        backup_path = Path(backup_file)
        if not backup_path.exists():
            # Try in backup directory
            backup_path = self.backup_dir / backup_file
            if not backup_path.exists():
                print(f"Backup file not found: {backup_file}", file=sys.stderr)
                return False

        print("\n" + "="*60)
        print(f"RESTORING FROM BACKUP: {backup_path.name}")
        print("="*60)

        # Confirm restore
        print("\nWARNING: This will replace all current database data!")
        response = input("Are you sure? (yes/no): ")
        if response.lower() != "yes":
            print("Restore aborted.")
            return False

        # Create a backup of current state before restoring
        print("\nCreating backup of current state...")
        self.create_backup("pre_restore")

        parsed = urlparse(self.db_url)
        db_name = parsed.path.lstrip('/')

        # Build psql command
        cmd = [
            "psql",
            "-h", parsed.hostname or "localhost",
            "-p", str(parsed.port or 5432),
            "-U", parsed.username or "civicq",
            "-d", db_name,
            "-f", str(backup_path)
        ]

        env = os.environ.copy()
        if parsed.password:
            env["PGPASSWORD"] = parsed.password

        try:
            result = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if result.returncode == 0:
                print("\nRestore completed successfully!")
                return True
            else:
                print(f"\nRestore failed: {result.stderr}", file=sys.stderr)
                return False
        except FileNotFoundError:
            print("psql not found. Install PostgreSQL client tools.", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(
        description="CivicQ Database Migration Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check migration status
  python migration_runner.py status

  # Run all pending migrations (with backup)
  python migration_runner.py upgrade

  # Run migrations without backup (NOT RECOMMENDED)
  python migration_runner.py upgrade --no-backup

  # Rollback last migration
  python migration_runner.py downgrade

  # Rollback to specific revision
  python migration_runner.py downgrade --revision abc123

  # Generate new migration
  python migration_runner.py generate "add user preferences table"

  # List available backups
  python migration_runner.py backups

  # Restore from backup
  python migration_runner.py restore civicq_backup_20260214_120000.sql
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Status command
    subparsers.add_parser("status", help="Show migration status")

    # Upgrade command
    upgrade_parser = subparsers.add_parser("upgrade", help="Run pending migrations")
    upgrade_parser.add_argument(
        "--revision",
        default="head",
        help="Target revision (default: head)"
    )
    upgrade_parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup creation (NOT RECOMMENDED)"
    )

    # Downgrade command
    downgrade_parser = subparsers.add_parser("downgrade", help="Rollback migrations")
    downgrade_parser.add_argument(
        "--revision",
        default="-1",
        help="Target revision (default: -1 for previous)"
    )

    # Generate command
    generate_parser = subparsers.add_parser("generate", help="Generate new migration")
    generate_parser.add_argument("message", help="Migration message")

    # Backup commands
    subparsers.add_parser("backups", help="List available backups")

    restore_parser = subparsers.add_parser("restore", help="Restore from backup")
    restore_parser.add_argument("backup_file", help="Backup file to restore")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    runner = MigrationRunner()

    try:
        if args.command == "status":
            runner.status()

        elif args.command == "upgrade":
            success = runner.upgrade(
                revision=args.revision,
                create_backup=not args.no_backup
            )
            sys.exit(0 if success else 1)

        elif args.command == "downgrade":
            success = runner.downgrade(revision=args.revision)
            sys.exit(0 if success else 1)

        elif args.command == "generate":
            runner.generate(args.message)

        elif args.command == "backups":
            runner.list_backups()

        elif args.command == "restore":
            success = runner.restore_backup(args.backup_file)
            sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
