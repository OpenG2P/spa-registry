from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column


class FinancialAddressType(BaseORMModel):
    __tablename__ = "financial_address_types"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    handler: Mapped[str] = mapped_column(String, nullable=True)
    validation_regex: Mapped[str] = mapped_column(String, nullable=True)
    normalizer: Mapped[str] = mapped_column(String, nullable=True)
    provider_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    details_schema: Mapped[dict] = mapped_column(JSONB, nullable=True)
    validation_method: Mapped[str] = mapped_column(String, nullable=False, default="NONE")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class FinancialServiceProvider(BaseORMModel):
    __tablename__ = "financial_service_providers"

    code: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    group_name: Mapped[str] = mapped_column(String, nullable=True)
    services: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    needs_review: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
