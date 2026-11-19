"""Shared request helpers for the penny-drop workers."""

import asyncio
import json
import uuid
from datetime import datetime, timedelta, timezone
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError


def request_body(settings, body: dict) -> dict:
    return {
        "request_header": {
            "sender_app_mnemonic": settings.g2p_bridge_sender_id or "spa-registry",
            "sender_app_url": settings.g2p_bridge_partner_url or "",
            "request_id": uuid.uuid4().hex,
            "request_timestamp": datetime.now(timezone.utc).isoformat(),
        },
        "request_body": body,
    }


def post(settings, url: str, body: dict) -> dict:
    raw = json.dumps(body).encode()
    headers = {"Content-Type": "application/json", "Signature": signature(body, settings)}
    req = urlrequest.Request(url, data=raw, headers=headers, method="POST")
    try:
        with urlrequest.urlopen(req, timeout=20) as response:
            text = response.read().decode()
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {exc.read().decode(errors='replace')[:500]}") from exc
    except URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc
    parsed = json.loads(text) if text else {}
    if not isinstance(parsed, dict):
        raise RuntimeError("bridge response was not an object")
    return parsed


def signature(body: dict, settings) -> str:
    from openg2p_fastapi_common.crypto.factory import CryptoFactory

    crypto = CryptoFactory.get()
    token = crypto.create_jwt_token(
        body,
        include_payload=False,
        km_app_id="REGISTRY",
        km_ref_id=f"PARTNER_{(settings.g2p_bridge_sender_id or 'spa-registry').replace('-', '_').upper()}",
    )
    if asyncio.iscoroutine(token):
        return asyncio.run(token)
    return token


def payload_id(response: dict) -> str | None:
    header = response.get("response_header") or {}
    if header.get("response_error_code") or header.get("response_error_message"):
        raise RuntimeError(
            header.get("response_error_message") or header.get("response_error_code")
        )
    payload = ((response.get("response_body") or {}).get("response_payload") or [None])[0] or {}
    return payload.get("id") or payload.get("disbursement_envelope_id")


def find(value, key: str):
    if isinstance(value, dict):
        if value.get(key):
            return value[key]
        for item in value.values():
            found = find(item, key)
            if found:
                return found
    if isinstance(value, list):
        for item in value:
            found = find(item, key)
            if found:
                return found
    return None


def retry(row, address, settings, error: str) -> None:
    now = datetime.now(timezone.utc)
    row.last_error = error
    row.updated_at = now
    if int(row.attempt_no or 1) >= int(settings.account_lookup_max_attempts or 3):
        row.status = "FAILED"
        address.account_validation_status = "FAILED"
        address.account_validation_next_date = None
        return
    row.attempt_no = int(row.attempt_no or 1) + 1
    row.status = "PENDING"
    row.confirm_after = now + timedelta(minutes=int(settings.penny_drop_poll_minutes or 5))


def finish(row, status: str, error: str) -> None:
    row.status = status
    row.last_error = error
    row.updated_at = datetime.now(timezone.utc)
