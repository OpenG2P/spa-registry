from typing import Optional

from openg2p_registry_core.schemas import G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PRegisterHistorySchema


class G2PSchemaBeneficiary:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[str] = None


class G2PRegisterSchemaBeneficiary(G2PRegisterBaseSchema, G2PSchemaBeneficiary):
    pass


class G2PRegisterHistorySchemaBeneficiary(G2PRegisterHistorySchema, G2PSchemaBeneficiary):
    pass


class G2PIntakeFormSchemaBeneficiary(G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PSchemaBeneficiary):
    pass
