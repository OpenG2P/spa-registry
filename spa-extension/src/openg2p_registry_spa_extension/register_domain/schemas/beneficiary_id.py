from typing import Optional

from openg2p_registry_core.schemas import G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PRegisterHistorySchema


class G2PSchemaBeneficiaryId:
    id_type: Optional[str] = None
    id_value: Optional[str] = None


class G2PRegisterSchemaBeneficiaryId(G2PRegisterBaseSchema, G2PSchemaBeneficiaryId):
    pass


class G2PRegisterHistorySchemaBeneficiaryId(G2PRegisterHistorySchema, G2PSchemaBeneficiaryId):
    pass


class G2PIntakeFormSchemaBeneficiaryId(G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PSchemaBeneficiaryId):
    pass
