import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import sessionmaker

from ...config import Settings
from ...register_domain.models.account_validation_queue import AccountLookupQueue
from ...register_domain.models.beneficiary import G2PRegisterFinancialAddress
from ...register_domain.services.account_lookup import ConnectorFactory
from ..helper import OpenQueueStatus

_logger = logging.getLogger("g2p-register-domain-service")


def register(celery_app) -> None:
    from openg2p_registry_celery_worker.control import task_enabled
    from openg2p_registry_celery_worker.engine import Engine

    engine = Engine.get_engine()

    @celery_app.task(name="account_validation_worker")
    def account_validation_worker(fa_ids: list[str]):
        if not task_enabled():
            _logger.info("account_validation_worker is disabled")
            return
        if not fa_ids:
            return
        session_maker = sessionmaker(bind=engine, expire_on_commit=False)
        with session_maker() as session:
            _enqueue_lookups(session, fa_ids)

    _ = account_validation_worker


def _enqueue_lookups(session, fa_ids: list[str]) -> None:
    # Celery's Settings subclasses this one and is already registered.
    # strict=False would return that object, which does not load
    # REGISTRY_EXTENSIONS_ACCOUNT_LOOKUP_CONNECTORS.
    settings = Settings.get_config(strict=True)
    for fa_id in fa_ids:
        address = session.get(G2PRegisterFinancialAddress, fa_id)
        if address is None or address.account_validation_status != "PENDING":
            continue
        if address.record_status != "ACTIVE":
            address.account_validation_status = "NOT_APPLICABLE"
            address.account_validation_next_date = None
            continue
        open_row = session.execute(
            select(AccountLookupQueue.lookup_id).where(
                AccountLookupQueue.fa_internal_record_id == fa_id,
                AccountLookupQueue.status.in_(OpenQueueStatus),
            )
        ).first()
        if open_row is not None:
            continue
        connector = ConnectorFactory.get(address.financial_address_type, address.provider_code, settings)
        if connector is None:
            _logger.warning(
                "No lookup connector for %s provider %s; marking NOT_APPLICABLE",
                address.financial_address_type,
                address.provider_code,
            )
            address.account_validation_status = "NOT_APPLICABLE"
            address.account_validation_next_date = None
            continue
        now = datetime.now(timezone.utc)
        session.add(
            AccountLookupQueue(
                lookup_id=f"LK-{uuid.uuid4().hex}",
                fa_internal_record_id=fa_id,
                attempt_no=1,
                status="PENDING",
                connector=connector.name,
                next_attempt_at=now,
                created_at=now,
                updated_at=now,
            )
        )
    session.commit()
