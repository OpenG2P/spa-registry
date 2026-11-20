INSERT INTO "public"."approval_stage" (
    "id","policy_id","stage_order","name","mode","mode_value","sla_hours","parallel_group",
    "skip_if","on_empty","on_breach","escalation_rules_json","created_at","updated_at"
)
SELECT v.id, p.id, v.stage_order, v.name, v.mode,
       CAST(NULL AS integer), CAST(NULL AS integer), CAST(NULL AS integer),
       'null','block',CAST(NULL AS integer),'null',NOW(),NOW()
FROM (VALUES
    ('f0000000-0000-4000-8000-000000000511','registry.change_request.beneficiary',1,'Stage 1 Officers','all'),
    ('f0000000-0000-4000-8000-000000000512','registry.change_request.beneficiary',2,'Stage 2 Officers','all'),
    ('f0000000-0000-4000-8000-000000000521','registry.intake_form.beneficiary',1,'Stage 1 Officers','all'),
    ('f0000000-0000-4000-8000-000000000522','registry.intake_form.beneficiary',2,'Stage 2 Officers','all')
) AS v(id, policy_key, stage_order, name, mode)
INNER JOIN approval_policy p ON p.policy_key = v.policy_key AND p.version = 1
WHERE NOT EXISTS (
    SELECT 1 FROM approval_stage s WHERE s.policy_id = p.id AND s.stage_order = v.stage_order
)
ON CONFLICT ("id") DO NOTHING;
