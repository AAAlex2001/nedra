import type { Invoice } from "@/entities/billing";
import { readErrorMessage } from "@/shared/api";

export const fetchInvoices = async (basePath: string): Promise<Invoice[]> => {
  const response = await fetch(`${basePath}/api/invoices`, { cache: "no-store" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const items: Invoice[] = await response.json();

  return items;
};

export const confirmInvoice = async (basePath: string, id: number): Promise<Invoice> => {
  const response = await fetch(`${basePath}/api/invoices/${id}/pay`, { method: "POST" });

  if (!response.ok) {
    const message = await readErrorMessage(response);
    throw new Error(message);
  }

  const invoice: Invoice = await response.json();

  return invoice;
};
