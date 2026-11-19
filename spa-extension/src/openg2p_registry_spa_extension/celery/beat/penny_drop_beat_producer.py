"""Queue due IFSC, IBAN, and BIC addresses for penny drop."""

import logging
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import PennyDropQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ..helper import OpenQueueStatus, PennyDropAddressType

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

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
            _enqueue_due_addresses(session, limit)

    celery_app.conf.beat_schedule["penny_drop_beat_producer"] = {
        "task": "penny_drop_beat_producer",
        "schedule": int(spa_settings.penny_drop_beat_seconds or 60),
    }
    _ = penny_drop_beat_producer


def _enqueue_due_addresses(session, limit: int) -> None:
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
    for address in rows:
        address.account_validation_status = "PENDING"
        open_row = session.execute(
            select(PennyDropQueue.attempt_id).where(
                PennyDropQueue.fa_internal_record_id == address.internal_record_id,
                PennyDropQueue.status.in_(OpenQueueStatus),
            )
        ).first()
        if open_row is not None:
            continue
        session.add(
            PennyDropQueue(
                attempt_id=f"PD-{uuid.uuid4().hex}",
                fa_internal_record_id=address.internal_record_id,
                attempt_no=1,
                status="PENDING",
                confirm_after=now,
                created_at=now,
                updated_at=now,
            )
        )
    session.commit()
