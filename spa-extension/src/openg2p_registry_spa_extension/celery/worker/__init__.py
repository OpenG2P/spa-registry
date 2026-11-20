from .account_lookup_worker import register as register_account_lookup_worker
from .account_validation_worker import register as register_account_validation_worker
from .penny_drop_confirmation_worker import register as register_penny_drop_confirmation_worker
from .penny_drop_disbursement_worker import register as register_penny_drop_disbursement_worker
from .penny_drop_envelope_worker import register as register_penny_drop_envelope_worker


def register_worker(celery_app) -> None:
    register_account_validation_worker(celery_app)
    register_account_lookup_worker(celery_app)
    register_penny_drop_envelope_worker(celery_app)
    register_penny_drop_disbursement_worker(celery_app)
    register_penny_drop_confirmation_worker(celery_app)
