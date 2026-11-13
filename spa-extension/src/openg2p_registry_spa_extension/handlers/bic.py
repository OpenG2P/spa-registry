import re

from .base import GenericHandler, HandlerContext, HandlerError

_BIC = re.compile(r"^[A-Z]{4}[A-Z]{2}[A-Z0-9]{2}([A-Z0-9]{3})?$")
_ACCOUNT = re.compile(r"^[A-Z0-9]{5,34}$")


class BicHandler(GenericHandler):
    def normalize(self, raw: str, ctx: HandlerContext) -> str:
        return re.sub(r"[\s-]+", "", (raw or "")).upper()

    def validate(self, value: str, ctx: HandlerContext) -> None:
        if not _ACCOUNT.fullmatch(value or ""):
            raise HandlerError("invalid bank account number")

    def validate_details(self, details: dict | None, provider_code: str | None, ctx: HandlerContext) -> None:
        bic = re.sub(r"\s+", "", ((details or {}).get("bic") or "")).upper()
        if not _BIC.fullmatch(bic):
            raise HandlerError("bic is required and must be 8 or 11 characters")
        if provider_code and bic != provider_code.upper():
            raise HandlerError("bic must equal provider_code")
