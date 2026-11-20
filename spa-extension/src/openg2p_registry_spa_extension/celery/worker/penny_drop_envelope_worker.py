"""Create one Bridge envelope for a penny-drop batch."""

import logging
from datetime import date, datetime, timezone

from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import PennyDropEnvelopeQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from .penny_drop_bridge import instructions_for, payload_id, post, request_body, retry

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_worker.control import task_enabled
    from openg2p_registry_celery_worker.engine import Engine

    engine = Engine.get_engine()

    @celery_app.task(name="penny_drop_envelope_worker")
    def penny_drop_envelope_worker(envelope_queue_ids: list[str]):
        if not task_enabled():
            _logger.info("penny_drop_envelope_worker is disabled")
            return
        if not envelope_queue_ids:
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _create_envelopes(session, envelope_queue_ids)

    _ = penny_drop_envelope_worker


def _create_envelopes(session, envelope_queue_ids: list[str]) -> None:
    settings = Settings.get_config(strict=True)
    for envelope_queue_id in envelope_queue_ids:
        envelope = session.get(PennyDropEnvelopeQueue, envelope_queue_id)
        instructions = instructions_for(session, envelope_queue_id)
        if envelope is None or envelope.envelope_id or not instructions:
            continue
        try:
            _start_envelope(envelope, instructions, settings)
        except Exception as exc:
            _logger.exception("Penny drop envelope %s failed", envelope_queue_id)
            envelope.status = "FAILED"
            envelope.last_error = str(exc)
            envelope.updated_at = datetime.now(timezone.utc)
            for row in instructions:
                address = session.get(G2PRegisterFinancialAddress, row.fa_internal_record_id)
                if address is not None:
                    retry(row, address, settings, str(exc))
    session.commit()


def _start_envelope(envelope, instructions, settings) -> None:
    base = str(settings.g2p_bridge_partner_url or "").rstrip("/")
    if not base:
        raise RuntimeError("g2p bridge url is not set")
    amount = float(settings.penny_drop_amount or 1)
    response = post(
        settings,
        f"{base}/create_disbursement_envelopes",
        _envelope_body(settings, amount, envelope.currency, len(instructions)),
    )
    envelope_id = payload_id(response)
    if not envelope_id:
        raise RuntimeError("bridge did not return an envelope id")
    now = datetime.now(timezone.utc)
    envelope.envelope_id = envelope_id
    envelope.status = "DISBURSEMENT_PENDING"
    envelope.updated_at = now
    envelope.last_error = None
    for row in instructions:
        row.envelope_id = envelope_id
        row.updated_at = now


def _envelope_body(settings, amount: float, currency: str, count: int) -> dict:
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
                    "number_of_beneficiaries": count,
                    "number_of_disbursements": count,
                    "total_disbursement_quantity": amount * count,
                    "measurement_unit": currency,
                    "disbursement_schedule_date": today,
                }
            ]
        },
    )
