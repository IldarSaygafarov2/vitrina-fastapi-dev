from celery import Celery
from backend.app.config import config

celery_app_dev = Celery(
    "dev_celery_tasks",
    broker=config.redis_config.broker_url,
    backend=config.redis_config.backend_url,
)

celery_app_dev.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Tashkent",
    enable_utc=True,
    include=["celery_tasks.tasks"],
)
