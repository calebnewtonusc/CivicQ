"""
CivicQ Load Testing with Locust

Simulates realistic user behavior across all major application flows.
Tests system performance under load with 10,000+ concurrent users.

Usage:
    # Web UI (recommended)
    locust -f load_tests/locustfile.py --host=http://localhost:8000

    # Headless mode
    locust -f load_tests/locustfile.py --host=http://localhost:8000 \
           --users 1000 --spawn-rate 10 --run-time 10m --headless

    # Distributed load testing
    # Master:
    locust -f load_tests/locustfile.py --master --expect-workers 4
    # Workers (run on multiple machines):
    locust -f load_tests/locustfile.py --worker --master-host=<master-ip>
"""

import random
import json
from locust import HttpUser, TaskSet, task, between, events
from locust.exception import RescheduleTask


class BrowseQuestionsTask(TaskSet):
    """Users browsing and voting on questions"""

    def on_start(self):
        """Initialize user session"""
        self.contest_id = random.randint(1, 10)
        self.user_id = random.randint(1, 10000)

    @task(10)
    def view_ballot(self):
        """View ballot for city"""
        city_slug = random.choice(["los-angeles", "san-francisco", "san-diego", "oakland"])
        with self.client.get(
            f"/api/ballots/{city_slug}",
            catch_response=True,
            name="/api/ballots/[city]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load ballot: {response.status_code}")

    @task(15)
    def browse_questions(self):
        """Browse paginated question list"""
        page = random.randint(1, 5)
        sort = random.choice(["trending", "recent", "top"])

        with self.client.get(
            f"/api/questions?contest_id={self.contest_id}&page={page}&sort={sort}",
            catch_response=True,
            name="/api/questions?contest_id=[id]&page=[n]&sort=[type]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load questions: {response.status_code}")

    @task(8)
    def view_question_detail(self):
        """View individual question"""
        question_id = random.randint(1, 1000)

        with self.client.get(
            f"/api/questions/{question_id}",
            catch_response=True,
            name="/api/questions/[id]"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 404:
                # Not found is acceptable (question may not exist)
                response.success()
            else:
                response.failure(f"Failed to load question: {response.status_code}")

    @task(5)
    def view_trending_questions(self):
        """View trending questions"""
        with self.client.get(
            f"/api/questions/trending?contest_id={self.contest_id}&limit=20",
            catch_response=True,
            name="/api/questions/trending?contest_id=[id]"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load trending: {response.status_code}")

    @task(12)
    def vote_on_question(self):
        """Vote on a question"""
        question_id = random.randint(1, 1000)

        # Simulate authenticated user vote
        with self.client.post(
            f"/api/questions/{question_id}/vote",
            json={"vote_type": "upvote"},
            catch_response=True,
            name="/api/questions/[id]/vote"
        ) as response:
            # Accept both success and auth failures (since we're not fully authenticated)
            if response.status_code in [200, 201, 401, 403]:
                response.success()
            else:
                response.failure(f"Vote failed: {response.status_code}")


class CandidatePortalTask(TaskSet):
    """Candidates viewing and responding to questions"""

    def on_start(self):
        """Initialize candidate session"""
        self.candidate_id = random.randint(1, 50)
        self.contest_id = random.randint(1, 10)

    @task(5)
    def view_candidate_profile(self):
        """View candidate profile"""
        with self.client.get(
            f"/api/candidates/{self.candidate_id}",
            catch_response=True,
            name="/api/candidates/[id]"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed to load profile: {response.status_code}")

    @task(3)
    def view_contest_candidates(self):
        """View all candidates in contest"""
        with self.client.get(
            f"/api/contests/{self.contest_id}/candidates",
            catch_response=True,
            name="/api/contests/[id]/candidates"
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Failed to load candidates: {response.status_code}")

    @task(2)
    def view_questions_to_answer(self):
        """View questions needing responses"""
        with self.client.get(
            f"/api/questions?contest_id={self.contest_id}&unanswered=true",
            catch_response=True,
            name="/api/questions?contest_id=[id]&unanswered=true"
        ) as response:
            if response.status_code in [200, 401]:
                response.success()
            else:
                response.failure(f"Failed to load questions: {response.status_code}")


class VideoStreamingTask(TaskSet):
    """Users streaming video responses"""

    @task(10)
    def stream_video(self):
        """Stream video response"""
        video_id = random.randint(1, 500)

        with self.client.get(
            f"/api/videos/{video_id}/stream",
            catch_response=True,
            name="/api/videos/[id]/stream"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed to stream video: {response.status_code}")

    @task(3)
    def get_video_metadata(self):
        """Get video metadata"""
        video_id = random.randint(1, 500)

        with self.client.get(
            f"/api/videos/{video_id}",
            catch_response=True,
            name="/api/videos/[id]"
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            else:
                response.failure(f"Failed to get video metadata: {response.status_code}")


class QuestionSubmissionTask(TaskSet):
    """Users submitting new questions"""

    def on_start(self):
        """Initialize session"""
        self.contest_id = random.randint(1, 10)

    @task(1)
    def submit_question(self):
        """Submit a new question"""
        question_data = {
            "contest_id": self.contest_id,
            "title": f"Test question {random.randint(1, 100000)}",
            "description": "This is a load testing question to test system performance under concurrent load.",
            "category": random.choice(["economy", "environment", "education", "healthcare", "housing"])
        }

        with self.client.post(
            "/api/questions",
            json=question_data,
            catch_response=True,
            name="/api/questions (POST)"
        ) as response:
            # Accept auth failures since we're not fully authenticated
            if response.status_code in [201, 401, 403, 429]:
                response.success()
            else:
                response.failure(f"Failed to submit question: {response.status_code}")


class AdminModerationTask(TaskSet):
    """Admin users moderating content"""

    @task(3)
    def view_pending_questions(self):
        """View questions pending moderation"""
        with self.client.get(
            "/api/admin/moderation/questions?status=pending",
            catch_response=True,
            name="/api/admin/moderation/questions?status=pending"
        ) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed to load pending questions: {response.status_code}")

    @task(2)
    def view_flagged_content(self):
        """View flagged content"""
        with self.client.get(
            "/api/admin/moderation/flagged",
            catch_response=True,
            name="/api/admin/moderation/flagged"
        ) as response:
            if response.status_code in [200, 401, 403]:
                response.success()
            else:
                response.failure(f"Failed to load flagged content: {response.status_code}")


# User Types with Different Behavior Patterns

class CasualBrowser(HttpUser):
    """
    Casual users browsing questions and voting
    Represents ~70% of users
    """
    wait_time = between(3, 10)
    weight = 70

    tasks = [BrowseQuestionsTask]


class ActiveVoter(HttpUser):
    """
    Active users browsing, voting, and watching videos
    Represents ~20% of users
    """
    wait_time = between(2, 6)
    weight = 20

    tasks = {
        BrowseQuestionsTask: 6,
        VideoStreamingTask: 4,
    }


class QuestionSubmitter(HttpUser):
    """
    Users submitting questions
    Represents ~5% of users
    """
    wait_time = between(10, 30)
    weight = 5

    tasks = {
        BrowseQuestionsTask: 5,
        QuestionSubmissionTask: 2,
    }


class CandidateUser(HttpUser):
    """
    Candidates viewing and responding to questions
    Represents ~3% of users
    """
    wait_time = between(5, 15)
    weight = 3

    tasks = {
        CandidatePortalTask: 7,
        VideoStreamingTask: 3,
    }


class AdminUser(HttpUser):
    """
    Admin users moderating content
    Represents ~2% of users
    """
    wait_time = between(4, 12)
    weight = 2

    tasks = {
        AdminModerationTask: 6,
        BrowseQuestionsTask: 4,
    }


# Event Hooks for Metrics Collection

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when load test starts"""
    print("\n" + "="*80)
    print("CivicQ Load Test Started")
    print(f"Target: {environment.host}")
    print("="*80 + "\n")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when load test stops"""
    print("\n" + "="*80)
    print("CivicQ Load Test Completed")
    print("="*80 + "\n")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """Track slow requests"""
    if response_time > 1000:  # Log requests slower than 1s
        print(f"SLOW REQUEST: {request_type} {name} took {response_time}ms")
