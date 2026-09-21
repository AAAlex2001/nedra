import { API_URL, readErrorMessage } from "@/shared/api";
import type { Act, Company, CompanyDraft, Invoice } from "../model/types";

export const fetchCompany = async (): Promise<Company | null> => {
  const response = await fetch(`${API_URL}/v1/me/company`, {
    credentials: "include",
    cache: "no-store",
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const company: Company | null = await response.json();

  return company;
};

export const saveCompany = async (draft: CompanyDraft): Promise<Company> => {
  const response = await fetch(`${API_URL}/v1/me/company`, {
    method: "PUT",
    credentials: "include",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(draft),
  });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const company: Company = await response.json();

  return company;
};

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

export const issueInvoice = async (expertiseId: number): Promise<Invoice> => {
  const response = await fetch(`${API_URL}/v1/expertise/${expertiseId}/invoice`, {
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

export const reportInvoicePaid = async (invoiceId: number): Promise<Invoice> => {
  const response = await fetch(`${API_URL}/v1/invoices/${invoiceId}/paid`, {
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

export const actPdfUrl = (expertiseId: number): string =>
  `${API_URL}/v1/acts/${expertiseId}/pdf`;
