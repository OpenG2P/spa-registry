INSERT INTO "public"."g2p_intake_form_ui_tab_sections" (
  "tab_section_id","tab_id","section_id","section_order"
) VALUES (
  'c0000000-0000-4000-8000-000000000203',
  'c0000000-0000-4000-8000-000000000202',
  'beneficiary_identity_section',
  10
),
(
  'c0000000-0000-4000-8000-000000000204',
  'c0000000-0000-4000-8000-000000000202',
  'beneficiary_financial_address_section',
  20
)
ON CONFLICT ("tab_section_id") DO UPDATE SET
  "tab_id" = EXCLUDED."tab_id",
  "section_id" = EXCLUDED."section_id",
  "section_order" = EXCLUDED."section_order";
