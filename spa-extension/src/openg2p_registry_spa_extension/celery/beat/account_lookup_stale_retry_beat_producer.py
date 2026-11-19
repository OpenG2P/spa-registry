import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import AccountLookupQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ..helper import LookupAddressType, OpenQueueStatus

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_beat.control import task_enabled
    from openg2p_registry_celery_beat.engine import Engine

    engine = Engine.get_engine()
    spa_settings = Settings.get_config(strict=False)

    @celery_app.task(name="account_lookup_stale_retry_beat_producer")
    def account_lookup_stale_retry_beat_producer():
        if not task_enabled():
            _logger.info("account_lookup_stale_retry_beat_producer is disabled")
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _reset_stale(session, int(spa_settings.account_lookup_stale_minutes or 30))

    celery_app.conf.beat_schedule["account_lookup_stale_retry_beat_producer"] = {
        "task": "account_lookup_stale_retry_beat_producer",
        "schedule": int(spa_settings.account_lookup_stale_retry_beat_seconds or 300),
    }
    _ = account_lookup_stale_retry_beat_producer


def _reset_stale(session, stale_minutes: int) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(minutes=stale_minutes)
    rows = (
        session.execute(
            select(AccountLookupQueue).where(
                AccountLookupQueue.status == "PROCESSING",
                AccountLookupQueue.updated_at.is_not(None),
                AccountLookupQueue.updated_at < cutoff,
            )
        )
        .scalars()
        .all()
    )
    now = datetime.now(timezone.utc)
    for row in rows:
        row.status = "PENDING"
        row.next_attempt_at = now
        row.updated_at = now
        row.last_error = "reset after the worker stopped"
    pending_ids = set(
        session.execute(
            select(G2PRegisterFinancialAddress.internal_record_id).where(
                G2PRegisterFinancialAddress.account_validation_status == "PENDING",
                G2PRegisterFinancialAddress.financial_address_type.in_(LookupAddressType),
            )
        )
        .scalars()
        .all()
    )
    if pending_ids:
        open_ids = set(
            session.execute(
                select(AccountLookupQueue.fa_internal_record_id).where(
                    AccountLookupQueue.fa_internal_record_id.in_(pending_ids),
                    AccountLookupQueue.status.in_(OpenQueueStatus),
                )
            )
            .scalars()
            .all()
        )
        for address in session.execute(
            select(G2PRegisterFinancialAddress).where(
                G2PRegisterFinancialAddress.internal_record_id.in_(pending_ids - open_ids)
            )
        ).scalars():
            address.account_validation_status = "UNVERIFIED"
    session.commit()
