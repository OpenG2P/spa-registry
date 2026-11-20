INSERT INTO "public"."g2p_intake_form_definitions" (
  "form_id","register_id","form_mnemonic","form_description","number_of_verifications","used_only_in_ingestion_pipeline"
) VALUES (
  'c0000000-0000-4000-8000-000000000201',
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_intake',
  'Register a beneficiary',
  1,
  'FALSE'
)
ON CONFLICT ("form_id") DO UPDATE SET
  "register_id" = EXCLUDED."register_id",
  "form_mnemonic" = EXCLUDED."form_mnemonic",
  "form_description" = EXCLUDED."form_description",
  "number_of_verifications" = EXCLUDED."number_of_verifications",
  "used_only_in_ingestion_pipeline" = EXCLUDED."used_only_in_ingestion_pipeline";
