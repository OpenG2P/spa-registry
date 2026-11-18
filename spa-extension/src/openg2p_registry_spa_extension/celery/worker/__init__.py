from .account_lookup_worker import register as register_account_lookup_worker
from .account_validation_worker import register as register_account_validation_worker


def register_worker(celery_app) -> None:
    register_account_validation_worker(celery_app)
    register_account_lookup_worker(celery_app)
