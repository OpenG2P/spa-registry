INSERT INTO "public"."g2p_register_schemas" ("register_id","deduplicate_schema","search_result_schema","filter_schema") VALUES
(
  'a0000000-0000-4000-8000-000000000101',
  '[{"field_name": "first_name", "match_type": "fuzzy", "weight": 0.4}, {"field_name": "last_name", "match_type": "fuzzy", "weight": 0.4}, {"field_name": "foundational_id", "match_type": "exact", "weight": 0.2}]',
  '[{"field_name": "functional_record_id", "display_label": "Beneficiary ID", "order": 1}, {"field_name": "first_name", "display_label": "First Name", "order": 2}, {"field_name": "last_name", "display_label": "Last Name", "order": 3}, {"field_name": "foundational_id", "display_label": "Foundational ID", "order": 4}, {"field_name": "record_status", "display_label": "Status", "order": 5}]',
  '[{"field_name": "first_name", "display_label": "First Name", "filter_type": "text", "order": 1, "allowed_operators": ["eq", "contains"]}, {"field_name": "last_name", "display_label": "Last Name", "filter_type": "text", "order": 2, "allowed_operators": ["eq", "contains"]}, {"field_name": "foundational_id", "display_label": "Foundational ID", "filter_type": "text", "order": 3, "allowed_operators": ["eq"]}, {"field_name": "record_status", "display_label": "Record Status", "filter_type": "dropdown", "order": 4, "allowed_operators": ["eq", "in"], "options_source": [{"value": "ACTIVE", "label": "ACTIVE"}, {"value": "INACTIVE", "label": "INACTIVE"}, {"value": "ARCHIVED", "label": "ARCHIVED"}]}]'
),
(
  'b0000000-0000-4000-8000-000000000102',
  'null',
  '[{"field_name": "financial_address_type", "display_label": "Type", "order": 1}, {"field_name": "provider_code", "display_label": "Provider", "order": 2}, {"field_name": "priority", "display_label": "Priority", "order": 3}, {"field_name": "record_status", "display_label": "Status", "order": 4}, {"field_name": "account_validation_status", "display_label": "Validation", "order": 5}]',
  '[{"field_name": "financial_address_type", "display_label": "Type", "filter_type": "text", "order": 1, "allowed_operators": ["eq"]}, {"field_name": "provider_code", "display_label": "Provider", "filter_type": "text", "order": 2, "allowed_operators": ["eq", "contains"]}, {"field_name": "record_status", "display_label": "Record Status", "filter_type": "dropdown", "order": 3, "allowed_operators": ["eq", "in"], "options_source": [{"value": "ACTIVE", "label": "ACTIVE"}, {"value": "INACTIVE", "label": "INACTIVE"}]}]'
)
ON CONFLICT ("register_id") DO UPDATE SET
  "deduplicate_schema" = EXCLUDED."deduplicate_schema",
  "search_result_schema" = EXCLUDED."search_result_schema",
  "filter_schema" = EXCLUDED."filter_schema";
