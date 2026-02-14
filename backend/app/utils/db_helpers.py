"""
Database Query Optimization Helpers

Utilities for optimizing database queries, reducing N+1 queries,
and improving database performance at scale.
"""

import logging
from typing import List, Type, Any, Optional
from sqlalchemy import func, select
from sqlalchemy.orm import Session, joinedload, selectinload, subqueryload
from contextlib import contextmanager

from app.utils.performance_monitoring import measure_db_query

logger = logging.getLogger(__name__)


class QueryOptimizer:
    """Database query optimization utilities"""

    @staticmethod
    def eager_load_relationships(query, *relationships):
        """
        Eager load relationships to avoid N+1 queries

        Args:
            query: SQLAlchemy query
            *relationships: Relationship attributes to load

        Returns:
            Optimized query

        Example:
            query = QueryOptimizer.eager_load_relationships(
                db.query(Question),
                Question.user,
                Question.contest,
                Question.votes
            )
        """
        for relationship in relationships:
            query = query.options(joinedload(relationship))
        return query

    @staticmethod
    def select_in_load(query, *relationships):
        """
        Use SELECT IN loading for one-to-many relationships

        Better than joined load for collections.

        Args:
            query: SQLAlchemy query
            *relationships: Collection relationships to load

        Returns:
            Optimized query
        """
        for relationship in relationships:
            query = query.options(selectinload(relationship))
        return query

    @staticmethod
    def defer_columns(query, *columns):
        """
        Defer loading of large columns until accessed

        Args:
            query: SQLAlchemy query
            *columns: Columns to defer

        Returns:
            Optimized query

        Example:
            # Don't load description field unless needed
            query = QueryOptimizer.defer_columns(
                db.query(Question),
                Question.description,
                Question.metadata
            )
        """
        from sqlalchemy.orm import defer
        for column in columns:
            query = query.options(defer(column))
        return query

    @staticmethod
    def load_only(query, *columns):
        """
        Load only specific columns

        Args:
            query: SQLAlchemy query
            *columns: Columns to load

        Returns:
            Optimized query
        """
        from sqlalchemy.orm import load_only
        query = query.options(load_only(*columns))
        return query

    @staticmethod
    def batch_fetch(session: Session, model: Type, ids: List[int], batch_size: int = 100):
        """
        Fetch multiple records by ID in batches

        Args:
            session: Database session
            model: SQLAlchemy model
            ids: List of record IDs
            batch_size: Batch size

        Returns:
            List of records

        Example:
            questions = QueryOptimizer.batch_fetch(
                db,
                Question,
                [1, 2, 3, ..., 1000]
            )
        """
        results = []
        for i in range(0, len(ids), batch_size):
            batch_ids = ids[i:i + batch_size]
            batch_results = session.query(model).filter(
                model.id.in_(batch_ids)
            ).all()
            results.extend(batch_results)

        return results

    @staticmethod
    def count_efficiently(query):
        """
        Get count more efficiently than query.count()

        Args:
            query: SQLAlchemy query

        Returns:
            Count of records
        """
        with measure_db_query("count"):
            count_query = query.statement.with_only_columns([func.count()]).order_by(None)
            return query.session.execute(count_query).scalar()

    @staticmethod
    def paginate_efficiently(
        query,
        page: int = 1,
        per_page: int = 20,
        max_per_page: int = 100
    ):
        """
        Paginate query results efficiently

        Args:
            query: SQLAlchemy query
            page: Page number (1-indexed)
            per_page: Items per page
            max_per_page: Maximum items per page

        Returns:
            Tuple of (items, total, has_next, has_prev)
        """
        # Limit per_page
        per_page = min(per_page, max_per_page)

        # Get total count efficiently
        total = QueryOptimizer.count_efficiently(query)

        # Calculate pagination
        offset = (page - 1) * per_page
        has_next = offset + per_page < total
        has_prev = page > 1

        # Fetch page
        with measure_db_query("select"):
            items = query.limit(per_page).offset(offset).all()

        return items, total, has_next, has_prev


class BulkOperations:
    """Bulk database operations for better performance"""

    @staticmethod
    def bulk_insert(session: Session, model: Type, data: List[dict]):
        """
        Bulk insert records

        Args:
            session: Database session
            model: SQLAlchemy model
            data: List of dictionaries with record data

        Example:
            BulkOperations.bulk_insert(
                db,
                Vote,
                [
                    {"user_id": 1, "question_id": 1, "vote_type": "upvote"},
                    {"user_id": 2, "question_id": 1, "vote_type": "upvote"},
                    ...
                ]
            )
        """
        with measure_db_query("insert"):
            session.bulk_insert_mappings(model, data)
            session.commit()

    @staticmethod
    def bulk_update(session: Session, model: Type, data: List[dict]):
        """
        Bulk update records

        Args:
            session: Database session
            model: SQLAlchemy model
            data: List of dictionaries with record data (must include id)

        Example:
            BulkOperations.bulk_update(
                db,
                Question,
                [
                    {"id": 1, "vote_count": 150},
                    {"id": 2, "vote_count": 120},
                    ...
                ]
            )
        """
        with measure_db_query("update"):
            session.bulk_update_mappings(model, data)
            session.commit()

    @staticmethod
    def bulk_delete(session: Session, model: Type, ids: List[int]):
        """
        Bulk delete records by ID

        Args:
            session: Database session
            model: SQLAlchemy model
            ids: List of record IDs
        """
        with measure_db_query("delete"):
            session.query(model).filter(model.id.in_(ids)).delete(
                synchronize_session=False
            )
            session.commit()


