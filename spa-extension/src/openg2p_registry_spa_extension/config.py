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
    account_validation_beat_seconds: int = 60
    account_lookup_beat_seconds: int = 30
    account_lookup_stale_retry_beat_seconds: int = 300
    account_lookup_batch_size: int = 200
    account_lookup_max_attempts: int = 3
    account_lookup_retry_backoff_minutes: int = 60
    account_lookup_stale_minutes: int = 30
    account_validation_chunk_size: int = 100
    account_validation_revalidation_days: int = 365
    # Worker Secret env REGISTRY_EXTENSIONS_ACCOUNT_LOOKUP_API_KEY. Not stored in the connector map.
    account_lookup_api_key: str = ""
    # Keyed by financial address type, or by "TYPE:PROVIDER_CODE" when that
    # provider needs its own request body. A missing url means no connector.
    account_lookup_connectors: dict = {}
