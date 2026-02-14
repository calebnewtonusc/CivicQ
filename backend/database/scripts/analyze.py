#!/usr/bin/env python3
"""
Database Analysis Script

Analyzes database performance, identifies issues, and provides recommendations.
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from database.utils import (
    get_table_stats,
    get_unused_indexes,
    get_missing_indexes,
    get_index_usage,
    get_cache_hit_ratio,
    get_bloat_stats,
    get_database_size
)
from database.monitoring import DatabaseMonitor

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseAnalyzer:
    """Database performance analyzer"""

    def __init__(self):
        self.monitor = DatabaseMonitor()
        self.recommendations = []

    def analyze_all(self) -> Dict[str, Any]:
        """
        Run comprehensive database analysis.

        Returns:
            Dictionary with analysis results and recommendations
        """
        logger.info("Starting comprehensive database analysis...")

        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "database_size": self.analyze_size(),
            "cache_performance": self.analyze_cache(),
            "index_analysis": self.analyze_indexes(),
            "bloat_analysis": self.analyze_bloat(),
            "connection_health": self.analyze_connections(),
            "query_performance": self.analyze_queries(),
            "recommendations": self.recommendations,
        }

        return results

    def analyze_size(self) -> Dict[str, Any]:
        """Analyze database size and growth"""
        logger.info("Analyzing database size...")

        db_size = get_database_size()

        # Check if size is concerning
        size_bytes = db_size.get("size_bytes", 0)
        size_gb = size_bytes / (1024 ** 3)

        if size_gb > 100:
            self.add_recommendation(
                "storage",
                "critical",
                f"Database size is {size_gb:.2f}GB. Consider archiving old data."
            )
        elif size_gb > 50:
            self.add_recommendation(
                "storage",
                "warning",
                f"Database size is {size_gb:.2f}GB. Monitor growth and plan for archival."
            )

        return db_size

    def analyze_cache(self) -> Dict[str, Any]:
        """Analyze cache hit ratio"""
        logger.info("Analyzing cache performance...")

        cache_stats = get_cache_hit_ratio()
        cache_ratio = cache_stats.get("cache_hit_ratio", 0)

        if cache_ratio < 90:
            self.add_recommendation(
                "cache",
                "critical",
                f"Cache hit ratio is {cache_ratio:.2f}%. Should be >95%. "
                "Consider increasing shared_buffers."
            )
        elif cache_ratio < 95:
            self.add_recommendation(
                "cache",
                "warning",
                f"Cache hit ratio is {cache_ratio:.2f}%. Could be improved."
            )

        return cache_stats

    def analyze_indexes(self) -> Dict[str, Any]:
        """Analyze index usage and recommendations"""
        logger.info("Analyzing indexes...")

        unused = get_unused_indexes()
        missing = get_missing_indexes()
        usage = get_index_usage()

        # Unused indexes
        if unused:
            total_size = sum(
                idx.get("size_bytes", 0) for idx in unused
                if "size_bytes" in idx
            )
            size_mb = total_size / (1024 ** 2)

            self.add_recommendation(
                "indexes",
                "warning",
                f"Found {len(unused)} unused indexes consuming {size_mb:.2f}MB. "
                "Consider dropping them."
            )

        # Tables with high sequential scans
        if missing:
            high_seq_scan = [
                t for t in missing
                if t.get("seq_scan", 0) > 1000 and t.get("n_live_tup", 0) > 1000
            ]

            if high_seq_scan:
                self.add_recommendation(
                    "indexes",
                    "critical",
                    f"Found {len(high_seq_scan)} tables with high sequential scans. "
                    "Review query patterns and add indexes."
                )

        return {
            "unused_indexes": unused,
            "missing_indexes_candidates": missing[:10],
            "total_indexes": len(usage),
        }

    def analyze_bloat(self) -> Dict[str, Any]:
        """Analyze table bloat"""
        logger.info("Analyzing table bloat...")

        bloat = get_bloat_stats()

        critical_bloat = [
            t for t in bloat
            if t.get("dead_tuple_percent", 0) > 30
        ]

        if critical_bloat:
            self.add_recommendation(
                "maintenance",
                "critical",
                f"Found {len(critical_bloat)} tables with >30% dead tuples. "
                "Run VACUUM immediately."
            )
        elif bloat:
            self.add_recommendation(
                "maintenance",
                "warning",
                f"Found {len(bloat)} tables with dead tuples. "
                "Consider running VACUUM."
            )

        return {
            "bloated_tables": bloat[:10],
            "critical_count": len(critical_bloat),
        }

    def analyze_connections(self) -> Dict[str, Any]:
        """Analyze connection health"""
        logger.info("Analyzing connections...")

        conn_stats = self.monitor.get_connection_stats()
        pool_stats = self.monitor.check_connection_pool()

        # Check for idle in transaction
        idle_in_trans = conn_stats.get("idle_in_transaction", 0)
        if idle_in_trans > 5:
            self.add_recommendation(
                "connections",
                "warning",
                f"Found {idle_in_trans} idle in transaction connections. "
                "Check application code for uncommitted transactions."
            )

        # Check pool utilization
        utilization = pool_stats.get("utilization_percent", 0)
        if utilization > 80:
            self.add_recommendation(
                "connections",
                "critical",
                f"Connection pool utilization is {utilization:.1f}%. "
                "Consider increasing pool size."
            )

        return {
            "connection_stats": conn_stats,
            "pool_stats": pool_stats,
        }

    def analyze_queries(self) -> Dict[str, Any]:
        """Analyze query performance"""
        logger.info("Analyzing query performance...")

        slow_queries = self.monitor.check_slow_queries(threshold_ms=1000)
        locks = self.monitor.check_locks()

        if slow_queries:
            self.add_recommendation(
                "performance",
                "warning",
                f"Found {len(slow_queries)} queries running >1 second. "
                "Review and optimize slow queries."
            )

        if locks.get("total_blocking", 0) > 0:
            self.add_recommendation(
                "performance",
                "critical",
                f"Found {locks['total_blocking']} blocking queries. "
                "Investigate lock contention."
            )

        return {
            "slow_query_count": len(slow_queries),
            "slow_queries": slow_queries[:5],
            "locks": locks,
        }

    def add_recommendation(self, category: str, severity: str, message: str):
        """Add a recommendation"""
        self.recommendations.append({
            "category": category,
            "severity": severity,
            "message": message,
        })

    def print_report(self, results: Dict[str, Any]):
        """Print human-readable analysis report"""
        print("\n" + "=" * 80)
        print("DATABASE ANALYSIS REPORT")
        print("=" * 80)
        print(f"Generated: {results['timestamp']}")
        print()

        # Database Size
        print("DATABASE SIZE")
        print("-" * 80)
        size = results["database_size"]
        print(f"  Total Size: {size.get('size', 'N/A')}")
        print()

        # Cache Performance
        print("CACHE PERFORMANCE")
        print("-" * 80)
        cache = results["cache_performance"]
        print(f"  Cache Hit Ratio: {cache.get('cache_hit_ratio', 0):.2f}%")
        print(f"  Index Cache Hit Ratio: {cache.get('index_cache_hit_ratio', 0):.2f}%")
        print()

        # Index Analysis
        print("INDEX ANALYSIS")
        print("-" * 80)
        idx = results["index_analysis"]
        print(f"  Total Indexes: {idx.get('total_indexes', 0)}")
        print(f"  Unused Indexes: {len(idx.get('unused_indexes', []))}")
        print(f"  Tables Needing Indexes: {len(idx.get('missing_indexes_candidates', []))}")
        print()

        # Bloat Analysis
        print("BLOAT ANALYSIS")
        print("-" * 80)
        bloat = results["bloat_analysis"]
        print(f"  Bloated Tables: {len(bloat.get('bloated_tables', []))}")
        print(f"  Critical Bloat: {bloat.get('critical_count', 0)}")
        print()

        # Connection Health
        print("CONNECTION HEALTH")
        print("-" * 80)
        conn = results["connection_health"]["connection_stats"]
        pool = results["connection_health"]["pool_stats"]
        print(f"  Total Connections: {conn.get('total_connections', 0)}")
        print(f"  Active: {conn.get('active', 0)}")
        print(f"  Idle: {conn.get('idle', 0)}")
        print(f"  Pool Utilization: {pool.get('utilization_percent', 0):.1f}%")
        print()

        # Query Performance
        print("QUERY PERFORMANCE")
        print("-" * 80)
        queries = results["query_performance"]
        print(f"  Slow Queries: {queries.get('slow_query_count', 0)}")
        print(f"  Blocking Queries: {queries['locks'].get('total_blocking', 0)}")
        print()

        # Recommendations
        print("RECOMMENDATIONS")
        print("-" * 80)
        if not results["recommendations"]:
            print("  No issues found. Database is healthy!")
        else:
            for rec in results["recommendations"]:
                severity_icon = {
                    "critical": "[CRITICAL]",
                    "warning": "[WARNING]",
                    "info": "[INFO]"
                }
                icon = severity_icon.get(rec["severity"], "")
                print(f"  {icon} {rec['category']}: {rec['message']}")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="CivicQ Database Analysis")
    parser.add_argument(
        "--output",
        help="Output file for JSON results (optional)"
    )
    parser.add_argument(
        "--json-only",
        action="store_true",
        help="Output JSON only (no report)"
    )

    args = parser.parse_args()

    # Run analysis
    analyzer = DatabaseAnalyzer()
    results = analyzer.analyze_all()

    # Print report
    if not args.json_only:
        analyzer.print_report(results)

    # Save JSON output
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        logger.info(f"Results saved to {args.output}")

    # Print JSON if json-only
    if args.json_only:
        print(json.dumps(results, indent=2, default=str))

    # Exit with error code if critical recommendations
    critical_count = sum(
        1 for r in results["recommendations"]
        if r["severity"] == "critical"
    )

    if critical_count > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
