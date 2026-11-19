"""Queue due IFSC, IBAN, and BIC addresses as one envelope batch."""

import logging
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import (
    PennyDropEnvelopeQueue,
    PennyDropInstructionQueue,
)
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ..helper import OpenQueueStatus, PennyDropAddressType

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.config import Settings as BeatSettings
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

    beat_config = BeatSettings.get_config()
    engine = Engine.get_engine()
    spa_settings = Settings.get_config(strict=False)

    @celery_app.task(name="penny_drop_beat_producer")
    def penny_drop_beat_producer():
        if not task_enabled():
            _logger.info("penny_drop_beat_producer is disabled")
            return
        limit = int(spa_settings.account_validation_chunk_size or 100)
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            envelope_ids = _enqueue_due_addresses(session, limit)
        for envelope_queue_id in envelope_ids:
            celery_app.send_task(
                "penny_drop_envelope_worker",
                args=([envelope_queue_id],),
                queue=beat_config.worker_queue,
            )

    celery_app.conf.beat_schedule["penny_drop_beat_producer"] = {
        "task": "penny_drop_beat_producer",
        "schedule": int(spa_settings.penny_drop_beat_seconds or 60),
    }
    _ = penny_drop_beat_producer


def _enqueue_due_addresses(session, limit: int) -> list[str]:
    today = date.today()
    rows = (
        session.execute(
            select(G2PRegisterFinancialAddress)
            .where(
                G2PRegisterFinancialAddress.record_status == "ACTIVE",
                G2PRegisterFinancialAddress.financial_address_type.in_(PennyDropAddressType),
                G2PRegisterFinancialAddress.account_validation_status.in_(("UNVERIFIED", "VERIFIED")),
                G2PRegisterFinancialAddress.account_validation_next_date.is_not(None),
                G2PRegisterFinancialAddress.account_validation_next_date <= today,
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        .scalars()
        .all()
    )
    now = datetime.now(timezone.utc)
    grouped: dict[str, list] = {}
    for address in rows:
        address.account_validation_status = "PENDING"
        open_row = session.execute(
            select(PennyDropInstructionQueue.attempt_id).where(
                PennyDropInstructionQueue.fa_internal_record_id == address.internal_record_id,
                PennyDropInstructionQueue.status.in_(OpenQueueStatus),
            )
        ).first()
        if open_row is not None:
            continue
        grouped.setdefault(address.currency or "INR", []).append(address)
    envelope_ids = []
    amount = float(Settings.get_config(strict=False).penny_drop_amount or 1)
    for currency, addresses in grouped.items():
        envelope_queue_id = f"PDE-{uuid.uuid4().hex}"
        session.add(
            PennyDropEnvelopeQueue(
                id=envelope_queue_id,
                currency=currency,
                instruction_count=len(addresses),
                total_quantity=amount * len(addresses),
                status="PENDING",
                created_at=now,
                updated_at=now,
            )
        )
        for address in addresses:
            previous = session.execute(
                select(func.count())
                .select_from(PennyDropInstructionQueue)
                .where(PennyDropInstructionQueue.fa_internal_record_id == address.internal_record_id)
            ).scalar_one()
            attempt_id = f"PD-{uuid.uuid4().hex}"
            session.add(
                PennyDropInstructionQueue(
                    attempt_id=attempt_id,
                    envelope_queue_id=envelope_queue_id,
                    fa_internal_record_id=address.internal_record_id,
                    disbursement_id=attempt_id,
                    attempt_no=int(previous or 0) + 1,
                    status="PENDING",
                    confirm_after=now,
                    created_at=now,
                    updated_at=now,
                )
            )
        envelope_ids.append(envelope_queue_id)
    session.commit()
    return envelope_ids
