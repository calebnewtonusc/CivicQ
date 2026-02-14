#!/usr/bin/env python3
"""
Database Vacuum Script

Performs VACUUM operations to reclaim space and update statistics.
Supports full, analyze, and table-specific vacuum operations.
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import text
from app.models.base import engine
from database.utils import execute_raw_query, get_table_names

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseVacuum:
    """Database vacuum manager"""

    def vacuum_table(
        self,
        table_name: str,
        full: bool = False,
        analyze: bool = True,
        verbose: bool = True
    ):
        """
        Vacuum a specific table.

        Args:
            table_name: Name of table to vacuum
            full: Perform VACUUM FULL (locks table, reclaims more space)
            analyze: Also run ANALYZE to update statistics
            verbose: Show detailed progress
        """
        options = []
        if full:
            options.append("FULL")
        if analyze:
            options.append("ANALYZE")
        if verbose:
            options.append("VERBOSE")

        vacuum_cmd = f"VACUUM {' '.join(options)} {table_name}"

        logger.info(f"Running: {vacuum_cmd}")

        try:
            # VACUUM cannot run in a transaction block
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                conn.execute(text(vacuum_cmd))

            logger.info(f"Vacuum completed for {table_name}")

        except Exception as e:
            logger.error(f"Vacuum failed for {table_name}: {e}")
            raise

    def vacuum_all_tables(
        self,
        full: bool = False,
        analyze: bool = True,
        exclude_tables: Optional[List[str]] = None
    ):
        """
        Vacuum all tables in database.

        Args:
            full: Perform VACUUM FULL
            analyze: Also run ANALYZE
            exclude_tables: List of tables to skip
        """
        exclude_tables = exclude_tables or []
        tables = get_table_names()

        logger.info(f"Found {len(tables)} tables to vacuum")

        for table in tables:
            if table in exclude_tables:
                logger.info(f"Skipping {table} (excluded)")
                continue

            try:
                self.vacuum_table(table, full=full, analyze=analyze, verbose=False)
            except Exception as e:
                logger.error(f"Failed to vacuum {table}: {e}")
                # Continue with other tables

    def vacuum_database(self, full: bool = False, analyze: bool = True):
        """
        Vacuum entire database.

        Args:
            full: Perform VACUUM FULL
            analyze: Also run ANALYZE
        """
        options = []
        if full:
            options.append("FULL")
        if analyze:
            options.append("ANALYZE")
        options.append("VERBOSE")

        vacuum_cmd = f"VACUUM {' '.join(options)}"

        logger.info(f"Running: {vacuum_cmd}")

        try:
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                conn.execute(text(vacuum_cmd))

            logger.info("Database vacuum completed")

        except Exception as e:
            logger.error(f"Database vacuum failed: {e}")
            raise

    def analyze_table(self, table_name: str, verbose: bool = True):
        """
        Run ANALYZE on a specific table to update statistics.

        Args:
            table_name: Name of table to analyze
            verbose: Show detailed progress
        """
        analyze_cmd = f"ANALYZE {'VERBOSE' if verbose else ''} {table_name}"

        logger.info(f"Running: {analyze_cmd}")

        try:
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as conn:
                conn.execute(text(analyze_cmd))

            logger.info(f"Analyze completed for {table_name}")

        except Exception as e:
            logger.error(f"Analyze failed for {table_name}: {e}")
            raise

    def get_vacuum_candidates(self, threshold_percent: float = 20.0) -> List[dict]:
        """
        Get tables that need vacuuming based on dead tuple percentage.

        Args:
            threshold_percent: Minimum dead tuple percentage to recommend vacuum

        Returns:
            List of tables with vacuum recommendations
        """
        query = f"""
            SELECT
                schemaname,
                tablename,
                n_live_tup,
                n_dead_tup,
                CASE
                    WHEN n_live_tup = 0 THEN 0
                    ELSE ROUND((n_dead_tup::numeric / n_live_tup) * 100, 2)
                END as dead_tuple_percent,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze
            FROM pg_stat_user_tables
            WHERE n_live_tup > 0
            AND (n_dead_tup::numeric / n_live_tup) * 100 > {threshold_percent}
            ORDER BY n_dead_tup DESC;
        """

        return execute_raw_query(query)

    def get_autovacuum_stats(self) -> List[dict]:
        """
        Get autovacuum statistics for all tables.

        Returns:
            List of autovacuum statistics
        """
        query = """
            SELECT
                schemaname,
                tablename,
                last_vacuum,
                last_autovacuum,
                last_analyze,
                last_autoanalyze,
                vacuum_count,
                autovacuum_count,
                analyze_count,
                autoanalyze_count,
                n_tup_ins,
                n_tup_upd,
                n_tup_del,
                n_live_tup,
                n_dead_tup
            FROM pg_stat_user_tables
            ORDER BY last_autovacuum DESC NULLS LAST;
        """

        return execute_raw_query(query)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="CivicQ Database Vacuum")
    parser.add_argument(
        "--table",
        help="Specific table to vacuum (if not specified, vacuums all tables)"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Perform VACUUM FULL (locks table, reclaims more space)"
    )
    parser.add_argument(
        "--no-analyze",
        action="store_true",
        help="Skip ANALYZE (only vacuum)"
    )
    parser.add_argument(
        "--analyze-only",
        action="store_true",
        help="Only run ANALYZE (no vacuum)"
    )
    parser.add_argument(
        "--candidates",
        action="store_true",
        help="Show tables that need vacuuming"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=20.0,
        help="Dead tuple percentage threshold for candidates (default: 20.0)"
    )
    parser.add_argument(
        "--stats",
        action="store_true",
        help="Show autovacuum statistics"
    )
    parser.add_argument(
        "--auto-vacuum",
        action="store_true",
        help="Automatically vacuum tables that exceed threshold"
    )

    args = parser.parse_args()

    vacuum_manager = DatabaseVacuum()

    # Show vacuum candidates
    if args.candidates:
        candidates = vacuum_manager.get_vacuum_candidates(threshold=args.threshold)
        print(f"\nTables needing vacuum (>{args.threshold}% dead tuples):\n")

        if not candidates:
            print("  No tables need vacuuming")
        else:
            for table in candidates:
                print(f"  {table['tablename']:30} "
                      f"Dead: {table['dead_tuple_percent']:6.2f}%  "
                      f"Size: {table['total_size']:10}  "
                      f"Last vacuum: {table['last_vacuum'] or table['last_autovacuum'] or 'Never'}")
        return

    # Show autovacuum stats
    if args.stats:
        stats = vacuum_manager.get_autovacuum_stats()
        print(f"\nAutovacuum Statistics:\n")

        for table in stats[:20]:  # Show top 20
            print(f"  {table['tablename']:30} "
                  f"Autovacuum: {table['autovacuum_count']:4}  "
                  f"Last: {table['last_autovacuum'] or 'Never'}")
        return

    # Auto vacuum based on threshold
    if args.auto_vacuum:
        candidates = vacuum_manager.get_vacuum_candidates(threshold=args.threshold)
        if not candidates:
            print("No tables need vacuuming")
            return

        print(f"\nFound {len(candidates)} tables to vacuum\n")
        for table in candidates:
            try:
                vacuum_manager.vacuum_table(
                    table['tablename'],
                    full=args.full,
                    analyze=not args.no_analyze
                )
            except Exception as e:
                logger.error(f"Failed to vacuum {table['tablename']}: {e}")
        return

    # Analyze only
    if args.analyze_only:
        if args.table:
            vacuum_manager.analyze_table(args.table)
        else:
            logger.error("--table required with --analyze-only")
            sys.exit(1)
        return

    # Vacuum specific table or all tables
    try:
        if args.table:
            vacuum_manager.vacuum_table(
                args.table,
                full=args.full,
                analyze=not args.no_analyze
            )
            print(f"\nVacuum completed for table: {args.table}")
        else:
            vacuum_manager.vacuum_database(
                full=args.full,
                analyze=not args.no_analyze
            )
            print("\nDatabase vacuum completed")

    except Exception as e:
        logger.error(f"Vacuum failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
