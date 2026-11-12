from openg2p_registry_core.config import Settings as CoreSettings
from pydantic_settings import SettingsConfigDict

from . import __version__


class Settings(CoreSettings):
    model_config = SettingsConfigDict(
        env_prefix="registry_extensions_", env_file=".env", extra="allow"
    )

    openapi_title: str = "OpenG2P SPA Registry"
    openapi_description: str = """
        FastAPI Service for the OpenG2P Social Payment Accounts Registry
        """
    openapi_version: str = __version__

    financial_address_encryption_at_rest: bool = False
    financial_address_encryption_key: str = ""
    financial_address_hash_key: str = "spa-dev-hash-key"
    financial_address_hash_key_version: int = 1
    default_phone_region: str = "IN"
    allow_unseen_upi_provider: bool = False
