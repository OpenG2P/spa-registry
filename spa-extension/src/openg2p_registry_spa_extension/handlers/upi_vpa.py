import re

from .base import GenericHandler, HandlerContext, HandlerError

_VPA = re.compile(r"^[a-z0-9._-]{2,256}@[a-z][a-z0-9]{1,63}$")


class UpiVpaHandler(GenericHandler):
    def normalize(self, raw: str, ctx: HandlerContext) -> str:
        return (raw or "").strip().lower()

    def validate(self, value: str, ctx: HandlerContext) -> None:
        if not _VPA.fullmatch(value or ""):
            raise HandlerError("invalid UPI VPA")

    def derive_provider(self, value: str, ctx: HandlerContext) -> str | None:
        handle = value.split("@", 1)[1] if "@" in value else ""
        return handle or None

    def mask(self, value: str) -> str:
        local, _, handle = value.partition("@")
        shown = local[:1] if local else ""
        return f"{shown}****@{handle}"
