"""
Cache Helper Functions

Specialized caching utilities for specific data types and use cases.
"""

import logging
from typing import Optional, List, Dict, Any, Callable
from datetime import datetime

from app.services.cache_service import cache_service
from app.core.cache_keys import CacheKeys, CACHE_TTL_MAP

logger = logging.getLogger(__name__)


class DataCache:
    """Helper functions for caching specific data types"""

    # Ballot Data Caching

    @staticmethod
    def get_ballot(ballot_id: int) -> Optional[Dict[str, Any]]:
        """Get ballot from cache"""
        key = CacheKeys.ballot(ballot_id)
        return cache_service.get(key)

    @staticmethod
    def set_ballot(ballot_id: int, data: Dict[str, Any]):
        """Cache ballot data (1 hour TTL)"""
        key = CacheKeys.ballot(ballot_id)
        ttl = CACHE_TTL_MAP["ballot"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def invalidate_ballot(ballot_id: int):
        """Invalidate all ballot-related caches"""
        pattern = CacheKeys.pattern_ballot(ballot_id)
        cache_service.delete_pattern(pattern)
        logger.info(f"Invalidated ballot cache: {ballot_id}")

    @staticmethod
    def get_ballot_list(city_slug: str, election_date: Optional[str] = None) -> Optional[List[Dict]]:
        """Get ballot list from cache"""
        key = CacheKeys.ballot_list(city_slug, election_date)
        return cache_service.get(key)

    @staticmethod
    def set_ballot_list(city_slug: str, data: List[Dict], election_date: Optional[str] = None):
        """Cache ballot list (5 min TTL)"""
        key = CacheKeys.ballot_list(city_slug, election_date)
        ttl = CACHE_TTL_MAP["ballot_list"]
        cache_service.set(key, data, ttl=ttl)

    # Contest Caching

    @staticmethod
    def get_contest(contest_id: int) -> Optional[Dict[str, Any]]:
        """Get contest from cache"""
        key = CacheKeys.contest(contest_id)
        return cache_service.get(key)

    @staticmethod
    def set_contest(contest_id: int, data: Dict[str, Any]):
        """Cache contest data (1 hour TTL)"""
        key = CacheKeys.contest(contest_id)
        ttl = CACHE_TTL_MAP["contest"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def invalidate_contest(contest_id: int):
        """Invalidate all contest-related caches"""
        pattern = CacheKeys.pattern_contest(contest_id)
        cache_service.delete_pattern(pattern)
        logger.info(f"Invalidated contest cache: {contest_id}")

    @staticmethod
    def get_contest_list(ballot_id: int) -> Optional[List[Dict]]:
        """Get contest list from cache"""
        key = CacheKeys.contest_list(ballot_id)
        return cache_service.get(key)

    @staticmethod
    def set_contest_list(ballot_id: int, data: List[Dict]):
        """Cache contest list (5 min TTL)"""
        key = CacheKeys.contest_list(ballot_id)
        ttl = CACHE_TTL_MAP["contest_list"]
        cache_service.set(key, data, ttl=ttl)

    # Question Caching

    @staticmethod
    def get_question(question_id: int) -> Optional[Dict[str, Any]]:
        """Get question from cache"""
        key = CacheKeys.question(question_id)
        return cache_service.get(key)

    @staticmethod
    def set_question(question_id: int, data: Dict[str, Any]):
        """Cache question data (15 min TTL)"""
        key = CacheKeys.question(question_id)
        ttl = CACHE_TTL_MAP["question"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def invalidate_question(question_id: int):
        """Invalidate all question-related caches"""
        pattern = CacheKeys.pattern_question(question_id)
        cache_service.delete_pattern(pattern)
        # Also invalidate trending questions
        cache_service.delete_pattern(CacheKeys.pattern_trending())
        logger.info(f"Invalidated question cache: {question_id}")

    @staticmethod
    def get_question_list(
        contest_id: Optional[int] = None,
        page: int = 1,
        sort: str = "trending"
    ) -> Optional[List[Dict]]:
        """Get question list from cache"""
        key = CacheKeys.question_list(contest_id, page, sort)
        return cache_service.get(key)

    @staticmethod
    def set_question_list(
        data: List[Dict],
        contest_id: Optional[int] = None,
        page: int = 1,
        sort: str = "trending"
    ):
        """Cache question list (5 min TTL)"""
        key = CacheKeys.question_list(contest_id, page, sort)
        ttl = CACHE_TTL_MAP["question_list"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def get_trending_questions(
        contest_id: Optional[int] = None,
        limit: int = 20
    ) -> Optional[List[Dict]]:
        """Get trending questions from cache"""
        key = CacheKeys.trending_questions(contest_id, limit)
        return cache_service.get(key)

    @staticmethod
    def set_trending_questions(
        data: List[Dict],
        contest_id: Optional[int] = None,
        limit: int = 20
    ):
        """Cache trending questions (15 min TTL)"""
        key = CacheKeys.trending_questions(contest_id, limit)
        ttl = CACHE_TTL_MAP["trending_questions"]
        cache_service.set(key, data, ttl=ttl)

    # Candidate Caching

    @staticmethod
    def get_candidate(candidate_id: int) -> Optional[Dict[str, Any]]:
        """Get candidate from cache"""
        key = CacheKeys.candidate(candidate_id)
        return cache_service.get(key)

    @staticmethod
    def set_candidate(candidate_id: int, data: Dict[str, Any]):
        """Cache candidate profile (30 min TTL)"""
        key = CacheKeys.candidate(candidate_id)
        ttl = CACHE_TTL_MAP["candidate"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def invalidate_candidate(candidate_id: int):
        """Invalidate all candidate-related caches"""
        pattern = CacheKeys.pattern_candidate(candidate_id)
        cache_service.delete_pattern(pattern)
        logger.info(f"Invalidated candidate cache: {candidate_id}")

    @staticmethod
    def get_candidate_list(contest_id: int) -> Optional[List[Dict]]:
        """Get candidate list from cache"""
        key = CacheKeys.candidate_list(contest_id)
        return cache_service.get(key)

    @staticmethod
    def set_candidate_list(contest_id: int, data: List[Dict]):
        """Cache candidate list (30 min TTL)"""
        key = CacheKeys.candidate_list(contest_id)
        ttl = CACHE_TTL_MAP["candidate_list"]
        cache_service.set(key, data, ttl=ttl)

    # City Configuration Caching

    @staticmethod
    def get_city(city_slug: str) -> Optional[Dict[str, Any]]:
        """Get city settings from cache"""
        key = CacheKeys.city(city_slug)
        return cache_service.get(key)

    @staticmethod
    def set_city(city_slug: str, data: Dict[str, Any]):
        """Cache city settings (1 day TTL)"""
        key = CacheKeys.city(city_slug)
        ttl = CACHE_TTL_MAP["city"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def invalidate_city(city_slug: str):
        """Invalidate all city-related caches"""
        pattern = CacheKeys.pattern_city(city_slug)
        cache_service.delete_pattern(pattern)
        logger.info(f"Invalidated city cache: {city_slug}")

    @staticmethod
    def get_city_list() -> Optional[List[Dict]]:
        """Get active cities from cache"""
        key = CacheKeys.city_list()
        return cache_service.get(key)

    @staticmethod
    def set_city_list(data: List[Dict]):
        """Cache active cities (1 hour TTL)"""
        key = CacheKeys.city_list()
        ttl = CACHE_TTL_MAP["city_list"]
        cache_service.set(key, data, ttl=ttl)

    # Analytics Caching

    @staticmethod
    def get_analytics(city_slug: str, date: str) -> Optional[Dict[str, Any]]:
        """Get analytics from cache"""
        key = CacheKeys.analytics_overview(city_slug, date)
        return cache_service.get(key)

    @staticmethod
    def set_analytics(city_slug: str, date: str, data: Dict[str, Any]):
        """Cache analytics (1 hour TTL)"""
        key = CacheKeys.analytics_overview(city_slug, date)
        ttl = CACHE_TTL_MAP["analytics"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def invalidate_analytics(city_slug: Optional[str] = None):
        """Invalidate analytics caches"""
        if city_slug:
            pattern = CacheKeys.pattern_city(city_slug)
        else:
            pattern = CacheKeys.pattern_analytics()
        cache_service.delete_pattern(pattern)
        logger.info(f"Invalidated analytics cache: {city_slug or 'all'}")

    # Video Caching

    @staticmethod
    def get_video(video_id: int) -> Optional[Dict[str, Any]]:
        """Get video metadata from cache"""
        key = CacheKeys.video(video_id)
        return cache_service.get(key)

    @staticmethod
    def set_video(video_id: int, data: Dict[str, Any]):
        """Cache video metadata (1 hour TTL)"""
        key = CacheKeys.video(video_id)
        ttl = CACHE_TTL_MAP["video"]
        cache_service.set(key, data, ttl=ttl)

    @staticmethod
    def get_video_url(video_id: int, quality: str = "720p") -> Optional[str]:
        """Get video streaming URL from cache"""
        key = CacheKeys.video_url(video_id, quality)
        return cache_service.get(key)

    @staticmethod
    def set_video_url(video_id: int, url: str, quality: str = "720p"):
        """Cache video streaming URL (6 hours TTL)"""
        key = CacheKeys.video_url(video_id, quality)
        ttl = CACHE_TTL_MAP["video_url"]
        cache_service.set(key, url, ttl=ttl)


class CacheWarming:
    """Cache warming utilities for preloading frequently accessed data"""

    @staticmethod
    def warm_ballot_data(ballot_id: int, loader_func: Callable):
        """Warm ballot data cache"""
        key = CacheKeys.ballot(ballot_id)
        ttl = CACHE_TTL_MAP["ballot"]
        return cache_service.warm_cache(key, loader_func, ttl=ttl)

    @staticmethod
    def warm_trending_questions(contest_id: Optional[int], loader_func: Callable):
        """Warm trending questions cache"""
        key = CacheKeys.trending_questions(contest_id)
        ttl = CACHE_TTL_MAP["trending_questions"]
        return cache_service.warm_cache(key, loader_func, ttl=ttl)

    @staticmethod
    def warm_candidate_profiles(contest_id: int, candidate_loader: Callable):
        """Warm all candidate profiles for a contest"""
        # Get candidate list
        candidates = candidate_loader()
        if not candidates:
            return

        # Warm individual candidate caches
        items = []
        for candidate in candidates:
            candidate_id = candidate.get("id")
            if candidate_id:
                key = CacheKeys.candidate(candidate_id)
                loader = lambda c=candidate: c
                ttl = CACHE_TTL_MAP["candidate"]
                items.append((key, loader, ttl))

        return cache_service.warm_many(items)

    @staticmethod
    def warm_city_data(city_slug: str, loader_func: Callable):
        """Warm city configuration cache"""
        key = CacheKeys.city(city_slug)
        ttl = CACHE_TTL_MAP["city"]
        return cache_service.warm_cache(key, loader_func, ttl=ttl)

    @staticmethod
    def warm_contest_data(ballot_id: int, contest_loader: Callable):
        """Warm all contests for a ballot"""
        key = CacheKeys.contest_list(ballot_id)
        ttl = CACHE_TTL_MAP["contest_list"]
        return cache_service.warm_cache(key, contest_loader, ttl=ttl)


class CacheInvalidation:
    """Cache invalidation strategies for data updates"""

    @staticmethod
    def on_question_create(contest_id: int):
        """Invalidate caches when question is created"""
        # Invalidate question lists
        cache_service.delete_pattern(f"*questions:contest:{contest_id}*")
        cache_service.delete_pattern(f"*questions:all*")
        # Invalidate trending
        cache_service.delete_pattern(CacheKeys.pattern_trending())
        # Invalidate contest stats
        cache_service.delete(CacheKeys.contest_stats(contest_id))

    @staticmethod
    def on_question_update(question_id: int, contest_id: int):
        """Invalidate caches when question is updated"""
        # Invalidate specific question
        DataCache.invalidate_question(question_id)
        # Invalidate lists
        CacheInvalidation.on_question_create(contest_id)

    @staticmethod
    def on_vote_cast(question_id: int, contest_id: int):
        """Invalidate caches when vote is cast"""
        # Invalidate question
        cache_service.delete(CacheKeys.question(question_id))
        # Invalidate trending (votes affect ranking)
        cache_service.delete_pattern(CacheKeys.pattern_trending())
        # Invalidate contest stats
        cache_service.delete(CacheKeys.contest_stats(contest_id))

    @staticmethod
    def on_candidate_update(candidate_id: int, contest_id: int):
        """Invalidate caches when candidate is updated"""
        # Invalidate candidate
        DataCache.invalidate_candidate(candidate_id)
        # Invalidate candidate list
        cache_service.delete(CacheKeys.candidate_list(contest_id))

    @staticmethod
    def on_video_upload(candidate_id: int, question_id: int):
        """Invalidate caches when video response is uploaded"""
        # Invalidate candidate responses
        cache_service.delete_pattern(f"*responses:candidate:{candidate_id}*")
        # Invalidate question (now has response)
        cache_service.delete(CacheKeys.question(question_id))
        # Invalidate candidate
        cache_service.delete(CacheKeys.candidate(candidate_id))

    @staticmethod
    def on_ballot_update(ballot_id: int):
        """Invalidate caches when ballot is updated"""
        DataCache.invalidate_ballot(ballot_id)

    @staticmethod
    def on_city_settings_update(city_slug: str):
        """Invalidate caches when city settings are updated"""
        DataCache.invalidate_city(city_slug)
        # Also invalidate city list
        cache_service.delete(CacheKeys.city_list())


# Convenience functions for common operations

def cache_or_fetch(
    cache_key: str,
    loader_func: Callable,
    ttl: int = CacheKeys.TTL_5_MINUTES
) -> Any:
    """
    Get from cache or fetch and cache

    Args:
        cache_key: Cache key
        loader_func: Function to load data if not cached
        ttl: Time-to-live in seconds

    Returns:
        Cached or freshly loaded data
    """
    cached = cache_service.get(cache_key)
    if cached is not None:
        return cached

    data = loader_func()
    if data is not None:
        cache_service.set(cache_key, data, ttl=ttl)

    return data


def invalidate_related_caches(*patterns: str):
    """
    Invalidate multiple cache patterns

    Args:
        patterns: Cache key patterns to invalidate
    """
    for pattern in patterns:
        cache_service.delete_pattern(pattern)
