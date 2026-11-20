from .base import AccountLookupConnector
from .http_json import HttpJsonConnector
from .juspay import JuspayConnector
from .paytm_vpa import PaytmVpaConnector
from .payu import PayuConnector
from .razorpay import RazorpayConnector


class ConnectorFactory:
    """Builds the connector class named by a config entry."""

    @staticmethod
    def create(config: dict) -> AccountLookupConnector | None:
        name = str(config.get("connector") or "")
        if name == "http-json":
            return HttpJsonConnector(config)
        elif name == "payu":
            return PayuConnector(config)
        elif name == "juspay":
            return JuspayConnector(config)
        elif name == "razorpay":
            return RazorpayConnector(config)
        elif name == "paytm-vpa":
            return PaytmVpaConnector(config)
        return None

    @classmethod
    def get(cls, financial_address_type: str, provider_code: str | None, settings) -> AccountLookupConnector | None:
        configured = getattr(settings, "account_lookup_connectors", None) or {}
        if not isinstance(configured, dict):
            return None
        chosen = cls._choose(configured.get(financial_address_type), provider_code)
        if not isinstance(chosen, dict) or not str(chosen.get("url") or "").strip():
            return None
        return cls.create(chosen)

    @staticmethod
    def _choose(entries, provider_code: str | None):
        if isinstance(entries, dict):
            entries = [entries]
        if not isinstance(entries, list):
            return None
        matched = None
        default = None
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            codes = entry.get("provider_codes") or []
            if isinstance(codes, str):
                codes = [codes]
            if "*" in codes and default is None:
                default = entry
            elif provider_code and provider_code in codes and matched is None:
                matched = entry
        if default is not None:
            return default
        return matched
