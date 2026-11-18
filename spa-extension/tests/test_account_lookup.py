from openg2p_registry_spa_extension.register_domain.services.account_lookup import (
    classify_response,
    connector_for,
    name_match,
    render_template,
)


class _Settings:
    account_lookup_connectors = {
        "UPI-VPA-BANK-ACCOUNT": {
            "connector": "upi",
            "url": "https://lookup.example/vpa",
            "payload": {"vpa": "{identifier}"},
        },
        "MSISDN-WALLET:PAYTM-WALLET": {
            "connector": "paytm",
            "url": "https://lookup.example/paytm",
            "payload": {"mobile": "{identifier}"},
        },
    }


def test_provider_specific_connector_wins():
    settings = _Settings()
    chosen = connector_for("MSISDN-WALLET", "PAYTM-WALLET", settings)
    assert chosen.name == "paytm"
    assert connector_for("MSISDN-WALLET", "AIRTEL-WALLET", settings) is None


def test_payload_template_and_result_mapping():
    payload = render_template(
        {"vpa": "{identifier}", "name": "{account_name}"},
        {"identifier": "ramesh@okicici", "account_name": "Ramesh Kumar"},
    )
    assert payload == {"vpa": "ramesh@okicici", "name": "Ramesh Kumar"}
    found = classify_response(
        {"status": "SUCCESS", "data": {"holder": "Ramesh Kumar"}},
        {"status_path": "status", "name_path": "data.holder", "found_values": ["SUCCESS"]},
    )
    assert found.status == "FOUND"
    assert found.name == "Ramesh Kumar"
    assert name_match("Ramesh Kumar", found.name) == ("MATCH", 1.0)
    assert name_match("Ramesh Kumar", "Other Person")[0] == "MISMATCH"
