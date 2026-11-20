from dataclasses import dataclass

from ...models.beneficiary import G2PRegisterFinancialAddress


@dataclass
class LookupResult:
    """FOUND or NOT_FOUND or ERROR. name is the holder name when the provider returned one. raw is the response kept on the queue row. error is set only for ERROR."""

    status: str
    name: str | None = None
    raw: dict | None = None
    error: str | None = None


class AccountLookupConnector:
    """One provider's lookup call. Subclasses build that provider's payload."""

    name = "lookup"

    def lookup(self, address: G2PRegisterFinancialAddress, identifier: str) -> LookupResult:
        """address is one G2PRegisterFinancialAddress row. identifier is the decrypted financial_address_identifier.

        The row column may still be ciphertext. A real UPI call looks like:

            address.financial_address_type == "UPI-VPA-BANK-ACCOUNT"
            address.provider_code == "okicici"
            address.financial_address_name == "Asha Rao"
            address.details == {}
            identifier == "user2@okicici"

        A real provider key is not on the row. The connector reads it from Settings, for example settings.account_lookup_api_key.
        """
        raise NotImplementedError


def name_match(expected: str | None, returned: str | None) -> tuple[str, float | None]:
    if not returned or not str(expected or "").strip():
        return "UNKNOWN", None
    left = " ".join(str(expected).upper().split())
    right = " ".join(str(returned).upper().split())
    if left == right:
        return "MATCH", 1.0
    return "MISMATCH", 0.0
