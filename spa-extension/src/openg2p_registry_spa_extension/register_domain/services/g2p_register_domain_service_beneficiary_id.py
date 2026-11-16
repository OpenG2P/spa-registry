import logging

from openg2p_registry_core.services import G2PRegisterDomainService

from .prepare import validation_error

_logger = logging.getLogger("g2p-register-domain-service")


class G2PRegisterDomainServiceBeneficiaryId(G2PRegisterDomainService):
    async def validate_domain_attributes(self, records: list[dict]):
        for record in records:
            if not str(record.get("id_type") or "").strip():
                validation_error("ID type is required")
            if not str(record.get("id_value") or "").strip():
                validation_error("ID value is required")

    def construct_record_name(self, payload: dict, extra: list[str] = None) -> str:
        id_type = str(payload.get("id_type") or "").strip()
        id_value = str(payload.get("id_value") or "").strip()
        return " ".join(part for part in (id_type, id_value) if part)

    def construct_search_text(self, payload: dict, extra: list[str] = None) -> str:
        parts = [
            payload.get("functional_record_id"),
            payload.get("id_type"),
            payload.get("id_value"),
            payload.get("record_name") or self.construct_record_name(payload),
        ]
        if extra:
            parts.extend(extra)
        return " ".join(str(part).strip() for part in parts if str(part or "").strip())
