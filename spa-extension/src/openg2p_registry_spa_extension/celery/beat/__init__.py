from .account_lookup_beat_producer import register as register_account_lookup_beat
from .account_lookup_stale_retry_beat_producer import register as register_account_lookup_stale_retry_beat
from .account_validation_beat_producer import register as register_account_validation_beat


def register_beat(celery_app) -> None:
    register_account_validation_beat(celery_app)
    register_account_lookup_beat(celery_app)
    register_account_lookup_stale_retry_beat(celery_app)
