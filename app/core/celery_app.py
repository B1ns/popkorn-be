# app/core/celery_app.py
from celery import Celery
from celery.signals import worker_process_init

from app.core import database
from app.core.config import settings

from app.auth import models as auth_models  # noqa: F401
from app.comments import models as comments_models  # noqa: F401
from app.movies import models as movies_models  # noqa: F401

celery_app = Celery(
    "popkorn",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=True,
    broker_connection_retry_on_startup=True
)

celery_app.autodiscover_tasks(["app.comments"])


@worker_process_init.connect
def _init_worker_db(**kwargs):
    database.reset_engine()