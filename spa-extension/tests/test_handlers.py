from openg2p_registry_spa_extension.handlers import handler_for
from openg2p_registry_spa_extension.handlers.base import HandlerContext
from openg2p_registry_spa_extension.crypto import decrypt_identifier, encrypt_identifier, identifier_hash


def test_ifsc_handler():
    handler = handler_for({"handler": "IfscBankAccountHandler"})
    ctx = HandlerContext()
    value = handler.normalize("5010-0123 456789", ctx)
    handler.validate(value, ctx)
    handler.validate_details({"ifsc": "HDFC0001234"}, "HDFC", ctx)
    assert handler.mask(value).endswith("6789")


def test_upi_derives_handle():
    handler = handler_for({"handler": "UpiVpaHandler"})
    ctx = HandlerContext()
    value = handler.normalize(" Ramesh@OkIcici ", ctx)
    handler.validate(value, ctx)
    assert handler.derive_provider(value, ctx) == "okicici"
    assert handler.mask(value).endswith("@okicici")


def test_msisdn_india():
    handler = handler_for({"handler": "MsisdnHandler"})
    ctx = HandlerContext(default_region="IN")
    assert handler.normalize("9876543210", ctx) == "+919876543210"


def test_encrypt_roundtrip():
    stored = encrypt_identifier("50100123456789", "test-key")
    assert stored.startswith("enc:v1:")
    assert decrypt_identifier(stored, "test-key") == "50100123456789"
    digest = identifier_hash("50100123456789", "hash-key")
    assert len(digest) == 64
