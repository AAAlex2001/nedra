"use client";

import { useState } from "react";
import type { Invoice } from "@/entities/billing";
import { confirmInvoice, fetchInvoices } from "../api/invoices";

const describe = (error: unknown, fallback: string): string =>
  error instanceof Error && error.message ? error.message : fallback;

export const useAdminInvoices = (initialItems: Invoice[], basePath: string) => {
  const [items, setItems] = useState(initialItems);
  const [pendingId, setPendingId] = useState<number | null>(null);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const confirm = async (id: number) => {
    setPendingId(id);
    setError(null);

    try {
      const updated = await confirmInvoice(basePath, id);
      setItems(items.map((item) => (item.id === id ? updated : item)));
    } catch (caught) {
      setError(describe(caught, "Не удалось отметить счёт оплаченным"));
    } finally {
      setPendingId(null);
    }
  };

  const refresh = async () => {
    setRefreshing(true);
    setError(null);

    try {
      setItems(await fetchInvoices(basePath));
    } catch (caught) {
      setError(describe(caught, "Не удалось обновить список"));
    } finally {
      setRefreshing(false);
    }
  };

  return { items, pendingId, refreshing, error, confirm, refresh };
};
