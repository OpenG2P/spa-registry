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
  '{"section-id":"beneficiary_identity","section-title":"beneficiary_identity","panels":[{"panel-id":"beneficiary_identity_panel","panel-orientation":"horizontal","panels":[{"panel-id":"beneficiary_identity_names","panel-orientation":"vertical","widgets":[
    {"widget":"text","widget-id":"first_name","widget-type":"input","widget-label":"first_name","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.first_name"},
    {"widget":"text","widget-id":"last_name","widget-type":"input","widget-label":"last_name","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.last_name"}
  ]},{"panel-id":"beneficiary_identity_contact","panel-orientation":"vertical","widgets":[
    {"widget":"text","widget-id":"phone_number","widget-type":"input","widget-label":"phone_number","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.phone_number"},
    {"widget":"text","widget-id":"email","widget-type":"input","widget-label":"email","widget-required":true,"widget-data-path":"a0000000-0000-4000-8000-000000000101.email"}
  ]}]}]}',
  'FALSE','FALSE','FALSE','FALSE'
),
(
  'a0000000-0000-4000-8000-000000000101',
  'beneficiary_id_section',
  'b0000000-0000-4000-8000-000000000103',
  'FALSE',
  'beneficiary_ids',
  'Identity documents of the beneficiary',
  'FALSE', 0, 'TRUE', 15,
  '{"section-id":"beneficiary_ids","section-title":"beneficiary_ids","panels":[{"panel-id":"beneficiary_id_panel","panels":[{"panel-id":"beneficiary_id_inner_panel","widgets":[{"widget":"dialog-table","widget-id":"beneficiary_ids","widget-type":"table","widget-label":"beneficiary_ids","widget-data-path":"b0000000-0000-4000-8000-000000000103.records","widget-data-operations":{"add":true,"edit":true,"remove":true},"widget-data-columns":[
    {"column-key":"id_type","widget":"select","widget-label":"id_type","widget-required":true,"widget-data-source":{"type":"api","method":"POST","service":"attributes","endpoint":"values","params":{"attribute_id":"ID_TYPE"},"labelKey":"value_display","valueKey":"value_code"}},
    {"column-key":"id_value","widget":"text","widget-label":"id_value","widget-required":true}
  ]}]}]}]}',
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
    {"column-key":"financial_address_type","widget":"select","widget-label":"financial_address_type","widget-required":true,"widget-data-source":{"type":"api","method":"POST","service":"attributes","endpoint":"values","params":{"attribute_id":"FINANCIAL_ADDRESS_TYPE"},"labelKey":"value_display","valueKey":"value_code"}},
    {"column-key":"financial_address_identifier","widget":"text","widget-label":"financial_address_identifier","widget-required":true,"widget-reset-when":"financial_address_type"},
    {"column-key":"provider_code","widget":"select","widget-label":"provider_code","column-visible-in-table":true,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"__table_only__"}},"widget-data-source":{"type":"api","method":"POST","service":"attributes","endpoint":"values","params":{"attribute_id":"FINANCIAL_SERVICE_PROVIDER"},"labelKey":"value_display","valueKey":"value_code"}},
    {"column-key":"details","widget":"financial-address-details","widget-label":"details","column-visible-in-table":false},
    {"column-key":"priority","widget":"number","widget-label":"priority","widget-data-format":{"decimalPlaces":0},"widget-data-options":{"action":"require","condition":{"field":"record_status","operator":"equals","value":"ACTIVE"}}},
    {"column-key":"currency","widget":"select","widget-label":"currency","widget-required":true,"widget-data-source":{"type":"api","method":"POST","service":"attributes","endpoint":"values","params":{"attribute_id":"CURRENCY"},"labelKey":"value_display","valueKey":"value_code"}},
    {"column-key":"account_validation_status","widget":"display","widget-label":"account_validation_status","widget-readonly":true,"column-visible-in-table":true,"widget-data-options":{"action":"show","condition":{"field":"financial_address_type","operator":"equals","value":"__table_only__"}}},
    {"column-key":"record_status","widget":"select","widget-label":"record_status","widget-required":true,"column-visible-in-table":true,"widget-data-default":"ACTIVE","widget-data-source":{"type":"static","options":[{"value":"ACTIVE","label":"Active"},{"value":"INACTIVE","label":"Inactive"}]}}
  ]}]}]}]}',
  'FALSE','FALSE','FALSE','FALSE'
)
ON CONFLICT ("section_id") DO UPDATE SET
  "section_ui_schema" = EXCLUDED."section_ui_schema",
  "section_mnemonic" = EXCLUDED."section_mnemonic",
  "is_list" = EXCLUDED."is_list";
