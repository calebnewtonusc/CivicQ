"""
Cache Key Management

Centralized cache key definitions for consistent caching patterns.
All cache keys follow the pattern: {prefix}:{entity}:{identifier}
"""

from typing import Optional


class CacheKeys:
    """Cache key generator with consistent naming patterns"""

    # Cache key prefixes
    PREFIX = "civicq"

    # TTL values (in seconds)
    TTL_1_MINUTE = 60
    TTL_5_MINUTES = 300
    TTL_15_MINUTES = 900
    TTL_30_MINUTES = 1800
    TTL_1_HOUR = 3600
    TTL_6_HOURS = 21600
    TTL_1_DAY = 86400
    TTL_1_WEEK = 604800

    # Ballot Data Keys
    @staticmethod
    def ballot(ballot_id: int) -> str:
        """Cache key for ballot data (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:ballot:{ballot_id}"

    @staticmethod
    def ballot_list(city_slug: str, election_date: Optional[str] = None) -> str:
        """Cache key for ballot list (TTL: 5 minutes)"""
        if election_date:
            return f"{CacheKeys.PREFIX}:ballots:{city_slug}:{election_date}"
        return f"{CacheKeys.PREFIX}:ballots:{city_slug}:all"

    @staticmethod
    def contest(contest_id: int) -> str:
        """Cache key for contest data (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:contest:{contest_id}"

    @staticmethod
    def contest_list(ballot_id: int) -> str:
        """Cache key for contest list (TTL: 5 minutes)"""
        return f"{CacheKeys.PREFIX}:contests:ballot:{ballot_id}"

    # Question Keys
    @staticmethod
    def question(question_id: int) -> str:
        """Cache key for single question (TTL: 15 minutes)"""
        return f"{CacheKeys.PREFIX}:question:{question_id}"

    @staticmethod
    def question_list(
        contest_id: Optional[int] = None,
        page: int = 1,
        sort: str = "trending"
    ) -> str:
        """Cache key for question list (TTL: 5 minutes)"""
        if contest_id:
            return f"{CacheKeys.PREFIX}:questions:contest:{contest_id}:page:{page}:sort:{sort}"
        return f"{CacheKeys.PREFIX}:questions:all:page:{page}:sort:{sort}"

    @staticmethod
    def trending_questions(contest_id: Optional[int] = None, limit: int = 20) -> str:
        """Cache key for trending questions (TTL: 15 minutes)"""
        if contest_id:
            return f"{CacheKeys.PREFIX}:trending:contest:{contest_id}:limit:{limit}"
        return f"{CacheKeys.PREFIX}:trending:all:limit:{limit}"

    @staticmethod
    def question_count(contest_id: int) -> str:
        """Cache key for question count (TTL: 5 minutes)"""
        return f"{CacheKeys.PREFIX}:question_count:contest:{contest_id}"

    # Candidate Keys
    @staticmethod
    def candidate(candidate_id: int) -> str:
        """Cache key for candidate profile (TTL: 30 minutes)"""
        return f"{CacheKeys.PREFIX}:candidate:{candidate_id}"

    @staticmethod
    def candidate_list(contest_id: int) -> str:
        """Cache key for candidate list (TTL: 30 minutes)"""
        return f"{CacheKeys.PREFIX}:candidates:contest:{contest_id}"

    @staticmethod
    def candidate_responses(candidate_id: int, page: int = 1) -> str:
        """Cache key for candidate's video responses (TTL: 15 minutes)"""
        return f"{CacheKeys.PREFIX}:responses:candidate:{candidate_id}:page:{page}"

    # City Configuration Keys
    @staticmethod
    def city(city_slug: str) -> str:
        """Cache key for city settings (TTL: 1 day)"""
        return f"{CacheKeys.PREFIX}:city:{city_slug}"

    @staticmethod
    def city_list() -> str:
        """Cache key for active cities (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:cities:active"

    # Analytics Keys
    @staticmethod
    def analytics_overview(city_slug: str, date: str) -> str:
        """Cache key for analytics overview (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:analytics:{city_slug}:{date}"

    @staticmethod
    def user_engagement(user_id: int, date: str) -> str:
        """Cache key for user engagement metrics (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:engagement:user:{user_id}:{date}"

    @staticmethod
    def contest_stats(contest_id: int) -> str:
        """Cache key for contest statistics (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:stats:contest:{contest_id}"

    # User/Session Keys
    @staticmethod
    def user(user_id: int) -> str:
        """Cache key for user data (TTL: 15 minutes)"""
        return f"{CacheKeys.PREFIX}:user:{user_id}"

    @staticmethod
    def user_profile(user_id: int) -> str:
        """Cache key for user profile (TTL: 30 minutes)"""
        return f"{CacheKeys.PREFIX}:profile:user:{user_id}"

    @staticmethod
    def user_votes(user_id: int) -> str:
        """Cache key for user's votes (TTL: 5 minutes)"""
        return f"{CacheKeys.PREFIX}:votes:user:{user_id}"

    # Video Keys
    @staticmethod
    def video(video_id: int) -> str:
        """Cache key for video metadata (TTL: 1 hour)"""
        return f"{CacheKeys.PREFIX}:video:{video_id}"

    @staticmethod
    def video_url(video_id: int, quality: str = "720p") -> str:
        """Cache key for video streaming URL (TTL: 6 hours)"""
        return f"{CacheKeys.PREFIX}:video_url:{video_id}:{quality}"

    # API Response Keys
    @staticmethod
    def api_response(path: str, query_params: str = "") -> str:
        """Cache key for API response (TTL: varies by endpoint)"""
        clean_path = path.strip("/").replace("/", ":")
        if query_params:
            return f"{CacheKeys.PREFIX}:api:{clean_path}:{query_params}"
        return f"{CacheKeys.PREFIX}:api:{clean_path}"

    # Invalidation pattern keys (for batch invalidation)
    @staticmethod
    def pattern_ballot(ballot_id: int) -> str:
        """Pattern to invalidate all ballot-related caches"""
        return f"{CacheKeys.PREFIX}:*ballot*{ballot_id}*"

    @staticmethod
    def pattern_contest(contest_id: int) -> str:
        """Pattern to invalidate all contest-related caches"""
        return f"{CacheKeys.PREFIX}:*contest*{contest_id}*"

    @staticmethod
    def pattern_candidate(candidate_id: int) -> str:
        """Pattern to invalidate all candidate-related caches"""
        return f"{CacheKeys.PREFIX}:*candidate*{candidate_id}*"

    @staticmethod
    def pattern_question(question_id: int) -> str:
        """Pattern to invalidate all question-related caches"""
        return f"{CacheKeys.PREFIX}:*question*{question_id}*"

    @staticmethod
    def pattern_city(city_slug: str) -> str:
        """Pattern to invalidate all city-related caches"""
        return f"{CacheKeys.PREFIX}:*{city_slug}*"

    @staticmethod
    def pattern_trending() -> str:
        """Pattern to invalidate all trending data"""
        return f"{CacheKeys.PREFIX}:trending:*"

    @staticmethod
    def pattern_analytics() -> str:
        """Pattern to invalidate all analytics data"""
        return f"{CacheKeys.PREFIX}:analytics:*"


# TTL mapping for different cache types
CACHE_TTL_MAP = {
    "ballot": CacheKeys.TTL_1_HOUR,
    "ballot_list": CacheKeys.TTL_5_MINUTES,
    "contest": CacheKeys.TTL_1_HOUR,
    "contest_list": CacheKeys.TTL_5_MINUTES,
    "question": CacheKeys.TTL_15_MINUTES,
    "question_list": CacheKeys.TTL_5_MINUTES,
    "trending_questions": CacheKeys.TTL_15_MINUTES,
    "candidate": CacheKeys.TTL_30_MINUTES,
    "candidate_list": CacheKeys.TTL_30_MINUTES,
    "city": CacheKeys.TTL_1_DAY,
    "city_list": CacheKeys.TTL_1_HOUR,
    "analytics": CacheKeys.TTL_1_HOUR,
    "video": CacheKeys.TTL_1_HOUR,
    "video_url": CacheKeys.TTL_6_HOURS,
}
