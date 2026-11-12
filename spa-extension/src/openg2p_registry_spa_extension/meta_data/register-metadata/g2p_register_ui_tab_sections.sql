INSERT INTO "public"."g2p_register_ui_tab_sections" (
  "tab_section_id","register_id","tab_id","section_id","section_order"
) VALUES
(
  'd0000000-0000-4000-8000-000000000300',
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_tab',
  'beneficiary_summary_section',
  5
),
(
  'd0000000-0000-4000-8000-000000000301',
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_tab',
  'beneficiary_identity_section',
  10
),
(
  'd0000000-0000-4000-8000-000000000302',
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_financial_address_tab',
  'beneficiary_financial_address_section',
  10
)
ON CONFLICT ("tab_section_id") DO UPDATE SET
  "section_id" = EXCLUDED."section_id",
  "section_order" = EXCLUDED."section_order";
