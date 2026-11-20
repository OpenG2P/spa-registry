INSERT INTO "public"."g2p_registry_awe_policy_configurations" (
  "awe_policy_config_id","policy_scope","register_id","intake_form_id","section_id","policy_type","policy_key","context_field_names"
) VALUES
(
  'e0000000-0000-4000-8000-000000000401','REGISTER','a0000000-0000-4000-8000-000000000101','','','registry.change_request','registry.change_request.beneficiary','null'
),
(
  'e0000000-0000-4000-8000-000000000404','INTAKE_FORM','a0000000-0000-4000-8000-000000000101','c0000000-0000-4000-8000-000000000201','','registry.intake_form','registry.intake_form.beneficiary','null'
)
ON CONFLICT ("awe_policy_config_id") DO NOTHING;

DELETE FROM "public"."g2p_registry_awe_policy_configurations"
WHERE "awe_policy_config_id" IN (
  'e0000000-0000-4000-8000-000000000402',
  'e0000000-0000-4000-8000-000000000403'
);
