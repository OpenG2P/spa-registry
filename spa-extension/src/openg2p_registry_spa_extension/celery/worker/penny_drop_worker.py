"""Create one ACCOUNT_VALIDATION envelope and disbursement per queue row."""

import logging
import uuid
from datetime import date, datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...crypto import decrypt_identifier
from ...register_domain.models.account_validation_queue import PennyDropQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from .penny_drop_bridge import finish, payload_id, post, request_body, retry

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_worker.control import task_enabled
    from openg2p_registry_celery_worker.engine import Engine

    engine = Engine.get_engine()

    @celery_app.task(name="penny_drop_worker")
    def penny_drop_worker(attempt_ids: list[str]):
        if not task_enabled():
            _logger.info("penny_drop_worker is disabled")
            return
        if not attempt_ids:
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _process(session, attempt_ids)

    _ = penny_drop_worker


def _process(session, attempt_ids: list[str]) -> None:
    settings = Settings.get_config(strict=True)
    for attempt_id in attempt_ids:
        row = session.get(PennyDropQueue, attempt_id)
        if row is None or row.status != "PROCESSING" or row.envelope_id:
            continue
        address = session.get(G2PRegisterFinancialAddress, row.fa_internal_record_id)
        if address is None or address.record_status != "ACTIVE":
            finish(row, "CANCELLED", "address is missing or inactive")
            continue
        try:
            _start_drop(row, address, settings)
        except Exception as exc:
            _logger.exception("Penny drop %s failed", attempt_id)
            retry(row, address, settings, str(exc))
    session.commit()


def _start_drop(row, address, settings) -> None:
    base = str(settings.g2p_bridge_partner_url or "").rstrip("/")
    if not base:
        retry(row, address, settings, "g2p bridge url is not set")
        return
    identifier = decrypt_identifier(address.financial_address_identifier or "", settings.financial_address_encryption_key)
    amount = float(settings.penny_drop_amount or 1)
    currency = address.currency or "INR"
    envelope = post(
        settings,
        f"{base}/create_disbursement_envelopes",
        _envelope_body(settings, amount, currency),
    )
    envelope_id = payload_id(envelope)
    if not envelope_id:
        retry(row, address, settings, "bridge did not return an envelope id")
        return
    disbursement_id = f"PD-{uuid.uuid4().hex}"
    post(
        settings,
        f"{base}/create_disbursements",
        _disbursement_body(settings, envelope_id, disbursement_id, address, identifier, amount),
    )
    now = datetime.now(timezone.utc)
    row.envelope_id = envelope_id
    row.run_id = disbursement_id
    row.sent_at = now
    row.status = "PENDING"
    row.confirm_after = now + timedelta(minutes=int(settings.penny_drop_poll_minutes or 5))
    row.updated_at = now
    row.last_error = None


def _envelope_body(settings, amount: float, currency: str) -> dict:
    today = date.today().isoformat()
    return request_body(
        settings,
        {
            "request_payload": [
                {
                    "benefit_program_mnemonic": settings.g2p_bridge_program_mnemonic or "ACCOUNT-VALIDATION",
                    "benefit_code_mnemonic": "PENNY-DROP",
                    "benefit_type": "CASH_DIGITAL",
                    "disbursement_frequency": "OnDemand",
                    "envelope_type": "ACCOUNT_VALIDATION",
                    "number_of_beneficiaries": 1,
                    "number_of_disbursements": 1,
                    "total_disbursement_quantity": amount,
                    "measurement_unit": currency,
                    "disbursement_schedule_date": today,
                }
            ]
        },
    )


def _disbursement_body(settings, envelope_id: str, disbursement_id: str, address, identifier: str, amount: float) -> dict:
    details = address.details or {}
    return request_body(
        settings,
        {
            "request_payload": [
                {
                    "disbursement_id": disbursement_id,
                    "disbursement_envelope_id": envelope_id,
                    "beneficiary_id": address.link_internal_record_id,
                    "beneficiary_name": address.financial_address_name,
                    "disbursement_quantity": amount,
                    "narrative": "penny-drop",
                    "bank_account_number": identifier,
                    "bank_code": address.provider_code,
                    "branch_code": details.get("ifsc") or details.get("bic") or address.provider_code,
                    "account_type": "BANK_ACCOUNT",
                    "compute_elements": {
                        "financial_address_type": address.financial_address_type,
                        "account": identifier,
                        "provider_code": address.provider_code,
                        "ifsc": details.get("ifsc"),
                        "bic": details.get("bic"),
                    },
                }
            ]
        },
    )
