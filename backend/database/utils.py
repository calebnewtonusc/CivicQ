"""
Database Utilities

Core database helper functions for CivicQ.
Provides utilities for connection management, query optimization, and common operations.
"""

import logging
from typing import Any, Dict, List, Optional, Callable
from contextlib import contextmanager
from datetime import datetime
from sqlalchemy import text, inspect, MetaData, Table
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.models.base import SessionLocal, engine

logger = logging.getLogger(__name__)


# ============================================================================
# Session Management
# ============================================================================

@contextmanager
def get_db_session(autocommit: bool = False):
    """
    Context manager for database sessions.

    Usage:
        with get_db_session() as db:
            user = db.query(User).first()

    Args:
        autocommit: If True, automatically commit on success
    """
    session = SessionLocal()
    try:
        yield session
        if autocommit:
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        session.close()


def execute_transaction(func: Callable, *args, **kwargs) -> Any:
    """
    Execute a function within a database transaction.

    Args:
        func: Function to execute (must accept db session as first arg)
        *args: Positional arguments to pass to func
        **kwargs: Keyword arguments to pass to func

    Returns:
        Result of func execution
    """
    with get_db_session() as db:
        try:
            result = func(db, *args, **kwargs)
            db.commit()
            return result
        except Exception as e:
            db.rollback()
            logger.error(f"Transaction failed: {e}")
            raise


# ============================================================================
# Query Utilities
# ============================================================================

def execute_raw_query(query: str, params: Optional[Dict] = None) -> List[Dict]:
    """
    Execute raw SQL query and return results as list of dicts.

    Args:
        query: SQL query string
        params: Query parameters (optional)

    Returns:
        List of result rows as dictionaries
    """
    with engine.connect() as conn:
        result = conn.execute(text(query), params or {})
        if result.returns_rows:
            columns = result.keys()
            return [dict(zip(columns, row)) for row in result.fetchall()]
        return []


def bulk_insert(session: Session, model_class, data: List[Dict]) -> int:
    """
    Perform bulk insert operation.

    Args:
        session: Database session
        model_class: SQLAlchemy model class
        data: List of dictionaries with insert data

    Returns:
        Number of rows inserted
    """
    try:
        session.bulk_insert_mappings(model_class, data)
        session.commit()
        return len(data)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Bulk insert failed: {e}")
        raise


def bulk_update(session: Session, model_class, data: List[Dict]) -> int:
    """
    Perform bulk update operation.

    Args:
        session: Database session
        model_class: SQLAlchemy model class
        data: List of dictionaries with update data (must include id)

    Returns:
        Number of rows updated
    """
    try:
        session.bulk_update_mappings(model_class, data)
        session.commit()
        return len(data)
    except SQLAlchemyError as e:
        session.rollback()
        logger.error(f"Bulk update failed: {e}")
        raise


# ============================================================================
# Schema Introspection
# ============================================================================

def get_table_names() -> List[str]:
    """Get list of all table names in database."""
    inspector = inspect(engine)
    return inspector.get_table_names()


def get_table_columns(table_name: str) -> List[Dict[str, Any]]:
    """
    Get column information for a table.

    Returns:
        List of column info dictionaries
    """
    inspector = inspect(engine)
    return inspector.get_columns(table_name)


def get_table_indexes(table_name: str) -> List[Dict[str, Any]]:
    """Get index information for a table."""
    inspector = inspect(engine)
    return inspector.get_indexes(table_name)


def get_foreign_keys(table_name: str) -> List[Dict[str, Any]]:
    """Get foreign key constraints for a table."""
    inspector = inspect(engine)
    return inspector.get_foreign_keys(table_name)


def get_table_stats(table_name: str) -> Dict[str, Any]:
    """
    Get statistics for a table.

    Returns:
        Dictionary with row count, size, and other stats
    """
    query = f"""
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size,
            pg_total_relation_size(schemaname||'.'||tablename) AS size_bytes,
            n_live_tup AS row_count,
            n_dead_tup AS dead_rows,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE tablename = '{table_name}';
    """
    result = execute_raw_query(query)
    return result[0] if result else {}


def get_database_size() -> Dict[str, Any]:
    """Get total database size and statistics."""
    query = """
        SELECT
            pg_size_pretty(pg_database_size(current_database())) AS size,
            pg_database_size(current_database()) AS size_bytes,
            current_database() AS database_name
    """
    result = execute_raw_query(query)
    return result[0] if result else {}


