"""Razorpay fund-account VPA validation. Key id and secret come from env vars.

The first response is often status "created". That is not a final answer, so it is returned as ERROR and the lookup retry runs again.
"""

import base64
import json
import os
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from .base import AccountLookupConnector, LookupResult


class RazorpayConnector(AccountLookupConnector):
    name = "razorpay"

    def __init__(self, config: dict):
        self.config = config
        self.name = str(config.get("connector") or self.name)

    def lookup(self, address, identifier: str) -> LookupResult:
        key_id = os.environ.get(str(self.config.get("key_id_env") or "")) or ""
        key_secret = os.environ.get(str(self.config.get("key_secret_env") or "")) or ""
        source = os.environ.get(str(self.config.get("source_account_env") or "")) or ""
        if not key_id or not key_secret or not source:
            return LookupResult(status="ERROR", error="Razorpay key or source account is not set")
        token = base64.b64encode(f"{key_id}:{key_secret}".encode()).decode()
        body = {
            "source_account_number": source,
            "fund_account": {
                "account_type": "vpa",
                "vpa": {"address": identifier},
                "contact": {"name": address.financial_address_name or identifier, "type": "customer"},
            },
        }
        req = urlrequest.Request(
            self.config["url"],
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": f"Basic {token}"},
            method="POST",
        )
        payload = _read(req)
        if isinstance(payload, LookupResult):
            return payload
        status = str(payload.get("status") or "").lower()
        results = payload.get("validation_results") if isinstance(payload.get("validation_results"), dict) else {}
        account_status = str(results.get("account_status") or "").lower()
        name = str(results.get("registered_name") or "").strip() or None
        if status == "completed" and account_status == "active":
            return LookupResult(status="FOUND", name=name, raw=payload)
        if status == "failed" or account_status == "invalid":
            return LookupResult(status="NOT_FOUND", name=name, raw=payload)
        return LookupResult(status="ERROR", error=status or "razorpay validation is not complete", raw=payload)


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
