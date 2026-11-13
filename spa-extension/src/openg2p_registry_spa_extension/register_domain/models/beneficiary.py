from datetime import date, datetime

from openg2p_registry_core.models import G2PRegister, G2PRegisterHistory
from openg2p_registry_core.models.g2p_intake_form import G2PIntakeForm
from sqlalchemy import Date, DateTime, Index, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from ..services.g2p_register_domain_service_beneficiary import (
    G2PRegisterDomainServiceBeneficiary,
)


class G2PBeneficiary:
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    foundational_id: Mapped[str] = mapped_column(String, nullable=True, index=True)
    alternate_ids: Mapped[dict] = mapped_column(JSONB, nullable=True)


class G2PRegisterBeneficiary(G2PRegister, G2PBeneficiary):
    __tablename__ = "g2p_register_beneficiary"

    def get_search_text_fields(self) -> str:
        return G2PRegisterDomainServiceBeneficiary().construct_search_text(self.to_dict())

    def get_record_name_fields(self) -> str:
        return G2PRegisterDomainServiceBeneficiary().construct_record_name(self.to_dict())


class G2PRegisterHistoryBeneficiary(G2PRegisterHistory, G2PBeneficiary):
    __tablename__ = "g2p_register_history_beneficiary"


class G2PIntakeFormBeneficiary(G2PIntakeForm, G2PRegister, G2PBeneficiary):
    __tablename__ = "g2p_intake_form_beneficiary"

    def get_search_text_fields(self) -> str:
        return G2PRegisterDomainServiceBeneficiary().construct_search_text(self.to_dict())

    def get_record_name_fields(self) -> str:
        return G2PRegisterDomainServiceBeneficiary().construct_record_name(self.to_dict())


class G2PFinancialAddressVersioned:
    """Columns shared with the history twin."""

    financial_address_type: Mapped[str] = mapped_column(String, nullable=True, index=True)
    financial_address_identifier: Mapped[str] = mapped_column(String, nullable=True)
    financial_address_identifier_hash: Mapped[str] = mapped_column(String, nullable=True, index=True)
    hash_key_version: Mapped[int] = mapped_column(Integer, nullable=True)
    provider_code: Mapped[str] = mapped_column(String, nullable=True, index=True)
    details: Mapped[dict] = mapped_column(JSONB, nullable=True)
    financial_address_name: Mapped[str] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String(3), nullable=True)
    priority: Mapped[int] = mapped_column(Integer, nullable=True)


class G2PFinancialAddressStatus:
    """System-maintained columns. Not copied onto the history twin."""

    account_validation_status: Mapped[str] = mapped_column(String, nullable=True)
    account_validation_next_date: Mapped[date] = mapped_column(Date, nullable=True)
    account_validation_last_validated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    account_validation_name_match: Mapped[str] = mapped_column(String, nullable=True)


class G2PRegisterFinancialAddress(G2PRegister, G2PFinancialAddressVersioned, G2PFinancialAddressStatus):
    __tablename__ = "g2p_register_financial_address"
    __table_args__ = (
        UniqueConstraint(
            "link_internal_record_id",
            "priority",
            name="uq_fa_beneficiary_priority",
            deferrable=True,
            initially="DEFERRED",
        ),
        Index("ix_fa_identifier_hash", "financial_address_identifier_hash"),
    )

    def get_search_text_fields(self) -> str:
        from ..services.g2p_register_domain_service_financial_address import (
            G2PRegisterDomainServiceFinancialAddress,
        )

        return G2PRegisterDomainServiceFinancialAddress().construct_search_text(self.to_dict())

    def get_record_name_fields(self) -> str:
        from ..services.g2p_register_domain_service_financial_address import (
            G2PRegisterDomainServiceFinancialAddress,
        )

        return G2PRegisterDomainServiceFinancialAddress().construct_record_name(self.to_dict())


class G2PRegisterHistoryFinancialAddress(G2PRegisterHistory, G2PFinancialAddressVersioned):
    __tablename__ = "g2p_register_history_financial_address"


class G2PIntakeFormFinancialAddress(G2PIntakeForm, G2PRegister, G2PFinancialAddressVersioned):
    __tablename__ = "g2p_intake_form_financial_address"

    def get_search_text_fields(self) -> str:
        from ..services.g2p_register_domain_service_financial_address import (
            G2PRegisterDomainServiceFinancialAddress,
        )

        return G2PRegisterDomainServiceFinancialAddress().construct_search_text(self.to_dict())

    def get_record_name_fields(self) -> str:
        from ..services.g2p_register_domain_service_financial_address import (
            G2PRegisterDomainServiceFinancialAddress,
        )

        return G2PRegisterDomainServiceFinancialAddress().construct_record_name(self.to_dict())
