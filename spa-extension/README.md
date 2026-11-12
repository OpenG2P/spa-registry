# OpenG2P SPA Registry extension

Extension package for the Social Payment Accounts Registry. It is selected with `REGISTRY_EXTENSION_MODULE=openg2p_registry_spa_extension.app:Initializer`.

Built on the same pattern as the farmer registry extension:

- `G2PRegisterBeneficiary` (`REGISTER`) and `G2PRegisterFinancialAddress` (`TABLE`)
- configuration tables `financial_address_types` and `financial_service_providers`
- handler package for identifier normalize / validate / mask
- domain services `G2PRegisterDomainServiceBeneficiary` and `G2PRegisterDomainServiceFinancialAddress`

Penny-drop jobs, lookup connectors, and G2P Bridge envelope changes are not in this package yet.
