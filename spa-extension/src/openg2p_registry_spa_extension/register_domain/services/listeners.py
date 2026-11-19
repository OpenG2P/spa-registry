import logging

from sqlalchemy import event, inspect as sa_inspect
from sqlalchemy.orm.attributes import get_history

from ...config import Settings
from ...handlers import HandlerName
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


def _content_changed(target) -> bool:
    """True when an existing row's address fields changed. Validation columns are ignored."""
    if not sa_inspect(target).persistent:
        return False
    fields = (
        "financial_address_type",
        "financial_address_identifier",
        "provider_code",
        "details",
        "financial_address_name",
        "currency",
    )
    return any(get_history(target, field).has_changes() for field in fields)


def _before_save(mapper, connection, target):
    settings = Settings.get_config()
    changed = _content_changed(target)
    code = getattr(target, "financial_address_type", None)
    type_row = _type_dict(code) if code else None
    if type_row is None:
        return
    unknown = type_row.get("handler")
    if unknown and unknown not in HandlerName:
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
    beneficiary_name = _beneficiary_record_name(connection, target)
    if beneficiary_name:
        target.financial_address_name = beneficiary_name
    elif not str(getattr(target, "financial_address_name", None) or "").strip():
        target.financial_address_name = None
    if target.financial_address_name:
        target.record_name = target.financial_address_name
    status = getattr(target, "record_status", None) or "ACTIVE"
    if status != "ACTIVE":
        target.priority = None
    if changed or not getattr(target, "account_validation_status", None):
        status, next_date = initial_validation_status(type_row)
        target.account_validation_status = status
        target.account_validation_next_date = next_date


def _beneficiary_name(target) -> str:
    joined = " ".join(
        part
        for part in (
            str(getattr(target, "first_name", None) or "").strip(),
            str(getattr(target, "last_name", None) or "").strip(),
        )
        if part
    )
    record = str(getattr(target, "record_name", None) or "").strip()
    if get_history(target, "first_name").has_changes() or get_history(target, "last_name").has_changes():
        return joined or record
    return record or joined


def _beneficiary_name_changed(target) -> bool:
    if not sa_inspect(target).persistent:
        return False
    return any(get_history(target, field).has_changes() for field in ("record_name", "first_name", "last_name"))


def _sync_address_names(mapper, connection, target) -> None:
    if not _beneficiary_name_changed(target):
        return
    named = _beneficiary_name(target)
    if not named:
        return
    link = str(getattr(target, "internal_record_id", None) or "").strip()
    if not link:
        return
    from sqlalchemy import text
    from sqlalchemy.orm import object_session

    from ..models.beneficiary import G2PIntakeFormFinancialAddress, G2PRegisterFinancialAddress

    session = object_session(target)
    if session is not None:
        for obj in list(session.new) + list(session.identity_map.values()):
            if isinstance(obj, (G2PRegisterFinancialAddress, G2PIntakeFormFinancialAddress)) and str(
                getattr(obj, "link_internal_record_id", "") or ""
            ) == link:
                obj.financial_address_name = named
                obj.record_name = named
    for table in ("g2p_register_financial_address", "g2p_intake_form_financial_address"):
        connection.execute(
            text(
                f"UPDATE {table} SET financial_address_name = :name, record_name = :name "
                "WHERE link_internal_record_id = :id"
            ),
            {"name": named, "id": link},
        )


def install_persistence_hooks() -> None:
    global _wired
    if _wired:
        return
    from ..models.beneficiary import (
        G2PIntakeFormBeneficiary,
        G2PIntakeFormFinancialAddress,
        G2PRegisterBeneficiary,
        G2PRegisterFinancialAddress,
    )

    event.listen(G2PRegisterFinancialAddress, "before_insert", _before_save)
    event.listen(G2PRegisterFinancialAddress, "before_update", _before_save)
    event.listen(G2PIntakeFormFinancialAddress, "before_insert", _before_save)
    event.listen(G2PIntakeFormFinancialAddress, "before_update", _before_save)
    event.listen(G2PRegisterBeneficiary, "before_update", _sync_address_names)
    event.listen(G2PIntakeFormBeneficiary, "before_update", _sync_address_names)
    _wired = True
