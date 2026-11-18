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
    # Values come from the worker Secret. The connector map only names these env vars.

    # http-json lookup
    account_lookup_api_key: str = ""

    # PayU validate VPA
    payu_merchant_key: str = ""
    payu_salt: str = ""

    # Juspay verify VPA
    juspay_api_key: str = ""
    juspay_merchant_id: str = ""

    # Razorpay composite VPA validation
    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""
    razorpay_source_account: str = ""

    # Paytm validate VPA
    paytm_mid: str = ""
    paytm_txn_token: str = ""
    # Keyed by financial address type. Each value is a list of connectors.
    # provider_codes ["*"] is used first. A named code is used only when there is no "*" entry.
    account_lookup_connectors: dict = {}
