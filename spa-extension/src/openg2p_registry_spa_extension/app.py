# ruff: noqa: E402
import asyncio
import logging

from .config import Settings

_config = Settings.get_config()

from openg2p_fastapi_common.app import Initializer as BaseInitializer
from openg2p_registry_core.app import Initializer as CoreInitializer

from .handlers import HANDLERS
from .register_domain.models import (
    FinancialAddressType,
    FinancialServiceProvider,
    G2PIntakeFormBeneficiary,
    G2PIntakeFormFinancialAddress,
    G2PRegisterBeneficiary,
    G2PRegisterFinancialAddress,
    G2PRegisterHistoryBeneficiary,
    G2PRegisterHistoryFinancialAddress,
)
from .register_domain.services import (
    G2PRegisterDomainServiceBeneficiary,
    G2PRegisterDomainServiceFinancialAddress,
)
from .register_domain.services.listeners import install_persistence_hooks

_logger = logging.getLogger(_config.logging_default_logger_name)


class Initializer(BaseInitializer):
    def initialize(self, **kwargs):
        super().initialize()
        CoreInitializer().initialize()
        _logger.info("SPA handlers registered: %s", ", ".join(sorted(HANDLERS)))
        G2PRegisterDomainServiceBeneficiary()
        G2PRegisterDomainServiceFinancialAddress()
        install_persistence_hooks()

    def migrate_database(self, args):
        async def migrate():
            _logger.info("Migrating SPA registry tables")
            await FinancialAddressType.create_migrate()
            await FinancialServiceProvider.create_migrate()
            await G2PRegisterBeneficiary.create_migrate()
            await G2PRegisterHistoryBeneficiary.create_migrate()
            await G2PIntakeFormBeneficiary.create_migrate()
            await G2PRegisterFinancialAddress.create_migrate()
            await G2PRegisterHistoryFinancialAddress.create_migrate()
            await G2PIntakeFormFinancialAddress.create_migrate()

        asyncio.run(migrate())
