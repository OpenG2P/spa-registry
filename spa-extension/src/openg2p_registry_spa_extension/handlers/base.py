import re
from typing import Protocol


class HandlerError(ValueError):
    pass


class HandlerContext:
    def __init__(self, default_region: str = "IN", provider_codes: set[str] | None = None):
        self.default_region = default_region
        self.provider_codes = provider_codes or set()


class AddressTypeHandler(Protocol):
    def normalize(self, raw: str, ctx: HandlerContext) -> str: ...

    def validate(self, value: str, ctx: HandlerContext) -> None: ...

    def mask(self, value: str) -> str: ...

    def derive_provider(self, value: str, ctx: HandlerContext) -> str | None: ...

    def validate_details(self, details: dict | None, provider_code: str | None, ctx: HandlerContext) -> None: ...


class GenericHandler:
    def __init__(self, validation_regex: str | None = None, normalizer: str | None = None):
        self.validation_regex = validation_regex
        self.normalizer = normalizer or "trim"

    def normalize(self, raw: str, ctx: HandlerContext) -> str:
        value = (raw or "").strip()
        if self.normalizer == "uppercase":
            return value.upper()
        if self.normalizer == "lowercase":
            return value.lower()
        return value

    def validate(self, value: str, ctx: HandlerContext) -> None:
        if not value:
            raise HandlerError("identifier is required")
        if self.validation_regex and not re.fullmatch(self.validation_regex, value):
            raise HandlerError("identifier does not match the type pattern")

    def mask(self, value: str) -> str:
        if len(value) <= 4:
            return "****"
        return "*" * (len(value) - 4) + value[-4:]

    def derive_provider(self, value: str, ctx: HandlerContext) -> str | None:
        return None

    def validate_details(self, details: dict | None, provider_code: str | None, ctx: HandlerContext) -> None:
        return None
