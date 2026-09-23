export type InvoiceStage = "advance" | "final";

export type PaymentDocumentKind = "payment_order" | "guarantee_letter";

export type Company = {
  name: string;
  inn: string;
  kpp: string | null;
  address: string;
  updated_at: string;
};

export type CompanyDraft = {
  name: string;
  inn: string;
  kpp: string | null;
  address: string;
};

export type Invoice = {
  id: number;
  number: string;
  expertise_id: number;
  stage: InvoiceStage;
  amount: string;
  payer_name: string;
  payer_inn: string;
  created_at: string;
  reported_at: string | null;
  paid_at: string | null;
};

export type Act = {
  expertise_id: number;
  number: string;
  amount: string | null;
  subject: string;
  signed_at: string;
};

export const INVOICE_STAGE_LABELS: Record<InvoiceStage, string> = {
  advance: "Аванс 50%",
  final: "Остаток 50%",
};
