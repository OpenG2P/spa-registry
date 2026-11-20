import re

from .base import GenericHandler, HandlerContext, HandlerError

_E164 = re.compile(r"^\+[1-9]\d{9,14}$")
_DIGITS = re.compile(r"\D+")


class MsisdnHandler(GenericHandler):
    def normalize(self, raw: str, ctx: HandlerContext) -> str:
        text = (raw or "").strip().replace(" ", "").replace("-", "")
        if text.startswith("00"):
            text = "+" + text[2:]
        if text.startswith("+"):
            return "+" + _DIGITS.sub("", text)
        digits = _DIGITS.sub("", text)
        if ctx.default_region == "IN" and len(digits) == 10:
            return "+91" + digits
        if digits.startswith("0"):
            digits = digits.lstrip("0")
        return "+" + digits if digits else ""

    def validate(self, value: str, ctx: HandlerContext) -> None:
        if value.startswith("+91"):
            if not re.fullmatch(r"\+91[6-9]\d{9}", value or ""):
                raise HandlerError("Indian mobile numbers must be 10 digits")
            return
        if not _E164.fullmatch(value or ""):
            raise HandlerError("invalid phone number")

    def mask(self, value: str) -> str:
        if len(value) <= 6:
            return "****"
        return value[:3] + "*" * (len(value) - 7) + value[-4:]

    def validate_details(self, details: dict | None, provider_code: str | None, ctx: HandlerContext) -> None:
        if details and "rail" in details and details["rail"] is not None and not str(details["rail"]).strip():
            raise HandlerError("rail must not be blank")
