import logging

from openg2p_fastapi_common.context import dbengine
from openg2p_registry_core.services import G2PRegisterDomainService
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from .prepare import validation_error

_logger = logging.getLogger("g2p-register-domain-service")


class G2PRegisterDomainServiceBeneficiary(G2PRegisterDomainService):
    async def validate_domain_attributes(self, records: list[dict]):
        for record in records:
            first = (record.get("first_name") or "").strip()
            last = (record.get("last_name") or "").strip()
            if not first and not last:
                validation_error("first_name or last_name is required")
            alts = record.get("alternate_ids") or []
            foundational = (record.get("foundational_id") or "").strip()
            if not foundational and not alts:
                validation_error("foundational_id or alternate_ids is required")
            for alt in alts:
                if not (alt.get("type") or "").strip() or not (alt.get("value") or "").strip():
                    validation_error("alternate id type and value are required")
            await self._check_uniqueness(record, foundational, alts)

    async def _check_uniqueness(self, record: dict, foundational: str, alts: list) -> None:
        from ..models.beneficiary import G2PRegisterBeneficiary

        own_id = record.get("internal_record_id")
        session_maker = async_sessionmaker(dbengine.get(), expire_on_commit=False)
        async with session_maker() as session:
            if foundational:
                stmt = select(G2PRegisterBeneficiary.internal_record_id).where(
                    G2PRegisterBeneficiary.foundational_id == foundational
                )
                found = (await session.execute(stmt)).scalars().all()
                if any(str(item) != str(own_id) for item in found):
                    validation_error("foundational_id already belongs to another beneficiary")

    def construct_record_name(self, payload: dict, extra: list[str] = None) -> str:
        parts = [
            str(payload.get("first_name") or "").strip(),
            str(payload.get("last_name") or "").strip(),
        ]
        return " ".join(part for part in parts if part)

    def construct_search_text(self, payload: dict, extra: list[str] = None) -> str:
        parts = [
            payload.get("functional_record_id"),
            payload.get("foundational_id"),
            payload.get("record_name") or self.construct_record_name(payload),
        ]
        for alt in payload.get("alternate_ids") or []:
            if isinstance(alt, dict):
                parts.append(alt.get("value"))
        if extra:
            parts.extend(extra)
        return " ".join(str(part).strip() for part in parts if str(part or "").strip())

    async def pre_approve(self, change_request, session):
        return None

    async def post_approve(self, change_request, session):
        return None

    async def post_ingest(self, register_id, row, session):
        return None
