import type { ServiceKind } from "@/entities/expertise";
import { API_URL, readErrorMessage } from "@/shared/api";
import type { Act, Invoice, PaymentDocumentKind } from "../model/types";

export const fetchInvoices = async (): Promise<Invoice[]> => {
  const response = await fetch(`${API_URL}/v1/invoices`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Invoice[] = await response.json();

  return items;
};

export const issueInvoice = async (expertiseId: number, service: ServiceKind): Promise<Invoice> => {
  const response = await fetch(`${API_URL}/v1/${service === "audit" ? "audit" : "expertises"}/${expertiseId}/invoice`, {
    method: "POST",
    credentials: "include",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const invoice: Invoice = await response.json();

  return invoice;
};

export const reportInvoicePaid = async (
  invoiceId: number,
  document: File | null = null,
  documentKind: PaymentDocumentKind = "payment_order",
): Promise<Invoice> => {
  const formData = new FormData();
  formData.append("document_kind", documentKind);

  if (document) {
    formData.append("document", document);
  }

  const response = await fetch(`${API_URL}/v1/invoices/${invoiceId}/paid`, {
    method: "POST",
    credentials: "include",
    body: formData,
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const invoice: Invoice = await response.json();

  return invoice;
};

export const fetchActs = async (): Promise<Act[]> => {
  const response = await fetch(`${API_URL}/v1/acts`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Act[] = await response.json();

  return items;
};

export const invoicePdfUrl = (invoiceId: number): string =>
  `${API_URL}/v1/invoices/${invoiceId}/pdf`;

export const actPdfUrl = (act: Act): string =>
  act.audit_id !== null
    ? `${API_URL}/v1/audit/${act.audit_id}/act`
    : `${API_URL}/v1/expertises/${act.expertise_id}/act`;
