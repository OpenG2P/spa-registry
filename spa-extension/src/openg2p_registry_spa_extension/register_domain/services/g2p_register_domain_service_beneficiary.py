import logging
import re

from openg2p_registry_core.services import G2PRegisterDomainService

from ...config import Settings
from ...handlers.base import HandlerContext, HandlerError
from ...handlers.msisdn import MsisdnHandler
from .prepare import validation_error

_logger = logging.getLogger("g2p-register-domain-service")
_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class G2PRegisterDomainServiceBeneficiary(G2PRegisterDomainService):
    async def validate_domain_attributes(self, records: list[dict]):
        settings = Settings.get_config()
        phone = MsisdnHandler()
        ctx = HandlerContext(default_region=settings.default_phone_region)
        for record in records:
            first = (record.get("first_name") or "").strip()
            last = (record.get("last_name") or "").strip()
            if not first and not last:
                validation_error("first_name or last_name is required")
            raw_phone = str(record.get("phone_number") or "").strip()
            if not raw_phone:
                validation_error("Phone number is required")
            try:
                record["phone_number"] = phone.normalize(raw_phone, ctx)
                phone.validate(record["phone_number"], ctx)
            except HandlerError as exc:
                validation_error(str(exc))
            raw_email = str(record.get("email") or "").strip()
            if not raw_email or not _EMAIL.fullmatch(raw_email):
                validation_error("A valid email is required")
            record["email"] = raw_email.lower()

    def construct_record_name(self, payload: dict, extra: list[str] = None) -> str:
        parts = [
            str(payload.get("first_name") or "").strip(),
            str(payload.get("last_name") or "").strip(),
        ]
        return " ".join(part for part in parts if part)

    def construct_search_text(self, payload: dict, extra: list[str] = None) -> str:
        parts = [
            payload.get("functional_record_id"),
            payload.get("phone_number"),
            payload.get("email"),
            payload.get("record_name") or self.construct_record_name(payload),
        ]
        if extra:
            parts.extend(extra)
        return " ".join(str(part).strip() for part in parts if str(part or "").strip())

    async def pre_approve(self, change_request, session):
        return None

    async def post_approve(self, change_request, session):
        return None

    async def post_ingest(self, register_id, row, session):
        return None
