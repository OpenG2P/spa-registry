"""Claim envelopes whose disbursements have not been sent yet."""

import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import PennyDropEnvelopeQueue

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.config import Settings as BeatSettings
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

    beat_config = BeatSettings.get_config()
    engine = Engine.get_engine()
    spa_settings = Settings.get_config(strict=False)

    @celery_app.task(name="penny_drop_dispatch_beat_producer")
    def penny_drop_dispatch_beat_producer():
        if not task_enabled():
            _logger.info("penny_drop_dispatch_beat_producer is disabled")
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            claimed = _claim_ready(session)
        for envelope_queue_id in claimed:
            celery_app.send_task(
                "penny_drop_disbursement_worker",
                args=([envelope_queue_id],),
                queue=beat_config.worker_queue,
            )

    celery_app.conf.beat_schedule["penny_drop_dispatch_beat_producer"] = {
        "task": "penny_drop_dispatch_beat_producer",
        "schedule": int(spa_settings.penny_drop_dispatch_beat_seconds or 30),
    }
    _ = penny_drop_dispatch_beat_producer


def _claim_ready(session) -> list[str]:
    now = datetime.now(timezone.utc)
    rows = (
        session.execute(
            select(PennyDropEnvelopeQueue)
            .where(
                PennyDropEnvelopeQueue.status == "DISBURSEMENT_PENDING",
                PennyDropEnvelopeQueue.envelope_id.is_not(None),
            )
            .with_for_update(skip_locked=True)
        )
        .scalars()
        .all()
    )
    claimed = []
    for row in rows:
        row.status = "PROCESSING"
        row.updated_at = now
        claimed.append(row.id)
    session.commit()
    return claimed
