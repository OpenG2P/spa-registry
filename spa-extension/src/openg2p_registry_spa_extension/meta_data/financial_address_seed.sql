INSERT INTO financial_address_types
  (code, description, kind, handler, provider_required, details_schema, validation_method, active)
VALUES
  ('UPI-VPA-BANK-ACCOUNT', 'UPI virtual payment address', 'BANK_ACCOUNT', 'UpiVpaHandler', FALSE, NULL, 'LOOKUP', TRUE),
  ('MSISDN-WALLET', 'Mobile wallet', 'WALLET', 'MsisdnHandler', TRUE, NULL, 'LOOKUP', TRUE),
  ('MSISDN-BANK-ACCOUNT', 'Phone number alias of a bank account', 'BANK_ACCOUNT', 'MsisdnHandler', TRUE, '{"type":"object","properties":{"rail":{"type":"string"}}}'::jsonb, 'LOOKUP', TRUE),
  ('IFSC-BANK-ACCOUNT', 'Indian bank account with IFSC', 'BANK_ACCOUNT', 'IfscBankAccountHandler', TRUE, '{"type":"object","required":["ifsc"],"properties":{"ifsc":{"type":"string"}}}'::jsonb, 'PENNY_DROP', TRUE),
  ('IBAN-BANK-ACCOUNT', 'IBAN bank account', 'BANK_ACCOUNT', 'IbanHandler', FALSE, NULL, 'PENNY_DROP', TRUE),
  ('BIC-BANK-ACCOUNT', 'BIC addressed bank account', 'BANK_ACCOUNT', 'BicHandler', TRUE, '{"type":"object","required":["bic"],"properties":{"bic":{"type":"string"}}}'::jsonb, 'PENNY_DROP', TRUE)
ON CONFLICT (code) DO NOTHING;

INSERT INTO financial_service_providers (code, name, group_name, services, needs_review, active)
VALUES
  ('okicici', 'Google Pay (ICICI)', 'Google Pay', ARRAY['BANK_ACCOUNT'], FALSE, TRUE),
  ('AIRTEL-WALLET', 'Airtel wallet', 'Airtel', ARRAY['WALLET'], FALSE, TRUE),
  ('PAYTM-WALLET', 'Paytm wallet', 'Paytm', ARRAY['WALLET'], FALSE, TRUE),
  ('HDFC', 'HDFC Bank', 'HDFC', ARRAY['BANK_ACCOUNT'], FALSE, TRUE),
  ('SBIN', 'State Bank of India', 'SBI', ARRAY['BANK_ACCOUNT'], FALSE, TRUE),
  ('ICIC', 'ICICI Bank', 'ICICI', ARRAY['BANK_ACCOUNT'], FALSE, TRUE),
  ('UTIB', 'Axis Bank', 'Axis', ARRAY['BANK_ACCOUNT'], FALSE, TRUE),
  ('HABBPKKA', 'Habib Bank Limited', 'HBL', ARRAY['BANK_ACCOUNT','WALLET'], FALSE, TRUE)
ON CONFLICT (code) DO NOTHING;
