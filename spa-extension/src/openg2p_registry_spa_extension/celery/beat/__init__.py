from .account_lookup_beat_producer import register as register_account_lookup_beat
from .account_lookup_stale_retry_beat_producer import register as register_account_lookup_stale_retry_beat
from .account_validation_beat_producer import register as register_account_validation_beat
from .penny_drop_beat_producer import register as register_penny_drop_beat
from .penny_drop_confirmation_beat_producer import register as register_penny_drop_confirmation_beat
from .penny_drop_dispatch_beat_producer import register as register_penny_drop_dispatch_beat
from .penny_drop_stale_retry_beat_producer import register as register_penny_drop_stale_retry_beat


def register_beat(celery_app) -> None:
    register_account_validation_beat(celery_app)
    register_account_lookup_beat(celery_app)
    register_account_lookup_stale_retry_beat(celery_app)
    register_penny_drop_beat(celery_app)
    register_penny_drop_dispatch_beat(celery_app)
    register_penny_drop_confirmation_beat(celery_app)
    register_penny_drop_stale_retry_beat(celery_app)