# ============================================================================
# Index Management
# ============================================================================

def get_unused_indexes() -> List[Dict[str, Any]]:
    """
    Find indexes that are not being used.

    Returns:
        List of unused index information
    """
    query = """
        SELECT
            schemaname,
            tablename,
            indexname,
            pg_size_pretty(pg_relation_size(i.indexrelid)) AS index_size,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes i
        JOIN pg_index USING (indexrelid)
        WHERE idx_scan = 0
        AND indisunique IS FALSE
        ORDER BY pg_relation_size(i.indexrelid) DESC;
    """
    return execute_raw_query(query)


def get_missing_indexes() -> List[Dict[str, Any]]:
    """
    Suggest potentially missing indexes based on sequential scans.

    Returns:
        List of tables with high sequential scan counts
    """
    query = """
        SELECT
            schemaname,
            tablename,
            seq_scan,
            seq_tup_read,
            idx_scan,
            n_live_tup,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size
        FROM pg_stat_user_tables
        WHERE seq_scan > 0
        AND n_live_tup > 1000
        AND seq_scan > idx_scan
        ORDER BY seq_scan DESC
        LIMIT 20;
    """
    return execute_raw_query(query)


def get_index_usage() -> List[Dict[str, Any]]:
    """
    Get index usage statistics.

    Returns:
        List of index usage information
    """
    query = """
        SELECT
            schemaname,
            tablename,
            indexname,
            idx_scan,
            idx_tup_read,
            idx_tup_fetch,
            pg_size_pretty(pg_relation_size(indexrelid)) AS index_size
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
    """
    return execute_raw_query(query)


# ============================================================================
# Query Performance
# ============================================================================

def get_slow_queries(min_duration_ms: int = 1000) -> List[Dict[str, Any]]:
    """
    Get slow queries from pg_stat_statements (if available).

    Args:
        min_duration_ms: Minimum duration in milliseconds

    Returns:
        List of slow query information
    """
    query = f"""
        SELECT
            query,
            calls,
            total_exec_time,
            mean_exec_time,
            max_exec_time,
            stddev_exec_time,
            rows
        FROM pg_stat_statements
        WHERE mean_exec_time > {min_duration_ms}
        ORDER BY mean_exec_time DESC
        LIMIT 20;
    """
    try:
        return execute_raw_query(query)
    except SQLAlchemyError:
        logger.warning("pg_stat_statements extension not available")
        return []


def get_active_connections() -> List[Dict[str, Any]]:
    """
    Get information about active database connections.

    Returns:
        List of active connection information
    """
    query = """
        SELECT
            pid,
            usename,
            application_name,
            client_addr,
            state,
            query,
            query_start,
            state_change,
            wait_event_type,
            wait_event
        FROM pg_stat_activity
        WHERE state != 'idle'
        AND pid != pg_backend_pid()
        ORDER BY query_start;
    """
    return execute_raw_query(query)


def get_blocking_queries() -> List[Dict[str, Any]]:
    """
    Get information about queries blocking other queries.

    Returns:
        List of blocking query information
    """
    query = """
        SELECT
            blocked_locks.pid AS blocked_pid,
            blocked_activity.usename AS blocked_user,
            blocking_locks.pid AS blocking_pid,
            blocking_activity.usename AS blocking_user,
            blocked_activity.query AS blocked_statement,
            blocking_activity.query AS blocking_statement
        FROM pg_catalog.pg_locks blocked_locks
        JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
        JOIN pg_catalog.pg_locks blocking_locks
            ON blocking_locks.locktype = blocked_locks.locktype
            AND blocking_locks.database IS NOT DISTINCT FROM blocked_locks.database
            AND blocking_locks.relation IS NOT DISTINCT FROM blocked_locks.relation
            AND blocking_locks.page IS NOT DISTINCT FROM blocked_locks.page
            AND blocking_locks.tuple IS NOT DISTINCT FROM blocked_locks.tuple
            AND blocking_locks.virtualxid IS NOT DISTINCT FROM blocked_locks.virtualxid
            AND blocking_locks.transactionid IS NOT DISTINCT FROM blocked_locks.transactionid
            AND blocking_locks.classid IS NOT DISTINCT FROM blocked_locks.classid
            AND blocking_locks.objid IS NOT DISTINCT FROM blocked_locks.objid
            AND blocking_locks.objsubid IS NOT DISTINCT FROM blocked_locks.objsubid
            AND blocking_locks.pid != blocked_locks.pid
        JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
        WHERE NOT blocked_locks.granted;
    """
    return execute_raw_query(query)


