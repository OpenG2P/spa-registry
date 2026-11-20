import re

from .base import GenericHandler, HandlerContext, HandlerError

_ACCOUNT = re.compile(r"^[A-Z0-9]{5,34}$")
_IFSC = re.compile(r"^[A-Z]{4}0[A-Z0-9]{6}$")


class IfscBankAccountHandler(GenericHandler):
    def normalize(self, raw: str, ctx: HandlerContext) -> str:
        return re.sub(r"[\s-]+", "", (raw or "")).upper()

    def validate(self, value: str, ctx: HandlerContext) -> None:
        if not _ACCOUNT.fullmatch(value or ""):
            raise HandlerError("invalid bank account number")

    def mask(self, value: str) -> str:
        if len(value) <= 4:
            return "****"
        return "*" * (len(value) - 4) + value[-4:]

    def validate_details(self, details: dict | None, provider_code: str | None, ctx: HandlerContext) -> None:
        ifsc = ((details or {}).get("ifsc") or "").strip().upper()
        if not _IFSC.fullmatch(ifsc):
            raise HandlerError("ifsc is required and must match the IFSC pattern")
        if provider_code and ifsc[:4] != provider_code.upper():
            raise HandlerError("ifsc prefix must equal provider_code")
