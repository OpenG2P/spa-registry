from .base import GenericHandler
from .bic import BicHandler
from .iban import IbanHandler
from .ifsc_bank_account import IfscBankAccountHandler
from .msisdn import MsisdnHandler
from .upi_vpa import UpiVpaHandler

HANDLERS = {
    "UpiVpaHandler": UpiVpaHandler,
    "MsisdnHandler": MsisdnHandler,
    "IbanHandler": IbanHandler,
    "IfscBankAccountHandler": IfscBankAccountHandler,
    "BicHandler": BicHandler,
}


def handler_for(type_row) -> GenericHandler:
    name = getattr(type_row, "handler", None) if not isinstance(type_row, dict) else type_row.get("handler")
    if isinstance(type_row, dict):
        regex = type_row.get("validation_regex")
        normalizer = type_row.get("normalizer")
    else:
        regex = getattr(type_row, "validation_regex", None)
        normalizer = getattr(type_row, "normalizer", None)
    cls = HANDLERS.get(name) if name else None
    if cls is None:
        return GenericHandler(regex, normalizer)
    return cls()
