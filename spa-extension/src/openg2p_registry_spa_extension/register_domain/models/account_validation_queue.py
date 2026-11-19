from datetime import datetime

from openg2p_fastapi_common.models import BaseORMModel
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class PennyDropEnvelopeQueue(BaseORMModel):
    """One Bridge envelope for a batch of penny-drop instructions."""

    __tablename__ = "penny_drop_envelope_queue"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    envelope_id: Mapped[str] = mapped_column(String, nullable=True)
    currency: Mapped[str] = mapped_column(String, nullable=False)
    instruction_count: Mapped[int] = mapped_column(Integer, nullable=False)
    total_quantity: Mapped[float] = mapped_column(Float, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    last_error: Mapped[str] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PennyDropInstructionQueue(BaseORMModel):
    """One account inside an envelope. disbursement_id is the financial address id."""

    __tablename__ = "penny_drop_instruction_queue"

    attempt_id: Mapped[str] = mapped_column(String, primary_key=True)
    envelope_queue_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    fa_internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    disbursement_id: Mapped[str] = mapped_column(String, nullable=False)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    envelope_id: Mapped[str] = mapped_column(String, nullable=True)
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    confirm_after: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    result_detail: Mapped[dict] = mapped_column(JSONB, nullable=True)
    bank_name_returned: Mapped[str] = mapped_column(String, nullable=True)
    name_match_score: Mapped[float] = mapped_column(Float, nullable=True)
    last_error: Mapped[str] = mapped_column(String, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class AccountLookupQueue(BaseORMModel):
    """One lookup attempt. Not a register."""

    __tablename__ = "account_lookup_queue"

    lookup_id: Mapped[str] = mapped_column(String, primary_key=True)
    fa_internal_record_id: Mapped[str] = mapped_column(String, nullable=False, index=True)
    attempt_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False)
    result: Mapped[str] = mapped_column(String, nullable=True)
    name_returned: Mapped[str] = mapped_column(String, nullable=True)
    name_match_score: Mapped[float] = mapped_column(Float, nullable=True)
    connector: Mapped[str] = mapped_column(String, nullable=True)
    response_detail: Mapped[dict] = mapped_column(JSONB, nullable=True)
    last_error: Mapped[str] = mapped_column(String, nullable=True)
    next_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
