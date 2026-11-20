"""Shared lookup constants used by more than one beat or worker."""

from enum import Enum


class LookupAddressType(str, Enum):
    UPI_VPA_BANK_ACCOUNT = "UPI-VPA-BANK-ACCOUNT"
    MSISDN_WALLET = "MSISDN-WALLET"
    MSISDN_BANK_ACCOUNT = "MSISDN-BANK-ACCOUNT"


class PennyDropAddressType(str, Enum):
    IFSC_BANK_ACCOUNT = "IFSC-BANK-ACCOUNT"
    IBAN_BANK_ACCOUNT = "IBAN-BANK-ACCOUNT"
    BIC_BANK_ACCOUNT = "BIC-BANK-ACCOUNT"


class OpenQueueStatus(str, Enum):
    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
