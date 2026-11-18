import logging
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...crypto import decrypt_identifier
from ...register_domain.models.account_validation_queue import AccountLookupQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ...register_domain.services.account_lookup import LookupResult, connector_for, name_match

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_worker.control import task_enabled
    from openg2p_registry_celery_worker.engine import Engine

    engine = Engine.get_engine()

    @celery_app.task(name="account_lookup_worker")
    def account_lookup_worker(lookup_ids: list[str]):
        if not task_enabled():
            _logger.info("account_lookup_worker is disabled")
            return
        if not lookup_ids:
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _process_lookups(session, lookup_ids)

    _ = account_lookup_worker


def _process_lookups(session, lookup_ids: list[str]) -> None:
    settings = Settings.get_config(strict=True)
    for lookup_id in lookup_ids:
        row = session.get(AccountLookupQueue, lookup_id)
        if row is None or row.status != "PROCESSING":
            continue
        address = session.get(G2PRegisterFinancialAddress, row.fa_internal_record_id)
        if address is None or address.record_status != "ACTIVE":
            _finish_queue(row, "CANCELLED", None, error="address is missing or inactive")
            continue
        connector = connector_for(address.financial_address_type, address.provider_code, settings)
        if connector is None:
            address.account_validation_status = "NOT_APPLICABLE"
            address.account_validation_next_date = None
            _finish_queue(row, "CANCELLED", None, error="lookup connector is not configured")
            continue
        try:
            identifier = decrypt_identifier(
                address.financial_address_identifier or "",
                settings.financial_address_encryption_key,
            )
            result = connector.lookup(address, identifier)
        except Exception as exc:
            _logger.exception("Lookup %s failed before a result", lookup_id)
            result = LookupResult(status="ERROR", error=str(exc))
        _apply_result(row, address, result, settings)
    session.commit()


def _apply_result(row, address, result: LookupResult, settings) -> None:
    now = datetime.now(timezone.utc)
    row.response_detail = result.raw
    row.name_returned = result.name
    row.last_error = result.error
    row.updated_at = now
    if result.status == "FOUND":
        flag, score = name_match(address.financial_address_name, result.name)
        row.status = "COMPLETED"
        row.result = "FOUND"
        row.name_match_score = score
        address.account_validation_status = "VERIFIED"
        address.account_validation_last_validated_at = now
        address.account_validation_name_match = flag
        address.account_validation_next_date = date.today() + timedelta(
            days=int(getattr(settings, "account_validation_revalidation_days", 365) or 365)
        )
        return
    if result.status == "NOT_FOUND":
        flag, score = name_match(address.financial_address_name, result.name)
        row.status = "COMPLETED"
        row.result = "NOT_FOUND"
        row.name_match_score = score
        address.account_validation_status = "REJECTED"
        address.account_validation_name_match = flag
        address.account_validation_next_date = None
        return
    max_attempts = int(getattr(settings, "account_lookup_max_attempts", 3) or 3)
    if row.attempt_no >= max_attempts:
        row.status = "FAILED"
        row.result = "ERROR"
        address.account_validation_status = "FAILED"
        address.account_validation_next_date = None
        return
    backoff = int(getattr(settings, "account_lookup_retry_backoff_minutes", 60) or 60)
    row.status = "PENDING"
    row.result = "ERROR"
    row.next_attempt_at = now + timedelta(minutes=backoff)


def _finish_queue(row, status: str, result: str | None, error: str | None = None) -> None:
    row.status = status
    row.result = result
    row.last_error = error
    row.updated_at = datetime.now(timezone.utc)
