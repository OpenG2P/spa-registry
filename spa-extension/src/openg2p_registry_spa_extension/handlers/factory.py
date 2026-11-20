from enum import Enum

from .base import GenericHandler
from .bic import BicHandler
from .iban import IbanHandler
from .ifsc_bank_account import IfscBankAccountHandler
from .msisdn import MsisdnHandler
from .upi_vpa import UpiVpaHandler


class HandlerName(str, Enum):
    UPI_VPA = "UpiVpaHandler"
    MSISDN = "MsisdnHandler"
    IBAN = "IbanHandler"
    IFSC_BANK_ACCOUNT = "IfscBankAccountHandler"
    BIC = "BicHandler"


class HandlerFactory:
    """Builds the handler class named by a financial-address type."""

    @staticmethod
    def create(name: str | None, regex: str | None = None, normalizer: str | None = None) -> GenericHandler:
        if name == HandlerName.UPI_VPA:
            return UpiVpaHandler()
        elif name == HandlerName.MSISDN:
            return MsisdnHandler()
        elif name == HandlerName.IBAN:
            return IbanHandler()
        elif name == HandlerName.IFSC_BANK_ACCOUNT:
            return IfscBankAccountHandler()
        elif name == HandlerName.BIC:
            return BicHandler()
        return GenericHandler(regex, normalizer)

    @classmethod
    def get(cls, type_row) -> GenericHandler:
        if isinstance(type_row, dict):
            name = type_row.get("handler")
            regex = type_row.get("validation_regex")
            normalizer = type_row.get("normalizer")
        else:
            name = getattr(type_row, "handler", None)
            regex = getattr(type_row, "validation_regex", None)
            normalizer = getattr(type_row, "normalizer", None)
        return cls.create(name, regex, normalizer)


def handler_for(type_row) -> GenericHandler:
    return HandlerFactory.get(type_row)
