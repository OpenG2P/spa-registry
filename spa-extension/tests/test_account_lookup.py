from openg2p_registry_spa_extension.register_domain.services.account_lookup import (
    classify_response,
    ConnectorFactory,
    name_match,
    render_template,
)


class _Settings:
    account_lookup_connectors = {
        "MSISDN-WALLET": [
            {
                "connector": "http-json",
                "url": "https://lookup.example/wallet",
                "provider_codes": ["*"],
            },
            {
                "connector": "http-json",
                "url": "https://lookup.example/paytm",
                "provider_codes": ["PAYTM-WALLET"],
            },
        ],
    }


def test_star_connector_wins():
    settings = _Settings()
    chosen = ConnectorFactory.get("MSISDN-WALLET", "PAYTM-WALLET", settings)
    assert chosen.config["url"] == "https://lookup.example/wallet"
    default = ConnectorFactory.get("MSISDN-WALLET", "AIRTEL-WALLET", settings)
    assert default.config["url"] == "https://lookup.example/wallet"


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
