import logging
from datetime import datetime, timezone

from sqlalchemy import or_, select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import AccountLookupQueue

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.config import Settings as BeatSettings
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

    beat_config = BeatSettings.get_config()
    engine = Engine.get_engine()
    spa_settings = Settings.get_config(strict=False)

    @celery_app.task(name="account_lookup_beat_producer")
    def account_lookup_beat_producer():
        if not task_enabled():
            _logger.info("account_lookup_beat_producer is disabled")
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            claimed = _claim_lookup_rows(session, int(spa_settings.account_lookup_batch_size or 200))
        if claimed:
            celery_app.send_task(
                "account_lookup_worker",
                args=(claimed,),
                queue=beat_config.worker_queue,
            )

    celery_app.conf.beat_schedule["account_lookup_beat_producer"] = {
        "task": "account_lookup_beat_producer",
        "schedule": int(spa_settings.account_lookup_beat_seconds or 30),
    }
    _ = account_lookup_beat_producer


def _claim_lookup_rows(session, limit: int) -> list[str]:
    now = datetime.now(timezone.utc)
    rows = (
        session.execute(
            select(AccountLookupQueue)
            .where(
                AccountLookupQueue.status == "PENDING",
                or_(
                    AccountLookupQueue.next_attempt_at.is_(None),
                    AccountLookupQueue.next_attempt_at <= now,
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
        claimed.append(row.lookup_id)
    session.commit()
    return claimed
