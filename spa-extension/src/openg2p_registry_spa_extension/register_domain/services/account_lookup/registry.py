from .base import AccountLookupConnector
from .http_json import HttpJsonConnector
from .juspay import JuspayConnector
from .paytm_vpa import PaytmVpaConnector
from .payu import PayuConnector
from .razorpay import RazorpayConnector

ADAPTERS: dict[str, type[AccountLookupConnector]] = {
    "http-json": HttpJsonConnector,
    "payu": PayuConnector,
    "juspay": JuspayConnector,
    "razorpay": RazorpayConnector,
    "paytm-vpa": PaytmVpaConnector,
}


def connector_key(financial_address_type: str, provider_code: str | None) -> str:
    if provider_code:
        return f"{financial_address_type}:{provider_code}"
    return financial_address_type


def connector_for(financial_address_type: str, provider_code: str | None, settings) -> AccountLookupConnector | None:
    configured = getattr(settings, "account_lookup_connectors", None) or {}
    if not isinstance(configured, dict):
        return None
    specific = configured.get(connector_key(financial_address_type, provider_code))
    chosen = specific or _by_provider_list(configured, financial_address_type, provider_code)
    chosen = chosen or configured.get(financial_address_type)
    if not isinstance(chosen, dict) or not str(chosen.get("url") or "").strip():
        return None
    adapter_cls = ADAPTERS.get(str(chosen.get("adapter") or "http-json"))
    if adapter_cls is None:
        return None
    adapter = adapter_cls(chosen)
    if not chosen.get("connector"):
        adapter.name = connector_key(financial_address_type, provider_code)
    return adapter


def _by_provider_list(configured: dict, financial_address_type: str, provider_code: str | None):
    if not provider_code:
        return None
    for entry in configured.values():
        if not isinstance(entry, dict):
            continue
        if entry.get("financial_address_type") != financial_address_type:
            continue
        codes = entry.get("provider_codes") or []
        if provider_code in codes:
            return entry
    return None
