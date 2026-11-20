# spa-registry
A registry of beneficiary financial addresses, built as an extension of the OpenG2P registry platform.

Packaging follows the farmer registry: `helm/openg2p-spa-registry`, `docker/` (staff API, partner API, staff UI, Celery, db-seed, sanity tests), `test/sanity`, and `scripts/`. There is no performance-test tree.

The installable package is `spa-extension` (`openg2p_registry_spa_extension`). Point the registry service at it with:

```
REGISTRY_EXTENSION_MODULE=openg2p_registry_spa_extension.app:Initializer
```

Seed `meta_data/g2p_register_definitions.sql` and `meta_data/financial_address_seed.sql` after the tables exist. Requirements: https://docs.openg2p.org/products/registry/spa-registry/spa-registry-requirements
