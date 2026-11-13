from typing import Optional

from openg2p_registry_core.schemas import G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PRegisterHistorySchema


class G2PSchemaFinancialAddress:
    financial_address_type: Optional[str] = None
    financial_address_identifier: Optional[str] = None
    provider_code: Optional[str] = None
    details: Optional[dict] = None
    financial_address_name: Optional[str] = None
    currency: Optional[str] = None
    priority: Optional[int] = None


class G2PSchemaFinancialAddressStatus:
    account_validation_status: Optional[str] = None
    account_validation_next_date: Optional[str] = None
    account_validation_last_validated_at: Optional[str] = None
    account_validation_name_match: Optional[str] = None


class G2PRegisterSchemaFinancialAddress(
    G2PRegisterBaseSchema, G2PSchemaFinancialAddress, G2PSchemaFinancialAddressStatus
):
    pass


class G2PRegisterHistorySchemaFinancialAddress(G2PRegisterHistorySchema, G2PSchemaFinancialAddress):
    pass


class G2PIntakeFormSchemaFinancialAddress(
    G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PSchemaFinancialAddress
):
    pass
