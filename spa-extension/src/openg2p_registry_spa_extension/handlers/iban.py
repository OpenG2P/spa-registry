import re

from .base import GenericHandler, HandlerContext, HandlerError

_IBAN_LEN = {
    "DE": 22,
    "FR": 27,
    "GB": 22,
    "NL": 18,
    "BE": 16,
    "ES": 24,
    "IT": 27,
}


class IbanHandler(GenericHandler):
    def normalize(self, raw: str, ctx: HandlerContext) -> str:
        return re.sub(r"\s+", "", (raw or "")).upper()

    def validate(self, value: str, ctx: HandlerContext) -> None:
        if len(value) < 5 or not value[:2].isalpha() or not value[2:4].isdigit():
            raise HandlerError("invalid IBAN")
        expected = _IBAN_LEN.get(value[:2])
        if expected and len(value) != expected:
            raise HandlerError("invalid IBAN length")
        rearranged = value[4:] + value[:4]
        digits = "".join(str(int(ch, 36)) if ch.isalpha() else ch for ch in rearranged)
        if int(digits) % 97 != 1:
            raise HandlerError("invalid IBAN checksum")

    def mask(self, value: str) -> str:
        if len(value) <= 8:
            return "****"
        return value[:4] + "*" * (len(value) - 8) + value[-4:]
