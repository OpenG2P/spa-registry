import logging
from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ..helper import LOOKUP_TYPES

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.config import Settings as BeatSettings
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

    beat_config = BeatSettings.get_config()
    engine = Engine.get_engine()
    spa_settings = Settings.get_config(strict=False)

    @celery_app.task(name="account_validation_beat_producer")
    def account_validation_beat_producer():
        if not task_enabled():
            _logger.info("account_validation_beat_producer is disabled")
            return
        limit = int(spa_settings.account_validation_chunk_size or 100)
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            claimed = _claim_due_addresses(session, limit)
        for start in range(0, len(claimed), limit):
            celery_app.send_task(
                "account_validation_worker",
                args=(claimed[start : start + limit],),
                queue=beat_config.worker_queue,
            )

    celery_app.conf.beat_schedule["account_validation_beat_producer"] = {
        "task": "account_validation_beat_producer",
        "schedule": int(spa_settings.account_validation_beat_seconds or 60),
    }
    _ = account_validation_beat_producer


def _claim_due_addresses(session, limit: int) -> list[str]:
    today = date.today()
    rows = (
        session.execute(
            select(G2PRegisterFinancialAddress)
            .where(
                G2PRegisterFinancialAddress.record_status == "ACTIVE",
                G2PRegisterFinancialAddress.financial_address_type.in_(LOOKUP_TYPES),
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
    claimed = []
    for row in rows:
        row.account_validation_status = "PENDING"
        claimed.append(row.internal_record_id)
    session.commit()
    return claimed
