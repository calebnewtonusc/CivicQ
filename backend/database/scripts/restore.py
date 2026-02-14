#!/usr/bin/env python3
"""
Database Restore Script

Restores database from backup files.
Supports full and partial restoration.
"""

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseRestore:
    """Database restore manager"""

    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        if not self.backup_dir.exists():
            raise ValueError(f"Backup directory does not exist: {backup_dir}")

    def restore_backup(
        self,
        backup_file: str,
        clean: bool = False,
        create_db: bool = False,
        tables: Optional[list] = None
    ) -> bool:
        """
        Restore database from backup.

        Args:
            backup_file: Path to backup file
            clean: Drop existing database objects before restore
            create_db: Create database if it doesn't exist
            tables: Optional list of specific tables to restore

        Returns:
            True if successful
        """
        backup_path = self._resolve_backup_path(backup_file)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        logger.info(f"Restoring from: {backup_path}")

        # Confirm if clean restore
        if clean:
            logger.warning("WARNING: This will DROP all existing database objects!")
            response = input("Continue? (yes/no): ")
            if response.lower() != "yes":
                logger.info("Restore cancelled")
                return False

        try:
            # Build pg_restore command
            cmd = self._build_restore_command(backup_path, clean, create_db, tables)

            # Execute restore
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.info("Restore completed successfully")
            return True

        except subprocess.CalledProcessError as e:
            logger.error(f"Restore failed: {e.stderr}")
            raise

    def _resolve_backup_path(self, backup_file: str) -> Path:
        """Resolve backup file path."""
        backup_path = Path(backup_file)

        # If relative path or just filename, look in backup directory
        if not backup_path.is_absolute():
            backup_path = self.backup_dir / backup_path

        return backup_path

    def _build_restore_command(
        self,
        backup_path: Path,
        clean: bool = False,
        create_db: bool = False,
        tables: Optional[list] = None
    ) -> list:
        """Build pg_restore or psql command."""
        db_url = settings.DATABASE_URL

        # Check if backup is compressed (custom format) or plain SQL
        if backup_path.suffix == ".sql":
            # Plain SQL file - use psql
            cmd = ["psql", db_url, "-f", str(backup_path)]
        else:
            # Compressed backup - use pg_restore
            cmd = ["pg_restore", "--dbname=" + db_url]

            if clean:
                cmd.append("--clean")

            if create_db:
                cmd.append("--create")

            # Table selection
            if tables:
                for table in tables:
                    cmd.extend(["-t", table])

            # Additional options
            cmd.extend([
                "--no-owner",
                "--no-acl",
                "--verbose",
                str(backup_path)
            ])

        return cmd

    def list_backup_contents(self, backup_file: str) -> list:
        """
        List contents of a backup file.

        Args:
            backup_file: Path to backup file

        Returns:
            List of objects in backup
        """
        backup_path = self._resolve_backup_path(backup_file)

        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")

        try:
            cmd = ["pg_restore", "--list", str(backup_path)]
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            return result.stdout.splitlines()

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list backup contents: {e.stderr}")
            return []

    def verify_backup(self, backup_file: str) -> bool:
        """
        Verify backup file integrity.

        Args:
            backup_file: Path to backup file

        Returns:
            True if backup is valid
        """
        backup_path = self._resolve_backup_path(backup_file)

        if not backup_path.exists():
            return False

        # Try to list contents
        contents = self.list_backup_contents(backup_file)
        return len(contents) > 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CivicQ Database Restore")
    parser.add_argument(
        "backup_file",
        help="Backup file to restore"
    )
    parser.add_argument(
        "--dir",
        default="./backups",
        help="Backup directory (default: ./backups)"
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Drop existing database objects before restore"
    )
    parser.add_argument(
        "--create-db",
        action="store_true",
        help="Create database if it doesn't exist"
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        help="Specific tables to restore"
    )
    parser.add_argument(
        "--list-contents",
        action="store_true",
        help="List backup contents without restoring"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify backup file integrity"
    )

    args = parser.parse_args()

    # Create restore manager
    restore_manager = DatabaseRestore(backup_dir=args.dir)

    # List backup contents
    if args.list_contents:
        contents = restore_manager.list_backup_contents(args.backup_file)
        print(f"\nBackup contents:\n")
        for line in contents:
            print(f"  {line}")
        return

    # Verify backup
    if args.verify:
        is_valid = restore_manager.verify_backup(args.backup_file)
        if is_valid:
            print(f"\nBackup file is valid: {args.backup_file}")
        else:
            print(f"\nBackup file is invalid or corrupted: {args.backup_file}")
            sys.exit(1)
        return

    # Restore backup
    try:
        success = restore_manager.restore_backup(
            backup_file=args.backup_file,
            clean=args.clean,
            create_db=args.create_db,
            tables=args.tables
        )

        if success:
            print(f"\nDatabase restored successfully from: {args.backup_file}")
        else:
            sys.exit(1)

    except Exception as e:
        logger.error(f"Restore failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
