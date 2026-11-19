"""Claim penny-drop rows that are waiting on Bridge status."""

import logging
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import PennyDropInstructionQueue

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.config import Settings as BeatSettings
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

    beat_config = BeatSettings.get_config()
    engine = Engine.get_engine()
    spa_settings = Settings.get_config(strict=False)

    @celery_app.task(name="penny_drop_confirmation_beat_producer")
    def penny_drop_confirmation_beat_producer():
        if not task_enabled():
            _logger.info("penny_drop_confirmation_beat_producer is disabled")
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            claimed = _claim_sent(session, int(spa_settings.account_validation_chunk_size or 100))
        if claimed:
            celery_app.send_task(
                "penny_drop_confirmation_worker",
                args=(claimed,),
                queue=beat_config.worker_queue,
            )

    celery_app.conf.beat_schedule["penny_drop_confirmation_beat_producer"] = {
        "task": "penny_drop_confirmation_beat_producer",
        "schedule": int(spa_settings.penny_drop_confirmation_beat_seconds or 60),
    }
    _ = penny_drop_confirmation_beat_producer


def _claim_sent(session, limit: int) -> list[str]:
    now = datetime.now(timezone.utc)
    rows = (
        session.execute(
            select(PennyDropInstructionQueue)
            .where(
                PennyDropInstructionQueue.status == "PENDING",
                PennyDropInstructionQueue.envelope_id.is_not(None),
                PennyDropInstructionQueue.sent_at.is_not(None),
                or_(
                    PennyDropInstructionQueue.confirm_after.is_(None),
                    PennyDropInstructionQueue.confirm_after <= now,
                ),
            )
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        .scalars()
        .all()
    )
    claimed = []
    for row in rows:
        row.status = "PROCESSING"
        row.updated_at = now
        claimed.append(row.attempt_id)
    session.commit()
    return claimed
