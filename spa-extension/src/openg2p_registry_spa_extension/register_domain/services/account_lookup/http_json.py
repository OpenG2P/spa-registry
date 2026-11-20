import json
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError

from ....config import Settings
from ...models.beneficiary import G2PRegisterFinancialAddress
from .base import AccountLookupConnector, LookupResult
from .template import render_template


class HttpJsonConnector(AccountLookupConnector):
    """POST a JSON body from a payload template and read status and name paths."""

    name = "http-json"

    def __init__(self, config: dict):
        self.config = config
        self.name = str(config.get("connector") or self.name)

    def lookup(self, address: G2PRegisterFinancialAddress, identifier: str) -> LookupResult:
        # address: G2PRegisterFinancialAddress. identifier: plaintext VPA, MSISDN, or account number.
        context = {
            "identifier": identifier,
            "provider_code": address.provider_code or "",
            "account_name": address.financial_address_name or "",
            "financial_address_type": address.financial_address_type or "",
            "details": address.details or {},
        }
        payload = render_template(self.config.get("payload") or {"identifier": "{identifier}"}, context)
        headers = {"Content-Type": "application/json"}
        api_key = Settings.get_config(strict=True).account_lookup_api_key
        if api_key:
            headers["X-Api-Key"] = api_key
        timeout = int(self.config.get("timeout_seconds") or 10)
        req = urlrequest.Request(
            self.config["url"],
            data=json.dumps(payload).encode(),
            headers=headers,
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=timeout) as response:
                raw = response.read().decode()
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")[:1000]
            return LookupResult(status="ERROR", error=f"HTTP {exc.code}: {detail}", raw={"http_status": exc.code})
        except URLError as exc:
            return LookupResult(status="ERROR", error=str(exc.reason))
        try:
            body = json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return LookupResult(status="ERROR", error="lookup response was not JSON")
        if not isinstance(body, dict):
            return LookupResult(status="ERROR", error="lookup response was not an object")
        return classify_response(body, self.config)


def classify_response(body: dict, connector: dict) -> LookupResult:
    status_text = str(_path(body, connector.get("status_path") or "status") or "").strip().upper()
    found = {str(item).upper() for item in connector.get("found_values") or ["FOUND", "SUCCESS"]}
    missing = {str(item).upper() for item in connector.get("not_found_values") or ["NOT_FOUND"]}
    name = _path(body, connector.get("name_path") or "name")
    name_text = str(name).strip() if name else None
    if status_text in found:
        return LookupResult(status="FOUND", name=name_text or None, raw=_sanitize(body))
    if status_text in missing:
        return LookupResult(status="NOT_FOUND", name=name_text or None, raw=_sanitize(body))
    return LookupResult(status="ERROR", raw=_sanitize(body), error=status_text or "unrecognized lookup response")


def _path(body: dict, path: str):
    current = body
    for part in str(path).split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def _sanitize(body: dict) -> dict:
    text = json.dumps(body, default=str)
    if len(text) <= 4000:
        return body
    return {"truncated": True, "preview": text[:4000]}
