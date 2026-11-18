"""Juspay verify-vpa. The API key is read from the env var named by api_key_env."""

import base64
import json
import os
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from .base import AccountLookupConnector, LookupResult


class JuspayConnector(AccountLookupConnector):
    name = "juspay"

    def __init__(self, config: dict):
        self.config = config
        self.name = str(config.get("connector") or self.name)

    def lookup(self, address, identifier: str) -> LookupResult:
        api_key = os.environ.get(str(self.config.get("api_key_env") or "")) or ""
        merchant_id = str(self.config.get("merchant_id") or "")
        if not api_key or not merchant_id:
            return LookupResult(status="ERROR", error="Juspay api key or merchant_id is not set")
        token = base64.b64encode(api_key.encode()).decode()
        body = urlencode({"vpa": identifier, "merchant_id": merchant_id}).encode()
        req = urlrequest.Request(
            self.config["url"],
            data=body,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Authorization": f"Basic {token}",
            },
            method="POST",
        )
        payload = _read(req)
        if isinstance(payload, LookupResult):
            return payload
        status = str(payload.get("status") or "").upper()
        name = str(payload.get("customer_name") or "").strip() or None
        if status == "VALID":
            return LookupResult(status="FOUND", name=name, raw=payload)
        if status == "INVALID":
            return LookupResult(status="NOT_FOUND", raw=payload)
        return LookupResult(status="ERROR", error=status or "unrecognized Juspay response", raw=payload)


def _read(req):
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
