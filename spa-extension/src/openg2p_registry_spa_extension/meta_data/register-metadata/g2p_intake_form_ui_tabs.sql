INSERT INTO "public"."g2p_intake_form_ui_tabs" ("tab_id","form_id","tab_label","tab_order")
VALUES (
  'c0000000-0000-4000-8000-000000000202',
  'c0000000-0000-4000-8000-000000000201',
  'beneficiary_intake_tab',
  10
)
ON CONFLICT ("tab_id") DO UPDATE SET
  "form_id" = EXCLUDED."form_id",
  "tab_label" = EXCLUDED."tab_label",
  "tab_order" = EXCLUDED."tab_order";