# ============================================================================
# Cache Statistics
# ============================================================================

def get_cache_hit_ratio() -> Dict[str, Any]:
    """
    Get database cache hit ratio.

    Returns:
        Dictionary with cache statistics
    """
    query = """
        SELECT
            sum(heap_blks_read) as heap_read,
            sum(heap_blks_hit) as heap_hit,
            sum(heap_blks_hit) / nullif(sum(heap_blks_hit) + sum(heap_blks_read), 0) * 100 AS cache_hit_ratio
        FROM pg_statio_user_tables;
    """
    result = execute_raw_query(query)
    return result[0] if result else {}


def get_table_cache_stats() -> List[Dict[str, Any]]:
    """
    Get cache statistics per table.

    Returns:
        List of table cache statistics
    """
    query = """
        SELECT
            schemaname,
            tablename,
            heap_blks_read,
            heap_blks_hit,
            CASE
                WHEN heap_blks_hit + heap_blks_read = 0 THEN 0
                ELSE (heap_blks_hit::float / (heap_blks_hit + heap_blks_read)) * 100
            END AS cache_hit_ratio,
            idx_blks_read,
            idx_blks_hit,
            CASE
                WHEN idx_blks_hit + idx_blks_read = 0 THEN 0
                ELSE (idx_blks_hit::float / (idx_blks_hit + idx_blks_read)) * 100
            END AS index_cache_hit_ratio
        FROM pg_statio_user_tables
        ORDER BY heap_blks_read + heap_blks_hit DESC
        LIMIT 20;
    """
    return execute_raw_query(query)


# ============================================================================
# Vacuum and Maintenance
# ============================================================================

def get_bloat_stats() -> List[Dict[str, Any]]:
    """
    Get table bloat statistics.

    Returns:
        List of table bloat information
    """
    query = """
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
            n_live_tup,
            n_dead_tup,
            CASE
                WHEN n_live_tup = 0 THEN 0
                ELSE (n_dead_tup::float / n_live_tup) * 100
            END AS dead_tuple_percent,
            last_vacuum,
            last_autovacuum,
            last_analyze,
            last_autoanalyze
        FROM pg_stat_user_tables
        WHERE n_dead_tup > 0
        ORDER BY n_dead_tup DESC
        LIMIT 20;
    """
    return execute_raw_query(query)


# ============================================================================
# Health Checks
# ============================================================================

def health_check() -> Dict[str, Any]:
    """
    Perform comprehensive database health check.

    Returns:
        Dictionary with health check results
    """
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        # Get basic stats
        db_size = get_database_size()
        cache_ratio = get_cache_hit_ratio()
        active_conns = len(get_active_connections())

        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database_size": db_size.get("size"),
            "cache_hit_ratio": round(cache_ratio.get("cache_hit_ratio", 0), 2),
            "active_connections": active_conns,
            "connection_pool": {
                "size": engine.pool.size(),
                "checked_in": engine.pool.checkedin(),
                "checked_out": engine.pool.checkedout(),
                "overflow": engine.pool.overflow(),
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e)
        }


# ============================================================================
# Data Export/Import
# ============================================================================

def export_table_to_csv(table_name: str, output_path: str, query: Optional[str] = None):
    """
    Export table data to CSV file.

    Args:
        table_name: Name of table to export
        output_path: Path to output CSV file
        query: Optional custom query (if None, exports entire table)
    """
    import csv

    if query is None:
        query = f"SELECT * FROM {table_name}"

    with engine.connect() as conn:
        result = conn.execute(text(query))
        columns = result.keys()

        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for row in result:
                writer.writerow(dict(zip(columns, row)))

    logger.info(f"Exported {table_name} to {output_path}")


def import_csv_to_table(table_name: str, csv_path: str, truncate: bool = False):
    """
    Import CSV file to table.

    Args:
        table_name: Name of target table
        csv_path: Path to CSV file
        truncate: If True, truncate table before import
    """
    import csv

    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        data = list(reader)

    with get_db_session() as session:
        if truncate:
            session.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))

        # Get table metadata
        metadata = MetaData()
        metadata.reflect(bind=engine)
        table = metadata.tables[table_name]

        # Insert data
        session.execute(table.insert(), data)
        session.commit()

    logger.info(f"Imported {len(data)} rows to {table_name}")
