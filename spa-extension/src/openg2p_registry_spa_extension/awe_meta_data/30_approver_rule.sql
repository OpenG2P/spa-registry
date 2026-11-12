INSERT INTO "public"."approver_rule" (
    "id","stage_id","rule_type","rule_value","kind","required","created_at","updated_at"
)
SELECT v.id, s.id, v.rule_type, v.rule_value::json, v.kind, v.required, NOW(), NOW()
FROM (VALUES
    ('f0000000-0000-4000-8000-000000000611','registry.change_request.beneficiary',1,'user','{"user_id": "alex.carter"}','approver',FALSE),
    ('f0000000-0000-4000-8000-000000000612','registry.change_request.beneficiary',2,'user','{"user_id": "nina.patel"}','approver',FALSE),
    ('f0000000-0000-4000-8000-000000000621','registry.intake_form.beneficiary',1,'user','{"user_id": "alex.carter"}','approver',FALSE),
    ('f0000000-0000-4000-8000-000000000622','registry.intake_form.beneficiary',2,'user','{"user_id": "nina.patel"}','approver',FALSE)
) AS v(id, policy_key, stage_order, rule_type, rule_value, kind, required)
INNER JOIN approval_policy p ON p.policy_key = v.policy_key AND p.version = 1
INNER JOIN approval_stage s ON s.policy_id = p.id AND s.stage_order = v.stage_order
WHERE NOT EXISTS (
    SELECT 1 FROM approver_rule r
    WHERE r.stage_id = s.id AND r.rule_type = v.rule_type AND r.rule_value::text = v.rule_value
)
ON CONFLICT ("id") DO NOTHING;
