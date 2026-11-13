INSERT INTO "public"."g2p_register_ui_tabs" ("tab_id","register_id","tab_label","tab_order","is_active")
VALUES
  ('beneficiary_tab','a0000000-0000-4000-8000-000000000101','beneficiary_tab',1,'TRUE'),
  ('beneficiary_financial_address_tab','a0000000-0000-4000-8000-000000000101','beneficiary_financial_address_tab',2,'TRUE')
ON CONFLICT ("tab_id") DO UPDATE SET
  "register_id" = EXCLUDED."register_id",
  "tab_label" = EXCLUDED."tab_label",
  "tab_order" = EXCLUDED."tab_order",
  "is_active" = EXCLUDED."is_active";
