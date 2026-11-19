"""Poll Bridge for a sent penny drop and write the address status."""

import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import PennyDropInstructionQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ...register_domain.services.account_lookup import name_match
from .penny_drop_bridge import find, finish, post, request_body, retry

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_worker.control import task_enabled
    from openg2p_registry_celery_worker.engine import Engine

    engine = Engine.get_engine()

    @celery_app.task(name="penny_drop_confirmation_worker")
    def penny_drop_confirmation_worker(attempt_ids: list[str]):
        if not task_enabled():
            _logger.info("penny_drop_confirmation_worker is disabled")
            return
        if not attempt_ids:
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _process(session, attempt_ids)

    _ = penny_drop_confirmation_worker


def _process(session, attempt_ids: list[str]) -> None:
    settings = Settings.get_config(strict=True)
    for attempt_id in attempt_ids:
        row = session.get(PennyDropInstructionQueue, attempt_id)
        if row is None or row.status != "PROCESSING" or not row.envelope_id:
            continue
        address = session.get(G2PRegisterFinancialAddress, row.fa_internal_record_id)
        if address is None or address.record_status != "ACTIVE":
            finish(row, "CANCELLED", "address is missing or inactive")
            continue
        try:
            _poll_drop(row, address, settings)
        except Exception as exc:
            _logger.exception("Penny drop confirmation %s failed", attempt_id)
            retry(row, address, settings, str(exc))
    session.commit()


def _poll_drop(row, address, settings) -> None:
    base = str(settings.g2p_bridge_partner_url or "").rstrip("/")
    body = request_body(settings, {"request_payload": [row.disbursement_id]})
    payload = post(settings, f"{base}/get_disbursement_status", body)
    name = find(payload, "beneficiary_name_from_bank")
    reversed_count = find(payload, "number_of_disbursements_reversed")
    now = datetime.now(timezone.utc)
    row.result_detail = payload
    row.updated_at = now
    if reversed_count:
        row.status = "COMPLETED"
        row.bank_name_returned = name
        address.account_validation_status = "REJECTED"
        address.account_validation_next_date = None
        return
    if name:
        flag, score = name_match(address.financial_address_name, name)
        row.status = "COMPLETED"
        row.bank_name_returned = name
        row.name_match_score = score
        address.account_validation_status = "VERIFIED"
        address.account_validation_name_match = flag
        address.account_validation_last_validated_at = now
        address.account_validation_next_date = date.today() + timedelta(
            days=int(settings.account_validation_revalidation_days or 365)
        )
        return
    row.status = "PENDING"
    row.confirm_after = now + timedelta(minutes=int(settings.penny_drop_poll_minutes or 5))
    row.last_error = None
