"""Celery beat and worker tasks shipped by the SPA extension.

The platform process calls register_celery() when this package exists.
"""

from .beat import register_beat
from .worker import register_worker


def register_celery(celery_app, role: str) -> None:
    if role == "beat":
        register_beat(celery_app)
    elif role == "worker":
        register_worker(celery_app)
