#!/usr/bin/env python3
"""
Database Backup Script

Creates full database backups with compression and optional encryption.
Supports local and remote storage (S3, etc.).
"""

import os
import sys
import argparse
import logging
import subprocess
from datetime import datetime
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


class DatabaseBackup:
    """Database backup manager"""

    def __init__(
        self,
        backup_dir: str = "./backups",
        compress: bool = True,
        include_schema: bool = True,
        include_data: bool = True
    ):
        self.backup_dir = Path(backup_dir)
        self.compress = compress
        self.include_schema = include_schema
        self.include_data = include_data
        self.backup_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(
        self,
        backup_name: Optional[str] = None,
        tables: Optional[list] = None
    ) -> Path:
        """
        Create database backup.

        Args:
            backup_name: Custom backup name (default: timestamp)
            tables: Optional list of specific tables to backup

        Returns:
            Path to backup file
        """
        if backup_name is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_name = f"civicq_backup_{timestamp}"

        # Determine file extension
        extension = ".sql.gz" if self.compress else ".sql"
        backup_path = self.backup_dir / f"{backup_name}{extension}"

        logger.info(f"Creating backup: {backup_path}")

        try:
            # Build pg_dump command
            cmd = self._build_dump_command(backup_path, tables)

            # Execute backup
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            # Get backup size
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            logger.info(f"Backup created successfully: {backup_path} ({size_mb:.2f} MB)")

            # Create metadata file
            self._create_metadata(backup_path, tables)

            return backup_path

        except subprocess.CalledProcessError as e:
            logger.error(f"Backup failed: {e.stderr}")
            if backup_path.exists():
                backup_path.unlink()
            raise

    def _build_dump_command(self, backup_path: Path, tables: Optional[list] = None) -> list:
        """Build pg_dump command."""
        # Parse database URL
        db_url = settings.DATABASE_URL
        # Format: postgresql://user:password@host:port/database

        cmd = ["pg_dump", db_url]

        # Schema and data options
        if not self.include_schema:
            cmd.append("--data-only")
        if not self.include_data:
            cmd.append("--schema-only")

        # Table selection
        if tables:
            for table in tables:
                cmd.extend(["-t", table])

        # Additional options
        cmd.extend([
            "--no-owner",
            "--no-acl",
            "--verbose",
        ])

        # Compression
        if self.compress:
            cmd.append("--compress=9")
            cmd.extend(["-f", str(backup_path)])
        else:
            cmd.extend(["-f", str(backup_path)])

        return cmd

    def _create_metadata(self, backup_path: Path, tables: Optional[list] = None):
        """Create metadata file for backup."""
        metadata_path = backup_path.with_suffix(backup_path.suffix + ".meta")

        metadata = {
            "backup_date": datetime.now().isoformat(),
            "database_url": settings.DATABASE_URL.split("@")[-1],  # Remove credentials
            "backup_size": backup_path.stat().st_size,
            "compressed": self.compress,
            "include_schema": self.include_schema,
            "include_data": self.include_data,
            "tables": tables or "all"
        }

        with open(metadata_path, 'w') as f:
            import json
            json.dump(metadata, f, indent=2)

    def list_backups(self) -> list:
        """List all available backups."""
        backups = []
        for backup_file in self.backup_dir.glob("*.sql*"):
            if backup_file.suffix in [".sql", ".gz"]:
                size_mb = backup_file.stat().st_size / (1024 * 1024)
                mtime = datetime.fromtimestamp(backup_file.stat().st_mtime)

                backups.append({
                    "name": backup_file.name,
                    "path": str(backup_file),
                    "size_mb": round(size_mb, 2),
                    "created": mtime.isoformat()
                })

        return sorted(backups, key=lambda x: x["created"], reverse=True)

    def cleanup_old_backups(self, keep_count: int = 10):
        """
        Remove old backups, keeping only the most recent ones.

        Args:
            keep_count: Number of backups to keep
        """
        backups = self.list_backups()

        if len(backups) <= keep_count:
            logger.info(f"Found {len(backups)} backups, no cleanup needed")
            return

        to_delete = backups[keep_count:]
        logger.info(f"Deleting {len(to_delete)} old backups")

        for backup in to_delete:
            backup_path = Path(backup["path"])
            logger.info(f"Deleting: {backup_path.name}")
            backup_path.unlink()

            # Delete metadata if exists
            meta_path = backup_path.with_suffix(backup_path.suffix + ".meta")
            if meta_path.exists():
                meta_path.unlink()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CivicQ Database Backup")
    parser.add_argument(
        "--name",
        help="Custom backup name (default: timestamp)"
    )
    parser.add_argument(
        "--dir",
        default="./backups",
        help="Backup directory (default: ./backups)"
    )
    parser.add_argument(
        "--no-compress",
        action="store_true",
        help="Disable compression"
    )
    parser.add_argument(
        "--schema-only",
        action="store_true",
        help="Backup schema only (no data)"
    )
    parser.add_argument(
        "--data-only",
        action="store_true",
        help="Backup data only (no schema)"
    )
    parser.add_argument(
        "--tables",
        nargs="+",
        help="Specific tables to backup"
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List existing backups"
    )
    parser.add_argument(
        "--cleanup",
        type=int,
        metavar="N",
        help="Keep only N most recent backups"
    )

    args = parser.parse_args()

    # Create backup manager
    backup_manager = DatabaseBackup(
        backup_dir=args.dir,
        compress=not args.no_compress,
        include_schema=not args.data_only,
        include_data=not args.schema_only
    )

    # List backups
    if args.list:
        backups = backup_manager.list_backups()
        print(f"\nFound {len(backups)} backups:\n")
        for backup in backups:
            print(f"  {backup['name']:50} {backup['size_mb']:8.2f} MB  {backup['created']}")
        return

    # Cleanup old backups
    if args.cleanup:
        backup_manager.cleanup_old_backups(keep_count=args.cleanup)
        return

    # Create backup
    try:
        backup_path = backup_manager.create_backup(
            backup_name=args.name,
            tables=args.tables
        )
        print(f"\nBackup created successfully: {backup_path}")
    except Exception as e:
        logger.error(f"Backup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
