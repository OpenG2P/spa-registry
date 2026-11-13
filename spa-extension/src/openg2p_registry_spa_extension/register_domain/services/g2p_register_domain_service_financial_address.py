import logging

from openg2p_fastapi_common.context import dbengine
from openg2p_registry_core.services import G2PRegisterDomainService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from ...config import Settings
from ...crypto import decrypt_identifier
from ...handlers import HandlerContext, HandlerError, handler_for
from .prepare import prepare, validation_error

_logger = logging.getLogger("g2p-register-domain-service")


class G2PRegisterDomainServiceFinancialAddress(G2PRegisterDomainService):
    async def validate_domain_attributes(self, records: list[dict]):
        settings = Settings.get_config()
        types = await self._load_types()
        providers = await self._load_providers()
        for record in records:
            code = record.get("financial_address_type")
            type_row = types.get(code)
            if type_row is None or not type_row.get("active", True):
                validation_error("UNKNOWN_FINANCIAL_ADDRESS_TYPE")
            prepare(type_row, record, providers=providers, settings=settings)
            status = (record.get("record_status") or "ACTIVE").upper()
            priority = record.get("priority")
            if not record.get("financial_address_type"):
                validation_error("Financial address type is required")
            if not str(record.get("financial_address_identifier") or "").strip():
                validation_error("Financial address identifier is required")
            if not str(record.get("currency") or "").strip():
                validation_error("Currency is required")
            if status != "ACTIVE" and priority not in (None, ""):
                validation_error("An inactive financial address cannot have a priority")
            if status == "ACTIVE" and (priority is None or str(priority).strip() == ""):
                validation_error("Priority is required")
            if status == "ACTIVE":
                try:
                    if int(priority) < 1:
                        raise ValueError
                except (TypeError, ValueError):
                    validation_error("Priority must be a whole number of 1 or higher")
        await self._advise_ifsc_directory(records)
        await self._reject_duplicate_priorities(records)

    async def _advise_ifsc_directory(self, records: list[dict]) -> None:
        """IFSC format and bank prefix are enforced in the handler.

        Whether the branch exists in Master Data is advisory: a miss or an
        unreachable directory is logged and the write still proceeds.
        """
        ifscs = []
        for record in records:
            if record.get("financial_address_type") != "IFSC-BANK-ACCOUNT":
                continue
            ifsc = str((record.get("details") or {}).get("ifsc") or "").strip().upper()
            if ifsc:
                ifscs.append(ifsc)
        if not ifscs:
            return
        try:
            from openg2p_registry_core.helpers.master_data import MasterDataClient

            client = MasterDataClient.get_component() or MasterDataClient()
            codes = await client.get_attribute_codes()
        except Exception:
            _logger.warning("MDS unreachable; skipping IFSC directory check", exc_info=True)
            return
        known = (codes or {}).get("IFSC_DIRECTORY") or set()
        for ifsc in ifscs:
            if ifsc not in known:
                _logger.warning(
                    "IFSC %s is not an active MDS directory branch; accepted because branch validation is advisory",
                    ifsc,
                )

    async def _reject_duplicate_priorities(self, records: list[dict]) -> None:
        claimed: dict[tuple[str, int], str] = {}
        for record in records:
            status = (record.get("record_status") or "ACTIVE").upper()
            raw = record.get("priority")
            if status != "ACTIVE" or raw in (None, ""):
                continue
            priority = int(raw)
            link = str(record.get("link_internal_record_id") or "")
            key = (link, priority)
            if key in claimed:
                validation_error(
                    f"Priority {priority} is already used by another financial address for this beneficiary"
                )
            claimed[key] = str(record.get("internal_record_id") or "")

        links = {link for link, _priority in claimed if link}
        if not links:
            return

        from ..models.beneficiary import G2PRegisterFinancialAddress

        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            rows = (
                await session.execute(
                    select(
                        G2PRegisterFinancialAddress.link_internal_record_id,
                        G2PRegisterFinancialAddress.priority,
                        G2PRegisterFinancialAddress.internal_record_id,
                    ).where(
                        G2PRegisterFinancialAddress.link_internal_record_id.in_(links),
                        G2PRegisterFinancialAddress.priority.is_not(None),
                    )
                )
            ).all()

        submitted_ids = {
            str(record.get("internal_record_id"))
            for record in records
            if record.get("internal_record_id")
        }
        for link, priority, internal_id in rows:
            owner = claimed.get((str(link), int(priority)))
            if owner is None or owner == str(internal_id):
                continue
            if str(internal_id) in submitted_ids:
                continue
            validation_error(
                f"Priority {int(priority)} is already used by another financial address for this beneficiary"
            )

    async def validate_intake_parent_link(self, record: dict, link_internal_record_id: str | None, session: AsyncSession) -> None:
        if not link_internal_record_id:
            validation_error("financial address requires a beneficiary")
        from ..models.beneficiary import G2PIntakeFormBeneficiary, G2PRegisterBeneficiary

        link_id = str(link_internal_record_id)
        parent = await session.get(G2PRegisterBeneficiary, link_id)
        if parent is None:
            parent = (
                await session.execute(
                    select(G2PIntakeFormBeneficiary).where(
                        G2PIntakeFormBeneficiary.internal_record_id == link_id
                    )
                )
            ).scalars().first()
        status = getattr(parent, "record_status", None) if parent is not None else None
        if parent is None or (status or "ACTIVE") != "ACTIVE":
            validation_error("beneficiary is missing or not active")

    def construct_record_name(self, payload: dict, extra: list[str] = None) -> str:
        return str(payload.get("financial_address_name") or "").strip()

    def construct_search_text(self, payload: dict, extra: list[str] = None) -> str:
        masked = self.mask_identifier(payload)
        parts = [
            payload.get("functional_record_id"),
            payload.get("financial_address_type"),
            payload.get("provider_code"),
            masked,
        ]
        if extra:
            parts.extend(extra)
        return " ".join(str(part).strip() for part in parts if str(part or "").strip())

    def validate_live(self, financial_address_type: str, raw_identifier: str, provider_code=None, details=None) -> dict:
        settings = Settings.get_config()
        record = {
            "financial_address_type": financial_address_type,
            "financial_address_identifier": raw_identifier,
            "provider_code": provider_code,
            "details": details or {},
        }
        errors = []
        normalized = None
        derived = None
        try:
            prepared = prepare(
                {"handler": None, "provider_required": bool(provider_code), "kind": None, "active": True},
                record,
                providers={},
                settings=settings,
            )
            normalized = prepared.get("financial_address_identifier")
            derived = prepared.get("provider_code")
        except Exception as exc:
            errors.append(str(exc))
        return {"normalized": normalized, "derived_provider": derived, "errors": errors}

    def mask_identifier(self, record: dict) -> str:
        ident = record.get("financial_address_identifier") or ""
        if ident.startswith("enc:v1:"):
            return "****"
        handler = handler_for({"handler": None})
        try:
            return handler.mask(ident) if ident else ""
        except HandlerError:
            return "****"

    def reveal_identifier(self, stored: str) -> str:
        settings = Settings.get_config()
        return decrypt_identifier(stored, settings.financial_address_encryption_key)

    async def _load_types(self) -> dict:
        from ..models.reference_data import FinancialAddressType

        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            rows = (await session.execute(select(FinancialAddressType))).scalars().all()
        return {
            row.code: {
                "code": row.code,
                "kind": row.kind,
                "handler": row.handler,
                "validation_regex": row.validation_regex,
                "normalizer": row.normalizer,
                "provider_required": row.provider_required,
                "validation_method": row.validation_method,
                "active": row.active,
            }
            for row in rows
        }

    async def _load_providers(self) -> dict:
        from ..models.reference_data import FinancialServiceProvider

        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            rows = (await session.execute(select(FinancialServiceProvider))).scalars().all()
        return {
            row.code: {"code": row.code, "services": list(row.services or []), "active": row.active}
            for row in rows
        }

    async def pre_approve(self, change_request, session):
        return None

    async def post_approve(self, change_request, session):
        _logger.info("Financial address approved; validation status is reset by the persistence hook")

    async def post_ingest(self, register_id, row, session):
        return None


def mask_for_search(payload: dict) -> str:
    ctx = HandlerContext()
    ident = payload.get("financial_address_identifier") or ""
    type_code = payload.get("financial_address_type") or ""
    handler_name = {
        "UPI-VPA-BANK-ACCOUNT": "UpiVpaHandler",
        "MSISDN-WALLET": "MsisdnHandler",
        "MSISDN-BANK-ACCOUNT": "MsisdnHandler",
        "IFSC-BANK-ACCOUNT": "IfscBankAccountHandler",
        "IBAN-BANK-ACCOUNT": "IbanHandler",
    }.get(type_code)
    handler = handler_for({"handler": handler_name})
    try:
        if ident.startswith("enc:v1:"):
            return "****"
        return handler.mask(ident)
    except HandlerError:
        return "****"
    finally:
        del ctx
