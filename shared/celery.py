from celery import Celery

from shared.settings import settings

celery = Celery("worker", broker=settings.rmq.URL, backend="rpc://")

import shared.auth.tasks  # noqa: E402, F401
