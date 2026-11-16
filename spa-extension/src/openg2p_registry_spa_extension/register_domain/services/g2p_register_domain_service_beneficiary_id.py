from openg2p_registry_core.services import G2PRegisterDomainService

from .prepare import validation_error


class G2PRegisterDomainServiceBeneficiaryId(G2PRegisterDomainService):
    async def _allowed_id_types(self) -> set[str]:
        try:
            from openg2p_registry_core.helpers.master_data import MasterDataClient

            client = MasterDataClient.get_component() or MasterDataClient()
            rows = await client.get_attribute_value_rows("ID_TYPE")
        except Exception:
            validation_error("ID_TYPE is not available in master data")
        allowed = {str(row.get("value_code")) for row in rows if row.get("value_code")}
        if not allowed:
            validation_error("ID_TYPE is not available in master data")
        return allowed

    async def validate_domain_attributes(self, records: list[dict]):
        allowed = await self._allowed_id_types()
        for record in records:
            id_type = str(record.get("id_type") or "").strip()
            if not id_type:
                validation_error("ID type is required")
            if id_type not in allowed:
                validation_error("Unknown ID type")
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
