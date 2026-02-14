"""
Database Monitoring and Performance Tracking

Real-time monitoring, alerting, and performance metrics for CivicQ database.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
from sqlalchemy import text
from app.models.base import engine
from database.utils import execute_raw_query

logger = logging.getLogger(__name__)


class AlertLevel(str, Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Database alert"""
    level: AlertLevel
    category: str
    message: str
    details: Dict[str, Any]
    timestamp: datetime


class DatabaseMonitor:
    """
    Database monitoring and alerting system.

    Monitors connection pools, query performance, locks, bloat, and more.
    """

    def __init__(self):
        self.alerts: List[Alert] = []
        self.metrics: Dict[str, Any] = {}

    # ========================================================================
    # Connection Monitoring
    # ========================================================================

    def check_connection_pool(self) -> Dict[str, Any]:
        """
        Monitor connection pool health.

        Returns:
            Dictionary with pool statistics and health status
        """
        pool = engine.pool
        stats = {
            "pool_size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "max_overflow": getattr(pool, "_max_overflow", None),
            "total_connections": pool.checkedin() + pool.checkedout(),
            "utilization_percent": 0
        }

        # Calculate utilization
        if pool.size() > 0:
            stats["utilization_percent"] = (
                stats["checked_out"] / pool.size() * 100
            )

        # Check for alerts
        if stats["utilization_percent"] > 80:
            self.add_alert(
                AlertLevel.WARNING,
                "connection_pool",
                "Connection pool utilization high",
                {"utilization": stats["utilization_percent"]}
            )

        if stats["overflow"] > 0:
            self.add_alert(
                AlertLevel.WARNING,
                "connection_pool",
                "Connection pool overflow in use",
                {"overflow": stats["overflow"]}
            )

        return stats

    def get_connection_stats(self) -> Dict[str, Any]:
        """
        Get detailed connection statistics from PostgreSQL.

        Returns:
            Dictionary with connection statistics
        """
        query = """
            SELECT
                count(*) as total_connections,
                count(*) FILTER (WHERE state = 'active') as active,
                count(*) FILTER (WHERE state = 'idle') as idle,
                count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction,
                count(*) FILTER (WHERE wait_event_type IS NOT NULL) as waiting,
                max(EXTRACT(EPOCH FROM (now() - query_start))) as max_query_duration,
                max(EXTRACT(EPOCH FROM (now() - state_change))) as max_idle_duration
            FROM pg_stat_activity
            WHERE pid != pg_backend_pid();
        """
        result = execute_raw_query(query)
        stats = result[0] if result else {}

        # Check for long-running connections
        if stats.get("max_query_duration", 0) > 300:  # 5 minutes
            self.add_alert(
                AlertLevel.WARNING,
                "connections",
                "Long-running query detected",
                {"duration_seconds": stats["max_query_duration"]}
            )

        # Check for idle in transaction
        if stats.get("idle_in_transaction", 0) > 5:
            self.add_alert(
                AlertLevel.WARNING,
                "connections",
                "Multiple idle in transaction connections",
                {"count": stats["idle_in_transaction"]}
            )

        return stats

    # ========================================================================
    # Query Performance Monitoring
    # ========================================================================

    def check_slow_queries(self, threshold_ms: int = 1000) -> List[Dict[str, Any]]:
        """
        Check for slow queries.

        Args:
            threshold_ms: Threshold in milliseconds for slow queries

        Returns:
            List of slow queries
        """
        query = f"""
            SELECT
                pid,
                usename,
                application_name,
                client_addr,
                query_start,
                EXTRACT(EPOCH FROM (now() - query_start)) * 1000 as duration_ms,
                state,
                wait_event_type,
                wait_event,
                substring(query, 1, 200) as query_preview
            FROM pg_stat_activity
            WHERE state = 'active'
            AND query_start < now() - interval '{threshold_ms} milliseconds'
            AND pid != pg_backend_pid()
            ORDER BY query_start;
        """
        slow_queries = execute_raw_query(query)

        if slow_queries:
            self.add_alert(
                AlertLevel.WARNING,
                "performance",
                f"Found {len(slow_queries)} slow queries",
                {"count": len(slow_queries), "threshold_ms": threshold_ms}
            )

        return slow_queries

    def check_locks(self) -> Dict[str, Any]:
        """
        Check for database locks and blocking queries.

        Returns:
            Dictionary with lock information
        """
        # Get lock counts
        lock_query = """
            SELECT
                mode,
                locktype,
                count(*) as count
            FROM pg_locks
            WHERE NOT granted
            GROUP BY mode, locktype
            ORDER BY count DESC;
        """
        locks = execute_raw_query(lock_query)

        # Get blocking queries
        blocking_query = """
            SELECT
                bl.pid AS blocked_pid,
                ka.query AS blocked_query,
                ka.state AS blocked_state,
                ka.usename AS blocked_user,
                bl.mode AS blocked_mode,
                a.pid AS blocking_pid,
                ka2.query AS blocking_query,
                ka2.state AS blocking_state,
                ka2.usename AS blocking_user,
                l.mode AS blocking_mode,
                EXTRACT(EPOCH FROM (now() - ka.query_start)) as blocked_duration
            FROM pg_catalog.pg_locks bl
            JOIN pg_catalog.pg_stat_activity ka ON bl.pid = ka.pid
            JOIN pg_catalog.pg_locks l ON bl.locktype = l.locktype
                AND bl.database IS NOT DISTINCT FROM l.database
                AND bl.relation IS NOT DISTINCT FROM l.relation
                AND bl.page IS NOT DISTINCT FROM l.page
                AND bl.tuple IS NOT DISTINCT FROM l.tuple
                AND bl.virtualxid IS NOT DISTINCT FROM l.virtualxid
                AND bl.transactionid IS NOT DISTINCT FROM l.transactionid
                AND bl.classid IS NOT DISTINCT FROM l.classid
                AND bl.objid IS NOT DISTINCT FROM l.objid
                AND bl.objsubid IS NOT DISTINCT FROM l.objsubid
                AND bl.pid != l.pid
            JOIN pg_catalog.pg_stat_activity ka2 ON l.pid = ka2.pid
            WHERE NOT bl.granted
            AND ka.pid != pg_backend_pid();
        """
        blocking = execute_raw_query(blocking_query)

        result = {
            "lock_counts": locks,
            "blocking_queries": blocking,
            "total_locks": sum(lock["count"] for lock in locks) if locks else 0,
            "total_blocking": len(blocking)
        }

        if result["total_blocking"] > 0:
            self.add_alert(
                AlertLevel.CRITICAL,
                "locks",
                f"{result['total_blocking']} blocking queries detected",
                {"blocking_queries": result["total_blocking"]}
            )

        return result

    # ========================================================================
    # Table Health Monitoring
    # ========================================================================

    def check_table_bloat(self, threshold_percent: float = 20.0) -> List[Dict[str, Any]]:
        """
        Check for table bloat.

        Args:
            threshold_percent: Threshold for bloat alert (dead tuple %)

        Returns:
            List of tables with significant bloat
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
                last_autovacuum
            FROM pg_stat_user_tables
            WHERE n_live_tup > 0
            AND (n_dead_tup::numeric / n_live_tup) * 100 > {threshold_percent}
            ORDER BY n_dead_tup DESC;
        """
        bloated_tables = execute_raw_query(query)

        if bloated_tables:
            self.add_alert(
                AlertLevel.WARNING,
                "maintenance",
                f"{len(bloated_tables)} tables need vacuuming",
                {
                    "count": len(bloated_tables),
                    "tables": [t["tablename"] for t in bloated_tables[:5]]
                }
            )

        return bloated_tables

    def check_index_usage(self) -> List[Dict[str, Any]]:
        """
        Check for unused indexes.

        Returns:
            List of unused indexes
        """
        query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch,
                pg_size_pretty(pg_relation_size(indexrelid)) as index_size,
                pg_relation_size(indexrelid) as size_bytes
            FROM pg_stat_user_indexes
            WHERE idx_scan = 0
            AND schemaname NOT IN ('pg_catalog', 'information_schema')
            AND indexrelid NOT IN (
                SELECT indexrelid FROM pg_index WHERE indisunique OR indisprimary
            )
            ORDER BY pg_relation_size(indexrelid) DESC;
        """
        unused_indexes = execute_raw_query(query)

        if unused_indexes:
            total_size = sum(idx["size_bytes"] for idx in unused_indexes)
            self.add_alert(
                AlertLevel.INFO,
                "optimization",
                f"{len(unused_indexes)} unused indexes found",
                {
                    "count": len(unused_indexes),
                    "total_size_bytes": total_size
                }
            )

        return unused_indexes

    # ========================================================================
    # Cache Performance Monitoring
    # ========================================================================

    def check_cache_hit_ratio(self, threshold_percent: float = 90.0) -> Dict[str, Any]:
        """
        Check cache hit ratio.

        Args:
            threshold_percent: Minimum acceptable cache hit ratio

        Returns:
            Dictionary with cache statistics
        """
        query = """
            SELECT
                sum(heap_blks_read) as heap_read,
                sum(heap_blks_hit) as heap_hit,
                CASE
                    WHEN sum(heap_blks_hit) + sum(heap_blks_read) = 0 THEN 100
                    ELSE ROUND((sum(heap_blks_hit)::numeric /
                        nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100, 2)
                END as cache_hit_ratio,
                sum(idx_blks_read) as idx_read,
                sum(idx_blks_hit) as idx_hit,
                CASE
                    WHEN sum(idx_blks_hit) + sum(idx_blks_read) = 0 THEN 100
                    ELSE ROUND((sum(idx_blks_hit)::numeric /
                        nullif(sum(idx_blks_hit) + sum(idx_blks_read), 0)) * 100, 2)
                END as index_cache_hit_ratio
            FROM pg_statio_user_tables;
        """
        result = execute_raw_query(query)
        stats = result[0] if result else {}

        cache_ratio = stats.get("cache_hit_ratio", 0)
        if cache_ratio < threshold_percent:
            self.add_alert(
                AlertLevel.WARNING,
                "performance",
                f"Cache hit ratio below threshold: {cache_ratio}%",
                {"cache_hit_ratio": cache_ratio, "threshold": threshold_percent}
            )

        return stats

    # ========================================================================
    # Replication Monitoring (if applicable)
    # ========================================================================

    def check_replication_lag(self, threshold_seconds: int = 60) -> Optional[Dict[str, Any]]:
        """
        Check replication lag (if replication is configured).

        Args:
            threshold_seconds: Maximum acceptable lag in seconds

        Returns:
            Dictionary with replication statistics or None if no replication
        """
        query = """
            SELECT
                client_addr,
                state,
                sync_state,
                EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp())) as lag_seconds
            FROM pg_stat_replication;
        """
        try:
            replicas = execute_raw_query(query)
            if not replicas:
                return None

            for replica in replicas:
                lag = replica.get("lag_seconds", 0)
                if lag and lag > threshold_seconds:
                    self.add_alert(
                        AlertLevel.CRITICAL,
                        "replication",
                        f"Replication lag on {replica['client_addr']}: {lag}s",
                        {"lag_seconds": lag, "threshold": threshold_seconds}
                    )

            return {
                "replica_count": len(replicas),
                "replicas": replicas,
                "max_lag": max((r.get("lag_seconds", 0) for r in replicas), default=0)
            }
        except Exception as e:
            logger.debug(f"Replication monitoring not available: {e}")
            return None

    # ========================================================================
    # Disk Space Monitoring
    # ========================================================================

    def check_disk_usage(self, threshold_percent: float = 80.0) -> Dict[str, Any]:
        """
        Check disk space usage.

        Args:
            threshold_percent: Threshold for disk usage alert

        Returns:
            Dictionary with disk usage statistics
        """
        query = """
            SELECT
                pg_database_size(current_database()) as size_bytes,
                pg_size_pretty(pg_database_size(current_database())) as size
        """
        result = execute_raw_query(query)
        stats = result[0] if result else {}

        # Get tablespace size
        tablespace_query = """
            SELECT
                spcname,
                pg_size_pretty(pg_tablespace_size(spcname)) as size,
                pg_tablespace_size(spcname) as size_bytes
            FROM pg_tablespace;
        """
        stats["tablespaces"] = execute_raw_query(tablespace_query)

        return stats

    # ========================================================================
    # Alert Management
    # ========================================================================

    def add_alert(self, level: AlertLevel, category: str, message: str, details: Dict[str, Any]):
        """Add an alert to the alert list."""
        alert = Alert(
            level=level,
            category=category,
            message=message,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.alerts.append(alert)
        logger.log(
            logging.WARNING if level == AlertLevel.WARNING else logging.ERROR,
            f"[{category}] {message}: {details}"
        )

    def get_alerts(self, level: Optional[AlertLevel] = None) -> List[Alert]:
        """
        Get alerts, optionally filtered by level.

        Args:
            level: Optional alert level filter

        Returns:
            List of alerts
        """
        if level:
            return [a for a in self.alerts if a.level == level]
        return self.alerts

    def clear_alerts(self):
        """Clear all alerts."""
        self.alerts = []

    # ========================================================================
    # Comprehensive Health Check
    # ========================================================================

    def run_health_check(self) -> Dict[str, Any]:
        """
        Run comprehensive database health check.

        Returns:
            Dictionary with all health check results
        """
        self.clear_alerts()
        start_time = time.time()

        try:
            results = {
                "timestamp": datetime.utcnow().isoformat(),
                "connection_pool": self.check_connection_pool(),
                "connection_stats": self.get_connection_stats(),
                "slow_queries": self.check_slow_queries(),
                "locks": self.check_locks(),
                "table_bloat": self.check_table_bloat(),
                "unused_indexes": self.check_index_usage(),
                "cache_performance": self.check_cache_hit_ratio(),
                "replication": self.check_replication_lag(),
                "disk_usage": self.check_disk_usage(),
                "alerts": [
                    {
                        "level": a.level.value,
                        "category": a.category,
                        "message": a.message,
                        "details": a.details,
                        "timestamp": a.timestamp.isoformat()
                    }
                    for a in self.alerts
                ],
                "duration_seconds": time.time() - start_time,
                "status": "healthy" if not any(a.level == AlertLevel.CRITICAL for a in self.alerts) else "degraded"
            }

            return results

        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "status": "error",
                "error": str(e),
                "duration_seconds": time.time() - start_time
            }


# ============================================================================
# Query Performance Tracker
# ============================================================================

class QueryPerformanceTracker:
    """
    Track query performance over time.

    Use as context manager to automatically track query execution time.
    """

    def __init__(self, query_name: str):
        self.query_name = query_name
        self.start_time = None
        self.end_time = None
        self.duration = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time

        # Log slow queries
        if self.duration > 1.0:  # 1 second threshold
            logger.warning(
                f"Slow query detected: {self.query_name} took {self.duration:.2f}s"
            )

        # Could also send to metrics system here
        logger.debug(f"Query {self.query_name} completed in {self.duration:.4f}s")


# ============================================================================
# Utility Functions
# ============================================================================

def get_database_metrics() -> Dict[str, Any]:
    """
    Get comprehensive database metrics.

    Returns:
        Dictionary with various database metrics
    """
    monitor = DatabaseMonitor()
    return monitor.run_health_check()


def export_metrics_prometheus() -> str:
    """
    Export metrics in Prometheus format.

    Returns:
        String with Prometheus-formatted metrics
    """
    metrics = get_database_metrics()
    lines = []

    # Connection pool metrics
    pool = metrics.get("connection_pool", {})
    lines.append(f"# HELP civicq_db_pool_size Database connection pool size")
    lines.append(f"# TYPE civicq_db_pool_size gauge")
    lines.append(f"civicq_db_pool_size {pool.get('pool_size', 0)}")

    lines.append(f"# HELP civicq_db_connections_checked_out Checked out connections")
    lines.append(f"# TYPE civicq_db_connections_checked_out gauge")
    lines.append(f"civicq_db_connections_checked_out {pool.get('checked_out', 0)}")

    # Cache hit ratio
    cache = metrics.get("cache_performance", {})
    lines.append(f"# HELP civicq_db_cache_hit_ratio Cache hit ratio percentage")
    lines.append(f"# TYPE civicq_db_cache_hit_ratio gauge")
    lines.append(f"civicq_db_cache_hit_ratio {cache.get('cache_hit_ratio', 0)}")

    # Active connections
    conn_stats = metrics.get("connection_stats", {})
    lines.append(f"# HELP civicq_db_active_connections Active database connections")
    lines.append(f"# TYPE civicq_db_active_connections gauge")
    lines.append(f"civicq_db_active_connections {conn_stats.get('active', 0)}")

    return "\n".join(lines)
