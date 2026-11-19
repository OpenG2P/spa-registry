"""Create the disbursements for one penny-drop envelope."""

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...crypto import decrypt_identifier
from ...register_domain.models.account_validation_queue import PennyDropEnvelopeQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from .penny_drop_bridge import finish, instructions_for, post, request_body

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_worker.control import task_enabled
    from openg2p_registry_celery_worker.engine import Engine

    engine = Engine.get_engine()

    @celery_app.task(name="penny_drop_disbursement_worker")
    def penny_drop_disbursement_worker(envelope_queue_ids: list[str]):
        if not task_enabled():
            _logger.info("penny_drop_disbursement_worker is disabled")
            return
        if not envelope_queue_ids:
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _create_disbursements(session, envelope_queue_ids)

    _ = penny_drop_disbursement_worker


def _create_disbursements(session, envelope_queue_ids: list[str]) -> None:
    settings = Settings.get_config(strict=True)
    for envelope_queue_id in envelope_queue_ids:
        envelope = session.get(PennyDropEnvelopeQueue, envelope_queue_id)
        instructions = instructions_for(session, envelope_queue_id)
        if envelope is None or not envelope.envelope_id or not instructions:
            continue
        try:
            _start_disbursements(session, envelope, instructions, settings)
        except Exception as exc:
            _logger.exception("Penny drop disbursements %s failed", envelope_queue_id)
            envelope.status = "DISBURSEMENT_PENDING"
            envelope.last_error = str(exc)
            envelope.updated_at = datetime.now(timezone.utc)
    session.commit()


def _start_disbursements(session, envelope, instructions, settings) -> None:
    base = str(settings.g2p_bridge_partner_url or "").rstrip("/")
    amount = float(settings.penny_drop_amount or 1)
    payloads = []
    kept = []
    for row in instructions:
        address = session.get(G2PRegisterFinancialAddress, row.fa_internal_record_id)
        if address is None or address.record_status != "ACTIVE":
            finish(row, "CANCELLED", "address is missing or inactive")
            continue
        identifier = decrypt_identifier(
            address.financial_address_identifier or "", settings.financial_address_encryption_key
        )
        payloads.append(_disbursement_payload(row.disbursement_id, envelope.envelope_id, address, identifier, amount))
        kept.append(row)
    if not payloads:
        envelope.status = "SENT"
        envelope.updated_at = datetime.now(timezone.utc)
        return
    post(
        settings,
        f"{base}/create_disbursements",
        request_body(settings, {"request_payload": payloads}),
    )
    now = datetime.now(timezone.utc)
    for row in kept:
        row.sent_at = now
        row.status = "PENDING"
        row.confirm_after = now + timedelta(minutes=int(settings.penny_drop_poll_minutes or 5))
        row.updated_at = now
        row.last_error = None
    envelope.status = "SENT"
    envelope.updated_at = now
    envelope.last_error = None


def _disbursement_payload(disbursement_id: str, envelope_id: str, address, identifier: str, amount: float) -> dict:
    details = address.details or {}
    return {
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
