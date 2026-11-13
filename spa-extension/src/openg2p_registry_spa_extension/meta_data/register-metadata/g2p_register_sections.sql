INSERT INTO "public"."g2p_register_sections" (
  "register_id","section_id","section_register_id","is_core_section","section_mnemonic",
  "section_description","documents_required","no_of_verifications_required","is_list",
  "section_weightage","section_ui_schema",
  "cr_auto_approve_for_bene_portal","cr_auto_approve_for_agent_portal",
  "cr_auto_approve_for_staff_portal","cr_auto_approve_for_partner"
) VALUES
(
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_summary_section',
  'a0000000-0000-4000-8000-000000000101',
  'TRUE',
  'beneficiary_summary',
  'Beneficiary summary',
  'FALSE', 0, 'FALSE', 0,
  '{"panels":[{"panels":[{"widgets":[{"widget":"header-section","widget-id":"registry-header","widget-type":"group","widget-data-path":{"name":"a0000000-0000-4000-8000-000000000101.record_name","image":"a0000000-0000-4000-8000-000000000101.record_image_document_id","status":"a0000000-0000-4000-8000-000000000101.record_status","imageUrl":"a0000000-0000-4000-8000-000000000101.record_image_url","createdAt":"a0000000-0000-4000-8000-000000000101.created_at","createdBy":"a0000000-0000-4000-8000-000000000101.created_by","functionalId":"a0000000-0000-4000-8000-000000000101.functional_record_id","statusReason":"a0000000-0000-4000-8000-000000000101.record_status_reason","lastApprovedAt":"a0000000-0000-4000-8000-000000000101.last_approved_at","lastApprovedBy":"a0000000-0000-4000-8000-000000000101.last_approved_by"},"widget-data-format":{"imageSize":120,"nameColor":"#ED7C22","statusColors":{"active":"#16A34A","archived":"#6B7280","inactive":"#D97706"}},"widget-field-config":{"status":{"data-source":{"type":"static","options":[{"label":"ACTIVE","value":"ACTIVE"},{"label":"INACTIVE","value":"INACTIVE"},{"label":"ARCHIVED","value":"ARCHIVED"}]}}}}],"panel-id":"beneficiary_summary_inside_panel","panel-orientation":"vertical"}],"panel-id":"beneficiary_summary_outside_panel","panel-orientation":"horizontal"}],"section-id":"beneficiary_summary","section-title":"beneficiary_summary","section-editable":false}',
  'FALSE','FALSE','FALSE','FALSE'
),
(
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_identity_section',
  'a0000000-0000-4000-8000-000000000101',
  'TRUE',
  'beneficiary_identity',
  'Beneficiary name and foundational id',
  'FALSE', 0, 'FALSE', 10,
  '{"section-id":"beneficiary_identity","section-title":"beneficiary_identity","panels":[{"panel-id":"beneficiary_identity_panel","panels":[{"panel-id":"beneficiary_identity_inner_panel","widgets":[
    {"widget":"text","widget-id":"first_name","widget-type":"input","widget-label":"first_name","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.first_name"},
    {"widget":"text","widget-id":"last_name","widget-type":"input","widget-label":"last_name","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.last_name"},
    {"widget":"text","widget-id":"foundational_id","widget-type":"input","widget-label":"foundational_id","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.foundational_id"}
  ]}]}]}',
  'FALSE','FALSE','FALSE','FALSE'
),
(
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_financial_address_section',
  'b0000000-0000-4000-8000-000000000102',
  'FALSE',
  'beneficiary_financial_addresses',
  'Financial addresses of the beneficiary',
  'FALSE', 0, 'TRUE', 20,
  '{"section-id":"beneficiary_financial_addresses","section-title":"financial_addresses","panels":[{"panel-id":"beneficiary_financial_address_panel","panels":[{"panel-id":"beneficiary_financial_address_inner_panel","widgets":[{"widget":"dialog-table","widget-id":"financial_addresses","widget-type":"table","widget-label":"financial_addresses","widget-data-path":"b0000000-0000-4000-8000-000000000102.records","widget-data-operations":{"add":true,"edit":true,"remove":false},"widget-data-columns":[
    {"column-key":"financial_address_type","widget":"select","widget-label":"financial_address_type","widget-required":true,"widget-data-source":{"type":"static","options":[{"value":"UPI-VPA-BANK-ACCOUNT","label":"UPI virtual payment address"},{"value":"MSISDN-WALLET","label":"Mobile wallet"},{"value":"MSISDN-BANK-ACCOUNT","label":"Phone number alias of a bank account"},{"value":"IFSC-BANK-ACCOUNT","label":"Indian bank account with IFSC"},{"value":"IBAN-BANK-ACCOUNT","label":"IBAN bank account"},{"value":"BIC-BANK-ACCOUNT","label":"BIC addressed bank account"}]}},
    {"column-key":"financial_address_identifier","widget":"text","widget-label":"financial_address_identifier","widget-required":true,"widget-reset-when":"financial_address_type"},
    {"column-key":"provider_code","widget":"select","widget-label":"provider_code","column-visible-in-table":true,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"__table_display__"}},"widget-data-source":{"type":"static","options":[{"value":"okicici","label":"Google Pay (ICICI)"},{"value":"AIRTEL-WALLET","label":"Airtel wallet"},{"value":"PAYTM-WALLET","label":"Paytm wallet"},{"value":"HDFC","label":"HDFC Bank"},{"value":"SBIN","label":"State Bank of India"},{"value":"ICIC","label":"ICICI Bank"},{"value":"UTIB","label":"Axis Bank"},{"value":"HABBPKKA","label":"Habib Bank Limited"}]}},
    {"column-key":"provider_code","widget":"select","widget-label":"provider_code","widget-required":true,"column-visible-in-table":false,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"MSISDN-WALLET"}},"widget-data-source":{"type":"static","options":[{"value":"AIRTEL-WALLET","label":"Airtel wallet"},{"value":"PAYTM-WALLET","label":"Paytm wallet"}]}},
    {"column-key":"provider_code","widget":"select","widget-label":"provider_code","widget-required":true,"column-visible-in-table":false,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"MSISDN-BANK-ACCOUNT"}},"widget-data-source":{"type":"static","options":[{"value":"HABBPKKA","label":"Habib Bank Limited"}]}},
    {"column-key":"provider_code","widget":"select","widget-label":"provider_code","widget-required":true,"column-visible-in-table":false,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"BIC-BANK-ACCOUNT"}},"widget-data-source":{"type":"static","options":[{"value":"HABBPKKA","label":"Habib Bank Limited"}]}},
    {"column-key":"details","widget":"financial-address-details","widget-label":"details","widget-required":true,"column-visible-in-table":false,"widget-address-type":"IFSC-BANK-ACCOUNT","widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"IFSC-BANK-ACCOUNT"}}},
    {"column-key":"details","widget":"financial-address-details","widget-label":"details","column-visible-in-table":false,"widget-address-type":"MSISDN-BANK-ACCOUNT","widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"MSISDN-BANK-ACCOUNT"}}},
    {"column-key":"details","widget":"financial-address-details","widget-label":"details","column-visible-in-table":false,"widget-address-type":"BIC-BANK-ACCOUNT","widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"BIC-BANK-ACCOUNT"}}},
    {"column-key":"priority","widget":"number","widget-label":"priority","widget-data-format":{"decimalPlaces":0},"widget-data-options":{"action":"require","condition":{"field":"record_status","operator":"equals","value":"ACTIVE"}}},
    {"column-key":"currency","widget":"select","widget-label":"currency","widget-required":true,"widget-data-source":{"type":"static","options":[{"value":"INR","label":"INR"},{"value":"PKR","label":"PKR"},{"value":"EUR","label":"EUR"}]}},
    {"column-key":"account_validation_status","widget":"display","widget-label":"account_validation_status","widget-readonly":true,"column-visible-in-table":true,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"__table_only__"}}},
    {"column-key":"record_status","widget":"select","widget-label":"record_status","widget-required":true,"column-visible-in-table":true,"widget-data-default":"ACTIVE","widget-data-source":{"type":"static","options":[{"value":"ACTIVE","label":"Active"},{"value":"INACTIVE","label":"Inactive"}]}}
  ]}]}]}]}',
  'FALSE','FALSE','FALSE','FALSE'
)
ON CONFLICT ("section_id") DO UPDATE SET
  "section_ui_schema" = EXCLUDED."section_ui_schema",
  "section_mnemonic" = EXCLUDED."section_mnemonic",
  "is_list" = EXCLUDED."is_list";
