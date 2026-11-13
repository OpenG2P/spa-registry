INSERT INTO "public"."g2p_register_definitions" (
  "register_id","register_mnemonic","register_subject","register_description",
  "master_register_id","register_rank","functional_id_generation_required","register_purpose",
  "program_id","program_mnemonic","register_icon","has_image","dedup_is_enabled",
  "dedup_threshold_score","completion_score_required","outgest_applicable",
  "requires_registrant_authentication","registrant_authentication_validity_days",
  "registrant_re_auth_warning_days_before"
) VALUES
(
  'a0000000-0000-4000-8000-000000000101','Beneficiary','Beneficiaries','SPA beneficiary register',
  NULL,1,'TRUE','REGISTER',NULL,NULL,NULL,'FALSE','FALSE',0,'FALSE','FALSE','FALSE',730,30
),
(
  'b0000000-0000-4000-8000-000000000102','FinancialAddress','Financial Addresses','SPA financial address register',
  'a0000000-0000-4000-8000-000000000101',2,'FALSE','TABLE',NULL,NULL,NULL,'FALSE','FALSE',0,'FALSE','FALSE','FALSE',730,30
)
ON CONFLICT ("register_id") DO UPDATE SET
  "register_mnemonic" = EXCLUDED."register_mnemonic",
  "register_subject" = EXCLUDED."register_subject",
  "register_description" = EXCLUDED."register_description",
  "master_register_id" = EXCLUDED."master_register_id",
  "register_rank" = EXCLUDED."register_rank",
  "register_purpose" = EXCLUDED."register_purpose",
  "functional_id_generation_required" = EXCLUDED."functional_id_generation_required";
