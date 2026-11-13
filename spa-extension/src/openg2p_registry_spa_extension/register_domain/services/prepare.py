import copy
import logging
from datetime import date

from openg2p_registry_core.errors import G2PRegistryErrorCodes, G2PRegistryException

from ...crypto import encrypt_identifier, identifier_hash
from ...handlers import HandlerContext, HandlerError, handler_for

_logger = logging.getLogger("g2p-register-domain-service")


def validation_error(message: str) -> None:
    raise G2PRegistryException(
        code=G2PRegistryErrorCodes.REQUEST_VALIDATION_ERROR.value[1],
        message=message,
    )


def prepare(type_row: dict, record: dict, *, providers: dict, settings, check_providers: bool = True) -> dict:
    """Normalize and fill derived fields on a copy. Raises G2PRegistryException."""
    record = copy.deepcopy(record)
    handler = handler_for(type_row)
    ctx = HandlerContext(
        default_region=settings.default_phone_region,
        provider_codes=set(providers),
    )
    try:
        ident = handler.normalize(record.get("financial_address_identifier") or "", ctx)
        handler.validate(ident, ctx)
    except HandlerError as exc:
        validation_error(str(exc))

    derived = handler.derive_provider(ident, ctx)
    if derived:
        given = record.get("provider_code")
        if given and given != derived:
            validation_error("Provider does not match the identifier")
        record["provider_code"] = derived
    if type_row.get("provider_required") and not record.get("provider_code"):
        validation_error("Provider is required for this financial address type")

    provider_code = record.get("provider_code")
    if check_providers and provider_code:
        provider = providers.get(provider_code)
        if provider is None or not provider.get("active", True):
            validation_error("Provider is not a known active financial service provider")
        services = provider.get("services") or []
        if type_row.get("kind") not in services:
            validation_error("Provider does not offer this kind of financial address")

    details = record.get("details") or {}
    try:
        handler.validate_details(details, provider_code, ctx)
    except HandlerError as exc:
        validation_error(str(exc))

    record["financial_address_identifier"] = ident
    record["financial_address_identifier_hash"] = identifier_hash(ident, settings.financial_address_hash_key)
    record["hash_key_version"] = settings.financial_address_hash_key_version
    return record


def apply_encryption(record: dict, settings) -> dict:
    if settings.financial_address_encryption_at_rest:
        ident = record.get("financial_address_identifier") or ""
        if ident and not ident.startswith("enc:v1:"):
            record["financial_address_identifier"] = encrypt_identifier(
                ident, settings.financial_address_encryption_key
            )
    return record


def initial_validation_status(type_row: dict) -> tuple[str, date | None]:
    method = type_row.get("validation_method") or "NONE"
    if method in {"PENNY_DROP", "LOOKUP"}:
        return "UNVERIFIED", date.today()
    return "NOT_APPLICABLE", None
