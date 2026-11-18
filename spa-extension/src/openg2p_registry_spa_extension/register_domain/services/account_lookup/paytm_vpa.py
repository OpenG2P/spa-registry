"""Paytm validate-vpa. MID and the request token come from env vars.

Paytm does not accept a static API key on this call. token_env must be a TXN_TOKEN or ACCESS token from Paytm's token API. This connector does not fetch that token.
"""

import json
import os
import time
import uuid
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

from .base import AccountLookupConnector, LookupResult


class PaytmVpaConnector(AccountLookupConnector):
    name = "paytm-vpa"

    def __init__(self, config: dict):
        self.config = config
        self.name = str(config.get("connector") or self.name)

    def lookup(self, address, identifier: str) -> LookupResult:
        mid = os.environ.get(str(self.config.get("mid_env") or "")) or ""
        token = os.environ.get(str(self.config.get("token_env") or "")) or ""
        if not mid or not token:
            return LookupResult(status="ERROR", error="Paytm mid or token is not set")
        order_id = uuid.uuid4().hex
        query = urlencode({"mid": mid, "orderId": order_id})
        url = self.config["url"] + ("&" if "?" in self.config["url"] else "?") + query
        now = str(int(time.time()))
        body = {
            "head": {"version": "v1", "requestTimestamp": now, "tokenType": "TXN_TOKEN", "token": token},
            "body": {"vpa": identifier, "mid": mid},
        }
        req = urlrequest.Request(
            url,
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        payload = _read(req)
        if isinstance(payload, LookupResult):
            return payload
        inner = payload.get("body") if isinstance(payload.get("body"), dict) else {}
        info = inner.get("resultInfo") if isinstance(inner.get("resultInfo"), dict) else {}
        result_status = str(info.get("resultStatus") or "").upper()
        valid = inner.get("valid")
        if result_status == "S" and valid is True:
            return LookupResult(status="FOUND", raw=payload)
        if result_status == "F" or valid is False:
            return LookupResult(status="NOT_FOUND", raw=payload)
        return LookupResult(status="ERROR", error=str(info.get("resultMsg") or "unrecognized Paytm response"), raw=payload)


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