class IndexHelpers:
    """Database index management and analysis"""

    @staticmethod
    def check_index_usage(session: Session, table_name: str):
        """
        Check index usage statistics for a table

        Args:
            session: Database session
            table_name: Name of the table

        Returns:
            List of index usage statistics
        """
        query = """
            SELECT
                schemaname,
                tablename,
                indexname,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_stat_user_indexes
            WHERE tablename = :table_name
            ORDER BY idx_scan DESC;
        """

        result = session.execute(query, {"table_name": table_name})
        return result.fetchall()

    @staticmethod
    def find_missing_indexes(session: Session):
        """
        Find potentially missing indexes

        Returns:
            List of suggestions for missing indexes
        """
        query = """
            SELECT
                schemaname,
                tablename,
                attname as column_name,
                n_distinct,
                correlation
            FROM pg_stats
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
              AND n_distinct > 100  -- Column has many distinct values
              AND correlation < 0.5  -- Not well-correlated with physical order
            ORDER BY n_distinct DESC
            LIMIT 20;
        """

        result = session.execute(query)
        return result.fetchall()

    @staticmethod
    def analyze_slow_queries(session: Session, min_duration_ms: int = 100):
        """
        Get slow query statistics

        Requires pg_stat_statements extension.

        Args:
            session: Database session
            min_duration_ms: Minimum query duration in milliseconds

        Returns:
            List of slow queries
        """
        query = """
            SELECT
                query,
                calls,
                total_time,
                mean_time,
                max_time
            FROM pg_stat_statements
            WHERE mean_time > :min_duration
            ORDER BY mean_time DESC
            LIMIT 20;
        """

        try:
            result = session.execute(
                query,
                {"min_duration": min_duration_ms}
            )
            return result.fetchall()
        except Exception as e:
            logger.warning(
                f"Could not analyze slow queries. "
                f"Ensure pg_stat_statements is enabled: {e}"
            )
            return []


class ConnectionPoolMonitor:
    """Monitor database connection pool"""

    @staticmethod
    def get_pool_status(engine):
        """
        Get connection pool status

        Args:
            engine: SQLAlchemy engine

        Returns:
            Dictionary with pool statistics
        """
        pool = engine.pool

        return {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "overflow_size": pool._overflow,
            "max_overflow": pool._max_overflow,
            "usage_percent": (pool.checkedout() / (pool.size() + pool._max_overflow)) * 100
        }

    @staticmethod
    def log_pool_status(engine):
        """Log connection pool status"""
        status = ConnectionPoolMonitor.get_pool_status(engine)

        logger.info(
            f"DB Pool Status: "
            f"{status['checked_out']}/{status['size']} connections used, "
            f"{status['overflow']} overflow, "
            f"{status['usage_percent']:.1f}% utilization"
        )

        # Warn if pool is nearly exhausted
        if status['usage_percent'] > 90:
            logger.warning(
                f"Connection pool nearly exhausted! "
                f"Consider increasing pool size or max overflow."
            )


# Context managers for optimized queries

@contextmanager
def optimized_query(session: Session, model: Type, *eager_load):
    """
    Context manager for optimized queries

    Args:
        session: Database session
        model: SQLAlchemy model
        *eager_load: Relationships to eager load

    Usage:
        with optimized_query(db, Question, Question.user, Question.contest) as query:
            questions = query.filter(Question.status == 'active').all()
    """
    query = session.query(model)

    # Apply eager loading
    for relationship in eager_load:
        query = query.options(joinedload(relationship))

    try:
        yield query
    finally:
        pass


# Decorators for query optimization

def with_eager_loading(*relationships):
    """
    Decorator to automatically eager load relationships

    Args:
        *relationships: Relationships to eager load

    Usage:
        @with_eager_loading(Question.user, Question.contest)
        def get_questions(db: Session):
            return db.query(Question).all()
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Execute original function
            result = func(*args, **kwargs)

            # If result is a query, apply eager loading
            if hasattr(result, 'options'):
                for relationship in relationships:
                    result = result.options(joinedload(relationship))

            return result

        return wrapper
    return decorator


# Query performance analyzer

class QueryAnalyzer:
    """Analyze and explain query performance"""

    @staticmethod
    def explain_query(session: Session, query, analyze: bool = False):
        """
        Get EXPLAIN output for a query

        Args:
            session: Database session
            query: SQLAlchemy query
            analyze: Whether to run EXPLAIN ANALYZE (actually executes query)

        Returns:
            EXPLAIN output as string
        """
        from sqlalchemy.dialects import postgresql

        # Compile query to SQL
        compiled = query.statement.compile(
            dialect=postgresql.dialect(),
            compile_kwargs={"literal_binds": True}
        )

        sql = str(compiled)

        # Add EXPLAIN
        if analyze:
            explain_query = f"EXPLAIN (ANALYZE, BUFFERS) {sql}"
        else:
            explain_query = f"EXPLAIN {sql}"

        # Execute EXPLAIN
        result = session.execute(explain_query)
        return "\n".join([row[0] for row in result])

    @staticmethod
    def log_slow_query_warning(query, duration_ms: float, threshold_ms: float = 100):
        """
        Log warning for slow queries

        Args:
            query: SQLAlchemy query
            duration_ms: Query duration in milliseconds
            threshold_ms: Threshold for slow query warning
        """
        if duration_ms > threshold_ms:
            logger.warning(
                f"Slow query detected ({duration_ms:.2f}ms): "
                f"{query.statement}"
            )
