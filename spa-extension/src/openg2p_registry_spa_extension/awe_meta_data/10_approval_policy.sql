INSERT INTO "public"."approval_policy" (
    "id","policy_key","version","name","description","status","artifact_type",
    "created_by","forbid_self_approval","forbid_repeat_approvers","created_at","updated_at"
) VALUES
    ('f0000000-0000-4000-8000-000000000501','registry.change_request.beneficiary',1,'Policy for Beneficiary Change Request',NULL,'active','registry.change_request','seed','FALSE','FALSE',NOW(),NOW()),
    ('f0000000-0000-4000-8000-000000000504','registry.intake_form.beneficiary',1,'Policy for Beneficiary Intake Form',NULL,'active','registry.intake_form','seed','FALSE','FALSE',NOW(),NOW())
ON CONFLICT ("policy_key","version") DO NOTHING;
