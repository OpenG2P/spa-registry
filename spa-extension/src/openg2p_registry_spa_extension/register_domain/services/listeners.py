import logging

from sqlalchemy import event

from ...config import Settings
from ...handlers import HANDLERS
from .prepare import apply_encryption, initial_validation_status, prepare

_logger = logging.getLogger("g2p-register-domain-service")
_wired = False


def _type_dict(code: str) -> dict | None:
    # Persistence runs inside the session flush. Callers that already validated
    # still pass through here so hash and encryption are applied on save.
    return {
        "code": code,
        "handler": {
            "UPI-VPA-BANK-ACCOUNT": "UpiVpaHandler",
            "MSISDN-WALLET": "MsisdnHandler",
            "MSISDN-BANK-ACCOUNT": "MsisdnHandler",
            "IFSC-BANK-ACCOUNT": "IfscBankAccountHandler",
            "IBAN-BANK-ACCOUNT": "IbanHandler",
            "BIC-BANK-ACCOUNT": "BicHandler",
        }.get(code),
        "kind": "WALLET" if code == "MSISDN-WALLET" else "BANK_ACCOUNT",
        "provider_required": code not in {"UPI-VPA-BANK-ACCOUNT", "IBAN-BANK-ACCOUNT"},
        "validation_method": "PENNY_DROP" if code in {"IFSC-BANK-ACCOUNT", "IBAN-BANK-ACCOUNT", "BIC-BANK-ACCOUNT"} else "LOOKUP",
        "active": True,
    }


def _beneficiary_record_name(connection, target) -> str:
    link = str(getattr(target, "link_internal_record_id", None) or "").strip()
    if not link:
        return ""
    from sqlalchemy import text
    from sqlalchemy.orm import object_session

    from ..models.beneficiary import G2PIntakeFormBeneficiary, G2PRegisterBeneficiary

    session = object_session(target)
    if session is not None:
        parent = session.get(G2PRegisterBeneficiary, link)
        if parent is None:
            for obj in list(session.new) + list(session.identity_map.values()):
                if isinstance(obj, (G2PRegisterBeneficiary, G2PIntakeFormBeneficiary)) and str(
                    getattr(obj, "internal_record_id", "") or ""
                ) == link:
                    parent = obj
                    break
        if parent is not None:
            named = str(getattr(parent, "record_name", None) or "").strip()
            if not named:
                named = " ".join(
                    part
                    for part in (
                        str(getattr(parent, "first_name", None) or "").strip(),
                        str(getattr(parent, "last_name", None) or "").strip(),
                    )
                    if part
                )
            if named:
                return named

    for table in ("g2p_register_beneficiary", "g2p_intake_form_beneficiary"):
        row = connection.execute(
            text(
                f"SELECT record_name, first_name, last_name FROM {table} "
                "WHERE internal_record_id = :id"
            ),
            {"id": link},
        ).first()
        if row is None:
            continue
        named = str(row[0] or "").strip() or " ".join(part for part in (row[1], row[2]) if part).strip()
        if named:
            return named
    return ""


def _before_save(mapper, connection, target):
    settings = Settings.get_config()
    code = getattr(target, "financial_address_type", None)
    type_row = _type_dict(code) if code else None
    if type_row is None:
        return
    unknown = type_row.get("handler")
    if unknown and unknown not in HANDLERS:
        _logger.warning("Unknown handler %s", unknown)
    record = {
        "financial_address_identifier": target.financial_address_identifier,
        "provider_code": target.provider_code,
        "details": target.details or {},
        "record_status": getattr(target, "record_status", "ACTIVE"),
    }
    try:
        prepared = prepare(type_row, record, providers={}, settings=settings, check_providers=False)
    except Exception:
        _logger.exception("financial address persistence hook failed")
        raise
    prepared = apply_encryption(prepared, settings)
    target.financial_address_identifier = prepared["financial_address_identifier"]
    target.financial_address_identifier_hash = prepared["financial_address_identifier_hash"]
    target.hash_key_version = prepared["hash_key_version"]
    target.provider_code = prepared.get("provider_code")
    if not str(getattr(target, "financial_address_name", None) or "").strip():
        target.financial_address_name = _beneficiary_record_name(connection, target) or None
    if target.financial_address_name:
        target.record_name = target.financial_address_name
    status = getattr(target, "record_status", None) or "ACTIVE"
    if status != "ACTIVE":
        target.priority = None
    if not getattr(target, "account_validation_status", None):
        status, next_date = initial_validation_status(type_row)
        target.account_validation_status = status
        target.account_validation_next_date = next_date


def install_persistence_hooks() -> None:
    global _wired
    if _wired:
        return
    from ..models.beneficiary import G2PIntakeFormFinancialAddress, G2PRegisterFinancialAddress

    event.listen(G2PRegisterFinancialAddress, "before_insert", _before_save)
    event.listen(G2PRegisterFinancialAddress, "before_update", _before_save)
    event.listen(G2PIntakeFormFinancialAddress, "before_insert", _before_save)
    event.listen(G2PIntakeFormFinancialAddress, "before_update", _before_save)
    _wired = True
