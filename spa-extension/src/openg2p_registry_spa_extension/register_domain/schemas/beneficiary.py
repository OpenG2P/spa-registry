from typing import Optional

from openg2p_registry_core.schemas import G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PRegisterHistorySchema
from pydantic import BaseModel


class AlternateId(BaseModel):
    type: str
    value: str


class G2PSchemaBeneficiary:
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    foundational_id: Optional[str] = None
    alternate_ids: Optional[list[AlternateId]] = None


class G2PRegisterSchemaBeneficiary(G2PRegisterBaseSchema, G2PSchemaBeneficiary):
    pass


class G2PRegisterHistorySchemaBeneficiary(G2PRegisterHistorySchema, G2PSchemaBeneficiary):
    pass


class G2PIntakeFormSchemaBeneficiary(G2PIntakeFormSchemaBase, G2PRegisterBaseSchema, G2PSchemaBeneficiary):
    pass
