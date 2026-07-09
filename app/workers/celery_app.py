from celery import Celery

from app.config import settings

celery_app = Celery(
    "ecommerce_watch",
    broker=str(settings.redis_url),
    backend=str(settings.redis_url),
    include=["app.workers.tasks"],
)


celery_app.conf.beat_schedule = {
    "scrape-periodique": {
        "task": "app.workers.tasks.scrape_task",
        "schedule": 60.0,
    },
}
