"""PayU validateVPA. Merchant key and salt come from Settings.payu_merchant_key and Settings.payu_salt."""

import hashlib
import json
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from ....config import Settings
from ...models.beneficiary import G2PRegisterFinancialAddress
from .base import AccountLookupConnector, LookupResult


class PayuConnector(AccountLookupConnector):
    name = "payu"

    def __init__(self, config: dict):
        self.config = config
        self.name = str(config.get("connector") or self.name)

    def lookup(self, address: G2PRegisterFinancialAddress, identifier: str) -> LookupResult:
        settings = Settings.get_config(strict=True)
        key = settings.payu_merchant_key
        salt = settings.payu_salt
        if not key or not salt:
            return LookupResult(status="ERROR", error="PayU key or salt is not set")
        digest = hashlib.sha512(f"{key}|validateVPA|{identifier}|{salt}".encode()).hexdigest()
        body = urlencode(
            {"form": "2", "key": key, "command": "validateVPA", "var1": identifier, "hash": digest}
        ).encode()
        payload = _post(self.config["url"], body, "application/x-www-form-urlencoded")
        if isinstance(payload, LookupResult):
            return payload
        valid = str(payload.get("isVPAValid") if payload.get("isVPAValid") is not None else "")
        name = str(payload.get("payerAccountName") or "").strip()
        if name.upper() in {"", "NA"}:
            name = None
        if str(payload.get("status") or "").upper() == "SUCCESS" and valid == "1":
            return LookupResult(status="FOUND", name=name, raw=payload)
        if str(payload.get("status") or "").upper() == "SUCCESS" and valid == "0":
            return LookupResult(status="NOT_FOUND", raw=payload)
        return LookupResult(status="ERROR", error="unrecognized PayU response", raw=payload)


def _post(url: str, data: bytes, content_type: str):
    req = urlrequest.Request(
        url,
        data=data,
        headers={"Content-Type": content_type, "accept": "application/json"},
        method="POST",
    )
    try:
        with urlrequest.urlopen(req, timeout=10) as response:
            raw = response.read().decode()
    except HTTPError as exc:
        return LookupResult(status="ERROR", error=f"HTTP {exc.code}: {exc.read().decode(errors='replace')[:500]}")
    except URLError as exc:
        return LookupResult(status="ERROR", error=str(exc.reason))
    try:
        body = json.loads(raw) if raw else {}
    except json.JSONDecodeError:
        return LookupResult(status="ERROR", error="lookup response was not JSON")
    if not isinstance(body, dict):
        return LookupResult(status="ERROR", error="lookup response was not an object")
    return body
