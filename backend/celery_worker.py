"""
Celery Worker Configuration

Entry point for starting Celery workers for video processing tasks.
"""

from app.tasks.video_tasks import celery_app

if __name__ == '__main__':
    celery_app.start()
